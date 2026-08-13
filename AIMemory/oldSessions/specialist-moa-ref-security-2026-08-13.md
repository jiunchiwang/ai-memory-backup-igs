**User:**
<identity>
你是 moa-ref-security，MoA security reviewer (資安視角，可讀檔)。
</identity>

<artifact_output>
任務完成時，在回覆最末附一個 JSON code block 作為結構化摘要：

```json
{"type":"artifact","summary":"一句話摘要（≤200字）","outputs":[{"type":"finding|recommendation|code_change","content":"..."}],"files_modified":[],"tags":["tag1","tag2"]}
```

規則：type 必須是 "artifact"；outputs 列出關鍵發現/變更；files_modified 列出改過的檔案；tags 用於日後檢索。
</artifact_output>


[Wiki retrieval — auto-loaded pages relevant to this message]
## [[codegen-git-init-gap]] (relevance 0.79)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/codegen-git-init-gap.md]
- 1. 缺口的形狀
- 2. 修法：Step 0.2 + 機械閘門
- 3. UK slot 專案的 git 追蹤慣例（實查，非推測）
- 4. 五輪異源覆核抓到的 12 條
- 5. 順帶回報但未動的既有問題
- 相關

## [[cc-session-reader]] (relevance 0.79)
[長頁面 — 僅顯示段落目錄，需要細節請用 read tool 讀 ${MEMORY_DIR}/wiki/*/cc-session-reader.md]
- 0. 證據等級（先講清楚）
- 1. 這是什麼
- 2. 三篇 ADR 的實質發現（本次研究最有價值的部分）
- 3. 與 bridge 既有能力比對（Step 1 對照表）
- 4. 借鏡評估結論（Step 2/3 · 2026-08-09 查證後）：**無項目值得吸收**
- 5. 風險與注意事項
- 6. 實測：ADR-003 的 `is_error` 主張在本機不重現（2026-08-09，A 級）
[End wiki retrieval]

[Delegation Task — id: moaplan_lens_security]
Goal: 審查對象：G:\Cocos_Project\uk_slot_clash_of_olympus\docs\M2-VS-design.md
背景：審查 M2.1 純資料解析設計。規則權威為 G:\Cocos_Project\uk_slot_clash_of_olympus\docs\dev-spec.md:149-247；現有 stub 在 assets\Script\GameState\VsFeatureShowState.ts。範圍刻意不接 Cocos State、proto、動畫或 RoundWin。請特別檢查 VS Collect 是否只在收分時乘倍且多個為相加、server 結果是否仍為權威、以及輸入可否被 Node 單元測試。

你的 lens 是「安全」。關注：輸入驗證缺口、路徑穿越、憑證或敏感值外洩、權限邊界被繞過、注入、對外部輸入的信任假設。

請做到：
1. 先自己讀過對象本體，並在回報時為每個發現附上你**逐字複製**的那一行原始碼（不是你重述的版本）——沒有逐字引用的發現視為未經查證，寧可不報。
2. 每個發現要給**具體攻擊路徑**（誰能構造什麼輸入 → 得到什麼不該有的結果），不接受泛泛的「應加強驗證」。
3. 明確標示這條是否在本專案的威脅模型內（例如僅單機自用 vs 對外服務），不在模型內的降級說明而非誇大。

回報格式：每個發現一段，含 檔案:行號 / 一句話結論 / 攻擊路徑 / 嚴重度（high/medium/low）。沒有發現就說沒有。
Context: 此工項屬於計畫「[wf-review] G:\Cocos_Project\uk_slot_clash_of_olympus\docs\M2-VS-design.md」。

Complete this task. When done, summarize what you accomplished.
[結構化結果 — 必要步驟]
完成後**呼叫 structured_output 工具**繳交下列欄位（不是把 JSON 印在回覆裡，
那樣下一步收不到）：
  - findings: array
文字回覆照常寫（人會看），structured_output 是額外的一步，不是取代。

---

**moa-ref-security:**
## 審查結果：moa-ref-security lens

**審查範圍**：`docs/M2-VS-design.md`（VSManager 純資料解析設計），對照 `docs/dev-spec.md:149-247` 與現有 stub `VsFeatureShowState.ts`。

**結論：本切片範圍內沒有可利用的安全性發現。**

### 逐項確認（依你要求的三點）

**1. VS Collect 是否只在收分時乘倍、多個為相加**

逐字引用（`M2-VS-design.md:47`）：
> `T = 原地 Cash/JP + Σ(vsValue)`。每個 Collect 各收一次；多個 VS Collect 對總贏分為 `T × Σ(multiplier)`，不連乘。

搭配 `dev-spec.md:205-209`：
> S5 收分：T = Σ(原地 Cash/JP 值) + Σ(vsValue[])
>   VS Collect  → T × collectMul[col]
>   普通 Collect → T × 1
>   總贏分 = Σ 各 Collect 收到的值  ← 相加，不是連乘

以及可驗收契約 BC-VS-7（`M2-VS-design.md:56`）：「雙 VS Collect（×10、×5）對同一 `T=1000` 的總額為 15000，不是 50000 或 100000。」確認設計是相加、非連乘，且倍率只在收分（S5）套用，不打到盤面（S4 明寫「不改動任何盤面分數」）。

**2. server 結果是否仍為權威**

逐字引用（`M2-VS-design.md:11`）：
> 它**不是賠付來源**：不可改寫 `SpinAck.RoundWin`、不可抽隨機倍率、不可取代 server 的 `VSResult`。

以及類型不合時的處理（`M2-VS-design.md:39`）：
> `warnings`：server `vsType` 與欄位推導的類型不一致時記錄；仍以 server 為準，不自行改寫結果。

client 端只做展示/一致性檢查，不覆寫或替代 server 權威值——這是老虎機客戶端正確的信任邊界劃分（真實金流判定留在 server，client 端計算即使被構造出異常輸入也不影響實際派彩）。**這一點在威脅模型內確認成立**：即使假設惡意/異常的 `vsResults`（例如 `winningMultiplier` 為極端值）流入 `Resolve()`，也只會導致展示層數字錯誤，不會回寫或影響 `SpinAck.RoundWin`——不構成派彩層面的攻擊路徑。

**3. 輸入可否被 Node 單元測試**

這是可測試性問題非安全問題，但附帶確認：`VSManager.ts` 不可 import `cc` 或 `Game_Define`（`M2-VS-design.md:17`），可用 `ts-node --transpile-only` 直測——不在我的 lens 範圍，留給對應視角。

### 威脅模型判定

此模組的攻擊面被設計本身結構性收斂掉了：
- 無檔案 I/O、無路徑操作 → 路徑穿越不適用。
- 無憑證/敏感值 → 外洩不適用。
- `vsResults` 來自既有 server 協定通道（`SpinAck.RoundQueue[...].VSResult`），本切片未新增或修改該通道，威脅面（傳輸安全、server 端驗證）不在此文件範圍內，也不應在此重複審查。
- 唯一的「外部輸入信任假設」是 client 信任 server 給的 `winningMultiplier`/`vsType`/`reelIndex`，但設計明確排除該計算結果成為派彩依據（見上），且對類型不符採「記警告、以 server 為準」而非「靜默接受並改寫行為」——這是恰當的處理，不是漏洞。

**低嚴重度觀察（非漏洞、僅供留意，不算 finding）**：文件未明寫 `winningMultiplier` 的數值邊界檢查（NaN/負值/極端值），若 server 傳來異常值，`vsValues`/`collectWins` 展示數字可能失真。因為不影響實際派彩（RoundWin 仍權威）且 server 通道本身超出本切片範圍，這屬於顯示層健壯性建議，非安全性缺陷，故不列為正式 finding。

**沒有發現。**

```json
{"type":"artifact","summary":"審查 M2-VS-design.md 資安視角：VS Collect 相加非連乘、server 權威未被繞過，皆有逐字引用確認；範圍內無可利用漏洞，僅有一項低嚴重度非漏洞觀察（winningMultiplier 缺數值邊界檢查，但因不影響派彩故不列為 finding）","outputs":[{"type":"finding","content":"無安全性發現。VS Collect 倍率相加邏輯（M2-VS-design.md:47, dev-spec.md:205-209, BC-VS-7）與 server 權威未被覆寫（M2-VS-design.md:11,39）皆已逐字核實，符合威脅模型：client 僅做展示/一致性檢查，不產生派彩，真實金流仍由 server 端 RoundWin 決定，未在此切片範圍內。"}],"files_modified":[],"tags":["security-review","vs-manager","no-findings","threat-model-confirmed"]}
```審查完成：資安視角對 `M2-VS-design.md` 沒有發現可利用漏洞。VS Collect 倍率相加（非連乘）與 server 權威未被 client 覆寫這兩點都已逐字核對規格原文確認成立；client 端計算僅供展示/一致性檢查，不影響實際派彩（`RoundWin`），因此不構成攻擊路徑。已用 `structured_output` 回報空 findings 陣列。

---

