---
name: ms-windows-shell-interactive-prompt
description: 當在 Windows PowerShell 或 cmd.exe 中執行讀檔、列目錄、搜尋指令（Get-Content、type、cat、more）導致 tool call 卡住不回、或在 Kiro agent 與 ACP bridge 裡看到 PowerShell 的互動式參數詢問（例如 Path 參數提示）時使用
---

# Windows shell 互動式 prompt 卡死 agent — 讀檔禁用 Get-Content 系列

## 概述

Windows PowerShell 的許多 cmdlet（最常見：`Get-Content`、`Remove-Item`、`Copy-Item`）在缺必填參數（通常是 `-Path`）時，會**開啟互動式 prompt** 在 stdin 上等輸入，例如：

```
Cmdlet Get-Content 在命令管線位置 1
請提供下列參數的值:
Path[0]:
```

Agent 透過 shell tool 跑指令時，**沒有機制回應這個 prompt**，子行程就永遠掛著 → shell tool call 不 return → 整個 session 凍結（Telegram bridge / ACP client 端看到的症狀是「agent 不回覆也不報錯」）。

## 何時使用

- 要讀單一或多個檔案內容
- 要依內容搜尋（grep）或依檔名找檔
- 要列目錄
- ACP / Telegram bridge 的 session 明顯卡住，檢查 agent log 發現最後一筆 tool call 是跑 PowerShell
- 準備下 Windows shell 指令前，檢核該指令是否安全

## 核心原則

**Windows 上，讀檔 / 搜尋 / 列目錄一律走 dedicated tool，不走 shell。**

| 要做的事 | 正確 tool | 禁用的 shell 指令 |
|---|---|---|
| 讀單一檔案 | `readFile` / `readCode` | `Get-Content`, `type`, `cat`, `more` |
| 讀多個檔案 | `readMultipleFiles` | 同上 |
| 列目錄 | `listDirectory` | （`Get-ChildItem` 可以，但仍建議走 tool） |
| 依內容搜尋 | `grepSearch` | `Select-String`, `findstr` + pipe |
| 依檔名搜尋 | `fileSearch` | `Get-ChildItem -Recurse -Filter` |

## 必須跑 PowerShell 時的 checklist

某些任務只能走 shell（例如 `New-Item -ItemType Junction`、`Remove-Item -Recurse -Force`、winget、git）。這時遵守三條：

### 1. 一律加 `-NoProfile -NonInteractive`

```
powershell -NoProfile -NonInteractive -Command '<your command>'
```

- `-NonInteractive`：缺參數時直接丟錯誤（non-zero exit），**不會**開 prompt。
- `-NoProfile`：跳過使用者 profile，確保行為可預測。

### 2. 所有路徑用 named parameter 顯式傳入

不要依賴 positional argument 或環境變數。Bad：

```
Get-Content $file
```

Good：

```
Get-Content -Path 'F:\AI\foo.md'
```

### 3. 下指令前心裡跑一次：缺參數會丟錯還是開 prompt？

若答案是「開 prompt」就改方案 — 換 dedicated tool 或補參數。

## 診斷已卡住的 session

徵兆：Kiro agent / ACP client 側看到 tool call 送出後再也沒回。

檢查步驟：

1. 看 agent stderr / log，找最後一筆 tool invocation。
2. 若是 PowerShell 指令且尾巴停在 `請提供下列參數的值` / `Supply values for the following parameters`，就是這個症狀。
3. Telegram bridge：發 `/cancel`（送 `session/cancel`）先試，無效再 `/reset` 或 `/restart`。
4. 本機 IDE 側：關 terminal、重開 agent。

## 相關 skill

- `ms-windows-shell-exit-code-false-positive` — Windows exit code 處理
- `ms-acp-protocol-limitations` — ACP 協定層問題診斷


## PowerShell Set-Content / Out-File 編碼陷阱（UTF-16 覆蓋 UTF-8 檔案）

### 症狀

用 PowerShell 的 `Set-Content` 或 `$content | Out-File` 寫回含中文的檔案後，檔案變成 UTF-16 LE 編碼（BOM `FF FE`）。後續用 Node.js / Python / Kiro 的 `read` tool 讀取時：
- 出現 `stream did not contain valid UTF-8` 錯誤
- 或內容全部亂碼 / 只剩最後幾行

### 根本原因

PowerShell 5.x 的 `Set-Content` 預設編碼是 **系統 locale**（cp950 / Big5），`Out-File` 預設是 **UTF-16 LE**。即使加 `-Encoding UTF8`，PowerShell 5 會寫 **UTF-8 with BOM**（`EF BB BF`），某些工具仍會出問題。

### 硬規則

**永遠不要用 PowerShell 修改 UTF-8 文字檔內容。** 改用：

| 需求 | 正確做法 |
|------|---------|
| 取代字串 | Kiro `write` tool 的 `strReplace` |
| 批次取代 | `py -c "..."` 用 Python 讀寫（明確指定 `encoding='utf-8'`） |
| Append 一行 | Kiro `write` tool 的 `insert` |
| 整檔重寫 | Kiro `write` tool 的 `create` |

### 如果已經搞壞了

```powershell
# 檢測是否 UTF-16
py -c "print(open('file.md','rb').read()[:4])"
# 如果是 b'\xff\xfe' 就是 UTF-16 LE，修復：
py -c "p='file.md'; open(p,'w',encoding='utf-8',newline='\n').write(open(p,encoding='utf-16-le').read())"
```
