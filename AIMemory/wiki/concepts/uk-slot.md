---
title: UK Slot 老虎機專案群
type: concept
created: 2026-06-02
updated: 2026-07-11
sources: [f_4cfe4c, f_be8c07, f_093bcf, f_79c118, f_967ccc, f_e8b2cf, f_991386, f_cea694, f_3f7536, f_r0b1nh, f_wr4th9, f_f4rw3s, f_3y3s2k, f_ch4ch4, f_e9d947, f_09acc4, f_89a745, f_f4621c, f_e22204, f_9322f0, f_82c757, f_46f6e0, f_94500e, f_b0253d, f_0b3520, f_e9bd6a, f_73183f, f_49dae6, f_4cd205, f_59bf73, f_e2665f, f_ac9912, f_98e336, f_1b276f, f_4c48e6, f_d03f34, f_f79167, f_e84e55, f_b20c5e, f_593c2e, f_c7ce92, f_a4bcd5, f_233d31, f_0376d5, f_8a9474, f_3165ae, f_4f4b55, f_500f52, f_7e491d, f_800551, f_ba8cc5, f_b773d9, f_6fe390, f_b13c42]
---

# UK Slot 老虎機專案群

## 概述

使用者開發一系列面向 UK 市場的老虎機遊戲，基於 Cocos Creator 3.6.2 + Astarte Framework + TypeScript 技術棧。所有遊戲從共用模板 fork 而來，目前共 9 個專案（1 模板 + 7 遊戲 + 1 demo）。

## 技術棧約束

- **Astarte Framework 不可改動** — 所有專案共用的底層框架，禁止修改
- 方法（method/function）命名使用**大駝峰（PascalCase）**

## 專案清單

### uk_slot_template（模板）

- 位置：`G:\Cocos_Project\uk_slot_template`
- 性質：所有 UK slot 遊戲的複製起新來源（git archive，不帶模板 history）
- 支援三種轉輪玩法，透過 FillStrategy 策略模式切換：
  - **Standard** — 傳統滾動
  - **Cascade** — 消除天降
  - **Tumble** — 快速掉落 + 乘倍
- **2026-07-07 回灌修正**（4 commits 本地未 push）：bgm 改註解佔位（模板不含音檔）、欄數陣列改 `Game_Define.COL` 衍生（原寫死 6 欄）、CheckPlateInfo 欄數不符改回報不 crash（對帳函式不應 throw）、ReelDevTool 修復（驅動缺失 + IDLE 就緒閘門，原版從未實測過）
- **起新專案陷阱**：`FirstClone.bat` 的 `../extensions` 相對於執行時 cwd——需在 `Tools_SlotSetUP/` 內執行，從專案根執行會 clone 到上一層

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
| uk_917_leprechauns_pots_client | `G:\Cocos_Project\uk_917_leprechauns_pots_client` | 3 Leprechaun's Pots（開發中）→ 詳見 [[uk-917]] |
| clash_of_olympus_demo | `G:\Cocos_Project\clash_of_olympus_demo` | 諸神之戰 Clash of Olympus（6×4 4096-Ways，希臘神話，開發中）→ 基準 tripleCoinTreasure |

## 專案文件規範

所有 UK slot 專案採用分層文件策略（skill `uk-slot-project-docs` 控制）：
- **AI.md**（索引層，≤2000 字）— 專案 meta、盤面、模組地圖、踩坑
- **docs/modules.md**（詳細層）— 每個模組的事件介面、依賴、資料流

不管改動檔案數多少，進入老虎機專案時都主動建立/更新 AI.md。

## uk-slot-codegen 整合（2026-07-09）

同事開發的 `uk-slot-codegen` skill（全自動 codegen pipeline：xlsx→骨架→Mock→gate 驗證）已整合為 `uk-slot-spec-to-impl` 的 **M0a~M1 可選加速器**：

