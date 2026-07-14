# vc-uof-hours — 設計文件

> 2026-07-13 brainstorming 定案。查詢公司內網 UOF（U-Office Force）的加班時數與剩餘特休，並做加班達標分析。

## 目的

透過 AI 直接問「我這個月加了幾小時班 / 特休還剩多少 / 我加班進度夠不夠」，skill 自動登入 UOF、抓數字、算缺口，用中文回答。

## 範圍（YAGNI）

**做**：
1. 本月累計加班時數（平日 / 假日 / 補班 / 合計）
2. 當年度累計加班時數（跨部門列加總）
3. 剩餘特休（未休 / 應休 / 已休 + 給假期間）
4. 加班達標分析：逐月明細、對月目標的缺口、剩餘月份需補時數
5. 每個上班日還要加幾小時（用 IGS 行事曆算實際工作天）：**兩個判斷**——(A) 追全年平均、(B) 追本月

**不做**（用戶已排除）：補休餘額（用戶無此額度）、事假等其他假別餘額（表單不顯示）、請假 / 打卡 / 出缺勤查詢。

**填單（2026-07-13 新增，僅 dry-run）**：
6. 預填加班單（新申請）欄位並截圖，讓用戶自行到瀏覽器確認後手動送出。**不含**：自動送出、修改/刪除既有加班單、請假單填寫（第二階段才做）、假日加班事先申請單（視需求再做）。詳見「加班單欄位」與「填單安全設計」章節。

## 系統事實（recon 2026-07-13 實測）

- 站台：`http://uof/UOF/`，U-Office Force（一等一科技 e-Excellence），ASP.NET WebForms + Telerik，版本 28.0.9137D。
- 登入頁：`Login.aspx`，欄位 `#txtAccount` / `#txtPwd` / `#btnSubmit`。正常登入**不需驗證碼**（僅多次失敗才動態出現 `#captchaImage`）。
- 重複登入：若已有 active session，會出現 `#btnRemoveRepeatLogin`（確定），點了會踢掉另一個 session 才能登入。
- 登入成功導向 `Homepage.aspx`。

### 加班資料來源
- 頁面：`Project/BAE/Stats_Search.aspx`（加班統計查詢；選單「加班統計查詢」透過 `LinkUrl.aspx?menuID=50e0c745…` 的 iframe 開啟，但可直接 goto 此頁）。
- 表單控制項：
  - `#SDate` / `#EDate`：日期文字框，格式 `YYYY/MM/DD`，帶 jQuery UI datepicker。**必須用 JS 設值**（`el.value=…; dispatchEvent('change')`）避免彈出的日曆蓋住送出鈕。
  - 簽核狀態 checkbox：`#StsChkBoxList_0`=同意、`_1`=否決、`_2`=簽核中、`_3`=作廢。
  - 送出：`#BtnSubmit`（onclick `__doPostBack('BtnSubmit','')`）；送出前先 `Escape` + 隱藏 `#ui-datepicker-div`。
- 結果：頁面 footer 文字「平日加班時數合計：X 小時 ／ 假日加班時數合計：Y 小時 ／ 補班時數合計：Z」。
  - 正則：`平日加班時數合計：\s*([\d.]*)\s*小時.*?假日加班時數合計：\s*([\d.]*)\s*小時.*?補班時數合計：\s*([\d.]*)`（空字串當 0）。
  - **注意**：換過部門的區間查詢會回**多列**（每個部門一列），footer 已是全部加總，直接用 footer 即可，不必自己疊列。

### 特休資料來源
- 頁面：請假單表單 `WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=14ac1707-9566-4f02-b895-3da0e7395310`
- 資料在 iframe（`dialog2FrameContent` → `FirstSite.aspx`）內，**開頁即顯示**（不需選假別）：
  - 文字格式：`<起>~<迄>特休未休<未休>小時 = 應休<應休>小時-已休<已休>小時`
  - 正則：`(\d{4}/\d\d/\d\d)~(\d{4}/\d\d/\d\d)特休未休([\d.]+)小時\s*=\s*應休([\d.]+)小時-已休([\d.]+)小時`
  - 掃所有 frame 找含「特休未休」者。表單渲染慢，等 5s。

### 加班單欄位（recon 2026-07-13，見截圖標籤，非猜測）

