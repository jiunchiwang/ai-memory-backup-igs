---
title: Bridge Model 選型與配額策略
type: concept
created: 2026-08-05
updated: 2026-08-14（wikilint：修正「目前配置」節內部自相矛盾——主 session 誤留 claude-fable-5[1m] 舊值、kiro pin 誤留已移除的 claude-opus-4.6，與 [[bridge-acp]] 對齊為現況）
sources: [f_c228c9, f_fedf5c, f_efd659, f_c5dfde, f_392c22, f_fb7004, f_bd8491, f_948bf2, f_f6406d, f_7bf9a8, f_174485, f_61ec60, f_ab8e2f, f_30e280, f_244bfd, f_aad37e, f_5b9478, f_d49b9a, f_7c7a20, f_ed90b4, f_c0459d, f_5c3ef5, f_d36619, f_ccb09c, f_fd5954, f_31877c, f_e84ad9, f_d6f8a7, f_8a90df, f_e2fe39, f_cd3300, f_ea64e9]
---

# Bridge Model 選型與配額策略

2026-08-05 topic review 從過大的 [[bridge-acp]]（原 57 筆）拆出。[[bridge-acp]] 講的是 ACP 協定機制本身（adapter 切換、capability 偵測、session lifecycle）；本頁講的是**選哪個 model、怎麼分配配額、pin 怎麼設定**——兩者常同時出現在同一個決策裡，但關注點不同。

## 目前配置

- `/agent claude` backend model pin：`opus[1m]`（effort high）——設定檔 `${MEMORY_DIR}/config/acp-providers.json`
- bridge 主 session model 為 `opus[1m]`（Opus 5 1M context 變體）——⚠️ 本節先前誤留 `claude-fable-5[1m]` 舊值，`claude-opus-4.6` 已於 2026-07-27 移除見下方「走過的 pin 修正史」，主 session 與 `/agent claude` pin 現在是同一個值，兩者一致
- 三個 backend（`acp-providers.json`）：`claude`（claude-agent-acp，pin `opus[1m]`/high）、`kiro`（`kiro-cli acp --model claude-opus-4.5 -a --agent main`——⚠️ 本節先前誤留已移除的 `claude-opus-4.6`）、`codex`（2026-08-06 遷移為 `npx -y @agentclientprotocol/codex-acp`，pin `gpt-5.6-terra`/high；已用 ChatGPT 登入可正常運作，細節見 [[bridge-acp]]「Codex authMethods 誤判」）——此檔每次 `/agent` 即時重讀，不需重啟 bridge；三個 backend 現況以 [[bridge-acp]] 的「目前配置」節為準
- `.env` 的 adapter 註解已於 2026-08-06 修正三處：codex 段改推維護中的套件並刪掉誤導的 `-c model` 範例、claude 段改推 repo 內鎖版路徑取代已 deprecated 的 global bin、`ACP_MODEL` 段落原本錯寫「Codex 收到 `set_config_option` 會 reject」已更正為實測正確的「Codex 會接受」（`.env` 在 `.gitignore` 內，此為本機檔修正非 commit）

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

## Kiro CLI Effort 值域是 per-model，幾乎沒有 model 支援（2026-08-11 實測，kiro-cli 2.16.2）

11 個 `availableModels` 逐一問過（開 ACP session 送裸 `/effort`），**只有 `claude-sonnet-4.6` 可設**，合法值 `low`/`medium`/`high`/`max`（**沒有 `xhigh`**——送 xhigh 被後端逐字拒：`invalid value 'xhigh' for 'output_config.effort', must be one of: low, medium, high, max`）。`claude-opus-4.5`/`claude-sonnet-4.5`/`claude-sonnet-4`/`claude-haiku-4.5`/`auto`/`glm-5`/`deepseek-3.2`/`minimax-m2.5`/`qwen3-coder-next` 一律回「Effort configuration is currently not available on \<model\>」（`minimax-m2.1` 未測）。

