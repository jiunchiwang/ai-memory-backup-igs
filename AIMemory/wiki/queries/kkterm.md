---
title: KKTerm 外部 repo 研究：ACP client 多 backend 與 one-shot 退化路徑、dangerous 命名空間式廉價核可閘門（推翻 cloudflare-os B3 的成本前提）、prompt 投影與 secret 斷言閘門、assistant-skills 的 SKILL.md 慣例，以及對 telegram-kiro-bridge 的十列差距判定與 K1-K5 借鏡
type: query
created: 2026-08-18
updated: 2026-08-18
status: Step 1–2 完成（比對表 + 借鏡排序）——吸收範圍待使用者裁決，未動任何 bridge 碼
sources:
  - https://github.com/ryantsai/KKTerm
  - https://raw.githubusercontent.com/ryantsai/KKTerm/main/docs/AI_PROVIDERS.md
  - https://raw.githubusercontent.com/ryantsai/KKTerm/main/docs/MCP.md
  - https://raw.githubusercontent.com/ryantsai/KKTerm/main/docs/ARCHITECTURE.md
  - https://raw.githubusercontent.com/ryantsai/KKTerm/main/docs/AIINSTRUCTIONS.md
  - https://raw.githubusercontent.com/ryantsai/KKTerm/main/assistant-skills/ssh-troubleshooter/SKILL.md
---

# KKTerm 研究（外部 repo 吸收評估）

2026-08-18 依 `ms-external-repo-absorption` 流程研究 `ryantsai/KKTerm`，
走到 **Step 2（比對表 → 借鏡排序）** 為止，**未 clone、未讀原始碼、未安裝執行**。

相關頁面：[[bridge-research]]（外部框架借鏡總索引）、
[[cloudflare-os]]（本頁最重要的對照基準，K1 直接推翻它的一條成本判定）、
[[opencode-acp-implementation]] 與 [[deepseek-harness]]（同流程的前兩次 ACP／context 研究）、
[[bridge-acp]]（bridge 的 ACP backend 現況）、
[[bridge-secrets-backup]]（K3 的落點）、[[verification-diagnosis]]（本頁證據等級紀律來源）。

## 0. 證據等級

⚠️ **本頁全部是 B 級。** 所有內容都經過 WebFetch 的小模型摘要層——即使走
`raw.githubusercontent.com` 也一樣會過那一層（[[cloudflare-os]] §0 已記過同一個限制）。
沒有 clone、沒有讀原始碼、沒有跑過。

**本輪自己抓到一條差點寫錯的**：第一次摘要把 `docs/AIINSTRUCTIONS.md` 讀成
「內建 AI assistant 的 runtime system prompt」，我差點據此寫出一整列「prompt 架構」比對。
二次查證確認它是**給貢獻 repo 的 AI coding agent 看的文件**（等同 CLAUDE.md／AGENTS.md）：
開頭是 "To the AI assistant reading this: Read this entire document before taking any action"，
主體是 Fork and Clone、Dev Environment Setup、Opening a Pull Request。
∴ 該列已按正確語意重寫。形狀與 [[verification-diagnosis]] 記的「摘要層把兩個層級混為一談」一致——
**當一份文件的檔名同時可以指涉兩個層級時（給 AI 的指令 vs AI 的指令），必須先確定讀者是誰再引用它**。

bridge 側凡寫「未見等價」者，依據是查了 `scripts/` 清單、`POLICIES/` 清單與
`src/acp-providers.ts`，**不是窮舉全碼** ∴ 不宣稱不存在。

## 1. 這是什麼

446 star / 55 fork / 3,308 commit，TypeScript + Rust（Tauri v2），MIT + Commons Clause
（可自架，商業再散布受限）。Local-first、無 telemetry、無雲同步，支援 Windows/macOS/Linux。

定位是「vibe coder 與系統管理員的桌面工作站」：本機終端、SSH/SFTP/FTP/Telnet/serial、
RDP/VNC、內嵌網頁、檔案瀏覽全部收斂成**單一 `Connection` 抽象**，可在同一個 tab 內混排多窗格。
另有 dashboard、IT Ops 批次任務、Windows 安裝助手、內建 AI 助理。

**與 bridge 的真正交集不是終端機**，是「一個宿主 app 怎麼接多家 AI agent、
怎麼管它們的動作權限」——這一層兩邊高度同構 ∴ 值得逐項比。

## 2. 四條有實質內容的交集軸

### 2.1 它也是 ACP client，而且有 bridge 沒有的退化路徑

KKTerm 先試 ACP stdio backend：Codex 與 Claude Agent 走 registry adapter，
Cursor 走原生 `agent acp` / `cursor-agent acp`。
adapter 起不來或初始化失敗時，**退回各家的 one-shot CLI**
（`codex exec`、`claude -p`、Cursor `--print --mode=ask` 配 stdin prompt），
且文件明寫這條 "is strictly a setup-failure path"——只是安裝失敗的兜底，不是常規路徑。

