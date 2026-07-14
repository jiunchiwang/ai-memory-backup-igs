---
title: UK Slot 模板專案
type: concept
created: 2026-07-15
updated: 2026-07-15
sources: [f_946c9d, f_946c9e, f_946c9f, f_85a1b2, f_102c3d, f_105d4e, f_107e5f, f_133f60]
---

# UK Slot 模板專案

`uk_slot_template` 位於 `G:\Cocos_Project\uk_slot_template`，是所有 [[uk-slot]] 遊戲的 fork 來源。Cocos Creator 3.6.2 + Astarte Framework + TypeScript。

## 核心特性

- **三種轉輪玩法**：Standard（傳統滾動）、Cascade（消除天降）、Tumble（快速掉落+乘倍），透過 `FillStrategy` 策略模式切換
- **命名規範**：方法/函式使用 PascalCase（大駝峰）
- **音訊決策**：MG_Bgm / FG_Bgm 引用先註解掉（模板不附實際音檔），新遊戲需要 BGM 時再解除註解

## 起新專案慣例

```
git archive → git init 全新 repo
  → Tools_SlotSetUP/FirstClone.bat（clone slotExtensions-client → extensions/）
  → npm install
  → 改 GameId / 盤面 / FillStrategy
```

⚠️ `FirstClone.bat` 的 `../extensions` 相對於執行時 cwd——需在 `Tools_SlotSetUP/` 內執行，從專案根跑會 clone 到上一層。

## 回灌工作流

| 修正層級 | 回灌目標 |
|---------|---------|
| 模板級（工具/守衛/寫死值） | 同步回 uk_slot_template |
| 流程級教訓 | AI-canonical-corp skill 正本 |
| 專案級踩坑 | 專案 AI.md |
| 模式級修正 | pattern-library 卡片 |

## 待處理

- 4 個本地 commit 未 push（org 共用 repo IGS-ARCADE-DIVISION-RD2，push 前需使用者確認）
- demo 流程綁 eyestrike proto（6 欄盤面）——衍生遊戲改 COL 後轉輪驗證應走 ReelDevTool 假盤

## 相關

- [[uk-slot]] — 專案群總覽
- [[uk-slot-codegen]] — codegen 工具（依賴模板路徑）
