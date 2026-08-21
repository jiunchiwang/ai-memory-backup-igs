---
title: Clash of Olympus（諸神之戰）
type: concept
created: 2026-07-16
updated: 2026-08-21
sources: [f_4c48e6, f_f79167, f_b20c5e, f_593c2e, f_c7ce92, f_385d4d, f_90d6e8, f_5927a3, f_6587d2, f_ab095f, f_baad41, f_2675c6, f_cf423c, f_e0a15e, f_9b909e, f_05937b, f_f8bf81, f_4b8603, f_a732fb, f_166468, f_676da8, f_fe2aba, f_8481cf]
history_sources: []
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

## 規格裁決與缺口登記 → 已拆出獨立頁

規格缺口登記（GAP-01~10 的唯一真相源是專案內 `docs/spec-gaps.md`，不在版控）、GAP-04 語意定案、VS Feature 規則定案（符號 id／尺寸與轉型／兩層閘門／VS Collect 相加不連乘）、VS 轉型權威來源裁決、規格圖是 A 級證據、設計文件單一真相源紀律——全部移到 **[[uk-slot-clash-olympus-spec]]**（2026-08-21 拆出，本頁原 210 行超過 wiki 200 行上限）。

分界線是**這句話由誰說了算**：規格層的裁決在那一頁，專案現況與進度在本頁。

## 借來的 placeholder 字型（2026-08-14）

本作前身 uk_739（wrath_of_thunder）沒做金額顯示 ∴ 從 uk_872_eyestrike2_client 借了字型放進 `assets/game/Font/`，但那是埃及美術風格、本作是希臘神話 ∴ **上線前必須換掉**。

- `SymbolCashNUM.fnt`：已接上並實機驗證（綁在 `MainGame.prefab` 的 `GameView.m_cashFont`）
- `Multiplier_Num.fnt`：**刻意未接線**——其 `.fnt` 表頭 `charset="32,48-57,120"` = 空白+`0-9`+小寫 `x`，**沒有大寫 X (88)** ∴ 畫不出 `2X`

∴ 倍率現階段共用 `SymbolCashNUM`（它含 88 與 120 兩者）。可遷移判準：接線點陣字型前先讀 `.fnt` 表頭的 charset 確認涵蓋所需字符，缺字不會報錯只會靜默少一個字。

## M2 實作進度

- **M2.1 已完成**：新增純 `VSManager.Resolve()` 與單元測試（VS Collect 僅於收分時計入自身倍率且多個相加），專案編譯、spec-gaps 對帳與 codegen finalize gate 皆通過。
- **M2.2 已完成資料接線切片**：proto/mock adapter（`AdaptRoundToVSInput`）、修正 `GameView.ts` 的 `vsfeature` mock（原本型別上讓 `Resolve()` 恆不觸發）、`VsFeatureShowState`→`CollectFeatureShowState` 資料交接、轉型後盤面套用顯示層（不改寫 `RoundInfo.MainPlateSymbol`）。異源覆核抓到一個 High finding（`IsValidReel` 把「位置與 server vsType 不符」當硬性過濾，違反規格「dev-only warn、不改行為、以 server 為準」）已修並以 mutation test 驗證測試真的會攔住該回歸。
- **M2.3 已完成**：VS 欄的倍率（`NX`）與加總值顯示，走 BitmapFont（GAP-04 解除）。
- **M2.4 已完成（2026-08-18，commit `9c8d605`）**：對決演出時序骨架。每個 VS 欄四拍——
  ①觸發符號飛向 VS 種子格 ②整欄換成 VS 符號 ③對決（Spine 未交付 ∴ 佔位等待）④揭示數字。
  `OnEnter` 改 async、轉場照 `AwardState` 的旗標 idiom 交給 `OnProcess`。
  Preview 實機逐幀驗過：演出順序（Cash 型左→右先、Collect 型後）、飛行複本無殘留、
  cell 位置未被動到、下一局清空、演出期擋按停。
  ⚠️ 三項未結：中斷窗口（EH-VS-6）實機測試**被 `IsMgOmen` 擋掉 ∴ 沒真的觸發**、
  unshow 修法只證明可達、兩路徑等價只有間接證據。細節在專案的 `docs/M2-VS-design.md`
  （該檔**不進版控**，只在本機）。
