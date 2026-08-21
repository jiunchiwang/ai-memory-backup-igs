---
title: Bridge Upstream Fork 同步與合併衝突處理
type: concept
created: 2026-07-21
updated: 2026-08-16（dream high-priority：fork 獨有功能清單經 git grep upstream/main 逐項複驗全數已在上游，改記「怎麼現算」；f_5a2532+f_493b31 → f_8a9bd7）
sources: [f_8a9bd7, f_d61c50, f_8da350, f_2a93b5, f_a23d83, f_4c12ce, f_ea9657, f_a3f2b2, f_489e55, f_c42db4]
history_sources: [f_e272f0, f_5a2532, f_493b31]
---

# Bridge Upstream Fork 同步與合併衝突處理

> 2026-07-21 從 [[bridge-project]] 與 [[bridge-acp]] 拆出（原本因關鍵字巧合分散在兩處）。涵蓋 [[bridge-project]] 與 upstream（`redkilin/telegram-kiro-bridge`）之間的 fork 同步策略、合併衝突處理原則、以及 push 前的安全網。

## Remote 配置

bridge repo 的 remote：`origin=jiunchiwang/telegram-kiro-bridge`、`upstream=redkilin/telegram-kiro-bridge`，https URL 皆嵌使用者名以避免 Git Credential Manager 帳號視窗混淆。

## 同步策略：merge 而非 rebase

用 `merge`（非 `rebase`）合併 upstream，衝突解決原則是 **upstream 架構為主**。

**⚠️ 2026-08-16：原本掛在這裡的「fork 獨有功能清單」已整份失效。** 該清單把 `/reset clean`、`handleDocUpdate`（`/docupdate`）、`specialist-memory`、`reaction_feedback`、READ-BACK 紀律、`userProfileBlock`、SS（skill search）callback 七項列為「解衝突時必須手動保留」；`git fetch upstream` 後對 `upstream/main` 逐一 `git grep`，七個識別字在上游樹**全部有命中**（`/reset clean` 在 `src/commands/misc.ts:113`、SS callback 在 `src/commands/skillsearch.ts:203`，其餘五項在 `src`/`scripts` 底下的命中檔數與本地完全相同）∴ 它們已不是需要手動保留的對象——與下一段 `efab1ab` 的 port-back 一致。

> 誠實邊界：識別字存在只證明**對應程式碼在上游存在**，不證明兩側實作等價；雙邊都改過的檔案仍照下方原則 2／4「比較兩側完整度、保留較完整的一方」處理，不得機械沿用固定優先權。清單不再維護——需要時對當下的 `upstream/main` 重跑 `git grep` 現算。

2026-07-09：upstream（redkilin）於 `efab1ab` 把 fork 的功能 port 回上游（session/resume、token-policy 等）——之後同步時 fork 獨有功能清單的衝突面大幅縮小，本地獨有 commit 僅剩少數未被 port 的項目。

## 合併衝突處理三原則（實證教訓）

1. **`checkout --theirs/--ours` 陷阱**：這是整檔取代，會洗掉對側已乾淨自動合併的 hunk（combined diff 不顯示乾淨 hunk）。雙邊都有改動的檔案應用 `git merge-file` 三方合併，或 `checkout -m` 恢復衝突標記後只改衝突區，並逐檔 diff 兩側核對無遺失。

2. **假衝突判別（2026-07-15 實證）**：若共同祖先本身意外把未解決的合併標記（conflict markers）烘焙進歷史造成假衝突，應採用清理較完整的一方（不論本地或 upstream），而非機械套用固定優先權；**真正的功能路線分歧**（如同日 Electron 桌面監控視窗開關的取捨）才需要停下來問使用者決定。

3. **結構性衝突慣例（2026-07-16）**：AI.md/README.md 這類「本地已把細節搬到子文件（如 `src/AI.md`、`docs/setup-agents.md`）」vs「upstream 就地擴充原檔內容」的衝突，應保留本地 pointer 結構、把 upstream 新增內容手動補進對應子文件，而非整段改用 upstream 版本。

4. **add/add 假衝突（2026-07-27 實證）**：upstream（redkilin）會選擇性把本 fork 的修正 backport 回去，但**以英文註解重寫並改名識別字**，因此同一份修正在兩邊成為「內容等價但文字不同的新檔」，merge 時表現為 add/add 假衝突而非一般內容衝突。處理原則同原則 2——比較兩側完整度、保留較完整的一方（實測本地測試基建較完整，`check-transient-retry.mjs`、`check-npm-audit.mjs`、`run-smoke-suite.mjs`、`dependency-security.md` 四檔皆以 `git checkout --ours` 保留），而非機械沿用固定優先權。

