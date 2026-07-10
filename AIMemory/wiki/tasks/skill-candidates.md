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

- [x] **external-repo-absorption-methodology** | count=5 | score=0.80 | **已升格為 ms-external-repo-absorption (2026-07-10)**
  - 正本：`AI-canonical/skills/general/ms-external-repo-absorption/SKILL.md`
  - 代表 session: ai_multi_agent 2 次、AI-DLC Power、侯智薰 7 層、同事 codegen skill

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
- ~~"slot" pattern（3 sessions）~~ — 2026-07-10 判定誤判：頻率偵測抓到的 3 次「slot」出現是查詢 codegen 修正狀態的問句（「請問我本機的uk-slot-codegen skill是否都有把之前測試的問題修正了?」），非可重用技術模式
- ~~"fable relevance" / "背景 bug" / "bug 清單與修正" / "教訓 commit" / "commit 紀錄" / "紀錄 相關" / "fable" / "relevance" / "bug" 等 10 個 pattern（各 3 sessions）~~ — 2026-07-11 判定誤判：全部來自 bridge wiki retrieval 注入的 header `## [[fable]] (relevance 0.70) - 背景 - Bug 清單與修正 - 教訓 - Commit 紀錄 - 相關`，是 metadata 而非使用者行為模式（與 "score" 先例同類）

---
Last updated: 2026-07-11
