---
name: ms-agent-scheduled-prompts
description: 當需要為 LLM agent bridge（Telegram bot、Slack bot、CLI UI）做延遲 / 常態性 prompt 觸發、排程 bridge 指令（如每天凌晨 /restart）、或要在 agent 回覆裡嵌 token 讓使用者自助建排程時使用
---

# Agent 排程 Prompt（delayed / recurring / bridge command）

## 概述

讓 bridge 在**未來某時間點**自動把一段 prompt 丟給 agent 或執行 bridge 內建指令。沒有自己的 daemon、沒有向量 DB、就用一個 JSON 持久化 store + `setTimeout` + ephemeral session。同時給 agent 一個文字 token（`<<SCHEDULE:...>>`）讓它在對話裡自助建排程，人類也用一個 slash command（`/schedule`）操作。

核心原則：**「到點要做什麼」是純資料（time + prompt），資料存 JSON；ephemeral session 跑 agent；persist-before-run 避免 crash 重放；recurring 到點先算下一 tick 再改寫 runAt 最後 re-arm。**

## 何時使用

- 做 Telegram / Slack / IRC bot 想加「30 分鐘後提醒我」「每天 09:00 早安」
- 想讓 agent 自己在回覆裡建排程（例如使用者說「一小時後叫我」，agent 嵌 `<<SCHEDULE:1h|...>>`）
- 想讓排程觸發時執行 bridge 指令（例如每天凌晨 `/restart` 清 context）
- 已經有 long-term memory / facts 機制，不想另外做向量 DB 或 cron daemon

**不要用在：**
- 大量併發排程（數百個同時觸發）— `setTimeout` fan-out 會吃記憶體，改用 bull/agenda 之類
- 需要跨機器分散式排程 — 單機 JSON 不夠，改用 redis / database
- 需要秒級精確度 — `setTimeout` 本身就有 event loop 延遲
- 純粹的「提醒」（不進 agent turn）— 直接 `bot.api.sendMessage` 就好，不需要 ephemeral session

## 架構分層

```
┌────────────┐   JSON file      ┌─────────────┐
│ /schedule  │ ─── persist ───► │  store.json │
│  command   │                  └─────────────┘
└────────────┘                         │
      │                                ▼
      ▼                          ┌─────────────┐
┌────────────┐     setTimeout   │  Scheduler  │
│ <<SCHEDULE:│ ── register ────►│  in-memory  │
│  token     │                  │  timer Map  │
└────────────┘                  └──────┬──────┘
                                       │ fire
                    ┌──────────────────┼───────────────────┐
                    ▼                                      ▼
           bridge command?                         ephemeral AcpClient
           (prompt starts with /)                  → agent prompt
           → fake grammY ctx                       → post reply to chat
           → COMMAND_HANDLERS[name](fake_ctx)
```

### 三個關鍵元件

| 元件 | 職責 |
|---|---|
| **Store**（`schedule-store.ts`） | JSON 持久化；load/add/remove/list/persist；load 時對過期 one-shot 回報 missed，recurring 滾下一 tick |
| **Scheduler**（`scheduler.ts`） | `arm(entry)` 設 `setTimeout`；`fire(entry)` 到點觸發；recurring 完成後 `afterFire` 算下一 tick 再 re-arm；維護 `timers: Map<id, NodeJS.Timeout>` |
| **Bridge 側整合** | `/schedule` slash command 與 wizard；`<<SCHEDULE:...>>` token 剝除；`armAll()` 啟動時重載；shutdown 前 `stop()` 清 timer |

## 資料結構

```ts
// schedule-store.ts
export interface ScheduleEntry {
  id: string;             // 8 碼 random
  chatId: number;
  userId: number;
  runAt: number;          // epoch ms；recurring 每次 fire 後會被改寫成下一 tick
  prompt: string;         // 到點要送給 agent 的 user turn
  createdAt: number;
  recurrence?: Recurrence; // 可選；不存在等同 "once"
}

// recurrence.ts
export type Recurrence =
  | { kind: "every"; intervalMs: number }
  | { kind: "daily"; hour: number; minute: number }
  | { kind: "weekly"; weekday: 0|1|2|3|4|5|6; hour: number; minute: number }
  | { kind: "cron"; expr: string };   // 5 欄位 cron: min hour dom mon dow
```

Store 檔：`<MEMORY_DIR>/schedules.json`（扁平陣列）。

## 核心模式

### 1. `fire()` 的 one-shot vs recurring 分流

**one-shot**：先 `store.remove(id)` + persist，再執行。確保 crash 或 `/restart` 自殺時不會重放。

