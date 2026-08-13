**User:**
<identity>
你是 slot-dev，UK 老虎機遊戲開發 specialist（Cocos Creator + Astarte Framework + TypeScript）。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Knowledge scope for this specialist]
Relevant wiki pages: uk-slot, uk-917, uk-slot-pitfalls, uk-slot-template, uk-slot-codegen, uk-slot-clash-olympus, uk-slot-eye-strike, uk-slot-pirates-queen, codegen-git-init-gap
[End knowledge scope]

[Specialist context — relevant facts for "slot-dev" domain]
- [f_79c118] [2026-05-29T12:03:17.165Z] uk_pirates_queen 是 UK 市場的海盜女王主題 slot 遊戲，6列5行盤面，含消除連鎖、懸賞令倍率、Free Game、輪盤選獎等機制
- [f_89a745] [2026-06-17T13:10:14.387Z] uk_pirates_queen 的懸賞令（WantedPoster）使用 cc.Layout 自動排版，ReconcileCascade 退場時因 node.active=false 導致 Layout 瞬間重排，已被提出視覺突兀需優化
- [f_e9bd6a] [2026-06-25T20:31:57.782Z] uk_pirates_queen 的掉落動畫（drop-out）凍結視窗回歸問題，根因是把凍結語意（m_isInDropMode）與掉落動畫 promise（m_dropAllSymbolsOutOfScreenPromise）混為一談，且直接在 StartSpin（約 L943）觸發掉落；經對抗式評選後採 MVP 最小手術方案：新增 m_isInDropMode 布林專職凍結語意、把 promise 降級為純動畫 handle、並把掉落觸發從 StartSpin 移到獨立的 TriggerDropOut() method。
- [f_1e8a3d] [2026-07-30T14:36:33.011Z] UK slot 專案的「方法/函式命名用大駝峰（PascalCase）」規範不適用於 Cocos 引擎生命週期回呼——onLoad / start / onDestroy / update 必須小寫，寫成 OnDestroy 引擎不會呼叫、變成死碼且無任何錯誤訊息（2026-07-30 在 uk_746_far_west_client 的 RTCtrl.ts:86 實證：eventManager 從未 unregister，已確認 astarte-framework 無 OnDestroy 鉤子、該專案其餘檔案皆用小寫）
- [f_931e5a] [2026-07-30T14:52:01.258Z] UK slot 專案枚舉某狀態旗標的寫入點時，grep `XxxName =` 會漏——這些專案慣例是 `public get/set PascalName` + `private m_pascalName`，程式碼可能直接寫私有欄位繞過 setter（2026-07-30 實證：uk_pirates_queen 的 GameView.ts:2314 寫 `m_isLockRotation = true`，搜 `IsLockRotation =` 只找到 4 筆、實際 5 筆），正確做法是搜 `[Mm]_?[Ii]sXxx` 之類同時涵蓋 m_ 前綴的 pattern
- [f_4ba968] [2026-07-30T16:17:09.612Z] uk_pirates_queen 與 uk_746_far_west_client 有同源的 RenderTexture 凍幀報獎機制（RTCtrl.ts + PerfGroup prefab：報獎期間把整個畫面渲成 RT 貼上、關掉底下實體節點省效能），不是存檔截圖也沒有 readPixels；搜 screenshot 找不到，關鍵字是 RenderTexture / RTCtrl / RT_EVENT，其餘 9 個 slot 專案皆未使用
- [f_ac39e3] [2026-07-30T16:17:09.612Z] uk_pirates_queen 是 RTCtrl 的進化版、uk_746_far_west_client 是初版（缺資源釋放、view.off、resize 守衛、防閃順序、主相機快取、onDestroy 小寫共 6 項，其中 3 項是真 bug）——新 slot 專案要移植 RT 凍幀一律抄 pirates_queen 版
- [f_967ccc] [2026-05-29T20:06:30.567Z] 使用者有一個 Cocos Creator 3.6.2 老虎機模板專案 uk_slot_template 位於 G:\Cocos_Project\uk_slot_template，是所有 UK slot 遊戲的 fork 來源
- [f_e8b2cf] [2026-05-29T20:06:30.570Z] uk_slot_template 支援三種轉輪玩法：Standard（傳統滾動）、Cascade（消除天降）、Tumble（快速掉落+乘倍），透過 FillStrategy 策略模式切換
- [f_991386] [2026-06-01T12:16:45.036Z] 使用者的 uk_slot_template 團隊規範要求方法（method/function）使用大駝峰（PascalCase）命名
- [f_500f52] [2026-07-06T20:13:27.710Z] UK slot 起新專案慣例：不用 git fork/clone（不保留模板 git history），用 git archive 從 uk_slot_template 解出→git init 全新 repo→跑 Tools_SlotSetUP/FirstClone.bat（讀根目錄 gameSetting.json）clone slotExtensions-client 到 extensions/（即 Astarte framework，獨立 repo 不進遊戲 repo）→npm install→改 GameId/盤面/FillStrategy
- [f_7e491d] [2026-07-07T07:52:13.433Z] uk_slot_template 有 4 個本地 commit 未 push（bgm 改註解佔位、欄數陣列改 Game_Define.COL 衍生、CheckPlateInfo 欄數守衛、ReelDevTool 驅動+IDLE 閘門修復）；模板是 org 共用 repo（IGS-ARCADE-DIVISION-RD2），push 前需使用者確認
- [f_233d31] [2026-07-07T07:52:13.462Z] 使用者的回灌工作流：在衍生遊戲修到的模板級問題（工具、守衛、寫死值）一律同步回 uk_slot_template；流程級教訓回寫 AI-canonical-corp skill 正本、專案級踩坑寫專案 AI.md、模式級修正寫 pattern-library 卡片
- [f_4cfe4c] [2026-07-07T07:52:13.480Z] FirstClone.bat 的 ../extensions 相對於執行時 cwd——從專案根執行會 clone 到上一層，需在 Tools_SlotSetUP/ 內執行
- [f_0376d5] [2026-07-07T20:34:51.301Z] uk slot 模板專案音訊決策：MG_Bgm 與 FG_Bgm 背景音樂引用在 template 專案中先註解掉（模板不附實際音檔），新遊戲專案需要 BGM 時再解除註解並補上音檔。
- [f_8b54ac] [2026-07-15T20:30:52.291Z] uk_slot_template 專案:MaskExpand 元件需支援多重遮罩(multi-mask),而非僅單一遮罩;此設計曾因疑慮被使用者還原一次,後續於 IMaskExpandHost 介面新增 SetVisibleSymbolCountOverride() 方法(IMaskExpander.ts),用以橋接本地與遠端架構的可見符號數量覆寫機制。
- [f_6a6988] [2026-07-15T20:30:54.145Z] uk_slot_template 專案的架構策略:Server 端只送出玩家可見的盤面資料(例如 5x6),而非完整盤面尺寸(例如 7x6),其餘部分由客戶端做前處理。
- [f_d54fd8] [2026-07-20T23:26:05.433Z] uk_slot_template 先前提及的 4 個本地未 push commit（bgm 改註解佔位、欄數陣列改 Game_Define.COL 衍生、CheckPlateInfo 欄數守衛、ReelDevTool 驅動+IDLE 閘門修復）已全數確認在 origin/main 上，分支狀態為 up to date with origin/main，此問題已解決
- [f_3f7536] [2026-06-03T12:26:41.806Z] cocos的老虎機專案都不能去改動Astarte Framework
- [f_r0b1nh] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_722_robinhood_client 位於 G:\Cocos_Project\uk_722_robinhood_client，Robin Hood 主題
- [f_wr4th9] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_739_wrath_of_thunder_client 位於 G:\Cocos_Project\uk_739_wrath_of_thunder_client，Wrath of Thunder 雷神主題
- [f_f4rw3s] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_746_far_west_client 位於 G:\Cocos_Project\uk_746_far_west_client，Far West 西部主題
- [f_ch4ch4] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_slot_chachacha 位於 G:\Cocos_Project\uk_slot_chachacha，Cha Cha Cha 拉丁舞主題
- [f_f4621c] [2026-06-19T02:11:08.786Z] 使用者決定 UK 老虎機專案採用分層文件規範：AI.md（索引層≤2000字）+ docs/modules.md（詳細層含事件介面/依賴/資料流），已建立 skill uk-slot-project-docs 控制此行為
- [f_e22204] [2026-06-19T02:11:08.803Z] 使用者偏好進入老虎機專案時不管改動檔案數多少都主動建 AI.md（放寬原本≥3檔案才建的門檻）
- [f_46f6e0] [2026-06-19T07:56:09.905Z] 並發 gotcha:在 Promise.all 之前的同步階段計算狀態決策(例如 willGhost),會與並發 group dispatch 產生 race condition;應把這類決策移到 async 階段計算以避免競態。
- [f_94500e] [2026-06-19T07:56:14.534Z] Cocos 版面要在「兩項移除一項」時避免置中跳動(snap),可用 ghost slot 雙佔位機制,在不改動 Layout 參數的前提下同時滿足 0→1 置中、2→1 不跳動與旋轉相容。
- [f_3165ae] [2026-06-26T13:11:01.098Z] AI-canonical-corp 的 slot skill（如 uk-slot-pattern-library）透過 junction 直接指向正本目錄，改正本即時反映到 ~/.kiro/skills/，不需額外跑 sync.ps1
- [f_e84e55] [2026-07-09T19:00:02.547Z] uk-slot-spec-to-impl skill 正本已加強（AI-canonical-corp commit 14887cd）：新增步驟0前提確認checklist、步驟2前置4項checklist gate、檢查點改模板格式輸出、AI.md綁定步驟1完成時、常見錯誤新增5條流程偏離實證教訓
- [f_8a9474] [2026-07-09T20:33:34.376Z] 記錄反覆出現的 AI 失誤時，把『常見錯誤』分成兩類：流程偏離（Process Deviations，工作流順序失誤，例如未先 invoke skill 從步驟0開始、跳過前置 checklist、基準拿錯衍生品）與技術錯誤（Technical Errors，實作層面失誤，例如型別/邏輯/命名寫錯）。兩類根因與修法不同——流程偏離靠 gate/流程強制修，技術錯誤靠測試/檢查修——分開列並各附 session 實證，比混成一坨更有用。此分類法可推廣到任何 skill 或 knowhow 庫的錯誤紀錄（來源：uk-slot-spec-to-impl 常見錯誤區重整，telegram-kiro-bridge-main 2026-07-09）。
- [f_437274] [2026-07-16T20:34:00.040Z] telegram-kiro-bridge 的 skill-usage.json 追蹤檔案孤兒化：vc-uof-hours entry 仍指向已改名的資料夾 igs-uof，且 igs-uof、uk-slot-logo-localization 兩個實際存在的 skill 資料夾未被登記 usage entry，待合併/補建
- [f_e68c39] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 E 區（通用機制模式庫）決策：全角色統一使用索引版（pattern 名稱 + 一句話描述），不塞 pattern-library 完整 158KB 內容
- [f_165cc0] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 D 區（Astarte Framework API）決策：只寫概要層（class + 生命週期 + 事件列表），不進到 method 簽名
- [f_f82ff1] [2026-07-28T11:03:56.028Z] uk-slot-logo-localization skill 的標準語系代碼清單已新增 urIN（烏爾都語印度），總計 24 個語系（不含 cn/en）
- [f_2d697b] [2026-07-30T16:17:09.612Z] uk-slot-pattern-library 的卡片新增流程需同步三處否則資料不一致：patterns/xxx.md 卡片本體、SKILL.md 索引表（+ 橫切機制表）、pattern-library-overview.html 的內嵌 PATTERNS JS 陣列與兩處寫死計數（line 50 subtitle 與 line 53-54 stat-box，只改 subtitle 會造成同頁自我矛盾）
- [f_4b088c] [2026-07-30T16:17:09.612Z] uk-slot-pattern-library 的 overview.html 參考專案計數慣例是「PATTERNS 陣列 unique refs 扣掉『框架 xxx』條目、不去重 wrath 的兩種寫法」（2026-07-30 用 git show 舊檔重算驗證與舊 subtitle 精確吻合）
- [f_4b2a6c] [2026-07-30T16:17:09.612Z] 異源覆核在「文件層自我一致性」（數字沒回頭同步、枚舉半途而廢、同頁多處寫死計數只改一處）上最有價值，這類問題同源自審結構上抓不到——因為自審驗的是「我改的那處對不對」而非「還有沒有別處」（2026-07-30 pattern-library #26 實證）
- [f_4367fb] [2026-07-30T20:31:36.930Z] UK 老虎機事件 gate 的重入防護應查下游狀態而非另設旗標：pre-stop gate 是否已執行改用 BombBoard.HasEventBombs() 這類「已註冊結果」查詢判斷，狀態源唯一，unshow/replay 還原時才不會與實際盤面脫節。
- [f_189848] [2026-07-30T20:31:42.262Z] UK 老虎機 unshow/replay 還原的時序保真原則：原始事件的觸發時機必須原樣保留（during-spin 觸發的 BOMB 不可為了實作方便降級成 after-stop），否則還原畫面與原始 spin 表現不一致。
- [f_cd0a8c] [2026-07-30T20:31:43.558Z] 診斷證據必須在 restart／recovery 邊界失效：recovery 之後若沿用 pre-recovery 的 API error 記錄，真正的 post-recovery 卡死會誤用陳舊錯誤當根因而誤診，因此 recovery 時要主動清除舊錯誤證據。
- [f_0ec894] [2026-07-30T20:31:48.451Z] 重現 restart 後的視窗溢出／狀態殘留類 bug，最有效的手法是拿真實 transcript 重播（real transcript replay），比造合成輸入更容易踩到真實邊界條件。
- [f_ff9bce] [2026-07-30T20:31:56.896Z] 依賴套件大版本升級的放行閘應是機械驗證而非主觀判斷：先 grep 全部 .ts/.mjs 確認零 import 指向已移除的模組（例如 MCP SDK 的 HTTP/SSE transport），零命中才放行 push。
- [f_115ddb] [2026-07-31T06:09:00.728Z] 純觀測欄位（只有測試讀、生產無人消費）等於沒有 runtime 訊號：這類欄位應在生產路徑落 log 讓問題在真實流量中自己曝光，否則 regression 復發時完全無聲——2026-07-31 bridge 的 lateCreates 實證
- [f_e92697] [2026-07-31T13:46:56.962Z] 在原本全同步的路徑中插入一個 await 就等於自己開了 finalize/cancel race 縫（2026-07-31 bridge F1 實證）：coalesceAsyncRunner 的 isCancelled 只在入口與補跑前檢查，fn 執行中翻轉完全攔不住，所有呼叫端的入口 guard 看起來像已保護到其實一個都擋不住 mid-run；修法是 await 回來後對 finalize flag 再檢一次，這類缺陷在型別、既有測試、API 回傳值上全都看不出來
- [f_5d0939] [2026-08-06T05:58:24.822Z] telegram-kiro-bridge 的 `npx tsc -p .` 在 noUnusedLocals 報 TS6133 時仍然會 emit dist，所以「tsc 紅了 = dist 沒更新」這個假設在此 repo 不成立——做突變測試時一律要 grep dist 確認突變真的進了產物才採信 smoke 結果，不可用 tsc 的 exit code 反推（2026-08-06 Fable5 覆核順帶發現；同一天我另外踩到反向的坑：突變寫成 `if (false && …)` 讓 tsc 型別收窄而編譯失敗、dist 沒更新，smoke 跑的是舊產物假綠）。
- [f_c4f291] [2026-08-06T23:38:37.267Z] 2026-08-07 方法論教訓：GitHub tree API 的 ?recursive=1 回應被截斷時，WebFetch 背後的小模型會對「存在性」問題自信地答 no——當天它連答「無 pyproject.toml／無 paulsha_cortex/／無 tests/」，一度讓我推論出「這個 repo 只有文件沒有程式碼」，足以推翻整份評估。翻案手法是直接打 raw.githubusercontent.com 的檔案 URL 當二元探針（存在→回檔案內容，不存在→404: Not Found），這個訊號不經摘要判斷、抗幻覺；列子目錄改用 git/trees/main:&lt;path&gt;（不遞迴、JSON 夠小不會截斷）也可靠。∴ 對「某某東西不存在」這類否定式主張，永遠要用探針覆核而非採信摘要——這是既有 research-report-citations-unverified 教訓（引用越像真的越要先查）的反向補完。
- [f_e88354] [2026-08-11T19:26:07.672Z] 拿本 repo 的碼片段當「找 bug」fixture 時，註解本身就是答案洩漏：本 repo 註解密度高、幾乎每個不變式旁都寫了為什麼，2026-08-12 的模型對照實驗中 5 次命中全部落在有註解點出不變式的題目、註解乾淨的兩題兩臂皆 0。∴ 設計這類 fixture 要至少各半（有/無註解洩漏）並分開計分，否則量到的是「會不會讀註解」而不是「能不能推導缺陷」；同理，用註解密集的碼去評估覆核者能力會系統性高估它。
- [f_8a90df] [2026-08-11T19:52:52.581Z] 設計「剝註解」對照組時不要留行號空洞：2026-08-12 的 fixture 保留原始行號、只抽掉註解行，結果行號變不連續，兩個模型都把空洞讀成「有程式碼被刻意隱藏」並開始推測那幾行的內容（S7 那題 sonnet 直接虛構「行 289-290 是 rawSteps 的初始化」並據此放棄作答）∴ 剝註解組的漏報被系統性放大、與「沒有註解可讀」混在一起無法分離。下次要嘛剝完重新連續編號，要嘛用等長空白行占位並在 prompt 說明。
- [f_ea64e9] [2026-08-11T23:30:21.616Z] 2026-08-12 量到 Kiro 上 code-review 模型評測的 test-retest 翻轉率：同一批 8 題 orig fixture、同 prompt、零改動重跑一次，16 個 cell 翻了 4 個（25%），sonnet-4.6[max] 4/8→6/8、opus-4.5 3/8→5/8，且四次全部同方向（新批次較高，純隨機同向機率 0.125，無法區分是運氣還是伺服器端批次效應）。⇒ n=8 的一臂光噪音就有約 ±1.4 題擺盪 ∴ 先前所有「有註解 vs 剝註解」「sonnet vs opus」的差值都落在噪音帶內、不能當訊號讀。任何拿 n≤8 fixture 比較模型或條件的實驗，必須先跑一次零改動重跑量翻轉率當底噪，否則量到的是噪音。資料在 G:\AI\AIMemory\artifacts\arm-test-2026-08-12\（含 ANALYSIS.md 與 64 筆逐字回答）。
- [f_3f5340] [2026-08-12T00:31:53.092Z] 2026-08-12 行為測試軸對照（同一組 8 個缺陷，模型冷讀 vs repo 既有 mutate-gate 閘門）：閘門 8/8 killed 且每條都紅在目標 check；模型按站點的命中率是 0/8 到 8/8 不等。⚠️ 這**不能**宣稱行為測試比模型會找 bug（閘門是為這些變異寫的、模型是冷讀，8/8 是構造上的），能宣稱的是「對**已枚舉**的缺陷，行為測試給確定性偵測，模型給 0–100% 外加 25% run-to-run 噪音」。可操作判準有兩條：①缺陷若「與標準樣板同形但參數處理被動過手腳」（實例 `const max = Math.max(1, Math.floor(limit) || 1)` → `const max = limit`），模型覆核期望值是 0——16 個回答全漏且全部在同一檔案誤報另一個不存在的缺陷，加派覆核者不會改善（同源天花板）∴ 這類不變式**必須**有行為閘門；②「碼內自相矛盾」（相鄰三行用不同陣列、計數器只增不減）模型 8/8 全中，是覆核甜蜜區、不必優先寫閘門。
[End specialist context]

