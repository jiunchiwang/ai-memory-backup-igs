#!/usr/bin/env python3
"""
填寫 UOF 表單（目前僅加班單）—— 唯讀 dry-run 專用：把欄位填好、截圖、輸出 JSON，
但程式碼裡完全沒有「點送出/儲存鈕」的路徑，絕不會真的送出申請。

用法：
  uof_form.py overtime --date 2026/07/20 --start 18:30 --hours 2 \
      --reason "版本上線支援" --output "修復加班單填寫功能"

離開碼：0 成功產出 dry-run；2 連不到內網；3 登入失敗/驗證碼；
       4 表單版型跟預期不符（欄位對不上，安全起見直接中止不填）；5 其他。
"""
import argparse, sys, os, json, datetime, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from uof_query import die, load_config, resolve_credentials, login, BASE

OVERTIME_FORM = "WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=cd8fb94e-a539-4c7e-9762-43e87e653ced"
DRY_RUN_DIR = os.path.expanduser("~/.config/uof/dry_run")

# 加班單欄位（2026-07-13 recon 確認，見 DESIGN.md「加班單欄位」章節）
UC = {
    "category_radio": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC3_rbList_0",  # 申請
    "start_date": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC6_RadDatePicker1_dateInput",
    "start_time": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC7_DropDownList1",
    "end_date": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC9_RadDatePicker1_dateInput",
    "end_time": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC10_DropDownList1",
    "reason": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC12_tbxMultiLineText",
    "output": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC13_tbxMultiLineText",
    "participate_yes": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC15_rbList_0",
    "participate_no": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC15_rbList_1",
    "project_owner": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC16_DropDownList1",
    "makeup_yes": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC17_rbList_0",
    "makeup_no": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC17_rbList_1",
}
LABELS = {
    "category_radio": "類別（申請）",
    "start_date": "開始日期",
    "start_time": "開始時間",
    "end_date": "結束日期",
    "end_time": "結束時間",
    "reason": "事由",
    "output": "工作產出",
    "participate": "是否參展",
    "project_owner": "專案負責人",
    "makeup": "是否調為補班",
}


def parse_hhmm(s):
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        die(5, "bad_arg", hint=f"時間格式需為 HH:MM，收到：{s}")
    return int(m.group(1)), int(m.group(2))


def add_minutes_snap15(hhmm, minutes):
    h, m = parse_hhmm(hhmm)
    total = h * 60 + m + minutes
    total = round(total / 15) * 15  # 對齊下拉 15 分鐘刻度
    total %= 24 * 60
    return f"{total // 60:02d}:{total % 60:02d}"


def find_form_frame(page):
    for fr in page.frames:
        try:
            if fr.query_selector("[id*='VersionFieldCollectionUsingUC1']"):
                return fr
        except Exception:
            continue
    return None


def verify_schema(frame):
    """填任何值之前先確認欄位仍在——版型變了就直接中止，不猜著填。"""
    missing = [k for k, cid in UC.items() if not frame.query_selector(f"#{cid}")]
    if missing:
        die(4, "form_layout_changed",
            hint=f"加班單欄位對不上預期（缺少：{missing}），可能表單版型變了，需重新 recon 確認欄位 id")


