---
title: Bridge ACP 與 Model 配置
type: concept
created: 2026-07-06
updated: 2026-08-09（新增 tool 結果狀態判定鏈查證）
sources: [f_b533eb, f_493309, f_fedf5c, f_efd659, f_0c44ff, f_51868b, f_0b0e71, f_c5dfde, f_130b5d, f_7fb676, f_611812, f_392c22, f_fb7004, f_b1b0f4, f_3c7a91, f_884e78, f_7bf9a8, f_948bf2, f_e17260, f_50d5f5, f_174485, f_b21c3a, f_a1ecf7, f_bd8491, f_ceda58, f_5caae0, f_f6406d, f_20ed42, f_2f4ae9, f_6d48aa, f_87efaf, f_61ec60, f_ab8e2f, f_30e280, f_244bfd, f_aad37e, f_5c5722, f_d8cd71, f_9c4a6e, f_ae2bf4, f_fc50c8, f_e63d1a, f_87a34f, f_6b2c90, f_f4d872, f_4f2c91, f_a7d3e8, f_c92b41, f_d8f6a2, f_e3c7b5, f_f1a8d9, f_02e4c6, f_6e52ff, f_8e6494, f_c0459d, f_6ae02c, f_525552, f_5b7539, f_f2a212, f_8c08d6, f_3dddec, f_634e34, f_97d203, f_ec0c7c, f_4ef3e7, f_dccd98, f_3cad91, f_ca3437, f_820b01, f_43da84]
---

# Bridge ACP 與 Model 配置

[[bridge-project]] 透過 ACP（JSON-RPC over stdio）接上 agent CLI。本頁涵蓋 ACP adapter 切換、model 配置與 pin 機制、harness hook 行為——這些知識跨 adapter 有效，換 CLI 時特別需要。

## 目前配置（2026-08-02 更新）

- 主 session model：`opus[1m]`（Opus 5 1M context 變體）
- `.env`：`ACP_AGENT_COMMAND=claude-agent-acp` + `ACP_MODEL=opus[1m]`
- `/agent claude` backend model pin：`opus[1m]`（effort high）— 設定檔 `${MEMORY_DIR}/config/acp-providers.json`
- **重要更新（2026-07-29）**：`.env ACP_MODEL` 從無效值 `claude-opus-5` 改為 `opus[1m]`，同時將 `@agentclientprotocol/claude-agent-acp` 從 0.59.0 升到 0.63.0（SDK 0.3.207→0.3.220）才讓 `opus[1m]` 正確解析成 Opus 5 (1M)
- Model 由 bridge 在 `session/new` 後透過 `session/set_config_option` pin——**claude-agent-acp 的 CLI `--model` flag 在 ACP 模式無效**
- `ACP_SESSION_RESUME=true` 已於 2026-07-07 啟用
- `claude-agent-acp` **不支援** `effort` config option——設 effort 會回 `-32603 Unknown config option`，bridge 已 graceful ignore

### ACP Model 別名與 Adapter SDK 關係（2026-07-29 事故教訓）

- **ACP model 別名/id 的有效性由 claude-agent-acp adapter 釘死的 SDK 版本決定**——必須升 adapter 才拿得到新 model
- **靜默降級陷阱**：pin 被 adapter reject 時 `applyModelEffort()` 會 by-design 靜默降級到帳號預設 model，不會有任何錯誤浮到 Telegram
- **依賴文件保存期限**：此類寫死版本的悲觀結論應標日期並定期複驗

### ACP Adapter 能力偵測陷阱（2026-08-02 新增）

codex-acp 同時公告 `models` 形狀**與** `configOptions` 裡 `id="model"` 的條目，所以「有沒有 model config option」不能拿來判別「這個 adapter 能不能在 session 期間換 model」——用它會讓 bridge 真的對 CLI-arg adapter 送出 `set_config_option`。

**正確判別式**：
1. `models` 區塊是否出現過（kiro/codex 有、claude-agent-acp 沒有）
2. 要在 `availableModels` membership 驗證**之前**就 latch，因為回音了假 model 的 kiro 一樣是 CLI-arg adapter

repo 自己的 BC-13 fixture（`FAKE_ACP_MODELS_SHAPE=1` + `FAKE_ACP_CONFIG_OPTIONS=1` 同時開）就是這個雙形狀的證據。

### AcpBackendDef model vs displayModel 語意差異（2026-08-02 新增）

