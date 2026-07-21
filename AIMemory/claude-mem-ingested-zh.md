# claude-mem 精選寫入紀錄(繁中,供事後抽查)

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
