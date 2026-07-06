# Pattern: Multiplier 格子

## 識別條件

- 盤面上特定位置帶有持續性乘倍標記（跨 spin 累加）
- 每手旋轉前隨機 1~3 個新位置被標記乘倍
- 已有乘倍的位置累加（×2 → ×3 → …）
- CASH symbol 停在乘倍格時，收分金額先乘再計入
- 作用順序固定：Bomb → Multiplier → Collect
- 兩種顏色效果框區分低倍/高倍

## 參考實作

| 專案 | 核心檔案 | 大小 | 說明 |
|------|----------|------|------|
| uk_slot_eye_strike | `MultiplierManager` | 65KB | 乘倍格完整實作，含累加邏輯與雙色特效 |

## State 映射

無獨立 State。乘倍格邏輯嵌入以下流程：

```
NormalSpinState → FeatureShowState（乘倍標記動畫）→ CollectState（乘倍計算）
```

- **FeatureShowState**：播放新增/累加乘倍的動畫
- **CollectState**：CASH 落在乘倍格時，先讀取倍率再計分

## Data 需求（proto 假設）

```typescript
interface MultiplierGridData {
  /** 本輪新增或累加的乘倍位置 */
  multiplierUpdates: MultiplierCell[];
  /** 全盤面當前乘倍狀態（含歷史累加） */
  currentGrid: MultiplierCell[];
}

interface MultiplierCell {
  /** 盤面位置 (col, row) */
  position: { col: number; row: number };
  /** 當前倍率值 */
  multiplier: number;
  /** 是否為本輪新增 */
  isNew: boolean;
  /** 效果等級：low=低倍色框, high=高倍色框 */
  tier: 'low' | 'high';
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 轉輪停止，結算 symbol 落點 | reel stop callback | NormalSpinState 完成 |
| 2 | Bomb 先作用（若有） | Bomb 演出完成 event | bomb-feature |
| 3 | 新乘倍格亮起（低倍色框） | tween 完成 | multiplierUpdates |
| 4 | 已有乘倍格累加動畫（數字翻轉+可能升色） | tween 完成 | currentGrid diff |
| 5 | CASH 落在乘倍格 → 倍率數字飛入 CASH | fly animation 完成 | CASH 位置 ∩ 乘倍位置 |
| 6 | 計算乘後金額，更新顯示 | 立即 | 計算完成 |
| 7 | 進入 Collect 流程 | CollectState enter | Step 6 完成 |

## 常見變體

| 變體 | 差異 | 範例 |
|------|------|------|
| 固定倍率格 | 不累加，每輪重新隨機 | 部分低波動機台 |
| 全盤乘倍事件 | 特殊觸發一次性全盤 ×2 | Feature trigger 獎勵 |
| 乘倍上限 | 累加到 ×10 後鎖定不再增長 | eye_strike 高倍上限 |
| 乘倍衰減 | 若該格 N 輪未被 CASH 觸發則降級 | 長 session 平衡設計 |
| 單色框 | 不區分高低倍，統一特效 | 簡化版 |
| 乘倍格觸發 Feature | 累加到閾值觸發額外獎勵 | Bonus 入口條件之一 |
| Bomb 產出 + Multiplier 連動 | Bomb 先在乘倍格產出/升級 CASH，再由 Multiplier 乘倍 | 3LP（Bomb→Multiplier→Collect 固定順序） |
| 擴展盤面乘倍 | 盤面 3x5→5x5 擴展後，新行也可被指定乘倍格 | 3LP Expand+Multiplier FG |
| 單手觸發型（Wheel 分配） | 非跨 spin 累加，由 Feature Wheel 單次分配格子+倍率；重轉後 CASH 落在標記格才乘。FG 中效果持續（見 persistent-grid-effect） | Eye Strike2 |

## 邊界案例

1. **同一格同輪多次累加**：Bomb 產出 CASH 落在已有乘倍格，需確認是先累加再乘還是用當輪初始倍率
2. **乘倍格滿盤**：所有位置都已有乘倍時，新增邏輯退化為純累加，不應報錯
3. **CASH 金額為 0**：乘倍 × 0 仍為 0，演出是否省略飛數字動畫
4. **Replay/Unshow 還原**：需將 currentGrid 回退到上一手狀態，累加歷史須可逆
5. **乘倍格 + Collect 同時觸發多格**：多個 CASH 同時落在不同乘倍格，演出是逐格播放還是並行
6. **斷線重連**：currentGrid 須由 server 完整下發，client 不可依賴本地累加歷史重建
7. **乘倍格 + JP 符號交互（3LP）**：JP 先轉分數再乘倍再被 Collect 收走，三步驟順序不可顛倒

## 常見錯誤

1. **❌ 乘倍在 Bomb 之前作用**：固定順序是 Bomb → Multiplier → Collect；乘倍先算會讓 Bomb 產出的新 CASH 跳過乘倍
2. **❌ Unshow 沒還原 currentGrid**：回退一手時 multiplier 累加歷史沒回退 → 下一手倍率從錯誤基數累加
3. **❌ 用 client 本地累加重建 grid**：currentGrid 必須由 server 每手完整下發，本地累加遇 race condition（如跳手）會漂移
4. **❌ 乘倍格視覺 tier 判定寫死**：高低倍色框的閾值應讀設定（如 ≥5x 換色），硬寫在 code 裡改規格要大動
5. **❌ 乘倍 × 0 不處理**：CASH value=0 時乘完仍為 0，若省略飛數字動畫需確保不影響後續 Collect 流程（位置仍要算入）
