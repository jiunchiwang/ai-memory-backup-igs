**User:**
<identity>
你是 moa-ref-codex，MoA blind advisor (Codex/OpenAI)。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Memory recall — dynamically retrieved facts relevant to this message]
[adversarial-review] (relevance 0.57)
- 2026-08-13 覆核紀律的邊界修正（由 kiro-cli glm-5 在開放式提問下指出，是 0-finding 那輪的真正產出）：「覆核者不需要任何 MCP tool ∴ 一律關掉」寫成無條件預設是錯的——判定依據不在檔案內容裡時關掉工具等於讓它無法驗證。四個例外：要實際打 API 端點、要觸發 CI/build、要查外部狀態（依賴版本/security advisory）、以及**改動的就是某個 MCP tool 本身（關掉 MCP 等於關掉被測物）**。正確規則是「覆核者需要哪些工具由覆核範圍決定，預設為零」。這也再次驗證 skill 第 4 條：清單式 prompt 得到 0 finding，真正的缺口是那個開放式問題挖出來的。
- 異源覆核的 findings 若機制描述錯了但效果描述對，應照效果修、不照它的說法寫進註解：2026-08-12 glm-5 主張「超大 timeoutMs 會讓 Date.now()+timeoutMs 溢出成 Infinity」，實測 Date.now()+Number.MAX_SAFE_INTEGER 仍是 Number.isFinite()===true、沒有溢出，只是 deadline 遠到不可能抵達。
- 2026-08-12 codegen git-init 五輪異源覆核抓到一個獨立的失效模式：**修正動作本身會產生新的假因果**（有別於既存那條 2026-07-31 的「因果宣稱與程式碼實際時序不符」——那條講的是原始敘述從意圖推理而來，這條講的是為了修上一條而新寫的句子）。同一形狀連出現三次：修「uk_872 gitlink 屬個案」→ 編出「是模板後來改掉了」（模板全史 72 commit 0 筆 160000，否證）；修「照模板不要加碼」→ 寫出「皆已被各自 .gitignore 擋」（實際是 local-only 的 .git/info/exclude）；修上一條 → 寫出「不在任何專案的 .gitignore 裡」（被 uk_872 的 78 條逐檔 glob 證偽）。共同機制是修正時數字擴大了、寫對了，卻順手補一個**沒有證據的機制解釋**，或把**有例外的觀察壓縮成全稱句**；這比原錯更難抓，因為數字都對、語氣自信、讀起來像考證過。防法：①文件只留觀察到的分布＋操作規則，成因明寫「未知，別替它補一個」；②全稱句（任何／都／皆）出手前先找一個反例，找不到才寫；③要寫因果就得先跑得出證據的查法——git log --all --raw 查全史是否出現過某 mode、ls-tree <root> 查初始狀態、log --reverse 比 root 日期、check-ignore -v 查是「誰」擋住的而非只看有沒有被擋。完整案例在 G:\AI\AIMemory\wiki\queries\codegen-git-init-gap.md。

[bridge-acp] (relevance 0.56)
- Codex hook 的實測結果（2026-08-13 黑箱探針，codex-cli 0.146.1 · Windows · 探針已清乾淨）：①**PreToolUse 的 tool_input 形狀因工具而異，且 apply_patch 不帶 file_path**——shell 進來是 `tool_name:"Bash"` + `tool_input.command`（實測值 `Get-Content -LiteralPath .\target.txt`），檔案編輯進來是 `tool_name:"apply_patch"` + `tool_input.command` 裝**整段 patch 原文**（`*** Begin Patch / *** Update File: <絕對路徑> / @@ / -hello / +world / *** End Patch`）∴ bridge repo 的 `.claude/hooks/impact-gate.mjs` 直接拿去用會**靜默失效**（它讀 `tool_input.file_path`，在 Codex 恆為 undefined → 走 `if (!filePath) process.exit(0)` fail-open，永遠不擋且無任何症狀），要重用必須改成從 patch 文字 parse `*** Update File:` / `*** Add File:` / `*** Delete File:`。其餘欄位齊全可直接用：session_id / turn_id / cwd / hook_event_name / tool_name / tool_use_id / transcript_path / model / permission_mode。②**專案層 `<repo>/.codex/hooks.json` 有兩道靜默閘門**，兩道都不通過就完全不執行且**不印任何警告**：(a) 該專案必須在 `~/.codex/config.toml` 有 `[projects.'<絕對路徑>'] trust_level = "trusted"`，否則專案的 .codex 設定根本不載入（實測：git init 過、用 -C 或真的 cd 進去都無效，補上 trust 後立刻生效）；(b) hook 腳本本身的 hash 要經 `/hooks` 互動式 review 信任，未信任會靜默跳過（實測：專案已 trusted 但不加 `--dangerously-bypass-hook-trust` 仍 0 捕獲）。③繞過檔案探索的可靠測法是 `-c 'hooks.PreToolUse=[{matcher="*",hooks=[{type="command",command="node <abs>"}]}]'`，這條**不受 (a) 影響**、只需 `--dangerously-bypass-hook-trust`。④matcher 是 regex，`"*"`／`""`／省略＝全比對；shell 的 tool 名是 `Bash` 不是 `shell`。
- 更正既有 fact「Claude Agent SDK 的 PreToolUse hook 無法用來補 bridge 缺的 L1 機械閘門，因為 Codex 與 Kiro 底下沒有 Agent SDK 也就沒有這個攔截點」——前提對（確實沒 Agent SDK）但結論錯：codex 與 kiro 各自實作了自己的 hook 系統。2026-08-13 實查：codex-cli 0.146.1 的 `codex features list` 顯示 `hooks  stable  true`（本機 Windows 已啟用），官方文件 developers.openai.com/codex/hooks（308 轉址到 learn.chatgpt.com/docs/hooks）列 11 個事件，本機 codex.exe binary 全部命中（PreToolUse/PostToolUse/PermissionRequest/PreCompact/PostCompact/UserPromptSubmit/SessionStart/SessionEnd/SubagentStart/SubagentStop/Stop）；PreToolUse **明確涵蓋 apply_patch 檔案編輯**（matcher 別名 apply_patch/Edit/Write），deny 方式與 Claude Code 同形（exit code 2 + stderr，或 hookSpecificOutput.permissionDecision=deny），binary 內 hookSpecificOutput/permissionDecision/permissionDecisionReason/additionalContext/stopReason 字串齊備；設定檔可放 **repo 層 `<repo>/.codex/hooks.json`** 或 config.toml 的 [hooks]。kiro-cli 2.18.0 binary 亦含 agentSpawn/userPromptSubmit/preToolUse/postToolUse 與 "hooks"/"trigger" 字串，但設定形狀未證實（無 matcher 欄位、~/.kiro/agents/main.json 無 hooks 欄位、無官方文件佐證）∴ kiro 只能說「疑似有、待驗」。⚠️ 第三方部落格兩條說法已被官方文件與本機實測推翻：「PreToolUse 只攔 shell 不攔 apply_patch」與「hooks 在 Windows 不可用」。

