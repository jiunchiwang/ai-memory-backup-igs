---
name: decision-gate-hook-minimal
description: 2026-07-06 閘門 A/B hook 最終決策：已部署 Claude-only 最小版（settings.local.json + impact-gate.mjs），不做跨 CLI 投影
type: project
---

閘門 A/B hook 決策演變：先決定不部署 → 使用者改為部署 **Claude-only 最小版**（2026-07-06 已完成）。

**Why:** correctness 軸 ritual 實證零增益 + repo 已有 tsc/smoke 機械防線，所以不值得跨 CLI 投影工程；但使用者要人軸價值（修改前逼輸出影響範圍供他看），最小版成本低（一支 script + 幾行設定）。

**現況：**
- `G:/AI/telegram-kiro-bridge-main/.claude/hooks/impact-gate.mjs` — Node script，每 session 每檔首次 Edit/Write exit 2 要求輸出 🟠 收到/打算 + 因果鏈分析，重試即放行；只閘專案內檔案，`.claude/` 與專案外（含 auto-memory）放行；狀態在 tmpdir/impact-gate/<session_id>；fail-open
- 註冊在專案 `.claude/settings.local.json` 的 hooks.PreToolUse（machine-local，不 git-track）
- 已測：首次 exit 2 / 重試 0 / skip 路徑 0 / 空 stdin 0

**How to apply:** 在此 repo 被擋時照訊息輸出分析再重試，是預期行為別繞過。勿再建議跨 CLI（Kiro/Codex）投影版——已明確否決。切非 Claude ACP 時閘門消失屬接受的設計。bridge 的 src/tool-hooks.ts 是 Post、fire-and-forget、僅 direct provider 生效，不是閘門機制。
