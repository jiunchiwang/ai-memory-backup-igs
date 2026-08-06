# Codegen Flow

**⚠️ 關鍵規則：收到 codegen 委派後，必須一口氣從 Pre-A 跑到 Step 5（Report）完畢才停。標準 codegen 的完成邊界是無頭編譯驗證；禁止啟動、等待或呼叫 Cocos Editor。禁止中途暫停等待使用者說「繼續」。若 context 不夠用 <<CONTINUE>> 自動延續。**

每步只讀「📖 讀取」欄位列出的檔案。每步結束跑對應 gate。

---

## Pipeline 總覽

| Step | 名稱 | 需 Editor | 可跳過 |
|------|------|-----------|--------|
| Pre-0 | 前提確認 | ❌ | ❌ |
| Pre-A | 規格轉換 (excel-to-ai-doc) | ❌ | 條件（docs/spec/ 已存在時跳） |
| Pre-B | 差異分類 + dev-spec | ❌ | 條件（dev-spec.md 已存在時跳） |
| 0 | Preflight | ❌ | ❌ |
| 0.0 | Template Copy | ❌ | 條件（目標非空時跳） |
| 0.1 | Extensions Clone | ❌ | ❌ |
| 1 | Spec Ingestion (adapter) | ❌ | ❌ |
| 1.5 | Spec Traceability | ❌ | ❌ |
| 2 | Summary Generation | ❌ | ❌ |
| 3.1 | Game_Define | ❌ | ❌ |
| 3.2 | GameView / StateMachine | ❌ | ❌ |
| 3.3 | Proto | ❌ | ❌ |
| 3.4 | Mock Server | ❌ | ❌ |
| 3.5 | Reel Module | ❌ | ❌ |
| 3.6 | Scaffold（State files + Common + Directory，合併原 3.6/3.8/3.9） | ❌ | ❌ |
| 3.7 | Audio | ❌ | ❌ |
| 3.10 | Feature Code | ❌ | ❌ |
| H1 | Feature Prefab | ❌ | ❌ |
| H2 | Symbol PNG | ❌ | ❌ |
| H4 | Art Manifest | ❌ | ❌ |
| 4a | Headless Compile Validation | ❌ | ❌ |
| 5 | Report | ❌ | ❌ |

---

## Mode / Input 執行矩陣

| Mode | xlsx | markdown | 生成碼改寫 |
|------|------|----------|--------------|
| new | Pre-A/B → Step 0~5 | 複製 markdown 為 `scratch/Game_Spec.md` → Pre-B → Step 0~5 | 允許 |
| update | 重跑 ingestion/summary，再按 anchor merge 到 Step 5 | 同左 | 只改 CODEGEN anchor／差異追加 |
| validate | 若有新 spec 先重建 `Game_Spec.md`，再跑 Step 0 → 4a → 5 | 複製為 `Game_Spec.md`，再跑 Step 0 → 4a → 5 | **禁止** |

`validate` 模式不執行 Pre-B、Step 0.0/0.1、Step 2~H4；若未提供新 spec，必須使用 target 現有的 `scratch/Game_Spec.md`，不得偷用其他專案 fixture。

---

## Pre-0: 前提確認

📖 無（只確認參數）

收到委派後第一件事，**填完才能進 Pre-A**。不停等使用者，但未填的欄位要在 Step 5 Report
的「人工檢查點待確認」區塊列出來。

```
- [ ] 規格書路徑：________________
- [ ] 專案輸出目錄：________________
- [ ] uk_slot_template 來源：遠端 clone / 本地 archive ________________
- [ ] 最近似衍生品（僅供 code review 參考）：________________（無則留空）
- [ ] Proto 狀態：已發佈 ________________ / ⏳ 未發佈（走 proto stub，見 _milestones.md）
```

> ⚠️ **差異分析的基準永遠是 `uk_slot_template`，不是衍生品。**
> 拿衍生品當基準會把「衍生品已實作的遊戲特有功能」誤判成 🟢，導致 Pre-B 分類錯誤與
> 工作量低估（2026-07-09 Clash of Olympus 實證：模板本來就有 Collect/Cash/CoinState，
> 因為只看衍生品而誤判為 🔴）。衍生品只用於 code review 參考，不影響 🟢/🟡/🔴 判定。

**驗證**：`spec_path` 與 `target_path` 已確定；proto 狀態已標記

---

## Pre-A: 規格轉換 (excel-to-ai-doc)

