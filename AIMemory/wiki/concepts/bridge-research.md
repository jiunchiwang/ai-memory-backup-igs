---
title: Bridge 改善研究與 Roadmap
type: concept
created: 2026-06-28
updated: 2026-07-16
sources: [f_5a495e, f_af99c8, f_5209cd, f_c228c9, f_9d641c, f_7f1ee1, f_d933fc, f_5bd2fc, f_db1e8b, f_029977, f_50c2e9, f_9b0067, f_f1be4b, f_31228e, f_bdf14b, f_7fcdfa, f_1a894e, f_1a58d7, f_7cfe9b, f_1867ae, f_de84a8, f_0561d8, f_7fb676, f_bd8491, f_719003, f_121c69, f_a2c25a]
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

### ai_multi_agent（IGS RD2 內部框架）

- 公司 Python 多 agent 框架（Telegram Forum Topic 每 Topic 一 agent、中央 daemon + MCP reply）
- 定位互補：它往團隊/中央艦隊走，bridge 往單人深度助理 + MoA 品質走
- **2026-07-14 五項借鏡結論**：
  1. Memory Nudge（每 N turns 自動抽記憶）→ 擱置（機器未裝 llama.cpp）
  2. Improvement Harness（結構化錯誤收集）→ 不採用（真正缺口是紀律而非基礎設施）
  3. Workspace 結構化 → 不採用（意外查出 taskId 路徑穿越漏洞，已修）
  4. Central 知識萃取 → 縮小版採用（specialistreflect dream step，commit 21f12bf）
  5. ask_user timeout fallback → 縮小版採用（goal ASK-aware，commit 8e52c2e）
- 不適合 bridge 的：Forum Topic 路由、Central 中樞、cost_guard

## 通用架構教訓

- 為 headless CLI agent 設計架構時，不能直接套用長駐 async process 模式（同步阻塞/非同步 inbox）——一次性 spawn 無法 await，應先確認執行模型是否相容
- 引入結構化錯誤記錄機制不一定能提升實際診斷能力；若缺口是「紀律」就應補強紀律而非疊加基礎設施

### Fable-Advisor（echo-of-machines/fable-advisor）

- 借鏡 **context packaging pattern**（commit 4c1cfd5）：
  - RELAY_DELEGATE / PARALLEL_DELEGATE goal prompt 從三要素擴充為五要素（加「已知背景」「待決問題」）
  - PARALLEL_DELEGATE 區分決策型（自打包 context brief）/ 調查型（給路徑讓 specialist 自己讀）兩種 context 模式
  - 結果權重協議：給 delegate 結論認真權重，僅經驗性失敗或一手資料矛盾時不採納

### claude-plugins-official（anthropics/claude-plugins-official）

- 官方 Telegram plugin 定位：極簡 MCP channel（reply/react/edit 三 tool + pairing access control）
- 與 bridge 互補而非競爭——它是 Claude Code session 的 passthrough messaging，bridge 是完整 autonomous agent 平台
- 最大借鏡：**Permission Relay** 概念（高風險操作前走 Telegram 按鈕確認）
- 結論：現有 `<<ASK:...>>` token 已可實現同效果，只差 specialist preamble 加 guardrail 規則（列 watchlist）

### 三模型分工架構（已暫緩）

- 提案：Fable 5 當 orchestrator（~10% tokens）、Codex 5.5 當 executor（~60%）、Gemini 3.1 Pro 當 reviewer（~15%）
- 決策：暫緩不採用，避免未來重複提案

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

#### 增量 gap 報告後續（最終狀態 2026-07-07）

- 權限分層（leader-only gate 等效）→ ✅ 2026-07-08 `src/token-policy.ts`
- 分層權限 preamble → 不做（specialist preamble 已有 scope 分層，僅 cosmetic）
- MCP session/new 原生注入 + ACP trace → 已存在（gap 報告基於舊基準已過時）
- Warm Pool（specialist 冷啟動預熱）→ ⬜ 遠期，體感延遲優化

### 侯智薰 AI Agent 7 層 Harness 架構（2026-07-02）

研究侯智薰（雷蒙）對照 Hermes Agent（⭐20 萬）的文章，歸納 7 層：核心規則 / 技能 / 精煉記憶 / 使用者畫像 / 對話歷史 / 生命週期自動化 / 多平台門面。