頁面：`WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=cd8fb94e-a539-4c7e-9762-43e87e653ced`（Homepage 選單「加班單」）。欄位控制項命名模式 `..._VersionFieldCollectionUsingUC1_versionFieldUC<N>_<控制項>`：

| UC | 中文標籤 | 控制項 | 必填 | 本工具處理 |
|---|---|---|---|---|
| 0 | 申請者 | 唯讀文字 | - | 不填（系統帶入）|
| 1 | 表單編號 | 唯讀文字 | - | 不填（系統自動產生）|
| 2 | （工時規則提示文字）| 唯讀 RadEditor | - | 不是欄位，略過 |
| 3 | 類別 | radio 申請/修改/刪除 | ✅ | 固定填「申請」（本工具不支援修改/刪除）|
| 4 | 加班單單號 | select | - | 不填（僅修改/刪除模式需要，見頁面註「類別選擇修改/刪除才可選擇」）|
| 5 | 班別（上班日/休息日/例假日/國定假日/非法定休息日） | radio | - | **不填**——頁面註「表單送出後判斷」，是系統算的，不是使用者填的 |
| 6 | 開始日期 | RadDatePicker | ✅ | `--date` |
| 7 | 開始時間 | select（15分鐘刻度，需晚於上班刷卡時間） | ✅ | `--start` |
| 8 | 上班刷卡時間 | 唯讀文字 | - | 不填（系統顯示）|
| 9 | 結束日期 | RadDatePicker | ✅ | `--end-date`（預設同開始日期）|
| 10 | 結束時間 | select（需早於下班刷卡時間） | ✅ | `--end` 或用 `--hours` 換算（對齊15分鐘刻度）|
| 11 | 下班刷卡時間 | 唯讀文字 | - | 不填（系統顯示）|
| 12 | 事由 | textarea | ✅ | `--reason` |
| 13 | 工作產出 | textarea | ✅ | `--output` |
| 14 | 異動原因 | textarea | - | 不填（頁面註「類別選擇修改/刪除必須輸入」）|
| 15 | 是否參展 | radio 是/否 | ✅ | `--participate`，預設「否」|
| 16 | 專案負責人 | select（同事姓名+「專案」） | - | `--project-owner`（選填，不給就留「─請選擇─」）|
| 17 | 是否調為補班 | radio 是/否 | - | `--makeup`，預設「否」（頁面註「每月加班前四小時預設為補班」）|

頁面下半部「申請資訊/意見/相關附件/個人附件」屬 WKF 共用流程欄位（緊急程度、簽核意見、檔案），非本表單專屬，本工具不碰。

## 填單安全設計（uof_form.py）

- **只做 dry-run**：`fill_overtime()` 填完欄位後只做 `page.screenshot()`，**程式碼裡沒有任何送出/儲存按鈕的 selector 或點擊呼叫**——不是「預設關閉」而是物理上不存在該路徑，避免 prompt injection 或誤判導致意外送出。
- **版型守衛 `verify_schema()`**：填任何欄位前，先確認 UC 對照表裡的每個 id 都存在於頁面上；缺一個就直接 `die(4, "form_layout_changed")` 中止，不會用錯的 id 填錯欄位。
- **截圖是唯一驗收依據**：JSON 輸出的 `fields` 陣列只是文字對照，真正判斷「有沒有填對」要看 `screenshot` 路徑的圖——SKILL.md 已寫死「一定要把截圖給用戶看」。
- **時間對不上選項時不硬填**：`select_option` 失敗會落到 `warnings`，不會用最接近的值頂替（避免看起來像成功但值是錯的）。
- 截圖存在 `~/.config/uof/dry_run/`（跟設定檔同層級，在 repo 目錄之外，不會被 git 追蹤到）。

## 判定參數（優先序：CLI 參數 > 設定檔 > 內建預設）

| 參數 | 內建預設 | 設定檔鍵 / CLI | 說明 |
|---|---|---|---|
| 達標基準 | **平日+假日**（不含補班） | `countable_basis` / `--basis` | 補班仍抓出並顯示，但不計入達標判定 |
| 簽核狀態 | **同意 + 簽核中**（`StsChkBoxList_0`,`_2`） | `status` / `--approved-only` | 已排定的都算 |
| 月目標 | **20 小時** | `monthly_target` / `--target` | 每人可自訂（有人 20、有人 30）|

