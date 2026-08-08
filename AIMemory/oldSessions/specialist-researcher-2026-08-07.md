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
- [f_52d1ec] [2026-07-14T02:55:14.674Z] vc-uof-hours P3 recon 完成（2026-07-14）：送出按鈕是 frame 2 的 ctl00_MasterPageRadButton13（Telerik RadButton, autoPostBack）；送出後行為是 postback → 簽核 dialog（$uof.dialog.open2, 850x500）→ dialog close；儲存（草稿）是 MasterPageRadButton1；驗證策略用 dialog close + 草稿列表少一筆；三個前置問題已全確認（無撤回、專案負責人非必填、補班不被覆蓋）
- [f_ce6c91] [2026-07-14T03:31:07.365Z] vc-uof-hours P3（加班單真正送出）已實作完成（2026-07-14）：uof_form.py 加入 --submit --token 模式；Phase A 產出 plan.json + 一次性 token；Phase B 五層安全防線全實作（CLI flag / plan+token / 使用者確認 / 欄位比對 / consumed 防重複）；Playwright click RadButton13 觸發 postback + alert 攔截驗證通過；簽核 dialog 因環境限制（無刷卡紀錄）未能實測，handle_sign_dialog 用啟發式偵測；首次真正送出時需觀察簽核 dialog 行為做微調
- [f_c76741] [2026-07-15T01:19:58.386Z] uof_form.py overtime 的已知問題：直接用 JS 填日期欄不會觸發 onchange，導致刷卡時間欄空白；正確做法是點日曆按鈕選日期（觸發 AJAX 查刷卡）→ 等刷卡時間出現 → 再填其他欄位
- [f_16d690] [2026-07-16T03:56:32.137Z] 使用者決定 igs-uof 保留原 vc-uof-hours 的加班單 dry-run 填寫功能（uof_form.py），標註為「個人擴充，非公司共享唯讀範圍」——同事的 v2 設計原本已排除寫入操作；若要把 skill 整包分享給同事需重新評估是否移除該檔案
- [f_02e1bb] [2026-07-17T01:30:04.249Z] uof_form.py overtime 的 submit 流程會把 UOF 的二次確認彈窗（含申請資料摘要的 alert/dialog）誤判為 submit_rejected——實際上第一次 headless submit 就已經成功送出（BAE260706086 於 09:27 申請），腳本需修正確認彈窗處理邏輯
- [f_40460d] [2026-07-30T13:27:05.145Z] 公司內網 UOF（http://uof → https://hq.igs.com.tw/UOF/）於 2026-07-30 前後新增 Cloudflare 反機器人驗證（AntiBotCheck.aspx + Turnstile），headless Playwright 無法通過，導致 igs-uof skill 的所有查詢子命令（hours/attendance/leave/todo/whois）全數失效
- [f_cd9df4] [2026-07-30T13:27:05.145Z] igs-uof skill 的 uof_client.py 登入與首頁導航 timeout 已從 20s 改為 60s（正本 G:\AI\AI-canonical-corp\skills\office\igs-uof\，2026-07-30 尚未進 git）；UOF 首頁在 headless 下實測需約 22 秒才到 DOMContentLoaded
- [f_d0b4fc] [2026-07-30T13:27:05.145Z] 診斷 igs-uof 失敗時不可信任其 unreachable 錯誤訊息：uof_client.py 的 _is_net_error() 把 Playwright Timeout 也歸類為網路錯誤，實際網路多半正常，應先確認是否被 AntiBotCheck 擋住
- [f_c64ef5] [2026-07-30T13:27:05.145Z] 使用者對 UOF 反機器人驗證的處理選擇：不做規避驗證的工程（stealth 參數／指紋偽裝），2026-07-30 遇到時選擇自己上網頁手動查加班時數，未採用 --headed 手動過驗證的路徑
- [f_ecd35a] [2026-07-30T13:27:05.145Z] UOF 加班時數查詢位置：差勤 → 加班統計查詢（Project/BAE/Stats_Search.aspx），設日期區間並勾選簽核狀態「同意」+「簽核中」，看底部平日／假日合計
- [f_d5b5eb] [2026-08-06T00:52:14.026Z] UOF 的 Cloudflare Turnstile（https://hq.igs.com.tw/UOF/AntiBotCheck.aspx，登入成功後才跳）只有「接管非自動化啟動的瀏覽器」能過：2026-08-06 實測 Playwright headless 與 headed 兩臂皆敗（內建 Chromium 與 channel=msedge 真 Edge 都停在 AntiBotCheck，等 241s 未過），可行路徑是 Start-Process msedge --remote-debugging-port=9222 --user-data-dir=<乾淨profile> 讓使用者自己登入+點驗證，再用 playwright connect_over_cdp("http://127.0.0.1:9222") 取既有 page 並直接呼叫 cmd_hours.overtime_range 抓數字——不需任何 stealth 參數或指紋偽裝。過驗證前刻意不用 CDP 碰該頁。
- [f_303689] [2026-08-06T02:05:47.968Z] igs-uof 已在 2026-08-06 加入 CDP 接管模式（commit fce516d，AI-canonical-corp）：查詢被 Cloudflare Turnstile 擋住時腳本現在回明確的 error=antibot（不再誤報 unreachable/scrape_failed），處置是跑 scripts/launch_cdp_browser.py 開瀏覽器→使用者自己登入並點驗證→uof.py --cdp 接管。antibot 有兩種相反處置必須照 hint 走：非 CDP 時「別重試同一條命令」，已在 CDP 卻被中途重新挑戰時「在既有視窗重點驗證後重跑同一條命令、不要重開瀏覽器」。CDP 模式刻意不寫 session.json——storage_state 會把使用者全部網站 cookies 落地成明文（實測連乾淨 profile 都混進 .msn.com/.bing.com，且 chmod 600 在 Windows 是 no-op）。填單路徑的 CDP 模式尚未端到端實測。
- [f_7c41c5] [2026-06-03T12:19:51.275Z] 使用者的機器已安裝 Python youtube-transcript-api、playwright + chromium，可用於抓 YouTube 字幕和 HTML 轉 PDF
- [f_8a4a0e] [2026-06-03T12:19:51.293Z] 使用者偏好 HTML 文件要有目錄錨點跳轉功能（點擊跳段落 + 回目錄連結）
- [f_99b243] [2026-06-03T12:19:51.310Z] 使用者產 PDF 的工作流程：HTML+CSS 排版 → Playwright headless Chromium 渲染（docs/to_pdf.py），不用 fpdf2 或 WeasyPrint
- [f_86246b] [2026-06-09T08:29:22.331Z] 使用者的 Obsidian Vault 位於 C:\Users\jiunchiwang\OneDrive - International Games System\文件\Obsidian Vault\，內含 TypeScript 等技術筆記
- [f_947e7a] [2026-06-24T20:31:30.593Z] 驗證 TypeScript 介面重構或整併時，用 npx tsc --noEmit 做型別檢查；若遇到 TS6.0 的 deprecation 警告，可加 --ignoreDeprecations 6.0 抑制以聚焦真正錯誤。
- [f_a8a12e] [2026-07-06T05:19:36.045Z] 在 bash shell 呼叫 PowerShell 時引號（單引號/$_）會被 bash 層吃掉導致 ParserError，可靠做法是把指令轉 UTF-16LE 再 base64，用 powershell -EncodedCommand 執行
- [f_af2a3f] [2026-07-16T09:36:02.404Z] 使用者這台機器的 gh CLI 尚未執行 gh auth login／未設 GH_TOKEN，研究 GitHub repo 時 gh repo view 等指令會直接失敗，需改用 WebFetch 抓取
- [f_ab7e0a] [2026-07-30T20:31:49.767Z] skill bundle 大幅更新的標準流程：先把未提交檔 commit 建立 restore point → 依差異分三類處理（整包替換／回填缺漏／選擇性合併）→ 被取代的舊 skill 轉成 deprecation pointer 並移除其觸發關鍵字避免撞名搶觸發 → 獨立審查通過才 push。
- [f_9bb794] [2026-07-31T11:33:09.321Z] 在 Bash tool 裡寫多行 git commit message 必須用 bash heredoc，不可用 PowerShell here-string（@'...'@）—— 後者會讓首行多一個 @ 吃掉整個 subject、末行也留一個 @，且 git commit 會照樣成功不報錯（2026-07-31 實證，需 amend 修正）
- [f_129738] [2026-08-02T13:31:37.803Z] 在 Edit 工具做整行刪除或改解構名時，若目標字串在同檔重複出現（如 relay.ts 的 const { runPrompt, sessions } = deps() 全檔 9 個相同字串），必須用上下文定位而非 replace_all，否則會誤改其他 8 處——tsc 只標出未使用的那一處，行號才是唯一可靠依據
- [f_b09bb8] [2026-08-06T03:11:54.658Z] 在 Windows shell 裡把「會 spawn 子進程的命令」接管線（| tail、| grep）會假裝成掛住：管線要等 EOF，而子進程（如 ACP adapter）握著 stdout 不放，即使父進程已經印完結果並退出也看不到任何輸出——2026-08-06 因此兩次誤判 codex-acp 探針「300 秒沒回應」，實際上兩次都成功回了 PONG，殺掉孤兒進程後輸出才一次吐出來。對這類命令要用 `> file 2>&1` 落檔再讀，不要接管線；同理 child.kill() 只殺 shell wrapper，孫進程要另外清（用 CommandLine 比對 + 查 ParentProcessId 存活再殺）。
- [f_ddc6a2] [2026-08-06T10:57:15.181Z] openpyxl 的 `load_workbook(data_only=True)` 讀到的是 Excel 上次存檔時算好的快取值，不是公式本身；由 openpyxl 之類產生器寫出、或存檔前未重算的檔案沒有快取，那些公式格一律讀成 None——2026-08-06 在 excel-to-ai-doc 實測，一張三格全公式的 sheet 整張被判成空白、輸出只剩「此工作表無儲存格內容」，而自我驗證因為刻意跳過 empty sheet 的檢查照樣印「整體：通過」。任何用 openpyxl 讀 xlsx 的腳本都會踩到；解法是另載一次 `data_only=False` 比對，把只有公式沒有快取的格回填公式字串並讓驗證失敗（回填的是 =SUM(...) 不是數值，仍須請對方在 Excel 重新存檔以寫入快取）。
- [f_00d0b6] [2026-08-06T10:57:25.696Z] 用 openpyxl 讀儲存格顏色時，`fill.fgColor.rgb` 只在 `color.type == 'rgb'` 時是字串；Excel 調色盤上排「佈景主題色彩」的 type 是 'theme'、舊調色盤是 'indexed'，只判斷 rgb 是不是字串會靜默漏掉一整類上色（比不做更危險，因為輸出看起來已支援顏色）。theme 要讀 xl/theme/theme1.xml 的 clrScheme，且 Excel 的 theme 索引順序與 XML 排列不同——XML 是 dk1,lt1,dk2,lt2,accent1..6,hlink,folHlink，Excel 索引前兩對互換（0→lt1, 1→dk1, 2→lt2, 3→dk2, 4..9→accent1..6, 10→hlink, 11→folHlink）——再套 tint（ECMA-376：在 HLS 亮度上，tint<0 → L*(1+tint)、tint>0 → L*(1-tint)+tint，HLSMAX 正規化為 1.0）；indexed 走 openpyxl.styles.colors.COLOR_INDEX。
- [f_c3d198] [2026-06-19T07:55:58.294Z] 跨模型 AI 策略 v4 的核心原則:正典語料庫(canonical corpus)本身就是產品——以 markdown + git 追蹤的精煉知識為唯一真實來源(G:\AI\AI-canonical),CLI / MCP / bridge / 索引都只是部署基礎設施而非產品本體。
- [f_7d7ffe] [2026-06-19T07:56:04.782Z] AI 產物的雲端 vs 本地儲存政策:正典 skills、steering 政策與通用文件放公開 GitHub repo(AI-canonical);session 執行日誌與框架內部狀態僅保留本地、不進版控。
- [f_6d4701] [2026-06-27T00:45:09.031Z] memory-to-skill 正本 SKILL.md 已加入 Confidence Scoring 量化門檻（Step 2 後）：confidence = F×C（頻率×成本），≥0.5 進候選、0.3-0.49 留底觀察、<0.3 跳過；靈感來自 ECC continuous-learning-v2 的 instinct confidence scoring
- [f_f92692] [2026-07-14T20:31:29.740Z] 撰寫可攜式 skill 時,若該 skill 會被多個 agent CLI(如 Kiro、Codex、Claude)或多台機器共用,應避免在 SKILL.md 中寫死絕對路徑(例如特定磁碟機代號或使用者目錄),以免跨環境失效。
- [f_e68e53] [2026-07-31T20:47:31.616Z] 使用者的 skill 正本一律寫在 G:\AI\AI-canonical\skills\general\（通用）或 AI-canonical-corp（slot/office），絕不直接編輯 ~/.claude/skills 或 ~/.kiro/skills——那兩處是 sync.ps1 產生的 junction 投影，直接改會被下次 sync 覆蓋
- [f_4568c1] [2026-08-02T13:31:37.803Z] 使用者的 skill 投影機制細節：~/.claude/skills 與 ~/.kiro/skills 下的 skill 目錄是指向 AI-canonical 正本的 junction（非 copy），所以改正本即時對三個 CLI 生效、不需再跑 sync.ps1；sync.ps1 -Apply 真正必要的是 steering 那批 copy
- [f_76462d] [2026-08-05T14:58:05.531Z] sync.ps1（AI-canonical）自 2026-08-05（commit b330aad）起一次投三個 CLI：skills 對 ~/.kiro、~/.claude、~/.codex 各逐 skill junction 直達正本（Codex 原本是二段 junction 繞 Kiro，且整個 skills root 不可 junction 否則蓋掉它的 .system）；steering 對 Codex 走「copy 到 ~/.codex/steering + 全文內嵌 ~/.codex/AGENTS.md 的 canonical-steering managed block」，選內嵌而非 pointer/@import 是因為 Codex 是否支援檔案引用未經驗證，marker 之間每次 sync 覆蓋所以不漂移、marker 外手寫內容保留
- [f_d5d14e] [2026-08-05T14:58:18.745Z] 這台機器的 Codex CLI（0.146.0）在 2026-08-05 時未登入（codex login status → Not logged in、~/.codex 無 auth 檔、bridge .env 也沒有 OPENAI/CODEX key），所以任何「skill/steering 在 Codex 上能不能正確執行」的端到端驗證都做不了，探針會撞 401 Unauthorized；連帶「Codex 是否真的讀 ~/.codex/AGENTS.md 全域指令」仍未實測——官方 docs 說會讀但 openai/codex#8759 與 #27705 報告過全域檔不載入，登入後值得用 canary 字串跑一次 codex exec --skip-git-repo-check 驗證
- [f_0e4a79] [2026-08-05T15:08:54.618Z] Codex CLI 0.146.0 原生支援 skills 機制（掃 ~/.codex/skills/，內建 skill 放 .system/ 子目錄），且 SKILL.md frontmatter 格式與 Claude 完全一致（name + description），因此同一份 skill 正本可三個 CLI 共用不需改寫
- [f_ac4b34] [2026-08-05T15:08:54.619Z] Codex 的 ~/.codex/skills/.system 由 Codex CLI 自己在啟動時重建（2026-08-05 跑 codex exec 後自動多出 review-agent，從 5 支變 6 支），所以該目錄的內容數量會自行變動，投影工具不應把它的變化誤判為外部干擾
- [f_b9e59d] [2026-08-05T15:08:54.619Z] ~/.kiro/steering/karpathy-guardrails.md 沒有對應的 AI-canonical 正本（正本 steering 只有 closed-loop-system / skill-workflow / task-acknowledgement 三支），所以 Kiro 吃著一份 Claude 與 Codex 都拿不到的 steering——待決定是補進正本或確認為 Kiro 專屬
- [f_806752] [2026-08-06T11:05:47.071Z] 【推翻先前記錄】關於「這台機器的 Codex CLI 未登入、端到端驗證做不了」那條 2026-08-05 的 fact 已於 2026-08-06 實測推翻：`codex login status` → Logged in using ChatGPT、版本 0.146.1，當日實跑兩輪 `codex exec` 異源覆核成功；`~/.codex/AGENTS.md` 全域指令是否被讀取也已用 canary 字串實測通過（見 AI-canonical 的 steering/skill-workflow.md），openai/codex#8759 與 #27705 報告的全域檔不載入在此版本不重現。仍未解的是 `codex app-server` 在這台機器壞掉（failed to initialize sqlite state runtime under ~/.codex，穩定重現），而 Claude Code 的 `codex:setup` 是透過 app-server 探測登入狀態，所以它會誤報 loggedIn: false——判斷 Codex 可用性一律以 `codex login status` 為準，不要相信 codex:setup。舊 fact 因被 wiki 頁 concepts/ai-strategy.md 的引用保護，forget 三次皆 deleted=0，故以本條並存推翻而非刪除。
- [f_4e6745] [2026-05-29T16:20:19.509Z] 使用者偏好 agent 回覆時以選項按鈕（<<ASK:...>>）優先，減少需要打字的情況
- [f_70542c] [2026-06-01T12:16:45.051Z] 使用者偏好 git commit 訊息使用中文
- [f_e0ce0f] [2026-06-24T20:31:28.200Z] 使用者偏好 git commit 前先確認：執行 commit 之前應多問幾個釐清問題並取得使用者同意，不要逕自 commit。
- [f_0c44ff] [2026-07-06T02:55:13.600Z] 使用者對非 Claude model 的判斷：DeepSeek 3.2 是非 Claude 裡 coding 最強穩定選項，qwen3-coder-next 超便宜但 experimental 穩定度未知
- [f_be8c07] [2026-07-07T07:52:13.452Z] 使用者的除錯對策偏好：對帳/檢查類函式遇格式不符應「回報不 crash」（守衛 + error log），反對用關掉檢查或 clamp 掩蓋——理由是不用記得開回來、production 遇壞資料也不炸
- [f_a738db] [2026-07-10T00:12:51.617Z] 使用者決定 underused skills 處理策略（2026-07-10）：刪除 skill-creator、knowhow-accumulation、non-engineer-agent-design（磁碟+store），保留 huashu-slides、dual-skill-review-loop、self-eval-prompt-pattern 繼續觀察
- [f_d29dfc] [2026-07-13T13:25:29.299Z] 使用者對會產生真實外部紀錄的自動化（如公司系統表單送出）採保守策略：即使技術上可行，仍選擇只做到 dry-run+截圖、手動確認後才送出，不做一鍵全自動
- [f_99e9ba] [2026-07-30T22:22:40.029Z] 使用者對「純進度/完成記錄」類型 facts 的去留判準：包含技術實作細節（如 selector、防線設計、API 行為）的進度記錄值得保留，純日期綁定的進度快照（如「M0a 完成」「三步驟已完成」）和歷史拆分記錄可刪除
- [f_ebe025] [2026-07-31T11:33:09.321Z] 使用者對承重改動的驗證要求偏好「留下可否證條件」而非宣稱已修好：修法上線時要同時定義出「什麼觀測結果代表原假設是錯的」（2026-07-31 draft H1 修法實測，判讀表區分 status-restore 幀存在但症狀仍在=假設錯）
- [f_48fdd8] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 B 區（規格書結構）決策：寫常見模式而非固定規範（因為每案 sheet 命名不同）
- [f_71c654] [2026-08-05T02:45:22.922Z] Daily Intel 產出的 markdown 檔案在手機上顯示亂碼的問題是因為 UTF-8 without BOM，已於 2026-08-05 在 src/daily-intel/reports/daily.ts 加上 UTF-8 BOM（\uFEFF）修復
- [f_9a7397] [2026-08-05T11:38:02.464Z] G:\AI\AIMemory\wiki 底下沒有 SCHEMA.md（只有 index.md、四個子目錄、兩個 .jsonl），新增 wiki 頁時應比對現有同型頁面的實際 frontmatter 格式（query 型為 title / type / created / updated / sources）
- [f_10d8ff] [2026-08-06T07:06:05.871Z] 編輯 .env 這類含機密的檔案時，使用者接受的做法是：只讀取需要的行範圍（避免把 token 拉進 context）、用 regex 定位而非手抄空白、並以「匹配數必須恰為 1」與「KEY=value 行數前後不變」兩道保險驗證未動到設定值
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
[verification-diagnosis] (relevance 0.55)
- 2026-08-07 方法論教訓：GitHub tree API 的 ?recursive=1 回應被截斷時，WebFetch 背後的小模型會對「存在性」問題自信地答 no——當天它連答「無 pyproject.toml／無 paulsha_cortex/／無 tests/」，一度讓我推論出「這個 repo 只有文件沒有程式碼」，足以推翻整份評估。翻案手法是直接打 raw.githubusercontent.com 的檔案 URL 當二元探針（存在→回檔案內容，不存在→404: Not Found），這個訊號不經摘要判斷、抗幻覺；列子目錄改用 git/trees/main:&lt;path&gt;（不遞迴、JSON 夠小不會截斷）也可靠。∴ 對「某某東西不存在」這類否定式主張，永遠要用探針覆核而非採信摘要——這是既有 research-report-citations-unverified 教訓（引用越像真的越要先查）的反向補完。
- telegram-kiro-bridge 的 `npx tsc -p .` 在 noUnusedLocals 報 TS6133 時仍然會 emit dist，所以「tsc 紅了 = dist 沒更新」這個假設在此 repo 不成立——做突變測試時一律要 grep dist 確認突變真的進了產物才採信 smoke 結果，不可用 tsc 的 exit code 反推（2026-08-06 Fable5 覆核順帶發現；同一天我另外踩到反向的坑：突變寫成 `if (false && …)` 讓 tsc 型別收窄而編譯失敗、dist 沒更新，smoke 跑的是舊產物假綠）。

