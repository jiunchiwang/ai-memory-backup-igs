---
title: Claude Agent SDK（原 Claude Code SDK）研究：定位與四路對照、TypeScript API 面、能力清單、以及 bridge → claude-agent-acp → Agent SDK 的層次與 settingSources 影響
type: query
created: 2026-08-11
updated: 2026-08-11
sources:
  - https://code.claude.com/docs/en/agent-sdk/overview.md
  - https://code.claude.com/docs/en/agent-sdk/typescript.md
  - node_modules/@anthropic-ai/claude-agent-sdk/package.json（本機實查 0.3.220）
  - node_modules/@agentclientprotocol/claude-agent-acp/{package.json,dist/acp-agent.js}（本機實查 0.63.0）
---

# Claude Agent SDK 研究

2026-08-11 研究。起因是「研究一下 claude code sdk」，第一個發現就是**它改名了**。

相關頁面：[[bridge-acp]]（bridge 的三個 ACP backend 與 model pin）、
[[opencode-acp-implementation]]（另一個 ACP agent 的實作對照）、
[[agent-claude-opus46]]（settings 覆蓋 model pin 的未解懸案，第 5 節有可能的診斷工具）。

## 1. 命名：Claude Code SDK → Claude Agent SDK

「Claude Code SDK」是**舊稱**。現行名稱與套件：

| 語言 | 套件 |
|------|------|
| TypeScript | `@anthropic-ai/claude-agent-sdk` |
| Python | `claude-agent-sdk` |

官方文件：`code.claude.com/docs/en/agent-sdk`。
**只有 Python 和 TypeScript 有 library**；其他語言官方建議把 CLI 當 subprocess 跑
（`-p` + `--output-format json`）。

## 2. 定位：四路對照（最容易搞混的地方）

一句話定義：**把 Claude Code 本身當成 library** —— 同一套 agent loop、同一組內建
工具、同一份 context 管理，跑在你自己的 process 裡。

| 需求 | 該用 | 差別 |
|------|------|------|
| 要 agent 但不想自己寫 tool loop | **Agent SDK** | harness 由 SDK 提供，你自己 host |
| 終端機互動 / 一次性任務 | Claude Code CLI | 同一核心，介面不同 |
| 直接打 API、自己寫 loop | Client SDK（`@anthropic-ai/sdk`） | 只有 API，無內建工具、無檔案系統 |
| 長時間／非同步、不想管 sandbox | Managed Agents（REST） | Anthropic 同時託管 loop 與 sandbox |

### ⚠️ Tool Runner ≠ Agent SDK

`client.beta.messages.tool_runner` 與 Agent SDK 都號稱「幫你跑 loop」，但：

- **Tool Runner** 屬於一般 Anthropic API SDK，**只跑你自己定義的工具**，沒有內建
  Read/Write/Bash/Grep，沒有檔案系統。
- **Agent SDK** 是完整的 Claude Code harness，內建工具全帶。

判準是**兩個獨立問題**：誰提供 harness / 誰提供部署。

| 方案 | harness | 部署 |
|------|---------|------|
| manual loop | 你 | 你 |
| Tool Runner | SDK（僅 loop） | 你 |
| **Agent SDK** | SDK（完整 Claude Code harness） | 你 |
| Managed Agents | Anthropic | Anthropic |

前三者都是自己 host；只有 Managed Agents 多了託管部署。

## 3. TypeScript API 面

