---
title: UK Slot 老虎機專案群
type: concept
created: 2026-06-02
updated: 2026-08-21
sources: [f_4cfe4c, f_be8c07, f_093bcf, f_79c118, f_967ccc, f_e8b2cf, f_991386, f_cea694, f_3f7536, f_09acc4, f_89a745, f_f4621c, f_e22204, f_9322f0, f_82c757, f_46f6e0, f_94500e, f_0b3520, f_e9bd6a, f_73183f, f_49dae6, f_4cd205, f_59bf73, f_e2665f, f_ac9912, f_98e336, f_1b276f, f_4c48e6, f_f79167, f_e84e55, f_b20c5e, f_593c2e, f_c7ce92, f_a4bcd5, f_233d31, f_0376d5, f_8a9474, f_3165ae, f_4f4b55, f_500f52, f_800551, f_ba8cc5, f_b773d9, f_6fe390, f_b13c42, f_4367fb, f_189848, f_1284be, f_b4c328, f_0af12a, f_937a50, f_4b6004, f_437274, f_e68c39, f_165cc0, f_f82ff1, f_2d697b, f_4b088c, f_4b2a6c, f_65e102, f_769e08]
---

# UK Slot 老虎機專案群

## 概述

使用者開發一系列面向 UK 市場的老虎機遊戲，基於 Cocos Creator 3.6.2 + Astarte Framework + TypeScript 技術棧。所有遊戲從共用模板 fork 而來，目前共 9 個專案（1 模板 + 7 遊戲 + 1 demo）。

## 技術棧約束

- **Astarte Framework 不可改動** — 所有專案共用的底層框架，禁止修改
- 方法（method/function）命名使用**大駝峰（PascalCase）**

## 專案清單

### uk_slot_template（模板）

- 位置：`G:\Cocos_Project\uk_slot_template`
- 性質：所有 UK slot 遊戲的複製起新來源（git archive，不帶模板 history）
- 支援三種轉輪玩法，透過 FillStrategy 策略模式切換：
  - **Standard** — 傳統滾動
  - **Cascade** — 消除天降
  - **Tumble** — 快速掉落 + 乘倍
- **2026-07-07 回灌修正**（4 commits，2026-07-22 查證已全數在 `origin/main` 上）：bgm 改註解佔位（模板不含音檔）、欄數陣列改 `Game_Define.COL` 衍生（原寫死 6 欄）、CheckPlateInfo 欄數不符改回報不 crash（對帳函式不應 throw）、ReelDevTool 修復（驅動缺失 + IDLE 就緒閘門，原版從未實測過）
- **起新專案陷阱**：`FirstClone.bat` 的 `../extensions` 相對於執行時 cwd——需在 `Tools_SlotSetUP/` 內執行，從專案根執行會 clone 到上一層

### 衍生遊戲

| 專案 | 路徑 | 主題 |
|------|------|------|
| uk_pirates_queen | `G:\Cocos_Project\uk_pirates_queen` | 海盜女王（6×5，消除連鎖+懸賞令+輪盤選獎） |
| uk_722_robinhood_client | `G:\Cocos_Project\uk_722_robinhood_client` | Robin Hood 羅賓漢 |
| uk_739_wrath_of_thunder_client | `G:\Cocos_Project\uk_739_wrath_of_thunder_client` | Wrath of Thunder 雷神 |
| uk_746_far_west_client | `G:\Cocos_Project\uk_746_far_west_client` | Far West 西部 |
| uk_slot_eye_strike | `G:\Cocos_Project\uk_slot_eye_strike` | Eye Strike 神眼奪金 |
| uk_872_eyestrike2_client | `G:\Cocos_Project\uk_872_eyestrike2_client` | Eye Strike 2（續作） |
| uk_slot_chachacha | `G:\Cocos_Project\uk_slot_chachacha` | Cha Cha Cha 拉丁舞/水果 |
| uk_917_leprechauns_pots_client | `G:\Cocos_Project\uk_917_leprechauns_pots_client` | 3 Leprechaun's Pots（開發中）→ 詳見 [[uk-917]] |
| uk_963_divine_duel_client | `G:\Cocos_Project\uk_963_divine_duel_client` | 諸神之戰 Clash of Olympus（ROW=4／COL=6，4096 Ways，希臘神話，開發中）→ 詳見 [[uk-slot-clash-olympus]]。⚠️ 舊路徑 `clash_of_olympus_demo` 與盤面寫法「6×4」都是 2026-07 那批 spec-to-impl 的錯誤記錄，2026-08-12 已實查該路徑不存在 |

## 專案文件規範

