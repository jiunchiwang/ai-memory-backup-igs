import json
import tempfile
import unittest
from pathlib import Path

from gate_runner import gate_traceability
from spec_traceability import build_traceability, parse_spec_items, tag_spec, write_manifest


SPEC = """\
## 1. 基本資訊
- **盤面**: 3×5 [SPEC:OV-1]

## 2. Symbol 清單
| SymID | Symbol Name | 類型 | [SPEC:BD-1]
| 0 | WILD | 特殊 | [SPEC:BD-2]

## 3. 特色功能
### 3.1 Clover Bomb [SPEC:SYM-1]

## 6. 音效清單
| Key | FileName | 說明 | [SPEC:RSP-1]
| MG_BGM | MG_BGM | 主遊戲 | [SPEC:RSP-2]

## 7. 盤面配置
- **COL**: 5 [SPEC:FG-1]
- **SymbolWidth**: 123 [SPEC:FG-2]
- **SymbolHeight**: 114 [SPEC:FG-3]
- **SeparateLineWidth**: 4 [SPEC:FG-4]
- **MIDDLE_PLATE_INDEX**: 1 [SPEC:FG-5]
"""


def make_fixture(include_audio: bool = True) -> tuple[Path, Path]:
    root = Path(tempfile.mkdtemp())
    spec = root / "scratch" / "Game_Spec.md"
    spec.parent.mkdir(parents=True)
    spec.write_text(SPEC, encoding="utf-8")
    (root / "scratch" / "Game_Summary_File.md").write_text("summary", encoding="utf-8")

    script = root / "assets" / "Script"
    script.mkdir(parents=True)
    (script / "Game_Define.ts").write_text(
        "export enum Symbol { WILD = 0 }\n"
        "export class Game_Define { static COL = 5; static ROW = 3; "
        "static SymbolWidth = 123; static SymbolHeight = 114; "
        "static SeparateLineWidth = 0; }\n",
        encoding="utf-8",
    )
    (script / "SlotReels.ts").write_text("Game_Define.COL;\n", encoding="utf-8")
    if include_audio:
        audio = script / "Audio"
        audio.mkdir()
        (audio / "AudioManager.ts").write_text(
            'static AudioClips = { MG_BGM: { FileName: "MG_BGM" } };\n',
            encoding="utf-8",
        )
    return root, spec


