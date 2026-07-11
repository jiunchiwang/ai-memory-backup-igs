---
name: fact-embedding-backfill-gap
description: hit-log fact=0 的根因是 fact 文字從未被算 embedding（join 重疊 0），已加 backfill 修復；順帶記錄 dream 三項處理決策
metadata: 
  node_type: memory
  type: project
  originSessionId: 62402a1b-ecae-439b-8517-849db12b2937
---

2026-07-11 處理 dream 三項 High Priority 的結論：

1. **fact recall 恆 0 的根因**：`memory-db.ts` 的 `vectorSearch` JOIN `embedding_cache`，但全 codebase 只有 query 會被 `getEmbeddingCached` 嵌入，facts 表 195 筆 join 重疊實測 = 0 → vector 分量恆 0，hybrid 分數上限 0.3×decay < 0.2 門檻。修法：新增 `backfillFactEmbeddings()`（啟動非阻塞補算）+ `insertFact` fire-and-forget 補嵌入。**教訓：hybrid search 兩條腿（BM25+vector）要分別驗證有資料，join-based 檢索空集合是靜默失敗。**
2. **zombie skill 清理**：使用者決定保留 knowhow-accumulation / non-engineer-agent-design / skill-creator，store entry 已重建並 pinned=true。注意：sync.ps1 會重建正本裡所有 skill 的 junction，「只拆 junction」永遠不是有效的移除手段，要刪必須刪 AI-canonical 正本。
3. **uk-conventions 誤報**：是 custom command 非 skill；`markUsed` 會自動重建 entry（orphan=true），所以刪 entry 不持久——durable 修法是 skilllint prompt 加 notes 排除規則（notes 在 markUsed 更新時會保留）。

**Why:** 三項都有「表面修法無效」的陷阱（重啟不解決 embedding 缺失、拆 junction 會被 sync 重建、刪 entry 會被 markUsed 重建），先追資料流再動手。
**How to apply:** 遇到 dream/lint 類建議先驗證其假設（grep 資料流 + 查實際 DB/store 狀態），別照字面執行。相關：[[smoke-suite-env-pitfall]]
