---
title: 為何 doctor 報「Embedding router 未就緒」
type: query
created: 2026-07-06
updated: 2026-07-06
sources: [f_6a3827, f_054543, f_1dbc98]
---

# 為何 doctor 報「Embedding router 未就緒」

2026-07-06 使用者問：doctor 的 Embedding 檢查若沒用 NotebookLM，embed router 從未初始化 → 報「router 未就緒」，會影響不少功能？診斷結論：**推測正確，且影響面比 NotebookLM 路由大很多**。

## 根因

`src/index.ts` 把 embedding model 的載入綁在 `notebooklm-routing.json` 上：

- 檔案不存在（ENOENT）→ `initEmbedRouter()` 完全不跑 → `embedder` 永遠 null
- 但 `initEmbedRouter()` 做兩件事：**載入 ONNX embedding model** + 算 notebook centroids——model 本身跟 NotebookLM 無關，卻被 routing table 的存在與否 gate 住

## 受影響功能（9 個模組全靠 `embedText()` / `isEmbedRouterReady()`）

語意記憶召回（memory-recall）、skill 語意路由（skill-router）、wiki 語意檢索（wiki-retrieval）、意圖分類（intent-classifier）、index 檢索、SQLite 向量搜尋（memory-db）、page index 語意搜尋、sticker 情緒 fallback（run-prompt）、NotebookLM 路由（enrichment，預期內）。

∴ doctor 報「router 未就緒」實際意義是**整個 embedding 子系統都沒起來**。

## 修法（已採行：解耦修復，commit ae19ebd）

- 新增 `initEmbedModel()` 啟動時無條件載模型（冪等）；`initEmbedRouter()` 只負責 centroids
- 其他 8 個模組 gate 從 `isEmbedRouterReady` 換成 `isEmbedModelReady`
- doctor 拆分：model 未載 → ✗；model 就緒但缺 routing → ✓ 附註「NotebookLM 路由未載入」
- 排除「先生成 routing.json」方案：依賴未安裝的 NotebookLM MCP，會卡

## 注意事項

- 需重啟 bridge 生效；首次啟動從 HuggingFace 下載 `Xenova/bge-small-zh-v1.5`（約 100MB），之後走快取

## 相關

- [[bridge-project]] — Embedding Router 與 NotebookLM 懸案完整脈絡
