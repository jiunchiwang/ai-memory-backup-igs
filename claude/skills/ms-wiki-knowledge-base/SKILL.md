---
name: ms-wiki-knowledge-base
description: 當 agent bridge 要維運雙層記憶（facts + wiki 知識庫）時使用：執行 wikisync（topic shard 蒸餾成 wiki 頁）、factlint（facts 去重/去瑣碎/衰減/升格偵測）、wikilint（wiki 過時/孤兒/斷連健康檢查），或要為新 bridge 設計同款 wiki 維運流程時使用
---

# Wiki 知識庫維運（wikisync / factlint / wikilint）

## 概述

Bridge 的記憶分兩層：**facts**（append-only 流水帳，master log + topic shards）與 **wiki**（結構化知識頁，`${MEMORY_DIR}/wiki/`）。facts 便宜好寫但會膨脹、退化；wiki 貴但可讀可引用。本 skill 是三個維運迴圈，把 facts 蒸餾上升為 wiki、並持續清理兩層的健康度。

核心原則：**寫入走 facts（低摩擦），閱讀走 wiki（高密度）；lint 迴圈負責單向蒸餾與雙向除錯，破壞性操作一律走 MCP tool + 人工確認，不走 shell。**

## Wiki 目錄結構

```
${MEMORY_DIR}/wiki/
├── index.md          ← 全頁面索引（wikilink + 一行摘要 + Total pages）
├── SCHEMA.md         ← frontmatter 與頁面格式規範
├── concepts/         ← 主題頁（由 topic shard 蒸餾）
├── lessons/          ← 踩坑教訓頁（含 BC-x/EH-x 可 grep 檢查點）
├── references/       ← 外部資源指標
└── queries/          ← 優質回答存檔（query auto-save 候選）
```

頁面 frontmatter 必含：`type`、`updated`、`sources: [f_xxxxxx, ...]`（來源 fact IDs，從 shard 行首 `[f_xxxxxx]` 提取）；lesson 頁另加 `why`（一句根因）。每頁至少 1 個 `[[wikilink]]`、≤200 行、結構化段落（不是 flat list）。

## 三個維運迴圈

### 1. wikisync — facts → wiki 蒸餾（建設性）

1. wiki/ 不存在先建目錄骨架 + 空 index.md
2. 讀 index.md 取得現有頁面；讀 topics 取得所有 shard
3. **≥5 facts 且無對應頁面**的 topic → 讀 shard、產出 `concepts/<topic>.md`
4. 已有頁面但 shard 有新內容 → 更新頁面 + bump `updated` + 追加 fact IDs 到 sources
5. 每次新增/更新後同步 index.md
6. 回報：新增/更新/跳過（含原因）

節流：一次最多 5 個 topic，避免 context 爆炸。
可注入兩種優先清單：**Ingest Ripple**（新 fact 寫入時標記受影響頁面，sync 時優先處理）、**Query Auto-save 候選**（被判定值得留存的回覆 → `queries/<slug>.md`）。

### 2. factlint — facts 除錯（破壞性，最小權限）

⛔ 安全鐵則：**絕不用 shell（node -e / sed / powershell / cat）直接讀寫 facts 檔**——Windows CRLF 會讓行比對失敗、寫回空檔毀掉資料。刪除一律走 MCP `forget()` tool（內部用 `/\r?\n/` 安全切行）。

逐 shard 檢查四類問題：
- **矛盾**：同主題對同一事物記了不同值 → 只列報告，不刪（等使用者確認）
- **過時**：被後面 fact 明確取代（改名/改 port/改路徑）→ 可刪
- **重複**：語意相同措辭不同 → 可刪
- **瑣碎**：一次性確認（「測試成功」）、過程紀錄（「commit xxx」）、只對當時 session 有意義、已被 wiki/skill 涵蓋 → 可刪

進階檢查：
- **衰減**：讀 access log，>60 天零命中的 topic 列「衰減候選」（不自動刪）
- **升格偵測**：同 shard 內 ≥3 條含「bug/修復/踩坑/workaround」關鍵字且無對應 lessons 頁 → 建議寫 `lessons/{topic}-pitfalls.md`
- **跨產出物矛盾**：lessons 頁的 BC-x/EH-x 檢查點 grep 對應程式碼，防護不存在即報矛盾（只查可 grep 的具體檢查點）

節流：一次最多 10 個 shard。可選配 local LLM pre-scan（dedup/合併建議）當提示注入，僅供參考不自動執行。

### 3. wikilint — wiki 健康檢查（診斷性）

對每頁檢查三項：
- **過時**：頁面 `updated` vs 對應 shard 最新 facts，shard 有新資訊未反映 → stale
- **孤兒**：index.md 有列但檔案不存在，或檔案存在但 index 未列
- **斷連**：`[[wikilink]]` 指向不存在的 slug

回報格式：🟢 健康數 / 🟡 stale（slug + 原因）/ 👻 orphans / 🔗 broken links / 建議動作。stale 且更新內容明確的直接修 + bump `updated`，其餘只列報告。

## 何時使用

- Bridge 定期維運（如 /dream 夜間流程）要跑記憶健康檢查
- Facts 膨脹（記錄性 >> 可行動性）需要清理
- 要為新的 agent bridge 設計 facts→wiki 雙層記憶架構

**不要用在：**
- 單層記憶系統（只有 facts 沒有 wiki）— 只取 factlint 部分即可
- 需要即時一致性的場景 — 這是批次維運迴圈，設計上容忍暫時 stale

## 踩坑教訓

- **CRLF 清空事故**：agent 曾繞過 MCP tool 用 `node -e` + `split('\n')` 過濾 CRLF 檔案，比對全失敗、寫回 0 bytes。防禦三層：prompt 開頭 ⛔ 禁令、寫入端空寫保護（kept=0 throw）+ 比例閘門（刪 >50% throw）、寫入前自動 `.bak.timestamp` 備份。
- **樂觀清理**：ripple/candidate 清單交給 agent 後即清標記；agent 部分失敗靠後續新 fact 寫入重新累積，不做精確 ack（簡單性 > 精確性）。
- **矛盾不自動刪**：自動化只刪「機械可判定」的（過時/重複/瑣碎），語意矛盾永遠留給人裁決。
