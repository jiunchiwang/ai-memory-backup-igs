---
name: short-spin-up-plate-residual
description: short spin 時 up plate 沒機會 TRIG，殘留前手 server FakePlateSymbolUpper 內容，已評估為可接受設計侷限
metadata: 
  node_type: memory
  type: project
  originSessionId: 7654f70d-6a6c-4d7a-a1c7-608293d6c21d
---

**現象**：玩家在某些 spin 視覺上看到 reel 5 出現「兩個 Collect (Symbol 13) 中間 1-2 格」的近距離排列，violates「fakeReel 任兩同 symbol 最近距離 ≥ 5 indices」的直觀預期。

**根因**：plate cycling 機制中 up plate 的 `comparePos = totalLength × 2/3 ≈ 820` 很高。當 spin 動畫太短，`moveLength` 從 0 累積到結束前沒爬到 820，up plate 連一次 `ChangeSymbol` (TRIG) 都不會被觸發 → 沿用前手 spin 結束時的內容（通常是 server 給的 `RoundInfo.FakePlateSymbolUpper`，可能含 Collect）。

當本手 mid/low plate 新 fakeReel 內容剛好也含 Collect，且兩個 plate 各自 Collect 的 row 位置剛好讓視覺距離接近 → 出現「兩個 Collect 視覺相鄰」現象。

**Why（為何接受不修）**：2026-05-22 完整評估過所有修法選項，全部有副作用：
- 改 RESET 條件、wrap 偵測：已修（commit `5d0889c`），解了 state 卡死部分，但對「ml 沒爬到 820」這個物理現象無解
- StartSpin 強制 refresh up/low plate：會閃爍（[[reel-visible-mask-buffer]] 露出 buffer row）
- cycling 後跳轉瞬間 refresh：up5 沒 TRIG 過就沒「跳回頂部」瞬間，邏輯上做不到
- buffer 區全用 server 控制：大改設計，犧牲 buffer 隨機感
- 發生率約 1-2%（每 100 手 spin 約 1 次），影響可接受

**How to apply**：未來如果再有人回報「reel 5 兩個 Collect 視覺相近」，**不要重新追根究柢**，直接告訴他這是已知設計侷限。若客戶/設計強烈要求修，再評估「buffer 區改用 server 永久控制」或「拉長 spin 動畫保證 ml ≥ 820」這兩個方向。

**相關**：[[parent-project-tripleCoinTreasure]] 提供對比參考、[[reel-visible-mask-buffer]] 解釋為何 refresh 修法會閃爍
