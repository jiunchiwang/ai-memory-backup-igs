# claude-mem 精選寫入紀錄(繁中,供事後抽查)

## 2026-08-12(AUTO 模式;10 筆候選 → 精選 + 去重後寫入 3 條)

呼叫端機械讀到的本批 shortlist header（原樣照登,含亂碼）：
`<<> ?Ｙ?:2026-08-11T20:30:25.243Z;蝑:10(銝? 15);??epoch 1786338503767>>`

檔案自身 header 為「產生:2026-08-11T20:30:25.243Z;筆數:10(上限 15);自 epoch 1786338503767」——時間戳、筆數(10)、epoch 三者與呼叫端 header 一致,**無矛盾**。本批為全新批次（epoch 1786338503767 ≠ 前一批 1786193461343,筆數 10 ≠ 4）,**非重掃舊批**。

來源 project：`telegram-kiro-bridge-main`(8)、`uk_872_eyestrike2_client`(2),皆為 decision 類。

寫入 3 條：

1. telegram-kiro-bridge 決定不為 Kiro `--effort` 的靜默 no-op 加 runtime 警告（2026-08-11 commit 9897f46 pre-push 覆核通過時定案,來源未記錄理由）∴ bridge 端不會有任何訊號告訴你 ACP_EFFORT 對 kiro backend 沒生效;要判斷只能回頭確認該 backend 的 model 是不是 claude-sonnet-4.6（Kiro 上唯一吃 effort 的 model）。→ shard `bridge-config.md`
2. 已推翻的假設：停用 chroma 並不能防止 worker 靜默死亡——2026-08-11 觀測到 chroma 自 18:52 起已停用,worker 47424 仍於 19:07 無聲死亡 ∴ chroma 不是（唯一）成因,別再把「關掉 chroma」當修法、也不必重跑這個實驗（來源未載明該 worker 屬哪個子系統,故不在 fact 裡指名）。→ shard `bridge-project.md`
3. 要讓單一專案不受專案級 CLAUDE.md 某條指示約束（例如「改完自動 git commit」）,做法是在專案根建 CLAUDE.local.md 寫下反向指示壓過它,而不是去改共用的 CLAUDE.md——2026-08-11 於 uk_872_eyestrike2_client 用此法停掉自動 commit。→ shard `uk-872-eyestrike2.md`

精選階段淘汰（一次性過程紀錄,非跨 session 可重用）：

- 候選 3、4、5（Pre-push review approved 9897f46 / Pre-push commit verification workflow for 9897f46 / Pre-Push Independent Review Initiated,含 parallel_delegate id `parallel_delegate_793cac0ae7954fde869ef3091326f0cf`）：同一次 pre-push 覆核的三段動作紀錄,綁死單一 commit hash 與單一 delegate id。其中有方法論成分的部分既有 fact 已涵蓋——查「假設」命中的「中途擴張 scope 會把先寫好的『診斷』敘述凍結成現在式的假事實…（同一個 commit 9897f46 就補上了 max）…修正在 4ec4ece」已完整記錄該 commit 的教訓與 max 已補上的事實,故三條只留下唯一未被涵蓋的成分（不加 runtime 警告的決定,即上方第 1 條）。
- 候選 7（Refined Windows Spawn Bug Analysis with Evidence Grading :: readiness check 三路 OR：port probe (Bn) || alive status (qs()) || process check (s > 0 && Ve(s))）：識別字是壓縮後的 minified 名稱（Bn/qs/Ve）,換一次 build 就失效,無法跨 session 定位;證據分級本身既有 fact 已有更完整版本（查「證據等級」命中「研究／吸收外部 repo…每條主張都要標證據等級：A 級＝親自讀過原始檔案…B 級＝只根據摘要」）。
- 候選 9（Automated backfill monitoring implemented with 40-minute watch window :: 背景任務 b08kinmni 監看 "Backfill check complete for all projects"）：綁死單一背景任務 id 的一次性運維動作。
- 候選 6（Removed Invalid Cross-Version Comparison from Memory Document :: 移除「08-10：死 23 次但 0 個空窗」）：一次性的文件清理動作;可泛化成分（跨版本數據不能當證據）過於稀薄,且既有的證據紀律 fact 群（證據等級 A/B、可否證條件、「調整等待延遲後時間差不變就不是競態」）已覆蓋同一位置,單寫一條只會稀釋。

去重階段淘汰（命中既有 fact）：

- 候選 1（Sonnet-4.6[max] vs Opus-4.5 找 bug 能力 n=5 inconclusive、共同天花板）：**完全重複且已被超越**。既有 fact 已有兩條更完整的版本——「2026-08-12 實測…5 個真實 mutate-gate 變異…命中 sonnet 2/5、opus 3/5…n=5 差一題毫無區分力」以及擴大版「每臂 16 題…9/16 vs 6/16,配對 McNemar 5 對不一致、雙尾 p=0.375 ∴ 仍不能宣稱任一方更強」,後者已含「同源天花板」與註解效應的修正。
- 候選 2 的事實面（Kiro CLI 對所有 model 收 `--effort` 但只有 claude-sonnet-4.6 真的吃）：既有 fact 命中兩條——「Kiro CLI 2.16.2 的 effort 是 per-model…11 個 availableModels 中只有 claude-sonnet-4.6 可設,合法值 low/medium/high/max（無 xhigh）」與「`kiro-cli chat --effort bogus-zzz` 照跑且 exit 0…CLI 層完全不驗證、是靜默 no-op」。僅「不加 runtime 警告」這個決定為新,故只寫該決定。
- 「ACP_EFFORT_FALLBACK.kiro 已補上 max」：**刻意不寫**——既有的「中途擴張 scope」那條 fact 內文已明載 9897f46 補上了 max,且與本批候選同屬 effort 主題（未來查 effort 必定命中同一 shard）,再寫一次就是本步驟該擋掉的重複。

結果：**新增 3 條。未呼叫 forget。**

---

## 2026-08-11(AUTO 模式;4 筆候選 → 精選合併 + 去重後寫入 2 條)

呼叫端機械讀到的本批 shortlist header（原樣照登,含亂碼）：
`<<> ?Ｙ?:2026-08-10T20:30:03.592Z;蝑:4(銝? 15);??epoch 1786193461343>>`

檔案自身 header 為「產生:2026-08-10T20:30:03.592Z;筆數:4(上限 15);自 epoch 1786193461343」——時間戳、筆數(4)、epoch 三者與呼叫端 header 一致,**無矛盾**。本批為全新批次（epoch 1786193461343 ≠ 前一批 1786098514174,筆數 4 ≠ 2）,**非重掃舊批**。

來源 project：`verifier`(1)、`telegram-kiro-bridge-main`(2)、`uk_872_eyestrike2_client`(1),皆為 decision 類。

寫入 2 條：

1. （合併候選 1+2,同主題）telegram-kiro-bridge 的 run_plan 在指定的 specialist domain 不存在時會靜默 fallback 到 general、不向呼叫端顯示這次降級（2026-08-10 由 verifier 發現）;此案例被歸納成可泛化的「閘門盲視」失效形狀——檢查/路由機制存在但對「目標缺失」無感,對外回報成功、實際已偷偷換路徑,且已回填成方法論文件（commits 71f84a1、2528f9c 已 push）。→ shard `bridge-specialist.md`
2. uk_872_eyestrike2_client 的 MagicPotFlyToCenterTrail.prefab 兩支動畫（ES2_FGBoard_In_H、ES2_FGBoard_In_S）飛行路徑是烘進動畫裡的（baked path）、完全不靠骨骼定位 ∴ 要改飛行起訖點或落點,調整骨骼與節點座標不會有效果。→ shard `uk-872-eyestrike2.md`

合併說明：候選 1（run_plan 靜默 fallback 的可見性缺口）與候選 2（把 gate blindness 記成可泛化失效形狀,附 commit）是同一天同一主題的「現象」與「歸納」兩半,拆成兩條會互相指涉,故併為一條;去重時查「fallback」命中 18 筆、「靜默降級」3 筆、「run_plan specialist」0 筆、「gate blindness」0 筆、「backflow」0 筆——既有最接近的是「bridge 的 resume 直接賭一發 session/load、失敗才 fallback 開新 session 並只寫 stderr（靜默降級）」,那是 ACP session 路徑,與 specialist domain 路由不同機制,不構成重複。

精選階段淘汰（一次性過程紀錄,非跨 session 可重用）：

- 候選 4（Launched independent adversarial review agent for R-2 异源覆核 :: Agent a8d7da585723c4c47,claude-fable-5,覆核 CLAUDE.md 修改）：綁死單一 agent id 的「我派了一個 agent」動作紀錄。其中唯一有方法論成分的「CLAUDE.md 修改需要 R-2 異源覆核」在既有 fact 已有更完整版本（查「閘門」命中 12 筆,含「使用者的跨模型對抗覆核紀律於 2026-08-06 補上『不要把覆核自動化成無條件停止閘門』一節…覆核維持人為判斷觸發、不做無條件攔停」）,無新成分。

去重階段淘汰：無（2 條存活條目皆無命中）。

結果：**新增 2 條。未呼叫 forget。**

---

## 2026-08-09(AUTO 模式;2 筆候選 → 精選 + 去重後寫入 0 條)

呼叫端機械讀到的本批 shortlist header（原樣照登,含亂碼）：
`<<> ?Ｙ?:2026-08-08T20:30:03.436Z;蝑:2(銝? 15);??epoch 1786098514174>>`

檔案自身 header 為「產生:2026-08-08T20:30:03.436Z;筆數:2(上限 15);自 epoch 1786098514174」——時間戳、筆數(2)、epoch 三者與呼叫端 header 一致,**無矛盾**。本批為全新批次（epoch 1786098514174 ≠ 前一批 1786018890310,筆數 2 ≠ 7）,**非重掃舊批**。

來源 project：`uk_872_eyestrike2_client`（2 筆,皆為 decision 類）。

精選階段直接淘汰（一次性過程紀錄,非跨 session 可重用）：

- 候選 2（Second round review workspace integrity verification :: HEAD verified at commit 7c369051e23f02a6025802b2b755da071a17f9f5）：純粹是「某次覆核前確認工作區 HEAD 在某個 commit」的一次性動作紀錄,綁死單一 commit hash,無任何跨 session 可重用的判準或方法論成分。

去重階段淘汰（`list_facts` 命中既有 fact,實質重複）：

- 候選 1（Terminated recursive verification loop with documented residual risk after third round :: 第三輪用 kiro-cli --model glm-5,Zhipu 跨 vendor 強異源,對 commit c6fffcd）：查「覆核」命中 39 筆、「glm-5」命中 3 筆（其中 2 筆與前者重疊,聯集 40 筆）,其中三條合起來完全涵蓋本條的兩個成分——
  - 「終止遞迴覆核 + 記錄殘餘風險」→ 既有 fact「使用者的異源覆核紀律再擴充（2026-08-02）：第一輪覆核後修正產生的新 commit 要再派第二輪、且換新 agent 不告知前一輪結論;第二輪若回報無 high/medium 即視為收斂可 push,不強制第三輪 —— 但要誠實交代『覆核者的可 push 判斷是針對它看過的那個 commit,之後的修正 commit 未經覆核』」,以及「使用者的 Fable5 push 前覆核紀律已擴充為『可多輪、範圍逐輪收窄』…直到只剩敘事精確度類 finding 才收斂 push」。既有版本已把「何時可停」與「停下時要交代什麼殘餘風險」都寫死,比候選更完整。
  - 「glm-5 = Zhipu 跨 vendor 強異源」→ 既有 fact「異源覆核選型的核心判準：強異源與貴是兩個獨立的軸…glm-5 是 0.50x credits（比 Sonnet 便宜）卻是跨 vendor 強異源」已記載,且附帶成本軸的推論陷阱。
  - 本條無任何超出上述三條的新成分,丟棄。

結果：**新增 0 條。未呼叫 remember,未呼叫 forget。**

補充說明（依使用者指示）：寫入 0 條屬正常結果,不代表 producer 壞掉——本批 2 筆全出自 uk_872 當日的覆核 session,而該 session 期間產生的知識已即時寫進 AIMemory,隔日再以 claude-mem observation 形式出現在 shortlist,重疊本來就是預期行為。

---

## 2026-08-08(AUTO 模式;7 筆候選 → 精選 + 去重後寫入 2 條)

呼叫端機械讀到的本批 shortlist header（原樣照登,含亂碼）：
`<<> ?Ｙ?:2026-08-07T20:30:02.814Z;蝑:7(銝? 15);??epoch 1786018890310>>`

檔案自身 header 為「產生:2026-08-07T20:30:02.814Z;筆數:7(上限 15);自 epoch 1786018890310」——時間戳、筆數(7)、epoch 三者與呼叫端 header 一致,**無矛盾**。本批為全新批次（epoch 1786018890310 ≠ 前一批 1785929047040,筆數 7 ≠ 10）,非重掃舊批。

來源 project：`telegram-kiro-bridge-main`（6 筆）+ `uk_872_eyestrike2_client`（1 筆）。

精選階段直接淘汰（一次性過程紀錄,非跨 session 可重用）：

- 候選 1（uk_872 Idle State 旋轉與 Collect Symbol 觸發邏輯澄清:視覺元素分別亮起而非同時）：單一專案的規格澄清,無跨 session 可重用的方法論成分。
- 候選 2（派第二輪異源覆核驗證 F0–F5 修正,agent af8753828c9897050、d14923c→6190dce 共 10 檔）：單次派工紀錄;做法本身已由既有 fact「第一輪覆核後修正產生的新 commit 要再派第二輪、且換新 agent」涵蓋。
- 候選 4（為 BC-19/BC-20 修正發起跨 vendor 覆核,subagent_type codex:codex-rescue 審 commit 6898125）：單次派工紀錄,是既有跨 vendor 紀律的又一實例。
- 候選 6（以 mcp__bridge-actions__ask 佇列 cortex_domain_impl 五選項給使用者裁決）：單次互動紀錄。

