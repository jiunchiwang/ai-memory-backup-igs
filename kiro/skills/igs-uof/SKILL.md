---
name: igs-uof
description: 操作公司內網 UOF（U-Office Force, http://uof）的查詢入口：加班時數與個人目標進度、剩餘特休、出勤打卡記錄、請假記錄、待簽核表單進度；以及公司通訊錄查詢（某人的分機/部門/Email、某部門或某組有誰、某職級名單、各部門人數）；另含個人擴充的加班單預填（僅 dry-run 產生截圖，二階段確認才送出）。當用戶問「我這個月加班幾小時／特休還剩幾天／我今天幾點打卡／上週有沒有遲到／我請了哪些假／我的單子簽到哪了／有沒有待簽的單」等內網個人差勤問題時觸發（含「加班達標了沒」等口語）；當用戶問「某某人的分機幾號／他在哪個部門／某部門有哪些人／某組名單／公司有幾個人」等通訊錄問題時也觸發；當用戶說「幫我填加班單」時觸發填單流程。差勤查詢需連上公司內網；通訊錄走本地快照，離線可用。帳密與偏好放設定檔（Mac/Windows 皆可）。
---

# igs-uof

登入 UOF 查個人差勤與辦公資訊，用繁體中文回答。公司共享 skill，可分享給 IGS 同事（Mac/Windows 皆支援，安裝見 `SETUP.md`）。**加班單預填是個人擴充功能**（見文末「填加班單」章節），不在公司共享的唯讀查詢範圍內——分享此 skill 給同事前請自行評估是否移除 `scripts/uof_form.py`。

## 執行

用 skill 專屬 venv 的 python 跑 `scripts/uof.py`。**依作業系統選 python 路徑**：

- **Mac / Linux**：`~/.claude/skills/igs-uof/.venv/bin/python`
- **Windows**：`%USERPROFILE%\.claude\skills\igs-uof\.venv\Scripts\python.exe`

```bash
# Mac 範例
~/.claude/skills/igs-uof/.venv/bin/python \
  ~/.claude/skills/igs-uof/scripts/uof.py [子命令...] [flags]
```

**一次可帶多個子命令 = 單次登入依序查**（例：`uof.py todo attendance`）。輸出單一 JSON；解析它回答，別把原始 JSON 丟給用戶。

## 子命令路由（用戶問什麼 → 跑什麼）

| 用戶問什麼 | 命令 |
|---|---|
| 加班時數／目標進度／「幫我看一下加班」 | `hours`（不加 flag = 全查，約 40–50 秒） |
| 只問本月加班 / 今年加班 / 特休 | `hours --overtime-month` / `--overtime-year` / `--annual-leave` |
| 臨時改個人月目標 / 只算已核准 | `hours --target 30` / `hours --approved-only` |
| 出勤狀況／幾點上下班／有沒有異常 | `attendance`（預設本月 1 日～今天） |
| **今天/昨天**幾點打卡（彙總有延遲） | `attendance --punch`（即時刷卡流水） |
| 指定期間出勤 | `attendance --from 2026/06/01 --to 2026/06/30` |
| 請了哪些假／請假記錄 | `leave`（預設今年全年） |
| 某假別 / 指定期間 / 只看簽核中 | `leave --kind 特休假 --leave-from … --leave-to … --status 簽核中` |
| 有沒有待簽的單／待辦 | `todo` |
| 我送的單簽到哪了／進度 | `todo --sent` |
| 某人的分機／部門／Email | `whois --name 名字`（或 `--ext 分機`、`--empno 員編`） |
| 某部門／某組有誰、名單 | `whois --dept 線上研一部`（或 `--team 客服組`、`--rank 組長`、`--title 副理`）※離線 |
| 某部門幾個人、全公司人數分布 | `whois --count-by dept`（可搭 `--dept 線上研` 先縮範圍）※離線 |
| 分機查到的是舊資料／新進同仁查不到 | 同一條命令加 `--online` 重查 |

全域 flags：`--headed`（登入被要求驗證碼時手動過）、`--fresh-login`（session 失效異常時強制重登）、
`--cdp` / `--cdp-endpoint URL`（接管使用者自己開的瀏覽器——被 Cloudflare 人機驗證擋住時的唯一走法，見下節）。

## 通訊錄：離線快照優先

`whois` 預設查**本地快照**，不開瀏覽器、不需內網、不需登入，所以問分機不會像 `hours` 那樣等幾十秒。
快照查不到人時**不會**自動上線（避免無預警啟瀏覽器），而是回 `hint` 建議加 `--online`。

