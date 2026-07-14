# Pattern: Collect Feature

## 識別條件

規格書出現以下描述時匹配：
- 「收集符號」「COLLECT」出現在特定輪（通常第5輪或最後一輪）
- 「CASH 符號帶數字/獎金值」出現在其他輪
- 「COLLECT 收集盤面上所有 CASH 的獎金值」
- 「JP 符號被收集時先轉換成分數」

## 參考實作

| 專案 | 複雜度 | 特殊點 |
|------|--------|--------|
| uk_slot_eye_strike | 高 | Collect 收 Cash/JP，搭配 MagicPot 能量等級(0~3) 與 Multiplier（**無** Basic/Boost/Multi/Chain 分級——已對程式碼覆驗，eye_strike 不存在此 4 型，勿誤植） |
| uk_739_wrath_of_thunder | 高 | 4 種 Collect（Basic/Boost/Multi/Chain），分裂 CASH（2顆/3顆）——**4 型升級唯一來源** |
| tripleCoinTreasure | 中 | FG 單格 Respin 收集 |

### 核心檔案（eye_strike）
- `GameView.ts` → OnRecvSpinAck 解析 CollectResult
- `GameState/FeatureShowState.ts` 或自建 `CollectFeatureState.ts`
- `EffectPlate.ts` → 收分飛行動畫
- `FlyManager.ts` → CASH 飛向 COLLECT 的飛行路徑

## State 映射

**基本型**：不新增 State，走 `FeatureShowState`
- CheckState 判斷 `hasCollect && hasCash` → FeatureShowState
- FeatureShowState 內部跑完收分演出後 → 下一個 State

**複雜型**（建議）：獨立 `CollectFeatureState`
- 職責更清晰，避免 FeatureShowState 過度膨脹
- 繼承 BaseState，OnEnter 為 async

## Data 需求

```typescript
// proto 假設結構
interface CollectResult {
    collectPositions: { col: number, row: number }[];     // COLLECT 符號位置
    cashPositions: { col: number, row: number, value: number, cashType: CashType }[];  // CASH 位置+面值
    jpPositions: { col: number, row: number, jpLevel: JPType, jpValue: number }[];     // JP 位置+等級+值
    totalWin: number;  // 本次 Collect 總贏分
}

enum CashType { Bronze, Silver, Gold }
enum JPType { Mini, Minor, Major, Mega, Grand }
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 壓暗非 CASH/COLLECT 符號 | 即時 | Game_Define.Color.Dark |
| 2 | 第 1 個 COLLECT 開始收分 | — | — |
| 2a | 帶分數 CASH 逐顆飛向 COLLECT（上→下、左→右） | await FlyManager / tween | spine: CashFly |
| 2b | 已收集 CASH 壓暗 | 即時 | — |
| 2c | JP 符號轉換分數顯示 | await tween(0.3s) | NumberAnimation |
| 2d | JP 飛向 COLLECT | await FlyManager | — |
| 3 | 若有第 2 個 COLLECT → 重複 2a~2d | await | — |
| 4 | 所有收集完成，JP 轉回文案 | 即時 | — |
| 5 | 還原壓暗 | 即時 | — |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 單 COLLECT vs 複數 COLLECT | 複數排隊收，每個各收一次 | eye_strike, 3LP |
| 升級版 Collect（Boost/Multi/Chain） | 累積 N 個 COLLECT 解鎖進階效果 | wrath_of_thunder |
| 搭配 Multiplier | 收分前先乘倍 | eye_strike, 3LP |
| 搭配 Bomb | 炸彈先作用再收 | 3LP Clover Bomb |
| CASH 分裂 | 一顆 CASH 分裂成 2~3 顆 | wrath_of_thunder |
| CASH 升級 | 乘倍後金額達閾值 → 外觀升級（銅→銀→金） | 3LP |
| 搭配神秘事件 | 停輪後第5輪逐格重轉追加更多 COLLECT，再執行收分 | 3LP（見 collect-mystery.md） |
| 5 級 JP | Mini/Minor/Major/Mega/Grand，一律轉分數收分（GRAND/MEGA 獨立報獎面板曾在早期規格出現，**6/23 修訂整個移除**——2026-07-07 檢查點 2 確認） | 3LP |
| 雙向 Collect（第1+6輪） | COLLECT 分佈在盤面兩端（第1輪+第6輪），各自獨立收分；飛入方向相反（左→右 vs 右→左），FlyManager 需方向參數 | Eye Strike2 |
| Burst（注入保證收分） | 第1+6輪皆 Collect 但中間 2-5 輪無 Cash 時，跳宣告→隨機注入數顆 Cash 到 2-5 輪→觸發 Collect 收分（保證該手有收分）；MG/FG 皆可 | Wrath of Thunder v2 |
| 單輪收集器 → 特殊 Collect | Super FG 中未收 Cash 飛入該輪下方收集器，每集滿 3 顆變成「只收該輪」的特殊 Collect，下一手生效後重置 | Wrath of Thunder v2 |
| 升級版解鎖門檻 | Boost/Multi/Chain 等型需累積 Collect 數依序解鎖（解鎖層見 progression-unlock.md） | wrath_of_thunder |

## 邊界案例

1. **收分順序**：帶分數 CASH 先收 → JP 後收（JP 需先轉分數）
2. **最高階 JP 是否有獨立報獎面板要對規格修訂記錄**：3LP 早期規格有 GRAND/MEGA 獨立面板、6/23 修訂移除（所有 JP 一律轉分數收分）——實作前確認拿到的是最新版規格，別照舊版做出多餘分支
3. **複數 COLLECT 排隊**：第 1 個收完才換第 2 個，順序為上→下
4. **Multiplier 交互**：作用順序 Bomb → Multiplier → Collect
5. **FG 回 MG 時**：Collect 狀態不需要 reset（它是一次性觸發）
6. **神秘事件交互**：神秘事件可能在 Collect 前追加更多 COLLECT（先做神秘再做收分）
7. **JP 文案還原時機**：所有 COLLECT 收完後 JP 符號才從分數文案還原回 JP 名稱（3LP 規格明確要求）
8. **Burst 與一般 Collect 的觸發互斥/優先序**：Burst 是「兩端 Collect + 中間無 Cash」的特例分支，需先判 Burst 再走一般收分，別讓「無 Cash 不觸發」把 Burst 也擋掉（Wrath of Thunder v2）
9. **升級型 Collect 的加成順序**：Boost（加 Cash/分數）→ Multi（乘倍）→ Chain（注入再收）各自有作用時機，且 Chain 符號可再被 Boost/Multi 加成；多型同手需定義固定順序（Wrath of Thunder v2）

## 常見錯誤

1. **❌ 把 Boost/Multi/Chain 四型誤植到 eye_strike**：eye_strike 不存在此 4 型分級（已覆驗），四型唯一來源是 wrath_of_thunder——混用會導致分支邏輯永遠走不到
2. **❌ Collect 收分順序搞反**：正確順序 CASH 先 → JP 後（JP 需先轉分數再飛）；反過來會導致 JP 動畫跟 CASH 動畫重疊
3. **❌ 忽略 Multiplier 作用時機**：Bomb → Multiplier → Collect 是固定順序；在 Multiplier 之前就收分 = 少算倍率
4. **❌ 複數 COLLECT 不排隊**：多個 COLLECT 必須逐一收完再換下一個（上→下）；並行會導致飛行目標錯誤 + 分數累加錯
5. **❌ FG 結束後沒清 Collect 暫存**：Collect 是一次性觸發不需 reset，但如果把 collectPositions 存在 Manager 而非 State 局部 → 下次 FG 可能髒讀
