---
name: ms-kiro-strreplace-silent-fail
description: 當用 Kiro 的 strReplace 或 fs-edit 類工具改檔、tool 回報 Successfully replaced N occurrences 但事後 grep / read 發現磁碟內容沒變、或同一個檔案連續發幾個 strReplace 只有部分生效時使用
---

# Kiro strReplace Silent-Fail 防禦

## 概述

Kiro（以及部分 MCP 或 Claude tool）提供的 `strReplace` 工具**偶發會回報成功但磁碟沒有真的改到**。錯誤率不高（每次可能 <5%），但後果很嚴重：tool 回你 `Successfully replaced 1 occurrence`，你繼續往下寫、build、push，最後才發現檔案根本沒動，PR review 時才爆出來。

這個 skill 給三條防線，讓你不再信任「工具說成功就是成功」。

## 何時使用

- 使用 Kiro、Claude Code、或任何用 `oldStr/newStr` 做字串替換的編輯工具
- 一次要對**同一個檔案**下多個 strReplace
- 改動的是**會被下游立刻讀到**的檔（config、schema、strcit parser 讀的 JSON）
- 改完之後自己**無法肉眼驗證結果**（例如只在某個 runtime 路徑才會觸發）

## 不要用在

- 純 read / list 類工具：沒有寫入，不會踩
- 用 `write.create` 整檔覆寫：不走 strReplace 路徑，沒有這個 bug
- 你已經會馬上 `git diff` 的情境：diff 本身就抓得到

## 三條防線（由輕到重）

### 防線 1：每次 strReplace 後立即驗證

**最低成本、最高 ROI**。改完下一個 tool call 就是驗證，中間不要插別的工作：

```
# 改完 src/foo.ts 的某段
→ grep 'newStr 特徵' src/foo.ts        # 或 read 那幾行
  命中 → OK 往下走
  沒中 → 立刻重試 strReplace 或改用 create 重寫
```

**不要**累積好幾個 strReplace 之後再一次性驗證——那樣出錯時不知道哪個失敗，浪費除錯時間。

### 防線 2：同一檔案多個 strReplace **一律序列化**

不要以為 tool 會幫你排隊。實測 Kiro 偶爾會「報告 5 個都成功，實際只落地 2 個」，特別是在同一 response 裡發多個 tool call 時，彼此會 race。

**正確流程**：

```
1. strReplace A → 等 response → grep 驗證 A
2. strReplace B → 等 response → grep 驗證 B
3. strReplace C → 等 response → grep 驗證 C
```

**錯誤流程（會踩）**：

```
1. 一次性發 strReplace A、B、C 三個 tool call
2. 三個都回 Successfully
3. 實際 A 沒落地、B 落地、C 沒落地
4. build 爆，你以為 B 的邏輯壞掉
```

### 防線 3：改動多或 oldStr 複雜時，改用 `write.create` 整檔覆寫

以下情境**跳過 strReplace**、直接 `create` 重寫整份：

- 要改的地方 > 5 處
- `oldStr` 含多行、含正規字元（`$`、`[`、`.`）、含中文全形
- 檔案本身 < 300 行（整檔覆寫成本很低）
- 前一次對這檔的 strReplace 已經失敗過一次

`write.create` 是寫入整個檔案內容，沒有「找不到 oldStr」的失敗模式，一定落地。缺點是要先 `read` 整檔內容才寫得出來——但這正好也當副作用驗證檔案目前狀態。

## 典型 Silent-Fail 症狀

你會看到：

```
[strReplace] Successfully replaced 1 occurrence in src/memory.ts
```

然後：

```
grep "newKeyword" src/memory.ts → 0 match
read src/memory.ts → 還是舊內容
```

或更隱晦的：

```
1 次 response 裡發 4 個 strReplace 到同一檔
→ 4 個都回 success
→ grep 其中 2 個 newStr 特徵 → 只有 2 個命中
```

這就是 silent-fail。

## 為什麼會 silent-fail（推測）

非官方解釋，但觀察到的規律：

1. **同一 response 多個 tool call 的寫入有 race**——後寫的可能 overwrite 前面的結果，而且兩邊都回 success
2. **`oldStr` 含特殊字元時 matcher 的 escape 有 bug**，匹配不到但回傳「成功」
3. **tool 端的 cache**——某些情境下 strReplace 對 in-memory 的檔案快照生效，但 flush 到磁碟那步失敗

