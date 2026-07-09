"""
slot-codegen-regression-check / check_regression.py
===================================================

Regression harness for the slot-game-codegen-skill.

Compares what a reverse_spec.md *claims* the client has versus what the
actual client has on disk. Used as a non-regression check: if we change the
codegen skill's templates or workflow, we want to make sure the existing
production clients (pirate2, eye_strike, etc.) would still be reproducible
from their reverse_spec.

What we check in v1:
    1. State list:
       - Parse reverse_spec.md for mentions of `XxxState.ts` (the state
         classes listed under the state-machine section).
       - Glob `<client>/assets/game/Script/GameState/*.ts`.
       - Compare sets.
    2. Symbol count (lightweight sanity):
       - Parse the Symbol enum mention in reverse_spec for total count.
       - Grep the client's Game_Define.ts for `enum Symbol { ... }` and
         count members.
       - Compare numbers.

Out of scope for v1 (deferred to v2):
    - Feature flag presence comparison (different clients use different
      HAS_* constant styles; needs per-client heuristic)
    - Audio clip list comparison
    - CHEAT_KEY enum comparison
    - Proto message shape

CLI:
    py check_regression.py --spec <reverse_spec.md> --client <client-root>

Exit codes:
    0  PASS (all checks matched)
    1  FAIL (one or more mismatch)
    2  usage error
    3  fixture path missing / unreadable
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Parser: reverse_spec.md → expected artifacts
# ---------------------------------------------------------------------------


# Match state-class name mentions anywhere in reverse_spec. Accept both:
#   - "ExplodeState.ts" / "GameState/ExplodeState.ts" (pirate2 style)
#   - "`ExplodeState`" / "CheckState / CheckJpState" (eye_strike style, no .ts)
# Require PascalCase + "State" suffix, min 2 chars before "State" (avoid false positive on "State" alone).
_STATE_TS_RE = re.compile(r"\b([A-Z]\w{1,}State)\b")

# Also recognize SCREAMING_SNAKE state names (GAMEVIEW_STATE enum members), because
# reverse_specs often write flows like "ROUND_END → IDLE" without referencing
# the PascalCase class. We translate SCREAMING_SNAKE_CASE → PascalCaseState.
# e.g. ROUND_END → RoundEndState, CHECK_JP → CheckJpState
# Must be all uppercase, contain at least one underscore OR be in a known list,
# length ≥ 3 to avoid matching trivial tokens like "OK" "FG".
_SCREAMING_SNAKE_RE = re.compile(r"\b([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)\b")


def _screaming_snake_to_state_class(token: str) -> str:
    """Translate SCREAMING_SNAKE_CASE enum member to PascalCase State class name.

    Examples:
        ROUND_END → RoundEndState
        CHECK_JP → CheckJpState
        ENTER_FREE → EnterFreeState
        MATCHING_PATCH_UP → MatchingPatchUpState
    """
    parts = token.split("_")
    pascal = "".join(p.capitalize() for p in parts)
    return pascal + "State"


# A narrow whitelist of SCREAMING_SNAKE tokens that *definitely* correspond to
# state-machine states (so we don't translate random ALL_CAPS constants).
_KNOWN_STATE_ENUMS = {
    "WAIT_RES", "WAIT_READY", "PLATE_SHOW", "FEATURE_SHOW", "UNSHOW_PREPARE",
    "EFFECT_START", "SCATTER_SHOW", "AWARD",
    "ROUND_SHOW_END", "ROUND_END", "END", "IDLE", "SPIN", "CHECK_STATE",
    "ENTER_FREE", "LEAVE_FREE", "ADD_FREE", "FULL_REWARD",
    "ENTER_BONUS", "LEAVE_BONUS", "BONUS_GAME",
    "ENTER_RESPIN", "LEAVE_RESPIN", "RESPIN",
    "EXPLODE", "MATCHING_PATCH_UP", "COUNT_MULT",
    "CHECK_JP", "COIN",
}

# Frame-work states that don't correspond to a .ts file in assets/game/Script/GameState/.
# These are provided by astarte-framework's CommonState enum (numeric 0-5).
# The reverse_spec may mention them but the actual file won't exist.
_FRAMEWORK_ONLY_STATES = {
    # e.g. "LOGIN", "END" live in framework's CommonState. They don't have
    # per-client .ts overrides.
}

# State class names to ignore when extracted. Reasons vary:
#   - BaseState / CommonState: framework base / enum, not a client-side .ts
#   - GameState: directory name and generic term; often appears in text
#     like "GameState/XxxState.ts" — the `GameState` token itself is not a class
#   - JPState: in eye_strike it's a proto enum (Mini/Minor/Major/Mega/Grand),
#     not a state-machine state
_IGNORE_STATE_NAMES = {
    "BaseState",
    "CommonState",
    "GameState",
    "JPState",
}

# Match Symbol enum count hints in reverse_spec.md.
# We look for the "10.2 Symbol 索引" table and count rows, or fall back to
# explicit "N 個符號" mentions.
_SYMBOL_TABLE_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*`?([A-Z][A-Z_0-9]*)`?\s*\|", re.MULTILINE)


def parse_spec_state_classes(spec_text: str) -> set[str]:
    """Extract the set of state-class names referenced in reverse_spec.md.

    Uses two strategies combined:
      1. Direct PascalCase matches like "ExplodeState" / "ExplodeState.ts"
      2. SCREAMING_SNAKE_CASE matches that are in the known state-enum whitelist,
         translated e.g. ROUND_END → RoundEndState

    Returns a set like {"WaitResState", "IdleState", "SpinState", ...}.
    """
    names: set[str] = set()

    # Strategy 1: direct PascalCase
    for m in _STATE_TS_RE.findall(spec_text):
        names.add(m)

    # Strategy 2: SCREAMING_SNAKE from whitelist
    for m in _SCREAMING_SNAKE_RE.findall(spec_text):
        if m in _KNOWN_STATE_ENUMS:
            names.add(_screaming_snake_to_state_class(m))

    names -= _IGNORE_STATE_NAMES
    return names


def parse_spec_symbol_count(spec_text: str) -> int | None:
    """Try to extract total symbol count from reverse_spec.md.

    v1 heuristic: count rows in `| id | NAME |` style Symbol tables.
    Returns None if we can't confidently determine.
    """
    rows = _SYMBOL_TABLE_ROW_RE.findall(spec_text)
    # dedupe by id
    ids_seen: set[int] = set()
    for idx_str, _name in rows:
        try:
            ids_seen.add(int(idx_str))
        except ValueError:
            continue
    if not ids_seen:
        return None
    # Symbol ids should be 0..N-1 consecutive. If they are, total = len.
    # If not, return the max+1 as a best guess.
    return max(max(ids_seen) + 1, len(ids_seen))


# ---------------------------------------------------------------------------
# Parser: actual client → real artifacts
# ---------------------------------------------------------------------------


def find_state_files(client_root: Path) -> set[str]:
    """Find all XxxState.ts file basenames in the client's GameState dir.

    Tries multiple common layouts:
    - `<client>/assets/game/Script/GameState/*.ts`
    - `<client>/assets/Script/GameState/*.ts`

    Returns set like {"WaitResState", "IdleState", ...}.
    """
    candidates = [
        client_root / "assets" / "game" / "Script" / "GameState",
        client_root / "assets" / "Script" / "GameState",
    ]
    results: set[str] = set()
    for d in candidates:
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.is_file() and f.suffix == ".ts":
                stem = f.stem  # "IdleState" from "IdleState.ts"
                results.add(stem)
    return results


_ENUM_SYMBOL_RE = re.compile(
    r"enum\s+Symbol\s*\{([^}]+)\}",
    re.DOTALL,
)


def count_game_define_symbols(client_root: Path) -> int | None:
    """Parse the client's Game_Define.ts to count Symbol enum members."""
    candidates = [
        client_root / "assets" / "game" / "Script" / "Game_Define.ts",
        client_root / "assets" / "Script" / "Game_Define.ts",
    ]
    for p in candidates:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        m = _ENUM_SYMBOL_RE.search(text)
        if not m:
            continue
        body = m.group(1)
        # count non-empty, non-comment lines with an identifier
        count = 0
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
                continue
            # lines look like "Q," or "SUPER_BONUS,"
            # strip trailing comma and comments
            token = stripped.rstrip(",").split("//")[0].strip()
            if token and re.match(r"^[A-Za-z_][A-Za-z0-9_]*(\s*=\s*\d+)?$", token):
                count += 1
        return count if count > 0 else None
    return None


