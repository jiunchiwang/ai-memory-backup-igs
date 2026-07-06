# Pattern: Wild 變身

## 識別條件

規格書出現以下描述時匹配：
- 「符號變身為 Wild」「角色升級為百搭版本」
- 「特定條件下普通符號轉換為 Wild」
- 「Wild 只取代一般符號」
- 「觸發條件後指定符號升級為帶 Wild 功能的版本」

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| uk_722_robinhood | SymbolChange.ts | 3種角色各有 Wild 版（RobinHood→WildRobinHood 等），FG 期間觸發 |
| uk_746_far_west | WildExpand | 特定列整列變 Wild（Expanding Wild） |

### 核心檔案（722 robinhood）
- `SymbolChange.ts` — 變身邏輯與動畫觸發
- `Game_Define.ts` → Symbol enum 含 WildRobinHood(12), WildLittleJohn(13), WildTucker(14)
- `PlateShowState.ts` → 停輪後 checkWildTransform() 判定

## State 映射

**不需要獨立 State**。在 `PlateShowState` 或 `FeatureShowState` 中處理：
- 停輪後、對獎前，執行變身動畫
- 變身完成後替換 plateInfo 中的 symbolId
- 再走正常對獎流程

```
SpinState（停輪完成）→ PlateShowState
  → checkWildTransform()
  → 有變身? → 播動畫 → 更新 plateInfo → AwardState
  → 無變身? → 直接 AwardState
```

## Data 需求

```typescript
interface WildTransformResult {
  /** 本手所有變身資料 */
  transforms: WildTransformEntry[];
  /** 觸發條件類型（server 判定） */
  triggerType: WildTransformTrigger;
}

interface WildTransformEntry {
  col: number;
  row: number;
  fromSymbol: number;   // 原始符號 ID
  toSymbol: number;     // 變身後 Wild 版本 ID
}

enum WildTransformTrigger {
  /** 角色升級（特定符號→Wild 版本） */
  CharacterUpgrade = 0,
  /** 隨機觸發（server 隨機選格） */
  Random = 1,
  /** 條件觸發（如 FG 中每手固定轉） */
  Conditional = 2,
  /** Feature 觸發（如 Feature Wheel 結果） */
  FeatureTriggered = 3,
}
```

### 與 symbol-transform.md 的差異

| | Wild 變身 | Symbol Transform |
|--|-----------|-----------------|
| 語意 | 一般符號→Wild 版本（獲得百搭能力） | 任何符號→另一種符號（身份更換） |
| 對獎影響 | 變身後可替代任何一般符號連線 | 變身後以新身份參與對獎 |
| 典型來源 | 固定角色映射（RobinHood→WildRobinHood） | server 決定目標符號（可為 Cash/JP） |

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 全部停輪完成 | — | SpinState 結束 |
| 2 | 符合條件的符號高亮/發光 | await tween(0.3s) | transforms[] |
| 3 | 播放變身 Spine 動畫（所有格同時） | await spine（0.5~1s） | SpineKit |
| 4 | 替換為 Wild 版本圖片（更新 plateInfo） | 即時 | SymbolChange |
| 5 | 進入正常對獎流程 | — | CheckState/AwardState |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 角色→Wild角色 | 保留角色形象但加 Wild 標記，有固定映射表 | 722 robinhood |
| 隨機變身 | 每手隨機 N 格變 Wild（server 選位） | — |
| 條件觸發 | 特定事件/Feature 觸發才變（如 Feature Wheel 結果） | Eye Strike2 |
| Sticky Wild | 變身後保留到下一手（跨 spin 持久） | Respin 類遊戲 |
| Expanding Wild | Wild 擴展到整列（停輪後整列替換） | 746 far_west |
| Cascading Wild | 消除後 Wild 不消失、留在原位 | Tumble 類遊戲 |

## 邊界案例

1. **Wild 不取代 Scatter/特殊符號**：變 Wild 後對獎只替代一般符號，Scatter/Bonus/Collect 等不被替代
2. **變身後的對獎**：plateInfo 需先更新再跑 Award 邏輯——順序錯會導致連線計算用到舊 symbolId
3. **Unshow 還原**：變身後的 unshow 需回復原始符號（從 transforms[].fromSymbol 還原）
4. **FG 中行為差異**：722 的 Wild 變身只在 FG 觸發；若 MG 也有需確認觸發條件是否不同
5. **與 Mystery 的差異**：Mystery 是「佔位符號停輪後揭示身份」；Wild 變身是「已有身份的符號升級為 Wild 版本」——觸發時機、動畫語意、proto 結構都不同
6. **多個同時變身**：通常一起播動畫（不逐顆），節省演出時間；但需確保 plateInfo 批次更新不漏格
7. **與 Multiplier/Collect 交互順序**：Wild 變身 → 對獎計算（含 Wild 替代）→ Multiplier 作用 → Collect 收分；變身必須最先做
8. **Expanding Wild 整列替換**：整列變 Wild 時 plateInfo 該列所有 row 都要更新，且原始符號全部記錄（unshow 用）
9. **斷線重連**：RecoverSpinAck 需直接顯示變身後狀態，不重播動畫

## 常見錯誤

1. **❌ 對獎前忘記更新 plateInfo**：只播了動畫但沒把 symbolId 寫回 plateInfo → 連線判定用到舊值 → 少算贏分
2. **❌ Unshow 忘記還原**：Wild 變身後的 unshow 沒回復 fromSymbol → 下一手視覺殘留 Wild 但實際已非 Wild
3. **❌ 把 Wild 變身與 Mystery 用同一套流程**：兩者 proto 結構不同（Mystery 帶 revealSymbol + revealValue，Wild 變身帶 fromSymbol/toSymbol 映射）、觸發時機可能不同，共用會導致邏輯糾纏
4. **❌ Expanding Wild 只改中間行**：整列擴展時漏掉 row 0 或最後一行（特別是不等高盤面如 eye_strike 的 5-4-4-4-4-5）
5. **❌ Wild 替代了 Scatter 參與連線**：Wild 的替代規則是「只替代一般符號」，必須在對獎邏輯排除 Scatter/Bonus/Collect 等特殊符號
