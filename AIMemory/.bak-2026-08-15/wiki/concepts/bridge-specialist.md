---
title: Bridge Specialist 分身系統
type: concept
created: 2026-07-11
updated: 2026-08-15（新增：run_plan 能力錯配缺陷修正（wf-review/wf-verify 改派 verifier/moa-ref-security）+ 三個 CLI 各讀各自 MCP 設定檔的補充事實）
sources: [f_5a2532, f_493b31, f_946c9d, f_e19357, f_2a93b5, f_ad29fd, f_02206d, f_bf688a, f_121c69, f_db7050, f_040f63, f_1ed45f, f_e2b049, f_88f2a3, f_e6394d, f_bdf14b, f_493309, f_ad661e, f_51868b, f_3c7a91, f_719003, f_b01ccb, f_c965d5, f_56f3c9, f_3bb538, f_76b1f7, f_a2c25a, f_182f52, f_10fbe3, f_7ab946, f_6a2483, f_705e1e, f_bd5b93, f_8b9cb4, f_7e1d01, f_af6d38, f_14861b, f_618525, f_2fe4f7, f_fd8698, f_6d597d, f_667928, f_9de427, f_6039c4, f_e8b20f, f_3ce2e3, f_f9956d, f_5c3a5a, f_198e79, f_665ffb, f_d878ad, f_e7bcdd, f_2bcda2, f_39026e, f_aa67b7, f_75089c]
history_sources: [f_32a736]
---

# Bridge Specialist 分身系統

> 2026-07-11 從 [[bridge-project]] 拆出。涵蓋 specialist 配置、token 執行權限層、監控 Dashboard、並行委派品質機制。

## 分身配置

`specialist-domains.json` 配置（2026-06-24 建立，**2026-07-13 改為品質優先方案**；**2026-08-12 直接讀取設定檔更正**：`defaultModel=claude-opus-4.5`、`defaultEffort=high`，全部繼承 `effort: high`）：

- **slot-dev**：UK 老虎機開發（harness `claude-agent-acp`、model `sonnet`——claude-agent-acp 的 canonical alias，不是舊敘述的 Kiro 命名 `claude-sonnet-4.6`；memory MCP，skill prefix 隔離 `prefixes: ["uk-"]`——2026-08-13 直接讀設定檔核對，舊敘述的五條 `uk-slot-`/`slot-`/`uk-`/`pq3-`/`cocos-` 已收斂成單一前綴；另有 topicKeywords 與 9 個 wikiPages）
- **bridge-dev**：telegram-kiro-bridge 專案自身開發特化（ACP adapter 切換、memory/wiki 維運、streaming、session 生命週期、specialist 系統；model=`(default)` 即 opus-4.5）——**2026-07-16 已建立，見下方「不建」決策更正**
- **researcher**：深度研究 / AI 策略（model=`(default)` 即 claude-opus-4.5；舊敘述的 pin `claude-opus-4.6` 已於 2026-07-27 從 Kiro 移除失效，目前退回繼承 `defaultModel`，memory + google MCP，`inheritsAll` 全繼承）
- **general**：完整能力並行多工（`inheritsAll`，model=`(default)` 即 claude-opus-4.5，memory + google MCP）
- **verifier**：輸出品質判定，advisory only（harness `claude-agent-acp`、model `sonnet`）

⚠️ **上面除 `slot-dev`/`verifier` 外全部繼承 `defaultModel=claude-opus-4.5`，不是各自寫死的 sonnet-4.6/opus-4.6**——2026-08-12 factlint 才發現這個落差，查無對應的變更 fact，很可能是設定檔被直接改動但沒補記錄；查證時請直接讀 `specialist-domains.json`，不要信這幾行歷史敘述的舊值。

> 🗑️ **2026-08-13：來源 fact `f_05ac7e`（2026-07-13「品質優先方案」配置快照）已解除 wiki 引用並刪除。** 它的三個 model 值、slot-dev 五條 prefix 全部與設定檔不符，而 fact 會被注入 preamble 當成事實 ∴ 留著的成本高於它的 provenance 價值。這是對 2026-07-08「接受 wiki 保護、不解除引用」裁決的一次例外，適用範圍限「內容已被證實為假」的 fact，不是瑣碎但為真的那一類。**刻意不補記新的設定快照**——現況 30 秒內可從 `specialist-domains.json` 讀出，而新快照只會用同樣的方式再腐爛一次。

