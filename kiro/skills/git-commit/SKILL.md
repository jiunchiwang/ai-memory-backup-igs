---
name: git-commit
description: 把 working tree 的變更整理成一個或多個語意清楚的 commit。先檢查暫存區並詢問處理方式（絕不自作主張 reset/commit），再依上次 commit 與本次編輯範圍判斷 commit 邊界、必要時拆多個 commit，最後產生跟隨 repo 現有風格的標題與結構化 body（含 BREAKING CHANGE 與未處理項目）。當使用者說「幫我 commit」「分 commit」「整理一下 commit」時使用。
type: skill
domain: general
created: 2026-08-06
tags: [git, commit, workflow]
source: skillhub（公司內網）· 已在地修正 emoji 硬規則與 Co-Authored-By 條款
---

# Git Commit — 根據編輯範圍自動分 commit

把當前 working tree 的變更整理成一個或多個語意清楚的 commit。標題短而精準；內容說明做了什麼、為何、有沒有破壞性變更、有沒有 TODO。**不是一次全 stage 一次全 commit**——根據上次 commit 與本次編輯範圍判斷邊界，必要時拆多個 commit。

## 0. 先檢查暫存區（最重要的一步）

在做任何規劃前，先跑：

```bash
git status --short
git diff --cached --stat
```

如果暫存區（index）已經有檔案被 `git add` 過：

1. **停下來**，把已 staged 的檔案列出來給使用者看。
2. 詢問使用者要怎麼處理，**不要自己做主**。給三個明確選項：
   - **A. 直接 commit 暫存區的內容**：把這批已 staged 的當成一個 commit，剩下未 staged 的另外規劃。
   - **B. 先 `git reset` 把 index 清空**，然後由你重新根據編輯範圍規劃所有 commit 的分組。
   - **C. 自己決定**：使用者可能想自己手動加減 staged 的檔案。

等使用者選擇後再繼續。**不要在使用者沒回應前自己 `git reset` 或 `git commit`。**

## 1. 收集脈絡

需要看的東西（用 Bash 平行跑）：

```bash
git status --short                      # 全部變更狀態
git diff --stat                          # 未 staged 的檔案統計
git diff --cached --stat                 # 已 staged 的檔案統計（如果上面步驟有保留）
git log -10 --oneline                    # 最近 10 個 commit 的標題風格
git log -1 --format='%B'                 # 上一個 commit 的完整內容（學風格 + 判斷邊界）
git diff HEAD                            # 整體 diff 內容（如果很大，分段或挑檔案看）
```

**重點觀察**：

- **上一個 commit 涵蓋了什麼？** 本次的變更如果是同一個邏輯範圍的延續，可能可以併進去（但通常不 amend，建立新 commit）；如果是不同主題，務必另開 commit。
- **這次的變更橫跨幾個主題？** 一次 commit = 一個邏輯變更。範例：
  - 同時改了「fix login bug」+「rename a util」→ 拆兩個 commit。
  - 「add new endpoint」+「補它的 test」→ 一個 commit。
  - 「format 全專案」+「修 bug」→ 拆兩個（formatting 噪音會淹沒真正的修改）。
- **檔案類型混雜**：lockfile / generated / vendor 變更要不要跟邏輯改動分開？通常分開，commit message 寫 `chore: update lockfile`。
- **看 git log 的標題風格**：是 conventional commits（`feat:`、`fix:`）還是自由格式？有沒有 emoji？語言是中文還英文？**跟著現有風格走**。

## 2. 規劃 commit 邊界

根據上面的觀察，列出計畫：

```
Commit 1: <標題> — 包含檔案 A, B, C
Commit 2: <標題> — 包含檔案 D
Commit 3: <標題> — 包含檔案 E, F
```

把計畫告訴使用者，請他確認或調整。**不要直接開始 commit。**

如果只有一個邏輯主題，就一個 commit；不要硬拆。

## 3. 寫 commit message

### 標題

- **風格一律跟隨 repo 現有慣例**（從 `git log -10 --oneline` 判讀）。這是硬規則，優先於下面任何預設。
  - repo 用 conventional commits 無 emoji（如 `feat: xxx`）→ **不要**自己加 emoji。
  - repo 既有 commit 帶 emoji → 跟著加，位置與用法照現有慣例。
  - repo 無明確風格（歷史混亂或全新 repo）→ 才用下面的預設：conventional 前綴 + emoji。
- **簡潔清楚**：英文 50 字內，中文 25 字內。動詞開頭。
- 語言跟隨 repo 現有 commit 的語言。

**無既有風格時**的預設 emoji 對照表：

| emoji | 用途 |
|---|---|
| ✨ | 新功能 (feat) |
| 🐛 | 修 bug (fix) |
| ♻️ | 重構 (refactor) |
| 🎨 | 程式碼風格 / format |
| ⚡ | 效能優化 (perf) |
| 📝 | 文件 (docs) |
| ✅ | 測試 (test) |
| 🔧 | 設定 / 工具鏈 (chore / config) |
| 🚀 | 部署 / release |
| 🔥 | 移除程式碼 |
| 🚧 | WIP（盡量不要用，除非使用者明確要） |
| 💥 | 破壞性變更（breaking change） |
| 🔒 | 安全性修正 |
| 📦 | 相依性 / 套件變更 |
| ⬆️ ⬇️ | 升級 / 降級套件 |

