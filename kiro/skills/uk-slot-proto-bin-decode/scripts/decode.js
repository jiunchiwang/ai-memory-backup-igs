#!/usr/bin/env node
/**
 * UK slot server 封包（protobuf .bin）還原工具。
 *
 * 用法（cwd 必須是 slot 專案根目錄，才找得到 node_modules 裡的 proto）：
 *   node decode.js <檔案.bin> [更多.bin ...] [選項]
 *
 * 選項：
 *   --type <MessageName>  指定 message 型別，跳過自動判斷
 *   --list                只列出這個專案 proto 有哪些 message 型別
 *   --stdout              把 JSON 印到 stdout（預設是寫檔）
 *   --out <dir>           指定輸出目錄（預設寫在 .bin 旁邊）
 *   --force               允許覆蓋已存在的輸出檔
 *
 * 輸出：<檔名>.decoded.json（刻意不叫 <檔名>.json，避免蓋掉人工整理過的同名檔）
 */
'use strict';

const fs = require('fs');
const path = require('path');

// ---------- 1. 找 proto ----------
// 不寫死專案名：掃 node_modules 的公司 scope，找名字含 proto 的套件。
function findProto(cwd) {
  const scopes = ['@igs-arcade-division-rd2', '@igs-arcade-division-rd1'];
  const found = [];
  for (const scope of scopes) {
    const scopeDir = path.join(cwd, 'node_modules', scope);
    if (!fs.existsSync(scopeDir)) continue;
    for (const pkg of fs.readdirSync(scopeDir)) {
      if (!/proto/i.test(pkg)) continue;
      const pkgDir = path.join(scopeDir, pkg);
      const js = fs.readdirSync(pkgDir).filter(f => f.endsWith('.js'));
      if (!js.length) continue;
      // 優先挑名字含 Proto 的（例如 ar2es2Proto.js），否則取第一支
      const entry = js.find(f => /proto/i.test(f)) || js[0];
      found.push(path.join(pkgDir, entry));
    }
  }
  if (!found.length) return null;
  if (found.length > 1) {
    // 本機 9 個專案目前都只裝一個 proto 套件，但殘留舊遊戲 proto 或版本並存是
    // 想像得到的。載錯包的後果特別惡劣: wire format 寬容，錯包照樣可能唯一命中，
    // 然後以「高信心」回報語意錯誤的 JSON。∴ 不靜默取第一個。
    console.error(`⚠ 找到 ${found.length} 個 proto 套件，取第一個：`);
    found.forEach((p, i) => console.error(`   ${i === 0 ? '→' : ' '} ${path.relative(cwd, p)}`));
    console.error('  解出來的東西語意不對的話，這裡是第一個要看的地方。');
  }
  return found[0];
}

function loadRoot(protoPath) {
  const mod = require(protoPath);
  // 套件通常把 package 名當成一層 namespace（例如 mod.ar2es2Proto）
  const nsKeys = Object.keys(mod).filter(
    k => mod[k] && typeof mod[k] === 'object' && Object.values(mod[k]).some(v => v && typeof v.decode === 'function')
  );
  if (nsKeys.length === 1) return mod[nsKeys[0]];
  // 也可能是直接攤平在頂層
  if (Object.values(mod).some(v => v && typeof v.decode === 'function')) return mod;
  if (nsKeys.length > 1) {
    // 沒遇過的情況。本腳本其他地方都不靜默猜，這裡也不該——挑第一個但要講出來。
    console.error(`⚠ proto 有多個 namespace（${nsKeys.join(', ')}），取第一個 ${nsKeys[0]}。`);
    console.error('  若解出來的東西不對，這裡就是第一個要看的地方。');
    return mod[nsKeys[0]];
  }
  return mod;
}

// ---------- 2. 判斷型別 ----------
// 判準：解碼 → 重新編碼 → 位元組與原檔「完全相等」。
// 為什麼不是「解碼沒丟例外」：protobuf 解碼極度寬容，packed repeated int32
// （例如 Column / IntAry）會把任何 bytes 欄位當成整數陣列吃下去而不報錯。
// 實測（uk_872 8 個真封包）：長度比對會留下 3 個候選，位元組完全相等只留 1 個。
function candidates(root, buf) {
  const names = Object.keys(root).filter(k => root[k] && typeof root[k].decode === 'function');
  const exact = [];
  const ranked = [];
  for (const name of names) {
    const T = root[name];
    let msg;
    try {
      msg = T.decode(buf);
      // 這裡曾經有一道 T.verify(T.toObject(msg))。實測 8 個真封包 × 全部型別＝
      // 78 次解碼成功，它一次都沒擋下東西——解碼出來的 Message 欄位型別必然合法，
      // verify() 是給「人手拼的 plain object」用的。留著只會讓人以為有一層驗證。
      const re = Buffer.from(T.encode(msg).finish());
      ranked.push({ name, ratio: re.length / buf.length });
      if (re.length === buf.length && re.equals(buf)) exact.push(name);
    } catch (e) {
      /* 這個型別解不動，跳過 */
    }
  }
  ranked.sort((a, b) => b.ratio - a.ratio);
  return { exact, ranked };
}

