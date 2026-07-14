---
name: uk-slot-codegen
description: UK slot codegen 統一入口。使用者提供規格路徑+目標專案路徑，自動串接 adapter→codegen→validation 全流程。支援新專案/增量更新/僅驗證三種模式，每步 checkpoint 可中斷恢復。
---

# UK Slot Codegen

統一 pipeline：`規格（xlsx/md）→ Game_Spec → Game_Summary → TS 模組 → Validation → Report`

## 與 uk-slot-spec-to-impl 的分工

- 要「快速可跑骨架 + Mock demo」（真 server / 美術未到、想先看流程跑起來）→ 用本 skill
- 正式開發全程（差異分析、milestone 拆解、特色機制實作）→ 主流程走
  `uk-slot-spec-to-impl`，本 skill 只承接其 **M0a~M1 的骨架生成**，跑完回到
  該 skill 的人工檢查點與 M0b
- **本地慣例覆蓋（proto）**：proto 一律經 `assets/Script/Proto.ts` 單一間接點
  （`import protocol from "..."; export default protocol;`），全案其他 .ts 只
  import `./Proto`。本 skill Step 3.3 的「替換所有 .ts 的 proto import」改為
  只維護 Proto.ts 一處——換 proto 時免動幾十個檔案（uk_917 實證教訓）

## 三種模式

| 模式 | 觸發 | 行為 |
|------|------|------|
| `new` | 目標路徑不存在或空 | 完整 pipeline |
| `update` | 目標已有 codegen 產物（含 anchor） | 增量 merge（CODEGEN 覆寫、USER_EDIT 保留） |
| `validate` | 使用者明確要求 | 只跑驗證 |

## 輸入

| 參數 | 必填 | 說明 |
|------|------|------|
| `spec_path` | 是 | 規格檔（.xlsx / .md） |
| `target_path` | 是 | 目標專案根目錄 |
| `mode` | 否 | 強制指定模式 |

## 核心原則

1. **按需讀取**：每步只讀 `_flow.md` 該步「📖 讀取」列出的文件，禁止一次全部載入
2. **Checkpoint 恢復**：每步完成寫 `<target>/.codegen-checkpoint.json`，中斷後從斷點繼續
3. **Mock 只替換資料不改邏輯**：OnCommand 攔截 SpinAck，狀態機/RoundEnd/roundController 全不動
4. **Feature 逐一驗證**：每個 State 必須有 NextState 出口，不能卡死
5. **Gate 驅動**：每步結束跑 `_gates.md` 對應段落的 grep，不通過禁止往下走

## 子檔案（按需讀取）

| 檔案 | 何時讀 | 內容 |
|------|--------|------|
| `_flow.md` | 執行 codegen 時（主骨架） | Step 0-5+H 流程順序、輸入/輸出、讀取指令 |
| `_primer.md` | 首次接觸此 skill 時 | Framework 架構速覽：CommonState 雙層、Mock 語意、BigWin API |
| `_api-ref.md` | Step 3 coding 時 | Template API 簽名：SlotReels/Game_Define/Mock/Feature Manager |
| `_pitfalls.md` | 各 Step 對應段落 | 踩坑 checklist（按 Step 分段） |
| `_gates.md` | 每 Step 結束時 | Mandatory Gate grep 驗證命令 |
| `gate_runner.py` | 每 Step 結束時（可選） | 結構化 gate 驗證（JSON 輸出），涵蓋 BOM/§3.2/§3.4/§3.10/tsc |
| `compile-proto.js` | Step 3.3（proto 編譯） | 從 .proto 產出 CJS static module |
| `gen-spine-placeholder.js` | Step H1.5（Spine placeholder） | 產生帶文字標示的 Spine placeholder |
| `spec_adapter.py` | Step 1（xlsx 輸入時） | xlsx → Game_Spec.md 轉換（含 custom_features 偵測） |
| `post-codegen-extract.ts` | Step 5 後手動觸發 | Template 自進化：diff → 分類 → 累積 patterns |
| `verify-preview.ts` | Step 4（有 Preview 時） | Puppeteer 自動化驗證：按熱鍵 + 收集 errors |
| `ensure_game_meta.py` | Step 0 preflight | 確保 game.meta 存在 |
| `anchor_merge.py` | update 模式 Step 3 | 增量合併（CODEGEN/USER_EDIT anchor） |
| `check_regression.py` | Step 5 驗證 | v1 state list 比對 |
| `check_regression_v2.py` | Step 5 驗證 | v2 col/row/symbol/variable_board 比對 |
| `spec_traceability.py` | Step 1.5 + Step 5 | Spec ID 標記 + 覆蓋率 |

## Spec Adapter 用法

```powershell
$env:PYTHONIOENCODING='utf-8'
py <skill_dir>/uk-slot-codegen/spec_adapter.py <input.xlsx> <output.md>
```

前置：`py -m pip install openpyxl`

## Anchor Merge 用法

```powershell
# 新檔
py <skill_dir>/uk-slot-codegen/anchor_merge.py --new <expected.ts> <output.ts>
# 合併
py <skill_dir>/uk-slot-codegen/anchor_merge.py <existing.ts> <expected.ts> <output.ts>
```

## Regression Check 用法

```powershell
# v2（推薦）
py <skill_dir>/uk-slot-codegen/check_regression_v2.py --spec <Game_Spec.md> --client <client-root>
# 全部 fixture
py <skill_dir>/uk-slot-codegen/check_regression_v2.py --all
```

## Template Slot Mode

Template 支援 3 種模式（SpinMode 判定規則見 `_flow.md` Step 2，preset 設定見 Step 3.5）：

| Mode | 設定 | 行為 |
|------|------|------|
| Standard | `REEL_LAYOUT_PRESETS.standard` + `SpinMode.Standard` | 傳統轉輪滾動 |
| Cascade | `.standard` + `SpinMode.Cascade` + `CascadeFillStrategy` | 轉輪 + 消除補位 |
| Tumble | `.dropEntry` + `SpinMode.Tumble` + `DropEntryStrategy` | 掉落式 + 消除補位 |

## Specialist 委派

```
<<PARALLEL_DELEGATE:pt_codegen|slot-dev|從 <spec_path> 產新 slot 到 <target_path>，跑 uk-slot-codegen 全流程>>
```

## Template 注意事項

- **BigWinComponent 用框架版**（`db://astarte-framework/Component/BigWinComponent`），不要在專案放 BigWinControll.ts
- **Spine placeholder 的 keyframe 須有位移**（`x: 0.01`），否則 Cocos 不觸發 complete
- **音效 placeholder 用 ffmpeg 產 0.1 秒靜音 AAC**，禁止複製現有 .m4a（size < 5KB）
- **AwardState 用 AudioManager.Play**（不能用 soundManager.Play，後者不接受字串 key）

## Related

- `slot-art-manifest-validator` — 美術覆蓋率驗證（獨立 skill）
- Template: `E:\UK\uk_slot_template\`
- Codegen 模板: `E:\UK\AI\.kiro\skills\slot-game-codegen-skill\`