[Persistent memory — lessons from your previous tasks]
- [2026-07-09T03:48:10.729Z] (目標與動機：用 uk-slot-codegen skill（位於 ~/.kiro/skills/uk-slot-code) [auto-summary] 覆寫修正後最終 Game_Define.ts 正確，但 spec_adapter 本身需修正。
[End persistent memory]

[Artifact output]
任務完成後，在回覆最末附一個 JSON block 供系統存檔：
```json
{"type":"artifact","summary":"一句話摘要","outputs":[{"type":"finding","content":"..."}],"files_modified":[],"tags":["tag1"]}
```
outputs.type 可用：finding, code_change, recommendation, analysis。
tags 用英文小寫。如果任務失敗或無有意義產出，不需要附。
[End artifact output]

[Memory recall — dynamically retrieved facts relevant to this message]
[uk-slot-codegen] (relevance 0.55)
- uk_slot_clash_of_olympus 的 M0b（Editor/Runtime 驗證）已於 2026-08-13 全綠：五項全過（Preview、SkeletonData 綁定、EffectPlate 19 份、熱鍵 1~8、Mask contentSize 含目視），scratch/codegen-report.md 的風險 1「執行期行為完全未驗證」降級；但綠燈邊界僅止於「骨架不會斷」不等於「功能會動」——PlayVsFeature()／PlayCollectFeature() 仍是空 stub、JP 無專屬演出、報獎跑分未串接
- 2026-08-12 uk_slot_clash_of_olympus codegen 完成（G:\Cocos_Project\uk_slot_clash_of_olympus，finalize gate 38 檢查 0 失敗、tsc 專案 diagnostics 0）。三個可重用的技術教訓（都是主 agent 接手修 65 個編譯錯誤時實查出來的）：①**`import protocol from "./Proto"` 的 default import 不能當 namespace 型別用**——寫 `protocol.<ns>.IRoundInfo` 會噴 TS2503，本次一口氣 60 處（RecoverSpinAck 43／SlotReels 13／ReelDevTool 4）。修法是補 `import type { <ns> } from "./Proto"` 並只改型別位置；⚠️**值位置（`new protocol.<ns>.SpinAck()`）必須保留**，Proto.ts 刻意用 default export 保住 CJS runtime object，誤改會編譯過但執行期 undefined ∴ 不可全域字串取代，要依 tsc 回報的精確 (line,col) 動刀。②**proto stub 的 `.d.ts` 會與 runtime `.js` 失步**且失步位置不對稱：本次 CollectResult/VSResult/JPResult 在 `.js` 有 prototype 預設值、`interface IRoundInfo` 也有（型別 any[]）、只有 `class RoundInfo` 缺 → TS2339 報的是 class，若只 grep interface 前幾十行會誤判成「interface 缺」而插錯位置（我就插錯了一次，撞出 TS2300 duplicate identifier）。③**mock 的實際形狀才是有效契約，不是 dev-spec proto 映射表的推測形狀**——本次 CollectResult 實際是 `{col, cashPositions:[{col,row,value}], totalWin}`，映射表寫的是 `{collectPositions, cashPositions:number[], jpPositions}`，照映射表寫 .d.ts 會讓 GameView mock 整批型別錯。另：gate_runner 的 3.4 `Mock_symbol_effect_data` regex 要求 `AwardDataVec:`（物件字面值形式），`round.AwardDataVec = [...]` 屬性指派**永遠過不了**，必須用具名 typed literal（這也正是 skill Step 3.4 規則 7「加 type annotation 讓 TS 攔缺欄位」的原意）。

[uk-872-eyestrike2] (relevance 0.52)
- uk_872_eyestrike2_client 的 FeatureWheel 停輪曲線量化事實（A 級：原型 v2 的移植常數與 FeatureWheelManager.ts:216-258 的七個 readonly 逐一比對相符——4.5s / 0.75s / 10% / 20% / 1% / 0.25s / 0.3s）：用該曲線算出「主曲線時間走到 85% 時，距離已經跑完 99.5%」∴ 最後 15% 的時間只走 0.5% 的角度——這就是輪盤「看起來早就停了但還沒亮」的成因，元凶是 SPEED_CURVE_SLOW_SPEED_RATIO=0.01；把它拖到 20% 時同一時點是 92.8%。調參用原型 G:\Cocos_Project\uk_872_eyestrike2_client\.claude_temp\wheel-click-prototype.html（v2 起現況版九格常數全開成滑桿、預設＝專案現值、附「回到專案現值」鈕）。

[uk-slot-eye-strike] (relevance 0.51)
- uk_872 Eye Strike 2 的轉輪 click 音效節奏提案（2026-08-09）做成獨立 HTML 原型放在 G:\Cocos_Project\uk_872_eyestrike2_client\.claude_temp\wheel-click-prototype.html（遊戲碼未動），內含現況版原封移植的 CalcSpeedCurve 三段曲線與停輪懸念三分支可背靠背 A/B；關鍵量測為現況到 Collect 亮起 5.55 秒（其中死時間 2.15 秒：慢爬 0.85＋hold 0.3＋settle 0.25＋空窗 0.75，注意 settle 是從 ROTATE_TIME 內扣不是外加）對比新版 A 分支 3.92 秒、峰值 447°/s；狀態為使用者拿去給編導評估中，待回饋才決定調整／寫設計文件／接進遊戲。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[codegen-git-init-gap]] (relevance 0.76)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/codegen-git-init-gap.md]
- 1. 缺口的形狀
- 2. 修法：Step 0.2 + 機械閘門
- 3. UK slot 專案的 git 追蹤慣例（實查，非推測）
- 4. 五輪異源覆核抓到的 12 條
- 5. 順帶回報但未動的既有問題
- 相關

## [[uk-slot-clash-olympus]] (relevance 0.72)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/uk-slot-clash-olympus.md]
- ⚠️ 本頁曾長期過時（2026-07-17 → 2026-08-12 才修正）
- 概述
- 開發進度
- 機制分類（2026-08-12 codegen 驗證版）
- 規格缺口 → 專案內的 `docs/spec-gaps.md`（2026-08-13 起唯一真相源）
- spec-to-impl 教訓（仍成立）
- Cocos prefab 踩坑（2026-08-12 M0b 實證）
- 相關
[End wiki retrieval]

