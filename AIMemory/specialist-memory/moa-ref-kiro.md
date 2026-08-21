- [2026-08-10T05:08:31.815Z] (設計問題：telegram-kiro-bridge 的 run_plan 目前有一個靜默失效：plan-template) [auto-summary] ge 可以）
3. **降級仍是成功路徑** — 題目說「全綠完成」，所以 `_fallback` 不應該是錯誤，只是事實陳述
4. **plan-template 的 `specialist` 欄位是 domain 名稱字串** — 若是其他格式（陣列、物件），解析邏輯要調整

### 4. 這個方案什麼情況下是錯的選擇

1. **呼叫端需要程式化處理降級事件** — `_fallback` 只是事實陳述，沒有錯誤碼或型別標記，不方便寫 `if (result._fallback.length > 0)`
2. **需要細粒度控制每個 step 的降級策略** — 此方案一律退回 gene
- [2026-08-11T15:19:00.892Z] (目標與動機：對 git commit 9897f46 做 push 前的獨立覆核。你是跨 vendor 的異源覆核者（g) [auto-summary] reaking change；若從未使用，也應說明如何確認。

---

## Finding 5 (medium)

**檔案與行號**: 整體 diff

**問題敘述**: 作者主張「--effort 在 CLI 層完全不驗證，帶不存在的值照跑且 exit 0」，但**未見任何測試程式碼**證明此行為。若此主張為真，應有對應的測試或 log。

**逐字證據**: diff 無測試檔案。

**建議修法**: 新增 `tests/effort-validation.test.ts` 或於 commit message 附測試指令與輸出。

---

## 我實際跑過的指令清單

```

- [2026-08-21T01:04:46.519Z] (設計問題：目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dre) [auto-summary] 都走 session manager，所以清洗點集中在 extraction。

### 這個方案什麼情況下會是錯的選擇

1. **人格不只是語氣，而是「身分」**——例如「你是這位使用者的秘書」，會改變 LLM 對「哪些資訊重要」的判斷。清洗後抽出的事實會跟「秘書人格下的對話」不一致，長期記憶會變成「兩個人格混合」。

2. **有其他寫入 facts 的路徑**——例如 `/dream` body 裡 LLM 自己決定呼叫 `remember()`、或其他 command 也會觸發 extraction。那時要補的清洗點會變多，最終可能比現在的 carve-out 還複雜。

3. **
