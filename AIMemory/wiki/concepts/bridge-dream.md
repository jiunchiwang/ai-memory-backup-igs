---
title: Bridge Dream 例行維運框架
type: concept
created: 2026-07-16
updated: 2026-07-22
sources: [f_e1f99f, f_e2d60b, f_e547d2, f_6e3e02, f_a3ef7e, f_411672, f_a18e55]
---

# Bridge Dream 例行維運框架

## 概述

`/dream` 是 telegram-kiro-bridge 每日 04:00 自動觸發的例行維運框架（`src/commands/dream.ts` + `~/.kiro/dream.json`），依序執行多個維運步驟（sharedsync/dailylog/memorytoskill/claudememcurate/topicreview/wikisync/factlint/wikilint/skilllint/docupdate/specialistreview/artifactcleanup/backup/restart）。本頁記錄框架本身的設計與踩坑；各步驟實際維運的記憶系統內容見 [[bridge-memory]]。

## dream.json 執行機制

- 讀取路徑優先序：`MEMORY_DIR/config/dream.json` → 退回 `~/.kiro/dream.json`（此機器實際生效檔）→ 內建 `DEFAULT_STEPS` fallback
- 每個 step 的 `cmd` 字串必須存在於 `index.ts` 的 `COMMAND_HANDLERS` map 中才能被執行，否則判定「未知指令已跳過」但不中斷其餘步驟（`continue_on_error` 預設 true）

## claude-mem-curate → 第 14 步（2026-07-16）

原本只能手動觸發或 agent 主動提醒，新增 `handleClaudeMemCurate` handler（仿 `handleDocUpdate` 的 meta-prompt 模式）並註冊進 `COMMAND_HANDLERS`，`dream.json` 插入 `claudememcurate` 步驟（`memorytoskill` 之後、`topicreview` 之前），使精選流程從純手動變成每日自動執行。2026-07-19 補修 SKILL_USED 追蹤缺口：該步驟 meta-prompt 原未要求輸出 `<<SKILL_USED:...>>`，導致 `skill-usage.json` 的 `use_count` 恆為零（統計口徑缺口非真低使用），已補上第 8 步指示。

## dream turn 誤報「(no output)」— 兩種不同根因

### 根因 A：turn 中途崩潰（2026-07-17 修復）

架構陷阱：`session.buffer` 只靠串流 `agent_message_chunk` 累積文字，若 turn 在產出最終文字前中途崩潰（如 ACP 行程卡死），`buffer` 維持初始空字串，與「agent 真的沒話說」在 `dream.ts` 眼中完全無法區分，兩者都顯示成誤導性的 `(no output)`。診斷手法是交叉比對 `events.jsonl` 的 `tool_call` 時間戳與 session transcript，找出 turn 中途停止的實證。

修復（commit `de0b7e2`，觀測層）：`sessionManager.ts` 新增 `_lastTurnFailed` 旗標並在 `resetTurn()` 重置、`run-prompt.ts` 錯誤路徑寫入此旗標、`dream.ts` 讀取旗標讓真正失敗的步驟顯示 ❌ 而非 `(no output)`；同時修好 `handleSharedSync` 吞錯誤的既有 bug。

### 根因 B：dailylog 合法跳過被誤判（2026-07-22 修復）

`dream.ts` 的 stepResults 只認 `session.buffer` 差異或結構化回傳值來判斷 summary。`handleDailyLog` 在「今日無 session 記錄」分支原本直接用 `ctx.reply()` 回覆（不寫入 buffer），導致該步驟被誤記成 `(no output)` 並被後續蒸餾誤判為 High Priority 失敗——但這其實是合法跳過（非例行 04:00 執行時，當日 session 檔案可能尚未落地）。修復：該分支改為回傳結構化 `DreamStepResult`（排除同時修改 `session.get` 失敗分支，因為未觸發、屬範圍外）。

## 已知混淆：skill 觸發語境重疊

`memory-to-skill` / `knowhow-accumulation` / `claude-mem-curate` 三個 skill 的觸發語境（回顧過去對話抽取可重用模式）高度重疊，雖輸出產物不同（ms-skill / ❌→✅ knowhow / AIMemory facts）但易造成選用混淆；`knowhow-accumulation` 自建立以來 use_count 仍為 0（使用者已明確裁決保留，非疏漏）。

## 相關

- [[bridge-memory]] — /dream 各維運步驟實際操作的記憶系統內容（factlint/wikisync/wikilint/skilllint）
- [[bridge-project]] — 主專案頁
