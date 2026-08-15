# Loop State — telegram-kiro-bridge
Last run: 2026-08-14T20:36:46.683Z

> 📌 **2026-08-15 下午另一輪（處理 dream 剩餘待辦）**：三個 commit 已 push
> （`92697d0..1d8a1d0`：`c07b3b4` POLICIES 假宣稱三段更正 · `11a9489` canary topic 改必填 ·
> `1d8a1d0` 覆核抓到的文件矛盾）。pre-push 157/157 passed in 190.4s、戳記 tree `329f92a`。
> 覆核：codex 兩輪各抓到成立的 finding（第一輪 4 條含「更正本身沒有閘門保護」、
> 第二輪 1 條「範例違反自己剛寫的規則」）；glm-5 弱 prompt 兩次純複述無效，強 prompt
> 這輪有查證痕跡但關鍵那軸讀的是已修狀態 ∴ 不計為獨立確認。
> ⚠️ **最後那個 commit（`1d8a1d0`）本身未經第三方覆核** —— 它是覆核的產物，
> 而本 repo 已有三次「修法自己引入新缺陷」的紀錄，下輪若碰這一帶請先看它。

## High Priority (action needed)
- ✅ **2026-08-15 push 前覆核四輪完成，六個 commit 已 push**（`0db8132..92697d0`；
  pre-push gate 157/157 passed in 236.4s、綠燈戳記 tree cc6acc7）。
  commits：6fa3f4b / fb3e5d7 / e8276e7 / 14e8387 / 436b4a1 / 92697d0。收斂判定**由我自己的枚舉下**，不是採信覆核者的「已收斂」：
  第四輪 0 行為 finding，且端到端重跑 canary 得到與修法前**逐位元相同**的品質數字
  （microP 0.061/0.126、microR 0.444/1.000、MRR 0.273/0.933、cov 1.0），兩個 gate 皆過。

  | 輪 | 覆核者 | vendor | findings | 留痕 |
  |---|---|---|---|---|
  | 1 | glm-5 | zhipu | 0 | ⛔ **無獨立檢查痕跡**（純複述；抽查兩個引用都指錯） |
  | 2 | gpt-5.6-sol | openai | 5（2 high） | 全部成立、無駁回 |
  | 3 | gpt-5.6-sol | openai | 3（1 high） | **全部是上一輪修法自己引入的** |
  | 4 | glm-5 | zhipu | 0 | ⚠️ 有展示成分，**但含一條經查為錯的支撐主張** |

  ⚠️ 第四輪不記為「已取得獨立確認」：它宣稱「exit code 2 在這個 repo 的慣例裡是輸入錯誤」，
  而 repo 唯一文件化 exit code 的地方（`docs/memory-rollout-contract.md:83`）寫的是
  `2` = unavailable、`3` = 輸入/runtime 錯誤。結論（非缺陷）我同意，但理由是錯的 ∴ 不採信為確認。
  ⚠️ **末輪判斷不受檢**：第三、四輪我都沒有駁回任何 finding ∴ 沒有駁回清單可交叉檢查；
  而「我判斷第四輪已收斂」這個決定，定義上沒有下一輪能看到它。
  ~~四個 commit 在修完前不可 push~~（已修完，findings 詳如下）：
  1. **high — 契約文件與碼互相矛盾**：`docs/memory-rollout-contract.md:84-86` 逐字寫「只有 `0` 可以授權
     rollout」「超過絕對雜訊下限後仍由 25% 門檻阻擋實質退化」，但 `14e8387` 把 latency 降成 advisory
     ∴ p95 從 100→10000ms 仍然 exit 0。**分岔決策**：改契約（明寫 exit 0 不涵蓋 latency）或還原 gate
     （先做 warmup + 多輪統計）——需裁決。
  2. **high — 畸形 ID 修法只蓋小寫**：`memory-db.ts:959` 的 malformed regex 是大小寫敏感的 `f_`，
     而 `facts-store.ts:730` 的 `auditFactIdIntegrity` 用 `/^\s*-\s*\[f_/i`（帶 `i`）。
     決定性重現：`- [F_ABCDEF] [ts] body` → `isMalformedId=false` → **欄位左移復發**、
     createdAt 吃到 `F_ABCDEF`。稽核抓得到、parser 抓不到 —— 與本 repo 先前的 `cut ⊇ hide 超集`
     同形狀。另 `f_`（無尾碼）兩條通道都不匹配。BC-8/MFL9 只用 `f_r0b1nh` ∴ 蓋不到。
  3. **medium — cohort 比的是聯集不是逐 lane**：`memory-production-canary.mjs:299` 的
     `selectedCohort` 是三個 lane 的 `flatMap` 聯集，且只比 `goldCohorts[0]`。反例：legacy 選 {B}、
     p1 選 {A,B} → 聯集 {A,B} 等於 gold ∴ `goldCohortComparable: true`，但 legacy 實際少一筆。
     P1 改變 topic 分類時可達。（既有碼的缺口，但 `memory-gold-set-build.mjs` 的註解把它寫成「全等」
     ∴ 敘事也要一起修。）
  4. **medium — `fact-dup-scan.mjs:53-54` 讀錯 env 且把個人 ID 寫死**：用 `USER_ID` 而非 repo 標準的
     `MEMORY_USER_ID`，預設值硬寫 `G:/AI/AIMemory` 與 `509424983`。在本機因 bridge 剛好有 export
     `USER_ID` 而「碰巧會動」，換一台機器或另一個 user 會靜默掃錯 shard；且該 repo 與同事共用。
  5. **low — 數值旗標不驗證**：`--jaccard nope` → `NaN`，而 `x < NaN` 恆 false ∴ 兩個門檻都失效、
     只要有一個共同 bigram 就進候選，腳本仍 exit 0；`--jaccard 2 --contain 2` 則全部排除、同樣 exit 0。
  ⚠️ **第一輪（glm-5，zhipu）回「已收斂 0 findings」但記為「無獨立檢查痕跡」**：全篇是「讀 檔:行號 →
  複述碼在做什麼 → 結論一致」，零反例；抽查兩個最不顯眼的引用**都指錯**
  （說 `mutate-gate.mjs:3838-3862` 是 MRC12/13，實際那裡是 MRC1/2/3；說 `fact-dup-scan.mjs:73-88`
  算 jaccard，實際在 122-123）。**不可寫成「已取得獨立確認」。**