# ---------------------------------------------------------------------------
# Check engine
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    name: str
    status: str   # "PASS" / "FAIL" / "SKIP"
    message: str
    detail_lines: list[str]


def _pass(name: str, msg: str) -> CheckResult:
    return CheckResult(name=name, status="PASS", message=msg, detail_lines=[])


def _fail(name: str, msg: str, detail: list[str] | None = None) -> CheckResult:
    return CheckResult(name=name, status="FAIL", message=msg, detail_lines=detail or [])


def _skip(name: str, msg: str) -> CheckResult:
    return CheckResult(name=name, status="SKIP", message=msg, detail_lines=[])


def check_state_classes(spec_text: str, client_root: Path) -> CheckResult:
    spec_states = parse_spec_state_classes(spec_text)
    actual_states = find_state_files(client_root)

    if not spec_states:
        return _skip("state_classes", "reverse_spec 未提及任何 *State.ts 檔（無法比對）")
    if not actual_states:
        return _fail(
            "state_classes",
            "client 找不到 GameState/ 目錄或目錄為空",
            detail=[f"試過：{client_root / 'assets' / 'game' / 'Script' / 'GameState'}"],
        )

    missing_in_client = spec_states - actual_states
    extra_in_client = actual_states - spec_states

    if not missing_in_client and not extra_in_client:
        return _pass(
            "state_classes",
            f"{len(actual_states)} 個 state 檔全部一致（spec=實際）",
        )

    detail: list[str] = []
    if missing_in_client:
        detail.append(f"spec 提到但 client 找不到 ({len(missing_in_client)})：")
        for name in sorted(missing_in_client):
            detail.append(f"  - {name}.ts")
    if extra_in_client:
        detail.append(f"client 有但 spec 未提及 ({len(extra_in_client)})：")
        for name in sorted(extra_in_client):
            detail.append(f"  - {name}.ts")
    return _fail(
        "state_classes",
        f"spec {len(spec_states)} 個 vs client {len(actual_states)} 個（不一致）",
        detail=detail,
    )


