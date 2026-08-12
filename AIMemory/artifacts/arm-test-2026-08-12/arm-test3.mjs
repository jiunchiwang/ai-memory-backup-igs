import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

// arm-test3：修掉 arm-test2 的行號空洞混淆。
// 唯一變更：nocmt 剝完註解後「連續重編行號」，讓片段看起來是完整連續的一段。
// strip 邏輯與 prompt 逐字節與 arm-test2 相同 —— 這樣
//   old-orig vs new-orig  = 純 test-retest（同條件重跑的翻轉率）
//   old-nocmt vs new-nocmt = 只差行號連續性（修洞效果）
const REPO = "G:/AI/telegram-kiro-bridge-main";
const OUT = path.join(process.env.TEMP, "arm-test3-results.json");
const DRY = process.argv.includes("--dry");

const SITES = [
  { id: "S1", file: "src/concurrency.ts", from: 1, to: 35,
    mutFrom: "  const max = Math.max(1, Math.floor(limit) || 1);", mutTo: "  const max = limit;" },
  { id: "S2", file: "src/concurrency.ts", from: 1, to: 35,
    mutFrom: "    const next = waiters.shift();\n    if (next) next();\n    else active--;",
    mutTo: "    active--;\n    const next = waiters.shift();\n    if (next) next();" },
  { id: "S3", file: "src/moa-plan.ts", from: 466, to: 500,
    mutFrom: "      const blocker = stepDeps(s).find((d) => failedIds.has(d) || notRunReason.has(d));",
    mutTo: "      const blocker = stepDeps(s).find((d) => failedIds.has(d));" },
  { id: "S4", file: "src/moa-plan.ts", from: 570, to: 600,
    mutFrom: "      results.set(runnable[i].id, r);", mutTo: "      results.set(ready[i].id, r);" },
  { id: "S5", file: "src/plan-templates.ts", from: 240, to: 290,
    mutFrom: "    task: s.task.replace(PLACEHOLDER_RE, (whole, key: string) => values.get(key) ?? whole),",
    mutTo: "    task: [...values.entries()].reduce((acc, [k, v]) => acc.replace(new RegExp(`\\\\{\\\\{${k}\\\\}\\\\}`, \"g\"), v), s.task)," },
  { id: "S6", file: "src/sessionManager.ts", from: 1060, to: 1085,
    mutFrom: "    const msgId = session._toolWarningMsgId;\n    session._toolWarningMsgId = undefined;",
    mutTo: "    const msgId = session._toolWarningMsgId;" },
  { id: "S7", file: "src/agent-actions.ts", from: 275, to: 300,
    mutFrom: "rawSteps.length < 1 || rawSteps.length > PLAN_MAX_STEPS", mutTo: "rawSteps.length < 1" },
  { id: "S8", file: "src/tool-progress.ts", from: 44, to: 135,
    mutFrom: "          finished++;\n          if (id) titles.delete(id);", mutTo: "          if (id) titles.delete(id);" },
];

/** 機械式剝註解：整行註解直接丟、行尾註解在引號成對時才剝。不挑句子。（與 arm-test2 相同） */
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

/** 回傳 { text, mutLines }：mutLines 是突變碼在「渲染後」的行號（ground truth，不事後再搜一次）。 */
function buildExcerpt(site, variant) {
  const all = fs.readFileSync(path.join(REPO, site.file), "utf8").split(/\r?\n/);
  let text = all.slice(site.from - 1, site.to).join("\n");
  if (!text.includes(site.mutFrom)) throw new Error(site.id + ": 錨點不在區段內");
  const idx = text.indexOf(site.mutFrom);
  const offset = text.slice(0, idx).split("\n").length - 1;   // 突變起點在片段內的 0-based 行位移
  const mutCount = site.mutTo.split("\n").length;
  text = text.replace(site.mutFrom, site.mutTo);
  let lines = text.split("\n").map((l, i) => ({
    n: site.from + i, l, mut: i >= offset && i < offset + mutCount,
  }));
  if (variant === "nocmt") {
    lines = stripComments(lines);
    lines = lines.map((e, i) => ({ ...e, n: site.from + i }));  // ← 唯一的修正：連續重編
  }
  return {
    text: lines.map(({ n, l }) => String(n).padStart(4) + "  " + l).join("\n"),
    mutLines: lines.filter((e) => e.mut).map((e) => e.n),
    nLines: lines.length,
  };
}

// prompt 逐字節與 arm-test2 相同（含「不連續是因為部分行未附上」那句——對連續片段永不觸發，
// 但保留它才能讓 old vs new 的比較只差一個變因）
function prompt(site, variant) {
  return [
    "你在審查一份 TypeScript 專案的程式碼片段（行號是原檔的真實行號；不連續是因為部分行未附上）。",
    "請只根據這段程式碼本身推理，列出你認為**真的有缺陷**的地方。",
    "可能沒有缺陷，也可能有一個或多個。不要列風格、命名、型別註記等非行為問題。",
    "每一條格式：行號 + 一句失效機制（什麼輸入或時序會導致什麼錯誤結果）。",
    "最多列 5 條，按你的信心從高到低排。若認為沒有缺陷就明說沒有。",
    "不要呼叫任何工具、不要嘗試讀檔，片段就是全部可用資訊。",
    "",
    "檔案：" + site.file,
    "```typescript",
    buildExcerpt(site, variant).text,
    "```",
  ].join("\n");
}

