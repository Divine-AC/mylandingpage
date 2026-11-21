#!/usr/bin/env python3
"""Parse data/trades-100k-raw.txt and emit data/trades-100k.json + data/stats-100k.json.

This is the *actual* $100,000 account from the broker export — a separate ledger
from the small account in data/trades-raw.txt, starting at exactly 100,000.00 on
2026-11-13. Every row chains: balance_before of a row equals balance_after of the
row before it, and profit equals (exit - entry) * direction * units exactly.

Nothing here is scaled or rebased. These are real fills.
"""
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "trades-100k-raw.txt"
OUT_TRADES = ROOT / "data" / "trades-100k.json"
OUT_STATS = ROOT / "data" / "stats-100k.json"


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
    date_s, bal_b, bal_a, profit, desc = [p.strip() for p in line.split("|")]
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

rows.sort(key=lambda r: datetime.strptime(r["time"], "%Y-%m-%d %H:%M:%S"))

# ---- integrity checks: these must pass or the numbers are not publishable ----
for i, r in enumerate(rows):
    delta = round(r["balance_after"] - r["balance_before"], 2)
    assert abs(delta - r["profit"]) < 0.02, f"profit != balance delta: {r}"
    r["direction"] = 1 if r["side"] == "long" else -1
    r["price_pnl"] = round((r["exit"] - r["entry"]) * r["direction"] * r["units"], 2)
    assert abs(r["price_pnl"] - r["profit"]) < 0.02, f"profit != price*units: {r}"
    r["notional"] = round(r["entry"] * r["units"], 2)
    if i:
        assert abs(r["balance_before"] - rows[i - 1]["balance_after"]) < 0.02, (
            f"ledger does not chain at {r['time']}"
        )

curve = rows
wins = [r for r in curve if r["profit"] > 0]
losses = [r for r in curve if r["profit"] < 0]
flats = [r for r in curve if r["profit"] == 0]
gross_win = sum(r["profit"] for r in wins)
gross_loss = -sum(r["profit"] for r in losses)
net = sum(r["profit"] for r in curve)

peak = curve[0]["balance_before"]
mdd_abs = mdd_pct = 0.0
for r in curve:
    peak = max(peak, r["balance_after"])
    dd = peak - r["balance_after"]
    if dd > mdd_abs:
        mdd_abs, mdd_pct = dd, dd / peak * 100

best_streak = worst_streak = cur_w = cur_l = 0
for r in curve:
    if r["profit"] > 0:
        cur_w, cur_l = cur_w + 1, 0
    elif r["profit"] < 0:
        cur_l, cur_w = cur_l + 1, 0
    else:
        cur_w = cur_l = 0
    best_streak, worst_streak = max(best_streak, cur_w), max(worst_streak, cur_l)

by_symbol = {}
for r in curve:
    s = by_symbol.setdefault(r["ticker"], {"trades": 0, "wins": 0, "net": 0.0,
                                           "gross_win": 0.0, "gross_loss": 0.0})
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
    s["profit_factor"] = round(s["gross_win"] / s["gross_loss"], 2) if s["gross_loss"] else None

biggest = max(curve, key=lambda r: r["profit"])
worst = min(curve, key=lambda r: r["profit"])

# the final two trades account for more than the whole net result — say so
last_two = sum(r["profit"] for r in curve[-2:])
without_last_two = net - last_two

stats = {
    "source": "data/trades-100k-raw.txt (user-supplied broker export, $100,000 account)",
    "basis": "actual ledger — no scaling, no rebasing",
    "period": {"from": curve[0]["time"], "to": curve[-1]["time"]},
    "days": (datetime.strptime(curve[-1]["time"], "%Y-%m-%d %H:%M:%S")
             - datetime.strptime(curve[0]["time"], "%Y-%m-%d %H:%M:%S")).days,
    "closed_trades": len(curve),
    "wins": len(wins),
    "losses": len(losses),
    "flat": len(flats),
    "win_rate": round(len(wins) / len(curve) * 100, 1),
    "net_pnl": round(net, 2),
    "return_pct": round(net / curve[0]["balance_before"] * 100, 2),
    "gross_win": round(gross_win, 2),
    "gross_loss": round(gross_loss, 2),
    "profit_factor": round(gross_win / gross_loss, 2) if gross_loss else None,
    "avg_win": round(gross_win / len(wins), 2),
    "avg_loss": round(-gross_loss / len(losses), 2),
    "expectancy_per_trade": round(net / len(curve), 2),
    "largest_win": {"profit": biggest["profit"], "symbol": biggest["symbol"],
                    "time": biggest["time"]},
    "largest_loss": {"profit": worst["profit"], "symbol": worst["symbol"],
                     "time": worst["time"]},
    "longest_win_streak": best_streak,
    "longest_loss_streak": worst_streak,
    "start_balance": curve[0]["balance_before"],
    "end_balance": curve[-1]["balance_after"],
    "peak": round(max([curve[0]["balance_before"]] + [r["balance_after"] for r in curve]), 2),
    "max_drawdown_abs": round(mdd_abs, 2),
    "max_drawdown_pct": round(mdd_pct, 2),
    "instruments": sorted(by_symbol),
    "instrument_count": len(by_symbol),
    "by_symbol": by_symbol,
    "net_by_month": {},
    "short_count": sum(1 for r in curve if r["side"] == "short"),
    "long_count": sum(1 for r in curve if r["side"] == "long"),
    "final_two_trades": round(last_two, 2),
    "net_without_final_two": round(without_last_two, 2),
    "max_notional": round(max(r["notional"] for r in curve), 2),
    "max_leverage": round(max(r["notional"] / r["balance_before"] for r in curve), 2),
    "max_risk_pct": round(max(-r["profit"] / r["balance_before"] for r in curve if r["profit"] < 0) * 100, 2),
}
stats["net_by_month"] = {}
for r in curve:
    k = r["time"][:7]
    stats["net_by_month"][k] = round(stats["net_by_month"].get(k, 0.0) + r["profit"], 2)

OUT_TRADES.write_text(json.dumps(rows, indent=1))
OUT_STATS.write_text(json.dumps(stats, indent=1))
print(json.dumps({k: v for k, v in stats.items() if k != "by_symbol"}, indent=1))
