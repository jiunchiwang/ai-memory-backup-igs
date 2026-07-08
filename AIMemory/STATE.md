# Loop State — telegram-kiro-bridge
Last run: 2026-07-07T20:37:02.639Z

## High Priority (action needed)
- ~~skill-usage.json 測試汙染~~ ✅ 已處理（2026-07-08）：根因 = check-usage-store.mjs / check-ab6-integration.mjs 靜態 import dist 導致 MEMORY_DIR 解析到生產路徑（usageFilePath 無視 skillDir 參數）；兩支 script 改為「先設 temp MEMORY_DIR 再動態 import」，14 fixture 已刪、28 skill de-orphan（僅 uk-conventions 維持 orphan，實體來源仍待查），備份 skill-usage.bak.20260708.json
- ~~factlint 27 條刪除候選~~ ✅ 已套用（2026-07-08）：實刪 7 條、19 條被 forgetCommit 的 wiki-reference 保護擋下（wiki sources 引用 fact ID 即不可刪，by design）、1 條重複本就不在 master；master 153→146，shards 重建 + SQLite 同步完成，audit 在 forget-log.md。政策衝突已裁決（2026-07-08）：使用者選（a）接受 wiki 保護——facts 是 wiki 的 provenance；FACTLINT_PROMPT 冗餘規則 3.d 已加排除條款（memory.ts，dist 已 build，下次 bridge 重啟生效）
- ~~hit-log fact 命中從未落盤~~ ✅ 已修（2026-07-08）：根因 = index.ts 主 turn 的 inline enrichment（非 enrichment.ts 路徑）漏了 logHit——wiki/fact 注入正常但從不落盤，只有 skill block 有 log；已補 `logHit("wiki")` + `logHit("fact")` 兩處（index.ts:1167,1183），dist 已 build，**下次 bridge 重啟生效**；注意 hit-log 在此之前的期間 fact/wiki 全是假性 zero-hit，factlint 衰減判斷需以修復日為起算點
- ~~2 條 fact 矛盾~~ ✅ 已處理（2026-07-08）：① f_392c22 vs f_7bf9a8 **實非矛盾**——.env:26 實值 `ACP_MODEL=claude-fable-5`（無 [1m]），[1m] 是 session 層 runtime 設定，兩層並存；已改寫 f_7bf9a8 消歧義（factlint 原建議「以 [1m] 為準合併」會寫錯 .env 值，未採納）。② f_11b405 已改寫：標記借鏡排序過時（指向 f_719003），保留報告路徑 + 中央生態對接點殘值。兩條皆為 bridge-acp wiki sources，改寫保 ID 不刪

## Watch List (monitor)
- 升格候選 external-repo-absorption-methodology 已達 count=4 / score=0.64，第 5 次完整循環出現即升格為 ms- skill
- 9 個 ms-* 防護 skill + vc-kiro-delegate 建議 pin=true（SKILL_USED 上報率低造成計量盲區，vc-kiro-delegate 07-07 實用兩次 count 仍 0）
- Underused 待使用者裁決：內訓 4 件套（dual-skill-review-loop 等）+ huashu-slides + skill-creator（後者建議併入 writing-skills）
- uk-conventions 在 store 且 harness 可用，但不在 .kiro/.claude 兩個 SKILL_DIR，實體來源待查
- MCP SDK query 頁錯置 concepts/，下次 wikisync 搬 queries/ 並確認 frontmatter type
- uk_slot_template 4 個本地 commit 未 push（org 共用 repo，push 前需使用者確認）
- 新 topic shard（uk-917 / bridge-session）待 bridge 下次 re-shard 生成實體檔
- skill-candidates 新增觀察：kiro-delegate-three-stage-review（count=2）、session-context-passphrase-e2e（count=6 檔）

## Noise (ignored this run)
- sharedsync / backup / specialistreview 正常完成無輸出；artifactcleanup 刪 0 剩 1
- dailylog 24 檔濃縮寫入完成；sessionreflect 無 transcript 跳過
- memorytoskill：0 新建 0 更新（門檻嚴篩），28 檔搬 oldSessions，2 條 rationale facts，"score" 頻率候選判定誤判
- topicreview：新增 uk-917 / bridge-session 兩 topic，misc 16→0，備份 topics.bak.20260708041134.json
- wikisync 2 新頁 + 3 更新 + index 修復；wikilint 18/18 綠（dev-tools stale 當場修）；docupdate 5 處落地
