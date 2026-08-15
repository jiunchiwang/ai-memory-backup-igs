---
title: 什麼情況下會自動使用 specialist
type: query
created: 2026-07-10
updated: 2026-07-10
sources: []
---

# 什麼情況下會自動使用 specialist

2026-07-10 使用者問：「你在什麼情況下會自動使用 specialist？」

## `<<SPECIALIST_PROXY:...>>`（即時互動）

當使用者的問題明確屬於某 specialist 領域且需要來回對話：

| Specialist | 自動觸發情境 |
|---|---|
| `slot-dev` | UK slot 專案的實作問題（改 code、debug、codegen） |
| `researcher` | 需要深度網路研究、多來源比較 |
| `general` | 不屬於以上兩類但需要專注互動的任務 |

## `<<PARALLEL_DELEGATE:...>>` / `<<RELAY_DELEGATE:...>>`（背景任務）

當任務可拆成獨立子任務且各自耗時 > 1 分鐘：
- 同時研究多個不相關主題
- 同時改不同模組/專案（不碰同一個檔案）
- 批量獨立作業（例如多支影片逐一分析）

## 實際判斷標準

大多數情況不會自動轉，而是主 agent 自己處理。會主動轉的條件：

1. **Context budget 壓力** — 研究型任務預估 >10 tool calls，轉 `researcher` 省主 session context
2. **領域專精** — slot 實作涉及框架細節，`slot-dev` 的工作目錄和 steering 更貼近
3. **並行加速** — 明確可拆且使用者在等結果

不會自動轉的情況：簡單問答、單步操作、使用者明確在跟主 agent 對話的語境。

## 後續決策（同一 session）

同一輪對話中，specialist review 曾建議新增 `bridge-dev` specialist（涵蓋 bridge-acp/bridge-research/bridge-session/bridge-project 共 97 則 facts），使用者詢問是否採納。判定**不需要**：主 agent 本身工作目錄就是 telegram-kiro-bridge-main，CLAUDE.md/policies/hook 已全載入、context 最完整；額外開一個 specialist 反而是降級版的自己（少方法論、少 hook 護欄）。97 則 bridge facts 的價值在於主 agent 自己用（preamble 已注入 topic shards），不是分給另一個 instance。使用者確認跳過。

## 相關

- [[bridge-specialist]] — Specialist 配置與判斷邏輯完整脈絡
- [[bridge-project]] — 主 agent 與 specialist 的 context 完整度對比