- 快照位置：`~/.config/uof/directory.tsv`（+ 同名 `.meta.json`）。可用 `$UOF_DIRECTORY` 或 config.json 的 `directory_snapshot` 覆蓋。
- **快照不進 git**：含全公司姓名/Email/員編，屬 PII。skill 目錄只放產生它的腳本。
- 重建（人員異動、或第一次安裝）：先在 UOF 分機頁查出全部同仁並把表格複製成 txt，然後
  ```bash
  python scripts/build_directory.py <匯出的.txt>
  ```
  會印出人數/部門數/同名/共用分機摘要；表頭對不上會直接中止（UOF 版型改了才會發生）。
- 只想要純查詢、不經 `uof.py`：`python scripts/directory.py --dept 線上研一部 --count-by team`，參數與 `whois` 相同。

輸出的 `source` 欄分辨資料來源：`offline_snapshot`（本地快照）/ `uof_live`（現爬 UOF）。
`error: directory_unavailable` = 快照還沒建，照 `hint` 跑 `build_directory.py`；此時只用 `--name/--ext/--empno` 的查詢會自動改走線上，不受影響。

## 被人機驗證擋住時（`error: antibot`）

UOF 在**登入成功之後**會跳 Cloudflare Turnstile 驗證頁（`AntiBotCheck.aspx`）。腳本自己開的瀏覽器過不了這關——2026-08-06 實測 Playwright 內建 Chromium 與 `channel=msedge` 的真 Edge 兩臂皆敗（headed 等 241 秒未過）。**分野不在瀏覽器廠牌也不在無痕模式，而在瀏覽器是否由自動化啟動**，所以換瀏覽器、開無痕都沒用。

可行走法是接管使用者自己開的瀏覽器（驗證由真人點擊完成，不做任何指紋偽裝）：

```bash
# 1) 開一個非自動化啟動的瀏覽器（Edge→Chrome 自動找；獨立 profile + CDP port）
python scripts/launch_cdp_browser.py

# 2) 請使用者在那個視窗登入 UOF 並點過「驗證您是人類」，視窗保持開著

# 3) 照常查，加 --cdp
python scripts/uof.py --cdp hours attendance
```

**agent 端流程**：收到 `error: antibot` → 跑 `launch_cdp_browser.py` → 告訴使用者去點驗證並等他回覆 → 重跑原查詢加 `--cdp`。不要自己反覆重試無 `--cdp` 的查詢（必然同樣失敗），也不要去做規避驗證的工程。

**已經在 `--cdp` 卻收到 `antibot`** 是另一回事（clearance 中途被重新挑戰）：**不要**再開一個瀏覽器，只要請使用者在既有視窗重點一次驗證，然後重跑同一條命令。兩種情境的 `hint` 文字不同，**以 `hint` 為準**。

⚠️ `--cdp` 模式的三個性質：
- 腳本**不會**關掉那個瀏覽器（是使用者的視窗，關掉他得重過驗證）；查完視窗仍開著，可連續多次查詢。
- **不寫 session.json**（`storage_state` 會把使用者全部網站的 cookies 落地成明文）。∴ `--headed` / `--fresh-login` 在此模式無作用。
- 一定要用 `launch_cdp_browser.py` 開的獨立 profile；**不要**叫使用者拿日常 profile 加 `--remote-debugging-port` 來接管。

## 如何回答

- **hours**：查加班時數一律附本月目標進度（`overtime.month.status`）：`still_needed`（距本月個人目標還差幾小時）、`remaining_workdays`（本月剩幾個上班日）、`per_workday`（平均每上班日要加幾小時）。加班時數講 `countable`（平日+假日）為主，補班（`makeup`）另外點出。目標進度分析（`overtime.analysis`）用小表格呈現逐月 `countable` vs 個人目標，`gap_ytd` 負=較目標進度落後、正=超前（已按月中工作日比例折算，照字面講）。`workday_calc` 兩判斷：`per_workday_year` 追全年平均、`per_workday_month` 追本月。`workday_source` 是 `estimate` 時提醒是估算。特休講 `remaining_h` 小時與 `remaining_days` 天。
- **attendance**：`days[]` 逐日列刷卡起迄（HHMM）；`type` 非空＝出勤類別異常，當日的加班/請假掛在 `overtime`/`leave` 子物件。⚠️ **彙總資料延遲約 2 天**——用戶問今天/昨天時自動改用 `--punch`，或明講彙總還沒出來。
- **leave**：`records[]` 含假別/起訖/時數/事由/簽核狀態；總時數自己加總 `hours` 欄。已自動翻頁，`total` 即全部筆數。
- **todo**：`counts` 五類件數（待簽-自己/代理、被退回、被知會、被徵詢）；`pending_total`>0 才需要提醒去簽。`--sent` 的 `forms[]` 看 `current_signer` 講「單子現在在誰手上」。
- **whois**：直接報 姓名/部門-組/分機/Email（`title` 是職稱、`rank` 是主管層級，有才講）；`updated_at` 是資料日期，不用每次講。`total` > 1 時**全部列出**別只挑第一筆——公司有 5 組同名同姓（李婉瑜/林子傑/王俊棋/陳嘉宏/陳怡君），用部門幫用戶區辨。分機 3820/3830 是技術服務部客服組的共用分機，多人共用是正常的。`counts` 是聚合結果（用 `--count-by` 時才有），用表格呈現。有 `truncated` 表示名單被截斷，照它說的講清楚共幾筆。
- **params**：`session` 是 `reused`/`new`/`cdp`（登入方式，不用主動講）；hours 的實際採用參數也在這裡，回答以它為準。

