# Pattern: 蓄能容器（Pot / 角色等級）+ 滿級投放

## 識別條件

規格書出現以下描述時匹配：
- 「盤面上的現金符號會被角色/容器吸走，累積能量條或等級」
- 「等級滿（L5）時，容器把符號**丟回盤面**」
- 「等級會保留到下次遊玩」「等級不影響中獎結果」
- 主題別名：聚寶盆 / 金鍋 / 妖精的鍋 / 能量槽 / Meter

> ⚠️ **這是「演出用的假 meter」**：等級變化由 client 端隨機決定，投放內容由 server 決定。兩者接縫處是本 pattern 全部的坑。與 `progression-unlock.md`（真的解鎖玩法內容）不同，此 meter **不影響任何獎金結果**。

## 參考實作

| 專案 | 複雜度 | 特殊點 |
|------|--------|--------|
| leprechaunsGoldStreak（LGS） | 中 | 等級存 localStorage、5% 機率升級、server 有 `PotSymbols` 才強制升滿並投放 |

### 核心檔案（LGS）
- `Spine/CharacterSpine.ts` — 等級狀態機（`LevelUp` / `LevelMax` / `PlayThrow` / `PlayLastThrow`）+ `StoreLevel` / `RestoreLevel`
- `GameState/PotThrowState.ts` — 投放主流程；**有無 `PotSymbols` 走兩條完全不同的路**
- `EffectPlate.ts:636 PotCollect()` — MG 停輪時 CASH/JP 飛進容器
- `EffectPlate.ts:673 ThrowSymbol()` — 容器飛出符號 → 落點 Spawn
- `Game_Define.ts:69 POT_LVUP_RATE = 0.05` — client 端升級機率

## State 映射

**新增獨立 State `POT_THROW`**，插在 SPIN 與收集判定之間：

```
SPIN（停輪時 ReelStopEffect 把 CASH/JP 推進 m_collectPromises）
  → POT_THROW
      ├─ 有 PotSymbols：await 收集動畫 → LevelMax()
      │                 → 逐顆【PlayThrow()（不 await）+ await ThrowSymbol()】
      │                    最後一顆改用 PlayLastThrow()（L5→L1，等級同步歸 1）
      │                 → SlotReels.UpdatePlate(PlateSymbolLog, PlateNumLog)
      └─ 無 PotSymbols：Math.random() < 0.05 → await 收集動畫 → LevelUp() → PlayIdle()
  → CHECK_COLLECT
```

投放結束後**必須** `SlotReels.UpdatePlate()` 把底層盤面換成 `PlateSymbolLog`——投放是加符號到盤上，底層 sprite 若不更新，後續收集會讀到舊盤面。

## Data 需求

```typescript
interface RoundInfo {
  /** 只在「這手要投放」時出現；不存在 = 這手不投放 */
  PotSymbols?: IPotData[];
  PlateSymbolLog: IColumn[];   // 投放後的最終盤面
  PlateNumLog: IColumnFloat[];
}

interface IPotData {
  /** 投放的符號 id（CASH / JP / COLLECT / BONUS 都可能） */
  Symbol: number;
  /** 面值（CASH 類才有） */
  Value?: number;
  /** 扁平座標；col = floor(Pos / ROW), row = Pos % ROW。缺省視為 0 */
  Pos?: number;
}
```

> ⚠️ `Pos` 是**扁平索引**不是 {col,row}，且 LGS 假資料裡真的出現過**缺 `Pos` 的項目**（`{ Symbol: 9, Value: 0.5 }`）。解析必須 `potData.Pos ?? 0`，否則 `undefined / ROW` → NaN → 飛到畫面外。

**等級持久化**：`localStorage` key = `${AID}:${GAME_ID}:pot`，初始值 1，範圍 1~5。

## 演出時序

### A. 收集（每手停輪時，MG 限定）

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | `ReelStopEffect` 偵測 CASH/JP 且 `!IsInFG` → push `PotCollect()` 進 `m_collectPromises` | 不 await（收集動畫與停輪並行） | — |
| 2 | 每 col 首次播 `Collect_Fly`（快停時一次播完全部旗標） | 即時 | m_collectFlySounds |
| 3 | `PotFlySpine.CoinFly()` 從格子飛到容器收集點 | await | Character.GetCollectWorldPosition() |
| 4 | 全程只播一次角色 `PlayCollect()`（`m_hasCollect` 旗標） | await | — |

### B. 投放（PotThrowState）

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | `await Promise.all(CollectPromises)` 等收集全部飛完 | await | — |
| 2 | `LevelMax()` 逐級升到 L5（timeScale 1.5 加速） | await | 目前等級 |
| 3 | 循環播 `Pot_L5_Throw` 音效 + 逐顆 `ThrowSymbol()` | await（序列） | PotSymbols[] |
| 4 | 每顆投放**前**先觸發角色動畫（`PlayThrow()` / 最後一顆停循環音 + `PlayLastThrow()`）——**兩者都不 await**，與該顆的 `ThrowSymbol()` 並行 | 不 await | i === len-1 |
| 4a | ⚠️ `PlayLastThrow()` 內部把 `m_level` **同步設成 1**，不等動畫播完。等級歸 1 發生在最後一顆還在飛的時候 | — | — |
| 5 | 每顆落點依 Symbol 類型播不同音效（COLLECT / BONUS / 其他） | 即時 | potData.Symbol |
| 6 | 落點 `CreateSymbolNode()` + `PlaySpawn()` | await | Pos |
| 7 | `SlotReels.UpdatePlate(PlateSymbolLog, PlateNumLog)` | 即時 | — |

