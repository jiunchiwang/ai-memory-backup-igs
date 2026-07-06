# Pattern: Mystery 符號

## 識別條件

規格書出現以下描述時匹配：
- 「Mystery 符號/神秘符號」
- 「停輪後轉換/揭示為其他符號」
- 「所有 Mystery 轉換為同一種符號」
- 「server 決定轉什麼，client 做動畫」
- 「MysteryEvent」「逐格重轉」

## 參考實作

| 專案 | 機制 | 特殊點 |
|------|------|--------|
| uk_slot_eye_strike | ShowRewardController.ts (6.6KB) | MysteryEventKind enum，轉為 Cash/JP，有 4 種 event |
| uk_746_far_west | server-only symbol (Symbol.Mystery=98) | server 端直接替換，client 無 sprite/動畫 |
| uk_739_wrath_of_thunder | Symbol.Mystery=20, CollectMystery=18 | server 自動轉為其他 collect/symbol |
| 3LP | MysteryEvent（逐格重轉型） | 停輪後第5輪逐格重轉追加更多 COLLECT（見 collect-mystery.md） |

### 核心檔案（eye_strike）
- `Mystery/ShowRewardController.ts` — 揭示動畫控制（管理多格同步/序列播放）
- `Game_Define.ts` → Symbol.Mystery = 20
- `RecoverSpinAck.ts` → 解析 mystery 轉換結果
- `MysteryEventKind.ts` → enum 定義事件類型

## State 映射

**不需要獨立 State**。處理位置在 `PlateShowState` 或 `FeatureShowState`：
- 停輪後、正式對獎/Feature 前
- 先做 Mystery 揭示動畫
- 替換 plateInfo 中的 symbolId
- 再走後續流程

```
SpinState（停輪完成）→ PlateShowState / FeatureShowState
  → hasMystery? → 揭示動畫 → 更新 plateInfo
  → 進入後續流程（對獎 / Collect / Feature）
```

**例外**：3LP 的 MysteryEvent（逐格重轉型）有獨立的 `MysteryEventState`（因為涉及重轉而非單純揭示），詳見 `collect-mystery.md`。

## Data 需求

```typescript
interface MysteryResult {
  /** Mystery 出現位置 */
  mysteryPositions: { col: number; row: number }[];
  /** 揭示為什麼符號（所有 Mystery 統一揭示 or 各自不同） */
  revealSymbol: number;
  /** 若揭示為 Cash，帶金額 */
  revealValue?: number;
  /** 若揭示為 JP，帶等級 */
  revealJpType?: JPType;
  /** Mystery 事件種類（eye_strike 有 4 種） */
  mysteryEventKind?: MysteryEventKind;
}

enum MysteryEventKind {
  /** 標準：停輪揭示為一般符號 */
  Standard = 0,
  /** Cash 型：揭示為帶金額的 Cash */
  Cash = 1,
  /** JP 型：揭示為某等級 JP */
  JP = 2,
  /** 逐格重轉型：第5輪逐格重轉追加 Collect（見 collect-mystery.md） */
  Respin = 3,
}

enum JPType { Mini, Minor, Major, Mega, Grand }
```

### Server-only 變體（far_west 型）

far_west 的 Mystery 是純 server 概念：
- Symbol.Mystery = 98 僅存在於 server 機率表
- client 收到的 plateData 已是轉換後結果
- **不需要任何揭示動畫邏輯**
- 辨識方式：proto 中不會有 mysteryPositions 欄位

## 演出時序

| Step | 動作 | 等待方式 | 依賴 |
|------|------|---------|------|
| 1 | 全部停輪完成 | — | SpinState |
| 2 | Mystery 符號同時發光/震動（聚焦注意力） | await tween(0.3s) | mysteryPositions |
| 3 | 播翻轉/揭示動畫（所有格同步或依序） | await spine（0.5~0.8s） | SpineKit |
| 4 | 顯示揭示後的符號（更新 plateInfo） | 即時 | revealSymbol |
| 5 | 繼續正常流程（對獎/Collect/Feature） | — | — |

## 常見變體

| 變體 | 差異 | 參考 |
|------|------|------|
| 全部轉同一種 | 所有 Mystery 揭示為相同符號（最常見） | 大部分遊戲 |
| 各自不同 | 每個 Mystery 揭示不同（少見） | — |
| 轉為 Cash/JP | Mystery → 帶金額的 Cash 或 JP | eye_strike |
| 轉為 Wild | Mystery → Wild（同時取得百搭能力） | — |
| Server-only（無動畫） | server 端直接替換，client 收到已是最終結果 | far_west |
| CollectMystery | Mystery 版的 Collect 符號，揭示後變成 Collect | wrath_of_thunder |
| 逐格重轉型（MysteryEvent） | 停輪後觸發重轉流程（非單純揭示） | 3LP（見 collect-mystery.md） |
| Trigger 條件門檻 | 盤面上 Mystery 數量達 N 顆才觸發揭示，不足則當一般符號 | 部分機台 |

## 邊界案例

1. **Mystery 與 Collect 交互**：先揭示 Mystery → 若揭示為 CASH → 再被 Collect 收（順序不可反）
2. **Mystery 與 Multiplier 交互**：揭示為 CASH 後若在 Multiplier 格 → 先乘倍再被收
3. **FG 中 Mystery 行為**：可能揭示範圍不同（FG 限定只轉 Cash/JP，不轉一般符號）
4. **RecoverSpinAck**：斷線重連需直接顯示揭示後結果，跳過動畫
5. **FakeReelManager**：假轉輪帶中 Mystery 的出現由 server 機率表控制，FakeReel 不需模擬
6. **與 Wild 變身的差異**：Mystery 是「佔位符號停輪後揭示身份」；Wild 變身是「已有身份的符號升級為 Wild 版本」
7. **與 Symbol Transform 的差異**：Symbol Transform 是「Feature Wheel 觸發後批量指定格轉換」；Mystery 是「停輪時自帶佔位符號自動揭示」
8. **全盤 Mystery 極端情況**：所有格都是 Mystery 時揭示動畫不可逐格播（太久），需走批次同步動畫
9. **Mystery 與 VS Feature 交互**：若 Mystery 揭示為 Cash/JP 且同輪有 VS → 需被 VS 倍率影響（揭示先於 VS）

## 常見錯誤

1. **❌ 揭示後忘記更新 plateInfo**：只播了動畫但 symbolId 沒改 → 後續對獎/Collect 讀到 Mystery symbolId 而非實際符號 → 邏輯錯誤
2. **❌ 把 server-only 型（far_west）也寫揭示邏輯**：far_west 的 Mystery 不下發 mysteryPositions，client 寫動畫邏輯等於 dead code 且永遠不觸發
3. **❌ 揭示順序放在 Collect 之後**：正確順序是 Mystery 揭示 → 再做 Collect；反過來會導致 Mystery 格沒被收（Collect 看到的還是 Mystery ID）
4. **❌ 把 Mystery 和 MysteryEvent（逐格重轉）混為一談**：前者是單純揭示（0.5s 動畫），後者是完整重轉流程（需獨立 State + server 再次回傳結果），兩者 proto 結構和流程完全不同
5. **❌ FakeReel 帶放入 Mystery sprite**：far_west 型 Mystery 在 client 無 sprite 資源（Symbol=98 是 server 專用），FakeReel 顯示會報錯
