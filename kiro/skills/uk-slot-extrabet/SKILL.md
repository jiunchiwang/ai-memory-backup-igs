---
name: uk-slot-extrabet
description: UK 老虎機 ExtraBet（額外押注/加倍投注）子系統指南。建立、修改、除錯 ExtraBet 功能，或處理 unshow/replay 還原、單倍率單步驟 / 多倍率兩步驟跳窗變體、多倍率 type 時觸發。涵蓋 framework ExtraBetComponent / extraBetController、專案 ExtraBetWindow 跳窗、ExtraBetEffectManager 動畫、SlotReels 假轉輪整合、GameView 整合多方關係。
---

# UK Slot ExtraBet

## 概覽

ExtraBet 讓玩家用更高押注換取更好的中獎機會（更高倍率/更多特色觸發機率）。實作有兩種變體，依遊戲倍率數量決定：

| 變體 | 倍率數 | 是否跳窗 | `isTwoStep` | 範例專案 |
|------|--------|---------|-------------|---------|
| **A. 單倍率單步驟** | 只有 `Mul[1]` 一種 | 無跳窗，點按鈕直接 ON/OFF | `false`（預設） | `uk_slot_eye_strike` |
| **B. 多倍率兩步驟** | `Mul[1..n]` 多種 | 有跳窗讓玩家選卡 | `true` | 多倍率機台 |

兩種變體共用 framework 的 `ExtraBetComponent`，差異在 callback 內是否引入 `ExtraBetWindow`。

### 多方協作角色

| 角色 | 檔案 | 適用變體 | 職責 |
|------|------|---------|------|
| **ExtraBetComponent** | `extensions/astarte-framework/assets/Component/ExtraBetComponent.ts`（framework） | A + B | EX 按鈕/Bar 的 UI、動畫、開關狀態 `m_isExtra`、呼叫 `newBottombarManager.ChangeMultiBet()` 切換押注倍率 |
| **extraBetController** | `extensions/astarte-framework/assets/utilis/ExtraBetController.ts`（framework） | A + B | 全域 controller，`ExtraBetComponent.Init` 內部會 `extraBetController.Init(node, ForceSetExtraBet.bind(this))` 註冊。外部模組（如 unshow flow）取此 controller 觸發強制設值 |
| **ExtraBetEffectManager** | `assets/Script/ExtraBet/ExtraBetEffectManager.ts`（專案） | A（單步驟） | 透過事件 `EXTRA_BET_EFFECT_MANAGER_EVENT.PLAY_ACTIVATE_EFFECT` 播激活 spine 動畫 + `AudioManager.AudioClips.ExbetActive` 音效 + `DelayChangeSlotReelsPlateInfo()` 切換 fake reel 盤面 |
| **ExtraBetWindow** | `assets/Script/ExtraBet/ExtraBetWindow.ts`（專案） | B（兩步驟） | 跳窗：顯示多張倍率卡片供選擇，回傳 `{ confirmed, type }` |
| **SlotReels** | `assets/Script/SlotReels.ts`（專案） | A + B | `SetExtraBetInitPlateInfo()` 切到 ExtraBet 版預設盤；`SetInitPlateInfo()` 切回一般盤。fake reel skill 與 extrabet skill 的交界 |
| **GameView** | `assets/Script/GameView.ts`（專案） | A + B | 整合層：`InitExtraBet()` 綁 callback、`ShowExtraBet()` 顯隱、保存倍率表、unshow 還原 `RestoreExtraBetState()`、`ExtraBetFirstShowBar()` 首次展開 |

**倍率表（`info.Mul`）是核心資料**：`Mul[0]`=基礎倍率，`Mul[1..]`=各種 ExtraBet 倍率。`type` 就是 `Mul` 的索引。變體 B 選卡片 index `i` → `type = i+1` → `ChangeMultiBet(type)` 套用 `Mul[type]`；變體 A 永遠 `type=1`（`TYPE.Special`）。

## TYPE 常數（framework 定義）

```typescript
const TYPE = { Normal: 0, Special: 1 };  // Normal=關閉 ExtraBet, Special=第一種 ExtraBet
```
多倍率遊戲的 type 可為 1、2、3...（對應 `Mul[1]`、`Mul[2]`、`Mul[3]`）。

## 變體 A：單倍率單步驟流程（isTwoStep=false，本專案）

1. 玩家點 EX 按鈕 → `ChangeBetMode()`：`m_isExtra=true`，因 `isTwoStep=false` **立即** `ChangeMultiBet(TYPE.Special=1)`
2. 呼叫 `triggerCb(isActive=true, isForce=false)` → GameView 的 callback：
   - `ClearAllForExtraBet()` → 透過 event 觸發 `ExtraBetEffectManager` 播激活 spine 動畫
   - 動畫播完後（或內部延遲）→ `m_slotReels.SetExtraBetInitPlateInfo()` 切假轉輪預設盤
3. 關閉時 `triggerCb(false, false)`：`m_slotReels.SetInitPlateInfo()` 切回一般盤

