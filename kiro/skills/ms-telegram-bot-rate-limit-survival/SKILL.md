---
name: ms-telegram-bot-rate-limit-survival
description: 當 Telegram bot 對使用者 chat 串 streaming edit 或連發多則訊息、遇到 429 Too Many Requests / retry_after 愈累積愈長（60s→183s）、grammY autoRetry 超過 maxDelaySeconds 拋錯、或需要設計「限流期間凍結 UI + 限流結束後自動補發」時使用
---

# Telegram Bot 429 Rate Limit 存活指南

## 概述

Telegram Bot API 對單一 chat 有硬性限制：**1 訊息 / 秒、edit 大約 1 次 / 秒**。streaming bot（每 1.2s editMessage 刷 typing 進度）很容易撞到。更糟的是：**retry_after 會隨近期違規頻率累加**，從幾秒漲到 60、120、甚至 183+ 秒。限流期間繼續發訊息會重置或延長冷靜期，**唯一對策是安靜等待**。

核心原則：**預防（主動 pacing + 拉長 edit 間隔）勝於救火；真的發生了就 freeze UI、queue 失敗訊息、靠 observer transformer 在 autoRetry 放棄時攔 `retry_after` 並排程 recovery。**

## 何時使用

- Streaming reply 長回覆 edit 到一半卡住不動、使用者以為 bot 掛了
- log 看到 `Call to 'sendMessage' failed! (429: Too Many Requests: retry after N)`
- 本來幾秒的 retry_after 愈滾愈大（典型：30s → 79s → 167s → 183s）
- grammY `autoRetry` plugin 拋 `MaxDelayExceededError`
- 連發多則分段訊息，中間某一則開始失敗
- 想實作「限流期間暫停 edit、結束後自動送通知 + 補傳」

**不要用在：**
- 一般 API 失敗（network 錯、auth 失敗）— 那些不是 rate limit
- Telegram 30/sec 的**全 bot 廣播上限**（bot 同時對多個 chat 送訊息才會撞；UX 不同，另解）
- 非 Telegram 的限流（Discord / Slack 語意不一樣）

## Telegram 429 的核心機制

這幾條事實決定所有設計選擇：

| 事實 | 含意 |
|---|---|
| 單一 chat 上限約 1 msg/sec | 1.1s pacing 最安全，**每則送完 sleep 一下** |
| editMessage 也算在類似限額 | streaming edit 間隔要 ≥ 2s 才保守 |
| `retry_after` 是 **累加懲罰**，初次 3–5s 可以漲到 60–120s 甚至 183s+ | 不能重試太積極；**限流期間發任何訊息都會延長冷靜期** |
| 限流期間通知使用者「正在限流」的訊息**也會被擋** | 必須等冷靜期結束才能送通知；靠 timer schedule |
| autoRetry plugin `maxDelaySeconds` 預設 30 太小 | 超過就直接拋錯，訊息徹底丟失 |

## 設計模式（分三層）

### 第 1 層：主動降噪（平常就做）

目標：不讓限流發生。

```ts
// STREAM_EDIT_INTERVAL_MS 建議值
// 預設 1200 太積極；正式環境設 2500
const streamEditInterval = Number(process.env.STREAM_EDIT_INTERVAL_MS ?? 2500);
```

連發多則分段訊息（final render chunks）時**每則之間 sleep 1100ms**：

```ts
const TG_CHAT_PACING_MS = 1100;   // ≤ Telegram 1 msg/sec chat 限額

for (let i = 0; i < chunks.length; i++) {
  if (i > 0) await sleep(TG_CHAT_PACING_MS);
  try {
    await ctx.reply(chunks[i]);
  } catch (e) {
    // 見第 3 層
    queuePendingMessage(chatId, chunks[i]);
  }
}
```

### 第 2 層：observer transformer 攔截 raw response

grammY 的 `autoRetry` plugin **自己會消化 429**，外層 catch 不到原始 `parameters.retry_after`。要另外塞一個 transformer 在 autoRetry 內側，觀察每筆 Telegram raw response。

```ts
// 先 use autoRetry（外層，包住一切），再 use observer（內層，看得到 raw response）
bot.api.config.use(
  autoRetry({
    maxRetryAttempts: 3,
    maxDelaySeconds: Number(process.env.TG_AUTORETRY_MAX_DELAY_SECONDS ?? 120),
    // 預設 30 太小，會在「累積懲罰」時直接拋錯。設 120 才吸收得住
  }),
);

let rateLimitedUntil = 0;
let lastRateLimitSecs = 0;
let rateLimitChatId: number | null = null;
let rateLimitRecoveryTimer: NodeJS.Timeout | null = null;

bot.api.config.use(async (prev, method, payload, signal) => {
  const res = await prev(method, payload, signal);
  // res 的型別是 ApiResponse<...>，ok:false 時有 parameters.retry_after
  if (!res.ok && res.parameters?.retry_after) {
    const secs = res.parameters.retry_after;
    const until = Date.now() + secs * 1000;
    if (until > rateLimitedUntil) {
      rateLimitedUntil = until;
      lastRateLimitSecs = secs;
      rateLimitChatId = (payload as any)?.chat_id ?? rateLimitChatId;
      console.warn(
        `[rate-limit] Telegram 429: retry_after=${secs}s chat=${rateLimitChatId} method=${method} — pausing edits until ${new Date(until).toISOString()}`,
      );
      scheduleRecovery(secs);
    }
  }
  return res;
});
```

