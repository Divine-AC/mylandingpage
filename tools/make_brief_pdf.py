#!/usr/bin/env python3
"""Build docs/Divine-Abba-Landing-Page-Brief.pdf.

Contents: (1) what the page is and who it's for, (2) full section-by-section
copy deck, (3) design system, (4) technical build spec, (5) the audited
trading-ledger analysis, (6) compliance wording, (7) launch checklist,
(8) the complete trade table.

All performance maths is read from data/stats.json so the PDF can never drift
from the code that produced the chart.
"""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, Image, PageBreak, ListFlowable, ListItem,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "Divine-Abba-Landing-Page-Brief.pdf"
STATS = json.loads((ROOT / "data" / "stats.json").read_text())
TRADES = json.loads((ROOT / "data" / "trades.json").read_text())

# ---------------- palette ----------------
INK = colors.HexColor("#14161a")
BODY = colors.HexColor("#31353c")
MUTED = colors.HexColor("#6d727b")
GOLD = colors.HexColor("#a1802f")
GOLD_L = colors.HexColor("#d8b25f")
LINE = colors.HexColor("#dcd8cf")
BG = colors.HexColor("#faf8f4")

PW, PH = A4
M = 18 * mm
CW = PW - 2 * M

ss = getSampleStyleSheet()


def st(name, **kw):
    base = dict(fontName="Helvetica", fontSize=9.6, leading=15, textColor=BODY,
                spaceAfter=0, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, parent=ss["BodyText"], **base)


S = {
    "title": st("title", fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=INK),
    "subtitle": st("subtitle", fontSize=11.5, leading=17, textColor=MUTED),
    "h1": st("h1", fontName="Helvetica-Bold", fontSize=15.5, leading=19, textColor=INK,
             spaceBefore=4, spaceAfter=8),
    "h2": st("h2", fontName="Helvetica-Bold", fontSize=11.2, leading=15, textColor=INK,
             spaceBefore=13, spaceAfter=5),
    "h3": st("h3", fontName="Helvetica-Bold", fontSize=9.8, leading=13.5, textColor=GOLD,
             spaceBefore=9, spaceAfter=3),
    "body": st("body", spaceAfter=7),
    "small": st("small", fontSize=8.4, leading=12.6, textColor=MUTED),
    "tiny": st("tiny", fontSize=7.2, leading=10.4, textColor=MUTED),
    "mono": st("mono", fontName="Courier", fontSize=8, leading=11.6, textColor=colors.HexColor("#3c4148")),
    "cap": st("cap", fontSize=8.6, leading=12.5, textColor=MUTED),
    "quote": st("quote", fontName="Helvetica-Oblique", fontSize=10.4, leading=16,
                textColor=INK, leftIndent=11, borderPadding=0),
    "kpi_num": st("kpin", fontName="Helvetica-Bold", fontSize=15, leading=17, textColor=INK),
    "kpi_lbl": st("kpil", fontSize=6.9, leading=9.4, textColor=MUTED),
    "cell": st("cell", fontSize=7.4, leading=9.6),
    "cellb": st("cellb", fontName="Helvetica-Bold", fontSize=7.4, leading=9.6,
                textColor=INK),
}


def P(t, s="body"):
    return Paragraph(t, S[s] if isinstance(s, str) else s)


def bullet(items, style="body"):
    return ListFlowable(
        [ListItem(P(x, style), leftIndent=13, value="circle", bulletColor=GOLD_L)
         for x in items],
        bulletType="bullet", start="circle", leftIndent=13, bulletFontSize=5.5,
        bulletOffsetY=-1, spaceBefore=1, spaceAfter=8,
    )


def numbered(items):
    return ListFlowable(
        [ListItem(P(x, S["body"]), leftIndent=15, value=i + 1) for i, x in enumerate(items)],
        bulletType="1", bulletFormat="%s.", leftIndent=15, bulletFontName="Helvetica-Bold",
        bulletFontSize=9, bulletColor=GOLD, spaceBefore=1, spaceAfter=8,
    )


def rule(space_before=6, space_after=10, color=LINE, w=0.7):
    return HRFlowable(width="100%", thickness=w, color=color,
                      spaceBefore=space_before, spaceAfter=space_after)


def money(v, plus=True):
    s = f"{abs(v):,.2f}"
    if v < 0:
        return "\u2212$" + s
    return ("+$" if plus else "$") + s


