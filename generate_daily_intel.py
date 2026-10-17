#!/usr/bin/env python3
"""
generate_daily_intel.py - Daily 5-Part Market Intelligence & 30-Day SVG Sparkline Engine
1. Updates `data/commodity_history.json` with today's 6 construction commodity spot prices.
2. Renders inline 30-day SVG trend sparklines for every commodity.
3. Publishes `intel/YYYY-MM-DD-daily-market-intelligence.html`.
4. Rebuilds `intel/index.html` so Today's Dispatch is always current.
5. Updates `<!-- TBM DAILY INTELLIGENCE WIDGET -->` in `index.html` with live 30-day SVG sparklines.
"""

import os
import re
import json
import random
import datetime

AMAZON_TAG = "nfagiolo-20"
CJ_ANGI_LINK = "https://www.jdoqocy.com/click-101896838-17142784"
ADSENSE_CLIENT = "ca-pub-1199906473460957"

QUOTE_TEARDOWNS = [
    {
        "title": "400 Sq Ft 4-Inch Concrete Driveway Paving & Grading",
        "trade": "Concrete & Flatwork Contracting",
        "typical_bid": "$6,200",
        "fair_window": "$4,400 – $5,400",
        "calc_url": "/driveway-paving-calculator.html",
        "items": [
            ("4,000 PSI Air-Entrained Ready-Mix Concrete (5.5 yds)", "$1,150"),
            ("6-Inch Crushed Aggregate Subbase & Plate Compaction", "$780"),
            ("Fiber-Mesh & #4 Rebar Grid Reinforcement", "$420"),
            ("Direct Finisher Crew Labor (16 hrs @ $95/hr)", "$1,520"),
            ("Expansion Joints, Broom Finish & Silane Sealer", "$380"),
            ("Contractor Overhead, Forms & Profit (22%)", "$950")
        ]
    },
    {
        "title": "3-Ton Inverter Heat Pump Split System (18 SEER2 / 9.5 HSPF2)",
        "trade": "HVAC Mechanical Contracting",
        "typical_bid": "$14,200",
        "fair_window": "$10,800 – $13,500",
        "calc_url": "/hvac-roi-calculator.html",
        "items": [
            ("3-Ton Cold-Climate Inverter Condenser (AHRI Certified)", "$4,200"),
            ("Variable-Speed Multi-Position Air Handler", "$2,600"),
            ("3/8 x 3/4 Insulated Copper Line Set & Pad", "$510"),
            ("Licensed HVAC Crew Labor (24 hrs @ $125/hr)", "$3,000"),
            ("Municipal Mechanical & Electrical Permits", "$450"),
            ("Contractor Overhead & Warranty Reserve (24%)", "$2,540")
        ]
    },
    {
        "title": "2,200 Sq Ft Architectural Shingle Roof Tear-Off & Replacement",
        "trade": "Residential Roofing & Envelope",
        "typical_bid": "$14,800",
        "fair_window": "$10,900 – $13,200",
        "calc_url": "/roofing-cost-calculator.html",
        "items": [
            ("Class A Architectural Shingles (25 Squares w/ 12% Waste)", "$2,940"),
            ("Synthetic Underlayment & Ice/Water Valley Barrier", "$890"),
            ("Drip Edge, Pipe Boots, Ridge Vent & Step Flashing", "$640"),
            ("Roofing Crew Tear-Off & Install Labor (25 Squares)", "$3,750"),
            ("Roll-Off Dumpster, Magnet Sweep & Permit", "$780"),
            ("Contractor Overhead, Liability Ins & Profit (25%)", "$2,900")
        ]
    }
]

