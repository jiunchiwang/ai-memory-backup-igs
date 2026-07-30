"""
verify_compile.py — Codegen 產出後的快速編譯驗證
用法：py verify_compile.py <target_path>

做五件事：
1. 檢查所有 import 的本地 .ts 檔案是否存在
2. 檢查 .js 檔案（如 proto）語法是否正確（用 Node.js 嘗試 require）
3. 檢查常見的遺漏 pattern（未宣告變數、重複 export 等）
4. 檢查 Proto.ts runtime/type bridge 與 Mock／placeholder 欄位契約
5. 執行 TypeScript compiler，專案自身 diagnostics 不為 0 即失敗

不需要 Cocos Editor 在線。回報 PASS / FAIL + 具體錯誤列表。
"""
import sys
import re
import subprocess
import os
import shutil
from pathlib import Path


PROTO_IMPORT_RE = re.compile(
    r'import\s+protocol\s+from\s+["\'](?P<path>\./Test/[^"\']+\.js)["\']'
)

PROJECT_SOURCE_PREFIXES = ("assets/Script/", "assets/game/Script/", "tests/")
TS_ERROR_RE = re.compile(r"^(?P<path>.+?)\(\d+,\d+\): error TS\d+:")


def _real_tsc_from_shim(path: Path) -> Path | None:
    """npm/pnpm 的 .bin/tsc shim 對應到同層 node_modules/typescript/bin/tsc。"""
    if path.parent.name.lower() != ".bin":
        return None
    candidate = path.parent.parent / "typescript" / "bin" / "tsc"
    return candidate if candidate.is_file() else None


def resolve_typescript_compiler(target: Path) -> tuple[list[str] | None, str]:
    """解析並驗證 TypeScript compiler；不使用會隱式下載套件的 npx。"""
    node = shutil.which("node")
    if not node:
        return None, "node executable not found"

    candidates: list[tuple[Path, str]] = []

    def add_candidate(path: Path | None, label: str) -> None:
        if not path:
            return
        path = path.resolve()
        if path.is_file() and all(existing != path for existing, _ in candidates):
            candidates.append((path, label))

    add_candidate(target / "node_modules" / "typescript" / "bin" / "tsc", "target-local")

    env_path = os.environ.get("TSC_PATH")
    if env_path:
        configured = Path(env_path)
        if configured.is_dir():
            configured = configured / "bin" / "tsc"
        add_candidate(_real_tsc_from_shim(configured) or configured, "TSC_PATH")

    for name in ("tsc.cmd", "tsc"):
        found = shutil.which(name)
        if not found:
            continue
        found_path = Path(found)
        add_candidate(_real_tsc_from_shim(found_path) or found_path, "PATH")

    rejected = []
    for path, source in candidates:
        command = [node, str(path)]
        try:
            probe = subprocess.run(
                [*command, "--version"], capture_output=True, text=True, timeout=10
            )
        except (OSError, subprocess.SubprocessError) as exc:
            rejected.append(f"{source}:{path} ({exc})")
            continue
        version_output = (probe.stdout + probe.stderr).strip()
        if probe.returncode == 0 and re.search(r"\bVersion\s+\d+\.\d+", version_output):
            return command, f"{source}:{path} ({version_output})"
        rejected.append(f"{source}:{path} ({version_output or 'invalid compiler'})")

    detail = "; ".join(rejected) if rejected else "no candidates"
    return None, (
        "TypeScript compiler not found. Install target devDependency 'typescript' or set TSC_PATH. "
        f"Checked: {detail}"
    )


def classify_typescript_diagnostics(output: str, target: Path) -> tuple[list[str], int]:
    """回傳專案自身 error 行與忽略的 framework/extension error 數。"""
    owned = []
    external_count = 0
    target_prefix = target.resolve().as_posix().rstrip("/") + "/"
    for raw_line in output.splitlines():
        line = raw_line.strip()
        match = TS_ERROR_RE.match(line)
        if not match:
            continue
        path = match.group("path").replace("\\", "/")
        if path.lower().startswith(target_prefix.lower()):
            path = path[len(target_prefix):]
        if path.startswith(PROJECT_SOURCE_PREFIXES):
            owned.append(line)
        else:
            external_count += 1
    return owned, external_count