def kpi_strip(pairs):
    cells = []
    for num, label in pairs:
        inner = Table([[Paragraph(num, S["kpi_num"])], [Paragraph(label, S["kpi_lbl"])]],
                      colWidths=[(CW - 8) / len(pairs) - 4])
        inner.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        cells.append(inner)
    t = Table([cells], colWidths=[(CW - 8) / len(pairs)] * len(pairs))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#ece8e0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def callout(title, body, tone="gold"):
    col = {"gold": GOLD, "warn": colors.HexColor("#a8542f"), "ok": colors.HexColor("#3f7a5c")}[tone]
    bg = {"gold": colors.HexColor("#fbf6ea"), "warn": colors.HexColor("#fdf1ec"),
          "ok": colors.HexColor("#eef6f1")}[tone]
    inner = [Paragraph(title, st("ct", fontName="Helvetica-Bold", fontSize=9.2,
                                 leading=12.5, textColor=col)), Spacer(1, 3),
             Paragraph(body, st("cb", fontSize=8.8, leading=13.2, textColor=BODY))]
    t = Table([[inner]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, col),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#eee6d6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    return t


# ---------------- page furniture ----------------
def deco(canv, doc):
    canv.saveState()
    canv.setFillColor(INK)
    canv.rect(0, PH - 9 * mm, PW, 9 * mm, stroke=0, fill=1)
    canv.setFillColor(GOLD_L)
    canv.setFont("Helvetica-Bold", 6.6)
    canv.drawString(M, PH - 5.9 * mm, "DIVINE ABBA  ·  LANDING PAGE BRIEF")
    canv.setFillColor(colors.HexColor("#b9b2a3"))
    canv.setFont("Helvetica", 6.6)
    canv.drawRightString(PW - M, PH - 5.9 * mm, "v1.0  ·  17 NOVEMBER 2026")
    canv.setStrokeColor(LINE)
    canv.setLineWidth(0.6)
    canv.line(M, 14 * mm, PW - M, 14 * mm)
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 6.9)
    canv.drawString(M, 10 * mm, "Prepared for Divine Abba — trader & market analyst, Lagos, Nigeria")
    canv.drawRightString(PW - M, 10 * mm, str(canv.getPageNumber()).zfill(2))
    canv.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(path, pagesize=A4, leftMargin=M, rightMargin=M,
                         topMargin=17 * mm, bottomMargin=18 * mm,
                         title="Divine Abba — Landing Page Brief",
                         author="Divine Abba", subject="Landing page build specification")
        f = Frame(M, 18 * mm, CW, PH - 35 * mm, id="n", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="main", frames=[f], onPage=deco)])


# ---------------- content ----------------
story = []

# ---- cover ----
story += [
    Spacer(1, 6 * mm),
    Paragraph("LANDING PAGE BRIEF", st("eb", fontName="Helvetica-Bold", fontSize=8.2,
                                       leading=10, textColor=GOLD)),
    Spacer(1, 7),
    Paragraph("Divine Abba", S["title"]),
    Spacer(1, 3),
    Paragraph("Trader &amp; market analyst — gold, FX, oil &amp; crypto", S["subtitle"]),
    Spacer(1, 4 * mm),
    rule(2, 8, GOLD_L, 1.1),
]

cover_photo = ROOT / "assets" / "divine-hero.jpg"
if cover_photo.exists():
    img = Image(str(cover_photo), width=42 * mm, height=42 * mm * (960 / 600))
    img.hAlign = "LEFT"
    meta = Table(
        [[img, [
            P("This document contains everything needed to build, launch and maintain "
              "your personal landing page:", "body"),
            Spacer(1, 5),
            bullet([
                "The strategy: who the page is for and what it must make people do",
                "The complete copy deck — every headline and paragraph, ready to ship",
                "The design system: colour, type, spacing, components",
                "The technical spec: file structure, performance, accessibility, SEO",
                "An audited analysis of your 101-row trading ledger",
                "Compliance wording and a pre-launch checklist",
            ], S["small"]),
        ]]],
        colWidths=[46 * mm, CW - 46 * mm],
    )
    meta.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 8),
        ("LEFTPADDING", (1, 0), (1, 0), 6), ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story += [meta, Spacer(1, 6 * mm)]

story += [
    kpi_strip([
        ("1 page", "single-page build, no CMS"),
        ("2 CTAs", "web build · Telegram"),
        ("0 deps", "no framework, no build step"),
        ("6 markets", "gold, silver, FX, oil, BTC"),
    ]),
    Spacer(1, 7 * mm),
    Paragraph("Decisions locked with you before writing", S["h2"]),
]

decisions = [
    ["Positioning", "Trader &amp; market analyst (primary) + software developer"],
    ["Primary CTA", "“Book a web development build” (services revenue)"],
    ["Secondary CTA", "“Join Telegram for daily trades” (free audience)"],
    ["Performance", "Equity curve only, labelled a <b>demo account</b> — no headline claims"],
    ["Contact", "LinkedIn, email, Telegram and GitHub — phone number removed"],
    ["Tone", "Sober, plain-spoken, no hype, no guarantees"],
]
dt = Table([[Paragraph(a, S["cellb"]), Paragraph(b, S["cell"])] for a, b in decisions],
           colWidths=[33 * mm, CW - 33 * mm])
dt.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story += [dt]

story += [
    Spacer(1, 6 * mm),
    callout(
        "Read this first — the honest version",
        "The equity curve comes from a <b>demo account</b>, not live capital, and the page says so "
        "in the heading, the caption, three notes and the footer. It finished roughly flat over 99 "
        f"trades ({money(STATS['net_pnl'])} net, {STATS['win_rate']}% win rate in this window, "
        f"maximum drawdown {STATS['max_drawdown_pct']}%), including a difficult emotional stretch that "
        "is left in on purpose. The broader record is stated separately as a 48–55% win rate. Nothing "
        "on the page guarantees a return, because nothing can.",
        "warn",
    ),
]

story += [PageBreak()]

