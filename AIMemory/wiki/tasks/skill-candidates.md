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

- [ ] **dream-report-action** | count=4 | score=0.28 | 仍低於 0.3，繼續觀察
  - 代表 session: 2026-06-26 dream 建議處理（orphan清理 + backup + dream.json）、2026-07-06T22-30 處理建議（skill-usage store 合併 + 幽靈 skill 補實體 + STATE.md 入口 A+D）、2026-07-17T20-40 處理建議（factlint/wikilint/skilllint/docupdate 靜默失敗診斷：_lastTurnFailed 旗標 + sharedsync 吞錯誤修復）、2026-07-30T22-22 處理建議（skill-usage 加 deprecated + factlint wiki-reference 保護 5 條逐條審核）
  - 觀察點：固定骨架已穩定 4 次（讀 STATE.md High Priority → 逐項因果鏈分析 → 處理 → 更新/清空 STATE.md 項目），但每次消耗 turn 數都很低（C≈0.35）所以分數上不來。**判定：即使再出現也不新建 skill** —— 流程綁 bridge 的 STATE.md / dream.json，屆時 append 到 `ms-wiki-knowledge-base`（同域：bridge 記憶維運）

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

- [ ] **windows-git-credential-multi-account** | count=3 | score=0.30 | 留底觀察
  - Pattern：git push/fetch 對某帳號的 repo 卡住/逾時（連 `GIT_TERMINAL_PROMPT=0` 也逾時而非快速失敗），但 push 平常能用——根因是 Windows Credential Manager 對 generic `https://github.com` 快取的是「另一個」帳號，與目標 repo 擁有者帳號不符；修法是把 remote URL 改嵌正確帳號（`https://<account>@github.com/...`）配對到另一組已快取憑證，不需重新登入或給 token
  - 代表 session: 2026-07-19T09-10（/sharedsync 建 `jiunchiwang/ai-shared-knowledge` 修復：generic→`igs-jiunchiwang` vs 新 repo→`jiunchiwang`，改嵌帳號後 push/pull 正常）、2026-07-19T13-37（Fable5 commit push 卡住逾時，remote 嵌 `igs-jiunchiwang`，疑同源未確認）、2026-07-20T20-25（bridge repo `igs-jiunchiwang` 帳號 push F-1~F-4 卡在互動式 git-credential-manager 驗證/疑似瀏覽器 OAuth，非互動 session 無法完成，兩次卡住皆手動清掉 hung process，未能在該 session 內解決，需使用者自行在一般終端機跑一次 `git push` 完成登入快取）
  - 觀察點：若第 4~5 次出現且沉澱出固定診斷步驟（`GIT_TERMINAL_PROMPT=0` 快速失敗判別、`git credential` 帳號比對、remote URL 帳號嵌入），可升格；屆時評估 append 到 `ms-windows-shell-exit-code-false-positive`（同域 Windows git 誤報）或獨立。本次 3rd 案例症狀略有分歧（互動式 OAuth 掛起 vs 純帳號快取不符），升格前需先確認是否同一根因或需拆成兩個 pattern
  - 現有覆蓋：fact f_dff56f（兩組帳號憑證快取對應關係）

- [x] **blackbox-probe-experiment-design** | count=3 | score=0.36 | **已升格為 ms-blackbox-probe-experiment-design (2026-08-01)**
  - 正本：`AI-canonical/skills/general/ms-blackbox-probe-experiment-design/SKILL.md`
  - 代表 session: 2026-07-26（背景通知 flakiness）、2026-07-31T13-46（draft 八臂全負）、2026-08-01T15-33（draft 2×2 探針設計：發現「20s 同內容重送」這格沒測過、ttl2 四臂測 append-only 重打閾值）
  - 內容：三條設計原則（陽性對照必須有效、observable 對齊症狀、內容相依時不可固定內容）、探針結構模板、2×2 矩陣覆蓋檢查、`probe-*` vs `check-*` 命名隔離

- [x] **vacuous-test-gate** | count=6 | score=0.58 | **已升格為 ms-vacuous-test-gate (2026-08-01)**
  - 正本：`AI-canonical/skills/general/ms-vacuous-test-gate/SKILL.md`
  - 6 個實例（皆 2026-07-31，跨 6 個 session）：恆真斷言（truncate 後驗上限）、計數閘門硬寫期望值（且加閘門本身改變該數字）、彙總 throw 是死碼、錨點切到下一條 exit 而放過、測試 resolver 被覆蓋靠 1.5s 逾時放生仍全綠、runner 只印 ok 所以通過不證明斷言跑到

- [x] **cross-model-adversarial-review** | count=8 | score=0.87 | **已升格為 ms-cross-model-adversarial-review (2026-08-01)**
  - 正本：`AI-canonical/skills/general/ms-cross-model-adversarial-review/SKILL.md`
  - 代表 session: 2026-07-18（merge 安全）、07-26（protobufjs 論證缺陷，37 tool calls/587s）、07-29（5 孤兒 import + 1 死碼，tsc 全綠抓不到）、07-30（4 條中 3 成立 1 駁回）、07-31 五輪（00-48 一輪 5 條、07-41 三輪 10 條、13-46 一輪 F1 await race）
  - 與既有候選 `kiro-delegate-three-stage-review` 的分界：後者是**委派實作後**的三段 QA（append 到 vc-kiro-delegate），本 skill 是**push 前**的異源對抗覆核紀律，兩者不合併

