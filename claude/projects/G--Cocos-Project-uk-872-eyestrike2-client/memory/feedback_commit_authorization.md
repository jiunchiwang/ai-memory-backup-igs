---
name: feedback-commit-authorization
description: 閉環完成後不要自動 commit，須等使用者明確指示才 commit
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d551cfb6-98fc-4083-83a4-e232c0eea539
---

閉環（精簡閉環迷你追溯通過後 / 完整閉環 Phase 5 通過後）禁止自動 commit。即使 CLAUDE.md 工作規範寫「自證通過後 commit」、精簡閉環步驟列「commit」為自動步驟，仍須改為**報告完成狀態 + 列出待 commit 檔案 + 等使用者指示**。

**Why**：使用者要保留 commit 決策權，方法論的「commit」步驟對此 project 應降級為「準備好 commit material 等指示」。違反此規則 → 違反系統 prompt「NEVER commit unless explicitly asked」原則，使用者已明確表態。

**How to apply**：
- 閉環走完後輸出總結 + 列出已 staged / 待 staged 檔案清單
- 提示「請決定是否 commit / 修改 message / 拆 commit」
- 使用者說「commit」「commit 吧」「OK 提交」等明確授權 → 才執行 git commit
- 使用者說「先別 commit」「我自己來」「等等」→ 不動
- 即使是「跑精簡閉環」「跑完整閉環」這類 workflow 觸發詞，commit 步驟仍須等明確授權（workflow 授權 ≠ commit 授權，scope 不擴張）

**邊界**：
- 「commit 並 push」「直接 commit」這類使用者主動指令 → 視為明確授權，正常執行
- learning-log / 問題追蹤升降級 / artifact 寫入仍可自動執行（這些是閉環產出物，不涉及版控決策）

**相關**：閉環方法論詳見 [[../G--Cocos-Project-uk-872-eyestrike2-client/CLAUDE.md]]「迷你追溯通過後」section
