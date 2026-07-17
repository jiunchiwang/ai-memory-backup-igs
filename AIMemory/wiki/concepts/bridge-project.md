---
title: Telegram-Kiro-Bridge 專案
type: concept
created: 2026-06-03
updated: 2026-07-17
sources: [f_946c9d, f_e19357, f_719003, f_e17260, f_36e49d, f_842a1b, f_8da350, f_4e8237, f_d21a12, f_0b90e2, f_60159c, f_b7206d, f_5a495e, f_af99c8, f_a10e66, f_721fa7, f_07d587, f_460731, f_7d747c, f_5b7f6a, f_381c4b, f_e47a60, f_5209cd, f_c228c9, f_71bf67, f_789096, f_5a515c, f_1c58e2, f_937543, f_d0b214, f_651961, f_75d645, f_a6e65d, f_78b50f, f_bd10fc, f_0a8153, f_9b1654, f_b533eb, f_456de2, f_645ea3, f_892166, f_046ffa, f_ae069c, f_493309, f_eb92f6, f_b615b7, f_84107f, f_e6facf, f_1ff1d5, f_bdc742, f_5a2532, f_e62610, f_15ac36, f_510f59, f_2327e5, f_d274c6, f_fedf5c, f_b966f9, f_dc72cc, f_6a3827, f_a4464b, f_054543, f_1dbc98, f_912029, f_152b53, f_ceda58, f_6a6c22, f_e5843d, f_f94c52, f_d61c50, f_493b31, f_1e4cda, f_9c5954, f_b01ccb, f_ace685, f_c965d5, f_a0a929, f_5bb6fa, f_a1d087, f_56f3c9, f_de84a8, f_7cfe9b, f_1867ae, f_0c2487, f_2a93b5, f_50951c, f_dd41a9, f_7d8cb9, f_5871a8, f_69884b, f_36529c, f_3bc9f5, f_32a736, f_3bb538, f_ad29fd, f_02206d, f_bf688a, f_0e5446, f_76b1f7, f_88d3a1, f_5bd2fc, f_0561d8, f_130b5d, f_b1b0f4, f_166fd1, f_5bf5da, f_eb9ddd, f_131cef, f_f44d46, f_b1e2ca, f_484853, f_cc8fd5, f_f144ad, f_28e17b, f_f16f7b, f_d6b17c, f_9f9b1f, f_87901e, f_3f826e, f_b21c3a, f_7d5145, f_51bc41, f_90a25d, f_a23d83, f_4c12ce, f_651a0d, f_e72b07, f_ea9657, f_d878ad, f_e1f99f, f_9b9689, f_e2d60b, f_e547d2, f_6e3e02, f_e7bcdd, f_1b2fd1, f_6de90c]
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

## Process 管理

- `start.bat`：loop 用 `npm run dev`（tsx 直跑 src），RESTART 即帶最新 code 生效
- `start-psmux.ps1`：psmux（Windows 原生 tmux）替代方案，與 start.bat 並存。決策：psmux 不導入 bridge code，只當外層容器（排除依賴 psmux 因為增加耦合無對等收益）
- 架構陷阱：`index.ts` 的 `unhandledRejection` handler 會 `process.exit(1)`，新增 server/handler 必須自帶錯誤邊界

## SELF_EVAL 量化自評

- 2026-07-14 實作完成：balanced-scanner 抽取、token-policy 白名單（main 允許、proxy/delegate 不允許）
- 持久化：`selfEvalStore.ts`（低分閾值 60、全域上限 200 筆）
- 對抗性審查發現六個共通致命缺陷（型別驗證可被謊報繞過、觸發條件與 backend 限制矛盾、未驗證前提等）

## Upstream 同步紀錄與原則

