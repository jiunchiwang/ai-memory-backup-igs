#!/usr/bin/env python3
"""
leave 子命令：請假資料查詢（BAA）。假別/起訖/時數/事由/簽核狀態，自動翻頁合併（每頁 20 筆）。
餘額僅特休可查（hours --annual-leave）；其他假別 UOF 無餘額頁。
"""
import datetime, re
from uof_client import BASE, ScrapeFailed, SessionExpired

BAA = "Project/BAA/Search.aspx"
DATE_RE = re.compile(r"^\d{4}/\d\d/\d\d$")
ROW_DATE = re.compile(r"^\d{4}/\d\d/\d\d \d\d:\d\d$")
MAX_PAGES = 50
STATUS_CHOICES = ["全部", "同意", "否決", "簽核中", "作廢"]


def add_args(ap):
    ap.add_argument("--leave-from", dest="leave_from", default=None, help="起日 YYYY/MM/DD（預設今年 1/1）")
    ap.add_argument("--leave-to", dest="leave_to", default=None, help="迄日 YYYY/MM/DD（預設今年 12/31）")
    ap.add_argument("--kind", default=None, help="假別（如 特休假、事假；預設全部）")
    ap.add_argument("--status", default=None, choices=STATUS_CHOICES, help="簽核狀態（預設全部）")


def _js_set(page, elem_id, value):
    page.evaluate(
        """({id,v})=>{const el=document.getElementById(id);if(el){el.value=v;el.dispatchEvent(new Event('change',{bubbles:true}));}}""",
        {"id": elem_id, "v": value})


def _wait_settle(page, ms=2500):
    page.wait_for_timeout(ms)
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass


def _grid_rows(page):
    """讀 #GridView1 的資料列（9 欄且開始時間為日期格式）。"""
    rows = page.eval_on_selector_all(
        "#GridView1 tr",
        "els => els.map(r => [...r.cells].map(c => c.innerText.trim()))")
    out = []
    for cells in rows:
        # 資料列 9 欄＋尾端可能有隱藏欄（實測 10 欄，最後為隱藏的 "0"）
        if len(cells) >= 9 and ROW_DATE.match(cells[3]):
            out.append({
                "dept": cells[0],
                "kind": cells[2],
                "start": cells[3],
                "end": cells[4],
                "hours": cells[5],
                "reason": cells[6],
                "status": cells[8],
            })
    return out


def run(page, args, cfg):
    today = datetime.date.today()
    sdate = args.leave_from or f"{today.year}/01/01"
    edate = args.leave_to or f"{today.year}/12/31"
    if not (DATE_RE.match(sdate) and DATE_RE.match(edate)):
        raise ScrapeFailed("leave", f"日期格式須為 YYYY/MM/DD（收到 {sdate} ~ {edate}）")

    page.goto(BASE + BAA, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)
    if "login.aspx" in page.url.lower():
        raise SessionExpired()
    for sel in ("#SDate", "#BtnSubmit", "#KindList", "#StsList"):
        if not page.query_selector(sel):
            raise ScrapeFailed("leave", f"請假資料查詢頁結構改變（找不到 {sel}）")
    if args.kind:
        try:
            page.select_option("#KindList", label=args.kind)
        except Exception:
            opts = page.eval_on_selector_all("#KindList option", "els => els.map(e=>e.innerText.trim())")
            raise ScrapeFailed("leave", f"假別「{args.kind}」不存在；可用：{'、'.join(opts)}")
    if args.status and args.status != "全部":
        try:
            page.select_option("#StsList", label=args.status)
        except Exception:
            raise ScrapeFailed("leave", f"無法選擇簽核狀態「{args.status}」")
    _js_set(page, "SDate", sdate)
    _js_set(page, "EDate", edate)
    page.click("#BtnSubmit")
    _wait_settle(page)

    body = page.inner_text("body")
    tot = re.search(r"總筆數[：:]\s*(\d+)", body)
    if tot is None:
        raise ScrapeFailed("leave", f"請假資料查詢頁找不到總筆數（{sdate}~{edate}），版型可能改變")
    total = int(tot.group(1))
    records = _grid_rows(page)

    # 自動翻頁：pager 連結 __doPostBack('GridView1','Page$N')
    pageno = 2
    while pageno <= MAX_PAGES:
        link = page.query_selector(f"#GridView1 a[href*=\"Page${pageno}\"]")
        if link is None:
            break
        link.click()
        _wait_settle(page)
        got = _grid_rows(page)
        if not got:
            raise ScrapeFailed("leave", f"翻到第 {pageno} 頁後解析不到資料列，版型可能改變")
        records.extend(got)
        pageno += 1

    if total != len(records):
        raise ScrapeFailed("leave", f"請假解析筆數 {len(records)} 與頁面總筆數 {total} 不符（翻頁可能失敗）")
    return {"period": f"{sdate}~{edate}", "kind": args.kind or "全部",
            "status": args.status or "全部", "total": total, "records": records}