- ✅ **2026-08-15 canary gold set 已建立，品質軸首次量到**（`metricsComparable: true`、
  `goldCohortComparable: true`、`gates` 不再是 null）。cohort＝`uk-slot`＋`uk-slot-eye-strike` 共 26 facts，
  15 個 recall query／5 個 consolidation pair（全 `distinct`——該 cohort 沒有真重複）。
  檔案 `${MEMORY_DIR}/canary-gold.json`（**不進 repo**，含逐字記憶；只靠 /backup），
  生成器 `scripts/memory-gold-set-build.mjs`（facts 由腳本重建、標註跨次保留、標註指向死 fact 會硬失敗）。
  **pooling 後的量測（judgedCoverage = 1.0，三條 lane 同分母）**：

  | lane | retrieved | relevant | irrelevant | unjudged | microP | macroP | microR | MRR | cov |
  |---|---|---|---|---|---|---|---|---|---|
  | legacy | 131 | 8 | 123 | 0 | 0.061 | 0.057 | 0.444 | 0.273 | 1.0 |
  | p1 | 131 | 8 | 123 | 0 | 0.061 | 0.057 | 0.444 | 0.273 | 1.0 |
  | p1-p5 | 143 | 18 | 125 | 0 | **0.126** | **0.195** | **1.000** | **0.933** | 1.0 |

  ⇒ `status: passed`、`failureReasons: []`、**p1 與 p5 兩個 gate 全過**。
  ⚠️ **事後補注（見下一條）**：此輪的 PASSED 含 latency 檢查，而該檢查事後被證實**同輸入會翻面**
  ∴ 這個 PASSED 裡「latency 那一項」不具意義，與 cohort 2 第一次那個 FAILED 一樣不可信；
  品質三軸（precision／recall／MRR）是確定性的，不受影響。
  P5 在**每一個軸**都優於 legacy：precision 0.061→0.126、recall 0.444→1.000、MRR 0.273→0.933、
  latency 26.8→15.0ms，injection mean 1668→1778 chars（budget 8000，未逼近）。
  **P1 與 legacy 逐項完全相同 ∴ P1 對召回品質是 no-op**（它動的是分類 sidecar 不是 ranking）。

  ⚠️ 過程中有一次錯誤判讀值得記住：首輪 judgedCoverage 只有 9.2% 時 p5 gate **紅在 precision
  0.667→0.474**，我當時判斷那是被 coverage 差三倍混淆的、不可當成 P5 變差的證據——**pooling 後
  證實這個判斷是對的**（同分母下 p5 的 precision 反而是 legacy 的兩倍）。但當時另一個推論是**錯的**：
  我說「119 筆 unjudged 是 cohort 外的、retrieval 沒有依 topic 侷限」，實測 pool 的唯一 fact 數
  ＝ cohort 26 筆、越界 0、從未被回傳 0 ⇒ **retrieval 嚴格依 topic 侷限**，那 119 筆是 cohort 內
  我沒替該 query 標到的。∴ 補判不需要跨 topic，只需把每條 query 對 26 筆判完（已改 `closedWorld: true`，
  且是逐條複核過 relevant 完整性才敢宣稱，不是為了讓 coverage 好看的捷徑）。

  絕對值 microP 0.061 的意思是 **legacy 每條 query 注入約 9 筆而真正相關的只有 1–2 筆**
  —— 召回稀釋現在量得到了。

