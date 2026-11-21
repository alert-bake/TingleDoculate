import tempfile
import unittest
from pathlib import Path

from tingledoculate.build import build


class BuildTests(unittest.TestCase):
    def test_incremental_build_and_nested_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            (docs / "api").mkdir(parents=True)
            (docs / "index.md").write_text("# Home\n\n[API](api/index.md)", encoding="utf-8")
            (docs / "api" / "index.md").write_text("# API\n\nLuaJ reference.", encoding="utf-8")
            (root / "tingledoculate.toml").write_text(
                '[site]\ntitle = "Test Wiki"\nsource = "docs"\noutput = "site"\n',
                encoding="utf-8",
            )

            first = build(root)
            self.assertEqual(first, {"pages": 2, "rendered": 2, "skipped": 0})
            home = (root / "site" / "index.html").read_text(encoding="utf-8")
            nested = (root / "site" / "api" / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="api/index.html"', home)
            self.assertIn('href="../assets/tingledoculate.css"', nested)
            self.assertTrue((root / "site" / "search-index.json").is_file())

            second = build(root)
            self.assertEqual(second, {"pages": 2, "rendered": 0, "skipped": 2})

            (docs / "api" / "index.md").write_text("# API\n\nUpdated reference.", encoding="utf-8")
            third = build(root)
            self.assertEqual(third, {"pages": 2, "rendered": 1, "skipped": 1})

            (docs / "api" / "index.md").unlink()
            fourth = build(root)
            self.assertEqual(fourth, {"pages": 1, "rendered": 1, "skipped": 0})
            self.assertFalse((root / "site" / "api" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
