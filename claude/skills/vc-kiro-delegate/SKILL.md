---
name: vc-kiro-delegate
description: 將實作任務委派給 Kiro CLI（headless mode + claude-opus-4.6）執行，把主 agent 的 Claude Max 5x 配額（5 小時 message cap）保留給協調與決策，把實作丟給 Kiro 的不限量訂閱算力。Claude Code 負責預估、規劃、light review；Kiro 負責具體實作與第一輪 self-review。當用戶說「用 kiro 做」「交給 kiro」「省 token」「叫 kiro 寫」時務必使用此 skill；當主 agent 自己評估某個任務「預估會花 2k+ tokens」時也要主動委派 — 例如新增函式、寫測試、重構函式、實作模組。即使用戶沒明說「kiro」，只要預估產出規模 ≥2k tokens，就主動委派並在訊息中告知預估值。
---

# Kiro Delegate

把適合的工作委派給 `kiro-cli`（headless mode、Opus 4.6 模型），自己留下需要全局 context 的工作。

---

## 為什麼要這樣分工

用戶用 Claude Max 5x 訂閱（5 小時 message cap），同時有不限量的 Kiro 公司訂閱。**真正稀缺的是主 agent 的配額**，Kiro 對用戶來說是免費算力。最大化價值的方式：把所有能丟給 Kiro 的工作丟出去，主 agent 只留「不能外包的判斷」。

主 agent 留下三件不能完全外包的事：

1. **委派前的預估與規劃** — 任務是否該委派？怎麼切 spec？約束是什麼？
2. **委派後的 light review** — 看 Kiro 的 self-review 結論 + git diff，確認方向對
3. **跟用戶的對話** — 回報結果、收用戶 feedback、做最終決策

中間的「實作」+「self-review」+「跑測試」全部交給 Kiro。主 agent 不重做 Kiro 已經做過的事。

---

## 預估 + 階梯門檻（最重要的規則）

每次接到任務，動工前先做一次粗略的 token 預估：「**如果我自己做，會花多少 tokens？**」

### 預估參考表

| 任務類型 | 預估主 agent 消耗 |
|---|---|
| 改 1-2 行 / 改變數名 / 改 import | <500 |
| 修小 bug（1 個檔、根因已知） | 500-2k |
| 新增 1 個簡單函式（含 docstring） | 1k-3k |
| 新增 1 個複雜函式 | 3k-8k |
| 寫 1 檔單元測試（5-10 個 case） | 5k-15k |
| 重構 50-100 行函式 | 8k-20k |
| 實作新模組 / 整套小功能 | 20k-50k+ |
| 跨多檔套同 pattern（5+ 檔） | 20k-100k+ |

預估精度 ±50% 是合理的。寧可高估不要低估（高估了多委派一次成本小，低估漏委派浪費更多）。

### 階梯門檻

| 預估 token | 行動 | Review 模式 |
|---|---|---|
| **<2k** | **自己做**。typo、改變數名、單行修改、改 import — 連最精簡的委派 overhead 都不值 | n/a |
| **2k-25k** | **委派 Kiro** | **Light Review**（見下節） |
| **>25k** | **強制委派**。範圍太大可拆段委派（用 `--resume` 串接） | **Heavy Review**（見下節） |

**為什麼門檻是 2k**：簡化後的委派 overhead 約 5-8k tokens — 寫 spec prompt + 看 Kiro 結果 + 看 self-review + 做 light review。低於 2k 的任務（typo、單行）連這個 overhead 都比直接寫貴。但 ≥2k 就值得委派，因為主 agent 自己寫的話會超過 2k 而且**全部吃 Claude Max 配額**；委派的話 Kiro 那邊跑的 token 完全不算。

### 觸發優先順序

1. **用戶明確要求**（「用 kiro」「交給 kiro」「省 token」「省配額」） → 一定委派，不需要預估
2. **預估 ≥2k** → 主動委派，預估值寫進宣告
3. **預估 <2k** → 自己做，但如果用戶事後說「應該委派的」，下次調低門檻

### 不該委派的（不論預估多少）

