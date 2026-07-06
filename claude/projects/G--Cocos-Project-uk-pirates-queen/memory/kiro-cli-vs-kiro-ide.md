---
name: kiro-cli-vs-kiro-ide
description: kiro 指令是 Amazon Kiro IDE，kiro-cli 才是 headless CLI，兩者不同
type: feedback
originSessionId: 72ed0a26-c971-4db7-bec7-da714fc4b797
---
`kiro` 和 `kiro-cli` 是兩個完全不同的工具，不要搞混：

- `kiro`（PATH: `C:\Users\jiunchiwang\AppData\Local\Programs\Kiro\bin`）→ Amazon Kiro IDE（VS Code fork），`kiro chat` 是開 GUI 介面，沒有 `--no-interactive`、`--trust-all-tools`、`--model` 等 flag
- `kiro-cli`（PATH: `C:\Users\jiunchiwang\AppData\Local\Kiro-Cli`）→ headless CLI，v2.0.1，支援 `--no-interactive --trust-all-tools --model claude-opus-4.7`，這才是 `/vc-kiro-delegate` skill 要用的工具

**Why:** 2026-04-24 測試 vc-kiro-delegate 時誤用 `kiro chat` 以為找不到工具，實際上 `kiro-cli` 一直都在 PATH 裡且可正常使用。

**How to apply:**
- 執行 vc-kiro-delegate skill 時，指令一律用 `kiro-cli chat ...`，不要用 `kiro chat ...`
- 兩個工具都在 PATH，`which kiro-cli` 可確認路徑
