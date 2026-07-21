---
title: Bridge Upstream Fork 同步與合併衝突處理
type: concept
created: 2026-07-21
updated: 2026-07-21
sources: [f_5a2532, f_d61c50, f_493b31, f_8da350, f_2a93b5, f_f144ad, f_90a25d, f_a23d83, f_4c12ce, f_a1ecf7, f_ea9657, f_e272f0]
---

# Bridge Upstream Fork 同步與合併衝突處理

> 2026-07-21 從 [[bridge-project]] 與 [[bridge-acp]] 拆出（原本因關鍵字巧合分散在兩處）。涵蓋 [[bridge-project]] 與 upstream（`redkilin/telegram-kiro-bridge`）之間的 fork 同步策略、合併衝突處理原則、以及 push 前的安全網。

## Remote 配置

bridge repo 的 remote：`origin=jiunchiwang/telegram-kiro-bridge`、`upstream=redkilin/telegram-kiro-bridge`，https URL 皆嵌使用者名以避免 Git Credential Manager 帳號視窗混淆。

## 同步策略：merge 而非 rebase

用 `merge`（非 `rebase`）合併 upstream，衝突解決原則是 **upstream 架構為主、手動保留 fork 獨有功能**。

**Fork 獨有功能清單**（同步 upstream 解衝突時必須保留）：
- `/reset clean`
- `handleDocUpdate`（`/docupdate`）
- `specialist-memory`
- `reaction_feedback`
- READ-BACK 紀律
- `userProfileBlock`
- SS（skill search）callback

2026-07-09：upstream（redkilin）於 `efab1ab` 把 fork 的功能 port 回上游（session/resume、token-policy 等）——之後同步時 fork 獨有功能清單的衝突面大幅縮小，本地獨有 commit 僅剩少數未被 port 的項目。

## 合併衝突處理三原則（實證教訓）

1. **`checkout --theirs/--ours` 陷阱**：這是整檔取代，會洗掉對側已乾淨自動合併的 hunk（combined diff 不顯示乾淨 hunk）。雙邊都有改動的檔案應用 `git merge-file` 三方合併，或 `checkout -m` 恢復衝突標記後只改衝突區，並逐檔 diff 兩側核對無遺失。

2. **假衝突判別（2026-07-15 實證）**：若共同祖先本身意外把未解決的合併標記（conflict markers）烘焙進歷史造成假衝突，應採用清理較完整的一方（不論本地或 upstream），而非機械套用固定優先權；**真正的功能路線分歧**（如同日 Electron 桌面監控視窗開關的取捨）才需要停下來問使用者決定。

3. **結構性衝突慣例（2026-07-16）**：AI.md/README.md 這類「本地已把細節搬到子文件（如 `src/AI.md`、`docs/setup-agents.md`）」vs「upstream 就地擴充原檔內容」的衝突，應保留本地 pointer 結構、把 upstream 新增內容手動補進對應子文件，而非整段改用 upstream 版本。

## Upstream 同步歷程

| 日期 | 內容 |
|---|---|
| 2026-07-13 | merge 進 upstream 的 relay 多 peer 系統（`relay-peers.json` + `src/relayPeers.ts`，commit `fa2b9f4`），取代本地未實際使用的 `RELAY_PEER_USERNAMES`/`resolvePeerUsername` 機制 |
| 2026-07-15 | 一次 merge 19 個上游 commit（Rich Telegram replies 統一、MoA rich replies、psmux 開發啟動器規劃、背景通知修復等）+ 1 個本地 ctx 統計後綴 commit，`691e7f8..0a3c551` 已 push origin/main；同日對 `src/commands/status.ts` 的 Electron 桌面監控視窗路線衝突選擇採用 upstream 版（恢復自動開啟），推翻先前本地移除 Electron 改純 Bot 推送的決定 |
| 2026-07-16 | merge 進 MCP-first action domain 基礎建設（`agent-actions.ts`/`agent-action-runtime.ts`/`agent-action-metrics.ts`/`mcp-actions.ts`）+ skill sync hook 改為 opt-in（postinstall 不再自動設定 `core.hooksPath`）+ legacy action id 消毒修規，main `0a3c551` → `199e30a` 已 push origin/main |

## Push 前安全網

完成 merge/sync 後、push 到 origin 前，會先派一個獨立的 Claude Fable 5 agent 覆核合併安全性，確認無誤才 push——避免有問題的合併直接推上遠端。

## 相關

- [[bridge-project]] — Bridge 本體架構與功能
- [[bridge-acp]] — ACP adapter 與 model 配置
