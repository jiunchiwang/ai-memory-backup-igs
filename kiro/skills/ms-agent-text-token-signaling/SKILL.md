---
name: ms-agent-text-token-signaling
description: 當 LLM agent 需要觸發 host 端動作（傳檔、開網址、執行指令）但協定不允許 agent 端發起自訂 RPC、或想在 streaming 文字回覆中加上 side effect 又不破壞聊天 UX 時使用
---

# Agent 文字 Token 訊號

## 概述

當 LLM agent 只能輸出文字（沒有自訂 RPC、也沒有 function calling 可用）時，就在回覆中嵌入一個格式良好的標記 token，讓 host 在顯示給使用者之前把它「剝除並執行」。這種方式零協定成本就能做到「agent 觸發 side effect」。

核心原則：**agent 輸出文字 token → host 在 streaming 時掃描 → host 從顯示內容剝除 + 執行動作 → 使用者看到乾淨文字 + 動作結果。**

## 何時使用

- 你在做 **ACP / MCP / 自訂 bridge**，而 agent 端沒辦法對 host 發任意 RPC
- 不能（或不該）加 function calling 工具，因為動作是 host-UI 特定的（例如「把這個檔案附到這個 Telegram 聊天室」）
- 你需要 agent 觸發「只有 host 能做」的 side effect（傳 Telegram 檔案、複製到剪貼簿、開編輯器、顯示通知）
- Streaming 文字回覆已經就位

**不要用在：**
- 有 function calling / tool use API — 用那些更安全、有結構
- 動作需要複雜參數（改用 MCP tool）
- Agent 本地跑、對子系統有直接 API 權限

## 樣式

```
Agent 輸出串流：
  "已幫你附上檔案。<<SEND_FILE:F:\AI\facts.md>> 有需要再跟我說..."
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                  host 把這段取出、執行動作、再把它從顯示文字拿掉

使用者看到：
  "已幫你附上檔案。 有需要再跟我說..."
  [檔案附件]
```

### Token 形狀

Token 要：

1. **有清楚的前後綴** — `<<SEND_FILE:...>>` 對 regex 友善、在自然文字裡幾乎不會出現
2. **參數直接內嵌** — 參數放在 token 裡，不要分開傳
3. **每個 token 一個單一責任** — 一個 token 一個檔案；一次回覆裡多個 token 也 OK

```
<<SEND_FILE:<絕對路徑>>>
<<OPEN_URL:<url>>>
<<COPY:<text>>>
<<NOTIFY:<title>|<body>>>
```

避免看起來像一般標點、或常見 LaTeX/markdown 樣式的 token。

## 實作（Streaming 友善）

兩個抽取點都很重要：**streaming 中**（從顯示文字剝除）和 **stream 結束**（對 final buffer 執行動作）。

```ts
const SEND_FILE_RE = /<<SEND_FILE:([^>]+)>>/g;

/** 從顯示文字剝除 token，對部分 buffer 也安全。 */
function stripSendTokens(text: string): string {
  return text.replace(SEND_FILE_RE, "").replace(/\n{3,}/g, "\n\n");
}

/** 從最終完整 buffer 抽出不重複的路徑。 */
function extractSendTokens(text: string): string[] {
  const seen = new Set<string>();
  for (const m of text.matchAll(SEND_FILE_RE)) {
    const path = m[1].trim();
    if (path) seen.add(path);
  }
  return [...seen];
}

// Streaming 時（edit 訊息）：
function renderReply(buffer: string): string {
  return stripSendTokens(buffer);
}

// Stream 結束時：
async function finalize(ctx: Context, finalBuffer: string) {
  const paths = extractSendTokens(finalBuffer);
  const cleanedText = stripSendTokens(finalBuffer);

  // 1. 送乾淨文字作為可見訊息
  await ctx.reply(cleanedText);

  // 2. 每個 token 各自執行 side effect
  for (const p of paths) {
    await sendFileWithWhitelist(ctx, p);   // 重用現有白名單程式碼
  }
}
```

### 為什麼 streaming 時就要剝除

如果不在 streaming 時剝，使用者會看著 token 一字一字出現（`<<SEND_FIL...` → `<<SEND_FILE:F...`）。又醜又令人困惑。剝除讓 streaming UX 保持乾淨。

## 教 Agent 用 Token

Agent 要知道 token 存在、也要知道什麼時候用。把這段注入**session preamble**（或 system prompt）：