[adversarial-review] (relevance 0.53)
- 2026-08-07 確立異源覆核的 domain 判定：異源性的單位是模型供應商而非 CLI／harness／分身名字，而 vc-kiro-delegate 走的是 kiro-cli --model claude-opus-4.5，所以「Claude 寫、Kiro 覆核」在模型層是同源（只有 harness/context 不同），屬弱異源——對「換個 context 就會發現」的錯（枚舉漏、敘事與碼不符、恆真斷言）仍有效，對「這個模型本來就會這樣想」的錯（共有推理偏誤、共有知識盲點）沒有防禦力；承重路徑優先跨 vendor（anthropic→openai/Codex）。拿不到強異源時降級不跳過，階梯為 強異源→弱異源→同源重置（只餵 diff 不餵 commit message／註解／AI.md，切斷敘事回音是這一層唯一有效的機制）→不覆核，且降級必須留痕、不可只寫「已覆核」。已寫入 AI-canonical 的 ms-cross-model-adversarial-review SKILL.md（commit 64b4b4e），概念吸收自 hamanpaul/paulsha-cortex 的 ModelIdentity.independence_domain 必填欄位，但刻意不吸收其 fail-closed 攔停。
- ms-cross-model-adversarial-review skill 的覆核者選型已於 2026-08-07 重寫為單表雙軸結構（commit a8e3725 已 push 到 jiunchiwang/ai-canonical）：原本 domain 與 tier 分成兩張表（Q1/Q2），因跨 vendor 覆核連兩輪抓到「兩張表分類軸對不齊」而判定是結構問題非標籤問題，改為一張三欄表（預期的 finding 類型 | domain | tier），「承重路徑」降為前四列（不變式／論證推理缺陷／時序 race／跨模組契約）的合稱而非表中一列；節標題同步改為「domain 與 tier 是兩個獨立的軸」
- Node 的 readdirSync(dir,{withFileTypes:true}) 回的 Dirent 不跟隨連結：junction/symlink 一律 isDirectory()===false、isSymbolicLink()===true——而這台機器的 skill 投影全靠逐 skill junction，所以任何 readdirSync(...).filter(e=>e.isDirectory()) 掃 skill 目錄的碼拿到的都是靜默空集合。scripts/refresh-codex-skill-links.mjs 就這樣壞掉且沒人發現：sourceNames 恆空造成①建立邏輯全斷②移除迴圈把既有 link 全判 stale 刪掉，實測 dry-run 修前 isDirectory()=0/isSymbolicLink()=37 → REMOVE=12 CREATE=0（每跑一次 postinstall 清空一次 Codex），修後 REMOVE=0 KEEP=12 CREATE=25。正確寫法是篩「目錄或指向目錄的 symlink」並用 statSync 跟隨連結確認（斷掉的 link 不算來源）。2026-08-04 曾一度靠讀碼推理判成「下次 npm install 會擴成 37 支」方向完全相反，是異源覆核抓到——這類事情要直接寫 dry-run 跑真實環境而非讀碼推理。
- kiro-cli 自己的預設 model 是 auto 不是 claude-opus-4.5（--list-models 輸出的 * 標在 auto，說明為「Models chosen by task」且不回報實際挑選結果）：不帶 --model 呼叫 Kiro 當覆核者時 domain 不可知，比同源更糟——連「本輪為弱異源」這種降級留痕都寫不出來，所以當覆核者用時一律顯式帶 --model。注意 vc-kiro-delegate 寫死的 claude-opus-4.5 與 kiro-cli 本身的預設是兩層不同的「預設」
- Codex CLI 的 `codex exec -s read-only` 會被執行政策擋掉 git（2026-08-06 實測 0.146.1：`git show`、連 `git --version` 都回 "rejected: blocked by policy"），所以派 Codex 做 push 前異源覆核時必須先用 `git show <commit> > diff.txt` 把 diff 匯出成檔案再餵路徑給它；否則它只能讀工作區現況、完全覆核不到「這次改了什麼」——當天第一輪就是這樣，兩條 finding 全部命中既有缺陷而非本次改動。第二輪改成餵 diff 檔 + `-s workspace-write` 才看得到 commit 內容，但 scratchpad 若在 workspace 之外它仍無法寫檔實跑，只能讀既有 artifact（比獨立重跑弱一階，回報時要標明）。

