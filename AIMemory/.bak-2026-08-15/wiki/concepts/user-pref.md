---
title: 使用者偏好與決策風格
type: concept
created: 2026-07-15
updated: 2026-08-01
sources: [f_be8c07, f_d29dfc, f_c73099, f_0c44ff, f_31febf, f_de7bc7, f_4e6745, f_70542c, f_8a4a0e, f_e0ce0f, f_a738db, f_99e9ba, f_ebe025, f_9d9c71]
---

# 使用者偏好與決策風格

本頁彙整跨專案通用的使用者偏好——agent 每次 session 都應遵循。專案特定偏好見各專案 wiki 頁。

## 溝通互動

- **ASK 按鈕優先**：回覆含選項時用 `<<ASK:...>>` button，減少手機打字
- **重要決策先列選項再問**，不要代替決定

## Git 紀律

- **Commit 訊息使用中文**
- **Commit 前先確認**：多問幾個釐清問題並取得同意，不逕自 commit
- 同一 session 不相關的改動**拆成多個小顆粒 commit**

## 文件產出

- HTML 文件要有**目錄錨點跳轉**（點擊跳段落 + 回目錄連結）

## 自動化保守策略

- 會產生真實外部紀錄的自動化（如公司系統表單送出）：**只做到 dry-run + 截圖**
- 手動確認後才送出，不做一鍵全自動
- 這是刻意設計，避免誤觸發產生公司內部真實紀錄

## 除錯對策

- 對帳/檢查類函式遇格式不符應「**回報不 crash**」（守衛 + error log）
- 反對用關掉檢查或 clamp 掩蓋——不用記得開回來、production 遇壞資料也不炸

## Session 管理

- 日常用 `/reset`（快速清 context 重開）
- `/handoff` 保留給較大任務完成 / 換機器 / 當天收工等需要記憶留存的場景

## Skill 管理

- Underused skills 處理策略（2026-07-10 決策，**已於隔天撤回**）：原決定刪除 skill-creator / knowhow-accumulation / non-engineer-agent-design，但 2026-07-11 使用者否決了 dream 的 zombie 清理提案，改為保留三者（`skill-usage.json` 對應 entry notes 記載此撤回）；huashu-slides / dual-skill-review-loop / self-eval-prompt-pattern 仍持續觀察中
- 對非 Claude model 的判斷：DeepSeek 3.2 是非 Claude 裡 coding 最強穩定選項，qwen3-coder-next 超便宜但 experimental 穩定度未知
- 把「多視角分析 + 每個發現派 skeptic 對抗驗證」的 review 流程做成固定 skill，加入日後的 skill 開發流程，會對既有 skill 原始碼重跑此流程來優化

## 誤進版控處理慣例

對已誤進版控的診斷資料（如 `ai-memory-backup-igs` 裡的 `acp-trace`）：只做 `git rm --cached` 移除追蹤 + 加 `.gitignore` 防再犯，不做 `git filter-repo` 歷史清除、不 force-push，接受舊 commit 歷史仍保留內容。

## 驗證與診斷的偏好（2026-07-31 新增）

- **要「可否證條件」而不是「已修好」的宣稱**：承重改動上線時要同時定義出**什麼觀測結果代表原假設是錯的**。實例：draft H1 修法的判讀表把「`status-restore` 幀存在但症狀仍在」明確標成「假設錯、需換方向」，而不是只列成功條件。
- **重建撞牆時選「改看真實資料」而不是再猜一輪**：raw API 八臂探針全負後，選擇加內容快照 + 等症狀自然發生再 diff 出事的前後兩幀；明確排除「先停等下次重播再處理」與「順便把強制補送拿掉」兩個選項。
- **記憶去留的判準**：含技術實作細節（selector、防線設計、API 行為）的進度記錄值得保留；純日期綁定的進度快照與歷史拆分記錄可刪。詳見 [[bridge-memory]]。

## 相關

- [[bridge-project]] — Bridge 專案偏好
- [[uk-slot]] — UK slot 專案偏好（PascalCase 等）
