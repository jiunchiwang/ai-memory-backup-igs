---
title: Go CLI 靜態壓縮 Claude Code session transcript：架構、inherit 分頁、ADR-003 狀態判定階梯與 ADR-004/005 對抗覆核發現、與 bridge session-extract/agent-diagnostics 的比對與借鏡候選、安裝腳本會寫入 junction 正本的風險
type: query
created: 2026-08-09
updated: 2026-08-09
status: 借鏡評估已結案——無項目吸收（見 Section 4）
sources:
  - https://github.com/Mapleeeeeeeeeee/cc-session-reader
  - https://raw.githubusercontent.com/Mapleeeeeeeeeee/cc-session-reader/main/README.zh-TW.md
  - https://raw.githubusercontent.com/Mapleeeeeeeeeee/cc-session-reader/main/SKILL.md
  - https://raw.githubusercontent.com/Mapleeeeeeeeeee/cc-session-reader/main/docs/benchmark.md
  - https://raw.githubusercontent.com/Mapleeeeeeeeeee/cc-session-reader/main/docs/adr-002-tool-compression-optimization.md
  - https://raw.githubusercontent.com/Mapleeeeeeeeeee/cc-session-reader/main/docs/adr-003-tool-result-status-and-summaries.md
  - https://raw.githubusercontent.com/Mapleeeeeeeeeee/cc-session-reader/main/docs/adr-004-failure-retention-strategy.md
  - https://raw.githubusercontent.com/Mapleeeeeeeeeee/cc-session-reader/main/docs/adr-005-collapse-retry-loops-and-reads.md
---

# cc-session-reader 研究（外部 repo 吸收評估）

2026-08-09 依 `ms-external-repo-absorption` 流程研究 `Mapleeeeeeeeeee/cc-session-reader`，
走到 Step 2（現狀盤點 → 對照表 → 借鏡排序）為止，**未進入實作、未安裝**，吸收範圍待裁決。

相關頁面：[[adversarial-review]]（該 repo 的 ADR-004/005 用 Codex 做異源覆核，與本地紀律同構）、
[[verification-diagnosis]]（ADR-003 的「假 ok」正是綠燈假象的一種）、
[[bridge-session]]（bridge 既有的 session 蒸餾層，本頁主要對照基準）、
[[bridge-infra]]（`agent-diagnostics.ts` 讀同一批 transcript 檔）、
[[bridge-research]]（外部框架借鏡總索引）、
[[paulsha-cortex-governance-plane]]（同流程的前一次外部 repo 研究）。

## 0. 證據等級（先講清楚）

本頁所有內容的來源是 **repo 自述文件的逐字原文**（走 `raw.githubusercontent.com` 直取，
不經 WebFetch 摘要模型——沿用「否定式主張／存在性主張要用二元探針，不採信摘要」的教訓）。

- **A 級**：「repo 這樣宣稱」「ADR 這樣寫」「tree API 回傳這些檔案且 `truncated: false`」。
- **B 級 / 未驗證**：實際執行行為。**沒讀 Go 原始碼、沒安裝、沒跑過**。
- ∴ README 的「token reduction 80–88%」只能敘述為「它自己這樣量測並公開了方法與公式」，
  **不得寫成「經證實壓縮 80%」**。

## 1. 這是什麼

Go 寫的 CLI，讀 Claude Code 的 session transcript JSONL，**純靜態壓縮**成精簡文字餵回 context。
**不使用 LLM**。每個 tool call 壓成一行（tool name + 關鍵參數 + result 狀態），
user／assistant 對話文字**完整保留不壓**。

| 項目 | 值（2026-08-09 查） |
|------|------|
| 授權 / 語言 | Apache-2.0 / Go |
| 建立 / 最新 release | 2026-05-28 / v0.1.71（2026-08-08） |
| ★ / fork / open issues | 56 / 10 / 0 |
| 規模 | 單人作者，約 90 個檔案，含 5 篇 ADR + benchmark 文件 |

八個子命令：`list`／`read`／`context`／`inherit`／`stats`／`audit`／`expand`／`usage`。

- **`inherit`** 是核心：把整個 session **分頁**灌進新 context（每頁 ≤20K chars），
  CLI 端記住讀取進度，重複呼叫同一命令就翻頁，出現 `[inherit complete]` 為止；`-reset` 重來。
  設計動機是 `read` 預設截斷 200 行，多數 session 遠超過 ∴ 只看得到開頭。
- `expand <id> <tool-id>` 可還原任一被壓掉的 tool call 原始 input/result——
  **壓縮是有損的，但保留了逆向查詢的把手**。
- `audit` 取樣「被過濾掉的內容」，用來確認沒漏掉重要資訊（自帶反向檢查機制）。
- 架構上 `internal/claudecodec` 是**唯一**與 JSONL 格式耦合的套件，
  其餘經 `TranscriptReader`／`HeaderScanner` 介面存取。

## 2. 三篇 ADR 的實質發現（本次研究最有價值的部分）

這三條是**協定層／方法論層**的知識，價值不依賴 Go 或這支 CLI。

### ADR-003 — tool 結果狀態判定階梯（Accepted）

