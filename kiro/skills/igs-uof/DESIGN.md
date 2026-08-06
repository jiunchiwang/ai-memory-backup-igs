# igs-uof — 設計文件

> **v2 2026-07-15 brainstorming 定案**：由 `vc-uof-hours` 改名擴充為 `igs-uof`，從「加班/特休查詢」擴充為「UOF 內網查詢類操作」入口。狀態：**已實作（2026-07-15），全子命令活站實測通過**。v1（2026-07-13，加班/特休）設計見 git 歷史，其系統事實已併入本文件。

## 目的與定位

透過 AI 用中文查公司內網 UOF（U-Office Force）的個人差勤與辦公資訊。**公司共享 skill**：`igs-` 前綴 = 會分享給 IGS 同事的公司內部 skill（與 `vc-` 個人 skill 區隔，此命名規則記錄於 conventions.md），持續維護 SETUP.md 供同事安裝（Mac/Windows）。

## 範圍

**保留（行為不變）**：
1. 加班時數（本月/當年度/逐月）＋目標進度分析＋每上班日換算（v1 全部功能）
2. 剩餘特休

**新增（查詢類，全部唯讀）**：
3. `attendance` 出勤/打卡記錄：預設逐日彙總（刷卡起迄＋當日加班/請假；資料延遲約 2 天），`--punch` 查即時刷卡流水（含今日）
4. `leave` 請假記錄（假別/起訖/時數/事由/簽核狀態；可篩假別與狀態）
5. `todo` 待簽核/待辦件數與清單；`--sent` 查自己送出單子的簽核進度
6. `whois` 同仁通訊錄（姓名/部門/組/分機/員編/Email）

**不做（v2 公司共享範圍已排除）**：申請類（填請假單/加班單）與簽核類（同意/否決）等**寫入操作**——`uof.py` 的子命令路由不含這些。

**個人擴充（2026-07-16 決定保留，不進公司共享範圍）**：`scripts/uof_form.py` 保留 v1（2026-07-13）的加班單 dry-run 填單 + 二階段確認送出（詳見下方「v1 加班單欄位」與「填單安全設計」章節）。這是刻意違背上一段「用戶已排除」決定的例外——v1 已有此功能，合併 v2 時使用者明確要求保留。權衡：寫入操作已有 dry-run 截圖 + 二階段確認 + `verify_schema` 版型守衛三層防護，風險可控；但**若此 skill 要整包分享給同事，需重新評估是否移除 `uof_form.py`**（SKILL.md 已標註此提醒）。實作為獨立腳本、不掛 `uof.py` 子命令路由，登入/session 改用 `uof_client.open_uof()` 共用（v1 原本各自獨立登入，未享有 session 持久化）。

**recon 後移除（2026-07-15 實測）**：
- `news` 公告：UOF Bulletin 模組（EIP/Bulletin/Default.aspx）所有分類（最新/公司/內部/團膳公告）與首頁「最新公告」widget 皆「沒有資料」——IGS 未使用此模組，無資料可查。
- `leave` 的「各假別餘額」：請假資料查詢頁（BAA）只有記錄無餘額；UOF 僅特休餘額可查（請假單表頭，已在 `hours --annual-leave`）。其他假別餘額無資料來源。

## 改名計畫（vc-uof-hours → igs-uof）

- `git mv skills/vc-uof-hours skills/igs-uof`；frontmatter `name: igs-uof`；description 擴寫觸發詞（打卡、請假、待簽核、公告、分機/通訊錄…）。
- ⚠️ **目錄改名會弄壞 `.venv`**（venv 內含建立時的絕對路徑）→ 改名後刪除重建。
- 設定檔 `~/.config/uof/config.json` **路徑不變**（鍵名沿用），既有使用者免動設定。
- SETUP.md 加「舊版 vc-uof-hours 遷移」段：改資料夾名＋重建 venv 即可。
- conventions.md append `igs-` 命名空間規則（公司共享 skill）。
- 外部引用檢查（2026-07-15）：`~/.claude` 下無其他檔案引用 `vc-uof-hours`，rename 無連鎖改動。

## 架構

```
~/.claude/skills/igs-uof/
├── SKILL.md              # 路由表（用戶問題→子命令組合）＋每功能回答要點＋錯誤表
├── DESIGN.md             # 本文件
├── SETUP.md              # 同事安裝說明（Mac/Windows）＋舊版遷移段
├── requirements.txt      # playwright, xlrd
├── config.example.json   # 設定檔範例
├── scripts/
│   ├── uof.py               # CLI 入口：子命令路由；一次可帶多個子命令
│   ├── uof_client.py        # 共用：設定/帳密/登入/重複登入/驗證碼/session 持久化/die/frame helpers
│   ├── cmd_hours.py         # v1 加班+特休+目標進度分析邏輯搬移（行為與 JSON 不變）
│   ├── cmd_attendance.py    # 打卡記錄
│   ├── cmd_leave.py         # 請假記錄+假別餘額
│   ├── cmd_todo.py          # 待簽核/待辦（--sent 已送審進度）
│   ├── cmd_whois.py         # 同仁通訊錄（分機查詢）
│   ├── calendar_workdays.py # 工作日提供者（不動）
│   └── uof_form.py          # 個人擴充：加班單 dry-run 填單 + 二階段確認送出（不掛 uof.py 子命令路由）
└── .venv/                   # 改名後重建
```

