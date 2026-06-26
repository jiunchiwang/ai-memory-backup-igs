# Pattern: VS Feature（對決乘倍）

## 識別條件

規格書出現以下描述時匹配：
- 「VS」「對決」「兩端不同倍數」「對決動畫隨機決定勝出倍數」
- 有 `VS` / `VS Cash` / `VS Collect` 之類「帶兩端倍數」的符號（符號美術常為左右兩色對峙，如紅 vs 綠）
- 「收分時 CASH 金額乘上勝出倍數」
- 「VS 符號擴展至該輪滿盤」後才作用
- 競品語意：Hacksaw「Eternal Duel」式對決乘倍

與其他乘倍類 pattern 的差異（重要，別混）：
- vs `multiplier-grid.md`：Multiplier 是格子標記倍率（單值、跨 spin 累加）；VS 是**單顆符號帶「兩端」候選倍率，靠對決演出隨機選出勝方**，非累加。
- vs `symbol-transform.md`：Symbol Transform 改的是符號身份（一般→CASH）；VS 不改符號身份，只決定並施加倍數。
- vs `persistent-grid-effect.md`：VS 倍率是**單手作用**（停留在當手 VS 符號上、收分時用），非跨 spin 常駐。

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| Clash of Olympus（規格） | VS Feature | 三種 VS 符號（VS / VS Cash / VS Collect），Cash 型乘該輪、Collect 型乘全盤 |
| Hacksaw Eternal Duel（競品） | 對決乘倍 | 兩端倍數對峙、隨機決定勝出 |

### 核心檔案（Clash of Olympus，規劃中）
- `GameState/VSFeatureState.ts` — 對決演出主 State（在 Collect Feature 之前作用）
- `Feature/VSManager.ts` — 兩端倍數對決邏輯、勝方判定、倍率施加範圍（該輪 vs 全盤）
- `GameView.ts` → 解析 VS 結果（位置、兩端倍率、勝方、作用對象）

## State 映射

**獨立 State**：`VSFeatureState`，作用時機在「對線獎之後、Collect Feature 之前」。

```
CheckState（hasVS && 同輪有 Collect/Cash/JP）→ VSFeatureState → CollectFeatureState → Award
```

多 VS 作用順序（規格明定，1-6 輪都有 VS 時）：
```
1. 先做 Cash 的 VS：由左而右，自第 2 輪開始
2. 再做 Collect 的 VS：由左而右，自第 1 輪開始
3. VS Collect 的勝出倍率作用在盤面所有 Cash/JP 分數上
4. 進 Collect Feature 收分（CASH 先、再 COLLECT）
```

## Data 需求

```typescript
interface VSFeatureData {
  /** 本手所有 VS 符號 */
  vsResults: VSResult[];
  /** 作用總順序（server 排好或 client 依規則排） */
  executionOrder: number[];
}

interface VSResult {
  position: { col: number; row: number };
  /** VS 類型：影響倍率作用範圍 */
  vsType: VSType;
  /** 兩端候選倍率（對決前顯示兩個值） */
  candidateMultipliers: [number, number];
  /** 勝出的那一端（server 預決定） */
  winningMultiplier: number;
  /** 該 VS 作用的目標位置（Cash 型=該輪；Collect 型=全盤 Cash/JP） */
  appliedPositions: { col: number; row: number }[];
}

enum VSType {
  VS        = 0, // 一般 VS（任意輪），為同輪 Collect/Cash 增加倍數
  VSCash    = 1, // VS Cash（限第1/6輪）：乘該輪 Cash
  VSCollect = 2, // VS Collect（限第1/6輪）：勝出倍率打到全盤所有 Cash/JP
}
```

> ⚠️ 倍率語意 `2X` vs `X2` 規格標記待確認（規格 [S44] 留問）；實作前向企劃確認是「加 2 倍」還是「乘 2」。

## 演出時序

