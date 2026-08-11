---
title: 異源對抗覆核紀律
type: concept
created: 2026-08-05
updated: 2026-08-12（新增派工前能力軸：blind advisor 會產出幻覺、scope 中途擴張的敘述凍結陷阱、樣板知識同源天花板實證）
sources: [f_69884b, f_31febf, f_e85cc9, f_7a2f9d, f_fc4695, f_233414, f_243d72, f_6af093, f_bcc99d, f_932293, f_cdf362, f_0dd859, f_6e52ff, f_8e6494, f_6ae02c, f_b490fe, f_ca4aa1, f_2f425e, f_9bcb64, f_f81858, f_5317fe, f_b1c968, f_e97f74, f_03f2f0, f_667928, f_14cb23, f_15086c, f_d6f8a7]
---

# 異源對抗覆核紀律

2026-08-05 topic review 從過大的 [[bridge-acp]]（原 57 筆）拆出。核心主張：**單一模型自審有結構性天花板，異源模型對抗覆核能打破它**——這一頁記的是這套紀律怎麼形成、用什麼流程、以及它抓到過什麼同源自審抓不到的東西。

## 長期警戒模式清單（設計/審查對抗檢查清單）

來自 bridge 的 `.claudedocs/records/問題追蹤.md`，設計階段架構師必讀：

- **#001** 未經查證就宣稱某物存在
- **#002** 把「存在」與「路由/接線」混為一談（因果宣稱與程式碼實際時序不符，2026-07-31 升格，涵蓋註解/AI.md/commit message/測試敘事四類高風險位置）
- **#003** 單一來源就推斷結論
- **#004** 忽略字面上的明確證據
- **#005** 把共享值私有化（shared-value privatization）
- **#006** 行數預算過度樂觀
- **#007** 單一視角自審的盲點（需異源 skeptic 才能打破——本頁的存在理由）

## 覆核紀律（2026-08-02 最新版，累積演化而來）

1. **開放授權不給檢查清單**：讓覆核者自己探索，且要求它讀原始碼而非信 commit message；結論不可照單全收，每條 finding 須自己重現後才動手
2. **多輪連續覆核要換新 context**：修法常是上一位覆核者提出的建議，讓他覆核自己的提案等於同源自審——第二輪起刻意不告知前一輪結論，避免錨定
3. **可多輪、範圍逐輪收窄**：每修完一輪 finding 就對新 commit 再派一輪範圍限定的覆核，直到只剩敘事精確度類 finding 才收斂
4. **收斂條件**：第二輪若回報無 high/medium 即視為收斂可 push，不強制第三輪
5. **誠實交代覆核範圍**：覆核者的可 push 判斷是針對它看過的那個 commit，之後的修正 commit 未經覆核
6. **明確授權回報「已收斂」**：避免覆核者為交差硬湊 finding——連續多輪都生出 finding 本身可能是覆核者在配合期待

## 價值實證（時間序）

| 日期 | 事件 | 抓到什麼 |
|---|---|---|
| 2026-07-26 | Fable 5 對 commit `afb9d8e` 覆核（37 次工具呼叫、587 秒） | 「接受 protobufjs 依賴」的原始論證存在關鍵推理缺陷 |
| 2026-07-30 | Fable5 push 前覆核（開放授權不給檢查清單） | 4 條中 3 成立 1 駁回，且有 1 條連覆核者也枚舉不全 |
| 2026-07-31 | Fable5 對 unpushed commit 覆核 | 最有價值一條不是程式 bug，是「commit message / 註解 / AI.md 三處共用同一個錯誤因果敘事」——因為寫註解時是從意圖推理而非讀實際呼叫順序時序 |
| 2026-07-31 | 檢查清單式 prompt 覆核 | 同源自審漏掉的 medium 缺陷；且覆核推翻了原本的風險模型（怕強制補送打穿 429，實際上舊碼節流早已失效） |
| 2026-08-06 | Codex ACP authMethods 誤判修正的三輪覆核 | 缺陷連續往上層遷移 4 層：碼裡 hint 字串硬編 → 靜態文件（SKILL.md）與碼矛盾 → 另一份靜態文件（DESIGN.md）錯誤值清單漏舉 → 列舉完整性（三份文件都沒提的 error 值）；每層都是異源在下一輪抓到，每輪都誤判「這輪應該只剩敘事精確度」 |

