---
title: Clash of Olympus（諸神之戰）
type: concept
created: 2026-07-16
updated: 2026-08-13（VS Feature 規則與編導多輪確認定案：符號 id 更正、觸發兩層閘門、VS Collect 改收分時乘倍相加非連乘；M2.1/M2.2 進度）
sources: [f_4c48e6, f_f79167, f_b20c5e, f_593c2e, f_c7ce92, f_385d4d, f_90d6e8, f_5927a3, f_6587d2, f_ab095f, f_baad41, f_2675c6, f_cf423c, f_e0a15e, f_9b909e, f_05937b, f_f8bf81]
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
- **2026-08-12 M0b（Editor/Runtime 驗證）**：Preview 起得來、19 份 SymbolEffect 的
  SkeletonData 綁定正常；但發現並修復一個真 bug——`RecoverSpinAck.TraverseAwardData()` 漏複製
  `EliminatePos` 欄位，proto stub 預設回退 `emptyArray`，導致中獎 Spine 演出完全不播且無任何錯誤
  訊息（已修一行、`verify_compile.py` 5/5 PASS）
- **2026-08-13 M0b ✅ 全綠**：使用者重測確認 `EliminatePos` 修法生效；**熱鍵 1~8 全數通過**；
  Mask contentSize 數值層（576×328）+ Preview 目視皆正常。五項全過，
  `scratch/codegen-report.md` 風險 1「執行期行為完全未驗證」**已降級**。
  清單見 `docs/M0b-checklist.md`。
  ⚠️ **綠燈的邊界**：熱鍵全過只證明**控制流不卡**——`VsFeatureShowState.PlayVsFeature()` 與
  `CollectFeatureShowState.PlayCollectFeature()` 目前都是空 stub，演出內容完全未驗證。
  兩個新 state 的雙分支已都被走過（空分支 ← `5`；非空分支 ← `6`/`7`/`8`）。

### M0b 期間的三個查證結論（都不是 bug，避免重查）

1. **按 `5` 有 symbol 演出但無報獎跑分＝正確**：mock `RoundWin = bet*3` → rate 3 落在
   `AwardState` 中贏分分支（`PlateEftOdds = [1,3,6,15,30]`），該分支的「分數跑動」是
   `TODO(M2+)`（SmallWin 為公版 Node、尚未串接顯示元件）。
2. **按 `3` 的多次縮放＝三階連播不是單一演出**：mock `bet*35` → rate 35 ≥ 30 → `lvl = 3`
   （`Level.SUPER`），而 `BigWinComponent.Show()` 第三參數 `isStepByStep` **預設 `true`** 且
   `AwardState` 未傳 ∴ 從 BIG 逐階播到 SUPER。
   🔴 **附帶發現**：framework 的 `BigWinAnimName.Max` 找 `MaxWin_Start/End`，但資產
   `BigWin.json` 提供的是 **`UltimateWin_Start/End`** —— 名稱不符、`findAnimation` 會回 null
   且不報錯。現在 `lvl` 最高只到 3 故踩不到，接 MAX WIN 時會浮出。已記入 `ART_ASSET_MANIFEST.md`。
3. **`// CHECK_JP` 不會讓熱鍵 `7` 卡住（原疑慮已否證）**：三處是**一致**關閉——
   `Game_Define.ts:15` enum 成員、`GameView.ts:636` 註冊、`CheckJpState.ts` 整檔皆註解，
   且全專案與 framework 內 `NextState.*CHECK_JP` **零命中** ∴ 無懸空轉場。
   （危險的是「關一半」：enum 留著但註冊拿掉。）
   另注意 **`JPResult` 無任何消費者**，只有 mock 寫入與 `RecoverSpinAck` 複製 ∴ 按 `7`
   不會有 JP 專屬演出，獎金是走一般 BigWin 報獎出來的。

## 機制分類（2026-08-12 codegen 驗證版）

| 難度 | 機制 | 說明 |
|------|------|------|
| 🔴 新開發 | VS Feature | Cash 乘倍 + Collect 乘倍 + 多 VS 作用順序，本作最重機制 |
| 🟡 適配 | Collect Feature | 模板已有 Collect/Cash/CoinState 骨架 |
| 🟡 適配 | 聚寶盆 | 3+1 階狀態機，pattern-library 有驗證變體 |
| — | 其他 | FG、JP 五階、BuyBonus、MAX WIN、預中、聽牌 |

## 規格缺口 → 專案內的 `docs/spec-gaps.md`（2026-08-13 起唯一真相源）