**結論**：bridge 已覆蓋全部 7 層，且超越部分包括 embedding router、Local LLM、Specialist 分身、跨機 Relay、Self-improving reflexion、Context budget discipline。借鏡成果：觸發 P1 user-profile 獨立化實作。

P2 候選：週度反思迴圈（與 Conversation Summarizer 共享「掃 session」基礎設施但方向不同——反思升級 vs 壓縮上下文）。

#### Memory Nudge（本機 LLM 中途記憶抽取，評估中 · 2026-07-14）

- **來源動機**：ai_multi_agent「每 N turns spawn subprocess 回顧對話自動抽記憶」，探索改用本機 LLM（`local-llm.ts`）取代遠端呼叫
- **現況基準**：bridge 已有更厚的防線——`onBeforeClose` 自動存 transcript + 語意去重 fact 抽取（失敗進 pending-extract queue 開機重放）、agent crash 也存 transcript 供 `/dream` 撿。中途 nudge 唯一補的真空窗是 **bridge process 本體 hard-crash/斷電**（in-memory history 全滅，事後什麼都撈不回）
- **若做，最小可行設計**：
  - 觸發：assistant 回覆後新增 ≥N turns → 排 90 秒 idle debounce 才真正執行（避開快速對話時搶本機模型資源，不需新旗標，靠既有 `isLlamaCppBusy()` 跳過即可）
  - 抽取：不可直接重用 `extractLearnings()`（頭截斷 8000 字元，長 session 中途永遠看不到新內容）→ 需要增量變體：只餵「上次 nudge 後的新 turns」+ prompt 內附 EXISTING_FACTS 語意去重（`session-extract.ts` 既有 pattern 可抄）
  - 範圍：**只寫 facts,不寫 skill-candidates**——避開跟每日 `/dream`（`dream-session-reflect.ts` 的 skill-candidates 是盲 `appendFile` 零去重）雙寫
- **決策前置驗證**：本機小模型在「只看片段 + EXISTING_FACTS」下能否抽出乾淨不重複的 facts，未經實測前不動工
- ⛔ **離線驗證受阻（2026-07-14）**：這台機器沒裝 llama.cpp（`http://127.0.0.1:8080/health` 連不上、`.env` 的 `LLAMACPP_START_CMD` 是空的、系統上搜不到 `llama-server` 執行檔）。使用者確認：目前沒有實際用到本機 LLM enrichment,所以沒裝。**這比 Memory Nudge 本身更前置的一個事實**——`local-llm.ts` 掛的一整組 enrichment（`extractLearnings`/`compressFactsForPreamble`/`rerankRecallHits`/`prefilterSpecialistRoute`/`classifyIntentLLM`/`suggestFactMerges`/`detectShardDuplicates`）在沒裝 llama.cpp 的機器上全部靜默 fallback 成 no-op（每個函式開頭都是 `detectLlamaCpp()` 失敗就回傳 null/[]）。Memory Nudge 建在這組基礎設施上,若基礎設施本身不是常駐服務,應該先確認「要不要裝 + 裝在哪台機器」,而非先設計 Nudge 細節
- **狀態**：設計筆記保留,離線驗證與後續實作擱置,等基礎設施部署決策
- **完整探索記錄**：見 2026-07-14 對話（Fable 5 agent 產出設計筆記,附程式碼行號引用）

#### Improvement Harness（結構化錯誤收集，✅ 已評估 · 2026-07-14）

