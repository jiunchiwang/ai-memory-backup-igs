---
name: project-featurewheel-respin-flow
description: Eye Strike 2 停輪後 FeatureWheel→Respin→FG 的 10 步演出時序與狀態機 seam 規劃
metadata: 
  node_type: memory
  type: project
  originSessionId: 5a77d491-abb5-4d3c-aa00-f792c7ccde10
---

Eye Strike 2「停輪後到進 FG」的完整演出時序（用戶 2026-06-15 確認的權威順序）：

1. 有線獎→先報線獎(WAYS) = **AWARD**
2. FeatureWheel 依陣列序（=盤面 position 低→高）逐個轉出+格子標記作用；FreeGame→盤面外圖示標記、**Grand→當下報獎**
3. 有轉換(Transfer)→先處理轉換
4. 鎖定位置 = **ENTER_RESPIN**
5. 開始 Respin = **SPIN 重轉**
6. 有 Cash→再鎖再 Respin（重複 4、5；雙層索引迴圈）
7. 有升級(Upgrade)→處理升級
8. 結算報獎（沿用最後一手 **AWARD**，讀 `plate.Win`）
9. Wheel 有 FreeGame→Scatter 丟場演出（也可能不演）
10. 進入 FreeGame = **ENTER_FREE**

**關鍵架構**：轉輪演出被 Respin 迴圈夾成前後兩段——前段(②③)在 respin 前（已有 `FeatureWheelShowState` 站位：AWARD 後、ENTER_RESPIN 前）；後段(⑦升級→⑦.5乘倍→⑧結算→⑨Scatter)在最後一手、被 AWARD 切兩半。

**選定 seam 方案 A（沿用 AWARD 當結算）**：升級/乘倍→`SCATTER_SHOW`與`AWARD`間插一個 State（gated 末手+有對應 wheel 功能）；結算→沿用 AWARD；Scatter→AWARD 後縫（ROUND_SHOW_END / LEAVE_RESPIN 前）。否決方案 B（結算搬出 AWARD 會重複 win 邏輯）、C（塞既有 state = 當初否決 EffectStart 的反模式）。

**進度（2026-06-15，狀態機骨架 + 演出接口全到位）**：
- `FeatureWheelShowState`（前段②轉輪+SHOW_MARK seam、尾段③APPLY_TRANSFER）、`FeatureResultShowState`（後段⑦APPLY_UPGRADE→⑦.5APPLY_MULTIPLIER）皆已建並接進狀態機。
- seam 入口：`AfterShowWin`(plate0+HasActiveWheel→前段) / `AfterScatterToNext`(末手+HasPostRespinFeature→後段) / `EnterFreeState`(HasFreeGameWheel→⑨SHOW_SCATTER_DROP)。
- 5 個演出事件全在 `FeatureWheel/FeatureMarkEvent.ts`：SHOW_MARK / APPLY_TRANSFER / APPLY_UPGRADE / APPLY_MULTIPLIER / SHOW_SCATTER_DROP，皆 **fire-and-forget**（演出由另一位同事寫 handler 串接；他上線後可改 await 排序）。
- 純守衛 `HasActiveWheel`/`HasPostRespinFeature`/`HasFreeGameWheel` 在 `FeatureWheelTypes.ts`，有 BC 測試。
- commit：`da3886b`(前段State) `c464434`(FG/MG切層) `4f114e1`(②SHOW_MARK) `72e7e90`(後段State) `89513be`(③⑨)。

**剩餘（非本人）**：① 同事填 5 個演出 handler；② 三個 server 對拍前提（見 [[reference-featurewheel-server-contract]]：SlotIndex↔12格序、Count 語意、WheelFeatures 排序已確認）；③ ⑨SHOW_SCATTER_DROP 在 EnterFreeState 的時點待演出端串接時校準。資料契約見 [[reference-featurewheel-server-contract]]。
