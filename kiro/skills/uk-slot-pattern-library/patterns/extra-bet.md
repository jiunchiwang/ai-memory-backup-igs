# Pattern: ExtraBet

## 識別條件

- 規格提到「額外押注」「加注」「Extra Bet」「付更高押注換取更好機率」
- 有 ON/OFF 切換按鈕影響中獎倍率或特色觸發率
- 倍率表 `Mul[0]` 為基礎、`Mul[1..]` 為 ExtraBet 倍率
- 影響假轉輪預設盤面（ExtraBet 版有更多特殊符號）
- **主題包裝別名**：規格常用主題名稱包裝此機制，未必出現「額外押注」字樣。已知別名：「懸賞令」(Eye Strike2)。遇到「付費/加注換取更高乘倍或更好觸發率」的主題化敘述，先比對是否為 ExtraBet 換皮，不要因關鍵字不符就漏判

> ⚠️ **判準是實作不是文案**：spec 可能把 ExtraBet 寫成偏「玩法乘倍」的敘述（如 Eye Strike2「消除到指定符號提升額外乘倍」）。確認方式以實作為準——專案若有 `ExtraBet/` 目錄、`ExtraBet_ON/OFF` 動畫、`Mul[]` 倍率表，即為本 pattern；若無對應實作而是盤面內乘倍格，應改判 `multiplier-grid.md` / `persistent-grid-effect.md`。

## 參考實作

| 專案 | 核心檔案 | 說明 |
|------|----------|------|
| eye_strike | ExtraBet/ExtraBetEffectManager.ts（5.5KB） | 單倍率單步驟（`isTwoStep` 旗標在框架 ExtraBetController 側，eye_strike 專案碼未直接定義——覆驗查無） |
| 框架 | ExtraBetComponent.ts | EX 按鈕 UI、開關狀態管理 |
| 框架 | ExtraBetController.ts | 全域 controller，供 unshow/replay 強制設值 |
| 已有 skill | uk-slot-extrabet | 完整架構含兩種變體、陷阱紀錄 |

## State 映射

ExtraBet **不需要獨立 State**。它在 IDLE 時由玩家操作，影響的是下次 Spin 的參數：

```
IDLE（玩家點 EX 按鈕）
  → ExtraBetComponent.ChangeBetMode()
  → ChangeMultiBet(type) 切換押注倍率
  → triggerCb → GameView callback
  → SlotReels.SetExtraBetInitPlateInfo() 切換假轉輪預設盤
```

與其他 State 互動：
- `IdleState`：`CheckCanUseBtn()` 守門（需在 MG + IDLE + 非 BuyBonus）
- `EnterFreeState`：隱藏 ExtraBet UI
- `LeaveFreeState`：恢復 ExtraBet UI
- `UnshowPrepareState`：`ForceSetExtraBet()` 還原狀態

## Data 需求

```typescript
/** 倍率表（server info ack 提供） */
interface IGameInfoData {
  /** Mul[0]=基礎倍率, Mul[1..]=ExtraBet 各種倍率 */
  Mul: number[];
  /** 本次連線是否提供 ExtraBet */
  ShowExtra?: boolean;
}

/** ExtraBet 類型常數 */
const TYPE = {
  Normal: 0,   // ExtraBet 關閉，用 Mul[0]
  Special: 1,  // 第一種 ExtraBet，用 Mul[1]
  // 多倍率時：2→Mul[2], 3→Mul[3]...
};

/** ExtraBet callback 簽名 */
type ExtraBetCallback = (isActive: boolean, isForce: boolean) => Promise<void>;

/** 跳窗結果（變體 B 才有） */
interface ExtraBetWindowResult {
  confirmed: boolean;
  type: number;  // 選擇的卡片 index+1 → 對應 Mul[type]
}

/** ExtraBet 影響 FakeReelManager 的 BetMode */
enum FakeReelBetMode {
  Normal   = 0,
  ExtraBet = 3,  // ExtraBet ON 時切換到此
}
```

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|----------|------|
| 1 | 玩家點 EX 按鈕 | user interaction | IDLE + CheckCanUseBtn |
| 2 | ChangeBetMode() 設 m_isExtra=true | 同步 | — |
| 3a（單步驟）| 立即 ChangeMultiBet(TYPE.Special) | 同步 | isTwoStep=false |
| 3b（兩步驟）| 設 m_toStepTwo=true，等跳窗 | — | isTwoStep=true |
| 4 | triggerCb(isActive, isForce) | async | — |
| 5 | ClearAllForExtraBet() 清場 | 同步 | — |
| 6 | PlayExtraBetActiveAnimation()（spine + 音效） | await animation | ExtraBetEffectManager |
| 7 | DelayChangeSlotReelsPlateInfo() 切假轉輪盤 | delay 1s（對齊動畫高潮） | SlotReels |
| 8（關閉時）| SetInitPlateInfo() 切回一般盤 | 同步 | — |

## 常見變體

| 變體 | 倍率數 | isTwoStep | 跳窗 | 代表專案 |
|------|--------|-----------|------|----------|
| A. 單倍率單步驟 | Mul[1] 一種 | false | 無 | eye_strike |
| B. 多倍率兩步驟 | Mul[1..n] 多種 | true | ExtraBetWindow 選卡 | 多倍率機台 |
| 無動畫簡化版 | 任意 | 任意 | 任意 | 小型專案（跳過 EffectManager） |

## 邊界案例

1. **ForceSetExtraBet 不帶 type（變體 B 陷阱）**：unshow/replay 還原時 `ForceSetExtraBet(true)` 預設 type=1，多倍率遊戲會永遠還原成第一種，需從 proto 反推正確 type
2. **ExtraBet 連動持久視覺被每轉 reset**：SpinState.OnEnter 可能清空乘倍底板等視覺，ExtraBet 開啟時需在 reset 處判斷並重套用
3. **triggerCb 中 type 資訊丟失**：callback 簽名只有 `(isActive, isForce)`，type 未傳入；需在 GameView 存成員 type 供 isForce 分支讀取
4. **與 BuyBonus 互斥**：啟用 BuyBonus 時須關閉 ExtraBet、禁用按鈕；反之亦然。`CheckCanUseBtn()` 已排除 `IsBuyBonus`
5. **ShowExtra=false 時的 gating**：server 可能不提供 ExtraBet，GameView 各入口方法（ShowExtraBet / RestoreExtraBetState / FirstShowBar）需 early return
6. **FG 期間 ExtraBet 狀態保留**：進 FreeGame 隱藏 UI 但不清除 `m_isExtra`；離開 FG 後 UI 恢復時需正確反映當前狀態（開或關）

## 常見錯誤

1. **❌ ForceSetExtraBet 不帶 type（變體 B 多倍率）**：unshow/replay 還原時預設 type=1，實際可能是 type=2 或 3 → 還原到錯誤倍率
2. **❌ ExtraBet 開關沒切 FakeReel BetMode**：ExtraBet ON 應切到 BetMode.ExtraBet 的假轉輪帶（符號分布更好）；忘切 = 旋轉中符號預期與實際不符
3. **❌ triggerCb 結束前就發 Spin**：callback 是 async，動畫播完前玩家按 Spin = 用舊盤面計算 → 押注金額與視覺不一致
4. **❌ ShowExtra=false 時沒 early return**：server 不提供 ExtraBet 的場景（ShowExtra=false），各入口函式沒 guard → null reference crash
5. **❌ ExtraBet + BuyBonus 沒互斥**：兩者同時啟用會導致 FeatureBetValue 與 ExtraBet Mul 衝突 → 發送非法 bet 值
