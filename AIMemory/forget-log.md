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
- [2026-07-19T20:20:59.112Z] user=509424983 query="表格未反映已知的二次確認彈窗誤判 bug" deleted=1 token=forget-ec646cc9-1
    - [f_824a2a] [2026-07-18T20:31:18.716Z] telegram-kiro-bridge 的 igs-uof SKILL.md「填單專屬錯誤」表格未反映已知的二次確認彈窗誤判 bug（f_02e1bb），submit_rejected 狀態可能誤導使用者以為加班單未送出而重複操作，待補充說明
- [2026-07-19T20:21:05.008Z] user=509424983 query="SKILL.md 已補上 submit_rejected 誤判二次確認彈窗的說明" deleted=1 token=forget-2d75dd5a-1
    - [f_ac807a] [2026-07-19T09:11:28.458Z] telegram-kiro-bridge 的 igs-uof SKILL.md 已補上 submit_rejected 誤判二次確認彈窗的說明（先前待辦已完成）
- [2026-07-19T20:21:49.518Z] user=509424983 query="統計永遠零筆——是統計口徑缺口非真低使用率，待修正 meta-prompt" deleted=1 token=forget-1f12c8ee-1
    - [f_6cd081] [2026-07-18T20:31:18.716Z] telegram-kiro-bridge 的 claude-mem-curate 已接成 /dream 第 14 步每日自動執行，但因該步驟 meta-prompt 未要求輸出 <<SKILL_USED:...>>，導致 skill-usage.json 的 use_count 統計永遠零筆——是統計口徑缺口非真低使用率，待修正 meta-prompt
- [2026-07-19T20:22:30.054Z] user=509424983 query="git status 顯示 src 兩檔改動尚未 commit，README.md 另有既有未提交改動（不相關，勿混）" deleted=0 token=forget-4c8e291f-1

- [2026-07-20T23:25:58.358Z] user=509424983 query="uk_slot_template 有 4 個本地 commit 未 push" deleted=0 token=forget-254aa623-1

- [2026-07-22T20:17:20.910Z] user=509424983 query="handleDailyLog 在「今日無 session 記錄」分支原本直接用 ctx.reply()" deleted=1 token=forget-4131a0cc-1
    - [f_a18e55] [2026-07-22T20:16:48.619Z] 因為 dream.ts 的 stepResults 只認 session.buffer 差異或結構化回傳值來判斷 summary，而 handleDailyLog 在「今日無 session 記錄」分支原本直接用 ctx.reply() 回覆（不寫入 buffer），導致該步驟被誤記成 (no output) 並被後續蒸餾誤判為 High Priority 失敗，所以把該分支改為回傳結構化 DreamStepResult（排除同時修改 session.get 失敗分支，因為本次未觸發、屬範圍外）
- [2026-07-25T02:19:00.225Z] user=509424983 query="topics.json 從 21 個增至 22 個" deleted=1 token=forget-e1d3cfe9-1
    - [f_ae3a52] [2026-07-22T21:49:00.863Z] telegram-kiro-bridge 於 2026-07-22 新增 bridge-dream topic（從 bridge-project 拆出）：涵蓋 /dream 排程框架本身（dream.json 執行機制、claude-mem-curate 接入沿革），topics.json 從 21 個增至 22 個
- [2026-07-27T05:59:02.679Z] user=509424983 query="Not logged in" deleted=0 token=forget-32df4c3b-1

- [2026-07-28T20:08:18.292Z] user=509424983 query="[WS] task: 把 claude-mem-curate 精選流程接成" deleted=0 token=forget-77531c79-1

- [2026-07-28T20:08:18.463Z] user=509424983 query="[WS] next_action: 重啟後確認 bridge 正常啟動且新 dist 生效" deleted=0 token=forget-e81aebb2-1

- [2026-07-28T20:08:18.614Z] user=509424983 query="session resume 待辦：生產 bridge .env 加 ACP_SESSION_RESUME" deleted=0 token=forget-5a757299-1

- [2026-07-28T20:08:25.360Z] user=509424983 query="session resume 已知 cosmetic 待補：resume 後 /context 顯示 preamble 0 chars" deleted=0 token=forget-e09f6458-1

