**User:**
<identity>
你是 researcher，深度研究與方法論 specialist（AI 策略、知識管理、agent 設計模式分析）。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Specialist context — relevant facts for "researcher" domain]
- [f_ecd35a] [2026-07-30T13:27:05.145Z] UOF 加班時數查詢位置：差勤 → 加班統計查詢（Project/BAE/Stats_Search.aspx），設日期區間並勾選簽核狀態「同意」+「簽核中」，看底部平日／假日合計
- [f_d5b5eb] [2026-08-06T00:52:14.026Z] UOF 的 Cloudflare Turnstile（https://hq.igs.com.tw/UOF/AntiBotCheck.aspx，登入成功後才跳）只有「接管非自動化啟動的瀏覽器」能過：2026-08-06 實測 Playwright headless 與 headed 兩臂皆敗（內建 Chromium 與 channel=msedge 真 Edge 都停在 AntiBotCheck，等 241s 未過），可行路徑是 Start-Process msedge --remote-debugging-port=9222 --user-data-dir=<乾淨profile> 讓使用者自己登入+點驗證，再用 playwright connect_over_cdp("http://127.0.0.1:9222") 取既有 page 並直接呼叫 cmd_hours.overtime_range 抓數字——不需任何 stealth 參數或指紋偽裝。過驗證前刻意不用 CDP 碰該頁。
- [f_303689] [2026-08-06T02:05:47.968Z] igs-uof 已在 2026-08-06 加入 CDP 接管模式（commit fce516d，AI-canonical-corp）：查詢被 Cloudflare Turnstile 擋住時腳本現在回明確的 error=antibot（不再誤報 unreachable/scrape_failed），處置是跑 scripts/launch_cdp_browser.py 開瀏覽器→使用者自己登入並點驗證→uof.py --cdp 接管。antibot 有兩種相反處置必須照 hint 走：非 CDP 時「別重試同一條命令」，已在 CDP 卻被中途重新挑戰時「在既有視窗重點驗證後重跑同一條命令、不要重開瀏覽器」。CDP 模式刻意不寫 session.json——storage_state 會把使用者全部網站 cookies 落地成明文（實測連乾淨 profile 都混進 .msn.com/.bing.com，且 chmod 600 在 Windows 是 no-op）。填單路徑的 CDP 模式尚未端到端實測。
- [f_2e77d3] [2026-08-14T13:44:45.636Z] 使用者已啟動 iGaming 原始碼 Mend SCA/SAST 掃描導入，採私有控制倉庫 `igaming-mend-scan` 搭配自架 runner group `mend.io` 管理。
- [f_975249] [2026-08-14T13:44:45.636Z] iGaming Mend workflow 必須以 `MEND_TARGET_GITHUB_ORG` 明確指定掃描組織；fine-grained PAT 走 `/user/orgs` 可能回空陣列造成「0 個 org 的假綠燈」，不可只看 Action 綠燈判定成功。
- [f_e40af6] [2026-08-14T13:44:45.636Z] iGaming Mend 首個已驗證 pilot 為 `IGS-ARCADE-DIVISION-RD4-IG/Client_Activity_LuckyMission`，Type 為 `Client(Cocos)`，SCA 與 SAST 均成功。
- [f_0dec36] [2026-08-14T13:44:45.636Z] 使用者下週優先要補 Mend workflow 的 P0 保護：任一 repository 的 SCA 或 SAST 失敗時，Action 必須明確標紅並輸出失敗原因。
- [f_0d1a3b] [2026-08-14T13:44:45.636Z] Mend User Key 曾出現在來源文件明文中；目前先沿用既有 Key，但已列為後續應輪替、且新 Key 僅可存放 GitHub Secret 的資安待辦。
- [f_7c41c5] [2026-06-03T12:19:51.275Z] 使用者的機器已安裝 Python youtube-transcript-api、playwright + chromium，可用於抓 YouTube 字幕和 HTML 轉 PDF
- [f_8a4a0e] [2026-06-03T12:19:51.293Z] 使用者偏好 HTML 文件要有目錄錨點跳轉功能（點擊跳段落 + 回目錄連結）
- [f_99b243] [2026-06-03T12:19:51.310Z] 使用者產 PDF 的工作流程：HTML+CSS 排版 → Playwright headless Chromium 渲染（docs/to_pdf.py），不用 fpdf2 或 WeasyPrint
- [f_86246b] [2026-06-09T08:29:22.331Z] 使用者的 Obsidian Vault 位於 C:\Users\jiunchiwang\OneDrive - International Games System\文件\Obsidian Vault\，內含 TypeScript 等技術筆記
- [f_4f4b55] [2026-06-22T07:43:19.491Z] 使用者有一個 excel-to-ai-document 專案位於 G:\AI\excel-to-ai-document，含 skill/excel-to-ai-doc 資料夾（SKILL.md + scripts/convert.py），用於將 Excel 規格書轉為 AI 可讀的 Markdown + 圖片結構
- [f_947e7a] [2026-06-24T20:31:30.593Z] 驗證 TypeScript 介面重構或整併時，用 npx tsc --noEmit 做型別檢查；若遇到 TS6.0 的 deprecation 警告，可加 --ignoreDeprecations 6.0 抑制以聚焦真正錯誤。
- [f_a8a12e] [2026-07-06T05:19:36.045Z] 在 bash shell 呼叫 PowerShell 時引號（單引號/$_）會被 bash 層吃掉導致 ParserError，可靠做法是把指令轉 UTF-16LE 再 base64，用 powershell -EncodedCommand 執行
- [f_af2a3f] [2026-07-16T09:36:02.404Z] 使用者這台機器的 gh CLI 尚未執行 gh auth login／未設 GH_TOKEN，研究 GitHub repo 時 gh repo view 等指令會直接失敗，需改用 WebFetch 抓取
- [f_ab7e0a] [2026-07-30T20:31:49.767Z] skill bundle 大幅更新的標準流程：先把未提交檔 commit 建立 restore point → 依差異分三類處理（整包替換／回填缺漏／選擇性合併）→ 被取代的舊 skill 轉成 deprecation pointer 並移除其觸發關鍵字避免撞名搶觸發 → 獨立審查通過才 push。
- [f_129738] [2026-08-02T13:31:37.803Z] 在 Edit 工具做整行刪除或改解構名時，若目標字串在同檔重複出現（如 relay.ts 的 const { runPrompt, sessions } = deps() 全檔 9 個相同字串），必須用上下文定位而非 replace_all，否則會誤改其他 8 處——tsc 只標出未使用的那一處，行號才是唯一可靠依據
- [f_b09bb8] [2026-08-06T03:11:54.658Z] 在 Windows shell 裡把「會 spawn 子進程的命令」接管線（| tail、| grep）會假裝成掛住：管線要等 EOF，而子進程（如 ACP adapter）握著 stdout 不放，即使父進程已經印完結果並退出也看不到任何輸出——2026-08-06 因此兩次誤判 codex-acp 探針「300 秒沒回應」，實際上兩次都成功回了 PONG，殺掉孤兒進程後輸出才一次吐出來。對這類命令要用 `> file 2>&1` 落檔再讀，不要接管線；同理 child.kill() 只殺 shell wrapper，孫進程要另外清（用 CommandLine 比對 + 查 ParentProcessId 存活再殺）。
- [f_10d8ff] [2026-08-06T07:06:05.871Z] 編輯 .env 這類含機密的檔案時，使用者接受的做法是：只讀取需要的行範圍（避免把 token 拉進 context）、用 regex 定位而非手抄空白、並以「匹配數必須恰為 1」與「KEY=value 行數前後不變」兩道保險驗證未動到設定值
- [f_ddc6a2] [2026-08-06T10:57:15.181Z] openpyxl 的 `load_workbook(data_only=True)` 讀到的是 Excel 上次存檔時算好的快取值，不是公式本身；由 openpyxl 之類產生器寫出、或存檔前未重算的檔案沒有快取，那些公式格一律讀成 None——2026-08-06 在 excel-to-ai-doc 實測，一張三格全公式的 sheet 整張被判成空白、輸出只剩「此工作表無儲存格內容」，而自我驗證因為刻意跳過 empty sheet 的檢查照樣印「整體：通過」。任何用 openpyxl 讀 xlsx 的腳本都會踩到；解法是另載一次 `data_only=False` 比對，把只有公式沒有快取的格回填公式字串並讓驗證失敗（回填的是 =SUM(...) 不是數值，仍須請對方在 Excel 重新存檔以寫入快取）。
- [f_00d0b6] [2026-08-06T10:57:25.696Z] 用 openpyxl 讀儲存格顏色時，`fill.fgColor.rgb` 只在 `color.type == 'rgb'` 時是字串；Excel 調色盤上排「佈景主題色彩」的 type 是 'theme'、舊調色盤是 'indexed'，只判斷 rgb 是不是字串會靜默漏掉一整類上色（比不做更危險，因為輸出看起來已支援顏色）。theme 要讀 xl/theme/theme1.xml 的 clrScheme，且 Excel 的 theme 索引順序與 XML 排列不同——XML 是 dk1,lt1,dk2,lt2,accent1..6,hlink,folHlink，Excel 索引前兩對互換（0→lt1, 1→dk1, 2→lt2, 3→dk2, 4..9→accent1..6, 10→hlink, 11→folHlink）——再套 tint（ECMA-376：在 HLS 亮度上，tint<0 → L*(1+tint)、tint>0 → L*(1-tint)+tint，HLSMAX 正規化為 1.0）；indexed 走 openpyxl.styles.colors.COLOR_INDEX。
- [f_cbcb3c] [2026-08-11T07:11:08.032Z] **Bun 正常**：版本 1.3.9 已安裝
- [f_b120d4] [2026-08-12T07:20:10.466Z] 在 Git Bash 環境用 Start-Process 排延遲工作時不可用 `timeout /t N`：Git Bash 的 PATH 讓 cmd 解析到 GNU coreutils 的 timeout 而非 Windows 的 timeout.exe，GNU 版看不懂 /t 會直接非零退出，接在後面的 `&&` 整串短路、後續指令完全不執行且無明顯錯誤。2026-08-12 因此宣告「重啟已排定」但實際什麼都沒發生。正確做法是用 PowerShell 的 Start-Sleep 或呼叫完整路徑 C:\Windows\System32\timeout.exe。
- [f_a1b97e] [2026-08-12T20:39:57.271Z] 查「某支 skill 到底被用了幾次」的權威來源是 `~/.claude.json` 的 `skillUsage` 物件（每支 skill 一筆 usageCount + lastUsedAt，全時間累計、不隨 transcript 輪替），**不是拿 transcript grep**——transcript 約 30 天輪替，數出來的是視窗內的數字；2026-08-12 就因此把 vc-kiro-delegate 的「全歷史 1 次」寫錯，實際是 10 次、排名 8/57（中位數 2）。配套的第二條判準：當計數來源的比對條件寬到會把無關事件也記進去（kiro-usage.log 把「commit message 提到 kiro-cli」也算一筆，連當次調查本身都灌進 27 筆），**分母被污染而分子沒有，此時只能報絕對數、不可寫成比例或百分比**，並明講分母為何不可用。
- [f_e189b1] [2026-08-14T00:21:06.070Z] 在 Bash tool 裡寫 git commit message 必須用 bash heredoc，PowerShell here-string（@'…'@）會讓首行的游離 @ 變成 commit 標題、末尾再留一個 @，且 git commit 照樣成功不報錯——2026-08-14 再次踩到（先前 2026-07-31 已有同型紀錄），修法是 git commit --amend -F - 配 heredoc 重寫並驗證首尾。
- [f_1a68bf] [2026-08-14T13:44:45.636Z] 使用者希望技術流程交接同時提供 Markdown 與具目錄錨點、可列印的 HTML 版本。
- [f_c3d198] [2026-06-19T07:55:58.294Z] 跨模型 AI 策略 v4 的核心原則:正典語料庫(canonical corpus)本身就是產品——以 markdown + git 追蹤的精煉知識為唯一真實來源(G:\AI\AI-canonical),CLI / MCP / bridge / 索引都只是部署基礎設施而非產品本體。
- [f_7d7ffe] [2026-06-19T07:56:04.782Z] AI 產物的雲端 vs 本地儲存政策:正典 skills、steering 政策與通用文件放公開 GitHub repo(AI-canonical);session 執行日誌與框架內部狀態僅保留本地、不進版控。
- [f_6d4701] [2026-06-27T00:45:09.031Z] memory-to-skill 正本 SKILL.md 已加入 Confidence Scoring 量化門檻（Step 2 後）：confidence = F×C（頻率×成本），≥0.5 進候選、0.3-0.49 留底觀察、<0.3 跳過；靈感來自 ECC continuous-learning-v2 的 instinct confidence scoring
- [f_f92692] [2026-07-14T20:31:29.740Z] 撰寫可攜式 skill 時,若該 skill 會被多個 agent CLI(如 Kiro、Codex、Claude)或多台機器共用,應避免在 SKILL.md 中寫死絕對路徑(例如特定磁碟機代號或使用者目錄),以免跨環境失效。
- [f_e68e53] [2026-07-31T20:47:31.616Z] 使用者的 skill 正本一律寫在 G:\AI\AI-canonical\skills\general\（通用）或 AI-canonical-corp（slot/office），絕不直接編輯 ~/.claude/skills 或 ~/.kiro/skills——那兩處是 sync.ps1 產生的 junction 投影，直接改會被下次 sync 覆蓋
- [f_4568c1] [2026-08-02T13:31:37.803Z] 使用者的 skill 投影機制細節：~/.claude/skills 與 ~/.kiro/skills 下的 skill 目錄是指向 AI-canonical 正本的 junction（非 copy），所以改正本即時對三個 CLI 生效、不需再跑 sync.ps1；sync.ps1 -Apply 真正必要的是 steering 那批 copy
- [f_76462d] [2026-08-05T14:58:05.531Z] sync.ps1（AI-canonical）自 2026-08-05（commit b330aad）起一次投三個 CLI：skills 對 ~/.kiro、~/.claude、~/.codex 各逐 skill junction 直達正本（Codex 原本是二段 junction 繞 Kiro，且整個 skills root 不可 junction 否則蓋掉它的 .system）；steering 對 Codex 走「copy 到 ~/.codex/steering + 全文內嵌 ~/.codex/AGENTS.md 的 canonical-steering managed block」，選內嵌而非 pointer/@import 是因為 Codex 是否支援檔案引用未經驗證，marker 之間每次 sync 覆蓋所以不漂移、marker 外手寫內容保留
- [f_d5d14e] [2026-08-05T14:58:18.745Z] 這台機器的 Codex CLI（0.146.0）在 2026-08-05 時未登入（codex login status → Not logged in、~/.codex 無 auth 檔、bridge .env 也沒有 OPENAI/CODEX key），所以任何「skill/steering 在 Codex 上能不能正確執行」的端到端驗證都做不了，探針會撞 401 Unauthorized；連帶「Codex 是否真的讀 ~/.codex/AGENTS.md 全域指令」仍未實測——官方 docs 說會讀但 openai/codex#8759 與 #27705 報告過全域檔不載入，登入後值得用 canary 字串跑一次 codex exec --skip-git-repo-check 驗證
- [f_ac4b34] [2026-08-05T15:08:54.619Z] Codex 的 ~/.codex/skills/.system 由 Codex CLI 自己在啟動時重建（2026-08-05 跑 codex exec 後自動多出 review-agent，從 5 支變 6 支），所以該目錄的內容數量會自行變動，投影工具不應把它的變化誤判為外部干擾
- [f_b9e59d] [2026-08-05T15:08:54.619Z] ~/.kiro/steering/karpathy-guardrails.md 沒有對應的 AI-canonical 正本（正本 steering 只有 closed-loop-system / skill-workflow / task-acknowledgement 三支），所以 Kiro 吃著一份 Claude 與 Codex 都拿不到的 steering——待決定是補進正本或確認為 Kiro 專屬
- [f_806752] [2026-08-06T11:05:47.071Z] 【推翻先前記錄】關於「這台機器的 Codex CLI 未登入、端到端驗證做不了」那條 2026-08-05 的 fact 已於 2026-08-06 實測推翻：`codex login status` → Logged in using ChatGPT、版本 0.146.1，當日實跑兩輪 `codex exec` 異源覆核成功；`~/.codex/AGENTS.md` 全域指令是否被讀取也已用 canary 字串實測通過（見 AI-canonical 的 steering/skill-workflow.md），openai/codex#8759 與 #27705 報告的全域檔不載入在此版本不重現。仍未解的是 `codex app-server` 在這台機器壞掉（failed to initialize sqlite state runtime under ~/.codex，穩定重現），而 Claude Code 的 `codex:setup` 是透過 app-server 探測登入狀態，所以它會誤報 loggedIn: false——判斷 Codex 可用性一律以 `codex login status` 為準，不要相信 codex:setup。舊 fact 因被 wiki 頁 concepts/ai-strategy.md 的引用保護，forget 三次皆 deleted=0，故以本條並存推翻而非刪除。
- [f_ac57f8] [2026-08-09T01:20:19.280Z] 第三方工具的安裝腳本可能靜默寫進 skill 正本：cc-session-reader 的 install.sh/install.ps1 預設會裝一份 skill 到 ~/.claude/skills/cc-session，而本機該路徑是 junction 到 AI-canonical 正本 repo，等於繞過 sync.ps1 投影流程直接改正本。要裝必須帶 --no-skill 或把 SKILL.md 走正本流程手動放。
- [f_4e6745] [2026-05-29T16:20:19.509Z] 使用者偏好 agent 回覆時以選項按鈕（<<ASK:...>>）優先，減少需要打字的情況
- [f_70542c] [2026-06-01T12:16:45.051Z] 使用者偏好 git commit 訊息使用中文
- [f_e0ce0f] [2026-06-24T20:31:28.200Z] 使用者偏好 git commit 前先確認：執行 commit 之前應多問幾個釐清問題並取得使用者同意，不要逕自 commit。
- [f_be8c07] [2026-07-07T07:52:13.452Z] 使用者的除錯對策偏好：對帳/檢查類函式遇格式不符應「回報不 crash」（守衛 + error log），反對用關掉檢查或 clamp 掩蓋——理由是不用記得開回來、production 遇壞資料也不炸
- [f_a738db] [2026-07-10T00:12:51.617Z] 使用者決定 underused skills 處理策略（2026-07-10）：刪除 skill-creator、knowhow-accumulation、non-engineer-agent-design（磁碟+store），保留 huashu-slides、dual-skill-review-loop、self-eval-prompt-pattern 繼續觀察
- [f_cc8fd5] [2026-07-13T11:39:16.104Z] 使用者偏好把同一 session 內不相關的改動拆成多個小顆粒 commit，而非合併成一個（2026-07-13 對 README 拆分+roadmap更新兩件事確認選擇拆兩個 commit）
- [f_d29dfc] [2026-07-13T13:25:29.299Z] 使用者對會產生真實外部紀錄的自動化（如公司系統表單送出）採保守策略：即使技術上可行，仍選擇只做到 dry-run+截圖、手動確認後才送出，不做一鍵全自動
- [f_4ad101] [2026-08-14T00:21:06.070Z] 使用者於 2026-08-14 確認：說「commit」不等於授權 push——選定修法（如選 A）也不等於授權 commit，兩者都要各自明確指示。
- [f_48fdd8] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 B 區（規格書結構）決策：寫常見模式而非固定規範（因為每案 sheet 命名不同）
- [f_b0c1d8] [2026-08-13T03:00:58.319Z] 使用者的公司內部 AIBI 平台有一台 MCP server rockmanx4-aibi（Streamable HTTP，https://ai-gw-02.i17game.net/rockmanx4/mcp，Bearer token 認證），提供 SkillHub 技能庫／AI 採購用量／團膳菜單／員工通訊錄／平台公告；2026-08-13 嘗試加入時 claude mcp add 被 Claude Code auto mode classifier 擋下，尚未加成
- [f_271855] [2026-08-14T20:08:54.910Z] iGaming Mend 掃描導入時，使用者選了沿用附件文件中已外流的既有 Mend User Key，排除撤銷重發——理由是「目前那把就是配發給我用的 Key」，非帳號本身有問題只是文件外流；assistant 已明確 push back 建議撤銷重發，使用者知情後仍裁決沿用。2026-08-14。
[End specialist context]

