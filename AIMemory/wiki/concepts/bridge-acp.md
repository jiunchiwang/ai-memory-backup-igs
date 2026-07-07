---
title: Bridge ACP 與 Model 配置
type: concept
created: 2026-07-06
updated: 2026-07-08
sources: [f_b533eb, f_493309, f_fedf5c, f_efd659, f_0c44ff, f_51868b, f_0b0e71, f_c5dfde, f_130b5d, f_7fb676, f_611812, f_392c22, f_fb7004, f_b1b0f4, f_3c7a91, f_884e78, f_7bf9a8, f_948bf2, f_e17260]
---

# Bridge ACP 與 Model 配置

[[bridge-project]] 透過 ACP（JSON-RPC over stdio）接上 agent CLI。本頁涵蓋 ACP adapter 切換、model 配置與 pin 機制、harness hook 行為——這些知識跨 adapter 有效，換 CLI 時特別需要。

## 目前配置（2026-07-07 起）

- 主 session model：`claude-fable-5[1m]`（1M context 變體）
- `.env`：`ACP_AGENT_COMMAND=claude-agent-acp` + `ACP_MODEL=claude-fable-5`（effort medium）
- Model 由 bridge 在 `session/new` 後透過 `session/set_config_option` pin——**claude-agent-acp 的 CLI `--model` flag 在 ACP 模式無效**
- 歷史配置（~2026-07-06 前）：`kiro-cli acp --model claude-opus-4.6 -a`

## /agent 熱切換與多 Backend 設定檔（2026-07-07）

- `/agent <key>` 熱切換 ACP backend（自動交接對話摘要、跨 restart 持久化）；設定檔 `${MEMORY_DIR}/config/acp-providers.json`，**每次 `/agent` 即時重讀、不用重啟 bridge**
- 檔案缺失時 fallback 為 `.env` 單一 agent；`/agent init` 顯式建立範本——seed 自 `.env` 當前 agent（保證至少一筆語意正確）+ 另兩個 backend scaffold，既有檔一律不覆蓋（排除啟動自動 seed 因為靜默寫檔違反「不逕自動作」偏好）
- codex-acp 的 initialize 回 -32000（需 auth，2026-07-07 實測未解），切換可能失敗

## Tool Call Title 顯示差異（非 bug）

Bridge 的 tool call 進度（`🔧 {title}` / `✅ {toolName}`，sessionManager 渲染）用的是 **adapter 回報的 title**：claude-agent-acp 對 shell 執行類一律回泛用名「Terminal」，kiro-cli acp 的 title 較具描述性——切 backend 後顯示風格不同屬正常。

## ACP Adapter 設定檔差異（互不通用）

| Adapter | 讀取的設定檔 |
|---|---|
| Kiro CLI | `AGENTS.md` + `~/.kiro/steering/` |
| Codex | `AGENTS.md` |
| Claude Agent（claude-agent-acp） | `CLAUDE.md`（全域 + 專案，原生自動載入） |

切換 adapter 時，靠另一家設定檔承載的規範會**靜默漏接**——這是跨 CLI 的結構性 gap（追蹤中：skill-candidates 的 agent-cli-config-hook-portability）。

## Harness Hooks（Claude 路徑）

- **impact-gate**：`.claude/hooks/impact-gate.mjs` + `settings.local.json` 註冊 PreToolUse。每 session 每檔首次 Edit/Write exit 2 要求輸出因果鏈、重試放行、只閘專案內檔案、fail-open。決策為 Claude-only 最小版（排除跨 CLI 投影因為成本/價值不成比例，切回 Kiro 時閘門消失屬接受的設計）
- **Hooks 快照**：Claude Code hooks 在 session 啟動時定格，settings 新增的 hook 要下次新 session 才生效；hook 機制在 claude-agent-acp（ACP 路徑）下有效
- **Bridge 的 tool-hooks.ts 不是閘門**：PostToolUse、fire-and-forget、僅 direct provider 路徑（tool-loop.ts）生效——走任何 ACP 時不會 fire，不能當阻擋式機制

## Kiro CLI Model 生態

- **短名格式**：`claude-sonnet-4.6`、`claude-opus-4.6`（非完整 API model ID）
- **Claude 系**：auto / claude-opus-4.6 / claude-sonnet-4.6 / claude-opus-4.5 / claude-sonnet-4.5 / claude-sonnet-4 / claude-haiku-4.5
- **非 Claude 系（2026-07）**：deepseek-3.2（0.25x, 164K）、qwen3-coder-next（0.05x, 256K）、minimax-m2.5（0.25x, 196K）、minimax-m2.1（0.15x, 196K）、glm-5（0.5x, 200K）
- **判斷**：DeepSeek 3.2 是非 Claude 裡 coding 最強穩定選項；qwen3-coder-next 超便宜但 experimental 穩定度未知

## Specialist Model Pin 與 Benchmark

- `specialist-domains.json` 的 `defaultModel` 在 spawn 時 pin 住 model——**parallel delegate 無法動態指定 model**，prompt 裡要求換 model 無效
- PARALLEL_DELEGATE 的 prompt 含 `>>`（或多行）會被 token parser 截斷導致任務**靜默未 spawn**
- ∴ Model benchmark 正確做法：`kiro-cli chat --model <name> --no-interactive -a "prompt"` 獨立 session（`--model` 在 chat 子命令下，非頂層 flag；排除建臨時 specialist domain 因為對一次性測試過重）

## vc-kiro-delegate 三段 Review（實證有效）

委派 Kiro 實作後的品質鏈：① Kiro `--resume` self-review ② 獨立新 session Kiro 冷讀 git diff ③ 主 agent heavy review（親跑 tsc + smoke + BC 對照）。2026-07-07 兩輪實戰各抓到一個 self-review 漏掉的真 bug（`/restart` 走 shutdown() 漏清 registry、self-review 修法誤殺 SIGINT resume 場景）；抓到後由主 agent 接手修，不叫 Kiro 修第二次。

## Co-Authored-By Trailer 陷阱

- Git commit 的 `Co-Authored-By` trailer 是 **harness 模板字串**（session 啟動時定格），非 runtime model 自我宣告
- Harness 認不得非標準 model ID（如 claude-fable-5）時 fallback 寫 `Claude Opus 4.6`——**不可當實際 model 證據**
- 對策：專案 CLAUDE.md「開發偏好」規則——model 名以 session 環境宣告（`You are powered by...`）為準（排除關掉 attribution 因為想保留紀錄、排除 git hook 因為過重）

## 相關

- [[bridge-project]] — Bridge 本體架構與功能
- [[dev-tools]] — 機器環境與 CLI 工具