實際採用值會回在 JSON `params`。

## 架構

```
~/.claude/skills/vc-uof-hours/
├── SKILL.md              # 觸發詞 + 流程：呼叫腳本、解讀 JSON、中文回答
├── DESIGN.md             # 本文件
├── SETUP.md              # 給同事的跨平台安裝說明（Mac/Windows）
├── requirements.txt      # playwright, xlrd
├── config.example.json   # 設定檔範例（帳密 + 偏好）
├── scripts/
│   ├── uof_query.py         # Playwright 登入 + 抓數字 + 達標分析，輸出 JSON
│   ├── uof_form.py          # 加班單 dry-run 填單+截圖（import uof_query 的登入邏輯，不重寫）
│   └── calendar_workdays.py # 工作日提供者（內建年份 / 行事曆 .xls / 估算）
└── .venv/                   # 專屬 venv（playwright + xlrd；.gitignore 不入庫）
```

跨平台：python 路徑 Mac `.venv/bin/python`、Windows `.venv\Scripts\python.exe`。設定檔 `~/.config/uof/config.json`（`os.path.expanduser` 兩系統皆通）。

### uof_query.py 行為
- 帳密與偏好：`resolve_credentials()` 優先序 環境變數 `UOF_ACCOUNT`/`UOF_PASSWORD` > 設定檔 `~/.config/uof/config.json` > （僅 macOS）Keychain `uof-hr`。取不到 → `error=no_credential` + 跨平台設定教學。
- 啟 headless Chromium → 登入（處理重複登入 dialog；偵測驗證碼則報錯提示改用 `--headed`）。
- 依 CLI 參數決定要查什麼：
  - `--overtime-month`（本月）
  - `--overtime-year`（當年度）
  - `--annual-leave`（特休）
  - `--analysis`（逐月 1..當月 + 缺口計算，預設全開）
- 輸出**單一 JSON** 到 stdout（`ensure_ascii=False`）。結構如下（數值僅為格式示意）：
  ```json
  {
    "as_of": "YYYY-MM-DD",
    "params": {"target_per_month":20, "countable_basis":"weekday+holiday", "status":"approved+pending"},
    "overtime": {
      "month": {"weekday":0.0,"holiday":0.0,"makeup":0.0,"countable":0.0,"total":0.0,"records":0,
                "status": {"target":20,"done":0.0,"still_needed":0.0,"remaining_workdays":0,
                           "per_workday":0.0,"counted_from":"YYYY-MM-DD","workday_source":"baked:2026"}},
      "year":  {"weekday":0.0,"holiday":0.0,"makeup":0.0,"countable":0.0,"total":0.0,"records":0},
      "by_month": {"1":{...},"2":{...}},
      "analysis": {
        "target_per_month":20,"countable_basis":"weekday+holiday","months_elapsed":0,
        "ytd_countable":0.0,"target_to_date":0.0,"gap_ytd":0.0,
        "annual_target":240,"still_needed_this_year":0.0,
        "remaining_full_months":0,"need_per_remaining_month":0.0,
        "workday_calc": {"workday_source":"baked:2026","counted_from":"YYYY-MM-DD",
                         "remaining_workdays_year":0,"remaining_workdays_month":0,
                         "per_workday_year":0.0,"per_workday_month":0.0}
      }
    },
    "annual_leave": {"period":"<起>~<迄>","remaining_h":0.0,"entitled_h":0.0,"used_h":0.0,"remaining_days":0.0}
  }
  ```
  - `countable` = 依達標基準（預設 平日+假日）。`total` = 平日+假日+補班。
  - **查加班時數一律附 `month.status`**（本月還差幾小時 / 剩幾個上班日 / 每上班日要加幾小時）——回應用戶要求。
  - `workday_source`：`baked:<year>` / `calendar:<檔名>` / `estimate`（估算會附 `workday_note`）。
  - 特休天數 = 未休小時 / 8。
- 錯誤處理（JSON `{"error":...,"hint":...}` + 非 0 exit）：`unreachable`(2) / `login_failed`,`captcha`,`no_credential`(3) / `scrape_failed`(4) / `bad_config`,其他(5)。