**GameView `InitExtraBet` 簽名**（本專案）：

```typescript
this.m_extraBetComp?.Init(
    async (_isActive, _isForce) => {
        this.ClearAllForExtraBet();
        if (_isActive && !_isForce) {
            await this.PlayExtraBetActiveAnimation();  // event 派發給 ExtraBetEffectManager
        }
        if (_isActive) {
            // PlayExtraBetActiveAnimation 內部已 DelayChangeSlotReelsPlateInfo
            // isForce 路徑沒播動畫，這裡手動補一次
            this.m_slotReels.SetExtraBetInitPlateInfo();
        } else {
            this.m_slotReels.SetInitPlateInfo();
        }
    },
    Game_Define.StringKey.EXTRA_BET_DESC,   // 第 2 參數：描述文字 i18n key（不是布林）
    Game_Define.StringKey.MG_SPECIAL_TXT    // 第 3 參數：ExtraBet 標題 i18n key（不是布林）
    // isTwoStep / isSpecial 未傳，使用預設 false
);
```

## 變體 B：多倍率兩步驟跳窗流程（isTwoStep=true）

1. 玩家點 EX 按鈕 → `ChangeBetMode()`：`m_isExtra=true`，因 `isTwoStep` 只設 `m_toStepTwo=true`（**先不** `ChangeMultiBet`）
2. 呼叫 `triggerCb(isActive=true, isForce=false)` → GameView 的 callback：
   - `ClearAllForExtraBet()` → 播放啟用動畫 → `m_extraBetWindow.ShowAndWait()`（等玩家操作）
   - 玩家選卡確認 → `SetTwoStepMulti(confirmed, type)`
3. `SetTwoStepMulti`：確認 → `ChangeMultiBet(type)` 正式切倍率；取消 → `m_isExtra=false` + 播 OFF 動畫

**關鍵**：`Promise.all` 在 `triggerCb` 內等待，使 `m_ExtraBetAniPlaying=true` 直到玩家操作完，避免動畫錯亂。

## 強制設值流程（ForceSetExtraBet）

unshow / replay 還原時用，**跳過跳窗**：

```typescript
async ForceSetExtraBet( isActive: boolean, type: number = TYPE.Special )
```

- `isActive=true`：`m_isExtra=true` → `ChangeMultiBet(type)` → `triggerCb(true, isForce=true)`（callback 因 `isForce` 跳過跳窗分支）→ 播動畫
- **⚠️ 陷阱（變體 B 才需處理）**：`type` 預設 `TYPE.Special=1`。多倍率遊戲若不帶 type，會永遠還原成第一種。詳見 [references/unshow-restore.md](references/unshow-restore.md)
- **變體 A 不踩此陷阱**：本專案 `RestoreExtraBetState()` 只呼叫 `ForceSetExtraBet(true)` 不帶 type，因為只有一種倍率，預設值剛好正確

## fake reel 整合（SlotReels）

ExtraBet 開關直接影響假轉輪預設盤面：

| 狀態 | 呼叫 | 用途 |
|------|------|------|
| ExtraBet **開** | `SlotReels.SetExtraBetInitPlateInfo()` | 用 ExtraBet 版預設盤（通常含更多 special symbol） |
| ExtraBet **關** | `SlotReels.SetInitPlateInfo()` | 用一般版預設盤 |

切換時機：
- 變體 A：`PlayExtraBetActiveAnimation()` 內部 `DelayChangeSlotReelsPlateInfo(1)` 在動畫播完前 1 秒切（trick：與動畫高潮對齊）；`isForce` 路徑沒播動畫，GameView callback 直接補一次切換
- 變體 B：跳窗確認後切（依專案）

跨 skill 銜接見 `uk-slot-fake-reel-manager`。

## ExtraBet 連動持久視覺的兩個陷阱（盤面 / 乘倍底板等）

ExtraBet 開關常需連動「持續留在畫面上的視覺」——`SlotReels` 預設盤、乘倍底板 index 等。除了在 callback 一般路徑切換，還有兩個非顯而易見、現有範例都沒示範的整合點，做這類功能前**先主動查這兩題**：

1. **強制還原路徑 callback 拿不到 type**：`ForceSetExtraBet(isActive, type)` 內部呼叫的是 `triggerCb(isActive, isForce=true)`——**type 沒傳進 callback**。所以「依 type 切視覺」在 unshow/replay 還原時無法只靠 callback。作法：在呼叫端（`RestoreExtraBetState`，type 由 `GetUnshowExtraBetType()` 已知）於 `ForceSetExtraBet` 之後直接補套用視覺，或 GameView 存成員 type 供 callback `_isForce` 分支讀。

2. **其他 GameState 的 per-spin reset 會反覆抹掉**：持久視覺常被某狀態每轉清空（例：`SpinState.OnEnter` 主遊戲分支 `SET_MULTIPLIER -1,0 + SET_SHOW -1,false` 把乘倍底板歸零隱藏）。ExtraBet 開啟時這會讓玩家每轉看到視覺被清掉。該 reset 必須 ExtraBet-aware：GameView 存目前 type，reset 處先判斷 ExtraBet 是否開啟 → 開啟則重套用 ExtraBet 對應狀態，而非清成預設。

