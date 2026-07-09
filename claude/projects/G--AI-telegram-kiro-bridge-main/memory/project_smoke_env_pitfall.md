---
name: smoke-suite-env-pitfall
description: 在 bridge spawn 的 agent session 內跑 scripts/check-*.mjs 會因繼承空環境變數而大量假失敗
type: project
---

在 bridge spawn 的 agent session 內直接跑 smoke suite（`node scripts/check-*.mjs`）會出現大量假失敗（2026-07-09 實測 15/56 誤報）。

**Why:** bridge 給子 agent 的環境含空值變數（`TELEGRAM_BOT_TOKEN=""`、`ACP_AGENT_NAME=""` 等），而 dotenv 不覆蓋既有 process.env → `config.ts` 的 `required()` throw「Missing required env var」。

**How to apply:** 跑 smoke 前先清掉 .env 內出現的繼承變數，但保留 `MEMORY_DIR`（清掉會 fallback 到不存在的 `F:\AI\AIMemory`）：

```bash
unset_args=$(grep -oE '^[A-Z_0-9]+' .env | grep -v MEMORY_DIR | sed 's/^/-u /' | tr '\n' ' ')
env $unset_args node scripts/check-xxx.mjs
```

其他已知非故障：`check-acp-model-effort` 的 effort 選項被 claude-agent-acp 拒絕（Unknown config option），bridge graceful ignore，屬已知限制；`check-acp-handshake` 需要手動帶參數，不算失敗。topic shard drift 用 `scripts/rebuild-topic-shards.mjs` 重建（從 master facts log 決定性重建）。