### SKILL.md 流程
1. 觸發詞：加班時數、加班幾小時、特休剩多少、加班進度 / 達標 / 缺口、UOF 出勤等。
2. 跑 `.venv/bin/python scripts/uof_query.py <flags>`（依用戶問的內容選 flag；問「全部」就全開）。
3. 解析 JSON，用繁體中文口語回答；達標分析用小表格呈現逐月 + 缺口 + 剩餘月份需補時數。
4. 若 `error` → 照 hint 告知用戶（多半是沒連內網）。

## 每個上班日換算（工作日提供者，scripts/calendar_workdays.py）

`count_workdays(year, start, end)` 回 `(天數, source, note)`，來源三層：
1. **內建年份 `BAKED`**（目前 2026）：只記例外——`weekday_off`（平日卻放假，21 天）+ `weekend_work`（週末卻補班，0），其餘照週一~五。跨平台、免檔案、最可靠。新的一年可從行事曆解析後把例外清單貼進 BAKED。
2. **行事曆 .xls**：Downloads 內檔名含民國年（西元−1911）+「行事曆/IGS」（如 `IGS 116行事曆.xls`）。供未內建年份。
3. **估算**：僅計平日，若區間含七月則扣 5 天旅遊假（IGS 慣例），附 `note` 標註為估計。

行事曆顏色分類（`pattern_colour_index` → colour_map RGB）：
  - 白 / 無填色 / `(255,255,255)` = **上班日 work**
  - 粉紅 `(255,153,204)` = **放假日 off**（週末+國定假）
  - 淺黃 `(255,255,204)` = **旅遊假 travel**（公司旅遊假，不上班）
  - 其他色保守當 off（不會誤要求上班日加班）
- 版面偵測：掃「星期表頭列（日一二三四五六）」定欄群組，不寫死列號；月份從表頭上方兩列抓「N月」。
- **正確性保證**：解析後用『欄位位置推得星期（0=日）vs `date.isoweekday()%7`』全量驗證，任一天對不上就丟 ValueError → 退回估算（來源3）。天數 <300 也視為版型異常。
- 兩個判斷（`analysis.workday_calc`，從隔天 `counted_from` 起算）：
  - `per_workday_year` = (target×12 − ytd_countable) ÷ 今年剩餘上班日 → **追全年平均**
  - `per_workday_month` = (target − 本月 countable) ÷ 本月剩餘上班日 → **追本月**

## 達標分析公式

- `countable(month)` = weekday + holiday（預設基準）
- `ytd_countable` = Σ countable(1..當月)
- `target_to_date` = target_per_month × (已完成整月數 + 當月已過工作日比例)。**當月按已過工作日比例折算**,不是整月——否則月中查詢會把 on-pace 誤判成落後。
- `gap_ytd` = ytd_countable − target_to_date（負=落後、正=超前）
- 剩餘月份 = 12 − 當月
- `need_per_remaining_month` = (target_per_month×12 − ytd_countable) / 剩餘月份

## 安全與副作用
- 帳密來源：設定檔 `~/.config/uof/config.json`（跨平台，明文——`config.example.json` 提供範例，本體不入庫、建議 `chmod 600`）；macOS 可改用 Keychain `uof-hr`（設定檔只留偏好）。環境變數可覆蓋。
- 設定檔與 `.venv` 皆在 `.gitignore`；分享 skill 時只傳程式碼，不傳個人設定檔。
- ⚠️ 自動登入會觸發 UOF 重複登入偵測 → 可能踢掉你當下瀏覽器的登入（反之亦然）。屬系統限制，非 bug。

## 分享給同事（Mac/Windows）
- 安裝流程見 `SETUP.md`：放 skill → 建 venv + `pip install -r requirements.txt` + `playwright install chromium` → 建 `~/.config/uof/config.json`。
- 2026 工作日已內建，同事免下載行事曆即可用「每上班日要加幾小時」；明年換行事曆放進 Downloads 或把例外貼進 BAKED。

## 對抗驗證審查加固（2026-07-13，多 agent 多角度 + adversarial verify）

