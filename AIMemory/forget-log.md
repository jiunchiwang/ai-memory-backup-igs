- [2026-07-07T23:33:10.425Z] user=509424983 query="telegram-kiro-bridge 目前三項待辦（2026-07-06 使用者決定暫緩）：NotebookLM MCP 安裝修復、SPEC-acp-hot-swap 實作（W1-W7 未做）、SPEC-moa-provider 實作（W1-W18 未做）" deleted=0 token=forget-fb233b6a-1

- [2026-07-07T23:33:10.446Z] user=509424983 query="session resume 待辦：生產 bridge .env 加 ACP_SESSION_RESUME=true 重啟後做手動 e2e；首次啟用需觀察 replay 時序——真 adapter 若在 session/load 回應後才補送 replay update 有 token 重放風險，保守 fallback 方案在計畫檔風險 #1" deleted=0 token=forget-5a757299-1

- [2026-07-07T23:33:10.461Z] user=509424983 query="telegram-kiro-bridge 生產機 .env 的 ACP_SESSION_RESUME=true 已於 2026-07-07 啟用（.env:39 解除註解），待使用者重啟 bridge 後做手動 e2e：建 context 暗號 → idle → 驗證 resumed ACP session log + 暗號保留 + 無舊訊息/ASK token 重放" deleted=0 token=forget-efcd647a-1

- [2026-07-07T23:33:10.476Z] user=509424983 query="telegram-kiro-bridge 已完成 preamble 瘦身（commit ac88285）：MEMORY_PREAMBLE_TAIL 30→15，且 memory.ts 的 7 個 guideline 區塊合併為單一 [Agent disciplines] 精簡塊；preamble 從 18,650 降到 12,975 chars（-30%），需 bridge 重啟才生效" deleted=1 token=forget-daad479d-1
    - [f_f67f15] [2026-07-06T22:56:52.238Z] telegram-kiro-bridge 已完成 preamble 瘦身（commit ac88285）：MEMORY_PREAMBLE_TAIL 30→15，且 memory.ts 的 7 個 guideline 區塊合併為單一 [Agent disciplines] 精簡塊；preamble 從 18,650 降到 12,975 chars（-30%），需 bridge 重啟才生效
- [2026-07-07T23:33:10.497Z] user=509424983 query="遺留待辦：upstream 的 check-moa.mjs 壞測試（6c70901 把 resolvePreset 改 async 但測試仍同步呼叫，8 項假失敗）——與 merge 無關，可另開 commit 修並回報 upstream" deleted=0 token=forget-c86465c6-1

- [2026-07-07T23:33:10.536Z] user=509424983 query="使用者對 session 移植的決策：選方案 A（只做 resume 不做 /session UI），方案 B（SessionStore+UI）等 A 跑穩再議；理由是 restart 連續性 + idle 殺 process 省記憶體最實、避免與 goal/MoA/relay 單 session 假設的互動風險" deleted=0 token=forget-b8b3d9e1-1

- [2026-07-07T23:33:10.562Z] user=509424983 query="telegram-kiro-bridge 已實作 /agent init 指令（commit 8613135，尚未 push）：設定檔缺失時自動建立 acp-providers.json 範本——以 .env 當前 agent 推斷 key（kiro/claude/codex）種出保證可用 entry（帶 model/effort pin），另兩個已知 backend 以 scaffold 附上並在 label 標「請確認 command」；既有檔一律不覆蓋，需重啟 bridge 生效" deleted=1 token=forget-4625968d-1
    - [f_a479e6] [2026-07-07T13:14:07.481Z] telegram-kiro-bridge 已實作 /agent init 指令（commit 8613135，尚未 push）：設定檔缺失時自動建立 acp-providers.json 範本——以 .env 當前 agent 推斷 key（kiro/claude/codex）種出保證可用 entry（帶 model/effort pin），另兩個已知 backend 以 scaffold 附上並在 label 標「請確認 command」；既有檔一律不覆蓋，需重啟 bridge 生效
- [2026-07-07T23:33:10.590Z] user=509424983 query="telegram-kiro-bridge 的 reply/quote context 注入 commit 1346519 已於 2026-07-07 push 至 origin/main，本地與遠端同步（功能仍需重啟 bridge 主程序才生效）" deleted=1 token=forget-3e8785f7-1
    - [f_f578ad] [2026-07-07T09:39:42.001Z] telegram-kiro-bridge 的 reply/quote context 注入 commit 1346519 已於 2026-07-07 push 至 origin/main，本地與遠端同步（功能仍需重啟 bridge 主程序才生效）
