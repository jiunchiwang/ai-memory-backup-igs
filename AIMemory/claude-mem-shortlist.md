# claude-mem shortlist (高價值候選,英文待精選)
> 產生:2026-08-13T20:30:04.436Z;筆數:15(上限 15);自 epoch 1786526680353
> 給 AI:精選真正「跨 session 可重用」的 → 翻繁中 → 用 memory search 去重 → 提案 ≤10。一次性步驟略過。

- (decision|telegram-kiro-bridge-main|2026-08-13) VSManager M2.2 code review completed with one High finding on server authority violation :: Review submitted structured output with findings, passed items, and risks arrays
- (decision|telegram-kiro-bridge-main|2026-08-13) M2.2 adapter design finalized with critical GameView mock bugs identified :: Design decision: AdaptRoundToVSInput() pure function in VSManager.ts with type-only colProto import to preserve ts-node testability
- (decision|telegram-kiro-bridge-main|2026-08-13) M2.2 VS Feature design review completed: thin adapter pattern with derive-not-persist plateAfter strategy and 6 identified risks :: Design review concluded VsFeatureShowState should be thin adapter: convert proto VSResult → call VSManager.Resolve() → iterate steps for Fly/Expand/Spine演出 → pass results to CollectFeatureShowState via new GameView.VsFeatureResult field
- (decision|telegram-kiro-bridge-main|2026-08-13) M2.2 VS Feature演出 design review initiated for Clash of Olympus :: Task moaplan_lifecycle_review targets uk_slot_clash_of_olympus M2.2 VS Feature implementation review
- (decision|telegram-kiro-bridge-main|2026-08-13) Hang detection threshold intentionally not adjusted despite margin erosion :: Hang detection threshold safety margin dropped from ~2x to ~1.39x after smoke suite increased to 432.1s (7.2 minutes)
- (decision|telegram-kiro-bridge-main|2026-08-13) Second-round semantic merge review initiated after mechanical verification :: First review found 2 verification gaps: incorrect mutation set identification and invalid tsc reasoning for .mjs files
- (decision|telegram-kiro-bridge-main|2026-08-13) VS Collect multiplier changed from compound to additive model :: Original specification suggested VS Collect multipliers would modify all Cash/JP values on the board
- (decision|telegram-kiro-bridge-main|2026-08-13) GAP-11 正式关闭：多个 VS Collect 为相加非连乘，最大赢分降低两个数量级 :: GAP-11（两个 VS Collect 是否连乘）于 2026-08-13 经编导答覆正式关闭，结论为相加非连乘
- (decision|telegram-kiro-bridge-main|2026-08-13) VSManager.Resolve() 演算法完整定案，编导条 7 确定 VS Collect 为收分係数非盘面倍数 :: VSManager.Resolve() 演算法 S4 步骤改为只记录 collectMul[col] = winningMultiplier，不改动任何盘面分数（编导条 7）
- (decision|telegram-kiro-bridge-main|2026-08-13) VS Collect 倍数作用语意确认为改写盘面分数本身 :: 规格 [C79] "VS Collect 的乘倍作用在盘面所有分数上" 的语意为改写分数本身，2026-08-13 使用者确认
- (decision|telegram-kiro-bridge-main|2026-08-13) 多个 VS Cash 互不影响，各自只乘自己轮次的加总值 :: 多个 VS Cash 之间不会互相作用，2026-08-13 使用者确认
- (decision|telegram-kiro-bridge-main|2026-08-13) VS 转型权威来源为 server 给定 + client 推导对账模式 :: VS 转型由 server 给还是 client 判的待确认事项，2026-08-13 使用者裁决为 server 给 + client 推导对账
- (decision|telegram-kiro-bridge-main|2026-08-13) VS Collect 倍数方案从盘面倍数改为收集时列倍数 :: VS Collect 方案不再将倍数打到盘面上的 Cash 或 JP 符号
- (decision|telegram-kiro-bridge-main|2026-08-13) VS Collect compounding deferred to director confirmation with implementation constraint :: User decided on 2026-08-13 to ask director before assuming VS Collect compound behavior, not preset either interpretation
- (decision|telegram-kiro-bridge-main|2026-08-13) VS Feature multiplier mechanics clarified for uk_slot_clash_of_olympus :: VS Collect multiplier confirmed to rewrite Cash score values directly on the board, not just during collection phase
