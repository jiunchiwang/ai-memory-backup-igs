---
title: 開發工具與環境設定
type: concept
created: 2026-06-28
updated: 2026-08-05（補 Edit 工具 replace_all 陷阱）
sources: [f_7c41c5, f_99b243, f_0b76be, f_86246b, f_5871a8, f_947e7a, f_fedf5c, f_a8a12e, f_eb9ddd, f_5bf5da, f_8da350, f_af2a3f, f_cb572a, f_9bb794, f_ab7e0a, f_129738]
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

## 文件產出

- `docs/typescript-guide.html` — TypeScript 教學手冊 HTML 版（深色主題、左側目錄、語法高亮），來源為 Obsidian Vault 的 `typescript-guide_Claude.md`

## 相關

- [[bridge-smoke-gate]] — `tsc --noEmit` / `tsc -p .` 在 bridge 的把關鏈裡各自的角色
- [[bridge-project]] — bridge 專案的開發環境筆記
- [[user-pref]] — Git commit 相關的使用者紀律