- 需要看遍 codebase 才能決定怎麼改（架構研究先做完再說 — 未來會有 `vc-kiro-research` skill 處理這個）
- 需要跟用戶來回討論的決策
- 跨多個檔案的協同重構，且每個檔案的變更彼此互相依賴
- Bug 修復但根因尚未定位 — 先自己定位
- typo / 單行改變數名（即使用戶說「用 kiro」也要先確認 — 通常不值得）

### 不確定時

向用戶確認：「這個任務我預估要 ~Xk tokens。按你的偏好應該委派 Kiro / 自己做。要照建議嗎？」

---

## 執行流程（三段式）

### Step 1：宣告（含預估值）

**每次委派前，必須在用戶可見的訊息中明說：**

> 預估這個任務 ~**Xk** tokens（自己做的話），按你的偏好應委派。
> 請 kiro-cli 用 **claude-opus-4.6** 執行：[一句話描述任務]

**宣告之後，立即執行以下指令記錄委派意圖**（把 `{任務摘要}` 換成一句話描述）：

```bash
bash -c 'LOG="$HOME/.claude/logs/kiro-usage.log"; mkdir -p "$(dirname "$LOG")"; echo "$(date +"%Y-%m-%d %H:%M:%S") | $(basename $(pwd)) | intent: {任務摘要}" >> "$LOG"'
```

這條記錄比 Bash hook 早一步（hook 在 kiro-cli 實際執行後才觸發），包含任務語意。

兩條規則的目的：

1. **告知模型版本**（用戶要求） — 讓他能判斷模型是否需要更新。如果未來有更新的 Opus（例如 4.8），用戶會主動說「換新的」
2. **告知預估值**（用戶要求） — 讓他能驗證預估準不準，也能即時 override（「這個太簡單了你直接寫」「這個更大的拆段委派」）

**永遠不要省略這兩行宣告**。即使在「用戶明確要求委派」的場景，預估值也要報出來，因為用戶可能會根據預估值改變決定。

### Step 2：寫委派 prompt（必含五要素）

Kiro 看不到主 agent 的對話歷史。給它的 prompt 必須是「冷讀也能執行」的等級：

1. **任務目標** — 為什麼要做這件事（一句話）
2. **明確檔案路徑** — 用絕對路徑，不要說「這個檔案」「那個檔案」
3. **當前現況** — 必要時把相關 code 片段貼進 prompt（Kiro 可以自己 read，但提示它從哪看起省時間）
4. **預期輸出** — 要改成什麼樣 / 新增什麼檔案 / 函式簽名長什麼樣
5. **邊界條件** — 不要動什麼、要遵循什麼風格、要保持什麼不變（向後相容、API 不變、style 對齊既有檔案等）

**Prompt 範例：**

```
任務：在 /Users/me/proj/utils.py 新增 flatten_dict(d, sep='.') 函式，
把巢狀字典攤平成單層。

現況：utils.py 已有 deep_merge() 等工具函式，請參考其 docstring 與
type hint 風格（Google style）。

預期：
- 函式簽名：flatten_dict(d: dict, sep: str = '.') -> dict
- 範例：{"a": {"b": 1}} → {"a.b": 1}
- 處理 nested list（例如 {"a": [1, 2]}）時保持 value 為 list，不展開
- 加入 Google-style docstring 與 doctest
- 在檔尾新增（不要動其他函式）

邊界：
- 不要修改既有函式
- 不要新增 import（用內建即可）
- 不要寫單元測試（另一個任務）
```

### Step 3：第一次委派（新 session）

```bash
kiro-cli chat --no-interactive --trust-all-tools --model claude-opus-4.6 "<完整 prompt>"
```

注意事項：

- `--no-interactive`：避免任何 hang 在輸入提示
- `--trust-all-tools`：避免 hang 在權限詢問。如果任務敏感（例如不希望 Kiro 跑任意 bash），改用 `--trust-tools=fs_read,fs_write,execute_bash` 等明確列舉
- `--model claude-opus-4.6`：固定用最強的（用戶要求）
- prompt 用雙引號包起來，內部的雙引號要 escape 或改用 here-doc
- **Windows 注意**：PATH 上同時有 `kiro`（Amazon Kiro IDE，開 GUI 視窗，無 headless 支援）和 `kiro-cli`（headless CLI，這才是本 skill 要用的）。一律用 `kiro-cli`，不要用 `kiro`