一輪「5 視角分析 → 每個發現派 skeptic 推翻」後,確認並修掉 5 個問題:
1. **簽核狀態 checkbox**（high）:改成明確設定 4 個 checkbox 的目標狀態（要的 check、不要的 uncheck），並要求預期 id 都存在，缺則 `scrape_failed`——避免「只勾不取消」讓否決/作廢或簽核中混入、或 id 改名靜默失效造成加班數字被汙染卻不報錯。
2. **月中達標**（med）:`target_to_date` 改按當月已過工作日比例折算，月中 on-pace 不再被誤報落後。
3. **0 筆月份**（med）:某月 0 筆時 UOF 不渲染合計 footer（實測「總筆數：0」整段消失）→ 偵測到 0 筆回傳 0 而非 `die`，避免年中到職者逐月查詢整份中斷。
4. **stdout UTF-8**（med）:module 頂 `sys.stdout.reconfigure('utf-8')`，修 Windows cp950 下中文輸出亂碼/crash。
5. **一律附 month.status**（med）:`--overtime-year` 也強制帶本月，落實「查加班一律附本月達標現況」。

被 adversarial 判定**誤報而未改**（記錄以免重複糾結）:日期塞值無反查（實測現行站台純文字框 .value 即送出值,改版多會以 scrape_failed 浮現）、`need_per_remaining_month` 分子分母不對稱（刻意投影,且對用戶呈現的是 `per_workday_year`）、SKILL.md `%USERPROFILE%`（文件佔位符,與 `~` 對稱,agent 不會逐字貼）、錯誤表未列 `browser_launch_failed`（`detail` 已帶 Playwright 官方安裝指示）。

此輪 review 只涵蓋 `uof_query.py`（唯讀查詢），未涉及 `uof_form.py`（加班單 dry-run 填單，同日稍晚才加入）。

## P3 設計規格：真正送出（2026-07-14）

> **前置確認結果**（2026-07-14 使用者實測）：
> 1. UOF 加班單**沒有撤回/抽單機制**——送出即定案，無法反悔
> 2. 「專案負責人」（UC16）非必填——留「─請選擇─」可正常送出
> 3. 「是否調為補班」（UC17）系統不會覆蓋——填什麼就是什麼
>
> **設計等級：最高安全**（因為不可撤回）

### 核心原則

1. **不可能意外送出**：submit 路徑需要 dry-run 產生的 plan 檔 + 一次性 token + 使用者明確確認，三者缺一不可
2. **二次比對**：submit 不是接著 dry-run 的 browser session 直接按鈕——而是重新開表單、重新填入、逐欄位比對值與 plan 一致，才點送出
3. **失敗 = 停止**：任何異常（欄位比對不符、頁面超時、selector 消失、網路中斷）→ 絕不送出、絕不重試，回報使用者自行處理
4. **單次消耗**：token 用過即失效，plan 檔標記 consumed；想再送必須重跑 dry-run 取得新 token

### 兩階段流程

```
┌─────────────────── Phase A: Dry-Run（已實作，P2） ───────────────────┐
│  uof_form.py overtime --date ... --reason ... (不帶 --submit)        │
│  → 登入 → 填欄位 → 截圖 → 產出 plan.json + token → 結束             │
└──────────────────────────────────────────────────────────────────────┘
                            ↓ 使用者確認截圖正確
┌─────────────────── Phase B: Submit（P3 新增） ───────────────────────┐
│  uof_form.py overtime --submit --token <token>                       │
│  → 讀 plan.json → 驗證 token 有效 + 未消耗                           │
│  → 登入 → 重新開表單 → 重新填入所有欄位                               │
│  → 逐欄位比對（填入值 vs plan 記錄值）→ 全部一致才繼續                 │
│  → 點送出鈕 → 等待頁面回應                                           │
│  → 到 PersonalBox 驗證新表單出現                                      │
│  → 標記 plan.json consumed → 輸出結果 JSON                           │
└──────────────────────────────────────────────────────────────────────┘
```

### CLI 介面（P3 新增參數）

```bash
# Phase A（現有，P3 加入 plan 產出）
uof_form.py overtime --date 2026/07/20 --start 18:30 --hours 2 \
  --reason "版本上線支援" --output "修復加班單填寫功能"
# → 輸出 JSON 多出 plan_file + token 欄位

# Phase B（P3 新增）
uof_form.py overtime --submit --token <token>
# → 讀取 plan_file，重新填表 + 比對 + 送出 + 驗證
```

`--submit` 模式下所有欄位參數**不再接受**（從 plan 讀取，防止 Phase A/B 參數不一致）。唯一需要的是 `--token`（以及選用的 `--headed`）。

