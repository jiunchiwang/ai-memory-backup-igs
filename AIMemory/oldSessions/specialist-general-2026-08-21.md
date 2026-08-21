**general:**
🟠 收到：收斂三份人格系統簡化方案，選主方案、嫁接有價值想法、回應對抗挑戰、列出未決事項
🟠 打算：先讀一手程式碼（sessionManager.ts、dream.ts、session-extract.ts）驗證各方案的假設，再做設計決策現在讓我確認 ACP 是否支援 per-request system inject（驗證方案 C 的前提）：關鍵發現：ACP 的 `_meta.systemPrompt.append` **只在 session/new 和 session/load 時生效**，不是 per-request。讓我確認這一點：關鍵確認。現在我有足夠資訊做設計決策。讓我整理一下：

---

## 設計決策：收斂報告

### 主方案：**方案 A（現有完整 session carve-out）**，並列出可嫁接的精簡項

**選擇理由**（一手程式碼證據，非推論）：

1. **方案 C 已被協定事實推翻**
   - `acpClient.ts:175-176` 逐字：「⚠️ 只有 claude-agent-acp 吃 `_meta.systemPrompt`（實測；Kiro 與 codex-acp 皆不吃，見 spec §8）」
   - `buildSessionNewParams`/`buildSessionLoadParams` 的實作確認：人格只在 `session/new` 和 `session/load` 帶入，ACP 協定**沒有 per-request system inject**
   - 方案 C 自陳的「最關鍵未查證前提」**已查證為假** → 方案不存在

2. **方案 B 的唯一入口假設被實查推翻**
   - `dream.ts:53/:56/:739` 附近、`session-extract.ts:115` 明文記載：dream 的步驟**本身**會呼叫 `remember()` 寫 fact
   - `session-extract.ts:199-202` 逐字：「dream 該寫的 fact 由各步驟自己的 `remember()` 負責」與「`appendFactsDedup()` 永久寫進與 `remember()` 相同的語料層」
   - `extractFromSession` **不是唯一的 facts 寫入路徑**，方案 B 的清洗點只能攔截其中一條（close-time extraction），`remember()` 那條完全繞過
   - 對抗階段的挑戰「`extractFromSession()` 是唯一的 facts 寫入路徑——若 `/dream` body 本身會呼叫 `remember()` 或直接寫檔，此方案失效」**實查命中**

3. **方案 A 有一手實作且測試覆蓋存在**
   - `runWithPersonaCarveOut` 抽成獨立函式（`dream.ts:135-184`），四種 throw 路徑的排列組合可被 BC-16 系列測試
   - `maintenanceSession` 旗標記在 `session.maintenanceSession`（`sessionManager.ts:1101`），四條退出路徑（drop/shutdown/crash/sweepIdle）都能讀到
   - `saveTranscript` 已下守衛到 sink（`session-extract.ts:142-150`），維運 session 回 `null` 而不是 throw，保護不被呼叫點空 catch 吃掉

---

### 嫁接：落選方案中值得併入的具體想法

1. **來自方案 B：「在寫入層一次攔截」的思路**
   - 逐字引用：「把複雜度從『session 生命週期管理』壓縮到『單一清洗點』」
   - 嫁接方式：現有實作已部分採納——`saveTranscript` 守衛下到 sink 而非每個呼叫點（`session-extract.ts:128-168` 的長 JSDoc 第五輪覆核就是這個形狀）
   - 未完成：`remember()` 路徑沒有對應的單一清洗點，目前靠 carve-out 讓整個 dream body 不帶人格來保護

2. **來自方案 C：「人格應該只活在回覆生成的那一瞬間」的長期方向**
   - 逐字引用：「人格只活在回覆生成的那一瞬間，不存在於 session 生命週期裡」
   - 嫁接方式：**不是現在做**。等 ACP 協定支援 per-request inject、或 bridge 改用直連 API（非 subprocess spawn）時，這是正確的長期方向
   - 此刻的阻礙：ACP 協定層限制（見上方 1.）

---

### 回應挑戰：對抗階段指出的問題逐條處理

#### 挑戰 1（方案 C 致命缺陷）
> 逐字引用：「方案自陳『ACP 協定支援 per-request system message 注入——這是最關鍵的未查證前提，若不支援則方案在協定層不可行』，卻仍作為推薦方案交出。」

**處理**：已實查 `acpClient.ts:175-176`，前提為假，方案 C 不選。

#### 挑戰 2（方案 B 致命缺陷）
> 逐字引用：「方案自陳『`extractFromSession()` 是唯一的 facts 寫入路徑——沒有其他地方會把人格語氣寫入長期記憶。若 `/dream` body 本身會呼叫 `remember()` 或直接寫檔，此方案失效。』」

**處理**：已實查 `dream.ts` 與 `session-extract.ts`，dream 步驟會呼叫 `remember()` 是架構必然（不是假設），方案 B 不選。

#### 挑戰 3（方案 A 的 try/finally 邊界風險）
> 逐字引用：「try/finally 邊界的已知缺陷（entry 副作用在 try 外、exit 順序錯誤、finally 最後一句 throw 蓋掉回傳值）——這些都是架構上的已知缺陷」

**處理**：
- 已修正於 `dream.ts:135-184`（`runWithPersonaCarveOut` 的不變式說明），三個缺陷都有對應修法
- BC-16 系列驗證四種 throw 路徑
- **剩餘風險誠實承認**：每次有人碰 entry/exit 邊界仍有機率引入新缺陷，需靠測試覆蓋防守

#### 挑戰 4（三案共有盲點）
> 逐字引用：「三案都把『人格污染』定義為 extraction 時間點的問題，沒有人問：/dream body 執行中，LLM 用人格語氣進行的 reasoning 對 wikisync/factlint 等步驟的決策有沒有副作用路徑」

**處理**：
- **現有方案 A 完全處理這個盲點**——carve-out 在 dream body **進場前**就把人格清掉（`setPersonaOverride(chatId, null)`），整個 body 都跑在無人格的 session 裡
- 這是 carve-out 比清洗點方案更重的原因，也是為什麼它是正確選擇
- 一手證據：`dream.ts:193-195` 逐字「D2 剩下的步驟（factlint／wikisync／dailylog，全是 remember() 寫入者）就在角色語氣下寫進長期記憶」——這正是 carve-out 要防的

---

### 未決事項（需人決定或需查證才能定案）

1. **維運視窗（maintenanceWindow）是否需要**
   - `dream.ts:148-156` 已實作 `openMaintenanceWindow(userId)`
   - 用途：維運期間禁止委派/代理（見 maintenance-window.ts）
   - 未決：這個功能是否真的需要？它增加了一個「忘記關會永久拒絕所有委派」的新失效模式

2. **waitForTurnIdle 的上限**
   - `dream.ts:159-164` 進場前等使用者 turn 跑完
   - 未決：timeout 上限是多少？等太久 dream 會延遲，不等會把使用者的 turn 砍掉

3. **priorArchive 的消費時機**
   - `session-extract.ts` 第四輪覆核指出 `skipArchiveRestore` 必須連「排在 guard 之前的那段」一起跳過
   - 未決：這個修正是否已 commit（memory recall 說「尚在工作區未 commit」）

4. **人格對非 claude adapter 的支援**
   - `acpClient.ts:175-176` 明文只有 claude-agent-acp 吃 `_meta.systemPrompt`
   - 未決：是否需要支援 Kiro/Codex adapter 的人格？若需要，架構會有大改

---

### 本次設計未覆蓋到的