- `kiro-cli --help` 寫的「(e.g. low, medium, high, xhigh, max)」是通用範例、**不是值域**。
- `--effort` 在 CLI 層完全不驗證：`kiro-cli chat --effort bogus-zzz` 照跑、exit 0、零警告；對不支援 effort 的 model 帶 `--effort` 同樣安靜——是靜默 no-op。∴ bridge 的 `ACP_EFFORT` 對 Kiro 幾乎恆無效。
- 查值域唯一路徑：Kiro 的 `session/new` 從不回報 `configOptions`（只有 `models`/`modes`），只能開 session 後送裸 `/effort`。
- ⚠️ **誠實邊界**：「`--effort <合法值>` 對 sonnet-4.6 是否真的套用」**未驗證**——無 flag／`xhigh`／`max` 三次的 `/effort` 輸出完全相同且不含 current 標記，區分不出「已套用」與「被忽略」。可區分的探針 `/effort set-current-as-default` 會寫入使用者預設值，未經同意不要跑。

`src/configRegistry.ts` 的 `ACP_EFFORT_FALLBACK.kiro` 已於 commit `9897f46` 補上 `max`（原缺）；連帶把「靜態清單只在 adapter 還沒開過 session 時用得到」的舊註解更正——對 Kiro 的 effort 軸，這份清單是**永久生效**的唯一來源（Kiro 從不自報 effort 值域）。

## Sonnet-4.6[effort=max] vs Opus-4.5：找 bug 能力對照實驗（2026-08-11/12）

起因是想知道 Kiro 上把 opus-4.5 換成 sonnet-4.6+max 當覆核腳划不划算。兩輪盲測（真實 `mutate-gate` 變異注入本 repo 碼片段、同 prompt、各自新 session）：

| 輪次 | 樣本 | sonnet-4.6[max] 命中 | opus-4.5 命中 | 統計顯著性 |
|---|---|---|---|---|
| 第一輪 | n=5 | 2/5 | 3/5 | 差一題，毫無區分力 |
| 第二輪（擴大） | n=16（8 變異 × 有/無註解） | 6/16 | 5/16 | 3 對不一致（全偏 sonnet），精確雙尾 p=0.25，**不顯著** |
| 第三輪（修 fixture 後重跑） | n=16（同上，剝註解組行號改連續） | 10/16 | 7/16 | 3 對不一致（全偏 sonnet），精確雙尾 p=0.25，**不顯著** |

> ⚠️ **命中數是評分尺依賴的。** 第二輪原本記為 9/16 vs 6/16，那是當時 session 的尺；
> 2026-08-12 用一把逐字寫死的判準（命中＝引用行號落在突變行 ±2 **且** 說對失效機制
> **且** 結論主張它是缺陷）把兩批共 64 筆在同一輪重評，得到上表數字。差異來源是**評分者漂移**
> 而非資料變動。∴ 引用本表時務必連判準一起引；只有同尺重評過的數字彼此可比。
>
> 🔴 **更重要的是這張表的差值全都沒有解讀價值。** 第三輪順帶量到 **test-retest 翻轉率 25%**：
> orig 條件零改動重跑，16 個 cell 翻了 4 個（sonnet 4/8→6/8、opus 3/8→5/8，且四次同方向）。
> n=8 的一臂光噪音就有約 ±1.4 題擺盪 ∴ 上表所有「誰多幾題」的差距都落在噪音帶內。
> 判準：**任何 n≤8 的 fixture 比較，先跑一次零改動重跑量底噪，再談差值。**

**結論只能是「量不出 sonnet@max 更強」，不得推論任一方更強。** 兩個比排名更有價值的副產物：

1. **同源天花板的一手證據**：兩臂對 `src/concurrency.ts` 的 semaphore「直接交棒」邏輯犯了完全相同的誤報（主張「waiter 沒有 `active++` 會超上限」）——這個誤報在缺陷**不存在**與**存在**時都講得出來，是複述樣板知識、不是從碼推導。拿這類覆核者背書併發碼的正確性沒有價值，要驗這一軸得用行為測試。
2. **本 repo 註解密度會高估覆核者能力**：兩個「碼內自相矛盾」的變異——index 來源 `runnable`→`ready`、`finished++` 被刪——在兩批次 × 有無註解共 8 個組合下 **8/8 全中**，那兩題不需要註解也不需要跨檔上下文。反面是 `const max = Math.max(1, Math.floor(limit) || 1)` 被改成 `const max = limit`（少夾下界）**16/16 全漏**。
   註解效應在修完 fixture 後方向仍在但不顯著（第三輪 orig 11/16 vs nocmt 6/16，7 對不一致 6 對偏有註解，p=0.125）。比計數更硬的是**機制證據**：兩處模型逐字說出自己靠註解與碼的矛盾找到缺陷——「諷刺的是，註解（行 12-15）描述的正是這個問題並聲稱透過『直接交棒』解決，但實作並沒有做到」、「註解說『用 function replacer』，而程式碼用的是 `.replace(regex, v)`……與註解聲稱的防護不符」。

