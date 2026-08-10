**moa-ref-claude:**
## 方案：Bridge 端執行紀錄 + 整合步驟強制注入

### 核心取捨
犧牲整合 prompt 的乾淨度（強制塞入結構化執行紀錄），換取「降級事實不可迴避地出現在最終輸出」。

---

### 主要組件與資料流

**1. StepExecutionRecord（新增型別）**
```ts
type StepExecutionRecord = {
  stepId: string
  declaredDomain: string      // plan-template 裡寫的
  actualDomain: string        // bridge 實際派給哪個 specialist
  degraded: boolean           // actualDomain !== declaredDomain
  reason?: string             // 降級原因（specialist 不存在等）
}
```

**2. run_plan 執行層**
每個 step 執行前，bridge 比對 `declaredDomain` 與實際可用 specialist，若不符就填 `degraded: true`，照跑（維持現有行為），但把 record 累積進 `planExecutionContext`。

**3. 整合步驟強制前綴注入**
整合 step 的 prompt 組裝時，若 `records.some(r => r.degraded)`，在 prompt 最前面插入：
```
⚠️ EXECUTION NOTICE（不可省略，必須在整合結果開頭引用）：
下列 step 的執行者與宣告不符：
- step_2: declared=claude, actual=general（specialist 不存在）
整合結果必須包含此段，否則視為不完整輸出。
```

這樣整合者（也是 LLM）被明確指示要把這段帶入輸出，呼叫端拿到的最終文字裡一定看得到。

---

### 假設

1. **整合 step 是 LLM 執行**——方案靠 prompt 指令讓整合者主動引用降級通知。若整合是純程式拼接，可直接前綴，反而更可靠；但若整合者會截斷或改寫 prompt，通知仍可能消失。
2. **bridge 端知道哪些 specialist domain 存在**——run_plan 執行前或執行時可以查到 specialist registry，不需要 specialist 自我回報。
3. **plan-template 的 domain 欄位已經存在或可新增**——若舊模板缺欄位，`declaredDomain` fallback 為 `undefined`，視為「未宣告」而非「降級」，不觸發通知（向後相容）。
4. **整合步驟永遠存在**——若某個 plan 沒有整合 step，注入點不存在，此方案需要額外的回流路徑。

---

### 什麼情況下這是錯的選擇

- **整合 LLM 會忽略或縮寫 prompt 前綴**：這是 prompt injection 式的可見性，不是程式碼層保證。若整合者的 system prompt 有「精簡輸出」指令，通知可能被吃掉。更強的做法是讓 bridge 程式碼在整合結果之後直接 append，完全繞過 LLM 判斷。
- **呼叫端需要的是機器可讀的降級狀態**（非人類可讀文字）：此方案輸出是文字，若下游要做條件判斷，仍需解析。
- **降級很頻繁**：每次都在整合結果塞通知會讓輸出雜訊化，使用者開始忽略它，等同沒有可見性。**完成摘要**：提出了「Bridge 端執行紀錄 + 整合步驟強制 prompt 注入」方案。核心是在 bridge 程式碼層累積 `StepExecutionRecord`，於整合 step 的 prompt 前綴插入不可省略的降級通知，讓最終輸出文字強制帶有執行差異說明。已繳交 structured_output（core_tradeoff、assumptions、wrong_when 三欄）。

---

**User:**
你是盲審顧問。收到問題後只用文字給出你的分析和建議。

規則：
- 不要使用任何工具（不讀檔、不寫檔、不跑命令）
- 不要問問題，直接給意見
- 回覆控制在 600 字以內
- 專注在：風險、替代方案、你覺得有問題的地方
- 如果看不出問題，明確說「此方案看起來 OK」而非硬湊
- 你看不到其他顧問的意見，這是故意的