- [2026-07-07T23:33:10.624Z] user=509424983 query="telegram-kiro-bridge 的 README 已於 2026-07-07 補齊文檔並 push（commit 5233767）：/agent 熱切換、ACP_SESSION_RESUME、/session 指令與 /reset 只清 active 新語意" deleted=0 token=forget-69547103-1

- [2026-07-07T23:33:10.657Z] user=509424983 query="bridge 的 /agent 無回應事件（2026-07-07）診斷結案：暫時性故障（429 rate-limit 窗口或 crash 重啟空窗），code 無 bug；已實測該回覆訊息以 parse_mode=Markdown 可正常送出（HTTP 200）" deleted=1 token=forget-7374e323-1
    - [f_c8aeb0] [2026-07-07T13:00:14.433Z] bridge 的 /agent 無回應事件（2026-07-07）診斷結案：暫時性故障（429 rate-limit 窗口或 crash 重啟空窗），code 無 bug；已實測該回覆訊息以 parse_mode=Markdown 可正常送出（HTTP 200）
- [2026-07-07T23:33:10.693Z] user=509424983 query="ms-wiki-knowledge-base 原是幽靈 skill（bridge memory.ts 的 wikisync/factlint/wikilint prompt 引用它但 SKILL.md 從未存在，累積 19 次 orphan 使用），已蒸餾三個 lint 迴圈邏輯補回實體於 AI-canonical/skills/general/（commit a8ced88）" deleted=1 token=forget-2317984c-1
    - [f_45e860] [2026-07-06T22:31:18.830Z] ms-wiki-knowledge-base 原是幽靈 skill（bridge memory.ts 的 wikisync/factlint/wikilint prompt 引用它但 SKILL.md 從未存在，累積 19 次 orphan 使用），已蒸餾三個 lint 迴圈邏輯補回實體於 AI-canonical/skills/general/（commit a8ced88）
- [2026-07-07T23:33:10.724Z] user=509424983 query="skill-usage 兩 store 分裂已於 2026-07-07 解決：舊 ~/.kiro/skills/.usage.json（29 筆完整歷史）合併進 ${MEMORY_DIR}/config/skill-usage.json，舊檔改名 .usage.json.merged-20260707 封存；分裂根因是 ACP 從 Kiro 切 Claude 後 SKILL_DIR 變更，usageStore 一次性遷移邏輯掃不到舊路徑" deleted=1 token=forget-db611fab-1
    - [f_f98bd7] [2026-07-06T22:31:18.738Z] skill-usage 兩 store 分裂已於 2026-07-07 解決：舊 ~/.kiro/skills/.usage.json（29 筆完整歷史）合併進 ${MEMORY_DIR}/config/skill-usage.json，舊檔改名 .usage.json.merged-20260707 封存；分裂根因是 ACP 從 Kiro 切 Claude 後 SKILL_DIR 變更，usageStore 一次性遷移邏輯掃不到舊路徑
- [2026-07-07T23:33:10.762Z] user=509424983 query="使用者從「從LLM到AI_Agent.pdf」（IGS 小葉內訓教材）萃取了 4 個 skill：dual-skill-review-loop、non-engineer-agent-design、knowhow-accumulation、self-eval-prompt-pattern" deleted=0 token=forget-81868bef-1

- [2026-07-07T23:33:10.800Z] user=509424983 query="telegram-kiro-bridge 已實作 P1 Session 歸檔/恢復機制：session 關閉時 exportSession() 寫結構化 JSON 到 session-archive-{chatId}.json（含 turns/goal/stats/recentSummary），新 session 建立時 loadArchive() + buildRestorationBlock() 注入 preamble 後自動刪除；與 working-state 互補（WS 說做什麼，archive 說上下文在哪）" deleted=0 token=forget-201b1ef1-1

- [2026-07-07T23:33:10.832Z] user=509424983 query="telegram-kiro-bridge 已新增 /reset clean（或 /reset fresh）指令：結束 session 後額外刪除 session-archive + working-state，下次對話不帶入上次上下文；預設 /reset 行為不變（照舊歸檔）" deleted=0 token=forget-45e4743b-1

- [2026-07-07T23:33:10.861Z] user=509424983 query="Session Archive 設計決策：因為只需最近一次 session 所以 per-chatId 單檔覆寫（排除 append-only 因為歷史有 transcript MD）；因為避免 context 爆炸所以恢復只注入 ~300 字摘要（排除全量 turn 注入因為會佔太多 budget）；turn text 截斷 2000 字" deleted=0 token=forget-c0bc8001-1

