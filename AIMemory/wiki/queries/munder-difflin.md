---
title: Munder Difflin 外部 repo 研究：11 家 CLI 的三層 bridge 分級與 canReceiveInbox 降級、階梯式 circuit breaker、出站 secret redaction 與它自己沒在跑的閘門，以及對 telegram-kiro-bridge 的比對表與 M1-M6 借鏡
type: query
created: 2026-08-19
updated: 2026-08-19
status: Step 4 完成（M2+M3 已實作，29/29 變異 killed，跨 vendor 覆核 round 1 的 8 條全數重現並修掉）；未 commit
sources:
  - https://github.com/chaitanyagiri/munder-difflin
  - sparse clone @ HEAD（v0.4.4，2026-08-18）：src/main、src/shared、src/preload、test、.github、根 *.md
---

# Munder Difflin 研究（外部 repo 吸收評估）

2026-08-19 依 `ms-external-repo-absorption` 流程研究 `chaitanyagiri/munder-difflin`，
走到 **Step 2（比對表 → 借鏡排序）** 為止，**未動任何 bridge 的碼**。

相關頁面：[[bridge-research]]（外部框架借鏡總索引）、
[[kkterm]]（最接近的前一次研究——同樣是「宿主 app 接多家 agent CLI」）、
[[cloudflare-os]]（成本不對稱換算方向的判準來源）、
[[bridge-specialist]]（M2 的落點）、[[bridge-secrets-backup]]（M3 的落點）、
[[bridge-smoke-gate]] 與 [[verification-diagnosis]]（本頁「它自己的閘門沒在跑」那條的判準來源）。

## 0. 證據等級

本頁**混合等級，逐條標**——與 [[kkterm]] 全頁 B 級不同，這次有 clone。

- 🟢 **A 級（讀了原始碼）**：`src/shared/agentProvider.ts`、`src/main/breaker.ts`、
  `src/main/hooks.ts`、`src/main/memory.ts` 四支全文；`src/main/hive.ts` 的
  `redactSecrets` / `PROTOCOL_MD` / `routeOnce` / `commit` / `untrackCostLedger` 五段；
  `package.json`、`.github/workflows/ci.yml`、`LICENSE`、`test/` 檔案清單；
  另十支 main 模組的檔頭註解。
- 🟡 **B 級（過 WebFetch 小模型摘要層）**：README、`HIVE.md`、`SPEC.md`、`DESIGN.md`。
- ⚪ **完全沒看**：`src/renderer/`（140 檔）、`src/main/index.ts`（4,828 行）、
  `pty.ts`、`slack.ts`、`webhook.ts`、`realtime*.ts` 內文、`docs/blog`、`landing-remotion`。

⚠️ **本輪抓到它的文件與碼不符，且方向是文件落後**（A 級，
`grep -rn tmux src/main src/shared src/preload` = **0 命中**；`src/renderer` 未 checkout
∴ 未掃，但 PTY spawn 全在 main ∴ 不影響結論）：
`SPEC.md` 通篇描述的是「attach 到既有 tmux pane 的**唯讀 viewer**，明文寫 MVP
*Not an agent-to-agent message bus*」；而 HEAD 的碼是 node-pty 自己 spawn、外加一整套
outbox→inbox 訊息匯流排。∴ **`SPEC.md` 是早期 MVP 規格、已被實作走過頭**，
引用它描述現況會整段錯。這正是 skill 常見錯誤 #5（預設外部是對的）的實例。
本頁凡引 SPEC.md 者一律標記為「舊規格」。

授權 **MIT**（`LICENSE` 全文確認），無 Commons Clause ∴ 連碼帶抄也不受限——
與 [[kkterm]] 不同，那份是 MIT + Commons Clause。

## 1. 這是什麼

Electron 桌面 app（v0.4.4，2026-08-18），把**你已經在付錢的那些 agent CLI**
包成一個協作蜂巢，賣點是 "a multi-agent harness that works with the subscriptions
you already pay for"。UI 是 Animal Crossing 風格的像素辦公室，每個 agent 是一個
會走動的 avatar；但那層與 bridge 無關，**真正的交集在 main process**。

