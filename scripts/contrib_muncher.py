"""Draws the last year of contributions with the mascot walking over the graph and
eating every lit square. Usage: GITHUB_TOKEN=... python contrib_muncher.py <user> <out.svg>"""
import datetime
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprite import logical  # noqa: E402

USER, OUT = sys.argv[1], sys.argv[2]

query = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { contributionLevel date } } } } } }"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
    headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
)
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = cal["weeks"]

LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
COLORS = ["#1f1d2b", "#3b2f7a", "#5b45c9", "#8467f5", "#b9a6ff"]

W, CELL, STEP = 880, 12, 15
X0 = (W - len(weeks) * STEP + (STEP - CELL)) // 2
Y0 = 122
H = Y0 + 7 * STEP + 40
D = 14.0  # seconds per loop
WALK = 0.85  # fraction of the loop spent walking

sprite, SW, SH = logical()
PX = 4  # sprite pixel size
MW, MH = SW * PX, SH * PX
LANE_Y = Y0 - MH - 10
START, END = -MW - 10, W + 10
MOUTH_Y = LANE_Y + 16 * PX


def eat_time(cx):
    """Loop fraction when the mascot's centre passes x = cx."""
    return (cx - (START + MW / 2)) / (END - START) * WALK


cells, crumbs = [], []
for wi, week in enumerate(weeks):
    for day in week["contributionDays"]:
        dow = int(datetime.date.fromisoformat(day["date"]).strftime("%w"))
        x, y = X0 + wi * STEP, Y0 + dow * STEP
        lvl = LEVEL[day["contributionLevel"]]
        if not lvl:
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{COLORS[0]}"/>')
            continue
        c = COLORS[lvl]
        te = eat_time(x + CELL / 2)
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{c}">'
            f'<animate attributeName="fill" values="{c};{c};{COLORS[0]};{COLORS[0]};{c};{c}" '
            f'keyTimes="0;{te:.4f};{te + .004:.4f};.9;.95;1" dur="{D}s" repeatCount="indefinite"/></rect>'
        )
        # the square gets sucked up into the mascot's mouth
        dx = (END - START) / WALK * 0.03  # where the mascot will be when it lands
        dy = MOUTH_Y - y
        crumbs.append(
            f'<rect x="{x + 2}" y="{y + 2}" width="8" height="8" fill="{c}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{te:.4f};{te + .003:.4f};{te + .03:.4f};1" '
            f'dur="{D}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{dx:.0f} {dy};{dx:.0f} {dy}" '
            f'keyTimes="0;{te:.4f};{te + .03:.4f};1" dur="{D}s" repeatCount="indefinite"/></rect>'
        )

mascot = "".join(
    f'<rect x="{x * PX}" y="{y * PX}" width="{PX}" height="{PX}" fill="{c}"/>' for (x, y), c in sprite.items()
)
walk = (
    f'<g transform="translate({START} {LANE_Y})">'
    f'<animateTransform attributeName="transform" type="translate" values="{START} {LANE_Y};{END} {LANE_Y};{END} {LANE_Y}" '
    f'keyTimes="0;{WALK};1" dur="{D}s" repeatCount="indefinite"/>'
    f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -{PX * 2}" keyTimes="0;.5" '
    f'calcMode="discrete" dur=".36s" repeatCount="indefinite"/>{mascot}</g></g>'
)

total = cal["totalContributions"]
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} contributions in the last year, being eaten by a pixel mascot">
<defs><linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7f5af0"/><stop offset="1" stop-color="#2cb67d"/></linearGradient></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="#0f0e17" stroke="url(#edge)" stroke-width="2"/>
{"".join(cells)}
{"".join(crumbs)}
{walk}
<text x="{X0}" y="{H - 16}" fill="#94a1b2" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">{total} contributions in the last year · every one of them eaten</text>
<g transform="translate({W - X0 - 5 * STEP - 30} {H - 26})" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11" fill="#94a1b2">
<text x="-36" y="10">less</text>{"".join(f'<rect x="{i * STEP}" y="0" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>' for i, c in enumerate(COLORS))}<text x="{5 * STEP + 4}" y="10">more</text></g>
</svg>
'''
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
open(OUT, "w").write(svg)
print("wrote", OUT, total, "contributions", len(svg), "bytes")
