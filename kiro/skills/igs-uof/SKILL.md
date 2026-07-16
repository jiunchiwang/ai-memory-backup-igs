---
name: igs-uof
description: 操作公司內網 UOF（U-Office Force, http://uof）的查詢入口：加班時數與個人目標進度、剩餘特休、出勤打卡記錄、請假記錄、待簽核表單進度、同仁分機查詢；另含個人擴充的加班單預填（僅 dry-run 產生截圖，二階段確認才送出）。當用戶問「我這個月加班幾小時／特休還剩幾天／我今天幾點打卡／上週有沒有遲到／我請了哪些假／我的單子簽到哪了／有沒有待簽的單／某某人的分機」等內網個人差勤與辦公資訊問題時觸發（含「加班達標了沒」等口語）；當用戶說「幫我填加班單」時觸發填單流程。需連上公司內網；帳密與偏好放設定檔（Mac/Windows 皆可）。
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

全域 flags：`--headed`（登入被要求驗證碼時手動過）、`--fresh-login`（session 失效異常時強制重登）。

## 如何回答

- **hours**：查加班時數一律附本月目標進度（`overtime.month.status`）：`still_needed`（距本月個人目標還差幾小時）、`remaining_workdays`（本月剩幾個上班日）、`per_workday`（平均每上班日要加幾小時）。加班時數講 `countable`（平日+假日）為主，補班（`makeup`）另外點出。目標進度分析（`overtime.analysis`）用小表格呈現逐月 `countable` vs 個人目標，`gap_ytd` 負=較目標進度落後、正=超前（已按月中工作日比例折算，照字面講）。`workday_calc` 兩判斷：`per_workday_year` 追全年平均、`per_workday_month` 追本月。`workday_source` 是 `estimate` 時提醒是估算。特休講 `remaining_h` 小時與 `remaining_days` 天。
- **attendance**：`days[]` 逐日列刷卡起迄（HHMM）；`type` 非空＝出勤類別異常，當日的加班/請假掛在 `overtime`/`leave` 子物件。⚠️ **彙總資料延遲約 2 天**——用戶問今天/昨天時自動改用 `--punch`，或明講彙總還沒出來。
- **leave**：`records[]` 含假別/起訖/時數/事由/簽核狀態；總時數自己加總 `hours` 欄。已自動翻頁，`total` 即全部筆數。
- **todo**：`counts` 五類件數（待簽-自己/代理、被退回、被知會、被徵詢）；`pending_total`>0 才需要提醒去簽。`--sent` 的 `forms[]` 看 `current_signer` 講「單子現在在誰手上」。
- **whois**：直接報 姓名/部門-組/分機/Email；`updated_at` 是通訊錄快照時間，不用每次講。
- **params**：`session` 是 `reused`/`new`（登入方式，不用主動講）；hours 的實際採用參數也在這裡，回答以它為準。

## 錯誤處理

**全域錯誤**（整份 JSON 只有 `error` 欄，整體中止）：

| error | 對用戶說 |
|---|---|
| `unreachable` | 連不到 UOF，請確認已連上公司內網 / VPN |
| `login_failed` / `captcha` | 登入失敗或跳驗證碼；驗證碼用 `--headed` 手動過一次 |
| `no_credential` | 還沒設定帳密：照 `hint` 建立 config.json（見 `SETUP.md`） |
| `bad_config` / `bad_args` | 照 `hint` 修正設定檔或參數 |
| `login_error` | 登入流程非預期異常，看 `detail`；可先加 `--fresh-login` 重試一次 |

**功能級錯誤**（某子命令的結果鍵有 `error` 欄，其他子命令照常）：`scrape_failed`＝該頁版型可能改變或操作逾時（看 `page` 欄），`unexpected_error`＝非預期異常；其餘結果照答，並說明該項暫時查不到。`session_expired`＝查詢中途被踢：**已完成的結果仍在 JSON 裡照答**，缺的告訴用戶重跑一次即可（會自動重登）。**解析 JSON 時逐鍵檢查 `error` 欄。**

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

### 填單專屬錯誤

| error | 對使用者說 |
|---|---|
| `form_layout_changed` | 加班單版型變了，需更新腳本欄位對照（見 DESIGN.md「加班單欄位」章節） |
| `plan_not_found` / `plan_already_consumed` / `token_mismatch` | 重新跑 dry-run 取得新 token |
| `field_mismatch` | 重新填表後欄位值與 plan 不一致，重新 dry-run |
| `submit_rejected` / `submit_status_unknown` | 見上表 |

## 注意事項

- ⚠️ session 失效需要重新登入時，會觸發 UOF 重複登入偵測，**可能踢掉你瀏覽器的 UOF 登入**（反之亦然）；session 重用大幅減少但無法完全避免。
- `hours`/`attendance`/`leave`/`todo`/`whois` 五個子命令**唯讀**（只查詢，不送出任何申請/簽核）；加班單預填是個別獨立腳本的個人擴充功能，見上節。
- 安裝步驟見 `SETUP.md`；各頁面選擇器與 JSON 結構細節見 `DESIGN.md`。
