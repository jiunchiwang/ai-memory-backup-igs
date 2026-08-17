---
name: uk-slot-proto-bin-decode
description: 把 UK 老虎機專案的 server protobuf 封包（.bin）直接還原成可讀資料。當使用者丟一個 .bin 檔進來、說「解封包」「還原 server 資料」「這包在幹嘛」「bin 轉 JSON」「幫我看這手的盤面/中獎/feature」，或需要用真封包驗證 client 邏輯時使用。使用者不需要先自己轉 JSON。僅適用 server 通訊封包；Cocos 專案 library/ 底下的 .bin 是資產編譯快取，不適用本 skill。
---

# UK Slot Server 封包（.bin）還原

## 何時觸發

- 使用者給一個 `.bin` 檔（通常在 `.claude_temp/`），要看裡面的 server 資料
- 要用真封包驗證 client 邏輯（配合無編輯器 harness）
- 要比對「server 給了什麼」vs「client 表演了什麼」

**邊界**：只處理 server 通訊封包。`library/**/*.bin` 是 Cocos 資產編譯快取、
`temp/asset-db/**/out.bin` 是 FBX 轉檔中繼檔，兩者都不是 protobuf，別拿本 skill 去解。

## 前提

專案 `node_modules` 裡有公司 proto 套件（`@igs-arcade-division-rd2/<專案>_proto/`），
內含編譯好的 `*Proto.js`。這是 `npm install` 就會有的東西，不必另外產生，
**也不需要 `.proto` 原始檔**。沒有的話先 `npm install`。

## 做法

在**專案根目錄**執行（cwd 決定去哪找 proto）：

```bash
node <skill目錄>/scripts/decode.js .claude_temp/MaxWin.bin
```

預設行為：自動判斷 message 型別 → 解碼 → 摘要印到 stderr → 完整 JSON 寫成
`.claude_temp/MaxWin.decoded.json`。

常用選項：

| 選項 | 用途 |
|------|------|
| `--list` | 列出這個專案 proto 有哪些 message 型別 |
| `--type <名稱>` | 指定型別，跳過自動判斷 |
| `--stdout` | JSON 印到 stdout 而不寫檔 |
| `--out <dir>` | 指定輸出目錄 |
| `--force` | 允許覆蓋既有的 `.decoded.json` |

一次多包可直接列多個檔，或用 glob（`.claude_temp/*.bin`）。

> glob 由**腳本自己展開**，不靠 shell。PowerShell 不會替原生程式展開萬用字元，
> 會把 `*.bin` 原字串丟進來——所以「交給 shell 處理」在本團隊主力 shell 上是壞的。
>
> 支援 `*` 與 `?`，**只掃單層目錄**（不支援 `**` 遞迴）。大小寫比對跟著檔案系統走：
> Windows / macOS 不分大小寫，Linux 分。配到的目錄會自動略過。

## 型別自動判斷怎麼判的

**解碼沒丟例外不等於型別正確。** protobuf 解碼極度寬容：packed repeated int32
（例如 `Column` / `IntAry`）會把任意 bytes 欄位當成整數陣列吃下去，不報錯、
`verify()` 也過，重編碼長度甚至只差 1%。用「解得動」當判準會選到垃圾。

實際判準是**解碼 → 重新編碼 → 與原檔位元組完全相等**。
只有真正把每個 byte 都認得的型別能還原出一模一樣的 bytes。

判斷結果分三種，腳本會誠實區分，不會靜默猜：

| 情況 | 行為 | 離開碼 |
|------|------|--------|
| 恰好 1 個型別位元組相等 | 直接用，標「唯一命中」 | 0 |
| ≥2 個型別位元組相等 | 印出全部候選、先用第一個，提示可用 `--type` 指定 | **1** |
| 0 個型別位元組相等 | 退回「重編碼長度比」排序，明講結果**未確認** | **1** |

> ⚠️ **型別未確認時離開碼是 1，即使 JSON 有正常產出。** 這是給自動化看的：
> 警告只印在 stderr，只讀 stdout 的 agent 會拿到一份乾淨合法的 JSON，
> 與「已確認」的結果一模一樣、分辨不出來。**要程式化使用就必須看離開碼。**
> 用 `--type` 明確指定型別時不算未確認（那是使用者的決定）。

### 位元組相等**不是**語意身分的證明

初版文件寫「只有真正把每個 byte 都認得的型別能還原出一模一樣的 bytes」——
這句話成立，但**推不出「所以型別是唯一的」**。相等只證明另一個 schema 對這組
wire tag 相容，不證明語意相同。稀疏或小封包很容易碰撞。

