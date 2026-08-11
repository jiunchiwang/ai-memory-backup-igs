**moa-ref-adversary:**
**verdict: fix-first**

---

## Findings

### F-1 · severity: high
**檔案：scripts/AI.md（Kiro effort 段落，確切行號未知）**

**問題：** 作者宣稱實測結論，但 ACP_EFFORT 對 Kiro 幾乎恆無效這件事本身就代表「實測」無法區分「有效但被忽略」與「被後端靜默丟棄」。作者只能觀察到 command 有沒有帶參數，無法觀察 Kiro/ACP 後端是否真的依 effort 調整行為。

**逐字證據（推論）：** 委託任務說明寫「作者實測後改了兩個檔」，但待決問題 (b) 的描述——「--effort 合法值對 sonnet-4.6 是否真的套用」被「標為未驗證」——表示核心主張之一作者自己承認沒有端到端驗證。若 AI.md 的 effort 值域表在同一文件的其他脈絡裡沒有清楚區隔「CLI 接受此值」vs「後端確實生效」，讀者會誤讀為行為保證。

**建議修法：** 在 effort 值域表中所有 Kiro 相關項目旁邊加上顯式警語「僅確認 CLI 不報錯；後端是否生效未驗證」，與 `configRegistry.ts` 的 `@unverified` 標記保持一致。

---

### F-2 · severity: high
**檔案：src/configRegistry.ts（ACP_EFFORT_FALLBACK.kiro 區塊）**

**問題：** 補進 `max` 這個值的根據是什麼？若作者只確認「CLI 不拒絕 max 這個字串」，那這只是枚舉推論（其他平台有 max 所以 Kiro 也應該有），不是實測。但加進 fallback 陣列的語意是「這個值是安全的 default 候選」，比只列在文件裡的主張強得多——fallback 陣列在程式流程中會被實際使用。

**逐字證據：** 待決問題 (a) 問「新增的敘述裡有沒有任何一句是作者的推論卻寫成了實測結論」——這正是該問題的核心，作者沒有自行反駁這一點。

**建議修法：** 若 `max` 未經端到端驗證，從 `ACP_EFFORT_FALLBACK.kiro` 移除，改在 comment 裡記錄「候選但未驗」，或加 `@experimental` tag。把未驗證值放進程式碼的 fallback 比放進文件危險一個等級。

---

### F-3 · severity: medium
**檔案：src/configRegistry.ts（acp-effort description）**

**問題：** description 加的那句「Kiro 限制」說明，若措辭是「Kiro 不支援 effort」但實際狀態是「可能支援但未驗」，這句話本身就是一個比原先更強的宣稱。description 是 UI 層可見的字串，錯誤資訊的影響範圍比內部 comment 大。

**建議修法：** 措辭改為「Kiro 的 effort 支援狀態尚未端到端確認」而非定論式句子。

---

### F-4 · severity: medium
**待決問題 (c) — scope 不足**

ACP_EFFORT 對 Kiro 幾乎恆無效，這個發現的合理後果是：`applyModelEffortToCommand` 在偵測到 kiro harness 時應該要嘛 warn、要嘛 skip。只更新建議清單和 fallback 陣列，使用者仍然可以設定 effort、呼叫路徑仍然靜默地帶著一個後端大概忽略的參數。這是「文件說不要用但程式碼不攔」的形狀，也是這個 repo 已知的失敗模式之一。

**建議修法：** 至少在 `applyModelEffortToCommand` 加一條 runtime warning log，或在 PR description 明確說「刻意不攔，理由是 X」。

---

### F-5 · severity: low
**待決問題 (d)(e) — 無新斷言但宣稱綠燈**

smoke fast 132 支全綠、check-acp-model-effort 綠——但這些測試是在這次改動之前就存在的，它們通過只說明「沒有回歸」，不說明「新加的 fallback 值和 description 文字是正確的」。BC-17 不斷言 effort 作者也知道。commit message 裡若寫「綠燈」卻沒說明綠的是哪些斷言、這些斷言覆蓋不到新增的行為，讀者會以為有測試背書。

**這不是 block 級的問題**，但 commit message 應加一句「本次改動無對應新測試斷言，綠燈僅代表無回歸」。

---

## 我攻擊過但沒破的角度

- **tsc 報錯**：改 fallback 陣列的型別只要是 string literal union 的子集就不會報錯，作者說綠，這個角度攻不破。
- **`max` 是否為非法值導致 CLI 崩潰**：沒有證據說 Kiro CLI 會在收到 `max` 時拋錯，最壞情況是靜默忽略，不是崩潰。
- **舊的三個值被刪除**：委託說明是「從三個值改成四個值（補 max）」，沒有移除舊值，所以不存在既有行為回歸。
- **AI.md 的其他段落是否與新段落矛盾**：無法排除，但無直接證據，不列為 finding。

