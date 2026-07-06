# uk-slot-project-docs

當進入 uk_slot_* 系列專案（Cocos Creator 老虎機）讀取或修改檔案時，
遵循以下文件維護規則，確保 AI agent 每次進入都能快速定位。

## 觸發條件

讀取或修改 uk_slot_*、uk_7xx_*、uk_8xx_* 等 UK 老虎機專案底下的檔案時適用。

## 文件結構

每個 UK slot 專案維護兩層文件：

```
專案根/
├── AI.md              ← 索引層（≤2000字），必讀
└── docs/
    └── modules.md     ← 模組詳細文件，改到相關模組時讀取對應段落
```

## AI.md 內容規範（索引層）

- 專案 meta：GameId、ShortGameName、框架版本、proto 來源
- 盤面佈局：幾列幾行、特殊配置
- 模組地圖：每個模組一句話 summary
- 遊戲模式、Symbol 列表
- 不可動的部分（Astarte Framework、extensions、proto）
- 踩坑紀錄
- 驗證指令
- 深入指引：`改到特定模組時，讀 docs/modules.md#<anchor>`

## docs/modules.md 內容規範（詳細層）

每個模組用 `## ModuleName` 分段，內含：

1. **進入點**：主要 class / 檔案路徑
2. **事件介面**：該模組 emit 和 on 的事件名
3. **依賴關係**：依賴誰（import）/ 被誰依賴（grep 結果）
4. **資料流**：server proto 欄位 → 經過誰 → 最終影響什麼
5. **注意事項**：改這個模組時特別要注意的

## 更新時機

| 情境 | AI.md | modules.md |
|------|-------|-----------|
| 踩坑修復 | ✅ 加踩坑紀錄 | ✅ 更新相關模組段落 |
| 結構性改動（新增/刪除模組） | ✅ 更新模組地圖 | ✅ 新增/刪除段落 |
| 改完某模組的 bug | ❌ | ✅ 更新該段落（如果有新發現）|
| 只讀沒改 | ❌ | ❌ |

## 首次進入新專案

- 若無 AI.md → 研究專案後建立（不限改動檔案數）
- 若有 AI.md 但無 modules.md → 改到第二個模組時建立
- 若兩者都有 → 直接使用，改動時增量更新
