# claude-mem 精選寫入紀錄(繁中,供事後抽查)

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
