---
name: ms-streaming-token-pipeline
description: Use when a Telegram/Slack bot streams text via mid-turn edits plus a final render. Both paths must share one transform, or ASK buttons drop, half-tokens leak, and rate-limit recovery overwrites it.
---

# Streaming Token Pipeline（streaming + final render 雙路共用 transform）

## 概述

Agent bridge 的文字 token 協定（見 `ms-agent-text-token-signaling`）面對一個架構問題：**streaming 階段**（agent 還在寫字，bridge 每 N ms editMessageText 把 placeholder 更新成目前 buffer）跟 **final render 階段**（agent end_turn、bridge 拿完整 buffer 抽 token 執行 side effect + 最終 editMessageText）都要處理 token，又不能行為不一致。

踩過的六組坑：
1. **Double-strip**：streaming 用 `transform()` 把 token 剝光，final render 再在 `ab7.text` 上跑 legacy extract → 剝空的 text 裡找不到 token → ASK keyboard 消失
2. **半截 token 洩漏**：agent 還在寫 `<<GOAL_DONE:...` 還沒 close，placeholder 顯示 opener 字面，使用者看到 `<<GOAL_DONE:aa996f9 streaming hide 驗證`
3. **Rate-limit recovery 蓋掉 final render**：429 期間 final edit fail，recovery listener 用 streaming render 再蓋一次 placeholder，蓋到「streaming 幀」版本，鍵盤丟失
4. **ACP agent 純文字 turn token 被吞**：Kiro CLI 在無 tool calls 的 turn 過濾掉 `<<...>>` pattern，final render 的 `session.buffer` 不含 token；需 streaming capture fallback
5. **editNow 無並發互斥狂發相同訊息**：streaming edit 函式被 onUpdate（每 chunk）fire-and-forget 觸發、節流時間戳只在成功後更新——送出開始失敗後閘門全開，並發呼叫在「draft 失敗 → `!placeholder` → `await sendMessage`」的 TOCTOU 窗口各自建立新訊息，1-2 秒冒出十幾則相同內容
6. **Mutable 內容混進 draft 幀，動畫抖動**：Telegram draft 更新動畫是官方規格的純 append-only 模型（淡入 `max(0, strlen(new)-strlen(prev))` 個尾端字元、無 mid-text 更新語意），tool 進度行的 emoji 翻轉（⚙️→✅）、秒數插入、`slice(-5)` 視窗滑動、body 追加推擠 statusTail 全是 mid-text 變動 → 使用者看到文字跳動、tool 行殘缺、已顯示文字倒退。「volatile 區排在 body 後」只能緩解不能根治

核心原則：**streaming 與 final render 共用同一條 `transform()` pipeline（single source of truth），UX 保護函式（hide unterminated、剝 token）放在 pipeline 最下游一次做完；final render 直接讀 `ab7.text` 和 `ab7.askTokens`，下游不重新 extract；用 `turnFinalized` latch 讓 recovery listener 看到就 no-op；streaming edit 函式用 coalescing latch 保證同時最多一個 in-flight；edit fail 時先 `sendMessage(text, {reply_markup})` 保 keyboard，再退到 queue；draft 幀只放 append-only 內容（恆定 header + body），tool/thinking 等 mutable 內容走獨立 status 訊息通道**。

## 何時使用

- 做 Telegram / Slack bot 用 streaming edit 把 agent 回覆逐步更新
- Bridge 協定有多個 token（SEND_FILE / ASK / SCHEDULE / SKILL_USED / GOAL_DONE）
- Streaming 幀上看到 `<<TOKEN:...` 半截洩漏
- ASK 按鈕應該掛上但使用者看到 raw token 文字
- Rate-limit 期間 edit fail 後 keyboard 消失
- 已有 observerTransformer.ts / 類似的 token 抽取模組
- Token 在有 tool calls 的 turn 正常運作，但純文字 turn 被吞掉
- 同一則回覆在聊天室裡突然出現一連串內容相同的訊息（streaming 降級 race）
- Draft streaming 期間文字跳動、tool 進度行殘缺、已顯示文字倒退（mutable 內容混進 append-only draft）

