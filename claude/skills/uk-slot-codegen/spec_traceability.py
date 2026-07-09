"""
slot-codegen-regression-check / spec_traceability.py
====================================================

Spec traceability tool for slot codegen pipeline.

Three modes:
  1. `tag-spec`  — Add [SPEC:XX-N] IDs to Game_Spec.md sections/rules
  2. `check-coverage` — Compare [SPEC:*] IDs in spec vs // [SPEC:*] in client TS
  3. `report` — Generate coverage report

Usage:
    py spec_traceability.py tag-spec <Game_Spec.md>
    py spec_traceability.py check-coverage --spec <Game_Spec.md> --client <client-root>
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# Section prefix mapping
SECTION_PREFIXES = {
    "1": "OV",   # Overview
    "2": "BD",   # Board
    "3": "SYM",  # Symbol
    "4": "PRT",  # Protocol
    "5": "WIN",  # Win rules
    "6": "RSP",  # Respin
    "7": "FG",   # Free Game
    "8": "SM",   # State Machine
    "9": "UI",   # UI/Scene
    "10": "APP", # Appendix
}


def tag_spec(spec_path: Path) -> int:
    """Add [SPEC:XX-N] tags to key lines in Game_Spec.md."""
    text = spec_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    output = []
    current_section = ""
    counter = {}

    # Fallback: map known Chinese/English section titles to section numbers
    TITLE_TO_SECTION = {
        "專案資訊": "1", "project": "1", "overview": "1",
        "轉輪配置": "2", "board": "2", "reel": "2",
        "符號定義": "3", "symbol": "3",
        "協議": "4", "proto": "4", "protocol": "4",
        "賠付": "5", "win": "5", "pay": "5",
        "respin": "6",
        "特色玩法": "7", "free": "7", "feature": "7",
        "狀態機": "8", "state": "8",
        "ui": "9", "scene": "9",
        "音效": "10", "audio": "10", "appendix": "10",
    }

    for line in lines:
        # Detect section header: ## N. Title  OR  ## Title (no number)
        m = re.match(r"^##\s+(\d+)\.\s+", line)
        if m:
            current_section = m.group(1)
            if current_section not in counter:
                counter[current_section] = 0
            output.append(line)
            continue
        # Fallback: ## Title without number prefix
        m_title = re.match(r"^##\s+(.+)", line)
        if m_title and not line.startswith("###"):
            title_lower = m_title.group(1).strip().lower()
            for key, sec in TITLE_TO_SECTION.items():
                if key in title_lower:
                    current_section = sec
                    if current_section not in counter:
                        counter[current_section] = 0
                    break
            output.append(line)
            continue

        # Skip if already tagged
        if re.search(r"\[SPEC:[A-Z]+-\d+\]", line):
            output.append(line)
            continue

        # Tag table rows with data (| value | value |) in sections 2,3,5,6,7,8
        if current_section in SECTION_PREFIXES and re.match(r"^\|[^-]", line):
            # Skip header separator rows and header rows
            if re.match(r"^\|\s*---", line) or re.match(r"^\|\s*(項目|#|索引|值|名稱)", line):
                output.append(line)
                continue
            # Tag this row
            prefix = SECTION_PREFIXES[current_section]
            counter[current_section] += 1
            tag = f"[SPEC:{prefix}-{counter[current_section]}]"
            # Append tag at end of line
            output.append(f"{line} {tag}")
            continue

        # Tag ### subsection headers
        m2 = re.match(r"^###\s+(\d+\.\d+)\s+", line)
        if m2 and current_section in SECTION_PREFIXES:
            prefix = SECTION_PREFIXES[current_section]
            counter[current_section] += 1
            tag = f"[SPEC:{prefix}-{counter[current_section]}]"
            output.append(f"{line} {tag}")
            continue

        # Tag bullet points with key specs (- **xxx**: yyy)
        if current_section in SECTION_PREFIXES and re.match(r"^-\s+\*\*", line):
            prefix = SECTION_PREFIXES[current_section]
            counter[current_section] += 1
            tag = f"[SPEC:{prefix}-{counter[current_section]}]"
            output.append(f"{line} {tag}")
            continue

        output.append(line)

    result = "\n".join(output)
    spec_path.write_text(result, encoding="utf-8")

    total = sum(counter.values())
    print(f"Tagged {total} items across {len(counter)} sections")
    for sec, cnt in sorted(counter.items()):
        prefix = SECTION_PREFIXES.get(sec, "?")
        print(f"  [{prefix}] section {sec}: {cnt} tags")
    return 0


def extract_spec_ids(spec_path: Path) -> set[str]:
    """Extract all [SPEC:XX-N] IDs from Game_Spec.md."""
    text = spec_path.read_text(encoding="utf-8")
    return set(re.findall(r"\[SPEC:([A-Z]+-\d+)\]", text))


def extract_client_ids(client_root: Path) -> set[str]:
    """Extract all // [SPEC:XX-N] references from client TS files."""
    ids = set()
    script_dirs = [
        client_root / "assets" / "Script",
        client_root / "assets" / "game" / "Script",
    ]
    for d in script_dirs:
        if not d.exists():
            continue
        for f in d.rglob("*.ts"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            ids.update(re.findall(r"//\s*\[SPEC:([A-Z]+-\d+)\]", text))
    return ids


def check_coverage(spec_path: Path, client_root: Path) -> int:
    """Compare spec IDs vs client references."""
    spec_ids = extract_spec_ids(spec_path)
    client_ids = extract_client_ids(client_root)

    if not spec_ids:
        print("No [SPEC:*] tags found in spec. Run `tag-spec` first.")
        return 2

    covered = spec_ids & client_ids
    uncovered = spec_ids - client_ids
    extra = client_ids - spec_ids

    total = len(spec_ids)
    cov_pct = len(covered) / total * 100 if total else 0

    print(f"{'='*50}")
    print(f"  Spec Traceability Coverage Report")
    print(f"{'='*50}")
    print(f"  Spec IDs:     {total}")
    print(f"  Covered:      {len(covered)} ({cov_pct:.0f}%)")
    print(f"  Uncovered:    {len(uncovered)}")
    if extra:
        print(f"  Extra (client refs spec not found): {len(extra)}")
    print(f"{'='*50}")

    if uncovered:
        print(f"\n  Uncovered spec items:")
        for sid in sorted(uncovered):
            print(f"    - [SPEC:{sid}]")

    if extra:
        print(f"\n  Extra client refs (spec ID not found):")
        for sid in sorted(extra):
            print(f"    - [SPEC:{sid}]")

    print(f"\n  RESULT: {'PASS' if not uncovered else 'PARTIAL'} ({cov_pct:.0f}% coverage)")
    return 0 if not uncovered else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Spec traceability for slot codegen")
    sub = ap.add_subparsers(dest="cmd")

    p_tag = sub.add_parser("tag-spec", help="Add [SPEC:XX-N] IDs to Game_Spec.md")
    p_tag.add_argument("spec", type=Path, help="Game_Spec.md path")

    p_cov = sub.add_parser("check-coverage", help="Check coverage of spec IDs in client")
    p_cov.add_argument("--spec", type=Path, required=True)
    p_cov.add_argument("--client", type=Path, required=True)

    args = ap.parse_args(argv)
    if args.cmd == "tag-spec":
        return tag_spec(args.spec)
    elif args.cmd == "check-coverage":
        return check_coverage(args.spec, args.client)
    else:
        ap.print_help()
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.exit(main())
