---
title: Bridge 測試閘門與建置
type: concept
created: 2026-08-01
updated: 2026-08-15（新增：mutate-gate harness 慣例（紅燈行規範／noUnusedLocals 陷阱／無 timeout 風險）、hang detection 門檻侵蝕、raw JSON-RPC probe 查證法；更正：「dist 只有 smoke suite 在用」為誤，MCP 子行程亦吃 dist）
sources: [f_5871a8, f_50951c, f_28e17b, f_da3d5b, f_221993, f_eb4263, f_fad6c9, f_e2e14a, f_bfaf63, f_faa25e, f_40504b, f_9744ee, f_771784, f_204218, f_ea9ccb, f_dac7e8, f_29e3fe, f_173f37, f_75ce78, f_9219db, f_940b63, f_2f4ae9, f_88d3a1, f_f32658, f_b01fe2, f_ed5f8b, f_cb572a, f_06ae88, f_23885a, f_377321, f_932293, f_156659, f_820b01, f_3c7003, f_30d188, f_47b507, f_5e618d, f_3e05f4, f_0b4a7b]
history_sources: [f_a692b7]
---

# Bridge 測試閘門與建置

## 概述

telegram-kiro-bridge 的品質把關由三層構成：**tsc 型別檢查 → smoke suite（fast / full tier）→ pre-push hook**。這一頁記錄這條鏈上的機制、慣例與踩坑；閘門「有效性」層面的方法論（恆真斷言、突變測試）見 [[verification-diagnosis]]。2026-08-01 的 topic review 從過大的 [[bridge-project]] 拆出。

## 把關鏈

| 層 | 指令 | 說明 |
|---|---|---|
| 型別 | `npx tsc --noEmit` | 改完 `src/` 必跑；`--noEmit` **不寫檔** |
| 建置 | `npx tsc -p .` | 產 `dist/`；**smoke 讀 dist 不讀 src**，改完 src 沒重編會用過期 dist 跑出假失敗 |
| 測試 | `npm run smoke -- --fast` | fast tier；`SMOKE_ONLY=check-foo` 可只跑單支 |
| Push 閘 | `.githooks/pre-push` | 自動跑 build + fast tier，紅了就擋；Telegram 端等價入口是 `/smoke` |

`core.hooksPath=.githooks` 是 repo 設定——裝進 `.git/hooks/` 的 hook 永不執行。`pre-commit` 會自動跑 `scripts/sync-skills-to-repo.mjs`，把 `default-skills/` 從本機 skill 目錄（取最新 mtime）覆蓋同步回 repo，改 `default-skills` 前要注意可能被它蓋掉。

## dist 與跑著的 bridge 是兩件事

**「dist 已重編」≠「跑著的 bridge 已載新碼」。** 兩者互不相干：

- bridge 進程走 `package.json` 的 dev script（`tsx src/index.ts`）**直讀 src** → 重啟就帶新碼，不需要先 build
- `start.bat` 是 `:loop` + `goto loop` 的 supervisor 迴圈 → 任何 `process.exit`（含 `/restart` 與 `<<RESTART>>`）都會自動被帶回來
- `dist/` 的消費者是 **smoke suite（`scripts/check-*.mjs` 幾乎全部 `import "../dist/*.js"`）＋ MCP server 子行程（`dist/mcp-memory.js` / `mcp-google.js` / `mcp-actions.js`）**，跑著的 bridge 主程序不在其中
  - ⚠️ 本行 2026-08-15 更正：原文寫「`dist/` **只有 smoke suite 在用**」，該「只有」為誤——同頁 [[bridge-infra]] 早就記著 MCP 子行程也吃 dist，兩條並存互相打臉。證據：`package.json` 的 `bin` 指 `dist/mcp-memory.js`、`scripts/setup-mcp.mjs:25-27` 三個 MCP 路徑皆在 `dist/`
- `start.bat` 裡的 `call npm build` 是 no-op（`npm build` 非有效指令，實跑得 `Unknown command: "build"`）∴ **重啟 bridge 不會重建 dist**，smoke 前的 build 仍要自己跑

2026-07-31 差點把 dist build 時間當成「修法已生效」的證據；正確判準是 **src mtime vs bridge 進程啟動時間**。

## 環境隔離（smoke 假失敗的根因）

⛔ **不要直接跑 `node scripts/check-*.mjs`**。在 bridge spawn 出來的 agent session 裡會整批假失敗——繼承到的**空值**環境變數（`TELEGRAM_BOT_TOKEN=""` 等）不會被 dotenv 覆蓋（dotenv 不覆蓋既有 env），`config.required()` 就 throw。