### 呼叫模型
- `uof.py <子命令>... [flags]`，例：`uof.py todo news`、`uof.py hours --analysis`、`uof.py attendance --from 2026/07/01 --to 2026/07/15`。
- **一次呼叫多子命令 = 單次登入依序執行**，輸出合併為單一 JSON（頂層鍵 = 子命令名 + `as_of` + `params`）。
- **例外（實作時裁定）**：`hours` 沿用 v1 輸出形狀——`overtime`/`annual_leave` 直掛頂層、其 params 併入頂層 `params`——以保住回歸基準；只有新子命令用子命令名當頂層鍵。`params.session` 回報 `new`/`reused`（session 持久化的可觀察欄位）。子命令失敗時（含 hours）錯誤 payload 一律放在**子命令名**鍵下（如 `"hours": {"error":"scrape_failed",…}`），成功結果整包 atomic。
- 不帶子命令 = `hours` 全查；未冠子命令的 flags 也歸 hours（向後相容 v1 直接下 flags 的用法）。

### 錯誤模型（兩級＋session 特例）
- **全域錯誤**（發生即整體中止，JSON `{"error":...,"hint":...}` + 非 0 exit，同 v1）：`unreachable`(2)、`login_failed`/`captcha`/`no_credential`(3)、`bad_config`/`bad_args`/`browser_launch_failed`/`login_error`(5)。
- **功能級錯誤**：單一子命令失敗時，該子命令結果為 `{"error":...,"page":...,"hint":...}`，**其餘子命令照常執行** — 組合查詢可部分成功，整體 exit 4。錯誤值：`scrape_failed`（版型變化、Playwright 逾時/DOM 異常）、`unexpected_error`（保底，任何非預期例外都不得打破「輸出單一 JSON」契約）。
- **session 中途失效特例**（`session_expired`，exit 3）：查詢中途被踢（互踢競態）→ 錯誤記在當前子命令鍵、**停止後續子命令**（session 已死，續跑必然全失敗），但**已完成子命令的結果保留並照常印出**。
- SKILL.md 錯誤表對應更新：解讀 JSON 時逐鍵檢查 `error` 欄。

### Session 持久化（已核可納入）
- 登入成功後 `context.storage_state(path=~/.config/uof/session.json)`（建檔後 chmod 600；Windows 沿用 NTFS 預設權限）。
- 啟動時若 session 檔存在 → 用它建 context → goto `Homepage.aspx` 驗證（redirect 到 Login.aspx 即失效）→ 失效才走帳密登入並回存。
- 效益：有效期內免登入（省 ~10s），且**不觸發重複登入互踢**（v1 每次執行都踢掉瀏覽器的 UOF session，查詢頻率變高後此痛點放大）。
- `--fresh-login` flag 可強制忽略舊 session（debug 用）。
- 敏感性：session 檔含 cookie，與 config.json 同等級；不入 git（設定目錄本來就在 repo 外）。

## 子命令規格

| 子命令 | 預設 | 主要 flags | 輸出（依 recon 實測定案） |
|---|---|---|---|
| `hours` | 全查（=analysis+annual-leave） | v1 全部 flags 沿用（--target/--basis/--approved-only/--overtime-month/--overtime-year/--annual-leave/--analysis） | v1 JSON 原樣（`overtime`+`annual_leave` 掛頂層） |
| `attendance` | 本月 1 日～今天（彙總） | `--from --to`（YYYY/MM/DD）；`--punch` 改查刷卡流水 | 彙總：`{total, days:[{date, first_in, last_out, type, overtime:{...}, leave:{...}}], note}`；punch：`{total, punches:[{time, gate}]}` |
| `leave` | 今年 1/1～12/31 | `--leave-from --leave-to`、`--kind 假別`、`--status 狀態` | `{total, records:[{kind, start, end, hours, reason, status}]}`（自動翻頁合併） |
| `todo` | 待簽核件數＋清單 | `--sent`（改查已送審表單進度） | `{counts:{sign_self, sign_agent, returned, informed, consulted}, items:[…]}`；sent：`{total, forms:[{no, form, title, applied_at, closed_at, current_signer}]}` |
| `whois` | —（至少帶一個條件） | `--name`、`--ext`、`--empno` | `{total, people:[{dept, team, name, ext, empno, email}], updated_at}` |

