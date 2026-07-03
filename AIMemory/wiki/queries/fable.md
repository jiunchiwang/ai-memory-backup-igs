---
title: Claude Fable 5 修正 Karpathy P0 接線 Bug
type: query
created: 2026-07-04
updated: 2026-07-04
sources: [f_d274c6]
summary: Karpathy P0 三模組原始實作的接線 bug 清單及 Fable 的修正方式
---

# Claude Fable 5 修正 Karpathy P0 接線 Bug

## 背景

telegram-kiro-bridge 的 Karpathy Wiki 對齊三項 P0（activity-log / ingest-ripple / query-auto-save）由主 agent 實作後，存在多個「寫了模組但沒正確接上既有基礎設施」的問題。由 Claude Fable 5 兩個 commit 修正。

## Bug 清單與修正

| 模組 | 問題 | 根因 | 修正 |
|------|------|------|------|
| query-auto-save | `shouldSave` 永遠 false | 自己 `JSON.parse` topics.json 吃不下 JSONC 標頭 + 讀了 `name` 欄位（正確是 `topic`） | 改用 `getTopicRules()` 統一入口 |
| ingest-ripple | shard 檔名猜錯 | 硬猜 `topic.md` 格式 | 改用 `topicToFilename()` 正規化邏輯 |
| mcp-memory | factId 格式不一致 | 帶中括號 `[f_xxxxxx]` vs 裸 `f_xxxxxx` | 改用 `extractFactId()` + 手動組 |
| run-prompt | wiki auto-save 缺接線 | 完全沒 call `evaluateForAutoSave` | user 回合 + agent 沒加 WIKI_QUERY 時自動觸發 |
| commands/memory | wikisync prompt 沒注入候選 | `buildWikiSyncPrompt()` 沒讀 ripple/auto-save 資料 | 注入優先清單 + 完成後 `clearProcessedRipples` |
| commands/dream | 報告沒活動摘要 | 開頭缺呼叫 | 加 `getActivitySummary(24)` |
| activity-log | 讀寫路徑不對齊 | tool-observer 尊重 `BRIDGE_OBSERVATIONS_PATH` 但 activity-log 硬寫路徑 | export `observationsPath()` 共用 resolver |

## 教訓

1. **新模組不只是寫完 export** — 必須在消費端（run-prompt、commands、dream）接線才有用
2. **既有基礎設施優先** — 讀 topics.json 用 `getTopicRules()`、shard 檔名用 `topicToFilename()`，不要自己重寫解析
3. **格式一致性** — factId 在整個系統應有統一的裸格式（`f_xxxxxx`），中括號只在 master log 行首顯示用

## Commit 紀錄

- `d043253` — 修正 P0 三模組解析 bug + 補完生產端接線
- `d3c35c6` — activity-log 路徑讀寫不對齊

## 相關

- [[bridge-project]] — P0 三模組說明
- [[bridge-research]] — Karpathy Wiki 對齊 Roadmap
