---
title: Bridge 記憶與維運系統
type: concept
created: 2026-07-11
updated: 2026-07-21
sources: [f_d21a12, f_b615b7, f_84107f, f_a4464b, f_054543, f_912029, f_152b53, f_e5843d, f_b01ccb, f_c965d5, f_a0a929, f_0c2487, f_dd41a9, f_7d8cb9, f_36529c, f_a8bb58, f_7cb830, f_a1f2f2, f_909065, f_741af7, f_e737a7, f_b7367a, f_182f52, f_484853, f_de06cc, f_36e49d, f_77ddbd, f_e3b009, f_e6facf, f_15ac36, f_6a6c22, f_f94c52, f_ace685, f_b773d9, f_8cc27f, f_437274]
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
- **user-profile.md** — 使用者畫像獨立化（5 區塊：身份/溝通風格/工作偏好/Agent設定偏好/工作節奏），preamble 固定注入於 envBlock 和 memoryBlock 之間；因為畫像是穩定結構化資料所以獨立成檔（排除混在 facts 因為語意召回不保證每次注入）

## /dream 夜間維運

每日凌晨 04:00 自動執行 14 步：memorytoskill → topicreview → wikisync → factlint → wikilint → skilllint → specialistreview → artifactcleanup → docupdate → backup → restart 等。`dream.json` 讀取路徑優先序：`MEMORY_DIR/config/dream.json`（目前不存在）→ 退回 `~/.kiro/dream.json`（此機器實際生效檔）→ 內建 DEFAULT_STEPS fallback。每步 `cmd` 字串須存在於 `index.ts` 的 `COMMAND_HANDLERS` map 才會被執行，否則判定「未知指令已跳過」但不中斷其餘步驟（`continue_on_error` 預設 true）。維運結果寫 `STATE.md`（三層：High Priority / Watch List / Noise）。High Priority 非空時另有跨 ACP 入口：新 session preamble 注入 `[Pending dream suggestions]` block（`STATE.md` Last run<48h 且非空才注入、只讀不刪、隨 preamble 凍結），dream 寫完 STATE.md 後另發「處理 High Priority」按鈕（callback 點擊時重讀檔案丟給主 session）。

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

Factlint ratio 3.0 目標在 87%+ wiki-protection 下結構性不可達，已接受為設計取捨（實測 actionable ratio ~4.7，>3.0 警告閾值視為已知取捨，未來 factlint 遇到此警告應跳過不報，除非 wiki-unprotected facts 本身有新問題）。

**Factlint vs forget 政策衝突裁決（2026-07-08）**：接受 wiki-reference 保護——wiki `sources` 引用的 fact 是 provenance 不可刪（排除解除引用再刪，因為工程量大）；例外：若引用僅是 frontmatter `sources` 溯源清單（內容已蒸餾進頁面），可先從該 wiki 頁 `sources` 移除該 fact id 再刪，避免留 dangling ref（2026-07-12 補充操作）。

**forgetMatch 陷阱**：比對的是 `stripFactPrefix` 後的內文（`[f_id]` 前綴已被剝掉），用 fact id 當 query 永遠 0 匹配——正確做法是用該 fact 的獨特內文子字串查詢，再用 `extractFactId` 驗證匹配行的 id 才刪。

**Headless 場景的額外防線**：在無人值守的自動化腳本中，用 `claude.exe` 的 `--disallowedTools` 參數封鎖 `mcp__memory__remember` 與 `mcp__memory__forget`，可強制走 proposal-only（只提案、不直接寫入記憶）工作流程，避免自動流程擅自改寫長期記憶。

## 記憶命中日誌與衰減判斷

命中有兩套 log：`fact-access-log.jsonl` 只在 agent 手動呼叫 `list_facts` 時寫入（06-26 後幾乎停寫，`trackAccess` 保留為 write-only 殘留），`hit-log.jsonl` 由 embedding 語意召回自動寫入，factlint 衰減檢查統一讀 `hit-log.jsonl`（commit f1a4e01）。2026-07-08 前 hit-log fact/wiki 零命中是假性的——根因是 `logHit` 只在 `enrichment.ts`（僅 specialist 走）呼叫，主 turn 的 `index.ts` inline 複製版漏了這行；修復（commit 540325b）後 factlint 衰減判斷應以 2026-07-08 為起算點，之前的空窗不代表真的零召回。

Preamble 大小取捨：佔 context 5-6% 可接受，到警戒線才削減；優先砍 facts tail 與 guideline 區塊（不動 wiki 索引），理由是舊 facts 有 topic index + `list_facts` 補位。實例：`MEMORY_PREAMBLE_TAIL` 已從 15 砍到 10（commit 3885a8b，.env 與 .env.example 同步改，preamble 預估 12.9k → 11.7k chars，需重啟生效）；排除砍到 5，因為 facts 爆發式寫入會斷跨日工作連續性（embedding 召回按語意不按時間近撈，補不了）。

## Skill Lint

讀 `${MEMORY_DIR}/config/skill-usage.json` 的 `use_count` 與 `last_agent_used_at`，評估各 skill 是否仍被使用、需否淘汰。2026-07-11 曾把 `knowhow-accumulation`／`non-engineer-agent-design`／`skill-creator` 標為殭屍 skill，經評估決定保留不刪——日後 skilllint 再標記這三個應視為已知豁免，不需重複提案刪除。

