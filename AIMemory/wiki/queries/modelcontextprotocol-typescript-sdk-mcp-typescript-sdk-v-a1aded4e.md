---
title: "modelcontextprotocol/typescript-sdk: MCP TypeScript SDK v2 (beta)"
type: concept
status: draft
created: 2026-07-08
updated: 2026-07-08
topics:
  - daily-intel
aliases: []
---

# modelcontextprotocol/typescript-sdk: MCP TypeScript SDK v2 (beta)

## 摘要

MCP TypeScript SDK v2 正式進入 beta，對應 2026-07-28 MCP 規範。重大變革包含：套件拆分為 server/client、支援任意 schema 庫（不再綁 Zod）、stateless core 設計、multi-round-trip requests、Header-based routing/caching、以及向下相容 2025 era clients。

## 來源與理由

- Profile: ai
- Run: ab3afe13
- Source: https://github.com/modelcontextprotocol/typescript-sdk/releases/tag/v2.0.0-beta.1
- Rationale: score=0.920; has project impact; has recommended actions; has verifiable claims

## Notes

# modelcontextprotocol/typescript-sdk: MCP TypeScript SDK v2 (beta)

Profile: ai
Run: ab3afe13
Source: mcp-typescript-sdk-releases
Published: 2026-06-30T22:50:42.000Z
URL: https://github.com/modelcontextprotocol/typescript-sdk/releases/tag/v2.0.0-beta.1

## Summary
MCP TypeScript SDK v2 正式進入 beta，對應 2026-07-28 MCP 規範。重大變革包含：套件拆分為 server/client、支援任意 schema 庫（不再綁 Zod）、stateless core 設計、multi-round-trip requests、Header-based routing/caching、以及向下相容 2025 era clients。

## Claims
- MCP SDK v2 對應 2026-07-28 spec，預計 7 月 28 日隨規範一同發布 stable 版
- v2 將 @modelcontextprotocol/sdk 拆分為 @modelcontextprotocol/server 和 @modelcontextprotocol/client
- Stateless core：server 可在無 session affinity 的 HTTP 上擴展，session 變為 opt-in

## Project Impact
- bridge 的 mcp-memory.ts 基於 MCP SDK v1；v2 的 breaking changes（套件拆分、新 handler context、serving API 變更）將需要重寫
- stateless core + multi-round-trip 對 bridge 的 memory MCP 互動模式有重大影響：forget 的 two-phase confirm 流程可能可以用原生 elicitation 取代
- Header-based routing 可能改善 bridge 與多個 MCP server 的 dispatch 效率
- v1 仍維護 6 個月，bridge 不需要立即遷移但應開始規劃

## Recommended Actions
- 在 2026-07-28 stable 發布前用 codemod 對 mcp-memory.ts 做試跑，評估遷移工作量
- 研究 multi-round-trip requests 是否能簡化 forget tool 的 two-phase confirm 流程
- 將 MCP v2 遷移加入 bridge roadmap，目標在 v1 EOL（約 2027-01）前完成
