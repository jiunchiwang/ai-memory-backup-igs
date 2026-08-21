---
title: Bridge Persona 人格系統
type: concept
created: 2026-08-20
updated: 2026-08-21
sources: [f_5247b2, f_145db3, f_0c20d9, f_3fafee, f_3bf9d1, f_99fc0a, f_c991f8, f_521237, f_5135e1, f_5b26fa, f_4dcd48, f_1887dd, f_f6f453, f_60a8a0, f_ddba08, f_31118f, f_21c16c, f_f0eee2, f_3f98e6, f_67f584, f_d4e4fe]
history_sources: [f_1bd398]
---

# Bridge Persona 人格系統

## 概述

telegram-kiro-bridge 的角色人格功能（首個人格：哆啦A夢），讓 bridge 的 Claude backend 在互動時帶一個可設定的語氣人格，同時把工程紀律（承重核、事實主張閘門、push back 格式等）完全隔離在人格檔之外。**Stage 1 與 Stage 2 皆已完成並實機驗證生效**：session 的 system prompt 逐字帶著人格設定（A 級證據），`persona_switch` 切換路徑走通。歷史脈絡：最初的架構（session carve-out）曾因跨 vendor 覆核抓到兩條 Critical 而卡在未 push 狀態，後改採 Dream Executor 架構才收斂交付（見下節）。

## 設計定案（v4）

- **人格只放語氣個性關係**，工程紀律完全不進 persona 檔——紀律留在 `CLAUDE.md`／`POLICIES/` 那一層，不會因為切換人格而跟著變。
- **注入通道走 Claude ACP 的 `_meta.systemPrompt.append`**，不是 preamble——preamble 有凍結快照政策（見 [[bridge-project]]），人格切換不能違反它。
- **僅支援 Claude backend**：這是 Stage 1 的明確 scope 邊界，不是疏漏；Kiro／Codex 的重新測試是 Stage 3 的範圍。

## 四階拆解與現況

使用者於 2026-08-20 核可將功能拆成四個階段推進：

1. **Stage 1**（✅ 已完成）— 注入通道 + `/dream` 維運隔離（人格不能污染夜間維運寫進去的長期記憶）
2. **Stage 2**（✅ 已完成）— `/persona` 指令與人格切換
3. **Stage 3**（未開始）— Kiro／Codex 重新測試，並補惡意 persona（prompt injection 類）測試
4. （第四階未在 fact 中具體展開）

## 架構演進：Dream Executor 取代 Session Carve-out

Stage 1 最初的實作是「暫時關掉人格 → 執行 `/dream` → 還原人格」的 session carve-out 骨架，但這類「暫時關掉 X → 做事 → 還原 X」的骨架有三個與 `try/finally` 邊界相關的通病，皆已在本專案實測踩過並修正：

1. **entry 的副作用不可留在 `try` 外面**——若 `setPersonaOverride`／進場 `drop()`／通知使用者三件事都排在 `try` 之前，任一 throw 就讓 `finally` 永遠不會跑，人格永久卡死且無回復路徑。
2. **`finally` 內「還原」必須排在「可能失敗的收尾」之前**——exit `drop()` 若排在 `clearPersonaOverride()` 前面，`drop()` 失敗會連帶擋住還原。
3. **`finally` 的最後一句若 throw，會蓋掉 `try` 區塊正常回傳的值**（JS `finally` 語義）——該句必須自帶 `.catch()`。

這三個缺陷指出更根本的問題：carve-out 把「維運無人格」這個保證綁在 session 生命週期的進出場邏輯上，每補一個退出路徑就多一個可能漏接的角落。查證後改採**方案 D：Dream Executor**（無人格、非註冊、短命的獨立 session），推翻另兩個候選——方案 C「per-request 呈現層注入」因 ACP 的 `systemPrompt` 只在 `session/new`／`session/load` 生效、無 per-request 通道而不可行；方案 B「只在 close-time extraction 清洗」因 `/dream` 步驟本身會直接呼叫 `remember()` 寫 fact、繞過唯一清洗點而不可行。決策記於 `docs/SPEC-persona-dream-executor.md`。改版後以 commit `51e1c01` 推送至 `origin/feat/persona-stage1`，通過獨立覆核 READY。

## 外部注入通道旁路（繞過 `_meta`，結構上是 Dream Executor 的盲點）

Dream Executor 的「不送 `_meta.systemPrompt`」保證只鎖住一個注入通道；同一個 SDK／CLI 常有另一條完全獨立的通道能達到同等效果並繞過它。2026-08-21 同一天連中兩次：

