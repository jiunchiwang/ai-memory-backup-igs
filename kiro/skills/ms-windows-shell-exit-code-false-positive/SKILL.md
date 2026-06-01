---
name: ms-windows-shell-exit-code-false-positive
description: 當在 Windows PowerShell 或 cmd.exe 中跑 git clone、pip install、npm install、winget 等命令時，明明工作完成卻收到 exit code 1、stderr 有進度條或 notice、shell tool 回報失敗時使用
---

# Windows Shell Exit Code 假陽性

## 概述

Windows 的 PowerShell 與 cmd.exe 處理外部程式 stderr 的方式會和 Unix shell 有顯著差異。許多命令列工具（git、pip、winget、apt 等）**把進度條、警告、通知訊息都寫到 stderr**，在 PowerShell 的 `$ErrorActionPreference=Stop` 或 MCP shell tool 的嚴格判斷下會被當成錯誤 → 回報 exit code 1 / RemoteException，儘管命令**實際上成功了**。

核心原則：**在 Windows 上，`exit code ≠ 0` 與 `stderr 有內容` 都不足以判定命令失敗，必須交叉檢視 stdout、檔案系統副作用、或用 `-q` 靜音旗標後再跑一次。**

## 何時使用

- 在 Windows 跑 `git clone`、看到 `Updating files: 100% done` 但 tool 回報 exit code 1
- `pip install` 看到 `Notice: A new release of pip...` 而被當成失敗
- `npm install` 的警告被 MCP shell tool 解讀成錯誤
- cmd.exe 的 `mkdir ... && ...` 鏈結明明執行了，仍回 exit 1
- Agent 發出 shell command 後收到 error，但人工驗證檔案已建立

**不要用在：**

- 真的失敗的命令（編譯錯誤、真的找不到 repo、權限不足等）— 要先確認**不是**這些才套用本 skill
- Linux / macOS 上遇到的 exit code 問題（那邊的 stderr 慣例與此不同）

## 典型症狀

### 情境 A：git clone（7696 檔全數下載完，卻 exit 1）

```
git : Cloning into 'E:\...\extensions'...
At line:1 char:...
+ git clone git@github.com:...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (Cloning into ...:String)
      [RemoteException]
    + FullyQualifiedErrorId : NativeCommandError

Updating files:  19% (1536/7696)
Updating files:  20% (1540/7696)
...
Updating files: 100% (7696/7696), done.
```

PowerShell 看到 git 把 `Cloning into...` 與進度條寫到 stderr，就把整個 invocation 標紅，即使最終 exit 成功。

### 情境 B：pip install（只是 notice）

```
Installing collected packages: pypdf
Successfully installed pypdf-6.10.2
[notice] A new release of pip is available: 24.0 -> 25.3
[notice] To update, run: python -m pip install --upgrade pip
```

pip 把「新版本通知」寫 stderr → exit 0 但 shell tool 可能把 stderr 非空當成 fail 條件。

### 情境 C：cmd.exe mkdir + &&

```cmd
mkdir F:\AI\AIMemory\oldSessions && move F:\AI\AIMemory\sessions\* F:\AI\AIMemory\oldSessions\
```

若資料夾已存在，`mkdir` 寫 `A subdirectory or file ... already exists.` 到 stderr 並 exit 1，`&&` 後面就不跑了——即使使用者真正要的是「確保存在」的 idempotent 行為。

## 判斷真假失敗的 checklist

收到 exit code ≠ 0 時按順序檢查：

1. **stdout 有沒有 success token？** `done`、`Successfully installed`、`Cloning into` + `100%` → 八成是假陽性
2. **stderr 的內容是 progress / notice / warning 嗎？** `Updating files: X%`、`[notice]`、`npm WARN` → 是
3. **副作用達成了嗎？** 用 `Test-Path`、`Get-Item` 驗證檔案/資料夾是否真的建立或更新
4. **去掉進度輸出再跑一次會怎樣？** 加 `-q` / `--quiet` / `--progress=plain` 後 exit 應該是 0