- [2026-07-07T23:33:10.894Z] user=509424983 query="telegram-kiro-bridge 已實作 ACP session resume 方案 A（feat b6e028f + docs 72277b9，已 push origin/main）：ACP_SESSION_RESUME=true 閘控且預設 off；idle/crash/SIGINT 保留 registry 可 session/load 恢復（不重注 preamble），/reset、/agent、/restart、<<RESTART>> 走 fresh 並清 registry（shutdown 帶 clearResume 參數區分）" deleted=0 token=forget-e8a3928d-1

- [2026-07-07T23:33:10.929Z] user=509424983 query="session resume 實作計畫與三段 review 軌跡存於 bridge repo docs/superpowers/plans/2026-07-07-acp-session-resume.md（含 BC-1~5 行為契約與 adapter 實測記錄表）" deleted=0 token=forget-b8652107-1

- [2026-07-07T23:33:10.952Z] user=509424983 query="uk_pirates_queen 的懸賞令（WantedPoster）使用 cc.Layout 自動排版，ReconcileCascade 退場時因 node.active=false 導致 Layout 瞬間重排，已被提出視覺突兀需優化" deleted=0 token=forget-d262f259-1

- [2026-07-07T23:33:10.973Z] user=509424983 query="並發 gotcha:在 Promise.all 之前的同步階段計算狀態決策(例如 willGhost),會與並發 group dispatch 產生 race condition;應把這類決策移到 async 階段計算以避免競態。" deleted=0 token=forget-be752e05-1

- [2026-07-07T23:33:10.996Z] user=509424983 query="Cocos 版面要在「兩項移除一項」時避免置中跳動(snap),可用 ghost slot 雙佔位機制,在不改動 Layout 參數的前提下同時滿足 0→1 置中、2→1 不跳動與旋轉相容。" deleted=0 token=forget-9f8b4c41-1

- [2026-07-07T23:33:11.027Z] user=509424983 query="uk_pirates_queen 的掉落動畫（drop-out）凍結視窗回歸問題，根因是把凍結語意（m_isInDropMode）與掉落動畫 promise（m_dropAllSymbolsOutOfScreenPromise）混為一談，且直接在 StartSpin（約 L943）觸發掉落；經對抗式評選後採 MVP 最小手術方案：新增 m_isInDropMode 布林專職凍結語意、把 promise 降級為純動畫 handle、並把掉落觸發從 StartSpin 移到獨立的 TriggerDropOut() method。" deleted=0 token=forget-32ec40d4-1

- [2026-07-07T23:33:11.052Z] user=509424983 query="使用者確認 bridge 的自我改進優先級：Context Budget（事前紀律 + 事中熔斷）和 ASK 強制觸發規則是當前最需要的兩個 preamble 加強項" deleted=0 token=forget-92ed5d53-1

- [2026-07-07T23:33:11.083Z] user=509424983 query="使用者建立了 uk-slot-spec-to-impl skill（正本 G:\\AI\\AI-canonical-corp\\skills\\slot\\，commit 95da214）：UK 老虎機規格書→實作的三步驟工作流程（xlsx 轉換→差異開發規格 docs/dev-spec.md→SPEC.md milestone 任務拆解 M0a~M4），含兩個人工檢查點與 proto 未發佈時的 ⏳ 假設記錄雙路徑" deleted=1 token=forget-8d8bd995-1
    - [f_411e3f] [2026-07-06T20:13:27.683Z] 使用者建立了 uk-slot-spec-to-impl skill（正本 G:\AI\AI-canonical-corp\skills\slot\，commit 95da214）：UK 老虎機規格書→實作的三步驟工作流程（xlsx 轉換→差異開發規格 docs/dev-spec.md→SPEC.md milestone 任務拆解 M0a~M4），含兩個人工檢查點與 proto 未發佈時的 ⏳ 假設記錄雙路徑
- [2026-07-07T23:33:11.113Z] user=509424983 query="memory-to-skill 正本 SKILL.md 已加入 Confidence Scoring 量化門檻（Step 2 後）：confidence = F×C（頻率×成本），≥0.5 進候選、0.3-0.49 留底觀察、<0.3 跳過；靈感來自 ECC continuous-learning-v2 的 instinct confidence scoring" deleted=0 token=forget-08e35cd3-1

- [2026-07-07T23:33:11.148Z] user=509424983 query="使用者對 preamble 大小的取捨判斷：佔 context 5-6% 可接受但到警戒線就削減；優先砍 facts tail 與 guideline 區塊（排除 wiki 索引瘦身與維持現狀），理由是舊 facts 有 topic index + list_facts 補位" deleted=0 token=forget-0b99da08-1



