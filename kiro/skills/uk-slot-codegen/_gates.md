# Mandatory Gates

每個 Step 結束後必跑的 grep/驗證命令。不通過 → 禁止往下走。
連續失敗 2 次 → 停止並報告具體失敗原因。

---

## §0 Preflight

```powershell
Test-Path "<target>/assets/Script/Game_Define.ts"  # mode=new 時 clone 完必須存在
Test-Path "<target>/extensions/astarte-framework"   # extensions 必須存在
Test-Path "<target>/.git"                           # Step 0.2 之後必須存在（mode=new）
py "${SKILL_DIR}/uk-slot-codegen/gate_runner.py" --step git --target "<target>"
# ⚠️ Step 0.2 之後才跑：它會 exit 1，在 Step 0 / 0.1 結束時照字面跑必紅
# 另驗「至少一個 commit」與「remote 不是 uk_slot_template」——只驗 .git 存在
# 會放過 init 後 commit 失敗、與 Step 0.0 的 rm .git 失敗這兩種帶錯 history 的狀態
```

---

## §1 Spec Ingestion

```powershell
Test-Path "<target>/scratch/Game_Spec.md"           # 非空
(Get-Content "<target>/scratch/Game_Spec.md").Length -gt 0
```

---

## §1.5 Spec Traceability

```powershell
py "${SKILL_DIR}/uk-slot-codegen/spec_traceability.py" check-coverage --spec "<target>/scratch/Game_Spec.md" --client "<target>"
# codegen-owned 全部有 value/path evidence；inferred defaults 與 deferred M2+ 僅列統計
```

---

## §2 Summary

```powershell
Test-Path "<target>/scratch/Game_Summary_File.md"
Select-String -Path "<target>/scratch/Game_Summary_File.md" -Pattern "SpinMode"
# 必須有 SpinMode: standard | dropEntry
```

---

## §3.1 Game_Define

```powershell
# SYMBOL_COUNT 必須是硬編碼數字（禁止 Object.keys 動態計算）
Select-String -Path "<target>/assets/Script/Game_Define.ts" -Pattern "SYMBOL_COUNT\s*=\s*\d+"
# 若無輸出 → 未完成

# Symbol enum 的 ID 集合 = Game_Spec 中所有非 server_only SymID
# server_only 只屬於 server/protocol，不計入 client enum、SYMBOL_COUNT 或 prefab 數量
py ${SKILL_DIR}/uk-slot-codegen/check_regression_v2.py --spec "<target>/scratch/Game_Spec.md" --client "<target>"
# symbol_count 必須 PASS；輸出會列 client IDs 與排除的 server-only IDs

# Symbol enum member 數量 = SYMBOL_COUNT 值（由同一 regression 自動驗證）
```

---

## §3.2 GameView — enum/SetStateMachine/NextState 三方一致

```powershell
# 收集所有 NextState 引用的 key
Select-String -Path "<target>/assets/Script" -Pattern "NextState.*GAMEVIEW_STATE\.(\w+)" -AllMatches | 
  ForEach-Object { $_.Matches.Groups[1].Value } | Sort-Object -Unique

# 每個 key 必須同時存在於：
# 1. Game_Define.ts 的 enum GAMEVIEW_STATE
# 2. GameView.ts 的 SetStateMachine() 註冊

# CommonState 完整性：RoundShowEndState 必須跳 COMMON_SHOW（不能自行替換）
Select-String -Path "<target>/assets/Script/GameState/RoundShowEndState.ts" -Pattern "CommonState\.COMMON_SHOW"
# ≥1

# ForEndToNext 非 FG 路徑必須跳 CommonState.END
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "CommonState\.END"
# ≥1

# RetryRoundEnd 禁止 USE_MOCK_SERVER guard（Mock 仍接真 server）
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "RetryRoundEnd" -Context 0,3 |
  Select-String -Pattern "USE_MOCK_SERVER"
# 必須為空（不可有 mock guard）
```

---

## §3.3 Proto