**用 here-doc 寫長 prompt：**

```bash
PROMPT=$(cat <<'EOF'
任務：...
現況：...
預期：...
邊界：...
EOF
)
kiro-cli chat --no-interactive --trust-all-tools --model claude-opus-4.6 "$PROMPT"
```

執行完後 stdout 會顯示 Kiro 的回覆與工具使用。檔案修改已直接落地。

### Step 4：請 Kiro self-review（resume 同個 session）

Self-review 必須在同一個 session，否則 Kiro 不知道剛才改了什麼。用 `--resume` 接最近一次 session（不需要 parse session_id）：

```bash
kiro-cli chat --no-interactive --trust-all-tools --model claude-opus-4.6 --resume "<self-review prompt>"
```

**Self-review prompt 模板：**

```
請 review 你剛剛的修改：

1. 是否符合原始任務的每一項要求？逐項對照原始 prompt 的「預期」與「邊界」
2. 有沒有編譯錯誤、type 錯誤、明顯 bug？實際讀回檔案確認
3. 是否破壞了原有功能？檢查相關的既有測試或呼叫端
4. 程式碼風格是否與檔案其他部分一致？

如果發現問題，請直接修正。如果完全沒問題，第一行回覆 "PASS"，後面列出
你做了什麼修改的摘要。
```

**重要**：如果 working directory 同時有並行的多個 Kiro 任務在跑，`--resume` 可能接錯 session。並行委派時改用 `--resume-id <id>`，session_id 用 `kiro-cli chat --list-sessions` 找。**預設我們序列執行，用 `--resume` 即可。**

### Step 5：獨立 Kiro reviewer（新 session）

Self-review 有自我盲點 — Kiro 自己 review 自己剛寫的 code，傾向認可自己的邏輯。所以再開**一個獨立的 Kiro session**（不 resume），讓它在「不知道是它寫的」情況下審查同一份 diff。

```bash
# 先抓 git diff（如果不在 git repo，用 cat 修改後的檔案）
DIFF=$(cd <workdir> && git diff)

PROMPT=$(cat <<'EOF'
你是獨立的 code reviewer。下面是某 agent 剛剛完成的修改，請冷讀檢視：

# 原始 spec
[把 Step 2 寫的完整委派 prompt 貼進來，包含五要素]

# 實際修改（git diff）
[把 $DIFF 內容貼進來]

請評估：
1. diff 是否符合 spec 的每一項「預期」與「邊界」？
2. 有沒有明顯 bug、edge case 漏處理、或破壞既有功能的疑慮？
3. 程式碼風格是否與檔案其他部分一致？
4. 有沒有「看起來對但其實有問題」的地方？

請第一行回覆 PASS 或 NOT_PASS，後面列出你的具體觀察與理由。
**注意**：你不是寫的人，請用挑剔的角度看。如果有疑問，列出來。
EOF
)

kiro-cli chat --no-interactive --trust-all-tools --model claude-opus-4.6 "$PROMPT"
```

**重要**：

- **不要用 `--resume`** — 必須是新 session，這樣 Kiro 才不會帶著「我剛寫的」偏見
- **diff 太大時** — 如果 diff 超過 500 行，貼前後 200 行 + 用文字說明中段做了什麼；或是只貼關鍵改動段落
- **沒有 git** — 用 `diff <(cat original.bak) <(cat modified.py)` 之類的方式產 diff，或直接附上修改後的檔案內容

### Step 6：Claude Code 看兩輪 review 結論（依模式選 Light / Heavy）

主 agent 的工作不是重做 Kiro 已經做過的事，而是**判斷兩輪 review 結論是否吻合**：

#### 兩輪結論吻合 + 都 PASS → Light Review 收工

預設用於 2k-25k 區間任務。**不重 Read 整檔、不重跑驗證**。

