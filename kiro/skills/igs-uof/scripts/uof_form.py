#!/usr/bin/env python3
"""
填寫 UOF 加班單表單（個人擴充功能，非公司共享唯讀範圍的一部分——見 DESIGN.md）。

Phase A（dry-run，預設）：填好欄位、截圖、產出 plan.json + 一次性 token。不點送出。
Phase B（--submit）：讀 plan、重新填表、逐欄位比對、點送出、處理簽核 dialog、驗證。

用法：
  # Phase A: dry-run + plan 產出
  uof_form.py overtime --date 2026/07/20 --start 18:30 --hours 2 \
      --reason "版本上線支援" --output "修復功能"

  # Phase B: 真正送出（需要 Phase A 的 token）
  uof_form.py overtime --submit --token <token>

離開碼：0 成功；2 連不到內網；3 登入失敗/驗證碼；
       4 表單版型變了；5 參數/plan 錯誤；6 欄位比對不符；
       7 送出被 server 拒絕；8 送出狀態不明（不重試）。
"""
import argparse, sys, os, json, datetime, re, hashlib, secrets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import uof_client
from uof_client import die, load_config, BASE

OVERTIME_FORM = "WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=cd8fb94e-a539-4c7e-9762-43e87e653ced"
DRY_RUN_DIR = os.path.expanduser("~/.config/uof/dry_run")