- 共用 flags：`--headed`（驗證碼手動過）、`--fresh-login`。
- **flag 名稱全域唯一**：所有子命令的 flags 在同一個 parser 下不得重名（故 leave 用 `--leave-from/--leave-to` 與 attendance 的 `--from/--to` 區隔），一次帶多子命令時才不會歧義。

## 系統事實（v1 recon 2026-07-13 實測，cmd_hours 沿用）

- 站台：`http://uof/UOF/`，ASP.NET WebForms + Telerik，版本 28.0.9137D。
- 登入：`Login.aspx`，`#txtAccount` / `#txtPwd` / `#btnSubmit`；正常不需驗證碼（多次失敗才出現 `#captchaImage`）；重複登入出現 `#btnRemoveRepeatLogin`；成功導向 `Homepage.aspx`。
- 加班統計：`Project/BAE/Stats_Search.aspx`。`#SDate`/`#EDate` 必須 JS 設值（datepicker 會蓋按鈕）；簽核狀態 `#StsChkBoxList_0..3`（同意/否決/簽核中/作廢）**四個都明確 set 目標狀態**，缺任一 id 即 `scrape_failed`（防靜默汙染）；送出 `__doPostBack('BtnSubmit','')`；結果抓 footer 正則 `平日加班時數合計…假日…補班…`；0 筆時 footer 不渲染 → 回 0 不中斷；跨部門多列時 footer 已是加總。
- 特休：請假單 `WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=14ac1707-9566-4f02-b895-3da0e7395310`，掃 frames 找「特休未休」正則；渲染慢等 5s。
### 新頁面 recon 事實（2026-07-15 實測）

- **出缺勤查詢（attendance 預設）**：`Project/VPPA/Search.aspx`（可直連）。控制項 `#TypeRadioBtnList_0`(部門)、`#DeptList`、`#UserList`、`#SDate`/`#EDate`（YYYY/MM/DD，JS 設值）、`#BtnSubmit`。結果：`總筆數：N`＋TSV 表，欄：部門/專案|人員|日期|出勤類別|刷卡起時|刷卡迄時|加班類別|加班起時|加班迄時|加班時數|請假類別|請假起時|請假迄時|請假時數。時間格式 HHMM，倒序。⚠️ 資料延遲約 2 天（實測 7/15 查詢最新列為 7/13）。
- **打卡資料查詢（attendance --punch）**：`Project/EQRsearch/index.php`（PHP，URL 帶加密 token，**必須經 `System/CustomMenu/LinkUrl.aspx?menuID=39483847-5b19-4430-87c2-7699ea3c2742` 的 linkFrame 進入**）。控制項（frame 內）`#Group_ID`、`#USER_GUID`、`#stime`/`#etime`（YYYY/MM/DD）、`#Submit`。結果：`總筆數：N`＋rows 流水編|打卡時間(YYYY-MM-DD HH:MM:SS)|姓名|門組。即時（含今日）。
- **請假資料查詢（leave）**：`Project/BAA/Search.aspx`（可直連）。控制項同 VPPA 家族＋`#KindList`（假別 24 種）＋`#StsList`（全部/同意/否決/簽核中/作廢）。結果：`總筆數：N`＋`#GridView1`，欄：部門/專案|請假人|假別|開始時間(YYYY/MM/DD HH:MM)|結束時間|時數|事由|類別|簽核狀態。**分頁每頁 20 筆**，pager 連結 `__doPostBack('GridView1','Page$N')`，需自動翻頁合併。
- **個人表單（todo）**：`WKF/FormUse/PersonalBox/MyFormList.aspx?item=SignSelf`。左側分類樹文字含件數，正則可解析：`待簽表單-自己(N)`、`待簽表單-代理(N)`、`被退回的申請(N)`、`被知會表單(N)`、`被徵詢表單(N)`（急件細分 普通/急/緊急/逾時）。⚠️ **已知限制**：右側清單 grid 於 recon 時 0 件、真實 id 未實測；`_grids()` 以 `table[id*='grd']` 假設與 FormExamined 的 `…_grdFormExamined` 同命名家族。若日後有待簽件時 `items` 空但 `counts` 非 0（輸出會附 note 提示不對稱），即此假設破功，屆時補 recon 修 selector。
- **已送審表單（todo --sent）**：`MyFormList.aspx?item=FormExamined`。grid `#…_grdFormExamined`，欄：表單編號|表單名稱|標題|結果|申請時間|結案時間|目前簽核者|操作；頁腳 `Export筆數:… 共 N 筆…共 N 頁`。
- **電話分機查詢（whois）**：`CDS/WebPage/ExtQuery.aspx`（可直連）。控制項 `#name_TB`、`#engName_TB`、`#empno_TB`、`#company_DL`、`#department_DL`、`#team_DL`、`#ext_TB`、`#searchBtn`。結果 `#resultGrid`，欄：(2 空欄)|部門|組|姓名|分機|員工編號|Email；頁首 `查詢筆數: N筆`＋`資料最後更新時間: …（每小時更新）`。**0 筆時不渲染「查詢筆數」與 `#resultGrid`，只顯示「查無資料」**（2026-07-15 實測）→ 視為 total=0，不報錯。
- **公告（已移除）**：`EIP/Bulletin/Default.aspx` 分類樹可點（postback），但所有分類含團膳公告皆「沒有資料」；首頁「最新公告」widget 同樣空。IGS 未使用此模組。