**本頁不再保留缺口清單副本。** 收斂前同一批缺口存在五份（`docs/dev-spec.md` 11 項、
`scratch/codegen-report.md` 11 項、`SPEC.md` 10 項、`AI.md` 概述、本頁 9 項），數量已對不起來。
現行登記表為 GAP-01 ~ GAP-10，含逐項阻塞判定、暫代值、碼內錨點與「填上後要改哪裡」。

⚠️ 該登記表**不在 git 版控內**（`.gitignore` 擋 `docs/`，比照 uk_917 慣例）∴ 碼內的
`GAP-xx` 註解寫成自我描述式，不依賴那份檔案。

需要記住的判斷（其餘查登記表）：

- **阻塞判定的原則**：UK slot 架構下 server 算賠付、client 只顯示 ∴ 阻塞 client 的**不是
  「數字」而是「基數」**（品項數／種類數／階數——決定 UI 結構與美術資產張數）。
  原本把整個 M1 標「阻塞下游」是錯的框架。
- **真正阻塞的只有 2 項**：GAP-02（BuyBonus 品項數）、GAP-04（VS 語意 `2X`/`X2` ＋ 倍率種類數）。
  M2 的 VS Feature / Collect / 聚寶盆 / MAX WIN 現在就能開工，等的只有美術字。
- **VS 語意 `NX` 是暫定非定案**（規格 sheet 3 `S44` 仍是問句）。
- **道具卡是「不實作」不是「待辦」**——三張流程表零規格，不猜測是否為 ExtraBet。
- 對帳：`node docs/check-spec-gaps.mjs`（雙向；三道斷言皆經突變測試確認會紅）。

## VS Feature 規則定案（2026-08-13，多輪與編導確認）

**符號 id 更正**（規格 A 級原文，與 `Game_Define.ts:63-73` 一致）：`Cash=13`／`CashJp(JP)=14`／`Collect=15`／`Vs=16`／`VsCash=17`／`VsCollect=18`。⚠️ 與 `uk_slot_template` 模板的 id 撞車（模板 `13=Collect`／`14=Cash`），引用文件裡的 id 前務必先確認講的是哪一邊。

**尺寸與轉型**：`Vs`(16) 是 1×1「未發動態」；停輪時該輪有 Cash/JP 轉 `VsCash`(17)、有 Collect 轉 `VsCollect`(18)，兩者皆 1×4 覆蓋整輪；覆蓋後該輪四格的盤面**資料**（非純視覺）都變成對應 Symbol id，順序是「原符號先飛走加總 → 才覆蓋」。

**觸發是兩層閘門**（編導口頭補充，規格未寫）：Level 1 盤面級＝有 Collect 且（有 Cash 或 JP）才可能發動；Level 2 輪級＝該輪有 Cash/JP 轉 VsCash、有 Collect 轉 VsCollect、都沒有則不發動。因 Collect 只在第 1/6 輪、Cash/JP 只在第 2~5 輪，型別由輪次唯一決定（col 0/5 → 只可能 VsCollect，col 1~4 → 只可能 VsCash），上限 4 個 VsCash + 2 個 VsCollect。

**VS Collect 分數處置（編導 2026-08-13 改規格，推翻規格原文）**：倍率**不打到盤面上的 Cash/JP**，只在收集時才乘倍（每個 Collect 用自己的倍率乘它收到的分數）∴ 多個 VS Collect 是**相加**不是連乘（例：col0 ×10、col5 ×5、盤面總分 T=1000 → 10000+5000=15000），沒有 VS 的普通 Collect 收到未乘倍的 T。VS Cash 側不變（仍改寫分數、只乘自己那輪的加總，多個 VS Cash 互不影響）。

## M2 實作進度

- **M2.1 已完成**：新增純 `VSManager.Resolve()` 與單元測試（VS Collect 僅於收分時計入自身倍率且多個相加），專案編譯、spec-gaps 對帳與 codegen finalize gate 皆通過。
- **M2.2 已完成資料接線切片**：proto/mock adapter（`AdaptRoundToVSInput`）、修正 `GameView.ts` 的 `vsfeature` mock（原本型別上讓 `Resolve()` 恆不觸發）、`VsFeatureShowState`→`CollectFeatureShowState` 資料交接、轉型後盤面套用顯示層（不改寫 `RoundInfo.MainPlateSymbol`）。異源覆核抓到一個 High finding（`IsValidReel` 把「位置與 server vsType 不符」當硬性過濾，違反規格「dev-only warn、不改行為、以 server 為準」）已修並以 mutation test 驗證測試真的會攔住該回歸。
- **尚未開始**：Fly／Expand／Spine 實際演出、完整 Unshow/replay UI（模板既有缺口，VS Feature 只是繼承不在此切片單獨解決）。

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
