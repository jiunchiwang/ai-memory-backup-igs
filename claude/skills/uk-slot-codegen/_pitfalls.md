# Pitfalls Checklist

按 Step 分段的踩坑紀錄。每條 ≤3 行。執行各 Step 時只讀對應段落。

---

## §0 Preflight / Clone

- **extensions clone 路徑**：`git clone <repo> "<target>/extensions"`（不是 `extensions/repoName/`）。Cocos 只認 extensions/ 直接子目錄。
- **gameSetting.json 的 folder**：clone 目標用 `folder` 欄位值，不要自己推測目錄名。
- **Step 0.0 跳過≠Step 0.1 跳過**：即使 template 已手動複製，extensions 仍需執行。

---

## §3.1 Game_Define

- **禁刪 export class**：`SymbolInfo`、`FgCellInfo`、`GAME_EVENT` 等被多處 import/new，刪掉 → "is not a constructor"。
- **SYMBOL_COUNT 禁止動態計算**：`Object.keys(Symbol).filter(...)` 被 Cocos bundler tree-shake 後 runtime=0。必須硬編碼數字。
- **SymbolWidth/Height 非固定值**：依盤面查表（5×6=128×100, 5×3=123×114, 6×4=96×82），改完同步 Mask。
- **Symbol.A / Symbol.Ten 硬編碼**：SlotReels.ts 有兩處引用具體 enum member，改 enum 後必須改為 index 或 SYMBOL_COUNT。

---

## §3.2 GameView / State Machine

- **新 state 需確認 .ts 有 export class**：template 部分 State 整檔被註解（如 CheckJpState），import undefined → crash。
- **template 基礎 state 禁刪**：WAIT_READY/PLATE_SHOW/FEATURE_SHOW/EFFECT_START/EXPLODE/MATCHING_PATCH_UP/SCATTER_SHOW/AWARD/ROUND_END 等 12 個不可移除。
- **三方一致**：enum GAMEVIEW_STATE ↔ SetStateMachine 註冊 ↔ NextState 引用，缺任一 → "State undefined Not Exist!!!"。
- **CommonState.* 是 framework 內建狀態，禁止替換或繞過**：`LOGIN`/`WAIT_RES`/`IDLE`/`SPIN_REQ`/`SPIN`/`COMMON_SHOW`/`CHECK_STATE`/`END`/`CHECK_FREESPIN` 等由 stateManager 內部處理，遊戲端只需註冊 `IDLE`/`SPIN`/`WAIT_RES`/`CHECK_STATE`（繼承 framework 抽象類），其餘不需註冊也不可替換成 Game_Define 的 state。`RoundShowEndState` 必須跳 `CommonState.COMMON_SHOW`，`ForEndToNext` 非 FG 路徑必須跳 `CommonState.END`——這些是 framework 自帶的中繼邏輯（處理 FG 續局、unshow 恢復等），繞過會導致 FG 被踢。
- **`USE_MOCK_SERVER` 不可 guard 框架通訊呼叫**：Mock 模式仍接真 server（借用別遊戲），`RetryRoundEnd`/`ReqRoundEnd`/heartbeat 全部正常走。只有 `OnCommand(AckType.spin)` 裡的 decode 結果可以用假資料覆蓋。

---

## §3.3 Proto

