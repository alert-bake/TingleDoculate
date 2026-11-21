from __future__ import annotations

from html import escape
from pathlib import PurePosixPath
import posixpath


CSS = """\
:root{color-scheme:light dark;--bg:#fff;--panel:#f5f6f8;--text:#20242b;--muted:#687180;--line:#e1e4e8;--link:#315fc4;--code:#f0f2f5}
@media(prefers-color-scheme:dark){:root{--bg:#111318;--panel:#191d24;--text:#e7eaf0;--muted:#a1a9b7;--line:#303642;--link:#91b4ff;--code:#202630}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}.layout{min-height:100vh;display:grid;grid-template-columns:270px minmax(0,1fr)}
.sidebar{position:sticky;top:0;height:100vh;overflow:auto;padding:24px 18px;background:var(--panel);border-right:1px solid var(--line)}
.brand{font-size:1.1rem;font-weight:750;overflow-wrap:anywhere}.description{color:var(--muted);font-size:.88rem;margin:.35rem 0 1.3rem}
.search{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--text);font:inherit}
.search-results{list-style:none;padding:0;margin:8px 0}.search-results li{padding:5px 0;font-size:.9rem}
.nav{list-style:none;padding:0;margin:18px 0}.nav li{margin:3px 0}.nav a{display:block;padding:5px 8px;border-radius:6px;color:var(--text);font-size:.94rem}.nav a:hover{background:var(--bg);text-decoration:none}.nav .depth-1{padding-left:14px}.nav .depth-2{padding-left:28px}.nav .depth-3{padding-left:42px}
main{width:min(900px,100%);padding:54px clamp(22px,6vw,76px);margin:0 auto}main h1,main h2,main h3{line-height:1.25;letter-spacing:-.025em}main h1{font-size:2.25rem}main h2{margin-top:2.2em;border-bottom:1px solid var(--line);padding-bottom:.35em}main p,main li{max-width:78ch}code{background:var(--code);padding:.15em .35em;border-radius:4px;font-size:.9em}pre{overflow:auto;padding:16px;border:1px solid var(--line);border-radius:10px;background:var(--code)}pre code{padding:0;background:transparent}blockquote{margin:1.2em 0;padding:.2em 1em;border-left:3px solid var(--line);color:var(--muted)}table{border-collapse:collapse;display:block;overflow:auto}th,td{border:1px solid var(--line);padding:8px 12px;text-align:left}img{max-width:100%;height:auto}
@media(max-width:760px){.layout{display:block}.sidebar{position:relative;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:16px}.nav{display:flex;flex-wrap:wrap;gap:4px;margin:12px 0 0}.nav li{margin:0}.nav .depth-1,.nav .depth-2,.nav .depth-3{padding-left:0}main{padding:30px 20px}main h1{font-size:1.8rem}}
"""

JS = """\
(() => {
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
) -> str:
    root_prefix = "../" * len(output_path.parent.parts) if output_path.parent.as_posix() != "." else "./"
    nav_items = []
    for item in navigation:
        depth = min(int(item["depth"]), 3)
        href = posixpath.relpath(item["url"], start=output_path.parent.as_posix())
        nav_items.append(
            f'<li class="depth-{depth}"><a href="{escape(href, quote=True)}">{escape(item["title"])}</a></li>'
        )
    nav = "\n".join(nav_items)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <title>{escape(title)} · {escape(site_title)}</title>
  <link rel="stylesheet" href="{root_prefix}assets/tingledoculate.css">
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <a class="brand" href="{root_prefix}index.html">{escape(site_title)}</a>
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
