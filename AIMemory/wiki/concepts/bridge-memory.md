---
title: Bridge 記憶與維運系統
type: concept
created: 2026-07-11
updated: 2026-08-15（topicreview 阻塞已修：phase-aware guidance 上線 commit 892f68f；補記 renderTopicReviewSnapshot 兩個呼叫者更正、topicreview 回歸斷言已知缺口、skill orphan 涵蓋不到 plugin marketplace 補充事實來源）
sources: [f_d21a12, f_b615b7, f_84107f, f_a4464b, f_054543, f_912029, f_152b53, f_e5843d, f_b01ccb, f_c965d5, f_a0a929, f_0c2487, f_dd41a9, f_7d8cb9, f_36529c, f_7cb830, f_a1f2f2, f_909065, f_741af7, f_e737a7, f_b7367a, f_182f52, f_484853, f_de06cc, f_36e49d, f_77ddbd, f_e3b009, f_e6facf, f_15ac36, f_6a6c22, f_f94c52, f_ace685, f_b773d9, f_8cc27f, f_437274, f_a8b737, f_9a349f, f_0e4a79, f_072633, f_900c14, f_51511f, f_5c1956, f_5e6afb, f_9a7397, f_34a003, f_6f6762, f_7fb676, f_842a1b, f_e17260, f_e547d2, f_d742a1, f_99e9ba, f_88c0ba, f_213f2c, f_622428, f_ee9da7]
history_sources: [f_713852, f_017f18]
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

**⚠️ `apply_topics` 必然被拒 —— P2 未開啟卻被要求帶 P2-only token（2026-08-14 實測定案）**：`applyTopics`（`src/facts-store.ts:1759-1777`）只有在 `MEMORY_EVENT_TAXONOMY_ENABLED=1` 時才拿 `expectedToken` 比對 `MemorySnapshotId`（`ms1_` 開頭）；該 flag 在 `memory-rollout.ts` 的 `defaultEnabled=false` 且 `.env` 未設 ∴ 走 legacy 分支，比對的是 `computeTopicsToken()` 的 `topics-<sha1前8>-<條數>`。兩個命名空間不相交，而 `renderTopicReviewSnapshot`（`facts-store.ts:1510`）無條件印 `ms1_` token、`TOPIC_REVIEW_PROMPT` 第 3 步（`src/commands/memory.ts:229`）無條件要求原樣帶它 ⇒ 必拒。

- **重試不收斂的原因**：legacy 的 expected 是「該次呼叫傳入的 topics 陣列」的雜湊，陣列一變 expected 就變——不是 token 遺失（2026-08-13 記的「token 被輸出截斷丟失」推測已被反證）。
- **⚠️「每輪重燒」與 apply 成敗無關**（本頁初版寫成「throw 就不 acknowledge ∴ trigger 下輪再命中」，2026-08-14 經跨 vendor 覆核推翻）：P2 off 時 `topicReviewCheck()` 回的是寫死的 `shouldReview: true`（`src/memory-taxonomy-maintenance.ts:359-370`），`acknowledgeTopicReview()` 則直接 `return null` 不寫任何 state（同檔 `:433`）∴ **apply 就算完全成功，下一輪照樣觸發**。P2 off 下根本沒有 acknowledge 機制。
  > 教訓形狀同 `correction-invents-new-causal-story`：真實觀察（連 3 輪 `written=false`）被接上一個沒查證的機制，數字對、語氣自信、因果是編的。抓到它的是異源覆核，不是自審——自審那輪還把這個機制同時寫進 fact、wiki、docs 與兩處碼註解。
- **零改動 workaround**：非 P2 下**省略 `expectedToken`**，`mcp-memory.ts:1030` 會自動補 `dryRunToken`；`normaliseProposedTopics` 對正式 `topics.json` 實測冪等（三次皆 `topics-884fede8-32`）∴ 必定通過。
- **錯誤訊息本身會誤導**：legacy 分支建議「re-run propose_topics to get a fresh token」，但重跑 propose 只會再給一個 `ms1_` token，永遠不會match。

實測重現（`dist/` 直接 import、temp `MEMORY_DIR`、驗證在寫檔前 throw）：傳 `ms1_...` 得 `topics token mismatch (got=ms1_..., expected=topics-f67c5d32-2)`。`propose_topics` 本身唯讀、不受影響。

