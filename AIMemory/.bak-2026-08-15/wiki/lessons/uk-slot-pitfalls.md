---
title: UK Slot 踩坑經驗
type: lesson
created: 2026-06-23
updated: 2026-07-09
sources: [f_89a745, f_46f6e0, f_94500e, f_e9bd6a, uk-slot-codegen skill]
why: 因為 Cocos Layout/Promise.all/node 退場的隱性行為導致視覺 bug 和 race condition，所以記錄防護模式
---

# UK Slot 踩坑經驗

---

## 1. cc.Layout 退場重排（WantedPoster）

**專案**：uk_pirates_queen
**症狀**：ReconcileCascade 退場時，懸賞令（WantedPoster）使用 `cc.Layout` 自動排版，`node.active = false` 瞬間觸發 Layout 重排，畫面跳動突兀。

**根因**：Layout 元件在子節點 active 狀態改變時會立即重新計算排版，退場動畫還沒播完就已經位移。

**對策**：
- 退場前先把節點移出 Layout 管轄（或改用手動定位）
- 或先播完退場動畫再設 `active = false`

---

## 2. Promise.all 前同步決策的 Race Condition

**症狀**：在 `Promise.all` 之前的同步階段計算狀態決策（如 `willGhost`），與並發的 group dispatch 產生競態，導致決策時讀到的狀態已被其他並發分支改動。

**根因**：同步計算完成 → 進入 `Promise.all` → 其他 promise 改了共享狀態 → 先前的決策結果已過時。

**對策**：
- 把依賴共享狀態的決策移到 **async 階段**（在各自的 promise 內）計算
- 確保決策時讀取的狀態不會被並發分支覆寫

---

## 3. Ghost Slot 雙佔位防跳動

**症狀**：Cocos Layout「兩項移除一項」時，剩餘項瞬間置中造成視覺跳動（snap）。

**根因**：Layout 計算只看 active children 的數量與尺寸，移除一項後剩餘項立即重新定位。

**對策**：Ghost slot 雙佔位機制——
- 移除的項目不真正移除，改用不可見的 ghost node 佔住原位
- 同時滿足：0→1 置中、2→1 不跳動、旋轉相容
- 不需修改 Layout 參數


---

## 4. Drop-Out 動畫凍結視窗回歸（Pirates Queen）

**專案**：uk_pirates_queen
**症狀**：掉落動畫（drop-out）播完後視窗仍處於凍結狀態，或在不該凍結時被凍住。

**根因**：把「凍結語意」（`m_isInDropMode`）與「掉落動畫 promise」（`m_dropAllSymbolsOutOfScreenPromise`）混為一談，且掉落觸發直接寫在 `StartSpin`（約 L943）——職責過度耦合。

**對策**（MVP 最小手術方案）：
- 新增 `m_isInDropMode` 布林**專職凍結語意**
- 把 promise 降級為純動畫 handle（不再承擔凍結控制）
- 把掉落觸發從 `StartSpin` 移到獨立的 `TriggerDropOut()` method

**防護**：凍結語意與動畫 handle 永遠分開管理，避免「完成動畫 = 解除凍結」的隱含假設。

---

## 5. UTF-8 BOM 丟失 → Cocos 不產 chunk [src: uk-slot-codegen]

**症狀**：改完 .ts 後 runtime 報 `__unresolved_X`，Cocos Babel parser 報 `InvalidEscapeSequenceTemplate`。

**根因**：Template .ts 是 UTF-8 with BOM（EF BB BF），`strReplace` / `WriteAllText` 類工具寫回時丟 BOM。

**對策**：改既有 .ts 用 byte-level 操作（ReadAllBytes → 轉字串 → Replace → WriteAllBytes）保留 encoding。grep 看到 `?�` 亂碼 = 檔案已損壞，從 template 重新複製。

---

## 6. SYMBOL_COUNT 禁動態計算 [src: uk-slot-codegen]

**症狀**：`Object.keys(Symbol).filter(...)` 算符號數，本機正常、build 後 runtime = 0。

**根因**：Cocos bundler tree-shake 把 enum 反查代碼搖掉。

**對策**：SYMBOL_COUNT 一律硬編碼數字，gate 驗證 enum member 數量與之相符。

---

## 7. Spine placeholder 必須用 .json [src: uk-slot-codegen]

**症狀**：自產 .skel binary placeholder 永遠載入失敗。

**根因**：Cocos 3.6.2 對 `.skel` 副檔名強制 binary parser，不做 JSON fallback；自產 binary 格式從未成功。

**對策**：placeholder 用 .json 格式 + keyframe 帶位移（`x: 0.01`，否則不觸發 complete）；正式美術交付後直接換 .skel。

---

## 8. Mock 資料欄位不完整 → 報獎整段被跳過 [src: uk-slot-codegen]

**症狀**：Mock spin 正常轉，但 BigWin / 報獎永遠不觸發。

**根因**：mock IRoundInfo 缺 `RoundWin` → AwardState 的 `rate = undefined / bet = NaN` → `rate > 0` 為 false，整段報獎邏輯靜默跳過。陣列欄位給 undefined 也會 `.length` crash。

**對策**：每個 mock mode 都設 RoundWin；所有陣列欄位給空陣列；mock 物件加 proto type annotation 讓 tsc 攔缺欄位。

---

## 9. 規格書 "Scatter_XXX" ≠ 程式的 SCATTER_SYMBOL [src: uk-slot-codegen]

**症狀**：NearWin 永遠不觸發，或 FG 觸發判定錯符號。

**根因**：規格書常把 Feature Symbol 命名為 Scatter_Expand / Scatter_Bomb 等，但 `SCATTER_SYMBOL` 只放「觸發 FG / NearWin 累計」的那一顆。且 NearWinDetector 用 `===` 比對——SCATTER_SYMBOL 必須是單一 enum member，不可 array 或裸數字。

**對策**：判斷依據是「是否觸發 FG / 參與 NearWin」，不是名字；多種 Scatter 變體選一顆當門檻代表，需要全清單另開 `SCATTER_SYMBOLS` array。

## 相關

- [[uk-slot]] — 專案群總覽與技術棧約束
- `uk-slot-codegen` skill（同事的 codegen pipeline）— 條目 5~9 來源，完整踩坑見其 `_pitfalls.md`