`commonSkills` 含 5 項基礎防護 skill、`commonMcpServers` 含 memory。**設計決策已反轉**：2026-07-10 曾決定不建 bridge-dev specialist（理由：主 agent 工作目錄就是 bridge repo、bridge-dev 是降級冗餘），但 2026-07-16 仍建立並持續在用（2026-08-11/12 本次工作階段內兩度實際委派覆核）——舊決策 fact 因受 wiki 引用保護留存，但内容已被現況取代，此處以現況為準。

互動模式兩種：`SPECIALIST_PROXY`（即時對話，使用者訊息直送 specialist 直到 /back）、`PARALLEL_DELEGATE`（背景並行任務，結果一次注入主 session）。歷史產出存 `${MEMORY_DIR}/artifacts/`（結構化 JSON）。持久記憶由 `src/specialist-memory.ts` 實作（`extractLessons`/`appendMemory`/`readMemory`/`onSpecialistDone`），掛在 `artifact.ts` 的 `saveArtifact`（status=done 時 fire-and-forget，因 specialist 完成不是 tool call 事件，不適用 PostToolHook registry）；記憶檔存 `${MEMORY_DIR}/specialist-memory/<name>.md`，上限 20 條。

⚠️ **model 無法動態指定**：spawn 時 model 已由 `defaultModel` pin 住，prompt 裡要求換 model 無效；`PARALLEL_DELEGATE` 的 prompt 含 `>>` 或多行會被 bridge token parser 截斷導致任務靜默未 spawn，model benchmark 類需求改走 `kiro-cli chat --model` 獨立 session 執行。

## MoA 顧問系統（2026-07-15）

`specialist-domains.json` 新增 3 個 `moa-ref-*` domain（`effort: low`、`mcpServers` 空、`prefixes` 空），對應 `preamble.md` 建於 `specialists/moa-ref-*/`：

- `moa-ref-claude`（claude-sonnet-4.6）、`moa-ref-kiro`（glm-5）、`moa-ref-adversary`（claude-sonnet-4.6）
- 後續補齊（未查到建立日期 fact）：`moa-ref-security`/`moa-ref-perf`/`moa-ref-ux`（皆 harness `claude-agent-acp`、model `sonnet`，effort high，可讀檔）、`moa-ref-codex`（minimax-m2.5，harness `kiro-cli acp --agent {name} -a`）

先前 `moa-presets.json` 引用的顧問名只是空殼、無法 spawn，此次補齊後 `/moa` 指令可正常運作。ctx 統計行已同步加上 agent/model/effort 後綴（格式「· agent/model/effort」），specialist proxy 則顯示 specialist name。

⚠️ **`moa-ref-kiro` 與 `moa-ref-adversary` 是 blind advisor，不能用來覆核程式碼**（2026-08-11 實測）：前者 `readOnlyLens:true` 但 `mcpServers` 只有 `readonly`、後者 `mcpServers` 為空且 harness `kiro-cli acp -a` 不帶 `--agent`——兩者皆讀不到檔（`src/specialist-config-audit.ts:26,28` 已列為靜默失敗不變式）。`moa-ref-kiro` 曾對盲審任務產出捏造檔名與變數名的幻覺 diff。可讀檔的覆核者是走 `claude-agent-acp` 那組（`moa-ref-security`/`moa-ref-perf`/`moa-ref-ux`/`verifier`/`bridge-dev`）。目前**沒有任何「可讀檔＋跨 vendor」的分身**（唯二非 Anthropic 模型 `moa-ref-kiro`/`moa-ref-codex` 都是 blind advisor）。

✅ **`wf-review`/`wf-verify` 的能力錯配已修（2026-08-13 發生、2026-08-14 修正，commit `9626e10`）**：`plan-templates/wf-review.json` 的 `lens_adversary` 與 `wf-verify.json` 的 `reverse_sweep` 都要求「先自己讀過對象本體＋逐字複製原始碼」，卻派給 `moa-ref-adversary`——它的 preamble 明寫「不要使用任何工具（不讀檔、不寫檔、不跑命令）」∴ 開場即回「我沒有讀取工具的權限」、findings 全部降級成推測。**承重的不是這個錯配本身而是它的不可見性**：step 有回東西就算完成，`moa_plan_done` 記 `failed:0`、run status `done`，拒答只出現在 verifier 的 `NEEDS_FIX` 與顧問自己的內文裡、`/job` 看全綠。改派理由：`lens_adversary` → **verifier**（實測會讀檔並附「檔案:行號」逐字引用）；`reverse_sweep` 排除 general（它同時是該模板的 enumerate/converge 角色，反向遍歷跟枚舉用同一個模型會共享盲點）改派 **moa-ref-security**（preamble 明寫「可讀檔」）。另在 `check-job-orchestration.mjs` 加一條用 **preamble 原文**判盲審的斷言（不寫死名單，名單會漂）＋新增變異守它。兩個容易誤判的事實：①「權限」是顧問自己的措辭不是 ACP 拒絕——`readOnlyLens` 只設在 `moa-ref-kiro`，`moa-ref-adversary` 沒有 ∴ 它握有讀檔工具只是被 prompt 禁用；② 盲審顧問接 `wf-prd`/`wf-design` 的 `challenge` 是合法的（那裡「逐字引用」的對象是 `depends_on` 餵進來的產出不是檔案），斷言的正則不能放寬到涵蓋那種用語，否則會製造假紅燈。