### 第 3 層：freeze UI + queue + recovery timer

限流發生時：
1. `editNow` 提早 return（不要再送 API call，會延長冷靜期）
2. 失敗的連發 chunks 塞進 `pendingMessages` queue
3. Recovery timer 在 `retry_after` 秒後觸發：先送「限流解除」獨立通知 → flush queue（每則 pacing 1.1s）

```ts
const pendingMessages: Array<{ chatId: number; text: string }> = [];

function queuePendingMessage(chatId: number, text: string) {
  pendingMessages.push({ chatId, text });
}

function scheduleRecovery(secs: number) {
  if (rateLimitRecoveryTimer) clearTimeout(rateLimitRecoveryTimer);
  rateLimitRecoveryTimer = setTimeout(async () => {
    const waited = lastRateLimitSecs;
    const chatId = rateLimitChatId;
    console.log(`[rate-limit] recovered after ${waited}s — flushing ${pendingMessages.length} pending message(s)`);

    // 1. 送獨立通知（此時應該已通過冷靜期，可以發）
    if (chatId) {
      try {
        await bot.api.sendMessage(chatId, `⏳ Telegram 限流解除（等了 ${waited}s）— 現在可以正常收發訊息了`);
      } catch (e) {
        // 若再次 429，observer 會再 schedule 新 timer
      }
    }

    // 2. Flush queue，每則 pacing
    while (pendingMessages.length > 0) {
      const { chatId, text } = pendingMessages[0];
      try {
        await bot.api.sendMessage(chatId, text);
        pendingMessages.shift();
        await sleep(1100);
      } catch (e) {
        // 若又被 429，保留在 queue 裡等下次 recovery
        break;
      }
    }

    rateLimitedUntil = 0;
    rateLimitRecoveryTimer = null;
  }, secs * 1000 + 200);   // 加 200ms 緩衝避免邊界
}

// Streaming edit skip
async function editNow(content: string) {
  if (rateLimitedUntil > Date.now()) {
    return;   // 限流期間跳過，不發 API call；避免 bridge 主迴圈被 autoRetry 的 pause 塞住
  }
  await ctx.api.editMessageText(chatId, placeholder.message_id, content);
}
```

## 範圍控制（該 queue 什麼不該 queue 什麼）

不是所有訊息都值得 queue 補發。挑保護重點：

| 訊息類型 | 要 queue 嗎 | 理由 |
|---|---|---|
| Streaming turn 的 final render chunks | **是** | 使用者等這個回覆，丟了就真的沒了 |
| 限流期間的 heartbeat edit | 否 | 下次成功 edit 會自動蓋掉，不需補 |
| 命令回覆（/help、/save 等短訊息） | 否 | 瞬態、使用者重試成本低 |
| 檔案傳輸（sendDocument / sendPhoto） | 否 | queue shape 要存 path 而不是 text，複雜度高；使用者會重請求 |
| 「限流解除」通知本身 | 否 | 已由 recovery timer 負責 |

保住 streaming final chunks 就夠解 90% 的痛點。

## Console log 策略（Edge-triggered，不洗版）

在限流**進入**與**解除**兩個邊緣各印一次，其他時刻（例如每次 editNow skip、每次 heartbeat）**刻意不印**：

```
[rate-limit] Telegram 429: retry_after=79s chat=763055942 method=editMessageText — pausing edits until 2026-04-29T08:47:12.000Z
...（限流期間，靜默）...
[rate-limit] recovered after 79s — flushing 3 pending message(s)
```

不洗版很重要 — bridge 通常跑在同一個 terminal，洗版會蓋掉真正有用的 debug log。

## Common Mistakes

