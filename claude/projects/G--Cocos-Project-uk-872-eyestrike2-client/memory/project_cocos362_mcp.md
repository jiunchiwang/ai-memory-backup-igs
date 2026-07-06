---
name: project-cocos362-mcp
description: 本專案已安裝 cocos362-mcp-server（Cocos 3.6.2 編輯器自動化 MCP），檔案散落在 repo 外
metadata: 
  node_type: memory
  type: project
  originSessionId: 49a5a50a-3ebf-4f02-85c9-470015dddffc
---

本專案（uk_872_eyestrike2_client, Cocos Creator 3.6.2）已安裝 `cocos362-mcp-server`（私有 repo redkilin/cocos362-mcp-server）。架構是兩段式：Node MCP server（stdio）↔ WebSocket :17362 ↔ Cocos 編輯器 extension。

安裝位置（皆不在主 repo 內，故 git 看不到）：
- **MCP server（Node）**：`C:\Users\jiunchiwang\mcp-servers\cocos362-mcp-server`，已 build（`dist/index.js`）。
- **MCP 註冊**：user scope，寫在 `~/.claude.json` 頂層 `mcpServers.cocos362`（`node .../dist/index.js`）→ 所有專案可見。
- **Cocos extension**：`extensions/cocos362-mcp-bridge` 是 **junction**，指向 server repo 的 `cocos-extension/cocos362-mcp-bridge`。`extensions/` 本身是獨立 repo（OLD-RD1/slotExtensions-client）且被主專案 gitignore。

提供 23 個工具（editor_ping / scene_* / node_* / component_* / asset_* / prefab_* / spine_query / preview_*）。使用前提：Cocos 編輯器需開著且 extension 已載入（Develop 選單可見 MCP Bridge: Status）；沒開時工具回 "editor not connected"。更新 server：到安裝目錄 `git pull && npm run build`，extension 端 `npm run build` 後在 Cocos 重載。

⚠️ **`component_set_property` 已知限制（2026-06-16 實測）**：此 bridge 會把 `value` 一律**字串化**，且**設不了元件型別參考**（如 `SpriteChange` 等 Component 欄位）。傳物件 `{refNodeUuid}` 或 `null` 都會被存成字面字串（污染欄位），回傳仍 `ok:true`（假陽性）。∴ 元件參考類接線一律在 editor 手動拖；用此工具設值後**務必存檔→讀 prefab 檔比對**驗證（正確序列化是 `{ "__id__": N }`，非字串）。Node/Vec3/primitive 是否可靠未完整實測。要編輯 prefab 內節點需先在編輯器雙擊進 prefab-edit 模式（否則節點不在開啟場景樹中）。
