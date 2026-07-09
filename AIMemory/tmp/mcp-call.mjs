// Temporary helper: invoke mcp-memory.js tools directly over stdio JSON-RPC.
// Usage: node mcp-call.mjs <toolName> '<jsonArgs>'
import { spawn } from 'node:child_process';

const [, , toolName, argsJson] = process.argv;
if (!toolName) {
  console.error('Usage: node mcp-call.mjs <toolName> <jsonArgs>');
  process.exit(1);
}
import { readFileSync } from 'node:fs';
const rawArgs = argsJson && argsJson.startsWith('@')
  ? readFileSync(argsJson.slice(1), 'utf8')
  : argsJson;
const toolArgs = rawArgs ? JSON.parse(rawArgs) : {};

const child = spawn('node', ['G:\\AI\\telegram-kiro-bridge-main\\dist\\mcp-memory.js'], {
  cwd: 'G:\\AI\\telegram-kiro-bridge-main',
  env: {
    ...process.env,
    MEMORY_USER_ID: '509424983',
    MEMORY_DIR: 'G:\\AI\\AIMemory',
  },
  stdio: ['pipe', 'pipe', 'pipe'],
});

let buf = '';
const send = (msg) => child.stdin.write(JSON.stringify(msg) + '\n');

const timeout = setTimeout(() => {
  console.error('TIMEOUT');
  child.kill();
  process.exit(2);
}, 60000);

child.stderr.on('data', (d) => process.stderr.write(d));
child.stdout.on('data', (d) => {
  buf += d.toString();
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { continue; }
    if (msg.id === 1) {
      send({ jsonrpc: '2.0', method: 'notifications/initialized' });
      send({ jsonrpc: '2.0', id: 2, method: 'tools/call', params: { name: toolName, arguments: toolArgs } });
    } else if (msg.id === 2) {
      clearTimeout(timeout);
      console.log(JSON.stringify(msg, null, 2));
      child.kill();
      process.exit(0);
    }
  }
});

send({
  jsonrpc: '2.0',
  id: 1,
  method: 'initialize',
  params: {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'mcp-call', version: '1.0.0' },
  },
});