```
[Telegram bridge tool]
要把檔案送到使用者的 Telegram 聊天室時，在你的回覆中加入 token：
`<<SEND_FILE:<絕對路徑>>>`
bridge 會在訊息送出前移除 token，並把該檔案以 Telegram file 附上
（圖片 ≤10MB 走 photo，其餘走 document）。
路徑必須位於允許的根目錄（TG_SEND_ROOTS 或 ACP_SESSION_CWD）底下。
可同時出現多個 token。

只有使用者要求「傳檔案給我」這類意圖時才加 token；一般討論不要自動產生。
[End tool]
```

Prompt 幾個關鍵：

- **展示精確語法** — 一個具體範例勝過描述
- **說明 pipeline** — 「bridge 會移除 token」告訴模型「token 不會污染回覆」
- **明列限制** — 模型就不會嘗試它摸不到的路徑
- **給使用時機** — 「只有被要求時」防止亂傳檔

## 安全

文字 token **不可信** — agent 本質上是 user input。一定要：

1. **驗證 payload** — 路徑過白名單（見 `ms-windows-path-prefix-check` skill）、URL 過 scheme/domain 檢查
2. **Per-chat 限流** — 每次回覆的檔案數要設上限
3. **記錄每個動作** — audit log 很便宜
4. **優雅拒絕** — 不良 token 從顯示中默默丟掉，在 server 端記 log：

```ts
if (!isUnderAllowedRoot(path, config.allowedRoots)) {
  console.warn(`[chat ${id}] SEND_FILE refused (not under roots): ${path}`);
  return;   // 默默丟掉 — 不要每個壞 token 都對使用者顯示錯誤
}
```

## 與其他做法比較

| 做法 | 優點 | 缺點 | 適合情境 |
|---|---|---|---|
| **文字 token（本 skill）** | 零協定工作，任何會輸出文字的 agent 都適用 | 要教 agent，結構性弱 | Host 特定 UI 的 side effect |
| Function calling / tool use | 結構化、有驗證 | 需要 API 支援 | 支援 tool 的 API 後端 |
| MCP tool | 整合度佳、可重用 | 設置成本、增加 runtime 依賴 | 跨 agent 重用的工具 |
| 檔案系統 watch | 不用改 agent | 延遲、狀態會過期 | 批次工作流 |
| 自訂 JSON-RPC | 乾淨 | CLI 不允許 agent 發 RPC 就無法做（常見） | 你同時控制兩端 |

**對 ACP 而言**（多數 CLI 不允許 agent 主動發 RPC — 見 `ms-acp-protocol-limitations`），文字 token 通常是正解。

## 常見錯誤

| 錯誤 | 修正 |
|---|---|
| Token 太簡單（`[FILE]`、`{path}`） | 會跟一般文字撞；用 `<<PREFIX:...>>` |
| 只在 stream 結束才剝除 | Streaming 時 token 閃爍；每次 render 都要剝 |
| 路徑沒去重 | 同一個 token 出現兩次就傳兩次 |
| 每個壞 token 都回錯誤給使用者 | Server 端 log、使用者端默默丟掉 |
| 跳過白名單 | Agent 可以拿到磁碟上任何檔案 — 要把 token 當不可信輸入 |
| Preamble 沒寫說明 | Agent 永遠不會產生 token；然後你在想為什麼「沒作用」 |
| 搭配啟發式路徑掃描「幫忙」補 token | 見下方「切勿搭配啟發式掃描」 |
| 在 agent prose 裡散文裸寫合法 token（解釋、示範、討論）| Host bridge 不猜意圖，合法字面一律 strip + 執行 side effect，造成 `.usage.json` 虛增、無意排程、假宣告 GOAL_DONE；且 token 被吃掉後使用者看到的句子殘破。規則：展示字面一律 backtick 或 fence 包；討論協定用 `<name>` / `<reason>` 這類非法佔位符；真要觸發時訊息尾端獨立裸寫一個 |

## 切勿搭配啟發式掃描（實戰警示）

初版 bridge 常見設計：除了 `<<SEND_FILE:...>>` token，再加一條「備援」機制——用 regex 掃回覆裡長得像絕對路徑的字串（例如 `F:\...\*.md`），自動當檔案傳出去。**這條路最終都要拔掉，不要加。**

### 為什麼啟發式掃描一定會踩雷

Agent 的文字回覆裡會提到絕對路徑的情境非常多：

