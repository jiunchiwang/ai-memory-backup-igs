---
title: UK Slot 老虎機專案群
type: concept
created: 2026-06-02
updated: 2026-06-04
sources: [f_093bcf, f_79c118, f_967ccc, f_e8b2cf, f_991386, f_cea694, f_3f7536, f_r0b1nh, f_wr4th9, f_f4rw3s, f_3y3s2k, f_ch4ch4]
---

# UK Slot 老虎機專案群

## 概述

使用者開發一系列面向 UK 市場的老虎機遊戲，基於 Cocos Creator 3.6.2 + Astarte Framework + TypeScript 技術棧。所有遊戲從共用模板 fork 而來，目前共 8 個專案（1 模板 + 7 遊戲）。

## 技術棧約束

- **Astarte Framework 不可改動** — 所有專案共用的底層框架，禁止修改
- 方法（method/function）命名使用**大駝峰（PascalCase）**

## 專案清單

### uk_slot_template（模板）

- 位置：`G:\Cocos_Project\uk_slot_template`
- 性質：所有 UK slot 遊戲的 fork 來源
- 支援三種轉輪玩法，透過 FillStrategy 策略模式切換：
  - **Standard** — 傳統滾動
  - **Cascade** — 消除天降
  - **Tumble** — 快速掉落 + 乘倍

### 衍生遊戲

| 專案 | 路徑 | 主題 |
|------|------|------|
| uk_pirates_queen | `G:\Cocos_Project\uk_pirates_queen` | 海盜女王（6×5，消除連鎖+懸賞令+輪盤選獎） |
| uk_722_robinhood_client | `G:\Cocos_Project\uk_722_robinhood_client` | Robin Hood 羅賓漢 |
| uk_739_wrath_of_thunder_client | `G:\Cocos_Project\uk_739_wrath_of_thunder_client` | Wrath of Thunder 雷神 |
| uk_746_far_west_client | `G:\Cocos_Project\uk_746_far_west_client` | Far West 西部 |
| uk_slot_eye_strike | `G:\Cocos_Project\uk_slot_eye_strike` | Eye Strike 神眼奪金 |
| uk_872_eyestrike2_client | `G:\Cocos_Project\uk_872_eyestrike2_client` | Eye Strike 2（續作） |
| uk_slot_chachacha | `G:\Cocos_Project\uk_slot_chachacha` | Cha Cha Cha 拉丁舞/水果 |

## 待優化項目

- uk_slot_eye_strike：`MultiplierManager.m_downEffectSpine` 的 Idle 動畫實際靜止，可優化為靜態圖 + 隱藏 Spine 省效能

## 相關

- [[bridge-project]]（開發工具鏈的一部分）
