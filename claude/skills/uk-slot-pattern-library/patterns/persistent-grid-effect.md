# Pattern: Persistent Grid Effect（格子效果持續）

## 識別條件

規格書出現以下描述時匹配：
- 「效果保留直到 FG 結束」「格子上的效果跨 spin 持續」
- 「已被標記的格子下一手自動作用」
- 「乘倍/轉換/升級標記在 FG 中累積」
- 格子右下角有常駐視覺標記（圖示區分效果類型）
- 與單次觸發的 multiplier-grid 差異：此 pattern 是多種效果共用一套持續系統

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| Eye Strike2（規格） | FG 保留效果 | 3 種效果（轉換/乘倍/升級）跨 spin 累積到 FG 結束 |

### 核心檔案（Eye Strike2，規劃中）
- `Feature/PersistentEffectManager.ts` — 全盤面效果狀態追蹤（Map<position, Effect[]>）
- `UI/GridEffectMarker.ts` — 格子右下角常駐標記 UI
- `GameState/ApplyPersistentEffectState.ts` — 每 spin 自動作用已有效果

## State 映射

**嵌入既有流程**：不一定需要獨立 State，但建議有明確的作用時機：

```
FG 每 spin 流程：
  停輪 → FeatureWheelState（新增效果）→ ApplyPersistentEffects → Respin → Collect → Award

ApplyPersistentEffects 位置：
  - 若有 COLLECT 符號 → 觸發重轉 + 作用所有已標記效果
  - 若無 COLLECT 符號 → 跳到 Award（格子效果保留但不作用）
```

FG 結束時 `PersistentEffectManager.reset()` 清除所有標記。

## Data 需求

```typescript
interface PersistentEffectGrid {
  /** 全盤面效果狀態（server 每 spin 回傳最新快照） */
  effects: PersistentEffect[];
}

interface PersistentEffect {
  position: GridPosition;
  type: PersistentEffectType;
  /** 乘倍值（type=Multiplier 時） */
  multiplier?: number;
  /** 此效果是否為本輪新增 */
  isNew: boolean;
  /** 累積來源（第幾 spin 加的，debug 用） */
  addedAtSpin?: number;
}

enum PersistentEffectType {
  Transform = 1,   // 轉換：格子上出現一般符號時自動轉 CASH
  Multiplier = 2,  // 乘倍：格子上 CASH 被收集時乘以倍率
  Upgrade = 3,     // 升級：格子上 CASH 自動升級為 Mystery
}
```

## 演出時序

### 新增效果（Wheel 轉出後）

| Step | 動作 | 等待方式 |
|------|------|---------|
| 1 | 格子亮起，右下角飛入效果標記 icon | await(0.3s) |
| 2 | 標記 icon 落定並常駐顯示 | 即時 |

### 每 spin 自動作用

| Step | 動作 | 等待方式 |
|------|------|---------|
| 1 | 停輪完成 | — |
| 2 | 有 COLLECT 符號 → 逐格檢查已標記格子 | 即時 |
| 3 | Transform 格：若有一般符號 → 轉換動畫 → 變 CASH | await(0.5s) |
| 4 | 觸發重轉（鎖定 COLLECT+CASH，餘位重轉） | await |
| 5 | Upgrade 格：重轉後若有 CASH → 升級為 Mystery | await(0.5s) |
| 6 | Multiplier 格：標記倍率（Collect 階段才實際乘算） | 即時 |
| 7 | → CollectFeatureState 正常收分 | — |

### FG 結束

| Step | 動作 |
|------|------|
| 1 | 所有格子標記同時淡出 |
| 2 | PersistentEffectManager.reset() |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 乘倍累加 | 同一格多次被標記乘倍 → 倍率相加（×2+×3=×5） | Eye Strike2 |
| 單一效果 vs 多效果共存 | 同一格可同時有轉換+乘倍 | Eye Strike2 |
| 有 COLLECT 才作用 vs 每 spin 作用 | Eye Strike2 需要 COLLECT 才觸發已標記效果 | — |
| 效果可覆蓋 vs 疊加 | 轉換覆蓋（不重複標記）、乘倍疊加 | Eye Strike2 |
| 視覺升級 | 高倍格子（≥5x）換色框或加特效 | 通用 |

## 邊界案例

1. **無 COLLECT 時效果不作用**：FG 中即使有 CASH 在標記格，若無 COLLECT 符號→效果保留但不觸發
2. **效果疊加上限**：設計上可能有倍率上限（如 ×99），需確認規格
3. **FG 結束 timing**：最後一 spin 的效果正常作用→結算→然後才清除
4. **SUPER FG 共用**：Super FG 和一般 FG 共用同一套持續系統，差別只在局數
5. **重轉與效果交互**：重轉出的新 CASH 若落在已標記格→該效果立即適用（不等下一 spin）

## 常見錯誤

1. **❌ 無 COLLECT 時仍觸發格子效果**：Eye Strike2 規格明確要求「有 COLLECT 符號才作用已標記效果」；無 COLLECT 時效果保留但不觸發——忽略 = 每 spin 都作用（多送獎金）
2. **❌ FG 結束忘記 reset**：PersistentEffectManager 所有格子標記必須在 LeaveFreeState 清除；忘了 = 下次 FG 繼承上次殘留標記
3. **❌ 乘倍效果在 Collect 之前就乘了**：Multiplier 格子的作用時機是 Collect 收分時（被收走的 CASH 才乘）；提前乘 = 非 Collect 的贏分被多乘
4. **❌ 新增標記和本 spin 的作用混在同一步**：Wheel 轉出新標記→本 spin 的新標記「下一手才作用」（部分規格）或「本手即作用」（依遊戲）→ 搞錯時機 = 效果多/少觸發一手
5. **❌ 效果狀態純 client Map 沒讀 server 快照**：server 每 spin 回傳 effects 快照，client 必須以此為準；純本地累加會因斷線/race condition 導致漂移