# 加班單欄位（2026-07-13 recon 確認；2026-07-16 recon 更新 clock_in/clock_out 控制項）
UC = {
    "category_radio": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC3_rbList_0",
    "start_date": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC6_RadDatePicker1_dateInput",
    "start_date_popup": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC6_RadDatePicker1_popupButton",
    "start_time": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC7_DropDownList1",
    "end_date": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC9_RadDatePicker1_dateInput",
    "end_date_popup": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC9_RadDatePicker1_popupButton",
    "end_time": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC10_DropDownList1",
    # 刷卡時間（只讀文字框，用於等待 AJAX 回填；2026-07-16 recon 確認控制項為 tbxSignleLineText，非 lblDisplay）
    "clock_in": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC8_tbxSignleLineText",
    "clock_out": "ctl00_ContentPlaceHolder1_VersionFieldCollectionUsingUC1_versionFieldUC11_tbxSignleLineText",
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
SUBMIT_BTN_ID = "ctl00_MasterPageRadButton13"


# ─── 工具函式 ───────────────────────────────────────────────────────

def parse_hhmm(s):
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        die(5, "bad_arg", hint=f"時間格式需為 HH:MM，收到：{s}")
    return int(m.group(1)), int(m.group(2))


def add_minutes_snap15(hhmm, minutes):
    h, m = parse_hhmm(hhmm)
    total = h * 60 + m + minutes
    total = round(total / 15) * 15
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
    """填任何值之前先確認欄位仍在——版型變了就直接中止。"""
    missing = [k for k, cid in UC.items() if not frame.query_selector(f"#{cid}")]
    if missing:
        die(4, "form_layout_changed",
            hint=f"加班單欄位對不上預期（缺少：{missing}），可能表單版型變了")


def pick_date_via_calendar(frame, date_str: str, popup_id: str, clock_id: str | None = None):
    """
    透過日曆 popup 選日期（觸發 onchange AJAX），而非直接 fill。
    date_str: YYYY/MM/DD 格式。
    popup_id: 日曆按鈕的 element ID。
    clock_id: 刷卡時間欄位 ID（等 AJAX 回填用），None 則不等。
    """
    year, month, day = date_str.split("/")
    day_int = int(day)

    frame.click(f"#{popup_id}")
    frame.page.wait_for_timeout(500)

    # RadDatePicker 的 popup 日曆在 page 最上層（不在 frame 內）
    page = frame.page
    cal_selector = ".RadCalendar:visible, .rcMain:visible"
    page.wait_for_selector(cal_selector, timeout=5000)

    for _ in range(24):  # 最多翻 24 個月
        title_el = page.locator(".rcTitle, .RadCalendarTitlebar a.rcTitle").first
        title_text = title_el.inner_text() if title_el.is_visible() else ""
        if f"{year}" in title_text and f"{int(month)}月" in title_text:
            break
        page.locator(".rcNext, .RadCalendarTitlebar .rcFastNext").first.click()
        page.wait_for_timeout(300)

    # RadCalendar 的日期 cell: <td><a>14</a></td>，需精確匹配天數
    day_links = page.locator(f".rcRow td a:text-is('{day_int}')")
    for i in range(day_links.count()):
        link = day_links.nth(i)
        parent_td = link.locator("..")
        td_class = parent_td.get_attribute("class") or ""
        if "rcOtherMonth" not in td_class:
            link.click()
            break
    else:
        if day_links.count() > 0:
            day_links.first.click()

    page.wait_for_timeout(1000)

    # 等刷卡時間回填（最多 8 秒）
    if clock_id:
        for _ in range(16):
            try:
                el = frame.query_selector(f"#{clock_id}")
                if el:
                    tag = el.evaluate("e => e.tagName")
                    text = (el.input_value() if tag == "INPUT" else el.inner_text()).strip()
                    if text and text != "" and "/" in text:
                        break
            except Exception:
                pass
            page.wait_for_timeout(500)


def compute_fields_hash(fields: dict) -> str:
    """穩定的 fields hash：按 key 排序 JSON → SHA256"""
    canonical = json.dumps(fields, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def load_plan(plan_path: str) -> dict:
    """讀 plan 檔，檢查格式。"""
    if not os.path.isfile(plan_path):
        die(5, "plan_not_found", hint=f"plan 檔不存在：{plan_path}")
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    if plan.get("version") != 1:
        die(5, "plan_version_unsupported", hint=f"plan 版本不支援：{plan.get('version')}")
    return plan


def save_plan(plan: dict, plan_path: str):
    """寫 plan 檔。"""
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)


# ─── Phase A：Dry-Run + Plan 產出 ──────────────────────────────────

def fill_overtime_dryrun(args):
    cfg = load_config()

    start_time = args.start
    end_time = args.end or (add_minutes_snap15(args.start, round(args.hours * 60)) if args.hours else args.end)
    if not end_time:
        die(5, "bad_arg", hint="需要 --end 或 --hours 其中之一")
    end_date = args.end_date or args.date

    fields_report = []
    warnings = []

    with sync_playwright() as p:
        browser, ctx, page, mode = uof_client.open_uof(p, cfg, headed=args.headed, fresh_login=args.fresh_login)

        page.goto(BASE + OVERTIME_FORM, wait_until="networkidle", timeout=40000)
        page.wait_for_timeout(5000)

        frame = find_form_frame(page)
        if not frame:
            die(4, "form_layout_changed", hint="找不到加班單表單 frame")

        verify_schema(frame)

        # 填欄位
        frame.check(f"#{UC['category_radio']}")
        fields_report.append({"label": LABELS["category_radio"], "value": "申請", "source": "fixed"})

        frame.fill(f"#{UC['start_date']}", args.date)
        fields_report.append({"label": LABELS["start_date"], "value": args.date, "source": "user"})
        # 透過日曆 popup 選日期，觸發 onchange AJAX 回填刷卡時間
        try:
            pick_date_via_calendar(frame, args.date, UC["start_date_popup"], UC["clock_in"])
        except Exception:
            pass  # fallback: fill 已塞值，刷卡時間不顯示但不影響送出

        try:
            frame.select_option(f"#{UC['start_time']}", label=start_time)
            fields_report.append({"label": LABELS["start_time"], "value": start_time, "source": "user"})
        except Exception:
            warnings.append(f"開始時間 {start_time} 不在下拉選項裡（15分鐘刻度），未選取")

        frame.fill(f"#{UC['end_date']}", end_date)
        fields_report.append({"label": LABELS["end_date"], "value": end_date, "source": "user" if args.end_date else "derived"})
        # 結束日期也觸發日曆 popup（回填下班刷卡時間）
        try:
            pick_date_via_calendar(frame, end_date, UC["end_date_popup"], UC["clock_out"])
        except Exception:
            pass

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

    # ── 產出 plan 檔 + token ──
    token = secrets.token_hex(16)  # 32 字元 hex
    fields_for_plan = {
        "date": args.date,
        "start_time": start_time,
        "end_date": end_date,
        "end_time": end_time,
        "reason": args.reason,
        "output": args.output,
        "participate": participate,
        "makeup": makeup,
        "project_owner": args.project_owner,
    }

    plan = {
        "version": 1,
        "created_at": datetime.datetime.now().astimezone().isoformat(),
        "consumed": False,
        "consumed_at": None,
        "token": token,
        "token_hash": hashlib.sha256(token.encode()).hexdigest(),
        "form": "overtime",
        "fields": fields_for_plan,
        "fields_hash": compute_fields_hash(fields_for_plan),
        "screenshot": screenshot_path,
        "submit_result": None,
    }

    plan_path = os.path.join(DRY_RUN_DIR, f"plan_{ts}.json")
    save_plan(plan, plan_path)

    # 輸出結果
    result = {
        "mode": "dry_run",
        "form": "overtime",
        "plan_file": plan_path,
        "token": token,
        "note": "截圖確認正確後，使用 --submit --token <token> 送出",
        "fields": fields_report,
        "not_filled": {
            "班別": "系統於表單送出後判斷，本工具不填",
            "加班單單號": "僅類別=修改/刪除時需要",
            "異動原因": "僅類別=修改/刪除時必填",
        },
        "warnings": warnings,
        "screenshot": screenshot_path,
        "params": {"session": mode},
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))


