from __future__ import annotations

import html


# ============================================================
# ICON DEFINITIONS
# ============================================================

ICONS: dict[str, str] = {

    "database":
        '<path d="M4 5c0-2 16-2 16 0v14'
        'c0 2-16 2-16 0z"/>'
        '<path d="M4 5c0 2 16 2 16 0"/>'
        '<path d="M4 12c0 2 16 2 16 0"/>',

    "cpu":
        '<rect x="6" y="6" width="12" height="12" rx="2"/>'
        '<path d="M9 1v5M15 1v5'
        'M9 18v5M15 18v5'
        'M1 9h5M18 9h5'
        'M1 15h5M18 15h5"/>',

    "document":
        '<path d="M6 2h8l4 4v16H6z"/>'
        '<path d="M14 2v5h5"/>'
        '<path d="M9 12h6M9 16h6"/>',

    "chart":
        '<path d="M4 20V4"/>'
        '<path d="M4 20h17"/>'
        '<path d="M7 16l4-5 3 2 5-7"/>',

    "check":
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M7 12l3 3 7-7"/>',

    "warning":
        '<path d="M12 3l10 18H2z"/>'
        '<path d="M12 9v5"/>'
        '<path d="M12 17v1"/>',

    "search":
        '<circle cx="11" cy="11" r="7"/>'
        '<path d="M16.5 16.5L22 22"/>',

    "server":
        '<rect x="3" y="3" width="18" height="7" rx="2"/>'
        '<rect x="3" y="14" width="18" height="7" rx="2"/>'
        '<path d="M7 6.5h.01M7 17.5h.01"/>'
        '<path d="M11 6.5h7M11 17.5h7"/>',

    "cloud":
        '<path d="M7 18h11'
        'a4 4 0 0 0 .5-7.97'
        'A6 6 0 0 0 7.2 8.5'
        'A4.5 4.5 0 0 0 7 18z"/>',

    "user":
        '<circle cx="12" cy="8" r="4"/>'
        '<path d="M4 21a8 8 0 0 1 16 0"/>',

    "users":
        '<circle cx="9" cy="8" r="3.5"/>'
        '<path d="M2.5 20a6.5 6.5 0 0 1 13 0"/>'
        '<path d="M15 5.5a3.5 3.5 0 0 1 0 6.8"/>'
        '<path d="M17 14a6 6 0 0 1 4.5 6"/>',

    "folder":
        '<path d="M3 6a2 2 0 0 1 2-2h5l2 2h7'
        'a2 2 0 0 1 2 2v10'
        'a2 2 0 0 1-2 2H5'
        'a2 2 0 0 1-2-2z"/>',

    "file":
        '<path d="M6 2h8l4 4v16H6z"/>'
        '<path d="M14 2v5h5"/>',

    "database_add":
        '<ellipse cx="9" cy="5" rx="6" ry="3"/>'
        '<path d="M3 5v9c0 1.7 2.7 3 6 3"/>'
        '<path d="M3 9c0 1.7 2.7 3 6 3"/>'
        '<path d="M18 14v7M14.5 17.5h7"/>',

    "download":
        '<path d="M12 3v12"/>'
        '<path d="M7 10l5 5 5-5"/>'
        '<path d="M4 21h16"/>',

    "upload":
        '<path d="M12 21V9"/>'
        '<path d="M7 14l5-5 5 5"/>'
        '<path d="M4 3h16"/>',

    "link":
        '<path d="M10 13a5 5 0 0 0 7.1.1l2-2'
        'a5 5 0 0 0-7.1-7.1l-1.1 1.1"/>'
        '<path d="M14 11a5 5 0 0 0-7.1-.1l-2 2'
        'A5 5 0 0 0 12 20l1.1-1.1"/>',

    "settings":
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8'
        '-.1-.1a1.7 1.7 0 0 0-1.9-.3'
        '1.7 1.7 0 0 0-1 1.6V20'
        'h-2.6v-.1a1.7 1.7 0 0 0-1-1.6'
        '1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8'
        '.1-.1A1.7 1.7 0 0 0 8 15'
        'a1.7 1.7 0 0 0-1.6-1H6v-2.6h.1'
        'a1.7 1.7 0 0 0 1.6-1'
        '1.7 1.7 0 0 0-.3-1.9l-.1-.1'
        '1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3'
        '1.7 1.7 0 0 0 1-1.6V5h2.6v.1'
        'a1.7 1.7 0 0 0 1 1.6'
        '1.7 1.7 0 0 0 1.9-.3l.1-.1'
        '1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9'
        '1.7 1.7 0 0 0 1.6 1h.1V14h-.1'
        'a1.7 1.7 0 0 0-1.6 1z"/>',

    "info":
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M12 11v6"/>'
        '<path d="M12 7h.01"/>',

    "x":
        '<path d="M6 6l12 12M18 6L6 18"/>',

    "plus":
        '<path d="M12 5v14M5 12h14"/>',

    "minus":
        '<path d="M5 12h14"/>',
}


# ============================================================
# FALLBACK ICON
# ============================================================

def _fallback_svg(
    name: str,
    x: float,
    y: float,
    size: float,
    color: str,
) -> str:

    escaped = html.escape(
        name,
        quote=True,
    )

    return (
        f'<text '
        f'x="{x}" '
        f'y="{y + size * 0.8}" '
        f'font-size="{size}" '
        f'font-family="Arial, sans-serif" '
        f'font-weight="600" '
        f'fill="{color}">'
        f'{escaped}'
        f'</text>'
    )


# ============================================================
# ICON SVG
# ============================================================

def icon_svg(
    name: str,
    x: float,
    y: float,
    size: float = 26,
    color: str = "#52657A",
) -> str:
    """
    Render a DiaForge icon as inline SVG.

    Parameters
    ----------
    name:
        Icon name from ICONS.

    x, y:
        Top-left position.

    size:
        Icon size in SVG units.

    color:
        Stroke color.
    """

    body = ICONS.get(name)

    if not body:
        return _fallback_svg(
            name,
            x,
            y,
            size,
            color,
        )

    scale = size / 24

    return (
        f'<g '
        f'transform="translate('
        f'{x},{y}'
        f') scale({scale:.5f})" '
        f'fill="none" '
        f'stroke="{html.escape(color, quote=True)}" '
        f'stroke-width="1.8" '
        f'stroke-linecap="round" '
        f'stroke-linejoin="round">'
        f'{body}'
        f'</g>'
    )


# ============================================================
# PUBLIC HELPERS
# ============================================================

def has_icon(name: str) -> bool:
    """Return True when an icon exists."""

    return name in ICONS


def icon_names() -> list[str]:
    """Return all available icon names."""

    return sorted(ICONS)