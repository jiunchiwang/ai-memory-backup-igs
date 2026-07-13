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

## 待辦（Roadmap）

填單功能目前停在 P2（dry-run + 截圖，使用者自行到瀏覽器手動送出）。後續視需求推進：

- **P3 真正送出**：`uof_form.py overtime --submit --token <token>`。設計已在 dry-run 階段產生 plan 檔（含填入內容 hash）+ token，`--submit` 讀 plan 檔重新開表單、比對 prefill 欄位（部門/簽核人）與 dry-run 記錄一致才送出，送出後到 PersonalBox 驗證新表單出現。狀態不明時絕不自動重試（防重複開單），改回報用戶自行確認。這是目前**風險最高**的階段，需要先確認個人申請箱有沒有抽單/撤回機制（決定填錯的代價多大），再動手。
- **P4 請假單 dry-run/填單**：復用 `uof_form.py` 的 dry-run 機制，但請假單的假別（UC3）與後續欄位（UC5/UC6）有連動 cascade，需要額外 recon 選了假別之後 postback 出現的欄位再處理，比加班單複雜。
- **P5（選配）假日加班事先申請單**（`formId=87be8977-...`）：先確認公司流程上是否真的跟一般加班單（`cd8fb94e-...`）分開送，還是語意重疊；沒有明確需求前不做。
- **待確認項**（做 P3 前應該先釐清，不確定性標記）：
  - 「專案負責人」（UC16）在畫面上沒有紅色必填星號，但實際送出時是否為隱性必填未驗證過（目前 dry-run 沒給值時維持「─請選擇─」）。
  - 「是否調為補班」（UC17）目前一律預設「否」；表單註記「每月加班前四小時預設為補班，超過可自行選擇」，暗示公司系統本身可能有自動判斷邏輯，需要真的送出一次才能確認這個欄位的預設值會不會被系統覆蓋。

## 驗證方式
- 開發時已用真站台跑通全部路徑（登入、加班統計、特休表頭、逐月、行事曆換算）。
- 成品驗收：`uof_query.py`（全查）輸出的本月/當年度加班、特休餘額、剩餘上班日與每上班日換算，均與網站實際查詢一致。
- 加固後回歸：5 項修正逐一實測（含真站台 0 筆區間回 0、`--overtime-year` 帶 month.status）。
- `uof_form.py overtime` dry-run 已用測試資料實跑一次，截圖視覺比對欄位填值正確。
```
