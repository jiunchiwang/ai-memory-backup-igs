# Wiki Index

> Source of truth: `facts-509424983.md`（master log）
> Wiki 是 derived 綜合層，facts 有衝突時以 facts 為準。

## Pages

- [[uk-slot]] — UK 市場老虎機專案群（1 模板 + 7 遊戲 + 1 demo、codegen 整合、Clash of Olympus、spec-to-impl 教訓、回灌工作流、錯誤分類法）
- [[uk-slot-template]] — UK Slot 模板專案（三種 FillStrategy、起新專案慣例、回灌工作流、命名規範）
- [[uk-slot-codegen]] — UK Slot Codegen 工具整合（定位 M0a~M1 加速器、anchor merge 限制、驗證結果、回饋修正）
- [[uk-slot-pirates-queen]] — UK Slot 海盜女王專案（6×5 盤面、懸賞令、RTCtrl 凍幀報獎進化版、PascalCase 搜尋陷阱）
- [[uk-917]] — uk_917 3 Leprechaun's Pots（遊戲輪廓、M0a 進度、proto stub、規格確認事項）
- [[uk-slot-clash-olympus]] — Clash of Olympus 諸神之戰（ROW=4/COL=6 4096 Ways、M0b 全綠、VS Feature 規則與編導多輪確認定案、M2.1 完成＋M2.2 資料接線切片完成；2026-08-13 更新）
- [[uk-slot-eye-strike]] — Eye Strike 系列（第一代 uk_658 + 續作 uk_872、7 個專案特有機制、SpineKit 規範、停輪曲線量化分析、baked path 動畫限制、CLAUDE.local.md 覆蓋技巧、型別檢查閘門唯一有效指令是 npm run typecheck＋診斷工具鏈的權威來源順序；2026-08-18 更新）
- [[bridge-project]] — Telegram-Kiro-Bridge 專案（架構、AIMemory、Rich Messages、Reply Context、Smoke 隔離、Specialist Dashboard、Status Server 加固、背景通知 flakiness 診斷判準、Fable5 對抗覆核、claude-mem plugin worker 診斷、Claude Agent SDK 權限模型、heredoc \n 展開陷阱、POLICIES 假宣稱更正、Telegram 出站訊息重複投遞四層修復＋重放安全性三判準、同事接手 repo 用獨立 fork 而非 GitHub Fork 按鈕、grammY transformer 安裝順序更正；2026-08-16 更新）
- [[bridge-acp]] — Bridge ACP 與 Model 配置（adapter 切換差異、/agent 熱切換、model pin、ACP adapter 能力偵測陷阱、AcpBackendDef 語意差異、session/resume 語意分析與能力探測、tool 結果狀態判定鏈與 is_error 可信度實測、Codex/Kiro hooks 能力更正）
- [[adversarial-review]] — 異源對抗覆核紀律（長期警戒模式清單、覆核紀律演化、價值實證時間序、覆核者成本分級、派工前能力軸/blind advisor 幻覺、scope 擴張敘述凍結、樣板知識同源天花板、修正動作本身產生假因果的獨立失效模式、覆核強度受 prompt 影響的受控對照、覆核者看不到 git 版控狀態；2026-08-05 從 bridge-acp 拆出，2026-08-16 更新）
- [[bridge-model-strategy]] — Bridge Model 選型與配額策略（pin 修正史、Kiro model 生態、Kiro effort 值域 per-model 實測、sonnet-4.6[max] vs opus-4.5 對照實驗、advisor 顧問工具與其 token 成本／context 剝除機制、Claude Max 5x 分配策略；2026-08-05 從 bridge-acp 拆出）
- [[bridge-session]] — Bridge Session 生命週期（archive 蒸餾層、ACP resume、/session 多 session、transcript 路徑）
- [[bridge-streaming]] — Bridge Streaming 與訊息渲染（Draft API 三階段 lifecycle、4096 截斷、rate limit、Rich Messages）
- [[bridge-draft-diag]] — Bridge Draft 診斷與重播修復（三個獨立成因、cutPendingTokenTail 扣留式設計、診斷探針、可重用方法論；2026-08-08 從 bridge-streaming 拆出）
- [[bridge-memory]] — Bridge 記憶與維運系統（AIMemory 結構、/dream 14 步維運、factlint 三層防禦、topic 分類、wiki 知識庫、embedding router、備份、判斷 wiki 保護不要自行 Grep 要直接呼叫 forget()、apply_topics token 機制阻塞已修（phase-aware guidance）、skill orphan 涵蓋不到 plugin marketplace、fact ID 完整性與 provenance 稽核缺陷、memory canary gold set 與 latency gate 翻面實測、skill 真孤兒 entry 直接刪不留墓碑、preamble 固定區塊只掛最長 return 的附帶損害型缺陷；2026-08-18 更新）
- [[bridge-dream]] — Bridge Dream 例行維運框架（dream.json models 表 per-backend 設計、claude-mem-curate 接入、turn 誤報根因、confabulation 教訓）
- [[bridge-specialist]] — Bridge Specialist 分身系統（配置、token 執行權限層、PARALLEL_DELEGATE cross-check、Dashboard 監控、run_plan 全有全無設計、moa-ref-codex 已知擱置、moa-ref-kiro/adversary 是 blind advisor 不能覆核、run_plan 能力錯配缺陷已修（wf-review/wf-verify 改派 verifier/moa-ref-security）、委派逾時 per-domain 可設定、extractModel()/maxTurns 已知未修項目；2026-08-15 更新）
- [[bridge-research]] — Bridge 改善研究與 Roadmap（外部框架借鏡、fable-advisor context packaging、claude-plugins-official Permission Relay、PostTool Hooks A→D、Karpathy P0、Rich Messages Draft、spine-animation-ai 自包含 Skill 打包機制）
- [[bridge-upstream-sync]] — Bridge Upstream Fork 同步與合併衝突處理（remote 配置、merge 策略、三種衝突處理原則、同步歷程、push 前異源覆核閘（2026-08-13 起預設 kiro-cli glm-5，非 Fable5）；2026-07-21 從 bridge-project/bridge-acp 拆出）
- [[bridge-roadmap]] — Bridge 開發 Roadmap（Pending / In Progress 追蹤，2026-07-28 建立）
- [[bridge-smoke-gate]] — Bridge 測試閘門與建置（tsc/smoke tier/pre-push 三層、dist≠跑著的碼、環境隔離假失敗、計數同步儀式、probe-* 命名隔離、CI 決策、check-draft-streaming.mjs 測試陷阱三則、smoke 逾時 flaky 診斷與 A/B 類逾時分法、mutate-gate harness 慣例（紅燈行規範／noUnusedLocals 陷阱／無 timeout 風險）、hang detection 門檻侵蝕、fast tier 成本分布偏斜與 SLOW 移出兩條件、canary 的 cleanup 型 suite-only 紅燈、突變步驟自己失敗的 CRLF／轉義兩機制；2026-08-01 從 bridge-project 拆出，2026-08-18 更新）
- [[bridge-doc-sync]] — Bridge 文件同步機制（事實來源改直接 import、計數類機械閘門設計原則、耗時排除在硬閘門外；2026-08-08 新建）
- [[bridge-secrets-backup]] — Bridge 備份與密鑰洩漏防護（acp-trace 洩漏修復、GitHub PAT 洩漏與自我重複污染迴圈、/sharedsync 跨帳號 credential、default-skills 自動回填；2026-08-08 新建）
- [[bridge-infra]] — Bridge 基礎設施（Process 生命週期、start.bat supervisor、暖機 coreReady/FIFO、session.buffer 中途失敗偵測、Impact-Gate Hook；2026-08-08 新建）
- [[bridge-self-eval]] — Bridge 自評與收尾檢查（SELF_EVAL 六個共通致命缺陷檢查清單、/selfeval 決策、Turn-Lint 啟發式 warn-only 設計；2026-08-08 新建）
- [[dev-tools]] — 開發工具與環境設定（Python/Playwright/TypeScript、機器路徑、工作流程、excel-to-ai-document 專案、.env 編輯驗證做法、Git Bash timeout /t 陷阱、skillUsage 權威來源、Markdown 無註解語法導致 ghost @import 仍載入（11,393 tokens）；2026-08-18 更新）
- [[agent-system-architecture]] — Agent 系統五層架構（公司比喻：Agent/MCP/Memory/Workflow/Agent SDK 的角色與關係）
- [[spine-viewer]] — Spine Viewer 插件（Cocos Creator 編輯器擴充，批次掃描 DrawCall/Triangle 效能報告）
- [[ai-strategy]] — 跨模型 AI 策略（正典語料庫架構、投影分發、headless 安全機制、第三方安裝腳本汙染正本風險）
- [[user-pref]] — 使用者偏好與決策風格（ASK 優先、Git 紀律、自動化保守策略、除錯對策）
- [[skill-and-eval]] — Skill 評估與管理（方法論整合、工具評估決策）[歷史頁面，topic 已併入其他分類]
- [[igs-uof]] — IGS-UOF 加班單自動化（原 vc-uof-hours 改名擴充、加班單送出五層防線、刷卡時間 onchange 踩坑、Cloudflare CDP 接管；2026-08-16 provenance 修正）
- [[verification-diagnosis]] — 驗證與診斷方法論（綠燈假象五型與突變測試、診斷實驗三原則、證據的 recovery 邊界、純觀測欄位、await 縫開 race、同源自審天花板、註解洩漏答案、行為測試 vs 模型冷讀判準、防禦性修法第二次被繞過即改驗不變式；2026-08-01 從 misc 拆出，2026-08-18 更新）

