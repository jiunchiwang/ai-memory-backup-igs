---
title: Telegram-Kiro-Bridge 踩坑經驗
type: lesson
created: 2026-07-16
updated: 2026-07-16
sources: [f_6a2483, f_90a25d, f_4c12ce, f_e72b07, f_651a0d, f_6a6988]
why: 因為 bridge 開發中反覆遇到環境變數繼承、merge 衝突、rate limit、unhandledRejection 等隱性陷阱，所以蒐集防護模式
---

# Telegram-Kiro-Bridge 踩坑經驗

---

## 1. dotenv 不覆蓋既有環境變數

**症狀**：`.env` 改了值，重跑 smoke test 仍讀到舊值；bridge spawn 的子 shell 繼承空字串 `TELEGRAM_BOT_TOKEN=""`，`config.required()` 拋錯。

**根因**：`node --env-file`（及 dotenv）不覆蓋 process 中已存在的環境變數——bridge spawn 的 agent subprocess 繼承父 process 的舊 env。

**對策**：
- 測試 `.env` 改動時用顯式變數覆蓋（`$env:VAR="val"; node ...`）模擬重啟後行為
- 需要真正更新的場景→重啟 bridge process（不是只改 .env）

---

## 2. git checkout --theirs/--ours 整檔取代

**症狀**：merge 解衝突後，被選中的一側有改動消失。

**根因**：`git checkout --theirs file`（或 `--ours`）是整檔取代，會洗掉對側已乾淨自動合併的 hunk。combined diff 不顯示乾淨 hunk，所以看不出被洗掉了什麼。

**對策**：
- 雙邊都有改動的檔案→`git merge-file` 三方合併或 `checkout -m` 恢復衝突標記後只改衝突區
- 逐檔 `diff` 兩側核對無遺失
- 共同祖先烘焙進衝突標記造成假衝突→採清理完整的一方

---

## 3. unhandledRejection 全域殺 process

**症狀**：新增的 HTTP server handler 丟一個未捕捉的 async 錯誤，整個 bridge 掛掉。

**根因**：`index.ts` 的全域 `unhandledRejection` handler 會 `process.exit(1)`，任何同 process 的 async callback 未捕捉 throw 都會殺掉整個 bridge。

**對策**：新增 server/handler **必須自帶錯誤邊界**（try-catch 或 `.catch()`），不能仰賴全域兜底。

---

## 4. Telegram .md 檔中文亂碼

**症狀**：送 `.md` 檔給 Telegram，使用者打開是亂碼。

**根因**：Telegram in-app viewer 對 `.md` 副檔名的 UTF-8 偵測不可靠（尤其含中文時）。

**對策**：送 `.md` 內容時 InputFile 第二參數用 `.txt` 顯示名，強制 Telegram 以純文字開啟。

---

## 5. Draft TTL 過期訊息消失

**症狀**：rate limit 期間 streaming 訊息從使用者畫面消失，恢復後只看到新的。

**根因**：Telegram draft 有 30s TTL，rate limit 期間無法 edit 續命，draft 過期後 `editNow()` 失敗——如果沒有 placeholder 備援，訊息就消失了。

**對策**：`editNow()` 中 `trySendDraft()` 失敗且無 placeholder 時，用 `sendMessage` 建 placeholder 並降級為 placeholder 模式（`useDraftMode=false, draftId=0`）。

---

## 6. grammY api.raw Proxy 能力偵測陷阱

**症狀**：用 `typeof api.raw.someMethod !== 'function'` 做能力偵測，條件永遠為 false（認為支援），呼叫後才 API error。

**根因**：grammY 的 `api.raw` 是 ES Proxy，任意屬性名都回傳 callable function。`typeof` 檢測是死碼。

**對策**：真正的 API 不支援偵測要靠 `try { await api.raw.method() } catch(e) { ... }` 錯誤捕捉，不能用 property 存在性判斷。

---

## 7. 共用 module-state 洩漏要同類掃描

**症狀**：修了 `atomicWriteJson` 的 pending-by-path 洩漏，但同一檔的 `updateJson` 有相同問題沒修到，回歸測試才發現。

**根因**：module-scope 共享狀態（如 `writePendingByPath`）的寫入端通常不只一個，只修一個進入點會遺漏。

**對策**：修 module-state 洩漏時→同類掃描同檔所有寫入端。先 grep 再改，不要改完才想到。

---

## 8. check-preamble.mjs 空 facts 量測失真

**症狀**：`check-preamble.mjs` 報 ceiling FAIL，但數字遠大於真實 preamble。

**根因**：facts 為空時 memory block header 不渲染，`indexOf` 找不到錨點→fixed core 計算涵蓋整份 preamble（7783 vs 真實 5884）。

**對策**：空 facts 環境跑到 ceiling FAIL 時先想到此原因；腳本用真實 facts 跑不受影響。

---

## 9. /goal + <<ASK>> 無條件推進

**症狀**：`/goal` 迴圈或 `<<CONTINUE>>` 排程的 continuation 在該輪有 `<<ASK:...>>` 按鈕時仍 500ms 後推進，使用者選擇形同虛設。

**根因**：continuation 排程完全不看該輪有沒有 emit ASK token。

**對策**：ASK-aware 排程——新增 `GOAL_ASK_WAIT_MS`（預設 10 分鐘）與 `turnHadAsk` 旗標，有 ASK 時暫停推進等使用者回應。

---

## 10. /backup 意外推送診斷 trace

**症狀**：`/backup` git push 帶進了 `acp-trace/` 資料夾（ACP JSON-RPC debug trace），可能含完整對話內容。

**根因**：AIMemory backup job 的 `excludeDirs` 原本只排除 `transcripts/shared`，未排除 `acp-trace`（`ACP_TRACE=1` 時產生）。

**對策**：`excludeDirs` 加入 `acp-trace`。新增任何可能含敏感內容的資料夾時→立即更新 backup exclude 清單。

---

## 11. SELF_EVAL 跨 backend 設計的 6 個通用缺陷

**情境**：設計跨 ACP backend 的自評機制時，對抗性審查否決三個方案。

**通用缺陷清單**（可作為未來設計自評/評分機制的檢查表）：
1. tsc 型別驗證可被 agent 謊報低分繞過
2. 觸發條件可能與不同 backend 已知限制互相矛盾
3. circuit breaker 整合的前提條件未經驗證
4. 沒有證據顯示 backend 真的會遵守自評指令
5. 未驗證的實作細節被當成行為契約使用
6. 巢狀 payload 會破壞既有的扁平欄位慣例

---

## 相關

- [[bridge-project]] — Bridge 專案架構總覽
- [[bridge-streaming]] — Streaming 與 rate limit 機制
- [[bridge-memory]] — 記憶維運系統
- [[bridge-acp]] — ACP adapter 切換與陷阱