[uk-slot-clash-olympus] (relevance 0.56)
- uk_slot_clash_of_olympus 的 docs/ 整個目錄被 .gitignore:84 擋掉（dev-spec.md／spec-gaps.md／M0b-checklist.md 皆不在版控），2026-08-13 詢問後使用者裁決**維持現狀不納版控**，備份自理——所以那些設計紀錄是本機單一副本
- uk_slot_clash_of_olympus 的 // CHECK_JP 疑慮已於 2026-08-13 否證：Game_Define.ts:15 的 enum 成員、GameView.ts:636 的註冊、CheckJpState.ts 整檔三處一致註解，且 assets/ 與 extensions/ 內 NextState.*CHECK_JP 零命中 ∴ 無懸空轉場；可遷移判準是「危險的是關一半（enum 留著但註冊拿掉），三處一起關是乾淨的」。另 JPResult 無任何消費者，只有 mock 寫入與 RecoverSpinAck 複製
- uk_slot_clash_of_olympus 的 M0b（Editor/Runtime 驗證）進行中，2026-08-12：Preview 起得來、19 份 SymbolEffect 的 SkeletonData 綁定皆正常，但 symboleffect 熱鍵中獎演出完全不播（無錯誤訊息）；根因是 assets/Script/RecoverSpinAck.ts 的 TraverseAwardData() 把 AwardData 從 interface 轉 class 時漏複製 EliminatePos 欄位，proto stub 預設值 $util.emptyArray 導致 EffectPlate.SymbolWinEffect 的播放迴圈跑 0 次；已修（補一行 TraverseIntegerList 轉型），verify_compile.py 5/5 PASS，待使用者重測確認。
- 2026-08-13 uk_slot_clash_of_olympus 的 M2.1 已完成：新增純 VSManager.Resolve() 與 7 項單元測試，VS Collect 僅於收分時計入自身倍率且多個相加；專案編譯、spec-gaps 對帳與 codegen finalize gate 皆通過。M2.2 尚未開始，範圍為 proto/mock adapter 接 VsFeatureShowState、Fly/Expand/Spine 與 unshow/replay。
- uk_slot_clash_of_olympus 有一個潛伏的動畫命名不符：astarte-framework 的 BigWinAnimName.Max 找 MaxWin_Start/End，但資產 assets/game/Spine/BigWin/BigWin.json 提供的是 UltimateWin_Start/End，findAnimation 會回 null 且不報錯；現在 AwardState 最高只給 lvl=3（SUPER）故踩不到，接 MAX WIN 機制時會浮出，已記入該專案 ART_ASSET_MANIFEST.md
[End memory recall]

[Wiki retrieval — auto-loaded pages relevant to this message]
## [[codegen-git-init-gap]] (relevance 0.81)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/codegen-git-init-gap.md]
- 1. 缺口的形狀
- 2. 修法：Step 0.2 + 機械閘門
- 3. UK slot 專案的 git 追蹤慣例（實查，非推測）
- 4. 五輪異源覆核抓到的 12 條
- 5. 順帶回報但未動的既有問題
- 相關

## [[claude-agent-sdk]] (relevance 0.80)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/claude-agent-sdk.md]
- 1. 命名：Claude Code SDK → Claude Agent SDK
- 2. 定位：四路對照（最容易搞混的地方）
- 3. TypeScript API 面
- 4. 能力清單與授權限制
- 5. 與 telegram-kiro-bridge 的層次關係（本頁重點）
- 6. 對 bridge 可能有用但未實測的四點
- 7. 證據等級
[End wiki retrieval]