不用太糾結原因。這個 skill 的重點是**外部驗證機制，不信任 tool 回報**。

## 實戰範例

### 範例 1：改 `src/memory.ts` 三處 → 序列化 + 驗證

```
(1) strReplace oldStr="const TAIL = 20" newStr="const TAIL = 30"
    → success
    → grep "TAIL = 30" src/memory.ts  ✓ 1 match

(2) strReplace oldStr="..."             newStr="..."
    → success
    → grep "<新字串特徵>" src/memory.ts  ✗ 0 match
    → 重試 strReplace
    → 還是 0 match
    → 改用 write.strReplace with 更精確 oldStr（多加上下文）
    → ✓ 命中

(3) strReplace ...
    → success → 驗證 ✓
```

### 範例 2：oldStr 複雜 → 直接 create

```
想改 src/config.ts 的 5 個 env 宣告、加註解中文。
oldStr 要含 5 組 `process.env.XXX ?? "..."`，多行、有中文預設值。

→ read src/config.ts 整份
→ 在 response 內自己編輯整份內容
→ write.create 覆寫
→ grep 驗證 5 處特徵字串  ✓ all
```

### 範例 3：事後發現 silent-fail 的修復

```
Build 失敗：error TS2304: Cannot find name 'newFunction'.
我以為上一個 strReplace 把新函式加進去了。

→ grep "newFunction" src/foo.ts → 0 match
→ 證實 silent-fail
→ 追溯：那個 strReplace 跟另外兩個 strReplace 在同一 response 發出
→ 重新發：序列化、一個一個驗證
→ build 通過
→ 記憶更新：「同檔多 strReplace 要序列化，嚴禁 parallel」
```

## Common Mistakes

| 錯誤 | 修正 |
|---|---|
| 連發 5 個 strReplace 都回 success，不驗證直接 build | 每個 strReplace 後立刻 grep / read 驗證 |
| 驗證用 `git diff`（要 stage 才看得到 working tree 改動） | 用 grep 或 read 看磁碟實際內容，不要走 git |
| silent-fail 後重試相同 `oldStr`，以為只是 tool 抽風 | 失敗兩次就換 strategy：換 `oldStr`（加上下文）、或改 create |
| 同時發對同一檔的多個 strReplace | 一律序列化：改完 A 驗 A，才發 B |
| oldStr 含多行或特殊字元時還硬用 strReplace | 整檔小（<300 行）直接 create 重寫 |
| 「Tool 剛才回 success 了我相信它」 | 永遠追一個 external check：grep / read / test run |
| silent-fail 的檔被下游讀（build / runtime / test） → 誤判是邏輯 bug | 先排除 silent-fail 再 debug 邏輯：`git diff src/foo.ts` 比 `oldStr 預期改法` |
| Multi-line `oldStr` 在同一個檔連續失敗 2 次以上（空行 / 空白處也沒錯） | 多半是**行尾字元混雜**（CRLF vs LF）— strReplace 匹配器會把 tool input 的 LF 和磁碟 CRLF 當成不同字串。對策：改用**單行短 anchor**一次只改一行，或寫 Python 腳本 `read_bytes → byte-level replace → write_bytes` 繞過工具層。**不要**把同一批 patch 當成「所有檔行尾一致」處理（實戰看過 `src/index.ts` 是 CRLF 但 `src/observerTransformer.ts` 是 LF 混在同一個 batch） |
| `replaceAll` 同名 pattern 吃掉 helper 自身的 fallback call → 無窮遞迴 | `replaceAll` 不懂 scope，會把 helper 函式內部的同名 call 也替換掉（和 ast-grep 的陷阱同家族，見 `ms-ast-grep-refactor-safety`）。對策：(1) helper 定義時用**臨時字面常數**擋開 replaceAll（例如 `// @@FALLBACK@@ eventManager.Dispatch(...)`）跑完再手改回來；(2) 先跑 `replaceAll`、全部改完再加 helper；(3) 改用 `pattern_rewrite` + `dry_run=true` 先看命中清單 |

## 相關

- **writing-skills** — 寫 skill 時本 skill 是必遵守的工程紀律
- **ms-agent-long-term-memory** — memory-to-skill 流程涉及大量 skill 檔案改動，特別容易踩
