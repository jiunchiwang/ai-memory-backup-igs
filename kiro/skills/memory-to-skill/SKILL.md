---
name: memory-to-skill
description: 當使用者要求「檢視 session 資料夾並把內容整理成 skill」、需要從過去對話中抽取可重用模式、或要把剛剛完成的工作經驗固化成 skill 時使用
---

# Memory to Skill（把對話記憶整理成 skill）

## 概述

把 `${MEMORY_DIR}/sessions/` 資料夾裡的對話記錄掃過一遍，抽出可重用的技術/模式/參考，寫成符合 writing-skills 規範的 SKILL.md，**先比對已安裝的 `ms-` skill、有重疊就 append/rewrite 而不是新建**，最後把處理過的 session 檔搬到 `${MEMORY_DIR}/oldSessions/`。

核心原則：**事後整理（retrospective），不是 TDD；但產出必須符合 writing-skills 的格式規範；絕不重複建立已存在的 skill。**

### 路徑變數（重要）

所有路徑都寫成 `${MEMORY_DIR}` / `${SKILL_DIR}` / `${USER_ID}`，**實際值由 bridge 的 Environment preamble 注入**——你在每次 session 開頭看到的 `[Environment — machine-specific paths...]` block 會列出這三個值。動手前先從那個 block 讀出真值再開工。

典型值（不同機器不同）：

| 變數 | Kiro 這台範例 | Codex 那台範例 |
|---|---|---|
| `${MEMORY_DIR}` | `F:\AI\AIMemory` | `F:\AI_Codex\AIMemory` |
| `${SKILL_DIR}` | `C:\Users\tonykuo\.kiro\skills` | `C:\Users\user\.codex\skills` |
| `${USER_ID}` | Telegram user id 數字 | 同左 |

**找不到 preamble 環境值**（例如有人重跑老 session 沒注入）時，當成錯誤回報給使用者，不要腦補預設值動手。

## 何時使用

- 使用者明確要求「檢視 session 資料夾」、「把對話整理成 skill」、「這次經驗寫成 skill」
- 累積了多個 session 後想盤點可沉澱的知識
- 剛完成一段工作，要把經驗固化成可跨專案重用的指南

**不要用在：**
- 使用者只問問題、沒有要求整理成 skill
- 內容只對單一專案有意義（寫進專案 CLAUDE.md 或 README 比較對）
- 一次性解法、偏好設定、環境資訊（該進 `facts-<userId>.md`，不是 skill）

## 與 writing-skills 的關係

writing-skills 要求 **「No skill without a failing test first」**（TDD-for-docs）。本 skill 是**事後抽取**路徑，並行但不衝突：

| 維度 | writing-skills | memory-to-skill |
|---|---|---|
| 時機 | 發現新模式時、主動創作 | 事後盤點 session |
| 驗證 | 用 subagent pressure scenario 做 RED → GREEN | 以「已在真實對話中被反覆使用」作為事後驗證 |
| 適合的 skill 類型 | discipline-enforcing、technique | reference、已證實的 pattern |

產出仍必須符合 writing-skills 的**格式**（YAML frontmatter、`Use when...` description、sections 結構）。差別在於「測試」這一關用「這個 pattern 是否在 session 中反覆出現並解決了真實問題」來取代 pressure scenario。

## 完整流程

```
1. 掃 sessions/ 資料夾 → 識別可重用模式
2. 篩選候選（跨專案有價值？不是一次性？不是專案特定？）
3. 對每個候選 → 比對已安裝的 ms- skill
   ├─ 無衝突 → 新建 ms-<name>/SKILL.md
   ├─ 有部分重疊 → append 到既有 skill（新踩的坑/補充小節）
   └─ 既有內容過時或錯誤 → rewrite 整份
4. 把處理過的 session 檔搬到 oldSessions/
5. 向使用者回報：建了哪些、更新了哪些、搬了哪些檔
```

## Step 1 — 掃描與識別

### 讀檔策略

- 先 `list` sessions/ 取得檔名與大小
- **大檔優先**（>10KB 通常含完整討論，小檔可能只是問候）
- 批次讀（一次 2–3 個檔），不要一個一個讀

### 可成為 skill 的訊號

| 訊號 | 範例 |
|---|---|
| 「踩到坑 → 解釋根因 → 修正」的完整循環 | Windows 盤符根 prefix bug |
| 「為什麼不能用 A，改用 B」的替代方案討論 | ACP 無法自訂 method → 用 text token |
| 反覆在不同 session 出現的設計決策 | facts.md preamble 注入一次 vs 每 turn |
| 明確的「這個方法是 pattern，可以跨專案」 | file-based long-term memory |