**不要用在：**
- 沒有 streaming（一次送完整訊息）— 直接 regex extract 就好
- 協定只有一種 token（單純 regex）— balanced scanner 還不值得
- 用 function calling / tool use API 做 side effect — 不用 text token

## 架構：single pipeline

```
           ┌─────────────────────────────────────┐
           │ transform(buffer, parsers)          │
           │                                      │
           │  1. maskCodeRegions()               │  ← code fence 內 token 不觸發
           │  2. Phase A: balanced scanner       │  ← <<GOAL_DONE:>> <<SKILL_USED:>>
           │     (SKILL_USED/GOAL_DONE/RESTART)  │     <<RESTART:>> 等 free-form reason
           │     深度棧 <<>> 原子吸收 inner       │
           │  3. Phase B: regex extract           │
           │     (SEND_FILE/SCHEDULE/ASK)         │  ← 結構化 body，regex 夠
           │  4. restore() code fence             │
           │  5. hideTrailingUnterminatedToken()  │  ← opener 沒 close 換 …
           │  6. return { text, askTokens,       │
           │            sendFiles, scheduleTokens,│
           │            skillUsages, goalDone,   │
           │            restartToken }            │
           └─────────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                              ▼
 Streaming render                  Final render
 （每 STREAM_EDIT_INTERVAL_MS）     （prompt() resolve 後）
  ↓                                 ↓
 editMessageText(r.text)           editMessageText(ab7.text,
                                     { reply_markup:
                                       buildAskKeyboard(ab7.askTokens) })
                                   for path of ab7.sendFiles: sendFileWithWhitelist
                                   for entry of ab7.scheduleTokens: registerSchedule
                                   for usage of ab7.skillUsages: usageStore.markUsed
                                   if (ab7.goalDone) goalStore.markDone(...)
```

一條 pipeline，兩個消費者；streaming 只消費 `r.text`，final render 消費所有欄位。不要在下游 re-run extract。

## 六組坑與修法

### 坑 1：Double-strip（ASK 按鈕消失）

**症狀**：使用者看到 `<<ASK:...>>` 原文，沒按鈕。Bridge log 沒 warn（token 格式 OK）。

**根因**：`runPrompt` 先做 `ab7 = transformReplyTokens(session.buffer)` 預剝（AB-7a 加的），但沒傳 parsers → SCHEDULE 沒 parse 但 ASK 照樣被剝。然後下游 legacy pipeline `extractAskTokens(ab7.text)` → `ab7.text` 已經沒 ASK token 了 → `asks = []` → `buildAskKeyboard([])` → 沒 keyboard。

```ts
// ❌ 踩雷版
const ab7 = transformReplyTokens(session.buffer);       // 不傳 parsers
const { text: s1, paths } = extractSendFileTokens(ab7.text);
const { text: s2, entries } = extractScheduleTokens(s1); // ab7.text 已無 SCHEDULE
const { text: s3, asks } = extractAskTokens(s2);         // 也無 ASK → asks=[]
```

**修法**：第一次 `transform()` 就傳 parsers，一次 extract 所有 token；下游讀 `ab7.*`，不重跑 extract：

```ts
// ✅ 正解
const bridgeParsers = { parseDuration, parseAbsoluteTime, parseRecurrence, computeNextRunAt };
const ab7 = transformReplyTokens(session.buffer, bridgeParsers);

const displayBody = ab7.text;            // 剝光的文字
const sendFiles = ab7.sendFiles;         // 不重 extract
const scheduleEntries = ab7.scheduleTokens;
const asks = ab7.askTokens;
const skillUsages = ab7.skillUsages;
const goalDone = ab7.goalDone;
const restartToken = ab7.restartToken;

await editMessageText(displayBody, { reply_markup: buildAskKeyboard(asks) });
```

**規則**：transform 是 single source of truth。下游別 re-run legacy extract。

### 坑 2：半截 token opener 洩漏

**症狀**：placeholder 卡在 `<<GOAL_DONE:aa996f9 streaming hide 驗證` 這種半截 token，沒 `>>` 結尾，使用者截圖看到原文。

**根因**：agent 正在 stream 寫 reason，`>>` 還沒送出。`runBalancedPhase` scanner 找不到配對 `>>` 走 aborted 分支，原文保留 → editMessageText 就把 opener 字面貼給使用者。

