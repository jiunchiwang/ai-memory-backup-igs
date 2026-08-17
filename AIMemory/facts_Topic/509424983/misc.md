- [f_10fbe3] [2026-07-13T03:23:05.711Z] 使用者的公司網路環境封鎖 QUIC 協定導致 cloudflared quick tunnel 無法取得 URL（卡在 Requesting new quick Tunnel 超過 35 秒無回應）；ngrok（走 TLS 443）是驗證過的可行替代但最終選擇不用 tunnel
- [f_48fdd8] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 B 區（規格書結構）決策：寫常見模式而非固定規範（因為每案 sheet 命名不同）
- [f_b0c1d8] [2026-08-13T03:00:58.319Z] 使用者的公司內部 AIBI 平台有一台 MCP server rockmanx4-aibi（Streamable HTTP，https://ai-gw-02.i17game.net/rockmanx4/mcp，Bearer token 認證），提供 SkillHub 技能庫／AI 採購用量／團膳菜單／員工通訊錄／平台公告；2026-08-13 嘗試加入時 claude mcp add 被 Claude Code auto mode classifier 擋下，尚未加成
- [f_271855] [2026-08-14T20:08:54.910Z] iGaming Mend 掃描導入時，使用者選了沿用附件文件中已外流的既有 Mend User Key，排除撤銷重發——理由是「目前那把就是配發給我用的 Key」，非帳號本身有問題只是文件外流；assistant 已明確 push back 建議撤銷重發，使用者知情後仍裁決沿用。2026-08-14。
**tool search 的實際貢獻（`ENABLE_TOOL_SEARCH=false` 對照臂）**：關掉後全開 114,923、strict-mcp 101,090 ∴ MCP schema 全載也只有 13,833；而兩個「都沒有 MCP」的臂相差 13,926 ⇒ **deferral 也 defer 內建工具（WebFetch/Task/Cron…），不只 MCP**。deferral 共省 26,776（非деferred prefix 的 23.3%），其中僅約一半來自 MCP。
**第二個乘數仍成立（未重測）**：每輪重送全部 context——2026-07-29 那輪 Fable 覆核 85 個請求、context 從 90,218 長到 185,549、累計送進 12,724,628 vs output 156,050（81:1）。⚠️ 12.7M 是原始傳輸量非成本當量（cache_read 0.1x；cache_write 1h TTL 2x／5m TTL 1.25x，訂閱制預設 1h）。
⚠️ **仍未驗證**：把 import 路徑包進 code block 能不能讓 parser 跳過——確定有效的只有拿掉 `@` 字元本身。⚠️ 生效時機：CLAUDE.md 在 session 啟動時讀入並持有，mid-session 編輯不會生效也不會打掉快取，要下一次 `/clear`／`/compact`／重啟才載入新版。
**可遷移判準**：任何「用註解語法停用設定」的做法，都要先確認那個檔格式**真的有註解語法**——Markdown、JSON 都沒有。