- [2026-07-28T20:08:25.487Z] user=509424983 query="[WS] key_refs: 改動檔案 src/commands/dream.ts" deleted=0 token=forget-4c8e291f-1

- [2026-07-28T20:08:25.751Z] user=509424983 query="[WS] completed: 已新增 handleClaudeMemCurate" deleted=0 token=forget-a4cf51ac-1

- [2026-07-28T20:08:34.604Z] user=509424983 query="dream 步驟文件（README/usage-guide.html）與本機實際" deleted=1 token=forget-275f901a-1
    - [f_b91398] [2026-07-18T20:31:18.716Z] telegram-kiro-bridge 的 /dream 步驟文件（README/usage-guide.html）與本機實際 ~/.kiro/dream.json 不一致：文件寫的 sessionreflect/specialistreflect 步驟並未出現在本機設定檔，實際存在的 claudememcurate/docupdate 步驟兩份文件都未記錄，待對齊
- [2026-07-28T20:08:34.816Z] user=509424983 query="uk_slot_template 先前提及的 4 個本地未 push commit" deleted=0 token=forget-8bba4cc9-1

- [2026-07-28T20:08:45.739Z] user=509424983 query="共享知識庫（Shared Knowledge）目錄於 2026-07-18 dream run 出現 /sharedsync 失敗" deleted=0 token=forget-63e91a91-1

- [2026-07-28T20:08:45.846Z] user=509424983 query="skill-usage.json 追蹤檔案孤兒化：vc-uof-hours entry 仍指向" deleted=0 token=forget-ef9823f2-1

- [2026-07-28T20:08:50.229Z] user=509424983 query="2026-07-26 檢查時處於未登入狀態" deleted=0 token=forget-32df4c3b-1

- [2026-07-28T22:06:14.980Z] user=509424983 query="[WS] task: 把 claude-mem-curate 精選流程接成 /dream 第 14 步" deleted=1 token=forget-77531c79-1
    - [f_e1f99f] [2026-07-16T13:13:25.950Z] [WS] task: 把 claude-mem-curate 精選流程接成 /dream 第 14 步，讓每日 04:00 自動觸發（原本只能手動觸發）
- [2026-07-28T22:06:15.063Z] user=509424983 query="[WS] next_action: 重啟後確認 bridge 正常啟動且新 dist 生效" deleted=1 token=forget-e81aebb2-1
    - [f_e2d60b] [2026-07-16T13:13:35.726Z] [WS] next_action: 重啟後確認 bridge 正常啟動且新 dist 生效，然後詢問使用者是否要 git commit 這次 claudememcurate 改動（只 add src/commands/dream.ts + src/index.ts，不要連帶 commit README.md 既有改動）
- [2026-07-28T22:06:15.196Z] user=509424983 query="session resume 待辦：生產 bridge .env 加 ACP_SESSION_RESUME=true" deleted=1 token=forget-5a757299-1
    - [f_86bdbb] [2026-07-07T11:48:47.056Z] session resume 待辦：生產 bridge .env 加 ACP_SESSION_RESUME=true 重啟後做手動 e2e；首次啟用需觀察 replay 時序——真 adapter 若在 session/load 回應後才補送 replay update 有 token 重放風險，保守 fallback 方案在計畫檔風險 #1
- [2026-07-28T22:06:15.345Z] user=509424983 query="session resume 已知 cosmetic 待補：resume 後 /context 顯示 preamble 0 chars" deleted=0 token=forget-e09f6458-1

- [2026-07-28T22:06:31.921Z] user=509424983 query="session resume 已知 cosmetic 待補：resume 後 /context 顯示 preamble 0 chars" deleted=1 token=forget-e09f6458-1
    - [f_daf156] [2026-07-07T13:26:02.669Z] session resume 已知 cosmetic 待補：resume 後 /context 顯示 preamble 0 chars
- [2026-07-28T22:06:40.961Z] user=509424983 query="[WS] completed: 已新增 handleClaudeMemCurate" deleted=1 token=forget-a4cf51ac-1
    - [f_9b9689] [2026-07-16T13:13:27.920Z] [WS] completed: 已新增 handleClaudeMemCurate（src/commands/dream.ts，仿 docupdate 的 meta-prompt 模式）、註冊進 COMMAND_HANDLERS（src/index.ts）、在 C:\Users\jiunchiwang\.kiro\dream.json 插入 claudememcurate 步驟（memorytoskill 之後、topicreview 之前）；tsc --noEmit 過、npm run build 過、check-dream.mjs 24 項 smoke test 全過、手動 load 實際 dream.json 確認 14 步解析正確無 warning
