# claude-mem shortlist (高價值候選,英文待精選)
> 產生:2026-08-11T20:30:25.243Z;筆數:10(上限 15);自 epoch 1786338503767
> 給 AI:精選真正「跨 session 可重用」的 → 翻繁中 → 用 memory search 去重 → 提案 ≤10。一次性步驟略過。

- (decision|telegram-kiro-bridge-main|2026-08-11) Sonnet-4.6[max] vs Opus-4.5 bug-finding capability verdict: inconclusive at n=5, shared model ceiling identified :: Sonnet-4.6[max]: 2/5 correct hits, 3 false positives, 12-31s latency per task
- (decision|telegram-kiro-bridge-main|2026-08-11) No runtime warning added for Kiro effort no-op behavior :: Kiro CLI accepts --effort flag for all models but only claude-sonnet-4.6 actually uses it
- (decision|telegram-kiro-bridge-main|2026-08-11) Pre-push review approved commit 9897f46 for Kiro effort handling without runtime warnings :: Commit 9897f46 modifies ACP_EFFORT configuration and documentation for Kiro adapter in telegram-kiro-bridge
- (decision|telegram-kiro-bridge-main|2026-08-11) Pre-push commit verification workflow for 9897f46 :: Commit 9897f46 adds Kiro effort domain explanation to scripts/AI.md and extends ACP_EFFORT_FALLBACK.kiro to include 'max' value in src/configRegistry.ts
- (decision|telegram-kiro-bridge-main|2026-08-11) Pre-Push Independent Review Initiated for Kiro Effort Commit :: parallel_delegate launched with ID parallel_delegate_793cac0ae7954fde869ef3091326f0cf to review commit 9897f46
- (decision|telegram-kiro-bridge-main|2026-08-11) Removed Invalid Cross-Version Comparison from Memory Document :: Removed "08-10：**死 23 次但 0 個空窗**" comparison from measurement tool section
- (decision|telegram-kiro-bridge-main|2026-08-11) Refined Windows Spawn Bug Analysis with Evidence Grading :: Readiness check uses three-way OR: port probe (Bn) || alive status (qs()) || process check (s > 0 && Ve(s))
- (decision|telegram-kiro-bridge-main|2026-08-11) Disproven hypothesis: disabling chroma does not prevent worker crashes :: Worker 47424 died silently at 19:07 despite chroma being disabled since 18:52
- (decision|uk_872_eyestrike2_client|2026-08-11) Automated backfill monitoring implemented with 40-minute watch window :: Background monitoring task b08kinmni launched to watch for "Backfill check complete for all projects" log marker
- (decision|uk_872_eyestrike2_client|2026-08-11) Local override created to prevent automatic git commits :: Created G:\Cocos_Project\uk_872_eyestrike2_client\CLAUDE.local.md to override project-level CLAUDE.md behavior
