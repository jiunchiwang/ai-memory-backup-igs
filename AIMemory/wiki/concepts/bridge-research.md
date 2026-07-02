---
title: Bridge 改善研究與 Roadmap
type: concept
created: 2026-06-28
updated: 2026-07-03
sources: [f_5a495e, f_af99c8, f_5209cd, f_c228c9, f_9d641c, f_7f1ee1, f_d933fc, f_5bd2fc, f_db1e8b, f_029977, f_50c2e9, f_9b0067, f_f1be4b, f_31228e, f_bdf14b, f_7fcdfa, f_1a894e]
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

1. **Unified Activity Log** — 統一各 log（~100 行）
2. **Ingest Ripple** — 漣漪式更新 wiki（~200 行）
3. **Query Auto-save** — 自動存優質回覆為 wiki（~150 行）

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
| 5 | Conversation Summarizer（重啟前摘要） | ⬜ P2 | — | close 前用 local LLM 跑摘要存到 working state |

#### 排除項目（ai_multi_agent 有但 bridge 不需要/已有更好方案）

- Forum Topic 路由 — bridge 是單人使用，/specialist 夠用
- Warm Pool — bridge 單 session 模型，不需要預熱池
- Leader/Worker 角色分層 — bridge 的 specialist 已有 domain 隔離
- Backend 熱切換 — bridge 用 env 切換 + restart，改動頻率低

### 侯智薰 AI Agent 7 層 Harness 架構（2026-07-02）

研究侯智薰（雷蒙）對照 Hermes Agent（⭐20 萬）的文章，歸納 7 層：核心規則 / 技能 / 精煉記憶 / 使用者畫像 / 對話歷史 / 生命週期自動化 / 多平台門面。

**結論**：bridge 已覆蓋全部 7 層，且超越部分包括 embedding router、Local LLM、Specialist 分身、跨機 Relay、Self-improving reflexion、Context budget discipline。借鏡成果：觸發 P1 user-profile 獨立化實作。

P2 候選：週度反思迴圈（與 Conversation Summarizer 共享「掃 session」基礎設施但方向不同——反思升級 vs 壓縮上下文）。
