# 狀態詳細說明參考

## 遊戲狀態流程概覽

```
LOGIN（框架起點）
  └→ WAIT_RES（等待資源）
       └→ WAIT_READY（初始化）
            └→ PLATE_SHOW（盤面顯示）
                 └→ FEATURE_SHOW（首次特色教學）
                      └→ IDLE（等待玩家操作）
                           └→ SPIN（轉輪中）
                                └→ WAIT_RES（等待伺服器）
                                     └→ CHECK_STATE（結果判斷路由）
                                          ├→ UNSHOW_PREPARE → IDLE（資料回補）
                                          ├→ EFFECT_START → SCATTER_SHOW → AWARD → ...
                                          │    ├→ ENTER_FREE → IDLE（進入免費）
                                          │    │    ├→ ADD_FREE → IDLE（追加次數）
                                          │    │    └→ FULL_REWARD → LEAVE_FREE → IDLE（結束免費）
                                          │    └→ ROUND_SHOW_END → ROUND_END → IDLE（一般結算）
                                          └→ [CHECK_JP] → ...（選用 JP 檢查）
```

---

## 框架通用狀態（CommonState）

### WaitResState — `CommonState.WAIT_RES`
| 屬性 | 內容 |
|------|------|
| 父類別 | 框架 `BaseState` |
| 觸發時機 | 每次需要等候伺服器回應時 |
| `OnEnter` | 送出 API 請求，開始等候旗標 |
| `OnProcess` | 輪詢回應旗標，到達後切換下一狀態 |
| `OnLeave` | 重置等候旗標 |
| 外部系統 | Socket / HTTP API |

### IdleState — `CommonState.IDLE`
| 屬性 | 內容 |
|------|------|
| 父類別 | 框架 `Common_IdleState` |
| 觸發時機 | 所有操作完成，等待玩家點擊 SPIN |
| `OnEnter` | 啟用 SPIN 按鈕、更新 UI 餘額顯示 |
| `OnProcess` | 監聽玩家輸入事件 |
| `OnLeave` | 停用 SPIN 按鈕 |
| 外部系統 | UI 系統（SpinBtn）、BetSystem |

### SpinState — `CommonState.SPIN`
| 屬性 | 內容 |
|------|------|
| 父類別 | 框架 `BaseState` |
| 觸發時機 | 玩家按下 SPIN 後 |
| `OnEnter` | 扣除賭注、啟動轉輪動畫 |
| `OnProcess` | 等待轉輪停止旗標 |
| `OnLeave` | 清除轉輪動畫狀態 |
| 外部系統 | ReelSystem、BetSystem |

### CheckState — `CommonState.CHECK_STATE`
| 屬性 | 內容 |
|------|------|
| 父類別 | 框架 `BaseState` |
| 觸發時機 | 伺服器回應處理完畢後 |
| `OnEnter` | 讀取本局結果資料 |
| `OnProcess` | **路由判斷**：依遊戲模式、中獎類型、Free 狀態決定下一狀態 |
| `OnLeave` | — |
| 路由邏輯 | 一般中獎 → `EFFECT_START`；無中獎 → `ROUND_SHOW_END`；資料缺失 → `UNSHOW_PREPARE` |

---

## 遊戲初始化狀態

### WaitReadyState — `WAIT_READY`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 登入後，遊戲元件尚未就緒 |
| `OnEnter` | 等待所有子系統完成初始化 |
| `OnProcess` | 輪詢就緒旗標 |
| `OnLeave` | 切換至 `PLATE_SHOW` |
| 外部系統 | GameView 各子系統 init 回呼 |

### PlateShowState — `PLATE_SHOW`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 遊戲初始化完成後 |
| `OnEnter` | 依螢幕方向（橫 / 豎）選擇 Intro 動畫；播放背景音樂 |
| `OnProcess` | 等待 Intro 動畫完成旗標 |
| `OnLeave` | 隱藏 Loading UI；顯示主 UI |
| 外部系統 | AnimSystem（IntroAnim）、AudioSystem、OrientationManager |
| TODO | 依遊戲需求替換 Intro 動畫素材 |

### FeatureShowState — `FEATURE_SHOW`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 首次進入遊戲，或遊戲有 Demo / 教學需求 |
| `OnEnter` | 判斷是否為首次；是 → 播放特色說明動畫 |
| `OnProcess` | 等待玩家關閉說明或動畫結束 |
| `OnLeave` | 標記「已看過說明」；切換至 `IDLE` |
| 外部系統 | PlayerDataSystem（firstTimeFlag）、UISystem（FeaturePanel）、BuyBonus 按鈕可見性 |
| 備註 | `BuyBonus` 按鈕使用可選鏈（`?.`）存取，避免未啟用時報錯 |

### UnshowPrepareState — `UNSHOW_PREPARE`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | `CHECK_STATE` 發現上局結果尚未呈現（伺服器資料超前） |
| `OnEnter` | 從伺服器快取讀取未展示結果資料 |
| `OnProcess` | 回補動畫 / 資料填入，完成後切回 `CHECK_STATE` |
| `OnLeave` | 清空回補暫存區 |
| 外部系統 | ServerCache、ReelSystem |

---

## 中獎表演狀態

### EffectStartState — `EFFECT_START`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 轉輪停止後、中獎時 |
| `OnEnter` | 依是否在免費遊戲中選擇動畫速度（免費加速） |
| `OnProcess` | 播放停輪特效；等待完成旗標 |
| `OnLeave` | 清除特效節點 |
| 外部系統 | AnimSystem（StopEffect）、FreeGameSystem（速度判斷） |