[bridge-acp] (relevance 0.52)
- Codex 的 ACP adapter 有兩個套件：@zed-industries/codex-acp 已 deprecated（npm 明寫 "replaced by @agentclientprotocol/codex-acp"，停更 2026-06-23，最新 0.16.0；這台機器全域裝 0.15.0），維護中的是 @agentclientprotocol/codex-acp（1.1.9，upstream redkilin 的預設命令）。2026-08-06 raw ACP probe 實測差異：舊版 currentModelId 用斜線 gpt-5.5/medium、effort 只有 low/medium/high/xhigh、sessionCapabilities 整塊缺席；新版 1.1.7 用方括號 gpt-5.6-terra[medium]、effort 多 max/ultra、宣告 resume/list/close/delete/additionalDirectories（對 bridge session resume gate 有意義）。兩者已登入時都回非空 authMethods，所以 authMethodsImplyLoggedOut 的 codex 例外對兩個套件都必要。換套件必須同時改 pin（gpt-5.5 在新版不存在）。新套件經 bridge AcpClient 端到端驗證可用：pinned model=gpt-5.6-terra + reasoning_effort=high 皆確認生效。
- telegram-kiro-bridge 選擇 stdio JSON-RPC 而非 HTTP server mode 與底層 agent CLI 通訊（2026-08-04 QM 研究時確認）：因為 bridge 場景單一 Telegram chat 對應單一 ACP session（不需多 client）、streaming 已靠 ACP 的 session/update notification 解決、沒有跨機器需求（relay 是另一個 bot 不是連同一個 CLI）——成本高（要處理 port 分配、改寫整個 acpClient.ts）收益低。排除 HTTP server mode 因為 kiro-cli 根本沒有 serve subcommand、QM 用 HTTP 是為了支援併發 abort+steer+prompt 與 tool bridging 回打場景，bridge 都用不到
- telegram-kiro-bridge 的 effort 後綴解析（splitEffortSuffix）刻意不無條件拆斜線格式的 currentModelId（如 codex-acp 0.15.0 的 gpt-5.5/medium）：因為 vendor/model 是 model id 的常見寫法，無條件拆會把正常 model 名砍一半、後半誤當成 effort；所以只在後綴命中該 adapter 自己公告的 reasoning_effort 值域時才拆，值域拿不到就不拆（寧可少報 effort，也不謊報 model）——方括號格式（如 gpt-5.6-terra[medium]）因為是專用語法無歧義，維持無條件拆。2026-08-06 commit 7974d27，經 Fable5 覆核抓出兩次恆真斷言（BC-17a 斷言的值其實跟斜線解析無關；兩臂都傳 pin 導致 set_config_option 回應把 effort 蓋回去）才驗證這條邏輯真的成立。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[bridge-project]] (relevance 0.78)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/bridge-project.md]
- 概述
- 子系統索引（已拆分頁）
- 文件事實來源改為原始碼（2026-07-31）
- 文件與教學
- 部署與 Git
- 訊息排版
- Preamble 與 Steering
- 其他功能紀錄
- Process 管理
- SELF_EVAL 量化自評
- bridge-actions MCP（2026-07-16）
- /goal ASK-aware 修復
- /backup acp-trace 洩漏修復
- Turn-Lint 回覆格式機械檢查（2026-07-17）
- Push 前安全機制
- 共享知識庫同步（/sharedsync，2026-07-19）
- 暖機期訊息處理（warmup，2026-07-19）
- GitHub PAT 洩漏事件與 /backup 修復（2026-07-19~22，反覆發生 2 次）
- CI 把關決策（2026-07-25）
- 背景通知與對抗覆核（2026-07-26）
- 已知陷阱
- 積壓修復記錄（2026-08-05 補記，實際發生於 2026-08-01~04）
- 開發環境筆記
- Context 壓縮（Headroom 評估）
- 設計原則
- 相關工具
- 相關