## Cloudflare 人機驗證與 CDP 接管（2026-08-06 實測定案）

**系統事實**：UOF 在**登入成功之後**跳 `AntiBotCheck.aspx?targetUrl=…`（頁面標題「安全驗證 - UOF System Verification」，內嵌 `challenges.cloudflare.com/…/turnstile/…` iframe 的「驗證您是人類」勾選框）。實際 host 為 `https://hq.igs.com.tw/UOF/`（`BASE` 的 `http://uof/UOF/` 會被 redirect 過去）。

**三臂實驗**（同一天、同帳號、同網路）：

| 臂 | 做法 | 結果 |
|---|---|---|
| 1 | Playwright 內建 Chromium `launch(headless=False)` | ❌ 停在 AntiBotCheck；連 Turnstile iframe 都定位不到 |
| 2 | Playwright `launch(channel="msedge")` 真 Edge headed | ❌ 等 241 秒未過（iframe 有抓到） |
| 3 | 使用者自行啟動的 Edge（`--remote-debugging-port` + 獨立 profile）+ 真人點擊 → `connect_over_cdp` 接管 | ✅ 查詢正常 |

∴ **分野是「瀏覽器是否由自動化啟動」，不是瀏覽器廠牌、也不是無痕模式**。換瀏覽器與開無痕都無效（臂 1/2 已否證）。已排除的路徑：stealth 參數、指紋偽裝（使用者 2026-07-30 明確決定不做這類工程）。

**修掉的假陽性**：`_goto_home_ok()` 只判 URL 有無 `login.aspx`，被導到 AntiBotCheck 時回 True → `open_uof` 回報 `session: reused/new`（看起來成功），失敗延後到查詢頁才炸成 `scrape_failed` / `Page.goto Timeout`；2026-07-30 因此被誤讀成「連不到內網」。現在 `open_uof` 的兩條路徑（session 重用後、帳密登入後）與 `attach_uof` 各接一個 `_die_if_antibot()`，改報全域錯誤 `antibot`(3)。

**新增錯誤值**：`antibot`(3)、`cdp_no_uof_page`(3)、`cdp_connect_failed`(5)、launcher 的 `cdp_port_in_use`/`cdp_not_ready`/`browser_not_found`/`browser_launch_failed`(5，後者與 `uof_client` 既有的同名錯誤同語意)。

`antibot` 的兩個維度（第三輪覆核 F-A/F-B 修正）：
- **hint 依模式分流**：`ANTIBOT_HINT_LAUNCH`（還沒接管 → 跑 launcher、**別重試同一條命令**）／`ANTIBOT_HINT_ATTACHED`（已在 CDP、視窗被重新挑戰 → 在既有視窗重點驗證即可、**重跑同一條命令**）。兩者的處置**相反**，∴ 文件不可寫成單一無條件指引，必須要 agent 以 `hint` 為準。
- **錯誤層級依觸發點分流**：擋在 session 建立點 → 全域錯誤（`die`，整份 JSON 只有 `error`）；查詢中途被重新挑戰 → **功能級**錯誤（掛該子命令鍵、`break` 停止後續，已完成子命令結果保留），語意同 `session_expired`。SKILL.md 兩處都要載明，否則 agent 會把仍然有效的部分結果整批丟掉重查。

**CDP 模式設計**：
- `open_uof(..., cdp=endpoint)` → 委派 `attach_uof()`：`connect_over_cdp` → 取 `contexts[0]` → 挑 URL 含 `/uof/` 的分頁 → antibot 檢查 → 若停在 Login 頁則代填帳密登入 → 再檢一次 antibot（驗證在登入後才跳）→ 存 session。`session_mode` 回 `'cdp'`。
- ⚠️ **承重連動**：呼叫端原本一律 `ctx.close(); browser.close()`，那會關掉**使用者自己的瀏覽器**、害他重過一次驗證。∴ 新增 `close_uof(browser, ctx, session_mode)`，`'cdp'` 時 no-op；`uof.py` 與 `uof_form.py`（Phase A/B）共 3 處收尾全部改走它。這條是本次改動最容易漏的地方，已用「跑完後 curl `/json/version` 確認瀏覽器還活著」實測。
- 過驗證**之前**刻意不用 CDP 碰那個頁面（減少自動化痕跡）；帳密代填只發生在已過驗證之後。
- `launch_cdp_browser.py`：Edge→Chrome 依平台找路徑，獨立 `user-data-dir`（既有瀏覽器在跑時 `--remote-debugging-port` 會被忽略，故不共用預設 profile），輪詢 `/json/version` 確認 port 起來才回 JSON。

