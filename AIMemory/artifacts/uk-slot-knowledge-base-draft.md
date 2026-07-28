# UK Slot 靜態知識庫

供公司 ai_multi_agent 使用的靜態 markdown 知識，涵蓋 UK 老虎機專案全角色（開發、企劃、機率、QA）。

---

## A. 術語表 / Glossary

### 盤面與結構

| 術語 | 英文 | 說明 |
|------|------|------|
| 轉輪 | Reel | 垂直排列的 symbol 列（直行） |
| 橫列 | Row | 盤面的水平列 |
| 盤面 | Grid / Board | 所有 Reel × Row 組成的完整畫面 |
| 連線 | Payline | 固定路線，symbol 按線排列才算中獎 |
| Ways | Ways to Win | 不依賴固定 payline，相鄰列出現相同 symbol 即中獎（如 4096 Ways = 6×4×4×4×4×4） |
| 停輪位置 | Stop Position | 轉輪帶上每列最終停在哪個 index |
| 轉輪帶 | Reel Strip | 每列 symbol 的完整排列定義（循環） |

### 符號類型

| 術語 | 英文 | 說明 |
|------|------|------|
| 一般符號 | Regular Symbol | 基礎賠付符號（高賠 H1~H5 / 低賠 L1~L5） |
| 百搭 | Wild | 替代任何一般符號（通常不替代 Scatter/Bonus） |
| 分散符號 | Scatter | 不需在 payline 上，出現 N 個即觸發功能（通常觸發 Free Spin） |
| 獎勵符號 | Bonus | 觸發 Bonus Game（如 Pick Game） |
| 神秘符號 | Mystery | 停輪後統一變身為同一種 symbol |
| 收集符號 | Collect | 觸發收集機制（蒐集盤面上的特定值） |

### 功能機制

| 術語 | 英文 | 說明 |
|------|------|------|
| 免費旋轉 | Free Spin / Free Game (FG) | 不扣注的旋轉回合，通常由 Scatter 觸發 |
| 重轉 | Respin | 特定條件下重新旋轉部分或全部轉輪 |
| 消除 | Cascade / Tumble | 中獎 symbol 消除後上方落下補位，可連鎖 |
| 額外押注 | ExtraBet | 加碼投注以提高觸發機率或強化功能 |
| 購買功能 | Buy Bonus / Feature Buy-in | 玩家付費直接進入 Feature（跳過觸發） |
| 鎖定重轉 | Hold & Win / Lock & Spin | 特殊符號鎖定，其餘重轉，集滿或用盡次數結算 |
| 乘倍 | Multiplier | 獎金倍數放大 |
| 最大獎上限 | Max Win Cap | 單次功能或單局總贏分上限 |
| 假轉輪 | Fake Reel | client 端演出用的視覺轉輪帶（非 server 真實結果） |
| 聽牌 | Near Miss / Near Win | 差一個即觸發功能，有特殊演出 |

### 數學與機率

| 術語 | 英文 | 說明 |
|------|------|------|
| 返還率 | RTP (Return to Player) | 長期理論回饋百分比（如 96.5%） |
| 波動度 | Volatility | 獎金分布的離散程度（低=頻繁小獎 / 高=罕見大獎） |
| 命中率 | Hit Rate | 每 N 次 spin 平均中獎一次（如 1/3.5） |
| 投注等級 | Bet Level | 玩家可選的下注金額檔位 |
| 線注 | Line Bet | 單條 payline 的投注金額 |
| 總注 | Total Bet | Line Bet × Payline 數（或 Ways 制下的固定倍率） |

---

## B. 規格書結構說明

> 每個專案的規格書 sheet 命名不固定，以下為常見模式。

### 常見 Sheet 分類

| Sheet 名稱模式 | 內容 | 主要讀者 |
|---|---|---|
| Paytable / 賠付表 | 各 symbol 在不同連線數下的賠付倍率 | 機率、QA |
| Reel Strips / 轉輪帶 | 每列 symbol 排列（Base Game 和 Free Game 各一組） | 機率、開發 |
| Math / RTP | 數學模型、RTP 計算結果、hit rate | 機率 |
| Game Flow / 遊戲流程 | 狀態流程圖、模式切換條件 | 企劃、全角色 |
| Feature Rules / 功能規則 | 各 Feature 觸發條件、獎勵計算、特殊規則 | 全角色 |
| Symbol List / 符號表 | symbol ID、名稱、圖檔對應 | 開發、美術 |
| Bet Config / 投注設定 | 投注等級、line bet 對應 total bet | 全角色 |

### 關鍵數值讀法