**可重用教訓**：檢查清單式的 prompt 也能抓到同源自審漏掉的缺陷，關鍵是至少有一項要問成「開放式的互動問題」而非「確認某宣稱對不對」。「往上層遷移」沒有層數上限——收斂判準要看這輪還有沒有新類型的 finding，不是已經修過幾輪。

## 覆核工具本身的限制（2026-08-06）

- **不要把覆核自動化成無條件停止閘門**：CLI 提供的「stop 時自動跑異源覆核」hook（如 Codex `--enable-review-gate`）常見陷阱是①沒有 diff 閘門（純文字問答也觸發）②失敗一律 block 不是降級（額度耗盡/timeout/空輸出都算 block）③agentic 工具迴圈把成本放大。判準：免費/有限額度方案一律不開；付費且長時間連續改碼才值得評估，且要先確認有 diff 閘門、失敗是 warn 不是 block。已寫進 `ms-cross-model-adversarial-review` 正本。
- **`codex exec -s read-only` 會被執行政策擋掉 git**（2026-08-06 實測 0.146.1：連 `git --version` 都 "rejected: blocked by policy"）：派 Codex 做 push 前覆核時必須先用 `git show <commit> > diff.txt` 把 diff 匯出成檔案再餵路徑，否則它只讀得到工作區現況、完全覆核不到「這次改了什麼」。改用 `-s workspace-write` 才看得到 commit 內容，但 scratchpad 若在 workspace 之外仍無法寫檔實跑，只能讀既有 artifact（比獨立重跑弱一階，回報時要標明）。

## Advisor 工具 vs 異源覆核（2026-08-02 判定，不可互相取代）

Claude Code 的 `advisor` 是 server-side tool：零參數、呼叫時整段對話逐字稿自動轉發，回傳 `advisor_tool_result` content block（與 `web_search` 同族）。

**不能取代 push 前異源覆核**，三個理由：
1. 視野等於主 agent 的視野，讀不到你沒讀過的檔案，無法「自己讀原始碼而不信敘事」
2. 對象是「這場對話」不是「這個 commit」，跨 session 改動缺席
3. 是模型自主 opt-in，不是 gate（覆核紀律是 hard requirement）

價值在時間軸另一端（設計決策前／卡住時），與 push 覆核互補，不是替代。

## 覆核者選型（成本分級，2026-08-02，判準：改動有沒有碰承重路徑）

Claude 家族相對單價（catalog pricing tier）：Sonnet 5 = 1x、Opus 5 = 1.7x、**Fable 5 = 3.3x**、Haiku 4.5 ≈ 0.3x。覆核者是 agentic 的（工具迴圈讀進去的碼全算 input），模型選型的成本差會被放大。

分級規則（已寫進 `ms-cross-model-adversarial-review` 正本）：
- 孤兒 import／死碼 → **不派人**，交給型別系統
- 敘事比對、恆真斷言 → Sonnet 級
- 不變式／論證推理／時序 race → 最強模型（Fable 5）

### Domain 判定與單表雙軸結構（2026-08-07）

**異源性的單位是模型供應商**，不是 CLI／harness／分身名字：
- `vc-kiro-delegate` 走的是 `kiro-cli --model claude-opus-4.5`，所以「Claude 寫、Kiro 覆核」在模型層是**同源**（只有 harness/context 不同），屬**弱異源**
- 弱異源對「換個 context 就會發現」的錯（枚舉漏、敘事與碼不符、恆真斷言）仍有效
- 對「這個模型本來就會這樣想」的錯（共有推理偏誤、共有知識盲點）沒有防禦力
- **承重路徑優先跨 vendor**（anthropic → openai/Codex）

