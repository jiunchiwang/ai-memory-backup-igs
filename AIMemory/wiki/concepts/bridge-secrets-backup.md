---
title: Bridge 備份與密鑰洩漏防護（/backup、/sharedsync）
type: concept
created: 2026-07-11
updated: 2026-08-17
sources: [f_f44d46, f_28e17b, f_b21c3a, f_de7bc7, f_dff56f, f_cd57ae, f_a4eb9f, f_cba34c, f_b8922f, f_212e36, f_95d4e4, f_4e0d9d]
history_sources: [f_810445]
---

# Bridge 備份與密鑰洩漏防護

[[bridge-project]] 的 `/backup` 把 AIMemory 自動 commit + push 到私有 repo，`/sharedsync` 另外同步共享知識庫；兩者都曾因為診斷檔或使用者貼的真實密鑰意外落地版控而需要修復。

## acp-trace 洩漏（已修）

- `/backup` 的 excludeDirs 原本只排除 `transcripts/shared`，未排除 `acp-trace`（`ACP_TRACE=1` 時的 JSON-RPC debug trace，可能含完整對話內容），導致 2026-07-09 起至少 5 次 `/backup` 自動 push 把診斷檔帶進 `ai-memory-backup-igs`；已修正 excludeDirs 加入 `acp-trace`（commit `691e7f8`）
- 使用者對已誤進版控的診斷資料選擇的處理方式：只做 `git rm --cached` 移除追蹤 + 加 `.gitignore` 防再犯，不做 `git filter-repo` 歷史清除、不 force-push，接受舊 commit 歷史仍保留內容

## GitHub PAT 洩漏（已修）

- 2026-07-19：使用者先前貼在對話的 GitHub PAT（`ghp_` token）洩漏進 `AIMemory/events.jsonl` 與 oldSessions 的 session transcript，觸發 GitHub push protection 擋下 `/backup`；教訓是對話中貼的真實密鑰會落地 `events.jsonl` 與 transcript，不應在對話貼 token
- **自我重複污染迴圈**：bridge session 會把每個 bash 指令逐字記進 `events.jsonl`（含指令參數本身），若用 grep 打出洩漏 secret 的字面值來驗證是否清乾淨，該驗證指令本身又把 secret 重新記回 `events.jsonl`；解法是改用通用正則（如 `ghp_[A-Za-z0-9]{30,40}`）取代逐字打出 secret 本身來搜尋/驗證
- **未推送 commit 的清理技巧**：若含 secret 的 commit 尚未推送到遠端（push protection 已在推送前擋下），可安全用 `git commit --amend` 改寫該 commit 內容移除 secret，再用 `git reflog expire --expire=now --expire-unreachable=now --all` + `git gc --prune=now` 徹底清除本地磁碟上的殘留 commit 物件

## /sharedsync 與跨帳號 Credential 快取

- 使用者主機（jiunchiwang）的 Windows Credential Manager 對 GitHub 快取兩組不同帳號憑證：generic `https://github.com` 對應 `igs-jiunchiwang`、`https://jiunchiwang@github.com` 對應 `jiunchiwang`；跨帳號 git 操作需注意 remote URL 要嵌對帳號名才能配對到正確快取憑證
- 已建立新的 GitHub private repo `jiunchiwang/ai-shared-knowledge`，接上本機 `G:\AI\AIMemory\shared\` 供 `/sharedsync` 使用（取代先前誤以為要接的 upstream 作者 redkilin 私人 repo）

## default-skills 自動回填

- `default-skills/` 目錄由 `.githooks/pre-commit` 呼叫 `scripts/sync-skills-to-repo.mjs` 在每次 commit 自動從本機 skill 目錄回填，因此 AI-canonical 的 skill 改動會自己流進 repo 副本，不需手動 cp 維護——commit 時看到 `[sync-skills] N skill(s) updated` 即代表機制生效；也代表「default-skills 是過期舊副本」這類 finding 會在下次任何 commit 自動消失

## Git 歷史 Secret 掃描結果（2026-08-14）

對 telegram-kiro-bridge 1005 commit 全掃（`--all`）結果：

- `.env` **從未進版控**
- 無任何 `*.pem`、`*.key`、`credential*`、`token.json`、`client_secret*` 曾被新增
- `ghp_`/`github_pat_`/`sk-ant-`/`AKIA`/`xoxb-`/Telegram bot token 形狀皆有命中，但逐條查證**全為 redaction 正則、文件表格或測試 fixture**（`AKIAIOSFODNN7EXAMPLE`、`sk-ant-...` 佔位符等）

⚠️ **只涵蓋固定前綴**，無熵值分析 ∴ 下游 repo 預設 private，**要轉 public 前須跑 gitleaks/trufflehog**。

## Zip 打包分享的陷阱

把 repo 直接打包成 zip 分享會連 **untracked 的 `.env`**（含 `TELEGRAM_BOT_TOKEN`）、`logs/`、`.claude/`、`.github/` 一起送出——這比 git 歷史洩漏更實際（git 只會包含 tracked 檔案）。

額外風險：**兩個 bridge 共用同一個 bot token** 長輪詢會互搶 `getUpdates` 導致 Telegram 回 409 Conflict、兩邊都不穩 ∴ 下游**必須換自己的 token**。

## 相關

- [[bridge-project]] — Bridge 本體架構
- [[bridge-memory]] — AIMemory 結構與 /backup 排除規則
- [[bridge-upstream-sync]] — git 帳號/憑證相關的另一類坑（push 卡住）