## 2026-07-09T04:28 factlint batch delete (dream High Priority)

Deleted 8 facts (completion events / superseded records):
- f_cb10bc: 內訓教材 4 skill 萃取記錄（純來源記錄，skill 仍存在）
- f_e255b2: uk_slot_template push 完成（純完成事件）
- f_3b73a9: topics.json 重整記錄（已被新版取代）
- f_f0d764: skill-usage 測試汙染問題記錄（已被 f_de4ad8 修復記錄取代，且修復記錄本身也是完成事件）
- f_de4ad8: 測試汙染修復完成記錄（純完成事件）
- f_7a3d00: hit-log 零命中發現（已被 f_c965d5 修復記錄取代）
- f_ab7c55: factlint 27條刪除結果（純完成事件）
- f_98933f: dream High Priority 全處理完成（純完成事件）

Master: 163 → 155 facts
Backup: facts-509424983.bak.20260709.md
Shards updated: bridge-project.md (-3), misc.md (-3), uk-slot.md (-2)
- [2026-07-09T20:25:59.728Z] user=509424983 query="使用者認識 IGS（鈊象電子）的工程師小葉（葉錦頤）" deleted=1 token=forget-4595c545-1
    - [f_d0757b] [2026-05-29T16:20:19.523Z] 使用者認識 IGS（鈊象電子）的工程師小葉（葉錦頤），該文件來自其商用魚機 RD7 部門 7 週內訓
- [2026-07-09T20:26:10.158Z] user=509424983 query="uk-conventions skill 在 usage store 且 harness 可用，但實體不在" deleted=1 token=forget-94039045-1
    - [f_d7548f] [2026-07-07T20:38:22.816Z] uk-conventions skill 在 usage store 且 harness 可用，但實體不在 ~/.claude/skills 也不在 ~/.kiro/skills，來源待查（可能專案級或 plugin 載入）
- [2026-07-09T20:26:21.464Z] user=509424983 query="telegram-kiro-bridge 已於 2026-07-09 同步 upstream 至 dd63cd4" deleted=1 token=forget-9b3e61c6-1
    - [f_b12677] [2026-07-09T01:57:54.687Z] telegram-kiro-bridge 已於 2026-07-09 同步 upstream 至 dd63cd4（8 個 commit，含 session archive staleness gate、tool-use 訊息摺疊 UI、doctor specialist-domains 健檢、preamble 交辦三要素等），merge 乾淨無衝突已 push origin/main；生產 bridge 需 rebuild（tsc -p .）+ 重啟才生效
- [2026-07-10T20:13:40.605Z] user=509424983 query="external-repo-absorption-methodology 從 skill-candidates 升格為正式" deleted=1 token=forget-8c5be7f4-1
    - [f_30c844] [2026-07-10T00:12:51.622Z] 使用者確認將 external-repo-absorption-methodology 從 skill-candidates 升格為正式 skill ms-external-repo-absorption（AI-canonical commit 542a20a），5 次同構循環達門檻
- [2026-07-10T20:13:49.048Z] user=509424983 query="preamble 強化 commit 4c1cfd5 已於 2026-07-11 驗證正確" deleted=1 token=forget-189e4697-1
    - [f_235a08] [2026-07-10T16:07:35.320Z] telegram-kiro-bridge 的 preamble 強化 commit 4c1cfd5 已於 2026-07-11 驗證正確：tsc 通過、ceiling 5884/8000 chars、PARALLEL_DELEGATE 新五要素文案確認落在被量測的 fixed core 內、運行中 bridge 的實際 preamble 已逐字生效、相關 smoke 全過
- [2026-07-10T20:13:57.366Z] user=509424983 query="Fable 5 model pin 修復（commit 91f64e2 nested SDK 手動升級）已驗證生效" deleted=1 token=forget-b7da4a7d-1
    - [f_79a52f] [2026-07-10T15:54:46.752Z] claude-agent-acp 的 Fable 5 model pin 修復（commit 91f64e2 nested SDK 手動升級）已驗證生效：bridge Claude backend session 實際跑 claude-fable-5（先前 session 為 Opus 4.6）
