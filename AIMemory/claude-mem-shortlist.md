# claude-mem shortlist (高價值候選,英文待精選)
> 產生:2026-08-14T20:30:03.245Z;筆數:15(上限 15);自 epoch 1786623206724
> 給 AI:精選真正「跨 session 可重用」的 → 翻繁中 → 用 memory search 去重 → 提案 ≤10。一次性步驟略過。

- (decision|telegram-kiro-bridge-main|2026-08-14) Two high-priority replay safety issues documented but deferred for separate design work :: ACP entire-turn prompt replay retries whole turn including tool side effects when adapter connection fails
- (decision|telegram-kiro-bridge-main|2026-08-14) Documented planUncertainReplay limitation instead of implementing recursive splitting :: planUncertainReplay assumes input text does not exceed limit parameter
- (decision|telegram-kiro-bridge-main|2026-08-14) Cross-vendor adversarial review process for telegram retry fixes :: Review uses adversarial framing telling reviewer their value is in refuting claims not agreeing
- (decision|telegram-kiro-bridge-main|2026-08-14) Explicit uncertainty marking for transport-layer retry messages :: pendingMessages array now includes `uncertain: boolean` field alongside chatId and text
- (decision|telegram-kiro-bridge-main|2026-08-14) Launched cross-vendor adversarial review for commit validation :: Created adversarial review prompt in scratch/review-prompt-ff976f6.txt (2555 bytes)
- (decision|telegram-kiro-bridge-main|2026-08-14) Adopted idempotency-based retry strategy for Telegram API calls :: Retry guard logic borrowed from cloudflare/cloudflare-os callMayHaveTakenEffect() pattern
- (decision|telegram-kiro-bridge-main|2026-08-14) Corrected Transformer Order Criticality After Testing :: Initial documentation claimed guard installation before autoRetry causes silent total failure
- (decision|telegram-kiro-bridge-main|2026-08-14) User asked to choose fix scope for unbounded retry and resume issues :: ASK submitted with id "cfos_b1fix" offering 4 implementation options
- (decision|telegram-kiro-bridge-main|2026-08-14) Cloudflare OS research completed and presented to user for absorption decision :: Wiki index.md cloudflare-os entry updated from research-in-progress to Step 2-3 complete with source verification
- (decision|telegram-kiro-bridge-main|2026-08-14) Cloudflare OS absorption evaluation completed with two recommended patterns and two rejected :: Four borrowable patterns identified after filtering already-have and don't-need items
- (decision|uk_slot_clash_of_olympus|2026-08-14) VS multiplier rendering uses BitmapFont instead of static art :: VS multiplier display format finalized as `NX` (number first, X second, e.g., `2X` for ×2)
- (decision|uk_slot_clash_of_olympus|2026-08-14) Game resource reuse policy and wrath_of_thunder heritage :: Amount numbers cannot use substitutes or reference other games like eye_strike2
- (decision|uk_slot_clash_of_olympus|2026-08-14) GAP-04 resolved: multiplier uses "NX" format with BitmapFont dynamic composition :: GAP-04 spec gap resolved on 2026-08-14 via director's verbal response, replacing temporary placeholder
- (decision|uk_slot_clash_of_olympus|2026-08-14) Dynamic multiplier display uses text rendering :: Multiplier values are displayed in format like "2X", "3X"
- (decision|telegram-kiro-bridge-main|2026-08-14) Fork-based collaboration workflow for telegram-kiro-bridge :: telegram-kiro-bridge is being shared with a colleague who has completed installation