- **禁刪 `import Long from "long"` 和 `import protobuf from "protobufjs"`**：這兩行是 GameView.onLoad 裡 `protobuf.util.Long = Long; protobuf.configure()` 的依賴，刪掉 → runtime `protobuf is not defined`。Step 3.3 替換 proto import 時只改 `import protocol from "..."` 那行，不動 Long/protobuf。
- **不要用專案內的 compile-proto.js 自產**：該腳本產出的是精簡版（缺 decode/encode 實作），OnCommand 呼叫 `.decode(data)` 會 undefined crash。正確做法：複製 template 完整 proto 再 rename namespace。注意：被否決的只是此精簡腳本的輸出，`pbjs -t static-module -w commonjs` + `pbts` 產出的完整版含 decode/encode，接真 server 沒問題。
- **import 格式必須是 default import + 帶 .js**：`import protocol from "./Test/xxxProto.js"`。不能用 `import * as protocol from "./Test/xxxProto"`（Cocos 3.6.2 對 assets/ 內 CJS 用 namespace import 會報「找不到模塊」）。
- **d.ts 末尾必須有 `export default protocol;`**：格式 `declare const protocol: { <ns>: typeof <ns> }; export default protocol;`
- **CColumn 欄位名必須是 Col 不是 Symbol**：template SlotReels 讀 `.Col`，用錯名 → undefined → 空盤面。
- **替換所有 .ts 的 proto import**：遺留 `eyestrike` / `@igs-arcade-division` / `ar2esProto` 會 build 失敗。
- **rename namespace 用全文 replace**：js 和 d.ts 都要換，包括 `$root.xxxProto` 和 `namespace xxxProto`。
- **node_modules**：`npm install` 在 3.3.6 做（替換 package.json 後），不能提前。

---

## §3.4 Mock Server

- **Mock 模式的語意是「替換盤面資料」不是「沒有 server」**：仍接真 server（借用別遊戲的），GameInfo/RoundEnd/heartbeat 全部正常走。`USE_MOCK_SERVER` 只控制 `OnCommand(AckType.spin)` 裡用 `GenerateMockSpinAck()` 取代真實 decode 結果。真 server 好了只要改 `false` 就無痛切換。
- **Mock 只替換資料不改邏輯**：OnCommand 攔截 SpinAck，RoundEndState/CheckState/ForEndToNext 全不動。禁止在任何框架通訊（RetryRoundEnd/ReqRoundEnd/roundController）加 `USE_MOCK_SERVER` guard。
- **MainPlateSymbol 必須是 ICColumn[] 格式**：`{ Col: [{ Symbol, JPState, Number }] }`，不是純數字陣列。
- **FG 觸發三條件缺一不可**：`RoundQueue.length>1` AND `FreePlateSymbol.length>0` AND `NextFeverGameType>0`。
- **所有陣列欄位必須給空陣列**：`FreePlateSymbol[]`, `AwardDataVec[]`, `FeaturePosQueue[]` 等，undefined → `.length` crash。
- **IsGoingToFree = true 必須取消註解**：template 骨架是註解狀態。
- **CheckState FG 離場判斷必須啟用**：`CurPlateIndex >= RoundQueue.length - 1`。
- **FG 各輪 MainPlateSymbol 獨立產生**：不能共用同一 reference（否則所有輪都同盤面）。
- **Cocos input 系統**：Preview iframe 收不到 document keydown，必須用 `input.on(Input.EventType.KEY_DOWN)` + `KeyCode.DIGIT_X`。
- **InitMockKeyboard 必須在 start() 呼叫**：只定義不呼叫 → 熱鍵無反應。
- **Mock IRoundInfo 必須包含 RoundWin**：缺失時 AwardState 的 `rate = undefined/bet = NaN`，`rate > 0` 為 false → 整段報獎邏輯被跳過（BigWin 不觸發）。每個 mock mode 都要設 RoundWin。
- **NearWin mock 必須用 SCATTER_SYMBOL 的值**：NearWinDetector 偵測的是 Scatter 符號累計，放 CASH/WILD/Collect 等非 Scatter 符號無法觸發。從 `Game_Define.SCATTER_SYMBOL` 讀值填入。
- **SCATTER_SYMBOL 必須是單一 enum member（`Symbol.XXX`）**：所有 Game_Define 的 symbol 欄位（SCATTER_SYMBOL、WILD_SYMBOL 等）都必須用 enum member 賦值，不可用裸數字或 array。NearWinDetector 用 `===` 比對，array 會永遠 false、裸數字在 enum 重排後斷連。多種 Scatter 變體（如 4 色）只選一顆作為 NearWin 門檻代表，若需列所有 Scatter 另外定義 `SCATTER_SYMBOLS` array。
- **多 Scatter 遊戲的 NearWin 必須改用 `SCATTER_SYMBOLS.includes()`**：預設 NearWinDetector 用 `=== SCATTER_SYMBOL` 單顆比對，多 Scatter 時只會計到代表那顆，其餘全部漏算。正確做法：在 Game_Define 定義 `SCATTER_SYMBOLS: Symbol[] = [Symbol.SC_R, Symbol.SC_G, Symbol.SC_B, Symbol.SC_SUPER]`，NearWin 偵測邏輯改為 `SCATTER_SYMBOLS.includes(symbol)`。不改會導致 3/4 種 Scatter 的 NearWin 永遠不觸發。
- **規格書名稱帶 "Scatter" ≠ 程式的 SCATTER_SYMBOL**：規格書常把 Feature Symbol 命名為 Scatter_XXX（如 Scatter_Expand / Scatter_Bomb），但只有觸發 FG 和 NearWin 的那一顆才是 `SCATTER_SYMBOL`。其他帶 "Scatter" 前綴的是 Feature Symbol，在 enum 裡正常定義但不放進 `SCATTER_SYMBOL`。判斷依據：**是否參與 NearWin 累計 / 是否觸發 FG**，不是看名字。

