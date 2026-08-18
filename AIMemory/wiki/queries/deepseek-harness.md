---
title: DeepSeek Harness (dsh) 借鏡評估：源碼層 49 個 package 盤點、packages/acp 是 agent 側但對 bridge 不可用（無 MCP capability、無 session/load）、2026-08-17 報告的證據等級更正
type: query
created: 2026-08-18
updated: 2026-08-18（第二輪：追查 compaction/spill，**更正本頁初版「bridge 完全沒有對應物」為誤**——bridge 有 context-assembly／context-telemetry／70% 警告三塊，真缺口只有「70% 警告是一次性的」）
status: 借鏡評估已結案——ACP backend「不可用（能力缺口非成熟度）」；compaction／spill 皆不做（bridge 不擁有 context ＋ 成本不對稱方向相反）；唯一建議項＝警告觸發模型分層
sources:
  - https://github.com/deepseek-ai/deepseek-harness
  - https://api.github.com/repos/deepseek-ai/deepseek-harness（metadata 實查）
  - https://api.github.com/repos/deepseek-ai/deepseek-harness/contents/packages（目錄清單實查）
  - https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/README.md
  - https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/acp/README.md
  - https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/packages/acp/acp/README.md
  - ${MEMORY_DIR}/sessions/session-509424983-2026-08-17T20-11-45.md（2026-08-17 首輪研究報告全文）
---

# DeepSeek Harness (`dsh`) 借鏡評估

## 0. 這一輪為什麼要重看（前一份報告的證據等級被高估）

2026-08-17 已做過一份完整研究報告（架構、Cordis 核心、Plugin 分類、四種執行模式、Session 模型、bridge 對照），結論是三條軟性借鏡：**Effect disposal pattern（中）／Declarative capability composition（低）／Append-only projection（低）**。

但那一輪的**取材路徑**寫在 session log 裡：`GitHub raw 被 rate limit 了`、`看起來這個 repo 可能不存在或是私有的`——∴ 該報告是從**搜尋結果＋官方文件站**建起來的，**沒有讀到任何一行源碼**。它的架構敘述屬 B 級（二手轉述），而非它讀起來的那種確定語氣。

本輪只做三件事，不重推 Cordis 理論：① 用 GitHub API 驗基礎事實 ② 取**源碼層** package 盤點 ③ 追一個 08-17 完全沒提到、但對 bridge 最要命的東西——`packages/acp`。

> ⚠️ 首輪那份報告的「九大 Plugin 類別」是**文件站的分類法**，與下面的源碼佈局（49 個 package）不是同一套切法。兩者**刻意不合併**——文件分類 ≠ 源碼結構，硬併會生出一張兩邊都不成立的表。

## 1. 基礎事實（A 級 · GitHub API 原始欄位）

| 欄位 | 值 |
|---|---|
| description | `DeepSeek Harness: Everything is a Plugin.` |
| **default_branch** | **`master`**（不是 `main`——raw URL 打 `main` 一律 404，08-17 的「repo 可能不存在」誤判有一半是這個）|
| stargazers / forks / watchers | 149,717 / 15,341 / 624 |
| created_at / pushed_at | 2026-08-13T11:56Z ／ 2026-08-17T12:01Z |
| license / archived | MIT ／ false |
| **open_issues_count** | **0** ← 149.7k star 的 repo 不可能真的零 issue ∴ issues 應是關閉的。**上游問不到問題，源碼是唯一 oracle** |
| topics | `ai-agents` `cordis` `dsh` `dsh-plugin` |

README 自述（B+ 級，WebFetch 轉述並標為原文）：`developer preview`、`is iterating rapidly. **THERE WILL BE COMPATIBILITY-BREAKING CHANGES.**`

註：08-17 記的 147k★ 與本輪 149.7k★ 兩者都對，差一天的成長，不是矛盾。

## 2. 源碼層盤點（A 級 · contents API）

`packages/` 底下 **49 個目錄**。與 bridge 概念直接對位的挑出來：

| dsh package | bridge 的對應物 |
|---|---|
| `acp` | bridge 的 backend 介面（見 §3）|
| `mcp` | bridge 的 MCP 註冊（bridge-actions / memory）|
| `session` `session-query` | `sessionManager.ts` ＋ session archive |
| `subagent` `jobs` `schedule` `plan` `workflow` | specialist ／ `run_plan` ／ `<<SCHEDULE>>` |
| `skill` `goal` `todo` | `<<SKILL_USED>>` ／ `/goal` ／ TodoWrite |
| `hooks` `guard` | impact-gate ／ turn-lint |
| `compaction` `spill` | context 壓力處理（⚠️ 初版寫「bridge 沒有對應物」**為誤**，已於 §4 更正）|
| `sandbox` `e2b` `shell` `subprocess` `code-runtime` | 無（bridge 不是執行層）|
| `llm` `credentials` `identity` `settings` `preset` `bundle` | `acp-providers.json` ／ `.env` |
| 其餘 | `api` `attachment` `boot` `client` `context` `core` `examples` `extensions` `feedback` `fs` `host` `interaction` `lsp` `runtime-diagnostics` `sdk` `storage` `terminal` `test-support` `typert` `util` `web` `workspace` |

