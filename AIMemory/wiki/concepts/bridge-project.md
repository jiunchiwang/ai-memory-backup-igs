---
title: Telegram-Kiro-Bridge 專案
type: concept
created: 2026-06-03
updated: 2026-07-23
sources: [f_946c9d, f_e19357, f_719003, f_e17260, f_36e49d, f_842a1b, f_8da350, f_4e8237, f_d21a12, f_0b90e2, f_60159c, f_b7206d, f_5a495e, f_af99c8, f_a10e66, f_721fa7, f_07d587, f_460731, f_7d747c, f_5b7f6a, f_381c4b, f_e47a60, f_5209cd, f_c228c9, f_71bf67, f_789096, f_5a515c, f_1c58e2, f_937543, f_d0b214, f_651961, f_75d645, f_a6e65d, f_78b50f, f_bd10fc, f_0a8153, f_9b1654, f_b533eb, f_456de2, f_645ea3, f_892166, f_046ffa, f_ae069c, f_493309, f_eb92f6, f_b615b7, f_84107f, f_e6facf, f_1ff1d5, f_bdc742, f_5a2532, f_e62610, f_15ac36, f_510f59, f_2327e5, f_d274c6, f_fedf5c, f_b966f9, f_dc72cc, f_6a3827, f_a4464b, f_054543, f_1dbc98, f_912029, f_152b53, f_ceda58, f_6a6c22, f_e5843d, f_f94c52, f_d61c50, f_493b31, f_1e4cda, f_9c5954, f_b01ccb, f_ace685, f_c965d5, f_a0a929, f_5bb6fa, f_a1d087, f_56f3c9, f_de84a8, f_7cfe9b, f_1867ae, f_0c2487, f_2a93b5, f_50951c, f_dd41a9, f_7d8cb9, f_5871a8, f_69884b, f_36529c, f_3bc9f5, f_32a736, f_3bb538, f_ad29fd, f_02206d, f_bf688a, f_0e5446, f_76b1f7, f_88d3a1, f_5bd2fc, f_0561d8, f_130b5d, f_b1b0f4, f_166fd1, f_5bf5da, f_eb9ddd, f_131cef, f_f44d46, f_b1e2ca, f_484853, f_cc8fd5, f_f144ad, f_28e17b, f_f16f7b, f_d6b17c, f_9f9b1f, f_87901e, f_3f826e, f_b21c3a, f_7d5145, f_51bc41, f_90a25d, f_a23d83, f_4c12ce, f_651a0d, f_e72b07, f_ea9657, f_d878ad, f_9b9689, f_e7bcdd, f_1b2fd1, f_6de90c, f_332dae, f_e272f0, f_235eef, f_f2dc75, f_dff56f, f_cd57ae, f_b56b60, f_810445, f_ff0915, f_4835ec, f_a4eb9f, f_b8922f]
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
- [[bridge-upstream-sync]] — Fork 同步策略、合併衝突處理原則、push 前 Fable5 覆核（2026-07-21 拆出）
- [[bridge-dream]] — /dream 例行維運框架本身（dream.json 機制、claude-mem-curate 接入、turn 誤報「(no output)」兩種根因；2026-07-22 拆出）

## 文件與教學

- `docs/usage-guide.html` — 功能教學頁面，深色主題，24 章節附範例
- `docs/pending-roadmap.html` — 待做方案總覽（深色主題、目錄跳轉），記錄所有未完成 roadmap 項目
- `docs/llm-to-ai-agent-summary.html`、`docs/hermes-vs-bridge.html`、`docs/karpathy-wiki-alignment-roadmap.html` — 學習/比較/roadmap 專頁
- `docs/session-archive-explained.html` — session 歸檔說明

## 部署與 Git

- `start.bat` 開機自動啟動（`shell:startup`），process 退出後 loop 3 秒自動重來
- 多機器部署：本機 G: 磁碟（`MEMORY_DIR=G:\AI\AIMemory`），原開發機 F: 磁碟；`.env` 必須正確設 `MEMORY_DIR`、`BACKUP_REPO_DIR`，否則 /dream 全部失敗
- Git：upstream `redkilin/telegram-kiro-bridge`、fork `jiunchiwang/telegram-kiro-bridge`（origin）；fork 同步策略與合併衝突處理原則見 [[bridge-upstream-sync]]
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

## bridge-actions MCP（2026-07-16）

`bridge-actions` MCP server 提供 6 個 action 工具：`ask`/`schedule`/`delegate`/`parallel_delegate`/`send_file`/`relay_file`，取代舊的裸文字 token 協定（`<<ASK:...>>` 等仍保留作 fallback）。同步進來時功能旗標雖預設開但未接線（`dist/mcp-actions.js` 未 build、agent config 未註冊）；經確認後執行 `npm run build` + `node scripts/setup-mcp.mjs`，已寫入 `~/.claude/settings.json`、`~/.claude.json`、`~/.kiro/agents/main.json`、`~/.codex/config.toml`。⚠️ MCP server 於 session 建立時 spawn，不可熱插拔，需重啟受影響 session 才會生效。README.md 與 `docs/usage-guide.html`（2026-07-17 補上 6 個 action tool 的說明章節）皆已同步補上說明。

