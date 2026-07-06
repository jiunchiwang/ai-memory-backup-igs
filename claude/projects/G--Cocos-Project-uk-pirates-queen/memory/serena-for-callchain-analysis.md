---
name: serena-for-callchain-analysis
description: Section 9 因果鏈分析優先用 Serena find_referencing_symbols 而非 grep；codegraph 評估後判定多餘
metadata: 
  node_type: memory
  type: feedback
  evidence_level: strong
  verified_by_user: false
  originSessionId: 7b0bb281-08b5-4859-bc58-adf75fe7974f
---

做 CLAUDE.md Section 9 因果鏈分析（找呼叫者）時，優先用 Serena 的 `find_referencing_symbols` 取代逐一 grep。

**已驗證事實（A 級，本 session 對 GameView.ts 實測）**：
- Serena LSP 在本專案（Cocos Creator 3.6.2 + TypeScript）正常運作；`get_symbols_overview` 乾淨解出 god-class ~100 方法。
- `find_referencing_symbols(GameView/OnRecvSpinAck)` 跨 3 檔精確抓出呼叫者（WaitResState.ts:36、SpinState.ts:31、GameView.ts:1006），含 file:line、周圍程式碼、以及巢狀 callback 的 symbol 路徑。
- 注意：本專案未在 Serena 註冊，首次用需先 `activate_project` 指向 `G:\Cocos_Project\uk_pirates_queen`（首次 activate 等於順手註冊，之後通常不用再跑）。
- ⚠️ active project 切換風險：Serena 一次只有一個 active project，多專案並用或它記錯時，`find_referencing_symbols` 會在錯的 codebase 上跑。實測 known projects 曾只有其他 slot 專案（uk_722_robinhood_client / uk_739_wrath_of_thunder_client / uk_slot_eye_strike / uk_slot_template），不含本專案。

**推論（中級，codegraph 未實機比對）**：codegraph（github.com/colbymchenry/codegraph）主打的 impact analysis 與 Serena 高度重疊，且它用 tree-sitter（AST 層）理論上對巢狀 callback / structural typing 精度低於 Serena 的 LSP。其框架 route→handler 連結對 Cocos 遊戲專案無用。故判定對本專案多餘 —— 但此結論未實跑 codegraph 驗證。唯一備案情境：若 Serena LSP 索引在大型 session 變慢或 TS language server 常崩，再評估 codegraph 的預建 SQLite+FTS5。

**Why**：grep 只給文字行、分不清定義/呼叫、看不出呼叫點埋在哪層函式或 callback；Serena LSP 給語意結構，更符合 Section 9 要求的「呼叫者逐一分析」深度。
**How to apply**：首改某檔案做因果鏈分析時 →（1）先確認 Serena active project 是當前專案，不是則 `activate_project` 切過去（首次用本專案要先註冊）→（2）再 `find_referencing_symbols`；grep 僅用於 Serena 無法涵蓋的非 symbol 文字搜尋（字串常量、設定 key 等）。
