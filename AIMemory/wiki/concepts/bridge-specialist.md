---
title: Bridge Specialist 分身系統
type: concept
created: 2026-07-11
updated: 2026-07-19
sources: [f_5a2532, f_493b31, f_946c9d, f_e19357, f_2a93b5, f_ad29fd, f_02206d, f_bf688a, f_121c69, f_db7050, f_040f63, f_1ed45f, f_e2b049, f_88f2a3, f_e6394d, f_bdf14b, f_493309, f_ad661e, f_51868b, f_3c7a91, f_719003, f_b01ccb, f_c965d5, f_56f3c9, f_32a736, f_3bb538, f_76b1f7, f_a2c25a, f_a8bb58, f_182f52, f_05ac7e, f_10fbe3, f_7ab946, f_6a2483, f_705e1e, f_48b44d, f_bd5b93]
---

# Bridge Specialist 分身系統

> 2026-07-11 從 [[bridge-project]] 拆出。涵蓋 specialist 配置、token 執行權限層、監控 Dashboard、並行委派品質機制。

## 分身配置

`specialist-domains.json` 配置 3 個分身（2026-06-24 建立，**2026-07-13 改為品質優先方案**，全部 `effort: high`）：

- **slot-dev**：UK 老虎機開發（claude-sonnet-4.6，memory MCP，skill prefix 隔離 `uk-slot-`/`slot-`/`uk-`/`pq3-`/`cocos-` + topicKeywords + wikiPages）
- **researcher**：深度研究 / AI 策略（**claude-opus-4.6**，memory + google MCP，`inheritsAll` 全繼承）
- **general**：完整能力並行多工（`inheritsAll`，claude-sonnet-4.6，memory + google MCP）

`commonSkills` 含 5 項基礎防護 skill、`commonMcpServers` 含 memory。設計決策：不建 bridge-dev specialist——主 agent 工作目錄就是 bridge repo，bridge-dev 是降級冗餘。

互動模式兩種：`SPECIALIST_PROXY`（即時對話，使用者訊息直送 specialist 直到 /back）、`PARALLEL_DELEGATE`（背景並行任務，結果一次注入主 session）。歷史產出存 `${MEMORY_DIR}/artifacts/`（結構化 JSON）。持久記憶由 `src/specialist-memory.ts` 實作（`extractLessons`/`appendMemory`/`readMemory`/`onSpecialistDone`），掛在 `artifact.ts` 的 `saveArtifact`（status=done 時 fire-and-forget，因 specialist 完成不是 tool call 事件，不適用 PostToolHook registry）；記憶檔存 `${MEMORY_DIR}/specialist-memory/<name>.md`，上限 20 條。

⚠️ **model 無法動態指定**：spawn 時 model 已由 `defaultModel` pin 住，prompt 裡要求換 model 無效；`PARALLEL_DELEGATE` 的 prompt 含 `>>` 或多行會被 bridge token parser 截斷導致任務靜默未 spawn，model benchmark 類需求改走 `kiro-cli chat --model` 獨立 session 執行。

## MoA 顧問系統（2026-07-15）

`specialist-domains.json` 新增 3 個 `moa-ref-*` domain（`effort: low`、`mcpServers` 空、`prefixes` 空），對應 `preamble.md` 建於 `specialists/moa-ref-*/`：

- `moa-ref-claude`（claude-sonnet-4.6）、`moa-ref-kiro`（kiro 預設模型）、`moa-ref-adversary`（claude-sonnet-4.6）

先前 `moa-presets.json` 引用的顧問名只是空殼、無法 spawn，此次補齊後 `/moa` 指令可正常運作。ctx 統計行已同步加上 agent/model/effort 後綴（格式「· agent/model/effort」），specialist proxy 則顯示 specialist name。

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

## 輕量獨立審查：不透過 specialist 機制

實測出呼叫 Claude Fable 5 做一次性獨立審查（如 merge 前覆核）的輕量方法：`claude -p --model fable "prompt"`，不透過 specialist/domain 機制註冊。比建立臨時 specialist domain 更適合單次第二意見診斷——省去 `specialist-domains.json` 配置與 preamble 建置成本。實際應用見 [[bridge-project]] 的「Push 前安全機制」。

## 延伸筆記

- Steering 架構：`closed-loop-system.md`（完整閉環）與 `karpathy-guardrails.md`（精簡 4 原則）共存而非合併——前者用於主 agent 長 session，後者用於 specialist/delegation/短任務場景
- 研究侯智薰（雷蒙）AI Agent 7 層 Harness 架構後確認 bridge 已覆蓋全部 7 層，超越部分含 Specialist 分身、跨機 Relay、Self-improving reflexion
- Telegram Bot API 9.6 Managed Bots（`getManagedBotToken`/`replaceManagedBotToken`）適合未來 specialist 自動產生獨立 bot 身份，目前未採用
- 2026-07-16 啟用的 `bridge-actions` MCP（`delegate`/`parallel_delegate` 工具）取代舊 `RELAY_DELEGATE`/`PARALLEL_DELEGATE` 裸 token，詳見 [[bridge-project]]

## 相關

- [[bridge-project]] — 專案總覽
- [[bridge-memory]] — 記憶與維運（specialistreview 步驟在 /dream 內）
- [[bridge-acp]] — specialist model pin 與 ACP 配置