**recurring**：不 remove，執行完（或被 bridge command dispatch 掉）跑 `afterFire()` 算下一 tick，改寫 `runAt` 後 persist + re-arm。

```ts
async fire(entry: ScheduleEntry) {
  // 1. one-shot 先移除再跑；recurring 不動
  if (!entry.recurrence) {
    this.store.removeInMemory(entry.id);
    await this.store.persist();
  }

  // 2. 試試 bridge command（見下一節）
  const handled = await this.tryBridgeCommand(entry);
  if (!handled) {
    // 3. 走 ephemeral AcpClient
    await this.runAgentPrompt(entry);
  }

  // 4. recurring 滾下一 tick
  await this.afterFire(entry);
}

private async afterFire(entry: ScheduleEntry) {
  if (!entry.recurrence) return;
  const next = computeNextRunAt(entry.recurrence, Date.now());
  if (next == null) return;                // 永遠不會再觸發（很罕見）
  entry.runAt = next;
  await this.store.persist();
  this.arm(entry);
}
```

### 2. Missed-fire 策略：skip

bridge 下線期間到期的排程，**重啟後跳過，不補跑**。這是最不打擾使用者的預設。

```ts
// load() 時對每筆處理
const now = Date.now();
for (const e of entries) {
  if (e.runAt > now) {
    upcoming.push(e);
    continue;
  }
  // 已過期
  if (e.recurrence) {
    // recurring: 滾到下一個未來 tick
    const next = computeNextRunAt(e.recurrence, now);
    if (next) {
      e.runAt = next;
      upcoming.push(e);
    }
    // 否則 drop
  } else {
    // one-shot: 視為 missed，從 store 移除
    missed.push(e);
  }
}
await persist();
```

啟動時若 `missed.length > 0`，**以 chat 分組**一次通知使用者，不要每筆發一則。

### 3. Ephemeral AcpClient（不污染使用者 session）

排程觸發時開一個**全新**的 AcpClient，跑完就 close。它看不到使用者當下那個聊天的 history，所以 prompt 必須自足。

```ts
const client = new AcpClient({ agent: "main" });
await client.initialize();
const session = await client.newSession();
const reply = await client.prompt(session.id, entry.prompt);
await client.close();
await bot.api.sendMessage(entry.chatId, `⏰ 排程 ${entry.id} 執行完成\n\n${reply}`);
```

### 4. Bridge command dispatch（Fake grammY Context）

讓 prompt 以 `/` 開頭時（如 `/restart`、`/schedule list`），**不送 agent**，直接跑 bridge 內建 handler。這樣使用者才能「每天 03:00 自動 /restart」。

```ts
// scheduler-commands.ts
export function parseBridgeCommand(prompt: string): { name: string; arg: string } | null {
  const trimmed = prompt.trimStart();
  if (!trimmed.startsWith("/")) return null;
  const space = trimmed.indexOf(" ");
  return space < 0
    ? { name: trimmed.slice(1).toLowerCase(), arg: "" }
    : { name: trimmed.slice(1, space).toLowerCase(), arg: trimmed.slice(space + 1) };
}

export async function tryRunBridgeCommand(
  bot: Bot, entry: ScheduleEntry, handlers: Record<string, (ctx: Context) => Promise<void>>
): Promise<{ handled: boolean; reply: string }> {
  const parsed = parseBridgeCommand(entry.prompt);
  if (!parsed) return { handled: false, reply: "" };
  const handler = handlers[parsed.name];
  if (!handler) return { handled: false, reply: "" };

  const replies: string[] = [];
  const fakeCtx: any = {
    chat: { id: entry.chatId },
    from: { id: entry.userId },
    match: parsed.arg,
    reply: async (text: string) => { replies.push(text); },
    replyWithPhoto: (file: any, opts?: any) =>
      bot.api.sendPhoto(entry.chatId, file, opts),
    replyWithDocument: (file: any, opts?: any) =>
      bot.api.sendDocument(entry.chatId, file, opts),
    api: bot.api,
  };

  await handler(fakeCtx);
  return { handled: true, reply: replies.join("\n\n") };
}
```

**關鍵點：**
- `reply()` 累積到 buffer，scheduler 收到後組「⏰ 排程 X（指令）執行完成」header 送出，保持 UX 一致
- `replyWithPhoto`/`replyWithDocument` 直接走 `bot.api` 送到目標 chatId（不累積）
- `match` 給字串（handlers 多數只檢查 `typeof === "string"`）
- **Scheduler 建構時不一定拿得到 `COMMAND_HANDLERS`**（forward reference），用 `setCommandHandlers(handlers)` setter 延後注入最乾淨

### 5. Scheduler lifecycle

