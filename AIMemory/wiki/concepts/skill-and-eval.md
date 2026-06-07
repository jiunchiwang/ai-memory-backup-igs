---
title: Skill 評估與管理
type: concept
created: 2026-06-08
updated: 2026-06-08
sources: [f_73e043, f_e6ba59, f_cb10bc, f_af99c8, f_ed0429, f_8f81fa]
---

# Skill 評估與管理

## 概述

使用者持續評估外部工具與方法論，決定哪些值得整合進 agent skill 系統。評估標準偏務實：有明確需求才裝，避免過度囤積。已安裝的 skill 透過 [[bridge-project]] 的 `/skilllint` 追蹤使用狀態。

## 已整合的方法論

### SkillOpt 迭代原則

微軟 SkillOpt 論文的核心概念已整合進 `writing-skills` SKILL.md，用於指導 skill 的撰寫與迭代改進流程。

### IGS 內訓教材萃取

從「從LLM到AI_Agent.pdf」（IGS 小葉內訓教材，商用魚機 RD7 部門 7 週內訓）萃取了 4 個 skill：
- `dual-skill-review-loop` — 產出物自評迭代
- `non-engineer-agent-design` — 非工程師 agent 設計
- `knowhow-accumulation` — 經驗累積結構化
- `self-eval-prompt-pattern` — 自評 prompt 模式

## 評估後暫緩的工具

| 工具 | 決定 | 理由 |
|------|------|------|
| 微軟 Webwright（瀏覽器自動化） | 暫不安裝 | 目前無明確需求 |
| Claude Code Dynamic Workflows | 只借鏡 cross-check | 架構定位不同、規模不需要動態 delegation plan |

## UI/UX 設計輔助

已安裝 `ui-ux-pro-max` skill 到 `~/.kiro/steering/`（透過 uipro-cli），提供 HTML 頁面設計時的配色、字型、佈局建議。裝在 steering/ 而非 skills/ 是該工具的設計（含 Python 腳本搜尋資料庫）。

## Orphan 追蹤

`ms-wiki-knowledge-base` 曾是使用頻率最高的 skill（use_count=18~24），SKILL.md 已刪除但 `.usage.json` 紀錄殘留（orphan 狀態）。其功能已內化到 bridge preamble 和 `/wikisync`、`/wikilint` 等指令中。

## 相關

- [[bridge-project]] — skill 的宿主系統，提供 `/skilllint`、`/skillusage` 等管理指令
- [[uk-slot]] — 主要消費 skill 的開發領域
