# Pattern: Unshow 斷線復原

## 識別條件

規格書出現以下描述時匹配：
- 「玩家在演出未播完就離線，下次進入需回到中斷點」
- 「重連後跳提示視窗，按確定接續播放」
- 「獎金遊戲進行中斷線，需還原盤面、鎖定、累計金額、剩餘手數」

這是**橫切機制**（cross-cutting），框架提供管線（`commonGameManager.HasUnshow` / `UnshowStartRound`、`msgBoxManager` 的 `MSGBOX_UNSHOW_BACK`），但**每個遊戲要自己寫還原內容**——這一段就是本卡的價值。

> 每一款都必須做，但「還原什麼」完全取決於該遊戲有哪些持久狀態。做 Feature 時就該同步問：**這個狀態斷線後怎麼回來？**

## 參考實作

| 專案 | 複雜度 | 特殊點 |
|------|--------|--------|
| leprechaunsGoldStreak（LGS） | 中 | MG / FG **兩條完全不同的還原路徑**；收集器累計值、雙層鎖定、FG 計數器 |
| eye_strike / 各 ExtraBet 機台 | 低 | `ForceSetExtraBet()` 還原加注狀態（見 extra-bet.md 邊界案例 1） |

### 核心檔案（LGS）
- `GameState/UnshowPrepareState.ts` — 還原主流程
- `EffectPlate.ts:1025 UnshowRecover()` — 重建收集器 node 並灌回累計值
- `GameView.ts StartSpin()` — MG 路徑的補播入口

## State 映射

```
（登入後收到 unshow 封包 → m_unshowSpinAck）
  → UNSHOW_PREPARE
      ├─ FG 路徑（commonGameManager.UnshowStartRound 有值）
      │    重建盤面/鎖定/收集器/計數器 → 清 HasUnshow → msgbox → SPIN
      └─ MG 路徑（UnshowStartRound 為 0/undefined）
           不重建盤面，保留 HasUnshow → msgbox → SPIN
             → StartSpin() 裡 `if (HasUnshow) OnRecvSpinAck(m_unshowSpinAck)` 整手重播
```

**兩條路徑的關鍵差異**：MG 只有一手，直接把整包 ack 當新的一手重播即可；FG 有多手且有跨手累積狀態（收集器金額、鎖定、剩餘手數），必須先把「上一手結束時的畫面」重建出來，才能從中斷點續播。

判準就是 `HasUnshow` 這個旗標**清或不清**——FG 路徑清掉（自己重建完了），MG 路徑留著（交給 `StartSpin` 補播）。搞反就是「FG 重播兩次」或「MG 完全不播」。

## Data 需求

```typescript
// server 送的是同一個 SpinAck 結構，只是走 unshow 封包
interface UnshowContext {
  ack: SpinAck;                    // 與正常 spin 相同的完整結果
  unshowStartRound: number;        // 1-based，中斷在第幾手；0/undefined = MG
  hasUnshow: boolean;              // 框架旗標
}

// SpinAck 內用來還原的欄位
interface RoundInfo {
  PlateSymbolLog: IColumn[];       // ← 還原一律用 Log（演出後的最終盤面）
  Collected: number[];             // 收集器累計值
  BonusRemainRound?: number;       // 剩餘手數
}
```

## 演出時序（FG 路徑）

| Step | 動作 | 說明 |
|------|------|------|
| 1 | `SkipIntro()` | 跳過前導動畫，直接進遊戲畫面 |
| 2 | `ForceSetExtraBet(ack.Extra)` | 加注狀態要在盤面重建**前**還原（影響假轉輪與符號皮） |
| 3 | `Round = unshowStartRound - 1` | 指向**前一手**，因為接著要從那手的結果續播 |
| 4 | `IsInFG = true` + `SwitchBackground(true)` | 背景/BGM/特效切 FG |
| 5 | 取 `PlateSymbolLog`，**把 `symbol < BRONZE` 全改成 EMPTY** | 一般線獎符號不還原，只留特殊符號 |
| 6 | `SlotReels.SetPlateSymbol(plateArray)` | 寫底層盤面 |
| 7 | 對非 EMPTY 格 `SetSymbolActive(col,row,false)` | **關掉底層 sprite**，改由 EffectPlate 的動態 node 呈現 |
| 8 | `EffectPlate.UnshowRecover(plate, collected)` | 建收集器 node + 灌回累計金額 + 播 Idle |
| 9 | `EffectPlate.SetSymbolLock()` + `SlotReels.SetSymbolLock()` | **兩層都要**（見 hold-and-win-lock.md 常見錯誤 1） |
| 10 | `FGCounter.SetRound(remain)` | 直接設值不播減少動畫 |
| 11 | 清 `commonGameManager.HasUnshow` + `m_unshowSpinAck = null` | FG 路徑專屬 |
| 12 | 播 BGM（依 `IsInFG` 選 MG/BG） | — |
| 13 | `newExtraManager.HasUnshow = false` | 框架端旗標 |
| 14 | `msgBoxManager.ShowMessageBox(MSGBOX_UNSHOW_BACK, ...)` → callback `NextState(SPIN)` | 玩家按確定才續播 |

