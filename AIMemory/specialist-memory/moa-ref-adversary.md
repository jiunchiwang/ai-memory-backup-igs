- [2026-08-11T15:19:00.893Z] (目標與動機：對 git commit 9897f46 做 push 前的對抗式覆核。你的任務不是確認作者對，而是盡力找出) [auto-summary] 些測試是在這次改動之前就存在的，它們通過只說明「沒有回歸」，不說明「新加的 fallback 值和 description 文字是正確的」。BC-17 不斷言 effort 作者也知道。commit message 裡若寫「綠燈」卻沒說明綠的是哪些斷言、這些斷言覆蓋不到新增的行為，讀者會以為有測試背書。

**這不是 block 級的問題**，但 commit message 應加一句「本次改動無對應新測試斷言，綠燈僅代表無回歸」。

---

## 我攻擊過但沒破的角度

- **tsc 報錯**：改 fallback 陣列的型別只要是 string literal union 的子集就不會
