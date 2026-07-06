---
title: UK Slot 踩坑經驗
type: lesson
created: 2026-06-23
updated: 2026-06-27
sources: [f_89a745, f_46f6e0, f_94500e, f_e9bd6a]
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
## 相關

- [[uk-slot]] — 專案群總覽與技術棧約束
