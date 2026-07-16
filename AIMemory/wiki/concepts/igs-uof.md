---
title: IGS-UOF 加班單自動化
type: concept
created: 2026-07-16
updated: 2026-07-16
sources: [f_8f1b99, f_52d1ec, f_ce6c91, f_c76741, f_16d690]
---

# IGS-UOF 加班單自動化

`igs-uof`（原 `vc-uof-hours`，2026-07-16 改名擴充）是查詢公司內網 UOF（U-Office Force）加班時數/特休、並可 dry-run 預填/送出加班單的 skill，正本位於 `AI-canonical-corp/skills/office/igs-uof`。屬 [[ai-strategy]] 正典語料庫下 office domain 首個入駐 skill。

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

## 相關

- [[ai-strategy]] — AI-canonical-corp office domain 定位
- [[user-pref]] — 使用者對真實外部紀錄自動化的保守策略（dry-run + 截圖 + 手動確認）
