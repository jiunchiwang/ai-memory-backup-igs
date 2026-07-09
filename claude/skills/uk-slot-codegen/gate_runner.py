"""
gate_runner.py — Codegen Gate 驗證工具（結構化 JSON 輸出）

用法：
  py gate_runner.py --step 3.2 --target E:/UK/uk_leprechauns_pots_client
  py gate_runner.py --step all --target E:/UK/uk_leprechauns_pots_client
  py gate_runner.py --step bom --target E:/UK/uk_leprechauns_pots_client

輸出：JSON { "step": "3.2", "pass": true/false, "checks": [...] }
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "pass": passed, "detail": detail}


def gate_bom(target: Path) -> list:
    """驗證所有 .ts 保留 UTF-8 BOM (EF BB BF)"""
    results = []
    no_bom = []
    for ts in (target / "assets" / "Script").rglob("*.ts"):
        data = ts.read_bytes()
        if len(data) >= 3 and data[:3] != b'\xef\xbb\xbf':
            no_bom.append(str(ts.relative_to(target)))
    if no_bom:
        results.append(check("BOM", False, f"Missing BOM: {', '.join(no_bom[:5])}{'...' if len(no_bom)>5 else ''}"))
    else:
        results.append(check("BOM", True, f"All .ts files have BOM"))
    return results


def gate_3_2(target: Path) -> list:
    """三方一致 + CommonState 完整性"""
    results = []
    gd = (target / "assets/Script/Game_Define.ts").read_text(encoding="utf-8-sig")
    gv = (target / "assets/Script/GameView.ts").read_text(encoding="utf-8-sig")

    # enum members
    enum_match = re.search(r"enum GAMEVIEW_STATE\s*\{([^}]+)\}", gd)
    enum_members = set(re.findall(r"(\w+)", enum_match.group(1))) if enum_match else set()

    # SetStateMachine registrations
    reg_members = set(re.findall(r"Game_Define\.GameState\.(\w+)", gv))

    missing_reg = enum_members - reg_members - {"__len__"}
    if missing_reg:
        results.append(check("enum↔register", False, f"In enum but not registered: {missing_reg}"))
    else:
        results.append(check("enum↔register", True))

    # CommonState integrity
    rse = (target / "assets/Script/GameState/RoundShowEndState.ts").read_text(encoding="utf-8-sig")
    if "CommonState.COMMON_SHOW" in rse:
        results.append(check("COMMON_SHOW", True))
    else:
        results.append(check("COMMON_SHOW", False, "RoundShowEndState must jump to CommonState.COMMON_SHOW"))

    if "CommonState.END" in gv:
        results.append(check("CommonState.END", True))
    else:
        results.append(check("CommonState.END", False, "ForEndToNext must have CommonState.END path"))

    # RetryRoundEnd mock guard
    retry_section = re.search(r"RetryRoundEnd\(\)[^}]+}", gv)
    if retry_section and "USE_MOCK_SERVER" in retry_section.group():
        results.append(check("RetryRoundEnd_no_mock", False, "RetryRoundEnd has USE_MOCK_SERVER guard (forbidden)"))
    else:
        results.append(check("RetryRoundEnd_no_mock", True))

    return results


def gate_3_4(target: Path) -> list:
    """Mock Server gate"""
    results = []
    gv = (target / "assets/Script/GameView.ts").read_text(encoding="utf-8-sig")

    if "GenerateMockSpinAck" in gv:
        results.append(check("GenerateMockSpinAck", True))
    else:
        results.append(check("GenerateMockSpinAck", False))

    if "this.InitMockKeyboard()" in gv:
        results.append(check("InitMockKeyboard_called", True))
    else:
        results.append(check("InitMockKeyboard_called", False, "InitMockKeyboard() not called in start()"))

    # IsGoingToFree = true must be uncommented (not on a // line)
    lines = gv.split("\n")
    fg_trigger = any(
        "IsGoingToFree" in l and "= true" in l and not l.strip().startswith("//")
        for l in lines
    )
    if fg_trigger:
        results.append(check("IsGoingToFree_uncommented", True))
    else:
        results.append(check("IsGoingToFree_uncommented", False,
                             "IsGoingToFree = true is still commented out — FG won't trigger"))

    # RoundWin must exist in mock data (missing → NaN → award skipped)
    if "RoundWin" in gv:
        results.append(check("Mock_RoundWin", True))
    else:
        results.append(check("Mock_RoundWin", False, "Mock IRoundInfo missing RoundWin field"))

    # SCATTER_SYMBOL must be single enum member (Symbol.XXX), not array or bare number
    gd = (target / "assets/Script/Game_Define.ts").read_text(encoding="utf-8-sig")
    if re.search(r"SCATTER_SYMBOL\s*=\s*\[", gd):
        results.append(check("SCATTER_SYMBOL_not_array", False,
                             "SCATTER_SYMBOL is array — must be single Symbol.XXX enum member"))
    else:
        results.append(check("SCATTER_SYMBOL_not_array", True))

    if re.search(r"SCATTER_SYMBOL\s*=\s*Symbol\.", gd):
        results.append(check("SCATTER_SYMBOL_enum", True))
    else:
        results.append(check("SCATTER_SYMBOL_enum", False,
                             "SCATTER_SYMBOL must use enum member (Symbol.XXX), not bare number"))

    return results


def gate_3_10(target: Path) -> list:
    """Feature Code gate"""
    results = []
    award = (target / "assets/Script/GameState/AwardState.ts").read_text(encoding="utf-8-sig")

    if "AudioManager.Play" in award:
        results.append(check("AudioManager.Play", True))
    else:
        results.append(check("AudioManager.Play", False, "AwardState must use AudioManager.Play"))

    if "soundManager.Play" in award:
        results.append(check("no_soundManager", False, "AwardState uses soundManager (forbidden)"))
    else:
        results.append(check("no_soundManager", True))

    if "Game_Define.AudioClips" in award:
        results.append(check("no_Game_Define_AudioClips", False, "AudioClips is on AudioManager, not Game_Define"))
    else:
        results.append(check("no_Game_Define_AudioClips", True))

    if re.search(r"BigWin\.Show\(", award):
        results.append(check("BigWin.Show", True))
    else:
        results.append(check("BigWin.Show", False, "AwardState must call BigWin.Show(win, lvl)"))

    if "ShowBigWin(" in award:
        results.append(check("no_ShowBigWin", False, "ShowBigWin is not a valid API (use BigWin.Show)"))
    else:
        results.append(check("no_ShowBigWin", True))

    return results


def gate_5_tsc(target: Path) -> list:
    """TypeScript compilation check"""
    results = []
    tsconfig = target / "tsconfig.json"
    if not tsconfig.exists():
        results.append(check("tsc_noEmit", False, "tsconfig.json not found"))
        return results

    proc = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", str(tsconfig)],
        capture_output=True, text=True, cwd=str(target), timeout=60
    )
    if proc.returncode == 0:
        results.append(check("tsc_noEmit", True))
    else:
        errors = proc.stdout.strip().split("\n")[:5]
        results.append(check("tsc_noEmit", False, "; ".join(errors)))
    return results


GATES = {
    "bom": gate_bom,
    "3.2": gate_3_2,
    "3.4": gate_3_4,
    "3.10": gate_3_10,
    "5": gate_5_tsc,
}


def main():
    parser = argparse.ArgumentParser(description="Codegen Gate Runner")
    parser.add_argument("--step", required=True, help="Gate step (e.g. 3.2, bom, all)")
    parser.add_argument("--target", required=True, help="Target project root")
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(json.dumps({"error": f"Target not found: {target}"}))
        sys.exit(1)

    if args.step == "all":
        steps_to_run = list(GATES.keys())
    else:
        steps_to_run = [args.step]

    all_results = []
    for step in steps_to_run:
        if step not in GATES:
            all_results.append({"step": step, "pass": None, "checks": [check("unknown", False, f"No gate for step {step}")]})
            continue
        try:
            checks = GATES[step](target)
            passed = all(c["pass"] for c in checks)
            all_results.append({"step": step, "pass": passed, "checks": checks})
        except Exception as e:
            all_results.append({"step": step, "pass": False, "checks": [check("exception", False, str(e))]})

    output = {
        "target": str(target),
        "results": all_results,
        "all_pass": all(r["pass"] for r in all_results if r["pass"] is not None),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    sys.exit(0 if output["all_pass"] else 1)


if __name__ == "__main__":
    main()
