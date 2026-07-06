---
name: reference-featurewheel-server-contract
description: Eye Strike 2 FeatureWheel/Respin 的 server 資料契約（WheelFeatures 排序、盤面位置編碼、後段資料源）
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5a77d491-abb5-4d3c-aa00-f792c7ccde10
---

Eye Strike 2 FeatureWheel + Respin 演出的 server 資料契約（多數經 server 對拍確認，2026-06-15）：

- **盤面位置編碼**：serverPos = `col*4 + row`（盤面 4 列×6 行，pos 0~23；col0→0-3、col5→20-23）。`Common.DecodeServerPosByRowConfig` 為權威解碼器。
- **WheelCount = 盤面 Wheel 符號數**：`Game_Define.Symbol.Wheel = 15`；每個 Wheel(15) 符號 → 一次轉輪 → 一個 `WheelFeatures` entry。
- **WheelFeatures 已排序（server 對拍確認）**：`RoundInfo.WheelFeatures: IFeatureResult[]` 已按各對應 Wheel 符號的盤面 position(col*4+row) **低→高排序**。`IFeatureResult` 無盤面位置欄位，client 無法自行配對，故演出**直接照陣列序播放即為 position 序**。
- **FeatureResult Type enum**（`FeatureWheelTypes.ts`，刻意對齊 server）：None=-1 / FreeGame=0 / Multiplier=1 / Upgrade=2 / SymbolConvert(Transfer)=3 / GrandJP=4。
- **演出後段資料源**：③轉換=`RoundInfo.TransferResult: ITransformInfo[]`（`{Pos,Symbol,Number}`）；⑦升級=`RoundInfo.UpgradeResult: ITransformInfo[]`；⑦.5乘倍=`WheelFeatures[i].Multipliers[]`+`Positions[]`；②Grand當下報獎=`WheelFeatures[i].Win`。

停輪後完整演出時序見 [[project-featurewheel-respin-flow]]。相關純邏輯/State：`FeatureWheelTypes.ts`(HasActiveWheel/ParseServerWheelData) · `FeatureWheelShowState.ts`(前段轉輪演出)。