四項都確認是假陽性後，才可以忽略 exit code 繼續下一步。

## 實作：防護寫法

### PowerShell：預期 stderr 寫入的命令加 `2>&1`

把 stderr 合併到 stdout，PowerShell 就不會把它當 error stream：

```powershell
git clone git@github.com:OLD-RD1/slotExtensions-client.git extensions 2>&1
```

副作用：輸出內容混在一起，但進度條不再觸發 RemoteException。

### PowerShell：用 `& { ... } 2>&1 | Out-Host; $LASTEXITCODE`

更精準的做法——明確讀 `$LASTEXITCODE`（外部程式真正的 exit code）而不是依賴 PowerShell 的 `$?`：

```powershell
& git clone <url> <path> 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) {
    # 這才是真的失敗
    throw "git clone failed with exit $LASTEXITCODE"
}
```

### cmd.exe：用 PowerShell 的 `New-Item -Force` 取代 mkdir

```powershell
# ❌ cmd 版本，資料夾存在會 exit 1
# mkdir F:\path && move ... F:\path

# ✅ PowerShell 版本，idempotent
New-Item -ItemType Directory -Path 'F:\path' -Force | Out-Null
Move-Item -Path 'F:\src\*' -Destination 'F:\path\' -Force
```

`-Force` 讓「已存在」不算錯誤。`Out-Null` 避免 New-Item 回傳的物件污染 stdout。

### Node.js / TypeScript：spawn 時分別處理

```ts
const { spawn } = require("child_process");
const child = spawn("git", ["clone", url, dest], { stdio: ["inherit", "pipe", "pipe"] });

let stdout = "", stderr = "";
child.stdout.on("data", (d) => (stdout += d));
child.stderr.on("data", (d) => (stderr += d));

child.on("close", (code) => {
    // 判斷條件：exit code + stdout/stderr 內容
    const succeeded = code === 0 || /100%|done|Successfully/.test(stdout + stderr);
    if (!succeeded) reject(new Error(stderr));
    else resolve(stdout);
});
```

## 為什麼會這樣

- **git** 預設把進度條寫 stderr，讓 stdout 可以純粹輸出 patch / diff（Unix pipe 友善）。加 `--quiet` 靜音或 `--progress=plain` 改變行為。
- **pip** 的 `[notice]` / 警告訊息寫 stderr，升級提示尤其常見。
- **PowerShell 5.1** 遇到外部程式寫 stderr 且觸發 `$ErrorActionPreference=Stop` 時會拋 `RemoteException`。PowerShell 7 有改善但仍不完全。
- **MCP shell tool** 的預設失敗判斷常用 `exit !== 0 || stderr.length > 0`，對 Windows 慣例不夠寬容。

## Common Mistakes

| 錯誤 | 修正 |
|---|---|
| 看到 exit code 1 就回報失敗、中止流程 | 先查 stdout 是否有 success token、檔案系統副作用是否達成 |
| 想用 cmd.exe 的 `mkdir && move` 做 idempotent 建資料夾 | 用 PowerShell `New-Item -Force`，或 `if not exist ... mkdir ...` |
| 在 git / pip 命令 2>&1 前加 `$ErrorActionPreference='Stop'` | 對外部程式用 `$LASTEXITCODE` 判斷，不要用 `$?` |
| 把 stderr 當成「錯誤訊息」顯示給使用者 | 包 stdout 一起看；或用 `--quiet` / `-q` 降噪 |
| 在 loop 裡對每次假陽性都重試 | 先判斷是不是假陽性，如果是就接受 exit code 不為 0 |
| Agent 跑 `npm install` 收到 warning 就以為要再跑一次 | 用 `npm install --silent` 或把 exit code 當唯一依據 |
| PowerShell `git commit -m "..." -m "..."` 多行 message 整個吞空（exit 1、stdout/stderr 都空） | 改用 `git commit -F <tmpfile>`，把訊息寫進暫存檔 |
| `gh push` / `gh repo create ... --push` 的進度 `To https://...` 寫到 stderr，被判為 NativeCommandError、exit 1 | 當作**成功**：stderr 只有 `To <url>` 和 `<sha>..<sha> branch -> branch` 是正常的 push 進度 |

