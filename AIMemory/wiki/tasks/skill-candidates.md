# Skill Candidates（未成熟候選追蹤）

## 待觀察

- [ ] **youtube-to-document** | count: 1 | 「YouTube 字幕抓取→HTML 整理→Playwright PDF」完整工具鏈（youtube-transcript-api + HTML+CSS排版 + Playwright headless Chromium 渲染 PDF）。踩坑：fpdf2 Variable Font 寬度 bug、WeasyPrint 需 GTK 放棄、翻譯字幕被 IP 封鎖只能抓原文。代表性 session: 2026-06-03T12-19-39
- [ ] **electron-fork-worker-progress** | count: 1 | Electron/Node 插件中密集計算卡 UI → child_process.fork 到 worker + IPC 回傳進度 + BrowserWindow 顯示進度條。Pattern: main process 只做 fork+監聽，worker 做 CPU 密集，IPC message 格式 {type:"progress",current,total,name}。代表性 session: 2026-06-17T10-50-58