[Delegation Task — id: moaplan_lifecycle_review]
Goal: 目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS Feature 演出與 unshow/replay 時序。背景：需要在 VsFeatureShowState 依 VSManager steps 串 Fly Expand Spine，且轉型前盤面用於還原、轉型後盤面用於收分。請自行讀 docs/M2-VS-design.md、docs/dev-spec.md 的 VS 段、GameView.ts、Game_Define.ts、VsFeatureShowState.ts、CollectFeatureShowState.ts、RecoverSpinAck.ts、SlotReels.ts。待決問題：現有框架有哪些既有 API 可最小復用，何時保存與恢復快照，無資產時如何避免假演出。驗收：給出狀態流程與可測驗收條件，指出 race 或 replay 風險。回報格式：結論、狀態流、風險、建議測試。
Context: 此工項屬於計畫「為 Clash of Olympus M2.2 在實作前完成獨立設計審查，鎖定 adapter、演出時序與 unshow/replay 的最小可交付邊界。」。

Complete this task. When done, summarize what you accomplished.
[結構化結果 — 必要步驟]
完成後**呼叫 structured_output 工具**繳交下列欄位（不是把 JSON 印在回覆裡，
那樣下一步收不到）：
  - summary: string
  - flow: array
  - risks: array
  - tests: array
文字回覆照常寫（人會看），structured_output 是額外的一步，不是取代。

---

**slot-dev:**
I'll start by reading the design docs and relevant source files for this review task.Good, found all files. Let me read them in parallel.## 結論

M2.1 的 `VSManager.Resolve()`（純函式，7/7 測試通過）已經把 VS Feature 的全部業務規則定案，M2.2 應該把 `VsFeatureShowState` 定位成**薄的 adapter + 演出層**：轉 proto → 呼叫 `Resolve()` → 依 `steps` 逐步播 Fly/Expand/Spine → 把結果交給 `CollectFeatureShowState`。目前 `VsFeatureShowState.ts` 與 `CollectFeatureShowState.ts` 都是空 stub（只有觸發判斷，`PlayVsFeature`/`PlayCollectFeature` 內容全空），`GameView.ts` 也還沒有任何欄位承接兩者之間的資料交接。

框架既有 API 可直接複用：`SlotReels.SetPlateSymbolForUnshow()`（無動畫、直接依資料寫死盤面）示範了「瞬間切到某個盤面狀態」該怎麼寫；`ColumnSymbol.SetSymbolInfos()/ChangeSymbol()` 是動畫結束後定案外觀的正確落點；`EffectPlate/SymbolSpine.ts`、`Spine/BaseSpine.ts`/`InLoopOutSpine.ts` 是「對決」idle spine 該仿的殼。但**跨格符號的 Fly/Expand（VS Cash/Collect 1×4）完全沒有現成元件**——`MaskExpand/` 是整盤遮罩，不是單符號佔多格；全專案 grep `Fly` 只有常數與音效名稱，沒有任何飛行動畫實作——這是要新建的元件，dev-spec 已經明確指出這點，本次審查確認無誤。

**最關鍵的一個結構性判斷**：dev-spec 把「轉型前/轉型後兩個盤面快照」講得很清楚，但沒講清楚的是——**轉型後盤面（`plateAfter`）不需要被持久化**。因為 `Resolve()` 是純函式、輸入只是 `RoundInfo.MainPlateSymbol`（轉型前，已存在 `SpinAck` 裡）與 `RoundInfo.VSResult`（也已存在），所以任何時候要「回到某一輪的 VS 結果」，只要重跑 `Resolve()` 就能得到一模一樣的 `plateAfter`/`collectWins`——不需要額外欄位、不需要 proto 補 log（GAP-09 對 VS 這條路徑其實不是阻塞）。這跟 `SetNowRoundInfo()` 現有做法（每次進場都重新從 `MainPlateSymbol` 算渲染盤面，不存渲染結果）是同一個模式，直接沿用即可。

## 狀態流

```
ScatterShowState
  └─ NextState(VS_FEATURE_SHOW)

VsFeatureShowState.OnEnter()
  1. vsResult = SpinAck.RoundQueue[CurPlateIndex].VSResult
  2. guard: !Game_Define.FEATURES.VS_FEATURE || !vsResult?.length
       → NextState(COLLECT_FEATURE_SHOW)；不做任何視覺變動（已存在的早退邏輯，須保留）
  3. input = AdaptVSResult(RoundInfo.MainPlateSymbol, vsResult, symbolIds)   ← 新增的薄 adapter，唯一新業務碼
  4. result = VSManager.Resolve(input)     ← 直接呼叫 M2.1 模組，不重寫規則
  5. for each step in result.steps（Cash 組 col 遞增 → Collect 組 col 遞增，M2.1 已保證順序）:
       a. Fly：該欄 Cash/JP 或 Collect 符號飛向 Vs(16) 位置（新元件）
       b. Expand：該欄 4 格覆蓋成 VsCash(17)/VsCollect(18)（新元件，仿 ColumnSymbol.SetSymbolInfos 落點）
       c. Spine：對決/倍率美術字（若資產未到位，走 AwardState.BigWin 那種 optional-component null guard，不 hard fail）
  6. GameView.VsFeatureResult = result   ← 新欄位，唯一交接管道，供步驟 7 讀
  7. NextState(COLLECT_FEATURE_SHOW)

CollectFeatureShowState.OnEnter()
  1. collectResult = SpinAck.RoundQueue[CurPlateIndex].CollectResult
  2. vsResult = GameView.VsFeatureResult   ← 讀步驟6的交接，不重算 S0-S4
  3. guard: 無 collectResult → NextState(AWARD)
  4. 依 [B28] Cash 先收、COLLECT/JP 後收，每個 Collect 用 vsResult.collectWins[col] ?? T 收分
  5. NextState(AWARD)
```

**Unshow/replay（現況，不建議在 M2.2 單獨解）**：`SpinState.OnEnter` 的 `HasUnshow` 分支只重灌 `SpinAck`，`UnshowPrepareState.ts:38-43` 那段真正要「回到上一局畫面、還原 `CurPlateIndex`」的邏輯整段是 TODO 註解，尚未實作——這是模板級缺口，VS Feature 只是繼承它，不是 VS 自己的問題。等這條路徑真正接上時，VS 這邊唯一要做的事就是：`SetNowRoundInfo(round)` 之後再呼叫一次 `VSManager.Resolve(round.MainPlateSymbol, round.VSResult)` 取得 `plateAfter`，用類似 `SetPlateSymbolForUnshow` 的無動畫寫入方式直接渲染定案盤面——不需要新的持久化欄位。

## 風險

1. **（高，框架級但 VS 首當其衝）Async 中斷無取消機制**：`BaseState`（`StateManager.ts:3-8`）沒有 `isActive`/取消 token，`VsFeatureShowState.OnEnter` 的 `await PlayVsFeature(...)` 是本輪目前最長的 await 鏈（Cash 組→Collect 組，逐欄 Fly+Expand+Spine）。若中途有任何外部呼叫 `stateManager.NextState()`（例如強制重連/skip），stub 目前寫法在動畫播完後仍會無條件呼叫 `NextState(COLLECT_FEATURE_SHOW)`，蓋掉中斷後真正該去的狀態——與本專案已知的 `await-gap-opens-finalize-race` 教訓同形，但這裡的曝光窗口是全輪最大的。
2. **（高）現有 `vsfeature` mock 資料不合法**：`GameView.ts:904-914` 直接把 `MainPlateSymbol[0].Col[0]` 寫成已轉型的 `VsCollect`，且只佔 1 格不是 1×4，盤面上完全沒有 `Vs`(16) 種子符號。拿這份 mock 餵真正的 `VSManager.Resolve()` 會落在 S1 找不到任何 VS 候選、S0 guard 判定不成立，等於這份 mock 目前**驗證不到 M2.2 要接的路徑**，必須先改寫成合規的轉型前盤面才能當整合測試 fixture。
3. **（中）Collect 收分係數交接管道不存在**：`CollectFeatureShowState` 讀的是自己的 `CollectResult`，但 S5 算法需要 `VsFeatureShowState` 算出的 `collectMul[col]`。目前 `GameView.ts` 沒有任何欄位可以帶這個值過去；若 `CollectFeatureShowState` 自己重算一份，等於複製 S0-S4 邏輯、兩份實作會漂移。
4. **（中）GAP-09 只是暫時不擋，不是已結**：`plateAfter` 不需持久化的結論只對「client 自己 Resolve」成立；若 server 未來真的補一個轉型後盤面欄位，兩邊必須比對（dev-only warn），不能默認 client 算的一定對——這個 cross-check 目前只設計給 `vsType`（S1），沒有預留給 `plateAfter`。
5. **（低）美術資產缺口（GAP-04）**：倍率書寫語意（`3X` vs `X2`）與美術字張數未定案，`PlayVsFeature` 若對美術元件寫死依賴會在資產未到位時整段掛掉；應仿 `AwardState.ts:106-110` 的 `if (!component) { log; skip }` 寫法降級。

## 建議測試

1. Adapter 單元測試：`colProto.IVSResult[]` → `VSResolveInput.vsResults` 轉換（含現有錯誤 mock 形狀應被拒絕/不觸發的案例）。
2. 用**改寫後**的合規 `vsfeature` mock（`Vs`(16) 種子 + 正確欄位）跑 Editor Preview，驗證 Cash 組先於 Collect 組播放、覆蓋後該欄 4 格皆為 17/18。
3. 無資產/關閉 flag 路徑：`Game_Define.FEATURES.VS_FEATURE=false` 或 `vsResult=[]` → 斷言零視覺變動、直接 `NextState(COLLECT_FEATURE_SHOW)`。
4. 交接測試：`VsFeatureShowState` 算出的 `collectWins[col]` 與 `CollectFeatureShowState` 實際收到的金額逐欄比對相等。
5. 中斷測試（對應風險1）：把 `PlayVsFeature` 內的某個 await 換成手動 resolver，在 pending 期間外部呼叫 `stateManager.NextState(其他狀態)`，斷言最終狀態是外部設定的那個，不是被 stale continuation 蓋回 `COLLECT_FEATURE_SHOW`。
6. Derive-not-persist 一致性測試（對應風險4，等 unshow 基礎路徑補上後才跑）：同一個 `RoundInfo` 呼叫兩次 `Resolve()`，斷言 `plateAfter`/`collectWins` 逐位元相同。Review complete. Summary of what I did:

**方法**：讀了 `docs/M2-VS-design.md`（僅涵蓋 M2.1 資料層）、`docs/dev-spec.md` 的 VS 段（規格定案細節）、`VsFeatureShowState.ts`/`CollectFeatureShowState.ts`（皆為空 stub）、`RecoverSpinAck.ts`、`SlotReels.ts`、`GameView.ts`、`Game_Define.ts`，並額外追了 `UnshowPrepareState.ts`、`SpinState.ts`、`StateManager.ts`、`ScatterShowState.ts` 這幾個 dev-spec 沒指名但決定得了「unshow 現況」與「狀態機能不能取消」的檔案。

**核心發現**：
1. `VSManager.Resolve()` 是純函式，這代表 VS 轉型後盤面根本不需要持久化——unshow/replay 只要重跑 `Resolve()` 就能還原，GAP-09 對 VS 這條路徑其實不阻塞。
2. 但 unshow 的基礎還原路徑（`CurPlateIndex` 回復、畫面重繪）在 `UnshowPrepareState.ts` 整段是 TODO 註解，尚未實作——VS Feature 只是繼承這個模板級缺口。
3. `StateManager`/`BaseState` 沒有取消機制，VS 的多步 Fly/Expand/Spine await 鏈是全輪最長的中斷曝光窗口。
4. 現有 `GameView.ts` 的 `vsfeature` mock 資料形狀不合法，測不到真正要接的 `Resolve()` 路徑。

已用 `structured_output` 提交 summary/flow/risks/tests 四欄位供下一步驟消費。

---

**User:**
<identity>
你是 slot-dev，UK 老虎機遊戲開發 specialist（Cocos Creator + Astarte Framework + TypeScript）。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Knowledge scope for this specialist]
Relevant wiki pages: uk-slot, uk-917, uk-slot-pitfalls, uk-slot-template, uk-slot-codegen, uk-slot-clash-olympus, uk-slot-eye-strike, uk-slot-pirates-queen, codegen-git-init-gap
[End knowledge scope]