- [2026-07-28T22:06:41.007Z] user=509424983 query="共享知識庫（Shared Knowledge）目錄於 2026-07-18 dream run 出現 /sharedsync 失敗" deleted=1 token=forget-63e91a91-1
    - [f_235eef] [2026-07-18T20:31:18.716Z] telegram-kiro-bridge 的共享知識庫（Shared Knowledge）目錄於 2026-07-18 dream run 出現 /sharedsync 失敗：git status --porcelain 回報 not a git repository，需確認路徑設定或 .git 是否遺失
- [2026-07-28T22:06:41.100Z] user=509424983 query="[WS] key_refs: 改動檔案 src/commands/dream.ts" deleted=1 token=forget-4c8e291f-1
    - [f_48b44d] [2026-07-16T13:13:34.612Z] [WS] key_refs: 改動檔案 src/commands/dream.ts、src/index.ts、~/.kiro/dream.json（14 步：sharedsync→dailylog→memorytoskill→claudememcurate→topicreview→wikisync→factlint→wikilint→skilllint→docupdate→specialistreview→artifactcleanup→backup→restart）；git status 顯示 src 兩檔改動尚未 commit，README.md 另有既有未提交改動（不相關，勿混）
- [2026-07-28T22:06:45.197Z] user=509424983 query="2026-07-26 檢查時處於未登入狀態" deleted=1 token=forget-32df4c3b-1
    - [f_b283c9] [2026-07-26T12:27:52.448Z] telegram-kiro-bridge 主機的 kiro-cli（2.13.0，路徑 C:\Users\jiunchiwang\AppData\Local\Kiro-Cli\kiro-cli.exe）於 2026-07-26 檢查時處於未登入狀態（kiro-cli whoami 回報 Not logged in），headless 執行 kiro-cli chat --list-models 會卡在「Opening auth portal」無窮重試迴圈，需使用者手動互動式 kiro-cli login 重新登入才能恢復（含 vc-kiro-delegate 委派功能）
- [2026-07-29T20:06:34.817Z] user=509424983 query="kiro-cli 登入狀態已於 2026-07-27 恢復正常" deleted=0 token=forget-0761a95e-1

- [2026-07-30T20:10:30.172Z] user=509424983 query="P3 recon 完成" deleted=0 token=forget-6c93085e-1

- [2026-07-30T20:10:34.324Z] user=509424983 query="check-moa 壞測試待辦已完成" deleted=0 token=forget-4d6daaec-1

- [2026-07-30T20:10:39.592Z] user=509424983 query="已確認 redkilin/ai-shared-knowledge 是 upstream 專案作者" deleted=0 token=forget-12317354-1

- [2026-07-30T20:10:43.935Z] user=509424983 query="使用者已建立新的 GitHub private repo jiunchiwang/ai-shared-knowledge" deleted=0 token=forget-08d8a036-1

- [2026-07-30T20:10:48.860Z] user=509424983 query="Clash of Olympus 的 spec-to-impl 三步驟已完成" deleted=0 token=forget-d589d5ba-1

- [2026-07-30T22:17:10.211Z] user=509424983 query="uk_917 開發進度（2026-07-07）：M0a 起專案完成且驗收通過" deleted=0 token=forget-3edbab99-1

- [2026-07-30T22:17:10.451Z] user=509424983 query="Clash of Olympus 的 spec-to-impl 三步驟已完成（2026-07-09）" deleted=0 token=forget-d589d5ba-1

- [2026-07-30T22:17:10.698Z] user=509424983 query="2026-07-11 已完成 bridge-project wiki 頁拆分" deleted=0 token=forget-fb896823-1

