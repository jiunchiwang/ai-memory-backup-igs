---
name: sync-fork-from-upstream
description: 當使用者要把自己的 fork / 下游倉庫同步到原專案（upstream）的最新更新時使用。觸發語包含「同步原專案」「拿上游更新」「sync upstream」「更新原專案」「原本的倉庫有更新怎麼拉」。涵蓋一次性 upstream remote 設定、半自動同步流程（fetch → 拋棄式分支試合併 → 型別檢查 → 停在衝突/失敗 → push 前獨立覆核閘 → 絕不自動 push）、以及 fork 與 upstream 無共同歷史時的「重新接血脈」做法。
---

# 同步 fork ← upstream（半自動、停在衝突）

把下游倉庫（你的 fork，`origin`）同步到原專案（`upstream`）的更新。核心原則:**所有合併在拋棄式分支上做、型別檢查當品質閘、遇到需要判斷的衝突就停下來問人、push 永遠是人為確認的最後一步。**

## 何時使用

- 使用者說「同步原專案」「拿上游更新」「sync upstream」「原本的倉庫有更新」。
- 你的倉庫是從別人的 repo copy / fork 來的，想定期拿原作者的新 commit。

## 心智模型

- `origin` = 你自己的倉庫（你 push 的地方）。
- `upstream` = 原作者的倉庫（你只拉、不推）。
- **永遠不對 upstream push**;同步方向只有「拉進來」和「推到自己的 origin」。

## 一次性設定 upstream

```bash
git remote add upstream <原專案網址>
git remote -v   # 確認 origin + upstream
```

**避免每次跳帳號選擇視窗（Windows / Git Credential Manager）**:在 https URL 嵌入使用者名，
GCM 就會直接用該身分、不再彈視窗。只放使用者名、不放 token,無洩漏風險:

```bash
git remote set-url origin   https://<user>@github.com/<user>/<repo>.git
git remote set-url upstream https://<user>@github.com/<上游owner>/<repo>.git
```

> 連 `upstream`（公開 repo、唯讀）也要嵌使用者名 — 否則自動化腳本在 `git fetch upstream`
> 會卡在帳號選擇視窗上不回。

## 先判斷:兩邊有沒有共同歷史

```bash
git fetch upstream
git merge-base main upstream/main   # 印不出 sha = NO COMMON ANCESTOR
```

### 情況 A — 有共同祖先（正常 fork）

直接走下面的「半自動同步流程」。衝突通常很小。

### 情況 B — 無共同祖先（當初是「無歷史匯入」: 直接 copy 程式碼再 push，沒帶原 git 紀錄）

此時 `git merge` 會因 unrelated histories 失敗，硬合會把每個檔案都當雙方各自新建 → 災難級衝突。
正解是**一次性「重新接血脈」**,之後就變成情況 A:

1. 找出你當初匯入的快照點 — 用「你的初版 commit」對每個 upstream 候選 commit 算 diff，
   檔案差異最小者就是快照原點:
   ```bash
   # 對幾個 upstream commit 試:差異最小的就是當初 copy 的版本
   git diff --shortstat <你的初版commit> <候選upstream commit>
   ```
2. 你「真正獨有的工作」= `git diff <快照點> <你的main>`,通常只是少數幾個 commit。
3. 從 upstream 最新版開分支，把你那幾個 commit **cherry-pick** 上去:
   ```bash
   git checkout -b sync-upstream upstream/main
   git cherry-pick <你的commit1> <你的commit2> ...
   ```
4. 過時 / 與上游撞車的重構 commit 該**跳過**（`git cherry-pick --skip`）而非硬套 —
   見下方「衝突判斷」。
5. 型別檢查通過、實測 OK,**且過下方半自動流程 step 6 的獨立覆核閘**（force-push 是
   全流程破壞性最高、最難回退的一步,更需要異源覆核）後,才改名取代 main +
   `git push --force-with-lease`。舊 main 先 `git branch -m main main-old-backup` 留底。

## 半自動同步流程（情況 A，或重新接血脈之後）

**前置條件:工作樹必須乾淨。** 若專案執行中會自動重生檔案（例如 bridge 重生
說明文件弄髒工作樹），同步前先 commit 或 stash 那些變動。

1. `git fetch upstream`
2. 從 `main` 開**拋棄式分支** `sync-attempt`,在它上面 merge — **絕不直接動 main**:
   ```bash
   git switch -C sync-attempt main
   git merge --no-edit upstream/main
   ```
3. **衝突 → 停下來判斷**（見下節）。乾淨 → 進品質閘。
4. **品質閘用「型別檢查」而非「build」**:
   ```bash
   node node_modules/typescript/bin/tsc --noEmit
   ```
   - 為何不用 `npm run build`:build 會 emit 到 `dist/`,執行中的程式會鎖住
     `dist/*.js`,Windows 上造成假性失敗。型別檢查不寫檔、不搶鎖。
   - 為何用 `node` 直跑 tsc 而非 `npx.cmd tsc`:避開 Windows `.cmd` shim 的
     exit-code 假陽性。
   - **不要在同步腳本裡跑 `npm install`**:相依很少在同步間變動,且常觸發有副作用的
     postinstall。若合併帶進新相依,tsc 會以 `Cannot find module` 明確報出,屆時再手動
     `npm install`。
   - **lockfile 善後**:上述手動 `npm install` 產生的 `package-lock.json` 變動要
     **單獨一個 chore commit**(例:`chore: npm install lockfile normalization after
     upstream sync`),不要和 merge commit 混在一起——分開才看得出「哪些改動來自上游、
     哪些只是本地依賴善後」,回溯與 revert 都乾淨。