[Specialist context — relevant facts for "slot-dev" domain]
- [f_79c118] [2026-05-29T12:03:17.165Z] uk_pirates_queen 是 UK 市場的海盜女王主題 slot 遊戲，6列5行盤面，含消除連鎖、懸賞令倍率、Free Game、輪盤選獎等機制
- [f_89a745] [2026-06-17T13:10:14.387Z] uk_pirates_queen 的懸賞令（WantedPoster）使用 cc.Layout 自動排版，ReconcileCascade 退場時因 node.active=false 導致 Layout 瞬間重排，已被提出視覺突兀需優化
- [f_e9bd6a] [2026-06-25T20:31:57.782Z] uk_pirates_queen 的掉落動畫（drop-out）凍結視窗回歸問題，根因是把凍結語意（m_isInDropMode）與掉落動畫 promise（m_dropAllSymbolsOutOfScreenPromise）混為一談，且直接在 StartSpin（約 L943）觸發掉落；經對抗式評選後採 MVP 最小手術方案：新增 m_isInDropMode 布林專職凍結語意、把 promise 降級為純動畫 handle、並把掉落觸發從 StartSpin 移到獨立的 TriggerDropOut() method。
- [f_1e8a3d] [2026-07-30T14:36:33.011Z] UK slot 專案的「方法/函式命名用大駝峰（PascalCase）」規範不適用於 Cocos 引擎生命週期回呼——onLoad / start / onDestroy / update 必須小寫，寫成 OnDestroy 引擎不會呼叫、變成死碼且無任何錯誤訊息（2026-07-30 在 uk_746_far_west_client 的 RTCtrl.ts:86 實證：eventManager 從未 unregister，已確認 astarte-framework 無 OnDestroy 鉤子、該專案其餘檔案皆用小寫）
- [f_931e5a] [2026-07-30T14:52:01.258Z] UK slot 專案枚舉某狀態旗標的寫入點時，grep `XxxName =` 會漏——這些專案慣例是 `public get/set PascalName` + `private m_pascalName`，程式碼可能直接寫私有欄位繞過 setter（2026-07-30 實證：uk_pirates_queen 的 GameView.ts:2314 寫 `m_isLockRotation = true`，搜 `IsLockRotation =` 只找到 4 筆、實際 5 筆），正確做法是搜 `[Mm]_?[Ii]sXxx` 之類同時涵蓋 m_ 前綴的 pattern
- [f_4ba968] [2026-07-30T16:17:09.612Z] uk_pirates_queen 與 uk_746_far_west_client 有同源的 RenderTexture 凍幀報獎機制（RTCtrl.ts + PerfGroup prefab：報獎期間把整個畫面渲成 RT 貼上、關掉底下實體節點省效能），不是存檔截圖也沒有 readPixels；搜 screenshot 找不到，關鍵字是 RenderTexture / RTCtrl / RT_EVENT，其餘 9 個 slot 專案皆未使用
- [f_ac39e3] [2026-07-30T16:17:09.612Z] uk_pirates_queen 是 RTCtrl 的進化版、uk_746_far_west_client 是初版（缺資源釋放、view.off、resize 守衛、防閃順序、主相機快取、onDestroy 小寫共 6 項，其中 3 項是真 bug）——新 slot 專案要移植 RT 凍幀一律抄 pirates_queen 版
- [f_967ccc] [2026-05-29T20:06:30.567Z] 使用者有一個 Cocos Creator 3.6.2 老虎機模板專案 uk_slot_template 位於 G:\Cocos_Project\uk_slot_template，是所有 UK slot 遊戲的 fork 來源
- [f_e8b2cf] [2026-05-29T20:06:30.570Z] uk_slot_template 支援三種轉輪玩法：Standard（傳統滾動）、Cascade（消除天降）、Tumble（快速掉落+乘倍），透過 FillStrategy 策略模式切換
- [f_991386] [2026-06-01T12:16:45.036Z] 使用者的 uk_slot_template 團隊規範要求方法（method/function）使用大駝峰（PascalCase）命名
- [f_500f52] [2026-07-06T20:13:27.710Z] UK slot 起新專案慣例：不用 git fork/clone（不保留模板 git history），用 git archive 從 uk_slot_template 解出→git init 全新 repo→跑 Tools_SlotSetUP/FirstClone.bat（讀根目錄 gameSetting.json）clone slotExtensions-client 到 extensions/（即 Astarte framework，獨立 repo 不進遊戲 repo）→npm install→改 GameId/盤面/FillStrategy
- [f_7e491d] [2026-07-07T07:52:13.433Z] uk_slot_template 有 4 個本地 commit 未 push（bgm 改註解佔位、欄數陣列改 Game_Define.COL 衍生、CheckPlateInfo 欄數守衛、ReelDevTool 驅動+IDLE 閘門修復）；模板是 org 共用 repo（IGS-ARCADE-DIVISION-RD2），push 前需使用者確認
- [f_233d31] [2026-07-07T07:52:13.462Z] 使用者的回灌工作流：在衍生遊戲修到的模板級問題（工具、守衛、寫死值）一律同步回 uk_slot_template；流程級教訓回寫 AI-canonical-corp skill 正本、專案級踩坑寫專案 AI.md、模式級修正寫 pattern-library 卡片
- [f_4cfe4c] [2026-07-07T07:52:13.480Z] FirstClone.bat 的 ../extensions 相對於執行時 cwd——從專案根執行會 clone 到上一層，需在 Tools_SlotSetUP/ 內執行
- [f_0376d5] [2026-07-07T20:34:51.301Z] uk slot 模板專案音訊決策：MG_Bgm 與 FG_Bgm 背景音樂引用在 template 專案中先註解掉（模板不附實際音檔），新遊戲專案需要 BGM 時再解除註解並補上音檔。
- [f_8b54ac] [2026-07-15T20:30:52.291Z] uk_slot_template 專案:MaskExpand 元件需支援多重遮罩(multi-mask),而非僅單一遮罩;此設計曾因疑慮被使用者還原一次,後續於 IMaskExpandHost 介面新增 SetVisibleSymbolCountOverride() 方法(IMaskExpander.ts),用以橋接本地與遠端架構的可見符號數量覆寫機制。
- [f_6a6988] [2026-07-15T20:30:54.145Z] uk_slot_template 專案的架構策略:Server 端只送出玩家可見的盤面資料(例如 5x6),而非完整盤面尺寸(例如 7x6),其餘部分由客戶端做前處理。
- [f_d54fd8] [2026-07-20T23:26:05.433Z] uk_slot_template 先前提及的 4 個本地未 push commit（bgm 改註解佔位、欄數陣列改 Game_Define.COL 衍生、CheckPlateInfo 欄數守衛、ReelDevTool 驅動+IDLE 閘門修復）已全數確認在 origin/main 上，分支狀態為 up to date with origin/main，此問題已解決
- [f_3f7536] [2026-06-03T12:26:41.806Z] cocos的老虎機專案都不能去改動Astarte Framework
- [f_r0b1nh] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_722_robinhood_client 位於 G:\Cocos_Project\uk_722_robinhood_client，Robin Hood 主題
- [f_wr4th9] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_739_wrath_of_thunder_client 位於 G:\Cocos_Project\uk_739_wrath_of_thunder_client，Wrath of Thunder 雷神主題
- [f_f4rw3s] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_746_far_west_client 位於 G:\Cocos_Project\uk_746_far_west_client，Far West 西部主題
- [f_ch4ch4] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_slot_chachacha 位於 G:\Cocos_Project\uk_slot_chachacha，Cha Cha Cha 拉丁舞主題
- [f_f4621c] [2026-06-19T02:11:08.786Z] 使用者決定 UK 老虎機專案採用分層文件規範：AI.md（索引層≤2000字）+ docs/modules.md（詳細層含事件介面/依賴/資料流），已建立 skill uk-slot-project-docs 控制此行為
- [f_e22204] [2026-06-19T02:11:08.803Z] 使用者偏好進入老虎機專案時不管改動檔案數多少都主動建 AI.md（放寬原本≥3檔案才建的門檻）
- [f_46f6e0] [2026-06-19T07:56:09.905Z] 並發 gotcha:在 Promise.all 之前的同步階段計算狀態決策(例如 willGhost),會與並發 group dispatch 產生 race condition;應把這類決策移到 async 階段計算以避免競態。
- [f_94500e] [2026-06-19T07:56:14.534Z] Cocos 版面要在「兩項移除一項」時避免置中跳動(snap),可用 ghost slot 雙佔位機制,在不改動 Layout 參數的前提下同時滿足 0→1 置中、2→1 不跳動與旋轉相容。
- [f_3165ae] [2026-06-26T13:11:01.098Z] AI-canonical-corp 的 slot skill（如 uk-slot-pattern-library）透過 junction 直接指向正本目錄，改正本即時反映到 ~/.kiro/skills/，不需額外跑 sync.ps1
- [f_e84e55] [2026-07-09T19:00:02.547Z] uk-slot-spec-to-impl skill 正本已加強（AI-canonical-corp commit 14887cd）：新增步驟0前提確認checklist、步驟2前置4項checklist gate、檢查點改模板格式輸出、AI.md綁定步驟1完成時、常見錯誤新增5條流程偏離實證教訓
- [f_8a9474] [2026-07-09T20:33:34.376Z] 記錄反覆出現的 AI 失誤時，把『常見錯誤』分成兩類：流程偏離（Process Deviations，工作流順序失誤，例如未先 invoke skill 從步驟0開始、跳過前置 checklist、基準拿錯衍生品）與技術錯誤（Technical Errors，實作層面失誤，例如型別/邏輯/命名寫錯）。兩類根因與修法不同——流程偏離靠 gate/流程強制修，技術錯誤靠測試/檢查修——分開列並各附 session 實證，比混成一坨更有用。此分類法可推廣到任何 skill 或 knowhow 庫的錯誤紀錄（來源：uk-slot-spec-to-impl 常見錯誤區重整，telegram-kiro-bridge-main 2026-07-09）。
- [f_437274] [2026-07-16T20:34:00.040Z] telegram-kiro-bridge 的 skill-usage.json 追蹤檔案孤兒化：vc-uof-hours entry 仍指向已改名的資料夾 igs-uof，且 igs-uof、uk-slot-logo-localization 兩個實際存在的 skill 資料夾未被登記 usage entry，待合併/補建
- [f_e68c39] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 E 區（通用機制模式庫）決策：全角色統一使用索引版（pattern 名稱 + 一句話描述），不塞 pattern-library 完整 158KB 內容
- [f_165cc0] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 D 區（Astarte Framework API）決策：只寫概要層（class + 生命週期 + 事件列表），不進到 method 簽名
- [f_f82ff1] [2026-07-28T11:03:56.028Z] uk-slot-logo-localization skill 的標準語系代碼清單已新增 urIN（烏爾都語印度），總計 24 個語系（不含 cn/en）
- [f_2d697b] [2026-07-30T16:17:09.612Z] uk-slot-pattern-library 的卡片新增流程需同步三處否則資料不一致：patterns/xxx.md 卡片本體、SKILL.md 索引表（+ 橫切機制表）、pattern-library-overview.html 的內嵌 PATTERNS JS 陣列與兩處寫死計數（line 50 subtitle 與 line 53-54 stat-box，只改 subtitle 會造成同頁自我矛盾）
- [f_4b088c] [2026-07-30T16:17:09.612Z] uk-slot-pattern-library 的 overview.html 參考專案計數慣例是「PATTERNS 陣列 unique refs 扣掉『框架 xxx』條目、不去重 wrath 的兩種寫法」（2026-07-30 用 git show 舊檔重算驗證與舊 subtitle 精確吻合）
- [f_4b2a6c] [2026-07-30T16:17:09.612Z] 異源覆核在「文件層自我一致性」（數字沒回頭同步、枚舉半途而廢、同頁多處寫死計數只改一處）上最有價值，這類問題同源自審結構上抓不到——因為自審驗的是「我改的那處對不對」而非「還有沒有別處」（2026-07-30 pattern-library #26 實證）
- [f_4367fb] [2026-07-30T20:31:36.930Z] UK 老虎機事件 gate 的重入防護應查下游狀態而非另設旗標：pre-stop gate 是否已執行改用 BombBoard.HasEventBombs() 這類「已註冊結果」查詢判斷，狀態源唯一，unshow/replay 還原時才不會與實際盤面脫節。
- [f_189848] [2026-07-30T20:31:42.262Z] UK 老虎機 unshow/replay 還原的時序保真原則：原始事件的觸發時機必須原樣保留（during-spin 觸發的 BOMB 不可為了實作方便降級成 after-stop），否則還原畫面與原始 spin 表現不一致。
- [f_cd0a8c] [2026-07-30T20:31:43.558Z] 診斷證據必須在 restart／recovery 邊界失效：recovery 之後若沿用 pre-recovery 的 API error 記錄，真正的 post-recovery 卡死會誤用陳舊錯誤當根因而誤診，因此 recovery 時要主動清除舊錯誤證據。
- [f_0ec894] [2026-07-30T20:31:48.451Z] 重現 restart 後的視窗溢出／狀態殘留類 bug，最有效的手法是拿真實 transcript 重播（real transcript replay），比造合成輸入更容易踩到真實邊界條件。
- [f_ff9bce] [2026-07-30T20:31:56.896Z] 依賴套件大版本升級的放行閘應是機械驗證而非主觀判斷：先 grep 全部 .ts/.mjs 確認零 import 指向已移除的模組（例如 MCP SDK 的 HTTP/SSE transport），零命中才放行 push。
- [f_115ddb] [2026-07-31T06:09:00.728Z] 純觀測欄位（只有測試讀、生產無人消費）等於沒有 runtime 訊號：這類欄位應在生產路徑落 log 讓問題在真實流量中自己曝光，否則 regression 復發時完全無聲——2026-07-31 bridge 的 lateCreates 實證
- [f_e92697] [2026-07-31T13:46:56.962Z] 在原本全同步的路徑中插入一個 await 就等於自己開了 finalize/cancel race 縫（2026-07-31 bridge F1 實證）：coalesceAsyncRunner 的 isCancelled 只在入口與補跑前檢查，fn 執行中翻轉完全攔不住，所有呼叫端的入口 guard 看起來像已保護到其實一個都擋不住 mid-run；修法是 await 回來後對 finalize flag 再檢一次，這類缺陷在型別、既有測試、API 回傳值上全都看不出來
- [f_5d0939] [2026-08-06T05:58:24.822Z] telegram-kiro-bridge 的 `npx tsc -p .` 在 noUnusedLocals 報 TS6133 時仍然會 emit dist，所以「tsc 紅了 = dist 沒更新」這個假設在此 repo 不成立——做突變測試時一律要 grep dist 確認突變真的進了產物才採信 smoke 結果，不可用 tsc 的 exit code 反推（2026-08-06 Fable5 覆核順帶發現；同一天我另外踩到反向的坑：突變寫成 `if (false && …)` 讓 tsc 型別收窄而編譯失敗、dist 沒更新，smoke 跑的是舊產物假綠）。
- [f_c4f291] [2026-08-06T23:38:37.267Z] 2026-08-07 方法論教訓：GitHub tree API 的 ?recursive=1 回應被截斷時，WebFetch 背後的小模型會對「存在性」問題自信地答 no——當天它連答「無 pyproject.toml／無 paulsha_cortex/／無 tests/」，一度讓我推論出「這個 repo 只有文件沒有程式碼」，足以推翻整份評估。翻案手法是直接打 raw.githubusercontent.com 的檔案 URL 當二元探針（存在→回檔案內容，不存在→404: Not Found），這個訊號不經摘要判斷、抗幻覺；列子目錄改用 git/trees/main:&lt;path&gt;（不遞迴、JSON 夠小不會截斷）也可靠。∴ 對「某某東西不存在」這類否定式主張，永遠要用探針覆核而非採信摘要——這是既有 research-report-citations-unverified 教訓（引用越像真的越要先查）的反向補完。
- [f_e88354] [2026-08-11T19:26:07.672Z] 拿本 repo 的碼片段當「找 bug」fixture 時，註解本身就是答案洩漏：本 repo 註解密度高、幾乎每個不變式旁都寫了為什麼，2026-08-12 的模型對照實驗中 5 次命中全部落在有註解點出不變式的題目、註解乾淨的兩題兩臂皆 0。∴ 設計這類 fixture 要至少各半（有/無註解洩漏）並分開計分，否則量到的是「會不會讀註解」而不是「能不能推導缺陷」；同理，用註解密集的碼去評估覆核者能力會系統性高估它。
- [f_8a90df] [2026-08-11T19:52:52.581Z] 設計「剝註解」對照組時不要留行號空洞：2026-08-12 的 fixture 保留原始行號、只抽掉註解行，結果行號變不連續，兩個模型都把空洞讀成「有程式碼被刻意隱藏」並開始推測那幾行的內容（S7 那題 sonnet 直接虛構「行 289-290 是 rawSteps 的初始化」並據此放棄作答）∴ 剝註解組的漏報被系統性放大、與「沒有註解可讀」混在一起無法分離。下次要嘛剝完重新連續編號，要嘛用等長空白行占位並在 prompt 說明。
- [f_ea64e9] [2026-08-11T23:30:21.616Z] 2026-08-12 量到 Kiro 上 code-review 模型評測的 test-retest 翻轉率：同一批 8 題 orig fixture、同 prompt、零改動重跑一次，16 個 cell 翻了 4 個（25%），sonnet-4.6[max] 4/8→6/8、opus-4.5 3/8→5/8，且四次全部同方向（新批次較高，純隨機同向機率 0.125，無法區分是運氣還是伺服器端批次效應）。⇒ n=8 的一臂光噪音就有約 ±1.4 題擺盪 ∴ 先前所有「有註解 vs 剝註解」「sonnet vs opus」的差值都落在噪音帶內、不能當訊號讀。任何拿 n≤8 fixture 比較模型或條件的實驗，必須先跑一次零改動重跑量翻轉率當底噪，否則量到的是噪音。資料在 G:\AI\AIMemory\artifacts\arm-test-2026-08-12\（含 ANALYSIS.md 與 64 筆逐字回答）。
- [f_3f5340] [2026-08-12T00:31:53.092Z] 2026-08-12 行為測試軸對照（同一組 8 個缺陷，模型冷讀 vs repo 既有 mutate-gate 閘門）：閘門 8/8 killed 且每條都紅在目標 check；模型按站點的命中率是 0/8 到 8/8 不等。⚠️ 這**不能**宣稱行為測試比模型會找 bug（閘門是為這些變異寫的、模型是冷讀，8/8 是構造上的），能宣稱的是「對**已枚舉**的缺陷，行為測試給確定性偵測，模型給 0–100% 外加 25% run-to-run 噪音」。可操作判準有兩條：①缺陷若「與標準樣板同形但參數處理被動過手腳」（實例 `const max = Math.max(1, Math.floor(limit) || 1)` → `const max = limit`），模型覆核期望值是 0——16 個回答全漏且全部在同一檔案誤報另一個不存在的缺陷，加派覆核者不會改善（同源天花板）∴ 這類不變式**必須**有行為閘門；②「碼內自相矛盾」（相鄰三行用不同陣列、計數器只增不減）模型 8/8 全中，是覆核甜蜜區、不必優先寫閘門。
[End specialist context]

