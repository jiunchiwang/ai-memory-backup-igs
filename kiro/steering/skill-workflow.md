# Skill 新增/修改工作流程

正本是唯一 source of truth，各 CLI skill 目錄都是可重建投影。

## 正本位置

```
G:\AI\AI-canonical\skills\<domain>\<skill-name>\SKILL.md
```

- `domain`：`general`（通用）或 `slot`（UK 老虎機）
- `skill-name`：kebab-case

## 新增 Skill 步驟

1. **在正本建立** `skills/<domain>/<skill-name>/SKILL.md`
2. **跑投影** `powershell G:\AI\AI-canonical\tools\sync.ps1 -Apply`
3. **Commit + Push**：`cd G:\AI\AI-canonical && git add skills/ && git commit && git push`

## SKILL.md 最小模板

```markdown
---
name: <skill-name>
description: <何時該觸發這個 skill：情境 + 觸發語 + 邊界。寫給「還不知道內容的 agent」看>
type: skill
domain: general
created: YYYY-MM-DD
tags: []
source: session
---

# <skill-name>

<何時觸發這個 skill 的一段描述>

## 觸發條件

- ...

## 步驟

1. ...
```

⚠️ **`name` 與 `description` 是必填**，不是選填的補充欄位。缺任一個，
Codex 會直接拒載該 skill（`failed to load skill ...: missing field description`），
Claude Code 則 fallback 成「description = skill 名字」，等於 agent 無法判斷何時該觸發它——
skill 檔案還在，但實際上是死的，而且不會有任何錯誤訊息。

`type`/`domain`/`created`/`tags`/`source` 是自用 metadata，loader 不讀，可省。

檢查全部正本 skill 的 frontmatter 是否齊備：

```powershell
Get-ChildItem G:\AI\AI-canonical\skills,G:\AI\AI-canonical-corp\skills -Recurse -Filter SKILL.md |
  ForEach-Object {
    $l = Get-Content $_.FullName
    if ($l.Count -eq 0 -or $l[0].Trim() -ne '---') { "[NO-FRONTMATTER] $($_.FullName)"; return }
    $end = 1; while ($end -lt $l.Count -and $l[$end].Trim() -ne '---') { $end++ }
    if ($end -ge $l.Count) { "[UNCLOSED] $($_.FullName)"; return }
    $fm = $l[1..($end-1)]
    if (-not ($fm -match '^\s*name\s*:'))        { "[NO-NAME] $($_.FullName)" }
    if (-not ($fm -match '^\s*description\s*:')) { "[NO-DESCRIPTION] $($_.FullName)" }
  }
```

## 正本歸屬判斷

| 條件 | 正本 repo | 路徑 |
|------|-----------|------|
| 使用者明確指定歸屬 | 依使用者指示 | — |
| UK slot 專屬（slot-、uk-slot-、pq3-、cocos-） | AI-canonical-corp | `G:\AI\AI-canonical-corp\skills\slot\` |
| 通用工具/方法論/其他 | AI-canonical | `G:\AI\AI-canonical\skills\general\` |

優先級：使用者指示 > 前綴/內容判斷。拿不準時問使用者。

## 修改既有 Skill

直接改正本的 SKILL.md（junction 會即時反映到各 CLI），改完 commit + push。

## 禁止事項

- ❌ 直接在 `~/.kiro/skills/`、`~/.claude/skills/` 或 `~/.codex/skills/` 裡新增或編輯（會被下次 sync 覆蓋）
- ❌ 手改 `~/.codex/AGENTS.md` 的 `canonical-steering` managed block（同上，改正本）
- ❌ 把公司 raw code 寫進 SKILL.md（distilled-only 原則）

## 投影機制

`tools/sync.ps1 -Apply`（三個 CLI 一次投完）：

| 來源 | Kiro | Claude | Codex |
|------|------|--------|-------|
| skills | junction `~/.kiro/skills/` | junction `~/.claude/skills/` | junction `~/.codex/skills/`（逐 skill，不碰它的 `.system`）|
| steering `.md` | copy `~/.kiro/steering/`（開機自動載入）| copy `~/.claude/steering/` + `CLAUDE.md` `@import` | copy `~/.codex/steering/` + **全文內嵌** `~/.codex/AGENTS.md` managed block |

Codex 走「全文內嵌」而非 pointer/import，是因為它是否支援 `@` 檔案引用未經驗證；
內嵌由 sync 每次覆蓋 marker 之間的內容，所以不會與正本漂移，marker 外的手寫內容保留。

✅ Codex 讀 `~/.codex/AGENTS.md` **已於 2026-08-06 在本機實測通過**（codex-cli 0.146.1、Windows）。

驗法：在一個沒有本地 `AGENTS.md` 的空目錄跑 `codex exec`，要求「不准用工具、只從 instructions 回答」，
引用 managed block 裡一段不可能猜到的原文；它一字不差回出來（連行尾兩空格斷行都保留）。
openai/codex#8759、#27705 報告的全域檔不載入在此版本不重現。

⚠️ 但 `codex app-server` 在本機是壞的：
`failed to initialize sqlite state runtime under C:\Users\<user>\.codex`（穩定重現）。
`codex exec` / `codex login` 都正常，只有 app-server 這條路徑掛。
副作用：Claude Code 的 `codex:setup` 透過 app-server 探測登入狀態，
因此會誤報 `loggedIn: false`——別被它騙了，以 `codex login status` 為準。
