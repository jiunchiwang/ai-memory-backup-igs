#!/usr/bin/env python3
"""
whois 子命令：電話分機查詢。

兩條路徑：
- 離線（預設）：查 ~/.config/uof/directory.tsv 快照，秒回、不開瀏覽器、不需內網。
  額外支援線上頁面做不到的 --dept/--team/--rank/--title 名單與 --count-by 聚合。
- 線上（--online，或快照不存在時自動退回）：爬 CDS/WebPage/ExtQuery.aspx，資料每小時更新。

兩條路徑輸出形狀一致：name 是純姓名、職稱獨立在 title（UOF 頁面把兩者黏在同一欄）。
"""
import re

from directory import DirectoryUnavailable, count_by, load, query, split_name
from uof_client import BASE, ScrapeFailed, SessionExpired, die

EXT_QUERY = "CDS/WebPage/ExtQuery.aspx"

# 只有離線快照支援的條件（線上頁面沒有這些查詢欄位）
OFFLINE_ONLY = ("dept", "team", "rank", "title", "count_by")
# 可用來鎖定特定人的條件；線上查詢至少要有一個
IDENTITY = ("name", "ext", "empno")


def add_args(ap):
    ap.add_argument("--name", default=None, help="姓名關鍵字（中文或英文名）")
    ap.add_argument("--ext", default=None, help="分機號碼")
    ap.add_argument("--empno", default=None, help="員工編號")
    # 以下離線快照專用
    ap.add_argument("--dept", default=None, help="[離線] 部門關鍵字，如『線上研一部』或『線上研』")
    ap.add_argument("--team", default=None, help="[離線] 組別關鍵字")
    ap.add_argument("--rank", default=None, help="[離線] 職級：部長/副部長/組長/…")
    ap.add_argument("--title", default=None, help="[離線] 職稱：主任/資深主任/副理/經理/…")
    ap.add_argument("--count-by", dest="count_by", default=None,
                    help="[離線] 改回聚合計數：dept/team/rank/title/…")
    ap.add_argument("--limit", type=int, default=50,
                    help="[離線] 名單最多幾筆（預設 50；total 一律是真實筆數）")
    ap.add_argument("--online", action="store_true",
                    help="略過離線快照，直接爬 UOF 取最新（需內網＋登入，較慢）")


def _offline_flags(ns):
    return [f for f in OFFLINE_ONLY if getattr(ns, f, None)]


def validate(ns):
    """在開瀏覽器前 fail-fast：條件不足、或線上路徑收到離線專用 flag。"""
    used_offline = _offline_flags(ns)
    if ns.online and used_offline:
        die(5, "bad_args",
            hint=f"--online 不支援 {'/'.join('--' + f.replace('_', '-') for f in used_offline)}"
                 "（UOF 分機頁沒有這些查詢欄位）；拿掉 --online 走離線快照即可")
    if not any(getattr(ns, f, None) for f in IDENTITY) and not used_offline:
        die(5, "bad_args",
            hint="whois 至少要一個條件：--name/--ext/--empno，"
                 "或離線快照專用的 --dept/--team/--rank/--title/--count-by")


def run_offline(args, cfg):
    """離線快照查詢。回 None 表示「無法離線服務，請走線上」，由 uof.py 決定開瀏覽器。"""
    if args.online:
        return None

    used_offline = _offline_flags(args)
    try:
        rows, meta = load(cfg)
    except DirectoryUnavailable as e:
        if used_offline:
            # 這些條件線上做不到，不能默默退回線上假裝沒事
            return {"error": "directory_unavailable", "hint": e.hint}
        return None  # 只查單人 → 讓它退回線上，使用者無感

    hits = query(rows, name=args.name, ext=args.ext, empno=args.empno,
                 dept=args.dept, team=args.team, rank=args.rank, title=args.title)
    out = {"source": "offline_snapshot", "total": len(hits)}
    if meta.get("snapshot_date"):
        out["updated_at"] = meta["snapshot_date"]

    if args.count_by:
        try:
            out["counts"] = count_by(hits, args.count_by)
        except ValueError as e:
            return {"error": "bad_args", "hint": str(e)}
        return out

    out["people"] = hits[:args.limit]
    if len(hits) > args.limit:
        out["truncated"] = f"僅列前 {args.limit} 筆，共 {len(hits)} 筆；加 --limit 或縮小條件"
    if not hits:
        out["hint"] = (f"離線快照（{out.get('updated_at', '日期不明')}）查無此人；"
                       "若是新進同仁或近期異動，加 --online 查 UOF 最新資料")
    return out


def run(page, args, cfg):
    page.goto(BASE + EXT_QUERY, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)
    if "login.aspx" in page.url.lower():
        raise SessionExpired()
    for sel in ("#name_TB", "#searchBtn"):
        if not page.query_selector(sel):
            raise ScrapeFailed("whois", f"分機查詢頁結構改變（找不到 {sel}）")
    if args.name:
        page.fill("#name_TB", args.name)
    if args.ext:
        page.fill("#ext_TB", args.ext)
    if args.empno:
        page.fill("#empno_TB", args.empno)
    page.click("#searchBtn")
    page.wait_for_timeout(2500)
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass

    body = page.inner_text("body")
    m = re.search(r"查詢筆數[：:]\s*(\d+)\s*筆", body)
    if m is None:
        # 0 筆時頁面不渲染「查詢筆數」與 #resultGrid，只顯示「查無資料」（2026-07-15 實測）
        if "查無資料" in body:
            return {"source": "uof_live", "total": 0, "people": []}
        raise ScrapeFailed("whois", "分機查詢頁找不到「查詢筆數」，版型可能改變")
    total = int(m.group(1))
    upd = re.search(r"資料最後更新時間[：:]\s*([^\(（\n]+)", body)

    people = []
    if total > 0:
        rows = page.eval_on_selector_all(
            "#resultGrid tr",
            "els => els.map(r => [...r.cells].map(c => c.innerText.trim()))")
        if not rows:
            raise ScrapeFailed("whois", "分機查詢結果 #resultGrid 消失，版型可能改變")
        header = rows[0]
        need = ["部門", "姓名", "分機"]
        if not all(h in header for h in need):
            raise ScrapeFailed("whois", f"分機查詢表頭欄位改變（現為 {header}）")
        idx = {h: i for i, h in enumerate(header)}
        for cells in rows[1:]:
            if len(cells) < len(header) - 1:
                continue

            def col(name):
                i = idx.get(name)
                return cells[i].strip() if i is not None and i < len(cells) else ""

            if not col("姓名"):
                continue
            # 與離線快照對齊：姓名欄的職稱拆到 title（UOF 回的是『蘇清源 資深主任』）
            nm, title = split_name(col("姓名"))
            people.append({
                "dept": col("部門"),
                "team": col("組"),
                "name": nm,
                "title": title,
                "ext": col("分機"),
                "empno": col("員工編號"),
                "email": col("Email"),
            })
        if len(people) != total:
            raise ScrapeFailed("whois", f"分機解析筆數 {len(people)} 與頁面筆數 {total} 不符，版型可能改變")
    out = {"source": "uof_live", "total": total, "people": people}
    if upd:
        out["updated_at"] = upd.group(1).strip()
    return out