### Cash 型 VS（規格 STEP1~9）

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | SPIN 後停輪；該輪同時有 Cash/JP 與 VS（第1/6輪有 Collect） | — | 觸發條件成立才演 |
| 2 | 對線獎 | await | — |
| 3 | 該輪 Cash 符號往 VS 符號飛去並加總 | await fly | FlyManager |
| 4 | VS 符號擴展至該輪滿盤 | await tween | — |
| 5 | 對決演出，決定勝出倍數 | await spine（對決動畫） | winningMultiplier |
| 6 | VS 維持擴展，勝出倍數停留在 VS Cash 上 | 即時 | — |
| 7 | Cash Collect 蒐集盤面所有 Cash/JP（收分=乘倍後分數） | await | CollectFeature |
| 8 | 結算分數 | await count | — |

### Collect 型 VS（規格 STEP1~9）

| Step | 動作 | 等待方式 |
|------|------|---------|
| 1 | 停輪；第1/6輪同輪同時有 Collect 與 VS，中間輪有 Cash/JP | — |
| 2 | 對線獎 | await |
| 3 | Collect 往 VS 飛去 → VS Collect 擴展至該輪滿盤 | await tween |
| 4 | 對決演出決定勝出倍數 | await spine |
| 5 | 勝出倍數打到盤面所有 Cash/JP 上 | await | 
| 6 | VS Collect 蒐集盤面所有 Cash/JP 獎金值 | await |
| 7 | 結算分數 | await count |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| VS Cash（乘該輪） | 倍率只作用觸發 VS 的那一輪 Cash | Clash of Olympus |
| VS Collect（乘全盤） | 勝出倍率作用到盤面所有 Cash/JP | Clash of Olympus |
| 一般 VS（同輪加成） | 為同一輪的 Collect 或 Cash 增加倍數 | Clash of Olympus |
| 兩端來源不同主題 | 兩端對應主題角色（如宙斯/黑帝斯、紅/藍寶藏），勝方換不同美術 | Clash of Olympus（VS COLLECT 需製作對決/黑帝斯/宙斯 3 種） |
| 對決交互式 vs 純演出 | 結果 server 預決定，client 只播動畫（玩家不可操作） | Clash of Olympus |

## 邊界案例

1. **觸發條件嚴格**：只有「同輪同時存在 VS + Collect/Cash/JP」才演 VS；條件不成立則不演（規格明定「若上述情況沒有發生，不演出 VS Feature」）
2. **1-6 輪都有 VS 的順序**：Cash VS（左→右自第2輪）→ Collect VS（左→右自第1輪）→ VS Collect 乘全盤 → 才進 Collect 收分；順序錯會導致乘倍對象/金額錯
3. **CASH 先、COLLECT 後**：VS 流程結束後，收分一律 CASH 先再 COLLECT（規格 [L60] 明示）
4. **每輪最多 1 個 VS**：每次停輪每條輪帶最多出現 1 個 VS 符號
5. **倍率作用範圍不可混**：VS Cash 只乘該輪、VS Collect 乘全盤——實作別把範圍搞錯
6. **與 JP 交互**：JP 先轉分數 → 套用 VS 勝出倍率 → 再被 Collect 收走（順序同 multiplier-grid 的 JP 規則）
7. **斷線重連**：直接顯示勝出結果（VS 已擴展、倍率已定），不重播對決動畫
8. **Unshow/Replay 還原**：需還原到對決前狀態（移除擴展、清除勝出倍率），勝方為 server 資料不可本地重抽
9. **與 MAX WIN 交互**：VS 乘倍後若觸發 MAX WIN 上限，依 `max-win.md` 處理（報獎只給差值）

## 常見錯誤

1. **❌ 條件不成立也演 VS**：只有「同輪同時存在 VS + Collect/Cash/JP」才演；條件不成立時 VS 是普通符號——忘了 guard = 浪費 2s 播空動畫
2. **❌ VS Cash 和 VS Collect 作用範圍搞反**：Cash 型只乘該輪、Collect 型乘全盤——搞反 = 金額差距巨大
3. **❌ 多 VS 順序不對**：1-6 輪都有 VS 時固定順序是 Cash VS（左→右自第2輪）→ Collect VS（左→右自第1輪）；亂序 = 乘倍基數錯
4. **❌ 對決結果用 client 隨機**：winningMultiplier 由 server 預決定，client 只播動畫；本地隨機 = 跟 server 結算不匹配
5. **❌ Unshow 重播對決動畫**：Unshow 還原應移除擴展 + 清除勝出倍率，直接呈現對決前狀態——重播動畫浪費時間且可能因 spine 狀態殘留出錯