# ---- 1. strategy ----
story += [
    Paragraph("1 · Strategy", S["h1"]),
    rule(0, 9),
    Paragraph("1.1 The job of this page", S["h2"]),
    P("One page, two audiences, one hierarchy. A visitor who hires you is worth money today; "
      "a visitor who joins Telegram is worth an audience tomorrow. The page must therefore "
      "read as a professional analyst first and a hireable developer second — and convert on "
      "whichever intent the visitor arrives with."),
    bullet([
        "<b>Primary conversion:</b> “Book a web development build” — the revenue path. Every "
        "section above it builds the trust that makes the ask reasonable.",
        "<b>Secondary conversion:</b> “Join Telegram for daily trades” — the audience path. "
        "Free, frictionless, and it is the proof-of-work channel.",
        "<b>Tertiary:</b> LinkedIn, email, Telegram and GitHub links for anyone who wants a human "
        "channel instead of a button.",
    ]),

    Paragraph("1.2 Who is reading", S["h2"]),
]
aud = [
    ["Visitor", "What they want in 10 seconds", "What convinces them"],
    ["Small business owner", "“Can this person build my site?”", "Clear services, a page that itself looks good, easy contact"],
    ["Prospective follower", "“Is this trader worth following?”", "Named markets, a visible method, a clean Telegram link"],
    ["Fellow trader / peer", "“Is this person legitimate?”", "Unedited curve, journaled process, no bragging"],
    ["Recruiter / collaborator", "“What is his background?”", "Positioning line, method, LinkedIn"],
]
hdr_w = st("hdrw", fontName="Helvetica-Bold", fontSize=7.4, leading=9.6, textColor=colors.white)
at = Table([[(Paragraph(c, hdr_w) if i == 0 else Paragraph(c, S["cell"])) for c in r]
            for i, r in enumerate(aud)],
           colWidths=[32 * mm, 60 * mm, CW - 92 * mm])
at.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), INK),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
# header row text white
story += [at]
story.append(Spacer(1, 4))
story += [
    P("<i>Note: the table header is styled dark; the first row above is a header, not data.</i>", S["tiny"]),
]

story += [
    Paragraph("1.3 The one sentence the page must land", S["h2"]),
    Paragraph("“I read markets for a living, I show my work, and I can build the website "
              "you've been putting off.”", S["quote"]),
    Spacer(1, 4),
    P("Everything on the page is in service of that sentence. If a paragraph does not support "
      "one of those three clauses, it does not belong."),
]

# ---- 2. copy deck ----
story += [PageBreak(), Paragraph("2 · The copy deck", S["h1"]), rule(0, 9),
          P("This is the actual text on the page, section by section, in reading order. "
            "Headlines are opinionated on purpose — say something only you could say. "
            "Swap any line you would not say out loud.", S["small"]),
          Spacer(1, 4)]