bridge 的 `src/acp-providers.ts:128-130` 是 kiro / claude / codex 三個，
**沒有 Cursor，也沒有「adapter 起不來就退成 one-shot CLI」這條路**。

它自報的 ACP 方法只涵蓋 `session/prompt` 與 `session/update`，
**沒有提到 `session/new` / `session/load` / permission request** ∴ 不能拿它當
[[bridge-session]] 記錄的 resume/load 語意分析那類問題的參考來源。

### 2.2 危險工具核可：便宜到不像話的形狀（本頁最有價值的一條）

KKTerm 對外開一支 `kkterm-cli` stdio **MCP server**，把 app 能力給外部 agent 用
（Claude Desktop / Code / Codex / Copilot）。工具分八個命名空間
（workspace / dashboard / installer / screenshots / itops / network / watchdog / app）。

核可只有兩個開關：`built_in_mcp_server_enabled`（預設 true）與
`built_in_mcp_allow_all_dangerous`（預設 **false**）。
**危險工具直接編在命名空間裡**——`*.dangerous.*`；後者為 false 時，
任何 dangerous 呼叫一律回 `permissionRequired` 工具錯誤。

三個設計性質值得抄：
1. **危險性是命名當下的決定**，不是事後補設定 → 新增工具時「這算不算危險動作」躲不掉。
2. **一個 boolean 管全部**，不需要 per-tool 設定表 → 沒有「漏設一項就靜默放行」的洞。
3. **default-deny**。

⚠️ 這一條為什麼重要：[[cloudflare-os]] §6 把「側效動作核可閘門」（B3）判成
**不建議、YAGNI**，理由寫的是「要新增狀態機 + UI + 儲存，**成本高**」。
KKTerm 這版沒有狀態機、沒有 UI、沒有儲存。
**被推翻的是成本前提，不是價值判斷**——B3 應重新評估。

### 2.3 AI context 是「投影」不是「傾倒」，而且用測試釘住

`ARCHITECTURE.md` 把 assistant context 列為 command-boundary 議題：
任何前端頁面 context、後端工具輸出、debug-only 的 assistant payload
都必須設計成 **compact projection, not a raw dump**。
每次請求的被動 context 只含 labels / ids / summaries / counts / 小 metadata / 當前 UI 狀態；
原始碼、終端內容、截圖只能經**明確使用者動作或受限讀取工具**帶上去。

最值得抄的是機械層那一句：**新的 assistant surface 必須有測試斷言
「序列化後的 prompt 不含 raw secret、也不含可避免的大塊資料」**。

bridge 有 acp-trace 洩漏前科（[[bridge-secrets-backup]]），修的是那一次的洞；
`scripts/` 內有 `check-acp-trace-orphan.mjs`（管孤兒 trace 檔）與
`check-streaming-token-strip.mjs`（管出站 token），
但**未見「新 surface 一律要有 prompt-secret 斷言」的通則型閘門**。
差別是**逐案 vs 通則**——這正是 [[bridge-smoke-gate]] 反覆記過的閘門涵蓋面問題。

### 2.4 assistant-skills 就是 Anthropic SKILL.md 格式

12 支領域排障 skill（ssh / dns-dhcp / firewall-port / tls-certificate /
network-connectivity / sftp / rdp / terminal-command-planner + 4 支 dashboard 相關），
frontmatter 只有 `name` + `description`，與正本格式一致。

讀了 `ssh-troubleshooter/SKILL.md` 全文，兩個慣例值得抄進自己的 skill 寫法：

- **結尾的「Boundaries」詞彙釘樁段**：把本產品的專有名詞邊界寫死——
  「儲存的資源叫 Connection 不叫 profile」「活的終端狀態叫 Session」
  「secret 屬於 OS keychain，不進 chat 也不進 SQLite」。
  作用是防模型用泛稱詞漂移掉領域語意。
- **工作流裡的排序紀律**：「按證據強度排列可能成因，不是按方便程度排列」；
  以及「不要叫使用者把 secret 貼進 chat」「host key 變更視為資安敏感，
  未經帶外確認前不得叫使用者刪信任紀錄」。

## 3. Step 1 比對表