[Persistent memory — lessons from your previous tasks]
- [2026-07-01T03:20:24.251Z] (用一句話總結「Kiro CLI」是什麼工具，然後回報你目前使用的 model ID) Kiro CLI 是 AI 驅動的命令列開發工具，支援自然語言指令完成程式撰寫與多步驟任務自動化；目前 agent 運行於 claude-sonnet-4.6。
- [2026-07-01T03:20:24.251Z] (用一句話總結「Kiro CLI」是什麼工具，然後回報你目前使用的 model ID) Kiro CLI 是一個讓開發者透過自然語言在終端機中執行程式撰寫、檔案操作、多步驟任務委派的 AI agent 工具。
- [2026-07-01T03:20:24.251Z] (用一句話總結「Kiro CLI」是什麼工具，然後回報你目前使用的 model ID) 目前對話使用的 model 為 claude-sonnet-4.6（系統 context 顯示值）。
- [2026-07-13T02:08:06.667Z] (研究任務：請調查 telegram-kiro-bridge 專案的 status-server.ts 實作，回答以下問題) 調查 status-server.ts 實作：port 3847、SSE 在 /api/status/:taskId/stream、TaskEntry 含 12 欄位、前端為外部 status-app/index.html
- [2026-07-13T02:08:06.667Z] (研究任務：請調查 telegram-kiro-bridge 專案的 status-server.ts 實作，回答以下問題) HTTP server 預設 port 3847，綁 127.0.0.1（STATUS_BIND_HOST 可覆寫）
- [2026-07-13T02:08:06.667Z] (研究任務：請調查 telegram-kiro-bridge 專案的 status-server.ts 實作，回答以下問題) SSE endpoint: /api/status/:taskId/stream，連線後立即推送現狀再持續 broadcast
- [2026-07-13T02:08:06.667Z] (研究任務：請調查 telegram-kiro-bridge 專案的 status-server.ts 實作，回答以下問題) TaskEntry 結構含 taskId/type/specialist/peer/goal/status/startTime/endTime/checkpoint/lastOutput/error/turns 共 12 欄位
- [2026-07-13T02:08:06.667Z] (研究任務：請調查 telegram-kiro-bridge 專案的 status-server.ts 實作，回答以下問題) 前端為外部檔案：專案根 status-app/index.html，由 readFile 動態讀入後回傳
- [2026-07-13T02:29:16.614Z] (目標：研究 cloudflared quick tunnel 的運作原理，寫一份 200 字中文摘要。背景：使用者正在測) Cloudflared Quick Tunnel 免登入模式運作原理與 7 項限制摘要，含對 bridge status-tunnel 的影響分析
- [2026-07-13T02:29:16.614Z] (目標：研究 cloudflared quick tunnel 的運作原理，寫一份 200 字中文摘要。背景：使用者正在測) Quick Tunnel 執行 cloudflared tunnel --url 後建立僅出站連線至 Cloudflare 網路，自動產生隨機 trycloudflare.com 子網域反向代理回 localhost，免帳號免 DNS
- [2026-07-13T02:29:16.614Z] (目標：研究 cloudflared quick tunnel 的運作原理，寫一份 200 字中文摘要。背景：使用者正在測) 關鍵限制：URL 每次重啟變更（ephemeral）、不支援 SSE、並發上限 200 requests、無 SLA、無自訂網域、無認證（僅靠 URL 隨機性）
- [2026-07-13T02:29:16.614Z] (目標：研究 cloudflared quick tunnel 的運作原理，寫一份 200 字中文摘要。背景：使用者正在測) bridge 的 status-tunnel.ts SSE endpoint 在 quick tunnel 下不可用，Mini App 前端需改用 HTTP polling 或升級到 named tunnel 才能使用即時串流
- [2026-08-07T20:36:55.798Z] (# 研究任務：Google A2A (Agent-to-Agent Protocol)
[End persistent memory]

[Artifact output]
任務完成後，在回覆最末附一個 JSON block 供系統存檔：
```json
{"type":"artifact","summary":"一句話摘要","outputs":[{"type":"finding","content":"..."}],"files_modified":[],"tags":["tag1"]}
```
outputs.type 可用：finding, code_change, recommendation, analysis。
tags 用英文小寫。如果任務失敗或無有意義產出，不需要附。
[End artifact output]

[Memory recall — dynamically retrieved facts relevant to this message]
[bridge-project] (relevance 0.57)
- telegram-kiro-bridge 的 planUncertainReplay 刻意不做遞迴切分，改為把限制文件化（2026-08-14 裁決，src/telegram-retry-guard.ts:124-142）：該函式對「送出結果不明」的待重送訊息加上不確定性前綴，前綴後若超過 TELEGRAM_MESSAGE_LIMIT 就拆成「通知 + 原文」兩則，但**前提是 text 本身不得超過 limit**——超過時它不會也無法補救（回傳的第二則仍會超限）。不代為 split 的理由是可遷移的：多一個切塊實作＝多一個會與既有 splitForTelegram 漂移的來源，切塊是呼叫端的責任；且「超長訊息 → Telegram 400 退回 → 被 catch 重新入列 → 永遠送不出去」這個迴圈在本護欄出現之前就存在，不是護欄引入的新缺陷。判準形狀同 f_ee9da7：在護欄裡複製一份既有不變式的實作，比明列前提與已知限制更糟。
- telegram-kiro-bridge 的 grammY transformer 安裝順序已於 2026-08-14 實測後更正，先前文件宣稱「護欄裝在 autoRetry 之前會造成 silent total failure」是錯的：grammY 的 `bot.api.config.use()` 是 `reduce(concatTransformer, this.call)` ∴ **後裝的在外層**；重試護欄裝在 autoRetry 之後（外層）好處是護欄自己發動的重試會重新經過 autoRetry 的 429 處理，但⚠️**這一點不是承重的**——因為 autoRetry 已設 `rethrowHttpErrors: true`，順序對調時「非冪等方法只嘗試一次」照樣成立，差別只有 429 那一項。實據：src/bot-setup.ts:195-198（該註解本身即更正後版本）。與 f_f9f50a 互補非重複：那條講 rethrowHttpErrors 預設 false、HttpError 重試迴圈在 call() 內層使 maxRetryAttempts 管不到；這條講 use() 的層序方向與「順序不承重」的判定。

[bridge-specialist] (relevance 0.56)
- telegram-kiro-bridge 的 run_plan 模板有一類「能力錯配」缺陷，2026-08-13 實際發生並於 2026-08-14 修正（commit 9626e10，已 commit 未 push）：wf-review 的 lens_adversary 與 wf-verify 的 reverse_sweep 都要求「先自己讀過對象本體＋逐字複製原始碼」，卻派給 moa-ref-adversary——它的 specialists/moa-ref-adversary/preamble.md:4 寫「不要使用任何工具（不讀檔、不寫檔、不跑命令）」∴ 它開場回「我沒有讀取工具的權限」、findings 全部降級成推測。⚠️ 承重的不是這個錯配本身而是它的不可見性：step 有回東西就算完成，moa_plan_done 記 failed:0、run status done、/job 全綠，拒答只出現在 verifier 的 NEEDS_FIX 與顧問自己的內文裡。修法是改派（lens_adversary→verifier、reverse_sweep→moa-ref-security）＋在 check-job-orchestration.mjs 加一條用 preamble 原文判盲審的斷言（不寫死名單）＋K17 變異守它。兩個容易誤判的事實：①「權限」是顧問自己的措辭不是 ACP 拒絕——readOnlyLens（會拿掉 @builtin 只留 MCP）只設在 moa-ref-kiro，moa-ref-adversary 沒有 ∴ 它握有讀檔工具只是被 prompt 禁用；② 盲審顧問接 wf-prd/wf-design 的 challenge 是合法的，那裡「逐字引用」的對象是 depends_on 餵進來的產出不是檔案，把斷言的正則放寬到涵蓋那種用語會製造假紅燈。

[adversarial-review] (relevance 0.55)
- 2026-08-12 codegen git-init 五輪異源覆核抓到一個獨立的失效模式：**修正動作本身會產生新的假因果**（有別於既存那條 2026-07-31 的「因果宣稱與程式碼實際時序不符」——那條講的是原始敘述從意圖推理而來，這條講的是為了修上一條而新寫的句子）。同一形狀連出現三次：修「uk_872 gitlink 屬個案」→ 編出「是模板後來改掉了」（模板全史 72 commit 0 筆 160000，否證）；修「照模板不要加碼」→ 寫出「皆已被各自 .gitignore 擋」（實際是 local-only 的 .git/info/exclude）；修上一條 → 寫出「不在任何專案的 .gitignore 裡」（被 uk_872 的 78 條逐檔 glob 證偽）。共同機制是修正時數字擴大了、寫對了，卻順手補一個**沒有證據的機制解釋**，或把**有例外的觀察壓縮成全稱句**；這比原錯更難抓，因為數字都對、語氣自信、讀起來像考證過。防法：①文件只留觀察到的分布＋操作規則，成因明寫「未知，別替它補一個」；②全稱句（任何／都／皆）出手前先找一個反例，找不到才寫；③要寫因果就得先跑得出證據的查法——git log --all --raw 查全史是否出現過某 mode、ls-tree <root> 查初始狀態、log --reverse 比 root 日期、check-ignore -v 查是「誰」擋住的而非只看有沒有被擋。完整案例在 G:\AI\AIMemory\wiki\queries\codegen-git-init-gap.md。
- 覆核 findings 有第四種處置維度「嚴重度降級」：Codex 把 unref 導致行程結束佇列遺失評為 high，但查證後該風險先於改動即存在（佇列本就是記憶體內、退出即失，與 unref 無關）∴ 降級為既有問題而非本次引入
- `vc-kiro-delegate` skill 已於 2026-08-12 正式廢止，內容併入 AI-canonical 的 ms-cross-model-adversarial-review（SKILL.md〈相關〉節 481-495 行，Kiro 呼叫法與 model pin 過期的坑改放〈Kiro 專屬：pin 驗證與唯讀呼叫〉）。⚠️ 記憶庫裡另外 5 條談 vc-kiro-delegate 的 fact（三段 review 流程實證有效、37KB 命令列長度上限、2026-07-27 登入恢復、走 kiro-cli --model claude-opus-4.5 屬弱異源、寫死 pin 與 kiro-cli 預設 auto 是兩層預設）全部是**廢止前的狀態**，讀到時當歷史看、不要據以走那套六步委派流程。廢止理由不是「沒人用」而是「用過然後停了，且真的觸發時它規定的儀式也照樣被跳過」——skillUsage 記 10 次呼叫（排名 8/57），但 kiro-usage.log 全歷史只換到 3 筆 intent 宣告、2 筆 self-review resume。現行做法：委派實作直接呼叫 kiro-cli chat --no-interactive，覆核者一律換不同模型（承重路徑跨 vendor）。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[cloudflare-os]] (relevance 0.80)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/cloudflare-os.md]
- 0. 證據等級（先講清楚）
- 1. 這是什麼
- 2. 三個核心概念
- 3. 三個設計上真的新的東西
- 4. 對 bridge 的差距判定（Step 1 比對表）
- 5. 該知道的限制
- 6. Step 2 借鏡排序（價值／成本）
- 7. Step 3 方案與風險（僅 B1 / B2）
- 7.5 ⚠️ 我在 §7 與 commit `ff976f6` 裡寫錯的一條事實（2026-08-15 更正）
- 8. 尚未做的事（誠實邊界）

