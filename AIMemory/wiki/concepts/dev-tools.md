---
title: 開發工具與環境設定
type: concept
created: 2026-06-28
updated: 2026-08-15（新增：.env 編輯驗證做法、Git Bash timeout /t 陷阱、skillUsage 權威來源、HTML 目錄錨點偏好）
sources: [f_7c41c5, f_99b243, f_86246b, f_5871a8, f_947e7a, f_fedf5c, f_a8a12e, f_eb9ddd, f_5bf5da, f_8da350, f_af2a3f, f_cb572a, f_9bb794, f_ab7e0a, f_129738, f_b09bb8, f_ddc6a2, f_00d0b6, f_4f4b55, f_8a4a0e, f_10d8ff, f_cbcb3c, f_b120d4, f_a1b97e, f_e189b1, f_1a68bf]
---

# 開發工具與環境設定

## 概述

此台機器（jiunchiwang）的開發工具安裝狀態、路徑配置、以及常用工作流程。

## 機器環境

- **Kiro agent config**：`C:\Users\jiunchiwang\.kiro`（非舊機器的 `C:\Users\tonykuo\.kiro`）
- **Obsidian Vault**：`C:\Users\jiunchiwang\OneDrive - International Games System\文件\Obsidian Vault\`
- smoke test 中硬寫的 tonykuo 路徑需注意替換

### Kiro CLI Model ID 格式

Kiro CLI 使用**短名格式**（如 `claude-sonnet-4.6`、`claude-opus-4.6`），不是完整 API model ID（如 `claude-sonnet-4-5-20250514`）。可用清單：`auto` / `claude-opus-4.6` / `claude-sonnet-4.6` / `claude-opus-4.5` / `claude-sonnet-4.5` / `claude-sonnet-4` / `claude-haiku-4.5` / `deepseek-3.2`。

## 相關專案

- **excel-to-ai-document**（`G:\AI\excel-to-ai-document`）— 含 `skill/excel-to-ai-doc` 資料夾（`SKILL.md` + `scripts/convert.py`），用於將 Excel 規格書轉為 AI 可讀的 Markdown + 圖片結構。是通用工具而非 slot 專屬（曾被 `uk-slot` topic 的過寬關鍵字誤收，2026-08-09 topic review 已修正）。

## 已安裝工具

| 工具 | 用途 |
|------|------|
| Python + youtube-transcript-api | 抓 YouTube 字幕 |
| Playwright + Chromium | HTML → PDF 渲染、網頁自動化 |
| TypeScript（npx tsc） | 型別檢查 |
| Bun runtime（`~/.bun/bin`） | claude-mem plugin hooks 依賴，**不可刪除** |

## 工作流程

### PDF 產出

HTML+CSS 排版 → Playwright headless Chromium 渲染（`docs/to_pdf.py`）。不用 fpdf2 或 WeasyPrint。

### TypeScript 驗證

```bash
npx tsc --noEmit
```

遇到 TS6.0 deprecation 警告時加 `--ignoreDeprecations 6.0` 抑制。

### Smoke Test 依賴 dist/ 編譯產物

`npm run smoke` 跑的是 `dist/` 下的編譯產物，但 `tsc --noEmit` 不會寫檔——改完 `src/` 後要跑 smoke 前必須先用 `tsc -p .` 重新編譯，否則會用過期 `dist/` 跑出假失敗。

### node --env-file 不覆蓋既有變數

`node --env-file` 不會覆蓋已存在的環境變數——子 shell 繼承舊 env 值時，測試 `.env` 改動要用顯式變數覆蓋模擬重啟後行為。

### Git merge 解衝突（--theirs 整檔取代陷阱）

`git checkout --theirs/--ours` 是**整檔取代**，會洗掉對側已乾淨自動合併的 hunk（combined diff 不顯示乾淨 hunk）。雙邊都有改動的檔案應用 `git merge-file` 三方合併，或 `checkout -m` 恢復衝突標記後只改衝突區，並逐檔 diff 兩側核對無遺失。

### Bash 呼叫 PowerShell（引號陷阱）

在 bash shell 呼叫 PowerShell 時，引號（單引號 / `$_`）會被 bash 層吃掉導致 ParserError。可靠做法：把指令轉 UTF-16LE 再 base64，用 `powershell -EncodedCommand <base64>` 執行。heredoc 傳 PowerShell 也有同類格式問題，替代方案是先寫暫存 script 檔再執行。

### gh CLI 未登入

此台機器的 `gh` CLI 尚未執行 `gh auth login`／未設 `GH_TOKEN`，研究 GitHub repo 時 `gh repo view` 等指令會直接失敗，需改用 WebFetch 抓取頁面。

### 多行 git commit message（heredoc vs here-string）

在 **Bash tool** 裡寫多行 commit message 必須用 **bash heredoc**，不可用 PowerShell 的 here-string `@'...'@`——後者會讓首行多一個 `@` **吃掉整個 subject**、末行也留一個 `@`，而且 `git commit` 照樣成功、不報任何錯（2026-07-31 實證，得 `--amend` 修正）。

```bash
git commit -m "$(cat <<'EOF'
subject line
body...
EOF
)"
```

反過來也成立：PowerShell tool 裡才用 `@'...'@`，且結尾 `'@` 必須頂格在第 0 欄。兩個 shell 各有自己的語法，別跨用。

