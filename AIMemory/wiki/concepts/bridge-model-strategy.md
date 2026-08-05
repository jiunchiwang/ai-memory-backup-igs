---
title: Bridge Model 選型與配額策略
type: concept
created: 2026-08-05
updated: 2026-08-05
sources: [f_c228c9, f_fedf5c, f_efd659, f_c5dfde, f_392c22, f_fb7004, f_bd8491, f_948bf2, f_f6406d, f_7bf9a8, f_174485, f_61ec60, f_ab8e2f, f_30e280, f_244bfd, f_aad37e, f_5b9478, f_d49b9a, f_7c7a20, f_ed90b4, f_c0459d]
---

# Bridge Model 選型與配額策略

2026-08-05 topic review 從過大的 [[bridge-acp]]（原 57 筆）拆出。[[bridge-acp]] 講的是 ACP 協定機制本身（adapter 切換、capability 偵測、session lifecycle）；本頁講的是**選哪個 model、怎麼分配配額、pin 怎麼設定**——兩者常同時出現在同一個決策裡，但關注點不同。

## 目前配置

- `/agent claude` backend model pin：`opus[1m]`（effort high）——設定檔 `${MEMORY_DIR}/config/acp-providers.json`
- bridge 主 session model 為 `claude-fable-5[1m]`（1M context 變體）——這是 session 層 runtime 設定，與 `.env` 的 `ACP_MODEL` 屬不同層，不矛盾
- 三個 backend（`acp-providers.json`）：`claude`（claude-agent-acp，pin opus[1m]/high）、`kiro`（`kiro-cli acp --model claude-opus-4.6 -a --agent main`）、`codex`（`npx @zed-industries/codex-acp`，auth 未解可能切換失敗）——此檔每次 `/agent` 即時重讀，不需重啟 bridge

## 走過的 pin 修正史（勿當成當前值，只看最新 fact）

| 日期 | 變更 | 原因 |
|---|---|---|
| 2026-07-27 | Kiro CLI 移除 `claude-opus-4.6`，只剩 `claude-opus-4.5` | 上游供應端變動 |
| 2026-07-29 | `.env ACP_MODEL` 從無效值 `claude-opus-5` 改為 `opus[1m]` + adapter 0.59.0→0.63.0 | `opus[1m]` 需新 SDK 才能解析成 Opus 5 (1M)；此更新推翻舊 fact「.env 為 claude-fable-5」 |
| 2026-07-30 | `/agent claude` pin 從 `claude-sonnet-5` 改為 `opus[1m]` | 推翻先前「刻意 pin 成 Sonnet 5 為配額考量」的決定 |

**教訓**：這類 pin 值會反覆變動，查現況一律信最新 fact 與 `acp-providers.json` 實檔，不要信本頁敘述性文字的具體 model 名。

## Kiro CLI Model 生態

- **短名格式**：`claude-sonnet-4.6`、`claude-opus-4.5`（非完整 API model ID `claude-sonnet-4-5-20250514`）
- **Claude 系可用清單**：auto / claude-opus-4.5 / claude-sonnet-4.6 / claude-sonnet-4.5 / claude-sonnet-4 / claude-haiku-4.5（`claude-opus-4.6` 已於 2026-07-27 移除）
- **非 Claude 系（2026-07）**：deepseek-3.2（0.25x, 164K）、qwen3-coder-next（0.05x, 256K）、minimax-m2.5（0.25x, 196K）、minimax-m2.1（0.15x, 196K）、glm-5（0.5x, 200K）
- `kiro-cli chat --list-models`（`--format plain/json/json-pretty`）可查可用清單，但需登入狀態才回傳結果；2026-07-26 曾因未登入失效，2026-07-27 恢復正常

## ACP Adapter 的 model 偵測陷阱（與 [[bridge-acp]] 的協定機制交界處）

