---
name: excel-to-ai-doc
description: Convert image-heavy Excel game spec spreadsheets (.xlsx) into an AI-readable knowledge structure — Markdown text + extracted original images (anchored to their source cells) + cell colors preserved as a legend + metadata.json + a self-validation report. Use when the user wants to turn a 規格書/spec/design xlsx into something an AI or agent can read, asks to "convert this spec to markdown", "make this xlsx AI-readable", "extract images and tables from this spreadsheet for analysis", or needs to feed a slot/game spec workbook to a vision model. Triggers on game design specs, paytables, UI/flow screenshots embedded in .xlsx. NOT for clean tabular data exports (use a plain csv/markdown converter) or non-xlsx files.
---

# excel-to-ai-doc

## Overview

Converts a spec `.xlsx` (multi-sheet, merged cells, colour-coded, lots of embedded
screenshots/flow diagrams) into:
`markdown/` (text + tables; sparse "document" sheets rebuilt as `[cell]`-tagged lists,
dense tables rebuilt with merged-cell values filled across their span, cell colours
carried as `[c1]` tags backed by a legend) + `images/` (original PNGs, named
`<sheet>_<cell>_<orig>.png`) + `metadata/` (`metadata.json`, `validation.txt`,
`stats.json`) + `source/` (xlsx backup).
The **original images are the source of truth** — this tool does NOT OCR them.

## Prerequisites

**With `uv` (preferred, zero setup):** nothing to install. `scripts/convert.py` carries
its dependencies as a [PEP 723](https://peps.python.org/pep-0723/) inline block, so
`uv run` resolves and caches them in uv's own global cache on first run. Check with
`uv --version`; install via `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
(Windows) or `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux).

**Without `uv`:** `pip install -r scripts/requirements.txt` (markitdown[xlsx], openpyxl),
once per machine, then run with `python`.

## Step 1 — Convert

The script lives in this skill's `scripts/` directory — use the path where this skill is
installed (e.g. `~/.claude/skills/excel-to-ai-doc`, `~/.kiro/skills/excel-to-ai-doc`,
`$HOME/.agents/skills/excel-to-ai-doc`).

```bash
uv run <this-skill-dir>/scripts/convert.py "<path/to/spec.xlsx>" [output-dir]
# 或（已 pip install 過）：python <this-skill-dir>/scripts/convert.py ...
# output-dir defaults to ./output/<xlsx-stem>/ relative to Python cwd
```

**⚠️ 建議明確指定 output-dir**：預設的 `./output/` 是相對於 agent 當前工作目錄，不是 xlsx 所在位置。不指定時產出可能跑到非預期的地方。

**⚠️ Windows 注意**：腳本的 `print()` 進度訊息在 Windows cmd/PowerShell 下可能因 cp950 編碼問題不顯示（但轉換仍正常執行）。如需看進度，可設環境變數：`set PYTHONUTF8=1`。

**⚠️ Windows + 檔名含單引號（`'`）或其他特殊字元**：cmd.exe 的雙引號無法正確處理路徑中的 `'`（會靜默失敗 exit code 1、無輸出）。改用 PowerShell 執行，單引號內的 `'` 用 `''` 跳脫：
```powershell
powershell -Command "$env:PYTHONUTF8='1'; python -u '<script>' '<file-with-apostrophe''s-name.xlsx>' '<output-dir>'"
```

**⏱ 大檔案（>10MB / 含大量嵌入圖）可能需要 10-30 秒**，期間無輸出不代表失敗。

Re-running is safe: it skips copy-to-self and clears `images/` first, so no stale files. No need to delete the old output.

## Step 1.5 — 讀 `metadata/validation.txt`，不要預設成功

腳本最後會做四項自我驗證並印出來（圖片錨定、sheet 形狀、資料覆蓋、公式快取；同時
寫進 `metadata/validation.txt`）。**先讀第一行的「整體：」**再往下回報：

- **`整體：通過`** → 無工作表遺失、密集表未縮水、無「有內容卻輸出為空」、無公式缺快取。可以當完整產出使用。
- **`整體：有需要人工確認的項目`** → 逐項看 ⚠，不要籠統說「轉換失敗」：
  - **`⚠ N 張圖在 xl/media 但無 drawing 錨點`** — 這是**情報不是錯誤**。xlsx 裡確實存在
    但沒有儲存格錨點的圖（背景圖、被刪 anchor 的殘留、或 Google Sheets 匯出掉錨點）。
    數量少屬正常；若接近總數，代表這份 xlsx 的圖幾乎都沒錨點，要回頭確認來源匯出方式。
  - **`⚠ 密集表比 MarkItDown 版小`** — 這個要當**真問題**查。重建版理應 ≥ MarkItDown 版
    （合併補值只會讓表變大）。變小代表重建邏輯漏了東西。
  - **`⚠ 有內容卻輸出為空的工作表`** — 真問題，該 sheet 的資料沒有出口。
  - **`⚠ N 格有公式但無 cached 結果`** — 真問題，而且**要回頭找人處理**。openpyxl
    讀的是 Excel 上次存檔時算好的快取值；沒有快取的公式格會讀成 None。工具已回填
    公式字串（所以不會靜默消失），但那是 `=SUM(...)` 而不是數字——規格要的是數字。
    請對方在 Excel 開啟該檔重新存檔（會寫入快取）後再轉一次，不要拿這份輸出去推
    數值。