```powershell
# 以下 3 條全部必須回傳空（無殘留）
Select-String -Path "<target>/assets/Script" -Pattern "eyestrike" -Recurse | Select-Object -First 1
Select-String -Path "<target>/assets/Script" -Pattern "@igs-arcade-division" -Recurse | Select-Object -First 1
Select-String -Path "<target>/assets/Script" -Pattern "ar2esProto" -Recurse | Select-Object -First 1

# 正面驗證：新 namespace 出現在 proto 檔案中（防止 replace 漏做）
Select-String -Path "<target>/assets/Script/Test/*.js" -Pattern "\$root\.<NEW_NS>"
# ≥1（新 namespace 在 js 中正確出現）
Select-String -Path "<target>/assets/Script/Test/*.d.ts" -Pattern "namespace <NEW_NS>"
# ≥1（新 namespace 在 d.ts 中正確出現）
# <NEW_NS> 替換為實際 namespace（如 ar2lpProto）

# CColumn 欄位名必須是 Col（不是 Symbol）
Select-String -Path "<target>/assets/Script/Test/*.js" -Pattern "CColumn" -Context 0,2
# 確認輸出含 this.Col = []（不是 this.Symbol = []）

# SpinAck.decode 必須有完整實作（不能只是空殼 return）
Select-String -Path "<target>/assets/Script/Test/*.js" -Pattern "SpinAck.decode"
# ≥1，且函式體應含 reader.uint32() 或 $Reader 呼叫

# Proto.ts bridge 格式驗證（不要直接檢查 GameView 的底層 .js import）
Select-String -Path "<target>/assets/Script/Proto.ts" -Pattern 'import protocol from ".*\.js"'
# ≥1（default runtime import + .js）
Select-String -Path "<target>/assets/Script/Proto.ts" -Pattern 'export default protocol'
# ≥1（保留 CJS runtime object）
Select-String -Path "<target>/assets/Script/Proto.ts" -Pattern 'export type \{ <NEW_NS> \}'
# ≥1（namespace type export）
Select-String -Path "<target>/assets/Script/Proto.ts" -Pattern 'export \*'
# 必須為 0（export * 不能取代 default runtime export）

# 自動契約 gate：runtime namespace/constructor + Mock 欄位與 placeholder 一致
py ${SKILL_DIR}/uk-slot-codegen/verify_compile.py <target>
# exit code 0 = PASS
```

---

## §3.4 Mock Server

```powershell
# 以下全部必須有輸出
Select-String -Path "<target>/assets/Script/Game_Define.ts" -Pattern "USE_MOCK_SERVER"
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "GenerateMockSpinAck"
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "USE_MOCK_SERVER"

# InitMockKeyboard 必須被呼叫（不能只定義不呼叫）
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "this\.InitMockKeyboard\(\)"
# ≥1（在 start() 裡呼叫）

# Mock 資料格式驗證
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "Symbol.*JPState.*Number"
# ≥1（CSymbol 物件格式）

Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "MainPlateSymbol"
# ≥2（Mock 賦值 + OnRecvSpinAck 讀取）

Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "FreePlateSymbol"
# freegame 分支必須給非空 FreePlateSymbol

# Mock IRoundInfo 欄位完整性：RoundWin 必須存在（缺失→NaN→報獎跳過）
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "RoundWin"
# ≥2（mock 賦值 + AwardState 讀取）

# Symbol Effect cheat：5=symboleffect，固定三格中獎假資料；jackpot 保留到 7
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "case 'symboleffect'"
# 外部 ID 固定採 MAX_ROW；5×3 第一排依 columnAlignment 為 top [0,5,10]、center [1,6,11]、bottom [2,7,12]。
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "DIGIT_5" -Context 0,3 |
  Select-String -Pattern "symboleffect"
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "DIGIT_7" -Context 0,3 |
  Select-String -Pattern "jackpot"

# NearWin mock 符號一致性：必須用 SCATTER_SYMBOL 的值（不是 CASH/WILD）
# 確認 nearwin 分支的 Symbol 賦值包含 Game_Define 中定義的 Scatter enum 值
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "nearwin" -Context 0,5 |
  Select-String -Pattern "Symbol\s*="
# ≥1（nearwin 分支有設 symbol）

# SCATTER_SYMBOL 必須是單一 enum member（Symbol.XXX）— 不可是 array 或裸數字
Select-String -Path "<target>/assets/Script/Game_Define.ts" -Pattern "SCATTER_SYMBOL\s*=\s*\["
# 必須為 0（不可是 array）
Select-String -Path "<target>/assets/Script/Game_Define.ts" -Pattern "SCATTER_SYMBOL\s*=\s*Symbol\."
# ≥1（必須用 enum member 賦值）

Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "IsGoingToFree\s*=\s*true" |
  Select-String -NotMatch "^\s*//"
# ≥1（取消註解，不能是 // 開頭的行）

Select-String -Path "<target>/assets/Script/GameState/CheckState.ts" -Pattern "CurPlateIndex.*RoundQueue\.length"
# ≥1（FG 離場判斷啟用）
```

