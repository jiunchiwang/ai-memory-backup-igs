---
title: Bridge 改善研究與 Roadmap
type: concept
created: 2026-06-28
updated: 2026-07-09
sources: [f_5a495e, f_af99c8, f_5209cd, f_c228c9, f_9d641c, f_7f1ee1, f_d933fc, f_5bd2fc, f_db1e8b, f_029977, f_50c2e9, f_9b0067, f_f1be4b, f_31228e, f_bdf14b, f_7fcdfa, f_1a894e, f_a0d9ac, f_1a58d7, f_7cfe9b, f_1867ae, f_de84a8]
---

# Bridge 改善研究與 Roadmap

## 概述

記錄 telegram-kiro-bridge 從外部框架/工具研究中借鏡的設計模式、評估決策、以及待實施的改善方案。核心原則：**Bridge 是中介層不是 harness，不追求功能對齊，保持差異化**。

## 外部研究對象

### Claude Code Dynamic Workflows

- 借鏡 **cross-check pattern**（adversarial review）→ 已整合到 PARALLEL_DELEGATE
- 排除動態 delegation plan 和 script 持久化（因為架構定位不同、規模不需要）

### Cowart（zhongerxin/cowart）

- 面向 Codex CLI 的 tldraw 無限畫布插件
- 借鏡點：MCP server 當 bridge + 3 skill 極簡工作流

### Headroom（headroomlabs-ai/headroom）

- 整合優先級：方案 A（MCP server 掛給 agent）> 方案 D > 方案 C
- 排除 proxy wrap（Kiro CLI 不吃 ANTHROPIC_BASE_URL）

### Loop Engineering（cobusgreyling/loop-engineering ⭐2.7k）

- 判斷 bridge 已超越其核心設計（語意路由、Self-improving、跨機 Relay、Local LLM）
- 借鏡操作紀律：L1 先行、顯式 budget、三段式 state、attempt cap
- 已實作：STATE.md 三段式（/dream 結束前 High Priority / Watch List / Noise 覆寫）

### Claude Code Tools（六大子系統）

- 研究報告：`docs/claude-code-tools-research.html`（454 行、8 tab）
- 最大借鏡：Specialist Persistent Memory + [[bridge-project|Pluggable PostTool Hooks]]
- 發現：ClaudeCodeTools v7.0 把固定 5-Phase 改為 native Workflow（因為對照實驗顯示正確性不變但 token 很貴）

### SkillsMP（skillsmp.com）

- 收錄 ~196 萬份公開 SKILL.md，格式與 bridge 完全相容
- 但絕大多數設計給 Claude Code 本地 CLI 環境，bridge 無法直接安裝使用
- 已實作 `/skillsearch` 指令整合 API

## 改善 Roadmap

### Karpathy LLM Wiki 對齊（P0）

1. **Unified Activity Log** — 統一各 log（~100 行）✅ 2026-07-03
2. **Ingest Ripple** — 漣漪式更新 wiki（~200 行）✅ 2026-07-03
3. **Query Auto-save** — 自動存優質回覆為 wiki（~150 行）✅ 2026-07-03

### PostToolUse Hooks（A→B→C→D）

| 階段 | 名稱 | 狀態 |
|------|------|------|
| ✅ A | Tool Usage Log | 已完成 |
| ✅ B | Pluggable PostTool Hooks（~90 行） | 已完成 |
| ✅ B+ | Specialist Persistent Memory（~50 行） | 已完成 |
| ⬜ C | Instinct Observer（~300 行） | 遠期 |
| ⬜ D | Worktree Isolation（~100 行） | 遠期 |

### Loop Engineering 改善

- ⬜ #2 Loop Budget 顯式化（等 Parallel Delegate 大量使用）
- ⬜ #3 漸進 Level 標記（等新增自動化步驟）


### ai_multi_agent（IGS-ARCADE-DIVISION-RD2）

- 來源：`github.com/IGS-ARCADE-DIVISION-RD2/ai_multi_agent` release branch（公司私有）
- 本地路徑：`G:\AI\Study\ai_multi_agent`
- 定位：Python 多 Agent 團隊框架，Telegram Forum Topic 路由，中心化 Daemon + 多獨立 subprocess
- 比較報告：`G:\AI\Study\ai_multi_agent\comparison-report.html`

#### 架構差異

| 維度 | ai_multi_agent | bridge |
|------|---------------|--------|
| 模型 | 中心化 Daemon + 多 Agent process | 單一 Bridge + Specialist subprocess |
| 通訊 | MCP tool → HTTP API（FastAPI :8470） | Text token protocol（<<TOKEN:...>>） |
| UI 隔離 | Forum Topic 天然隔離 | /specialist 手動切換 |
| 回覆 | MCP reply() 一次性送出 | Streaming chunk 即時編輯 |

#### 吸收方案（5 個已評估，3 個已實作）

