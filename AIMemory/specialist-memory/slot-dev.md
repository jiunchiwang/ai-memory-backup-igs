- [2026-07-09T03:48:10.729Z] (目標與動機：用 uk-slot-codegen skill（位於 ~/.kiro/skills/uk-slot-code) [auto-summary] 覆寫修正後最終 Game_Define.ts 正確，但 spec_adapter 本身需修正。

**B 節結論**：Probe enum 28 個符號依規格書 ODDS 表 idx 正確建立；SCATTER_SYMBOL 選 SC_SUPER（idx=21）作為 NearWin 代表合理但不完整，3 色 Scatter（idx 18/19/20）不在計數範圍內，正確做法應改用已同步定義的 `SCATTER_SYMBOLS[]` + `.includes()` 判斷。

**C 節結論**：R1~R6 custom feature 偵測清單與 dev-spec.md 🔴 清單**完全對應**
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) 審查 uk_slot_clash_of_olympus M2.2 VS proto mock adapter 設計：建議把轉換邏輯放在 VSManager.ts 內的純函式（保持 ts-node 可測），並發現現有 GameView mock 有兩處會讓 Resolve() 恆不觸發的 bug，需與 adapter 一併修正
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) AdaptRoundToVSInput() 應為 VSManager.ts 內的 exported pure function（type-only import colProto），VsFeatureShowState 只做呼叫+播放+plateAfter 寫回顯示層
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) GameView.ts:908-912 的 vsfeature mock：col0 用轉型後符號 VsCollect(18) 而非 Collect(15)、VSResult 缺 reelIndex，兩者疊加會讓 VSManager.Resolve() 恆回傳 isTriggered=false
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) VSManager.Resolve() 回傳的 plateAfter 目前沒有任何寫回顯示盤面或 CollectFeatureShowState 的機制，是 M2.2 必須釘的整合缺口
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) proto IVSResult.vsType 為 number，其編碼語意（symbol id vs 獨立 enum）未定案，僅有 mock 先例可循，應登記 spec-gap
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) M2.1 設計文件（安全略過）與 dev-spec.md 規格權威 S1（warn 不改行為）對「類型不符」措辭不一致，雖因欄位互斥實務不會觸發，仍建議對齊文件用字
- [2026-08-13T12:16:03.386Z] (請 code review G:\Cocos_Project\uk_slot_clash_of_olympus 目前未提) [auto-summary] 狀態，不會殘留上一局的值。
3. **mock 可觸發真正 Resolve()** — 逐行手動追蹤 `'vsfeature'` mock 資料流過 `AdaptRoundToVSInput → VSManager.Resolve`，確認 `isTriggered=true`；這修正了上一輪設計審查抓到的兩個 bug（VSResult 缺 reelIndex、col0 誤用轉型後符號）。另外實跑 `tests/VSManager.test.ts` 9 案例全過，`npx tsc -p . --noEmit` 篩選這三個檔案 0 錯誤。

殘留風險（均非本切片範圍內的 bug，僅記錄供後續實作留
