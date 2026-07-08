---
name: rich-messages-upgrade-verdict
description: Rich Messages draft 化升級 PoC 結論 — @grammyjs/stream append-only 語意否決 1.5-2h 快速路線；小 bug 已修（ce0e1ac）
type: project
---

Rich Messages 升級 PoC 裁決（2026-07-08）：原「grammY @grammyjs/stream 1.5-2h 接上」方案**不成立**，改為只修小 bug。

**Why**（PoC 靜態驗證，讀 plugin 型別/源碼確認）：
- R-1 ❌：plugin 是 **append-only 累積**（yield 過的 chunk 收不回），與 bridge「整 buffer 重跑 transform → 整份 replace」的 streaming token 模型完全不相容；draft 化需重寫成 hold-back incremental emitter（偵測 `<<` opener 暫停 yield 等 close）＝大型任務，須 `/dev-design` 起步
- R-2 ✅：`replyWithMarkdownStream` 回傳 RichMessageMessage（有 message_id）、`otherRichMessage` 支援 reply_markup — ASK keyboard 可行
- R-3：`editMessageText` 官方就收 `rich_message` 參數（Bot API 10.1），現有 renderer 是合法 rich 渲染、只缺 draft 動畫；grammY `api.raw` 是 Proxy → typeof guard 對真 API 是死碼
- Draft 僅限 private chat；「不受 429」是誤解 — plugin 依賴 autoRetry，收益是 draft 幀可跳不丟資料，final 照樣限流

**How to apply**：
- 已修（ce0e1ac）：`tryEditRichMessageDraft` 內部 catch 回 false → 呼叫端自然退 plain edit，防 editNow 整幀丟失
- 日後若做 draft 化：從 `/dev-design` 開，核心是 hold-back emitter + 無 placeholder 流程 + 保留 relay/group plain path；勿再引用「1.5-2h」估計（f_a0d9ac 的估計已被 PoC 否決）
- 已列 roadmap：`docs/pending-roadmap.html` Section 7 更新為 PoC 裁決版，P2 / 大型（b265a72）