```ts
// 啟動
const store = new ScheduleStore(path);
await store.load();                      // 讀檔 + 過期處理
const scheduler = new Scheduler({ bot, store });
scheduler.setCommandHandlers(COMMAND_HANDLERS);  // 在 handlers 宣告後接線
scheduler.armAll();                      // 對 upcoming 全部 arm

// 關閉
scheduler.stop();                        // clearTimeout 全部 timer
```

### 6. `<<SCHEDULE:...>>` token 協定

配合 `ms-agent-text-token-signaling`，給 agent 一個嵌入 token 的方式：

```
<<SCHEDULE:<time>|<prompt>>>
```

- **整段同一行**（不能跨行）
- `<time>` 先試 duration（`30s`/`15m`/`2h`/`1d`）→ 再試 recurring（`every 30m`/`daily 09:00`/`weekly mon 09:00`/`cron */5 * * * *`）→ 再試 absolute（`HH:MM`/`HH:MM:SS`/`tomorrow HH:MM`/`MM-DD HH:MM`/`YYYY-MM-DD HH:MM`）
- `<prompt>` 可含 `|`（只切第一個），**不可含 `>>`**；長度上限 1000 字
- 單則訊息至多 N 個 token（建議 3）

Bridge 剝除 token → 用當下 ctx 的 chatId/userId 建 entry → 回執 `⏰ 已排程 <id> <when>` 附在訊息末尾。

**注意：**
- token 協定也要走 `maskCodeRegions`（在 code fence 內的範例不渲染）
- 註冊 entry **在 final render 時才做**，不要在 streaming 時做（避免被拆 chunk 或中途失敗重送重複建）
- receipt 要標註 recurrence（`[每 30m]` / `[每天 09:00]` / `[cron */5 * * * *]`）

## /schedule wizard（ASK-based）

搭配 `<<ASK:...>>` 按鈕（見 `ms-agent-text-token-signaling` 的 interactive 小節）做多步導引：

```
/schedule                                  ← 空參數
  └─ bridge 回 <<ASK:sched_kind|add=⏱ 幾分鐘後|at=🗓 指定時刻|every=🔁 常態|...>>
       └─ 使用者點 "add"
            └─ bridge 回 <<ASK:sched_t_add|30s=30 秒後|10m=10 分鐘後|...>>
                 └─ 使用者點 "10m"
                      └─ bridge 寫 pendingSchedules Map（5 分鐘 TTL）
                          └─ 使用者下則訊息非 slash command → 當 prompt 送回 handleSchedule
```

**pendingSchedules 設計：**

```ts
interface PendingSchedule {
  userId: number;
  kind: "add" | "at" | "every" | "daily";
  time: string;                           // 已轉成 handleSchedule 能解析的格式
  createdAt: number;
}
const pendingSchedules = new Map<number /* chatId */, PendingSchedule>();
const PENDING_TTL_MS = 5 * 60 * 1000;
```

**ASK-safe time key 設計**：key 只能 `[a-zA-Z0-9_-]{1,20}`，所以 `09:00` 無法當 key（有冒號），要設計 `askTimeKeyToWire`：

```ts
function askTimeKeyToWire(kind: PendingSchedule["kind"], key: string): string | null {
  if (kind === "add" || kind === "every") {
    // key 本身就是 duration: "30s", "10m", "1h"...
    return /^\d+[smhd]$/.test(key) ? key : null;
  }
  if (kind === "at") {
    // "0900" -> "09:00"；"tmr_0900" -> "tomorrow 09:00"
    if (/^\d{4}$/.test(key)) return `${key.slice(0, 2)}:${key.slice(2)}`;
    if (/^tmr_\d{4}$/.test(key)) return `tomorrow ${key.slice(4, 6)}:${key.slice(6)}`;
    return null;
  }
  if (kind === "daily") {
    return /^\d{4}$/.test(key) ? `${key.slice(0, 2)}:${key.slice(2)}` : null;
  }
  return null;
}
```

**訊息 handler 攔截 pending：**

```ts
bot.on("message:text", async (ctx, next) => {
  const text = (ctx.message?.text ?? "").trim();
  const chatId = ctx.chat?.id;
  const pending = pendingSchedules.get(chatId);

  if (pending) {
    // 過期
    if (Date.now() - pending.createdAt > PENDING_TTL_MS) {
      pendingSchedules.delete(chatId);
    } else if (text.startsWith("/")) {
      // 使用者想用 slash command 中斷 wizard
      pendingSchedules.delete(chatId);
    } else {
      // 當 prompt 收下
      pendingSchedules.delete(chatId);
      const wireText = `${pending.kind} ${pending.time} ${text}`;
      ctx.match = wireText;
      return handleSchedule(ctx);
    }
  }
  return next();
});
```