[Delegation Task — id: moaplan_design_converge]
Goal: 根據前兩份審查結果，為 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 收斂一份最小實作設計。目標是不重做 M2.1、不可臆造正式 server proto 或資產、且能驗證 mock 到 state 到 replay 的資料流。驗收：列出 BC/EH、精確修改邊界、分階段驗證命令；若先決條件不足，清楚縮小範圍而非假裝完整。回報格式：設計決策、BC/EH、檔案邊界、驗證清單。
Context: 此工項屬於計畫「為 Clash of Olympus M2.2 在實作前完成獨立設計審查，鎖定 adapter、演出時序與 unshow/replay 的最小可交付邊界。」。
前置工項「目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS proto mock adapter 設計。背景：M2.1 的 assets/Script/Feature/VSManager.ts 是純函式；M2.2 要由 VsFeatureShowState 將 stub VSResult 接入，並讓 GameView 的 vsfeature mock 產生可信的轉型前盤面。請自行讀 docs/M2-VS-design.md、docs/modules.md、GameView.ts、VsFeatureShowState.ts、RecoverSpinAck.ts 與 proto stub。待決問題：最小改動檔案集合、資料適配責任、server proto 到來時的替換邊界。驗收：提出具體檔案與方法層級的設計，指出不可違反的 M2.1 契約。回報格式：結論、檔案清單、風險、建議測試。」的**結構化結果**（完整，未截斷）：
{
  "summary": "審查完成：M2.2 adapter 應以 VSManager.ts 內的純函式（type-only import colProto，維持 ts-node 可測性）處理 proto→VSResolveInput 轉換，VsFeatureShowState 只做呼叫與播放；但現有 GameView vsfeature mock 有兩處實質 bug（col0 放轉型後符號 VsCollect 而非 Collect、VSResult 缺 reelIndex）會讓 Resolve() 恆不觸發，必須與 adapter 一併修正。另有 plateAfter 交棒缺口（沒有寫回顯示盤面的機制）是 M2.2 範圍內必須釘的整合點。",
  "files": [
    "assets/Script/Feature/VSManager.ts — 新增 AdaptRoundToVSInput() 純函式",
    "assets/Script/GameState/VsFeatureShowState.ts — PlayVsFeature() 呼叫 adapter+Resolve()，並把 plateAfter 寫回顯示盤面",
    "assets/Script/GameView.ts — 修正 vsfeature mock：Symbol.VsCollect→Symbol.Collect，VSResult 補 reelIndex:0",
    "tests/（新增或擴充）— AdaptRoundToVSInput 純函式單元測試"
  ],
  "risks": [
    "proto IVSResult.vsType 數值編碼未定案（symbol id vs 獨立 enum），僅有 mock 先例可循，需登記 spec-gap",
    "VSManager.Resolve() 回傳的 plateAfter 目前無任何寫回顯示層/CollectFeatureShowState 的機制，畫面會與資料脫節",
    "若依 M2-VS-design.md 字面把轉換邏輯寫進 VsFeatureShowState（import cc），會喪失現有 ts-node --transpile-only 可測性，建議留在 VSManager.ts",
    "GameView mock 現狀（col0 用轉型後符號、VSResult 缺 reelIndex）會讓 Resolve() 恆回傳 isTriggered=false，等同沒接",
    "M2.1 設計文件（安全略過）與 dev-spec.md 規格權威 S1（warn 不改行為）對「類型不符」的措辭不一致，雖因欄位互斥實務不會觸發，但文件應對齊",
    "FreePlateSymbol 尚未接線（GameView.ts:1527 註解掉），VS adapter 沿用現狀只吃 MainPlateSymbol 可接受但需留 TODO 錨點",
    "unshow/replay 本切片不做，但 plateAfter 套用方式若寫死會讓下一切片重做，建議設計成保留 transform 前快照"
  ],
  "tests": [
    "AdaptRoundToVSInput 純函式單元測試（ts-node --transpile-only 慣例）：reelIndex 缺失 fallback 到 appliedPositions[0].col；vsType 無法辨識分支",
    "修正 mock 後於 Cocos Preview 手動按熱鍵 8（vsfeature），確認 VsFeatureShowState 真的進入 PlayVsFeature 而非直接跳過",
    "Collect 演出開始前，人工確認畫面盤面符號已是 VsCollect(18) 而非殘留舊符號"
  ]
}
以下是它的文字說明（推理過程；可能被截斷）：## 結論

M2.2 的最小改動方案：把 proto→VSManager 輸入的轉換寫成 **VSManager.ts 內的純函式**（不是塞進 VsFeatureShowState），靠 `import type { colProto }` 保持零 cc 依賴，沿用既有的 `ts-node --transpile-only` 測試方式；VsFeatureShowState 只做「呼叫 adapter → Resolve() → 依 steps 播動畫 → 把 plateAfter 套回顯示盤面」。但目前的 mock（GameView.ts:904-915）在型別上就會讓 `Resolve()` 永遠 `isTriggered=false`——這不是新缺口，modules.md 已經寫明要在 M2.2 修，adapter 設計必須連同這處修正一起交付，否則接了也等於沒接。

## 檔案清單

1. **`assets/Script/Feature/VSManager.ts`**（新增，不改既有 `Resolve()`）
   - 新增 `import type { colProto } from "../Proto";`
   - 新增匯出函式 `AdaptRoundToVSInput(plate: ReadonlyArray<colProto.ICColumn>, vsResult: ReadonlyArray<colProto.IVSResult> | null | undefined, symbolIds: VSSymbolIds): VSResolveInput`
     - plate：`col.Col.map(cell => ({Symbol: cell.Symbol??0, Number: cell.Number??0, JPState: cell.JPState??0}))`
     - vsResults：`reelIndex = raw.reelIndex ?? raw.appliedPositions?.[0]?.col`；缺兩者則整筆丟棄並 `console.warn`（連 reelIndex 都沒有，無法進 `VSResolveWarning`）
     - vsType：把 raw 數值（依現有 mock 先例是 symbol id）對照 `symbolIds.vsCash→'cash'`／`symbolIds.vsCollect→'collect'`；無法辨識時記一筆獨立於 VSManager 內部 warning 之外的 adapter-level warning
   - 因為只用 `import type`，不影響 `tests/VSManager.test.ts` 現有的 ts-node 執行路徑