**舊修法（不夠）**：`hideTrailingUnterminatedToken()` 只在 streaming `renderReply()` 呼叫。結果：agent **stream 結束在半截 token** 的 case（沒再 send `>>` 就 end_turn），final render 走 `ab7.text` 不過 hide → 使用者最終訊息仍看到半截。

**正解**：hide 整合進 `transform()` 收尾：

```ts
function transform(raw: string, parsers?: ScheduleParsers): TransformedReply {
  const { masked, restore } = maskCodeRegions(raw);

  // Phase A: balanced scanner for free-form-reason tokens
  let stripped = runBalancedPhase(masked, handlers);

  // Phase B: regex for structured tokens
  stripped = stripped.replace(SEND_FILE_RE, ...)
                     .replace(SCHEDULE_RE, ...)
                     .replace(ASK_RE, ...);

  stripped = restore(stripped);
  stripped = stripped.replace(/\n{3,}/g, "\n\n").trim();

  // ✅ 收尾統一 hide,streaming / final 共用
  stripped = hideTrailingUnterminatedToken(stripped);

  return { text: stripped, askTokens, sendFiles, ... };
}
```

Helper 長這樣：

```ts
const OPENER_RE = /<<(GOAL_DONE|SKILL_USED|RESTART|ASK|SCHEDULE|SEND_FILE):/g;

function hideTrailingUnterminatedToken(text: string): string {
  // 找最後一個 opener
  let lastOpenerIdx = -1;
  for (const m of text.matchAll(OPENER_RE)) lastOpenerIdx = m.index!;
  if (lastOpenerIdx < 0) return text;

  const tail = text.slice(lastOpenerIdx);
  if (tail.includes(">>")) return text;        // 有 close，正常
  return text.slice(0, lastOpenerIdx).trimEnd() + "\n…";
}
```

**規則**：UX 保護函式放在 **shared pipeline 最下游**，不要 per-callsite hook — 新 callsite 會忘記呼叫。

### 坑 3：rate-limit recovery 蓋掉 final render

**症狀**：使用者最終看到的訊息是 streaming 的 in-progress 版本，ASK 按鈕消失。

**根因鏈**：
1. Final render 在 `editMessageText(ab7.text, {reply_markup})` throw（429）
2. Fallback 進 `queuePendingMessage(chatId, text + suffix)`，pendingMessages queue 的是 `sendMessage`（不支援 reply_markup）→ keyboard 丟失
3. Rate-limit 復原後，**rate-limit recovery listener**（之前註冊在 session.onUpdate）被觸發
4. Listener 內呼叫 `editNow()` → `renderReply(session.buffer, false)` → streaming-style render
5. Recovery 把 placeholder edit 成 streaming 版本（剝 token 的 text 但沒 keyboard）

**修法兩層**：

**Layer A**：`turnFinalized` latch，prompt() resolve 後 set true，recovery listener 看到就 no-op：

```ts
let turnFinalized = false;

const recoveryListener = () => {
  if (turnFinalized) return;                       // ← no-op
  editNow().catch(err => console.error(...));
};
rateLimitRecoveryListeners.add(recoveryListener);

try {
  await client.prompt(session.id, promptText);
  turnFinalized = true;                            // ← set true 在 AB-7a 分析前
  const ab7 = transformReplyTokens(session.buffer, bridgeParsers);
  // ... final render with askKeyboard
} finally {
  rateLimitRecoveryListeners.delete(recoveryListener);
}
```

**Layer B**：final edit fail 時先 `sendMessage` 重送（帶 keyboard），只有連 sendMessage 也 fail 才進 queue：

```ts
async function sendFinalBody(ctx, chatId, placeholderId, body, keyboard) {
  try {
    await ctx.api.editMessageText(chatId, placeholderId, body, {
      reply_markup: keyboard,
    });
  } catch (err) {
    // Edit 失敗 → 試 sendMessage 當新訊息（帶 keyboard）
    try {
      await ctx.api.sendMessage(chatId, body, { reply_markup: keyboard });
    } catch (err2) {
      // sendMessage 也失敗 → queue（keyboard 丟失，但至少 body 不會掉）
      queuePendingMessage(chatId, body);
    }
  }
}
```