[Persistent memory — lessons from your previous tasks]
- [2026-07-09T03:48:10.729Z] (目標與動機：用 uk-slot-codegen skill（位於 ~/.kiro/skills/uk-slot-code) [auto-summary] 覆寫修正後最終 Game_Define.ts 正確，但 spec_adapter 本身需修正。
[End persistent memory]

[Artifact output]
任務完成後，在回覆最末附一個 JSON block 供系統存檔：
```json
{"type":"artifact","summary":"一句話摘要","outputs":[{"type":"finding","content":"..."}],"files_modified":[],"tags":["tag1"]}
```
outputs.type 可用：finding, code_change, recommendation, analysis。
tags 用英文小寫。如果任務失敗或無有意義產出，不需要附。
[End artifact output]

[Memory recall — dynamically retrieved facts relevant to this message]
[uk-slot-codegen] (relevance 0.56)
- 2026-08-12 uk_slot_clash_of_olympus codegen 完成（G:\Cocos_Project\uk_slot_clash_of_olympus，finalize gate 38 檢查 0 失敗、tsc 專案 diagnostics 0）。三個可重用的技術教訓（都是主 agent 接手修 65 個編譯錯誤時實查出來的）：①**`import protocol from "./Proto"` 的 default import 不能當 namespace 型別用**——寫 `protocol.<ns>.IRoundInfo` 會噴 TS2503，本次一口氣 60 處（RecoverSpinAck 43／SlotReels 13／ReelDevTool 4）。修法是補 `import type { <ns> } from "./Proto"` 並只改型別位置；⚠️**值位置（`new protocol.<ns>.SpinAck()`）必須保留**，Proto.ts 刻意用 default export 保住 CJS runtime object，誤改會編譯過但執行期 undefined ∴ 不可全域字串取代，要依 tsc 回報的精確 (line,col) 動刀。②**proto stub 的 `.d.ts` 會與 runtime `.js` 失步**且失步位置不對稱：本次 CollectResult/VSResult/JPResult 在 `.js` 有 prototype 預設值、`interface IRoundInfo` 也有（型別 any[]）、只有 `class RoundInfo` 缺 → TS2339 報的是 class，若只 grep interface 前幾十行會誤判成「interface 缺」而插錯位置（我就插錯了一次，撞出 TS2300 duplicate identifier）。③**mock 的實際形狀才是有效契約，不是 dev-spec proto 映射表的推測形狀**——本次 CollectResult 實際是 `{col, cashPositions:[{col,row,value}], totalWin}`，映射表寫的是 `{collectPositions, cashPositions:number[], jpPositions}`，照映射表寫 .d.ts 會讓 GameView mock 整批型別錯。另：gate_runner 的 3.4 `Mock_symbol_effect_data` regex 要求 `AwardDataVec:`（物件字面值形式），`round.AwardDataVec = [...]` 屬性指派**永遠過不了**，必須用具名 typed literal（這也正是 skill Step 3.4 規則 7「加 type annotation 讓 TS 攔缺欄位」的原意）。
- uk_slot_clash_of_olympus 的 M0b（Editor/Runtime 驗證）已於 2026-08-13 全綠：五項全過（Preview、SkeletonData 綁定、EffectPlate 19 份、熱鍵 1~8、Mask contentSize 含目視），scratch/codegen-report.md 的風險 1「執行期行為完全未驗證」降級；但綠燈邊界僅止於「骨架不會斷」不等於「功能會動」——PlayVsFeature()／PlayCollectFeature() 仍是空 stub、JP 無專屬演出、報獎跑分未串接

[uk-917] (relevance 0.55)
- 使用者要求 codegen 產出的老虎機專案不可 commit AI 相關目錄（.kiro 等）與 docs 目錄；正確追蹤範圍照 uk_917 的 .gitignore 而非模板（模板不是出貨形態，自己 track 著 .kiro/ 24 檔）

[uk-872-eyestrike2] (relevance 0.52)
- uk_872_eyestrike2_client 的 FeatureWheel 停輪曲線量化事實（A 級：原型 v2 的移植常數與 FeatureWheelManager.ts:216-258 的七個 readonly 逐一比對相符——4.5s / 0.75s / 10% / 20% / 1% / 0.25s / 0.3s）：用該曲線算出「主曲線時間走到 85% 時，距離已經跑完 99.5%」∴ 最後 15% 的時間只走 0.5% 的角度——這就是輪盤「看起來早就停了但還沒亮」的成因，元凶是 SPEED_CURVE_SLOW_SPEED_RATIO=0.01；把它拖到 20% 時同一時點是 92.8%。調參用原型 G:\Cocos_Project\uk_872_eyestrike2_client\.claude_temp\wheel-click-prototype.html（v2 起現況版九格常數全開成滑桿、預設＝專案現值、附「回到專案現值」鈕）。
- 要讓單一專案不受專案級 CLAUDE.md 某條指示約束（例如「改完自動 git commit」），做法是在專案根建 CLAUDE.local.md 寫下反向指示來壓過它，而不是去改共用的 CLAUDE.md——2026-08-11 於 G:\Cocos_Project\uk_872_eyestrike2_client 用此法停掉自動 commit。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[codegen-git-init-gap]] (relevance 0.79)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/codegen-git-init-gap.md]
- 1. 缺口的形狀
- 2. 修法：Step 0.2 + 機械閘門
- 3. UK slot 專案的 git 追蹤慣例（實查，非推測）
- 4. 五輪異源覆核抓到的 12 條
- 5. 順帶回報但未動的既有問題
- 相關

## [[uk-slot-clash-olympus]] (relevance 0.73)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/uk-slot-clash-olympus.md]
- ⚠️ 本頁曾長期過時（2026-07-17 → 2026-08-12 才修正）
- 概述
- 開發進度
- 機制分類（2026-08-12 codegen 驗證版）
- 規格缺口 → 專案內的 `docs/spec-gaps.md`（2026-08-13 起唯一真相源）
- spec-to-impl 教訓（仍成立）
- Cocos prefab 踩坑（2026-08-12 M0b 實證）
- 相關
[End wiki retrieval]

[Delegation Task — id: moaplan_adapter_review]
Goal: 目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS proto mock adapter 設計。背景：M2.1 的 assets/Script/Feature/VSManager.ts 是純函式；M2.2 要由 VsFeatureShowState 將 stub VSResult 接入，並讓 GameView 的 vsfeature mock 產生可信的轉型前盤面。請自行讀 docs/M2-VS-design.md、docs/modules.md、GameView.ts、VsFeatureShowState.ts、RecoverSpinAck.ts 與 proto stub。待決問題：最小改動檔案集合、資料適配責任、server proto 到來時的替換邊界。驗收：提出具體檔案與方法層級的設計，指出不可違反的 M2.1 契約。回報格式：結論、檔案清單、風險、建議測試。
Context: 此工項屬於計畫「為 Clash of Olympus M2.2 在實作前完成獨立設計審查，鎖定 adapter、演出時序與 unshow/replay 的最小可交付邊界。」。

Complete this task. When done, summarize what you accomplished.
[結構化結果 — 必要步驟]
完成後**呼叫 structured_output 工具**繳交下列欄位（不是把 JSON 印在回覆裡，
那樣下一步收不到）：
  - summary: string
  - files: array
  - risks: array
  - tests: array
文字回覆照常寫（人會看），structured_output 是額外的一步，不是取代。

---

**slot-dev:**
## 結論

