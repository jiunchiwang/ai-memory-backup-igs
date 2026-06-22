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

- ❌ 直接在 `~/.kiro/skills/` 或 `~/.claude/skills/` 裡新增或編輯（會被下次 sync 覆蓋）
- ❌ 把公司 raw code 寫進 SKILL.md（distilled-only 原則）

## 投影機制

`tools/sync.ps1 -Apply`：
- skills → junction 到 `~/.kiro/skills/` + `~/.claude/skills/`
- steering `.md` → copy 到 `~/.kiro/steering/`