📖 `${SKILL_DIR}/excel-to-ai-doc/SKILL.md`

**跳過條件**：`<target>/docs/spec/markdown/` 已有 .md 檔案

用 excel-to-ai-doc 把 xlsx 轉成 AI 可讀結構。產出是整個 pipeline 的 **ground truth**。

```powershell
$env:PYTHONUTF8='1'
uv run "${SKILL_DIR}/excel-to-ai-doc/scripts/convert.py" "<spec_path>" "<target>/docs/spec"
# 沒裝 uv 時退回：py "${SKILL_DIR}/excel-to-ai-doc/scripts/convert.py" ...（需先 pip install requirements）
```

**輸出**：`<target>/docs/spec/markdown/<stem>.md`（含顏色圖例）+ `<stem>_markitdown_raw.md`
（比對基準，平時不讀）+ `images/` + `metadata/metadata.json` + `metadata/validation.txt`
+ `metadata/stats.json`

> 🔍 **檢查點 1（請使用者過目）**：Codegen 不停等確認即可繼續，但**必須逐項輸出下列
> 格式並收進 Step 5 Report**，不可只寫「看起來沒問題」：
>
> ```
> - 自我驗證：{validation.txt 第一行「整體：」原文}
>   - 孤兒圖（xl/media 有但無錨點）：{N} 張 → {數量少屬正常 / 接近總數需查匯出方式}
>   - 密集表縮水 / 有內容卻空輸出：{無 / 逐項列出}
> - 圖片：共 {N} 張（validation 的「已錨定抽出」）
> - 賠付表數值：{有完整數值 / 部分空白需機率文件 / 全空}
> - 顏色圖例：{M} 種樣式組合 → {是否有明顯語意分組，如黃底=待確認}
> - 關鍵玩法圖對應章節：
>   - {章節名} → {圖片 cell 位置} {對/缺}
> ```
>
> 前三項直接引用 `metadata/validation.txt`，不要自己數。

Pre-A 完成後**立即建立 `<target>/AI.md`**（照 `uk-slot-project-docs` 慣例），填入已知的
專案 meta、盤面佈局、Symbol 列表；後續每個 Step 增量更新。越早建越有用——留到 M0a
之後才建，前面幾步的發現就沒地方落。

**驗證**：`<target>/docs/spec/markdown/` 至少有一個 .md 檔案，且 `<target>/AI.md` 存在

---

## Pre-B: 差異分類 + dev-spec

📖 `<target>/docs/spec/markdown/<stem>.md`（Pre-A 產出，含關鍵玩法圖片）
📖 `<template>/assets/Script/Game_Define.ts`（**模板現碼**：Symbol enum + GameState enum）
📖 `${SKILL_DIR}/uk-slot-pattern-library/SKILL.md`（模式索引）
📖 `${SKILL_DIR}/uk-slot-pattern-library/patterns/`（按需讀取對應模式卡片）

⚠️ **必讀模板 `Game_Define.ts` 再分類**。不讀就分類是「模板已有的符號/State 被標成 🔴」
的直接成因（見檢查點 2 常見錯誤）——分類基準是模板現碼，不是印象也不是衍生品。

**跳過條件**：`<target>/docs/dev-spec.md` 已存在

讀規格書 規格 markdown，對照 pattern-library 的模式卡片，產出差異開發規格。

### 功能分類表

規格書每個功能標一類：

| 分類 | 意義 | dev-spec 裡要寫的 |
|------|------|------------------|
| 🟢 模板已有 | Standard/Cascade/Tumble、基本 UI 等 | 只列設定值 |
| 🟡 有既成模式 | pattern-library 裡有卡片的（ExtraBet、FakeReel 等） | 標對應 pattern 名 |
| 🔴 本作特有 | 新機制（如能量收集、輪盤選獎） | 附一段迷你設計 |

🔴 清單就是真正的工作量所在。

### proto 映射表

功能 ↔ proto 欄位對照。**proto 未發佈時**：整表標 ⏳，每項記錄「假設的資料形狀」。

**輸出**：`<target>/docs/dev-spec.md`

> 🔍 **檢查點 2（請使用者過目）**：同樣不停等，但**必須逐項輸出下列格式並收進 Step 5
> Report**：
>
> ```
> - 🔴 清單完整性：共 {N} 項，有無遺漏？
> - 分類正確性：有無 🟡 應為 🔴、或 🔴 應為 🟡 的？
>   （常見錯誤：模板已有的符號/State 被標成 🔴）
> - Proto 假設合理性：{合理 / 需調整項目}
> ```