- 引用 log：`[chat 763055942] sent ...: F:\AI\AIMemory\facts-763055942.md`
- 報告錯誤訊息：`ENOENT: no such file or directory, stat 'F:\AI\telegram-kiro-bridge\...'`
- 回報工作成果：`ok: appended to F:\AI\AIMemory\facts-763055942.md`
- 文件示範：`路徑對應 assets/game/Prefab/MainGame.prefab`

這些**都不是傳檔意圖**，但啟發式掃描無法分辨。使用者可能只是問「為什麼剛剛有錯」，agent 引用 log 後整個 facts 檔就被自動傳出來。

### 唯一穩定的協定：**明確 token 才傳**

```
agent 沒加 <<SEND_FILE:...>> → bridge 不動作（不論回覆裡提幾次路徑）
agent 加了 <<SEND_FILE:...>> → bridge 傳該檔（並過白名單）
```

### 拔除啟發式掃描時的連帶工作

- 刪掉 `PATH_RE` / `sendFilesFromText` 等函式
- prompt 有兩條路徑（streaming 與 non-streaming）時，兩處都要拔
- preamble 明確告訴 agent「產生／修改／儲存檔案這類請求本身不構成傳檔意圖——完成後只需回報絕對路徑」
- 再加一條「不確定時預設不加 token」的兜底規則

### 保留一個開關 flag 也不建議

有人會想加 `TG_AUTOSEND_PATHS=1` 當 escape hatch。實務上：

- 預設值永遠是關閉的（否則上面的坑全部回來）
- 使用者幾乎不會開
- 開關本身多一層認知負擔
- 真的有批次傳檔需求時，bot 指令 `/sendfile <path>` 更直接

直接拔乾淨，比留開關更清爽。

## 進階變形 1：互動式 Token（ASK 按鈕）

`SEND_FILE` 是「單向 side effect」— agent 嵌 token、bridge 執行、結束。但**互動式**的情境（agent 要使用者做選擇）需要雙向迴路：token 要在使用者端渲染成 UI 元素（inline keyboard），**按下後 bridge 再注入一則 user turn 回送 agent**。

### Token 語法

```
<<ASK:question_id|key1=label1|*key2=label2|...|keyN=labelN>>
```

- `question_id`：agent 自編，`[a-zA-Z0-9_-]{1,32}`
- 每個 option 是 `key=label` 形式（`=` 必填，**不能只有 key**，否則 parser reject 整個 token）
- `key`：`[a-zA-Z0-9_-]{1,20}`
- `label`：顯示給使用者看，≤ 40 字元，**不可含 `|` 或 `=`**
- 每題 1–8 個 options
- 單一 option 可用 `*` 前綴標記為推薦（整題最多一個）
- 整段**必須在同一行**

### 點擊後的雙向流程

```
1. Agent 嵌 <<ASK:place|final=final chunk|*separate=另開訊息>>
2. Bridge 剝 token → 在最後一則訊息掛 inline keyboard
   （推薦選項 label 前加 ⭐，並額外渲染「👉 照你的建議」全寬鈕）
3. Bridge 把 askRegistry.set(messageId, askEntries)
4. 使用者點按鈕 → Telegram 送 callback_query
5. Bridge:
   a. answerCallbackQuery（關 spinner）
   b. editMessageText 移除 keyboard + 追加「→ 你選擇了：X」
   c. 把選擇以 [ASK:place] separate 格式送回 agent 當新 user turn
6. Agent 收到時能辨認是 ASK 回答，按 question_id 找出脈絡繼續
```

### Callback data 編碼

Telegram `callback_data` 上限 64 bytes，格式：

```
A:{question_id}:{key}
```

例如 `A:place:separate`。`A:` 前綴讓 bridge 與其他 callback 種類（如 `run:`、`help:`）分流。

### 解析（含防禦性驗證）