## Common Mistakes（排程相關）

| 錯誤 | 修正 |
|---|---|
| One-shot `fire()` 先跑 handler 再 `remove` | 若 handler throw 或觸發 `/restart` 自殺，entry 留在檔案 → respawn 後重放。**先 remove+persist 再跑** |
| Recurring `fire()` 完忘了 `afterFire` | 只觸發一次就停了；recurring 邏輯位置錯誤 |
| Recurring `afterFire` 用 `entry.runAt + intervalMs` 當下一 tick | 遇到 `/restart` 隔很久會一次補跑多次；正確做法是 `computeNextRunAt(recurrence, Date.now())` 從當下算 |
| `setTimeout` 直接用 `runAt - Date.now()` 不設上限 | Node.js `setTimeout` 超過 2^31-1 ms (~24.8 天) 會 overflow 變成立即觸發；超過時用 `setTimeout(() => arm(e), maxSafe)` 分段 |
| 啟動時 `armAll` 前忘了 `setCommandHandlers` | bridge command dispatch 拿到空 handlers map，`/restart` 排程 fallthrough 變送 agent 說文字 |
| Ephemeral AcpClient 用完沒 `close` | spawn 的 child process 累積、file descriptor 洩漏 |
| Recurring `/restart` + one-shot dispatch 順序反 | one-shot `/restart` 要先 remove+persist 再 dispatch（`process.exit` 不會回來 persist） |
| Meta-command routine 把 `/restart` 放中間 | `handleRestart` 最後呼 `process.exit(N)`，控制權不會回到 for-loop,後面步驟靜默跳過、`✅ 完成` 訊息不會發。**自殺型步驟必須排最後**,loader 加 lint 自動搬或 refuse load |
| Missed-fire 補跑所有過期（firesAll） | 開機一次炸 20 則；預設 skip 最穩；要補最多 fire-once-and-skip-rest |
| Missed 通知一筆一則訊息 | 使用者被刷屏；以 chatId 分組一次報 |
| SCHEDULE token 在 streaming 就註冊 | token 可能被切 chunk，或整筆 agent 回覆失敗但 entry 已建；**只在 final render 註冊** |
| Wizard prompt 那步沒 TTL | 使用者選一半不回來，pending 永遠留著，下次想對話的第一句被吃掉 |
| Wizard 攔截用 `session.has(chatId)` 判斷 | 各 chat 的 pending 用同一個 Map key 即可；不要綁到 agent session id |
| Scheduler 沒提供 `stop()` 清 timer | `/restart` 前 timer 還在，respawn 後 armAll 又加一遍 → 記憶體兩份 |
| Bridge command handler 拿 `ctx.message`/`ctx.update` | Fake ctx 只提供最小欄位；擴充時要同步更新 `tryRunBridgeCommand` |
| `daily`/`weekly` recurrence 沒帶 `second` 欄位 | `setHours(h, m, undefined, 0)` 產生 Invalid Date → `next=NaN`，`JSON.stringify(NaN)="null"` 落盤 → 下次 arm 時 `Math.max(0, NaN - now)=NaN` → `setTimeout(NaN)` 被 Node clamp 到 1ms → 每秒熱迴圈。**解**：`computeNextRunAt` 用 `rec.second ?? 0` |
| `scheduler.arm` 沒擋 `runAt` 是 NaN/Infinity | 單一壞 entry 就能熱迴圈。**解**：arm 前檢 `Number.isFinite(entry.runAt)`，不過就 drop + forgetInMemory + persist + 通知使用者 |
| `ScheduleStore.persist` 寫入 NaN 被序列化成 `null` | load 時被 `isScheduleEntry` 擋掉（`typeof null !== "number"`），但寫盤當下沒警告。**解**：persist 前 filter 掉 `!Number.isFinite(runAt)` 的 entry |

### 實戰 bug 案例：常態排程每秒重觸發

**症狀**：排 `daily 04:00 /topicreview` 後 bridge 每秒送 20+ 次訊息、壓爆 Telegram 429。

**追因**（四段骨牌）：

```
1. schedules.json entry 的 recurrence 物件只有 {hour:4, minute:0}，漏 second
2. computeNextRunAt → setHours(4, 0, undefined, 0) → Invalid Date → NaN
3. NaN 落盤時 JSON.stringify 變 "null"：`"runAt": null`
4. setTimeout(NaN) 被 Node 當成最小值 ~1ms → 每秒 fire → afterFire 再算出 NaN → 再 arm → 熱迴圈
```

