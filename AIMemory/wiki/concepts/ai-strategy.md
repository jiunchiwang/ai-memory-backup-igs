---
type: concept
title: 跨模型 AI 策略
created: 2026-06-23
updated: 2026-08-06（Codex CLI 登入狀態更正——內容已於當時補上，此次僅補正 frontmatter 日期與 source ID）
sources: [f_c3d198, f_7d7ffe, f_e3b009, f_e6394d, f_6d4701, f_0561d8, f_3165ae, f_f92692, f_fd8698, f_e68e53, f_4568c1, f_76462d, f_d5d14e, f_0e4a79, f_b9e59d, f_806752]
why: 因為需要讓同一份 skill/steering 跨 Kiro、Claude Code、Codex 多個 AI CLI 共用，所以建立正本集中管理 + 投影分發的架構
---

# 跨模型 AI 策略（v4）

統一管理多個 AI agent CLI 共用的知識資產（skills、steering、facts），以 markdown + git 為唯一真實來源。

## 核心原則

**正典語料庫（canonical corpus）本身就是產品**——CLI / MCP / bridge / 索引都只是部署基礎設施，不是產品本體。

## 架構

```
G:\AI\AI-canonical\          ← 正本（source of truth）
├── skills\general\          ← 通用 skill
├── skills\slot\             ← UK slot 專屬 skill
└── tools\sync.ps1           ← 投影腳本
         ↓ junction/symlink
~/.kiro/skills/              ← Kiro 投影
~/.claude/skills/            ← Claude Code 投影
```

## 儲存政策

| 內容類型 | 位置 | 版控 |
|---------|------|------|
| Skills、steering 政策、通用文件 | GitHub repo（AI-canonical） | ✅ |
| Session 執行日誌、框架內部狀態 | 僅本地 | ❌ |
| 長期記憶（facts、wiki） | 本地 + backup repo | ✅ |

## Skill 新增/修改 SOP

1. 在正本建立 `skills/<domain>/<name>/SKILL.md`
2. 跑 `sync.ps1 -Apply` 投影到各 CLI
3. `git commit && git push`

詳見 `steering/skill-workflow.md`。直接改 `~/.kiro/skills/` 無效（是 junction，會被下次 sync 覆蓋）。

撰寫可攜式 skill 時，若該 skill 會被多個 agent CLI（Kiro、Codex、Claude）或多台機器共用，應避免在 SKILL.md 中寫死絕對路徑（例如特定磁碟機代號或使用者目錄），以免跨環境失效。

## 安全機制

- Headless 自動化（無人值守）時，用 `claude.exe --disallowedTools mcp__memory__remember,mcp__memory__forget` 封鎖記憶寫入，強制走 proposal-only 工作流程
- 避免自動流程擅自改寫長期記憶

## Steering 架構

`closed-loop-system.md`（完整閉環）與 `karpathy-guardrails.md`（精簡 4 原則）共存而非合併：
- **完整閉環**：主 agent 長 session 使用（Phase 1-5、閘門、因果鏈分析）
- **精簡 4 原則**：specialist / delegation / 短任務場景（Think → Simplicity → Surgical → Goal-Driven）
- 理由：省 token 又不失約束；精簡版的力量在「短到能一次讀完就內化」

## Confidence Scoring 量化門檻

memory-to-skill 萃取流程（及 `<<SKILL_PROPOSE>>` 的 agent 端 guardrail）採用量化門檻：

```
confidence = F × C
F = min(出現次數 / 5, 1.0)
C = min(平均消耗 turn 數 / 10, 1.0)
```

| 分數 | 動作 |
|------|------|
| ≥ 0.5 | 進入正式候選 |
| 0.3 – 0.49 | `remember()` 留底觀察 |
| < 0.3 | 跳過 |

靈感來源：ECC continuous-learning-v2 的 instinct confidence scoring。差異在 ECC 用 hooks 即時觀測，bridge 用事後 session 掃描。

## Dev-Design 多 Agent 設計工作流

可重用的設計方法論，四階段：

1. **Explore** — 查證實際程式碼架構（不靠記憶）
2. **Propose** — 產出 3 個互相競爭的設計方案（常收斂到單一寫入匯流點）
3. **Adversarial** — 對抗找出致命缺陷並評分
4. **Synthesize** — 整合出最終規格

效用：在設計初期就能抓出如「多輪迴圈中 snapshot 過期（staleness）」這類隱性 bug，避免實作後才發現。

## Junction 即時反映