- ✅ **第二 cohort（`bridge-draft-diag`，26 facts / 15 queries，closedWorld）已完成獨立重測**，
  並在過程中發現 **p5 gate 的 latency 檢查會在無任何輸入變更下翻面**：

  | lane | retrieved | rel | microP | macroP | microR | MRR | injection |
  |---|---|---|---|---|---|---|---|
  | legacy | 225 | 20 | 0.089 | 0.089 | 0.909 | 0.833 | 4565 |
  | p1 | 225 | 20 | 0.089 | 0.089 | 0.909 | 0.833 | 4565 |
  | p1-p5 | **197** | 21 | **0.107** | **0.112** | **0.955** | **0.967** | **4458** |

  **同 cohort、同 gold set 連跑兩次的對照**：

  | run | legacy p95/mean | p1 p95/mean | p1-p5 p95/mean | p5 gate |
  |---|---|---|---|---|
  | 1 | 27.3/16.6 | 13.1/11.3 | 19.7/12.4 | **FAILED**（latency 13.11→19.75，limit 18.11）|
  | 2 | 29.2/17.3 | 16.1/12.3 | **14.8**/11.5 | **PASSED** |

  品質三軸兩次**逐位元相同** ∴ 確定性；latency 不是。
  ⇒ **可信結論（兩個獨立 cohort 各一次確定性複製）**：① P1 對召回品質是 no-op（兩組皆與 legacy
  逐項相同）；② P5 在 precision／recall／MRR 三軸都優於 legacy，且 cohort 2 是「回傳更少」達成的。
  ⇒ **不可信**：latency 的任何方向。cohort 1 量到 P5 快 44%、cohort 2 第一次量到慢 51%、
  第二次又變快——同輸入的擺動幅度大於它要偵測的效應量（15 條 query 的 p95、三條 lane 循序跑
  有暖快取順序效應、毫秒量級）。**cohort 1 那個「P5 快 44%」同樣作廢。**
  ✅ **已處置（使用者裁決：降級成 observation）** — commit `14e8387`：`checks` 加 `advisory?: boolean`，
  latency 標記 advisory，`passed` 改成 `every(c => c.advisory || c.passed)`。
  **刻意不是把 latency 拿掉** —— 報表照樣有那一行、照樣算 `passed`、照樣顯示超限，只是不計入放行。
  第三個獨立樣本進一步佐證雜訊判斷：驗證輪的 p1 lane 是 34.6ms，前兩輪是 13.1 / 16.1ms（同碼同資料）。
  ⚠️ **這是永久少一道守衛**：P5 若真的變慢，現在沒有東西會擋，只會在報表多一行紅字等人看見。
  恢復成 gate 的路徑是**先讓量測穩下來**（warmup／多輪取中位數），**不是放寬門檻**。
  鎖住降級語意的斷言有兩條（缺任一都會變質）：「advisory 不再拉低 passed」與「latency 照樣量、
  照樣報 false、標著 advisory」；只有前者的話**把 latency 整條刪掉也會過**。
  mutate-gate MRC12／MRC13 兩個變異皆 killed。
