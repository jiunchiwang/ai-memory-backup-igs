import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verify_compile import (
    check_typescript_compile,
    classify_typescript_diagnostics,
    resolve_typescript_compiler,
)


class TypeScriptGateTest(unittest.TestCase):
    def test_classifies_only_project_sources_as_blocking(self):
        target = Path("C:/work/game")
        output = "\n".join([
            "assets/Script/GameView.ts(1,2): error TS2339: bad",
            "assets/game/Script/Feature.ts(2,2): error TS2339: bad game script",
            "tests/Foo.test.ts(2,3): error TS2304: bad test",
            "C:/ProgramData/cocos/cc.d.ts(4,5): error TS2416: framework noise",
            "extensions/foo/index.ts(6,7): error TS2307: extension noise",
        ])
        owned, ignored = classify_typescript_diagnostics(output, target)
        self.assertEqual(3, len(owned))
        self.assertEqual(2, ignored)

    def test_external_errors_do_not_fail_compile_gate(self):
        root = Path(tempfile.mkdtemp())
        (root / "tsconfig.json").write_text("{}", encoding="utf-8")
        completed = subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout="extensions/foo.ts(1,1): error TS2307: ignored\n", stderr="",
        )
        with patch("verify_compile.resolve_typescript_compiler", return_value=(["node", "tsc"], "fake")):
            with patch("verify_compile.subprocess.run", return_value=completed):
                result = check_typescript_compile(root)
        self.assertEqual([], result["errors"])
        self.assertEqual(1, result["ignored_errors"])

    def test_project_error_fails_compile_gate(self):
        root = Path(tempfile.mkdtemp())
        (root / "tsconfig.json").write_text("{}", encoding="utf-8")
        completed = subprocess.CompletedProcess(
            args=[], returncode=1,
            stdout="assets/Script/Bad.ts(1,1): error TS2322: bad\n", stderr="",
        )
        with patch("verify_compile.resolve_typescript_compiler", return_value=(["node", "tsc"], "fake")):
            with patch("verify_compile.subprocess.run", return_value=completed):
                result = check_typescript_compile(root)
        self.assertEqual(1, len(result["errors"]))

    def test_missing_compiler_is_actionable_failure(self):
        root = Path(tempfile.mkdtemp())
        with patch.dict("verify_compile.os.environ", {}, clear=True):
            with patch(
                "verify_compile.shutil.which",
                side_effect=lambda name: "C:/node.exe" if name == "node" else None,
            ):
                command, detail = resolve_typescript_compiler(root)
        self.assertIsNone(command)
        self.assertIn("Install target devDependency", detail)


if __name__ == "__main__":
    unittest.main()
