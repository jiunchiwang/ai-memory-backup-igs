# QM 研究報告與 Bridge 借鏡計畫

> 研究日期：2026-08-04
> 目標：研究 Y Combinator 出品的 QM (yc-software/qm) 架構，提取可借鏡到 telegram-kiro-bridge 的設計模式

---

## 1. QM 專案概述

### 1.1 定位

**QM** 是 Y Combinator 出品的 **multiplayer agent harness**，專為「公司級」使用場景設計。與個人助理型 agent 不同，QM 讓公司員工各有獨立 workspace，又能在 Slack channel/project 裡協作。

- **GitHub**: https://github.com/yc-software/qm
- **Stars**: 9.7k
- **授權**: MIT

### 1.2 核心特性

| 特性 | 說明 |
|------|------|
| **Personal + Shared scopes** | 每人獨立 workspace，可在 channel 協作 |
| **Slack + Web 雙端** | 同一身份跨平台 |
| **Admin 控制** | Org 級設定、security posture、harness/model 白名單 |
| **Web apps** | 可發布內部 app 給特定人 |
| **Shared skills** | Skill 可共享、org 審核後推廣 |
| **Background work** | Cron 和 watch 背景執行 |

### 1.3 技術棧

- Runtime: Node.js + TypeScript
- HTTP: Fastify
- Persistence: PostgreSQL
- Web UI: Vite + Lit
- Slack: Bolt

---

## 2. 架構分析

### 2.1 整體架構

```
Postgres (sessions / memory / queue)
        ↕
 Headless Core（API + identity + policy + scheduler）
        ↕
   Agent Loop（可換 harness：Pi / OpenCode / Claude Code / Codex）
        ↕
   Per-scope Sandbox（files / tools / logged-in services）
```

### 2.2 關鍵設計原則

1. **Harness 抽象**：同一套 core 可以換底層 agent CLI（Pi、OpenCode、Codex、Claude Code），透過環境變數切換
2. **Scope 隔離**：每個人/每個 room 有獨立的 memory、files、keychain、crons、permissions、sandbox
3. **Durable by default**：不信任 process memory（藍綠部署會洗掉），所有持久狀態必須存 Postgres
4. **Plugins 架構**：Slack/Web UI/Admin/Portal 都是可選 plugin

---

## 3. Harness 抽象層深入分析

### 3.1 核心 Interface

```typescript
export interface Harness {
  profile: HarnessAdapterProfile;    // 身份宣告
  turns: HarnessTurnController;       // 執行對話
  models: HarnessModelUtilities;      // 輔助功能
  tools: HarnessToolPresentation;     // tool 名稱轉換
}
```

### 3.2 HarnessAdapterProfile — 能力宣告

```typescript
interface HarnessAdapterProfile {
  id: string;                              // "pi" | "claude" | "opencode" | "codex"
  controlTransport: HarnessControlTransport; // "in-process" | "sdk" | "http"
  toolTransport: HarnessToolTransport;       // "in-process" | "plugin" | "in-process-mcp"
  transcriptFormat: string;                  // "pi" | "claude-agent-sdk" | "opencode"
  capabilities: ReadonlySet<HarnessCapability>; // "abort" | "steer" | "images" | ...
}
```

**HarnessCapability 類型**：
- `abort` — 支援 mid-turn 取消
- `steer` — 支援 mid-turn 插話
- `images` — 支援圖片輸入
- `thinking-level` — 支援 thinking level 調整
- `fast-mode` — 支援 fast mode
- `provider-sessions` — 支援 provider session 管理

### 3.3 四個 Harness Adapter 比較

| 面向 | Pi | Claude | OpenCode | Codex |
|------|----|----|----------|-------|
| **controlTransport** | in-process | sdk | http | http |
| **toolTransport** | in-process | in-process-mcp | plugin | — |
| **底層** | `@earendil-works/pi-coding-agent` | `@anthropic-ai/claude-agent-sdk` | OpenCode CLI + HTTP server | Codex CLI |
| **capabilities** | abort, steer, images, thinking-level, fast-mode, provider-sessions | abort, steer, images, thinking-level, fast-mode | abort, steer, images, provider-sessions | — |
| **工作目錄** | 每 turn 建 tmpdir jail | 每 turn 建 tmpdir jail | 共用 jail + per-session | — |

### 3.4 Harness Router — 動態路由

