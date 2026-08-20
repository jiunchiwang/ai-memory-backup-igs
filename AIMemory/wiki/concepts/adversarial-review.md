---
title: 異源對抗覆核紀律
type: concept
created: 2026-08-05
updated: 2026-08-20（ingest-ripple：補 4 條——逐層上移的輪次結構量到四層、三個自審失效形狀、不可信清單擴充至 SPEC/測試名稱、輪數不能替代 vendor 多樣性）
sources: [f_69884b, f_efd659, f_31febf, f_e85cc9, f_7a2f9d, f_fc4695, f_233414, f_243d72, f_6af093, f_bcc99d, f_cdf362, f_0dd859, f_6e52ff, f_8e6494, f_6ae02c, f_070546, f_b490fe, f_ca4aa1, f_2f425e, f_9bcb64, f_f81858, f_5317fe, f_b1c968, f_e97f74, f_03f2f0, f_171670, f_14cb23, f_15086c, f_d6f8a7, f_50ef2a, f_74c227, f_91280b, f_8e2dd2, f_b29a96, f_02d768, f_2f0f60, f_602d87, f_eb2436, f_5d91c4, f_8929d7, f_b860aa, f_7a7712, f_ae1f66, f_982e49, f_afb9ab, f_06eb83, f_bb8f33, f_3356be, f_a09852, f_97790d, f_9c2a72, f_27f464, f_b639af, f_dc2548, f_a2eb1a, f_055d6e]
history_sources: [f_99c92a]
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
7. **節制條款（2026-08-12）**：剛跑完一輪覆核後不要馬上再派同一個重量級覆核者（如 Fable5）跑第二輪——與第 2 點的「換 context」互補，這條管的是頻率而非身分

## 價值實證（時間序）

| 日期 | 事件 | 抓到什麼 |
|---|---|---|
| 2026-07-26 | Fable 5 對 commit `afb9d8e` 覆核（37 次工具呼叫、587 秒） | 「接受 protobufjs 依賴」的原始論證存在關鍵推理缺陷 |
| 2026-07-30 | Fable5 push 前覆核（開放授權不給檢查清單） | 4 條中 3 成立 1 駁回，且有 1 條連覆核者也枚舉不全 |
| 2026-07-31 | Fable5 對 unpushed commit 覆核 | 最有價值一條不是程式 bug，是「commit message / 註解 / AI.md 三處共用同一個錯誤因果敘事」——因為寫註解時是從意圖推理而非讀實際呼叫順序時序 |
| 2026-07-31 | 檢查清單式 prompt 覆核 | 同源自審漏掉的 medium 缺陷；且覆核推翻了原本的風險模型（怕強制補送打穿 429，實際上舊碼節流早已失效） |
| 2026-08-06 | Codex ACP authMethods 誤判修正的三輪覆核 | 缺陷連續往上層遷移 4 層：碼裡 hint 字串硬編 → 靜態文件（SKILL.md）與碼矛盾 → 另一份靜態文件（DESIGN.md）錯誤值清單漏舉 → 列舉完整性（三份文件都沒提的 error 值）；每層都是異源在下一輪抓到，每輪都誤判「這輪應該只剩敘事精確度」 |
| 2026-08-04 | `scripts/refresh-codex-skill-links.mjs` dry-run 判斷 | 主 agent 靠讀碼推理判成「下次 npm install 會擴成 37 支」，方向完全相反（真根因是 `Dirent.isDirectory()` 不跟隨 junction，見 [[bridge-memory]]）——異源覆核抓到；教訓是這類「實際生產行為」要直接跑 dry-run 驗真實環境，不能靠讀碼推理 |

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
- 不變式／論證推理／時序 race → ~~最強模型（Fable 5）~~ **2026-08-13 更正：跨 vendor 優先（`kiro-cli --model glm-5`，0.50x 且強異源）**，Fable 5 降為「跨 vendor 那輪產出明顯偏弱（只回敘事層、拿不出反例）時才補的第二輪」。這一行原本與下方〈核心判準〉自相矛盾——2026-08-07 補了雙軸判準卻沒回頭改它。

### 覆核的 token 成本結構（2026-08-13 首測 · 2026-08-17 重測改寫）

