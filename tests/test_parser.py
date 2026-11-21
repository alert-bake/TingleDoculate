import unittest

from tingledoculate.parser import page_title, plain_text, rewrite_markdown_links


class ParserTests(unittest.TestCase):
    def test_title_uses_first_h1(self):
        self.assertEqual(page_title("Intro\n\n# API Reference\n", "fallback"), "API Reference")

    def test_title_falls_back_to_filename(self):
        self.assertEqual(page_title("No heading", "custom-command"), "Custom Command")

    def test_markdown_links_become_html_links(self):
        rendered = '<p><a href="guide.md#setup">Guide</a></p>'
        self.assertEqual(
            rewrite_markdown_links(rendered),
            '<p><a href="guide.html#setup">Guide</a></p>',
        )

    def test_plain_text_decodes_entities_and_removes_tags(self):
        self.assertEqual(plain_text("<p>Lua &amp; commands</p>"), "Lua & commands")


if __name__ == "__main__":
    unittest.main()