```typescript
function createHarnessRouter(
  adapters: ReadonlyMap<HarnessId, Harness>,  // 所有已註冊的 harness
  utility: Harness,                            // 共用的輔助 harness
  resolve: (input) => RuntimeChoice,           // 選擇邏輯
): Harness
```

關鍵邏輯：
- `resolveRuntimeChoice()` — 根據 org config → scope config → turn request 三層決定用哪個 harness/model
- Session 切換處理 — 同一 session 換 harness 時，先 reset 舊的再 reset 新的
- Approved harness 過濾 — org admin 可限制哪些 harness 可用

### 3.5 HarnessModelUtilities — 輔助 LLM 任務

| 方法 | 用途 |
|------|------|
| `shouldRespond?` | 偵測是否該回覆（Slack ambient listening） |
| `compactHistory?` | 壓縮對話歷史 |
| `contextTokenBudget?` | 回報可用 context 額度 |
| `oneShot?` | 單次 prompt（不帶 tool） |
| `judge?` | 用輕量 model 做分類判斷 |
| `screenSecurity?` | 安全篩選外部內容 |
| `pickAckEmoji?` | 選 emoji 反應（Slack 用） |
| `generateTitle?` | 生成對話標題 |
| `summarizeApproval?` | 摘要待審核指令 |

### 3.6 Tool Bridging 機制

QM 的 tool 不是直接暴露給各 harness，而是透過 **PiTools** 統一定義後橋接：

```typescript
function createPiTools(ref: ToolContextRef, options: PiToolsOptions): BridgedTool[]
```

每個 harness 再做名稱轉換：
- **OpenCode**：`execute` → `workspace_execute`、`read` → `workspace_read`
- **Claude**：透過 MCP server 掛 `mcp__qm__<tool>`

這讓 **tool 定義只寫一次**，各 harness 自動適配。

---

## 4. CLI 接入方式比較

### 4.1 QM 的做法

| Harness | 接入方式 | 說明 |
|---------|---------|------|
| **Pi** | in-process（API） | 直接 import SDK，跑在同一個 Node process |
| **Claude** | SDK（spawn CLI） | 用 SDK spawn `claude` binary 並控制 |
| **OpenCode** | HTTP（CLI server） | spawn `opencode serve` 啟動 HTTP server |
| **Codex** | HTTP（CLI server） | spawn CLI 再透過 HTTP |

### 4.2 HTTP Server vs stdio JSON-RPC

| 面向 | stdio JSON-RPC（bridge 用） | HTTP server（QM 用） |
|------|----------------|------------------|
| **連線方式** | 父進程的 stdin/stdout pipe | TCP socket（localhost:port） |
| **生命週期** | 父進程 spawn 時自動建立 | 需要等 server ready、管理 port |
| **多 client** | 1:1 | 1:N |
| **Debug 難度** | 較難 | 較易（可用 curl） |
| **跨機器** | 不行 | 可以 |

### 4.3 QM 選 HTTP 的理由

1. **Event streaming** — SSE 推 streaming delta，HTTP 天生支援
2. **併發請求** — 同時 abort + steer + prompt，HTTP 天然支援
3. **Bridge plugin** — QM 的 tool bridging 另開 HTTP server 讓 CLI 回打

### 4.4 Bridge 不換的理由

stdio JSON-RPC 對 bridge 的場景夠用：
- 單一 Telegram chat → 單一 ACP session，不需要多 client
- Streaming 靠 ACP 的 `session/update` notification
- 沒有跨機器連同一個 CLI 的需求

---

## 5. 安全模型

### 5.1 三種 Security Posture

| Posture | 行為 |
|---------|------|
| **strict** | 每個 tool call 都暫停等人核准 |
| **auto**（預設）| classifier 篩外部資料，通過才送 model |
| **dangerous** | 無篩選、無暫停 |

### 5.2 其他安全機制

- **Command policy**：預宣告的命令審核規則（如擋 `rm -rf`）
- **Credential scope**：憑證只在授權 scope 內可見
- **Audit log**：所有 security-relevant action 都記錄
- **npm 7-day cooldown**：新套件版本需 7 天熟化期才能進 lockfile

---

## 6. 與 telegram-kiro-bridge 的比較

