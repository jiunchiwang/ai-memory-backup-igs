# claude-mem 提案(繁中,待核准)
> 來源:claude-mem-shortlist.md(15 筆候選)→ 精選 + 合併 → 4 條提案
> 已用 memory list_facts 對 AIMemory(53 筆)去重:無重複。
> 核准後再逐條 remember;此檔僅提案,未自動寫入。

- [ ] (ai-canonical-architecture) 跨模型 AI 知識架構 v4 核心原則:canonical corpus(精煉知識)本身即產品,以 markdown + git 為單一真實來源(G:\AI\AI-canonical);CLI/MCP/bridge/index 等只是部署基礎設施,而非產品本體。〔來源:10.3.1/2026-06-19〕
- [ ] (ai-storage-policy) AI 產物雲端 vs 本地分流政策:canonical skills、steering 政策與通用文件納入版控的共享 canonical 知識庫;session 執行 log 與框架內部狀態僅留本地、不上版控。〔來源:10.3.1/2026-06-19〕
- [ ] (async-race-gotcha) 並發群組派發(concurrent group dispatch)情境下,分支/狀態決策(如 willGhost)應在 async 階段計算,而非在 Promise.all 之前的同步階段算,否則並發 dispatch 會造成 race condition。〔來源:uk_pirates_queen/2026-06-17〕
- [ ] (cocos-ghost-slot-pattern) Cocos Layout 防跳位 pattern:移除兩項之一時改用 ghost slot「雙 active」機制,並以單一收斂點(NormalizeGhosts)統一管理 ghost 生命週期,即可同時滿足 0→1 置中、2→1 不跳位、旋轉相容,且無需更動 Layout 參數。〔來源:uk_pirates_queen/2026-06-17〕
