---
name: kiro-model-version
description: kiro-cli 2.2.0 可用模型最強是 claude-opus-4.6，不是 claude-opus-4.7（不存在）
type: feedback
originSessionId: 36bec1b7-84c8-4d6f-8b2b-466ec9c10709
---
`kiro-cli chat --model` 必須用 `claude-opus-4.6`，不是 `claude-opus-4.7`（在 kiro-cli 2.2.0 不存在，會 exit code 1）。

**Why:** 2026-05-05 測試時發現 skill 文件寫的是 `claude-opus-4.7`，但 `kiro-cli --version 2.2.0` 可用模型清單裡只有到 `claude-opus-4.6`。用錯模型名稱會直接報錯並出現「Failed with non-blocking status code」。

kiro-cli 2.2.0 可用模型（截至 2026-05-05）：
- auto, claude-opus-4.6, claude-sonnet-4.6, claude-opus-4.5, claude-sonnet-4.5, claude-sonnet-4, claude-haiku-4.5, deepseek-3.2, minimax-m2.5, minimax-m2.1, glm-5, qwen3-coder-next

**How to apply:**
- 一律用 `--model claude-opus-4.6`（最強 Claude 模型）
- kiro-cli 版本升級後再確認一次可用模型清單（`kiro-cli --help` 或直接跑看 error 訊息）
- `DEP0190` warning 是 kiro-cli 內部 Node.js 問題，無法從外部修正，可忽略（不影響功能）
