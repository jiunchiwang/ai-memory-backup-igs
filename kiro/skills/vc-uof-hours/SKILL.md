---
name: vc-uof-hours
description: 查詢公司內網 UOF（U-Office Force, http://uof）的加班時數與剩餘特休，並做加班達標分析；也能預填加班單（僅 dry-run 產生截圖，不會自動送出）。當用戶問「我這個月加班幾小時 / 今年加班多少 / 特休還剩幾天 / 加班進度夠不夠 / 還要加多少班才達標」等出勤加班相關問題時觸發查詢；當用戶說「幫我填加班單」時觸發填單（僅到 dry-run，絕不自動送出）。需連上公司內網；帳密與偏好放設定檔（Mac/Windows 皆可）。
---

# vc-uof-hours

登入 UOF 抓「加班時數 + 剩餘特休」並算加班達標缺口，用繁體中文回答用戶。可分享給同事（Mac/Windows 皆支援）。

## 執行

用 skill 專屬 venv 的 python 跑 `scripts/uof_query.py`。**依作業系統選 python 路徑**：

- **Mac / Linux**：`~/.claude/skills/vc-uof-hours/.venv/bin/python`
- **Windows**：`%USERPROFILE%\.claude\skills\vc-uof-hours\.venv\Scripts\python.exe`

```bash
# Mac 範例
~/.claude/skills/vc-uof-hours/.venv/bin/python \
  ~/.claude/skills/vc-uof-hours/scripts/uof_query.py [flags]
```

依用戶問的內容選 flag（**不加任何 flag = 全查**，約 40–50 秒）：

| 用戶問什麼 | flag |
|---|---|
| 全部 / 加班進度 / 達標 / 缺口 / 「幫我看一下」 | （不加，預設全查）|
| 只問本月加班 | `--overtime-month` |
| 只問今年總加班 | `--overtime-year` |
| 只問特休剩多少 | `--annual-leave` |
| 臨時改月目標 | `--target 30`（覆蓋設定檔）|
| 只算已核准（不含簽核中）| `--approved-only` |
| 加班換驗證碼卡住 | `--headed`（有頭模式手動過驗證碼）|

腳本輸出**單一 JSON** 到 stdout。解析它，別把原始 JSON 丟給用戶。

**第一次使用（venv 或設定檔還沒建）**：腳本會回 `no_credential` 或 python 執行失敗。這時照 `SETUP.md` 引導用戶完成安裝（建 venv、裝套件、建設定檔），不要自己硬猜。

## 判定基準（可被設定檔 / CLI 覆蓋）

- **達標基準**：預設 `weekday+holiday`（只算平日+假日，**補班不計入**，但 `makeup`/`total` 仍顯示）。設定檔 `countable_basis` 或 `--basis` 可改。
- **簽核狀態**：預設 同意+簽核中。設定檔 `status` 或 `--approved-only` 可改。
- **月目標**：預設 20h。設定檔 `monthly_target` 決定（有人設 20、有人設 30），`--target` 臨時覆蓋。
- 實際採用值都會回在 JSON 的 `params`，回答時以它為準。

## 如何回答

- **查加班時數時，一律附上本月達標現況**（`overtime.month.status`，回應用戶要求的三件事）：
  - `still_needed`（本月還差幾小時達標）、`remaining_workdays`（本月還剩幾個上班日）、`per_workday`（平均每個上班日要加幾小時）。
- **加班時數**：講 `countable`（平日+假日）為主，補班（`makeup`）另外點出。
- **當年度換過部門**會讓 `records` >1，但 `year.countable` 已是全部加總，直接用。
- **達標分析**（`overtime.analysis`）用小表格呈現逐月 `countable` vs 目標，並講：
  - `gap_ytd`（負=落後、正=超前）：比較的是 `ytd_countable` vs `target_to_date`。`target_to_date` 已把「進行中的當月」按**已過工作日比例**折算(不是整月),所以月中查詢不會把 on-pace 誤報成落後,可放心照字面講。
  - `workday_calc` 的**兩個判斷**：`per_workday_year`（**追全年平均**）與 `per_workday_month`（**追本月**）。都從隔天 `counted_from` 起算、今天當已過。
  - 若 `workday_calc.workday_source` 是 `estimate` → 附帶 `workday_note` 說明是估算（沒有當年度行事曆），提醒下載行事曆會更準。
- **特休**：講 `remaining_h` 小時與 `remaining_days` 天（=小時/8），附 `period` 給假期間。

## 錯誤處理（JSON 有 `error` 欄時）