| 面向 | QM | telegram-kiro-bridge |
|------|----|-----------------------|
| **用戶規模** | 公司 org（多人 + scope 隔離） | 單人 + specialist 分身 |
| **前端** | Slack + Web UI | Telegram |
| **Harness 切換** | 環境變數熱換 | `/agent` 切 ACP + `/model` 切 Direct API |
| **Session 持久化** | Postgres | JSON 檔 + ACP session/load |
| **Skill 系統** | scope-owned + grant 共享 + org 審核 | SKILL.md junction + 正本 repo |
| **安全 posture** | 3 級（strict/auto/dangerous） | 無分級，依賴 agent guardrail |
| **Cron/排程** | 內建 `cron/` 模組 | `schedules.json` + bridge 排程 |
| **輔助 LLM** | `HarnessModelUtilities` 9 個方法 | 分散各處（local-llm、embed-router） |

---

## 7. 借鏡計畫：Capability Set 宣告

### 7.1 現況問題

Bridge 的 ACP adapter 能力差異是 **執行期動態偵測 + 硬編碼判斷**，散落各處：

```typescript
// acpClient.ts
const hasLoadSession = initResult.capabilities?.includes("loadSession");

// sessionManager.ts
if (backendId === "claude") { /* Claude 特有邏輯 */ }

// run-prompt.ts
const mcpAvailable = await probeMcpTool("ask");
```

**問題**：
1. 每個消費端自己偵測，邏輯重複且不一致
2. 新增能力時要改多處
3. 沒有單一 source of truth
4. Specialist/Relay 繼承能力時更混亂

### 7.2 設計方案

#### 7.2.1 定義 Capability 類型

```typescript
// src/provider/capabilities.ts

export type AdapterCapability =
  // Session 管理
  | "session-load"        // 支援 session/load 恢復
  | "session-multi"       // 支援多 session 並存
  
  // Model 控制
  | "model-pin"           // 支援 configOptions model pin
  | "effort-pin"          // 支援 reasoning effort 設定
  | "thinking-level"      // 支援 thinking level 調整
  
  // Streaming
  | "streaming"           // 支援 session/update streaming
  | "cancel"              // 支援 mid-turn cancel
  | "steer"               // 支援 mid-turn steer
  
  // MCP
  | "mcp-bridge-actions"  // 載入 bridge-actions MCP
  | "mcp-memory"          // 載入 memory MCP
  | "mcp-google"          // 載入 google MCP
  
  // 媒體
  | "images"              // 支援圖片輸入
  | "files"               // 支援檔案附件
  
  // 進階
  | "sub-agents"          // 支援內建 sub-agent
  | "fast-mode";          // 支援 fast mode

export interface AdapterProfile {
  id: string;
  displayName: string;
  capabilities: ReadonlySet<AdapterCapability>;
  defaultModel?: string;
  authMethods?: string[];
}
```

#### 7.2.2 Adapter Profile 宣告

```typescript
// Kiro
export const KIRO_PROFILE: AdapterProfile = {
  id: "kiro",
  displayName: "Kiro CLI",
  capabilities: new Set([
    "session-load", "session-multi", "model-pin", "effort-pin",
    "streaming", "cancel",
    "mcp-bridge-actions", "mcp-memory", "mcp-google",
    "images", "files",
  ]),
  defaultModel: "claude-sonnet-4",
};

// Claude Code
export const CLAUDE_PROFILE: AdapterProfile = {
  id: "claude",
  displayName: "Claude Code",
  capabilities: new Set([
    "session-load", "model-pin", "effort-pin", "thinking-level",
    "streaming", "cancel", "steer",
    "mcp-bridge-actions", "mcp-memory",
    "images", "sub-agents", "fast-mode",
  ]),
  defaultModel: "claude-sonnet-4",
  authMethods: ["oauth", "api-key"],
};

// Codex
export const CODEX_PROFILE: AdapterProfile = {
  id: "codex",
  displayName: "Codex CLI",
  capabilities: new Set([
    "streaming", "cancel",
    "mcp-bridge-actions", "mcp-memory",
  ]),
  defaultModel: "o3",
};
```

#### 7.2.3 Runtime 驗證

```typescript
export async function resolveCapabilities(
  declared: AdapterProfile,
  initResult: AcpInitResult,
): Promise<ReadonlySet<AdapterCapability>> {
  const verified = new Set(declared.capabilities);
  
  // 宣告有但 runtime 沒有 → 移除
  if (verified.has("session-load") && !initResult.capabilities?.includes("loadSession")) {
    verified.delete("session-load");
  }
  
  // runtime 有但宣告沒有 → 加入（新版 CLI）
  if (!verified.has("steer") && initResult.capabilities?.includes("steer")) {
    verified.add("steer");
  }
  
  return verified;
}
```

