#!/usr/bin/env python3
"""Render assets/risk-ladder.svg — risk-per-trade ladder on a $100,000 account.

The user's stated progression: 1% -> 2% -> 3% -> currently 5% per trade.
The chart shows what a three-loss run costs at each step and the gain needed
to recover it, with a 10% reference line (a common prop-firm max-drawdown
limit) because that is where the 5% setting becomes dangerous.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "risk-ladder.svg"

START = 100_000.0
LEVELS = [
    ("1%", 0.01, "earlier"),
    ("2%", 0.02, "earlier"),
    ("3%", 0.03, "earlier"),
    ("5%", 0.05, "current"),
]
STREAK = 3  # consecutive losses

W, H = 1000, 380
PL, PR, PT, PB = 14, 14, 46, 64
PW, PH = W - PL - PR, H - PT - PB

bars = []
for label, pct, tag in LEVELS:
    left = START * (1 - pct) ** STREAK
    lost = (1 - left / START) * 100
    recover = (START / left - 1) * 100
    bars.append(
        {
            "label": label,
            "pct": pct,
            "tag": tag,
            "risk_usd": START * pct,
            "lost_pct": lost,
            "recover_pct": recover,
            "left": left,
        }
    )

# y axis scaled to the largest drawdown with headroom
top = max(b["lost_pct"] for b in bars) * 1.28
# round to a nice max
import math

step = 5 if top <= 25 else 10
ymax = math.ceil(top / step) * step


def Y(v):
    return PT + PH * (1 - v / ymax)


grid = []
v = 0
while v <= ymax:
    y = Y(v)
    grid.append(
        f'<line x1="{PL}" y1="{y:.2f}" x2="{W - PR}" y2="{y:.2f}" '
        f'stroke="#ffffff" stroke-opacity="0.07" stroke-width="1"/>'
        f'<text x="{PL - 4}" y="{y - 6:.2f}" class="ax">{v:.0f}%</text>'
    )
    v += step

# 10% reference line (prop-firm style max drawdown)
ref10 = Y(10)
ref = (
    f'<line x1="{PL}" y1="{ref10:.2f}" x2="{W - PR}" y2="{ref10:.2f}" '
    f'stroke="#e0736a" stroke-opacity="0.55" stroke-width="1.4" stroke-dasharray="5 5"/>'
    f'<text x="{W - PR}" y="{ref10 - 7:.2f}" text-anchor="end" class="warntxt">'
    f"10% — where most funded-account rules stop you</text>"
)

slot = PW / len(bars)
bar_w = slot * 0.42
body = []
for i, b in enumerate(bars):
    cx = PL + slot * (i + 0.5)
    x = cx - bar_w / 2
    y = Y(b["lost_pct"])
    h = PT + PH - y
    current = b["tag"] == "current"
    fill = "url(#gcur)" if current else "url(#gprev)"
    stroke = "#e6c574" if current else "rgba(216,178,95,.35)"
    body.append(
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" rx="5" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        # risk per trade label
        f'<text x="{cx:.2f}" y="{y - 12:.2f}" text-anchor="middle" class="val">'
        f"−{b['lost_pct']:.1f}%</text>"
        # dollar risk above the bar
        f'<text x="{cx:.2f}" y="{y - 27:.2f}" text-anchor="middle" class="sub">'
        f"${b['risk_usd']:,.0f} risked / trade</text>"
        # recovery note under the axis
        f'<text x="{cx:.2f}" y="{PT + PH + 22:.2f}" text-anchor="middle" class="lvl">'
        f"{b['label']} per trade</text>"
        f'<text x="{cx:.2f}" y="{PT + PH + 38:.2f}" text-anchor="middle" class="rec">'
        f"needs +{b['recover_pct']:.1f}% to recover</text>"
        f'<text x="{cx:.2f}" y="{PT + PH + 54:.2f}" text-anchor="middle" class="tag'
        f'{" cur" if current else ""}">'
        f"{b['tag']}</text>"
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"
     role="img" aria-label="Risk ladder on a 100,000 dollar account: after three consecutive losses, 1% risk loses 3.0%, 2% loses 5.9%, 3% loses 8.7% and 5% loses 14.3%, which crosses a 10% drawdown limit.">
<defs>
  <linearGradient id="gprev" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#4b4636"/>
    <stop offset="100%" stop-color="#2a2822"/>
  </linearGradient>
  <linearGradient id="gcur" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#e6c574" stop-opacity="0.92"/>
    <stop offset="100%" stop-color="#8f7a45" stop-opacity="0.55"/>
  </linearGradient>
  <style>
    .ax{{font:11px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#8b8f98;letter-spacing:.03em}}
    .val{{font:700 15px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#f2f1ee}}
    .sub{{font:11px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#c3c6cd}}
    .lvl{{font:700 12.5px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#f2f1ee}}
    .rec{{font:11px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#8b8f98}}
    .tag{{font:10px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#6d717a;letter-spacing:.1em;text-transform:uppercase}}
    .tag.cur{{fill:#e6c574}}
    .warntxt{{font:10.5px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#e0736a;letter-spacing:.04em}}
    .hdr{{font:10.5px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#8b8f98;letter-spacing:.12em;text-transform:uppercase}}
  </style>
</defs>
<text x="{PL}" y="18" class="hdr">$100,000 account · loss after {STREAK} consecutive losing trades</text>
<text x="{W - PR}" y="18" text-anchor="end" class="hdr">risk per trade</text>
{''.join(grid)}
{ref}
{''.join(body)}
</svg>
'''
OUT.write_text(svg)
print("wrote", OUT, len(svg), "bytes")
for b in bars:
    print(
        f"{b['label']:>3}  risk ${b['risk_usd']:>7,.0f}  "
        f"3 losses -> -{b['lost_pct']:.2f}%  (${b['left']:,.0f})  recover +{b['recover_pct']:.2f}%"
    )