**✅ 已修（2026-08-14，commit `892f68f`，phase-aware guidance）**：使用者選修法 A——讓 guidance 跟著 P2 flag 走、不動 P2 rollout 本身（排除 B「開啟 P2 flag」因為 rollout 有 source mutation 與三步 rollback 成本，屬獨立決策；排除 D「只用手動 workaround」因為 dream 自動迴圈跑的是寫死的 `TOPIC_REVIEW_PROMPT`，子 session 不會知道 workaround）。新增 `renderExpectedTokenGuidance()` 依 `MEMORY_EVENT_TAXONOMY_ENABLED` 產生指示（P2 off 明講「省略 expectedToken」、snapshot id 降級為 provenance），`/topicreview` prompt／`apply_topics` tool schema／`docs/`／`README` 全部改成指回 `propose_topics` 印的那一行，不再各自複述 flag 相依規則；legacy 拒絕訊息不再給「re-run propose_topics」這條死路。

⚠️ **`renderTopicReviewSnapshot` 有兩個 production 呼叫者，不是一個**：`mcp-memory.ts` 的 `propose_topics` handler（agent 真正讀到的那份）與 `memory-baseline.ts:408` 的 `topicReviewPayloadChars`（只取 `.length`）。2026-08-14 連兩輪跨 vendor 覆核都只枚舉到前者，自己的因果鏈也因 grep 結果被 `head_limit` 截斷而寫成「唯一」——覆核者確認的是既有錯誤（回音而非獨立驗證）。實際影響：`check-memory-baseline.mjs:122` 是相對斷言（兩邊同一個 renderer 現算）∴ 不受影響，但 `topicReviewPayloadChars` 這個成本指標從此隨 P2 flag 微幅變動（百字級 vs 千字級 payload）。

⚠️ **回歸斷言缺口（已知未修，非靜默略過）**：沒有任何閘門覆蓋 MCP handler 層的 `expectedToken` 補值邏輯——該 handler 是註冊在 `server.setRequestHandler` 上的 inline closure（`mcp-memory.ts:726`，未 export），要覆蓋需另建 MCP stdio 測試 harness，成本與風險不成比例。替代做法是補一條讓該 fallback 安全的不變式斷言（`normaliseProposedTopics` 冪等，`check-topic-review.mjs` 第 6f 段）。

## Wiki 知識庫

wikisync 步驟把 topic shard 蒸餾成 wiki 頁，門檻 ≥5 facts 自動產出 concepts 頁。配套模組（Karpathy P0，commit 6931445）：

1. **activity-log.ts** — 統一讀取 hit-log / event-log / observations JSONL
2. **ingest-ripple.ts** — hook 在 `remember()` 的 `insertFact` 後標記 wiki 漣漪式更新，wikisync 組 prompt 時注入優先清單
3. **query-auto-save.ts** — 自動偵測優質回覆存為 wiki 候選

頁面過長時拆分（先例：bridge-acp、bridge-session、bridge-streaming、bridge-memory、bridge-specialist），原頁留指標 stub，並在 topics.json 加對應規則分流未來 facts。roadmap 類長期追蹤內容選擇放獨立 wiki page（如 `bridge-roadmap`）而非散在 facts 用前綴標記——理由是跟現有 wiki 系統整合、preamble 可見、wikilint 自動維護，散在 facts 沒有優先級/狀態追蹤能力。

`G:\AI\AIMemory\wiki` 底下**沒有 SCHEMA.md**（只有 `index.md`、四個子目錄、兩個 `.jsonl`）——新增頁面時應比對現有同型頁面的實際 frontmatter 格式（concept 型見本頁；query 型為 `title`/`type`/`created`/`updated`/`sources`），不要假設有一份權威 schema 文件可查。

## Factlint 三層防禦

2026-07-01 因 agent 繞過 MCP `forget` tool 改用 `node -e` shell command，`split('\n')` 對 CRLF 檔案比對失敗導致 master facts 清空。事後建立：

1. **Preamble 硬禁令**：FACTLINT_PROMPT 開頭 `⛔ CRITICAL SAFETY RULE` 禁止 shell 直接操作 facts 檔
2. **空寫保護 + 比例閘門**：`forgetCommit()` 中 `kept.length === 0` 或刪除 >50% 時 throw
3. **寫前備份**：寫入前自動 `copyFileSync` 到 `.bak.<timestamp>`

Factlint ratio 3.0 目標在 87%+ wiki-protection 下結構性不可達，已接受為設計取捨（實測 actionable ratio ~4.7，>3.0 警告閾值視為已知取捨，未來 factlint 遇到此警告應跳過不報，除非 wiki-unprotected facts 本身有新問題）。

**Factlint vs forget 政策衝突裁決（2026-07-08）**：接受 wiki-reference 保護——wiki `sources` 引用的 fact 是 provenance 不可刪（排除解除引用再刪，因為工程量大）；例外：若引用僅是 frontmatter `sources` 溯源清單（內容已蒸餾進頁面），可先從該 wiki 頁 `sources` 移除該 fact id 再刪，避免留 dangling ref（2026-07-12 補充操作）。

