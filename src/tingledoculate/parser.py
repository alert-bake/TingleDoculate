from __future__ import annotations

import html
import re
from pathlib import PurePosixPath

import nh3
from markdown_it import MarkdownIt
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.styles import get_style_by_name
from pygments.token import STANDARD_TYPES
from pygments.util import ClassNotFound

from .kennel import render_kennel
from .icons import render_icon


_MARKDOWN_LINK = re.compile(r"(?P<prefix>href=[\"'])(?P<url>[^\"']+\.md)(?P<suffix>(?:#[^\"']*)?[\"'])", re.IGNORECASE)
_TAGS = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")
_HEX_COLOR = r"(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})"
_COLOR_OPEN = re.compile(r'<color=["\'](#?' + _HEX_COLOR + r')["\']>', re.IGNORECASE)
_COLOR_PLACEHOLDER = re.compile(r"TINGLECOLOROPEN(" + _HEX_COLOR + r")TINGLE", re.IGNORECASE)
_ICON_TAG = re.compile(r'<icon="([^"<>]+)"(?:\s+set="(lucide|material)")?\s*/?>', re.IGNORECASE)
_INLINE_CODE = re.compile(r"(\x60+)(.+?)(\1)")


def _expand_color_tags(markdown: str, icon_config: dict | None = None, icons: list | None = None) -> str:
    """Replace HTMD color and icon tags with placeholders, skipping code."""
    output: list[str] = []
    icon_config = icon_config or {}
    icons = icons if icons is not None else []
    default_set = str(icon_config.get("default_set", "lucide")).lower()
    icons_enabled = bool(icon_config.get("enabled", True))
    fence_char = ""
    fence_size = 0

    for line in markdown.splitlines(keepends=True):
        stripped = line.lstrip()
        fence = re.match(r"(?:\|)?(\x60{3,}|~{3,})", stripped)
        if fence:
            marker = fence.group(1)
            if not fence_char:
                fence_char, fence_size = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                fence_char, fence_size = "", 0
            output.append(line)
            continue

        if fence_char:
            output.append(line)
            continue

        def transform(segment: str) -> str:
            segment = _COLOR_OPEN.sub(
                lambda match: "TINGLECOLOROPEN" + match.group(1).lstrip("#") + "TINGLE",
                segment,
            )
            segment = re.sub(r"</color\s*>", "TINGLECOLORCLOSE", segment, flags=re.IGNORECASE)
            def icon_replace(match):
                icon_name = match.group(1)
                icon_set = (match.group(2) or default_set).lower()
                placeholder = f"TINGLEICON{len(icons)}END"
                icons.append((placeholder, render_icon(icon_name, icon_set)))
                return placeholder
            return _ICON_TAG.sub(icon_replace, segment) if icons_enabled else segment

        pieces = _INLINE_CODE.split(line)
        for index, piece in enumerate(pieces):
            # re.split includes the opening ticks, code contents, and closing ticks.
            output.append(piece if index % 4 in (1, 2, 3) else transform(piece))

    return "".join(output)


def _highlighter(highlight_config: dict):
    enabled = bool(highlight_config.get("enabled", True))
    guess = bool(highlight_config.get("guess_language", False))
    style = str(highlight_config.get("theme", "monokai"))
    if enabled:
        get_style_by_name(style)

    def render(code: str, language: str, _attrs: str) -> str:
        if not enabled or not language:
            return ""
        try:
            lexer = get_lexer_by_name(language, stripall=False)
        except ClassNotFound:
            if not guess:
                return ""
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                return ""
        return pygments_highlight(code, lexer, HtmlFormatter(style=style, nowrap=True))

    return render


def make_highlight_css(highlight_config: dict | None = None) -> str:
    """Return locally generated Pygments CSS for the configured style."""
    config = highlight_config or {}
    if not config.get("enabled", True):
        return ""
    style = str(config.get("theme", "monokai"))
    return HtmlFormatter(style=style).get_style_defs("pre code")


