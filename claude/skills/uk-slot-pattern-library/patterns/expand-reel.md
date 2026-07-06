# Pattern: 盤面擴展 (Expand)

## 識別條件

規格書出現以下描述時匹配：
- 「盤面擴張/擴展」「3×5 → 5×5」「增加行數」
- 「FG 中盤面變大」
- 「上下各增加一排」

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| uk_739_wrath_of_thunder | ReelMode 系統 | 4種模式（4x6→5x6→6x6→7x6），漸進擴展 |

### 核心檔案（wrath_of_thunder）
- `SlotReels.ts` → `ReelSystemConfig` class + `SwitchReelMode()` API
- `SlotReels.ts` → `SetMaskHeightByMode()` 遮罩動畫
- `SlotReels.ts` → `AdjustColumnSymbolCounts()` 符號數量調整

## State 映射

**不需要新 State**。盤面擴展是 SlotReels 的內建能力。

觸發位置：
- `EnterFreeState.OnEnter()` → `SlotReels.SwitchReelMode(targetMode)`
- `LeaveFreeState.OnEnter()` → `SlotReels.SwitchReelMode(originalMode)` 回復

## Data 需求

```typescript
// 不需要額外 proto — 盤面大小由觸發的 FG 類型決定（client 本地邏輯）
// 但 server 回傳的 plateInfo 行數需對應擴展後的盤面

// SlotReels 內建
enum ReelMode {
    To3x5 = 'to3x5',  // MG 原始盤面
    To5x5 = 'to5x5',  // FG 擴展盤面
}

const ReelModeMaskHeight = {
    [ReelMode.To3x5]: 246,   // 3行 × 82px
    [ReelMode.To5x5]: 410,   // 5行 × 82px
};

interface ReelModeConfig {
    columns: { targetSymbolCount: number, visibleSymbolCount: number }[];
    maskExpandDirection: MaskExpandDirection;  // Up / Down / Both
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 進入 FG 轉場動畫 | await spine | FreeGameDeclareManager |
| 2 | 呼叫 `SwitchReelMode(To5x5)` | — | — |
| 2a | 遮罩 tween 擴張（0.2s, easing: smooth） | await tween | UITransform |
| 2b | 調整 ColumnSymbol 數量 | 即時（跟 2a 同步） | — |
| 3 | FG 場景就緒，開始第一手旋轉 | — | — |
| ... | FG 結束 | — | — |
| N | 呼叫 `SwitchReelMode(To3x5)` 回復 | await tween(0.2s) | — |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 漸進擴展（每手可能再擴） | 4→5→6→7 逐步 | wrath_of_thunder |
| 一次擴展（進 FG 直接到位） | 3→5 一步到位 | 3LP |
| 上擴 vs 下擴 vs 雙向 | MaskExpandDirection | 依遊戲設計 |
| 不等高列（Megaways 風格） | 每列 visibleSymbolCount 不同 | — |
| 擴展搭配 +1 SPIN 符號 | 擴展區才有 +1 SPIN | 3LP |
| 擴展搭配 Multiplier 格 | 擴展出的新行可被指定乘倍格 | 3LP（Expand+Multiplier FG） |

## 邊界案例

1. **FakeReelManager 需同步切換**：擴展後的假轉輪帶行數要對應（ROW=5 not 3）
2. **回 MG 時符號位置 reset**：切回小盤面時多餘符號要清除
3. **RecoverSpinAck**：斷線重連時需根據 IsFG 決定用哪個 ReelMode
4. **EffectPlate 座標系**：中獎框/飛行特效的 Y 座標需對應擴展後的位置
5. **NearMiss 聽牌**：擴展盤面的聽牌門檻可能不同（更多格子）
6. **上下擴展同時**：wrath_of_thunder 只做向上擴，3LP 需要上下同時（可能需擴展 MaskExpandDirection enum）
7. **+1 SPIN 符號只出現在擴展行**：3LP 規格限定 +1 SPIN 只能出現在擴展出的 row 0 和 row 4，FakeReel 帶需對應

## 常見錯誤

1. **❌ FakeReelManager 沒隨盤面同步切換**：擴展後 FakeReel 仍用 3 行帶→旋轉期間符號數不對→視覺跳動
2. **❌ 回 MG 時忘記 SwitchReelMode 回去**：LeaveFreeState 漏呼叫 → MG 盤面永久變大 → 與 server 的 plateInfo 行數不匹配
3. **❌ EffectPlate Y 座標沒重算**：擴展後中獎框用舊座標 → 框偏移到符號外面
4. **❌ RecoverSpinAck 不判 IsFG 就套用預設 ReelMode**：斷線重連在 FG 中間→盤面應已擴展但顯示成小盤面
5. **❌ 擴展方向硬寫 Up**：3LP 需要上下同時擴（row 0 + row 4），只做向上會少一行