**三層防禦**（commit 級別的修法）：

```typescript
// Layer 1: src/recurrence.ts
if (rec.kind === "daily" || rec.kind === "weekly") {
  const d = new Date(from);
  d.setHours(rec.hour, rec.minute, rec.second ?? 0, 0);  // ← 預設 0
  const ms = d.getTime();
  if (!Number.isFinite(ms)) return null;                  // ← 守門 1
  // ...
}

// Layer 2: src/scheduler.ts::arm
if (!Number.isFinite(entry.runAt)) {
  console.error(`[scheduler] dropping entry ${entry.id}: non-finite runAt`);
  this.forgetInMemory(entry.id);
  await this.store.persist();
  this.notifyUser(entry, "entry dropped: non-finite runAt");
  return;
}

// Layer 3: src/schedule-store.ts
function isScheduleEntry(e: unknown): e is ScheduleEntry {
  // ... 其他檢查 ...
  if (!Number.isFinite((e as any).runAt)) return false;   // ← load 時也擋
  return true;
}
async persist() {
  const clean = this.entries.filter((e) => Number.isFinite(e.runAt));
  // ... write clean ...
}
```

**驗證**：寫一支 `scripts/check-recurrence-guards.mjs`，餵 18 個邊界 case（null / NaN / Infinity / 漏 second / 合法 from），跑到全 pass 才 ship。三層都不可省——單層只能防特定路徑。

## Fake ctx 的深坑：必須真呼叫 bot.api 拿真 message_id

基礎的 fake-ctx 設計（見前面「Bridge command dispatch」）讓 `ctx.reply` 累積到 buffer 陣列、scheduler 收集後 join 成一則訊息送。**但這跟 `runPrompt` 類 handler 衝突** — `runPrompt` 需要真的 `ctx.reply("Thinking...")` 回傳一個帶 `message_id` 的 Telegram Message object，後續 streaming editMessageText 才有對象。

### 踩雷症狀

排 `daily 03:00 /memorytoskill`（handler 內部走 runPrompt streaming）實際跑的時候：

- Placeholder `Thinking…` 訊息發得出來（fake ctx.reply 的第一個 reply）
- 但 agent 整整跑 19 分鐘、buffer 寫完整份報告
- 使用者最終只看到 `⏰ 排程 X（指令）執行完成 / Thinking...`
- Agent 實際輸出整份報告**全被吞掉**

### 根因

舊版 fake ctx 給 `ctx.reply` 回 `{ message_id: 0 }` 假物件：

```ts
// ❌ 踩雷版
reply: async (text: string) => {
  replyChunks.push(text);
  return { message_id: 0 };    // ← 假的 message_id
},
```

runPrompt 內部每 N ms 做 `ctx.api.editMessageText(chatId, 0, ...)` 每次都 400 `message to edit not found`，但 runPrompt 把 edit 錯誤吞了繼續跑。最終 `session.buffer` 有整份產出，但從來沒成功被 edit 到使用者看到的 placeholder 上。

### 修法：fake ctx 的 reply 真呼叫 bot.api

```ts
// ✅ 正解
const fakeCtx = {
  chat: { id: entry.chatId },
  from: { id: entry.userId },
  match: parsed.arg,

  // 真呼叫 bot.api，拿真 message_id 讓 streaming edit 能運作
  reply: async (text: string, extra?: any) => {
    const msg = await bot.api.sendMessage(entry.chatId, text, extra);
    return msg;   // 回傳真的 Telegram Message 物件（含 real message_id）
  },

  replyWithPhoto: (file: any, opts?: any) =>
    bot.api.sendPhoto(entry.chatId, file, opts),
  replyWithDocument: (file: any, opts?: any) =>
    bot.api.sendDocument(entry.chatId, file, opts),
  api: bot.api,
};

await handler(fakeCtx);
```

**改完之後**：

- Scheduler fire() 自己發 start marker（`⏰ 排程 X 開始執行…`）+ end marker（`✅ 執行完成` / `❌ 失敗`）
- Handler 內 `ctx.reply` 直接發真訊息（每個 reply 獨立一則）
- runPrompt 的 placeholder 是真 message，streaming edit 正確運作
- 使用者實際看到整段處理過程 + 最終結果

### 副作用：scheduler 層拿不到 reply 內容了

`replyChunks` 累積機制拿掉後，`BridgeCommandResult` 也不需要 `reply: string` 欄位了，改成：

```ts
interface BridgeCommandResult {
  handled: boolean;
  messagesSent: number;   // 計數用（作 log / debug）
  filesSent: number;
}
```

