# claude-mem 精選寫入紀錄(繁中,供事後抽查)

## 2026-08-07(AUTO 模式;10 筆候選 → 精選 + 去重後寫入 2 條)

呼叫端機械讀到的本批 shortlist header（原樣照登,含亂碼）：
`<<> ?Ｙ?:2026-08-06T20:30:09.133Z;蝑:10(銝? 15);??epoch 1785929047040>>`

檔案自身 header 為「產生:2026-08-06T20:30:09.133Z;筆數:10(上限 15);自 epoch 1785929047040」——時間戳、筆數(10)、epoch 三者與呼叫端 header 一致,**無矛盾**。本批為全新批次,非重掃舊批。

來源 project：`telegram-kiro-bridge-main`（5 筆）+ `uk_872_eyestrike2_client`（4 筆）+ `system32`（1 筆）。

精選階段直接淘汰（一次性過程紀錄,非跨 session 可重用）：

- 候選 1/3（Task 4 / Task 1 之 UK 文件修正任務佇列）：單次任務建立與排序,非知識。
- 候選 5（Adversarial review prompt authored to scratchpad）：單次產出物路徑;做法本身已由 `ms-cross-model-adversarial-review` 既有紀律涵蓋。
- 候選 8（Code review of tween chain lines 628-677 confirms correct）：單次審查通過紀錄。
- 候選 2（Task 3 / GetBuyOdds 的 Client template limit vs Server DB cap）：同屬上述任務佇列紀錄,且 shortlist 自述為 *interpretive documentation additions without code evidence*——未經程式碼查證的解讀,依證據紀律不得寫成 fact。

去重階段淘汰（`list_facts` 命中既有 fact,實質重複）：

- 候選 7（codex adapter 兩套件 deprecated vs maintained）：查「codex-acp」命中既有 fact「Codex 的 ACP adapter 有兩個套件：@zed-industries/codex-acp 已 deprecated…維護中的是 @agentclientprotocol/codex-acp（1.1.9）」,既有版本含 raw probe 實測差異、pin 連動、authMethods 例外 → **既有更豐富**,丟棄。
- 候選 10（CDP attach mode 併入 igs-uof skill）：查「CDP」命中既有兩條 fact——Turnstile 只有接管非自動化瀏覽器能過（含 Playwright 兩臂皆敗實測）,以及「igs-uof 已在 2026-08-06 加入 CDP 接管模式（commit fce516d）」含 antibot 兩種相反處置與不寫 session.json 的理由 → **完全重複**,丟棄。
- 候選 4（SKILL.md 寫「three validation items」但程式實作四項）：查「覆核」/「閘門」命中既有兩條 fact——「異源覆核在文件層自我一致性（數字沒回頭同步、同頁多處寫死計數只改一處）上最有價值」與「計數類文件漂移的機械閘門期望值必須當場從真實來源算出」→ 本次只是同一模式的又一個實例,**實質重複**,丟棄。

實際寫入：

1. （shard `adversarial-review`）使用者的跨模型對抗覆核紀律於 2026-08-06 補上「不要把覆核自動化成無條件停止閘門」一節（寫進 AI-canonical 正本 ms-cross-model-adversarial-review/SKILL.md）,記錄把異源覆核接成 CLI stop-time 自動閘門（如 Codex --enable-review-gate 類）的陷阱——覆核維持人為判斷觸發、不做無條件攔停。
2. （shard `uk-slot-eye-strike`）uk_872_eyestrike2_client 的停輪節奏設計決策（2026-08-06）：每一輪停下後會先短暫停頓,才讓下一輪開始停輪,目的是為特殊符號的進場演出留出播放時間。

結果：**新增 2 條**。未呼叫 forget。

備註：① 覆核紀律那條寫入前確認 `覆核` shard 已有 29 條（成本分級、多輪換 agent、授權回報收斂、advisor 不可取代覆核）,但**無任何一條**談「自動化成無條件閘門」的取捨,故判為新增而非重複。② 停輪那條在 `停輪`(0 筆)/`轉輪`(4 筆)/`eyestrike2`(7 筆) 三個查詢下均無命中。③ shortlist 未提供停頓秒數或類別名,刻意不補寫細節。④ 本紀錄檔前一筆為 2026-08-01,中間 08-03-08-06 期間無 entry——依證據紀律不臆測原因（可能為寫入 0 條時未 append）,僅如實標記此空檔。

## 2026-08-01(AUTO 模式;12 筆候選 → 精選 + 去重後寫入 1 條)

來源 project：`telegram-kiro-bridge-main`（10 筆）+ `uk_917_leprechauns_pots_client`（1 筆）+ 2026-07-30 殘留 2 筆（shortlist 產生時間 2026-07-31T20:30:02.427Z，共 12 筆候選）。

精選階段直接淘汰（一次性過程紀錄，非跨 session 可重用）：

- 候選 4（Ghost Draft Fix Commit Strategy Decision）：內容是「建了一個 ASK action 詢問 F1 回歸測試範圍」→ 單次互動事件。
- 候選 6（User choice point: scope of fixes to apply before push）：單次選擇點。
- 候選 9（Chose status_first approach to fix streaming restart issue）：單次修法選擇；其技術結論已由既有 `status-channel` shard 的 4276f08 fact 涵蓋。

去重階段淘汰（`list_facts` 命中既有 fact，實質重複）：

- 候選 1（probe-* vs check-* 命名慣例）：查「probe」命中既有 fact，已完整記載「smoke runner 用 readdirSync 以 `check-*` 前綴自動發現，有真實副作用的探針刻意命名 `probe-draft-clearing.mjs` 並預設 dry-run、要 `--go`」→ **完全重複**。
- 候選 2+5（Fable5 push 前獨立對抗覆核 / checklist 精煉）：查「Fable」命中 22 條，含 2026-07-30、2026-07-31 的多輪覆核紀律與「檢查清單式 prompt 也能抓到 medium 缺陷」精煉條目 → **完全重複**。
- 候選 3（await gap opens finalize race）：查「await」命中既有 fact「在原本全同步的路徑中插入一個 await 就等於自己開了 finalize/cancel race 縫（2026-07-31 bridge F1 實證）」→ **完全重複**。
- 候選 7（status-channel.ts 零 import 硬約束）：查「status-channel」命中既有 fact，已載明零 import 原因（check-draft-streaming.mjs 單獨 transpile 成 data-URL module 載入）→ **完全重複**。
- 候選 8（順序型承重不變式的契約測試）：查「契約」命中既有 fact「模組契約測試（fake api 記錄 send/edit/delete）＋來源順序斷言＋mutation test 三件套」→ **完全重複**。
- 候選 11（Documentation sync fact-sourcing architecture）：查「Fable」命中既有 fact「doc-facts.ts 從 regex 撕原始碼重構為直接 import TypeScript 模組（COMMAND_SPECS/DEFAULT_STEPS/EVENT_TYPES）」→ **完全重複**。
- 候選 12（Vacuous assertion identification pattern）：查「vacuous assertion」命中既有 fact（含 truncateBotCommandDescription 276 字元實例）→ **完全重複**。

實際寫入（`uk-slot` shard）：

1. UK 老虎機要讓純邏輯能在 Cocos 編輯器外（ts-node）單獨測試，必須把運算層設計成 CC-free 的獨立模組：Game_Define.ts 本身 import 'cc' 與 astarte-framework，任何 import 它的模組在 ts-node 下都載不起來，所以像 bomb 事件結果計算這類純運算應抽成不依賴 cc / Game_Define 的一層（2026-07-31 uk_917_leprechauns_pots_client 實證）。此為可載入性問題，與「tsc --noEmit 要過濾只看 assets/Script 錯誤」的編譯期問題不同。

結果：**新增 1 條**。未呼叫 forget。

備註：本批 12 筆中有 7 筆是**完全重複**，比例明顯高於前幾批——原因是 2026-07-31 的 bridge draft/status race 工作在當下已直接寫入 AIMemory，claude-mem 只是同一批工作的第二次抽取。若此模式延續，可考慮把 shortlist 產生器的起始 epoch 對齊上次 ingest 時間以減少重複候選。

## 2026-07-30(AUTO 模式;4 筆候選 → 精選 + 合併 + 去重後寫入 2 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 產生時間 2026-07-29T20:30:02.527Z，4 筆候選）。

淘汰紀錄：

- 候選 1（Pre-push fact-checking review process for documentation updates）：`list_facts` 查「覆核」命中既有多條 fact——已涵蓋「push 前派獨立 Fable5 agent 審查分支」與「知識萃取類 commit 由 Fable5 對照真實原始碼逐項查證」；本次只是把同一做法套到 docs/roadmap HTML vs wiki 來源 → **實質重複**，丟棄。
- 候選 2（Kiro as primary implementation, Codex as fallback）：`list_facts` 查「委派」命中既有 Claude Max 5x 模型分配策略 fact（≥2k token 實作一律委派 Kiro）→ **實質重複**，丟棄。
- 候選 3+4（ACP adapter model 回報異質性 / model 身分注入架構）：**同主題合併**後寫入 2 條（去重時確認既有 fact 只涵蓋 claude-agent-acp 單一 adapter 的 probe 手法與注入位置，未涵蓋「三 adapter 回報形狀不同」與「實際 vs 請求值分欄保存」）。

