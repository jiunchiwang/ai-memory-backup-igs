---
title: Telegram-Kiro-Bridge 專案
type: concept
created: 2026-06-03
updated: 2026-06-29
sources: [f_4e8237, f_d21a12, f_0b90e2, f_60159c, f_b7206d, f_5a495e, f_af99c8, f_a10e66, f_721fa7, f_07d587, f_460731, f_7d747c, f_5b7f6a, f_381c4b, f_e47a60, f_5209cd, f_c228c9, f_71bf67, f_789096, f_5a515c, f_1c58e2, f_937543, f_d0b214, f_651961, f_75d645, f_a6e65d, f_78b50f, f_bd10fc, f_0a8153, f_9b1654]
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

每日凌晨 04:00 由 `/dream` 自動維運（memorytoskill → topicreview → wikisync → factlint → wikilint → skilllint → specialistreview → artifactcleanup → backup → restart）。

## 文件與教學

- `docs/usage-guide.html` — 功能教學頁面，深色主題，24 章節附範例（含 Environment Preamble、Event Log、AI.md、RTK Shell、Codegraph、429 防護）
- `docs/llm-to-ai-agent-summary.html` — 「從LLM到AI_Agent.pdf」重點學習整理頁面（深色主題、8 章節、目錄跳轉）
- `docs/hermes-vs-bridge.html` — Hermes AI Agent vs Bridge 功能比較頁面（7 區塊比較表 + 6 張評分卡）
- `docs/karpathy-wiki-alignment-roadmap.html` — Karpathy LLM Wiki × Bridge 改進 Roadmap

## 相關工具

- **GitHubTool**：位於 `G:\AI\GitHubTool`，基於 Streamlit 的 GitHub 組織管理 Web UI（Python 3.10+），主要操作對象為 IGS-ARCADE-DIVISION-RD2 組織（批量建倉、權限、團隊管理）

## 部署配置

- `start.bat` 已設定在 Windows 開機時自動啟動（透過 `shell:startup` 資料夾的 bat 檔）
- Bridge process 退出後由 `start.bat` 的 loop 機制自動 3 秒重來

## 備份機制

- 備份 repo：`G:\AI\ai-memory-backup-igs`
- Remote：`https://github.com/jiunchiwang/ai-memory-backup-igs.git`（branch: master）
- `/backup` 指令：robocopy AIMemory + agent 設定目錄到 repo → git push
- 每日 `/dream` 自動觸發備份步驟

## 訊息排版美化

2026-06-19 實作 Telegram 訊息 HTML 美化功能：
- 新增 `src/format-html.ts`（Markdown → Telegram HTML 轉換）
- 修改 `telegram-ui.ts` 和 `run-prompt.ts`，主 agent 回覆改用 `parse_mode: HTML`
- 支援：粗體、斜體、code block、inline code、blockquote、連結、刪除線
- 每個 `editMessageText` 都有 strip-tags fallback 防 400 error
- 設計文件：`docs/telegram-formatting-plan.md`
- 選 HTML 而非 MarkdownV2：因為 agent 輸出常含 `_ * [ ]` 等字元，MarkdownV2 跳脫規則太嚴格會大量 400 error；HTML 只需 escape `<>&`

未來可升級：Telegram Bot API 10.1（2026-06-11）新增 Rich Messages 支援標題/表格/清單/LaTeX/摺疊區塊/腳註，透過 `sendRichMessage` 使用，最多 32768 字。

## AI 策略與正典語料庫

跨模型 AI 策略 v4 核心原則：**正典語料庫（canonical corpus）本身就是產品**——以 markdown + git 追蹤的精煉知識為唯一真實來源（`G:\AI\AI-canonical`），CLI / MCP / bridge / 索引都只是部署基礎設施而非產品本體。

儲存政策：
- **公開 GitHub repo（AI-canonical）**：正典 skills、steering 政策與通用文件
- **僅本地保留（不進版控）**：session 執行日誌與框架內部狀態

## 品質機制

- PARALLEL_DELEGATE 已加入 **cross-check** 功能（≥2 specialist 結果時自動注入交叉驗證指引），借鏡自 Claude Code Dynamic Workflows 的 adversarial review 概念
- 設計決策：只借鏡 cross-check pattern，不搬動態 delegation plan 和 script 持久化（架構定位不同、規模不需要）

## Specialist 分身系統

`specialist-domains.json` 配置 3 個分身（2026-06-24）：
- **slot-dev**：UK 老虎機開發（claude-sonnet-4，memory MCP）
- **researcher**：深度研究 / AI 策略（claude-sonnet-4，memory + google MCP）
- **general**：完整能力並行多工（inheritsAll，claude-sonnet-4，memory + google MCP）

## Embedding Router

本地 ONNX 模型 `bge-small-zh-v1.5`（23.3 MB），效能 2.6 ms/embed、512 維向量。模型快取在 `node_modules/@xenova/transformers/.cache/`。7 個語意應用：memory recall、skill routing、wiki retrieval、notebook routing、intent classification、sticker auto-select、重複 fact 偵測。

## UI 修復紀錄

- `/help` inline keyboard：parse_mode 從 Markdown 改為 HTML + `escHtml()`（desc/usage 含 `*_<>|${}` 導致 API 400）
- 「返回選單」按鈕：callback data 從 `help:menu` 改為 `help:_back`（原本與 COMMAND_SPECS `name:menu` 撞名被攔截）

## Context 壓縮（Headroom 評估）

研究 Headroom（headroomlabs-ai/headroom）後的整合優先級：
1. **方案 A（MCP server）**：零改 code，agent 自主壓大 tool output
2. **方案 D（headroom learn）**：獨立跑，挖失敗 session 產改進建議
3. **方案 C（library 整合）**：最有效但需改 bridge core
4. ~~方案 B（proxy）~~：排除，因為 Kiro CLI 不吃 `ANTHROPIC_BASE_URL`

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
- [[skill-and-eval]] — skill 評估與管理追蹤


## 近期改善（2026-06-26~28）

### Optimistic Cancel

`/cancel` 後 bridge 立即清 inflight + 停 streaming + 編輯 placeholder 顯示「⛔ 已取消」。使用者無需等 CLI 回應即可送新訊息。Force-kill timeout 從 60s 降為 15s。

### /skillsearch 指令

呼叫 SkillsMP API 搜尋公開 SKILL.md。安裝路徑動態判斷 domain（slot → slot/，其餘 → general/）、cache 10min、fetch 10s timeout、安裝後自動跑 sync.ps1。

### Preamble Steering 加強

- **Context Budget Discipline**：事前估算 + 70% token 事中熔斷警告
- **ASK Button Discipline**：2+ 選項強制使用 `<<ASK:...>>` token

### Dream 配置

dream.json 已建立於 `~/.kiro/dream.json`（13 步），不再依賴 bridge 內建 DEFAULT_STEPS fallback。

### 設計原則

Bridge 是中介層不是 harness，不追求與 Claude Code 功能對齊；保持差異化優勢（語意路由 + topic shard + embed-router）。詳見 [[bridge-research]]。

### Git 架構

- upstream：`redkilin/telegram-kiro-bridge`（remote: upstream）
- fork：`jiunchiwang/telegram-kiro-bridge`（remote: origin）

### QUIET_HOURS 靜默時段

`QUIET_HOURS=HH-HH` 環境變數，靜默期間排程延遲到結束時刻才 fire（支援跨午夜）。目前未啟用，Passive Monitor 改用 cron 精確控制（`0 8,10,12,14,16,18,20,22 * * *`）。
