- [2026-07-09T03:48:10.729Z] (目標與動機：用 uk-slot-codegen skill（位於 ~/.kiro/skills/uk-slot-code) [auto-summary] 覆寫修正後最終 Game_Define.ts 正確，但 spec_adapter 本身需修正。

**B 節結論**：Probe enum 28 個符號依規格書 ODDS 表 idx 正確建立；SCATTER_SYMBOL 選 SC_SUPER（idx=21）作為 NearWin 代表合理但不完整，3 色 Scatter（idx 18/19/20）不在計數範圍內，正確做法應改用已同步定義的 `SCATTER_SYMBOLS[]` + `.includes()` 判斷。

**C 節結論**：R1~R6 custom feature 偵測清單與 dev-spec.md 🔴 清單**完全對應**