比較所依賴的定價事實（Kiro 自報，A 級）：`sonnet-4.6` 是 1.3x credits／1M context，`opus-4.5` 是 2.2x credits／200k context——量不出能力差距時，這組數字是比「哪個比較聰明」更紮實的決策依據。

## Claude Code `advisor` 顧問工具

- 需 `/advisor` 指令、`settings.json` 的 `advisorModel`、或 `--advisor` 旗標三選一顯式設定，且組織 `availableModels` allow-list 需允許該顧問模型
- Gating 條件：`advisorModel` 設定 + 僅第一方帳號（Bedrock/Vertex 不行）+ 顧問模型的 `advisor_rank` 必須 ≥ 主模型（Haiku 4.5=1、Sonnet 4.6=2、Sonnet 5／Opus 4.6=3、Opus 4.7/4.8/Opus 5=4、Fable 5=5）
- 2026-07-14 使用者親自執行 `/advisor` 選定 Fable 5 後解除組織存取限制，之後 `advisor()` 呼叫確認可用
- 不能取代異源覆核，細節見 [[adversarial-review]]

### Token 成本與 context 機制（2026-08-13 查 CLI binary 實證）

⚠️ **advisor 的 context 是被剝除，不是被快取**——這與直覺相反，寫在這裡是因為前者會讓人以為
「advisor 的建議留在對話裡供後續參考」，那個假設不成立。

`~/.local/bin/claude`（307 MB bundle）逐字：

```js
// server-side tool，帶自己的 model
le.push({ type: "advisor_20260301", name: "advisor", model: S })

// 送給主模型前，把 advisor 的問答整段濾掉
i = o.filter(s => s.type !== "advisor_tool_result" &&
                  (s.type !== "server_tool_use" || s.name !== "advisor"));
// 整則被濾空時塞回佔位符：
i.push({ type: "text", text: "[Advisor response]", citations: [] })
```

推論三件事（機制一致，但**只讀了字串與該函式片段、沒追過完整控制流** ∴ 標 B 級）：
- 主模型 prefix 不被打亂 → prompt cache 保持命中
- **advisor 的請求不出現在本機 transcript**（實查：叫過 2 次，今天所有 `.jsonl` 裡 `model=fable` 命中 0）
- 主模型後續**看不到 advisor 說過什麼**，只看得到自己據此寫出的文字

成本面：
- 每次呼叫送**當下的完整 transcript**且不吃 cache ∴ 成本隨 session 長度線性成長。
  實測同一 session 冷啟 109,380 → 39 個請求後 256,711，**同一次呼叫晚叫貴一倍以上**。
- ⛔ **「快模型主力＋強模型 advisor 通常更省」這條通則在本機設定下不成立**：
  它的前提是主力比 advisor 便宜很多（Sonnet 1x + Opus 1.7x）。現況是 Opus 5 主力（1.7x）
  ＋ Fable 5 advisor（3.3x），只有 1.94 倍價差。
- 官方自己的提示逐字：`Advisor Tool (experimental) is on and may use more tokens · /advisor`

關閉方式（binary 實查）：
- `CLAUDE_CODE_DISABLE_ADVISOR_TOOL=1` ✅ 存在
- `/advisor` 互動式指令（`type:"local-jsx"`，描述 `Let Claude consult a stronger model at key moments`）
  → picker 裡選 `{label:"No advisor", value:"off"}`
- ⛔ **`/advisor off` 不存在**（該字串在 binary 中 0 命中）——它不吃參數，只能走 picker
- ⚪ **未解**：`/usage` 是否把 advisor 用量拆成分項顯示，未驗證（advisor 請求不落本機 ∴ 只能從伺服器端看）

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
