---
title: OpenCode 的 ACP 實作研究：stdio+HTTP 雙層架構、完整方法表、capabilities 宣告、session/update 與 tool kind 對映、permission fail-closed 設計，以及接成 bridge 第四個 backend 的相容性分析（含 authMethods 恆非空的誤判陷阱）
type: query
created: 2026-08-05
updated: 2026-08-05
sources:
  - https://opencode.ai/docs/acp/
  - https://zed.dev/acp/agent/opencode
  - https://github.com/sst/opencode（dev branch，packages/opencode/src/acp/*）
---

# OpenCode 的 ACP 實作研究

2026-08-05 深入研究 OpenCode 的 ACP（Agent Client Protocol）支援。官方文件只有一頁
（`opencode.ai/docs/acp`），內容偏設定範例，**真正的規格在原始碼**。本頁結論來自直接
讀 `sst/opencode` 的 `dev` branch（v1.18.13）：
`packages/opencode/src/acp/{agent,service,session,event,tool,permission,usage,error}.ts`
＋ `packages/opencode/src/cli/cmd/acp.ts`。

相關頁面：[[bridge-acp]]（bridge 的 ACP adapter 配置與能力偵測陷阱）、
[[bridge-project]]（bridge 整體架構）、[[verification-diagnosis]]（本頁的事實主張驗證法）。

## 1. 執行模型：stdio 前臉 + HTTP 後腦

`opencode acp` **不是**另一套 agent 實作，而是 opencode 自己 HTTP API 的薄轉譯層：

1. `Server.listen()` 起一個本機 HTTP server
2. `createOpencodeClient({ baseUrl: http://host:port })` — 自己當自己的 client
3. stdin/stdout 包成 `ndJsonStream` → `AgentSideConnection`（官方 `@agentclientprotocol/sdk`）

ACP 層每個方法都轉成一次內部 HTTP 呼叫
（`sdk.session.create / get / messages / prompt / command / abort`）。

**與 bridge 的對照**：這正是 bridge 在 2026-08-04 QM 研究時排除掉的架構。opencode 之所以
兩層都做，是因為它要同時餵 TUI、web、ACP 三種前端；bridge 是單一 Telegram chat 對單一
session，多一層 HTTP 沒有收益。此發現**反向佐證**了 bridge 選 stdio JSON-RPC 的原判斷。

## 2. 完整方法表（`acp/agent.ts`）

實作的 ACP `Agent` interface 全員：

| 方法 | 備註 |
|---|---|
| `initialize` / `authenticate` | ✅ |
| `newSession` / `loadSession` / `closeSession` | ✅ |
| `listSessions` / `resumeSession` | ✅ 分頁 cursor，limit 100 |
| `unstable_forkSession` | ✅ 帶 `unstable_` 前綴 |
| `setSessionConfigOption` / `setSessionMode` / `unstable_setSessionModel` | ✅ |
| `prompt` / `cancel` | ✅ |

比 bridge 現用的三個 adapter 都完整——`listSessions` / `fork` / `close` 是 Kiro CLI 與
claude-agent-acp 都沒提供的。

## 3. initialize 宣告（`service.ts:112`）

```
protocolVersion: 1
agentCapabilities:
  loadSession: true
  mcpCapabilities: { http: true, sse: true }          // stdio 是 ACP baseline
  promptCapabilities: { embeddedContext: true, image: true }   // 無 audio
  sessionCapabilities: { close, fork, list, resume }
authMethods: [ "Login with opencode" ]
agentInfo: { name: "OpenCode", version: <安裝版號> }
```

巧思：client 若在 `clientCapabilities._meta["terminal-auth"]` 宣告支援，opencode 會回一個
可執行的登入指令（`opencode auth login` + label），讓編輯器直接開 terminal 跑登入流程。

## 4. 串流與工具對映

`event.ts` 訂閱 opencode 內部事件流，翻成 ACP `session/update`：

- `agent_message_chunk` / `agent_thought_chunk` / `user_message_chunk`（reasoning 走 thought）
- `tool_call` + `tool_call_update`（含 `locations`、`rawInput`；edit 類附 diff、附圖）
- `usage_update`（`usage.ts` 分算 input / output / reasoning / cache read+write，並累計 USD 成本）
- `available_commands` 與 configOptions 同步

`tool.ts` 把 opencode 工具名對映成 ACP 的 `kind`：
`execute / fetch / edit / search / read / think / other`。