**規則**：streaming 跟 final render 是**兩條邏輯**但共用 transform。final 有額外的 keyboard / side effect，fail 時先保 keyboard 再退而求其次。

### 坑 4：ACP agent 純文字 turn token 被吞（streaming capture fallback）

**症狀**：agent 回覆帶 `<<RELAY_DELEGATE:...>>` 或其他 token，bridge 的 final render 提取為空（`relayDelegateTokens = []`），token 沒被執行。但同一個 token 在有 tool calls 的 turn 裡正常運作。

**根因**：Kiro CLI（ACP agent）在**純文字 turn**（沒有任何 tool call）時，對最終文字輸出做 post-processing，過濾掉它不認識的 `<<...>>` pattern。有 tool calls 的 turn 不受影響——文字是在 tool calls 之間分段 stream 出來的，post-processing 沒機會跑。

**觀察到的規律**：
- ✅ 有 tool calls 的 turn → `session.buffer` 包含完整 token → final render 正常提取
- ❌ 純文字 turn（無 tool calls）→ `session.buffer` 不包含 token → final render 提取為空

**修法：streaming capture fallback（雙層防護）**

**Hard fix**：在 `sessionManager.applyUpdate`（每次收到 `agent_message_chunk` 時）掃描 buffer 是否包含完整 token，有的話存到 `session._streamingDelegates`。Final render 時如果正常提取為空，fallback 到 streaming 階段捕獲的 token：

```ts
// sessionManager.ts — applyUpdate
applyUpdate(session, update) {
  if (update.type === "agent_message_chunk") {
    session.buffer += update.content.text;
    // Streaming capture: 偵測完整 token 存起來
    const RE = /<<RELAY_DELEGATE:\s*([^|>\r\n]+?)\s*\|\s*(\{[^>\r\n]+?\})\s*>>/g;
    for (const m of session.buffer.matchAll(RE)) {
      if (!session._streamingDelegates) session._streamingDelegates = [];
      const key = m[0];
      if (!session._streamingDelegates.some(d => d.raw === key)) {
        session._streamingDelegates.push({ raw: key, target: m[1], json: m[2] });
      }
    }
  }
}
```

```ts
// index.ts — final render fallback
const relayDelegateTokens = extractRelayDelegates(session.buffer);
if (relayDelegateTokens.length === 0 && session._streamingDelegates?.length) {
  // Kiro CLI 吞了 token，用 streaming 階段捕獲的
  relayDelegateTokens.push(...session._streamingDelegates);
}
```

**Soft fix**：preamble tool note 加警告「發 `<<RELAY_DELEGATE:...>>` 的 turn 必須包含至少一個 tool call」。Agent 不一定遵守，所以 hard fix 是必要的。

**規則**：任何 token 如果可能出現在純文字 turn 裡，都需要 streaming capture fallback。不能只靠 final render 的 `session.buffer` 提取——ACP agent CLI 可能在 final output 時過濾掉 token。

### 坑 5：editNow 無並發互斥，draft 降級 race 狂發相同訊息

**症狀**：agent 單一回答，聊天室卻一口氣出現十幾則內容相同（或幾乎相同）的訊息（2026-07-11 live bug：問 roadmap → 1x 則相同訊息）。

**根因鏈**（三個條件疊加，缺一不可）：
1. `editNow` 是 async 但被 `session.onUpdate` **fire-and-forget** 呼叫（每個 chunk 一次），**沒有 in-flight 鎖**
2. 節流時間戳 `lastEditAt` **只在成功送出後更新** → draft 送出一旦開始失敗（TTL 過期 / client 清掉 / API 瞬時錯誤），`elapsed >= interval` 對每個 chunk 恆真，閘門全開（chunk 速率 ~10/秒 = 10 並發/秒）
3. Draft 降級分支是 TOCTOU：`await trySendDraft`（失敗）→ 檢查 `if (!placeholder)` → `await ctx.api.sendMessage(...)`。`placeholder` 要等第一個 sendMessage **resolve** 才賦值，網路延遲 1-2 秒的窗口內，每個並發呼叫檢查 `!placeholder` 都是 true → **各自發出一則新訊息**

重複數量 = 窗口內的並發呼叫數 ≈ chunk 速率 × sendMessage 延遲 ≈ 10-15 則。

