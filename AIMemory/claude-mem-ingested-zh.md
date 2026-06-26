# claude-mem 精選寫入紀錄(繁中,供事後抽查)

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
