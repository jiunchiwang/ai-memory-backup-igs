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

from check_regression_v2 import run_one as run_regression
from spec_traceability import extract_spec_ids, write_manifest
from verify_compile import check_proto_contract, check_typescript_compile
from bind_symbol_effect_prefabs import bind as check_symbol_effect_bindings


def check(name: str, passed: bool, detail: str = "", level: str = "error") -> dict:
    return {"name": name, "pass": passed, "detail": detail, "level": level}


def visible_row_start(max_rows: int, visible_rows: int, alignment: str) -> int:
    """Return the first physical row shown by a top/center/bottom-aligned window."""
    difference = max(0, max_rows - visible_rows)
    if alignment == "bottom":
        return difference
    if alignment == "top":
        return 0
    return difference // 2


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
    enum_members = set()
    if enum_match:
        enum_body = re.sub(r"/\*.*?\*/", "", enum_match.group(1), flags=re.S)
        enum_body = re.sub(r"//.*", "", enum_body)
        for entry in enum_body.split(","):
            member = re.match(r"\s*([A-Za-z_$][\w$]*)", entry)
            if member:
                enum_members.add(member.group(1))

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
    gd = (target / "assets/Script/Game_Define.ts").read_text(encoding="utf-8-sig")

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

    row_match = re.search(r"static\s+ROW\s*=\s*(\d+)", gd)
    visible_rows = int(row_match.group(1)) if row_match else 0
    max_row_match = re.search(r"static\s+MAX_ROW\s*=\s*(\d+)", gd)
    max_rows = int(max_row_match.group(1)) if max_row_match else visible_rows
    standard_block = gv
    layout_path = target / "assets" / "Script" / "ReelLayoutConfig.ts"
    if layout_path.exists():
        layout_text = layout_path.read_text(encoding="utf-8-sig")
        standard_block = layout_text.split("standard:", 1)[1].split("dropEntry:", 1)[0] if "standard:" in layout_text else layout_text
    alignment = "bottom" if "columnAlignment: 'bottom'" in standard_block else (
        "top" if "columnAlignment: 'top'" in standard_block else "center"
    )
    first_visible_row = visible_row_start(max_rows, visible_rows, alignment)
    expected_positions = [first_visible_row + col * max_rows for col in range(3)]
    expected_pattern = r"\s*,\s*".join(str(pos) for pos in expected_positions)
    symbol_effect_mode = re.search(
        r"case\s+['\"]symboleffect['\"]\s*:[\s\S]*?AwardDataVec\s*:\s*\[[\s\S]*?"
        rf"EliminatePos\s*:\s*\[\s*{expected_pattern}\s*\][\s\S]*?break\s*;",
        gv,
    )
    results.append(check(
        "Mock_symbol_effect_data",
        symbol_effect_mode is not None,
        f"symboleffect mode must use fixed MAX_ROW IDs for the MG-visible cells; expected EliminatePos {expected_positions}",
    ))
    key_5_symbol_effect = re.search(
        r"case\s+KeyCode\.DIGIT_5\s*:[\s\S]*?MOCK_MODE\s*=\s*['\"]symboleffect['\"]",
        gv,
    )
    results.append(check(
        "Mock_key_5_symbol_effect",
        key_5_symbol_effect is not None,
        "DIGIT_5 must select symboleffect mock mode",
    ))
    key_7_jackpot = re.search(
        r"case\s+KeyCode\.DIGIT_7\s*:[\s\S]*?MOCK_MODE\s*=\s*['\"]jackpot['\"]",
        gv,
    )
    results.append(check(
        "Mock_key_7_jackpot",
        key_7_jackpot is not None,
        "DIGIT_7 must preserve jackpot mock mode",
    ))

    # SCATTER_SYMBOL must be single enum member (Symbol.XXX), not array or bare number
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


def gate_3_3(target: Path) -> list:
    """Proto runtime/type bridge + Mock schema contract."""
    errors = check_proto_contract(target)
    if errors:
        return [check("proto_contract", False, "; ".join(errors))]
    return [check("proto_contract", True)]


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


