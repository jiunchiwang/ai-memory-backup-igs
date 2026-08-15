---
title: Eye Strike 系列
type: concept
created: 2026-07-16
updated: 2026-08-16（wikilint：補 4 條漏同步 fact——轉輪 click 音效節奏提案、停輪曲線量化分析、baked path 動畫限制、CLAUDE.local.md 覆蓋技巧）
sources: [f_cea694, f_937a50, f_9322f0, f_82c757, f_0b3520, f_800551, f_564bea, f_b9aeb7, f_391f10, f_73dbc7, f_6c587f, f_8ad906, f_4f973f, f_bbcecf, f_479ac3, f_e12b2f]
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

### 轉輪 click 音效節奏提案（2026-08-09，狀態：編導評估中）

針對續作 uk_872 的轉輪 click 音效節奏，做了一支獨立 HTML 原型（`uk_872_eyestrike2_client\.claude_temp\wheel-click-prototype.html`，遊戲碼未動）：內含現況版原封移植的 `CalcSpeedCurve` 三段曲線，與停輪懸念三分支可背靠背 A/B。關鍵量測：現況到 Collect 亮起 **5.55 秒**（死時間 2.15 秒 = 慢爬 0.85 + hold 0.3 + settle 0.25 + 空窗 0.75，⚠️ settle 是從 `ROTATE_TIME` 內扣不是外加）對比新版 A 分支 **3.92 秒**、峰值 447°/s。使用者拿去給編導評估，待回饋才決定調整／寫設計文件／接進遊戲。

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

### 停輪曲線量化分析（2026-08-06，A 級：與 `FeatureWheelManager.ts:216-258` 七個 readonly 逐一比對相符）

移植常數量化後算出：**主曲線時間走到 85% 時，角度已經跑完 99.5%**——最後 15% 的時間只走 0.5% 的角度，這正是「轉輪看起來早就停了但燈還沒亮」的成因，元凶是 `SPEED_CURVE_SLOW_SPEED_RATIO=0.01`；把它拖到 20% 時同一時點是 92.8%。調參用同一份 `wheel-click-prototype.html`（v2 起現況版九格常數全開成滑桿、預設＝專案現值、附「回到專案現值」鈕）。

### MagicPotFlyToCenterTrail 是 baked path 動畫

`MagicPotFlyToCenterTrail.prefab` 兩支動畫（`ES2_FGBoard_In_H`、`ES2_FGBoard_In_S`）的飛行路徑是烘進動畫裡的（baked path），完全不靠骨骼定位——要改飛行起訖點或落點，調整骨骼與節點座標不會有效果。

### 專案級規則覆蓋技巧

要讓單一專案不受專案級 `CLAUDE.md` 某條指示約束（例如「改完自動 git commit」），做法是在專案根建 `CLAUDE.local.md` 寫下反向指示壓過它，而不是去改共用的 `CLAUDE.md`（2026-08-11 於 uk_872_eyestrike2_client 用此法停掉自動 commit）。

## 與模板的關係

[[uk-slot-template]] 的 demo 流程綁 eyestrike（uk_658）proto 與 dev server（6 欄盤面），衍生遊戲改 COL 後連該 server 必然欄數不符。轉輪驗證應走 ReelDevTool 假盤，端到端等各自真 proto。

## 相關

- [[uk-slot]] — UK 老虎機專案群
- [[uk-slot-template]] — 模板專案
