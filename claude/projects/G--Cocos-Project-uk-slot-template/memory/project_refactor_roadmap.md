---
name: project-refactor-roadmap
description: SlotReels 重構進度 — Option 1 配置驅動已完成；Option 4 拆 component / Option 5 Entry-Fill 邊界釐清為待議項。
metadata: 
  node_type: memory
  type: project
  originSessionId: ebce2f83-747e-4bca-8821-5e3802f903dc
---

SlotReels.ts 過去是 2200+ 行 god class。本專案啟動了一系列重構，目前完成「Option 1：配置驅動架構」。

**Why**：原本 plate 層數寫死 `SHOW_COLUMNS=3`、`MIDDLE_PLATE_INDEX=1` 也寫死在 `Game_Define.ts`，導致 DropEntry 玩法（單層盤面）需要靠 hack（隱藏上下假盤面）才能用。Option 1 把這些移到 `assets/Script/ReelLayoutConfig.ts` 的 `ReelLayoutConfig` 介面，由 `SlotReel.SetLayoutConfig(REEL_LAYOUT_PRESETS.xxx)` 注入。

**How to apply**：
- 跟使用者繼續討論時，假設 Option 1 已完成、不需要再做。
- 「拆 SlotReels 成 Component（Option 4）」與「Entry/Fill 策略職責邊界釐清（Option 5）」**刻意延後**。延後理由：(1) 目前只有一個明確痛點被解決即可、(2) template 是給多個遊戲做基礎，動結構會牽動下游、(3) 還沒出現「連續 2-3 個新玩法都要動 SlotReels 才能加入」這類強推動信號。等真的撞到瓶頸再做。
- 不要主動建議重做 Option 1 已涵蓋的事（移除 SHOW_COLUMNS / MIDDLE_PLATE_INDEX 已完成；columnAlignment 已加入並驗證）。
- columnAlignment 預設值為 `'center'`，是使用者比較過 center / top / bottom 三種視覺後選的。其他兩種仍支援作為可配置選項。
- DropEntry preset 已端到端驗證（暫改 GameView 用 dropEntry preset 跑過 spin/cascade），確認 [[ReelLayoutConfig|`plateCount=1`]] 可行。

相關位置：`assets/Script/ReelLayoutConfig.ts`、`assets/Script/SlotReels.ts` 的 `SetLayoutConfig` / `MiddlePlateIndex` getter / `UpdateReelYPositions`。
