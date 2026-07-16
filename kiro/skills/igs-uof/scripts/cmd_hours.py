#!/usr/bin/env python3
"""
hours 子命令：加班時數（本月/當年度/逐月）＋個人加班目標進度分析＋剩餘特休。
邏輯自 v1 uof_query.py 原樣搬移（回歸基準），僅 scrape_failed 由 die 改為 raise ScrapeFailed。
"""
import datetime, re
from uof_client import BASE, ScrapeFailed, SessionExpired, fnum

HOURS_PER_DAY = 8.0
MONTH_END = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
LEAVE_FORM = "WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=14ac1707-9566-4f02-b895-3da0e7395310"
OT_STAT = "Project/BAE/Stats_Search.aspx"


def add_args(ap):
    ap.add_argument("--overtime-month", action="store_true", help="本月加班")
    ap.add_argument("--overtime-year", action="store_true", help="當年度加班")
    ap.add_argument("--annual-leave", action="store_true", help="剩餘特休")
    ap.add_argument("--analysis", action="store_true", help="逐月明細＋個人目標進度分析（含本月/當年度）")
    ap.add_argument("--target", type=float, default=None, help="個人每月加班目標時數（覆蓋設定檔；預設 20）")
    ap.add_argument("--approved-only", action="store_true", help="只算『同意』，不含『簽核中』")
    ap.add_argument("--basis", choices=["weekday+holiday", "total"], default=None,
                    help="計入基準（覆蓋設定檔；預設 weekday+holiday，不含補班）")


def leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def month_range(year, mo):
    end = MONTH_END[mo]
    if mo == 2 and leap(year):
        end = 29
    return f"{year}/{mo:02d}/01", f"{year}/{mo:02d}/{end:02d}"