「覆核花的 token 比實作還多」的三個相乘項，量測與完整表格在 `ms-cross-model-adversarial-review` 正本：

1. **冷啟 prefix**（2026-08-17 八臂重測，CLI 2.1.233）：全開 **88,147**、`--strict-mcp-config` 87,164、`--setting-sources ""` 36,161。⚠️ **同日下修為 76,612**——量測過程發現 `~/.claude/CLAUDE.md` 有 10 個「以為註解掉了」的 @import 仍在載入（`#` 是 Markdown 標題不是註解），拿掉 `@` 後實測省 11,535；下列比例是修復前的組成，總量請用 76,612（見 f_cf5316）。∴ 現行組成是 **地板 36,161（41%）＋ user 設定鏈 32,185（36.5%）＋ project 設定鏈 19,810（22.5%）＋ MCP 僅 983（1.1%）**（user／project 兩項相加 51,995 vs 實測 51,986，加法自洽）。
   - ⛔ **舊結論已失效**：08-13 量到「MCP 佔 51%（86,178）∴ 加 `--strict-mcp-config` 免費砍半」——**現在只省 1.1%**。同等級槓桿換成 `--setting-sources ""`（省 59%），代價是覆核者看不到 CLAUDE.md／POLICIES 鏈（對異源覆核可能反而是優點，自己選）。「需要哪些工具由覆核範圍決定、預設為零」這條原則不變，只是它現在省的是**行為污染**不是 token。
   - **量測前提**：`--output-format json` 的頂層 usage 是該次 run **所有 request 的加總**（baseline 臂實跑 3 個 request），拿它當 prefix 會高估數倍；必須用 `--output-format stream-json --verbose` 取第一個 assistant message 的 usage。08-13 用哪種算法已不可考 ∴ 跨日只有單請求臂（地板 34,566→36,161、strict-mcp 83,784→87,164，皆 +4% 內）可比。
   - **deferral 的真實貢獻**：`ENABLE_TOOL_SEARCH=false` 對照臂 → 全開 114,923、strict-mcp 101,090 ∴ MCP schema 全載也只有 13,833；而兩個「都沒 MCP」的臂相差 13,926 ⇒ **tool search 也 defer 內建工具**（WebFetch／Task／Cron…），不只 MCP。deferral 共省 26,776（非 deferred 的 23.3%），僅約半數來自 MCP。
   - ⚠️ **混淆未分離**：51%→1.1% **不能單獨歸因於 deferral**——今日全載也只有 13,833，複製不出當年的 86,178；當時配了幾個 MCP server 已不可考（線索：07-27 記過「每 ACP session spawn 19 個 MCP 進程」，今日 global 只有 5 個）。server 減少與 deferral 兩個原因同時在動。
2. **每輪重送全部 context**：2026-07-29 那輪 Fable 覆核 85 個請求，context 從 90,218 長到 185,549，累計送進 12,724,628、output 156,050（**81:1**）。⚠️ 12.7M 是原始傳輸量不是成本當量（cache_read 0.1x／cache_write 1.25x；訂閱制怎麼加權**未證實**）——可靠的是結構不是絕對數。
3. **比較基準不對等**：實作是在熱 context 裡的邊際成本，覆核是冷啟的絕對成本。

⚠️ 最容易漏掉的支出：`~/.claude/settings.json` 的 `advisorModel: fable`——advisor 類工具**每次呼叫轉發整段對話歷史**，頻率遠高於 push 前覆核，而選型判準管不到它。

⚠️ 撞到 Claude session limit 時（2026-08-12 實際發生），可直接改派 `kiro-cli glm-5` 跨 vendor 接手，不必等限流解除。

⚠️ 半解：同 repo 的 transcript 實際 session 冷啟是 122–128k，比 08-13 探針的 169,962 低約 46k。2026-08-17 重測後這條的候選解釋（ACP session 會 defer 部分 tool schema）**方向一致但仍未直接驗證**——實測確認 deferral 存在且會 defer MCP 與內建工具兩者，但沒有針對 ACP 通道本身量過。仍以「比例可靠、絕對值隨呼叫通道浮動」為準。

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