2. **`assets/Script/GameState/VsFeatureShowState.ts`**
   - `PlayVsFeature()` 呼叫 `AdaptRoundToVSInput` + `VSManager.Resolve()`
   - `!result.isTriggered` 時直接跳過（維持現有「無 VS 就跳 State」語意的延伸）
   - 依 `result.steps` 順序（Cash 組已排在前、Collect 組在後）逐步做 Fly/Expand/Spine
   - **關鍵**：`OnLeave()`/播放結束前，必須把 `result.plateAfter` 寫回實際顯示盤面（`SlotReels.SetPlateInfo` 或等效呼叫），否則 CollectFeatureShowState 進場時畫面符號跟資料不同步

3. **`assets/Script/GameView.ts`**（修正既有 bug，非新增功能）
   - Line 908：`Symbol.VsCollect` → `Symbol.Collect`（轉型前盤面不該放轉型後符號，否則 `VSManager` 的 `HasSymbol(plate, symbolIds.collect)` guard 直接失敗）
   - Line 910-912：`VSResult` 條目補上 `reelIndex: 0`（目前完全沒有這個欄位）

4. **測試**：在 `tests/` 下對 `AdaptRoundToVSInput` 補純函式單元測試（走既有 `ts-node --transpile-only` 慣例），涵蓋 reelIndex 缺失 fallback 與 vsType 無法辨識兩個分支。

## 風險

