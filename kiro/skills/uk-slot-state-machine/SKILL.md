---
name: uk-slot-state-machine
description: UK 老虎機狀態機設定，新增、移除或修改 SetStateMachine() 遊戲狀態時觸發。
---

# Slot 狀態機設定

## 檔案位置

`assets/Script/GameView.ts` → 私有方法 `SetStateMachine()`

## 標準狀態機模板

```typescript
private SetStateMachine() {
    let states = {};

    // ── 框架通用狀態（CommonState）──────────────────
    states[ CommonState.WAIT_RES ]    = new WaitResState( this );
    states[ CommonState.IDLE ]        = new IdleState( this );
    states[ CommonState.SPIN ]        = new SpinState( this );
    states[ CommonState.CHECK_STATE ] = new CheckState( this );

    // ── 遊戲流程狀態 ────────────────────────────────
    states[ Game_Define.GameState.WAIT_READY ]      = new WaitReadyState( this );
    states[ Game_Define.GameState.PLATE_SHOW ]      = new PlateShowState( this );
    states[ Game_Define.GameState.FEATURE_SHOW ]    = new FeatureShowState( this );
    states[ Game_Define.GameState.UNSHOW_PREPARE ]  = new UnshowPrepareState( this );
    states[ Game_Define.GameState.AWARD ]           = new AwardState( this );
    states[ Game_Define.GameState.ROUND_SHOW_END ]  = new RoundShowEndState( this );
    states[ Game_Define.GameState.ROUND_END ]       = new RoundEndState( this );
    states[ Game_Define.GameState.EFFECT_START ]    = new EffectStartState( this );
    states[ Game_Define.GameState.SCATTER_SHOW ]    = new ScatterShowState( this );

    // ── 免費遊戲狀態 ────────────────────────────────
    states[ Game_Define.GameState.ENTER_FREE ]   = new EnterFreeState( this );
    states[ Game_Define.GameState.FULL_REWARD ]  = new FullRewardState( this );
    states[ Game_Define.GameState.ADD_FREE ]     = new AddFreeState( this );
    states[ Game_Define.GameState.LEAVE_FREE ]   = new LeaveFreeState( this );

    // ── 選用狀態（依遊戲需求啟用）──────────────────
    // states[ Game_Define.GameState.CHECK_JP ] = new CheckJpState( this );  // Jackpot 檢查

    stateManager.Init( states );
    stateManager.NextState( CommonState.LOGIN );  // 固定起點，勿移除
}
```

## 規則

1. `stateManager.NextState( CommonState.LOGIN )` 是初始觸發點，**不可移除**。
2. 新增自訂狀態前，需先在 `Game_Define.ts` 的 `GAMEVIEW_STATE` 列舉中新增對應 Key。
3. 新增狀態類別檔案後，需在 `GameView.ts` 頂部補上對應 `import`。
4. `CHECK_JP` 等選用狀態預設以註解停用；有需要時取消註解，不要刪除。
5. 狀態切換一律透過 `stateManager.NextState(...)` 呼叫，不直接操作狀態物件。

## 新增自訂狀態的步驟

1. 從 `assets/GameState/` 選最接近的狀態模板複製到 `assets/Script/GameState/MyState.ts`
2. 修改類別名稱、`@ccclass`、log 字串中的狀態名稱
3. 在 `Game_Define.ts` 的 `GAMEVIEW_STATE` 列舉加入新 Key（例如 `MY_STATE`）
4. 在 `GameView.ts` 加入 import：`import { MyState } from "./GameState/MyState";`
5. 在 `SetStateMachine()` 加入：`states[ Game_Define.GameState.MY_STATE ] = new MyState( this );`

## 狀態模板（assets/GameState/）

`assets/GameState/` 收錄所有 19 個狀態的完整模板，每個模板：
- **已含 `log( "OnEnter State : ..." )`** 和 **`log( "OnLeave State : ..." )`**（使用 `log` from `cc`）
- 業務邏輯完整保留，可直接複製修改
- `CheckJpState.ts` 已解除全行註解，可直接啟用

| 模板檔案 | 適合作為... |
|---------|------------|
| `AddFreeState.ts` | 追加免費次數類狀態 |
| `AwardState.ts` | 需等待非同步完成的表演狀態 |
| `CheckState.ts` | 路由判斷狀態（無等待直接切換）|
| `EnterFreeState.ts` / `LeaveFreeState.ts` | 多系統初始化 / 清理狀態 |
| `EffectStartState.ts` | 需條件等待的特效狀態 |
| `FullRewardState.ts` | Placeholder 類狀態（待填入）|
| `CheckJpState.ts` | 選用功能狀態（需時解除註解啟用）|

## 詳細狀態說明

各狀態的完整說明請參閱 [references/states.md](references/states.md)。
