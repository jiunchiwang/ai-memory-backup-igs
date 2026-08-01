# Loop State — telegram-kiro-bridge
Last run: 2026-07-31T20:46:29.688Z
Suggestions processed: 2026-08-01（見各項 ✅/⏸ 標記）

## High Priority (action needed)
- ✅ **「shortlist 未清空」是 curate agent 的同源 confabulation，不是系統故障**（2026-08-01 定案；
  途中我自己也先誤診成「兩個 consumer 搶 watermark」，同樣被推翻，過程留著當教訓）：
  · 產生端 `G:\AI\AI-canonical\tools\ingest-claude-mem.mjs` L76-77 **本來就覆寫檔案並推進 watermark**，
    watermark 鏈 07-29→07-30→07-31 完整。
  · 唯一跑過的 consumer 是排程 `claudemem-daily-curate`（LastRunTime `2026/8/1 04:30:01`、result 0），
    它跑的 `daily-claudemem.ps1` L20 先 extractor、L33 才 curate，**配對正確**。
  · `claudememcurate` **從未被執行過**（`events.jsonl` 17 個命中全是 grep，無 command 事件），
    且不在 `DEFAULT_STEPS`、`dream.json` 不存在 → `/dream` 走不到它。
  ∴ 真因：8/1 那則 curate log 自己寫「內容與**上方 2026-07-31 那批**逐條相同」——它比對的是**上一則 log**
  而非手上的檔案，連「6 筆已寫入／8 筆已捨棄」都是抄 07-31 那則自己的帳。實際兩批幾乎零重疊
  （07-31＝bomb/transcript replay/skill bundle/MCP SDK；8/1＝probe-*/status-channel/契約測試/status_first）。
  「檔頭仍是 07-30」「逐條相同」「cursor 沒前進」三條宣稱**全部是假的**。這是長期警惕模式 #002 的實例，
  而 dream 報告把 confabulation 升格成 High Priority 並開錯藥方。
  已做的修（**bridge 工作區，未 commit**）：`src/commands/dream.ts` 新增 `refreshClaudeMemShortlist()`
  讓手動 `/claudememcurate` 自帶 extractor（best-effort、失敗不阻斷），並在 prompt 加同源禁令
  （比照 `/docupdate` 既有的「不可拿其中一份當另一份的事實依據」）+ 要求原文貼出檔頭 + 說明「寫 0 條是正常」。
  tsc 0 error、smoke 93/93、extractor 契約用隔離 `AIMEMORY_DIR` 實跑驗過（exit 0、stderr 格式相符）。
  ✅ 排程那條（真正天天在跑的）也修完並 push：AI-canonical `ab619d1` 加 `$EVIDENCE_RULES`
  （禁拿 log 舊條目推斷本次內容、要求原文貼檔頭、說明寫 0 條正常），`8d506be` 補 extractor
  失敗即中止（exit code + shortlist mtime 雙檢）。後者是覆核 F1 抓到的：`$EVIDENCE_RULES` 的
  「寫 0 條正常」會把**唯一真實的**重掃故障（extractor 靜默失敗 → 舊檔留在原地）偽裝成健康。
  已用 5.1 + stub 三案實測，含突變測試（exit 0 但不重寫仍被擋 → 證明 freshness 檢查承重）。
- ✅ **AI-canonical 4 項已 commit + push**（2026-08-01，`73c1d9a..979b8ae`）：
  `06681d1` 新增 2 支 skill + 寫入 draft 前提推翻；`979b8ae` 修 Fable 5 覆核的 F1/F2/F4。
  兩輪異源覆核：round 1 抓到 1 high + 2 medium（本 commit 自己把推論冒充實測——正是它宣稱要根絕的錯），
  round 2 範圍限定後收斂（只剩 3 條 low 措辭級）並放行。junction 投影即時生效，無需跑 sync.ps1。
