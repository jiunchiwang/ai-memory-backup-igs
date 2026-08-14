# Loop State — telegram-kiro-bridge
Last run: 2026-08-13T20:44:37.730Z

## High Priority (action needed)
- ~~topicreview 連續 3 輪失敗（written=false）：apply_topics 的 expectedToken 機制打不通~~ → **2026-08-14 根因已定案（原「輸出截斷丟失 token」推測已被實測反證）**：`MEMORY_EVENT_TAXONOMY_ENABLED`（P2）預設 off 且 `.env` 未設 ⇒ `applyTopics` 走 legacy 分支比對 `topics-<hash>-<n>`，但 `renderTopicReviewSnapshot`（facts-store.ts:1510）與 `TOPIC_REVIEW_PROMPT` 第 3 步（commands/memory.ts:229）無條件要求帶 P2-only 的 `ms1_` snapshot token ⇒ 必拒；詳見 wiki `concepts/bridge-memory.md` 與 f_5c1956。⚠️ **同日跨 vendor 覆核推翻了我第一版的一段因果**：我原本寫「acknowledge 排在 throw 之後 ⇒ trigger 每輪重燒」，實查 `memory-taxonomy-maintenance.ts:433`（P2 off 直接 return null、不寫 state）與 `:359-370`（P2 off 回寫死的 shouldReview:true）⇒ **重燒與 apply 成敗無關**，apply 就算成功下輪照樣觸發。該錯誤機制當時已同時寫進 fact／wiki／docs／兩處碼註解，全部已更正。**使用者 2026-08-14 選 A（改 guidance 成 phase-aware），已實作**：`renderExpectedTokenGuidance()` 依 flag 產生指示（P2 off 明講「省略」、snapshot id 降級為 provenance）；`/topicreview` prompt、`apply_topics` tool schema、`docs/memory-system.md`、`README.md` 全部改成指回那一行，不再各自複述規則；legacy 拒絕訊息不再給「re-run propose_topics」這條死路。回歸斷言 `check-topic-review.mjs` 第 6 段釘**預設 flag 狀態**並含 P2 on 對照，變異集 `node scripts/mutate-gate.mjs topic-review-guidance` 實跑 4/4 killed。**跨 vendor 覆核已完成 2 輪並收斂**（kiro-cli glm-5，pin 已驗自報「智譜」）：round 1 出 5 條（採納 1/3/5、駁回 2/4），round 2 針對駁回覆核回「已收斂、0 finding」且兩條駁回經獨立追碼確認。我自己重跑枚舉另抓到覆核者漏掉的第二呼叫者 `memory-baseline.ts:408`（它回音了我「唯一呼叫者」的錯誤），查證後無行為影響、已寫進註解。最終驗證：build 0 錯、fast tier 155/155、變異集 4/4 killed。**已 commit（892f68f，未 push）**。⚠️ **待辦：跑一次 `/restart`** ——`TOPIC_REVIEW_PROMPT` 在 bridge 主行程啟動時載入，不重啟的話舊 prompt（要求帶 snapshot token）會與新 render（叫它省略）給出矛盾指示。⚠️ **兩層生效時機不同**：render／applyTopics／錯誤訊息在 memory MCP child，每個 session 重 spawn ∴ 新 dist 自動生效；但 `TOPIC_REVIEW_PROMPT` 字串由 bridge 主行程啟動時載入 ⇒ **正在跑的 bridge restart 前仍是舊 prompt**（會叫 agent 帶 token）＋新 render（叫它省略）＝互相矛盾的指示，最壞情況是失敗一次後被新的拒絕訊息救回，不是乾淨通過。∴ commit 後補一次 `/restart` 才算完全生效。
- ~~skill-usage.json 的 `brainstorming` entry 是孤兒假陽性~~ → **2026-08-14 已處理**：已補 notes（標 false positive + 實際 plugin cache 路徑 + `src/usageStore.ts:177-182` 只組六條路徑的證據），下輪 skill lint 不再重報

## Watch List (monitor)
- 全 wiki provenance 掃描發現系統性幻影 source ID（50 blocking，集中在 bridge-dream/bridge-research/bridge-streaming/uk-slot/uk-slot-pirates-queen/user-pref/igs-uof/skill-and-eval/dev-tools 等頁），需獨立一輪處理，非本次 factlint 範圍
- bridge-model-strategy 的 f_392c22／f_f6406d 兩則舊 model pin snapshot fact 已知過時但未 supersede（wiki 層已修正，fact 層待處理）
- bridge-infra shard 內 4 條近乎重複的 tsx/dist fact（f_484853/f_210d6f/f_a692b7/f_b1e2ca）待整併
- Underused skill 候選 8 個（writing-skills/dual-skill-review-loop/huashu-slides/self-eval-prompt-pattern/uk-slot-fake-reel-manager/uk-slot-multilang-sync/sync-fork-from-upstream/uk-slot-logo-localization）——僅觀察，不作退場依據
- 3 個 skill「常相關但 agent 不自報」（ms-cross-model-adversarial-review/ms-blackbox-probe-experiment-design/git-commit）——token 紀律問題
- wikilint 本輪僅深度檢查 9/49 頁，剩餘 ~40 頁 staleness 未逐一比對
- writing-skills 與 skill-creator 觸發情境重疊，待下次同時觸發時判斷是否需分工

## Noise (ignored this run)
- /sharedsync、/dailylog、/sessionreflect、/docupdate、/specialistreview、/artifactcleanup、/backup 皆正常完成
- /specialistreflect 處理 27 條 lesson，0 facts/candidates
- /memorytoskill 更新 2 個既有 skill（append），無新建
- /wikisync 5 頁更新完成，provenance 皆 blocking=0
- /factlint 完成 1 條 supersede + 2 條 forget，皆已驗證
- /wikilint 修正 2 頁 stale 內容，orphan/broken link 皆 0
