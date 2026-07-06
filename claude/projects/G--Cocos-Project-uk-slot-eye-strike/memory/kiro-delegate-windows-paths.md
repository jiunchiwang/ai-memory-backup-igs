---
name: kiro-delegate-windows-paths
description: 委派 Kiro 時 prompt 內的路徑一律用 Windows drive letter 絕對路徑（G:\..., C:\...），避免 /tmp、/c/... 這類 MSYS 映射
type: feedback
originSessionId: 0db9f6d0-6bf9-4389-8128-3b1998a74a26
---
委派 `kiro-cli` 時，委派 prompt 中的檔案路徑一律用 Windows drive letter 絕對路徑（`G:\Cocos_Project\uk_slot_eye_strike\...`、`C:\Users\...`），不要用 MSYS/Git Bash 風格的 `/tmp/...`、`/c/Users/...`、`~/...`。

**Why:** 2026-04-24 /vc-kiro-delegate 端到端驗證時觀察到 Kiro 會把 prompt 裡的 `/tmp/kiro-delegate-test` 自動解析成 `C:\Users\jiunchiwang\AppData\Local\Temp\kiro-delegate-test`。翻譯結果正確，但這是 Kiro 在「推測」MSYS 路徑映射——每多一層推測就多一層出錯空間，而且 Step 2 `--resume` self-review 時 Kiro 回報的路徑會是 Windows 格式，主 agent 這邊 bash 讀檔驗證時又要再換回 MSYS 格式，來回轉譯容易混淆。

**How to apply:**
- 寫委派 prompt 的「明確檔案路徑」要素時，統一用 `C:\...` 或 `G:\...` 格式
- 任務需要「當前目錄」語意時，prompt 開頭明寫「工作目錄：`<Windows 絕對路徑>`」而不是依賴 cwd
- 臨時檔案首選 `C:\Users\jiunchiwang\AppData\Local\Temp\<task-name>\`（Windows 原生 Temp），不要用 `/tmp/...`
- 避免 `~`、`.`、相對路徑、MSYS 掛載點（`/c/`、`/g/`）
