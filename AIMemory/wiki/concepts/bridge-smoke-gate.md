---
title: Bridge 測試閘門與建置
type: concept
created: 2026-08-01
updated: 2026-08-01
sources: [f_5871a8, f_50951c, f_28e17b, f_da3d5b, f_221993, f_eb4263, f_fad6c9, f_a692b7, f_bfaf63, f_faa25e]
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
- `dist/` **只有 smoke suite 在用**

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

## 為既有 smoke 腳本加單例狀態的陷阱

為既有腳本加 module-level 單例（如 registry）時，要先檢查**既有測試區塊的狀態污染**：`check-draft-streaming.mjs` 的區塊 ①②③④ 刻意不 close（那正是它們要驗的事），加 registry 之後這些實例會殘留在 Set 裡。新區塊必須**先 drain 排空再斷言**，否則會拿到非 0 的 count 並誤刪前面區塊的 fake api 訊息。

## CI 決策（刻意不進版控的 ci.yml）

2026-07-25 裁決：**測試把關靠本機 pre-push hook，GitHub Actions 暫緩導入。** `.github/workflows/ci.yml` 已寫好並在本機驗證通過（當時 86/86），但**刻意保留為未追蹤檔案不進版控**（卡在 PAT 缺 workflow scope）。

⚠️ 未來看到 `?? .github/` 未 commit 屬**預期狀態，不是遺漏**。

## 相關

- [[verification-diagnosis]] — 閘門是否真的會紅（恆真斷言、突變測試、計數閘門自我過期）
- [[bridge-project]] — bridge 專案架構與其他子系統
- [[bridge-pitfalls]] — dotenv 繼承等踩坑的完整清單
- [[dev-tools]] — tsc / shell 相關工具慣例