## run_plan 與 wf-design 全有全無設計（2026-08-10）

`run_plan` 的 DAG 依賴阻擋機制讓 `wf-design` 模板成為**全有全無**：三個提案 step（moa-ref-claude / moa-ref-kiro / moa-ref-codex）任一 failed，後續的 challenge 與 decide 步驟整個不執行（回報「未執行：前置 #3 失敗」），已完成的 2/3 份有效產出連帶白費。

**已知問題（刻意擱置）**：`moa-ref-codex` 的 model pin `gpt-5.6-terra` 在本機 codex-cli 0.146.1 必掛（400 requires newer version），使用者於 2026-08-10 選擇**暫不修**（不改 pin、不重跑、不加 pin 驗證閘門）——後續 session 不應自行改掉該 pin。實測 2026-08-10 wf-design 因此只拿到兩份原始方案、零收斂產出，白燒 4 分 7 秒行程時間。

## 委派逾時可 per-domain 設定（2026-08-12，commit 3fd8a9e + 62f5701）

查證委派逾時發現：預設是 **30 分鐘總時長**（`src/specialist.ts:575`/`:961` 的 `entry.timeoutMs ?? 1_800_000`），且**同時有第二道上限 `maxTurns`**，`while (turns < maxTurns && Date.now() < deadline)` 先到先停。兩者回報不同（`specialist.ts:654`）：`Date.now() >= deadline ? "timeout" : "done"` ∴ 收到 `⏱️ timeout` 代表真的跑滿時間、不是 turns 用完；turns 用完會回 `done` 帶部分輸出。

三個容易踩的結構事實：

1. **改 `specialist-domains.json` 對逾時原本無效**——`DomainDef` 原本沒有 `timeoutMs`/`maxTurns` 欄位，runtime 讀的是 `specialists.json`，而 `specialist-create.ts:generateSpecialistConfig` 產生它時是**寫死** `maxTurns: 30, timeoutMs: 1800000`
2. ∴ 直接手改 `specialists.json` 會在下次 `syncAllSpecialists()`（`/specialist sync`、建新分身）被整包覆寫回去，且**沒有任何訊息**
3. 桌面設定 UI 的 `recordSchema` **只有 string 欄位**，數字會以字串寫入 JSON，消費端是 `Date.now() + timeoutMs` → 字串串接讓 deadline 恆大於任何時間戳、`while` 一次都不跑，失敗形狀是「委派秒結束、零輸出、無錯誤」

已修：`DomainDef` 加 `timeoutMs`/`maxTurns`、產生器改吃 domain 值並用新增的 `positiveIntOr()` 強制轉正整數（下界 `>0`、上界 24 小時／1000 turns）、常數集中為 `DEFAULT_SPECIALIST_{MAX_TURNS,TIMEOUT_MS}`、`configRegistry` 補兩個表單欄位、新增 `scripts/check-specialist-budget.mjs` 行為閘門（34 條斷言，4 種突變全殺，見 [[bridge-smoke-gate]]）。`slot-dev` 已設 `timeoutMs=5400000`（90 分）+ `maxTurns=40`，理由是 `uk-slot-codegen` 這種長 pipeline 一輪跑不完（實測連三輪各吃滿 30 分鐘超時，但**產物是好的**——timeout ≠ 失敗，收到 timeout 先去查 `.codegen-checkpoint.json` 與實際檔案，不要照字面判失敗更不要重跑）。

**上限設不到防手滑**：24 小時上限原本註解宣稱「擋得住多打一個零的手滑」，但 90 分鐘多一個零是 15 小時、仍在上限內完全擋不到——沒有任何上限能區分手滑與故意。已改寫成「只擋明確荒謬值」，並在測試裡加反面斷言明文記錄「15 小時仍會被接受」。