## [[bridge-research]] (relevance 0.77)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/bridge-research.md]
- 概述
- 外部研究對象
- 通用架構教訓
- 改善 Roadmap
[End wiki retrieval]

[Delegation Task — id: delegate_c3a642ae536247a9bacd01c8aa5d711a]
Goal: # 研究任務：Google A2A (Agent-to-Agent Protocol)

## 目標
深度研究 Google 發布的 A2A Protocol，產出結構化研究報告。

## 背景
- 使用者正在開發 telegram-kiro-bridge（Telegram ↔ ACP agent 橋接器）
- 已有 ACP (Agent Client Protocol) 作為主要 agent 通訊協定
- 想了解 A2A 的設計理念、與 ACP/MCP 的差異、以及可能的借鏡點

## 研究範圍
1. **A2A 核心概念**
   - 設計目標與定位
   - 核心抽象（Agent Card、Task、Message、Artifact 等）
   - 通訊模式（HTTP+JSON-RPC vs streaming）

2. **與現有協定比較**
   - A2A vs ACP：定位差異（agent-to-agent vs client-to-agent）
   - A2A vs MCP：工具暴露 vs agent 協作
   - 三者的互補關係

3. **技術細節**
   - Agent Discovery（Agent Card、well-known endpoint）
   - Task lifecycle（pending → running → completed/failed）
   - Streaming 機制（SSE）
   - 認證與授權模式