- ✅ **draft 重播根因已定案並修復**（2026-08-01，bridge commit `00149a6` 儀器 + `b613dba` 修復，**未 push**）：
  等級 2 內容快照上線後，05:00/05:01 與 09:17 兩次症狀被完整錄下。根因是 `renderDraftReply`
  在每幀尾端接 `" ▍"` 游標——游標夾在穩定前綴與新增 delta 之間，使幀 N 永遠不是幀 N+1 的前綴，
  client 的長度差動畫（立即顯示前 strlen(prev) 字元）因此每個前進幀都整段重繪。
  實證 1612 幀：帶游標 APPEND 17 / DIVERGE 598，剝掉後 568 / 32。09:17 窗口剝游標後殘餘歸零，
  且內容為純散文 → 第四輪的 markdown 區塊重排假設一併否證。
  `check-draft-render` 測試 3 標的正是此不變式卻恆綠（門檻 `>= 5` 剛好等於 bug 產生的值），已改成
  `startsWith` 多幀鏈並先驗紅再修。tsc 0 / fast tier 93/93。
  游標成因的生產確認已做（2026-08-01，bridge pid 106244 跑 `tsx src/index.ts` 於 09:38:48 重啟）：
  重啟後帶游標幀 0。工具：`scripts/probe-draft-frame-append.mjs`（untracked）。
  ⚠️ **但當時宣稱的「DIVERGE 0 = 已驗證」是過早結論**：那份樣本窗口截止在 01:43:02Z，而症狀在
  01:47 才發生（使用者回報「剛才 09:4x 長回覆時又消失」）。教訓：分析窗口的結束時間必須晚於
  「使用者回報的症狀時間」才有資格宣稱驗證通過，否則是在症狀發生前就收工。
- ✅ **draft 重播第二成因已定案並修復（token 隱藏的縮回，非 truncateTail）**（2026-08-01，未 commit）：
  09:47 生產幀顯示 agent 在寫 `<<SELF_EVAL:...>>` 時 draft 連縮兩次 —— 2233 (`…。\n\n<<SEL` 半個 token
  裸漏) → 2228 (`…。\n…`，`hideTrailingUnterminatedToken` 把 span 換成較短的 `"\n…"`) → 2226（token
  終止被 transform 吃掉）。與 `truncateTail` 無關（才 2233 字）。修法：新增
  `observerTransformer.cutPendingTokenTail`（**扣留式**：尾端「可能長成 token」的片段先不渲染，
  只扣 viable prefix 所以散文 `價格 << 100` 不受影響），在 `renderDraftReply` 於 **transform 之前**
  呼叫——擺在之後只修得掉第二次收縮，修不掉 `<<SEL` 那次裸漏。既有
  `hideTrailingUnterminatedToken` 與 `renderReply` 路徑一字未動。
  測試 `check-draft-render` 3b 先驗紅（`prevLen=13 curLen=8`，縮小版精確重現生產形狀）再修。
  tsc 0 / fast tier 93/93。已 commit `bd068e1`。
  症狀為何時有時無：tick 節流約 2s，只有剛好有一幀落在 token 書寫中途才踩得到。
  **重啟後驗證（2026-08-01 10:0x）**：bridge pid 114244 於 10:05:56 重啟（在 `bd068e1` 之後、跑
  `tsx src/index.ts` 吃 source），修復確實在跑。但重啟後生產樣本只有 10 幀 / 1 draft / 24 秒且**全是
  散文、沒有任何 `<<`**——只再次確認了游標成因，**打不到 token 路徑**。改用確定性重現補上：新增
  `scripts/probe-draft-token-append.mjs`（untracked，兩臂對照：OLD=`transform(buf)` 必須紅、
  NEW=`transform(cutPendingTokenTail(buf))` 必須綠，逐字元串流檢查每幀是否為下一幀前綴）。
  結果 3/3 PASS：OLD 臂重現生產同形的兩段連續收縮（30→19→17，先裸漏 `<<SELF_EVAL` 再換 `\n…` 再消失），
  NEW 臂 0 違反；散文 `價格 << 100` 未被凍結（扣過頭的回歸守衛）。
  ⚠️ 仍缺：**含 token 的生產幀**確認（單元級已證，生產級待自然發生後用 probe 再驗一次）。
