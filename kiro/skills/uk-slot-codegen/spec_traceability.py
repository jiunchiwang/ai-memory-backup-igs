"""
slot-codegen-regression-check / spec_traceability.py
====================================================

Spec traceability tool for slot codegen pipeline.

Four modes:
  1. `tag-spec`  — Add [SPEC:XX-N] IDs to Game_Spec.md sections/rules
  2. `build-manifest` — Split codegen-owned/deferred items and write evidence JSON
  3. `check-coverage` — Validate codegen-owned evidence; deferred M2+ is advisory
  4. `report` — Generate coverage report

Usage:
    py spec_traceability.py tag-spec <Game_Spec.md>
    py spec_traceability.py build-manifest --spec <Game_Spec.md> --client <client-root> --output <json>
    py spec_traceability.py check-coverage --spec <Game_Spec.md> --client <client-root>
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

from check_regression_v2 import (
    check_variable_board,
    parse_client_game_define,
    parse_client_prefab,
    parse_client_slot_reels,
    parse_game_spec,
)

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
        existing = re.search(r"\[SPEC:([A-Z]+)-(\d+)\]", line)
        if existing:
            # Preserve stable IDs when tag-spec is rerun on a partially tagged
            # document. Without this, the next new row restarts at 1 and can
            # duplicate an existing ID in the same section.
            if current_section in SECTION_PREFIXES and existing.group(1) == SECTION_PREFIXES[current_section]:
                counter[current_section] = max(counter.get(current_section, 0), int(existing.group(2)))
            output.append(line)
            continue

        # Tag table rows with data (| value | value |) in sections 2,3,5,6,7,8
        if current_section in SECTION_PREFIXES and re.match(r"^\|[^-]", line):
            # Skip header separator rows and header rows
            if re.match(r"^\|\s*---", line) or re.match(
                r"^\|\s*(項目|#|索引|值|名稱|SymID|Key)(?:\s*\||\s*$)",
                line,
                re.IGNORECASE,
            ):
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


HEADER_KEYS = {"symid", "key", "id", "index", "索引", "編號", "項目", "名稱", "值"}
INFERRED_DEFAULT_KEYS = {
    "SymbolWidth", "SymbolHeight", "SeparateLineWidth", "MIDDLE_PLATE_INDEX",
}
BOARD_CONFIG_KEYS = {
    "COL", "ROW", "FULL_PLATE_NUM", "MAX_ROW", "SYMBOL_COUNT",
    "BoardLayout", *INFERRED_DEFAULT_KEYS,
}


def _table_cells(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return [cell for cell in cells if not re.fullmatch(r"\[SPEC:[A-Z]+-\d+\]", cell)]


def _bullet_key(line: str) -> str:
    match = re.search(r"-\s+\*\*([^*]+)\*\*\s*:", line)
    return match.group(1).strip() if match else ""


def _classify_item(section: str, line: str) -> tuple[str, str]:
    """Return (scope, kind) using section semantics, never the unstable ID prefix."""
    cells = _table_cells(line) if line.lstrip().startswith("|") else []
    if cells and cells[0].strip().lower() in HEADER_KEYS:
        return "informational", "table_header"

    title = section.lower()
    if any(key in title for key in ("custom", "特色", "feature", "mg演出", "fg演出")):
        return "deferred", "game_feature"
    if "symbol" in title or "符號" in title:
        return "codegen", "symbol"
    if "音效" in title or "audio" in title:
        return "codegen", "audio"
    if "盤面配置" in title or "board" in title or "reel" in title:
        key = _bullet_key(line)
        if key in INFERRED_DEFAULT_KEYS and not re.search(r"\[SOURCE:(?:original|xlsx)\]", line, re.I):
            return "inferred", "board_config"
        if key in BOARD_CONFIG_KEYS:
            return "codegen", "board_config"
        if key.lower() == "lines":
            return "informational", "payline_info"
        return "deferred", "game_feature"
    if "基本" in title or "overview" in title or "project" in title:
        key = _bullet_key(line)
        if key == "盤面":
            return "codegen", "basic_board"
        if key.lower() == "spinmode":
            return "codegen", "spin_mode"
        if key in {"遊戲名稱", "對線方式"}:
            return "informational", "overview_info"
        return "deferred", "game_rule"
    return "deferred", "unclassified"


def parse_spec_items(spec_path: Path) -> list[dict]:
    """Parse tagged spec lines with semantic ownership and stable line evidence."""
    items = []
    section = ""
    for line_number, line in enumerate(spec_path.read_text(encoding="utf-8").splitlines(), start=1):
        heading = re.match(r"^##\s+(?!#)(?:\d+\.\s*)?(.+)$", line)
        if heading:
            section = heading.group(1).strip()
        for spec_id in re.findall(r"\[SPEC:([A-Z]+-\d+)\]", line):
            scope, kind = _classify_item(section, line)
            items.append({
                "id": spec_id,
                "section": section,
                "line": line_number,
                "text": re.sub(r"\s*\[SPEC:[A-Z]+-\d+\]\s*", "", line).strip(),
                "scope": scope,
                "kind": kind,
                "origin": "codegen_default" if scope == "inferred" else "game_spec",
            })
    return items


def extract_client_refs(client_root: Path) -> dict[str, list[str]]:
    """Map explicit // [SPEC:*] references to relative TypeScript paths."""
    refs: dict[str, list[str]] = {}
    for relative in (Path("assets/Script"), Path("assets/game/Script")):
        source_root = client_root / relative
        if not source_root.exists():
            continue
        for path in source_root.rglob("*.ts"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for spec_id in re.findall(r"//\s*\[SPEC:([A-Z]+-\d+)\]", text):
                refs.setdefault(spec_id, []).append(path.relative_to(client_root).as_posix())
    return refs


def _find_game_define(client_root: Path) -> Path | None:
    for relative in (Path("assets/Script/Game_Define.ts"), Path("assets/game/Script/Game_Define.ts")):
        path = client_root / relative
        if path.exists():
            return path
    return None


def _find_audio_manager(client_root: Path) -> Path | None:
    candidates = (
        Path("assets/Script/Audio/AudioManager.ts"),
        Path("assets/Script/GameAudio/AudioManager.ts"),
        Path("assets/game/Script/Audio/AudioManager.ts"),
    )
    for relative in candidates:
        path = client_root / relative
        if path.exists():
            return path
    return None


def _path_evidence(client_root: Path, path: Path, contract: str) -> dict:
    return {"path": path.relative_to(client_root).as_posix(), "contract": contract}


def _artifact_evidence(item: dict, spec_path: Path, client_root: Path) -> list[dict]:
    """Return value-checked structural evidence for one codegen-owned item."""
    evidence: list[dict] = []
    kind = item["kind"]
    line = item["text"]
    game_define = _find_game_define(client_root)
    client_gd = parse_client_game_define(client_root)

    if kind == "basic_board":
        match = re.search(r"(\d+)\s*[x×]\s*(\d+)", line, re.IGNORECASE)
        if match and client_gd.get("ROW") == int(match.group(1)) and client_gd.get("COL") == int(match.group(2)):
            if game_define:
                evidence.append(_path_evidence(client_root, game_define, "ROW×COL exact match"))

    elif kind == "spin_mode":
        expected = next((mode for mode in ("Standard", "Tumble", "Cascade") if re.search(mode, line, re.I)), None)
        if expected:
            for relative in (Path("assets/Script/GameView.ts"), Path("assets/Script/SlotReels.ts")):
                path = client_root / relative
                if path.exists() and re.search(rf"SpinMode\.{expected}", path.read_text(encoding="utf-8-sig", errors="ignore")):
                    evidence.append(_path_evidence(client_root, path, f"SpinMode.{expected}"))
                    break

    elif kind == "symbol":
        cells = _table_cells(line)
        if cells and re.fullmatch(r"\d+", cells[0]):
            sym_id = int(cells[0])
            marker = " ".join(cells[2:])
            server_only = bool(re.search(r"server[_\s-]*only|server\s*用|伺服器", marker, re.I))
            actual_ids = set(client_gd.get("symbol_ids", []))
            matched = sym_id not in actual_ids if server_only else sym_id in actual_ids
            if matched and game_define:
                contract = "server-only excluded" if server_only else f"client SymID {sym_id} present"
                evidence.append(_path_evidence(client_root, game_define, contract))

    elif kind == "audio":
        cells = _table_cells(line)
        audio_manager = _find_audio_manager(client_root)
        if len(cells) >= 2 and audio_manager:
            key, filename = cells[0], cells[1]
            text = audio_manager.read_text(encoding="utf-8-sig", errors="ignore")
            has_key = bool(re.search(rf"\b{re.escape(key)}\b", text))
            has_filename = bool(re.search(rf"FileName\s*:\s*[\"']{re.escape(filename)}[\"']", text))
            if has_key and has_filename:
                evidence.append(_path_evidence(client_root, audio_manager, f"AudioClips {key}→{filename}"))

    elif kind == "board_config":
        key = _bullet_key(line)
        expected_match = re.search(r":\s*(\d+)", line)
        direct_keys = {
            "COL": "COL", "ROW": "ROW", "FULL_PLATE_NUM": "FULL_PLATE_NUM",
            "MAX_ROW": "MAX_ROW", "SYMBOL_COUNT": "SYMBOL_COUNT",
        }
        if key in direct_keys and expected_match and game_define:
            actual = client_gd.get(direct_keys[key])
            if actual == int(expected_match.group(1)):
                evidence.append(_path_evidence(client_root, game_define, f"{key}={actual}"))
        elif key in {"SymbolWidth", "SymbolHeight", "SeparateLineWidth"} and expected_match and game_define:
            expected = int(expected_match.group(1))
            text = game_define.read_text(encoding="utf-8-sig", errors="ignore")
            if re.search(rf"static\s+{re.escape(key)}\s*=\s*{expected}\b", text):
                evidence.append(_path_evidence(client_root, game_define, f"{key}={expected}"))
        elif key == "MIDDLE_PLATE_INDEX" and expected_match:
            expected = int(expected_match.group(1))
            for relative in (Path("assets/Script/Game_Define.ts"), Path("assets/Script/SlotReels.ts")):
                path = client_root / relative
                if path.exists() and re.search(
                    rf"MIDDLE_PLATE_INDEX\s*=\s*{expected}\b",
                    path.read_text(encoding="utf-8-sig", errors="ignore"),
                ):
                    evidence.append(_path_evidence(client_root, path, f"MIDDLE_PLATE_INDEX={expected}"))
                    break
        elif key == "BoardLayout":
            spec = parse_game_spec(spec_path.read_text(encoding="utf-8"))
            result = check_variable_board(
                spec,
                client_gd,
                parse_client_slot_reels(client_root),
                parse_client_prefab(client_root),
            )
            if result.status == "PASS":
                slot_reels = client_root / "assets" / "Script" / "SlotReels.ts"
                if slot_reels.exists():
                    evidence.append(_path_evidence(client_root, slot_reels, result.message))

    return evidence


def _uncovered_diagnostic(item: dict, client_root: Path) -> dict:
    """Explain why a codegen-owned contract has no value-checked evidence."""
    kind = item["kind"]
    line = item["text"]
    if kind == "board_config":
        key = _bullet_key(line)
        expected_match = re.search(r":\s*(-?\d+)", line)
        expected = int(expected_match.group(1)) if expected_match else None
        for relative in (
            Path("assets/Script/Game_Define.ts"),
            Path("assets/game/Script/Game_Define.ts"),
            Path("assets/Script/SlotReels.ts"),
        ):
            path = client_root / relative
            if not path.exists():
                continue
            match = re.search(
                rf"\b{re.escape(key)}\b\s*=\s*(-?\d+)",
                path.read_text(encoding="utf-8-sig", errors="ignore"),
            )
            if match:
                actual = int(match.group(1))
                return {
                    "reason": "value mismatch",
                    "expected": expected,
                    "actual": actual,
                    "path": path.relative_to(client_root).as_posix(),
                }
        return {"reason": "client value not found", "expected": expected, "actual": None}
    if kind == "basic_board":
        match = re.search(r"(\d+)\s*[x×]\s*(\d+)", line, re.IGNORECASE)
        expected = {"ROW": int(match.group(1)), "COL": int(match.group(2))} if match else None
        client_gd = parse_client_game_define(client_root)
        return {
            "reason": "board dimensions mismatch or missing",
            "expected": expected,
            "actual": {"ROW": client_gd.get("ROW"), "COL": client_gd.get("COL")},
        }
    return {"reason": f"no value-checked {kind} artifact evidence"}


def build_traceability(spec_path: Path, client_root: Path) -> dict:
    """Build deterministic scoped traceability with artifact/value evidence."""
    refs = extract_client_refs(client_root)
    items = []
    for raw_item in parse_spec_items(spec_path):
        item = dict(raw_item)
        artifact_evidence = []
        if item["scope"] in {"codegen", "inferred"}:
            artifact_evidence = _artifact_evidence(item, spec_path, client_root)
        evidence = list(artifact_evidence)
        for path in refs.get(item["id"], []):
            evidence.append({"path": path, "contract": "explicit SPEC reference"})
        item["evidence"] = evidence
        if item["scope"] == "informational":
            item["status"] = "ignored"
        elif item["scope"] == "deferred":
            item["status"] = "linked" if evidence else "deferred"
        elif item["scope"] == "inferred":
            item["status"] = "verified" if artifact_evidence else "needs_review"
            if not artifact_evidence:
                item["diagnostic"] = _uncovered_diagnostic(item, client_root)
        else:
            # A comment proves only that somebody linked the requirement. For
            # codegen-owned values, coverage requires independently parsed
            # artifact evidence so stale/wrong values cannot pass the gate.
            item["status"] = "covered" if artifact_evidence else "uncovered"
            if not artifact_evidence:
                item["diagnostic"] = _uncovered_diagnostic(item, client_root)
        items.append(item)

    codegen = [item for item in items if item["scope"] == "codegen"]
    deferred = [item for item in items if item["scope"] == "deferred"]
    inferred = [item for item in items if item["scope"] == "inferred"]
    informational = [item for item in items if item["scope"] == "informational"]
    covered = [item for item in codegen if item["status"] == "covered"]
    known_ids = {item["id"] for item in items}
    extra_refs = sorted(set(refs) - known_ids)
    return {
        "version": 1,
        "summary": {
            "codegen_total": len(codegen),
            "codegen_covered": len(covered),
            "codegen_uncovered": len(codegen) - len(covered),
            "deferred_total": len(deferred),
            "deferred_linked": sum(item["status"] == "linked" for item in deferred),
            "inferred_total": len(inferred),
            "inferred_verified": sum(item["status"] == "verified" for item in inferred),
            "inferred_review": sum(item["status"] == "needs_review" for item in inferred),
            "informational_total": len(informational),
            "extra_client_refs": len(extra_refs),
        },
        "extra_client_ref_ids": extra_refs,
        "items": items,
    }


def write_manifest(spec_path: Path, client_root: Path, output: Path) -> dict:
    """Write scoped traceability JSON and return the same manifest."""
    manifest = build_traceability(spec_path, client_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def check_coverage(spec_path: Path, client_root: Path) -> int:
    """Validate codegen-owned evidence and report M2+ deferred separately."""
    if not extract_spec_ids(spec_path):
        print("No [SPEC:*] tags found in spec. Run `tag-spec` first.")
        return 2

    manifest = build_traceability(spec_path, client_root)
    summary = manifest["summary"]
    uncovered = [
        item for item in manifest["items"]
        if item["scope"] == "codegen" and item["status"] == "uncovered"
    ]

    print(f"{'='*50}")
    print(f"  Spec Traceability Coverage Report")
    print(f"{'='*50}")
    print(f"  Codegen:      {summary['codegen_covered']}/{summary['codegen_total']} covered")
    print(f"  Deferred M2+: {summary['deferred_total']} ({summary['deferred_linked']} linked)")
    print(
        f"  Inferred:     {summary['inferred_verified']}/{summary['inferred_total']} verified "
        f"({summary['inferred_review']} need review; non-blocking)"
    )
    print(f"  Informational:{summary['informational_total']}")
    if summary["extra_client_refs"]:
        print(f"  Extra client refs: {summary['extra_client_refs']}")
    print(f"{'='*50}")

    if uncovered:
        print(f"\n  Uncovered spec items:")
        for item in uncovered:
            print(f"    - [SPEC:{item['id']}] {item['text']}")

    if manifest["extra_client_ref_ids"]:
        print(f"\n  Extra client refs (spec ID not found):")
        for sid in manifest["extra_client_ref_ids"]:
            print(f"    - [SPEC:{sid}]")

    print(f"\n  RESULT: {'PASS' if not uncovered else 'FAIL'} (codegen scope)")
    return 0 if not uncovered else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Spec traceability for slot codegen")
    sub = ap.add_subparsers(dest="cmd")

    p_tag = sub.add_parser("tag-spec", help="Add [SPEC:XX-N] IDs to Game_Spec.md")
    p_tag.add_argument("spec", type=Path, help="Game_Spec.md path")

    p_cov = sub.add_parser("check-coverage", help="Check coverage of spec IDs in client")
    p_cov.add_argument("--spec", type=Path, required=True)
    p_cov.add_argument("--client", type=Path, required=True)

    p_manifest = sub.add_parser("build-manifest", help="Write scoped traceability evidence JSON")
    p_manifest.add_argument("--spec", type=Path, required=True)
    p_manifest.add_argument("--client", type=Path, required=True)
    p_manifest.add_argument("--output", type=Path, required=True)

    args = ap.parse_args(argv)
    if args.cmd == "tag-spec":
        return tag_spec(args.spec)
    elif args.cmd == "check-coverage":
        return check_coverage(args.spec, args.client)
    elif args.cmd == "build-manifest":
        manifest = write_manifest(args.spec, args.client, args.output)
        summary = manifest["summary"]
        print(
            f"codegen {summary['codegen_covered']}/{summary['codegen_total']}; "
            f"deferred M2+ {summary['deferred_total']}; "
            f"inferred defaults {summary['inferred_verified']}/{summary['inferred_total']} verified; "
            f"informational {summary['informational_total']}"
        )
        for item in manifest["items"]:
            if item["scope"] == "codegen" and item["status"] == "uncovered":
                print(f"  {item['id']}: {item.get('diagnostic', {}).get('reason', 'uncovered')}")
        return 0 if summary["codegen_uncovered"] == 0 else 1
    else:
        ap.print_help()
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.exit(main())
