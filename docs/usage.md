# Usage

Install TingleDoculate from the repository:

```sh
python -m pip install .
```

Or install directly from GitHub:

```sh
python -m pip install "git+https://github.com/alert-bake/TingleDoculate.git"
```

Create a `docs/` directory and put Markdown files inside it. Then create `tingledoculate.toml` in the project root.

Build the site:

```sh
tingledoculate build
```

Preview it locally:

```sh
tingledoculate serve
```

Remove generated output and the build cache:

```sh
tingledoculate clean
```

Use `tingledoculate build --force` to render every page instead of reusing unchanged pages.