### 異源覆核紀錄（Fable 5，2026-08-06，0 high / 3 medium / 6 low）

採納並修掉：

| # | 問題 | 處置 |
|---|---|---|
| M1 | `attach_uof` 存 session → `storage_state()` 匯出 context **全部 origin** 的 cookies。**實證比覆核者說的更嚴重**：連 launcher 的乾淨 profile 都混進 `.msn.com`/`.bing.com`/`turbo.microsoft.com`（18 顆 cookie 有 12 顆無關），且 `chmod 600` 在 Windows 是 no-op（實測 mode 666） | CDP 模式**不存 session**；已污染的 session.json 就地清洗只留 `hq.igs.com.tw`；`_save_session` 加警告 docstring；`browser_not_found` 的手動啟動 hint 補「用獨立目錄」 |
| M2 | antibot 偵測只護 session 建立點。clearance 中途失效 → selector 逾時 → 回報 `scrape_failed`「版型可能改變」，填單更報「表單版型變了」——**正是這次要修掉的誤診模式在 mid-session 復發** | 新增 `antibot_result()`；`run_segments` 三條 except 分支（ScrapeFailed / PlaywrightError / 保底 Exception）各先問一次，命中即回 `antibot`(3) 並停止後續；`uof_form` 兩處 `find_form_frame` 失敗處同樣先排除 |
| M3 | launcher 先 Popen 再輪詢 `/json/version`，port 已被別的 CDP 瀏覽器占用時會打到**別人**的瀏覽器並回報假成功（本機有其他 CDP 工具，情境真實） | Popen **之前**先探一次 port，占用即報 `cdp_port_in_use` 並指出兩條出路 |
| L1 | CDP 模式下 hint 指錯方向（叫已在 CDP 的人去跑 launcher；驗證碼叫他用 `--headed`） | `_die_if_antibot(attached=)` / `login(attached=)` 兩套 hint |
| L3 | `--browser chrome` 仍會靜默 fallback 到 Edge；缺 Chrome 使用者層安裝路徑 | 明確指定不 fallback；補 `%LOCALAPPDATA%` 路徑 |
| L6 | `attach_uof` 只看 `contexts[0]`，使用者開無痕視窗（獨立 context）時誤報 `cdp_no_uof_page` | `_pick_uof_page(browser)` 掃全部 context，回 `(ctx, page)` |
| L2 | `--fresh-login` / `--headed` 在 CDP 模式被靜默忽略 | uof.py docstring + SKILL.md 明載 |

**第二輪覆核（範圍限定在上表的修正集）抓到 1 medium + 3 敘事**，全部已修：

- **F1**（medium，行為）— 修 M2 時把 L1 剛修掉的同型錯誤又埋回來：新寫的 `antibot_result` 硬編 `ANTIBOT_HINT_ATTACHED`，非 CDP 模式中途被重新挑戰時會叫使用者「去點那個接管的視窗」（不存在）並「重跑本命令」（按三臂實驗必敗，且與 SKILL.md 的「別重試」矛盾）。根因：`run_segments` 拿不到 `mode`，`main` 手上有卻沒傳。→ `antibot_result(page, attached)` + `run_segments(..., attached=(mode == "cdp"))`。
- **F2/F3/F4**（敘事）— `run_segments` 函式層 docstring 未同步新的 antibot 出口、DESIGN 的新增錯誤值清單漏 `cdp_port_in_use`、`uof_form.py` 頂部離開碼清單未涵蓋 antibot/cdp 錯誤。→ 三處補齊。

**第三輪覆核（Sonnet，範圍限第二輪的修正集）抓到 2 條敘事-行為不符 + 3 條列舉不全**，全部已修：

- **F-A**（medium-high）— SKILL.md 錯誤表的 `antibot` 列無條件寫「別重試同一條命令」，但碼在 attached 情境的 hint 明寫「重跑本命令」。**兩種情境的正確處置是相反的**，靜態文件寫成單一指引就必然有一半是錯的；agent 照表做會在已有視窗的情況下再開一個多餘的瀏覽器。→ 錯誤表列出兩種情境並要求以 `hint` 為準；agent 端流程段補 attached 分支。
- **F-B**（medium）— `antibot` 只列在「全域錯誤」表，但 mid-query 觸發時走的是功能級路徑（`result[cmd]` + `break`，保留已完成結果）。agent 可能因此把仍有效的部分結果整批丟掉重查。→ 功能級錯誤段補一則跨兩層的說明。
- **F-C**（low，3 項）— `uof_form.py` 離開碼清單漏 `cdp_no_uof_page`（exit 3，且同樣在 token 標 consumed 之後才觸發）、DESIGN 錯誤值清單漏 `browser_launch_failed`。→ 補齊。

