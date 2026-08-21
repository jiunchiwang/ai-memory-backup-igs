---
title: Bridge Session 生命週期與多 Session 管理
type: concept
created: 2026-07-08
updated: 2026-08-21
sources: [f_456de2, f_645ea3, f_046ffa, f_bafa71, f_bef432, f_ecaf0b, f_76faa7, f_42aed5, f_c73099, f_233da9, f_1d7bed, f_3dddec, f_634e34, f_a7d81f, f_827e53, f_ec382e]
history_sources: [f_20ed42]
---

# Bridge Session 生命週期與多 Session 管理

[[bridge-project]] 的 session 連續性走**兩層互補架構**：蒸餾記憶層（archive 摘要 + working state + facts）與 ACP 原生恢復層（session/load resume）。前者丟掉原始 context 靠蒸餾重建，後者保留完整 ACP context 原地接續。

## 蒸餾記憶層（2026-06-30 起）

- **Session 歸檔**：session 關閉時 `exportSession()` 寫結構化 JSON（turns/goal/stats/recentSummary）到 `session-archive-{chatId}.json`；新 session 以 `buildRestorationBlock()` 注入 preamble 後自動刪除。與 working-state 互補——WS 說做什麼，archive 說上下文在哪
- **設計決策**：per-chatId 單檔覆寫（排除 append-only 因為歷史已有 transcript MD）；恢復只注入 ~300 字摘要（排除全量 turn 注入因為 context 爆炸）；turn text 截斷 2000 字
- **`/reset clean`**（或 `/reset fresh`）：額外刪 archive + working-state，下次不帶上次上下文；預設 `/reset` 照舊歸檔

## ACP Session Resume（方案 A，2026-07-07）

- `ACP_SESSION_RESUME=true` 閘控（預設 off）；idle/crash/SIGINT 保留 registry 可 `session/load` 恢復（不重注 preamble）；`/reset`、`/agent`、`/restart`、`<<RESTART>>` 走 fresh 並清 registry（`shutdown` 帶 `clearResume` 參數區分）
- **選型理由**：只做 resume 不做 UI——restart 連續性 + idle 殺 process 省記憶體最實、避免與 goal/MoA/relay 單 session 假設互動（方案 B SessionStore+UI 等 A 跑穩再議 → 實際同日完成，見下）
- 生產機已於 2026-07-07 啟用並通過手動 e2e（context 暗號驗證）
- 實作計畫與三段 review 軌跡：bridge repo `docs/superpowers/plans/2026-07-07-acp-session-resume.md`（BC-1~5 + adapter 實測表）
- ✅ **cosmetic 已處理**（commit `55b3628`，2026-07-07 同日）：resume 後 `/context`/`/usage` 的 preamble breakdown 顯示 0 tok 是刻意的（preamble 凍在原 agent session 內、bridge 本 process 未重注），非 bug——`ChatSession` 加 `resumed` flag，UI 顯示層加註說明而非假造舊數字。舊版「cosmetic 待補」fact 措辭已過時（已於 2026-07-23 factlint 查證確認並刪除）

## SessionStore + /session 多 Session 管理（同日結案）

- 手動 e2e 全過：BC-3 雙 session 暗號互切不互漏、BC-5 `/reset` 只清 active、BC-2 v1→v2 registry migration、BC-8 claude↔kiro 跨 backend record 互切 model pin 自動連動
- 5 個 commit（8c65748→22cd8d5）已 push；README 已同步（commit 5233767：/agent、ACP_SESSION_RESUME、/session、/reset 新語意）

## Transcript 儲存路徑（四條，皆正常）

`/reset`、onBeforeClose（idle sweep/restart/shutdown）、crash（onUnexpectedExit）、`/session` park。idle sweep 為**靜默存檔**（只寫 console log，使用者決定不加 Telegram 通知）；`Saved → sessions/xxx` 訊息只在 `/reset` 當下仍有 live session 且有歷史時顯示。

## 使用場景偏好

日常用 `/reset`（快速清 context 重開）；`/handoff` 保留給較大任務完成、換機器、當天收工等需要記憶留存的場景。

## ACP session/load 與 session/resume 的規格分工（2026-08-05 新增）

ACP 協定規定：`session/load` 的 Agent **MUST** 用 `session/update` 重播整段對話歷史；`session/resume` 的 Agent **MUST NOT** 重播。兩者的 Request/Response 逐欄同形（`{sessionId,cwd,mcpServers}` → `{modes,configOptions}`）。

