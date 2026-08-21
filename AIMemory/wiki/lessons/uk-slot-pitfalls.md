---
title: UK Slot 踩坑經驗
type: lesson
created: 2026-06-23
updated: 2026-08-17
sources: [f_89a745, f_46f6e0, f_94500e, f_e9bd6a, f_1e8a3d, f_931e5a, f_4ba968, f_ac39e3, uk-slot-codegen skill]
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

---

## 10. Cocos 生命週期回呼命名大小寫（2026-07-30 實證）

**專案**：uk_746_far_west_client
**症狀**：`eventManager` 從未 unregister，導致 memory leak 或事件重複觸發。

**根因**：UK slot 專案的「方法命名用大駝峰（PascalCase）」規範**不適用於 Cocos 引擎生命週期回呼**——`onLoad` / `start` / `onDestroy` / `update` 必須小寫，寫成 `OnDestroy` 引擎不會呼叫、變成死碼且無任何錯誤訊息。

**對策**：
- 生命週期回呼一律小寫（`onDestroy`），只有自定義方法才用 PascalCase
- 已確認 astarte-framework 無 `OnDestroy` 鉤子可用

---

## 11. Grep `m_XxxName` 漏私有欄位直寫（2026-07-30 實證）

**專案**：uk_pirates_queen
**症狀**：枚舉某狀態旗標的寫入點時漏掉一處。

**根因**：UK slot 專案慣例是 `public get/set PascalName` + `private m_pascalName`，程式碼可能直接寫私有欄位繞過 setter。

**實例**：`GameView.ts:2314` 直接寫 `m_isLockRotation = true`，搜 `IsLockRotation =` 只找到 4 筆、實際 5 筆。

**對策**：搜尋同時涵蓋 `m_` 前綴的 pattern，如 `[Mm]_?[Ii]sXxx`。

---

## 12. RenderTexture 凍幀報獎機制（RTCtrl）

**專案**：uk_pirates_queen、uk_746_far_west_client
**症狀**：搜 `screenshot` / `readPixels` 找不到截圖相關功能。

**說明**：這兩個專案有同源的 **RenderTexture 凍幀報獎機制**（`RTCtrl.ts` + `PerfGroup` prefab）——報獎期間把整個畫面渲成 RT 貼上、關掉底下實體節點省效能。這**不是存檔截圖**也沒有 `readPixels`，關鍵字是 `RenderTexture` / `RTCtrl` / `RT_EVENT`。

**版本差異**：
- **pirates_queen**：進化版（有資源釋放、view.off、resize 守衛、防閃順序、主相機快取、正確的 `onDestroy` 小寫）
- **far_west**：初版，缺上述 6 項保護措施，其中 3 項是真 bug

**對策**：新 slot 專案要移植 RT 凍幀**一律抄 pirates_queen 版**。其餘 9 個 slot 專案皆未使用此機制。

---

## 13. 跨專案搬 Spine 資產：「動畫解析成功」≠「畫得對」

**專案**：uk_872_eyestrike2_client → Clash of Olympus（2026-08-18；2026-08-21 從 [[uk-slot]] 移來當主場）
**症狀**：執行期檢查**可以全綠**——節點存在、動畫名正確、`hasSkeletonData` true、`findBone` 都拿得到——但畫面上的東西完全不在飛行路徑上。

**說明**：來源專案的做法是把控制骨移到起訖世界座標、路徑交給 Spine 動畫自己畫。原樣搬過來後骨頭座標仍依賴**來源專案的節點階層與縮放** ∴ 資料層的取樣結構上看不到這個錯。唯一抓得到的方法是**在飛行當下截圖**。

**對策**：借來的 Spine 只要牽涉「用骨頭／插槽帶座標」就必須**看畫面驗收**，不能用回傳值或屬性快照代替；退而求其次的穩健做法是讓路徑由自己已驗證的 tween 決定、Spine 只當跟著跑的視覺。

**同型陷阱**：視覺類懷疑（例如「壓暗是不是沒生效」）要造**對照組**（強制全套用再截圖比對），不要靠單張截圖的印象判斷。相關方法論見 [[verification-diagnosis]]。
