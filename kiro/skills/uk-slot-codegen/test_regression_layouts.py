import tempfile
import unittest
from pathlib import Path

from check_regression_v2 import (
    check_normal_columns,
    check_variable_board,
    parse_client_game_define,
    parse_client_slot_reels,
    parse_game_spec,
)
from gate_runner import visible_row_start


def write_client(root: Path, slot_reels: str) -> None:
    script_dir = root / "assets" / "Script"
    script_dir.mkdir(parents=True)
    (script_dir / "Game_Define.ts").write_text(
        "export class Game_Define {\n"
        "    static COL = 5;\n"
        "    static ROW = 3;\n"
        "    static MAX_ROW = 5;\n"
        "    static FULL_PLATE_NUM = 15;\n"
        "}\n",
        encoding="utf-8",
    )
    (script_dir / "SlotReels.ts").write_text(slot_reels, encoding="utf-8")


class LayoutRegressionTests(unittest.TestCase):
    def test_visible_window_alignment_directions(self) -> None:
        self.assertEqual(0, visible_row_start(5, 3, "top"))
        self.assertEqual(1, visible_row_start(5, 3, "center"))
        self.assertEqual(2, visible_row_start(5, 3, "bottom"))
        self.assertEqual(0, visible_row_start(5, 5, "bottom"))

    def test_dynamic_normal_columns_derived_from_col_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_client(
                root,
                "const NORMAL_COLUMNS = Array.from( { length: Game_Define.COL }, ( _, i ) => i );\n",
            )
            spec = parse_game_spec("COL: 5\nROW: 3\n")

            result = check_normal_columns(spec, parse_client_slot_reels(root))

            self.assertEqual("PASS", result.status, result.message)
            self.assertIn("Game_Define.COL", result.message)

    def test_unicode_multi_mode_uniform_layout_passes_single_mask(self) -> None:
        spec = parse_game_spec(
            "- **COL**: 5\n- **ROW**: 3\n- **FULL_PLATE_NUM**: 15\n"
            "- **BoardLayout**: 3×3×3×3×3（MG）/ 5×5×5×5×5（FG EXPAND）\n"
        )
        self.assertEqual((5, 3, 15), (spec["COL"], spec["ROW"], spec["FULL_PLATE_NUM"]))
        self.assertEqual([[3, 3, 3, 3, 3], [5, 5, 5, 5, 5]], spec["BoardLayouts"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_client(root, "private m_reelMask = null;\n")
            result = check_variable_board(
                spec,
                parse_client_game_define(root),
                parse_client_slot_reels(root),
                {},
            )

            self.assertEqual("PASS", result.status, result.details)
            self.assertIn("multi-mode uniform", result.message)

    def test_unicode_per_column_layout_still_requires_mask_array(self) -> None:
        spec = parse_game_spec("COL: 5\nROW: 5\nBoardLayout: 5×4×4×4×5\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_client(root, "private m_reelMask = null;\n")
            result = check_variable_board(
                spec,
                parse_client_game_define(root),
                parse_client_slot_reels(root),
                {},
            )

            self.assertEqual("FAIL", result.status)
            self.assertTrue(any("m_reelMasks" in item for item in result.details))


if __name__ == "__main__":
    unittest.main()