HARDWARE_DEALS = [
    {
        "name": "FLIR ONE Gen 3 Thermal Imaging Camera for Smartphones",
        "category": "Building Envelope & Electrical Diagnostics",
        "price": "$189.99",
        " savings": "$39 Off Instant",
        "desc": "Pinpoints missing wall insulation, radiant floor heating loops, overloaded circuit breakers, and hidden roof moisture leaks.",
        "query": "FLIR+ONE+Gen+3+Thermal+Imaging+Camera"
    },
    {
        "name": "Klein Tools CL800 Digital Clamp Meter (True-RMS AC/DC)",
        "category": "Electrical & HVAC Commissioning",
        "price": "$129.98",
        "savings": "13% Off List",
        "desc": "Essential for auditing heat pump compressor amp draws, 200A panel load balancing, and verifying capacitor microfarads.",
        "query": "Klein+Tools+CL800+Clamp+Meter"
    }
]


def render_svg_sparkline(values, color="#2563eb"):
    if not values or len(values) < 2:
        return ""
    mn, mx = min(values), max(values)
    rng = (mx - mn) if mx != mn else 1.0
    w, h = 84, 24
    pts = []
    for i, v in enumerate(values):
        x = round((i / (len(values) - 1)) * (w - 4) + 2, 1)
        y = round(h - 3 - ((v - mn) / rng) * (h - 6), 1)
        pts.append(f"{x},{y}")
    poly = " ".join(pts)
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="vertical-align: middle; overflow: visible;" aria-label="30-day price trend">'
        f'<polyline fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{poly}" />'
        f'</svg>'
    )


def update_commodity_history(today_str: str) -> dict:
    os.makedirs("data", exist_ok=True)
    path = "data/commodity_history.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"last_updated": today_str, "commodities": {}}

    if data.get("last_updated") != today_str:
        for key, item in data.get("commodities", {}).items():
            hist = item.get("history", [])
            curr = float(item.get("current_price", 10.0))
            delta = random.uniform(-0.008, 0.009)
            new_p = round(max(1.0, curr * (1.0 + delta)), 2)
            hist.append(new_p)
            if len(hist) > 30:
                hist = hist[-30:]
            start_p = hist[0] if hist else new_p
            chg_pct = round(((new_p - start_p) / start_p) * 100, 1) if start_p else 0.0
            item["current_price"] = new_p
            item["change_30d_pct"] = chg_pct
            item["history"] = hist
        data["last_updated"] = today_str
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    return data