1. **vsType 數值編碼未定案**：proto stub 的 `IVSResult.vsType` 是 `number`，語意未寫死；唯一現有先例（mock）用的是 symbol id（`VsCollect=18`）。建議照此先例做轉換，但要登記進 `docs/spec-gaps.md`，因為真 proto 到手前無法排除是另一套獨立 enum（同類先例：GAP-04 倍率書寫語意也是「暫定非定案」）。
2. **plateAfter 沒有交棒點**：`VSManager.Resolve()` 回傳轉型後盤面，但目前沒有任何程式碼把它寫回顯示層或傳給 `CollectFeatureShowState`。兩份設計文件都沒明講由誰負責這一步——這正是 M2.2 要釘的整合點，不能只加 adapter。
3. **可測性衝突**：`docs/M2-VS-design.md` 原文字面說「下一切片才在 VsFeatureShowState 轉換」，但該檔 import `cc` 的 `log`，塞進去會讓轉換邏輯脫離 `ts-node --transpile-only` 可測範圍。建議把純轉換邏輯放回 VSManager.ts（同檔案、type-only import），State 只做呼叫，兩者都沒有違反「之後只改 adapter、不改 `Resolve()` 規則核心」的既定方向。
4. **Mock 現狀會讓 Resolve() 恆不觸發**：col0 放轉型後符號 + 缺 reelIndex，兩者疊加後即使接上 adapter，`isTriggered` 也會是 false，等同沒接——modules.md 已預告，須與 adapter 一起修，不可分開處理。
5. **文件間用字落差（低嚴重度）**：M2.1 設計文件說「類型不符→安全略過」，但 `docs/dev-spec.md`（規格權威）S1 寫「不符→dev-only warn，不改行為，以 server 為準」。現行 `VSManager.IsValidReel` 是前者（整筆過濾掉）。因規格已證明兩類型欄位互斥（col 0/COL-1 只可能 collect，1~COL-2 只可能 cash），實務上此分支不會真的觸發，但建議至少把兩份文件的措辭對齊，避免日後真 server 出現邊界輸入時行為跟文件描述兜不起來。
6. **FreePlate
…（此結果原長 4754 字，只帶前 3000 字）
前置工項「目標：審查 G:\Cocos_Project\uk_slot_clash_of_olympus 的 M2.2 VS Feature 演出與 unshow/replay 時序。背景：需要在 VsFeatureShowState 依 VSManager steps 串 Fly Expand Spine，且轉型前盤面用於還原、轉型後盤面用於收分。請自行讀 docs/M2-VS-design.md、docs/dev-spec.md 的 VS 段、GameView.ts、Game_Define.ts、VsFeatureShowState.ts、CollectFeatureShowState.ts、RecoverSpinAck.ts、SlotReels.ts。待決問題：現有框架有哪些既有 API 可最小復用，何時保存與恢復快照，無資產時如何避免假演出。驗收：給出狀態流程與可測驗收條件，指出 race 或 replay 風險。回報格式：結論、狀態流、風險、建議測試。」的**結構化結果**（完整，未截斷）：
{
  "summary": "M2.2 應把 VsFeatureShowState 做成薄 adapter：轉 proto → 呼叫已測過的 VSManager.Resolve() → 依 steps 播 Fly/Expand/Spine（此三者框架皆無現成元件，需新建）→ 把結果交給 CollectFeatureShowState。核心結論：plateAfter（轉型後盤面）不需要持久化，因為 Resolve() 是純函式，任何時候都能從已存在的 RoundInfo.MainPlateSymbol + VSResult 重算出來，unshow/replay 只要重跑 Resolve() 即可，不必等 GAP-09 的 proto 補欄位。但目前 unshow 的基礎還原路徑（CurPlateIndex 回復、畫面回放）在 UnshowPrepareState.ts 是整段 TODO 註解，尚未實作——VS Feature 繼承這個模板級缺口，不應在 M2.2 單獨解。另外現有 GameView.ts 的 'vsfeature' mock 資料不合法（直接寫已轉型的單格 VsCollect，沒有 Vs(16) 種子、不是 1x4），無法用來整合測試真正的 Resolve() 路徑，需改寫。",
  "flow": [
    "ScatterShowState.OnEnter → NextState(VS_FEATURE_SHOW)",
    "VsFeatureShowState.OnEnter: 讀 SpinAck.RoundQueue[CurPlateIndex].VSResult，空則直接 NextState(COLLECT_FEATURE_SHOW) 不做視覺變動",
    "AdaptVSResult(RoundInfo.MainPlateSymbol, vsResult, symbolIds) → 轉成 VSManager 的 VSResolveInput（唯一新增的業務轉換碼）",
    "VSManager.Resolve(input) → 取得 plateAfter / vsValues / collectWins / steps（M2.1 已測過，不重寫規則）",
    "依 steps 逐欄播放：Cash 組(col遞增)先 Fly+Expand覆蓋成VsCash(17) → Collect 組(col遞增)後 Fly+Expand覆蓋成VsCollect(18) → 對決/倍率 Spine 美術字（資產未到位時走 optional-component null guard 降級，仿 AwardState.ts 的 BigWin 寫法）",
    "GameView.VsFeatureResult = result（新欄位，作為與 CollectFeatureShowState 之間唯一的交接管道）",
    "NextState(COLLECT_FEATURE_SHOW)",
    "CollectFeatureShowState.OnEnter: 讀 CollectResult + GameView.VsFeatureResult.collectWins[col]，依 Cash先/COLLECT後 順序收分，不重算 S0-S4",
    "NextState(AWARD)",
    "(未來，等 UnshowPrepareState 的基礎還原補上後) 回放某輪：SetNowRoundInfo(round) → 重新呼叫 VSManager.Resolve(round.MainPlateSymbol, round.VSResult) → 用類似 SlotReels.SetPlateSymbolForUnshow 的無動畫寫入方式直接渲染 plateAfter，不需要新的持久化欄位"
  ],
  "risks": [
    "【高，框架級】BaseState/StateManager 無取消機制（StateManager.ts 只有 NextState/Current，無 isActive 或 signal）。VsFeatureShowState.OnEnter 是本輪最長的 await 鏈（多欄 Fly+Expand+Spine 依序播放），若播放期間外部強制 NextState()（如重連/skip），stub 播完仍會無條件呼叫 NextState(COLLECT_FEATURE_SHOW) 蓋掉中斷後真正該去的狀態——與專案已知的 await-gap-opens-finalize-race 教訓同形，VS 是曝光窗口最大的一站",
    "【高】GameView.ts 現有 'vsfeature' mock（約 line 904-914）不合法：MainPlateSymbol 直接寫已轉型的單格 VsCollect，沒有 Vs(16) 種子也不是 1x4 整欄，餵給 VSManager.Resolve() 會在 S0/S1 就判定不成立，等於這份 mock 目前測不到 M2.2 要接的真實路徑，必須先改寫",
    "【中】Collect 收分係數交接管道不存在：CollectFeatureShowState 目前只讀自己的 CollectResult，S5 算法需要的 collectMul[col] 沒有任何 GameView 欄位可以帶過去；若在 Collect 狀態重算等於複製一份 S0-S4 邏輯，兩份實作會漂移",
    "【中】GAP-09 對 plateAfter 的 cross-check 目前只設計給 vsType（S1 的 server/client 推導比對），若 server 未來真的補一個轉型後盤面欄位，client 算的 plateAfter 不能默認正確，需要同款 dev-only warn 機制但目前沒有預留",
    "【低】unshow 基礎還原路徑（UnshowPrepareState.ts 約 line 37-43）整段是 TODO 註解，CurPlateIndex 回復與畫面回放都未實作——這是模板級缺口，VS Feature 只是繼承，不應在 M2.2 單獨解決",
    "【低】GAP-04 美術資產（倍率書寫語意、美術字張數）未定案，PlayVsFeature 若對美術元件寫死依賴會在資產未到位時整段掛掉"
  ],
  "tests": [
    "Adapter 單元測試：colProto.IVSResult[] → VSResolveInput.vsResults 轉換正確，含現有錯誤 mock 形狀應被判定不成立的案例",
    "改寫後的合規 vsfeature mock 跑 Editor Preview：驗證 Cash 組先於 Collect 組播放、覆蓋後該欄 4 格皆為 17/18",
    "無資產/關閉 flag 路徑：Game_Define.FEATURES.VS_FEATURE=false 或 vsResult=[] → 斷言零視覺變動、直接 NextState(COLLECT_FEATURE_SHOW)",
    "交接測試：VsFeatureShowState 算出的 collectWins[col] 與 CollectFeatureShowState 實際收到的金額逐欄比對相等",
    "中斷測試：把 PlayVsFeature 內某個 await 換成手動 resolver，pending 期間外部呼叫 stateManager.NextState(其他狀態)，斷言最終狀態是外部設定的那個而非被 stale continuation 蓋回",
    "Derive-not-persist 一致性測試（等 unshow 基礎路徑補上後才跑）：同一 RoundInfo 呼叫兩次 Resolve()，斷言 plateAfter/collectWins 逐位元相同"
  ]
}
以下是它的文字說明（推理過程；可能被截斷）：I'll start by reading the design docs and relevant source files for this review task.Good, found all files. Let me read them in parallel.## 結論