### 收集器累計值的還原（EX 陷阱）

```typescript
// EffectPlate.UnshowRecover——COLLECT_EX 有兩個收集槽，值要對半拆
if ( symbol == Game_Define.Symbol.COLLECT ) {
    spine.SetValue( collected[ row ] );
} else if ( symbol == Game_Define.Symbol.COLLECT_EX ) {
    let value = tools.divide( collected[ row ], 2 );
    spine.SetValue( value, 0 );
    spine.SetValue( value, 1 );
}
```

`Collected[row]` 是**兩槽加總**。EX 狀態下不對半拆 → 畫面顯示的金額變兩倍，且後續 `AddValue()` 從錯的基數往上加。

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| MG 整手重播 | 不重建狀態，把 ack 當新一手丟回 `OnRecvSpinAck` | LGS |
| FG 續播 | 重建上一手畫面 + 從中斷點接續 | LGS |
| 只還原 UI 狀態 | 無跨手累積的機台（純線獎）只要還原 ExtraBet | 多數簡單機台 |
| Replay 復盤 | 走另一條路（`GameRecover()`），但要還原的清單高度重疊 | LGS |

## 邊界案例

1. **`Round` 要指向前一手**：`unshowStartRound - 1`。設成 `unshowStartRound` 會跳過一手
2. **`ForceSetExtraBet` 必須在盤面重建前**：它會切假轉輪帶與符號皮（`SwitchReel`），順序反了盤面會用錯的圖
3. **只還原特殊符號**：`symbol < BRONZE` 的一般符號一律換 EMPTY——FG 盤面本來就只該有 CASH/JP/COLLECT
4. **底層 sprite 與演出層 node 的顯示權**：還原後特殊符號由 EffectPlate 的動態 node 負責，底層 `SetSymbolActive(false)`。兩層同時顯示 = 疊圖
5. **`FGCounter.SetRound()` 不是 `Reduce()`**：還原是設定不是遞減，且它內部依 `round == 3` 選 `Show` 或 `SPIN_ANIM[round]`——`round` 必須在 0~3 內，否則取到 undefined 動畫
6. **不重播提示面板**：若中斷點在「已跳過 MAX WIN 提示」之後，還原不該再跳一次（見 max-win.md 常見錯誤 5）
7. **Replay / Demo 共用還原清單**：`GameRecover()` 要清的東西（EffectPlate、SpinAck、盤面、角色等級、ExtraBet）與 unshow 高度重疊；新增任何跨手持久狀態時，**兩邊都要補**
8. **框架旗標有兩個**：`commonGameManager.HasUnshow` 與 `newExtraManager.HasUnshow` 是不同的東西，都要清

## 常見錯誤

1. **❌ FG 路徑忘了清 `HasUnshow`**：`StartSpin()` 會再跑一次 `OnRecvSpinAck` → 剛重建好的畫面被整包重播蓋掉
2. **❌ MG 路徑誤清 `HasUnshow`**：`StartSpin()` 的補播不會觸發 → 那手結果完全遺失（`SetPlateInfo` 永不被呼叫，轉輪拿不到停輪資料）
3. **❌ 用 `PlateSymbol` 而非 `PlateSymbolLog` 還原**：`PlateSymbol` 是停輪當下的盤面，不含投放/收集後的結果（見下方附錄）
4. **❌ COLLECT_EX 累計值沒對半拆**：金額顯示變兩倍
5. **❌ 鎖定只設一層**：還原後中央輪照轉，或反過來不轉但每手重播 Stop 動畫
6. **❌ 新增 Feature 時沒同步補還原邏輯**：unshow 是最容易被忘記的一環——只在 QA 拔網線時才會發現，而多數人不會拔

---

## 附錄：盤面雙軌 `PlateSymbol` vs `PlateSymbolLog`

LGS 的 proto 每手同時給兩組盤面，**用錯是最高頻的一類 bug**：

| 欄位 | 語意 | 什麼時候用 |
|------|------|-----------|
| `PlateSymbol` / `PlateNum` | **停輪當下**的盤面 | `SetPlateInfo()` 餵給轉輪停輪、預告判定（`OnRecvSpinAck`）、`SpinState` 設 FG 盤面 |
| `PlateSymbolLog` / `PlateNumLog` | **本手所有演出結束後**的最終盤面（含 Pot 投放進來的符號、收集後的狀態） | 收集流程、鎖定判定、對獎（`ShowSymbolAwardLoop`）、unshow 還原、`UpdatePlate()` |

判準：**任何「投放 / 變身 / 追加」之後才成立的判斷，一律讀 Log**。

實際案例（LGS `FeatureAck_MG`）：
- `PlateSymbol[2].Col = [2, 17, 3]` — 停輪時 col2 row1 是 COLLECT，row0/row2 是一般符號
- `PlateNumLog[2].Col = [0, 1001.5, 0]` — 演出結束後 col2 row1 的收集器累計了 1001.5

停輪盤面的 `PlateNum[2]` 全是 0；只有 Log 才有收集後的金額。拿 `PlateNum` 去還原收集器 = 全部歸零。
