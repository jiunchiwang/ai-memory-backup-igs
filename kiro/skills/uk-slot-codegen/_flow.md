# Codegen Flow

**⚠️ 關鍵規則：收到 codegen 委派後，必須一口氣從 Step 0 跑到 Step 5（Report）完畢才停。禁止中途暫停等待使用者說「繼續」。若 context 不夠用 <<CONTINUE>> 自動延續。**

每步只讀「📖 讀取」欄位列出的檔案。每步結束跑對應 gate。

---

## Pipeline 總覽

| Step | 名稱 | 需 Editor | 可跳過 |
|------|------|-----------|--------|
| 0 | Preflight | ❌ | ❌ |
| 0.0 | Template Copy | ❌ | 條件（目標非空時跳） |
| 0.1 | Extensions Clone | ❌ | ❌ |
| 1 | Spec Ingestion | ❌ | ❌ |
| 1.5 | Spec Traceability | ❌ | ❌ |
| 2 | Summary Generation | ❌ | ❌ |
| 3.1 | Game_Define | ❌ | ❌ |
| 3.2 | GameView / StateMachine | ❌ | ❌ |
| 3.3 | Proto | ❌ | ❌ |
| 3.4 | Mock Server | ❌ | ❌ |
| 3.5 | Reel Module | ❌ | ❌ |
| 3.6 | State Machine files | ❌ | ❌ |
| 3.7 | Audio | ❌ | ❌ |
| 3.8 | Common | ❌ | ❌ |
| 3.9 | Directory & Prefab | ❌ | ❌ |
| 3.10 | Feature Code | ❌ | ❌ |
| H1 | Feature Prefab | ❌ | ❌ |
| H2 | Symbol PNG | ❌ | ❌ |

| H4 | Art Manifest | ❌ | ❌ |
| 4 | Validation | ✅ | ⚠️ 可跳 |
| 5 | Report | ❌ | ❌ |

---

## Step 0: Preflight

📖 無（只用 shell/read 偵測）

1. 檢查 `.codegen-checkpoint.json` → 存在則恢復
2. 檢查 `assets/Script/` → 決定 mode（new/update/validate）
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

## Step 0.1: Extensions Clone

📖 `<target>/gameSetting.json`

⚠️ 即使 Step 0.0 跳過仍必須執行。Preflight: `Test-Path extensions/astarte-framework`。

**repo URL 來源規則**：讀 `<target>/gameSetting.json` → 取 `extensions[0].git` 欄位值作為 repo URL。若該欄位不存在，使用 `git@github.com:IGS-ARCADE-DIVISION-RD2/uk_slot_template_extensions.git`。

```powershell
git clone <repo_url> "<target>/extensions"
```

**驗證**：`_gates.md` §0

---

## Step 1: Spec Ingestion

📖 `${SKILL_DIR}/uk-slot-codegen/spec_adapter.py`（xlsx 時）

```powershell
$env:PYTHONIOENCODING='utf-8'
py "${SKILL_DIR}/uk-slot-codegen/spec_adapter.py" <spec_path> <target>/scratch/Game_Spec.md
```

**輸出**：`<target>/scratch/Game_Spec.md`
**驗證**：`_gates.md` §1

---

## Step 1.5: Spec Traceability

📖 無

```powershell
py "${SKILL_DIR}/uk-slot-codegen/spec_traceability.py" tag-spec <target>/scratch/Game_Spec.md
```

**驗證**：`_gates.md` §1.5

---

## Step 2: Summary Generation

📖 `<target>/scratch/Game_Spec.md`

1. 解析 Game_Spec 產出 7 章節 Summary
2. 辨識 SpinMode（4 條優先規則）
3. 產出 `Game_Summary_File.md`

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

1. 替換 `enum Symbol`（符號清單）
2. 替換 COL/ROW/FULL_PLATE_NUM/MAX_ROW
3. 替換 AudioClips block
4. 替換/增減 enum GAMEVIEW_STATE
5. 設定 SCATTER_SYMBOL / NEARWIN_COLLECT_COUNT
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
4. 更新 package.json（移除舊 proto npm 依賴）
5. 替換所有 .ts 中 proto import 為 `import protocol from "./Test/<ns>Proto.js"`
6. `npm install`