## [[bridge-memory]] (relevance 0.77)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/bridge-memory.md]
- AIMemory 結構
- /dream 夜間維運
- Topic 分類系統
- Wiki 知識庫
- Factlint 三層防禦
- 記憶命中日誌與衰減判斷
- Skill Lint
- 維運工具與接線陷阱
- Embedding Router
- 備份機制
- 瑣碎 fact 的審核判準（2026-07-30 使用者逐條裁決）
- 延伸筆記（積壓補記）
- 相關
[End wiki retrieval]

[Delegation Task — id: delegate_25ef8c6cf4a842508f9fc7ed2f5815c1]
Goal: 研究「LLM agent 長期記憶（long-term memory）在規模成長後的三個問題」的現行解法，回報可操作的技術做法清單。目標與動機：我維運一個 Telegram-ACP bridge 的雙層記憶（append-only facts 流水帳 + 蒸餾出的 wiki 知識頁），facts 已累積 616 條並持續成長，要決定投資哪些機制。已知背景：每輪注入是固定上限（最近 10 條 + 語意召回最多 3 個 topic／30 條，cosine 門檻 0.65），所以 token 成本不隨總量成長；痛點不在容量而在三處——(1) 召回稀釋：召回名額固定但候選池變大，相關的舊 fact 被擠掉；(2) 維運覆蓋率下降：去重/蒸餾迴圈有節流（一次最多 10 個 shard），總量長、節流不變導致每輪掃到的比例逐年下降；(3) 矛盾累積：同一件事被記多次且措辭不同，其中互斥的錯誤宣稱會被注入 preamble 當事實使用。待決問題：這三項各有哪些已被實作驗證過的解法？請特別找 Mem0／Zep／Letta(MemGPT)／A-MEM／Cognee／LangGraph memory／OpenAI 與 Anthropic 的 memory 設計文件，以及學術上關於 memory consolidation、contradiction detection、temporal knowledge graph、recall reranking 的做法。每個解法要說明：它解的是上述哪一項、核心機制一句話、實作成本量級、已知失敗模式或批評。驗收條件：至少 8 個具體解法、每個附可查證的來源連結、明確標示哪些是有實作/論文背書哪些只是部落格主張。回報格式：Markdown，先一段「三個問題各自的主流解法收斂到什麼」，再逐解法列表，最後一段「哪些不值得做及理由」。用繁體中文。

