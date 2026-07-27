# Pattern: Hold & Win（鎖定收集器 + 局數重置）

## 識別條件

規格書出現以下描述時匹配：
- 「觸發後進入 N 局獎金遊戲，**每次有新符號落下，局數重置回 N**」
- 「收集符號固定不動（鎖定），未鎖定的輪繼續旋轉」
- 「獎金遊戲結束時，收集器內累計的金額一次結算」
- 主題別名：Link & Win / Hold & Spin / Cash Collect FG / 「聚寶」FG

> ⚠️ **與 `respin.md` 的分界**：傳統 Respin 鎖的是**中獎符號本身**（CASH 留在盤上，集滿盤面才結算）。本 pattern 鎖的是**收集器**（COLLECT 符號），CASH 每手落下即被吸走並累加進收集器。兩者都用「新符號 → 重置次數」，但鎖定對象、結算時機、盤面殘留完全不同——照 respin 的模型做會發現「盤上 CASH 為何消失」對不上。

## 參考實作

| 專案 | 複雜度 | 特殊點 |
|------|--------|--------|
| leprechaunsGoldStreak（LGS） | 高 | 收集器鎖在**中央輪 col 2**、逐 row 獨立累加、FG 末局一次結算 |

### 核心檔案（LGS）
- `GameState/CheckCollectState.ts` — 收集主流程 + `remain == 3 && !maxFlag` 觸發計數器重置
- `GameState/SpinState.ts` — `FGCounter.Reduce()`（每手減 1）
- `GameState/EnterFreeState.ts` — 進 FG 首次收集（觸發手的收集延後到這裡做）
- `GameState/CheckState.ts` — `Round >= RoundQueue.length - 1 || maxFlag` → LEAVE_FREE
- `SlotReels.ts:1420 SetSymbolLock()` / `StartSpin()` — 邏輯層鎖；**全 row 鎖滿時整列跳過旋轉**
- `EffectPlate.ts:367 SetSymbolLock()` — 演出層獨立一份鎖（兩層都要設，見常見錯誤 1）
- `Spine/FGCounterSpine.ts` — 3→2→1→0 的 spine 計數器 + `Reset()` 回 3 的專屬動畫

## State 映射

**不新增 respin 專用 State**。整個 Hold & Win 就是「FG 的每一手」，靠 `RoundQueue` 陣列驅動：

```
CHECK_STATE
  ├─ !IsInFG && RoundQueue.length > 1        → ENTER_FREE（進 FG，做觸發手的收集）
  ├─ IsInFG && (Round >= len-1 || MaxFlag)   → LEAVE_FREE（結算收集器）
  └─ else                                    → ROUND_END → SPIN（下一手）

每手：SPIN（FGCounter.Reduce）→ POT_THROW → CHECK_COLLECT（收集 + 可能 Reset 回 3）
      → CHECK_MAX_FLAG → ROUND_SHOW_END → CHECK_STATE
```

關鍵：**剩餘手數由 server 的 `BonusRemainRound` 決定，client 只負責播動畫**。client 端 `FGCounter` 的 `m_round` 僅供選對 spine 動畫名（`Time_3_to_2` / `Time_1_to_3`），不是判定依據。

## Data 需求

```typescript
// LGS 實際 proto（lgsProto.ISpinAck）
interface SpinAck {
  RoundQueue: RoundInfo[];   // [0] = MG 觸發手，[1..n] = FG 各手
  BonusTotalWin?: number;    // FG 總贏分
  TotalWin: number;
}

interface RoundInfo {
  /** 停輪盤面（演出前） */
  PlateSymbol: IColumn[];        // { Col: number[] }[]，外層 col、內層 row
  PlateNum: IColumnFloat[];      // 同座標的面值（CASH/JP 才有值）
  /** 演出全部結束後的最終盤面（含 Pot 投放、收集後的結果）——見 unshow-recover.md 附錄 */
  PlateSymbolLog: IColumn[];
  PlateNumLog: IColumnFloat[];

  /** 每個 row 的收集器累計值（0 = 該 row 無收集器） */
  Collected: number[];           // length = ROW
  /** 已進行第幾手（1-based，觸發手無此欄） */
  BonusNowRound?: number;
  /** 剩餘手數；有新符號落下時 server 會重置回 3 */
  BonusRemainRound?: number;
  /** 只在最後一手出現 = Σ Collected */
  CollectWin?: number;
  RoundWin?: number;
  MaxFlag?: boolean;
}
```

**`BonusRemainRound` 的實際軌跡**（LGS `FeatureAck.ts` 假資料，可直接當回歸基準）：

