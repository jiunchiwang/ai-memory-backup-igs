---
title: Eye Strike 系列
type: concept
created: 2026-07-16
updated: 2026-07-17
sources: [f_cea694, f_3y3s2k, f_9322f0, f_82c757, f_0b3520, f_800551]
---

# Eye Strike 系列

## 概述

UK 市場的眼睛打擊主題老虎機系列，含第一代 Eye Strike（uk_slot_eye_strike）和續作 Eye Strike 2（uk_872_eyestrike2_client），皆位於 `G:\Cocos_Project\`。

## 第一代 — uk_slot_eye_strike

| 欄位 | 值 |
|------|------|
| GameId | 658 |
| ShortGameName | ar2es |
| 盤面 | 6 列不等高（5-4-4-4-4-5）共 26 格 |
| Proto | @igs-arcade-division-rd2/uk_658_eyestrike_proto |

### 專案特有機制（7 個）

1. **MagicPot** — 能量收集（4 階）
2. **Multiplier** — 乘倍輪盤
3. **GoldBlitzRoulette** — FG 內輪盤
4. **FakeReelManager** — 4 種投注模式
5. **NearMiss** — 聽牌
6. **ReelSymbolMode** — 4 種顯示模式
7. **Mystery** — 神秘符號

### 待優化

- `MultiplierManager.m_downEffectSpine` 的 Idle 動畫是靜止的，可改用靜態圖 + 隱藏 Spine 省效能

## 第二代 — uk_872_eyestrike2_client

- 架構規範：Spine 動畫一律透過 **SpineKit** 播放（統一的 Spine 播放架構），不直接操作底層 spine 元件

## 與模板的關係

[[uk-slot-template]] 的 demo 流程綁 eyestrike（uk_658）proto 與 dev server（6 欄盤面），衍生遊戲改 COL 後連該 server 必然欄數不符。轉輪驗證應走 ReelDevTool 假盤，端到端等各自真 proto。

## 相關

- [[uk-slot]] — UK 老虎機專案群
- [[uk-slot-template]] — 模板專案