- **Ways 計算**：各列可出現 symbol 的行數相乘（如 5 列各 4 行 = 4^5 = 1024 Ways）
- **Scatter 觸發**：看 Feature Rules 中「N 個 Scatter 出現在任意位置」的條件
- **RTP 區分**：Base Game RTP + Feature RTP = 總 RTP；ExtraBet 開啟時通常有獨立 RTP

### 各角色看規格書的重點

| 角色 | 重點 Sheet | 關注什麼 |
|------|-----------|----------|
| 企劃 | Game Flow、Feature Rules | 玩法是否清楚、流程有無矛盾 |
| 機率 | Math、Reel Strips、Paytable | RTP 是否達標、數值平衡 |
| 開發 | 全部（重點 Reel Strips + Feature Rules） | 轉成程式邏輯 |
| QA | Paytable、Feature Rules | 驗證實作是否與規格一致 |

---

## C. 遊戲流程模式

### 基本狀態機

```
[Idle] → 玩家按 Spin → [Spinning] → Server 回傳結果 → [Stopping]
  → [Award] → 有 Feature? → [Feature] → [Award] → [Idle]
                           → 無 Feature → [Idle]
```

### 通用單局流程

1. 玩家下注（選 Bet Level）
2. 按 Spin → client 送 request → server 回 response（含 result + 獎勵資訊）
3. 轉輪演出 → 停輪
4. 中獎判定 + 中獎演出（WinLine / Ways highlight）
5. 若觸發 Feature → 進入 Feature 狀態
6. Feature 結束 → 結算總獎金 → 回 Idle

### 常見 Feature 模式

| 模式 | 觸發條件 | 行為 | 頻率 |
|------|----------|------|------|
| Free Spin | N 個 Scatter | 給固定/累加次數，可 retrigger | 高 |
| Pick Bonus | Bonus symbol | 玩家選物件揭獎 | 高 |
| Cascade / Tumble | 中獎後 | 消除中獎 symbol、上方落下補位、連鎖 | 中 |
| Respin | 特定條件（如特殊 symbol） | 鎖定部分 reel 重轉 | 高 |
| Hold & Win | 特殊 symbol 集滿觸發 | 鎖定收集、局數重置、集滿/用盡結算 | 中 |
| Expanding Wild | Wild 落定 | Wild 擴展整列 | 中 |
| Multiplier Trail | 連續中獎 | 倍率遞增 | 中 |
| Feature Buy-in | 玩家付費 | 直接進入 Feature（跳過觸發條件） | 高 |
| Mystery Symbol | Mystery 停定 | 全部 Mystery 變身為同一種 symbol | 高 |
| Collect Feature | Collect symbol 出現 | 收集盤面上其他 symbol 的值（乘倍/金額） | 高 |
| VS Feature | 對決觸發 | 兩方角色各自累積乘倍對決 | 低 |

### 結算邏輯

- **Ways 制**：相鄰列同 symbol 個數相乘 × 賠率 × Total Bet
- **Lines 制**：payline 上連續匹配數 → 查 Paytable 得倍率 × Line Bet
- **Max Win Cap**：單局/單 Feature 獎金超過上限時截斷

---

## D. Astarte Framework 概要

> 僅概要層，不含完整 API 細節。

### 生命週期

```
GameApp 初始化
  → SceneManager 載入場景
    → GameView (主遊戲容器) onLoad
      → 各 Component onLoad → start
        → 遊戲就緒
```

### 核心 Class 繼承

| Base Class | 衍生 | 職責 |
|---|---|---|
| BaseGame | GameView | 主遊戲容器、狀態機宿主 |
| BaseSlotReels | SlotReels | 轉輪控制（啟動/停止/設結果） |
| BaseSymbol | Symbol | 單格符號（顯示/動畫/狀態） |
| StateMachine | — | 遊戲狀態流程控制 |

### 事件系統

- 採 EventEmitter 模式（on / off / emit）
- 常用事件：
  - `SPIN_START` — 轉輪開始轉動
  - `SPIN_END` — 所有列停定
  - `WIN_SHOW` — 中獎演出開始
  - `FEATURE_ENTER` — 進入 Feature
  - `FEATURE_EXIT` — Feature 結束回 Base

### 不可動的部分

- `extensions/` — Astarte Framework core，專案不可修改
- `proto/` — server 端定義的通訊協定，client 只讀
- 框架 base class — 只可 override 指定 method，不可改 base

---

## E. 通用機制模式庫（索引）

> 完整說明需查閱各模式卡片。以下為索引摘要。

