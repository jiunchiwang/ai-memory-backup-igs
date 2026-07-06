# Pattern: Global Multiplier（全局乘倍 / Bonus Multiplier / Wild 乘倍）

## 識別條件

規格書出現以下描述時匹配：
- 「BONUS MULTIPLIER」「該局所有贏分乘上累積倍數」
- 「FG 中贏分受 {倍數} 影響」「FG 結束倍數歸 1」
- 「Wild 自帶乘倍 x2/x3/x5，連線時該手贏分乘上 Wild 倍率」
- 倍率作用對象是**整手 / 整局贏分**，不是單一符號或單一格子

與 `multiplier-grid.md` / `persistent-grid-effect.md` 的關鍵差異：
- 那兩者：倍率綁在**特定格子**，只有落在該格的 CASH 才乘。
- 本 pattern：倍率是**全局係數**——乘的是整手線獎 / 整局總贏分（或由連線中的 Wild 帶入），不挑格子。

兩種子型（常共存於一款遊戲）：
1. **累積型（Bonus Multiplier）**：跨 spin 累加的全局倍率，作用該局所有贏分，模式結束歸 1。
2. **符號型（Wild 乘倍）**：Wild 自帶倍率，**僅當該 Wild 參與連線**時乘該手贏分（多個 Wild 同線通常相乘或相加，依規格）。

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| Wrath of Thunder v2（規格） | BONUS MULTIPLIER + Wild 乘倍 | FG 全局累積倍率（結束歸 1）；FG 中每個 Wild 帶 x2/x3/x5，連線時乘該手贏分 |

### 核心檔案（規劃中）
- `Manager/BonusMultiplierManager.ts` — 全局累積倍率狀態（跨 spin、模式結束 reset）
- `WildMultiplier` 邏輯 — 連線判定時讀取參與連線的 Wild 倍率並施加
- `AwardState` → 計分時套用全局倍率 / Wild 倍率

## State 映射

**不需要獨立 State**，嵌在計分階段：

```
AwardState（線獎 + Collect 等贏分算出後）
  → 套用 Wild 乘倍（若該手連線含帶倍 Wild）
  → 套用 Bonus Multiplier（全局累積係數）
  → 顯示最終贏分 → 累加 Bonus Multiplier（若本手規則要求成長）
模式結束（LeaveFreeState）→ BonusMultiplierManager.reset()（歸 1）
```

## Data 需求

```typescript
interface GlobalMultiplierData {
  /** 當前全局累積倍率（跨 spin，模式結束歸 1） */
  bonusMultiplier: number;
  /** 本手是否成長 + 成長後值 */
  bonusMultiplierNext?: number;
  /** 本手參與連線的 Wild 及其倍率 */
  wildMultipliers?: { position: { col: number; row: number }; multiplier: number }[];
}
```

> ⚠️ 多 Wild 同線是「相乘」還是「相加」、Bonus Multiplier 的成長規則（每手 +1？每觸發 +N？）規格常未寫死，實作前需向企劃 / 機率文件確認。

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 本手線獎 / Collect 贏分算出 | — | AwardState |
| 2 | 連線含帶倍 Wild → Wild 倍率飛入贏分、數字翻倍 | await tween | wildMultipliers |
| 3 | 套用全局 Bonus Multiplier → 總贏分再乘 | await count | bonusMultiplier |
| 4 | 顯示最終贏分 | await count | — |
| 5 | （若成長）Bonus Multiplier UI 累加動畫 | await tween | bonusMultiplierNext |
| N | 模式結束 → 倍率歸 1 動畫 | 即時 | reset |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 累積型（Bonus Multiplier） | 跨 spin 累加、作用整局贏分、結束歸 1 | Wrath of Thunder v2 |
| 符號型（Wild 乘倍） | Wild 自帶倍率，僅參與連線時乘 | Wrath of Thunder v2 |
| 兩型共存 | 同一 FG 同時有全局倍率與 Wild 倍率（作用順序需定義） | Wrath of Thunder v2 |
| 多 Wild 相乘 vs 相加 | 同手多個帶倍 Wild 的合成規則 | 依規格 |
| 全局倍率只增不減 vs 可重置階段 | 只增到模式結束 vs 中途特定事件重置 | 依設計 |

## 邊界案例

1. **作用對象別搞錯**：全局倍率乘「整手/整局贏分」，不是逐格——別誤用 multiplier-grid 的逐格邏輯
2. **作用順序**：Wild 乘倍（手內）→ 全局 Bonus Multiplier（局係數），順序顛倒金額會錯
3. **結束歸 1**：模式（FG）結束務必 reset，否則污染下次
4. **與 Collect/JP 交互**：Collect 收分、JP 轉分後的金額才套全局倍率（確認規格是否含 Collect 贏分）
5. **與 MAX WIN 交互**：套完所有倍率的最終金額才比對 MAX WIN 上限（見 `max-win.md`）
6. **斷線重連**：bonusMultiplier 由 server 下發還原，不可本地重算
7. **Wild 不參與連線時**：帶倍 Wild 若沒形成任何線，倍率不作用（符號型的核心條件）

## 常見錯誤

1. **❌ 把全局乘倍和格子乘倍混用**：全局倍率乘「整手/整局贏分」；格子乘倍只乘「該格的 CASH」——用錯 = 金額差距巨大
2. **❌ 作用順序顛倒**：正確是 Wild 乘倍（手內）→ Bonus Multiplier（局係數）；顛倒 = 數學結果不同
3. **❌ 模式結束不歸 1**：FG 結束時 bonusMultiplier 必須 reset to 1；忘了 = 下次 FG 從上次殘留倍率開始累加
4. **❌ Wild 不在連線中也乘**：符號型倍率的核心條件是「該 Wild 參與連線時」才作用；不在線上的帶倍 Wild 不乘——忽略條件 = 每手都多乘
5. **❌ 多 Wild 合成規則沒確認就寫死**：同手多個帶倍 Wild 是「相乘」還是「相加」規格常未寫死，實作前需向企劃確認——猜錯 = 贏分差距指數級