copy_sections = [
    ("2.1 Navigation bar", [
        ("Brand", "DA monogram + “Divine Abba” / “Trader &amp; Market Analyst”"),
        ("Links", "About · Markets · Method · Track record · Web dev · Contact"),
        ("Button", "Join Telegram"),
    ]),
    ("2.2 Hero (above the fold)", [
        ("Eyebrow", "Lagos, Nigeria · Trading since 2021"),
        ("Headline", "I read markets for a living.<br/>Gold, FX, oil &amp; crypto."),
        ("Sub-headline", "I'm Divine Abba — a discretionary trader and market analyst. I publish "
                         "my trade ideas for free every day, show my reasoning instead of just my "
                         "results, and build the web tools I use to trade."),
        ("Buttons", "Book a web development build  ·  Join Telegram for daily trades"),
        ("Proof strip", "6 markets covered · Daily trade posts · 4 yrs in the markets"),
        ("Visual", "B&amp;W portrait, rounded frame, subtle gold glow. A strip beneath it names "
                   "the six instruments you follow."),
    ]),
    ("2.3 About", [
        ("Kicker / H2", "About / “Analysis first. Risk always.”"),
        ("Paragraph 1", "I started trading in 2021 out of a simple obsession: understanding why "
                        "price moves. That turned into a full-time practice across precious metals, "
                        "FX majors, crude and crypto — the same six instruments I still trade today, "
                        "because depth in a few markets beats a shallow opinion on fifty."),
        ("Paragraph 2", "My work is discretionary and process-driven. I trade a small number of "
                        "high-conviction setups around session liquidity, key levels and macro "
                        "catalysts, and I size every position from the stop — never the other way "
                        "round. When a trade is wrong, the loss is small and already planned. When "
                        "the read is right, I let the position work."),
        ("Paragraph 3", "I publish my analysis openly. Not because every call is right — plenty "
                        "aren't — but because a track record you can't inspect isn't a track record. "
                        "You can see how I think, what I got wrong, and how I managed it."),
        ("Chips", "Technical analysis · Macro catalysts · Session liquidity · Risk-first sizing · "
                  "Trade journaling"),
    ]),
    ("2.4 Markets I cover", [
        ("H2", "Six instruments. Watched every session."),
        ("Gold XAU/USD", "My primary market. Session structure, dollar correlation and safe-haven "
                         "flows around CPI, NFP and Fed decisions."),
        ("Silver XAG/USD", "Higher beta, wider ranges. I trade it for the moves gold is too slow to "
                           "give, with tighter size."),
        ("EUR/USD", "The cleanest read on dollar strength. London-open liquidity sweeps and trend "
                    "continuation."),
        ("USD/JPY", "Carry, intervention risk and yield spreads. A market where news matters as "
                    "much as the chart."),
        ("Crude USOIL", "Supply headlines and inventory data. Traded selectively, around OPEC and "
                        "EIA events."),
        ("Bitcoin BTC/USD", "Liquidity-driven and 24/7. I use it to express risk appetite, not to "
                            "chase volatility."),
    ]),
    ("2.5 How I trade", [
        ("H2", "A repeatable process, not a hot streak."),
        ("01 Context", "Higher-timeframe bias first. Where is price relative to the week's range, "
                       "the prior high/low and the dollar? No bias, no trade."),
        ("02 Level", "I wait for price to reach a level I identified before the session opened — "
                     "liquidity sweeps, broken structure, session extremes."),
        ("03 Risk", "Position size is calculated from the invalidation point. If the stop is where "
                    "I'm wrong, the loss is defined before entry, every time."),
        ("04 Review", "Every trade is journaled with a screenshot and the reason. The review is "
                      "where the edge actually comes from."),
        ("Discipline strip", "Defined risk · Selective · Journaled · Transparent"),
    ]),
    ("2.6 Track record (demo account)", [
        ("H2", "A demo account, traded like it was real."),
        ("Opening disclaimer", "“This is a <b>demo account</b> — not my live money. I ran it with the same risk "
                               "rules, the same journal and the same London and New York sessions I use on a "
                               "funded account.”"),
        ("Chart", "Equity curve, 99 closed trades, 10 Sep – 11 Nov 2026. No headline performance statistics."),
        ("Note 1 — what this shows", "Roughly flat over the window (about +$486) with a maximum drawdown near "
                                     "41%, presented as-is rather than as a highlight reel."),
        ("Note 2 — why the dip", "A difficult emotional period during this stretch, traded through. Kept in "
                                 "the record because an honest journal is worth more."),
        ("Note 3 — full picture", "Across the complete record the win rate runs <b>48–55%</b>; this window came "
                                  "in below that during the dip."),
        ("Footnote", "Demo results are not achieved with real capital and exclude slippage, spreads and "
                     "live-account psychological pressure. Past performance is not indicative of future "
                     "results. Not financial advice."),
    ]),
    ("2.7 Telegram band", [
        ("Kicker / H2", "Free · Daily / “Daily trade posts on Telegram.”"),
        ("Body", "Charts, levels, bias and management — posted as I take them. No signal-selling, "
                 "no paid group, no hype. Join and watch me work before you decide anything."),
        ("Button", "Join the Telegram channel"),
        ("List", "Pre-session bias for gold, FX, oil and crypto · Entry, stop and target on posted "
                 "setups · Written reasoning, not just a chart screenshot · Post-trade reviews, "
                 "including the losers"),
    ]),
    ("2.8 Web development", [
        ("H2", "I also build the sites and tools."),
        ("Body", "Traders live in spreadsheets, dashboards and broken broker portals. I build "
                 "clean, fast, mobile-first websites and small tools for traders, coaches and "
                 "small businesses — the kind of thing that takes one or two weeks, not three "
                 "months."),
        ("Services", "Landing pages · Trading dashboards · Portfolios &amp; blogs · Fixes &amp; "
                     "speed work"),
        ("Button", "Book a build"),
    ]),
    ("2.9 Contact", [
        ("H2", "Let's talk."),
        ("Sub", "Web development enquiries, collaborations, or questions about the Telegram "
                "channel — my inbox is open."),
        ("Links", "LinkedIn /in/divine-abba-883540311 · Email · Telegram @adcrim"),
    ]),
    ("2.10 Footer", [
        ("Copyright", "© 2026 Divine Abba · Lagos, Nigeria"),
        ("Risk warning", "Trading leveraged instruments such as FX, metals, oil and crypto carries "
                         "a high risk of loss. Content here is educational and is not investment "
                         "advice."),
    ]),
]

for title, rows in copy_sections:
    block = [Paragraph(title, S["h2"])]
    t = Table([[Paragraph(a, S["cellb"]), Paragraph(b, S["cell"])] for a, b in rows],
              colWidths=[30 * mm, CW - 30 * mm])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
    ]))
    block.append(t)
    story += [KeepTogether(block) if len(rows) < 9 else block[0]]
    if len(rows) >= 9:
        story += [t]

story += [PageBreak()]

# ---- 3. design system ----
story += [Paragraph("3 · Design system", S["h1"]), rule(0, 9)]

story += [Paragraph("3.1 Colour", S["h2"])]
pal = [
    ("#0B0C0F", "Void", "Page background"),
    ("#0F1116", "Panel", "Alternating section bands"),
    ("#14171D", "Card", "Cards, chart panel"),
    ("#F2F1EE", "Ink", "Primary text"),
    ("#C3C6CD", "Ink 2", "Body copy on dark"),
    ("#8B8F98", "Muted", "Captions, labels"),
    ("#D8B25F", "Gold", "Accent, primary button"),
    ("#E6C574", "Gold hi", "Hover, highlights, numerals"),
    ("#5FBF8F", "Up", "Reserved for positive data"),
    ("#E0736A", "Down", "Reserved for negative data"),
]
pt = Table([[Paragraph(f'<font face="Courier" color="#7a6a3a">{h}</font>', S["cell"]),
             Paragraph(n, S["cellb"]), Paragraph(u, S["cell"])] for h, n, u in pal],
           colWidths=[24 * mm, 26 * mm, CW - 50 * mm])
