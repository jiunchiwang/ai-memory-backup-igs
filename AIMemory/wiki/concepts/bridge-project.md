---
title: Telegram-Kiro-Bridge 專案
type: concept
created: 2026-06-03
updated: 2026-07-15
sources: [f_946c9d, f_e19357, f_719003, f_e17260, f_36e49d, f_842a1b, f_8da350, f_4e8237, f_d21a12, f_0b90e2, f_60159c, f_b7206d, f_5a495e, f_af99c8, f_a10e66, f_721fa7, f_07d587, f_460731, f_7d747c, f_5b7f6a, f_381c4b, f_e47a60, f_5209cd, f_c228c9, f_71bf67, f_789096, f_5a515c, f_1c58e2, f_937543, f_d0b214, f_651961, f_75d645, f_a6e65d, f_78b50f, f_bd10fc, f_0a8153, f_9b1654, f_b533eb, f_456de2, f_645ea3, f_892166, f_046ffa, f_ae069c, f_493309, f_eb92f6, f_b615b7, f_84107f, f_e6facf, f_1ff1d5, f_bdc742, f_5a2532, f_e62610, f_15ac36, f_510f59, f_2327e5, f_d274c6, f_fedf5c, f_b966f9, f_dc72cc, f_6a3827, f_a4464b, f_054543, f_1dbc98, f_912029, f_152b53, f_ceda58, f_6a6c22, f_e5843d, f_f94c52, f_d61c50, f_493b31, f_1e4cda, f_9c5954, f_b01ccb, f_ace685, f_c965d5, f_a0a929, f_a0d9ac, f_5bb6fa, f_a1d087, f_56f3c9, f_de84a8, f_7cfe9b, f_1867ae, f_0c2487, f_2a93b5, f_50951c, f_dd41a9, f_7d8cb9, f_5871a8, f_69884b, f_36529c, f_3bc9f5, f_32a736, f_3bb538, f_ad29fd, f_02206d, f_bf688a, f_0e5446, f_76b1f7, f_88d3a1]
---

# Telegram-Kiro-Bridge 專案

## 概述

telegram-kiro-bridge 是一個 Telegram Bot ↔ ACP Agent 橋接器，位於 `G:\AI\telegram-kiro-bridge-main`。透過 ACP JSON-RPC over stdio 接上 Kiro CLI / Codex / Claude / Gemini 等 agent，讓使用者在手機上直接跟 AI agent 對話、跑工具、管理長期記憶。專案另含 desktop-pet Electron 桌面寵物功能。

## 子系統索引（已拆分頁）

- [[bridge-memory]] — AIMemory 結構、/dream 維運、factlint 三層防禦、topic 分類、wiki 知識庫、embedding router、備份
- [[bridge-specialist]] — Specialist 分身配置、token 執行權限層、監控 Dashboard、PARALLEL_DELEGATE cross-check
- [[bridge-session]] — Session 歸檔與恢復（archive 蒸餾層、ACP resume、/session 多 session、transcript 路徑）
- [[bridge-acp]] — ACP adapter 切換、model pin、harness hooks。目前走 `claude-agent-acp` + pin `claude-fable-5`（2026-07-06 起）
- [[bridge-streaming]] — Draft API 三階段 lifecycle、4096 截斷、429 限流、Rich Messages
- [[bridge-research]] — 研究方向與外部借鏡、roadmap

## 文件與教學

- `docs/usage-guide.html` — 功能教學頁面，深色主題，24 章節附範例
- `docs/pending-roadmap.html` — 待做方案總覽（深色主題、目錄跳轉），記錄所有未完成 roadmap 項目
- `docs/llm-to-ai-agent-summary.html`、`docs/hermes-vs-bridge.html`、`docs/karpathy-wiki-alignment-roadmap.html` — 學習/比較/roadmap 專頁
- `docs/session-archive-explained.html` — session 歸檔說明

## 部署與 Git

