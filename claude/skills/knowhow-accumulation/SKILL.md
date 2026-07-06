---
name: knowhow-accumulation
description: Use when capturing lessons from AI failures into structured ❌→✅ records, when reviewing past interactions to extract reusable patterns, or when building a self-improving knowledge base from repeated mistakes
---

# KnowHow Accumulation

## Overview

把每次 AI 出包或使用者不滿意的結果，結構化記錄成 ❌→✅ 配對，累積成可被 AI 自動遵守的教訓庫。本質是 Strategic Memory：情境 → 方法 → 結果 → 原因 → 建議。

## When to Use

- AI 產出不符預期，需要記錄避免再犯
- 跑完一輪任務後要萃取教訓
- 定期 review 對話歷史，提煉可重用模式
- 建立新 Skill 時需要初始 KnowHow

## 硬性格式

```
❌ [具體錯誤做法] → ✅ [具體正確做法]
```

**規則**：
- 不寫「應該避免 X」「建議要 Y」這種抽象建議
- 必須是「具體錯誤動作 → 具體正確動作」的配對
- 每條要可被檢查（AI 寫完能掃一遍確認有沒有違反）

## 累積流程

```
用 AI 做一件事 → 出來結果
    ↓
你 review → 發現「不對，這裡又犯一樣的錯」
    ↓
把「犯的錯」+「該怎麼做」變成一條 ❌→✅
    ↓
加進 Instructions / facts / Skill 的 KnowHow 區塊
    ↓
下次再做同件事，AI 自動避開
```

## 收斂判斷

| 輪次 | 狀態 |
|------|------|
| 第 1 輪 | 「還要改一堆」 |
| 第 2-3 輪 | 「只要改 1-2 個地方」 |
| 第 4-5 輪 | 「幾乎可以直接用」 |
| 第 6-7 輪 | 「比我自己寫還順」 |
| 第 8+ 輪 | 收斂——3 次沒新 KnowHow 可記就停 |

## 批次萃取提詞

對話結束後用這段萃取：

```
請整理我跟你過去 [N] 次對話中，
所有「我修正過」的地方，
彙整成 KnowHow 清單：

❌ 你的舊作法 → ✅ 我修正後的作法
```

## 品質標準

好的 KnowHow：
- ✅ 可被檢查（AI 能掃描自己有沒有違反）
- ✅ 可被搬移（寄給別人也能用）
- ✅ 可被累積（每多踩一個雷 = 多一條）
- ✅ 有具體場景（不是泛泛而談）

壞的 KnowHow：
- ❌ 「注意品質」（太抽象）
- ❌ 「要寫好一點」（沒有具體動作）
- ❌ 「參考最佳實踐」（哪個最佳實踐？）

## 維護週期

| 週期 | 動作 |
|------|------|
| 每次出包 | 補一條 ❌→✅ |
| 月度 | 檢視是否有重複/矛盾的條目 |
| 季度 | 合併相似條目、刪除過時的 |
| 年度 | 全面 review，考慮是否升格為 Skill |

## 與 bridge 系統的對應

| 文件概念 | bridge 對應 |
|---------|------------|
| KnowHow 區塊 | `facts-*.md` + topic shards |
| 累積動作 | `remember()` MCP tool |
| 批次萃取 | `/save` 觸發 agent 抽事實 |
| 升格為 Skill | `/MemoryToSkill` |
| 定期整理 | `/factlint` + `/topicreview` |