4. **實作生態**
   - 官方 SDK（Python/JS）
   - 已知的實作案例
   - 成熟度評估

5. **借鏡評估**
   - 哪些概念可用於 bridge 的 specialist/relay 系統
   - 哪些設計可能過度複雜不適合採用

## 驗收條件
- 產出結構化 Markdown 報告
- 包含官方文件的關鍵引用（附 URL）
- 明確標註「確認的事實」vs「推測」
- 結尾給出對 bridge 專案的具體借鏡建議

## 回報格式
```markdown
# A2A Protocol 研究報告

## Executive Summary
（一段話總結）

## 1. 核心概念
...

## 2. 與 ACP/MCP 比較
...

## 3. 技術細節
...

## 4. 實作生態
...

## 5. 借鏡評估
...

## 參考資料
（URL 列表）
```

Complete this task. When done, summarize what you accomplished.

---

**researcher:**
🟠 收到：研究 Google A2A Protocol，產出結構化報告，包含核心概念、與 ACP/MCP 比較、技術細節、實作生態、及對 bridge 專案的借鏡建議
🟠 打算：
1. 搜尋 A2A Protocol 官方資源與文件
2. 研究核心概念（Agent Card、Task、Message 等）
3. 比較 A2A vs ACP vs MCP
4. 調查實作生態與成熟度
5. 產出結構化報告並給出借鏡建議我已取得 A2A 官方規格文件和 GitHub README。讓我繼續搜尋更多比較資料和實作生態資訊。我已收集足夠資料。現在來撰寫完整的研究報告。

