"""
slot-codegen-anchor-merge / anchor_merge.py
============================================

Anchor-aware merge utility for the Phase 2 Incremental Patch Protocol
(see slot-game-codegen-skill/_incremental-patch.md).

Reads an existing .ts / .proto file, scans for `<<CODEGEN_BEGIN:name>>` and
`<<USER_EDIT_BEGIN:name>>` anchor pairs, and merges a freshly-generated
"expected" version against it:
  * CODEGEN blocks     → overwritten with expected's matching block
  * USER_EDIT blocks   → preserved from existing
  * new anchors in expected → inserted
  * anchors no longer in expected → marked with CODEGEN_DEPRECATED comment
  * existing has malformed anchors → abort with clear error

Standalone CLI:
    py anchor_merge.py <existing.ts> <expected.ts> <output.ts>
    py anchor_merge.py --new <expected.ts> <output.ts>   # first-time write

Exit codes:
    0 — OK
    2 — usage error
    3 — file not found or unreadable
    4 — malformed anchors in existing file
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------------------------
# Anchor token syntax
# ---------------------------------------------------------------------------


class AnchorKind(str, Enum):
    CODEGEN = "CODEGEN"
    USER_EDIT = "USER_EDIT"


_NAME_PATTERN = r"[a-z0-9_]{1,40}"
# One regex captures all four marker variants. Group 1 = BEGIN/END, group 2 = kind, group 3 = name.
# Anchor lines look like:
#   // <<CODEGEN_BEGIN:name>>
#   // <<CODEGEN_END:name>>
#   // <<USER_EDIT_BEGIN:name>>
#   // <<USER_EDIT_END:name>>
# Allow leading whitespace and optional `// ` or `/* `…`*/ ` or `# ` or `<!-- `…` -->` wrappers
_ANCHOR_RE = re.compile(
    r"""
    ^                                            # line start
    \s*                                          # optional leading whitespace
    (?:
        //\s* |                                  # // comment (TS / proto)
        /\*\s* |                                 # /* comment
        \#\s* |                                  # # comment (Python)
        <!--\s*                                  # <!-- comment (Markdown)
    )?
    <<                                            # literal <<
    (CODEGEN|USER_EDIT)_(BEGIN|END)              # kind + begin/end
    :
    (""" + _NAME_PATTERN + r""")                 # name
    >>
    (?:\s*\*/|\s*-->)?                           # optional closing */ or -->
    \s*$                                          # optional trailing whitespace
    """,
    re.VERBOSE,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class AnchorBlock:
    """A parsed anchor region spanning [begin_line, end_line] (1-based, inclusive)."""

    kind: AnchorKind
    name: str
    begin_line: int        # the line containing `<<..._BEGIN:name>>`
    end_line: int          # the line containing `<<..._END:name>>`
    begin_text: str        # original begin marker line (preserved verbatim)
    end_text: str          # original end marker line
    inner_lines: list[str] = field(default_factory=list)   # lines strictly between begin and end


@dataclass
class ScanResult:
    blocks: list[AnchorBlock] = field(default_factory=list)
    # a flattened block-index lookup by (kind, name)
    by_key: dict[tuple[AnchorKind, str], int] = field(default_factory=dict)


class AnchorError(Exception):
    """Raised when an anchor-scan hits a malformed structure."""


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def scan(text: str) -> ScanResult:
    """Parse anchor markers out of file text. Raises AnchorError on malformed input."""
    lines = text.splitlines()
    # Stack of (kind, name, begin_idx). At end we verify stack is empty.
    stack: list[tuple[AnchorKind, str, int, str]] = []
    result = ScanResult()
    for idx, line in enumerate(lines, start=1):
        m = _ANCHOR_RE.match(line)
        if not m:
            continue
        kind_str, direction, name = m.group(1), m.group(2), m.group(3)
        kind = AnchorKind(kind_str)
        if direction == "BEGIN":
            # push
            stack.append((kind, name, idx, line))
        else:  # END
            if not stack:
                raise AnchorError(
                    f"Line {idx}: encountered {kind.value}_END:{name} with no matching BEGIN"
                )
            top_kind, top_name, top_begin_idx, top_begin_text = stack[-1]
            if top_kind != kind or top_name != name:
                raise AnchorError(
                    f"Line {idx}: {kind.value}_END:{name} does not match "
                    f"last open {top_kind.value}_BEGIN:{top_name} (line {top_begin_idx}). "
                    f"Crossed / mismatched anchor nesting is not allowed."
                )
            stack.pop()
            inner = lines[top_begin_idx:idx - 1]  # lines strictly between begin and end (0-indexed slice)
            block = AnchorBlock(
                kind=kind,
                name=name,
                begin_line=top_begin_idx,
                end_line=idx,
                begin_text=top_begin_text,
                end_text=line,
                inner_lines=list(inner),
            )
            # duplicate-name guard (same kind + same name twice)
            key = (kind, name)
            if key in result.by_key:
                raise AnchorError(
                    f"Line {idx}: duplicate anchor {kind.value}:{name} "
                    f"(previous at line {result.blocks[result.by_key[key]].begin_line})"
                )
            result.by_key[key] = len(result.blocks)
            result.blocks.append(block)
    if stack:
        top_kind, top_name, top_begin_idx, _ = stack[-1]
        raise AnchorError(
            f"Unterminated anchor {top_kind.value}_BEGIN:{top_name} opened at line {top_begin_idx} "
            f"has no matching {top_kind.value}_END"
        )
    return result


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------


_DEPRECATED_NOTE = "// <<CODEGEN_DEPRECATED>> region below was in a previous spec; safe to remove after review"


def merge(existing: str | None, expected: str) -> str:
    """Merge expected (freshly generated) on top of existing, honoring anchor protocol.

    Cases:
        1. existing is None or empty → return expected verbatim (first-time write).
        2. existing has no anchors → overwrite entirely with expected.
           (File isn't under anchor protocol; codegen owns it.)
        3. existing + expected both have anchors → walk expected, for each anchor:
           a. if CODEGEN and same name in existing → replace existing block's
              inner content with expected's inner.
           b. if USER_EDIT and same name in existing → KEEP existing block's
              inner content verbatim.
           c. if anchor name is new in expected → insert it (preserving expected's
              surrounding context).
        4. existing has anchors not in expected:
           - USER_EDIT → preserve (never delete user content).
           - CODEGEN → mark as deprecated but preserve (warn user via output).

    Strategy: use expected as the skeleton (because it's the source-of-truth
    layout), and swap in existing content where USER_EDIT blocks match, and
    preserve deprecated/extra existing blocks by appending them to the tail.
    """
    if existing is None or existing.strip() == "":
        return expected

    # Try to scan existing. If malformed, re-raise (caller surfaces to user).
    existing_scan = scan(existing)
    expected_scan = scan(expected)

    # Case 2: existing has no anchors → full overwrite
    if not existing_scan.blocks:
        return expected

    # Build lookups for existing by (kind, name)
    existing_by_key: dict[tuple[AnchorKind, str], AnchorBlock] = {
        (b.kind, b.name): b for b in existing_scan.blocks
    }
    expected_by_key: dict[tuple[AnchorKind, str], AnchorBlock] = {
        (b.kind, b.name): b for b in expected_scan.blocks
    }

    # Walk expected line-by-line; where we encounter an anchor we know about, swap
    # inner content per the rules. Non-anchor lines from expected are kept verbatim.
    expected_lines = expected.splitlines()
    # Build a map of begin_line → block so we can jump over blocks in one step.
    begin_line_to_block: dict[int, AnchorBlock] = {b.begin_line: b for b in expected_scan.blocks}

    output: list[str] = []
    i = 1  # 1-based line pointer
    total = len(expected_lines)
    while i <= total:
        line = expected_lines[i - 1]
        block = begin_line_to_block.get(i)
        if block is None:
            output.append(line)
            i += 1
            continue

        # We've hit an anchor BEGIN in expected. Emit begin marker, then decide
        # what inner to use, then emit end marker.
        output.append(block.begin_text)
        key = (block.kind, block.name)
        existing_match = existing_by_key.get(key)

        if block.kind == AnchorKind.USER_EDIT and existing_match is not None:
            # Case 3b: preserve user edits
            output.extend(existing_match.inner_lines)
        elif block.kind == AnchorKind.CODEGEN:
            # Case 3a: replace with expected's fresh content.
            # BUT: if the existing CODEGEN block contains nested USER_EDIT anchors,
            # we must preserve their content. We do this by recursing: treat the
            # existing inner as "existing" and expected inner as "expected" and
            # let merge() handle the nested anchor matching.
            if existing_match is not None:
                existing_inner = "\n".join(existing_match.inner_lines)
                expected_inner = "\n".join(block.inner_lines)
                try:
                    merged_inner = merge(existing_inner, expected_inner)
                except AnchorError:
                    # nested existing malformed somehow — fall back to expected
                    merged_inner = expected_inner
                # merge() returns possibly-with-trailing-newline; split back to lines
                merged_lines = merged_inner.splitlines()
                output.extend(merged_lines)
            else:
                # no existing match; just use expected
                output.extend(block.inner_lines)
        else:
            # New anchor (not in existing) — just use expected's content
            output.extend(block.inner_lines)

        output.append(block.end_text)
        # Skip ahead past this anchor block in expected
        i = block.end_line + 1

    # Case 4: handle existing anchors that are not in expected (deprecated CODEGEN or extra USER_EDIT)
    extras: list[AnchorBlock] = []
    for b in existing_scan.blocks:
        if (b.kind, b.name) not in expected_by_key:
            extras.append(b)

    if extras:
        output.append("")
        output.append("// ============================================================")
        output.append("// Anchors below are no longer in the codegen spec.")
        output.append("// USER_EDIT blocks are preserved; CODEGEN blocks are marked deprecated.")
        output.append("// Review and remove manually once confirmed unused.")
        output.append("// ============================================================")
        for b in extras:
            output.append("")
            output.append(b.begin_text)
            if b.kind == AnchorKind.CODEGEN:
                output.append(_DEPRECATED_NOTE)
            output.extend(b.inner_lines)
            output.append(b.end_text)

    # Trailing newline hygiene: if expected ended with newline, keep the same.
    trailing = "\n" if expected.endswith("\n") else ""
    return "\n".join(output) + trailing


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"!! file not found: {path}", file=sys.stderr)
        sys.exit(3)
    except OSError as e:
        print(f"!! failed to read {path}: {e}", file=sys.stderr)
        sys.exit(3)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Anchor-aware merge for Phase 2 Incremental Patch Protocol"
    )
    ap.add_argument(
        "--new",
        action="store_true",
        help="First-time write: use only <expected.ts> as the output. Ignores <existing.ts>.",
    )
    ap.add_argument("existing", nargs="?", type=Path, help="path to existing file (may be omitted when --new)")
    ap.add_argument("expected", type=Path, help="path to freshly-generated expected file")
    ap.add_argument("output", type=Path, help="path to write merged output")
    args = ap.parse_args(argv)

    if args.new:
        expected_text = _read(args.expected)
        _write(args.output, expected_text)
        print(f"OK (new): wrote {args.output} ({len(expected_text):,} chars)")
        return 0

    if args.existing is None:
        print("!! existing file required when --new is not set", file=sys.stderr)
        return 2

    existing_text = _read(args.existing)
    expected_text = _read(args.expected)
    try:
        merged = merge(existing_text, expected_text)
    except AnchorError as e:
        print(f"!! anchor malformed in {args.existing}:\n   {e}", file=sys.stderr)
        return 4
    _write(args.output, merged)
    print(f"OK: wrote {args.output} ({len(merged):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