`AcpBackendDef` 有 `model` 與 `displayModel` 兩個欄位且語意不對稱：
- `applyModelEffortToCommand` 只在 claude 分支回傳 `acpModel`
- 所以 kiro/codex 的 `model` 恆為 `undefined`，只有 `displayModel` 有值
- 實跑確認：kiro `model=undefined`、`displayModel=claude-opus-4.5`
- **要比對「這個 backend 現在跑什麼」必須用 `displayModel`**，用 `model` 對 CLI-arg adapter 恆不命中

### Agent 無法自知 Model 的結構性問題

- SDK 不注入「You are powered by the model named X」到 agent context，被問只能猜
- 修法：在 `sessionManager.create()` 於 `initialize()` 後、preamble 注入前追加一行實際 model
- 三個 ACP adapter 在 `session/new` 回報 model 的結構各不相同（記錄在 `acp-model-report-shapes.md`）

### claude-agent-acp 合法 model id（2026-08-02 驗證）

以 `scripts/check-acp-model-effort.mjs` 實際 spawn adapter 驗證：
- `claude-sonnet-5` 是合法 model id，adapter 會原樣回報
- 同 adapter 公告的合法值含：`default` / `opus[1m]` / `sonnet`

## /agent 熱切換與多 Backend 設定檔

- `/agent <key>` 熱切換 ACP backend，設定檔 `${MEMORY_DIR}/config/acp-providers.json`，**每次 `/agent` 即時重讀**
- 三個 backend 配置（2026-08-01 對照實檔更正）：
  - `claude`：claude-agent-acp，pin `opus[1m]` / effort high
  - `kiro`：`kiro-cli acp --model claude-opus-4.5 -a --agent main`
  - `codex`：`npx -y @agentclientprotocol/codex-acp`（2026-08-06 遷移自已 deprecated 的 `@zed-industries/codex-acp`），pin `gpt-5.6-terra` / effort high；auth 已用 ChatGPT 登入可正常運作，見下方「Codex authMethods 誤判」

## Kiro CLI Model 生態

- **短名格式**：`claude-sonnet-4.6`、`claude-opus-4.5`（非完整 API model ID）
- **Claude 系**：auto / claude-sonnet-4.6 / claude-opus-4.5 / claude-sonnet-4.5 / claude-sonnet-4 / claude-haiku-4.5
- **注意**：`claude-opus-4.6` 已於 2026-07-27 被 Kiro CLI 移除
- **非 Claude 系（2026-07）**：deepseek-3.2（0.25x, 164K）、qwen3-coder-next（0.05x, 256K）、minimax-m2.5/m2.1、glm-5

## 異源對抗覆核紀律（常態化實踐）

### 核心原則

異源模型對抗覆核能打破同源自審天花板，已常態化套用於高風險決策。

### 覆核紀律（2026-08-02 最新版）

1. **開放授權不給檢查清單**：讓覆核者自己探索
2. **讀原始碼而非信 commit message**
3. **多輪連續覆核要換新 context**：修法常是上一位覆核者提出的建議，讓他覆核自己的提案等於同源自審
4. **第二輪起刻意不告知前一輪結論**：避免錨定
5. **收斂條件**：第二輪若回報無 high/medium 即視為收斂可 push
6. **誠實交代**：覆核者的可 push 判斷是針對它看過的那個 commit，之後的修正 commit 未經覆核
7. **授權回報「已收斂」**：避免覆核者為交差硬湊 finding

### 價值實證

- 2026-07-26：Fable 5 對 commit afb9d8e 做覆核（37 次工具呼叫、587 秒），抓出 protobufjs 依賴論證的關鍵推理缺陷
- 2026-07-31：抓到「commit message / 註解 / AI.md 三處共用同一個錯誤因果敘事」——教訓：寫「因為 X 所以要 Y」前必須讀到 X 的實際時序
- 2026-08-01：Fable5 覆核抓出 cutPendingTokenTail 的結構性不變式缺陷（TOKEN_OPENERS 缺 `<<CONTINUE:`）

### 可重用教訓（2026-08-01）

兩份清單分別用「字串陣列」與「regex」表達同一個集合時，衍生自同一個 NAMES 常數並不足以保證等價——裸型 token（RESTART/CONTINUE）是在 regex 那邊手寫的，衍生機制蓋不到。

### Advisor 工具 vs 異源覆核（2026-08-02 新增）