### Edit 工具 replace_all 誤改陷阱

在 Edit 工具做整行刪除或改解構名時，若目標字串在同檔重複出現（如 `relay.ts` 的 `const { runPrompt, sessions } = deps()` 全檔 9 個相同字串），必須用**上下文定位**而非 `replace_all`，否則會誤改其他處——`tsc` 只標出未使用的那一處，行號才是唯一可靠依據（2026-08-02 實證）。

### Windows shell 管線接會 spawn 子進程的命令會假裝掛住

把「會 spawn 子進程的命令」（如 ACP adapter handshake）接管線（`| tail`、`| grep`）會假裝成掛住：管線要等 EOF，而子進程握著 stdout 不放，即使父進程已經印完結果並退出也看不到任何輸出。2026-08-06 因此兩次誤判 codex-acp 探針「300 秒沒回應」，實際上兩次都成功回了 `PONG`，殺掉孤兒進程後輸出才一次吐出來。對這類命令要用 `> file 2>&1` 落檔再讀，不要接管線；同理 `child.kill()` 只殺 shell wrapper，孫進程要另外清（用 CommandLine 比對 + 查 ParentProcessId 存活再殺）。

### openpyxl 讀 xlsx 的兩個靜默陷阱

- **公式格沒有快取值會讀成 None**：`load_workbook(data_only=True)` 讀到的是 Excel **上次存檔時算好的快取值**，不是公式本身。由 openpyxl 之類產生器寫出、或存檔前未重算的檔案沒有快取，那些公式格一律讀成 `None`。2026-08-06 實測一張三格全公式的 sheet 整張被判成空白，而自我驗證因為刻意跳過 empty sheet 的檢查照樣印「整體：通過」。解法是另載一次 `data_only=False` 比對，把只有公式沒有快取的格回填公式字串並讓驗證失敗（回填的是 `=SUM(...)` 不是數值，仍須請對方在 Excel 重新存檔以寫入快取）。
- **讀儲存格顏色只判斷 `.rgb` 是字串會漏掉 theme 色**：`fill.fgColor.rgb` 只在 `color.type == 'rgb'` 時是字串；Excel 調色盤上排的「佈景主題色彩」`type` 是 `'theme'`、舊調色盤是 `'indexed'`，只判斷 rgb 是不是字串會靜默漏掉一整類上色（比不做更危險，因為輸出看起來已支援顏色）。theme 要讀 `xl/theme/theme1.xml` 的 `clrScheme`，且 Excel 的 theme 索引順序與 XML 排列**不同**——XML 是 `dk1,lt1,dk2,lt2,accent1..6,hlink,folHlink`，Excel 索引前兩對互換（`0→lt1, 1→dk1, 2→lt2, 3→dk2, 4..9→accent1..6, 10→hlink, 11→folHlink`）——再套 tint（ECMA-376：在 HLS 亮度上，`tint<0 → L*(1+tint)`、`tint>0 → L*(1-tint)+tint`，HLSMAX 正規化為 1.0）；indexed 走 `openpyxl.styles.colors.COLOR_INDEX`。

### 編輯含機密的檔案（如 .env）

只讀取需要的行範圍（避免把 token 拉進 context）、用 regex 定位而非手抄空白，並以「匹配數必須恰為 1」與「`KEY=value` 行數前後不變」兩道保險驗證未動到設定值。

### Git Bash 用 Start-Process 排延遲工作不可用 `timeout /t N`

Git Bash 的 `PATH` 讓 cmd 解析到 GNU coreutils 的 `timeout` 而非 Windows 的 `timeout.exe`，GNU 版看不懂 `/t` 會直接非零退出，接在後面的 `&&` 整串短路、後續指令完全不執行且無明顯錯誤（2026-08-12 因此宣告「重啟已排定」但實際什麼都沒發生）。正確做法是用 PowerShell 的 `Start-Sleep` 或呼叫完整路徑 `C:\Windows\System32\timeout.exe`。

### 查「某支 skill 被用了幾次」的權威來源

`~/.claude.json` 的 `skillUsage` 物件（每支 skill 一筆 `usageCount` + `lastUsedAt`，全時間累計、不隨 transcript 輪替）——**不是**拿 transcript grep（transcript 約 30 天輪替，數出來的只是視窗內的數字）。配套判準：當計數來源的比對條件寬到會把無關事件也記進去（如某 log 把「commit message 提到某工具名」也算一筆），分母被污染而分子沒有，此時只能報絕對數，不可寫成比例或百分比，並明講分母為何不可用。

## 文件產出

- `docs/typescript-guide.html` — TypeScript 教學手冊 HTML 版（深色主題、左側目錄、語法高亮），來源為 Obsidian Vault 的 `typescript-guide_Claude.md`

## 使用者偏好

- HTML 文件要有目錄錨點跳轉功能（點擊跳段落 + 回目錄連結）
- 技術流程交接同時提供 Markdown 與具目錄錨點、可列印的 HTML 版本

## 相關

- [[bridge-smoke-gate]] — `tsc --noEmit` / `tsc -p .` 在 bridge 的把關鏈裡各自的角色
- [[bridge-project]] — bridge 專案的開發環境筆記
- [[user-pref]] — Git commit 相關的使用者紀律