- ⏸ **draft 診斷刻意留著，勿清理**（2026-08-01 使用者裁決，且已證明有價值——第二成因就是它抓到的）：
  `.env` 的 `TG_DRAFT_DIAG=2` 與 `logs/draft-frames.jsonl` **不要關、不要刪**。
  收尾條件：重啟後再收一段含長回覆 + 含 token 的樣本，用同一支 probe 驗 DIVERGE 為 0，
  且分析窗口必須涵蓋到最後一次症狀回報時間之後。收尾動作 = 關 `TG_DRAFT_DIAG` + 刪 log。
- ✅ **Fable5 覆核 findings 全部已修並 push**（2026-08-01，`4d5f969..1bc65b2`）：
  - F1/F2/F3/F4：`4d5f969` 修（cut/hide 共用 lastUnterminatedOpener + proxy 分流游標 + 刪死 export）
  - F-A（fixpoint 只跑一次）：`179976c` 修（迭代到 fixpoint）
  - F-3A（cut 沒 trim、兩層不交替）：`1bc65b2` 修（開頭 trim + 外層迴圈包兩層）
  - 測試：check-draft-render 新增 F1/F2/F-A/F-3A 形狀 + 反向守衛 + fuzz 300 輪；93/93 passed
- ⏸ **draft 重播殘餘成因（另案，未處理）**：回覆超過 ~3900 字後 `truncateTail` 滑動視窗在頭部插
  `"…"` 並整段位移，共同前綴剩 1 → 之後每個 tick 必定重播。非上述兩次症狀的成因（55–1938 字未達上限），
  要解需改設計（拆多則訊息，或到上限就凍結 draft 讓最終訊息帶完整文字）
- ✅ **bridge 側 8 處已推翻前提全部降級**（2026-08-01，bridge commit `10d1654` + `d92986f`，**未 push**）：
  `status-channel.ts` 檔頭/JSDoc/行內共 4 處、`check-draft-streaming.mjs:537`（**assert 期望值一字未動**，
  只改理由敘述）、`default-skills/` 兩處（由 `.githooks/pre-commit` 的 `sync-skills-to-repo.mjs` 自動回填，
  **不需手動維護**——此機制之前不知道，記下來）。
  承重排序（status 先建、draft 後開）**刻意保留**並在註解明寫「不要因為前提被推翻就拆掉」。
  仍在工作區未 commit（刻意）：`src/run-prompt.ts:625/702/714` 三段註解（該檔另有前一輪 WIP，不掃進來）、
  `scripts/probe-draft-clearing.mjs:68-69`（該檔仍 untracked，是否納入版控待裁決）。
- 🆕 **curate 防護的殘餘天花板（覆核 F2/F3/F4，全 low）**：
  F2 verbatim header echo 仍可被 confabulate（抄上一則 log 裡格式正確的引文，機械上無法與真引文區分）
  → 根治法是 ps1 自己讀第 2 行注入 prompt（`@(Get-Content $shortlist -TotalCount 2)[1]`），順便解除
  「檔頭永遠在第 2 行」的隱性耦合；F3「寫 0 條正常」也把過度去重正常化；F4 規則文本寫「three claims」
  但規則裡只看得出兩條。
- ~~🆕 跨 repo follow-up：bridge 有 8 處仍把已推翻的 draft 前提寫成確定事實~~（已完成，見上）：
  `src/run-prompt.ts:702`「sendMessage **早已證實**」（另 625、714 同款）、
  `src/status-channel.ts:49`「**確定**會清掉 live draft」（另 40、249）、
  `default-skills/ms-streaming-token-pipeline/SKILL.md:328,418` 舊版原文照留（`sync.ps1` 不涵蓋 default-skills），
  `scripts/check-draft-streaming.mjs:537` 把它**編進測試預期**，
  以及 `scripts/probe-draft-clearing.mjs:68-69` 寫「不清、不重播（**實測**）」而同檔 `:87` 自己說「問錯 observable，三臂全部白測」
  ——證據來源自相矛盾，這兩行是未來把本次修正回滾掉的現成彈藥。
  處理方向：降級為「保守假設，2026-07-31 探針未能證實」，別直接刪（症狀根因仍未定案）。
- 🆕 **兩條 low 措辭 follow-up（AI-canonical，round 2 明說可不改）**：
  `ms-streaming-token-pipeline:344` 陽性對照失效的依賴註記只掛 sendMessage 列，實際同樣覆蓋 edit 列（F-a）；
  `:356`「全臂皆負」嚴格說是 9 負 + 1 無效（md 表格臂）（F-c）。刻意未修：round 2 放行只針對 `979b8ae`，不追加未覆核的 commit。
