# Pattern: Bomb 爆炸

## 識別條件

- 盤面出現 Bomb symbol，停輪後觸發爆炸
- 爆炸範圍可為 8 方向 / 4 方向（chachacha：紅炸彈 8 向、黑炸彈 4 向）或垂直整輪（3LP Clover Bomb）
- 爆炸路徑產出 CASH symbol 或升級已有 CASH 金額
- 受影響格由 **server 指定**（如 chachacha 的 `change_pos`），client 不自算相鄰格
- 同輪複數炸彈：演出可逐顆依序 **或並行**（chachacha 為 `Promise.all` 並行播放，非依序迴圈）
- 作用順序 Bomb → Multiplier → Collect **僅適用同時具三者的遊戲**（3LP / eye_strike 系）；chachacha 只有 Bomb → ChangeSymbol（無 Multiplier/Collect）
- cascade chain（產出新炸彈）由 **server 決定並回傳**，client 照資料播放，**非 client 自行迴圈遞迴**

## 參考實作

| 專案 | 核心檔案 | 大小 | 說明 |
|------|----------|------|------|
| uk_slot_chachacha | `CrossFeverController.ts` | 48KB | 炸彈特色主控 |
| uk_slot_chachacha | `FeatureBomb.ts` | ~22.5KB | 單顆炸彈生命週期（爆炸→ChangeSymbol） |
| 3LP 規格 | Clover Bomb | — | 垂直方向（上下整輪），產出/升級 CASH |
| uk_slot_eye_strike | `MagicPot` | — | 間接相關：能量蒐集機制 |

> ⚠️ **chachacha 實裝校準（已對程式碼覆驗）**：① 紅炸彈 8 向、黑炸彈僅 4 向，範圍由 server `change_pos` 給；② `FeatureBomb.PlayBombEffectByData()` 對 server `BombInfo[]` 以 `Promise.all` **並行**播放，**無 cascade 偵測/遞迴迴圈**——「鏈式產出新炸彈」是 server 資料層概念，非 client 邏輯；③ chachacha **無 Multiplier/Collect**，作用僅 Bomb→ChangeSymbol。下方「演出時序」的逐顆迴圈與「進入 Multiplier 階段」僅適用具該流程的遊戲。

## State 映射

**chachacha 模式**：不加額外 State，走 Feature 機制內嵌處理

```
NormalSpinState → FeatureShowState（Bomb 演出）→ 後續流程
```

**3LP 模式**：可能需要獨立 State

```
NormalSpinState → BombFeatureState → FeatureShowState → CollectState
```

CheckState 需新增判斷：`hasBomb ? goto BombFeatureState : skip`

## Data 需求（proto 假設）