`metadata/stats.json` 有逐 sheet 的機器可讀版本（mode / 非空格數 / 行列數 / 合併補值數）。

## Step 2 — Consume the output (read this before answering spec questions)

The whole point is selective, anchored retrieval — do NOT dump every image into context.

1. **Read `markdown/<stem>.md` first** to locate the relevant area by text.
2. **Match a `[cell]` tag** (e.g. `[B124]`) in the `.md` → look it up in `metadata.json` `images[]` → get the original PNG path.
3. **Send the ORIGINAL PNG to a vision model** (Claude / GPT / Gemini). Never substitute OCR — these are flow charts, state diagrams, annotated UI screenshots whose meaning is visual.

### How to read each part of the output

- **`### 本工作表圖片`** in the `.md` — `[cell]` → image. The join key into `metadata.json`.
- **`### 本工作表標註（圖形文字）`** — callout text overlaid on screenshots (e.g. COLLECT step sequence), extracted from vector shapes. Gives the "which step is this screenshot showing" context. Also in metadata `shapes[]`.
- **Cell lists** (`- **[B13:C19]** 基本規格說明`) — sparse "document" sheets are rendered as cell-addressed lists, not tables. A `range` address (e.g. `[B13:C19]`) means a merged block; the rows it spans that follow it belong under it. Zero `NaN` noise by design.
- **Dense tables** — rebuilt from openpyxl, not MarkItDown. A merged cell's value is **repeated across every cell of its span** (GFM has no colspan/rowspan; without this the covered cells are blank and their owning header is invisible). A merge whose repeated text would exceed the bloat cap shows `(→ 合併自 B12)` instead — follow the backreference to that cell for the full text.
- **`[c1]` 顏色代號** — appended after a cell's text; look it up in the `## 顏色圖例` table at the end of the `.md` (also `metadata.json` `style_legend[]`). 規格書的底色/字色通常帶語意（分組、待確認、已砍、修改標記），判讀時一併參考。**空白儲存格的顏色不標**（純排版色帶，無語意）。
- **`markdown/<stem>_markitdown_raw.md`** — MarkItDown 的未加工輸出，留作比對基準。**一般不要讀它**；只有懷疑重建邏輯出錯時才拿來對照。
- **圖片路徑的兩種基準**（別搞混）：`metadata.json` 的 `image` 欄位是**相對輸出根
  目錄**（`images/xxx.png`）；`.md` 內的 inline 連結多一層 `../`（`../images/xxx.png`），
  因為 `.md` 本身在 `markdown/` 底下。要組絕對路徑時用 metadata 的版本接輸出根。
- **`metadata.json`** — `images[{sheet,cell,merged_range,image,source_in_zip,description}]`, `shapes[{sheet,cell,text}]`, `merges[{sheet,range,header}]`, `style_legend[{id,bg,font,count,sample}]`, `styled_cells[{sheet,cell,style}]`。`merged_range`/`header` carry grouping semantics; `description` is an optional retrieval hint (usually null).

## Critical rules

- **Original image = source of truth. Do NOT OCR.** Send PNGs to vision.
- **Numeric spec (payouts, probabilities, RTP, reel strips) is usually NOT in the xlsx** — specs externalize it to a separate "機率文件" (math doc). If the `.md` says `{}中的數值請見機率文件` or `{??}x`, the numbers live elsewhere; ask for that doc rather than guessing.
- Don't re-flatten the cell lists back into tables — the `[cell]` addresses are the spatial information.
- 回報結果時引用 `validation.txt` 的實際內容，不要只說「轉換完成」。

## Limitations

- 稀疏/密集的分界是非空格密度 0.15（`DENSITY_THRESHOLD`）。分錯邊時（例如一張其實是表格的稀疏 sheet 被做成清單）調這個值。
- 合併補值的膨脹上限 `FULL_FILL_CHAR_CAP = 5000`（span 格數 × 文字長度）。超過改掛回指。
- Google Sheets floating images may be lost on xlsx export — 現在由 validation 的孤兒圖檢查自動報出，不需再人工翻 `xl/media/`。
- Vector shapes: only their text (`<a:t>`) is extracted, not the rendered graphic.
- 顏色解析涵蓋 rgb / indexed / theme（含 tint）三種來源；讀不到 `theme1.xml` 時會在轉換過程印警告，該情況下佈景主題色會被當成無色。
- 公式格取的是 Excel 存檔時寫入的快取值。無快取時回填公式字串並讓 validation 失敗（見 Step 1.5），但工具**不會自行計算公式**——要數值就得讓來源檔帶快取。
- `styled_cells` 逐格明細上限 20000 筆（`STYLE_CELL_DETAIL_CAP`），超出只保留圖例，validation 會標明少收幾筆。