// ---------- 3. 摘要 ----------
// 只挑本框架常見欄位；欄位不存在就不印，不同專案 proto 也不會爆。
function summarize(obj) {
  const out = [];
  const money = ['TotalWin', 'FreeTotalWin', 'Bet', 'BaseBet', 'MaxBet'];
  for (const k of money) if (obj[k] !== undefined) out.push(`${k}=${obj[k]}`);
  if (obj.BetType !== undefined) out.push(`BetType=${obj.BetType}`);

  const rounds = obj.RoundQueue;
  if (Array.isArray(rounds)) {
    out.push(`RoundQueue=${rounds.length} round`);
    rounds.forEach((r, i) => {
      const bits = [];
      if (r.RoundWin !== undefined) bits.push(`win=${r.RoundWin}`);
      if (r.ReelWeightResult !== undefined) bits.push(`reel=${r.ReelWeightResult}`);
      if (r.MaxFlag) bits.push('MaxFlag');
      if (r.CurrFeverGameType) bits.push(`fever=${r.CurrFeverGameType}`);
      if (r.FreeNowRound || r.FreeTotalRound) bits.push(`free=${r.FreeNowRound || 0}/${r.FreeTotalRound || 0}`);
      if (r.WheelCount) bits.push(`wheel=${r.WheelCount}`);
      // 注意：proto3 + defaults:false 會把 0 值欄位整個拿掉，
      // 而 Type=0（FG）、SlotIndex=0 都是合法值 → 一律補 0，別印成 undefined
      if (Array.isArray(r.WheelFeatures) && r.WheelFeatures.length)
        bits.push(
          `features=[${r.WheelFeatures.map(f => `T${f.Type ?? 0}@${f.SlotIndex ?? 0}x${f.Count ?? 0}`).join(' ')}]`
        );
      if (Array.isArray(r.PlateQueue)) bits.push(`plate=${r.PlateQueue.length}`);
      if (r.MysteryEventTrigger) bits.push('Mystery');
      // 各專案 RoundInfo 欄位名不同（例：wrath_of_thunder 是 MGReelWeightResult、
      // 盤面直接掛在 round 上而非 PlateQueue）。認得的欄位太少時改印欄位名，
      // 至少讓人看得出這包的結構，而不是給一行空摘要。
      if (bits.length <= 1) bits.push(`欄位=[${Object.keys(r).join(' ')}]`);
      out.push(`  round[${i}] ${bits.join(' ')}`);
    });
  }
  return out;
}

// ---------- 4. glob 展開 ----------
// 不能靠 shell：PowerShell（本團隊主要 shell）不會替原生程式展開萬用字元，
// 會把 `*.bin` 原字串丟進來。實測 `node decode.js .claude_temp/*.bin` 在
// PowerShell 下就是拿到字面值然後 ENOENT。∴ 自己展開，各 shell 行為才一致。
function expandGlobs(patterns) {
  const out = [];
  for (const p of patterns) {
    if (!/[*?]/.test(p)) {
      out.push(p);
      continue;
    }
    const dir = path.dirname(p);
    const base = path.basename(p);
    // 大小寫要跟著檔案系統走，不能跟著 regex 預設走。Windows / macOS 的檔名比對
    // 不分大小寫，`*.BIN` 在 PowerShell 的 Get-ChildItem 配得到 8 個檔——
    // 腳本若用區分大小寫的 regex 就會配到 0 個，與所在平台的慣例相反。
    const ci = process.platform === 'win32' || process.platform === 'darwin' ? 'i' : '';
    const re = new RegExp(
      '^' + base.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$',
      ci
    );
    let entries = [];
    try {
      entries = fs.readdirSync(dir);
    } catch (e) {
      console.error(`⚠ glob「${p}」的目錄讀不到：${dir}`);
      continue;
    }
    const hit = entries
      .filter(f => re.test(f))
      .map(f => path.join(dir, f))
      // 目錄配到了也不要：後面 readFileSync 會噴 EISDIR，訊息看起來像檔案壞掉
      .filter(f => {
        try {
          return fs.statSync(f).isFile();
        } catch (e) {
          return false;
        }
      })
      .sort();
    if (!hit.length) console.error(`⚠ glob「${p}」沒有配到任何檔案。`);
    out.push(...hit);
  }
  return out;
}