所有 UK slot 專案採用分層文件策略（skill `uk-slot-project-docs` 控制）：
- **AI.md**（索引層，≤2000 字）— 專案 meta、盤面、模組地圖、踩坑
- **docs/modules.md**（詳細層）— 每個模組的事件介面、依賴、資料流

不管改動檔案數多少，進入老虎機專案時都主動建立/更新 AI.md。

## 五節已改主場（2026-08-21）

本頁是**專案群 hub**，但下列五節長年在這裡留著一份與專屬頁重複的副本，而副本停在較早的結論——最嚴重的是 Clash of Olympus 那節仍寫「`clash_of_olympus_demo`／6×4 4096 Ways／待確認 8 項」，那個路徑 2026-08-12 已實查不存在、盤面也是反的。過時副本比沒有更糟 ∴ 刪除副本、改為指向主場：

| 原本在這裡的 | 主場 | 副本錯在哪 |
|---|---|---|
| Clash of Olympus（諸神之戰） | [[uk-slot-clash-olympus]] ＋ [[uk-slot-clash-olympus-spec]] | 路徑不存在、盤面反了、「待確認 8 項」已收斂成 GAP-01~10 登記表 |
| uk-slot-codegen 整合 | [[uk-slot-codegen]] | 主場為超集；唯一本頁獨有的「proto 慣例覆蓋」已移過去，且兩邊 spec_adapter bug 計數 5 vs 3 的矛盾已在主場明文登記為未收斂 |
| uk_slot_eye_strike 詳細 | [[uk-slot-eye-strike]] | 主場為超集（表格化 + 7 機制逐條展開 + baked path 等後續實證） |
| Spine-Viewer 插件 | [[spine-viewer]] | 主場為超集（含 Batch Scan／DrawCall 模擬／Editor.Message.send 踩坑） |
| spec-to-impl 教訓補充（2026-08-18） | 「規格圖是 A 級證據」→ [[uk-slot-clash-olympus-spec]]；「跨專案搬 Spine 資產」→ [[uk-slot-pitfalls]] 第 13 條 | 兩條是不同層級的知識混在同一節：一條是該專案的規格裁決，一條是跨專案驗收通則 |

⚠️ 下方〈spec-to-impl 流程教訓（2026-07-09）〉**刻意保留**——那是流程層通則（回饋進 skill 正本的 5 條偏離），不是專案細節。

## spec-to-impl 流程教訓（2026-07-09 實證）

Clash of Olympus 實作過程暴露 5 個流程偏離，已回饋改善 skill 正本（commit 14887cd）：

1. 拿到規格書必須先 invoke skill 從步驟 0 開始，不可直接提方案
2. 基準永遠是 `uk_slot_template`，衍生品只當「最近似參考」
3. 步驟 2 必須讀 `uk-slot-pattern-library` 索引，否則會重複設計已驗證模式
4. 新增步驟 0 前提確認 checklist + 步驟 2 前置 4 項 gate
5. AI.md 綁定步驟 1 完成時建立

## 開發參考文件

- uk_872_eyestrike2_client：`.claude_temp/proto參數說明.md` 記錄 `ar2es2Proto.d.ts` 的欄位用途與值域，作為 proto 協議開發參考

## 架構規範

- **uk_872_eyestrike2_client**：Spine 動畫一律透過 **SpineKit** 播放（統一的 Spine 播放架構），不直接操作底層 spine 元件。

## 待優化項目

- uk_slot_eye_strike：`MultiplierManager.m_downEffectSpine` 的 Idle 動畫實際靜止，可優化為靜態圖 + 隱藏 Spine 省效能
- uk_pirates_queen：懸賞令（WantedPoster）退場時 `cc.Layout` 瞬間重排視覺突兀，需改為動畫過渡

## 回灌工作流

在衍生遊戲修到的問題依層級回灌到不同位置：

| 層級 | 回灌目標 | 範例 |
|------|---------|------|
| 模板級（工具/守衛/寫死值） | `uk_slot_template` repo | ReelDevTool 修復、欄數陣列改 `COL` 衍生 |
| 流程級教訓 | AI-canonical-corp skill 正本 | spec-to-impl checklist 強化 |
| 專案級踩坑 | 專案 `AI.md` | 特定遊戲的已知坑 |
| 模式級修正 | `uk-slot-pattern-library` 卡片 | 已驗證的設計模式 |

## 模板音訊慣例

`MG_Bgm` 與 `FG_Bgm` 背景音樂引用在模板中先**註解掉**（模板不附實際音檔）。新遊戲專案需要 BGM 時再解除註解並補上音檔。

## Skill 管理

