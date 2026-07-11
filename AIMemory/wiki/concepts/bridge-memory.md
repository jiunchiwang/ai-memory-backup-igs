---
title: Bridge 記憶與維運系統
type: concept
created: 2026-07-11
updated: 2026-07-11
sources: [f_d21a12, f_b615b7, f_84107f, f_a4464b, f_054543, f_912029, f_152b53, f_e5843d, f_b01ccb, f_c965d5, f_a0a929, f_0c2487, f_dd41a9, f_7d8cb9, f_36529c, f_a8bb58, f_7cb830]
---

# Bridge 記憶與維運系統

> 2026-07-11 從 [[bridge-project]] 拆出。涵蓋 AIMemory 結構、/dream 維運、factlint、topic 分類、wiki 知識庫、embedding router、備份。

## AIMemory 結構

長期記憶系統位於 `G:\AI\AIMemory`：

- **facts** — master fact log（`facts-<userId>.md`）+ topic shards（`facts_Topic/<userId>/<topic>.md`）
- **topics** — 分類規則（`topics.json`）
- **wiki** — 結構化知識庫（concepts / references / lessons / queries）
- **dailylog** — 每日摘要
- **sessions** — 對話紀錄（處理完搬到 oldSessions）
- **config** — bridge 集中化配置（acp-providers、skill-usage 等）

## /dream 夜間維運

每日凌晨 04:00 自動執行 14 步：memorytoskill → topicreview → wikisync → factlint → wikilint → skilllint → specialistreview → artifactcleanup → docupdate → backup → restart 等。`dream.json` 位於 `~/.kiro/dream.json`（fork 比 upstream 多 docupdate 一步），不依賴 bridge 內建 DEFAULT_STEPS fallback。維運結果寫 `STATE.md`（三層：High Priority / Watch List / Noise）。

## Topic 分類系統

`topics.json` 定義 keyword-based first-match-wins 分類規則，bridge 每 2 秒重讀（改完即生效，不需重啟）。fact 文字轉小寫後做 substring 比對，無匹配歸 misc。topicreview 步驟會定期實體重分 shard（如 2026-07-10 新建 bridge-streaming shard、misc 清零）。

## Wiki 知識庫

wikisync 步驟把 topic shard 蒸餾成 wiki 頁，門檻 ≥5 facts 自動產出 concepts 頁。配套模組（Karpathy P0，commit 6931445）：

1. **activity-log.ts** — 統一讀取 hit-log / event-log / observations JSONL
2. **ingest-ripple.ts** — hook 在 `remember()` 的 `insertFact` 後標記 wiki 漣漪式更新，wikisync 組 prompt 時注入優先清單
3. **query-auto-save.ts** — 自動偵測優質回覆存為 wiki 候選

頁面過長時拆分（先例：bridge-acp、bridge-session、bridge-streaming、bridge-memory、bridge-specialist），原頁留指標 stub，並在 topics.json 加對應規則分流未來 facts。

## Factlint 三層防禦

2026-07-01 因 agent 繞過 MCP `forget` tool 改用 `node -e` shell command，`split('\n')` 對 CRLF 檔案比對失敗導致 master facts 清空。事後建立：

1. **Preamble 硬禁令**：FACTLINT_PROMPT 開頭 `⛔ CRITICAL SAFETY RULE` 禁止 shell 直接操作 facts 檔
2. **空寫保護 + 比例閘門**：`forgetCommit()` 中 `kept.length === 0` 或刪除 >50% 時 throw
3. **寫前備份**：寫入前自動 `copyFileSync` 到 `.bak.<timestamp>`

Factlint ratio 3.0 目標在 87%+ wiki-protection 下結構性不可達，已接受為設計取捨（實測 ~9.75）。

## Embedding Router

本地 ONNX 模型 `bge-small-zh-v1.5`（23.3 MB），2.6 ms/embed、512 維。快取在 `node_modules/@xenova/transformers/.cache/`。7 個語意應用：memory recall、skill routing、wiki retrieval、notebook routing、intent classification、sticker auto-select、重複 fact 偵測。

### 解耦修復（2026-07-06，commit ae19ebd）

原本 model 載入被綁在 `notebooklm-routing.json`——檔案缺失時整個 embedding 子系統不啟動，連坐 8 個功能。修復後 `initEmbedModel()` 無條件載入；`isEmbedRouterReady` 語意收窄為「NotebookLM 路由就緒」，其他模組改用 `isEmbedModelReady`。

### Fact embedding backfill（2026-07-11，commit 14d81ad）

fact recall 恆 0 的根因：fact embedding 從未被算（facts 195 vs embedding_cache join 重疊 0，vectorSearch 恆空）。修法：啟動時 `backfillFactEmbeddings` 補算 + `insertFact` fire-and-forget 嵌入。表面修法（調門檻/重啟）無效，必須補 embedding 本體。

### NotebookLM 懸案

`config/notebooklm-routing.json` 缺失，根因是 NotebookLM MCP server 從未安裝；`scripts/setup-local-notebooklm-mcp.mjs` 有架構性錯配需先修（2026-07-06 使用者決定暫緩）。

## 備份機制

- 備份 repo：`G:\AI\ai-memory-backup-igs`，remote `https://github.com/jiunchiwang/ai-memory-backup-igs.git`（branch: master）
- `/backup` 指令：robocopy AIMemory + agent 設定目錄到 repo → git push
- 每日 /dream 自動觸發

## 相關

- [[bridge-project]] — 專案總覽
- [[bridge-specialist]] — Specialist 分身系統（specialist memory 回寫見該頁）
- [[ai-strategy]] — 正典語料庫與跨模型策略
