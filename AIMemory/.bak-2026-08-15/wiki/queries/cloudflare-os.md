---
title: Cloudflare OS 開源研究：Gadget/Gatekeeper/Observer 三概念、observation 當權限依據、lazy revocation 權限圖、非同步人工核可，以及對 telegram-kiro-bridge 的差距判定
type: query
created: 2026-08-14
updated: 2026-08-14
status: Step 2–3 完成（已 clone 核對原始碼）——吸收與否待使用者裁決，未動任何 bridge 碼
correction: 初版「bridge ASK 是同步阻塞」為事實錯誤，同日以一手證據更正，見 §4.1
sources:
  - https://github.com/cloudflare/cloudflare-os
  - https://blog.cloudflare.com/cloudflare-os/
  - https://raw.githubusercontent.com/cloudflare/cloudflare-os/main/README.md
  - https://raw.githubusercontent.com/cloudflare/cloudflare-os/main/docs/observers.md
  - https://raw.githubusercontent.com/cloudflare/cloudflare-os/main/docs/sharing.md
  - https://www.cloudflare.com/press/press-releases/2026/cloudflare-os-is-the-first-ai-workspace-built-around-how-companies-actually-work/
  - https://www.helpnetsecurity.com/2026/08/06/cloudflare-os-open-source/
---

# Cloudflare OS 研究（外部 repo 吸收評估）

2026-08-14 依 `ms-external-repo-absorption` 流程研究 `cloudflare/cloudflare-os`，
走到 **Step 1（現狀盤點 → 比對表）** 為止，**未 clone、未讀 `packages/` 實作、未安裝**。

相關頁面：[[bridge-research]]（外部框架借鏡總索引）、
[[cc-session-reader]] 與 [[paulsha-cortex-governance-plane]]（同流程的前兩次外部 repo 研究）、
[[bridge-specialist]]（bridge 的動作／派工權限層，本頁主要對照基準）、
[[bridge-memory]]（observation-as-provenance 若要吸收會落在這裡）、
[[verification-diagnosis]]（本頁的證據等級紀律來源）。

## 0. 證據等級（先講清楚）

⚠️ **本頁所有內容都經過 WebFetch 的摘要模型，不是逐字原文。**
這與 [[cc-session-reader]] 那次不同——那次刻意走 `raw.githubusercontent.com` 直取以避開摘要層，
本次雖然也用了 raw URL，但 WebFetch 工具**無論來源都會再過一次小模型**，∴ 摘要層沒有被繞開。

- **B 級（可信但非逐字）**：三個核心概念的存在與大致職責、OS 類比、Apache-2.0、early access。
  這幾項在 blog／README／press release 三個獨立來源交叉出現。
- **B− 級（單一來源且經摘要）**：`docs/observers.md` 與 `docs/sharing.md` 的機制細節。
- **✅ 已升級為 A 級（2026-08-14 同日 clone 核對）**：repo 已 shallow clone
  （~9 MB，`git clone --depth 1`）。初版標為「未驗證」的識別字**全部確認存在於原始碼**：
  `authorizeObservation` / `addObserver` / `removeObserver` / `excludeObservers` /
  `ObserverRecord` / `OverseerClientInterface` 皆有實體檔案命中。
  §3.2、§3.4 的引文出自 `packages/workshop-shared/src/gatekeeper.ts` 與
  `packages/mcp-shared/src/action-store.ts` 的**逐字註解**（我親自 Read，非摘要）。
  star 數 8199 由 GitHub API 直取。
- **仍然沒有的**：實際執行行為。**沒跑過 `pnpm run-local`**、沒觀察過真實核可流程。
  ∴ 介面契約與註解的宣稱是 A 級，「跑起來真的這樣運作」仍是 B 級。

∴ §2 以後關於**設計契約**的敘述可引用為事實；關於**執行時行為**的仍須標推論。

## 1. 這是什麼

Cloudflare 內部給員工用的「AI 生產力作業系統」，2026-08 開源，Apache-2.0，跑在 Workers 上。
自述定位同時是「公司用 AI 提高生產力的 OS」與「跑 AI workload 的 OS」。
開源動機是讓別人 fork 成「Your Company OS」。