```typescript
interface BombFeatureData {
  /** 本輪所有炸彈位置（按作用順序排列） */
  bombPositions: { col: number; row: number }[];
  /** 每顆炸彈作用後的結果 */
  bombResults: BombResult[];
}

interface BombResult {
  /** 對應 bombPositions 的 index */
  bombIndex: number;
  /** 爆炸影響的格子 */
  affectedCells: AffectedCell[];
}

interface AffectedCell {
  position: { col: number; row: number };
  /** 該格發生的變化 */
  action: 'new_cash' | 'upgrade_cash' | 'destroy';
  /** new_cash/upgrade_cash 時的金額 */
  cashValue?: number;
  /** upgrade 時的原金額（用於演出差異） */
  previousValue?: number;
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 轉輪停止，辨識炸彈位置 | reel stop callback | NormalSpinState 完成 |
| 2 | 第 1 顆炸彈發光（highlight） | tween 完成 (≈0.5s) | bombPositions[0] |
| 3 | 爆炸範圍覆蓋特效（8方向/垂直整輪） | 特效 animation 完成 | 爆炸類型設定 |
| 4 | 特效消失，受影響格 CASH 出現/升級動畫 | tween 完成 | bombResults[0].affectedCells |
| 5 | 若有下一顆未作用炸彈 → 回到 Step 2 | 迴圈判斷 | bombPositions.length |
| 6 | 全部炸彈作用完畢，進入 Multiplier 階段 | event emit | 所有 bombResults 處理完 |

## 常見變體

| 變體 | 差異 | 範例 |
|------|------|------|
| 8 方向爆炸 | 以炸彈為中心 8 格（chachacha 紅炸彈；黑炸彈為 4 向） | chachacha CrossFever |
| 垂直整輪 | 以炸彈為中心上下整列 | 3LP Clover Bomb |
| 十字爆炸 | 上下左右 4 方向延伸（chachacha 黑炸彈即此型） | chachacha 黑炸彈 / 常見變體 |
| Cascade chain | 「產出新炸彈→繼續爆」由 server 回傳分批資料表達；chachacha client 對 server 給的 `BombInfo[]` 並行播放，**非 client 遞迴** | chachacha（server 驅動） |
| 範圍隨等級擴大 | 連續觸發時爆炸半徑 +1 | 進階設計 |
| 定向爆炸 | 只往特定方向（如向下） | 特殊主題機台 |
| 小妖精投擲（BombEvent） | 非盤面自然轉出，由角色動畫投入 1~3 顆 | 3LP（F06，見下方說明） |
| 條件限制 | 有 COLLECT 才作用，無 COLLECT 時炸彈不爆 | 3LP（Clover Bomb 規格） |

### BombEvent 子變體（3LP F06）

3LP 的 Clover Bomb FG 中，除了盤面自然轉出炸彈（F05），還有「小妖精投擲」事件（F06）：
- 時機：spinning 中或停輪後（server 決定）
- 數量：1~3 顆（位置由 server 指定）
- 互斥：停輪後觸發時跳過神秘事件（F07）
- 保證贏分：觸發後該手必定有贏分
- 後續：加完炸彈後走正常 F05 炸彈作用流程

## 邊界案例

1. **兩顆炸彈爆炸範圍重疊**：同一格被兩次影響時，CASH 是累加還是取較高值（3LP 規格：升級金額）
2. **炸彈炸到另一顆炸彈**：是否觸發 cascade 由 server 決定（chachacha 的鏈式結果由 server 回傳，client 不自行判定「炸到炸彈→再爆」）；client 端只負責照資料播放
3. **炸彈位置本身已有 CASH**：先收走 CASH 再爆，還是直接升級該 CASH
4. **爆炸範圍超出盤面邊界**：邊緣/角落炸彈的有效格數少於完整範圍，不應 index out of bounds
5. **Replay/Unshow 還原**：需逐顆逆序還原，升級的 CASH 回退到 previousValue，新產出的 CASH 移除
6. **斷線重連在炸彈演出中途**：server 下發最終態，client 需能跳過動畫直接呈現結果盤面
7. **無 COLLECT 時炸彈不作用（3LP）**：盤面無 COLLECT 符號時即使有 Bomb 也不爆，需前置條件判斷
8. **BombEvent 投擲 + 盤面自有 Bomb 同手（3LP）**：投擲加入的 + 自然轉出的合併，統一按 order 逐顆作用

## 常見錯誤

1. **❌ Client 自己判「炸到另一顆炸彈→cascade」**：cascade 是 server 資料層概念，chachacha 的 client 對 BombInfo[] 並行播放，不做本地遞迴——自己寫遞迴會跟 server 結果不一致
2. **❌ 把 chachacha 的並行播放邏輯套到有序 Bomb（3LP）上**：chachacha 用 Promise.all 並行；3LP Clover Bomb 需逐顆依序（先爆完一顆才爆下顆）。照搬會導致演出順序混亂
3. **❌ 忽略 Bomb 觸發前置條件**：3LP 的 Clover Bomb 規格要求「盤面有 COLLECT 才作用」，無 COLLECT 時不爆——忘了前置檢查 = 無效爆炸（server 不回 bombResults 但 client 自行觸發動畫）
4. **❌ 爆炸範圍超出盤面不做 clamp**：邊緣/角落炸彈的有效格少於完整 8 向，不 clamp 會 index out of bounds crash
5. **❌ Unshow 逆序邏輯忘記升級的 previousValue**：還原時升級 CASH 要回退到 previousValue，新產出的要移除——順序也要逆序（最後一顆先還原）
