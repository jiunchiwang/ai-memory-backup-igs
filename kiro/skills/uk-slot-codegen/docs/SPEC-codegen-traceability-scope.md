---
title: UK Slot Codegen Scoped Traceability
created: 2026-07-13
status: completed
---

## Why

現行 traceability 只比較全部 Spec ID 與 TypeScript 註解，導致 codegen 骨架固定顯示 `0/N`，無法區分 codegen 已交付的設定／資產契約與必須留到 M2+ 的 game-specific features。

## Approach

依 Game_Spec section 與 provenance 將需求分成 `codegen`、`inferred`、`deferred`、`informational`，並為 codegen scope 建立 machine-readable evidence manifest。Gate 只阻擋缺少 codegen evidence 的項目；codegen 推定值與 M2+ deferred 誠實列入統計但不阻擋。

## Scope

### P0：Scope 與 Evidence Model

- [x] 解析每個 Spec ID 的 section、文字與 scope — 驗收：基本資訊／Symbol／Audio／盤面為 codegen，特色演出為 deferred，table header 為 informational
- [x] 為 codegen scope 解析可重現的 artifact/gate evidence — 驗收：每個 covered item 至少有一筆 value-checked path evidence；explicit `// [SPEC:*]` 只建立連結，不能掩蓋數值錯誤
- [x] 產生 `scratch/codegen-traceability.json` — 驗收：包含 codegen covered/uncovered、deferred、informational、逐項 evidence 與 mismatch diagnostic

### P1：Gate 與流程整合

- [x] Codegen evidence 缺失改為 blocker，deferred 不阻擋 — 驗收：缺 AudioManager fixture FAIL；只有 deferred 未實作仍 PASS
- [x] 更新 Step 1.5／Step 5、report 契約與 AI.md — 驗收：文件不再指示用全部 `0/N` 當 codegen coverage
- [x] UK917 實跑 — 驗收：輸出 codegen/deferred 分流統計；若 codegen-owned 值不符，準確列出 mismatch，不再以 0/104 這類混合分母誤報

### P2：來源追溯修正

- [x] 將模板補值分成 `inferred default` — 驗收：四個參考表欄位不進 codegen blocker，manifest 保留 origin、verified／needs_review
- [x] 支援 `[SOURCE:xlsx]` 升格 — 驗收：原始 xlsx 明載的 inferred-key 仍是 blocking codegen contract
- [x] 更新 Gate／report／流程文件與 UK917 產物 — 驗收：UK917 不再因 codegen 自己注入的假設值 FAIL

## Out of Scope

- 自動實作 UK917 Custom Features
- Cocos Editor／Preview 驗證
- 將所有 Spec ID 強制寫成 TypeScript 行內註解

## Progress

- 2026-07-13：追查確認 FG-8/FG-9 來自 `_api-ref.md` 範例而非 UK917 xlsx；新增 inferred provenance，避免 gate 將 codegen 自己補的預設值誤稱為規格 mismatch。
- 2026-07-13：UK917 scoped manifest = codegen 74/76、deferred M2+ 23、informational 5；FG-8 診斷為 expected 4 / actual 0，FG-9 診斷為 expected 1 / client value not found。
- 2026-07-13：32 項 unittest 全數通過；新增 explicit ref 不得掩蓋 value mismatch、tag-spec idempotence/header skip 等防回歸測試。
- 2026-07-13：UK917 characterization 發現 `SeparateLineWidth` 與規格不一致，且 `MIDDLE_PLATE_INDEX` 尚無 client evidence；因此驗收改為「正確揭露 scoped mismatch」，不要求在未修改遊戲專案前強行讓 finalize PASS。

- 2026-07-13：確認現行資料流為 `extract_spec_ids/extract_client_ids → gate_traceability → report`；目前沒有 scope 或 artifact evidence model。