```ts
const ASK_RE = /<<ASK:\s*([^>\r\n]+?)\s*>>/g;
const ASK_ID_RE = /^[a-zA-Z0-9_-]{1,32}$/;
const ASK_KEY_RE = /^[a-zA-Z0-9_-]{1,20}$/;
const ASK_LABEL_MAX = 40;

function parseAskInner(inner: string): AskEntry | null {
  const reject = (reason: string) => {
    console.warn(`[ASK] malformed token rejected: ${reason} | inner="${inner.slice(0, 200)}"`);
    return null;
  };
  const parts = inner.split("|").map(s => s.trim()).filter(Boolean);
  if (parts.length < 2) return reject(`too few parts`);
  const [questionId, ...optParts] = parts;
  if (!ASK_ID_RE.test(questionId)) return reject(`question_id "${questionId}" invalid`);
  if (optParts.length < 1 || optParts.length > 8) return reject(`option count ${optParts.length} out of 1..8`);

  const options: Array<{ key: string; label: string; recommended: boolean }> = [];
  let rec = 0;
  const seen = new Set<string>();
  for (const p of optParts) {
    const eq = p.indexOf("=");
    if (eq <= 0) return reject(`option "${p}" missing "key=label"`);
    let key = p.slice(0, eq);
    const label = p.slice(eq + 1).trim();
    const recommended = key.startsWith("*");
    if (recommended) { key = key.slice(1); rec++; }
    if (!ASK_KEY_RE.test(key)) return reject(`key "${key}" invalid (need [a-zA-Z0-9_-]{1,20}, got length ${key.length})`);
    if (label.length === 0 || label.length > ASK_LABEL_MAX) return reject(`key "${key}" label too long (got ${label.length}, max ${ASK_LABEL_MAX})`);
    if (label.includes("|") || label.includes("=")) return reject(`label contains forbidden char`);
    if (seen.has(key)) return reject(`duplicate key "${key}"`);
    seen.add(key);
    options.push({ key, label, recommended });
  }
  if (rec > 1) return reject(`more than one recommended option`);
  return { questionId, options };
}
```

**每個 reject 都 `console.warn` 原因**是關鍵：沒 log 的話 agent 寫錯 token 時只會看到「token 原文外顯」完全不知道哪裡壞。

### Bridge 側主動發 ASK：replyWithAsk helper

當 bridge 自己（不是透過 agent final render）也要送含 `<<ASK:...>>` 的訊息（例如 `/schedule` wizard），要跟 agent 路徑共用同一套「extract → inline keyboard → registry」流程，不能直接 `ctx.reply(含 token 原文)`：

```ts
async function replyWithAsk(ctx: Context, text: string): Promise<void> {
  const { clean, asks } = extractAskTokens(text);
  const markup = asks.length > 0 ? buildAskKeyboard(asks) : undefined;
  const msg = await ctx.reply(clean, { reply_markup: markup });
  if (asks.length > 0) {
    askRegistry.set(msg.message_id, asks);
  }
}
```

少了這步 token 會原文顯示。這是非常容易忘的 bug——看到使用者端 `<<ASK:...>>` 原文、按鈕沒出現，通常就是 bridge 側有某個路徑直接 `ctx.reply` 了含 token 的字串。

### Agent 端使用規約

1. **只在 code block 外的實際使用時機產 token** — `maskCodeRegions` 會把 code fence 內的 ``<<ASK:...>>`` 遮掉不渲染，利用這點在文件 / 範例中安全展示 token 語法
2. **推薦選項用 `*` 前綴的同一個 key，不要複製一個 `*key` 再加一個 `key`** — parser 會判 duplicate key 整個 reject
3. **每個 option 必須 `key=label`，只有 key 沒 `=` 會讓整題 reject**
4. **逐欄檢查字元數**：ASK_KEY_MAX=20、ASK_LABEL_MAX=40、ID ≤32、options 1-8；超限整 token 被拒
5. **多題同訊息**：agent 一則回覆可嵌多個 `<<ASK:...>>` 題目。使用者只答其中一題時，agent 下則應**把沒答的題目重新嵌 ASK 補問**（只處理「多題只答一題」情境，不處理「沒點就打字」）
6. **選項說明過長時，先在訊息正文以 1./2./3. 列出完整說明，token 的 label 只放簡短標題**（避免踩 40 字上限）
7. **實測踩雷：中英混雜 label 要逐字算長度，別靠眼睛估**。parser 用 `label.length`（JavaScript UTF-16 code units），對下列都算 **1 char**：
   - 英文字母 / 數字 / 空白 / ASCII 標點
   - 中文全形字
   - 全形標點（，。「」（）、）

   `commit 1`（連空白）是 8 char，`topic-rules.ts` 是 13 char，所以 **label 裡只要有完整短句、加上 1-2 個 ASCII 片段，就很容易踩 40 字上限**。實例：

   ```
   ❌ 43 char：把 topic-rules.ts 進 commit 1、外部化改動留 commit 2
   ```

   修法有三條，優先序由上到下：

   - **壓縮 label，詳述搬到正文**：label 只寫「拆兩筆 commit」「合成一筆」「跳過」這類 ≤ 20 字的標題；上面用 `1.` / `2.` / `3.` 把完整說明列出來
   - **key 當語意承載**：`merge_topic_rules=拆兩筆 commit` 讓 key 負責表意，label 只要人類看得懂差異即可
   - **真的寫得下才逐字算**：如果堅持放長 label，心算時**英文字母也算 1 char**（不只中文算 1 char），42 字就炸

   label 炸掉時 bridge log 會出現：

   ```
   [ASK] malformed token rejected: key "merge_topic_rules" label too long (got 43, max 40): "把 topic-rules.ts 進..."
   ```

   使用者端會看到 `<<ASK:...>>` 原文外顯、沒按鈕。看到這個樣子 = 你有 label 踩 40 字上限，回上一則自己的 token 逐欄算一次。

   **習慣：嵌 ASK 前先在腦中把每個 label 倒過來數一次字元**，或者「任何 label 只要出現完整短句 + 逗號 + 接續說明」就強制走壓縮路徑。寧可 label 偏短也不要超界——ASCII label 最多給自己留 30 字 margin,中文 label 35 字 margin。