- [2026-07-30T22:18:11.140Z] user=509424983 query="uk_917 開發進度（2026-07-07）：M0a 起專案完成且驗收通過" deleted=1 token=forget-3edbab99-1
    - [f_7a309c] [2026-07-07T07:52:13.393Z] uk_917 開發進度（2026-07-07）：M0a 起專案完成且驗收通過（ReelDevTool 5 欄假盤驗轉輪），dev-spec.md + SPEC.md 已產出，repo 全本地無 remote；ShortGameName 未定（scene 佔位 ar2es，等 M0b）、機率文件 {} 值未拿到
- [2026-07-30T22:18:11.348Z] user=509424983 query="Clash of Olympus 的 spec-to-impl 三步驟已完成（2026-07-09）" deleted=1 token=forget-d589d5ba-1
    - [f_d03f34] [2026-07-09T19:00:02.536Z] Clash of Olympus 的 spec-to-impl 三步驟已完成（2026-07-09）：docs/spec（80圖）+ dev-spec.md（1🔴 VS Feature + 6🟡 + 8🟢）+ SPEC.md（25任務 M0a~M4）+ AI.md；下一步是 M0a 起專案，需先確認 GameId 和 Proto 狀態
- [2026-07-30T22:18:11.597Z] user=509424983 query="2026-07-11 已完成 bridge-project wiki 頁拆分" deleted=1 token=forget-fb896823-1
    - [f_a8bb58] [2026-07-11T03:19:33.619Z] 2026-07-11 已完成 bridge-project wiki 頁拆分：新建 bridge-memory（記憶與維運，78 行）與 bridge-specialist（分身系統，54 行）兩頁，主頁從 277 行縮到 80 行（含 6 子頁索引）；topics.json 新增 bridge-memory（34 keyword）與 bridge-specialist（14 keyword）規則插在 bridge-project 之前，既有 shard 實體重分等下次 topicreview
- [2026-07-31T06:25:17.676Z] user=509424983 query="run-prompt 的 finally 來不及跑，所以每次 restart 都會留孤兒" deleted=1 token=forget-41a43287-1
    - [f_878f84] [2026-07-31T06:09:00.728Z] status bubble 孤兒的真正主要來源是 /restart 與 <<RESTART>>（session-extract.ts 的 process.exit），不是 SIGKILL——<<RESTART>> 由 agent 在 turn 進行中發出，run-prompt 的 finally 來不及跑，所以每次 restart 都會留孤兒；原先把它判成「硬殺才會發生的邊角」是錯的，是 grep 全庫 process.exit 逐條分析才挖出來
- [2026-07-31T20:35:07.029Z] user=509424983 query="[WS]" deleted=8 token=forget-e8e2786e-8
    - [f_8fd601] [2026-07-31T10:58:18.766Z] [WS] task: 診斷 draft streaming 症狀「工具的訊息變化時，原本的對話會消失再從頭重跑」的根因（2026-07-31 未結案）
    - [f_1674f1] [2026-07-31T10:58:21.299Z] [WS] completed: 已加 opt-in draft 診斷層（新增 src/draft-diag.ts + config.tgDraftDiag + status-channel.ts 的 onApiCall 注入 + run-prompt.ts 6 個觀測點 + .gitignore 加 logs/），tsc exit 0、fast tier 93/93 過、check-draft-streaming 12 支過，.env:238 已設 TG_DRAFT_DIAG=1；這批尚未 commit
    - [f_0cacc3] [2026-07-31T10:58:28.686Z] [WS] blocked: 根因未定案，卡在需要 runtime log 才能判別 H1（status bubble 的 editMessageText 也會清掉 live draft）vs H2（draft ~30s TTL 在長工具/rate limit 期間過期）——兩者在 Bot API 回傳值上都是「成功」，官方文件查不到 editMessageText 是否清 draft
    - [f_b6ff51] [2026-07-31T10:58:32.116Z] [WS] key_refs: 診斷輸出 logs/draft-diag.jsonl（欄位 seq/at/ms/event/sinceLastMs/reason）；候選修法在 src/run-prompt.ts 的 editNowInner——目前順序是 trySendDraft 然後 statusChannel.update()，若 H1 成立就把 update() 移到 trySendDraft 之前讓 draft 永遠是最後動作；判別法：status.edit 後緊跟重播=H1，draft.send 的 sinceLastMs>30000=H2
    - [f_aeeea3] [2026-07-31T10:58:38.960Z] [WS] next_action: 重啟後請使用者做幾輪「含多次工具呼叫」的對話觸發重播，然後讀 logs/draft-diag.jsonl，比對 status.edit 與 draft.send 的時序交錯定案 H1 或 H2，再改；診斷完要把 .env 的 TG_DRAFT_DIAG 關回 0
    - [f_91d132] [2026-07-31T11:31:53.673Z] [WS] task: 驗證 draft streaming 修法（commit 4276f08）是否真的消滅「工具訊息變化時，已串完的回覆整段消失再從頭重播」
    - [f_cacf97] [2026-07-31T11:32:03.630Z] [WS] completed: draft 重播根因已用 logs/draft-diag.jsonl 定案為 H1（status bubble 的 editMessageText 也會清掉 live draft），消去法排除 H2/限流/降級/lateCreate；修法 A 已實作並 commit 4276f08（status-channel 的 update() 改回傳「是否發出過 chat 層寫入」、run-prompt 把 status.update() 移到 draft 送出之前、送出條件加 || statusWrote、補送幀記 reason:"status-restore"）；tsc 零診斷、fast tier 93/93、4 種突變逐一驗證新斷言有效
    - [f_44e77d] [2026-07-31T11:32:05.904Z] [WS] next_action: 重啟後做幾輪「含多次工具呼叫」的對話，然後讀 logs/draft-diag.jsonl 找 reason:"status-restore" 幀 —— 有該幀且症狀消失=修法成立；有該幀但症狀仍在=H1 錯需換方向（這是刻意設計的否證條件）；同時確認沒有 draft.skip reason=rateLimit（修法會增加 API 呼叫量）。驗完把 .env 的 TG_DRAFT_DIAG 關回 0，push 前先派 Fable5 覆核 4276f08
