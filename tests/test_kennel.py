import unittest

from tingledoculate.parser import make_markdown_parser, render_markdown


class KennelTests(unittest.TestCase):
    def test_mermaid_kennel_renders_svg(self):
        markdown = """|\`\`\`mermaid
graph TD
    A[Markdown] --> B[TingleDoculate]
    B -->|renders| C[Website]
|\`\`\`"""
        parser = make_markdown_parser({"html": False}, {"enabled": False})
        rendered = render_markdown(parser, markdown)
        self.assertIn('<figure class="kennel kennel-mermaid">', rendered)
        self.assertIn("<svg", rendered)
        self.assertIn("Markdown", rendered)
        self.assertIn("TingleDoculate", rendered)
        self.assertIn("renders", rendered)
        self.assertNotIn("TINGLEKENNELINTERNAL", rendered)

    def test_normal_fence_still_displays_source(self):
        markdown = """\`\`\`mermaid
graph TD
    A[Markdown] --> B[Website]
\`\`\`"""
        parser = make_markdown_parser({"html": False}, {"enabled": False})
        rendered = render_markdown(parser, markdown)
        self.assertIn("<pre><code", rendered)
        self.assertIn("graph TD", rendered)
        self.assertNotIn("<svg", rendered)

    def test_kennel_labels_are_escaped(self):
        markdown = """|\`\`\`mermaid
graph TD
    A[<script>alert(1)</script>]
|\`\`\`"""
        parser = make_markdown_parser({"html": False}, {"enabled": False})
        rendered = render_markdown(parser, markdown)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)

    def test_html_sanitization_does_not_strip_generated_kennel_svg(self):
        markdown = """|\`\`\`mermaid
graph TD
    A[Safe] --> B[SVG]
|\`\`\`"""
        parser = make_markdown_parser({"html": True}, {"enabled": False})
        rendered = render_markdown(parser, markdown, {"html": True})
        self.assertIn("<svg", rendered)
        self.assertIn("viewBox=", rendered)


if __name__ == "__main__":
    unittest.main()
