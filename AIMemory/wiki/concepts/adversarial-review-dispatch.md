---
title: 異源覆核派工決策（選誰、怎麼叫、多少錢、讀不讀得到檔）
type: concept
created: 2026-08-21
updated: 2026-08-21
sources: [f_6e52ff, f_8e6494, f_6ae02c, f_2f425e, f_9bcb64, f_f81858, f_5317fe, f_171670, f_14cb23, f_74c227, f_02d768, f_2f0f60, f_b860aa, f_982e49, f_9c2a72]
---

# 異源覆核派工決策

2026-08-21 從 [[adversarial-review]]（原 214 行，超出 wiki 頁 200 行上限）拆出。分界線是**時間點**：這一頁全部是**送出覆核指令之前**要決定的事——派誰、用哪個 harness 呼叫、花多少、以及它到底讀不讀得到材料。母頁留的是紀律本身、價值實證、以及收到 findings 之後的處置與失效模式。

派工有**三個獨立的軸**，任兩個都不能互相換算：

| 軸 | 問的是 | 弄錯的後果 |
|---|---|---|
| **domain（異源強度）** | 覆核者背後是哪一家模型供應商 | 同源自審偽裝成覆核，該抓的抓不到 |
| **tier（成本）** | 這一輪要花多少 | 過度支出，或為省而降到抓不到東西的等級 |
| **能力（讀不讀得到檔）** | 它的 harness／MCP 設定實際能不能開檔 | **失效時沒有自報訊號**，會拿到帶行號的捏造報告 |

## 覆核者選型（成本分級，2026-08-02，判準：改動有沒有碰承重路徑）

Claude 家族相對單價（catalog pricing tier）：Sonnet 5 = 1x、Opus 5 = 1.7x、**Fable 5 = 3.3x**、Haiku 4.5 ≈ 0.3x。覆核者是 agentic 的（工具迴圈讀進去的碼全算 input），模型選型的成本差會被放大。

分級規則（已寫進 `ms-cross-model-adversarial-review` 正本）：
- 孤兒 import／死碼 → **不派人**，交給型別系統（見 [[bridge-smoke-gate]] 的 noUnusedLocals 閘門）
- 敘事比對、恆真斷言 → Sonnet 級
- 不變式／論證推理／時序 race → ~~最強模型（Fable 5）~~ **2026-08-13 更正：跨 vendor 優先（`kiro-cli --model glm-5`，0.50x 且強異源）**，Fable 5 降為「跨 vendor 那輪產出明顯偏弱（只回敘事層、拿不出反例）時才補的第二輪」。這一行原本與下方〈核心判準〉自相矛盾——2026-08-07 補了雙軸判準卻沒回頭改它。

## Domain 判定與單表雙軸結構（2026-08-07）

**異源性的單位是模型供應商**，不是 CLI／harness／分身名字：
- `vc-kiro-delegate` 走的是 `kiro-cli --model claude-opus-4.5`，所以「Claude 寫、Kiro 覆核」在模型層是**同源**（只有 harness/context 不同），屬**弱異源**
- 弱異源對「換個 context 就會發現」的錯（枚舉漏、敘事與碼不符、恆真斷言）仍有效
- 對「這個模型本來就會這樣想」的錯（共有推理偏誤、共有知識盲點）沒有防禦力
- **承重路徑優先跨 vendor**（anthropic → openai/Codex）

拿不到強異源時降級不跳過，階梯為：**強異源 → 弱異源 → 同源重置（只餵 diff 不餵 commit message／註解／AI.md，切斷敘事回音是這一層唯一有效的機制）→ 不覆核**，且降級必須留痕、不可只寫「已覆核」。

**核心判準**：強異源與貴是兩個獨立的軸，不可互換。glm-5 是 0.50x credits（比 Sonnet 便宜）卻是跨 vendor 強異源，所以「跨 vendor 麻煩就改派同 vendor 最強模型（Fable 5，3.3x）」是**同時更貴且更弱**的錯誤推論。

