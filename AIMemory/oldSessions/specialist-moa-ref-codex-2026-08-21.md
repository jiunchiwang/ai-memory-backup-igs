**moa-ref-codex:**


我需要先讀取一手程式碼來理解現有實作，然後提出分析。讓我開始讀取相關檔案。


















## 我的提案

### 一句話核心取捨

**放棄 session 層級的 carve-out，改在 fact 寫入層一次攔截洗乾淨** — 犧牲「/dream 執行時模型看不到人格」這個視覺純粹性，換取大幅簡化架構（移除 personaOverride、maintenanceSession flag、skipArchiveRestore、BC-16 排列組合測試、waitForTurnIdle 等）。

---

### 主要組件與資料流

```
[現況 /dream]
  get() → setPersonaOverride(null) → 建立 maintenanceSession → runWithPersonaCarveOut
    → 執行 dream 步驟 → remember() 寫 fact → exit drop() → clearPersonaOverride()

[我建議的架構]
  get() → 正常使用 session（帶人格）→ 執行 dream 步驟 
    → remember() 改走 writeMaintenanceFacts() → exit（無額外處理）

writeMaintenanceFacts(userId: number, facts: string[]): number {
  // 實作：spawn 一個獨立的 fresh client（無 _meta.systemPrompt）做 fact extraction
  // 或直接用 extractFromTranscript（已存在的 persona-free 路径）
  // 只負責「把傳入的事實寫入」，不解讀、不改寫、不沾人格語氣
}
```

**關鍵差異**：
- `/dream` 仍在同一個 session 跑，模型仍看到人格 → 但寫出的 fact 來自獨立的 extraction client
- 不需要 `maintenanceSession` flag（所有守衛圍繞這個 flag）
- 不需要 `skipArchiveRestore`（不再有「維運 session」的語意）
- 不需要 `personaOverride` Map
- 不需要 `waitForTurnIdle`（不用等使用者 turn 結束）
- 不需要 `runWithPersonaCarveOut` 的 entry/try/finally/exit 骨架

---

### 我假設了什麼

1. **人格對 /dream 的 task execution 沒有實質影響** — dream 執行的步驟是 workflow（dailylog、factlint、wikisync），不是創作。模型用哪種語氣回覆指令不影響這些步驟的正確性。

2. **writeMaintenanceFacts 可以簡單實作** — extractFromSession 裡已經有一條 persona-free 分支（session.personaKey 存在時走 `extractFree`），我假設這條路徑可以抽離出來直接被 remember 呼叫。

3. **現有 extractFromTranscript 是乾淨的** — 這個 function 只吃 session.history 組文字，不涉及 model 互動，理論上與人格無關。

4. **使用者不會在意 /dream 的對話風格** — 如果 dream 用角色腔回覆「正在執行 dailylog...」，這不是產品等級的問題，只是 internal 細節。

5. **archive/working-state 消費不是核心問題** — 即使維運 session 讀了使用者的 working-state，影響範圍有限（只是 context 大一點），不構成「資料污染」。

---

### 什麼情況下會是錯的選擇

- **如果人格真的會影響 /dream 步驟的正確性** — 例如某個人格會讓模型拒絕執行特定維運步驟，或人格的 tool-use 習慣與維運流程衝突。這種情況下，session 層級隔離是必要的。

- **如果未來要擴充「維運視窗禁止派工」** — 現有架構有 `maintenanceWindow` 概念，用來在 /dream 執行期間阻擋其他 specialist 派工。如果需要這個功能，放棄 maintenanceSession flag 之後要在哪裡實作需要重新設計。

- **如果「人格直接寫入 fact」的後果比我想像嚴重** — 我假設了只要 fact 乾淨就沒事，但如果模型在 dream 執行期間因為人格而產生其他副作用（寫檔、tool call、狀態變更），那些也會帶人格。現有架構的 carve-out 把整個 session 換掉，就是為了杜絕所有這類隱性副作用。