進入點只有一個 `query()`，回傳 async generator：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Hello",
  options: { maxTurns: 3 }
})) { console.log(message); }
```

### 值得認識的 Options

- `systemPrompt` —— 字串，或 `{ type: 'preset', preset: 'claude_code', append?: string }`
  （沿用 Claude Code 本尊的 prompt 再追加）
- `settingSources: ('user'|'project'|'local')[]` —— **決定要不要載入 `.claude/` 與
  CLAUDE.md**。對 bridge 是承重欄位，見第 4 節
- `allowedTools` / `disallowedTools` / `permissionMode`
  （`default` / `bypassPermissions` / `plan` / `dontAsk`）/ `canUseTool` 回呼
- `mcpServers`、`agents`（程式化定義 subagent）、`agent`（主執行緒用哪個）
- `resume` / `forkSession` / `continue`、`cwd`、`model`、`hooks`、`abortController`

### Query 物件可中途操控

不只是 generator：`interrupt()`、`setModel()`、`setPermissionMode()`、
`mcpServerStatus()`、`supportedModels()`、`supportedAgents()`、`stopTask()`、`close()`。

### 其他 top-level helper

- `tool()` + `createSdkMcpServer()` —— 用 Zod schema 定義 **in-process** MCP 工具，
  不用另外開行程
- `startup()` —— 預熱 CLI subprocess，回傳 `WarmQuery`
- `listSessions()` / `getSessionMessages()` / `renameSession()` / `tagSession()`
- `resolveSettings()` —— 回傳 `{ effective, provenance }`，**可查出某個設定值是誰設的**

## 4. 能力清單與授權限制

內建工具（Read / Write / Edit / Bash / Glob / Grep / WebSearch / WebFetch）、Hooks、
Subagents、MCP、Permissions、Sessions、Plugins；**Skills / slash commands / memory
會自動從專案 `.claude/` 與 `~/.claude/` 載入**，與 Claude Code 一致。

⚠️ **授權**：Anthropic 不允許第三方產品（含 Agent SDK 蓋的 agent）提供 claude.ai
登入或吃 claude.ai 額度，除非事先核准；對外產品要走 API key。自用不受影響，但若要把
bridge 對外分享會咬人。

## 5. 與 telegram-kiro-bridge 的層次關係（本頁重點）

實測層次（2026-08-11 本機 `node_modules` 實查）：

```
telegram-kiro-bridge
  └─ @agentclientprotocol/claude-agent-acp  0.63.0   ← ACP 轉接層
       └─ @anthropic-ai/claude-agent-sdk    0.3.220  ← 本頁主角
            └─ Claude Code harness
```

∴ `/agent claude` 這條 backend **底下跑的就是 Agent SDK**，不是直打 API。

### settingSources 是寫死的

`dist/acp-agent.js` 內：

```js
const options = {
    systemPrompt,
    settingSources: ["user", "project", "local"],
```

bridge 的 `session/new` **不覆寫**它。兩個直接後果：

1. `~/.claude/CLAUDE.md` 與整條 `@import` 鏈**直達** bridge 的 agent，不管 cwd 在哪個
   專案 —— 這是政策不用靠 preamble 注入的機制。
2. 同一個 `'project'` source 也是**每 session spawn 19 個 MCP 行程**的來源。
   收 `settingSources` 能降到 0，代價是同時斷掉第 1 點。

**這兩件事是同一個開關的兩面，不是兩個獨立問題** —— 評估 MCP 行程精簡時必須一起算。

### ⚠️ 行號會漂移

那行的位置隨 adapter 版本移動（0.6x 時 3749，0.63.0 已到 4145）∴ **grep
`settingSources:` 而不是照行號跳**。同套件 `dist/index.js` 另有一處
`settingSources: []`，**用途未查證**，別與主路徑混淆。

## 6. 對 bridge 可能有用但未實測的四點

以下**只讀了 API 簽名，沒讀 SDK 實作、沒實跑**，等級為推論：

- `resolveSettings()` 的 `provenance` 可直接回答「這個設定是誰設的」——對
  [[agent-claude-opus46]] 那個「settings watcher 蓋掉 model pin」的懸案可能是現成診斷工具。
- `Query.setModel()` 能在 session 中途換 model；bridge 現在是重建 session 才能換 pin。
- `listSessions()` / `getSessionMessages()` 是官方讀 transcript 的路徑；bridge 目前
  自己解 `~/.claude/projects/<slug>/*.jsonl`。
- `startup()` 預熱可能與 bridge 自己的 `coreReady` / FIFO 暖機重疊。

## 7. 證據等級

| 節 | 等級 | 依據 |
|----|------|------|
| 1–4 | 🟢 A | 官方 docs 原文 |
| 5 | 🟢 A | 本機檔案 literal 引用 + `require()` 讀出版本 + `sed` 逐字確認 |
| 6 | 🟡 推論 | 僅讀 API 簽名，未實測 |

未查證項目：`dist/index.js` 那處 `settingSources: []` 的用途。
