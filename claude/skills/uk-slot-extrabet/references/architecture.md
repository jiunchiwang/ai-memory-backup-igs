# ExtraBet 架構與整合

## 目錄
- [三方資料流](#三方資料流)（變體 A 單倍率 / 變體 B 多倍率）
- [倍率表 info.Mul](#倍率表-infomul)
- [framework ExtraBetComponent API](#framework-extrabetcomponent-api)
- [ExtraBetWindow 跳窗](#extrabetwindow-跳窗)（變體 B 才用）
- [GameView 整合](#gameview-整合)（變體 A / B 範例）
- [顯隱與互斥規則](#顯隱與互斥規則)

## 三方資料流

### 變體 A：單倍率單步驟（isTwoStep=false，本專案 uk_slot_eye_strike）

```
玩家點 EX 按鈕
  └─> ExtraBetComponent.ChangeBetMode()                 [framework: UI/動畫/狀態]
        ├─> newBottombarManager.ChangeMultiBet(Special) [立即切倍率]
        └─> triggerCb(isActive=true, isForce=false)     [GameView 注入]
              ├─> ClearAllForExtraBet()
              ├─> PlayExtraBetActiveAnimation()
              │     └─> eventManager.Dispatch(PLAY_ACTIVATE_EFFECT, resolve)
              │           └─> ExtraBetEffectManager.PlayActivateEffect()
              │                 ├─> AudioManager.Play(ExbetActive)
              │                 ├─> activateEffectSpine.PlayAnimation('In')
              │                 └─> DelayChangeSlotReelsPlateInfo(1)
              │                       └─> SlotReels.SetExtraBetInitPlateInfo()
              └─> [動畫完成 callback resolve]
```

關閉時對稱：`triggerCb(false, false)` → `ClearAllForExtraBet()` → `SlotReels.SetInitPlateInfo()`。

### 變體 B：多倍率兩步驟（isTwoStep=true）

```
玩家點 EX 按鈕
  └─> ExtraBetComponent.ChangeBetMode()        [framework: UI/動畫/狀態]
        └─> triggerCb(isActive, isForce)        [GameView 注入的 callback]
              └─> ExtraBetWindow.ShowAndWait()  [專案: 跳窗選卡]
                    └─> { confirmed, type }
              └─> ExtraBetComponent.SetTwoStepMulti(confirmed, type)
                    └─> newBottombarManager.ChangeMultiBet(type)  [實際切換押注倍率]
```

- **framework** 不知道有幾種倍率，只負責 UI/動畫與呼叫 `ChangeMultiBet(idx)`
- **專案** 透過 `triggerCb` 注入跳窗邏輯與倍率表，決定 `type`
- 倍率的真正套用在 `newBottombarManager.ChangeMultiBet(type)`（framework Manager）

### 變體 A vs B 的關鍵差異

| 項目 | 變體 A | 變體 B |
|------|--------|--------|
| `ChangeMultiBet` 觸發點 | `ChangeBetMode` 內**立即**呼叫 | `SetTwoStepMulti` 確認後才呼叫 |
| `triggerCb` 內等待 | 等 spine 動畫播完 | 等跳窗操作 + 動畫 |
| 玩家可選 type | 無（永遠 Special=1） | 多種（依 Mul 長度） |
| 取消路徑 | 無（直接 ON/OFF） | 跳窗取消 → 復原 m_isExtra |

## 倍率表 info.Mul

伺服器 GameInfo 提供 `info.Mul: number[]`：

| 索引 | 意義 | 用途 |
|------|------|------|
| `Mul[0]` | 基礎倍率（一般幾乎為 1） | `ChangeMultiBet(TYPE.Normal=0)` 還原一般押注 |
| `Mul[1]` | 第一種 ExtraBet（TYPE.Special） | 跳窗第 1 張卡 / 預設強制種類 |
| `Mul[2]`, `Mul[3]`... | 其他 ExtraBet 倍率 | 跳窗第 2、3 張卡 |

GameView 收到 GameInfo 後（`GameView.ts` 的 GameInfo 解碼處）：
```typescript
newBottombarManager.SetMultiBetInfo({
    IsMulti: () => this.m_extraBetComp?.IsExtra ?? false,
    Multi: info.Mul
});
this.m_betMultipliers = info.Mul.slice();          // 保存完整表供 unshow 反推 type
const extraBetMultiplierRates = info.Mul.slice(1); // 跳窗只需 ExtraBet 倍率（去掉基礎）
this.m_extraBetWindow?.Init( extraBetMultiplierRates );
```

**對應關係**：跳窗卡片 `i`（0-based）顯示 `Mul[i+1]` → 玩家選中回傳 `type = i+1` → `ChangeMultiBet(type)` 套用 `Mul[type]`。三者索引一致，勿錯位。

## framework ExtraBetComponent API

| 方法 | 用途 |
|------|------|
| `Init(triggerCb, description, extraBetTxt, isTwoStep=false, isSpecial=false)` | 初始化。第 2、3 參數是 **i18n string key**（如 `Game_Define.StringKey.EXTRA_BET_DESC`），不是布林。`triggerCb: (isActive, isForce) => Promise<void>` 是遊戲多表演的注入點。內部會 `extraBetController.Init((isSpecial)?null:this.node, this.ForceSetExtraBet.bind(this))` 註冊全域 controller |
| `ForceSetExtraBet(isActive, type=TYPE.Special)` | 強制設值（跳過跳窗），unshow/replay 用。**注意 type 預設值** |
| `SetTwoStepMulti(isActive, type)` | 兩步驟確認後正式切倍率；取消則復原 |
| `ShowExtra(show)` | 顯隱整顆 EX 節點 |
| `OnSpin()` / `OnRotation()` | spin/轉動時收 Bar、播對應動畫 |
| `FirstShowBar()` | 進遊戲首次自動展開 Bar + 說明（已用過 force 則不彈） |
| `IsExtra`（getter） | 目前是否開啟 ExtraBet |
| `CheckCanUseBtn()` | 按鈕可用條件（見下方互斥規則） |

**callback 兩個參數的意義**：
- `isActive`：要開啟還是關閉
- `isForce`：是否為強制路徑。`true` 時 GameView callback 應**跳過跳窗**（unshow/replay 不需玩家再選）

**isTwoStep 行為差異**：
- `isTwoStep=true`：`ChangeBetMode` 先不切倍率，等跳窗 `SetTwoStepMulti` 確認才切（多倍率機台採用）
- `isTwoStep=false`：`ChangeBetMode` 直接 `ChangeMultiBet(TYPE.Special)`，無跳窗（本專案 `uk_slot_eye_strike` 採用，預設值）

## ExtraBetWindow 跳窗

專案自訂 UI（`assets/Script/ExtraBet/ExtraBetWindow.ts`），非 framework。

- `Init(multiplierRates: number[])`：傳入 `Mul.slice(1)`，存為 `m_multiplierRates`
- `ShowAndWait(): Promise<{ confirmed, type }>`：顯示跳窗，等玩家操作後 resolve
  - `type = selectedIndex + 1`；`0` 表示未選/取消
- `SetPrice()`：卡片金額 = `tools.times(bet, m_multiplierRates[i])`
- 確認時 `newBottombarManager.SetNowBet(...)` 同步 bet，再 resolve

## GameView 整合

### 變體 A 範例（本專案 uk_slot_eye_strike，isTwoStep=false）

```typescript
private InitExtraBet() {
    this.m_extraBetComp?.Init(
        async (_isActive: boolean, _isForce: boolean) => {
            let isPlayActiveAnimation = false;
            this.ClearAllForExtraBet();
            if (_isActive && !_isForce) {
                // 一般開啟：播激活動畫（內部會 DelayChangeSlotReelsPlateInfo）
                await this.PlayExtraBetActiveAnimation();
                isPlayActiveAnimation = true;
            }
            if (_isActive) {
                if (!isPlayActiveAnimation) {
                    // isForce 路徑（unshow 還原）沒播動畫 → 手動切假轉輪盤
                    this.m_slotReels.SetExtraBetInitPlateInfo();
                }
            } else {
                this.m_slotReels.SetInitPlateInfo();
            }
        },
        Game_Define.StringKey.EXTRA_BET_DESC,
        Game_Define.StringKey.MG_SPECIAL_TXT
        // isTwoStep / isSpecial 未傳 → 預設 false
    );
    this.m_extraBetComp?.ShowExtra(false);  // 啟動先隱藏，等 info ack 才 ShowExtraBet()
}

public async RestoreExtraBetState() {
    // 單倍率：不帶 type，預設 TYPE.Special=1 剛好對
    await this.m_extraBetComp?.ForceSetExtraBet( true );
}
```

### 變體 B 範例（多倍率機台，isTwoStep=true）

```typescript
this.m_extraBetComp?.Init(
    async (_isActive, _isForce) => {
        this.ClearAllForExtraBet();
        if (_isActive && !_isForce) {           // 一般開啟 → 跳窗
            await this.PlayExtraBetActiveAnimation();
            const result = await this.m_extraBetWindow?.ShowAndWait();
            await this.m_extraBetComp?.SetTwoStepMulti(result?.confirmed ?? false, result?.type ?? 0);
        } else if (!_isActive) {
            // 關閉時的清理
        }
        // _isForce=true（unshow/replay）：不跳窗，倍率已由 ForceSetExtraBet 內的 ChangeMultiBet 處理
    },
    Game_Define.StringKey.EXTRA_BET_DESC,
    Game_Define.StringKey.MG_SPECIAL_TXT,
    true  // isTwoStep
);
```

## 顯隱與互斥規則

- **僅主遊戲顯示**：進免費遊戲須 `SetExtraBetVisible(false)`。注意 unshow 還原進 FreeGame 的路徑可能繞過 `EnterFreeState`，須在 `RestoreUI` 之後手動隱藏，且須在 inactive 之前完成 `RestoreExtraBetState` 動畫 await（否則 await 不 resolve）
- **info ack 才顯示**：伺服器資料就緒後才 `ShowExtraBet()`，避免倍率表未到就讓玩家操作
- **BuyBonus 互斥**：啟用 BuyBonus 時關閉 ExtraBet 並取消啟用；`CheckCanUseBtn()` 已排除 `buyBonusManager.IsBuyBonus`
- **可用條件全集**：`Define.IsInMG() && CommonState.IDLE && !Define.IsUsingItem && !buyBonusManager.IsBuyBonus && !newExtraManager.IsFeaturesDemoMode && !CheckSwitchOff(CloseExtraBet)`
