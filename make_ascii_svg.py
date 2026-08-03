"""
Convert a square portrait photo into a duotone ASCII-art SVG, styled to
match a dark GitHub-profile README (bg #0D1117). Shadows render in deep
violet, highlights in hot pink — the same duotone used by the wordmark,
so the two hero panels read as one cohesive, modern palette.
"""
from PIL import Image, ImageOps, ImageFilter

SRC = "/home/claude/assets/photo.jpg"
OUT = "/home/claude/assets/tharani-ascii.svg"

RAMP = "@%#*+=-:. "  # dark -> light (dark pixels get dense glyphs)

COLS = 90
CHAR_W = 7.0
CHAR_H = 12.4
FONT_SIZE = 12

# Duotone palette — shadows (dense glyphs) fade to highlights (sparse glyphs)
SHADOW_COLOR = "#581c87"     # deep violet
HIGHLIGHT_COLOR = "#ec4899"  # hot pink


def lerp_color(c1, c2, t):
    c1, c2 = c1.lstrip("#"), c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def build():
    im = Image.open(SRC).convert("L")
    im = ImageOps.autocontrast(im, cutoff=1)
    im = im.filter(ImageFilter.SHARPEN)

    w, h = im.size
    aspect_correct = 0.55
    rows = int((h / w) * COLS * aspect_correct)
    im_small = im.resize((COLS, rows))
    pixels = list(im_small.getdata())

    # build rows of (char, color) pairs, grouping consecutive same-color runs
    # into single <tspan> segments to keep the SVG light.
    row_segments = []
    for r in range(rows):
        segments = []  # list of [char_string, color]
        for c in range(COLS):
            p = pixels[r * COLS + c]
            t = p / 255  # 0 = dark/shadow, 1 = light/highlight
            idx = int(t * (len(RAMP) - 1))
            ch = RAMP[idx]
            color = lerp_color(SHADOW_COLOR, HIGHLIGHT_COLOR, t)
            if segments and segments[-1][1] == color:
                segments[-1][0] += ch
            else:
                segments.append([ch, color])
        row_segments.append(segments)

    width_px = COLS * CHAR_W
    height_px = rows * CHAR_H

    def escape(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    svg_parts = [
        f'<svg viewBox="0 0 {width_px:.0f} {height_px:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="Tharani Dharan Saravanan ASCII portrait">',
        f"""
  <style>
    .bg {{ fill: #0D1117; }}
    .ascii {{
      font-family: 'Fira Code', 'Courier New', monospace;
      font-size: {FONT_SIZE}px;
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
""",
        f'<rect class="bg" x="0" y="0" width="{width_px:.0f}" height="{height_px:.0f}" rx="14"/>',
    ]

    for i, segments in enumerate(row_segments):
        y = (i + 1) * CHAR_H
        delay = i * 0.018
        tspans = "".join(
            f'<tspan fill="{color}">{escape(chars)}</tspan>' for chars, color in segments
        )
        svg_parts.append(
            f'<text class="ascii row" x="6" y="{y:.1f}" '
            f'style="animation-delay:{delay:.3f}s">{tspans}</text>'
        )

    svg_parts.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(svg_parts))
    print(f"wrote {OUT} — {COLS}x{rows} chars, {width_px:.0f}x{height_px:.0f}px")


if __name__ == "__main__":
    build()
