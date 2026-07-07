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

- [ ] **dream-report-action** | count=2 | score=0.16 | 太低，繼續觀察
  - 代表 session: 2026-06-26 dream 建議處理（orphan清理 + backup + dream.json）、2026-07-06T22-30 處理建議（skill-usage store 合併 + 幽靈 skill 補實體 + STATE.md 入口 A+D）
  - 觀察點：若 dream 報告格式穩定且處理流程可模板化

- [ ] **external-repo-absorption-methodology** | count=4 | score=0.64 | 接近升格門檻（count ≥5 即升格）
  - 代表 session: 2026-06-30 ai_multi_agent 研究→吸收 3 個 P0 改進、2026-07-01 AI-DLC Power 研究→借鏡 4 點、2026-07-02 侯智薰 7 層架構研究→觸發 P1 user-profile 獨立化、2026-07-07T11-48 ai_multi_agent 增量差距分析→session resume 移植（方案 ABC 評估→計畫→委派實作）
  - 觀察點：已出現第 4 次完整循環且步驟固定（既有報告過時比對 → 增量分析 → 借鏡排序表 → 逐項風險評估 → 移植方案 ABC → 實作）；第 5 次出現時直接升格為 ms- skill
  - 與 research-to-html-report 區別：該候選是「研究過程中產 HTML 報告」的輸出格式；本候選是「外部 repo 吸收方法論」的輸入流程

- [ ] **agent-cli-config-hook-portability** | count=3 | score=0.48 | 留底觀察
  - Pattern：各 agent CLI 的設定檔與 hook 體系互不通用（Kiro 讀 AGENTS.md+steering、Codex 讀 AGENTS.md、Claude 讀 CLAUDE.md；hook 體系 Claude settings.json 可 exit 2 阻擋 / Kiro 自有格式 / Codex 無 blocking hook），切換 ACP adapter 時規範與閘門會靜默消失
  - 代表 session: 2026-07-06T07-01（CLAUDE.md 讀取查證 + hook 三軸比較 + impact-gate 部署）、2026-07-06T07-26（ACP 確認延續）、更早 bridge-steering-integration 同構 gap
  - 觀察點：若第 4~5 次出現「換 CLI 後規範漏接」實際踩坑，或要做跨 CLI 投影（sync.ps1 層），可升格；屆時評估是 append 到 ms-portable-skill-authoring（跨 CLI 可攜性同域）還是獨立 skill
  - 現有覆蓋：facts f_c5dfde / f_130b5d / f_611812、memory bridge-steering-integration.md（部分）

- [ ] **session-context-passphrase-e2e** | count=6 檔（3 個偵測 session） | score=0.15 | 太低，繼續觀察
  - Pattern：用 context 暗號（如「暗號是 8964」）驗證多 session 隔離、backend 切換、session/load resume 後的 context 保留——每個 session 設一個暗號，切換/resume 後回問
  - 代表 session: 2026-07-07T15-03~15-27 系列（BC-2/3/5/8 e2e：靛藍海豚-1707 / 8964 / 4396 跨 session 互切不互漏）
  - 觀察點：目前只在 bridge session-store 驗證用過一輪；若未來測其他 agent 系統的 session 功能再次採用，且沉澱出固定測試腳本（暗號命名、切換順序、驗證清單），可升格

- [ ] **kiro-delegate-three-stage-review** | count=2 | score=0.30 | 留底觀察
  - Pattern：Kiro 委派實作後的三段 review — ① Kiro `--resume` self-review ② 獨立新 session Kiro 冷讀 git diff ③ 主 agent heavy review（親跑 tsc+smoke+BC 對照）；兩次實戰各抓到 1 個 self-review 漏掉的真 bug（shutdown registry 誤清、rememberFacts 無 enforcement）
  - 代表 session: 2026-07-07T11-48（session resume `b6e028f`）、2026-07-07T16-09（token-policy `028a5ea`）
  - 觀察點：第 3 次委派仍走同流程且再抓到 bug 就固化；屆時 **append 到 vc-kiro-delegate**（同域：委派品質保證），不新建

## 誤判紀錄（防重複偵測）

- ~~"score" pattern（4 sessions）~~ — 2026-07-08 判定誤判：來源是 bridge skill-routing 注入 header 的 `(score 0.65)` metadata，非使用者行為模式

---
Last updated: 2026-07-08