M2.2 的最小改動方案：把 proto→VSManager 輸入的轉換寫成 **VSManager.ts 內的純函式**（不是塞進 VsFeatureShowState），靠 `import type { colProto }` 保持零 cc 依賴，沿用既有的 `ts-node --transpile-only` 測試方式；VsFeatureShowState 只做「呼叫 adapter → Resolve() → 依 steps 播動畫 → 把 plateAfter 套回顯示盤面」。但目前的 mock（GameView.ts:904-915）在型別上就會讓 `Resolve()` 永遠 `isTriggered=false`——這不是新缺口，modules.md 已經寫明要在 M2.2 修，adapter 設計必須連同這處修正一起交付，否則接了也等於沒接。

## 檔案清單

1. **`assets/Script/Feature/VSManager.ts`**（新增，不改既有 `Resolve()`）
   - 新增 `import type { colProto } from "../Proto";`
   - 新增匯出函式 `AdaptRoundToVSInput(plate: ReadonlyArray<colProto.ICColumn>, vsResult: ReadonlyArray<colProto.IVSResult> | null | undefined, symbolIds: VSSymbolIds): VSResolveInput`
     - plate：`col.Col.map(cell => ({Symbol: cell.Symbol??0, Number: cell.Number??0, JPState: cell.JPState??0}))`
     - vsResults：`reelIndex = raw.reelIndex ?? raw.appliedPositions?.[0]?.col`；缺兩者則整筆丟棄並 `console.warn`（連 reelIndex 都沒有，無法進 `VSResolveWarning`）
     - vsType：把 raw 數值（依現有 mock 先例是 symbol id）對照 `symbolIds.vsCash→'cash'`／`symbolIds.vsCollect→'collect'`；無法辨識時記一筆獨立於 VSManager 內部 warning 之外的 adapter-level warning
   - 因為只用 `import type`，不影響 `tests/VSManager.test.ts` 現有的 ts-node 執行路徑

2. **`assets/Script/GameState/VsFeatureShowState.ts`**
   - `PlayVsFeature()` 呼叫 `AdaptRoundToVSInput` + `VSManager.Resolve()`
   - `!result.isTriggered` 時直接跳過（維持現有「無 VS 就跳 State」語意的延伸）
   - 依 `result.steps` 順序（Cash 組已排在前、Collect 組在後）逐步做 Fly/Expand/Spine
   - **關鍵**：`OnLeave()`/播放結束前，必須把 `result.plateAfter` 寫回實際顯示盤面（`SlotReels.SetPlateInfo` 或等效呼叫），否則 CollectFeatureShowState 進場時畫面符號跟資料不同步

3. **`assets/Script/GameView.ts`**（修正既有 bug，非新增功能）
   - Line 908：`Symbol.VsCollect` → `Symbol.Collect`（轉型前盤面不該放轉型後符號，否則 `VSManager` 的 `HasSymbol(plate, symbolIds.collect)` guard 直接失敗）
   - Line 910-912：`VSResult` 條目補上 `reelIndex: 0`（目前完全沒有這個欄位）

4. **測試**：在 `tests/` 下對 `AdaptRoundToVSInput` 補純函式單元測試（走既有 `ts-node --transpile-only` 慣例），涵蓋 reelIndex 缺失 fallback 與 vsType 無法辨識兩個分支。

## 風險

1. **vsType 數值編碼未定案**：proto stub 的 `IVSResult.vsType` 是 `number`，語意未寫死；唯一現有先例（mock）用的是 symbol id（`VsCollect=18`）。建議照此先例做轉換，但要登記進 `docs/spec-gaps.md`，因為真 proto 到手前無法排除是另一套獨立 enum（同類先例：GAP-04 倍率書寫語意也是「暫定非定案」）。
2. **plateAfter 沒有交棒點**：`VSManager.Resolve()` 回傳轉型後盤面，但目前沒有任何程式碼把它寫回顯示層或傳給 `CollectFeatureShowState`。兩份設計文件都沒明講由誰負責這一步——這正是 M2.2 要釘的整合點，不能只加 adapter。
3. **可測性衝突**：`docs/M2-VS-design.md` 原文字面說「下一切片才在 VsFeatureShowState 轉換」，但該檔 import `cc` 的 `log`，塞進去會讓轉換邏輯脫離 `ts-node --transpile-only` 可測範圍。建議把純轉換邏輯放回 VSManager.ts（同檔案、type-only import），State 只做呼叫，兩者都沒有違反「之後只改 adapter、不改 `Resolve()` 規則核心」的既定方向。
4. **Mock 現狀會讓 Resolve() 恆不觸發**：col0 放轉型後符號 + 缺 reelIndex，兩者疊加後即使接上 adapter，`isTriggered` 也會是 false，等同沒接——modules.md 已預告，須與 adapter 一起修，不可分開處理。
5. **文件間用字落差（低嚴重度）**：M2.1 設計文件說「類型不符→安全略過」，但 `docs/dev-spec.md`（規格權威）S1 寫「不符→dev-only warn，不改行為，以 server 為準」。現行 `VSManager.IsValidReel` 是前者（整筆過濾掉）。因規格已證明兩類型欄位互斥（col 0/COL-1 只可能 collect，1~COL-2 只可能 cash），實務上此分支不會真的觸發，但建議至少把兩份文件的措辭對齊，避免日後真 server 出現邊界輸入時行為跟文件描述兜不起來。
6. **FreePlateSymbol 尚未接線**：`GameView.ts:1527` 有一行被註解掉的「free game 讀 FreePlateSymbol」邏輯，目前恆讀 `MainPlateSymbol`。VS adapter 比照現狀只吃 `MainPlateSymbol` 是可接受的（非本切片新增缺口），但建議在呼叫處留一個好認的 TODO 錨點。
7. **unshow/replay**：兩份文件都已標記本切片不做；但風險 2 的「plateAfter 套用方式」若隨手寫死，會讓下一切片做 unshow 時要整個重做——建議套用方式順便保留 transform 前的盤面快照，為 unshow 鋪路，但不在本切片實作。

## 建議測試

1. `AdaptRoundToVSInput` 純函式單元測試（同 VSManager 現有 `ts-node --transpile-only` 慣例）：reelIndex 缺失時 fallback 到 `appliedPositions[0].col`；vsType 無法辨識時的分支。
2. 修正 mock 後，Cocos Preview 手動按熱鍵 8（vsfeature），確認 `VsFeatureShowState` 不再直接跳過（`!vsResult || vsResult.length===0` 分支不成立）且真的進入 `PlayVsFeature`。
3. 針對風險 2：確認 Collect 演出開始時，畫面盤面符號已是 `VsCollect(18)`，不是殘留舊符號（手動 log 或 codegen finalize gate 皆可，非必要寫成自動化測試）。```json
{"type":"artifact","summary":"審查 uk_slot_clash_of_olympus M2.2 VS proto mock adapter 設計：建議把轉換邏輯放在 VSManager.ts 內的純函式（保持 ts-node 可測），並發現現有 GameView mock 有兩處會讓 Resolve() 恆不觸發的 bug，需與 adapter 一併修正","outputs":[{"type":"recommendation","content":"AdaptRoundToVSInput() 應為 VSManager.ts 內的 exported pure function（type-only import colProto），VsFeatureShowState 只做呼叫+播放+plateAfter 寫回顯示層"},{"type":"finding","content":"GameView.ts:908-912 的 vsfeature mock：col0 用轉型後符號 VsCollect(18) 而非 Collect(15)、VSResult 缺 reelIndex，兩者疊加會讓 VSManager.Resolve() 恆回傳 isTriggered=false"},{"type":"finding","content":"VSManager.Resolve() 回傳的 plateAfter 目前沒有任何寫回顯示盤面或 CollectFeatureShowState 的機制，是 M2.2 必須釘的整合缺口"},{"type":"finding","content":"proto IVSResult.vsType 為 number，其編碼語意（symbol id vs 獨立 enum）未定案，僅有 mock 先例可循，應登記 spec-gap"},{"type":"finding","content":"M2.1 設計文件（安全略過）與 dev-spec.md 規格權威 S1（warn 不改行為）對「類型不符」措辭不一致，雖因欄位互斥實務不會觸發，仍建議對齊文件用字"}],"files_modified":[],"tags":["uk-slot-clash-olympus","vs-feature","adapter-design","proto-stub","design-review"]}
```

---

**User:**
<identity>
你是 slot-dev，UK 老虎機遊戲開發 specialist（Cocos Creator + Astarte Framework + TypeScript）。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Knowledge scope for this specialist]
Relevant wiki pages: uk-slot, uk-917, uk-slot-pitfalls, uk-slot-template, uk-slot-codegen, uk-slot-clash-olympus, uk-slot-eye-strike, uk-slot-pirates-queen, codegen-git-init-gap
[End knowledge scope]