`.env` 實際含完整 46 字元 token，所以「sanitized 版需加 dummy」那條舊記錄已過時——真因是繼承空值。走 runner（`scripts/smoke-env.mjs`）它會自己隔離環境。手動跑的話要 `env -u` 清掉繼承變數，但**必須保留 `MEMORY_DIR`**（清掉會 fallback 到不存在的路徑造成 ENOENT 假失敗）。

另注意此機器的 Kiro agent config 路徑是 `C:\Users\jiunchiwang\.kiro`（非舊機器的 `tonykuo`），smoke 中硬寫舊路徑的地方要留意。

## 計數同步儀式（新增測試腳本的隱性成本）

runner 用 `readdirSync` 以 `check-*` 前綴**自動發現**腳本 → 新增一支 `check-*.mjs` 就會改變 suite 支數，而那個數字當時散在**約 10 個檔案**（README / CLAUDE.md / AGENTS.md / AI.md / usage-guide.html / pre-push 註解 / smoke.ts 註解 / bot-setup desc / runner 自印字串）。

由此衍生兩個慣例：

- **使用者偏好把新測試加進既有 smoke 腳本而非新增檔案**（可接受為了可測性做小幅重構，例如把嵌在巨型函式裡的邏輯抽成獨立模組，但避免觸發計數同步儀式）
- **會對真實 chat 發訊息的診斷探針刻意命名 `probe-*` 而非 `check-*`**（例如 `probe-draft-clearing.mjs`）——後者會被 runner 自動執行；探針另外預設 dry-run、要 `--go` 才動手

## 閘門該驗什麼、不該驗什麼

- ✅ **硬計數**（支數、指令數、事件型別數）→ 納入機械檢查，但期望值必須當場向 `run-smoke-suite.mjs --list` 取得，**零硬寫**
- ❌ **耗時** → 不納入。run-to-run 約 8% 變異（2026-07-31 full tier 實測 260.7s / 274.1s / 249.9s），納入會變成每次跑都可能紅的雜訊閘；耗時只寫進文件並**標註量測日期**

## noUnusedLocals 閘門（2026-08-02 新增）

`tsconfig.json` 已開啟 `"noUnusedLocals": true`（commit 134aebe），一次性清掉 22 檔共 72 處未讀取宣告（64 個未用 import + 8 個 local）。開之前孤兒 import／死碼只有異源獨立覆核（如 Fable5）或手動 grep 才抓得到（2026-07-29 sync-upstream 覆核實測，抓到 5 個孤兒 import + 1 個死碼函式）——這條舊記錄已過時，現在型別系統會直接擋。

`noUnusedParameters` 刻意**不開**：11 處多為 callback 佔位參數，開了會逼人補 `_` 前綴。這項調整也讓 push 前異源覆核的成本分級（見 [[bridge-acp]]）第一條規則落地：「孤兒 import／死碼不派人，交給型別系統」。

## 為既有 smoke 腳本加單例狀態的陷阱

為既有腳本加 module-level 單例（如 registry）時，要先檢查**既有測試區塊的狀態污染**：`check-draft-streaming.mjs` 的區塊 ①②③④ 刻意不 close（那正是它們要驗的事），加 registry 之後這些實例會殘留在 Set 裡。新區塊必須**先 drain 排空再斷言**，否則會拿到非 0 的 count 並誤刪前面區塊的 fake api 訊息。

## check-draft-streaming.mjs 的額外陷阱（2026-07-31～08-01）

同一支測試檔的另外三則陷阱，與上面「加單例狀態」屬同批教訓：

- **零 import 硬約束**：`src/status-channel.ts` 刻意維持零 import——`check-draft-streaming.mjs` 是把該檔單獨 transpile 成 data-URL module 載入的，加任何 import 測試就載不起來。因此進程層 registry 必須自我包含（含自帶 `setTimeout` 上界，不可引用共用的 `withTimeout`）。
- **「某字串必須完全不存在於原始碼」斷言會被自己的說明註解打成恆假**：正確做法是先濾掉註解行只掃可執行碼——解釋「為何移除」的註解必須留著，否則下一個人會照舊前提把碼加回來（2026-08-01 實證）。
- **把已被推翻的前提釘死在測試裡會變成修復的阻礙**：原本要求送出條件必須含 `|| statusWrote`、要求 `"status-restore"` 字串存在，前提實測推翻後這兩條反而擋住正確修法，須改寫成**反向釘死**（該字串不得出現）加位置比較斷言（2026-08-01）。

