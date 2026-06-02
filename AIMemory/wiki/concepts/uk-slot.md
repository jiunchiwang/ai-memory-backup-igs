---
title: UK Slot 老虎機專案群
type: concept
created: 2026-06-02
updated: 2026-06-02
sources: [f_093bcf, f_79c118, f_967ccc, f_e8b2cf, f_991386]
---

# UK Slot 老虎機專案群

## 概述

使用者開發一系列面向 UK 市場的老虎機遊戲，基於 Cocos Creator 3.6.2 + Astarte Framework + TypeScript 技術棧。所有遊戲從共用模板 fork 而來。

## 專案結構

### uk_slot_template（模板）

- 位置：`G:\Cocos_Project\uk_slot_template`
- 性質：所有 UK slot 遊戲的 fork 來源
- 支援三種轉輪玩法，透過 FillStrategy 策略模式切換：
  - **Standard** — 傳統滾動
  - **Cascade** — 消除天降
  - **Tumble** — 快速掉落 + 乘倍

### uk_pirates_queen（海盜女王）

- 位置：`G:\Cocos_Project\uk_pirates_queen`
- 主題：海盜女王
- 盤面：6 列 × 5 行
- 機制：消除連鎖、懸賞令倍率、Free Game、輪盤選獎

## 團隊規範

- 方法（method/function）命名使用**大駝峰（PascalCase）**

## 相關

- [[bridge-project]]（開發工具鏈的一部分）