- [2026-07-10T20:14:05.693Z] user=509424983 query="已完成 Specialist Dashboard v1（feat/specialist-dashboard 分支 3 commits merged" deleted=1 token=forget-570a61f8-1
    - [f_d98d05] [2026-07-10T09:30:03.955Z] telegram-kiro-bridge 已完成 Specialist Dashboard v1（feat/specialist-dashboard 分支 3 commits merged to main）：status-server 新增 6 個 specialist API endpoints（設定/preamble/歷史/產出物/facts）、status-app/index.html 重寫為 hash-based SPA（Dashboard 卡片總覽 + Specialist Detail 五 tab + Live View SSE）、/status 指令移除 Electron 改用 web_app 按鈕（STATUS_HTTPS_URL env var 控制）+ fallback URL、status-app/main.js 與 package.json 已刪除
- [2026-07-11T23:56:26.704Z] user=509424983 query="寫成 173881a" deleted=1 token=forget-a6edb234-1
    - [f_724810] [2026-07-11T11:40:35.131Z] telegram-kiro-bridge 的 commit 8d0b8fa body 引用原修正 hash 筆誤（寫成 173881a，正確為 173591a），決定不 amend，僅程式碼追溯時需知悉
- [2026-07-11T23:56:26.817Z] user=509424983 query="先前「未 push」狀態已過時" deleted=1 token=forget-79ef8da0-1
    - [f_f7fe66] [2026-07-11T12:13:08.819Z] telegram-kiro-bridge 的 commit 8d0b8fa 已於 2026-07-11 push 上 origin/main（cdf1ff3..8d0b8fa），先前「未 push」狀態已過時；仍需重啟 bridge 才生效
- [2026-07-11T23:56:26.945Z] user=509424983 query="merge f6341fd 已 push" deleted=0 token=forget-6765cf0d-1

- [2026-07-11T23:56:27.048Z] user=509424983 query="f970aa0a" deleted=0 token=forget-733e319b-1

- [2026-07-11T23:56:27.149Z] user=509424983 query="13b25fc..cdf1ff3" deleted=1 token=forget-9e1c9ed4-1
    - [f_602278] [2026-07-11T08:33:32.120Z] telegram-kiro-bridge 自檢修正已 commit 8d0b8fa（updateJson 補 compare-and-delete、hideTrailingUnterminatedToken opener 補 CONTINUE 裸型、刪 tool-hooks 文件殘留）；連同前面 8 個 dead-code/修正 commit（13b25fc..cdf1ff3）都需重啟 bridge 才生效
- [2026-07-11T23:57:25.908Z] user=509424983 query="merge f6341fd 已 push" deleted=1 token=forget-6765cf0d-1
    - [f_c899ab] [2026-07-07T08:51:39.027Z] telegram-kiro-bridge 已於 2026-07-07 同步 upstream（merge f6341fd 已 push）：拉入 23 個 commit 含 MoA Phase 1-4（blind review/plan mode/debate/review-panel/read-only MCP）、/agent ACP 熱切換、auto_trigger semantic routing——原暫緩的 SPEC-acp-hot-swap 與 SPEC-moa-provider 已由 upstream 實作補齊；需重啟 bridge 主程序才生效
- [2026-07-11T23:57:25.932Z] user=509424983 query="f970aa0a" deleted=1 token=forget-733e319b-1
    - [f_1746d0] [2026-07-08T06:05:03.357Z] 使用者於 2026-07-08 把 Passive Monitor 排程 f970aa0a 從每日 8 次（8-22 偶數時整點）改為每日 2 次（12:00、22:00），直接改 schedules.json，若 bridge cache 未重載需重啟生效
- [2026-07-12T20:06:41.743Z] user=509424983 query="[WS] task: 修復 memory MCP 啟動即死" deleted=1 token=forget-a120033a-1
    - [f_138118] [2026-07-12T00:32:42.698Z] [WS] task: 修復 memory MCP 啟動即死 — 已全部完成。completed: ingest-ripple 改用 resolveMemoryDir() 切斷 config.js 依賴（commit 89ca1d6）、dist 已 rebuild、空 token 實測 + smoke 過、教訓已存 bridge-research shard。next_action: 重啟後用 ToolSearch 確認 memory MCP 工具（list_facts/remember/forget）已掛載即收工，無其他待辦
- [2026-07-12T20:06:55.792Z] user=509424983 query="README 已於 2026-07-07 補齊文檔並 push" deleted=0 token=forget-69547103-1

- [2026-07-13T20:05:52.271Z] user=509424983 query="[WS] completed: 新增 src/status-tunnel.ts" deleted=1 token=forget-cf438355-1
    - [f_aa639e] [2026-07-13T02:23:45.380Z] [WS] completed: 新增 src/status-tunnel.ts（cloudflared quick tunnel 自動 spawn），index.ts 接入啟動/關閉流程，tsc 通過；重啟後 /status 應顯示 Mini App 按鈕（需有 running task）