兩個資料平面：**terminal plane**（node-pty → IPC → xterm.js）與
**event/hive plane**（磁碟上的 git repo 當黑板 + mailbox + router）。
一個叫 Michael 的 GOD agent 當協調者。

與 bridge 的交集比 [[kkterm]] 更深：兩邊都在解「一個宿主怎麼驅動多家 agent CLI、
怎麼在它們之間傳工作、怎麼防跑飛、怎麼不把 secret 漏出去」。

## 2. 五條有實質內容的交集軸

### 2.1 11 家 CLI 的三層接法分級 —— 而且不支援某能力時是「降級」不是「不支援」🟢A

`agentProvider.ts` 用一張 preset 表描述 claude / codex / grok / kimi / antigravity /
qwen / opencode / crush / pi / copilot / custom，每家標明 spawn 旗標、model flag、
resume 形式、初始 prompt 怎麼進去（flag / positional / **打字進 TUI**）、安裝指令。

真正值得抄的是**兩個正交的能力旗標**（原始碼註解明講兩者不同）：

- `hiveAware` —— 吃不吃 Claude 專屬的 `--append-system-prompt` + `--settings` 注入。
- `canReceiveInbox` —— **router 可不可以把信投給它**。false 時信不是丟掉，
  也不是讓這家 CLI 變成不支援，而是**退回給 god 代收**（`kimi`、`copilot`、`custom` 就是這格）。

而「怎麼拿到 lifecycle 事件」分三階，愈往下愈醜但覆蓋愈廣：
① 原生旗標（claude）→ ② 寫一份 hook 設定檔的 shim（codex / agy / grok / pi / opencode）
→ ③ **proxy tier**：CLI 完全沒有 hook 面（qwen / crush），就起一個 loopback 反向代理
夾在它與 LLM 之間，**從流量合成出等價的 Stop 事件**。

### 2.2 CircuitBreaker：steer → constrain → stop 的階梯，且預設不會殺 🟢A

`breaker.ts` 檔頭第一句就是動機：Claude Code 有 `--max-turns` 但**沒有金額上限**，
所以自己補一個。設計性質（全部逐字可查）：

- 一拍只升一級、健康一拍就降一級；`hardStop` **預設 false**，不開就永遠停在
  `constrained` 不會 kill。
- 五條 trip：同一 tool 重複 8 次、api_error 連 5 次、per-agent token cap、
  全樓 $ / token cap（**歸咎最大花費者**，不是連坐整層）、output token 速率。
- 觸發後的動作是**往那個 agent 的 inbox 寄一封信**（`PROTOCOL_MD` 逐字教它：
  「你就是它抓到的問題本身，停止重複、總結你試過什麼」）——是 in-band 糾正不是 out-of-band 殺。

最可遷移的其實是**它的偽陽性工程**（這幾條與領域無關）：
- 「速率是**連續兩次累計取樣的差**，絕不把單一 sample 當成增量」（檔頭逐字）。
- compaction 期間豁免 Δoutput 判定（否則 `/compact` 自己會觸發自己的斷路器——
  他們標為 upstream issue #109）。
- 「最近有**不同的** tool call」也算 progress，否則背景工作流會被誤判成沒進度。
- no-progress 要**連 2 拍**才算，避免單拍抖動。

### 2.3 出站 secret redaction —— 做在 IPC 邊界，但它自己的證明沒在跑 🟢A

`hive.ts:232 redactSecrets()` 把每一則訊息的 subject/body 在**離開 main process 之前**
洗過：PEM 私鑰整塊、JWT、七家的 key 前綴（`sk-`/`sk-ant-`/`xox[bpaors]-`/`gh[posru]_`/
`github_pat_`/`AKIA`/`AIza`）、bearer token、以及 `(namespace_)*(api_key|secret|token|
password|…)\s*[:=]\s*value` 這種賦值形式。註解寫明立場：**「過度遮蔽可接受，漏一個真的 secret 不可接受」**，
且刻意不做 entropy 全域遮蔽，好讓 git SHA / 路徑 / 散文活下來。renderer 端**零遮蔽政策**，
只收已經洗乾淨的字串。

