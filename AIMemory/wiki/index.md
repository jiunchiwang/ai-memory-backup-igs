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
- [[uk-slot-eye-strike]] — Eye Strike 系列（第一代 uk_658 + 續作 uk_872、7 個專案特有機制、SpineKit 規範）
- [[bridge-project]] — Telegram-Kiro-Bridge 專案（架構、AIMemory、Rich Messages、Reply Context、Smoke 隔離、Specialist Dashboard、Status Server 加固、背景通知 flakiness 診斷判準、Fable5 對抗覆核、claude-mem plugin worker 診斷、Claude Agent SDK 權限模型、heredoc \n 展開陷阱、POLICIES 假宣稱更正、Telegram 出站訊息重複投遞四層修復＋重放安全性三判準、同事接手 repo 用獨立 fork 而非 GitHub Fork 按鈕；2026-08-15 更新）
- [[bridge-acp]] — Bridge ACP 與 Model 配置（adapter 切換差異、/agent 熱切換、model pin、ACP adapter 能力偵測陷阱、AcpBackendDef 語意差異、session/resume 語意分析與能力探測、tool 結果狀態判定鏈與 is_error 可信度實測、Codex/Kiro hooks 能力更正）
- [[adversarial-review]] — 異源對抗覆核紀律（長期警戒模式清單、覆核紀律演化、價值實證時間序、覆核者成本分級、派工前能力軸/blind advisor 幻覺、scope 擴張敘述凍結、樣板知識同源天花板、修正動作本身產生假因果的獨立失效模式；2026-08-05 從 bridge-acp 拆出）
- [[bridge-model-strategy]] — Bridge Model 選型與配額策略（pin 修正史、Kiro model 生態、Kiro effort 值域 per-model 實測、sonnet-4.6[max] vs opus-4.5 對照實驗、advisor 顧問工具與其 token 成本／context 剝除機制、Claude Max 5x 分配策略；2026-08-05 從 bridge-acp 拆出）
- [[bridge-session]] — Bridge Session 生命週期（archive 蒸餾層、ACP resume、/session 多 session、transcript 路徑）
- [[bridge-streaming]] — Bridge Streaming 與訊息渲染（Draft API 三階段 lifecycle、4096 截斷、rate limit、Rich Messages）
- [[bridge-draft-diag]] — Bridge Draft 診斷與重播修復（三個獨立成因、cutPendingTokenTail 扣留式設計、診斷探針、可重用方法論；2026-08-08 從 bridge-streaming 拆出）
- [[bridge-memory]] — Bridge 記憶與維運系統（AIMemory 結構、/dream 14 步維運、factlint 三層防禦、topic 分類、wiki 知識庫、embedding router、備份、判斷 wiki 保護不要自行 Grep 要直接呼叫 forget()、apply_topics token 機制阻塞已修（phase-aware guidance）、skill orphan 涵蓋不到 plugin marketplace；2026-08-15 更新）
- [[bridge-dream]] — Bridge Dream 例行維運框架（dream.json models 表 per-backend 設計、claude-mem-curate 接入、turn 誤報根因、confabulation 教訓）
- [[bridge-specialist]] — Bridge Specialist 分身系統（配置、token 執行權限層、PARALLEL_DELEGATE cross-check、Dashboard 監控、run_plan 全有全無設計、moa-ref-codex 已知擱置、moa-ref-kiro/adversary 是 blind advisor 不能覆核、run_plan 能力錯配缺陷已修（wf-review/wf-verify 改派 verifier/moa-ref-security）、委派逾時 per-domain 可設定、extractModel()/maxTurns 已知未修項目；2026-08-15 更新）
- [[bridge-research]] — Bridge 改善研究與 Roadmap（外部框架借鏡、fable-advisor context packaging、claude-plugins-official Permission Relay、PostTool Hooks A→D、Karpathy P0、Rich Messages Draft、spine-animation-ai 自包含 Skill 打包機制）
- [[bridge-upstream-sync]] — Bridge Upstream Fork 同步與合併衝突處理（remote 配置、merge 策略、三種衝突處理原則、同步歷程、push 前異源覆核閘（2026-08-13 起預設 kiro-cli glm-5，非 Fable5）；2026-07-21 從 bridge-project/bridge-acp 拆出）
- [[bridge-roadmap]] — Bridge 開發 Roadmap（Pending / In Progress 追蹤，2026-07-28 建立）
- [[bridge-smoke-gate]] — Bridge 測試閘門與建置（tsc/smoke tier/pre-push 三層、dist≠跑著的碼、環境隔離假失敗、計數同步儀式、probe-* 命名隔離、CI 決策、check-draft-streaming.mjs 測試陷阱三則、smoke 逾時 flaky 診斷與 A/B 類逾時分法、mutate-gate harness 慣例（紅燈行規範／noUnusedLocals 陷阱／無 timeout 風險）、hang detection 門檻侵蝕；2026-08-01 從 bridge-project 拆出，2026-08-15 更新）
- [[bridge-doc-sync]] — Bridge 文件同步機制（事實來源改直接 import、計數類機械閘門設計原則、耗時排除在硬閘門外；2026-08-08 新建）
- [[bridge-secrets-backup]] — Bridge 備份與密鑰洩漏防護（acp-trace 洩漏修復、GitHub PAT 洩漏與自我重複污染迴圈、/sharedsync 跨帳號 credential、default-skills 自動回填；2026-08-08 新建）
- [[bridge-infra]] — Bridge 基礎設施（Process 生命週期、start.bat supervisor、暖機 coreReady/FIFO、session.buffer 中途失敗偵測、Impact-Gate Hook；2026-08-08 新建）
- [[bridge-self-eval]] — Bridge 自評與收尾檢查（SELF_EVAL 六個共通致命缺陷檢查清單、/selfeval 決策、Turn-Lint 啟發式 warn-only 設計；2026-08-08 新建）
- [[dev-tools]] — 開發工具與環境設定（Python/Playwright/TypeScript、機器路徑、工作流程、excel-to-ai-document 專案、.env 編輯驗證做法、Git Bash timeout /t 陷阱、skillUsage 權威來源；2026-08-15 更新）
- [[agent-system-architecture]] — Agent 系統五層架構（公司比喻：Agent/MCP/Memory/Workflow/Agent SDK 的角色與關係）
- [[spine-viewer]] — Spine Viewer 插件（Cocos Creator 編輯器擴充，批次掃描 DrawCall/Triangle 效能報告）
- [[ai-strategy]] — 跨模型 AI 策略（正典語料庫架構、投影分發、headless 安全機制、第三方安裝腳本汙染正本風險）
- [[user-pref]] — 使用者偏好與決策風格（ASK 優先、Git 紀律、自動化保守策略、除錯對策）
- [[skill-and-eval]] — Skill 評估與管理（方法論整合、工具評估決策）[歷史頁面，topic 已併入其他分類]
- [[igs-uof]] — IGS-UOF 加班單自動化（原 vc-uof-hours 改名擴充、加班單送出五層防線、刷卡時間 onchange 踩坑）
- [[verification-diagnosis]] — 驗證與診斷方法論（綠燈假象五型與突變測試、診斷實驗三原則、證據的 recovery 邊界、純觀測欄位、await 縫開 race、同源自審天花板、註解洩漏答案、行為測試 vs 模型冷讀判準；2026-08-01 從 misc 拆出）

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

---

Total pages: 50
Last updated: 2026-08-15（wikisync ingest-ripple 優先清單：更新 [[bridge-project]]／[[bridge-smoke-gate]]／[[bridge-specialist]]／[[bridge-memory]]／[[dev-tools]] 五頁，補齊 62 條未同步 fact 的 sources（bridge-project 15、bridge-smoke-gate 18、bridge-specialist 7、bridge-memory 10、dev-tools 7 + 清掉 dev-tools 1 個幻影 source ID），audit_provenance 五頁皆 blocking=0；topicreview 阻塞已修並記錄於 [[bridge-memory]]、run_plan 能力錯配已修並記錄於 [[bridge-specialist]]、Telegram 重複投遞四層修復已記錄於 [[bridge-project]]）
Previous: 2026-08-14（新增 [[cloudflare-os]] 外部 repo 研究頁，Step 0–1 完成、吸收範圍待裁決）