Claude Code 的 `advisor` 是 server-side tool：零參數、呼叫時整段對話逐字稿自動轉發、回傳 `advisor_tool_result` content block（與 `web_search` 同族）。Gating 條件為 `advisorModel` 設定 + 僅第一方帳號（Bedrock/Vertex 不行）+ 顧問模型的 `advisor_rank` 必須 ≥ 主模型（Haiku 4.5=1、Sonnet 4.6=2、Sonnet 5／Opus 4.6=3、Opus 4.7/4.8/Opus 5=4、Fable 5=5），關閉用 `CLAUDE_CODE_DISABLE_ADVISOR_TOOL`。

**不能取代 push 前異源覆核**：
1. 它的視野等於主 agent 的視野，讀不到你沒讀過的檔案，無法「自己讀原始碼而不信敘事」
2. 對象是「這場對話」不是「這個 commit」，跨 session 改動缺席
3. 它是模型自主 opt-in，不是 gate（覆核紀律是 hard requirement）

價值在時間軸另一端（設計決策前／卡住時），與 push 覆核互補，不是替代。

### 覆核者選型（成本分級，2026-08-02 新增）

Claude 家族相對單價（catalog pricing tier）：Sonnet 5 = 1x、Opus 5 = 1.7x、**Fable 5 = 3.3x**、Haiku 4.5 ≈ 0.3x。覆核者是 agentic 的（工具迴圈讀進去的碼全算 input），模型選型的成本差會被放大。

分級規則（已寫進 `ms-cross-model-adversarial-review` 正本）：
- 孤兒 import／死碼 → **不派人**，交給型別系統（見 [[bridge-smoke-gate]] 的 noUnusedLocals 閘門）
- 敘事比對、恆真斷言 → Sonnet 級
- 不變式／論證推理／時序 race → 最強模型（Fable 5）

判準：**改動有沒有碰承重路徑**。

## vc-kiro-delegate 三段 Review

委派 Kiro 實作後的品質鏈：① Kiro self-review ② 獨立新 session 冷讀 git diff ③ 主 agent heavy review。

**2026-07-14 教訓**：`kiro-cli` 的 prompt 走命令列參數有長度上限（37KB 會炸 `Argument list too long`），長 spec 應寫成檔案讓 Kiro 自己讀路徑。

## Claude Max 5x 模型分配策略

- Opus 只留給高認知決策（架構、最終審查、難 debug、對抗驗證）
- ≥2k token 的實作產出委派 Kiro CLI
- **快速判準**：自問「這個錯誤是 Sonnet 級還是 Opus 級」
- Workflow / subagent 必須顯式指定 model override

## Skill 新增（2026-08-01）

- `ms-vacuous-test-gate`（綠燈假象五型 + 突變測試，score 0.58）
- `ms-cross-model-adversarial-review`（push 前異源對抗覆核紀律，score 0.87）

已投影到 `~/.claude/skills` 與 `~/.kiro/skills`。

## 為何選擇 stdio JSON-RPC（2026-08-04 QM 研究決策）

Bridge 選擇 stdio JSON-RPC 而非 HTTP server mode 與底層 agent CLI 通訊：

**場景評估**：
- 單一 Telegram chat 對應單一 ACP session（不需多 client）
- Streaming 已靠 ACP 的 `session/update` notification 解決
- 沒有跨機器需求（relay 是另一個 bot 不是連同一個 CLI）

**成本/收益分析**：
- 成本高：要處理 port 分配、改寫整個 `acpClient.ts`
- 收益低：無對應使用場景

**排除 HTTP server mode 的額外理由**：
- `kiro-cli` 根本沒有 `serve` subcommand
- QM 用 HTTP 是為了支援併發 abort+steer+prompt 與 tool bridging 回打場景，bridge 都用不到

## ACP Session Resume 語意分析與能力探測（2026-08-05）

### load 與 resume 是規格層的語意分離

ACP spec 明文（normative）：
- `session/load` — Agent **MUST** 把整段對話以 `session/update` 重播給 client
- `session/resume` — Agent **MUST NOT** 在回應前重播對話歷史

這不是某個 adapter 的實作偏好，是協定分工。opencode 的 `resumeSession`/`loadSession` 共用同一函式、`resume` 只多讀 `limit: 20` 且不重播，`fork` 則讀 20 筆並重播（opencode 自己此處不一致，別照抄 fork 的 limit）。

