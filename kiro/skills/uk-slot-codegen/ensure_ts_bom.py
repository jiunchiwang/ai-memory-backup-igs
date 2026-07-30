#!/usr/bin/env python3
"""Ensure codegen-owned TypeScript files use UTF-8 with BOM."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


UTF8_BOM = b"\xef\xbb\xbf"
OWNED_ROOTS = (
    Path("assets/Script"),
    Path("assets/game/Script"),
    Path("tests"),
)


def ensure_bom_for_target(target: Path) -> list[Path]:
    """Add a BOM to UTF-8 TypeScript files below codegen-owned roots."""
    target = target.resolve()
    changed: list[Path] = []
    for relative_root in OWNED_ROOTS:
        source_root = target / relative_root
        if not source_root.exists():
            continue
        for path in sorted(source_root.rglob("*.ts")):
            raw = path.read_bytes()
            if raw.startswith(UTF8_BOM):
                continue
            # Refuse to rewrite an unknown encoding. This prevents a blind BOM
            # prefix from hiding existing file corruption.
            raw.decode("utf-8")
            path.write_bytes(UTF8_BOM + raw)
            changed.append(path)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="slot client project root")
    args = parser.parse_args(argv)
    if not args.target.exists():
        parser.error(f"target does not exist: {args.target}")
    try:
        changed = ensure_bom_for_target(args.target)
    except UnicodeDecodeError as exc:
        print(f"ERROR: non-UTF-8 TypeScript file: {exc}", file=sys.stderr)
        return 1
    print(f"BOM fixed: {len(changed)} file(s)")
    for path in changed:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
