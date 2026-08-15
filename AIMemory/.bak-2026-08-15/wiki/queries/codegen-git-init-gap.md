---
title: codegen clone 路徑從不建 repo 的流程缺口、補 Step 0.2 與 gate_git 三條斷言、UK slot 專案的 git 追蹤慣例（node_modules 進版控 / extensions 排除 / Tools_SlotSetUP gitlink 分布），以及兩輪異源覆核抓到的假因果敘述
type: query
created: 2026-08-12
updated: 2026-08-12
sources:
  - G:\AI\AI-canonical-corp commits 84ec055, 3813af7（已 push 20d89aa..3813af7）
  - G:\Cocos_Project\uk_slot_clash_of_olympus commit e030eda
  - skills/slot/uk-slot-codegen/_flow.md、_gates.md、_milestones.md、gate_runner.py、test_finalize_gate.py
---

# codegen 建 repo 缺口與兩輪異源覆核

2026-08-12 使用者發現 codegen 新建的老虎機專案沒有 git，要求先查流程。查證結論：
**不是誰漏跑，是 uk-slot-codegen 流程本身從來沒有這一步。**

## 1. 缺口的形狀

| 位置 | 原文 | 問題 |
|------|------|------|
| `_flow.md` Step 0.0 | `git clone --depth=1` 模板 → `Remove-Item .git -Recurse -Force`，理由寫「讓 target 可建新 repo」；驗證條件是「`.git` **不存在**」 | 刪了但沒人建回來 |
| `_flow.md` Step 0.1 | 只做 extensions 同步 | 完全沒碰主專案的 git |
| `_milestones.md` | 全 skill 唯一的 `git init`，寫在 **archive 路徑**清單第 1 項，標頭括號寫「clone 路徑由 Step 0.1 自動處理」 | **該括號對第 1 項是錯的**；0.1 只同步 extensions |

∴ 走預設 clone 路徑（codegen 的預設）產出的專案，**結構上必定不在版控**。
`uk_slot_clash_of_olympus` 是在 finalize gate **38/38 全綠**的情況下這樣交付的——
這正是 [[verification-diagnosis]] 的綠燈假象形狀：閘門沒有一條在問這件事。

誠實邊界：文件沒寫「刻意留給人工做」，也沒寫「應該自動做」，**無法判定是缺口還是刻意**。
兩種情況的修法相同（明文寫進流程），所以不卡在這個判定上。

## 2. 修法：Step 0.2 + 機械閘門

- `_flow.md` 新增 **Step 0.2: Git Init**，位置在 Extensions Sync 之後、Spec Ingestion 之前
  （extensions 已被 `.gitignore` 排除 ∴ 先後不影響 baseline commit 內容）；
  Pipeline 總覽 / Update Mode 差異表（update 跳過）/ validate 矩陣同步
- `_gates.md` §0 加驗證，並註明「Step 0.2 之後才跑」（它 exit 1，早跑必紅）
- `gate_runner.py` 新增 `gate_git` 掛進 `PRE_FINALIZE_GATES`
- `test_finalize_gate.py` 加 4 支測試，三條斷言各有專屬紅燈路徑（15/15 過）

`gate_git` 的三條斷言 —— 後兩條是覆核逼出來的：

| 斷言 | 擋住的狀態 |
|------|-----------|
| `git_repo_exists` | 專案完全不在版控 |
| `git_has_commit`（`rev-parse --verify HEAD`）| init 成功但首次 commit 失敗（新機器未設 `user.email` 時必然）→ 空 repo |
| `git_not_template_clone`（`remote -v` 含 `uk_slot_template`）| Step 0.0 的 `rm .git` 失敗 → 專案帶著模板 history，而 Step 0.2 又因「`.git` 已存在」被跳過 |

**只驗第一條會放過後兩種**，而它們的外觀與正常無異。這是「斷言比它自己的錯誤訊息窄」
的典型：訊息叫人「init + 首次 commit」，卻只驗了 init。

誤紅實測（六情境）：detached HEAD、uk_917、uk_872、clash、模板本身、
extensions-URL remote —— 無現實 false positive；git 不在 PATH 時大聲紅而非靜默綠。

## 3. UK slot 專案的 git 追蹤慣例（實查，非推測）

