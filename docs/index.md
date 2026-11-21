# TingleDoculate

TingleDoculate turns Markdown documents into a static documentation website. It is a small alternative to larger documentation systems, with a focus on a simple build pipeline and ordinary web output.

## How it works

1. Read Markdown files from the configured source directory.
2. Render Markdown into HTML.
3. Generate navigation and a search index.
4. Write the finished site, stylesheet, and search script to the output directory.

The generated website does not require Python at runtime.

## Current scope

The current implementation includes Markdown rendering, filesystem navigation, relative Markdown link rewriting, client-side search, incremental builds, static asset copying, and a local preview server.

TingleDoculate is in early development. See the [usage guide](usage.md) and [configuration reference](configuration.md).
