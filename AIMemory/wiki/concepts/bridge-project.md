---
title: Telegram-Kiro-Bridge 專案
type: concept
created: 2026-06-03
updated: 2026-06-03
sources: [f_4e8237, f_d21a12, f_0b90e2, f_60159c, f_b7206d, f_87759e, f_5a495e]
---

# Telegram-Kiro-Bridge 專案

## 概述

telegram-kiro-bridge 是一個 Telegram Bot ↔ ACP Agent 橋接器，位於 `G:\AI\telegram-kiro-bridge-main`。透過 ACP JSON-RPC over stdio 接上 Kiro CLI / Codex / Claude / Gemini 等 agent，讓使用者在手機上直接跟 AI agent 對話、跑工具、管理長期記憶。專案另含 desktop-pet Electron 桌面寵物功能。

## AIMemory 系統

專案的長期記憶系統位於 `G:\AI\AIMemory`，包含以下子結構：

- **facts** — master fact log + topic shards
- **topics** — 分類規則（`topics.json`）
- **wiki** — 結構化知識庫（concepts / references / lessons / queries）
- **dailylog** — 每日摘要
- **sessions** — 對話紀錄（處理完搬到 oldSessions）

每日凌晨 04:00 由 `/dream` 自動維運（memorytoskill → topicreview → wikisync → factlint → wikilint → skilllint → docupdate → specialistreview → artifactcleanup → backup → restart）。

## 文件與教學

- `docs/usage-guide.html` — 功能教學頁面，深色主題，依重要性分 12 章節附範例
- `/dream` 流程含 `docupdate` 步驟，每日自動比對 README 與 HTML 差異並補上缺少的功能說明

## 部署配置

- `start.bat` 已設定在 Windows 開機時自動啟動（透過 `shell:startup` 資料夾的 bat 檔）
- Bridge process 退出後由 `start.bat` 的 loop 機制自動 3 秒重來

## 品質機制

PARALLEL_DELEGATE 機制已加入 **cross-check** 功能（≥2 specialist 結果時自動注入交叉驗證指引），借鏡自 Claude Code Dynamic Workflows 的 adversarial review 概念。零額外 API call，只在 metaPrompt 尾部加指引文字。

## Wiki 知識庫

wiki 系統門檻為 ≥5 facts 才自動產出 concepts 頁面（由 `/wikisync` 步驟處理）。已產出的頁面：

- [[uk-slot]] — UK 市場老虎機專案群

## 相關

- [[uk-slot]] — 使用者的主要開發產品線
