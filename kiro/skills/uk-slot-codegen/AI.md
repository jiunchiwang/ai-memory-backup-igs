# UK Slot Codegen Context

## 完成邊界

- 標準 codegen 是無頭流程：Pre-A 到 Step 5 Report。
- 分身不啟動、不等待、不呼叫 Cocos Editor / Preview。
- Step 5 先跑 `prefinalize`、產生 report，再跑 `finalize`。只有 finalize `all_pass=true` 才能清 checkpoint。
- TypeScript diagnostics、proto contract、regression FAIL/SKIP、codegen-owned traceability evidence 缺失、report schema 是 blocker；inferred defaults、deferred M2+ 與 Editor 驗證不是 blocker。

## 唯一契約

- Audio 一律使用 `AudioManager.AudioClips`。
- Tumble = `.dropEntry + SpinMode.Tumble + TumbleFillStrategy + DropEntryStrategy`。
- Proto 消費端只 import `./Proto`；只有 `Proto.ts` import `./Test/<ns>Proto.js`。
- Symbol client 契約只包含非 `server_only` SymID；server-only 只留在 Summary／protocol，不計入 `Game_Define.Symbol`、`SYMBOL_COUNT`、prefab 或 PNG。
- Regression 必須接受 markdown bold、`x/×`、同列 MG/FG 多模式 BoardLayout，以及 `Array.from({ length: Game_Define.COL })` 動態欄位。
- Step 4a 編譯前執行 `ensure_ts_bom.py`，自動補 codegen-owned TypeScript 的 UTF-8 BOM。
- Extensions repo 存在時 `git pull --ff-only`，不存在時 clone，非 git 目錄停止。

## 報告契約

`scratch/codegen-report.md` 必須有：

- `## 無頭階段完成項目`
- `## Gate 結果`
- `## 後續未完成工項`（使用 `- [ ]`，列原因、目標與驗收）
- `## 已知風險`

Traceability 由 `scratch/codegen-traceability.json` 提供 machine-readable 證據。報告 Gate 結果必須列 `codegen X/Y`、`inferred defaults A/B verified` 與 `deferred M2+ N`；M2+ 項目轉入後續未完成工項。Spec ID prefix 僅是歷史 chapter 編號，scope 依 section、欄位語意與 provenance 判定；行內 `[SPEC]` 註解不能取代數值比對。`SymbolWidth/Height`、`SeparateLineWidth`、`MIDDLE_PLATE_INDEX` 預設是 codegen inferred，除非原始資料明載並標記 `[SOURCE:xlsx]`。

後續工項至少覆蓋 Runtime/Preview、Prefab/Spine 綁定、美術音效替換與未實作的 game-specific features。

## 驗證

修改流程後，用 `rg` 掃描 `editor_ping|scene_open|preview_start|Step 4b|Editor offline`，確認沒有舊的 Editor 必跑規則。
