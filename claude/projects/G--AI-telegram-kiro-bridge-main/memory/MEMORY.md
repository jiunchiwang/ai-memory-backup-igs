# Memory Index

- [bridge-steering-integration](bridge-steering-integration.md) — bridge 不注入 steering，但 Kiro ACP 自載 → 端到端有效；gap 只在切 Codex/Claude，且該在 sync.ps1 層修
- [steering-corpus-types](steering-corpus-types.md) — 3 份 steering 是混合型（always-on vs 相關時才查）；steering 投影是 copy 非 junction
- [decision-gate-hook-minimal](decision-no-gate-hook.md) — 已部署閘門 A/B Claude-only 最小版（impact-gate.mjs + settings.local.json）；跨 CLI 投影已否決