## Lessons

- [[uk-slot-pitfalls]] — UK Slot 踩坑經驗（Layout 退場重排、Promise.all race condition、ghost slot 雙佔位）
- [[bridge-pitfalls]] — Telegram-Kiro-Bridge 踩坑經驗（dotenv 繼承、merge 整檔取代、unhandledRejection、draft TTL、grammY Proxy）

## Tasks

- [[skill-candidates]] — 未成熟 Skill 候選追蹤（pattern、count、觀察點）

## Queries

- [[fable]] — Claude Fable 5 修正 Karpathy P0 接線 Bug（7 個問題 + 教訓 + commit）
- [[modelcontextprotocol-typescript-sdk-mcp-typescript-sdk-v-f2c3525b]] — MCP TypeScript SDK v2 beta（套件拆分 server/client、任意 schema 庫、stateless core）
- [[askintel-time-split]] — Intel 排程分割策略（輕量 daily + 重量 podcast 隔天）
- [[trio-model-architecture]] — 三模型協作架構評析（借鏡點、疑點、與 bridge 差異）
- [[embedding-router]] — 為何 doctor 報 Embedding router 未就緒（根因、影響面、解耦修復）
- [[modelcontextprotocol-typescript-sdk-mcp-typescript-sdk-v-a1aded4e]] — MCP TypeScript SDK v2 正式進入 beta（2026-07-28 規範、套件拆分、任意 schema 庫、stateless core）
- [[specialist]] — 什麼情況下會自動使用 specialist（SPECIALIST_PROXY vs PARALLEL_DELEGATE 觸發條件、bridge-dev specialist 不採納理由）
- [[agent-claude-opus46]] — 懸案：`/agent claude` 切回後 model 仍是 Opus 4.6 而非 pin 的 Fable 5（settings watcher 覆蓋 set_config_option，未解決）
- [[opencode-acp-implementation]] — OpenCode 的 ACP 實作研究（stdio+HTTP 雙層架構、完整方法表、capabilities 宣告、session/update 與 tool kind 對映、permission fail-closed、接成 bridge 第四個 backend 的 authMethods 恆非空陷阱）
- [[paulsha-cortex-governance-plane]] — 外部 repo paulsha-cortex 研究（治理三件套、foreign review 的 independence_domain 資料化、verification contract 的 must_change 產出物驗證、對照 bridge 的借鏡排序；成熟度 VERSION 0.0.0 僅當概念來源）
- [[cc-session-reader]] — 外部 repo cc-session-reader 研究（Go CLI 靜態壓縮 Claude Code transcript、inherit 分頁、ADR-003 狀態判定階梯揭露 Bash 結果無 success 欄位／is_error 不可信、ADR-004 fleet data 與異源覆核後刻意不實作、ADR-005 錯誤相同才折的不變式、安裝腳本會寫進 junction 正本；**借鏡評估已結案：無項目吸收**，且實測證實 is_error 在現行版本可信）
- [[claude-agent-sdk]] — Claude Agent SDK（原 Claude Code SDK 已改名）研究（四路對照與 Tool Runner≠Agent SDK 的 harness/部署二維判準、query() 與 Options/Query 物件 API 面、能力清單與 claude.ai 額度授權限制、bridge → claude-agent-acp 0.63.0 → Agent SDK 0.3.220 層次；settingSources 寫死 user/project/local 是「CLAUDE.md 直達」與「19 個 MCP 行程」的同一個開關）
- [[cloudflare-os]] — 外部 repo cloudflare/cloudflare-os 研究（**Step 2–3 完成、已 clone 核對原始碼**；Gadget/Gatekeeper/Observer 三概念、讀取核可同步 vs 側效動作核可完全非同步的刻意不對稱且「不存在可略過檢查的模式」、ActionStore 重啟即認賠的 at-most-once 構造、型別當權限閘門；判別式是**單人 vs 多人** ∴ Observer／可達圖整套是「不需要」非「還沒做」；⚠️ **初版一條事實錯誤已更正**——「bridge ASK 是同步阻塞」為誤，實為 queue 後 turn 結束才 commit，真實差距是 turn 終結 vs 帶假定值續跑（見 §4.1）；借鏡排序 B1 at-most-once／B2 無 skip 模式 建議吸收，B3 動作核可閘門／B4 模擬續跑 不建議；上游明言不收外部貢獻 ∴ 回饋路徑不通）
- [[codegen-git-init-gap]] — codegen clone 路徑從不建 repo 的流程缺口（Step 0.0 刪 .git 卻沒人建回來、專案在 finalize gate 38/38 全綠下無版控）、補 Step 0.2 與 gate_git 四條斷言、UK slot 的 git 追蹤慣例（**模板不是出貨形態**、node_modules 進版控、AI 產物靠專案自行加碼、`.claudedocs` 其實是 local-only 的 info/exclude 在擋），以及五輪異源覆核 12 條 findings——含**同一形狀的假因果連出現三次，每次都是「為了修上一條而新寫的句子」**
- [[deepseek-harness]] — DeepSeek Harness (dsh) 借鏡評估（源碼層 49 個 package 盤點、`packages/acp` 是 **agent 側**但對 bridge **不可用**——不宣告 MCP capability ∴ agent-action 層歸零、`session/load` 明列不支援、啟動只有 demo script；更正 2026-08-17 首輪報告的證據等級為 B 級（raw 被 rate limit ∴ 從搜尋＋文件站建、未讀源碼）；原三條軟性借鏡沿用；**第二輪追查 compaction/spill 並更正本頁初版**——「bridge 完全沒有對應物」為誤（實有 context-assembly 注入側預算／context-telemetry 精確使用率／70% 警告），且壓縮既有歷史結構上不是 bridge 的活（不擁有 context），套 spill 到 list_facts 的成本不對稱方向相反（漏 fact 比多花 1.4% 視窗貴，已量測最大 shard 31.5k chars）∴ 唯一建議項是「70% 警告一次性、之後到死線再無提醒」的分層觸發；2026-08-18 新增並更新）
- [[query-msh2m15g]] — BC-17b 恆真問題的根因分析（突變 2 沒被抓到、withProvider pin 被 set_config_option 回應的 configOptions 蓋回去、突變測試的結構性限制；2026-08-17 新增）
- [[kkterm]] — 外部 repo ryantsai/KKTerm 借鏡評估（Tauri 桌面終端工作站，真正交集是「宿主 app 怎麼接多家 AI agent、怎麼管動作權限」；**K1 最有價值**——`*.dangerous.*` 命名空間 + 單一 flag + default-deny 的廉價核可閘門，**推翻 [[cloudflare-os]] B3「要狀態機+UI+儲存 ∴ 成本高」的前提**，但須換算方向：bridge 常在無人值守輪次跑 ∴ 該走 ask 佇列而非回 `permissionRequired` 讓 agent 靜默卡死；K2 ACP 初始化失敗退回 one-shot CLI（bridge 未見等價）、K3「新 assistant surface 必須有 prompt-secret 斷言」通則閘門、K4 Cursor 當第 4 backend、K5 SKILL.md 的 Boundaries 詞彙釘樁；排除對外 MCP server／compaction／ADR／skill 隨 repo 出貨；**全頁 B 級未 clone**，並記一條自抓的誤讀——AIINSTRUCTIONS.md 是貢獻者文件不是 runtime prompt；2026-08-18 新增）

