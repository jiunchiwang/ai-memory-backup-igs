---
title: Bridge Dream 例行維運框架
type: concept
created: 2026-07-16
updated: 2026-08-16（wikilint：補齊 provenance——「claude-mem-shortlist 問題釐清」節內容早已涵蓋 f_6fd455/f_5ca96d/f_157e9c/f_3a6356 但 sources 漏列；新增 desc 基線 232 字元的閘門限制小節）
sources: [f_e547d2, f_6e3e02, f_a3ef7e, f_411672, f_a18e55, f_071df3, f_1ae434, f_6fd455, f_5ca96d, f_157e9c, f_3a6356, f_f53d82]
---

# Bridge Dream 例行維運框架

## 概述

`/dream` 是 telegram-kiro-bridge 每日 04:00 自動觸發的例行維運框架（`src/commands/dream.ts` + `${MEMORY_DIR}/config/dream.json`），依序執行多個維運步驟。本頁記錄框架本身的設計與踩坑；各步驟實際維運的記憶系統內容見 [[bridge-memory]]。

## dream.json 執行機制

讀取路徑優先序：
1. `MEMORY_DIR/config/dream.json`（此機器：`G:\AI\AIMemory\config\dream.json`，已於 2026-08-02 建立）
2. 退回 `~/.kiro/dream.json`
3. 內建 `DEFAULT_STEPS` fallback

每個 step 的 `cmd` 字串必須存在於 `index.ts` 的 `COMMAND_HANDLERS` map 中才能被執行，否則判定「未知指令已跳過」但不中斷其餘步驟（`continue_on_error` 預設 true）。

## dream.json models 表：per-backend 設計（2026-08-02 新增）

### 使用者需求澄清

要的是 **per-backend** 而非 per-step，也不是換 provider：
- kiro 跑 `claude-opus-4.5`
- claude 跑 `claude-sonnet-5`
- codex 保留條目（未買訂閱）
- 任一 backend 若查不到設定就沿用既有 pin

使用者明確否認過「想用 Gemini/DeepSeek/local」（那是 agent 先前自行推測後誤存的）。

### 設計決策：per-backend + 顯式還原

選擇「per-backend + 顯式還原」而非 per-step model，因為：
- 三個 ACP adapter 的 model 生效路徑不同：
  - **claude**：走 `session/set_config_option`，可在 session 存活期改
  - **kiro**（`--model`）與 **codex**（`-c model=`）：綁在 CLI 啟動參數，改 model 等於 respawn subprocess
- per-step 會變成 15 步 dream 換 15 次 agent 並打斷 `session.buffer` 判定

還原不靠「最後一步是 restart」，因為使用者自編 dream.json 拿掉 restart 時會靜默停在便宜 model。

### 實際設定檔（2026-08-02）

位於 `G:\AI\AIMemory\config\dream.json`，內容只有 models 表：

```json
{
  "models": {
    "claude": "claude-sonnet-5",
    "kiro": "claude-opus-4.5"
  }
}
```

刻意不列 steps——`dream-config` 已支援「steps 缺席不等於寫錯」，缺席時靜默沿用 `DEFAULT_STEPS`，避免把 15 步抄一份成第二事實來源。

## claude-mem-curate → 第 14 步（2026-07-16）

新增 `handleClaudeMemCurate` handler（仿 `handleDocUpdate` 的 meta-prompt 模式）並註冊進 `COMMAND_HANDLERS`，`dream.json` 插入 `claudememcurate` 步驟（`memorytoskill` 之後、`topicreview` 之前），使精選流程從純手動變成每日自動執行。

2026-07-19 補修 SKILL_USED 追蹤缺口：該步驟 meta-prompt 原未要求輸出 `<<SKILL_USED:...>>`，導致 `skill-usage.json` 的 `use_count` 恆為零，已補上第 8 步指示。

**skill 跨 CLI 可攜性盤點（2026-08-05）**：使用者的 skill 集裡只有 `claude-mem-curate` 綁 Claude 專屬工具鏈（引用 `claude-mem` plugin），Codex 端讀得到但執行不了；其餘 36 支內容層皆可攜（絕對路徑僅 `ms-portable-skill-authoring` 的教學反例一處）。Codex 端原生 skill 支援細節見 [[bridge-memory]]。

## dream turn 誤報「(no output)」— 兩種不同根因

### 根因 A：turn 中途崩潰（2026-07-17 修復）

`session.buffer` 只靠串流 `agent_message_chunk` 累積文字，若 turn 在產出最終文字前中途崩潰（如 ACP 行程卡死），`buffer` 維持初始空字串，與「agent 真的沒話說」完全無法區分。

修復（commit `de0b7e2`）：新增 `_lastTurnFailed` 旗標讓真正失敗的步驟顯示 ❌ 而非 `(no output)`。

### 根因 B：dailylog 合法跳過被誤判（2026-07-22 修復）

`handleDailyLog` 在「今日無 session 記錄」分支原本直接用 `ctx.reply()` 回覆（不寫入 buffer），導致被誤記成 `(no output)` 並被後續蒸餾誤判為 High Priority 失敗。

修復：該分支改為回傳結構化 `DreamStepResult`。

## claude-mem-shortlist 問題釐清（2026-08-01 最終定案）

**問題原描述**：同一批候選連續 3 輪 `claude-mem-curate` 執行都未被上游清空。

**2026-08-01 查清**：從 07-22 起 6 次記載「shortlist 未清空、同一批重掃」全是 curate agent 的**同源 confabulation**，不是系統故障：
- 產生端 `ingest-claude-mem.mjs` L76-77 本來就覆寫檔案並推進 watermark、watermark 鏈完整
- 唯一跑過的 consumer 是排程 `claudemem-daily-curate`，配對正確
- bridge 的 `/claudememcurate` 從未被執行過（events.jsonl 零 command 事件）

**根因**：那則 log 比對的是「上一則 log」而非手上的檔案，連筆數帳都是抄上一則的。

### 可重用教訓

curate 這類「讀檔 A 後 append 到 log B」的步驟，agent 極易拿 B 的前一則當 A 的內容依據——prompt 必須明文禁止並要求原文貼出 A 的檔頭；且 dream 報告會把 confabulation 原封升格成 High Priority 加錯藥方，**處理 dream 建議前要先獨立查證它的前提**。

## desc 基線與截斷閘門的空間限制

`check-bot-command-descriptions` 閘門把「desc 會被 `truncateBotCommandDescription` 截斷」視為失敗而非可接受，而 `/dream` 條目的 desc 基線是 232 字元——加上 button 前綴後距 256 上限僅約 11 字元餘裕。要在該欄位補說明幾乎無空間，應改為指向 schema 正本而非就地列舉。

## 已知混淆：skill 觸發語境重疊

`memory-to-skill` / `knowhow-accumulation` / `claude-mem-curate` 三個 skill 的觸發語境（回顧過去對話抽取可重用模式）高度重疊，雖輸出產物不同（ms-skill / ❌→✅ knowhow / AIMemory facts）但易造成選用混淆；`knowhow-accumulation` 自建立以來 use_count 仍為 0（使用者已明確裁決保留）。

## 相關

- [[bridge-memory]] — /dream 各維運步驟實際操作的記憶系統內容
- [[bridge-acp]] — ACP adapter 能力偵測與 model 設定（與 per-backend model 相關）
- [[bridge-project]] — 主專案頁