---

## §3.5 Reel / SpinMode

- **dropEntry 呼叫順序**：`SetLayoutConfig → CreateSymbol → SetSpinMode → SetEntryStrategy`。亂序 → m_allColumns null。
- **漏 SetSpinMode → 不進 EXPLODE 循環**；**漏 SetEntryStrategy → SpinState 走轉輪滾動**。
- **m_reelPositionOffset 長度必須 ≥ COL**：否則 `UpdateReelXPositions` → undefined.x crash。
- **SHOW_COLUMNS**：dropEntry=1 / standard=3。MIDDLE_PLATE_INDEX 對應 0 / 1。
- **Mask contentSize 兩處都要改**：prefab 裡 Mask 節點 + 根節點各有一個 contentSize。
- **可變盤面需 per-column Mask**：單一矩形 Mask 無法遮不等高列。需 Mask_Left/Center/Right。
- **CompPrefabInfo.fileId 禁改**：可變盤面重寫 prefab 時保留原始值，否則 MainGame.prefab 的 TargetOverrideInfo 斷連。

---

## §3.7 Audio

- **FileName 大小寫必須一致**：AudioManager.AudioClips FileName = .m4a 檔名。
- **Windows rename 兩步**：同名不同大小寫需先改臨時名再改目標名。
- **FG_BGM 常被漏產**：template 帶了 45 個音效湊數但不含 FG_BGM，gate 要逐一比對不能只比數量。
- **AwardState 用 AudioManager.Play**：soundManager.Play 只接 AudioClip 物件，傳字串 → "Invalid audio clip"。
- **AudioClips 定義在 AudioManager 上，不在 Game_Define**：`Game_Define.AudioClips` 不存在（會 TypeError: undefined）。正確寫法：`AudioManager.Play( AudioManager.AudioClips.Win_Normal )`。

---

## §3.10 Feature Code

- **禁止跳過 Step 3.10**：不依賴 Cocos Editor，純 TS 操作。不可以「需要 Editor」「待後續」為由跳過。
- **FgDeclareManager / FgComplimentManager 禁止重寫**：template 已正確，分身忠實複製後不改。
- **ScatterShowState FG 路徑**：每個分支（FG/MG/MaxFlag）都必須有 NextState 出口。被註解 → 卡死。
- **ShowBigWin 不是公版 API**：正確用法是 `this.m_gameView.BigWin.Show(win, lvl)`（BigWinComponent.Show），不是 `this.m_gameView.ShowBigWin()`。GameView 沒有 ShowBigWin 方法，直接呼叫會 TypeError。lvl 用 `BigWinComponent.Level.BIG/MEGA/SUPER` 根據 rate 對照 PlateEftOdds 算。
- **BigWin getter 用 lazy init**：getComponent 在 start 時 node 未初始化可能回 null。
- **NearWin 按 SpinMode 分流**：Standard → SlotReels 逐列停輪；DropEntry → EffectStartState 消除結束。
- **NearWin PrefabPoolManager.RegisterPrefab**：動態生成（不同遊戲 COL 不同），不用 @property 靜態綁定。
- **DropEntry NearWin 光效不能同步 for loop**：ShowNearWin + StopNearWinAt 同幀 → m_spine.color null crash。
- **Scatter 動畫生命週期**：UpdateDropEntry 完成播 Stop → 停最後一幀留著 → 下一輪 SpinState.OnEnter 才清。
- **每個 Feature 必須有 MOCK_MODE + 熱鍵 + Mock 資料分支**。
- **Spine 播動畫前重置**：clearTrack(0) → setSkin → setToSetupPose() → PlayAnimation。