---

Total pages: 53
Last updated: 2026-08-18 wikisync（ingest-ripple 4 頁更新——uk-slot 補 9 條含 2 則新內容（規格圖是 A 級證據、跨專案搬 Spine 驗收陷阱）；verification-diagnosis 新增第九節補 7 條（可否證條件、持久化宣稱前查 tool call、上限誠實邊界、3 則今日執行期驗收陷阱）；bridge-smoke-gate 補 1 條（tsc-only-fail 突變體移出 runtime 集）；adversarial-review 補 3 條（未版控實作只給推論、全稱結論的外部事件前提、駁回本身要受檢且可能雙向過頭）；5 個 Query Auto-save 候選皆判定內容不足（3 個是純 ASK 按鈕回應無實質內容、2 個是被截斷的片段看不到完整脈絡）跳過）
Previous: 2026-08-18 新增 [[kkterm]]（外部 repo 借鏡評估；K1 推翻 [[cloudflare-os]] B3 的成本前提）
Earlier: 2026-08-18 新增 [[deepseek-harness]]（外部 repo 借鏡評估；補上 08-17 那份研究報告從未落成 wiki 頁的缺口——`wiki-auto-save-candidates.jsonl` 該筆仍 `processed:false`，**未手改該檔**，因全檔 100 筆有 92 筆同樣未處理 ∴ 該旗標不是 pipeline 的實際驅動）
Earlier: 2026-08-18 wikisync 手動重跑（08-18 dream 那輪失敗、turn 無產出，本輪補做）：ingest-ripple 5 個 topic／5 頁更新——bridge-smoke-gate 補 3 條（fast tier 成本偏斜、canary cleanup 型紅燈、突變改錯對象）、dev-tools 補 ghost @import（f_3d90f2 已被 f_cf5316 取代 ∴ 移入 history_sources）、bridge-memory 補 2 條、uk-slot-eye-strike 更正 tsc 閘門並補診斷順序、verification-diagnosis 新增第八節（f_e21eb1 原判給 bridge-project，因該頁在行數棘輪基線上且內容屬方法論而改收）。行數棘輪 PASS。**未處理積壓（下輪優先）**：f_ca710c（bridge-model-strategy，08-13 起最久）、f_166468／f_676da8（uk-slot-clash-olympus）、f_c9d934（bridge-infra）、f_0611d8（無 ripple 條目，且其 88,147 已被 f_cf5316 標為修前值）、f_bc5b05／f_5eaaed（ripple 記的 bridge-testing topic 已不存在，重分類後分別落在 bridge-smoke-gate 與 bridge-project shard）、f_271855（misc，設計上無頁）
Earlier: 2026-08-17 wikisync（ingest-ripple 3 頁更新——user-pref 補 2 條 Git 紀律、adversarial-review 補 5 條含 2026-08-16 觀察、bridge-project 補 3 條含重試 instrumentation；query-msh2m15g 新增；4 個無 fact sources 的 ASK 回應 query 跳過）
Earlier: 2026-08-16 wikilint（機械檢查 50 頁：orphans=0、broken links=0，全 wiki 連結完整；深查 sources-vs-shard 計數落差挑出 3 頁 stale 並修正——[[igs-uof]] 補 5 條漏引用 fact + 修正一次錯誤懷疑（f_6420f5 經查證為真實有效 fact 非錯字）、[[uk-slot-eye-strike]] 補 4 條含新技術內容（停輪曲線量化、baked path 限制）、[[bridge-dream]] 補 5 條含既有段落漏引用的 provenance + 新增 desc 截斷閘門限制小節；audit_provenance 全域 51 頁 blocking=0）