實測反例（可自行重現）：`GameInfoData{ShowExtra: true}` 編碼後是 2 bytes `08 01`，
而 field 1 的 `bool true` 與 field 1 的 `int32 1` 在 wire format 上完全同形。
拿這 2 bytes 去比對 eyestrike2 的 18 個 message，**9 個同時位元組完全相等**：

```
CSymbol{Symbol:1}  AwardData{AwardType:1}  FeatureResult{Type:1}
ScAccuUpgradeInfo{Upgrade:true}  TransformInfo{Pos:1}  GridInfo{Mark:1}
WheelUnlockInfo{Symbol:1}  GameInfoData{ShowExtra:true}  MysteryWheelInfo{Pos:1}
```

`exact[0]` 會挑到 `CSymbol`，把 `{"ShowExtra":true}` 解成 `{"Symbol":1}`——
**兩者都是這 2 bytes 的合法解讀，靠位元組永遠分不出來。**
∴ 封包越小、欄位越稀疏，越該用 `--type` 指定而不是靠自動判斷。

> ⚠️ 誠實邊界：實測樣本 31 個真封包、跨 4 個 proto 套件（見下表），
> 位元組相等唯一命中 31/31（長度比對則會留下 3 個候選，區分不出來）——
> 但這 31 包**全是 `SpinAck`**，而 `SpinAck` 夠大夠複雜才會唯一命中。
> 「≥2 命中」在真實擷取樣本裡沒出現過，但上面那個構造反例證明**它是走得到的**，
> 不是理論上的顧慮。「0 命中」則仍未被任何樣本觸發。

## 跨專案實測狀況（2026-08-17）

| 專案 | proto 套件 | 結果 |
|------|-----------|------|
| uk_872_eyestrike2 | `ar2es2Proto.js` | 8 包全部唯一命中 |
| uk_722_robinhood | `ar2rhProto.js` | 14 包全部唯一命中 |
| uk_739_wrath_of_thunder | `ar2wotProto.js` | 1 包唯一命中 |
| uk_slot_eye_strike | `ar2esProto.js` | 8 包全部唯一命中 |
| uk_746_far_west / uk_917 / uk_pirates_queen / uk_slot_chachacha / uk_slot_template | 各自套件 | proto 載入 + `--list` 通過，**無現成封包可解** |
| uk_slot_clash_of_olympus / 非 uk_ 前綴專案 | — | 沒裝 proto 套件（未 `npm install`）→ 腳本會明講找不到 |

**尋找 proto 的規則**：從 cwd 掃 `node_modules/@igs-arcade-division-rd{1,2}/`，
取名字含 `proto` 的套件裡的 `*Proto.js`。9 個專案全部命中，沒有寫死專案名。

> ⚠️ **摘要是 eyestrike2 偏向的，解碼不是。** 型別判斷與 JSON 還原是通用的（全專案通過），
> 但 stderr 摘要挑的是 eyestrike2 系的欄位名。別的專案 RoundInfo 結構不同
> （例：wrath_of_thunder 盤面直接掛 round 上、沒有 `PlateQueue`，轉輪帶叫 `MGReelWeightResult`），
> 摘要就會撈不到東西 —— 此時腳本改印該 round 的**欄位名清單**，讓人看得出結構。
> **完整資料一律在 JSON 裡，摘要薄不代表解得不完整。**

## 解出來之後

摘要（stderr）會挑常見欄位印：`TotalWin` / `Bet` / `BetType`，以及每個 round 的
`RoundWin`、`ReelWeightResult`、`MaxFlag`、fever 類型、剩餘免費局數、`WheelCount`、
`WheelFeatures`、`PlateQueue` 長度、Mystery 觸發。欄位不存在就不印，
所以換一個專案的 proto 也不會爆，只是摘要變短。

盤面座標慣例：`col * RowNum + row`（`Positions`、`RespinLockedPos`、`TransformInfo.Pos`
都是這個編碼）。要對照欄位語意，讀專案 proto 套件裡的 `.d.ts`，或專案自己的
`.proto` 註解——**不要把公司 proto 內容抄進本 skill**。

## 能驗什麼、不能驗什麼

| 可以 | 不行 |
|------|------|
| server 給的盤面、獎項、feature 順序、權重編號、狀態累積 | 演出時序、動畫、視覺（要實機） |
| 「client 顯示的和 server 給的對不對得上」的資料層對帳 | server 為什麼這樣算（那是 server 端邏輯） |

配合「無編輯器實測 harness」（真封包 + 切原始碼行區間 transpile）可以在不開
Cocos 編輯器的情況下對純資料邏輯做實測。
