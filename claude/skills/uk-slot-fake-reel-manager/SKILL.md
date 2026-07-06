---
name: uk-slot-fake-reel-manager
description: FakeReelManager 假轉輪帶建立、修改、檢查或擴充
---

# UK Slot FakeReelManager

## 概覽

FakeReelManager 是 Cocos Creator 元件，透過 astarte-framework 的 eventManager 提供事件驅動 API，管理老虎機的假轉輪帶資料。

核心功能：載入 Tab 分隔文字檔（Row/Column 模式）、取得符號資料。
可選功能：Seed 循環取值、SymbolInfo 轉換、Coin 金額加權隨機。
設計分叉：**BetMode 分類（fileIndex 由 Server 提供）** 或 **GameType 分類（fileIndex 由本地權重表決定）**。

## 核心與可選模組

| 模組 | 必要性 | 說明 |
|------|--------|------|
| 假轉輪帶載入與解析 | **必要** | Row/Column 模式解析 Tab 分隔 TextAsset |
| 事件系統 | **必要** | 透過 eventManager 註冊/分發事件（事件名稱與數量依專案需求自訂） |
| 分類維度（BetMode/GameType） | **必要** | BetMode：Normal/ToolCard/BuyBonus/ExtraBet；GameType：MainGame/FreeGame 等 |
| Seed 循環取值 | 可選 | 預決定起始位置，從指定位置循環取得符號。不需要時可用簡單隨機取值 |
| fileIndex 來源 | 依方案 | BetMode 方案：Server 直接提供；GameType 方案：本地 Model/File 權重表 |
| SymbolInfo 轉換 | 可選 | 不需要時直接回傳 number[] |
| Coin 金額權重表 | 可選 | 僅 Coin/Cash Symbol 需要隨機金額時使用 |

## 建立新 FakeReelManager

1. 讀取 [references/architecture.md](references/architecture.md) 了解完整架構（含兩種方案說明）
2. 讀取 [references/FakeReelManager.reference.ts](references/FakeReelManager.reference.ts) 作為參考原始碼（BetMode 方案）
3. 向使用者確認：
   - **分類維度**：BetMode（投注模式）還是 GameType（遊戲類型）？
   - **fileIndex 來源**：Server 直接提供（IRoundInfo.FakeReelWeightResult）還是本地權重表？
   - 具體的分類列舉（如 `FakeReelBetMode` 或 `FeverGameType`）— **以專案實際列舉為準**
   - 需要哪些可選模組（Seed？SymbolInfo？Coin 金額？）
   - 事件 API 設計（哪些操作需要透過事件暴露？名稱偏好？）
4. 根據需求裁剪可選功能，建立檔案到 `assets/Script/FakeReelManager.ts`
5. 在場景中建立節點並掛載元件

## 修改現有 FakeReelManager

1. 讀取 [references/customization.md](references/customization.md) 了解可客製化項目
2. 常見操作：
   - **新增/移除 BetMode 或 GameType**：參考 customization.md「分類維度調整」
   - **新增/移除可選功能**：參考 customization.md 各「可選功能」章節

## 檢查現有 FakeReelManager

1. 讀取 [references/architecture.md](references/architecture.md) 了解架構規範
2. 讀取 [references/customization.md](references/customization.md)「審查檢查清單」章節
3. 對照檢查：
   - **分類方案確認**：BetMode 還是 GameType？fileIndex 從 Server 還是本地權重表？
   - **編譯安全**：分類維度列舉引用是否與專案一致、無硬編碼常數
   - **事件一致性**：定義的事件是否全數註冊、與呼叫端匹配
   - **可選功能配置**：BetMode fallback 邏輯是否正確、Column 列數是否動態
   - **資料解析**：讀取模式與檔案格式對應正確
4. 產出檢查報告（按檢查清單逐項）

## 符號取值模式

依專案複雜度選擇其一：

### 模式 A：簡單隨機取值（適合基本需求）
```
GetRandomSymbol(betMode/gameType, reelIndex, position?)
  → 從假轉輪帶資料中取得指定位置（或隨機位置）的符號
  → 返回 number
```

### 模式 B：Seed 循環取值（適合需要可預測/可重現的轉輪結果）

**BetMode 方案（Server fileIndex）**：
```
GenerateFakeReelSeed(betMode, fakeReelWeightResult)
  → effectiveBetMode = 有檔案 ? betMode : Normal（fallback）
  → fileIndex = fakeReelWeightResult（Server 直接給）
  → 隨機各 Reel 的 startPosition
  → 返回 FakeReelSeed（含 betMode）

GetFakeReelDataBySeed(seed, reelIndex, count)
  → betMode 從 seed.betMode 讀取，不需額外傳入
  → 返回 number[]
```

**GameType 方案（本地權重表）**：
```
GenerateFakeReelSeed(gameType, modelIndex?)
  → [有權重表] 按權重選 fileIndex / [無權重表] fileIndex = 0
  → 隨機各 Reel 的 startPosition
  → 返回 FakeReelSeed（不含 gameType）

GetFakeReelDataBySeed(gameType, seed, reelIndex, count)
  → gameType 需額外傳入
  → 返回 number[]
```

## 程式碼規範

遵循專案命名規則：
- 類別：大駝峰（`FakeReelManager`）
- 私有成員：`m_` 前綴（`m_fakeReelData`）
- 常數：全大寫底線（`FAKE_REEL_MANAGER_EVENT`）
- 註解：`/**@ch ... */` 格式
- 區塊：`#region` / `#endregion`
- **避免硬編碼**：Reel/Column 數量應從 Game_Define 取得（如 `Game_Define.COL`）