8. **絕不在自己的 prose（散文、說明、對話討論）裡裸寫合法 token 字面**。這是 agent 端最容易自我污染的坑。

   **現象**：你在向使用者解釋 token 協定、示範格式、討論某支 skill 時，順手寫了 `<<SKILL_USED:ms-diagnose|real trigger example>>` 這種**格式完全合法**的字串。你的意圖是「示範」，但 host bridge 的 `transform()` / observer 不會猜你的意圖——看到合法 token 就**真的 strip + 執行 side effect**：

   - `<<SKILL_USED:...>>` → `.usage.json` 被 markUsed、use_count 虛增
   - `<<GOAL_DONE:...>>` → 若 goal active 直接宣告完成，loop 停
   - `<<SEND_FILE:...>>` → 實際傳檔（若路徑過白名單）
   - `<<SCHEDULE:...>>` → 實際註冊排程
   - `<<RESTART:...>>` → 若 goal active 且未到 cap，agent 被真的重啟
   - `<<ASK:...>>` → 使用者聊天室冒出莫名其妙的 inline keyboard

   **更糟的連鎖**：token 被 strip 後，原 prose 文字從使用者端消失，使用者看到的版本少了那一段，句子殘破。如果 host 有 `hideTrailingUnterminatedToken`（見 `ms-streaming-token-pipeline`），訊息**結尾附近**出現的 token 字面還會觸發「opener 沒 close 就換 …」把整段尾巴截掉——CJK 訊息尾常有 `」`、`。`、backtick，一被誤判成半截 token 就整句斷尾。

   **三條寫作規則**：

   | 情境 | 正確寫法 | 錯誤寫法 |
   |---|---|---|
   | 想**真觸發**一次 | 訊息尾端獨立一行、裸寫一個合法 token | 前文先寫一次示範、後面又寫一次真的——前面那個會先被吃 |
   | 想**展示 token 字面**給使用者看 | 用 backtick 包：`` `<<SKILL_USED:name\|reason>>` `` 或 fenced code block；`maskCodeRegions` 會保護整段不被掃 | 裸寫在散文裡（host 真的觸發）|
   | 想**討論 token 格式**（寫 skill、回答協定問題）| 用 `...` 或 `name` / `reason` 這類**非法佔位符**，例如 `<<SKILL_USED:<skill-name>\|<reason>>`；parser reject 後 fail-open 留字面 | 用合法的 `ms-diagnose` / `ms-grill-with-docs` 當示範名 |

   **一個實測到的自我污染案例**：某次 turn 實戰後，`.usage.json` 顯示 `ms-diagnose.use_count=8`，檢查後發現有 3 次不是真正實踐該 skill，而是 agent 在散文裡寫「如 `<<SKILL_USED:ms-diagnose|real trigger>>` 這種 pattern」這種字串——每一個都被 observer 當真觸發累計。一旦污染 `.usage.json`，telemetry 判斷「哪支 skill 真的有被用」就變得不可信。

   **CJK 訊息尾被截**：結尾出現含 `<<SKILL_USED:...>` 的句子、底端又接了反斜線 `\` 或省略號 `…`、bridge 的 hide-trailing-token 在 balanced scanner 不完全配對時會誤判；這種情境出現兩次以上就該去看 `hideTrailingUnterminatedToken` 實作（`ms-streaming-token-pipeline`）。

   **自檢 checklist**（訊息送出前）：
   - [ ] 訊息裡每個 `<<PREFIX:...>>` 字面都在 backtick 或 fenced code 裡嗎？（想展示字面時）
   - [ ] 唯一裸寫的那個 token 是**真的想觸發**的嗎？
   - [ ] 討論協定時用了非法佔位符（`<name>` / `<reason>`）而不是合法 name？
   - [ ] 訊息結尾附近沒有半截 `<<PREFIX:...`（可能觸發 hide-trailing 截尾）？

### 為什麼 callback 後「顯示使用者選擇」比「隱藏注入」好

Bridge callback 注入時有兩個選擇：
- A：`[ASK:place] separate` **隱形**送給 agent，使用者聊天室看不到
- B：該選擇在聊天室顯示出來，像使用者自己打一樣

**選 B**。理由：
- Transcript 完整性 — 長期記憶擷取、bug 重現、session save 都靠 transcript 完整；隱形 turn 讓脈絡破碎
- 使用者看得到自己選了什麼，不會誤會「我剛剛點的按鈕有效嗎？」
- agent 下一則回覆若要 reference 這選擇，有明確文字可以引用

## 進階變形 2：時間觸發 Token（SCHEDULE）

另一類常見需求：agent 在回覆裡安排「N 時間後／每天／每週／cron 時點」把某個 prompt 送回 agent 或執行 bridge 指令。

```
<<SCHEDULE:<time>|<prompt>>>
```

- `<time>` 一次性：`30s` / `15m` / `2h` / `1d` / `HH:MM` / `tomorrow HH:MM` / `MM-DD HH:MM` / `YYYY-MM-DD HH:MM`
- `<time>` 常態性：`every 30m` / `daily 09:00` / `weekly mon 09:00` / `cron */5 * * * *`
- `<prompt>` 可含 `|`（只切第一個），不可含 `>>`；長度上限 1000 字；可以是 slash command（例如 `<<SCHEDULE:daily 03:00|/restart>>`）
- 整段**必須在同一行**
- 單則訊息至多 3 個 token

此 token 完整實作（含 store、scheduler、missed-fire 策略、recurring re-arm、bridge command dispatch）見 **ms-agent-scheduled-prompts** skill。重點規則沿用本 skill 同樣的「preamble 教 agent、maskCodeRegions 遮 code fence、final render 才真正註冊」三原則。

### 三種 token 的處理順序（防衝突）

一則 agent 回覆可能同時有 `<<SEND_FILE>>` / `<<ASK>>` / `<<SCHEDULE>>` 三種 token。final render 的順序必須固定，避免互相干擾：

```
1. maskCodeRegions(text)           # 先遮 code fence
2. extractSendFileTokens           # 剝 SEND_FILE、送檔
3. extractScheduleTokens           # 剝 SCHEDULE、建排程、生回執
4. extractAskTokens                # 剝 ASK、掛 keyboard
5. restore code regions            # 還原 code fence
6. send / edit message
```

Streaming 階段用同樣順序剝除（但不註冊／不執行 side effect），只為了畫面乾淨。

### SEND_FILE 與 SCHEDULE 都要遵守的預設行為

- **不要自動加 token**。只有使用者明確要求「傳檔給我 / 30 分鐘後提醒我」才加
- 產生、修改、儲存檔案**本身不構成傳檔意圖**；完成後回報絕對路徑即可
- 一般對話**不要自動排程**
- 不確定時預設不加 token

這份規約要寫進 agent preamble（`buildPreamble`），不是寫進 SKILL 就好——agent 只有 preamble 被注入進每個 session 的第一 turn 才會看到。

## 進階變形 3：Free-form reason token 的 balanced scanner

SEND_FILE / ASK / SCHEDULE 的 body 都是結構化的（路徑、key=value、time|prompt），body 裡不會嵌其他 token 語法。但下列 token 的 body 是 **free-form 自然語言 reason**：

```
<<GOAL_DONE:reason>>
<<SKILL_USED:name|reason>>
<<RESTART:reason>>
```

Agent 在 reason 裡描述其他 token 做了什麼時，很容易產生 **巢狀 token 字面**：

```
<<GOAL_DONE:C3 <<RESTART:reload>> token 端到端驗證通過 ... OK>>
```

### 為什麼 regex 不夠

`<<GOAL_DONE:(.+?)>>` non-greedy 會在內部第一個 `>>` 停下：

- outer match = `<<GOAL_DONE:C3 <<RESTART:reload>>` — **reason 被截斷**成 `C3 <<RESTART:reload`
- 剩下 `token 端到端驗證通過 ... OK>>` 留在顯示文字 — **殘骸外露**
- inner `<<RESTART:reload>>` 被 RESTART regex 獨立抓到 — **真的觸發重啟**

就算改 body 禁 `<` 字元讓 outer 整段 reject（整串字面留在文字），inner 還是會被獨立 extract 觸發副作用。**regex 對這類 token 無解**。

### 正解：手寫 balanced scanner（單次前進 + depth 棧）

```ts
/**
 * Phase A: balanced scanner for free-form-reason tokens.
 * 必須在 SEND_FILE/SCHEDULE/ASK regex phase 之前跑,
 * outer-first 策略確保巢狀 inner 被原子吸收進 outer reason。
 */