**修法：coalescing latch**（同時最多一個 in-flight，中間觸發合併成結束後補跑一次拿最新 buffer）：

```ts
export function coalesceAsyncRunner(
  fn: () => Promise<void>,
  isCancelled: () => boolean = () => false,
): () => Promise<void> {
  let inFlight = false, pending = false;
  const run = async (): Promise<void> => {
    if (isCancelled()) return;
    if (inFlight) { pending = true; return; }
    inFlight = true;
    try { await fn(); }
    finally {
      inFlight = false;
      if (pending) { pending = false; if (!isCancelled()) void run(); }
    }
  };
  return run;
}

// run-prompt：以 turnFinalized 為取消條件
const editNow = coalesceAsyncRunner(editNowInner, () => turnFinalized);
```

`isCancelled = () => turnFinalized` 一石二鳥：順帶堵掉「in-flight 幀在 final render 之後才 resolve、再冒出一則 streaming 訊息」的第二個洞（坑 3 的 latch 只擋 recovery listener，沒擋 editNow 自己）。另外在降級分支 await 之後補 `if (turnFinalized) return` 再檢查——await 期間狀態可能已翻轉。

**規則**：任何被多路觸發（per-chunk onUpdate / keepalive timer / recovery listener）的 async streaming edit 函式，都必須有並發互斥。「內容 identical check」不是互斥——失敗期間 `lastRendered` 不更新，擋不住並發。抽成獨立無依賴 helper（如 `async-coalesce.ts`）才能被 smoke 直測 shipped code。

### 坑 6：mutable 內容混進 draft 幀，動畫抖動（雙通道拆分）

**症狀**：draft streaming 期間文字跳動、tool 進度行逐字慢慢浮現又被截斷、body 尾端看起來倒退。工具越多、完成越頻繁抖越兇（2026-07-12 live bug）。

**根因**：Telegram 官方規格（core.telegram.org/api/bots/ai）定義 draft 更新動畫為純 append-only：client 立即顯示新文字前 `strlen(prev)` 個字元、淡入 `max(0, strlen(new)-strlen(prev))` 個尾端字元，**規格沒有 mid-text / 頭部變動的更新方式**。tool 行的 emoji 翻轉（⚙️→✅）、完成秒數插入 `(0.3s)`、`slice(-5)` 視窗滑動、body 追加把 statusTail 往後推——全是 mid-text 變動，前綴對不齊時 client 顯示錯位內容再慢慢淡入修正。

**舊修法（不夠）**：volatile 區（thinking/tools）排在 body 之後。只要 tool 行還在 draft 裡，body 追加照樣推擠它、它自己的原地變動照樣抖——緩解不根治。

**正解：雙通道拆分**（參考 OpenClaw `streaming.mode: "progress"`）：

- **Draft 通道**：只放恆定 header（如 ASK 的「我選擇了：X」，第一幀到最後一幀不變）+ 回答 body + cursor——嚴格尾端追加。
- **Status 通道**：tool 進度行 + thinking preview 走**獨立的靜音一般訊息**（`sendMessage({disable_notification: true})` 一次、之後 `editMessageText` 原地更新）。一般訊息的 edit 是整則重繪、沒有字元淡入動畫——emoji 翻轉、秒數插入、行數增減都不抖。turn 結束（finally，含 cancel/superseded/錯誤）刪除。

```
Draft（append-only）        Status 訊息（可自由 mutate）
┌──────────────────┐       ┌─────────────────────┐
│ 我選擇了：方案A    │       │ ✅ Read (2.7s)       │
│                  │       │ ⚙️ Grep              │
│ 回答文字逐步追加… ▍│       │ 💭 thinking preview  │
└──────────────────┘       └─────────────────────┘
  trySendDraft 全量替換        editMessageText 原地更新
  final 時由正式訊息取代        finally 時 deleteMessage
```

**四個實作陷阱**：
1. **sendMessage 會清掉 live draft**（draft 除了 ~30s TTL，「chat 收到任何一般訊息」也立即清除）→ status 訊息**建立**後同 tick 用同 draftId 重送最新內容恢復（edit 不會清 draft，只有建立那次要補）。
2. **draft identical check 不可短路 status 更新**：tool 完成但 body 沒新字時，draft 內容不變、status 有變——兩通道各自判斷 identical，不能共用一個 early return。
3. **draft 降級 placeholder 時先刪 status 訊息**：placeholder 路徑的 renderReply 自帶 tool 行，不刪會雙份顯示。
4. **status 建立的 await 期間 turn 可能 finalize**：await 後補查 `turnFinalized`，是則立刻刪掉剛建立的訊息，避免殘留。

