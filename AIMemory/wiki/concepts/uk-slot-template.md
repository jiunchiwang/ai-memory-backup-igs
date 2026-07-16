---
title: UK Slot 模板專案
type: concept
created: 2026-07-15
updated: 2026-07-16
sources: [f_967ccc, f_e8b2cf, f_991386, f_500f52, f_7e491d, f_233d31, f_4cfe4c, f_0376d5, f_8b54ac, f_6a6988]
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

## 架構決策（2026-07-15）

- **盤面可見性策略**：Server 端只送出玩家可見的盤面資料（例如 5x6），而非完整盤面尺寸（例如 7x6），其餘部分由客戶端做前處理——用於降低頻寬並支援遮罩效果
- **MaskExpand 多重遮罩**：`MaskExpand` 元件需支援多重遮罩（multi-mask），而非僅單一遮罩；此設計曾因疑慮被使用者還原一次，後續於 `IMaskExpandHost` 介面新增 `SetVisibleSymbolCountOverride()` 方法（`IMaskExpander.ts`），用以橋接本地與遠端架構的可見符號數量覆寫機制

## 相關

- [[uk-slot]] — 專案群總覽
- [[uk-slot-codegen]] — codegen 工具（依賴模板路徑）
