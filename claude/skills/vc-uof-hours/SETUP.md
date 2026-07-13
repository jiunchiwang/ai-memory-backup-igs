# vc-uof-hours 安裝說明（Mac / Windows 皆適用）

查 UOF 加班時數與剩餘特休的 Claude Code skill。第一次使用要做三件事：**放好 skill → 建環境 → 設定帳密**。

## 1. 放好 skill

把整個 `vc-uof-hours/` 資料夾放到你的 Claude Code skills 目錄：

- Mac / Linux：`~/.claude/skills/vc-uof-hours/`
- Windows：`C:\Users\<你的帳號>\.claude\skills\vc-uof-hours\`

## 2. 建 Python 環境（venv + 套件 + 瀏覽器）

需要 Python 3.10+。在 skill 資料夾裡開終端機執行：

**Mac / Linux**
```bash
cd ~/.claude/skills/vc-uof-hours
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m playwright install chromium
```

**Windows（PowerShell）**
```powershell
cd $HOME\.claude\skills\vc-uof-hours
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m playwright install chromium
```

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

- `monthly_target`：你的每月加班目標時數（有人抓 20、有人抓 30，自己設）。
- `countable_basis`：`weekday+holiday`=只算平日+假日加班（不含補班，預設）；`total`=含補班。
- `status`：`approved+pending`=同意+簽核中（預設）；`approved`=只算已核准。

> ⚠️ 這個檔含明文密碼，請勿分享、勿放進 git。Mac/Linux 建議 `chmod 600 ~/.config/uof/config.json`。
> macOS 使用者也可改用 Keychain（不放密碼進檔案）：`security add-generic-password -s uof-hr -a <帳號> -U -w`，設定檔只留 `monthly_target` 等偏好即可。

## 4.（選用）加班達標的「每天要加幾小時」

要算「今年剩下每個上班日平均要加幾小時」需要工作日資料：

- **2026 年已內建**，免下載，直接可用。
- 其他年份：把公司發的「IGS 行事曆」Excel（檔名要含民國年，如 `IGS 116行事曆.xls`）放到 `下載/Downloads` 資料夾即可自動讀取。
- 都沒有時會用「平日扣七月旅遊假 5 天」估算，並標註為估計值。

## 使用

環境設定好後，直接對 Claude Code 用中文問即可，例如：
- 「我這個月加班幾小時？還差多少才達標？」
- 「今年加班進度夠不夠？剩下每天要加幾小時？」
- 「特休還剩幾天？」

需要連上**公司內網 / VPN** 才查得到（站台 `http://uof`）。
