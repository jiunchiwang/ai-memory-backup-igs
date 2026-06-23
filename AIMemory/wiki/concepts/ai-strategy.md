---
type: concept
title: 跨模型 AI 策略
created: 2026-06-23
updated: 2026-06-24
sources: [f_c3d198, f_7d7ffe, f_e3b009, f_e6394d]
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

## 安全機制

- Headless 自動化（無人值守）時，用 `claude.exe --disallowedTools mcp__memory__remember,mcp__memory__forget` 封鎖記憶寫入，強制走 proposal-only 工作流程
- 避免自動流程擅自改寫長期記憶

## Steering 架構

`closed-loop-system.md`（完整閉環）與 `karpathy-guardrails.md`（精簡 4 原則）共存而非合併：
- **完整閉環**：主 agent 長 session 使用（Phase 1-5、閘門、因果鏈分析）
- **精簡 4 原則**：specialist / delegation / 短任務場景（Think → Simplicity → Surgical → Goal-Driven）
- 理由：省 token 又不失約束；精簡版的力量在「短到能一次讀完就內化」

## 相關

- [[bridge-project]] — Bridge 是正典的消費者之一
- [[skill-and-eval]] — Skill 的評估與生命週期管理
