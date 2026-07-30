import tempfile
import unittest
from pathlib import Path

from check_regression_v2 import CheckResult, has_blocking_results
from gate_runner import gate_3_2, gate_report, gate_traceability


class FinalizeGateTest(unittest.TestCase):
    def test_state_enum_parser_ignores_comments(self):
        root = Path(tempfile.mkdtemp())
        script = root / "assets" / "Script"
        states = script / "GameState"
        states.mkdir(parents=True)
        (script / "Game_Define.ts").write_text(
            "enum GAMEVIEW_STATE {\n"
            "  // Tumble / Cascade 消除狀態\n"
            "  WAIT_READY = 0,\n"
            "  AWARD, // COLLECT 收分演出\n"
            "}\n",
            encoding="utf-8",
        )
        (script / "GameView.ts").write_text(
            "Game_Define.GameState.WAIT_READY;\n"
            "Game_Define.GameState.AWARD;\n"
            "CommonState.END;\n"
            "RetryRoundEnd() { return; }\n",
            encoding="utf-8",
        )
        (states / "RoundShowEndState.ts").write_text(
            "CommonState.COMMON_SHOW;\n", encoding="utf-8"
        )
        checks = gate_3_2(root)
        enum_check = next(item for item in checks if item["name"] == "enum↔register")
        self.assertTrue(enum_check["pass"], enum_check["detail"])

    def test_regression_skip_is_blocking(self):
        results = [CheckResult("symbol_count", "SKIP", "spec has no symbol table")]
        self.assertTrue(has_blocking_results(results))

    def test_report_requires_all_sections_and_unfinished_checklist(self):
        root = Path(tempfile.mkdtemp())
        report = root / "scratch" / "codegen-report.md"
        report.parent.mkdir(parents=True)
        report.write_text("# Codegen Report\n", encoding="utf-8")
        self.assertFalse(all(item["pass"] for item in gate_report(root)))

        report.write_text(
            "# Codegen Report\n\n"
            "## 無頭階段完成項目\n- compile\n\n"
            "## Gate 結果\n- traceability: codegen 4/4; deferred M2+ 1; inferred defaults 2/4 verified\n\n"
            "## 後續未完成工項\n- [ ] Preview 驗證\n\n"
            "## 已知風險\n- Runtime 未驗證\n",
            encoding="utf-8",
        )
        self.assertTrue(all(item["pass"] for item in gate_report(root)))

    def test_traceability_deferred_is_reported_without_blocking(self):
        root = Path(tempfile.mkdtemp())
        spec = root / "scratch" / "Game_Spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text("- rule [SPEC:BD-1]\n", encoding="utf-8")
        (root / "assets" / "Script").mkdir(parents=True)

        checks = gate_traceability(root)
        self.assertTrue(all(item["pass"] for item in checks))
        self.assertTrue(any("codegen 0/0" in item["detail"] for item in checks))
        self.assertTrue(any("deferred M2+ 1" in item["detail"] for item in checks))


if __name__ == "__main__":
    unittest.main()