---

# A2A Protocol 研究報告

## Executive Summary

Google A2A (Agent-to-Agent) Protocol 是一個開放標準，專門解決 **獨立 AI Agent 之間的通訊與協作** 問題。與 Anthropic 的 MCP (Model Context Protocol) 不同——MCP 是「agent 連接工具/資料」的垂直整合，A2A 則是「agent 對等協作」的水平連接。A2A 的核心設計是讓不同框架、不同組織建構的 agent 能夠在不暴露內部狀態（記憶、工具、推理邏輯）的前提下完成任務委派與結果交換。對 telegram-kiro-bridge 而言，A2A 的 Agent Card 概念（自描述能力清單）和 Task 生命週期（含 input-required、streaming、push notification）值得借鏡，但完整採用 A2A 協定的複雜度可能過高——bridge 的 specialist/relay 系統目前仍在單一信任域內，orchestration 足矣。

---

## 1. 核心概念

### 1.1 設計目標與定位

A2A 解決的問題是：**不同框架、不同公司、不同伺服器上的 AI agent，如何以 peer-to-peer 方式協作，而非作為被呼叫的工具**。

**關鍵設計原則**（官方文件 Section 1.2）：
- **Simple**：複用 HTTP、JSON-RPC 2.0、SSE 等既有標準
- **Enterprise Ready**：內建認證、授權、追蹤、監控考量
- **Async First**：原生支援長時任務、human-in-the-loop
- **Modality Agnostic**：支援文字、檔案、結構化資料、甚至嵌入式 UI
- **Opaque Execution**：agent 不需暴露內部思考、計畫、工具實作