function runOne(model, wantMax, site, variant, timeoutMs = 420000) {
  const taskLabel = site.id + "-" + variant;
  const gt = buildExcerpt(site, variant);
  return new Promise((resolve) => {
    const child = spawn("kiro-cli acp --model " + model, [], { shell: true, stdio: ["pipe", "pipe", "pipe"] });
    let buf = "", nextId = 1, text = "", effortAck = "", stderr = "";
    const pending = new Map();
    const base = { model, task: taskLabel, site: site.id, variant, mutLines: gt.mutLines, nLines: gt.nLines };
    const done = (r) => {
      try { spawn("taskkill", ["/PID", String(child.pid), "/T", "/F"], { stdio: "ignore", detached: true }).unref(); } catch {}
      try { child.kill(); } catch {}
      resolve({ ...base, ...r });
    };
    const hard = setTimeout(() => done({ error: "hard timeout", text, effortAck, stderr }), timeoutMs + 60000);
    child.stderr.on("data", (d) => { stderr += d.toString("utf8").slice(0, 300); });
    child.stdout.on("data", (d) => {
      buf += d.toString("utf8");
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
        if (!line) continue;
        let msg; try { msg = JSON.parse(line); } catch { continue; }
        if (msg.method === "session/update") {
          const u = msg.params?.update;
          if (u?.sessionUpdate === "agent_message_chunk" && u.content?.type === "text") text += u.content.text;
          continue;
        }
        if (msg.method && msg.id !== undefined) {
          child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: msg.id, result: { outcome: { outcome: "cancelled" } } }) + "\n");
          continue;
        }
        if (msg.id !== undefined && pending.has(msg.id)) {
          const p = pending.get(msg.id); pending.delete(msg.id);
          msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result);
        }
      }
    });
    const call = (m, p, ms = timeoutMs) => {
      const id = nextId++;
      return new Promise((res, rej) => {
        pending.set(id, { resolve: res, reject: rej });
        child.stdin.write(JSON.stringify({ jsonrpc: "2.0", id, method: m, params: p }) + "\n");
        setTimeout(() => { if (pending.has(id)) { pending.delete(id); rej(new Error(m + " timeout")); } }, ms);
      });
    };
    (async () => {
      const t0 = Date.now();
      await call("initialize", { protocolVersion: 1, clientCapabilities: { fs: { readTextFile: false, writeTextFile: false } } }, 60000);
      const sess = await call("session/new", { cwd: REPO, mcpServers: [] }, 120000);
      if (wantMax) {
        await call("session/prompt", { sessionId: sess.sessionId, prompt: [{ type: "text", text: "/effort max" }] }, 120000);
        effortAck = text.trim(); text = "";
        if (!/Effort set to max/i.test(effortAck)) {
          return done({ effort: "max", error: "effort 未確認生效", effortAck, stderr });
        }
      }
      const res = await call("session/prompt", { sessionId: sess.sessionId, prompt: [{ type: "text", text: prompt(site, variant) }] });
      clearTimeout(hard);
      done({ effort: wantMax ? "max" : "(none)", stopReason: res?.stopReason,
             ms: Date.now() - t0, effortAck, text: text.trim(), stderr });
    })().catch((e) => { clearTimeout(hard); done({ error: e.message, text, effortAck, stderr }); });
  });
}

// 預覽 + ground truth 自檢：突變首行必須真的出現在 mutLines[0] 那一行
const preview = [];
let bad = 0;
for (const s of SITES) {
  for (const v of ["orig", "nocmt"]) {
    const ex = buildExcerpt(s, v);
    const firstMut = s.mutTo.split("\n")[0].trim();
    const rendered = ex.text.split("\n");
    const hit = rendered.find((r) => r.startsWith(String(ex.mutLines[0]).padStart(4) + "  "));
    const ok = ex.mutLines.length > 0 && hit && hit.includes(firstMut);
    // 行號連續性檢查
    const nums = rendered.map((r) => Number(r.slice(0, 4)));
    const contiguous = nums.every((n, i) => i === 0 || n === nums[i - 1] + 1);
    if (!ok || !contiguous) bad++;
    preview.push(`${s.id}-${v}\t${ok ? "GT-OK" : "GT-BAD"}\t${contiguous ? "連續" : "有空洞"}\t${ex.nLines} 行\tmutLines=[${ex.mutLines}]`);
  }
}
console.log(preview.join("\n"));
if (bad) { console.error("\n自檢失敗 " + bad + " 項，中止"); process.exit(1); }
if (DRY) {
  console.log("\n===== S7-nocmt 預覽（上輪 sonnet 在這裡虛構隱藏行）=====");
  console.log(buildExcerpt(SITES[6], "nocmt").text);
  process.exit(0);
}

const results = [];
for (const s of SITES) {
  for (const v of ["orig", "nocmt"]) {
    for (const arm of [{ m: "claude-sonnet-4.6", max: true }, { m: "claude-opus-4.5", max: false }]) {
      const r = await runOne(arm.m, arm.max, s, v);
      results.push(r);
      console.log(s.id + "-" + v + " " + arm.m + (arm.max ? "[max]" : "") + " → " +
        (r.error ? "ERROR " + r.error : (r.ms / 1000).toFixed(0) + "s " + r.text.length + "ch"));
      fs.writeFileSync(OUT, JSON.stringify(results, null, 1), "utf8");
    }
  }
}
console.log("WROTE " + OUT);
