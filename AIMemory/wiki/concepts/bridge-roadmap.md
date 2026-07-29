---
title: Bridge Roadmap
type: concept
created: 2026-07-28
updated: 2026-07-29
sources: []
---

# Bridge Roadmap

## Pending

- [ ] Expandable blockquote / Rich Message `<details>` 支援（bridge-streaming）：HTML fallback path 需在 format-html.ts 識別 `>...\|\|` 結尾並輸出 `<blockquote expandable>`；Rich Message path 可能天然支援或改用 `<details>` 標籤（有 summary 標題更強）；待實測 Rich Markdown 是否認 `||` 語法
- [ ] Footer 組裝層 smoke 覆蓋（bridge-specialist / bridge-acp）：`proxyUsageFooter()`（proxy-finalize.ts）與 `getProxyModelInfo()`（specialist.ts）零覆蓋，`check-acp-model-truth.mjs` 只守到 provider 層的 verifiedModelInfo 語意；bb2e265（2026-07-29 footer 補 model/effort + `(pin)` 標註）留下的測試債，Fable5 覆核 LOW-2 點名。**已有的**：fake-acp-agent.mjs 兩種 model 回報形狀（`FAKE_ACP_CONFIG_OPTIONS`=claude、`FAKE_ACP_MODELS_SHAPE`=Kiro 回音形狀）、check-specialist.mjs 的 temp specialists.json pattern、runner 自動掃 check-*.mjs 免註冊。**唯一摩擦**：`spawnOrReuse` 是 module-private，外部只能經 `promptProxy` 填 `instances`，而它第一輪會連帶跑 preamble + enrichment。**未實測的假設**：那三者的 `.catch` 兜底在 temp MEMORY_DIR 下會不會乾淨降級——這是工時從「一支 ~130-180 行小 smoke」擴大的唯一變數，動工前先花 5 分鐘探測。要鎖的 BC：無 proxy 回空字串 / model+effort 皆空只印 specialist 名（回歸保護）/ 未 spawn 走 entry pin 標 `(pin)` / claude 形狀 spawn 後不標 / Kiro 形狀（model verified、effort 來自 pin）要標（鎖 LOW-1 修法）/ closeInstance 後退回 pin 重新標。**不含**主 agent footer 側（run-prompt.ts 的 modelSuffix 埋在 runPrompt 中段、無可測接縫，要先抽函式，另一筆帳）

## In Progress

## Done
