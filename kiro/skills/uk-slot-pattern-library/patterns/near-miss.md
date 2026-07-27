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
| 預告 + 先揭曉關鍵符號（Omen） | 收 ack 當下 | 全屏預告動畫 → **收集符號先落定** → 其餘輪走長 NearWin | LGS |
| 堆疊連線假轉（LineOmen） | 停輪過程 | 非大獎預告，是「讓某符號在旋轉中看起來一直堆疊」的機率性假轉 | LGS |

### 預告子變體：Omen（LGS）

與 3LP 的 BigWin Announcement 同族，但**先揭曉一部分結果再拉長剩下的期待**：

| Step | 動作 |
|------|------|
| 1 | `OnRecvSpinAck` 收到完整結果，判定是否 Omen |
| 2 | `await OmenSpine.Play()` 全屏預告動畫 + `Omen_Start` 音效 |
| 3 | 中央輪的 COLLECT 逐 row **直接播停輪特效落定**（`ReelStopEffect` + `Collect_Stop`） |
| 4 | `SetPlateInfo(plate, plateNum, isOmen=true)`：其餘 1/2/4/5 輪切成 NearWin 模式（3 秒慢停、多轉 5 圈、換 `NEARWIN_SPIN_ORDER` 停輪順序） |
| 5 | 假轉符號權重也跟著換（`GetRandomSymbol(col, isNearWin, isOmen)` 提高特殊符號出現率） |

**觸發條件（LGS 實作，client 端從完整 ack 推導）**：

> 🔒 下段含專案調校數值（倍率門檻、觸發機率）。此庫若要外流出 corp 範圍，這裡是第一個該抽換成佔位符的地方。

```typescript
// 條件一：進 BG 且盤面夠豐富        條件二：收分夠大
if ( isBonus && hasBonusSymbol && collectCount > 0 && cashCount >= 4 ||
     isCollect && ( collectCount >= 2 && totalRate >= 15 || totalRate >= 30 ) )
{
    // 30 倍以上 100% 觸發，其餘擲 50%
    if ( Define.HAS_REPLAY || totalRate >= 30 || Math.random() < 0.5 ) {
        isOmen = true;
        await this.ShowOmen( plate );
    }
}
```

> ⚠️ **這不牴觸「client 不該自行判斷 NearMiss」**：client 是拿**已到手的完整結果 ack** 反推該不該演，不是猜結果。分界在於——用 `SpinAck` 全量資料決定演出強度 = 可以；用「目前停了幾輪、差幾個符號」即時推算 = 不行（會與 server 結果不同步）。但 `Math.random()` 這種**純 client 隨機的演出分歧**會讓同一手在 replay 時表現不一致，LGS 用 `Define.HAS_REPLAY` 強制為 true 來繞開。

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
8. **預告手要禁用快停（LGS）**：`if (m_isHardStop && !isOmen)` ——預告已經是「保證好事」的演出，讓玩家切停會把鋪陳砍掉。turbo 旗標本身不清除，只是這一手不套用
9. **預告與其他假轉演出互斥**：LGS 在 `isOmen` 為真時**不做**堆疊連線假轉（`SetLineOmen`）；兩種假轉同時作用會互搶符號權重
10. **client 端隨機造成 replay 不一致**：`Math.random() < 0.5` 的演出分歧在復盤時會變成另一種表現。LGS 用 `Define.HAS_REPLAY` 短路成必定觸發；任何 client 隨機的演出分歧都要想好 replay 怎麼辦
11. **預告動畫是 `await`，期間不可收下一手**：`OnRecvSpinAck` 內 `await ShowOmen()` 會拖住整個 ack 處理；此時若 autoplay 又送出 spin request，狀態機會錯亂

## 常見錯誤

1. **❌ 快停模式完全跳過 NearMiss**：turbo 應縮短演出（如 0.1s 減速）但不能完全跳過 → 否則玩家無法感知「差一點」的體驗，規格通常要求最低限度呈現
2. **❌ Client 自行判斷 NearMiss 條件**：NearMiss 是 server 主動通知，client 不該用本地算「差幾個符號」來自行觸發 → 跟 server 結果不同步
3. **❌ NearMiss 演出阻塞 AutoPlay**：演出完成後應立即恢復流程；若 await 寫在不對的 layer → autoPlay 的 interval timer 被卡住
4. **❌ 大獎預告和 NearMiss 動畫互搶 spine track**：兩者共用同一 spine 時序 → 先播預告再播停輪減速需確保 track 不衝突
5. **❌ 連續兩手都 NearMiss 不做頻率控制**：server 通常會控頻率，但 client 若有本地 cooldown 保護沒加 → 連續觸發體驗差（像在騙玩家）
