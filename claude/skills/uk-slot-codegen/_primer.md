# Framework Primer（≤500 字速覽）

## astarte-framework 架構

UK Slot 專案使用 `astarte-framework`（放在 `extensions/`）提供共用基建。

### StateManager 雙層設計

```
CommonState（framework 內建，不需遊戲端註冊）
├─ LOGIN          — 初始化、等 server GameInfo
├─ WAIT_RES       — 遊戲端提供（繼承點）
├─ IDLE           — 遊戲端提供（繼承 Common_IdleState）
├─ SPIN_REQ       — framework 自動處理 spin request 發送
├─ SPIN           — 遊戲端提供（轉輪動畫）
├─ COMMON_SHOW    — framework 自動處理共用表演、轉場
├─ CHECK_STATE    — 遊戲端提供（判斷進/出 FG）
├─ END            — framework 結束 round 並回 IDLE
├─ CHECK_FREESPIN — 斷線重連恢復 FG 用
└─ FREESPIN_WAIT_RES — FG 模式下 spin 等待

Game_Define.GameState（遊戲自訂，必須在 SetStateMachine 註冊）
├─ WAIT_READY / PLATE_SHOW / FEATURE_SHOW / UNSHOW_PREPARE
├─ AWARD / ROUND_SHOW_END / ROUND_END
├─ EFFECT_START / EXPLODE / MATCHING_PATCH_UP
├─ SCATTER_SHOW / ENTER_FREE / LEAVE_FREE / ADD_FREE / FULL_REWARD
└─ …（遊戲特有 state）
```

### 關鍵規則

1. **CommonState 不能替換**：`RoundShowEndState` → `COMMON_SHOW`，`ForEndToNext` → `END`（framework 負責 FG 續局判斷）
2. **遊戲端只註冊 4 個 CommonState**：`IDLE`/`SPIN`/`WAIT_RES`/`CHECK_STATE`（繼承 framework 抽象類）
3. **其餘 CommonState 由 stateManager.Init 自動處理**（類似內建中間件）

### Mock 模式語意

Mock = 接別遊戲的 server + 用假盤面資料覆蓋 SpinAck。所有框架通訊（GameInfo/RoundEnd/heartbeat）正常走。`USE_MOCK_SERVER` 唯一用途：`OnCommand(AckType.spin)` 裡用 `GenerateMockSpinAck()` 取代 decode 結果。

### BigWin 報獎

公版 API：`this.m_gameView.BigWin.Show(win, lvl)`（BigWinComponent from framework）。`ShowBigWin` 不存在。AudioClips 定義在 `AudioManager` 上（不在 Game_Define）。
