# claude-mem shortlist (高價值候選,英文待精選)
> 產生:2026-08-02T20:30:08.729Z;筆數:8(上限 15);自 epoch 1785570559110
> 給 AI:精選真正「跨 session 可重用」的 → 翻繁中 → 用 memory search 去重 → 提案 ≤10。一次性步驟略過。

- (decision|telegram-kiro-bridge-main|2026-08-02) Cost-tiered reviewer selection for cross-model adversarial review :: Cross-model adversarial review skill updated with cost-based reviewer selection strategy at G:\AI\AI-canonical\skills\general\ms-cross-model-adversarial-review\SKILL.md
- (decision|telegram-kiro-bridge-main|2026-08-02) Second adversarial review approved commit 7d4eba8 with 4 low-severity findings :: Round 2 adversarial review used Fable 5 agent with clean context, explicitly instructed not to trust commit message claims
- (decision|telegram-kiro-bridge-main|2026-08-02) Adversarial code review completed for model-switching commit :: Independent Fable 5 agent reviewed commit f986406 (dream.json per-backend model specification) through adversarial lens
- (decision|telegram-kiro-bridge-main|2026-08-02) Dream models uses per-backend explicit restoration to avoid subprocess churn :: Three ACP adapters have different model configuration mechanisms with different persistence scopes
- (decision|telegram-kiro-bridge-main|2026-08-02) Clarified /dream model requirement is per-backend, not provider switching :: User requirement for /dream models field is per-backend model selection, not per-step or provider switching
- (decision|telegram-kiro-bridge-main|2026-08-02) /dream 工作流模型還原策略三選項 :: 方案 A（顯式還原）由 dream 末尾主動切換回原 agent，設為推薦選項
- (decision|telegram-kiro-bridge-main|2026-08-02) Multi-Agent Model Assignment 策略 :: Kiro agent 指定使用 opus-4.5 模型
- (decision|telegram-kiro-bridge-main|2026-08-02) Dream per-step model configuration architecture decision pending :: Decision prompt presented with id=dreammodel asking user to select from 5 options
