---
title: Bridge Persona 人格系統
type: concept
created: 2026-08-20
updated: 2026-08-20
sources: [f_1bd398, f_5247b2, f_145db3, f_0c20d9, f_3fafee, f_3bf9d1]
---

# Bridge Persona 人格系統

## 概述

telegram-kiro-bridge 的角色人格功能（首個人格：哆啦A夢），讓 bridge 的 Claude backend 在互動時帶一個可設定的語氣人格，同時把工程紀律（承重核、事實主張閘門、push back 格式等）完全隔離在人格檔之外。Stage 1（通道 + `/dream` 維運隔離）已實作完成於分支 `feat/persona-stage1`（12 commit），但因跨 vendor 覆核抓到兩條 Critical 而尚未 push。

## 設計定案（v4）

- **人格只放語氣個性關係**，工程紀律完全不進 persona 檔——紀律留在 `CLAUDE.md`／`POLICIES/` 那一層，不會因為切換人格而跟著變。
- **注入通道走 Claude ACP 的 `_meta.systemPrompt.append`**，不是 preamble——preamble 有凍結快照政策（見 [[bridge-project]]），人格切換不能違反它。
- **僅支援 Claude backend**：這是 Stage 1 的明確 scope 邊界，不是疏漏；Kiro／Codex 的重新測試是 Stage 3 的範圍。

## 四階拆解

使用者於 2026-08-20 核可將功能拆成四個階段推進，並要求先做 Stage 1：

1. **Stage 1** — 注入通道 + `/dream` 維運隔離（人格不能污染夜間維運寫進去的長期記憶）
2. **Stage 2** — `/persona` 指令與人格切換
3. **Stage 3** — Kiro／Codex 重新測試，並補惡意 persona（prompt injection 類）測試
4. （第四階未在 fact 中具體展開）

## 人格檔慣例

正本位於 `personas/*.md`，**進版控**——比照 `plan-templates/*.json` 的「模板是資料不是程式碼」慣例，新增一個人格只需加檔案，不需改 code。首個人格 `doraemon.md` 逐字複製自使用者提供的原始 System Prompt 文件，不做任何改寫。

## 外部建議的取用與反駁

使用者提供兩份外部 AI 對「Codex ACP 如何加入角色人格」的建議文件。其中一份的 **Persona／Behavior 解耦概念**被採用（比原設計乾淨）；但同一份文件建議的兩個具體實作方向——**Kiro Custom Agent** 與 **`claude -p --append-system-prompt`**——都經實測反駁，不適用於本專案的 ACP 架構。這是「概念可用、具體實作建議不可用」的典型案例，取用外部建議時要分開評估這兩層。

## 連動的環境變更（與 persona 無關但同時做）

使用者移除全域 `@zed-industries/codex-acp@0.15.0`、安裝 `@agentclientprotocol/codex-acp@1.6.0`。舊版經實測已不可用（prompt 被 API 打回 400 錯誤，訊息指出需要更新版本的 Codex）。此更換獨立於 persona 功能，但在同一輪工作中一併處理。

## 相關

- [[bridge-project]] — preamble 凍結快照政策、bridge 整體架構
- [[bridge-acp]] — ACP adapter 能力矩陣（`_meta.systemPrompt` 通道與各 backend 支援差異的根源）
- [[bridge-dream]] — `/dream` 夜間維運框架（Stage 1 隔離的對象）
- [[adversarial-review]] — persona Stage 1 的跨 vendor 覆核（11 輪同源覆核判 READY、換 vendor 一輪抓到兩條 Critical 的實例，見該頁「輪數不能替代 vendor 多樣性」節）