### Plan 檔格式（`~/.config/uof/dry_run/plan_<ts>.json`）

```json
{
  "version": 1,
  "created_at": "2026-07-20T18:30:00+08:00",
  "consumed": false,
  "consumed_at": null,
  "token": "<隨機 32 字元 hex>",
  "token_hash": "<SHA256(token)>",
  "form": "overtime",
  "fields": {
    "date": "2026/07/20",
    "start_time": "18:30",
    "end_date": "2026/07/20",
    "end_time": "20:30",
    "reason": "版本上線支援",
    "output": "修復加班單填寫功能",
    "participate": "no",
    "makeup": "no",
    "project_owner": null
  },
  "fields_hash": "<SHA256(canonical JSON of fields)>",
  "screenshot": "~/.config/uof/dry_run/overtime_20260720_183000.png",
  "submit_result": null
}
```

設計決策：
- `token` 存明文在 plan 檔（本機單人使用，無需加密；plan 檔跟帳密同目錄同權限）
- `fields_hash` 用來快速比對 Phase B 填入後的值是否與 Phase A 紀錄一致
- `consumed` 一旦標 `true` 就不能再用，即使 submit 失敗也標記（防重複送出）

### Phase A 改動（向後相容）

現有 dry-run 輸出加入兩個欄位：

```json
{
  "mode": "dry_run",
  "plan_file": "~/.config/uof/dry_run/plan_20260720_183000.json",
  "token": "a1b2c3d4...",
  "fields": [...],
  "screenshot": "...",
  "warnings": [...]
}
```

- `plan_file`：plan 的絕對路徑
- `token`：一次性 token（Phase B 要用）
- 若呼叫方未使用 `--submit`，行為完全不變（仍是 dry-run only）

### Phase B 流程細節

```
1. 讀 plan_file
   ├─ 檔案不存在 → die(5, "plan_not_found")
   ├─ consumed=true → die(5, "plan_already_consumed")
   └─ SHA256(token_arg) ≠ token_hash → die(5, "token_mismatch")

2. ⚠️ 立即標記 consumed=true + consumed_at（寫回 plan）
   （先標記再送出——寧可浪費一次 dry-run 也不要重複送單）

3. 登入 UOF（復用 login()）

4. 開表單頁面 + find_form_frame + verify_schema
   ├─ 任何 selector 找不到 → die(4, "form_layout_changed")
   └─ 成功 → 繼續

5. 逐欄位填入（與 Phase A 相同邏輯）

6. 逐欄位回讀比對
   ├─ 讀回每個欄位的實際值（input.value / select.value / radio checked）
   ├─ 與 plan.fields 逐一比對
   ├─ 任何不一致 → die(6, "field_mismatch", detail={欄位, 預期, 實際})
   └─ 全部一致 → 繼續

7. 點送出鈕
   ├─ selector: 表單的「送出/儲存」按鈕（需 recon 確認 id）
   ├─ 等待 navigation 或 postback 完成（timeout 30s）
   ├─ 偵測頁面 response：
   │   ├─ 出現「送出成功」/ redirect 到 PersonalBox → 成功
   │   ├─ 出現 alert / validation error → die(7, "submit_rejected", detail=訊息)
   │   └─ 超時 / 未知狀態 → die(8, "submit_status_unknown")
   └─ 成功 → 繼續

8. 送後驗證（PersonalBox 確認）
   ├─ 導航到個人申請箱
   ├─ 找最新一筆加班單（依日期+時間比對）
   ├─ 確認狀態 = 簽核中
   ├─ 驗證成功 → 截圖存檔
   └─ 找不到 → 回報 warning（不 die，因為可能只是列表刷新延遲）

9. 輸出結果 JSON
```

### 輸出 JSON（Phase B）

```json
{
  "mode": "submitted",
  "form": "overtime",
  "plan_file": "...",
  "status": "success|rejected|unknown",
  "verification": {
    "found_in_personalbox": true,
    "form_status": "簽核中",
    "screenshot": "~/.config/uof/dry_run/submit_verify_20260720_183500.png"
  },
  "detail": null
}
```

### 錯誤碼擴充（Phase B 新增）

