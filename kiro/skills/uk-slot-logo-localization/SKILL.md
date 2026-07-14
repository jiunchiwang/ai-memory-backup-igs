---
type: skill
domain: slot
created: 2026-07-14
tags: [uk-slot, logo, localization, asset]
source: session
---

# uk-slot-logo-localization

UK 老虎機專案的 logo 圖多語系複製。每個專案的 `assets/game/Text/logo/` 底下，
除了 `logo_cn.png`（簡體中文有獨立設計、不可複製英文版覆蓋）之外，
其餘語系的 logo 預設都是英文版 `logo_en.png` 的原圖複製，只是換檔名。

## 觸發條件

- 新專案／既有專案要補齊 logo 多語系檔案
- 使用者要求「logo 圖複製到各語系」「logo 在地化」

## 標準語系代碼清單（參考 uk_slot_eye_strike）

`assets/game/Text/logo/` 下實際出現過的語系代碼（不含 cn/en）：

```
bn da de es frFR grGR hi id it jp ko mm ms nl pt ro ruRU se ta th trTR tw vn
```

這份清單不是寫死的規格，是「已知曾經需要過的語系」的參考基準；
實際要建哪些語系，以當下專案的規格/既有 `assets/game/Text/<語系>/gameStrings.xml` 目錄或使用者提供的清單為準。
若使用者沒有明確清單，且專案也還沒建立對應語系的文字目錄，先跟使用者確認語系清單再動手，不要自行假設。

## 步驟

1. 確認目標語系代碼清單（見上）。
2. 檔名規則：`logo_<語系代碼>.png`（大小寫依語系代碼原樣，如 `frFR`、`ruRU` 是大小寫混合，不要自行改成全小寫）。
3. **只複製 `.png`，絕對不要複製 `.png.meta`**：Cocos Creator 的 `.meta` 內含 `uuid`，
   若整個 meta 一起複製，會造成兩個資產共用同一個 uuid，資產資料庫會壞掉。
   - Cocos 編輯器有開著、且 `cocos362` MCP bridge 可連線時：優先用
     `mcp__cocos362__asset_import`（`sourcePath` = 來源 png 絕對路徑，`targetUrl` = `db://assets/game/Text/logo/logo_<語系>.png`），
     編輯器會自動產生正確的 `.meta` + SpriteFrame 子資產。
   - 編輯器沒開／MCP 連不上：直接在檔案系統複製 `logo_en.png` → `logo_<語系>.png`，
     不建立 `.meta`。下次在 Cocos Creator 開啟專案時，asset-db 偵測到沒有 meta 的新檔案會自動 import 並產生 uuid，不需要手動處理。
4. 複製完之後 `ls logo_*.png` 確認數量、`ls *.meta` 確認沒有多出非預期的 meta 檔。
5. 若之後美術有提供某語系的專屬設計圖（不是英文版直接沿用），用該圖覆蓋對應的 `logo_<語系>.png` 即可，
   不影響其他語系。

## 常見誤區

- 誤把 `logo_cn.png` 也用英文版覆蓋 — cn 有自己的設計，不在複製範圍內。
- 連同 `.png.meta` 一起複製 — 會造成 uuid 衝突。
- 語系代碼大小寫寫錯（例如 `frfr` 而非 `frFR`）— 要跟專案既有 `assets/game/Text/<語系>/` 目錄名稱或
  `uk-slot-multilang-sync` 用到的語系代碼保持一致。
