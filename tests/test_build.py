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

    def test_htmd_color_html_and_syntax_highlighting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            fence = chr(96) * 3
            (docs / "index.md").write_text(
                '# Aizo\n\n<color="FF00FF">pink</color>\n\n'
                + fence + 'python\nprint("hello")\n' + fence + '\n\n'
                + '<script>alert(1)</script><strong>safe</strong>',
                encoding="utf-8",
            )
            (root / "tingledoculate.toml").write_text(
                '[site]\nsource = "docs"\noutput = "site"\n'
                '[markdown]\nhtml = true\n'
                '[highlight]\nenabled = true\ntheme = "monokai"\n',
                encoding="utf-8",
            )

            build(root)
            page = (root / "site" / "index.html").read_text(encoding="utf-8")
            css = (root / "site" / "assets" / "tingledoculate.css").read_text(encoding="utf-8")
            self.assertIn('style="color:#FF00FF"', page)
            self.assertIn("<strong>safe</strong>", page)
            self.assertNotIn("<script>", page)
            self.assertIn('class="k"', page)
            self.assertIn("pre code .k", css)

    def test_htmd_color_works_when_raw_html_is_disabled(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            docs = root / "docs"
            docs.mkdir()
            (docs / "index.md").write_text(
                '<color="FF00FF">pink</color>\n\n<span>raw HTML</span>',
                encoding="utf-8",
            )
            (root / "tingledoculate.toml").write_text(
                '[site]\nsource = "docs"\noutput = "site"\n',
                encoding="utf-8",
            )

            build(root)
            page = (root / "site" / "index.html").read_text(encoding="utf-8")
            self.assertIn('style="color:#FF00FF"', page)
            self.assertIn("&lt;span&gt;raw HTML&lt;/span&gt;", page)


if __name__ == "__main__":
    unittest.main()
