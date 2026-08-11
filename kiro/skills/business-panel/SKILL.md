---
name: business-panel
description: 多專家商業策略分析小組（Christensen / Porter / Drucker / Godin / Kim & Mauborgne / Collins / Taleb / Meadows / Doumont），支援 discussion / debate / socratic 三種模式與跨框架綜合。當使用者要求商業策略分析、市場/競爭/商業模式評估、策略計畫審視、風險與創新評估，或直接呼叫 /sc:business-panel 時使用。純技術性程式碼分析不適用。
type: skill
domain: general
created: 2026-08-11
tags: [business, strategy, superclaude]
source: session
---

# business-panel

這個 skill 承載原本常駐在 `~/.claude/CLAUDE.md` 的 SuperClaude 商業分析框架。
2026-08-11 健檢時改為延遲載入：內容一字未刪，只是不再每次對話都佔約 7,100 tokens。

## 觸發條件

- 使用者呼叫 `/sc:business-panel`
- 要求商業策略、市場分析、競爭定位、商業模式、風險評估、創新策略的多角度評估
- 要求以特定商業思想家的框架（五力、藍海、JTBD、反脆弱、系統思考…）分析

## 步驟

被觸發時，依需要讀取以下檔案（都在 `~/.claude/` 底下，內容為完整正本）：

| 檔案 | 內容 |
|------|------|
| `~/.claude/MODE_Business_Panel.md` | 模式架構：三階段方法論（discussion / debate / socratic）、專家選擇演算法、文件類型對應、綜合框架與輸出模板 |
| `~/.claude/BUSINESS_SYMBOLS.md` | 符號系統：策略分析符號、專家語音符號、綜合輸出模板、token 效率壓縮策略 |
| `~/.claude/BUSINESS_PANEL_EXAMPLES.md` | 使用範例：基本/進階用法、專家選擇策略、輸出格式變體、與其他指令整合、品質驗證標準 |

一般流程：

1. 先讀 `MODE_Business_Panel.md` — 判定該用哪個模式、選哪 3–5 位專家
2. 需要輸出格式或符號時再讀 `BUSINESS_SYMBOLS.md`
3. 需要參考既有用法或整合流程時才讀 `BUSINESS_PANEL_EXAMPLES.md`

不需要三個都讀完才開始——按需載入才是這個 skill 存在的理由。

## 邊界

- 純技術性的程式碼/架構分析 → 不用這個 skill
- 單一框架的簡短解釋 → 直接回答即可，不必啟動整個小組

## 備註

三份來源檔案目前仍放在 `~/.claude/`（SuperClaude 框架原始位置），未搬進本 skill 目錄，
避免與 SuperClaude 自身的更新機制衝突。若日後 SuperClaude 更新覆寫那三個檔，本 skill 仍指得到。
