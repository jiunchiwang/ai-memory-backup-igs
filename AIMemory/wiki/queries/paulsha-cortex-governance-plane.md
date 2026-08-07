---
title: 外部 repo paulsha-cortex 研究：agent 治理平面三件套（persona 契約/coordinator 派工/control 檔案契約）、foreign review 的 independence_domain 設計、verification contract 的 must_change 產出物驗證，以及對照 bridge 既有系統的借鏡排序
type: query
created: 2026-08-07
updated: 2026-08-07
sources:
  - https://github.com/hamanpaul/paulsha-cortex
  - https://raw.githubusercontent.com/hamanpaul/paulsha-cortex/main/README.md
  - https://raw.githubusercontent.com/hamanpaul/paulsha-cortex/main/docs/onboarding/concepts.md
---

# paulsha-cortex 研究（外部 repo 吸收評估）

2026-08-07 依 `ms-external-repo-absorption` 流程研究 `hamanpaul/paulsha-cortex`，
走到 Step 2（現狀盤點 → 對照表 → 借鏡排序）為止，**未進入實作**，吸收範圍待使用者裁決。

相關頁面：[[adversarial-review]]（異源覆核紀律，本頁最大借鏡點的對照基準）、
[[verification-diagnosis]]（恆真斷言／綠燈假象，`must_change` 對應的既有問題）、
[[bridge-specialist]]（specialist 角色宣告 vs 執行實體）、
[[bridge-smoke-gate]]（既有 gate 三層）、
[[bridge-research]]（外部框架借鏡的總索引）。

## 1. 這是什麼

Agent **治理控制平面**（governance control plane），Python 3.10+，唯一執行期依賴 PyYAML。
屬 `paulsha-*` 系列中間層：

```
主產品 repo（產品行為）
   └─ paulsha-cortex（治理平面：CLI + persona guardrail + manager runtime + 檔案契約）
        └─ paulsha-hippo（共用底層，cortex 刻意切斷執行期依賴）
```

核心主張是「唯一權威」：cortex 是 work / WorkflowRun / Job / Slice 生命週期的唯一 writer，
`domain tools 只回傳 artifacts，不得改寫 lifecycle truth`。所有變更
（fanout / tick / complete / slice-action / work）走 control request queue；
daemon 未啟動時 CLI **明確拒絕**，而不是自己競寫 registry。

支援 executor：copilot / claude / codex（headless CLI）。

### 成熟度判定（重要）

10 stars、3 forks、26 open issues、617 commits、`VERSION` 仍為 `0.0.0`（bootstrap）、
README 40KB 但使用者個位數、README 自列多項 "Not yet implemented"
（operator bootstrap、model pin、monitor init、instance/path isolation、state migration，追在 issue #12）。

∴ **當設計概念來源，不當可依賴的套件。**

## 2. 治理三件套

| 件 | 內容 |
|---|---|
| **Persona 契約** | persona 是「角色檔 + scope 主體」的**資料**，不是在跑的 agent session。原文：`真正執行的是 AgentInstance，真正做安全判斷的是 guardrail / policy engine，它們只讀 persona 契約做 enforcement`。由 `personas.yaml` 的 `enforcement` 欄位驅動，配獨立 CI（`.github/workflows/persona-scope.yml`）+ coordinator 內 fail-closed 的 `persona-scope` gate。切 `enforce` 前先對已 merge 的 PR 做 backtest 確認零誤報。 |
| **Coordinator 派工** | 四層 `spec → job → slice → work`。Slice 狀態 `pending / building / reviewing / verified / completed / needs_human / failed`；work 狀態 `topic → todo → on-going → done`。明確聲明 **job 結束 ≠ 交付完成**。 |
| **Control 檔案契約** | merge-authorized record、CompletionRecord、delivery attestation 皆用 atomic no-clobber + fsync；完成順序原子化：先寫 CompletionRecord 再標 slice completed。 |

## 3. Foreign review（外部覆核）設計

跟既有異源覆核紀律最貼的一塊：

- 覆核者從 `model-identities.yaml` 選，必須「明示 `capabilities: [review]` 且與 Builder 不同
  independence domain」
- 每個 identity 帶 `independence_domain` 欄位（如 `google` / `codex-builder-domain` /
  `claude-reviewer-domain`）；v1 舊 identity 未宣告 `capabilities` 的**不得**當 reviewer
- Claude reviewer 跑拋棄式沙箱：只開 OS-sandboxed Bash、強制結構化 JSON、
  **不給 Candidate 的 `CLAUDE.md` / MCP / remote**；檔案系統預設拒 home、`/run/user`、
  Docker socket；Linux/WSL 需 `bubblewrap` + `socat` + 官方 sandbox runtime（`srt`）
