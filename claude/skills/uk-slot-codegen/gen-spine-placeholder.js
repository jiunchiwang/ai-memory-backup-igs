/**
 * gen-spine-placeholder.js
 * 產生 Spine placeholder（JSON + atlas + PNG with text label）
 * 
 * Usage: node gen-spine-placeholder.js <outputDir> <name1> [name2] [name3] ...
 * Example: node gen-spine-placeholder.js E:\UK\uk_slot_pq5\assets\game\Spine FG_Declare FG_Compliment BigWin NearWin Scatter
 * 
 * 產出: <outputDir>/<name>/
 *   ├── <name>.json   (Spine skeleton data, 3 animations: Start/Loop/End)
 *   ├── <name>.atlas  (atlas description)
 *   └── <name>.png    (256x256 帶文字標示)
 */

const fs = require('fs');
const path = require('path');

// Try to find sharp from common locations
let sharp;
const sharpPaths = [
  path.join(process.env.BRIDGE_DIR || 'F:/AI/telegram-kiro-bridge', 'node_modules/sharp'),
  'sharp'
];
for (const p of sharpPaths) {
  try { sharp = require(p); break; } catch(e) {}
}
if (!sharp) {
  console.error('sharp not found. Install it or set BRIDGE_DIR env.');
  process.exit(1);
}

const WIDTH = 256;
const HEIGHT = 256;

function generateAtlas(name) {
  return `${name}.png
size: ${WIDTH},${HEIGHT}
format: RGBA8888
filter: Linear,Linear
repeat: none
${name}
  rotate: false
  xy: 0, 0
  size: ${WIDTH}, ${HEIGHT}
  orig: ${WIDTH}, ${HEIGHT}
  offset: 0, 0
  index: -1
`;
}

function generateSkeleton(name) {
  // 根據名稱決定動畫集合，確保直接綁定後 code 播動畫不報錯
  const presets = {
    // InLoopOutSpine（FgDeclare, FgCompliment 等）
    fg: { In: 0.5, Loop: 1.0, Out: 0.3 },
    // NearWinEffectComponent
    nearwin: { FadeIn: 0.3, NearWin: 1.0, FadeOut: 0.3 },
    // BigWinControll
    bigwin: { Start: 0.5, Loop: 1.0, End: 0.3, BigWin_Start: 0.5, BigWin_End: 0.3, MegaWin_Start: 0.5, MegaWin_End: 0.3, SuperWin_Start: 0.5, SuperWin_End: 0.3, UltimateWin_Start: 0.5, UltimateWin_End: 0.3 },
    // Scatter 動畫（Stop/Enter/Win/Idle/Collect）
    scatter: { Stop: 0.5, Enter: 1.0, Win: 1.0, Idle: 1.0, Collect: 0.5 },
    // 通用 Symbol 演出（Win/Remove）— SymbolSpine.SetAnimKey 用
    symbol: { Win: 1.0, Remove: 0.5 },
    // 通用 fallback
    default: { Start: 0.5, Loop: 1.0, End: 0.3, In: 0.5, Out: 0.3, FadeIn: 0.3, FadeOut: 0.3, NearWin: 1.0 },
  };

  // 自動選 preset
  let animSet;
  const lower = name.toLowerCase();
  if (lower.includes('fg_') || lower.includes('free') || lower.includes('declare') || lower.includes('compliment')) animSet = presets.fg;
  else if (lower.includes('nearwin')) animSet = presets.nearwin;
  else if (lower.includes('bigwin') || lower.includes('big_win')) animSet = presets.bigwin;
  else if (lower.includes('scatter')) animSet = presets.scatter;
  else if (lower.includes('symbol') || lower.includes('symboleffect')) animSet = presets.symbol;
  else animSet = presets.default;

  const animations = {};
  for (const [animName, duration] of Object.entries(animSet)) {
    animations[animName] = {
      slots: { slot: { attachment: [{ time: 0, name: name }, { time: duration, name: animName.includes('Out') || animName.includes('End') ? null : name }] } }
    };
  }

  return JSON.stringify({
    skeleton: { hash: "placeholder", spine: "3.8.99", width: WIDTH, height: HEIGHT },
    bones: [{ name: "root" }],
    slots: [{ name: "slot", bone: "root", attachment: name }],
    skins: {
      default: {
        slot: {
          [name]: { x: 0, y: 0, width: WIDTH, height: HEIGHT }
        }
      }
    },
    animations
  }, null, 2);
}

async function generatePng(name) {
  // 建立帶文字的 SVG 再轉 PNG
  const svg = `<svg width="${WIDTH}" height="${HEIGHT}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#333"/>
    <rect x="4" y="4" width="${WIDTH-8}" height="${HEIGHT-8}" fill="none" stroke="#0ff" stroke-width="2" stroke-dasharray="8,4"/>
    <text x="50%" y="40%" text-anchor="middle" fill="#0ff" font-size="16" font-family="monospace">PLACEHOLDER</text>
    <text x="50%" y="60%" text-anchor="middle" fill="#fff" font-size="20" font-family="sans-serif" font-weight="bold">${name}</text>
    <text x="50%" y="80%" text-anchor="middle" fill="#888" font-size="12" font-family="monospace">Spine Anim</text>
  </svg>`;
  return sharp(Buffer.from(svg)).png().toBuffer();
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: node gen-spine-placeholder.js <outputDir> <name1> [name2] ...');
    process.exit(1);
  }

  const outputDir = args[0];
  const names = args.slice(1);

  for (const name of names) {
    const dir = path.join(outputDir, name);
    fs.mkdirSync(dir, { recursive: true });

    // PNG
    const pngBuf = await generatePng(name);
    fs.writeFileSync(path.join(dir, `${name}.png`), pngBuf);

    // Atlas
    fs.writeFileSync(path.join(dir, `${name}.atlas`), generateAtlas(name));

    // Skeleton JSON
    fs.writeFileSync(path.join(dir, `${name}.json`), generateSkeleton(name));

    console.log(`✅ ${name} → ${dir}`);
  }

  console.log(`\nDone! ${names.length} spine placeholders generated.`);
}

main().catch(e => { console.error(e); process.exit(1); });