- `AI-canonical-corp` 的 slot skill（如 `uk-slot-pattern-library`）透過 **junction** 直接指向正本目錄，改正本即時反映到 `~/.kiro/skills/`，不需額外跑 `sync.ps1`
- `uk-conventions` 是 Claude Code **custom command**（`/uk-conventions`），不是 skill
- `skill-usage.json` 追蹤檔會孤兒化：曾出現 `vc-uof-hours` entry 仍指向已改名的資料夾 `igs-uof`，而 `igs-uof`、`uk-slot-logo-localization` 兩個實際存在的 skill 資料夾卻沒有登記 usage entry——改名/新增 skill 資料夾後記得回頭核對這份追蹤檔

### uk-slot-pattern-library 維護要點

**新增卡片需同步三處**，否則資料不一致：
1. `patterns/xxx.md` — 卡片本體
2. `SKILL.md` — 索引表（+ 橫切機制表）
3. `pattern-library-overview.html` — 內嵌 `PATTERNS` JS 陣列與**兩處寫死計數**（line 50 subtitle 與 line 53-54 stat-box）

**overview.html 參考專案計數慣例**：`PATTERNS` 陣列 unique refs 扣掉「框架 xxx」條目、不去重 wrath 的兩種寫法（2026-07-30 用 `git show` 舊檔重算驗證與舊 subtitle 精確吻合）

### uk-slot-logo-localization 語系清單

標準語系代碼共 24 個（不含 cn/en）：
- 2026-07-29 新增：`urIN`（烏爾都語印度）

## 公司 AI 知識庫設計決策

UK 助理知識包專案（2026-07-28）定案的資料分區策略：

| 區域 | 決策 | 理由 |
|------|------|------|
| **B 區**（規格書結構） | 寫常見模式，非固定規範 | 每案 sheet 命名不同 |
| **D 區**（Astarte Framework API） | 只寫概要層（class + 生命週期 + 事件列表） | 不進到 method 簽名，避免過度細節 |
| **E 區**（通用機制模式庫） | 全角色統一用索引版 | pattern 名稱 + 一句話描述，不塞 158KB 完整 pattern-library |

## 錯誤紀錄分類法

記錄 AI 反覆失誤時，分成兩類：

| 類型 | 定義 | 修法 |
|------|------|------|
| **流程偏離** | 工作流順序失誤（跳過 checklist、基準拿錯） | Gate / 流程強制 |
| **技術錯誤** | 實作層面失誤（型別/邏輯/命名寫錯） | 測試 / 檢查 |

兩類根因不同，分開列並各附 session 實證。此分類法可推廣到任何 skill 或 knowhow 庫。

## 異源覆核在文件層的價值（2026-07-30）

異源覆核在「文件層自我一致性」上最有價值——這類問題同源自審結構上抓不到：

- **數字沒回頭同步**：overview.html 新增 pattern 卡片後忘記改 subtitle 計數
- **枚舉半途而廢**：列舉清單只改一半
- **同頁多處寫死計數只改一處**：line 50 改了 line 53-54 忘改

自審驗的是「我改的那處對不對」而非「還有沒有別處」，pattern-library #26 卡片實證此類問題需異源覆核才能可靠抓出。

## 事件還原（unshow / replay）兩條通則（2026-07-30，uk_917 BOMB event 實證）

這兩條是設計任何「事件疊加在盤面上」的 feature 時都會踩到的，不限 uk_917：

1. **重入防護要查下游狀態，不要另設旗標。** pre-stop gate 是否已執行，改用 `BombBoard.HasEventBombs()` 這類「已註冊結果」的查詢來判斷——狀態源唯一，unshow/replay 還原時才不會與實際盤面脫節。另設一個 `m_hasRun` 旗標的話，還原路徑一定有一條忘記重設。
2. **時序保真：原始事件的觸發時機必須原樣保留。** during-spin 觸發的 BOMB **不可**為了實作方便降級成 after-stop，否則還原畫面與原始 spin 的表現不一致。

詳細的 feature 輪廓見 [[uk-917]]。

## 重要設計模式

### Ghost Slot 雙佔位機制

Cocos 版面在「兩項移除一項」時避免置中跳動（snap），使用 ghost slot：item root 佔 Layout 格但 Content 設 `active=false`。同時滿足 0→1 置中、2→1 不跳動、旋轉相容，不需改動 Layout 參數。

### 並發 Gotcha

在 `Promise.all` 之前的同步階段計算狀態決策（例如 `willGhost`），會與並發 group dispatch 產生 race condition。解法：把這類決策移到 async 階段計算。

## 相關

- [[bridge-project]]（開發工具鏈的一部分）
- [[uk-917]]（同期開發中的專案）
- [[uk-slot-pitfalls]]（踩坑經驗，含 codegen 來源 5 條）