| 面向 | KKTerm | bridge 現況 | 判定 |
|---|---|---|---|
| ACP client 多 backend | Codex / Claude Agent / **Cursor** | kiro / claude / codex | **部分已有**；Cursor 是第 4 backend 候選 |
| ACP 起不來的退化路徑 | one-shot vendor CLI，明文只當安裝失敗兜底 | **未見等價** | **值得借鏡（K2）** |
| 危險動作核可 | `*.dangerous.*` 命名空間 + 單 flag + `permissionRequired` | 動作層無核可閘門 | **值得重評（K1）** |
| prompt 是投影不是傾倒 | 設計原則 + 新 surface 強制 secret 測試 | 有 preamble 紀律，**未見通則型 secret 斷言閘門** | **值得借鏡（K3）** |
| 對外暴露 MCP server | `kkterm-cli` 給外部 agent 驅動 app | bridge-actions 只服務自己的 in-process agent | **低優先** |
| skill 格式 | Anthropic SKILL.md，隨 repo 出貨 | 同格式，2026-08-08 **刻意移除** `default-skills/` | **context 不同、不衝突** |
| skill 內文慣例 | Boundaries 詞彙釘樁 + 按證據排序 | 正本 skill 無此固定段落 | **小額借鏡（K5）** |
| context 預算 | compaction trigger → 留最新輪、截斷過大單輪、`agent.context_compacted` 落 debug log | 注入側預算 + telemetry + 70%/90% 分層警告 | **已有／不需要** |
| 架構決策記錄 | `docs/ADR/` 13 篇編號 ADR | `docs/SPEC-*.md` + `POLICIES/` | **已有等價**（形式不同） |
| 貢獻者 AI 紀律 | 「Surgical changes only」「No speculative features」+ i18n 強制（zh-TW 不得抄 zh-CN） | development-methodology 的 Karpathy 四原則 | **已有**，bridge 這層更厚 |
| 多 provider 適配 | 明文「需要不同協定/OAuth/SDK 就**不要**硬塞進 openai-compatible adapter」 | 三 backend 各自 def | **已有**（同一個 move） |

「skill 隨 repo 出貨」判成不衝突的理由要寫明：KKTerm 的 skill 是
**出貨給終端使用者的產品內容**，bridge 的 skill 是**跨機器的 agent 設定投影**。
兩者的失效模式不同（前者不會被 sync 靜默覆蓋），∴ 不是 bridge 該回頭抄的東西。

## 4. Step 2 借鏡排序

| # | 項目 | 增量價值 | 成本 | 建議 |
|---|---|---|---|---|
| **K1** | 危險動作核可的廉價形狀（命名空間 + 單 flag + default-deny） | **高**——bridge 的 `send_file`/`delegate`/`schedule` 目前完全無閘門 | 中（須換算方向） | **建議進 Step 3 評估** |
| **K2** | ACP 初始化失敗的 one-shot CLI fallback | 中——現在 adapter 掛了整個 backend 不能用 | 低 | 建議吸收 |
| **K3** | 「新 assistant surface 必須有 prompt-secret 斷言」通則閘門 | 中——有前科，且現有閘門是逐案不是通則 | 低 | 建議吸收 |
| **K4** | Cursor 當第 4 個 ACP backend | 低-中 | 低 | 可選 |
| **K5** | SKILL.md 加 Boundaries 詞彙釘樁段 | 低 | 極低 | 順手做 |

**排除**：對外 MCP server（bridge 無「別的 agent 要驅動我」情境）、context compaction
（[[deepseek-harness]] 已結論壓縮既有歷史結構上不是 bridge 的活）、ADR、skill 隨 repo 出貨。

### ⚠️ K1 必須換算方向，不能照搬

這正是 `ms-external-repo-absorption` 常見錯誤 #2（照搬不適配）的形狀。

KKTerm 是**桌面 app，使用者就坐在螢幕前** ∴ 回一個 `permissionRequired` error
讓呼叫端重試是合理的——人會看到、會去按核可。

bridge 不是：agent 常在**排程輪次、背景通知輪次、specialist 派工**裡跑，沒人在看。
同一個做法搬過來，「回錯誤讓 agent 重試」會變成**靜默卡死**——代價方向相反。

換算後的落點是：**危險動作不回錯誤，而是改走既有的 `ask` 佇列**
（queue 後 turn 結束才 commit，語意已由 [[cloudflare-os]] §4.1 釐清）。
要抄的是「危險性編進命名 + 單一開關 + default-deny」這三件事，不是它的錯誤回傳形狀。

## 5. 誠實邊界（尚未做的事）

- **沒動任何 bridge 的碼**，以上全是提案。
- 沒 clone、沒讀原始碼、沒跑過。[[cloudflare-os]] 那次是 clone 後才把介面契約升到 A 級；
  本頁若要進入實際吸收，K1／K3 的依據應先升級。
- `docs/PRD.md`、`ROADMAP.md`、`CUSTOM_MODULE_*`、`manual/`、`docs/ADR/` 內文全未看
  （ADR 只看到 13 個檔名）。
- **K1 的適用面盤點還沒做**——bridge 到底哪些動作該標 dangerous，
  那是吸收與否的決定性前提，不是實作細節（同 [[cloudflare-os]] B1 的教訓：
  「適用面盤點是決定性前提」，那次盤點結果直接推翻了原本的低估）。
- 授權是 MIT + **Commons Clause** ∴ 若日後有任何「把它的碼搬進商業散布物」的想法，
  必須先看授權；純設計借鏡不受此限。