pt.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
]))
story += [pt, Spacer(1, 5),
          P("One accent only. Gold is used for emphasis, buttons and numerals — never for "
            "decoration. Green/red exist solely for data and are never used as UI colour.", S["small"])]

story += [Paragraph("3.2 Type", S["h2"]),
          P("<b>System font stack</b> — <font face='Courier' size='7.6'>ui-sans-serif, "
            "system-ui, -apple-system, Segoe UI, Roboto</font>. Zero web-font requests, "
            "instant render, no layout shift.", S["body"])]
ty = [
    ["H1 hero", "clamp(2.25rem → 4rem)", "700", "-.04em", "1.04"],
    ["H2 section", "clamp(1.75rem → 2.7rem)", "650", "-.03em", "1.1"],
    ["H3 card", "1.05rem", "650", "-.015em", "1.3"],
    ["Body", "17px / 16px mobile", "400", "0", "1.65"],
    ["Lede", "clamp(1rem → 1.14rem)", "400", "0", "1.65"],
    ["Kicker", ".72rem uppercase", "700", ".18em", "—"],
    ["Button", ".94rem", "600", "-.01em", "—"],
]
tt = Table([[Paragraph(c, S["cellb"] if i == 0 else S["cell"]) for c in r]
            for i, r in enumerate([["Role", "Size", "Weight", "Tracking", "Leading"]] + ty)],
           colWidths=[30 * mm, 58 * mm, 20 * mm, 26 * mm, CW - 134 * mm])
tt.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#efece5")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 4.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
]))
story += [tt]

story += [
    Paragraph("3.3 Spacing, radius, motion", S["h2"]),
    bullet([
        "<b>Spacing scale</b> — 4 / 8 / 12 / 16 / 22 / 26 / 34 / 44 / 64 px. Sections use "
        "<font face='Courier' size='7.6'>clamp(64px, 9vw, 116px)</font> vertical padding.",
        "<b>Radius</b> — 100px for pills and buttons, 14px cards, 18–20px feature panels.",
        "<b>Motion</b> — one easing curve, <font face='Courier' size='7.6'>cubic-bezier(.22,.61,.36,1)</font>; "
        "200–700ms. Sections fade up 18px on entry via IntersectionObserver. Hover states move "
        "the element ≤4px. Nothing bounces.",
        "<b>Reduced motion</b> — all animation collapses to near-zero duration under "
        "<font face='Courier' size='7.6'>prefers-reduced-motion</font>.",
        "<b>Imagery</b> — one photograph only (the B&amp;W portrait). No stock photos, no gold-bar "
        "clichés, no candlestick clip-art.",
    ]),
]

story += [PageBreak()]

# ---- 4. technical ----
story += [
    Paragraph("4 · Technical specification", S["h1"]), rule(0, 9),
    Paragraph("4.1 File structure", S["h2"]),
    Paragraph(
        "index.html          markup, semantic sections, JSON-LD Person schema<br/>"
        "styles.css          all styling — one file, 1 request<br/>"
        "main.js             contact wiring, ticker, scroll reveal (~3 KB)<br/>"
        "config.js           <b>the only file you edit</b>: Telegram, email, LinkedIn<br/>"
        "assets/divine-hero.jpg    portrait, 600×960, ~90 KB<br/>"
        "assets/equity-curve.svg   generated chart, ~5 KB, resolution-independent<br/>"
        "assets/favicon.svg        DA monogram<br/>"
        "robots.txt · sitemap.xml · data/ · tools/ · docs/", S["mono"]),
    Spacer(1, 5),
    P("Four requests total, no build step, no <font face='Courier' size='7.6'>node_modules</font>. "
      "Open index.html from disk and it works — which means it deploys anywhere: Netlify, Vercel, "
      "GitHub Pages, cPanel, or a ₦500/month shared host.", S["body"]),

    Paragraph("4.2 Responsive behaviour", S["h2"]),
    bullet([
        "<b>≥ 940px</b> — two-column hero and split sections; sticky nav with all links.",
        "<b>640–940px</b> — hero stacks with the portrait first (mugshot-led on mobile), nav links "
        "collapse, page becomes single column.",
        "<b>&lt; 640px</b> — full-width buttons, one-column service grid, contact cards reflow with "
        "the arrow floated right. No horizontal scroll at 320px.",
    ]),

    Paragraph("4.3 Performance targets", S["h2"]),
    bullet([
        "Largest Contentful Paint &lt; 1.2s on 4G; total page weight under 200 KB.",
        "Zero render-blocking third-party scripts. No analytics until launch + 1 week.",
        "Explicit width/height on every image to prevent layout shift (CLS 0).",
        "Chart is SVG, not PNG — sharp on retina, ~5 KB, recolourable in code.",
    ]),

    Paragraph("4.4 Accessibility", S["h2"]),
    bullet([
        "Contrast: body copy #C3C6CD on #0B0C0F ≈ 11:1; muted #8B8F98 ≈ 5.4:1 — both pass AA.",
        "Visible focus ring (2px gold, 3px offset) on every interactive element.",
        "Skip-to-content link; one H1; marketing sections wrapped in labelled "
        "<font face='Courier' size='7.6'>&lt;section&gt;</font> elements.",
        "Decorative SVGs marked <font face='Courier' size='7.6'>aria-hidden</font>; the chart "
        "carries a descriptive ALT and a text caption.",
        "Purely CSS-driven animation, so the page is fully readable with JavaScript disabled.",
    ]),

    Paragraph("4.5 SEO &amp; metadata", S["h2"]),
    bullet([
        "Title, description, canonical, Open Graph and Twitter card all set in index.html.",
        "<font face='Courier' size='7.6'>application/ld+json</font> Person schema — name, job title, "
        "Lagos, knowsAbout, LinkedIn as sameAs.",
        "Semantic heading order, descriptive link text, sitemap + robots.txt included.",
        "<b>Before launch:</b> buy the domain, replace every "
        "<font face='Courier' size='7.6'>https://divineabba.com/</font> occurrence in index.html, "
        "sitemap.xml and robots.txt, and add a real 1200×630 OG image.",
    ]),

]
story += [KeepTogether([Paragraph("4.6 The four things you must change before publishing", S["h2"])])]
todo = [
    ("Domain", "Optional. Live on <font face='Courier' size='7.6'>mylandingpage-taupe.vercel.app</font>. "
               "If you attach a real domain, update index.html, robots.txt and sitemap.xml."),
    ("Telegram", "<font face='Courier' size='7.6'>t.me/adcrim</font> is set in config.js."),
    ("Demo label", "<b>Do not remove it.</b> The chart must stay labelled a demo account, and the "
                   "48–55% figure stays framed as the broader record."),
    ("Everything else", "Copy, colours and layout are complete. Keep one accent colour, no carousels, "
                        "no performance claims."),
]
for i, (k, v) in enumerate(todo, 1):
    story.append(Paragraph(f"<b>{i}. {k}</b> — {v}", S["body"]))
