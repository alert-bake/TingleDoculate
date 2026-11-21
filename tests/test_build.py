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
            self.assertIn('data-theme="dark"', home)
            self.assertIn('data-theme-toggle', home)
            self.assertIn('class="icon-sun"', home)
            self.assertIn('class="icon-moon"', home)
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

    def test_theme_palettes_are_configurable_and_invalidate_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "index.md").write_text("# Home", encoding="utf-8")
            config = root / "tingledoculate.toml"
            config.write_text(
                '[site]\nsource = "docs"\noutput = "site"\n'
                '[theme]\ndefault_mode = "light"\n'
                '[theme.dark]\nbackground = "#121212"\n'
                '[theme.light]\nbackground = "#FAFAFA"\n',
                encoding="utf-8",
            )

            first = build(root)
            page = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-theme="light"', page)
            self.assertIn('html[data-theme="dark"]{--bg:#121212', page)
            self.assertIn('html[data-theme="light"]{--bg:#FAFAFA', page)
            self.assertEqual(first["rendered"], 1)

            config.write_text(
                '[site]\nsource = "docs"\noutput = "site"\n'
                '[theme]\ndefault_mode = "dark"\n'
                '[theme.dark]\nbackground = "#131313"\n',
                encoding="utf-8",
            )
            second = build(root)
            self.assertEqual(second["rendered"], 1)
            updated = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-theme="dark"', updated)
            self.assertIn('--bg:#131313', updated)


if __name__ == "__main__":
    unittest.main()