## 3. `packages/acp` —— 本輪核心，判定：**不可用**

### 3.1 它是哪一側（決定後面全部分支）

**agent 側（server）**。`packages/acp/README.md` 的原話：

> The ACP group exposes harness agents to programmatic clients over the Agent Client Protocol.

且明講 client 那一側在別處：`the matching out-of-process subagent *client* lives in subagent/subagent-acp`。

∴ 結構上 dsh **可以**被 bridge 當第四個 backend 驅動——與 [[opencode-acp-implementation]] 同一種形狀。

### 3.2 但實際契約擋住了（`packages/acp/acp/README.md`）

| 項目 | dsh-acp | bridge 需要什麼 |
|---|---|---|
| npm | `@deepseek-ai/dsh-acp` | — |
| 實作方法 | `initialize` `authenticate` `session/new` `session/prompt` `session/cancel` `session/update` `session/request_permission` | — |
| **`session/load`** | **明列不支援** | bridge 已 gate 在 `agentCapabilities.loadSession` 後、失敗自動 fallback `session/new`（`acpClient.ts:1020`, `:1035`）∴ **不會炸，但 `/session` resume 直接失去**，每次都變新 session |
| **MCP capability** | **`No session, editor, terminal, filesystem, or MCP capability is advertised.`** | ⛔ **這條是真正的 blocker**——bridge 在 `session/new` 與 `session/load` 都帶 `mcpServers` 陣列（`acpClient.ts:1026`, `:1043`），bridge-actions（ask／delegate／run_plan／send_file）與 memory MCP 全走這條。對方不宣告，這一整層等於不存在 |
| authMethods | 不宣告任何一種 | 與 [[opencode-acp-implementation]] 的「authMethods 恆非空陷阱」**方向相反**，這裡是恆空 |
| 啟動方式 | `pnpm --dir /path/to/deepseek-harness run demo:acp` | bridge 的 backend 是一行 command（見 `acp-providers.json`）。這是 **demo composition，不是打包好的 CLI 進入點** |
| 設定 | `provider` / `model` 兩個 optional 欄位，但可跑的組合兩者都要給 | — |

### 3.3 結論的形狀很重要

**不是「還太早、等它成熟」，是「能力面缺一塊 bridge 的承重結構」。** 成熟度會隨時間解決，capability 宣告不會自己長出來——除非 dsh 之後補 MCP 支援。∴ 這條的複查觸發條件很明確：**`packages/acp/acp/README.md` 裡那句 `No ... MCP capability is advertised.` 改掉的那天**，才值得重新評估，中間不必定期回看。

⚠️ 誠實邊界：以上 §3.2 的內容是 WebFetch 小模型讀該頁後的轉述（B+ 級），引號內為它標示的原文。**沒有讀 `packages/acp/acp/src/` 的實作**——「宣告不支援」與「傳了會怎樣（忽略／報錯）」是兩件事，後者未驗。要動手前必須先跑一次 raw ACP 探針（做法見 [[bridge-acp]]）。

## 4. `compaction` / `spill` 深入（2026-08-18 追查 · **更正本頁初版**）

### 4.0 ⚠️ 先更正自己

本頁初版寫「這是 49 個 package 裡唯一 bridge **完全沒有對應物**的一塊」——**那是錯的**，寫的時候沒查 `src/`。實查後 bridge 有兩塊對應物：

| bridge 既有 | 做什麼 | 等級 |
|---|---|---|
| `src/context-assembly.ts` | **注入側**預算：檢索候選（skill／memory／wiki／notebook／index）帶 `key` 去重、`priority`、`budget-exceeded` 裁切結果 | 🟢 A（讀原始碼）|
| `src/context-telemetry.ts` | **精確**使用率：吃 ACP 的 `usage_update`（used／size）或 Kiro `session_info`，非估算 | 🟢 A |
| `src/run-prompt.ts:793-815` | 70% 一次性警告：注入「建議收尾、`remember()` 存狀態、必要時 `<<RESTART:context budget>>`」 | 🟢 A |

真正缺的不是「對應物」，是**壓縮既有歷史**的能力——而那一塊有結構性理由（§4.2）。

### 4.1 dsh 兩個子系統實際在做什麼（🟡 B+ · WebFetch 轉述 `docs/subsystems/compaction.md` 與兩份 README）

