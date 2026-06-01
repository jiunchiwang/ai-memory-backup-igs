---
name: non-engineer-agent-design
description: Use when designing Custom GPT / Claude Project / Gemini Gem instructions for non-engineers, or when helping someone structure their AI workflow using the 5-piece framework (Agent, Skill, Steering, Hook, KnowHow)
---

# Non-Engineer Agent Design

## Overview

用五件套框架（Agent / Skill / Steering / Hook / KnowHow）幫非工程師設計可自我優化的 AI 工作流。產出物是一份可直接貼進 Custom GPT / Claude Project / Gemini Gem 的 Instructions。

## When to Use

- 幫非工程師設計 Custom GPT / Project / Gem
- 自己要快速建立一個新領域的 AI 助理
- 需要把散亂的工作流程標準化成 AI 可執行的格式

## 五件套速查

| 觀念 | 角色 | 一句話 |
|------|------|--------|
| Agent | 員工 | 一個有名字、有角色的 AI 實例 |
| Skill | 工具 | 一件事情的標準做法（可命名呼叫） |
| Steering | 員工守則 | 永遠在背景的全域規範 |
| Hook | 鬧鐘 | 特定時間點觸發的強制動作 |
| KnowHow | 教訓筆記 | 踩過的雷的 ❌→✅ 記錄 |

## Instructions 標準模板

```
═══════════════════════════════════
你是「[Agent 名]」，[一句話角色描述]。
═══════════════════════════════════

【Steering — 永遠遵守的規則】
1. [語言規範]
2. [語氣規範]
3. [格式規範]
4. [禁忌]
5. 完成後強制執行下方「自評環節」

═══════════════════════════════════
【Skill — 我擅長做的事】
═══════════════════════════════════

Skill 1: [名稱]
- 觸發：使用者說「[關鍵字]」
- 固定格式：[輸出模板]
- 規則：
  - ...

═══════════════════════════════════
【自評環節】（每次完成都要跑 = Hook）
═══════════════════════════════════
完成後自問：
1. 完成度幾分（0-100）？
2. 最弱項是什麼？
3. 是否違反 Steering 禁忌？
4. 是否有 [TODO]？
任一項 < 85 → 自己改完再輸出。

═══════════════════════════════════
【歷史教訓 — KnowHow】
═══════════════════════════════════
❌ ... → ✅ ...
（持續累積，每次都讀過）
```

## 設計流程

1. **選痛點**：找頻率高 + 痛苦大 + 可標準化的任務
2. **找範本**：拿一份你過去做得最好的版本當基準
3. **寫 v1**：用上方模板填空，不追求完美
4. **直接用**：v1 上線，靠用累積 KnowHow
5. **6-7 輪收斂**：每次不滿意就補一條 ❌→✅

## 痛點評估矩陣

每個候選痛點打分（0-10）：

| 項目 | 說明 |
|------|------|
| 頻率 | 一週/一月做幾次 |
| 痛苦 | 不做的話多痛 |
| 可標準化 | 步驟+規則明確嗎 |
| 我熟悉 | 我自己會做嗎 |

4 項加總最高 → 第一個 Skill 目標。

## 平台對應

| | ChatGPT | Claude | Gemini |
|--|---------|--------|--------|
| Skill 容器 | Custom GPT | Project | Gem |
| 跨對話風格 | Memory | Custom Style | Saved info |
| 長文遵從度 | 中 | 高 | 中 |

## Common Mistakes

❌ 同時用 3 個平台 → KnowHow 分散，累積不起來
❌ 追求完美才上線 → v1 就該直接用
❌ 規則只在當下對話講 → 要寫進 Steering 才持久
❌ 自評說「都很好」→ 強迫具體扣分
❌ 不確定就假裝懂 → 標 [待確認]