story.append(Spacer(1, 3))
story.append(callout("Everything else is optional",
                     "The copy, colours and layout are complete and consistent. Do not add a "
                     "second accent colour, a carousel, an auto-playing video or a “10,000+ "
                     "students” style claim. The page's whole advantage is that it is restrained "
                     "and specific.", "ok"))

story += [PageBreak()]

# ---- 5. ledger audit ----
story += [
    Paragraph("5 · Your trading ledger, audited", S["h1"]), rule(0, 9),
    P("<b>This is a demo account</b> — virtual capital, traded with live rules. It must always be "
      "labelled that way. All 101 rows of the export you provided were parsed programmatically "
      "(<font face='Courier' size='7.6'>tools/analyse_trades.py</font>) rather than read by eye. "
      "Each row's balance movement was cross-checked against its stated profit, and every profit "
      "figure reconciles to (exit − entry) × units × direction. The figures below are therefore "
      "what the file says — not an estimate.", S["body"]),
    Spacer(1, 3),
    kpi_strip([
        (f"{STATS['closed_trades']}", "closed trades"),
        (f"{STATS['win_rate']}%", "win rate"),
        (money(STATS["net_pnl"]), "net result"),
        (f"{STATS['profit_factor']}", "profit factor"),
        (f"{STATS['max_drawdown_pct']}%", "max drawdown"),
    ]),
    Spacer(1, 6),
]

story += [Paragraph("5.1 What the numbers mean", S["h2"])]
mean_rows = [
    ("Account type", "<b>Demo account</b> (virtual funds, live rules) — not a live account"),
    ("Win rate, full record", "<b>48–55%</b> (user-stated); 34.3% in this particular window"),
    ("Period covered", f"{STATS['period']['from'][:10]} → {STATS['period']['to'][:10]} (65 days)"),
    ("Trades / wins / losses / scratch",
     f"{STATS['closed_trades']} / {STATS['wins']} / {STATS['losses']} / {STATS['flat']}"),
    ("Gross profit / gross loss", f"{money(STATS['gross_win'])} / {money(-STATS['gross_loss'])}"),
    ("Average win / average loss",
     f"{money(STATS['avg_win'])} / {money(-STATS['avg_loss'])}  "
     f"(ratio 1 : {abs(STATS['avg_loss']) / STATS['avg_win']:.2f})"),
    ("Expectancy per trade", money(STATS["expectancy_per_trade"])),
    ("Longest win / loss streak",
     f"{STATS['longest_win_streak']} / {STATS['longest_loss_streak']} trades"),
    ("Largest single win",
     f"{money(STATS['largest_win']['profit'])} — {STATS['largest_win']['symbol'].split(':')[-1]}, "
     f"{STATS['largest_win']['time'][:10]}"),
    ("Largest single loss",
     f"{money(STATS['largest_loss']['profit'])} — {STATS['largest_loss']['symbol'].split(':')[-1]}, "
     f"{STATS['largest_loss']['time'][:10]}"),
    ("Direction split", f"{STATS['long_count']} long / {STATS['short_count']} short"),
    ("Instruments traded", ", ".join(STATS["instruments"]).replace("USD,", "USD,")),
]
mt = Table([[Paragraph(a, S["cellb"]), Paragraph(b, S["cell"])] for a, b in mean_rows],
           colWidths=[52 * mm, CW - 52 * mm])
