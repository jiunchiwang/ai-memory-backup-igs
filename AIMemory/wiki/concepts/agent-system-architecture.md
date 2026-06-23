---
title: Agent 系統五層架構
type: concept
created: 2026-06-11
updated: 2026-06-11
sources: []
---

# Agent System Architecture — 五層公司比喻

> 來源：社群圖解「MCP、Agent SDK、Memory、Workflow 到底是什麼關係？」

## 核心比喻

把 Agent 系統想成一家公司，五個元件各自扮演不同角色：

| 比喻 | 元件 | 職責 | 回答的問題 |
|------|------|------|-----------|
| 員工 | Agent | 實際執行任務、分析、判斷、產出結果 | 誰來做？ |
| 工具櫃 | MCP | 標準化接口，讓 Agent 連接外部工具與服務 | AI 能使用哪些工具？ |
| 知識庫 | Memory | 累積經驗、偏好、歷史，形成判斷依據 | AI 記得什麼？ |
| SOP 流程 | Workflow | 定義步驟、順序、規則、交接與例外處理 | 工作怎麼進行？ |
| 管理制度 | Agent SDK | 任務分派、協調、狀態追蹤、錯誤處理、權限控管 | 如何讓整個團隊運作？ |

## 架構分層（由上而下）

1. **使用者/目標** — 提出需求，設定目標
2. **Agent SDK（管理層）** — 任務分派、協調調度、狀態追蹤、錯誤處理、權限控管
3. **Workflow（流程層）** — 步驟 1 → 步驟 2 → … → 步驟 N
4. **Agent 團隊（執行層）** — 策略分析 Agent、文案撰寫 Agent、設計生成 Agent、資料分析 Agent、審核檢查 Agent…
5. **Memory（知識層）** + **MCP（工具層）** — 底層支撐
6. **外部世界/真實環境** — 網路、資料來源、第三方服務、使用者互動

## 關鍵重點

- MCP 讓 AI 能「使用工具」，但不決定怎麼工作
- Memory 讓 AI 能「累積經驗」，形成判斷與個人化能力
- Workflow 讓 AI 知道「步驟與規則」，確保工作有條不紊
- Agent SDK 讓整個團隊「協同運作」，處理複雜任務與例外狀況
- Agent 是「真正執行任務」的數位員工

## 總結公式

有工具（MCP）→ 有記憶（Memory）→ 有流程（Workflow）→ 有管理（Agent SDK）→ 有人做事（Agent）= **有成果的 AI 組織**

五層並不是競爭關係，而是相互依存。

## 對應到 telegram-kiro-bridge

| 層級 | 實作 |
|------|------|
| Agent | Kiro CLI / Codex / Claude（透過 ACP 接入） |
| MCP | 內建 memory MCP + NotebookLM + cocos362 等外掛 |
| Memory | facts / topics / wiki / hit-log 長期記憶系統 |
| Workflow | /dream pipeline、/goal 多 turn 執行、specialist delegation |
| Agent SDK | bridge 本身（session 管理、specialist 分派、relay 協調、錯誤重試、reflexion） |
