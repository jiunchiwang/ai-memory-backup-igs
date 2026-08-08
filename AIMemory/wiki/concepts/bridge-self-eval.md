---
title: Bridge 自評與收尾檢查（SELF_EVAL / Turn-Lint）
type: concept
created: 2026-07-13
updated: 2026-08-08
sources: [f_f16f7b, f_9f9b1f, f_87efaf, f_1b2fd1, f_6de90c]
---

# Bridge 自評與收尾檢查

[[bridge-project]] 有兩套獨立的「agent 自我檢查」機制：`SELF_EVAL` 是模型主動回報的量化自評 token，`turn-lint` 是收尾時的機械啟發式檢查；兩者都刻意選擇「觀察而非攔截」的設計。

## SELF_EVAL 設計

設計跨 backend 量化自評（`SELF_EVAL` token）機制時，對抗性審查否決了三個複雜方案，發現六個共通致命缺陷，可作為未來設計類似自評/評分機制的通用檢查清單：

1. tsc 型別驗證可被 agent 謊報低分繞過
2. 觸發條件可能與 Kiro/Codex 等 backend 已知限制互相矛盾
3. circuit breaker 整合的前提條件未經驗證
4. 沒有證據顯示 backend 真的會遵守自評指令
5. 未驗證的實作細節被當成行為契約使用
6. 巢狀 payload 會破壞既有的扁平欄位慣例

查詢介面決策：選新增獨立 `/selfeval` 指令，排除併入既有 `/status` 擴充。

## vc-kiro-delegate 實證教訓（實作 SELF_EVAL 時撞到）

- kiro-cli 的 prompt 走命令列參數有長度上限（37KB 會炸 `Argument list too long`），長 spec 應寫成檔案讓 Kiro 自己讀路徑
- 獨立 reviewer 這輪抓到 3 個真問題（多餘空行、`listRecent` 死碼、`/selfeval` 漏登記 `COMMAND_SPECS`），主 agent 接手修不叫 Kiro 修第二次

## Turn-Lint（機械收尾檢查）

- 新增 `src/turn-lint.ts`（2026-07-17）：機械檢查回覆結尾語言/ASK 按鈕違規（問句無 ASK、CJK 本文卻英文收尾），掛在 `run-prompt.ts` 的 turn 收尾處，只 `console.warn` 不擋訊息不改文字——根因是 Fable5 診斷「收尾提議句繞過規則檢查、只有 model-independent 機械層才治本」
- 因為判斷邏輯是啟發式正則（問句/語言比例判斷），容易對 code block、反問句等正常內容產生 false positive，所以選擇只 `console.warn` 觀察（定位同 SELF_EVAL），排除直接攔截或自動改寫回覆——避免誤傷正常訊息

## 相關

- [[bridge-project]] — Bridge 本體架構
- [[bridge-model-strategy]] — vc-kiro-delegate 委派機制
