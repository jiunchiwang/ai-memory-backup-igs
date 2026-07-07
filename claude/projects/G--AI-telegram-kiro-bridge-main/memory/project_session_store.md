---
name: session-store-ui-state
description: SessionStore + /session 多 session 管理已完成，手動 e2e 全過（BC-2/3/5/8），無待辦
type: project
---

SessionStore + /session UI（借鏡 ai_multi_agent，2026-07-07）——**已完成，e2e 通過**。

**Why:** 7/7 差距報告 ROI 第一名——SessionStore + /session inline keyboard 是「最大且最可抄的 gap」。

**How to apply:**
- Commits：`8c65748`（smoke dotenv 隔離修復）→ `d500e48`（store v2 + plan）→ `db557cd`（SessionManager park/switch/new）→ `452ae60`（/session UI）。計畫檔 `docs/superpowers/plans/2026-07-07-session-store-ui.md`（含對抗 review R-1~R-7 軌跡 + 實測記錄表）。
- 核心設計：switch = park（不清 record 不 archive、單獨存 transcript）→ setActive → create()（resolveResumeCandidate 自然命中）；clearResumable 語意變窄只清 active；BC-8 跨 backend 切換連動 pin。
- **手動 e2e 結果（2026-07-07 生產機，全過）**：BC-3 雙 session 暗號互切 ✅（context 不互漏）、BC-5 /reset 只清 active ✅、BC-2 v1→v2 registry migration ✅、BC-8 claude↔kiro 跨 backend record 互切 pin 自動連動 ✅。