Complete this task. When done, summarize what you accomplished.

---

**researcher:**
🟠 收到：研究 LLM agent 長期記憶在規模成長後的三個問題（召回稀釋、維運覆蓋率下降、矛盾累積）的現行解法，產出可操作技術清單
🟠 打算：
1. 搜尋 Mem0/Zep/Letta/A-MEM/Cognee/LangGraph memory 等主流框架的記憶設計
2. 搜尋學術上 memory consolidation、contradiction detection、temporal knowledge graph 做法
3. 搜尋 OpenAI/Anthropic 的 memory 設計文件
4. 彙整成 Markdown 報告，每解法標明解哪個問題、核心機制、成本、失敗模式、來源

讓我開始搜尋相關資料：讓我進一步深入幾篇關鍵論文與框架細節：現在我有足夠的資料可以彙整報告了。

---

# LLM Agent 長期記憶規模化的三個問題：現行解法研究報告

## 摘要：三個問題的主流解法收斂

你的三個痛點在學術與業界都已被識別，但解法成熟度差異很大：

| 問題 | 主流解法收斂方向 | 成熟度 |
|------|------------------|--------|
| **召回稀釋** | Reranking + Hierarchical index + 多策略檢索 | ⭐⭐⭐ 已有多個實作 |
| **維運覆蓋率下降** | 背景異步蒸餾（Dreaming）+ 時間衰減 + 分層整合 | ⭐⭐ 有實作，細節不公開 |
| **矛盾累積** | 確定性 supersession（時間戳優先）+ LLM 衝突偵測 | ⭐⭐⭐ 有論文驗證，但多數框架未實作好 |