- [2026-07-13T20:05:54.379Z] user=509424983 query="已新增 src/status-tunnel.ts（cloudflared quick tunnel 自動 spawn）：bridge 啟動時 fire-and-forget spawn cloudflared" deleted=1 token=forget-273d5b67-1
    - [f_2ca7bd] [2026-07-13T02:23:57.607Z] telegram-kiro-bridge 已新增 src/status-tunnel.ts（cloudflared quick tunnel 自動 spawn）：bridge 啟動時 fire-and-forget spawn cloudflared tunnel 指向 localhost:3847，解析到 trycloudflare.com URL 後動態設 process.env.STATUS_HTTPS_URL，讓 /status 在有 running task 時顯示 Telegram Mini App 按鈕；cloudflared 沒裝或 spawn 失敗則 graceful fallback 原本行為
- [2026-07-14T20:09:31.122Z] user=509424983 query="Rich Message streaming 升級評估（2026-07-08）：grammY 1.44" deleted=0 token=forget-a985645a-1

- [2026-07-14T20:09:31.176Z] user=509424983 query="草稿串流(Path A)採三階段生命週期" deleted=1 token=forget-e715bc7c-1
    - [f_f3dd1f] [2026-07-10T20:32:24.955Z] telegram-kiro-bridge 的 Rich Message 草稿串流(Path A)採三階段生命週期:先 sendMessageDraft 送空草稿顯示「Thinking…」,再用 sendRichMessageDraft 串流更新草稿內容,最後以 sendRichMessage 定稿;完整規格見 SPEC-draft-streaming.md。
- [2026-07-14T20:09:31.303Z] user=509424983 query="session 移植的決策：選方案 A（只做 resume 不做 /session UI）" deleted=0 token=forget-b8b3d9e1-1

- [2026-07-14T20:09:41.859Z] user=509424983 query="skill 說明裡明寫：程式碼裡完全沒有點送出鈕的路徑" deleted=1 token=forget-1cd609d4-1
    - [f_f6476c] [2026-07-14T02:13:49.359Z] skill 說明裡明寫：程式碼裡完全沒有點送出鈕的路徑，不會、也不能自動送出申請
- [2026-07-14T20:09:41.931Z] user=509424983 query="這是刻意的保守設計（skill 描述提到對「會產生真實外部紀錄的自動化」採保守策略）" deleted=0 token=forget-e07162af-1

- [2026-07-14T20:09:42.041Z] user=509424983 query="setup-local-notebooklm-mcp.mjs 目標 CLI 有架構性錯配" deleted=0 token=forget-33490f92-1

- [2026-07-14T20:09:51.059Z] user=509424983 query="cloudflared quick tunnel 在使用者網路環境下需要超過 15 秒" deleted=1 token=forget-cd7607e6-1
    - [f_9f698d] [2026-07-13T02:39:12.918Z] cloudflared quick tunnel 在使用者網路環境下需要超過 15 秒才能取得 trycloudflare.com URL（12 秒後仍停在 Requesting new quick Tunnel），status-tunnel.ts timeout 已從 15s 改為 30s
- [2026-07-14T20:09:51.135Z] user=509424983 query="Cloudflared Quick Tunnel 不支援 SSE" deleted=1 token=forget-5d10aa25-1
    - [f_42843e] [2026-07-13T02:39:12.928Z] Cloudflared Quick Tunnel 不支援 SSE（Server-Sent Events）——bridge 的 /status Mini App 即時串流 endpoint（/api/status/:taskId/stream）在 quick tunnel 下不可用，需改用 polling 或升級 named tunnel
- [2026-07-14T20:09:51.259Z] user=509424983 query="使用者機器已安裝 cloudflared 2026.7.1" deleted=1 token=forget-1b23f894-1
    - [f_72a155] [2026-07-13T02:23:57.615Z] 使用者機器已安裝 cloudflared 2026.7.1（winget install Cloudflare.cloudflared），供 status-server Mini App HTTPS tunnel 使用