拿不到強異源時降級不跳過，階梯為：**強異源 → 弱異源 → 同源重置（只餵 diff 不餵 commit message／註解／AI.md，切斷敘事回音是這一層唯一有效的機制）→ 不覆核**，且降級必須留痕、不可只寫「已覆核」。

**核心判準**：強異源與貴是兩個獨立的軸，不可互換。glm-5 是 0.50x credits（比 Sonnet 便宜）卻是跨 vendor 強異源，所以「跨 vendor 麻煩就改派同 vendor 最強模型（Fable 5，3.3x）」是**同時更貴且更弱**的錯誤推論。

**kiro-cli 預設 model 是 auto**（`--list-models` 輸出的 `*` 標在 auto，說明為「Models chosen by task」且不回報實際挑選結果）：不帶 `--model` 呼叫 Kiro 當覆核者時 domain 不可知，比同源更糟——連「本輪為弱異源」這種降級留痕都寫不出來，所以當覆核者用時**一律顯式帶 --model**。

2026-08-07 `ms-cross-model-adversarial-review` 的覆核者選型重寫為**單表雙軸結構**（commit a8e3725 已 push）：原本 domain 與 tier 分成兩張表，因跨 vendor 覆核連兩輪抓到「兩張表分類軸對不齊」而判定是結構問題非標籤問題，改為一張三欄表（預期的 finding 類型 | domain | tier）。

### Findings 處置的第三種路徑（2026-08-07）

除了**採納**與**駁回**，還有第三種處置：**「指的位置對、但建議是錯的」**。

2026-08-07 實測第三輪 glm-5 建議把表格標頭括號拿掉，照做會讓第一輪的 finding 原地復活，但它指出的接縫是真的。若照單全收會在兩個 finding 間來回，若因建議不對就整條駁回則會錯過「連兩輪打在同一個接縫＝**結構問題不是措辭問題**」這個訊號。

**結構問題判定原則**：若連續兩輪的 finding 落在同一個接縫，應判定為結構問題而非措辭問題並**改做結構解**，不要繼續修標籤。實測併表才真正消除該類錯誤。

### Findings 處置的三個獨立維度（2026-08-07）

收到 code review／異源覆核的 findings 時，處置有三個獨立維度而非一個：

1. **這條成立嗎**——finding 描述的問題是否真實存在
2. **它給的建議對嗎**——即使問題成立，覆核者給的修法本身可能是錯的（見上一節第三種處置）
3. **它的修法屬不屬於本次改動的範圍**——最容易漏的一維：成立且建議正確的 finding，仍可能把不相干的既有缺陷拉進來造成範圍蔓延

「不要盲目修掉每一條 finding」指的不只是駁回錯誤的 finding，也包含把**正確但越界**的 finding 記錄下來留待另一次改動處理，而非當場擴大本次 PR 範圍（2026-08-07 telegram-kiro-bridge 記錄此模式為 `review-findings-pull-scope`）。

## 派工前的第三個軸：能力（讀不讀得到檔）——不是 domain 也不是 tier（2026-08-11）

domain（異源強度）與 tier（成本）是兩個獨立軸（見上一節），但兩者都假設覆核者**讀得到材料**。這個假設不一定成立，而且失效時**沒有任何自報訊號**：

telegram-kiro-bridge 的 `moa-ref-kiro`（glm-5，跨 vendor）與 `moa-ref-adversary` 派去盲審一個 commit 時都產出了帶行號的逐字引用——但兩者的設定都讓它們讀不到檔（`readOnlyLens:true` 卻只給 `readonly` MCP、或 `mcpServers` 為空且 harness 不帶 `--agent`）。`moa-ref-kiro` 那份報告**捏造了不存在的檔名與變數名**；`moa-ref-adversary` 那份報告的證據欄自己寫「逐字證據（推論）」。兩者都沒有主動說「我讀不到」。改派可讀檔的 `bridge-dev`／`verifier`（走 `claude-agent-acp`）才拿到有效覆核，其中 `verifier` 自行重跑驗證指令並比對 tree hash 排除過期戳記。