- **定位**：快速出可跑骨架 + Mock demo，不做特色機制（custom feature 報告不實作）
- **分工**：正式開發全程走 spec-to-impl，codegen 只承接前段骨架生成
- **proto 慣例覆蓋**：一律經 `Proto.ts` 單一間接點（排除 codegen 原本的 replace-all-imports，因 uk_917 實戰教訓）
- **規格轉換**：`excel-to-ai-doc` 是 canonical SOT（抽圖+保真），`spec_adapter.py` 只是 codegen 內部餵料管
- **實測**（uk_917 probe）：17/17 gate 全過，但 spec_adapter 有 5 個 bug（SymID 排序、音效漏抽、JP 偵測等），custom feature 偵測滿分（0 漏 0 誤報）
- **8 項回饋**全部修正完畢（commit cee689e）；整合驗證包已交付同事
- **不抽出整合**：自有 skill 體系已自包含，codegen 保留原樣偶爾借用

相關：回饋文件 `G:\AI\Skill\uk-slot-codegen-feedback.md`、驗證包 `uk-slot-integration-bundle.zip`、[[uk-slot-pitfalls]] 已回灌 5 條 codegen 來源踩坑

## Clash of Olympus（諸神之戰）

- **專案**：`G:\Cocos_Project\clash_of_olympus_demo`
- **規格**：希臘神話主題、6×4 盤面 4096 Ways、基於 uk_slot_template + Astarte
- **最近似參考**：tripleCoinTreasure-client（三幣瑞龍，GameId=399，5×3）
- **spec-to-impl 完成**（2026-07-09）：docs/spec（80 圖）+ dev-spec.md + SPEC.md（25 任務 M0a~M4）
- **分類**：唯一 🔴 是 VS Feature（Cash 乘倍 + Collect 乘倍 + 多 VS 順序），Collect Feature 和聚寶盆降為 🟡（模板有 Collect/Cash/CoinState + pattern-library 有驗證變體）
- **待確認 8 項**：賠率表空白、BuyBonus 售價、FG 手數、VS 乘倍語意、聚寶盆機率、ExtraBet、Proto 時間、GameId
- **下一步**：M0a 起專案，需先確認 GameId 和 Proto 狀態

## spec-to-impl 流程教訓（2026-07-09 實證）

Clash of Olympus 實作過程暴露 5 個流程偏離，已回饋改善 skill 正本（commit 14887cd）：

1. 拿到規格書必須先 invoke skill 從步驟 0 開始，不可直接提方案
2. 基準永遠是 `uk_slot_template`，衍生品只當「最近似參考」
3. 步驟 2 必須讀 `uk-slot-pattern-library` 索引，否則會重複設計已驗證模式
4. 新增步驟 0 前提確認 checklist + 步驟 2 前置 4 項 gate
5. AI.md 綁定步驟 1 完成時建立

## uk_slot_eye_strike 詳細

- GameId=658、ShortGameName=ar2es
- 盤面 6 列不等高（5-4-4-4-4-5）共 26 格
- Proto 來自 `@igs-arcade-division-rd2/uk_658_eyestrike_proto`
- 7 個專案特有機制：MagicPot 能量收集（4階）、Multiplier 乘倍輪盤、GoldBlitzRoulette（FG 內輪盤）、FakeReelManager（4 種投注模式）、NearMiss 聽牌、ReelSymbolMode（4 種顯示模式）、Mystery 神秘符號

## 開發參考文件

- uk_872_eyestrike2_client：`.claude_temp/proto參數說明.md` 記錄 `ar2es2Proto.d.ts` 的欄位用途與值域，作為 proto 協議開發參考

## 架構規範

- **uk_872_eyestrike2_client**：Spine 動畫一律透過 **SpineKit** 播放（統一的 Spine 播放架構），不直接操作底層 spine 元件。

## 待優化項目

