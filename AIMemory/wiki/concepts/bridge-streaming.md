---
title: Bridge Streaming 與訊息渲染
type: concept
created: 2026-07-11
updated: 2026-08-01
sources: [f_5bb6fa, f_a1d087, f_56f3c9, f_1a58d7, f_7cfe9b, f_1867ae, f_de84a8, f_9792ce, f_43b977, f_ff9e43, f_330e15, f_192761, f_2a855c, f_131cef, f_562fe5, f_867564, f_20c975, f_6551d6, f_7c00f6, f_a9f3cf, f_6f02c7, f_585d7f]
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

Rate limit 期間 draft TTL 會過期，訊息從使用者畫面消失。修復：`editNow()` 中 `trySendDraft()` 失敗且無 placeholder 時，用 `sendMessage` 建 placeholder 並降級為 placeholder 模式（`useDraftMode=false, draftId=0`）。

> ⚠️ TTL 數字更正（2026-07-31 實測）：**約 35 秒**，不是本頁與程式碼註解沿用的「~30s」。舊值偏保守但方向正確；詳見下節。

### Placeholder Guard 修復（commit df788dc）

`run-prompt.ts:991` 的前置 guard 漏排除 `useDraftMode`，draft mode 時 `placeholder` 故意為 undefined 卻觸發 throw。修正：加 `&& !useDraftMode` 條件。

## 2026-07-31 draft 重播診斷（根因未定案）

症狀（使用者報）：**「工具的訊息變化時，原本的對話會消失再從頭重跑」**——已串完的回覆整段消失、打字動畫從 0 重播。長回覆（1075 字）明顯，短回覆（37 字）幾乎看不出來。

### 兩批修法與它們的現況

| Commit | 修法 | 現況 |
|---|---|---|
| `5de4a15` | status 訊息改在**開 draft 之前**建立（抽出 `src/status-channel.ts` 的 open/update/close 契約） | 前提未成立（見下），但 eager open 本身無害 |
| `06191f8`→`d703bf3` | status bubble 接上 5 條 process 出口的有界 drain + `draining` 閂 | **與根因無關但正確**（孤兒 bubble 是真問題） |
| `4276f08` | `update()` 回傳「是否發出過 chat 層寫入」、把 status 寫入排到 draft 送出之前、`\|\| statusWrote` 強制補送（幀記 `reason:"status-restore"`） | **失去依據**——既未證明有效也未證明有害，多出來的只有 API 呼叫量 |
| `a895c24` | `editNowInner` 在 `await statusChannel.update()` 之後補 `if (turnFinalized) return` | **不管根因是什麼都對**（await 縫開 race，見 [[verification-diagnosis]]） |

修法選擇：採方案 A（讓 draft 永遠是最後一個 chat 層寫入 + 裸 status.edit 後強制補送），排除方案 B（keepalive 縮到 2–3s：只縮短空窗、不消滅重播，且 API 量暴增招限流）與方案 C（不開獨立 status bubble、把 tool/thinking 折回 draft 內容：UI 變動最大）。

### 實測推翻的前提（八臂 raw API 探針）

`scripts/probe-draft-clearing.mjs`（三模式：三臂／`--ttl`／`--frames`／`--md`）直接打 Bot API、不經 bridge，每臂送完刻意靜候不補送：

| 受測行為 | 結果 |
|---|---|
| `editMessageText` 編輯其他訊息 | **不清 draft、不重播** |
| `sendMessage` 送新訊息 | **不清 draft、不重播**（推翻「chat 收到任何一般訊息就清掉 live draft」這條被當成已證實的地基前提） |
| 靜候（單臂測 TTL） | 約 **35 秒**才消失 |
| 同內容重送 / 內容變短 | 不重播 |
| 純散文 append / code fence 開闔 | 平順 |
| markdown 表格逐行成形 | **此臂無效**——Telegram 原生不支援表格，永遠不會有半成品→成形的重排 |

∴ H1（`editMessageText` 清 draft）與 H2（TTL 過期，症狀時段最大間隔僅 19.6s vs TTL 35s）**都被實測排除**。八臂全負代表「raw API 重建不出症狀」，不代表症狀不存在。

三個附帶確立的操作事實：

