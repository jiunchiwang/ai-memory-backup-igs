# FakeReelManager 架構說明

## 概覽

FakeReelManager 是 Cocos Creator 元件（`@ccclass`），負責管理老虎機的假轉輪帶（Fake Reel Strip）資料。
透過 astarte-framework 的 `eventManager` 提供事件驅動 API，供 SlotReels 等元件取用轉輪帶符號。

## 兩種分類方案

FakeReelManager 依**分類維度**管理假轉輪帶資料，有兩種常見設計：

### 方案 A：BetMode（投注模式分類）
依投注模式（如 Normal / ToolCard / BuyBonus / ExtraBet）分類，搭配 **Server 直接提供 fileIndex**：
- `FakeReelSeed.betMode`：記錄投注模式
- `FakeReelSeed.fileIndex`：由 Server 回傳的 `IRoundInfo.FakeReelWeightResult` 直接決定
- 無需本地權重表（Server 負責選檔邏輯）
- Coin 金額支援 fallback（betMode 無表時回退到 Normal）

### 方案 B：GameType（遊戲類型分類）
依遊戲類型（如 MainGame / FreeGame / RespinGame）分類，搭配**本地權重表選擇 fileIndex**：
- `FakeReelSeed.gameType`：記錄遊戲類型
- `FakeReelSeed.modelIndex`：情境/模式編號
- `FakeReelSeed.fileIndex`：由本地權重表（`ParseWeightTableConfigs`）隨機決定
- 需要 `ParseWeightTableString` / `ValidateWeightTable` / `SelectFileByModel`

**重要**：建立或修改時必須先確認專案採用哪種方案，不預設特定設計。

## 事件系統

事件名稱、數量和參數格式皆可依專案需求自訂。以下為通用原則：

### 核心事件（必要）

| 功能 | 用途 | 典型參數 |
|------|------|---------|
| 載入資料 | 載入/重載所有假轉輪帶檔案 | 無 |
| 取得符號 | 取得指定 Reel 的符號資料 | seed/betMode, reelIndex, ... |

### 可選事件

依啟用的可選模組新增，例如：
- Seed 生成、Seed 取值、Seed 位置處理
- Coin 金額生成
- 資料長度查詢、可用性檢查

### 事件設計原則

- 使用 `FAKE_REEL_MANAGER_EVENT` 常數物件集中管理所有事件名稱
- `EVENTS_TO_REGISTER` 陣列必須包含所有定義的事件
- 每個事件的 `OnEvent` switch/case 必須有對應處理
- callback 模式：可選的最後一個參數為回呼函式

## 資料結構

### FakeReelData（核心）
```typescript
class FakeReelData {
    // [Reel 編號] = 符號 ID 陣列（一條完整的轉輪帶）
    ReelData: { [index: number]: number[] } = {};
}
```

### FakeReelSeed — 方案 A（BetMode + Server fileIndex）
```typescript
class FakeReelSeed {
    betMode: number;     // 投注模式（FakeReelBetMode）
    fileIndex: number;   // 由 Server IRoundInfo.FakeReelWeightResult 直接提供
    startPositions: { [reelIndex: number]: number }; // 每條 Reel 的起始位置
}
```

### FakeReelSeed — 方案 B（GameType + 本地權重表）
```typescript
class FakeReelSeed {
    gameType: number;    // 遊戲類型
    modelIndex: number;  // 情境/模式編號（權重表的行）
    fileIndex: number;   // 由本地權重表選出（權重表的列）
    startPositions: { [reelIndex: number]: number };
}
```

### SymbolInfo（可選）
僅在需要將符號 ID 轉換為帶附加資訊的物件時使用。定義來自 `Game_Define.ts`，每個專案可能不同或不需要：
```typescript
class SymbolInfo {
    Symbol: number;  // 符號 ID
    Value: number;   // 符號值（Coin 金額等）
    JpType: number;  // JP 類型
}
```
若專案不需要 SymbolInfo，直接使用 `number[]`（符號 ID 陣列）即可。

### CoinCreditWeightTable / CoinCreditWeightEntry（可選）
僅在專案有 Coin/Cash Symbol 需要隨機金額時使用：
```typescript
class CoinCreditWeightEntry {
    credit: number | 'JP';  // 金額或 'JP' 標記
    weight: number;
}
class CoinCreditWeightTable {
    entries: CoinCreditWeightEntry[];
    totalWeight: number;
}
```

## 資料架構

### 方案 A（BetMode + Server fileIndex）
```
BetMode → File（由 Server FakeReelWeightResult 直接指定）→ Reel[]
```
每個 BetMode 可有多個假轉輪帶檔案，由 Server 決定使用哪一個。

