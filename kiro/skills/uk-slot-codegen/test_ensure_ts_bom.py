import tempfile
import unittest
from pathlib import Path

from ensure_ts_bom import UTF8_BOM, ensure_bom_for_target


class EnsureTsBomTests(unittest.TestCase):
    def test_adds_bom_once_to_owned_typescript_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # ensure_bom_for_target() 會 resolve()，Windows 上 TEMP 若是 8.3 短檔名
            # （C:\Users\JIUNCH~1\...）會展開成長路徑，預期值必須先對齊
            root = Path(tmp).resolve()
            script_dir = root / "assets" / "Script"
            script_dir.mkdir(parents=True)
            proto = script_dir / "Proto.ts"
            existing = script_dir / "Existing.ts"
            proto.write_bytes(b"export default protocol;\n")
            existing.write_bytes(UTF8_BOM + b"export const ok = true;\n")

            changed = ensure_bom_for_target(root)
            changed_again = ensure_bom_for_target(root)

            self.assertEqual([proto], changed)
            self.assertEqual([], changed_again)
            self.assertEqual(UTF8_BOM + b"export default protocol;\n", proto.read_bytes())
            self.assertEqual(UTF8_BOM + b"export const ok = true;\n", existing.read_bytes())


if __name__ == "__main__":
    unittest.main()
