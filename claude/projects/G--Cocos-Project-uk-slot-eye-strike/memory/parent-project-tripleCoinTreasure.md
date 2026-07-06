---
name: parent-project-triplecointreasure
description: uk_slot_eye_strike 從 tripleCoinTreasure-client 改寫而來，偵錯時可對比原版找出改寫引入的 bug
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7654f70d-6a6c-4d7a-a1c7-608293d6c21d
---

uk_slot_eye_strike 專案是從 `G:/Cocos_Project/tripleCoinTreasure-client` fork 改寫而來，核心架構（SlotReels、FakeReelManager、ColumnSymbol、plate cycling 機制）大致同源。

**用途**：當這專案出現「邏輯怪怪的」bug 而又難找根因時，第一步可以去 grep 對應的 `tripleCoinTreasure-client/assets/Script/` 對應檔案，比對改寫差異。

**為何有效**：改寫過程常見模式是「把原版鬆散的 state 機制改嚴」「把混用 key 拆成 plate-specific key」之類，看似清理但容易破壞原版隱性平衡，引入邊界條件不可達的 bug。對比原版能快速定位是「新增的條件」還是「改過的判斷」造成的問題。

**實例**：2026-05-22 追「reel 5 兩個 Collect 視覺相近」bug 時，對比 `tripleCoinTreasure-client/SlotReels.ts:668` `CheckMoveLength` 跟本專案 `SlotReels.ts:2497`，發現本專案多了 `else if (ml-cl >= vh)` 嚴格 RESET 條件，對 up plate 數學上不可達 → state 卡死。原版 `else { state = true }` 無條件 reset 雖然會「每幀 TRIG」浪費效能但功能正確。