### 方案 B（GameType + 本地權重表）
```
GameType → Model (情境/模式) → File (按本地權重隨機選擇) → Reel[]
```
- **Model**：代表不同情境（如不同 RTP），是權重表的行
- **File**：代表不同假轉輪帶檔案，是權重表的列
- 權重表格式：`"w1,w2;w1,w2"`（分號分隔 Model，逗號分隔 File 權重）

### 方案 A 的 BetMode Fallback（重要）
當特定 BetMode 未設定假轉輪帶檔案時，自動 fallback 到 Normal：
```typescript
// GenerateFakeReelSeed 中
const effectiveBetMode = this.HasFilesForBetMode(betMode) ? betMode : FakeReelBetMode.Normal;
```

## 資料檔案格式

假轉輪帶檔案為 Tab 分隔的純文字檔（TextAsset），支援兩種讀取模式：

### Row 模式（FakeReelReadMode.Row）
每行 = 一條假轉輪帶（Reel），Tab 分隔符號 ID：
```
0	1	2	3	4	5	6	7	8	...
0	3	2	1	4	5	7	6	8	...
```
第 1 行 = Reel 0，第 2 行 = Reel 1。

### Column 模式（FakeReelReadMode.Column）
每列 = 一條假轉輪帶（Reel），行數為轉輪帶長度：
```
0	3	5	2	1	4
1	2	6	3	0	5
2	1	7	4	5	6
```
第 1 列 = Reel 0，第 2 列 = Reel 1。
Column 模式會進行矩陣轉置，空值會被忽略。

**⚠️ Column 模式列數**：應從 `Game_Define.COL` 動態取得，避免硬編碼：
```typescript
// ✅ 動態取得
const expectedColumns = Game_Define.COL;

// ❌ 硬編碼（reference.ts 中有標注此適配點）
const expectedColumns = 6;
```

### Coin 金額權重表檔案（可選）
Tab 分隔，每行一個項目：`金額\t權重` 或 `JP\t權重`
```
5000	300
10000	200
JP	120
```

## Seed 工作流程

### 方案 A
```
GenerateFakeReelSeed(betMode, fakeReelWeightResult)
  → effectiveBetMode = 有檔案 ? betMode : Normal（fallback）
  → fileIndex = fakeReelWeightResult（Server 直接提供）
  → 隨機各 Reel 的 startPosition
  → 返回 FakeReelSeed

GetFakeReelDataBySeed(seed, reelIndex, count)
  → betMode 從 seed.betMode 讀取（無需額外傳入）
  → 從 startPosition 循環取值
  → 返回 number[]
```

### 方案 B
```
GenerateFakeReelSeed(gameType, modelIndex?)
  → [有權重表] 按權重選 fileIndex / [無權重表] fileIndex = 0
  → 隨機各 Reel 的 startPosition
  → 返回 FakeReelSeed

GetFakeReelDataBySeed(gameType, seed, reelIndex, count)
  → 需傳入 gameType（seed 內不含）
  → 從 startPosition 循環取值
  → 返回 number[]
```

## 元件生命週期

### 方案 A
```
onLoad()
  ├─ [可選] ParseCoinCreditWeightTables() ← 解析 Coin 金額權重表
  ├─ OnLoadFakeReelData()                  ← 載入所有 BetMode 的假轉輪帶
  └─ RegisterEvent()

onDestroy()
  └─ UnregisterEvent()
```

### 方案 B
```
onLoad()
  ├─ [可選] ParseWeightTableConfigs()     ← 解析 Model/File 選擇權重表
  ├─ [可選] ParseCoinCreditWeightTables() ← 解析 Coin 金額權重表
  ├─ OnLoadFakeReelData()                  ← 載入所有 GameType 的假轉輪帶
  └─ RegisterEvent()
```

## Inspector 屬性

### 方案 A（BetMode 分組）
使用 `@property group` 在 Inspector 中分組：
```typescript
@property({
    type: [TextAsset],
    group: { name: '一般 (Normal)' },
    tooltip: "假轉輪帶資料檔案"
})
private m_fakeReelAssets: TextAsset[] = [];
```

各 BetMode 各有一組：TextAsset[]、ReadMode、CoinCreditWeightAsset。

### 方案 B（GameType 分組）
各 GameType 各有一組：TextAsset[]、ReadMode、WeightTableConfig（string）、CoinCreditWeightAsset。

## 避免硬編碼

以下值必須從 Game_Define 或配置取得，禁止硬編碼：

| 項目 | 正確來源 | 常見硬編碼錯誤 |
|------|---------|--------------|
| Column 模式列數 | `Game_Define.COL` | `const expectedColumns = 6` |
| Symbol ID | 專案 Symbol 列舉 | `symbolId === 14` |
| 分類維度列舉值 | 專案實際列舉（BetMode/GameType） | 假設存在某個未定義的類型 |