| exit code | error | 說明 |
|---|---|---|
| 5 | `plan_not_found` | plan 檔不存在 |
| 5 | `plan_already_consumed` | 這個 plan+token 已經用過了 |
| 5 | `token_mismatch` | CLI 傳入的 token 與 plan 紀錄不符 |
| 6 | `field_mismatch` | 填入後回讀比對不一致（detail 含哪個欄位差異） |
| 7 | `submit_rejected` | 點送出後頁面回傳 validation error |
| 8 | `submit_status_unknown` | 超時或無法判定送出是否成功——**不重試** |

### 安全防線總結（5 層）

| 層 | 防護 | 繞過條件 |
|---|---|---|
| L1 | CLI flag 隔離：沒有 `--submit` 就物理上不可能送出 | 使用者主動加 flag |
| L2 | Plan + Token：dry-run 必須先跑成功才有 token | 拿到 token |
| L3 | 使用者確認：agent 透過 <<ASK>> 按鈕等使用者點「確認送出」 | 使用者點按鈕 |
| L4 | 二次比對：Phase B 重新填表後逐欄位回讀，不一致就中止 | 欄位值一致 |
| L5 | 一次性消耗：token 用過即失效，plan 標 consumed | 重新跑 dry-run |

### Bridge 端整合（SKILL.md 流程）

```
使用者：「幫我填 7/20 18:30 加兩小時班，事由：版本上線」
  → agent 跑 uof_form.py overtime --date ... (Phase A dry-run)
  → agent 用 <<SEND_FILE:截圖路徑>> 傳截圖給使用者
  → agent 用 <<ASK:ot_confirm|*submit=確認送出|cancel=取消>> 詢問
  → 使用者點「確認送出」
  → agent 跑 uof_form.py overtime --submit --token <token> (Phase B)
  → agent 回報結果（成功/失敗）
  → 若成功，附上驗證截圖（PersonalBox 的新表單）
```

### Recon 結果（2026-07-14 Playwright 自動抓取）

#### 送出按鈕（frame 2，表單 iframe 內的 MasterPage 區域）

| id | 文字 | visible | 用途 |
|---|---|---|---|
| `ctl00_MasterPageRadButton1` | 儲存 | ✅ | 存草稿（暫存不送出） |
| `ctl00_MasterPageRadButton3` | 送出 | ❌ display:none | 舊版送出（被隱藏，不用） |
| **`ctl00_MasterPageRadButton13`** | **送出** | ✅ | **P3 要點的按鈕** |
| `ctl00_MasterPageRadButtonClose` | 關閉視窗 | ✅ | 關閉 dialog |

按鈕型態：Telerik `RadButton`（`<span class="RadButton ...">` + `autoPostBack:true`），點擊觸發 ASP.NET postback。

#### 送出後行為（從 FirstSitejs 抽取）

```
點「送出」(RadButton13) → postback → server 驗證欄位
  → 驗證失敗：頁面回傳 validation message（可抓 alert / validator text）
  → 驗證成功：設 hiddenActionMode="Send"，server 回 script 開簽核 dialog：
      $uof.dialog.open2(簽核URL, '', title, 850, 500, signDialogResult)
      → 簽核 dialog 內自動帶入簽核人
      → dialog 返回 returnValue → 主 dialog 也 close
```

**注意**：送出後會彈出**簽核確認 dialog**（850×500），這不是普通 alert，是另一個 iframe dialog。P3 實作需要：
1. 偵測 postback 完成後是否彈出新 dialog（`$uof.dialog.open2` 會在 DOM 產生新的 RadWindow）
2. 在簽核 dialog 裡找確認按鈕並點擊（或者直接等待 returnValue 回傳）
3. 最終結果是主 dialog 自動關閉（`$uof.dialog.close()`）

#### RadButton 觸發方式（v6-v8 實測確認）

- **正確方式**：Playwright `frame.locator("#ctl00_MasterPageRadButton13").click()` — 真實 DOM click 事件可觸發 Telerik autoPostBack
- **錯誤方式**：`$find().click()`（RadButton server-side 模式沒有 client object）、`__doPostBack()`（Telerik strict mode 衝突）
- Postback 後的結果：
  - **validation 失敗**：server 回一個 **JS `alert()`**（Playwright `page.on("dialog")` 可攔截），例如：
    - `"加班開始時間...未到，不可事先填寫加班！"`
    - `"無上下班刷卡時間，無法填寫加班單！"`
  - **validation 成功**：`hiddenActionMode` 變 `"Send"` → 開簽核 dialog → 確認後 `$uof.dialog.close()` 關主表單
