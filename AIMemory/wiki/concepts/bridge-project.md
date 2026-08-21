---
title: Telegram-Kiro-Bridge 專案
type: concept
created: 2026-06-03
updated: 2026-08-21
sources: [f_946c9d, f_e19357, f_719003, f_e17260, f_36e49d, f_842a1b, f_8da350, f_4e8237, f_d21a12, f_af99c8, f_5b7f6a, f_5209cd, f_c228c9, f_0a8153, f_456de2, f_645ea3, f_046ffa, f_493309, f_b615b7, f_84107f, f_e6facf, f_8a9bd7, f_15ac36, f_fedf5c, f_b966f9, f_a4464b, f_054543, f_912029, f_152b53, f_ceda58, f_6a6c22, f_e5843d, f_f94c52, f_d61c50, f_1e4cda, f_9c5954, f_b01ccb, f_ace685, f_c965d5, f_a0a929, f_5bb6fa, f_a1d087, f_56f3c9, f_de84a8, f_7cfe9b, f_1867ae, f_0c2487, f_2a93b5, f_50951c, f_dd41a9, f_7d8cb9, f_5871a8, f_69884b, f_36529c, f_3bc9f5, f_3bb538, f_ad29fd, f_02206d, f_bf688a, f_0e5446, f_76b1f7, f_88d3a1, f_5bd2fc, f_0561d8, f_130b5d, f_b1b0f4, f_166fd1, f_5bf5da, f_eb9ddd, f_131cef, f_f44d46, f_e2e14a, f_cc8fd5, f_28e17b, f_f16f7b, f_d6b17c, f_9f9b1f, f_87901e, f_3f826e, f_b21c3a, f_7d5145, f_51bc41, f_a23d83, f_4c12ce, f_e72b07, f_ea9657, f_d878ad, f_e7bcdd, f_1b2fd1, f_6de90c, f_332dae, f_dff56f, f_cd57ae, f_b56b60, f_ff0915, f_4835ec, f_a4eb9f, f_b8922f, f_da3d5b, f_877531, f_e85cc9, f_06ae88, f_5302c0, f_3fb62a, f_10387c, f_bb1fcf, f_b01fe2, f_84dd82, f_cba34c, f_40504b, f_c79917, f_66f268, f_6b85d6, f_633596, f_a60ce8, f_bee7a3, f_d71f60, f_39ef23, f_1076e9, f_489e55, f_15bffc, f_7d05b7, f_c0ada7, f_191c67, f_916228, f_a37cfa, f_82bd9f, f_6ad6e7, f_8d5086, f_198e79, f_bef432, f_71c654, f_1ac058, f_200c89, f_b82b6e, f_f0aeea, f_8ca646, f_42e862, f_57bf1c, f_4d4805, f_f9f50a, f_4a3140, f_5df807, f_549d3f, f_474e9e, f_aff418, f_e04f09, f_18f02e, f_b5d499, f_5eaaed, f_565fbf, f_6dffc5, f_b35b6b]
history_sources: [f_32a736, f_b1e2ca, f_484853, f_e272f0, f_5a2532, f_493b31, f_810445]
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
- [[bridge-smoke-gate]] — 測試閘門與建置（tsc/smoke tier/pre-push、環境隔離假失敗、計數同步儀式、CI 決策；2026-08-01 拆出）
- [[verification-diagnosis]] — 跨專案的驗證／診斷方法論（恆真斷言、實驗設計原則；2026-08-01 從 misc 拆出）
- [[gate-mutation-testing]] — 突變測試方法論（2026-08-21 從 verification-diagnosis + bridge-smoke-gate 拆出）
- [[bridge-infra]] — Process 生命週期、start.bat supervisor、暖機 coreReady/FIFO、session.buffer 中途失敗偵測、Impact-Gate Hook
- [[bridge-secrets-backup]] — acp-trace 洩漏、GitHub PAT 洩漏與自我重複污染迴圈、/sharedsync 跨帳號 credential
- [[bridge-self-eval]] — SELF_EVAL 六個共通致命缺陷、Turn-Lint 啟發式 warn-only 設計
- [[bridge-doc-sync]] — 文件事實來源機制與計數類機械閘門設計原則
- [[bridge-telegram-delivery]] — 出站投遞：HTML 排版取捨、重試 instrumentation 的存活者偏誤、重複投遞四層修復與重放安全性判準 R-A/R-B/R-C（2026-08-21 拆出）