> 通則：「ExtraBet 連動持久視覺」前先問——(a) 強制還原路徑誰負責切這視覺？(b) 有沒有別的狀態每轉 reset 它？兩題都是 grep「該視覺的切換/reset 呼叫點」就能查到，但容易整段漏看。

## 常見操作

### 建立新遊戲的 ExtraBet
讀取 [references/architecture.md](references/architecture.md) 了解三方整合與 `InitExtraBet()` 設定（`isTwoStep` / `isSpecial` 參數、callback 結構、倍率表保存點）。

### 修改 / 除錯
- **unshow/replay 還原成錯誤的倍率種類**（變體 B）→ [references/unshow-restore.md](references/unshow-restore.md)（type 反推機制）
- **激活動畫沒播 / 音效沒響**（變體 A）→ 檢查 `ExtraBetEffectManager` 是否註冊事件、`m_activateEffectSpine` 是否綁定。GameView 透過 `eventManager.Dispatch(EXTRA_BET_EFFECT_MANAGER_EVENT.PLAY_ACTIVATE_EFFECT, resolve)` 觸發
- **跳窗卡片金額顯示**（變體 B）→ ExtraBetWindow `SetPrice()`：`卡片值 = Bet × Mul[i+1]`
- **按鈕可用條件** → `CheckCanUseBtn()`：`IsInMG && IDLE && !IsUsingItem && !IsBuyBonus && !FeaturesDemoMode && !CloseExtraBet`
- **顯隱規則** → ExtraBet **僅主遊戲顯示**，進免費遊戲須 `SetExtraBetVisible(false)`；info ack 就緒後才 `ShowExtraBet()`
- **首次進 IDLE 自動展開 Bar** → `ExtraBetFirstShowBar() → m_extraBetComp.FirstShowBar()`，已用過 force 還原則不彈
- **與 BuyBonus 互斥** → 啟用 BuyBonus 時關閉 ExtraBet（`CheckCanUseBtn` 已排除 `IsBuyBonus`）
- **`extraBetController` 全域取用** → `ExtraBetComponent.Init` 內部自動 `extraBetController.Init(node, ForceSetExtraBet.bind(this))`。外部模組（如 unshow flow）可直接從 `db://astarte-framework/utilis` import `extraBetController` 觸發強制設值，不需透過 GameView

### 依 server `IGameInfoData.ShowExtra` 開關整個功能

本次連線是否提供 ExtraBet 由 server 欄位 `IGameInfoData.ShowExtra`（proto optional `boolean|null`）決定，與 license 級 `CloseExtraBet` switch **正交**（任一關閉即不提供）。

⚠️ **三個 `ShowExtra` 別搞混**：
- `IGameInfoData.ShowExtra`：**server 資料欄位**（per-session 遊戲資訊）
- `ExtraBetComponent.ShowExtra(bool)`：**框架 UI 方法**（顯/隱 EX 節點）
- `SwitchOffKeyDefine.CloseExtraBet = 61`：**license bitmask switch**（`LicenseSetting.ts`，每個框架方法都 `CheckSwitchOff` 它）

作法：GameView 存成員 `m_showExtra = info.ShowExtra ?? false`（info ack 時賦值），**gate 集中在 GameView 各入口方法內部**，呼叫端（IdleState / UnshowPrepareState）不動：
- `ShowExtraBet()` / `RestoreExtraBetState()` / `ExtraBetFirstShowBar()` → 開頭 `if ( !this.m_showExtra ) return;`
- `SetMultiBetInfo` 的 `IsMulti` callback → `() => this.m_showExtra && ( this.m_extraBetComp?.IsExtra ?? false )`（callback 為 lazy 求值，無賦值排序問題）

關鍵判斷：
- gating `IsMulti` 是**防禦冗餘**——`ShowExtra=false` 時 `IsExtra` 不可能為 true（按鈕隱藏點不到 + `ForceSetExtraBet` 已 gate + 專案無 `extraBetController` 外部呼叫）。寫上去是防未來新增繞過路徑
- **勿整段跳過 `SetMultiBetInfo`**——`Mul[0]` 基礎倍率一般 bet 也需要，跳過會弄壞基礎 bet 顯示
- 時序：`RestoreExtraBetState` 在 `CloseIntroLoading → UNSHOW_PREPARE` 才跑，晚於 info ack，`m_showExtra` 已設好

## 程式碼規範

遵循專案慣例（與 fake-reel-manager / state-machine skill 一致）：
- 類別大駝峰、私有成員 `m_` 前綴、常數全大寫底線
- 註解 `/** @ch ... */`、`#region`/`#endregion`
- 倍率比較用 `tools.times()` 交叉相乘，避免浮點 `===` 誤差
- 不直接操作 framework 的 `m_isExtra`；透過 `ForceSetExtraBet` / `SetTwoStepMulti` 改狀態