原實作「`toolUseResult.success` 欄位不存在就預設為 true」，被真實 transcript 推翻：

- **Bash 結果根本沒有 `success` 欄位**（只有 `stdout/stderr/interrupted/isImage/noOutputExpected`），
  ∴ 失敗指令被渲染成自相矛盾的 `-> ok: Exit code 1`。
- `Read` 結果同樣沒有 `success`。只有少數工具（如 Agent 生命週期操作）明確設定。
- `tool_result` content block 的 `is_error` **當時完全沒被解析**，而且**即使解析也不可靠**：
  真實 transcript 中存在 `is_error: false` 但文字寫著 `Exit code 1` 的 Bash 結果——
  Claude Code 把非零 exit 當成正常結果回報，只把 exit code 附在文字裡。

修法是四段階梯：① `success` 存在就用它 → ② `is_error: true` → 失敗 →
③ **保守列舉式**內容嗅探（目前只有 `Exit code N`（N≠0）與 `... hook error` 前綴）→ ④ 否則 ok。

> 設計理由值得抄：嗅探**刻意做成小白名單而非啟發式**，因為「假的 FAILED 誤導讀者的程度
> 和假的 ok 一樣糟」。新增 pattern 必須附**真實 transcript 樣本作為證據 + 回歸測試**。

### ADR-004 — 失敗訊息保留策略（Proposed，**刻意不實作**）

跑了 fleet data：**379 sessions / 30 天 / 1,194 個失敗**，失敗文字長度分布（chars）：

| p50 | p75 | p90 | p95 | p99 | max |
|-----|-----|-----|-----|-----|-----|
| 143 | 407 | 1,274 | 2,093 | 11,895 | 26,029 |

極度右偏：最長的 10%（>1,274 chars）佔了總失敗字元的 **68%**（522K/763K）。

方法論上的三個好習慣：

1. **明確標註偏誤方向**：判定階梯刻意保守（未知形狀 → 判 ok）∴ 這是「**已偵測到**的失敗」
   分布，真實分布只會更寬；並註明是以 chars/runes 計、非 tokens。
2. **標出未經證實的部分**：head/middle/tail 的最佳比例「從未對照標註樣本量測 → unproven」。
3. **異源對抗覆核**：六條設計主張送 **Codex（xhigh）**覆核，結果 **四條 PARTIAL、兩條 REFUTED**。
   其中一條修正是「候選行要用**單一加權排序 + 分類上限 + 預算**，不能做成分層——
   分層會讓前面的層把預算吃光」。

結論是 **deliberately deferred**：即使新方案「任何合理閾值都嚴格優於現狀（200 runes 平切）」，
仍決定不實作，只把證據與覆核結果寫進 ADR，讓未來的修訂**從證據出發而不是重新推導一次**。
另有一則有用的取證：某 session 在繼承自己的歷史後，**6.5 分鐘內連發 19 次 `expand`**——
摘要不足時的失敗模式是**探索性亂翻**，不是一次乾淨的取回。

### ADR-005 — 折疊重試迴圈與連續同檔 Read（Accepted）

連續失敗的同指令折成一行 `[Bash#<last-id>] <desc> -> FAILED ×N: <error>`，
但關鍵在那條不變式：**錯誤摘要必須完全相同才折**。

> 第一版**沒有**這條，會把「較早發生的、不同的錯誤」藏在最後一個後面——
> 這是**對抗覆核在任何 release 之前抓到的**。

其餘保守設計：`×1` 永不出現；跨越成功呼叫／不同工具／任何**已渲染**事件都不折；
放寬識別規則必須附真實樣本 + 回歸測試（與 ADR-003 同一道證據門檻）。

## 3. 與 bridge 既有能力比對（Step 1 對照表）

| 功能 | cc-session-reader | bridge 既有 | 判定 |
|------|------|------|------|
| 讀 `~/.claude/projects/<slug>/<id>.jsonl` | 核心資料源 | `src/agent-diagnostics.ts:56` `transcriptPath()` 已讀同一批檔 | 已有，但用途不同（取證 vs 壓縮） |
| session 蒸餾／摘要 | 靜態、確定性、無 LLM | `src/session-extract.ts` + `/dream` + claude-mem，**靠 LLM 精選** | **互補，非取代** |
| 分頁灌 context | `inherit`，≤20K chars/頁、CLI 端記進度 | preamble 凍結 + 記憶注入（機制不同） | 可借鏡 |
| tool call 壓一行 + 狀態判定 | 有，含 ADR-003 階梯 | 無等價物 | 可借鏡 |
| 壓縮率／成本量測 | `stats`／`benchmark`（接 Anthropic token counting API） | 無 | 差距（低優先） |
| 還原被壓內容 | `expand <tool-id>` | 不適用 | — |

## 4. 借鏡評估結論（Step 2/3 · 2026-08-09 查證後）：**無項目值得吸收**

> ⚠️ 本節推翻了本頁初版的候選排序。初版第 1 順位「bridge 的 `agent-diagnostics.ts`
> 在判斷 tool 成敗時踩同一個坑」是**錯的**：該模組只 parse
> `type:"system", subtype:"api_error"`（`src/agent-diagnostics.ts:79`），
> **從頭到尾不看 tool result**，與 ADR-003 沒有交集。錯誤保留在此以記錄形狀。