See also: `_pitfalls.md` §3.4

---

## §3.5 SpinMode

```powershell
# 確認 preset 選擇正確
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "REEL_LAYOUT_PRESETS\.(standard|dropEntry)"
# dropEntry 遊戲必須是 dropEntry；standard 遊戲必須是 standard

# === 以下僅 SpinMode = dropEntry 時驗證 ===
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "SetEntryStrategy\s*\(\s*new\s+DropEntryStrategy"
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "SetSpinMode\s*\(\s*SpinMode\.Tumble"
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "TumbleFillStrategy"
Select-String -Path "<target>/assets/Script/GameView.ts" -Pattern "DropEntryStrategy"
# 以上 4 條若任一為空 → 策略未啟用

# Mask contentSize 驗證（自動修正 + 驗證）
py ${SKILL_DIR}/uk-slot-codegen/fix_mask_size.py <target>
# 輸出 "OK" 或 "DONE" 代表通過；"ERROR" 代表 Game_Define 缺常數
Select-String -Path "<target>/assets/game/Prefab/Reel/SlotPlate_MG.prefab" -Pattern '"_contentSize"' -Context 0,2
```

---

## §3.6 Scaffold — State files + Directory

```powershell
# 每個在 SetStateMachine 註冊的 state 都必須有對應 .ts 且含 export class
$stateFiles = Get-ChildItem "<target>/assets/Script/GameState" -Filter "*.ts"
foreach ($f in $stateFiles) {
    $content = Get-Content $f.FullName -Raw
    if ($content -notmatch "export class") { "FAIL: $($f.Name) missing export class" }
}

# 每個自訂 state 的 OnEnter 必須有 NextState 出口（防卡死）
$noExit = $stateFiles | Where-Object {
    $c = Get-Content $_.FullName -Raw
    $c -match "OnEnter" -and $c -notmatch "NextState" -and $c -notmatch "m_isShowAwardEffectEnd"
}
if ($noExit) { "FAIL: states without NextState exit: $($noExit.Name -join ', ')" }
```

See also: `_pitfalls.md` §3.2

---

## §3.7 Audio — 逐一精確比對

```powershell
# 從 AudioManager.ts 抽取所有 AudioClips FileName（case-sensitive 比對）
$amPath = "<target>/assets/Script/Audio/AudioManager.ts"
if (-not (Test-Path $amPath)) { $amPath = "<target>/assets/Script/GameAudio/AudioManager.ts" }
$fileNames = [regex]::Matches((Get-Content $amPath -Raw), 'FileName:\s*"(\w+)"') | ForEach-Object { $_.Groups[1].Value }

# 取 Sound/ 目錄的實際檔名（不含副檔名），做 case-sensitive 比對
$soundDir = "<target>/assets/game/Sound"
$actualFiles = Get-ChildItem "$soundDir/*.m4a" | ForEach-Object { $_.BaseName }
$missing = $fileNames | Where-Object { $_ -cnotin $actualFiles }
if ($missing) { "FAIL: audio case mismatch or missing: $($missing -join ', ')" }
```

---

## §3.10 Feature Code