**kiro-cli 預設 model 是 auto**（`--list-models` 輸出的 `*` 標在 auto，說明為「Models chosen by task」且不回報實際挑選結果）：不帶 `--model` 呼叫 Kiro 當覆核者時 domain 不可知，比同源更糟——連「本輪為弱異源」這種降級留痕都寫不出來，所以當覆核者用時**一律顯式帶 --model**。

2026-08-07 `ms-cross-model-adversarial-review` 的覆核者選型重寫為**單表雙軸結構**（commit a8e3725 已 push）：原本 domain 與 tier 分成兩張表，因跨 vendor 覆核連兩輪抓到「兩張表分類軸對不齊」而判定是結構問題非標籤問題，改為一張三欄表（預期的 finding 類型 | domain | tier）。

### Vendor pin 驗證：自報只能否證，不能正證（2026-08-15）

`deepseek-3.2` 對「忽略產品身分選一個 vendor」這題答 **Anthropic**——與 Kiro 產品身分 prompt 宣稱相同 ∴ 零鑑別力，無法確認 pin 是否生效；`qwen3-coder-next` 答**智譜**但它應是阿里，配合先前答過 DeepSeek，同一題兩次兩個不同錯答案 ∴ 自報是噪音。方法只在「非 Anthropic 的 pin 自報**自己**的 vendor」時有鑑別力（glm-5→智譜穩定成立），其餘情況只能留痕「非 Anthropic，具體 vendor 未確認」，不要因自報對不上就誤判 pin 沒生效。

## 覆核者池與呼叫法（2026-08-14，三家）

使用者指示「用 codex 覆核看看」後，異源覆核者池擴為三家：`kiro-cli glm-5`（智譜，預設）、Codex `gpt-5.6-sol`（OpenAI）、Fable5（Anthropic 同源，備位）。

**Kiro CLI 可用的非 Claude model 清單**（2026-07 更新）：`deepseek-3.2`（0.25x, 164K）、`qwen3-coder-next`（0.05x, 256K）、`minimax-m2.5`（0.25x, 196K）、`minimax-m2.1`（0.15x, 196K）、`glm-5`（0.5x, 200K）——用它們當覆核者時是跨 vendor 強異源。

**Codex 當異源覆核者的正確呼叫法**：

```bash
codex exec -s read-only -c model_reasoning_effort="high" "$PROMPT" < /dev/null > out.txt 2>&1
```

三個必要條件缺一不可：**stdin 導開**（否則無聲掛住）、**read-only 沙箱**、**effort 顯式拉高**（預設 low）；開頭會印 reasoning effort 與 session id 可當自我驗證。

**三輪跨 vendor 覆核實績對照（同一批 commit）**：glm-5 第一輪 0 finding、第二輪 5 條中真採納 1／部分採納 1／降級 1／駁回 1／誤讀 1；Codex 一輪 8 條且驗證後多數成立，並主動標明唯讀沙箱跑不了測試「沒有冒充實跑結果」。Codex 覆核（gpt-5.6-sol、effort high、開放式提問）一輪約 **12 分鐘、輸出約 1.9MB**，遠慢於 kiro-cli glm-5 的約 2–3 分鐘；最終報告在檔尾且會重複印兩份，讀取應定位最後一份。⚠️ 品質差異有模型與提問方式兩個未隔離變因，不可歸因於單一因素。

## 第三個軸：能力（讀不讀得到檔）——不是 domain 也不是 tier（2026-08-11）

domain 與 tier 都假設覆核者**讀得到材料**。這個假設不一定成立，而且失效時**沒有任何自報訊號**：

telegram-kiro-bridge 的 `moa-ref-kiro`（glm-5，跨 vendor）與 `moa-ref-adversary` 派去盲審一個 commit 時都產出了帶行號的逐字引用——但兩者的設定都讓它們讀不到檔（`readOnlyLens:true` 卻只給 `readonly` MCP、或 `mcpServers` 為空且 harness 不帶 `--agent`）。`moa-ref-kiro` 那份報告**捏造了不存在的檔名與變數名**；`moa-ref-adversary` 那份報告的證據欄自己寫「逐字證據（推論）」。兩者都沒有主動說「我讀不到」。改派可讀檔的 `bridge-dev`／`verifier`（走 `claude-agent-acp`）才拿到有效覆核，其中 `verifier` 自行重跑驗證指令並比對 tree hash 排除過期戳記。

