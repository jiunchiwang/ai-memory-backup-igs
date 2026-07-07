---
title: UK Slot 老虎機專案群
type: concept
created: 2026-06-02
updated: 2026-07-08
sources: [f_4cfe4c, f_be8c07, f_093bcf, f_79c118, f_967ccc, f_e8b2cf, f_991386, f_cea694, f_3f7536, f_r0b1nh, f_wr4th9, f_f4rw3s, f_3y3s2k, f_ch4ch4, f_e9d947, f_09acc4, f_89a745, f_f4621c, f_e22204, f_9322f0, f_82c757, f_46f6e0, f_94500e, f_b0253d, f_0b3520, f_e9bd6a]
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

## 專案文件規範

所有 UK slot 專案採用分層文件策略（skill `uk-slot-project-docs` 控制）：
- **AI.md**（索引層，≤2000 字）— 專案 meta、盤面、模組地圖、踩坑
- **docs/modules.md**（詳細層）— 每個模組的事件介面、依賴、資料流

不管改動檔案數多少，進入老虎機專案時都主動建立/更新 AI.md。

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
