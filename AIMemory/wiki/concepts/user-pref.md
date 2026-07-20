---
title: 使用者偏好與決策風格
type: concept
created: 2026-07-15
updated: 2026-07-21
sources: [f_af99c7, f_946c9f, f_e19358, f_be8c07, f_d29dfc, f_c73099, f_218abc, f_0c44ff, f_31febf, f_de7bc7]
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

## 相關

- [[bridge-project]] — Bridge 專案偏好
- [[uk-slot]] — UK slot 專案偏好（PascalCase 等）