### C. 假升級（無投放時）

| Step | 動作 | 等待方式 |
|------|------|---------|
| 1 | `Math.random() < POT_LVUP_RATE`（5%） | 即時 |
| 2 | **不論升不升級，都要接上收集動畫的 Promise 解鎖轉向**（規格要求「假升級也要等」） | 見下方 |
| 3 | 升級：`await collectAnim` → `LevelUp()` → `PlayIdle()` | await |

```typescript
// LGS PotThrowState 的實際寫法——注意 collectAnim 無論 up 與否都先建立
let up = Math.random() < Game_Define.POT_LVUP_RATE;
let collectAnim = Promise.all( this.m_gameView.EffectPlate.CollectPromises ).then( () => {
    this.m_gameView.IsLockRotation = false;
} );
if ( up ) {
    await collectAnim;          // 只有升級時才擋住流程
    await this.m_gameView.Character.LevelUp();
    this.m_gameView.Character.PlayIdle();
}
// 不升級時不 await，收集動畫在背景跑完自行解鎖轉向
```

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 本地隨機升級 + server 投放 | 等級純演出，投放才是真結果 | LGS |
| server 給等級 | ack 帶 meter 值，client 只播 | 其他機台 |
| 等級決定投放數量 | 等級 = 真實玩法變數（此時屬 progression-unlock.md） | — |
| 投放內容含 COLLECT/BONUS | 投放可以直接製造觸發（LGS 假資料 Symbol 16/17 = BONUS/COLLECT） | LGS |
| FG 不收集 | LGS 的 `PotCollect` 只在 `!IsInFG` 觸發 | LGS |

## 邊界案例

1. **等級是裝置級持久狀態**：存 localStorage 且 key 綁 `AID + GAME_ID`。換裝置/清快取會回到 L1，這是預期行為不是 bug
2. **Demo / Replay 必須存還原等級**：進特色示範或復盤前 `m_oldLevel = Character.Level`，離開時 `SetLevel(m_oldLevel)`——否則 demo 裡的強制升滿會污染玩家真實 meter
3. **`StoreLevel()` 的呼叫時機在 IDLE**：LGS 在 `IdleState.Enter()` 才寫入，代表「演出全部結束、狀態穩定」才落盤。改在投放中途寫會存到過渡等級
4. **已在 L5 時 `LevelUp()` / `LevelMax()` 直接 return**：兩者都有上限檢查，但 `PlayLastThrow()` **無條件**把等級設成 1——投放流程若中途 return，等級會卡在 L5
5. **快停 / 切停的音效去重**：`m_collectFlySounds` / `m_potCollectSounds` 是 per-col 旗標，`isHardStop` 時直接把整個陣列填滿 true（只播一次），否則五列同時飛會疊五層音效
6. **`IsLockRotation` 的成對釋放**：投放期間鎖定螢幕旋轉，兩條分支（有/無 PotSymbols）都必須把它放掉——無投放分支是靠 `collectAnim.then()` 放，漏掉會永久鎖住
7. **投放落點若已有動態 node 是「重用」不是「覆寫」**：`CreateSymbolNode()` 先讀 `m_symbolNodes[col][row]`，有值就直接沿用該 node（只有 null 才從 NodePool 取新的）。後果分三種——
   - 落到**純靜態格**（無動態 node）：正常新建，符合直覺
   - 落到**同型格**（COLLECT 投到已有 COLLECT 的格）：沿用舊 node，`SetValue(0)` 會把累計值歸零
   - 落到**異型格**（CASH 投到 COLLECT 格）：`getComponent(CashSymbolSpine)` 取到 null → 直接拋錯

   ∴ server 給的 `Pos` 落在鎖定的收集器格子上，不是「蓋掉收集器」而是資料錯誤，且異型時會直接 crash

## 常見錯誤

1. **❌ 把 `Pos` 當 {col,row} 解析**：它是扁平索引，`col = floor(Pos/ROW)`、`row = Pos % ROW`；且要 `?? 0` 防缺欄
2. **❌ 不升級時就不等收集動畫**：規格明示「假升級也要等」——收集飛行動畫仍在跑，直接進下一個 State 會讓飛行中的符號被 `ClearAllEffect()` 砍掉
3. **❌ 投放後忘了 `UpdatePlate`**：`ThrowSymbol` 只加了演出層 node，底層 SlotReels sprite 還是舊盤面 → 後續 `CollectCashSymbol` 讀 plate 讀得到、但畫面對不上
4. **❌ 用 meter 等級推算玩法結果**：等級是 client `Math.random()` 決定的，跟 server 完全無關；任何「L5 才會投放」的邏輯都是倒果為因（實際是「server 說要投放 → client 才強制升滿」）
5. **❌ Demo/Replay 沒還原等級**：示範模式會強制 LevelMax → 投放 → 歸 1，玩家離開示範後真實 meter 被清成 1
6. **❌ 收集動畫的 Promise 陣列跨手殘留**：`m_collectPromises` 必須在 `ClearAllEffect()`（SpinState 進入時）清空，否則會 await 到上一手的 Promise
