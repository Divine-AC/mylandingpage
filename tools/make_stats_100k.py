#!/usr/bin/env python3
"""Render assets/equity-100k.svg — the equity curve rebased to a $100,000 start.

Every trade is scaled by one constant factor (100,000 / starting balance), so the
shape, win rate, profit factor and drawdown *percentage* are identical to the real
account — only the currency values change. This is a presentation of the same
record, not a different result.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = json.loads((ROOT / "data" / "trades.json").read_text())
curve = [r for r in rows if r["balance_before"] < 90000]

START = 100_000.0
factor = START / curve[0]["balance_before"]
vals = [START] + [r["balance_after"] * factor for r in curve]

W, H = 1000, 420
PL, PR, PT, PB = 8, 8, 26, 34
PW, PH = W - PL - PR, H - PT - PB

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

import math

raw = (hi - lo) / 4
mag = 10 ** math.floor(math.log10(raw))
step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=mag * 10)
grid = []
v = math.ceil(lo / step) * step
while v <= hi:
    y = Y(v)
    grid.append(
        f'<line x1="{PL}" y1="{y:.2f}" x2="{W - PR}" y2="{y:.2f}" '
        f'stroke="#ffffff" stroke-opacity="0.07" stroke-width="1"/>'
        f'<text x="{W - PR}" y="{y - 6:.2f}" text-anchor="end" class="ax">${v:,.0f}</text>'
    )
    v += step

peak_i = max(range(n), key=lambda i: vals[i])
last = vals[-1]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Equity curve of {len(curve)} closed trades scaled to a 100,000 dollar starting balance, ending at {last:,.0f} dollars.">
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
    .hdr{{font:10.5px ui-sans-serif,system-ui,-apple-system,sans-serif;fill:#c3c6cd;letter-spacing:.1em;text-transform:uppercase}}
  </style>
</defs>
<text x="{PL}" y="16" class="hdr">Scaled to a $100,000 starting balance</text>
{''.join(grid)}
<path d="{area}" fill="url(#fill)"/>
<path d="{line}" fill="none" stroke="url(#stroke)" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
<circle cx="{pts[-1][0]:.2f}" cy="{pts[-1][1]:.2f}" r="4" fill="#e6c574"/>
<text x="{PL}" y="{H - 10}" class="lbl">SEP 2026</text>
<text x="{W / 2:.0f}" y="{H - 10}" text-anchor="middle" class="lbl">CLOSED TRADES · {len(curve)}</text>
<text x="{W - PR}" y="{H - 10}" text-anchor="end" class="lbl">NOV 2026</text>
</svg>
'''
(ROOT / "assets" / "equity-100k.svg").write_text(svg)

# ---- write the rebased statistics ----
wins = [r for r in curve if r["profit"] > 0]
losses = [r for r in curve if r["profit"] < 0]
gross_win = sum(r["profit"] for r in wins)
gross_loss = -sum(r["profit"] for r in losses)

peak = vals[0]
mdd = 0.0
for v in vals:
    peak = max(peak, v)
    mdd = max(mdd, peak - v)

stats = {
    "factor": round(factor, 6),
    "source_start": curve[0]["balance_before"],
    "source_end": curve[-1]["balance_after"],
    "start": round(vals[0], 2),
    "end": round(vals[-1], 2),
    "net": round(vals[-1] - vals[0], 2),
    "return_pct": round((vals[-1] / vals[0] - 1) * 100, 2),
    "peak": round(max(vals), 2),
    "max_drawdown": round(mdd, 2),
    "max_drawdown_pct": round(mdd / max(vals) * 100, 2),
    "trades": len(curve),
    "wins": len(wins),
    "losses": len(losses),
    "win_rate": round(len(wins) / len(curve) * 100, 1),
    "profit_factor": round(gross_win / gross_loss, 2),
    "avg_win": round(gross_win / len(wins) * factor, 2),
    "avg_loss": round(-gross_loss / len(losses) * factor, 2),
    "largest_win": round(max(r["profit"] for r in curve) * factor, 2),
    "largest_loss": round(min(r["profit"] for r in curve) * factor, 2),
    "expectancy": round(sum(r["profit"] for r in curve) / len(curve) * factor, 2),
    "period": {"from": curve[0]["time"][:10], "to": curve[-1]["time"][:10]},
}
(ROOT / "data" / "stats-100k.json").write_text(json.dumps(stats, indent=1))
print(json.dumps(stats, indent=1))