## Upstream 同步歷程

| 日期 | 內容 |
|---|---|
| 2026-07-13 | merge 進 upstream 的 relay 多 peer 系統（`relay-peers.json` + `src/relayPeers.ts`，commit `fa2b9f4`），取代本地未實際使用的 `RELAY_PEER_USERNAMES`/`resolvePeerUsername` 機制 |
| 2026-07-15 | 一次 merge 19 個上游 commit（Rich Telegram replies 統一、MoA rich replies、psmux 開發啟動器規劃、背景通知修復等）+ 1 個本地 ctx 統計後綴 commit，`691e7f8..0a3c551` 已 push origin/main；同日對 `src/commands/status.ts` 的 Electron 桌面監控視窗路線衝突選擇採用 upstream 版（恢復自動開啟），推翻先前本地移除 Electron 改純 Bot 推送的決定 |
| 2026-07-16 | merge 進 MCP-first action domain 基礎建設（`agent-actions.ts`/`agent-action-runtime.ts`/`agent-action-metrics.ts`/`mcp-actions.ts`）+ skill sync hook 改為 opt-in（postinstall 不再自動設定 `core.hooksPath`）+ legacy action id 消毒修規，main `0a3c551` → `199e30a` 已 push origin/main |

## 參考 upstream 前先查 merge-base（2026-08-06）

查證 fork 修正可能領先 upstream 時，發現 upstream/main 至今仍有 `authRequired = authMethods.length > 0` 誤判與方括號-only 的 effort 後綴 regex（詳見 [[bridge-acp]]），而四個 codex 相關 upstream commit 早已全數在本 fork——直接讀 upstream 程式碼前先跑一次 `git merge-base` 對照，能避免誤判「upstream 有我沒有的東西」而重工。

## Push 前安全網

完成 merge/sync 後、push 到 origin 前，會先派一個**獨立 context 的異源覆核者**檢查合併安全性，確認無誤才 push——避免有問題的合併直接推上遠端。閘門本身不放寬。

⚠️ **2026-08-13 換覆核者**：預設從 Claude Fable 5 改為 `kiro-cli chat --no-interactive --model glm-5 --trust-tools=fs_read`。理由是 Fable 5 是 `anthropic`、與產出者**同源**（只算弱異源）且 3.3x 單價，而 glm-5 是 0.50x 的跨 vendor 強異源——同時更便宜且更強。Fable 5 保留為「跨 vendor 那輪產出明顯偏弱時才補的第二輪」。成本量測與選型判準見 [[adversarial-review-dispatch]]。

這個閘門已在至少 4 個 commit 中實際採用（如 `04cc0bc` 訊息明確標註「Fable5 push 前覆核」），是跨多次 merge 反覆使用的專案慣例、非單次紀錄。

## /sync 指令的結果判定：exit code 為主（2026-08-16 決策，2026-08-21 從 [[bridge-project]] 移來）

`10`→衝突、`11`→型別檢查失敗、`3`→preflight 失敗、`0`→成功。文字輸出只用來補充細節，**不用來判定結果種類**——理由是文字會隨工具版本與語系漂移，exit code 才是穩定契約。

## 分享 repo 給同事：獨立 repo 而非 GitHub Fork 鈕（2026-08-14，2026-08-21 從 [[bridge-project]] 移來）

同事接手時選了「同事自建 private repo 當 origin ＋ 使用者的 repo 當 upstream」而非按 GitHub 的 Fork 鈕。理由：使用者的 repo（`jiunchiwang/telegram-kiro-bridge`）與 upstream（`redkilin/telegram-kiro-bridge`）**皆為 private**（未認證打 GitHub API 兩者皆回 404；403=rate limit、301=改名 ∴ 推論成立），而 private repo 的 fork **綁在母 repo 的存取權限上**——撤存取即失效、也無法獨立轉 public；獨立 repo 沒這問題。

⚠️ GitHub 個人帳號**沒有「唯讀 collaborator」角色**（細粒度角色只有 organization 才有）∴ 把人加成 collaborator 等於給 `main` 寫入權。下游設定流程因此把**廢掉 upstream 的 push URL**（`git remote set-url --push upstream no-push`）當成**必要步驟**而非建議。

設定流程檔在 `scratch/SETUP-downstream-fork.md`（裁決不 commit 進版控、只轉給同事；刻意搬到 `scratch/` 是結構性避免被 `git add -A` 誤掃）。

## 相關

- [[bridge-project]] — Bridge 本體架構與功能
- [[bridge-acp]] — ACP adapter 與 model 配置
