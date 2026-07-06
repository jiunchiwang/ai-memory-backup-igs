---
title: 開發工具與環境設定
type: concept
created: 2026-06-28
updated: 2026-07-06
sources: [f_7c41c5, f_99b243, f_0b76be, f_86246b, f_5871a8, f_947e7a, f_fedf5c, f_a8a12e]
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

## 工作流程

### PDF 產出

HTML+CSS 排版 → Playwright headless Chromium 渲染（`docs/to_pdf.py`）。不用 fpdf2 或 WeasyPrint。

### TypeScript 驗證

```bash
npx tsc --noEmit
```

遇到 TS6.0 deprecation 警告時加 `--ignoreDeprecations 6.0` 抑制。

### Bash 呼叫 PowerShell（引號陷阱）

在 bash shell 呼叫 PowerShell 時，引號（單引號 / `$_`）會被 bash 層吃掉導致 ParserError。可靠做法：把指令轉 UTF-16LE 再 base64，用 `powershell -EncodedCommand <base64>` 執行。heredoc 傳 PowerShell 也有同類格式問題，替代方案是先寫暫存 script 檔再執行。

## 文件產出

- `docs/typescript-guide.html` — TypeScript 教學手冊 HTML 版（深色主題、左側目錄、語法高亮），來源為 Obsidian Vault 的 `typescript-guide_Claude.md`
