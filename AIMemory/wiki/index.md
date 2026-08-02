# Wiki Index

> Source of truth: `facts-509424983.md`（master log）
> Wiki 是 derived 綜合層，facts 有衝突時以 facts 為準。

## Pages

- [[uk-slot]] — UK 市場老虎機專案群（1 模板 + 7 遊戲 + 1 demo、codegen 整合、Clash of Olympus、spec-to-impl 教訓、回灌工作流、錯誤分類法）
- [[uk-slot-template]] — UK Slot 模板專案（三種 FillStrategy、起新專案慣例、回灌工作流、命名規範）
- [[uk-slot-codegen]] — UK Slot Codegen 工具整合（定位 M0a~M1 加速器、anchor merge 限制、驗證結果、回饋修正）
- [[uk-slot-pirates-queen]] — UK Slot 海盜女王專案（6×5 盤面、懸賞令、RTCtrl 凍幀報獎進化版、PascalCase 搜尋陷阱）
- [[uk-917]] — uk_917 3 Leprechaun's Pots（遊戲輪廓、M0a 進度、proto stub、規格確認事項）
- [[uk-slot-clash-olympus]] — Clash of Olympus 諸神之戰（6×4 4096 Ways、VS Feature 🔴、spec-to-impl 完成、待確認 8 項）
- [[uk-slot-eye-strike]] — Eye Strike 系列（第一代 uk_658 + 續作 uk_872、7 個專案特有機制、SpineKit 規範）
- [[bridge-project]] — Telegram-Kiro-Bridge 專案（架構、AIMemory、Rich Messages、Reply Context、Smoke 隔離、Specialist Dashboard、Status Server 加固、背景通知 flakiness 診斷判準、Fable5 對抗覆核）
- [[bridge-acp]] — Bridge ACP 與 Model 配置（adapter 切換差異、/agent 熱切換、model pin、ACP adapter 能力偵測陷阱、AcpBackendDef 語意差異、異源覆核紀律常態化）
- [[bridge-session]] — Bridge Session 生命週期（archive 蒸餾層、ACP resume、/session 多 session、transcript 路徑）
- [[bridge-streaming]] — Bridge Streaming 與訊息渲染（Draft API 三階段 lifecycle、4096 截斷、rate limit、Rich Messages）
- [[bridge-memory]] — Bridge 記憶與維運系統（AIMemory 結構、/dream 14 步維運、factlint 三層防禦、topic 分類、wiki 知識庫、embedding router、備份）
- [[bridge-dream]] — Bridge Dream 例行維運框架（dream.json models 表 per-backend 設計、claude-mem-curate 接入、turn 誤報根因、confabulation 教訓）
- [[bridge-specialist]] — Bridge Specialist 分身系統（配置、token 執行權限層、PARALLEL_DELEGATE cross-check、Dashboard 監控）
- [[bridge-research]] — Bridge 改善研究與 Roadmap（外部框架借鏡、fable-advisor context packaging、claude-plugins-official Permission Relay、PostTool Hooks A→D、Karpathy P0、Rich Messages Draft、spine-animation-ai 自包含 Skill 打包機制）
- [[bridge-upstream-sync]] — Bridge Upstream Fork 同步與合併衝突處理（remote 配置、merge 策略、三種衝突處理原則、同步歷程、push 前 Fable5 覆核；2026-07-21 從 bridge-project/bridge-acp 拆出）
- [[bridge-roadmap]] — Bridge 開發 Roadmap（Pending / In Progress 追蹤，2026-07-28 建立）
- [[bridge-smoke-gate]] — Bridge 測試閘門與建置（tsc/smoke tier/pre-push 三層、dist≠跑著的碼、環境隔離假失敗、計數同步儀式、probe-* 命名隔離、CI 決策；2026-08-01 從 bridge-project 拆出）
- [[dev-tools]] — 開發工具與環境設定（Python/Playwright/TypeScript、機器路徑、工作流程）
- [[agent-system-architecture]] — Agent 系統五層架構（公司比喻：Agent/MCP/Memory/Workflow/Agent SDK 的角色與關係）
- [[spine-viewer]] — Spine Viewer 插件（Cocos Creator 編輯器擴充，批次掃描 DrawCall/Triangle 效能報告）
- [[ai-strategy]] — 跨模型 AI 策略（正典語料庫架構、投影分發、headless 安全機制）
- [[user-pref]] — 使用者偏好與決策風格（ASK 優先、Git 紀律、自動化保守策略、除錯對策）
- [[skill-and-eval]] — Skill 評估與管理（方法論整合、工具評估決策）[歷史頁面，topic 已併入其他分類]
- [[igs-uof]] — IGS-UOF 加班單自動化（原 vc-uof-hours 改名擴充、加班單送出五層防線、刷卡時間 onchange 踩坑）
- [[verification-diagnosis]] — 驗證與診斷方法論（綠燈假象五型與突變測試、診斷實驗三原則、證據的 recovery 邊界、純觀測欄位、await 縫開 race、同源自審天花板；2026-08-01 從 misc 拆出）

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
- [[agent-claude-opus46]] — 懸案：`/agent claude` 切回後 model 仍是 Opus 4.6 而非 pin 的 Fable 5（settings watcher 覆蓋 set_config_option，未解決）

---

Total pages: 37
Last updated: 2026-08-02（wikisync：更新 [[bridge-acp]] 追加 ACP adapter 能力偵測陷阱、AcpBackendDef 語意差異、claude-sonnet-5 合法性驗證、異源覆核紀律擴充；更新 [[bridge-dream]] 追加 per-backend model 設計、confabulation 教訓定案；新增 [[uk-slot-pirates-queen]] 海盜女王專案頁）