**派工前必查**：這個覆核者的 harness／MCP 設定實際上讀不讀得到檔？跨 vendor 不等於能讀檔——目前 telegram-kiro-bridge **沒有任何「可讀檔＋跨 vendor」的分身**（唯二非 Anthropic 模型 `moa-ref-kiro`/`moa-ref-codex` 都是 blind advisor），能做到的最強是「同源、獨立 context、可讀檔」，留痕時不要把這個講成跨 vendor 異源。

## Scope 中途擴張會凍結敘述成假事實（2026-08-11）

在 scope 只有 A 的階段寫的「診斷」敘述（如「X 缺 Y——尚未修」），若後續 scope 擴大到連 Y 一起改掉，卻沒回頭改那句敘述，就會變成文件、程式碼、commit message 三者互相打臉的假事實——`scripts/AI.md` 寫「`ACP_EFFORT_FALLBACK.kiro` 缺 `max`——尚未修」，但同一個 commit 已經補上了 `max`，由 `verifier` 異源覆核抓到。

**判準**：任何一輪只要 scope 從 A 擴到 A+B，收尾前重讀「在只有 A 的前提下寫的每一句對 B 的描述」——「尚未修」「目前沒有」「待處理」這類現在式否定句最容易凍結。修法不是刪掉整句，是拆成「已修的那部分」與「仍為真、但不是這裡能修的那部分」。

## 樣板知識會偽裝成從碼推導：同源天花板的一手證據（2026-08-11/12）

claude-sonnet-4.6 與 claude-opus-4.5 對 `src/concurrency.ts` 的 semaphore「超上限」宣稱與**程式碼實際內容無關**：未注入缺陷時兩臂都主張「waiter 被喚醒沒有 `active++` 導致超上限」（該版是直接交棒，`active` 本來就不該變，是誤報）；把 `active--` 真的搬到交棒之前（缺陷真的存在）後，sonnet 反而在有註解版斷言「release 先叫 waiter、不先 `active--` 本身是正確的」——與眼前的碼相反。兩個模型在同一處犯了完全相同的誤報，是**同源天花板**的直接證據：這類覆核者對有標準樣板的碼（semaphore、鎖、佇列）是在複述樣板知識、不是從碼推導。要驗這一軸得用行為測試而非模型審查，覆核找不到不代表沒有缺陷。詳見 [[bridge-model-strategy]] 的對照實驗完整數據。

## 與 SDD 規格自審閘的關係

規格驅動開發（SDD）流程的規格自審品質閘（2026-07-28 定案）是**互補而非取代**：機械化檢查未填佔位符、內部矛盾、範圍蔓延、模糊敘述——擋掉的是「人工審查時最浪費來回的低階瑕疵」，異源對抗覆核處理的是更深層的論證/因果/不變式缺陷。

## 這套紀律本身的固化

使用者已把「多視角分析 + 每個發現派 skeptic 對抗驗證」的 review 流程做成固定 skill（`ms-cross-model-adversarial-review`，score 0.87，2026-08-01 升格），並會對既有 skill 原始碼重跑此流程來優化。

## 相關

- [[bridge-acp]] — 本頁拆出的來源頁面，ACP 協定與 model 配置機制
- [[bridge-model-strategy]] — 覆核者選型與 model 分工的延伸主題（同源自 bridge-acp 拆分）；sonnet-4.6[max] vs opus-4.5 對照實驗完整數據
- [[bridge-specialist]] — moa-ref-kiro/adversary 的 blind advisor 設定細節（`readOnlyLens`／`mcpServers`／harness 組合）
- [[verification-diagnosis]] — 覆核揭露問題後的驗證方法論（恆真斷言、突變測試）
- [[bridge-smoke-gate]] — 孤兒 import／死碼交給型別系統攔（noUnusedLocals 閘門）