當前是 **v2 完全重寫的 early access**，README 自承「非常能用，但還有很多粗糙邊角」。

## 2. 三個核心概念

| 概念 | 職責 |
|------|------|
| **Gadget** | 每個使用者自己的 app 實例（不是集中式 SaaS）。AI 幫寫幫改，跑在 sandbox。範本叫 **blueprint** |
| **Gatekeeper** | 每個外部服務一支 Worker，管 OAuth／憑證／政策／稽核。agent 拿到的是 **typed binding 不是原始憑證** |
| **Observer** | 記錄「這個 Gadget 讀過哪些資源」，分享時反過來驗**收件人自己**是否也有那些資源的權限 |

capability binding 的形狀（blog 給的示例）：

```ts
const issues = await env.PROJECT.listIssues({ teamId: "ENG", state: "open" })
```

`env.PROJECT` 是「代表在特定政策下使用特定資源之權限的 capability」，不是 API key。

**OS 類比**（README 自己講的）：Durable Objects＝kernel、Gatekeeper＝device driver、
Dynamic Worker＝process、blueprint＝執行檔。
執行隔離：server 端跑 Dynamic Worker 且**全域對外連網被關閉**，client 端跑瀏覽器 sandbox frame，
兩邊都只能經明確授予的 capability 出去。

## 3. 三個設計上真的新的東西

### 3.1 observation 當權限依據（`docs/observers.md`）

Gadget 每次透過 Gatekeeper 讀資料就記一筆 observation。非擁有者要開這個 Gadget 時：

1. 依角色決定 in-scope 的 Gatekeeper（`build` = 全部；`use` = 只有具名 binding）
2. 檢查此人是否已為每個 Gatekeeper 選好連線帳號
3. 逐一呼叫各 Gatekeeper 的 `addObserver()`，確認此人**能存取目前為止讀過的全部東西**
4. 全過才寫 `ObserverRecord` 落地

`ObserverRecord` 內容：`profileId`（分享表的 key）、`observerId`（隨機不透明 handle，
傳給 gatekeeper 用）、`accountChoices`（gatekeeper id → 選定的連線帳號 id）。
存在 `observers` collection，主索引 `profileId` + 次索引 `byObserverId` 反查。

**前向強制**：往後若某筆 observation 被標 `excludeObservers`，該次讀取會被擋，
除非所有具名 observer 都已經失去分享權限。
**拆除**：分享權限一收回，記錄刪除並對受影響的 gatekeeper 呼叫 `removeObserver()`。

→ 這解的問題是：**「我把 AI 產出分享給你，結果它裡面混了你本來看不到的資料」**。
一般 RBAC 只管「誰能開這個檔」，管不到「這個檔的內容是從哪些你無權的來源合成的」。

### 3.2 讀 / 寫的核可時序被刻意做成不對稱（`workshop-shared/src/gatekeeper.ts`）

這是整份設計最值得抄的一條，且**只有讀原始碼才看得到**——blog 沒講清楚。

- **讀（`authorizeObservation()`）＝同步**：「gatekeeper 在每個讀取操作上呼叫它，
  且**必須等到回應才能把任何東西回給 gadget**」。刻意建議在**取完資料之後**才呼叫，
  這樣 description 能包含實際資料細節；只要操作嚴格唯讀、且在回資料給 gadget 前呼叫就安全。
- **寫（`submitAction()`）＝完全非同步**：「它立即返回，但動作可能要很久以後才真的執行。
  設計上預期使用者可能**數小時或數天後**才核可，而這不應該造成任何問題。」

**沒有 skip 模式**：「gatekeeper 仍被要求提交所有動作以供核可；**不存在可以略過檢查的模式**。」
自動核可是佇列**內部**的政策，不是呼叫端的旁路——這正好是 bridge 的 POLICIES 一再警告的
「以省略達成 fail-open」的反面做法。

**「模擬」的代價它自己寫明了**：`rejectAction()` 的回傳型別是 `void | {restart?: boolean}`，
註解說「這有時是**會把動作模擬成已核可**的 gatekeeper 所需要的——session 可能處於難以回滾、
回滾會讓 Gadget 混亂的狀態。Overseer 會負責重啟。」
∴ 官方對「agent 基於模擬結果做下去、結果被拒」的答案是**重啟整個 Gadget**，不是回滾。
blog 把這件事講得很乾淨，介面定義沒有。