- **來源動機**：ai_multi_agent「結構化錯誤收集（含 `fix_applied` 欄位）+ 推送到 review topic」（`improvement_harness.py`）
- **決策：不引進這個概念**。關鍵證據：ai_multi_agent 自己的事後檢討文件（`docs/錯誤紀錄機制問題與解法.md`，2026-07-12）記錄了實際排查兩起 agent 崩潰時發現——harness 記錄的內容對診斷幾乎沒幫助,根因是**呼叫端沒把真正的診斷資訊傳進去**（timeout 事件永遠沒 `error_detail`、crash 事件的 `error_detail` 固定寫死成重試計數器）。教訓：schema 完整 ≠ 內容有用,問題在呼叫端紀律,不在基礎設施
- **bridge 現況已預告同樣的坑**：`src/local-llm.ts` 有 9 個 silent catch（179/230/253/306/351/409/454/501/564 行，`detectShardDuplicates`/`compressFactsForPreamble`/`summarizeChunk`/`summarizeSession`/`prefilterSpecialistRoute`/`rerankRecallHits`/`suggestFactMerges`/`classifyIntentLLM`/`extractLearnings`）失敗時連 `console.warn` 都沒有——比 ai_multi_agent 的 harness 還糟（後者至少記一筆空白事件）
- **bridge 現有機制已覆蓋 harness 的合理用途**：event schema → STATE.md 已證明能做結構化彙整；推播管道 → bridge 本身就是 Telegram 訊息機制；fix_applied（錯誤→修復留痕）→ knowhow-accumulation 的 ❌→✅ 記錄已在做，且 ai_multi_agent 自己的檢討裡這欄位從沒被提到有幫助
- **推送路徑判斷**：bridge 單人 chat，即時推播每則 enrichment 失敗等於洗版（服務沒起來時 9 個函式常常一起掛）；`/dream` 每日批次彙整進 STATE.md（High Priority/Watch List/Noise）才是對的預設，除非是既有 health monitor 已經在管的 critical 事件（ACP process 死亡）
- **已執行的第一步（零風險）**：9 個 silent catch 補上帶函式名與錯誤訊息的 `console.warn`，觀察 1-2 週實際 log 再決定要不要往上蓋彙整層——大機率連 STATE.md 彙整都不需要
- **完整探索記錄**：見 2026-07-14 對話（Fable 5 agent 產出設計筆記，附 ai_multi_agent 原始碼與事後檢討文件引用）

#### Workspace 結構化（每 agent knowledge/inbox/tasks.md，✅ 已評估 · 2026-07-14）

- **來源動機**：ai_multi_agent 的 `AgentWorkspace`（`workspace.py`）——每個 agent 一個資料夾：`knowledge/shared`+`knowledge/private`（會/不會被中央同步匯出）、`inbox/from_central/{tasks,knowledge,market}`（中央推送、agent 讀取後 unlink）、`tasks.md` 任務看板（進行中/待辦/等待中/已完成）、`.history/` 覆寫前備份
- **決策：整套不搬**。根因是架構前提不同，不是 bridge 機制已完美：ai_multi_agent 是「中央 daemon + 多個常駐 agent process」，workspace 是這些長駐 process 跟中央之間**持續存在的狀態**；bridge 的 specialist 是**用完即丟的 headless CLI spawn**（PARALLEL_DELEGATE/RELAY_DELEGATE 每次全新 process，做完就結束），bridge 本身就是唯一協調者
- **四件式逐項對照**：inbox（一次性推送消費）被「spawn 時直接傳 goal prompt」結構性取代；`export_knowledge(since)` 增量同步無用武之地（沒有兩份狀態要收斂）；shared/private 分區的存在理由是「決定匯出邊界」，bridge 無匯出，動機歸零；tasks.md 看板無讀者——specialist 一次 spawn 做完，artifact 的 status 就是完成記錄，跨多次 delegation 的長期任務目前是靠主 agent 的 facts/memory + goalStore 追蹤，不該搬進 specialist workspace
- **意外抓到的真問題（已修復）**：探索過程中查出 `RELAY_DELEGATE` 的 `id`（`run-prompt.ts:751`）與 `PARALLEL_DELEGATE` 的 `taskId`（`run-prompt.ts:776`）都未經淨化直接流進 `saveArtifact()`，拼進 artifact 檔名（`artifact.ts:92`）；`path.join` 會正規化 `..`，理論上可路徑穿越寫出 `artifacts/` 目錄外。嚴重度低（需 agent 自己被誘導吐出惡意 token），但修法便宜——已在 `artifact.ts` 對 taskId 做白名單化
- **獨立立案但不掛在此借鏡下的技術債**：`specialist-memory.ts` 純 append-only、無分類、讀取只取尾 20 行，舊 lessons 事實上蒸發但沒有真的被清理——這是既有 Phase B+ 的技術債，跟 workspace 借鏡無關，不需要因為這次評估去抄 ai_multi_agent 的目錄式知識庫或版本化方案
- **完整探索記錄**：見 2026-07-14 對話（Fable 5 agent 產出設計筆記，附 ai_multi_agent 原始碼引用 + bridge 端 taskId 未淨化的具體行號）

