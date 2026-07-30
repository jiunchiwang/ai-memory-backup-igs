import unittest
from pathlib import Path


ROOT = Path(__file__).parent


class ContractDocsTest(unittest.TestCase):
    def test_audio_contract_uses_audio_manager(self):
        flow = (ROOT / "_flow.md").read_text(encoding="utf-8")
        api = (ROOT / "_api-ref.md").read_text(encoding="utf-8")
        self.assertNotIn("Game_Define.AudioClips", flow)
        self.assertNotIn("static AudioClips", api)
        self.assertIn("AudioManager.AudioClips", flow)

    def test_tumble_contract_is_consistent(self):
        api = (ROOT / "_api-ref.md").read_text(encoding="utf-8")
        gates = (ROOT / "_gates.md").read_text(encoding="utf-8")
        self.assertIn("SetSpinMode(SpinMode.Tumble, new TumbleFillStrategy())", api)
        self.assertIn("SpinMode\\.Tumble", gates)

    def test_proto_contract_has_single_bridge_instruction(self):
        flow = (ROOT / "_flow.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("替換所有 .ts 中 proto import 為", flow)
        self.assertIn("<ns>Proto.js", flow)
        self.assertNotIn("| `compile-proto.js` | Step 3.3", skill)

    def test_validate_markdown_and_extension_sync_are_explicit(self):
        flow = (ROOT / "_flow.md").read_text(encoding="utf-8")
        self.assertIn("validate |", flow)
        self.assertIn("Step 0 → 4a → 5", flow)
        self.assertIn("filesystem copy", flow)
        self.assertIn("git pull --ff-only", flow)
        self.assertIn("git clone <repo_url>", flow)

    def test_step5_requires_finalize_before_checkpoint_cleanup(self):
        flow = (ROOT / "_flow.md").read_text(encoding="utf-8")
        self.assertIn("--step prefinalize", flow)
        self.assertIn("--step finalize", flow)
        self.assertIn("只有 finalize `all_pass=true` 才能清除 checkpoint", flow)

    def test_server_only_symbols_are_not_client_assets(self):
        flow = (ROOT / "_flow.md").read_text(encoding="utf-8")
        gates = (ROOT / "_gates.md").read_text(encoding="utf-8")
        pitfalls = (ROOT / "_pitfalls.md").read_text(encoding="utf-8")
        for text in (flow, gates, pitfalls):
            self.assertIn("server_only", text)
        self.assertIn("不得放進 `Game_Define.Symbol`", flow)
        self.assertIn("非 server_only SymID", gates)

    def test_headless_flow_repairs_bom_before_compile(self):
        flow = (ROOT / "_flow.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("ensure_ts_bom.py", flow)
        self.assertLess(flow.index("ensure_ts_bom.py"), flow.index("verify_compile.py"))
        self.assertIn("ensure_ts_bom.py", skill)


if __name__ == "__main__":
    unittest.main()