def sanitize_html_fragment(rendered_html: str) -> str:
    """Keep common documentation HTML while removing unsafe markup and attributes."""
    tags = set(nh3.ALLOWED_TAGS) | {
        "center", "code", "div", "h1", "h2", "h3", "h4", "h5", "h6",
        "hr", "kbd", "pre", "s", "span", "sub", "sup", "u",
        "details", "summary", "mark", "small", "table", "thead",
        "tbody", "tr", "th", "td",
    }
    attributes = {tag: set(values) for tag, values in nh3.ALLOWED_ATTRIBUTES.items()}
    attributes.setdefault("*", set()).add("style")
    token_classes = set(STANDARD_TYPES.values()) | {"hll", "linenos"}
    return nh3.clean(
        rendered_html,
        tags=tags,
        clean_content_tags={"script", "style", "iframe", "object", "embed"},
        attributes=attributes,
        allowed_classes={"span": token_classes},
        filter_style_properties={
            "color", "background-color", "font-weight", "font-style",
            "text-decoration", "text-align",
        },
    )


def make_markdown_parser(
    markdown_config: dict | None = None,
    highlight_config: dict | None = None,
) -> MarkdownIt:
    """Create the shared Markdown/HTMD parser used by every page."""
    markdown_config = markdown_config or {}
    highlight_config = highlight_config or {}
    parser = MarkdownIt(
        "default",
        {
            "html": bool(markdown_config.get("html", False)),
            "linkify": False,
            "typographer": False,
            "highlight": _highlighter(highlight_config),
        },
    )

    def kennel_rule(state, start_line: int, end_line: int, silent: bool):
        if state.sCount[start_line] > 3:
            return False
        line = state.src[state.bMarks[start_line]:state.eMarks[start_line]]
        opening = re.match(r"^\|(`{3,}|~{3,})(.*)$", line.strip())
        if not opening:
            return False
        marker, info = opening.groups()
        next_line = start_line + 1
        closing_re = re.compile(r"^\|" + re.escape(marker[0]) + r"{" + str(len(marker)) + r",}\s*$")
        while next_line < end_line:
            candidate = state.src[state.bMarks[next_line]:state.eMarks[next_line]].strip()
            if closing_re.fullmatch(candidate):
                break
            next_line += 1
        if next_line >= end_line:
            return False
        if silent:
            return True
        token = state.push("kennel", "div", 0)
        token.block = True
        token.info = info.strip()
        token.content = state.getLines(start_line + 1, next_line, 0, True)
        token.map = [start_line, next_line + 1]
        state.line = next_line + 1
        return True

    parser.block.ruler.before("fence", "kennel", kennel_rule, {"alt": ["paragraph", "reference", "blockquote", "list"]})

    def render_kennel_token(self, tokens, idx, options, env):
        rendered = render_kennel(tokens[idx].info, tokens[idx].content)
        kennels = env.setdefault("_tingledoculate_kennels", [])
        placeholder = f"TINGLEKENNELINTERNAL{len(kennels)}END"
        kennels.append((placeholder, rendered))
        return placeholder

    parser.add_render_rule("kennel", render_kennel_token)
    return parser


def render_markdown(
    parser: MarkdownIt,
    markdown: str,
    markdown_config: dict | None = None,
    icon_config: dict | None = None,
) -> str:
    """Render Markdown and restore safe HTMD color and icon placeholders."""
    config = markdown_config or {}
    env: dict = {}
    icons: list[tuple[str, str]] = []
    rendered = parser.render(_expand_color_tags(markdown, icon_config, icons), env)
    rendered = _COLOR_PLACEHOLDER.sub(
        lambda match: '<span style="color:#' + match.group(1) + '">',
        rendered,
    )
    rendered = rendered.replace("TINGLECOLORCLOSE", "</span>")
    if config.get("html", False):
        rendered = sanitize_html_fragment(rendered)
    for placeholder, icon_html in icons:
        rendered = rendered.replace(placeholder, icon_html)
    for placeholder, kennel_html in env.get("_tingledoculate_kennels", []):
        rendered = rendered.replace(placeholder, kennel_html)
    return rendered


def rewrite_markdown_links(rendered_html: str) -> str:
    """Point rendered links at generated .html pages instead of source .md files."""
    def replace(match: re.Match[str]) -> str:
        url = match.group("url")
        suffix = match.group("suffix")
        target = PurePosixPath(url).with_suffix(".html").as_posix()
        return f'{match.group("prefix")}{target}{suffix}'

    return _MARKDOWN_LINK.sub(replace, rendered_html)


def plain_text(rendered_html: str) -> str:
    """Extract compact searchable text from rendered HTML."""
    return _WHITESPACE.sub(" ", html.unescape(_TAGS.sub(" ", rendered_html))).strip()


def page_title(markdown: str, fallback: str) -> str:
    """Use the first Markdown H1 as the page title, falling back to its filename."""
    for line in markdown.splitlines():
        match = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback.replace("-", " ").replace("_", " ").title()
