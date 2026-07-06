export const meta = {
  name: 'dev-design',
  description: '架構設計 workflow（取代閉環 Phase 1+1b）：多方案 judge-panel → 對抗驗證砍缺陷 → 設計規格（含 BC-x）。承重核（因果鏈+事實求證）注入每個 agent。',
  phases: [
    { title: 'Explore' },
    { title: 'Propose' },
    { title: 'Adversarial' },
    { title: 'Synthesize' },
  ],
}

// args: 需求描述字串（由 /dev-design <需求> 傳入），或 undefined（則用 .claude-loop/artifacts 既有需求）
const REQUIREMENT = typeof args === 'string' && args.trim()
  ? args.trim()
  : (Array.isArray(args) ? args.join(' ') : '（未提供需求字串——請從 .claude-loop/artifacts/ 或對話脈絡推斷，若無則回報需要需求輸入）')

// ── 承重核注入片段（每個設計 agent 都帶）──
const LOADBEARING = `
【承重核要求 — 必須遵守】
1. 事實求證（認知驗證）：任何「X 是 Y / 系統現在如何」的事實斷言，先分級證據：
   🟢 A 級（檔:行原文）/ 🟡 B 級（間接）/ 🔴 反例檢查（若真應見X·若假應見Y·實際Z）。
   只有 A 級或 B 級+反例通過才可當設計前提；弱證據必須標「待驗證」，不可當既成事實設計。
2. 因果鏈（依賴影響）：設計觸及既有程式碼時，標出受影響的連動點（grep 呼叫者窮舉），
   呼叫者=0 的修改點要警示（可能有 inline 繞過）。
3. 誠實邊界：不確定就說不確定，不要為了完整性編造需求未指定的設計選擇。
`

// ============================================================
phase('Explore')

const CONTEXT_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['existingArchitecture', 'constraints', 'unknowns', 'factClaims'],
  properties: {
    existingArchitecture: { type: 'string', description: '既有系統相關結構（若 greenfield 則說明）' },
    constraints: { type: 'array', items: { type: 'string' } },
    unknowns: { type: 'array', items: { type: 'string' }, description: '需求中未指定、需澄清的點' },
    factClaims: { type: 'array', items: { type: 'string' }, description: '探索中做的事實斷言 + 證據級（A/B/弱）' },
  },
}

const ctx = await agent(
  `你是架構探索 agent。需求：「${REQUIREMENT}」
探索專案現況（Read/Grep/Glob）：相關既有模組、架構模式、約束、需求未指定的 unknowns。
${LOADBEARING}
回報：既有架構摘要 / 約束 / unknowns / 你做的事實斷言及證據級。`,
  { label: 'explore', phase: 'Explore', schema: CONTEXT_SCHEMA }
)
const CTX = JSON.stringify(ctx)

// ============================================================
phase('Propose')

const DESIGN_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['approach', 'modules', 'behaviorContracts', 'tradeoffs', 'rippleImpact'],
  properties: {
    approach: { type: 'string', description: '此方案的核心取向（一句話）' },
    modules: { type: 'array', items: { type: 'string', description: '模組/檔案 + 職責' } },
    behaviorContracts: { type: 'array', items: { type: 'string', description: 'BC-x：可驗證的行為契約' } },
    tradeoffs: { type: 'string', description: '此方案的取捨與最大風險' },
    rippleImpact: { type: 'array', items: { type: 'string', description: '因果鏈：觸及的既有連動點' } },
  },
}

const angles = [
  { key: 'mvp-first', brief: 'MVP 優先：最小可行、最少新增、最大複用既有。' },
  { key: 'robustness-first', brief: '健壯優先：邊界/錯誤處理/可擴展性優先，接受多一點結構。' },
  { key: 'simplicity-first', brief: '簡單優先：資深工程師視角，砍掉一切非必要抽象，KISS/YAGNI。' },
]

const proposals = (await parallel(angles.map(a => () =>
  agent(
    `你是架構設計 agent（${a.key} 視角）：${a.brief}
需求：「${REQUIREMENT}」
探索結果：${CTX}
產出一個完整架構方案：核心取向 / 模組與職責 / BC-x 行為契約（≥ 2，可驗證）/ 取捨與風險 / 因果鏈觸及的既有連動點。
${LOADBEARING}`,
    { label: `propose:${a.key}`, phase: 'Propose', schema: DESIGN_SCHEMA }
  )
))).filter(Boolean)

// ============================================================
phase('Adversarial')

const JUDGE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['rankings', 'fatalFlaws', 'recommendation'],
  properties: {
    rankings: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['approach', 'score', 'why'], properties: { approach: { type: 'string' }, score: { type: 'number' }, why: { type: 'string' } } } },
    fatalFlaws: { type: 'array', items: { type: 'string', description: '任一方案的致命缺陷' } },
    recommendation: { type: 'string', description: '推薦哪個方案為基底 + 該嫁接其他方案的哪些亮點' },
  },
}

// 對每個方案派 skeptic 找致命缺陷（perspective-diverse），再 judge-panel 評分
const critiques = (await parallel(proposals.map((p, i) => () =>
  agent(
    `你是設計缺陷 skeptic。盡力找出以下架構方案的致命缺陷（過度設計 / 遺漏邊界 / 因果鏈漏接 / 事實前提錯誤 / 可維護性陷阱）。預設懷疑，找不到才說沒有。
方案：${JSON.stringify(p)}
需求：「${REQUIREMENT}」
探索結果：${CTX}`,
    { label: `refute:${angles[i]?.key || i}`, phase: 'Adversarial' }
  )
))).filter(Boolean)

const judgment = await agent(
  `你是設計評審團。根據 ${proposals.length} 個方案 + 各自的 skeptic 批評，評分排名、列出跨方案的致命缺陷、推薦基底方案並指出該嫁接哪些亮點。
方案：${JSON.stringify(proposals)}
批評：${JSON.stringify(critiques)}`,
  { label: 'judge-panel', phase: 'Adversarial', schema: JUDGE_SCHEMA }
)

// ============================================================
phase('Synthesize')

const spec = await agent(
  `你是首席架構師，產出最終設計規格（繁中，直接落檔到 .claude-loop/artifacts/P1-design-spec.md）。
從評審推薦的基底方案綜合，嫁接亞軍亮點，吸收 skeptic 指出的缺陷做修正。
需求：「${REQUIREMENT}」
探索：${CTX}
方案：${JSON.stringify(proposals)}
評審：${JSON.stringify(judgment)}

設計規格須含：目標 / 模組與職責 / BC-x 行為契約（可驗證，編號）/ 因果鏈（觸及的既有連動點 + 影響決策）/ 取捨與風險 / 學習查詢結果（若有讀到 .claudedocs/records/問題追蹤.md 長期警惕模式）。
${LOADBEARING}
用 Write 把規格寫入 .claude-loop/artifacts/P1-design-spec.md（目錄不存在先建），並在回報摘要設計要點 + 殘餘風險。`,
  { label: 'synthesize-spec', phase: 'Synthesize' }
)

return { spec, judgment }
