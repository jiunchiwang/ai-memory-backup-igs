**User:**
你是盲審顧問。收到問題後只用文字給出你的分析和建議。

規則：
- 不要使用任何工具（不讀檔、不寫檔、不跑命令）
- 不要問問題，直接給意見
- 回覆控制在 600 字以內
- 專注在：可行性、潛在陷阱、實作建議、你會怎麼做
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

[Delegation Task — id: moaplan_plan_kiro]
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

---

**moa-ref-kiro:**
🟠 收到：設計一個機制讓 plan 執行時 specialist domain 落空退回 general 這件事不再靜默失效，最終結果一定會呈現執行者與宣告不符的事實

🟠 打算：以 blind advisor 身分提出一個方案，包含核心取捨、資料流、假設與失效條件

---

## 提案：最終結果強制注入 `_fallback` 欄位

### 1. 核心取捨

**犧牲「結果乾淨度」換取「降級不可隱藏」** — 執行結果物件強制多一個 `_fallback: {declared: string, actual: string}[]` 欄位，正常情況是空陣列，降級時長度 > 0，呼叫端不想看也得收。

### 2. 主要組件與資料流

```
plan-template.json
  └─ steps[].specialist?  // 宣告的 domain（可選）

BridgePlanRunner
  ├─ resolveSpecialist(declared?): Specialist | null
  │    └─ 若 declared 不存在 → 回傳 null，bridge 記錄「fallback 事件」
  │
  ├─ executeStep(step)
  │    ├─ actual = declared ? resolveSpecialist(declared) : null
  │    ├─ if (actual === null) → 用 general 執行，push 到 _fallback 佇列
  │    └─ return {result, _fallback: [...] }
  │
  └─ aggregate(results)
       └─ 合併所有 step 的 _fallback 成最終結果的 _fallback 欄位
```

關鍵點：
- `_fallback` 是 **plan runner 層級** 的結構，不是 specialist 回報的
- 每個 step 執行完就 push 到陣列，最終彙總一定有值
- 舊 plan-template 沒有 `specialist` 欄位 → 不觸發降級邏輯，向後相容

### 3. 我假設了什麼（未查證的前提）

1. **plan 執行結果是 JSON 物件且可自由新增欄位** — 若 ACP 協定嚴格限制結果 schema，這方案就不可行
2. **bridge 知道當下用的是哪個 specialist 實例** — 這點題目已保證（「specialist 自己無法可靠回報」但 bridge 可以）
3. **降級仍是成功路徑** — 題目說「全綠完成」，所以 `_fallback` 不應該是錯誤，只是事實陳述
4. **plan-template 的 `specialist` 欄位是 domain 名稱字串** — 若是其他格式（陣列、物件），解析邏輯要調整

### 4. 這個方案什麼情況下是錯的選擇

1. **呼叫端需要程式化處理降級事件** — `_fallback` 只是事實陳述，沒有錯誤碼或型別標記，不方便寫 `if (result._fallback.length > 0)`
2. **需要細粒度控制每個 step 的降級策略** — 此方案一律退回 general，不支援「某 step 降級就停」或「改用備選 specialist」
3. **結果物件會被下游系統驗證 schema** — 若有嚴格 validator 拒絕額外欄位，這方案會炸

---

補充一句：這個方案的本質是「汙染結果結構來換不可忽略性」。若你更在意結果乾淨，可以改用 log 層級警告，但那就是題目說的「呼叫端要自己去翻 log」，我認為那違反「不依賴呼叫端事後行為」的約束。

---