註解還有一條 **LOCKSTEP** 紀律：正則陣列在 `test/voice-messages.test.cjs` 裡
「字元級鏡像」複製一份（.cjs 測試 import 不了 TS module），並宣稱
*"the test is what PROVES a secret-shaped value is stripped"*。

⚠️ **但那句宣稱在 HEAD 上不成立**（A 級，三條獨立佐證）：
`.github/workflows/` **三支（ci／release／blog）全部只跑 typecheck 與／或 build，
沒有任何 job 執行測試**（逐支 grep 過 `test` 與 `npm run`）；
`package.json` 只有 `test:focused` 一個測試腳本，**38 支測試裡有 8 支不在其中**——
而 `voice-messages.test.cjs`（就是那個「PROVES」的檔）**正是這 8 支之一**。
∴ 那道 secret 閘門的證明**不在任何自動路徑上**，只在有人手打指令時才跑。
形狀與 [[verification-diagnosis]] / [[bridge-smoke-gate]] 記過的「斷言存在但沒人執行它」同型，
差別是這次抓到的是**別人的**——正好是 skill 常見錯誤 #5 要防的。

### 2.4 兩個與 bridge 記憶直接對撞的獨立佐證 🟢A

- **model pin 靜默降級**：`agentProvider.ts` 的 opencode 段逐字記載——preset 曾預設
  `anthropic/claude-sonnet-4-5`，沒有該 key 的使用者那邊 OpenCode **靜默 fallback**
  到別的模型（實測落到 "DeepSeek V4 Flash Free"），而
  *"every surface in this app went on reporting Claude Sonnet 4.5 … nothing flagged the divergence"*。
  修法是**乾脆不發 `--model`**。這與 [[bridge-model-strategy]] 記的
  `acp-model-opus5-not-exist`（pin 被拒靜默降級、footer 報意圖非實際）是**兩個 codebase 各自撞到的同一顆雷**。
- **卡死的守衛旗標會靜默停掉全部後續**：`memory.ts` 檔頭寫，一個卡住的 mine
  「會永久持有 PID **並且讓 `mining` 卡在 true，靜默停掉所有未來的 pass**」，
  修法是硬上限 + SIGTERM/SIGKILL sweep + 失敗時 `lastMined.delete(id)` 讓下一拍重試。
  與 `claude-mem-worker-dies-silently` 同形。

### 2.5 一條乾淨的 git 判準：`.gitignore` 對「已被追蹤的檔」讀起來像修好了 🟢A

`hive.ts:1961 untrackCostLedger()` 的註解：append-only 的 `cost-ledger.jsonl` 每次
hive commit 都整份重存，幾千個 commit 後是數百 GB blob；而
**「git 對它已經在追蹤的檔案照記不誤、不管 .gitignore 說什麼——∴ 只加 ignore 那一行
讀起來像個修復，而 repo 繼續長大」**。修法是先 `ls-files` 探測（避免每次啟動都改寫 index）
再 `rm --cached`。

## 3. Step 1 比對表