∴ 這批改動的失敗模式**逐層上移過三次**：碼（F1 的 hint 硬編）→ hint 敘事 → 靜態文件（F-A/F-B）→ 列舉完整性（F-C）。三輪都是異源抓到，同源自審每一輪都宣稱「只剩敘事精確度」而每一輪都還有行為面的錯。這條經驗比本次的功能本身更值得記住：**守衛類改動的缺陷會往上層遷移，修完碼不等於修完，文件層的錯一樣會讓 agent 做錯事。**

未採納：

- **L4**（Phase B 的一次性 token 在「開瀏覽器前就失敗」時被燒掉）— 既有設計，`unreachable`/`login_error` 早就同樣會燒；CDP 模式只是提高了該分支機率。動 token 消耗順序是寫入路徑改動，超出本次 scope → **列為 follow-up**。
- **L5**（`--cdp-endpoint` 忘給值會吞掉下一個 token）— 標準 argparse 同行為，且失敗訊息會顯示 endpoint 值可自行診斷 → 不改，僅記錄。

覆核者查核後**無 finding** 的面（我自己複驗過的）：`die()` 拋 `SystemExit` 落在 `except SystemExit: raise` 先於 `except Exception` 的結構內、`run_segments` 的 `except Exception` 不吞 `BaseException`、`with sync_playwright()` 的 `__exit__` 保證非 CDP 路徑不洩漏瀏覽器、`close_uof` 全庫 3 個收尾點全覆蓋（剩下唯一裸 `ctx.close()` 只在非 CDP 分支可達）、`parse_segments` 改寫 13 組邊界輸入不變。

## 用詞規範（2026-07-15 用戶回饋）

- **框架**：`monthly_target` 是**個人自訂的加班目標時數**（personal goal），不是「公司最低標準/配額」。所有用戶可見的中文（SKILL.md 回答指引、SETUP.md、CLI help、JSON 內的中文 hint/note）一律採「目標」framing。
- **用**：個人加班目標、目標進度、距目標還差 X 小時、較目標進度超前/落後 X 小時。
- **避免**：「達標」「缺口」「需補時數」這類「不足額必須補齊」語感的字眼。
- **例外**：(1) 觸發詞可容納用戶口語（用戶問「達標了沒」仍要能觸發），但回覆不用這些詞；(2) JSON **英文鍵名不改**（`target`、`still_needed`、`gap_ytd` 等，保住回歸基準），只改中文文字值。

## 判定參數與工作日換算（v1 沿用，不變）

- 參數優先序：CLI > 設定檔 > 內建預設。計入基準（`countable_basis`，哪些加班計入目標）預設 `weekday+holiday`；簽核狀態預設 同意+簽核中；個人月目標預設 20h。實際採用值回 `params`。
- 工作日三層：內建 BAKED（2026）→ Downloads 行事曆 .xls（民國年檔名，底色分類＋星期全量驗證）→ 估算（平日扣七月旅遊假 5 天）。
- 目標進度公式（`target_to_date` 當月按已過工作日比例折算、`per_workday_year`/`per_workday_month` 兩判斷）照 v1，實作時整段搬移不重寫。

## 安全與副作用

- 帳密：環境變數 > `~/.config/uof/config.json` >（macOS）Keychain `uof-hr`。設定檔明文，勿分享勿進 git，建議 chmod 600。
- 全部功能**唯讀**：只 goto 查詢頁與送出查詢表單，不碰任何申請/簽核的送出鈕。
- session.json 含 cookie，敏感等級同 config.json。
- 重複登入互踢：session 重用大幅減少發生頻率，但 session 失效重登時仍可能發生，SKILL.md 保留提醒。

## hours 回歸基準

改版驗收時，`uof.py hours`（全查）的 JSON 輸出必須與改版前 `uof_query.py`（全查）**數值欄逐欄一致**（`as_of` 日期除外；中文 hint/note 文字值依用詞規範改寫，不列入比對）。搬移不重寫：目標進度分析、月中折算、工作日換算等邏輯原樣搬進 cmd_hours.py。

## 驗收

1. 真站台逐子命令實測，結果與 UOF UI 手查一致。
2. `hours` 回歸：與改版前輸出逐欄比對。
3. 組合查詢（如 `uof.py todo attendance`、`uof.py hours attendance --annual-leave`）驗證單次登入、部分失敗不中斷。
4. session 持久化：第二次執行跳過登入；手動刪 session 檔後自動重登回存；`--fresh-login` 生效。
5. Windows 相容性：維持 UTF-8 reconfigure 與跨平台路徑寫法；無 Windows 機器實測時在 SETUP.md 標註「Windows 未回歸實測」。

## v2 三階段審查加固紀錄（2026-07-15；Stage1 規格符合性 → Stage2 冷讀正確性 → Stage3 逐項對抗驗證，subagent 全為 sonnet）

