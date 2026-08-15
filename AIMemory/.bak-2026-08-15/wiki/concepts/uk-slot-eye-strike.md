---
title: Eye Strike 系列
type: concept
created: 2026-07-16
updated: 2026-08-08
sources: [f_cea694, f_3y3s2k, f_9322f0, f_82c757, f_0b3520, f_800551, f_564bea, f_b9aeb7, f_391f10, f_73dbc7, f_6c587f, f_8ad906]
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

### 轉輪燈光壓暗設計決策（2026-07-30）

逐側判斷門檻下沉到 `ReelUIManager.SetReelLightDark()`（方案 A），只在 `dark===true` 時檢查 `m_reelLightStates`、該側沒亮就不壓；還原路徑刻意不設此門檻，否則熄燈後燈光永遠回不到亮色。

- 轉輪兩側燈光（第1輪 LEFT / 第6輪 RIGHT）只在該輪落到 Collect 符號時才亮（`SlotReels.ts:694/734`）
- `ReelUIManager` 的壓暗（`DARK_LIGHT_REEL`，RGB 120）與熄燈（`HIDE_LIGHT_*_REEL`，收掉 spine）是兩套獨立狀態機制
- `m_reelLightStates` 與 `m_reelLightDarkStates` 分開記錄

### FeatureWheelShowState 燈光分工

壓暗由使用者實作（掛在 spotlight 那批 `SetAllSymbolsDark(true)` 同一拍），`RESTORE_LIGHT_REEL` 的還原時機與實作由同事決定處理。

### Collect 收分執行點

⚠️ Collect 收分有**三個執行點**且橫跨多個 State：

| 執行點 | 位置 | 時機 |
|--------|------|------|
| 一般手 | `ScatterShowState.ts:124` | `FEATURE_WHEEL_SHOW` 之前 |
| ⑧收分演出 | `FeatureResultShowState.ts:62` | — |
| ⑤收分飛行 | `FeatureResultShowState.ts:252` | — |

談「收分之後」的時機時必須先釐清是哪一個，否則會做出時序不可能的需求。

### 停輪節奏設計決策（2026-08-06）

每一輪停下後會先短暫停頓，才讓下一輪開始停輪，目的是為**特殊符號的進場演出**留出播放時間。這個節奏是刻意設計的，不是效能問題。

### tsc 驗證注意

Cocos Creator 專案在編輯器外跑 `tsc --noEmit` 會產出大量來自引擎 `cc.d.ts` 與 astarte framework 宣告的既有錯誤（uk_872 實測 509 行）。驗證自己的改動時應過濾只看 `assets/Script` 底下的錯誤，不能用總錯誤數當通過標準。

## 與模板的關係

[[uk-slot-template]] 的 demo 流程綁 eyestrike（uk_658）proto 與 dev server（6 欄盤面），衍生遊戲改 COL 後連該 server 必然欄數不符。轉輪驗證應走 ReelDevTool 假盤，端到端等各自真 proto。

## 相關

- [[uk-slot]] — UK 老虎機專案群
- [[uk-slot-template]] — 模板專案