def overtime_range(page, sdate, edate, status_idx):
    """查加班統計某區間，回 dict(weekday, holiday, makeup, records)。"""
    page.goto(BASE + OT_STAT, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(900)
    if "login.aspx" in page.url.lower():
        raise SessionExpired()
    # JS 設日期，避開 datepicker 蓋住按鈕
    page.evaluate("""({s,e})=>{const set=(id,v)=>{const el=document.getElementById(id);if(el){el.value=v;el.dispatchEvent(new Event('change',{bubbles:true}));}};set('SDate',s);set('EDate',e);}""",
                  {"s": sdate, "e": edate})
    # 明確設定 4 個簽核狀態 checkbox 的目標狀態（要的 check、不要的 uncheck）。
    # 只勾要的並不夠——頁面預設可能已勾「簽核中」，不主動取消就會混入過濾結果；
    # 預期 checkbox 缺失代表版型改變，直接報錯而非讓過濾靜默失效。
    for i in range(4):  # _0 同意 / _1 否決 / _2 簽核中 / _3 作廢
        cb = f"#StsChkBoxList_{i}"
        if not page.query_selector(cb):
            raise ScrapeFailed("overtime", f"加班統計頁簽核狀態選項結構改變（找不到 {cb}），過濾條件無法確保正確")
        try:
            if i in status_idx:
                page.check(cb)
            else:
                page.uncheck(cb)
        except Exception as e:
            raise ScrapeFailed("overtime", f"無法設定簽核狀態 {cb}：{e}")
    page.keyboard.press("Escape")
    page.evaluate("() => { const d=document.getElementById('ui-datepicker-div'); if(d) d.style.display='none'; }")
    page.evaluate("() => __doPostBack('BtnSubmit','')")
    page.wait_for_timeout(2500)
    try:
        page.wait_for_load_state("networkidle", timeout=12000)
    except Exception:
        pass
    body = page.inner_text("body")
    tot = re.search(r'總筆數[：:]\s*(\d+)', body)
    m = re.search(r'平日加班時數合計：\s*([\d.]*)\s*小時.*?假日加班時數合計：\s*([\d.]*)\s*小時.*?補班時數合計：\s*([\d.]*)',
                  body, re.S)
    if not m:
        # 0 筆時 UOF 不渲染合計 footer（實測「總筆數：0」且整段合計列消失）→ 視為 0 小時，不中斷整份分析
        if (tot and int(tot.group(1)) == 0) or "查無資料" in body:
            return {"weekday": 0.0, "holiday": 0.0, "makeup": 0.0, "records": 0}
        raise ScrapeFailed("overtime", f"加班統計頁找不到合計（{sdate}~{edate}）")
    wd, hd, mk = fnum(m.group(1)), fnum(m.group(2)), fnum(m.group(3))
    if tot is None:
        # 合計有值但總筆數缺失＝版型半改——報錯，不要回 records=0 這種自相矛盾的輸出
        raise ScrapeFailed("overtime", f"加班統計頁有合計但找不到總筆數（{sdate}~{edate}），版型可能改變")
    return {"weekday": wd, "holiday": hd, "makeup": mk, "records": int(tot.group(1))}


def shape_ot(raw, basis):
    """加上 countable / total 欄位。basis: 'weekday+holiday' 或 'total'。"""
    countable = raw["weekday"] + raw["holiday"] if basis == "weekday+holiday" else raw["weekday"] + raw["holiday"] + raw["makeup"]
    return {
        "weekday": round(raw["weekday"], 1),
        "holiday": round(raw["holiday"], 1),
        "makeup": round(raw["makeup"], 1),
        "countable": round(countable, 1),
        "total": round(raw["weekday"] + raw["holiday"] + raw["makeup"], 1),
        "records": raw["records"],
    }


def annual_leave(page):
    page.goto(BASE + LEAVE_FORM, wait_until="networkidle", timeout=40000)
    page.wait_for_timeout(5000)
    if "login.aspx" in page.url.lower():
        raise SessionExpired()
    txt = ""
    for f in page.frames:
        try:
            t = f.inner_text("body")
        except Exception:
            t = ""
        if "特休未休" in t:
            txt = t
            break
    m = re.search(r'(\d{4}/\d\d/\d\d)~(\d{4}/\d\d/\d\d)特休未休([\d.]+)小時\s*=\s*應休([\d.]+)小時-已休([\d.]+)小時', txt)
    if not m:
        raise ScrapeFailed("annual_leave", "請假單表頭找不到特休未休字串")
    p1, p2, remain, entitled, used = m.groups()
    return {
        "period": f"{p1}~{p2}",
        "remaining_h": float(remain),
        "entitled_h": float(entitled),
        "used_h": float(used),
        "remaining_days": round(float(remain) / HOURS_PER_DAY, 1),
    }


def _month_end(today):
    if today.month == 12:
        return datetime.date(today.year, 12, 31)
    return datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)


def _prorated_months_elapsed(today):
    """已完成整月數 + 當月已過工作日比例。用來算『到今天為止的目標累計』，
    避免把進行中的當月當作整月到期(否則月中 on-pace 會被誤判為進度落後)。"""
    import calendar_workdays as C
    first = datetime.date(today.year, today.month, 1)
    total, _, _ = C.count_workdays(today.year, first, _month_end(today))
    elapsed, _, _ = C.count_workdays(today.year, first, today)  # 含今天
    frac = (elapsed / total) if total else 1.0
    return round((today.month - 1) + frac, 3)


def month_status(target, month_done, today):
    """本月目標進度：距目標還差幾小時、本月剩幾個上班日、平均每上班日要加幾小時。
    查加班時數一律附上（回應用戶要求）。從隔天起算，今天當已過。"""
    import calendar_workdays as C
    tmr = today + datetime.timedelta(days=1)
    wm, source, note = C.count_workdays(today.year, tmr, _month_end(today))
    need = round(target - month_done, 1)
    st = {
        "target": target,
        "done": round(month_done, 1),
        "still_needed": need,                    # 距本月目標還差多少小時
        "remaining_workdays": wm,                # 本月還剩幾個上班日
        "per_workday": round(need / wm, 2) if wm > 0 else None,  # 平均每天要加幾小時
        "counted_from": tmr.isoformat(),
        "workday_source": source,
    }
    if note:
        st["workday_note"] = note
    return st


