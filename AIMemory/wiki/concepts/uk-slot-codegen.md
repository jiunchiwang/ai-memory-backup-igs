---
title: UK Slot Codegen 工具整合
type: concept
created: 2026-07-15
updated: 2026-07-15
sources: [f_154d5e, f_6a5a42, f_157c38, f_158d62, f_159e83, f_160f94, f_162ab6, f_163bc7, f_164cd8, f_191ab2]
---

# UK Slot Codegen 工具整合

同事提供的 uk-slot-codegen skill，定位為 [[uk-slot]] spec-to-impl 流程的 **M0a~M1 加速器**——快速骨架 + Mock demo，正式開發全程仍走 spec-to-impl。

## 定位與分工

| 工具 | 角色 | 特性 |
|------|------|------|
| uk-slot-codegen | M0a~M1 加速器（xlsx→骨架全自動） | 有硬依賴本地/遠端專案路徑 + git clone |
| uk-slot-spec-to-impl | 正式開發全流程（spec→impl） | 結合 pattern-library + checklist gate |
| excel-to-ai-doc | canonical 規格語料 source of truth | 抽圖片、逐格保真、人工檢查點 |
| spec_adapter.py | codegen 內部餵料管 | 用完即棄，不是 source of truth |

**決策**：codegen 保留原樣當「偶爾借用的加速器」，不需整合成獨立 skill——自有 skill 體系已自包含（spec-to-impl + pattern-library + state-machine/extrabet/fake-reel/multilang + excel-to-ai-doc + uk-slot-pitfalls）。

## 已知限制

- **update 模式（anchor merge）對既有手寫專案不可用**——無 anchor 的代碼會被視為 CODEGEN 區覆寫，只有新專案的 `new` 模式有價值
- **按需讀取設計有覆蓋盲區**：慣例覆蓋只寫在 SKILL.md 會被執行時跳過（agent 只讀 _flow.md 該步段落），必須就地寫進對應 Step 段落
- **pattern-library 是純知識庫**（零硬編碼路徑），codegen 則有硬依賴本地專案——兩者設計定位根本不同

## uk_917 拋棄式驗證結果

- Gate 17/17 通過
- Custom feature 偵測：對照 dev-spec 🔴 清單 0 漏 0 誤報
- spec_adapter.py 3 個實測 bug：Symbol idx 未依 ODDS 表 SymID 排序全錯位、音效表解析失敗、總數少算+HAS_JACKPOT 誤判
- **結論**：codegen 當 M0a~M1 加速器成立，但規格轉換不能無人化，人工檢查點 1 必須保留

## 回饋文件與修正

- 8 項全部修正完畢（commit cee689e）
- [[uk-slot-pitfalls]] 已回灌 5 條 codegen 來源踩坑（條目 5~9）

## 相關

- [[uk-slot]] — 專案群總覽
- [[uk-slot-pitfalls]] — 踩坑經驗（含 codegen 來源 5 條）
