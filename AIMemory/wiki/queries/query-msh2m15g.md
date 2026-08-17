---
title: BC-17b 恆真問題的根因分析
type: query
created: 2026-08-17
updated: 2026-08-17
sources: [f_ca3437]
---

# BC-17b 恆真問題的根因分析

## 問題描述

telegram-kiro-bridge 的 BC-17b 斷言被發現是恆真的——突變測試（改壞程式碼）後斷言仍然綠燈。突變 2 把 effort 解析邏輯改壞，但沒被抓到。

## 根因

**問題不在斷言本身，而在測試的設定方式**：

1. 測試在 `withProvider` 傳了 `pin`（model/effort 設定）
2. 接著呼叫 `applyModelEffort`，它會發 `set_config_option` 給 ACP adapter
3. ACP adapter 回應的 `configOptions` 包含當前生效的值
4. **那個回應沒帶 `models` block**
5. 導致後續邏輯把 `effort` 欄位用 `configOptions` 的值**蓋回去**

∴ 無論 effort 解析邏輯對不對，最終測到的 effort 都是同一個值——突變的效果被沖掉了。

## 可重用教訓

1. **突變測試只能證明斷言有被執行到，不能證明斷言守的是對的性質**——即使斷言不是恆真，如果 safety property 定義錯了（把錯誤行為釘成 expected），變異測試也會全綠

2. **「兩臂都傳 pin」是 A/B 測試的常見失效模式**：需要比較「有 vs 無」的效果時，兩臂都給同一個設定會讓差異消失

3. **驗證 effort 解析邏輯需要讓兩臂在「有 pin」與「無 pin」間產生差異**，不能都傳 pin

## 修復

commit 7974d27 修復了 effort 後綴解析（`splitEffortSuffix`）：
- 斜線格式（如 `gpt-5.5/medium`）只在後綴命中該 adapter 公告的 `reasoning_effort` 值域時才拆
- 方括號格式（如 `gpt-5.6-terra[medium]`）因是專用語法，維持無條件拆

修復後經 Fable5 覆核確認邏輯成立。

## 相關

- [[verification-diagnosis]] — 恆真斷言的五種形態與突變測試方法論
- [[bridge-smoke-gate]] — smoke 閘門與 BC-x 斷言追溯編號