- **如果 close-time extraction 的頻率很高** — 每個 session close 都會觸發 extractFromSession。如果都要走獨立 client，會增加 spawn 成本。現有架構的 maintenanceSession flag 在 extractFromSession 入口擋掉這個開銷。

---

### 誠實邊界

- 我**沒有**實測 `extractFree` 路徑是否真的不吃人格（只是 code review 顯示它不帶 _meta）
- 我**沒有**驗證 writeMaintenanceFacts 的實作複雜度（抽離 / 測試覆蓋）
- 我**沒有**看 maintenanceWindow 的完整實作，如果它依賴 maintenanceSession flag，取消這個 flag 可能需要重做

```json
{"type":"artifact","summary":"提出放棄 session 層級人格 carve-out、改在 fact 寫入層一次攔截的簡化方案。核心取捨：犧牲 /dream 執行時模型不見人格的純粹性，換取移除 personaOverride、maintenanceSession、skipArchiveRestore、waitForTurnIdle、BC-16 測試等大量複雜度。","outputs":[{"type":"recommendation","content":"用 writeMaintenanceFacts() 取代 /dream 的 remember() 呼叫，該函式內部 spawn 獨立 client（走 extractFromTranscript）寫事實，不經帶人格的 session"}],"files_modified":[],"tags":["moaplan","persona","dream","simplification"]}
```

---