### **不該**成為 skill 的內容

- 一次性除錯（「本次 build 失敗因為 npm cache」）
- 環境設定（寫進 `facts-<userId>.md` 或專案 README）
- 純事實問答（「Kiro CLI 支援哪些指令」）
- 個人偏好（繁中、語氣風格）

## Step 2 — 候選篩選（門檻要高）

對每個候選問四個問題，都是 yes 才做：

1. **跨專案有價值嗎？**（不只對 telegram-kiro-bridge 有用）
2. **有學習成本嗎？**（不是看文件就會的標準做法）
3. **我會再參考嗎？**（還是這輩子只碰一次）
4. **有具體可操作的內容嗎？**（能寫出 code pattern / 決策表 / 陷阱清單）

寧可少寫一個 skill，不要濫建。

### Confidence Scoring（量化門檻）

四個問題通過後，用信心分數做最終裁決。分數由兩個維度算出：

| 維度 | 計算 | 直覺 |
|------|------|------|
| **頻率 F** | `min(出現次數 / 5, 1.0)` | 出現 5+ 次 = 滿分 |
| **成本 C** | `min(平均消耗 turn 數 / 10, 1.0)` | 每次花 10+ turn = 滿分 |

```
confidence = F × C
```

「出現次數」的計量來源（取最大值）：
- session transcripts 中出現同 pattern 的 session 數
- dailylog 提及次數
- facts 中相關記錄數

「平均消耗 turn 數」= 該 pattern 所在 session 的 user turn 總數平均值（估算即可）。

**門檻決策表：**

| confidence | 動作 |
|-----------|------|
| ≥ 0.5 | ✅ 進入 Step 3（正式候選） |
| 0.3 – 0.49 | ⏳ 不建 skill，`remember("pattern: <描述> 出現 N 次，score=X")` 留底觀察 |
| < 0.3 | ❌ 跳過，不記錄 |

**範例：**
- 某個 Windows shell 陷阱出現 4 次、每次花 6 turn → `F=0.8, C=0.6, score=0.48` → 留底
- 同一個 pattern 出現 5 次、每次花 12 turn → `F=1.0, C=1.0, score=1.0` → 直接進候選
- 某 API 怪癖出現 2 次、每次花 3 turn → `F=0.4, C=0.3, score=0.12` → 跳過