- **Claude backend：`outputStyle`**——是 Claude settings 的欄位（`sdk.d.ts` 的 `settings` 型別內，非 top-level Options），由 adapter 宣告的 `settingSources: ["user","project","local"]` 載入，**不需要任何 `_meta` 就會生效，而且與 `_meta.systemPrompt.append` 疊加**（四臂探針實測：ON+無_meta→生效；OFF(檔案仍在)+無_meta→不生效，證明變因是設定非檔案存在；ON+送 append→兩個 marker 同時出現，append 壓不掉 outputStyle）。理論上唯一的壓制路徑是把 `_meta.systemPrompt` 送成字串整個取代 preset，但那會丟掉 Claude Code 的全部工具說明，dream 需要用工具 ∴ 不可用、且未實測。
- **Codex backend：`CODEX_CONFIG` 環境變數**——四臂探針證實 `CODEX_CONFIG={"developer_instructions":"..."}` 端到端生效，不必改 adapter、不必 fork：codex-acp 的 `newSession()` 不讀 `_meta`，但 `this.config` 來自 `process.env["CODEX_CONFIG"]`，經 `mergeGatewayConfig` 在無 gateway 時原封回傳 ∴ 未知鍵不被剝掉。誠實邊界：本機 `.env` 目前沒有 `CODEX_CONFIG`（洩漏是前瞻風險非現況）；且 bridge 是一 session 一 adapter 行程，切人格必須重 spawn 行程。

兩案結構相同：隔離設計者只審過自己選用的那一個通道，另一個通道躺在外部設定／環境層，不在任何 diff／原始碼審查的視野內——連六輪覆核（含兩輪跨 vendor）都沒有人提過，因為覆核者看的也只是 diff 與原始碼。已加 `src/claude-output-style.ts` 的 `/dream` 啟動偵測，但偵測讀不到 managed settings 層（企業政策層）∴ **偵測不到不等於沒有**，且只覆蓋 `/dream`、互動 session 的 persona+outputStyle 疊加不警告。設計成**警告而非阻擋**：`/dream` 是無人值守排程執行，拒絕執行會讓整晚維運靜默停擺，而 outputStyle 造成的後果是語氣染色（fact/wiki 語氣異常）而非資料損毀，warn+continue 比 block 更相稱。本機目前無此風險（三層 settings 檔皆無 `outputStyle` 欄位、`~/.claude/output-styles/` 目錄不存在；誠實邊界：managed settings 層讀不到，只能說這三層沒有）。

## Stage 2：`/persona` 指令與 pin

- **`/persona off` 用具名 `PERSONA_OFF` sentinel** 把「明確關閉」存成字面值，而非刪除 pin 記錄——刪除後下次 `create()` 會退回 `.env` 的 `PERSONA` 設定，造成人格靜默復活。
- **BC-8（pin 撐過 bridge 重啟）判斷曾一度被推翻又改回**：一度判斷「不該保留、新增磁碟 store 不划算」，但查證 `switchAgent()` 已有 `savePinnedAgents()` 完整持久化先例（含失效 pin 時 warn+清+退回 `.env` 的既有處置）後推翻此判斷，改為照抄該形狀新增 `pinned-persona.json` store。教訓：反對某設計前要追到真正執行的那一層（`sessionManager`），不能只讀 command handler 就下結論。
- **最終選擇 R-5 降 scope**：`/persona` 只受理已在 ACP Claude backend 且已有 live session 的 chat，其餘含 `off` 一律拒絕且不碰狀態——而非繼續擴大 provider/backend/session-state 狀態空間的測試覆蓋。理由：兩輪跨 vendor 覆核的 findings 100% 落在同一個狀態矩陣維度上（逐格被點名而非隨機擴散），代表繼續加測試是在追一個掃不完的表，縮小可達狀態空間比擴大覆蓋更根本。降 scope 過程中保留了 `switchPersona()` 裡 `existing?.activeProvider` 這一行防禦碼（未照原草稿刪除），因為它是正確的既有防線、刪除會重新引入前一輪覆核抓到的 High finding。

## 測試與驗證紀律教訓

