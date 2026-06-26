---
type: skill
domain: slot
created: 2026-06-25
tags: [pattern-library, route-c, translation-layer]
source: session
---

# uk-slot-pattern-library

UK 老虎機衍生模式庫。路線 C 翻譯層的 grounding：當 AI 拿到一份遊戲規格書，需要把 Feature 映射到程式實作時，比對此庫中的模式卡片。

## 觸發條件

- 從規格書翻譯 Feature 為程式映射時
- 新遊戲需要辨識「用到哪些已知模式」時
- 設計新 State / Manager 前，查看是否有現成參考

## 使用方式

1. 讀取 `patterns/` 下的模式卡片，找到最接近的已知模式
2. 標出規格與參考的差異點
3. 根據卡片的「程式映射」產出實作骨架

## 頻率定義

| 等級 | 條件 | 意義 |
|------|------|------|
| **高** | ≥3 個專案實際使用 | 幾乎每款都會碰到，優先熟讀 |
| **中** | 1–2 個專案使用 | 常見但非必備，遇到時查閱 |
| **低** | 僅規格出現、尚無實作 | 新設計，可信度較低 |
| **基礎** | 框架內建、每專案必有 | 骨架知識 |

## 模式卡片索引

| # | 模式 | 檔案 | 參考專案 | 頻率 | 驗證 |
|---|------|------|---------|------|------|
| 1 | Collect Feature | patterns/collect-feature.md | eye_strike, wrath_of_thunder, 3LP | 高 | ✅ |
| 2 | Scatter 蒐集觸發 | patterns/scatter-collect.md | eye_strike (MagicPot), 3LP | 高 | ✅ |
| 3 | 盤面擴展 (Expand) | patterns/expand-reel.md | wrath_of_thunder | 中 | ✅ |
| 4 | Multiplier 格子 | patterns/multiplier-grid.md | eye_strike | 中 | ✅ |
| 5 | Bomb 爆炸 | patterns/bomb-feature.md | chachacha, eye_strike | 中 | ✅ |
| 6 | BonusGame Pick | patterns/bonus-game-pick.md | 722 robinhood, 746 far_west | 高 | ✅ |
| 7 | Respin | patterns/respin.md | eye_strike, 746 far_west, 3LP | 高 | ✅ |
| 8 | NearMiss 聽牌 | patterns/near-miss.md | eye_strike, 3LP | 高 | ✅ |
| 9 | FakeReelManager | patterns/fake-reel-manager.md | eye_strike, 722, 746 | 高 | ✅ |
| 10 | ExtraBet | patterns/extra-bet.md | eye_strike | 中 | ✅ |
| 11 | Buy Bonus | patterns/buy-bonus.md | 框架 CommonBuyBonus, 722, tct, 3LP | 高 | ✅ |
| 12 | Wild 變身 | patterns/wild-transform.md | 722 robinhood, 746 far_west | 中 | ✅ |
| 13 | Mystery 符號 | patterns/mystery-symbol.md | eye_strike, 746 far_west, wrath_of_thunder | 高 | ✅ |
| 14 | COLLECT 神秘事件 | patterns/collect-mystery.md | 3LP | 中 | ✅ |
| 15 | Feature Wheel | patterns/feature-wheel.md | Eye Strike2 | 低 | ⚠️ |
| 16 | Symbol Transform | patterns/symbol-transform.md | Eye Strike2 | 低 | ⚠️ |
| 17 | Persistent Grid Effect | patterns/persistent-grid-effect.md | Eye Strike2 | 低 | ⚠️ |
| 18 | VS Feature（對決乘倍） | patterns/vs-feature.md | Clash of Olympus | 低 | ⚠️ |
| 19 | MAX WIN（最大獎上限） | patterns/max-win.md | Clash of Olympus | 低 | ⚠️ |
| 20 | Progression Unlock（進度解鎖/地圖） | patterns/progression-unlock.md | Wrath of Thunder v2 | 低 | ⚠️ |
| 21 | Global Multiplier（全局/Wild 乘倍） | patterns/global-multiplier.md | Wrath of Thunder v2 | 低 | ⚠️ |
| 22 | Template 骨架 | template/state-machine.md | uk_slot_template | 基礎 | ✅ |

> **驗證欄說明**：✅ = 有實際專案程式碼佐證；⚠️ = 僅從規格書推導，尚未經過實作驗證

## 模式卡片格式規範

每張卡片統一結構：
```
# Pattern: <名稱>
## 識別條件（規格書出現什麼關鍵字/描述時匹配此模式）
## 參考實作（哪個專案、哪些檔案）
## State 映射（需不需要新 State、走哪個現有 State）
## Data 需求（proto 結構假設）
## 演出時序（程式視角的 step-by-step，標註 await/即時）
## 常見變體（已知的不同實作方式）
## 邊界案例（容易漏的規則）
```