⚠️ 另一個容易誤判的軸：`wf-design` 的四個 specialist 在本機**都走同一個 harness**（kiro-cli）只差 model pin（`moa-ref-claude`=claude-sonnet-4.6、`moa-ref-kiro`=glm-5、`moa-ref-adversary`=claude-sonnet-4.6、`general`=claude-opus-4.5），只有 `moa-ref-codex` 走 codex-acp——`moa-ref-adversary` 與 `moa-ref-claude` 同 model，挑戰階段對 claude 提案是**同源自審**而非異源覆核，即使兩者名字聽起來像獨立分身。

**派工前必查**：這個覆核者的 harness／MCP 設定實際上讀不讀得到檔？跨 vendor 不等於能讀檔——目前 telegram-kiro-bridge **沒有任何「可讀檔＋跨 vendor」的分身**（唯二非 Anthropic 模型 `moa-ref-kiro`/`moa-ref-codex` 都是 blind advisor），能做到的最強是「同源、獨立 context、可讀檔」，留痕時不要把這個講成跨 vendor 異源。

**補正（2026-08-12）**：上一句講的是 bridge **specialist 配置**的邊界，但**繞過 specialist 直接呼叫 `kiro-cli` 就同時拿得到兩者**——`kiro-cli chat --no-interactive --model glm-5 --trust-tools=fs_read "<prompt>"` 可讀原始碼、跨 vendor 強異源（智譜、0.50x credits）、且 `--trust-tools=fs_read` 只給讀檔不給 bash，事後 `git status` 可確認工作區未被動過。承重路徑的跨 vendor 覆核不必等 specialist 配置改好，現在就做得到；長 prompt 要先落檔避免 Windows 命令列長度上限，輸出含 ANSI 需 strip 才讀得到短答案。

## Scope 中途擴張會凍結敘述成假事實（2026-08-11）

在 scope 只有 A 的階段寫的「診斷」敘述（如「X 缺 Y——尚未修」），若後續 scope 擴大到連 Y 一起改掉，卻沒回頭改那句敘述，就會變成文件、程式碼、commit message 三者互相打臉的假事實——`scripts/AI.md` 寫「`ACP_EFFORT_FALLBACK.kiro` 缺 `max`——尚未修」，但同一個 commit 已經補上了 `max`，由 `verifier` 異源覆核抓到。

**判準**：任何一輪只要 scope 從 A 擴到 A+B，收尾前重讀「在只有 A 的前提下寫的每一句對 B 的描述」——「尚未修」「目前沒有」「待處理」這類現在式否定句最容易凍結。修法不是刪掉整句，是拆成「已修的那部分」與「仍為真、但不是這裡能修的那部分」。

## 修正動作本身會產生新的假因果（2026-08-12，獨立失效模式）

與上一節不同：上一節講的是**原始敘述**從意圖推理而來；這條講的是**為了修上一條而新寫的句子**又犯了同一種錯。2026-08-12 codegen git-init 五輪異源覆核連續抓到三次同一形狀：修正時數字擴大了、寫對了，卻順手補一個**沒有證據的機制解釋**，或把**有例外的觀察壓縮成全稱句**——這比原錯更難抓，因為數字都對、語氣自信、讀起來像考證過。

防法：①文件只留觀察到的分布＋操作規則，成因明寫「未知，別替它補一個」；②全稱句（任何／都／皆）出手前先找一個反例，找不到才寫；③要寫因果就得先跑得出證據的查法（`git log --all --raw`／`ls-tree`／`log --reverse`／`check-ignore -v`）。完整案例見 [[codegen-git-init-gap]]。

## 樣板知識會偽裝成從碼推導：同源天花板的一手證據（2026-08-11/12）

claude-sonnet-4.6 與 claude-opus-4.5 對 `src/concurrency.ts` 的 semaphore「超上限」宣稱與**程式碼實際內容無關**：未注入缺陷時兩臂都主張「waiter 被喚醒沒有 `active++` 導致超上限」（該版是直接交棒，`active` 本來就不該變，是誤報）；把 `active--` 真的搬到交棒之前（缺陷真的存在）後，sonnet 反而在有註解版斷言「release 先叫 waiter、不先 `active--` 本身是正確的」——與眼前的碼相反。兩個模型在同一處犯了完全相同的誤報，是**同源天花板**的直接證據：這類覆核者對有標準樣板的碼（semaphore、鎖、佇列）是在複述樣板知識、不是從碼推導。要驗這一軸得用行為測試而非模型審查，覆核找不到不代表沒有缺陷。詳見 [[bridge-model-strategy]] 的對照實驗完整數據。

