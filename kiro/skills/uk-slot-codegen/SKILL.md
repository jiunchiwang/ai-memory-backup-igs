---
name: uk-slot-codegen
description: UK slot 開發統一入口。從規格書（xlsx）到可跑專案的全流程：規格轉換→差異分類→milestone 拆解→自動骨架生成→gate 驗證。使用者說「從規格書開新 slot」「規格書轉開發」「開新的 slot 專案」「跑 codegen」時觸發。
---

# UK Slot Codegen

統一 pipeline：`xlsx → AI 可讀規格 → 差異開發規格 → 骨架生成 → Validation → M2+ 實作`

## 流程總覽

```
Pre-0: 前提確認（規格路徑 / 輸出目錄 / 模板來源 / proto 狀態）
  │ ⚠️ 差異分析基準永遠是 uk_slot_template，不是衍生品
  ▼
xlsx 規格書
  │ Pre-A: excel-to-ai-doc（必跑）
  ▼
docs/spec/（markdown + 圖片）──── 🔍 檢查點1（人工）
  │ Pre-B: 差異分類（pattern-library）
  ▼
docs/dev-spec.md ──────────────── 🔍 檢查點2（人工）
  │ Step 0~5: 無頭骨架生成 + 編譯 Gate + Report
  ▼
可編譯的 Cocos 專案（Mock server、placeholder）
  │ Post: M2+ milestone 實作指引
  ▼
完成
```

⛔ 兩個人工檢查點不可跳過——源頭理解錯誤會被整條 pipeline 放大。

「不可跳過」指的是**必須逐項輸出檢查結果**，不是停下來等使用者回話：codegen 是無頭
pipeline，一口氣跑到 Step 5，檢查點的逐項輸出改收進 Report 的「人工檢查點待確認」
區塊供事後把關。格式見 `_flow.md` Pre-A / Pre-B。

## 三種模式

| 模式 | 觸發 | 行為 |
|------|------|------|
| `new` | 目標路徑不存在或空 | 完整 pipeline（Pre-A → Step 5） |
| `update` | 目標已有 codegen 產物（含 anchor） | 增量 merge（CODEGEN 覆寫、USER_EDIT 保留） |
| `validate` | 使用者明確要求，且 target 已存在 | 只跑 Step 0 → 4a → 5，禁止改寫生成碼 |

## 輸入

| 參數 | 必填 | 說明 |
|------|------|------|
| `spec_path` | new/update 必填；validate 條件必填 | 規格檔（.xlsx / .md）；validate 若 target 已有 `scratch/Game_Spec.md` 可省略 |
| `target_path` | 是 | 目標專案根目錄 |
| `mode` | 否 | 強制指定模式 |

## 核心原則

1. **按需讀取**：每步只讀 `_flow.md` 該步「📖 讀取」列出的文件，禁止一次全部載入
2. **Checkpoint 恢復**：每步完成寫 `<target>/.codegen-checkpoint.json`，中斷後從斷點繼續
3. **Mock 只替換資料不改邏輯**：OnCommand 攔截 SpinAck，狀態機/RoundEnd/roundController 全不動
4. **Feature 逐一驗證**：每個 State 必須有 NextState 出口，不能卡死
5. **Gate 驅動**：每步結束跑 `_gates.md` 對應段落的 grep，不通過禁止往下走
6. **Proto 單一間接點**：proto 一律經 `assets/Script/Proto.ts`；default export 保留 CJS runtime object，named type export 提供 namespace 型別。全案其他 .ts 只 import `./Proto`，換 proto 只動一處
7. **Mock／Proto 契約一致**：Mock 使用的 `IRoundInfo`／`IAwardData`／`ISpinAck` 欄位（含 `PlateQueue`、`WinLineIndex`、`EliminatePos`、`FreeGameRound`）必須同時存在於 `.d.ts` 與 runtime `.js` placeholder；禁止為了消除型別錯誤刪掉 Mock 資料
8. **Template API 以實作為準**：State 只能呼叫目標專案 component 真正存在的 API；`Node` 不得當成自訂 component，舊 template 的 `CurAwardLines`／`StopOneLineShow` 不存在時改用現有聚合清理 API
9. **Finalize Gate 是完成前置**：`assets/Script`／`assets/game/Script`／`tests` diagnostics、proto contract、regression 或 report schema 任一失敗時，禁止清除 checkpoint
10. **標準 codegen 只到無頭階段**：分身不得啟動、等待或呼叫 Cocos Editor；Gate 無論成敗都必須產生診斷 report，只有 finalize PASS 才能清 checkpoint 與宣告完成

