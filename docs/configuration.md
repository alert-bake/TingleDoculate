# Configuration

TingleDoculate reads a TOML configuration file named `tingledoculate.toml` by default.

```toml
[site]
title = "My Documentation"
description = "Project documentation."
source = "docs"
output = "site"

[build]
incremental = true
```

## `[site]`

- `title`: site title shown in the navigation and page titles.
- `description`: short site description.
- `source`: directory containing Markdown source files.
- `output`: directory receiving generated files.

## `[build]`

- `incremental`: reuse unchanged rendered pages when enabled. Defaults to `true`.

Pass a different configuration path with the global `--config` option:

```sh
tingledoculate --config config/site.toml build
```