`revertAction()` 為選配：「gatekeeper 不強制實作。未實作時會指示使用者依動作描述手動還原。
**高品質的 gatekeeper 幾乎總是應該實作它。**」MCP gatekeeper 就沒實作——
`REVERT_UNSUPPORTED_MESSAGE`：「MCP 工具沒有描述如何還原自己。」

### 3.2b ActionStore 的當機安全紀律（`packages/mcp-shared/src/action-store.ts`）

排隊動作的狀態機是 `pending → applying → applied / rejected / failed`，落在 facet 自己的 SQLite。
最值得抄的是**兩條不對稱處置**：

1. **重啟即認賠，不重放**。建構子開頭無條件把所有 `applying` 改成
   `failed, retryable = 0`，理由寫在註解：「全新的 store 意味著全新的 DO 啟動。
   任何持久化的 claim 都屬於一個被中斷的前次啟動，且**絕不可重放，因為那個寫入可能已經落地**。」
2. **「送出前失敗」與「送出後失敗」分開判**。`callMayHaveTakenEffect(err)` 決定
   `retryable`；送出後失敗的訊息是「這個呼叫在送出**之後**失敗，∴ 它可能生效也可能沒有。
   重試前請先去伺服器確認。」

→ 這是把「at-most-once」寫成構造而非祈禱。凡是「重試可能造成重複副作用」的地方都適用，
與 bridge 是不是多人系統無關。

### 3.3 lazy revocation 與權限圖（`docs/sharing.md`）

⚠️ 這整節對 bridge 判定為**不需要**（單人系統），∴ 只留骨架備查：
角色全序 `build > use`；effective role = 從 owner 出發的可達圖最大值，
每次 `open()` 即時算不快取；撤銷只砍邊不級聯刪除 ∴ **可逆**（失去路徑者「只是變成不可達」）；
share link 只存 HMAC-SHA-256；權限變動時重啟 Overseer 強制重連。

**唯一可跨到單人系統的一條**——**型別當閘門**：`open()` 依角色回傳完整或受限介面，
∴「任何新加的介面方法，在開發者**有意識地決定** use 級能不能用之前，都會編不過」。
形狀與 bridge 拿 tsc 當承重面同構，但更進一步：讓「忘記想」變成編譯錯誤而非預設放行。

## 4. 對 bridge 的差距判定（Step 1 比對表）

| 面向 | Cloudflare OS | bridge 現況 | 判定 |
|------|--------------|------------|------|
| 動作走 mediated capability 而非裸憑證／裸 token | Gatekeeper typed binding | bridge-actions MCP tool（`POLICIES/mcp-first-actions.md` 已明訂裸 token 只是 fallback） | **已有**——同一個 move |
| 團隊 context／skill 策展 | `.agents/skills/`（實際只有一個 `write-gatekeeper`） | AI-canonical 正本 + wiki + preamble 注入 | **已有**，且 bridge 這層更厚 |
| Observer／permission graph／share link／HMAC | 完整一套 | 無 | **不需要**——那整套是為了擋**員工之間**的洩漏，bridge 是單人單租戶 |
| 動作核可時序 | 寫入非同步排隊、可等數天；讀取同步擋 | **ASK 也已經是非同步的**——`queue()` 立即回 `state:"queued"`，`commitPending()` 在 turn 結束才送出（`src/agent-actions.ts:644/664`） | **已有一半**（見下方更正） |
| agent 可基於「假定答案」繼續做 | 有（模擬 + 被拒時重啟） | 無——ASK 送出即 turn 結束，下一輪才拿到答案 | **值得借鏡**，但代價高（見 §4.1） |
| 側效動作有核可閘門 | 全部 side-effect 動作強制過佇列 | **無**——`send_file` / `delegate` / `schedule` 直接執行 | **可評估** |
| observation 當 provenance | 用於存取控制 | transcript 逐筆記了工具呼叫，但**沒有從「主張」反查「支持它的讀取」的鏈路**；證據分級（A/B/無）靠模型自述 | **可評估**——稽核／事實求證角度，不是權限角度 |
| 型別系統當權限閘門 | `open()` 回傳受限介面，漏想就編不過 | tsc 擋簽名，但無「新增能力預設拒絕」的型別構造 | **可評估**（低優先） |