原本靠 `bridgeRes.reply` 當訊息 body 那段邏輯整個可以拿掉 — handler 自己發自己的訊息。scheduler `fire()` 只負責框架：start marker / end marker / error catch。

### 影響範圍：所有 bridge command

不只 `runPrompt` 類（/summary / /memorytoskill / /topicreview / /refreshrouting），**所有**排程觸發的 bridge command 都走新路徑。

**行為差異**（以 `/backup` 為例）：

舊（fake ctx 累積）：
```
⏰ 排程 X（指令）執行完成
🗂️ 備份啟動...
✅ 備份完成 (3.4s)
```
（reply 被 join 成一則，前面掛大 header）

新（fake ctx 真呼 bot.api）：
```
⏰ 排程 X 開始執行…       ← start marker（獨立訊息）
🗂️ 備份啟動...              ← handler reply 1
✅ 備份完成 (3.4s)           ← handler reply 2
✅ 排程 X 執行完成            ← end marker（獨立訊息）
```

訊息變多但清楚、streaming edit 能 work、使用者看得到完整過程。值得換。

## Meta-command：JSON 配置整合多個 slash command

常見需求：dialy 03:00 要跑四條（memorytoskill + summary + topicreview + backup）維運工作。三個方案：

**方案 A — 排四條獨立排程**（舊 pattern）：
```
daily 03:00 /memorytoskill
daily 03:30 /summary
daily 04:00 /topicreview
daily 04:30 /backup
```
缺點：30 分鐘間隔是 ad-hoc 的，無意義；任一條爛掉影響後續；排程 list 很吵。

**方案 B — Agent goal loop**：
```
daily 03:00 /goal 10 依序執行夜間例行
```
缺點：agent 發不了 bridge 自己的 slash command（協定不允許反向 RPC），除非擴 token 協定加 `<<RUN_CMD:...>>` — scope 大。

**方案 C — Meta-command 整合（推薦）**：新增 `/nightlyroutine` handler，bridge 內部依序 await 呼叫四個 handler：
```
daily 03:00 /nightlyroutine
```

### 配置路徑：`${AGENT_CONFIG_DIR}/nightly-routine.json`

Hardcode 內容不彈性（使用者要改順序/加步驟就得改 code），走 JSON 檔：

```json
{
  "steps": [
    { "cmd": "memorytoskill", "label": "萃取 session → skill" },
    { "cmd": "summary",       "label": "當日 summary" },
    { "cmd": "topicreview",   "label": "topic shard 重整" },
    { "cmd": "backup",        "label": "備份" }
  ],
  "continue_on_error": true
}
```

**設計重點**：
- `cmd` 必須 match `COMMAND_HANDLERS` 的 key（`/^[a-z][a-z0-9]*$/` 驗證）
- `label` 可選，Telegram 顯示中文說明比 raw cmd 清爽
- `continue_on_error` 預設 true：單步失敗只 log warn 繼續下一步；設 false 就 `🛑 abort`
- config 檔不存在時 fallback 到 `DEFAULT_STEPS`（跟原四條排程等價）

### 遞迴防呆：reserved_cmds

Agent（或使用者）手抖把 `cmd: "nightlyroutine"` 寫進 steps，會死循環。必擋：

```ts
const RESERVED_CMDS = new Set(["nightlyroutine"]);  // case-insensitive

function isReservedCmd(cmd: string): boolean {
  return RESERVED_CMDS.has(cmd.toLowerCase());
}

// 驗 config 時過濾
const steps = raw.steps.filter((s: any) => {
  if (!validateStep(s)) return false;
  if (isReservedCmd(s.cmd)) {
    console.warn(`[nightly-routine] cmd "${s.cmd}" is reserved, skipping`);
    return false;
  }
  return true;
});
```

未來要把其他 meta-command 加進 reserved 清單也容易。

### handler 實作模板