- Manager 只注入 Candidate + job ID；agent 拿不到報告、也沒有 Candidate 寫入權
- `Copilot finding 只允許兩輪 bounded fix/re-review`，超預算轉 operator recovery
- v1 自動 foreign review 只支援 `tier: shareable`，非 shareable **fail-closed 到 `needs_human`**

## 4. Verification contract

宣告式 YAML，重點在「產出物必須有變」：

```yaml
verification:
  docs_class: code
  required_artifacts:
    - path: reports/policy.json
      must_change: true            # 不只要存在，還必須有變動
  checks:
    - kind: persona-scope
    - kind: command
      name: policy
      argv: [python3, -m, pytest, -q, tests/policy.py]   # typed argv, shell=False
  full_suite:
    argv: [python3, -m, pytest, -q]
    timeout_seconds: 60
    baseline: no-regression
```

其他約束：`verify` / `review` 跑在 remote-free 拋棄式 clone 的**確切 Candidate** 上；
sanitized env **不等於** network / filesystem sandbox（README 自己標明）。

## 5. 對照 bridge 既有系統

| 設計 | cortex 做法 | bridge 既有 | 判定 |
|---|---|---|---|
| 覆核者異源 | `ModelIdentity.independence_domain` 為**必填**欄位；`select_secondary_planner` 跳過同 domain 候選（✅ 逐字驗證原始碼） | `src/moa.ts` `DEFAULT_CONFIG` 已宣告 reference pairs（`moa-ref-claude`+`moa-ref-kiro`／`+moa-ref-adversary`），檔頭註解自稱 `blind independence by construction`——但**無 domain 欄位、無 builder≠reviewer 檢查**，異源是 hardcode 的巧合 | **部分已有**，缺口見 §6 |
| 產出物驗證 | `required_artifacts` + `must_change: true` | BC-x 斷言 + smoke tier；恆真靠人抓（`ms-vacuous-test-gate`） | **借鏡（高）** |
| 覆核者隔離 | 拋棄式 clone、剝掉 CLAUDE.md/MCP、拒 home | Codex `-s read-only` / 餵 diff 檔（read-only 連 git 都被政策擋，2026-08-06 實測） | **借鏡（中，概念）** |
| 品質不足處置 | fail-closed → `needs_human` | SELF_EVAL 低分僅顯示旗標、**不擋** | 對照思考，非照搬 |
| 單一 writer | daemon 唯一 writer，未啟動即拒絕 | bridge 單進程，sessionStore/goalStore 直寫 | 不需要 |
| 角色宣告 vs 執行實體 | `personas.yaml`（資料）↔ AgentInstance（執行） | `specialist-domains.json` ↔ spawn 的 instance | **已有** |
| 派工引擎 / systemd / PR 級生命週期 | coordinator daemon + control queue | — | **不需要**（cortex 面向多 PR 平行工程流水線；bridge 是單使用者對話式） |
| merge-commit-only、CompletionRecord | 契約檔 + 原子寫 | pre-push gate + git 紀律 | 已有 |
| bubblewrap / socat 沙箱 | Linux/WSL | 本機是 Windows | 不適用 |

## 6. 借鏡排序（Step 2 產出，未實作）

**① `independence_domain` 欄位化（2026-08-07 深挖，範圍已收斂）**

cortex 側逐字驗證的實作（`paulsha_cortex/coordinator/model_identities.py`）：

```python
@dataclass(frozen=True)
class ModelIdentity:
    executor: str
    model_id: str
    independence_domain: str          # 必填，無預設
    capabilities: tuple[str, ...] = ()
    live_probe: str | None = None
```

`select_secondary_planner()` 內 `if identity.independence_domain == primary_identity.independence_domain: continue`。
`review.py` 的 `select_foreign_reviewer()` 同構，同 domain 回 `{"state": "absent", "reason": "same-independence-domain"}`，
非 shareable tier 回 `{"state": "needs_human", "reason": "non-shareable-tier"}`（B 級證據，見 §7）。

bridge 側**已有一半**：`src/moa.ts` 的 preset 已用資料宣告 reference pairs。
**真正缺口只剩三件**：

1. identity 上沒有 domain 欄位——`moa-ref-claude` + `moa-ref-kiro` 之所以異源是寫死的巧合，不是可檢查的宣告
2. 沒有任何機械檢查驗 builder ≠ reviewer
3. push 前覆核（Fable5 / Codex）完全在 MoA 之外，而那正是 ① 最該落的位置

