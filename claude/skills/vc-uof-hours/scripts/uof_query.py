#!/usr/bin/env python3
"""
查詢公司內網 UOF（U-Office Force）的加班時數與剩餘特休，並做加班達標分析。
帳密讀設定檔 ~/.config/uof/config.json（macOS 可 fallback Keychain uof-hr）。輸出單一 JSON 到 stdout。

用法：
  uof_query.py                 # 全查（本月+當年度+逐月分析+特休）
  uof_query.py --overtime-month --annual-leave
  uof_query.py --target 22 --approved-only
  uof_query.py --headed        # 有頭模式（登入被要求驗證碼時手動過）

離開碼：0 成功；2 連不到內網；3 登入失敗/驗證碼；4 抓取失敗；5 其他。
"""
import argparse, subprocess, sys, os, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 強制 stdout/stderr 為 UTF-8：Windows subprocess pipe 預設 cp950(Big5)，
# 輸出含中文(錯誤 hint / workday_note / 行事曆檔名)會亂碼或 UnicodeEncodeError。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass
from playwright.sync_api import sync_playwright

BASE = "http://uof/UOF/"
KEYCHAIN_SERVICE = "uof-hr"
HOURS_PER_DAY = 8.0
CONFIG_PATH = os.environ.get("UOF_CONFIG") or os.path.expanduser("~/.config/uof/config.json")
MONTH_END = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
LEAVE_FORM = "WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=14ac1707-9566-4f02-b895-3da0e7395310"
OT_STAT = "Project/BAE/Stats_Search.aspx"


def die(code, err, **extra):
    print(json.dumps({"error": err, **extra}, ensure_ascii=False))
    sys.exit(code)


SETUP_HINT = {
    "config": f"請建立設定檔 {CONFIG_PATH}，內容範例見 skill 目錄的 config.example.json："
              '{"account":"你的UOF帳號","password":"你的密碼","monthly_target":20}',
    "mac_keychain": '（macOS 也可改用 Keychain：security add-generic-password -s uof-hr -a <帳號> -U -w）',
}


def _keychain_get(field):
    """僅 macOS：讀 Keychain service uof-hr。取不到回 None。"""
    if sys.platform != "darwin":
        return None
    try:
        if field == "acct":
            r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE],
                               capture_output=True, text=True)
            if r.returncode != 0:
                return None
            for line in r.stdout.splitlines():
                if '"acct"' in line:
                    return line.split('="', 1)[1].rstrip('"') or None
            return None
        r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                           capture_output=True, text=True)
        return r.stdout.strip() or None if r.returncode == 0 else None
    except Exception:
        return None


