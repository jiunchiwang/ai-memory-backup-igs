---
name: claude-mem-curate
description: 把 claude-mem 抽出的 shortlist 精選成少量繁體中文、去重後寫進 AIMemory。當使用者說「精選/整理 claude-mem」「把最近重點存記憶」,或每日自動 ingestion 時使用。
---

# claude-mem 精選 → AIMemory(預設自動寫入)

從 `${AIMEMORY_DIR}/claude-mem-shortlist.md`(英文、`decision` 類候選)精選出**真正跨 session 可重用**的知識,翻成**繁體中文**、**去重**後**自動 `remember` 進 AIMemory**,並記錄到 ingest log 供事後抽查。預設**不需逐筆人工核准**(避免每日審查疲勞)。

`${AIMEMORY_DIR}` 預設 `G:\AI\AIMemory`。

## 步驟(預設 AUTO 模式)

1. 讀 shortlist。無候選 → 回報「無新內容」,結束。
2. **精選(寧缺勿濫)**:留架構決策、可重用 gotcha / pattern / trade-off、跨專案做法;丟一次性步驟、單檔瑣碎改動、「編譯過了」這類過程紀錄;**同主題合併**成 1–2 條;上限 **≤10**。
3. **翻繁中**:每條改寫成一句自足的繁體中文 fact。
4. **去重**:每條先用 `list_facts` 查 AIMemory,已存在 / 高度重複 → 丟。
5. **自動寫入**:逐條 `remember`(會自動分 topic / 再去重)。
6. **記 log**:把這次實際寫入的每條 append 到 `${AIMEMORY_DIR}/claude-mem-ingested-zh.md`(含日期 + 來源 project),供使用者**事後抽查**(不需每日審)。
7. 回報:本次新增 N 條並列出。

## 安全(自動模式的護欄)

- **只 ADD,不 `forget`、不刪**(自動流程嚴禁刪記憶)。
- 所有寫入都進 git-backed 的 AIMemory + ingest log → **事後可抽查、可 `forget` 修正**。
- 保守選取 + 去重 → 控制記憶膨脹。

## PROPOSE-ONLY 模式(使用者要把關時)

使用者說「這次先給我看 / 我要審」時,改為:把 ≤10 條寫成勾選提案到 `${AIMEMORY_DIR}/claude-mem-proposals-zh.md`,**不** `remember`,等核准。
