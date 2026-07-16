#!/usr/bin/env python3
"""
attendance 子命令：出勤/打卡記錄。
預設查「出缺勤查詢」（VPPA，逐日彙總：刷卡起迄＋當日加班/請假；資料延遲約 2 天）；
--punch 改查「打卡資料查詢」（EQRsearch，即時刷卡流水，含今日）。
"""
import datetime, re
from uof_client import BASE, ScrapeFailed, SessionExpired

VPPA = "Project/VPPA/Search.aspx"
PUNCH_MENU = "System/CustomMenu/LinkUrl.aspx?menuID=39483847-5b19-4430-87c2-7699ea3c2742"
DATE_RE = re.compile(r"^\d{4}/\d\d/\d\d$")
PUNCH_ROW = re.compile(r"^\d+\t(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\t[^\t]+\t(.+)$")
DELAY_NOTE = "出缺勤彙總資料延遲約 2 天；查今天/昨天的打卡請改用 --punch（即時刷卡流水）"


def add_args(ap):
    ap.add_argument("--from", dest="att_from", default=None, help="起日 YYYY/MM/DD（預設本月 1 日）")
    ap.add_argument("--to", dest="att_to", default=None, help="迄日 YYYY/MM/DD（預設今天）")
    ap.add_argument("--punch", action="store_true", help="改查即時刷卡流水（含今日；預設查逐日彙總，延遲約 2 天）")


def _js_set(target, elem_id, value):
    target.evaluate(
        """({id,v})=>{const el=document.getElementById(id);if(el){el.value=v;el.dispatchEvent(new Event('change',{bubbles:true}));}}""",
        {"id": elem_id, "v": value})


def _wait_settle(page, ms=2500):
    page.wait_for_timeout(ms)
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass


def _date_range(args):
    today = datetime.date.today()
    s = args.att_from or f"{today.year}/{today.month:02d}/01"
    e = args.att_to or today.strftime("%Y/%m/%d")
    if not (DATE_RE.match(s) and DATE_RE.match(e)):
        raise ScrapeFailed("attendance", f"日期格式須為 YYYY/MM/DD（收到 {s} ~ {e}）")
    return s, e


def _summary(page, sdate, edate):
    """VPPA 出缺勤查詢：逐日彙總。"""
    page.goto(BASE + VPPA, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)
    if "login.aspx" in page.url.lower():
        raise SessionExpired()
    if not page.query_selector("#SDate") or not page.query_selector("#BtnSubmit"):
        raise ScrapeFailed("attendance", "出缺勤查詢頁結構改變（找不到 #SDate/#BtnSubmit）")
    _js_set(page, "SDate", sdate)
    _js_set(page, "EDate", edate)
    page.click("#BtnSubmit")
    _wait_settle(page)
    body = page.inner_text("body")
    tot = re.search(r"總筆數[：:]\s*(\d+)", body)
    days = []
    for line in body.splitlines():
        cells = line.split("\t")
        if len(cells) < 14 or not DATE_RE.match(cells[2].strip()):
            continue
        d = {
            "date": cells[2].strip(),
            "type": cells[3].strip() or None,       # 出勤類別（正常日為空）
            "first_in": cells[4].strip() or None,   # 刷卡起時 HHMM
            "last_out": cells[5].strip() or None,   # 刷卡迄時 HHMM
        }
        if cells[6].strip():   # 加班類別
            d["overtime"] = {"kind": cells[6].strip(), "start": cells[7].strip(),
                             "end": cells[8].strip(), "hours": cells[9].strip()}
        if cells[10].strip():  # 請假類別
            d["leave"] = {"kind": cells[10].strip(), "start": cells[11].strip(),
                          "end": cells[12].strip(), "hours": cells[13].strip()}
        days.append(d)
    if tot is None:
        raise ScrapeFailed("attendance", f"出缺勤查詢頁找不到總筆數（{sdate}~{edate}），版型可能改變")
    total = int(tot.group(1))
    if total != len(days):
        raise ScrapeFailed("attendance", f"出缺勤解析筆數 {len(days)} 與頁面總筆數 {total} 不符，版型可能改變")
    days.sort(key=lambda x: x["date"])
    return {"source": "summary", "period": f"{sdate}~{edate}", "total": total,
            "days": days, "note": DELAY_NOTE}


def _punch(page, sdate, edate):
    """EQRsearch 打卡資料查詢：即時刷卡流水（經 LinkUrl 的 token iframe）。"""
    page.goto(BASE + PUNCH_MENU, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3500)
    if "login.aspx" in page.url.lower():
        raise SessionExpired()
    fr = next((f for f in page.frames if "EQRsearch" in f.url), None)
    if fr is None or not fr.query_selector("#stime"):
        raise ScrapeFailed("attendance", "打卡資料查詢頁結構改變（找不到 EQRsearch frame 或 #stime）")
    _js_set(fr, "stime", sdate)
    _js_set(fr, "etime", edate)
    fr.click("#Submit")
    page.wait_for_timeout(4000)
    fr = next((f for f in page.frames if "EQRsearch" in f.url), None)
    if fr is None:
        raise ScrapeFailed("attendance", "打卡查詢送出後 EQRsearch frame 消失")
    body = fr.inner_text("body")
    tot = re.search(r"總筆數[：:]\s*(\d+)", body)
    punches = []
    for line in body.splitlines():
        m = PUNCH_ROW.match(line.strip())
        if m:
            punches.append({"time": m.group(1), "gate": m.group(2).strip()})
    if tot is None:
        raise ScrapeFailed("attendance", f"打卡查詢頁找不到總筆數（{sdate}~{edate}），版型可能改變")
    total = int(tot.group(1))
    if total != len(punches):
        raise ScrapeFailed("attendance", f"打卡解析筆數 {len(punches)} 與頁面總筆數 {total} 不符，版型可能改變")
    return {"source": "punch", "period": f"{sdate}~{edate}", "total": total, "punches": punches}


def run(page, args, cfg):
    sdate, edate = _date_range(args)
    if args.punch:
        return _punch(page, sdate, edate)
    return _summary(page, sdate, edate)