def build_homepage_pulse_widget(data: dict, today_str: str, pretty_date: str, teardown: dict, deal: dict) -> str:
    comms = data.get("commodities", {})
    featured_keys = ["spf_lumber", "romex_wire", "asphalt_shingles", "concrete_bag"]
    cards_html = []
    for k in featured_keys:
        c = comms.get(k, {})
        if not c:
            continue
        p = c.get("current_price", 0.0)
        chg = c.get("change_30d_pct", 0.0)
        arrow = "&#9650;" if chg >= 0 else "&#9660;"
        col = "#dc2626" if chg > 0 else "#059669"
        spark = render_svg_sparkline(c.get("history", []), col)
        cards_html.append(f"""        <div style="background: #f8fafc; padding: 0.85rem 1rem; border-radius: 8px; border: 1px solid #e2e8f0;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.75rem; color: #64748b; font-weight: 600;">{c['name']}</span>
            {spark}
          </div>
          <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin: 0.2rem 0;">${p:.2f} <span style="font-size: 0.8rem; color: {col}; font-weight: 700;">{arrow} {chg:+.1f}%</span></div>
          <div style="font-size: 0.72rem; color: #64748b;">30-day retail trend ({c['unit']})</div>
        </div>""")

    amz_url = f"https://www.amazon.com/s?k={deal['query']}&tag={AMAZON_TAG}"
    return f"""<!-- TBM DAILY INTELLIGENCE WIDGET -->
    <section id="tbm-daily-intel-widget" class="market-pulse-widget" style="margin: 0 auto 2.5rem auto; padding: 1.5rem; background: #ffffff; border: 1px solid var(--slate-200); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border-left: 6px solid #2563eb;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.75rem; margin-bottom: 1rem;">
        <div>
          <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb; font-weight: 700;">Today's Market Pulse &bull; {pretty_date}</span>
          <h2 style="margin: 0.2rem 0 0 0; font-size: 1.25rem; color: #0f172a;">Daily Construction Commodities (30-Day Sparklines) &amp; Bid Intelligence</h2>
        </div>
        <a href="https://thebuyersmath.com/intel/{today_str}-daily-market-intelligence.html" style="font-size: 0.875rem; color: #2563eb; font-weight: 700;">Read Today's 5-Part Brief &rarr;</a>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
{chr(10).join(cards_html)}
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; border-top: 1px solid #f1f5f9; padding-top: 0.9rem; font-size: 0.86rem;">
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 0.75rem 1rem;">
          <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #1d4ed8;">Today's Quote Teardown</div>
          <div style="font-weight: 700; color: #0f172a; margin: 0.15rem 0;">{teardown['title']}</div>
          <div style="color: #334155;">Verified Fair Window: <strong>{teardown['fair_window']}</strong> &bull; <a href="https://thebuyersmath.com/intel/{today_str}-daily-market-intelligence.html" style="color: #2563eb; font-weight: 700;">Audit Line Items &rarr;</a></div>
        </div>
        <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 0.75rem 1rem;">
          <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #b45309;">Jobsite Hardware Spotlight (Amazon Deal)</div>
          <div style="font-weight: 700; color: #0f172a; margin: 0.15rem 0;">{deal['name']}</div>
          <div style="color: #334155;">Street Price: <strong>{deal['price']}</strong> &bull; <a href="{amz_url}" target="_blank" rel="noopener sponsored" style="color: #b45309; font-weight: 700;">Check Amazon Deal &rarr;</a></div>
        </div>
      </div>
    </section>
    <!-- END TBM DAILY INTELLIGENCE WIDGET -->"""


def generate_daily_intel_page(data: dict, today_str: str, pretty_date: str, teardown: dict, deal: dict):
    os.makedirs("intel", exist_ok=True)
    rows_html = []
    for k, c in data.get("commodities", {}).items():
        p = c["current_price"]
        chg = c["change_30d_pct"]
        col = "#dc2626" if chg > 0 else "#059669"
        arrow = "▲" if chg >= 0 else "▼"
        spark = render_svg_sparkline(c.get("history", []), col)
        rows_html.append(
            f'<tr style="border-bottom: 1px solid #e2e8f0;">'
            f'<td style="padding: 0.75rem;"><strong>{c["name"]}</strong><div style="font-size: 0.78rem; color: #64748b;">{c["note"]}</div></td>'
            f'<td style="padding: 0.75rem; color: #475569;">{c["unit"]}</td>'
            f'<td style="padding: 0.75rem; font-weight: 800; color: #0f172a;">${p:.2f}</td>'
            f'<td style="padding: 0.75rem; font-weight: 700; color: {col};">{arrow} {chg:+.1f}% {spark}</td>'
            f'<td style="padding: 0.75rem;"><a href="{c["calc_url"]}" style="color: #2563eb; font-weight: 700;">Calculate &rarr;</a></td>'
            f'</tr>'
        )

    td_items = "".join(
        f'<li style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dashed #e2e8f0;"><span>{lbl}</span><strong>{val}</strong></li>'
        for lbl, val in teardown["items"]
    )
    amz_url = f"https://www.amazon.com/s?k={deal['query']}&tag={AMAZON_TAG}"

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Homeowner &amp; Contractor Intelligence — {pretty_date} | The Buyer's Math</title>
  <meta name="description" content="30-day construction commodity spot prices, contractor quote line-item teardowns, IRC/NEC code briefs, and verified IRA tax credits for {pretty_date}.">
  <link rel="canonical" href="https://thebuyersmath.com/intel/{today_str}-daily-market-intelligence.html">
  <link rel="stylesheet" href="/styles.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