M2.1 的 `VSManager.Resolve()`（純函式，7/7 測試通過）已經把 VS Feature 的全部業務規則定案，M2.2 應該把 `VsFeatureShowState` 定位成**薄的 adapter + 演出層**：轉 proto → 呼叫 `Resolve()` → 依 `steps` 逐步播 Fly/Expand/Spine → 把結果交給 `CollectFeatureShowState`。目前 `VsFeatureShowState.ts` 與 `CollectFeatureShowState.ts` 都是空 stub（只有觸發判斷，`PlayVsFeature`/`PlayCollectFeature` 內容全空），`GameView.ts` 也還沒有任何欄位承接兩者之間的資料交接。

框架既有 API 可直接複用：`SlotReels.SetPlateSymbolForUnshow()`（無動畫、直接依資料寫死盤面）示範了「瞬間切到某個盤面狀態」該怎麼寫；`ColumnSymbol.SetSymbolInfos()/ChangeSymbol()` 是動畫結束後定案外觀的正確落點；`EffectPlate/SymbolSpine.ts`、`Spine/BaseSpine.ts`/`InLoopOutSpine.ts` 是「對決」idle spine 該仿的殼。但**跨格符號的 Fly/Expand（VS Cash/Collect 1×4）完全沒有現成元件**——`MaskExpand/` 是整盤遮罩，不是單符號佔多格；全專案 grep `Fly` 只有常數與音效名稱，沒有任何飛行動畫實作——這是要新建的元件，dev-spec 已經明確指出這點，本次審查確認無誤。

**最關鍵的一個結構性判斷**：dev-spec 把「轉型前/轉型後兩個盤面快照」講得很清楚，但沒講清楚的是——**轉型後盤面（`plateAfter`）不需要被持久化**。因為 `Resolve()` 是純函式、輸入只是 `RoundInfo.MainPlateSymbol`（轉型前，已存在 `SpinAck` 裡）與 `RoundInfo.VSResult`（也已存在），所以任何時候要「回到某一輪的 VS 結果」，只要重跑 `Resolve()` 就能得到一模一樣的 `plateAfter`/`collectWins`——不需要額外欄位、不需要 proto 補 log（GAP-09 對 VS 這條路徑其實不是阻塞）。這跟 `SetNowRoundInfo()` 現有做法（每次進場都重新從 `MainPlateSymbol` 算渲染盤面，不存渲染結果）是同一個模式，直接沿用即可。

## 狀態流

```
ScatterShowState
  └─ NextState(VS_FEATURE_SHOW)

VsFeatureShowState.OnEnter()
  1. vsResult = SpinAck.RoundQueue[CurPlateIndex].VSResult
  2. guard: !Game_Define.FEATURES.VS_FEATURE || !vsResult?.length
       → NextState(COLLECT_FEATURE_SHOW)；不做任何視覺變動（已存在的早退邏輯，須保留）
  3. input = AdaptVSResult(RoundInfo.MainPlateSymbol, vsResult, symbolIds)   ← 新增的薄 adapter，唯一新業務碼
  4. result = VSManager.Resolve(input)     ← 直接呼叫 M2.1 模組，不重寫規則
  5. for each step in result.steps（Cash 組 col 遞增 → Collect 組 col 遞增，M2.1 已保證順序）:
       a. Fly：該欄 Cash/JP 或 Collect 符號飛向 Vs(16) 位置（新元件）
       b. Expand：該欄 4 格覆蓋成 VsCash(17)/VsCollect(18)（新元件，仿 ColumnSymbol.SetSymbolInfos 落點）
       c. Spine：對決/倍率美術字（若資產未到位，走 AwardState.BigWin 那種 optional-component null guard，不 hard fail）
  6. GameView.VsFeatureResult = result   ← 新欄位，唯一交接管道，供步驟 7 讀
  7. NextState(COLLECT_FEATURE_SHOW)

CollectFeatureShowState.OnEnter()
  1. collectResult = SpinAck.RoundQueue[CurPlateIndex].CollectResult
  2. vsResult = GameView.VsFeatureResult   ← 讀步驟6的交接，不重算 S0-S4
  3. guard: 無 collectResult → NextState(AWARD)
  4. 依 [B28] Cash 先收、COLLECT/JP 後收，每個 Collect 用 vsResult.collectWins[col] ?? T 收分
  5. NextState(AWARD)
```

**Unshow/replay（現況，不建議在 M2.2 單獨解）**：`SpinState.OnEnter` 的 `HasUnshow` 分支只重灌 `SpinAck`，`UnshowPrepareState.ts:38-43` 那段真正要「回到上一局畫面、還原 `CurPlateIndex`」的邏輯整段是 TODO 註解，尚未實作——這是模板級缺口，VS Feature 只是繼承它，不是 VS 自己的問題。等這條路徑真正接上時，VS 這邊唯一要做的事就是：`SetNowRoundInfo(round)` 之後再呼叫一次 `VSManager.Resolve(round.MainPlateSymbol, round.VSResult)` 取得 `plateAfter`，用類似 `SetPlateSymbolForUnshow` 的無動畫寫入方式直接渲染定案盤面——不需要新的持久化欄位。

## 風險

