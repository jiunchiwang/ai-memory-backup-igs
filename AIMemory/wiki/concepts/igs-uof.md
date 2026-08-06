---
title: IGS-UOF 加班單自動化
type: concept
created: 2026-07-16
updated: 2026-08-06（新增 CDP 接管模式突破 Cloudflare 反機器人驗證）
sources: [f_8f1b99, f_52d1ec, f_ce6c91, f_c76741, f_16d690, f_02e1bb, f_6420f5, f_cf4a82, f_9b3d71, f_e8c5f0, f_a2d693, f_d5b5eb, f_303689]
---

# IGS-UOF 加班單自動化

`igs-uof`（原 `vc-uof-hours`，2026-07-16 改名擴充）是查詢公司內網 UOF（U-Office Force）加班時數/特休、並可 dry-run 預填/送出加班單的 skill，正本位於 `AI-canonical-corp/skills/office/igs-uof`。屬 [[ai-strategy]] 正典語料庫下 office domain 首個入駐 skill。改名擴充時合併了同事版新增的 `attendance`/`leave`/`todo`/`whois` 唯讀查詢子命令，並新增 `uof_client.py` 共用登入/session 持久化，取代原本各自登入的 `uof_query.py`（commit `c20f6d5`）。

## 定位與範圍

- **查詢功能（唯讀）**：加班時數、特休、出勤打卡、請假記錄、待簽核表單——公司共享範圍，帳密設定檔 `~/.config/uof/config.json`，月目標 24 小時
- **填單功能**（`uof_form.py`）：標註為「個人擴充，非公司共享唯讀範圍」——同事的 v2 設計原本已排除寫入操作；若要整包分享同事需重新評估是否移除該檔案

## 加班單送出流程（P3，2026-07-14 實作完成）

- 送出按鈕：frame 2 的 `ctl00_MasterPageRadButton13`（Telerik RadButton, autoPostBack）
- 送出後行為：postback → 簽核 dialog（`$uof.dialog.open2`, 850x500）→ dialog close
- 儲存草稿按鈕：`MasterPageRadButton1`
- 驗證策略：dialog close + 草稿列表少一筆
- **五層安全防線**：CLI flag / plan+token / 使用者確認 / 欄位比對 / consumed 防重複（`--submit --token` 模式，Phase A 產出 `plan.json` + 一次性 token）
- 簽核 dialog 因環境限制（無刷卡紀錄）未能實測，`handle_sign_dialog` 用啟發式偵測；首次真正送出時需觀察行為做微調

## 已知踩坑

⚠️ **刷卡時間欄位不會自動回填**：直接用 JS/`frame.fill` 填日期欄不會觸發 `onchange` 事件，導致刷卡時間欄空白。正確做法是點日曆按鈕選日期（觸發 AJAX 查刷卡）→ 等刷卡時間出現 → 再填其他欄位；`fill` 塞值當保底 fallback，防日曆 DOM selector 猜錯時整個腳本失敗。

⚠️ **二次確認彈窗誤判為送出失敗**（2026-07-17）：`uof_form.py` 的 submit 流程會把 UOF 的二次確認彈窗（含申請資料摘要的 alert/dialog）誤判為 `submit_rejected`——實際上第一次 headless submit 就已經成功送出（實測案例 BAE260706086 於 09:27 申請成功，腳本卻回報失敗）。腳本需修正確認彈窗處理邏輯，目前尚未修復。

## Cloudflare 反機器人驗證與 CDP 接管（2026-07-30 → 2026-08-06 已破解）

公司內網 UOF（`http://uof` → `https://hq.igs.com.tw/UOF/`）於 2026-07-30 前後新增 Cloudflare 反機器人驗證（`AntiBotCheck.aspx` + Turnstile，登入成功後才跳）。**2026-08-06 已找到可行的接管路徑，查詢功能恢復可用**——以下記錄從全數失效到破解的完整過程。

### Turnstile 判的是什麼（三臂實測，2026-08-06）

Turnstile 認的**不是** cookie、無痕、或瀏覽紀錄，而是「這個瀏覽器是不是自動化啟動的」：

| 臂 | 做法 | 結果 |
|---|---|---|
| 1 | Playwright 內建 Chromium（headless/headed 皆試） | ❌ 停在 AntiBotCheck |
| 2 | Playwright `channel=msedge` 真 Edge headed | ❌ 等 241s 未過 |
| 3 | 使用者自己用 `Start-Process msedge --remote-debugging-port=9222 --user-data-dir=<乾淨profile>` 開的 Edge，登入+點驗證後，`playwright connect_over_cdp("http://127.0.0.1:9222")` 接管既有 page | ✅ |

分野純粹在瀏覽器是否由自動化啟動，不需要任何 stealth 參數或指紋偽裝。過驗證前刻意不用 CDP 碰該頁（避免留下自動化痕跡影響過驗證判定）。

### CDP 接管模式已進 skill（commit `fce516d`，AI-canonical-corp）

- `scripts/launch_cdp_browser.py`：開瀏覽器（獨立 profile + CDP port，Edge→Chrome 依平台找路徑）
- 使用者在該視窗登入 + 點過驗證，視窗保持開著
- `uof.py --cdp <子命令>` / `uof_form.py --cdp`：接管該視窗執行查詢/填單
- 被 Turnstile 擋住時現在回明確的 `error=antibot`（不再誤報 `unreachable`/`scrape_failed`）

**antibot 的處置依模式相反，agent 必須照 hint 走，不可套同一句話**：
- 非 CDP 模式：**別重試同一條命令**（重試必敗，見上面三臂實驗）
- 已在 CDP 卻中途被重新挑戰：**在既有視窗重新點過驗證後重跑同一條命令**，不要重開瀏覽器

**CDP 模式刻意不落地 `session.json`**：`storage_state` 會把使用者當時瀏覽器裡**全部網站**的 cookies 存成明文——實測連新開的「乾淨」profile 都混進 `.msn.com`/`.bing.com`（Edge 開機頁塞的），且 Windows 上 `chmod 600` 是 no-op 沒有實際權限保護。

**尚未端到端實測**：填單（`uof_form.py`）的 CDP 路徑。查詢路徑已驗證可用。

### 診斷注意事項（歷史踩坑，仍有效）

- `uof_client.py` 的 `_is_net_error()` 把 Playwright Timeout 也歸類為網路錯誤——**不可信任其 unreachable 錯誤訊息**，先確認是否被 AntiBotCheck 擋住（此問題在 antibot 偵測補上後已緩解，但邏輯本身的陷阱仍值得記住）

### 手動查詢路徑（CDP 模式前的備援，仍可用）

加班時數：差勤 → 加班統計查詢（`Project/BAE/Stats_Search.aspx`），設日期區間並勾選簽核狀態「同意」+「簽核中」，看底部平日／假日合計。

### 其他調整

- `uof_client.py` 登入與首頁導航 timeout 已從 20s 改為 60s（UOF 首頁在 headless 下實測需約 22 秒才到 DOMContentLoaded）

## 相關

- [[ai-strategy]] — AI-canonical-corp office domain 定位
- [[user-pref]] — 使用者對真實外部紀錄自動化的保守策略（dry-run + 截圖 + 手動確認）
