# Template API Reference

Template（uk_slot_template）的關鍵 API 簽名與配置結構。只在 Step 3 coding 時讀取。

---

## SlotReels

### ReelLayoutConfig

```typescript
interface ReelLayoutConfig {
  plateCount: number;           // 1(DropEntry) 或 3(Standard)
  columns: ColumnConfig[];      // 長度 = COL
  columnAlignment: 'center' | 'top' | 'bottom';
  fakeSymbolStrategy: 'random' | 'repeat';
}

interface ColumnConfig {
  targetSymbolCount: number;    // 轉輪帶總 cell 數
  visibleSymbolCount: number;   // 可見行數（可變盤面各列不同）
}
```

### SpinMode Preset 組合

| Mode | ReelLayoutConfig | SpinMode | FillStrategy | EntryStrategy | 狀態機路由 |
|------|-----------------|----------|--------------|---------------|-----------|
| Standard | `.standard`(plateCount=3) | Standard | null | null | SPIN→EFFECT_START→SCATTER_SHOW→AWARD |
| Cascade | `.standard`(plateCount=3) | Cascade | CascadeFillStrategy | null | SPIN→EFFECT_START→EXPLODE↔MATCHING_PATCH_UP→AWARD |
| Tumble | `.dropEntry`(plateCount=1) | Tumble | TumbleFillStrategy | DropEntryStrategy | SPIN(掉落)→EFFECT_START→EXPLODE↔MATCHING_PATCH_UP→AWARD |

### GameView.LoadSymbol 初始化範例

```typescript
// Standard
this.m_slotReels?.SetLayoutConfig(REEL_LAYOUT_PRESETS.standard);
this.SlotReels?.CreateSymbol();

// Tumble/DropEntry
this.m_slotReels?.SetLayoutConfig(REEL_LAYOUT_PRESETS.dropEntry);
this.SlotReels?.CreateSymbol();
this.m_slotReels?.SetSpinMode(SpinMode.Tumble, new TumbleFillStrategy());
this.m_slotReels?.SetEntryStrategy(new DropEntryStrategy());
```

### 需同步的硬編碼位置（改 COL/ROW 時）

| # | 檔案 | 位置 | 值 |
|---|------|------|---|
| 1 | Game_Define.ts | `static COL` | 規格列數 |
| 2 | Game_Define.ts | `static ROW` | 初始／MG 行數 |
| 3 | Game_Define.ts | `static FULL_PLATE_NUM` | 各列 row 加總 |
| 4 | Game_Define.ts | `static MAX_ROW` | 所有 BoardLayout 的最大行數；無擴版時 = ROW |
| 5 | SlotReels.ts | `NORMAL_COLUMNS` | 長度=COL 的 index 陣列 |
| 6 | SlotReels.ts | `ReelSystemConfig.columns` | COL 個 ColumnConfig |
| 7 | SlotReels.ts | `m_reelPositionOffset` | COL 個 v3(0,0) |
| 8 | Prefab | `SlotPlate_MG.prefab` Mask contentSize | 公式計算 |

### Mask contentSize 公式

```
width  = COL × SymbolWidth + (COL-1) × SeparateLineWidth
height = ROW × SymbolHeight
```

### SymbolWidth/Height 參考表

| 盤面 | SymbolWidth | SymbolHeight |
|------|-------------|--------------|
| 5×6 | 128 | 100 |
| 5×3 | 123 | 114 |
| 6×4 | 96 | 82 |

### BoardLayout 解析

- 等寬（`3x3x3x3x3`）：standard 每列 target/visible = ROW
- 多模式等寬（MG `3x3x3x3x3`、FG `5x5x5x5x5`）：standard 建立 MAX_ROW 個實體 cell、MG 以 ROW 控制可見數；FG 往上擴張沿用同一盤面，外部 ID 固定以 MAX_ROW 編碼
- 可變（`5x4x4x4x4x5`）：按順序拆分，ROW = max，FULL_PLATE_NUM = sum

---

## Game_Define 結構

```typescript
export class Game_Define {
  static COL = 5;
  static ROW = 3;
  static FULL_PLATE_NUM = 15;
  static MAX_ROW = 3;
  static SYMBOL_COUNT = 11;        // 硬編碼數字
  static SymbolWidth = 123;
  static SymbolHeight = 114;
  static SeparateLineWidth = 4;
  static MIDDLE_PLATE_INDEX = 1;   // dropEntry 改為 0
  static USE_MOCK_SERVER = true;
  static MOCK_MODE: string = 'normal';
  static SCATTER_SYMBOL = Symbol.Scatter;
  static NEARWIN_COLLECT_COUNT = 2;
  static SCATTER_COLUMNS = [0,1,2,3,4];

  enum Symbol { Wild=0, Scatter=1, H1=2, ... }
  enum GAMEVIEW_STATE { WAIT_READY, PLATE_SHOW, ... }
}
```

Audio key 與 FileName 定義在 `AudioManager.AudioClips`，不屬於 `Game_Define`。

---

## Mock Server 資料結構（GenerateMockSpinAck）