- Server validation 規則（實測確認）：
  - 加班時間必須已經過了（不能事先填未來的）
  - 該日必須有上下班刷卡紀錄
  
#### P3 實作的送出流程設計

```python
# 1. click 送出
frame.locator("#ctl00_MasterPageRadButton13").click()

# 2. 等待結果（三種可能）：
#    a) JS alert → server validation 失敗
#    b) 新 frame 出現（簽核 dialog）→ 找確認按鈕
#    c) timeout → 狀態不明

# 3a. 攔截 alert
page.on("dialog", handler)  # 記錄 message，accept() 關閉

# 3b. 等新 frame / RadWindow，找確認按鈕
#     簽核 dialog URL 包含 "Sign" 或 WKF 簽核頁面
#     dialog 內的確認按鈕可能是 RadButton 或 rwPopupButton

# 4. 簽核 dialog 確認後，外層 dialog 自動 close
#    偵測方式：外層 RadWindow 的 display 變 none，或 frame 被 detach
```

#### 草稿列表（驗證已送出用的對照）

表單開啟頁 `ApplyFormList.aspx` 右側有 `DGDraftList`（GridView），結構：
- 每列 id：`..._DGDraftList_ctl{NN}_lbtnDraftModify`
- 含 scriptId（唯一識別）
- 文字格式：「加班單YYMMDD」（民國年月日）

#### 已送出表單查詢

`PersonalSentSearch.aspx` 需要輸入查詢條件才顯示結果（初始為空表格）。P3 送後驗證可改用以下策略之一：
- **策略 A**：送出前記錄草稿列表數量，送出後確認數量減少（代表草稿變成正式單）
- **策略 B**：送出後到 PersonalSentSearch 查詢當天日期的加班單，確認出現
- **策略 C**：偵測主 dialog 自動 close 作為成功信號（最簡但較脆弱）

建議**策略 A + C 組合**：dialog close = 初步成功信號 + 檢查草稿列表少一筆 = 確認。

### 不做的事（明確排除）

- ❌ 自動重試（狀態不明 → 停止，由人確認）
- ❌ 修改/刪除既有加班單（本工具只做新申請）
- ❌ 跳過截圖確認直接送出（即使 agent 可以比對 JSON，使用者視覺確認是必要步驟）
- ❌ 批次送出多張（一次一張，降低風險）

## 待辦（Roadmap）

填單功能目前停在 P2（dry-run + 截圖，使用者自行到瀏覽器手動送出）。後續視需求推進：

- **P3 真正送出**（設計規格已完成，見上方 section）：待 recon 送出鈕 selector + 送出後頁面行為 + PersonalBox 列表 selector 後可進入實作。
- **P4 請假單 dry-run/填單**：復用 `uof_form.py` 的 dry-run 機制，但請假單的假別（UC3）與後續欄位（UC5/UC6）有連動 cascade，需要額外 recon 選了假別之後 postback 出現的欄位再處理，比加班單複雜。
- **P5（選配）假日加班事先申請單**（`formId=87be8977-...`）：先確認公司流程上是否真的跟一般加班單（`cd8fb94e-...`）分開送，還是語意重疊；沒有明確需求前不做。
- **已確認項**（2026-07-14 使用者實測，原「待確認項」已全部解決）：
  - ✅「專案負責人」（UC16）非必填——留「─請選擇─」可送出。
  - ✅「是否調為補班」（UC17）系統不會覆蓋——填什麼就是什麼。
  - ✅ UOF 加班單**無撤回機制**——送出即定案。

## 驗證方式
- 開發時已用真站台跑通全部路徑（登入、加班統計、特休表頭、逐月、行事曆換算）。
- 成品驗收：`uof_query.py`（全查）輸出的本月/當年度加班、特休餘額、剩餘上班日與每上班日換算，均與網站實際查詢一致。
- 加固後回歸：5 項修正逐一實測（含真站台 0 筆區間回 0、`--overtime-year` 帶 month.status）。
- `uof_form.py overtime` dry-run 已用測試資料實跑一次，截圖視覺比對欄位填值正確。
```