1. **live draft 渲染在訊息區**（跟一般回覆串流同位置），不是輸入框——舊假設錯，導致第一輪三臂全在問錯地方
2. **keepalive 實際週期是 20 秒而非設計的 10 秒**：`setInterval` 跑固定 10s 網格，每次送出把 `lastDraftSentAt` 推到網格後約 0.8s，下一 tick 看到 9.2s < 10s 就走了**不落 log** 的 tooSoon 早退（`run-prompt.ts:808` 註解已預期「最壞 20s」）。35s TTL 下仍安全，屬 robustness 問題
3. **status 內容每個 tick 都在變**：`toolPrefixLines` 對執行中的工具算 `Date.now() - startedAt` 並以 0.1 秒精度渲染 → `update()` 的 identical 早退永遠走不到

### 診斷儀器（用完要關）

| 等級 | 落檔 | 內容 |
|---|---|---|
| `TG_DRAFT_DIAG=1` | `logs/draft-diag.jsonl` | 事件時序（`seq`/`event`/`sinceLastMs`/`reason`） |
| `TG_DRAFT_DIAG=2` | `logs/draft-frames.jsonl` | **每幀完整內容快照**（獨立旗標 `tgDraftDiagVerbose`；含完整回覆文字，隱私分量不同故分檔） |

兩檔靠 `seq` 對齊，等級 2 的新函式**刻意不自增 seq**（自增會讓兩檔序號各自漂移對不齊）。`logs/` 在 `.gitignore`。診斷完要關回 0 **並刪掉 frames 檔**（每幀 1KB+、每 turn 數十幀）。

⚠️ **兩種事件的時間戳語意刻意不對稱**：`status.edit` 記在 `await editMessageText` **之前**（`status-channel.ts:252`，註解寫明「動作發出的時刻才是因」），`draft.send` 記在 `await` **之後**。所以同一個 tick 在 log 裡會長成 `draft.send` 排在 `status.edit` 之前，**看起來像順序反了**——判斷順序必須讀碼，不能只讀 log 序號。

### 下一步

停止用 raw API 重建，改看真實生產資料：等級 2 已裝好，等症狀自然發生後 diff 出事的前後兩幀。也要接受一個可能：症狀或許是 client 端排版行為，那在碰不到的層，抓到幀也只能繞不能修。

## 業界 Streaming 策略比較

| 策略 | 代表實作 | 特點 |
|------|---------|------|
| Tail-truncation | 多數 bot | 超長截尾，簡單但丟資訊 |
| Force new message | 部分 bot | 超長開新訊息，碎片化 |
| Draft API | Bot API 10.0+ | 原生 streaming，TTL 實測 ~35s |
| Entity-aware split | GramIO `@gramio/split` | 操作 text+entities 而非 HTML 字串 |

grammY 和 Telegraf 都**沒有**內建 message splitter。`@gramio/split` 是目前最完整的方案。

## 常見陷阱

- `「sendRichMessageDraft 不受 429 限流」是誤解`：draft 幀可跳過不丟資料，但 final `sendRichMessage` 照樣受限流
- grammY 的 `api.raw` 是 Proxy — `typeof method !== 'function'` 做能力偵測是死碼，不支援偵測要靠 catch API 錯誤
- `@grammyjs/stream` 的 append-only 不等於 API 限制 — 查 Bot API spec 是關鍵轉折
- **「chat 收到一般訊息就會清掉 live draft」是未經實測的推論**，2026-07-31 已被探針牴觸；別再拿它當因果鏈的起點（詳見下方診斷節）
- runtime 診斷的兩個結構性盲點：`console.warn` 只存在於 `start.bat` 那個 `cmd /K` 視窗的 scrollback（零 stdout 重導向、關窗即失、其他進程讀不到）；rate limit 狀態是 `bot-setup.ts` 的 module-level 區域變數（無落檔、無 endpoint）。凡需事後比對時間戳的診斷都必須自己落檔

## Expandable Blockquote 支援（Roadmap）

Telegram Bot API 7.3+ 支援 `expandable_blockquote` entity。研究結論（2026-07-28）：

- **HTML path**（`format-html.ts`）：需識別 `>...\|\|` 結尾語法並輸出 `<blockquote expandable>`，約 ~10 行改動
- **Rich Message path**：可能天然支援 MarkdownV2 的 `||` 語法，或可改用 `<details>` 標籤（有 summary 標題更強）
- 待實測 Rich Markdown 是否認 `||` 語法後再決定實作方案

## 相關

- [[bridge-project]] — Bridge 整體架構與 transform pipeline
- `ms-streaming-token-pipeline` — Streaming + final render 雙路共用 transform 的 skill
- `ms-telegram-bot-rate-limit-survival` — 429 存活指南 skill
