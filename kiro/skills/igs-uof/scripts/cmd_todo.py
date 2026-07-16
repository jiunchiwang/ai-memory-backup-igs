#!/usr/bin/env python3
"""
todo 子命令：電子簽核個人表單。
預設：待簽核件數（分類樹）＋待簽清單；--sent 改查已送審表單的簽核進度。
"""
import re
from uof_client import BASE, ScrapeFailed, SessionExpired

SIGN_SELF = "WKF/FormUse/PersonalBox/MyFormList.aspx?item=SignSelf"
FORM_EXAMINED = "WKF/FormUse/PersonalBox/MyFormList.aspx?item=FormExamined"

COUNT_PATTERNS = {
    "sign_self": r"待簽表單-自己\((\d+)\)",
    "sign_agent": r"待簽表單-代理\((\d+)\)",
    "returned": r"被退回的申請\((\d+)\)",
    "informed": r"被知會表單\((\d+)\)",
    "consulted": r"被徵詢表單\((\d+)\)",
}


def add_args(ap):
    ap.add_argument("--sent", action="store_true", help="改查自己送出的表單簽核進度（已送審表單）")


def _wait_page(page, url):
    page.goto(BASE + url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4500)
    if "login.aspx" in page.url.lower():
        raise SessionExpired()


def _counts(body):
    counts = {}
    for key, pat in COUNT_PATTERNS.items():
        m = re.search(pat, body)
        if m is None:
            raise ScrapeFailed("todo", f"個人表單分類樹找不到「{pat}」，版型可能改變")
        counts[key] = int(m.group(1))
    return counts


def _grids(page):
    """回傳頁面右側所有 grd* 表格的 (id, rows[cells])。"""
    return page.eval_on_selector_all(
        "table[id*='grd']",
        "els => els.map(t => [t.id, [...t.rows].map(r => [...r.cells].map(c => c.innerText.trim()))])")


def _rows_by_header(grids, want_header):
    """從 grd* 表格中找含 want_header 的表頭列（不一定是第一列——前面可能有
    「Export筆數」資訊列），回其後資料列的 dict 清單。"""
    for gid, rows in grids:
        hdr_i = next((i for i, r in enumerate(rows) if want_header in r), None)
        if hdr_i is None:
            continue
        header = rows[hdr_i]
        idx = {h: i for i, h in enumerate(header)}
        out = []
        for cells in rows[hdr_i + 1:]:
            if len(cells) < len(header) - 1:
                continue  # pager / 操作列
            def col(name):
                i = idx.get(name)
                return cells[i].strip() if i is not None and i < len(cells) else ""
            if not col("表單編號"):
                continue
            out.append({
                "no": col("表單編號"),
                "form": col("表單名稱"),
                "title": col("標題"),
                "applied_at": col("申請時間"),
                "closed_at": col("結案時間"),
                "current_signer": col("目前簽核者"),
            })
        return out
    return None


def run(page, args, cfg):
    if args.sent:
        _wait_page(page, FORM_EXAMINED)
        body = page.inner_text("body")
        counts = _counts(body)
        m = re.search(r"共\s*(\d+)\s*筆", body)
        forms = _rows_by_header(_grids(page), "表單編號")
        if forms is None:
            if "沒有資料" in body:
                forms = []
            else:
                raise ScrapeFailed("todo", "已送審表單頁找不到表單清單 grid，版型可能改變")
        # 「共 N 筆」缺失時不得靜默用 len(forms) 頂替——那會讓下方截斷提示永遠失效
        # （total==len(forms) 恆真），悄悄回報不完整清單。與其他子命令一致：報錯。
        if m:
            total = int(m.group(1))
        elif not forms:
            total = 0
        else:
            raise ScrapeFailed("todo", "已送審表單頁找不到「共 N 筆」字樣，版型可能改變")
        # 已送審清單每頁 10-20 筆；超過一頁時如數告知（進度追蹤通常只看最近幾筆，不翻頁）
        out = {"counts": counts, "total": total, "forms": forms}
        if total > len(forms):
            out["note"] = f"僅列出第一頁 {len(forms)} 筆（共 {total} 筆）；需要更早的請縮小日期範圍到 UOF 查"
        return out

    _wait_page(page, SIGN_SELF)
    body = page.inner_text("body")
    counts = _counts(body)
    items = _rows_by_header(_grids(page), "表單編號")
    if items is None:
        items = []  # 0 件時右側顯示「沒有資料」；列格式在有待簽件時才可驗證
    pending = counts["sign_self"] + counts["sign_agent"]
    out = {"counts": counts, "pending_total": pending, "items": items}
    # 分類樹件數（pending）是真總數；清單只讀當前頁 DOM——不對稱時如數告知，別讓
    # 「pending_total: 15 但 items 只有 10 筆」看起來像已列完
    if pending > len(items):
        out["note"] = f"清單僅列出當前頁 {len(items)} 筆（待簽共 {pending} 筆），完整清單請上 UOF 看"
    return out
