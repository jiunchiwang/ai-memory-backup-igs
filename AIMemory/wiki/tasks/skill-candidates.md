# Skill Candidates（未成熟候選追蹤）

## 待觀察

- [ ] **youtube-to-document** | count: 1 | 「YouTube 字幕抓取→HTML 整理→Playwright PDF」完整工具鏈（youtube-transcript-api + HTML+CSS排版 + Playwright headless Chromium 渲染 PDF）。踩坑：fpdf2 Variable Font 寬度 bug、WeasyPrint 需 GTK 放棄、翻譯字幕被 IP 封鎖只能抓原文。代表性 session: 2026-06-03T12-19-39
- [ ] **electron-fork-worker-progress** | count: 1 | Electron/Node 插件中密集計算卡 UI → child_process.fork 到 worker + IPC 回傳進度 + BrowserWindow 顯示進度條。Pattern: main process 只做 fork+監聽，worker 做 CPU 密集，IPC message 格式 {type:"progress",current,total,name}。代表性 session: 2026-06-17T10-50-58

- [ ] **telegram-inline-keyboard-parse-mode** | count: 1 | Telegram inline keyboard callback 搭配動態內容（含 `*_<>|${}` 字元的 desc/usage）用 MarkdownV1 parse_mode 會導致 API 400 靜默失敗、按鈕無回應。修法：改用 HTML + escHtml()。決策表：純靜態文字可用 Markdown、動態拼接一律 HTML。代表性 session: 2026-06-23T22-08-27