- **2026-07-15**：merge 19 個 upstream commit（Rich Telegram replies 統一、MoA rich replies、psmux 開發啟動器規劃、背景通知修復等）+ 1 個本地 ctx 統計後綴 commit，push `691e7f8..0a3c551`；`status.ts` 的 Electron 桌面監控視窗路線衝突採用 upstream 版（推翻先前移除 Electron 改純 Bot 推送的決定）
- **2026-07-16**：merge MCP-first action domain 基礎建設（`agent-actions.ts`/`agent-action-runtime.ts`/`agent-action-metrics.ts`/`mcp-actions.ts`）+ skill sync hook 改為 opt-in（`postinstall` 不再自動設定 `core.hooksPath`）+ legacy action id 消毒修規，`main` 從 `0a3c551` 更新到 `199e30a`
- **衝突處理原則（實證，2026-07-15/16 累計兩種模式）**：
  - 假衝突（共同祖先烘焙了 conflict markers）→ 採清理較完整的一方，不機械套用固定優先權
  - 真衝突（功能路線分歧，如 Electron 開關）→ 停下問使用者決定
  - 結構性衝突（本地已把細節搬到子文件如 `src/AI.md`/`docs/setup-agents.md` vs upstream 就地擴充原檔）→ 保留本地 pointer 結構，把 upstream 新增內容手動補進對應子文件，而非整段改用 upstream 版本

## bridge-actions MCP（2026-07-16）

`bridge-actions` MCP server 提供 6 個 action 工具：`ask`/`schedule`/`delegate`/`parallel_delegate`/`send_file`/`relay_file`，取代舊的裸文字 token 協定（`<<ASK:...>>` 等仍保留作 fallback）。同步進來時功能旗標雖預設開但未接線（`dist/mcp-actions.js` 未 build、agent config 未註冊）；經確認後執行 `npm run build` + `node scripts/setup-mcp.mjs`，已寫入 `~/.claude/settings.json`、`~/.claude.json`、`~/.kiro/agents/main.json`、`~/.codex/config.toml`。⚠️ MCP server 於 session 建立時 spawn，不可熱插拔，需重啟受影響 session 才會生效。README.md 與 `docs/usage-guide.html`（2026-07-17 補上 6 個 action tool 的說明章節）皆已同步補上說明。

跨專案文件同步慣例：AI-canonical 正本三份 skill（`ms-agent-scheduled-prompts`、`ms-agent-text-token-signaling`、`ms-telegram-ask-button-protocol`）已同步更新為 MCP-first 邊界說明——bridge-managed session 優先呼叫 `bridge-actions` MCP tool，只有明確回報 unavailable 才退回文字 token；validation/policy 錯誤須修參數，不可用 token 繞過（commit d6853e2，未 push；詳見 [[ai-strategy]]）。

## claude-mem-curate → /dream 第 14 步（2026-07-16）

原本只能手動觸發或 agent 主動提醒，新增 `handleClaudeMemCurate` handler（`src/commands/dream.ts`，仿 `handleDocUpdate` 的 meta-prompt 模式）並註冊進 `COMMAND_HANDLERS`，`dream.json` 插入 `claudememcurate` 步驟（`memorytoskill` 之後、`topicreview` 之前），使精選流程從純手動變成每日 04:00 自動執行。⚠️ `dream.json` 每步 `cmd` 字串必須存在於 `COMMAND_HANDLERS` map 中才會被執行，否則判定「未知指令已跳過」但不中斷其餘步驟（`continue_on_error` 預設 true）。

## /goal ASK-aware 修復

- 原問題：continuation 排程 500ms 後無條件推進，不看該輪有無 `<<ASK:...>>`，使用者問題形同虛設
- 修復：新增 `GOAL_ASK_WAIT_MS=10分鐘` + `turnHadAsk` 旗標（commit 8e52c2e）

## /backup acp-trace 洩漏修復

- AIMemory job `excludeDirs` 原只排除 transcripts/shared，未排除 acp-trace（含完整對話內容）
- 2026-07-09 起至少 5 次 /backup 自動 push 把診斷檔帶進 ai-memory-backup-igs
- 修正：excludeDirs 加入 acp-trace（commit 691e7f8）；歷史不做 force-push 清除

## Turn-Lint 回覆格式機械檢查（2026-07-17）

反覆出現「回覆結尾用英文」「問句漏附 ASK 按鈕」兩類違規（4+ session 累犯），委派 Claude Fable 5 做獨立診斷後確認根因：**違規集中在回覆最後追加的「下一步提議句」**——任務主體完成後才補的收尾句，不會走生成主體內容時的規則檢查路徑，純靠自律漏看率 50-67%，只有 model-independent 的機械層才能治本。

依診斷結果新增 `src/turn-lint.ts`：純函式 `lintTurnReply(body, askCount)` 檢查回覆最後一行——① 問句 pattern（嗎/呢/要不要/?/？）但沒有 ASK ② 全文有中文但尾行像純英文；掛在 `run-prompt.ts` 約 1136 行（`asks`/`body` 都底定之後、實際發送前）。

