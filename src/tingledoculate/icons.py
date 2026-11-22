"""Small, locally bundled SVG icon catalogue for HTMD."""

from __future__ import annotations

import html
import re

_LUCIDE = {
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    "house": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "moon": '<path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401"/>',
    "search": '<path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/>',
    "book-open": '<path d="M12 5v16"/><path d="M20.001 19A2 2 0 0 0 22 17V5a2 2 0 0 0-1.999-2L16 3.002A5 5 0 0 0 12 5a5 5 0 0 0-4-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 1.999 2H8a5 5 0 0 1 4 2 5 5 0 0 1 4-2z"/>',
}

_MATERIAL = {
    "home": '<path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>',
    "search": '<path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>',
    "light-mode": '<path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm0-6v3m0 14v3M4.93 4.93l2.12 2.12m9.9 9.9 2.12 2.12M2 12h3m14 0h3M4.93 19.07l2.12-2.12m9.9-9.9 2.12-2.12"/>',
}


def render_icon(name: str, icon_set: str = "lucide") -> str:
    """Render a bundled icon as an accessible, inline SVG."""
    selected = icon_set.strip().lower()
    if selected not in {"lucide", "material"}:
        selected = "lucide"
    key = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", name.strip()).lower().replace("_", "-").replace(" ", "-")
    catalogue = _LUCIDE if selected == "lucide" else _MATERIAL
    paths = catalogue.get(key)
    if paths is None:
        label = html.escape(name, quote=True)
        return f'<span class="td-icon-missing" role="img" aria-label="Unknown {selected} icon: {label}">[icon: {label}]</span>'
    if selected == "lucide":
        return (
            f'<svg class="td-icon td-icon-lucide" xmlns="http://www.w3.org/2000/svg" '
            f'width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true" focusable="false">{paths}</svg>'
        )
    return (
        f'<svg class="td-icon td-icon-material" xmlns="http://www.w3.org/2000/svg" '
        f'width="1em" height="1em" viewBox="0 0 24 24" fill="currentColor" '
        f'aria-hidden="true" focusable="false">{paths}</svg>'
    )
