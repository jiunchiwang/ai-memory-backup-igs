---
title: UK Slot 老虎機專案群
type: concept
created: 2026-06-02
updated: 2026-06-18
sources: [f_093bcf, f_79c118, f_967ccc, f_e8b2cf, f_991386, f_cea694, f_3f7536, f_r0b1nh, f_wr4th9, f_f4rw3s, f_3y3s2k, f_ch4ch4, f_e9d947, f_02cb06, f_f944d1, f_bf6094, f_28e62a, f_09acc4, f_4b8ff5, f_c01dbd, f_e61df4, f_89a745]
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

## 開發參考文件

- uk_872_eyestrike2_client：`.claude_temp/proto參數說明.md` 記錄 `ar2es2Proto.d.ts` 的欄位用途與值域，作為 proto 協議開發參考

## 待優化項目

- uk_slot_eye_strike：`MultiplierManager.m_downEffectSpine` 的 Idle 動畫實際靜止，可優化為靜態圖 + 隱藏 Spine 省效能
- uk_pirates_queen：懸賞令（WantedPoster）退場時 `cc.Layout` 瞬間重排視覺突兀，需改為動畫過渡

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
