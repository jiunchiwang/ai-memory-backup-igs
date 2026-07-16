---
title: Bridge Session 生命週期與多 Session 管理
type: concept
created: 2026-07-08
updated: 2026-07-17
sources: [f_456de2, f_645ea3, f_046ffa, f_bafa71, f_86bdbb, f_bef432, f_20ed42, f_daf156, f_ecaf0b, f_76faa7, f_42aed5, f_c73099]
---

# Bridge Session 生命週期與多 Session 管理

[[bridge-project]] 的 session 連續性走**兩層互補架構**：蒸餾記憶層（archive 摘要 + working state + facts）與 ACP 原生恢復層（session/load resume）。前者丟掉原始 context 靠蒸餾重建，後者保留完整 ACP context 原地接續。

## 蒸餾記憶層（2026-06-30 起）

- **Session 歸檔**：session 關閉時 `exportSession()` 寫結構化 JSON（turns/goal/stats/recentSummary）到 `session-archive-{chatId}.json`；新 session 以 `buildRestorationBlock()` 注入 preamble 後自動刪除。與 working-state 互補——WS 說做什麼，archive 說上下文在哪
- **設計決策**：per-chatId 單檔覆寫（排除 append-only 因為歷史已有 transcript MD）；恢復只注入 ~300 字摘要（排除全量 turn 注入因為 context 爆炸）；turn text 截斷 2000 字
- **`/reset clean`**（或 `/reset fresh`）：額外刪 archive + working-state，下次不帶上次上下文；預設 `/reset` 照舊歸檔

## ACP Session Resume（方案 A，2026-07-07）

- `ACP_SESSION_RESUME=true` 閘控（預設 off）；idle/crash/SIGINT 保留 registry 可 `session/load` 恢復（不重注 preamble）；`/reset`、`/agent`、`/restart`、`<<RESTART>>` 走 fresh 並清 registry（`shutdown` 帶 `clearResume` 參數區分）
- **選型理由**：只做 resume 不做 UI——restart 連續性 + idle 殺 process 省記憶體最實、避免與 goal/MoA/relay 單 session 假設互動（方案 B SessionStore+UI 等 A 跑穩再議 → 實際同日完成，見下）
- 生產機已於 2026-07-07 啟用並通過手動 e2e（context 暗號驗證）
- 實作計畫與三段 review 軌跡：bridge repo `docs/superpowers/plans/2026-07-07-acp-session-resume.md`（BC-1~5 + adapter 實測表）
- 已知 cosmetic：resume 後 `/context` 顯示 preamble 0 chars

## SessionStore + /session 多 Session 管理（同日結案）

- 手動 e2e 全過：BC-3 雙 session 暗號互切不互漏、BC-5 `/reset` 只清 active、BC-2 v1→v2 registry migration、BC-8 claude↔kiro 跨 backend record 互切 model pin 自動連動
- 5 個 commit（8c65748→22cd8d5）已 push；README 已同步（commit 5233767：/agent、ACP_SESSION_RESUME、/session、/reset 新語意）

## Transcript 儲存路徑（四條，皆正常）

`/reset`、onBeforeClose（idle sweep/restart/shutdown）、crash（onUnexpectedExit）、`/session` park。idle sweep 為**靜默存檔**（只寫 console log，使用者決定不加 Telegram 通知）；`Saved → sessions/xxx` 訊息只在 `/reset` 當下仍有 live session 且有歷史時顯示。

## 使用場景偏好

日常用 `/reset`（快速清 context 重開）；`/handoff` 保留給較大任務完成、換機器、當天收工等需要記憶留存的場景。

## 風險備忘

- **Replay 時序**：真 adapter 若在 session/load 回應後補送 replay update，歷史 `<<ASK>>` 等 token 有重放風險——保守 fallback 在計畫檔風險 #1

## 相關

- [[bridge-project]] — Bridge 本體架構
- [[bridge-acp]] — adapter 能力差異（loadSession capability：kiro ✅ / claude ✅ / codex 未判定）