**驗證方式**：改 `specialists.json` 後 `/restart`（重啟 agent session）不夠，specialists 設定是開機時載入的 module 層變數（`index.ts` 開機路徑先跑 `syncAllSpecialists()` 再跑 `loadSpecialistsConfig()`），必須重啟 bridge 行程才會重讀。驗證是否生效的最強證據是 `GET http://127.0.0.1:3847/api/specialists`（status server 讀的是記憶體中的 `loadedConfig`，不是磁碟檔）。

### 兩個已知未修項目

- **`extractModel()` 錯報 model**：`status-server.ts` 只從 `harness.args` 撈 `--model` 旗標、不看 `entry.model` 欄位，所以所有走 `claude-agent-acp`（model 放 `entry.model` 而非 CLI 旗標）的 specialist 在 dashboard 都會錯報成 `default`；只有 `kiro-cli acp --model X` 這種把 model 塞進 args 的才顯示得對。2026-08-12 刻意排除在 timeoutMs 改動的 commit 之外避免 scope 膨脹，仍未修。
- **`maxTurns` 預設值有兩個不一致的答案**：`specialist-create.ts` 產生器寫入 `DEFAULT_SPECIALIST_MAX_TURNS=30`，但 `specialist.ts:574` 與 `status-server.ts:300/325` 的保底都是 `?? 15`。實務上因產生器必定寫入該欄位故 15 幾乎不生效，屬潛在誤導來源，尚未修。

## Token 執行權限層（2026-07-07，commit 028a5ea）

- `src/token-policy.ts` 的 `TOKEN_POLICY` 顯式白名單：main 全開 / proxy 限 sendFiles·ask·skillUsages·sticker·rememberFacts / delegate 全禁；`isTokenAllowed()` enforcement
- Specialist memory 回寫附 `[via specialist:<name>]` provenance、單次上限 5 條
- 評估結論：bridge 原本就有隱性 gate，顯式化是防未來 refactor 誤開；唯一實際風險是外部內容→specialist→facts 的**記憶污染**路徑，已由 provenance + 上限緩解
- 分層權限 preamble 評估後不做（僅 cosmetic，specialist preamble 已有 scope 分層）

## 品質機制：PARALLEL_DELEGATE cross-check

≥2 specialist 結果時自動注入交叉驗證指引，借鏡 Claude Code Dynamic Workflows 的 adversarial review 概念。設計決策：只借鏡 cross-check pattern，不搬動態 delegation plan 和 script 持久化（架構定位不同、規模不需要）。

## Specialist Dashboard（2026-07-10）

Status server（port 3847）擴充為 specialist 監控面板：

- **技術選型**：多頁面 hash-based SPA + 純 HTML/vanilla JS（排除 React SPA 太重、排除最小增量擴展性差）
- **入口**：瀏覽器直開 `localhost:3847`（Electron 已移除）
- **用途定位**：即時監控（A）+ 日常管理（B），非純除錯
- **安全加固**（commit c9174e3）：async 錯誤邊界防 crash、預設綁 `127.0.0.1`（`STATUS_BIND_HOST` 可改）、移除 CORS `*`、env 機密遮罩、preamble 路由 specialist 白名單、artifact 檔名 specialist name 錨定 regex

### 監控入口變更：Mini App + tunnel → Bot 訊息推送（2026-07-13）

原設計用 Telegram Mini App 按鈕開 WebView 讀 SSE，需要 HTTPS tunnel（cloudflared quick tunnel）打通 `localhost:3847`。實測 cloudflared 在使用者網路環境下卡在 `Requesting new quick Tunnel` 超過 35 秒拿不到 URL（公司網路封鎖 QUIC），且 quick tunnel 本身不支援 SSE。評估 ngrok/zrok/Tailscale Funnel 等替代方案後，最終決策是**放棄 tunnel 依賴**，改用 `status-push.ts`：任務開始發靜音 Telegram 通知、進度每 5 秒節流編輯同一則訊息、完成時最終更新——零外部服務依賴。`status-tunnel.ts` 與 cloudflared 依賴已刪除，`/status` 指令的 Mini App 按鈕邏輯移除，改純文字顯示。

## Context Packaging（借鏡 fable-advisor，2026-07-10）

`RELAY_DELEGATE` 和 `PARALLEL_DELEGATE` 的 goal prompt 從三要素擴充為五要素（加「已知背景」「待決問題」），比照 fable-advisor（echo-of-machines/fable-advisor，commit 4c1cfd5）的 context packaging pattern。`PARALLEL_DELEGATE` 另加決策型/調查型兩種 context 模式指引，兩處加結果權重協議（給認真權重，僅經驗性失敗或一手資料矛盾時不採納）。

### 架構陷阱

