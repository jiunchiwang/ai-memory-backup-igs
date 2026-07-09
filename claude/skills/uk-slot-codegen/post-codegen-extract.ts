/**
 * post-codegen-extract.ts
 * 
 * Template 自進化：比較 template 原始 vs codegen 產出，
 * 萃取可重用 pattern 累積到 codegen-patterns.json。
 * 
 * Usage:
 *   npx tsx post-codegen-extract.ts <template_path> <output_path> [--patterns <patterns.json>]
 * 
 * Example:
 *   npx tsx post-codegen-extract.ts E:\UK\uk_slot_template E:\UK\uk_slot_leprechauns_pots
 */

import * as fs from 'fs';
import * as path from 'path';

interface DiffEntry {
  file: string;           // relative path from assets/Script/
  type: 'modified' | 'added' | 'deleted';
  hunks: string[];        // diff hunks (simplified)
}

interface Pattern {
  file: string;
  description: string;
  category: 'always' | 'conditional' | 'custom';
  condition?: string;     // e.g. "SpinMode=dropEntry" or "HAS_FREE_GAME"
  occurrences: number;
  games: string[];        // game names that had this pattern
  stability: number;      // min(1.0, occurrences/3)
  propose_to_template: boolean;
}

interface PatternsDB {
  version: number;
  last_updated: string;
  patterns: Pattern[];
}

// --- Helpers ---

function getScriptFiles(dir: string): Map<string, string> {
  const result = new Map<string, string>();
  const scriptDir = path.join(dir, 'assets', 'Script');
  if (!fs.existsSync(scriptDir)) return result;
  
  function walk(d: string, prefix: string) {
    for (const entry of fs.readdirSync(d, { withFileTypes: true })) {
      const rel = prefix ? `${prefix}/${entry.name}` : entry.name;
      if (entry.isDirectory()) walk(path.join(d, entry.name), rel);
      else if (entry.name.endsWith('.ts')) {
        result.set(rel, fs.readFileSync(path.join(d, entry.name), 'utf8'));
      }
    }
  }
  walk(scriptDir, '');
  return result;
}

function computeDiffs(templateFiles: Map<string, string>, outputFiles: Map<string, string>): DiffEntry[] {
  const diffs: DiffEntry[] = [];
  
  for (const [file, outputContent] of outputFiles) {
    const templateContent = templateFiles.get(file);
    if (!templateContent) {
      diffs.push({ file, type: 'added', hunks: [outputContent.slice(0, 500)] });
    } else if (templateContent !== outputContent) {
      // Simple line-level diff: find changed lines
      const tLines = templateContent.split('\n');
      const oLines = outputContent.split('\n');
      const hunks: string[] = [];
      let hunk = '';
      for (let i = 0; i < Math.max(tLines.length, oLines.length); i++) {
        if (tLines[i] !== oLines[i]) {
          hunk += `L${i + 1}: -${(tLines[i] || '').trim()}\n`;
          hunk += `L${i + 1}: +${(oLines[i] || '').trim()}\n`;
        } else if (hunk) {
          hunks.push(hunk.trim());
          hunk = '';
        }
      }
      if (hunk) hunks.push(hunk.trim());
      if (hunks.length > 0) diffs.push({ file, type: 'modified', hunks: hunks.slice(0, 20) });
    }
  }
  
  for (const file of templateFiles.keys()) {
    if (!outputFiles.has(file)) {
      diffs.push({ file, type: 'deleted', hunks: [] });
    }
  }
  return diffs;
}

function classifyDiff(diff: DiffEntry): Pick<Pattern, 'category' | 'condition' | 'description'> {
  const content = diff.hunks.join('\n');
  
  // Always patterns: uncomment template code, fix known issues
  if (content.includes('IsGoingToFree') || content.includes('取消註解')) {
    return { category: 'always', description: `${diff.file}: uncomment flow-critical code` };
  }
  if (content.includes('SYMBOL_COUNT') && content.includes('static')) {
    return { category: 'always', description: `${diff.file}: replace SYMBOL_COUNT with game-specific value` };
  }
  if (content.includes('Symbol.A') || content.includes('Symbol.Ten')) {
    return { category: 'always', description: `${diff.file}: fix hardcoded Symbol enum references` };
  }
  
  // Conditional patterns: depend on feature flags or SpinMode
  if (content.includes('DropEntryStrategy') || content.includes('dropEntry')) {
    return { category: 'conditional', condition: 'SpinMode=dropEntry', description: `${diff.file}: dropEntry setup` };
  }
  if (content.includes('FreeGame') || content.includes('EnterFree') || content.includes('FgDeclare')) {
    return { category: 'conditional', condition: 'HAS_FREE_GAME', description: `${diff.file}: FreeGame wiring` };
  }
  if (content.includes('BigWin') || content.includes('ShowBigWin')) {
    return { category: 'conditional', condition: 'HAS_BIGWIN', description: `${diff.file}: BigWin integration` };
  }
  
  // Custom: game-specific (not reusable)
  return { category: 'custom', description: `${diff.file}: game-specific modification` };
}

