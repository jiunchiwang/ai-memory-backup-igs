# igs-uof 安裝說明（Mac / Windows 皆適用）

查公司內網 UOF 的 Claude Code skill：加班時數與個人目標進度、剩餘特休、出勤打卡、請假記錄、待簽核表單、同仁分機。第一次使用要做三件事：**放好 skill → 建環境 → 設定帳密**。

## 0.（舊版使用者）從 vc-uof-hours 遷移

已裝過舊版 `vc-uof-hours` 的話：

1. 把 skills 目錄下的資料夾改名：`vc-uof-hours` → `igs-uof`（或直接刪掉換新版資料夾）。
2. **重建 venv**（venv 內含絕對路徑，改名後會壞）：刪掉 `igs-uof/.venv`，照下方步驟 2 重建。
3. 設定檔 `~/.config/uof/config.json` **不用動**，直接沿用。

## 1. 放好 skill

把整個 `igs-uof/` 資料夾放到你的 Claude Code skills 目錄：

- Mac / Linux：`~/.claude/skills/igs-uof/`
- Windows：`C:\Users\<你的帳號>\.claude\skills\igs-uof\`

## 2. 建 Python 環境（venv + 套件 + 瀏覽器）

需要 Python 3.10+。在 skill 資料夾裡開終端機執行：

**Mac / Linux**
```bash
cd ~/.claude/skills/igs-uof
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m playwright install chromium
```

**Windows（PowerShell）**
```powershell
cd $HOME\.claude\skills\igs-uof
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m playwright install chromium
```

> Windows 未逐項回歸實測（腳本以跨平台寫法開發：UTF-8 輸出、`os.path.expanduser` 路徑）；有問題請回報。

## 3. 設定帳密與偏好（設定檔）

複製範例檔 `config.example.json`，填入你的 UOF 帳密，另存成設定檔：

- Mac / Linux：`~/.config/uof/config.json`
- Windows：`C:\Users\<你的帳號>\.config\uof\config.json`

```json
{
  "account": "你的UOF帳號",
  "password": "你的UOF密碼",
  "monthly_target": 20,
  "countable_basis": "weekday+holiday",
  "status": "approved+pending"
}
```

- `monthly_target`：你的個人每月加班目標時數（有人抓 20、有人抓 30，自己設）。
- `countable_basis`：`weekday+holiday`=只算平日+假日加班（不含補班，預設）；`total`=含補班。
- `status`：`approved+pending`=同意+簽核中（預設）；`approved`=只算已核准。

> ⚠️ 這個檔含明文密碼，請勿分享、勿放進 git。Mac/Linux 建議 `chmod 600 ~/.config/uof/config.json`。
> macOS 使用者也可改用 Keychain（不放密碼進檔案）：`security add-generic-password -s uof-hr -a <帳號> -U -w`，設定檔只留 `monthly_target` 等偏好即可。
> 登入狀態會存 `~/.config/uof/session.json`（自動建立與管理），有效期內查詢免重新登入。

## 4.（選用）加班目標的「每天要加幾小時」

要算「今年剩下每個上班日平均要加幾小時」需要工作日資料：

- **2026 年已內建**，免下載，直接可用。
- 其他年份：把公司發的「IGS 行事曆」Excel（檔名要含民國年，如 `IGS 116行事曆.xls`）放到 `下載/Downloads` 資料夾即可自動讀取。
- 都沒有時會用「平日扣七月旅遊假 5 天」估算，並標註為估計值。

## 使用

環境設定好後，直接對 Claude Code 用中文問即可，例如：

- 「我這個月加班幾小時？距離目標還差多少？」
- 「特休還剩幾天？」
- 「我今天幾點打卡進來的？」「上週出勤有沒有異常？」
- 「我今年請了幾天假？」「六月的特休記錄給我看」
- 「我有沒有待簽的單？」「我昨天送的加班單簽到哪了？」
- 「幫我查一下某某某的分機」
- 「幫我填加班單」（`scripts/uof_form.py`，個人擴充功能，見下方說明）

需要連上**公司內網 / VPN** 才查得到（站台 `http://uof`）。

> ⚠️ **`scripts/uof_form.py`（填加班單）是個人擴充功能，不在本 SETUP.md 主要涵蓋的公司共享唯讀範圍內**。它會預填加班單並截圖給你確認，二階段明確確認後才真正送出（見 `DESIGN.md`「v1 加班單填單設計」章節）。若要把這份 skill 整包分享給同事，請自行評估是否移除該檔案。