| 錯誤 | 修正 |
|---|---|
| `STREAM_EDIT_INTERVAL_MS=1200` | 正式環境至少 2500ms；每 2 秒 editMessage 才安全 |
| 連發分段訊息沒 pacing | 每則中間 sleep 1100ms（≤ 1 msg/sec 留 10% 餘裕） |
| `autoRetry({ maxDelaySeconds: 30 })` | 設 120，才吸收得住累積懲罰；小於 60 幾乎一定會撞拋錯 |
| 限流期間繼續送訊息（包括錯誤通知） | 任何送出都會延長冷靜期 — freeze 住，靠 recovery timer 補 |
| 在 autoRetry **外層** 加 transformer 想看 `retry_after` | autoRetry 把 429 處理掉了，外層看不到；observer 要塞在**內側**（後 use） |
| 對每次 editNow skip 都 console.log | 洗版；只在 edge 印一次 |
| 用 `ctx.reply` 的 error 當觸發點 queue | 不全面；observer transformer 才能攔到所有 method 的 429 |
| Recovery timer 沒清舊值 | 下一次 429 到來時新 timer 跟舊 timer 會同時觸發 |
| 邊界秒數剛好取整 | Timer 加 100–200ms 緩衝，避免 server 還沒準備好 |
| 以為 Telegram 會分片大訊息 | 錯，**單則硬上限 4096 字元**，超過被 silent truncate（API 不回 error、訊息尾巴直接消失） |
| 長總結一次送、尾段被截在句中 | 控制在 ~3500 字元以內（留 margin 給 token、footer）；或 bridge 端 `splitForTelegram` 切多則帶 `(n/m)` |

## 長回覆的訊息長度規劃

Telegram API **單則文字訊息硬上限 4096 字元**（含標點），超過**不會回 error**、server 直接丟尾段。bridge 層或 agent 層都要自己擋。

三種策略，由輕到重：

1. **Agent 自我限制**：長總結寫到 3500 字元左右就收；需要更長就主動切兩則（「以上是前半，接下來是後半」）。適合對話式 UX。
2. **Bridge 端 `splitForTelegram`**：bridge 的 final render 函式偵測 `buffer.length > TG_MAX`（通常 3900，留 margin）就切多則，每則標 `(1/2)`、`(2/2)`。不需要 agent 配合。
3. **Streaming 期間 intermediate edit 的長度檢查**：streaming 過程中 `body + toolsPrefix + cursor` 整段長度都要算進去；只對 `body` 做 `slice(-TG_MAX)` 是不夠的（toolsPrefix 可能也塞 5 行 tool log）。

### Bridge 側實作重點

```typescript
// 不夠安全：只截 body
if (body.length > TG_MAX) body = "…" + body.slice(-TG_MAX);
return tools + body + cursor;   // ← tools 可能讓整段再超上限

// 正確：整段算長度
const combined = tools + body + cursor;
if (combined.length > TG_MAX) {
  return "…" + combined.slice(-(TG_MAX - 1));
}
return combined;
```

**符號衝突**要特別小心：Telegram 訊息若開 `parse_mode: "Markdown"`，未閉合的 `_` / `*` / `` ` `` 會讓 server reject（回 400），**不是截斷而是整則訊息消失**。streaming edit 切字的位置不該停在 entity 中間。最保險是 streaming 不開 parse_mode，只在 `/help` 等固定文案用。

### 診斷「訊息尾巴不見」

使用者報「訊息尾段被截掉」時，四段檢查：

```
1. 肉眼字元數估算 vs 4096
   → 接近或超 → Telegram 截，無法從 bridge 側修
   → 遠低於 4096 → 不是長度問題

2. bridge console 有沒有 `delivered 1/1 chunks (stopReason=end_turn, bufferChars=X)`
   → bufferChars 跟使用者看到的長度差很多 → agent stream 在 bridge 這端就提早結束
   → bufferChars 對得上 → bridge 側已經只送了這麼多

3. 是否最後一則
   → 不是最後一則但尾段沒了 → 很可能 parse_mode 吃 entity 或 API 400 吞訊息
   → 是最後一則且後面沒更多內容 → agent 本來就想在此收尾

4. `stopReason`
   → end_turn 但 bufferChars < 100 → agent 提早放棄或撞 output token 上限
   → max_tokens → model 輸出到上限
```

## 診斷流程（看到 retry_after 變大時）

```
1. log 近 10 分鐘的 retry_after 序列
   → 「3s, 15s, 30s, 79s, 167s」這種遞增模式 = 累積懲罰
   → 繼續發會更長；立刻 freeze

2. 查 streamEditIntervalMs 設定
   → < 2000ms 即為風險；拉高

3. 查 chunk 連發是否有 pacing
   → 沒有就是主因；加 1100ms sleep

4. 查 autoRetry maxDelaySeconds
   → <= 60 遇到 79s 以上就直接拋；拉到 120
```

## 為什麼 retry_after 會累加（Telegram 側行為）

Telegram server 側對「最近違規的 bot × chat」維護一個動態 cooldown。每次撞限：

- 初犯：retry_after 小（3–5s）
- 近期再犯：基底 × 2、× 4...
- 限流期間繼續發（即使只是一次 sendMessage 嘗試）：**重新計時 + 可能進一步拉長**

這不是記錄在文件裡的行為，而是觀察出來的。結論就是一條：**看到 429 = 徹底停手，讓 timer 接管**。別試圖「小心一點繼續發」。

## 相關

- **ms-windows-shell-exit-code-false-positive** — 同主題的「看起來失敗其實成功 / 看起來成功其實失敗」，都在講 Windows + 網路邊界的誤判