- [2026-07-31T21:24:28.748Z] user=509424983 query="真因是兩個 consumer 搶同一個 watermark" deleted=1 token=forget-473d580a-1
    - [f_32d759] [2026-07-31T21:02:18.933Z] AIMemory 的 claude-mem curate 反覆「空轉重掃同一批」（07-22 起 6 次）根因不是 shortlist 未清空：產生端 G:\AI\AI-canonical\tools\ingest-claude-mem.mjs 本來就覆寫檔案並推進 watermark，真因是兩個 consumer 搶同一個 watermark——daily-claudemem.ps1（排程）是 extractor+curate 成對，而 bridge /dream 的 /claudememcurate（src/commands/dream.ts:484）只 curate 不跑 extractor，因此永遠讀到排程那輪已處理完的殘檔。另：同一 live session 當場 remember() 過的內容會再變成 claude-mem decision 觀察，curate 去重後寫 0 是結構性正常而非故障。
- [2026-08-01T20:12:51.476Z] user=509424983 query="wiki 新增兩頁 concepts/verification-diagnosis.md" deleted=1 token=forget-3e603940-1
    - [f_2d800f] [2026-07-31T20:47:31.616Z] wiki 新增兩頁 concepts/verification-diagnosis.md 與 concepts/bridge-smoke-gate.md（2026-08-01），index.md Total pages 34→36
- [2026-08-01T20:12:51.571Z] user=509424983 query="先前「5 項仍未修屬同事責任」的狀態已過時" deleted=0 token=forget-a15f78a4-1

- [2026-08-01T20:13:07.840Z] user=509424983 query="此問題已解決" deleted=0 token=forget-8bba4cc9-1

- [2026-08-02T01:36:36.874Z] user=509424983 query="便宜的 Gemini/DeepSeek/local" deleted=1 token=forget-79173d10-1
    - [f_69d516] [2026-08-02T00:33:50.805Z] 使用者想要 /dream 指令能指定執行時用的 model，而非一律用當前 session 的 model（場景：日常對話用 Opus、/dream 用便宜的 Gemini/DeepSeek/local）
- [2026-08-02T05:41:28.368Z] user=509424983 query="[WS] task: telegram-kiro-bridge draft 重播第二成因" deleted=1 token=forget-41b37769-1
    - [f_bebd71] [2026-08-01T02:05:04.551Z] [WS] task: telegram-kiro-bridge draft 重播第二成因（token 隱藏縮回）已修復並 commit bd068e1，正在重啟 bridge 讓修復生效
