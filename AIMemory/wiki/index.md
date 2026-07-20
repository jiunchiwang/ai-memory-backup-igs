# Wiki Index

> Source of truth: `facts-509424983.md`（master log）
> Wiki 是 derived 綜合層，facts 有衝突時以 facts 為準。

## Pages

- [[uk-slot]] — UK 市場老虎機專案群（1 模板 + 7 遊戲 + 1 demo、codegen 整合、Clash of Olympus、spec-to-impl 教訓、回灌工作流、錯誤分類法）
- [[uk-slot-template]] — UK Slot 模板專案（三種 FillStrategy、起新專案慣例、回灌工作流、命名規範）
- [[uk-slot-codegen]] — UK Slot Codegen 工具整合（定位 M0a~M1 加速器、anchor merge 限制、驗證結果、回饋修正）
- [[uk-917]] — uk_917 3 Leprechaun's Pots（遊戲輪廓、M0a 進度、proto stub、規格確認事項）
- [[uk-slot-clash-olympus]] — Clash of Olympus 諸神之戰（6×4 4096 Ways、VS Feature 🔴、spec-to-impl 完成、待確認 8 項）
- [[uk-slot-eye-strike]] — Eye Strike 系列（第一代 uk_658 + 續作 uk_872、7 個專案特有機制、SpineKit 規範）
- [[bridge-project]] — Telegram-Kiro-Bridge 專案（架構、AIMemory、Rich Messages、Reply Context、Smoke 隔離、Specialist Dashboard、Status Server 加固）
- [[bridge-acp]] — Bridge ACP 與 Model 配置（adapter 切換差異、/agent 熱切換、model pin、harness hooks、trailer 陷阱）
- [[bridge-session]] — Bridge Session 生命週期（archive 蒸餾層、ACP resume、/session 多 session、transcript 路徑）
- [[bridge-streaming]] — Bridge Streaming 與訊息渲染（Draft API 三階段 lifecycle、4096 截斷、rate limit、Rich Messages）
- [[bridge-memory]] — Bridge 記憶與維運系統（AIMemory 結構、/dream 14 步維運、factlint 三層防禦、topic 分類、wiki 知識庫、embedding router、備份）
- [[bridge-specialist]] — Bridge Specialist 分身系統（配置、token 執行權限層、PARALLEL_DELEGATE cross-check、Dashboard 監控）
- [[bridge-research]] — Bridge 改善研究與 Roadmap（外部框架借鏡、fable-advisor context packaging、claude-plugins-official Permission Relay、PostTool Hooks A→D、Karpathy P0、Rich Messages Draft）
- [[dev-tools]] — 開發工具與環境設定（Python/Playwright/TypeScript、機器路徑、工作流程）
- [[agent-system-architecture]] — Agent 系統五層架構（公司比喻：Agent/MCP/Memory/Workflow/Agent SDK 的角色與關係）
- [[spine-viewer]] — Spine Viewer 插件（Cocos Creator 編輯器擴充，批次掃描 DrawCall/Triangle 效能報告）
- [[ai-strategy]] — 跨模型 AI 策略（正典語料庫架構、投影分發、headless 安全機制）
- [[user-pref]] — 使用者偏好與決策風格（ASK 優先、Git 紀律、自動化保守策略、除錯對策）
- [[skill-and-eval]] — Skill 評估與管理（方法論整合、工具評估決策）[歷史頁面，topic 已併入其他分類]
- [[igs-uof]] — IGS-UOF 加班單自動化（原 vc-uof-hours 改名擴充、加班單送出五層防線、刷卡時間 onchange 踩坑）

## Lessons

- [[uk-slot-pitfalls]] — UK Slot 踩坑經驗（Layout 退場重排、Promise.all race condition、ghost slot 雙佔位）
- [[bridge-pitfalls]] — Telegram-Kiro-Bridge 踩坑經驗（dotenv 繼承、merge 整檔取代、unhandledRejection、draft TTL、grammY Proxy）

## Tasks

- [[skill-candidates]] — 未成熟 Skill 候選追蹤（pattern、count、觀察點）

## Queries

- [[fable]] — Claude Fable 5 修正 Karpathy P0 接線 Bug（7 個問題 + 教訓 + commit）
- [[modelcontextprotocol-typescript-sdk-mcp-typescript-sdk-v-f2c3525b]] — MCP TypeScript SDK v2 beta（套件拆分 server/client、任意 schema 庫、stateless core）
- [[askintel-time-split]] — Intel 排程分割策略（輕量 daily + 重量 podcast 隔天）
- [[trio-model-architecture]] — 三模型協作架構評析（借鏡點、疑點、與 bridge 差異）
- [[embedding-router]] — 為何 doctor 報 Embedding router 未就緒（根因、影響面、解耦修復）
- [[modelcontextprotocol-typescript-sdk-mcp-typescript-sdk-v-a1aded4e]] — MCP TypeScript SDK v2 正式進入 beta（2026-07-28 規範、套件拆分、任意 schema 庫、stateless core）
- [[specialist]] — 什麼情況下會自動使用 specialist（SPECIALIST_PROXY vs PARALLEL_DELEGATE 觸發條件、bridge-dev specialist 不採納理由）

---

Total pages: 30
Last updated: 2026-07-21（wikilint：user-pref 補 3 條缺漏 fact + 矛盾註記，sources +3；bridge-research 超過 200 行待拆分）
