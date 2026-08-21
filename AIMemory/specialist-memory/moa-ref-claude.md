- [2026-08-10T05:08:31.813Z] (設計問題：telegram-kiro-bridge 的 run_plan 目前有一個靜默失效：plan-template) [auto-summary] 點不存在，此方案需要額外的回流路徑。

---

### 什麼情況下這是錯的選擇

- **整合 LLM 會忽略或縮寫 prompt 前綴**：這是 prompt injection 式的可見性，不是程式碼層保證。若整合者的 system prompt 有「精簡輸出」指令，通知可能被吃掉。更強的做法是讓 bridge 程式碼在整合結果之後直接 append，完全繞過 LLM 判斷。
- **呼叫端需要的是機器可讀的降級狀態**（非人類可讀文字）：此方案輸出是文字，若下游要做條件判斷，仍需解析。
- **降級很頻繁**：每次都在整合結果塞通知會讓輸出雜訊化，使用者開始忽略它，等同沒有可見性。**
- [2026-08-21T01:04:46.519Z] (設計問題：目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dre) [auto-summary] 什麼情況下這是錯的選擇

- ACP 協定不支援 per-request system inject，只能在 session init 時設定 → 方案在架構層就死掉，必須回到 session 層操作。
- 使用者需要的是跨多輪持續的人格（例如「整個 /dream 對話過程中都保持角色」），per-request inject 每輪都要帶入，且若中間有 extraction 觸發，仍有窗口問題。
- 現有 Stage 1 已有大量測試（BC-13～BC-33）綁定 session 層行為 → 遷移成本可能比從零建新機制更高，特別是那些 carve-out 的邊界測試。
- 若未來人格需要影響 
