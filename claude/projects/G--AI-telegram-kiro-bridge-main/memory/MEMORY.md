# Memory Index

- [session-store-ui-state](project_session_store.md) — /session 多 session 管理完成，e2e 全過（BC-2/3/5/8 含跨 backend pin 連動），無待辦

- [acp-session-resume-state](project_session_resume.md) — session resume 全部收尾：e2e 通過（2026-07-07 SIGINT 路徑）+ cosmetic 已補（55b3628），無待辦
- [bridge-steering-integration](bridge-steering-integration.md) — bridge 不注入 steering，但 Kiro ACP 自載 → 端到端有效；gap 只在切 Codex/Claude，且該在 sync.ps1 層修
- [steering-corpus-types](steering-corpus-types.md) — 3 份 steering 是混合型（always-on vs 相關時才查）；steering 投影是 copy 非 junction
- [decision-gate-hook-minimal](decision-no-gate-hook.md) — 已部署閘門 A/B Claude-only 最小版（impact-gate.mjs + settings.local.json）；跨 CLI 投影已否決
- [rich-messages-upgrade-verdict](project_rich_messages_upgrade.md) — @grammyjs/stream append-only 否決快速升級；小 bug 已修（ce0e1ac），draft 化須 dev-design