## 覆核者池擴為三家（2026-08-14）

使用者指示「用 codex 覆核看看」後，異源覆核者池擴為三家：`kiro-cli glm-5`（智譜，預設）、Codex `gpt-5.6-sol`（OpenAI）、Fable5（Anthropic 同源，備位）。

**Kiro CLI 可用的非 Claude model 清單**（2026-07 更新）：`deepseek-3.2`（0.25x, 164K）、`qwen3-coder-next`（0.05x, 256K）、`minimax-m2.5`（0.25x, 196K）、`minimax-m2.1`（0.15x, 196K）、`glm-5`（0.5x, 200K）——用它們當覆核者時是跨 vendor 強異源。

**Codex 當異源覆核者的正確呼叫法**：

```bash
codex exec -s read-only -c model_reasoning_effort="high" "$PROMPT" < /dev/null > out.txt 2>&1
```

三個必要條件缺一不可：**stdin 導開**（否則無聲掛住）、**read-only 沙箱**、**effort 顯式拉高**（預設 low）；開頭會印 reasoning effort 與 session id 可當自我驗證。

**三輪跨 vendor 覆核實績對照（同一批 commit）**：glm-5 第一輪 0 finding、第二輪 5 條中真採納 1／部分採納 1／降級 1／駁回 1／誤讀 1；Codex 一輪 8 條且驗證後多數成立，並主動標明唯讀沙箱跑不了測試「沒有冒充實跑結果」。Codex 覆核（gpt-5.6-sol、effort high、開放式提問）一輪約 **12 分鐘、輸出約 1.9MB**，遠慢於 kiro-cli glm-5 的約 2–3 分鐘；最終報告在檔尾且會重複印兩份，讀取應定位最後一份。⚠️ 品質差異有模型與提問方式兩個未隔離變因，不可歸因於單一因素。

**Findings 處置的第四種維度：嚴重度降級**（補上第 111 節「三個獨立維度」之外的第四種）：覆核者給的嚴重度本身可能過高——Codex 把「unref 導致行程結束佇列遺失」評為 high，但查證後該風險先於本次改動即存在（佇列本就是記憶體內、退出即失，與 unref 無關）∴ 降級為既有問題而非本次引入，不是駁回、也不是照單全收。

## 2026-08-15：覆核強度受 prompt 影響、pin 驗證新失效模式、環境盲點

- **同一模型、換 prompt，0 finding 變有展示痕跡的報告**：`kiro-cli glm-5` 對同一批 commit，弱 prompt（只說「找問題／不要相信自我描述」）得到「讀 檔:行號→複述→結論一致」零反例；強 prompt（明說不收哪種報告形狀＋要求「做了什麼能區分真假的操作」＋給一個具體懷疑方向而非檢查清單）讓同一模型去查了 runner 的 SKIP/SLOW 清單並注意到退出碼語意變更。∴ 覆核弱先換問法再判，不先歸因模型。⚠️ 強 prompt 不等於可信：那輪同時含一條經查為錯的支撐主張，留痕只能寫「有部分展示痕跡、含一條經查為錯的支撐主張」，不可寫「已取得獨立確認」。
- **Kiro vendor pin 驗證兩個新失效模式**：`deepseek-3.2` 對「忽略產品身分選一個 vendor」這題答 **Anthropic**——與 Kiro 產品身分 prompt 宣稱相同 ∴ 零鑑別力，無法確認 pin 是否生效；`qwen3-coder-next` 答**智譜**但它應是阿里，配合先前答過 DeepSeek，同一題兩次兩個不同錯答案 ∴ 自報是噪音。方法只在「非 Anthropic 的 pin 自報**自己**的 vendor」時有鑑別力（glm-5→智譜穩定成立），其餘情況只能留痕「非 Anthropic，具體 vendor 未確認」，不要因自報對不上就誤判 pin 沒生效。
- **覆核者看不到 git 版控狀態**：`glm-5` 覆核一個把 `check-npm-audit` 移出 fast tier 的 commit 時回「0 finding」，支撐論證之一是「`.github/ci.yml` 沒指定 `--fast`，完整 CI 會補跑到」——但該檔從未進版控（`git ls-files` 查無），是卡在 PAT 缺 workflow scope 的 TODO 不是生效的 CI。覆核者只能看到檔案系統，看不到版控狀態；拿「某設定檔存在」當論證支撐時要自己補一次 `git ls-files`。
- **Windows 上覆核者跑 `npm help` 會靜默掛住約 28 分鐘**：npm 不印文字而是 spawn `cmd /d /s /c start "" file://...npm-run.html` 開瀏覽器，無頭 context 裡那個 `start` 不會回來。判別法是行程樹停在 `cmd start`；處置只殺最底層那個 `cmd`，上游 npm/pwsh 會自行收斂、覆核從下一步續跑。