| # | 方案 | 狀態 | 日期 | 說明 |
|---|------|------|------|------|
| 1 | ACP Protocol Trace | ✅ 已完成 | 2026-06-30 | `src/acp-trace.ts` + acpClient.ts 插入；JSONL 寫到 `${MEMORY_DIR}/acp-trace/` |
| 2 | Reply Dedup | ✅ 已完成 | 2026-06-30 | `src/reply-dedup.ts` + run-prompt.ts 兩個注入點 guard；SHA-256 + 5min window |
| 3 | Runtime Health Monitor | ✅ 已完成 | 2026-06-30 | sessionManager.ts sweepIdle 加 `process.kill(pid, 0)` 探測；AcpProvider 暴露 pid |
| 4 | Session 歸檔/恢復 | ✅ 已完成 | 2026-06-30 | `src/session-archive.ts`（220 行）+ sessionManager create/drop 整合；per-chatId 單檔 JSON + preamble 摘要注入 |
| 5 | Conversation Summarizer（重啟前摘要） | ✅ 已關閉 | 2026-07-03 | upstream `archiveSummaryEnabled` + llama.cpp 真摘要已覆蓋此需求，不再獨立追蹤 |

#### 排除項目（ai_multi_agent 有但 bridge 不需要/已有更好方案）

- Forum Topic 路由 — bridge 是單人使用，/specialist 夠用
- Warm Pool — bridge 單 session 模型，不需要預熱池
- Leader/Worker 角色分層 — bridge 的 specialist 已有 domain 隔離
- ~~Backend 熱切換 — bridge 用 env 切換 + restart，改動頻率低~~ → **排除決策已推翻**：2026-07-07 實作 `/agent` 熱切換 + `/agent init`（acp-providers.json）

#### 增量 gap 報告（comparison-gap-2026-07-07.html）後續

- 權限分層（leader-only gate 等效）→ ✅ 2026-07-08 `src/token-policy.ts`：TOKEN_POLICY 顯式白名單（main/proxy/delegate）+ memory 回寫 provenance/上限（commit 028a5ea）
- 分層權限 preamble（角色模板）→ 評估後不做（僅 cosmetic，specialist preamble 已有 scope 分層）
- Warm Pool（specialist 冷啟動預熱）→ ⬜ 未做，體感延遲優化，遠期

### 侯智薰 AI Agent 7 層 Harness 架構（2026-07-02）

研究侯智薰（雷蒙）對照 Hermes Agent（⭐20 萬）的文章，歸納 7 層：核心規則 / 技能 / 精煉記憶 / 使用者畫像 / 對話歷史 / 生命週期自動化 / 多平台門面。

**結論**：bridge 已覆蓋全部 7 層，且超越部分包括 embedding router、Local LLM、Specialist 分身、跨機 Relay、Self-improving reflexion、Context budget discipline。借鏡成果：觸發 P1 user-profile 獨立化實作。

P2 候選：週度反思迴圈（與 Conversation Summarizer 共享「掃 session」基礎設施但方向不同——反思升級 vs 壓縮上下文）。

### Rich Messages Draft 化（✅ 2026-07-10，commit e3a3a45）

- **背景**：Bot API 10.1（2026-06-11）新增 `sendRichMessageDraft`，grammY 1.44 已 type-safe 支援，官方 `@grammyjs/stream` v1.1.0 封裝 draft lifecycle
- **PoC 結果**（2026-07-08，commit b265a72）：
  - R-1 **失敗**：plugin 是 append-only 累積（yield 出去的字收不回），與 bridge 現有「整 buffer 重跑 transform → 整份 replace」streaming 模型不相容
  - R-2 通過：`replyWithMarkdownStream` 回傳 message_id + 支援 reply_markup，ASK 按鈕可行
- **關鍵發現**（2026-07-10）：PoC R-1 失敗是 plugin 設計，非 API 限制。Raw API `sendRichMessageDraft` 同 `draft_id` 重複呼叫 = **全量替換 + 動畫**，與 rebuild-replace 模型完全相容，不需 hold-back emitter
- **實作（Path A — Raw Draft API + Rebuild-Replace）**：
  - `trySendDraft()` 新增於 `telegram-rich-renderer.ts`（plain/rich 雙模式）
  - `run-prompt.ts` 三處改動：placeholder → draft、editNow → draft、final → sendRichMessage 持久化
  - `TG_DRAFT_ENABLED` env var（預設開）；relay/group/非 private chat 走現有 fallback
  - 24 assertions smoke test（`check-draft-streaming.mjs`）
  - 設計文檔：`SPEC-draft-streaming.md`（BC-1~BC-8）
- **已修小 bug**（commit ce0e1ac）：`tryEditRichMessageDraft` 補 catch，rich edit 失敗收斂回 false 走 plain fallback

### Ruflo（前 Claude Flow，⭐46.6k）

- GitHub 開源多代理編排平台，宣稱把 Claude Code 擴展成多 worker swarm + AgentDB + 成本路由
- **自審報告揭露核心功能是 stub**：agent_spawn 未接線 LLM、hive-mind 單進程 EventEmitter（共識協議為裝飾品）、workflow_execute 回 "not found"、WASM agent 只是 echo；~240 工具只有 ~195 真正運作
- **判斷**：不引入（綁 Claude Code 生態 + 核心 stub），bridge 已有 specialist/relay/trio-llm 覆蓋同類需求
- **可借鏡**（列 watchlist 等 ADR G1-G4 修完再評估）：
  - SONA 自學回饋（confidence threshold 自動拒絕低信心輸出）
  - Batch 工具並行（單次回應 4-6 tool call）
  - Per-task complexity scoring 做成本路由
