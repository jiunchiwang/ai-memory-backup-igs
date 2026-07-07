---
name: acp-session-resume-state
description: ACP session resume（方案A）已上線並通過手動 e2e（2026-07-07，SIGINT 路徑），生產機 flag 已啟用
type: project
---

ACP session resume（方案 A）於 2026-07-07 完成並 push origin/main（feat `b6e028f` + docs `72277b9`）。

**Why:** idle/crash 後原本只能靠摘要注入降級恢復；借鏡公司 ai_multi_agent 框架的 session 管理差距分析後，選了「只做 resume 不做 UI」的最小方案。

**How to apply:**
- 功能由 `ACP_SESSION_RESUME=true` 閘控，預設 off（BC-1 零行為變化）。**2026-07-07 已在生產機 `.env:39` 啟用並通過手動 e2e**。
- 語意：idle/crash/SIGINT 訊號關閉 → 保留 registry 可 resume；`/reset`、`/agent`、`/restart`、`<<RESTART>>` → 清 registry 走 fresh（shutdown 帶 `clearResume` 參數區分，這是三段 review 抓到的兩個 bug 修出來的邊界）。
- Adapter 實測：kiro-cli acp ✅、claude-agent-acp ✅（冷啟動可能 >60s）、codex-acp 未判定（需 auth）。
- **手動 e2e 已通過（2026-07-07，claude-agent-acp，SIGINT/kill console 路徑）**：resume log 出現、context 暗號保留、無舊訊息/ASK token 重放（replay 時序風險未觀察到）。idle 自然路徑未實測（`SESSION_IDLE_MINUTES=9000` 等不到），但與 SIGINT 走同一 registry 保留邏輯。
- Cosmetic 已補（`55b3628`）：resume 後 `/context` `/usage` 的 preamble 0 tok 加註「凍在原 agent context 內」——刻意不假造舊數字。**專案全部收尾，無待辦。**
- 計畫與 review 軌跡：`docs/superpowers/plans/2026-07-07-acp-session-resume.md`。