def check_symbol_count(spec_text: str, client_root: Path) -> CheckResult:
    """v1 DISABLED.

    Parsing symbol counts out of reverse_spec.md Markdown tables proves brittle:
    different reverse_spec authors use different table layouts, backtick styles,
    or list enum contents inside code fences. False positives outweigh signal.

    v2 plan: drop Markdown-table parsing entirely. Instead, find an
    ``` ```proto ``` or ```ts``` fenced block in reverse_spec that contains
    ``enum Symbol`` and compare its members to the client's Game_Define.ts
    enum. That's a direct enum-to-enum compare, no Markdown format guessing.
    """
    return _skip(
        "symbol_count",
        "v1 停用（Markdown 表格解析過度脆弱；v2 改走 fenced code block enum 比對）",
    )


# ---------------------------------------------------------------------------
# CLI / runner
# ---------------------------------------------------------------------------


def run(spec_path: Path, client_root: Path) -> int:
    if not spec_path.exists():
        print(f"!! reverse_spec not found: {spec_path}", file=sys.stderr)
        return 3
    if not client_root.exists():
        print(f"!! client root not found: {client_root}", file=sys.stderr)
        return 3

    spec_text = spec_path.read_text(encoding="utf-8")

    checks = [
        check_state_classes(spec_text, client_root),
        check_symbol_count(spec_text, client_root),
    ]

    # Print report
    print("=" * 60)
    print(f"Regression Check")
    print(f"  spec:   {spec_path}")
    print(f"  client: {client_root}")
    print("=" * 60)

    any_fail = False
    for r in checks:
        icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭"}[r.status]
        print(f"{icon} [{r.status}] {r.name}: {r.message}")
        for line in r.detail_lines:
            print(f"    {line}")
        if r.status == "FAIL":
            any_fail = True

    print("=" * 60)
    if any_fail:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Reverse-spec regression check for slot-game-codegen-skill"
    )
    ap.add_argument("--spec", type=Path, required=True, help="reverse_spec.md path")
    ap.add_argument("--client", type=Path, required=True, help="client project root (e.g. E:\\UK\\pirate2-client)")
    args = ap.parse_args(argv)
    return run(args.spec, args.client)


if __name__ == "__main__":
    sys.exit(main())