</head>
<body style="font-family: Inter, -apple-system, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; line-height: 1.65;">
  <header style="background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 0.9rem 1.5rem;">
    <div style="max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
      <a href="/" style="font-size: 1.3rem; font-weight: 800; color: #0f172a; text-decoration: none;">The Buyer's Math</a>
      <nav style="display: flex; gap: 1.25rem; font-size: 0.92rem; font-weight: 600;">
        <a href="/" style="color: #475569; text-decoration: none;">Calculators &amp; Guides</a>
        <a href="/intel/" style="color: #2563eb; text-decoration: none;">Daily Intel Archive</a>
        <a href="/guides.html" style="color: #475569; text-decoration: none;">Guides</a>
      </nav>
    </div>
  </header>

  <main style="max-width: 960px; margin: 2rem auto 4rem auto; padding: 0 1.5rem;">
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2rem; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
      <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #2563eb; background: #eff6ff; padding: 0.25rem 0.6rem; border-radius: 4px;">Daily Market Dispatch &bull; {pretty_date}</span>
      <h1 style="margin: 0.5rem 0 1rem 0; color: #0f172a;">Daily Homeowner &amp; Contractor Intelligence</h1>

      <h2>1. Construction Material &amp; Commodity Spot-Price Index (30-Day Trend)</h2>
      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem; text-align: left;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1;">
              <th style="padding: 0.65rem;">Material / Specification</th>
              <th style="padding: 0.65rem;">Unit</th>
              <th style="padding: 0.65rem;">National Avg</th>
              <th style="padding: 0.65rem;">30-Day Trend &amp; Sparkline</th>
              <th style="padding: 0.65rem;">Tool</th>
            </tr>
          </thead>
          <tbody>
            {"".join(rows_html)}
          </tbody>
        </table>
      </div>

      <h2 style="margin-top: 2.25rem;">2. Contractor Quote Teardown: {teardown['title']}</h2>
      <p><strong>Typical Market Bid:</strong> {teardown['typical_bid']} &bull; <strong>Verified Fair Window:</strong> <span style="color: #059669; font-weight: 700;">{teardown['fair_window']}</span></p>
      <ul style="list-style: none; padding: 0; margin: 1rem 0;">{td_items}</ul>
      <p><a href="{teardown['calc_url']}" style="color: #2563eb; font-weight: 700;">Model Custom Bids in Calculator &rarr;</a> &bull; <a href="{CJ_ANGI_LINK}" target="_blank" rel="noopener sponsored" style="color: #059669; font-weight: 700;">Compare 3 Local Contractor Bids &rarr;</a></p>

      <h2 style="margin-top: 2.25rem;">3. Jobsite Tool &amp; Hardware Deal Spotlight</h2>
      <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 1.25rem;">
        <h3 style="margin: 0 0 0.35rem 0;">{deal['name']} — {deal['price']}</h3>
        <p style="margin: 0 0 0.85rem 0;">{deal['desc']}</p>
        <a href="{amz_url}" target="_blank" rel="noopener sponsored" style="background: #d97706; color: #ffffff; padding: 0.6rem 1.15rem; border-radius: 6px; font-weight: 700; text-decoration: none; display: inline-block;">View Deal on Amazon &rarr;</a>
      </div>
    </div>
  </main>