def fill_overtime(args):
    cfg = load_config()
    acct, pw = resolve_credentials(cfg)

    start_time = args.start
    end_time = args.end or add_minutes_snap15(args.start, round(args.hours * 60)) if args.hours else args.end
    if not end_time:
        die(5, "bad_arg", hint="需要 --end 或 --hours 其中之一")
    end_date = args.end_date or args.date

    fields_report = []
    warnings = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=not args.headed)
        except Exception as e:
            die(5, "browser_launch_failed", detail=str(e))
        ctx = browser.new_context(locale="zh-TW", viewport={"width": 1600, "height": 1600})
        page = ctx.new_page()

        try:
            login(page, acct, pw)
        except SystemExit:
            raise
        except Exception as e:
            msg = str(e)
            if "ERR_NAME_NOT_RESOLVED" in msg or "ERR_CONNECTION" in msg or "ERR_ADDRESS_UNREACHABLE" in msg or "Timeout" in msg:
                die(2, "unreachable", hint="連不到 http://uof，請確認已連上公司內網 / VPN", detail=msg)
            die(5, "login_error", detail=msg)

        page.goto(BASE + OVERTIME_FORM, wait_until="networkidle", timeout=40000)
        page.wait_for_timeout(5000)

        frame = find_form_frame(page)
        if not frame:
            die(4, "form_layout_changed", hint="找不到加班單表單 frame，可能選單路徑或版型變了")

        verify_schema(frame)

        # 類別固定「申請」（本工具目前只做新申請，不支援修改/刪除既有加班單）
        frame.check(f"#{UC['category_radio']}")
        fields_report.append({"label": LABELS["category_radio"], "value": "申請", "source": "fixed"})

        frame.fill(f"#{UC['start_date']}", args.date)
        fields_report.append({"label": LABELS["start_date"], "value": args.date, "source": "user"})

        try:
            frame.select_option(f"#{UC['start_time']}", label=start_time)
            fields_report.append({"label": LABELS["start_time"], "value": start_time, "source": "user"})
        except Exception:
            warnings.append(f"開始時間 {start_time} 不在下拉選項裡（15分鐘刻度），未選取")

        frame.fill(f"#{UC['end_date']}", end_date)
        fields_report.append({"label": LABELS["end_date"], "value": end_date, "source": "user" if args.end_date else "derived"})

        try:
            frame.select_option(f"#{UC['end_time']}", label=end_time)
            fields_report.append({"label": LABELS["end_time"], "value": end_time,
                                   "source": "user" if args.end else "derived_from_hours"})
        except Exception:
            warnings.append(f"結束時間 {end_time} 不在下拉選項裡（15分鐘刻度），未選取")

        frame.fill(f"#{UC['reason']}", args.reason)
        fields_report.append({"label": LABELS["reason"], "value": args.reason, "source": "user"})

        frame.fill(f"#{UC['output']}", args.output)
        fields_report.append({"label": LABELS["output"], "value": args.output, "source": "user"})

        participate = args.participate or "no"
        frame.check(f"#{UC['participate_yes' if participate == 'yes' else 'participate_no']}")
        fields_report.append({"label": LABELS["participate"], "value": "是" if participate == "yes" else "否",
                               "source": "user" if args.participate else "default"})

        if args.project_owner:
            try:
                frame.select_option(f"#{UC['project_owner']}", label=args.project_owner)
                fields_report.append({"label": LABELS["project_owner"], "value": args.project_owner, "source": "user"})
            except Exception:
                warnings.append(f"專案負責人「{args.project_owner}」不在下拉選項裡，未選取")

        makeup = args.makeup or "no"
        frame.check(f"#{UC['makeup_yes' if makeup == 'yes' else 'makeup_no']}")
        fields_report.append({"label": LABELS["makeup"], "value": "是" if makeup == "yes" else "否",
                               "source": "user" if args.makeup else "default"})

        page.wait_for_timeout(500)
        os.makedirs(DRY_RUN_DIR, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(DRY_RUN_DIR, f"overtime_{ts}.png")
        page.screenshot(path=screenshot_path, full_page=True)

        ctx.close()
        browser.close()

    result = {
        "mode": "dry_run",
        "form": "overtime",
        "note": "此工具只填欄位、截圖，不會點送出鈕；請自行到瀏覽器確認後手動送出",
        "fields": fields_report,
        "not_filled": {
            "班別": "系統於表單送出後判斷，本工具不填",
            "加班單單號": "僅類別=修改/刪除時需要，本工具只做新申請",
            "異動原因": "僅類別=修改/刪除時必填，本工具只做新申請",
        },
        "warnings": warnings,
        "screenshot": screenshot_path,
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ot = sub.add_parser("overtime", help="加班單 dry-run（只填欄位+截圖，不送出）")
    ot.add_argument("--date", required=True, help="開始日期 YYYY/MM/DD")
    ot.add_argument("--start", required=True, help="開始時間 HH:MM（需對齊15分鐘刻度）")
    ot.add_argument("--end", help="結束時間 HH:MM；不給則用 --hours 換算")
    ot.add_argument("--hours", type=float, help="加班時數；沒給 --end 時用來換算結束時間")
    ot.add_argument("--end-date", help="結束日期 YYYY/MM/DD；不給預設同 --date")
    ot.add_argument("--reason", required=True, help="事由")
    ot.add_argument("--output", required=True, help="工作產出")
    ot.add_argument("--participate", choices=["yes", "no"], help="是否參展，預設 no")
    ot.add_argument("--makeup", choices=["yes", "no"], help="是否調為補班，預設 no")
    ot.add_argument("--project-owner", help="專案負責人（下拉選項裡的姓名）")
    ot.add_argument("--headed", action="store_true", help="有頭模式（驗證碼時手動過）")

    args = ap.parse_args()
    if args.cmd == "overtime":
        fill_overtime(args)


if __name__ == "__main__":
    main()