設計取捨：只 `console.warn`，不擋訊息、不改文字（定位同 SELF_EVAL，是 observability 而非攔截器）。因為判斷規則是啟發式正則，容易對 code block、反問句等正常內容產生 false positive，若直接攔截或強制改寫可能誤傷本來正常的回覆，所以排除 blocking/auto-rewrite 方案。

## 已知陷阱

- Smoke test 環境隔離：bridge session 內跑 `scripts/check-*.mjs` 會假失敗（繼承空 env 蓋掉 dotenv），跑前 `env -u`（保留 MEMORY_DIR）
- `check-preamble.mjs`：facts 為空時 memory block header 不渲染，fixed core 計算會涵蓋整份 preamble
- `RELAY_DELEGATE` tool note 只在 `config.relay` 開啟且 `relay-peers.json` 存在時注入（目前生產不含）
- **主程序 vs MCP 子行程的執行方式不同**：bridge 主程序跑 `tsx` 直吃 `src`，但 MCP 子行程（memory/google）三個 CLI 都吃 `dist`——改到 `mcp-memory` 的 import 鏈必須 `npx tsc -p .` 重建 `dist` 才生效，且要重啟 session 才會重新 spawn MCP
- `TokenSource.main` 是宣告但未被任何呼叫點套用的死政策（R-5 訂正發現）：`filterTransformedByPolicy()` 只被 `relay.ts` 與 `index.ts` 的 proxy 路徑呼叫，`run-prompt.ts` 主線完全不經過它，main 路徑實際靠 `TOKEN_POLICY.main` 全開放語意直接信任
- 修 `writePendingByPath` 這類共用 module-state 洩漏時要同類掃描同檔所有寫入端（commit 173591a 曾只修 `atomicWriteJson` 漏了 `updateJson`）

## 開發環境筆記

- `node --env-file` 不會覆蓋已存在的環境變數——bridge spawn 的子 shell 繼承舊 env 值，測試 `.env` 改動要用顯式變數覆蓋模擬重啟後行為
- 使用者機器已安裝 Bun runtime（`~/.bun/bin`），claude-mem plugin 的 hooks 依賴它執行，不可刪除
- Git commit 訊息的 Co-Authored-By model 名以 session 環境宣告的實際 model 為準；偏好把同一 session 內不相關的改動拆成多個小顆粒 commit，而非合併成一個
- repo 設定 `core.hooksPath=.githooks`，pre-commit 自動跑 `scripts/sync-skills-to-repo.mjs` 把 `default-skills/` 從本機 skill 目錄覆蓋同步回 repo——改 `default-skills` 前需注意可能被此 hook 覆蓋
- 2026-07-13 已同步 upstream relay 多 peer 系統（`relay-peers.json` + `src/relayPeers.ts`），取代本地未實際使用的 `RELAY_PEER_USERNAMES` 機制

## Context 壓縮（Headroom 評估）

整合優先級：方案 A（MCP server，零改 code）> 方案 D（headroom learn 獨立跑）> 方案 C（library 整合，最有效但改 core）；方案 B（proxy）排除因 Kiro CLI 不吃 `ANTHROPIC_BASE_URL`。

## 設計原則

Bridge 是中介層不是 harness，不追求與 Claude Code 功能對齊；保持差異化優勢（語意路由 + topic shard + embed-router）。Conversation Summarizer 已由 upstream `archiveSummaryEnabled` 覆蓋，不再獨立追蹤。

`dev-design` 多 agent 設計工作流分四階段（Explore → Propose → Adversarial → Synthesize）：即使 judge panel 把某提案排名第一，該提案仍可能被評為「無法照案直接實作」；Explore 階段宣稱「現有程式缺少某項能力」也可能是錯的（該能力其實透過其他底層邏輯間接實現）——adversarial 驗證應優先檢查 Explore 階段的假設本身，而非只驗證新提案。

## 相關工具

- **GitHubTool**：`G:\AI\GitHubTool`，Streamlit GitHub 組織管理 Web UI，主要操作 IGS-ARCADE-DIVISION-RD2 組織

## 相關

- [[uk-slot]] — 使用者的主要開發產品線
- [[ai-strategy]] — 跨模型策略與正典語料庫