[Specialist context — relevant facts for "slot-dev" domain]
- [f_79c118] [2026-05-29T12:03:17.165Z] uk_pirates_queen 是 UK 市場的海盜女王主題 slot 遊戲，6列5行盤面，含消除連鎖、懸賞令倍率、Free Game、輪盤選獎等機制
- [f_89a745] [2026-06-17T13:10:14.387Z] uk_pirates_queen 的懸賞令（WantedPoster）使用 cc.Layout 自動排版，ReconcileCascade 退場時因 node.active=false 導致 Layout 瞬間重排，已被提出視覺突兀需優化
- [f_e9bd6a] [2026-06-25T20:31:57.782Z] uk_pirates_queen 的掉落動畫（drop-out）凍結視窗回歸問題，根因是把凍結語意（m_isInDropMode）與掉落動畫 promise（m_dropAllSymbolsOutOfScreenPromise）混為一談，且直接在 StartSpin（約 L943）觸發掉落；經對抗式評選後採 MVP 最小手術方案：新增 m_isInDropMode 布林專職凍結語意、把 promise 降級為純動畫 handle、並把掉落觸發從 StartSpin 移到獨立的 TriggerDropOut() method。
- [f_1e8a3d] [2026-07-30T14:36:33.011Z] UK slot 專案的「方法/函式命名用大駝峰（PascalCase）」規範不適用於 Cocos 引擎生命週期回呼——onLoad / start / onDestroy / update 必須小寫，寫成 OnDestroy 引擎不會呼叫、變成死碼且無任何錯誤訊息（2026-07-30 在 uk_746_far_west_client 的 RTCtrl.ts:86 實證：eventManager 從未 unregister，已確認 astarte-framework 無 OnDestroy 鉤子、該專案其餘檔案皆用小寫）
- [f_931e5a] [2026-07-30T14:52:01.258Z] UK slot 專案枚舉某狀態旗標的寫入點時，grep `XxxName =` 會漏——這些專案慣例是 `public get/set PascalName` + `private m_pascalName`，程式碼可能直接寫私有欄位繞過 setter（2026-07-30 實證：uk_pirates_queen 的 GameView.ts:2314 寫 `m_isLockRotation = true`，搜 `IsLockRotation =` 只找到 4 筆、實際 5 筆），正確做法是搜 `[Mm]_?[Ii]sXxx` 之類同時涵蓋 m_ 前綴的 pattern
- [f_4ba968] [2026-07-30T16:17:09.612Z] uk_pirates_queen 與 uk_746_far_west_client 有同源的 RenderTexture 凍幀報獎機制（RTCtrl.ts + PerfGroup prefab：報獎期間把整個畫面渲成 RT 貼上、關掉底下實體節點省效能），不是存檔截圖也沒有 readPixels；搜 screenshot 找不到，關鍵字是 RenderTexture / RTCtrl / RT_EVENT，其餘 9 個 slot 專案皆未使用
- [f_ac39e3] [2026-07-30T16:17:09.612Z] uk_pirates_queen 是 RTCtrl 的進化版、uk_746_far_west_client 是初版（缺資源釋放、view.off、resize 守衛、防閃順序、主相機快取、onDestroy 小寫共 6 項，其中 3 項是真 bug）——新 slot 專案要移植 RT 凍幀一律抄 pirates_queen 版
- [f_967ccc] [2026-05-29T20:06:30.567Z] 使用者有一個 Cocos Creator 3.6.2 老虎機模板專案 uk_slot_template 位於 G:\Cocos_Project\uk_slot_template，是所有 UK slot 遊戲的 fork 來源
- [f_e8b2cf] [2026-05-29T20:06:30.570Z] uk_slot_template 支援三種轉輪玩法：Standard（傳統滾動）、Cascade（消除天降）、Tumble（快速掉落+乘倍），透過 FillStrategy 策略模式切換
- [f_991386] [2026-06-01T12:16:45.036Z] 使用者的 uk_slot_template 團隊規範要求方法（method/function）使用大駝峰（PascalCase）命名
- [f_500f52] [2026-07-06T20:13:27.710Z] UK slot 起新專案慣例：不用 git fork/clone（不保留模板 git history），用 git archive 從 uk_slot_template 解出→git init 全新 repo→跑 Tools_SlotSetUP/FirstClone.bat（讀根目錄 gameSetting.json）clone slotExtensions-client 到 extensions/（即 Astarte framework，獨立 repo 不進遊戲 repo）→npm install→改 GameId/盤面/FillStrategy
- [f_7e491d] [2026-07-07T07:52:13.433Z] uk_slot_template 有 4 個本地 commit 未 push（bgm 改註解佔位、欄數陣列改 Game_Define.COL 衍生、CheckPlateInfo 欄數守衛、ReelDevTool 驅動+IDLE 閘門修復）；模板是 org 共用 repo（IGS-ARCADE-DIVISION-RD2），push 前需使用者確認
- [f_233d31] [2026-07-07T07:52:13.462Z] 使用者的回灌工作流：在衍生遊戲修到的模板級問題（工具、守衛、寫死值）一律同步回 uk_slot_template；流程級教訓回寫 AI-canonical-corp skill 正本、專案級踩坑寫專案 AI.md、模式級修正寫 pattern-library 卡片
- [f_4cfe4c] [2026-07-07T07:52:13.480Z] FirstClone.bat 的 ../extensions 相對於執行時 cwd——從專案根執行會 clone 到上一層，需在 Tools_SlotSetUP/ 內執行
- [f_0376d5] [2026-07-07T20:34:51.301Z] uk slot 模板專案音訊決策：MG_Bgm 與 FG_Bgm 背景音樂引用在 template 專案中先註解掉（模板不附實際音檔），新遊戲專案需要 BGM 時再解除註解並補上音檔。
- [f_8b54ac] [2026-07-15T20:30:52.291Z] uk_slot_template 專案:MaskExpand 元件需支援多重遮罩(multi-mask),而非僅單一遮罩;此設計曾因疑慮被使用者還原一次,後續於 IMaskExpandHost 介面新增 SetVisibleSymbolCountOverride() 方法(IMaskExpander.ts),用以橋接本地與遠端架構的可見符號數量覆寫機制。
- [f_6a6988] [2026-07-15T20:30:54.145Z] uk_slot_template 專案的架構策略:Server 端只送出玩家可見的盤面資料(例如 5x6),而非完整盤面尺寸(例如 7x6),其餘部分由客戶端做前處理。
- [f_d54fd8] [2026-07-20T23:26:05.433Z] uk_slot_template 先前提及的 4 個本地未 push commit（bgm 改註解佔位、欄數陣列改 Game_Define.COL 衍生、CheckPlateInfo 欄數守衛、ReelDevTool 驅動+IDLE 閘門修復）已全數確認在 origin/main 上，分支狀態為 up to date with origin/main，此問題已解決
- [f_3f7536] [2026-06-03T12:26:41.806Z] cocos的老虎機專案都不能去改動Astarte Framework
- [f_r0b1nh] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_722_robinhood_client 位於 G:\Cocos_Project\uk_722_robinhood_client，Robin Hood 主題
- [f_wr4th9] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_739_wrath_of_thunder_client 位於 G:\Cocos_Project\uk_739_wrath_of_thunder_client，Wrath of Thunder 雷神主題
- [f_f4rw3s] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_746_far_west_client 位於 G:\Cocos_Project\uk_746_far_west_client，Far West 西部主題
- [f_ch4ch4] [2026-06-03T12:35:00.000Z] 使用者有一個 Cocos Creator 老虎機專案 uk_slot_chachacha 位於 G:\Cocos_Project\uk_slot_chachacha，Cha Cha Cha 拉丁舞主題
- [f_f4621c] [2026-06-19T02:11:08.786Z] 使用者決定 UK 老虎機專案採用分層文件規範：AI.md（索引層≤2000字）+ docs/modules.md（詳細層含事件介面/依賴/資料流），已建立 skill uk-slot-project-docs 控制此行為
- [f_e22204] [2026-06-19T02:11:08.803Z] 使用者偏好進入老虎機專案時不管改動檔案數多少都主動建 AI.md（放寬原本≥3檔案才建的門檻）
- [f_46f6e0] [2026-06-19T07:56:09.905Z] 並發 gotcha:在 Promise.all 之前的同步階段計算狀態決策(例如 willGhost),會與並發 group dispatch 產生 race condition;應把這類決策移到 async 階段計算以避免競態。
- [f_94500e] [2026-06-19T07:56:14.534Z] Cocos 版面要在「兩項移除一項」時避免置中跳動(snap),可用 ghost slot 雙佔位機制,在不改動 Layout 參數的前提下同時滿足 0→1 置中、2→1 不跳動與旋轉相容。
- [f_3165ae] [2026-06-26T13:11:01.098Z] AI-canonical-corp 的 slot skill（如 uk-slot-pattern-library）透過 junction 直接指向正本目錄，改正本即時反映到 ~/.kiro/skills/，不需額外跑 sync.ps1
- [f_e84e55] [2026-07-09T19:00:02.547Z] uk-slot-spec-to-impl skill 正本已加強（AI-canonical-corp commit 14887cd）：新增步驟0前提確認checklist、步驟2前置4項checklist gate、檢查點改模板格式輸出、AI.md綁定步驟1完成時、常見錯誤新增5條流程偏離實證教訓
- [f_8a9474] [2026-07-09T20:33:34.376Z] 記錄反覆出現的 AI 失誤時，把『常見錯誤』分成兩類：流程偏離（Process Deviations，工作流順序失誤，例如未先 invoke skill 從步驟0開始、跳過前置 checklist、基準拿錯衍生品）與技術錯誤（Technical Errors，實作層面失誤，例如型別/邏輯/命名寫錯）。兩類根因與修法不同——流程偏離靠 gate/流程強制修，技術錯誤靠測試/檢查修——分開列並各附 session 實證，比混成一坨更有用。此分類法可推廣到任何 skill 或 knowhow 庫的錯誤紀錄（來源：uk-slot-spec-to-impl 常見錯誤區重整，telegram-kiro-bridge-main 2026-07-09）。
- [f_437274] [2026-07-16T20:34:00.040Z] telegram-kiro-bridge 的 skill-usage.json 追蹤檔案孤兒化：vc-uof-hours entry 仍指向已改名的資料夾 igs-uof，且 igs-uof、uk-slot-logo-localization 兩個實際存在的 skill 資料夾未被登記 usage entry，待合併/補建
- [f_e68c39] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 E 區（通用機制模式庫）決策：全角色統一使用索引版（pattern 名稱 + 一句話描述），不塞 pattern-library 完整 158KB 內容
- [f_165cc0] [2026-07-28T08:04:03.118Z] 公司 AI 知識庫的 D 區（Astarte Framework API）決策：只寫概要層（class + 生命週期 + 事件列表），不進到 method 簽名
- [f_f82ff1] [2026-07-28T11:03:56.028Z] uk-slot-logo-localization skill 的標準語系代碼清單已新增 urIN（烏爾都語印度），總計 24 個語系（不含 cn/en）
- [f_2d697b] [2026-07-30T16:17:09.612Z] uk-slot-pattern-library 的卡片新增流程需同步三處否則資料不一致：patterns/xxx.md 卡片本體、SKILL.md 索引表（+ 橫切機制表）、pattern-library-overview.html 的內嵌 PATTERNS JS 陣列與兩處寫死計數（line 50 subtitle 與 line 53-54 stat-box，只改 subtitle 會造成同頁自我矛盾）
- [f_4b088c] [2026-07-30T16:17:09.612Z] uk-slot-pattern-library 的 overview.html 參考專案計數慣例是「PATTERNS 陣列 unique refs 扣掉『框架 xxx』條目、不去重 wrath 的兩種寫法」（2026-07-30 用 git show 舊檔重算驗證與舊 subtitle 精確吻合）
- [f_4b2a6c] [2026-07-30T16:17:09.612Z] 異源覆核在「文件層自我一致性」（數字沒回頭同步、枚舉半途而廢、同頁多處寫死計數只改一處）上最有價值，這類問題同源自審結構上抓不到——因為自審驗的是「我改的那處對不對」而非「還有沒有別處」（2026-07-30 pattern-library #26 實證）
- [f_4367fb] [2026-07-30T20:31:36.930Z] UK 老虎機事件 gate 的重入防護應查下游狀態而非另設旗標：pre-stop gate 是否已執行改用 BombBoard.HasEventBombs() 這類「已註冊結果」查詢判斷，狀態源唯一，unshow/replay 還原時才不會與實際盤面脫節。
- [f_189848] [2026-07-30T20:31:42.262Z] UK 老虎機 unshow/replay 還原的時序保真原則：原始事件的觸發時機必須原樣保留（during-spin 觸發的 BOMB 不可為了實作方便降級成 after-stop），否則還原畫面與原始 spin 表現不一致。
- [f_cd0a8c] [2026-07-30T20:31:43.558Z] 診斷證據必須在 restart／recovery 邊界失效：recovery 之後若沿用 pre-recovery 的 API error 記錄，真正的 post-recovery 卡死會誤用陳舊錯誤當根因而誤診，因此 recovery 時要主動清除舊錯誤證據。
- [f_0ec894] [2026-07-30T20:31:48.451Z] 重現 restart 後的視窗溢出／狀態殘留類 bug，最有效的手法是拿真實 transcript 重播（real transcript replay），比造合成輸入更容易踩到真實邊界條件。
- [f_ff9bce] [2026-07-30T20:31:56.896Z] 依賴套件大版本升級的放行閘應是機械驗證而非主觀判斷：先 grep 全部 .ts/.mjs 確認零 import 指向已移除的模組（例如 MCP SDK 的 HTTP/SSE transport），零命中才放行 push。
- [f_115ddb] [2026-07-31T06:09:00.728Z] 純觀測欄位（只有測試讀、生產無人消費）等於沒有 runtime 訊號：這類欄位應在生產路徑落 log 讓問題在真實流量中自己曝光，否則 regression 復發時完全無聲——2026-07-31 bridge 的 lateCreates 實證
- [f_e92697] [2026-07-31T13:46:56.962Z] 在原本全同步的路徑中插入一個 await 就等於自己開了 finalize/cancel race 縫（2026-07-31 bridge F1 實證）：coalesceAsyncRunner 的 isCancelled 只在入口與補跑前檢查，fn 執行中翻轉完全攔不住，所有呼叫端的入口 guard 看起來像已保護到其實一個都擋不住 mid-run；修法是 await 回來後對 finalize flag 再檢一次，這類缺陷在型別、既有測試、API 回傳值上全都看不出來
- [f_5d0939] [2026-08-06T05:58:24.822Z] telegram-kiro-bridge 的 `npx tsc -p .` 在 noUnusedLocals 報 TS6133 時仍然會 emit dist，所以「tsc 紅了 = dist 沒更新」這個假設在此 repo 不成立——做突變測試時一律要 grep dist 確認突變真的進了產物才採信 smoke 結果，不可用 tsc 的 exit code 反推（2026-08-06 Fable5 覆核順帶發現；同一天我另外踩到反向的坑：突變寫成 `if (false && …)` 讓 tsc 型別收窄而編譯失敗、dist 沒更新，smoke 跑的是舊產物假綠）。
- [f_c4f291] [2026-08-06T23:38:37.267Z] 2026-08-07 方法論教訓：GitHub tree API 的 ?recursive=1 回應被截斷時，WebFetch 背後的小模型會對「存在性」問題自信地答 no——當天它連答「無 pyproject.toml／無 paulsha_cortex/／無 tests/」，一度讓我推論出「這個 repo 只有文件沒有程式碼」，足以推翻整份評估。翻案手法是直接打 raw.githubusercontent.com 的檔案 URL 當二元探針（存在→回檔案內容，不存在→404: Not Found），這個訊號不經摘要判斷、抗幻覺；列子目錄改用 git/trees/main:&lt;path&gt;（不遞迴、JSON 夠小不會截斷）也可靠。∴ 對「某某東西不存在」這類否定式主張，永遠要用探針覆核而非採信摘要——這是既有 research-report-citations-unverified 教訓（引用越像真的越要先查）的反向補完。
- [f_e88354] [2026-08-11T19:26:07.672Z] 拿本 repo 的碼片段當「找 bug」fixture 時，註解本身就是答案洩漏：本 repo 註解密度高、幾乎每個不變式旁都寫了為什麼，2026-08-12 的模型對照實驗中 5 次命中全部落在有註解點出不變式的題目、註解乾淨的兩題兩臂皆 0。∴ 設計這類 fixture 要至少各半（有/無註解洩漏）並分開計分，否則量到的是「會不會讀註解」而不是「能不能推導缺陷」；同理，用註解密集的碼去評估覆核者能力會系統性高估它。
- [f_8a90df] [2026-08-11T19:52:52.581Z] 設計「剝註解」對照組時不要留行號空洞：2026-08-12 的 fixture 保留原始行號、只抽掉註解行，結果行號變不連續，兩個模型都把空洞讀成「有程式碼被刻意隱藏」並開始推測那幾行的內容（S7 那題 sonnet 直接虛構「行 289-290 是 rawSteps 的初始化」並據此放棄作答）∴ 剝註解組的漏報被系統性放大、與「沒有註解可讀」混在一起無法分離。下次要嘛剝完重新連續編號，要嘛用等長空白行占位並在 prompt 說明。
- [f_ea64e9] [2026-08-11T23:30:21.616Z] 2026-08-12 量到 Kiro 上 code-review 模型評測的 test-retest 翻轉率：同一批 8 題 orig fixture、同 prompt、零改動重跑一次，16 個 cell 翻了 4 個（25%），sonnet-4.6[max] 4/8→6/8、opus-4.5 3/8→5/8，且四次全部同方向（新批次較高，純隨機同向機率 0.125，無法區分是運氣還是伺服器端批次效應）。⇒ n=8 的一臂光噪音就有約 ±1.4 題擺盪 ∴ 先前所有「有註解 vs 剝註解」「sonnet vs opus」的差值都落在噪音帶內、不能當訊號讀。任何拿 n≤8 fixture 比較模型或條件的實驗，必須先跑一次零改動重跑量翻轉率當底噪，否則量到的是噪音。資料在 G:\AI\AIMemory\artifacts\arm-test-2026-08-12\（含 ANALYSIS.md 與 64 筆逐字回答）。
- [f_3f5340] [2026-08-12T00:31:53.092Z] 2026-08-12 行為測試軸對照（同一組 8 個缺陷，模型冷讀 vs repo 既有 mutate-gate 閘門）：閘門 8/8 killed 且每條都紅在目標 check；模型按站點的命中率是 0/8 到 8/8 不等。⚠️ 這**不能**宣稱行為測試比模型會找 bug（閘門是為這些變異寫的、模型是冷讀，8/8 是構造上的），能宣稱的是「對**已枚舉**的缺陷，行為測試給確定性偵測，模型給 0–100% 外加 25% run-to-run 噪音」。可操作判準有兩條：①缺陷若「與標準樣板同形但參數處理被動過手腳」（實例 `const max = Math.max(1, Math.floor(limit) || 1)` → `const max = limit`），模型覆核期望值是 0——16 個回答全漏且全部在同一檔案誤報另一個不存在的缺陷，加派覆核者不會改善（同源天花板）∴ 這類不變式**必須**有行為閘門；②「碼內自相矛盾」（相鄰三行用不同陣列、計數器只增不減）模型 8/8 全中，是覆核甜蜜區、不必優先寫閘門。
[End specialist context]

