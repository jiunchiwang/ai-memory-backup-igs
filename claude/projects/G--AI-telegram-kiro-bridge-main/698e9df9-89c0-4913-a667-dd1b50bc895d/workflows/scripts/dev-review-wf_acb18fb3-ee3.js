export const meta = {
  name: 'dev-review',
  description: '品質+安全審查 workflow（取代閉環 Phase 3）：parallel 多視角審查（correctness/security/repro lens）→ 對抗驗證 findings。異源 skeptic 打破同源自審天花板（#007）。',
  phases: [
    { title: 'Review' },
    { title: 'Verify' },
    { title: 'Synthesize' },
  ],
}

// args: 審查目標（檔案清單 / 變更描述 / undefined=審查未 commit 變更）
const TARGET = typeof args === 'string' && args.trim()
  ? args.trim()
  : (Array.isArray(args) ? args.join(' ') : '未 commit 變更（用 git diff / git status 找出範圍）')

const FINDING_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['lens', 'findings'],
  properties: {
    lens: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['severity', 'where', 'problem', 'fix'],
        properties: {
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          where: { type: 'string', description: '檔:行' },
          problem: { type: 'string' },
          fix: { type: 'string' },
        },
      },
    },
  },
}

// ============================================================
phase('Review')

const lenses = [
  {
    key: 'correctness',
    prompt: `你是 correctness 審查者。審查目標：${TARGET}。
重點：邏輯錯誤 / 邊界條件 / 因果鏈漏接（改了 X 但連動的 Y 沒改——grep 呼叫者窮舉驗證）/ 設計-實作一致性。
對每個「改了某處」的判斷，用 grep 驗證呼叫者，呼叫者=0 的修改要警示。`,
  },
  {
    key: 'security',
    prompt: `你是 security 審查者。審查目標：${TARGET}。
5 面向：輸入驗證 / 注入（SQL/cmd/path）/ 認證授權 / 敏感資料暴露 / 依賴風險。給攻擊向量，不只列規則。
無安全面向（純算法/UI 無外部輸入）則回報「無安全相關 finding」。`,
  },
  {
    key: 'repro-quality',
    prompt: `你是可重現性+質量審查者。審查目標：${TARGET}。
重點：是否可被測試覆蓋（BC-x 有無對應測試）/ 過度設計（YAGNI 違反）/ 你的改動造成的 dead code（orphan imports/函式）/ 既有 dead code（提及不動）。`,
  },
]

const reviews = (await parallel(lenses.map(l => () =>
  agent(l.prompt, { label: `review:${l.key}`, phase: 'Review', schema: FINDING_SCHEMA })
))).filter(Boolean)

// 攤平所有 high/medium findings 去重後對抗驗證
const allFindings = reviews.flatMap(r => (r.findings || []).map(f => ({ ...f, lens: r.lens })))
const toVerify = allFindings.filter(f => f.severity === 'high' || f.severity === 'medium')

// ============================================================
phase('Verify')

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['isReal', 'confidence', 'reasoning'],
  properties: {
    isReal: { type: 'boolean', description: '這個 finding 是真問題還是誤報' },
    confidence: { type: 'number' },
    reasoning: { type: 'string' },
  },
}

// 每個 high/medium finding 派獨立 skeptic 嘗試「反駁這是真問題」（異源驗證，打破同源天花板）
const verified = (await parallel(toVerify.map((f, i) => () =>
  agent(
    `你是獨立驗證者（與發現此問題的 reviewer 不同 context）。盡力反駁以下 finding 是真問題——它可能是誤報。
若你能證明它不是問題（誤讀程式碼 / 已被別處處理 / 不在執行路徑），判 isReal=false。若反駁失敗，判 isReal=true。
Finding：${JSON.stringify(f)}
審查目標：${TARGET}
用 Read/Grep 實際查證程式碼，不要憑空判斷。`,
    { label: `verify:${f.lens}-${i}`, phase: 'Verify', schema: VERDICT_SCHEMA }
  ).then(v => ({ finding: f, verdict: v }))
))).filter(Boolean)

const confirmed = verified.filter(v => v.verdict?.isReal)
const dismissed = verified.filter(v => v.verdict && !v.verdict.isReal)

// ============================================================
phase('Synthesize')

const report = await agent(
  `你是審查彙整者。產出審查報告（繁中）。
確認為真的 findings（已通過獨立 skeptic 驗證）：${JSON.stringify(confirmed)}
被駁回的誤報（記錄但不要求修）：${JSON.stringify(dismissed)}
低嚴重度 findings（未經對抗驗證，摘要即可）：${JSON.stringify(allFindings.filter(f => f.severity === 'low'))}

彙整：(1) high findings 清單（R-x 編號，severity high→必修）(2) medium（建議/用戶決策）(3) low 摘要 (4) 誤報記錄 (5) 整體 verdict（pass / fix-required / needs-attention）。
誠實，不放大也不縮小。寫入 .claude-loop/artifacts/P3-review.md 並回報摘要。`,
  { label: 'review-synthesis', phase: 'Synthesize' }
)

return { report, confirmed: confirmed.length, dismissed: dismissed.length }
