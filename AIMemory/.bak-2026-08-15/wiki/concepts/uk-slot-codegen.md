---
title: UK Slot Codegen 工具整合
type: concept
created: 2026-07-15
updated: 2026-08-14（wikilint：新增 Clash of Olympus 交付案例——三個可重用技術教訓 + M0b 全綠邊界）
sources: [f_ba8cc5, f_5fa621, f_73183f, f_49dae6, f_4cd205, f_59bf73, f_e2665f, f_81ef45, f_ac9912, f_98e336, f_1b276f, f_6fe390, f_0db6f9, f_1007ff, f_1751fa]
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
- **skill-usage.json 的 use_count 會低估真實使用**：只在 agent 主動輸出 `<<SKILL_USED:...>>` 時累加，因此 `use_count=0` 往往是回報缺口而非真的沒用（uk-slot-codegen 顯示 0 卻是 slot 開發主入口）——修好回報覆蓋率之前不可用 `use_count` 當刪除 skill 的依據

## uk_917 拋棄式驗證結果

- Gate 17/17 通過
- Custom feature 偵測：對照 dev-spec 🔴 清單 0 漏 0 誤報
- spec_adapter.py 3 個實測 bug：Symbol idx 未依 ODDS 表 SymID 排序全錯位、音效表解析失敗、總數少算+HAS_JACKPOT 誤判
- **結論**：codegen 當 M0a~M1 加速器成立，但規格轉換不能無人化，人工檢查點 1 必須保留

## 回饋文件與修正

- 8 項全部修正完畢（commit cee689e）
- [[uk-slot-pitfalls]] 已回灌 5 條 codegen 來源踩坑（條目 5~9）

## Clash of Olympus 交付案例（2026-08-12/13）：三個可重用技術教訓

`uk_slot_clash_of_olympus` 的 codegen 交付（finalize gate 38/38、tsc 0 error）由主 agent 接手修 65 個編譯錯誤時實查出來：

1. **`import protocol from "./Proto"` 的 default import 不能當 namespace 型別用**——寫 `protocol.<ns>.IRoundInfo` 會噴 TS2503（本次一口氣 60 處）。修法是補 `import type { <ns> } from "./Proto"` 只改型別位置；⚠️ **值位置（`new protocol.<ns>.SpinAck()`）必須保留**，Proto.ts 刻意用 default export 保住 CJS runtime object，誤改會編譯過但執行期 undefined——不可全域字串取代，要依 tsc 回報的精確 (line,col) 動刀。
2. **proto stub 的 `.d.ts` 會與 runtime `.js` 失步且失步位置不對稱**：某型別在 `.js` 有 prototype 預設值、`interface` 也有，只有 `class` 缺——若只 grep interface 前幾十行會誤判成「interface 缺」而插錯位置。
3. **mock 的實際形狀才是有效契約，不是 dev-spec proto 映射表的推測形狀**——映射表寫的欄位名／結構與 mock 實際產出可能不一致，照映射表寫 `.d.ts` 會讓 mock 整批型別錯，要以 mock 實際輸出為準。另：`gate_runner` 的 `Mock_symbol_effect_data` 要求物件字面值形式（`AwardDataVec:`），屬性指派（`round.AwardDataVec = [...]`）永遠過不了 gate。

**M0b（Editor/Runtime 驗證）於 2026-08-13 全綠**，但綠燈邊界僅止於「骨架不會斷」不等於「功能會動」——演出類 state 仍可能是空 stub。細節見 [[uk-slot-clash-olympus]]。

## 相關

- [[uk-slot]] — 專案群總覽
- [[uk-slot-pitfalls]] — 踩坑經驗（含 codegen 來源 5 條）
