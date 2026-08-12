# Milestones & M2+ 實作指引

Step 5 Report 完成後，讀本文件產出 `<target>/SPEC.md`（milestone 任務清單）。

---

## Milestone 骨架

寫入 `<game>/SPEC.md`，按依賴排序、milestone 內按機制垂直切：

| Milestone | 內容 | 前置 |
|-----------|------|------|
| M0a | 起新專案（codegen Step 0~0.2 已完成） | — |
| M0b | proto 接通，能 spin 出 server 結果 | proto 發佈 |
| M1 | Base game 可玩（轉輪表演、贏分、基本 UI）— codegen Step 1~5 已產骨架 | M0b |
| M2 | 特色機制：每個 🔴 一個任務（來源：`docs/dev-spec.md`） | M1 |
| M3 | Polish（NearMiss、音效、動畫細節） | M2 |
| M4 | 收尾（多語系 sync、全流程 replay、賠付核對） | M3 |

規則：
- 每個任務帶三要素：**規格出處**（spec 章節）、**對應 pattern**（🟡 類）、**可驗證的驗收標準**
- **每個 M2 機制的驗收標準必含該機制 unshow/replay 還原**——不要留到最後一次補
- proto 晚到時 M0a + 🔴 機制設計可先行；再做「自產 proto stub」可連 M0b/M1/M2 client 邏輯一起解鎖

---

## Proto Stub 路徑（proto 未發佈時 · 2026-07-07 uk_917 實證）

proto 未發佈不必卡 M0b——把 `docs/dev-spec.md` 的假設映射表直接編譯成可用套件：

```
1. <game>/proto-stub/<short_name>.proto ← 三區段：
   a. 基礎結構：抄「模板 code 實際消費的形狀」
      （grep -rho "ar2esProto\.[A-Za-z]*" assets/Script | sort -u 盤點，
       再用 awk 從舊 proto d.ts 抽完整 interface 欄位——⚠️ 別用行號節錄，會漏欄位）
   b. 模板殘留相容欄位（demo proto 專屬欄位，保編譯綠，M1 清 code 後刪）
   c. 本作特色欄位：dev-spec §4 假設逐項轉 message（field number 分段：本作 1~39、殘留 40+）
2. pbjs -t static-module -w commonjs + pbts 產生（與正式套件同工藝）
   → local package（node_modules/@local-stub/<game>_proto/，源與 build script 留 proto-stub/）
3. assets/Script/Proto.ts 單一間接點：
   import protocol from "@local-stub/..."; export default protocol;
   全案 import 改接 ./Proto、namespace 全案 sed 一次
4. 驗證：node 一行 encode/decode roundtrip + tsc 錯誤集合對模板 baseline diff（必須零新增）
```

真 proto 到手：只改 Proto.ts import（+ namespace sed 一次），diff 兩份 .proto 即完成
假設核對，然後刪 proto-stub/ 與 @local-stub。
解鎖範圍：M0b 資料流、M1 State 讀欄位、M2 機制 client 邏輯全部提前開工。

---

## M0a 起新專案：兩條等價路徑（二擇一，不要混跑）

codegen Step 0.0 預設走遠端 clone。沒有 GitHub SSH 權限、或想以本地模板為基準時，
改走 `git archive`——兩者結果等價（都不帶模板 history），差別只在來源。

| 路徑 | 指令 | 前提 |
|------|------|------|
| 遠端（codegen 預設） | `git clone --depth=1 <template-repo> <target>` → `rm -rf <target>/.git` | GitHub SSH 權限 |
| 本地 archive | `git -C <模板目錄> archive HEAD \| tar -x -C <新專案目錄>` | 本機已有 uk_slot_template |

archive 路徑接續步驟（clone 路徑的對應步驟列在括號內）：

⚠️ 2026-08-12 更正：這裡原本寫「clone 路徑由 Step 0.1 自動處理」，**對第 1 項是錯的**
——Step 0.1 只同步 extensions，整條 codegen 流程當時沒有任何一步建 repo，
∴ 走預設 clone 路徑的專案結構上必定沒有 git（`uk_slot_clash_of_olympus` 實證）。
現已補上 `_flow.md` **Step 0.2: Git Init**。

```
1. git init → initial commit（全新 history，不帶模板 log）      → clone 路徑：Step 0.2
2. 執行 Tools_SlotSetUP/FirstClone.bat                          → clone 路徑：Step 0.1
   （讀根目錄 gameSetting.json，clone slotExtensions-client 到 extensions/，
    即 Astarte framework，獨立 repo、不進遊戲 repo）
3. npm install                                                  → clone 路徑：Step 3.3.6
4. 改 GameId / ShortGameName / 盤面 / FillStrategy 設定
   → clone 路徑：盤面＝Step 3.1、FillStrategy＝Step 3.5；
     GameId / ShortGameName 在模板 client code grep 不到（0 命中），
     對應步驟未查證，不要假設有人幫你改
```

---

## 下游 skill 交棒表

codegen 跑完 Step 5 之後，各 milestone 該接誰：

| 階段 | skill | 做什麼 |
|------|-------|--------|
| M0a 後進專案 | `uk-conventions` | 把 UK 開發規範寫入專案 CLAUDE.md |
| M0a 後進專案 | `uk-slot-project-docs` | 建 `<game>/AI.md`（全程增量更新） |
| M1~M2 實作 | `uk-slot-state-machine` | 新增/修改 `SetStateMachine()` 狀態 |
| M1~M2 實作 | `uk-slot-extrabet` | ExtraBet 跳窗與 unshow/replay 還原 |
| M1~M2 實作 | `uk-slot-fake-reel-manager` | FakeReelManager 假轉輪帶 |
| M2 對照 | `uk-slot-pattern-library` | 🟡 類機制找已驗證模式卡片 |
| M4 收尾 | `uk-slot-multilang-sync` | xlsx 多國語言灌進 gameStrings.xml |

---

## M2 實作原則

每個 🔴 機制：

1. 讀 `docs/dev-spec.md` 對應區段
2. 讀 `uk-slot-pattern-library` 最接近的模式卡片（如果被分類為 🟡）
3. 新增 State / Manager（參考 pattern 卡片的「State 映射」段）
4. 驗收標準含：功能觸發 + 演出完整 + unshow/replay 還原

---

## 常見錯誤

- ❌ proto 假設寫完不回頭核對 → proto 到手後必須逐項驗證 ⏳ 項目
- ❌ 抄舊 proto 形狀時用行號範圍節錄 d.ts → 會漏欄位；用 awk 抓完整 interface 區塊
- ❌ 模板 demo 驗收拿別款 dev server 驗 → 欄數/形狀不符必炸；改用 ReelDevTool 假盤或 stub ack
- ❌ unshow/replay 還原留到專案尾聲 → 放進每個機制的驗收標準
- ❌ M0a 起專案時 clone 與 archive 兩條路徑混跑 → 二擇一，混用會出現重複 remote/殘留 .git
- ❌ 以為 clone 路徑會自動建 repo → 不會；`_flow.md` Step 0.2 是唯一建 repo 的地方，
  交付前用 `Test-Path <target>/.git` 確認（`_gates.md` §0 已納入）
