---
title: Clash of Olympus（諸神之戰）
type: concept
created: 2026-07-16
updated: 2026-07-17
sources: [f_4c48e6, f_d03f34, f_f79167, f_b20c5e, f_593c2e, f_c7ce92]
---

# Clash of Olympus（諸神之戰）

## 概述

希臘神話主題 UK 老虎機，6×4 盤面 4096 Ways，基於 [[uk-slot-template]] + Astarte Framework。位於 `G:\Cocos_Project\clash_of_olympus_demo`，規格書 `G:\AI\Clash of Olympus.xlsx`。最近似參考為 tripleCoinTreasure-client（三幣瑞龍，GameId=399）。

## 開發進度

spec-to-impl 三步驟已於 2026-07-09 完成：
- `docs/spec/`（80 張圖）
- `dev-spec.md`（1🔴 + 6🟡 + 8🟢）
- `SPEC.md`（25 任務 M0a~M4）
- `AI.md`

**下一步**：M0a 起專案，待確認 GameId 和 Proto 狀態。

## 機制分類

| 難度 | 機制 | 說明 |
|------|------|------|
| 🔴 新開發 | VS Feature | Cash 乘倍 + Collect 乘倍 + 多 VS 作用順序 |
| 🟡 適配 | Collect Feature | 模板已有 Collect/Cash/CoinState 骨架 |
| 🟡 適配 | 聚寶盆 | pattern-library 有驗證變體 |

## 待確認事項（8 項）

1. 賠率表全空需機率文件
2. BuyBonus 售價未定
3. FG 手數未明
4. VS 乘倍數值 + 2X vs X2 語意
5. 聚寶盆機率
6. ExtraBet 規格
7. Proto 發佈時間
8. GameId 待分配

## spec-to-impl 教訓

- Agent 拿到規格書後必須先 invoke skill 從步驟 0 開始
- 基準永遠是 [[uk-slot-template]] 不是衍生品
- 步驟 2 必須讀 pattern-library 索引否則會重複設計已驗證模式

## 相關

- [[uk-slot]] — UK 老虎機專案群
- [[uk-slot-template]] — 模板專案
- [[uk-slot-pitfalls]] — 踩坑經驗