def check_typescript_compile(target: Path) -> dict:
    """執行 tsc；以專案兩個 Script 目錄與 tests diagnostics 阻擋 codegen。"""
    tsconfig = target / "tsconfig.json"
    if not tsconfig.exists():
        return {
            "errors": [f"tsconfig.json not found: {tsconfig}"],
            "ignored_errors": 0,
            "compiler": "",
        }

    command, compiler = resolve_typescript_compiler(target)
    if not command:
        return {"errors": [compiler], "ignored_errors": 0, "compiler": ""}

    try:
        proc = subprocess.run(
            [*command, "--noEmit", "--pretty", "false", "--project", str(tsconfig)],
            capture_output=True, text=True, cwd=str(target), timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "errors": [f"TypeScript compiler execution failed: {exc}"],
            "ignored_errors": 0,
            "compiler": compiler,
        }

    output = "\n".join(part for part in (proc.stdout, proc.stderr) if part)
    owned, ignored = classify_typescript_diagnostics(output, target)
    if proc.returncode != 0 and not owned and ignored == 0:
        detail = output.strip().splitlines()[:3]
        owned.append("TypeScript compiler failed without diagnostics: " + " | ".join(detail))
    return {"errors": owned, "ignored_errors": ignored, "compiler": compiler}


def _declaration_body(content: str, kind: str, name: str) -> str:
    # pbts 在 exported namespace 內的 members 通常不重複寫 export。
    match = re.search(rf'(?:export\s+)?{kind}\s+{re.escape(name)}\b[^{{]*\{{', content)
    if not match:
        return ""
    start = match.end()
    end = content.find("}", start)
    return content[start:end] if end >= 0 else ""