**確認的事實**：A2A 於 2025 年 4 月由 Google 發布，2025 年 6 月捐贈給 Linux Foundation，目前有 150+ 組織支持（含 AWS、Microsoft、Salesforce、SAP）。

### 1.2 核心抽象

| 抽象 | 說明 |
|------|------|
| **Agent Card** | JSON 格式的自描述清單，發布於 `/.well-known/agent-card.json`，宣告 agent 的身份、能力、技能、端點、認證需求 |
| **Task** | 工作的基本單位，有狀態、有生命週期（submitted → working → completed/failed/canceled/input-required/auth-required） |
| **Message** | client/agent 之間的通訊單位，有 role（user/agent）與多個 Part |
| **Part** | Message/Artifact 的內容單位：text、file（raw/url）、data（structured JSON） |
| **Artifact** | Task 的輸出物（如報告、圖片、結構化資料） |
| **Context** | 可選的群組識別符，用於關聯多個 Task/Message |

---

## 2. 與 ACP/MCP 比較

### 2.1 定位差異

| 維度 | MCP | A2A | ACP（bridge 現用） |
|------|-----|-----|-------------------|
| **定位** | agent → tool/resource（垂直整合） | agent ↔ agent（水平協作） | client → agent session（stdio/HTTP） |
| **通訊模式** | client-server，agent 呼叫被動的 tool | peer-to-peer，agent 委派給另一個 agent | client 驅動 session，agent 回應 |
| **狀態** | 規格上 stateless（server 可自行持有狀態） | 有狀態的 Task 生命週期 | session-based，有 checkpoint |
| **Discovery** | 無（需預先設定 endpoint） | Agent Card at well-known URL | 無標準 discovery |
| **核心原語** | tools, resources, prompts | tasks, messages, artifacts, Agent Cards | prompt, session/update, tool calls |

### 2.2 互補而非競爭

Redis 的分析文章總結得很好：

> "MCP connects an agent to its tools and data. A2A connects independent agents to each other."

實務上會同時使用：
- **A2A**：跨組織/跨框架的 agent 協作（如旅行規劃 agent 委派給航班預訂 agent）
- **MCP**：agent 內部呼叫自己的工具（如查資料庫、讀檔案）

**確認的事實**：MCP 現由 Anthropic 發起並於 2025 年 11 月轉移到 Linux Foundation 下的 Agentic AI Foundation；A2A 由 Google 發起並捐給 Linux Foundation。兩者治理正在趨同。

### 2.3 何時需要 A2A？

Redis 文章提出的決策規則：

> "Do you own your agents?"

- **需要 A2A**：agent 跨越你不控制的信任邊界、對方不能暴露內部工具/記憶、任務需要有狀態生命週期（含人工審批）、不同框架必須互通
- **不需要 A2A**：所有 agent 都是你擁有的白盒元件、在同一個 codebase 內、用 LangGraph/CrewAI 等 orchestration framework 即可

---

## 3. 技術細節

### 3.1 Agent Discovery

**Agent Card** 是 A2A 的核心發現機制：

```json
{
  "name": "Research Assistant Agent",
  "description": "...",
  "supportedInterfaces": [
    {
      "url": "https://agent.example.com/a2a/v1",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0"
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "extendedAgentCard": true
  },
  "skills": [
    {
      "id": "academic-research",
      "name": "Academic Research Assistant",
      "description": "...",
      "tags": ["research", "citations"],
      "inputModes": ["text/plain"],
      "outputModes": ["text/plain", "application/json"]
    }
  ],
  "securitySchemes": { ... },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"]
}
```

**確認的事實**：Agent Card 發布於 `/.well-known/agent-card.json`，可選擇性簽章（JWS/RFC 7515）以確保完整性。

### 3.2 Task Lifecycle

| 狀態 | 說明 |
|------|------|
| `TASK_STATE_SUBMITTED` | 已提交，等待處理 |
| `TASK_STATE_WORKING` | 正在處理中 |
| `TASK_STATE_COMPLETED` | 成功完成（終態） |
| `TASK_STATE_FAILED` | 失敗（終態） |
| `TASK_STATE_CANCELED` | 被取消（終態） |
| `TASK_STATE_REJECTED` | 被拒絕執行（終態） |
| `TASK_STATE_INPUT_REQUIRED` | 需要額外輸入（中斷態） |
| `TASK_STATE_AUTH_REQUIRED` | 需要授權（中斷態） |

**亮點**：`INPUT_REQUIRED` 支援 multi-turn 對話，agent 可中途要求澄清；`AUTH_REQUIRED` 支援 in-task 授權委派。

### 3.3 通訊機制

A2A 支援三種更新傳遞方式：

1. **Polling**（GetTask）：簡單，適合低頻更新
2. **Streaming**（SSE）：即時，SendStreamingMessage / SubscribeToTask
3. **Push Notifications**（Webhook）：非同步，適合長時任務

**Protocol Bindings**：
- JSON-RPC 2.0 over HTTP（主流）
- gRPC
- HTTP+JSON/REST

**確認的事實**：版本協商透過 `A2A-Version` header，目前為 `1.0`（v0.3 → v1.0 有 breaking changes，如移除 `kind` discriminator）。

### 3.4 認證與授權

A2A 不自己發明認證機制，而是複用標準：

- **SecurityScheme** 支援：API Key、HTTP Auth（Bearer）、OAuth 2.0、OpenID Connect、mTLS
- Agent Card 的 `securitySchemes` 宣告需要哪種認證
- **In-Task Authorization**：agent 可透過 `AUTH_REQUIRED` 狀態委派授權給 client

---

