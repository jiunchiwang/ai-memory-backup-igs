---
title: Clash of Olympus（諸神之戰）
type: concept
created: 2026-07-16
updated: 2026-08-12（大幅更正：舊路徑/舊機制清單/舊待確認 8 項已過時，改寫為 codegen 交付後的實況）
sources: [f_4c48e6, f_f79167, f_b20c5e, f_593c2e, f_c7ce92, f_385d4d, f_90d6e8]
---

# Clash of Olympus（諸神之戰）

## ⚠️ 本頁曾長期過時（2026-07-17 → 2026-08-12 才修正）

舊版寫「位於 `clash_of_olympus_demo`」「6×4 4096 Ways」「VS Feature 🔴 + 待確認 8 項」——這是
**2026-07 那批 spec-to-impl 產出**的記錄。2026-08-12 查證時該路徑**已實查不存在**，專案已改走
uk-slot-codegen 全新產出，機制清單與待確認事項也已改變。舊 facts（f_4c48e6/f_f79167/f_593c2e）
因受本頁 `sources` 保護，factlint 無法刪除，仍列在 sources 供歷史追溯，但**內容以下文為準**。

## 概述

希臘神話主題 UK 老虎機，基於 [[uk-slot-template]] + Astarte Framework。**現行專案路徑**
`G:\Cocos_Project\uk_slot_clash_of_olympus`（GameId 未分配，分配後改名 `uk_<id>_..._client`）。
規格書 `G:\UK\Clash of Olympus.xlsx`（2026-08-07 更新，舊路徑 `G:\AI\Clash of Olympus.xlsx` 已搬遷）。
最近似參考仍是 tripleCoinTreasure-client（三幣瑞龍，GameId=399）。

盤面：**ROW=4 / COL=6，4096 Ways**（19 顆符號 symbol00~18，`SCATTER_SYMBOL` 只有 symbol12——
Cash/CollectVS 等皆為 feature symbol 不是 scatter）。

## 開發進度

- **2026-07**：spec-to-impl 三步驟產出（`clash_of_olympus_demo`）——**已確認此路徑不存在**，只能當歷史參考
- **2026-08-12 M0a（codegen）已完成交付**：`uk-slot-codegen` 全流程（`mode=new`、proto stub、template 遠端 clone HEAD=`527de9b2`），finalize gate 38/38、tsc 專案 diagnostics 0
- **2026-08-12 git repo 已建立**：分支 `main`、889 檔、`.gitignore` 比照 uk_917 慣例（AI 相關目錄與 `docs/` 不進版控）、**未設 remote**（待 GameId 分配）
- **2026-08-12 M0b（Editor/Runtime 驗證）進行中**：Preview 起得來、19 份 SymbolEffect 的
  SkeletonData 綁定正常；但發現並修復一個真 bug——`RecoverSpinAck.TraverseAwardData()` 漏複製
  `EliminatePos` 欄位，proto stub 預設回退 `emptyArray`，導致中獎 Spine 演出完全不播且無任何錯誤
  訊息（已修一行、`verify_compile.py` 5/5 PASS，待使用者重測確認）

## 機制分類（2026-08-12 codegen 驗證版）

| 難度 | 機制 | 說明 |
|------|------|------|
| 🔴 新開發 | VS Feature | Cash 乘倍 + Collect 乘倍 + 多 VS 作用順序，本作最重機制 |
| 🟡 適配 | Collect Feature | 模板已有 Collect/Cash/CoinState 骨架 |
| 🟡 適配 | 聚寶盆 | 3+1 階狀態機，pattern-library 有驗證變體 |
| — | 其他 | FG、JP 五階、BuyBonus、MAX WIN、預中、聽牌 |

## 待確認事項（9 項，2026-08-12 codegen 重新枚舉，非舊版 8 項）

1. 賠率表全空需機率文件
2. BuyBonus 售價未定
3. FG 手數未明
4. VS 乘倍數值 + 2X vs X2 語意
5. 聚寶盆機率
6. ExtraBet 規格
7. Proto 發佈時間
8. GameId 待分配
9. **新發現**：道具卡（`道具卡 = True`）但三張流程表零規格；sheet 7 音樂音效與 sheet 8
   多國語言皆為零儲存格空白——音效清單只能推定，i18n 延到 M2+

## spec-to-impl 教訓（仍成立）

- Agent 拿到規格書後必須先 invoke skill 從步驟 0 開始
- 基準永遠是 [[uk-slot-template]] 不是衍生品
- 步驟 2 必須讀 pattern-library 索引否則會重複設計已驗證模式

## Cocos prefab 踩坑（2026-08-12 M0b 實證）

`MainGame.prefab` 的元件欄位值顯示 `None` **不代表未綁定**——跨 nested prefab 的參照存在
`PrefabInfo.targetOverrides`，查欄位值會誤判。判斷是否真的接線要 grep 該 prefab 的
`cc.TargetOverrideInfo` 條目，不能只看欄位值。

## 相關

- [[uk-slot]] — UK 老虎機專案群
- [[uk-slot-template]] — 模板專案
- [[uk-slot-codegen]] — 本作 M0a 使用的 codegen 工具
- [[codegen-git-init-gap]] — codegen 流程 git 初始化缺口的修復（本作是首個實測案例）
- [[uk-slot-pitfalls]] — 踩坑經驗