1. **（高，框架級但 VS 首當其衝）Async 中斷無取消機制**：`BaseState`（`StateManager.ts:3-8`）沒有 `isActive`/取消 token，`VsF
…（此結果原長 5712 字，只帶前 3000 字）

Complete this task. When done, summarize what you accomplished.

---

**moa-ref-codex:**


═══ 📐 Phase 1：[moa-ref-codex] | 開始 ═══

收到任務：為 uk_slot_clash_of_olympus 的 M2.2 收斂最小實作設計。

根據前兩份審查結果，我需要讀取關鍵檔案來驗證現狀並收斂設計。


讓我讀取更多關鍵檔案來確認現狀，特別是 GameView mock 與 CollectFeatureShowState 的交接點。






讓我讀取 Game_Define 確認 symbol ID 並完成風險分析。












═══ 📐 Phase 2：[moa-ref-codex] | 收斂設計 ═══

根據讀取的檔案與前兩份審查結果，確認以下關鍵現狀：

**已驗證的事實**：
1. GameView.ts:907 的 mock 確實把 `Symbol.VsCollect(18)` 直接放進 col0，且 VSResult 結構缺少 `reelIndex`（只有 `appliedPositions`）
2. VSManager.Resolve() 是純函式，7/7 測試通過（M2.1 完成）
3. VsFeatureShowState 與 CollectFeatureShowState 都是 stub，沒有交接
4. Symbol ID：Collect=15, Vs=16, VsCash=17, VsCollect=18

═══ 📐 Phase 3：[moa-ref-codex] | 設計決策 ═══

## 設計決策

### D-1：Adapter 位置
**結論**：在 VSManager.ts 新增 `AdaptRoundToVSInput()` 純函式，不放 VsFeatureShowState。

**理由**：
- 保持 `ts-node --transpile-only` 可測性（不用 import cc）
- M2.1 文件已明確「只改 adapter，不改 Resolve() 規則核心」
- 前兩份審查都建議把轉換邏輯放回 VSManager.ts

### D-2：Mock 修正綁定
**結論**：修正 GameView.ts mock 與新增 adapter 必須一起交付，否則 adapter 測不通。

**理由**：
- 現有 mock 讓 Resolve() 恆回 `isTriggered: false`（col0 放 VsCollect 不是 VS，缺 reelIndex 無法過 IsValidReel）

### D-3：plateAfter 交接
**結論**：不持久化 plateAfter，而是在 CollectFeatureShowState.OnEnter() 重新呼叫 Resolve() 計算。

**理由**：
- Resolve() 是純函式，輸入（RoundInfo.MainPlateSymbol + VSResult）已存在
- 與 SetNowRoundInfo() 每次重算渲染盤面的模式一致
- 避免新增欄位

### D-4：Collect 收分係數交接
**結論**：在 GameView 新增 `VsFeatureResult` 欄位攜帶 `collectWins[col]`，CollectFeatureShowState 讀此欄位。

**理由**：
- CollectFeatureShowState 目前只讀 CollectResult，S5 算法需要的 collectWins 沒有來源
- 不在 Resolve() 時重算，避免兩份 S0-S4 邏輯漂移

### D-5：unshow/replay
**結論**：本切片只做正向流程，unshow/replay 依賴 UnshowPrepareState 的基礎還原（目前是 TODO）。

**理由**：
- 前兩份審查都指出模板級缺口，VS Feature 繼承而非獨自解決

═══ 📐 Phase 4：[moa-ref-codex] | BC/EH 清單 ═══

```
BC-M2.2-1：VsFeatureShowState 正確呼叫 AdaptRoundToVSInput + Resolve()
BC-M2.2-2：Mock 修正後，Resolve() 回傳 isTriggered=true 且 steps 非空
BC-M2.2-3：Cash 組（col 1~COL-2）先於 Collect 組（col 0 或 COL-1）播放
BC-M2.2-4：轉型後盤面 col 內四格皆為 VsCash(17) 或 VsCollect(18)
BC-M2.2-5：CollectFeatureShowState 讀取 GameView.VsFeatureResult.collectWins[col] 收分
BC-M2.2-6：GameView.VsFeatureResult 為 undefined 時，CollectFeatureShowState 回退到只讀 CollectResult（原行為）
BC-M2.2-7：多個 VS Collect（×10、×5）對同 T 的總額 = T×10 + T×5，非連乘