def workday_analysis(target, ytd, month_done, today):
    """『每個上班日還要加多少』兩判斷：(A)追全年平均 (B)追本月。工作天來源見 workday_source。"""
    import calendar_workdays as C
    tmr = today + datetime.timedelta(days=1)
    wy, source, note = C.count_workdays(today.year, tmr, datetime.date(today.year, 12, 31))
    ms = month_status(target, month_done, today)
    year_need = round(target * 12 - ytd, 1)
    out = {
        "counted_from": tmr.isoformat(),
        "workday_source": source,
        "remaining_workdays_year": wy,
        "remaining_workdays_month": ms["remaining_workdays"],
        "year_still_needed": year_need,
        "month_still_needed": ms["still_needed"],
        "per_workday_year": round(year_need / wy, 2) if wy > 0 else None,   # (A) 追全年平均
        "per_workday_month": ms["per_workday"],                            # (B) 追本月
    }
    if note:
        out["workday_note"] = note
    return out


def run(page, args, cfg):
    """執行 hours 查詢，回 {"params":…, "overtime":…, "annual_leave":…}（依 flags 取捨）。
    uof.py 會把這些鍵直接併到頂層（沿用 v1 輸出形狀，保回歸基準）。"""
    # 沒指定任何項目 → 全查（v1 預設）
    if not (args.overtime_month or args.overtime_year or args.annual_leave or args.analysis):
        args.analysis = True
        args.annual_leave = True
    if args.analysis:
        args.overtime_month = args.overtime_year = True
    # 查任何加班一律附本月目標進度(month.status);故查當年度時也一併帶本月
    if args.overtime_year:
        args.overtime_month = True

    # 參數優先序：CLI > 設定檔 > 內建預設
    target = args.target if args.target is not None else float(cfg.get("monthly_target", 20))
    basis = args.basis or cfg.get("countable_basis", "weekday+holiday")
    status_str = "approved" if args.approved_only else cfg.get("status", "approved+pending")
    status_idx = [0] if status_str == "approved" else [0, 2]  # 同意 / 同意+簽核中
    today = datetime.date.today()

    out = {"params": {"target_per_month": target, "countable_basis": basis, "status": status_str}}

    ot = {}
    if args.overtime_month:
        e = month_range(today.year, today.month)[1]
        s = f"{today.year}/{today.month:02d}/01"
        m = shape_ot(overtime_range(page, s, e, status_idx), basis)
        # 查加班時數一律附本月目標進度：距目標還差幾小時 / 本月剩幾個上班日 / 平均每天要加幾小時
        m["status"] = month_status(target, m["countable"], today)
        ot["month"] = m
    if args.overtime_year:
        ot["year"] = shape_ot(overtime_range(page, f"{today.year}/01/01", f"{today.year}/12/31", status_idx), basis)

    if args.analysis:
        by_month = {}
        for mo in range(1, today.month + 1):
            s, e = month_range(today.year, mo)
            by_month[str(mo)] = shape_ot(overtime_range(page, s, e, status_idx), basis)
        ot["by_month"] = by_month
        ytd = round(sum(v["countable"] for v in by_month.values()), 1)
        months_elapsed = today.month
        remaining_full = 12 - today.month
        annual_target = round(target * 12, 1)
        still_needed = round(annual_target - ytd, 1)
        month_done = ot.get("month", {}).get("countable", 0.0)
        # 到今天的目標累計:已完成整月 + 當月按已過工作日比例(月中不會誤判進度落後)
        prorated = _prorated_months_elapsed(today)
        target_to_date = round(target * prorated, 1)
        ot["analysis"] = {
            "target_per_month": target,
            "countable_basis": basis,
            "months_elapsed": months_elapsed,
            "ytd_countable": ytd,
            "target_to_date": target_to_date,   # 到今天(當月按工作日比例)的目標累計
            "gap_ytd": round(ytd - target_to_date, 1),  # 負=較目標進度落後、正=超前;月中已按比例校正
            "annual_target": annual_target,
            "still_needed_this_year": still_needed,
            "remaining_full_months": remaining_full,
            "need_per_remaining_month": round(still_needed / remaining_full, 1) if remaining_full > 0 else None,
            "workday_calc": workday_analysis(target, ytd, month_done, today),
        }

    if ot:
        out["overtime"] = ot
    if args.annual_leave:
        out["annual_leave"] = annual_leave(page)
    return out
