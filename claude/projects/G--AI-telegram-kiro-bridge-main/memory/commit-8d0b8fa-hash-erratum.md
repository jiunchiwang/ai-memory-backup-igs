---
name: commit-8d0b8fa-hash-erratum
description: commit 8d0b8fa 訊息內引用的 hash 筆誤勘誤（173881a → 正確為 173591a），程式碼不受影響
metadata: 
  node_type: memory
  type: project
  originSessionId: 63726a55-88ee-42f8-b270-e24d589a204a
---

telegram-kiro-bridge 的 commit `8d0b8fa`（updateJson compare-and-delete + CONTINUE opener + tool-hooks 文件殘留清理）的 commit body 引用「原修正」的 hash 打錯：寫成 `173881a`，正確是 `173591a`（writePending map compare-and-delete 那個 commit）。

**影響**：僅 commit 訊息內的參照筆誤，程式碼完全正確。已決定**不 amend**（不值得改寫歷史）。

**用途**：日後追溯 8d0b8fa 的因果鏈時，看到 173881a 找不到 commit 不要慌，對象就是 `173591a`。
