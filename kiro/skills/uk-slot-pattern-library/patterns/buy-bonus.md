# Pattern: Buy Bonus

## 識別條件

- 規格提到「購買 Bonus」「Buy Feature」「Buy Free Spins」「付費直接進入 FG」
- 玩家可花費固定倍數的 bet 直接跳過 BaseGame 進入 FreeGame/特殊遊戲
- 有 2~3 種選擇品項（不同價位對應不同 FG 配置）
- UI 上有獨立的 Buy 按鈕，點擊後彈出選擇面板

## 參考實作

| 專案 | 核心檔案 | 說明 |
|------|----------|------|
| 框架 | CommonBuyBonus component | 基礎 UI 面板、按鈕可見性控制 |
| tct | BuyBonus/BuyBonus.ts + BuyBonusCell.ts | 完整實作含品項 Cell 渲染 |
| 722 robinhood | Game_Define.FeatureBetValue=10 | 固定倍率方案（單品項） |
| 3LP | BuyBonusPanel + 3 品項 | 漸進式（隨機 1/2+/3 特色） |
| 框架 | newExtraManager | SetBuyBonusState / CheckBuyBonusOverAni |

## State 映射

Buy Bonus **不需要獨立 State**。它走現有的 FreeGame 進入流程：

```
IDLE（玩家點 Buy 按鈕 → 選擇品項 → 確認付費）
  → WaitResState：發送 spin request（帶 BuyBonus 參數 + FeatureBetValue）
  → SpinState → EnterFreeState → FreeGame 流程
```

與其他 State 互動：
- `IdleState`：`newExtraManager.SetBuyBonusState(true)` 標記 BuyBonus 進行中
- `WaitResState`：使用 `FeatureBetValue` 替換正常 bet，帶入選定品項參數
- `EnterFreeState`：`BuyBonus?.SetBuyBtnVisible(false)` 隱藏按鈕
- `LeaveFreeState`：`BuyBonus?.SetBuyBtnVisible(true)` 恢復按鈕
- `RoundEndState`：`newExtraManager.CheckBuyBonusOverAni()` 播結束動畫

## Data 需求

```typescript
/** Buy Bonus 品項定義 */
interface BuyBonusItem {
  /** 品項類型 ID */
  buyBonusType: number;
  /** 費用倍數（相對於 base bet） */
  costMultiplier: number;
  /** 觸發的 FG 配置 */
  freeGameConfig: {
    /** scatter 數量（決定 FG 初始次數） */
    scatterCount: number;
    /** 特殊條件描述（如特色符號組合） */
    specialCondition?: string;
  };
  /** 顯示用描述 i18n key */
  descKey: string;
}

/** Buy Bonus 請求（送 server） */
interface BuyBonusRequest {
  /** 選定的品項 type */
  buyBonusType: number;
  /** 實際扣款金額 = bet × costMultiplier */
  cost: number;
}

/** Game_Define 常數 */
const FeatureBetValue: number = 10;  // 722: 固定倍率

/** FakeReelManager BetMode 切換 */
enum FakeReelBetMode {
  Normal   = 0,
  BuyBonus = 2,  // BuyBonus 期間假轉輪切換到此 mode
}

/** Buy Bonus 面板回傳 */
interface BuyBonusPanelResult {
  confirmed: boolean;
  selectedItem?: BuyBonusItem;
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 玩家點 Buy 按鈕 | user interaction | IDLE + MG + 非 ExtraBet |
| 2 | 彈出品項選擇面板（2~3 Cell） | 等待玩家操作 | BuyBonusItem[] |
| 3 | 玩家選擇品項 + 確認付費 | user confirm | 餘額 ≥ cost |
| 4 | SetBuyBonusState(true) 標記狀態 | 同步 | newExtraManager |
| 5 | 發送 spin request（FeatureBetValue + buyBonusType） | server response | WaitResState |
| 6 | 收到 ack → 正常 SpinState 流程 | spin ack | — |
| 7 | EnterFreeState（隱藏 Buy 按鈕） | state transition | 與普通 FG 相同 |
| 8 | FreeGame 流程完整執行 | FG 結束 | — |
| 9 | LeaveFreeState（恢復 Buy 按鈕 + CheckBuyBonusOverAni） | animation | — |

## 常見變體

| 變體 | 品項數 | 定價方式 | 選擇 UI | 代表專案 |
|------|--------|----------|---------|----------|
| 固定單品項 | 1 | FeatureBetValue 固定倍率 | 直接確認（無選擇） | 722 robinhood |
| 多品項面板 | 2~3 | 各品項不同 costMultiplier | Cell 列表 + 確認 | tct |
| 漸進式 | 3 | 隨機1特色 / 隨機2+特色 / 全特色 | 卡片選擇（標注特色圖示） | 3LP |
| 附帶動畫 | 任意 | 任意 | 面板 + 過場動畫 | — |

## 邊界案例

1. **與 ExtraBet 互斥**：Buy Bonus 啟用時必須關閉 ExtraBet（`CheckCanUseBtn` 已排除）；ExtraBet 開啟時 Buy 按鈕應 disable 或隱藏
2. **餘額不足**：選擇品項後確認前需即時檢查餘額 ≥ cost；若不足需提示且不發送 request
3. **BuyBonus 期間 FakeReelManager BetMode**：進入 BuyBonus 流程後 FakeReelManager 需切到 `BetMode.BuyBonus`，FG 結束後切回 Normal
4. **Unshow/Replay 還原**：BuyBonus 觸發的 FG 與普通觸發的 FG 走相同 state，但 unshow 時需正確還原 `IsBuyBonus` 標記以決定結束時是否播 BuyBonusOverAni
5. **SetBuyBtnVisible 可選鏈**：框架用 `this.m_gameView.BuyBonus?.SetBuyBtnVisible()` 可選鏈存取，未啟用 BuyBonus 的專案不會報錯但也不可遺漏掛載
6. **FeatureBetValue 與 bet 表的關係**：`FindBetIndexByValue(FeatureBetValue)` 需確保 bet 表中存在該值，否則會 -1 導致 request 異常
7. **品項與 FG 特色對應**：Buy 品項 3（全特色）的 FG 配置與自然觸發全 Scatter 的 FG 必須一致（server 不區分來源）
8. **AutoPlay 期間不顯示品項機率**：Buy Bonus 面板不可在 AutoPlay 啟動時彈出（UI 衝突）
9. **監管合規**：部分市場（如 UK LCCP）要求 Buy Bonus 面板顯示 RTP 資訊或機率揭露，確認規格有無此要求

## 常見錯誤

1. **❌ BuyBonus 後 FakeReel 沒切 BetMode**：進入 BuyBonus FG 時 FakeReelManager 仍用 Normal mode → 假轉輪帶的機率/符號分布不對（應切到 BuyBonus mode 的帶）
2. **❌ ExtraBet 與 BuyBonus 同時啟用**：兩者同時開會導致 bet 計算衝突（FeatureBetValue vs ExtraBet multiplier）→ 必須互斥
3. **❌ LeaveFreeState 忘記恢復 Buy 按鈕**：FG 結束後 Buy 按鈕永久消失 → 玩家無法再次購買
4. **❌ FeatureBetValue 不在 bet 表中**：`FindBetIndexByValue` 回傳 -1 → 發送非法 bet 值給 server → server reject → 卡住
5. **❌ BuyBonus 期間改 bet**：Buy 面板打開後玩家若能切換 bet → cost 計算基數改變但 UI 顯示舊值 → 扣款金額與預期不符。正確做法：面板開啟期間鎖定 bet selector
