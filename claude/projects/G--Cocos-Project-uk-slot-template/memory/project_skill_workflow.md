---
name: project-skill-workflow
description: Skill 檔案的雙軌維護方式 — .kiro/skills/ 是 source of truth，根目錄 .skill zip 是發佈用打包。
metadata: 
  node_type: memory
  type: project
  originSessionId: ebce2f83-747e-4bca-8821-5e3802f903dc
---

本專案有 Agent Skill 檔案（uk-slot-state-machine、reel-fill-strategy）。檔案有兩種存在形式：

1. `.kiro/skills/<name>/` — 解壓後的資料夾，是**真正的 source of truth**，含 SKILL.md、references/、assets/ 等子目錄，git 追蹤。
2. 專案根目錄 `<name>.skill` — zip 封裝，是「發佈成品」，供其他開發者載入或從外部安裝 skill 用。

**Why**：解壓版好維護（git diff 看得到變動），但實際分發 skill 給其他人時用 zip 比較方便。所以兩者都保留，但 `.kiro/` 那份才是要編輯的。

**How to apply**：
- 編輯 skill 內容請動 `.kiro/skills/<name>/` 底下的檔案
- 編完後重新打包成 root 的 `.skill`（PowerShell 用 `Compress-Archive -Path .kiro/skills/<name>/ -DestinationPath <name>.zip` 後改副檔名 `.skill`；bash 沒 `zip` 指令）
- **不要直接編輯根目錄的 .skill zip**
- 舊版本 `slot-state-machine.skill` 已被 `uk-slot-state-machine.skill` 取代並刪除，不要再參考前者

目前已建立的 skill：
- `uk-slot-state-machine` — 遊戲狀態機設定（含 21 個 state .ts 模板，含 ExplodeState / MatchingPatchUpState）
- `reel-fill-strategy` — Cascade/Tumble 補位策略 + DropEntry 進場策略