class ScopedTraceabilityTests(unittest.TestCase):
    def test_classifies_codegen_deferred_and_informational_items(self) -> None:
        root, spec = make_fixture()

        items = parse_spec_items(spec)
        by_id = {item["id"]: item for item in items}

        self.assertEqual("codegen", by_id["OV-1"]["scope"])
        self.assertEqual("informational", by_id["BD-1"]["scope"])
        self.assertEqual("codegen", by_id["BD-2"]["scope"])
        self.assertEqual("deferred", by_id["SYM-1"]["scope"])
        self.assertEqual("informational", by_id["RSP-1"]["scope"])
        self.assertEqual("codegen", by_id["RSP-2"]["scope"])
        self.assertEqual("codegen", by_id["FG-1"]["scope"])
        self.assertEqual("inferred", by_id["FG-2"]["scope"])
        self.assertEqual("inferred", by_id["FG-3"]["scope"])
        self.assertEqual("inferred", by_id["FG-4"]["scope"])
        self.assertEqual("inferred", by_id["FG-5"]["scope"])

    def test_builds_manifest_with_artifact_evidence(self) -> None:
        root, spec = make_fixture()

        manifest = build_traceability(spec, root)

        self.assertEqual(4, manifest["summary"]["codegen_total"])
        self.assertEqual(4, manifest["summary"]["codegen_covered"])
        self.assertEqual(0, manifest["summary"]["codegen_uncovered"])
        self.assertEqual(1, manifest["summary"]["deferred_total"])
        self.assertEqual(2, manifest["summary"]["informational_total"])
        self.assertEqual(4, manifest["summary"]["inferred_total"])
        self.assertEqual(2, manifest["summary"]["inferred_verified"])
        self.assertEqual(2, manifest["summary"]["inferred_review"])
        for item in manifest["items"]:
            if item["scope"] == "codegen":
                self.assertTrue(item["evidence"], item)

        output = root / "scratch" / "codegen-traceability.json"
        write_manifest(spec, root, output)
        self.assertEqual(manifest["summary"], json.loads(output.read_text(encoding="utf-8"))["summary"])

    def test_missing_codegen_evidence_blocks_gate_but_deferred_does_not(self) -> None:
        root, _ = make_fixture(include_audio=False)

        checks = gate_traceability(root)

        self.assertFalse(all(item["pass"] for item in checks))
        self.assertTrue(any("RSP-2" in item["detail"] for item in checks))
        self.assertFalse(any("SYM-1" in item["detail"] and not item["pass"] for item in checks))

    def test_gate_reports_scoped_counts_instead_of_zero_over_all(self) -> None:
        root, _ = make_fixture()

        checks = gate_traceability(root)

        self.assertTrue(all(item["pass"] for item in checks), checks)
        self.assertTrue(any("codegen 4/4" in item["detail"] for item in checks))
        self.assertTrue(any("deferred M2+ 1" in item["detail"] for item in checks))
        self.assertTrue(any("inferred defaults 2/4 verified" in item["detail"] for item in checks))

    def test_inferred_defaults_never_block_codegen_gate(self) -> None:
        root, _ = make_fixture()

        checks = gate_traceability(root)

        self.assertTrue(all(item["pass"] for item in checks), checks)
        self.assertTrue(any("inferred defaults 2/4 verified" in item["detail"] for item in checks))

    def test_source_marker_promotes_real_spec_value_to_blocking_codegen_contract(self) -> None:
        root, spec = make_fixture()
        content = spec.read_text(encoding="utf-8").replace(
            "**SeparateLineWidth**: 4 [SPEC:FG-4]",
            "**SeparateLineWidth**: 4 [SOURCE:xlsx] [SPEC:FG-4]",
        )
        spec.write_text(content, encoding="utf-8")

        by_id = {item["id"]: item for item in parse_spec_items(spec)}
        checks = gate_traceability(root)

        self.assertEqual("codegen", by_id["FG-4"]["scope"])
        self.assertFalse(all(item["pass"] for item in checks))
        self.assertTrue(any("FG-4" in item["detail"] for item in checks))

    def test_explicit_reference_does_not_hide_wrong_codegen_value(self) -> None:
        root, spec = make_fixture()
        game_define = root / "assets" / "Script" / "Game_Define.ts"
        game_define.write_text(
            "// [SPEC:OV-1]\n"
            "export enum Symbol { WILD = 0 }\n"
            "export class Game_Define { static COL = 5; static ROW = 4; }\n",
            encoding="utf-8",
        )

        manifest = build_traceability(spec, root)
        item = next(item for item in manifest["items"] if item["id"] == "OV-1")

        self.assertEqual("uncovered", item["status"])
        self.assertEqual({"ROW": 3, "COL": 5}, item["diagnostic"]["expected"])
        self.assertEqual({"ROW": 4, "COL": 5}, item["diagnostic"]["actual"])
        self.assertTrue(any(e["contract"] == "explicit SPEC reference" for e in item["evidence"]))

    def test_tag_spec_is_stable_and_skips_table_headers(self) -> None:
        root = Path(tempfile.mkdtemp())
        spec = root / "Game_Spec.md"
        spec.write_text(
            "## 2. Symbol 清單\n"
            "| SymID | Symbol Name |\n"
            "| --- | --- |\n"
            "| 0 | WILD | [SPEC:BD-1]\n"
            "| 1 | SCATTER |\n",
            encoding="utf-8",
        )

        tag_spec(spec)
        first = spec.read_text(encoding="utf-8")
        tag_spec(spec)

        self.assertNotIn("SymID | Symbol Name | [SPEC:", first)
        self.assertIn("| 1 | SCATTER | [SPEC:BD-2]", first)
        self.assertEqual(first, spec.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