// --- Main ---

function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: npx tsx post-codegen-extract.ts <template_path> <output_path> [--patterns <file>]');
    process.exit(1);
  }
  
  const templatePath = args[0];
  const outputPath = args[1];
  const patternsIdx = args.indexOf('--patterns');
  const patternsFile = patternsIdx >= 0 ? args[patternsIdx + 1] : path.join(__dirname, 'codegen-patterns.json');
  
  // Derive game name from output path
  const gameName = path.basename(outputPath);
  
  console.log(`Template: ${templatePath}`);
  console.log(`Output:   ${outputPath}`);
  console.log(`Patterns: ${patternsFile}`);
  console.log(`Game:     ${gameName}`);
  console.log('');
  
  // Load existing patterns DB
  let db: PatternsDB;
  if (fs.existsSync(patternsFile)) {
    db = JSON.parse(fs.readFileSync(patternsFile, 'utf8'));
  } else {
    db = { version: 1, last_updated: '', patterns: [] };
  }
  
  // Compute diffs
  const templateFiles = getScriptFiles(templatePath);
  const outputFiles = getScriptFiles(outputPath);
  const diffs = computeDiffs(templateFiles, outputFiles);
  
  console.log(`Files compared: template=${templateFiles.size}, output=${outputFiles.size}`);
  console.log(`Diffs found: ${diffs.length} (modified=${diffs.filter(d => d.type === 'modified').length}, added=${diffs.filter(d => d.type === 'added').length})`);
  console.log('');
  
  // Classify and merge into patterns DB
  let newPatterns = 0;
  let updatedPatterns = 0;
  
  for (const diff of diffs) {
    if (diff.type === 'deleted') continue; // template file removed = unusual, skip
    
    const classified = classifyDiff(diff);
    
    // Find existing pattern by file + category
    const existing = db.patterns.find(p => p.file === diff.file && p.category === classified.category && p.description === classified.description);
    
    if (existing) {
      if (!existing.games.includes(gameName)) {
        existing.games.push(gameName);
        existing.occurrences = existing.games.length;
        existing.stability = Math.min(1.0, existing.occurrences / 3);
        existing.propose_to_template = existing.category === 'always' && existing.occurrences >= 3;
        updatedPatterns++;
      }
    } else {
      db.patterns.push({
        file: diff.file,
        description: classified.description,
        category: classified.category,
        condition: classified.condition,
        occurrences: 1,
        games: [gameName],
        stability: Math.min(1.0, 1 / 3),
        propose_to_template: false,
      });
      newPatterns++;
    }
  }
  
  db.last_updated = new Date().toISOString();
  fs.writeFileSync(patternsFile, JSON.stringify(db, null, 2));
  
  // Report
  console.log(`Results: ${newPatterns} new patterns, ${updatedPatterns} updated`);
  console.log('');
  
  const proposals = db.patterns.filter(p => p.propose_to_template);
  if (proposals.length > 0) {
    console.log('🔥 PROPOSED FOR TEMPLATE (stability ≥ 1.0):');
    for (const p of proposals) {
      console.log(`  [${p.category}] ${p.description} (${p.occurrences} games: ${p.games.join(', ')})`);
    }
  }
  
  // Summary by category
  const always = db.patterns.filter(p => p.category === 'always');
  const conditional = db.patterns.filter(p => p.category === 'conditional');
  const custom = db.patterns.filter(p => p.category === 'custom');
  console.log(`\nPattern DB: ${db.patterns.length} total (always=${always.length}, conditional=${conditional.length}, custom=${custom.length})`);
}

main();