⚠️ 邊界（不可漂移）：借的是「**宣告誰跟誰算異源**」，**不是**「自動攔停」。
cortex 的 foreign review 是 fail-closed 閘門；2026-08-06 已明確立下
「不要把覆核自動化成無條件停止閘門」（寫進 `ms-cross-model-adversarial-review` 正本）。
資料層宣告要，閘門層強制不要。

附帶候選（不在本輪 scope）：`live_probe` 欄位對到 `acp-model-report-shapes` 的
「adapter 回報 model 是回音非驗證、pin 被拒會靜默降級」——cortex 用一個欄位聲明「怎麼實測這個 identity 活著」。

**② `must_change: true` 產出物契約（成本最低）**
既有 gate 驗「檢查有沒有過」，cortex 多驗「產出物有沒有真的變」。
這是對恆真斷言的**結構性**防禦，比每次靠人做 mutation test 便宜。

**③ 覆核者剝奪 CLAUDE.md / MCP**
目前派 Codex 覆核時，它帶著自己的 `~/.codex/AGENTS.md` 全域指令跑。
cortex 明確剝掉 Candidate 的 agent 指令檔——理由是覆核者不該讀被覆核者寫給 agent 的話。
這一條目前沒有對應機制。

## 7. 證據分級

| 主張 | 級別 | 來源 |
|---|---|---|
| `ModelIdentity` 五個欄位、`independence_domain` 必填、`select_secondary_planner` 跳過同 domain | 🟢 A | `paulsha_cortex/coordinator/model_identities.py` raw 原始碼 |
| 套件真實存在、entry point `cortex = "paulsha_cortex.cli:main"`、僅依賴 `PyYAML>=6` | 🟢 A | `pyproject.toml` raw |
| `paulsha_cortex/coordinator/` 30 個模組（含 `model_identities.py` / `review.py` / `verification.py`） | 🟢 A | 子目錄 tree API（小 JSON，未截斷） |
| `select_foreign_reviewer()` 的 `same-independence-domain` → `absent`、`non-shareable-tier` → `needs_human` | 🟡 B | review.py 摘要（該次摘要**自相矛盾**：先說「不含 reviewer selection」又引用了該函式；引用行本身可信度中等） |
| `must_change`、兩輪 bounded fix/re-review、`tier: shareable`、bubblewrap/socat、persona backtest | 🟡 B | 40KB README 的小模型摘要，未逐字驗證 |

### 本輪新增的方法論教訓

**GitHub tree API 的 `?recursive=1` 回應被截斷時，小模型會對「存在性」問題自信地答 `no`。**
本輪它連答「無 `pyproject.toml`／無 `paulsha_cortex/`／無 `tests/`」，一度推論出
「這個 repo 只有文件沒有程式碼」——足以推翻整份評估。
翻案手法：**直接打 raw URL 當二元探針**（存在 → 回檔案內容；不存在 → `404: Not Found`），
這個訊號不經摘要判斷，抗幻覺。子目錄用 `git/trees/main:<path>`（不遞迴、JSON 夠小）也可靠。

∴ 對「某某東西不存在」這類否定式結論，永遠要用探針覆核，不能採信摘要。
（延伸 `research-report-citations-unverified` 的既有教訓：引用越像真的越要先查；
本輪補的是**否定式**主張同樣要查。）

## 8. 狀態

- Step 0–2 完成（2026-08-07）
- Step 3–5 完成：使用者選**方案 A（只改 skill 正本）**，已實作並 push
  （AI-canonical `64b4b4e`，`ms-cross-model-adversarial-review/SKILL.md` +55 行）
- 落地內容：〈異源域〉一節（domain 對照表 + 降級階梯）+ Common Mistakes 一列
- **副產物發現**：`vc-kiro-delegate` 走 `kiro-cli --model claude-opus-4.5`，
  ∴「Claude 寫、Kiro 覆核」在模型層同源，只有 harness/context 異源 → 歸類為**弱異源**。
  宣告這個動作本身逼出了這個原本沒被問過的問題，這正是 cortex 那個必填欄位的價值
- ② `must_change` 產出物契約、③ 剝奪覆核者的 CLAUDE.md/MCP：未展開
- 方案 B（`specialist-domains.json` / `moa.ts` 資料宣告）、C（smoke 機械檢查）：未動
- 未進行任何 bridge 端程式碼修改；本次方法論修改**未經異源覆核即 push**（使用者裁決，已記在 commit message）
