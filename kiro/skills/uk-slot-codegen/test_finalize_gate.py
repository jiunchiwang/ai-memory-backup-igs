import subprocess
import tempfile
import unittest
from pathlib import Path

from check_regression_v2 import CheckResult, has_blocking_results
from gate_runner import AI_ARTIFACT_PATHS, gate_3_2, gate_git, gate_report, gate_traceability


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


class GitGateTest(unittest.TestCase):
    """gate_git 的三條斷言各自都要紅得起來——只驗綠燈等於沒驗。"""

    def _run(self, root: Path) -> dict:
        return {item["name"]: item for item in gate_git(root)}

    def _git(self, root: Path, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(root), "-c", "user.email=t@example.com", "-c", "user.name=t", *args],
            check=True, capture_output=True,
        )

    def _init_with_commit(self, root: Path) -> None:
        self._git(root, "init", "-b", "main")
        (root / "README.md").write_text("x", encoding="utf-8")
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", "init")

    def test_red_without_repo(self):
        root = Path(tempfile.mkdtemp())
        checks = self._run(root)
        self.assertFalse(checks["git_repo_exists"]["pass"])
        # 沒有 .git 時提早返回，不該假裝驗過其餘兩條（鎖總數而非個別 key，
        # 否則把某一條搬進早退分支仍會綠）
        self.assertEqual(list(checks), ["git_repo_exists"])

    def test_green_for_fresh_repo(self):
        root = Path(tempfile.mkdtemp())
        self._init_with_commit(root)
        checks = self._run(root)
        self.assertTrue(all(item["pass"] for item in checks.values()), checks)

    def test_red_when_init_without_commit(self):
        """init 成功但 commit 失敗（新機器未設 user.email）→ 空 repo。"""
        root = Path(tempfile.mkdtemp())
        self._git(root, "init", "-b", "main")
        checks = self._run(root)
        self.assertTrue(checks["git_repo_exists"]["pass"])
        self.assertFalse(checks["git_has_commit"]["pass"])

    def test_red_when_ai_artifacts_tracked(self):
        """.kiro/ 與 AI.md 被 commit 進遊戲 repo（clash_of_olympus 首次 commit 的形狀）。"""
        root = Path(tempfile.mkdtemp())
        self._init_with_commit(root)
        (root / ".kiro" / "skills").mkdir(parents=True)
        (root / ".kiro" / "skills" / "SKILL.md").write_text("x", encoding="utf-8")
        (root / "AI.md").write_text("x", encoding="utf-8")
        self._git(root, "add", "-A")
        self._git(root, "commit", "-m", "leak")
        checks = self._run(root)
        self.assertTrue(checks["git_has_commit"]["pass"])
        self.assertFalse(checks["git_no_ai_artifacts"]["pass"])
        self.assertIn("AI.md", checks["git_no_ai_artifacts"]["detail"])

    # 期望值硬寫在測試裡，**不是** import AI_ARTIFACT_PATHS——拿被測物自己的常數
    # 當期望值，等於「清單移掉一項，測試就跟著不測那項」，漏列永遠測不出來。
    # 2026-08-12 mutation 實測：先寫成遍歷 AI_ARTIFACT_PATHS，移除 ".kiro" 後
    # 測試仍全綠（存活突變體）；改成下面這份獨立清單才殺得掉。
    # 來源：前 8 項是 uk_917 的 .gitignore（實查最完整的一份）；後 3 項是其他 AI
    # 工具目錄，**沒有任何專案的 .gitignore 有目錄層級的擋法**——uk_872 只有逐檔
    # glob（`/.claudedocs/*.md`、`/.agents/skills/.../*.py` 之類 78 條），其餘專案
    # 靠 local-only 的 .git/info/exclude（見 gate_runner.AI_ARTIFACT_PATHS 註解）。
    EXPECTED_AI_ARTIFACTS = (
        ".kiro",
        "docs",
        "scratch",
        "AI.md",
        "SPEC.md",
        "ART_ASSET_MANIFEST.md",
        "uk-slot-state-machine.skill",
        ".codegen-checkpoint.json",
        ".claudedocs",
        ".claude-loop",
        ".agents",
    )

    def test_ai_artifact_list_matches_project_convention(self):
        """清單本身不得被悄悄縮減——與 uk_917 慣例的獨立副本比對。"""
        self.assertEqual(set(AI_ARTIFACT_PATHS), set(self.EXPECTED_AI_ARTIFACTS))

    def test_each_ai_artifact_path_is_detected(self):
        """慣例清單裡的每一項都要能單獨觸發紅燈。

        只用「.kiro + AI.md 一起洩漏」測是不夠的——任一項還在清單裡就會紅，
        ∴ 從清單移掉某一項（例如 .kiro）測試仍全綠。2026-08-12 mutation 實測
        確認過這個存活突變體，這支就是為了殺它。
        """
        for path in self.EXPECTED_AI_ARTIFACTS:
            with self.subTest(path=path):
                root = Path(tempfile.mkdtemp())
                self._init_with_commit(root)
                target = root / path
                if path.endswith((".md", ".json", ".skill")):
                    target.write_text("x", encoding="utf-8")
                else:
                    target.mkdir(parents=True)
                    (target / "leaked.txt").write_text("x", encoding="utf-8")
                self._git(root, "add", "-A", "-f")
                self._git(root, "commit", "-m", "leak")
                checks = self._run(root)
                self.assertFalse(
                    checks["git_no_ai_artifacts"]["pass"],
                    f"{path} 被追蹤卻沒紅——它可能不在 AI_ARTIFACT_PATHS 裡",
                )

    def test_red_when_ls_files_fails(self):
        """`ls-files` 查不了時必須紅——空 stdout 會讓它長得像「查過了沒事」。"""
        root = Path(tempfile.mkdtemp())
        self._init_with_commit(root)
        # 讓 ls-files 非零退出但 rev-parse 仍成功：塞一個壞掉的 index
        (root / ".git" / "index").write_bytes(b"garbage-not-an-index")
        checks = self._run(root)
        self.assertFalse(checks["git_no_ai_artifacts"]["pass"])
        self.assertIn("ls-files 失敗", checks["git_no_ai_artifacts"]["detail"])

    def test_red_for_leftover_template_clone(self):
        """Step 0.0 的 rm .git 失敗 → 專案帶著模板 history，且 Step 0.2 會被跳過。"""
        root = Path(tempfile.mkdtemp())
        self._init_with_commit(root)
        self._git(root, "remote", "add", "origin",
                  "git@github.com:IGS-ARCADE-DIVISION-RD2/uk_slot_template.git")
        checks = self._run(root)
        self.assertTrue(checks["git_repo_exists"]["pass"])
        self.assertTrue(checks["git_has_commit"]["pass"])
        self.assertFalse(checks["git_not_template_clone"]["pass"])


if __name__ == "__main__":
    unittest.main()
