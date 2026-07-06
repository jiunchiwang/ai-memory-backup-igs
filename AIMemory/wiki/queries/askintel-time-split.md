---
title: Intel 排程分割策略
type: query
created: 2026-07-05
updated: 2026-07-05
sources: [f_b966f9]
---

# Intel 排程分割策略

## 問題

Daily Intel 有三個 profile（`ai`、`game-industry`、`topic-ai`），如何排程避免早晨資訊過載？

## 決策

採用 **split 策略**：輕量 daily + 重量 podcast 隔天。

| Profile | 類型 | 頻率 | Cron |
|---|---|---|---|
| `ai` | 輕量 report | 每日 08:00 | `0 8 * * *` |
| `game-industry` | 輕量 report | 每日 08:00 | `0 8 * * *` |
| `topic-ai` | podcast（較重） | 隔天 08:00 | `0 8 */2 * *` |

## 設計理由

- `ai` 和 `game-industry` 是純文字摘要，生成快、閱讀負擔小 → 每日
- `topic-ai` 是 podcast 模式（需要 TTS + 更長的分析），生成慢且內容重 → 隔天
- 全部排 08:00 確保起床後有新鮮資訊，但不在深夜打擾

## 相關

- [[bridge-project]] — Daily Intel 情報排程設定
