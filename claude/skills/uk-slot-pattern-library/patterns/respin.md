# Pattern: Respin

## 識別條件

- 特定符號組合觸發後，鎖定部分轉輪格子，僅旋轉未鎖定區域
- 重複旋轉直到無新鎖定或達到次數上限
- 可在 BaseGame 或 FreeGame 內觸發（如 FeverGameType.RespinInFreeGame）

## 參考實作

| 專案 | 核心檔案 | 說明 |
|------|----------|------|
| uk_slot_eye_strike | EnterRespinState.ts, LeaveRespinState.ts | 鎖定左右兩列 col 0,5 |
| uk_slot_eye_strike | RespinUIManager.ts | Respin 期間 UI 管理 |
| uk_746_far_west | RespinState.ts | 單一 RESPIN state，兩種類型 |
| uk_746_far_west | RespinType.ts | Thief / Super5 enum 定義 |

## State 映射

**方案 A（eye_strike 雙 state）：**
```
SPIN → ENTER_RESPIN → RESPIN_SPIN → (loop until done) → LEAVE_RESPIN → RESULT
```

**方案 B（far_west 單 state）：**
```
SPIN → RESPIN → (loop until done) → RESULT
```

## Data 需求

```typescript
interface RespinResult {
  /** 本輪 respin 的盤面結果 */
  reels: number[][];
  /** 本輪新增鎖定位置 */
  newLocked: GridPosition[];
  /** 本輪獎項 */
  wins: WinInfo[];
}

interface RespinData {
  /** respin 類型（多種變體時） */
  respinType: RespinType;
  /** 被鎖定的格子座標 */
  lockedPositions: GridPosition[];
  /** 剩餘 respin 次數（-1 = 無限直到無新鎖定） */
  respinCount: number;
  /** 每輪 respin 結果 */
  respinResults: RespinResult[];
  /** 總計獎金 */
  totalWin: number;
}

interface GridPosition {
  col: number;
  row: number;
}

enum RespinType {
  NORMAL = 0,
  THIEF = 1,    // far_west
  SUPER5 = 2,  // far_west
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 觸發動畫（符號高亮/擴展） | tween complete | spin result |
| 2 | 鎖定格子演出（lock effect + 音效） | all lock anims done | lockedPositions |
| 3 | UI 切換（顯示 respin 計數器） | immediate | RespinUIManager |
| 4 | 未鎖定列旋轉 | server response | respinResults[i] |
| 5 | 停輪 + 判定新鎖定 | reel stop callback | newLocked |
| 6 | 新鎖定演出（若有） | lock anim done | newLocked.length > 0 |
| 7 | 重複 4-6 或結束判定 | respinCount === 0 or no newLocked | — |
| 8 | 結算動畫 + 離開 respin | tween complete | totalWin |

## 常見變體

| 變體 | 鎖定方式 | 結束條件 | 代表專案 |
|------|----------|----------|----------|
| 整列鎖定 | 指定 col 全列鎖定 | 固定次數 | eye_strike |
| 單格鎖定 | 個別 GridPosition | 無新鎖定 | 常見 hold&spin |
| 多類型 | 不同觸發符號→不同 RespinType | 各自規則 | far_west |
| FG 內 Respin | FreeGame 中觸發 | 同 BaseGame | eye_strike |
| 累積式 | 每輪新鎖定重置計數 | 計數歸零 | — |
| +1 SPIN（非鎖定型） | 不鎖定格子，純追加 FG 局數 | 追加完繼續 FG 流程 | 3LP（Expand FG 中 +1 SPIN 符號） |
| 功能附帶重轉（限縮帶） | 由 Feature Wheel 觸發的單次重轉；鎖定第1/6輪+已有 CASH/Mystery，中間四輪換成只出空格+CASH 的限縮帶。非 loop，固定 1 次 | Eye Strike2 |

### +1 SPIN 子變體（3LP F03）

3LP 的 Expand FG 中，擴展行（row 0 / row 4）可能出現 +1 SPIN 符號：
- 觸發：停輪後偵測到 +1 SPIN 符號存在
- 效果：FG 剩餘次數 +1（不是重轉，是追加局數）
- 演出：+1 SPIN 符號高亮 → 數字飛入 FG 計數器 → 計數器 +1 動畫
- State：獨立 `PlusBonusSpinState`（在 CheckState 中判斷 hasPlusSpin → 進入）
- 與傳統 Respin 差異：不鎖格、不重轉當前盤面，僅追加次數後繼續下一手

## 邊界案例

1. **Respin 中斷重連**：client 重連時需從 proto 還原所有 lockedPositions + 當前 respinCount，正確顯示鎖定狀態
2. **FG 內觸發 Respin**：state machine 需正確巢狀，離開 respin 後回到 FG 流程而非 BaseGame
3. **全盤鎖定**：所有格子都鎖定時需立即結束 respin 循環，不可再發送 spin request
4. **Respin 期間 UI 互動**：bet/spin 按鈕需禁用，autoplay 計數不應在 respin 期間遞減
5. **多種 RespinType 同時觸發**：需定義優先級或合併規則，避免 state 衝突
6. **Respin 動畫中途收到下一輪結果**：需 queue 處理，確保演出完整播放後才進入下一輪

## 常見錯誤

1. **❌ FG 內觸發 Respin 後回到 MG 流程**：state machine 巢狀管理錯誤 → 離開 Respin 應回 FG 下一手而非 MG 的 IDLE
2. **❌ 全盤鎖定不終止迴圈**：所有格子已鎖時仍發 spin request → server 回空結果 → 無限空轉
3. **❌ AutoPlay 計數在 Respin 期間遞減**：Respin 的多輪不該消耗 AutoPlay 次數；減了 = AutoPlay 比預期早結束
4. **❌ lockedPositions 用 client 本地累加**：斷線重連時本地累加記錄遺失 → 鎖定狀態全錯。必須從 server 的 RecoverSpinAck 完整還原
5. **❌ 快停直接跳過 lock 動畫**：turbo 可以縮短但不能完全跳過鎖定演出（玩家需看到哪些格鎖了）；全跳會讓 UI 與邏輯狀態不同步