### 2026-08-21：本頁瘦身 268→165 行

兩種動作，不要混為一談：

**① 十五節刪除過時副本（改主場）。** 這些主題長年在本頁與專屬子系統頁各留一份，而本頁那份停在較早的結論——例如「Push 前安全機制」仍寫 Fable5，而 08-13 已換成 `kiro-cli glm-5` 跨 vendor。**過時副本比沒有更糟** ∴ 刪除副本、只留上方索引：

`/sync Upstream 同步機制`＋`Push 前安全機制` → [[bridge-upstream-sync]]；`Process 管理`＋`暖機期訊息處理` → [[bridge-infra]]；`SELF_EVAL 量化自評`＋`Turn-Lint 回覆格式機械檢查` → [[bridge-self-eval]]；`/backup acp-trace 洩漏修復`＋`GitHub PAT 洩漏事件`＋`共享知識庫同步（/sharedsync）` → [[bridge-secrets-backup]]；`CI 把關決策` → [[bridge-smoke-gate]]；`Claude Agent SDK 權限模型` → [[claude-agent-sdk]] §4.1；`背景通知與對抗覆核`的 Fable5/afb9d8e 那條已在 [[adversarial-review]] 的價值實證表內。

**② 四處本頁獨有內容，先移到主場再刪**（不是刪掉）：`/sync` 的 exit-code 判定契約＋「分享 repo 給同事」整節 → bridge-upstream-sync；Agent SDK 六階權限評估與四個陷阱 → claude-agent-sdk §4.1；「調延遲後時間差不變就不是競態」→ [[verification-diagnosis]]；`訊息排版`＋`Telegram 重試`＋`重複投遞四層修復` 整個叢集 → 新頁 [[bridge-telegram-delivery]]。

## 文件事實來源改為原始碼（2026-07-31）

`/docupdate` 原本的設計是「讀 README 當比對基準去修 `docs/usage-guide.html`」——**拿產出物當事實來源**，形成自我回歸迴圈：README 自己會過期，於是那次同步依過期 README **刪掉了 HTML 裡真實存在的 `specialistreflect` 步驟**並把 Dream 步驟數從 15 改成 13。兩份文件互相一致但都錯。

修法（commits `d8bf64a` → `6e47af6` → `7e75990`）：

- **新增 `src/doc-facts.ts`** — bridge 自己從原始碼機械枚舉事實並算差集，agent 只負責寫文字：指令 48 個（`bot-setup.ts` COMMAND_SPECS）／Dream 步驟 15 步含順序（`dream-config.ts` DEFAULT_STEPS）／事件型別 20 種（`event-log.ts` EVENT_TYPES）
- **三個防呆**：下界斷言（regex 與結構脫鉤時 throw，避免「永遠成功、永遠什麼都不做」）／只加不減（文件多出來的另列「可疑」供人判斷）／別名正規化
- **後續重構**：`doc-facts.ts` 從 regex 撕原始碼改成**直接 import 模組**（Fable 5 覆核建議，減少平行實作脫鉤）；為此 `event-log.ts` 改寫成 `const array + type 推導`（`EVENT_TYPES` 可 runtime 枚舉、`EventType` 從陣列推導）
- **`scripts/check-doc-sync.mjs`** 成為 pre-push 閘門 → 見 [[bridge-smoke-gate]]

順帶抓到的同類問題：`check-bot-command-descriptions.mjs` 的斷言是恆真的（見 [[verification-diagnosis]]），導致 `/dream` 的 Telegram desc 276 字元被靜默截斷、步數寫錯（10 vs 實際 15）卻測試全綠。

> `.claudedocs/` 在 `.gitignore` 內 —— `問題追蹤.md` 是**刻意不進版控**的本機記錄檔，升格條目寫進磁碟即生效（CLAUDE.md Section 6a 讀的就是本機檔），不應用 `git add -f` 硬塞進版控。

## 文件與教學