**User:**
<identity>
你是 moa-ref-codex，MoA blind advisor (Codex/OpenAI)。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Memory recall — dynamically retrieved facts relevant to this message]
[verification-diagnosis] (relevance 0.62)
- **時序窗口從外部控制不到時，正解是把斷言縮小到「這個時序下真的驗得到」的性質，並在註解寫死誠實邊界，另找一條決定性時序的測試補回被放掉的性質**——2026-08-20 telegram-kiro-bridge 的 BC-24 逐字實例（scripts/check-persona.mjs:784-804）。情境：`get()` 的 `existing` 與 `pending` 兩個早退分支都只看 chatId、把本次傳入的 opts 整個丟掉，∴ 維運流程（/dream，全是 remember() 寫入者）會拿到一個為使用者互動而建、帶著人格的 session。BC-24 要驗的是 in-flight create 分支（create() 在 provider.initialize() 完成前不會 sessions.set() ⇒ 這個窗口內維運的進場 drop() 會 no-op，而背景 poller 會 fire-and-forget 對同一個 owner chat 建 session）。**關鍵取捨**：這條**刻意不驗人格**，只驗「維運意圖不被 pending 去重吃掉」（拿到的不是同一個 session／是維運 session／被取代的那個真的關掉了）——理由逐字寫在註解：in-flight create 何時讀到 personaOverride 那個讀取點在 create() 內部好幾個 await 之後、無法從外部控制，**若在這裡把 override 翻成 null，有可能連 in-flight 那個也變成無人格 ⇒ 兩邊都乾淨、斷言恆綠而什麼都沒驗**；「維運 session 是乾淨的」改由 BC-23 用決定性時序負責。另兩個可遷移細節：①這類測試要靠**同一個微任務內必然發生的註冊順序**取得決定性（第一個 get() 會在同一個微任務內把 pending 註冊進 creating）而不是靠 sleep；②順手多驗一項 `client.isClosed` 防子行程洩漏——舊碼是兩個 session 同時活著、exit handler 的身份比對恆 false。∴ 判準：縮小斷言範圍的正當理由是「不縮小會恆綠」，不是「不縮小會 flaky」；縮小之後必須指名哪一條測試接手了被放掉的性質。
- **「純函式斷言全綠」完全不代表 production call site 有接線**——2026-08-20 telegram-kiro-bridge 第一手（commit b0dc46b 的 Critical 1，異源覆核者示範三個一行 no-op 全部 tsc 乾淨且閘門 1/1 passed）：覆核者把 sessionManager.ts:1182 的 `systemPromptAppend,` 改成 `systemPromptAppend: undefined,`、拿掉 :922 呼叫 createProvider() 的第 6 個參數、刪掉 dream.ts 裡呼叫 `runWithPersonaCarveOut(...)` 的那一行——三者都讓功能永遠不會生效，卻沒有任何斷言碰到，因為既有斷言全是測試檔自己呼叫純函式（buildSessionMeta／buildSessionNewParams），從未經過那些 call site；中間層（src/provider/acp.ts）根本沒有任何 task 打開過，值穿過它靠的是繼承不是決定。**兩種互補補法**：①**真子行程 e2e**（BC-17：spawn 一支 fake ACP agent fixture，用 `FAKE_ACP_RECORD_PATH` 把它實際收到的 session/new・session/load params 落成檔案再回讀斷言）——驗的是真實 wire payload；②**原始碼字面結構斷言**（BC-18：切出 handleDreamBody 的函式邊界，正則驗其中真的出現 `runWithPersonaCarveOut(`），用在「真的跑起來要造出完整 deps 太貴」的 call site，**但必須在斷言訊息與註解裡明寫「結構斷言、非行為驗證」**並標明錨點是原始碼結構（原始碼一改就要更新錨點）。**把 wire payload builder 抽成 exported 純函式（buildSessionNewParams／buildSessionLoadParams，src/acpClient.ts:209/227）的正確定位**：它換掉的是「拿測試自造的複製品物件當被測物」這個更糟的形狀，讓實際送出的 params 組法可直接被驗——但它**不涵蓋**「call site 有沒有把值傳進來」，那一格只有上述①②蓋得到。∴ 抽純函式與驗 call site 是兩件事，做了前者不要以為後者也做了。與 f_d682b4（要求覆核者真的改一個 token 看功能能不能被靜默關掉）互補：那條是覆核者的義務，本條是被覆核方該預先寫好的斷言形狀。
- **只驗「該跳過的跳過了」的 skip 守衛測試組，必須配一條負對照驗「該跑的還在跑」**，否則守衛被寫成恆真時整組照樣全綠而功能無聲死掉——2026-08-20 telegram-kiro-bridge 逐字寫在 scripts/check-persona.mjs 的 BC-22 註解裡（「BC-22 是負對照且不可省：BC-20/21 只驗該跳過的跳過了，守衛若被寫成恆真（所有抽取全被跳過），BC-20/21 照樣全綠而 fact 抽取整個死掉、無聲無息」）。具體形狀是三條一組：BC-20 帶人格的 session → 不對它的 client 下 prompt、改走 persona-free 抽取器且素材必須是**同一份 transcript**（不是空字串、不是重拼一份）；BC-21 維運 session → 兩條路徑都不走、一筆 fact 都不寫；**BC-22 一般 session（無人格、非維運）→ 必須照舊真的對自己的 client 下 prompt**。缺陷本體同時是「skip 旗標蓋不到的鄰居」的實例（f_88faeb 記的是該追問什麼，本條記該怎麼測）：`drop()` 在 `s.client.close()` 之前無條件跑 `onBeforeClose` → `extractFromSession()` → 用**帶人格的 client** 下 prompt → `appendFactsDedup()` 永久寫進與 remember() 相同的語料層，而 `skipArchive` 只包住排在 onBeforeClose 之前的 archiveOnClose、救不到。另兩條測試設計細節：fake session 的 `buffer` 必須留空（非空會讓 live 路徑真的走到 appendFactsDedup 寫檔）、userId 用一個不存在的值（listFacts 讀不到檔回空陣列，不碰真實語料）——「驗寫入守衛」的測試自己要有不污染生產資料的隔離手段。