### 踩雷範例：多行 git commit message 被吞

PowerShell 的 native command arg passing 對多個 `-m` 有 quirky 行為——`git commit -m "subject" -m "body line 1" -m "body line 2"` 在 cmd.exe 通常沒問題，在 PowerShell 可能整段被吞、`git` 退出碼 1 但 stdout/stderr 什麼都不印。你看到的是：

```
> git commit -m "feat: xxx" -m "body description"
>
(exit code 1)
```

沒有 error message、working tree 也沒變成 committed。很難 debug 因為**沒任何線索**。

**正解**：把 commit message 存到檔案、用 `-F`：

```powershell
$msg = @"
feat: xxx

body description with multiple
lines and special characters.
"@
$msg | Out-File -Encoding utf8 .tmp-commit-msg.txt
git commit -F .tmp-commit-msg.txt
Remove-Item .tmp-commit-msg.txt
```

或更簡單地用 heredoc + stdin：

```powershell
git commit -F - <<EOF
feat: xxx

body
EOF
```

**單行 `-m`**（沒 body）在 PowerShell 通常 OK，但含引號、`` ` ``、`$`、中文時也可能踩；**養成習慣一律走 `-F`** 最穩。

### 踩雷範例：gh push 的 stderr 進度被誤判

`gh repo create --push` 或 `git push origin main` 成功時的輸出：

```
stdout: (空)
stderr:
  To https://github.com/user/repo.git
   * [new branch]  main -> main
  branch 'main' set up to track 'origin/main'.