#### Central 知識萃取增量匯出（縮小版：specialist lessons 升格通道，✅ 已實作 · 2026-07-14）

- **來源動機**：ai_multi_agent 的 `GET /api/knowledge/export?since=...`（中央 daemon 拉每個 agent workspace 的增量知識）+ `POST /api/inbox/receive`。原始形式跟 Workspace 結構化是同一套機制的兩端，已隨該借鏡一併否決（bridge 無「中央+常駐 agent 收斂兩份狀態」的前提）
- **但重新框定後找到真缺口**：bridge 的 4 個 specialist（slot-dev/researcher/general/video-prod）分工正交，**橫向互通價值低不值得建**；缺口是**縱向**的——`specialist-memory.ts` 抽出的 lessons 只回流自己下次 spawn 的 preamble（`readMemory()` 取最近 20 行），`/dream` 的 `session-reflect` 只掃主 session 的 `sessions/*.md`，完全不掃 `specialist-memory/*.md`。specialist 學到的教訓跟主 session 聊出來的 lessons 價值同級，卻沒有升格進主 facts/wiki 的通道，而且舊 lessons 被擠出「最近 20 行」視窗後連自己都用不到——升格是唯一保存路徑
- **ai_multi_agent 的關鍵教訓可套用**：他們程式碼註解明講「task_assignment 不能只推進 inbox 等 agent 自己讀，實測過同一顆 LLM 面對簡單問候就是不會主動檢查，必須由程式碼保證送達」。這條教訓精確命中 bridge 現有的 pending-ingest 機制（`artifact.ts` 的 `savePendingIngest`/`listPendingIngests`，僅 researcher + 輸出 >5000 字才觸發）——目前完全依賴 preamble 底部提示 + 主 agent 自己注意到，是同一種「靠 agent 主動檢查」的不可靠模式，只是範圍窄所以還沒爆
- **最小可行設計**：`/dream` 新增 `specialistreflect` step（獨立 step，不擴充 session-reflect，理由：dream 的 per-step `continue_on_error` 隔離 + metrics + 使用者可各別關閉）——讀 4 個 `specialist-memory/*.md`，用 `appendMemory()` 既有的行內時間戳當土砲游標（存 `.reflect-cursor.json` 記每個 specialist 上次處理到哪個時間戳，不需要 HTTP/since，因為是同一顆 process 讀本地檔），餵既有 `extractLearnings()` 本機 LLM 抽取，fact 走 `appendFactsDedup` 去重、candidate 走 `skill-candidates.md`；同一個 step 順便檢查 pending-ingest 累積 ≥3 天者，寫進 STATE.md High Priority（既有「dream High Priority 跨 ACP 入口」按鈕機制可直接複用，見上方 P1 章節），把「preamble 提示等注意」升級為「排程檢查 + 使用者一鍵轉送」
- **風險提醒**：`specialist-memory.ts` 有 `[auto-summary]` fallback 尾巴（品質較雜），`extractLearnings` 的 confidence 過濾要能擋掉，上線後應觀察 facts 污染率
- **實作狀態**：已完成（commit `21f12bf`）——新增 `src/commands/dream-specialist-reflect.ts`，註冊進 `index.ts` COMMAND_HANDLERS 與 `dream-config.ts` DEFAULT_STEPS（14→15 步），`check-dream.mjs` 步數斷言同步更新，24 項全過，`npx tsc --noEmit` 通過
- **已知限制**：這台機器沒裝 llama.cpp（見上方 Memory Nudge 條目），`extractLearnings` 短期內會持續回傳 []——這個 step 上線後短期只有「游標推進」與「pending-ingest 老化檢查」會生效，facts/candidates 升格要等本機 LLM 就緒才會真的發生
- **完整探索記錄**：見 2026-07-14 對話（Fable 5 agent 產出設計筆記）

