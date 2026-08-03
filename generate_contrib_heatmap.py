"""
Fetch the real contribution calendar for a GitHub user via the GraphQL API
and render it as an animated SVG heatmap (cells reveal one by one).

Usage:
    GITHUB_TOKEN=ghp_xxx python3 generate_contrib_heatmap.py TharaniDharan10

Needs a Personal Access Token with at least `read:user` scope, passed as the
GITHUB_TOKEN env var (in the workflow this comes from a repo secret, e.g.
secrets.CONTRIB_PAT — the default GITHUB_TOKEN cannot read another user's
contribution calendar).
"""
import json
import os
import sys
import urllib.request

OUT = "contrib-heatmap.svg"
CELL = 11
GAP = 3
BG = "#0D1117"
EMPTY = "#161b22"
SCALE = ["#0e4429", "#006d32", "#26a641", "#39d353"]  # low -> high, GitHub's default green ramp

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def color_for(count, max_count):
    if count == 0:
        return EMPTY
    idx = min(len(SCALE) - 1, int((count / max(max_count, 1)) * (len(SCALE) - 1)) + 1)
    idx = min(idx, len(SCALE) - 1)
    return SCALE[idx]


def build(login, token):
    data = fetch(login, token)
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    all_counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    max_count = max(all_counts) if all_counts else 1

    n_weeks = len(weeks)
    width = n_weeks * (CELL + GAP) + GAP
    height = 7 * (CELL + GAP) + GAP + 24  # +24 for title text

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{login} GitHub contribution graph, {total} contributions">',
        f"""
  <style>
    .bg {{ fill: {BG}; }}
    .label {{ font-family: 'Fira Code','Consolas',monospace; font-size: 11px; fill: #8b949e; }}
    .cell {{ opacity: 0; animation: reveal 0.35s ease-out forwards; }}
    @keyframes reveal {{ to {{ opacity: 1; }} }}
  </style>
""",
        f'<rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="10"/>',
        f'<text x="{GAP}" y="14" class="label">{total} contributions in the last year</text>',
    ]

    delay_step = 0.9 / max(1, n_weeks * 7)
    i = 0
    for w, week in enumerate(weeks):
        x = GAP + w * (CELL + GAP)
        for d, day in enumerate(week["contributionDays"]):
            y = 24 + GAP + d * (CELL + GAP)
            fill = color_for(day["contributionCount"], max_count)
            delay = i * delay_step
            i += 1
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{fill}" style="animation-delay:{delay:.3f}s">'
                f'<title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
            )

    parts.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} — {n_weeks} weeks, {total} total contributions")


if __name__ == "__main__":
    login = sys.argv[1] if len(sys.argv) > 1 else "TharaniDharan10"
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("CONTRIB_TOKEN")
    if not token:
        print("Set GITHUB_TOKEN (a PAT with read:user scope) in the environment.", file=sys.stderr)
        sys.exit(1)
    build(login, token)
