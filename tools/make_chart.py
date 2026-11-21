#!/usr/bin/env python3
"""Render the closed-trade equity curve to assets/equity-curve.svg.

Design intent (per user decision): show the curve, not headline performance
statistics. No win-rate / net-P&L callouts, no peak/drawdown annotations.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = json.loads((ROOT / "data" / "trades.json").read_text())
curve = [r for r in rows if r["balance_before"] < 90000]

W, H = 1000, 420
PL, PR, PT, PB = 8, 8, 22, 34
PW, PH = W - PL - PR, H - PT - PB

vals = [curve[0]["balance_before"]] + [r["balance_after"] for r in curve]
lo, hi = min(vals), max(vals)
pad = (hi - lo) * 0.12
lo, hi = lo - pad, hi + pad

n = len(vals)


def X(i):
    return PL + PW * i / (n - 1)


def Y(v):
    return PT + PH * (1 - (v - lo) / (hi - lo))


pts = [(X(i), Y(v)) for i, v in enumerate(vals)]
line = " ".join(f"{'M' if i == 0 else 'L'}{x:.2f},{y:.2f}" for i, (x, y) in enumerate(pts))
area = line + f" L{pts[-1][0]:.2f},{PT + PH} L{pts[0][0]:.2f},{PT + PH} Z"

# gridlines on nice round values
import math
raw = (hi - lo) / 4
mag = 10 ** math.floor(math.log10(raw))
step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=mag * 10)
grid = []
v = math.ceil(lo / step) * step
ticks = []
while v <= hi:
    ticks.append(v)
    v += step
for v in ticks:
    y = Y(v)
    grid.append(
        f'<line x1="{PL}" y1="{y:.2f}" x2="{W - PR}" y2="{y:.2f}" '
        f'stroke="#ffffff" stroke-opacity="0.07" stroke-width="1"/>'
        f'<text x="{W - PR}" y="{y - 6:.2f}" text-anchor="end" class="ax">{v:,.0f}</text>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Equity curve of {len(curve)} closed trades, September to November 2026">
<defs>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#d8b25f" stop-opacity="0.28"/>
    <stop offset="100%" stop-color="#d8b25f" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="stroke" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#8f7a45"/>
    <stop offset="55%" stop-color="#e6c574"/>
    <stop offset="100%" stop-color="#d8b25f"/>
  </linearGradient>
  <style>
    .ax{{font:11px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#8b8f98;letter-spacing:.04em}}
    .lbl{{font:11px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#8b8f98;letter-spacing:.08em}}
  </style>
</defs>
<rect width="{W}" height="{H}" fill="none"/>
{''.join(grid)}
<path d="{area}" fill="url(#fill)"/>
<path d="{line}" fill="none" stroke="url(#stroke)" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="{pts[-1][0]:.2f}" cy="{pts[-1][1]:.2f}" r="4" fill="#e6c574"/>
<text x="{PL}" y="{H - 10}" class="lbl">SEP 2026</text>
<text x="{W / 2:.0f}" y="{H - 10}" text-anchor="middle" class="lbl">CLOSED TRADES · {len(curve)}</text>
<text x="{W - PR}" y="{H - 10}" text-anchor="end" class="lbl">NOV 2026</text>
</svg>
'''
(ROOT / "assets" / "equity-curve.svg").write_text(svg)
print("wrote assets/equity-curve.svg", len(svg), "bytes; range", round(lo), round(hi))