5. 全綠後**先給人看摘要、實測功能**,確認 OK。**此時仍在 `sync-attempt`,main 一直沒動。**
6. **覆核閘（在 `sync-attempt` 上、合回 main 之前,不可略過）**:push 是唯一對外、難
   回退的一步。**刻意在合回前覆核**——缺陷直接在這條拋棄式分支上修、重審,main 全程
   不碰(守住「絕不直接動 main」);且 diff 基準就是 main、天然存在,不必事先記 sha。
   派**獨立 context 的覆核者**對 sync 結果做對抗式審查(衝突解得對不對、有沒有回退
   上游新功能、本地功能有沒有被合掉):
   - **diff 基準**:`git diff main HEAD`(本次合併相對舊 main 的全部改動)搭配
     `git diff upstream/main HEAD`(合併結果 vs 上游的殘差 = 你的本地增補全集,看
     「本地功能有沒有被合掉」最精準),再加衝突檔逐檔看。
   - **覆核者優先序(異源 > 同源,三級分明、不可混為等價)**:
     ① **異源 model**(例如 Fable5)**優先** — 打破同源盲點(同源自審漏看率高)。
     ② 異源不可用 → 退化用**同 model 新乾淨 context**,回報標「同源異 context」。
     ③ 都沒有 → 至少**人工**逐檔 diff + 實測關鍵路徑,回報標「單源自審」。
   - 覆核出 high/medium 缺陷 → **在 `sync-attempt` 上修完、回到本步重審**,過關才進下一步。
7. 覆核過關才合回 main + 發佈(`--ff-only` 保證合回不引入任何新內容):
   ```bash
   git switch main
   git merge --ff-only sync-attempt
   git push origin main
   git branch -d sync-attempt
   ```
8. 失敗 / 衝突未解時，main 完全沒動、沒 push;放棄就:
   ```bash
   git merge --abort 2>/dev/null; git switch main; git branch -D sync-attempt
   ```

> **Windows 註**:PowerShell / cmd 下 `git fetch` / `clone` / `merge` 常因 stderr 帶
> 進度條或 notice 被 shell 判成 exit 1 假失敗——別憑退出碼就當同步失敗,以實際
> `git status` / ahead-behind 為準。詳見 skill `ms-windows-shell-exit-code-false-positive`。

## 衝突判斷（這是不能自動化的部分）

逐檔看衝突。常見三類:

- **雙方各自新增**（例如各自往同一個陣列加一筆）→ 兩邊都保留。
- **你的重構 vs 上游在同處的演進撞車** → 通常**該採用上游版、跳過你的重構**。
  典型訊號:你的 commit 是「把 inline 邏輯抽成共享函式」,但上游保留 inline 並
  在上面長出新功能(新欄位 / 新流程)。硬套你的舊重構會**回退上游的新功能**。
  這種 commit 用 `git cherry-pick --skip`;需要的話事後在上游新結構上手動補回你要的小行為改變。
- **結構性文件衝突**(`CLAUDE.md` / `AI.md` / `README.md` 這類:本地加了 pointer 或
  段落,上游改了文件結構)→ **不是二選一**,而是「採上游新結構 + 補回本地增補」。
  典型:本地在 `README` 留一行指向 `POLICIES/`,上游重寫了 README 架構 → 採用上游
  新架構,再把本地那行 pointer 補回去;本地增補的實質內容則移進對應子文件
  (如 `AI.md` / `POLICIES/*.md`),避免根文件膨脹。文件衝突別當 code 衝突硬挑一邊。
  **但這只適用「本地是在上游文件上做增補」**;若本地已把該文件**整份改寫**成不同的
  政策文件(fork 的文件路線與上游分家),「採上游新結構」等於丟掉本地文件 → 這屬語意
  取捨,回到本節末的原則**停下來問人**,別預設採上游。

遇到需要取捨的語意衝突,**停下來向使用者說明選項**,不要替他猜。

## 可選:固化成專案腳本

把上面流程寫成 `scripts/sync-upstream.mjs`(node、`spawnSync` 跑 git):
preflight（乾淨樹 / 無進行中 merge / upstream 存在）→ fetch → 算 ahead/behind（0 就結束）→
開 `sync-attempt` → merge → 型別檢查 → 用退出碼區分結果(0 成功/已最新、10 衝突、11 編譯失敗、
3 前置不符)。腳本**只做安全部分、絕不 push**,衝突就停在 `sync-attempt` 留給人/AI 解。

## 反例（不要這樣）

- ❌ 直接 `git merge upstream/main` 進 `main`,然後在主分支上解一堆衝突。
- ❌ 用 `npm run build` 當品質閘(會跟執行中程式搶 dist 鎖)。
- ❌ 自動 push,或硬套過時的本地重構覆蓋上游新功能。
- ❌ upstream URL 不嵌使用者名,導致自動化在 fetch 卡在帳號視窗。