[Memory recall — dynamically retrieved facts relevant to this message]
[verification-diagnosis] (relevance 0.54)
- 2026-08-07 方法論教訓：GitHub tree API 的 ?recursive=1 回應被截斷時，WebFetch 背後的小模型會對「存在性」問題自信地答 no——當天它連答「無 pyproject.toml／無 paulsha_cortex/／無 tests/」，一度讓我推論出「這個 repo 只有文件沒有程式碼」，足以推翻整份評估。翻案手法是直接打 raw.githubusercontent.com 的檔案 URL 當二元探針（存在→回檔案內容，不存在→404: Not Found），這個訊號不經摘要判斷、抗幻覺；列子目錄改用 git/trees/main:&lt;path&gt;（不遞迴、JSON 夠小不會截斷）也可靠。∴ 對「某某東西不存在」這類否定式主張，永遠要用探針覆核而非採信摘要——這是既有 research-report-citations-unverified 教訓（引用越像真的越要先查）的反向補完。

[misc] (relevance 0.54)
- 宣告持久化成果（檔案已改／已 commit／已存記憶）前必須確認該輪真的有對應的 tool call，判準是「指得出是哪一次呼叫」——2026-08-09 曾在回覆結尾具體寫出「wiki 頁已改寫（Section 4 重寫、加 Section 6）」但整輪零 Edit/Write；具體的章節號反而讓假宣稱更可信，且 READ-BACK 紀律結構上擋不到（沒有 write 就沒有東西可讀回，自檢項被整個跳過而非失敗）。

[adversarial-review] (relevance 0.54)
- 2026-08-07 確立異源覆核的 domain 判定：異源性的單位是模型供應商而非 CLI／harness／分身名字，而 vc-kiro-delegate 走的是 kiro-cli --model claude-opus-4.5，所以「Claude 寫、Kiro 覆核」在模型層是同源（只有 harness/context 不同），屬弱異源——對「換個 context 就會發現」的錯（枚舉漏、敘事與碼不符、恆真斷言）仍有效，對「這個模型本來就會這樣想」的錯（共有推理偏誤、共有知識盲點）沒有防禦力；承重路徑優先跨 vendor（anthropic→openai/Codex）。拿不到強異源時降級不跳過，階梯為 強異源→弱異源→同源重置（只餵 diff 不餵 commit message／註解／AI.md，切斷敘事回音是這一層唯一有效的機制）→不覆核，且降級必須留痕、不可只寫「已覆核」。已寫入 AI-canonical 的 ms-cross-model-adversarial-review SKILL.md（commit 64b4b4e），概念吸收自 hamanpaul/paulsha-cortex 的 ModelIdentity.independence_domain 必填欄位，但刻意不吸收其 fail-closed 攔停。
- 收到 code review／異源覆核的 findings 時，處置有三個獨立維度而非一個：①這條成立嗎 ②它給的建議對嗎 ③它的修法屬不屬於本次改動的範圍——第三個維度最容易漏，成立且建議正確的 finding 仍可能把不相干的既有缺陷拉進來造成範圍蔓延，所以「不要盲目修掉每一條 finding」指的不只是駁回錯誤的 finding，也包含把正確但越界的 finding 記錄下來留待另一次改動處理（2026-08-07 telegram-kiro-bridge 建立 review-findings-pull-scope 記錄此模式）。
- ms-cross-model-adversarial-review skill 的覆核者選型已於 2026-08-07 重寫為單表雙軸結構（commit a8e3725 已 push 到 jiunchiwang/ai-canonical）：原本 domain 與 tier 分成兩張表（Q1/Q2），因跨 vendor 覆核連兩輪抓到「兩張表分類軸對不齊」而判定是結構問題非標籤問題，改為一張三欄表（預期的 finding 類型 | domain | tier），「承重路徑」降為前四列（不變式／論證推理缺陷／時序 race／跨模組契約）的合稱而非表中一列；節標題同步改為「domain 與 tier 是兩個獨立的軸」
- 異源覆核收到的 findings 有第三種處置（除了採納與駁回）：「指的位置對、但建議是錯的」——2026-08-07 實測第三輪 glm-5 建議把表格標頭括號拿掉，照做會讓第一輪的 finding 原地復活，但它指出的接縫是真的；若照單全收會在兩個 finding 間來回，若因建議不對就整條駁回則會錯過「連兩輪打在同一個接縫＝結構問題不是措辭問題」這個訊號
- kiro-cli 自己的預設 model 是 auto 不是 claude-opus-4.5（--list-models 輸出的 * 標在 auto，說明為「Models chosen by task」且不回報實際挑選結果）：不帶 --model 呼叫 Kiro 當覆核者時 domain 不可知，比同源更糟——連「本輪為弱異源」這種降級留痕都寫不出來，所以當覆核者用時一律顯式帶 --model。注意 vc-kiro-delegate 寫死的 claude-opus-4.5 與 kiro-cli 本身的預設是兩層不同的「預設」
- Node 的 readdirSync(dir,{withFileTypes:true}) 回的 Dirent 不跟隨連結：junction/symlink 一律 isDirectory()===false、isSymbolicLink()===true——而這台機器的 skill 投影全靠逐 skill junction，所以任何 readdirSync(...).filter(e=>e.isDirectory()) 掃 skill 目錄的碼拿到的都是靜默空集合。scripts/refresh-codex-skill-links.mjs 就這樣壞掉且沒人發現：sourceNames 恆空造成①建立邏輯全斷②移除迴圈把既有 link 全判 stale 刪掉，實測 dry-run 修前 isDirectory()=0/isSymbolicLink()=37 → REMOVE=12 CREATE=0（每跑一次 postinstall 清空一次 Codex），修後 REMOVE=0 KEEP=12 CREATE=25。正確寫法是篩「目錄或指向目錄的 symlink」並用 statSync 跟隨連結確認（斷掉的 link 不算來源）。2026-08-04 曾一度靠讀碼推理判成「下次 npm install 會擴成 37 支」方向完全相反，是異源覆核抓到——這類事情要直接寫 dry-run 跑真實環境而非讀碼推理。
- 異源覆核多輪收斂時，若連續兩輪的 finding 落在同一個接縫，應判定為結構問題而非措辭問題並改做結構解，不要繼續修標籤（2026-08-07 實測：兩張表標頭不一致 → 改成一致但內容仍不一致，兩輪都在同一處，最後靠併表才真正消除該類錯誤）
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

