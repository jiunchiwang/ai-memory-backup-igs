# claude-mem shortlist (高價值候選,英文待精選)
> 產生:2026-07-07T20:30:02.302Z;筆數:11(上限 15);自 epoch 1783368606705
> 給 AI:精選真正「跨 session 可重用」的 → 翻繁中 → 用 memory search 去重 → 提案 ≤10。一次性步驟略過。

- (decision|telegram-kiro-bridge-main|2026-07-07) Explicit Token Policy + Memory Provenance for Bridge Security :: telegram-kiro-bridge currently has implicit token execution gating where proxy specialists cannot execute SCHEDULE/RESTART/MOA_PLAN tokens
- (decision|telegram-kiro-bridge-main|2026-07-07) Session park() implementation strategy refined after adversarial review :: onBeforeClose in session-extract.ts:446 performs writeWorkingState("session closed") + saveArchive + saveTranscript which pollutes parked sessions
- (decision|telegram-kiro-bridge-main|2026-07-07) Selected plan+review workflow for multi-session management implementation :: User selected "plan" option from ASK:sess_flow dialog to implement multi-session management feature
- (decision|telegram-kiro-bridge-main|2026-07-07) Multi-session management system design proposed for telegram-kiro-bridge :: New `src/session-store.ts` would manage multiple named sessions per chat (id, name, acp sessionId, backendKey, agentCommand, cwd, status)
- (decision|telegram-kiro-bridge-main|2026-07-07) Default config suggestion for /agent when acp-providers.json missing :: The /agent command requires G:\AI\AIMemory\config\acp-providers.json to switch between ACP backends
- (decision|telegram-kiro-bridge-main|2026-07-07) Independent cold-read review initiated for ACP session resume implementation :: Independent reviewer launched as background task b2w6oahmn using claude-opus-4.6 model via kiro-cli chat
- (decision|telegram-kiro-bridge-main|2026-07-07) Delegated ACP session resume implementation to Kiro :: User selected Kiro delegation (vc-kiro-delegate) for ACP session resume implementation
- (decision|telegram-kiro-bridge-main|2026-07-07) ACP Session Resume Implementation Plan :: Implementation plan created at docs/superpowers/plans/2026-07-07-acp-session-resume.md defines three-layer architecture for session resumption
- (decision|telegram-kiro-bridge-main|2026-07-07) Audio File Handling Strategy for Template Project :: MG_Bgm and FG_Bgm will be commented out in template project
- (decision|telegram-kiro-bridge-main|2026-07-07) Project-isolated extensions architecture chosen over shared workspace pattern :: Extensions directory relocated from G:/Cocos_Project/extensions to G:/Cocos_Project/uk_917_leprechauns_pots_client/extensions for project isolation
- (decision|telegram-kiro-bridge-main|2026-07-07) GRAND/MEGA JP symbols follow standard collection flow :: GRAND and MEGA jackpot symbols no longer trigger independent award panels