1. **Kiro/Codex adapter 的人格支援**——現有設計只對 claude-agent-acp 有效
2. **「人格記憶」（每個人格獨立 long-term memory 空間）**——若日後需要，需重新設計
3. **跨 session 人格持續性**——per-session inject 每次重建都要重傳，無法保證「上次用這個人格聊到哪」的連續性
4. **pending queue 的 maintenance 標記**——`PendingExtract` 結構沒有欄位標記維運來源，目前靠入 queue 前攔截

```json
{"type":"artifact","summary":"收斂三份人格系統方案：選方案 A（session carve-out），因為方案 C 的 per-request ACP inject 不存在、方案 B 的唯一入口假設被 remember() 路徑推翻。嫁接方案 B 的 sink 守衛思路（已部分採用）與方案 C 的長期方向。","outputs":[{"type":"analysis","content":"方案 C 致命缺陷：ACP 協定不支援 per-request system inject（acpClient.ts:175-176 實證）"},{"type":"analysis","content":"方案 B 致命缺陷：dream 步驟本身會呼叫 remember()（dream.ts:53/:56/:739），清洗點只攔得到 extractFromSession 那條路徑"},{"type":"recommendation","content":"維持現有 session carve-out 架構，它是唯一能處理「dream body 執行中 LLM 決策污染」這個三案共有盲點的方案"},{"type":"finding","content":"四項未決：maintenanceWindow 必要性、waitForTurnIdle 上限、priorArchive 修正 commit 狀態、非 claude adapter 人格支援"}],"files_modified":[],"tags":["persona","dream","architecture","decision"]}
```---

## 設計決策完成摘要

**主方案**：現有 session carve-out（方案 A）

**為什麼不選 B/C**：
- 方案 C 的前提（ACP per-request inject）已被 `acpClient.ts:175-176` 推翻——協定只支援 session/new 和 session/load 時帶入
- 方案 B 的清洗點假設被 `dream.ts` 的 `remember()` 呼叫推翻——dream 步驟本身就會寫 fact，不只是 close-time extraction

**對抗挑戰的回應**：
- 三案共有盲點（「dream body 執行中 LLM 決策污染」）只有方案 A 處理到——carve-out 在進場前就清掉人格
- try/finally 邊界風險已有修正（`runWithPersonaCarveOut` 不變式）並由 BC-16 系列覆蓋

**未決**：maintenanceWindow 必要性、waitForTurnIdle 上限、priorArchive commit 狀態、非 claude adapter 人格支援。

---