- ✅ **2 支新 skill 已登記 usage entry**（2026-08-01）：改用 bridge 自己的 `usageStore.migrateFromDisk()` sweep 補，非手改 JSON；35→37 筆。
  副產物：`uk-conventions` 被正確標為 orphan（它已從 skill 轉成 `~/.claude/commands/uk-conventions.md` slash command，非 skill）。
  ⚠️ 「升格流程加自動補 entry」仍未做——機制早已存在（`/skillusage` 會呼叫 `migrateFromDisk`），缺口只是**沒人在建 skill 後跑它**；
  真正的修法是讓 /dream 的 skillreview 步驟先 sweep 再讀 JSON。
- ✅ **「2 支 skill 路徑範例過時」判定為 false positive**（2026-08-01，不修）：
  `ms-portable-skill-authoring:55` 位於該檔自己的「### Before（寫死，不可攜）」**教學性反例 code block** 內，
  `memory-to-skill:23` 是標明「典型值（不同機器不同）」的**對照表一格**。
  依該 skill 自己的稽核判準（L307-313）兩者皆列為 ✅ 合法；改掉會毀掉教學範例。
  遺留（低優先、非違規）：L299-302 的稽核 grep 仍以舊機器前綴當 ground truth，L315-324 的違規清單是 2026-05-03 snapshot 已自述會過期。
- ⏸ **Repo 膨脹 ratio 3.9（>3.0）**：87%+ facts 受 wiki-reference 保護不可刪，結構性無法靠 factlint 降低——要降需改 provenance 策略（架構決策，本輪未動）
- ✅ **`f_f6406d` 過時但受保護** — 無需動作：依 2026-07-08 裁決不解除引用，wiki 側已更正，本項僅為知情紀錄，下輪可從 High Priority 移除

## Watch List (monitor)
- `ms-external-repo-absorption`：2026-07-10 升格後 use_count 仍為 0，觀察是觸發條件太窄或 description 沒對上情境
- `use_count` 口徑不可信：依賴 agent 主動輸出 `<<SKILL_USED>>`，`uk-slot-codegen` 顯示 0 但它是 slot 開發主入口——修回報覆蓋率前不可用它做刪除決策
- 缺頁：`uk-slot-pirates-queen`（8 facts）無 concept 頁，下輪 wikisync 補
- `bridge-memory` ripple 順延：本輪 wikisync 達 5 topic 節流上限，該頁已由 wikilint 代補但 ripple 標記可能重複累計
- 升格候選 4 個（bridge-acp 5 條／uk-slot-codegen 4／bridge-streaming 3／uk-slot-template 3）：建議 append 進既有兩頁 lessons，不新建碎頁
- 新候選 `blackbox-probe-experiment-design`（count=2, score=0.35）：第 3 次黑箱多臂探針即升格
- `dream-report-action`（count=4, score=0.28）：骨架已穩定但 turn 成本低分數上不來，判定不新建 skill
- 衰減判定期間不足：hit-log 最早 fact 命中為 2026-07-11，僅 21 天 < 60 天門檻
- `verification-diagnosis`／`bridge-smoke-gate` 列入零命中區屬假訊號（今日才建立）
- 弱連結頁：`bridge-roadmap`、`agent-system-architecture`、`spine-viewer`、`igs-uof`、`skill-candidates` 與 8 個 query 頁只被 index 連到

## Noise (ignored this run)
- /sharedsync 無更新、/backup 成功（commit `b06684b`、72 檔、8.4s）、/artifactcleanup 刪 0 剩 1
- /dailylog 寫入 `2026-07-31.md`（27 行）、10 個 session 檔已歸檔至 oldSessions（341→351）
- /docupdate 文件已與原始碼一致（`check-doc-sync` 閘門 PASS）；`/forget` 警告為抽取器 false positive，兩份文件寫的正是「它不存在」
- /topicreview 22→24 topic、misc 13→1、bridge-project 76→55；/factlint 刪 8 條 `[WS]`；/specialistreview 0 新增 1 擴充
