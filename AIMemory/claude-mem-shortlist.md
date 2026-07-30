# claude-mem shortlist (高價值候選,英文待精選)
> 產生:2026-07-29T20:30:02.527Z;筆數:4(上限 15);自 epoch 1785243042184
> 給 AI:精選真正「跨 session 可重用」的 → 翻繁中 → 用 memory search 去重 → 提案 ≤10。一次性步驟略過。

- (decision|telegram-kiro-bridge-main|2026-07-29) Pre-push fact-checking review process for documentation updates :: Fable 5 agent invoked to fact-check docs/pending-roadmap.html changes against source wiki files before push
- (decision|telegram-kiro-bridge-main|2026-07-29) Kiro as primary implementation, Codex as fallback :: Kiro designated as the primary implementation target
- (decision|telegram-kiro-bridge-main|2026-07-29) Documented ACP adapter model reporting heterogeneity and verification requirements :: Created acp-model-report-shapes.md memory documenting session/new response differences across three ACP adapters
- (decision|telegram-kiro-bridge-main|2026-07-29) Model identity injection architecture respects preamble-frozen-snapshot policy :: AcpClient tracks actual model/effort in private _sessionConfig field, separate from requested opts.acpModel to handle mismatches
