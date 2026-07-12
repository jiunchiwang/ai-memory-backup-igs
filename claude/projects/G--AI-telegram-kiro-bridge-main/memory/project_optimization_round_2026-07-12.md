---
name: bridge-optimization-round-2026-07-12
description: 2026-07-12 優化輪 8 commits 全修完（9ab3e88..f9efd87）；ACP_TRACE 改 opt-in 部署要知道；enrichment 全量合併刻意 deferred
metadata: 
  node_type: memory
  type: project
  originSessionId: 47f67988-fe00-45d3-acdc-cbfe4807346e
---

2026-07-12 優化輪（接續 [[bridge-review-handoff-2026-07-11]]）：兩個 agent 掃描
（審後 5 commits 審查 + 全庫效能掃）→ 7 項全修完，commits `9ab3e88..f9efd87`，
tsc + 15+ smoke scripts 全綠。內容：embedding size-1 快取、status 空燒修復、
tool title fallback 收緊、ACP trace gate、token 估算去重、啟動 init 並行化、
重複碼抽取（makeMetaCtx / dispatchRelayResults / goal 記帳 / prefix cap）。

**Why（部署與後續要知道的）**：
- `ACP_TRACE` 磁碟寫入改 opt-in（預設關）——之後要跑
  `check-acp-trace-orphan.mjs` 診斷前必須先設 `ACP_TRACE=1` 收集；
  舊 trace 檔 >7 天啟動自動清。
- bot 現在**先上線再暖 embedding**：啟動初期幾秒~幾十秒 enrichment 是
  degraded（isReady guard 跳過），屬預期行為非 bug。

**How to apply（deferred 決策）**：
- index.ts enrichment 區與 `runEnrichment` 的**全量合併刻意不做**：兩邊
  dedup 語意不同（`injectedWikiSlugs`/`tailFacts` vs `recentFacts` 前綴
  key、recall 是否寫回 set、主路徑無 index retrieval 階段）——合併是行為
  變更，要做需獨立決策；本輪只補了主路徑 prefix cap + 修 routing 命中丟
  replyContextBlock 的 bug。
- `electron` 在 devDependencies 但 `pet-server.ts` runtime spawn 它：
  `npm install --omit=dev` 部署時 pet 功能靜默壞（pet 為選配，未動）。
- 靜態解析 src 的 smoke script（如 check-relay-done-reply）錨點易被重構
  弄壞且壞了沒人發現——該 script 曾在 75a5428 後靜默失效，本輪已修錨。
