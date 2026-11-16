#!/usr/bin/env python3
"""Render animated SVG cards for the GitHub profile README.

Reads contribution data from data/contributions.json and redraws every card.
Set STATIC=1 to show the final frame (no animations) for screenshotting.
"""
import base64
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
STATIC = os.environ.get("STATIC", "0") == "1"

# Brand palette (paper / ink / three colours)
PAPER = "#f4f1ea"
INK = "#1a1a1a"
BLUE = "#2563eb"
RED = "#dc2626"
YELLOW = "#eab308"
MUTED = "#6b7280"

# Fonts (subset .woff files; fall back to system fonts if missing)
FONTS_DIR = ROOT / "fonts"


def font_face(name, filename):
    p = FONTS_DIR / filename
    if not p.exists():
        return ""
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"@font-face{{font-family:'{name}';src:url(data:font/woff;base64,{b64})format('woff');font-weight:400;font-style:normal;}}"


FONTS_CSS = "\n".join([
    font_face("Instrument Serif", "serif-400.woff"),
    font_face("Geist", "geist-400.woff"),
])

ANIM_CSS = "" if STATIC else """
@keyframes riseIn { from { opacity:0; transform:translateY(12px);} to { opacity:1; transform:translateY(0);} }
@keyframes growUp { from { transform:scaleY(0);} to { transform:scaleY(1);} }
@keyframes popIn { 0%{opacity:0;transform:scale(.6)} 70%{transform:scale(1.08)} 100%{opacity:1;transform:scale(1)} }
@keyframes pulse { 0%{r:4;opacity:.6} 100%{r:14;opacity:0} }
@keyframes shine { 0%{transform:translateX(-120%)} 100%{transform:translateX(120%)} }
@keyframes printRow { from{opacity:0} to{opacity:1} }
.reduce-motion * { animation:none !important; }
"""

def wrap(svg_body, w, h, title=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">
<style>
{FONTS_CSS}
{ANIM_CSS}
text{{font-family:'Geist',system-ui,sans-serif;fill:{INK};}}
.serif{{font-family:'Instrument Serif',Georgia,serif;}}
.muted{{fill:{MUTED};}}
</style>
<rect width="{w}" height="{h}" fill="{PAPER}" rx="12"/>
{svg_body}
</svg>'''


def load_data():
    if DATA.exists():
        return json.loads(DATA.read_text())
    # fallback sample
    return {
        "total": 1247,
        "months": [42, 38, 55, 61, 78, 92, 110, 95, 88, 70, 58, 65],
        "streak": 14,
        "active_days": 218,
        "busiest_day": "2026-03-14",
        "busiest_count": 12,
        "graph": [1 if i % 3 == 0 else 0 for i in range(365)],
    }


def render_hero():
    data = load_data()
    name = "Bhanu Prakash"
    delay = "0s" if STATIC else None
    body = f'''
  <text x="40" y="90" class="serif" font-size="64" font-weight="400">{name}</text>
  <text x="40" y="130" font-size="16" class="muted">Fullstack engineer · building things that matter</text>
  <text x="40" y="170" font-size="13" class="muted">github.com/Optional-BhanuPrakash</text>
  <circle cx="780" cy="90" r="6" fill="{BLUE}"/>
  <text x="800" y="95" font-size="12" class="muted">available for work</text>
'''
    return wrap(body, 880, 200, "Hero")


def render_tile(title, number, color, subtitle, link_hint):
    body = f'''
  <text x="24" y="40" font-size="13" font-weight="600" fill="{color}">{title}</text>
  <text x="24" y="110" class="serif" font-size="56" fill="{INK}">{number}</text>
  <text x="24" y="140" font-size="12" class="muted">{subtitle}</text>
  <circle cx="300" cy="40" r="6" fill="{color}"/>
'''
    return wrap(body, 320, 160, title)


def render_activity():
    data = load_data()
    months = data["months"]
    maxv = max(months) or 1
    bars = ""
    for i, v in enumerate(months):
        h = int((v / maxv) * 120)
        x = 60 + i * 68
        y = 200 - h
        color = BLUE if v == maxv else INK
        bars += f'<rect x="{x}" y="{y}" width="40" height="{h}" fill="{color}" rx="4"/>\n'
        bars += f'<text x="{x+20}" y="{y-6}" font-size="11" text-anchor="middle" class="muted">{v}</text>\n'
    body = f'''
  <text x="40" y="40" class="serif" font-size="28">Contributions per month</text>
  <text x="40" y="70" font-size="13" class="muted">streak {data["streak"]} days · {data["active_days"]} active days · busiest {data["busiest_count"]} on {data["busiest_day"]}</text>
  {bars}
'''
    return wrap(body, 880, 240, "Activity")


def render_heatmap():
    data = load_data()
    graph = data["graph"]
    cells = ""
    for i, v in enumerate(graph):
        col = i % 52
        row = i // 52
        x = 40 + col * 14
        y = 40 + row * 14
        fill = BLUE if v else "#d1d5db"
        opacity = 0.3 + 0.7 * v if v else 0.25
        cells += f'<rect x="{x}" y="{y}" width="11" height="11" fill="{fill}" opacity="{opacity:.2f}" rx="2"/>\n'
    body = f'''
  <text x="40" y="28" class="serif" font-size="22">Contribution graph</text>
  {cells}
'''
    return wrap(body, 880, 160, "Heatmap")


def render_repo(name, desc, lang, stars):
    body = f'''
  <text x="24" y="36" class="serif" font-size="22">{name}</text>
  <text x="24" y="64" font-size="13" class="muted">{desc}</text>
  <circle cx="24" cy="100" r="6" fill="{BLUE}"/>
  <text x="38" y="105" font-size="12" class="muted">{lang}</text>
  <text x="760" y="105" font-size="12" class="muted">★ {stars}</text>
'''
    return wrap(body, 880, 120, name)


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    d = load_data()

    (CARDS / "hero.svg").write_text(render_hero(), encoding="utf-8")
    (CARDS / "build.svg").write_text(render_tile("BUILD", d["total"], BLUE, "total contributions", ""), encoding="utf-8")
    (CARDS / "brand.svg").write_text(render_tile("BRAND", d["streak"], RED, "day streak", ""), encoding="utf-8")
    (CARDS / "learn.svg").write_text(render_tile("LEARN", d["active_days"], YELLOW, "active days", ""), encoding="utf-8")
    (CARDS / "activity.svg").write_text(render_activity(), encoding="utf-8")
    (CARDS / "heatmap.svg").write_text(render_heatmap(), encoding="utf-8")

    repos = [
        ("ResumeJobMatch_Crew", "AI resume-to-job matching crew", "Python", 0),
        ("Crypto", "Cryptography utilities and experiments", "Python", 0),
        ("Audio", "Audio processing tools", "Python", 0),
    ]
    for name, desc, lang, stars in repos:
        slug = name.lower().replace("_", "-")
        (CARDS / f"repo-{slug}.svg").write_text(render_repo(name, desc, lang, stars), encoding="utf-8")

    print(f"Rendered {len(list(CARDS.glob('*.svg')))} cards into {CARDS}")


if __name__ == "__main__":
    main()