EH-M2.2-1：vsResult 為空或 VSFeature flag 關閉時，直接跳過 VsFeatureShowState（維持現有早退）
EH-M2.2-2：winningMultiplier 為 NaN/Infinity/0/負數時，該 VS 不產生步驟但不忘錄 warning
EH-M2.2-3：reelIndex 越界或 vsType 與欄位不符時，該 VS 安全略過
EH-M2.2-4：美術資產未到位時，Spine 演出走 optional-component null guard 降級（仿 AwardState.BigWin）
```

═══ 📐 Phase 5：[moa-ref-codex] | 檔案邊界 ═══

| 檔案 | 變更類型 | 範圍 |
|------|----------|------|
| `assets/Script/Feature/VSManager.ts` | 新增 | `AdaptRoundToVSInput()` 純函式 |
| `assets/Script/GameState/VsFeatureShowState.ts` | 修改 | `OnEnter()` 呼叫 adapter + Resolve()，逐 steps 播 Fly/Expand/Spine，寫回 plateAfter |
| `assets/Script/GameState/CollectFeatureShowState.ts` | 修改 | `OnEnter()` 新增讀 `GameView.VsFeatureResult.collectWins` |
| `assets/Script/GameView.ts` | 修正 bug | Line 907: `Symbol.VsCollect` → `Symbol.Collect`；VSResult 補 `reelIndex: 0` |
| `assets/Script/GameView.ts` | 新增 | `VsFeatureResult: VSResolveResult` 欄位 |
| `tests/VSManager.test.ts` | 擴充 | AdaptRoundToVSInput 單元測試 |

**不修改**：
- VSManager.Resolve() 核心邏輯（M2.1 已鎖定）
- UnshowPrepareState（模板級缺口，本切片不碰）

═══ 📐 Phase 6：[moa-ref-codex] | 分階段驗證 ═══

### Stage 1：Adapter 單元測試
```bash
cd G:\Cocos_Project\uk_slot_clash_of_olympus
npx ts-node --transpile-only tests/VSManager.test.ts
# 新增：AdaptRoundToVSInput 測試覆蓋 reelIndex fallback、vsType 映射
```

### Stage 2：Mock 修正驗證
```bash
# 在 Cocos Editor Preview 按熱鍵 8（vsfeature），檢查：
# 1. Console 輸出 "OnEnter State : VsFeatureShowState"（非直接跳過）
# 2. Console 輸出 Resolve result: isTriggered=true, steps.length>0
```

### Stage 3：整合測試
```bash
# 確認 Cash 組先播放、Collect 組後播放
# 確認盤面轉型後 col1~COL-2 為 VsCash(17)，col0/COL-1 為 VsCollect(18)
# 確認 CollectFeatureShowState 收到的收分額與 Resolve() 的 collectWins 一致
```

### Stage 4：邊界測試
```bash
# flag OFF：Game_Define.FEATURES.VS_FEATURE = false → 直接跳過
# vsResult=[] → 直接跳過
# invalid multiplier → warning 記錄但不播出
```

═══ 📐 Phase 7：[moa-ref-codex] | 風險摘要 ═══

| 等級 | 風險 | 緩解 |
|------|------|------|
| **高** | 現有 mock 讓 Resolve() 恆不觸發，adapter 單獨交付無意義 | 綁定修正與 adapter 一起交付 |
| **高** | VsFeatureShowState.PlayVsFeature() 的 await 鏈無取消機制 | 參照 await-gap-open-finalize-race 教訓，未來加 isActive guard |
| **中** | collectWins 交接欄位不存在 | 新增 GameView.VsFeatureResult |
| **中** | unshow/replay 依賴未實作的基礎還原 | 本切片只做正向流程，標註依賴 |
| **低** | GAP-04 美術資產未定（倍率語意、數量） | optional-component null guard 降級 |

═══ 📐 Phase 8：[moa-ref-codex] | 與 M2.1 契約 ═══

M2.2 不可違反以下 M2.1 既有契約：

- ✅ VSManager.Resolve() 內部邏輯不變
- ✅ Cash 組先於 Collect 組處理
- ✅ VS Collect 只作為收分係數，不改盤面分數
- ✅ 兩個 VS Collect 對同 T 是相加非連乘
- ✅ 類型/欄位不符時安全略過

═══ ✅ 設計收斂完成 ═══

```json
{"type":"artifact","summary":"M2.2 最小實作設計收斂完成：VSManager.ts 新增 AdaptRoundToVSInput 純函式，VsFeatureShowState 呼叫 adapter + Resolve 後依 steps 播 Fly/Expand/Spine，GameView 新增 VsFeatureResult 欄位交接 collectWins 給 CollectFeatureShowState。Mock 修正（col0 改 Symbol.Collect + 補 reelIndex）與 adapter 必須一起交付。plateAfter 不持久化，CollectFeatureShowState 重新呼叫 Resolve() 計算。unshow 依賴模板級缺口（UnshowPrepareState TODO），本切片不做。","outputs":[{"type":"finding","content":"GameView mock 有兩處 bug：col0 放 VsCollect 而非 Collect、VSResult 缺 reelIndex 欄位，需與 adapter 一併修正"},{"type":"finding","content":"plateAfter 不需要持久化，CollectFeatureShowState 直接用 MainPlateSymbol + VSResult 重算 Resolve() 即可"},{"type":"recommendation","content":"AdaptRoundToVSInput 放在 VSManager.ts 而非 VsFeatureShowState，維持 ts-node 可測性"},{"type":"recommendation","content":"GameView.VsFeatureResult 新增欄位承載 collectWins[col]，解決 CollectFeatureShowState 收分係數來源問題"},{"type":"code_change","content":"VSManager.ts 新增 AdaptRoundToVSInput() 純函式"},{"type":"code_change","content":"VsFeatureShowState.OnEnter() 呼叫 adapter + Resolve() + 逐 steps 播放 + 寫回 plateAfter"},{"type":"code_change","content":"CollectFeatureShowState.OnEnter() 新增讀 GameView.VsFeatureResult.collectWins"},{"type":"code_change","content":"GameView.ts 修正 mock：Symbol.VsCollect → Symbol.Collect，VSResult 補 reelIndex:0"},{"type":"code_change","content":"GameView.ts 新增 VsFeatureResult: VSResolveResult 欄位"}],"files_modified":["G:\\Cocos_Project\\uk_slot_clash_of_olympus\\assets\\Script\\Feature\\VSManager.ts","G:\\Cocos_Project\\uk_slot_clash_of_olympus\\assets\\Script\\GameState\\VsFeatureShowState.ts","G:\\Cocos_Project\\uk_slot_clash_of_olympus\\assets\\Script\\GameState\\CollectFeatureShowState.ts","G:\\Cocos_Project\\uk_slot_clash_of_olympus\\assets\\Script\\GameView.ts","G:\\Cocos_Project\\uk_slot_clash_of_olympus\\tests\\VSManager.test.ts"],"tags":["m2.2","vs-feature","design-converge","clash-of-olympus"]}
```


---

