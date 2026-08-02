---
title: UK Slot 海盜女王專案
type: concept
created: 2026-08-02
updated: 2026-08-02
sources: [f_a1b2c3, f_d4e5f6, f_789abc, f_def012, f_345678, f_9abcde, f_f01234, f_567890]
---

# UK Slot 海盜女王專案

uk_pirates_queen 是 UK 市場的海盜女王主題 slot 遊戲，位於 `G:\Cocos_Project\uk_pirates_queen`，使用 Cocos Creator 3.6.2 + Astarte Framework + TypeScript。

## 基本規格

- **盤面**：6 列 5 行
- **主題機制**：消除連鎖、懸賞令倍率、Free Game、輪盤選獎

## 特色機制

### 懸賞令（WantedPoster）

使用 `cc.Layout` 自動排版。`ReconcileCascade` 退場時因 `node.active=false` 導致 Layout 瞬間重排，已被提出視覺突兀需優化。

### 掉落動畫凍結視窗（drop-out）

**問題根因**：把凍結語意（`m_isInDropMode`）與掉落動畫 promise（`m_dropAllSymbolsOutOfScreenPromise`）混為一談，且直接在 `StartSpin`（約 L943）觸發掉落。

**MVP 最小手術方案**（經對抗式評選）：
1. 新增 `m_isInDropMode` 布林專職凍結語意
2. 把 promise 降級為純動畫 handle
3. 把掉落觸發從 `StartSpin` 移到獨立的 `TriggerDropOut()` method

### RenderTexture 凍幀報獎機制（RTCtrl）

與 `uk_746_far_west_client` 同源的機制：
- `RTCtrl.ts` + `PerfGroup.prefab`
- 報獎期間把整個畫面渲成 RenderTexture 貼上、關掉底下實體節點省效能
- **不是**存檔截圖，沒有 `readPixels`
- 關鍵字：`RenderTexture` / `RTCtrl` / `RT_EVENT`
- 其餘 9 個 slot 專案皆未使用此機制

**pirates_queen 是 RTCtrl 進化版**（far_west 是初版，缺 6 項：資源釋放、view.off、resize 守衛、防閃順序、主相機快取、onDestroy 小寫，其中 3 項是真 bug）——新 slot 專案要移植 RT 凍幀**一律抄 pirates_queen 版**。

## 專案搜尋技巧

### PascalCase 私有欄位搜尋陷阱

UK slot 專案慣例是 `public get/set PascalName` + `private m_pascalName`，程式碼可能直接寫私有欄位繞過 setter。

**範例**：`GameView.ts:2314` 寫 `m_isLockRotation = true`
- 搜 `IsLockRotation =` 只找到 4 筆
- 實際有 5 筆（漏了直接寫 `m_` 的那筆）

**正確做法**：搜 `[Mm]_?[Ii]sXxx` 之類同時涵蓋 `m_` 前綴的 pattern。

### Cocos 生命週期命名例外

UK slot 專案的「方法命名用大駝峰」規範**不適用於** Cocos 引擎生命週期回呼：
- `onLoad` / `start` / `onDestroy` / `update` **必須小寫**
- 寫成 `OnDestroy` 引擎不會呼叫、變成死碼且無任何錯誤訊息

**實證**（2026-07-30 於 `uk_746_far_west_client` 的 `RTCtrl.ts:86`）：`eventManager` 從未 unregister，已確認 astarte-framework 無 `OnDestroy` 鉤子。

## 相關

- [[uk-slot]] — UK 老虎機專案群總覽
- [[uk-slot-template]] — 模板專案與慣例
- [[uk-slot-pitfalls]] — UK Slot 踩坑經驗