- [ ] **acp-raw-capability-probe** | count=4 | score=0.40 | 留底觀察
  - Pattern：文件查不到 ACP adapter 實際支援什麼（model/effort 現值、`sessionCapabilities.resume/list/fork`）時，寫一支 `probe-acp-*` 一次性腳本 spawn adapter → `initialize`/`session/new` → 直接讀回傳的 raw JSON-RPC 欄位，而非相信 adapter 的敘述或 CLI flag 成功與否
  - 代表 session: 2026-07-29（`check-acp-model-effort.mjs`，查證 ACP session 實際跑什麼 model）、2026-08-02（`probe-acp-config-options`，走 `session/new` 讀 configOptions）、2026-08-05T11-37（`probe-acp-session-capabilities.mjs`，initialize-only 讀 `agentCapabilities.sessionCapabilities`，確認 claude-agent-acp 支援 resume/list/fork 而 kiro-cli 整塊缺席）、2026-08-06T07-05（連續三次：codex-acp 已登入 authMethods 三方對照探針、`session/set_config_option` 的 `configId` 參數名探測、`@agentclientprotocol/codex-acp` 1.1.7 新舊套件 capability 差異探針——同一 session 內反覆用同一手法，且首次出現「探針本身逾時 timer 未 clear 造成掛住」這類探針工具本身的 bug）
  - 觀察點：與已升格的 `ms-blackbox-probe-experiment-design` 不是同一件事——那支是探針**實驗設計**原則（多臂矩陣、陽性對照），這個候選是**針對 ACP handshake 這一種特定協定**的固定探測手法（initialize-only、不開 session、逐 backend try/catch、探針前綴天生排除進 smoke gate）。若第 5 次出現且沉澱出可重用的探針骨架（共用 spawn/kill/timeout 邏輯，含這次發現的「逾時 timer 要 clearTimeout」教訓），評估獨立成 skill 或 append 到 ms-blackbox-probe-experiment-design 的「ACP 應用範例」小節
  - 現有覆蓋：wiki `verification-diagnosis`（raw JSON-RPC probe 是查證 model 的唯一可靠法）、`bridge-acp`（ACP adapter 能力偵測陷阱）

- [ ] **specialist-blind-advisor-hallucination** | count=2（同一輪內兩支 specialist） | score=0.40 | 留底觀察
  - Pattern：派 specialist 覆核 diff／文件時未先確認它有沒有讀檔工具就直接派工——`readOnlyLens:true` 但 `mcpServers` 只有 `readonly`、或 `mcpServers` 為空且 harness 不帶 `--agent`，兩者都會靜默收窄成零工具（`src/specialist-config-audit.ts:26,28` 已列為不變式），specialist 讀不到檔卻不會說「我讀不到」，反而產出帶行號、帶檔名的逐字引用；其中一支甚至捏造了不存在的檔名與變數名。可讀檔的 specialist（`readOnlyLens` 搭配非空 MCP，或 harness 帶 `--agent`）同一份任務跑起來則正常引用真實檔案內容
  - 代表 session：2026-08-11（本輪，`moa-ref-kiro`/`moa-ref-adversary` 兩支盲審 commit `9897f46` 皆產出幻覺 diff，改派 `bridge-dev`/`verifier` 才驗證通過；已存為 fact f_667928、f_14cb23）
  - 觀察點：目前只在 telegram-kiro-bridge 一輪內發生，且是這個 repo 特有的 specialist 設定形狀（`specialist-domains.json` 的 `readOnlyLens`/`mcpServers`/harness 組合）。若再出現 2–3 次（尤其換一個 agent 系統／換一種「盲審」設計仍踩到同一種「沒有讀檔能力卻不自報」失效），可考慮 append 到 `ms-cross-model-adversarial-review`（新增一節「派工前先確認覆核者讀得到檔」，與既有〈覆核者選型〉的 domain/tier 兩軸並列成第三軸：能力）
  - 現有覆蓋：fact f_667928（bridge-specialist topic）、f_14cb23（adversarial-review topic）——兩則已含具體檔案:行號與修法，暫不需要更多

## 誤判紀錄（防重複偵測）

- ~~"score" pattern（4 sessions）~~ — 2026-07-08 判定誤判：來源是 bridge skill-routing 注入 header 的 `(score 0.65)` metadata，非使用者行為模式
- ~~"slot" pattern（3 sessions）~~ — 2026-07-10 判定誤判：頻率偵測抓到的 3 次「slot」出現是查詢 codegen 修正狀態的問句（「請問我本機的uk-slot-codegen skill是否都有把之前測試的問題修正了?」），非可重用技術模式
- ~~"fable relevance" / "背景 bug" / "bug 清單與修正" / "教訓 commit" / "commit 紀錄" / "紀錄 相關" / "fable" / "relevance" / "bug" 等 10 個 pattern（各 3 sessions）~~ — 2026-07-11 判定誤判：全部來自 bridge wiki retrieval 注入的 header `## [[fable]] (relevance 0.70) - 背景 - Bug 清單與修正 - 教訓 - Commit 紀錄 - 相關`，是 metadata 而非使用者行為模式（與 "score" 先例同類）

- ~~"commit" pattern（3 sessions）~~ — 2026-07-16 判定誤判：使用者正常的 git commit 互動流程（「幫 commit」「有 commit 嗎」），不是可重用技術模式，已有 user-pref fact 覆蓋偏好（commit 前先確認）

- ~~"users jiunchiwang" / "users" / "jiunchiwang" pattern（4 sessions）~~ — 2026-08-13 判定誤判：全部命中同一個絕對路徑字串 `C:\Users\jiunchiwang\Downloads\Telegram Desktop\wheel-click-prototype.html`（使用者傳同一份 HTML 檔案討論多輪），是路徑字面值被重複引用，不是技術模式

---
Last updated: 2026-08-13
