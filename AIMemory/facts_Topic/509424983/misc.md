- [f_48fdd8] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 B 區（規格書結構）決策：寫常見模式而非固定規範（因為每案 sheet 命名不同）
- [f_b0c1d8] [2026-08-13T03:00:58.319Z] 使用者的公司內部 AIBI 平台有一台 MCP server rockmanx4-aibi（Streamable HTTP，https://ai-gw-02.i17game.net/rockmanx4/mcp，Bearer token 認證），提供 SkillHub 技能庫／AI 採購用量／團膳菜單／員工通訊錄／平台公告；2026-08-13 嘗試加入時 claude mcp add 被 Claude Code auto mode classifier 擋下，尚未加成
- [f_271855] [2026-08-14T20:08:54.910Z] iGaming Mend 掃描導入時，使用者選了沿用附件文件中已外流的既有 Mend User Key，排除撤銷重發——理由是「目前那把就是配發給我用的 Key」，非帳號本身有問題只是文件外流；assistant 已明確 push back 建議撤銷重發，使用者知情後仍裁決沿用。2026-08-14。
**tool search 的實際貢獻（`ENABLE_TOOL_SEARCH=false` 對照臂）**：關掉後全開 114,923、strict-mcp 101,090 ∴ MCP schema 全載也只有 13,833；而兩個「都沒有 MCP」的臂相差 13,926 ⇒ **deferral 也 defer 內建工具（WebFetch/Task/Cron…），不只 MCP**。deferral 共省 26,776（非деferred prefix 的 23.3%），其中僅約一半來自 MCP。
**第二個乘數仍成立（未重測）**：每輪重送全部 context——2026-07-29 那輪 Fable 覆核 85 個請求、context 從 90,218 長到 185,549、累計送進 12,724,628 vs output 156,050（81:1）。⚠️ 12.7M 是原始傳輸量非成本當量（cache_read 0.1x；cache_write 1h TTL 2x／5m TTL 1.25x，訂閱制預設 1h）。
**可遷移判準**：任何「用註解語法停用設定」的做法，都要先確認那個檔格式**真的有註解語法**——Markdown、JSON 都沒有。
- [f_d682b4] [2026-08-20T15:20:43.009Z] 逐 task 覆核會把缺陷推到沒人被指派的最外層：每輪覆核恪守自己的 brief 是對的，但沒有人擁有 task 之間的接縫，修正一律修在該 task 層內、未受測邊界每修一次外移一格；全分支覆核必做，且要求它真的改一個 token 看功能能不能被靜默關掉
- [f_88faeb] [2026-08-20T15:20:43.009Z] 對「加了一個 skip 旗標」這類修法要追問「這條路徑上這個旗標之前還有誰會動手」——旗標只保護它自己那一行的 if；對「用 chatId 去重」的 cache／pending map 要追問「去重時把 opts 丟掉了嗎」