---

## §H Phase H

- **禁止重新產 Spine placeholder**：template 複製已帶完整 6 組（BigWin/FG_Declare/FG_Compliment/NearWin/Scatter/SymbolEffect），不要覆蓋。
- **禁止覆寫含 Spine 綁定的 prefab**：template 的 FG_Declare.prefab / FG_Compliment.prefab / BigWin.prefab 已預綁 SkeletonData + component，codegen 不可用 strReplace/write 改這些檔案。clone 下來就能用。
- **Spine placeholder 用 .json 格式**：Cocos 3.6.2 對 `.skel` 副檔名強制 binary parser（不做 JSON fallback），自產 binary 格式從未成功。正式美術交付後直接替換為 .skel 即可。
- **H1 不需要 Editor**：只做 prefab JSON strReplace + 複製檔案。禁止歸類為「需要 Editor」。
- **SymbolEffectPrefab 結構**：根節點同時掛 UITransform + sp.Skeleton + Component，無子節點。
- **NearWinEffectPrefab 單層**：root 掛 UITransform + sp.Skeleton + NearWinEffectComponent(hash:93417)，不能有子節點。
- **Spine placeholder .skel 格式**：正式美術都用 .skel，gen-spine-placeholder 已改 binary 輸出。
- **Symbol PNG 不覆蓋 template 原圖**：placeholder 缺 spriteFrame meta f9941 sub-asset。超過 21 個才新增。
- **GameView @property(sp.Skeleton) 綁定格式**：MCP 必須用 `{componentType:"sp.Skeleton", refNodeUuid}`。

---

## §4 Validation

- **Cocos 離線時 graceful skip**：report 標注 "validation skipped: editor offline"。
- **Spine SkeletonData 綁定需 Editor 在線**：.meta 含 uuid 是 Cocos 掃到才產生的。

---

## §通用 Encoding / 檔案操作

- **Template .ts 檔案是 UTF-8 with BOM（EF BB BF）**：任何 file write 操作必須保留 BOM，否則 Cocos Babel parser 報 `InvalidEscapeSequenceTemplate` 且不產 chunk → `__unresolved_X` runtime error。
- **strReplace / WriteAllText 會丟 BOM**：若需改已有 .ts 的 import，用 byte-level 操作（ReadAllBytes → UTF8.GetString → Replace → UTF8.GetBytes → WriteAllBytes）保留原始 encoding。
- **中文註解亂碼 = encoding 被改壞**：如果 grep 看到 `?�` 字元，該檔案已損壞，必須從 template 重新複製再改。
- **CJS .js 放在 assets/Script/ 是合法的**：Cocos 3.6.2 bundler 能正確處理 assets/ 內的 CJS `require("protobufjs/minimal")` + `module.exports`，不需要轉 ESM。前提是 node_modules 有對應套件。

---

## §通用 Template 註解取消

| 檔案 | 被註解邏輯 | 不取消的後果 |
|------|-----------|------------|
| AwardState.ts | BigWin/SmallWin 報獎分支 | 報獎不觸發 |
| GameView.OnRecvSpinAck | `IsGoingToFree = true` | FG 永遠不觸發 |
| CheckState.ts | FG 離場判斷 | FG 結束不了，無限循環 |
| SpinState.ts | Unshow/清理 scatter | Scatter 無限累積 |

原則：凡 Mock 資料需要驅動的流程分支，程式碼不能是註解狀態。