```powershell
# FreeGame Spine 呼叫驗證（有 FG 時）
Select-String -Path "<target>/assets/Script/GameState/EnterFreeState.ts" -Pattern "FgDeclare"
# ≥1
Select-String -Path "<target>/assets/Script/GameState/LeaveFreeState.ts" -Pattern "FgCompliment"
# ≥1
Select-String -Path "<target>/assets/Script/GameState/EnterFreeState.ts" -Pattern "PlayAnimation|PlayInLoop"
# ≥1
Select-String -Path "<target>/assets/Script/GameState/LeaveFreeState.ts" -Pattern "PlayAnimation|PlayInLoop"
# ≥1
# BigWin 呼叫存在（公版 API 是 BigWin.Show，不是 GameView.ShowBigWin）
Select-String -Path "<target>/assets/Script/GameState/AwardState.ts" -Pattern "BigWin\.Show\(|BigWin\.NewShow\("
# ≥1（BigWin.Show 呼叫存在）
Select-String -Path "<target>/assets/Script/GameState/AwardState.ts" -Pattern "BigWin\.Show" | Select-String -NotMatch "/\*|^\s*//"
# ≥1（不在註解裡）
Select-String -Path "<target>/assets/Script/GameState/AwardState.ts" -Pattern "ShowBigWin\("
# 必須為 0（ShowBigWin 不是公版 API，正確用法是 this.m_gameView.BigWin.Show()）

# AwardState 用 AudioManager（不能用 soundManager / Game_Define.AudioClips）
Select-String -Path "<target>/assets/Script/GameState/AwardState.ts" -Pattern "AudioManager\.Play"
# ≥1
Select-String -Path "<target>/assets/Script/GameState/AwardState.ts" -Pattern "soundManager\.Play"
# 必須為 0（soundManager 不接受字串 key）
Select-String -Path "<target>/assets/Script/GameState/AwardState.ts" -Pattern "Game_Define\.AudioClips"
# 必須為 0（AudioClips 定義在 AudioManager 上，不在 Game_Define）

# NearWin 按 SpinMode 分流
# Standard → SlotReels 逐列停輪觸發
# DropEntry → EffectStartState 消除結束觸發
```

---

## §H1 Feature Prefab

```powershell
# SymbolEffectPrefab 複製數量 = SYMBOL_COUNT
$prefabs = Get-ChildItem "<target>/assets/game/Prefab/Reel/SymbolEffect" -Filter "*.prefab" | Measure-Object
# Count >= SYMBOL_COUNT

# Texture、atlas、母版與各 Prefab UITransform 必須為 178x178；另驗 UUID、SymbolSpine 與 m_symbolId
py "${SKILL_DIR}/uk-slot-codegen/bind_symbol_effect_prefabs.py" "<target>" --check

# 實體 cell 依目前 ReelLayoutConfig 建立；外部 position 固定採 MAX_ROW，向上擴張的小盤面以 bottom alignment 映射。
# MAX_ROW > ROW 時，standard 必須用 targetSymbolCount=MAX_ROW、visibleSymbolCount=ROW；center 對齊的可視起始 row 為 floor((MAX_ROW-ROW)/2)，不得另造 expanded preset 或 boardRowAlignment。
# EffectPlate 使用 SlotReels 的 position 轉換 API 與目前 SingleCell 世界座標，禁止 ±SymbolHeight 補償。
py "${SKILL_DIR}/uk-slot-codegen/gate_runner.py" --step H1 --target "<target>"
```

---

## §H2 Symbol PNG

```powershell
$dir = "<target>/assets/game/Img/Symbol/MG"
$pngs = (Get-ChildItem $dir -Filter "Symbol_*.png" | Measure-Object).Count
# pngs >= SYMBOL_COUNT

# 每張 .meta 必須有 f9941 spriteFrame sub-asset
Get-ChildItem $dir -Filter "Symbol_*.png.meta" | ForEach-Object {
  $json = Get-Content $_.FullName | ConvertFrom-Json
  if (-not $json.subMetas.PSObject.Properties.Name -contains 'f9941') { $_.Name }
}
# 必須無輸出（全部有 f9941）
```

