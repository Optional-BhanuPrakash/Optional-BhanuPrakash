#!/usr/bin/env python3
"""Render animated SVG cards for the GitHub profile README.

Reads contribution data from data/contributions.json and redraws every card.
Set STATIC=1 to show the final frame (no animations) for screenshotting.
Supports light/dark via prefers-color-scheme.
"""
import base64
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
STATIC = os.environ.get("STATIC", "0") == "1"

# Brand palette
LIGHT = {"paper": "#f4f1ea", "ink": "#1a1a1a", "muted": "#6b7280", "grid": "#d1d5db"}
DARK = {"paper": "#0d1117", "ink": "#e6edf3", "muted": "#8b949e", "grid": "#30363d"}
BLUE = "#2563eb"
RED = "#dc2626"
YELLOW = "#eab308"
GREEN = "#22c55e"

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
"""

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important;}}"


def theme_vars():
    return f"""
:root{{--paper:{LIGHT['paper']};--ink:{LIGHT['ink']};--muted:{LIGHT['muted']};--grid:{LIGHT['grid']};}}
@media (prefers-color-scheme: dark){{:root{{--paper:{DARK['paper']};--ink:{DARK['ink']};--muted:{DARK['muted']};--grid:{DARK['grid']};}}}}
"""


def wrap(svg_body, w, h, title=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">
<style>
{FONTS_CSS}
{theme_vars()}
{ANIM_CSS}
{REDUCED}
text{{font-family:'Geist',system-ui,sans-serif;fill:var(--ink);}}
.serif{{font-family:'Instrument Serif',Georgia,serif;}}
.muted{{fill:var(--muted);}}
rect.bg{{fill:var(--paper);}}
</style>
<rect class="bg" width="{w}" height="{h}" rx="12"/>
{svg_body}
</svg>'''


def load_data():
    if DATA.exists():
        try:
            return json.loads(DATA.read_text())
        except Exception:
            pass
    return {
        "total": 0,
        "months": [0] * 12,
        "streak": 0,
        "active_days": 0,
        "busiest_day": "",
        "busiest_count": 0,
        "graph": [],
    }


def render_hero():
    body = f'''
  <text x="40" y="80" class="serif" font-size="52">Bhanu Prakash</text>
  <text x="40" y="118" font-size="15" class="muted">Fullstack engineer · building things that matter</text>
  <text x="40" y="148" font-size="12" class="muted">github.com/Optional-BhanuPrakash</text>
  <circle cx="40" cy="172" r="5" fill="{GREEN}"/>
  <text x="54" y="177" font-size="12" class="muted">available for work</text>
'''
    return wrap(body, 880, 200, "Hero")


def render_tile(title, number, color, subtitle):
    body = f'''
  <text x="24" y="42" font-size="13" font-weight="700" fill="{color}">{title}</text>
  <text x="24" y="108" class="serif" font-size="52">{number}</text>
  <text x="24" y="138" font-size="12" class="muted">{subtitle}</text>
  <circle cx="296" cy="42" r="6" fill="{color}"/>
'''
    return wrap(body, 320, 160, title)


def render_activity():
    data = load_data()
    months = data["months"] or [0] * 12
    maxv = max(months) or 1
    bars = ""
    for i, v in enumerate(months):
        h = int((v / maxv) * 110) if maxv else 0
        x = 60 + i * 66
        y = 200 - h
        color = BLUE if v == maxv and v > 0 else "var(--ink)"
        bars += f'<rect x="{x}" y="{y}" width="40" height="{h}" fill="{color}" rx="4"/>\n'
        bars += f'<text x="{x+20}" y="{y-6}" font-size="10" text-anchor="middle" class="muted">{v}</text>\n'
    body = f'''
  <text x="40" y="40" class="serif" font-size="26">Contributions per month</text>
  <text x="40" y="68" font-size="12" class="muted">streak {data["streak"]} days · {data["active_days"]} active days · busiest {data["busiest_count"]} on {data["busiest_day"]}</text>
  {bars}
'''
    return wrap(body, 880, 240, "Activity")


def render_heatmap():
    data = load_data()
    graph = data["graph"] or []
    cells = ""
    for i, v in enumerate(graph):
        col = i % 52
        row = i // 52
        x = 40 + col * 14
        y = 40 + row * 14
        if v:
            opacity = 0.35 + 0.65 * min(v, 1)
            cells += f'<rect x="{x}" y="{y}" width="11" height="11" fill="{BLUE}" opacity="{opacity:.2f}" rx="2"/>\n'
        else:
            cells += f'<rect x="{x}" y="{y}" width="11" height="11" fill="var(--grid)" opacity="0.4" rx="2"/>\n'
    body = f'''
  <text x="40" y="28" class="serif" font-size="20">Contribution graph</text>
  {cells}
'''
    return wrap(body, 880, 160, "Heatmap")


def render_repo(name, desc, lang, stars):
    body = f'''
  <text x="24" y="36" class="serif" font-size="20">{name}</text>
  <text x="24" y="62" font-size="13" class="muted">{desc}</text>
  <circle cx="24" cy="96" r="6" fill="{BLUE}"/>
  <text x="38" y="101" font-size="12" class="muted">{lang}</text>
  <text x="760" y="101" font-size="12" class="muted">★ {stars}</text>
'''
    return wrap(body, 880, 120, name)


def main():
    CARDS.mkdir(parents=True, exist_ok=True)
    d = load_data()

    (CARDS / "hero.svg").write_text(render_hero(), encoding="utf-8")
    (CARDS / "build.svg").write_text(render_tile("BUILD", d["total"], BLUE, "total contributions"), encoding="utf-8")
    (CARDS / "brand.svg").write_text(render_tile("BRAND", d["streak"], RED, "day streak"), encoding="utf-8")
    (CARDS / "learn.svg").write_text(render_tile("LEARN", d["active_days"], YELLOW, "active days"), encoding="utf-8")
    (CARDS / "activity.svg").write_text(render_activity(), encoding="utf-8")
    (CARDS / "heatmap.svg").write_text(render_heatmap(), encoding="utf-8")

    repos = [
        ("ResumeJobMatch_Crew", "AI resume-to-job matching crew", "Python", 0),
        ("AI-Code-Debugger-Crew", "AI-powered code debugging crew", "Python", 0),
        ("Crypto", "Cryptography utilities and experiments", "Python", 0),
        ("Audio", "Audio processing tools", "Python", 0),
    ]
    for name, desc, lang, stars in repos:
        slug = name.lower().replace("_", "-")
        (CARDS / f"repo-{slug}.svg").write_text(render_repo(name, desc, lang, stars), encoding="utf-8")

    print(f"Rendered {len(list(CARDS.glob('*.svg')))} cards into {CARDS}")


if __name__ == "__main__":
    main()