**判定的判別式是單人 vs 多人**。Cloudflare OS 最亮眼的機制（ObserverRecord、可達圖、
lazy revocation、HMAC share link）全部服務於「同事之間不該互相洩漏」這個約束，
bridge 沒有這個約束 ∴ 它們是「不需要」而不是「還沒做」。
不要因為機制精巧就把它們塞進借鏡欄——那正是 `ms-external-repo-absorption`
列的常見錯誤之二「照搬不適配」。

### 4.1 ⚠️ 本頁初版的一條事實錯誤（2026-08-14 同日更正）

初版寫「bridge 的 ASK 是**同步阻塞**、agent 停在那裡等」，並據此把「非同步核可」
列為唯一結構性差異。**這是錯的。**

- **反證（A 級，一手）**：`src/agent-actions.ts:644` 的 `queue()` 直接回
  `{ ok: true, actionId, state: "queued" }`；動作累積在 `activeTurn.pending`，
  由 `commitPending()`（同檔 :664）在 turn 結束時才一次送出。
  本輪我自己呼叫 `ask` 時工具回的字面值就是 `ask accepted (...), state=queued`，
  且我在收到它之後繼續寫完整篇回覆——**agent 從未被阻塞**。
- **錯誤根因**：把「agent 拿不到答案」誤讀成「agent 被卡住等答案」。
  兩者的觀察表徵相同（答案都在下一輪才出現），但構造完全不同。
  我當時沒有讀 bridge 的碼就下了確定語氣的判斷——**違反事實主張閘門**
  （B 級證據卻寫成 A 級語氣），形狀同 [[verification-diagnosis]] 記的老問題。

**修正後的真實差距**：不是「同步 vs 非同步」，是「**turn 終結** vs **帶假定值續跑**」。

| | bridge | Cloudflare OS |
|---|---|---|
| 送出核可請求 | 非阻塞（queued） | 非阻塞（立即返回） |
| 送出後 agent 能否續跑 | **不能**——turn 在此結束 | **能**——拿模擬結果往下做 |
| 使用者延遲數天回應 | 沒問題（下一輪才續） | 沒問題（明文設計目標） |
| 假定值被推翻時 | 不適用（沒有假定值） | **重啟 Gadget**（`rejectAction → restart`） |

∴ Cloudflare 用「模擬 + 重啟」換來的東西，bridge 用「turn 邊界」換來——
**bridge 這條路沒有假定值，也就沒有假定值被推翻的失敗模式**。
兩者是不同的取捨點，不是一方落後另一方。

## 5. 該知道的限制

- **early access**，v2 完全重寫，自承粗糙邊角多。
- **「目前不接受外部貢獻」**：小 PR 可以，實質貢獻會被關。
  ∴ 若真進入吸收，`ms-external-repo-absorption` Step 5 的「產出回饋文件給來源方」**這條路不通**，
  發現的 bug 只能自己吞。這一點要在吸收決策時算進成本。
- 本機試跑：安裝 pnpm → `pnpm run-local` → http://localhost:8787。
  部署走 https://os.cloudflare.app/deploy 或 starter repo。

## 6. Step 2 借鏡排序（價值／成本）

篩掉「已有」與「不需要」後剩四項，依**價值/成本**排序：

| # | 項目 | 增量價值 | 整合成本 | 建議 |
|---|------|---------|---------|------|
| **B1** | at-most-once 紀律：重啟時把 in-flight 標為不可重試 + 區分「送出前/後失敗」 | **高（觀測後上修）**——命中 2 個真實缺口，其中 Telegram 出站是無界重試 | 低——落點集中在 `bot-setup.ts` 與 `restorePlanRun()` | **建議吸收**（觀測已完成，見 §7） |
| **B2** | 「沒有 skip 模式」：核可是佇列內部政策，不是呼叫端旁路 | 中高——直接對應 bridge 已知的「以省略達成 fail-open」失效形狀 | 低——紀律/文件層 | **建議吸收（文件層）** |
| **B3** | 側效動作核可閘門（bridge 目前完全沒有） | 中——但 bridge 是單人、動作皆本機，威脅模型弱 | **高**——要新增狀態機 + UI + 儲存 | **不建議**（YAGNI） |
| **B4** | 帶假定值續跑（模擬 + 被拒重啟） | 低——見 §4.1，bridge 的 turn 邊界已解同一問題且無假定值風險 | 高 | **不吸收** |

