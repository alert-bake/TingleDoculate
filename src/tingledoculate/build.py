from __future__ import annotations

import hashlib
import json
import shutil
import tomllib
from pathlib import Path, PurePosixPath

from .parser import make_markdown_parser, page_title, plain_text, rewrite_markdown_links
from .theme import CSS, JS, render_page


CACHE_VERSION = 2


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _output_path(relative: Path) -> Path:
    posix = PurePosixPath(relative.as_posix())
    if posix.name.lower() == "index.md":
        parent = Path(*posix.parts[:-1]) if len(posix.parts) > 1 else Path(".")
        return parent / "index.html"
    return Path(*posix.with_suffix(".html").parts)


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {"site": {"title": "Documentation", "description": "", "source": "docs", "output": "site"}, "build": {"incremental": True}}
    with config_path.open("rb") as handle:
        return tomllib.load(handle)


def _navigation(pages: list[tuple[Path, Path, str]]) -> list[dict[str, str]]:
    items = []
    for source, output, title in pages:
        depth = max(0, len(source.parts) - 1)
        items.append({"title": title, "url": output.as_posix(), "depth": str(depth)})
    return items


def build(root: Path, config_path: Path | None = None, force: bool = False) -> dict[str, int]:
    root = root.resolve()
    config_path = (config_path or root / "tingledoculate.toml").resolve()
    config = _load_config(config_path)
    site_config = config.get("site", {})
    build_config = config.get("build", {})
    source_dir = (root / site_config.get("source", "docs")).resolve()
    output_dir = (root / site_config.get("output", "site")).resolve()
    cache_dir = root / ".tingledoculate"
    cache_path = cache_dir / "cache.json"

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Documentation source directory does not exist: {source_dir}")

    old_cache = {}
    if build_config.get("incremental", True) and cache_path.exists() and not force:
        try:
            old_cache = json.loads(cache_path.read_text(encoding="utf-8"))
            if old_cache.get("version") != CACHE_VERSION:
                old_cache = {}
        except (OSError, json.JSONDecodeError):
            old_cache = {}

    source_files = sorted(
        p for p in source_dir.rglob("*.md")
        if not any(part.startswith(".") for part in p.relative_to(source_dir).parts)
    )
    old_pages = old_cache.get("pages", {})
    source_records = []
    for source in source_files:
        relative = source.relative_to(source_dir)
        key = relative.as_posix()
        source_hash = _digest(source.read_bytes())
        old_record = old_pages.get(key, {})
        if old_record.get("source_hash") == source_hash and old_record.get("title"):
            title = old_record["title"]
        else:
            title = page_title(source.read_text(encoding="utf-8"), source.stem)
        source_records.append((source, relative, _output_path(relative), source_hash, title))

    nav = _navigation([(relative, output, title) for _, relative, output, _, title in source_records])
    global_fingerprint = _digest(
        (json.dumps({"site": site_config, "nav": nav}, sort_keys=True) + CSS + JS).encode("utf-8")
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "tingledoculate.css").write_text(CSS, encoding="utf-8")
    (assets_dir / "tingledoculate.js").write_text(JS, encoding="utf-8")

    site_title = str(site_config.get("title", "Documentation"))
    description = str(site_config.get("description", ""))
    parser = make_markdown_parser()
    new_pages = {}
    search_pages = []
    rendered = skipped = 0

    for source, relative, output_relative, source_hash, title in source_records:
        key = relative.as_posix()
        destination = output_dir / output_relative
        page_fingerprint = _digest((source_hash + global_fingerprint).encode("utf-8"))
        old_record = old_pages.get(key, {})
        if (
            build_config.get("incremental", True)
            and not force
            and old_record.get("fingerprint") == page_fingerprint
            and destination.exists()
            and old_record.get("search")
        ):
            search_record = old_record["search"]
            skipped += 1
        else:
            markdown = source.read_text(encoding="utf-8")
            body = rewrite_markdown_links(parser.render(markdown))
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                render_page(title, site_title, description, body, nav, PurePosixPath(output_relative.as_posix())),
                encoding="utf-8",
            )
            search_record = {
                "title": title,
                "url": output_relative.as_posix(),
                "text": plain_text(body),
            }
            rendered += 1
        search_pages.append(search_record)
        new_pages[key] = {
            "source_hash": source_hash,
            "fingerprint": page_fingerprint,
            "title": title,
            "search": search_record,
        }

    for stale_key in old_pages.keys() - new_pages.keys():
        stale_output = _output_path(Path(stale_key))
        stale_file = output_dir / stale_output
        if stale_file.is_file():
            stale_file.unlink()

    user_assets = source_dir / "assets"
    if user_assets.is_dir():
        for asset in user_assets.rglob("*"):
            if asset.is_file():
                target = output_dir / "assets" / asset.relative_to(user_assets)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists() or asset.read_bytes() != target.read_bytes():
                    shutil.copy2(asset, target)

    (output_dir / "search-index.json").write_text(
        json.dumps(search_pages, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"version": CACHE_VERSION, "pages": new_pages}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return {"pages": len(source_records), "rendered": rendered, "skipped": skipped}
