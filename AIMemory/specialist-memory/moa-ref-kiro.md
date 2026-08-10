- [2026-08-10T05:08:31.815Z] (設計問題：telegram-kiro-bridge 的 run_plan 目前有一個靜默失效：plan-template) [auto-summary] ge 可以）
3. **降級仍是成功路徑** — 題目說「全綠完成」，所以 `_fallback` 不應該是錯誤，只是事實陳述
4. **plan-template 的 `specialist` 欄位是 domain 名稱字串** — 若是其他格式（陣列、物件），解析邏輯要調整

### 4. 這個方案什麼情況下是錯的選擇

1. **呼叫端需要程式化處理降級事件** — `_fallback` 只是事實陳述，沒有錯誤碼或型別標記，不方便寫 `if (result._fallback.length > 0)`
2. **需要細粒度控制每個 step 的降級策略** — 此方案一律退回 gene
