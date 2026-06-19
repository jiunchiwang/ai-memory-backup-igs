# unshow / replay 還原 ExtraBet type

## 問題

unshow（斷線重連補表演）或 replay 還原時，需把 ExtraBet 同步回玩家當初的狀態。`ExtraBetComponent.ForceSetExtraBet(isActive, type = TYPE.Special)` 的 `type` **預設值是 `TYPE.Special = 1`**。

若遊戲有多種倍率（`Mul[1]`、`Mul[2]`、`Mul[3]`），而還原時只呼叫 `ForceSetExtraBet(true)` 不帶 type，會**永遠還原成第一種**，遺失玩家當初選的種類（第 2、3 種）。

## 解法：依押注比值反推 type

伺服器提供兩個值（`commonGameManager`）：

| 欄位 | 意義 |
|------|------|
| `UnshowBaseBet` | 原始押注（未乘 ExtraBet 倍率） |
| `UnshowRealBet` | 真實押注（已乘倍率） |

關係：`UnshowRealBet / UnshowBaseBet === Mul[type] / Mul[0]`

反推：找出 `type` 使下式成立（交叉相乘避免除法/浮點誤差）：
```
Mul[type] × UnshowBaseBet === UnshowRealBet × Mul[0]
```

## 本專案實作（GameView.ts）

前提：GameView 在收到 GameInfo 時已 `this.m_betMultipliers = info.Mul.slice()` 保存倍率表（見 architecture.md）。

```typescript
public async RestoreExtraBetState() {
    await this.m_extraBetComp?.ForceSetExtraBet( true, this.GetUnshowExtraBetType() );
}

/**
 * @ch 依 unshow 的原始/真實押注比值反推 ExtraBet type（即 Mul 索引）
 * @description Mul[type]/Mul[0] === UnshowRealBet/UnshowBaseBet；用交叉相乘（tools.times）避免浮點誤差。
 * 倍率表不足或對不上時保底回 1（Special），維持還原不中斷
 */
private GetUnshowExtraBetType(): number {
    const FALLBACK_TYPE = 1;
    const baseBet = commonGameManager.UnshowBaseBet;
    const realBet = commonGameManager.UnshowRealBet;
    const mul = this.m_betMultipliers;

    if ( !mul || mul.length <= 1 || baseBet <= 0 ) {
        error( `[GameView] ExtraBet 還原資料不足 (mul=${mul}, baseBet=${baseBet})，保底用 type=${FALLBACK_TYPE}` );
        return FALLBACK_TYPE;
    }

    const target = tools.times( realBet, mul[ 0 ] );
    for ( let type = 1; type < mul.length; type++ ) {
        if ( tools.times( baseBet, mul[ type ] ) === target ) {
            return type;
        }
    }

    error( `[GameView] ExtraBet 倍率對不上 (baseBet=${baseBet}, realBet=${realBet}, mul=${mul})，保底用 type=${FALLBACK_TYPE}` );
    return FALLBACK_TYPE;
}
```

## 呼叫時機（UnshowPrepareState）

`UnshowPrepareState.RestoreUI()` 只在「曾開啟 ExtraBet」時才還原：
```typescript
if (this.m_gameView.UnshowSpinAck != null && commonGameManager.UnshowBaseBet < commonGameManager.UnshowRealBet) {
    await this.m_gameView.RestoreExtraBetState();
}
```
`UnshowBaseBet < UnshowRealBet` 即代表當初有乘倍率（開了 ExtraBet）。

## 注意事項

- **浮點比較**：務必用 `tools.times()` 交叉相乘，不要直接 `realBet / baseBet === mul[type]`（浮點誤差會導致對不上）
- **fallback 行為**：對不上時回 `type=1` 並 `error()` 警示（沿用專案 `UnshowPrepareState` out-of-range 的 fallback 慣例），維持還原不中斷
- **Mul[0] 前提**：公式採通用形 `Mul[type]/Mul[0]`。`Mul[0]=1`（一般情況）時完全正確。若伺服器把 `UnshowBaseBet` 定義為「未含 `Mul[0]` 的原始 bet」且 `Mul[0]≠1`，需改為不含 `Mul[0]` 的比較；實機若頻繁落到 fallback warning，先檢查此前提
- **FreeGame 還原順序**：unshow 還原進 FreeGame 時，`RestoreExtraBetState` 的動畫 await 必須在節點被 `SetExtraBetVisible(false)` 設為 inactive **之前**完成，否則動畫在 inactive node 上 await 不 resolve（見 architecture.md 顯隱規則）