### sessionCapabilities 實測（`scripts/probe-acp-session-capabilities.mjs`，initialize-only raw probe）

| Adapter | 版本 | `sessionCapabilities` | resume | list | fork |
|---|---|---|---|---|---|
| claude-agent-acp | 0.63.0 | `{additionalDirectories, close, delete, fork, list, resume}` 無條件宣告 | ✅ | ✅ | ✅ |
| kiro-cli | **2.16.1**（更正，舊記錄 2.15.1 已過時） | 整塊缺席（只有 `loadSession: true`） | ❌ | ❌ | ❌ |
| codex-acp | — | npx 下載逾時未測完 | **未知**（不可讀成不支援） | — | — |

### bridge 的 `replaying` 抑制旗標判定：不可刪，只能 capability-gate

`acpClient.ts` 的 `replaying` 旗標（:472 宣告、:732 丟棄 replay 期間的 `session/update`）**確定不可刪除**，只能 capability-gate 成兩條分支：

- **resume 路徑**（claude）：`session/resume`，request/response 與 load 版逐欄同形，呼叫端零改動，不需要 `replaying`
- **load 路徑**（kiro）：`session/load` + `replaying` 抑制**照留**——因為 Kiro 未宣告 resume，且是使用者日常會切的 backend，load + replaying 是常態路徑而非邊緣 fallback

Gate 條件：`agentCapabilities.sessionCapabilities?.resume !== undefined`（ACP 用空物件表示能力存在，Kiro 是整個欄位不存在，可靠區分，分支數確定為 2）。**已設計、尚未實作**——追蹤於 [[bridge-roadmap]]。

OpenCode 的 ACP 支援（`sst/opencode` dev branch v1.18.13）採 stdio 前臉 + HTTP 後腦架構：`opencode acp` 起本機 HTTP server 後自己當自己的 client，ACP 層每個方法轉一次內部 HTTP 呼叫。此架構反向佐證 bridge 選 stdio JSON-RPC 的判斷（opencode 兩層都要是因為同時要餵 TUI/web/ACP 三種前端，bridge 只有單一 Telegram chat 對單一 ACP session）。細節見 [[opencode-acp-implementation]]。

## Codex authMethods 誤判與 effort 斜線解析（2026-08-06）

### authMethods 語意在 adapter 間不一致

`initialize` 回傳的 `authMethods` 語意 ACP 沒規定，三方對照實測（2026-08-06）：

| Adapter | 已登入時 `authMethods` |
|---|---|
| claude-agent-acp 0.63.0 | `[]` |
| kiro-cli 2.16.1 | `[]` |
| codex-acp（兩個套件版本皆同） | **非空**（`["chatgpt", "CODEX_API_KEY", "OPENAI_API_KEY"]`），且同 session 的 `session/prompt` 正常拿到 `end_turn` |

bridge 原本 `authRequired = authMethods.length > 0`，把每個 Codex session 誤判成未登入，後果：靜默關掉整個 session 的 transient retry、錯誤訊息指向登入、多送一顆登入按鈕。已於 commit `56a09f0` 加 `authMethodsImplyLoggedOut(kind)` 例外（codex 豁免，`other` 維持保守）。OpenCode 已知同樣不遵守「已登入回空陣列」慣例，接成第四個 backend 時要一併加例外。

### effort 後綴解析：為何不無條件拆斜線

Codex 的 ACP adapter 有兩個套件，`currentModelId` 格式不同：

| 套件 | 狀態 | `currentModelId` 格式 | effort 檔位 | sessionCapabilities |
|---|---|---|---|---|
| `@zed-industries/codex-acp` 0.15.0/0.16.0 | ⚠️ **已 deprecated**（npm 明寫改用下者，停更 2026-06-23） | 斜線 `gpt-5.5/medium` | low/medium/high/xhigh | 整塊缺席 |
| `@agentclientprotocol/codex-acp` 1.1.9（upstream 預設） | 維護中 | 方括號 `gpt-5.6-terra[medium]` | 多 max/ultra | 宣告 resume/list/close/delete/additionalDirectories |

`splitEffortSuffix` **刻意不無條件拆斜線格式**：因為 `vendor/model` 是 model id 的常見寫法，無條件拆會把正常 model 名砍一半、後半誤當成 effort。做法是只在後綴命中該 adapter 自己公告的 `reasoning_effort` 值域時才拆，拿不到值域就不拆（寧可少報 effort，也不謊報 model）；方括號格式是專用語法無歧義，維持無條件拆。commit `7974d27`，經 Fable5 覆核抓出兩次恆真斷言（斷言值其實跟斜線解析無關；兩臂都傳 pin 導致 `set_config_option` 回應把 effort 蓋回去）才驗證邏輯真的成立。

