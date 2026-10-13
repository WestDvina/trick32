"""Rasterize Lucide SVG icons (ISC license) into PIL images for the OG template."""
import io
import re
from pathlib import Path

import cairosvg
from PIL import Image

ICONS_DIR = Path(__file__).parent / "icons"
_cache = {}


def available() -> list:
    return sorted(p.stem for p in ICONS_DIR.glob("*.svg"))


def render(name: str, size: int, color: str, stroke: float = 1.6) -> Image.Image:
    """Return a `size`x`size` RGBA icon in the given color. Cached."""
    key = (name, size, color, stroke)
    if key in _cache:
        return _cache[key].copy()

    path = ICONS_DIR / f"{name}.svg"
    if not path.exists():
        path = ICONS_DIR / "circle-dot.svg"
    svg = path.read_text(encoding="utf-8")

    def _hex(rgb):
        return "#%02x%02x%02x" % rgb if isinstance(rgb, tuple) else rgb

    svg = svg.replace("currentColor", _hex(color))
    svg = re.sub(r'width="24"', "", svg, count=1)
    svg = re.sub(r'height="24"', "", svg, count=1)
    svg = svg.replace('stroke-width="2"', f'stroke-width="{stroke}"')
    svg = svg.replace("<svg ", f'<svg width="{size}" height="{size}" ', 1)

    scale = 4
    png = cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                           output_width=size * scale, output_height=size * scale)
    img = Image.open(io.BytesIO(png)).convert("RGBA").resize((size, size), Image.LANCZOS)
    _cache[key] = img
    return img.copy()


def paste(img: Image.Image, name: str, cx: int, cy: int, size: int, color, stroke: float = 1.6):
    ic = render(name, size, color, stroke)
    img.paste(ic, (cx - size // 2, cy - size // 2), ic)
