from __future__ import annotations

import argparse
import shutil
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tingledoculate", description="Build a static documentation website.")
    parser.add_argument("--config", default="tingledoculate.toml", help="Path to the TOML configuration file.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Build the documentation site.")
    build.add_argument("--force", action="store_true", help="Re-render every page.")
    sub.add_parser("clean", help="Remove generated output and build cache.")
    serve = sub.add_parser("serve", help="Build and serve the generated site locally.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = Path.cwd()
    config_path = (root / args.config).resolve()

    if args.command == "clean":
        import tomllib
        config = tomllib.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        output = root / config.get("site", {}).get("output", "site")
        shutil.rmtree(output, ignore_errors=True)
        shutil.rmtree(root / ".tingledoculate", ignore_errors=True)
        print("Removed generated site and cache.")
        return 0

    from .build import build
    result = build(root, config_path=config_path, force=getattr(args, "force", False))
    print(f"Built {result['pages']} pages: {result['rendered']} rendered, {result['skipped']} unchanged.")

    if args.command == "serve":
        import tomllib
        config = tomllib.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        output = (root / config.get("site", {}).get("output", "site")).resolve()
        import os
        os.chdir(output)
        server = ThreadingHTTPServer((args.host, args.port), SimpleHTTPRequestHandler)
        print(f"Serving at http://{args.host}:{args.port}/ (Ctrl+C to stop)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    return 0