**turn 邊界**用 `runUntilIdle()`：等內部事件 `status.type === "idle"` 才 resolve prompt，
不是等 HTTP 回應返回。`stopReason` 有 `end_turn` / `cancelled` / `max_tokens` / `refusal`；
`cancel` → `sdk.session.abort()`。

## 5. Permission：fail-closed 設計

`permission.ts` 三個固定選項：`allow_once`（once）／`allow_always`（always）／
`reject_once`（reject）。**client 沒宣告 `requestPermission` 能力時一律 reject**，
不是預設放行——這個方向是對的（安全預設）。

## 6. 接成 bridge 第四個 backend 的相容性

正面：`configOptions` 的 id 是 `model` / `effort` / `mode`，**與 bridge 讀
claude-agent-acp 的形狀完全一致**（`acpClient.ts:931` 那條路徑）；加上
`loadSession: true`，理論上 `ACP_AGENT_COMMAND=opencode acp` 可直接插成第四個 backend，
`/model` pin 與 session resume 都對得上。

### ⚠️ 確定會踩的不相容：authMethods 恆非空

事實主張驗證（強：A 級雙邊證據 + 反例通過）：

- 🟢 A 級：`service.ts:96-131` — `authMethod` 物件**無條件建構**，`authMethods: [authMethod]`
  恆為長度 1；只有 `_meta` 隨 client 的 `terminal-auth` 能力變化，**沒有任何
  「已登入則省略」的分支**。
- 🟢 A 級：`acpClient.ts:481` `authRequired = authMethods.length > 0`；同檔 `:459-462`
  註解記錄 claude-agent-acp 與 kiro-cli **已登入時回 `[]`**。
- 🔴 反例檢查：若 opencode 會依登入狀態變動，`initialize` 內應查 auth 狀態 → 實際
  `initialize` 完全沒碰任何 auth 查詢，只有 `authenticate()` 在驗 `methodId`。反例不成立。

後果：bridge 會**永久誤判「需要登入」**→ `transient-retry` 被關掉，且 prompt 失敗時
多掛一句誤導的「請先登入」提示。要接的話得在 `authRequired` 判定上加 per-backend 例外。

**誠實邊界**：以上為讀碼推論，**尚未實跑 `opencode acp` 驗證**。

## 7. 文件生態的雷

- 官方唯一入口是 `opencode.ai/docs/acp`。已知限制：`/undo`、`/redo` 走 ACP **不支援**。
- `open-code.ai`、`opencode.asia`、`opencode-tutorial.com` 都是 SEO 克隆站，**非官方**。
- `bgauryy/open-docs` 的 `11-acp-protocol.md` 聲稱「streaming 未實作、cancellation 未實作、
  檔案是 `acp/agent.ts` + `acp/client.ts`」——**與原始碼矛盾**（`client.ts` 不存在、
  `event.ts` 整支就是 streaming）。該份已過時，不要引用。
- GitHub `api.github.com` 對 WebFetch 回 403、本機 `gh` 未認證；可行路徑是
  `raw.githubusercontent.com`（注意 opencode 預設 branch 是 `dev`，`main` 會 404）。

## 8. 借鏡：load vs resume（已 probe 定案，2026-08-05）

讀 opencode 的 `resumeSession` / `forkSession` 本體後發現，**最值得借鏡的不是「多幾個方法」，
是它把 session lifecycle 切開的方式**：

| 方法 | 取歷史 | 重播給 client |
|---|---|---|
| `loadSession` | 全量（無 limit） | ✅ `replayMessages()` |
| `resumeSession` | `limit: 20` | ❌ **不重播** |
| `forkSession` | `limit: 20` | ✅ 重播（← 與 load 不一致，疑似 opencode 疏漏，別照抄）|

ACP spec 的 normative 用語證實這是協定分工而非實作偏好：load 「**MUST** replay the entire
conversation」、resume 「**MUST NOT** replay the conversation history」。

`scripts/probe-acp-session-capabilities.mjs`（本次新增，initialize-only raw probe）實測三個
backend：claude-agent-acp 0.63.0 全宣告、**kiro-cli 2.16.1 整塊缺席**、codex-acp 未測完。
∴ bridge 的 `replaying` 抑制旗標**不可刪**，只能 capability-gate（分支數=2）。

完整結論、零改動紅利與必辦的雙臂 smoke 見 [[bridge-roadmap]] 的 Pending 首條。

**狀態（2026-08-05）**：已存檔，暫不實作。未辦的還有：接第四個 backend（含
`authMethods` 恆非空的判定修正）、實跑 `opencode acp` 驗證第 6 節推論。
