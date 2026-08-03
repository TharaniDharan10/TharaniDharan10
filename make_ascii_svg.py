"""
Convert a square portrait photo into a monochrome ASCII-art SVG,
styled to match a dark GitHub-profile README (bg #0D1117, accent #22D3EE).
"""
from PIL import Image, ImageOps, ImageFilter
import sys

SRC = "/home/claude/assets/photo.jpg"
OUT = "/home/claude/assets/tharani-ascii.svg"

# Density ramp: dark -> light. Fewer, chunkier glyphs read better at small size.
RAMP = "@%#*+=-:. "[::-1]  # light -> dark reversed later; we build dark->light below
RAMP = "@%#*+=-:. "  # dark -> light (dark pixels get dense glyphs)

COLS = 90                 # characters per row
CHAR_W = 7.0               # px advance per character in the SVG (monospace)
CHAR_H = 12.4              # px per row (line-height)
FONT_SIZE = 12

def build():
    im = Image.open(SRC).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    im = im.filter(ImageFilter.SHARPEN)

    w, h = im.size
    # character cells are taller than wide, compensate aspect ratio
    aspect_correct = 0.55
    rows = int((h / w) * COLS * aspect_correct)
    im_small = im.resize((COLS, rows))
    pixels = list(im_small.getdata())

    lines = []
    for r in range(rows):
        row_chars = []
        for c in range(COLS):
            p = pixels[r * COLS + c]
            idx = int((p / 255) * (len(RAMP) - 1))
            row_chars.append(RAMP[idx])
        lines.append("".join(row_chars))

    width_px = COLS * CHAR_W
    height_px = rows * CHAR_H

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width_px:.0f} {height_px:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Tharani Dharan Saravanan ASCII portrait">'
    )
    svg_parts.append(f"""
  <style>
    .bg {{ fill: #0D1117; }}
    .ascii {{
      font-family: 'Fira Code', 'Courier New', monospace;
      font-size: {FONT_SIZE}px;
      fill: #22D3EE;
      white-space: pre;
    }}
    .row {{
      opacity: 0;
      animation: typeIn 0.4s ease-out forwards;
    }}
    @keyframes typeIn {{
      from {{ opacity: 0; transform: translateX(-4px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
""")
    svg_parts.append(f'<rect class="bg" x="0" y="0" width="{width_px:.0f}" height="{height_px:.0f}" rx="14"/>')

    for i, line in enumerate(lines):
        y = (i + 1) * CHAR_H
        delay = i * 0.018
        escaped = (
            line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        svg_parts.append(
            f'<text class="ascii row" x="6" y="{y:.1f}" '
            f'style="animation-delay:{delay:.3f}s">{escaped}</text>'
        )

    svg_parts.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(svg_parts))
    print(f"wrote {OUT} — {COLS}x{rows} chars, {width_px:.0f}x{height_px:.0f}px")

if __name__ == "__main__":
    build()