#### 7.2.4 消費端改用統一查詢

```typescript
// Before
if (this.initResult?.capabilities?.includes("loadSession") && config.sessionResume) { ... }

// After
if (this.hasCapability("session-load") && config.sessionResume) { ... }
```

### 7.3 改善效果

| 痛點 | 現況 | 用 Capability Set 後 |
|------|------|---------------------|
| MCP fallback 判斷 | `probeMcpTool()` 每次 probe | 啟動時解析，直接查 Set |
| session/load 支援 | 偵測 `initResult.capabilities` | 查 `hasCapability("session-load")` |
| model pin 能力 | 偵測 `configOptions` | 查 `hasCapability("model-pin")` |
| Specialist 繼承 | 不清楚繼承哪些 | Profile 明確宣告或繼承 |
| Preamble 條件注入 | 硬編碼 `if (backendId === "claude")` | `if (hasCapability("sub-agents"))` |
| 文件同步 | 各 adapter 差異只在腦中 | Profile 就是 source of truth |

### 7.4 Preamble 條件注入

```typescript
// memory.ts buildPreamble()

if (capabilities.has("steer")) {
  sections.push(`[Steer support]
Agent supports mid-turn steering. User can send follow-up messages while you're working.
[End steer]`);
}

if (capabilities.has("sub-agents")) {
  sections.push(`[Sub-agents]
You have built-in research/code/consult sub-agents. Use them for bounded delegation.
[End sub-agents]`);
}

if (!capabilities.has("mcp-bridge-actions")) {
  sections.push(`[Legacy token fallback]
MCP bridge-actions unavailable. Use <<ASK:...>>, <<SEND_FILE:...>> tokens instead.
[End legacy token]`);
}
```

### 7.5 實作優先級

| 階段 | 內容 | 收益 |
|------|------|------|
| **P0** | 定義 `AdapterCapability` type + 三個 adapter profile | 建立 source of truth |
| **P1** | `resolveCapabilities()` + `hasCapability()` helper | 統一查詢入口 |
| **P2** | 改寫現有 ad-hoc 判斷 | 消除散落的偵測邏輯 |
| **P3** | Preamble 條件注入 | 讓 agent 知道自己能做什麼 |
| **P4** | Specialist profile 繼承 | 分身能力明確化 |

---

## 8. 其他值得借鏡的設計

### 8.1 Tool Bridging 統一層

- 現況：bridge 的 `bridge-actions` MCP 只服務 agent→bridge 方向
- QM：PiTools 是雙向統一，core 定義一次、各 harness 自動適配
- 可考慮：讓 MCP tool 定義也有類似的 adapter 轉換層

### 8.2 HarnessModelUtilities 整合

- 現況：輔助 LLM 功能（分類、壓縮、標題、security screen）分散在 `local-llm.ts`、`embed-router.ts`、各處
- 可考慮：收進 Provider interface 的 `utilities` 子物件

### 8.3 tmpdir Jail 隔離

- 現況：bridge 共用 CWD，agent 理論上可以改到 bridge 的檔案
- QM：每個 turn 都在獨立 tmpdir 跑
- 評估：對單人場景收益有限，暫不優先

### 8.4 三層 Config 覆蓋

- 現況：`/agent` 只有單層（acp-providers.json）
- QM：org → scope → turn 三層覆蓋
- 可考慮：per-specialist 或 per-chat override

---

## 9. 不適用的設計

| 設計 | 為何不適用 |
|------|-----------|
| Postgres 持久化 | Bridge 是 file-based，低運維成本 |
| Web apps 發布 | 單人用途過重 |
| Slack org workspace | 與個人 Telegram bot 場景不同 |
| Scope 隔離 | Bridge 是單人使用，不需 multi-tenant |

---

## 10. 參考連結

- [QM GitHub](https://github.com/yc-software/qm)
- [QM SECURITY.md](https://github.com/yc-software/qm/blob/main/SECURITY.md)
- [QM AGENTS.md](https://github.com/yc-software/qm/blob/main/AGENTS.md)
- [Harness 核心 interface](https://github.com/yc-software/qm/blob/main/src/harness/harness.ts)
- [Harness Router](https://github.com/yc-software/qm/blob/main/src/harness/harness-router.ts)