[bridge-persona] (relevance 0.60)
- 斷言要打在「實際送出去的那一層」，不是中間值——telegram-kiro-bridge 2026-08-20 的 persona 設計初稿實例（commit 48d0794 逐字更正，⚠️ 此機制本身已於當日被 v4 取代、見 f_5247b2，故以下只取可遷移形狀）：初稿 §3.3 斷定人格文字「串接在 preamble 最尾端」並以此當作「人格能壓過先前指令」的立論基礎，實查 sessionManager.ts:746 卻是 `breakdown.text + workingStateBlock + archiveBlock + dreamStateBlock + relayTaskBlock`，:936 之後還會 append 一段 [Model identity] ⇒ 人格後面還有五段，而其中 archiveBlock 正是切換人格時注入的 handoff（必定出現）。更刺的是原本的 BC-2 斷言打在 `breakdown.text` 上會**恆綠**，而真正送出的是 `session.memoryPreamble`——本 repo 已踩過的「閘門鎖錯層」形狀（pet-connect 那次），綠燈不代表沒事、代表沒驗到。三個可遷移處置：①**修法不是搬位置而是換立論**（需要被壓過的是「指令類」內容——工具說明、[Agent disciplines]、CLAUDE.md 帶進來的紀律，它們全在 breakdown.text 之內或更前面；後面五段是「狀態資料」不含風格或格式指令 ∴ 不競爭）；②**新立論的前提要自己配一道機械斷言**（當時加了一條白名單斷言：:746 之後的區塊集合必須在白名單內，見到未知區塊就紅由人判斷，而不是「檢查有沒有指令」——後者無法機械判定），理由是日後有人加進指令類區塊，症狀會是「角色偶爾變回機器腔」，幾乎不可能被歸因到這裡；③**驗中間值與驗實際送出值不可共用同一個 helper**，否則兩條斷言會一起鎖錯層。⚠️ 該白名單斷言（原編號 BC-9）已隨機制改版一併消失（2026-08-21 實查 check-persona.mjs 只剩 BC-1～BC-33 中無 BC-8/9/10，現存 BC-2 改成驗 `_meta.systemPrompt.append`）∴ 引用本條時引用的是形狀，不是現存閘門。
- **任何「暫時關掉 X → 做事 → 還原 X」的 carve-out 骨架有三個順序缺陷，全部與 try/finally 的邊界有關**（2026-08-20 telegram-kiro-bridge 的 /dream 人格隔離，前兩條由覆核抓出並修於 commit fe6e0ad，第三條修於 b0dc46b，均已逐字查證 src/commands/dream.ts 的 runWithPersonaCarveOut）：①**entry 的副作用不可留在 try 外面**——原碼 setPersonaOverride／進場 drop()／通知使用者三件事都在 try 之前，任一 throw 就讓 finally 永遠不會跑、人格永久卡死且無回復路徑；修法是 setPersonaOverride 後**立即**進 try，把 entry drop 與通知都圈進保護區內；②**finally 內「還原」必須排在「可能失敗的收尾」之前**——原碼 exit drop() 排在 clearPersonaOverride() 前面，drop() 失敗會連帶擋住還原；③**finally 的最後一句若 throw，會蓋掉 try 區塊正常回傳的值（JS finally 語義）**∴ 那一句必須自帶 `.catch()`，本例 exit drop() 加上 `.catch(err => console.error(...))` 並在訊息裡註明「override 已清除，不影響 body 結果」（dream.ts:159-165 逐字）。連帶紀律：carve-out 內所有「通知使用者」的呼叫都要與該檔其餘 ctx.reply 一致地補 `.catch()`，註解逐字寫「通知失敗不得吃掉還原」。測試面：這四種注入失敗（body／notify／entry drop／exit drop）該用排列組合各驗一條（BC-16 系列），並逐一 mutation 確認每條斷言在拿掉對應防護時**精確**變紅且互不誤傷。⚠️ 另一個易漏處：把 entry/try/finally/exit 抽成一個具名函式後，「body 真的有沒有被它包住」是**另一件事**，BC-16 系列全用測試檔自造的假 sessions/notify/body、驗不到接線（見同批的 call-site 斷言那條）。

