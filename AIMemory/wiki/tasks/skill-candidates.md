# Skill Candidates（未成熟，待觀察）

追蹤頻率偵測中尚未達門檻的候選 pattern。當 count ≥5 且 score ≥0.5 時考慮升格為正式 skill。

## 候選清單

- [ ] **research-to-html-report** | count=5 | score=0.80 | 已被 Context Budget Discipline steering 覆蓋核心技巧，暫不新建
  - 代表 session: 2026-06-26 Hermes 研究、2026-06-27 Loop Engineering、2026-06-27 Claude Code Tools
  - 觀察點：若未來出現 steering 未覆蓋的新陷阱（如 HTML tab 切換 bug、特定模板結構），再升格
  - 現有覆蓋：preamble `[Context budget discipline]` 段（先結論再寫、≤2 web_fetch、delegate）

- [ ] **skill-quality-self-check** | count=1 | score=0.12 | 太低，繼續觀察
  - 代表 session: 2026-06-27 /skillsearch 自檢（找到 5 個問題並修正）
  - 觀察點：如果對更多 skill/command 做自檢且每次都有固定 checklist，可升格

- [ ] **dream-report-action** | count=1 | score=0.08 | 太低
  - 代表 session: 2026-06-26 dream 建議處理（orphan清理 + backup + dream.json）
  - 觀察點：若 dream 報告格式穩定且處理流程可模板化

- [ ] **external-repo-absorption-methodology** | count=3 | score=0.48 | 留底觀察
  - 代表 session: 2026-06-30 ai_multi_agent 研究→吸收 3 個 P0 改進、2026-07-01 AI-DLC Power 研究→借鏡 4 點、2026-07-02 侯智薰 7 層架構研究→觸發 P1 user-profile 獨立化
  - 觀察點：若出現第 4~5 次「clone/browse 外部 repo → 比較 → 決定吸收哪些」的完整循環，且每次有固定步驟（README 掃描 → 架構比較 → 吸收決策表 → 實作），則升格
  - 與 research-to-html-report 區別：該候選是「研究過程中產 HTML 報告」的輸出格式；本候選是「外部 repo 吸收方法論」的輸入流程

- [ ] **agent-cli-config-hook-portability** | count=3 | score=0.48 | 留底觀察
  - Pattern：各 agent CLI 的設定檔與 hook 體系互不通用（Kiro 讀 AGENTS.md+steering、Codex 讀 AGENTS.md、Claude 讀 CLAUDE.md；hook 體系 Claude settings.json 可 exit 2 阻擋 / Kiro 自有格式 / Codex 無 blocking hook），切換 ACP adapter 時規範與閘門會靜默消失
  - 代表 session: 2026-07-06T07-01（CLAUDE.md 讀取查證 + hook 三軸比較 + impact-gate 部署）、2026-07-06T07-26（ACP 確認延續）、更早 bridge-steering-integration 同構 gap
  - 觀察點：若第 4~5 次出現「換 CLI 後規範漏接」實際踩坑，或要做跨 CLI 投影（sync.ps1 層），可升格；屆時評估是 append 到 ms-portable-skill-authoring（跨 CLI 可攜性同域）還是獨立 skill
  - 現有覆蓋：facts f_c5dfde / f_130b5d / f_611812、memory bridge-steering-integration.md（部分）

---
Last updated: 2026-07-06
