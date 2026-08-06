#!/usr/bin/env python3
"""
把 UOF 分機查詢頁匯出的原始 txt 正規化成離線快照（directory.tsv + directory.meta.json）。

原始 txt 是 UOF「CDS/WebPage/ExtQuery.aspx」整頁複製下來的 tab 分隔檔，特徵：
- 首欄與末欄是空的（表格邊框），實際資料在 idx1..idx7
- 表頭第 2 欄（職級）沒有標題，所以只驗 idx2..idx7 六個欄名
- 姓名欄把職稱黏在後面（『蘇清源 資深主任』），這裡拆成 name / title 兩欄

用法：
  python build_directory.py "G:/AI/IGS電話分機.txt"
  python build_directory.py raw.txt --out ~/.config/uof/directory.tsv --snapshot-date 2026-08-06

產出的 TSV 不進 git（含全公司姓名/Email/員編）。人員異動後重跑本腳本覆蓋即可。
"""
import argparse
import csv
import datetime
import json
import os
import sys

# Windows 主控台預設 cp950(Big5)，印中文與 ✅ 會 UnicodeEncodeError（同 uof_client.py 的處理）
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from directory import COLUMNS, meta_path, snapshot_path, split_name  # noqa: E402

# 原始 txt 的欄位位置 → 快照欄名。idx0/idx8 是表格邊框的空欄，不取。
RAW_MAP = {1: "rank", 2: "dept", 3: "team", 4: "_name_raw", 5: "ext", 6: "empno", 7: "email"}
# 表頭驗證：職級欄（idx1）在 UOF 頁面上沒有標題，故不驗
EXPECT_HEADER = {2: "部門", 3: "組", 4: "姓名", 5: "分機", 6: "員工編號", 7: "Email"}


def parse_raw(path):
    """解析原始 txt，回 (rows, skipped)。表頭不符直接丟 SystemExit（版型改變不該靜默吃掉）。"""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    if not lines:
        raise SystemExit(f"[錯誤] {path} 是空的")

    header = lines[0].split("\t")
    for idx, want in EXPECT_HEADER.items():
        got = header[idx].strip() if idx < len(header) else "(缺欄)"
        if got != want:
            raise SystemExit(
                f"[錯誤] 原始檔表頭第 {idx + 1} 欄預期『{want}』實得『{got}』。\n"
                f"       UOF 分機頁版型可能改了，請確認後調整 build_directory.py 的 RAW_MAP/EXPECT_HEADER。")

    rows, skipped = [], []
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cells = line.split("\t")
        rec = {}
        for idx, key in RAW_MAP.items():
            rec[key] = cells[idx].strip() if idx < len(cells) else ""
        rec["name"], rec["title"] = split_name(rec.pop("_name_raw"))
        # 姓名或分機缺一即無法當通訊錄用，記下來讓使用者知道少了什麼（不靜默丟棄）
        if not rec["name"] or not rec["ext"]:
            skipped.append({"line": lineno, "raw": line.strip()[:80]})
            continue
        rows.append(rec)
    return rows, skipped


def build_meta(rows, src, snapshot_date, skipped):
    """統計摘要，寫進 meta.json。同名/共用分機是真實現象（客服組 hunt group），不是錯誤，
    但要記下來——查詢回多筆時 AI 才知道那是正常的。"""
    names, exts = {}, {}
    for r in rows:
        names[r["name"]] = names.get(r["name"], 0) + 1
        exts[r["ext"]] = exts.get(r["ext"], 0) + 1
    return {
        "snapshot_date": snapshot_date,
        "built_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "source": os.path.abspath(src),
        "rows": len(rows),
        "depts": len({r["dept"] for r in rows}),
        "duplicate_names": sorted(n for n, c in names.items() if c > 1),
        "shared_exts": sorted(e for e, c in exts.items() if c > 1),
        "skipped_rows": skipped,
    }


def main():
    ap = argparse.ArgumentParser(
        prog="build_directory.py",
        description="從 UOF 分機頁匯出的 txt 建立離線通訊錄快照")
    ap.add_argument("source", help="原始 txt 路徑")
    ap.add_argument("--out", default=None,
                    help="快照輸出路徑（預設同 directory.py 的解析結果，通常 ~/.config/uof/directory.tsv）")
    ap.add_argument("--snapshot-date", default=None,
                    help="資料日期 YYYY-MM-DD（預設取原始檔的修改日期）")
    args = ap.parse_args()

    if not os.path.exists(args.source):
        raise SystemExit(f"[錯誤] 找不到原始檔 {args.source}")

    snapshot_date = args.snapshot_date or datetime.date.fromtimestamp(
        os.path.getmtime(args.source)).isoformat()
    out = args.out or snapshot_path()
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    rows, skipped = parse_raw(args.source)
    if not rows:
        raise SystemExit("[錯誤] 解析後 0 筆資料，不覆蓋既有快照")

    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})

    meta = build_meta(rows, args.source, snapshot_date, skipped)
    with open(meta_path(out), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)

    print(f"✅ 快照已建立：{out}")
    print(f"   {meta['rows']} 人 / {meta['depts']} 部門 / 資料日期 {snapshot_date}")
    if meta["duplicate_names"]:
        print(f"   ⚠️ 同名 {len(meta['duplicate_names'])} 組：{'、'.join(meta['duplicate_names'])}")
    if meta["shared_exts"]:
        print(f"   ℹ️ 共用分機 {len(meta['shared_exts'])} 支：{'、'.join(meta['shared_exts'])}")
    if skipped:
        print(f"   ⚠️ 略過 {len(skipped)} 行（缺姓名或分機），明細見 {meta_path(out)}")


if __name__ == "__main__":
    main()
