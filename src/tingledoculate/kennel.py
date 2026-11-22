from __future__ import annotations

from html import escape
import re


_HEADER = re.compile(r"^(?:graph|flowchart)\s+TD\s*$", re.IGNORECASE)
_EDGE = re.compile(r"^\s*(.*?)\s*-->\s*(?:\|([^|]*)\|\s*)?(.*?)\s*$")
_NODE = re.compile(
    r"^\s*([A-Za-z_][\w-]*)"
    r"(?:\[([^\]]*)\]|\(([^)]*)\)|\{([^}]*)\})?\s*$"
)


def _node(value: str) -> tuple[str, str, str]:
    match = _NODE.fullmatch(value)
    if not match:
        raise ValueError(f"Unsupported Mermaid node: {value.strip()}")
    node_id = match.group(1)
    label = next((part for part in match.groups()[1:] if part is not None), node_id)
    shape = "round" if match.group(3) is not None else "diamond" if match.group(4) is not None else "rect"
    return node_id, label, shape


def render_mermaid(source: str) -> str:
    """Render the supported Mermaid flowchart TD subset as a self-contained SVG."""
    lines = [line.strip() for line in source.splitlines()]
    lines = [line for line in lines if line and not line.startswith("%%")]
    if not lines or not _HEADER.fullmatch(lines[0]):
        raise ValueError("Kennel currently supports Mermaid 'graph TD' and 'flowchart TD'.")

    nodes: dict[str, dict[str, str]] = {}
    edges: list[tuple[str, str, str]] = []

    def add_node(raw: str) -> str:
        node_id, label, shape = _node(raw)
        nodes.setdefault(node_id, {"label": label, "shape": shape})
        if label != node_id or node_id not in nodes:
            nodes[node_id] = {"label": label, "shape": shape}
        return node_id

    for line in lines[1:]:
        match = _EDGE.fullmatch(line)
        if not match:
            # Standalone node declarations are valid too.
            add_node(line)
            continue
        left = add_node(match.group(1))
        right = add_node(match.group(3))
        edges.append((left, right, (match.group(2) or "").strip()))

    if not nodes:
        raise ValueError("The Mermaid diagram contains no nodes.")

    # Assign vertical ranks. Cycles are kept on the same rank rather than looping forever.
    ids = list(nodes)
    rank = {node_id: 0 for node_id in ids}
    for _ in range(len(ids)):
        changed = False
        for start, end, _label in edges:
            candidate = rank[start] + 1
            if candidate > rank[end] and candidate <= len(ids):
                rank[end] = candidate
                changed = True
        if not changed:
            break

    layers: dict[int, list[str]] = {}
    for node_id in ids:
        layers.setdefault(rank[node_id], []).append(node_id)

    max_label = max(len(node["label"]) for node in nodes.values())
    node_width = max(132, min(260, max_label * 9 + 36))
    node_height = 54
    horizontal_gap = 72
    vertical_gap = 92
    max_columns = max(len(layer) for layer in layers.values())
    width = max(360, max_columns * node_width + max(0, max_columns - 1) * horizontal_gap + 64)
    height = max(160, (max(layers) + 1) * (node_height + vertical_gap) + 32)

    positions: dict[str, tuple[float, float]] = {}
    for level, layer in layers.items():
        row_width = len(layer) * node_width + (len(layer) - 1) * horizontal_gap
        start_x = (width - row_width) / 2
        y = 24 + level * (node_height + vertical_gap)
        for column, node_id in enumerate(layer):
            positions[node_id] = (start_x + column * (node_width + horizontal_gap), y)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="kennel-diagram" role="img" '
        f'aria-label="Mermaid flowchart" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">',
        '<defs><marker id="kennel-arrow" markerWidth="8" markerHeight="8" '
        'refX="7" refY="3" orient="auto"><path d="M0 0 L0 6 L8 3 z" '
        'fill="currentColor"/></marker></defs>',
        '<g class="kennel-edges" fill="none" stroke="currentColor" '
        'stroke-width="1.6" marker-end="url(#kennel-arrow)">'
    ]
    for start, end, label in edges:
        sx, sy = positions[start]
        ex, ey = positions[end]
        x1, y1 = sx + node_width / 2, sy + node_height
        x2, y2 = ex + node_width / 2, ey
        middle = (y1 + y2) / 2
        parts.append(f'<path d="M{x1:g} {y1:g} V{middle:g} H{x2:g} V{y2:g}"/>')
        if label:
            parts.append(
                f'<text class="kennel-edge-label" x="{(x1 + x2) / 2:g}" '
                f'y="{middle - 7:g}" text-anchor="middle" fill="currentColor" '
                f'stroke="none">{escape(label)}</text>'
            )
    parts.append("</g><g class=\"kennel-nodes\">")
    for node_id, node in nodes.items():
        x, y = positions[node_id]
        label = escape(node["label"])
        if node["shape"] == "diamond":
            points = f"{x + node_width / 2:g},{y:g} {x + node_width:g},{y + node_height / 2:g} {x + node_width / 2:g},{y + node_height:g} {x:g},{y + node_height / 2:g}"
            parts.append(f'<polygon class="kennel-node kennel-diamond" points="{points}"/>')
        elif node["shape"] == "round":
            parts.append(
                f'<rect class="kennel-node kennel-round" x="{x:g}" y="{y:g}" '
                f'width="{node_width}" height="{node_height}" rx="24"/>'
            )
        else:
            parts.append(
                f'<rect class="kennel-node" x="{x:g}" y="{y:g}" '
                f'width="{node_width}" height="{node_height}" rx="8"/>'
            )
        parts.append(
            f'<text x="{x + node_width / 2:g}" y="{y + node_height / 2 + 5:g}" '
            f'text-anchor="middle">{label}</text>'
        )
    parts.append("</g></svg>")
    return '<figure class="kennel kennel-mermaid">' + "".join(parts) + "</figure>"


def render_kennel(info: str, source: str) -> str:
    language = info.strip().split(maxsplit=1)[0].lower() if info.strip() else ""
    if language != "mermaid":
        return (
            '<pre class="kennel-unsupported"><code>'
            + escape(source)
            + "</code></pre>"
        )
    try:
        return render_mermaid(source)
    except ValueError as error:
        return (
            '<div class="kennel-error"><strong>Mermaid kennel:</strong> '
            + escape(str(error))
            + '<pre><code>'
            + escape(source)
            + "</code></pre></div>"
        )