| 面向 | Munder Difflin | bridge 現況 | 判定 |
|---|---|---|---|
| 多 agent CLI 接法 | 11 家，三層（原生旗標／hook shim／流量 proxy） | 3 家 ACP adapter | **不同問題**——ACP 直接給結構化事件 ∴ 不需要 shim；但覆蓋面它贏 |
| 能力不足時的行為 | `canReceiveInbox:false` → **信退給 god**，agent 仍可用 | run_plan 是全有全無設計（[[bridge-specialist]]） | **值得借鏡（M2）** |
| runaway / 成本防護 | 五條 trip + steer→constrain→stop 階梯 + $/token cap | 三個靜態上限（併發 3／step 12／fan-out 5）+ per-domain 逾時，**無行為型偵測** | **值得評估（M1）** |
| context 用量來源 | statusLine shim 回傳 `context_window.{total_input_tokens,context_window_size}` | ACP `usage_update`（used+size）與 Kiro `session_info_update`（`src/context-telemetry.ts`） | **已有，且管道更好**（協定原生，不靠 shim） |
| 累計 token / $ 帳本 | 內嵌 OTLP collector（`CLAUDE_CODE_ENABLE_TELEMETRY=1`）+ cost-ledger + 每模型估價 | 只有當前 context 百分比 | **缺口，但適用性待判**（見 M1 註） |
| 出站 secret 遮蔽 | IPC 邊界主動 redact + LOCKSTEP 測試（**但沒在 CI 跑**） | K3 preamble 掃描是**入站、warn-only**（2026-08-19 上線） | **值得借鏡（M3）** |
| 訊息協定防迴圈 | `HOP_CAP=12` + 只有 request/query/propose 該回覆 | RELAY 有 `<<RELAY_DONE>>`，未見 hop 上限 | **小額借鏡（M4）** |
| 優雅關機 | Closing Time：廣播 → 每個 worker 存 WIP+memory → ACK 齊了才拆 | `<<RESTART>>` + `[WS]` working-state（單 session、增量寫） | **已有等價**（單 agent 不需 ACK barrier） |
| 記憶壓縮 | MemoryReflector：三區形狀 + backup-first → verify-don't-trust → atomic swap | /dream + factlint + wiki 蒸餾（更厚） | **已有**，惟「verify-don't-trust」是可抄的**命名** |
| 中途操控 agent | ControlRegistry：pause/gate 走 PreToolUse deny、steer 走 additionalContext、halt 走 `{continue:false}` | ACP `session/cancel`；無 mid-turn 注入 | **結構上做不到**（ACP 無等價 hook 回傳面） |
| skill 隨 repo 出貨 | 明文只做**探索與瀏覽、不安裝**："那個決定留給使用者" | 2026-08-08 刻意移除 `default-skills/` | **同一個 move**，互為佐證 |
| 測試閘門 | CI 只跑 typecheck+build；8/38 測試無腳本引用 | tsc + smoke fast tier + pre-push hook + 突變測試 | **bridge 這層明顯更厚** |

## 4. Step 2 借鏡排序

| # | 項目 | 增量價值 | 成本 | 建議 |
|---|---|---|---|---|
| **M2** | 降級要有明確可見的記號（他們是 bounce to god + appendLog + 前端事件） | **高**——`run-prompt.ts` 的 MCP 路徑只 `console.warn`（headless 不留檔），legacy token 路徑反而有給使用者看 | 低 | **Step 4 已實作**（`SPEC-degradation-visibility-and-outbound-redaction.md`） |
| **M3** | 出站邊界 secret redaction ＋「不做熵值全域遮蔽好讓 git SHA 活下來」的設計註記 | **中**——bridge 已有 `redactTerminalText`，缺的是三種形狀、**第二個邊界（relay）**與**邊界差異化**；正則陣列**不宜直搬** | 低-中 | **Step 4 已實作**；那條設計註記最後成為邊界拆分（`long-blob` 只掛 terminal）的依據 |
| **M1** | circuit breaker 的**偽陽性工程四條**（差分取樣／compaction 豁免／distinct-tool 算進度／連 N 拍去抖） | 中 | 低（是判準不是模組） | 建議吸收判準 |
| **M4** | 訊息協定的 hop 上限 + 「哪些 act 該回覆」白名單 | 中——RELAY 目前靠自律收尾 | 低 | 可選 |
| **M5** | `.gitignore` 對已追蹤檔無效 → 要 `rm --cached` 的判準 | 低-中（一次性稽核） | 極低 | 順手查一次 |
| **M6** | LLM 改寫產出物走 backup → **verify-don't-trust** → atomic swap 的命名分段 | 低 | 極低 | 併進 /dream 敘事即可 |