跨專案文件同步慣例：AI-canonical 正本三份 skill（`ms-agent-scheduled-prompts`、`ms-agent-text-token-signaling`、`ms-telegram-ask-button-protocol`）已同步更新為 MCP-first 邊界說明——bridge-managed session 優先呼叫 `bridge-actions` MCP tool，只有明確回報 unavailable 才退回文字 token；validation/policy 錯誤須修參數，不可用 token 繞過（commit d6853e2，未 push；詳見 [[ai-strategy]]）。

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

## Push 前安全機制

完成 merge/sync 後、push 到 origin 前的獨立 Fable5 覆核慣例見 [[bridge-upstream-sync]]；已在至少 4 個 commit 中實際採用（如 `04cc0bc` 訊息明確標註「Fable5 push 前覆核」），是跨多次 merge 反覆使用的專案慣例，非單次紀錄。輕量呼叫方式見 [[bridge-acp]]（`claude -p --model fable`，不透過 specialist/domain 機制註冊）。

## 共享知識庫同步（/sharedsync，2026-07-19）

`/sharedsync` 是 fork 自 upstream 的跨機知識庫雙向同步機制（`G:\AI\AIMemory\shared\`），與單向的 `/backup` 分離（`backup.ts` 刻意排除 `shared/` 防重複備份）。2026-07-18 dream run 報 `/sharedsync` 失敗（`not a git repository`），排查後發現兩層真因：

- **不是缺 repo**：`docs/SPEC-relay-workspace.md` 提到的 `redkilin/ai-shared-knowledge` 是 **upstream 作者 tonykuo 自己的私人跨機知識庫**（隨 fork 一起被拉進來的文件），與使用者無關、本來就無權限（404 正常），「建自己的 remote」這步從沒替使用者做過
- **真正卡 push 的是憑證帳號不匹配**：本機 Windows Credential Manager 對 generic `https://github.com` 快取的是 `igs-jiunchiwang` 帳號，與新 repo 所屬的 `jiunchiwang` 對不上——把 remote URL 改嵌 `https://jiunchiwang@github.com/...` 配對到另一組已快取憑證後 push/pull 正常，不需重新登入或 token

修復：新建私有 repo `jiunchiwang/ai-shared-knowledge`、`git init` + 初始 commit（保留原有 intel-learning 筆記）+ push，`/sharedsync` 已驗證正常。

## 暖機期訊息處理（warmup，2026-07-19）

啟動階段（specialist sync、llama 等待、`scheduleStore.load`、goal-resume 等慢速操作）尚未就緒時收到的 Telegram 訊息，過去可能遺失或在半初始化狀態被處理。經 `dev-design` judge-panel 選定 **MVP-first 方案**（72 分，勝過 robustness-first 54 / simplicity-first 40，並嫁接後兩者關鍵設計）：新增 `warmup.ts` 模組，用 `coreReady` 旗標 + FIFO 佇列暫存啟動期收到的原始 grammy Update，核心就緒後 replay。

可重用 trade-off：**`fetchReady`（runner 已在 poll、訊息不會遺失）與 `coreReady`（訊息→agent 處理路徑完全安全）是兩個獨立就緒層**，長輪詢 bot 若有慢速啟動階段應把這兩層分開處理。

## GitHub PAT 洩漏事件與 /backup 修復（2026-07-19~22，反覆發生 2 次）

2026-07-19 起 `/backup` 被 GitHub push protection 擋下：使用者先前貼在對話中的 GitHub PAT（`ghp_` token）洩漏進 `AIMemory/events.jsonl`（約 7868-7873 行）與 `oldSessions/session-509424983-2026-07-19T09-10-45.md:268`，需清除該 secret 才能恢復自動備份。教訓：對話中貼的真實密鑰會落地 `events.jsonl` 與 session transcript，不應在對話中貼 token。

查證確認該 secret 只存在於本機**尚未 push** 的 backup commit（GitHub push protection 在推到 remote 前即擋下，實際未外洩到 GitHub）；用通用 regex pattern（而非逐字打出 secret 本身，避免驗證指令又被 bridge 自己的事件記錄器重新記回 log）清除 `events.jsonl`/`observations.jsonl`/`oldSessions/*.md` 中的殘留。

同一份洩漏的 secret 在 2026-07-22 因 session 檔案再次被 `memory-to-skill` 搬進 `oldSessions/` 而重新進到一個新的未推送 commit（`0ee84d8`），再度被 push protection 擋下。清理技巧：**若含 secret 的 commit 尚未推送到遠端，可安全用 `git commit --amend` 改寫該 commit 內容移除 secret**（`0ee84d8`→`8428d72`），再用 `git reflog expire --expire=now --expire-unreachable=now --all` + `git gc --prune=now` 徹底清除本地磁碟上的殘留 commit 物件，才推送成功。使用者已被提醒去 GitHub 撤銷該 token。

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