- [2026-08-02T05:41:37.113Z] user=509424983 query="Telegram live draft 的兩條硬規則（bridge 實證 2026-07-31）" deleted=1 token=forget-9cd8c795-1
    - [f_a8b21e] [2026-07-31T05:18:03.742Z] Telegram live draft 的兩條硬規則（bridge 實證 2026-07-31）：任何一般訊息送進該 chat 就會立即清掉 live draft，且 client 的 draft 更新動畫是「長度差」語意（只淡入尾端新增字元）——前一幀狀態一失去或內容在頭部插入，就只能整段重播。設計 draft streaming 時任何 sendMessage 的時機都要當成 draft 的破壞點來排程。
- [2026-08-02T05:41:41.342Z] user=509424983 query="2026-07-13 同步 upstream（redkilin）relay 多 peer 系統" deleted=0 token=forget-190ad517-1

- [2026-08-02T05:41:45.845Z] user=509424983 query="2026-07-15 完成一次 upstream（redkilin/telegram-kiro-bridge）同步：merge 19 個上游" deleted=0 token=forget-68fff6d1-1

- [2026-08-02T05:41:49.971Z] user=509424983 query="2026-07-16 完成一次 upstream 同步：merge 進 MCP-first action domain" deleted=0 token=forget-ff3132c1-1

- [2026-08-02T05:41:55.707Z] user=509424983 query="docs/usage-guide.html 已於 2026-07-17 補上 bridge-actions MCP 說明章節" deleted=0 token=forget-910f49eb-1

- [2026-08-02T05:42:00.709Z] user=509424983 query="docs/usage-guide.html 已於 2026-07-19 補上 /refresh-routing 指令的別名" deleted=0 token=forget-26debaf2-1

- [2026-08-02T05:42:07.090Z] user=509424983 query="kiro-cli 登入狀態已於 2026-07-27 恢復正常" deleted=0 token=forget-0761a95e-1

- [2026-08-02T05:42:11.516Z] user=509424983 query="README.md 已於 2026-07-16 補上 bridge-actions MCP 說明" deleted=0 token=forget-c76825be-1

- [2026-08-02T05:42:17.055Z] user=509424983 query="/sharedsync 功能已修復並驗證可正常 push/pull" deleted=0 token=forget-11058436-1

- [2026-08-02T20:18:23.340Z] user=509424983 query="docs/SPEC-token-mcp-migration.md 連結" deleted=0 token=forget-c76825be-1

- [2026-08-02T20:18:26.843Z] user=509424983 query="usage-guide.html 已於 2026-07-17 補上 bridge-actions MCP 說明章節" deleted=0 token=forget-910f49eb-1

- [2026-08-02T20:18:33.022Z] user=509424983 query="已於 2026-07-19 補上 /refresh-routing 指令的別名" deleted=0 token=forget-26debaf2-1

- [2026-08-02T20:18:40.981Z] user=509424983 query="先前 not a git repository 的問題已解決" deleted=0 token=forget-11058436-1

- [2026-08-02T20:18:47.185Z] user=509424983 query="vc-kiro-delegate 委派功能可用（覆蓋 2026-07-26 的未登入記錄）" deleted=0 token=forget-0761a95e-1

- [2026-08-02T20:18:57.595Z] user=509424983 query="merge 19 個上游 commit" deleted=0 token=forget-68fff6d1-1

- [2026-08-04T20:07:47.585Z] user=509424983 query="claude-mem-shortlist.md 有已知問題" deleted=0 token=forget-47ff8f22-1

- [2026-08-05T20:32:37.331Z] user=509424983 query="AIMemory topic 分類於 2026-08-01 從 22 增為 24" deleted=1 token=forget-ed0bd29e-1
    - [f_d4c3fe] [2026-07-31T20:47:31.616Z] AIMemory topic 分類於 2026-08-01 從 22 增為 24：新增 verification-diagnosis（跨專案驗證/診斷方法論）與 bridge-smoke-gate（bridge 測試閘門與建置），兩者刻意排在 bridge-project 之前、其他細類之後，只從那個 catch-all topic 抽走 facts；misc 由 13 降到 1、bridge-project 由 76 降到 55