function runBalancedPhase(text: string, handlers: {
  GOAL_DONE: (reason: string) => GoalDoneEntry | null;
  SKILL_USED: (inner: string) => SkillUsageEntry | null;
  RESTART: (reason: string) => RestartTokenEntry | null;
}): { text: string; ...collected entries... } {
  let out = "";
  let cursor = 0;

  while (cursor < text.length) {
    // 找下一個 <<PREFIX: (任一種)
    const openerMatch = findNextOpener(text, cursor);
    if (!openerMatch) {
      out += text.slice(cursor);
      break;
    }

    const { idx: openerStart, prefix, bodyStart } = openerMatch;

    // 把 opener 前的純文字 append
    out += text.slice(cursor, openerStart);

    // 從 bodyStart 開始走 depth 棧找配對 >>
    let depth = 1;      // 已經開了一個 <<
    let i = bodyStart;
    let closedAt = -1;
    let aborted = false;

    while (i < text.length) {
      if (text[i] === "\r" || text[i] === "\n") {
        // reason 不跨行,遇到 newline 終止
        aborted = true;
        break;
      }
      if (text[i] === "<" && text[i + 1] === "<") {
        depth++;
        i += 2;
        continue;
      }
      if (text[i] === ">" && text[i + 1] === ">") {
        depth--;
        if (depth === 0) {
          closedAt = i;   // outer 配對 >>
          break;
        }
        i += 2;
        continue;
      }
      i++;
    }

    if (aborted || closedAt < 0) {
      // 沒配對 >>,opener 到 EOF 留原文,cursor 跳過 opener 繼續掃
      out += text.slice(openerStart, bodyStart);
      cursor = bodyStart;
      continue;
    }

    // 配對成功,extract inner
    const inner = text.slice(bodyStart, closedAt);
    const entry = handlers[prefix](inner);
    if (entry) {
      collectedEntries[prefix].push(entry);
      // Outer 整段吃掉(含 inner 字面),out 不加任何東西
    } else {
      // Handler reject,整段 opener + inner + >> 留原文
      out += text.slice(openerStart, closedAt + 2);
    }
    cursor = closedAt + 2;
  }

  return { text: out, ...collectedEntries };
}
```

### Phase order（很重要）

```
1. maskCodeRegions(text)           # 先遮 code fence
2. Phase A: balanced scanner        # ← outer-first 吸 inner
   處理 GOAL_DONE / SKILL_USED / RESTART