---

## §H4 Art Manifest

```powershell
Test-Path "<target>/ART_ASSET_MANIFEST.md"
```

---

## §BOM 通用 Encoding Gate（每步結束後附加執行）

```powershell
# 先自動補齊 codegen-owned TypeScript BOM
py ${SKILL_DIR}/uk-slot-codegen/ensure_ts_bom.py "<target>"
# exit code 0；可重複執行

# 驗證所有 codegen 產出/修改的 .ts 檔案保留 UTF-8 BOM（EF BB BF）
# BOM 遺失 → Cocos Babel parser 報 InvalidEscapeSequenceTemplate → __unresolved_X runtime error
$tsFiles = Get-ChildItem "<target>/assets/Script" -Recurse -Filter "*.ts"
$noBom = @()
foreach ($f in $tsFiles) {
    $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
    if ($bytes.Length -ge 3 -and -not ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)) {
        $noBom += $f.FullName
    }
}
if ($noBom.Count -gt 0) { "FAIL: BOM missing in: $($noBom -join ', ')" }
# 必須為空（所有 .ts 都有 BOM）
```

See also: `_pitfalls.md` §通用 Encoding

---

## §5 Report

```powershell
Test-Path "<target>/scratch/codegen-report.md"

# 先產生診斷 report，再跑最終 gate
py ${SKILL_DIR}/uk-slot-codegen/gate_runner.py --step finalize --target "<target>"
# all_pass=true 才能清 checkpoint 或宣告完成
# codegen traceability missing、regression FAIL/SKIP、compile/proto/report schema 失敗都必須停止；inferred defaults／deferred M2+ 不阻擋
```

See also: `_pitfalls.md` §通用

---

## 通用規則

- Gate 失敗 → 嘗試修正 → 重跑驗證
- 連續失敗 2 次同一 gate → 停止報告
- `_flow.md` 每步結尾會標注「驗證：`_gates.md` §X.X」指向本文件對應段落
- §BOM gate 在每步修改 .ts 後追加執行（不用等到 Step 5）

---

## Gate 失敗 → Pitfall 快速索引

Gate 失敗時，參考以下 mapping 快速定位修復方法：

| Gate 段落 | 常見失敗原因 | 對應 Pitfall |
|-----------|-------------|-------------|
| §0 Preflight | extensions 路徑錯 | `_pitfalls.md` §0 第1條 |
| §3.1 SYMBOL_COUNT | enum 成員數 ≠ 硬編碼值 | `_pitfalls.md` §3.1 第2條 |
| §3.2 三方一致 | state 有 enum 但沒 register | `_pitfalls.md` §3.2 第3條 |
| §3.2 COMMON_SHOW | RoundShowEndState 被改 | `_pitfalls.md` §3.2 第4條 |
| §3.3 殘留 namespace | replace 漏做 d.ts | `_pitfalls.md` §3.3 第7條 |
| §3.3 正面 namespace | replace 誤傷或未執行 | `_pitfalls.md` §3.3 第1條 |
| §3.4 InitMockKeyboard | 只定義沒呼叫 | `_pitfalls.md` §3.4 第10條 |
| §3.6 export class 缺失 | state 整檔被註解 | `_pitfalls.md` §3.2 第1條 |
| §3.6 NextState 出口 | OnEnter 沒有 NextState | `_pitfalls.md` §3.10 第3條 |
| §3.7 audio case mismatch | FileName 大小寫不一致 | `_pitfalls.md` §3.7 第1條 |
| §3.10 BigWin.Show | 用了 ShowBigWin | `_pitfalls.md` §3.10 第4條 |
| §3.10 AudioManager.Play | 用了 soundManager | `_pitfalls.md` §3.7 第4條 |
| §3.10 Game_Define.AudioClips | AudioClips 不在 Game_Define | `_pitfalls.md` §3.7 第5條 |
| §BOM | strReplace 吃掉 BOM | `_pitfalls.md` §通用 Encoding 第2條 |
| §5 tsc --noEmit | 型別錯誤 | 看 tsc 輸出的 file:line 定位 |