exit code: 1   ← ← ← ← ←
```

exit code 1 但**其實成功了**——push 確實上去了，遠端可以看到 commit、`git status` 顯示 `Your branch is up to date with 'origin/main'`。這是 PowerShell 把 stderr 非空就當失敗的老毛病。

**判斷真假**：

```powershell
git push origin main
if ($LASTEXITCODE -ne 0) {
  # 檢查遠端是否真的有拿到
  git fetch origin
  $local  = git rev-parse HEAD
  $remote = git rev-parse origin/main
  if ($local -eq $remote) {
    Write-Host "push succeeded despite exit 1 (false positive)"
  } else {
    throw "push really failed"
  }
}
```

或直接跑 `git status` 看是否是 `up to date`——是就當成功，不管 exit code。

### 踩雷範例：PowerShell 5.x 不支援 `&&` chain

`git add -A && git commit -F msg.txt` 在 bash / PowerShell 7 都 OK，但在 **Windows PowerShell 5.x（預裝版本）** 會：

```
> git add -A && git commit -F msg.txt
在這個版本中，'&&' 語彙基元不是有效的陳述式分隔符號。
(exit 1, stderr 為空)
```

`&&` 是 PowerShell 7+ 才加的 pipeline chain。PowerShell 5 解析 `&&` 當成 syntax error，**但 stderr 留空**（parse error 不寫 stderr），你會看到 exit 1 + 看起來成功的 stdout、working tree 仍無變化。

**修法**：

1. **分兩次 shell call**（最簡單）：
   ```
   git add -A
   git commit -F msg.txt
   ```

2. **寫成 `.cmd` batch**（單行也要跨步驟時）：
   ```cmd
   @echo off
   git add -A
   if errorlevel 1 exit /b 1
   git commit -F msg.txt
   ```

3. **強制用 PowerShell 7**（如有安裝 `pwsh.exe`）：
   ```
   pwsh -Command "git add -A; if (-not $?) { exit 1 }; git commit -F msg.txt"
   ```
   注意 `;` 沒有 short-circuit 語意，要自己 `$?` 判斷。

4. **`.cmd /c` 直接用 cmd.exe**（cmd.exe 支援 `&&`）：
   ```
   cmd /c "git add -A && git commit -F msg.txt"
   ```

**判別訊號**：PowerShell 裡 `&&` 出現 exit 1 + stderr 空 + stdout 看起來都成功 + 最後一個動作沒真的做（`git status` 顯示未 commit）→ 99% 是這個坑。

### 踩雷範例：`Select-Object -Last N` 把 exit code 搞混

想把 smoke 輸出用 pipeline 截尾部幾行：

```powershell
node scripts/check-foo.mjs | Select-Object -Last 3
```

`Select-Object` 是 PowerShell cmdlet，`$LASTEXITCODE` 被 pipeline 的最後一個 object 重寫成 cmdlet 自己的（`$null` 變 0 或其他）。即使 smoke 本身 exit 1 fail，pipeline 後**看起來 exit 0 通過**。

**反例**：

```powershell
# 這樣拿 exit code 會不準
node scripts/check-foo.mjs | Select-Object -Last 3
if ($LASTEXITCODE -eq 0) { echo "passed" }  # ← 謊話
```

反之，smoke 真的 exit 0，pipeline 可能回 exit 1（某些 PowerShell 版本對 cmdlet exit 處理怪異）。

**修法**：

1. **不用 pipeline**，用臨時檔：
   ```powershell
   node scripts/check-foo.mjs > out.txt 2>&1
   $code = $LASTEXITCODE
   Get-Content out.txt -Tail 3
   Remove-Item out.txt
   if ($code -eq 0) { echo "passed" } else { echo "failed: $code" }
   ```

2. **用 `.cmd` batch + `ERRORLEVEL`**：cmd.exe 的 `if errorlevel` 是真的 exit code：
   ```cmd
   @echo off
   setlocal enabledelayedexpansion
   node scripts/check-foo.mjs > out.txt 2>&1
   set code=!ERRORLEVEL!
   type out.txt
   del out.txt
   if !code! equ 0 (echo passed) else (echo failed: !code!)
   ```
   注意 `setlocal enabledelayedexpansion` + `!VAR!` 語法，for loop 內才正確展開變數。

3. **直接 `node -e "..."` inline**：避開 pipeline，自己組 stdin/stdout。

**判別訊號**：smoke 在 shell 直接跑明明 exit 0 / 1 很清楚，用了 `| Select-Object -Last N` 或 `| Out-String` 之後 `$LASTEXITCODE` 值變不合理 → 是 cmdlet pipeline 把 native command exit code 吃掉/改寫。

### 踩雷範例：Smoke 跑 `dist/` 不是 `src/`

改了 `src/observerTransformer.ts` 的 token 抽取邏輯，跑 `node scripts/check-observer-transformer.mjs` 發現**行為沒變**，以為修法無效。

**根因**：smoke 的 `import "../dist/observerTransformer.js"` 吃的是 **compiled `.js`**，不是 `.ts`。改 src 之後沒 `npx tsc` 重 build，`dist/` 還是舊版。

**標準流程**：

```
改 src/*.ts → npx tsc -p . → 跑 smoke 驗證
```

不做第二步結果一定騙你。可以包成 npm script：

```json
{
  "scripts": {
    "check": "tsc -p . && node scripts/check-foo.mjs"
  }
}
```

或自建 Windows batch：

```cmd
@echo off
call npx tsc -p .
if errorlevel 1 exit /b 1
node scripts/check-foo.mjs
```

## 相關

- **ms-windows-path-prefix-check** — Windows 平台另一個常見陷阱，路徑白名單比對
- **ms-windows-shell-interactive-prompt** — PowerShell 互動式提示卡死，也是跨 agent / bridge tool 的老坑
- **ms-windows-node-atomic-write** — Windows 磁碟操作的另一個特殊行為（EPERM on rename）
