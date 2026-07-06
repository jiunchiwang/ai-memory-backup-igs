# Template: State Machine + API Surface

uk_slot_template 基礎架構參考。所有衍生遊戲以此為起點擴展。

## 1. State Machine 完整清單（18 States）

### Framework CommonState（4 個，不可改）

| State | 用途 |
|-------|------|
| LOGIN | 初始觸發點（stateManager.NextState 起點） |
| WAIT_RES | 等待 server 回應 SpinAck |
| IDLE | 等待玩家操作（按 Spin） |
| SPIN | 轉輪旋轉中 |
| CHECK_STATE | 路由器：根據結果分派到對應 State |

### GAMEVIEW_STATE（14 個，可擴展）

| State | 用途 | 常見 async |
|-------|------|-----------|
| WAIT_READY | 進場後等資源就緒 | — |
| PLATE_SHOW | 盤面展示（停輪後的初始表演） | await spine |
| FEATURE_SHOW | Feature 類演出（Collect/Multiplier/Mystery 等） | await |
| UNSHOW_PREPARE | Unshow 還原準備（回復上一手的特效） | — |
| AWARD | 對獎 + 贏分動畫 | await BigWinComponent |
| ROUND_SHOW_END | 回合展示收尾 | — |
| ROUND_END | 回合結束，準備回 IDLE | — |
| EFFECT_START | 條件式特效播放 | await |
| SCATTER_SHOW | Scatter 飛入/盆子演出 | await spine |
| ENTER_FREE | 進入免費遊戲（轉場） | await |
| FULL_REWARD | 全盤獎勵 | await |
| ADD_FREE | 追加免費次數 | await panel |
| LEAVE_FREE | FG 結算 + 離場 | await |
| CHECK_JP | Jackpot 檢查（預設註解） | await panel |

## 2. CheckState 路由邏輯

```typescript
// Template 基礎版
if (IsGoingToFree)      → ENTER_FREE
if (IsFreeGame && 最後一局) → LEAVE_FREE
else                     → ROUND_END
```

衍生遊戲在此增加分支：
```typescript
// eye_strike 增加
if (IsGoingToRespinGame) → ENTER_RESPIN
if (IsRespinGame)        → LEAVE_RESPIN

// 722/746 增加
if (IsGoingToBonus)      → ENTER_BONUS
```

## 3. GameView 核心 API

| 方法 | 用途 |
|------|------|
| `SetStateMachine()` | 註冊所有 State |
| `OnCommand(cmd)` | 接收底部操作列指令（Spin/Stop/Auto） |
| `OnRecvSpinAck(data)` | 收到 server 回應，解析並儲存 |
| `StartSpin()` | 觸發轉輪開始旋轉 |
| `ClickSpin()` | 玩家點擊 Spin |
| `ClickStop()` | 玩家點擊快停 |
| `ForEndToNext()` | Feature/Award 完成後推進到下一步 |
| `SetComboData()` | 設定連擊資料 |
| `PauseMainGameBgm() / PlayFreeGameBgm()` | 音樂切換 |
| `get IsFreeGame / set IsFreeGame` | 免費遊戲旗標 |

## 4. SlotReels 核心 API

| 方法 | 用途 |
|------|------|
| `StartSpin(columns?)` | 開始旋轉指定列 |
| `ClickStopBtn()` | 快停所有列 |
| `SetPlateInfo(plateData)` | 設定真實盤面資料（server 回傳） |
| `SetSpinMode(mode)` | 切換旋轉模式（Standard/Cascade/Tumble） |
| `SwitchReelMode(mode)` | 切換盤面大小（擴展用） |
| `Explode(positions)` | 消除指定位置符號 |
| `Fill(fillData)` | 補位（消除後） |
| `SetLayoutConfig(config)` | 動態改佈局 |
| `SetEntryStrategy(strategy)` | 設定補位入場策略 |
| `get AllColumns` | 取得所有列的 ColumnSymbol |

## 5. astarte-framework 提供的 Manager/Component

| 模組 | 用途 |
|------|------|
| `stateManager` | 狀態機引擎（Init/NextState） |
| `eventManager` | 全域事件總線（Register/Emit） |
| `CommonGameManager` | 遊戲通用管理 |
| `newBottombarManager` | 底部操作列（Bet/Spin/Auto/Balance） |
| `ConnectionManager` | WebSocket 連線 |
| `SoundManager` | 音效播放 |
| `BigWinComponent` | 大報獎 UI（BIG/MEGA/SUPER WIN） |
| `ExtraBetComponent` | ExtraBet 按鈕/Bar |
| `extraBetController` | ExtraBet 全域 controller |
| `BaseState` | State 基類（OnEnter/OnLeave/OnUpdate） |
| `CommonBuyBonus` | Buy Bonus 基礎 UI |

## 6. 新增 State 的步驟

1. 在 `Game_Define.ts` 的 `GAMEVIEW_STATE` enum 加入新 key
2. 建立 `assets/Script/GameState/MyState.ts`，繼承 `BaseState`
3. 實作 `OnEnter()`（async 可用）和 `OnLeave()`
4. 在 `GameView.ts` import + `SetStateMachine()` 註冊
5. 在 `CheckState.ts` 加入路由條件

## 7. Game_Define.ts 標準欄位（新遊戲需改）

| 欄位 | 說明 | 範例 |
|------|------|------|
| `COL` | 列數 | 5 或 6 |
| `ROW` | 行數（MG） | 3 或 4 |
| `MAX_ROW` | 最大行數（擴展時） | 5 或 7 |
| `FULL_PLATE_NUM` | 總格數 | COL × ROW |
| `Symbol` enum | 符號列舉 | 依遊戲 |
| `SymbolHeight / SymbolWidth` | 符號像素大小 | 82 / 96 |
| `PlateEftOdds` | 報獎倍數門檻 | [1, 3, 6, 15, 30] |
| `WinType` | 贏分等級 | NoWin/Normal/Big/Mega/Super |
| `Color.Light / Color.Dark` | 壓暗色 | — |
| `IsFG` | 免費遊戲旗標 | — |
| `StringKey` | 多語系 key | — |

## 8. 常用 Common 工具

| 工具 | 用途 | 檔案 |
|------|------|------|
| `AsyncUtils.WaitForSeconds(sec)` | async 等待 N 秒 | Common/AsyncUtils.ts |
| `AsyncUtils.WaitUntil(predicate)` | async 等待條件成立 | Common/AsyncUtils.ts |
| `AsyncUtils.CancelToken` | 取消非同步操作 | Common/AsyncUtils.ts |
| `PrefabPoolManager` | Prefab 物件池（中獎框/飛行特效） | Common/PrefabPoolManager.ts |
| `NumberAnimation` | 數字滾動動畫（分數跳動） | Common/NumberAnimation.ts |
| `NodeProperty` / `getUItrans()` | 便捷取 UITransform | Common/NodeProperty.ts |
| `FrameAnimation` | 逐幀動畫播放 | Common/FrameAnimation.ts |
| `BaseSpine` / `InLoopOutSpine` | Spine 播放封裝（In→Loop→Out 三段式） | Spine/ |
| `RouletteRotate` | 輪盤旋轉（抽獎轉盤） | Common/RouletteRotate.ts |
| `SpriteChange` | 圖片切換 | Common/SpriteChange.ts |
