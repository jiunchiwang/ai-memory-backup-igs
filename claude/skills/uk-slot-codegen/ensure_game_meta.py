"""
uk-slot-spec-adapter / ensure_game_meta.py
===========================================

Tiny helper called by the slot-game-codegen-skill preflight step 0.4
(and optionally by bootstrap scripts) to guarantee every new UK slot
client has a valid `assets/game.meta` file marking that directory as a
Cocos asset bundle.

Without this file, Cocos Creator 3.6.2 preview typically shows:
  - `config.json 404` (bundle loader looks for /game/config.json)
  - `A Class already exists with the same __cid__` (ccclass re-registered
    when the same .ts is loaded via two different import paths)

What this script does:
    - If `<client-root>/assets/game.meta` already exists → verify its JSON
      parses and contains `userData.isBundle == true`; if so, exit 0; if
      malformed, exit 1 and tell the user.
    - If it doesn't exist → copy the template from
      `E:\\UK\\uk_slot_framework\\templates\\game.meta.template`
      (or the path passed via --template), substitute a fresh UUID v4 into
      the `<GAME_META_UUID>` placeholder, write the file, exit 0.

Usage:
    py ensure_game_meta.py <client-root>
    py ensure_game_meta.py <client-root> --template <path/to/game.meta.template>
    py ensure_game_meta.py <client-root> --dry-run     # check only, don't write

Exit codes:
    0  OK (already-good OR wrote new)
    1  malformed existing meta (refuse to overwrite)
    2  usage error
    3  template / client-root missing
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path


DEFAULT_TEMPLATE = Path(r"E:\UK\uk_slot_framework\templates\game.meta.template")
UUID_PLACEHOLDER = "<GAME_META_UUID>"


def _is_valid_meta(content: str) -> tuple[bool, str]:
    """Parse and check required fields. Returns (ok, reason)."""
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"not valid JSON: {e}"
    # minimal structural check
    userdata = obj.get("userData")
    if not isinstance(userdata, dict):
        return False, "missing `userData` object"
    if userdata.get("isBundle") is not True:
        return False, "`userData.isBundle` must be true (found: " + repr(userdata.get("isBundle")) + ")"
    uid = obj.get("uuid")
    if not isinstance(uid, str) or len(uid) < 8:
        return False, f"invalid `uuid` field: {uid!r}"
    return True, "OK"


def ensure_meta(client_root: Path, template: Path, dry_run: bool = False) -> int:
    if not client_root.exists():
        print(f"!! client-root not found: {client_root}", file=sys.stderr)
        return 3

    meta_path = client_root / "assets" / "game.meta"

    if meta_path.exists():
        content = meta_path.read_text(encoding="utf-8")
        ok, reason = _is_valid_meta(content)
        if ok:
            print(f"OK: {meta_path} already valid ({reason})")
            return 0
        print(f"!! {meta_path} exists but is malformed: {reason}", file=sys.stderr)
        print(f"   Refusing to overwrite an existing file. Delete it first or fix manually.", file=sys.stderr)
        return 1

    # New file path
    if not template.exists():
        print(
            f"!! template not found: {template}\n"
            f"   Provide --template <path> or ensure UK slot framework templates are available.",
            file=sys.stderr,
        )
        return 3

    tmpl_text = template.read_text(encoding="utf-8")
    if UUID_PLACEHOLDER not in tmpl_text:
        print(
            f"!! template {template} does not contain {UUID_PLACEHOLDER!r} placeholder; "
            f"aborting to avoid writing with unsubstituted uuid.",
            file=sys.stderr,
        )
        return 1

    fresh_uuid = str(uuid.uuid4())  # 36-char canonical, lowercase
    output = tmpl_text.replace(UUID_PLACEHOLDER, fresh_uuid)

    # Sanity: output must be valid JSON now
    ok, reason = _is_valid_meta(output)
    if not ok:
        print(
            f"!! after UUID substitution the output is not valid meta: {reason}. "
            f"Template might be corrupted.",
            file=sys.stderr,
        )
        return 1

    if dry_run:
        print(f"DRY-RUN: would write {meta_path} with uuid={fresh_uuid} ({len(output)} chars)")
        return 0

    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(output, encoding="utf-8")
    print(f"OK: wrote {meta_path} (new uuid={fresh_uuid}, {len(output)} chars)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ensure assets/game.meta is present for a UK slot client")
    ap.add_argument("client", type=Path, help="client project root")
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="game.meta template path")
    ap.add_argument("--dry-run", action="store_true", help="don't write; just report what would happen")
    args = ap.parse_args(argv)
    return ensure_meta(args.client, args.template, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