- `docs/usage-guide.html` — 功能教學頁面，深色主題，24 章節附範例
- `docs/pending-roadmap.html` — 待做方案總覽（深色主題、目錄跳轉），記錄所有未完成 roadmap 項目
- `docs/llm-to-ai-agent-summary.html`、`docs/hermes-vs-bridge.html`、`docs/karpathy-wiki-alignment-roadmap.html` — 學習/比較/roadmap 專頁
- `docs/session-archive-explained.html` — session 歸檔說明
- `docs/superpowers/plans/2026-07-07-acp-session-resume.md` — session resume 實作計畫，含 BC-1~5 行為契約與 adapter 實測記錄表（見 [[bridge-session]]）

## 部署與 Git

- `start.bat` 開機自動啟動（`shell:startup`），process 退出後 loop 3 秒自動重來
- 多機器部署：本機 G: 磁碟（`MEMORY_DIR=G:\AI\AIMemory`），原開發機 F: 磁碟；`.env` 必須正確設 `MEMORY_DIR`、`BACKUP_REPO_DIR`，否則 /dream 全部失敗
- Git：upstream `redkilin/telegram-kiro-bridge`、fork `jiunchiwang/telegram-kiro-bridge`（origin）；fork 同步策略與合併衝突處理原則見 [[bridge-upstream-sync]]
- 兩份 upstream SPEC 為 draft 未實作（acp-hot-swap、moa-provider），與 NotebookLM 修復並列暫緩待辦

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
- **Daily Intel BOM 修復**（2026-08-05）：產出的 markdown 檔案在手機上顯示亂碼，根因是 UTF-8 without BOM；已在 `src/daily-intel/reports/daily.ts` 加上 UTF-8 BOM（`﻿`）

## bridge-actions MCP（2026-07-16）

`bridge-actions` MCP server 提供 6 個 action 工具：`ask`/`schedule`/`delegate`/`parallel_delegate`/`send_file`/`relay_file`，取代舊的裸文字 token 協定（`<<ASK:...>>` 等仍保留作 fallback）。同步進來時功能旗標雖預設開但未接線（`dist/mcp-actions.js` 未 build、agent config 未註冊）；經確認後執行 `npm run build` + `node scripts/setup-mcp.mjs`，已寫入 `~/.claude/settings.json`、`~/.claude.json`、`~/.kiro/agents/main.json`、`~/.codex/config.toml`。⚠️ MCP server 於 session 建立時 spawn，不可熱插拔，需重啟受影響 session 才會生效。README.md 與 `docs/usage-guide.html`（2026-07-17 補上 6 個 action tool 的說明章節）皆已同步補上說明。

跨專案文件同步慣例：AI-canonical 正本三份 skill（`ms-agent-scheduled-prompts`、`ms-agent-text-token-signaling`、`ms-telegram-ask-button-protocol`）已同步更新為 MCP-first 邊界說明——bridge-managed session 優先呼叫 `bridge-actions` MCP tool，只有明確回報 unavailable 才退回文字 token；validation/policy 錯誤須修參數，不可用 token 繞過（commit d6853e2，未 push；詳見 [[ai-strategy]]）。

## /goal ASK-aware 修復

- 原問題：continuation 排程 500ms 後無條件推進，不看該輪有無 `<<ASK:...>>`，使用者問題形同虛設
- 修復：新增 `GOAL_ASK_WAIT_MS=10分鐘` + `turnHadAsk` 旗標（commit 8e52c2e）

## 已知陷阱