- `start.bat` 開機自動啟動（`shell:startup`），process 退出後 loop 3 秒自動重來
- 多機器部署：本機 G: 磁碟（`MEMORY_DIR=G:\AI\AIMemory`），原開發機 F: 磁碟；`.env` 必須正確設 `MEMORY_DIR`、`BACKUP_REPO_DIR`，否則 /dream 全部失敗
- Git：upstream `redkilin/telegram-kiro-bridge`、fork `jiunchiwang/telegram-kiro-bridge`（origin）
- Fork sync 策略：merge（非 rebase），upstream 架構為主、手動保留 fork 獨有功能。2026-07-09 upstream 已把 fork 功能 port 回上游，之後衝突面大幅縮小
- 同步教訓：`git checkout --theirs/--ours` 是整檔取代，會洗掉對側已乾淨自動合併的 hunk——雙邊都有改動的檔案應用 `git merge-file` 三方合併並逐檔核對
- 兩份 upstream SPEC 為 draft 未實作（acp-hot-swap、moa-provider），與 NotebookLM 修復並列暫緩待辦

## 訊息排版

Telegram 訊息用 HTML parse_mode（`src/format-html.ts`，Markdown → Telegram HTML）。選 HTML 而非 MarkdownV2：agent 輸出常含 `_ * [ ]`，MarkdownV2 跳脫太嚴會大量 400 error；HTML 只需 escape `<>&`。每個 editMessageText 都有 strip-tags fallback。送 `.md` 檔改用 `.txt` 顯示名解決 in-app viewer 中文亂碼。Rich Messages / draft 化細節見 [[bridge-streaming]]。

## Preamble 與 Steering

- **User Profile 結構化注入**（2026-07-02）：`${MEMORY_DIR}/user-profile.md` 獨立存放使用者畫像（5 區塊），preamble 固定注入。獨立成檔是因為畫像是穩定結構化資料，混在 facts 語意召回不保證每次注入
- **Preamble 瘦身**（2026-07-06）：18.6k → ~11.7k chars（facts tail 30→10、7 個 guideline 區塊合併成 `[Agent disciplines]`）。警戒線：佔 context 5-6%；tail 不砍到 5 因為 facts 爆發式寫入會斷跨日連續性
- **Steering 加強**：Context Budget Discipline（事前估算 + 70% 熔斷警告）、ASK Button Discipline（2+ 選項強制 `<<ASK:...>>`）
- **Reply/Quote Context**（2026-07-07，commit 1346519）：讀 reply_to_message 與 partial quote，組 `[Reply context]` 前置於 agent prompt，截 500 字

## 其他功能紀錄

- **Optimistic Cancel**：/cancel 立即清 inflight + 停 streaming + 顯示「⛔ 已取消」，force-kill timeout 60s→15s
- **/skillsearch**：SkillsMP API 搜尋公開 SKILL.md，安裝後自動跑 sync.ps1
- **/intel 情報排程**：ai + game-industry 每日 08:00、topic-ai podcast 隔天 08:00（split 策略避免早晨資訊過載）
- **QUIET_HOURS**：靜默時段排程延遲，目前未啟用；Passive Monitor 改 cron 每日 2 次（12:00、22:00）
- **UI 修復**：/help keyboard parse_mode 改 HTML + escHtml；「返回選單」callback data 改 `help:_back` 避免撞名

## 已知陷阱

- Smoke test 環境隔離：bridge session 內跑 `scripts/check-*.mjs` 會假失敗（繼承空 env 蓋掉 dotenv），跑前 `env -u`（保留 MEMORY_DIR）
- `check-preamble.mjs`：facts 為空時 memory block header 不渲染，fixed core 計算會涵蓋整份 preamble
- `RELAY_DELEGATE` tool note 只在 `config.relay` 開啟且 `relay-peers.json` 存在時注入（目前生產不含）

## Context 壓縮（Headroom 評估）

整合優先級：方案 A（MCP server，零改 code）> 方案 D（headroom learn 獨立跑）> 方案 C（library 整合，最有效但改 core）；方案 B（proxy）排除因 Kiro CLI 不吃 `ANTHROPIC_BASE_URL`。

## 設計原則

Bridge 是中介層不是 harness，不追求與 Claude Code 功能對齊；保持差異化優勢（語意路由 + topic shard + embed-router）。Conversation Summarizer 已由 upstream `archiveSummaryEnabled` 覆蓋，不再獨立追蹤。

## 相關工具

- **GitHubTool**：`G:\AI\GitHubTool`，Streamlit GitHub 組織管理 Web UI，主要操作 IGS-ARCADE-DIVISION-RD2 組織

## 相關

- [[uk-slot]] — 使用者的主要開發產品線
- [[ai-strategy]] — 跨模型策略與正典語料庫