實際寫入（皆 `bridge-acp` shard）：

1. 三個 ACP adapter 在 session/new 回報 model 的結構各不相同，因此「這個 session 實際跑什麼 model」的查證邏輯不能寫成單一通用解析——各 adapter 的回報形狀差異已記錄在 bridge 的 acp-model-report-shapes.md，新增或換 adapter 時須先實測其回報形狀再接線（2026-07-29）。
2. 處理「請求的 model 與實際生效的 model 可能不一致」時採用的架構是：AcpClient 用私有 `_sessionConfig` 欄位保存 adapter 回報的實際 model/effort，與呼叫端請求的 `opts.acpModel` 分開存放，讓靜默降級被記成事實而非回音請求值；model 身分注入排在 `initialize()` 之後、preamble 注入之前，因此不違反 preamble 凍結快照政策（2026-07-29）。

結果：**新增 2 條**。未呼叫 forget。

## 2026-07-26(第二批;同日重跑,shortlist 未變 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 產生時間仍是 2026-07-25T20:30:02.611Z，與本日第一批（見下方「## 2026-07-26」條目）完全相同的 2 筆候選——上游 shortlist 自第一批以來未再產生新內容）。

- 候選 1（CI gate via pre-push hook, GitHub Actions deferred）：`list_facts` 查「pre-push hook」命中既有 fact（本日第一批已寫入 `bridge-project` shard）→ **完全重複**，丟棄。
- 候選 2（Claude Max 5x Model Allocation Policy Established）：`list_facts` 查「model-allocation-max5x」命中既有 fact（`bridge-acp` shard 的核心分配策略）→ **完全重複**，丟棄。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-25(第五批;同日重跑,shortlist 未變 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main` + `system32`（shortlist 產生時間仍是 2026-07-22T20:30:24.953Z，與本日第四批完全相同的 2 筆候選——上游 shortlist 自第四批以來未再產生新內容）。

- 候選 1（Secret verification anti-pollution pattern，`telegram-kiro-bridge-main`）：`list_facts` 查「events.jsonl」再次命中同一條既有 fact → **完全重複**，丟棄。
- 候選 2（Memory Curation AUTO Mode Completed: Zero New Facts Ingested，`system32`）：仍是過程性執行紀錄，非架構決策/gotcha/pattern/trade-off → 於選取階段淘汰。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-25(第四批;shortlist 已改版更新,2 筆候選 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main` + `system32`（shortlist 產生時間 2026-07-22T20:30:24.953Z，內容與前三批不同——**上游已重新產生 shortlist**，不再是同一批 3 筆候選卡住不清空的狀況）。

- 候選 1（Secret verification anti-pollution pattern，`telegram-kiro-bridge-main`）：`list_facts` 查「events.jsonl」命中既有 fact（bash 指令逐字記進 events.jsonl → 驗證時字面值 grep 會自我重複污染 → 改用通用正則 `ghp_[A-Za-z0-9]{30,40}`）→ **完全重複**，丟棄。
- 候選 2（Memory Curation AUTO Mode Completed: Zero New Facts Ingested，`system32`）：內容是「上一輪精選跑完、0 條新增」的過程性執行紀錄，非架構決策/gotcha/pattern/trade-off → 於選取階段淘汰。

結果：**新增 0 條**。未呼叫 forget。

附註：先前追蹤的「shortlist 連續 3 輪未清空」問題本輪已不再出現，上游機制看起來已恢復正常清空/重製。

## 2026-07-23(第三批;同一份未清空的 shortlist,3 筆候選 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 檔仍是 2026-07-21T20:30:17 產出的同一批 3 筆候選，未被上游清空/重置，內容與前次 07-22 第二批完全相同）。

- 候選 1（Claude Max 5x Model Allocation Strategy）：`list_facts` 查「Max 5x」命中既有 fact（`bridge-acp` shard）→ **完全重複**，丟棄。
- 候選 2（Secret redaction 必須用正則避免透過 event logging 自我重複污染）：`list_facts` 查「events.jsonl」命中既有 fact（通用正則、自我重複污染迴圈）→ **完全重複**，丟棄。
- 候選 3（AI News Intelligence Pipeline 繁中輸出的主題設定：OpenAI/Anthropic/Gemini/AI models/Coding Agent/MCP/ACP/Data2Story）：屬單一 pipeline 的一次性主題設定快照，非跨 session 可重用之架構決策/pattern/trade-off → 於選取階段淘汰（結論與前次一致）。

結果：**新增 0 條**。未呼叫 forget。

附註（非本任務範圍）：`claude-mem-shortlist.md` 連續第 3 輪未被上游清空，同一批候選重複出現——建議之後找時間查上游產生/清空 shortlist 的機制。

## 2026-07-22(第二批;來源 shortlist 3 筆 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 2026-07-21T20:30 產出，3 筆 decision 候選）。

- 候選 1（Claude Max 5x Model Allocation Strategy，`.claudedocs/model-allocation-max5x.md`）：`list_facts` 查「Max 5x」命中既有 fact，2026-07-21 已寫入 `bridge-acp` shard → **完全重複**，丟棄。
- 候選 2（Secret redaction 必須用正則避免透過 event logging 自我重複污染）：`list_facts` 查「events.jsonl」命中既有 fact（`ghp_[A-Za-z0-9]{30,40}` 通用正則、自我重複污染迴圈），內容完全對應 → **完全重複**，丟棄。
- 候選 3（AI News Intelligence Pipeline 繁中輸出的主題設定：OpenAI/Anthropic/Gemini/AI models/Coding Agent/MCP/ACP/Data2Story）：屬單一 pipeline 的一次性設定快照，非跨 session 可重用之架構決策/pattern/trade-off → 依「丟一次性步驟」規則於選取階段淘汰。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-22(來源 shortlist 1 筆,同一份未清空的 shortlist → 精選後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（同 2026-07-21 那批候選，shortlist 檔自 2026-07-20T20:30:05 起未變動，仍是同一筆 Model allocation strategy 候選）。

- 候選（Model allocation strategy for Claude Max 5x quota optimization）：`list_facts` 查核「Max 5x」「model-allocation-max5x」「Sonnet 級還是 Opus 級」皆命中既有 fact——2026-07-21 已將此候選拆成 2 條寫入（`bridge-acp` shard 的核心分配策略 + `misc` shard 的快速判準/workflow model override 提醒），內容完全對應 → 判定**完全重複**，丟棄。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-21(來源 shortlist 1 筆 → 精選合併後寫入 2 條)

來源 project：`telegram-kiro-bridge-main`（1 筆 2026-07-20 decision：Model allocation strategy for Claude Max 5x quota optimization，產物 `.claudedocs/model-allocation-max5x.md`）。

- 唯一候選為跨 session 可重用的模型分配策略（架構決策 + trade-off + 決策判準），非一次性步驟 → 保留。
- `list_facts` 查核「Claude Max 5x 模型分配」「Kiro 委派 Opus quota」「模型分配」皆無現存 fact，「Kiro」shard 內既有 fact 只涉 specialist-domains.json 個別 model 選擇，與此配額分配策略不重複 → 非重複。
- 依「同主題合併」拆成 2 條耐久知識並 `remember()`：
  > 1.「Claude Max 5x 模型分配策略：Opus 只留給高認知決策、≥2k token 實作委派 Kiro、Haiku 機械操作、Sonnet 協調；配額受全模型週上限 + Sonnet 專屬週上限兩道牆，且跨 Claude.ai/Code/Cowork 共用」（寫入 `bridge-acp` shard）
  > 2.「模型分配快速判準：自問『這錯誤是 Sonnet 級還是 Opus 級』——可重跑錯誤降級委派、會污染下游決策的錯誤才用 Opus；Workflow/subagent 必須顯式指定 model override 否則配額爆掉」（寫入 `misc` shard）

結果：**新增 2 條**。未呼叫 forget。

## 2026-07-20(第二批;來源 shortlist 1 筆 → 精選後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（1 筆 2026-07-19 decision）。

- 唯一候選：Fable5 review 核准 commit `b3eb670` 修正、PUSH-VERDICT: GO，驗證 relay mode 的 relayReplyTo 現會跳過 line 1121 commit 區塊、讓 relayDelegateTokens 送達 line 1279 headless loop。
- 判定：綁定特定 commit hash 與行號（1121、1279）的一次性審查判決，屬過程紀錄，無跨 session 可重用價值 → 依「丟一次性步驟／單檔瑣碎改動」規則丟棄。
- 選取階段即淘汰，故無需去重、無 `remember` 呼叫。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-20(來源 shortlist 5 筆 → 精選合併後寫入 2 條)

來源 project：`telegram-kiro-bridge-main`（5 筆皆 2026-07-17 decision，全屬同一主題：暖機佇列架構的 dev-design workflow 產物，該功能已合併 commit 0149d82）。

- 5 條候選同主題，依「同主題合併」處理：candidate 5（multi-agent design workflow launched wf_ae97cee1）為純過程紀錄 → 丟；candidate 1（judge-panel 判決）+ 2/3/4（三個競爭方案細節）合併為 2 條耐久知識。
- `list_facts` 查核「暖機」「warmup」「coreReady」皆無現存 fact → 非重複，寫入 `bridge-project` shard：
  > 1.「telegram-kiro-bridge 的暖機期訊息處理最終採 MVP-first 方案（warmup.ts：coreReady 旗標 + FIFO 佇列暫存原始 grammy Update，就緒後 replay），judge-panel 72 分勝過 robustness-first 54 / simplicity-first 40，並嫁接後兩者關鍵設計」
  > 2.「暖機佇列可重用 trade-off：fetchReady（runner 已在 poll、訊息不遺失）vs coreReady（訊息→agent 路徑完全安全）是兩個獨立就緒層，長輪詢 bot 有慢速啟動階段時應分開處理」

結果：**新增 2 條**。未呼叫 forget。

## 2026-07-19(來源 shortlist 2 筆，同一份未清空的 shortlist → 精選後寫入 1 條)

來源 project：`telegram-kiro-bridge-main`（同 2026-07-18 那批候選，shortlist 檔自 2026-07-17T20:30:02 起未變動）。

- 候選 1（turn-lint warn-only 策略理由）：`list_facts` 查核仍是重複 → 丟，判定與 2026-07-18 一致。
- 候選 2（獨立 Fable5 review 核可 merge 推送 origin）：**推翻 2026-07-18 的「一次性過程紀錄」判定**。核對 `git log --grep="Fable5"` 發現該做法已在至少 4 個獨立 commit 中出現（`04cc0bc` 訊息明確寫「Fable5 push 前覆核」），確認是跨 session 反覆使用的專案慣例而非單次紀錄 → 改寫為繁中 fact 並 `remember()` 寫入 `bridge-project` shard：
  > 「telegram-kiro-bridge 完成 merge/sync 後、push 到 origin 前，會先派一個獨立的 Claude Fable 5 agent 覆核合併安全性，確認無誤才 push——避免有問題的合併直接推上遠端」

結果：**新增 1 條**。未呼叫 forget。

## 2026-07-18(來源 shortlist 2 筆 → 精選後寫入 0 條)

來源 project:`telegram-kiro-bridge-main`(2 筆,皆 2026-07-17 decision)。

候選:
1. turn-lint warn-only 策略理由(啟發式正則做問句/語言比例判斷)。
2. 獨立 Fable 5 review 核可 merge 推送 origin。

判定:
- 候選 1 **重複**:AIMemory 已存在幾乎逐字對應的既有記憶「telegram-kiro-bridge 的 turn-lint 因為判斷邏輯是啟發式正則(問句/語言比例判斷),容易對 code block、反問句等正常內容產生 false positive,所以選擇只 console.warn 觀察」→ 丟。
- 候選 2 **一次性過程紀錄**:單次 merge 的獨立審查核可 log,非跨 session 可重用決策/做法 → 丟。

結果:**未寫入任何新記憶**。未呼叫 forget。

## 2026-07-17(來源 shortlist 2 筆 → 精選合併後寫入 0 條)

來源 project:`telegram-kiro-bridge-main`(2 筆,皆 2026-07-16 decision,igs-uof 合併同事唯讀設計時保留個人加班單填寫擴充)。

精選:兩筆合併為同一決策(保留 uof_form.py 個人擴充 + 於 DESIGN.md 記載理由),視為同一件事的兩個面向。

去重:以 list_facts 查詢 igs-uof、個人擴充、唯讀,發現 AIMemory 已存在完全對應的既有記憶——「使用者決定 igs-uof 保留原 vc-uof-hours 的加班單 dry-run 填寫功能(uof_form.py),標註為『個人擴充,非公司共享唯讀範圍』——同事的 v2 設計原本已排除寫入操作;若要把 skill 整包分享給同事需重新評估是否移除該檔案」。判定為完全重複,**未寫入任何新記憶**。未呼叫 forget。

## 2026-07-16(來源 shortlist 5 筆 → 精選合併後寫入 2 條)

來源 project:`uk_slot_template`(4 筆,皆 2026-07-15 decision,MaskExpand/board visibility 架構)、`telegram-kiro-bridge-main`(1 筆,2026-07-15 decision)。

1. [合併 shortlist MaskExpand multi-mask / mask expansion revert / SetVisibleSymbolCountOverride 三筆 → shard uk-slot-template] uk_slot_template 專案:MaskExpand 元件需支援多重遮罩(multi-mask),而非僅單一遮罩;此設計曾因疑慮被使用者還原一次,後續於 IMaskExpandHost 介面新增 SetVisibleSymbolCountOverride() 方法(IMaskExpander.ts),用以橋接本地與遠端架構的可見符號數量覆寫機制。
2. [蒸餾 shortlist server-side partial board visibility 一筆 → shard uk-slot-template] uk_slot_template 專案的架構策略:Server 端只送出玩家可見的盤面資料(例如 5x6),而非完整盤面尺寸(例如 7x6),其餘部分由客戶端做前處理。

捨棄:telegram-kiro-bridge-main 的「status 指令合併衝突以 git checkout --theirs 採用上游版本」——屬一次性合併衝突解決紀錄,無跨 session 重用價值。

去重:以 list_facts 對 AIMemory(247 筆)查詢 MaskExpand、board visibility,均無匹配,確認兩條皆為淨新增。未呼叫 forget。

## 2026-07-15(來源 shortlist 15 筆 → 精選合併後寫入 5 條)

來源 project:`uk_slot_template`(9 筆,皆 2026-07-14 decision,mask expansion 整合架構 dev-design workflow)、`telegram-kiro-bridge-main`(6 筆,皆 2026-07-14 decision)。

1. [來源 telegram-kiro-bridge-main → shard misc] 撰寫可攜式 skill 時,若該 skill 會被多個 agent CLI(如 Kiro、Codex、Claude)或多台機器共用,應避免在 SKILL.md 中寫死絕對路徑(例如特定磁碟機代號或使用者目錄),以免跨環境失效。
2. [合併 shortlist ask_user timeout / workspace architecture 兩筆 → shard bridge-project] 為「無長駐行程、僅一次性執行」的 headless CLI agent bridge(如 Telegram-Kiro bridge)設計架構時,不能直接套用長駐 async process 的模式(例如同步阻塞等待回覆、非同步 inbox 消費模型),因為一次性 spawn 無法 await 或暫留對話回合;架構評估應先確認目標執行模型是否相容,再決定是否套用既有模式。
3. [合併 shortlist improvement harness 相關兩筆 → shard bridge-research] 引入結構化錯誤記錄機制(例如帶 fix_applied 欄位的 improvement harness)不一定能提升實際當機診斷能力;若事後檢討發現真正缺口是「紀律」(例如 catch block 中確實記錄錯誤內容),就應該優先補強紀律而非疊加新的基礎設施。
4. [蒸餾 uk_slot_template judge panel 評分紀錄 → shard bridge-research] 在 multi-agent 的 dev-design workflow 中,即使 judge panel 把某提案排名第一,該提案也可能被評為「無法照案直接實作」(例如僅 5.5/10 分),這代表評分結果本身是需要再迭代設計的訊號,不該直接採用第一名方案進入實作。
5. [蒸餾 uk_slot_template adversarial 8 findings 紀錄 → shard bridge-research] dev-design workflow 的 Explore phase 若宣稱「現有程式缺少某項能力」(例如缺少方向感知),該宣稱有可能是錯的(該能力其實透過其他底層邏輯間接實現),因此 adversarial 驗證階段應優先檢查 Explore 階段的假設是否成立,而不是只驗證新提案本身。

捨棄:uk_slot_template 的 mkdir artifacts 目錄建立記錄、workflow 啟動記錄(2筆)、7個 unknowns 清單、以及三個具體設計提案(IMaskExpander/策略介面/外部 controller)——皆為該次 mask expansion 功能的一次性執行細節或遊戲特定實作方案,無跨 session 重用價值;telegram-kiro-bridge 的「specialist knowledge backflow」單純描述問題現象未附解法,暫不收錄。

去重:以 list_facts 對 AIMemory(240 筆)分別查詢 portable skill absolute path、headless bridge async spawn、improvement harness fix_applied、judge panel proposal score、explore phase adversarial verify existing mechanism,五條查詢均無匹配,確認皆為淨新增。未呼叫 forget。

## 2026-07-14(來源 shortlist 6 筆 → 精選合併後寫入 2 條)

來源 project:`telegram-kiro-bridge-main`(6 筆,皆 2026-07-13 decision)。

1. [合併 shortlist #2+#3 → shard bridge-acp] telegram-kiro-bridge 設計跨 backend 量化自評（SELF_EVAL token）機制時，對抗性審查否決了三個複雜方案，發現六個共通致命缺陷,可作為未來設計類似自評/評分機制的通用檢查清單:(1) tsc 型別驗證可被 agent 謊報低分繞過;(2) 觸發條件可能與 Kiro/Codex 等 backend 已知限制互相矛盾;(3) circuit breaker 整合的前提條件未經驗證;(4) 沒有證據顯示 backend 真的會遵守自評指令;(5) 未驗證的實作細節被當成行為契約使用;(6) 巢狀 payload 會破壞既有的扁平欄位慣例。
2. [蒸餾 shortlist #4 → shard bridge-project] 當方法論缺乏量化評分機制(例如沒有「≤95 分即重做」這類邏輯)時,telegram-kiro-bridge 曾設計一套可參考的範本:跨 6 個維度、總分 100 分——型別驗證 V:25、功能測試 T:20、影響分析 I:20、範圍紀律 S:15、完整性 C:10、回讀驗證 R:10。

捨棄:shortlist #1(第二次 dev-review workflow 啟動記錄)、#5(vc-uof-hours skill 對抗驗證審查完成記錄)、#6(P2 實作計畫拆四個任務)——皆為一次性任務執行紀錄,無跨 session 重用價值。

去重:以 list_facts 對 AIMemory(225 筆)查詢 SELF_EVAL、自評、telegram-kiro-bridge、評分機制、circuit breaker,確認兩條皆為淨新增。未呼叫 forget。

## 2026-07-10(來源 shortlist 2 筆 → 精選後寫入 1 條)

來源 project:`telegram-kiro-bridge-main`(2 筆,皆 2026-07-09 decision)。

1. [合併/蒸餾 shortlist #1 → shard uk-slot] 記錄反覆出現的 AI 失誤時，把「常見錯誤」分兩類:流程偏離(Process Deviations,工作流順序失誤,如未先 invoke skill 從步驟0開始、跳過前置 checklist、基準拿錯衍生品)與技術錯誤(Technical Errors,實作層面失誤,如型別/邏輯/命名寫錯);兩類根因與修法不同,分開列並各附 session 實證。此分類法可推廣到任何 skill/knowhow 庫的錯誤紀錄。

捨棄:shortlist #2(Clash of Olympus dev-spec baseline 從 tripleCoinTreasure-client 改為 uk_slot_template + uk-slot-pattern-library)——可重用核心已由既有 fact「uk-slot-spec-to-impl 流程教訓…基準永遠是 uk_slot_template 不是衍生品;步驟2必須讀 pattern-library 索引」完整涵蓋,屬重複;而 Clash of Olympus 該次 spec 修訂本身是一次性專案事件。

去重:寫入前以 list_facts 對 AIMemory(179 筆)掃描 常見錯誤/spec-to-impl/流程偏離/技術錯誤/dev-spec/tripleCoinTreasure/knowhow/錯誤分類——確認兩類錯誤 taxonomy 為淨新增(既有僅記「常見錯誤新增5條流程偏離實證教訓」,未存分類法本身),#2 為重複。未呼叫 forget。

## 2026-07-09(來源 shortlist 6 筆 → 精選後寫入 1 條)

來源 project:`telegram-kiro-bridge-main`(5 筆)、`system32`(1 筆)。

1. [來源 system32,#6 → shard bridge-project] 當 session 的 memory MCP server 未連線(ToolSearch 找不到 list_facts/remember)時,可在 G:\AI\AIMemory\tmp\mcp-call.mjs 自建 stdio JSON-RPC helper 直接 spawn G:\AI\telegram-kiro-bridge-main\dist\mcp-memory.js 呼叫記憶工具——關鍵是 cwd 須設為 bridge 專案根(dotenv 才能載到 .env)、注入 MEMORY_USER_ID 與 MEMORY_DIR=G:\AI\AIMemory,用法 node mcp-call.mjs <toolName> '<jsonArgs>' 或 @argsFile;tmp/ 會被定期清空,helper 不在時照此模式重建即可。

捨棄:#1–#5(Rich Messages PoC 裁決/升級路線/grammY 1.44 支援/@grammyjs/stream append-only 否決/fix 選項執行)——AIMemory 既有 facts 已完整涵蓋(Rich Messages 升級評估、PoC 裁決列 P2、editMessageText 合法 rich 渲染、429 誤解修正、api.raw Proxy 死碼等多條),全屬重複。

去重:寫入前以 list_facts 掃描 mcp-call / mcp-memory / JSON-RPC 等關鍵詞(155 筆),無重複。本次並實際重建了已被清掉的 mcp-call.mjs helper(加上 @argsFile 支援,避免 Git Bash 反斜線跳脫問題)。

## 2026-07-01(來源 shortlist 10 筆 → 精選後寫入 2 條)

來源 project:`telegram-kiro-bridge-main`(Post-Tool Hook 多 agent 設計工作流)。

1. [來源 telegram-kiro-bridge-main,#6 → shard bridge-project] AI 長期警戒模式清單(問題追蹤.md 的 7 條,設計架構師必讀):#001 未查證就宣稱存在、#002 存在 vs 路由混淆、#003 單一來源推斷、#004 忽略字面證據、#005 共享值私有化、#006 行數預算過度樂觀、#007 單一視角自審盲點;可作對抗檢查清單。
2. [來源 telegram-kiro-bridge-main,合併 #5/#7/#8 → shard misc] 可重用多 agent 設計工作流(dev-design)四階段:Explore 查證程式碼 → Propose 3 個競爭方案(常收斂到單一寫入匯流點)→ Adversarial 找致命缺陷評分 → Synthesize 整合最終規格;能在設計初期抓出如多輪迴圈 snapshot 過期(staleness)之類隱性 bug。

捨棄:#1/#2(EyeStrike2 Trail/FlyManager 實作細節)、#3(throwaway-cluster.mjs 一次性驗證腳本)、#4(P1-design-spec.md 產物建立)、#9(工作流啟動 run ID)、#10(NearWin 最小手術選型)皆屬一次性專案實作/過程紀錄,非跨 session 可重用。

去重:寫入前以 list_facts 對 AIMemory(75 筆)掃描 design workflow / adversarial / vigilance / self-review,皆無重複。

## 2026-06-26(來源 shortlist 5 筆 → 精選合併後寫入 1 條)

來源 project:`uk_pirates_queen`(掉落動畫時序重構工作流)。

1. [合併 #3/#4 → shard uk-slot] uk_pirates_queen 掉落動畫凍結視窗回歸:根因為把凍結語意(m_isInDropMode)與掉落動畫 promise(m_dropAllSymbolsOutOfScreenPromise)混為一談、且在 StartSpin(L943)直接觸發掉落;採 MVP 最小手術——拆出 m_isInDropMode 專職凍結、promise 降為純動畫 handle、掉落觸發移到獨立 TriggerDropOut() method。

捨棄:#1(multi-agent review 啟動)、#5(設計工作流啟動 wf_2ff596b5)屬一次性過程紀錄;#2(judge panel 評分 66/58/42)為一次性評選結果,可重用技術核心已併入上條。

去重:寫入前以 list_facts 對 AIMemory(70 筆)掃描 pirates_queen / DropOut / freeze / StartSpin,皆無重複。

## 2026-06-25(來源 shortlist 5 筆 → 精選後寫入 2 條)

來源 project:`uk_pirates_queen`、`uk_872_eyestrike2_client`。

1. [來源 uk_pirates_queen,#1 → shard user-pref] 使用者偏好 git commit 前先確認:執行 commit 之前應多問幾個釐清問題並取得使用者同意,不要逕自 commit。
2. [來源 uk_872_eyestrike2_client,合併 #4/#5 → shard misc] 驗證 TypeScript 介面重構/整併時用 npx tsc --noEmit 做型別檢查;遇 TS6.0 deprecation 警告可加 --ignoreDeprecations 6.0 抑制以聚焦真正錯誤。

捨棄:#2/#3(telegram-kiro-bridge 分支改名 main-old-backup、cherry-pick --skip commit 0610f54)屬一次性 repo 狀態事件,非跨 session 可重用。

去重:寫入前以 list_facts 對 AIMemory(67 筆)掃描;既有「git commit 訊息使用中文」與本次「commit 前先確認」屬不同面向,TS 既有條目為專案/文件性質,皆無重複。


## 2026-06-19(來源 shortlist 15 筆 → 精選合併後寫入 4 條)

來源 project:`10.3.1`(AI 策略)、`uk_pirates_queen`(老虎機)。

1. [來源 10.3.1,合併 #1/#3/#5] 跨模型 AI 策略 v4 核心原則:正典語料庫本身就是產品——以 markdown + git 追蹤的精煉知識為唯一真實來源(G:\AI\AI-canonical),CLI / MCP / bridge / 索引都只是部署基礎設施而非產品本體。
2. [來源 10.3.1,合併 #2/#4] AI 產物雲端 vs 本地儲存政策:正典 skills、steering 政策與通用文件放公開 GitHub repo(AI-canonical);session 執行日誌與框架內部狀態僅保留本地、不進版控。
3. [來源 uk_pirates_queen,#12] 並發 gotcha:在 Promise.all 之前的同步階段計算狀態決策(如 willGhost),會與並發 group dispatch 產生 race condition;應移到 async 階段計算以避免競態。
4. [來源 uk_pirates_queen,合併 #10/#19] Cocos 版面「兩項移除一項」避免置中跳動(snap):用 ghost slot 雙佔位機制,在不改動 Layout 參數前提下同時滿足 0→1 置中、2→1 不跳動與旋轉相容。

捨棄:Wanted Poster 多筆設計規格草稿/方案排名/smoke-test 等一次性過程紀錄(#7–#9、#11、#13–#18);#6 ExtraBet 公版還原屬一次性事件,且「禁改公版」已由 UK conventions 涵蓋。

去重:寫入前以 list_facts 對 AIMemory(53 筆)掃描,皆無重複。

## 2026-06-20(來源 shortlist 1 筆 → 精選後寫入 1 條)

來源 project:`10.3.1`(AI 策略)。

1. [來源 10.3.1] 在 headless(無人值守)Claude 自動化腳本中,用 claude.exe 的 --disallowedTools 參數封鎖 mcp__memory__remember 與 mcp__memory__forget,即可強制走 proposal-only(只提案、不直接寫入記憶)工作流程,避免自動流程擅自改寫長期記憶。

去重:寫入前以 list_facts 對 AIMemory(claude-mem / disallowedTools / headless / daily-claudemem 多關鍵字)掃描,無重複。

## 2026-06-23(來源 shortlist 2 筆 → 精選後寫入 1 條)

來源 project:`uk_872_eyestrike2_client`(老虎機 client)。

1. [來源 uk_872_eyestrike2_client] uk_872_eyestrike2_client 專案架構規範:Spine 動畫一律透過 SpineKit 播放(統一的 Spine 播放架構),不直接操作底層 spine 元件。

捨棄:「Skin assets 指定用於 feature grid 中段過場燈光演出」屬單一專案特定場景的一次性細節,非可重用 pattern。

去重:寫入前以 list_facts 對 AIMemory(Spine / SpineKit 關鍵字,62 筆)掃描,既有 Spine 紀錄皆為 spine-viewer 工具相關,無重複(寫入後 shard=uk-slot.md)。

## 2026-07-07(來源 shortlist 6 筆 → 精選後寫入 3 條)

來源 project:`telegram-kiro-bridge-main`(bridge 專案,2026-07-06 decisions)。

1. [來源 #1] telegram-kiro-bridge 的 skill lint(skill 健康檢查)機制:讀取 G:/AI/AIMemory/config/skill-usage.json 的 use_count 與 last_agent_used_at 使用數據,評估各 skill 是否仍被使用、是否需要淘汰或修整。(shard=bridge-project)
2. [來源 #3] 使用者評估過三模型分工架構提案(Fable 5 當 orchestrator 佔約 10% tokens、Codex 5.5 當 executor 佔約 60%、Gemini 3.1 Pro 當 reviewer 佔約 15%),決定暫緩不採用,避免未來重複提案。(shard=misc)
3. [來源合併 #5/#6] telegram-kiro-bridge 的 gate hook 決策已反轉:專案記憶文件 decision-no-gate-hook.md 改名為 decision-gate-hook-minimal.md,改採最小版 gate hook;CLAUDE.md Section 7 的完整 impact-analysis-guard PreToolUse hooks 維持不部署,此決策文件用於防止未來重複提案。(shard=bridge-acp)

捨棄:#2(Excel→code 三步驟工作流)與既有 f_411e3f(uk-slot-spec-to-impl skill)重複;#4(PARALLEL_DELEGATE >> 截斷 gotcha)與既有 f_3c7a91 重複。

去重:寫入前以 list_facts 對 AIMemory(91 筆;skill-usage / skill lint / orchestrator / Codex 5.5 / gate-hook / impact-analysis 多關鍵字)掃描,皆無重複。

備註:本 session harness 未載入 memory MCP tools(server 未連上),改以 stdio JSON-RPC 直呼同一 mcp-memory.js 的 list_facts / remember tool(同一安全代碼路徑,僅 ADD,未動 forget)。

## 2026-07-08(來源 shortlist 11 筆 → 精選後寫入 2 條)

來源 project:`telegram-kiro-bridge-main`(2026-07-07 decisions;內容涵蓋 bridge 與 uk slot 兩域)。

1. [來源 #9] uk slot 模板專案音訊決策:MG_Bgm 與 FG_Bgm 背景音樂引用在 template 專案中先註解掉(模板不附實際音檔),新遊戲專案需要 BGM 時再解除註解並補上音檔。(shard=misc)
2. [來源 #10] Cocos extensions 目錄採專案隔離架構:棄用 G:/Cocos_Project/extensions 共用目錄,改置於各專案自身的 extensions/(如 uk_917_leprechauns_pots_client/extensions/),避免多專案共用一份 framework 互相干擾。(shard=uk-917)

捨棄(9 筆):#1 token policy 已由既有 fact(token-policy.ts commit 028a5ea 顯式 policy 表 + provenance)以更終態形式涵蓋;#2 park()/onBeforeClose 汙染為中途發現、既有 fact 已記「四條 transcript 儲存路徑皆正常運作」終態;#4 SessionStore 多 session 設計已由「/session 多 session 管理 2026-07-07 結案(5 commits)」涵蓋;#5 /agent 預設 config 已由 /agent init(commit 8613135)兩條 facts 涵蓋;#8 session resume 計畫已有 fact 記錄計畫文件路徑與三層架構;#11 GRAND/MEGA 走標準收分流已由 f_23086a 涵蓋;#3/#6/#7 為一次性過程紀錄(選 workflow、啟動 review、委派 Kiro)不入庫。

去重:寫入前以 list_facts(tail 20/146)+ 直接 grep facts 主檔與 facts_Topic shards(MG_Bgm / extensions / GRAND / MEGA / 917 多關鍵字)掃描,確認 2 條無重複。

備註:本 session harness 同樣未載入 memory MCP tools,沿用 stdio JSON-RPC 直呼 mcp-memory.js 的 list_facts / remember(僅 ADD,未動 forget);server 需以 bridge 專案目錄為 cwd 啟動(否則 .env 的 TELEGRAM_BOT_TOKEN 讀不到)。

## 2026-07-11(來源 shortlist 4 筆 → 精選後寫入 1 條)

來源 project:`telegram-kiro-bridge-main`(2026-07-10 decision)。

1. [來源 #1] telegram-kiro-bridge 的 Rich Message 草稿串流(Path A)採三階段生命週期:先 sendMessageDraft 送空草稿顯示「Thinking…」,再用 sendRichMessageDraft 串流更新草稿內容,最後以 sendRichMessage 定稿;完整規格見 SPEC-draft-streaming.md。(shard=bridge-streaming)

捨棄(3 筆):#2/#3/#4 皆為 2026-07-09 curation session 的去重查詢過程紀錄(「query 回傳 0/179」),屬一次性過程紀錄,不具跨 session 重用價值,不入庫。

去重:寫入前以 list_facts(tail 20/195)雙查詢(draft streaming / sendMessageDraft / Rich Message / 三階段 等關鍵字)確認 0 重複。

備註:本 session harness 同樣未載入 memory MCP tools,沿用 stdio JSON-RPC 直呼 mcp-memory.js 的 list_facts / remember(僅 ADD,未動 forget)。

## 2026-07-12(AUTO)

來源 shortlist:4 筆候選(皆 telegram-kiro-bridge,2026-07-11)。精選後寫入 1 筆,丟棄 3 筆一次性任務建立紀錄(Task #10/#12/#15)。

1. skilllint 於 2026-07-11 將 knowhow-accumulation、non-engineer-agent-design、skill-creator 三個 skill 標記為殭屍(zombie)skill,但經評估後決定保留不刪;日後 skilllint 再標記這三個 skill 時應視為已知豁免,不需重複提案刪除(來源:telegram-kiro-bridge)

## 2026-07-26

來源 shortlist：2 筆候選（產生於 2026-07-25T20:30Z）

寫入 1 條：

- (telegram-kiro-bridge) CI 把關決策（2026-07-25）：測試把關靠本機 pre-push hook 執行，GitHub Actions 暫緩導入；`.github/workflows/ci.yml` 雖已寫好並在本機驗證通過（86/86 測試），但刻意保留為未追蹤檔案不進版控——未來看到該檔案未 commit 屬預期狀態，不是遺漏。→ shard: bridge-project

丟棄 1 條：

- (telegram-kiro-bridge) Claude Max 5x 模型分配政策建立 → 去重丟棄，AIMemory 已有等價 fact（model-allocation-max5x 策略條目）

## 2026-07-27（AUTO）

來源 shortlist：3 筆候選（產生於 2026-07-26T20:30Z，皆 telegram-kiro-bridge）

寫入 2 條（shard: telegram-kiro-bridge）：

- 背景通知 flakiness 於 2026-07-26 經量測推翻 race condition 假設：sleep 縮到 2s、turn 長 31.9s 時通知仍固定在 turn 結束後 +3.0s 才到、未併入該 turn——可重用判準「調延遲後時間差不變就不是競態」，修復方向改從通知投遞路徑下手。
- 2026-07-26 派 Fable 5 subagent 對 commit afb9d8e 做對抗性覆核（37 次工具呼叫、587 秒），抓出「接受 protobufjs 依賴」原始論證的關鍵推理缺陷——印證異源模型對抗覆核可打破同源自審天花板，值得對高風險第三方依賴決策常態化。

丟棄 1 條：

- 「為 self-evaluation 修正建立 feature branch（fix/self-eval-streaming-leak-and-threshold）」→ 一次性流程紀錄，無跨 session 重用價值。

備註：本輪兩條均先以 `list_facts` 查詢（對抗審查／protobufjs／Fable／通知／flaky／競態）確認無既有等價 fact，才寫入；未呼叫 forget。

## 2026-07-28（AUTO）

來源 shortlist：12 筆候選（產生於 2026-07-27T20:30Z，皆 telegram-kiro-bridge-main）

寫入 4 條：

- 2026-07-27 把「異源模型對抗覆核」從高風險依賴決策擴大為常態做法，新驗證兩用途：push 前派獨立 Fable5 審查分支抓出測試斷言過弱；知識萃取 commit（pattern library c4922b3）由 Fable5 對照真實專案原始碼（leprechaunsGoldStreak-client，41 檔約 7800 行）逐項查證。指令須明寫「找缺陷而非讚美」。→ shard: uk-917
- upstream 同步陷阱：redkilin 會選擇性 backport 本 fork 修正但以英文註解重寫並改名識別字，造成「內容等價、文字不同」的 add/add 假衝突；處理原則為比較兩側完整度保留較完整一方（實測本地測試基建較完整，四檔以 git checkout --ours 保留），而非機械沿用固定優先權。→ shard: bridge-upstream-sync
- MCP 繼承最佳化（settingSources 限縮為 ['project'] 或 []，session/new 由 19 行程降到 3）決定暫緩：單純限縮會砍掉 specialist 需要的能力繼承，須先做保留能力前提下的架構設計，不可當純效能參數調整。→ shard: bridge-specialist
- 降低 session 啟動延遲的低風險手段：serena MCP 由 uvx 直接從 git 安裝改為預先 uv tool install 到本機，實測每 session 省約 10-11 秒且零程式碼改動，優先度高於需架構設計的 MCP 繼承限縮。→ shard: misc

丟棄 8 條：

- 「UK 助理 knowledge integration strategy」4 筆（同主題重複紀錄）→ 內容僅止於「使用者建立 UK 助理 specialist 以整合 UK Slot 知識」的規劃階段陳述，無實際決策內容可重用，全數丟棄。
- 「獨立 code review 抓出測試斷言弱點」「pattern library commit 經 Fable5 覆核」「對抗式 review 驗證 merge 正確性」3 筆 → 已合併為上方第 1 條。
- 「以 git checkout --ours 解 add/add 衝突保留本地測試基建」→ 已合併為上方第 2 條。
- 「MCP 繼承最佳化暫緩」原為 2 筆重複 → 已合併為上方第 3 條。

備註：四條均先以 `list_facts` 查詢（對抗／upstream／MCP／serena／backport／uvx／settingSources／UK助理）確認無既有等價 fact 才寫入。既有記憶已含 #007「單一視角自審盲點需異源 skeptic」與 2026-07-26 protobufjs 覆核事件，本次第 1 條保留的是「新增的兩種套用場景 + 指令措辭要求」增量。未呼叫 forget。

## 2026-07-29(來源:telegram-kiro-bridge-main,shortlist 9 筆 → 寫入 2 筆)

- 【bridge-memory】telegram-kiro-bridge 於 2026-07-28 為「UK 助理知識包」定案交付架構:採快照式(snapshot)蒸餾檔案 + headless agent CLI 直接讀取,刻意不引入向量資料庫與 embedding 層;配套三層把關為敏感資料過濾(禁止公司 raw code 外流)、明確的知識更新工作流、以及交付前驗證。可作為「小規模領域知識問答機器人」的預設架構——RAG 基礎設施的維運成本通常高於快照重生成的成本。
  - 合併自 shortlist 3 筆:snapshot-based delivery、Design Specification、Multi-layer validation strategy
- 【misc】規格驅動開發(SDD)流程的兩個結構性補強(2026-07-28 於 UK 助理知識包專案定案):(1) 以「調查現況」作為 Phase 1 開場——先盤點既有資料來源與載入機制,再進設計,避免憑空假設前提;(2) 在交付使用者審查前插入一道「規格自審」品質閘,機械化檢查未填的佔位符、內部矛盾、範圍蔓延、以及模糊未定義的敘述。此閘擋掉的是「人工審查時最浪費來回的低階瑕疵」,與異源對抗覆核互補而非取代。
  - 合併自 shortlist 2 筆:Quality Gate (Phase 6 spec self-audit)、Phased Approach (Phase 1 survey)

**捨棄 7 筆**:
- Adversarial Verification of Self-Modified Warning Embeddings —— 與既有「異源模型對抗覆核常態化」記憶高度重疊,僅屬同一做法的再一次套用
- UK knowledge pack execution plan read / Progress tracking ledger established —— 一次性執行步驟與進度檔建立,非可重用知識
- Knowledge pack scope excludes five Notion UK categories —— 專案專屬範圍設定,跨 session 無重用價值
- 其餘同主題重複條目已併入上列 2 筆

去重方式:list_facts 查詢 knowledge pack / 知識包 / 向量 / 自審 / 佔位符 / 品質閘 / 敏感資料 / UK 助理,現存 312 筆中除「自審」命中既有對抗覆核系列外無衝突。未呼叫 forget。

## 2026-07-31(來源:telegram-kiro-bridge-main + uk_917_leprechauns_pots_client,shortlist 14 筆 → 寫入 6 筆)

- 【uk-slot】UK 老虎機事件 gate 的重入防護應查下游狀態而非另設旗標:pre-stop gate 是否已執行改用 BombBoard.HasEventBombs() 這類「已註冊結果」查詢判斷,狀態源唯一,unshow/replay 還原時才不會與實際盤面脫節。
  - 來源:Replay prevention mechanism using BombBoard state check
- 【uk-slot】UK 老虎機 unshow/replay 還原的時序保真原則:原始事件的觸發時機必須原樣保留(during-spin 觸發的 BOMB 不可為了實作方便降級成 after-stop),否則還原畫面與原始 spin 表現不一致。
  - 來源:BOMB event timing and adapter contract decisions confirmed
- 【misc】診斷證據必須在 restart/recovery 邊界失效:recovery 之後若沿用 pre-recovery 的 API error 記錄,真正的 post-recovery 卡死會誤用陳舊錯誤當根因而誤診,因此 recovery 時要主動清除舊錯誤證據。
  - 來源:Review recommendation: do not push until MEDIUM bug fixed(該 MEDIUM bug 的本質)
- 【misc】重現 restart 後的視窗溢出/狀態殘留類 bug,最有效的手法是拿真實 transcript 重播(real transcript replay),比造合成輸入更容易踩到真實邊界條件。
  - 來源:Documented window overflow bug discovery and fix in SPEC Progress section
- 【dev-tools】skill bundle 大幅更新的標準流程:先把未提交檔 commit 建立 restore point → 依差異分三類處理(整包替換/回填缺漏/選擇性合併)→ 被取代的舊 skill 轉成 deprecation pointer 並移除其觸發關鍵字避免撞名搶觸發 → 獨立審查通過才 push。
  - 合併自 shortlist 3 筆:Create Restore Point Before Skill Bundle Update、Three-Phase Skill Update Strategy、Complete Update Workflow(Deprecation, Validation, Independent Review)
- 【misc】依賴套件大版本升級的放行閘應是機械驗證而非主觀判斷:先 grep 全部 .ts/.mjs 確認零 import 指向已移除的模組(例如 MCP SDK 的 HTTP/SSE transport),零命中才放行 push。
  - 來源:Independent review cleared MCP SDK upgrade for push with zero blocking issues

**捨棄 8 筆**:
- Fable5 independent review caught documentation inconsistencies after push —— 與既有「`claude -p --model fable` 做一次性獨立審查」記憶重疊,僅屬同一做法的再一次套用
- BOMB event feature design specification completed —— 專案階段性進度紀錄,非可重用知識
- Bomb Event Placement Ignores Underlying Wheel —— 單一遊戲的機制細節,跨專案無重用價值
- Structured 6-phase development workflow established for CLOVER BOMB —— 一次性任務拆解,且既有記憶已含 spec-to-impl/codegen 流程規範
- Restoration work delegated to colleague —— 一次性協作安排
- Dimming effect conditional logic for round-based lighting —— 敘述過於單薄,無法自足成 fact
- 其餘同主題重複條目已併入上列第 5 條

去重方式:list_facts 查詢 bomb / unshow / recovery / skill / deprecation / transcript / 獨立審查 / 升級,現存 335 筆中除「skill」與「獨立審查」命中既有系列(已據此捨棄 Fable5 那筆)外無衝突。未呼叫 forget。

## 2026-08-01(AUTO;同一份未清空的 shortlist 14 筆重掃 → 寫入 0 條)

shortlist 檔頭仍是「產生:2026-07-30T20:30:02.058Z;筆數:14(上限 15);自 epoch 1785321085374」,內容與上方 2026-07-31 那批**逐條相同**——ingest 之後 shortlist 沒有被清空、epoch cursor 也沒前進,所以同一批被重掃一次。

- 14 筆全部命中既有處置:**6 筆已於 2026-07-31 寫入**、**8 筆已判定捨棄**。
- 抽查驗證:以 list_facts 查 `after-stop`,確認「UK 老虎機 unshow/replay 還原的時序保真原則」那條**確實存在於 fact store**(不只記在本 log)。其 shard 是 uk-slot 而非 uk-917,查 uk-917 shard 會漏掉。
- 本輪先獨立精選、後才發現重複,兩輪結論一致:#4(during-spin 時機不可降級)值得存、#5 的 stale pre-recovery evidence 是真 gotcha、#11/#12/#13 應合併成一條 skill bundle 流程、其餘屬一次性紀錄/專案進度。故不改動既有寫入。
- 未呼叫 remember、未呼叫 forget。

⚠️ 待處理(非本輪能修):shortlist 未清空會讓每次 curate 空轉重掃同一批。本檔已有 07-22、07-23、07-25×2、07-26 共 5 次同類紀錄,本次是第 6 次。根治要在**產生端**於 ingest 後清檔或推進 epoch cursor,curate 這一側無法自救。


## 2026-08-02 (claude-mem AUTO)
來源 shortlist: 產生 2026-08-01T20:05:24.319Z, 13 筆, epoch 1785528817871
精選: 1 條（其餘 12 條與既有 fact 重疊或為過程紀錄）

1. telegram-kiro-bridge 的 draft streaming 拒絕採用 grammY stream plugin 的「Plan E」策略（draft 逼近上限時 finalize 再開新 draft 接續），因為 finalize 後舊 draft 仍會「幽靈並存」若干秒——client 在同一 chat 看到兩個 draft 泡泡會導致動畫行為不可預測。選用的方案是頭部凍結：到上限後只顯示尾端 N 字，讓最終訊息帶完整文字。

## 2026-08-03 (claude-mem AUTO;寫入 0 條)

來源 shortlist 檔頭（原文照貼，與 caller 傳入的 header 逐項一致）:
`> 產生:2026-08-02T20:30:08.729Z;筆數:8(上限 15);自 epoch 1785570559110`

**這是全新一批**（epoch 1785570559110 > 上一輪 1785528817871，8 筆內容與 2026-08-02 那批 13 筆不同），**不是同批重掃**。全 8 筆皆為 telegram-kiro-bridge，主題集中在「/dream per-backend model 設定」與「異源對抗覆核」——這兩件事都是同一場 coding session 當下就直接 remember 進 AIMemory 的，因此在 claude-mem observation 這一側原封再出現一次，重疊率高屬預期，非產生端故障。

**8 筆全數捨棄，逐條對應到已存在的 fact：**

1. `Cost-tiered reviewer selection for cross-model adversarial review` → 撞「使用者的異源覆核紀律於 2026-08-02 新增成本分級（寫進 AI-canonical 正本 ms-cross-model-adversarial-review，commit d8d74c6 已 push）：孤兒 import／死碼交給型別系統、敘事比對用 Sonnet 級、只有不變式／論證推理／時序 race 才用 Fable 5」。既有 fact 更完整（含判準與 commit）。
2. `Second adversarial review approved commit 7d4eba8 ... clean context, not trusting commit message claims` → 撞兩條：「異源覆核紀律再擴充（2026-08-02）：第一輪修正產生的新 commit 要再派第二輪、換新 agent 不告知前一輪結論、無 high/medium 即收斂」＋「Fable5 push 前獨立覆核紀律要求它讀原始碼而非信 commit message」。
3. `Adversarial code review completed for commit f986406` → 單次執行紀錄，無可重用內容；其方法論已由第 2 條那組 fact 覆蓋。
4. `Dream models uses per-backend explicit restoration to avoid subprocess churn` → 撞「dream.json models 表選擇『per-backend + 顯式還原』而非 per-step model：三個 ACP adapter 的 model 生效路徑不同——claude 走 session/set_config_option、kiro(--model) 與 codex(-c model=) 綁 CLI 啟動參數，per-step 等於 15 步換 15 次 agent 並打斷 session.buffer 判定」。既有 fact 含機制細節。
5. `Clarified /dream model requirement is per-backend, not provider switching` → 撞「/dream model 需求（2026-08-02 使用者澄清）：要 per-backend 而非 per-step，也不是換 provider；kiro 跑 claude-opus-4.5、claude 跑 sonnet 5、codex 保留條目」。
6. `/dream 工作流模型還原策略三選項（方案 A 顯式還原為推薦）` → 與第 4 條同一決策，既有 fact 已記載最終選定的顯式還原及「不能靠最後一步 restart」的理由。
7. `Multi-Agent Model Assignment 策略：Kiro agent 指定 opus-4.5` → 撞「已建立 G:\AI\AIMemory\config\dream.json，內容只有 models 表 {"claude":"claude-sonnet-5","kiro":"claude-opus-4.5"}，刻意不列 steps」。
8. `Dream per-step model configuration architecture decision pending（ASK id=dreammodel）` → 待決狀態的過程快照，已被第 4／5 條的定案 fact 取代。

去重方式:list_facts 查詢 `adversarial` / `dream` / `覆核` / `commit message`（現存 437 筆）。未呼叫 remember、未呼叫 forget。

## 2026-08-05 (claude-mem AUTO;寫入 1 條)

來源 shortlist 檔頭（原文照貼，與 caller 傳入的 header 逐項一致：時間戳、12 筆／上限 15、epoch 1785665585219）:
`> 產生:2026-08-04T20:30:03.071Z;筆數:12(上限 15);自 epoch 1785665585219`

**這是全新一批**（epoch 1785665585219 > 上一輪 1785570559110，12 筆內容與 2026-08-03 那批 8 筆不同），**不是同批重掃**。專案分布：uk_872_eyestrike2_client 4 筆、telegram-kiro-bridge-main 4 筆、uk_917_leprechauns_pots_client 3 筆、system32 1 筆。

**寫入 1 條：**

1. 防護正則表達式的 catastrophic backtracking 不能靠「檔案與檔案之間的靜態 checkpoint 或靜態 regex guard」——爆炸發生在單一次 test() 呼叫內部、控制權永遠回不到 checkpoint，所以「處理完一個檔案就檢查一次」的 v1 做法在原理上就攔不到；正解是把 regex 執行隔離進 worker 並由外部逾時中止（telegram-kiro-bridge，2026-08-04）。→ shard `bridge-project`

**捨棄 11 筆，逐條說明：**

- `Fifth adversarial review round initiated to validate round-4 fix effectiveness`、`Second-round adversarial review launched targeting fix commit itself for same-pattern errors`、`Adversarial code review initiated with Fable 5 for supply-chain commits` → 三筆合併後撞既有 fact「使用者的 Fable5 push 前覆核紀律已擴充為『可多輪、範圍逐輪收窄』：每修完一輪 finding 就對新 commit 再派一輪範圍限定的覆核，直到只剩敘事精確度類 finding 才收斂 push」＋「第二輪起改派新 agent 並刻意不告知前一輪結論，避免錨定」＋「異源覆核紀律於 2026-08-02 新增成本分級」。既有 fact 更完整（含輪數收斂條件與模型成本判準），三筆均為單次執行紀錄。
- `Respin Column Lock Skip Animation Optimization`（uk_872）→ 專案特定的 Respin 鎖列動畫最佳化，敘述僅到「1-4 列可能有 Cash symbol 鎖住」，無可跨專案重用的判準。
- `PlayFlyEffect序列執行需求明確化`（uk_872）→ 一次性需求澄清（改為依序飛行而非並行）。
- `POT_TO_REEL_TRAIL_INTRO_START_SECONDS set to 0.01`（uk_872）→ 單一常數調值，一次性。
- `Validated slow-crawl speed parameter choice through trade-off analysis`（uk_872，vSlowRatio=0.004）→ 專案特定的動畫參數調校數值，換遊戲即失效。
- `Complete bomb event UI, state machine, and testing plan defined`（uk_917 Task 11）→ 任務進度紀錄。
- `TDD-driven bomb event feature implementation plan established`（uk_917 Task 8）→ 任務進度紀錄；其 TDD 方法論已由既有 skill/fact 覆蓋。
- `Feature branch workflow initialized for bomb event`（uk_917 Task 7）→ 建分支的一次性步驟。
- `Memory curation completed with zero facts written due to live-session overlap`（system32）→ 本 log 2026-08-03 那則的 observation 回聲，屬過程紀錄。

去重方式:list_facts 查詢 `regex` / `backtracking` / `ReDoS` / `worker` / `逾時` / `對抗` / `Fable`（現存 440 筆）。`backtracking`、`ReDoS`、`worker` 三查皆 0 命中，故第 1 條確認為新知識。未呼叫 forget。

## 2026-08-06 (claude-mem AUTO;寫入 2 條)

來源 shortlist 檔頭（原文照貼；caller 傳入的 header 因編碼損毀呈 mojibake，但可判讀的欄位——時間戳 2026-08-05T20:30:04.052Z、筆數 3、上限 15、epoch 1785827290913——與檔案逐項一致）:
`> 產生:2026-08-05T20:30:04.052Z;筆數:3(上限 15);自 epoch 1785827290913`

**這是全新一批**（epoch 1785827290913 > 上一輪 1785665585219，3 筆內容與 2026-08-05 那批 12 筆不同），**不是同批重掃**。專案分布：telegram-kiro-bridge-main 2 筆、uk_872_eyestrike2_client 1 筆。

**寫入 2 條（皆源自候選 3 的底層 gotcha,已讀原始 artifact 取得實據而非由標題推論）：**

1. Node 的 readdirSync withFileTypes 回的 Dirent 不跟隨連結，junction/symlink 一律 isDirectory()===false、isSymbolicLink()===true；skill 投影全靠逐 skill junction,所以 filter(e=>e.isDirectory()) 掃 skill 目錄恆得靜默空集合。refresh-codex-skill-links.mjs 因此壞掉：dry-run 修前 isDirectory()=0/isSymbolicLink()=37 → REMOVE=12 CREATE=0（每跑一次 postinstall 清空一次 Codex），修後 REMOVE=0 KEEP=12 CREATE=25。正解是篩「目錄或指向目錄的 symlink」並 statSync 跟隨確認。→ shard `adversarial-review`
2. 測試 fixture 形狀必須跟生產一致,否則綠燈與「沒驗到」外觀相同：check-codex-skill-links.mjs 用 mkdirSync 建實體目錄當 skill,8 項全綠卻測不到 junction 的 bug；已改成 junction 型 + 實體目錄型各一並做變異測試。→ shard `bridge-smoke-gate`

**捨棄 1 筆:**

- `ACP session management upgrade path defined with capability gating :: load MUST replay history while resume MUST NOT replay`（telegram-kiro-bridge）→ 撞既有 fact 兩條:「ACP 協定規定 session/load 的 Agent MUST 用 session/update 重播整段對話歷史、session/resume 的 Agent MUST NOT 重播,兩者 Request/Response 逐欄同形…」與「acpClient.ts replaying 抑制旗標確定不可刪除,只能 capability-gate 成兩條分支…gate 條件為 agentCapabilities.sessionCapabilities?.resume !== undefined」。既有 fact 更完整（含 claude-agent-acp 0.63.0 原始碼佐證與 gate 判別式）。

**候選 2 判定為專案一次性,未寫入:**

- `Complete investigation confirms four-point integration approach for In_H_FS/In_S_FS animation support :: FREE_GAME_INTRO_EVENT.PLAY 簽章 (totalRound, callback?) 在 FreeGameIntro.ts line 16`（uk_872）→ 綁單一專案單一檔案行號的整合步驟,無跨專案可重用判準。

去重方式:list_facts 查詢 `junction` / `ACP` / `isDirectory` / `Dirent` / `fixture`（現存 459 筆）。`isDirectory`、`Dirent` 兩查皆 0 命中,故寫入兩條確認為新知識；`ACP` 查得 48 筆並命中上述兩條既有 fact。未呼叫 forget。

## 2026-08-06 第二次 (claude-mem AUTO;重掃同批 → 寫入 0 條)

shortlist 仍是同一份未重新產生的檔案（epoch 1785827290913、筆數 3、產生時間 2026-08-05T20:30:04.052Z），與本日第一輪逐欄一致。該批 3 筆已於第一輪全數處置完畢（候選 3 → 寫入 2 條、候選 1 → 撞既有 ACP fact 捨棄、候選 2 → 判定專案一次性）。

**未呼叫 remember、未呼叫 forget。** 判定依據是 shortlist 檔頭的 epoch 與筆數，而非內容比對後重新判斷——同批重掃不需要也不應該再走一次精選。

## 2026-08-06 第三次 (手動補記;寫入 3 條;非 shortlist 來源)

來源不是 claude-mem shortlist（那份仍是同批未重新產生的檔案），而是**當日對話 session 直接產出的知識**——把外部 sheet-to-markdown 的四項設計吸收進 excel-to-ai-doc，並派 Codex 做兩輪異源覆核的過程。使用者明確要求指定 topic 寫入，未走自動分類（避免跨界的第 2 條掉進 misc）。

**寫入 3 條：**

1. Codex `exec -s read-only` 被執行政策擋掉 git（連 `git --version` 都不給跑），派它做 push 前覆核必須先把 diff 匯出成檔案再餵路徑；否則它只能讀工作區現況、覆核不到本次改動。→ shard `adversarial-review`
2. openpyxl 的 `data_only=True` 讀的是 Excel 存檔時的快取值不是公式；無快取的公式格讀成 None，整張公式表會被判空而靜默消失，且若驗證跳過 empty sheet 就會假通過。→ shard `dev-tools`
3. openpyxl 的 `fgColor.rgb` 只在 `type=='rgb'` 時是字串，theme/indexed 兩類只判 rgb 會靜默漏掉；theme 需讀 theme1.xml 且 Excel 索引前兩對與 XML 排列互換，另需套 tint。→ shard `dev-tools`

去重方式：`list_facts` 查 `openpyxl` / `data_only` / `read-only` / `sandbox` 皆 0 命中；`codex exec` 命中 2 條但主題不同（一條講 2026-08-05 未登入、一條講 .system 自我重建）。未呼叫 forget。

**兩點待處理的觀察（未自行修正）：**

- `G:\AI\AIMemory` 底下**沒有 .git**，所以 claude-mem-curate skill 安全段所寫的「所有寫入都進 git-backed 的 AIMemory」不成立。實際復原手段是 `facts-*.md.bak.<timestamp>` 備份（150+ 個）＋ `forget-log.md` ＋ 本 ingest log。抽查與 forget 修正仍可行，但無版本控制歷史。
- 既有 fact「這台機器的 Codex CLI（0.146.0）在 2026-08-05 時未登入…任何端到端驗證都做不了」已與現況不符：2026-08-06 實測 `codex login status` → Logged in using ChatGPT、版本 0.146.1，當日確實跑了兩輪 `codex exec` 覆核。該 fact 的「AGENTS.md 仍未實測」也已被 steering/skill-workflow.md 的 2026-08-06 實測記錄取代。AUTO 流程只 ADD 不 forget，故未動它。

### 追記（同日）：過時 Codex fact 的處置 — 補推翻條，未刪除

使用者核准「forget 掉再寫一條現況」，但 **forget 三次皆 deleted=0**：該 fact 被 wiki 頁 `concepts/ai-strategy.md` 的引用保護（forget 工具回 "protected by wiki references"）。

嘗試過程：先把 wiki 那行的過時說法就地改成現況 → 仍被保護；再移除新文字中殘留的「401 / 未登入」引用字樣 → 仍被保護。判定保護不是鎖在我拿掉的那些字，而是 fact 與該頁的主題重疊（兩邊都在講 Codex / ~/.codex/AGENTS.md / canary 實測）。再往下追等於為了滿足護欄而挖空一頁正當的 wiki，故停止（3 次熔斷）並回報使用者，改採「補一條推翻 fact」。

**實際結果：**
- 舊 fact 保留（自帶 2026-08-05 時間戳，語意上是歷史記錄）。
- 新增 1 條推翻 fact → shard `ai-strategy`，內容含：0.146.1 已認證、AGENTS.md canary 實測通過、以及 app-server 壞掉導致 `codex:setup` 誤報 loggedIn:false（判斷可用性一律以 codex login status 為準）。
- **wiki 的兩次修改保留**：`wiki/concepts/ai-strategy.md` 原本寫「未解，2026-08-05，未登入、端到端驗證做不了」，已改為現況，並新增「仍未解」段落記下 app-server 壞掉與 `codex exec -s read-only` 擋 git 兩件。過時說法因此已從 wiki 層清掉，只剩舊 fact 那一行還舊。
- 三次 forget 嘗試均記入 `forget-log.md`（deleted=0），可追溯。
