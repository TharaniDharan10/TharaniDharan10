"""
Build a 3D-extruded ASCII wordmark SVG: block-letter ASCII art (pyfiglet,
ansi_shadow font) rendered with a stacked "extrusion" of offset copies to
fake 3D depth, wiping in left-to-right, then rocking gently on its
vertical axis (CSS scaleX oscillation = a cheap but convincing "3D turntable").
"""
import pyfiglet

WORD = "TD"
FONT = "ansi_shadow"
OUT = "/home/claude/assets/wordmark.svg"

FONT_SIZE = 34
CHAR_W = FONT_SIZE * 0.62     # advance width for this monospace glyph set
CHAR_H = FONT_SIZE * 1.02     # line height
DEPTH_LAYERS = 16             # how many offset copies build the extrusion
DEPTH_STEP = 1.6              # px offset per layer (diagonal, down-right)

FRONT_COLOR = "#ec4899"       # hot pink — matches the portrait's highlight tone
BACK_COLOR = "#581c87"        # deep violet — matches the portrait's shadow tone
BG = "#0D1117"

FONT_STACK = "'Cascadia Code','Fira Code','Consolas','DejaVu Sans Mono',monospace"


def lerp_color(c1, c2, t):
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def build():
    raw = pyfiglet.figlet_format(WORD, font=FONT)
    lines = [l for l in raw.split("\n")]
    while lines and lines[-1].strip() == "":
        lines.pop()
    n_cols = max(len(l) for l in lines)
    lines = [l.ljust(n_cols) for l in lines]
    n_rows = len(lines)

    art_w = n_cols * CHAR_W
    art_h = n_rows * CHAR_H

    total_w = art_w + DEPTH_LAYERS * DEPTH_STEP + 20
    total_h = art_h + DEPTH_LAYERS * DEPTH_STEP + 20

    def escape(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def text_block(x_off, y_off, color, extra_class=""):
        rows = []
        for r, line in enumerate(lines):
            y = 10 + (r + 1) * CHAR_H - CHAR_H * 0.25
            rows.append(
                f'<text x="{10 + x_off:.1f}" y="{y + y_off:.1f}" '
                f'class="glyph {extra_class}" fill="{color}">{escape(line)}</text>'
            )
        return "\n".join(rows)

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {total_w:.0f} {total_h:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{WORD} 3D ASCII wordmark">'
    )
    parts.append(f"""
  <style>
    .bg {{ fill: {BG}; }}
    .glyph {{
      font-family: {FONT_STACK};
      font-size: {FONT_SIZE}px;
      font-weight: 700;
      white-space: pre;
    }}
    #wordmark-rig {{
      transform-box: fill-box;
      transform-origin: center;
      animation: wipeIn 1s steps(24) forwards, rock 4.5s ease-in-out 1.1s infinite;
    }}
    @keyframes wipeIn {{
      from {{ clip-path: inset(0 100% 0 0); }}
      to   {{ clip-path: inset(0 0% 0 0); }}
    }}
    @keyframes rock {{
      0%   {{ transform: scaleX(1)    skewY(0deg); }}
      25%  {{ transform: scaleX(0.86) skewY(0.6deg); }}
      50%  {{ transform: scaleX(1)    skewY(0deg); }}
      75%  {{ transform: scaleX(1.1)  skewY(-0.6deg); }}
      100% {{ transform: scaleX(1)    skewY(0deg); }}
    }}
  </style>
""")
    parts.append(f'<rect class="bg" x="0" y="0" width="{total_w:.0f}" height="{total_h:.0f}" rx="12"/>')
    parts.append('<g id="wordmark-rig">')

    # extrusion: farthest layer first (drawn first = behind), front face last (on top)
    for i in range(DEPTH_LAYERS, -1, -1):
        t = i / DEPTH_LAYERS if DEPTH_LAYERS else 0
        color = FRONT_COLOR if i == 0 else lerp_color(FRONT_COLOR, BACK_COLOR, t)
        cls = "" if i == 0 else "depth"
        parts.append(text_block(i * DEPTH_STEP, i * DEPTH_STEP, color, cls))

    parts.append("</g>")
    parts.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} — {n_cols}x{n_rows} chars, {total_w:.0f}x{total_h:.0f}px")


if __name__ == "__main__":
    build()
