---
name: uk-slot-no-framework-edits
description: UK 老虎機專案禁止改動公版 framework 程式（extensions/astarte-framework）
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b9f4f77a-021b-4d10-9299-af73c1ac3e37
---

UK 老虎機專案**禁止改動公版 framework 程式**——`extensions/astarte-framework/**`（含 `assets/Component/*.ts` 如 ExtraBetComponent、`utilis/*.ts` 等）。需求要靠專案層（`assets/Script/**`）達成。

**Why:** framework 是跨 10+ 專案共用的公版，且 `extensions/` 被 `.gitignore`、不進專案 git。改公版會 ① review/git 看不到 ② 下次同步 framework 被蓋掉 ③ 影響其他專案。實例：2026-06-18 發現 ExtraBetComponent.ts 被誤加 two-step guard，已還原並記錄於 `.claudedocs/ExtraBet-公版誤改還原記錄.md`。

**How to apply:** 修改前先確認目標路徑——落在 `extensions/astarte-framework/` 就停手，改從專案層解。若某邏輯**真的搬不回專案層**（如 framework 私有方法內部行為），不要硬改公版，而是回報 astarte-framework 維護者進公版、或本地暫時 patch 並明確記錄待上游。判定 framework vs 專案版本差異時，可比對磁碟上其他 UK 專案（`G:\Cocos_Project\*\extensions\astarte-framework\`）多數一致者即公版基準。