- [2026-07-14T20:40:37.206Z] user=509424983 query="Rich Message streaming 升級評估（2026-07-08）：grammY 1.44 已完整支援 Bot API 10.1" deleted=1 token=forget-a985645a-1
    - [f_a0d9ac] [2026-07-08T08:35:28.183Z] telegram-kiro-bridge 的 Rich Message streaming 升級評估（2026-07-08）：grammY 1.44 已完整支援 Bot API 10.1（sendRichMessage + sendRichMessageDraft type-safe）；官方 @grammyjs/stream v1.1.0 plugin 封裝 draft lifecycle（draft_id 管理 + 30 秒 heartbeat + 最終 persist）；現有 telegram-rich-renderer.ts 的實作不完整（走 editMessageText 夾帶 rich_message 參數而非真 draft API）；正確升級路線：npm install @grammyjs/stream → bot.use(stream()) → run-prompt.ts 把 push-based onUpdate 轉 async iterator 接 ctx.replyWithMarkdownStream → 預估 1.5-2 小時；主要收益是 sendRichMessageDraft 不受 editMessageText 的 429 限流、可移除 format-html.ts 的 Markdown escape 邏輯、支援原生表格/程式碼高亮/LaTeX/tg-thinking 動畫
- [2026-07-14T20:40:37.306Z] user=509424983 query="選方案 A（只做 resume 不做 /session UI），方案 B（SessionStore+UI）等 A 跑穩再議" deleted=0 token=forget-b8b3d9e1-1

- [2026-07-14T20:40:37.430Z] user=509424983 query="這是刻意的保守設計（skill 描述提到對「會產生真實外部紀錄的自動化」採保守策略）" deleted=1 token=forget-e07162af-1
    - [f_f95ab5] [2026-07-14T02:13:49.369Z] 這是刻意的保守設計（skill 描述提到對「會產生真實外部紀錄的自動化」採保守策略），避免加班單這種會產生公司內部真實紀錄的動作被誤觸發送出
- [2026-07-14T20:40:49.123Z] user=509424983 query="選方案 A（只做 resume 不做 /session UI），方案 B（SessionStore+UI）等 A 跑穩再議" deleted=0 token=forget-b8b3d9e1-1

- [2026-07-14T20:41:44.442Z] user=509424983 query="選方案 A（只做 resume 不做 /session UI）" deleted=0 token=forget-b8b3d9e1-1

- [2026-07-14T20:42:58.741Z] user=509424983 query="session 移植的決策：選方案 A（只做 resume 不做 /session UI）" deleted=1 token=forget-b8b3d9e1-1
    - [f_12d648] [2026-07-07T11:48:47.046Z] 使用者對 session 移植的決策：選方案 A（只做 resume 不做 /session UI），方案 B（SessionStore+UI）等 A 跑穩再議；理由是 restart 連續性 + idle 殺 process 省記憶體最實、避免與 goal/MoA/relay 單 session 假設的互動風險
- [2026-07-15T20:09:23.790Z] user=509424983 query="Rich Messages 升級 PoC 裁決" deleted=0 token=forget-7c4264b2-1

- [2026-07-15T20:09:23.841Z] user=509424983 query="[WS] completed: ctx 統計行加上 agent/model/effort" deleted=1 token=forget-358792e8-1
    - [f_5eeea7] [2026-07-15T01:56:01.934Z] [WS] completed: ctx 統計行加上 agent/model/effort 後綴（5 檔改動：types.ts/acp.ts/direct.ts/run-prompt.ts/index.ts/relay.ts，tsc 通過）
- [2026-07-15T20:09:23.901Z] user=509424983 query="session resume 待辦：生產 bridge .env 加 ACP_SESSION_RESUME" deleted=0 token=forget-5a757299-1

- [2026-07-15T20:09:31.132Z] user=509424983 query="placeholder guard 漏排除 useDraftMode" deleted=0 token=forget-f675afca-1

- [2026-07-15T20:09:37.519Z] user=509424983 query="README 已於 2026-07-07 補齊文檔並 push" deleted=0 token=forget-69547103-1

- [2026-07-15T20:09:37.553Z] user=509424983 query="check-moa 壞測試待辦已完成" deleted=0 token=forget-4d6daaec-1

- [2026-07-15T20:09:44.767Z] user=509424983 query="README.md 已拆分重構（2026-07-13，commit 80e847b）" deleted=0 token=forget-8871c3c4-1

- [2026-07-15T20:09:44.823Z] user=509424983 query="Telegram Bot API 9.6（2026-04-03）Managed Bots" deleted=0 token=forget-12ce4b46-1

- [2026-07-15T20:09:55.446Z] user=509424983 query="session resume 已知 cosmetic 待補：resume 後 /context 顯示 preamble 0 chars" deleted=0 token=forget-e09f6458-1

