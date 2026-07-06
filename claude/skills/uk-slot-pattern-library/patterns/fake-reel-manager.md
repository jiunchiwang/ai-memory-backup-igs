# Pattern: FakeReelManager

## 識別條件

- 規格提到「假轉輪」「fake reel」「視覺轉輪帶」「spinning strip」
- 需要在 client 端顯示旋轉中的符號（server 尚未回應前）
- 不同投注模式/遊戲模式需要不同的轉輪帶資料
- 提到 Seed、循環取值、權重表選檔

## 參考實作

| 專案 | 核心檔案 | 說明 |
|------|----------|------|
| eye_strike | FakeReelManager.ts（42.7KB） | BetMode 方案（Normal/ToolCard/BuyBonus/ExtraBet），Server 提供 fileIndex |
| 722 robinhood | FakeReelManager.ts（17KB） | GameType 方案（MainGame/FreeGame），本地權重表（`fake_reel_mg.txt`/`fake_reel_fg.txt`） |
| 746 far_west | FakeReelsManager.ts（**複數**檔名，注意） | 含 FakeReel / FakePlate 類別 |
| 已有 skill | uk-slot-fake-reel-manager | 完整架構、建立/修改/檢查指南 |

## State 映射

FakeReelManager **不需要獨立 State**。它是被動資料提供者，透過 eventManager 事件驅動：

```
任何 State（SpinState / FreeSpinState 等）
  → dispatch FAKE_REEL_MANAGER_EVENT.GENERATE_SEED
  → SlotReels 取得 seed 後呼叫 GetFakeReelDataBySeed() 組盤面
```

整合點：
- `SpinState.OnEnter` → 觸發 GenerateSeed
- `SlotReels` → 消費 seed 取得符號陣列
- `ExtraBet ON/OFF` → 切換 BetMode → 影響下次 seed 用哪組檔案

## Data 需求

```typescript
/** 假轉輪帶投注模式（BetMode 方案） */
enum FakeReelBetMode {
  Normal   = 0,
  ToolCard = 1,
  BuyBonus = 2,
  ExtraBet = 3,
}

/** 假轉輪帶遊戲類型（GameType 方案） */
enum FakeReelGameType {
  MainGame = 0,
  FreeGame = 1,
}

/** Seed：記錄一次 Generate 的結果 */
interface FakeReelSeed {
  /** BetMode 方案才有 */
  betMode?: FakeReelBetMode;
  /** 選中的檔案索引 */
  fileIndex: number;
  /** 各 reel 的起始位置 */
  startPositions: number[];
}

/** Server 提供的 fileIndex（BetMode 方案） */
interface IRoundInfo {
  FakeReelWeightResult: number;  // → 直接當 fileIndex
}

/** 本地權重表項目（GameType 方案） */
interface FakeReelWeightEntry {
  fileIndex: number;
  weight: number;
}

/** Coin 金額權重項目（可選） */
interface CoinCreditEntry {
  value: number;
  weight: number;
}

/** 事件定義 */
const FAKE_REEL_MANAGER_EVENT = {
  LOAD_FAKE_REEL_DATA: "LOAD_FAKE_REEL_DATA",
  GENERATE_SEED: "GENERATE_FAKE_REEL_SEED",
  GET_DATA_BY_SEED: "GET_FAKE_REEL_DATA_BY_SEED",
  // 可選
  GET_SYMBOL_INFO: "GET_FAKE_REEL_SYMBOL_INFO",
  GET_COIN_CREDIT: "GET_FAKE_REEL_COIN_CREDIT",
};
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 載入 TextAsset（Tab 分隔檔） | onLoad / info ack | Cocos 資源系統 |
| 2 | 解析為 number[][] 存入 m_fakeReelData | 同步 | 載入完成 |
| 3 | SpinState 觸發 GENERATE_SEED | event dispatch | BetMode or GameType 已確定 |
| 4 | FakeReelManager 產生 seed（fileIndex + startPositions） | 同步 | BetMode 方案讀 server fileIndex；GameType 方案查本地權重表 |
| 5 | SlotReels 以 seed + reelIndex + count 呼叫取值 | 同步 | seed 已產生 |
| 6 | 從 startPosition 循環取得 count 個符號 | 同步 | — |
| 7 | SlotReels 用取得的符號陣列填充視覺轉輪 | immediate | — |

## 常見變體

| 變體 | 分類維度 | fileIndex 來源 | Seed 模式 | 代表專案 |
|------|----------|---------------|-----------|----------|
| BetMode + Server fileIndex | 投注模式 | IRoundInfo.FakeReelWeightResult | 循環取值 | eye_strike |
| GameType + 本地權重表 | 遊戲類型 | 按 weight 加權隨機 | 循環取值 | 722 robinhood |
| 簡化版（無 Seed） | 遊戲類型 | 固定 fileIndex=0 | 隨機位置 | 小型專案 |
| 含 SymbolInfo 轉換 | 任意 | 任意 | 循環取值 | 需要符號額外資訊時 |
| 含 CoinCredit 金額 | 任意 | 任意 | 循環取值 | Coin/Cash 符號遊戲 |

## 邊界案例

1. **BetMode fallback**：若某 BetMode 未配置檔案（如 ToolCard 無專用 fake reel），需 fallback 回 Normal 的檔案，否則取到空陣列
2. **Column 數量不一致**：某些遊戲不同模式有不同列數（如 Expand Reel），解析時需動態判斷列數而非寫死 `Game_Define.COL`
3. **Seed startPosition 越界**：循環取值時 `(startPosition + offset) % reelLength`，若 reelLength=0 會除以零
4. **ExtraBet 切換時機**：ExtraBet ON/OFF 切換 BetMode 後，下一次 GenerateSeed 才生效；若在旋轉中切換，當輪不受影響
5. **多組 TextAsset 載入順序**：BetMode 方案有 4 組 assets，需確保全部載入完成後才標記 ready，否則取值時可能讀到 null
6. **Row vs Column 解析模式混用**：同專案不同 BetMode 可能用不同排列方式的檔案，解析函式需依模式切換（但實務上極少見，通常統一）

## 常見錯誤

1. **❌ BetMode 切換沒切 FakeReel**：ExtraBet/BuyBonus ON 後 GenerateSeed 仍用 Normal 帶 → 旋轉中的假符號分布與實際結果差太多，玩家感知「假」
2. **❌ 載入未完成就取值**：onLoad 是 async，若 SpinState 在 assets 載入前就 GENERATE_SEED → 讀到 null → crash 或空盤面
3. **❌ 循環取值沒 mod**：`startPosition + offset` 直接當 index → 超出 array 長度 = undefined → 符號顯示為 0 號（通常是空白）
4. **❌ 擴展盤面時仍用舊 ROW 數取值**：盤面從 3 行擴到 5 行後，GetFakeReelDataBySeed 的 count 參數沒更新 → 少取 2 行符號 → 擴展區空白
5. **❌ Server fileIndex vs 本地權重表方案搞混**：eye_strike 用 server 給 fileIndex（BetMode 方案），722 用本地 weight 隨機（GameType 方案）；照搬錯方案 = fileIndex 永遠是 0
