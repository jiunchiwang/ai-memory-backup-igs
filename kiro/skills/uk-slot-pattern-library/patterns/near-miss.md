# Pattern: NearMiss 聽牌

## 識別條件

- Server 判定本輪結果「接近大獎但未中」，主動通知 client
- Client 在停輪階段做特殊減速/震動演出，增強緊張感
- 純表演層處理，不影響遊戲結果與獎金
- 不需要獨立 state，在 SpinState 停輪邏輯中內嵌處理

## 參考實作

| 專案 | 核心檔案 | 說明 |
|------|----------|------|
| uk_slot_eye_strike | PreWinManager.ts (9.9KB) | 完整聽牌管理，含多種 NearMissKind |
| uk_slot_eye_strike | NearMissKind.ts | enum 定義聽牌類型 |
| uk_slot_template | NearWinDetector.ts (5.7KB) | 門檻判定 NearWin_NUM=2 |

## State 映射

```
SPIN → [停輪階段內嵌 NearMiss 演出] → RESULT
```

不新增獨立 state。在 SpinState 的 reel-stop 流程中，根據 nearMiss 資料對指定列施加特殊停輪效果。

## Data 需求

```typescript
interface NearMissData {
  /** 聽牌類型 */
  nearMissType: NearMissKind;
  /** 觸發特殊演出的起始列 index */
  triggerColumn: number;
  /** 嚴重程度（影響演出強度） */
  severity: NearMissSeverity;
}

enum NearMissKind {
  NONE = 0,
  COLLECT = 1,  // 第5輪（最後一列）聽牌
  CASH = 2,     // 第1~4輪聽牌
}

enum NearMissSeverity {
  LOW = 0,    // 輕微減速
  MID = 1,    // 減速 + 震動
  HIGH = 2,   // 減速 + 強震動 + 音效升級
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 正常列依序停輪 | reel stop callback | spin result |
| 2 | triggerColumn 前一列停下後，全體轉輪加速 | tween complete | triggerColumn |
| 3 | triggerColumn 開始減速（慢停） | deceleration curve done | nearMissType |
| 4 | 震動效果啟動（依 severity） | 與減速同步 | severity |
| 5 | 音效切換（緊張音/心跳音） | immediate | nearMissType |
| 6 | 最終停輪定格 | reel fully stopped | — |
| 7 | 恢復正常流程進入 RESULT | immediate | — |

## 常見變體

| 變體 | 觸發列 | 演出特徵 | 代表 |
|------|--------|----------|------|
| COLLECT 聽牌 | col 5（最後列） | 全場聚焦最後一列，最高張力 | eye_strike, 3LP |
| CASH 聽牌 | col 1~4（中間列） | 較短演出，中等張力 | eye_strike, 3LP |
| 多符號門檻 | 已出現 N-1 個特殊符號 | 門檻數 NearWin_NUM | template |
| 漸進式 | 多列連續聽牌 | 每列加強震動幅度 | — |
| 靜默式 | 僅音效變化 | 無視覺震動，純聽覺暗示 | — |
| 大獎預告（BigWin Announcement） | 旋轉中觸發 | 非停輪差一格，而是「預告即將大獎」的全屏動畫 | 3LP F09 |

### 大獎預告子變體（3LP F09）

3LP 的 BigWin Announcement 在 SpinState 旋轉中途插入（不是停輪時），語意上是 near-miss 的擴展：
- 觸發：server 判定本手贏分達倍數門檻，或觸發 2+ 特色 FG
- 時序：轉輪旋轉中 → 收到 SpinAck → SetNowRoundInfo 判斷 → await 全屏動畫 → 播完後正常停輪
- 不可 skip：動畫播放期間轉輪持續旋轉，動畫結束才進入停輪流程

## 邊界案例

1. **快速停輪（turbo/skip）模式**：用戶點擊快停時需跳過或大幅縮短 NearMiss 演出，不可卡住流程
2. **NearMiss + 實際中獎重疊**：server 可能同時回傳 nearMiss 與 win，演出結束後需正確銜接 win 表演
3. **連續兩輪 NearMiss**：不應讓玩家感覺「被騙」，頻率由 server 控制但 client 需能正常連續播放
4. **斷線重連時正在播放 NearMiss**：重連後不重播聽牌演出，直接顯示最終盤面
5. **AutoPlay 期間觸發**：仍需播放完整演出（不可跳過），但不阻塞下一輪 auto spin 啟動超過合理時間
6. **多列同時 NearMiss**：需定義優先級，通常取最後一列（張力最高）為主演出列
7. **大獎預告 + NearMiss 同手（3LP）**：BigWin Announcement 在旋轉中播完後才進停輪流程，若停輪又有 NearMiss 需正確串接（先預告→再聽牌停輪）

## 常見錯誤

1. **❌ 快停模式完全跳過 NearMiss**：turbo 應縮短演出（如 0.1s 減速）但不能完全跳過 → 否則玩家無法感知「差一點」的體驗，規格通常要求最低限度呈現
2. **❌ Client 自行判斷 NearMiss 條件**：NearMiss 是 server 主動通知，client 不該用本地算「差幾個符號」來自行觸發 → 跟 server 結果不同步
3. **❌ NearMiss 演出阻塞 AutoPlay**：演出完成後應立即恢復流程；若 await 寫在不對的 layer → autoPlay 的 interval timer 被卡住
4. **❌ 大獎預告和 NearMiss 動畫互搶 spine track**：兩者共用同一 spine 時序 → 先播預告再播停輪減速需確保 track 不衝突
5. **❌ 連續兩手都 NearMiss 不做頻率控制**：server 通常會控頻率，但 client 若有本地 cooldown 保護沒加 → 連續觸發體驗差（像在騙玩家）
