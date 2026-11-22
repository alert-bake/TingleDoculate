import unittest

from tingledoculate.parser import (
    make_markdown_parser,
    page_title,
    plain_text,
    render_markdown,
    rewrite_markdown_links,
)


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

    def test_htmd_icons_render_inline_svg_with_default_and_override_sets(self):
        parser = make_markdown_parser()
        rendered = render_markdown(
            parser,
            '<icon="Sun"> <icon="home" set="material">',
            icon_config={"default_set": "lucide"},
        )
        self.assertIn('class="td-icon td-icon-lucide"', rendered)
        self.assertIn('class="td-icon td-icon-material"', rendered)
        self.assertIn('stroke="currentColor"', rendered)
        self.assertIn('fill="currentColor"', rendered)

    def test_icon_tags_can_be_disabled_and_are_ignored_in_code(self):
        parser = make_markdown_parser()
        disabled = render_markdown(parser, '<icon="Sun">', icon_config={"enabled": False})
        self.assertNotIn("td-icon", disabled)
        self.assertIn("&lt;icon=", disabled)
        code = render_markdown(parser, '`<icon="Sun">`')
        self.assertIn("&lt;icon=", code)
        self.assertNotIn("td-icon", code)

    def test_unknown_icon_has_visible_fallback(self):
        rendered = render_markdown(make_markdown_parser(), '<icon="NotARealIcon">')
        self.assertIn("Unknown lucide icon", rendered)

    def test_inline_code_closing_ticks_are_preserved(self):
        parser = make_markdown_parser()
        rendered = render_markdown(
            parser,
            'Use `first` and ``second ` span`` before <color="FF00FF">pink</color>.',
        )
        self.assertIn("<code>first</code>", rendered)
        self.assertIn("<code>second ` span</code>", rendered)
        self.assertIn('before <span style="color:#FF00FF">pink</span>.', rendered)


if __name__ == "__main__":
    unittest.main()