- **斷言要打在「實際送出去的那一層」，不是中間值**：Stage 1 設計初稿曾斷定人格文字「串接在 preamble 最尾端」並以此當作立論基礎，實查卻是人格後面還有五段狀態資料（含切換人格時必定出現的 archive handoff），而原本的斷言打在中間值 `breakdown.text` 上會恆綠、真正送出的是 `session.memoryPreamble`——綠燈不代表沒事、代表沒驗到。可遷移處置：①修法是換立論不是搬位置（要壓過的是指令類內容，不是後面的狀態資料）；②新立論的前提要自己配一道機械斷言（白名單擋未知區塊，而非「檢查有沒有指令」這種無法機械判定的寫法）；③驗中間值與驗實際送出值不可共用同一個 helper，否則兩條斷言會一起鎖錯層。
- **突變測試的三種假象**（persona-stage1 一輪同時踩到）：完整判準與修法見 [[gate-mutation-testing]]；本輪貢獻的具體案例是 `if (false)` 造成 unreachable code 被 tsc 擋下（顯示 `error` 不是 `survived`，等於 gate 沒跑）、變異體讓實作 throw 導致測試腳本整個崩掉而漏過目標斷言（false-kill）、殘留突變稽核只憑「想得到要 grep 什麼」而漏掉「移除守衛型」突變（正解是錨在突變定義本身的完整清單上）。
- **純函式斷言全綠不代表 production call site 有接線**：異源覆核者曾示範三個一行 no-op（把某參數改成 `undefined`、拿掉某個引數、刪掉某行呼叫）全都 `tsc` 乾淨且既有斷言仍 `passed`——因為既有斷言全是測試檔自己呼叫純函式，從未經過真正的 call site，值穿過中間層靠的是繼承不是決定。兩種互補補法：①**真子行程 e2e**（spawn fake agent fixture，把它實際收到的參數落成檔案再回讀斷言，驗真實 wire payload）；②**原始碼字面結構斷言**（正則驗某個呼叫真的出現在指定函式邊界內，但斷言訊息必須明寫「結構斷言、非行為驗證」，原始碼一改就要更新錨點）。抽純函式與驗 call site 是兩件事，做了前者不要以為後者也做了。
- **skip 守衛測試組必須配一條負對照**：只驗「該跳過的跳過了」的測試組，守衛被寫成恆真時整組照樣全綠而功能無聲死掉。正確形狀是三條一組：條件 A／B 該跳過 → 驗真的跳過且改走替代路徑或兩條路徑都不走；**條件 C（一般情況）不該跳過 → 必須驗證它照舊真的執行了原本的動作**——第三條常被漏掉，卻是唯一能抓到「守衛被寫成恆真」這個最危險回歸的斷言。
- **時序窗口從外部控制不到時，縮小斷言範圍要指名誰接手被放掉的性質**：某個早退分支的決定性時序點在函式內部好幾個 await 之後，無法從外部測試控制——若在測試裡強行改寫該處的中間狀態，可能連不該受影響的分支也一起被改乾淨，變成「兩邊都乾淨、斷言恆綠而什麼都沒驗」。正解是把斷言縮小到「這個時序下真的驗得到」的性質，並另找一條有決定性時序保證的測試（例如依賴同一個微任務內必然發生的註冊順序，而非 `sleep`）補回被放掉的性質。判準：縮小範圍的正當理由是「不縮小會恆綠」，不是「不縮小會 flaky」；縮小後必須指名哪一條測試接手了被放掉的性質。

## 人格檔慣例

正本位於 `personas/*.md`，**進版控**——比照 `plan-templates/*.json` 的「模板是資料不是程式碼」慣例，新增一個人格只需加檔案，不需改 code。首個人格 `doraemon.md` 逐字複製自使用者提供的原始 System Prompt 文件，不做任何改寫。

## 外部建議的取用與反駁

使用者提供兩份外部 AI 對「Codex ACP 如何加入角色人格」的建議文件。其中一份的 **Persona／Behavior 解耦概念**被採用（比原設計乾淨）；但同一份文件建議的兩個具體實作方向——**Kiro Custom Agent** 與 **`claude -p --append-system-prompt`**——都經實測反駁，不適用於本專案的 ACP 架構。這是「概念可用、具體實作建議不可用」的典型案例，取用外部建議時要分開評估這兩層。

## 連動的環境變更（與 persona 無關但同時做）

使用者移除全域 `@zed-industries/codex-acp@0.15.0`、安裝 `@agentclientprotocol/codex-acp@1.6.0`。舊版經實測已不可用（prompt 被 API 打回 400 錯誤，訊息指出需要更新版本的 Codex）。此更換獨立於 persona 功能，但在同一輪工作中一併處理。

## 相關

- [[bridge-project]] — preamble 凍結快照政策、bridge 整體架構
- [[bridge-acp]] — ACP adapter 能力矩陣（`_meta.systemPrompt` 通道與各 backend 支援差異的根源）
- [[bridge-dream]] — `/dream` 夜間維運框架（Stage 1 隔離的對象）
- [[adversarial-review]] — persona Stage 1 的跨 vendor 覆核（11 輪同源覆核判 READY、換 vendor 一輪抓到兩條 Critical 的實例，見該頁「輪數不能替代 vendor 多樣性」節）
- [[gate-mutation-testing]] — 突變測試通用判準（本頁「測試與驗證紀律教訓」節的完整技術細節）