⚠️ 另一個容易誤判的軸：`wf-design` 的四個 specialist 在本機**都走同一個 harness**（kiro-cli）只差 model pin（`moa-ref-claude`=claude-sonnet-4.6、`moa-ref-kiro`=glm-5、`moa-ref-adversary`=claude-sonnet-4.6、`general`=claude-opus-4.5），只有 `moa-ref-codex` 走 codex-acp——`moa-ref-adversary` 與 `moa-ref-claude` 同 model，挑戰階段對 claude 提案是**同源自審**而非異源覆核，即使兩者名字聽起來像獨立分身。

**派工前必查**：這個覆核者的 harness／MCP 設定實際上讀不讀得到檔？跨 vendor 不等於能讀檔——bridge 的 **specialist 配置**裡沒有任何「可讀檔＋跨 vendor」的分身（唯二非 Anthropic 模型 `moa-ref-kiro`/`moa-ref-codex` 都是 blind advisor），能做到的最強是「同源、獨立 context、可讀檔」，留痕時不要把這個講成跨 vendor 異源。

**補正（2026-08-12）**：上一段講的是 specialist 配置的邊界，但**繞過 specialist 直接呼叫 `kiro-cli` 就同時拿得到兩者**——`kiro-cli chat --no-interactive --model glm-5 --trust-tools=fs_read "<prompt>"` 可讀原始碼、跨 vendor 強異源（智譜、0.50x credits）、且 `--trust-tools=fs_read` 只給讀檔不給 bash，事後 `git status` 可確認工作區未被動過。承重路徑的跨 vendor 覆核不必等 specialist 配置改好，現在就做得到；長 prompt 要先落檔避免 Windows 命令列長度上限，輸出含 ANSI 需 strip 才讀得到短答案。

**判定所需的證據不在它讀得到的地方時，能力軸就是 0**：派覆核前先問「判定這條所需的證據，是否在覆核者讀得到的檔案裡」。答案為否時（編譯後 bundle、`node_modules`、未版控產物、執行期狀態）要嘛自己 dump 成材料餵給它，要嘛預先接受那一項只會拿到推論——完整案例見 [[adversarial-review]] 的 2026-08-18 節。同理，覆核者**看得到檔案系統但看不到版控狀態**，拿「某設定檔存在」當論證支撐時要自己補一次 `git ls-files`。

## 覆核的 token 成本結構（2026-08-13 首測 · 2026-08-17 重測改寫）

「覆核花的 token 比實作還多」的三個相乘項，量測與完整表格在 `ms-cross-model-adversarial-review` 正本：