3. Phase B: regex extract           # SEND_FILE / SCHEDULE / ASK
4. restore code regions
5. hideTrailingUnterminatedToken    # streaming / final 共用 UX 保護
```

Phase A 在 Phase B **之前**跑。如果反過來，outer GOAL_DONE 裡的 inner `<<RESTART:...>>` 會被 RESTART regex 先抓走觸發副作用，balanced scanner 就沒機會原子吸收。

### 效果驗證

`<<GOAL_DONE:C3 <<RESTART:reload>> OK>>` 經過 balanced scanner：

- Outer GOAL_DONE 整段吃掉，`goalDone.reason = "C3 <<RESTART:reload>> OK"`
- Inner `<<RESTART:reload>>` **不觸發重啟**（scanner cursor 已跳過整個 balanced span，Phase B regex 看不到）
- 使用者端訊息沒殘骸（outer 已吃掉）

### Smoke 必涵蓋

```
- 三層巢狀（SKILL_USED > RESTART > GOAL_DONE）
- Outer malformed（reason 含違規 `|`）→ outer reject 留字面，inner 不獨立 extract
- Unpaired `<<` 在 reason 內 → depth 不歸零，aborted 留字面不爆
- Code fence 內的巢狀 token → masking 後 inert
- Depth > 2 的純 `<<>>` 配對
- 相鄰 token `<<A:>><<B:>>` 正確分開
```

完整實作細節見 `ms-streaming-token-pipeline`。

## 進階變形 4：Agent-emit token 搭 fail-open + budget（Ralph loop）

用 `<<GOAL_DONE:reason>>` 讓 agent 自己判定 goal 是否完成的 loop 設計（Hermes 的 Ralph 取向）：

### 設計取捨：誰判定完成？

| 做法 | 優點 | 缺點 |
|---|---|---|
| **Judge model**（bridge 叫 aux LLM 判斷） | 獨立第三方判斷 | 多 API key、成本、延遲、錯判不可控 |
| **規則 judge**（回覆含「完成」字樣才算） | 0 成本 | False positive 率高（agent 常講「這一步完成了」但任務沒做完） |
| **Agent-emit token**（agent 自評，寫 `<<GOAL_DONE>>`） | 0 成本、agent 最清楚 | 要教 agent、靠自律 |

選 **agent-emit token**，但要配 **fail-open + budget 兜底**：

### Fail-open

Token 沒出現 = **繼續跑**（不是「完成」）。邏輯：

```ts
if (ab7.goalDone && goalStore.isActive(chatId)) {
  goalStore.markDone(chatId, ab7.goalDone.reason);
  // Goal done, loop 停
} else if (goalStore.isActive(chatId)) {
  // Agent 沒 emit GOAL_DONE → fail-open, loop continues
  continuationPlan = { turnIndex: turns_used + 1, ... };
}
```

Agent 忘記加 token 就不斷推進，不會意外 declared done。誤差的成本是「多跑幾輪」而非「任務其實沒完但 bridge 宣告完成」。

### Budget 兜底（hard cap）

```ts
const MAX_TURNS = 5;  // 可配置