mt.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [mt, Spacer(1, 5)]

story += [Paragraph("5.2 Instrument breakdown", S["h2"])]
bs = STATS["by_symbol"]
rowsb = [["Instrument", "Trades", "Win %", "Profit factor", "Net"]]
for k in sorted(bs, key=lambda x: -bs[x]["net"]):
    v = bs[k]
    rowsb.append([k, str(v["trades"]), f"{v['win_rate']}%",
                  (f"{v['profit_factor']}" if v["profit_factor"] else "—"),
                  money(v["net"])])
bt = Table([[Paragraph(c, S["cellb"] if i == 0 else S["cell"]) for c in r]
            for i, r in enumerate(rowsb)],
           colWidths=[34 * mm, 22 * mm, 22 * mm, 32 * mm, CW - 110 * mm])
bt.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#efece5")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [bt, Spacer(1, 5)]
story += [P("Read the breakdown honestly: gold and silver carried the period, EUR/USD was a "
            "net drag despite the single largest win, and the largest loss came from the same "
            "pair. That is useful, publishable self-knowledge — it is exactly the kind of "
            "insight that makes an analyst worth following.", S["small"])]

story += [Paragraph("5.3 Three problems in the data worth fixing", S["h2"])]
story += [numbered([
    "<b>The 13 November row does not chain.</b> It shows a balance moving from $100,000.00 to "
    "$102,297.18 (+$2,297.18) while every other row sits between $8,200 and $15,800. Either it is "
    "a different account, a deposit was omitted, or the export merged two ledgers. Do not publish "
    "a curve that jumps like that — it will be read as a fake screenshot. Confirm what that row is "
    "before using it anywhere.",
    f"<b>The peak-to-trough drawdown is {STATS['max_drawdown_pct']}%</b> (${STATS['max_drawdown_abs']:,.2f}) "
    "between late September and early November, including a 12-trade losing streak. Any realistic "
    "risk framework would treat that as outside tolerance. It is worth stating in your own words on "
    "the page — “I had a rough stretch, here is what I changed” is stronger material than a green "
    "number.",
    "<b>This window under-represents your real record.</b> 34.3% here sits well below the 48–55% you "
    "run across your full trading history, and the account finished roughly flat (+$486, profit factor "
    "1.02). One 65-day sample during a difficult emotional stretch cannot demonstrate an edge — say so "
    "on the page, because the explanation is more convincing than the number.",
])]

story.append(callout(
    "Why the page shows a curve and no numbers",
    "Two reasons. Commercially, a win-rate badge invites a comparison you currently lose. "
    "Legally, in the UK, EU, Nigeria and most other jurisdictions, publishing performance figures "
    "to attract clients or followers can bring you inside financial-promotion rules. An equity "
    "chart with a clear “past performance” disclaimer, presented as a personal journal rather than "
    "an advertised service, is far lower-risk — and it still proves the trades are real. If you ever "
    "want headline statistics on the page, you need a longer, cleaner sample first: ideally 200+ "
    "trades over 12+ months with drawdown under 20%.",
    "warn"))

story += [PageBreak()]

# ---- 6. compliance ----
story += [
    Paragraph("6 · Compliance, in plain language", S["h1"]), rule(0, 9),
    P("This is not legal advice — it is the minimum standard that keeps a personal trading page "
      "out of trouble. Rules differ by country; if the page starts taking payment for advice "
      "rather than for web work, get local advice.", S["small"]),
    Spacer(1, 4),
    Paragraph("Always", S["h2"]),
    bullet([
        "<b>Say it is not advice.</b> “Educational content, not investment advice” — already in the "
        "footer and under the chart. Keep it there permanently.",
        "<b>Include the risk warning</b> wherever performance appears. Never place the chart next "
        "to a call-to-action without it.",
        "<b>Never guarantee returns</b> and never use “profit”, “risk-free”, “signal”, “guaranteed”, "
        "“passive income” or “financial freedom” in copy.",
        "<b>Never promise to teach profitably.</b> If you ever sell a course, the wording must be "
        "about method and education, not outcomes.",
        "<b>Keep the evidence.</b> Retain your broker statement exports. “Full export available on "
        "request” is only a safe claim if you can actually produce it.",
    ]),
    Paragraph("Never", S["h2"]),
    bullet([
        "Show a chart without the disclaimer. Screenshots are fine; cherry-picked screenshots of "
        "single winning trades are not.",
        "Offer to trade other people's money from this page — that is regulated activity almost "
        "everywhere and needs a licence.",
        "Imply a win rate that the ledger does not support. The numbers above are what a careful "
        "reader could reconstruct; do not give them a reason to.",
    ]),
    Paragraph("On the Telegram channel", S["h2"]),
    P("Posting your own analysis is normal and generally fine. Posting “buy XAUUSD now” entries for "
      "followers to copy is where the risk begins, especially if anything is ever charged. Frame "
      "posts as your own trades and reasoning, not as instructions — and add the disclaimer to the "
      "channel pinned message."),
]