## 測試 fixture 與呼叫慣例陷阱（2026-08-05～06）

**Fixture 形狀要跟生產一致，否則綠燈與「沒驗到」外觀相同**（ms-vacuous-test-gate 的形狀）：`check-codex-skill-links.mjs` 用 `mkdirSync` 建實體目錄當 Kiro skill，8 項全綠卻完全測不到 `Dirent.isDirectory()` 對 junction 回 `false` 的 bug——因為生產環境的 skill 目錄是 junction 而非實體目錄。已改成 junction 型 + 實體目錄型各一並做過變異測試。

**命令列 argv 要傳分開的 token，不能傳一整串加引號的字串**：`check-acp-model-effort.mjs` 的位置參數取 `command = rest[0]`，若把 `"npx -y @agentclientprotocol/codex-acp"` 當單一參數傳入，含空白的整串會變成 command，`AcpClient` 的 `quoteForShell` 再把它整包加引號，cmd.exe 就去找一個檔名叫這整串的程式 → **exit 1 且完全沒有 stderr**。2026-08-06 因此誤判成「新套件走 bridge spawn 路徑會死」，花了五輪對照才發現是呼叫方式錯——這個失敗形狀（exit 1 + 零 stderr）之後應先懷疑命令解析，不是 adapter。已補防呆（含空白就自動 split，比照 `ACP_AGENT_COMMAND` 的既有處理方式）。

**BC-x 斷言編號是全專案追溯主軸，同號異義會讓事故追查拿到不相干的斷言**：新增斷言前要 grep 該檔全部既有 BC-x 編號確認真的沒被用過，不能只挑下一個看起來沒用到的數字。2026-08-06 自己在 `check-transient-retry.mjs` 撞到 BC-17（該號正是先前為避開 BC-15 撞號才從上游平移過來的），由 Fable5 覆核抓到才改為 BC-18a/b（commit `0546eeb`）；改號時要留下改號理由，不能只是靜默換號。

## smoke suite 逾時 flaky 診斷（2026-08-12）

`check-session-resume` 的 M1/M2/M3 在 fast tier 內 FAIL（50.3s）、單獨跑卻 PASS（17.1s）——
**單支 FAIL、單獨跑卻 PASS，且失敗的是連續一組斷言（不是隨機單點）**，是查「共用 setup」與
「子行程輸出解析方式」的訊號，不要當隨機抖動。這次三條共用 `JSON.parse(out.split("\n").pop())`
只認子行程 stdout 的最後一行，parse 失敗時 fallback 成 `r={}`，子行程多印任何一行就三條同時垮。

根因追下去發現是 `runM` 的 `timeout: 15000` 太小——該子行程要 import 整包 `dist/sessionManager.js`，
獨立跑實測 30.3s / 11.1s / 18.0s，冷載入是上限的**兩倍**；平常會過只因為在 suite 裡 `dist/` 已被
前面測試暖進 page cache。已修（commit `d128f28`，timeout → 120s ＋ 解析失敗改印原文，因為逾時
原本被 `catch {}` 吞掉、偽裝成「三個斷言不成立」）。

### 逾時的兩類分法：A 類預算 vs B 類上界

全面掃過 smoke suite 的寫死逾時後歸納出可重用的分法：

| 類型 | 定義 | 處置 |
|---|---|---|
| **A 類 = 等子行程的預算** | 負載敏感，該遠大於實測最大值 | 可調大（`check-mcp-readonly` 10s→120s、`check-auth-recovery` 20s→120s） |
| **B 類 = 行為斷言的時間上界** | 調大等於掏空測試 | 絕不可動（`check-mcp-readonly` 的 `elapsed < 9s`、`check-worker-terminate` 的 `elapsed < 2000`、`check-stale-agent-procs` 的 `< 10 分鐘`） |

⚠️ 兩個踩雷點：① `check-mcp-readonly` 的 9s 上界**正是靠** `RESPONSE_TIMEOUT_MS` 生效（阻塞回歸時
send 等滿它才回 null → elapsed 超標），沒讀到這段就盲調會誤以為在掏空斷言；② `run-smoke-suite.mjs`
用 `spawnSync`、**沒有 per-script timeout**——各腳本自己的 timeout 是唯一 hang 兜底，只能調大不可
移除。同類缺陷仍存在於 `scripts/check-mcp-readonly.mjs` 的 `RESPONSE_TIMEOUT_MS = 10000`（2026-08-12
高負載下實紅過一次，單獨跑 14.9s 通過），尚未修。本 repo fast tier 實測同日跑出 416s 與 1332s
（3.2 倍差距），是這類 flaky 的負載背景。

