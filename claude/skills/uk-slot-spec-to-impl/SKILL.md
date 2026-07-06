---
name: uk-slot-spec-to-impl
description: 當拿到一份 UK 老虎機遊戲規格書（xlsx）要開發新遊戲、使用者說「從規格書實作」「開新的 slot 專案」「規格書轉開發規格」、或要為新遊戲起專案/拆任務時使用。涵蓋 xlsx 轉換、差異開發規格、milestone 任務拆解三步驟。
type: skill
domain: slot
created: 2026-07-06
tags: [uk-slot, spec, workflow, milestone]
source: session
---

# uk-slot-spec-to-impl

從遊戲規格書（xlsx）到程式實作的完整工作流程。UK slot 每款遊戲都從
`uk_slot_template` 複製起新（**不是 git fork，不保留模板 git history**），
實際工作量只有「規格 − 模板」的 delta，所以核心產出是**差異開發規格**。

## 流程總覽

```
xlsx 規格書
  │ 步驟1 excel-to-ai-doc
  ▼
docs/spec/（markdown + 圖 + metadata）──🔍 檢查點1（人工）
  │ 步驟2 差異分析
  ▼
docs/dev-spec.md（差異開發規格）────────🔍 檢查點2（人工）
  │ 步驟3 任務拆解
  ▼
SPEC.md（milestone 任務清單）→ 實作 → 驗證
```

⛔ 兩個人工檢查點不可跳過——源頭理解錯誤會被整條 pipeline 放大。

## 產出物慣例（全部進版控）

| 位置 | 內容 | 產生於 |
|------|------|--------|
| `<game>/docs/spec/` | 規格書 markdown + 抽出圖片 + metadata.json | 步驟1 |
| `<game>/docs/dev-spec.md` | 差異開發規格（功能分類 + proto 映射） | 步驟2 |
| `<game>/SPEC.md` | milestone 任務清單（checklist，做完打 [x]） | 步驟3 |
| `<game>/AI.md` | 照 uk-slot-project-docs 慣例持續更新 | 全程 |

## 步驟 1：規格書轉換

用 `excel-to-ai-doc` skill 把 xlsx 轉成 AI 可讀結構，輸出到 `<game>/docs/spec/`。

**檢查點 1（請使用者過目）**：圖片有沒有漏抽、賠付表數字對不對、
關鍵玩法圖是否對應到正確章節。

## 步驟 2：差異開發規格（核心）

輸入四樣：`docs/spec/` + `uk_slot_template` 現碼 + `uk-slot-pattern-library` +
proto d.ts（若已發佈）。產出 `docs/dev-spec.md`，含兩張表：

### 功能分類表

規格書每個功能標一類：

| 分類 | 意義 | dev-spec 裡要寫的 |
|------|------|------------------|
| 🟢 模板已有 | Standard/Cascade/Tumble、基本 UI 等 | 只列設定值 |
| 🟡 有既成模式 | ExtraBet、FakeReel、狀態機等 | 標對應 skill 名 |
| 🔴 本作特有 | 新機制（如能量收集、輪盤選獎） | 附一段迷你設計 |

🔴 清單就是真正的工作量所在。

### proto 映射表

功能 ↔ proto 欄位對照。**proto 未發佈時**：整表標 ⏳，每項記錄
「假設的資料形狀」，proto 到手後回來逐項核對假設，不符就修 dev-spec。

**檢查點 2（請使用者過目）**：🔴 清單有沒有漏、分類有沒有錯、proto 假設合不合理。

## 步驟 3：Milestone 任務拆解

寫入 `<game>/SPEC.md`，骨架按依賴排序、milestone 內按機制垂直切：

| Milestone | 內容 | 前置 |
|-----------|------|------|
| M0a | 起新專案（見下方步驟） | — |
| M0b | proto 接通，能 spin 出 server 結果 | proto 發佈 |
| M1 | Base game 可玩（轉輪表演、贏分、基本 UI） | M0b |
| M2 | 特色機制：每個 🔴 一個任務 | M1 |
| M3 | Polish（NearMiss、音效、動畫細節） | M2 |
| M4 | 收尾（多語系 sync、全流程 replay、賠付核對） | M3 |

規則：
- 每個任務帶三要素：**規格出處**（spec 章節）、**對應 skill**（🟡 類）、
  **可驗證的驗收標準**
- **每個 M2 機制的驗收標準必含該機制 unshow/replay 還原**——不要留到最後一次補
- proto 晚到時 M0a + 🔴 機制設計可先行，M0b 之後的實作等 proto

### M0a 起新專案步驟

```
1. git archive（uk_slot_template HEAD）→ 解到新專案目錄
   git -C <模板目錄> archive HEAD | tar -x -C <新專案目錄>
   （只帶版控內容；gameSetting.json / Tools_SlotSetUP 會一起帶到）
2. git init → initial commit（全新 history，不帶模板 log）
3. 執行 Tools_SlotSetUP/FirstClone.bat
   （讀根目錄 gameSetting.json，clone slotExtensions-client 到 extensions/，
    即 Astarte framework，獨立 repo、不進遊戲 repo）
4. npm install
5. 改 GameId / ShortGameName / 盤面 / FillStrategy 設定
```

## 相關 skills

| 階段 | skill |
|------|-------|
| 步驟1 | excel-to-ai-doc |
| 步驟2 | uk-slot-pattern-library |
| M0a 後進專案 | uk-conventions（寫入專案 CLAUDE.md）、uk-slot-project-docs（建 AI.md） |
| M1~M2 實作 | uk-slot-state-machine、uk-slot-extrabet、uk-slot-fake-reel-manager |
| M4 | uk-slot-multilang-sync |

## 常見錯誤

- ❌ 用 git clone/fork 起專案 → 會帶入模板 history；一律 git archive + git init
- ❌ 把整份規格書當實作範圍 → 先做差異分析，只實作 delta
- ❌ 跳過人工檢查點直接往下走 → 源頭錯誤全線放大
- ❌ unshow/replay 還原留到專案尾聲 → 放進每個機制的驗收標準
- ❌ proto 假設寫完不回頭核對 → proto 到手後必須逐項驗證 ⏳ 項目