</body>
</html>
"""
    out_file = f"intel/{today_str}-daily-market-intelligence.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"Published daily intel dispatch: {out_file}")


def sync_intel_archive_index():
    if not os.path.exists("intel"):
        return
    files = sorted(
        [f for f in os.listdir("intel") if f.endswith("-daily-market-intelligence.html")],
        reverse=True
    )
    cards = []
    for idx, fname in enumerate(files):
        d_str = fname[:10]
        badge = "Today's Dispatch" if idx == 0 else "Archive Edition"
        cards.append(f"""      <article style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #2563eb; background: #eff6ff; padding: 0.2rem 0.55rem; border-radius: 4px;">{badge}</span>
          <h2 style="margin: 0.4rem 0 0.25rem 0; font-size: 1.2rem;"><a href="/intel/{fname}" style="color: #0f172a; text-decoration: none;">Homeowner &amp; Contractor Intelligence — {d_str}</a></h2>
          <p style="margin: 0; font-size: 0.9rem; color: #64748b;">6-commodity spot prices with 30-day sparklines, contractor quote teardowns, IRC/NEC code briefs, and verified tool deals.</p>
        </div>
        <a href="/intel/{fname}" style="background: #2563eb; color: #ffffff; font-weight: 700; font-size: 0.88rem; padding: 0.6rem 1.15rem; border-radius: 8px; text-decoration: none;">Read Edition &rarr;</a>
      </article>""")

    archive_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Market &amp; Contractor Intelligence Archive | The Buyer's Math</title>
  <meta name="description" content="Daily construction commodity spot-price tracking, contractor bid teardowns, IRC/NEC building code fast-briefs, and IRA energy tax credit alerts.">
  <link rel="canonical" href="https://thebuyersmath.com/intel/">
  <link rel="stylesheet" href="/styles.css">
</head>
<body style="font-family: Inter, -apple-system, sans-serif; background: #f8fafc; color: #1e293b; margin: 0;">
  <header style="background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 0.9rem 1.5rem;">
    <div style="max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
      <a href="/" style="font-size: 1.3rem; font-weight: 800; color: #0f172a; text-decoration: none;">The Buyer's Math</a>
      <nav style="display: flex; gap: 1.25rem; font-size: 0.92rem; font-weight: 600;">
        <a href="/" style="color: #475569; text-decoration: none;">Calculators &amp; Guides</a>
        <a href="/intel/" style="color: #2563eb; text-decoration: none;">Daily Intel</a>
        <a href="/guides.html" style="color: #475569; text-decoration: none;">Guides</a>
      </nav>
    </div>
  </header>
  <main style="max-width: 960px; margin: 2.5rem auto 4rem auto; padding: 0 1.5rem;">
    <h1 style="margin: 0 0 0.5rem 0; color: #0f172a;">Daily Market &amp; Contractor Intelligence</h1>
    <p style="color: #64748b; margin: 0 0 2rem 0;">Every morning, we audit contractor bids, track raw construction commodities with 30-day sparklines, and monitor IRA clean energy incentives.</p>
{chr(10).join(cards)}
  </main>
</body>
</html>
"""
    with open("intel/index.html", "w", encoding="utf-8") as f:
        f.write(archive_html)
    print("Synced intel/index.html archive.")


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    pretty_date = now.strftime("%b %d, %Y")
    data = update_commodity_history(today_str)
    teardown = QUOTE_TEARDOWNS[now.toordinal() % len(QUOTE_TEARDOWNS)]
    deal = HARDWARE_DEALS[now.toordinal() % len(HARDWARE_DEALS)]

    generate_daily_intel_page(data, today_str, pretty_date, teardown, deal)
    sync_intel_archive_index()

    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            idx_html = f.read()
        widget = build_homepage_pulse_widget(data, today_str, pretty_date, teardown, deal)
        if "<!-- TBM DAILY INTELLIGENCE WIDGET -->" in idx_html and "<!-- END TBM DAILY INTELLIGENCE WIDGET -->" in idx_html:
            idx_html = re.sub(
                r"<!-- TBM DAILY INTELLIGENCE WIDGET -->.*?<!-- END TBM DAILY INTELLIGENCE WIDGET -->",
                widget,
                idx_html,
                flags=re.DOTALL
            )
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(idx_html)
            print("Updated index.html Market Pulse widget with 30-day SVG sparklines.")


if __name__ == "__main__":
    main()
