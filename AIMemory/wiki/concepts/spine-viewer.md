---
type: concept
title: Spine Viewer 插件
created: 2026-06-23
updated: 2026-06-23
sources: [f_02cb06, f_f944d1, f_bf6094, f_28e62a, f_4b8ff5, f_c01dbd, f_e61df4]
---

# Spine Viewer 插件

Cocos Creator ≥3.6.2 的編輯器擴充，用於批次掃描專案中所有 Spine 動畫資源並產出效能報告（DrawCall、Triangle 數）。

## 基本資訊

- 安裝位置：`~/.CocosCreator/extensions/spine-viewer`
- 打包方式：`pack.bat` → `spine-viewer-release.zip`（含 dist + static + node_modules + package.json）
- 使用者解壓到 `~/.CocosCreator/extensions/` 即可啟用

## 核心架構

### Batch Scan

使用 `child_process.fork` 獨立進程執行批次掃描，不阻塞 Cocos 編輯器主進程。

### DrawCall 計算

採 CPU 模擬 PolygonBatcher 合批規則：
- 以 **texture identity + blend mode** 作為斷批判斷
- 不需要 WebGL context，純 CPU 計算

### Triangle 計算

採全 keyframe 掃描策略：
- 從 animation timelines 抽取所有 frame time
- 取各 frame 的 triangle 數最大值作為該動畫的代表值

## 注意事項

- [[uk-slot]] 專案的 Spine 資源量大，batch scan 是效能優化的關鍵工具
- `spine-webgl` 的 TextureAtlas texture factory callback **每次呼叫必須回傳獨立物件**（含 `getImage` 方法），否則 DC 比對會失效
- Cocos Creator 3.6 的 `Editor.Message.send` 只路由到 `main.ts` methods，不直接送到 panel；跨進程通訊用 Electron BrowserWindow + IPC

## 產出格式

參考 Excel 格式為 5 欄：

| 欄位 | 說明 |
|------|------|
| Spine 檔名 | `.skel` 或 `.json` 路徑 |
| Skin | 使用的皮膚名 |
| Animation | 動畫名稱 |
| Triangle 數（最大） | 全 keyframe 掃描的峰值 |
| DrawCall | 模擬合批後的 DC 數 |