## 依賴 Skill（按需讀取，不需要人工載入）

| Skill | 何時用 | 用途 |
|-------|--------|------|
| `excel-to-ai-doc` | Pre-A | xlsx → markdown + 圖片 + 顏色圖例 + 自我驗證報告 |
| `uk-slot-pattern-library` | Pre-B | 功能分類對照（模式索引 #1–#25，以該 skill 索引表為準） |

M2+ 交棒的下游 skill（uk-conventions / uk-slot-project-docs / state-machine / extrabet /
fake-reel-manager / multilang-sync）見 `_milestones.md`「下游 skill 交棒表」。

## 子檔案（按需讀取）

| 檔案 | 何時讀 | 內容 |
|------|--------|------|
| `_flow.md` | 執行 codegen 時（主骨架） | Pre-A/B + Step 0-5+H 流程順序 |
| `_primer.md` | 首次接觸此 skill 時 | Framework 架構速覽 |
| `_api-ref.md` | Step 3 coding 時 | Template API 簽名 |
| `_pitfalls.md` | 各 Step 對應段落 | 踩坑 checklist |
| `_gates.md` | 每 Step 結束時 | Mandatory Gate grep 驗證 |
| `_milestones.md` | Step 5 之後 | M2+ 實作指引、proto stub 路徑 |
| `gate_runner.py` | 每 Step 結束 + Step 5 finalize（必跑） | 結構化 gate、regression、traceability 與 report schema |
| `spec_adapter.py` | Step 1（加速器） | xlsx → Game_Spec.md 結構化提取 |
| `anchor_merge.py` | update 模式 Step 3 | 增量合併（CODEGEN/USER_EDIT anchor） |
| `check_regression_v2.py` | Step 5 驗證 | col/row/symbol/variable_board 比對 |
| `spec_traceability.py` | Step 1.5 + Step 5 | 穩定 Spec ID + provenance-aware manifest（codegen／inferred default／deferred M2+／informational） |
| `gen-spine-placeholder.js` | Step H2 | Spine placeholder 生成 |
| `bind_symbol_effect_prefabs.py` | Step H1 | 將 SymbolEffect_00..N 的 Prefab UUID 依 SymID 綁入 EffectPlate，並提供無頭檢查 |
| `ensure_game_meta.py` | Step 0 preflight | 確保 game.meta 存在 |
| `fix_mask_size.py` | Step 3.5 | 自動修正 SlotPlate_MG Mask contentSize |
| `ensure_ts_bom.py` | Step 4a 前 | 為 codegen-owned TypeScript 補 UTF-8 BOM，避免 Cocos parser 失敗 |
| `verify_compile.py` | Step 5 前 | 靜態契約 + 實際 TypeScript diagnostics（專案 source error 為 blocker） |
| `verify-preview.ts` | Step 4（有 Preview 時） | Puppeteer 驗證 |
| `post-codegen-extract.ts` | Step 5 後手動觸發 | Template 自進化 |

## 產出物慣例（全部進版控）

| 位置 | 內容 | 產生於 |
|------|------|--------|
| `<game>/docs/spec/` | 規格書 markdown（含顏色圖例）+ 圖片 + metadata/（metadata.json、validation.txt、stats.json） | Pre-A |
| `<game>/docs/dev-spec.md` | 差異開發規格（🟢🟡🔴 分類 + proto 映射） | Pre-B |
| `<game>/SPEC.md` | milestone 任務清單（做完打 [x]） | Post（Step 5 後） |
| `<game>/scratch/` | Game_Spec.md、Game_Summary_File.md、codegen-traceability.json、codegen-report.md | Step 1~5 |
| `<game>/AI.md` | 專案上下文（持續更新） | 全程 |

## Spec Adapter 用法

```powershell
$env:PYTHONIOENCODING='utf-8'
py ${SKILL_DIR}/uk-slot-codegen/spec_adapter.py <input.xlsx> <output.md>
```

前置：`py -m pip install openpyxl`

## Anchor Merge 用法

