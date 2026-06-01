---
name: dual-skill-review-loop
description: Use when producing any deliverable that needs quality assurance — writing, reports, proposals, code designs — and you want the output to reach ≥95 score through structured self-review iterations
---

# Dual-Skill Review Loop

## Overview

把「做」和「檢查」拆成兩個獨立角色（Generator + QA），用不同視角迭代直到品質收斂。核心原理：同一顆腦袋同時做+審會自我偏袒，拆開後 QA 會真的挑毛病。

## When to Use

- 對外輸出物（給客戶、給主管、要公開的）
- 重要文件（合約、提案、報告）
- 高頻使用的範本
- 你還沒摸清楚 AI 盲點的新任務

## When NOT to Use

- 簡單問答、一次性不重要任務
- 探索性對話（還沒想好要什麼）
- 已經很熟的任務（自評反而拖慢）

## Core Pattern

### 兩個角色定義

**Generator（生成者）**
- 目標：產出最好的版本
- 大膽創造，不保守
- 不夠好的部分標 `[TODO]`，不假裝完成

**QA（檢查者）**
- 目標：找問題（≥5 個才算合格）
- 像最挑剔的主管/客戶
- 禁止說「整體不錯」「很好」
- 每個問題必須有：具體位置 + 為什麼是問題 + 改善方向
- 用 0-100 打分，扣的每一分都要說明

### 執行流程

```
Generator 產出 v1
    ↓
QA 找 ≥5 問題，打分
    ↓
分數 < 95？→ Generator 根據回饋修正
    ↓
QA 再評 → 重複直到 ≥95
```

### 每輪報告格式

```
【第 N 輪】
#### Generator 輸出
[內容]

#### QA 回饋
- 問題 1：[具體位置] + [為什麼] + [建議]
- 問題 2：...
分數：__/100

#### Generator 反省
- 為什麼犯錯：...
- 根本原因：...

#### 修正版本
[內容]
```

## 簡化版（省 token）

單輪自評，不跑多輪：

```
完成後請：
1. 列 3 個優點
2. 列 5 個還可以更好的地方
3. 直接改最重要的 1 個
4. 給最終版
```

約多用 30% token，拿到 70% 完整版效果。

## 收斂判斷

- 通常 3-7 輪收斂
- 超過 10 輪 = 浪費，該停了
- QA 只挑得出 Nice-to-Have = 收斂

## Common Mistakes

❌ QA 說「整體很好」→ 等於沒檢查
❌ Generator 不寫反省直接改 → 會重複犯錯
❌ 不設分數門檻 → 永遠「差不多就好」
❌ 跑太多輪（>10）→ 邊際效益趨零
