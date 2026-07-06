# Pattern: Symbol Transform（符號轉換）

## 識別條件

規格書出現以下描述時匹配：
- 「符號轉換」「Transmute」「一般符號→CASH 符號」
- 「標記格子，盤面上所有相同符號被轉換」
- 「CASH→Mystery 升級」「分數升級」
- 轉換後通常搭配一次重轉

與 `wild-transform.md` 的差異：Wild 變身目的是替代對獎（增加 WAYS），
Symbol Transform 目的是產出更多 CASH/Mystery 給 Collect 收分。機制完全不同。

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| Eye Strike2（規格） | 符號轉換 + CASH升級 | 由 Feature Wheel 觸發，標記 N 格→同符號全轉 CASH→重轉 |
| Eye Strike2（規格） | CASH 升級 | 標記格子上的 CASH 升級為 Mystery（反向轉換） |

### 核心檔案（Eye Strike2，規劃中）
- `Feature/SymbolTransformManager.ts` — 轉換邏輯 + 動畫控制
- `GameState/SymbolTransformState.ts` — 執行轉換的 State（含重轉）
- `EffectPlate.ts` → 格子標記視覺效果

## State 映射

**可獨立 State 也可嵌入 FeatureShowState**：

```
FeatureWheelState → SymbolTransformState
  → 標記格子 → 轉換動畫 → 觸發重轉（RespinState）→ 下一功能
```

若不需獨立 State（簡單實作）：
```
FeatureShowState 內部 switch(featureType) 處理
```

## Data 需求

```typescript
interface SymbolTransformData {
  /** 被標記的格子（由 Wheel 或 server 決定） */
  markedPositions: GridPosition[];
  /** 轉換類型 */
  transformType: TransformType;
  /** 原始符號 ID（被轉換的） */
  sourceSymbolId?: number;
  /** 盤面上所有被影響的位置（同符號擴散） */
  affectedPositions: GridPosition[];
  /** 轉換後的 CASH 值（每格可不同） */
  resultValues?: number[];
}

enum TransformType {
  NormalToCash = 1,   // 一般符號 → CASH
  CashToMystery = 2, // CASH → Mystery（升級）
}
```

## 演出時序

### 符號轉換（Normal → CASH）

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 被標記格子亮起（右下角顯示轉換標記） | await(0.3s) | — |
| 2 | 標記格子上的符號辨識 → 盤面同符號全部高亮 | await(0.5s) | — |
| 3 | 高亮符號播轉換動畫（變為 CASH） | await spine(0.8s) | SpineKit |
| 4 | 顯示 CASH 符號+金額 | 即時 | — |
| 5 | 觸發重轉（鎖定 COLLECT+已有 CASH，其餘重轉） | → RespinState | — |

### CASH 升級（CASH → Mystery）

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 被標記格子亮起（右下角顯示升級標記） | await(0.3s) | — |
| 2 | 重轉完成後，檢查標記格是否有 CASH | 即時 | — |
| 3 | 有 CASH → 播升級動畫（底部刷光 → Mystery） | await(0.8s) | SpineKit |
| 4 | 無 CASH → 不發生任何事 | 即時 | — |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 全盤同符號轉換 | 標記格上的符號→盤面所有相同的都轉 | Eye Strike2 |
| 僅標記格轉換 | 只影響被標記的格子本身 | 其他競品 |
| 轉換後重轉 vs 不重轉 | Eye Strike2 帶重轉；簡單版可不重轉 | — |
| 單向 vs 雙向 | Normal→CASH（轉換）、CASH→Mystery（升級）是兩種 | Eye Strike2 |
| FG 效果保留 | 標記在 FG 中跨 spin 持續（見 persistent-grid-effect） | Eye Strike2 FG |

## 邊界案例

1. **標記格無一般符號**：被標記的格子上是特殊符號（COLLECT/WHEEL 等）→ 不轉換、不擴散
2. **重轉後才檢查升級**：CASH 升級的作用時機在重轉之後，若重轉沒落在標記格→不作用
3. **複合排序**：符號轉換排在乘倍之前（先轉再乘）
4. **FG 累積**：FG 中被標記的格子效果保留到 FG 結束，每 spin 自動作用
5. **多格標記重疊**：同一格被轉換+升級同時標記，以排序靠前的先作用

## 常見錯誤

1. **❌ 標記格上是特殊符號也轉換**：COLLECT/WHEEL/SCATTER 等特殊符號不應被轉換——忘了排除 = 特殊符號消失 + 遊戲邏輯異常
2. **❌ 升級在重轉之前作用**：CASH 升級的時機是重轉之後（新 CASH 可能落在標記格）；提前作用 = 新 CASH 不受升級影響
3. **❌ FG 累積效果用 client 本地 Map**：效果狀態需 server 每 spin 回傳快照同步，本地 Map 斷線重連後丟失
4. **❌ 擴散邏輯用 client 自算「同符號」**：哪些位置受影響應由 server 的 affectedPositions 決定；client 自己 grep 盤面可能跟 server 結果不同（如同時有其他 Feature 先改了符號）
5. **❌ 轉換順序放在乘倍之後**：固定排序是符號轉換→重轉→升級→乘倍→收分；轉換放後面 = 產出的 CASH 跳過了本手乘倍