## 錯誤處理

**全域錯誤**（整份 JSON 只有 `error` 欄，整體中止）：

| error | 對用戶說 |
|---|---|
| `unreachable` | 連不到 UOF，請確認已連上公司內網 / VPN（⚠️ 先排除 `antibot`——2026-07-30 曾把驗證頁誤讀成內網不可達） |
| `antibot` | 被 Cloudflare 人機驗證擋住。**兩種情境，照 `hint` 走**：(a) 還沒接管（非 `--cdp`）→ 走上節流程，**別重試同一條命令**；(b) 已在 `--cdp` 但視窗被重新挑戰 → 只要請使用者在**既有視窗**再點一次驗證，**然後重跑同一條命令**，不必重開瀏覽器 |
| `cdp_connect_failed` | CDP 連不上（視窗被關了或 port 不對）→ 重跑 `launch_cdp_browser.py` |
| `cdp_port_in_use` | 該 port 已有別的 CDP 瀏覽器 → 照 hint 換 `--port` 或直接接管既有那個 |
| `cdp_no_uof_page` | 接管的瀏覽器裡沒有 UOF 分頁 → 請使用者在該視窗開 UOF 登入頁 |
| `login_failed` / `captcha` | 登入失敗或跳驗證碼；驗證碼用 `--headed` 手動過一次 |
| `no_credential` | 還沒設定帳密：照 `hint` 建立 config.json（見 `SETUP.md`） |
| `bad_config` / `bad_args` | 照 `hint` 修正設定檔或參數 |
| `login_error` | 登入流程非預期異常，看 `detail`；可先加 `--fresh-login` 重試一次 |

**功能級錯誤**（某子命令的結果鍵有 `error` 欄，其他子命令照常）：`scrape_failed`＝該頁版型可能改變或操作逾時（看 `page` 欄），`unexpected_error`＝非預期異常；其餘結果照答，並說明該項暫時查不到。`session_expired`＝查詢中途被踢：**已完成的結果仍在 JSON 裡照答**，缺的告訴用戶重跑一次即可（會自動重登）。**解析 JSON 時逐鍵檢查 `error` 欄。**

⚠️ `antibot` **會出現在兩層**：擋在 session 建立點時是全域錯誤（整份 JSON 只有 `error`）；查詢**中途**被重新挑戰時是功能級錯誤（掛在該子命令鍵、停止後續子命令，語意同 `session_expired`）——此時**已完成子命令的結果仍然有效，照答，不要整批丟掉重查**。

**第一次使用**（venv 或設定檔還沒建）：腳本回 `no_credential` 或 python 執行失敗 → 照 `SETUP.md` 引導安裝，不要自己硬猜。

## 判定基準（hours，可被設定檔 / CLI 覆蓋）

- **計入基準**：預設 `weekday+holiday`（平日+假日計入個人目標，補班不計入但仍顯示）。`countable_basis` / `--basis` 可改。
- **簽核狀態**：預設 同意+簽核中。`status` / `--approved-only` 可改。
- **個人月目標**：預設 20h，`monthly_target` 設定（有人設 20、有人設 30），`--target` 臨時覆蓋。

## 工作日資料（「每上班日要加幾小時」用）

來源優先序：**內建年份（2026 已內建）→ Downloads 內當年度 IGS 行事曆 .xls（檔名含民國年）→ 估算（平日扣七月旅遊假 5 天）**。行事曆靠儲存格底色分類，解析後全量驗證，版型變了自動退回估算。

## 帳密與偏好

- 設定檔（跨 Mac/Windows）：`~/.config/uof/config.json`（Windows：`%USERPROFILE%\.config\uof\config.json`）。優先序：環境變數 `UOF_ACCOUNT`/`UOF_PASSWORD` > 設定檔 > （僅 macOS）Keychain `uof-hr`。
- 設定檔含明文密碼，勿分享、勿進 git；macOS 可改用 Keychain，設定檔只留偏好。
- session 持久化：登入狀態存 `~/.config/uof/session.json`（自動管理，權限 600）；有效期內免登入、不互踢。