去重階段淘汰（`list_facts` 命中既有 fact,實質重複）：

- 候選 5（異源覆核的 heterogeneity domain 單位是 model vendor,不是 CLI／harness／agent 名字）：查「覆核」命中既有 fact「2026-08-07 確立異源覆核的 domain 判定：異源性的單位是模型供應商而非 CLI／harness／分身名字…階梯為 強異源→弱異源→同源重置→不覆核,且降級必須留痕」→ 既有版本已含 kiro-cli 同源判定、防禦力邊界、降級階梯與留痕要求,**完全涵蓋且更豐富**,丟棄。

實際寫入：

1. （shard `adversarial-review`）收到 code review／異源覆核的 findings 時,處置有三個獨立維度而非一個：①這條成立嗎 ②它給的建議對嗎 ③它的修法屬不屬於本次改動的範圍——第三個維度最容易漏,成立且建議正確的 finding 仍可能把不相干的既有缺陷拉進來造成範圍蔓延,所以「不要盲目修掉每一條 finding」指的不只是駁回錯誤的 finding,也包含把正確但越界的 finding 記錄下來留待另一次改動處理（2026-08-07 telegram-kiro-bridge 建立 review-findings-pull-scope 記錄此模式）。
   - 與既有 fact 的關係：既有「覆核結論不可照單全收,每條 finding 須自己重現後才動手」管維度①、「異源覆核收到的 findings 有第三種處置：指的位置對、但建議是錯的」管維度②,本條補的是維度③（範圍),非重複。
2. （shard `bridge-doc-sync`）研究／吸收外部 repo 或文章時,筆記裡的每條主張都要標證據等級：A 級＝親自讀過原始檔案或原始碼查證過,B 級＝只根據摘要、README 或二手描述推得。這道標記是抗幻覺的紀律——分級本身會逼你察覺「這條其實沒查過」,也讓後續決策知道哪些前提還沒站穩;與「否定式主張要用二元探針覆核（如直接打 raw.githubusercontent 檔案 URL 看 200/404）而非採信摘要」互補（2026-08-06 telegram-kiro-bridge 於外部 repo 研究時定案）。
   - 與既有 fact 的關係：既有 2026-08-07 fact 記的是**探針手法**（GitHub tree API 截斷 → WebFetch 小模型自信答 no → 改打 raw URL 當二元探針）,本條記的是**標記紀律**（每條主張標 A/B 級）;手法解決「怎麼查」,紀律解決「哪些還沒查」,互補非重複。

結果：**新增 2 條**。未呼叫 forget。

---

## 2026-08-07(AUTO 模式;10 筆候選 → 精選 + 去重後寫入 2 條)

呼叫端機械讀到的本批 shortlist header（原樣照登,含亂碼）：
`<<> ?Ｙ?:2026-08-06T20:30:09.133Z;蝑:10(銝? 15);??epoch 1785929047040>>`

檔案自身 header 為「產生:2026-08-06T20:30:09.133Z;筆數:10(上限 15);自 epoch 1785929047040」——時間戳、筆數(10)、epoch 三者與呼叫端 header 一致,**無矛盾**。本批為全新批次,非重掃舊批。

來源 project：`telegram-kiro-bridge-main`（5 筆）+ `uk_872_eyestrike2_client`（4 筆）+ `system32`（1 筆）。

精選階段直接淘汰（一次性過程紀錄,非跨 session 可重用）：

- 候選 1/3（Task 4 / Task 1 之 UK 文件修正任務佇列）：單次任務建立與排序,非知識。
- 候選 5（Adversarial review prompt authored to scratchpad）：單次產出物路徑;做法本身已由 `ms-cross-model-adversarial-review` 既有紀律涵蓋。
- 候選 8（Code review of tween chain lines 628-677 confirms correct）：單次審查通過紀錄。
- 候選 2（Task 3 / GetBuyOdds 的 Client template limit vs Server DB cap）：同屬上述任務佇列紀錄,且 shortlist 自述為 *interpretive documentation additions without code evidence*——未經程式碼查證的解讀,依證據紀律不得寫成 fact。

去重階段淘汰（`list_facts` 命中既有 fact,實質重複）：

- 候選 7（codex adapter 兩套件 deprecated vs maintained）：查「codex-acp」命中既有 fact「Codex 的 ACP adapter 有兩個套件：@zed-industries/codex-acp 已 deprecated…維護中的是 @agentclientprotocol/codex-acp（1.1.9）」,既有版本含 raw probe 實測差異、pin 連動、authMethods 例外 → **既有更豐富**,丟棄。
- 候選 10（CDP attach mode 併入 igs-uof skill）：查「CDP」命中既有兩條 fact——Turnstile 只有接管非自動化瀏覽器能過（含 Playwright 兩臂皆敗實測）,以及「igs-uof 已在 2026-08-06 加入 CDP 接管模式（commit fce516d）」含 antibot 兩種相反處置與不寫 session.json 的理由 → **完全重複**,丟棄。
- 候選 4（SKILL.md 寫「three validation items」但程式實作四項）：查「覆核」/「閘門」命中既有兩條 fact——「異源覆核在文件層自我一致性（數字沒回頭同步、同頁多處寫死計數只改一處）上最有價值」與「計數類文件漂移的機械閘門期望值必須當場從真實來源算出」→ 本次只是同一模式的又一個實例,**實質重複**,丟棄。

實際寫入：

1. （shard `adversarial-review`）使用者的跨模型對抗覆核紀律於 2026-08-06 補上「不要把覆核自動化成無條件停止閘門」一節（寫進 AI-canonical 正本 ms-cross-model-adversarial-review/SKILL.md）,記錄把異源覆核接成 CLI stop-time 自動閘門（如 Codex --enable-review-gate 類）的陷阱——覆核維持人為判斷觸發、不做無條件攔停。
2. （shard `uk-slot-eye-strike`）uk_872_eyestrike2_client 的停輪節奏設計決策（2026-08-06）：每一輪停下後會先短暫停頓,才讓下一輪開始停輪,目的是為特殊符號的進場演出留出播放時間。

結果：**新增 2 條**。未呼叫 forget。

備註：① 覆核紀律那條寫入前確認 `覆核` shard 已有 29 條（成本分級、多輪換 agent、授權回報收斂、advisor 不可取代覆核）,但**無任何一條**談「自動化成無條件閘門」的取捨,故判為新增而非重複。② 停輪那條在 `停輪`(0 筆)/`轉輪`(4 筆)/`eyestrike2`(7 筆) 三個查詢下均無命中。③ shortlist 未提供停頓秒數或類別名,刻意不補寫細節。④ 本紀錄檔前一筆為 2026-08-01,中間 08-03-08-06 期間無 entry——依證據紀律不臆測原因（可能為寫入 0 條時未 append）,僅如實標記此空檔。

## 2026-08-01(AUTO 模式;12 筆候選 → 精選 + 去重後寫入 1 條)

來源 project：`telegram-kiro-bridge-main`（10 筆）+ `uk_917_leprechauns_pots_client`（1 筆）+ 2026-07-30 殘留 2 筆（shortlist 產生時間 2026-07-31T20:30:02.427Z，共 12 筆候選）。

精選階段直接淘汰（一次性過程紀錄，非跨 session 可重用）：

- 候選 4（Ghost Draft Fix Commit Strategy Decision）：內容是「建了一個 ASK action 詢問 F1 回歸測試範圍」→ 單次互動事件。
- 候選 6（User choice point: scope of fixes to apply before push）：單次選擇點。
- 候選 9（Chose status_first approach to fix streaming restart issue）：單次修法選擇；其技術結論已由既有 `status-channel` shard 的 4276f08 fact 涵蓋。

去重階段淘汰（`list_facts` 命中既有 fact，實質重複）：

- 候選 1（probe-* vs check-* 命名慣例）：查「probe」命中既有 fact，已完整記載「smoke runner 用 readdirSync 以 `check-*` 前綴自動發現，有真實副作用的探針刻意命名 `probe-draft-clearing.mjs` 並預設 dry-run、要 `--go`」→ **完全重複**。
- 候選 2+5（Fable5 push 前獨立對抗覆核 / checklist 精煉）：查「Fable」命中 22 條，含 2026-07-30、2026-07-31 的多輪覆核紀律與「檢查清單式 prompt 也能抓到 medium 缺陷」精煉條目 → **完全重複**。
- 候選 3（await gap opens finalize race）：查「await」命中既有 fact「在原本全同步的路徑中插入一個 await 就等於自己開了 finalize/cancel race 縫（2026-07-31 bridge F1 實證）」→ **完全重複**。
- 候選 7（status-channel.ts 零 import 硬約束）：查「status-channel」命中既有 fact，已載明零 import 原因（check-draft-streaming.mjs 單獨 transpile 成 data-URL module 載入）→ **完全重複**。
- 候選 8（順序型承重不變式的契約測試）：查「契約」命中既有 fact「模組契約測試（fake api 記錄 send/edit/delete）＋來源順序斷言＋mutation test 三件套」→ **完全重複**。
- 候選 11（Documentation sync fact-sourcing architecture）：查「Fable」命中既有 fact「doc-facts.ts 從 regex 撕原始碼重構為直接 import TypeScript 模組（COMMAND_SPECS/DEFAULT_STEPS/EVENT_TYPES）」→ **完全重複**。
- 候選 12（Vacuous assertion identification pattern）：查「vacuous assertion」命中既有 fact（含 truncateBotCommandDescription 276 字元實例）→ **完全重複**。

實際寫入（`uk-slot` shard）：

1. UK 老虎機要讓純邏輯能在 Cocos 編輯器外（ts-node）單獨測試，必須把運算層設計成 CC-free 的獨立模組：Game_Define.ts 本身 import 'cc' 與 astarte-framework，任何 import 它的模組在 ts-node 下都載不起來，所以像 bomb 事件結果計算這類純運算應抽成不依賴 cc / Game_Define 的一層（2026-07-31 uk_917_leprechauns_pots_client 實證）。此為可載入性問題，與「tsc --noEmit 要過濾只看 assets/Script 錯誤」的編譯期問題不同。

結果：**新增 1 條**。未呼叫 forget。

備註：本批 12 筆中有 7 筆是**完全重複**，比例明顯高於前幾批——原因是 2026-07-31 的 bridge draft/status race 工作在當下已直接寫入 AIMemory，claude-mem 只是同一批工作的第二次抽取。若此模式延續，可考慮把 shortlist 產生器的起始 epoch 對齊上次 ingest 時間以減少重複候選。

## 2026-07-30(AUTO 模式;4 筆候選 → 精選 + 合併 + 去重後寫入 2 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 產生時間 2026-07-29T20:30:02.527Z，4 筆候選）。

淘汰紀錄：

- 候選 1（Pre-push fact-checking review process for documentation updates）：`list_facts` 查「覆核」命中既有多條 fact——已涵蓋「push 前派獨立 Fable5 agent 審查分支」與「知識萃取類 commit 由 Fable5 對照真實原始碼逐項查證」；本次只是把同一做法套到 docs/roadmap HTML vs wiki 來源 → **實質重複**，丟棄。
- 候選 2（Kiro as primary implementation, Codex as fallback）：`list_facts` 查「委派」命中既有 Claude Max 5x 模型分配策略 fact（≥2k token 實作一律委派 Kiro）→ **實質重複**，丟棄。
- 候選 3+4（ACP adapter model 回報異質性 / model 身分注入架構）：**同主題合併**後寫入 2 條（去重時確認既有 fact 只涵蓋 claude-agent-acp 單一 adapter 的 probe 手法與注入位置，未涵蓋「三 adapter 回報形狀不同」與「實際 vs 請求值分欄保存」）。

實際寫入（皆 `bridge-acp` shard）：

1. 三個 ACP adapter 在 session/new 回報 model 的結構各不相同，因此「這個 session 實際跑什麼 model」的查證邏輯不能寫成單一通用解析——各 adapter 的回報形狀差異已記錄在 bridge 的 acp-model-report-shapes.md，新增或換 adapter 時須先實測其回報形狀再接線（2026-07-29）。
2. 處理「請求的 model 與實際生效的 model 可能不一致」時採用的架構是：AcpClient 用私有 `_sessionConfig` 欄位保存 adapter 回報的實際 model/effort，與呼叫端請求的 `opts.acpModel` 分開存放，讓靜默降級被記成事實而非回音請求值；model 身分注入排在 `initialize()` 之後、preamble 注入之前，因此不違反 preamble 凍結快照政策（2026-07-29）。

結果：**新增 2 條**。未呼叫 forget。

## 2026-07-26(第二批;同日重跑,shortlist 未變 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 產生時間仍是 2026-07-25T20:30:02.611Z，與本日第一批（見下方「## 2026-07-26」條目）完全相同的 2 筆候選——上游 shortlist 自第一批以來未再產生新內容）。