| 候選 | 判定 | 理由 |
|------|------|------|
| ADR-003 狀態判定階梯 | ❌ 駁回 | 前提在本機不重現（見 Section 6 實測）。且 bridge 沒有等價的「欄位缺席預設 ok」邏輯——`sessionManager.ts:1256/1289` 靠 ACP 顯式 status，兩個分支都明寫。 |
| turn 取證工具 | ⚠️ 不是設計吸收 | bridge 已有 `agent-diagnostics.ts` 專職撈 api_error，窗口大小是踩坑調出來的。cc-session 的價值在「事後便宜回顧整個 session」＝**工具採用**決策，與 bridge code 無關，另有 Section 5 的 junction 風險。 |
| `audit` 反向檢查構造 | 🟡 真實 gap，低優先 | `session-extract.ts` 是把 bridge 自己的 **markdown** transcript 丟給 LLM 抽 facts，確無「漏了什麼」的反查。但 `wf-verify` 反向遍歷、`factlint`／`wikilint` 已覆蓋鄰近功能，增量價值低於改動風險。 |
| ADR-004/005 的方法論 | ✅ 印證，非借鏡 | fleet data + 標偏誤方向 + 標 unproven + 異源覆核 + 刻意不實作，bridge 已在做（見 [[adversarial-review]]）。外部獨立長出同一套是好訊號，但沒有可搬的東西。 |

**根本原因**：兩系統的資料源與目的其實**不重疊**——cc-session 吃 Claude Code 的 JSONL、
產「可重新灌回 context 的壓縮歷史」；bridge 的 `session-extract` 吃自己的 markdown
transcript、產「長期記憶 facts」。本頁初版把它們放進同一張比對表時**高估了重疊度**。

## 5. 風險與注意事項

- ⚠️ **安裝腳本會寫進 skill 正本**：`install.sh`／`install.ps1` **預設**安裝一份 skill 到
  `~/.claude/skills/cc-session`，而本機 `~/.claude/skills` 是 **junction 到 AI-canonical 正本 repo**
  ∴ 第三方安裝腳本會直接寫進正本、繞過 `sync.ps1` 投影流程，且是靜默的。
  真要安裝就用 `--no-skill`（Windows 互動模式會詢問，別按預設），
  或把 SKILL.md 走正本流程手動放。參照 [[ai-strategy]] 的投影紀律。
- 其 `SKILL.md` 末尾有「回饋」一節，**指示 agent 在完成任務後提示使用者去 GitHub 給星星**。
  無害，但那是寫進 agent 指令裡的推廣文案，安裝前要知道。
- 預設會寫 CLI 使用追蹤 `usage.jsonl`；可用 `no_usage: true` 或 `CC_SESSION_NO_USAGE=1` 關閉。
- 單人維護、v0.1.x、56★ —— 成熟度上適合當**概念來源與一次性取證工具**，
  不適合當 bridge 的執行期相依。

## 6. 實測：ADR-003 的 `is_error` 主張在本機不重現（2026-08-09，A 級）

驗證動機：ADR-003 若成立，缺陷會落在 bridge 的這條線——上游 adapter
`@agentclientprotocol/claude-agent-acp` 的映射（`dist/acp-agent.js:5802`，逐字）：

```js
isError = "is_error" in chunk && chunk.is_error ? "failed" : "completed"
```

失敗的 Bash 若被報成 `completed` → `_consecutiveToolFails` 不累加 →
`sessionManager.ts:1318` 的 Reflexion hint 對「指令／測試失敗」這個最常見失敗類**永不觸發**。

量測：本機 `~/.claude/projects/G--AI-telegram-kiro-bridge-main/` 最近 25 份 transcript，
共 1,260 個 `tool_result` block。

| 觀察 | 結果 |
|------|------|
| 非零 `Exit code N` 的結果 | 18 筆，**18/18 皆帶 `is_error: true`** |
| `Bash` 的 `is_error` 欄位 | **從不缺席**（false 497 / true 8） |
| 欄位缺席的工具 | Edit 208、Read 106、Agent 48、Write 27…（Edit 另有 50 筆 `true`）→ **缺席＝成功** |
| 缺席 `is_error` 但文字帶失敗特徵 | **0 筆** |

∴ 現行 Claude Code 的 `is_error` 是可信的失敗訊號，adapter 映射正確，bridge 該路徑健全。
合理推測 ADR-003 量的是較舊版本，或 Claude Code 後來修了。

**誠實邊界**（照 [[verification-diagnosis]] 的 0/N 紀律）：
① n=18 太小——用 (1-p)^N 反推，真實錯誤率 p 高到約 15% 仍有 5% 機率量到 0/18
∴ 這是「未觀察到」不是「證明為零」；② 樣本為單一專案目錄、單機、單一近期版本；
③ 驗的是 **transcript 表示法 + adapter 原始碼**，未端到端驗 SDK 串流 chunk 的形狀——那段仍是 B 級推論。