[bridge-acp] (relevance 0.58)
- **判斷「現在實際跑的是哪個後端／哪個實作」要看真正會送出去的 command line，不要看「使用者有沒有顯式 pin」**——2026-08-20 telegram-kiro-bridge 的 `resolveAcpBackendKind`（src/sessionManager.ts:151）第一手：原 brief 指定直接拿 `backend?.key` 當 backendKey 參數，但**沒有下過 /agent pin 時 backend 是 undefined** ⇒ 該功能（只支援 Claude backend 的人格注入）會在最常見的預設狀態下靜默失效；改成同時吃「pin 定義」與「config.agent.command / args」兩個來源，沒 pin 時退回讀實際命令列。閘門逐字守住這個區分（check-persona.mjs BC-13a「用真正會送出去的 command line 判斷，不是『有沒有 pin』」）：`resolveAcpBackendKind(undefined, "npx claude-agent-acp", [])` 必須回 `"claude"`、`resolveAcpBackendKind({command:"kiro-cli",args:["acp"]}, "npx claude-agent-acp", [])` 必須回 `"kiro"`——後者證明 pin 優先於預設值、前者證明無 pin 不等於無身分。與 f_84dd82／f_f2a212 同屬「**不要把請求端／設定端的值當成實際生效的身分**」家族（那兩條是 model 身分：AcpClient 用私有 _sessionConfig 存 adapter 回報的實際 model，避免靜默降級被記成回音請求值），本條補的是 backend 身分，且失效模式更隱蔽——model 記錯只是顯示錯，backend 判錯是整個功能不啟動而沒有任何徵兆。連帶紀律：同一個判斷（本例 resolvePersonaKey + resolveAcpBackendKind）在多處呼叫時要抽成共用函式，避免兩處判斷漂移（sessionManager.ts:744 註解逐字）。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[deepseek-harness]] (relevance 0.82)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/deepseek-harness.md]
- 0. 這一輪為什麼要重看（前一份報告的證據等級被高估）
- 1. 基礎事實（A 級 · GitHub API 原始欄位）
- 2. 源碼層盤點（A 級 · contents API）
- 3. `packages/acp` —— 本輪核心，判定：**不可用**
- 4. `compaction` / `spill` 深入（2026-08-18 追查 · **更正本頁初版**）
- 5. 借鏡結論
- 6. 證據等級
- 相關

## [[kkterm]] (relevance 0.82)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/kkterm.md]
- 0. 證據等級
- 1. 這是什麼
- 2. 四條有實質內容的交集軸
- 3. Step 1 比對表
- 4. Step 2 借鏡排序
- 5. 誠實邊界（尚未做的事）
[End wiki retrieval]

[Delegation Task — id: moaplan_plan_codex]
Goal: 設計問題：目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dream 與 close-time fact extraction 都可能將人格語氣寫入長期記憶，因此 Stage 1 加入 persona override、維運 session、archive/working-state 跳過、maintenanceSession、退出路徑守衛、並發封鎖與維運視窗禁止委派/代理。使用者質疑為何做很久、是否有更簡單方案。
約束：請讀 repo 一手實作：src/sessionManager.ts、src/commands/dream.ts、src/acpClient.ts、src/session-extract.ts、scripts/check-persona.mjs。比較：(A) 現有完整 session carve-out；(B) 資料層人格清洗或獨立 extraction client；(C) 人格限制為呈現層/互動回覆。核心不可接受後果：人格語氣或維運內容錯誤寫入 facts，維運消費或覆蓋使用者 archive/working-state。不可把註解、SPEC 或測試名稱當證據。產出繁中、結論先行，標示一手程式碼證據與推論邊界，指出架構必然/驗證累積/範圍漂移，給最小可交付範圍與推薦；只分析不改檔。

請提出**一個**你認為最好的方案。你是三個獨立提案者之一，彼此看不到對方的方案——所以不要試圖折衷或預留空間，就提出你真正認為對的那個。

必須包含：
1. 一句話的核心取捨（你選擇犧牲什麼換什麼）。
2. 主要組件與資料流。
3. **你假設了什麼**——特別是你沒有查證、但方案成立所依賴的前提。
4. 這個方案什麼情況下會是錯的選擇（誠實寫，不要寫「幾乎沒有」）。

回報格式：控制在可讀範圍，重點在取捨與假設，不要寫成完整實作細節。
Context: 此工項屬於計畫「檢視 Telegram bridge 人格系統 Stage 1 為何複雜，提出更簡單且可交付的替代架構。」。

Complete this task. When done, summarize what you accomplished.

---

