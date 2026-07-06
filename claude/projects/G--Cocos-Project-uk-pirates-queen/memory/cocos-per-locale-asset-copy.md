---
name: cocos-per-locale-asset-copy
description: Cocos 多語系圖片資源複製：只複製 .png 不複製 .meta，避免 UUID 衝突；meta 由編輯器 import 自動生成
metadata: 
  node_type: memory
  type: project
  originSessionId: 6e31ccd0-84e4-47f3-bf68-6d31ab26369f
---

在本專案要把某 base 語系的圖片資源複製成全 26 語系（如 `logo_en.png` → `logo_<語系>.png`，放在 `assets/game/Text/<資源>/`）時：

**只複製 `.png`，絕不複製 `.meta`。**

**Why**：Cocos 的 `.meta` 內含唯一 UUID（例：`logo_en.png.meta` 的 `77b4a4f1-...`）。若連 `.meta` 一起複製，25 個檔會共用同一 UUID → asset-db UUID 衝突，會壞。

**How to apply**：
1. 只複製 png：`for loc in <25語系>; do cp logo_en.png "logo_${loc}.png"; done`（語系清單見 [[multilang-26-locales]]，排除 base 語系）
2. 不動 `.meta`。新 png 由 Cocos Creator 開啟/reimport 時自動生成各自獨立的 meta+UUID。
3. 編輯器沒開時複製照樣成立，下次開編輯器會自動 import；可選用 `mcp__cocos362__asset_reimport` 逐一確認。

注意：複製出來的圖內容都跟 base 一樣，只是建好「檔名+位置」佔位；各語系正式 logo 美術圖仍需後續逐一替換。

文字類多語系（gameStrings.xml）走 `uk-slot-multilang-sync` skill，與此圖片流程不同機制。