**驗證**：`<target>/docs/dev-spec.md` 存在且含 🟢🟡🔴 分類表

---

## Step 0: Preflight

📖 無（只用 shell/read 偵測）

1. 檢查 `.codegen-checkpoint.json` → 存在則恢復
2. mode 判定優先順序：使用者明確指定 `validate` → 否則目標空為 `new` → 已有 `assets/Script/` 為 `update`；`validate` 不得由檔案系統自動推測
3. 檢查 spec 副檔名 → 決定 ingestion 策略
4. 寫初始 checkpoint

**輸出**：mode + spec_format + start_step 確定
**驗證**：`_gates.md` §0

---

## Step 0.0: Template Copy（mode=new 且目標空時）

📖 無

**目的**：從遠端 uk_slot_template 取得完整 Cocos 專案骨架，**刪除 `.git/`** 讓 target 可建新 repo。

```powershell
git clone --depth=1 --progress git@github.com:IGS-ARCADE-DIVISION-RD2/uk_slot_template.git "<target>"
Remove-Item "<target>\.git" -Recurse -Force
```

⚠️ **不加 `--recursive`**：extensions 由 Step 0.1 獨立處理（獨立 repo）。

**驗證**：`assets/Script/Game_Define.ts` 存在 且 `<target>\.git` 不存在

---

## Step 0.1: Extensions Sync

📖 `<target>/gameSetting.json`

⚠️ 即使 Step 0.0 跳過仍必須執行。Preflight: `Test-Path extensions/astarte-framework`。

**repo URL 來源規則**：讀 `<target>/gameSetting.json` → 取 `extensions[0].git` 欄位值作為 repo URL。若該欄位不存在，使用 `git@github.com:IGS-ARCADE-DIVISION-RD2/uk_slot_template_extensions.git`。

分流是強制的：

- `<target>/extensions/.git` 存在：在該 repo 執行 `git pull --ff-only`
- `extensions` 不存在：`git clone <repo_url> "<target>/extensions"`
- `extensions` 存在但不是 git repo：停止並報告，不得覆蓋

**驗證**：`_gates.md` §0

---

## Step 1: Spec Ingestion (adapter)

📖 `${SKILL_DIR}/uk-slot-codegen/spec_adapter.py`（xlsx 時）

Pre-A 已產出 `docs/spec/`（ground truth），本步產出唯一的 `scratch/Game_Spec.md`。

```powershell
$env:PYTHONIOENCODING='utf-8'
py "${SKILL_DIR}/uk-slot-codegen/spec_adapter.py" <spec_path> <target>/scratch/Game_Spec.md
```

- `.xlsx`：執行上述 adapter
- `.md`：以 filesystem copy 將輸入複製為 `<target>/scratch/Game_Spec.md`；Gate 若解不出 COL/ROW/Symbol/BoardLayout 必須失敗，不得 SKIP 完成

**輸出**：`<target>/scratch/Game_Spec.md`

> 注意：adapter 的 Symbol idx 已從 ODDS 表 reindex 校正，但仍以 Pre-A 的 規格 markdown 為最終權威。
> Step 2 產出 Summary 時若發現 adapter 順序與 ODDS 表不一致，以 ODDS 表為準。

**驗證**：`_gates.md` §1

---

## Step 1.5: Spec Traceability

📖 無

```powershell
py "${SKILL_DIR}/uk-slot-codegen/spec_traceability.py" tag-spec <target>/scratch/Game_Spec.md
```

`tag-spec` 可重跑且必須保持既有 ID 穩定；表格 header 不得配置 ID。ID prefix 僅是歷史 chapter 編號，不代表 ownership，後續 scope 以 section title、欄位內容與 provenance 判定。

`SymbolWidth`、`SymbolHeight`、`SeparateLineWidth`、`MIDDLE_PLATE_INDEX` 若只是依 `_api-ref.md` 補入，scope 必須是 `inferred default`，不得冒充原始規格或阻擋 gate。只有原始 xlsx 明確提供值時，才在該行加 `[SOURCE:xlsx]`，提升為 codegen-owned contract。

**驗證**：`_gates.md` §1.5

---

## Step 2: Summary Generation

