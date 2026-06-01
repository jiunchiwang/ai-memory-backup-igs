---
name: ms-streaming-token-pipeline
description: Use when a Telegram/Slack bot streams text via mid-turn edits plus a final render. Both paths must share one transform, or ASK buttons drop, half-tokens leak, and rate-limit recovery overwrites it.
---

# Streaming Token Pipeline（streaming + final render 雙路共用 transform）

## 概述

Agent bridge 的文字 token 協定（見 `ms-agent-text-token-signaling`）面對一個架構問題：**streaming 階段**（agent 還在寫字，bridge 每 N ms editMessageText 把 placeholder 更新成目前 buffer）跟 **final render 階段**（agent end_turn、bridge 拿完整 buffer 抽 token 執行 side effect + 最終 editMessageText）都要處理 token，又不能行為不一致。

踩過的四組坑：
1. **Double-strip**：streaming 用 `transform()` 把 token 剝光，final render 再在 `ab7.text` 上跑 legacy extract → 剝空的 text 裡找不到 token → ASK keyboard 消失
2. **半截 token 洩漏**：agent 還在寫 `<<GOAL_DONE:...` 還沒 close，placeholder 顯示 opener 字面，使用者看到 `<<GOAL_DONE:aa996f9 streaming hide 驗證`
3. **Rate-limit recovery 蓋掉 final render**：429 期間 final edit fail，recovery listener 用 streaming render 再蓋一次 placeholder，蓋到「streaming 幀」版本，鍵盤丟失
4. **ACP agent 純文字 turn token 被吞**：Kiro CLI 在無 tool calls 的 turn 過濾掉 `<<...>>` pattern，final render 的 `session.buffer` 不含 token；需 streaming capture fallback

核心原則：**streaming 與 final render 共用同一條 `transform()` pipeline（single source of truth），UX 保護函式（hide unterminated、剝 token）放在 pipeline 最下游一次做完；final render 直接讀 `ab7.text` 和 `ab7.askTokens`，下游不重新 extract；用 `turnFinalized` latch 讓 recovery listener 看到就 no-op；edit fail 時先 `sendMessage(text, {reply_markup})` 保 keyboard，再退到 queue**。

## 何時使用

- 做 Telegram / Slack bot 用 streaming edit 把 agent 回覆逐步更新
- Bridge 協定有多個 token（SEND_FILE / ASK / SCHEDULE / SKILL_USED / GOAL_DONE）
- Streaming 幀上看到 `<<TOKEN:...` 半截洩漏
- ASK 按鈕應該掛上但使用者看到 raw token 文字
- Rate-limit 期間 edit fail 後 keyboard 消失
- 已有 observerTransformer.ts / 類似的 token 抽取模組
- Token 在有 tool calls 的 turn 正常運作，但純文字 turn 被吞掉

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

## 三組坑與修法

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

每次動 observerTransformer.ts 或 index.ts 的 final render 路徑，都跑完這四支。

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

## 相關

- **ms-agent-text-token-signaling** — token 協定基礎、ASK label 40 字上限、ASK-safe key 設計
- **ms-agent-scheduled-prompts** — `<<SCHEDULE:...>>` 實作，scheduler fake-ctx 必須用真 bot.api
- **ms-telegram-bot-rate-limit-survival** — rate-limit UI 凍結策略；本 skill 的 `turnFinalized` + sendMessage fallback 與該 skill 的 pendingMessages queue 對應
- **ms-kiro-strreplace-silent-fail** — 改完 observerTransformer 立刻 grep 驗證 token 列表更新