- `claude-agent-acp` 0.63.0 的 `resumeSession()` 與 `loadSession()` 呼叫同一個 `getOrCreateSession()`，唯一差別是 load 多一行 `replaySessionHistory()`——改走 resume 在 agent 端記憶復原上完全相同、無失憶風險（對照 opencode 的 resume 只讀 `limit:20`，不可推廣到所有 adapter）
- bridge 現用 `session/load` + `replaying` 抑制旗標丟棄整段重播——該設計與能力探測結果見 [[bridge-acp]]
- **兩個未接的免費訊號**：bridge 完全沒接 ACP 的 `usage_update` 與 `available_commands`（grep 0 命中），而 `claude-agent-acp` 的 resume 與 load 兩條路徑都會送 `available_commands`；bridge 的 resume 也沒用 `session/list` 做 pre-flight，現在是直接賭一發 `session/load`，失敗才 fallback 開新 session 並只寫 stderr（靜默降級）——追蹤於 [[bridge-roadmap]]
- **能力探測實測**（2026-08-05，`scripts/probe-acp-session-capabilities.mjs`，initialize-only raw probe）：`claude-agent-acp` 0.63.0 無條件宣告 `{additionalDirectories, close, delete, fork, list, resume}`；`kiro-cli` 2.16.1 整塊缺席（只有 `loadSession: true`）；codex-acp 當時因 npx 下載逾時未測完，屬「未知」不可讀成不支援
- **`replaying` 抑制旗標確定不可刪除，只能 capability-gate**：Kiro 未宣告 `resume` 且是使用者日常會切的 backend，`load + replaying` 是常態路徑而非邊緣 fallback；gate 條件為 `agentCapabilities.sessionCapabilities?.resume !== undefined`（ACP 用空物件表示能力存在，Kiro 是欄位不存在，可靠區分）
- **若改走 `session/resume` 的既知測試陷阱**：`scripts/check-session-resume.mjs` 現有「A2b replay updates suppressed」斷言會變成恆真綠燈（沒有 replay 可洩漏），必須改成雙臂 smoke（resume 臂 + load 臂各自 mutation test 確認會紅）——這是切換前必須先補的回歸網，不是切換後才發現的坑

## Session 退出路徑的意圖傳遞：物件旗標 vs 逐一 threading 參數

當一個「意圖」需要被多條退出路徑看見時，把它記成物件上的旗標（建立當下設定），不要逐一 threading 參數。2026-08-20 的一手實例：`/dream` 的維運 session 只在走 `drop({skipArchive:true})` 這條路時才不落盤，但 `shutdown()`／crash／`sweepIdle` 這些**不經 `drop()`** 的路徑會無條件 archive，把使用者剛存好的對話覆蓋掉；修法是在 `ChatSession` 上加 `maintenanceSession` 旗標（於 `create` 當下由入口參數設定），四個退出路徑各自檢查，取代把參數逐一 threading 到每個呼叫點。

可遷移判準：threading 參數只能保護「你記得改的那些呼叫點」，而退出路徑的完整清單是會成長的（新增一條 idle sweep 或 crash handler 時沒人會想到要傳這個參數）∴ 意圖屬於**物件的狀態**而不是**呼叫的參數**。⚠️ 邊界：旗標仍只保護讀它的那些 `if`，且旗標名與語意要對齊，不同開關（入口參數 vs 收尾參數 vs 由前者推導出的身分）不可混用。

**後續演進**：這個 `maintenanceSession` 旗標式 carve-out 後來被整套推翻——2026-08-21 改為無人格、非註冊的 **Dream Executor**，讓 `/dream` 從一開始就不進 `this.sessions` map、不接觸 archive／working-state／resume registry，而不是進場後再靠旗標抑制。完整取捨見 [[bridge-persona]]。

## 風險備忘

- **Replay 時序**：真 adapter 若在 session/load 回應後補送 replay update，歷史 `<<ASK>>` 等 token 有重放風險——保守 fallback 在計畫檔風險 #1

## 相關

- [[bridge-project]] — Bridge 本體架構
- [[bridge-acp]] — adapter 能力差異（loadSession capability：kiro ✅ / claude ✅ / codex 未判定）
- [[bridge-persona]] — Dream Executor 取代 maintenanceSession carve-out 的完整取捨（本頁只記舊旗標設計的可遷移教訓）
