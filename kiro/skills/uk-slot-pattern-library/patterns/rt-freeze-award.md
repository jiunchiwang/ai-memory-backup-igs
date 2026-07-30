# Pattern: RT 凍幀報獎（RenderTexture 蓋幀）

## 識別條件

- 規格要求報獎/進退 FG 期間顯示「整個遊戲畫面」當背景，但該畫面不需要繼續動
- 效能需求：報獎演出期間要降低 DrawCall / spine 更新量（轉輪、角色、背景 spine 全部可以停）
- 症狀導向：報獎面板一跳出來就掉幀，profiler 顯示底層節點仍在渲染
- 不是「存檔截圖」——沒有 `readPixels`、不寫檔、玩家拿不到圖片

> ⚠️ 命名陷阱：程式裡的 `@property tooltip` 寫「要截圖的節點」，實際語意是「**被貼圖蓋掉後要關掉的節點**」。搜 `screenshot` 找不到這個功能，要搜 `RenderTexture` / `RTCtrl`。

## 參考實作

| 專案 | 核心檔案 | 說明 |
|------|----------|------|
| uk_pirates_queen | `assets/Script/RTCtrl.ts` (218 行) | **進化版，新專案抄這份**。含資源釋放、防閃三步、主相機快取 |
| uk_pirates_queen | `assets/game/Prefab/PerfGroup.prefab` | RT 容器 prefab（掛在 `Node_Reel.prefab` 內） |
| uk_746_far_west_client | `assets/Script/RTCtrl.ts` (176 行) | 初版，同源但有 6 個已知缺陷（3 真 bug + 3 品質改進，見「兩版差異」） |

其餘 UK slot 專案（eyestrike2 / 917 / 722 / 739 / eye_strike / template / LGS / chachacha / clash demo）皆無 `RenderTexture` 使用。

### 節點結構

```
PerfGroup            ← m_RTRoot（平時 active = false）
├─ Node              ← sprite（cc.Sprite，貼 RT 的載體）
└─ Camera_RT         ← camera（第二台相機，targetTexture 指向 RT）
```

`RTCtrl` component 掛在 `Manager.prefab` 的 `Manager` 節點，四個欄位是在 `MainGame.prefab` 用
**`cc.TargetOverrideInfo`（targetOverrides）** 跨 prefab instance 接起來的，不是 propertyOverrides。

> 🔍 查接線時的陷阱：直接讀 `Manager.prefab` 會看到 `sprite`/`camera`/`m_RTRoot` 全是 `null`，
> 讀 `MainGame.prefab` 的 `propertyOverrides` 也只找到 `m_gameView` 跟一個 `m_hideNodes[0]`。
> **真正的引用在 `targetOverrides`**（pirates_queen 是 `MainGame.prefab` 的 idx 2889/2892/3018/3021/3024）。
> 別因為看到 null 就判定功能沒接好。
>
> 這也是 `uk-slot-codegen/_pitfalls.md`「CompPrefabInfo.fileId 禁改」的下游後果——
> codegen 重寫 prefab 若動了 fileId，這五條 targetOverride 會全部斷連，RT 就變成執行期 crash。

## State 映射

不新增 state。由各 State 自己 dispatch 事件，`RTCtrl` 單點收斂：

```
GameView.Init()                    → RT_EVENT.INIT
GameView.OnRotation()（未鎖旋轉時）  → RT_EVENT.INIT（重建 RT）

AwardState / AddFreeState / EnterFreeState / LeaveFreeState → AWARD_IN_RT
… 對應 State 結束 / SpinState                                → AWARD_OUT_RT
```

pirates_queen 的實際 dispatch 點：

| 位置 | 事件 |
|------|------|
| `GameView.ts:843` | `INIT`（初始化） |
| `GameView.ts:885` | `INIT`（`OnRotation` 內，`m_isLockRotation` 為 false 才發） |
| `AwardState.ts:107` / `:61` | IN / OUT |
| `AddFreeState.ts:54` / `:136` | IN / OUT |
| `EnterFreeState.ts:33` | IN（OUT 由 `SpinState.ts:45` 負責） |
| `LeaveFreeState.ts:157` / `:170` | IN / OUT |
| `DebugToolManager.ts:170-176` | 鍵盤 `R` 進、`F` 出（手測用） |

> ⚠️ **IN / OUT 不必成對出現在同一個 State**：`EnterFreeState` 只發 IN，OUT 交給 `SpinState`。
> 這是刻意的（FG 第一手才解除凍幀），但也代表新增 State 時很容易漏掉 OUT 而卡在凍幀畫面。

## Data 需求

