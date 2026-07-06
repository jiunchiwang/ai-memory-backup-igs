# Pattern: BonusGame Pick

## 識別條件

- 特定條件觸發後進入完全獨立的 Bonus 場景（非主轉輪疊層）
- 玩家主動選擇（pick）決定獎勵
- 可能有多 stage 遞進（如 robinhood 的弓箭 → 錢袋）
- 獨立 UI/場景，與主遊戲畫面切換
- 結算後回到主遊戲

## 參考實作

| 專案 | 核心檔案 | 大小 | 說明 |
|------|----------|------|------|
| uk_722_robinhood | `BonusGameControll` | 99KB | 主控制器，管理整體 Bonus 流程 |
| uk_722_robinhood | `PurseManager` + `PurseItem` | — | 錢袋 pick 選擇邏輯 |
| uk_722_robinhood | `WinBoardManager` | — | Bonus 中獎金累計顯示 |
| uk_722_robinhood | `ArcheryCtrl` | — | 弓箭射擊 stage |
| uk_746_far_west | `BonusGameController` | — | 多 stage 射擊小遊戲 |
| uk_746_far_west | `CowboyController` | — | 射擊互動邏輯 |

## State 映射

需新增 3 個 State + CheckState 路由：

```
CheckState ──(hasBonusTrigger)──→ ENTER_BONUS
                                       ↓
                                  BONUS_GAME（玩家互動迴圈）
                                       ↓
                                  LEAVE_BONUS → NormalSpinState
```

| State | 職責 |
|-------|------|
| `ENTER_BONUS` | 宣告面板、轉場動畫、載入 Bonus 場景資源 |
| `BONUS_GAME` | 玩家 pick 互動、多 stage 遞進、獎勵揭示 |
| `LEAVE_BONUS` | 結算面板、銷毀 Bonus 場景、轉場回主遊戲 |

CheckState 新增路由：
```typescript
if (data.bonusGame) {
  this.changeState('ENTER_BONUS');
  return;
}
```

## Data 需求（proto 假設）

```typescript
interface BonusGameData {
  /** Bonus 觸發資訊 */
  trigger: BonusTrigger;
  /** 可選擇項目（server 預決定結果，client 只負責揭示） */
  picks: BonusPick[];
  /** 多 stage 時的階段資訊 */
  stages: BonusStage[];
  /** 最終總獎金 */
  totalWin: number;
}

interface BonusTrigger {
  /** 觸發條件（如 3 個 Scatter） */
  triggerSymbols: { col: number; row: number }[];
  /** Bonus 類型標識 */
  bonusType: string;
}

interface BonusPick {
  /** pick 索引 */
  index: number;
  /** 該選項的獎勵（玩家選擇前 client 不知道） */
  reward: number | 'next_stage' | 'end';
  /** 是否為玩家選中的 */
  selected: boolean;
}

interface BonusStage {
  /** 階段編號 */
  stageIndex: number;
  /** 該階段的 picks */
  picks: BonusPick[];
  /** 該階段累計獎金 */
  stageWin: number;
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | Bonus 觸發宣告面板（恭喜進入 Bonus） | 玩家點擊/timer | triggerSymbols 演出完 |
| 2 | 轉場動畫（主場景淡出/Bonus 場景載入） | 場景 load + transition 完成 | ENTER_BONUS state |
| 3 | Bonus 場景就緒，顯示可選項目 | UI ready callback | 資源載入完成 |
| 4 | 等待玩家點擊選擇 | user input event | — |
| 5 | 揭示獎勵動畫（開獎） | tween 完成 | picks[selected] |
| 6 | 累計獎金更新 | counter tween 完成 | stageWin |
| 7 | 判斷是否進入下一 stage 或結束 | 邏輯判斷 | reward 類型 |
| 8 | （若多 stage）stage 轉場 → 回到 Step 3 | transition 完成 | next_stage |
| 9 | 結算面板（顯示 totalWin） | 玩家點擊/timer | 所有 stage 完成 |
| 10 | 轉場回主遊戲 | transition 完成 | LEAVE_BONUS state |

## 常見變體

| 變體 | 差異 | 範例 |
|------|------|------|
| 單次 Pick | 選一次即結算 | 簡易 Bonus |
| 多 Stage 遞進 | 每 stage 獎勵遞增，可能提前結束 | robinhood 弓箭+錢袋 |
| 射擊/技巧型 | 玩家操作影響結果呈現（實際 server 預決定） | far_west 射擊 |
| Wheel Pick | 轉盤代替直接選擇 | Bonus Wheel |
| 地圖探索 | 選路徑前進，遇怪結束 | Adventure Bonus |
| 累積 Pick | 選到特定 symbol 前可一直選 | Collect-until-end |

## 邊界案例

1. **玩家長時間不操作**：需要 auto-pick timeout（通常 30s），server 已預決定結果所以可自動揭示
2. **斷線重連在 Bonus 中途**：server 下發已揭示的 picks + 剩餘未選項，client 重建中間狀態
3. **Replay/Unshow**：整個 Bonus 結果作為一包還原，不需逐 pick 回退，直接跳到 Bonus 開始前或結束後
4. **Bonus 中觸發另一個 Bonus**：nested bonus 需 stack 管理（罕見但存在），或規格禁止巢狀
5. **stage 數量為 0**：trigger 後 server 回傳空 stages，需 graceful 直接進結算不 crash
6. **Bonus 場景資源載入失敗**：需 fallback 機制（顯示簡化版或重試），不能卡在 ENTER_BONUS 死循環

## 常見錯誤

1. **❌ Client 自行決定 pick 結果**：Bonus 結果 100% server 預決定，client 只負責揭示動畫——自行隨機會跟 server 結算不匹配
2. **❌ 忘記 auto-pick timeout**：玩家 30s 不操作時需自動揭示 server 指定的選項；沒做 = 卡死（伺服器等 client 回報、client 等玩家點擊，永久死鎖）
3. **❌ 轉場不銷毀 Bonus 場景**：LEAVE_BONUS 忘記 destroyScene → 記憶體洩漏 + 下次進 Bonus 場景疊加
4. **❌ 斷線重連不重建中間狀態**：重連在 Bonus 中途需讀 server 回傳的已揭示 picks 重繪畫面；不處理 = 白屏
5. **❌ 多 stage 間共用 stageWin 變數**：每 stage 的累計獎金是獨立的，共用變數會導致 stage 間金額互相污染
