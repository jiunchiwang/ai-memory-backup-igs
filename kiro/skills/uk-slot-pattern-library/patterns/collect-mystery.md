# Pattern: COLLECT 神秘事件

## 識別條件

規格書出現以下描述時匹配：
- 「停輪後觸發神秘事件」「Mystery Event」
- 「特定輪（通常第5輪/最後一輪）一格一格重轉」
- 「轉出更多 COLLECT 符號」
- 「條件：有 CASH + 無線獎 + 數量或金額達標」
- 「已有 COLLECT 不再重轉該格」

## 參考實作

| 專案 | 機制名 | 特殊點 |
|------|--------|--------|
| 3 Leprechaun's Pots（規格） | COLLECT 神秘事件 | 第5輪一格一格轉動，MG/FG 皆可觸發，條件門檻不同 |

### 核心檔案（3LP，規劃中）
- `GameState/CollectMysteryState.ts` — 神秘事件主 State
- `Feature/CollectMysteryManager.ts` — 第5輪逐格重轉邏輯 + 動畫控制
- `GameView.ts` → OnRecvSpinAck 解析 collectMystery 資料

## State 映射

**獨立 State**：`CollectMysteryState`

```
Feature 作用鏈（SCATTER_SHOW 之後，AWARD 之前）：
  → CollectMysteryState → BombEvent? → BombFeature? → Multiplier? → CollectFeature → Award
```

觸發位置：FeatureShowState 判斷 `hasCollectMystery` → 進入 CollectMysteryState。
完成後回到 Feature 作用鏈繼續後續步驟（新增的 COLLECT 會被後續 CollectFeature 收走）。

## Data 需求

```typescript
interface CollectMysteryData {
  /** 重轉方向（從上往下 or 從下往上） */
  direction: 'up' | 'down';
  /** 第5輪每格重轉結果（按演出順序） */
  reelResults: CollectMysteryCell[];
  /** 最終新增的 COLLECT 位置 */
  newCollectPositions: { col: number; row: number }[];
}

interface CollectMysteryCell {
  /** 格子位置（col 固定為最後一輪） */
  position: { col: number; row: number };
  /** 該格是否已有 COLLECT（已有則跳過不轉） */
  skip: boolean;
  /** 重轉結果 symbol ID */
  resultSymbol: number;
  /** 是否轉出 COLLECT */
  isCollect: boolean;
}
```

### 觸發條件（server 判定，client 不需自行計算）

| 條件 | MG | FG |
|------|----|----|
| 盤面有 CASH 符號 | ✅ 必要 | ✅ 必要 |
| 無線獎（非 line win 觸發） | ✅ 必要 | ❌ 不需要 |
| CASH 數量 ≥ N 或金額 ≥ M | ✅ 門檻（具體值待機率文件） | ✅ 門檻可能更低 |

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 神秘事件宣告（全屏提示/音效） | await spine（1~1.5s） | collectMystery != null |
| 2 | 聚焦第5輪，其餘壓暗 | 即時 | — |
| 3 | 第5輪從 direction 方向第1格開始旋轉 | — | — |
| 3a | 若該格已有 COLLECT → 跳過（高亮閃爍示意） | 即時 | cell.skip === true |
| 3b | 單格旋轉 0.5~1s → 停輪顯示結果 | await tween | cell.resultSymbol |
| 3c | 若轉出 COLLECT → 高亮 + 獎勵音效 | await spine（0.3s） | cell.isCollect |
| 3d | 若未轉出 → 靜默跳下一格 | 即時 | — |
| 4 | 重複 3a~3d 直到所有格跑完 | sequential await | reelResults.length |
| 5 | 新增 COLLECT 全體閃爍確認 | await spine（0.5s） | newCollectPositions |
| 6 | 還原壓暗，離開 State | 即時 | — |

## 常見變體

| 變體 | 差異 | 場景 |
|------|------|------|
| MG 神秘事件 | 門檻較高（CASH 數量+金額雙重限制） | BaseGame |
| FG 神秘事件 | 門檻較低，條件可能只需 CASH 存在 | FreeGame |
| 與 Bomb 事件互斥（停輪後型） | 同一手 BombEvent(afterStop) 觸發時跳過神秘事件 | FG Clover Bomb 特色 |
| 固定方向 vs 隨機方向 | direction 固定 up 或由 server 決定 | 依遊戲設計 |
| 單輪 vs 多輪 | 只重轉第5輪 vs 可能影響多輪 | 3LP 只有第5輪 |

## 邊界案例

1. **已有 COLLECT 的格子不重轉**：若第5輪本來就有 COLLECT，該格跳過，只轉沒有的格子
2. **全格都已有 COLLECT**：理論上不會觸發（server 不會在此情況下發 collectMystery 資料），但 client 需防禦性處理
3. **神秘事件後新增 COLLECT + 後續 CollectFeature 交互**：新增的 COLLECT 必須被後續 CollectFeatureState 正確識別並收分
4. **與 BombEvent 的時序**：停輪後型 BombEvent 觸發時，跳過神秘事件（互斥）；旋轉中型 BombEvent 不影響
5. **快停/skip 處理**：逐格演出可能耗時較長（3~5格 × 0.5~1s），turbo 模式需提供加速版（縮短為 0.2s/格）
6. **斷線重連**：若重連時正在播放神秘事件，需直接顯示最終結果（所有 COLLECT 就位），不重播逐格動畫
7. **Unshow/Replay 還原**：還原時需移除神秘事件新增的 COLLECT，恢復原始停輪盤面

## 常見錯誤

1. **❌ 把逐格重轉跟 Mystery 揭示搞混**：本 pattern 是完整重轉流程（需獨立 State + server 再次回傳結果），不是 mystery-symbol 的 0.5s 揭示動畫——流程、proto、State 都不同
2. **❌ 新增 COLLECT 沒傳給後續 CollectFeatureState**：神秘事件新增的 COLLECT 必須更新 plateInfo 讓後續 Collect 識別 → 忘了 = 新 COLLECT 不收分
3. **❌ Turbo 模式沒做加速版**：逐格演出 5 格 × 1s = 5s，turbo 必須壓到 5 格 × 0.2s = 1s；沒做 = turbo 模式跟一般一樣慢
4. **❌ skip 判定用 client 本地資料**：哪些格已有 COLLECT 應由 server 的 `cell.skip` 欄位決定，不可 client 看當前 plateInfo 自行判斷（可能與 server 不同步）
5. **❌ 與 BombEvent 互斥邏輯漏了**：停輪後型 BombEvent 觸發時需跳過神秘事件——忘了互斥 = 同一手又炸又重轉，結果混亂
