---
name: excel-to-ai-doc
description: Convert image-heavy Excel game spec spreadsheets (.xlsx) into an AI-readable knowledge structure — Markdown text + extracted original images (anchored to their source cells) + metadata.json. Use when the user wants to turn a 規格書/spec/design xlsx into something an AI or agent can read, asks to "convert this spec to markdown", "make this xlsx AI-readable", "extract images and tables from this spreadsheet for analysis", or needs to feed a slot/game spec workbook to a vision model. Triggers on game design specs, paytables, UI/flow screenshots embedded in .xlsx. NOT for clean tabular data exports (use a plain csv/markdown converter) or non-xlsx files.
---

# excel-to-ai-doc

## Overview

Converts a spec `.xlsx` (multi-sheet, merged cells, lots of embedded screenshots/flow diagrams) into:
`markdown/` (text + tables, with sparse "document" sheets rebuilt as `[cell]`-tagged lists) + `images/` (original PNGs, named `<sheet>_<cell>_<orig>.png`) + `metadata.json` (image/shape/merge maps) + `source/` (xlsx backup). The **original images are the source of truth** — this tool does NOT OCR them.

## Prerequisites

Needs Python 3.10+ and two packages. Run once per machine:

```bash
pip install -r scripts/requirements.txt   # markitdown[xlsx], openpyxl
```

## Step 1 — Convert

Run the bundled script (it lives in this skill's `scripts/` directory — use the path where this skill is installed, e.g. `~/.claude/skills/excel-to-ai-doc`, `~/.kiro/skills/excel-to-ai-doc`, or `$HOME/.agents/skills/excel-to-ai-doc`):

```bash
python <this-skill-dir>/scripts/convert.py "<path/to/spec.xlsx>" [output-dir]
# output-dir defaults to ./output/<xlsx-stem>/ relative to Python cwd
```

**⚠️ 建議明確指定 output-dir**：預設的 `./output/` 是相對於 agent 當前工作目錄，不是 xlsx 所在位置。不指定時產出可能跑到非預期的地方。

**⚠️ Windows 注意**：腳本的 `print()` 進度訊息在 Windows cmd/PowerShell 下可能因 cp950 編碼問題不顯示（但轉換仍正常執行）。如需看進度，可設環境變數：`set PYTHONUTF8=1`。

**⏱ 大檔案（>10MB / 含大量嵌入圖）可能需要 10-30 秒**，期間無輸出不代表失敗。

Re-running is safe: it skips copy-to-self and clears `images/` first, so no stale files. No need to delete the old output.

## Step 2 — Consume the output (read this before answering spec questions)

The whole point is selective, anchored retrieval — do NOT dump every image into context.

1. **Read `markdown/<stem>.md` first** to locate the relevant area by text.
2. **Match a `[cell]` tag** (e.g. `[B124]`) in the `.md` → look it up in `metadata.json` `images[]` → get the original PNG path.
3. **Send the ORIGINAL PNG to a vision model** (Claude / GPT / Gemini). Never substitute OCR — these are flow charts, state diagrams, annotated UI screenshots whose meaning is visual.

### How to read each part of the output

- **`### 本工作表圖片`** in the `.md` — `[cell]` → image. The join key into `metadata.json`.
- **`### 本工作表標註（圖形文字）`** — callout text overlaid on screenshots (e.g. COLLECT step sequence), extracted from vector shapes. Gives the "which step is this screenshot showing" context. Also in metadata `shapes[]`.
- **Cell lists** (`- **[B13:C19]** 基本規格說明`) — sparse "document" sheets are rendered as cell-addressed lists, not tables. A `range` address (e.g. `[B13:C19]`) means a merged block; the rows it spans that follow it belong under it. Zero `NaN` noise by design.
- **`metadata.json`** — `images[{sheet,cell,merged_range,image,description}]`, `shapes[{sheet,cell,text}]`, `merges[{sheet,range,header}]`. `merged_range`/`header` carry grouping semantics; `description` is an optional retrieval hint (usually null).

## Critical rules

- **Original image = source of truth. Do NOT OCR.** Send PNGs to vision.
- **Numeric spec (payouts, probabilities, RTP, reel strips) is usually NOT in the xlsx** — specs externalize it to a separate "機率文件" (math doc). If the `.md` says `{}中的數值請見機率文件` or `{??}x`, the numbers live elsewhere; ask for that doc rather than guessing.
- Don't re-flatten the cell lists back into tables — the `[cell]` addresses are the spatial information.

## Limitations

- MarkItDown distorts merged cells in genuinely dense tables (NaN). Sparse sheets are already rebuilt as cell lists; a real dense paytable (density ≥ 15%) keeps MarkItDown's table form — tune the threshold in `build_sheet_cell_lists()` if needed.
- Google Sheets floating images may be lost on xlsx export — verify `xl/media/` contains them.
- Vector shapes: only their text (`<a:t>`) is extracted, not the rendered graphic.
