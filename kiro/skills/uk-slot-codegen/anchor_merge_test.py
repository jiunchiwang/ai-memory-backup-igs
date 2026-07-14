"""
smoke_test.py — manual smoke test for anchor_merge.

Covers 6 scenarios + idempotency from Phase 2 Week 4 checklist:
    1. new file (existing is None) → output == expected
    2. CODEGEN overwrite (same name, different inner)
    3. USER_EDIT preserve (user added custom code)
    4. new anchor inserted (expected has anchor existing doesn't)
    5. deprecated CODEGEN (existing has anchor expected doesn't)
    6. malformed existing → AnchorError raised
    plus: idempotent — merge(merge(a, b), b) == merge(a, b)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the skill dir importable
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from anchor_merge import AnchorError, merge, scan  # noqa: E402


def _assert_eq(label: str, actual: str, expected: str) -> None:
    if actual == expected:
        print(f"  ✓ {label}")
    else:
        print(f"  ✗ {label}")
        print("    --- expected ---")
        for line in expected.splitlines():
            print(f"    | {line}")
        print("    --- actual ---")
        for line in actual.splitlines():
            print(f"    | {line}")
        raise AssertionError(f"mismatch in {label!r}")


def test_1_new_file() -> None:
    print("case 1: new file (existing is None)")
    expected = (
        "// header\n"
        "// <<CODEGEN_BEGIN:symbol_enum>>\n"
        "enum Symbol { A, B }\n"
        "// <<CODEGEN_END:symbol_enum>>\n"
    )
    result = merge(None, expected)
    _assert_eq("new file output == expected", result, expected)


def test_2_codegen_overwrite() -> None:
    print("case 2: CODEGEN overwrite")
    existing = (
        "// header\n"
        "// <<CODEGEN_BEGIN:symbol_enum>>\n"
        "enum Symbol { OLD }\n"
        "// <<CODEGEN_END:symbol_enum>>\n"
    )
    expected = (
        "// header\n"
        "// <<CODEGEN_BEGIN:symbol_enum>>\n"
        "enum Symbol { A, B, C }\n"
        "// <<CODEGEN_END:symbol_enum>>\n"
    )
    result = merge(existing, expected)
    _assert_eq("CODEGEN block replaced", result, expected)


def test_3_user_edit_preserve() -> None:
    print("case 3: USER_EDIT preserve")
    existing = (
        "// <<CODEGEN_BEGIN:feature>>\n"
        "static COL = 5;\n"
        "// <<CODEGEN_END:feature>>\n"
        "// <<USER_EDIT_BEGIN:custom>>\n"
        "static EXPERIMENTAL_MULT = 2.5;\n"
        "public MyHelper() { console.log('hi'); }\n"
        "// <<USER_EDIT_END:custom>>\n"
    )
    expected = (
        "// <<CODEGEN_BEGIN:feature>>\n"
        "static COL = 6;\n"
        "static ROW = 5;\n"
        "// <<CODEGEN_END:feature>>\n"
        "// <<USER_EDIT_BEGIN:custom>>\n"
        "// (default empty slot)\n"
        "// <<USER_EDIT_END:custom>>\n"
    )
    want = (
        "// <<CODEGEN_BEGIN:feature>>\n"
        "static COL = 6;\n"
        "static ROW = 5;\n"
        "// <<CODEGEN_END:feature>>\n"
        "// <<USER_EDIT_BEGIN:custom>>\n"
        "static EXPERIMENTAL_MULT = 2.5;\n"
        "public MyHelper() { console.log('hi'); }\n"
        "// <<USER_EDIT_END:custom>>\n"
    )
    result = merge(existing, expected)
    _assert_eq("USER_EDIT preserved, CODEGEN replaced", result, want)


def test_4_new_anchor_inserted() -> None:
    print("case 4: new anchor inserted (expected has anchor existing lacks)")
    existing = (
        "// <<CODEGEN_BEGIN:a>>\n"
        "old_a\n"
        "// <<CODEGEN_END:a>>\n"
    )
    expected = (
        "// <<CODEGEN_BEGIN:a>>\n"
        "new_a\n"
        "// <<CODEGEN_END:a>>\n"
        "// <<CODEGEN_BEGIN:b>>\n"
        "new_b_inserted\n"
        "// <<CODEGEN_END:b>>\n"
        "// <<USER_EDIT_BEGIN:hook>>\n"
        "// (default empty slot)\n"
        "// <<USER_EDIT_END:hook>>\n"
    )
    result = merge(existing, expected)
    # both new anchors should be present in output in expected's order
    assert "// <<CODEGEN_BEGIN:b>>" in result, "new CODEGEN anchor missing"
    assert "new_b_inserted" in result, "new CODEGEN content missing"
    assert "// <<USER_EDIT_BEGIN:hook>>" in result, "new USER_EDIT anchor missing"
    assert "new_a" in result, "existing anchor CODEGEN not replaced"
    print("  ✓ new anchors appear and existing CODEGEN is replaced")


def test_5_deprecated_codegen() -> None:
    print("case 5: deprecated CODEGEN (existing has anchor expected doesn't)")
    existing = (
        "// <<CODEGEN_BEGIN:a>>\n"
        "keep_a\n"
        "// <<CODEGEN_END:a>>\n"
        "// <<CODEGEN_BEGIN:legacy_jackpot>>\n"
        "handle_jackpot_logic()\n"
        "// <<CODEGEN_END:legacy_jackpot>>\n"
    )
    expected = (
        "// <<CODEGEN_BEGIN:a>>\n"
        "keep_a\n"
        "// <<CODEGEN_END:a>>\n"
    )
    result = merge(existing, expected)
    assert "legacy_jackpot" in result, "deprecated anchor should still be preserved"
    assert "CODEGEN_DEPRECATED" in result, "deprecated anchor should be marked"
    assert "handle_jackpot_logic" in result, "deprecated content preserved"
    print("  ✓ deprecated CODEGEN anchor preserved with warning")


def test_5b_deprecated_user_edit_preserved_silently() -> None:
    print("case 5b: deprecated USER_EDIT preserved without deprecated note")
    existing = (
        "// <<CODEGEN_BEGIN:a>>\n"
        "keep_a\n"
        "// <<CODEGEN_END:a>>\n"
        "// <<USER_EDIT_BEGIN:legacy_hook>>\n"
        "// user added long ago\n"
        "// <<USER_EDIT_END:legacy_hook>>\n"
    )
    expected = (
        "// <<CODEGEN_BEGIN:a>>\n"
        "keep_a\n"
        "// <<CODEGEN_END:a>>\n"
    )
    result = merge(existing, expected)
    assert "legacy_hook" in result, "deprecated USER_EDIT must be preserved"
    assert "// user added long ago" in result, "deprecated USER_EDIT content preserved"
    print("  ✓ deprecated USER_EDIT preserved silently (no deprecated note)")


def test_6_malformed_raises() -> None:
    print("case 6: malformed existing → AnchorError")
    # unmatched BEGIN
    malformed_1 = "// <<CODEGEN_BEGIN:oops>>\nbla\n"
    expected = "// nothing here\n"
    try:
        merge(malformed_1, expected)
    except AnchorError as e:
        print(f"  ✓ AnchorError raised for unmatched BEGIN: {str(e)[:60]}...")
    else:
        raise AssertionError("expected AnchorError for unmatched BEGIN")

    # unmatched END
    malformed_2 = "bla\n// <<CODEGEN_END:oops>>\n"
    try:
        merge(malformed_2, expected)
    except AnchorError as e:
        print(f"  ✓ AnchorError raised for unmatched END: {str(e)[:60]}...")
    else:
        raise AssertionError("expected AnchorError for unmatched END")

    # crossed nesting
    malformed_3 = (
        "// <<CODEGEN_BEGIN:a>>\n"
        "// <<USER_EDIT_BEGIN:b>>\n"
        "// <<CODEGEN_END:a>>\n"
        "// <<USER_EDIT_END:b>>\n"
    )
    try:
        merge(malformed_3, expected)
    except AnchorError as e:
        print(f"  ✓ AnchorError raised for crossed nesting: {str(e)[:60]}...")
    else:
        raise AssertionError("expected AnchorError for crossed nesting")

    # duplicate name
    malformed_4 = (
        "// <<CODEGEN_BEGIN:dup>>\n"
        "first\n"
        "// <<CODEGEN_END:dup>>\n"
        "// <<CODEGEN_BEGIN:dup>>\n"
        "second\n"
        "// <<CODEGEN_END:dup>>\n"
    )
    try:
        merge(malformed_4, expected)
    except AnchorError as e:
        print(f"  ✓ AnchorError raised for duplicate name: {str(e)[:60]}...")
    else:
        raise AssertionError("expected AnchorError for duplicate name")


def test_idempotent() -> None:
    print("idempotent: merge(merge(a, b), b) == merge(a, b)")
    existing = (
        "// header\n"
        "// <<CODEGEN_BEGIN:x>>\n"
        "old\n"
        "// <<CODEGEN_END:x>>\n"
        "// <<USER_EDIT_BEGIN:custom>>\n"
        "user code 1\n"
        "user code 2\n"
        "// <<USER_EDIT_END:custom>>\n"
    )
    expected = (
        "// header\n"
        "// <<CODEGEN_BEGIN:x>>\n"
        "new_x_content\n"
        "// <<CODEGEN_END:x>>\n"
        "// <<USER_EDIT_BEGIN:custom>>\n"
        "// (default empty slot)\n"
        "// <<USER_EDIT_END:custom>>\n"
    )
    once = merge(existing, expected)
    twice = merge(once, expected)
    _assert_eq("idempotent merge", twice, once)


def test_nested_user_edit_inside_codegen() -> None:
    print("nested: USER_EDIT inside CODEGEN preserved across CODEGEN rewrite")
    existing = (
        "// <<CODEGEN_BEGIN:outer>>\n"
        "outer line 1\n"
        "// <<USER_EDIT_BEGIN:inner>>\n"
        "user's inner code\n"
        "// <<USER_EDIT_END:inner>>\n"
        "outer line 2\n"
        "// <<CODEGEN_END:outer>>\n"
    )
    expected = (
        "// <<CODEGEN_BEGIN:outer>>\n"
        "BRAND NEW outer line A\n"
        "// <<USER_EDIT_BEGIN:inner>>\n"
        "// (default)\n"
        "// <<USER_EDIT_END:inner>>\n"
        "BRAND NEW outer line B\n"
        "// <<CODEGEN_END:outer>>\n"
    )
    result = merge(existing, expected)
    # expected: CODEGEN rewritten, but USER_EDIT nested inner preserved
    assert "BRAND NEW outer line A" in result, "outer CODEGEN (part A) should be rewritten"
    assert "BRAND NEW outer line B" in result, "outer CODEGEN (part B) should be rewritten"
    assert "user's inner code" in result, "USER_EDIT inner should be preserved"
    assert "// (default)" not in result, "expected default should be overridden by existing user edit"
    print("  ✓ nested USER_EDIT preserved when outer CODEGEN rewritten")


def main() -> int:
    print("=" * 60)
    print("anchor_merge smoke test")
    print("=" * 60)

    tests = [
        test_1_new_file,
        test_2_codegen_overwrite,
        test_3_user_edit_preserve,
        test_4_new_anchor_inserted,
        test_5_deprecated_codegen,
        test_5b_deprecated_user_edit_preserved_silently,
        test_6_malformed_raises,
        test_idempotent,
        test_nested_user_edit_inside_codegen,
    ]

    failures = 0
    for t in tests:
        try:
            t()
            print()
        except Exception as e:
            failures += 1
            print(f"  ✗ FAILED: {t.__name__}: {e}")
            print()

    print("=" * 60)
    if failures == 0:
        print(f"ALL {len(tests)} tests passed")
        return 0
    else:
        print(f"{failures} / {len(tests)} tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