| # | 模式 | 一句話說明 | 頻率 |
|---|------|-----------|------|
| 1 | Collect Feature | 盤面出現 Collect symbol 時收集其他 symbol 的值 | 高 |
| 2 | Scatter 蒐集觸發 | Scatter 累積 N 個觸發 Free Spin | 高 |
| 3 | 盤面擴展 (Expand) | 特定條件觸發後盤面行數增加 | 中 |
| 4 | Multiplier 格子 | 格子附帶乘倍值，中獎時乘倍疊加 | 中 |
| 5 | Bomb 爆炸 | Bomb symbol 炸開周圍格子，產生效果 | 中 |
| 6 | BonusGame Pick | 進入選物件揭獎的小遊戲 | 高 |
| 7 | Respin | 特定條件重轉部分或全部轉輪 | 高 |
| 8 | NearMiss 聽牌 | 差一個觸發功能，播特殊期待演出 | 高 |
| 9 | FakeReelManager | client 演出用的假轉輪帶管理 | 高 |
| 10 | ExtraBet | 加碼投注提高觸發機率/強化功能 | 中 |
| 11 | Buy Bonus | 玩家付費直接進入 Feature | 高 |
| 12 | Wild 變身 | Wild 停定後觸發特殊變身效果 | 中 |
| 13 | Mystery 符號 | 停輪後 Mystery 統一變身為同一 symbol | 高 |
| 14 | COLLECT 神秘事件 | Collect 觸發時的特殊神秘事件 | 中 |
| 15 | Feature Wheel | 轉盤決定獎勵/Feature 類型 | 低 |
| 16 | Symbol Transform | 符號在盤面上動態變形 | 低 |
| 17 | Persistent Grid Effect | 格子效果跨 spin 持續存在 | 低 |
| 18 | VS Feature | 兩方對決各自累積乘倍 | 低 |
| 19 | MAX WIN | 單局/Feature 獎金封頂機制 | 中 |
| 20 | Progression Unlock | 進度/地圖解鎖系統 | 低 |
| 21 | Global Multiplier | 全局/Wild 乘倍器 | 低 |
| 22 | Hold & Win | 鎖定收集 + 局數重置型功能 | 中 |
| 23 | Pot/Meter 蓄能投放 | 容器蓄能滿級後投放獎勵 | 中 |
| 24 | Unshow 斷線復原 | 斷線後復原盤面與功能狀態 | 基礎 |
| 25 | StateMachine 骨架 | 遊戲狀態機的模板結構 | 基礎 |

### 橫切機制（設計任何 Feature 都要考慮）

| 機制 | 為什麼重要 |
|------|-----------|
| MAX WIN 封頂 | 每種贏分來源都要計入上限，漏算就超額 |
| Unshow 斷線復原 | 新 Feature 幾乎必忘，只有拔網線才會發現 |
| PlateSymbol vs PlateSymbolLog 雙軌 | 用錯不報錯，只會少收/少算 |

---

## F. 專案慣例與命名規範

### 命名規範

| 類型 | 規則 | 範例 |
|------|------|------|
| 方法/函式 | PascalCase | `StartSpin()`, `ShowWin()` |
| 成員變數 | m_ + camelCase | `m_reelData`, `m_winAmount` |
| 區域變數 | camelCase | `symbolCount`, `isFeature` |
| 常數 | UPPER_SNAKE_CASE | `SYMBOL_COUNT`, `MAX_WIN_CAP` |
| 檔案名 | 與 class 同名 | `SlotReels.ts`, `GameView.ts` |

### 檔案結構

```
uk_xxx_client/
├── assets/
│   ├── scripts/       ← 遊戲邏輯（主要工作區）
│   ├── resources/     ← 動態載入資源
│   ├── scenes/        ← 場景檔
│   └── ...
├── extensions/        ← ❌ 不可動（Astarte Framework core）
├── proto/             ← ❌ 不可動（server 定義）
└── ...
```

### Proto 對接慣例

- Proto 檔由 server 端定義，client 只讀不改
- Response 欄位命名以 server 為準
- 使用 protobufjs 解析
- Mock 資料必須欄位完整（含 RoundWin、陣列欄位給空陣列）

### 起新專案流程

1. 從 `uk_slot_template` clone
2. 修改 `Game_Define`（GameId、ShortGameName、盤面配置：COL、ROW）
3. 根據規格書建立 `SetStateMachine()`（狀態流程）
4. 依 Feature 需求建立各 Manager / Component
5. 設定 FakeReel（client 演出用假轉輪帶）

### 不可動的部分

| 路徑 | 說明 |
|------|------|
| `extensions/` | Astarte Framework，由框架團隊維護 |
| `proto/` | Server 通訊定義，由 server 團隊維護 |
| 框架 Base Class | 只可 override 指定 method，不可修改 base 本身 |

---

## G. 測試與驗證指引

### 驗 Paytable 流程

1. 開啟規格書的 Paytable sheet
2. 對照程式中的賠率設定（通常在 Game_Define 或 proto response）
3. 逐一驗證：每個 symbol、每個連線數的賠付倍率是否一致
4. 注意 ExtraBet 開啟時可能有不同賠率組

### Proto Response 驗證

