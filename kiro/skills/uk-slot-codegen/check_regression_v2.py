"""
slot-codegen-regression-check / check_regression_v2.py
=====================================================

V2 regression harness: validates codegen output against Game_Spec.md.
Checks that the actual client matches what codegen SHOULD produce from the spec.

Usage:
    py check_regression_v2.py --spec <Game_Spec.md> --client <client-root>
    py check_regression_v2.py --all   # runs all 3 known fixtures

Exit codes: 0=PASS/WARN, 1=FAIL or required evidence SKIP, 2=usage error, 3=path missing
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
    def find_number(label: str) -> int | None:
        match = re.search(
            rf"(?<![A-Za-z0-9_])(?:\*\*)?{label}(?:\*\*)?\s*[:=]\s*(\d+)",
            text,
            re.IGNORECASE,
        )
        return int(match.group(1)) if match else None

    # COL/ROW
    col = find_number("COL")
    if col is not None: spec["COL"] = col
    row = find_number("ROW")
    if row is not None: spec["ROW"] = row
    # BoardLayout supports ASCII/Unicode separators and multiple named modes,
    # e.g. 3×3×3×3×3（MG）/ 5×5×5×5×5（FG EXPAND）.
    m = re.search(
        r"(?:\*\*)?BoardLayout(?:\*\*)?\s*[:=]\s*([^\r\n]+)",
        text,
        re.IGNORECASE,
    )
    if m:
        layouts = []
        for encoded in re.findall(r"\d+(?:\s*[x×]\s*\d+)+", m.group(1), re.IGNORECASE):
            layouts.append([int(value) for value in re.split(r"\s*[x×]\s*", encoded)])
        if layouts:
            spec["BoardLayouts"] = layouts
            spec["BoardLayout"] = "x".join(map(str, layouts[0]))
    # ROW_CONFIG (format: [5,4,4,4,4,5])
    if "BoardLayout" not in spec:
        m = re.search(r"ROW_CONFIG\s*[:=]\s*\[([^\]]+)\]", text)
        if m:
            nums = [x.strip() for x in m.group(1).split(",") if x.strip().isdigit()]
            if nums:
                spec["BoardLayout"] = "x".join(nums)
                spec["BoardLayouts"] = [[int(value) for value in nums]]
    # FULL_PLATE_NUM
    full_plate_num = find_number("FULL_PLATE_NUM")
    if full_plate_num is not None: spec["FULL_PLATE_NUM"] = full_plate_num
    # If no FULL_PLATE_NUM but have BoardLayout, compute it
    if "FULL_PLATE_NUM" not in spec and "BoardLayout" in spec:
        rows = [int(x) for x in spec["BoardLayout"].split("x")]
        spec["FULL_PLATE_NUM"] = sum(rows)
    # Symbols - preserve SymID and exclude rows explicitly marked server_only
    # from the client contract. Server-only IDs belong to the protocol/spec but
    # do not need a client enum member or SymbolEffect prefab.
    sym_section = re.search(
        r"##\s*(?:\d+\.\s*)?(?:Symbol|圖騰).*?\n(.*?)(?=\n##|\Z)",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if sym_section:
        symbols = []
        for line in sym_section.group(1).splitlines():
            if not re.match(r"^\|\s*\d+\s*\|", line):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            sym_id = int(cells[0])
            marker_text = " ".join(cells[2:])
            server_only = bool(
                re.search(r"server[_\s-]*only|server\s*用|伺服器", marker_text, re.IGNORECASE)
            )
            symbols.append({"id": sym_id, "name": cells[1], "server_only": server_only})
        if symbols:
            client_symbols = [symbol for symbol in symbols if not symbol["server_only"]]
            spec["symbols"] = symbols
            spec["symbol_ids"] = [symbol["id"] for symbol in client_symbols]
            spec["server_only_symbol_ids"] = [
                symbol["id"] for symbol in symbols if symbol["server_only"]
            ]
            spec["symbol_count"] = len(client_symbols)
            spec["total_symbol_count"] = len(symbols)
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

    # Symbol enum members and their numeric TypeScript enum values.
    em = re.search(r"export\s+enum\s+Symbol\s*\{([^}]+)\}", text, re.DOTALL)
    if em:
        body = em.group(1)
        symbols = []
        next_value = 0
        for line in body.splitlines():
            s = line.strip()
            if not s or s.startswith("//") or s.startswith("/*") or s.startswith("*"):
                continue
            token = s.rstrip(",").split("//")[0].strip()
            member = re.match(r"^([A-Za-z_]\w*)(?:\s*=\s*(-?\d+))?$", token)
            if not member:
                continue
            if member.group(2) is not None:
                next_value = int(member.group(2))
            symbols.append({"name": member.group(1), "id": next_value})
            next_value += 1
        result["symbols"] = symbols
        result["symbol_ids"] = [symbol["id"] for symbol in symbols]
        result["symbol_count"] = len(symbols)

    m = re.search(r"static\s+SYMBOL_COUNT\s*=\s*(\d+)", text)
    if m:
        result["SYMBOL_COUNT"] = int(m.group(1))

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
    elif re.search(
        r"NORMAL_COLUMNS\s*=\s*Array\.from\s*\(\s*\{\s*length\s*:\s*Game_Define\.COL\s*\}",
        text,
    ):
        result["NORMAL_COLUMNS_from_col"] = True

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
    """Verify the client Symbol enum against non-server-only spec SymIDs."""
    expected = spec.get("symbol_count")
    actual = client_gd.get("symbol_count")
    if expected is None:
        return CheckResult("symbol_count", "SKIP", "spec has no symbol table")
    if actual is None:
        return CheckResult("symbol_count", "SKIP", "client has no Symbol enum")
    expected_ids = spec.get("symbol_ids")
    actual_ids = client_gd.get("symbol_ids")
    if expected_ids is not None and actual_ids is not None:
        issues = []
        missing = sorted(set(expected_ids) - set(actual_ids))
        unexpected = sorted(set(actual_ids) - set(expected_ids))
        symbol_names = {symbol["id"]: symbol["name"] for symbol in spec.get("symbols", [])}
        if missing:
            labels = ", ".join(f"{sym_id} ({symbol_names.get(sym_id, '?')})" for sym_id in missing)
            issues.append(f"missing client SymID: {labels}")
        if unexpected:
            issues.append(f"unexpected client SymID: {', '.join(map(str, unexpected))}")
        if len(actual_ids) != len(set(actual_ids)):
            issues.append(f"duplicate client SymID values: {actual_ids}")

        declared_count = client_gd.get("SYMBOL_COUNT")
        if declared_count is not None and declared_count != actual:
            issues.append(f"SYMBOL_COUNT={declared_count}, but enum has {actual} members")

        if issues:
            return CheckResult("symbol_count", "FAIL", f"{len(issues)} symbol contract mismatch", issues)
        server_only = spec.get("server_only_symbol_ids", [])
        return CheckResult(
            "symbol_count",
            "PASS",
            f"client IDs={actual_ids}; server-only excluded={server_only}",
        )

    # Backward-compatible fallback for legacy spec formats without SymID rows.
    if actual >= expected:
        return CheckResult("symbol_count", "PASS", f"client={actual} >= spec={expected}")
    return CheckResult("symbol_count", "FAIL", f"client={actual} < spec={expected} (missing symbols)")


def check_normal_columns(spec: dict, client_sr: dict) -> CheckResult:
    """Verify NORMAL_COLUMNS length = COL."""
    col = spec.get("COL")
    nc_len = client_sr.get("NORMAL_COLUMNS_len")
    if col is None:
        return CheckResult("normal_columns", "SKIP", "cannot get COL or NORMAL_COLUMNS")
    if client_sr.get("NORMAL_COLUMNS_from_col"):
        return CheckResult("normal_columns", "PASS", "NORMAL_COLUMNS derived from Game_Define.COL")
    if nc_len is None:
        return CheckResult("normal_columns", "SKIP", "cannot get COL or NORMAL_COLUMNS")
    if col == nc_len:
        return CheckResult("normal_columns", "PASS", f"NORMAL_COLUMNS.length={nc_len} = COL")
    return CheckResult("normal_columns", "FAIL", f"COL={col} but NORMAL_COLUMNS.length={nc_len}")


def check_variable_board(spec: dict, client_gd: dict, client_sr: dict, client_prefab: dict) -> CheckResult:
    """Verify variable board layout handling."""
    layouts = spec.get("BoardLayouts")
    if not layouts and spec.get("BoardLayout"):
        layouts = [[int(value) for value in spec["BoardLayout"].split("x")]]
    if not layouts:
        return CheckResult("variable_board", "SKIP", "spec has no BoardLayout")

    board = " / ".join("x".join(map(str, layout)) for layout in layouts)
    issues = []
    col = spec.get("COL")
    if col is not None:
        bad_lengths = [layout for layout in layouts if len(layout) != col]
        if bad_lengths:
            issues.append(f"BoardLayout column count != COL={col}: {bad_lengths}")

    base_row = spec.get("ROW")
    if base_row is not None and any(value != base_row for value in layouts[0]):
        issues.append(f"base BoardLayout={layouts[0]} does not match ROW={base_row}")

    max_row = client_gd.get("MAX_ROW")
    expected_max_row = max(max(layout) for layout in layouts)
    if max_row is not None and max_row != expected_max_row:
        issues.append(f"MAX_ROW={max_row}, BoardLayouts max={expected_max_row}")

    has_per_column_variation = any(len(set(layout)) > 1 for layout in layouts)

    if not has_per_column_variation:
        if issues:
            return CheckResult("variable_board", "FAIL", f"uniform board {board}: {len(issues)} issues", issues)
        if client_sr.get("mask_type") == "single":
            label = "multi-mode uniform" if len(layouts) > 1 else "uniform"
            return CheckResult("variable_board", "PASS", f"{label} layouts {board}, single Mask ok")
        elif client_sr.get("mask_type") == "array":
            label = "multi-mode uniform" if len(layouts) > 1 else "uniform"
            return CheckResult("variable_board", "PASS", f"{label} layouts {board}, array Mask ok")
        return CheckResult("variable_board", "SKIP", "cannot determine mask type")

    # Variable board — must have per-column mask
    if client_sr.get("mask_type") != "array":
        issues.append("SlotReels should use m_reelMasks[], actual uses m_reelMask single ref")
    if not client_sr.get("has_reel_mask_columns"):
        issues.append("SlotReels missing REEL_MASK_COLUMNS mapping")

    # Check ROW_CONFIG
    rows = layouts[0]
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
        if r.status in {"FAIL", "SKIP"}:
            any_fail = True
    return any_fail


def has_blocking_results(results: list[CheckResult]) -> bool:
    """Required regression evidence may PASS or WARN; FAIL/SKIP blocks finalize."""
    return any(result.status in {"FAIL", "SKIP"} for result in results)


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