已知的孤兒清單狀況：`skill-usage.json` 的 `vc-uof-hours` entry 仍指向已改名的資料夾 `igs-uof`，且 `igs-uof`、`uk-slot-logo-localization` 兩個實際存在的 skill 資料夾未被登記 usage entry，待合併/補建。另外 `uk-conventions` 是 Claude Code custom command（位於 `AI-canonical-corp/commands/uk-conventions.md`），不是 skill——skilllint 的 orphan 偵測對它是 false positive，應排除不報。

## 維運工具與接線陷阱

- **memory MCP 未連線時的救援路徑**：可在 `G:\AI\AIMemory\tmp\mcp-call.mjs` 自建 stdio JSON-RPC helper 直接 spawn `dist/mcp-memory.js` 呼叫記憶工具（cwd 須設為 bridge 專案根、注入 `MEMORY_USER_ID`/`MEMORY_DIR`）；`tmp/` 會被定期清空，helper 不在時照此模式重建。session 完全無 MCP 時的等效刪除路徑：寫一次性 script 用 `npx tsx` 直接 import `facts-store.ts` 的 `forgetCommit()` + `memory-db.ts` 的 `deleteFact()`（與 MCP `forget` 同一條程式路徑，含備份/50% 閘門/稽核）。
- **smoke script 環境隔離**：`bridge session` 內跑 `scripts/check-*.mjs` 要用 `env -u` 清掉 `.env` 繼承變數但保留 `MEMORY_DIR`（清掉會 fallback 到不存在路徑 ENOENT 假失敗）。
- **smoke 隔離測試的 hoist 陷阱**：`dist` 模組的路徑由 config（dotenv）在 import 時定案，隔離測試必須「先設 `process.env.MEMORY_DIR=temp` 再 `await import()`」——ESM 靜態 import 會 hoist 到 env 設定之前，修了等於沒修；dotenv 不覆蓋既有 env 所以先設即生效。
- **三個 CLI 的 memory MCP 註冊全指向同一檔案** `dist/mcp-memory.js`：Claude 在 `~/.claude.json`、Kiro 在 `~/.kiro/agents/main.json`（specialist 繼承）、Codex 在 `~/.codex/config.toml`——修本體即三家同時生效。但主程序跑 `tsx` 直吃 `src`，MCP 子行程三個 CLI 都吃 `dist`，改到 `mcp-memory` 的 import 鏈必須 `npx tsc -p .` 重建 `dist` 才生效，且要重啟 session 才會重新 spawn MCP。
- **config.js import 陷阱**：任何會被 `mcp-memory` 子行程載入的模組禁止 `import config.js`——config 模組層 `required(TELEGRAM_BOT_TOKEN)`，而 `acpClient.buildSpawnEnv` 刻意把該 token 置空防 409，import 即炸導致 memory MCP 啟動即死（Karpathy P0 的 `ingest-ripple` 曾引入此鏈，2026-07-12 改用 `facts-store.ts` 的 `resolveMemoryDir()` 修復）；`MEMORY_DIR` 解析一律用 `resolveMemoryDir()`。

## Embedding Router

本地 ONNX 模型 `bge-small-zh-v1.5`（23.3 MB），2.6 ms/embed、512 維。快取在 `node_modules/@xenova/transformers/.cache/`。7 個語意應用：memory recall、skill routing、wiki retrieval、notebook routing、intent classification、sticker auto-select、重複 fact 偵測。

### 解耦修復（2026-07-06，commit ae19ebd）

原本 model 載入被綁在 `notebooklm-routing.json`——檔案缺失時整個 embedding 子系統不啟動，連坐 8 個功能。修復後 `initEmbedModel()` 無條件載入；`isEmbedRouterReady` 語意收窄為「NotebookLM 路由就緒」，其他模組改用 `isEmbedModelReady`。

### Fact embedding backfill（2026-07-11，commit 14d81ad）

fact recall 恆 0 的根因：fact embedding 從未被算（facts 195 vs embedding_cache join 重疊 0，vectorSearch 恆空）。修法：啟動時 `backfillFactEmbeddings` 補算 + `insertFact` fire-and-forget 嵌入。表面修法（調門檻/重啟）無效，必須補 embedding 本體。

### NotebookLM 懸案

`config/notebooklm-routing.json` 缺失，根因是 NotebookLM MCP server 從未安裝；`scripts/setup-local-notebooklm-mcp.mjs` 有架構性錯配需先修（2026-07-06 使用者決定暫緩）。

## 備份機制

- AIMemory（`G:\AI\AIMemory`）本身**不是 git repo**，版本保護走 `/backup` 備份機制（robocopy 到獨立備份 repo 再 push），wiki/topics.json/STATE.md 改動不需 git commit
- 備份 repo：`G:\AI\ai-memory-backup-igs`，remote `https://github.com/jiunchiwang/ai-memory-backup-igs.git`（branch: master）
- `/backup` 指令：robocopy AIMemory + agent 設定目錄到 repo → git push
- 每日 /dream 自動觸發

## 相關

- [[bridge-project]] — 專案總覽
- [[bridge-specialist]] — Specialist 分身系統（specialist memory 回寫見該頁）
- [[ai-strategy]] — 正典語料庫與跨模型策略
