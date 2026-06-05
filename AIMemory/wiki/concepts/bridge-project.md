---
title: Telegram-Kiro-Bridge 專案
type: concept
created: 2026-06-03
updated: 2026-06-06
sources: [f_4e8237, f_d21a12, f_0b90e2, f_60159c, f_b7206d, f_5a495e, f_af99c8, f_a10e66, f_721fa7]
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

## 備份機制

- 備份 repo：`G:\AI\ai-memory-backup-igs`
- Remote：`https://github.com/jiunchiwang/ai-memory-backup-igs.git`（branch: master）
- `/backup` 指令：robocopy AIMemory + agent 設定目錄到 repo → git push
- 每日 `/dream` 自動觸發備份步驟

## 品質機制

- PARALLEL_DELEGATE 已加入 **cross-check** 功能（≥2 specialist 結果時自動注入交叉驗證指引），借鏡自 Claude Code Dynamic Workflows 的 adversarial review 概念
- 設計決策：只借鏡 cross-check pattern，不搬動態 delegation plan 和 script 持久化（架構定位不同、規模不需要）

## Topic 分類系統

`topics.json` 定義 keyword-based first-match-wins 分類規則，bridge 每 2 秒重讀。目前 6 個 topic，misc 保持 0 條。

## Wiki 知識庫

wiki 系統門檻為 ≥5 facts 才自動產出 concepts 頁面（由 `/wikisync` 步驟處理）。

## 多機器部署

- 此專案已在第二台機器部署（G: 磁碟，`MEMORY_DIR=G:\AI\AIMemory`）
- 原開發機使用 F: 磁碟（`F:\AI\AIMemory`）
- `.env` 必須正確設定 `MEMORY_DIR`、`BACKUP_REPO_DIR`，否則 `/dream` 維運全部失敗

## 相關

- [[uk-slot]] — 使用者的主要開發產品線
