import tempfile
import unittest
from pathlib import Path

from check_regression_v2 import check_symbol_count, parse_client_game_define, parse_game_spec


SPEC_WITH_SERVER_ONLY = """\
## 1. Symbols

| ID | Symbol | Type | Note |
|---:|---|---|---|
| 0 | WILD | special | client |
| 1 | A | normal | client |
| 2 | SCATTER | server_only | server |
| 3 | MY1 | server_only | server |
"""


def write_game_define(root: Path, enum_body: str, symbol_count: int) -> None:
    script_dir = root / "assets" / "Script"
    script_dir.mkdir(parents=True)
    (script_dir / "Game_Define.ts").write_text(
        "export enum Symbol {\n"
        f"{enum_body}\n"
        "}\n"
        "export default class Game_Define {\n"
        f"    static SYMBOL_COUNT = {symbol_count};\n"
        "}\n",
        encoding="utf-8",
    )


class SymbolRegressionTests(unittest.TestCase):
    def test_server_only_symbols_are_excluded_from_client_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_game_define(root, "    WILD = 0,\n    A = 1,", 2)

            result = check_symbol_count(
                parse_game_spec(SPEC_WITH_SERVER_ONLY),
                parse_client_game_define(root),
            )

            self.assertEqual("PASS", result.status, result.details)
            self.assertIn("client IDs=[0, 1]", result.message)

    def test_missing_client_symbol_reports_its_sym_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_game_define(root, "    WILD = 0,", 1)

            result = check_symbol_count(
                parse_game_spec(SPEC_WITH_SERVER_ONLY),
                parse_client_game_define(root),
            )

            self.assertEqual("FAIL", result.status)
            self.assertTrue(any("missing client SymID: 1" in item for item in result.details))

    def test_declared_symbol_count_must_match_client_enum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_game_define(root, "    WILD = 0,\n    A = 1,", 4)

            result = check_symbol_count(
                parse_game_spec(SPEC_WITH_SERVER_ONLY),
                parse_client_game_define(root),
            )

            self.assertEqual("FAIL", result.status)
            self.assertTrue(any("SYMBOL_COUNT=4" in item for item in result.details))


if __name__ == "__main__":
    unittest.main()