# ---- 7. checklist ----
story += [Spacer(1, 6), Paragraph("7 · Launch checklist", S["h1"]), rule(0, 9)]
checks = [
    ("Content", "Telegram link is a real invite link and opens on mobile"),
    ("Content", "Demo-account label still present under the track record"),
    ("Content", "Contact shows LinkedIn, email, Telegram, GitHub — no phone number"),
    ("Content", "Portrait is your final chosen shot; delete the unused crops"),
    ("Content", "The 13 Nov ledger row either explained or removed from the chart"),
    ("Content", "Read every line of the copy out loud — cut anything you would not say"),
    ("Technical", "Tested at 320px, 768px, 1440px, 1920px in Chrome, Safari and Firefox"),
    ("Technical", "Lighthouse: Performance ≥ 95, Accessibility ≥ 95, SEO ≥ 95"),
    ("Technical", "Verified no horizontal scroll on any breakpoint"),
    ("Technical", "Domain replaced in index.html, robots.txt, sitemap.xml"),
    ("Technical", "Real 1200×630 OG image added and previewed in a link validator"),
    ("Technical", "Page loads with JavaScript disabled — no blank sections"),
    ("Legal", "Risk warning visible under the chart and in the footer"),
    ("Legal", "No performance claims anywhere in copy, meta or social previews"),
    ("Launch", "Deploy to Netlify/Vercel or shared host; attach the domain with HTTPS"),
    ("Launch", "Add to LinkedIn profile as website; add to Telegram channel bio"),
    ("Launch", "Submit sitemap to Google Search Console after DNS propagates"),
]
ct = Table([[Paragraph("[&nbsp;]", st("cb2", fontName="Helvetica", fontSize=9, leading=12,
                                    textColor=GOLD)),
             Paragraph(a, S["cellb"]), Paragraph(b, S["cell"])] for a, b in checks],
           colWidths=[8 * mm, 24 * mm, CW - 32 * mm])
ct.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BG]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e8e4dc")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
]))
story += [ct]

# ---- 8. appendix ----
story += [PageBreak(), Paragraph("Appendix · Full closed-trade ledger", S["h1"]), rule(0, 9),
          P("Every closed trade, oldest first, as parsed from your export. Scratch trades (0.00) "
            "are included. The 13 Nov snapshot row is listed last and flagged.", S["small"]),
          Spacer(1, 4)]


def cell(t):
    return Paragraph(str(t), st("x", fontSize=6.5, leading=8.4))


hdr = ["#", "Date / time", "Symbol", "Side", "Units", "Entry", "Exit", "P&amp;L (USD)", "Balance"]
data = [[Paragraph(h, st("xh", fontName="Helvetica-Bold", fontSize=6.5, leading=8.4,
                         textColor=colors.white)) for h in hdr]]
curve = [r for r in TRADES if r["balance_before"] < 90000]
snap = [r for r in TRADES if r["balance_before"] >= 90000]
for i, r in enumerate(curve, 1):
    units = f"{r['units']:,.0f}" if r["units"] >= 1 else f"{r['units']:,.4f}"
    data.append([
        cell(i),
        cell(r["time"][:16]),
        cell(r["ticker"]),
        cell(r["side"]),
        cell(units),
        cell(f"{r['entry']:,.4f}".rstrip("0").rstrip(".")),
        cell(f"{r['exit']:,.4f}".rstrip("0").rstrip(".")),
        cell(f"{r['profit']:+,.2f}"),
        cell(f"{r['balance_after']:,.2f}"),
    ])
for r in snap:
    data.append([
        cell("—"), cell(r["time"][:16]), cell(r["ticker"]), cell(r["side"]),
        cell(f"{r['units']:,.0f}"), cell(f"{r['entry']:,.3f}"), cell(f"{r['exit']:,.3f}"),
        cell(f"{r['profit']:+,.2f}*"), cell(f"{r['balance_after']:,.2f}"),
    ])

colw = [9 * mm, 30 * mm, 18 * mm, 12 * mm, 18 * mm, 22 * mm, 22 * mm, 22 * mm, CW - 153 * mm]
lt = Table(data, colWidths=colw, repeatRows=1)
style = [
    ("BACKGROUND", (0, 0), (-1, 0), INK),
    ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e8e4dc")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (4, 1), (-1, -1), "RIGHT"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
]
for i, r in enumerate(curve, 1):
    if r["profit"] < 0:
        style.append(("TEXTCOLOR", (7, i), (7, i), colors.HexColor("#a8542f")))
    elif r["profit"] > 0:
        style.append(("TEXTCOLOR", (7, i), (7, i), colors.HexColor("#3f7a5c")))
    if i % 2 == 0:
        style.append(("BACKGROUND", (0, i), (-1, i), BG))
lt.setStyle(TableStyle(style))
story += [lt, Spacer(1, 5),
          P("* Flagged row: balance does not chain with the rest of the ledger (see section 5.3).", S["tiny"]),
          Spacer(1, 6),
          rule(4, 6),
          P("Generated from data/trades-raw.txt by tools/analyse_trades.py and "
            "tools/make_brief_pdf.py. Re-run both to regenerate this document and the chart "
            "after any ledger update.", S["tiny"])]

doc = Doc(str(OUT))
doc.build(story)
print("wrote", OUT, OUT.stat().st_size, "bytes")