- [2026-07-15T20:09:55.495Z] user=509424983 query="疑似有功能宣稱與實作脫節：README 提到的「14類錯誤分類器" deleted=1 token=forget-79ab485f-1
    - [f_46533c] [2026-07-13T11:39:16.117Z] telegram-kiro-bridge 疑似有功能宣稱與實作脫節：README 提到的「14類錯誤分類器（ms-error-classification）」只在 docs/SPEC-self-improving-agent.md 出現，src/ 無對應程式碼、default-skills/ 未安裝此 skill，尚未確認是否要處理
- [2026-07-15T20:09:55.570Z] user=509424983 query="/dev-review workflow 完成後的通知沒有送達" deleted=1 token=forget-792f57a9-1
    - [f_6f4462] [2026-07-14T01:00:58.589Z] 使用者反映 /dev-review workflow 完成後的通知沒有送達（兩次都沒收到），但審查本身有成功執行並落地 artifacts——bridge/workflow 完成通知管線疑似有問題，待查
- [2026-07-15T20:10:01.408Z] user=509424983 query="SELF_EVAL 設計規格 P1-design-spec.md 的 CLAUDE.md 方法論小節仍欠" deleted=1 token=forget-74214b7d-1
    - [f_f762eb] [2026-07-14T01:00:58.598Z] SELF_EVAL 設計規格 P1-design-spec.md 的 CLAUDE.md 方法論小節仍欠一次 Section 12.6 R-2 異源 cross-source review（程式碼審查已完成，文字本身的方法論審查未做），使用者尚未決定是否執行
- [2026-07-16T20:05:14.971Z] user=509424983 query="刷卡時間欄位回填是綁在日期選擇器的 onchange 事件上" deleted=1 token=forget-8b0fec3a-1
    - [f_35a6e8] [2026-07-16T20:05:01.345Z] 因為 UOF 表單的刷卡時間欄位回填是綁在日期選擇器的 onchange 事件上，直接用 JavaScript/frame.fill 塞值不會觸發 AJAX 查詢，所以 uof_form.py 改成先 fill 塞值保底、再點日曆 icon 選日期觸發真正 onchange（排除純用 fill 因為刷卡時間欄位會保持空白，且加了 try/except fallback 避免日曆 DOM selector 猜錯時整個腳本失敗）
- [2026-07-16T20:08:06.822Z] user=509424983 query="因為 UOF 表單的刷卡時間欄位回填是綁在日期選擇器的 onchange 事件上，直接用 JavaScript/frame.fill" deleted=1 token=forget-c72eeeeb-1
    - [f_35a6e8] [2026-07-16T20:05:21.272Z] 因為 UOF 表單的刷卡時間欄位回填是綁在日期選擇器的 onchange 事件上，直接用 JavaScript/frame.fill 塞值不會觸發 AJAX 查詢，所以 uof_form.py 改成先 fill 塞值保底、再點日曆 icon 選日期觸發真正 onchange（排除純用 fill 因為刷卡時間欄位會保持空白，且加了 try/except fallback 避免日曆 DOM selector 猜錯時整個腳本失敗）
- [2026-07-16T20:20:53.088Z] user=509424983 query="notebooklm-routing.json 過時路徑引用（從 ${AGENT_CONFIG_DIR} 改為 ${MEMORY_DIR}/config/，commit e29fafc）" deleted=1 token=forget-4a1b5230-1
    - [f_169cb4] [2026-07-13T12:11:37.930Z] AI-canonical 的 ms-portable-skill-authoring skill 正本已修正 notebooklm-routing.json 過時路徑引用（從 ${AGENT_CONFIG_DIR} 改為 ${MEMORY_DIR}/config/，commit e29fafc）
- [2026-07-16T20:20:54.279Z] user=509424983 query="uk-slot-pitfalls wiki 已回灌 5 條 codegen 來源踩坑" deleted=0 token=forget-9afe0f39-1

- [2026-07-16T20:21:14.791Z] user=509424983 query="先前「5 項仍未修屬同事責任」的狀態已過時" deleted=0 token=forget-a15f78a4-1

- [2026-07-18T20:18:09.912Z] user=509424983 query="bridge-acp.md 的 sources 欄位仍混有一批疑似編造的假 fact ID" deleted=1 token=forget-b8820631-1
    - [f_5e81d2] [2026-07-16T20:34:00.040Z] telegram-kiro-bridge 的 wiki 頁 bridge-acp.md 的 sources 欄位仍混有一批疑似編造的假 fact ID（如 f_228abc 系列）尚未清理，是已知的 wiki-reference 保護部分失效風險，待下輪 wikilint/factlint 處理