def gate_h1(target: Path) -> list:
    gd_path = target / "assets" / "Script" / "Game_Define.ts"
    gd = gd_path.read_text(encoding="utf-8-sig") if gd_path.exists() else ""
    effect_plate_path = target / "assets" / "Script" / "EffectPlate" / "EffectPlate.ts"
    effect_plate = effect_plate_path.read_text(encoding="utf-8-sig") if effect_plate_path.exists() else ""
    slot_reels_path = target / "assets" / "Script" / "SlotReels.ts"
    slot_reels = slot_reels_path.read_text(encoding="utf-8-sig") if slot_reels_path.exists() else ""
    layout_path = target / "assets" / "Script" / "ReelLayoutConfig.ts"
    layout = layout_path.read_text(encoding="utf-8-sig") if layout_path.exists() else ""
    live_symbol_position = (
        "GetSingleCellFromColRow(col, row)?.ThisNode" in effect_plate
        and "symbolNode.getWorldPosition()" in effect_plate
        and "worldPosition.y -= Game_Define.SymbolHeight" not in effect_plate
    )
    results = [check(
        "symbol_effect_live_position",
        live_symbol_position,
        "EffectPlate.GetSymbolWorldPos must use the current SingleCell world position without a coordinate offset workaround",
    )]
    results.append(check(
        "runtime_layout_position_mapping",
        "boardRowAlignment" not in layout
        and "GetVisibleRowStart" in slot_reels
        and "Math.floor(position / Game_Define.MAX_ROW)" in slot_reels
        and "position % Game_Define.MAX_ROW" in slot_reels
        and "col * Game_Define.MAX_ROW + row" in slot_reels
        and "this.RebuildMiddleSymbolEmptyNodes();" in slot_reels,
        "SlotReels must use fixed MAX_ROW IDs for the maximum physical Layout and rebuild EmptyNodes after layout changes",
    ))
    results.append(check(
        "effect_position_uses_layout_api",
        "SlotReels.GetColRowFromPosition(pos)" in effect_plate
        and "SlotReels.GetPositionFromColRow(col, row)" in effect_plate
        and "pos / Game_Define.MAX_ROW" not in effect_plate,
        "EffectPlate must delegate position conversion to the active ReelLayout",
    ))
    results.append(check(
        "layout_alignment_controls_visible_window",
        "visibleRowAlignment" not in layout
        and "GetVisibleRowStart" in slot_reels
        and "visibleWindowOffset" in slot_reels
        and "this.m_layoutConfig.columnAlignment" in slot_reels,
        "Use the existing columnAlignment parameter for top/center/bottom visible-window alignment",
    ))
    row_match = re.search(r"static\s+ROW\s*=\s*(\d+)", gd)
    visible_rows = int(row_match.group(1)) if row_match else 0
    max_row_match = re.search(r"static\s+MAX_ROW\s*=\s*(\d+)", gd)
    max_rows = int(max_row_match.group(1)) if max_row_match else visible_rows
    results.append(check(
        "standard_layout_from_game_define",
        "length: Game_Define.COL" in layout
        and "targetSymbolCount: Game_Define.MAX_ROW" in layout
        and "visibleSymbolCount: Game_Define.ROW" in layout
        and "expanded:" not in layout
        and "boardRowAlignment" not in layout,
        "standard must build MAX_ROW physical cells and expose ROW visible cells; expansion reuses that layout",
    ))
    try:
        changed, symbol_count = check_symbol_effect_bindings(target, check_only=True)
        results.append(check(
            "symbol_effect_prefab_bindings",
            not changed,
            f"SymbolEffect PNG, atlas, Spine JSON bounds, template, and SymbolEffect_00..{symbol_count - 1:02d} must be 178x178; prefabs must keep BaseSpine and matching SymbolSpine",
        ))
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        results.append(check("symbol_effect_prefab_bindings", False, str(exc)))
    return results


def gate_5_tsc(target: Path) -> list:
    """TypeScript compilation check"""
    result = check_typescript_compile(target)
    errors = result["errors"]
    detail_parts = []
    if result["compiler"]:
        detail_parts.append(result["compiler"])
    if result["ignored_errors"]:
        detail_parts.append(f"ignored external declarations={result['ignored_errors']}")
    if errors:
        detail_parts.extend(errors[:5])
    return [check("tsc_project_sources", not errors, "; ".join(detail_parts))]


