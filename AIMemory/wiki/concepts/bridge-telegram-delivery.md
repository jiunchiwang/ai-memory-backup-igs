---
title: Bridge Telegram 出站投遞（排版、重試、重複投遞、重放安全性）
type: concept
created: 2026-08-21
updated: 2026-08-21
sources: [f_b35b6b, f_6dffc5, f_565fbf, f_5eaaed, f_b5d499, f_18f02e, f_e04f09, f_aff418]
---

# Bridge Telegram 出站投遞

2026-08-21 從 [[bridge-project]]（原 268 行）拆出。範圍是**訊息離開 bridge 之後那條路**：怎麼排版、失敗怎麼重試、以及重試／重放會不會把同一則送兩次。與 [[bridge-streaming]] 的分界線是**draft lifecycle vs 投遞語意**——那一頁講 draft 三階段、4096 截斷、429 限流節奏，本頁講 at-most-once。

## 訊息排版

Telegram 訊息用 HTML parse_mode（`src/format-html.ts`，Markdown → Telegram HTML）。**選 HTML 而非 MarkdownV2**：agent 輸出常含 `_ * [ ]`，MarkdownV2 跳脫太嚴會大量 400 error；HTML 只需 escape `<>&`。每個 `editMessageText` 都有 strip-tags fallback。送 `.md` 檔改用 `.txt` 顯示名解決 in-app viewer 中文亂碼。

## 重試與 Instrumentation（2026-08-14~16）

- **`planUncertainReplay` 的限制**：該函式對「送出結果不明」的待重送訊息加上不確定性前綴，前綴後若超過 `TELEGRAM_MESSAGE_LIMIT` 就拆成「通知 + 原文」兩則，但**前提是 text 本身不得超過 limit**——超過時它不會也無法補救。不代為 split 的理由：多一個切塊實作＝多一個會與既有 `splitForTelegram` 漂移的來源，切塊是呼叫端的責任；且「超長訊息→400→入列→永遠送不出」的迴圈**先於**本護欄即存在。
- **重試行為的參數不可在「只看得到失敗重試」的儀器上調整**（2026-08-15 分析 31 天事件 log）：現行 instrumentation 只記錄失敗的重試，成功的重試根本不入帳 ∴ 重試成功率**結構上不可觀測**（存活者偏誤）。裁決是先補上成功重試的遙測，把行為調整延後到能量到成功率之後。

## 重複投遞四層修復與重放安全性判準（2026-08-14/15）

異源覆核（Codex `gpt-5.6-sol`）用開放式問題「同一個缺陷形狀連續往上跑了三層，第四層在哪」逐層挖出重複投遞鏈，四個 commit 依序修完：

1. **`ff976f6`** — grammY `autoRetry` 的 `rethrowHttpErrors` 預設 `false`，HttpError 走 `call()` **內層** while 迴圈，`remainingAttempts` 只在**外層** do-while 遞減 ∴ 傳輸層失敗是**無界重試**（`maxRetryAttempts` 管不到）。改用 Cloudflare 的判準——**看操作不看錯誤**：唯讀/冪等方法有界重試，每次產生新內容的方法（`sendMessage` 等）不重試原樣拋出，未列到的方法 default-deny。
2. **`c8f7ddd`** — 上一層建立的保證被上層 catch-and-requeue 抵銷（transformer 層擋掉的重複投遞被上層放回佇列）；順帶發現 pending queue 沒有自己的排空觸發器（只搭 429 恢復的便車）與 flush 無併發防護（`shift`/`unshift` 之間有 `await`，兩路並行會交錯送出同一筆）。
3. **`c7bfca3`** — 訊息拆成兩則後，前段成功但後段失敗時整筆放回佇列重試，導致已送出的那則再送一次。
4. **`2406c4f`** — `trySendRichMessage` 的裸 `catch { return undefined; }` 把「可能已送達」翻譯成「沒送出」，呼叫端補一則 plain message ⇒ 兩則持久訊息且第二則不帶標記；而 `TG_RICH_STREAM_ENABLED` 預設開啟 ∴ **前三層修法在預設路徑上大多被繞過**。

⚠️ **「不是恆真斷言，但 safety property 定義錯」比恆真更難抓**：其中一條回歸測試（R10）曾把「重送整筆放回佇列」這個錯誤行為釘成 expected output，突變測試全綠——突變測試只能證明斷言有被執行到，**不能證明斷言守的是對的性質**（見 [[gate-mutation-testing]] 的能力上限那節）。抓到它的是異源覆核讀懂測試在驗什麼，不是機械檢查。

`docs/SPEC-replay-safety-audit.md` 記錄三條可複用判準與兩條未修項：

| 判準 | 內容 |
|---|---|
| **R-A** | 看操作不看錯誤——錯誤分不出「送出前失敗」與「送出後失敗」，判準要落在**操作重放會不會產生新副作用** |
| **R-B** | allow-list 而非 deny-list |
| **R-C** | 保證要沿層傳遞——第 N 層建立的 at-most-once，若第 N+1 層把錯誤翻譯成「確定沒發生」就歸零 ∴ **每建立一個保證必須往上追一層** |

兩條 high severity 未修（**H-1** ACP 整輪 prompt 重放含工具副作用、**H-2** `/job resume` 無 per-run lease）**選擇開案不動手**：各自要碰的是承重核心（session/turn 重試語意、lease 與持久化狀態），該先設計再動手，不該接在已疊四層的 commit 後面繼續加。

順手更正兩則自己的事實錯誤：`PlanRunStepStatus` 是 `pending | done | failed | timeout | blocked | expanded`，**沒有 `running`**（run 層級才有）；`scheduler.ts` 檔頭曾有假契約「crash 會 re-fire」，實際是 `schedule-store.ts` 的 `load()` 對過期 recurring entry 往前滾到下一個未來 tick、one-shot 進 `missed` 並丟棄，**不會重放**。

**順帶更正 transformer 安裝順序**：文件先前宣稱「護欄裝在 autoRetry 之前會造成 silent total failure」是錯的——grammY 的 `bot.api.config.use()` 是 `reduce(concatTransformer, this.call)` ∴ **後裝的在外層**。重試護欄裝在 autoRetry 之後有好處（自己發動的重試會重新經過 429 處理），但這點**不承重**，因為 `rethrowHttpErrors: true` 已保證非冪等方法只嘗試一次，順序對調只差 429 那一項。

驗證：full tier 159/159（含 3 支平常被 `--fast` 跳過的慢測試）+ mutate-gate 12/12 killed。五個 commit（`e914f21..0db8132`）已 push origin/main。

## 相關

- [[bridge-project]] — 母頁：bridge 本體架構與子系統索引
- [[bridge-streaming]] — draft lifecycle、4096 截斷、429 限流節奏
- [[bridge-draft-diag]] — draft 重播的三個獨立成因與診斷探針
- [[gate-mutation-testing]] — 突變測試證明得了什麼、證明不了什麼
- [[adversarial-review]] — 「缺陷逐層上移」這個輪次結構的完整記錄