- ✅ **已處理 2026-08-15（使用者裁決：移除預設改必填，非換成真 cohort）**：
  `DEFAULT_TOPICS` 那兩個名字**從來不是 production topic 名**，是 smoke fixture 名——
  gate 自己建同名 topic 才會綠 ∴ 舊斷言在 fixture 恆綠、在真實環境卻正是假紅燈的來源。
  不選「換成真 cohort」的理由：真 shard 名逐機器／逐使用者不同，寫死進與同事共用的 repo
  等於換一種形式的同一個缺陷（＝當天稍早 `fact-dup-scan` #4 的形狀）。
  改動 6 檔：`scripts/memory-production-canary.mjs`（`--topic` 必填，缺→exit 3 明確訊息）·
  `src/memory-rollout-canary.ts`（移除 `DEFAULT_MEMORY_CANARY_TOPICS`，`topics` 兩處改必填）·
  `src/memory-rollout.ts` + 重生 `docs/memory-rollout-contract.md`（BC-6 byte 相等）·
  `scripts/check-memory-rollout-canary.mjs`（**6 個 runner 呼叫點**原本都靠預設；舊斷言
  改成負向的「缺 --topic 必須報錯」＋新增「空 topic 集必 throw」）· `scripts/mutate-gate.mjs`
  （新增 MRC15 守「預設被加回來」；MRC5 原本守的對象已不存在 ∴ 改守空集 throw）。
  ⚠️ 過程中踩到一次自己剛寫的教訓：junction 與 invalidPath 兩條安全斷言原本不帶 `--topic`，
  改完會因「缺 --topic」而**同樣 exit 3、同樣綠**，但測到的已不是它宣稱的對象——已顯式補上。
  驗證：tsc 過 · 三支相關 gate 綠 · mutate-gate memory-rollout-canary **15/15 killed**
- ✅ **已處理 2026-08-15：工具三件已 commit 並 push**（`6fa3f4b`，工作區已乾淨）。原文如下保留脈絡：
  `src/memory-db.ts` 不合規 fact ID 不再吃「選配」路徑而讓欄位左移（＋per-process 去重的 `console.warn`）·
  `src/facts-store.ts` 新增 `extractWikiMalformedFactIds()` → `source_malformed_id`(blocking)／
  `history_malformed_id`(warning)，並把 `auditFactIdIntegrity` 的 `invalid_id_format` 併進
  `auditWikiProvenance` full audit（`master_id_malformed`）· `scripts/check-memory-fact-lifecycle.mjs`
  新增 BC-8 七條斷言 · `scripts/mutate-gate.mjs` 新增 MFL9/MFL10/MFL11（**三個變異全 killed 且紅在該紅處**）·
  `AI.md` 補記。⚠️ 第三件刻意**不掛 smoke**：`scripts/smoke-env.mjs:49-50` 強制 `MEMORY_DIR=temp`、
  `MEMORY_USER_ID=1` ∴ 掛上去必是恆綠假閘門。`tsc --noEmit` 過、完整 fast tier PASS。