## 7. Step 3 方案與風險（僅 B1 / B2）

### B1 方案

落點是 bridge 既有的重試路徑（派工逾時重試、`run_plan` step 重跑、`/job resume`）。
`POLICIES/run-plan-orchestration.md` 已有一條同形狀的紀律——
「狀態說 done 但結果本體讀不回來**必須重跑並說明**，不得當成已完成跳過」——
但那是「疑似沒做→重做」，缺的是反方向：**疑似已做→不可自動重做**。

#### B1 觀測結果（2026-08-14 執行，A 級——逐檔讀原始碼）

我原本預期「適用面可能很小」。**盤點後推翻：命中兩個，其中一個是無界重試。**

| 重試／重放路徑 | 重放什麼 | 重放會有外部副作用？ | 現有保護 |
|---|---|---|---|
| grammY `autoRetry` **HttpError 分支** | 任何 Telegram API 呼叫 | **會——重複送出訊息／檔案**。HttpError＝傳輸層失敗，請求**可能已被 Telegram 處理**，只是回應沒回來 | ❌ **無，且完全不受 `maxRetryAttempts` 限制** |
| grammY `autoRetry` **5xx 分支** | 同上 | **會**——Telegram 收到了但內部錯誤，可能已投遞 | 由 `maxRetryAttempts: 3` 限次，但不判「是否可能已生效」 |
| grammY `autoRetry` 429 分支 | 同上 | 不會——429 代表**未**被處理 | 構造上安全 |
| `/job resume` | 所有 `status !== "done"` 的 step | **可能會**——specialist 是完整 CLI harness，死前可能已寫檔／`remember()`／git commit，這些不經 bridge 的動作層 | ❌ `restorePlanRun()` 只還原 `done`，其餘直接重派 |
| scheduler 錯過的週期性 tick | — | — | ✅ **已有**：明文「Missed recurring ticks are skipped」 |
| specialist 結果注入 session | 結果文字 | 重複注入 | ✅ **已有**：`src/reply-dedup.ts`（5 分鐘內容 hash 窗） |
| 同 session 重發同一個 action | 依 `actionId` | 快取回舊結果 | ⚠️ 部分：`record.results` 是**記憶體內**、鍵是 **agent 自選的 id**、且會 LRU 淘汰 ∴ 跨重啟或換 id 就失效 |

**最嚴重的一條（`node_modules/@grammyjs/auto-retry/out/mod.js` 逐字）**：
`rethrowHttpErrors` 預設 `false`，HttpError 走 `call()` 內層的 `while (res === undefined)`
迴圈 `continue`，而 **`remainingAttempts` 只在外層 `do…while` 遞減**
∴ 網路層失敗是**無界重試**（backoff 指數成長，上限一小時）。
bridge 在 `src/bot-setup.ts:188` 設了 `maxRetryAttempts: 3`——**那個值管不到這條路徑**，
兩個 `rethrow*` 都留在預設。

⚠️ **誠實邊界**：以上是**機制**的證實，不是**發生頻率**的證實。
`grammy:auto-retry` 的 debug 通道未開啟 ∴ 沒有歷史命中紀錄可查，
我**不宣稱**曾經真的發生過重複投遞。要量化得先開 debug 或加計數器。

⚠️ **其他風險與前置**：
- `reply-dedup.ts` 覆蓋的是**入站**（結果注入），不是**出站**（Telegram 送出）
  ∴ 上表第一列的缺口沒有被它蓋到——這點差一步就會誤判成「已有」。
- 可逆性：高（純新增判斷，不改既有語意）。

#### B1 實作結果（2026-08-14，僅修 Telegram 那一條；`/job resume` 未動）

新增 `src/telegram-retry-guard.ts`：把 `autoRetry` 的 `rethrowHttpErrors` 設成 `true`
（關掉無界迴圈），再用一個 transformer 接回**有界**重試，並套用上游的判準——
**看方法不看錯誤**：唯讀／冪等的可重試，`send*` 這種每次產生新內容的不重試，
未列到的 **default-deny**。