## 填加班單（個人擴充，dry-run + 二階段確認送出）

`hours`/`attendance`/`leave`/`todo`/`whois` 五個子命令是唯讀查詢；加班單填寫是另一支獨立腳本 `scripts/uof_form.py`，**不掛在 `uof.py` 的子命令路由下**（避免把寫入操作混進查詢批次），登入/session 仍共用 `uof_client`。

當用戶說「幫我填加班單」時觸發：

### Phase A：Dry-Run（預填 + 截圖 + 產出 plan）

```bash
uof_form.py overtime --date 2026/07/20 --start 18:30 --hours 2 \
  --reason "事由文字" --output "工作產出文字"
```

必填：`--date`（開始日期 YYYY/MM/DD）、`--start`（開始時間 HH:MM，需對齊15分鐘刻度）、`--reason`、`--output`；`--hours` 或 `--end` 擇一給結束時間。`--participate`/`--makeup` 不給則預設「否」。

填單同樣支援 `--cdp` / `--cdp-endpoint`（人機驗證開著時必用；⚠️ 2026-08-06 加入，**填單路徑未經端到端實測**——只驗過共用的 attach/close 邏輯，Phase A/B 本身沒跑過 CDP 模式）。

Phase A 輸出 JSON 含 `plan_file`（下一步 submit 需要）、`token`（一次性）、`screenshot`、`fields`、`warnings`（欄位未成功填入的警告）。

### Phase B：真正送出（需使用者確認後才執行）

```bash
uof_form.py overtime --submit --token <Phase A 的 token>
```

**流程（agent 端）**：
1. 跑 Phase A → 把截圖用 `<<SEND_FILE>>` 傳給使用者
2. 用 `<<ASK:ot_confirm|*submit=確認送出|cancel=取消>>` 問使用者
3. 使用者點「確認送出」後才跑 Phase B
4. 回報結果（成功 / 被拒 / 狀態不明）

**硬規則**：
1. **一定要先跑 Phase A 拿到 token 才能 submit**——沒有 token 就沒有送出路徑。
2. **一定要把截圖給使用者看 + 等使用者確認**——絕對不能拿到 token 就直接 submit。截圖是唯一驗收依據，不用文字描述取代。
3. **失敗不重試**——`submit_rejected`（server 拒絕）或 `submit_status_unknown`（狀態不明）時回報使用者自行處理。
4. 不支援修改/刪除既有加班單；`warnings` 非空要跟使用者說清楚。

Phase B 輸出 `{"mode": "submitted", "status": "success|rejected|unknown", ...}`：

| status | 說明 | 使用者需做什麼 |
|---|---|---|
| `success` | 送出成功 + 簽核流程已啟動 | 無需動作，等主管簽核 |
| `rejected` | server 拒絕（detail 含原因） | 看 detail 修正後重新 dry-run |
| `unknown` | 無法判定（超時/頁面異常） | 到 UOF 個人申請箱確認 |

⚠️ **已知誤判 bug**：`submit_rejected` 有時是腳本把 UOF 的二次確認彈窗（含申請資料摘要的 alert/dialog）誤判為拒絕，實際上第一次 submit 可能已經送出成功。收到 `rejected` 時**先到 UOF 個人申請箱確認是否已送出**，確認未送出才重新 dry-run，避免重複申請。

### 填單專屬錯誤

| error | 對使用者說 |
|---|---|
| `form_layout_changed` | 加班單版型變了，需更新腳本欄位對照（見 DESIGN.md「加班單欄位」章節） |
| `plan_not_found` / `plan_already_consumed` / `token_mismatch` | 重新跑 dry-run 取得新 token |
| `field_mismatch` | 重新填表後欄位值與 plan 不一致，重新 dry-run |
| `plan_version_unsupported` | plan 檔是舊版格式（看 `hint` 的 version）→ 重新跑 dry-run |
| `submit_btn_not_visible` | 送出按鈕不可見，多半版型變了 → 同 `form_layout_changed` 處理 |
| `submit_rejected` / `submit_status_unknown` | 見上表 |

## 注意事項

- ⚠️ session 失效需要重新登入時，會觸發 UOF 重複登入偵測，**可能踢掉你瀏覽器的 UOF 登入**（反之亦然）；session 重用大幅減少但無法完全避免。`--cdp` 模式用的就是你自己那個視窗的登入，不會互踢。
- `hours`/`attendance`/`leave`/`todo`/`whois` 五個子命令**唯讀**（只查詢，不送出任何申請/簽核）；加班單預填是個別獨立腳本的個人擴充功能，見上節。
- 安裝步驟見 `SETUP.md`；各頁面選擇器與 JSON 結構細節見 `DESIGN.md`。