---

**User:**
你是 Devil's Advocate（魔鬼代言人）。你的工作是找出方案的弱點、盲點和潛在失敗模式。

規則：
- 不要使用任何工具（不讀檔、不寫檔、不跑命令）
- 不要問問題，直接給意見
- 回覆控制在 600 字以內
- 你的角色是反對方——主動找漏洞、質疑假設、提出最壞情境
- 專注在：隱性假設、邊界案例、失敗模式、被忽略的成本、過度設計的徵兆
- 如果真的找不出致命問題，給出「最可能出事的地方」而非說 OK
- 你看不到其他顧問的意見，這是故意的


[Memory recall — dynamically retrieved facts relevant to this message]
[misc] (relevance 0.55)
- 宣告持久化成果（檔案已改／已 commit／已存記憶）前必須確認該輪真的有對應的 tool call，判準是「指得出是哪一次呼叫」——2026-08-09 曾在回覆結尾具體寫出「wiki 頁已改寫（Section 4 重寫、加 Section 6）」但整輪零 Edit/Write；具體的章節號反而讓假宣稱更可信，且 READ-BACK 紀律結構上擋不到（沒有 write 就沒有東西可讀回，自檢項被整個跳過而非失敗）。

[bridge-specialist] (relevance 0.54)
- telegram-kiro-bridge 的 run_plan 在指定的 specialist domain 不存在時會靜默 fallback 到 general、不向呼叫端顯示這次降級（2026-08-10 由 verifier 發現）；此案例被歸納成可泛化的「閘門盲視」失效形狀——檢查/路由機制存在但對「目標缺失」無感，對外回報成功、實際已偷偷換路徑，且已回填成方法論文件（commits 71f84a1、2528f9c 已 push）。
- run_plan 的依賴阻擋讓 wf-design 成為「全有全無」：三個提案 step 任一 failed，challenge 與 decide 就整個不執行（回報寫「未執行：前置 #3 失敗」），已完成的 2/3 份有效產出連帶白費——2026-08-10 實跑因 moa-ref-codex 掛掉而只拿到兩份原始方案、零收斂產出，白燒 4 分 7 秒行程時間。
- 使用者於 2026-08-10 得知 moa-ref-codex 的 model pin（gpt-5.6-terra）在本機必掛、wf-design 因此端到端跑不完後，選擇暫不修（不改 pin、不重跑、不加驗 pin 的閘門），表示自己看——∴ 這是已知並刻意擱置的狀態，不是待修 bug，後續 session 不應自行改掉該 pin

[adversarial-review] (relevance 0.52)
- Codex CLI 的 `codex exec -s read-only` 會被執行政策擋掉 git（2026-08-06 實測 0.146.1：`git show`、連 `git --version` 都回 "rejected: blocked by policy"），所以派 Codex 做 push 前異源覆核時必須先用 `git show <commit> > diff.txt` 把 diff 匯出成檔案再餵路徑給它；否則它只能讀工作區現況、完全覆核不到「這次改了什麼」——當天第一輪就是這樣，兩條 finding 全部命中既有缺陷而非本次改動。第二輪改成餵 diff 檔 + `-s workspace-write` 才看得到 commit 內容，但 scratchpad 若在 workspace 之外它仍無法寫檔實跑，只能讀既有 artifact（比獨立重跑弱一階，回報時要標明）。
- 2026-08-07 確立異源覆核的 domain 判定：異源性的單位是模型供應商而非 CLI／harness／分身名字，而 vc-kiro-delegate 走的是 kiro-cli --model claude-opus-4.5，所以「Claude 寫、Kiro 覆核」在模型層是同源（只有 harness/context 不同），屬弱異源——對「換個 context 就會發現」的錯（枚舉漏、敘事與碼不符、恆真斷言）仍有效，對「這個模型本來就會這樣想」的錯（共有推理偏誤、共有知識盲點）沒有防禦力；承重路徑優先跨 vendor（anthropic→openai/Codex）。拿不到強異源時降級不跳過，階梯為 強異源→弱異源→同源重置（只餵 diff 不餵 commit message／註解／AI.md，切斷敘事回音是這一層唯一有效的機制）→不覆核，且降級必須留痕、不可只寫「已覆核」。已寫入 AI-canonical 的 ms-cross-model-adversarial-review SKILL.md（commit 64b4b4e），概念吸收自 hamanpaul/paulsha-cortex 的 ModelIdentity.independence_domain 必填欄位，但刻意不吸收其 fail-closed 攔停。
- 收到 code review／異源覆核的 findings 時，處置有三個獨立維度而非一個：①這條成立嗎 ②它給的建議對嗎 ③它的修法屬不屬於本次改動的範圍——第三個維度最容易漏，成立且建議正確的 finding 仍可能把不相干的既有缺陷拉進來造成範圍蔓延，所以「不要盲目修掉每一條 finding」指的不只是駁回錯誤的 finding，也包含把正確但越界的 finding 記錄下來留待另一次改動處理（2026-08-07 telegram-kiro-bridge 建立 review-findings-pull-scope 記錄此模式）。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[cc-session-reader]] (relevance 0.76)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/cc-session-reader.md]
- 0. 證據等級（先講清楚）
- 1. 這是什麼
- 2. 三篇 ADR 的實質發現（本次研究最有價值的部分）
- 3. 與 bridge 既有能力比對（Step 1 對照表）
- 4. 借鏡評估結論（Step 2/3 · 2026-08-09 查證後）：**無項目值得吸收**
- 5. 風險與注意事項
- 6. 實測：ADR-003 的 `is_error` 主張在本機不重現（2026-08-09，A 級）