AI-canonical-corp 的 slot skill（如 `uk-slot-pattern-library`）透過 Windows junction 直接指向正本目錄，改正本即時反映到 `~/.kiro/skills/`，不需額外跑 `sync.ps1`。這讓 corp（slot 專屬）的 skill 開發比通用 skill 更直覺——改完就生效。

**通用 skill 同樣如此**：`~/.claude/skills` 與 `~/.kiro/skills` 下的 skill 目錄本身就是指向 AI-canonical 正本的 junction（非 copy），改正本即時對這兩個 CLI 生效，不需再跑 `sync.ps1`；`sync.ps1 -Apply` 真正必要的是 steering 那批（copy，非 junction）。**因此正本一律寫在** `G:\AI\AI-canonical\skills\general\`（通用）或 `AI-canonical-corp`（slot/office），絕不直接編輯 `~/.claude/skills` 或 `~/.kiro/skills`——那兩處會被下次 sync 覆蓋。

## sync.ps1 三 CLI 投影擴展至 Codex（2026-08-05，commit `b330aad`）

`sync.ps1` 自本次起一次投三個 CLI，不再只有 Kiro/Claude：

| CLI | Skills 投影 | Steering 投影 |
|---|---|---|
| Kiro | 逐 skill junction 直達正本 | copy 到 `~/.kiro/steering/` |
| Claude | 逐 skill junction 直達正本 | copy 到 `~/.claude/steering/` + `CLAUDE.md` `@import` |
| **Codex（新）** | 逐 skill junction 直達正本（原本是繞經 Kiro 的**二段** junction，已改為**一段**） | copy 到 `~/.codex/steering/` **+ 全文內嵌** `~/.codex/AGENTS.md` 的 `canonical-steering` managed block |

**為何 Codex steering 選「全文內嵌」而非 pointer/`@import`**：Codex 是否支援檔案引用語法未經驗證，內嵌可確定生效；managed block 的 marker 之間每次 sync 覆蓋所以不會漂移，marker 外的手寫內容保留。

**環境狀態（已解，2026-08-06 更新）**：Codex CLI 0.146.1 在這台機器已完成認證（`codex login status` → Logged in using ChatGPT），端到端驗證已可執行——當日實跑兩輪 `codex exec` 異源覆核成功。先前 2026-08-05 記錄的認證障礙已排除。
「Codex 是否真的讀 `~/.codex/AGENTS.md` 全域指令」也已於 2026-08-06 用 canary 字串實測通過（見 `steering/skill-workflow.md`）；[openai/codex#8759](https://github.com/openai/codex/issues/8759) 與 #27705 報告的全域檔不載入在此版本不重現。

**仍未解**：`codex app-server` 在這台機器是壞的（`failed to initialize sqlite state runtime under ~/.codex`，穩定重現）。`codex exec` / `codex login` 都正常，只有 app-server 這條路徑掛。副作用是 Claude Code 的 `codex:setup` 透過 app-server 探測登入狀態，因此會誤報 `loggedIn: false`——以 `codex login status` 為準。
另外 `codex exec -s read-only` 的執行政策會擋掉 git（連 `git --version` 都 rejected by policy），派 Codex 做 push 前覆核時要先把 `git show <commit>` 匯出成檔案再餵路徑，否則它只讀得到工作區現況。

**已確認的事實**：Codex CLI 0.146.x 原生支援 skills 機制（掃 `~/.codex/skills/`，內建 skill 放 `.system/` 子目錄），SKILL.md frontmatter 格式與 Claude 完全一致（`name` + `description`），因此同一份 skill 正本可三個 CLI 共用不需改寫。

**已知既存漂移（本次未動，待決定）**：`~/.kiro/steering/karpathy-guardrails.md` 沒有對應的 AI-canonical 正本（正本 steering 只有 `closed-loop-system` / `skill-workflow` / `task-acknowledgement` 三支），所以 Kiro 吃著一份 Claude 與 Codex 都拿不到的 steering——要嘛補進正本，要嘛確認為 Kiro 專屬。

## MCP-First 邊界說明（2026-07-17）

正本三份 skill（`ms-agent-scheduled-prompts`、`ms-agent-text-token-signaling`、`ms-telegram-ask-button-protocol`）已更新統一邊界規則：bridge-managed session 優先呼叫 `bridge-actions` MCP tool，只有明確回報 unavailable 才退回文字 token 協定；validation/policy 錯誤須修參數，不可用文字 token 繞過（commit d6853e2，未 push）。此規則反映 [[bridge-project]] 的 `bridge-actions` MCP 上線後，正本文件需同步更新消費端行為的慣例。

## 相關

- [[bridge-project]] — Bridge 是正典的消費者之一
- [[skill-and-eval]] — Skill 的評估與生命週期管理