**forgetMatch 陷阱**：比對的是 `stripFactPrefix` 後的內文（`[f_id]` 前綴已被剝掉），用 fact id 當 query 永遠 0 匹配——正確做法是用該 fact 的獨特內文子字串查詢，再用 `extractFactId` 驗證匹配行的 id 才刪。

**Headless 場景的額外防線**：在無人值守的自動化腳本中，用 `claude.exe` 的 `--disallowedTools` 參數封鎖 `mcp__memory__remember` 與 `mcp__memory__forget`，可強制走 proposal-only（只提案、不直接寫入記憶）工作流程，避免自動流程擅自改寫長期記憶。

**判斷是否受 wiki 保護不要自己先 Grep 猜（2026-08-12）**：對 9 條 factlint 候選 fact 各自用 Grep 找過一次逐字子字串，6 條回「無命中」，但呼叫 `forget()` 後 MCP 的 `checkWikiReferences`（權威實作）全部回報「受保護」，指出的頁面 Grep 完全沒抓到。Grep 落空不代表沒保護——判斷是否受保護要直接呼叫 `forget()` 讓伺服器端全文掃描裁決，最快也最準。

## 記憶命中日誌與衰減判斷

命中有兩套 log：`fact-access-log.jsonl` 只在 agent 手動呼叫 `list_facts` 時寫入（06-26 後幾乎停寫，`trackAccess` 保留為 write-only 殘留），`hit-log.jsonl` 由 embedding 語意召回自動寫入，factlint 衰減檢查統一讀 `hit-log.jsonl`（commit f1a4e01）。2026-07-08 前 hit-log fact/wiki 零命中是假性的——根因是 `logHit` 只在 `enrichment.ts`（僅 specialist 走）呼叫，主 turn 的 `index.ts` inline 複製版漏了這行；修復（commit 540325b）後 factlint 衰減判斷應以 2026-07-08 為起算點，之前的空窗不代表真的零召回。

Preamble 大小取捨：佔 context 5-6% 可接受，到警戒線才削減；優先砍 facts tail 與 guideline 區塊（不動 wiki 索引），理由是舊 facts 有 topic index + `list_facts` 補位。實例：`MEMORY_PREAMBLE_TAIL` 已從 15 砍到 10（commit 3885a8b，.env 與 .env.example 同步改，preamble 預估 12.9k → 11.7k chars，需重啟生效）；排除砍到 5，因為 facts 爆發式寫入會斷跨日工作連續性（embedding 召回按語意不按時間近撈，補不了）。

### hit-log 衰減判定的觀測期間限制（2026-08-01 補充）

`hit-log.jsonl` 最早的 `type:"fact"` 命中是 **2026-07-11**。因此 factlint 的「60 天未命中」衰減判定在 **2026-09-09 之前都屬觀測期間不足**，不該產出衰減候選。超過半數的 facts 建檔早於 07-11，對它們來說 60 天衰減根本還沒開始計時。

## Skill Lint

讀 `${MEMORY_DIR}/config/skill-usage.json` 的 `use_count` 與 `last_agent_used_at`，評估各 skill 是否仍被使用、需否淘汰。2026-07-11 曾把 `knowhow-accumulation`／`non-engineer-agent-design`／`skill-creator` 標為殭屍 skill，經評估決定保留不刪——日後 skilllint 再標記這三個應視為已知豁免，不需重複提案刪除。

**Codex CLI 原生 skill 支援（2026-08-05）**：Codex CLI 0.146.0 原生支援 skills 機制（掃 `~/.codex/skills/`，內建 skill 放 `.system/` 子目錄），且 `SKILL.md` frontmatter 格式與 Claude 完全一致（`name` + `description`），因此同一份 skill 正本可三個 CLI 共用不需改寫。跨 CLI 可攜性盤點見 [[bridge-dream]]。

已知的孤兒清單狀況：`skill-usage.json` 的 `vc-uof-hours` entry 仍指向已改名的資料夾 `igs-uof`，且 `igs-uof`、`uk-slot-logo-localization` 兩個實際存在的 skill 資料夾未被登記 usage entry，待合併/補建。另外 `uk-conventions` 是 Claude Code custom command（位於 `AI-canonical-corp/commands/uk-conventions.md`），不是 skill——skilllint 的 orphan 偵測對它是 false positive，應排除不報。

**orphan 判定結構性涵蓋不到 plugin marketplace（2026-08-13）**：`usageStore` 的 skill orphan 判定只掃 `~/.{kiro,codex,claude}/skills/` 的 `<name>/` 與 `.system/<name>/` 六條路徑，涵蓋不到 `~/.claude/plugins/marketplaces/*/skills/`——任何 plugin skill 被 agent 自報 `<<SKILL_USED>>` 後都會在 `skill-usage.json` 留下 `orphan=true` 的假孤兒（`claude-api` 實例，已用 `notes` 標 false positive 讓 `/skilllint` 跳過，未改掃描邏輯以免多出約 20 筆從未使用的 plugin skill entry）。