- [2026-08-05T20:32:39.046Z] user=509424983 query="接受 claude-sonnet-5 作為合法 model id 並原樣回報" deleted=1 token=forget-ed99ff8c-1
    - [f_ace6e8] [2026-08-02T02:45:55.634Z] claude-agent-acp 接受 claude-sonnet-5 作為合法 model id 並原樣回報（不解析成其他 canonical id），2026-08-02 以 scripts/check-acp-model-effort.mjs 實際 spawn adapter 驗證；同 adapter 公告的合法值含 default / opus[1m] / sonnet
- [2026-08-05T20:32:41.057Z] user=509424983 query="/sharedsync 功能已修復並驗證可正常 push/pull" deleted=0 token=forget-11058436-1

- [2026-08-05T20:32:49.499Z] user=509424983 query="index.ts 的全域 unhandledRejection handler 會 process.exit(1)" deleted=0 token=forget-bcddd99f-1

- [2026-08-05T20:32:53.526Z] user=509424983 query="對 README 拆分+roadmap更新兩件事確認選擇拆兩個 commit" deleted=0 token=forget-de23ae5f-1

- [2026-08-06T06:33:52.652Z] user=509424983 query="走 bridge AcpClient 的 spawn 路徑會 exit 1 且無 stderr" deleted=1 token=forget-1a00be09-1
    - [f_346178] [2026-08-06T06:25:25.550Z] Codex 的 ACP adapter 有兩個套件且行為不同：@zed-industries/codex-acp 已 deprecated（npm 明寫 "replaced by @agentclientprotocol/codex-acp"，最後更新 2026-06-23，最新 0.16.0；這台機器全域裝的是 0.15.0），維護中的是 @agentclientprotocol/codex-acp（1.1.9，upstream redkilin 的預設命令就是它）。2026-08-06 raw ACP probe 實測差異：舊版 currentModelId 用斜線 gpt-5.5/medium、effort 只有 low/medium/high/xhigh、sessionCapabilities 整塊缺席；新版 1.1.7 用方括號 gpt-5.6-terra[medium]、effort 多了 max/ultra、且宣告 resume/list/close/delete/additionalDirectories（對 bridge 的 session resume gate 有意義）。兩者都在已登入時回非空 authMethods，所以 bridge 的 authMethodsImplyLoggedOut codex 例外對兩個套件都必要。⚠️ 換套件必須同時改 pin：gpt-5.5 在新版清單裡不存在。⚠️ 未解：`npx -y @agentclientprotocol/codex-acp` 直接 spawn 正常，但走 bridge AcpClient 的 spawn 路徑會 exit 1 且無 stderr，根因未查明——換命令前要先確認，否則 backend 會直接死。
- [2026-08-06T11:01:44.699Z] user=509424983 query="探針會撞 401 Unauthorized" deleted=0 token=forget-58cddbee-1

- [2026-08-06T11:02:48.643Z] user=509424983 query="探針會撞 401 Unauthorized" deleted=0 token=forget-58cddbee-1

- [2026-08-06T11:04:19.858Z] user=509424983 query="探針會撞 401 Unauthorized" deleted=0 token=forget-58cddbee-1

- [2026-08-09T20:24:20.518Z] user=509424983 query="外部 repo cc-session-reader（Mapleeeeeeeeeee，Go，Apache-2.0，讀 Claude Code transcript JSONL 做純靜態壓縮）於 2026-08-09 完成吸收評估並結案" deleted=1 token=forget-74258bdd-1
    - [f_a7524a] [2026-08-09T01:20:19.280Z] 外部 repo cc-session-reader（Mapleeeeeeeeeee，Go，Apache-2.0，讀 Claude Code transcript JSONL 做純靜態壓縮）於 2026-08-09 完成吸收評估並結案：無任何項目值得吸收進 bridge。根本原因是兩系統資料源與目的不重疊——cc-session 吃 Claude Code 的 JSONL 產「可重新灌回 context 的壓縮歷史」，bridge 的 session-extract 吃自己的 markdown transcript 產「長期記憶 facts」；初版比對表高估了重疊度。研究筆記與判定表存於 wiki queries/cc-session-reader.md。
