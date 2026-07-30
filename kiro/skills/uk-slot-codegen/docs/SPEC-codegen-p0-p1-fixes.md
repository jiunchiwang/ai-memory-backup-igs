---
title: UK Slot Codegen P0/P1 契約與 Gate 修正
created: 2026-07-13
status: done
---

## Why

Codegen 文件、Gate 與 template 實際 API 不一致，造成 AudioClips / Tumble 產錯碼，並允許 regression SKIP、traceability 失敗時仍清除 checkpoint。

## Approach

先將 template 實際 API 定為唯一契約，再把 compile、regression、traceability 與 report schema 集中到 finalize Gate。補齊 new/update/validate 及 xlsx/markdown 分流，最後用單元測試與 UK917 實際專案驗證。

## Scope

### P0：唯一 API 契約

- [x] 統一 AudioClips 為 `AudioManager.AudioClips` — 驗收：執行文件不再指示產生 `Game_Define.AudioClips`
- [x] 統一 Tumble 為 `SpinMode.Tumble + TumbleFillStrategy + DropEntryStrategy` — 驗收：SKILL/API/Gate 無 Cascade 誤判
- [x] 統一 Proto.ts 間接點、`<ns>Proto.js` 命名與工具用途 — 驗收：Step 3.3 無相互覆蓋步驟

### P0：完成 Gate

- [x] 新增 finalize/report schema 結構化 Gate — 驗收：必要檢查失敗時 exit 1，不得清 checkpoint
- [x] regression 必要資料 `SKIP` 視為失敗 — 驗收：缺 Symbol/Board/NORMAL_COLUMNS 的 fixture exit 1
- [x] compile blocker 範圍納入 `assets/game/Script` — 驗收：該路徑 TS error 被分類為 owned
- [x] Symbol regression 排除 `server_only` 並比對 client SymID 集合 — 驗收：UK917 client 0~24 PASS、server-only 25~27 明確列為 excluded，真正缺少的 client SymID 仍 FAIL
- [x] 支援 markdown bold、Unicode `×` 與 MG/FG 多模式 BoardLayout — 驗收：UK917 3×5／5×5 layout PASS，真正 per-column 不規則盤面仍要求 mask array
- [x] 支援由 `Game_Define.COL` 動態產生的 NORMAL_COLUMNS — 驗收：UK917 不再 SKIP
- [x] 新增 `ensure_ts_bom.py` 並接入 Step 4a — 驗收：缺 BOM 自動補齊、重跑不重複、非 UTF-8 停止

### P1：模式與流程分流

- [x] 明確 new/update/validate 步驟矩陣 與 xlsx/markdown ingestion — 驗收：validate 不寫生成檔，markdown 有確定輸出
- [x] Extensions 存在時 pull、不存在時 clone — 驗收：new/update 不會對既有目錄 clone
- [x] traceability 改為可誠實回報的 advisory 結果 — 驗收：未覆蓋列 WARN 且寫入 report，不假稱 PASS
- [x] 同步 `_flow.md` / `_gates.md` / `_api-ref.md` / `SKILL.md` — 驗收：rg 無已知 P0/P1 矛盾

## Out of Scope

- Cocos Editor / Preview 自動化
- P2 文件整理（Spine placeholder 歷史敘述、人工檢查點語意）
- 更動 UK917 專案遊戲碼

## Progress

- 2026-07-13：完成 audit 與因果鏈盤點；現行單元測試 8/8 PASS，但尚未覆蓋 finalize 與契約一致性。
- 2026-07-13：P0/P1 實作完成；17 tests PASS。UK917 實跑證明 regression FAIL/SKIP 會阻擋、traceability 0% 會標 WARN、enum 註解不再造成假陽性。等待使用者驗收後改 status=done。
- 2026-07-13：修正 Symbol regression 將規格總列數誤當 client count 的問題；新增 3 個行為測試與文件契約測試。UK917 正確判定 client IDs 0~24 PASS，server-only IDs 25~27 excluded。
- 2026-07-13：補齊 regression 的 markdown bold／Unicode 多模式 BoardLayout／dynamic NORMAL_COLUMNS 支援，並加入 TypeScript BOM 自動修復。UK917 四項 regression 全 PASS。
- 2026-07-13：26 tests PASS；UK917 prefinalize/finalize `all_pass=true`。P0/P1 修正完成。
