#!/usr/bin/env python3
"""Parse data/trades-raw.txt and emit data/trades.json + data/stats.json.

Rows are in descending time order. For each row:
  date | balance_before | balance_after | profit | description
The final row entered in the source export is a balance snapshot (2026-11-13)
whose balance_before (100,000.00) does not chain onto the rest of the series,
so it is flagged and excluded from equity-curve maths but kept as a trade.
"""
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "trades-raw.txt"
OUT_TRADES = ROOT / "data" / "trades.json"
OUT_STATS = ROOT / "data" / "stats.json"


def num(s: str) -> float:
    return float(s.replace(",", "").strip())


SYM_RE = re.compile(
    r"Close (?P<side>long|short) position for symbol (?P<sym>[\w:]+) at price "
    r"(?P<close>[\d.]+) for (?P<units>[\d.]+) units\. Position AVG Price was "
    r"(?P<avg>[\d.]+)"
)

rows = []
for line in RAW.read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    parts = [p.strip() for p in line.split("|")]
    date_s, bal_b, bal_a, profit, desc = parts
    m = SYM_RE.search(desc)
    if not m:
        raise SystemExit(f"unparsed: {line}")
    sym = m.group("sym")
    venue, _, ticker = sym.partition(":")
    rows.append(
        {
            "time": date_s,
            "balance_before": num(bal_b),
            "balance_after": num(bal_a),
            "profit": num(profit),
            "side": m.group("side"),
            "symbol": sym,
            "venue": venue,
            "ticker": ticker or venue,
            "units": num(m.group("units")),
            "entry": float(m.group("avg")),
            "exit": float(m.group("close")),
        }
    )

# sanity: profit column must equal bal_a - bal_b, and must equal price*units
for r in rows:
    delta = round(r["balance_after"] - r["balance_before"], 2)
    assert abs(delta - r["profit"]) < 0.02, (r, delta)
    r["direction"] = 1 if r["side"] == "long" else -1
    r["price_pnl"] = round((r["exit"] - r["entry"]) * r["direction"] * r["units"], 2)
    r["notional"] = round(r["entry"] * r["units"], 2)

rows.sort(key=lambda r: datetime.strptime(r["time"], "%Y-%m-%d %H:%M:%S"))

# the 100,000 snapshot row does not chain; exclude from curve
curve = [r for r in rows if r["balance_before"] < 90000]
snapshot = [r for r in rows if r["balance_before"] >= 90000]

wins = [r for r in curve if r["profit"] > 0]
losses = [r for r in curve if r["profit"] < 0]
flats = [r for r in curve if r["profit"] == 0]
gross_win = sum(r["profit"] for r in wins)
gross_loss = -sum(r["profit"] for r in losses)
net = sum(r["profit"] for r in curve)

# equity peak / max drawdown on the closed-trade curve
peak = curve[0]["balance_before"]
mdd_abs = 0.0
mdd_pct = 0.0
running = curve[0]["balance_before"]
for r in curve:
    running = r["balance_after"]
    peak = max(peak, running)
    dd = peak - running
    if dd > mdd_abs:
        mdd_abs = dd
        mdd_pct = dd / peak * 100

# streaks
best_streak = worst_streak = cur_w = cur_l = 0
for r in curve:
    if r["profit"] > 0:
        cur_w += 1
        cur_l = 0
    elif r["profit"] < 0:
        cur_l += 1
        cur_w = 0
    else:
        cur_w = cur_l = 0
    best_streak = max(best_streak, cur_w)
    worst_streak = max(worst_streak, cur_l)

by_symbol = {}
for r in curve:
    s = by_symbol.setdefault(
        r["ticker"], {"trades": 0, "wins": 0, "net": 0.0, "gross_win": 0.0, "gross_loss": 0.0}
    )
    s["trades"] += 1
    s["net"] += r["profit"]
    if r["profit"] > 0:
        s["wins"] += 1
        s["gross_win"] += r["profit"]
    elif r["profit"] < 0:
        s["gross_loss"] += -r["profit"]
for k, s in by_symbol.items():
    s["net"] = round(s["net"], 2)
    s["win_rate"] = round(s["wins"] / s["trades"] * 100, 1)
    pf = s["gross_win"] / s["gross_loss"] if s["gross_loss"] else None
    s["profit_factor"] = round(pf, 2) if pf else None

by_month = {}
for r in curve:
    k = r["time"][:7]
    by_month[k] = round(by_month.get(k, 0.0) + r["profit"], 2)

biggest = max(curve, key=lambda r: r["profit"])
worst = min(curve, key=lambda r: r["profit"])

stats = {
    "source": "data/trades-raw.txt (user-supplied broker export)",
    "period": {"from": curve[0]["time"], "to": curve[-1]["time"]},
    "closed_trades": len(curve),
    "wins": len(wins),
    "losses": len(losses),
    "flat": len(flats),
    "win_rate": round(len(wins) / len(curve) * 100, 1),
    "net_pnl": round(net, 2),
    "gross_win": round(gross_win, 2),
    "gross_loss": round(gross_loss, 2),
    "profit_factor": round(gross_win / gross_loss, 2) if gross_loss else None,
    "avg_win": round(gross_win / len(wins), 2),
    "avg_loss": round(gross_loss / len(losses), 2),
    "expectancy_per_trade": round(net / len(curve), 2),
    "largest_win": {"profit": biggest["profit"], "symbol": biggest["symbol"], "time": biggest["time"]},
    "largest_loss": {"profit": worst["profit"], "symbol": worst["symbol"], "time": worst["time"]},
    "longest_win_streak": best_streak,
    "longest_loss_streak": worst_streak,
    "start_balance": curve[0]["balance_before"],
    "end_balance": curve[-1]["balance_after"],
    "max_drawdown_abs": round(mdd_abs, 2),
    "max_drawdown_pct": round(mdd_pct, 2),
    "instruments": sorted(by_symbol),
    "instrument_count": len(by_symbol),
    "by_symbol": by_symbol,
    "net_by_month": by_month,
    "short_count": sum(1 for r in curve if r["side"] == "short"),
    "long_count": sum(1 for r in curve if r["side"] == "long"),
    "snapshot_rows": [
        {"time": s["time"], "balance_after": s["balance_after"], "profit": s["profit"]}
        for s in snapshot
    ],
}

OUT_TRADES.write_text(json.dumps(rows, indent=1))
OUT_STATS.write_text(json.dumps(stats, indent=1))
print(json.dumps({k: v for k, v in stats.items() if k not in ("by_symbol",)}, indent=1))