### 套件遷移

telegram-kiro-bridge 已於 2026-08-06 遷移到維護中的套件：`acp-providers.json` 的 codex 條目改為 `command=npx -y @agentclientprotocol/codex-acp`、`model=gpt-5.6-terra`、`effort=high`（原為 `npx @zed-industries/codex-acp` + `gpt-5.5`，該 model 在新套件不存在）；claude 與 kiro 兩個 backend 未動。新套件經 bridge `AcpClient` 端到端驗證：pinned `model=gpt-5.6-terra` + `reasoning_effort=high` 皆確認生效。

⚠️ **參考 upstream 前先查 merge-base**：2026-08-06 查證 upstream/main 至今仍有 `authRequired = authMethods.length > 0` 誤判與方括號-only 的 effort regex——上面兩個修正都領先 upstream，不是重工；四個 codex 相關 upstream commit 早已全數在本 fork。

## Tool 結果狀態判定鏈（2026-08-09 查證）

bridge 判斷一次 tool call 成敗完全依賴 ACP 的顯式 `status`，自己不做任何預設或嗅探：

- `sessionManager.ts:1256/1289` 分派邏輯直接讀 ACP 回傳的 status，兩個分支都明寫
- 上游 `claude-agent-acp` 的映射（`dist/acp-agent.js:5802`，逐字）：
  ```js
  isError = "is_error" in chunk && chunk.is_error ? "failed" : "completed"
  ```
- 下游消費者：`_consecutiveToolFails` 累加後於 `sessionManager.ts:1318` 觸發 Reflexion hint

**更正一條先前錯誤主張**：`agent-diagnostics.ts` 只 parse `type:"system"/subtype:"api_error"`，從頭到尾不看 tool result，跟這條判定鏈沒有交集。

### is_error 可信度實測（研究外部 repo cc-session-reader 時查證）

外部 repo cc-session-reader 的 ADR-003 主張「Bash 結果沒有 `success` 欄位、`is_error` 也不可信」。拿本機 25 份 transcript、1260 個 `tool_result` block 實測現行 Claude Code：

| 觀察 | 結果 |
|---|---|
| 非零 Exit code 的結果 | 18 筆，**18/18 都帶 `is_error: true`** |
| Bash 的 `is_error` 欄位 | 從不缺席（false 497 / true 8） |
| 欄位缺席的工具（Edit/Read/Agent/Write） | 缺席即代表成功，缺席但文字帶失敗特徵者 0 筆 |

∴ **現行 Claude Code 的 `is_error` 是可信的失敗訊號**，上面 adapter 的映射正確，bridge 這條路徑健全；ADR-003 的主張在此不重現。

⚠️ 誠實邊界：n=18 太小（錯誤率高到約 15% 仍有 5% 機率量到 0/18），單機單專案單版本，且未端到端驗 SDK 串流 chunk 的形狀——此段仍是 B 級推論，非普遍證實。完整研究脈絡見 [[cc-session-reader]]。

## ACP Adapter 設定檔差異

| Adapter | 讀取的設定檔 |
|---|---|
| Kiro CLI | `AGENTS.md` + `~/.kiro/steering/` |
| Codex | `AGENTS.md` |
| Claude Agent | `CLAUDE.md`（全域 + 專案） |

## 相關

- [[bridge-project]] — Bridge 本體架構與功能
- [[bridge-upstream-sync]] — Fork 同步與合併衝突處理
- [[bridge-dream]] — Dream 例行維運框架（per-backend model 設定）
- [[verification-diagnosis]] — 覆核的驗證方法論
- [[bridge-roadmap]] — session/resume 實作追蹤於 Pending 清單
- [[opencode-acp-implementation]] — OpenCode ACP 實作研究（stdio+HTTP 架構、完整方法表）
- [[adversarial-review]] — 異源對抗覆核紀律（自本頁拆出，2026-08-05）
- [[bridge-model-strategy]] — Model 選型/pricing/effort 策略（自本頁拆出，2026-08-05）
- [[cc-session-reader]] — is_error 可信度實測的完整研究脈絡與借鏡評估結案
