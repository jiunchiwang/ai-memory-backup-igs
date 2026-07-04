---
type: concept
title: 跨模型 AI 策略
created: 2026-06-23
updated: 2026-07-05
sources: [f_c3d198, f_7d7ffe, f_e3b009, f_e6394d, f_6d4701, f_0561d8, f_3165ae]
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

## 相關

- [[bridge-project]] — Bridge 是正典的消費者之一
- [[skill-and-eval]] — Skill 的評估與生命週期管理