| error | 對用戶說 |
|---|---|
| `unreachable` | 連不到 UOF，請確認已連上公司內網 / VPN |
| `login_failed` / `captcha` | 登入失敗或跳驗證碼；驗證碼的話用 `--headed` 手動過一次 |
| `no_credential` | 還沒設定帳密：照 `hint` 的設定檔路徑建立 config.json（範例見 `config.example.json`），詳見 `SETUP.md` |
| `bad_config` | 設定檔 JSON 格式錯誤，照 `hint` 修正 |
| `scrape_failed` | UOF 頁面結構可能變了（看 `page` 欄是哪頁），需更新腳本選擇器 |

## 工作日資料（給「每個上班日要加幾小時」用）

來源優先序：**內建年份（2026 已內建，免檔案）→ Downloads 內當年度 IGS 行事曆 .xls（檔名含民國年）→ 估算（平日扣七月旅遊假 5 天）**。行事曆靠儲存格底色分類（白=上班、粉紅=放假、淺黃=旅遊假），解析後用星期對位全量驗證，版型變了會自動退回估算。

## 帳密與偏好

- 放設定檔（跨 Mac/Windows）：`~/.config/uof/config.json`（Windows：`%USERPROFILE%\.config\uof\config.json`）。優先序：環境變數 `UOF_ACCOUNT`/`UOF_PASSWORD` > 設定檔 > （僅 macOS）Keychain `uof-hr`。
- 設定檔含明文密碼，勿分享、勿進 git；macOS 想更安全可改用 Keychain，設定檔只留偏好。

## 填加班單（P2 dry-run + P3 送出）

用同一支 venv 的 python 跑 `scripts/uof_form.py overtime`：

### Phase A：Dry-Run（預填 + 截圖 + 產出 plan）

```bash
uof_form.py overtime --date 2026/07/20 --start 18:30 --hours 2 \
  --reason "事由文字" --output "工作產出文字"
```

必填參數：`--date`（開始日期 YYYY/MM/DD）、`--start`（開始時間 HH:MM，需對齊15分鐘刻度）、`--reason`（事由）、`--output`（工作產出）；`--hours` 或 `--end` 擇一給結束時間。`--participate`/`--makeup` 不給則預設「否」。

Phase A 輸出 JSON 含：
- `plan_file`：plan 檔路徑（下一步 submit 需要）
- `token`：一次性 token（32 字元 hex）
- `screenshot`：截圖路徑
- `fields`：欄位/值對照
- `warnings`：欄位未成功填入的警告

### Phase B：真正送出（需使用者確認後才執行）

```bash
uof_form.py overtime --submit --token <Phase A 的 token>
```

**流程（agent 端）**：
1. 跑 Phase A → 把截圖用 `<<SEND_FILE>>` 傳給使用者
2. 用 `<<ASK:ot_confirm|*submit=確認送出|cancel=取消>>` 問使用者
3. 使用者點「確認送出」後才跑 Phase B
4. 回報結果（成功 / 被拒 / 狀態不明）

**三條硬規則（Phase B 新增，與原有規則並存）**：

1. **一定要先跑 Phase A 拿到 token 才能 submit** — 沒有 token 就沒有送出路徑。
2. **一定要把截圖給使用者看 + 等使用者確認** — 絕對不能拿到 token 就直接 submit。
3. **失敗不重試** — `submit_rejected`（server 拒絕）或 `submit_status_unknown`（狀態不明）時回報使用者自行處理，不自動再跑一次。

**原有 P2 硬規則仍然有效**：
- 截圖是唯一驗收依據（不要用文字描述取代）
- 不支援修改/刪除既有加班單
- `warnings` 非空要跟使用者說清楚

### Phase B 輸出

```json
{"mode": "submitted", "status": "success|rejected|unknown", ...}
```

| status | 說明 | 使用者需做什麼 |
|---|---|---|
| `success` | 送出成功 + 簽核流程已啟動 | 無需動作，等主管簽核 |
| `rejected` | server 拒絕（detail 含原因） | 看 detail 修正後重新 dry-run |
| `unknown` | 無法判定（超時/頁面異常） | 到 UOF 個人申請箱確認 |

### Phase B 錯誤

| error | 對使用者說 |
|---|---|
| `plan_not_found` | 找不到 plan 檔或 token 不對——重新跑 dry-run |
| `plan_already_consumed` | 這個 token 已經用過了——重新跑 dry-run 取得新 token |
| `token_mismatch` | token 與 plan 紀錄不符——確認複製的 token 正確 |
| `field_mismatch` | 重新填表後欄位值與 plan 不一致——可能表單有變動，重新 dry-run |
| `submit_rejected` | server 拒絕送出（看 detail）——常見：時間未到、無刷卡紀錄 |
| `submit_status_unknown` | 無法確認是否成功——到 UOF 確認，**不要再跑 submit** |

## 注意事項

- ⚠️ 自動登入會觸發 UOF 重複登入偵測，**可能踢掉你當下瀏覽器的 UOF 登入**（反之亦然），屬系統限制。
- 安裝步驟見 `SETUP.md`；資料來源與選擇器細節見 `DESIGN.md`。
