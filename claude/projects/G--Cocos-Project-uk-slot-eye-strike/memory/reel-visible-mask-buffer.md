---
name: reel-visible-mask-buffer
description: reel visible mask 不是剛好 5 cells，會多露出上下 plate 各約 1 row 多一點 buffer
metadata: 
  node_type: memory
  type: project
  originSessionId: 7654f70d-6a6c-4d7a-a1c7-608293d6c21d
---

reel 5 (跟 col 0、col 5) 的 visible mask 範圍 = **middle plate 5 cells + 上下各露出約 1 row 多一點 buffer**（不是剛好 5 cells）。

具體：
- 上方 mask 邊緣會露出 up plate row 4（最下一 row）的一部分
- 下方 mask 邊緣會露出 low plate row 0（最上一 row）的一部分

**Why**：slot UX 設計慣例，給玩家「reel 還有更多 symbol 在轉」的暗示。所以渲染區實際比 visible 5 cells 略大。

**How to apply**：
- 規劃 plate refresh / 改視覺呈現時，**不能假設 up/low plate 完全在 mask 外**——row 4 / row 0 會被看到
- 在 spin 進行中（特別是 raise 階段，plate 抬升讓 buffer 露出更多）對 up/low plate 做 `SetSymbolInfos` refresh 會被玩家看到瞬切（閃爍）
- StartSpin 那一瞬間 refresh up/low plate 也會被看到（reel 從靜止 → spin 的視覺切換點）
- 與此相關：[[parent-project-tripleCoinTreasure]] 對比可以理解 plate 機制如何演化，[[short-spin-up-plate-residual]] 是因這條約束無法簡單修的具體 case