- **M2.5 已完成（2026-08-18，commit `53858fc`）**：Collect 收分演出。逐顆 Cash 飛向 Collect、
  雙 Collect 各收一次、JP 先轉分數再飛、VS 欄的來源收合成承載值。Preview 實機驗過熱鍵 6 與 9。
  跨 vendor 覆核 7 條中採納 3 個新 warning（含把「proto 可能改用打包座標編碼」做成越界偵測）。
- **尚未開始**：對決 Spine 本體與 1×4 美術（資產未交付）、聚寶盆、Jackpot 五階、BuyBonus、
  MAX WIN、預中／聽牌、完整 Unshow/replay UI。

## 框架狀態機的兩個事實（2026-08-18 執行期查證，A 級）

1. **`stateManager.NextState()` 只設旗標**（`m_nextState` + `m_toTransit`），真正的轉場在
   `Tick()`；而 `Tick()` 在轉場時**必定**先呼叫當前 state 的 `OnLeave()` 才 `OnEnter()` 下一個。
   ∴ 「強制跳 state 會跳過 OnLeave」是**錯的**——這是異源覆核提出、被執行期原始碼否證的主張。
   查法：Preview 執行期 `window.Astarte.StateManager.Tick.toString()`（實作在未版控的
   `dist/main.js`，靜態讀 `StateManager.ts` 只會看到介面宣告）。
2. **`SpinState.OnEnter` 在呼叫 `OnRecvSpinAck( ack, true )` 之前就把
   `commonGameManager.HasUnshow` 清成 `false`** ∴ 任何在後續 state（VS／Collect／Award）
   讀 `HasUnshow` 判斷「這輪是不是斷線復原」的分支**恆為 false，是死碼**。
   要判斷得自己在 `OnRecvSpinAck` 把 `isUnshow` 記下來。

## Preview 實機驗收的三個入口坑（2026-08-18）

在這個專案跑 Preview 自動化時，以下三件事各害我誤判一輪：

1. **進場不會自己過**，要點 `IntroView/AnimNode/Btn/LoadingToBtn/Btn_Loading`（loading 跑完才 active）。
   同畫面的 `Btn_Right` / `Btn_Left` 都無效。
2. **spin 鍵是 `btn_spin`**（路徑 `Node_Bar/BarNode_share/floatView/Node_Bar/Bar_Body/Btn/btn_spin/btn_spin`）。
3. **找節點要看 `activeInHierarchy` 不是 `active`**——場景裡有 `Btn_Play` 自己 `active: true` 但父層關著，
   依 `active` 找到它、算座標、點下去是點到空氣，**外觀與「按了沒反應」完全一樣**。

另兩個誤導訊號：`Clip_Intro_*` 的 `instantiate` 失敗只是 warning（根因訊息是
`Node "AnimNode" has no path "Btn/Continue_Text"`）；`Common_Mask` 恆 `active: true` 是四邊 letterbox，
不是擋輸入的遮罩。

工具：專案內 `docs/preview-vs-probe.mjs`（自起 Chrome + CDP，Node 24 內建 WebSocket，零外部相依）
與 `docs/preview-interrupt-test.mjs`。⚠️ 兩支都在 `docs/` **不進版控**。

## spec-to-impl 教訓（仍成立）

- Agent 拿到規格書後必須先 invoke skill 從步驟 0 開始
- 基準永遠是 [[uk-slot-template]] 不是衍生品
- 步驟 2 必須讀 pattern-library 索引否則會重複設計已驗證模式

## Cocos prefab 踩坑（2026-08-12 M0b 實證）

`MainGame.prefab` 的元件欄位值顯示 `None` **不代表未綁定**——跨 nested prefab 的參照存在
`PrefabInfo.targetOverrides`，查欄位值會誤判。判斷是否真的接線要 grep 該 prefab 的
`cc.TargetOverrideInfo` 條目，不能只看欄位值。

## 相關

- [[uk-slot-clash-olympus-spec]] — 本頁拆出：規格裁決與缺口登記（含專案已改名 `uk_963_divine_duel_client` 的說明）
- [[uk-slot]] — UK 老虎機專案群
- [[uk-slot-template]] — 模板專案
- [[uk-slot-codegen]] — 本作 M0a 使用的 codegen 工具
- [[codegen-git-init-gap]] — codegen 流程 git 初始化缺口的修復（本作是首個實測案例）
- [[uk-slot-pitfalls]] — 踩坑經驗
