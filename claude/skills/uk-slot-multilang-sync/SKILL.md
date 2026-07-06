---
name: uk-slot-multilang-sync
description: >-
  把規格 xlsx 的多國語言文字批次同步進 uk 線上老虎機框架各語系的
  gameStrings.xml。當使用者要在老虎機專案新增/更新多國語言字串、提到
  「gameStrings.xml」「多國語言」「多語系文字」「i18n 字串」「把 xlsx 的翻譯填進去」、
  或要為某個 Key 一次寫入多國(常見 26 國)文字時使用。僅適用線上部門 uk 框架
  (plist 格式 gameStrings.xml、每語系一目錄、欄標題括號內為語系代碼);
  商用部門或其他文字格式不適用。
---

# uk 老虎機 多國語言同步

把規格 xlsx「多國語言」工作表某幾列的各國文字,依指定 Key 批次 upsert 進
`assets/game/Text/<語系代碼>/gameStrings.xml`。一次處理所有語系,取代手動逐檔貼字。

## 適用前提(先確認,不符就停)

此 skill 假設 **uk 線上老虎機框架**的慣例:

1. 每個語系一個目錄,目錄名 = 語系代碼(`tw`/`cn`/`en`/...),底下有 `gameStrings.xml`。
2. `gameStrings.xml` 是 plist,每個字串是一個標籤:`<KEY>文字</KEY>`,全部在 `<dict>...</dict>` 內。
3. xlsx「多國語言」工作表:**列 = Key、欄 = 語系**,語系欄標題的括號內就是代碼,
   例如「繁體中文(tw)zh-TW」→ `tw`。

驗證一次:`ls assets/game/Text` 看是否一堆語系目錄、各有 `gameStrings.xml`;
打開一個確認是 `<KEY>文字</KEY>` 格式。不符合(例如商用部門用別種格式)→ **不要用此 skill**,改手動或另議。

## 工作流

### 1. 檢視 xlsx,確認語系欄與列號

用 openpyxl 看「多國語言」工作表的第 1 列(欄標題)與要處理的資料列:

```python
import openpyxl
wb = openpyxl.load_workbook("規格.xlsx", read_only=True, data_only=True)
ws = wb[[s for s in wb.sheetnames if "多國語言" in s][0]]
for i, row in enumerate(ws.iter_rows(min_row=1, max_row=60, values_only=True), 1):
    print(i, [ (c or "")[:20] if isinstance(c, str) else c for c in row[:5] ])
```

### 2. 建對應表(由你 agent 建立,不是叫使用者手填)

`string_keys.tsv` 是中繼產物,由 **你(agent)** 依使用者給的資訊建立/填寫。
使用者通常只會「動嘴」:說「把這幾個 Key 加進去」或「Key=X 在第 N 列」。你的工作:

- 使用者給了 Key + 列號 → 直接落成 tsv 各一行。
- 使用者只給 Key 清單、不知道列號 → 你去 xlsx 比對文字幫他定位列號,再填。
- 只有單筆 → 臨時建一行的 tsv 也行(例如 `_claude_temp/string_keys.tsv`)。

複製 `scripts/string_keys.tsv` 範本當起點,每行 `Key <Tab> 列號 <Tab> 備註`。

🔴 **列號 = xlsx 左側的「實際 Excel 列號」,不是內部「編號」欄。** 編號欄常中途斷掉,拿來當識別會錯位。

### 3. dry-run 預覽 + 語意核對(最重要)

```bash
python <此skill>/scripts/sync_game_strings.py --xlsx 規格.xlsx --mapping _claude_temp/string_keys.tsv
```

dry-run 只印不寫。**務必核對每個 Key 對到的列,語意是否正確** —— 把該列的 en/tw 文字
跟現有 XML 裡同 Key 的值比一比。實務上「列號填錯一格」很常見且 dry-run 數字看起來照樣正常
(例如 EXTRA_BET_DESC 本該對「OFF→ON 開啟選擇畫面」那列,卻填到「初始乘倍」那列),
唯一抓得到的方法就是人眼核對語意。報告會列出每語系「新增/更新/缺字」,缺翻譯的語系要回報補齊。

### 4. 確認無誤才寫入

```bash
python <此skill>/scripts/sync_game_strings.py --xlsx 規格.xlsx --mapping _claude_temp/string_keys.tsv --write
```

行為:Key 已存在 → 覆蓋更新;不存在 → 插在 `</dict>` 前。保留各檔原本換行(CRLF/LF)與 UTF-8,
文字自動做 XML 跳脫(`& < >`)。寫入後用 `git diff` 抽查 2-3 個語系確認內容正確。

## 腳本參數

`scripts/sync_game_strings.py`(路徑全相對「當前工作目錄」,在專案根目錄執行):

| 參數 | 預設 | 說明 |
|------|------|------|
| `--xlsx` | (必填) | 規格 xlsx 路徑 |
| `--mapping` | `./string_keys.tsv` | Key↔列號對應表 |
| `--text-dir` | `./assets/game/Text` | 語系目錄根 |
| `--sheet` | 自動偵測含「多國語言」者 | 工作表名(多個符合時需手動指定) |
| `--xml-name` | `gameStrings.xml` | 各語系內 XML 檔名 |
| `--write` | (關;預設 dry-run) | 加上才實際寫入 |

需要 `openpyxl`(`pip install openpyxl`)。

## 常見問題

- **某語系報「找不到對應 gameStrings.xml」**:欄標題括號代碼與目錄名對不上 → 檢查 xlsx 標題或目錄。
- **缺字(∅)**:該列在某語系儲存格是空的 → 翻譯未提供,回報請對方補,腳本不會寫空字串。
- **git 跳 `CRLF will be replaced by LF`**:repo 換行設定行為,非腳本造成,磁碟檔仍為原換行。
- **新 Key 大量新增後**順序在 `</dict>` 前,屬正常;不影響讀取。
