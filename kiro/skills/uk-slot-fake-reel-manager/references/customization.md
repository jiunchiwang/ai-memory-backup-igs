# FakeReelManager 客製化指引

## 功能模組一覽

| 模組 | 必要性 | 說明 |
|------|--------|------|
| 假轉輪帶載入與解析 | **必要** | Row/Column 模式解析 Tab 分隔文字檔 |
| 事件系統 | **必要** | 透過 eventManager 註冊/分發事件（名稱與數量可自訂） |
| Seed 循環取值 | 可選 | 預決定起始位置，循環取得符號 ID |
| 分類維度（BetMode/GameType） | 依需求 | 見下方「分類維度調整」 |
| fileIndex 來源 | 依需求 | Server 直接提供 or 本地權重表 |
| SymbolInfo 轉換 | 可選 | 將 number[] 轉為帶附加資訊的物件 |
| Coin 金額權重表 | 可選 | Coin/Cash Symbol 的隨機金額生成 |

## 分類維度調整

### ⚠️ 重要原則

**必須先確認專案採用哪種分類方案**，所有程式碼必須與之完全對應：

- **方案 A（BetMode）**：依投注模式分類（Normal/ToolCard/BuyBonus/ExtraBet），fileIndex 由 Server 提供
- **方案 B（GameType）**：依遊戲類型分類（MainGame/FreeGame/RespinGame），fileIndex 由本地權重表決定

### 方案 A 調整步驟（BetMode）
1. 確認專案的投注模式列舉（或新建 `FakeReelBetMode`）
2. 修改 `m_fakeReelData` 和 `m_isFakeReelLoaded` 初始化 key
3. 為每個 BetMode 新增對應的 `@property`（建議用 `group` 分組）
4. 更新所有 `switch(betMode)` 的 case
5. 確認 `GenerateFakeReelSeed` 接受 `fakeReelWeightResult` 參數

### 方案 B 調整步驟（GameType）
1. 確認專案的遊戲類型列舉（`Game_Define.ts`）
2. 修改 `m_fakeReelData` 和 `m_isFakeReelLoaded` 初始化 key
3. 為每個 GameType 新增對應的 `@property`（含 WeightTableConfig）
4. 在 `OnLoadFakeReelData()` 新增對應載入邏輯
5. 在所有 `switch(gameType)` 新增對應 case

### 範例：新增 ExtraBet（方案 A）
```typescript
// 1. 在 FakeReelBetMode 新增
ExtraBet = 3,

// 2. 新增 @property（建議用 group 分組）
@property({
    type: [TextAsset],
    group: { name: 'ExtraBet' },
    tooltip: "[ExtraBet] 假轉輪帶資料檔案"
})
private m_fakeReelAssets_ExtraBet: TextAsset[] = [];

// 3. 在所有 switch(betMode) 新增 case
case FakeReelBetMode.ExtraBet: return this.m_fakeReelAssets_ExtraBet;
```

### 範例：新增 BonusGame（方案 B）
```typescript
// 在所有 switch(gameType) 新增 case
case FeverGameType.BonusGame:
    asset = this.m_fakeReelAssets_BonusGame[index];
    readMode = this.m_fakeReelReadMode_BonusGame;
    break;
```

## 事件自訂

### 設計原則
- 事件名稱、數量和參數格式可完全自訂
- 使用 `FAKE_REEL_MANAGER_EVENT` 常數物件集中管理
- 每個事件必須同時出現在三處：常數定義、`EVENTS_TO_REGISTER` 陣列、`OnEvent` switch/case
- callback 建議為可選的最後一個參數

### 方案 A 典型事件（BetMode）
```typescript
export const FAKE_REEL_MANAGER_EVENT = {
    LOAD_FAKE_REEL_DATA: "...",
    GENERATE_FAKE_REEL_SEED: "...",         // args: [betMode, fakeReelWeightResult, callback]
    GET_FAKE_REEL_DATA_BY_SEED: "...",      // args: [seed, reelIndex, count, ...]
    GET_FAKE_REEL_SYMBOL_BY_SEED: "...",    // 可選：有 SymbolInfo 時
    PROCESS_SEED_POSITION: "...",           // 可選
    GENERATE_COIN_CREDIT: "...",            // 可選：有 Coin 金額時，args: [betMode?, callback]
};
```

### 方案 B 典型事件（GameType）
```typescript
export const FAKE_REEL_MANAGER_EVENT = {
    LOAD_FAKE_REEL_DATA: "...",
    GENERATE_FAKE_REEL_SEED: "...",         // args: [gameType, modelIndex?, callback]
    GET_FAKE_REEL_DATA_BY_SEED: "...",      // args: [gameType, seed, reelIndex, count, ...]
    GET_FAKE_REEL_SYMBOL_BY_SEED: "...",    // 可選
    PROCESS_SEED_POSITION: "...",           // 可選
    GENERATE_COIN_CREDIT: "...",            // 可選
};
```

### 方案差異：betMode 在 Seed 內 vs 需額外傳入
- 方案 A：`betMode` 存在 `FakeReelSeed` 內，`GetFakeReelDataBySeed(seed, ...)` 不需額外傳 betMode
- 方案 B：`gameType` 不在 Seed 內，`GetFakeReelDataBySeed(gameType, seed, ...)` 需額外傳入

## 可選功能：fileIndex 來源

### 方案 A — Server 直接提供
```typescript
// GenerateFakeReelSeed 直接使用 Server 給的值
seed.fileIndex = fakeReelWeightResult;
```
移除 `ParseWeightTableConfigs` / `ParseWeightTableString` / `ValidateWeightTable` / `SelectFileByModel`。

