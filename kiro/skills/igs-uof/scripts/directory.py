#!/usr/bin/env python3
"""
離線通訊錄：載入快照 TSV、提供查詢。

兩個用途：
1. 被 cmd_whois.py 當離線後端（查得到就秒回，完全不開瀏覽器）
2. 直接當 CLI 用：python directory.py --dept 線上研一部 --count-by team

快照檔不進 git（含全公司姓名/Email/員編 = PII）。位置優先序：
  $UOF_DIRECTORY > config.json 的 directory_snapshot > ~/.config/uof/directory.tsv
用 build_directory.py 從 UOF 分機頁匯出的原始 txt 產生。
"""
import argparse
import csv
import json
import os
import sys

# Windows 主控台/subprocess pipe 預設 cp950(Big5)，印中文姓名會亂碼（同 uof_client.py 的處理）
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 快照 TSV 欄位（build_directory.py 產出時的表頭，順序即欄序）
COLUMNS = ["dept", "team", "rank", "name", "title", "ext", "empno", "email"]

DEFAULT_PATH = os.path.expanduser("~/.config/uof/directory.tsv")

# 子字串比對的欄位（其餘走精確比對）
_SUBSTR_FIELDS = ("dept", "team", "rank", "title")


class DirectoryUnavailable(Exception):
    """快照不存在或壞掉。呼叫端據此決定要不要退回線上查詢。"""

    def __init__(self, hint):
        super().__init__(hint)
        self.hint = hint


def snapshot_path(cfg=None):
    """回快照 TSV 路徑（不保證存在）。"""
    return (os.environ.get("UOF_DIRECTORY")
            or (cfg or {}).get("directory_snapshot")
            or DEFAULT_PATH)


def meta_path(path):
    """meta.json 與 TSV 同目錄同主檔名。"""
    return os.path.splitext(path)[0] + ".meta.json"


def split_name(raw):
    """UOF 姓名欄把職稱黏在名字後（『蘇清源 資深主任』）。回 (姓名, 職稱)。

    實測 1155 筆中 482 筆帶職稱，一律單一半形空格分隔、職稱只有 10 種，
    沒有出現兩個以上空格的情況；仍用 split(maxsplit=1) 防雙空格。
    """
    parts = (raw or "").strip().split(" ", 1)
    return (parts[0], parts[1].strip() if len(parts) > 1 else "")


def load(cfg=None):
    """載入快照，回 (rows, meta)。rows 是 dict list，欄位同 COLUMNS。

    任何讀不到/格式不符都丟 DirectoryUnavailable——呼叫端要能安全退回線上。
    """
    path = snapshot_path(cfg)
    if not os.path.exists(path):
        raise DirectoryUnavailable(
            f"離線通訊錄快照不存在（找過 {path}）；"
            "用 build_directory.py 從 UOF 分機頁匯出的 txt 建立，或改用線上查詢")
    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter="\t")
            if reader.fieldnames != COLUMNS:
                raise DirectoryUnavailable(
                    f"快照表頭不符（預期 {COLUMNS}，實得 {reader.fieldnames}）；請重跑 build_directory.py")
            rows = [{k: (r.get(k) or "").strip() for k in COLUMNS} for r in reader]
    except DirectoryUnavailable:
        raise
    except Exception as e:
        raise DirectoryUnavailable(f"快照 {path} 讀取失敗：{e}")
    if not rows:
        raise DirectoryUnavailable(f"快照 {path} 是空的；請重跑 build_directory.py")

    meta = {}
    mp = meta_path(path)
    if os.path.exists(mp):
        try:
            with open(mp, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}  # meta 壞掉不致命，資料本身還能用
    return rows, meta


def query(rows, name=None, ext=None, empno=None, dept=None, team=None,
          rank=None, title=None):
    """依條件過濾。多條件之間是 AND。全空回全部（呼叫端自行決定要不要允許）。

    比對語意：
    - name：子字串，同時比對中文姓名與 Email 帳號部分（英文名查得到，
      因為 UOF 的 Email 帳號就是英文名，例如 jiunchiwang）
    - ext / empno：精確比對（員編不分大小寫；分機是 4 碼，子字串會誤中）
    - dept / team / rank / title：子字串（可下「線上研」抓一整群部門）
    """
    def hit(r):
        if name:
            n = name.strip().lower()
            local = r["email"].split("@", 1)[0].lower()
            if n not in r["name"].lower() and n not in local:
                return False
        if ext and r["ext"] != ext.strip():
            return False
        if empno and r["empno"].lower() != empno.strip().lower():
            return False
        for key, val in (("dept", dept), ("team", team), ("rank", rank), ("title", title)):
            if val and val.strip() not in r[key]:
                return False
        return True

    return [r for r in rows if hit(r)]


def count_by(rows, field):
    """聚合計數，回 [{"value":…, "count":…}]，多到少排序。空值歸「(未填)」。"""
    if field not in COLUMNS:
        raise ValueError(f"--count-by 只能是 {'/'.join(COLUMNS)}，收到 {field}")
    tally = {}
    for r in rows:
        key = r[field] or "(未填)"
        tally[key] = tally.get(key, 0) + 1
    return [{"value": k, "count": v}
            for k, v in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))]


def _main():
    ap = argparse.ArgumentParser(
        prog="directory.py",
        description="離線查 IGS 通訊錄（不需內網、不開瀏覽器）")
    ap.add_argument("--name", help="姓名關鍵字（中文或英文名，子字串）")
    ap.add_argument("--ext", help="分機（精確）")
    ap.add_argument("--empno", help="員工編號（精確）")
    ap.add_argument("--dept", help="部門關鍵字（子字串，如『線上研一部』或『線上研』）")
    ap.add_argument("--team", help="組別關鍵字（子字串）")
    ap.add_argument("--rank", help="職級關鍵字（部長/副部長/組長/…）")
    ap.add_argument("--title", help="職稱關鍵字（主任/副理/經理/…）")
    ap.add_argument("--count-by", dest="count_by",
                    help=f"改回聚合計數而非名單，欄位擇一：{'/'.join(COLUMNS)}")
    ap.add_argument("--limit", type=int, default=50,
                    help="最多回幾筆名單（預設 50；total 一律回真實筆數，截斷會標 truncated）")
    args = ap.parse_args()

    try:
        rows, meta = load()
    except DirectoryUnavailable as e:
        print(json.dumps({"error": "directory_unavailable", "hint": e.hint}, ensure_ascii=False))
        sys.exit(5)

    hits = query(rows, name=args.name, ext=args.ext, empno=args.empno,
                 dept=args.dept, team=args.team, rank=args.rank, title=args.title)
    out = {"source": "offline_snapshot", "total": len(hits)}
    if meta.get("snapshot_date"):
        out["updated_at"] = meta["snapshot_date"]

    if args.count_by:
        try:
            out["counts"] = count_by(hits, args.count_by)
        except ValueError as e:
            print(json.dumps({"error": "bad_args", "hint": str(e)}, ensure_ascii=False))
            sys.exit(5)
    else:
        out["people"] = hits[:args.limit]
        if len(hits) > args.limit:
            out["truncated"] = f"僅列前 {args.limit} 筆，共 {len(hits)} 筆；加 --limit 或縮小條件"

    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    _main()