```typescript
interface ISpinAck {
  RoundQueue: IRoundInfo[];      // MG=1輪, FG≥2輪
}

interface IRoundInfo {
  MainPlateSymbol: ICColumn[];   // 盤面（COL 個 Column）
  FreePlateSymbol: ICColumn[];   // FG 觸發盤面（空=非 FG）
  PlateQueue: IPlateQueue[];     // Tumble 消除序列
  AwardDataVec: any[];
  FeaturePosQueue: any[];
  MultiplierUpgrade: any[];
  EnergyLevelUpgrade: any[];
  WinLineIndex: any[];
  FreePlateSymbolLog: any[];
  RoundWin: number;
  NextFeverGameType: number;     // 0=無, 1=FG, 2=Respin
}

interface ICColumn { Col: ICSymbol[]; }
interface ICSymbol { Symbol: number; JPState: number; Number: number; }
interface IPlateQueue { EliminatePos: number[]; MainPlateSymbol: ICColumn[]; }
```

### Mock 熱鍵表

| 鍵 | Mode | 觸發條件 |
|----|------|---------|
| 1 | normal | 隨機盤面+隨機消除+隨機贏分 |
| 2 | freegame | RoundQueue≥2 + FreePlateSymbol非空 + NextFeverGameType=1 |
| 3 | bigwin | RoundWin=大額（超過 PlateEftOdds[2]×bet） |
| 4 | nearwin | 盤面固定 2 顆 Scatter |
| 5 | symboleffect | 固定三格中獎，依初始 Layout position 編碼 |
| 6 | collect | Cash + Collect |
| 7 | jackpot（有 JP 時） | Cash + JP + Collect |

---

## Feature Manager（Template 預建）

| Feature | Manager | State | Spine |
|---------|---------|-------|-------|
| FreeGame | FgCounter, FgDeclare, FgCompliment | EnterFreeState, LeaveFreeState, AddFreeState | FG_Declare, FG_Compliment |
| BigWin | BigWinComponent（框架版） | AwardState 內判斷 | BigWin |
| NearWin | NearWinEffectComponent | EffectStartState 內觸發 | NearWin |
| Scatter | EffectPlate.ScatterAnim | ScatterShowState | Scatter |

### FgDeclareManager / FgComplimentManager

**禁止重寫**。Template 已正確實作（completeCb 模式）。codegen 只設定：
- 動畫名（In/Loop/Out）
- Skin 名

### BigWin — Lazy Getter

```typescript
get BigWin(): BigWinComponent | null {
  if (!this.m_bigWinComp && this.m_bigWinNode) {
    this.m_bigWinComp = this.m_bigWinNode.getComponent(BigWinComponent) 
      || this.m_bigWinNode.getComponentInChildren(BigWinComponent);
  }
  return this.m_bigWinComp;
}
```

### NearWin — PrefabPoolManager 動態生成

```typescript
// Init（COL 個 pool）
PrefabPoolManager.RegisterPrefab("NearWin", nearWinPrefab, COL);
// 使用
const node = PrefabPoolManager.GetNode("NearWin");
// 歸還
PrefabPoolManager.ReturnNode("NearWin", node);
```

---

## Tumble 消除資料流

```
GenerateMockSpinAck
  → baseRound.PlateQueue = [{EliminatePos, MainPlateSymbol}, ...]
  → OnRecvSpinAck → ParsePlateQueueToComboData(PlateQueue)
  → SetComboData(explodeList, fillList)
  → EffectStartState → EXPLODE → MATCHING_PATCH_UP → 循環 → AWARD
```

⚠️ ParsePlateQueueToComboData 必須 public，FG 的 SpinState.OnEnter 也要呼叫。

---

## Phase H — Template 預建 Prefab

| 項目 | 位置 | 綁定到 | Codegen 需做 |
|------|------|--------|-------------|
| EffectPlate | Node_Reel 內 | m_effectPlate | 不需要（已綁） |
| Node_BigWin | MainGame.prefab | m_bigWinNode | 不需要（已綁） |
| FG_Declare | MainGame.prefab | m_fgDeclareNode | 不需要（已綁） |
| FG_Compliment | MainGame.prefab | m_fgComplimentNode | 不需要（已綁） |
| SymbolEffectPrefab | Prefab/Reel/ | m_symbolEffectPrefabs[] | ✅ 複製 N 份 |

### gen-spine-placeholder.js 產出

6 組 Spine 資源（binary .skel + .atlas + .png），各含正確動畫名：
- BigWin: In/Loop/Out/Win1/Win2/Win3
- FG_Declare: In/Loop/Out
- FG_Compliment: In/Loop/Out
- NearWin: Loop
- Scatter: Win/Idle/Stop
- SymbolEffect: Win/Stop/Remove

每個 keyframe 須有位移（`x:0.01`）否則 Cocos 不觸發 complete。

---

## 附錄：可變盤面 Per-Column Mask

當 BoardLayout 各列 row 不同時（如 `5x4x4x4x4x5`）：
- 改 SlotPlate_MG.prefab 為 3 區域 Mask（Mask_Left + Mask_Center + Mask_Right）
- `m_reelMask: Node` → `m_reelMasks: Node[]`
- 新增 `REEL_MASK_COLUMNS` mapping + `GetReelMaskNode(col)`
- UpdateReelXPositions：左右列 X=0（各自 Mask 內居中），中間列相對 Mask_Center
- m_reelYOffsetProperty：短列設 `-SymbolHeight/2` 偏移
- ⚠️ CompPrefabInfo.fileId 保留原始值