1. 使用 DevTool 攔截 server response
2. 確認關鍵欄位存在且型別正確：
   - `RoundWin`（本局總獎金）
   - `Result`（盤面結果陣列）
   - Feature 相關欄位（FreeSpinCount、Multiplier 等）
3. 注意 number vs string 型別差異

### Feature 觸發驗證

1. 使用 ReelDevTool 設定假結果，強制觸發各 Feature
2. 確認觸發條件與規格一致（N 個 Scatter、特定組合等）
3. 驗證 Feature 內的次數、乘倍、獎金計算
4. 測試 retrigger（Feature 中再次觸發）

### 常見 QA Checkpoint

- [ ] Free Spin 次數與規格一致
- [ ] Multiplier 計算正確（累加 vs 相乘）
- [ ] Max Win Cap 在所有贏分路徑都有生效
- [ ] Scatter 觸發數量正確（不多不少）
- [ ] 斷線重連後狀態正確（Unshow）
- [ ] ExtraBet 開關對觸發機率/賠率的影響

### ReelDevTool 使用

- 開發時用 ReelDevTool 設定指定停輪結果
- 可強制觸發特定 Feature 場景
- 注意：DevTool 只控制 client 演出，不影響 server 判定

---

## H. 踩坑經驗

### H1. cc.Layout 退場重排

**症狀**：節點退場時 Layout 重排導致畫面跳動。
**根因**：`node.active = false` 瞬間觸發 Layout 重新計算。
**對策**：退場前移出 Layout 管轄，或先播完動畫再設 active = false。

### H2. Promise.all 前同步決策的 Race Condition

**症狀**：並發 promise 改了共享狀態，先前的同步決策已過時。
**根因**：同步計算完成後進入 Promise.all，其他 promise 改了依賴的狀態。
**對策**：依賴共享狀態的決策移到 async 階段（各自 promise 內）。

### H3. Ghost Slot 雙佔位

**症狀**：Layout 移除一項後剩餘項瞬間置中跳動。
**根因**：Layout 只看 active children 數量計算位置。
**對策**：用不可見 ghost node 佔住原位，同時滿足 0→1 置中和 2→1 不跳動。

### H4. Drop-Out 動畫凍結

**症狀**：掉落動畫播完後視窗仍凍結。
**根因**：凍結語意和動畫 promise 耦合在一起。
**對策**：新增獨立布林管凍結語意，promise 只管動畫 handle。

### H5. UTF-8 BOM 丟失

**症狀**：改完 .ts 後 runtime 報 `__unresolved_X`。
**根因**：工具寫回時丟失 UTF-8 BOM（EF BB BF）。
**對策**：用 byte-level 操作保留 encoding。看到 `?�` 亂碼 = 已損壞，從 template 重新複製。

### H6. SYMBOL_COUNT 禁動態計算

**症狀**：動態算 enum 數量在 build 後 = 0。
**根因**：Cocos bundler tree-shake 把 enum 反查搖掉。
**對策**：一律硬編碼數字。

### H7. Spine placeholder 必須用 .json

**症狀**：自產 .skel binary placeholder 載入失敗。
**根因**：Cocos 3.6.2 對 .skel 強制 binary parser，不做 JSON fallback。
**對策**：placeholder 用 .json 格式，正式美術交付後換 .skel。

### H8. Mock 資料欄位不完整

**症狀**：BigWin / 報獎永遠不觸發。
**根因**：mock 缺 `RoundWin` → rate = undefined → 報獎靜默跳過。
**對策**：每個 mock 都設 RoundWin；陣列欄位給空陣列；加 type annotation 讓 tsc 攔。

### H9. 規格書 Scatter 命名 ≠ 程式的 SCATTER_SYMBOL

**症狀**：NearWin 不觸發或判錯符號。
**根因**：規格書叫 Scatter_Expand / Scatter_Bomb，但程式的 SCATTER_SYMBOL 只放觸發 FG 的那顆。
**對策**：判斷依據是「是否觸發 FG / 參與 NearWin」，不是名字。

---

## I. 環境設定

### 技術棧

| 項目 | 版本/工具 |
|------|-----------|
| 遊戲引擎 | Cocos Creator 3.6.2 |
| 程式語言 | TypeScript |
| 框架 | Astarte Framework |
| Proto 工具 | protobufjs |
| 版本控制 | Git |

### Build 指令

- Cocos Creator 內建 Build（選平台 → Build → 產出 web-mobile 或 web-desktop）
- 本地預覽：Cocos Creator Editor 的 Play 按鈕

### ReelDevTool

- 開發用工具，可在 runtime 設定指定停輪結果
- 用途：強制觸發特定 Feature 場景、驗證演出邏輯
- 注意：僅影響 client 端演出，不改 server 回傳結果