**compaction**（四個 package 組成一條 seam）：`compaction`（seam ＋ event vocabulary）／`compaction-basic`（token 壓力偵測＋摘要 backend）／`compaction-tool-result-pruner`（**model-free** tool result 剪枝）／`command-compact`（人工指令）。

- **觸發兩條路**：自動（`CompactionTrigger` = `pressure` / `context-overflow`，跑在 `agent/pre-step`）＋ 明確（`compactNow()`，**低於壓力線也能叫**，用於 idle session 縮減）
- **保留**：tool-call/result 配對不拆、oversized turn 內已結束的 step、手動路徑上「摘要期間注入的 context」會活過 checkpoint
- **丟棄**：被摘要節點取代的表層節點；**turn 邊界不保證完整**
- **剪枝手法**：對超預算的 tool result **換掉文字中段**（留頭尾）、保 rich-block 順序、**按 Unicode code point 切**、非文字 block 不計成本
- ⚠️ **對 pinned／system 內容的保護：文件寫 ABSENT**

**spill**：超大 tool output 不進 inline，改為「持久化到外部 ＋ inline 只留 bounded preview ＋ retrieval locator」。`spill-local` 存 session-scoped 本地檔並註冊在 `ctx.spillStore`；`spill-policy` 是 **post-execution** 政策、掛在 tools 上。觸發門檻與取回機制文件皆 ABSENT。

### 4.2 決定性的不對稱：bridge 不擁有那個 context

**dsh 是 harness，bridge 是 harness 的 client。** 對話歷史活在 ACP agent（`claude-agent-acp` / `kiro-cli` / `codex-acp`）進程裡，bridge 只送 prompt、收 `session/update`。∴ **壓縮既有歷史結構上不是 bridge 能做的事**——而且擁有那層的人已經在做了（Claude Code 自己會在 context 壓力下 compact）。

⚪ **未驗**：ACP 有沒有任何 backend 暴露「觸發 compact」的介面。沒查過 ∴ 不把「bridge 至少能觸發」寫成可選項。

### 4.3 bridge 真正可控的兩塊 —— 都已有機制

**注入側**：`context-assembly.ts` 已預算化，無缺口。

**自家 MCP 工具的輸出**（bridge 自己產生、直接進 agent context 的部分）——逐檔實查（🟢 A）：

| MCP | 現況 | 判定 |
|---|---|---|
| `mcp-readonly.ts` | `MAX_READ_CHARS = 8000` ＋ 截斷註記；grep 有 cap ＋ timeout 註記 | ✅ 已有界 |
| `mcp-actions.ts` | 錯誤訊息 `slice(0, 600)` / `slice(0, 200)` | ✅ 已有界 |
| `mcp-memory.ts` | topic-shard 路徑**整份回傳、不看 `tail`**（工具說明明文如此，是刻意設計） | 🟡 已量測，非急件 |

**量測（🟢 A）**：最大 shard `adversarial-review` 31,578 chars ≈ 14.4k tok —— 在本 session 的 1M 視窗是 **1.44%**，在 200k backend 是 **7.2%**。單次呼叫，不是失控來源。

∴ **不建議**把 spill/pruning 套到 `list_facts`：**成本不對稱方向在這裡是反的**。dsh 防的是 tool output 撐爆 context；bridge 這條路上截斷的代價是**漏掉一條 fact → 重犯一個已記錄的失敗**，那比多花 1.4% 視窗貴得多。整份回傳是刻意的，判準沒有翻轉。

### 4.4 唯一真缺口：70% 警告是一次性的

`run-prompt.ts:794` 的 `session._budgetWarned` 一旦設起就**永久關閉** ∴ 過了 70% 之後、一路到死線之間**不會再有第二次提醒**。dsh 那邊對應的是「pressure 觸發是持續評估的、而且另有明確指令路徑」。這是完全落在 bridge 掌控內、且真的有缺的一件事。

**✅ 2026-08-18 已實作**（使用者裁決 A）：`_budgetWarned?: boolean` → `_budgetWarnedTier?: number`（記錄最高已觸發層級），70%／90% 各觸發一次；tiers 由高到低排列 ∴ 一次跨過兩層只給最急的 90% 那則、不補發 70%。90% 那則的語氣是硬停（不得再起新 tool call／子任務，先寫 `[WS]` 與 `remember()`、交付已完成部分、再 `<<RESTART>>`）。連動 `docs/usage-guide.html` 與 `docs/SPEC-context-telemetry-pty-observer.md`（後者已結案 ∴ 只追加變更紀錄、不改歷史條目）。

