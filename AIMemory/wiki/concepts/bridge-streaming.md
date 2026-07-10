---
title: Bridge Streaming 與訊息渲染
type: concept
created: 2026-07-11
updated: 2026-07-11
sources: [f_a0d9ac, f_5bb6fa, f_a1d087, f_56f3c9, f_1a58d7, f_7cfe9b, f_1867ae, f_de84a8, f_9792ce, f_43b977, f_ff9e43, f_330e15, f_192761, f_2a855c, f_131cef]
---

# Bridge Streaming 與訊息渲染

## 概述

telegram-kiro-bridge 的訊息輸出分為 streaming 階段（agent 仍在寫字）和 final render 階段。兩者共用同一個 transform pipeline（見 [[bridge-project]]），但面臨 Telegram Bot API 的 rate limit 和長度限制。2026-07-10 起正式採用 Draft API 三階段 lifecycle。

## Telegram Bot API 訊息格式

### Bot API 10.1 Rich Messages（2026-06-11）

- Block-based 結構化格式，21 種 RichBlock（段落/標題/表格/摺疊/LaTeX/地圖/媒體等）
- `sendRichMessageDraft` — 原生 streaming（30 秒 ephemeral draft、同 draft_id 動畫更新、僅限 private chat）
- Rich Markdown 輸入（相容 GFM）
- `editMessageText` 官方也接受 `rich_message` 參數（text/rich_message 二選一）

### Bot API 10.0（2026-05-08）

- Bot-to-Bot 原生通訊（bridge relay 已在用）
- 原生 Streaming Text（`sendMessageDraft`）

## Draft API 三階段 Lifecycle（commit e3a3a45）

```
[階段 1] sendMessageDraft(chatId, draftId, "")  → Thinking… 動畫
[階段 2] sendRichMessageDraft(chatId, draftId, content) → 全量替換+動畫過渡
[階段 3] sendRichMessage(chatId, finalContent, {reply_markup}) → 持久化，draft 消失
```

- `TG_DRAFT_ENABLED` env var 預設開
- relay/group 走現有 placeholder+editMessageText fallback
- 路徑選型：Path A Raw Draft API + Rebuild-Replace（非 hold-back emitter）

### 關鍵發現

- `sendRichMessageDraft` 同 draft_id 反覆呼叫 = 全量替換（非 append-only）
- 不存在 `editRichMessageDraft` 和 `finalizeRichMessageDraft`
- `@grammyjs/stream` 的 append-only 限制是 plugin 設計選擇，非 API 限制
- 原預估 500+ 行大型任務，實際走 Raw API 只改 ~180 行

## 訊息長度限制與截斷

### Telegram 4096 限制

- 限制對象：去除 HTML 標籤後的**純文字長度**（after entities parsing）
- 計算方式：UTF-16 code units
- bridge 使用 `TG_MAX = 3900`（留 ~200 字元安全邊距給 HTML 標記膨脹）

### 截斷策略（commit 718798e）

`renderReply()` 的 body budget 動態扣除 tools/thinkingBlock/cursor 已佔用長度：

```
bodyBudget = TG_MAX - overhead
overhead = tools.length + thinkingBlock.length + cursor.length
```

確保拼接後總長度不超過限制。工具狀態行增加時，body 可用空間相應縮小。

### Post-HTML 守衛（commit f9670c6）

`markdownToHtml()` 後若 HTML 長度超過 4096，fallback 到純文字（`parseMode: undefined`）。解決 markdown 密集內容 HTML 膨脹超限的邊界情況。

## Rate Limit 與 Draft TTL

### 429 Rate Limit

- 單一 chat 限制：~1 訊息/秒、edit ~1 次/秒
- `retry_after` 隨近期違規頻率累加（60s→183s）
- 限流期間唯一對策：安靜等待

### Draft TTL 過期修復（commit 75a5428）

Rate limit 期間 draft 30s TTL 會過期，訊息從使用者畫面消失。修復：`editNow()` 中 `trySendDraft()` 失敗且無 placeholder 時，用 `sendMessage` 建 placeholder 並降級為 placeholder 模式（`useDraftMode=false, draftId=0`）。

### Placeholder Guard 修復（commit df788dc）

`run-prompt.ts:991` 的前置 guard 漏排除 `useDraftMode`，draft mode 時 `placeholder` 故意為 undefined 卻觸發 throw。修正：加 `&& !useDraftMode` 條件。

## 業界 Streaming 策略比較

| 策略 | 代表實作 | 特點 |
|------|---------|------|
| Tail-truncation | 多數 bot | 超長截尾，簡單但丟資訊 |
| Force new message | 部分 bot | 超長開新訊息，碎片化 |
| Draft API | Bot API 10.0+ | 原生 streaming，30s TTL |
| Entity-aware split | GramIO `@gramio/split` | 操作 text+entities 而非 HTML 字串 |

grammY 和 Telegraf 都**沒有**內建 message splitter。`@gramio/split` 是目前最完整的方案。

## 常見陷阱

- `「sendRichMessageDraft 不受 429 限流」是誤解`：draft 幀可跳過不丟資料，但 final `sendRichMessage` 照樣受限流
- grammY 的 `api.raw` 是 Proxy — `typeof method !== 'function'` 做能力偵測是死碼，不支援偵測要靠 catch API 錯誤
- `@grammyjs/stream` 的 append-only 不等於 API 限制 — 查 Bot API spec 是關鍵轉折

## 相關

- [[bridge-project]] — Bridge 整體架構與 transform pipeline
- `ms-streaming-token-pipeline` — Streaming + final render 雙路共用 transform 的 skill
- `ms-telegram-bot-rate-limit-survival` — 429 存活指南 skill
