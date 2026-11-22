from __future__ import annotations

from html import escape
from pathlib import PurePosixPath
import posixpath
import re


DEFAULT_PALETTES = {
    "dark": {
        "background": "#101114",
        "surface": "#191B20",
        "surface_secondary": "#22252B",
        "text": "#E6E8ED",
        "text_muted": "#A0A5B0",
        "primary": "#8B9CF6",
        "link": "#9AAEFF",
        "link_hover": "#C0CBFF",
        "border": "#30343D",
        "code_background": "#1C1F26",
    },
    "light": {
        "background": "#FFFFFF",
        "surface": "#F5F6F8",
        "surface_secondary": "#EBEDF0",
        "text": "#20232A",
        "text_muted": "#686D78",
        "primary": "#586BD6",
        "link": "#4058C9",
        "link_hover": "#263FAF",
        "border": "#D9DCE3",
        "code_background": "#F0F1F4",
    },
}

COLOR_KEYS = tuple(DEFAULT_PALETTES["dark"])
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?$")


def _palette(theme_config: dict, mode: str) -> dict[str, str]:
    configured = theme_config.get(mode, {})
    defaults = DEFAULT_PALETTES[mode]
    palette = {}
    for key in COLOR_KEYS:
        value = configured.get(key, defaults[key])
        if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
            value = defaults[key]
        palette[key] = value
    return palette


def _theme_css(theme_config: dict) -> str:
    palettes = {
        mode: _palette(theme_config, mode)
        for mode in ("dark", "light")
    }
    variables = {
        "background": "bg",
        "surface": "panel",
        "surface_secondary": "panel-raised",
        "text": "text",
        "text_muted": "muted",
        "primary": "primary",
        "link": "link",
        "link_hover": "link-hover",
        "border": "line",
        "code_background": "code",
    }
    blocks = []
    for mode in ("dark", "light"):
        values = ";".join(
            f"--{variables[key]}:{palettes[mode][key]}"
            for key in COLOR_KEYS
        )
        blocks.append(f'html[data-theme="{mode}"]{{{values}}}')
    return "\n".join(blocks)


CSS = """\
:root{color-scheme:dark;--bg:#101114;--panel:#191B20;--panel-raised:#22252B;--text:#E6E8ED;--muted:#A0A5B0;--primary:#8B9CF6;--link:#9AAEFF;--link-hover:#C0CBFF;--line:#30343D;--code:#1C1F26}
html[data-theme="light"]{color-scheme:light}
html[data-theme="dark"]{color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--link);text-decoration:none}a:hover{color:var(--link-hover);text-decoration:underline}.layout{min-height:100vh;display:grid;grid-template-columns:270px minmax(0,1fr)}
.sidebar{position:sticky;top:0;height:100vh;overflow:auto;padding:24px 18px;background:var(--panel);border-right:1px solid var(--line)}
.brand-row{display:flex;align-items:center;justify-content:space-between;gap:12px}.brand{font-size:1.1rem;font-weight:750;overflow-wrap:anywhere;color:var(--text)}
.theme-toggle{display:inline-grid;place-items:center;flex:0 0 auto;width:38px;height:38px;padding:0;border:1px solid var(--line);border-radius:9px;background:var(--panel-raised);color:var(--text);cursor:pointer}
.theme-toggle:hover{border-color:var(--primary);color:var(--primary)}.theme-toggle:focus-visible{outline:2px solid var(--primary);outline-offset:2px}
.theme-toggle svg{width:19px;height:19px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.theme-toggle .icon-sun{display:none}html[data-theme="dark"] .theme-toggle .icon-sun{display:block}html[data-theme="dark"] .theme-toggle .icon-moon{display:none}
html[data-theme="light"] .theme-toggle .icon-moon{display:block}html[data-theme="light"] .theme-toggle .icon-sun{display:none}
.description{color:var(--muted);font-size:.88rem;margin:.35rem 0 1.3rem}
.search{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--text);font:inherit}
.search-results{list-style:none;padding:0;margin:8px 0}.search-results li{padding:5px 0;font-size:.9rem}
.nav{list-style:none;padding:0;margin:18px 0}.nav li{margin:3px 0}.nav a{display:block;padding:5px 8px;border-radius:6px;color:var(--text);font-size:.94rem}.nav a:hover{background:var(--bg);text-decoration:none}.nav .depth-1{padding-left:14px}.nav .depth-2{padding-left:28px}.nav .depth-3{padding-left:42px}
main{width:min(900px,100%);padding:54px clamp(22px,6vw,76px);margin:0 auto}main h1,main h2,main h3{line-height:1.25;letter-spacing:-.025em}main h1{font-size:2.25rem}main h2{margin-top:2.2em;border-bottom:1px solid var(--line);padding-bottom:.35em}main p,main li{max-width:78ch}code{background:var(--code);padding:.15em .35em;border-radius:4px;font-size:.9em}pre{overflow:auto;padding:16px;border:1px solid var(--line);border-radius:10px;background:var(--code)}pre code{padding:0;background:transparent}.kennel{margin:1.5rem 0;overflow-x:auto}.kennel-diagram{display:block;max-width:100%;height:auto;color:var(--text);background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}.kennel-node{fill:var(--panel-raised);stroke:var(--primary);stroke-width:1.6}.kennel-nodes text{fill:var(--text);font:14px system-ui,sans-serif}.kennel-edge-label{font:12px system-ui,sans-serif}.kennel-error,.kennel-unsupported{padding:12px;border:1px solid var(--line);border-radius:8px;background:var(--panel)}blockquote{margin:1.2em 0;padding:.2em 1em;border-left:3px solid var(--line);color:var(--muted)}table{border-collapse:collapse;display:block;overflow:auto}th,td{border:1px solid var(--line);padding:8px 12px;text-align:left}img{max-width:100%;height:auto}
@media(max-width:760px){.layout{display:block}.sidebar{position:relative;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:16px}.nav{display:flex;flex-wrap:wrap;gap:4px;margin:12px 0 0}.nav li{margin:0}.nav .depth-1,.nav .depth-2,.nav .depth-3{padding-left:0}main{padding:30px 20px}main h1{font-size:1.8rem}}
"""