**規則**：draft 通道裡的每一幀都必須是前一幀的字首延伸（恆定 header 除外，它從第一幀就在）。任何會原地變動的內容——進度指示、狀態 emoji、計時——一律走可自由 edit 的一般訊息通道。

## Balanced scanner（free-form reason 必用）

GOAL_DONE / SKILL_USED / RESTART 的 reason 欄位是 free-form 自然語言，agent 可能在 reason 裡寫：

```
<<GOAL_DONE:C3 <<RESTART:reason>> token 端到端驗證通過 ... OK>>
```

**regex 會炸**：`<<GOAL_DONE:(.+?)>>` non-greedy 匹配會在內部第一個 `>>` 停下，outer token 被截斷。

正解是 **balanced scanner**：單次前進掃描，`<<` 入棧、`>>` 出棧，深度歸零時才是配對的 outer close。

```ts
function runBalancedPhase(text: string, handlers: Record<string, Handler>): string {
  // 找 <<PREFIX:, PREFIX ∈ {GOAL_DONE, SKILL_USED, RESTART}
  // 從開頭開始掃，depth = 0
  // 遇到 <<  → depth++
  // 遇到 >>  → depth--
  // depth === 0 的 >> 就是 outer close
  // Outer 原子吸收，inner 字面留在 reason 內，下游 regex 不再看到 inner
  // ...
}
```

**Order 很重要**：Phase A（balanced）**先於** Phase B（regex）。outer 先吃掉整段，inner 的 `<<RESTART:...>>` 不會獨立觸發重啟。

Smoke 要涵蓋：
- 三層巢狀（SKILL_USED > RESTART > GOAL_DONE）
- Outer malformed 時 inner 不洩漏
- Unpaired `<<`（depth 不歸零，aborted 分支留字面）
- Code fence 內 token inert
- 相鄰 token（`<<A:>><<B:>>`）正確分開
- Depth > 2 的 balanced `<<>>`

## Smoke 注意事項

改 `observerTransformer.ts` 後必須重 build：

```bash
npx tsc -p .
# 然後才 node scripts/check-observer-transformer.mjs
```

Smoke 跑 `dist/observerTransformer.js` 不是 `src/`。這條沒做的話會誤判「修法無效」。標準流程：

```
改 src → npx tsc → 跑 smoke
```

## Smoke matrix

最少這幾支：

| Smoke | 驗什麼 |
|---|---|
| `check-observer-transformer` | 所有 token 的正常 extract + 半截 hide + double-strip 不再 |
| `check-balanced-scanner-edge` | 巢狀、unpaired、code fence、depth > 2 |
| `check-streaming-token-strip` | streaming 幀剝 token + 半截換 …（對 transform() 的直測） |
| `check-ab7-goal-loop` | final render 用 ab7.text + ab7.askTokens 不重 extract |
| `check-editnow-race` | editNow 並發互斥：10 並發只建 1 則 placeholder、trailing 補跑最新內容、finalize 後不補跑 |
| `check-draft-render` | draft 幀純淨（不含 tool/thinking）、tools/thinking 變動後幀逐字相同、status 訊息內容、replyHeader 恆定前綴、markdown 原文、截斷保尾 |

每次動 observerTransformer.ts 或 index.ts 的 final render 路徑，都跑完這幾支。

## Common Mistakes

