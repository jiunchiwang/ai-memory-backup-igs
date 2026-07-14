---
title: 使用者偏好與決策風格
type: concept
created: 2026-07-15
updated: 2026-07-15
sources: [f_af99c7, f_946c9f, f_e19358, f_be8c07, f_d29dfc, f_f95ab5, f_c73099, f_218abc]
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

- Underused skills 處理策略（2026-07-10 決策）：刪除 skill-creator / knowhow-accumulation / non-engineer-agent-design，保留 huashu-slides / dual-skill-review-loop / self-eval-prompt-pattern 繼續觀察

## 相關

- [[bridge-project]] — Bridge 專案偏好
- [[uk-slot]] — UK slot 專案偏好（PascalCase 等）
