---
title: Bridge Draft 診斷與重播修復
type: concept
created: 2026-08-08
updated: 2026-08-08
sources: [f_487476, f_585d7f, f_867564, f_20c975, f_7c00f6, f_bb1fcf, f_a9f3cf, f_6f02c7, f_306863, f_9d9c71, f_bfaf63, f_66f268, f_e694a0, f_c628c4, f_8899d7, f_2639eb, f_277b97, f_55d273, f_654f09, f_29848b, f_1ea2be, f_b55155, f_6d536c, f_525976, f_0f0140, f_a53534]
---

# Bridge Draft 診斷與重播修復

## 概述

2026-07-31～08-01 期間診斷並修復 telegram-kiro-bridge 的 draft streaming「跑幾個字就消失重頭跑」症狀的完整歷程。此頁記錄根因分析、修復方案、驗證方法，以及過程中累積的可重用診斷方法論。

2026-08-07 的 topic review 從 [[bridge-streaming]] 拆出，因為這批 facts 主題高度集中、數量龐大（26 條），放在 streaming 下會淹沒其他內容。

## 症狀與根因

### 症狀描述

使用者在 Telegram client 看到 draft 訊息「跑幾個字就消失、從頭重打」，約每 20 秒發生一次。

### 已確認的三個獨立成因

| 成因 | 根因機制 | 修復 commit |
|------|----------|-------------|
| **游標殘留** | 生產碼在 draft 尾端帶游標字元（如 `▌`），探針基準臂純 append 沒帶→漏抓 | `b613dba` |
| **Token 縮回式隱藏** | `<<SELF_EVAL:` 半成品先裸漏→完整後 `hideTrailingUnterminatedToken` 收縮，破壞 append-only | `bd068e1` |
| **Keepalive 同內容 × 長間隔** | Telegram client 對「同內容重送 × 間隔 ≥20s」會整段重打；keepalive sentinel 用 `\x00` 強制原樣重送、間隔正好 20s | `ab69bdb` |

另有第四個獨立成因（未處理）：回覆超過 ~3900 字後 `truncateTail` 的滑動視窗會在頭部插 `…` 並整段位移，每個 tick 必定重播。

## 診斷工具與儀器

### TG_DRAFT_DIAG 環境變數

| 等級 | 行為 |
|------|------|
| `0` | 關閉診斷 |
| `1` | 落 `logs/draft-diag.jsonl`（事件序列，不含完整內容） |
| `2` | 額外落 `logs/draft-frames.jsonl`（每幀完整內容，隱私敏感，分檔便於刪除） |

兩檔靠 seq 對齊。

### 時間戳語意差異

診斷 log 的時間戳語意刻意不對稱：
- `status.edit`：記在 await **之前**（動作發出的時刻才是因）
- `draft.send`：記在 await **之後**

∴ 同一個 tick 在 log 裡 `draft.send` 會排在 `status.edit` 之前，看起來像順序反了——判斷順序必須讀碼不能只讀 log 序號。

### 診斷探針

| 探針 | 用途 |
|------|------|
| `probe-draft-clearing.mjs` | 八臂探針：測 editMessageText/sendMessage 是否清 draft、TTL、同內容重送、markdown 各形態 |
| `probe-draft-frame-append.mjs` | 分析 `draft-frames.jsonl` 的 APPEND/DIVERGE 比率，驗證 append-only 不變式 |
| `probe-draft-token-append.mjs` | 逐字元餵渲染管線，確認 token 扣留是否保持 append-only |

探針命名刻意用 `probe-*` 而非 `check-*`，避免被 smoke runner 自動收進 suite（有真實副作用、需人工觀察）。

## 修復架構

### cutPendingTokenTail（扣留式設計）

核心原則：**任何 append-only 的串流通道都不能用「先渲染再收回」的清理器，只能用「還沒確定就先不渲染」的扣留器。**

`cutPendingTokenTail` 扣留尾端「可能長成 token」的片段先不渲染，但只扣 viable prefix（所以散文 `價格 << 100` 不被凍結）。必須擺在 `transform()` **之前**——擺在之後只修得掉第二次收縮，修不掉裸漏那次。

### 結構性不變式（Fable5 覆核抓出）

`cut` 扣住的集合必須是 `hide`（`hideTrailingUnterminatedToken`）會藏的**超集**，否則 hide 的縮回式行為就從缺口漏回來、重播成因復活。

實測反例：
1. `TOKEN_OPENERS` 缺 `<<CONTINUE:`（hide 的 regex 有 `<<(?:RESTART|CONTINUE)(?::|>?$)`）
2. cut 用 `lastIndexOf("<<")` 定錨而 hide 用 regex 全文掃描，payload 內含多個 `<<` 時定錨落錯位置

**可推廣的教訓（2026-08-01，原記在 [[bridge-acp]]，2026-08-21 移來這裡當主場）**：兩份清單分別用**字串陣列**與**regex** 表達同一個集合時，「衍生自同一個 `NAMES` 常數」並不足以保證等價——裸型 token（`RESTART`／`CONTINUE`）是在 regex 那一邊**手寫**的，衍生機制蓋不到它。∴ 判「兩處是否等價」要看**實際枚舉出來的成員**，不是看它們是否共用上游常數。

### 單一權威架構（commit 32f8d0e）

`transform()` 入口對 raw 輸入呼叫一次 `cutPendingTokenTail`，並移除尾端縮回式的 `hideTrailingUnterminatedToken`；draft / edit / final / proxy 四條路對同一段 buffer 產出完全相同的文字。

有界前瞻 `PENDING_SPAN_CAP=1200` 且刻意不做 per-opener 額度（額度不同會打破「更早的 opener span 只會更長 → 超額即可停止掃描」的單調性）。

## 診斷方法論（可重用）

### 探針全負時的處理

1. **重建式探針的盲點**：重建的是「你以為的生產行為」而非實際送出的 payload 形狀，其「已知良好基準臂」最不會被檢查卻最容易與生產分歧
2. **連續 2 輪全負就停止加臂**，改去逐位元組 diff 探針 payload vs 生產 payload，或直接把真實 payload 落檔等症狀自然發生再 diff
3. **懷疑兩個變數的交集**：把已測過的臂按變數排成 2×2 表，通常會發現交集那格從沒被測過

### 低頻觸發的串流 bug

不要等生產樣本，直接**逐字元重現管線**，並用「舊碼對照臂必須紅」證明探針非空洞。

### 同一毫秒多事件

log 裡「同一毫秒出現兩筆不同事件」是「一個觸發源驅動了兩個下游寫入」的線索——第一次判讀時容易把兩者當成同一件事而漏掉真正的兇手。

## 運維狀態

截至 2026-08-02：
- `TG_DRAFT_DIAG=2` 與 `logs/draft-frames.jsonl` 刻意留著，等一次長回覆自然發生驗 truncateTail 那條殘餘成因
- 三個修復 commit（`00149a6` 儀器 / `b613dba` 游標 / `bd068e1` token 扣留）+ 後續 commits 尚未 push，push 前要派 Fable5 獨立覆核
- `src/proxy-finalize.ts` 鏡像路徑同缺陷未修

## 相關

- [[bridge-streaming]] — Draft API 三階段 lifecycle、4096 截斷、rate limit、Rich Messages
- [[verification-diagnosis]] — 實驗設計三原則、交集盲點、探針方法論
- [[adversarial-review]] — Fable5 覆核紀律與實證價值