📖 `<target>/scratch/Game_Spec.md`（adapter 結構化輸出，快速參考）
📖 `<target>/docs/spec/markdown/<stem>.md`（excel-to-ai-doc 重建版，ground truth；
   **不是** `_markitdown_raw.md`，那份只是比對基準）

1. 解析 Game_Spec 產出 7 章節 Summary
2. 辨識 SpinMode（4 條優先規則）
3. **Symbol 排序校正**：從 規格 markdown 找「ODDS表」區塊，讀取 SymID 欄數字。
   非 `server_only` 項目的 SymID 是 `enum Symbol` 的 client 契約；若 adapter 的
   Game_Spec 中 Symbol idx 與 ODDS 表 SymID 不一致，**以 ODDS 表為準**。
4. 產出 `Game_Summary_File.md`

**SymID 校正規則**：
- ODDS 表通常在「2. 基本規格」sheet 內，規格 markdown 中搜尋「ODDS表」或「SymID」關鍵字定位
- 第一個 Symbol（通常 WILD）若無 SymID 數字，則為 idx=0
- 後續 Symbol 依 SymID 欄遞增排列
- ODDS 表有但 adapter 漏掉的 Symbol（如 FEATURE、Blank、server 用）須補入 Summary；
  server 用項目必須另列並標 `server_only`，不得計入 Client Symbol Count

**SpinMode 判定**：
1. 明確標示「Tumble/Cascade/消除/掉落」→ dropEntry
2. Performance_Flow 含 TUMBLE_DROP/ELIMINATE → dropEntry
3. Cluster Pay + 消除 → dropEntry
4. 以上皆無 → standard

**輸出**：`<target>/scratch/Game_Summary_File.md`
**驗證**：`_gates.md` §2

---

## Step 3.1: Game_Define Module

📖 本步讀：`_api-ref.md` §Game_Define + `_pitfalls.md` §3.1 + Game_Summary_File

1. 替換 `enum Symbol`（只含非 `server_only` 符號，保留 ODDS 表原始 SymID）；
   `server_only` 只保留在 Summary／protocol 契約，不得放進 `Game_Define.Symbol`、
   `SYMBOL_COUNT`、SymbolEffect prefab 或 Symbol PNG 需求
2. 替換 COL/ROW/FULL_PLATE_NUM/MAX_ROW
3. 替換/增減 enum GAMEVIEW_STATE
4. 設定 SCATTER_SYMBOL / NEARWIN_COLLECT_COUNT
   - `SCATTER_SYMBOL`：**只放規格書標示為 Scatter 的那一顆**（觸發 FG / NearWin 的符號），用 `Symbol.XXX` enum member
   - Feature Symbol（如 Expand/Multiplier/Bomb/Collect 等特殊功能符號）**不是 Scatter**，不放進 `SCATTER_SYMBOL`——它們各自在 Feature State 裡處理
6. **3.1.1**：修正 SlotReels.ts 中 `Symbol.A` / `Symbol.Ten` 硬編碼引用

**輸出**：`Game_Define.ts`（替換完成）
**驗證**：`_gates.md` §3.1

---

## Step 3.2: GameView Module

📖 本步讀：`_pitfalls.md` §3.2 + Game_Summary_File

1. 替換 `SetStateMachine()` state 註冊表
2. 確認每個新 state 的 .ts 有 valid export class
3. 三方一致驗證（enum ↔ register ↔ NextState）

**輸出**：`GameView.ts`
**驗證**：`_gates.md` §3.2

---

## Step 3.3: Proto Module

📖 本步讀：`_api-ref.md` §Mock Server 資料結構 + `_pitfalls.md` §3.3

**策略**：從 template（或上一個成功 codegen 產出）複製完整 proto .js/.d.ts，rename namespace。
不再用 `compile-proto.js` 自產（精簡版缺 decode/encode 實作，無法接真 server）。

1. 確定 namespace（如 `ar2lpProto`，取遊戲 short name）
2. 複製 template 的 `assets/Script/Test/` 下的 proto .js + .d.ts
3. 全文 replace 舊 namespace → 新 namespace（js + d.ts）
4. 更新 package.json（移除舊 proto npm 依賴；`devDependencies.typescript` 固定為已驗證版本 `5.9.3`）
5. 只建／更新 `assets/Script/Proto.ts` 單一間接點；其他 .ts 一律維持 `./Proto`
6. 若 package.json 有變更才執行 `npm install`

`compile-proto.js` 是舊的精簡產生器，禁止用於 Step 3.3；需自產 proto stub 時使用 `_milestones.md` 的標準 pbjs + pbts 路徑。