**無 proto 需求**。純 client 表演/效能層，server 不參與。唯一的跨模組狀態是
`GameView.IsLockRotation`（`GameView.ts:310-315`，setter 是純 passthrough 無副作用）。

**這個旗標有 5 個寫入點、4 個持有者**（pirates_queen 實測）——沒有任何互斥機制：

| 寫入點 | 值 | 備註 |
|--------|----|------|
| `RTCtrl.ts:177` / `:210` | true / false | RT 凍幀期間 |
| `ExplodeState.ts:45` / `:48` | true / false | 消除演出期間 |
| `GameView.ts:2314`（`BigHintShake`） | true | **直接寫私有欄位 `m_isLockRotation`，繞過 setter** |
| `GameView.ts:2327`（同上的 tween `.call()`） | false | **無條件**清除，不檢查是否有別人在鎖 |
| `GameView.ts:2341`（`RemoveBigHintShake`） | false | **無條件**清除 |
| `Common.ts:273`（`Common.SetLockOrientation()`） | 任意 | public static 對外入口，任何人都能改 |

> 🔍 **grep 陷阱**：搜 `IsLockRotation =` 只會找到 4 筆，**漏掉 `GameView.ts:2314`**——那行寫的是私有欄位
> `m_isLockRotation = true`。要枚舉完整必須搜 `[Ii]sLockRotation`（含 `m_` 前綴）。

## 演出時序

`AwardInRT()` — **順序就是防閃的全部**：

| Step | 動作 | 等待方式 | 為什麼是這個順序 |
|------|------|----------|-----------------|
| 1 | `m_isInAward = true`；`IsLockRotation = true` | immediate | 凍住旋轉，避免演出中 resize 觸發 re-init |
| 2 | `m_RTRoot.active = true`，但 `sprite.node.active = false` | immediate | 讓容器先過一幀初始化，貼圖還不要顯示 |
| 3 | 補設 sprite / camera 的 `y = -gameView.node.position.y` | immediate | 以防 Init 時位置還沒同步 |
| 4 | `camera.node.active = true` | `await Define.Wait(this, 0.01)` | 讓 RT 至少渲染一幀，否則貼圖是空白 |
| 5 | `camera.node.active = false` | immediate | **先關相機凍住 RT 內容**，之後畫面不再更新 |
| 6 | `sprite.node.active = true` | immediate | 貼圖現在才蓋上畫面 |
| 7 | `m_hideNodes.forEach(n => n.active = false)` | immediate | **最後**才關實體節點——已被貼圖蓋住，不會閃 |

`AwardOutRT()` — 反向還原：

| Step | 動作 |
|------|------|
| 1 | `m_isInAward = false`；`IsLockRotation = false` |
| 2 | `m_hideNodes` 全部 `active = true` |
| 3 | `m_RTRoot.active = false` |
| 4 | `camera.node.active = true`（還原成待命狀態） |

`Init()`（`RTCtrl.ts:113`）—— 建 RT 並對齊主相機：

1. `new SpriteFrame()` + `new RenderTexture()`，`reset({ width/height: view.getVisibleSize() })`
2. 從 `director.getScene().getComponentsInChildren(Camera)` 找 `node.name === 'Camera'` 的主相機，
   把 `orthoHeight` 抄到 RT 相機（**不抄會縮放不對**）
3. sprite 的 `UITransform.width/height` 設成可見區大小
4. sprite 與 camera 的 `y` 都設 `-gameView.node.position.y`（抵銷 GameView 位移）
5. `camera.targetTexture = renderTex` → `spriteFrame.texture = renderTex` → `sprite.spriteFrame = sp`
6. **釋放上一輪自建的 SpriteFrame 與 RenderTexture**

## 常見變體

| 變體 | 做法 | 代表 |
|------|------|------|
| `RT_EVENT` enum 放自己檔案 | `export enum RT_EVENT` 在 `RTCtrl.ts` 內 | pirates_queen |
| `RT_EVENT` enum 放共用定義 | 從 `Game_Define.ts` import | far_west |
| 防閃三步（sprite 先關後開） | Step 2 / 6 分離 | pirates_queen |
| 無防閃（RTRoot 一次開） | `m_RTRoot.active = true` 後直接關 hideNodes | far_west |
| 報獎中允許轉螢幕 | `onCanvasResize` 加 `IsLockRotation` 早退守衛 | pirates_queen |
| 報獎中轉螢幕強制退 RT | resize 時 `Init()` + `AwardOutRT()`，直接踢出凍幀 | far_west |

### 兩版差異（要抄哪一份）

