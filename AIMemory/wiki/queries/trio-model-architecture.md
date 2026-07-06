---
title: 三模型協作架構評析（Fable 5 + Codex 5.5 + Gemini 3.1 Pro）
type: query
created: 2026-07-06
updated: 2026-07-06
sources: []
---

# 三模型協作架構評析

2026-07-05 使用者分享一張「Fable 5 Orchestrator + Codex 5.5 Executor + Gemini 3.1 Pro Reviewer」三模型協作架構宣傳圖，討論其優缺點與對 [[bridge-project]] 的借鏡價值。

## 架構主張

- **Fable 5**（Orchestrator，10% token）：任務切割、驗收標準、仲裁決策
- **Codex 5.5**（Executor，60% token）：`/goal` 長模式實作
- **Gemini 3.1 Pro**（Reviewer，15% token）：異質角度審核、高 Recall、不做最終決策
- 工作流：定義任務 → 執行實作 → 異質審核 → 仲裁 → 驗收送代收斂

## 值得借鏡

1. **異質模型互審**——同家族模型自我 review 有 self-bias；bridge 的 specialist 全用 Claude 家族，認知偏差可能重疊
2. **Orchestrator 極簡化**——昂貴模型限縮在切工單 + 驗收，幾乎不碰實作 context
3. **送代收斂有明確退出條件**——bridge 的 goal system 由 agent 自判 GOAL_DONE，缺獨立第三方驗證

## 疑點

1. 宣稱數字（92% 完成率、Bug -82%、省 65% token）**無基準線定義、不可重現**，宣傳性質重
2. 三模型 round-trip 的協調成本在小任務上得不償失
3. 「總省 65%」的比較基準不明（跟全 Opus 比當然省）
4. 缺錯誤恢復機制（reviewer 意見矛盾怎辦、工單切錯怎麼回溯）——bridge 的 reflexion + retry + working-state 才是實戰需要的

## 與 Bridge 的差異

| 面向 | 圖中架構 | Bridge |
|---|---|---|
| 異質互審 | ✅ | ❌ 同家族自審 |
| 記憶/學習 | ❌ | ✅ facts + wiki + archive |
| 錯誤恢復 | ❌ | ✅ reflexion + retry |
| 使用者參與 | 最後驗收 | 每步可 ASK 介入 |

## 若只借一個概念

Specialist 完成後加**異質 reviewer quick sanity check**（用 Gemini Flash 問 3 個 yes/no：遺漏需求？邏輯矛盾？架構衝突？），成本低、能抓部分 self-bias。（討論後未採行，記錄備考）

## 相關

- [[bridge-acp]] — 非 Claude model 清單與能力判斷（後續 benchmark 的起點）