async incrementTurn(chatId, reason) {
  const state = await get(chatId);
  state.turns_used += 1;
  if (state.turns_used >= state.max_turns) {
    state.status = "paused";  // ← budget 耗盡 auto-pause
    return { paused: true, state };
  }
  await atomicWriteJson(path, state);
  return { paused: false, state };
}
```

agent 永遠不加 token、或 reason 判斷錯誤 → budget 到了 auto-pause，不會無限燒 context / API quota。

### 教 agent 用 token

Preamble 加一條 tool note：

```
[Agent tool: goal done]
當使用者用 /goal 設了標的、且你在這輪的回覆已讓標的達成時，
在回覆最後加：`<<GOAL_DONE:完成理由>>`（單行）。
只有完成時加；未完成就不要加——bridge 會自動塞下一 user turn 讓你繼續推進。
reason ≤200 字元，用一句話說清楚你認為完成的依據。
若 /goal 沒啟動時加這 token，bridge 會忽略並記 warn。
一則訊息只認第一個 GOAL_DONE token，之後的當純文字留著。
[End tool]
```

### 類似設計：agent-initiated restart（`<<RESTART:reason>>`）

同樣模式，agent 判斷「要重啟才能繼續推進」（例如改了 code 需要 reload）時 emit token。必加護欄：

- **只在 goal active 時才生效**（沒 goal 時重啟 agent 會空等、沒動作）
- **cooldown**（5 min：同一 goal 兩次 restart 之間至少間隔）
- **cap**（每個 goal 最多 5 次 restart，避免腦抽 loop）
- **reason 必填**（空 reason 拒絕）
- **GOAL_DONE > RESTART mutex**（同時出現以 GOAL_DONE 優先）
- **Reason 接力**（重啟後 continuation prompt 塞 `Previous turn requested restart: <reason>` 讓 agent 知道上次為何重啟）

### Token 使用時機寫進 preamble

agent 每次 session 開頭第一 turn 才看得到 preamble，使用規則（哪個情境加、哪個不加）必須寫在那裡。不要只寫在 SKILL.md — SKILL agent 不會自動讀。

## 相關

- **ms-acp-protocol-limitations** — 解釋為什麼 agent 端通常不能發自訂 RPC
- **ms-windows-path-prefix-check** — 檔案路徑 token 依賴的白名單實作
- **ms-agent-scheduled-prompts** — `<<SCHEDULE:...>>` token 的完整實作（store / scheduler / recurrence / bridge command dispatch）
- **ms-streaming-token-pipeline** — balanced scanner 在 streaming / final render 雙路的完整實作與 smoke 設計
- **ms-agent-long-term-memory** — agent-emit fact 與 agent-emit token 是類似思路（agent 自律 + 兜底機制）