- `index.ts` 全域 `unhandledRejection` handler 會 `process.exit(1)`——任何同 process 的 async callback 未捕捉 throw 都會殺掉整個 bridge，新增 server/handler 必須自帶錯誤邊界
- AIMemory artifacts 檔名 `<date>_<taskId>_<specialist>_<slug>.json` 中 taskId 可含底線，positional `split('_')` 解析必錯，須用已知欄位（specialist name）錨定 regex
- **路徑穿越修復（2026-07-14，commit 35d489c）**：`RELAY_DELEGATE`/`PARALLEL_DELEGATE` 的 taskId 未淨化直接拼進 artifact 檔名，`path.join` 正規化 `..` 可能寫出 `artifacts/` 目錄外；已新增 `sanitizeFilenamePart` 白名單化

## Specialist Reflect（/dream 步驟，2026-07-14）

`specialistreflect` 是 `/dream` 的第 4 步（sessionreflect 之後），掃描 4 個 specialist 的 `specialist-memory/<name>.md`，用本機 LLM 抽取 learnings 升格進 facts/skill-candidates，同時檢查 pending-ingest 老化（>48h）寫進 High Priority 通道。已知限制：本機未裝 llama.cpp 時 learnings 永遠為 []，只有游標推進與 pending-ingest 老化檢查會生效。

> `specialistreflect` 這個步驟名稱本身曾是 `/docupdate` 自我回歸迴圈的受害者——README 過期後被拿去修 `usage-guide.html`，把 HTML 裡真實存在的 `specialistreflect` 步驟刪掉、Dream 步驟數從 15 誤改成 13。事件全貌與修法（`src/doc-facts.ts` 機械枚舉）記在 [[bridge-project]] 的「文件事實來源改為原始碼」節，此處不重複。

## 輕量獨立審查：不透過 specialist 機制

實測出呼叫 Claude Fable 5 做一次性獨立審查（如 merge 前覆核）的輕量方法：`claude -p --model fable "prompt"`，不透過 specialist/domain 機制註冊。比建立臨時 specialist domain 更適合單次第二意見診斷——省去 `specialist-domains.json` 配置與 preamble 建置成本。實際應用見 [[bridge-project]] 的「Push 前安全機制」。

## MCP 繼承最佳化：暫緩（2026-07-27）

評估過把 `settingSources` 限縮為 `['project']` 或 `[]` 可讓 `session/new` 從 spawn 19 個行程降到 3 個，但**決定暫緩不做**——單純限縮會連帶砍掉 specialist 需要的能力繼承。此項要動必須先做「保留能力前提下的架構設計」，不可當成純效能參數調整直接改。

## 三個 CLI 各讀各自的 MCP 設定檔

新增 MCP server 必須三處分別加，改本體才自動三家同步：claude → `~/.claude.json`（`claude mcp add` 寫入）、codex → `~/.codex/config.toml` 的 `[mcp_servers.*]`、kiro → `~/.kiro/agents/main.json` 的 `mcpServers`。Kiro 額外有 `tools` 白名單欄位（如 `["@builtin","@memory","@google","@bridge-actions"]`），只加 `mcpServers` 不夠、還要在 `tools` 加對應的 `@<name>`，否則 server 起得來但工具被白名單擋住。SELF_EVAL token 功能（2026-07-14）與 bridge-actions MCP 的 README／usage-guide.html 說明補齊（2026-07-16/17）皆已在 [[bridge-project]] 記錄，此處不重複。

## 延伸筆記

- Steering 架構：`closed-loop-system.md`（完整閉環）與 `karpathy-guardrails.md`（精簡 4 原則）共存而非合併——前者用於主 agent 長 session，後者用於 specialist/delegation/短任務場景
- 研究侯智薰（雷蒙）AI Agent 7 層 Harness 架構後確認 bridge 已覆蓋全部 7 層，超越部分含 Specialist 分身、跨機 Relay、Self-improving reflexion
- Telegram Bot API 9.6 Managed Bots（`getManagedBotToken`/`replaceManagedBotToken`）適合未來 specialist 自動產生獨立 bot 身份，目前未採用
- 2026-07-16 啟用的 `bridge-actions` MCP（`delegate`/`parallel_delegate` 工具）取代舊 `RELAY_DELEGATE`/`PARALLEL_DELEGATE` 裸 token，詳見 [[bridge-project]]

## 相關

- [[bridge-project]] — 專案總覽
- [[bridge-memory]] — 記憶與維運（specialistreview 步驟在 /dream 內）
- [[bridge-acp]] — specialist model pin 與 ACP 配置