| 面向 | far_west（初版） | pirates_queen（進化版） |
|------|-----------------|------------------------|
| `onDestroy` 生命週期 | ❌ 寫成 `OnDestroy()` 大駝峰 → **引擎不會呼叫，事件從未 unregister** | ✅ `onDestroy()` |
| `view.off('canvas-resize')` | ❌ 完全沒解除監聽 | ✅ 有 |
| RT / SpriteFrame 釋放 | ❌ 每次 `Init()` 都 new，舊的不 destroy → resize 反覆觸發就洩漏 | ✅ `Init()` 尾端與 `onDestroy` 都釋放 |
| 只釋放自建資產 | — | ✅ `_createdSpriteFrame` 區分自建 vs prefab 指定的資產 |
| 主相機查找 | ❌ 每次 `Init()` 全場 `getComponentsInChildren` | ✅ `_cachedMainCamera` 快取 |
| resize 守衛 | ❌ 無，報獎中轉螢幕會被踢出凍幀 | ✅ `IsLockRotation` 早退 |
| 防閃順序 | ❌ 無 sprite 先關後開 | ✅ 有 |

> 📌 **結論：新專案一律抄 pirates_queen 版。** far_west 那份是同一份碼的較早狀態，
> 六個缺陷都在 pirates_queen 修掉了（git: `6d612cb 修正RT顯示問題`、`4a7bccb RT處理優化`、`9573b13 GC和效能優化`）。

## 邊界案例

1. **`m_hideNodes` 漏填**：漏掉的節點會繼續渲染、繼續動，但被貼圖蓋住看不見——**沒有任何錯誤訊息**，只有 profiler 看得出來省不到效能
2. **轉螢幕在報獎中**：pirates_queen 靠 `IsLockRotation` 抑制，但那是**共用旗標、5 個寫入點、無互斥**（見「Data 需求」表）。最具體的災害路徑：RT 凍幀開始前若有 `BigHintShake` 在跑，它的 tween `.call()`（`GameView.ts:2327`）會在震動結束時**無條件**把鎖清掉 → 此時轉螢幕就進 `onCanvasResize`、跑 `Init()` + `AwardOutRT()`，玩家被踢出凍幀。`RemoveBigHintShake()`（`:2341`）同樣無條件清除
3. **resize 延一幀**：`scheduleOnce(..., 0.01)` 是等 Widget 重算完，直接同幀 `Init()` 會拿到舊的 `getVisibleSize()`
4. **RT 尺寸跟著可見區**：直橫版切換要重建 RT，不是只改 sprite 尺寸（貼圖會被拉伸）
5. **`orthoHeight` 未同步**：RT 相機沿用預設值 → 凍幀畫面縮放與實際畫面不一致，通常表現為「報獎背景比原畫面大一圈」
6. **新增 State 只發 IN 沒發 OUT**：畫面永久卡在凍幀（可操作但完全不動），且因為 `IsLockRotation` 還是 true，連轉螢幕都沒反應
7. **`Define.Wait(this, 0.01)` 太短**：低階機一幀可能不夠，RT 會有機率是空白/半渲染；這個值沒有實測依據，遇到白畫面先調大它
8. **`m_hideNodes` 內含 prefab instance 根節點**：pirates_queen 的 `m_hideNodes[0]` 是 `Node_Reel` prefab instance，關掉整包沒問題；但若填的是 instance 內部節點，接線會走 `targetOverrides` 的兩段 localID，codegen 重寫更容易斷

## 常見錯誤

1. **❌ 用 PascalCase 寫引擎生命週期回呼**：UK slot 專案的命名規範是方法大駝峰，但 `onLoad` / `start` / `onDestroy` / `update` 是 **Cocos 引擎的回呼名，必須小寫**。far_west 的 `OnDestroy()` 就是這樣變成死碼的 → 命名規範不套用在引擎回呼上
2. **❌ 關實體節點在貼圖顯示之前**：會閃一幀空白 → 必須「camera 關 → sprite 開 → 才關 hideNodes」
3. **❌ 每次 `Init()` 都 new RT 卻不 destroy 舊的**：`canvas-resize` 會反覆觸發（拖視窗、轉螢幕），累積洩漏 → `Init()` 尾端必須釋放上一輪
4. **❌ destroy 了 prefab 上指定的 SpriteFrame**：只能 destroy 自己 `new` 出來的 → pirates_queen 用 `_createdSpriteFrame` 明確區分
5. **❌ 以為搜 `screenshot` 就能找到這個功能**：關鍵字是 `RenderTexture` / `RTCtrl` / `RT_EVENT`
6. **❌ 看到 prefab 欄位是 null 就判定沒接線**：真正的引用在 `targetOverrides`，不在 `propertyOverrides`
7. **❌ 忘記 RT 相機要抄主相機的 `orthoHeight`**：畫面比例會不對，但不會報錯