#### ask_user 同步阻塞 + timeout fallback（縮小版：goal 迴圈 ASK-aware continuation，✅ 已實作 · 2026-07-14）

- **來源動機**：ai_multi_agent 的 `ask_user()`（`telegram_adapter.py:1388`）——真的 `await` 一個 Future 阻塞 agent 執行緒等使用者點按鈕，預設 300 秒逾時自動解除、訊息改顯示「已逾時」、turn 被中斷時 `_sweep_pending_asks()` 強制取消殘留問題
- **決策：同步阻塞本體不搬**。bridge 三個 ACP backend（Kiro/Codex/Claude Agent）都是「跑一次 prompt→出結果→turn 結束」的 headless CLI 模型，沒有「暫停執行等外部訊號再恢復」的機制；為此改變整個 backend 執行模型不成比例，且 bridge 現行 fire-and-forget ASK（使用者晚點按，答案就是新一輪訊息）在一般對話下語意仍然有效，不需要 ai_multi_agent 那套 stale-callback 防護
- **意外查證出的真缺陷**：`/goal` 迴圈的 continuation 排程（`run-prompt.ts` 4 處 `GOAL_CONTINUATION_DELAY_MS = 500`，行 1151/1584/1807/1822）**完全不看這輪有沒有 emit ASK**，500ms 後就無條件推進下一輪——agent 在 goal 迴圈裡問使用者問題，答案結構上永遠來不及，下一輪 continuation prompt 只說「continue toward the goal」，agent 只能瞎猜或重複問，燒 turn budget。一般對話下「沒人回 ASK」代價幾乎零（按鈕不會真失效，`index.ts` callback fallback 直接解析 key），但 goal 迴圈是真痛點
- **可行性已查證**：函式作用域內已有 `asks.length`（`run-prompt.ts:1021` 診斷 log 已在用），代表「這輪有沒有問 ASK」這個布林值本來就摸得到，只是 4 個 continuation 排程點都沒有參考它——不需要新建資料流，純粹是既有資訊沒被使用
- **最小可行設計**：goal turn 若這輪 emit 了 ASK，continuation 排程改用較長延遲（例如 10 分鐘）而非固定 500ms；使用者點按 → 既有 `[ASK:id] key` user turn 本來就會 preempt continuation，零新路徑；逾時 → continuation prompt 注入一行「使用者未回覆 ASK，請做保守假設繼續或改用非互動方式推進」——這是 ai_multi_agent「timeout 回 None、agent 自己接手善後」的 bridge 等價物
- **次要補強（可選，二期）**：/dream 加一步「pending ASK 老化 → actionItems → STATE.md High Priority」，可直接複用 `dream-specialist-reflect.ts` 的 stale-ingests 前例；但 `AskRegistry` 是純 in-memory Map，重啟即失憶，要嘛接受此限制、要嘛加輕量持久化（已超出最小範圍）
- **實作狀態**：已完成（commit `8e52c2e`）——新增 `GOAL_ASK_WAIT_MS`（10 分鐘）常數與外層 `turnHadAsk` 旗標（`asks` 宣告在較深巢狀區塊，continuation 排程點在外層，仿 `continueTokenFired`/`pendingRestartReason` 模式做外層旗標），只改動 `continuationPlan`（AB-7b）與 `<<CONTINUE>>` token 兩個真正的 goal continuation 排程點，刻意不動另外兩處重用同常數的無關用途（relay 摘要 debounce、WIKI_QUERY 自動觸發）；使用者按鈕回覆本來就會透過 `index.ts:846` 的 `cancelPendingContinuation` 天然 preempt，不需新路徑；逾時則在下一輪 continuation prompt 注入提示，讓 agent 自行做保守假設。`npx tsc --noEmit` 通過，`check-ab7-goal-loop.mjs` 8/8 無 regression
- **驗證缺口（誠實記錄）**：既有測試只模擬「要不要產生 continuationPlan」的決策邏輯，不觸及 `runPrompt` 內真正的 timer 排程程式碼（需要活的 Telegram bot + ACP session 才能端到端驗證），這次沒有為此新建 mock 測試骨架——屬有意識的範圍取捨，不是遺漏
- **完整探索記錄**：見 2026-07-14 對話（Fable 5 agent 產出設計筆記）

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