**排除**：整套 hook shim / proxy tier（bridge 走 ACP ∴ 是**不需要**不是還沒做，同
[[cloudflare-os]] 對 Observer 的判定）、pixel UI 與 DESIGN.md、mid-turn steering（ACP 結構上沒有那個面）、
Closing Time（`[WS]` 已等價）、OTLP collector 本體（見下）。

### ⚠️ M1 的成本不對稱要換算方向，不能照搬整個 breaker

它的 breaker 服務的是「5–15 個 agent 在無人桌面上燒使用者訂閱額度」，∴ 值得為此養
一整套取樣 + 階梯 + 帳本。bridge 的 specialist 是**逐次派工、有 per-domain 逾時、
派完就結束**，「跑飛」的實證案例在記憶裡是 0；反過來，bridge 已量到的痛點是
**行程樹沒收乾淨**（`child-kill-leaks-process-tree`）與**併發爭用**
（`smoke-slow-is-contention-not-regression`）——那兩個 breaker 蓋不到。
∴ 建議**只吸收判準（M1）不吸收模組**；要吸收模組，得先做適用面盤點
（[[kkterm]] K1 與 [[cloudflare-os]] B1 都在這一步翻過案）。

同理，OTLP collector 本體先不碰：bridge 的 backend 是 `claude-agent-acp`（走 Agent SDK）
而非 Claude Code CLI，**那組 env 會不會被 SDK 認、會不會吐 OTel 完全未驗**。
要不要補「累計 token/$ 帳本」該獨立立案，不該搭 breaker 便車。

## 5. 誠實邊界（尚未做的事）

- ~~沒動任何 bridge 的碼~~ → **2026-08-19 已實作**（M2+M3，18 檔）。Step 4 又推翻了 Step 3 的兩處：①「RELAY_FILE 範圍外」是錯的前提——它的 caption 就是委派本體，secret 會原樣送給 peer（覆核 H1）；②「掛 relay 就照搬同一組 pattern」也不對——`long-blob` 在 relay 會把 git SHA 靜默吃掉，而那正是我用來排除使用者 DM 的理由（覆核 M3）。最終是**邊界差異化**：單一 pattern 陣列 + `boundaries` 標記。⚠️ **2026-08-19 Step 3 推翻了本頁兩處對 bridge 側的描述**：①「正則陣列 MIT 可直搬」為誤——bridge 早有 `pty-operational-observer.ts:89 redactTerminalText`（7 條 pattern，另含他們沒有的 authorization/cookie/long-blob），缺的是 PEM 塊／JWT／namespace 前綴折疊三種形狀；而它的 `long-blob`（`[a-f0-9]{40,}`）**會吃掉完整 git SHA** ∴ 正是他們檔頭那句「不做熵值全域遮蔽」在反對的東西，不可原樣掛到使用者回覆路徑。②M2 的落點不是「run_plan 沒有降級機制」而是「降級記號只進 console」——`moa-plan.ts:155` 有 `warnings.push`，MCP 路徑（`run-prompt.ts:2406`）吞進 console.warn，legacy token 路徑（`:2463`）反而顯示給使用者。且本機 12/12 domain 目前齊全 ∴ 這是**機制層的回歸護欄**，不是現行故障。
- bridge 側凡寫「未見等價」者，依據是 `src/` 的定向 grep（`OTEL|contextWindow|
  statusLine`）+ wiki 盤點，**不是窮舉全碼** ∴ 不宣稱不存在。
- 它的 `index.ts`（4,828 行）與 `pty.ts`（802 行）沒讀——**spawn 與 IPC 的實際接線
  全在那裡**，M2 若要落地必須先補讀它的 `ensureAgent` 全貌。
- §2.3 的「8 支測試無腳本引用」是**靜態比對 package.json 與 test/ 目錄**得出的，
  沒有實跑 `npm run test:focused` 驗證其餘 30 支真的會過。
- 它的 preset 表裡有多處作者自標的 `// TODO-verify` / `UNVERIFIED`（qwen、crush、
  pi、opencode 的 bridge 都標了 "live runtime … UNVERIFIED pending keys"）
  ∴ **不要把那張表當成 11 家都已實測可用**——它自己沒這樣宣稱。