**Proto.ts 固定格式**（runtime 與 type namespace 必須分流）：
```ts
import protocol from "./Test/<ns>Proto.js";
export type { <ns> } from "./Test/<ns>Proto.js";
export default protocol;
```

消費端固定格式：
```ts
import protocol from "./Proto";          // runtime：protocol.<ns>.GameInfoData
import type { <ns> } from "./Proto";      // type：<ns>.IRoundInfo
```

禁止 `export * from "./Test/<ns>Proto.js"` 取代 default export；Cocos 載入 CJS protobuf 時會使 runtime `protocol.<ns>` 變成 undefined。也禁止把 default import 當 namespace type（`protocol.<ns>.IRoundInfo`），會觸發 TS2503。

**import 格式**：底層 proto 必須是 `import protocol from "./Test/xxxProto.js"`（default import + 帶 .js）
**d.ts 格式**：末尾必須有 `declare const protocol: { <ns>: typeof <ns> }; export default protocol;`

**輸出**：`<target>/assets/Script/Test/<ns>Proto.js` + `<ns>Proto.d.ts` + `assets/Script/Proto.ts`
**驗證**：`_gates.md` §3.3

---

## Step 3.4: Mock Server

📖 本步讀：`_api-ref.md` §Mock Server 資料結構 + `_pitfalls.md` §3.4

1. Game_Define 加 `USE_MOCK_SERVER` + `MOCK_MODE`
2. GameView.OnCommand 加 Mock 攔截
3. 寫 `GenerateMockSpinAck()`（至少包含 normal/freegame/bigwin/nearwin/symboleffect；遊戲需要時追加 collect/jackpot）
4. 寫 `InitMockKeyboard()`（Cocos input 系統；固定 `5=symboleffect`，既有 jackpot 移至 `7`）
5. **必須取消以下 template 註解**（否則 FG/消除流程斷裂）：
   - `OnRecvSpinAck` 中 `this.IsGoingToFree = true`（FG 觸發）
   - `CheckState` 中 FG 離場判斷 `CurPlateIndex >= RoundQueue.length - 1`
   - `SpinState` 中 unshow/scatter 清理
6. `start()` 裡呼叫 `this.InitMockKeyboard()`
7. **Mock 資料完整性驗證**：
   - 每個 IRoundInfo 必須包含 `RoundWin`（bigwin 給高值如 50000，normal 給 random）
   - NearWin mock 的符號必須是 `Game_Define.SCATTER_SYMBOL` 的值（不是 CASH/WILD）
   - `GenerateMockSpinAck` 回傳的 ISpinAck 必須包含 `TotalWin`
   - Mock 使用到的欄位必須也存在於 placeholder `.d.ts` 與 runtime `.js`；`PlateQueue`、`WinLineIndex` 是 codegen 假資料契約，不可為了消除型別錯誤刪除
   - `GenerateMockSpinAck` 必須填 `TotalWin`、`Bet`；FG mock 另填 `FreeGameRound`。報獎效果若讀 `EliminatePos`，則 `IAwardData`／`AwardData` 與 runtime default 也必須保留該欄位
   - 實體 cell 依目前 `ReelLayoutConfig` 建立；外部 position 固定以 MAX_ROW 編碼。`columnAlignment` 同時控制可視窗：top 起始 0、center 起始 `floor((MAX_ROW-ROW)/2)`、bottom 起始 `MAX_ROW-ROW`
   - `MAX_ROW > ROW` 時仍只產生一個 `standard`：`targetSymbolCount=MAX_ROW`、`visibleSymbolCount=ROW`；`columnAlignment:'center'` 的 MG 可視起始 row 為 `floor((MAX_ROW-ROW)/2)`，往上擴張沿用同一組實體 cell
   - `symboleffect` mock 必須依 standard 的 `columnAlignment` 計算第一個可視 row；bottom 對齊 5×3 範例使用 `EliminatePos: [2, 7, 12]`；按鍵固定為 `5`
   - mock 物件加 type annotation（`const roundInfo: <ns>.IRoundInfo = {...}`）讓 TS 攔缺欄位；`<ns>` 必須由 `import type` 引入，不可寫成 `protocol.<ns>.IRoundInfo`

**輸出**：Game_Define.ts + GameView.ts
**驗證**：`_gates.md` §3.4

---

## Step 3.5: Reel Module