- uk_slot_eye_strike：`MultiplierManager.m_downEffectSpine` 的 Idle 動畫實際靜止，可優化為靜態圖 + 隱藏 Spine 省效能
- uk_pirates_queen：懸賞令（WantedPoster）退場時 `cc.Layout` 瞬間重排視覺突兀，需改為動畫過渡

## 回灌工作流

在衍生遊戲修到的問題依層級回灌到不同位置：

| 層級 | 回灌目標 | 範例 |
|------|---------|------|
| 模板級（工具/守衛/寫死值） | `uk_slot_template` repo | ReelDevTool 修復、欄數陣列改 `COL` 衍生 |
| 流程級教訓 | AI-canonical-corp skill 正本 | spec-to-impl checklist 強化 |
| 專案級踩坑 | 專案 `AI.md` | 特定遊戲的已知坑 |
| 模式級修正 | `uk-slot-pattern-library` 卡片 | 已驗證的設計模式 |

## 模板音訊慣例

`MG_Bgm` 與 `FG_Bgm` 背景音樂引用在模板中先**註解掉**（模板不附實際音檔）。新遊戲專案需要 BGM 時再解除註解並補上音檔。

## Skill 管理

- `AI-canonical-corp` 的 slot skill（如 `uk-slot-pattern-library`）透過 **junction** 直接指向正本目錄，改正本即時反映到 `~/.kiro/skills/`，不需額外跑 `sync.ps1`
- `uk-conventions` 是 Claude Code **custom command**（`/uk-conventions`），不是 skill

## 錯誤紀錄分類法

記錄 AI 反覆失誤時，分成兩類：

| 類型 | 定義 | 修法 |
|------|------|------|
| **流程偏離** | 工作流順序失誤（跳過 checklist、基準拿錯） | Gate / 流程強制 |
| **技術錯誤** | 實作層面失誤（型別/邏輯/命名寫錯） | 測試 / 檢查 |

兩類根因不同，分開列並各附 session 實證。此分類法可推廣到任何 skill 或 knowhow 庫。

## 重要設計模式

### Ghost Slot 雙佔位機制

Cocos 版面在「兩項移除一項」時避免置中跳動（snap），使用 ghost slot：item root 佔 Layout 格但 Content 設 `active=false`。同時滿足 0→1 置中、2→1 不跳動、旋轉相容，不需改動 Layout 參數。

### 並發 Gotcha

在 `Promise.all` 之前的同步階段計算狀態決策（例如 `willGhost`），會與並發 group dispatch 產生 race condition。解法：把這類決策移到 async 階段計算。

## Spine-Viewer 插件

Cocos Creator 全域插件，位於 `~/.CocosCreator/extensions/spine-viewer`，用於分析 Spine 資源效能。

- **Batch Scan**：掃描指定目錄下所有 Spine，輸出 Excel（5 欄：Spine檔名、Skin、Animation、Triangle數(最大)、DrawCall）
- **Triangle 計算**：全 keyframe 掃描（從 animation timelines 抽取所有 frame time 取最大值）
- **DrawCall 計算**：CPU 模擬 PolygonBatcher 合批規則（texture identity + blend mode 斷批），不需要 WebGL context
- **效能**：用 `child_process.fork` 獨立進程執行批量掃描，不阻塞 Cocos 主進程
- **注意**：spine-webgl TextureAtlas 的 texture factory callback 每次呼叫必須回傳獨立物件（含 getImage 方法），否則 DC 比對失效
- **打包**：`pack.bat` 產出 `spine-viewer-release.zip`，對方解壓到 `~/.CocosCreator/extensions/` 即可

### Cocos Creator 3.6 插件開發踩坑

- `Editor.Message.send` 只路由到 main.ts methods，不直接送到 panel；跨進程通訊用 Electron BrowserWindow + IPC

## 相關

- [[bridge-project]]（開發工具鏈的一部分）
- [[uk-917]]（同期開發中的專案）
- [[uk-slot-pitfalls]]（踩坑經驗，含 codegen 來源 5 條）