**原缺陷被實測出來了，不再只是讀碼推論**：變異測試 R5（把 `rethrowHttpErrors`
改回 `false`）時，端到端那條的紅燈訊息是
`sendMessage 超過 20000ms 未返回——疑似無界重試`。

驗證：`npx tsc -p .` 0 錯 · fast tier **156/156**（190.2s）·
變異測試 `node scripts/mutate-gate.mjs telegram-retry-guard` **5/5 killed**。

**過程中自己抓到兩個假東西**（都已修）：
1. 我在碼註解裡寫「transformer 順序裝反會整個靜默失效」——**誇大**。
   設了 `rethrowHttpErrors: true` 之後兩種順序對主行為都成立，
   真正差別只有「護欄自己的重試會不會重新經過 autoRetry 的 429 處理」。
2. 閘門初版用 `/rethrowHttpErrors:\s*true/` 比對原始碼，**恆真**——
   同檔註解裡就有這串字，變異把真設定改成 `false` 後正則仍命中註解
   ⇒ R5 落成 false-kill。改成整行錨定 `/^\s*rethrowHttpErrors:\s*true,\s*$/m`
   ＋反向斷言不得出現 `: false`。這是「錨點切太寬」的典型，
   靠變異測試才露出來，見 [[verification-diagnosis]]。

⚠️ **連動**：新增 smoke script ⇒ 支數 fast 155→156、full 158→159、total 162→163，
8 個 surface 的「N 支」全部同步（`check-doc-sync.mjs` 的白名單機制強制的）。
其中 `CLAUDE.md` 與 `AGENTS.md` 在 **R-2 保護清單**內 ∴ push 前需異源覆核。

### B2 方案

純文件層，寫進 `POLICIES/mcp-first-actions.md`：把 Cloudflare 那句
「不存在可以略過檢查的模式」的形狀記為設計原則——
**閘門的旁路要做成閘門內部的政策，不能做成呼叫端的條件跳過**。

⚠️ **風險**：
- `POLICIES/*.md` 在 **R-2 保護清單內** ∴ 改它**必須走異源覆核**（`run_plan` + `wf-review`），
  自審不算。這是硬成本，要算進去。
- 風險是「多一條沒人執行的紀律」。bridge 已有一次前科：宣稱有 hook 在強制、
  實際那支 hook 從不存在（見 `POLICIES/development-methodology.md` Section 7 的更正）。
  ∴ 若吸收，必須明寫它是**文字層自律、沒有機械強制**，不得暗示有東西在擋。

## 7.5 ⚠️ 我在 §7 與 commit `ff976f6` 裡寫錯的一條事實（2026-08-15 更正）

我寫過「`/job resume` 對 **status=running** 的 step 直接重派」。**`running` 這個 step 狀態不存在。**
`src/plan-run-store.ts` 的 `PlanRunStepStatus` 是
`"pending" | "done" | "failed" | "timeout" | "blocked" | "expanded"`——沒有 `running`。

我把**run 層級**的狀態（同檔另一處確實有 `"running" | "done" | "partial"`）誤讀成 step 層級。

**效果的描述仍然成立**（當機時在途的 step 會被重派），但**機制是我編的**：
真正的窗口是那個 step 從派工到 `patchPlanRunStep` 之間**一直維持 `pending`**，
而不是「被標成 running 然後被重派」。

形狀與 [[verification-diagnosis]] 記的 `correction-invents-new-causal-story` 完全一致：
真實觀察 + 沒查證的機制，數字對、語氣自信。
由 Codex（gpt-5.6-sol）第三輪跨 vendor 覆核抓到，前兩輪 glm-5 都沒發現。

## 8. 尚未做的事（誠實邊界）

- **沒動任何 bridge 的碼**，也沒改 `POLICIES/`。以上全是提案。
- 沒跑 `pnpm run-local`，沒觀察 Cloudflare OS 實際執行。
- B1 的適用面盤點**還沒做**——那是吸收與否的決定性前提，不是實作細節。
- clone 落在 `scratch/ext/cloudflare-os`（`.gitignore` 擋住，不會進版控）。