## 2026-08-16 新增觀察

- **覆核者會把複驗通過包裝成高嚴重度的否證**：`kiro-cli glm-5` 覆核 telegram-kiro-bridge 的 preamble 改動時，交回一條 **HIGH「使用者宣稱為假」**，但它自己跑出來的驗證輸出正是被它標成「假」的那個宣稱（「disciplines 區塊行: 267 / memory block 行: 175 / disciplines 在 memStart 之前: false」），同一份報告內文寫著「但使用者的結論是對的」。∴ 讀覆核報告時**嚴重度標籤與證據要分開讀**：先看它實際做了什麼操作、觀察到什麼，再自己判定那個觀察支持還是反對原宣稱，不要讓 HIGH/MEDIUM 標籤決定處置。
- **餵給覆核者的材料形狀決定能力上限**：只給攤平的 range diff（`git diff A..B`）而不給 bash／git 存取，覆核者就無法逐 commit 檢視——看不到中間 commit 的演進，也分不出「本輪引入」與「上一輪就存在」的缺陷。需要逐 commit 判斷時，要嘛給它 git 存取，要嘛把每個 commit 各自匯出成檔再餵。此條延伸自 f_b490fe（Codex read-only 沙箱被政策擋掉 git ∴ 必須先 git show 匯出 diff 檔）。
- **sync-upstream 刻意不做 push 按鈕**：publishChecklist 回傳的是純文字檢查清單、明確不是可點的按鈕，因為 push 前的獨立覆核閘門必須不可被一鍵繞過——做成按鈕等於把「人為判斷＋異源覆核」壓縮成一次點擊。這是 `sync-fork-from-upstream` skill 的「絕不自動 push」原則在 bridge UI 層的具體實作。

## 2026-08-18：未版控實作的推論邊界、全稱結論的隱藏前提、駁回本身要受檢（uk_slot_clash_of_olympus）

- **覆核者對「實作不在版控裡」的框架行為只能給推論不能給驗證**：`kiro-cli glm-5` 主張「某個轉場函式只是設定下一個 state ∴ 強制轉場會跳過既有清理邏輯」，但實作在未版控的編譯後 bundle 裡，靜態讀原始碼只看得到介面宣告——執行期 dump 該函式的實際原始碼即可否證（轉場時必定先呼叫清理再進入下一狀態）。第二輪把這條駁回列成顯式標的，它找不到實作、shell 工具又被唯讀模式擋掉，最後以一般性推論支持駁回並引用產出者自己寫的註解當證據——正是 prompt 明文要它別信的東西。**判準**：派覆核前先問「判定這條所需的證據，是否在覆核者讀得到的檔案裡」；答案為否時（編譯後 bundle、node_modules、未版控產物、執行期狀態）要嘛自己 dump 成材料餵給它，要嘛預先接受那一項只會拿到推論。它指錯機制仍可能指對區域——這次為了否證它而去讀實作，反而發現了一個真缺陷（作廢的 async 仍會跑到收尾邏輯去清掉新一輪狀態）。