- Smoke test 環境隔離：bridge session 內跑 `scripts/check-*.mjs` 會假失敗（繼承空 env 蓋掉 dotenv），跑前 `env -u`（保留 MEMORY_DIR）
- `check-preamble.mjs`：facts 為空時 memory block header 不渲染，fixed core 計算會涵蓋整份 preamble
- `RELAY_DELEGATE` tool note 只在 `config.relay` 開啟且 `relay-peers.json` 存在時注入（目前生產不含）
- **主程序 vs MCP 子行程的執行方式不同**：bridge 主程序跑 `tsx` 直吃 `src`，但 MCP 子行程（memory/google）三個 CLI 都吃 `dist`——改到 `mcp-memory` 的 import 鏈必須 `npx tsc -p .` 重建 `dist` 才生效，且要重啟 session 才會重新 spawn MCP
- `TokenSource.main` 是宣告但未被任何呼叫點套用的死政策（R-5 訂正發現）：`filterTransformedByPolicy()` 只被 `relay.ts` 與 `index.ts` 的 proxy 路徑呼叫，`run-prompt.ts` 主線完全不經過它，main 路徑實際靠 `TOKEN_POLICY.main` 全開放語意直接信任
- 修 `writePendingByPath` 這類共用 module-state 洩漏時要同類掃描同檔所有寫入端（commit 173591a 曾只修 `atomicWriteJson` 漏了 `updateJson`）
- **tsconfig 已於 2026-08-02 開啟 noUnusedLocals**（commit 134aebe），舊記錄「未開 noUnusedLocals」已過時；詳見 [[bridge-smoke-gate]]
- **impact-gate hook 是「每檔首次修改」觸發**：一次批次改 20 個檔案時 20 個 Edit 會全部被擋，同一份因果鏈分析可涵蓋整批同類改動，輸出後原樣重試即全數放行
- **Bash tool 用 heredoc 寫檔時 `\n` 可能被展開成真換行**，破壞產出的原始碼（2026-08-01 連續踩兩次：寫壞 TypeScript 註解、寫壞測試字串字面值導致 SyntaxError）；修法改用 `chr(10)`／`chr(92)+'n'` 這類不含跳脫字元的構造方式
- **`POLICIES/development-methodology.md` 一則「L1 機械層一直是空的」假宣稱已更正（2026-08-13）**：實查 `.claude/hooks/impact-gate.mjs`（2026-07-06 建）確實存在且已在 `.claude/settings.local.json` 註冊為 PreToolUse，本輪在 `claude-agent-acp` session 內實測會 `exit 2` 擋下 Write——真正不存在的只有另一套工具（ClaudeCodeTools）的 `impact-analysis-guard.sh`，兩者被誤判成同一件事。該檔在 R-2 保護清單內，改動須走異源覆核；`CLAUDE.md` 承重核摘要與 `POLICIES/run-plan-orchestration.md` 退化路徑有同句回音待一併修。方向性結論：閉環方法論的可重用概念不拆成獨立 skill（已是 skill 的部分已 skill 化，多階段編排已是 plan-templates，always-on 紀律靠 `@import`），跨專案共用的載體改用 AI-canonical 的 steering。

## 積壓修復記錄（2026-08-05 補記，實際發生於 2026-08-01~04）

以下 fact 因今日 topic review 拆分而落入本 shard，內容過去未曾寫進任何 wiki 頁，屬積壓補記：

- **draft 重播第二個獨立成因**：回覆超過 ~3900 字後 `truncateTail` 的滑動視窗會在頭部插 `…` 並整段位移，共同前綴只剩 1，之後每個 tick 必定重播——這不是 05:00/09:17 兩起症狀的成因（55–1938 字未達上限），要解需改設計（拆多則訊息，或到上限就凍結 draft 讓最終訊息帶完整文字）。列為待辦，未修。
- **「共用函式 ⇒ 共用決策」是錯的推論**：同一支 helper 被兩個呼叫端以不同字串呼叫時（cut 收 raw buffer、hide 收已抽 token/已 collapse/已 trim 的字串），共用它並不保證判定一致。這個輸入不對稱在決策不依賴長度時完全不可觀測，一旦引入長度門檻就會暴露成使用者可見的分歧（實證：draft 顯示 742 字、final 只剩 8 字）。
- **採納覆核建議的過度概括陷阱**：把「這個位置放上限會壞」讀成「這件事不該做」，於是製造出新的不一致——v1 反例真正禁止的只是「draft 幀上 hide 疊在 cut 之上」，卻被讀成「final 的 hide 必須無界」，導致 final 銷毀 draft 已展示的內容。
- **測試斷言寬窄決定它能不能擋住錯誤設計**：3g 原本斷言「draft 與 final 都不含 opener」（寬錨點）而綠著出貨三個版本，改成 `draft === final` 逐字相等後才擋得住；語料只有「對稱形狀」時會全盲，必須把已知反例形狀（走廊 A/B）納入語料，並加兩個反向守衛擋掉「都扣光」與「都不扣」這兩種讓相等成立的退化解。
- **live 計時器污染去重早退**：render 出來的字串若含 `Date.now()` 算出的經過秒數，下游所有 `content === lastRendered` 形式的去重早退會結構上永遠不命中，且不報錯，只安靜表現成週期性的多餘 API 寫入——單輪累計 3529 筆 `status.edit`，多數內容差異只有一個小數位。
- **`/model` 指令已修復顯示實際 ACP model**：ACP provider 時從 session 的 `verifiedModelInfo` 取得實際 model，而非硬編碼的 `claude-sonnet-4` via Bedrock；有 effort 設定時一併顯示（如 `claude-opus-4.5 (effort: high)`）；adapter 尚未回報或無 session 時 fallback 顯示靜態值。
- **正則 catastrophic backtracking 的正確防護層級**：不能靠「檔案與檔案之間的靜態 checkpoint 或靜態 regex guard」——爆炸發生在單一次 `test()` 呼叫內部、控制權永遠回不到 checkpoint，所以「處理完一個檔案就檢查一次」的做法在原理上就攔不到；正解是把 regex 執行隔離進 worker 並由外部逾時中止（2026-08-04）。
- **AI-canonical 的 `sync.ps1` 連動範圍**：`tools/pull.ps1`（拉 upstream 後自動跑 `sync.ps1 -Apply`）與 `tools/bootstrap.ps1`（新機器初始化）兩支腳本都呼叫 `sync.ps1`，因此改 `sync.ps1` 的 `$Targets` 會自動被這兩條路徑繼承，不需個別修改。詳見 [[ai-strategy]]（此 fact 因含「upstream」關鍵字被本 shard 的廣義關鍵字截走，內容實屬 AI-canonical 工具鏈範疇）。
- **參考 upstream 前先用 merge-base 確認哪些已在本地**（2026-08-06）：查證 telegram-kiro-bridge 的 fork 修正可能領先 upstream 時，發現 upstream/main 至今仍有 `authRequired = authMethods.length > 0` 誤判與方括號-only 的 effort 後綴 regex（見 [[bridge-acp]] 詳情），而四個 codex 相關 upstream commit 早已全數在本 fork——直接讀 upstream 程式碼前先跑一次 `git merge-base` 對照，能避免誤判「upstream 有我沒有的東西」而重工。