### 內容（body）

只在「值得寫」時才寫——一行小修正不用 body。需要 body 時用這個結構：

```
<標題>

<一段話說明：為什麼做這個變更？要解決什麼問題？>

變更內容：
- 具體做了什麼 A
- 具體做了什麼 B

破壞性變更：（如有）
- 改了 XX API 的簽名，呼叫端要改成 ...

未處理 / TODO：（如有）
- 還沒補 unit test
- Y 邊界情況待後續處理
```

**規則**：

- 「破壞性變更」這段如果有，必須加上 `BREAKING CHANGE:` 標記（conventional commits 慣例），讓 changelog 工具抓得到。
- 「未處理」要誠實寫——別假裝什麼都做完了。
- 不要寫廢話（「修改了一些檔案」、「優化了程式碼」）。
- 不要把 diff 抄一遍到 body。
- **這是最低標，不是上限**：如果某個決策有「為何選 A 不選 B」的理由、有隱性風險（時序 / 快取失效 / 語意漂移）、或有非顯而易見的因果，寫進 body。未來的你會需要它。

### trailer

跟隨 repo 現有慣例與所在 CLI harness 的指示。若 repo 既有 commit 帶 `Co-Authored-By:` 且本次為 AI 協作產出，**沿用**，不要靜默停掉——那會斷掉 AI 協作的可追溯性。

## 4. 執行 commit（每個 commit 依序做）

對每個規劃好的 commit：

```bash
# 1. 把該 commit 要包含的檔案加進 index
git add <files-for-this-commit>

# 2. 確認 index 內容正確
git diff --cached --stat

# 3. 用 heredoc 寫 commit message（避免引號跳脫問題）
git commit -m "$(cat <<'EOF'
<標題>

<body 如果需要>
EOF
)"
```

> ⚠️ Windows PowerShell 沒有 heredoc。改用單引號 here-string 傳給 git：
> ```powershell
> git commit -m @'
> <標題>
>
> <body>
> '@
> ```
> 結尾的 `'@` 必須頂格在自己一行（縮排會 parse error）。

**不要**：
- 不要用 `git add -A` 或 `git add .`，除非已經確認所有變更都屬於這個 commit。
- 不要 `--amend` 之前的 commit，除非使用者明確說要 amend。
- 不要 `--no-verify`，pre-commit hook 失敗就停下來看是什麼問題。
- 不要在使用者沒明確指示的情況下 `git push`。

## 5. 收尾回報

全部 commit 完後：

```bash
git log -5 --oneline       # 給使用者看做了哪些 commit
git status                  # 確認 working tree 乾淨（或剩下沒處理的）
```

一兩句話總結：做了幾個 commit、分別是什麼主題、有沒有東西還沒 commit（為什麼）。

## 常見情境

- **只有一個小改動**：跳過步驟 2 的規劃，直接 commit 就好，但暫存區檢查還是要做。
- **使用者已經 `git add` 過很多東西**：步驟 0 要先問，不要自己 reset。
- **發現一堆無關的 noise（log、commented code、IDE 設定）**：在步驟 1 提出來問使用者要不要一起 commit、要不要丟掉、還是要另外處理——不要自作主張。
- **pre-commit hook 改動了檔案**（lint auto-fix）：commit 失敗後，把 hook 改的檔案一起加進去再 commit，**建新 commit，不要 amend**。
- **使用者說「整理一下分 commit」但其實還沒做完**：可以建議先把當前進度存成 WIP commit 或 stash，等做完再回來分。
- **目前在 main/master 上**：若專案規範要求 feature branch，先提醒使用者，由他決定要不要開分支再 commit。

## 範例

### 範例 1：拆兩個 commit（repo 風格為 conventional + 無 emoji）

使用者改了 `auth.go`（修登入 bug）+ `README.md`（補 setup 說明）。應該：

```
Commit 1:
fix: 修正 session token 過期未刷新導致登入失敗

當 token 接近過期時，refresh 邏輯沒被觸發，使用者會被踢回登入頁。
改為在每次 request 前檢查剩餘時間 < 5 分鐘就主動刷新。

變更內容：
- 在 middleware 加上 token 剩餘時間檢查
- 加上 refresh 失敗的 fallback

未處理：
- 還沒補對應的 integration test

Commit 2:
docs: 補上本地開發環境的 setup 步驟
```

### 範例 2：一個 commit 就夠

新增一個 endpoint + 它的 handler + test，全部相關：

```
feat: 新增 GET /users/:id/preferences endpoint

提供使用者偏好設定查詢，供前端個人化頁面使用。

變更內容：
- 新增 handler 與 service 層
- 補上 unit test 與 integration test
- 更新 OpenAPI spec
```
