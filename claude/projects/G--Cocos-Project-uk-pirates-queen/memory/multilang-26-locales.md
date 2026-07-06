---
name: multilang-26-locales
description: 本專案多國語言 = 26 個語系，含完整語系代碼清單與 gameStrings.xml 路徑
metadata: 
  node_type: memory
  type: project
  originSessionId: 6e31ccd0-84e4-47f3-bf68-6d31ab26369f
---

本專案多國語言共 **26 個語系**，位於 `assets/game/Text/<語系>/gameStrings.xml`（plist 格式，每語系一目錄）。

語系代碼（2026-06-16 直接列舉，A 級證據）：
bn, cn, da, de, en, es, frFR, grGR, hi, id, it, jp, ko, mm, ms, nl, pt, ro, ruRU, se, ta, th, trTR, tw, urIN, vn

新增/更新多國字串時用 [[serena-for-callchain-analysis]] 無關；走 `uk-slot-multilang-sync` skill（其描述提到「常見 26 國」正對應此專案）。