## 外部研究的證據等級標記（2026-08-07）

研究／吸收外部 repo 或文章時，筆記裡的每條主張都要標證據等級：**A 級**＝親自讀過原始檔案或原始碼查證過，**B 級**＝只根據摘要、README 或二手描述推得。這道標記是抗幻覺的紀律——分級本身會逼你察覺「這條其實沒查過」，也讓後續決策知道哪些前提還沒站穩；與「否定式主張要用二元探針覆核（如直接打 raw.githubusercontent 檔案 URL 看 200/404）而非採信摘要」（見 [[verification-diagnosis]]）互補。

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

## claude-mem plugin 診斷（2026-08-11）

`claude-mem` 是第三方記憶 plugin（與 bridge 自己的記憶系統是兩個獨立系統）。`settings.json` 的
`claude-mem@thedotmack: true` 已啟用、Bun runtime 已裝、plugin `scripts/` 目錄完整，但**沒有
worker 進程在跑**——初步懷疑是 chroma（向量庫）被停用導致，但**已被觀測推翻**：chroma 自 18:52
起停用，worker 47424 仍於 19:07 無聲死亡，∴ chroma 不是（唯一）成因，別再把「關掉 chroma」當修法。

## 兩則機制更正（2026-08-19）

- **auth-recovery 判斷 providerType 應用 `config.defaultProvider`，不可用 `peek()?.activeProvider`**：`replyWithAgentStartError` 的呼叫點都在 `sessions.get()` 的 catch 分支，`create(chatId, userId)` 不帶 providerType ⇒ 按構造 `activeType = config.defaultProvider`，用它就等於這次失敗的 create 用的值；`peek()` 結構上描述的是另一個 session。
- **`run_plan` specialist 不存在時的靜默降級已修**（commit a09f0ff）：降級改回結構化欄位（不解析中文字串）、警告送到使用者而非只 console.warn、具名模板降級停下來走確認鍵盤不直接派工、單槽清理改身分比對（`get(chatId) === entry`）避免 A 跑完清掉 B 的槓位。

## 相關工具

- **GitHubTool**：`G:\AI\GitHubTool`，Streamlit GitHub 組織管理 Web UI，主要操作 IGS-ARCADE-DIVISION-RD2 組織

## 相關

- [[uk-slot]] — 使用者的主要開發產品線
- [[ai-strategy]] — 跨模型策略與正典語料庫
