# Pattern: Progression Unlock（進度解鎖 / 地圖系統）

## 識別條件

規格書出現以下描述時匹配：
- 「累積 N 個 {符號} 解鎖 {玩法}」「依序解鎖」
- 「地圖 / 進度條 / 解鎖樹」推進
- 「遊戲的 Feature 需要透過轉出 {符號} 來依序解鎖」
- 玩法不是一開始全開，而是隨長線累積逐步啟用
- 達某階改變遊戲型態（如解鎖 Super 模式、盤面擴張）

這是**長線 / 跨 spin 的 meta 機制**（不是單手 feature），核心是「持久計數器 + 階段門檻 → 啟用後續玩法」。

與其他「跨 spin」pattern 的差異：
- vs `persistent-grid-effect.md`：後者是格子效果在一段 session（FG）內累積；本 pattern 是**玩法本身的啟用狀態**沿進度推進，粒度更高（解鎖的是 feature 不是格子）。
- vs `scatter-collect.md`：盆子是單一容器階段；本 pattern 是**多階解鎖樹**，每階解一個不同玩法。

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| Wrath of Thunder v2（規格） | Feature 解鎖地圖 | 累積 Collect 數 → 依序解鎖 Boost/Multi/Chain/Burst/聚寶盆/Super Bonus；Super FG 另有地圖解 Split/盤面擴張 |

### 核心檔案（規劃中）
- `Manager/ProgressionManager.ts` — 持久計數器（跨 spin、需 server 同步）+ 解鎖門檻判定 + 已解鎖狀態
- `UI/ProgressMapUI.ts` — 地圖 / 進度條視覺、解鎖宣告動畫
- `GameView.ts` → 每手解析 progress 快照，判斷本手是否跨過門檻

## State 映射

**不需要獨立 State**，是橫切的狀態層；在每手結算後檢查門檻：

```
AwardState / RoundEndState（本手 Collect 數結算後）
  → ProgressionManager.add(collectCount)
  → 跨過門檻? → 播解鎖宣告 → 啟用對應 feature flag（影響後續 CheckState 路由）
  → 達最終門檻? → 切換遊戲型態（如進 Super 模式 / 盤面擴張，見 expand-reel）
```

解鎖的 feature flag 會被後續流程（CheckState / FeatureShowState）讀取，決定某 feature 是否觸發。

## Data 需求

```typescript
interface ProgressionData {
  /** 當前累積計數（server 權威，跨 spin 持久） */
  currentCount: number;
  /** 各門檻定義 */
  milestones: ProgressionMilestone[];
  /** 已解鎖的 feature 旗標 */
  unlocked: string[];
  /** 本手是否跨過門檻（觸發解鎖宣告） */
  newlyUnlocked?: string[];
}

interface ProgressionMilestone {
  /** 達標所需累積數 */
  threshold: number;
  /** 解鎖的 feature 識別 */
  unlocks: string;
  /** 附帶獎勵（如額外 FG 局數） */
  bonus?: { type: 'extraSpins' | 'expand' | 'splitLevel'; value: number };
}
```

### 範例門檻（Wrath of Thunder v2）

| 累積 Collect | MG 解鎖 | Super FG 解鎖 |
|---|---|---|
| 2 | Boost Collect | Split x2（+5 spins） |
| 5 | Multi Collect | 盤面向上擴 1 行（+5 spins） |
| 8 | Chain Collect | Split x3（+5 spins） |
| 10 | — | 盤面向上擴 2 行（+10 spins） |
| 12 | Burst Feature | — |
| 16 | 聚寶盆 | — |
| 19 | Super Bonus Game | — |

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 本手 Collect 結算完，計數器累加動畫 | await tween | currentCount |
| 2 | 跨過門檻 → 地圖節點亮起 | await spine(0.5s) | newlyUnlocked |
| 3 | 解鎖宣告面板（顯示新玩法 / 附帶獎勵） | await panel.close() | milestone |
| 4 | 附帶獎勵生效（+局數動畫 / 盤面擴張 → 見 expand-reel） | await | bonus |
| 5 | 後續 spin 起該 feature 進入可觸發狀態 | — | feature flag |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| MG 解鎖玩法 vs Super 模式解鎖強化 | MG 解鎖收集變體，Super FG 解鎖 Split/擴張 | Wrath of Thunder v2 |
| 線性門檻 vs 分支樹 | 單線累積 vs 多條路徑 | 依遊戲 |
| 解鎖即永久 vs session 內 | MG 進度可能永久；FG 地圖隨 FG 結束重置 | Wrath of Thunder v2 |
| 達頂改變型態 | 全解鎖後一般 FG 升級為 Super FG | Wrath of Thunder v2 |
| 計數來源 | Collect 數 / Scatter 數 / 特定符號數 | 依遊戲 |

## 邊界案例

1. **持久化是硬需求**：計數器必須 server 權威 + RecoverSpinAck 還原，斷線重連要正確顯示進度與已解鎖狀態，client 不可本地累加重建
2. **門檻跨越的 timing**：同一手可能一次跨多個門檻（大量 Collect），需依序播解鎖、不可吞掉
3. **解鎖與觸發解耦**：解鎖只是「啟用可觸發」，該玩法本手未必觸發；別把解鎖宣告和玩法觸發混在一起演
4. **達頂切換型態**：全解鎖後遊戲型態變化（進 Super / 擴張盤面）需與 expand-reel / 模式切換協調
5. **附帶獎勵與主流程順序**：解鎖附帶的 +局數 / 擴張要在進下一手前生效
6. **MG vs FG 進度是否共用**：需確認兩套地圖是獨立計數還是共享（Wrath 為獨立：MG 一套、Super FG 另一套）
7. **Unshow/Replay**：還原時計數器與已解鎖旗標需回退到該手之前狀態

## 常見錯誤

1. **❌ 計數器用 client 本地累加**：計數器是跨 spin 持久的，必須 server 權威 + RecoverSpinAck 還原；client 本地加會因斷線、跳手、replay 而漂移
2. **❌ 同一手跨多門檻只播第一個**：大量 Collect 可能一手跨 2-3 個門檻（如 2→8），需依序全部播解鎖宣告——只播一個 = 玩家不知道後面解了什麼
3. **❌ 把解鎖和觸發混在一起**：解鎖 = 啟用可觸發狀態（feature flag on），本手未必實際觸發該玩法；別把解鎖宣告動畫和玩法觸發演出合併
4. **❌ 附帶獎勵（+局數/擴張）在下一手才生效**：附帶獎勵應在進下一手前生效（如 +5 局數要先加完再開始下一 spin）；延遲一手 = 少給局數
5. **❌ MG 和 FG 進度共用同一個計數器**：Wrath of Thunder v2 的 MG 進度和 Super FG 進度是獨立的——共用 = 互相干擾（MG 進度被 FG 覆蓋）
