---
name: steering-corpus-types
description: The 3 canonical steering docs are mixed-type (always-on vs reference) — matters for any inject-vs-index decision
metadata: 
  node_type: memory
  type: reference
  originSessionId: c36322a2-44e4-41f6-91e6-da525f9fcdac
---

正本 `G:\AI\AI-canonical\steering\` 三份 steering 不是同一種注入需求，混合型語料 —— 任何「要不要塞進 prefix」的決策都要分開判斷，不能一視同仁:

- `task-acknowledgement.md`（354B）— **always-on 行為**：每個任務先輸出 🟠收到/🟠打算，「所有任務一律觸發，無例外」。必須進 prefix，不能交給 agent 自由裁量。
- `closed-loop-system.md`（4.9KB）— **always-on 系統提示**：繁中設定 + 閉環方法論 trade-off。always-on 但很大（全文常駐 ~1200 tok/session）。
- `skill-workflow.md`（1.7KB）— **相關時才查**：只在新增/修改 skill 時有用。適合純 index（列標題+路徑，agent 按需 read）。

含意:若哪天真要在 bridge 層注入 steering，正確做法是 frontmatter 驅動的 hybrid（`inject: always` 全文塞 / `inject: index` 列索引），而非統一用「index-only」方案。但現行 Kiro 配對下不需要做，見 [[bridge-steering-integration]]。

steering 投影機制是 **copy 非 junction**（`sync.ps1` 對 steering 只 `Copy-Item -Filter *.md`），所以投影目錄會累積非正本內容（曾有走失的 `ui-ux-pro-max/` skill 目錄殘留在 `~/.kiro/steering/`，2026-06-22 已清）。改正本後要手動 `sync.ps1 -Apply`，不像 skills junction 即時生效。
