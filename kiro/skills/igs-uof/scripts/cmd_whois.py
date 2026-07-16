#!/usr/bin/env python3
"""
whois 子命令：電話分機查詢（CDS/WebPage/ExtQuery.aspx）。
姓名/分機/員編至少帶一個條件；回部門/組/姓名/分機/員編/Email。資料每小時更新。
"""
import re
from uof_client import BASE, ScrapeFailed, SessionExpired, die

EXT_QUERY = "CDS/WebPage/ExtQuery.aspx"


def add_args(ap):
    ap.add_argument("--name", default=None, help="姓名關鍵字（中文或英文名）")
    ap.add_argument("--ext", default=None, help="分機號碼")
    ap.add_argument("--empno", default=None, help="員工編號")


def validate(ns):
    if not (ns.name or ns.ext or ns.empno):
        die(5, "bad_args", hint="whois 至少提供 --name/--ext/--empno 其中一個（全公司清單請直接上 UOF 查）")


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
            return {"total": 0, "people": []}
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
            people.append({
                "dept": col("部門"),
                "team": col("組"),
                "name": col("姓名"),
                "ext": col("分機"),
                "empno": col("員工編號"),
                "email": col("Email"),
            })
        if len(people) != total:
            raise ScrapeFailed("whois", f"分機解析筆數 {len(people)} 與頁面筆數 {total} 不符，版型可能改變")
    out = {"total": total, "people": people}
    if upd:
        out["updated_at"] = upd.group(1).strip()
    return out
