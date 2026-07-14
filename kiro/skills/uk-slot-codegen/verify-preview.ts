/**
 * verify-preview.ts
 * 
 * 自動化 Cocos Preview 驗證：連接 Preview → 按熱鍵 → 收集 console.error。
 * 
 * Prerequisites:
 *   - Cocos Editor 已開啟目標專案
 *   - Preview 已啟動（或本腳本觸發）
 *   - puppeteer 已安裝：npm i puppeteer
 * 
 * Usage:
 *   npx tsx verify-preview.ts [--url http://localhost:7456] [--wait 3000]
 * 
 * Output: JSON report to stdout
 */

import puppeteer, { type Page } from 'puppeteer';

interface ModeResult {
  mode: string;
  key: string;
  errors: string[];
  warnings: string[];
  passed: boolean;
}

interface VerifyReport {
  url: string;
  timestamp: string;
  modes: ModeResult[];
  overall: boolean;
}

const MODES = [
  { mode: 'normal', key: '1' },
  { mode: 'freegame', key: '2' },
  { mode: 'bigwin', key: '3' },
  { mode: 'nearwin', key: '4' },
];

async function pressKeyAndCollect(page: Page, key: string, waitMs: number): Promise<{ errors: string[]; warnings: string[] }> {
  const errors: string[] = [];
  const warnings: string[] = [];
  
  const errorHandler = (msg: any) => {
    const type = msg.type();
    const text = msg.text();
    if (type === 'error') errors.push(text);
    else if (type === 'warning' && text.includes('Error')) warnings.push(text);
  };
  
  page.on('console', errorHandler);
  
  // Press the mode key
  await page.keyboard.press(`Digit${key}`);
  // Wait a bit then press Space (Spin)
  await new Promise(r => setTimeout(r, 500));
  await page.keyboard.press('Space');
  // Wait for the mode to play out
  await new Promise(r => setTimeout(r, waitMs));
  
  page.off('console', errorHandler);
  return { errors, warnings };
}

async function main() {
  const args = process.argv.slice(2);
  const urlIdx = args.indexOf('--url');
  const url = urlIdx >= 0 ? args[urlIdx + 1] : 'http://localhost:7456';
  const waitIdx = args.indexOf('--wait');
  const waitMs = waitIdx >= 0 ? parseInt(args[waitIdx + 1]) : 3000;
  
  console.error(`Connecting to ${url} (wait=${waitMs}ms per mode)...`);
  
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  // Collect page errors
  const pageErrors: string[] = [];
  page.on('pageerror', err => pageErrors.push(err.message));
  
  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
  } catch (e: any) {
    console.error(`Failed to connect to ${url}: ${e.message}`);
    console.error('Is Cocos Preview running?');
    await browser.close();
    process.exit(1);
  }
  
  // Wait for game to initialize
  console.error('Waiting for game init (5s)...');
  await new Promise(r => setTimeout(r, 5000));
  
  // Check if there were init errors
  if (pageErrors.length > 0) {
    console.error(`⚠ ${pageErrors.length} page errors during init`);
  }
  
  // Focus the game canvas
  await page.click('canvas').catch(() => {});
  
  const report: VerifyReport = {
    url,
    timestamp: new Date().toISOString(),
    modes: [],
    overall: true,
  };
  
  for (const { mode, key } of MODES) {
    console.error(`Testing mode: ${mode} (key=${key})...`);
    const { errors, warnings } = await pressKeyAndCollect(page, key, waitMs);
    const allErrors = [...errors, ...pageErrors.splice(0)];
    const passed = allErrors.length === 0;
    if (!passed) report.overall = false;
    
    report.modes.push({ mode, key, errors: allErrors, warnings, passed });
  }
  
  await browser.close();
  
  // Output JSON report
  console.log(JSON.stringify(report, null, 2));
  
  // Exit code
  process.exit(report.overall ? 0 : 1);
}

main().catch(e => { console.error(e); process.exit(2); });
