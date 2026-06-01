---
name: ms-portable-skill-authoring
description: 當寫 skill 會被多個 agent CLI（Kiro / Codex / Claude）或多台機器共用、要避免把 F:\AI\AIMemory 或 ~/.kiro 這類絕對路徑寫死在 SKILL.md、或要讓 bridge 把環境差異注入成變數讓同一份 SKILL.md 跨機器重用時使用
---

# 可攜式 Skill 撰寫（不寫死路徑、環境變數由 bridge 注入）

## 概述

同一份 SKILL.md 常常要在多台機器、多個 agent CLI 下重用：Kiro 在 `C:\Users\alice\.kiro\skills\`，Codex 在 `C:\Users\bob\.codex\skills\`，Claude 在 `~/.claude/skills/`；memory 目錄也各自不同。如果 SKILL.md 寫死 `F:\AI\AIMemory\facts-123.md`，搬過去就壞。

解法：**bridge 啟動時偵測環境，把路徑注入成變數（`${MEMORY_DIR}`、`${SKILL_DIR}`、`${AGENT_CONFIG_DIR}`、`${USER_ID}`），skill 只引用變數不引用實值**。

## 何時使用

- 寫 / 改 `ms-*` skill、特別是涉及讀寫 memory 檔、skill 檔、agent config 檔
- 設計要部署到多台機器的 bridge / memory system
- 支援多個 ACP agent（Kiro + Codex + Claude）同時讀同一份 skill 集
- SKILL.md 裡出現 `F:\`、`C:\Users\xxx\`、`~/.kiro`、`~/.codex` 之類的絕對路徑

## 不要用在

- 純範例、反例說明（「不要這樣 log → `F:\AI\secret.env`」這種**示範性路徑**不用抽變數，那是教學內容）
- skill 只跑在單機且永遠不搬（少見，多數 skill 都會被 sync）
- 變數名稱對 LLM 來說反而更難讀的情境（例如只有一個路徑、沒 portability 需求）

## 四個標準變數

由 bridge 的 `Environment preamble` 區塊注入：

| 變數 | 意義 | Kiro 典型值 | Codex 典型值 | Claude 典型值 |
|---|---|---|---|---|
| `${MEMORY_DIR}` | 長期記憶根目錄（facts 主 log + shard + schedules） | `F:\AI\AIMemory` | `F:\AI_Codex\AIMemory` | `F:\AI_Claude\AIMemory` |
| `${SKILL_DIR}` | 目前 agent 的 skill 根（= `AGENT_CONFIG_DIR/skills`） | `C:\Users\tonykuo\.kiro\skills` | `C:\Users\user\.codex\skills` | `~/.claude/skills` |
| `${AGENT_CONFIG_DIR}` | agent CLI 的 config 家目錄（routing table、agent config） | `C:\Users\tonykuo\.kiro` | `C:\Users\user\.codex` | `~/.claude` |
| `${USER_ID}` | Telegram / 使用者 ID，fact 檔命名用 | `763055942` | 同左 | 同左 |

也有**衍生慣例**（不是變數但要記）：

- Session 檔 → `${MEMORY_DIR}/sessions/`
- 歸檔 session → `${MEMORY_DIR}/oldSessions/`
- 主 fact log → `${MEMORY_DIR}/facts-${USER_ID}.md`
- Topic shard → `${MEMORY_DIR}/facts_Topic/${USER_ID}/<topic>.md`
- NotebookLM routing table → `${AGENT_CONFIG_DIR}/notebooklm-routing.json`

## 核心模式

### Before（寫死，不可攜）

```markdown
## Step 1 — 掃描 sessions
先跑 `ls F:\AI\AIMemory\sessions\*.md`，挑大的先讀。

## Step 2 — 比對既有 skill
讀 `C:\Users\tonykuo\.kiro\skills\ms-*\SKILL.md` 的 frontmatter。
```

問題：在 Codex 機器上完全跑不起來。

### After（變數化，可攜）

```markdown
## Step 1 — 掃描 sessions
先跑 `ls ${MEMORY_DIR}/sessions/*.md`，挑大的先讀。
實際值從本 session preamble 的 `[Environment]` 區塊讀：
  MEMORY_DIR=F:\AI\AIMemory（Kiro）或 F:\AI_Codex\AIMemory（Codex）。