| 錯誤 | 修正 |
|---|---|
| Streaming 跑 transform()、final 跑 legacy 3-token extract | 下游讀 `ab7.*` 欄位，不重 extract |
| 第一次 transform() 不傳 parsers | 傳 parsers（見 `bridgeParsers` 範例）；不傳會讓 SCHEDULE 不 parse 但 ASK 照剝 |
| `hideTrailingUnterminatedToken` 只在 streaming 呼叫 | 移進 `transform()` 收尾；streaming / final 共用 |
| balanced scanner 放在 SEND_FILE/ASK 之後 | 順序要 balanced 先、regex 後；inner token 才不會獨立觸發 |
| 沒 `turnFinalized` latch，recovery listener 可能蓋 final | prompt resolve 後 set true，listener 檢查就 no-op |
| final edit fail 直接 queuePendingMessage | 先 try sendMessage（帶 keyboard），失敗再 queue |
| GOAL_DONE / SKILL_USED 的 reason 用 non-greedy regex | 改 balanced scanner；inner `<<...>>` 會把 non-greedy 切斷 |
| 改 `.ts` 後沒 `tsc` 重 build 就跑 smoke | smoke 跑 `dist/`；必須先 build |
| 沒 smoke 覆蓋「agent stream 結束在半截 token」 | 新增 case：`transform("text <<GOAL_DONE:half")` 斷言結尾 `…` |
| Recovery listener 跟 final edit 沒互斥 | `turnFinalized` latch + `rateLimitRecoveryListeners.delete` 在 finally |
| balanced scanner handler 對 reason 長度 hard reject（超過就 `return null` token verbatim 留） | **改成 silent truncate**：`if (reason.length > MAX) reason = reason.slice(0, MAX)`。hard reject 看似嚴格，但 agent 寫長 reason（完成理由／skill 使用理由）的機率遠高於它自己自檢長度；reject 會讓 GOAL_DONE 不觸發、goal 卡在 continuation 迴圈（2026-05-03 live bug）。truncate 保底不影響 UX（Telegram 單訊息 4096 字，500 字 reason 還有大量餘裕）。參考 `BALANCED_REASON_MAX = 500` in `observerTransformer.ts`。 |
| 只靠 final render 的 `session.buffer` 提取 token，沒有 streaming capture fallback | ACP agent（Kiro CLI）在純文字 turn 會吞掉 `<<...>>` token；必須在 streaming 階段（`applyUpdate`）就捕獲完整 token 存到 `session._streamingDelegates`，final render 為空時 fallback |
| streaming edit 函式 async 卻無 in-flight 鎖，靠節流時間戳防並發 | 時間戳只在成功後更新 → 失敗期間閘門全開；用 coalescing latch（in-flight + pending flag）保證同時最多一個，`isCancelled` 接 `turnFinalized`（見坑 5） |
| 降級分支「檢查 `!placeholder` → await 建新訊息」無再檢查 | TOCTOU：await 期間別的呼叫也過了檢查；latch 序列化 + await 後補 `turnFinalized` / `placeholder` 再檢查 |
| tool 進度行 / thinking preview 放進 draft 幀（即使排在 body 後） | Draft 動畫是官方規格的純 append-only；mutable 內容走獨立靜音訊息 + editMessageText 原地更新（見坑 6 雙通道拆分） |
| status 訊息 sendMessage 後 draft 消失沒處理 | 一般訊息會清掉 live draft；status **建立**後同 tick 重送 draft（edit 不會清，只有建立要補） |
| draft 通道與 status 通道共用一個 identical-check early return | tool 完成但 body 沒新字 → draft 不變、status 有變；兩通道各自判斷 |
| replyHeader（「我選擇了：X」等）只在 final render 拼上 | Streaming 幀（draft + placeholder edit）都要帶；header 恆定前綴不破壞 append-only，且要計入 4096 長度預算 |
| tool 行顯示 adapter 原文（整條 Bash 命令），或 title 固定在 tool_call 起始那刻 | 顯示層只取 title 第一個詞（工具種類）+ 秒數；`tool_call_update` 帶 title 時回寫 timeline entry（adapter 常在參數 stream 完才補完整 title） |

## 相關

- **ms-agent-text-token-signaling** — token 協定基礎、ASK label 40 字上限、ASK-safe key 設計
- **ms-agent-scheduled-prompts** — `<<SCHEDULE:...>>` 實作，scheduler fake-ctx 必須用真 bot.api
- **ms-telegram-bot-rate-limit-survival** — rate-limit UI 凍結策略；本 skill 的 `turnFinalized` + sendMessage fallback 與該 skill 的 pendingMessages queue 對應
- **ms-kiro-strreplace-silent-fail** — 改完 observerTransformer 立刻 grep 驗證 token 列表更新