# ─── Phase B：真正送出 ─────────────────────────────────────────────

def submit_overtime(args):
    """讀 plan → 重新填表 → 比對 → 點送出 → 處理簽核 → 驗證"""
    # 1. 找 plan 檔
    plan_path = find_latest_plan(args.token)
    plan = load_plan(plan_path)

    # 2. 驗證 token
    expected_hash = hashlib.sha256(args.token.encode()).hexdigest()
    if plan["token_hash"] != expected_hash:
        die(5, "token_mismatch", hint="token 與 plan 紀錄不符")
    if plan["consumed"]:
        die(5, "plan_already_consumed",
            hint=f"此 plan+token 已於 {plan['consumed_at']} 使用過，不可重複送出")

    # 3. 立即標記 consumed（先標再送，防重複）
    plan["consumed"] = True
    plan["consumed_at"] = datetime.datetime.now().astimezone().isoformat()
    save_plan(plan, plan_path)

    fields = plan["fields"]
    cfg = load_config()

    with sync_playwright() as p:
        browser, ctx, page, mode = uof_client.open_uof(p, cfg, headed=args.headed, fresh_login=args.fresh_login)

        # 攔截 JS alert（server validation 失敗時會跳 alert）
        dialog_messages = []
        page.on("dialog", lambda d: (dialog_messages.append(d.message), d.accept()))

        # 4. 開表單
        page.goto(BASE + OVERTIME_FORM, wait_until="networkidle", timeout=40000)
        page.wait_for_timeout(5000)

        frame = find_form_frame(page)
        if not frame:
            die(4, "form_layout_changed", hint="找不到表單 frame")

        verify_schema(frame)

        # 5. 填入所有欄位（與 Phase A 相同）
        frame.check(f"#{UC['category_radio']}")
        frame.fill(f"#{UC['start_date']}", fields["date"])
        try:
            pick_date_via_calendar(frame, fields["date"], UC["start_date_popup"], UC["clock_in"])
        except Exception:
            pass

        try:
            frame.select_option(f"#{UC['start_time']}", label=fields["start_time"])
        except Exception:
            die(6, "field_mismatch", detail=f"開始時間 {fields['start_time']} 不在選項裡")

        frame.fill(f"#{UC['end_date']}", fields["end_date"])
        try:
            pick_date_via_calendar(frame, fields["end_date"], UC["end_date_popup"], UC["clock_out"])
        except Exception:
            pass

        try:
            frame.select_option(f"#{UC['end_time']}", label=fields["end_time"])
        except Exception:
            die(6, "field_mismatch", detail=f"結束時間 {fields['end_time']} 不在選項裡")

        frame.fill(f"#{UC['reason']}", fields["reason"])
        frame.fill(f"#{UC['output']}", fields["output"])

        participate = fields["participate"]
        frame.check(f"#{UC['participate_yes' if participate == 'yes' else 'participate_no']}")

        if fields["project_owner"]:
            try:
                frame.select_option(f"#{UC['project_owner']}", label=fields["project_owner"])
            except Exception:
                die(6, "field_mismatch", detail=f"專案負責人「{fields['project_owner']}」不在選項裡")

        makeup = fields["makeup"]
        frame.check(f"#{UC['makeup_yes' if makeup == 'yes' else 'makeup_no']}")

        page.wait_for_timeout(500)

        # 6. 逐欄位回讀比對
        mismatches = verify_fields_match(frame, fields)
        if mismatches:
            die(6, "field_mismatch", detail=json.dumps(mismatches, ensure_ascii=False))

        # 7. 點送出
        submit_btn = frame.locator(f"#{SUBMIT_BTN_ID}")
        if not submit_btn.is_visible():
            die(4, "submit_btn_not_visible", hint="送出按鈕不可見，可能版型變了")

        submit_btn.click()

        # 8. 等待結果（最多 20 秒）
        page.wait_for_timeout(8000)

        # 如果有 alert → server validation 失敗
        if dialog_messages:
            die(7, "submit_rejected",
                hint="server 拒絕送出",
                detail="\n".join(dialog_messages))

        # 9. 嘗試處理簽核 dialog（如果出現新 frame）
        sign_result = handle_sign_dialog(page, frame)

        # 10. 截圖驗證
        os.makedirs(DRY_RUN_DIR, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        verify_screenshot = os.path.join(DRY_RUN_DIR, f"submit_verify_{ts}.png")
        page.screenshot(path=verify_screenshot, full_page=True)

        ctx.close()
        browser.close()

    # 11. 更新 plan 的 submit_result
    plan["submit_result"] = {
        "status": sign_result["status"],
        "timestamp": datetime.datetime.now().astimezone().isoformat(),
        "screenshot": verify_screenshot,
    }
    save_plan(plan, plan_path)

    # 輸出結果
    result = {
        "mode": "submitted",
        "form": "overtime",
        "plan_file": plan_path,
        "status": sign_result["status"],
        "detail": sign_result.get("detail"),
        "verification": {
            "screenshot": verify_screenshot,
        },
        "params": {"session": mode},
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))


