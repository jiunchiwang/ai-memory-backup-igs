# Pattern: Feature Wheel（功能轉輪）

## 識別條件

規格書出現以下描述時匹配：
- 「WHEEL 符號」「轉輪符號」觸發功能轉輪
- 轉輪上有多種不同功能（符號轉換/乘倍/升級/FG 等）
- 功能之間有複合排序邏輯（非 Pick 選擇，是隨機停輪）
- MG/FG 版本功能項不同
- 「根據 WHEEL 數量決定轉幾次」

與 `bonus-game-pick.md` 的差異：Pick 是玩家主動選擇，Feature Wheel 是被動隨機停輪；
Wheel 結果不直接給獎金，而是觸發後續流程鏈（重轉 + 功能作用 + Collect）。

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| Eye Strike2（規格） | Feature Wheel | MG 4功能 + FG 4功能（FG 把 FG 項換成 GRAND JP） |
| Duck Hunters（競品） | 功能轉輪 | 類似多功能隨機停輪觸發 |

### 核心檔案（Eye Strike2，規劃中）
- `Feature/FeatureWheelManager.ts` — 轉輪 UI 控制、停輪動畫、結果派發
- `GameState/FeatureWheelState.ts` — 進入轉輪的獨立 State
- `GameView.ts` → 解析 wheelResults 資料

## State 映射

**獨立 State**：`FeatureWheelState`

```
MG 流程：
  CheckState（hasWheel && hasCollect）→ FeatureWheelState → [根據結果]
    → SymbolTransformState → RespinState → UpgradeState → MultiplierState → CollectFeatureState → Award

FG 流程：
  CheckState（hasWheel，不需 Collect）→ FeatureWheelState → [同上，但多 GRAND JP 選項]
```

多個 WHEEL 符號時：依序轉 N 次，結果全部收集後一次性按固定排序執行。

## Data 需求

```typescript
interface FeatureWheelData {
  /** WHEEL 符號位置（決定轉幾次） */
  wheelPositions: GridPosition[];
  /** 每次轉輪結果 */
  wheelResults: WheelResult[];
  /** 複合排序後的執行序列 */
  executionOrder: FeatureType[];
}

interface WheelResult {
  /** 轉輪停在哪個功能 */
  feature: FeatureType;
  /** 功能參數（標記的格子位置等） */
  targetPositions?: GridPosition[];
  /** 乘倍值（乘倍功能時） */
  multiplierValue?: number;
}

enum FeatureType {
  SymbolTransform = 1,  // 符號轉換
  Multiplier = 2,       // 乘倍
  CashUpgrade = 3,      // CASH 升級
  FreeGame = 4,         // 觸發 FG（MG 限定）
  GrandJP = 5,          // GRAND JP（FG 限定）
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | WHEEL 符號亮起，光飛向上方轉輪 | await tween(0.5s) | SpineKit |
| 2 | 轉輪開始旋轉 | — | — |
| 3 | 轉輪減速停在目標功能 | await(1~2s) | server 決定結果 |
| 4 | 功能宣告彈窗（MULTIPLIER/TRANSMUTE/UPGRADE） | await(1.5s) | — |
| 5 | 若多個 WHEEL → 重複 2~4 | await | — |
| 6 | 全部轉完，按固定排序執行功能鏈 | — | 見下方排序 |

### 功能複合排序（固定）

```
符號轉換 → 重轉 → CASH升級 → 乘倍 → Collect報獎 → FG流程
```

MG 與 FG 差異：
- MG：需 COLLECT+WHEEL 同時出現才觸發
- FG：只需 WHEEL 出現（不需 COLLECT）；效果跨 spin 保留

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 需要 COLLECT 才觸發 vs 直接觸發 | MG 需配對，FG 不需 | Eye Strike2 |
| 功能項固定 vs 可解鎖 | FG 轉輪可能升級（格子替換為 JP） | Eye Strike2 FG |
| 轉輪分區固定 vs 可變權重 | server 控制各功能機率 | 通用 |
| 單輪盤 vs 多圈輪盤 | 外圈選功能、內圈選參數 | 其他競品 |

## 邊界案例

1. **多 WHEEL 複合**：同一 spin 轉出 2+ 個 WHEEL，每個各轉一次→結果合併→按排序執行
2. **FG 觸發複合**：轉出 FG 功能時，其他功能先做完再進 FG 流程（FG 宣告提前，執行最後）
3. **GRAND JP 直接授予**：FG 版轉到 GRAND 時不走 Collect，直接彈報獎面板
4. **格子標記重疊**：同一格被轉換+乘倍同時標記，兩者都生效（先轉換再乘倍）
5. **無 COLLECT 時的 MG Wheel**：MG 有 WHEEL 但無 COLLECT → 不觸發（WHEEL 視為普通符號）

## 常見錯誤

1. **❌ MG 有 WHEEL 就觸發（忘記 COLLECT 前提）**：MG 必須 WHEEL + COLLECT 同時出現才觸發；只有 WHEEL 不觸發——忘了 = 無 Collect 的手浪費演出時間
2. **❌ 多 WHEEL 結果不排序就執行**：功能複合排序是固定的（轉換→重轉→升級→乘倍→收分→FG），亂序會導致轉換後的 CASH 沒被乘倍
3. **❌ GRAND JP 走 Collect 流程**：FG 轉到 GRAND 是直接授予（彈報獎面板），不走 Collect 收分路徑——走了 = 等不到 COLLECT 符號永遠卡住
4. **❌ 轉輪結果用 client 隨機**：停輪結果 100% server 預決定，client 只播動畫；用 Math.random = 跟 server 結算不匹配
5. **❌ FG 中忘記效果保留**：FG 的轉輪結果（格子標記）需跨 spin 保留（見 persistent-grid-effect）；MG 不保留——搞反 = MG 累積或 FG 不累積
