"""
slot-codegen-regression-check / check_regression_v2.py
=====================================================

V2 regression harness: validates codegen output against Game_Spec.md.
Checks that the actual client matches what codegen SHOULD produce from the spec.

Usage:
    py check_regression_v2.py --spec <Game_Spec.md> --client <client-root>
    py check_regression_v2.py --all   # runs all 3 known fixtures

Exit codes: 0=PASS, 1=FAIL, 2=usage error, 3=path missing
"""
from __future__ import annotations
import argparse, re, sys, json
from pathlib import Path


# ---------------------------------------------------------------------------
# Spec parser
# ---------------------------------------------------------------------------

def parse_game_spec(text: str) -> dict:
    """Extract key values from Game_Spec.md."""
    spec = {}
    # COL/ROW
    m = re.search(r"COL\s*[:=]\s*(\d+)", text)
    if m: spec["COL"] = int(m.group(1))
    m = re.search(r"(?:MAX_)?ROW\s*[:=]\s*(\d+)", text)
    if m: spec["ROW"] = int(m.group(1))
    # BoardLayout (format: 5x4x4x4x4x5)
    m = re.search(r"BoardLayout\s*[:=]\s*([\dx]+)", text)
    if m: spec["BoardLayout"] = m.group(1)
    # ROW_CONFIG (format: [5,4,4,4,4,5])
    if "BoardLayout" not in spec:
        m = re.search(r"ROW_CONFIG\s*[:=]\s*\[([^\]]+)\]", text)
        if m:
            nums = [x.strip() for x in m.group(1).split(",") if x.strip().isdigit()]
            if nums:
                spec["BoardLayout"] = "x".join(nums)
    # FULL_PLATE_NUM
    m = re.search(r"FULL_PLATE_NUM\s*[:=]\s*(\d+)", text)
    if m: spec["FULL_PLATE_NUM"] = int(m.group(1))
    # If no FULL_PLATE_NUM but have BoardLayout, compute it
    if "FULL_PLATE_NUM" not in spec and "BoardLayout" in spec:
        rows = [int(x) for x in spec["BoardLayout"].split("x")]
        spec["FULL_PLATE_NUM"] = sum(rows)
    # Symbols - count lines in Symbol table
    sym_section = re.search(r"##\s*(?:\d+\.\s*)?Symbol.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
    if sym_section:
        rows = re.findall(r"^\|\s*\d+\s*\|", sym_section.group(1), re.MULTILINE)
        if rows: spec["symbol_count"] = len(rows)
    # Also try: count rows in any table under "圖騰" section
    if "symbol_count" not in spec:
        sym_section = re.search(r"##\s*(?:\d+\.\s*)?(?:Symbol|圖騰).*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if sym_section:
            rows = re.findall(r"^\|\s*\d+\s*\|", sym_section.group(1), re.MULTILINE)
            if rows: spec["symbol_count"] = len(rows)
    # PayMode
    m = re.search(r"PayMode\s*[:=]\s*(\w+)", text)
    if m: spec["PayMode"] = m.group(1)
    # SpinMode
    m = re.search(r"SpinMode\s*[:=]\s*(\w+)", text)
    if m: spec["SpinMode"] = m.group(1)
    return spec


# ---------------------------------------------------------------------------
# Client parser
# ---------------------------------------------------------------------------

def parse_client_game_define(client: Path) -> dict:
    """Extract values from client's Game_Define.ts."""
    result = {}
    gd = client / "assets" / "Script" / "Game_Define.ts"
    if not gd.exists():
        gd = client / "assets" / "game" / "Script" / "Game_Define.ts"
    if not gd.exists():
        return result
    text = gd.read_text(encoding="utf-8")

    m = re.search(r"static\s+COL\s*=\s*(\d+)", text)
    if m: result["COL"] = int(m.group(1))
    m = re.search(r"static\s+ROW\s*=\s*(\d+)", text)
    if m: result["ROW"] = int(m.group(1))
    m = re.search(r"static\s+FULL_PLATE_NUM\s*=\s*(\d+)", text)
    if m: result["FULL_PLATE_NUM"] = int(m.group(1))
    m = re.search(r"static\s+MAX_ROW\s*=\s*(\d+)", text)
    if m: result["MAX_ROW"] = int(m.group(1))

    # Symbol enum count
    em = re.search(r"export\s+enum\s+Symbol\s*\{([^}]+)\}", text, re.DOTALL)
    if em:
        body = em.group(1)
        count = 0
        for line in body.splitlines():
            s = line.strip()
            if not s or s.startswith("//") or s.startswith("/*") or s.startswith("*"):
                continue
            token = s.rstrip(",").split("//")[0].strip()
            if token and re.match(r"^[A-Za-z_]\w*(\s*=\s*\d+)?$", token):
                count += 1
        result["symbol_count"] = count

    # ROW_CONFIG
    m = re.search(r"static\s+ROW_CONFIG\s*=\s*\[([^\]]+)\]", text)
    if m:
        nums = [int(x.strip()) for x in m.group(1).split(",") if x.strip().isdigit()]
        result["ROW_CONFIG"] = nums

    return result


def parse_client_slot_reels(client: Path) -> dict:
    """Extract reel config from SlotReels.ts."""
    result = {}
    sr = client / "assets" / "Script" / "SlotReels.ts"
    if not sr.exists():
        return result
    text = sr.read_text(encoding="utf-8")

    # NORMAL_COLUMNS length
    m = re.search(r"NORMAL_COLUMNS\s*=\s*\[([^\]]+)\]", text)
    if m:
        items = [x.strip() for x in m.group(1).split(",") if x.strip()]
        result["NORMAL_COLUMNS_len"] = len(items)

    # m_reelMasks vs m_reelMask
    if "m_reelMasks" in text:
        result["mask_type"] = "array"
    elif "m_reelMask" in text:
        result["mask_type"] = "single"

    # REEL_MASK_COLUMNS
    m = re.search(r"REEL_MASK_COLUMNS\s*=\s*\[", text)
    result["has_reel_mask_columns"] = bool(m)

    return result


def parse_client_prefab(client: Path) -> dict:
    """Check SlotPlate_MG.prefab structure."""
    result = {}
    prefab = client / "assets" / "game" / "Prefab" / "Reel" / "SlotPlate_MG.prefab"
    if not prefab.exists():
        return result
    text = prefab.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return result

    # Count Mask child nodes
    mask_nodes = [n for n in data if isinstance(n, dict)
                  and n.get("__type__") == "cc.Node"
                  and "Mask" in n.get("_name", "")]
    result["mask_node_count"] = len(mask_nodes)
    result["mask_names"] = [n["_name"] for n in mask_nodes]

    return result


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self, name: str, status: str, message: str, details: list[str] | None = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or []


def check_col_row(spec: dict, client_gd: dict) -> CheckResult:
    """Verify COL/ROW/FULL_PLATE_NUM match."""
    issues = []
    for key in ["COL", "ROW"]:
        expected = spec.get(key)
        actual = client_gd.get(key)
        if expected is None:
            continue
        if actual is None:
            issues.append(f"{key}: spec={expected}, client=not found")
        elif expected != actual:
            issues.append(f"{key}: spec={expected}, client={actual}")
    # FULL_PLATE_NUM: if client doesn't have it, infer from COL*ROW
    fp_expected = spec.get("FULL_PLATE_NUM")
    fp_actual = client_gd.get("FULL_PLATE_NUM")
    if fp_expected is not None:
        if fp_actual is not None and fp_actual != fp_expected:
            issues.append(f"FULL_PLATE_NUM: spec={fp_expected}, client={fp_actual}")
        elif fp_actual is None:
            # Infer: if COL*ROW == FULL_PLATE_NUM, it's fine (equal-width board)
            col = client_gd.get("COL", 0)
            row = client_gd.get("ROW", 0)
            if col * row != fp_expected:
                issues.append(f"FULL_PLATE_NUM: spec={fp_expected}, client missing (COL*ROW={col*row})")
    if issues:
        return CheckResult("col_row", "FAIL", f"{len(issues)} mismatch", issues)
    return CheckResult("col_row", "PASS", "COL/ROW/FULL_PLATE_NUM consistent")


def check_symbol_count(spec: dict, client_gd: dict) -> CheckResult:
    """Verify symbol enum count."""
    expected = spec.get("symbol_count")
    actual = client_gd.get("symbol_count")
    if expected is None:
        return CheckResult("symbol_count", "SKIP", "spec has no symbol table")
    if actual is None:
        return CheckResult("symbol_count", "SKIP", "client has no Symbol enum")
    if actual >= expected:
        return CheckResult("symbol_count", "PASS", f"client={actual} >= spec={expected}")
    return CheckResult("symbol_count", "FAIL", f"client={actual} < spec={expected} (missing symbols)")


def check_normal_columns(spec: dict, client_sr: dict) -> CheckResult:
    """Verify NORMAL_COLUMNS length = COL."""
    col = spec.get("COL")
    nc_len = client_sr.get("NORMAL_COLUMNS_len")
    if col is None or nc_len is None:
        return CheckResult("normal_columns", "SKIP", "cannot get COL or NORMAL_COLUMNS")
    if col == nc_len:
        return CheckResult("normal_columns", "PASS", f"NORMAL_COLUMNS.length={nc_len} = COL")
    return CheckResult("normal_columns", "FAIL", f"COL={col} but NORMAL_COLUMNS.length={nc_len}")


def check_variable_board(spec: dict, client_gd: dict, client_sr: dict, client_prefab: dict) -> CheckResult:
    """Verify variable board layout handling."""
    board = spec.get("BoardLayout")
    if not board:
        return CheckResult("variable_board", "SKIP", "spec has no BoardLayout")

    rows = [int(x) for x in board.split("x")]
    is_variable = len(set(rows)) > 1

    if not is_variable:
        if client_sr.get("mask_type") == "single":
            return CheckResult("variable_board", "PASS", f"equal-width {board}, single Mask ok")
        elif client_sr.get("mask_type") == "array":
            return CheckResult("variable_board", "PASS", f"equal-width {board}, array Mask ok")
        return CheckResult("variable_board", "SKIP", "cannot determine mask type")

    # Variable board — must have per-column mask
    issues = []
    if client_sr.get("mask_type") != "array":
        issues.append("SlotReels should use m_reelMasks[], actual uses m_reelMask single ref")
    if not client_sr.get("has_reel_mask_columns"):
        issues.append("SlotReels missing REEL_MASK_COLUMNS mapping")

    # Check ROW_CONFIG
    row_config = client_gd.get("ROW_CONFIG")
    if row_config:
        if row_config != rows:
            issues.append(f"ROW_CONFIG={row_config}, spec BoardLayout={rows}")
    else:
        issues.append("Game_Define missing ROW_CONFIG")

    # Check prefab mask count
    mask_count = client_prefab.get("mask_node_count", 0)
    if mask_count < 3:
        issues.append(f"Prefab has {mask_count} Mask nodes, variable board needs >=3")

    if issues:
        return CheckResult("variable_board", "FAIL", f"variable board {board}: {len(issues)} issues", issues)
    return CheckResult("variable_board", "PASS", f"variable board {board} per-column Mask correct")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

FIXTURES = [
    ("三幣瑞龍", Path("E:/UK/uk_slot_tct_test/scratch/Game_Spec.md"), Path("E:/UK/uk_slot_tct_test")),
    ("Eye Strike", Path("E:/UK/uk_slot_eye_strike_new/scratch/Game_Spec.md"), Path("E:/UK/uk_slot_eye_strike_new")),
    ("海盜女王", Path("E:/UK/uk_slot_pirate_test/scratch/Game_Spec.md"), Path("E:/UK/uk_slot_pirate_test")),
]


def run_one(spec_path: Path, client_root: Path, label: str = "") -> list[CheckResult]:
    if not spec_path.exists():
        return [CheckResult("preflight", "FAIL", f"Game_Spec.md not found: {spec_path}")]
    if not client_root.exists():
        return [CheckResult("preflight", "FAIL", f"client not found: {client_root}")]

    spec_text = spec_path.read_text(encoding="utf-8")
    spec = parse_game_spec(spec_text)
    client_gd = parse_client_game_define(client_root)
    client_sr = parse_client_slot_reels(client_root)
    client_prefab = parse_client_prefab(client_root)

    return [
        check_col_row(spec, client_gd),
        check_symbol_count(spec, client_gd),
        check_normal_columns(spec, client_sr),
        check_variable_board(spec, client_gd, client_sr, client_prefab),
    ]


def print_results(label: str, results: list[CheckResult]) -> bool:
    print(f"\n{'─'*50}")
    print(f"  {label}")
    print(f"{'─'*50}")
    any_fail = False
    for r in results:
        icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭", "WARN": "⚠️"}[r.status]
        print(f"  {icon} {r.name}: {r.message}")
        for d in r.details:
            print(f"       {d}")
        if r.status == "FAIL":
            any_fail = True
    return any_fail


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Slot codegen regression check v2")
    ap.add_argument("--spec", type=Path, help="Game_Spec.md path")
    ap.add_argument("--client", type=Path, help="client project root")
    ap.add_argument("--all", action="store_true", help="run all 3 known fixtures")
    args = ap.parse_args(argv)

    if args.all:
        any_fail = False
        for label, spec, client in FIXTURES:
            results = run_one(spec, client, label)
            if print_results(label, results):
                any_fail = True
        print(f"\n{'═'*50}")
        print(f"  OVERALL: {'FAIL' if any_fail else 'ALL PASS'}")
        print(f"{'═'*50}")
        return 1 if any_fail else 0
    elif args.spec and args.client:
        results = run_one(args.spec, args.client)
        return 1 if print_results(str(args.client.name), results) else 0
    else:
        ap.print_help()
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    sys.exit(main())