### ScatterShowState — `SCATTER_SHOW`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 中獎結果含 Scatter 符號 |
| `OnEnter` | 高亮 Scatter 格；播放 Scatter 音效 |
| `OnProcess` | 等待 Scatter 動畫結束 |
| `OnLeave` | 移除 Scatter 高亮 |
| 外部系統 | AnimSystem、AudioSystem、ReelSystem（格位資訊）|

### AwardState — `AWARD`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | Scatter 表演後，或直接由 `CHECK_STATE` 路由 |
| `OnEnter` | 啟動中獎線動畫循環；開始報獎計數 |
| `OnProcess` | **非同步**等待報獎完成旗標（`m_isAwardDone`）；玩家可提前跳過 |
| `OnLeave` | 停止線動畫；重置報獎旗標 |
| 外部系統 | LineSystem、ScoreSystem（計數動畫）、SkipSystem |

---

## 回合結算狀態

### RoundShowEndState — `ROUND_SHOW_END`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 所有中獎表演結束 |
| `OnEnter` | 廣播「本局表演結束」事件 |
| `OnProcess` | 等待子系統（如 UI）回應完畢 |
| `OnLeave` | 切換至 `ROUND_END` |
| 外部系統 | EventSystem |

### RoundEndState — `ROUND_END`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 本局結算完成 |
| `OnEnter` | 更新餘額、重置本局資料 |
| `OnProcess` | 確認結算完成後切回 `IDLE` |
| `OnLeave` | 清空本局暫存 |
| 外部系統 | BetSystem、UISystem（餘額顯示）|

---

## 免費遊戲狀態

### EnterFreeState — `ENTER_FREE`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | Scatter 達標，觸發免費遊戲 |
| `OnEnter` | 初始化免費遊戲計數；播放 Enter Free 動畫；切換背景 / 音樂 |
| `OnProcess` | 等待入場動畫完成 |
| `OnLeave` | 設置免費遊戲模式旗標；切換至 `IDLE`（免費局） |
| 外部系統 | FreeGameSystem、AnimSystem（EnterFreeAnim）、AudioSystem、BGSystem |
| 備註 | 同時初始化多個子系統（多系統協調入口） |

### AddFreeState — `ADD_FREE`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 免費遊戲中再次觸發 Scatter，追加次數 |
| `OnEnter` | 讀取追加次數；播放追加動畫 |
| `OnProcess` | 等待動畫完成 |
| `OnLeave` | 更新免費遊戲剩餘次數 UI；切回 `IDLE` |
| 外部系統 | FreeGameSystem、UISystem（FreeCountUI）、AnimSystem |

### FullRewardState — `FULL_REWARD`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 免費遊戲全數用完 |
| `OnEnter` | 播放全盤獎勵動畫（或留空供客製） |
| `OnProcess` | 等待動畫完成 |
| `OnLeave` | 切換至 `LEAVE_FREE` |
| 備註 | 目前為 **Placeholder**，依遊戲需求填入 Bonus 結算邏輯 |

### LeaveFreeState — `LEAVE_FREE`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | `FULL_REWARD` 結束後 |
| `OnEnter` | 播放 Leave Free 動畫；恢復一般遊戲 UI |
| `OnProcess` | 等待動畫完成 |
| `OnLeave` | 清除免費遊戲模式旗標；恢復背景 / 音樂；切回 `IDLE` |
| 外部系統 | FreeGameSystem、AnimSystem（LeaveFreeAnim）、AudioSystem、BGSystem |
| 備註 | 與 `EnterFreeState` 對稱，負責多系統清理 |

---

## 選用狀態（預設停用）

### CheckJpState — `CHECK_JP`
| 屬性 | 內容 |
|------|------|
| 父類別 | `BaseState` |
| 觸發時機 | 中獎結果需要檢查 Jackpot 池（停用時由框架跳過）|
| `OnEnter` | 傳送 JP 驗證請求 |
| `OnProcess` | 等待 JP 驗證回應；依結果切至 JP 中獎或一般 `AWARD` |
| `OnLeave` | 清除 JP 暫存 |
| 啟用方式 | 取消 `SetStateMachine()` 中的註解即可；**勿刪除該行** |

---

## 目錄中存在但**未**註冊的狀態

### CoinState（`assets/Script/GameState/CoinState.ts`）
- 存在於 `GameState/` 目錄，但 **未** 在 `SetStateMachine()` 中註冊
- 推測用途：硬幣掉落特效或 Coin-style 獎勵動畫
- 若需啟用：
  1. 在 `Game_Define.ts` 的 `GAMEVIEW_STATE` 加入 `COIN`
  2. 在 `GameView.ts` 加入 `import { CoinState } from "./GameState/CoinState"`
  3. 在 `SetStateMachine()` 加入 `states[ Game_Define.GameState.COIN ] = new CoinState( this );`

---

## 外部系統速查

| 系統 | 常見使用狀態 | 用途 |
|------|------------|------|
| `AnimSystem` | PlateShow、EffectStart、Scatter、EnterFree | 動畫播放與完成旗標 |
| `AudioSystem` | PlateShow、Scatter、EnterFree、LeaveFree | 音效與背景音樂切換 |
| `FreeGameSystem` | EnterFree、AddFree、FullReward、LeaveFree | 免費遊戲次數與模式管理 |
| `ReelSystem` | Spin、EffectStart | 轉輪動畫控制 |
| `LineSystem` | Award | 中獎線繪製與動畫 |
| `ScoreSystem` | Award | 報獎數值動畫 |
| `BetSystem` | Idle、Spin | 下注金額管理 |
| `UISystem` | Idle、RoundEnd、FeatureShow | 按鈕狀態、餘額、計數 UI |
| `BGSystem` | EnterFree、LeaveFree | 背景圖切換 |
| `EventSystem` | RoundShowEnd | 跨系統廣播事件 |
| `ServerCache` | UnshowPrepare | 未展示結果資料存取 |