## 4. 實作生態

### 4.1 官方 SDK

| 語言 | 套件 | 成熟度 |
|------|------|--------|
| Python | `pip install a2a-sdk` | 官方維護，production-ready |
| Go | `go get github.com/a2aproject/a2a-go` | 官方維護 |
| JavaScript | `npm install @a2a-js/sdk` | 官方維護 |
| Java | Maven | 官方維護 |
| .NET | NuGet `A2A` | 官方維護 |
| Rust | `cargo add a2a-lf` | 官方維護 |

**確認的事實**：GitHub repo (`a2aproject/A2A`) 目前 25.2k stars、602 commits、174 issues、58 PRs。

### 4.2 已知實作案例

- **DeepLearning.AI 課程**：Google Cloud + IBM Research 合作的免費課程
- **Google ADK**：Agent Development Kit 原生支援 A2A
- **LinkedIn**：採用 MCP + A2A 建構企業 agent（A2A 仍為實驗性）
- **Google Codelabs**：Purchasing Concierge + Remote Seller Agent 範例

### 4.3 成熟度評估

| 維度 | 評估 |
|------|------|
| **規格穩定性** | v1.0 已發布，有 breaking change 遷移指南 |
| **SDK 完整度** | 六大語言官方支援 |
| **實際生產部署** | 少見，多數仍在探索階段 |
| **跨組織互通** | 理論上設計良好，實際案例稀少 |
| **社群活躍度** | 活躍（150+ 組織、Linux Foundation 治理） |

**推測**：目前大多數標榜「多 agent」的系統，實際上是單一團隊的 orchestrator 呼叫多個工具/專家，並非真正的跨信任邊界 agent 協作。A2A 的價值在後者，但後者的需求尚未普及。

---

## 5. 借鏡評估

### 5.1 可借鏡的概念

| 概念 | bridge 現況 | 借鏡可行性 |
|------|-------------|------------|
| **Agent Card** | specialist 定義在 `specialists.ts`，無標準化自描述格式 | ✅ 高。可為每個 specialist 產生類似 Agent Card 的 JSON，讓 main agent 更好選型 |
| **Task Lifecycle** | delegate 回傳 result/error，無中間態 | ⚠️ 中。`INPUT_REQUIRED` 對 Telegram 對話有用，但會增加 session 複雜度 |
| **Streaming** | 已有（ACP session/update） | — 已具備 |
| **Push Notifications** | 無 webhook，但有 SSE status-server | ⚠️ 低優先。bridge 是單機，webhook 不必要 |
| **contextId/taskId** | session 有 sessionId，無顯式 contextId | ⚠️ 可考慮。目前 chatId 隱式扮演 context |

### 5.2 不建議採用的部分

| 概念 | 理由 |
|------|------|
| **完整 A2A 協定** | 過度複雜。bridge 的 specialist/relay 在單一信任域內，不需要 opaque execution 的保護 |
| **跨組織互通** | 目前無此需求，relay 也是自己控制的 bot |
| **多 binding 支援** | JSON-RPC/gRPC/REST 三套綁定對 bridge 無意義 |
| **標準 Agent Card 發布** | `/.well-known/agent-card.json` 需要 HTTPS 公開端點，bridge 目前是私有部署 |

### 5.3 具體建議

1. **Specialist 自描述格式**
   - 現在 `SpecialistConfig` 已有 `description`
   - 可擴充為類似 Agent Card 的結構（skills、inputModes、tags）
   - 讓 main agent 的 specialist 選型更有依據

2. **Task 中斷態**
   - `INPUT_REQUIRED` 的概念可用於 specialist 回報「需要更多資訊」
   - 目前 delegate 是 fire-and-forget，無中途互動
   - 可考慮讓 specialist 回傳 `{ status: 'input-required', message: '...' }`

3. **contextId 顯式化**
   - 目前 chatId 隱式作為 context
   - 若未來支援跨 chat 的 long-running task，可加入顯式 contextId

---

## 參考資料

| 來源 | URL |
|------|-----|
| A2A 官方規格 | https://a2a-protocol.org/latest/specification/ |
| A2A GitHub | https://github.com/a2aproject/A2A |
| Google 發布公告 | https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability |
| A2A v1.0 升級公告 | https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade |
| Redis MCP vs A2A 比較 | https://redis.io/blog/mcp-vs-a2a-which-protocol-do-you-need/ |
| DeepLearning.AI 課程 | https://goo.gle/dlai-a2a |
| A2A + MCP 文件 | https://a2a-protocol.org/latest/topics/a2a-and-mcp/ |

---

```json
{"type":"artifact","summary":"A2A Protocol 深度研究報告：核心概念、與 ACP/MCP 比較、技術細節、實作生態、及對 telegram-kiro-bridge 的借鏡建議","outputs":[{"type":"finding","content":"A2A 定位是 agent-to-agent 水平協作（peer-to-peer），MCP 定位是 agent-to-tool 垂直整合（client-server），兩者互補非競爭"},{"type":"finding","content":"A2A 核心抽象：Agent Card（自描述能力清單）、Task（有狀態生命週期含 input-required）、Message/Part、Artifact"},{"type":"finding","content":"決策規則：需要 A2A 的情境是跨信任邊界的獨立 agent 協作，同一團隊擁有的 agent 用 orchestration framework 即可"},{"type":"recommendation","content":"bridge 可借鏡 Agent Card 概念為 specialist 建立結構化自描述；可考慮 INPUT_REQUIRED 中斷態讓 specialist 要求澄清"},{"type":"recommendation","content":"不建議完整採用 A2A 協定——bridge 的 specialist/relay 在單一信任域內，A2A 的 opaque execution 保護不必要，複雜度過高"}],"files_modified":[],"tags":["a2a","protocol","mcp","acp","agent-interoperability","research"]}
```

---