// ---------- 5. 主流程 ----------
function main(argv) {
  const files = [];
  const opt = { type: null, stdout: false, out: null, force: false, list: false };
  // 取值型旗標要驗下一個 argv 真的是值：漏給值時 `--type --stdout` 會把 --stdout
  // 當成型別名吃掉，同時讓 --stdout 靜默失效——兩個錯疊在一起還不報錯。
  const takeValue = (flag, argv, i) => {
    const v = argv[i + 1];
    if (v === undefined || v.startsWith('--')) {
      console.error(`✗ ${flag} 後面要接一個值。`);
      process.exit(1);
    }
    return v;
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--type') opt.type = takeValue('--type', argv, i++);
    else if (a === '--out') opt.out = takeValue('--out', argv, i++);
    else if (a === '--stdout') opt.stdout = true;
    else if (a === '--force') opt.force = true;
    else if (a === '--list') opt.list = true;
    else if (a.startsWith('--')) {
      console.error(`✗ 不認得的選項：${a}`);
      process.exit(1);
    } else files.push(a);
  }

  const protoPath = findProto(process.cwd());
  if (!protoPath) {
    console.error('✗ 找不到 proto 套件。請確認 cwd 是 slot 專案根目錄且已 npm install。');
    console.error('  預期路徑：node_modules/@igs-arcade-division-rd2/*proto*/');
    process.exit(1);
  }
  const root = loadRoot(protoPath);
  const typeNames = Object.keys(root).filter(k => root[k] && typeof root[k].decode === 'function');
  console.error(`proto: ${path.relative(process.cwd(), protoPath)}  (${typeNames.length} 個 message)`);

  if (opt.list) {
    console.log(typeNames.join('\n'));
    return;
  }
  const targets = expandGlobs(files);
  if (!targets.length) {
    console.error('✗ 沒有指定 .bin 檔（或 glob 沒有配到任何檔案）。');
    process.exit(1);
  }

  if (opt.stdout && targets.length > 1) {
    console.error(`⚠ ${targets.length} 個檔案配 --stdout：輸出是「每包一個 JSON 物件」接續印出，`);
    console.error('  不是單一 JSON、也不是 JSON array，直接 JSON.parse 整份 stdout 會失敗。');
    console.error('  要程式化處理請一次一包，或改用預設的寫檔模式。');
  }

  let failed = 0;
  // 型別沒有唯一確認時要能被「只看離開碼的自動化」發現。這支 skill 的消費者是 agent，
  // 而 agent 讀的是 stdout + exit code——警告只印在 stderr 等於沒說。
  let uncertain = 0;
  for (const f of targets) {
    let buf;
    try {
      buf = fs.readFileSync(f);
    } catch (e) {
      console.error(`\n✗ 讀不到 ${f}：${e.code === 'ENOENT' ? '檔案不存在' : e.message}`);
      failed++;
      continue;
    }
    console.error(`\n=== ${path.basename(f)} (${buf.length} bytes) ===`);

    let typeName = opt.type;
    if (!typeName) {
      const { exact, ranked } = candidates(root, buf);
      if (exact.length === 1) {
        typeName = exact[0];
        console.error(`型別：${typeName}（位元組完全相等，唯一命中）`);
      } else if (exact.length > 1) {
        typeName = exact[0];
        uncertain++;
        console.error(`⚠ 型別不唯一，${exact.length} 個候選同時位元組相等：${exact.join(', ')}`);
        console.error(`  先用 ${typeName} 解，不確定的話請加 --type <名稱> 指定。`);
        console.error('  ⚠ 本包型別未確認，離開碼會是非 0。');
      } else {
        if (!ranked.length) {
          console.error('✗ 沒有任何型別解得動這包，可能不是這個專案的 protobuf 封包。');
          failed++;
          continue;
        }
        typeName = ranked[0].name;
        uncertain++;
        const top = ranked.slice(0, 3).map(r => `${r.name}(${r.ratio.toFixed(3)})`).join(' ');
        console.error(`⚠ 沒有型別能位元組完全還原（可能欄位序非正規或含 unknown field）。`);
        console.error(`  依重編碼長度比排序：${top}`);
        console.error(`  暫用 ${typeName} 解，結果請當成「未確認」，必要時加 --type 指定。`);
        console.error('  ⚠ 本包型別未確認，離開碼會是非 0。');
      }
    } else {
      console.error(`型別：${typeName}（由 --type 指定）`);
    }

    const T = root[typeName];
    if (!T) {
      console.error(`✗ proto 裡沒有 message「${typeName}」。可用：${typeNames.join(', ')}`);
      failed++;
      continue;
    }
    const obj = T.toObject(T.decode(buf), { longs: String, enums: String, defaults: false, arrays: true });
    const json = JSON.stringify(obj, null, 2);

    for (const line of summarize(obj)) console.error(line);

    if (opt.stdout) {
      console.log(json);
      continue;
    }
    const dir = opt.out || path.dirname(f);
    const dest = path.join(dir, path.basename(f, path.extname(f)) + '.decoded.json');
    if (fs.existsSync(dest) && !opt.force) {
      console.error(`⚠ ${path.relative(process.cwd(), dest)} 已存在，未覆蓋（要覆蓋請加 --force）。`);
      continue;
    }
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(dest, json);
    console.error(`→ ${path.relative(process.cwd(), dest)} (${json.length} bytes)`);
  }
  if (uncertain) {
    console.error(`\n⚠ ${uncertain} 個檔案的型別未確認 → 離開碼 1。`);
    console.error('  JSON 還是產出了（人可以看），但不要當成已確認的結果直接往下用。');
  }
  if (failed || uncertain) process.exit(1);
}

main(process.argv.slice(2));