### 方案 B — 本地權重表
```typescript
// onLoad 中解析權重表
ParseWeightTableConfigs()
// GenerateFakeReelSeed 用權重表選 fileIndex
seed.fileIndex = this.SelectFileByModel(gameType, seed.modelIndex);
```

### ⚠️ 方案 B 無權重表時的行為（重要）
當權重表屬性存在但字串為空時，**不應阻擋資料載入**：
```typescript
// ✅ 無權重表時跳過驗證，直接載入
const hasWeightTable = weightTable && weightTable.length > 0;
if (!hasWeightTable || this.ValidateWeightTable(gameType)) {
    this.LoadFakeReelData(gameType, index);
}

// ❌ 無權重表時 ValidateWeightTable 回傳 false，阻擋載入
if (this.ValidateWeightTable(gameType)) {
    this.LoadFakeReelData(gameType, index);
}
```

## 可選功能：SymbolInfo 轉換

### 不需要時
- 移除 `GetFakeReelSymbolBySeed()` 和 `ConvertSymbolsToSymbolInfos()`
- 移除相關事件
- 取得符號時直接使用 `number[]`

### 需要時
- 確認專案的 `SymbolInfo` 類別結構（欄位可能不同）
- 根據專案的 Symbol 定義調整轉換邏輯

## 可選功能：Coin 金額權重表

### 不需要時
移除：`m_coinCreditWeightAsset_*` 屬性、`m_coinCreditWeightTables` / `m_coinCreditWeightTable_*`、
`CoinCreditWeightTable` / `CoinCreditWeightEntry` 類別、
`ParseCoinCreditWeightTables` / `ParseCoinCreditWeightTable` / `GetCoinCreditWeightTable` / `GenerateCoinCredit`、相關事件。

### 需要時
- 調整 Coin Symbol ID 和 JP Symbol ID（依專案定義，禁止硬編碼）
- 準備 Coin 金額權重表文字檔
- 確認 bet 計算方式（`OnGenerateCoinCredit` 中的計算邏輯依專案的下注管理器調整）

### 方案 A 特有：Coin Credit Fallback
方案 A 的 `GetCoinCreditWeightTable()` 支援 fallback：若 betMode 無對應表，自動使用 Normal 的表。
方案 B 通常不需要 fallback（各 GameType 各自設定）。

## Column 模式列數

`ParseColumnMode()` 中的列數應動態取得：
```typescript
// ✅ 正確：從 Game_Define 取得
const expectedColumns = Game_Define.COL;

// ❌ 錯誤（reference.ts 中有標注 【適配點】）：
const expectedColumns = 6;
```

## 避免硬編碼

| 項目 | 正確來源 | 常見錯誤 |
|------|---------|---------|
| Column 模式列數 | `Game_Define.COL` | `const expectedColumns = 6` |
| Symbol ID | 專案 Symbol 列舉 | `symbolId === 14` |
| JP Symbol ID | 專案定義 | `symbolId === 20` |
| BetMode/GameType 列舉值 | 專案實際列舉 | 假設存在某個未定義的類型 |
| Bet 計算方式 | 專案的 BottomBar 管理器 | 直接寫 `credit * 0.01` |

---

## 審查檢查清單

用於檢查現有 FakeReelManager 時逐項核對：

### 1. 分類維度與 fileIndex 來源
- [ ] 確認採用 BetMode 方案 A 還是 GameType 方案 B
- [ ] 方案 A：確認 `GenerateFakeReelSeed` 接受 `fakeReelWeightResult` 參數
- [ ] 方案 A：確認 BetMode fallback 邏輯（HasFilesForBetMode）
- [ ] 方案 B：確認有無本地權重表；無表時不阻擋載入

### 2. 編譯安全
- [ ] 所有引用的分類維度列舉值在專案中存在
- [ ] 無硬編碼的 Column 數量（應使用 `Game_Define.COL` 或同等常數）
- [ ] import 的型別和模組都存在且路徑正確

### 3. 事件一致性
- [ ] `FAKE_REEL_MANAGER_EVENT` 中定義的每個事件都在 `EVENTS_TO_REGISTER` 中
- [ ] `EVENTS_TO_REGISTER` 中的每個事件在 `OnEvent` switch/case 中都有處理
- [ ] 事件參數簽名與呼叫端（如 SlotReels）使用方式匹配
- [ ] 方案 A：`GetFakeReelDataBySeed` 事件不需傳 betMode（從 seed 讀取）
- [ ] 方案 B：`GetFakeReelDataBySeed` 事件第一個參數是 gameType

### 4. 可選功能配置
- [ ] Coin Credit Fallback 邏輯正確（方案 A 特有）
- [ ] SymbolInfo 轉換邏輯與專案的 `SymbolInfo` 結構匹配
- [ ] Coin 金額的 Symbol ID 與專案定義一致（非硬編碼）
- [ ] `OnGenerateCoinCredit` 中的 bet 計算使用正確的管理器

### 5. 資料解析
- [ ] Row/Column 讀取模式與實際檔案格式對應正確
- [ ] Column 模式的列數使用 `Game_Define.COL`（非硬編碼）
- [ ] 解析後的資料結構與取值邏輯一致

### 6. 邊界處理
- [ ] 資料未載入時有防護
- [ ] 無效的 reelIndex、position 等參數有防護
- [ ] 循環取值的索引計算正確處理負數和超出範圍的情況
- [ ] 方案 A：BetMode fallback 後 fileIndex 對應的資料存在
