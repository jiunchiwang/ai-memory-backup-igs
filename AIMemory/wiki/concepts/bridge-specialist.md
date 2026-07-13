---
title: Bridge Specialist 分身系統
type: concept
created: 2026-07-11
updated: 2026-07-13
sources: [f_5a2532, f_493b31, f_946c9d, f_e19357, f_2a93b5, f_ad29fd, f_02206d, f_bf688a, f_121c69, f_db7050, f_040f63, f_1ed45f]
---

# Bridge Specialist 分身系統

> 2026-07-11 從 [[bridge-project]] 拆出。涵蓋 specialist 配置、token 執行權限層、監控 Dashboard、並行委派品質機制。

## 分身配置

`specialist-domains.json` 配置 3 個分身（2026-06-24 建立，model 2026-07-01 更新）：

- **slot-dev**：UK 老虎機開發（claude-sonnet-4.6，memory MCP）
- **researcher**：深度研究 / AI 策略（claude-sonnet-4.6，memory + google MCP）
- **general**：完整能力並行多工（inheritsAll，claude-sonnet-4.6，memory + google MCP）

設計決策：不建 bridge-dev specialist——主 agent 工作目錄就是 bridge repo，bridge-dev 是降級冗餘。

互動模式兩種：`SPECIALIST_PROXY`（即時對話，使用者訊息直送 specialist 直到 /back）、`PARALLEL_DELEGATE`（背景並行任務，結果一次注入主 session）。歷史產出存 `${MEMORY_DIR}/artifacts/`（結構化 JSON）。

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

## 相關

- [[bridge-project]] — 專案總覽
- [[bridge-memory]] — 記憶與維運（specialistreview 步驟在 /dream 內）
- [[bridge-acp]] — specialist model pin 與 ACP 配置