1. `git status` 確認修改範圍沒超出預期（沒動到不該動的檔）
2. 確認 self-review（Step 4）回 PASS
3. 確認獨立 review（Step 5）回 PASS
4. 兩輪 review 對「做了什麼」的描述吻合（沒有一邊說「改了 X」另一邊說「沒改 X」這種矛盾）
5. **以上都 OK → 收工**，直接回報用戶

#### 兩輪結論不吻合 / 任一輪 NOT_PASS / 出現疑點 → 升級 Heavy Review

#### Heavy Review（用於 >25k、改公開 API、改 production 邏輯、兩輪 review 不一致）

1. **Read 兩輪 review 都提到的關鍵檔案 / 段落**（不需要 Read 全檔，聚焦在被點名的地方）
2. **對照原始 spec** 逐項檢查（特別是「邊界條件」是否被遵守）
3. **重跑驗證指令**：`pytest` / `npm test` / `tsc --noEmit` 等
4. **檢查副作用**：`git status` 看 Kiro 是否動了不該動的檔案

#### 不論哪種模式

任何不符之處 → **自己接手修，不再叫 Kiro**。重新 prompt Kiro 通常代表原 prompt 不夠清楚，再來一次反而更貴；同時把「prompt 哪一項沒講清楚」記下來，下次改進。

#### 觸發 Heavy Review 的情況

- 預估規模 >25k tokens
- 任務涉及公開 API、外部介面、認證/權限邏輯
- 修改 production 環境會跑到的程式（不是 test-only）
- Self-review 或獨立 review 任一輪 NOT_PASS
- 兩輪 review 結論不吻合（一個說對、另一個說錯）
- Kiro stdout 出現任何 warning / error 訊息
- 用戶明確要求「仔細 review」

---

## Session 串接的時機

| 場景 | 是否 resume |
|---|---|
| 委派任務 → self-review (Step 4) | **必須 resume** |
| Self-review → 獨立 reviewer (Step 5) | **不要 resume，必須開新 session**（避免帶著「我剛寫的」偏見） |
| 任務 A → 任務 B（不相關） | 不 resume，新 session |
| 「先實作 → 加 error handling → 加 logging」一條鏈 | 全部 resume 同一個 session |
| Claude Code 自己 review 後發現小問題，想叫 Kiro 修 | **不要再叫 Kiro，自己修**（見上方說明） |

---

## 失敗處理

| 情況 | 處理 |
|---|---|
| Kiro exit code 非 0 | 看 stderr。權限/設定問題 → 問用戶；任務本身錯誤 → 自己接手 |
| Kiro hang 住超過 5 分鐘 | 用 timeout 包裝指令（`timeout 300 kiro-cli ...`），超時後 kill 掉，自己接手 |
| Kiro 改錯方向 | 自己接手修。記錄「prompt 五要素哪一項沒講清楚」 |
| Kiro 說 PASS 但 Claude review 發現問題 | 自己接手修。不再 trust Kiro 的 self-review 結論 |
| Kiro 改了不該動的檔案 | 用 `git diff` 確認範圍，必要時用 `git checkout <file>` 還原非預期變更，再決定要不要重做 |
| 跑 test 失敗 | 自己接手修 |

---

## 不要做的事

- 不要省略宣告（兩行：預估值 + 模型版本）
- 不要省略 self-review（Kiro 那一輪）
- 不要省略 Claude review（主 agent 這一輪）
- 不要把 Kiro self-review 的「PASS」當作驗收依據
- 不要在 prompt 五要素不齊的狀態下委派 — 寧可花時間補齊
- 不要委派需要跨檔案探索的任務（先自己探索完，整理 spec 再委派）
- 不要在發現 Kiro 改錯後再叫 Kiro 修第二次 — 自己修
- 不要用 `--trust-tools=`（空值）— 那會讓 Kiro 連 fs_read 都不能用，除非你只是要它純文字回應
- 不要為了「練習用 kiro」而委派預估 <2k 的小任務 — 直接寫
- 不要在 Light Review 模式下還重 Read 整檔 / 重跑 pytest — 那等於白費 5-10k 配額。Light Review 的精神就是「信任 Kiro 的 self-review + 驗證 stdout，主 agent 只看 git diff」