```powershell
# 新檔
py ${SKILL_DIR}/uk-slot-codegen/anchor_merge.py --new <expected.ts> <output.ts>
# 合併
py ${SKILL_DIR}/uk-slot-codegen/anchor_merge.py <existing.ts> <expected.ts> <output.ts>
```

## Template Slot Mode

Template 支援 3 種模式（SpinMode 判定規則見 `_flow.md` Step 2，preset 設定見 Step 3.5）：

| Mode | 設定 | 行為 |
|------|------|------|
| Standard | `REEL_LAYOUT_PRESETS.standard` + `SpinMode.Standard` | 傳統轉輪滾動 |
| Cascade | `.standard` + `SpinMode.Cascade` + `CascadeFillStrategy` | 轉輪 + 消除補位 |
| Tumble | `.dropEntry` + `SpinMode.Tumble` + `TumbleFillStrategy` + `DropEntryStrategy` | 掉落式 + 消除補位 |

## Specialist 委派

優先呼叫 `bridge-actions.parallel_delegate`，以 `task_id=pt_codegen`、
`specialist_name=slot-dev`，並在 goal 中提供 `spec_path`、`target_path`、
驗收條件與回報格式。只有 tool 明確回報 `unavailable` 時，才使用 legacy
fallback：

`<<PARALLEL_DELEGATE:pt_codegen|slot-dev|從 <spec_path> 產新 slot 到 <target_path>，跑 uk-slot-codegen 全流程>>`

Validation、policy rejection 或參數錯誤必須修正 tool request，不可用 token
繞過。

## Template 注意事項

- **BigWinComponent 用框架版**（`db://astarte-framework/Component/BigWinComponent`），不要在專案放 BigWinControll.ts
- **Spine placeholder 的 keyframe 須有位移**（`x: 0.01`），否則 Cocos 不觸發 complete
- **音效 placeholder 用 ffmpeg 產 0.1 秒靜音 AAC**，禁止複製現有 .m4a（size < 5KB）
- **AwardState 用 AudioManager.Play**（不能用 soundManager.Play，後者不接受字串 key）

## 常見錯誤

### 流程偏離（2026-07-09 Clash of Olympus 實證）

- ❌ 收到規格書後直接提實作方案（「clone X 來改」）→ 必須從 Pre-0 前提確認開始，
  任何實作提案都在 `_milestones.md` 之後
- ❌ 拿衍生品當基準做差異分析 → **基準永遠是 uk_slot_template**；衍生品只是「最近似參考」
  用於 code review，不影響 🟢/🟡/🔴 分類判定
  （實例：模板有 Collect/Cash/CoinState，因為只看衍生品而誤判為 🔴）
- ❌ Pre-B 沒讀 pattern-library 就寫 dev-spec → 會漏掉已驗證的模式變體導致重複設計
  （實例：collect-feature.md 有「雙向 Collect」變體，直接可用）
- ❌ 檢查點只列摘要不逐項回答 → 用 `_flow.md` 的填空格式輸出，並收進 Step 5 Report

### 技術錯誤

- ❌ 用 git clone/fork 起專案 → 會帶入模板 history；codegen 用 `clone --depth=1 + rm .git`
- ❌ 把整份規格書當實作範圍 → 先做差異分析（Pre-B），只實作 delta
- ❌ 跳過人工檢查點直接往下走 → 源頭錯誤全線放大
- ❌ unshow/replay 還原留到專案尾聲 → 放進每個機制的驗收標準
- ❌ proto 假設寫完不回頭核對 → proto 到手後必須逐項驗證 ⏳ 項目
- ❌ 全案 code 直接 import proto 套件 → 換 proto 要動幾十處；一律經 Proto.ts 單一間接點

## Related

- `slot-art-manifest-validator` — 美術覆蓋率驗證（獨立 skill）
- `excel-to-ai-doc` — xlsx 轉換工具（Pre-A 依賴）
- `uk-slot-pattern-library` — 模式對照庫（Pre-B 依賴）
- `uk-slot-spec-to-impl` — 已於 2026-07-30 併入本 skill，保留為 pointer
- Template repo: `git@github.com:IGS-ARCADE-DIVISION-RD2/uk_slot_template.git`
  （無 SSH 權限時走本地 `git archive`，見 `_milestones.md`「M0a 起新專案」）