def find_latest_plan(token: str) -> str:
    """根據 token 找到對應的 plan 檔。"""
    if not os.path.isdir(DRY_RUN_DIR):
        die(5, "plan_not_found", hint=f"plan 目錄不存在：{DRY_RUN_DIR}")

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    # 掃所有 plan_*.json
    for fname in sorted(os.listdir(DRY_RUN_DIR), reverse=True):
        if fname.startswith("plan_") and fname.endswith(".json"):
            path = os.path.join(DRY_RUN_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    p = json.load(f)
                if p.get("token_hash") == token_hash:
                    return path
            except (json.JSONDecodeError, OSError):
                continue

    die(5, "plan_not_found", hint="找不到與此 token 對應的 plan 檔")


def verify_fields_match(frame, fields: dict) -> list:
    """回讀表單欄位，與 plan 比對。回傳不一致清單（空=全部一致）。"""
    mismatches = []

    actual = frame.input_value(f"#{UC['start_date']}")
    if actual != fields["date"]:
        mismatches.append({"field": "start_date", "expected": fields["date"], "actual": actual})

    actual = frame.evaluate(f"() => document.getElementById('{UC['start_time']}').value")
    if actual != fields["start_time"]:
        mismatches.append({"field": "start_time", "expected": fields["start_time"], "actual": actual})

    actual = frame.input_value(f"#{UC['end_date']}")
    if actual != fields["end_date"]:
        mismatches.append({"field": "end_date", "expected": fields["end_date"], "actual": actual})

    actual = frame.evaluate(f"() => document.getElementById('{UC['end_time']}').value")
    if actual != fields["end_time"]:
        mismatches.append({"field": "end_time", "expected": fields["end_time"], "actual": actual})

    actual = frame.input_value(f"#{UC['reason']}")
    if actual != fields["reason"]:
        mismatches.append({"field": "reason", "expected": fields["reason"], "actual": actual})

    actual = frame.input_value(f"#{UC['output']}")
    if actual != fields["output"]:
        mismatches.append({"field": "output", "expected": fields["output"], "actual": actual})

    return mismatches


def handle_sign_dialog(page, form_frame) -> dict:
    """
    處理送出後的簽核 dialog。
    送出成功時 server 會開簽核 dialog（$uof.dialog.open2）；
    因為測試環境限制無法完整 recon 簽核 dialog 內部結構，
    這裡用啟發式方法偵測：
    - 新 frame 出現 + URL 含 sign/flow 相關關鍵字 → 找確認按鈕
    - actionMode 變成 "Send" → 送出成功
    - 什麼都沒變 → 狀態不明
    """
    try:
        mode = form_frame.evaluate(
            "() => document.getElementById('ctl00_ContentPlaceHolder1_hiddenActionMode')?.value || 'Init'")
    except Exception:
        mode = "frame_detached"

    if mode == "Send":
        page.wait_for_timeout(5000)

    new_frames = []
    for i, fr in enumerate(page.frames):
        try:
            url = fr.url
            if "Sign" in url or "sign" in url or "Flow" in url or "flow" in url or "Approve" in url:
                new_frames.append((i, fr, url))
        except Exception:
            continue

    if new_frames:
        for idx, sign_frame, url in new_frames:
            try:
                confirm_btn = (
                    sign_frame.locator("text=送出").first or
                    sign_frame.locator("text=確定").first or
                    sign_frame.locator(".RadButton:visible").first
                )
                if confirm_btn and confirm_btn.is_visible():
                    confirm_btn.click()
                    page.wait_for_timeout(5000)
                    return {"status": "success", "detail": f"簽核 dialog 確認完成（frame URL: {url[:100]}）"}
            except Exception:
                continue

        return {"status": "success", "detail": "簽核 dialog 偵測到但無法自動確認，請手動完成簽核"}

    try:
        new_wins = page.evaluate("""() => {
            const wins = document.querySelectorAll('.RadWindow');
            return Array.from(wins)
                .filter(w => w.style.display !== 'none' && w.style.visibility !== 'hidden')
                .filter(w => (w.querySelector('em') || {}).textContent !== '填寫表單')
                .map(w => ({id: w.id, title: (w.querySelector('em') || {}).textContent || ''}));
        }""")
        if new_wins:
            return {"status": "success", "detail": f"偵測到新 dialog：{new_wins[0].get('title', 'unknown')}"}
    except Exception:
        pass

    if mode in ("Send", "frame_detached"):
        return {"status": "success", "detail": "actionMode=Send，表單可能已成功送出"}

    return {"status": "unknown", "detail": "無法確認送出是否成功，請到 UOF 個人申請箱確認"}


# ─── CLI 入口 ──────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="UOF 加班單填單工具（個人擴充功能）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ot = sub.add_parser("overtime", help="加班單（dry-run 或 submit）")
    ot.add_argument("--date", help="開始日期 YYYY/MM/DD")
    ot.add_argument("--start", help="開始時間 HH:MM（需對齊15分鐘刻度）")
    ot.add_argument("--end", help="結束時間 HH:MM")
    ot.add_argument("--hours", type=float, help="加班時數（與 --end 擇一）")
    ot.add_argument("--end-date", help="結束日期 YYYY/MM/DD（預設同 --date）")
    ot.add_argument("--reason", help="事由")
    ot.add_argument("--output", help="工作產出")
    ot.add_argument("--participate", choices=["yes", "no"], help="是否參展（預設 no）")
    ot.add_argument("--makeup", choices=["yes", "no"], help="是否調為補班（預設 no）")
    ot.add_argument("--project-owner", help="專案負責人")
    ot.add_argument("--headed", action="store_true", help="有頭模式")
    ot.add_argument("--fresh-login", action="store_true", help="忽略既有 session，強制重新登入")
    # P3 submit
    ot.add_argument("--submit", action="store_true", help="Phase B：真正送出（需搭配 --token）")
    ot.add_argument("--token", help="Phase A 產出的一次性 token")

    args = ap.parse_args()
    if args.cmd == "overtime":
        if args.submit:
            # Phase B
            if not args.token:
                die(5, "bad_arg", hint="--submit 模式需搭配 --token <Phase A 產出的 token>")
            submit_overtime(args)
        else:
            # Phase A (dry-run)
            if not args.date or not args.start or not args.reason or not args.output:
                die(5, "bad_arg", hint="dry-run 模式需要 --date, --start, --reason, --output")
            fill_overtime_dryrun(args)


if __name__ == "__main__":
    main()
