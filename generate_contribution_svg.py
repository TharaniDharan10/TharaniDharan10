#!/usr/bin/env python3
"""
Generates a static SVG GitHub contribution heatmap using real contribution
data, styled with a custom palette:
  level 0 (no contributions) -> dark grey
  level 1-4 (contributions)  -> a gradient of blue, dim to bright

Data source: https://github-contributions-api.jogruber.de/v4/<username>
(a free, public, no-auth mirror of the real GitHub contribution calendar).

Usage:
    python3 generate_contribution_svg.py <username> <output_path>
"""

import sys
import json
import datetime
import urllib.request

# ---- palette: index 0 = no contributions, 1-4 = increasing activity ----
COLORS = [
    "#21262d",  # no contributions - dark grey (matches GitHub's own dark-mode empty cell)
    "#1e3a5f",  # low activity - muted deep blue
    "#2b5a8f",  # 
    "#3b82f6",  # 
    "#60a5fa",  # high activity - brightest blue
]
BG = "#0d1117"
TEXT = "#7d8590"

CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT_PAD = 28
TOP_PAD = 24


def fetch_contributions(username):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.loads(resp.read().decode())
    return data["contributions"]


def build_svg(days, username):
    # index days by date for quick lookup
    by_date = {d["date"]: d for d in days}

    today = datetime.date.today()
    start = today - datetime.timedelta(days=364)
    # align start to a Sunday so columns line up like GitHub's grid
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    cur = start
    while cur <= today:
        week = []
        for _ in range(7):
            iso = cur.isoformat()
            entry = by_date.get(iso)
            level = entry["level"] if entry else 0
            week.append((cur, level))
            cur += datetime.timedelta(days=1)
        weeks.append(week)

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * STEP + 10
    height = TOP_PAD + 7 * STEP + 30

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="\'JetBrains Mono\', ui-monospace, monospace">',
        f'<rect width="100%" height="100%" fill="{BG}" rx="8"/>',
    ]

    # month labels
    last_month = None
    for wi, week in enumerate(weeks):
        month = week[0][0].month
        if month != last_month:
            label = week[0][0].strftime("%b")
            x = LEFT_PAD + wi * STEP
            svg.append(
                f'<text x="{x}" y="16" font-size="10" fill="{TEXT}">{label}</text>'
            )
            last_month = month

    # day cells
    for wi, week in enumerate(weeks):
        for di, (date, level) in enumerate(week):
            x = LEFT_PAD + wi * STEP
            y = TOP_PAD + di * STEP
            color = COLORS[min(level, 4)]
            svg.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}"><title>{date.isoformat()} — level {level}</title></rect>'
            )

    # legend
    ly = TOP_PAD + 7 * STEP + 16
    svg.append(f'<text x="{LEFT_PAD}" y="{ly + 8}" font-size="10" fill="{TEXT}">Less</text>')
    lx = LEFT_PAD + 34
    for c in COLORS:
        svg.append(f'<rect x="{lx}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
        lx += STEP
    svg.append(f'<text x="{lx + 4}" y="{ly + 8}" font-size="10" fill="{TEXT}">More</text>')

    # ---- snake path: visits only empty (level 0) cells, boustrophedon order ----
    snake_cells = []
    for wi, week in enumerate(weeks):
        row_order = range(7) if wi % 2 == 0 else range(6, -1, -1)
        for di in row_order:
            date, level = week[di]
            if level == 0:
                x = LEFT_PAD + wi * STEP
                y = TOP_PAD + di * STEP
                snake_cells.append((x, y))

    if snake_cells:
        n = len(snake_cells)
        step_dur = 0.16  # seconds per hop
        total_dur = round(n * step_dur, 2)
        xs = ";".join(str(x) for x, y in snake_cells) + f";{snake_cells[0][0]}"
        ys = ";".join(str(y) for x, y in snake_cells) + f";{snake_cells[0][1]}"
        key_times = ";".join(f"{i/n:.5f}" for i in range(n)) + ";1"

        snake_color = "#f472b6"  # pink, distinct from the blue activity palette
        trail_colors = ["#f472b6", "#e879a9", "#d16a97", "#b95c85"]
        trail_delays = [0, step_dur, step_dur * 2, step_dur * 3]

        svg.append('<g id="snake">')
        for color, delay in zip(trail_colors, trail_delays):
            opacity = 1.0 if delay == 0 else max(0.15, 0.6 - delay * 0.5)
            svg.append(
                f'<rect width="{CELL}" height="{CELL}" rx="2.5" fill="{color}" opacity="{opacity:.2f}">'
                f'<animate attributeName="x" values="{xs}" keyTimes="{key_times}" '
                f'dur="{total_dur}s" begin="-{delay}s" repeatCount="indefinite" calcMode="discrete"/>'
                f'<animate attributeName="y" values="{ys}" keyTimes="{key_times}" '
                f'dur="{total_dur}s" begin="-{delay}s" repeatCount="indefinite" calcMode="discrete"/>'
                f"</rect>"
            )
        svg.append("</g>")

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    if len(sys.argv) != 3:
        print("usage: generate_contribution_svg.py <username> <output_path>")
        sys.exit(1)
    username, out_path = sys.argv[1], sys.argv[2]
    days = fetch_contributions(username)
    svg = build_svg(days, username)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