**Node `readdirSync` 不跟隨 junction 的靜默失效（2026-08-04）**：`readdirSync(dir,{withFileTypes:true})` 回的 `Dirent` 對 junction/symlink 一律 `isDirectory()===false`、`isSymbolicLink()===true`——而這台機器的 skill 投影全靠逐 skill junction，任何 `readdirSync(...).filter(e=>e.isDirectory())` 掃 skill 目錄的碼拿到的都是靜默空集合。`scripts/refresh-codex-skill-links.mjs` 就這樣壞掉且沒人發現：`sourceNames` 恆空造成建立邏輯全斷、移除迴圈把既有 link 全判 stale 刪掉（每跑一次 `postinstall` 清空一次 Codex）。正確寫法是篩「目錄或指向目錄的 symlink」並用 `statSync` 跟隨連結確認。這條是異源覆核抓到的（主 agent 讀碼推理判斷方向完全相反），案例見 [[adversarial-review]]。

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

## 瑣碎 fact 的審核判準（2026-07-30 使用者逐條裁決）

wiki-reference 保護會讓 factlint 想刪的 fact 刪不掉，於是「哪些真的該刪」需要人的判準。實際裁決結果：

| 類型 | 處置 | 理由 |
|---|---|---|
| 純進度快照（日期綁定、wiki 頁已有同等彙整版） | **刪** | 資訊已被 wiki 取代，例如「M0a 完成」「三步驟已完成」「wiki 頁拆分記錄」 |
| 標題寫「完成」但內含技術細節（按鈕 selector、五層防線設計、API 行為） | **留** | 有持久參考價值，不因「完成」字樣而瑣碎 |

要真的刪掉受保護的 fact，流程是**先從相關 wiki 頁的 `sources:` frontmatter 移除該 fact id 解除保護，再 `forget()`**。但 2026-07-08 裁決是「接受保護、不解除引用」——所以這條流程是例外手段，不是常規。

**第二個例外：內容已被證實為假的 fact（2026-08-13）**：若 wiki sources 保護的 fact「內容已被證實為假」，同樣允許先移除 sources 再 `forget()`——理由是假 fact 被注入 preamble 當事實，成本高於它的 provenance 價值。此例外**不推翻**上面「瑣碎但為真」那類的保護裁決，兩者適用範圍不同：一個看內容真偽，一個看內容是否瑣碎。刪除後刻意不補記替代快照——可從設定檔直讀的現況不入 fact，否則同樣會腐爛（例：`bridge-specialist` shard 一則記錯 model pin 的 fact 已按此例外刪除）。

### `[WS]` working-state facts 應主動清理（2026-08-01 實證）

`<<RESTART>>` 前寫入的 `[WS] task/completed/blocked/key_refs/next_action` 是**設計上的過渡性筆記**，restart 完成後就沒有價值，而且會出現兩種害處：

1. 持續佔用 preamble 的 memory recall 額度（每輪都被召回）
2. 若當時的結論後來被推翻，它們會把**已否證的結論**餵回未來的 session

2026-08-01 一次清掉 8 條（bridge-streaming 的 draft 診斷 WS 組，其中 3 條主張的 H1 根因已被實測推翻）。判準：`[WS]` 前綴 + 對應工作已結束 + 未被任何 wiki 頁 `sources` 引用 → 可直接 `forget()`。

## 延伸筆記（積壓補記）

- `src/tool-hooks.ts` 的 PostToolUse hooks 是 Post、fire-and-forget，**僅 direct provider 路徑（`tool-loop.ts`）生效**——走任何 ACP 時不會 fire，不能當阻擋式閘門機制。
- 設定檔自動建立方案：選 `/agent init` 顯式子指令（排除啟動時自動 seed，因為靜默寫檔到 `MEMORY_DIR` 違反「不逕自動作」偏好；排除訊息內嵌範本，因為手機複製貼上麻煩）。
- `check-moa` 壞測試根因比原判大：某次改動不只把 `resolvePreset` 改 async，還以 embedding routing 整個取代 keyword routing（`routing.rules` 不再被讀），測試已對齊新語義。
- 「UK 助理知識包」交付架構（2026-07-28 定案，可作為小規模領域知識問答機器人的預設架構）：採快照式蒸餾檔案 + headless agent CLI 直接讀取，刻意不引入向量資料庫與 embedding 層——RAG 基礎設施的維運成本通常高於快照重生成的成本；配套三層把關為敏感資料過濾、明確的知識更新工作流、交付前驗證。

## 相關

- [[bridge-project]] — 專案總覽
- [[bridge-specialist]] — Specialist 分身系統（specialist memory 回寫見該頁）
- [[ai-strategy]] — 正典語料庫與跨模型策略
