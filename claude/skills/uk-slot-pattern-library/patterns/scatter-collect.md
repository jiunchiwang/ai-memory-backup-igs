# Pattern: Scatter 蒐集觸發

## 識別條件

規格書出現以下描述時匹配：
- 「Scatter 收集/蒐集到盆子/容器」
- 「累積 N 個 Scatter 觸發免費遊戲」
- 「盆子/容器有成長階段」
- 「多種顏色 Scatter 對應不同 FG 特色」

## 參考實作

| 專案 | 機制名 | 特殊點 |
|------|--------|--------|
| uk_slot_eye_strike | MagicPot | 單一盆子，server 6級→client 4級，影響 FG 獎勵 |
| tripleCoinTreasure | 三色 Scatter | Tiger/Loong/Koi 三種，組合觸發 |
| 3 Leprechaun's Pots（規格） | 三蒐集盆子 | 3色+1彩色，4階段成長，7種FG組合 |

### 核心檔案（eye_strike）
- `MagicPot/MagicPotController.ts`（47.6KB）— 盆子狀態管理、升級邏輯、動畫控制
- `GameState/ScatterShowState.ts` — Scatter 飛入盆子的演出
- `GameView.ts` → MagicPot 事件監聽

## State 映射

**使用現有 State**：`ScatterShowState`
- ScatterShowState 負責 Scatter 飛入盆子的演出
- 盆子成長/觸發判定通常在 ScatterShowState 結束後、CheckState 之前

**額外需要**：獨立 Manager（如 `ScatterCollectManager` 或 `PotManager`）
- 管理盆子當前階段（跨 spin 持久狀態）
- 判斷是否觸發 FG
- 控制成長/觸發成功/觸發失敗動畫

## Data 需求

```typescript
interface ScatterResult {
    scatterType: ScatterColor;        // 哪種顏色
    position: { col: number, row: number };  // 出現位置
    potStage: number;                 // 收集後盆子階段（server 算好）
    triggered: boolean;               // 是否觸發 FG
    fgFeatures?: FGFeatureType[];     // 觸發了哪些特色
}

enum ScatterColor { Blue, Green, Red, Super }
enum FGFeatureType { Expand, Multiplier, CloverBomb }
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | Scatter 符號高亮 | 即時 | — |
| 2 | Scatter 飛入對應盆子 | await spine/tween（飛行 0.5~0.8s） | SpineKit |
| 3 | 盆子收到反饋動畫（震動/發光） | await spine（0.3s） | PotManager |
| 4 | 檢查是否成長 → 播成長動畫 | await spine | PotManager |
| 5 | 檢查是否觸發 | — | server 結果 |
| 5a | 觸發成功：盆子一階一階長到頂 → 觸發爆發動畫 | await spine | — |
| 5b | 觸發失敗：盆子回退動畫 | await spine | — |
| 6 | 回到 CheckState 繼續 | — | — |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 單盆子 vs 多盆子 | 1個累積 vs 3+個各自累積 | eye_strike vs 3LP |
| 階段數 | 3~6 級不等 | 依遊戲 |
| 觸發方式 | 純累積滿觸發 vs 每次機率觸發 | eye_strike vs 3LP |
| Super Scatter | 一次進所有盆子 | 3LP 彩色 |
| FG 中可再觸發 | 未獲得的特色在 FG 中追加 | 3LP |
| 回 MG 後狀態 | 已觸發歸零 vs 未觸發保留 | 3LP (已觸發歸零，未觸發保留) |
| Scatter 注入升級 FG 階級 | 隨機事件（非蒐集）直接丟 1 顆 SCATTER 到輪帶上，把一般 FG 升級成 SUPER FG；走「補齊 SCATTER 數量」邏輯而非盆子蒐集 | Eye Strike2（神秘事件2）|

## 邊界案例

1. **每次旋轉 Scatter 數量限制**：通常每輪最多 1 顆、每次旋轉最多 1 顆
2. **Super Scatter 互斥**：彩色不與單色同時出現
3. **FG 中已有特色的 Scatter 不再出現**：需動態調整轉輪帶
4. **盆子觸發動畫必須一階一階長**：不能跳級直接播觸發
5. **跨 session 持久化**：盆子階段需要跟 server 同步（RecoverSpinAck）
6. **同時觸發多特色**：需排隊播觸發動畫（不能同時播 3 個盆子爆發）
7. **7 種 FG 組合（3LP）**：3 色各自觸發 + 任2色組合(3種) + 全3色 = 7 種 FG 配置，UI 宣告面板需對應所有組合
8. **注入式 vs 蒐集式要分清（Eye Strike2 神秘事件2）**：神秘事件2 是「畫面震動→丟 1 顆 SCATTER 到盤面補齊數量→升級 SUPER FG」的注入事件，與本 pattern 的盆子蒐集是不同路徑——它不進盆子、不改盆子階段，只動 SCATTER 計數。規格描述極簡（僅「畫面震動 突然丟一個 SCATTER 到輪帶上」），流程細節（觸發時機/機率/與 Feature Wheel FG 功能的關係）待規格補完，實作前需向企劃確認

## 常見錯誤

1. **❌ 盆子成長動畫跳級**：觸發時需一階一階長到頂→再播爆發；直接跳到最終階段播爆發 = 玩家無法感知累積感
2. **❌ 多盆子觸發同時播放**：多色同時觸發時需排隊依序播觸發動畫；並行會導致音效疊加+UI 遮擋
3. **❌ FG 中 Scatter 出現的顏色邏輯錯**：已觸發特色的顏色 Scatter 不再出現（需動態調整轉輪帶）；忘了就會出現「同色重複觸發」bug
4. **❌ 注入式（Eye Strike2 神秘事件2）走了蒐集式流程**：注入不進盆子不改階段，只補 SCATTER 計數升級 FG；混用會讓盆子無端跳級
5. **❌ 跨 session 盆子階段用 client 本地變數**：盆子階段必須 server 權威（RecoverSpinAck 下發），本地變數斷線重連後必錯
