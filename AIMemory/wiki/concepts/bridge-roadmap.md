---
title: Bridge Roadmap
type: concept
created: 2026-07-28
updated: 2026-08-05
sources: []
---

# Bridge Roadmap

## Pending

- [ ] **resume 成功但遠端沒有 preamble 的那一格**（bridge-session）：`sessionManager` 在 `if (resumed)` 無條件 `memoryPreamble = ""` + `preambleInjected = true`，但 **resumable 記錄在 create 當下就寫**（`saveResumable`，fire-and-forget），而 preamble 要到**第一個 prompt** 才注入（`run-prompt.ts` 的 `preambleInjected` 分支）。∴「建好 ACP session、還沒送任何 prompt 就重啟 bridge」這一格：`session/load` 成功、本地清空 preamble，但遠端 agent **從來沒收到過** preamble ⇒ 該 session 之後永遠在沒有記憶前言的狀態下跑。既有行為，2026-08-19 由 K2/K3 的第三輪跨 vendor 覆核（codex gpt-5.6-sol）在覆核 preamble 掃描接線點時順帶查出，**刻意不在該 commit 修**（會動到 resume／重注入契約，該獨立設計）。修法要考慮的：清空的條件應該是「遠端確實持有 preamble」而不是「resume 成功」，而 bridge 手上沒有那份文字 ∴ 可能要靠 `saveResumable` 記一個 `preambleDelivered` 旗標（在首個 prompt 注入後才寫）。註解留在 `sessionManager.ts` 掃描點；commit `63fabd2` 的 body 也記了一份
- [ ] **`session/resume` 取代 `session/load`（capability-gated）**（bridge-acp / bridge-session）：ACP spec 規定 `load` **MUST** 重播歷史、`resume` **MUST NOT**；bridge 只走 load，所以有 `replaying` 抑制旗標（`acpClient.ts:472` 宣告、`:732` 丟棄 replay 期間的 `session/update`）。**已 probe 定案（2026-08-05，`scripts/probe-acp-session-capabilities.mjs`）**：claude-agent-acp 0.63.0 宣告 `sessionCapabilities: {additionalDirectories, close, delete, fork, list, resume}`；kiro-cli 2.16.1 **整塊缺席**（`loadSession: true` 但無 sessionCapabilities）；codex-acp 未測完。∴ **分支數=2，`replaying` 不可刪**——它是 Kiro 路徑的常態機制而非邊緣 fallback。gate 條件 `agentCapabilities.sessionCapabilities?.resume !== undefined`（ACP 用空物件表示能力存在，Kiro 是欄位不存在，可靠區分）。**零改動紅利**：`ResumeSessionRequest/Response` 與 Load 版逐欄同形（`{sessionId,cwd,mcpServers}` → `{modes,configOptions}`），`captureSessionConfig` 與呼叫端不用改；claude-agent-acp 的 `resumeSession()` 與 `loadSession()` 共用同一個 `getOrCreateSession()`、只差一行 `replaySessionHistory()`，∴ agent 端記憶復原相同、無失憶風險。**收益誠實說**：省的是本來就被整段丟棄的 replay 流量 + resume 延遲，**無功能增益**，價值在拆掉結構性 hack。⚠️ **必辦**：`scripts/check-session-resume.mjs:119` 的 `A2b replay updates suppressed` 走 resume 後會變恆真綠燈（沒有 replay 可洩漏）——smoke 必須改雙臂（resume 臂 + load 臂各自 mutation test），否則命中測試鎖錯對象的模式。細節見 [[opencode-acp-implementation]]
- [ ] **接 `usage_update` / `available_commands`**（bridge-acp）：兩者 bridge 目前整包忽略（grep 0 命中）。`usage_update` 是 agent 側算好的 input/output/reasoning/cache 分項 + 累計成本（比自估準）；`available_commands` 是 agent 自報的 slash command 清單（現在 `/help` 列不出 agent 側指令）。claude-agent-acp 的 resume 與 load **兩條路徑都會**送 `available_commands`（`sendAvailableCommandsUpdate`）
- [ ] **resume pre-flight 用 `session/list`**（bridge-session）：現在 resume 是直接賭一發 `session/load`，失敗才 fallback 開新 session（`acpClient.ts:866` 只寫 stderr）——使用者以為續上了其實是新 session，是靜默降級。claude-agent-acp 已實作 `listSessions`（回 sessionId/cwd/title/updatedAt），可先比對 sessionId 是否還在 agent 側再決定，把降級變可觀測。Kiro 未宣告 list → 同樣要 capability gate

- [ ] Expandable blockquote / Rich Message `<details>` 支援（bridge-streaming）：HTML fallback path 需在 format-html.ts 識別 `>...\|\|` 結尾並輸出 `<blockquote expandable>`；Rich Message path 可能天然支援或改用 `<details>` 標籤（有 summary 標題更強）；待實測 Rich Markdown 是否認 `||` 語法
- [ ] Footer 組裝層 smoke 覆蓋（bridge-specialist / bridge-acp）：`proxyUsageFooter()`（proxy-finalize.ts）與 `getProxyModelInfo()`（specialist.ts）零覆蓋，`check-acp-model-truth.mjs` 只守到 provider 層的 verifiedModelInfo 語意；bb2e265（2026-07-29 footer 補 model/effort + `(pin)` 標註）留下的測試債，Fable5 覆核 LOW-2 點名。**已有的**：fake-acp-agent.mjs 兩種 model 回報形狀（`FAKE_ACP_CONFIG_OPTIONS`=claude、`FAKE_ACP_MODELS_SHAPE`=Kiro 回音形狀）、check-specialist.mjs 的 temp specialists.json pattern、runner 自動掃 check-*.mjs 免註冊。**唯一摩擦**：`spawnOrReuse` 是 module-private，外部只能經 `promptProxy` 填 `instances`，而它第一輪會連帶跑 preamble + enrichment。**未實測的假設**：那三者的 `.catch` 兜底在 temp MEMORY_DIR 下會不會乾淨降級——這是工時從「一支 ~130-180 行小 smoke」擴大的唯一變數，動工前先花 5 分鐘探測。要鎖的 BC：無 proxy 回空字串 / model+effort 皆空只印 specialist 名（回歸保護）/ 未 spawn 走 entry pin 標 `(pin)` / claude 形狀 spawn 後不標 / Kiro 形狀（model verified、effort 來自 pin）要標（鎖 LOW-1 修法）/ closeInstance 後退回 pin 重新標。**不含**主 agent footer 側（run-prompt.ts 的 modelSuffix 埋在 runPrompt 中段、無可測接縫，要先抽函式，另一筆帳）

## In Progress

## Done