```ts
async function handleNightlyRoutine(ctx: Context): Promise<void> {
  const cfg = loadNightlyRoutine();
  const { steps, continue_on_error, source } = cfg;

  // 解析 steps → {cmd, label, fn}，fn 從 COMMAND_HANDLERS 查
  const resolved = steps.map((s) => ({ ...s, fn: COMMAND_HANDLERS[s.cmd] }));
  const runnable = resolved.filter((s) => s.fn);
  const invalid = resolved.filter((s) => !s.fn);

  if (invalid.length > 0) {
    await ctx.reply(`⚠ nightly-routine.json 有未知 cmd: ${invalid.map((s) => s.cmd).join(", ")},已跳過`);
  }
  if (runnable.length === 0) {
    await ctx.reply(`❌ nightly routine 沒有可執行步驟`);
    return;
  }

  const sourceTag = source === "file" ? "" : " (default,無 config 檔)";
  await ctx.reply(`🌙 Nightly routine 開始,共 ${runnable.length} 步${sourceTag}`);

  for (let i = 0; i < runnable.length; i++) {
    const step = runnable[i];
    const labelPart = step.label ? ` — ${step.label}` : "";
    try {
      await ctx.reply(`▶ Step ${i + 1}/${runnable.length}: /${step.cmd}${labelPart}`);
      await step.fn(ctx);
    } catch (err) {
      const msg = (err as Error).message;
      await ctx.reply(`⚠ Step ${i + 1}/${runnable.length} /${step.cmd} 失敗: ${msg}`);
      if (!continue_on_error) {
        await ctx.reply(`🛑 continue_on_error=false,中斷後續步驟`);
        return;
      }
    }
  }

  await ctx.reply(`✅ Nightly routine 完成`);
}
```

ctx 直接 forward 給子 handler，**同時支援真 grammY ctx 和 scheduler fake-ctx**（因為兩者 interface 相容，且 fake-ctx 現在也真呼 bot.api）。

### 會 `process.exit` 的步驟必須排最後

Meta-command 的 for-loop 以 `await step.fn(ctx)` 串接。如果某個 handler 內部呼 `process.exit(N)`（例如 `/restart` 最後的 respawn），**process 直接結束，loop 根本不會回到下一 iteration**。後續步驟、`✅ 完成` 結尾訊息、任何 cleanup 都不會發生。

**實例**：`/nightlyroutine` 加入 `/restart` 作為 5 步之一。

```json
{
  "steps": [
    { "cmd": "memorytoskill", "label": "萃取 session → skill" },
    { "cmd": "summary",       "label": "當日 summary" },
    { "cmd": "topicreview",   "label": "topic shard 重整" },
    { "cmd": "backup",        "label": "備份" },
    { "cmd": "restart",       "label": "重啟（讓新 session 吃最新 preamble）" }
  ]
}
```

`restart` **必須在最後**。如果放中間：

- 後面幾步（例如 backup）永遠跑不到
- `✅ Nightly routine 完成` 永遠不會送出
- 不會 throw，也不會走 `continue_on_error=false` 的 abort 訊息 — 完全靜默

### 檢測與防呆

1. **書面文件**：在 config schema 註解寫清楚「自殺型 handler 必須 last」
2. **啟動時 lint**：`loadNightlyRoutine()` 遇到 `restart` / `shutdown` / `kill` 等已知自殺 cmd **不在最後一位**，印 warn 並自動搬到末尾（或 refuse load 要使用者修）

```ts
const SELF_TERMINATING_CMDS = new Set(["restart", "shutdown", "kill"]);

function validateRoutineOrder(steps: Step[]): Step[] {
  const lastIdx = steps.length - 1;
  for (let i = 0; i < lastIdx; i++) {
    if (SELF_TERMINATING_CMDS.has(steps[i].cmd.toLowerCase())) {
      console.warn(
        `[nightly-routine] self-terminating cmd "${steps[i].cmd}" at step ${i + 1} ` +
        `would skip steps ${i + 2}..${steps.length}; moving to last`,
      );
      const [step] = steps.splice(i, 1);
      steps.push(step);
      i--;
    }
  }
  return steps;
}
```

3. **Handler 側自律**：若某 handler 確實會 `process.exit`，在函式 JSDoc 寫 `@terminates true`；review 時以此為 grep 依據

### 推廣到其他 runner

同樣的限制適用於：

| 場景 | 「自殺」步驟 |
|---|---|
| CI 多 job 序列 | `deploy` 若會重啟 runner container |
| Shell script 連鎖 | `exec` 換掉 shell、`reboot`、`systemctl restart self` |
| Bot 的 wizard 步驟 | 觸發 `/restart` token 的對話步 |
| 測試 runner | 把 process 換成 worker 的 step |

**統一規則**：**任何不會把控制權交還給呼叫端的步驟，都必須是序列的最後一步。**

## Goal auto-fire：統一 helper 取代多個入口

`/goal` bridge loop（見 `ms-agent-text-token-signaling` 的「Agent-emit token」）有四條「第一 turn 自動啟動」的入口，早期各自實作：

1. `/goal set <objective>` — 使用者手動設
2. `/goal resume` — paused → active
3. `/restart` auto-resume — 重啟後續接 active goal
4. Scheduled `/goal` — 排程觸發（daily 03:00 /goal ...）

