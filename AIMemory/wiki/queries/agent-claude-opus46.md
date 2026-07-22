---
title: 為何 /agent 切回 claude 後 model 仍是 Opus 4.6 而非 Fable 5
type: query
created: 2026-07-10
updated: 2026-07-10
sources: []
---

# 為何 /agent 切回 claude 後 model 仍是 Opus 4.6 而非 Fable 5

2026-07-10 使用者問：「我沒有切，我只有切 agent，但我切回 claude 時卻還是用 Opus 4.6，幫我查一下」——`acp-providers.json` 的 `claude` backend 明明配置 `model: "claude-fable-5"`，`/agent claude` 之後 session 卻仍跑 Opus 4.6。

## 根因

`claude-agent-acp` 本質就是 Claude Code，session 建立時的 model 決定順序：

1. `createSession()` → `getAvailableModels()` → 讀 merged `settings.json`（user/project/local）→ 使用者全域 `~/.claude/settings.json` 寫死 `"model": "opus[1m]"` → `setModel(opus)`
2. Bridge 接著送 `session/set_config_option(model=claude-fable-5)` → adapter 回 OK、`query.setModel(fable-5)` 確實被呼叫
3. 但 Claude Code 的 **settings watcher 會持續監聽檔案變更**，每次 reload 都重新 merge settings，把 model 蓋回 `opus[1m]`

∴ ACP layer 回報 pin 成功，但 Claude Code 核心的全域 settings 優先權更高，事後又蓋回去——`set_config_option` 對 model 而言形同虛設。

## 衝突點

使用者平常也會直接開 Claude Code（非透過 bridge）並想用 Opus 4.6，所以不能單純把 `~/.claude/settings.json` 的 `model` 欄位改掉或移除。

## 討論過的方案（皆未拍板）

| 方案 | 做法 | 顧慮 |
|------|------|------|
| A. env var 覆蓋 | bridge `buildSpawnEnv` 注入 `CLAUDE_MODEL` 類環境變數 | 需先驗證 `claude-agent-acp` 是否認這個變數 |
| B（cwd）| 設定 `ACP_SESSION_CWD` 到專用目錄，該目錄的 `.claude/settings.local.json` 覆蓋 model | 使用者不會 cd 到該目錄直接用 Claude Code，故不衝突；需 bridge 支援獨立 session cwd |
| C（cfgdir）| 用 `CLAUDE_CONFIG_DIR` env var 換整個 config 目錄 | 換掉整個 config 而非只換 model，影響面較大 |

## 狀態：未解決

對話在 `<<ASK:fix_model|*cwd=...|cfgdir=...|think=...>>` 停住，之後未見使用者回覆或後續 commit——`list_facts` 查 `ACP_SESSION_CWD` 無任何 fact，此問題目前仍是懸案。若之後又遇到 bridge ACP model pin 對 `claude` backend 失效，可從這裡的根因分析（settings watcher 覆蓋）繼續。

## 相關

- [[bridge-acp]] — Bridge ACP adapter 與 model pin 機制總覽
