import fs from "node:fs";
import path from "node:path";

// 對 arm-test2（舊·nocmt 有行號空洞）與 arm-test3（新·nocmt 連續）在同一輪、同一把尺下評分。
// 判準（機械層）：回答中引用的行號 ∈ 突變行號集合 → 候選命中；
// 判準（判斷層）：候選命中還要「說對失效機制」才算命中，由人在下一步逐條看 snippet 判。
const REPO = "G:/AI/telegram-kiro-bridge-main";
const T = process.env.TEMP;

// 直接從 arm-test3.mjs 取 SITES 字面量，避免手抄一份（S5 的跳脫抄錯就全盤失準）
const src = fs.readFileSync(path.join(T, "arm-test3.mjs"), "utf8");
const SITES = eval(src.slice(src.indexOf("const SITES = ") + 14, src.indexOf("\n];") + 2));

function stripComments(lines) {
  const out = [];
  for (const e of lines) {
    const l = e.l;
    if (/^\s*(\/\/|\/\*|\*\/|\*(?!\w))/.test(l)) continue;
    let line = l;
    const i = line.indexOf("//");
    if (i > 0) {
      const before = line.slice(0, i);
      const dq = (before.match(/"/g) || []).length;
      const sq = (before.match(/'/g) || []).length;
      const bq = (before.match(/`/g) || []).length;
      if (dq % 2 === 0 && sq % 2 === 0 && bq % 2 === 0) line = before.replace(/\s+$/, "");
    }
    if (line.trim() === "") continue;
    out.push({ ...e, l: line });
  }
  return out;
}

/** renumber=true 是 arm-test3 的新行為；false 重現 arm-test2 的空洞編號。 */
function excerpt(site, variant, renumber) {
  const all = fs.readFileSync(path.join(REPO, site.file), "utf8").split(/\r?\n/);
  let text = all.slice(site.from - 1, site.to).join("\n");
  const idx = text.indexOf(site.mutFrom);
  const offset = text.slice(0, idx).split("\n").length - 1;
  const mutCount = site.mutTo.split("\n").length;
  text = text.replace(site.mutFrom, site.mutTo);
  let lines = text.split("\n").map((l, i) => ({ n: site.from + i, l, mut: i >= offset && i < offset + mutCount }));
  if (variant === "nocmt") {
    lines = stripComments(lines);
    if (renumber) lines = lines.map((e, i) => ({ ...e, n: site.from + i }));
  }
  return { mutLines: lines.filter((e) => e.mut).map((e) => e.n), lo: lines[0].n, hi: lines[lines.length - 1].n };
}

/**
 * 抽出回答中引用的行號。格式取自真實樣本（不是憑想像列舉）：
 *   「行 31：」「**行 31-32**」「行 288–291」（en dash）「第 293 行」「line 42」
 * 散文裡的裸數字（limit=2、3 個、active=1）刻意不收 —— 那會製造大量假候選。
 */
function citedLines(txt, lo, hi) {
  const out = new Set();
  const add = (a, b) => {
    const s = Number(a), e = b === undefined ? Number(a) : Number(b);
    if (!Number.isFinite(s) || e - s > 40) return;
    for (let v = s; v <= e; v++) if (v >= lo && v <= hi) out.add(v);
  };
  for (const m of txt.matchAll(/(?:行|line|L)\s*[:：]?\s*(\d+)\s*(?:[-–—~至]\s*(\d+))?/gi)) add(m[1], m[2]);
  for (const m of txt.matchAll(/第\s*(\d+)\s*(?:[-–—~至]\s*(\d+)\s*)?行/g)) add(m[1], m[2]);
  // 下面兩式是讀真實回答才發現的漏網格式（數字在前、無「行」前綴）：
  //   「584–587行：」「124–131：`tool_call_update` …」 — 少了它們會產生假漏報
  for (const m of txt.matchAll(/(\d+)\s*[-–—~至]\s*(\d+)\s*行/g)) add(m[1], m[2]);
  for (const m of txt.matchAll(/^[\s*_-]*(\d{2,5})(?:\s*[-–—~至]\s*(\d{2,5}))?\s*[：:]/gm)) add(m[1], m[2]);
  return [...out].sort((a, b) => a - b);
}

function load(file, renumber, tag) {
  const rows = JSON.parse(fs.readFileSync(path.join(T, file), "utf8"));
  return rows.map((r) => {
    const [sid, variant] = r.task.split("-");
    const site = SITES.find((s) => s.id === sid);
    const ex = excerpt(site, variant, renumber);
    const txt = r.text || "";
    const cited = citedLines(txt, ex.lo, ex.hi);
    const candidate = cited.some((c) => ex.mutLines.includes(c));
    return {
      batch: tag, site: sid, variant,
      arm: r.model === "claude-sonnet-4.6" ? "sonnet[max]" : "opus4.5",
      mutLines: ex.mutLines, cited, candidate,
      err: r.error || null, ms: r.ms, len: txt.length, text: txt,
    };
  });
}

const rows = [
  ...load("arm-test2-results.json", false, "old"),
  ...load("arm-test3-results.json", true, "new"),
];

const mode = process.argv[2] || "table";
if (mode === "table") {
  console.log("batch\tsite\tvar\tarm\t\tmut\t\tcited\t\t\t候選");
  for (const r of rows) {
    console.log([r.batch, r.site, r.variant, r.arm, "[" + r.mutLines + "]",
      "[" + r.cited.join(",") + "]", r.err ? "ERR" : (r.candidate ? "HIT?" : "-")].join("\t"));
  }
  const n = (b, v, a) => rows.filter((r) => r.batch === b && r.variant === v && r.arm === a && r.candidate).length;
  console.log("\n候選命中 /8：");
  for (const a of ["sonnet[max]", "opus4.5"])
    for (const v of ["orig", "nocmt"])
      console.log(`  ${a}\t${v}\told=${n("old", v, a)}\tnew=${n("new", v, a)}`);
} else if (mode === "judge") {
  // 候選：印引用突變行處的 ±窗口，供判斷「有沒有說對失效機制」
  // 非候選：印開頭，檢查有沒有「沒引行號但講對機制」的漏網
  const want = process.argv[3];
  for (const r of rows) {
    if (want && r.batch !== want) continue;
    const head = [r.batch, r.site, r.variant, r.arm].join("|");
    if (r.err) { console.log(`\n### ${head} ERROR ${r.err}`); continue; }
    if (!r.candidate) {
      console.log(`\n### ${head} 無候選 mut=[${r.mutLines}] cited=[${r.cited.join(",")}]\n${r.text.slice(0, 260).replace(/\n+/g, " ")}`);
      continue;
    }
    const pats = r.mutLines.flatMap((n) => [`行 ${n}`, `行${n}`, `第 ${n}`, `第${n}`, `行 ${n - 1}`, `**行 ${n}`]);
    let at = -1;
    for (const p of pats) { const i = r.text.indexOf(p); if (i >= 0 && (at < 0 || i < at)) at = i; }
    if (at < 0) at = 0;
    console.log(`\n### ${head} 候選 mut=[${r.mutLines}]\n${r.text.slice(Math.max(0, at - 80), at + 420).replace(/\n+/g, " ")}`);
  }
} else if (mode === "dump") {
  const filt = process.argv[3];
  for (const r of rows) {
    if (filt && !(r.batch + "-" + r.site + "-" + r.variant + "-" + r.arm).includes(filt)) continue;
    console.log("\n===== " + [r.batch, r.site, r.variant, r.arm].join(" | ") +
      "  mut=[" + r.mutLines + "] cited=[" + r.cited.join(",") + "] " + (r.candidate ? "候選" : "無候選") + " =====");
    console.log(r.err ? "ERROR: " + r.err : r.text);
  }
}