已 push（`b46b1a1` ＋ 覆核修正 `13e1e30`）。push 前的跨 vendor 覆核（`kiro-cli glm-5`，唯讀 `fs_read`，6m56s）出 4 條 finding、**1 條成立**：文件寫「用量達 70%」但程式碼判定是嚴格大於 ∴ 剛好 70.0% 不觸發——這是**既存**的敘事不精確（改動前的 `> 0.7` 與舊文件同樣不符），本次只是把它複製成兩層，處置為改文件不改行為。另 3 條為確認性（生命週期、無殘留、耦合宣稱成立且無其他依賴者），與我自己的獨立枚舉一致。

順帶修掉一個**跨檔字串不一致**：舊碼輸出的是 title-case `Context Budget Warning`，而 `src/memory.ts:196` 的 [Agent disciplines] 與 `usage-guide.html` 用的都是全大寫 `⚠️ CONTEXT BUDGET WARNING`。三處現已統一為全大寫。這是一致性修正**不是**已知缺陷修復——沒有證據顯示大小寫差異曾造成模型漏讀。

兩則附註（各一行，不展開）：
- `mcp-readonly.ts:151` 的 `slice(0, 8000)` 切的是 **UTF-16 code unit**，理論上會切斷 surrogate pair；dsh 明講按 Unicode code point 切。屬瑕疵非缺陷。
- dsh 的 compaction 對 pinned／system 內容保護是 **ABSENT** ∴ **整套搬會連這個洞一起進口**——bridge 的 preamble 帶著 always-on 紀律，正是 f_84bfee 那個失效形狀（固定區塊被靜默丟掉、外觀完全正常）。

## 5. 借鏡結論

| 項目 | 判定 | 理由 |
|---|---|---|
| **接成第四個 backend** | ⛔ **不做** | §3.2：無 MCP capability ＝ bridge 的 agent-action 層歸零；無 `session/load` ＝ 失去 resume；啟動路徑是 demo script |
| Effect disposal pattern | 🟡 中（沿用 08-17 判定） | bridge 的 MCP server／specialist 沒有「卸載時撤銷 side effect」的構造。但 bridge **目前沒有熱卸載需求** ∴ 不急 |
| Declarative capability composition | 🟢 低（沿用） | `specialist-domains.json` ＋ `acp-providers.json` 已近似，缺的只有 patch layer，現行規模不需要 |
| Append-only projection | 🟢 低（沿用） | bridge 的 session archive 是複製不是投影；fork/branch 需求不強 |
| `compaction`（壓縮既有歷史） | ⛔ **不做**（§4.2） | bridge 不擁有對話 context，harness 那層已經在做 |
| `spill` / tool-result pruning 套到 `list_facts` | ⛔ **不做**（§4.3） | 成本不對稱方向相反：漏 fact 比多花 1.4% 視窗貴；且已量測非急件 |
| **`compactNow()` 式的「持續評估 ＋ 明確路徑」觸發模型** | 🟠 **建議做**（§4.4） | bridge 的 70% 警告是一次性的，之後到死線再無提醒。單檔、微小級、完全在 bridge 掌控內 |
| Cordis kernel 整套 | ⛔ 不做（沿用） | bridge 是 Telegram adapter ＋ orchestration，不是 plugin runtime |
| 沙盒 | ⛔ 不做（沿用） | bridge 不執行程式碼 |

## 6. 證據等級

| 主張 | 等級 |
|---|---|
| repo metadata、`default_branch=master`、49 個 package 名 | 🟢 A（API 原始欄位／目錄清單） |
| bridge 側的 `mcpServers` 傳遞與 `loadSession` fallback | 🟢 A（自查 `src/acpClient.ts` 行號） |
| dsh-acp 的方法表、capability 宣告、npm 名 | 🟡 B+（WebFetch 轉述，引號為其標示之原文；未讀 `src/`） |
| 08-17 報告的 Cordis／九大分類／四種模式 | 🟡 B（二手：搜尋＋文件站，本輪未複驗） |
| bridge 的 context-assembly／telemetry／70% 一次性警告、三個 MCP 的輸出上限、shard 字元數實測 | 🟢 A（讀原始碼 ＋ 實際量測） |
| dsh compaction 的觸發／保留／丟棄／剪枝手法、spill 的 preview+locator 設計 | 🟡 B+（WebFetch 轉述 `docs/subsystems/compaction.md` 與兩份 README） |
| 「傳了 mcpServers 會被忽略還是報錯」 | ⚪ 未驗 |
| 「ACP 有沒有 backend 暴露觸發 compact 的介面」 | ⚪ 未驗 |

## 相關

- [[opencode-acp-implementation]] — 上一個「第四個 backend」候選，同樣形狀、相反的 authMethods 陷阱
- [[bridge-acp]] — bridge 的 ACP backend 契約與 raw JSON-RPC 探針做法
- [[bridge-session]] — `session/load` 缺席會影響到的 resume 行為
- [[bridge-research]] — 外部 repo 研究的總索引（該頁已達行數棘輪基線 278 行 ∴ 本頁刻意不往它加行）
