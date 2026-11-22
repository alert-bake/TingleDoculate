# TingleDoculate

> It tingles. It doculates. It doesn't document.

**TingleDoculate** turns a directory of Markdown files into a navigable, searchable static documentation website. It reads your source files, renders them, builds the page shell and navigation, copies static assets, and writes a complete website made from HTML, CSS, and JavaScript.

It is a lightweight Python build tool. The generated website does not need Python, a backend, a database, or a server-side runtime to display its pages.

<color="8B9CF6">Markdown goes in.</color> A doculated website comes out.

## Contents

- [What it does](#what-it-does)
- [How the build works](#how-the-build-works)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Markdown support](#markdown-support)
- [HTMD](#htmd-hypertext-markdown)
  - [Color tags](#color-tags)
  - [Icon tags](#icon-tags)
- [Kennels](#kennels)
- [Syntax highlighting](#syntax-highlighting)
- [Navigation and page structure](#navigation-and-page-structure)
- [Search](#search)
- [Themes](#themes)
- [Static assets](#static-assets)
- [Configuration reference](#configuration-reference)
- [Command-line reference](#command-line-reference)
- [Incremental builds and cache](#incremental-builds-and-cache)
- [Generated site structure](#generated-site-structure)
- [Limitations and compatibility](#limitations-and-compatibility)
- [Development](#development)

## What it does

TingleDoculate currently provides:

- Markdown-to-HTML page rendering.
- HTMD color tags for inline text coloring.
- Kennels: special fenced blocks that render supported content instead of showing source.
- A built-in static Mermaid flowchart renderer.
- Pygments syntax highlighting generated at build time.
- Optional raw HTML input with sanitization.
- Automatic page titles from the first H1 heading.
- Filesystem-derived navigation and nested pages.
- Rewriting of relative links from .md source files to generated .html pages.
- A client-side search index and search interface.
- Incremental builds that skip unchanged pages.
- Configurable light and dark theme palettes.
- A visitor-controlled light/dark theme toggle with a saved preference.
- Copying of files from the documentation asset directory.
- A local HTTP preview server.
- A clean command for removing generated output and build cache.

TingleDoculate aims to keep the output simple: ordinary static web files, with no mandatory runtime framework.

## How the build works

| Stage | What happens |
|---|---|
| 1. Discover | Finds Markdown files under the configured source directory. |
| 2. Title | Uses the first H1 as the page title, or derives one from the filename. |
| 3. Parse | Converts Markdown, HTMD color and icon tags, Kennels, and code blocks into HTML. |
| 4. Link | Rewrites local Markdown page links to their generated HTML destinations. |
| 5. Layout | Wraps each page in the responsive site shell and adds navigation. |
| 6. Assets | Writes the stylesheet, JavaScript, search index, and copied user assets. |
| 7. Cache | Saves fingerprints and search records for the next incremental build. |

|```mermaid
graph TD
    A[Markdown files] --> B[Discover pages]
    B --> C[Render Markdown and HTMD]
    C --> D[Render Kennels and highlight code]
    D --> E[Rewrite links and build navigation]
    E --> F[Write HTML, CSS and JavaScript]
    F --> G[Static documentation website]
|```

The build runs locally. The resulting site can be hosted on any static file host or served from a local web server.

## Installation

**Requirements:** Python 3.11 or newer.

Install from a local clone:

```sh
python -m pip install .
```

Install directly from GitHub:

```sh
python -m pip install "git+https://github.com/alert-bake/TingleDoculate.git"
```

For editable development:

```sh
python -m pip install -e .
```

The `tingledoculate` command is installed by the package.

## Quick start

Create a project with this structure:

```text
my-project/
├── tingledoculate.toml
└── docs/
    ├── index.md
    ├── getting-started.md
    ├── guides/
    │   └── setup.md
    └── assets/
        └── diagram.png
```

Create `tingledoculate.toml`:

```toml
[site]
title = "My Documentation"
description = "A place for project documentation."
source = "docs"
output = "site"

[build]
incremental = true

[markdown]
html = true

[highlight]
enabled = true
theme = "monokai"
guess_language = false

[theme]
default_mode = "dark"

[theme.dark]
background = "#101114"
surface = "#191B20"
surface_secondary = "#22252B"
text = "#E6E8ED"
text_muted = "#A0A5B0"
primary = "#8B9CF6"
link = "#9AAEFF"
link_hover = "#C0CBFF"
border = "#30343D"
code_background = "#1C1F26"

[theme.light]
background = "#FFFFFF"
surface = "#F5F6F8"
surface_secondary = "#EBEDF0"
text = "#20232A"
text_muted = "#686D78"
primary = "#586BD6"
link = "#4058C9"
link_hover = "#263FAF"
border = "#D9DCE3"
code_background = "#F0F1F4"
```

Write `docs/index.md`:

```md
# My Documentation

Welcome to the project docs.

- [Getting started](getting-started.md)
- [Setup guide](guides/setup.md)
```

Build the site:

```sh
tingledoculate build
```

The generated website is written to `site/`. Start a local preview server:

```sh
tingledoculate serve
```

By default, the preview server listens on `127.0.0.1:8000`. Open that address in a browser. Press Ctrl+C to stop the server.

## Markdown support

TingleDoculate uses `markdown-it-py` with its `default` preset. Standard Markdown remains the normal writing format.

### Headings and text

```md
# Heading 1
## Heading 2
### Heading 3

A paragraph with **bold**, *italic*, ~~strikethrough~~,
and `inline code`.

> A blockquote.
```

### Lists

```md
- First item
- Second item
  - Nested item

1. First step
2. Second step
```

### Links and images

```md
[Relative page](guides/setup.md)
[External website](https://example.com)

![An image](assets/diagram.png)
```

Relative Markdown links ending in `.md` are rewritten to `.html` in generated pages. A fragment such as `guide.md#installation` is retained as `guide.html#installation`.

### Tables

```md
| Feature | Status |
|---|---|
| Markdown rendering | Available |
| Static output | Available |
```

### Fenced code

Use ordinary triple-backtick fences to display source code:

```python
def greet(name):
    return f"Hello, {name}"
```

TingleDoculate supports tables and strikethrough through the Markdown parser's default preset. Bare URLs are not automatically linkified. Typographic quote and dash substitutions are disabled.

This is useful Markdown support, but it is **not full GitHub Flavored Markdown**. See [Limitations and compatibility](#limitations-and-compatibility).

## HTMD: Hypertext Markdown

HTMD extends Markdown with small authoring conveniences. It does not replace Markdown, and it is not intended to be a general-purpose programming language.

### Color tags

Use a color tag to color inline text:

```md
This word is <color="FF00FF">pink</color>.
This word is <color="#55D6A7">green</color>.
```

This word is <color="FF00FF">pink</color>. This word is <color="#55D6A7">green</color>.

Accepted colors are hexadecimal:

- 3 digits: `<color="F0A">`
- 6 digits: `<color="FF00AA">`
- 8 digits: `<color="FF00AAFF">`
- An optional leading `#` is accepted.

Close the tag with `</color>`. Color tags are converted to inline spans during rendering. They work even when raw HTML is disabled.

Color tags inside ordinary fenced code, Kennels, and inline code are intended to remain literal source rather than being interpreted as formatting.

### Icon tags

Insert a bundled icon with one self-contained tag, similar to an image:

```md
<icon="Sun">
<icon="House">
<icon="home" set="material">
```

The tag inserts an inline SVG at that position. It is not an opening/closing pair. Icon names are case-insensitive; Lucide names use their familiar PascalCase spelling or kebab-case form. Material names use lowercase snake_case or kebab-case.

Configure the default set in `tingledoculate.toml`:

```toml
[icons]
enabled = true
default_set = "lucide" # "lucide" or "material"
```

- `enabled`: enables or disables HTMD icon tags. Defaults to `true`.
- `default_set`: icon set used when a tag does not specify `set`. Defaults to `"lucide"`.
- `set`: optional per-tag override, either `"lucide"` or `"material"`.

For example, with Material selected as the default, `<icon="Sun" set="lucide">` still requests Lucide. Icons inherit `currentColor` and use the surrounding text size. SVGs are bundled and inserted during the build; the published site does not load an icon CDN or JavaScript icon package.

The current built-in catalogue is intentionally small: Lucide provides `Sun`, `House`, `Moon`, `Search`, and `BookOpen`; Material provides `home`, `search`, and `light_mode`. Unknown names render a visible fallback instead of silently disappearing. Third-party licensing is documented in [Third-party notices](../THIRD_PARTY_NOTICES.md).

### Raw HTML

Raw HTML is controlled by:

```toml
[markdown]
html = true
```

When enabled, rendered HTML is sanitized with `nh3`. Common documentation markup is allowed, while scripts, event handlers, unsafe attributes, and active embedded content are removed. Inline styles are restricted to selected presentation properties.

Set `html = false` to disable raw HTML input. HTMD color tags continue to work independently.

Do not treat the sanitizer as permission to paste arbitrary untrusted HTML into documentation. Review embedded content and external links.

## Kennels

A **Kennel** is a special fenced block for content that should be visualized instead of displayed as source code.

Normal Markdown fences already use triple backticks. Kennels use a leading pipe to distinguish their syntax:

```md
|```mermaid
graph TD
    A[Writer] --> B[Markdown]
    B --> C[TingleDoculate]
    C --> D[Website]
|```
```

The opening line can include a renderer identifier after the fence. The closing line uses the same leading pipe and fence character.

### Mermaid renderer

The first built-in Kennel renderer is Mermaid. It currently supports a deliberately small subset:

- `graph TD` and `flowchart TD` headers.
- Rectangular nodes: `A[Label]`.
- Rounded nodes: `A(Label)`.
- Diamond nodes: `A{Label}`.
- Directed arrows: `A --> B`.
- Labeled directed arrows: `A -->|label| B`.
- Standalone node declarations.
- Mermaid comment lines beginning with `%%`.

Example:

|```mermaid
flowchart TD
    Start([Start]) --> Check{Ready?}
    Check -->|Yes| Build[Build the site]
    Check -->|No| Edit[Edit the docs]
    Edit --> Check
    Build --> Done([Done])
|```

Kennels are rendered into self-contained SVG during the build. The published website does not load Mermaid from a CDN and does not execute the Mermaid source in the visitor's browser.

Unsupported renderer identifiers are displayed as escaped source. Unsupported Mermaid syntax produces an explanatory message and displays the source, rather than silently pretending the diagram was rendered.

**Important:** this is not full Mermaid compatibility. It is a small built-in top-down flowchart renderer. Other Mermaid diagram families, directions, styling directives, subgraphs, and advanced syntax are not implemented.

## Syntax highlighting

Fenced code blocks with a recognized language identifier can be highlighted by Pygments during the build.

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

Configure the highlighter:

```toml
[highlight]
enabled = true
theme = "monokai"
guess_language = false
```

- `enabled`: enables or disables syntax highlighting. Defaults to enabled.
- `theme`: a Pygments style name. Defaults to `monokai`.
- `guess_language`: allows Pygments to guess a language when a code fence has an unknown language identifier. Defaults to false.

Language guessing can occasionally guess incorrectly. Keep it disabled if predictable output matters.

Highlighting CSS is generated into `assets/tingledoculate.css`. Highlighting is local and does not require a browser-side highlighter, CDN, or JavaScript runtime dependency. Unknown or unlabeled code blocks remain ordinary escaped code.

## Navigation and page structure

Every discovered Markdown file becomes a page. The source directory structure is reflected in the generated output structure.

For example:

```text
docs/
├── index.md
├── install.md
└── api/
    ├── index.md
    └── reference.md
```

Produces:

```text
site/
├── index.html
├── install.html
├── api/
│   ├── index.html
│   └── reference.html
├── assets/
└── search-index.json
```

Special page behavior:

- A file named `index.md` becomes `index.html` in its directory.
- Other Markdown files become HTML files with the same relative path.
- The first H1 heading becomes the page title.
- If there is no H1, the filename is converted into a title by replacing hyphens and underscores with spaces and applying title casing.
- Navigation is generated from discovered Markdown files, ordered by their relative paths.
- Nested pages receive indentation in the navigation.
- Navigation depth styling is capped at depth classes 0 through 3.

TingleDoculate does not currently provide manual navigation ordering, custom labels, section grouping, or per-page navigation exclusion.

## Search

TingleDoculate generates `search-index.json` in the output directory.

Each index entry contains a page title, its generated URL, and plain text extracted from the rendered page. The site JavaScript loads this index when a visitor types into the search field.

Search behavior:

- Search starts after at least two characters are entered.
- Matching is case-insensitive substring matching over page titles and extracted page text.
- Up to 10 matching pages are displayed.
- The index is loaded on demand and cached in memory for the current page session.
- Search is client-side after the static index is downloaded.

This is a lightweight substring search, not a ranking engine. It does not provide fuzzy matching, stemming, filters, or server-side search.

## Themes

TingleDoculate generates a responsive layout with a sidebar, navigation, search field, page content, and a theme toggle.

The default theme mode is configured with:

```toml
[theme]
default_mode = "dark"
```

Allowed values are `"dark"` and `"light"`. Invalid values fall back to dark.

Each mode has its own palette:

```toml
[theme.dark]
background = "#101114"
surface = "#191B20"
surface_secondary = "#22252B"
text = "#E6E8ED"
text_muted = "#A0A5B0"
primary = "#8B9CF6"
link = "#9AAEFF"
link_hover = "#C0CBFF"
border = "#30343D"
code_background = "#1C1F26"

[theme.light]
background = "#FFFFFF"
surface = "#F5F6F8"
surface_secondary = "#EBEDF0"
text = "#20232A"
text_muted = "#686D78"
primary = "#586BD6"
link = "#4058C9"
link_hover = "#263FAF"
border = "#D9DCE3"
code_background = "#F0F1F4"
```

| Key | Used for |
|---|---|
| `background` | Main page background |
| `surface` | Sidebar and raised content surfaces |
| `surface_secondary` | Secondary surfaces and Kennel nodes |
| `text` | Main text and diagram labels |
| `text_muted` | Descriptions and blockquotes |
| `primary` | Accent color and diagram node borders |
| `link` | Links |
| `link_hover` | Links while hovered |
| `border` | Borders and separators |
| `code_background` | Inline and block code backgrounds |

Colors accept `#RGB`, `#RRGGBB`, or `#RRGGBBAA`. Invalid or missing values fall back to built-in defaults.

The visitor can switch between light and dark modes using the sun/moon button. The choice is saved in browser local storage under `tingledoculate-theme`. If local storage is unavailable, the configured default mode is used.

The layout adapts for smaller screens: the sidebar becomes part of the normal page flow and navigation items wrap.

## Static assets

Place static files in a directory named `assets` inside the configured documentation source directory:

```text
docs/
├── index.md
└── assets/
    ├── logo.svg
    ├── screenshot.png
    └── downloads/
        └── example.zip
```

During the build, files under `docs/assets/` are copied recursively into `site/assets/`. Reference them from Markdown using paths such as:

```md
![Screenshot](assets/screenshot.png)

[Download example](assets/downloads/example.zip)
```

TingleDoculate does not currently process, optimize, resize, or fingerprint individual assets. It copies files while preserving their relative paths.

## Configuration reference

TingleDoculate reads TOML configuration from `tingledoculate.toml` in the current working directory by default. A different file can be selected with the global `--config` option.

### `[site]`

| Setting | Default | Meaning |
|---|---|---|
| `title` | `"Documentation"` | Site name shown in the sidebar and page titles. |
| `description` | `""` | Site description shown in the sidebar and page metadata. |
| `source` | `"docs"` | Directory containing Markdown pages and an optional `assets/` folder. |
| `output` | `"site"` | Directory receiving the generated website. |

### `[build]`

| Setting | Default | Meaning |
|---|---|---|
| `incremental` | `true` | Reuse unchanged pages when their fingerprints still match. |

### `[markdown]`

| Setting | Default | Meaning |
|---|---|---|
| `html` | `false` | Allow raw HTML input, sanitized before it is written to the page. |

HTMD color and icon tags work regardless of this setting.

### `[icons]`\n\n| Setting | Default | Meaning |\n|---|---|---|\n| `enabled` | `true` | Enable or disable HTMD icon tags. |\n| `default_set` | `"lucide"` | Default icon catalogue: `"lucide"` or `"material"`. |\n\n### `[highlight]`

| Setting | Default | Meaning |
|---|---|---|
| `enabled` | `true` | Enable Pygments highlighting. |
| `theme` | `"monokai"` | Pygments style name. |
| `guess_language` | `false` | Guess a language for unknown code-fence labels. |

### `[theme]`

| Setting | Default | Meaning |
|---|---|---|
| `default_mode` | `"dark"` | Initial color mode, either `"dark"` or `"light"`. |

### `[theme.dark]` and `[theme.light]`

Both tables accept the ten color keys described in [Themes](#themes). Each palette is configured independently. Missing or invalid values use the corresponding built-in palette value.

### Custom configuration path

The global option is placed before the command:

```sh
tingledoculate --config config/site.toml build
tingledoculate --config config/site.toml serve
tingledoculate --config config/site.toml clean
```

The path is resolved relative to the current working directory.

## Command-line reference

### `tingledoculate build`

Builds the documentation site using the selected configuration.

```sh
tingledoculate build
```

The command prints the number of pages discovered, rendered, and skipped.

### `tingledoculate build --force`

Forces every discovered Markdown page to be rendered again, ignoring reusable page cache records.

```sh
tingledoculate build --force
```

### `tingledoculate serve`

Builds the site, then serves the output directory over a local HTTP server.

```sh
tingledoculate serve
tingledoculate serve --host 0.0.0.0 --port 9000
```

Options:

- `--host`: bind address. Defaults to `127.0.0.1`.
- `--port`: port number. Defaults to `8000`.

The server runs until interrupted with Ctrl+C. Binding to `0.0.0.0` makes the server listen on all network interfaces, so only use it when that exposure is intended.

### `tingledoculate clean`

Removes the configured output directory and the `.tingledoculate/` cache directory.

```sh
tingledoculate clean
```

If the configuration file is missing, the clean command uses `site/` as the output directory.

### Global `--config`

Selects a configuration file other than `tingledoculate.toml`:

```sh
tingledoculate --config path/to/site.toml build
```

The option is global and should appear before the subcommand.

## Incremental builds and cache

Incremental builds are enabled by default.

TingleDoculate stores build metadata in:

```text
.tingledoculate/
└── cache.json
```

The cache records source hashes, page fingerprints, page titles, and search records. A page can be skipped when its source and global build fingerprint are unchanged, its generated HTML file still exists, and a cached search record is available.

The global fingerprint includes site settings, theme settings, Markdown settings, highlighting settings, navigation, generated CSS, and generated JavaScript. Changes to these inputs invalidate pages so the output can be regenerated.

Use `tingledoculate build --force` to bypass reuse and render every page. Use `tingledoculate clean` to remove both generated output and cache data.

Incremental caching applies to Markdown page rendering. The search index and generated core assets are written on each build. User assets are copied when missing or when their contents differ.

## Generated site structure

A typical output directory looks like this:

```text
site/
├── index.html
├── getting-started.html
├── guides/
│   └── setup.html
├── assets/
│   ├── tingledoculate.css
│   ├── tingledoculate.js
│   └── ...copied user assets
└── search-index.json
```

- HTML files are the rendered documentation pages.
- `assets/tingledoculate.css` contains the site layout, theme-aware styles, Kennel styles, and generated Pygments styles.
- `assets/tingledoculate.js` handles the theme toggle and client-side search.
- `search-index.json` contains the page search records.

The generated pages reference local assets using paths relative to each page, so nested pages can load the shared stylesheet and script.

## Limitations and compatibility

TingleDoculate is in early development. Its supported behavior is intentionally smaller than a mature documentation platform.

Current limitations:

- It is **not full GitHub Flavored Markdown**. Task-list checkboxes and automatic bare-URL linking are not implemented.
- Typographer substitutions are disabled.
- Mermaid support is limited to the built-in top-down flowchart subset described above. It is not the full Mermaid language.
- Kennel renderer identifiers other than `mermaid` do not have renderers yet; their contents are shown as escaped source.
- There is no plugin API or user-defined renderer registration system.
- There is no automatic table of contents, heading permalink generation, or custom heading ID syntax.
- Navigation is derived from paths and cannot yet be manually reordered or grouped.
- Search is simple client-side substring matching, not fuzzy or ranked search.
- There is no built-in Markdown watch mode or automatic rebuild-on-save loop.
- There is no built-in deployment, minification, asset optimization, or image processing.
- Raw HTML is sanitized when enabled; it is not an unrestricted HTML passthrough.
- Configuration and internal APIs may change before a stable release.

Do not confuse planned ideas with implemented features. If a feature is not listed as supported in this reference or demonstrated by the current implementation, assume it is not available yet.

## Development

Clone the repository, then install it in editable mode:

```sh
python -m pip install -e .
```

Run the test suite:

```sh
python -m unittest discover -s tests -v
```

Build the project's own documentation:

```sh
tingledoculate build
```

The test suite covers parser behavior, build output, theme configuration, HTMD color handling, syntax highlighting, incremental builds, and Kennel rendering.

## Project

- Repository: [alert-bake/TingleDoculate](https://github.com/alert-bake/TingleDoculate)
- License: MIT
- Python: 3.11+

TingleDoculate doculates documentation. It does not write the documentation for you. That remains an exercise for the humans.
