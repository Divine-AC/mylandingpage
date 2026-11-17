# Divine Abba — personal landing page

A one-page site for **Divine Abba**, trader & market analyst (gold, FX, oil, crypto), with a
secondary offer: web development builds for traders and small businesses.

Built as plain HTML + CSS + JS: **no framework, no build step, no dependencies.** Open
`index.html` and it works, which means it deploys anywhere.

---

## What's in here

| Path | What it is |
|---|---|
| `index.html` | The landing page — all markup and copy |
| `styles.css` | All styling (one file, one request) |
| `main.js` | Contact-link wiring, hero ticker, scroll reveal, year |
| `config.js` | **The only file you edit** — Telegram, email, WhatsApp, LinkedIn |
| `assets/divine-hero.jpg` | Portrait, 600×960 |
| `assets/equity-curve.svg` | Generated equity-curve chart (~5 KB, sharp on retina) |
| `assets/favicon.svg` | "DA" monogram favicon |

### Sections (in order)

Hero (trader · engineer · builder) → **About: three disciplines + full CV timeline** →
Markets & Method → **Track record (demo account)** → Telegram → **Selected work (4 live apps +
4 more repos)** → Build with me → LinkedIn band → Contact.
On mobile there is a hamburger menu and a sticky "Daily trades / Hire me" bar at the bottom.

### ⚠️ The track record is a DEMO account

The equity curve is from a **demo account**, not live capital — the page says so in the heading,
the sub-headline, the chart caption, three explanatory notes and the footer. **Do not remove
those labels.** The page also states that the win rate across the full trading record is
**48–55%**, and that this 99-trade window (34.3%, ~flat) came in below that during a difficult
emotional stretch. That framing is deliberate: honest, and defensible if anyone challenges it.

### The Selected work section

Each project card shows a live iframe of the deployed site inside a browser frame, with a styled
fallback panel behind it. If a host ever blocks embedding (`X-Frame-Options` / CSP), the fallback
remains visible and the "Visit live site" link still works — so the section can never look broken.
Projects: `propfirmintelligenence.vercel.app`, `divine-banking-web-app.vercel.app`,
`group-6-capstone-project-two.vercel.app`, plus a "you are here" card for this site.
Below them, a smaller grid links BlockLedger, the Jumia-style backend, `reset-css` and the
full GitHub profile.
| `data/trades-raw.txt` | The broker ledger export, one line per trade |
| `data/trades.json` | Parsed + verified trades (generated) |
| `data/stats.json` | Computed statistics (generated) |
| `tools/analyse_trades.py` | Parses the ledger, verifies every row, writes the JSON |
| `tools/make_chart.py` | Regenerates `assets/equity-curve.svg` from the data |
| `tools/make_brief_pdf.py` | Regenerates the 14-page brief PDF |
| `docs/Divine-Abba-Landing-Page-Brief.pdf` | **The deliverable brief** — strategy, full copy deck, design system, technical spec, ledger audit, compliance wording, launch checklist, full trade table |

---

## Contact details — all wiring is done

`config.js` is already set to your real details:

```js
window.SITE = {
  telegram: "https://t.me/adcrim",
  email: "divineabbachimdirim1@gmail.com",
  linkedin: "https://linkedin.com/in/divine-abba-883540311",
  ticker: [...]
}
```

WhatsApp has been removed from the page entirely. Change any of the three links above and the
nav, hero, Telegram band, LinkedIn band, contact cards, sticky mobile bar and footer all update
at once — the markup never needs editing.

**Only remaining task:** if you attach a real domain, replace `mylandingpage-taupe.vercel.app` with it in
**`index.html`** (canonical, OG, JSON-LD), **`robots.txt`** and **`sitemap.xml`**. On the free
`*.vercel.app` URL nothing needs changing.

---

## Run it locally

```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

## Deploy it (free options)

- **Netlify / Vercel** — drag the folder onto the dashboard, or connect the repo. No build command, publish directory `/`.
- **GitHub Pages** — Settings → Pages → deploy from branch, root.
- **Any shared host** — upload everything except `tools/`, `data/` and `docs/` to `public_html`.

Set the domain's DNS, enable HTTPS (automatic on Netlify/Vercel), done.

---

## Updating the track record

The chart is generated from the ledger — never hand-edit the SVG.

1. Append new closed trades to `data/trades-raw.txt`, one per line, in this exact pipe format:

   ```
   2026-11-20 14:05:11 | 13,680.48 | 13,951.02 | +270.54 | Close long position for symbol OANDA:XAUUSD at price 4102.150 for 12 units. Position AVG Price was 4079.560000, currency: USD, rate: 1.000000, point value: 1.000000
   ```

   (`date | balance before | balance after | profit | broker description` — paste the broker's row order; the script sorts by time.)

2. Regenerate:

   ```bash
   pip install --break-system-packages reportlab
   python3 tools/analyse_trades.py      # verifies + recomputes stats
   python3 tools/make_chart.py          # rewrites assets/equity-curve.svg
   python3 tools/make_brief_pdf.py      # rewrites the PDF brief
   ```

The analyser **asserts** that every row's profit equals `balance_after − balance_before` and
`(exit − entry) × units × direction`. If a row doesn't reconcile, it stops with an error rather
than quietly producing a wrong chart.

> ⚠️ **Known data issue:** the `2026-11-13 20:30:17` row shows a balance jump from `100,000.00`
> to `102,297.18` while every other row sits between ~8,200 and ~15,800. It does not chain with
> the rest of the ledger, so it is **excluded from the chart** and flagged in the PDF. Work out
> what that row is (separate account? omitted deposit?) before publishing it anywhere.

---

## Design system in one paragraph

Near-black background (`#0B0C0F`) with a single gold accent (`#D8B25F`); a system font stack so
there are zero font requests; type set tight (negative tracking on headings); one photograph, no
stock imagery; motion is a single 18px fade-up on scroll, disabled under `prefers-reduced-motion`.
Green/red are reserved exclusively for data and never used as UI colour.

---

## Performance & accessibility

- 4 network requests, no third-party scripts, ~200 KB total.
- Explicit `width`/`height` on images → CLS 0.
- Contrast: body copy ≈ 11:1, muted text ≈ 5.4:1 (both pass WCAG AA).
- Skip link, single `<h1>`, labelled sections, visible focus rings, descriptive chart `alt`.
- Fully readable with JavaScript disabled.

---

## Compliance note (read the PDF, section 6)

The page deliberately shows an **equity curve and no headline performance statistics** —
no win rate, no "profit" claims, no guarantees. That's both a credibility choice and a
regulatory one. Keep the risk warning in the footer and under the chart, and never use the
words "guaranteed", "risk-free", "passive income" or "financial freedom" anywhere on the site
or in the Telegram channel's pinned message.