## Step 2 — 比對既有 skill
讀 `${SKILL_DIR}/ms-*/SKILL.md` 的 frontmatter。
```

## Bridge 端怎麼實作注入（給會改 bridge 的人）

一、在 `buildPreamble` 塞一段 Environment block：

```
[Environment — machine-specific paths the bridge resolved for this session]
Skills and notes that need filesystem paths should reference these variables,
not hard-coded values. This lets the same SKILL.md work on multiple machines.
- MEMORY_DIR=<實值>
- SKILL_DIR=<實值>
- AGENT_CONFIG_DIR=<實值>
- USER_ID=<實值>
Conventions: sessions are under ${MEMORY_DIR}/sessions/, archived under
${MEMORY_DIR}/oldSessions/, master fact log at ${MEMORY_DIR}/facts-${USER_ID}.md,
topic shards at ${MEMORY_DIR}/facts_Topic/${USER_ID}/<topic>.md.
Agent-wide config files (routing tables, agent configs) live under
${AGENT_CONFIG_DIR}/ — e.g. ${AGENT_CONFIG_DIR}/notebooklm-routing.json.
[End environment]
```

二、`AGENT_CONFIG_DIR` 的 heuristic：

```typescript
function detectAgentConfigDir(): string {
  // 1. env override 最優先
  if (process.env.AGENT_CONFIG_DIR) return process.env.AGENT_CONFIG_DIR;

  // 2. 從 ACP_AGENT_COMMAND 推：含 "kiro" → ~/.kiro、"codex" → ~/.codex、"claude" → ~/.claude
  const cmd = (process.env.ACP_AGENT_COMMAND ?? "").toLowerCase();
  const home = os.homedir();
  if (cmd.includes("codex")) return path.join(home, ".codex");
  if (cmd.includes("claude")) return path.join(home, ".claude");
  if (cmd.includes("kiro"))  return path.join(home, ".kiro");

  // 3. fallback：看哪個目錄先存在
  for (const name of [".kiro", ".codex", ".claude"]) {
    if (fs.existsSync(path.join(home, name))) return path.join(home, name);
  }
  throw new Error("cannot detect AGENT_CONFIG_DIR; set env var explicitly");
}
```

三、`SKILL_DIR = ${AGENT_CONFIG_DIR}/skills`、`MEMORY_DIR` 與 `USER_ID` 分別由 `.env` / config 提供（`MEMORY_DIR` 預設 `./AIMemory`，`USER_ID` 從 `TG_ACTIVE_USER_ID` 或 `MEMORY_USER_ID`）。

四、**寫一個 smoke script**（`npm run check-env`）驗四種 case：

- `ACP_AGENT_COMMAND=kiro-cli acp` → `.kiro`
- `ACP_AGENT_COMMAND=codex-acp` → `.codex`
- `ACP_AGENT_COMMAND=claude-agent-acp` → `.claude`
- `AGENT_CONFIG_DIR=F:\custom\path` → 強制 override

四個全綠才上線。

## 寫 skill 時的具體守則

1. **SKILL.md 的 YAML frontmatter `description`** 可以用 `${AGENT_CONFIG_DIR}` 這類變數，不要寫 `~/.kiro`
2. **程式碼範例裡**的檔路徑用變數：`read ${MEMORY_DIR}/facts-${USER_ID}.md`
3. **指令範例**寫兩行：一行帶變數（canonical）、一行帶 Kiro 典型值（方便 human eyeball）
4. **教學性反例、背景說明**保持絕對路徑沒關係——那是說故事不是指令
5. 寫完後做一次 `grep` 自我審查：

   ```
   grep -E '(F:\\AI|C:\\Users\\[^\\]+\\\.kiro|C:\\Users\\[^\\]+\\\.codex|~/\.kiro|~/\.codex)' SKILL.md
   ```

   命中的地方檢查是不是真的該抽變數

## 跨 agent Policy 共用：three-stub pattern

SKILL.md 是 **agent-specific**（寫進 `${SKILL_DIR}` 下，各 agent 各自一份）。但有些規則是**三邊通用 + bridge 層級**（例如「preamble frozen-snapshot policy」「Windows shell safety」），該放 repo root 而非 skills 目錄：

- 給 bridge 開發者 + 三種 agent（Kiro / Codex / Claude）都看得到
- 改一次三邊同步
- Bridge repo clone 下來就有（不靠本機 `~/.kiro/`、`~/.codex/` 目錄）

### Layout：POLICIES/ 原文 + 三個 stub

Bridge repo root 的 layout：

```
<bridge-repo>/
├── POLICIES/                          ← 唯一 source of truth
│   ├── README.md                      ← 索引 + 新增/修改流程
│   ├── preamble-frozen-snapshot.md    ← bridge preamble 凍結規則
│   └── windows-shell-safety.md        ← PowerShell / cmd.exe 注意事項
├── AGENTS.md                          ← Codex 自動讀；stub 指 POLICIES/
├── CLAUDE.md                          ← Claude Code 自動讀；stub 指 POLICIES/
├── .kiro/
│   └── steering/
│       └── policies.md                ← Kiro 自動讀；stub 指 POLICIES/
├── .gitignore                         ← 有 `.kiro/` entry（Kiro 個人設定）
└── src/...
```

### 三邊 entry point 各自怎麼吃

| Agent | Entry point | 版控 | 使用者做什麼 |
|---|---|---|---|
| **Kiro CLI** | `.kiro/steering/*.md` 啟動自掃注入 system prompt | ❌（被 `.gitignore` 擋） | 本機手建 stub，或 clone 後 bridge 啟動時自動建 |
| **Codex** | repo root `AGENTS.md`（進 repo 自動讀） | ✅ 進 git | 直接 clone 拿到 |
| **Claude Code** | repo root `CLAUDE.md`（進 repo 自動讀） | ✅ 進 git | 直接 clone 拿到 |

**關鍵限制**：`.kiro/` **被 `.gitignore` 擋**（Kiro 個人設定，不進版控）→ Kiro 使用者 clone 下來 **沒有** `.kiro/steering/policies.md`。這表示：

- 跨 agent 共用規則**必須放在 repo root**（`AGENTS.md`、`CLAUDE.md`、`POLICIES/`）才會真正 push 到 GitHub
- Kiro 端的 stub 是**本機配置**，等同「使用者告訴 Kiro：去讀 `POLICIES/` 原文」
- 原文 `POLICIES/*.md` 必須進版控，不能只放 `.kiro/steering/` 裡面

### Stub 內容範本

**AGENTS.md**（Codex 讀）：

```markdown
# Repository Policies for Codex

This repo ships AI-agent-relevant policies under `POLICIES/`.
Read those files for invariants that must not be broken when modifying code.

- `POLICIES/preamble-frozen-snapshot.md` — bridge preamble build timing, forbidden mid-session operations
- `POLICIES/windows-shell-safety.md` — PowerShell / cmd.exe pitfalls
- `POLICIES/README.md` — how to add / modify policies

Policies in this directory are authoritative — don't duplicate their content
elsewhere. If you need a new policy, add it under `POLICIES/` and link from
this file.
```

**CLAUDE.md**（Claude 讀）：

```markdown
# Repository Policies for Claude Code

Policies that apply to all AI agents operating on this repo live in `POLICIES/`.
Read them before making changes that touch preamble, sessions, or shell scripts.

- `POLICIES/preamble-frozen-snapshot.md`
- `POLICIES/windows-shell-safety.md`
- `POLICIES/README.md` — policy maintenance guide
```

**`.kiro/steering/policies.md`**（Kiro 讀，本機配置）：

```markdown
# Kiro Steering → Shared Policies

This file points Kiro CLI at the shared policy directory under this repo:

  <absolute-path-to-repo>/POLICIES/

Files to read:
- <repo>/POLICIES/preamble-frozen-snapshot.md
- <repo>/POLICIES/windows-shell-safety.md
- <repo>/POLICIES/README.md

(Other agents read `AGENTS.md` / `CLAUDE.md` at repo root, which are stubs
pointing to the same `POLICIES/` directory.)
```

**重要**：`.kiro/steering/` 裡不要放 full copy（例如直接把 `windows-shell-safety.md` 複製過來），只放 stub。Full copy 會跟 `POLICIES/` 原文漂移。

### 驗證 stub 是否真的被 agent 讀進 system prompt

Kiro / Codex / Claude 都不暴露 prompt inspection tool，沒有直接辦法看 stub 是否注入。**間接驗法**：

> 問一個**記憶 facts 沒覆蓋**、但 **POLICIES/ 原文有寫** 的細節。

例如：POLICIES/preamble-frozen-snapshot.md 提到 `session.memoryPreamble` 和 `session.preambleBreakdown` 兩個具體欄位名，但 memory shard 只寫到「preamble 是 frozen snapshot」概念層。

- 新 session 後問：「preamble policy 的 TL;DR 說什麼」
- **答得出**具體欄位名（`session.memoryPreamble`、`session.preambleBreakdown`、第一個 `client.prompt()` 注入時機）→ stub 有吃到原文 ✓
- **只答得出**概念層（「preamble 只在 session create 時建」）→ stub 沒注入或 agent 沒讀到 ✗

同樣做法對三個 agent 都可驗。

### POLICIES/README.md 的角色

索引 + 維護流程：

```markdown
# Repository Policies

Authoritative policies for any AI agent operating on this repo.

## Files
- preamble-frozen-snapshot.md  — preamble build timing invariant
- windows-shell-safety.md      — PowerShell / cmd.exe pitfalls

## Adding a new policy
1. Write `POLICIES/<name>.md` with invariant + rationale + checklist
2. Add link to `AGENTS.md`, `CLAUDE.md`
3. Add link to `.kiro/steering/policies.md` (local, not in git)
4. Commit `POLICIES/`, `AGENTS.md`, `CLAUDE.md`

## Three-stub layout (why)
See ms-portable-skill-authoring skill for the rationale — `.kiro/` is
gitignored (personal settings), so cross-agent rules must live at
repo root (`POLICIES/`) to reach Codex and Claude users via clone.
```

### Skill 裡自帶「實值由 bridge 注入」短註解

第一次出現 `${MEMORY_DIR}` / `${SKILL_DIR}` / `${AGENT_CONFIG_DIR}` 時加一行：

```markdown
（實值由 bridge 的 Environment preamble 注入。Kiro 常見 `F:\AI\AIMemory`、
Codex 常見 `F:\AI_Codex\AIMemory`。）
```

這樣沒 context 的讀者（或另一個 agent 拿 SKILL.md 當 reference）也能自己找到實值。

## Skill 作者 checklist

寫新 skill / rewrite 既有 skill 時過一遍：

- [ ] frontmatter description 不含絕對路徑
- [ ] 第一次出現 `${MEMORY_DIR}` / `${SKILL_DIR}` / `${AGENT_CONFIG_DIR}` / `${USER_ID}` 時有一行短註解「實值由 bridge Environment preamble 注入」
- [ ] 指令範例用變數，旁邊可附 typical value 當注釋
- [ ] 絕對路徑只出現在「反例」「故事背景」「範例踩坑記錄」
- [ ] 在 Kiro 跑過一次 smoke、在 Codex 機器跑一次、在 Claude 機器跑一次（至少其中兩個）
- [ ] 如果規則涉及「所有 agent 都要遵守」層級，放 `POLICIES/` 而不是 `${SKILL_DIR}/ms-*/SKILL.md`

## 稽核既有 skill（TODO / 不定期跑）

這個 skill 是 2026-05 才建立的，**比它早寫的 skill 很多都還帶著寫死路徑**。定期跑下面稽核流程把債還掉（不要一次全改，每次改 skill 順便對齊即可）。

### 一、掃當前違規（兩條硬編路徑）

```powershell
# 用 Kiro 這台當 ground truth；其他機器跑同樣 pattern 換掉前綴
grep -r "C:\\\\Users\\\\tonykuo\\\\" "${SKILL_DIR}" --include=SKILL.md
grep -r "F:\\\\AI\\\\AIMemory" "${SKILL_DIR}" --include=SKILL.md
```

**分辨合法 vs 違規**：

| 命中情境 | 合法 / 違規 |
|---|---|
| 對照表的一格（`\| ... \| F:\AI\AIMemory \| F:\AI_Codex\AIMemory \|`） | ✅ 合法（這就是對照表的目的） |
| `description: ... 避免把 F:\AI\AIMemory ...` 反例說明 | ✅ 合法（教學性反例） |
| 範例輸出（`ok: appended to F:\AI\AIMemory\facts-xxx.md`） | ✅ 合法（那是 tool log，不是 skill 指令） |
| **指令範例寫死 `py C:\Users\tonykuo\.kiro\skills\<skill>\...`** | ❌ **違規** — 改 `${SKILL_DIR}/<skill>/...` |
| **絕對路徑當成 command template 給使用者照抄** | ❌ **違規** — 改變數 |

### 二、已知違規 skill 清單（2026-05-03 snapshot）

| Skill | 違規行 | 修法 |
|---|---|---|
| `slot-codegen-anchor-merge` | L38, L41 指令寫死 `C:\Users\tonykuo\.kiro\skills\slot-codegen-anchor-merge\anchor_merge.py` | 改 `${SKILL_DIR}/slot-codegen-anchor-merge/anchor_merge.py` |
| `slot-codegen-regression-check` | L34, L43, L48 同型 | 同上 |
| `slot-art-manifest-validator` | L35, L45, L48 同型 | 同上 |
| `uk-slot-spec-adapter` | L35 同型 | 同上 |

共 4 支 skill、9 個違規行。這份清單**會隨時間過期**，每次進入這個 TODO section 前先重新跑第一步的 `grep` 驗證。

### 三、修法 template（before → after）

```markdown
<!-- before -->
py C:\Users\tonykuo\.kiro\skills\slot-codegen-anchor-merge\anchor_merge.py --new <expected.ts> <output.ts>