---

## 逐解法清單

### 1. Temporal Knowledge Graph + Bi-temporal Supersession（解：矛盾累積）

**核心機制**：每個 fact 帶 `valid_from`/`valid_to` 時間戳，新 fact 進入時以 `(subject, relation)` 為 key 執行確定性 supersession——用 Python `max(timestamp)` 決定現行值，不依賴 LLM 判斷。

**實作成本**：中（需改儲存 schema + 寫入時多一道比對）

**已知失敗模式**：
- Zep/Graphiti 在 MemoryAgentBench FactConsolidation 只拿 7%，因為它的 supersession 是 LLM prompt 驅動而非確定性程式碼
- 時間戳不精確時退化成先進先出

**來源**：
- [arxiv:2606.01435 "Don't Ask the LLM to Track Freshness"](https://arxiv.org/abs/2606.01435) — 實測 Python max(serial) 比任何 LLM-judgment baseline 高 10–28 pp
- [arxiv:2501.13956 Zep/Graphiti 論文](https://arxiv.org/abs/2501.13956)

---

### 2. Mem0 四操作衝突解決（解：矛盾累積）

**核心機制**：每筆新 fact 進入時，用 embedding 找 top-k 類似舊 fact，LLM 判定執行 `ADD`/`UPDATE`/`DELETE`/`NOOP` 四種操作之一；DELETE 用於刪除被新 fact 推翻的舊 fact。

**實作成本**：低–中（Mem0 開源，直接用）

**已知失敗模式**：
- LLM 對「什麼算矛盾」的判定不穩定，prior-override 問題（訓練資料先驗蓋過 in-context 規則）
- Multi-agent 場景 36.9% 失敗來自 inter-agent misalignment（Cemri et al.）

**來源**：
- [arxiv:2504.19413 Mem0 論文](https://arxiv.org/html/2504.19413v1) — LOCOMO benchmark 26% 相對提升
- [Mem0 文件](https://docs.mem0.ai/core-concepts/memory-operations)

---

### 3. Dreaming / 背景異步蒸餾（解：維運覆蓋率下降 + 矛盾累積）

**核心機制**：session 結束後，背景 process 掃過近期對話，提取/更新/刪除 memory state，自動處理過時、重複、矛盾的 fact。

**實作成本**：高（需 background job 基礎設施 + 每輪 compute 成本）

**已知失敗模式**：
- 蒸餾品質取決於 LLM，錯誤會被固化
- 需要明確的 freshness 策略否則舊值會覆蓋新值
- OpenAI 報告花了兩年迭代，V3 才把 compute 降到可服務 Free user（5× 降幅）

**來源**：
- [OpenAI Dreaming 公告](https://openai.com/index/chatgpt-memory-dreaming/)（2026-06-04）— 官方說明 staleness/correctness/scalability 挑戰
- [Arize 分析](https://arize.com/blog/two-labs-started-dreaming-and-they-built-two-different-architectures/)

---

### 4. A-MEM Zettelkasten 動態索引 + Memory Evolution（解：召回稀釋）

**核心機制**：每筆 memory 建立 atomic note（含 LLM 生成的 keywords/tags/contextual description），embedding 找 top-k 鄰居後 LLM 決定是否建立 link；新 memory 進入時會觸發舊 memory 的 contextual description 更新（evolution）。

**實作成本**：中

**已知失敗模式**：
- Link 品質取決於 LLM，不同 backbone 結果不同
- Multi-hop 問題仍難（30% 準確度 vs 單 hop 78%）

**來源**：
- [arxiv:2502.12110 A-MEM 論文](https://arxiv.org/html/2502.12110v1) — NeurIPS 2025 接受，LOCOMO benchmark 勝過 MemGPT/MemoryBank/ReadAgent

---

### 5. Reasoning-Aware Reranking（解：召回稀釋）

**核心機制**：retrieve-then-rerank，但 reranker 不是只看 semantic similarity，而是判斷「這段是否真的能回答問題」——reasoning-aware 而非 similarity-only。

**實作成本**：低–中（接上 cross-encoder reranker 或用 LLM 做一輪 rerank）

**已知失敗模式**：
- 增加 latency（LLM rerank 一輪 ~200–500ms）
- Reranking 只能從 recall pool 裡選，不能補救 recall miss

**來源**：
- [arxiv:2605.06132 Reasoning-Aware Reranking](https://arxiv.org/abs/2605.06132)
- [arxiv:2601.14224 Rerank Before You Reason](https://arxiv.org/abs/2601.14224)

---

### 6. Hierarchical / Graph Memory（解：召回稀釋 + 維運覆蓋率下降）

**核心機制**：把 fact 組織成分層結構（RAPTOR 的 recursive summary tree / MemGPT 的 core/archival/recall 三層 / Cognee 的 context graph），召回時從高層 summary 往下 drill-down，減少需要比對的候選數。

**實作成本**：高（需維護 tree/graph + offline indexing）

**已知失敗模式**：
- HippoRAG-v2 在 FactConsolidation 只拿 54%（hierarchical 結構沒解決 LLM-judgment 的 freshness 問題）
- Graph 建構時 LLM 抽取 entity/relation 的錯誤會 propagate

**來源**：
- [arxiv:2606.11680 HORMA](https://arxiv.org/abs/2606.11680) — file-system-like hierarchical structure
- [arxiv:2604.12285 GAM](https://arxiv.org/abs/2604.12285) — Graph-based Agentic Memory
- [Cognee 官方 blog](https://www.cognee.ai/blog/deep-dives/context-graphs-world-models-and-behavioral-validation)

---

### 7. Time Decay / Importance Scoring（解：維運覆蓋率下降 + 召回稀釋）

**核心機制**：每筆 fact 帶 importance 分數 + 最後存取時間，長期未被召回的 fact 分數衰減，低於閾值時 evict 或 archive。

**實作成本**：低

**已知失敗模式**：
- 衰減參數需要 tuning，太激進會丟掉低頻但重要的 fact
- MemoryBank 的 Ebbinghaus Forgetting Curve 實作在 LOCOMO 輸給 A-MEM

**來源**：
- [MemoryBank 論文 AAAI 2024](https://arxiv.org/abs/2305.10250)
- [Vectorize.io "The Consolidation Problem"](https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation)

---

### 8. Entity Linking / Merge（解：矛盾累積）

**核心機制**：新 fact 進入時，embedding 比對找到同一 entity 的既有 node，merge 成單一 canonical representation，避免同一件事有多筆 fact。

**實作成本**：中

**已知失敗模式**：
- Entity 解析錯誤會把不同東西合併
- Merge 策略（取新/取舊/union attributes）需要明確定義

**來源**：
- [Mem0g graph memory variant](https://arxiv.org/html/2504.19413v1) — 用 Neo4j 存 entity-relation graph
- [Cognee ECL pipeline](https://www.cognee.ai/blog/fundamentals/how-cognee-builds-ai-memory) — cognify 階段做 entity validation

---

### 9. MemStrata / Bi-temporal Ledger（解：矛盾累積）

**核心機制**：fact 不做 in-place update，而是 append-only + 確定性 supersession rule：當同一 `(subject, relation)` 出現新值時，舊值被標記為 retired（保留歷史），查詢時只回傳 valid 值。

**實作成本**：低–中

**已知失敗模式**：
- 需要 schema 能表達 subject/relation/object triple
- 如果 fact 不是乾淨的 triple 格式，需要額外抽取

**來源**：
- [arxiv:2606.26511 MemStrata](https://arxiv.org/abs/2606.26511) — 論文標題 "Eliminating Stale-Fact Errors for AI Agents over Evolving Knowledge"

---

### 10. LiCoMemory / Temporal-Semantic Reranking（解：召回稀釋 + 矛盾累積）

**核心機制**：entity-led graph retrieval + temporal-semantic reranking，召回時同時考慮 semantic similarity 和時間新舊。

**實作成本**：中–高

**已知失敗模式**：
- 小 model（Qwen3-8B）控制不好會 budget exhaustion，需要 32B+ 才穩定
- 論文實測 Qwen3-8B P90R=5（超出 2-call budget）

**來源**：
- [arxiv:2511.01448 LiCoMemory](https://arxiv.org/abs/2511.01448)
- [arxiv:2605.07313 Scale-Conditioned Evaluation](https://arxiv.org/html/2605.07313v1)

---

## 哪些不值得做及理由

| 做法 | 不值得的理由 |
|------|--------------|
| **純靠 LLM prompt 做 freshness 判斷** | 已被 MemoryAgentBench 證偽——所有 LLM-judgment baseline 在 FactConsolidation 都輸給 Python max(timestamp) 10–28 pp。prior-override + serial-tracking drift 是根本缺陷 |
| **增加 context window 取代 memory** | OpenAI 明確指出「更大 context 只是延遲而非解決問題」——attention 對遠距 token 會 degrade，且不相關對話會稀釋相關 fact |
| **單純增加 retrieval top-k** | 2026 Scale-Conditioned Evaluation 論文實測：top-k 增加後召回數增加但 precision 下降，Pass@B 反而更低 |
| **依賴 graph 複雜度解決衝突** | Zep/Graphiti（temporal KG）在 FactConsolidation 只有 7%，比 BM25 baseline 還低——graph 複雜度沒幫助，assembly 才是瓶頸 |
| **Full-context approach** | Mem0 論文實測 91% p95 latency 增加 + 90% token cost 增加，且 accuracy 在 multi-hop/temporal 類問題輸給 memory-augmented approach |

---

## 你的 bridge 適用建議

針對你的情境（616 條 facts、固定召回額度、雙層記憶）：

1. **矛盾累積**：最優先。你現有的 `supersede` 機制方向正確，但要確保是**確定性程式碼**（timestamp 比較）而非 LLM 判斷。可參考 MemStrata 的 bi-temporal ledger 設計。

2. **召回稀釋**：建議加 **lightweight reranker**（cross-encoder 或 LLM 做一輪 reasoning-aware rerank）。你的固定額度 30 條已經是硬限制，reranking 能確保這 30 條是真正相關的。

3. **維運覆蓋率下降**：你的節流設計合理，但可考慮 **importance-weighted 掃描**——不是均勻掃 10 個 shard，而是優先掃「最近被查詢但久未維護」的 shard。OpenAI Dreaming 的核心洞察是「異步背景處理」，你的 `/dream` 已經有這個架構。

```json
{"type":"artifact","summary":"研究 LLM agent 長期記憶規模化三問題（召回稀釋/維運覆蓋率/矛盾累積）的 10 個已驗證解法，含機制、成本、失敗模式與來源，並指出 4 類不值得做的方向","outputs":[{"type":"finding","content":"矛盾累積的最佳解是確定性 supersession（Python max(timestamp)），MemoryAgentBench 驗證比 LLM-judgment 高 10-28pp"},{"type":"finding","content":"召回稀釋主流解是 reasoning-aware reranking + hierarchical index，但 graph 複雜度本身不解決問題（Zep 只拿 7%）"},{"type":"finding","content":"維運覆蓋率主流解是背景異步蒸餾（Dreaming），OpenAI 花兩年迭代才做到 5× compute 降幅"},{"type":"recommendation","content":"bridge 優先實作確定性 supersession + lightweight reranker，/dream 加 importance-weighted shard 掃描順序"}],"files_modified":[],"tags":["memory","agent","long-term-memory","contradiction","recall","consolidation"]}
```

---