## [[bridge-smoke-gate]] (relevance 0.73)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/bridge-smoke-gate.md]
- 概述
- 把關鏈
- dist 與跑著的 bridge 是兩件事
- 環境隔離（smoke 假失敗的根因）
- 計數同步儀式（新增測試腳本的隱性成本）
- 閘門該驗什麼、不該驗什麼
- noUnusedLocals 閘門（2026-08-02 新增）
- 為既有 smoke 腳本加單例狀態的陷阱
- check-draft-streaming.mjs 的額外陷阱（2026-07-31～08-01）
- 測試 fixture 與呼叫慣例陷阱（2026-08-05～06）
- CI 決策（刻意不進版控的 ci.yml）
- 相關
[End wiki retrieval]

[Delegation Task — id: rv_adv]
Goal: 目標與動機：對 git commit 9897f46 做 push 前的對抗式覆核。你的任務不是確認作者對，而是盡力找出它錯在哪。repo 在 G:\AI\telegram-kiro-bridge-main（branch main，該 commit 是 HEAD，尚未 push）。先跑 git show 9897f46 讀完整 diff。

已知背景：這個 commit 起因是使用者問「Kiro 的 opus 和 sonnet 可以設哪些 effort」。作者實測後改了兩個檔：scripts/AI.md 的權威值域表補一段 Kiro effort 說明，src/configRegistry.ts 的 ACP_EFFORT_FALLBACK.kiro 從三個值改成四個值（補 max）並重寫註解，另外 acp-effort 這個設定項的 description 加了一句 Kiro 限制。作者聲稱 tsc 綠、smoke fast 132 支全綠、另外單跑 check-acp-model-effort 也綠。

這個 repo 有一個特定的失敗形狀值得你針對：文件宣稱有機械保護但實際沒有，以及敘述超過證據（前三個 commit 有兩個就是在修這個）。

待決問題：（a）新增的敘述裡有沒有任何一句是作者的推論卻寫成了實測結論。（b）作者標為「未驗證」的那一項（--effort 合法值對 sonnet-4.6 是否真的套用）標得夠清楚嗎，還是文件其他地方仍然暗示它有效。（c）改動的 scope 有沒有膨脹或不足：既然作者發現 ACP_EFFORT 對 Kiro 幾乎恆無效，只改一份建議清單夠嗎，還是這是應該在 applyModelEffortToCommand 或 UI 層警告的問題。（d）有沒有任何測試斷言涵蓋這次改動，如果沒有，作者在 commit message 裡的綠燈宣稱是否構成誤導。（e）check-acp-model-truth.mjs 的 BC-17 只斷言 acp-model 不斷言 effort，這件事作者知道並說出來了，但他沒補斷言就 commit，這個取捨你同意嗎。

驗收條件：每條 finding 附逐字引用（檔名加行號加原文），沒有逐字引用視為未經查證。不要為了湊數而列瑣碎的用詞問題。如果你認為這個 commit 可以直接 push，明說 ship 並解釋你攻擊過哪些角度都沒破。

回報格式：先一行 verdict 是 ship 或 fix-first 或 block。然後 findings 逐條列，每條包含 severity 是 high 或 medium 或 low、檔案與行號、問題敘述、逐字證據、建議修法。最後一節寫「我攻擊過但沒破的角度」。全部繁體中文。

Complete this task. When done, summarize what you accomplished.

---