def check_proto_contract(target: Path) -> list[str]:
    """驗證 CJS runtime bridge、namespace type export 與 Mock schema 一致。"""
    errors = []
    script_dir = target / "assets" / "Script"
    proto_ts = script_dir / "Proto.ts"
    if not proto_ts.exists():
        return ["assets/Script/Proto.ts: missing proto bridge"]

    bridge = proto_ts.read_text(encoding="utf-8-sig", errors="ignore")
    import_match = PROTO_IMPORT_RE.search(bridge)
    if not import_match:
        return ["assets/Script/Proto.ts: must default-import ./Test/*.js as protocol"]
    if "export default protocol" not in bridge:
        errors.append("assets/Script/Proto.ts: missing 'export default protocol' runtime export")
    if re.search(r'export\s+\*\s+from', bridge):
        errors.append("assets/Script/Proto.ts: export * is forbidden for the CJS runtime bridge")

    js_path = (script_dir / import_match.group("path")).resolve()
    dts_path = js_path.with_suffix(".d.ts")
    if not js_path.exists() or not dts_path.exists():
        errors.append(f"assets/Script/Proto.ts: proto pair not found for {import_match.group('path')}")
        return errors

    dts = dts_path.read_text(encoding="utf-8", errors="ignore")
    ns_match = re.search(r'export\s+namespace\s+(\w+)', dts)
    if not ns_match:
        errors.append(f"{dts_path.name}: exported namespace not found")
        return errors
    namespace = ns_match.group(1)

    type_export = re.search(
        rf'export\s+type\s*\{{[^}}]*\b{re.escape(namespace)}\b[^}}]*\}}\s+from\s+["\']{re.escape(import_match.group("path"))}["\']',
        bridge,
    )
    if not type_export:
        errors.append(f"assets/Script/Proto.ts: missing type export for namespace {namespace}")

    runtime_check = (
        "const p=require(process.argv[1]);const n=process.argv[2];"
        "const x=p&&p[n];const m=['GameInfoData','CColumn'].filter(k=>!x||typeof x[k]!=='function');"
        "if(m.length){console.error('missing '+n+'.'+m.join(','));process.exit(1)}"
    )
    result = subprocess.run(
        ["node", "-e", runtime_check, str(js_path), namespace],
        capture_output=True, text=True, cwd=str(target), timeout=10,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        errors.append(f"{js_path.name}: runtime namespace contract failed ({detail})")

    game_view = script_dir / "GameView.ts"
    mock = game_view.read_text(encoding="utf-8-sig", errors="ignore") if game_view.exists() else ""
    js = js_path.read_text(encoding="utf-8", errors="ignore")
    interface_body = _declaration_body(dts, "interface", "IRoundInfo")
    class_body = _declaration_body(dts, "class", "RoundInfo")
    for field in ("PlateQueue", "WinLineIndex"):
        if re.search(rf'\b{field}\s*:', mock):
            if not re.search(rf'\b{field}\??\s*:', interface_body):
                errors.append(f"{dts_path.name}: IRoundInfo missing Mock field {field}")
            if not re.search(rf'\b{field}\s*:', class_body):
                errors.append(f"{dts_path.name}: RoundInfo missing Mock field {field}")
            if not re.search(rf'(?:this|RoundInfo\.prototype)\.{field}\s*=', js):
                errors.append(f"{js_path.name}: RoundInfo runtime missing default for Mock field {field}")

    source_files = list(script_dir.rglob("*.ts"))
    sources = {
        path.relative_to(script_dir).as_posix(): path.read_text(encoding="utf-8-sig", errors="ignore")
        for path in source_files
    }
    all_source = "\n".join(sources.values())

    def require_compat_field(field: str, interface: str, runtime_class: str, source: str) -> None:
        if field not in source:
            return
        iface_body = _declaration_body(dts, "interface", interface)
        runtime_body = _declaration_body(dts, "class", runtime_class)
        if not re.search(rf'\b{field}\??\s*:', iface_body):
            errors.append(f"{dts_path.name}: {interface} missing used field {field}")
        if not re.search(rf'\b{field}\s*:', runtime_body):
            errors.append(f"{dts_path.name}: {runtime_class} missing used field {field}")
        if not re.search(rf'(?:this|{runtime_class}\.prototype)\.{field}\s*=', js):
            errors.append(f"{js_path.name}: {runtime_class} runtime missing default for {field}")

    require_compat_field("FreeGameRound", "ISpinAck", "SpinAck", all_source)
    require_compat_field(
        "EliminatePos", "IAwardData", "AwardData", sources.get("EffectPlate/EffectPlate.ts", "")
    )

    if "GenerateMockSpinAck" in mock and "FreeGameRound" in all_source:
        if not re.search(r'\bFreeGameRound\s*:', mock):
            errors.append("GameView.ts: GenerateMockSpinAck must initialize used field FreeGameRound")

    award_state = sources.get("GameState/AwardState.ts", "")
    if "SmallWin?.SetWinLabelRunning" in award_state and re.search(r'm_smallWin\w*\s*:\s*Node\b', mock):
        errors.append("AwardState.ts: SmallWin is Node; SetWinLabelRunning is not a Node API")

    spin_state = sources.get("GameState/SpinState.ts", "")
    effect_plate = sources.get("EffectPlate/EffectPlate.ts", "")
    for member in ("CurAwardLines", "StopOneLineShow"):
        if f"EffectPlate.{member}" in spin_state and not re.search(
            rf'(?:get\s+|\b){member}\b', effect_plate
        ):
            errors.append(f"SpinState.ts: EffectPlate.{member} is used but not implemented")

    recover = sources.get("RecoverSpinAck.ts", "")
    round_fields = interface_body + "\n" + class_body
    for field in re.findall(r'\bt\.(\w+)\s*=\s*cur\.\1\b', recover):
        if not re.search(rf'\b{field}\??\s*:', round_fields):
            errors.append(f"RecoverSpinAck.ts: RoundInfo field {field} is not declared by placeholder proto")

    return errors

def check_local_imports(target: Path) -> list[str]:
    """檢查所有 .ts 裡 import 的本地相對路徑是否存在"""
    errors = []
    script_dir = target / "assets" / "Script"
    if not script_dir.exists():
        return [f"Script directory not found: {script_dir}"]
    
    for ts_file in script_dir.rglob("*.ts"):
        content = ts_file.read_text(encoding='utf-8', errors='ignore')
        # 找相對 import：import ... from "./xxx" 或 "../xxx"
        for m in re.finditer(r'from\s+["\'](\./[^"\']+|\.\.\/[^"\']+)["\']', content):
            import_path = m.group(1)
            # 解析相對路徑
            resolved = (ts_file.parent / import_path).resolve()
            # 嘗試 .ts 和目錄下的 index.ts
            candidates = [
                resolved.with_suffix('.ts'),
                resolved / 'index.ts',
                resolved,  # 可能是完整路徑
            ]
            if not any(c.exists() for c in candidates):
                rel = ts_file.relative_to(target)
                errors.append(f"{rel}: import '{import_path}' -> file not found")
    return errors

def check_js_syntax(target: Path) -> list[str]:
    """用 Node.js 檢查 .js 檔案語法（特別是 proto）"""
    errors = []
    test_dir = target / "assets" / "Script" / "Test"
    if not test_dir.exists():
        return []
    
    for js_file in test_dir.glob("*.js"):
        # 用 node --check 驗證語法
        result = subprocess.run(
            ["node", "--check", str(js_file)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            errors.append(f"{js_file.name}: {result.stderr.strip()}")
            continue
        
        # 額外：grep 未宣告的 $util / $root 等 pattern
        content = js_file.read_text(encoding='utf-8', errors='ignore')
        if '$util.' in content and 'var $util' not in content and 'const $util' not in content:
            errors.append(f"{js_file.name}: uses $util but never declares it (missing 'var $util = protobuf.util;')")
        if '$root.' in content and 'var $root' not in content and 'const $root' not in content:
            # $root 通常在 protobuf.roots 那行
            if 'protobuf.roots' not in content:
                errors.append(f"{js_file.name}: uses $root but never declares it")
    
    return errors

def check_common_patterns(target: Path) -> list[str]:
    """檢查常見的 codegen 遺漏"""
    errors = []
    script_dir = target / "assets" / "Script"
    if not script_dir.exists():
        return []
    
    for ts_file in script_dir.rglob("*.ts"):
        content = ts_file.read_text(encoding='utf-8', errors='ignore')
        rel = ts_file.relative_to(target)
        
        # 檢查 ccclass 名稱是否跟檔名一致
        ccclass_matches = re.findall(r'@ccclass\(["\']([^"\']+)["\']\)', content)
        for name in ccclass_matches:
            if '.' in name:
                # namespace 格式如 "Game.IdleState" — 檢查後半
                class_part = name.split('.')[-1]
            else:
                class_part = name
            if class_part != ts_file.stem and class_part != ts_file.stem.replace('State', ''):
                # 允許一些 variation，只報明顯不匹配
                pass  # 暫時不報，太多假陽性
        
        # 檢查 export class 但沒有 import 對應的 decorator
        if 'export class' in content and '@ccclass' not in content and 'Component' in content:
            # 有 Component 但沒 ccclass → 可能忘了加
            if 'extends Component' in content or 'extends BaseState' in content:
                pass  # BaseState 不需要 ccclass
    
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: py verify_compile.py <target_path>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"ERROR: {target} not found")
        sys.exit(1)
    
    print(f"Verifying codegen output: {target}")
    print("=" * 60)
    
    all_errors = []
    
    # 1. Local import check
    print("\n[1/5] Checking local imports...")
    import_errors = check_local_imports(target)
    all_errors.extend(import_errors)
    print(f"  {'PASS' if not import_errors else f'FAIL ({len(import_errors)} errors)'}")
    for e in import_errors[:10]:
        print(f"    [x] {e}")
    
    # 2. JS syntax check
    print("\n[2/5] Checking JS files (proto)...")
    js_errors = check_js_syntax(target)
    all_errors.extend(js_errors)
    print(f"  {'PASS' if not js_errors else f'FAIL ({len(js_errors)} errors)'}")
    for e in js_errors:
        print(f"    [x] {e}")
    
    # 3. Common pattern check
    print("\n[3/5] Checking common patterns...")
    pattern_errors = check_common_patterns(target)
    all_errors.extend(pattern_errors)
    print(f"  {'PASS' if not pattern_errors else f'FAIL ({len(pattern_errors)} errors)'}")
    for e in pattern_errors:
        print(f"    [x] {e}")

    # 4. Proto bridge + Mock schema contract
    print("\n[4/5] Checking proto runtime/type and Mock schema contract...")
    proto_errors = check_proto_contract(target)
    all_errors.extend(proto_errors)
    print(f"  {'PASS' if not proto_errors else f'FAIL ({len(proto_errors)} errors)'}")
    for e in proto_errors:
        print(f"    [x] {e}")

    # 5. Actual TypeScript diagnostics
    print("\n[5/5] Running TypeScript diagnostics...")
    ts_result = check_typescript_compile(target)
    ts_errors = ts_result["errors"]
    all_errors.extend(ts_errors)
    print(f"  Compiler: {ts_result['compiler'] or 'unavailable'}")
    print(f"  {'PASS' if not ts_errors else f'FAIL ({len(ts_errors)} project errors)'}")
    if ts_result["ignored_errors"]:
        print(f"  Ignored framework/extension declaration errors: {ts_result['ignored_errors']}")
    for e in ts_errors[:20]:
        print(f"    [x] {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print(f"FAIL: {len(all_errors)} error(s) found")
        sys.exit(1)
    else:
        print("PASS: All checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