def load_config():
    """讀設定檔（跨 Mac/Windows）；不存在回 {}。"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            die(5, "bad_config", hint=f"設定檔 {CONFIG_PATH} 解析失敗：{e}")
    return {}


def resolve_credentials(cfg):
    """帳密優先序：環境變數 > 設定檔 > (macOS)Keychain。取不到給跨平台設定教學。"""
    acct = os.environ.get("UOF_ACCOUNT") or cfg.get("account") or _keychain_get("acct")
    pw = os.environ.get("UOF_PASSWORD") or cfg.get("password") or _keychain_get("pwd")
    if not acct or not pw:
        die(3, "no_credential",
            config_path=CONFIG_PATH,
            hint=SETUP_HINT["config"] + (SETUP_HINT["mac_keychain"] if sys.platform == "darwin" else ""))
    return acct, pw


def leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def month_range(year, mo):
    end = MONTH_END[mo]
    if mo == 2 and leap(year):
        end = 29
    return f"{year}/{mo:02d}/01", f"{year}/{mo:02d}/{end:02d}"


def fnum(x):
    x = (x or "").strip()
    return float(x) if x else 0.0


def _safe_visible(page, sel):
    """導頁中呼叫 selector 會拋 context destroyed，統一吞掉當作不可見。"""
    try:
        el = page.query_selector(sel)
        return bool(el and el.is_visible())
    except Exception:
        return False


def login(page, acct, pw):
    page.goto(BASE + "Login.aspx", wait_until="domcontentloaded", timeout=20000)
    page.fill("#txtAccount", acct)
    page.fill("#txtPwd", pw)
    page.click("#btnSubmit")
    # 等：登入成功離開 Login / 出現重複登入 / 驗證碼
    for _ in range(40):  # 最多約 20s
        page.wait_for_timeout(500)
        try:
            url = page.url
        except Exception:
            continue  # 導頁進行中
        if "login.aspx" not in url.lower():
            page.wait_for_timeout(500)
            return
        if _safe_visible(page, "#btnRemoveRepeatLogin"):
            try:
                page.click("#btnRemoveRepeatLogin")  # 踢掉另一 session 才能登入
                page.wait_for_timeout(3000)
            except Exception:
                pass
            continue
        if _safe_visible(page, "#captchaImage"):
            die(3, "captcha", hint="登入被要求驗證碼，請用 --headed 手動輸入一次")
    try:
        final = page.url.lower()
    except Exception:
        final = "login.aspx"
    if "login.aspx" in final:
        die(3, "login_failed", hint="登入未成功（帳密可能有誤，或被要求驗證碼）")


def overtime_range(page, sdate, edate, status_idx):
    """查加班統計某區間，回 dict(weekday, holiday, makeup, records)。"""
    page.goto(BASE + OT_STAT, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(900)
    if "login.aspx" in page.url.lower():
        die(3, "session_expired")
    # JS 設日期，避開 datepicker 蓋住按鈕
    page.evaluate("""({s,e})=>{const set=(id,v)=>{const el=document.getElementById(id);if(el){el.value=v;el.dispatchEvent(new Event('change',{bubbles:true}));}};set('SDate',s);set('EDate',e);}""",
                  {"s": sdate, "e": edate})
    # 明確設定 4 個簽核狀態 checkbox 的目標狀態（要的 check、不要的 uncheck）。
    # 只勾要的並不夠——頁面預設可能已勾「簽核中」，不主動取消就會混入過濾結果；
    # 預期 checkbox 缺失代表版型改變，直接報錯而非讓過濾靜默失效。
    for i in range(4):  # _0 同意 / _1 否決 / _2 簽核中 / _3 作廢
        cb = f"#StsChkBoxList_{i}"
        if not page.query_selector(cb):
            die(4, "scrape_failed", page="overtime",
                hint=f"加班統計頁簽核狀態選項結構改變（找不到 {cb}），過濾條件無法確保正確")
        try:
            if i in status_idx:
                page.check(cb)
            else:
                page.uncheck(cb)
        except Exception as e:
            die(4, "scrape_failed", page="overtime", hint=f"無法設定簽核狀態 {cb}：{e}")
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
        die(4, "scrape_failed", page="overtime", hint=f"加班統計頁找不到合計（{sdate}~{edate}）")
    wd, hd, mk = fnum(m.group(1)), fnum(m.group(2)), fnum(m.group(3))
    return {"weekday": wd, "holiday": hd, "makeup": mk, "records": int(tot.group(1)) if tot else 0}


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
        die(3, "session_expired")
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
        die(4, "scrape_failed", page="annual_leave", hint="請假單表頭找不到特休未休字串")
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
    """已完成整月數 + 當月已過工作日比例。用來算『到今天為止應達成的目標』，
    避免把進行中的當月當作整月到期(否則月中 on-pace 會被誤判為落後)。"""
    import calendar_workdays as C
    first = datetime.date(today.year, today.month, 1)
    total, _, _ = C.count_workdays(today.year, first, _month_end(today))
    elapsed, _, _ = C.count_workdays(today.year, first, today)  # 含今天
    frac = (elapsed / total) if total else 1.0
    return round((today.month - 1) + frac, 3)


def month_status(target, month_done, today):
    """本月達標現況：還差幾小時、本月剩幾個上班日、平均每上班日要加幾小時。
    查加班時數一律附上（回應用戶要求）。從隔天起算，今天當已過。"""
    import calendar_workdays as C
    tmr = today + datetime.timedelta(days=1)
    wm, source, note = C.count_workdays(today.year, tmr, _month_end(today))
    need = round(target - month_done, 1)
    st = {
        "target": target,
        "done": round(month_done, 1),
        "still_needed": need,                    # 本月還差多少小時
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overtime-month", action="store_true", help="本月加班")
    ap.add_argument("--overtime-year", action="store_true", help="當年度加班")
    ap.add_argument("--annual-leave", action="store_true", help="剩餘特休")
    ap.add_argument("--analysis", action="store_true", help="逐月明細 + 達標分析（含本月/當年度）")
    ap.add_argument("--target", type=float, default=None, help="每月加班目標時數（覆蓋設定檔；預設 20）")
    ap.add_argument("--approved-only", action="store_true", help="只算『同意』，不含『簽核中』")
    ap.add_argument("--basis", choices=["weekday+holiday", "total"], default=None,
                    help="達標基準（覆蓋設定檔；預設 weekday+holiday，不含補班）")
    ap.add_argument("--headed", action="store_true", help="有頭模式（驗證碼時手動過）")
    args = ap.parse_args()

    # 沒指定任何項目 → 全查
    if not (args.overtime_month or args.overtime_year or args.annual_leave or args.analysis):
        args.analysis = True
        args.annual_leave = True
    if args.analysis:
        args.overtime_month = args.overtime_year = True
    # 查任何加班一律附本月達標現況(month.status);故查當年度時也一併帶本月
    if args.overtime_year:
        args.overtime_month = True

    cfg = load_config()
    # 參數優先序：CLI > 設定檔 > 內建預設
    target = args.target if args.target is not None else float(cfg.get("monthly_target", 20))
    basis = args.basis or cfg.get("countable_basis", "weekday+holiday")
    if args.approved_only:
        status_str = "approved"
    else:
        status_str = cfg.get("status", "approved+pending")
    status_idx = [0] if status_str == "approved" else [0, 2]  # 同意 / 同意+簽核中
    today = datetime.date.today()
    acct, pw = resolve_credentials(cfg)

    result = {
        "as_of": today.isoformat(),
        "params": {
            "target_per_month": target,
            "countable_basis": basis,
            "status": status_str,
        },
    }

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=not args.headed)
        except Exception as e:
            die(5, "browser_launch_failed", detail=str(e))
        ctx = browser.new_context(locale="zh-TW", viewport={"width": 1500, "height": 1400})
        page = ctx.new_page()

        # 連線檢查
        try:
            login(page, acct, pw)
        except SystemExit:
            raise
        except Exception as e:
            msg = str(e)
            if "ERR_NAME_NOT_RESOLVED" in msg or "ERR_CONNECTION" in msg or "ERR_ADDRESS_UNREACHABLE" in msg or "Timeout" in msg:
                die(2, "unreachable", hint="連不到 http://uof，請確認已連上公司內網 / VPN", detail=msg)
            die(5, "login_error", detail=msg)

        ot = {}
        if args.overtime_month:
            e = month_range(today.year, today.month)[1]
            s = f"{today.year}/{today.month:02d}/01"
            m = shape_ot(overtime_range(page, s, e, status_idx), basis)
            # 查加班時數一律附本月達標現況：還差幾小時 / 本月剩幾個上班日 / 平均每天要加幾小時
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
            # 到今天應達成的目標:已完成整月 + 當月按已過工作日比例(月中不會誤判落後)
            prorated = _prorated_months_elapsed(today)
            target_to_date = round(target * prorated, 1)
            ot["analysis"] = {
                "target_per_month": target,
                "countable_basis": basis,
                "months_elapsed": months_elapsed,
                "ytd_countable": ytd,
                "target_to_date": target_to_date,   # 到今天(當月按工作日比例)應累計的目標
                "gap_ytd": round(ytd - target_to_date, 1),  # 負=落後、正=超前;月中已按比例校正
                "annual_target": annual_target,
                "still_needed_this_year": still_needed,
                "remaining_full_months": remaining_full,
                "need_per_remaining_month": round(still_needed / remaining_full, 1) if remaining_full > 0 else None,
                "workday_calc": workday_analysis(target, ytd, month_done, today),
            }

        if ot:
            result["overtime"] = ot
        if args.annual_leave:
            result["annual_leave"] = annual_leave(page)

        ctx.close()
        browser.close()

    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