> 💡 靈感來源：[ECC continuous-learning-v2](https://github.com/affaan-m/ECC) 的 instinct confidence scoring。差異：ECC 用 hooks 即時觀測，我們用事後 session 掃描。

## Step 3 — 比對已安裝的 ms- skill（關鍵步驟）

**在動手寫任何新 skill 之前**，先列出 `${SKILL_DIR}/` 底下所有 `ms-` 開頭的目錄，讀每個 SKILL.md 的 YAML frontmatter。

### 比對決策流程

```
對候選 X，掃過所有 ms-*/SKILL.md：

1. 有沒有 ms- skill 的 name 或 description 直接涵蓋 X？
   YES → 進入「是否要 append/rewrite」判斷
   NO  → 進入 step 2

2. 有沒有 ms- skill 的主題雖不同但涵蓋 X 的一部分？
   YES → append 一個子小節到那個 skill
   NO  → 全新建立
```

### append vs rewrite 判斷

**預設 append**。只有以下情況才 rewrite：

| 情況 | 動作 |
|---|---|
| 既有內容和新經驗**一致但不完整** | **append** 到 Common Mistakes 或新增小節 |
| 既有範例是某個版本的做法，新經驗是**更好的版本但原版本仍有效** | **append** 一節「替代做法」 |
| 既有內容**描述的行為已過時或錯誤** | **rewrite** 該段落（保留其他段落） |
| 整份 skill 的 framing 本身就錯了 | **rewrite** 整份（罕見） |

### append 的標準位置

優先順序：

1. `Common Mistakes` 表格新增一列
2. `Implementation` 區段新增子小節
3. 新增一個頂層 `## 延伸 / 補充` 段落（最後手段）

**不要**在檔案任意處插入 — 段落順序要保持一致，未來查閱才找得到。

## Step 4 — 撰寫或更新（格式規範）

一律遵守 writing-skills 的 frontmatter 規範：

```yaml
---
name: ms-<kebab-case-name>
description: 當<具體觸發條件/症狀/情境>時使用
---
```

- `name` 必須以 `ms-` 開頭（本機 convention），其餘只能用字母、數字、連字號
- `description` 必須以「當...時使用」開頭，**只描述觸發條件，不摘要 skill 做了什麼**
- 描述要包含具體關鍵詞方便未來搜尋（錯誤訊息、症狀、工具名）

### 內容語言

**繁體中文（zh-TW）**。程式碼註解、commit message、變數名保持英文；只有 prose、section 標題、表格文字用中文。

### 標準 section 結構

```markdown
# <標題>

## 概述
核心原則一兩句話。

## 何時使用 / 不要用在
bullet list。

## 核心模式 / 完整流程
code before/after、流程圖、步驟。

## Implementation
inline code 或 link 到附屬檔。

## Common Mistakes
表格：錯誤 | 修正。

## 相關
cross-reference 其他 ms- skill。
```

## Step 5 — 搬移 session 檔

**寫完且驗證通過後**才搬。順序重要：

```powershell
# 1. 確保 oldSessions 資料夾存在
New-Item -ItemType Directory -Path '${MEMORY_DIR}\oldSessions' -Force | Out-Null

# 2. 移動已處理的 session 檔（保留 sessions/ 資料夾本身）
Move-Item -Path '${MEMORY_DIR}\sessions\*.md' -Destination '${MEMORY_DIR}\oldSessions\' -Force
```

實際執行前先把 `${MEMORY_DIR}` 替換成 preamble 注入的真值（例如 `F:\AI\AIMemory` 或 `F:\AI_Codex\AIMemory`）。

Windows cmd 的 `mkdir` + `&&` 連鎖常有 exit code 1 的問題，**用 PowerShell 的 `New-Item -Force` 最穩**。

### 為什麼搬完整個資料夾、不是個別挑

1. 已讀過就算「處理過」，即使沒抽出 skill（也是一種判斷結果）
2. 避免下次再看到又重掃一次
3. `oldSessions/` 永遠可以回頭查

## 防止重複的 ms- skill（核心保護）

**寫新 skill 前的 checklist：**

- [ ] 列出 `${SKILL_DIR}/ms-*/SKILL.md` 所有 YAML frontmatter
- [ ] 對候選主題做關鍵詞比對（不只比對 `name`，也要比對 `description` 的觸發條件）
- [ ] 有疑似重疊就讀完整 SKILL.md 確認
- [ ] 明確選定：新建 / append / rewrite 其中之一
- [ ] **寫完後再掃一次**，確認沒有新舊兩份類似的

**典型重複陷阱：**

| 陷阱 | 預防 |
|---|---|
| 命名不同但主題相同（`json-parsing` vs `llm-extraction`） | 比對 description 關鍵詞，不只比 name |
| 新寫的範圍涵蓋既有 skill 的一部分 | 把新內容拆成「既有 skill 的補充」+「真正的新 skill」 |
| 把同一個坑寫進兩個 skill 的 Common Mistakes | 固定在主題最相關的那一個，另一個用 cross-reference |

## 回報格式

做完整個流程後，給使用者一個清晰的總結：

```
✅ 完成 N 個 session 檔的整理

新建 skill：
  - ms-xxx (<size>)
  - ms-yyy (<size>)

更新既有 skill：
  - ms-zzz（append 了「<小節名>」）

未產出 skill 的 session（判斷為一次性/專案特定）：
  - session-xxx-...md（簡短理由）
  - session-yyy-...md

已搬移：${MEMORY_DIR}\sessions\*.md → ${MEMORY_DIR}\oldSessions\
```

## Common Mistakes

| 錯誤 | 修正 |
|---|---|
| 沒比對既有 ms- skill 就開始寫 | 先列出所有 `${SKILL_DIR}/ms-*/SKILL.md` 的 frontmatter |
| 把專案特定的設定寫成 skill | 專案特定 → CLAUDE.md / README；跨專案 pattern → skill |
| 一個 session 一個 skill | 多個 session 可能支撐同一個 skill；一個 session 也可能含多個 skill 主題 |
| 寫完 skill 忘了搬 session 檔 | 流程最後一步一定要搬，否則下次會重掃 |
| append 時插在檔案任意處 | 固定插入位置優先順序：Common Mistakes → 新子小節 → 頂層延伸段落 |
| rewrite 時丟掉原本仍有效的內容 | rewrite 前先判斷哪些段落仍正確，只覆寫錯的部分 |
| description 摘要了工作流程 | description 只寫觸發條件，不寫 skill 內部的步驟 |
| 用英文寫（本機慣例是中文） | prose 一律繁中，code 保持英文 |

## 相關

- **writing-skills** — skill 撰寫的格式與 TDD 方法論（本 skill 遵守其格式，但用 retrospective 取代 TDD）
- **ms-agent-long-term-memory** — sessions/ 資料夾的來源，是 agent 長期記憶系統的 archive 層