[Persistent memory — lessons from your previous tasks]
- [2026-07-09T03:48:10.729Z] (目標與動機：用 uk-slot-codegen skill（位於 ~/.kiro/skills/uk-slot-code) [auto-summary] 覆寫修正後最終 Game_Define.ts 正確，但 spec_adapter 本身需修正。
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) 審查 uk_slot_clash_of_olympus M2.2 VS proto mock adapter 設計：建議把轉換邏輯放在 VSManager.ts 內的純函式（保持 ts-node 可測），並發現現有 GameView mock 有兩處會讓 Resolve() 恆不觸發的 bug，需與 adapter 一併修正
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) AdaptRoundToVSInput() 應為 VSManager.ts 內的 exported pure function（type-only import colProto），VsFeatureShowState 只做呼叫+播放+plateAfter 寫回顯示層
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) GameView.ts:908-912 的 vsfeature mock：col0 用轉型後符號 VsCollect(18) 而非 Collect(15)、VSResult 缺 reelIndex，兩者疊加會讓 VSManager.Resolve() 恆回傳 isTriggered=false
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) VSManager.Resolve() 回傳的 plateAfter 目前沒有任何寫回顯示盤面或 CollectFeatureShowState 的機制，是 M2.2 必須釘的整合缺口
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) proto IVSResult.vsType 為 number，其編碼語意（symbol id vs 獨立 enum）未定案，僅有 mock 先例可循，應登記 spec-gap
- [2026-08-13T11:55:52.858Z] (目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS pr) M2.1 設計文件（安全略過）與 dev-spec.md 規格權威 S1（warn 不改行為）對「類型不符」措辭不一致，雖因欄位互斥實務不會觸發，仍建議對齊文件用字
[End persistent memory]

[Artifact output]
任務完成後，在回覆最末附一個 JSON block 供系統存檔：
```json
{"type":"artifact","summary":"一句話摘要","outputs":[{"type":"finding","content":"..."}],"files_modified":[],"tags":["tag1"]}
```
outputs.type 可用：finding, code_change, recommendation, analysis。
tags 用英文小寫。如果任務失敗或無有意義產出，不需要附。
[End artifact output]

[Memory recall — dynamically retrieved facts relevant to this message]
[uk-slot-codegen] (relevance 0.58)
- 2026-08-12 uk_slot_clash_of_olympus codegen 完成（G:\Cocos_Project\uk_slot_clash_of_olympus，finalize gate 38 檢查 0 失敗、tsc 專案 diagnostics 0）。三個可重用的技術教訓（都是主 agent 接手修 65 個編譯錯誤時實查出來的）：①**`import protocol from "./Proto"` 的 default import 不能當 namespace 型別用**——寫 `protocol.<ns>.IRoundInfo` 會噴 TS2503，本次一口氣 60 處（RecoverSpinAck 43／SlotReels 13／ReelDevTool 4）。修法是補 `import type { <ns> } from "./Proto"` 並只改型別位置；⚠️**值位置（`new protocol.<ns>.SpinAck()`）必須保留**，Proto.ts 刻意用 default export 保住 CJS runtime object，誤改會編譯過但執行期 undefined ∴ 不可全域字串取代，要依 tsc 回報的精確 (line,col) 動刀。②**proto stub 的 `.d.ts` 會與 runtime `.js` 失步**且失步位置不對稱：本次 CollectResult/VSResult/JPResult 在 `.js` 有 prototype 預設值、`interface IRoundInfo` 也有（型別 any[]）、只有 `class RoundInfo` 缺 → TS2339 報的是 class，若只 grep interface 前幾十行會誤判成「interface 缺」而插錯位置（我就插錯了一次，撞出 TS2300 duplicate identifier）。③**mock 的實際形狀才是有效契約，不是 dev-spec proto 映射表的推測形狀**——本次 CollectResult 實際是 `{col, cashPositions:[{col,row,value}], totalWin}`，映射表寫的是 `{collectPositions, cashPositions:number[], jpPositions}`，照映射表寫 .d.ts 會讓 GameView mock 整批型別錯。另：gate_runner 的 3.4 `Mock_symbol_effect_data` regex 要求 `AwardDataVec:`（物件字面值形式），`round.AwardDataVec = [...]` 屬性指派**永遠過不了**，必須用具名 typed literal（這也正是 skill Step 3.4 規則 7「加 type annotation 讓 TS 攔缺欄位」的原意）。
- uk_slot_clash_of_olympus 的 M0b（Editor/Runtime 驗證）已於 2026-08-13 全綠：五項全過（Preview、SkeletonData 綁定、EffectPlate 19 份、熱鍵 1~8、Mask contentSize 含目視），scratch/codegen-report.md 的風險 1「執行期行為完全未驗證」降級；但綠燈邊界僅止於「骨架不會斷」不等於「功能會動」——PlayVsFeature()／PlayCollectFeature() 仍是空 stub、JP 無專屬演出、報獎跑分未串接

[uk-917] (relevance 0.55)
- 使用者要求 codegen 產出的老虎機專案不可 commit AI 相關目錄（.kiro 等）與 docs 目錄；正確追蹤範圍照 uk_917 的 .gitignore 而非模板（模板不是出貨形態，自己 track 著 .kiro/ 24 檔）

[uk-872-eyestrike2] (relevance 0.52)
- uk_872_eyestrike2_client 的 FeatureWheel 停輪曲線量化事實（A 級：原型 v2 的移植常數與 FeatureWheelManager.ts:216-258 的七個 readonly 逐一比對相符——4.5s / 0.75s / 10% / 20% / 1% / 0.25s / 0.3s）：用該曲線算出「主曲線時間走到 85% 時，距離已經跑完 99.5%」∴ 最後 15% 的時間只走 0.5% 的角度——這就是輪盤「看起來早就停了但還沒亮」的成因，元凶是 SPEED_CURVE_SLOW_SPEED_RATIO=0.01；把它拖到 20% 時同一時點是 92.8%。調參用原型 G:\Cocos_Project\uk_872_eyestrike2_client\.claude_temp\wheel-click-prototype.html（v2 起現況版九格常數全開成滑桿、預設＝專案現值、附「回到專案現值」鈕）。
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[codegen-git-init-gap]] (relevance 0.81)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/codegen-git-init-gap.md]
- 1. 缺口的形狀
- 2. 修法：Step 0.2 + 機械閘門
- 3. UK slot 專案的 git 追蹤慣例（實查，非推測）
- 4. 五輪異源覆核抓到的 12 條
- 5. 順帶回報但未動的既有問題
- 相關

## [[uk-slot-clash-olympus]] (relevance 0.77)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/uk-slot-clash-olympus.md]
- ⚠️ 本頁曾長期過時（2026-07-17 → 2026-08-12 才修正）
- 概述
- 開發進度
- 機制分類（2026-08-12 codegen 驗證版）
- 規格缺口 → 專案內的 `docs/spec-gaps.md`（2026-08-13 起唯一真相源）
- spec-to-impl 教訓（仍成立）
- Cocos prefab 踩坑（2026-08-12 M0b 實證）
- 相關
[End wiki retrieval]

[Delegation Task — id: moaplan_state_review]
Goal: 請 code review G:\Cocos_Project\uk_slot_clash_of_olympus 目前未提交的 M2.2 變更，集中審查 assets/Script/GameState/VsFeatureShowState.ts、CollectFeatureShowState.ts、GameView.ts。目標：驗證 VS 轉型後顯示盤面沒有改寫 RoundInfo.MainPlateSymbol、VSResolveResult 交接不跨局、mock 可觸發真正 Resolve。已知：M2.1 VSManager 是純函式，UnshowPrepareState 模板 TODO 不在本切片。驗收：只回報可重現的 High/Medium finding；無則明說。回報格式：findings（含檔行與修法）、通過項、殘留風險。
Context: 此工項屬於計畫「對 Clash of Olympus M2.2 已實作的 adapter、VS state、Collect state 與 mock 進行獨立品質審查，確認沒有違反轉型前盤面、不重算業務規則與 fail-safe 邊界。」。

Complete this task. When done, summarize what you accomplished.
[結構化結果 — 必要步驟]
完成後**呼叫 structured_output 工具**繳交下列欄位（不是把 JSON 印在回覆裡，
那樣下一步收不到）：
  - findings: array
  - passed: array
  - risks: array
文字回覆照常寫（人會看），structured_output 是額外的一步，不是取代。

---

**slot-dev:**
I'll start by reading the target files to review the M2.2 VS Feature changes.All 9 unit tests pass. Now let me verify TypeScript compiles cleanly and check a couple more integration edge cases (the `Game_Define.FEATURES.VS_FEATURE` flag and colProto type shapes).Good — `IVSResult.reelIndex?` exists in the proto stub, confirming the previously-flagged "VSResult 缺 reelIndex" gap is resolved and the adapter's field access is type-correct. Now let's run the TypeScript compiler to confirm no type errors were introduced.No type errors in the reviewed files (the noise is pre-existing Cocos editor typings noise, unrelated to this change). Let me check one more integration detail: `AwardState` and whether `RoundWin`/`AwardDataVec` payout math double-counts VS-transformed cells versus the mock's separate `RoundWin` field.I've completed the review. Let me load the structured output tool and submit the findings.## 審查結論：無 High/Medium finding

針對 `uk_slot_clash_of_olympus` 目前未提交的 M2.2 變更（`VsFeatureShowState.ts` / `CollectFeatureShowState.ts` / `GameView.ts` + 新增的 `Feature/VSManager.ts`），逐項驗證任務指定的三個驗收點，全部通過：

1. **RoundInfo.MainPlateSymbol 未被改寫** — VSManager 在 adapter 層與 Resolve() 層各做一次 cell 級深拷貝，`GameView.ApplyVsPlate()` 只把轉型後盤面寫進 `m_slotReels.SetPlateInfo()`（顯示層），從未觸碰 `this.RoundInfo`。
2. **VSResolveResult 交接不跨局** — `SetNowRoundInfo()` 新增的 `this.VsFeatureResult = null` 在目前唯二會被呼叫的路徑（`OnRecvSpinAck` 首輪、`SpinState.OnEnter` 的 FreeGame 分支）都先執行才進 VS 狀態，不會殘留上一局的值。
3. **mock 可觸發真正 Resolve()** — 逐行手動追蹤 `'vsfeature'` mock 資料流過 `AdaptRoundToVSInput → VSManager.Resolve`，確認 `isTriggered=true`；這修正了上一輪設計審查抓到的兩個 bug（VSResult 缺 reelIndex、col0 誤用轉型後符號）。另外實跑 `tests/VSManager.test.ts` 9 案例全過，`npx tsc -p . --noEmit` 篩選這三個檔案 0 錯誤。

殘留風險（均非本切片範圍內的 bug，僅記錄供後續實作留意）：
- RespinGame 的模板 TODO 若未來實作、且繞過 `SetNowRoundInfo`，`VsFeatureResult` 可能跨局殘留——目前該路徑整段被註解、不可達。
- `CollectFeatureShowState` 仍是 stub，日後串接時 `collectWins.reelIndex` 與 `CollectResult.col` 需顯式對應，不能假設欄位互通。

---