樣本：`uk_slot_template`、uk_917、uk_872、uk_722、uk_739、uk_746

- **`node_modules/` 要進版控** —— `.gitignore` 的 `#node_modules/` 是刻意註解掉的，
  三個 repo 各追蹤 282–310 個檔。看到它被 commit 不是意外
- **`extensions/` 排除** —— 它自己是獨立 repo，由 Step 0.1 管
- **`Tools_SlotSetUP`**：模板與 uk_917 是普通檔案（`100644`），
  uk_722 / uk_739 / uk_746 / uk_872 是 gitlink（`160000`）→ **gitlink 在專案側是多數**。
  根目錄 `.gitmodules` 指向 OLD-RD1，模板這側沒有對應 gitlink ∴ 不生效
- **remote 命名** `uk_<編號>_<name>_client`；目錄名可以不同
  （`uk_pirates_queen` 目錄 → `uk_815_pirates_queen_client` repo）

### ⛔ 本節初版把模板當基準，那是錯的（2026-08-12 使用者指出）

初版寫「對照模板逐項確認過，沒有缺漏」——但**模板不是出貨形態**：它自己 track 著
`.kiro/` 24 檔與 `uk-slot-state-machine.skill`，而每個出貨專案都會再補一批排除規則。
clash 的首次 commit 因此吃進 **119 個 AI 產物**（`.kiro/` 24、`docs/` 87 含 21MB
規格圖、`scratch/` 4、`AI.md`／`SPEC.md`／`ART_ASSET_MANIFEST.md`／`*.skill` 各 1）。

uk_917 的 `.gitignore` 比模板多出：`.kiro/` `kiro*/` `docs/` `scratch/` `/AI.md`
`/SPEC.md` `ART_ASSET_MANIFEST.md` `uk-slot-state-machine.skill`
`.codegen-checkpoint.json` `/.codegraph` `/assets/spineTest`。
uk_872 改用更寬的 `/*.md` ＋ 78 條 AI 工具目錄的逐檔 glob。

**`node_modules` 那條判斷是對的**（uk_917 自己也追蹤它），錯的只有「不要自行加碼」。

⚠️ **另一個陷阱：`.claudedocs` / `.claude-loop` / `.agents` 在既有專案是被
`.git/info/exclude` 擋的，不是 `.gitignore`**（`git check-ignore -v` 實查；uk_872
的 `.gitignore:134` 只有 `/.claudedocs/*.md` 逐檔 glob，子目錄 `.py` 仍靠
info/exclude）。`info/exclude` **不進版控、clone 不帶走** ∴ 那些 repo 的版控狀態裡
沒有這層保護——「照既有專案抄 `.gitignore`」抄不到它。

修法已進 skill 正本（`440e4f2`）：`_flow.md` Step 0.2 給出完整清單並標明
「先補 `.gitignore` 再 `add -A`」順序不可調換；`gate_runner.py` 的
`git_no_ai_artifacts` 讓「AI 產物被追蹤」變紅燈。

## 4. 五輪異源覆核抓到的 12 條

紀律來源：push 前派獨立覆核 + **findings 逐條自己重現才採納**。
五輪＝Fable 5 ×4 ＋ glm-5 ×1（第 3 輪 Fable 撞到 Anthropic session limit 中斷，
改派 glm-5 跨 vendor 接手；配額恢復後補跑 Fable 那輪，即第 4 輪）。

| 輪 | 等級 | 我寫的 | 反證 |
|----|------|--------|------|
| 1 | MED | gate 只驗 `.git` 存在 | 兩種失敗模式仍綠燈（見上表） |
| 1 | MED | 「uk_872 gitlink 屬個案」 | 擴大到 6 repo：4 個是 gitlink，**多數** |
| 1 | LOW×3 | M0a 表漏同步 / 「→ Step 3.1」假精確 / validate 禁跑 0.2 卻會紅 | 三條皆重現屬實 |
| 2 | MED | **「是模板後來改掉了」** | 模板全史 72 commit **0 筆 `160000`**、root 就是普通目錄；uk_872 root 還比模板晚 5 個月 |
| 3 | HIGH | 「clash 首次 commit 沒追蹤 AI artifacts」（glm-5 提出）| **否證**：時序錯位，它查的是 amend 後的版本 |
| 3 | LOW | 清單缺其他 AI 工具目錄 | 採納，補三項 |
| 4 | HIGH | **「皆已被各自 `.gitignore` 擋」** | 實際是 local-only 的 `.git/info/exclude`（見上節） |
| 4 | MED×2 | 「可查證 hash」`7d686c9` / flow 處方清單與 gate 強制清單不一致 | reflog 30 天會 gc 且不隨 push 傳播 → 改落檔；清單兩邊補齊 |
| 4 | LOW | `ls-files` 沒檢查 returncode | 會靜默綠燈（vacuous gate 形狀）|
| 5 | MED | **「後 3 項不在任何專案的 `.gitignore` 裡」** | 被 uk_872 的 **78 條**逐檔 glob 證偽（行 74–134）|