📖 本步讀：`_api-ref.md` §SlotReels + `_pitfalls.md` §3.5 + Game_Summary_File
📖 若可變盤面：額外讀 `_api-ref.md` §附錄：可變盤面

1. 同步 COL/ROW/FULL_PLATE_NUM/MAX_ROW/NORMAL_COLUMNS，並由 ROW/MAX_ROW 產生單一 standard ReelConfig
2. 修正 m_reelPositionOffset 長度
3. SpinMode 專屬（dropEntry: SHOW_COLUMNS=1 + MIDDLE_PLATE_INDEX=0）
4. GameView.LoadSymbol 初始化：Tumble 必須是 `.dropEntry` + `SpinMode.Tumble` + `TumbleFillStrategy` + `DropEntryStrategy`
5. Prefab Mask contentSize（自動修正）：
   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   py ${SKILL_DIR}/uk-slot-codegen/fix_mask_size.py <target>
   ```
6. 可變盤面 → per-column Mask 結構

**輸出**：Game_Define.ts + SlotReels.ts + SlotPlate_MG.prefab
**驗證**：`_gates.md` §3.5

---

## Step 3.6: Scaffold（State files + Common + Directory）

📖 Game_Summary_File

合併原 3.6/3.8/3.9 三個輕量步驟：

1. **State Machine files**：Template 已含所有常見 state 骨架。有自訂 state → 新建 .ts；多的 state → 保留不刪
2. **Common Module**：通常不需改動。僅不規則盤面時調整 Common.ts
3. **Directory & Prefab Structure**：依 Summary §7 補建缺少的 Prefab 子目錄

**輸出**：`GameState/*.ts` + 子目錄結構
**驗證**：`_gates.md` §3.6

---

## Step 3.7: Audio Module

📖 本步讀：`_pitfalls.md` §3.7 + Game_Summary_File

1. 替換 `AudioManager.AudioClips` 音效清單（key / FileName / `.m4a` 檔名大小寫完全一致）
2. 產生 placeholder .m4a（ffmpeg 靜音 0.1s）
3. Case-aware rename（Windows 兩步）
4. 確認逐一比對（不只比數量）

**輸出**：AudioManager.ts + `assets/game/Sound/*.m4a`
**驗證**：`_gates.md` §3.7

---

## Step 3.10: Feature Code Generation

📖 本步讀：`_api-ref.md` §Feature Manager + `_pitfalls.md` §3.10 + Game_Summary_File §3

⛔ **不可跳過 / 不可延後。純 TS 操作，不依賴 Editor。**

自檢：Game_Define.ts ✓ / GameView.ts ✓ / GameState/ ✓ → 立即執行。

### 3.10.1 Feature Flags 解析
從 Game_Summary_File §3 取得啟用的 Feature，加入 Game_Define.FEATURES。

### 3.10.2~3.10.6 各 Feature 配置
按 flags 啟用：FreeGame / Jackpot / Respin / NearWin / Multiplier
- 確認 Manager 存在（禁止重寫 FgDeclare/FgCompliment）
- 確認 State 有 NextState 出口
- BigWin.Show 呼叫不在註解裡（公版 API 是 `BigWin.Show(win, lvl)`）

### 3.10.6.5 Feature Spine 播放 Code
EnterFreeState/LeaveFreeState 加 Spine 呼叫。

### 3.10.7 MockServer 擴充
根據 FEATURES flags 擴充新 mode + 熱鍵。**熱鍵配置以 Step 3.4 為準**
（`5=symboleffect`、`7=jackpot`，`_gates.md` §3.4 驗 `DIGIT_5`/`DIGIT_7`）；
新 feature 往 `6`、`8` 之後排，不可佔用 5/7。

### 3.10.8 未覆蓋 Feature 偵測
偵測 game-specific 機制（砲彈/瞄準/重轉等）→ 報告不實作。

**驗證**：`_gates.md` §3.10

---

## Step H1: Feature Prefab Skeleton

📖 本步讀：`_api-ref.md` §Phase H + `_pitfalls.md` §H

⚠️ **Template 已預建 6 組 Spine placeholder（BigWin/FG_Declare/FG_Compliment/NearWin/Scatter/SymbolEffect），codegen 不要重新產生。**
`gen-spine-placeholder.js` 只在 template 缺少某組 Spine 時才需要執行。

1. 確認 `assets/game/Spine/` 下 6 組都存在（clone 帶來的）
2. 複製 SymbolEffectPrefab × SYMBOL_COUNT 份（各設 m_symbolId）
3. 執行 `py bind_symbol_effect_prefabs.py <target>`：同步 `SymbolEffect.png`／atlas／Spine JSON bounds與attachment／母版／各 Prefab 為 178×178；保留 `BaseSpine → sp.Skeleton`，另外在 root 加上 `SymbolSpine → BaseSpine`、寫入對應 `m_symbolId`，並依 SymID 順序把各 UUID 寫入 `EffectPlate.prefab.m_symbolEffectPrefabs`

此綁定步驟可重跑，且 update mode 即使跳過 Prefab 複製，也必須在 finalize 前執行一次，以修復新增 Symbol 或既有空陣列。

**驗證**：`_gates.md` §H1

---

## Step H2: Symbol PNG + Spine Placeholder

📖 `_pitfalls.md` §H

- Symbol PNG：不覆蓋 template 原圖（≤21 個免動），超過才複製+產新 meta
- 驗證每張 .meta 有 f9941 spriteFrame

**驗證**：`_gates.md` §H2

---

## Step H4: Art Asset Manifest

產出 `ART_ASSET_MANIFEST.md`（美術交付清單）。

**驗證**：`_gates.md` §H4

---

## Step 4a: Compile Verification（不需 Editor）

📖 無

```powershell
$env:PYTHONIOENCODING='utf-8'
py ${SKILL_DIR}/uk-slot-codegen/ensure_ts_bom.py <target>
py ${SKILL_DIR}/uk-slot-codegen/verify_compile.py <target>
```

先對 `assets/Script`、`assets/game/Script`、`tests` 補齊 UTF-8 BOM，再跑靜態契約與真正的 TypeScript compiler。BOM 工具可重複執行，不會重複加 BOM；遇到非 UTF-8 檔案會停止而不是盲目改寫。Compiler 解析順序：target local `node_modules/typescript/bin/tsc` → `TSC_PATH` → 經 `--version` 驗證的 PATH `tsc`；禁止用可能下載錯誤同名套件的裸 `npx tsc`。

`assets/Script`、`assets/game/Script`、`tests` diagnostics 是 blocker；Cocos／extension 既有 declaration error 分開計數，不可掩蓋專案錯誤。FAIL 時必須修正再繼續。常見錯誤：
- proto .js 缺 `var $util = protobuf.util;` 宣告
- import 相對路徑指向不存在的檔案
- JS 語法錯誤
- target 沒有 TypeScript dependency 且 `TSC_PATH`／PATH 也無有效 compiler

**驗證**：exit code 0 = PASS

---

## Post-E: Editor / Runtime Validation（不屬於標準 codegen）

📖 無

標準 codegen 與背景分身任務不執行本階段，也不得因本階段阻塞 Step 5。需要時由使用者另行啟動 Editor 後手動驗證：

1. 開啟 `MainGame.scene`
2. 啟動 Preview 並檢查 console
3. 確認 Spine placeholder / SkeletonData 綁定
4. 確認 Prefab、Mask contentSize 與實際美術素材

上述項目一律由 Step 5 寫入「後續未完成工項」，不得宣告為已驗證。

---

## Step 5: Report

📖 無（彙整結果）

1. 跑 `py ${SKILL_DIR}/uk-slot-codegen/gate_runner.py --step prefinalize --target <target>`，保留 JSON 結果；此 gate 同時寫出 `<target>/scratch/codegen-traceability.json`。regression `FAIL/SKIP` 與 codegen-owned evidence 缺失都是 blocker；inferred defaults 顯示 verified／needs review，deferred M2+ 只列入統計，兩者都不阻擋
2. 不論 prefinalize PASS/FAIL 都寫 `<target>/scratch/codegen-report.md`，作為交接與診斷記錄；必須包含以下區塊：
   - `## 無頭階段完成項目`：生成內容與已通過的 gate
   - `## Gate 結果`：編譯、regression，以及 traceability 的 `codegen X/Y`、`inferred defaults A/B verified`、`deferred M2+ N`；codegen 未覆蓋時逐項列 ID
   - `## 後續未完成工項`：每項使用 `- [ ]`，寫明原因、目標檔案/場景與驗收方式
   - `## 人工檢查點待確認`：把 Pre-0 未填欄位、檢查點 1、檢查點 2 的逐項輸出原樣貼進來，
     每項 `- [ ]`。這是 codegen 不停等使用者的代價，**不可省略**——省了就等於檢查點沒發生
   - `## 已知風險`：無法由無頭階段證明的行為
3. 「後續未完成工項」至少列出 Runtime/Preview 驗證、Prefab/Spine 綁定、實際美術音效替換，以及 manifest 中的 deferred M2+／Step 3.10.8 偵測到但未實作的 game-specific feature；不適用時要寫明排除依據
4. 跑 `py ${SKILL_DIR}/uk-slot-codegen/gate_runner.py --step finalize --target <target>` 驗證所有必要 Gate + report schema
5. **只有 finalize `all_pass=true` 才能清除 checkpoint 與宣告 codegen 完成**

硬性規則：report 是診斷產物，可在 Gate 失敗時產生；checkpoint 與「完成」狀態只由 finalize 決定。Editor / Preview 未執行不是 blocker，但必須如實列入後續未完成工項。

**驗證**：`_gates.md` §5

---

## Checkpoint

每步完成後更新 `<target>/.codegen-checkpoint.json`：
```json
{
  "version": 1,
  "mode": "new",
  "current_step": "3.2",
  "completed_steps": ["0", "1", "2", "3.1"],
  "next_step": "3.2",
  "decisions": {
    "spin_mode": "dropEntry",
    "namespace": "ar2lpProto",
    "col": 5,
    "row": 3,
    "features": ["FreeGame", "NearWin"]
  }
}
```
`decisions` 欄位存放跨步驟需要的判定結果，避免恢復時重新解析 Summary：
- `spin_mode`：Step 2 判定的 SpinMode preset
- `namespace`：Step 3.3 確定的 proto namespace
- `col`/`row`：盤面尺寸
- `features`：Step 3.10.1 偵測到的啟用 Feature 清單

中斷恢復：讀 checkpoint → 跳到 next_step + 讀取 `decisions` 恢復決策 context。

---

## Update Mode 步驟差異表

`mode=update` 時，已有 codegen 產物（含 anchor）。以下列出各步差異：

| Step | New | Update | 說明 |
|------|-----|--------|------|
| 0 Template Copy | 執行 | **跳過** | 目標非空 |
| 0.1 Extensions | 執行 | 執行（pull） | `git pull` 更新 |
| 1 Spec Ingestion | 執行 | 執行 | 重新產 Game_Spec |
| 2 Summary | 執行 | 執行 | 重新產 Summary |
| 3.1 Game_Define | 覆寫 | **Anchor Merge**（CODEGEN 區覆寫、USER_EDIT 保留） |
| 3.2 GameView | 覆寫 | **Anchor Merge** |
| 3.3 Proto | 覆寫 | **跳過**（namespace 已正確則不動） |
| 3.4 Mock | 覆寫 | **Merge**（新 MOCK_MODE 追加、既有保留） |
| 3.5 Reel | 覆寫 | **Anchor Merge** |
| 3.6-3.9 Scaffold | 執行 | **跳過**（state/common/dir 已存在） |
| 3.7 Audio | 覆寫 | **差異追加**（新音效加入、舊的保留） |
| 3.10 Feature | 執行 | **增量**（新 Feature 加入、既有不刪） |
| H1-H4 | 執行 | **跳過**（prefab/PNG 已存在） |
| 4a Headless Compile Validation | 執行 | 執行 |
| 5 Report | 執行 | 執行 |

**Anchor Merge 規則**（語法以 `anchor_merge.py` 為準）：
- `// <<CODEGEN_BEGIN:name>>` ~ `// <<CODEGEN_END:name>>` 區塊 → 覆寫
- `// <<USER_EDIT_BEGIN:name>>` ~ `// <<USER_EDIT_END:name>>` 區塊 → 保留
- expected 新增的 anchor → 插入；expected 已移除的 anchor → 標 CODEGEN_DEPRECATED 註解
- 無 anchor 的程式碼 → 視為 CODEGEN 區覆寫（保守策略）

---

## 重要規則（所有 Step 適用）

1. **按需讀取**：只讀當前步驟「📖 讀取」列出的文件
2. **Template 註解取消**：凡 Mock 需驅動的分支不能是註解狀態（見 `_pitfalls.md` §通用）
3. **Checkpoint 每步更新**：寫完產出立即更新
4. **Gate 失敗**：修正 → 重跑 → 連續 2 次失敗 → 停止報告
5. **Custom Features**：Game_Spec 有 `## Custom Features` section → Step 3.10.8 報告但不實作