- **`check-memory-rollout-canary` 歸因未定的紅燈**（見 bridge-smoke-gate 當日 fact）：完整 suite 四輪
  前兩紅後兩綠，控制組（stash 掉當日改動）綠但只跑一輪 ∴ **不可宣稱與改動無關**。
  下次遇到先清 `os.tmpdir()` 的 `memory-production-canary-*` 再重跑，並記錄連續失敗次數。
  📌 2026-08-15 13:2x 依此協定查過：`C:\Users\jiunchiwang\AppData\Local\Temp\` **零殘留** ∴ 此刻沒有
  被污染的起始狀態。**刻意不做投機修法**（曾考慮給 `removeRunnerTemp` 加 retry/backoff，否決——
  歸因未定就改，形狀等同使用者剛否決的「把量測工具調到自己想要的答案」）。本項維持開啟。

## Watch List (monitor)
- ✅ **已處理 2026-08-15：memory canary 兩個結構性 blocker 全清，`structuralPassed: true`（三個 lane 皆
  `provenance.blocking: 0`、`derivedMatchesActive: true`、`extraSqliteFactIds: []`）**。
  兩個 blocker 是**同一個根因**：master log 第 16-20 行的 5 個 fact ID 是手寫 leet 字串
  （`f_r0b1nh` / `f_wr4th9` / `f_f4rw3s` / `f_3y3s2k` / `f_ch4ch4`），含非 hex 字元 ∴ 全 codebase 的
  `f_[0-9a-f]{6}` 一律匹配失敗。`memory-db.ts:935` 的 ID 括號是**選配**的 ∴ 匹配失敗時欄位整個左移一格
  （`createdAt` 吃到 `f_r0b1nh`、`text` 黏著 timestamp），再拿這段錯的 text 重新雜湊出 master 裡不存在的
  ID —— 就是那 5 筆孤兒。附帶後果：`created_at` 非日期字串 ∴ hybridSearch 的時序衰減對它們整個跳過。
  ⛔ **昨天寫的修法「重啟 bridge 讓 startup sync 把 5 筆 -deleted 掉」是錯的**：master 那幾行沒改，
  每次 sync 都會重新推導出同一批孤兒。實際修法＝正規化 master 的 ID 本身
  （→ `f_1284be` / `f_b4c328` / `f_0af12a` / `f_937a50` / `f_4b6004`，即 `f_${sha256(text).slice(0,6)}`）
  ＋同步 shard 與 wiki 引用，再跑 `syncFactsToDb`（實跑 `inserted:5 deleted:5`）。
  ⚠️ 剩餘的 `passed: false` 只有一個原因 `quality-metrics-unavailable-or-incomparable`
  ——**沒有 gold set**，非結構問題（見下一條）。修改前的檔案備份在 `G:\AI\AIMemory\.bak-2026-08-15\`。
- ~~**2026-08-15 memory canary 首跑結果（`status: failed`，但失敗原因是既有債不是新問題）**~~（已解決，保留脈絡）：
  三個 lane（legacy／p1／p1-p5）全部 `structuralPassed: false`，**含全 flag 關閉的 legacy lane**
  ∴ 與 P1/P5 無關。兩個 blocker：
  ① `provenance.blocking: 49`（checkedPages 51）—— 就是本清單既有那條「全 wiki provenance 49 blocking」
  ② `derivedMatchesActive: false` —— `extraSqliteFactIds` 有 5 筆孤兒
     （f_250cf0 / f_2c6123 / f_3afe4d / f_461a70 / f_7f0951，**五筆都不在 master log**）。
     shard 是乾淨的（missing/extra 皆 0）∴ 只有 SQLite index 有殘留。
     **非本日操作造成**：今日 supersede/forget 的 9 個 ID 都不在這 5 筆裡。
     文件記載的修法（`src/memory-db.ts:11`）是刪掉 .db 再 `syncFactsToDb()` 重建（之後要 backfill embedding）。
  ⇒ **在這兩項清掉之前，任何 P-phase rollout 的量測都拿不到 gate**（`gates: {p1: null, p5: null}`）。
  ✅ 安全性已驗證：`stableAfterCopy/stableAfterRun: true`、`protectedFiles: 88`、`cleanup: completed`
     —— 真實 MEMORY_DIR 未被寫入，全在 temp clone 內跑。
- ⚠️ `scripts/memory-production-canary.mjs` 的 `DEFAULT_TOPICS = ["bridge-memory-system","gate-mutation-testing"]`
  **兩個都不是實際 shard 名**（真名 `bridge-memory`；後者是 wiki 頁不是 topic）∴ 不帶 `--topic` 直接跑會選不到 fact
  而落成假紅燈。首跑已改帶 `--topic bridge-memory --topic bridge-project --topic adversarial-review`
- ⚠️ **沒有 gold set**（磁碟無任何 `canary-gold.json`）∴ canary 目前只能驗結構完整性，
  `metrics.status` 恆為 `unavailable`（reason: no production gold set provided），
  **量不到召回品質** —— 而那正是「召回稀釋」要驗的東西
- ✅ **已處理 2026-08-15**：bridge-infra 重複 fact 群。查證後三條沒有一條可當正本——`dist/` 的消費者是
  「MCP server 子行程 ＋ smoke suite」兩類，而 f_a692b7 寫「只有 smoke suite 在用」、f_210d6f 寫
  「只給 MCP server 子行程使用」，兩條「只有」互相矛盾且皆為誤（證據：package.json 的 bin 指
  dist/mcp-memory.js、scripts/setup-mcp.mjs:25-27、scripts/check-*.mjs 幾乎全部 import ../dist/*.js）。
  處置（使用者裁決 sup4）：f_b1e2ca/f_484853/f_a692b7/f_210d6f 四條 supersede 成 **f_e2e14a**；
  四頁 wiki 的 sources→history_sources 已遷移（bridge-infra/bridge-memory/bridge-project/bridge-smoke-gate）；
  bridge-infra.md 與 bridge-smoke-gate.md 的錯誤敘述已改寫 + bump updated。
- ✅ **已處理 2026-08-15**：f_c61829（一整段 `[WS] ...` working-state blob 被寫成永久 fact）已 forget，
  先從 wiki/concepts/bridge-specialist.md 的 sources 移除引用（它不是正當 provenance，故直接刪不入 history）。
  ⚠️ **漏擋路徑尚未查明，不要當成已解決**：`[WS]` 守衛（`isWorkingStateFact`，`^\s*\[WS\]`）於
  commit 7591318（2026-08-10）落地，接在 facts-store.ts:971（supersede）／mcp-memory.ts:139（remember）／
  memory.ts:44、128（appendFact / appendFactsDedup）四處；而該 fact 的時間戳是 2026-08-12 ∴ 確實繞過了。
  已查到的線索：`appendFactShardOnly`（facts-store.ts:145）**沒有** `[WS]` 檢查，但它只寫 shard 不寫 master log，
  而該 fact 在 master log 裡 ∴ **不足以解釋**。未經證實的假說（B 級、勿當事實）：守衛在 08-10 進 src，
  但 remember() 實際跑的是 `dist/mcp-memory.js`，若當時 dist 尚未重建 + session 未重啟則守衛不生效——
  這正好是本輪 f_e2e14a 記的那條規則。無法回溯查證（dist 現在的 mtime 是 2026-08-15 00:38，對 08-12 無鑑別力）。
  **2026-08-15 補充（掃描後）**：`[WS]` 洩漏不是單一事件，master log 共 3 條——f_277b97（2026-08-01，
  守衛之前 ∴ 已解釋）、f_c61829（08-12，已 forget）、**f_2d2996（08-13，仍在，落在 bridge-project shard 第 40 行）**。
  ✅ 決定性探針已跑：對活著的 MCP 呼叫 `remember()` 傳 `[WS] task: …` **被正確拒絕** ∴ 守衛在**現在**是生效的，
  leak 不是當前 bug。剩下未解的只有「08-12／08-13 當時為何沒擋」，stale dist 仍是最合理但未證實的解釋。
  ✅ f_2d2996 已於 2026-08-15 forget（先解 bridge-project.md 的 sources 引用）。⚠️ 它裡面卡著一個**實質發現**
  （POLICIES/development-methodology.md Section 7 說 impact-gate hook 不存在是假宣稱，實際存在且會 exit 2 擋人），
  刪除前已升格成正式 fact 存進 bridge-topic。**教訓：`[WS]` blob 不是純垃圾，forget 前要逐條看有沒有夾帶持久發現。**
- **POLICIES 假宣稱待修**（R-2 保護清單內，要異源覆核）：`POLICIES/development-methodology.md` Section 7 宣稱
  「.claude/hooks/ 不存在 ∴ L1 機械層一直是空的」為誤——`.claude/hooks/impact-gate.mjs` 存在且 2026-08-15
  第一手實測會擋下 Write。`CLAUDE.md` 承重核摘要與 `POLICIES/run-plan-orchestration.md` 有同一句回音，要一起修
- ✅ **已處理 2026-08-15：skill 正本兩件都補完並投影**（AI-canonical `21d7c16`；
  `readlink -f` 確認正本＝`G:/AI/AI-canonical/skills/general/ms-wiki-knowledge-base`，
  `tools/sync.ps1 -Apply` 後在 `~/.claude/skills/` 投影端 grep 到兩段新內容）。原文保留：
  - **skill 正本待同步**：`ms-wiki-knowledge-base` 的 factlint 段落仍寫「fact ID 出現在任何 wiki 頁 frontmatter
  sources 中者不列候選（2026-07-08 裁決：接受保護而非解除引用）」——2026-08-15 使用者已把例外擴大到
  「已解決的一次性狀態」（見同日 bridge-memory fact）。正本在 AI-canonical，改完要跑 `tools/sync.ps1 -Apply` + commit
  ⚠️ **同一支 skill 還要補第二件（2026-08-15 新增）**：`audit_provenance` 現在多了三個 code ——
  `source_malformed_id`(blocking)／`history_malformed_id`(warning)／`master_id_malformed`(blocking)。
  既有 runbook 只教過「blocking＝來源不存在或已失效 → 移除引用」，**對畸形 ID 套用那條會重犯今天才剛更正的錯**：
  **ID 形狀不合規 ≠ 該 fact 是捏造的**。正確處置是「拿內容去 master log 找 → 找得到就把 master 的 ID
  正規化成 `f_${sha256(text).slice(0,6)}` 並同步 shard + wiki 引用 → 跑 `syncFactsToDb`」，
  **不是移除 citation**。只有 master log 與 forget-log 兩處都查無才判捏造、才移除。
  （今日實例：5 個手寫 leet ID 被誤判為捏造而移除，隔天才由 master log 第 16-20 行否證）
- fact 去重掃描工具 `scripts/fact-dup-scan.mjs`（唯讀；✅ 已於 `e8276e7` commit 並 push，
  後續 `436b4a1`/`92697d0` 修掉覆核抓到的 env/身分/數值驗證三類問題）：Jaccard + containment 找近似重複群。
  P4 內建 consolidation 本機是 `enabled: false` ∴ 沒有自動偵測在跑，這支補那個缺口。
  建議參數 `--contain 0.70`（0.62 會讓短 fact 被長 fact 涵蓋而產生大量偽陽性）
- ✅ **已處理 2026-08-15（`54873da`，使用者選 A 案：改成 `npm run build`）**：`start.bat` 第 4 行
  `call npm build` 是 no-op（`npm build` 非有效 npm 指令，實跑得 `Unknown command: "build"`）。
  根因由 git 史確認是 `fee59d1`（05-29）把 upstream 的 `call pnpm build` 機械改名——pnpm 允許
  `pnpm <script>` 簡寫、npm 不允許。代價已量測：每次 supervisor 重啟多約 11s（`tsc -p .` 全量 10.7s）。
  README.md:243 同時修（原句寫 `pnpm build` 且宣稱會編譯，指令名與行為兩處失真），並補上
  「不能寫 `npm build`」的反例說明避免下次改名重蹈覆轍。
  可遷移的形狀：**套件管理器改名是一類靜默失效向量**——`pnpm <script>` / `yarn <script>` 有簡寫、
  npm 沒有，而 batch 的 `call` 不檢查 errorlevel ∴ 唯一徵兆是一行會被洗掉的錯誤訊息。
  它能躺兩個半月是因為 bridge 主行程走 tsx 直讀 `src/`、根本不需要 dist ∴ 功能面零症狀。
- 全 wiki provenance 掃描仍有 49 blocking（bridge-dream/bridge-research/bridge-streaming/igs-uof/skill-and-eval/uk-slot-pirates-queen/uk-slot/user-pref/queries 等），需獨立一輪處理
- ✅ **已處理 2026-08-15：wiki provenance 49 blocking → 0**。根因**不是**「fact 被刪掉留下引用」，
  而是**捏造的 provenance**：49 個 ID 裡 **48 個從來不存在**（master log 含 superseded 列、forget-log.md 都查無），
  只有 f_cb10bc 是真的被刪過。最露骨的是 uk-slot-pirates-queen.md 的 8 個
  （f_a1b2c3 / f_d4e5f6 / f_789abc / f_def012 / f_345678 / f_9abcde / f_f01234 / f_567890 —— 明顯是佔位字串），
  bridge-streaming.md 的 f_b613db / f_bd068e 則疑似把 **git commit hash**（b613dba / bd068e1）當成 fact ID 寫進去。
  處置：10 個頁面移除 49 個假 ID；queries/fable.md 唯一 source 是假的 ∴ 變成 `sources: []` 並加 provenance_note。
  ⚠️ **順手修掉 audit 的盲點**：它只認 `f_[0-9a-f]{6}` ∴ 畸形 ID 完全掃不到——
  uk-slot.md 的 f_r0b1nh / f_wr4th9 / f_f4rw3s / f_3y3s2k / f_ch4ch4 與 bridge-streaming.md 的 f_plan_e
  （共 6 個）過去一直隱形，已一併移除。
  ⛔ **2026-08-15 稍後更正：上一句「含非 hex 字元 ∴ 定義上不可能是真 ID」是錯的推論**，
  已被 master log 第一手否證——那 5 個 `uk-slot.md` 的 ID **是 2026-06-03 就存在的真 fact**
  （master log 第 16-20 行、shard 也有），只是 ID 為手寫字串。只有 `f_plan_e` 是兩處查無、移除正確。
  處置：5 條 ID 已正規化並回填 wiki 引用（見上方 canary 那條）；fact `f_05c854` 已 supersede 成
  `f_e42c5d`。**可遷移判準：ID 形狀不合規 ≠ 該 fact 不存在——形狀只證明工具鏈看不到它，
  要另外拿內容去 master log 找。**
  ~~**這個盲點本身沒修**——audit_provenance 仍然看不到畸形 ID，下次有人寫進去照樣全綠。
  另：`facts-store.ts:741` 已有 `invalid_id_format`（blocking）能抓這類 ID，但**沒有任何 gate 在跑它**~~
  ✅ **兩句都已於 2026-08-15 由 `6fa3f4b` 解決**：新增 `extractWikiMalformedFactIds()` →
  `source_malformed_id`(blocking)／`history_malformed_id`(warning)，並把 `invalid_id_format`
  併進 `auditWikiProvenance` full audit（`master_id_malformed`）；BC-8 七條斷言 + MFL9/10/11
  三個變異全 killed。runbook 已同步回 skill 正本（見上方 High Priority）
- Telegram replay-safety 兩條 high severity 未修（ACP 整輪 prompt 重放、/job resume 無 per-run lease）——已開案於 docs/SPEC-replay-safety-audit.md，設計先於動手
  📌 **2026-08-15 進展（H-1）**：SPEC 原本把「先量測這條重試實際救回多少次」列為裁決前置，
  實查後發現**那個問題現在問不出來**——31 天／10,989 筆 `events.jsonl` 裡符合的只有 1 筆，
  而且是夾在一個**失敗** prompt 的 `stderrTail` 裡；retry 事件的唯一消費者
  （`sessionManager.ts:777`）只 `console.warn`，∴ **成功的重試結構上不留痕**、樣本只含失敗端。
  ⛔ 不可寫成「重試救回 0 次」（有偏誤樣本當全稱）。前置條件已改寫成「先補遙測
  （retry attempt + outcome 各一個結構化事件）再回來裁決」；補遙測不改行為 ∴ 不受
  「會動到自動復原」那條顧慮拘束。
  ✅ **遙測已實作並 push**（`c7ae3fb` + 覆核修正 `95835a0`）：四種 outcome
  （succeeded / exhausted / cancelled / non_transient）落 `events.jsonl`，
  行為驗證用 `scripts/fake-acp-agent.mjs`（非原文比對），mutate 5/5 killed。
  ⚠️ **看數字前必讀三個前提**（已寫進 SPEC）：① `cancelled` 要與 `succeeded` 分開看
  ——初版就是把「重試後被取消」記成 succeeded，污染的正好是要量的那個數字；
  ② attempt 數與 outcome 數不保證相等（hang 住的輪不會有 outcome）；
  ③ specialist 走 acpClient 但不經 sessionManager ∴ 那條路徑沒有事件。
  📌 **下一步是等**：保留期 30 天（`event-log.ts` 的 `RETENTION_DAYS`），
  要在窗口內回來看 `succeeded` 有幾筆，再裁決 H-1 要不要改重試行為。
  **H-2（per-run lease）未動** —— 那是設計決策不是量測，性質與本輪不同。
- Mend User Key 資安債：沿用已外流的 Key，待輪替且新 Key 僅存 GitHub Secret
- ✅ **已處理 2026-08-15**：bridge-model-strategy 4 條 fact 已同步進 wiki。實際只有 3 條缺
  ——**第 4 條（advisor context 剝除機制）本來就在頁上**（`bridge-model-strategy.md:90-103`，
  含 `[Advisor response]` 佔位符的原始碼片段）∴ 該待辦的「4 條」是高估。新增三節：
  vendor pin 自報的鑑別力判準（glm-5 ✅／deepseek-3.2 零鑑別力／qwen3-coder-next 噪音）·
  `specialists.json` 的 pin 無閘門驗證（`moa-ref-codex` → `gpt-5.6-terra` 回 400）·
  HTTP MCP header 需手改設定檔。sources 補 f_3e1d20 / f_7dbef0 / f_982e49，`updated` 已 bump
- uk-slot-spec-to-impl skill-usage entry 為真孤兒（功能已併入 uk-slot-codegen），可考慮清理
- Underused skill 候選 8 個（writing-skills/dual-skill-review-loop/huashu-slides/self-eval-prompt-pattern/uk-slot-fake-reel-manager/uk-slot-multilang-sync/sync-fork-from-upstream/uk-slot-logo-localization）——僅觀察，不作退場依據
- 3 個 skill「常相關但 agent 不自報」（ms-cross-model-adversarial-review/ms-blackbox-probe-experiment-design/git-commit）——token 紀律問題
- wikilint 本輪僅深度檢查 9/50 頁，剩餘頁面 staleness 未逐一比對
- writing-skills 與 skill-creator 觸發情境重疊，待下次同時觸發時判斷

## Noise (ignored this run)
- /sharedsync、/dailylog、/sessionreflect、/specialistreflect、/docupdate、/specialistreview、/artifactcleanup、/backup 皆正常完成
- /memorytoskill 更新 3 個既有 skill（append），無新建，10 個 session 檔已歸檔
- /topicreview 成功套用（33 topics，misc 收斂至 3）
- /wikisync 5 頁更新完成，provenance 皆 blocking=0
- /factlint 完成 2 條 supersede，皆已驗證
- /wikilint 修正 2 頁 stale 內容 + 1 條斷連 wikilink，orphan 為 0
