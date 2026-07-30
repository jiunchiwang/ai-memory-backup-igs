---
name: uk-slot-spec-to-impl
description: 已停用（2026-07-30 併入 uk-slot-codegen）。保留為指標，不要直接使用；從規格書開新 slot 專案一律走 uk-slot-codegen。
type: skill
domain: slot
created: 2026-07-06
deprecated: 2026-07-30
superseded_by: uk-slot-codegen
tags: [uk-slot, spec, workflow, milestone, deprecated]
source: session
---

# uk-slot-spec-to-impl（已停用）

⛔ **本 skill 已於 2026-07-30 併入 `uk-slot-codegen`，請改用該 skill。**

## 為什麼合併

兩個 skill 的觸發詞完全重疊（「從規格書開新 slot 專案」），同時維護會內容漂移。
`uk-slot-codegen` 已有兩款遊戲的實戰驗證，且已吸收本 skill 的三個步驟。

## 對照表

| 本 skill 原有 | 現在在哪 |
|---------------|----------|
| 步驟 0 前提確認（含「基準永遠是模板不是衍生品」） | `uk-slot-codegen/_flow.md` → Pre-0 |
| 步驟 1 xlsx 轉換 + 檢查點 1 | `uk-slot-codegen/_flow.md` → Pre-A |
| 步驟 2 差異開發規格（🟢🟡🔴 + proto 映射）+ 檢查點 2 | `uk-slot-codegen/_flow.md` → Pre-B |
| 步驟 3 milestone 拆解（M0a~M4） | `uk-slot-codegen/_milestones.md` |
| M0a 起專案（git archive + FirstClone.bat） | `uk-slot-codegen/_milestones.md` → M0a 起新專案 |
| 自產 proto stub 路徑 | `uk-slot-codegen/_milestones.md` → Proto Stub 路徑 |
| 下游 skill 對照表 | `uk-slot-codegen/_milestones.md` → 下游 skill 交棒表 |
| 常見錯誤（流程偏離 + 技術） | `uk-slot-codegen/SKILL.md` → 常見錯誤 |

## 一個行為差異要注意

原本兩個人工檢查點是 `⛔ 不可跳過`（阻擋式）。`uk-slot-codegen` 是無頭 pipeline，
設計成一口氣跑完不停等，所以檢查點降級為「不擋路但必須逐項輸出，並收進 Step 5 Report
的『人工檢查點待確認』區塊」。要人工把關的話，看 report 那一節。

完整歷史內容見 `git show c8b68a7:skills/slot/uk-slot-spec-to-impl/SKILL.md`
（`c8b68a7` 本身就是合併前的最後一版）。