### 最值得記的一條：修正動作本身會產生新的假因果

同一個形狀在這件事上出現**三次**，每次都是「為了修上一條而新寫的句子」：

1. 修「uk_872 gitlink 屬個案」→ 編出「是模板後來改掉了」（全史 0 筆 gitlink，否證）
2. 修「照模板不要加碼」→ 寫出「皆已被各自 `.gitignore` 擋」（實際是 info/exclude）
3. 修上一條 → 寫出「不在**任何**專案的 `.gitignore` 裡」（uk_872 有 78 條）

共同機制：修正時數字擴大了、寫對了，卻順手補一個**沒有證據的機制解釋**或**把有例外
的觀察壓縮成全稱句**。這比原本的錯誤更難抓——數字都對、語氣自信、讀起來像考證過。

處置：
- 文件只留**觀察到的分布 + 操作規則**，成因明寫「未知，別替它補一個」
- 全稱句（「任何」「都」「皆」）出手前先找一個反例，找不到才寫
- 要寫因果就得先跑得出證據的查法：`git log --all --raw` 查全史是否出現過某 mode、
  `ls-tree <root>` 查初始狀態、`log --reverse` 比 root 日期、
  `check-ignore -v` 查**是誰**擋住的（而非只看「有沒有被擋」）

已存成 fact `correction-invents-new-causal-story`。相關：[[adversarial-review]]。

### 附帶方法論收穫

- **事故案例要附落檔的證據，不能只附 hash**：`7d686c9` 只從 local reflog 可達，
  `gc.reflogExpireUnreachable` 預設 30 天且不隨 push/clone 傳播 ∴ 對別人與 30 天後
  的自己都不可查。已把 119 行清單落檔進 skill 版控。
- **修好之後的事故案例會查不到**：跨 vendor 覆核者查現 HEAD 而非原始 commit，因此
  誤判「敘述與事實不符」給 NO-GO。這不是它的疏失，是敘述沒給對錨點。
- **測試不能拿被測物的常數當期望值**：逐項測試原本遍歷 `AI_ARTIFACT_PATHS` 本身，
  等於「清單移掉一項就跟著不測那項」，mutation 實測仍全綠。改硬寫獨立副本才殺得掉。
- **覆核者會回音送審者的數字**：我寫「19/19 過」沒給分母，覆核者量到 12（單檔）
  與 43（discover）都對不上並指出來。正確是 12 + 7 = 19（兩支測試檔合跑）。

## 5. 順帶回報但未動的既有問題

覆核者在範圍外發現，**非本次改動造成**：

1. Pre-A 先寫 `<target>/docs/spec`，之後 Step 0.0 才 `git clone` 進同一目錄 ——
   clone 進非空目錄會 fatal，且 0.0 的跳過條件「目標非空」會被 Pre-A 產物觸發
2. `_flow.md` 說讀 `gameSetting.json` 的 `extensions[0].git`，模板實際結構是 `Setting[0].git`

另外 `uk_slot_clash_of_olympus` 目前**未設 remote**（repo 名需要遊戲編號，未配號前不猜），
最終狀態：889 檔、`.gitignore` 已含全部 AI 產物排除規則（含三個 AI 工具目錄）。

## 相關

- [[uk-slot-codegen]] — codegen 工具整合與 milestone 定位
- [[uk-slot]] — 專案群總覽與專案文件規範
- [[adversarial-review]] — 異源對抗覆核紀律（本頁是它的一個完整案例）
- [[verification-diagnosis]] — 綠燈假象五型與突變測試
