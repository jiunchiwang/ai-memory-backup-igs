- [2026-08-11T15:19:00.893Z] (目標與動機：對 git commit 9897f46 做 push 前的對抗式覆核。你的任務不是確認作者對，而是盡力找出) [auto-summary] 些測試是在這次改動之前就存在的，它們通過只說明「沒有回歸」，不說明「新加的 fallback 值和 description 文字是正確的」。BC-17 不斷言 effort 作者也知道。commit message 裡若寫「綠燈」卻沒說明綠的是哪些斷言、這些斷言覆蓋不到新增的行為，讀者會以為有測試背書。

**這不是 block 級的問題**，但 commit message 應加一句「本次改動無對應新測試斷言，綠燈僅代表無回歸」。

---

## 我攻擊過但沒破的角度

- **tsc 報錯**：改 fallback 陣列的型別只要是 string literal union 的子集就不會
- [2026-08-13T10:56:28.690Z] (審查對象：G:\Cocos_Project\uk_slot_clash_of_olympus\docs\M2-VS-de) [auto-summary] 則，但設計文件若只說「以 server 為準」卻沒有明確指出：當 client 端推算結果與 server 不一致時**由誰負責偵測、在哪個時序**——這條原則就只是口號。失敗情境：client 用本地狀態決定動畫播放，server 回的 VS 結果延遲到達，兩者已對分岔，卻沒有 rollback 機制。

**推測 3：「純資料解析」的邊界滲漏**
設計刻意排除 Cocos State、動畫、RoundWin——但 VS 分數計算通常需要知道「當前 round 是否已結算」，若 M2.1 的 parser 拿不到 RoundWin 狀態卻又需要判斷收分時機，它會偷偷耦合進去，只是藏得更深。

- [2026-08-13T12:17:27.165Z] (根據兩份 M2.2 code review，請判定 G:\Cocos_Project\uk_slot_clash_of_) [auto-summary] VSInput` 的 `raw.reelIndex` 在 strict 模式下 possibly-null，執行期安全，但若日後切 `strict: true` 需補型別斷言。

### Evidence

1. 第一份 review：RoundInfo 不可變性、VsFeatureResult 跨局不殘留、mock 可觸發 Resolve() — 三項驗收點全過，0 High/Medium finding，9/9 unit tests PASS，tsc 0 error（目標三檔）。
2. 第二份 review：`IsValidReel` 的 filter 行為與 dev-spec.md:19