- **codex-acp 雙形狀陷阱**（2026-08-02）：同時公告 `models` 形狀與 `configOptions` 裡 `id="model"` 的條目，所以「有沒有 model config option」不能拿來判別「這個 adapter 能不能在 session 期間換 model」。正確判別式是 `models` 區塊是否出現過（kiro/codex 有、claude-agent-acp 沒有），且要在 `availableModels` membership 驗證**之前**就 latch
- **`AcpBackendDef` 的 `model` 與 `displayModel` 語意不對稱**：`applyModelEffortToCommand` 只在 claude 分支回傳 `acpModel`，所以 kiro/codex 的 `model` 恆為 `undefined`、只有 `displayModel` 有值（實跑確認 kiro `model=undefined`、`displayModel=claude-opus-4.5`）——要比對「這個 backend 現在跑什麼」必須用 `displayModel`

## Claude Code `advisor` 顧問工具

- 需 `/advisor` 指令、`settings.json` 的 `advisorModel`、或 `--advisor` 旗標三選一顯式設定，且組織 `availableModels` allow-list 需允許該顧問模型
- Gating 條件：`advisorModel` 設定 + 僅第一方帳號（Bedrock/Vertex 不行）+ 顧問模型的 `advisor_rank` 必須 ≥ 主模型（Haiku 4.5=1、Sonnet 4.6=2、Sonnet 5／Opus 4.6=3、Opus 4.7/4.8/Opus 5=4、Fable 5=5）
- 2026-07-14 使用者親自執行 `/advisor` 選定 Fable 5 後解除組織存取限制，之後 `advisor()` 呼叫確認可用
- 不能取代異源覆核，細節見 [[adversarial-review]]

## Claude Code commit trailer 不是 model 自我宣告

`git commit` 的 `Co-Authored-By` trailer 是 harness 模板字串（session 啟動時定格），非 runtime model 自我宣告；harness 認不得非標準 model ID（如 `claude-fable-5`）時會 fallback 寫 `Claude Opus 4.6`，**不可當實際 model 證據**——查實際 model 要用 raw JSON-RPC probe（見 [[verification-diagnosis]]）。

## Claude Max 5x 配額分配策略

記於 `.claudedocs/model-allocation-max5x.md`：

- **Opus 是最稀缺配額**，只留給高認知決策（架構、最終審查、難 debug、對抗驗證）
- **所有 ≥2k token 的實作產出委派給不限量的 Kiro CLI**
- Haiku 處理機械/批次操作；Sonnet 負責協調
- 配額同時受「全模型每週上限」與「Sonnet 專屬每週上限」兩道牆限制，且跨 Claude.ai chat / Claude Code / Cowork 共用
- **快速判準**：自問「這個錯誤是 Sonnet 級還是 Opus 級」——可重跑、重做成本低的錯誤降級委派，會污染下游決策（架構、事實、記憶）的錯誤才值得動用 Opus
- Workflow / subagent 必須顯式指定 model override，否則沿用預設 model 會造成配額爆掉

## vc-kiro-delegate 三段 Review

委派 Kiro 實作後的品質鏈：① Kiro self-review ② 獨立新 session 冷讀 git diff ③ 主 agent heavy review。實證有效：Kiro self-review 抓到 `/restart` 走 `shutdown()` 漏清 registry、獨立 reviewer 抓到 self-review 修法誤殺 SIGINT resume 場景——兩輪各抓到一個真 bug，主 agent 接手修（不叫 Kiro 修第二次）。

## 已否決的方案

- **三模型分工架構**（Fable 5 orchestrator ~10% tokens、Codex 5.5 executor ~60%、Gemini 3.1 Pro reviewer ~15%）——已評估，決定暫緩不採用，避免未來重複提案
- **Headroom 整合方案 B（proxy wrap）**——排除因 Kiro CLI 大概不吃 `ANTHROPIC_BASE_URL`；優先序 A（MCP server）> D（headroom learn 獨立跑）> C（library 整合）

## 相關

- [[bridge-acp]] — 本頁拆出的來源頁面，ACP 協定機制與 adapter 設定檔差異
- [[adversarial-review]] — 覆核者選型的成本分級（同源自 bridge-acp 拆分）
- [[verification-diagnosis]] — 查證「實際跑什麼 model」的 raw probe 方法論
- [[bridge-research]] — Headroom 整合評估的完整背景