JS = """\
(() => {
  const root = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  const setTheme = mode => {
    const next = mode === 'light' ? 'light' : 'dark';
    root.dataset.theme = next;
    if (toggle) {
      const target = next === 'dark' ? 'light' : 'dark';
      toggle.setAttribute('aria-label', 'Switch to ' + target + ' mode');
      toggle.setAttribute('title', 'Switch to ' + target + ' mode');
    }
    try { localStorage.setItem('tingledoculate-theme', next); } catch (_) {}
  };

  if (toggle) {
    toggle.addEventListener('click', () => {
      setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark');
    });
    setTheme(root.dataset.theme);
  }

  const input = document.querySelector('[data-search]');
  const results = document.querySelector('[data-search-results]');
  if (!input || !results) return;
  let indexPromise;
  const loadIndex = () => indexPromise ||= fetch(input.dataset.index).then(r => {
    if (!r.ok) throw new Error('Search index unavailable');
    return r.json();
  });
  input.addEventListener('input', async () => {
    const query = input.value.trim().toLowerCase();
    results.replaceChildren();
    if (query.length < 2) return;
    try {
      const pages = await loadIndex();
      const matches = pages.filter(p => (p.title + ' ' + p.text).toLowerCase().includes(query)).slice(0, 10);
      for (const page of matches) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = new URL(page.url, new URL(input.dataset.root, document.baseURI)).href;
        a.textContent = page.title;
        li.append(a);
        results.append(li);
      }
    } catch (error) {
      results.textContent = 'Search could not load.';
    }
  });
})();
"""


def render_page(
    title: str,
    site_title: str,
    description: str,
    body: str,
    navigation: list[dict[str, str]],
    output_path: PurePosixPath,
    theme_config: dict | None = None,
) -> str:
    theme_config = theme_config or {}
    default_mode = theme_config.get("default_mode", "dark")
    if default_mode not in ("dark", "light"):
        default_mode = "dark"
    root_prefix = "../" * len(output_path.parent.parts) if output_path.parent.as_posix() != "." else "./"
    nav_items = []
    for item in navigation:
        depth = min(int(item["depth"]), 3)
        href = posixpath.relpath(item["url"], start=output_path.parent.as_posix())
        nav_items.append(
            f'<li class="depth-{depth}"><a href="{escape(href, quote=True)}">{escape(item["title"])}</a></li>'
        )
    nav = "\n".join(nav_items)
    palette_css = _theme_css(theme_config)
    return f'''<!doctype html>
<html lang="en" data-theme="{default_mode}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <title>{escape(title)} · {escape(site_title)}</title>
  <link rel="stylesheet" href="{root_prefix}assets/tingledoculate.css">
  <style>{palette_css}</style>
  <script>
    (() => {{
      try {{
        const saved = localStorage.getItem('tingledoculate-theme');
        document.documentElement.dataset.theme = saved === 'light' || saved === 'dark' ? saved : '{default_mode}';
      }} catch (_) {{
        document.documentElement.dataset.theme = '{default_mode}';
      }}
    }})();
  </script>
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand-row">
        <a class="brand" href="{root_prefix}index.html">{escape(site_title)}</a>
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to {'light' if default_mode == 'dark' else 'dark'} mode" title="Switch to {'light' if default_mode == 'dark' else 'dark'} mode">
          <svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"></path></svg>
          <svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.9 13A9 9 0 0 1 11 3.1 9 9 0 1 0 20.9 13Z"></path></svg>
        </button>
      </div>
      <p class="description">{escape(description)}</p>
      <input class="search" data-search data-root="{root_prefix}" data-index="{root_prefix}search-index.json" type="search" placeholder="Search documentation…" aria-label="Search documentation">
      <ul class="search-results" data-search-results aria-live="polite"></ul>
      <ul class="nav">{nav}</ul>
    </aside>
    <main><article>{body}</article></main>
  </div>
  <script src="{root_prefix}assets/tingledoculate.js" defer></script>
</body>
</html>
'''