def gate_regression(target: Path) -> list:
    """Spec-to-client regression. FAIL and missing evidence (SKIP) both block."""
    spec = target / "scratch" / "Game_Spec.md"
    results = run_regression(spec, target, target.name)
    return [
        check(
            result.name,
            result.status in {"PASS", "WARN"},
            f"{result.status}: {result.message}"
            + (f"; {'; '.join(result.details)}" if result.details else ""),
            "warning" if result.status == "WARN" else "error",
        )
        for result in results
    ]


def gate_traceability(target: Path) -> list:
    """Require codegen-owned evidence while keeping M2+ items explicitly deferred."""
    spec = target / "scratch" / "Game_Spec.md"
    if not spec.exists():
        return [check("traceability", False, f"missing {spec}")]
    spec_ids = extract_spec_ids(spec)
    if not spec_ids:
        return [check(
            "traceability",
            True,
            "WARN: no [SPEC:*] tags found; run tag-spec and report as unfinished",
            "warning",
        )]
    manifest = write_manifest(spec, target, target / "scratch" / "codegen-traceability.json")
    summary = manifest["summary"]
    uncovered = [
        item["id"] for item in manifest["items"]
        if item["scope"] == "codegen" and item["status"] == "uncovered"
    ]
    scoped_detail = (
        f"codegen {summary['codegen_covered']}/{summary['codegen_total']} covered; "
        f"deferred M2+ {summary['deferred_total']}; "
        f"inferred defaults {summary['inferred_verified']}/{summary['inferred_total']} verified; "
        f"informational {summary['informational_total']}"
    )
    if uncovered:
        preview = ", ".join(uncovered[:10])
        return [check(
            "traceability",
            False,
            f"{scoped_detail}; uncovered codegen IDs: {preview}",
        )]
    return [check("traceability", True, scoped_detail)]


REPORT_HEADINGS = (
    "## 無頭階段完成項目",
    "## Gate 結果",
    "## 後續未完成工項",
    "## 已知風險",
)


def gate_report(target: Path) -> list:
    """Validate the handoff report before checkpoint cleanup."""
    report = target / "scratch" / "codegen-report.md"
    if not report.exists():
        return [check("report_exists", False, f"missing {report}")]
    content = report.read_text(encoding="utf-8", errors="ignore")
    results = [check(f"report_heading:{heading[3:]}", heading in content) for heading in REPORT_HEADINGS]
    has_scoped_traceability = (
        "codegen" in content and "deferred M2+" in content and "inferred defaults" in content
    )
    results.append(check(
        "report_scoped_traceability",
        has_scoped_traceability,
        "Gate 結果 must include codegen, deferred M2+, and inferred defaults counts",
    ))
    unfinished = content.split("## 後續未完成工項", 1)
    has_unfinished = len(unfinished) == 2 and "- [ ]" in unfinished[1].split("\n## ", 1)[0]
    results.append(check("report_unfinished_checklist", has_unfinished, "requires at least one '- [ ]' item"))
    return results


PRE_FINALIZE_GATES = (
    ("bom", gate_bom),
    ("3.2", gate_3_2),
    ("3.3", gate_3_3),
    ("3.4", gate_3_4),
    ("3.10", gate_3_10),
    ("H1", gate_h1),
    ("5", gate_5_tsc),
    ("regression", gate_regression),
    ("traceability", gate_traceability),
)


def _aggregate(target: Path, gates) -> list:
    results = []
    for step, gate in gates:
        for item in gate(target):
            item = dict(item)
            item["name"] = f"{step}:{item['name']}"
            results.append(item)
    return results


def gate_prefinalize(target: Path) -> list:
    return _aggregate(target, PRE_FINALIZE_GATES)


def gate_finalize(target: Path) -> list:
    return gate_prefinalize(target) + _aggregate(target, (("report", gate_report),))


GATES = {
    "bom": gate_bom,
    "3.2": gate_3_2,
    "3.3": gate_3_3,
    "3.4": gate_3_4,
    "3.10": gate_3_10,
    "H1": gate_h1,
    "5": gate_5_tsc,
    "regression": gate_regression,
    "traceability": gate_traceability,
    "report": gate_report,
    "prefinalize": gate_prefinalize,
    "finalize": gate_finalize,
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
        steps_to_run = [step for step, _ in PRE_FINALIZE_GATES] + ["report"]
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    main()