<!-- after -->
py ${SKILL_DIR}/slot-codegen-anchor-merge/anchor_merge.py --new <expected.ts> <output.ts>
（實值由 bridge Environment preamble 注入；Kiro 典型 `C:\Users\tonykuo\.kiro\skills`、Codex 典型 `C:\Users\user\.codex\skills`）
```

**第一次出現變數的那個 skill** 才加一行短註解；同一份 SKILL.md 後面再出現不用重複。

### 四、為什麼不一次全改

- 違反「workflow 已動就別改」原則：有些 slot-codegen skill 正被 slot 專案引用，批次 mutation 風險高
- 作者在改哪個 skill 就順便對齊那一份，技術債「沿途清理」比「專門清理」健康
- 這份 TODO 當**checklist for the next time you touch one of these skills**，不是當 sprint 任務

## Common Mistakes

| 錯誤 | 修正 |
|---|---|
| SKILL.md 到處寫 `F:\AI\AIMemory\...` | 全部改 `${MEMORY_DIR}/...`，在開頭列變數 → 典型值對照表 |
| 寫 `~/.kiro/skills` 當 skill 目錄 | 改 `${SKILL_DIR}`（= `${AGENT_CONFIG_DIR}/skills`） |
| 把 routing table、agent config 放 `${MEMORY_DIR}` | 那是 agent 層的東西，應該 `${AGENT_CONFIG_DIR}` |
| 在 Codex 機器直接複製 Kiro 的 skill 檔但沒有 bridge 支援環境 preamble | 先在 bridge 加 `detectAgentConfigDir`，再 sync skill 過去 |
| heuristic 判 agent 只看 `command` 字串 | 加 env override 當逃生口（`AGENT_CONFIG_DIR=...`） |
| 新機器沒 `.kiro/`、`.codex/` 任一目錄，heuristic fallback 失敗 | fallback 失敗就 throw + 提示使用者設 env；不要假設一個預設值 |
| 把 `MEMORY_DIR` 和 `AGENT_CONFIG_DIR` 混用（例如記憶檔塞進 `~/.kiro`） | 明確職責切分：bridge 的資料 → MEMORY_DIR；agent CLI 的 config → AGENT_CONFIG_DIR |
| 變數用大括號寫成 `{MEMORY_DIR}` 或 `$MEMORY_DIR` | 統一 `${MEMORY_DIR}` 風格，跟 shell variable expansion 一致 |
| 跨 agent 共用規則只放 `.kiro/steering/` | `.kiro/` 被 `.gitignore` 擋，Codex/Claude 使用者 clone 拿不到；必須 `POLICIES/` + 三個 stub |
| `.kiro/steering/*.md` 放 full copy 不是 stub | 會跟 `POLICIES/` 原文漂移；只放 stub 指回原文 |
| AGENTS.md / CLAUDE.md 直接複製 POLICIES/ 全文 | 同上，維護時要改三處；只寫 stub，維護時改 `POLICIES/` 一處 |

## SKILL_PROPOSE 量化門檻

Agent 發出 `<<SKILL_PROPOSE:...>>` 前必須通過此 guardrail：

1. **計數**：grep dailylog + facts，計算該 pattern 出現幾次（相似 keyword / 相同操作流程）
2. **門檻**：
   - < 3 次 → **不 propose**。改為 `remember("pattern: <描述> 出現 N 次")` 留底
   - ≥ 3 次 → 允許 propose
3. **reason 裡附計數**：`reason` 欄位須包含「出現 N 次」佐證，例如 `"dailylog 出現 4 次 + facts 2 條相關"`

這避免「只做過一次就抽 skill」的過早抽象。3 次比業界常見的 5 次低，因為我們跨專案場景少，3 次已夠顯著。

## 相關

- **ms-agent-long-term-memory** — `${MEMORY_DIR}` 下的 fact 檔 / shard / topics.json 設計
- **ms-acp-protocol-limitations** — `${AGENT_CONFIG_DIR}` 各 agent 的 config 格式差異（Kiro main.json vs Codex config.toml）
- **ms-notebooklm-routing-builder** — 用 `${AGENT_CONFIG_DIR}/notebooklm-routing.json` 的實例
- **memory-to-skill** — 自身就是一個跨機器 skill 的範例（Kiro + Codex 版本差異就是路徑）