> ⚠️ **本地慣例覆蓋（見 SKILL.md「與 uk-slot-spec-to-impl 的分工」）**：步驟 5 不改
> 所有 .ts——只建 `assets/Script/Proto.ts` 單一間接點
> （`import protocol from "./Test/<ns>Proto.js"; export default protocol;`），
> 其他 .ts 一律 `import protocol from "./Proto"`。換 proto 時只動 Proto.ts 一處
> （uk_917 實證：全案直接 import 換 proto 要動幾十個檔案）。

**import 格式**：`import protocol from "./Test/xxxProto.js"`（default import + 帶 .js）
**d.ts 格式**：末尾必須有 `declare const protocol: { <ns>: typeof <ns> }; export default protocol;`

**輸出**：`<target>/assets/Script/Test/<ns>.js` + `.d.ts`
**驗證**：`_gates.md` §3.3

---

## Step 3.4: Mock Server

📖 本步讀：`_api-ref.md` §Mock Server 資料結構 + `_pitfalls.md` §3.4

1. Game_Define 加 `USE_MOCK_SERVER` + `MOCK_MODE`
2. GameView.OnCommand 加 Mock 攔截
3. 寫 `GenerateMockSpinAck()`（4 mode：normal/freegame/bigwin/nearwin）
4. 寫 `InitMockKeyboard()`（Cocos input 系統，熱鍵 1~4）
5. **必須取消以下 template 註解**（否則 FG/消除流程斷裂）：
   - `OnRecvSpinAck` 中 `this.IsGoingToFree = true`（FG 觸發）
   - `CheckState` 中 FG 離場判斷 `CurPlateIndex >= RoundQueue.length - 1`
   - `SpinState` 中 unshow/scatter 清理
6. `start()` 裡呼叫 `this.InitMockKeyboard()`
7. **Mock 資料完整性驗證**：
   - 每個 IRoundInfo 必須包含 `RoundWin`（bigwin 給高值如 50000，normal 給 random）
   - NearWin mock 的符號必須是 `Game_Define.SCATTER_SYMBOL` 的值（不是 CASH/WILD）
   - `GenerateMockSpinAck` 回傳的 ISpinAck 必須包含 `TotalWin`
   - 建議 mock 物件加 type annotation（`const roundInfo: protocol.xxx.IRoundInfo = {...}`）讓 TS 攔缺欄位

**輸出**：Game_Define.ts + GameView.ts
**驗證**：`_gates.md` §3.4

---

## Step 3.5: Reel Module

📖 本步讀：`_api-ref.md` §SlotReels + `_pitfalls.md` §3.5 + Game_Summary_File
📖 若可變盤面：額外讀 `_api-ref.md` §附錄：可變盤面

1. 同步 6 處硬編碼（COL/ROW/FULL_PLATE_NUM/MAX_ROW/NORMAL_COLUMNS/ReelConfig）
2. 修正 m_reelPositionOffset 長度
3. SpinMode 專屬（dropEntry: SHOW_COLUMNS=1 + MIDDLE_PLATE_INDEX=0）
4. GameView.LoadSymbol 初始化（SetLayoutConfig/CreateSymbol/SetSpinMode/SetEntryStrategy）
5. Prefab Mask contentSize（公式計算）
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

1. 替換 AudioManager 音效清單（FileName 與 Game_Define.AudioClips 完全一致）
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
根據 FEATURES flags 擴充新 mode + 熱鍵（5=jackpot, 6=respin）。

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

## Step 4: Runtime Validation（需 Editor）

📖 無

1. editor_ping
2. scene_open MainGame.scene
3. preview_start → 等 10 秒檢查 console
4. Spine placeholder 綁定（4.2）

Editor 離線 → 跳過。

---

## Step 5: Report

📖 無（彙整結果）

1. 彙整所有步驟狀態
2. 跑 spec_traceability check-coverage
3. 跑 check_regression_v2
4. **Prefab 綁定檢測**：若盤面非 5×3 標準（Mask contentSize 被改過）或有 template 外新增 Spine → report 加 `⚠️ 手動：開 Cocos Editor 執行 Prefab 綁定（SkeletonData uuid + Mask contentSize 確認）`
5. 寫 `<target>/scratch/codegen-report.md`
6. 清除 checkpoint

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
| 4 Validation | 執行 | 執行 |
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
