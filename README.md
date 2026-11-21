# TingleDoculate

> It tingles. It doculates. It doesn't document.

TingleDoculate is a lightweight, incremental static documentation generator inspired by the useful parts of MkDocs. It turns Markdown files into a navigable static website made of HTML, CSS, and JavaScript.

It is designed to keep the build pipeline understandable and the generated site simple: visitors do not need Python or a server-side runtime.

## Status

**Early development.** The current implementation provides the core build pipeline, but it is not yet a mature or production-hardened documentation platform. APIs and configuration may change.

## Features

- Markdown-to-HTML rendering
- Filesystem-derived navigation
- Relative Markdown links rewritten to generated HTML pages
- Client-side search index
- Incremental page rendering
- Responsive theme with independently configurable light and dark palettes
- Built-in SVG sun/moon theme toggle with saved visitor preference
- Static asset copying
- Local preview server

## Requirements

- Python 3.11 or newer

## Install

Install from the repository:

```sh
python -m pip install .
```

Or install directly from GitHub:

```sh
python -m pip install "git+https://github.com/alert-bake/TingleDoculate.git"
```

## Quick start

Create a `docs/` directory containing Markdown files, then add a `tingledoculate.toml` configuration file:

```toml
[site]
title = "My Documentation"
description = "Project documentation."
source = "docs"
output = "site"

[build]
incremental = true

[theme]
default_mode = "dark" # "dark" or "light"

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

The `[theme.dark]` and `[theme.light]` sections are independent palettes. Set the colors you want in each; omitted or invalid colors use the built-in defaults. Colors currently accept hexadecimal notation (`#RGB`, `#RRGGBB`, or `#RRGGBBAA`).

Visitors can switch modes with the sun/moon button in the sidebar. Their choice is saved in browser local storage. If they have not chosen a mode before, `default_mode` is used.

Build and preview:

```sh
tingledoculate build
tingledoculate serve
```

The generated website is written to `site/`.

## Commands

- `tingledoculate build` builds the site.
- `tingledoculate build --force` re-renders every page.
- `tingledoculate clean` removes generated output and the build cache.
- `tingledoculate serve` builds and serves the site locally.

## Documentation

The `docs/` directory contains TingleDoculate's own documentation. Start with [the overview](docs/index.md).

## Development

```sh
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
tingledoculate build
```

## Design goals

1. Keep the build pipeline understandable.
2. Keep runtime dependencies out of the generated website.
3. Avoid rebuilding unchanged pages.
4. Prefer predictable filesystem conventions over a large plugin system.
5. Measure performance before making optimization claims.

## License

TingleDoculate is licensed under the MIT License. See [LICENSE](LICENSE) for the full license text.
