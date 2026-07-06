---
name: bridge-steering-integration
description: "How ~/.kiro/steering reaches the ACP agent through the bridge — Kiro auto-loads it, bridge code does not; cross-provider gap and where to fix it"
metadata: 
  node_type: memory
  type: project
  originSessionId: c36322a2-44e4-41f6-91e6-da525f9fcdac
---

telegram-kiro-bridge 的程式碼**不注入 steering**(只有 `src/backup.ts` 為了備份而碰 `~/.kiro/steering`;preamble builder `buildPreambleWithBreakdown` 完全不讀 steering)。但 steering **端到端是有效的** —— 因為配對的 `kiro-cli acp`(`.env` 的 `ACP_AGENT_COMMAND=kiro-cli acp ...`)**自己在開機時載入 `~/.kiro/steering/*.md`**,即使是 bridge spawn 的 headless ACP 模式也照載。

**證據(2026-06-22 調查):** Telegram bot 會輸出 `🟠 收到 / 🟠 打算`,這來自 `steering/task-acknowledgement.md`(一條 always-on 規則)。bridge 不注入它,所以一定是 Kiro 自己載的。

**所以第一輪「steering 是 dead code / 完全沒整合」的判斷是錯的** —— 那只是「bridge 程式碼層」的觀察,不反映端到端現實。下結論前要選對觀測層。

**Cross-provider 矩陣(唯一真實殘留 gap,只在 `/switch` 後出現):**
- Kiro(現行):✅ 全部 3 份 steering（Kiro ACP 自載）
- Codex:❌ 完全沒有（sync.ps1 沒 copy 到 `~/.codex/steering`，Codex 無 steering 自動載入）
- Claude Agent:◐ 只有 `skill-workflow`（`~/.claude/CLAUDE.md` 只 `@import` 這份；另兩份雖 copy 到 `~/.claude/steering/` 但沒被 import）

**要修時改 sync.ps1（投影層），不要改 bridge code** —— 問題本質是「投影沒鋪到該 provider 的載入點」。Codex:在 `steerDsts` 加 `~/.codex/steering` + 設定載入點;Claude:把 task-ack、closed-loop 也加進 CLAUDE.md `@import` 守衛清單。

**驗證技巧:** 想知道某個 ACP agent 是否載 steering，看它有沒有遵守 `task-acknowledgement.md` 的 always-on 🟠 行為即可（免費 probe）。

**決議:** 目前跑 Kiro，steering 全正常，**不需要做 bridge preamble 注入（方案 A/hybrid）** —— 那會解一個現在沒有的問題、還會 double-inject task-ack。等真的切 Codex/Claude 再於 sync.ps1 層處理（YAGNI）。

相關:steering 三份檔的型別分類見 [[steering-corpus-types]]。