10 個 findings 經 skeptic 對抗驗證後 9 個 CONFIRMED 並修復：
1. **session_expired 丟棄部分結果**（high）：7 處 `die(3)` 改 `raise SessionExpired` → run_segments 記錯誤於當前子命令鍵、停止後續、保留已完成結果、exit 3。
2. **Playwright 例外穿透**（high）：run_segments 加 `except PlaywrightError`（scrape_failed）與 `except Exception`（unexpected_error）保底，任何情況都輸出單一 JSON、exit code 落在文件承諾內。
3. **切段誤判 flag 值**（high）：`whois --name todo` 的 todo 曾被誤切成子命令 → `_value_flags()` 自 argparse 內省「吃值 flags」，切段時跳過其值。
4. **`_is_net_error` 漏 `ERR_INTERNET_DISCONNECTED` 等**（mid-high）：改 `net::ERR_` 前綴比對涵蓋整類（skeptic 驗證逐個補字串會繼續漏）。
5. **hours records=0 自相矛盾**（mid）：合計命中但總筆數缺失時改報 scrape_failed，不再回 `records:0` 配非零時數。
6. **todo --sent 總筆數靜默 fallback**（mid）：「共 N 筆」缺失時報錯（除非明確「沒有資料」），與其他子命令一致。
7. **todo 預設路徑缺截斷提示**（mid）：`pending_total > len(items)` 時補 note，與 --sent 對稱。
8. **殘留 `uof.py todo news` 範例**（doc）：DESIGN 驗收節與 uof.py docstring 改用現存子命令。
9. **`session_expired`/`login_error` 未收錄文件**（doc）：錯誤模型與 SKILL.md 錯誤表補齊，session_expired 並補 hint。
10. **whois 0 筆誤報 scrape_failed**（修復後活站驗證時發現）：查無資料時頁面不渲染「查詢筆數」→ 改判「查無資料」字樣回 total=0。

UNCERTAIN 保留為已知限制：SignSelf grid 真實 id 未實測（見系統事實節 todo 條目）。被 skeptic **推翻**而未改（記錄以免重複糾結）：`table[id*='grd']` 大小寫論證（`GridView1` 無論大小寫都不含 `grd` 子字串，非大小寫問題）；leave 翻頁 `Page$N` substring 碰撞（頁碼遞增排列，query_selector 取第一個必為正確頁）；「VPN 未連線必誤分類」（DNS 失敗與逾時路徑原本就有覆蓋，漏的是介面全關等情境）。

## v1 對抗驗證加固紀錄（2026-07-13，保留以免重複糾結）

一輪「5 視角分析 → 每發現派 skeptic 推翻」確認修掉：簽核 checkbox 四個明確 set＋缺 id 報錯（high）；`target_to_date` 月中按工作日比例折算（med）；0 筆月份回 0 不中斷（med）；stdout 強制 UTF-8 修 Windows cp950（med）；查加班一律附 `month.status`（med）。
被判定**誤報而未改**：日期塞值無反查（改版會以 scrape_failed 浮現）、`need_per_remaining_month` 分子分母不對稱（刻意投影）、`%USERPROFILE%` 文件佔位符、錯誤表未列 `browser_launch_failed`（detail 已帶官方指示）。

## v1 加班單填單設計（uof_form.py，個人擴充功能，2026-07-13/14/16 定案並保留）

> 此節記錄 `scripts/uof_form.py` 的欄位對照、安全設計、送出流程與 recon 事實。此腳本不在 v2 公司共享（唯讀查詢）範圍內，見「範圍」章節的「個人擴充」段。

### 加班單欄位（recon 2026-07-13 確認；2026-07-16 recon 更新 UC8/UC11 控制項）

頁面：`WKF/FormUse/PersonalBox/ApplyFormList.aspx?fillFormDirectly=true&formId=cd8fb94e-a539-4c7e-9762-43e87e653ced`（Homepage 選單「加班單」）。欄位控制項命名模式 `..._VersionFieldCollectionUsingUC1_versionFieldUC<N>_<控制項>`：