1. **冷啟 prefix**（2026-08-17 八臂重測，CLI 2.1.233）：全開 **88,147**、`--strict-mcp-config` 87,164、`--setting-sources ""` 36,161。⚠️ **同日下修為 76,612**——量測過程發現 `~/.claude/CLAUDE.md` 有 10 個「以為註解掉了」的 @import 仍在載入（`#` 是 Markdown 標題不是註解），拿掉 `@` 後實測省 11,535；下列比例是修復前的組成，總量請用 76,612（見 f_cf5316）。∴ 現行組成是 **地板 36,161（41%）＋ user 設定鏈 32,185（36.5%）＋ project 設定鏈 19,810（22.5%）＋ MCP 僅 983（1.1%）**（user／project 兩項相加 51,995 vs 實測 51,986，加法自洽）。
   - ⛔ **舊結論已失效**：08-13 量到「MCP 佔 51%（86,178）∴ 加 `--strict-mcp-config` 免費砍半」——**現在只省 1.1%**。同等級槓桿換成 `--setting-sources ""`（省 59%），代價是覆核者看不到 CLAUDE.md／POLICIES 鏈（對異源覆核可能反而是優點，自己選）。「需要哪些工具由覆核範圍決定、預設為零」這條原則不變，只是它現在省的是**行為污染**不是 token。
   - **量測前提**：`--output-format json` 的頂層 usage 是該次 run **所有 request 的加總**（baseline 臂實跑 3 個 request），拿它當 prefix 會高估數倍；必須用 `--output-format stream-json --verbose` 取第一個 assistant message 的 usage。08-13 用哪種算法已不可考 ∴ 跨日只有單請求臂（地板 34,566→36,161、strict-mcp 83,784→87,164，皆 +4% 內）可比。
   - **deferral 的真實貢獻**：`ENABLE_TOOL_SEARCH=false` 對照臂 → 全開 114,923、strict-mcp 101,090 ∴ MCP schema 全載也只有 13,833；而兩個「都沒 MCP」的臂相差 13,926 ⇒ **tool search 也 defer 內建工具**（WebFetch／Task／Cron…），不只 MCP。deferral 共省 26,776（非 deferred 的 23.3%），僅約半數來自 MCP。
   - ⚠️ **混淆未分離**：51%→1.1% **不能單獨歸因於 deferral**——今日全載也只有 13,833，複製不出當年的 86,178；當時配了幾個 MCP server 已不可考（線索：07-27 記過「每 ACP session spawn 19 個 MCP 進程」，今日 global 只有 5 個）。server 減少與 deferral 兩個原因同時在動。
2. **每輪重送全部 context**：2026-07-29 那輪 Fable 覆核 85 個請求，context 從 90,218 長到 185,549，累計送進 12,724,628、output 156,050（**81:1**）。⚠️ 12.7M 是原始傳輸量不是成本當量（cache_read 0.1x／cache_write 1.25x；訂閱制怎麼加權**未證實**）——可靠的是結構不是絕對數。
3. **比較基準不對等**：實作是在熱 context 裡的邊際成本，覆核是冷啟的絕對成本。

⚠️ 最容易漏掉的支出：`~/.claude/settings.json` 的 `advisorModel: fable`——advisor 類工具**每次呼叫轉發整段對話歷史**，頻率遠高於 push 前覆核，而選型判準管不到它。

⚠️ 撞到 Claude session limit 時（2026-08-12 實際發生），可直接改派 `kiro-cli glm-5` 跨 vendor 接手，不必等限流解除。

⚠️ 半解：同 repo 的 transcript 實際 session 冷啟是 122–128k，比 08-13 探針的 169,962 低約 46k。2026-08-17 重測後這條的候選解釋（ACP session 會 defer 部分 tool schema）**方向一致但仍未直接驗證**——實測確認 deferral 存在且會 defer MCP 與內建工具兩者，但沒有針對 ACP 通道本身量過。仍以「比例可靠、絕對值隨呼叫通道浮動」為準。

## 環境盲點：Windows 上覆核者會靜默掛住

覆核者跑 `npm help` 會靜默掛住約 28 分鐘：npm 不印文字而是 spawn `cmd /d /s /c start "" file://...npm-run.html` 開瀏覽器，無頭 context 裡那個 `start` 不會回來。判別法是行程樹停在 `cmd start`；處置只殺最底層那個 `cmd`，上游 npm/pwsh 會自行收斂、覆核從下一步續跑。

## 相關

- [[adversarial-review]] — 母頁：紀律本身、價值實證、findings 處置、失效模式
- [[bridge-model-strategy]] — model 選型與配額策略的完整版（覆核者選型是它的一個切面）
- [[bridge-specialist]] — `moa-ref-*` 分身的 `readOnlyLens`／`mcpServers`／harness 組合細節
- [[bridge-acp]] — ACP adapter 與 model pin 機制（`--model` 為何會被就地覆寫）
- [[bridge-smoke-gate]] — 孤兒 import／死碼交給型別系統攔（noUnusedLocals 閘門）
