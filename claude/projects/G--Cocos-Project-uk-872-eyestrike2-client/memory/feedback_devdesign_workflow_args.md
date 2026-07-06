---
name: devdesign-workflow-args-concise
description: dev-design/dev-review workflow 的 args 過長會導致 explore agent 窮舉失控
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3986c528-a988-4010-a6db-de3c14947726
---

dev-design / dev-review workflow 的 args 只給「需求 + 已確認事實 + 方向」，**不要列窮舉式的「逐字驗證 / 連帶檢查點清單 / 逐點決策矩陣」**。

**Why:** 2026-06-10 一次 dev-design workflow 的 args 塞了大量逐項檢查清單，explore agent 被逼成「把每一項都 grep/read 驗證一遍」的窮舉迴圈，跑 1.5 小時、966 tool calls 仍不收斂，被迫 TaskStop。正常 explore agent 幾十個 tool call 就該收斂。

**How to apply:** 把詳細的檢查清單留給主 agent 自己（或 inline 流程），workflow args 給高層次脈絡讓 agent 自決探索深度。若 workflow 又卡在單一 phase、tool 數異常爬升（>200），及早 TaskStop，改 inline 或精簡 args 重跑。相關：[[feedback_commit_authorization]]。