| UC | 中文標籤 | 控制項 | 必填 | 本工具處理 |
|---|---|---|---|---|
| 0 | 申請者 | 唯讀文字 | - | 不填（系統帶入）|
| 1 | 表單編號 | 唯讀文字 | - | 不填（系統自動產生）|
| 2 | （工時規則提示文字）| 唯讀 RadEditor | - | 不是欄位，略過 |
| 3 | 類別 | radio 申請/修改/刪除 | ✅ | 固定填「申請」（本工具不支援修改/刪除）|
| 4 | 加班單單號 | select | - | 不填（僅修改/刪除模式需要）|
| 5 | 班別（上班日/休息日/例假日/國定假日/非法定休息日） | radio | - | **不填**——頁面註「表單送出後判斷」，是系統算的 |
| 6 | 開始日期 | RadDatePicker | ✅ | `--date` |
| 7 | 開始時間 | select（15分鐘刻度，需晚於上班刷卡時間） | ✅ | `--start` |
| 8 | 上班刷卡時間 | **文字輸入框**（2026-07-16 recon：`tbxSignleLineText`，非舊版 `lblDisplay` 唯讀 label） | - | 不填（AJAX 選日期後自動回填，程式只等待不填值）|
| 9 | 結束日期 | RadDatePicker | ✅ | `--end-date`（預設同開始日期）|
| 10 | 結束時間 | select（需早於下班刷卡時間） | ✅ | `--end` 或用 `--hours` 換算（對齊15分鐘刻度）|
| 11 | 下班刷卡時間 | **文字輸入框**（同 UC8，2026-07-16 recon 更新） | - | 不填（同上）|
| 12 | 事由 | textarea | ✅ | `--reason` |
| 13 | 工作產出 | textarea | ✅ | `--output` |
| 14 | 異動原因 | textarea | - | 不填（僅修改/刪除必填）|
| 15 | 是否參展 | radio 是/否 | ✅ | `--participate`，預設「否」|
| 16 | 專案負責人 | select（同事姓名+「專案」） | - | `--project-owner`（選填，不給就留「─請選擇─」）|
| 17 | 是否調為補班 | radio 是/否 | - | `--makeup`，預設「否」|

頁面下半部「申請資訊/意見/相關附件/個人附件」屬 WKF 共用流程欄位，非本表單專屬，本工具不碰。

**2026-07-16 版型變更教訓**：UC8/UC11 從 `lblDisplay`（唯讀 `<span>`，讀值用 `inner_text()`）改成 `tbxSignleLineText`（`<input type="text">`，讀值須用 `input_value()`）。`verify_schema()` 因對照表 id 對不上而正確攔下（`form_layout_changed`），而非誤填錯欄位——版型守衛設計如預期運作。修法：`pick_date_via_calendar()` 等值迴圈改為依 `tagName` 動態選 `input_value()`/`inner_text()`。

### 填單安全設計

- **只做 dry-run（Phase A）**：`fill_overtime_dryrun()` 填完欄位後只做 `page.screenshot()`，程式碼裡沒有任何送出/儲存按鈕的 selector 或點擊呼叫——不是「預設關閉」而是物理上不存在該路徑。
- **版型守衛 `verify_schema()`**：填任何欄位前，先確認 UC 對照表裡的每個 id 都存在於頁面上；缺一個就直接 `die(4, "form_layout_changed")` 中止。
- **截圖是唯一驗收依據**：JSON 輸出的 `fields` 陣列只是文字對照，真正判斷「有沒有填對」要看 `screenshot` 路徑的圖——SKILL.md 已寫死「一定要把截圖給用戶看」。
- **時間對不上選項時不硬填**：`select_option` 失敗會落到 `warnings`，不會用最接近的值頂替。
- 截圖與 plan 檔存在 `~/.config/uof/dry_run/`（跟設定檔同層級，在 repo 目錄之外，不會被 git 追蹤到）。

### Phase B 送出安全防線（5 層）

| 層 | 防護 | 繞過條件 |
|---|---|---|
| L1 | CLI flag 隔離：沒有 `--submit` 就物理上不可能送出 | 使用者主動加 flag |
| L2 | Plan + Token：dry-run 必須先跑成功才有 token | 拿到 token |
| L3 | 使用者確認：agent 透過 `<<ASK>>` 按鈕等使用者點「確認送出」 | 使用者點按鈕 |
| L4 | 二次比對：Phase B 重新填表後逐欄位回讀，不一致就中止 | 欄位值一致 |
| L5 | 一次性消耗：token 用過即失效，plan 標 consumed | 重新跑 dry-run |

### 送出按鈕與送出後行為（recon 2026-07-14）

- 送出按鈕：`ctl00_MasterPageRadButton13`（Telerik RadButton，需真實 DOM click 觸發 `autoPostBack`；`$find().click()`/`__doPostBack()` 皆不可靠）。
- Server validation 失敗 → JS `alert()`（`page.on("dialog")` 攔截），常見：「加班開始時間…未到，不可事先填寫加班！」「無上下班刷卡時間，無法填寫加班單！」。
- Server validation 成功 → `hiddenActionMode` 變 `"Send"` → server 開簽核 dialog（`$uof.dialog.open2`，另一個 iframe，非普通 alert）→ 簽核 dialog 內自動帶簽核人 → 確認後主 dialog 自動 `close()`。
- 已確認（2026-07-14 使用者實測）：UOF 加班單**無撤回/抽單機制**（送出即定案）；「專案負責人」非必填；「是否調為補班」系統不覆蓋填入值。

### 不做的事（明確排除）

- ❌ 自動重試（狀態不明 → 停止，由人確認）
- ❌ 修改/刪除既有加班單（本工具只做新申請）
- ❌ 跳過截圖確認直接送出
- ❌ 批次送出多張（一次一張）
- ❌ 請假單填寫、假日加班事先申請單（視需求另做，未排入計畫）