| 手 | BonusNowRound | BonusRemainRound | 該手是否有新 CASH 落下 |
|----|---------------|------------------|----------------------|
| 觸發手 | —  | 3 | （進 FG） |
| 1 | 1 | 3 | 有 → 重置 |
| 2 | 2 | 3 | 有 → 重置 |
| 3 | 3 | 2 | 無 → 遞減 |
| 4 | 4 | 1 | 無 → 遞減 |
| 5 | 5 | （無此欄）| 無 → 結束，帶 `CollectWin` |

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | SPIN 進入，`FGCounter.Reduce()` 播 `Time_N_to_N-1` | 不 await（與旋轉並行） | m_round |
| 2 | 未鎖定列旋轉；**全鎖的列整列跳過**（不重設 stopTime、不開上下延伸符號） | — | m_collectLock.every() |
| 3 | 停輪，新 CASH / COLLECT 播 Stop/Spawn | await stopPromises | CheckStop() |
| 4 | 逐 row 收集：`CollectCashSymbol(spCol, row, ...)` 依 row 順序 await | await（序列） | Collected[row] |
| 5 | JP 收集（若有）`CollectJP()` | await | 見 collect-feature.md |
| 6 | `remain == 3 && !maxFlag` → `FGCounter.Reset(3)` 播 `Time_N_to_3` + 音效 | await | BonusRemainRound |
| 7 | 兩層 `SetSymbolLock(plate)` 同步鎖定狀態 | 即時 | PlateSymbolLog |
| 8 | 末局：`ShowBGAward()` 全收集器播 Win → `BGCompliment` 結算面板 | await | BonusTotalWin |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 鎖收集器（本卡） | COLLECT 鎖定，CASH 每手被吸走 | LGS |
| 鎖 CASH（傳統 Hold&Spin） | CASH 留在盤上，集滿盤面才結算 | 見 respin.md |
| 收集器在中央輪 | spCol = 2，逐 row 各自累加 | LGS |
| 收集器在頭尾輪 | col 0 / col 5 各自收分 | 見 collect-feature.md「雙向 Collect」 |
| 重置局數 N | LGS 為 3；其他機台常見 3 / 5 | — |
| 全盤鎖滿 = 提前結束 | LGS 未採用（靠 remain 歸零） | 傳統 Hold&Spin |

## 邊界案例

1. **鎖定要設兩層**：`SlotReels.SetSymbolLock()`（決定該列還轉不轉）+ `EffectPlate.SetSymbolLock()`（決定停輪特效放不放）是**兩個獨立陣列**，只設一個會出現「符號不轉但每手重播 Stop 動畫」或反之
2. **解鎖用 `SetSymbolLock(null)`**：離開 FG 時兩層都要傳 `null` 清空，否則回 MG 中央輪還是不轉（`LeaveFreeState` 有做）
3. **觸發手的收集延後到 ENTER_FREE**：MG 中獎進 FG 時，`CheckCollectState` 只收 Bonus 符號（`CollectBonus`），CASH/JP 的收集在 `EnterFreeState` 才做——因為要先播完 FG 宣告、換背景、`ChangeEmptySymbol()` 清盤才收得好看
4. **`FGCounter.Reset()` 的動畫名靠 client 端 `m_round`**：若 client 的 `m_round` 與 server `BonusRemainRound` 不同步（例如漏播一次 Reduce），`RESET_ANIM[m_round]` 會取到錯的動畫或 undefined
5. **`remain == 3` 不等於「這手有新符號」**：第一手進 FG 時 remain 本來就是 3。LGS 用 `Game_Define.IsInFG` 分支把觸發手排除在外，別直接拿 `remain == 3` 當「有新符號」的唯一判準
6. **MaxFlag 同手觸發時不播 Reset**：`remain == 3 && !maxFlag` 的 `!maxFlag` 是必要的——封頂當手要直接走結算，不該播「重置回 3」誤導玩家還有 3 手
7. **斷線重連**：鎖定狀態不可用 client 本地累加，必須從 `PlateSymbolLog` 重建 + `Collected[]` 還原累計值（見 unshow-recover.md）
8. **收集器數值只在末局換成 CollectWin**：中間各手 `Collected[]` 會長大但 `CollectWin` 不存在；別在每手都拿 `CollectWin` 加總

## 常見錯誤

1. **❌ 只設一層 SetSymbolLock**：邏輯層與演出層各有一份鎖，漏設演出層 = 鎖定的收集器每手重播 Stop 動畫；漏設邏輯層 = 收集器跟著轉走
2. **❌ 用 client 本地計數決定 FG 何時結束**：手數權威是 server 的 `RoundQueue.length` 與 `BonusRemainRound`；本地 counter 只驅動 spine 動畫
3. **❌ 把觸發手也當成 FG 的一手**：`RoundQueue[0]` 是 MG 觸發手，FG 從 `[1]` 開始；用 `Round` 直接當 FG 手數會多算一手
4. **❌ 離開 FG 忘了 `SetSymbolLock(null)`**：回 MG 後中央輪永遠不轉，且是「下一手才發現」的延遲爆炸
5. **❌ 拿 respin 的「全盤鎖滿即結束」套上來**：本變體收集器只有 ROW 個位置，鎖滿是常態（每手都鎖滿也還有 3 手），提前結束會砍掉玩家該得的手數
