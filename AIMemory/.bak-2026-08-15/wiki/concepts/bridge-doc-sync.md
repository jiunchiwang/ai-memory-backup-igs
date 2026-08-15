---
title: Bridge 文件同步機制（doc-sync）
type: concept
created: 2026-07-18
updated: 2026-08-08
sources: [f_f2dc75, f_221993, f_5302c0, f_3fb62a, f_faa25e]
---

# Bridge 文件同步機制（doc-sync）

[[bridge-project]] 的 README/使用手冊與程式碼保持一致，靠的是「事實來源改為原始碼」的機械化管線，而非人工比對兩份文件。

## 事實來源改為直接 import

- `doc-facts.ts` 從「regex 撕原始碼」重構為直接 `import` TypeScript 模組（`COMMAND_SPECS`/`DEFAULT_STEPS`/`EVENT_TYPES`），消除「平行實作」的脫鉤風險（2026-07-31，Fable 5 review 建議）
- `event-log.ts` 改寫成 `const array + type 推導`：`EVENT_TYPES` 陣列可在 runtime 枚舉，`EventType` 型別從該陣列推導，而非手寫兩份互相脫鉤的定義

## 計數類機械閘門的設計原則

- `check-doc-sync.mjs` 只把「支數」這類**硬計數**納入機械檢查，耗時類數字只寫進文件並標註量測日期——因為 smoke 耗時 run-to-run 有約 8% 變異（2026-07-31 full tier 實測 260.7s/274.1s/249.9s），若把耗時納入 gate 會變成每次跑都可能紅的雜訊閘
- 期望值必須當場從真實來源算出、絕不可硬寫，否則閘門自己會變成下一個過期來源——閘門本身加入後就會改變它要驗的數字（2026-07-31 加 gate 後 smoke fast 從 92→93、full 95→96，支數改向 `run-smoke-suite.mjs --list` 動態取得）
- 同一組計數若散在多個檔案（曾一度散在 10 個檔案），只改部分會讓 repo 內部互相矛盾、比全錯更難察覺

## 歷史修復

- 2026-07-19：`docs/usage-guide.html` 補上 `/refresh-routing` 指令別名 `/refreshrouting` 說明，修正與 README 常用指令表的落差

## 相關

- [[bridge-project]] — Bridge 本體架構
- [[bridge-smoke-gate]] — smoke 耗時變異與 gate 設計互相參照