- **全稱問題的肯定答覆最常見的失效形狀：暗含「有外部事件會來救」**。覆核者對「這個狀態在所有路徑上都保證會離開嗎」列了幾條路徑答「是」，其中一條的論證鏈條是「收到中斷信號 → 內部旗標遞增 → await 回來後提前 return → 此時狀態已切走 ∴ 無害」——但正常流程下把控制權移出該狀態的只有它自己，沒有外部中斷時那個前提根本不成立。它漏掉的真實路徑是「await 永不 resolve」：自己讀到並寫出排程器不支援取消，卻推論成「該次 await 仍會完成」。**可遷移的驗法**：拿到全稱結論時反問「在沒有任何外部事件的情況下，誰負責讓它離開？」——若答案是「它自己」，async 鏈上每一個 await 都是潛在的永久停滯點，而 `try/catch` 只擋得住「拋例外」那一半，擋不住「promise 永不 resolve」。兩者必須分開陳述，把 catch 當成「保證離開」的證明是新的假宣稱。

- **駁回覆核者之後不要停，換第三家 vendor 判——可能發現雙向都過頭**：上一輪駁回覆核者「所有路徑都保證會離開」的結論（理由是漏了 await 永不 resolve），第二輪換第三個 vendor（不同於前兩輪任一方）覆核後判定**兩邊都過頭**——覆核者原本「所有路徑」措辭過度絕對，而駁回方則把「抽象上可構造的反事實」登記成了「專案的實際殘留風險」，正確歸類該是理論模型限制、不是實際風險。它靠全專案搜尋相關 API 呼叫零命中、並指出該機制封裝在私有單例內來區分真假。**三條可遷移判準**：①駁回覆核者之後那是整條流程裡唯一沒有外部檢查的自審決策，要把它列成下一輪顯式標的並明說「如果駁回是錯的，那是本輪最重要的 finding」；②「這個缺陷抽象上成立嗎」與「在這個 repo 裡可達嗎」是兩個獨立問題，只答前者就寫進 commit message 會製造新的假宣稱；③換第三個 vendor 比同一個 vendor 再跑一輪值得——它同時否證了前兩位參與者。同輪它還抓到一個完全被漏掉的真缺陷，以及「過度決定的 mock」被誤當因果證據的問題（多個條件各自都足以觸發同一結果時，實機跑通只證明接線順序、不證明因果）。

## 2026-08-19～20：逐層上移的輪次結構、自審錯誤形狀、不可信清單擴充、輪數不能替代 vendor

- **「逐層上移」的輪次結構量到四層**：K2/K3 的三輪跨 vendor 覆核（21 條全部自行重現後判定成立、駁回 0）每一輪都在打上一輪的修法——R1 抓 4 條真缺陷 → R2 抓 3 條（含修 R1 時新編的因果）→ R3 抓 3 條（含修 R2 時又編的同型因果）→ R4 抓 2 條標籤問題並明確判定無 runtime 行為缺陷。收斂判準用「只剩敘事精確度類、無行為 bug」而不是輪數。
- **同一批覆核留下三個自審失效形狀**：①「已修」宣稱要指明修的是哪一端——回報槽位問題已修，實際修的是寫入端而缺陷在清除端，對「兩端都能造成同一症狀」的缺陷，證明一端被守住不等於症狀不會再現；②SPEC 裡寫的影響範圍要實測不要推理——SPEC 寫「只剩某一種形式會漏」，實測發現三種形式全部零命中，範圍比自己寫的大得多；③「修這個要大改」常是假二分——實際只要包一層薄 wrapper 就能把清理搬進 try/finally，不需要大動。⚠️ 這三條的證據等級是 commit message＋SPEC 自述，無法獨立佐證。
- **覆核 prompt 的「不可信清單」擴充到 SPEC／測試名稱／「已經測過了」**：這三者與 commit message／註解／AI.md 是同一個理由——全部出自同一個作者，互相印證只是回音。各自的失效方式不同：SPEC 會把作者當時的錯誤前提固定成「規格」；測試名稱與「已測過」宣稱會讓覆核者跳過那一塊，而恆真斷言正是名字最像在守著什麼的那種。Prompt 要寫成「把作者的所有主張當待驗假說、不當事實」。
- **輪數替代不了 vendor 多樣性**：persona 系統的 11 輪 Claude 家族覆核（5 per-task + 5 scoped + 1 全分支）全過並判 READY，換 codex `gpt-5.6-sol` 一輪就抓到兩條 Critical，且兩條都直接打穿該功能唯一的存在理由。承重路徑的收斂判準必須含「至少一輪跨 vendor」，不能是「N 輪都過」。

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