**早期踩雷**：`/goal set` 不 auto-fire，使用者設完以為 loop 開始跑了但其實在等發話（memory 看不到動靜）。一度用「▶️ 開始」inline button 解，但 scheduled `/goal` 觸發時沒人按按鈕，loop 就卡著。最終決定**全部自動 fire，拿掉按鈕**。

### 統一 helper

```ts
async function fireGoalFirstTurn(
  ctx: Context,                  // 真 ctx 或 fake-ctx 都行
  chatId: number,
  userId: number | undefined,
  opts?: { source?: string }     // "goal-set" | "goal-resume" | "restart-resume" | "schedule"
): Promise<void> {
  // 1. 確認 active + budget 未滿
  const state = await goalStore.get(memoryDir, chatId);
  if (!state || state.status !== "active") return;
  if (state.turns_used >= state.max_turns) return;

  // 2. 取 session,檢查 inflight
  const session = await sessions.get(chatId, userId);
  if (session.inflight) return;

  // 3. 組 continuation context
  const continuationPrompt = buildContinuationPrompt(state, opts?.source);
  const continuationContext: ContinuationContext = {
    turnIndex: state.turns_used + 1,    // ← 關鍵:turns_used+1 不是寫死 1
    maxTurns: state.max_turns,
    objective: state.objective,
    lastReason: state.last_reason,
  };

  // 4. fire-and-forget 呼叫 runPrompt
  runPrompt(ctx, session, continuationPrompt, continuationContext)
    .catch((err) => console.error(`[goal-auto-fire ${opts?.source}] ${err.message}`));
}
```

### 四條入口都改用 helper

```ts
// /goal set
await ctx.reply(`⊙ Goal set (${budget}-turn): ${objective}\n↻ 正在啟動 turn 1/${budget}…`);
void fireGoalFirstTurn(ctx, chatId, userId, { source: "goal-set" });

// /goal resume
await ctx.reply(`▶️ Goal resumed`);
void fireGoalFirstTurn(ctx, chatId, userId, { source: "goal-resume" });

// /restart auto-resume (在 maybeAutoResumeGoalAfterRestart 內)
void fireGoalFirstTurn(ctx, chatId, userId, { source: "restart-resume" });

// Scheduled /goal (handleGoal via fake-ctx 自動走同路徑)
```

### Restart reason 接力

`/restart` 帶 `<<RESTART:reason>>` token 走的 case，重啟後 continuation prompt 要帶上 reason：

```ts
function buildContinuationPrompt(state: GoalState, source?: string): string {
  const base = `Continue toward your standing goal (turn ${state.turns_used + 1}/${state.max_turns}).\nObjective: ${state.objective}`;

  if (source === "restart-resume" && state.last_restart_reason) {
    return `[bridge restart — previous turn requested restart: ${state.last_restart_reason}]\n\n${base}`;
  }
  if (state.last_reason) {
    return `${base}\n\nPrevious turn preview: ${state.last_reason.slice(0, 200)}`;
  }
  return base;
}
```

Agent turn 2 開頭就看到「上次為何重啟」，不會又觸發同樣條件的重啟（避免迴圈）。

### 設計教訓

- **單一 helper 涵蓋多入口**比各入口各寫一份穩；行為不漂移
- `turnIndex = turns_used + 1` 不寫死 1，配合 restart resume 的連號語意
- ▶️ 開始按鈕在 schedule 場景悖論（沒人按），拿掉改 auto-fire 三邊一致
- 按鈕也丟棄後 `buildGoalStartKeyboard` / `goal-start` callback 分支刪掉 ~80 行

## 為什麼不用 cron daemon / node-cron / agenda

- **node-cron**：沒 persistence，restart 掉光
- **agenda**：吃 MongoDB，過重
- **cron-parser / croner**：純 parser，仍要自己 persist + dispatch
- **作業系統 cron / Windows Task Scheduler**：跨機器部署不一致、不能 per-user、要 spawn 新 process 很笨重

本 pattern 的優勢是**就用 bridge 已有的 process + 一個 JSON file**，persistence 與 recurring 都用最小 primitives 自己做，避開任何外部依賴。規模到數百個同時排程才需要換。

## 相關

- **ms-agent-text-token-signaling** — `<<SCHEDULE:...>>` token 是該協定的一個實例；ASK 按鈕用在 /schedule wizard；fail-open + budget 設計
- **ms-agent-long-term-memory** — 同樣檔案式持久化思路；排程 store 與 facts 放在同一個 `MEMORY_DIR`
- **ms-acp-protocol-limitations** — ephemeral AcpClient 同 session ACP client 用法；排程觸發時新開一條才不擠使用者當下的 session
- **ms-streaming-token-pipeline** — 排程觸發 runPrompt 類 handler 的 streaming 行為細節