### 突變存活時先驗證突變真的套用了

`positiveIntOr` 拿掉 `Number.isFinite` 的突變一度存活，先驗證該字串出現次數 1→0、程式碼可見已改，
才確認是**等價突變**（下界 `>0` 與上界 `<=max` 的檢查已涵蓋 NaN/±Infinity，因 `Math.floor(NaN)>0`
為 false、`Infinity<=max` 為 false），據此把該行當死碼刪除。教訓：突變測試出現存活的突變體，先確認
「突變真的套用了」再判斷是測試太弱還是等價突變——順序反了會錯殺測試或錯放死碼。

## Mutate-gate Harness 慣例與陷阱（2026-08-14）

`scripts/mutate-gate.mjs` 只認輸出含 `❌` 或 `[FAIL]` 的紅燈行——「只丟例外不印標記」的閘門會被判成 false-kill；harness 註解明訂的處置是「讓閘門去符合慣例」（改成收集全部失敗再 `exit 1` 並印 `❌`），不是放寬比對。

三個容易踩的坑：

- **`run()` 沒有 timeout** ∴ 會掛住的變異體會拖死整個變異測試。驗「無界重試」這類缺陷時，變異要用「放寬上限」而非「拿掉上限」，並把便宜的原始碼斷言排在會掛住的端到端斷言之前讓變異快速紅燈。
- **變異體撞 `noUnusedLocals` 會被判 error 而非 killed**：拿掉呼叫或改成 `if (false)` 會讓符號變孤兒（TS6133）或只寫不讀；正確做法是保留讀取點只讓條件不成立（如 `if (x && false)`、`return f(x) || true`）。
- **Windows Git Bash 下不要用 `/tmp` 存突變備份**：`cp` 會成功（Git Bash 有虛擬映射），但 Node 收到字面路徑會解析成 `G:\tmp` 而 ENOENT，突變根本沒寫進檔案，測試對未突變原檔跑出「1/1 passed」的假綠（2026-08-01 實證）。改用 repo 內相對路徑（`./.rp.bak`）。

驗「順序型承重不變式」的可重用三件套：模組契約測試（fake api 記錄呼叫）＋ 來源順序斷言（`indexOf(A) < indexOf(B)`，錨在該呼叫點獨有的字串上避免多處 match）＋ mutation test（手動搬錯位置確認測試真的紅，還原後 `git diff` 確認無殘留）。

## 效能觀察：hang detection 門檻侵蝕（2026-08-13）

Smoke suite 整體的 hang detection 門檻安全邊際已被 suite 耗時成長侵蝕：耗時增至 432.1s（7.2 分）後，邊際從約 2 倍降到約 1.39 倍；使用者決定刻意不調高門檻。此條與上面「A 類/B 類逾時分法」互補——那條管單支腳本的逾時，這條管整個 suite 之上的 hang 兜底，下次再加 smoke 腳本前要先意識到這道兜底已所剩不多。

## 查證 ACP session 實際跑什麼 model（raw JSON-RPC probe）

唯一可靠法：spawn adapter → `initialize` → `session/new` → 讀回傳 `configOptions` 裡 `id==="model"` 的 `currentValue`（`options[].description` 開頭即真名如「Opus 5 with 1M context」）。`scripts/check-acp-model-effort.mjs` 只驗 pin 成不成功、不告訴你實際在跑什麼——`claude-agent-acp` 不支援 `effort` config option（`session/set_config_option` 設 effort 會回 `-32603 Unknown config option`，bridge 已 graceful ignore，屬已知限制非故障，該閘門因此必然報 effort 拒絕）。

## CI 決策（刻意不進版控的 ci.yml）

2026-07-25 裁決：**測試把關靠本機 pre-push hook，GitHub Actions 暫緩導入。** `.github/workflows/ci.yml` 已寫好並在本機驗證通過（當時 86/86），但**刻意保留為未追蹤檔案不進版控**（卡在 PAT 缺 workflow scope）。

⚠️ 未來看到 `?? .github/` 未 commit 屬**預期狀態，不是遺漏**。

## 相關

- [[verification-diagnosis]] — 閘門是否真的會紅（恆真斷言、突變測試、計數閘門自我過期）
- [[bridge-project]] — bridge 專案架構與其他子系統
- [[bridge-pitfalls]] — dotenv 繼承等踩坑的完整清單
- [[dev-tools]] — tsc / shell 相關工具慣例
