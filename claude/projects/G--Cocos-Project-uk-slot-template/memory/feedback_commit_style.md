---
name: feedback-commit-style
description: 使用者偏好每個重構步驟單獨 commit，使用 conventional commit 格式 + 中文標題 + Co-Authored-By。
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ebce2f83-747e-4bca-8821-5e3802f903dc
---

每完成一個邏輯步驟就 commit，不要把多個步驟綁在一起。Commit message 用 conventional commit 格式：

```
<type>(<scope>): 中文標題

詳細說明...
- 第一點
- 第二點

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

常用 type：`feat`、`refactor`、`fix`、`chore`、`docs`。Scope 例如 `slot-reels`、`reel-layout-config`、`fill-strategy`、`game-view`、`skills`。

**Why**：Option 1 重構期間每個 step（抽介面 → 換用法 → 動 plateCount → GameView 整合 → ...）都各自 commit，事後查 bug 或想 revert 部分變更時很方便。使用者明確要求「每步做完都 commit 一次」並驗證後才接著做下一步。也方便我把驗證結果寫進 commit message 留歷史。

**How to apply**：
- 多步驟工作要拆 commit，每個 commit 對應一個「可單獨驗證的進度」
- Commit message 內文寫「為什麼這樣改」與「驗證了什麼」，不只寫 what
- Heredoc 多行格式：`git commit -m "$(cat <<'EOF' ... EOF\n)"` 保險（使用者用 PowerShell 但 Bash tool 可走）
- Co-Authored-By 行用 Claude Opus 4.7 的固定字串
- 若一個步驟改壞要修正，建議新 commit `fix(...)` 而不是 amend 前一個（除非當下沒 push）

延伸：使用者也偏好驗證-導向，每個 step 改完先請使用者到 Cocos Editor 跑 DevTool 驗證，沒問題才 commit。例如重構途中 `feat/fix` 之間穿插「Standard 模式跑得起來」、「DropEntry 切換正確」這類人工驗證 check。