## [[bridge-smoke-gate]] (relevance 0.74)
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

[Delegation Task — id: moaplan_plan_claude]
Goal: 設計問題：telegram-kiro-bridge 的 run_plan 目前有一個靜默失效：plan-template 指名的 specialist domain 若不存在，會退回 general 執行，整個 plan 仍全綠完成，呼叫端無從得知「三個獨立模型各出一案」這件事結構上根本沒發生。請設計一個「降級可見性」機制，讓任何 step 的執行者與宣告不符時，這個事實一定會出現在最終整合結果裡，且不依賴呼叫端事後自己去翻 log。
約束：TypeScript，Node.js。階段邊界即 turn 邊界，plan 執行期間無法與呼叫端互動；最終整合是唯一回流通道。不新增外部相依。不改 ACP 協定本身。既有 plan-templates/*.json 是純資料，新增欄位可以但要對舊模板向後相容（缺欄位不得使 plan 失敗）。specialist 自己無法可靠回報自身 model，執行者身分必須由 bridge 端得知。

請提出**一個**你認為最好的方案。你是三個獨立提案者之一，彼此看不到對方的方案——所以不要試圖折衷或預留空間，就提出你真正認為對的那個。

必須包含：
1. 一句話的核心取捨（你選擇犧牲什麼換什麼）。
2. 主要組件與資料流。
3. **你假設了什麼**——特別是你沒有查證、但方案成立所依賴的前提。
4. 這個方案什麼情況下會是錯的選擇（誠實寫，不要寫「幾乎沒有」）。

回報格式：控制在可讀範圍，重點在取捨與假設，不要寫成完整實作細節。
Context: 此工項屬於計畫「測試 wf-design 模板：用一個小型、真實的 bridge 設計題跑完整 5 步 DAG」。

Complete this task. When done, summarize what you accomplished.
[結構化結果 — 必要步驟]
完成後**呼叫 structured_output 工具**繳交下列欄位（不是把 JSON 印在回覆裡，
那樣下一步收不到）：
  - core_tradeoff: string
  - assumptions: array
  - wrong_when: string
文字回覆照常寫（人會看），structured_output 是額外的一步，不是取代。

---