- 候選 1（CI gate via pre-push hook, GitHub Actions deferred）：`list_facts` 查「pre-push hook」命中既有 fact（本日第一批已寫入 `bridge-project` shard）→ **完全重複**，丟棄。
- 候選 2（Claude Max 5x Model Allocation Policy Established）：`list_facts` 查「model-allocation-max5x」命中既有 fact（`bridge-acp` shard 的核心分配策略）→ **完全重複**，丟棄。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-25(第五批;同日重跑,shortlist 未變 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main` + `system32`（shortlist 產生時間仍是 2026-07-22T20:30:24.953Z，與本日第四批完全相同的 2 筆候選——上游 shortlist 自第四批以來未再產生新內容）。

- 候選 1（Secret verification anti-pollution pattern，`telegram-kiro-bridge-main`）：`list_facts` 查「events.jsonl」再次命中同一條既有 fact → **完全重複**，丟棄。
- 候選 2（Memory Curation AUTO Mode Completed: Zero New Facts Ingested，`system32`）：仍是過程性執行紀錄，非架構決策/gotcha/pattern/trade-off → 於選取階段淘汰。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-25(第四批;shortlist 已改版更新,2 筆候選 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main` + `system32`（shortlist 產生時間 2026-07-22T20:30:24.953Z，內容與前三批不同——**上游已重新產生 shortlist**，不再是同一批 3 筆候選卡住不清空的狀況）。

- 候選 1（Secret verification anti-pollution pattern，`telegram-kiro-bridge-main`）：`list_facts` 查「events.jsonl」命中既有 fact（bash 指令逐字記進 events.jsonl → 驗證時字面值 grep 會自我重複污染 → 改用通用正則 `ghp_[A-Za-z0-9]{30,40}`）→ **完全重複**，丟棄。
- 候選 2（Memory Curation AUTO Mode Completed: Zero New Facts Ingested，`system32`）：內容是「上一輪精選跑完、0 條新增」的過程性執行紀錄，非架構決策/gotcha/pattern/trade-off → 於選取階段淘汰。

結果：**新增 0 條**。未呼叫 forget。

附註：先前追蹤的「shortlist 連續 3 輪未清空」問題本輪已不再出現，上游機制看起來已恢復正常清空/重製。

## 2026-07-23(第三批;同一份未清空的 shortlist,3 筆候選 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 檔仍是 2026-07-21T20:30:17 產出的同一批 3 筆候選，未被上游清空/重置，內容與前次 07-22 第二批完全相同）。

- 候選 1（Claude Max 5x Model Allocation Strategy）：`list_facts` 查「Max 5x」命中既有 fact（`bridge-acp` shard）→ **完全重複**，丟棄。
- 候選 2（Secret redaction 必須用正則避免透過 event logging 自我重複污染）：`list_facts` 查「events.jsonl」命中既有 fact（通用正則、自我重複污染迴圈）→ **完全重複**，丟棄。
- 候選 3（AI News Intelligence Pipeline 繁中輸出的主題設定：OpenAI/Anthropic/Gemini/AI models/Coding Agent/MCP/ACP/Data2Story）：屬單一 pipeline 的一次性主題設定快照，非跨 session 可重用之架構決策/pattern/trade-off → 於選取階段淘汰（結論與前次一致）。

結果：**新增 0 條**。未呼叫 forget。

附註（非本任務範圍）：`claude-mem-shortlist.md` 連續第 3 輪未被上游清空，同一批候選重複出現——建議之後找時間查上游產生/清空 shortlist 的機制。

## 2026-07-22(第二批;來源 shortlist 3 筆 → 精選 + 去重後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（shortlist 2026-07-21T20:30 產出，3 筆 decision 候選）。

- 候選 1（Claude Max 5x Model Allocation Strategy，`.claudedocs/model-allocation-max5x.md`）：`list_facts` 查「Max 5x」命中既有 fact，2026-07-21 已寫入 `bridge-acp` shard → **完全重複**，丟棄。
- 候選 2（Secret redaction 必須用正則避免透過 event logging 自我重複污染）：`list_facts` 查「events.jsonl」命中既有 fact（`ghp_[A-Za-z0-9]{30,40}` 通用正則、自我重複污染迴圈），內容完全對應 → **完全重複**，丟棄。
- 候選 3（AI News Intelligence Pipeline 繁中輸出的主題設定：OpenAI/Anthropic/Gemini/AI models/Coding Agent/MCP/ACP/Data2Story）：屬單一 pipeline 的一次性設定快照，非跨 session 可重用之架構決策/pattern/trade-off → 依「丟一次性步驟」規則於選取階段淘汰。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-22(來源 shortlist 1 筆,同一份未清空的 shortlist → 精選後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（同 2026-07-21 那批候選，shortlist 檔自 2026-07-20T20:30:05 起未變動，仍是同一筆 Model allocation strategy 候選）。

- 候選（Model allocation strategy for Claude Max 5x quota optimization）：`list_facts` 查核「Max 5x」「model-allocation-max5x」「Sonnet 級還是 Opus 級」皆命中既有 fact——2026-07-21 已將此候選拆成 2 條寫入（`bridge-acp` shard 的核心分配策略 + `misc` shard 的快速判準/workflow model override 提醒），內容完全對應 → 判定**完全重複**，丟棄。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-21(來源 shortlist 1 筆 → 精選合併後寫入 2 條)

來源 project：`telegram-kiro-bridge-main`（1 筆 2026-07-20 decision：Model allocation strategy for Claude Max 5x quota optimization，產物 `.claudedocs/model-allocation-max5x.md`）。

- 唯一候選為跨 session 可重用的模型分配策略（架構決策 + trade-off + 決策判準），非一次性步驟 → 保留。
- `list_facts` 查核「Claude Max 5x 模型分配」「Kiro 委派 Opus quota」「模型分配」皆無現存 fact，「Kiro」shard 內既有 fact 只涉 specialist-domains.json 個別 model 選擇，與此配額分配策略不重複 → 非重複。
- 依「同主題合併」拆成 2 條耐久知識並 `remember()`：
  > 1.「Claude Max 5x 模型分配策略：Opus 只留給高認知決策、≥2k token 實作委派 Kiro、Haiku 機械操作、Sonnet 協調；配額受全模型週上限 + Sonnet 專屬週上限兩道牆，且跨 Claude.ai/Code/Cowork 共用」（寫入 `bridge-acp` shard）
  > 2.「模型分配快速判準：自問『這錯誤是 Sonnet 級還是 Opus 級』——可重跑錯誤降級委派、會污染下游決策的錯誤才用 Opus；Workflow/subagent 必須顯式指定 model override 否則配額爆掉」（寫入 `misc` shard）

結果：**新增 2 條**。未呼叫 forget。

## 2026-07-20(第二批;來源 shortlist 1 筆 → 精選後寫入 0 條)

來源 project：`telegram-kiro-bridge-main`（1 筆 2026-07-19 decision）。

- 唯一候選：Fable5 review 核准 commit `b3eb670` 修正、PUSH-VERDICT: GO，驗證 relay mode 的 relayReplyTo 現會跳過 line 1121 commit 區塊、讓 relayDelegateTokens 送達 line 1279 headless loop。
- 判定：綁定特定 commit hash 與行號（1121、1279）的一次性審查判決，屬過程紀錄，無跨 session 可重用價值 → 依「丟一次性步驟／單檔瑣碎改動」規則丟棄。
- 選取階段即淘汰，故無需去重、無 `remember` 呼叫。

結果：**新增 0 條**。未呼叫 forget。

## 2026-07-20(來源 shortlist 5 筆 → 精選合併後寫入 2 條)

來源 project：`telegram-kiro-bridge-main`（5 筆皆 2026-07-17 decision，全屬同一主題：暖機佇列架構的 dev-design workflow 產物，該功能已合併 commit 0149d82）。

- 5 條候選同主題，依「同主題合併」處理：candidate 5（multi-agent design workflow launched wf_ae97cee1）為純過程紀錄 → 丟；candidate 1（judge-panel 判決）+ 2/3/4（三個競爭方案細節）合併為 2 條耐久知識。
- `list_facts` 查核「暖機」「warmup」「coreReady」皆無現存 fact → 非重複，寫入 `bridge-project` shard：
  > 1.「telegram-kiro-bridge 的暖機期訊息處理最終採 MVP-first 方案（warmup.ts：coreReady 旗標 + FIFO 佇列暫存原始 grammy Update，就緒後 replay），judge-panel 72 分勝過 robustness-first 54 / simplicity-first 40，並嫁接後兩者關鍵設計」
  > 2.「暖機佇列可重用 trade-off：fetchReady（runner 已在 poll、訊息不遺失）vs coreReady（訊息→agent 路徑完全安全）是兩個獨立就緒層，長輪詢 bot 有慢速啟動階段時應分開處理」

結果：**新增 2 條**。未呼叫 forget。

## 2026-07-19(來源 shortlist 2 筆，同一份未清空的 shortlist → 精選後寫入 1 條)

來源 project：`telegram-kiro-bridge-main`（同 2026-07-18 那批候選，shortlist 檔自 2026-07-17T20:30:02 起未變動）。

- 候選 1（turn-lint warn-only 策略理由）：`list_facts` 查核仍是重複 → 丟，判定與 2026-07-18 一致。
- 候選 2（獨立 Fable5 review 核可 merge 推送 origin）：**推翻 2026-07-18 的「一次性過程紀錄」判定**。核對 `git log --grep="Fable5"` 發現該做法已在至少 4 個獨立 commit 中出現（`04cc0bc` 訊息明確寫「Fable5 push 前覆核」），確認是跨 session 反覆使用的專案慣例而非單次紀錄 → 改寫為繁中 fact 並 `remember()` 寫入 `bridge-project` shard：
  > 「telegram-kiro-bridge 完成 merge/sync 後、push 到 origin 前，會先派一個獨立的 Claude Fable 5 agent 覆核合併安全性，確認無誤才 push——避免有問題的合併直接推上遠端」

結果：**新增 1 條**。未呼叫 forget。

## 2026-07-18(來源 shortlist 2 筆 → 精選後寫入 0 條)

來源 project:`telegram-kiro-bridge-main`(2 筆,皆 2026-07-17 decision)。

候選:
1. turn-lint warn-only 策略理由(啟發式正則做問句/語言比例判斷)。
2. 獨立 Fable 5 review 核可 merge 推送 origin。

判定:
- 候選 1 **重複**:AIMemory 已存在幾乎逐字對應的既有記憶「telegram-kiro-bridge 的 turn-lint 因為判斷邏輯是啟發式正則(問句/語言比例判斷),容易對 code block、反問句等正常內容產生 false positive,所以選擇只 console.warn 觀察」→ 丟。
- 候選 2 **一次性過程紀錄**:單次 merge 的獨立審查核可 log,非跨 session 可重用決策/做法 → 丟。

結果:**未寫入任何新記憶**。未呼叫 forget。

## 2026-07-17(來源 shortlist 2 筆 → 精選合併後寫入 0 條)

來源 project:`telegram-kiro-bridge-main`(2 筆,皆 2026-07-16 decision,igs-uof 合併同事唯讀設計時保留個人加班單填寫擴充)。

精選:兩筆合併為同一決策(保留 uof_form.py 個人擴充 + 於 DESIGN.md 記載理由),視為同一件事的兩個面向。

去重:以 list_facts 查詢 igs-uof、個人擴充、唯讀,發現 AIMemory 已存在完全對應的既有記憶——「使用者決定 igs-uof 保留原 vc-uof-hours 的加班單 dry-run 填寫功能(uof_form.py),標註為『個人擴充,非公司共享唯讀範圍』——同事的 v2 設計原本已排除寫入操作;若要把 skill 整包分享給同事需重新評估是否移除該檔案」。判定為完全重複,**未寫入任何新記憶**。未呼叫 forget。

## 2026-07-16(來源 shortlist 5 筆 → 精選合併後寫入 2 條)

來源 project:`uk_slot_template`(4 筆,皆 2026-07-15 decision,MaskExpand/board visibility 架構)、`telegram-kiro-bridge-main`(1 筆,2026-07-15 decision)。

1. [合併 shortlist MaskExpand multi-mask / mask expansion revert / SetVisibleSymbolCountOverride 三筆 → shard uk-slot-template] uk_slot_template 專案:MaskExpand 元件需支援多重遮罩(multi-mask),而非僅單一遮罩;此設計曾因疑慮被使用者還原一次,後續於 IMaskExpandHost 介面新增 SetVisibleSymbolCountOverride() 方法(IMaskExpander.ts),用以橋接本地與遠端架構的可見符號數量覆寫機制。
2. [蒸餾 shortlist server-side partial board visibility 一筆 → shard uk-slot-template] uk_slot_template 專案的架構策略:Server 端只送出玩家可見的盤面資料(例如 5x6),而非完整盤面尺寸(例如 7x6),其餘部分由客戶端做前處理。

捨棄:telegram-kiro-bridge-main 的「status 指令合併衝突以 git checkout --theirs 採用上游版本」——屬一次性合併衝突解決紀錄,無跨 session 重用價值。

去重:以 list_facts 對 AIMemory(247 筆)查詢 MaskExpand、board visibility,均無匹配,確認兩條皆為淨新增。未呼叫 forget。

## 2026-07-15(來源 shortlist 15 筆 → 精選合併後寫入 5 條)

來源 project:`uk_slot_template`(9 筆,皆 2026-07-14 decision,mask expansion 整合架構 dev-design workflow)、`telegram-kiro-bridge-main`(6 筆,皆 2026-07-14 decision)。

1. [來源 telegram-kiro-bridge-main → shard misc] 撰寫可攜式 skill 時,若該 skill 會被多個 agent CLI(如 Kiro、Codex、Claude)或多台機器共用,應避免在 SKILL.md 中寫死絕對路徑(例如特定磁碟機代號或使用者目錄),以免跨環境失效。
2. [合併 shortlist ask_user timeout / workspace architecture 兩筆 → shard bridge-project] 為「無長駐行程、僅一次性執行」的 headless CLI agent bridge(如 Telegram-Kiro bridge)設計架構時,不能直接套用長駐 async process 的模式(例如同步阻塞等待回覆、非同步 inbox 消費模型),因為一次性 spawn 無法 await 或暫留對話回合;架構評估應先確認目標執行模型是否相容,再決定是否套用既有模式。
3. [合併 shortlist improvement harness 相關兩筆 → shard bridge-research] 引入結構化錯誤記錄機制(例如帶 fix_applied 欄位的 improvement harness)不一定能提升實際當機診斷能力;若事後檢討發現真正缺口是「紀律」(例如 catch block 中確實記錄錯誤內容),就應該優先補強紀律而非疊加新的基礎設施。
4. [蒸餾 uk_slot_template judge panel 評分紀錄 → shard bridge-research] 在 multi-agent 的 dev-design workflow 中,即使 judge panel 把某提案排名第一,該提案也可能被評為「無法照案直接實作」(例如僅 5.5/10 分),這代表評分結果本身是需要再迭代設計的訊號,不該直接採用第一名方案進入實作。
5. [蒸餾 uk_slot_template adversarial 8 findings 紀錄 → shard bridge-research] dev-design workflow 的 Explore phase 若宣稱「現有程式缺少某項能力」(例如缺少方向感知),該宣稱有可能是錯的(該能力其實透過其他底層邏輯間接實現),因此 adversarial 驗證階段應優先檢查 Explore 階段的假設是否成立,而不是只驗證新提案本身。

捨棄:uk_slot_template 的 mkdir artifacts 目錄建立記錄、workflow 啟動記錄(2筆)、7個 unknowns 清單、以及三個具體設計提案(IMaskExpander/策略介面/外部 controller)——皆為該次 mask expansion 功能的一次性執行細節或遊戲特定實作方案,無跨 session 重用價值;telegram-kiro-bridge 的「specialist knowledge backflow」單純描述問題現象未附解法,暫不收錄。

去重:以 list_facts 對 AIMemory(240 筆)分別查詢 portable skill absolute path、headless bridge async spawn、improvement harness fix_applied、judge panel proposal score、explore phase adversarial verify existing mechanism,五條查詢均無匹配,確認皆為淨新增。未呼叫 forget。

## 2026-07-14(來源 shortlist 6 筆 → 精選合併後寫入 2 條)

來源 project:`telegram-kiro-bridge-main`(6 筆,皆 2026-07-13 decision)。

1. [合併 shortlist #2+#3 → shard bridge-acp] telegram-kiro-bridge 設計跨 backend 量化自評（SELF_EVAL token）機制時，對抗性審查否決了三個複雜方案，發現六個共通致命缺陷,可作為未來設計類似自評/評分機制的通用檢查清單:(1) tsc 型別驗證可被 agent 謊報低分繞過;(2) 觸發條件可能與 Kiro/Codex 等 backend 已知限制互相矛盾;(3) circuit breaker 整合的前提條件未經驗證;(4) 沒有證據顯示 backend 真的會遵守自評指令;(5) 未驗證的實作細節被當成行為契約使用;(6) 巢狀 payload 會破壞既有的扁平欄位慣例。
2. [蒸餾 shortlist #4 → shard bridge-project] 當方法論缺乏量化評分機制(例如沒有「≤95 分即重做」這類邏輯)時,telegram-kiro-bridge 曾設計一套可參考的範本:跨 6 個維度、總分 100 分——型別驗證 V:25、功能測試 T:20、影響分析 I:20、範圍紀律 S:15、完整性 C:10、回讀驗證 R:10。

捨棄:shortlist #1(第二次 dev-review workflow 啟動記錄)、#5(vc-uof-hours skill 對抗驗證審查完成記錄)、#6(P2 實作計畫拆四個任務)——皆為一次性任務執行紀錄,無跨 session 重用價值。

去重:以 list_facts 對 AIMemory(225 筆)查詢 SELF_EVAL、自評、telegram-kiro-bridge、評分機制、circuit breaker,確認兩條皆為淨新增。未呼叫 forget。

## 2026-07-10(來源 shortlist 2 筆 → 精選後寫入 1 條)

來源 project:`telegram-kiro-bridge-main`(2 筆,皆 2026-07-09 decision)。

1. [合併/蒸餾 shortlist #1 → shard uk-slot] 記錄反覆出現的 AI 失誤時，把「常見錯誤」分兩類:流程偏離(Process Deviations,工作流順序失誤,如未先 invoke skill 從步驟0開始、跳過前置 checklist、基準拿錯衍生品)與技術錯誤(Technical Errors,實作層面失誤,如型別/邏輯/命名寫錯);兩類根因與修法不同,分開列並各附 session 實證。此分類法可推廣到任何 skill/knowhow 庫的錯誤紀錄。

捨棄:shortlist #2(Clash of Olympus dev-spec baseline 從 tripleCoinTreasure-client 改為 uk_slot_template + uk-slot-pattern-library)——可重用核心已由既有 fact「uk-slot-spec-to-impl 流程教訓…基準永遠是 uk_slot_template 不是衍生品;步驟2必須讀 pattern-library 索引」完整涵蓋,屬重複;而 Clash of Olympus 該次 spec 修訂本身是一次性專案事件。

去重:寫入前以 list_facts 對 AIMemory(179 筆)掃描 常見錯誤/spec-to-impl/流程偏離/技術錯誤/dev-spec/tripleCoinTreasure/knowhow/錯誤分類——確認兩類錯誤 taxonomy 為淨新增(既有僅記「常見錯誤新增5條流程偏離實證教訓」,未存分類法本身),#2 為重複。未呼叫 forget。

## 2026-07-09(來源 shortlist 6 筆 → 精選後寫入 1 條)

來源 project:`telegram-kiro-bridge-main`(5 筆)、`system32`(1 筆)。

1. [來源 system32,#6 → shard bridge-project] 當 session 的 memory MCP server 未連線(ToolSearch 找不到 list_facts/remember)時,可在 G:\AI\AIMemory\tmp\mcp-call.mjs 自建 stdio JSON-RPC helper 直接 spawn G:\AI\telegram-kiro-bridge-main\dist\mcp-memory.js 呼叫記憶工具——關鍵是 cwd 須設為 bridge 專案根(dotenv 才能載到 .env)、注入 MEMORY_USER_ID 與 MEMORY_DIR=G:\AI\AIMemory,用法 node mcp-call.mjs <toolName> '<jsonArgs>' 或 @argsFile;tmp/ 會被定期清空,helper 不在時照此模式重建即可。

捨棄:#1–#5(Rich Messages PoC 裁決/升級路線/grammY 1.44 支援/@grammyjs/stream append-only 否決/fix 選項執行)——AIMemory 既有 facts 已完整涵蓋(Rich Messages 升級評估、PoC 裁決列 P2、editMessageText 合法 rich 渲染、429 誤解修正、api.raw Proxy 死碼等多條),全屬重複。

去重:寫入前以 list_facts 掃描 mcp-call / mcp-memory / JSON-RPC 等關鍵詞(155 筆),無重複。本次並實際重建了已被清掉的 mcp-call.mjs helper(加上 @argsFile 支援,避免 Git Bash 反斜線跳脫問題)。

## 2026-07-01(來源 shortlist 10 筆 → 精選後寫入 2 條)

來源 project:`telegram-kiro-bridge-main`(Post-Tool Hook 多 agent 設計工作流)。

1. [來源 telegram-kiro-bridge-main,#6 → shard bridge-project] AI 長期警戒模式清單(問題追蹤.md 的 7 條,設計架構師必讀):#001 未查證就宣稱存在、#002 存在 vs 路由混淆、#003 單一來源推斷、#004 忽略字面證據、#005 共享值私有化、#006 行數預算過度樂觀、#007 單一視角自審盲點;可作對抗檢查清單。
2. [來源 telegram-kiro-bridge-main,合併 #5/#7/#8 → shard misc] 可重用多 agent 設計工作流(dev-design)四階段:Explore 查證程式碼 → Propose 3 個競爭方案(常收斂到單一寫入匯流點)→ Adversarial 找致命缺陷評分 → Synthesize 整合最終規格;能在設計初期抓出如多輪迴圈 snapshot 過期(staleness)之類隱性 bug。

捨棄:#1/#2(EyeStrike2 Trail/FlyManager 實作細節)、#3(throwaway-cluster.mjs 一次性驗證腳本)、#4(P1-design-spec.md 產物建立)、#9(工作流啟動 run ID)、#10(NearWin 最小手術選型)皆屬一次性專案實作/過程紀錄,非跨 session 可重用。

去重:寫入前以 list_facts 對 AIMemory(75 筆)掃描 design workflow / adversarial / vigilance / self-review,皆無重複。

## 2026-06-26(來源 shortlist 5 筆 → 精選合併後寫入 1 條)

來源 project:`uk_pirates_queen`(掉落動畫時序重構工作流)。

1. [合併 #3/#4 → shard uk-slot] uk_pirates_queen 掉落動畫凍結視窗回歸:根因為把凍結語意(m_isInDropMode)與掉落動畫 promise(m_dropAllSymbolsOutOfScreenPromise)混為一談、且在 StartSpin(L943)直接觸發掉落;採 MVP 最小手術——拆出 m_isInDropMode 專職凍結、promise 降為純動畫 handle、掉落觸發移到獨立 TriggerDropOut() method。

捨棄:#1(multi-agent review 啟動)、#5(設計工作流啟動 wf_2ff596b5)屬一次性過程紀錄;#2(judge panel 評分 66/58/42)為一次性評選結果,可重用技術核心已併入上條。

去重:寫入前以 list_facts 對 AIMemory(70 筆)掃描 pirates_queen / DropOut / freeze / StartSpin,皆無重複。

## 2026-06-25(來源 shortlist 5 筆 → 精選後寫入 2 條)

來源 project:`uk_pirates_queen`、`uk_872_eyestrike2_client`。

1. [來源 uk_pirates_queen,#1 → shard user-pref] 使用者偏好 git commit 前先確認:執行 commit 之前應多問幾個釐清問題並取得使用者同意,不要逕自 commit。
2. [來源 uk_872_eyestrike2_client,合併 #4/#5 → shard misc] 驗證 TypeScript 介面重構/整併時用 npx tsc --noEmit 做型別檢查;遇 TS6.0 deprecation 警告可加 --ignoreDeprecations 6.0 抑制以聚焦真正錯誤。

捨棄:#2/#3(telegram-kiro-bridge 分支改名 main-old-backup、cherry-pick --skip commit 0610f54)屬一次性 repo 狀態事件,非跨 session 可重用。

去重:寫入前以 list_facts 對 AIMemory(67 筆)掃描;既有「git commit 訊息使用中文」與本次「commit 前先確認」屬不同面向,TS 既有條目為專案/文件性質,皆無重複。


## 2026-06-19(來源 shortlist 15 筆 → 精選合併後寫入 4 條)

來源 project:`10.3.1`(AI 策略)、`uk_pirates_queen`(老虎機)。

1. [來源 10.3.1,合併 #1/#3/#5] 跨模型 AI 策略 v4 核心原則:正典語料庫本身就是產品——以 markdown + git 追蹤的精煉知識為唯一真實來源(G:\AI\AI-canonical),CLI / MCP / bridge / 索引都只是部署基礎設施而非產品本體。
2. [來源 10.3.1,合併 #2/#4] AI 產物雲端 vs 本地儲存政策:正典 skills、steering 政策與通用文件放公開 GitHub repo(AI-canonical);session 執行日誌與框架內部狀態僅保留本地、不進版控。
3. [來源 uk_pirates_queen,#12] 並發 gotcha:在 Promise.all 之前的同步階段計算狀態決策(如 willGhost),會與並發 group dispatch 產生 race condition;應移到 async 階段計算以避免競態。
4. [來源 uk_pirates_queen,合併 #10/#19] Cocos 版面「兩項移除一項」避免置中跳動(snap):用 ghost slot 雙佔位機制,在不改動 Layout 參數前提下同時滿足 0→1 置中、2→1 不跳動與旋轉相容。

捨棄:Wanted Poster 多筆設計規格草稿/方案排名/smoke-test 等一次性過程紀錄(#7–#9、#11、#13–#18);#6 ExtraBet 公版還原屬一次性事件,且「禁改公版」已由 UK conventions 涵蓋。

去重:寫入前以 list_facts 對 AIMemory(53 筆)掃描,皆無重複。

## 2026-06-20(來源 shortlist 1 筆 → 精選後寫入 1 條)

來源 project:`10.3.1`(AI 策略)。

1. [來源 10.3.1] 在 headless(無人值守)Claude 自動化腳本中,用 claude.exe 的 --disallowedTools 參數封鎖 mcp__memory__remember 與 mcp__memory__forget,即可強制走 proposal-only(只提案、不直接寫入記憶)工作流程,避免自動流程擅自改寫長期記憶。

去重:寫入前以 list_facts 對 AIMemory(claude-mem / disallowedTools / headless / daily-claudemem 多關鍵字)掃描,無重複。

## 2026-06-23(來源 shortlist 2 筆 → 精選後寫入 1 條)

來源 project:`uk_872_eyestrike2_client`(老虎機 client)。

1. [來源 uk_872_eyestrike2_client] uk_872_eyestrike2_client 專案架構規範:Spine 動畫一律透過 SpineKit 播放(統一的 Spine 播放架構),不直接操作底層 spine 元件。

捨棄:「Skin assets 指定用於 feature grid 中段過場燈光演出」屬單一專案特定場景的一次性細節,非可重用 pattern。

去重:寫入前以 list_facts 對 AIMemory(Spine / SpineKit 關鍵字,62 筆)掃描,既有 Spine 紀錄皆為 spine-viewer 工具相關,無重複(寫入後 shard=uk-slot.md)。

## 2026-07-07(來源 shortlist 6 筆 → 精選後寫入 3 條)

來源 project:`telegram-kiro-bridge-main`(bridge 專案,2026-07-06 decisions)。

1. [來源 #1] telegram-kiro-bridge 的 skill lint(skill 健康檢查)機制:讀取 G:/AI/AIMemory/config/skill-usage.json 的 use_count 與 last_agent_used_at 使用數據,評估各 skill 是否仍被使用、是否需要淘汰或修整。(shard=bridge-project)
2. [來源 #3] 使用者評估過三模型分工架構提案(Fable 5 當 orchestrator 佔約 10% tokens、Codex 5.5 當 executor 佔約 60%、Gemini 3.1 Pro 當 reviewer 佔約 15%),決定暫緩不採用,避免未來重複提案。(shard=misc)
3. [來源合併 #5/#6] telegram-kiro-bridge 的 gate hook 決策已反轉:專案記憶文件 decision-no-gate-hook.md 改名為 decision-gate-hook-minimal.md,改採最小版 gate hook;CLAUDE.md Section 7 的完整 impact-analysis-guard PreToolUse hooks 維持不部署,此決策文件用於防止未來重複提案。(shard=bridge-acp)

捨棄:#2(Excel→code 三步驟工作流)與既有 f_411e3f(uk-slot-spec-to-impl skill)重複;#4(PARALLEL_DELEGATE >> 截斷 gotcha)與既有 f_3c7a91 重複。

去重:寫入前以 list_facts 對 AIMemory(91 筆;skill-usage / skill lint / orchestrator / Codex 5.5 / gate-hook / impact-analysis 多關鍵字)掃描,皆無重複。

備註:本 session harness 未載入 memory MCP tools(server 未連上),改以 stdio JSON-RPC 直呼同一 mcp-memory.js 的 list_facts / remember tool(同一安全代碼路徑,僅 ADD,未動 forget)。

## 2026-07-08(來源 shortlist 11 筆 → 精選後寫入 2 條)

來源 project:`telegram-kiro-bridge-main`(2026-07-07 decisions;內容涵蓋 bridge 與 uk slot 兩域)。

1. [來源 #9] uk slot 模板專案音訊決策:MG_Bgm 與 FG_Bgm 背景音樂引用在 template 專案中先註解掉(模板不附實際音檔),新遊戲專案需要 BGM 時再解除註解並補上音檔。(shard=misc)
2. [來源 #10] Cocos extensions 目錄採專案隔離架構:棄用 G:/Cocos_Project/extensions 共用目錄,改置於各專案自身的 extensions/(如 uk_917_leprechauns_pots_client/extensions/),避免多專案共用一份 framework 互相干擾。(shard=uk-917)

捨棄(9 筆):#1 token policy 已由既有 fact(token-policy.ts commit 028a5ea 顯式 policy 表 + provenance)以更終態形式涵蓋;#2 park()/onBeforeClose 汙染為中途發現、既有 fact 已記「四條 transcript 儲存路徑皆正常運作」終態;#4 SessionStore 多 session 設計已由「/session 多 session 管理 2026-07-07 結案(5 commits)」涵蓋;#5 /agent 預設 config 已由 /agent init(commit 8613135)兩條 facts 涵蓋;#8 session resume 計畫已有 fact 記錄計畫文件路徑與三層架構;#11 GRAND/MEGA 走標準收分流已由 f_23086a 涵蓋;#3/#6/#7 為一次性過程紀錄(選 workflow、啟動 review、委派 Kiro)不入庫。

去重:寫入前以 list_facts(tail 20/146)+ 直接 grep facts 主檔與 facts_Topic shards(MG_Bgm / extensions / GRAND / MEGA / 917 多關鍵字)掃描,確認 2 條無重複。

備註:本 session harness 同樣未載入 memory MCP tools,沿用 stdio JSON-RPC 直呼 mcp-memory.js 的 list_facts / remember(僅 ADD,未動 forget);server 需以 bridge 專案目錄為 cwd 啟動(否則 .env 的 TELEGRAM_BOT_TOKEN 讀不到)。

## 2026-07-11(來源 shortlist 4 筆 → 精選後寫入 1 條)

來源 project:`telegram-kiro-bridge-main`(2026-07-10 decision)。

1. [來源 #1] telegram-kiro-bridge 的 Rich Message 草稿串流(Path A)採三階段生命週期:先 sendMessageDraft 送空草稿顯示「Thinking…」,再用 sendRichMessageDraft 串流更新草稿內容,最後以 sendRichMessage 定稿;完整規格見 SPEC-draft-streaming.md。(shard=bridge-streaming)

捨棄(3 筆):#2/#3/#4 皆為 2026-07-09 curation session 的去重查詢過程紀錄(「query 回傳 0/179」),屬一次性過程紀錄,不具跨 session 重用價值,不入庫。

去重:寫入前以 list_facts(tail 20/195)雙查詢(draft streaming / sendMessageDraft / Rich Message / 三階段 等關鍵字)確認 0 重複。

備註:本 session harness 同樣未載入 memory MCP tools,沿用 stdio JSON-RPC 直呼 mcp-memory.js 的 list_facts / remember(僅 ADD,未動 forget)。

## 2026-07-12(AUTO)

來源 shortlist:4 筆候選(皆 telegram-kiro-bridge,2026-07-11)。精選後寫入 1 筆,丟棄 3 筆一次性任務建立紀錄(Task #10/#12/#15)。

1. skilllint 於 2026-07-11 將 knowhow-accumulation、non-engineer-agent-design、skill-creator 三個 skill 標記為殭屍(zombie)skill,但經評估後決定保留不刪;日後 skilllint 再標記這三個 skill 時應視為已知豁免,不需重複提案刪除(來源:telegram-kiro-bridge)

## 2026-07-26

來源 shortlist：2 筆候選（產生於 2026-07-25T20:30Z）

寫入 1 條：

- (telegram-kiro-bridge) CI 把關決策（2026-07-25）：測試把關靠本機 pre-push hook 執行，GitHub Actions 暫緩導入；`.github/workflows/ci.yml` 雖已寫好並在本機驗證通過（86/86 測試），但刻意保留為未追蹤檔案不進版控——未來看到該檔案未 commit 屬預期狀態，不是遺漏。→ shard: bridge-project

丟棄 1 條：

- (telegram-kiro-bridge) Claude Max 5x 模型分配政策建立 → 去重丟棄，AIMemory 已有等價 fact（model-allocation-max5x 策略條目）

## 2026-07-27（AUTO）

來源 shortlist：3 筆候選（產生於 2026-07-26T20:30Z，皆 telegram-kiro-bridge）

寫入 2 條（shard: telegram-kiro-bridge）：

- 背景通知 flakiness 於 2026-07-26 經量測推翻 race condition 假設：sleep 縮到 2s、turn 長 31.9s 時通知仍固定在 turn 結束後 +3.0s 才到、未併入該 turn——可重用判準「調延遲後時間差不變就不是競態」，修復方向改從通知投遞路徑下手。
- 2026-07-26 派 Fable 5 subagent 對 commit afb9d8e 做對抗性覆核（37 次工具呼叫、587 秒），抓出「接受 protobufjs 依賴」原始論證的關鍵推理缺陷——印證異源模型對抗覆核可打破同源自審天花板，值得對高風險第三方依賴決策常態化。

丟棄 1 條：

- 「為 self-evaluation 修正建立 feature branch（fix/self-eval-streaming-leak-and-threshold）」→ 一次性流程紀錄，無跨 session 重用價值。

備註：本輪兩條均先以 `list_facts` 查詢（對抗審查／protobufjs／Fable／通知／flaky／競態）確認無既有等價 fact，才寫入；未呼叫 forget。

## 2026-07-28（AUTO）

來源 shortlist：12 筆候選（產生於 2026-07-27T20:30Z，皆 telegram-kiro-bridge-main）

寫入 4 條：

- 2026-07-27 把「異源模型對抗覆核」從高風險依賴決策擴大為常態做法，新驗證兩用途：push 前派獨立 Fable5 審查分支抓出測試斷言過弱；知識萃取 commit（pattern library c4922b3）由 Fable5 對照真實專案原始碼（leprechaunsGoldStreak-client，41 檔約 7800 行）逐項查證。指令須明寫「找缺陷而非讚美」。→ shard: uk-917
- upstream 同步陷阱：redkilin 會選擇性 backport 本 fork 修正但以英文註解重寫並改名識別字，造成「內容等價、文字不同」的 add/add 假衝突；處理原則為比較兩側完整度保留較完整一方（實測本地測試基建較完整，四檔以 git checkout --ours 保留），而非機械沿用固定優先權。→ shard: bridge-upstream-sync
- MCP 繼承最佳化（settingSources 限縮為 ['project'] 或 []，session/new 由 19 行程降到 3）決定暫緩：單純限縮會砍掉 specialist 需要的能力繼承，須先做保留能力前提下的架構設計，不可當純效能參數調整。→ shard: bridge-specialist
- 降低 session 啟動延遲的低風險手段：serena MCP 由 uvx 直接從 git 安裝改為預先 uv tool install 到本機，實測每 session 省約 10-11 秒且零程式碼改動，優先度高於需架構設計的 MCP 繼承限縮。→ shard: misc

丟棄 8 條：

- 「UK 助理 knowledge integration strategy」4 筆（同主題重複紀錄）→ 內容僅止於「使用者建立 UK 助理 specialist 以整合 UK Slot 知識」的規劃階段陳述，無實際決策內容可重用，全數丟棄。
- 「獨立 code review 抓出測試斷言弱點」「pattern library commit 經 Fable5 覆核」「對抗式 review 驗證 merge 正確性」3 筆 → 已合併為上方第 1 條。
- 「以 git checkout --ours 解 add/add 衝突保留本地測試基建」→ 已合併為上方第 2 條。
- 「MCP 繼承最佳化暫緩」原為 2 筆重複 → 已合併為上方第 3 條。

備註：四條均先以 `list_facts` 查詢（對抗／upstream／MCP／serena／backport／uvx／settingSources／UK助理）確認無既有等價 fact 才寫入。既有記憶已含 #007「單一視角自審盲點需異源 skeptic」與 2026-07-26 protobufjs 覆核事件，本次第 1 條保留的是「新增的兩種套用場景 + 指令措辭要求」增量。未呼叫 forget。

## 2026-07-29(來源:telegram-kiro-bridge-main,shortlist 9 筆 → 寫入 2 筆)

- 【bridge-memory】telegram-kiro-bridge 於 2026-07-28 為「UK 助理知識包」定案交付架構:採快照式(snapshot)蒸餾檔案 + headless agent CLI 直接讀取,刻意不引入向量資料庫與 embedding 層;配套三層把關為敏感資料過濾(禁止公司 raw code 外流)、明確的知識更新工作流、以及交付前驗證。可作為「小規模領域知識問答機器人」的預設架構——RAG 基礎設施的維運成本通常高於快照重生成的成本。
  - 合併自 shortlist 3 筆:snapshot-based delivery、Design Specification、Multi-layer validation strategy
- 【misc】規格驅動開發(SDD)流程的兩個結構性補強(2026-07-28 於 UK 助理知識包專案定案):(1) 以「調查現況」作為 Phase 1 開場——先盤點既有資料來源與載入機制,再進設計,避免憑空假設前提;(2) 在交付使用者審查前插入一道「規格自審」品質閘,機械化檢查未填的佔位符、內部矛盾、範圍蔓延、以及模糊未定義的敘述。此閘擋掉的是「人工審查時最浪費來回的低階瑕疵」,與異源對抗覆核互補而非取代。
  - 合併自 shortlist 2 筆:Quality Gate (Phase 6 spec self-audit)、Phased Approach (Phase 1 survey)

**捨棄 7 筆**:
- Adversarial Verification of Self-Modified Warning Embeddings —— 與既有「異源模型對抗覆核常態化」記憶高度重疊,僅屬同一做法的再一次套用
- UK knowledge pack execution plan read / Progress tracking ledger established —— 一次性執行步驟與進度檔建立,非可重用知識
- Knowledge pack scope excludes five Notion UK categories —— 專案專屬範圍設定,跨 session 無重用價值
- 其餘同主題重複條目已併入上列 2 筆

去重方式:list_facts 查詢 knowledge pack / 知識包 / 向量 / 自審 / 佔位符 / 品質閘 / 敏感資料 / UK 助理,現存 312 筆中除「自審」命中既有對抗覆核系列外無衝突。未呼叫 forget。

## 2026-07-31(來源:telegram-kiro-bridge-main + uk_917_leprechauns_pots_client,shortlist 14 筆 → 寫入 6 筆)

- 【uk-slot】UK 老虎機事件 gate 的重入防護應查下游狀態而非另設旗標:pre-stop gate 是否已執行改用 BombBoard.HasEventBombs() 這類「已註冊結果」查詢判斷,狀態源唯一,unshow/replay 還原時才不會與實際盤面脫節。
  - 來源:Replay prevention mechanism using BombBoard state check
- 【uk-slot】UK 老虎機 unshow/replay 還原的時序保真原則:原始事件的觸發時機必須原樣保留(during-spin 觸發的 BOMB 不可為了實作方便降級成 after-stop),否則還原畫面與原始 spin 表現不一致。
  - 來源:BOMB event timing and adapter contract decisions confirmed
- 【misc】診斷證據必須在 restart/recovery 邊界失效:recovery 之後若沿用 pre-recovery 的 API error 記錄,真正的 post-recovery 卡死會誤用陳舊錯誤當根因而誤診,因此 recovery 時要主動清除舊錯誤證據。
  - 來源:Review recommendation: do not push until MEDIUM bug fixed(該 MEDIUM bug 的本質)
- 【misc】重現 restart 後的視窗溢出/狀態殘留類 bug,最有效的手法是拿真實 transcript 重播(real transcript replay),比造合成輸入更容易踩到真實邊界條件。
  - 來源:Documented window overflow bug discovery and fix in SPEC Progress section
- 【dev-tools】skill bundle 大幅更新的標準流程:先把未提交檔 commit 建立 restore point → 依差異分三類處理(整包替換/回填缺漏/選擇性合併)→ 被取代的舊 skill 轉成 deprecation pointer 並移除其觸發關鍵字避免撞名搶觸發 → 獨立審查通過才 push。
  - 合併自 shortlist 3 筆:Create Restore Point Before Skill Bundle Update、Three-Phase Skill Update Strategy、Complete Update Workflow(Deprecation, Validation, Independent Review)
- 【misc】依賴套件大版本升級的放行閘應是機械驗證而非主觀判斷:先 grep 全部 .ts/.mjs 確認零 import 指向已移除的模組(例如 MCP SDK 的 HTTP/SSE transport),零命中才放行 push。
  - 來源:Independent review cleared MCP SDK upgrade for push with zero blocking issues

**捨棄 8 筆**:
- Fable5 independent review caught documentation inconsistencies after push —— 與既有「`claude -p --model fable` 做一次性獨立審查」記憶重疊,僅屬同一做法的再一次套用
- BOMB event feature design specification completed —— 專案階段性進度紀錄,非可重用知識
- Bomb Event Placement Ignores Underlying Wheel —— 單一遊戲的機制細節,跨專案無重用價值
- Structured 6-phase development workflow established for CLOVER BOMB —— 一次性任務拆解,且既有記憶已含 spec-to-impl/codegen 流程規範
- Restoration work delegated to colleague —— 一次性協作安排
- Dimming effect conditional logic for round-based lighting —— 敘述過於單薄,無法自足成 fact
- 其餘同主題重複條目已併入上列第 5 條

去重方式:list_facts 查詢 bomb / unshow / recovery / skill / deprecation / transcript / 獨立審查 / 升級,現存 335 筆中除「skill」與「獨立審查」命中既有系列(已據此捨棄 Fable5 那筆)外無衝突。未呼叫 forget。

## 2026-08-01(AUTO;同一份未清空的 shortlist 14 筆重掃 → 寫入 0 條)

shortlist 檔頭仍是「產生:2026-07-30T20:30:02.058Z;筆數:14(上限 15);自 epoch 1785321085374」,內容與上方 2026-07-31 那批**逐條相同**——ingest 之後 shortlist 沒有被清空、epoch cursor 也沒前進,所以同一批被重掃一次。

- 14 筆全部命中既有處置:**6 筆已於 2026-07-31 寫入**、**8 筆已判定捨棄**。
- 抽查驗證:以 list_facts 查 `after-stop`,確認「UK 老虎機 unshow/replay 還原的時序保真原則」那條**確實存在於 fact store**(不只記在本 log)。其 shard 是 uk-slot 而非 uk-917,查 uk-917 shard 會漏掉。
- 本輪先獨立精選、後才發現重複,兩輪結論一致:#4(during-spin 時機不可降級)值得存、#5 的 stale pre-recovery evidence 是真 gotcha、#11/#12/#13 應合併成一條 skill bundle 流程、其餘屬一次性紀錄/專案進度。故不改動既有寫入。
- 未呼叫 remember、未呼叫 forget。

⚠️ 待處理(非本輪能修):shortlist 未清空會讓每次 curate 空轉重掃同一批。本檔已有 07-22、07-23、07-25×2、07-26 共 5 次同類紀錄,本次是第 6 次。根治要在**產生端**於 ingest 後清檔或推進 epoch cursor,curate 這一側無法自救。


## 2026-08-02 (claude-mem AUTO)
來源 shortlist: 產生 2026-08-01T20:05:24.319Z, 13 筆, epoch 1785528817871
精選: 1 條（其餘 12 條與既有 fact 重疊或為過程紀錄）

1. telegram-kiro-bridge 的 draft streaming 拒絕採用 grammY stream plugin 的「Plan E」策略（draft 逼近上限時 finalize 再開新 draft 接續），因為 finalize 後舊 draft 仍會「幽靈並存」若干秒——client 在同一 chat 看到兩個 draft 泡泡會導致動畫行為不可預測。選用的方案是頭部凍結：到上限後只顯示尾端 N 字，讓最終訊息帶完整文字。

## 2026-08-03 (claude-mem AUTO;寫入 0 條)

來源 shortlist 檔頭（原文照貼，與 caller 傳入的 header 逐項一致）:
`> 產生:2026-08-02T20:30:08.729Z;筆數:8(上限 15);自 epoch 1785570559110`

**這是全新一批**（epoch 1785570559110 > 上一輪 1785528817871，8 筆內容與 2026-08-02 那批 13 筆不同），**不是同批重掃**。全 8 筆皆為 telegram-kiro-bridge，主題集中在「/dream per-backend model 設定」與「異源對抗覆核」——這兩件事都是同一場 coding session 當下就直接 remember 進 AIMemory 的，因此在 claude-mem observation 這一側原封再出現一次，重疊率高屬預期，非產生端故障。

**8 筆全數捨棄，逐條對應到已存在的 fact：**

1. `Cost-tiered reviewer selection for cross-model adversarial review` → 撞「使用者的異源覆核紀律於 2026-08-02 新增成本分級（寫進 AI-canonical 正本 ms-cross-model-adversarial-review，commit d8d74c6 已 push）：孤兒 import／死碼交給型別系統、敘事比對用 Sonnet 級、只有不變式／論證推理／時序 race 才用 Fable 5」。既有 fact 更完整（含判準與 commit）。
2. `Second adversarial review approved commit 7d4eba8 ... clean context, not trusting commit message claims` → 撞兩條：「異源覆核紀律再擴充（2026-08-02）：第一輪修正產生的新 commit 要再派第二輪、換新 agent 不告知前一輪結論、無 high/medium 即收斂」＋「Fable5 push 前獨立覆核紀律要求它讀原始碼而非信 commit message」。
3. `Adversarial code review completed for commit f986406` → 單次執行紀錄，無可重用內容；其方法論已由第 2 條那組 fact 覆蓋。
4. `Dream models uses per-backend explicit restoration to avoid subprocess churn` → 撞「dream.json models 表選擇『per-backend + 顯式還原』而非 per-step model：三個 ACP adapter 的 model 生效路徑不同——claude 走 session/set_config_option、kiro(--model) 與 codex(-c model=) 綁 CLI 啟動參數，per-step 等於 15 步換 15 次 agent 並打斷 session.buffer 判定」。既有 fact 含機制細節。
5. `Clarified /dream model requirement is per-backend, not provider switching` → 撞「/dream model 需求（2026-08-02 使用者澄清）：要 per-backend 而非 per-step，也不是換 provider；kiro 跑 claude-opus-4.5、claude 跑 sonnet 5、codex 保留條目」。
6. `/dream 工作流模型還原策略三選項（方案 A 顯式還原為推薦）` → 與第 4 條同一決策，既有 fact 已記載最終選定的顯式還原及「不能靠最後一步 restart」的理由。
7. `Multi-Agent Model Assignment 策略：Kiro agent 指定 opus-4.5` → 撞「已建立 G:\AI\AIMemory\config\dream.json，內容只有 models 表 {"claude":"claude-sonnet-5","kiro":"claude-opus-4.5"}，刻意不列 steps」。
8. `Dream per-step model configuration architecture decision pending（ASK id=dreammodel）` → 待決狀態的過程快照，已被第 4／5 條的定案 fact 取代。

去重方式:list_facts 查詢 `adversarial` / `dream` / `覆核` / `commit message`（現存 437 筆）。未呼叫 remember、未呼叫 forget。

## 2026-08-05 (claude-mem AUTO;寫入 1 條)

來源 shortlist 檔頭（原文照貼，與 caller 傳入的 header 逐項一致：時間戳、12 筆／上限 15、epoch 1785665585219）:
`> 產生:2026-08-04T20:30:03.071Z;筆數:12(上限 15);自 epoch 1785665585219`

**這是全新一批**（epoch 1785665585219 > 上一輪 1785570559110，12 筆內容與 2026-08-03 那批 8 筆不同），**不是同批重掃**。專案分布：uk_872_eyestrike2_client 4 筆、telegram-kiro-bridge-main 4 筆、uk_917_leprechauns_pots_client 3 筆、system32 1 筆。

**寫入 1 條：**

1. 防護正則表達式的 catastrophic backtracking 不能靠「檔案與檔案之間的靜態 checkpoint 或靜態 regex guard」——爆炸發生在單一次 test() 呼叫內部、控制權永遠回不到 checkpoint，所以「處理完一個檔案就檢查一次」的 v1 做法在原理上就攔不到；正解是把 regex 執行隔離進 worker 並由外部逾時中止（telegram-kiro-bridge，2026-08-04）。→ shard `bridge-project`

**捨棄 11 筆，逐條說明：**

- `Fifth adversarial review round initiated to validate round-4 fix effectiveness`、`Second-round adversarial review launched targeting fix commit itself for same-pattern errors`、`Adversarial code review initiated with Fable 5 for supply-chain commits` → 三筆合併後撞既有 fact「使用者的 Fable5 push 前覆核紀律已擴充為『可多輪、範圍逐輪收窄』：每修完一輪 finding 就對新 commit 再派一輪範圍限定的覆核，直到只剩敘事精確度類 finding 才收斂 push」＋「第二輪起改派新 agent 並刻意不告知前一輪結論，避免錨定」＋「異源覆核紀律於 2026-08-02 新增成本分級」。既有 fact 更完整（含輪數收斂條件與模型成本判準），三筆均為單次執行紀錄。
- `Respin Column Lock Skip Animation Optimization`（uk_872）→ 專案特定的 Respin 鎖列動畫最佳化，敘述僅到「1-4 列可能有 Cash symbol 鎖住」，無可跨專案重用的判準。
- `PlayFlyEffect序列執行需求明確化`（uk_872）→ 一次性需求澄清（改為依序飛行而非並行）。
- `POT_TO_REEL_TRAIL_INTRO_START_SECONDS set to 0.01`（uk_872）→ 單一常數調值，一次性。
- `Validated slow-crawl speed parameter choice through trade-off analysis`（uk_872，vSlowRatio=0.004）→ 專案特定的動畫參數調校數值，換遊戲即失效。
- `Complete bomb event UI, state machine, and testing plan defined`（uk_917 Task 11）→ 任務進度紀錄。
- `TDD-driven bomb event feature implementation plan established`（uk_917 Task 8）→ 任務進度紀錄；其 TDD 方法論已由既有 skill/fact 覆蓋。
- `Feature branch workflow initialized for bomb event`（uk_917 Task 7）→ 建分支的一次性步驟。
- `Memory curation completed with zero facts written due to live-session overlap`（system32）→ 本 log 2026-08-03 那則的 observation 回聲，屬過程紀錄。

去重方式:list_facts 查詢 `regex` / `backtracking` / `ReDoS` / `worker` / `逾時` / `對抗` / `Fable`（現存 440 筆）。`backtracking`、`ReDoS`、`worker` 三查皆 0 命中，故第 1 條確認為新知識。未呼叫 forget。

## 2026-08-06 (claude-mem AUTO;寫入 2 條)

來源 shortlist 檔頭（原文照貼；caller 傳入的 header 因編碼損毀呈 mojibake，但可判讀的欄位——時間戳 2026-08-05T20:30:04.052Z、筆數 3、上限 15、epoch 1785827290913——與檔案逐項一致）:
`> 產生:2026-08-05T20:30:04.052Z;筆數:3(上限 15);自 epoch 1785827290913`

**這是全新一批**（epoch 1785827290913 > 上一輪 1785665585219，3 筆內容與 2026-08-05 那批 12 筆不同），**不是同批重掃**。專案分布：telegram-kiro-bridge-main 2 筆、uk_872_eyestrike2_client 1 筆。

**寫入 2 條（皆源自候選 3 的底層 gotcha,已讀原始 artifact 取得實據而非由標題推論）：**

1. Node 的 readdirSync withFileTypes 回的 Dirent 不跟隨連結，junction/symlink 一律 isDirectory()===false、isSymbolicLink()===true；skill 投影全靠逐 skill junction,所以 filter(e=>e.isDirectory()) 掃 skill 目錄恆得靜默空集合。refresh-codex-skill-links.mjs 因此壞掉：dry-run 修前 isDirectory()=0/isSymbolicLink()=37 → REMOVE=12 CREATE=0（每跑一次 postinstall 清空一次 Codex），修後 REMOVE=0 KEEP=12 CREATE=25。正解是篩「目錄或指向目錄的 symlink」並 statSync 跟隨確認。→ shard `adversarial-review`
2. 測試 fixture 形狀必須跟生產一致,否則綠燈與「沒驗到」外觀相同：check-codex-skill-links.mjs 用 mkdirSync 建實體目錄當 skill,8 項全綠卻測不到 junction 的 bug；已改成 junction 型 + 實體目錄型各一並做變異測試。→ shard `bridge-smoke-gate`

**捨棄 1 筆:**

- `ACP session management upgrade path defined with capability gating :: load MUST replay history while resume MUST NOT replay`（telegram-kiro-bridge）→ 撞既有 fact 兩條:「ACP 協定規定 session/load 的 Agent MUST 用 session/update 重播整段對話歷史、session/resume 的 Agent MUST NOT 重播,兩者 Request/Response 逐欄同形…」與「acpClient.ts replaying 抑制旗標確定不可刪除,只能 capability-gate 成兩條分支…gate 條件為 agentCapabilities.sessionCapabilities?.resume !== undefined」。既有 fact 更完整（含 claude-agent-acp 0.63.0 原始碼佐證與 gate 判別式）。

**候選 2 判定為專案一次性,未寫入:**

- `Complete investigation confirms four-point integration approach for In_H_FS/In_S_FS animation support :: FREE_GAME_INTRO_EVENT.PLAY 簽章 (totalRound, callback?) 在 FreeGameIntro.ts line 16`（uk_872）→ 綁單一專案單一檔案行號的整合步驟,無跨專案可重用判準。

去重方式:list_facts 查詢 `junction` / `ACP` / `isDirectory` / `Dirent` / `fixture`（現存 459 筆）。`isDirectory`、`Dirent` 兩查皆 0 命中,故寫入兩條確認為新知識；`ACP` 查得 48 筆並命中上述兩條既有 fact。未呼叫 forget。

## 2026-08-06 第二次 (claude-mem AUTO;重掃同批 → 寫入 0 條)

shortlist 仍是同一份未重新產生的檔案（epoch 1785827290913、筆數 3、產生時間 2026-08-05T20:30:04.052Z），與本日第一輪逐欄一致。該批 3 筆已於第一輪全數處置完畢（候選 3 → 寫入 2 條、候選 1 → 撞既有 ACP fact 捨棄、候選 2 → 判定專案一次性）。

**未呼叫 remember、未呼叫 forget。** 判定依據是 shortlist 檔頭的 epoch 與筆數，而非內容比對後重新判斷——同批重掃不需要也不應該再走一次精選。

## 2026-08-06 第三次 (手動補記;寫入 3 條;非 shortlist 來源)

來源不是 claude-mem shortlist（那份仍是同批未重新產生的檔案），而是**當日對話 session 直接產出的知識**——把外部 sheet-to-markdown 的四項設計吸收進 excel-to-ai-doc，並派 Codex 做兩輪異源覆核的過程。使用者明確要求指定 topic 寫入，未走自動分類（避免跨界的第 2 條掉進 misc）。

**寫入 3 條：**

1. Codex `exec -s read-only` 被執行政策擋掉 git（連 `git --version` 都不給跑），派它做 push 前覆核必須先把 diff 匯出成檔案再餵路徑；否則它只能讀工作區現況、覆核不到本次改動。→ shard `adversarial-review`
2. openpyxl 的 `data_only=True` 讀的是 Excel 存檔時的快取值不是公式；無快取的公式格讀成 None，整張公式表會被判空而靜默消失，且若驗證跳過 empty sheet 就會假通過。→ shard `dev-tools`
3. openpyxl 的 `fgColor.rgb` 只在 `type=='rgb'` 時是字串，theme/indexed 兩類只判 rgb 會靜默漏掉；theme 需讀 theme1.xml 且 Excel 索引前兩對與 XML 排列互換，另需套 tint。→ shard `dev-tools`

去重方式：`list_facts` 查 `openpyxl` / `data_only` / `read-only` / `sandbox` 皆 0 命中；`codex exec` 命中 2 條但主題不同（一條講 2026-08-05 未登入、一條講 .system 自我重建）。未呼叫 forget。

**兩點待處理的觀察（未自行修正）：**

- `G:\AI\AIMemory` 底下**沒有 .git**，所以 claude-mem-curate skill 安全段所寫的「所有寫入都進 git-backed 的 AIMemory」不成立。實際復原手段是 `facts-*.md.bak.<timestamp>` 備份（150+ 個）＋ `forget-log.md` ＋ 本 ingest log。抽查與 forget 修正仍可行，但無版本控制歷史。
- 既有 fact「這台機器的 Codex CLI（0.146.0）在 2026-08-05 時未登入…任何端到端驗證都做不了」已與現況不符：2026-08-06 實測 `codex login status` → Logged in using ChatGPT、版本 0.146.1，當日確實跑了兩輪 `codex exec` 覆核。該 fact 的「AGENTS.md 仍未實測」也已被 steering/skill-workflow.md 的 2026-08-06 實測記錄取代。AUTO 流程只 ADD 不 forget，故未動它。

### 追記（同日）：過時 Codex fact 的處置 — 補推翻條，未刪除

使用者核准「forget 掉再寫一條現況」，但 **forget 三次皆 deleted=0**：該 fact 被 wiki 頁 `concepts/ai-strategy.md` 的引用保護（forget 工具回 "protected by wiki references"）。

嘗試過程：先把 wiki 那行的過時說法就地改成現況 → 仍被保護；再移除新文字中殘留的「401 / 未登入」引用字樣 → 仍被保護。判定保護不是鎖在我拿掉的那些字，而是 fact 與該頁的主題重疊（兩邊都在講 Codex / ~/.codex/AGENTS.md / canary 實測）。再往下追等於為了滿足護欄而挖空一頁正當的 wiki，故停止（3 次熔斷）並回報使用者，改採「補一條推翻 fact」。

**實際結果：**
- 舊 fact 保留（自帶 2026-08-05 時間戳，語意上是歷史記錄）。
- 新增 1 條推翻 fact → shard `ai-strategy`，內容含：0.146.1 已認證、AGENTS.md canary 實測通過、以及 app-server 壞掉導致 `codex:setup` 誤報 loggedIn:false（判斷可用性一律以 codex login status 為準）。
- **wiki 的兩次修改保留**：`wiki/concepts/ai-strategy.md` 原本寫「未解，2026-08-05，未登入、端到端驗證做不了」，已改為現況，並新增「仍未解」段落記下 app-server 壞掉與 `codex exec -s read-only` 擋 git 兩件。過時說法因此已從 wiki 層清掉，只剩舊 fact 那一行還舊。
- 三次 forget 嘗試均記入 `forget-log.md`（deleted=0），可追溯。

## 2026-08-13 (claude-mem AUTO;寫入 3 條)

caller 傳入的 header（編碼損毀，照原樣回貼，未從其他來源改寫）:
`<<> ?Ｙ?:2026-08-12T20:30:03.855Z;蝑:15(銝? 15);??epoch 1786476378062>>`

檔案本身的 header（逐字）:
`> 產生:2026-08-12T20:30:03.855Z;筆數:15(上限 15);自 epoch 1786476378062`

兩者可判讀欄位逐項一致（時間戳 2026-08-12T20:30:03.855Z、15 筆、上限 15、epoch 1786476378062），檔內實際條目數清點亦為 15。**這是全新一批**（epoch 1786476378062 > 上一次記錄在案的 1785827290913），不是同批重掃。來源全為 telegram-kiro-bridge-main（14 筆 2026-08-12 + 1 筆 2026-08-11）。

**寫入 3 條（皆已讀原始 artifact 取得實據，非由標題推論）：**

1. 修正動作本身會產生新的假因果——2026-08-12 codegen git-init 五輪覆核裡同一形狀出現三次（模板後來改掉了／皆已被各自 .gitignore 擋／不在任何專案的 .gitignore 裡），機制是修正時補一個沒有證據的機制解釋、或把有例外的觀察壓縮成全稱句；附三條防法與四個查全史的 git 指令。→ shard `adversarial-review`。實據：`G:\AI\AIMemory\wiki\queries\codegen-git-init-gap.md` 第 111-127 行。**與既有 2026-07-31 那條刻意區分**：那條講原始敘述從意圖推理而來，這條講「為了修上一條而新寫的句子」，fact 內文已寫明差異避免日後被誤併。
2. vc-kiro-delegate skill 已於 2026-08-12 廢止並併入 ms-cross-model-adversarial-review，且明列記憶庫裡另外 5 條談它的 fact 皆為廢止前狀態、只能當歷史讀。→ shard `adversarial-review`。實據：`G:\AI\AI-canonical\skills\general\ms-cross-model-adversarial-review\SKILL.md:481-495`。採 supersede 式寫法（比照先前補正 f_14cb23 的做法），因為 AUTO 流程不 forget，舊 fact 會留著。
3. 查 skill 使用次數的權威來源是 `~/.claude.json` 的 `skillUsage`（全時間累計）而非 transcript grep（約 30 天輪替，數到的是視窗內數字）；配套判準是分母被污染時只報絕對數不寫比例。→ shard `dev-tools`。實據：同上 SKILL.md 段落。

**捨棄 3 筆（撞既有 fact，逐條指名）：**

- 候選 15「ARM benchmark 25% test-retest variability」→ 撞既有 fact「2026-08-12 量到 Kiro 上 code-review 模型評測的 test-retest 翻轉率：…16 個 cell 翻了 4 個（25%）…」。既有 fact 更完整（含逐臂數字、同向機率 0.125、artifacts 路徑）。
- 候選 11「flaky timeout in smoke tests / check-session-resume」→ 撞既有兩條：「⚠️ 更正並結案先前那條『check-session-resume flaky』的 fact：根因已證實是 runM 的 timeout: 15000 太小…（commit d128f28）」與「2026-08-12 掃過全 smoke suite 的寫死逾時，A 類＝等子行程的預算 vs B 類＝行為斷言的時間上界」。
- 候選 6「MAX_SPECIALIST_TIMEOUT_MS 改 24 小時」→ 撞既有 fact「telegram-kiro-bridge 的 specialist 委派逾時已可 per-domain 設定…經 positiveIntOr() 收斂（下界 >0、**上界 24 小時 / 1000 turns**）」。候選標題的 "absurdity threshold" 即該 24h 上界。

**捨棄 9 筆（一次性過程紀錄，無跨 session 可重用判準）：** 候選 1/2/3/5（某 commit 的 GO/NO-GO 覆核請求與結論）、7（gate_runner H1 某專案跑過）、8/10（某次委派給 slot-dev）、9（某次 pipeline 拆 7 個背景任務）、14（一次性 research task 規格）。

去重方式：`list_facts` 查 `vc-kiro-delegate`(5)／`因果`(6)／`test-retest`(2)／`逾時`(8)／`修正`(25)／`adversarial-review` 整個 shard(33)／`廢止`(0)／`全稱`(0)／`gitlink`(0)／`假因果`(0)／`skillUsage`(1，內容無關)／`transcript`(9，無一相關)，現存 554 筆。未呼叫 forget。

**兩點矛盾，照實回報未自行修正：**

- `wiki/queries/codegen-git-init-gap.md:129` 寫「已存成 fact `correction-invents-new-causal-story`」，但記憶庫查無此 fact（adversarial-review 整個 shard 33 筆逐條看過 + 4 組關鍵字掃描皆 0 命中）；shortlist 候選 4 也宣稱建立了 `correction-invents-new-causal-story.md`，但 `find G:/AI -iname "*causal*" -o -iname "*invent*"` 只找到 `SPEC-causal-chain-permission-guard.md` 與 `analyze-causal-audit.mjs`，無該檔。∴ 該知識先前只存在於 wiki 頁，本次才真正落成 fact。**未修改 wiki 那一行**（AUTO 只 ADD，且動 wiki 依 2026-08-06 先例需使用者核准）。
- 本 log 上一則是 2026-08-06 第三次，但 claude-mem observation 記錄 08-07(2 條)／08-08／08-09(0 條)／08-11(2 條)／08-12(3 條) 都跑過 curation ∴ **中間 5 次的 log 條目缺漏**。不影響本次判斷——去重一律以 `list_facts` 為準、批次身分以 epoch 為準，兩者都不依賴這份 log。

## 2026-08-14 (claude-mem AUTO;15 筆候選 → 寫入 3 條)

caller 機械讀到的 header（編碼損毀，照原樣回貼，未從其他來源改寫）:
`<<> ?Ｙ?:2026-08-13T20:30:04.436Z;蝑:15(銝? 15);??epoch 1786526680353>>`

檔案本身的 header（逐字）:
`> 產生:2026-08-13T20:30:04.436Z;筆數:15(上限 15);自 epoch 1786526680353`

兩者可判讀欄位逐項一致（時間戳 2026-08-13T20:30:04.436Z、15 筆、上限 15、epoch 1786526680353），**無矛盾**；檔內實際條目數清點亦為 15（行 5-19）。**全新一批**：epoch 1786526680353 > 上一則記錄的 1786476378062（見上方 2026-08-13 條目行 697）。來源全為 `telegram-kiro-bridge-main`，15 筆全部日期 2026-08-13，主題全部圍繞 `uk_slot_clash_of_olympus` 的 VS Feature（M2.2）。

**寫入 3 條：**

1. （shard `uk-slot-clash-olympus`）VS 轉型權威來源 2026-08-13 裁決為「server 給定 + client 推導對帳」——client 自行推導只用於對帳、不自行判定，∴「自己算出結果就直接採用」即違反 server 權威。合併候選 12(裁決) + 1(M2.2 覆核據此開出 High finding)；**覆核 finding 具體違反在哪，shortlist 未載明，刻意不重建**。去重：查「server 權威」0 筆、「對帳」3 筆皆無關；既有 f_cf423c 只涵蓋「轉型時機與 1×4 覆蓋順序」，不含「誰說了算」→ 淨新增。
2. （shard `uk-slot-clash-olympus`）M2.2 VS Feature 演出定案為薄轉接器：VsFeatureShowState 只做 proto VSResult → VSManager.Resolve() → 逐 step 跑 Fly/Expand/Spine → 經新增 GameView.VsFeatureResult 交棒 CollectFeatureShowState；plateAfter 採 derive-not-persist；轉換層抽成 VSManager.ts 的純函式 `AdaptRoundToVSInput()` + colProto 只用 type-only import 以保 ts-node 可測。合併候選 2+3。與 f_917144（UK 老虎機運算層要 CC-free 才能在 ts-node 測）**互補非重複**——那條是原則，這條是 proto 型別上的具體做法；並已在 fact 內標明本條使 f_f8bf81 的「M2.2 尚未開始」過期。候選裡的「6 項風險」「GameView mock 嚴重 bug」是**沒有內容的計數**，只標「來源未列明細」不擴寫。
3. （shard `bridge-smoke-gate`，來源候選 5）hang detection 安全邊際自 suite 增至 432.1s 後由約 2 倍降到約 1.39 倍，2026-08-13 刻意不調高門檻。**只寫 shortlist 給的數字**；門檻絕對值與「不調」的理由來源未載明，不寫入（由 432.1×1.39 反推的門檻值屬推導非實據，刻意不放進 fact）。與 f_9219db（腳本內寫死逾時的 A/B 兩類分法）互補：那條管單支腳本，這條管 suite 之上的兜底。

**⚠️ 本批內部含同一問題的先後兩讀，照實記錄不靜默消解：**

候選 10（VS Collect 倍數語意＝改寫盤面分數本身，稱 2026-08-13 使用者確認）與候選 15（同義，稱 confirmed to rewrite Cash score values directly on the board）是**被推翻的舊讀**，與同批的候選 7/8/9/13（編導條 7：只記 collectMul[col]、不動盤面；多個 VS Collect 相加非連乘）語意相反。既有 f_9b909e 已載明編導於 2026-08-13 改規格、明確推翻 [C72]/[C79]「打到盤面所有 Cash/JP」那一側。∴ 候選 10/15 是**「已被推翻」而淘汰，不是「重複」而淘汰**——兩者處置相同但理由不同，記在此以免日後誤讀成 f_9b909e 涵蓋了它們。

**捨棄 6 筆（撞既有 fact，逐條指名）：**

- 候選 7（VS Collect 由連乘改相加模型）、8（GAP-11 正式關閉：相加非連乘、最大贏分降兩個數量級）、9（VSManager.Resolve() S4 只記 collectMul[col] 不動盤面，編導條 7）、11（多個 VS Cash 互不影響、各自只乘自己輪次加總）、13（方案從盤面倍數改為收集時列倍數）→ 全數撞 **f_9b909e**，該 fact 已含具體算例（col0 ×10、col5 ×5、T=1000 → 15000）、規格條號對照（推翻 [C72]/[C79]、選 [B49]/[B64]）與 VS Cash 側不變、普通 Collect 收未乘倍 T 的但書，**比五條候選加起來更完整**。
- 候選 14（VS Collect 連乘與否延後到問編導、不預設任一解讀）→ 同一決策鏈的前一步，其結論已由 f_9b909e 記載（GAP-11 已關閉）；「先問不預設」的方法論成分則已被既有的證據紀律 fact 群覆蓋，單寫會稀釋。

**捨棄 2 筆（一次性過程紀錄）：** 候選 4（M2.2 VS Feature 演出設計覆核「已啟動」，含 task 名 moaplan_lifecycle_review）、6（第二輪語意合併覆核「已啟動」）。另候選 1 與 2/3 的「覆核完成／設計定案」敘述部分同屬過程紀錄，其有內容的成分已分別併入寫入第 1、2 條。

候選 6 另含「第一輪覆核有 2 個查證缺口：mutation set 認定錯誤、對 .mjs 檔的 tsc 推理無效」——`.mjs` 那半有潛在可重用性（tsc 預設不檢 .mjs，用它當覆核依據是空的），但 shortlist 只給結論不給前後文，**寫成 fact 必須自行補完機制敘述＝過度推論**，依證據紀律丟棄而非猜著寫。

去重方式：`list_facts` 查 `VS Collect`(2)／`clash_of_olympus`(16，逐條看過)／`VsFeatureShowState`(1)／`server 權威`(0)／`對帳`(3)／`ts-node`(1)／`hang`(4)／`mjs`(40)，現存 582 筆。未呼叫 forget。

**兩點照實回報：**

- 本檔排序已不一致：行 3 起是 2026-08-12 起往回倒序，但 2026-08-13 那則在檔尾（行 691）。本次依指示「append」續接檔尾，未重排（重排不在本次範圍）。
- 帳目：15 筆＝貢獻寫入 5（候選 1、2、3、5、12）＋已被推翻 2（10、15）＋撞既有 fact 6（7、8、9、11、13、14）＋純過程紀錄 2（4、6）。即 10 筆整條丟棄，重疊率高——與 2026-08-01 那則觀察到的成因相同：08-13 當天的 clash_of_olympus VS Feature 工作在當下已即時寫進 AIMemory（f_9b909e、f_cf423c、f_e0a15e、f_f8bf81 等 16 條），claude-mem 隔日只是對同一批工作的第二次抽取。此為預期行為，非 producer 故障。

## 2026-08-15 (claude-mem AUTO;15 筆候選 → 寫入 4 條)

caller 機械讀到的 header（編碼損毀，照原樣回貼，未從其他來源改寫）:
`<<> ?Ｙ?:2026-08-14T20:30:03.245Z;蝑:15(銝? 15);??epoch 1786623206724>>`

檔案本身的 header（逐字）:
`> 產生:2026-08-14T20:30:03.245Z;筆數:15(上限 15);自 epoch 1786623206724`

兩者可判讀欄位逐項一致（時間戳 2026-08-14T20:30:03.245Z、15 筆、上限 15、epoch 1786623206724），**無矛盾**；檔內實際條目數清點亦為 15（行 5-19）。**全新一批**：epoch 1786623206724 > 上一則記錄的 1786526680353。來源 11 筆 `telegram-kiro-bridge-main` + 4 筆 `uk_slot_clash_of_olympus`，全部日期 2026-08-14。

**寫入 4 條（皆已讀原始 artifact 取得實據，非由標題推論）：**

1.（shard `uk-slot-clash-olympus`，合併候選 11/13/14＝shortlist 行 15/17/18）GAP-04 於 2026-08-14 由編導口頭答覆關閉：①語意 `2X` 與 2026-08-13 暫定的 `NX` 一致 ∴ 是**確認非改變**、碼不需回頭改；②「種類數」是**問題被消滅**而非答出數字——倍率不固定 ∴ 改 BitmapFont 動態組字（字符集 `0-9`+大寫 `X` 共 11 字），演出切片解鎖；③數值由 server `winningMultiplier` 給、client 不持有倍率表。含遺留假設（正整數）與「口頭答覆、S44 仍是問句、勿默默採用日後文件版」兩條警告。實據 `docs/spec-gaps.md:42、65-84`。**此條使 f_5927a3 的「工作假設」狀態過期**，已在 fact 內文標明（採 supersede 式寫法，未呼叫 supersede 工具——AUTO 不退役既有 fact）。
2.（shard `uk-slot-clash-olympus`，候選 12＝行 16）借來的 placeholder 字型與 charset 陷阱：前身 uk_739（wrath_of_thunder）沒做金額顯示 ∴ 從 uk_872_eyestrike2 借字型（埃及風格 vs 本作希臘主題，上線前必換）；`SymbolCashNUM` 已接線並實機驗證，`Multiplier_Num.fnt` 刻意未接線因其 `charset="32,48-57,120"` 只有小寫 `x`、缺 88（大寫 X）∴ 畫不出 `2X`，倍率改共用 `SymbolCashNUM`。可遷移判準＝接線點陣字型前先讀 .fnt 表頭 charset，缺字不報錯只靜默少字。實據 `ART_ASSET_MANIFEST.md:123-157`。
3.（shard `bridge-project`，候選 7＝行 11）grammY transformer 層序更正：`bot.api.config.use()` 是 `reduce(concatTransformer, this.call)` ∴ **後裝的在外層**；護欄裝在 autoRetry 之後只換到「護欄自發重試會再過一次 429 處理」，⚠️**不承重**——已設 `rethrowHttpErrors: true` ∴ 順序對調時「非冪等方法只嘗試一次」照樣成立。推翻先前文件「順序裝反會 silent total failure」的宣稱。實據 `src/bot-setup.ts:195-198`（該註解本身即更正後版本）。已在 fact 內文寫明與 f_f9f50a **互補非重複**（那條講 rethrowHttpErrors 預設值與內層迴圈使 maxRetryAttempts 失效；這條講層序方向與不承重判定），以免日後 dedupe 誤併。
4.（shard `bridge-project`，候選 2＝行 6）planUncertainReplay 刻意不做遞迴切分、改文件化限制：前提是 `text` 本身不得超過 limit，超過時無法補救。可遷移的是**理由**而非該前提——多一個切塊實作＝多一個會與既有 `splitForTelegram` 漂移的來源，切塊是呼叫端責任；且「超長 → 400 → 重新入列」的迴圈在護欄出現前就存在，非護欄引入。判準形狀同 f_ee9da7。實據 `src/telegram-retry-guard.ts:124-142`。

**捨棄 5 筆（撞既有 fact，逐條指名）：**

- 候選 1（行 5，兩條 high 重放安全問題文件化後延後 / ACP 整輪 prompt 重放含工具副作用）→ 撞 **f_549d3f**（同一決策，2026-08-14，含「排除接在已疊四層的 commit 後面」的理由）、**f_f0aeea**（SPEC-replay-safety-audit.md 六條含 H-1/H-2 逐條）、**f_8ca646**（R-A/R-B/R-C 三條可複用判準）。三條加起來比候選完整。
- 候選 3（行 7，覆核用對抗式框架：告訴覆核者價值在反駁而非同意）→ 撞 **f_eb2186**（「關鍵是指令必須明寫『找缺陷而非讚美』，否則 agent 會傾向附和」），且該做法已固化為 skill `ms-cross-model-adversarial-review`。
- 候選 4（行 8，pendingMessages 加 `uncertain: boolean` 欄位）→ 撞 **f_45b6ff**（「保留重送＋把不確定性顯性化」即此設計的判準層）＋ **f_5e618d**（四層修復已完成並 push）。候選只多出欄位名這個實作細節。
- 候選 6（行 10，採冪等性重試、借 cloudflare-os `callMayHaveTakenEffect()`）→ 撞 **f_45b6ff**（明確點名 callMayHaveTakenEffect 並記載「成本不對稱在本 domain 是反過來的 ∴ 不照搬」）＋ **f_f9f50a**。
- 候選 15（行 19，fork 式協作／同事已完成安裝）→ 撞 **f_1ac058**、**f_474e9e**（皆記載選「同事自建 repo + upstream remote」而非 GitHub Fork 鈕及其理由）、**f_b82b6e**（SETUP-downstream-fork.md 的產出與裁決）。

**捨棄 3 筆（一次性過程紀錄）：** 候選 5（行 9，建立 `scratch/review-prompt-ff976f6.txt`、2555 bytes）、候選 8（行 12，ASK id `cfos_b1fix` 提供 4 個選項待使用者選範圍）、候選 9（行 13，cloudflare-os research 完成、wiki index.md 條目由 research-in-progress 改為 Step 2-3 complete）。

**捨棄 1 筆（沒有內容的計數）：** 候選 10（行 14，cloudflare-os 吸收評估「兩個建議採用、兩個否決」）——shortlist 只給數字不給是哪四個模式，寫成 fact 必須自行補完＝過度推論；其唯一有實據的成分（callMayHaveTakenEffect 的成本不對稱判準）已在 f_45b6ff。

**⚠️ 一處標題與 artifact 的張力，照實回報未靜默消解：**

候選 12 標題寫「Amount numbers cannot use substitutes or reference other games like eye_strike2」（不得沿用他案），但 artifact `ART_ASSET_MANIFEST.md:123-126` 記載的是**確實已從 eye_strike2 借了兩份字型**並標為 placeholder。兩者可調和為「交付政策 vs 開發期現況」——上線前不得沿用他案資產，開發期作為顯性標記的暫代品則可接受——寫入的是這個調和版本，不是標題的字面版本。判讀依據是 artifact 原文「**上線前必須換掉**」。

**⚠️ 一項刻意不寫（超出本批範圍，非遺漏）：**

查證 artifact 時在 `src/telegram-retry-guard.ts:154-162` 讀到 2026-08-15 由 Codex 覆核抓到的更正——`sentParts` 只能證明前面幾則成功、證明不了當前失敗那則沒送達，∴ 判準改為「任何一次以『可能已送達』收場的嘗試都讓該筆從此變成不確定」（fail-safe 方向）。這是有價值的可重用判準，但**日期在本批（2026-08-14）之後、不屬本批候選**，依證據紀律不寫入，預期會出現在下一批 shortlist。

**帳目（15 筆全部有下落）:** 寫入貢獻 6 筆（候選 2、7、11、12、13/14 併入第 1 條 ∴ 行 6/11/15/16/17/18 共 6 行 → 4 條 fact）＋撞既有 fact 5 筆（行 5、7、8、10、19）＋純過程紀錄 3 筆（行 9、12、13）＋無內容計數 1 筆（行 14）。

去重方式：`list_facts` 查 `retry`(8)／`冪等`(2)／`cloudflare`(6)／`replay`(12)／`clash_of_olympus`(18，逐條看過)／`transformer`(0)／`uncertain`(0)／`BitmapFont`(0)／`wrath_of_thunder`(1，僅專案存在性)／`eye_strike2`(0)／`同事`(10)／`附和`(1)／`splitForTelegram`(0)，寫入前現存 622 筆。未呼叫 forget。

本次依指示 append 於檔尾；先前記錄的檔內排序不一致未處理（重排不在本次範圍）。