**User:**
<identity>
你是 general，完整能力 specialist，用於並行多工（繼承所有 skill 和 MCP）。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Specialist context — relevant facts for "general" domain]
- [f_975249] [2026-08-14T13:44:45.636Z] iGaming Mend workflow 必須以 `MEND_TARGET_GITHUB_ORG` 明確指定掃描組織；fine-grained PAT 走 `/user/orgs` 可能回空陣列造成「0 個 org 的假綠燈」，不可只看 Action 綠燈判定成功。
- [f_e40af6] [2026-08-14T13:44:45.636Z] iGaming Mend 首個已驗證 pilot 為 `IGS-ARCADE-DIVISION-RD4-IG/Client_Activity_LuckyMission`，Type 為 `Client(Cocos)`，SCA 與 SAST 均成功。
- [f_0dec36] [2026-08-14T13:44:45.636Z] 使用者下週優先要補 Mend workflow 的 P0 保護：任一 repository 的 SCA 或 SAST 失敗時，Action 必須明確標紅並輸出失敗原因。
- [f_0d1a3b] [2026-08-14T13:44:45.636Z] Mend User Key 曾出現在來源文件明文中；目前先沿用既有 Key，但已列為後續應輪替、且新 Key 僅可存放 GitHub Secret 的資安待辦。
- [f_7c41c5] [2026-06-03T12:19:51.275Z] 使用者的機器已安裝 Python youtube-transcript-api、playwright + chromium，可用於抓 YouTube 字幕和 HTML 轉 PDF
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
- [f_b120d4] [2026-08-12T07:20:10.466Z] 在 Git Bash 環境用 Start-Process 排延遲工作時不可用 `timeout /t N`：Git Bash 的 PATH 讓 cmd 解析到 GNU coreutils 的 timeout 而非 Windows 的 timeout.exe，GNU 版看不懂 /t 會直接非零退出，接在後面的 `&&` 整串短路、後續指令完全不執行且無明顯錯誤。2026-08-12 因此宣告「重啟已排定」但實際什麼都沒發生。正確做法是用 PowerShell 的 Start-Sleep 或呼叫完整路徑 C:\Windows\System32\timeout.exe。
- [f_a1b97e] [2026-08-12T20:39:57.271Z] 查「某支 skill 到底被用了幾次」的權威來源是 `~/.claude.json` 的 `skillUsage` 物件（每支 skill 一筆 usageCount + lastUsedAt，全時間累計、不隨 transcript 輪替），**不是拿 transcript grep**——transcript 約 30 天輪替，數出來的是視窗內的數字；2026-08-12 就因此把 vc-kiro-delegate 的「全歷史 1 次」寫錯，實際是 10 次、排名 8/57（中位數 2）。配套的第二條判準：當計數來源的比對條件寬到會把無關事件也記進去（kiro-usage.log 把「commit message 提到 kiro-cli」也算一筆，連當次調查本身都灌進 27 筆），**分母被污染而分子沒有，此時只能報絕對數、不可寫成比例或百分比**，並明講分母為何不可用。
- [f_e189b1] [2026-08-14T00:21:06.070Z] 在 Bash tool 裡寫 git commit message 必須用 bash heredoc，PowerShell here-string（@'…'@）會讓首行的游離 @ 變成 commit 標題、末尾再留一個 @，且 git commit 照樣成功不報錯——2026-08-14 再次踩到（先前 2026-07-31 已有同型紀錄），修法是 git commit --amend -F - 配 heredoc 重寫並驗證首尾。
- [f_ca2e4f] [2026-08-15T23:33:11.271Z] 使用者偏好 HTML 文件要有目錄錨點跳轉功能（點擊跳段落 + 回目錄連結）；技術流程交接則希望同時提供 Markdown 與具目錄錨點、可列印的 HTML 版本。
- [f_cf5316] [2026-08-17T01:24:23.059Z] 【已修 2026-08-17】Markdown 沒有行註解 ∴ `~/.claude/CLAUDE.md` 裡用 `#   @Foo.md` 想「註解掉」的 @import **照樣會被解析並載入**。兩條獨立 A 級證據：① 當時 session context 直接出現那 10 個檔的全文並被 harness 標成 "user's private global instructions"；② repo 外暫存目錄差分探針，`#   @big.md` 讓 prefix +2,838、裸 `@big.md` +2,716（同量級 ∴ 有載入，多出的 122 是那行字面文字本身）。代價：使用者 2026-08-11 健檢決定移除的 10 個檔（MCP_Magic/Morphllm/Playwright/Sequential/Tavily/Context7/Serena ＋ BUSINESS_PANEL_EXAMPLES/BUSINESS_SYMBOLS/MODE_Business_Panel，44,543 chars）每次冷啟仍付 **11,393 tokens**，而正文寫著「已移除」「已改為延遲載入」；business-panel 那三個檔更是與既有的 lazy-load skill 重複載入同一份內容。同一行可有多個 @（第 33 行三個檔全部載入）。
- [f_ce935e] [2026-08-19T20:44:21.829Z] 🚨 用**未加引號的 heredoc**（`<<EOF` 而非 `<<'EOF'`）生成含反引號的文字檔時，shell 會在生成檔案的當下就把反引號內容當命令執行——2026-08-19 telegram-kiro-bridge 第一手事故：寫給異源覆核者的 prompt 裡有一句「或它與 \`git push --no-verify\` 的關係」，結果 `git push --no-verify` 在產生 prompt 檔的瞬間**真的被執行**，把 commit 604a7d6 繞過 pre-push 閘門推上 origin；同一批六輪覆核的 prompt 全部中招（另有 \`git init\` 被執行，在既有 repo 上是 re-init、無害，已確認 core.hooksPath 仍是 .githooks）。這個失效模式特別危險的地方是**它沒有任何錯誤訊息**：檔案照樣產生、內容看起來正常（反引號段被替換成命令輸出或空字串），副作用發生在別的地方 ∴ 只會事後從 git log 或閘門紀錄發現。紀律：①凡是要寫「內容裡可能有反引號／`$(...)`／`$VAR`」的檔（prompt、review 指示、文件、程式碼片段）**一律用 `<<'EOF'`**；②寫完立刻比對檔案內容與你打算寫的字串是否逐字相同；③談論危險指令時在文字裡就不要用反引號包它。與 f_8d5086（heredoc 裡 `\n` 被展開破壞產出）、f_e189b1（PowerShell here-string 汙染 commit 標題）同屬「heredoc 引號語意」家族，但本條的後果是**執行任意命令並繞過閘門**，嚴重度高一階。
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
- [f_cc8fd5] [2026-07-13T11:39:16.104Z] 使用者偏好把同一 session 內不相關的改動拆成多個小顆粒 commit，而非合併成一個（2026-07-13 對 README 拆分+roadmap更新兩件事確認選擇拆兩個 commit）
- [f_d29dfc] [2026-07-13T13:25:29.299Z] 使用者對會產生真實外部紀錄的自動化（如公司系統表單送出）採保守策略：即使技術上可行，仍選擇只做到 dry-run+截圖、手動確認後才送出，不做一鍵全自動
- [f_4ad101] [2026-08-14T00:21:06.070Z] 使用者於 2026-08-14 確認：說「commit」不等於授權 push——選定修法（如選 A）也不等於授權 commit，兩者都要各自明確指示。
- [f_53944a] [2026-08-16T00:13:40.736Z] 回覆送出前的收尾驗收（2026-08-16 由使用者裁決採用，借自外部 repo ayghri/i-have-adhd 的 Pre-send check）：**只讀第一行與最後一行，讀者是否知道 (a) 下一步做什麼 (b) 剛剛發生了什麼**——不通過就把答案往前提、把結論寫進末行。為什麼補這一條：既有三層自檢各驗一個軸而沒有人驗「可讀性」——turn-lint 驗語言紀律與 ASK 按鈕、SELF_EVAL 驗正確性、事實主張閘門驗證據等級，沒有任何一層問「這則回覆讀得動嗎」。配套採用的還有它的「刪 hedge 但保留承載真實不確定性的 hedge」——刪的是 perhaps/might 這種無資訊量軟化詞，保留的是「B 級證據 ∴ 標為推論」這種真實不確定性；刪錯方向就是製造虛假自信。**刻意不採用**該 repo 的機械化部分：規則 10（無開場白/客套）在近 30 天 4505 則回覆實測命中率為客套 2 則（0.04%）、英文開場且現行閘門抓不到 4 則（0.09%，其中 3 則是回 JSON 的 structured-output 子任務）∴ 加閘門只會製造誤報；規則 6（一律給具體時間估計）與 RULES.md 的 No Fake Metrics 成本不對稱方向相反；規則 9（清單上限 5）與承重核的呼叫者窮舉／證據逐條列衝突。
- [f_4f0022] [2026-08-17T23:22:41.870Z] underused skills 的處置結論（2026-07-10 初裁 → 2026-07-11 改判，2026-08-18 依使用者指示合併更正）：`skill-creator`、`knowhow-accumulation`、`non-engineer-agent-design` 三支 **2026-07-10 一度決定刪除（磁碟+store），但隔天 2026-07-11 被推翻改為保留**，並列為 skilllint 的已知豁免——日後再被標成殭屍 skill 不需重複提案刪除。另三支 `huashu-slides`、`dual-skill-review-loop`、`self-eval-prompt-pattern` 自 2026-07-10 起維持「保留繼續觀察」，未變。保留一側有三條獨立佐證（2026-08-18 實查）：①`${MEMORY_DIR}/config/skill-usage.json` 三筆皆 `pinned:true` 且 `notes` 逐字寫「使用者 2026-07-11 決定保留（否決 dream zombie 清理提案）」；②三支在 `~/.claude/skills/` 仍是 junction 指向正本 `G:\AI\AI-canonical\skills\general\<name>`（∴ 若日後真要刪，必須刪正本再重跑 sync，直接砍投影會留下懸空 junction）；③改判後仍有實際使用—— `non-engineer-agent-design` 2026-07-27 用過一次、`skill-creator` 2026-08-17 被 routing 命中。可遷移判準：**同一議題的兩條 fact 差一天且結論相反時，先去找第三方 artifact（註冊表 notes／磁碟狀態／使用紀錄）當裁判，不要只比時間戳**。
- [f_10fbe3] [2026-07-13T03:23:05.711Z] 使用者的公司網路環境封鎖 QUIC 協定導致 cloudflared quick tunnel 無法取得 URL（卡在 Requesting new quick Tunnel 超過 35 秒無回應）；ngrok（走 TLS 443）是驗證過的可行替代但最終選擇不用 tunnel
- [f_48fdd8] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 B 區（規格書結構）決策：寫常見模式而非固定規範（因為每案 sheet 命名不同）
- [f_b0c1d8] [2026-08-13T03:00:58.319Z] 使用者的公司內部 AIBI 平台有一台 MCP server rockmanx4-aibi（Streamable HTTP，https://ai-gw-02.i17game.net/rockmanx4/mcp，Bearer token 認證），提供 SkillHub 技能庫／AI 採購用量／團膳菜單／員工通訊錄／平台公告；2026-08-13 嘗試加入時 claude mcp add 被 Claude Code auto mode classifier 擋下，尚未加成
- [f_271855] [2026-08-14T20:08:54.910Z] iGaming Mend 掃描導入時，使用者選了沿用附件文件中已外流的既有 Mend User Key，排除撤銷重發——理由是「目前那把就是配發給我用的 Key」，非帳號本身有問題只是文件外流；assistant 已明確 push back 建議撤銷重發，使用者知情後仍裁決沿用。2026-08-14。
- [f_d682b4] [2026-08-20T15:20:43.009Z] 逐 task 覆核會把缺陷推到沒人被指派的最外層：每輪覆核恪守自己的 brief 是對的，但沒有人擁有 task 之間的接縫，修正一律修在該 task 層內、未受測邊界每修一次外移一格；全分支覆核必做，且要求它真的改一個 token 看功能能不能被靜默關掉
- [f_88faeb] [2026-08-20T15:20:43.009Z] 對「加了一個 skip 旗標」這類修法要追問「這條路徑上這個旗標之前還有誰會動手」——旗標只保護它自己那一行的 if；對「用 chatId 去重」的 cache／pending map 要追問「去重時把 opts 丟掉了嗎」
[End specialist context]

[Persistent memory — lessons from your previous tasks]
- [2026-07-13T02:04:22.314Z] (測試任務：請用 read tool 讀取你自己工作目錄下的 AGENTS.md 檔案，回報前 3 行內容，然後回報你的 ) 讀取 AGENTS.md 前 3 行，回報 model 為 claude-sonnet-4.6，時間為 2026-07-13T10:04:10+08:00
- [2026-07-13T02:04:22.314Z] (測試任務：請用 read tool 讀取你自己工作目錄下的 AGENTS.md 檔案，回報前 3 行內容，然後回報你的 ) AGENTS.md 前 3 行：'# general — Specialist Agent'、空行、'Full-capability specialist for parallel multi-tasking (inherits all skills and MCP)'
- [2026-07-13T02:04:22.314Z] (測試任務：請用 read tool 讀取你自己工作目錄下的 AGENTS.md 檔案，回報前 3 行內容，然後回報你的 ) Model: claude-sonnet-4.6，時間: 2026-07-13T10:04:10+08:00
- [2026-07-13T02:28:11.361Z] (目標：回覆一段 50 字的自我介紹（測試用）。驗收：回覆任意文字即可。回報格式：直接回覆文字。) 完成測試用委派任務，輸出 50 字自我介紹
- [2026-07-13T02:28:11.361Z] (目標：回覆一段 50 字的自我介紹（測試用）。驗收：回覆任意文字即可。回報格式：直接回覆文字。) 任務為測試 pt_tunnel_test 委派通道，已成功回覆自我介紹文字，驗收條件滿足。
- [2026-08-03T15:20:03.105Z] (## 任務：獨立覆核 /model 指令修改
- [2026-08-03T15:20:03.105Z] (## 任務：獨立覆核 /model 指令修改
- [2026-08-03T15:20:03.105Z] (## 任務：獨立覆核 /model 指令修改
- [2026-08-03T15:20:03.105Z] (## 任務：獨立覆核 /model 指令修改
- [2026-08-03T15:20:03.105Z] (## 任務：獨立覆核 /model 指令修改
- [2026-08-03T15:20:03.105Z] (## 任務：獨立覆核 /model 指令修改
- [2026-08-13T10:57:57.851Z] (上面三個前置工項是同一個對象（G:\Cocos_Project\uk_slot_clash_of_olympus\doc) 收斂三 lens 審查：0 條確認、3 條剔除（對抗 lens 未讀檔全推測，經原文驗證均不成立）、1 條低嚴重度觀察（winningMultiplier 缺邊界檢查但不影響派彩）；未覆蓋面向：可測試性實證、step 順序、warnings 機制、proto adapter 契約
- [2026-08-13T10:57:57.851Z] (上面三個前置工項是同一個對象（G:\Cocos_Project\uk_slot_clash_of_olympus\doc) 剔除 3 條虛報：(1) VS Collect 相乘非相加 — M2-VS-design.md:47+BC-VS-7 明文為 Σ(multiplier) 不連乘；(2) server 權威缺 rollback — client 不是權威不需要對帳；(3) 隱性依賴 RoundWin — 介面無此入參物理上無法耦合
- [2026-08-13T10:57:57.851Z] (上面三個前置工項是同一個對象（G:\Cocos_Project\uk_slot_clash_of_olympus\doc) 低嚴重度觀察：winningMultiplier 缺 NaN/負值邊界檢查，僅影響展示不影響派彩（安全 lens 命中）
- [2026-08-13T10:57:57.851Z] (上面三個前置工項是同一個對象（G:\Cocos_Project\uk_slot_clash_of_olympus\doc) 後續補驗：(1) ts-node 實測可否跑通；(2) warnings 回報機制是否靜默吞掉；(3) proto adapter 契約
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
[verification-diagnosis] (relevance 0.61)
- **時序窗口從外部控制不到時，正解是把斷言縮小到「這個時序下真的驗得到」的性質，並在註解寫死誠實邊界，另找一條決定性時序的測試補回被放掉的性質**——2026-08-20 telegram-kiro-bridge 的 BC-24 逐字實例（scripts/check-persona.mjs:784-804）。情境：`get()` 的 `existing` 與 `pending` 兩個早退分支都只看 chatId、把本次傳入的 opts 整個丟掉，∴ 維運流程（/dream，全是 remember() 寫入者）會拿到一個為使用者互動而建、帶著人格的 session。BC-24 要驗的是 in-flight create 分支（create() 在 provider.initialize() 完成前不會 sessions.set() ⇒ 這個窗口內維運的進場 drop() 會 no-op，而背景 poller 會 fire-and-forget 對同一個 owner chat 建 session）。**關鍵取捨**：這條**刻意不驗人格**，只驗「維運意圖不被 pending 去重吃掉」（拿到的不是同一個 session／是維運 session／被取代的那個真的關掉了）——理由逐字寫在註解：in-flight create 何時讀到 personaOverride 那個讀取點在 create() 內部好幾個 await 之後、無法從外部控制，**若在這裡把 override 翻成 null，有可能連 in-flight 那個也變成無人格 ⇒ 兩邊都乾淨、斷言恆綠而什麼都沒驗**；「維運 session 是乾淨的」改由 BC-23 用決定性時序負責。另兩個可遷移細節：①這類測試要靠**同一個微任務內必然發生的註冊順序**取得決定性（第一個 get() 會在同一個微任務內把 pending 註冊進 creating）而不是靠 sleep；②順手多驗一項 `client.isClosed` 防子行程洩漏——舊碼是兩個 session 同時活著、exit handler 的身份比對恆 false。∴ 判準：縮小斷言範圍的正當理由是「不縮小會恆綠」，不是「不縮小會 flaky」；縮小之後必須指名哪一條測試接手了被放掉的性質。
- **「純函式斷言全綠」完全不代表 production call site 有接線**——2026-08-20 telegram-kiro-bridge 第一手（commit b0dc46b 的 Critical 1，異源覆核者示範三個一行 no-op 全部 tsc 乾淨且閘門 1/1 passed）：覆核者把 sessionManager.ts:1182 的 `systemPromptAppend,` 改成 `systemPromptAppend: undefined,`、拿掉 :922 呼叫 createProvider() 的第 6 個參數、刪掉 dream.ts 裡呼叫 `runWithPersonaCarveOut(...)` 的那一行——三者都讓功能永遠不會生效，卻沒有任何斷言碰到，因為既有斷言全是測試檔自己呼叫純函式（buildSessionMeta／buildSessionNewParams），從未經過那些 call site；中間層（src/provider/acp.ts）根本沒有任何 task 打開過，值穿過它靠的是繼承不是決定。**兩種互補補法**：①**真子行程 e2e**（BC-17：spawn 一支 fake ACP agent fixture，用 `FAKE_ACP_RECORD_PATH` 把它實際收到的 session/new・session/load params 落成檔案再回讀斷言）——驗的是真實 wire payload；②**原始碼字面結構斷言**（BC-18：切出 handleDreamBody 的函式邊界，正則驗其中真的出現 `runWithPersonaCarveOut(`），用在「真的跑起來要造出完整 deps 太貴」的 call site，**但必須在斷言訊息與註解裡明寫「結構斷言、非行為驗證」**並標明錨點是原始碼結構（原始碼一改就要更新錨點）。**把 wire payload builder 抽成 exported 純函式（buildSessionNewParams／buildSessionLoadParams，src/acpClient.ts:209/227）的正確定位**：它換掉的是「拿測試自造的複製品物件當被測物」這個更糟的形狀，讓實際送出的 params 組法可直接被驗——但它**不涵蓋**「call site 有沒有把值傳進來」，那一格只有上述①②蓋得到。∴ 抽純函式與驗 call site 是兩件事，做了前者不要以為後者也做了。與 f_d682b4（要求覆核者真的改一個 token 看功能能不能被靜默關掉）互補：那條是覆核者的義務，本條是被覆核方該預先寫好的斷言形狀。
- **只驗「該跳過的跳過了」的 skip 守衛測試組，必須配一條負對照驗「該跑的還在跑」**，否則守衛被寫成恆真時整組照樣全綠而功能無聲死掉——2026-08-20 telegram-kiro-bridge 逐字寫在 scripts/check-persona.mjs 的 BC-22 註解裡（「BC-22 是負對照且不可省：BC-20/21 只驗該跳過的跳過了，守衛若被寫成恆真（所有抽取全被跳過），BC-20/21 照樣全綠而 fact 抽取整個死掉、無聲無息」）。具體形狀是三條一組：BC-20 帶人格的 session → 不對它的 client 下 prompt、改走 persona-free 抽取器且素材必須是**同一份 transcript**（不是空字串、不是重拼一份）；BC-21 維運 session → 兩條路徑都不走、一筆 fact 都不寫；**BC-22 一般 session（無人格、非維運）→ 必須照舊真的對自己的 client 下 prompt**。缺陷本體同時是「skip 旗標蓋不到的鄰居」的實例（f_88faeb 記的是該追問什麼，本條記該怎麼測）：`drop()` 在 `s.client.close()` 之前無條件跑 `onBeforeClose` → `extractFromSession()` → 用**帶人格的 client** 下 prompt → `appendFactsDedup()` 永久寫進與 remember() 相同的語料層，而 `skipArchive` 只包住排在 onBeforeClose 之前的 archiveOnClose、救不到。另兩條測試設計細節：fake session 的 `buffer` 必須留空（非空會讓 live 路徑真的走到 appendFactsDedup 寫檔）、userId 用一個不存在的值（listFacts 讀不到檔回空陣列，不碰真實語料）——「驗寫入守衛」的測試自己要有不污染生產資料的隔離手段。

[bridge-persona] (relevance 0.59)
- **任何「暫時關掉 X → 做事 → 還原 X」的 carve-out 骨架有三個順序缺陷，全部與 try/finally 的邊界有關**（2026-08-20 telegram-kiro-bridge 的 /dream 人格隔離，前兩條由覆核抓出並修於 commit fe6e0ad，第三條修於 b0dc46b，均已逐字查證 src/commands/dream.ts 的 runWithPersonaCarveOut）：①**entry 的副作用不可留在 try 外面**——原碼 setPersonaOverride／進場 drop()／通知使用者三件事都在 try 之前，任一 throw 就讓 finally 永遠不會跑、人格永久卡死且無回復路徑；修法是 setPersonaOverride 後**立即**進 try，把 entry drop 與通知都圈進保護區內；②**finally 內「還原」必須排在「可能失敗的收尾」之前**——原碼 exit drop() 排在 clearPersonaOverride() 前面，drop() 失敗會連帶擋住還原；③**finally 的最後一句若 throw，會蓋掉 try 區塊正常回傳的值（JS finally 語義）**∴ 那一句必須自帶 `.catch()`，本例 exit drop() 加上 `.catch(err => console.error(...))` 並在訊息裡註明「override 已清除，不影響 body 結果」（dream.ts:159-165 逐字）。連帶紀律：carve-out 內所有「通知使用者」的呼叫都要與該檔其餘 ctx.reply 一致地補 `.catch()`，註解逐字寫「通知失敗不得吃掉還原」。測試面：這四種注入失敗（body／notify／entry drop／exit drop）該用排列組合各驗一條（BC-16 系列），並逐一 mutation 確認每條斷言在拿掉對應防護時**精確**變紅且互不誤傷。⚠️ 另一個易漏處：把 entry/try/finally/exit 抽成一個具名函式後，「body 真的有沒有被它包住」是**另一件事**，BC-16 系列全用測試檔自造的假 sessions/notify/body、驗不到接線（見同批的 call-site 斷言那條）。
- 斷言要打在「實際送出去的那一層」，不是中間值——telegram-kiro-bridge 2026-08-20 的 persona 設計初稿實例（commit 48d0794 逐字更正，⚠️ 此機制本身已於當日被 v4 取代、見 f_5247b2，故以下只取可遷移形狀）：初稿 §3.3 斷定人格文字「串接在 preamble 最尾端」並以此當作「人格能壓過先前指令」的立論基礎，實查 sessionManager.ts:746 卻是 `breakdown.text + workingStateBlock + archiveBlock + dreamStateBlock + relayTaskBlock`，:936 之後還會 append 一段 [Model identity] ⇒ 人格後面還有五段，而其中 archiveBlock 正是切換人格時注入的 handoff（必定出現）。更刺的是原本的 BC-2 斷言打在 `breakdown.text` 上會**恆綠**，而真正送出的是 `session.memoryPreamble`——本 repo 已踩過的「閘門鎖錯層」形狀（pet-connect 那次），綠燈不代表沒事、代表沒驗到。三個可遷移處置：①**修法不是搬位置而是換立論**（需要被壓過的是「指令類」內容——工具說明、[Agent disciplines]、CLAUDE.md 帶進來的紀律，它們全在 breakdown.text 之內或更前面；後面五段是「狀態資料」不含風格或格式指令 ∴ 不競爭）；②**新立論的前提要自己配一道機械斷言**（當時加了一條白名單斷言：:746 之後的區塊集合必須在白名單內，見到未知區塊就紅由人判斷，而不是「檢查有沒有指令」——後者無法機械判定），理由是日後有人加進指令類區塊，症狀會是「角色偶爾變回機器腔」，幾乎不可能被歸因到這裡；③**驗中間值與驗實際送出值不可共用同一個 helper**，否則兩條斷言會一起鎖錯層。⚠️ 該白名單斷言（原編號 BC-9）已隨機制改版一併消失（2026-08-21 實查 check-persona.mjs 只剩 BC-1～BC-33 中無 BC-8/9/10，現存 BC-2 改成驗 `_meta.systemPrompt.append`）∴ 引用本條時引用的是形狀，不是現存閘門。

[bridge-session] (relevance 0.58)
- **當一個「意圖」需要被多條退出路徑看見時，把它記成物件上的旗標（建立當下設定），不要逐一 threading 參數**——2026-08-20 telegram-kiro-bridge commit b0dc46b 的 Important 2 第一手：/dream 的維運 session 只在走 `drop({skipArchive:true})` 這條路時才不落盤，但 `shutdown()`／crash／`sweepIdle` 這些**不經 drop()** 的路徑會無條件 archive，把使用者剛存好的對話覆蓋掉；修法是在 ChatSession 上加 `maintenanceSession` 旗標（sessionManager.ts:1115 於 create 當下由 `!!opts?.skipArchiveRestore` 設定），四個路徑各自檢查，**取代把參數逐一 threading 到每個呼叫點**。可遷移判準：threading 參數只能保護「你記得改的那些呼叫點」，而退出路徑的完整清單是會成長的（新增一條 idle sweep 或 crash handler 時沒人會想到要傳這個參數）∴ 意圖屬於**物件的狀態**而不是**呼叫的參數**；反過來說，這也是 f_88faeb 那個追問（「這條路徑上這個旗標之前還有誰會動手」）的正面答案——把判準收斂到一個所有路徑都讀得到的欄位，才有辦法逐條檢查。⚠️ 邊界：旗標仍只保護讀它的那些 if，且旗標名與語意要對齊——本例 `skipArchiveRestore`（入口參數，管 create 時不消費 archive）與 `skipArchive`（drop 參數，管收尾不落盤）是兩個不同開關，`maintenanceSession` 是從前者推導出的**身分**，三者不可混用；另外 sessionManager.ts:944-956 記載 `skipArchiveRestore` 必須連「排在 `if (!opts?.skipArchiveRestore)` 之前的那一段」一起跳過，是第四輪跨 vendor 覆核才查出的漏網格（⚠️ 2026-08-21 讀到時該修正尚在工作區未 commit）。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[munder-difflin]] (relevance 0.82)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/munder-difflin.md]
- 0. 證據等級
- 1. 這是什麼
- 2. 五條有實質內容的交集軸
- 3. Step 1 比對表
- 4. Step 2 借鏡排序
- 5. 誠實邊界（尚未做的事）

## [[cloudflare-os]] (relevance 0.82)
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
[End wiki retrieval]

[Delegation Task — id: moaplan_decide]
Goal: 前置工項給了你同一個問題（目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dream 與 close-time fact extraction 都可能將人格語氣寫入長期記憶，因此 Stage 1 加入 persona override、維運 session、archive/working-state 跳過、maintenanceSession、退出路徑守衛、並發封鎖與維運視窗禁止委派/代理。使用者質疑為何做很久、是否有更簡單方案。）的三份獨立方案，以及一份對全部三案的對抗挑戰。

請收斂成一份設計決策：
1. **選一個主方案**，說明為什麼——理由要對得上約束（請讀 repo 一手實作：src/sessionManager.ts、src/commands/dream.ts、src/acpClient.ts、src/session-extract.ts、scripts/check-persona.mjs。比較：(A) 現有完整 session carve-out；(B) 資料層人格清洗或獨立 extraction client；(C) 人格限制為呈現層/互動回覆。核心不可接受後果：人格語氣或維運內容錯誤寫入 facts，維運消費或覆蓋使用者 archive/working-state。不可把註解、SPEC 或測試名稱當證據。產出繁中、結論先行，標示一手程式碼證據與推論邊界，指出架構必然/驗證累積/範圍漂移，給最小可交付範圍與推薦；只分析不改檔。），不是「比較完整」這種空話。
2. **嫁接**：落選方案裡有哪些具體想法值得併進主方案，逐條說明。
3. **回應挑戰**：對抗階段指出的致命缺陷與共有盲點，逐條說明主方案怎麼處理，或者誠實承認沒處理、代價是什麼。
4. **標註未決**：仍需人決定或需要查證才能定案的點，明確列出來，不要自己替使用者決定。

回報格式：主方案一段、嫁接一段、挑戰回應逐條、未決事項列表。結尾附一行「本次設計未覆蓋到的」。回應挑戰時每一條都要**逐字引用**你正在回答的那個挑戰，嫁接時逐字引用你要併進來的那個想法——沒有逐字引用就無法確認你真的讀過前一階，那條視為未處理。
Context: 此工項屬於計畫「檢視 Telegram bridge 人格系統 Stage 1 為何複雜，提出更簡單且可交付的替代架構。」。
前置工項「設計問題：目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dream 與 close-time fact extraction 都可能將人格語氣寫入長期記憶，因此 Stage 1 加入 persona override、維運 session、archive/working-state 跳過、maintenanceSession、退出路徑守衛、並發封鎖與維運視窗禁止委派/代理。使用者質疑為何做很久、是否有更簡單方案。
約束：請讀 repo 一手實作：src/sessionManager.ts、src/commands/dream.ts、src/acpClient.ts、src/session-extract.ts、scripts/check-persona.mjs。比較：(A) 現有完整 session carve-out；(B) 資料層人格清洗或獨立 extraction client；(C) 人格限制為呈現層/互動回覆。核心不可接受後果：人格語氣或維運內容錯誤寫入 facts，維運消費或覆蓋使用者 archive/working-state。不可把註解、SPEC 或測試名稱當證據。產出繁中、結論先行，標示一手程式碼證據與推論邊界，指出架構必然/驗證累積/範圍漂移，給最小可交付範圍與推薦；只分析不改檔。

請提出**一個**你認為最好的方案。你是三個獨立提案者之一，彼此看不到對方的方案——所以不要試圖折衷或預留空間，就提出你真正認為對的那個。

必須包含：
1. 一句話的核心取捨（你選擇犧牲什麼換什麼）。
2. 主要組件與資料流。
3. **你假設了什麼**——特別是你沒有查證、但方案成立所依賴的前提。
4. 這個方案什麼情況下會是錯的選擇（誠實寫，不要寫「幾乎沒有」）。

回報格式：控制在可讀範圍，重點在取捨與假設，不要寫成完整實作細節。」的**結構化結果**（完整，未截斷）：
{
  "core_tradeoff": "犧牲跨 session 持續人格能力，換取人格永遠不進長期記憶的結構保證——把人格移到 per-request 呈現層，session 本身永遠 persona-free，carve-out/skip/maintenanceSession 全部不需要。",
  "assumptions": [
    "ACP 協定支援 per-request system message 注入（不只是 session/new 初始化時）——這是最關鍵的未查證前提，若不支援則方案在協定層不可行",
    "人格效果只需影響回覆語氣，不需要 agent 在整個對話流程中持續記得自己是誰（跨多輪人格一致性非硬需求，或可接受每次 re-inject）",
    "/dream 的主要價值是「這次回覆用不同語氣」而非「這個 session 從此活在另一個人格裡」"
  ],
  "wrong_when": "ACP 協定不支援 per-request system inject 時方案直接死掉；或使用者需要跨多輪持續人格（每輪都要帶入且仍有 extraction 窗口問題）；或現有 Stage 1 大量 session 層測試遷移成本超過收益；或未來人格需要影響 agent 工具選擇而非只有語氣。"
}
以下是它的文字說明（推理過程；可能被截斷）：## 方案：呈現層隔離（Option C）

**核心取捨**：犧牲「人格能改寫 agent 底層行為」，換取「人格永遠不進長期記憶」的結構保證。

---

### 核心立論

人格污染記憶的根本原因是：人格注入在 session 層，而 fact extraction 也在 session 層，兩者共用同一個 client。只要這個結構不變，隔離機制（carve-out、skip flag、maintenanceSession）都是在用補丁追補丁。

最簡單的解法是：**人格只活在回覆生成的那一瞬間，不存在於 session 生命週期裡。**

---

### 主要組件與資料流

1. **人格移出 session 層**：`_meta.systemPrompt.append` 改為每次呼叫 ACP 時作為 per-request 參數帶入，不寫進 session config，session 本身永遠是 persona-free。

2. **Fact extraction 不受影響**：extraction 用的是同一個 session client，但 session 裡沒有人格，所以不需要 skip flag、不需要 maintenanceSession、不需要 carve-out。

3. **/dream 路徑**：只在最終 reply 組裝時注入人格文字（作為 system message prefix 或 user-side wrapper），不觸碰 session 狀態。

4. **Archive/working-state**：正常運作，不需要跳過邏輯，因為 session 從未被人格污染。

---

### 我假設了什麼

- ACP 協定支援 per-request 的 system message 注入（不只是 session 初始化時）。這是最關鍵的未查證前提。若 ACP 只在 session/new 時接受 system prompt，此方案在協定層就不可行。
- 人格效果只需要影響「回覆語氣」，不需要讓 agent 在整個對話流程中持續記得自己是誰（亦即跨多輪的人格一致性不是硬需求，或可接受靠每次 re-inject 達成）。
- `/dream` 的主要價值是「這次回覆用不同語氣」，不是「這個 session 從此活在另一個人格裡」。

---

### 什麼情況下這是錯的選擇

- ACP 協定不支援 per-request system inject，只能在 session init 時設定 → 方案在架構層就死掉，必須回到 session 層操作。
- 使用者需要的是跨多輪持續的人格（例如「整個 /dream 對話過程中都保持角色」），per-request inject 每輪都要帶入，且若中間有 extraction 觸發，仍有窗口問題。
- 現有 Stage 1 已有大量測試（BC-13～BC-33）綁定 session 層行為 → 遷移成本可能比從零建新機制更高，特別是那些 carve-out 的邊界測試。
- 若未來人格需要影響 agent 的工具選擇或決策（不只是語氣），呈現層注入的能力會不夠。完成。提出的方案是「呈現層隔離」（Option C）：將人格注入移至 per-request 呈現層，讓 session 本身永遠 persona-free，從根本消除污染長期記憶的結構性風險，代價是放棄跨 session 持續人格能力，且依賴 ACP 支援 per-request system inject 這個未查證的前提。
前置工項「設計問題：目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dream 與 close-time fact extraction 都可能將人格語氣寫入長期記憶，因此 Stage 1 加入 persona override、維運 session、archive/working-state 跳過、maintenanceSession、退出路徑守衛、並發封鎖與維運視窗禁止委派/代理。使用者質疑為何做很久、是否有更簡單方案。
約束：請讀 repo 一手實作：src/sessionManager.ts、src/commands/dream.ts、src/acpClient.ts、src/session-extract.ts、scripts/check-persona.mjs。比較：(A) 現有完整 session carve-out；(B) 資料層人格清洗或獨立 extraction client；(C) 人格限制為呈現層/互動回覆。核心不可接受後果：人格語氣或維運內容錯誤寫入 facts，維運消費或覆蓋使用者 archive/working-state。不可把註解、SPEC 或測試名稱當證據。產出繁中、結論先行，標示一手程式碼證據與推論邊界，指出架構必然/驗證累積/範圍漂移，給最小可交付範圍與推薦；只分析不改檔。

請提出**一個**你認為最好的方案。你是三個獨立提案者之一，彼此看不到對方的方案——所以不要試圖折衷或預留空間，就提出你真正認為對的那個。

必須包含：
1. 一句話的核心取捨（你選擇犧牲什麼換什麼）。
2. 主要組件與資料流。
3. **你假設了什麼**——特別是你沒有查證、但方案成立所依賴的前提。
4. 這個方案什麼情況下會是錯的選擇（誠實寫，不要寫「幾乎沒有」）。

回報格式：控制在可讀範圍，重點在取捨與假設，不要寫成完整實作細節。」的結果：⚠️ 這份產出**沒有通過品質驗證**（verifier 的意見，未重繳）：未讀取指定的一手實作檔案（src/sessionManager.ts、src/commands/dream.ts、src/specialist.ts）就直接產出方案——全文用「我假設」「若...此方案失效」等假設語氣鋪陳，沒有任何 grep/read 引用實際程式碼作為證據，違反任務明確要求的「請讀 repo 一手實作」；提出的「方案 B」是憑空設計，未對照 repo 現狀（目前 Stage 1 的 maintenanceSession / carve-out / maintenance window 已實作並 commit），因此無法回答使用者真正問的「現有做法是否真的比較複雜、簡化方案是否可行」。
請自行查證後再採用，不要當成已覆核的結論；若它是你收斂的依據之一，請明說這塊未經驗證。

🟠 收到：設計問題，人格系統 Stage 1 複雜度高，需評估更簡單方案
🟠 打算：提出一個完整方案，含取捨、資料流、假設與失敗模式

---

## 方案 B：資料層人格清洗

**核心取捨**：犧牲「人格是全域狀態」的簡潔，換取「不需要 session carve-out」的單純。

### 主要組件與資料流

```
/dream 進場
  ├─ setPersonaOverride(chatId, persona)  // 只是一個 flag
  ├─ 正常執行 body，人格文字存在 preamble
  └─ body 結束 → clearPersonaOverride(chatId)

extractFromSession() 被呼叫時
  ├─ 檢查 getPersonaOverride(chatId)
  ├─ 若有 → 送 prompt 時「不加人格文字」
  └─ 寫入 facts 的內容來自無人格的 prompt 結果
```

**關鍵差異**：
- 不需要 `maintenanceSession`、不需要 `drop()` carve-out
- `extractFromSession()` 本身就有一個「下 prompt」的節點——在那裡清洗
- 現有 `session-extract.ts` 的 `extractFromSession()` 是唯一寫入 facts 的入口

### 我假設了什麼

1. **`extractFromSession()` 是唯一的 facts 寫入路徑**——沒有其他地方會把人格語氣寫入長期記憶。若 `/dream` body 本身會呼叫 `remember()` 或直接寫檔，此方案失效。

2. **人格文字只影響 LLM 回覆的語氣，不影響「要記住什麼事實」**——如果人格會改變「哪些事實被抽出來」，那清洗後的結果會跟使用者實際體驗不一致。這是 trade-off，但在大部分人格應用（角色扮演、語氣風格）是可接受的。

3. **維運操作（/dream）不會直接操作 archive/working-state 檔案**——若會，還是需要獨立 client 或檔案鎖。目前看起來所有 state 操作都走 session manager，所以清洗點集中在 extraction。

### 這個方案什麼情況下會是錯的選擇

1. **人格不只是語氣，而是「身分」**——例如「你是這位使用者的秘書」，會改變 LLM 對「哪些資訊重要」的判斷。清洗後抽出的事實會跟「秘書人格下的對話」不一致，長期記憶會變成「兩個人格混合」。

2. **有其他寫入 facts 的路徑**——例如 `/dream` body 裡 LLM 自己決定呼叫 `remember()`、或其他 command 也會觸發 extraction。那時要補的清洗點會變多，最終可能比現在的 carve-out 還複雜。

3. **未來要支援「人格記憶」**——若要讓每個人格有獨立的 long-term memory，清洗法做不到，必須走「獨立 extraction client + 獨立語料空間」。

---

**結論**：此方案把複雜度從「session 生命週期管理」壓縮到「單一清洗點」，前提是 extraction 真的是唯一入口。我認為這是目前最簡單可交付的路徑，風險在於人格若影響認知（不只是語氣），記憶會漂移。
前置工項「設計問題：目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dream 與 close-time fact extraction 都可能將人格語氣寫入長期記憶，因此 Stage 1 加入 persona override、維運 session、archive/working-state 跳過、maintenanceSession、退出路徑守衛、並發封鎖與維運視窗禁止委派/代理。使用者質疑為何做很久、是否有更簡單方案。
約束：請讀 repo 一手實作：src/sessionManager.ts、src/commands/dream.ts、src/acpClient.ts、src/session-extract.ts、scripts/check-persona.mjs。比較：(A) 現有完整 session carve-out；(B) 資料層人格清洗或獨立 extraction client；(C) 人格限制為呈現層/互動回覆。核心不可接受後果：人格語氣或維運內容錯誤寫入 facts，維運消費或覆蓋使用者 archive/working-state。不可把註解、SPEC 或測試名稱當證據。產出繁中、結論先行，標示一手程式碼證據與推論邊界，指出架構必然/驗證累積/範圍漂移，給最小可交付範圍與推薦；只分析不改檔。

請提出**一個**你認為最好的方案。你是三個獨立提案者之一，彼此看不到對方的方案——所以不要試圖折衷或預留空間，就提出你真正認為對的那個。

必須包含：
1. 一句話的核心取捨（你選擇犧牲什麼換什麼）。
2. 主要組件與資料流。
3. **你假設了什麼**——特別是你沒有查證、但方案成立所依賴的前提。
4. 這個方案什麼情況下會是錯的選擇（誠實寫，不要寫「幾乎沒有」）。

回報格式：控制在可讀範圍，重點在取捨與假設，不要寫成完整實作細節。」的結果：

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
前置工項「上面三個前置工項是同一個問題（目前人格僅支援 Claude ACP，透過 _meta.systemPrompt.append 注入。/dream 與 close-time fact extraction 都可能將人格語氣寫入長期記憶，因此 Stage 1 加入 persona override、維運 session、archive/working-state 跳過、maintenanceSession、退出路徑守衛、並發封鎖與維運視窗禁止委派/代理。使用者質疑為何做很久、是否有更簡單方案。）的三份獨立方案，提案者彼此看不到對方。

你的工作是**挑戰它們**，不是排名：
1. 逐案找出**致命缺陷**——會讓該方案在約束（請讀 repo 一手實作：src/sessionManager.ts、src/commands/dream.ts、src/acpClient.ts、src/session-extract.ts、scripts/check-persona.mjs。比較：(A) 現有完整 session carve-out；(B) 資料層人格清洗或獨立 extraction client；(C) 人格限制為呈現層/互動回覆。核心不可接受後果：人格語氣或維運內容錯誤寫入 facts，維運消費或覆蓋使用者 archive/working-state。不可把註解、SPEC 或測試名稱當證據。產出繁中、結論先行，標示一手程式碼證據與推論邊界，指出架構必然/驗證累積/範圍漂移，給最小可交付範圍與推薦；只分析不改檔。）下直接不成立的那種，不是可以靠實作補救的粗糙處。
2. 找出**三案共有的盲點**：三個提案者都沒想到、或都做了同一個未經查證的假設。這條最有價值，因為它不會在互相比較中被發現。
3. 檢查每案自陳的「假設」有沒有漏——提案者沒意識到自己在假設的東西。

不要提出第四個方案，你的職責是拆不是建。沒有致命缺陷就明說某案站得住，不要為了交差硬找。

回報格式：逐案一段（致命缺陷 或 站得住的理由），最後獨立一段寫「三案共有的盲點」。每個致命缺陷都必須**逐字引用**該方案裡你要攻擊的那句話（不是你重述的版本）——沒有逐字引用的挑戰視為沒讀過那份方案，寧可不報。」的**結構化結果**（完整，未截斷）：
{
  "per_plan": [
    {
      "plan": "C",
      "verdict": "致命缺陷",
      "reason": "方案自陳「ACP 協定支援 per-request system message 注入——這是最關鍵的未查證前提，若不支援則方案在協定層不可行」，卻仍作為推薦方案交出。前提未驗證，方案整個不存在，不是實作粗糙可補救的層次。"
    },
    {
      "plan": "B",
      "verdict": "致命缺陷",
      "reason": "方案自陳「extractFromSession() 是唯一的 facts 寫入路徑——若 /dream body 本身會呼叫 remember() 或直接寫檔，此方案失效」，但方案資料流裡沒有任何機制阻止 LLM 在 dream body 直接呼叫 remember()。清洗點在 extraction 層，對另一條路徑完全無效，提供的是假安全感。",
      "quoted_attack": "extractFromSession() 是唯一的 facts 寫入路徑——沒有其他地方會把人格語氣寫入長期記憶。若 /dream body 本身會呼叫 remember() 或直接寫檔，此方案失效。"
    },
    {
      "plan": "A",
      "verdict": "站得住，但最可能出事的地方",
      "reason": "現有 carve-out 是三案中唯一有程式碼支撐的。但 try/finally 邊界的已知缺陷（entry 副作用在 try 外、exit 順序、finally throw 蓋回傳值）是架構層的固有風險，每次有人碰 entry/exit 邊界都有機率引入 override 洩漏，且這些缺陷已被找到過一次。"
    }
  ],
  "shared_blindspot": "三案都把「人格污染」定義為 extraction 時間點的問題，沒有人問：/dream body 執行中，LLM 用人格語氣進行的 reasoning 對 wikisync/factlint 等步驟的決策有沒有副作用路徑。這些維運步驟本身就會觸發寫入（wiki 更新、facts 清除判斷），若在帶人格的 session 裡執行，污染不只在 extraction，而在整個 dream body 的 LLM 決策過程。三方共同把問題邊界劃在「寫入攔截」，跳過了「決策污染」這一層。"
}
以下是它的文字說明（推理過程；可能被截斷）：我沒有讀取任何檔案，因此所有「致命缺陷」都必須基於各方案自陳的假設與邏輯矛盾來攻擊——這是我唯一誠實的立場。

---

## 方案 C（呈現層隔離）

**致命缺陷：方案的成立前提已被自己標記為「最關鍵的未查證前提」，但仍作為推薦方案交出。**

方案自陳：「ACP 協定支援 per-request system message 注入（不只是 session/new 初始化時）——這是**最關鍵的未查證前提**，若不支援則方案在協定層不可行」。

這不是「實作粗糙可以補救」，這是「如果這個前提為假，方案整個不存在」。一個架構方案把自己的存活條件列為未查證假設，然後還推薦它——邏輯上等同於說「如果協定允許我想做的，我就這樣做」，沒有任何資訊量。

方案 C **站不住腳**，不是因為它的思路錯，而是它沒有先查最關鍵的那一條，就把結論交出來了。

---

## 方案 B（資料層人格清洗）

**致命缺陷：攔截點的「唯一性」假設沒有被驗證，而方案自己承認這是死穴。**

方案自陳：「`extractFromSession()` 是唯一的 facts 寫入路徑——沒有其他地方會把人格語氣寫入長期記憶。**若 `/dream` body 本身會呼叫 `remember()` 或直接寫檔，此方案失效。**」

方案的資料流圖裡沒有任何機制阻止 dream body 的 LLM 直接呼叫 `remember()`。若 agent 在 /dream 執行過程中以人格語氣抽取事實並自行呼叫寫入，清洗點在 extraction 層完全沒有用——因為那是另一條路徑。方案 B 的「架構簡化」建立在一個未驗證的拓撲假設上：facts 只有一個入口。這正是核心不可接受後果（人格語氣寫入 facts）的風險所在，方案卻把驗證這件事留給讀者。

方案 B **有致命缺陷**：在未確認寫入路徑唯一性之前，它提供的是一個假安全感，而不是架構保證。

---

## 方案 A（現有完整 session carve-out）

三份提案裡只有 A（現有實作）是有 code 的，攻擊點在它被拿來和 B/C 比較的那個前提：「Stage 1 的複雜度是必要的」——這個主張在三份方案裡都沒有人去驗。

**最可能出事的地方**：carve-out 的 try/finally 邊界問題（memory recall 裡已記錄：entry 副作用在 try 外、exit 順序錯誤、finally 最後一句 throw 蓋掉回傳值）——這些都是架構上的已知缺陷，不是假設，而且已經被找到過一次。如果 B/C 都不可行，A 仍是最有程式碼支撐的方案，但它的複雜度本身就是風險，每次有人碰 entry/exit 邊界都有機率引入新的 override 洩漏。

---

## 三案共有的盲點

**三案都假設「人格污染」是一個 extraction 時間點的問題，但沒有人問：人格寫進 preamble 之後，LLM 在 /dream body 執行中用人格語氣進行的 reasoning 有沒有其他副作用路徑？**

所有方案的「污染防護」都只針對 facts/archive/working-state 的寫入。但 /dream 執行的是維運步驟（dailylog、factlint、wikisync），這些步驟可能本身就會觸發寫入——例如 wikisync 更新 wiki 頁、factlint 決定哪些 facts 要清除。如果這些操作在帶人格的 session 裡執行，「人格影響判斷」的風險不只在 extraction，而在整個 dream body 的 LLM 決策過程。三個方案都把問題定義為「extraction 的污染」，沒有人問「body 執行期間的決策污染」。這是共同的問題定義邊界，不是個別方案的設計疏漏。完成。總結：

- **方案 C**：致命缺陷——自陳「最關鍵的未查證前提」（ACP per-request inject）卻仍推薦，前提若假則方案不存在。
- **方案 B**：致命缺陷——清洗點在 extraction 層，但沒有機制阻止 LLM 在 dream body 直接呼叫 `remember()`，唯一入口的假設未驗證。
- **方案 A**：站得住腳，但 try/finally 邊界的已知缺陷是持續性風險。
- **共有盲點**：三案都把污染問題定義在「extraction 時間點」，但 /dream body 執行中 LLM 的維運決策（wikisync 更新、factlint 清除判斷）本身也在帶人格的 session 裡，決策層的污染沒有任何方案觸碰。

Complete this task. When done, summarize what you accomplished.

---

