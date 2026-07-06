---
name: confirm-before-commit
description: commit 前須先列出步驟給使用者確認、同意後才執行
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9915621a-5e0b-41fe-b236-6b3c033a4ec0
---

執行 `git commit` 前，先把打算做的步驟（要 commit 哪些檔案、commit message、是否開分支等）列給使用者確認，等使用者明確同意後才真正 commit。不要逕自提交。

**Why:** 使用者要對進入版控的內容有最後把關權；先前曾發生我自行決定要開分支（套用全域 RULES.md「Feature Branches Only」）而與本專案直接 commit 到 main 的實證慣例衝突。

**How to apply:** 收到 commit 指令 → 列出 staged 檔案清單 + 預計 commit message + 分支策略 → 等使用者點頭 → 才執行。另注意本專案慣例為直接 commit 到 `main`、不開 feature 分支（遇通用規則 vs 專案實證衝突時，專案實證優先）。
