#!/usr/bin/env python3
"""
sync_guides.py - Bidirectional Content, Sitemap & Calculator Freshness Sync for The Buyer's Math
1. Scans `articles/` and `guides/`, stripping any raw Markdown `# ` prefixes and extracting unique excerpts.
2. Updates `index.html` (`<!-- TBM LEAD STORY START -->` and `<!-- TBM GUIDES GRID START -->`).
3. Regenerates `guides.html`, `feed.xml` (RSS 2.0), and `sitemap.xml` (updating `<lastmod>` to today across all calculators, guides, and intel dispatches with clean canonical URLs).
4. Bidirectional Sync: Injects the 3 newest trade-matched articles directly into each of the 21 calculator HTML files (`<!-- TBM CALCULATOR TRADE GUIDES START -->`) so every calculator page updates daily with fresh internal links and editorial context.
"""

import os
import re
import email.utils
from datetime import datetime

GENERIC_BOILERPLATE = "Detailed empirical cost breakdown, licensed labor pricing, building code requirements, and contractor bid verification."

ALL_21_CALCULATORS = [
    "roofing-cost-calculator.html",
    "siding-cost-calculator.html",
    "window-replacement-estimator.html",
    "fence-cost-calculator.html",
    "driveway-paving-calculator.html",
    "deck-cost-calculator.html",
    "gutter-cost-calculator.html",
    "garage-door-calculator.html",
    "patio-cost-calculator.html",
    "exterior-painting-calculator.html",
    "hvac-roi-calculator.html",
    "mini-split-calculator.html",
    "attic-insulation-calculator.html",
    "water-heater-calculator.html",
    "solar-payback-calculator.html",
    "pool.html",
    "kitchen-remodel-calculator.html",
    "bathroom-remodel-calculator.html",
    "basement-cost-calculator.html",
    "ev-charger-calculator.html",
    "generator-calculator.html"
]

FLAGSHIP_GUIDES = [
    {
        "url": "/guides/heat-pump-tax-credit-2026.html",
        "title": "Heat Pump Tax Credit 2026: Section 25C Eligibility, Costs & Payback",
        "date": "2026-10-03",
        "description": "Section 25C $2,000 tax credit eligibility, SEER2/HSPF2 minimum efficiency tiers, dual-fuel installation costs, and multi-year utility bill ROI.",
        "category": "Mechanical & Energy",
        "filter_tag": "featured mechanical",
        "calc_url": "/hvac-roi-calculator.html",
        "calc_label": "Heat Pump Calc"
    },
    {
        "url": "/guides/roof-replacement-cost-per-square-2026.html",
        "title": "Roof Replacement Cost per Square in 2026: Architectural vs. 3-Tab",
        "date": "2026-10-03",
        "description": "Pricing per roofing square (100 sq ft), tear-off labor benchmarks, roof pitch slope multipliers, ice & water shield code rules, and quote vetting.",
        "category": "Building Envelope",
        "filter_tag": "envelope",
        "calc_url": "/roofing-cost-calculator.html",
        "calc_label": "Roofing Calc"
    },
    {
        "url": "/guides/ev-charger-tax-credit-2026.html",
        "title": "2026 EV Charger Tax Credit Guide: Section 30C Rules & Panel Upgrades",
        "date": "2026-10-05",
        "description": "How to qualify for the 30% Section 30C federal tax credit (up to $1,000) for Level 2 EV charging stations and 200A electrical service upgrades.",
        "category": "Interior & Power",
        "filter_tag": "interior",
        "calc_url": "/ev-charger-calculator.html",
        "calc_label": "EV Charger Calc"
    }
]


def clean_heading(raw_title: str) -> str:
    t = re.sub(r"\s*\|\s*The Buyer'?s Math.*$", "", raw_title, flags=re.IGNORECASE)
    t = re.sub(r"^[\s#*\"'`>]+|[\s*\"'`]+$", "", t)
    return re.sub(r"\s+", " ", t).strip()


def extract_unique_excerpt(html_content: str, fallback_title: str) -> str:
    desc_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html_content,
        re.IGNORECASE | re.DOTALL
    )
    meta_desc = desc_match.group(1).strip() if desc_match else ""
    if meta_desc and meta_desc.lower() != GENERIC_BOILERPLATE.lower():
        return re.sub(r"\s+", " ", meta_desc)

    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", html_content, flags=re.IGNORECASE | re.DOTALL)
    for p in paragraphs:
        clean_p = re.sub(r"<[^>]+>", " ", p)
        clean_p = re.sub(r"\s+", " ", clean_p).strip()
        if (
            len(clean_p) > 75
            and "affiliate disclosure" not in clean_p.lower()
            and "amazon associate" not in clean_p.lower()
            and clean_p.lower() != GENERIC_BOILERPLATE.lower()
        ):
            if len(clean_p) > 165:
                return clean_p[:162].rsplit(" ", 1)[0] + "..."
            return clean_p

    return f"Empirical 2026 cost breakdown, licensed trade labor benchmarks, and ROI analysis for {fallback_title}."


def classify_article(title: str, description: str):
    low = (title + " " + description).lower()
    if any(w in low for w in ["roof", "shingle"]):
        return ("Building Envelope", "envelope", "/roofing-cost-calculator.html", "Roofing Calc")
    if any(w in low for w in ["siding", "hardie", "vinyl siding"]):
        return ("Building Envelope", "envelope", "/siding-cost-calculator.html", "Siding Calc")
    if any(w in low for w in ["window", "glazing", "u-factor"]):
        return ("Building Envelope", "envelope", "/window-replacement-estimator.html", "Window Calc")
    if any(w in low for w in ["fence", "fencing"]):
        return ("Building Envelope", "envelope", "/fence-cost-calculator.html", "Fence Calc")
    if any(w in low for w in ["driveway", "asphalt"]):
        return ("Building Envelope", "envelope", "/driveway-paving-calculator.html", "Driveway Calc")
    if any(w in low for w in ["deck", "trex"]):
        return ("Building Envelope", "envelope", "/deck-cost-calculator.html", "Deck Calc")
    if any(w in low for w in ["gutter"]):
        return ("Building Envelope", "envelope", "/gutter-cost-calculator.html", "Gutter Calc")
    if any(w in low for w in ["garage door"]):
        return ("Building Envelope", "envelope", "/garage-door-calculator.html", "Garage Door Calc")
    if any(w in low for w in ["patio", "paver"]):
        return ("Building Envelope", "envelope", "/patio-cost-calculator.html", "Patio Calc")
    if any(w in low for w in ["paint", "painting"]):
        return ("Building Envelope", "envelope", "/exterior-painting-calculator.html", "Painting Calc")
    if any(w in low for w in ["pool", "pump"]):
        return ("Mechanical & Energy", "mechanical", "/pool.html", "Pool Pump Calc")
    if any(w in low for w in ["water heater", "tankless"]):
        return ("Mechanical & Energy", "mechanical", "/water-heater-calculator.html", "Water Heater Calc")
    if any(w in low for w in ["mini-split", "ductless"]):
        return ("Mechanical & Energy", "mechanical", "/mini-split-calculator.html", "Mini-Split Calc")
    if any(w in low for w in ["insulation", "air sealing", "r-value", "r-49"]):
        return ("Mechanical & Energy", "mechanical", "/attic-insulation-calculator.html", "Insulation Calc")
    if any(w in low for w in ["solar", "photovoltaic", "25d"]):
        return ("Mechanical & Energy", "mechanical", "/solar-payback-calculator.html", "Solar Calc")
    if any(w in low for w in ["heat pump", "furnace", "hvac", "seer2"]):
        return ("Mechanical & Energy", "mechanical", "/hvac-roi-calculator.html", "Heat Pump Calc")
    if any(w in low for w in ["generator", "standby", "transfer switch"]):
        return ("Interior & Power", "interior", "/generator-calculator.html", "Generator Calc")
    if any(w in low for w in ["ev ", "charger", "30c", "240v"]):
        return ("Interior & Power", "interior", "/ev-charger-calculator.html", "EV Charger Calc")
    if any(w in low for w in ["basement", "egress"]):
        return ("Interior & Power", "interior", "/basement-cost-calculator.html", "Basement Calc")
    if any(w in low for w in ["bathroom", "shower", "wet-room"]):
        return ("Interior & Power", "interior", "/bathroom-remodel-calculator.html", "Bathroom Calc")
    return ("Interior & Power", "interior", "/kitchen-remodel-calculator.html", "Kitchen Calc")


def get_all_articles():
    articles = list(FLAGSHIP_GUIDES)
    seen_urls = {a["url"] for a in articles}
    articles_dir = "articles"

    if os.path.exists(articles_dir):
        for fname in sorted(os.listdir(articles_dir), reverse=True):
            if not fname.endswith(".html"):
                continue
            rel_url = f"/articles/{fname}"
            if rel_url in seen_urls:
                continue
            fpath = os.path.join(articles_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            t_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
            raw_title = t_match.group(1) if t_match else fname.replace(".html", "")
            title = clean_heading(raw_title)

            d_match = re.match(r"^(\d{4}-\d{2}-\d{2})", fname)
            if not d_match:
                d_match = re.search(r"Published on (\d{4}-\d{2}-\d{2})", content)
            date_str = d_match.group(1) if d_match else datetime.now().strftime("%Y-%m-%d")

            description = extract_unique_excerpt(content, title)
            category, filter_tag, calc_url, calc_label = classify_article(title, description)

            articles.append({
                "url": rel_url,
                "title": title,
                "date": date_str,
                "description": description,
                "category": category,
                "filter_tag": filter_tag,
                "calc_url": calc_url,
                "calc_label": calc_label
            })
            seen_urls.add(rel_url)

    articles.sort(key=lambda x: x["date"], reverse=True)
    for idx, art in enumerate(articles):
        if idx < 12 and "featured" not in art["filter_tag"]:
            art["filter_tag"] = "featured " + art["filter_tag"]
    return articles


def update_index_editorial(articles):
    if not os.path.exists("index.html") or not articles:
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    lead = articles[0]
    recent_four = articles[1:5]

    recent_items_html = []
    for r in recent_four:
        recent_items_html.append(f"""            <li class="recent-dispatch-item">
              <div>
                <div class="lead-meta-row" style="margin-bottom: 0.25rem;">
                  <span class="badge-cat">{r['category']}</span>
                  <span class="meta-date">{r['date']}</span>
                </div>
                <h3 class="recent-dispatch-title">
                  <a href="{r['url']}">{r['title']}</a>
                </h3>
                <p class="recent-dispatch-snippet">{r['description']}</p>
              </div>
              <a href="{r['calc_url']}" class="recent-calc-pill">{r['calc_label']} &rarr;</a>
            </li>""")

    lead_block_html = f"""<!-- TBM LEAD STORY START -->
    <section class="editorial-hero-grid" aria-label="Featured Daily Research and Quick Calculator Launcher">
      <div>
        <article class="lead-story-card">
          <div class="lead-meta-row">
            <span class="badge-lead">Today's Lead Cost Analysis</span>
            <span class="badge-cat">{lead['category']}</span>
            <span class="meta-date">Published {lead['date']} &bull; Empirical Cost Audit</span>
          </div>
          <h1 class="lead-title">
            <a href="{lead['url']}">{lead['title']}</a>
          </h1>
          <p class="lead-excerpt">{lead['description']}</p>
          <div class="lead-actions">
            <a href="{lead['url']}" class="btn-primary">Read Today's Full Guide &rarr;</a>
            <a href="{lead['calc_url']}" class="btn-secondary">Open {lead['calc_label']} &rarr;</a>
          </div>
        </article>

        <div class="recent-dispatches-box">
          <div class="recent-box-header">
            <h2>Recent Daily Cost Breakdowns</h2>
            <a href="#guides-section" style="font-size: 0.82rem; font-weight: 700; color: var(--primary);">Browse All {len(articles)} Guides &darr;</a>
          </div>
          <ul class="recent-dispatch-list">
{chr(10).join(recent_items_html)}
          </ul>
        </div>
      </div>
      <!-- TBM LEAD STORY END -->"""

    if "<!-- TBM LEAD STORY START -->" in content and "<!-- TBM LEAD STORY END -->" in content:
        content = re.sub(
            r"<!-- TBM LEAD STORY START -->.*?<!-- TBM LEAD STORY END -->",
            lead_block_html,
            content,
            flags=re.DOTALL
        )

    grid_cards_html = []
    for a in articles:
        grid_cards_html.append(f"""        <a href="{a['url']}" class="guide-card" data-guide-category="{a['filter_tag']}">
          <div>
            <div class="card-meta-top">
              <span class="badge-category">{a['category']}</span>
              <span class="card-date">{a['date']}</span>
            </div>
            <h3>{a['title']}</h3>
            <p>{a['description']}</p>
          </div>
          <span class="cta-link">Read Guide &rarr;</span>
        </a>""")

    grid_block_html = (
        "<!-- TBM GUIDES GRID START -->\n"
        '      <div class="cards-grid" id="guideGrid">\n\n'
        + "\n\n".join(grid_cards_html)
        + "\n\n      </div>\n      <!-- TBM GUIDES GRID END -->"
    )

    if "<!-- TBM GUIDES GRID START -->" in content and "<!-- TBM GUIDES GRID END -->" in content:
        content = re.sub(
            r"<!-- TBM GUIDES GRID START -->.*?<!-- TBM GUIDES GRID END -->",
            grid_block_html,
            content,
            flags=re.DOTALL
        )

    content = re.sub(
        r'(<button[^>]*data-guide-filter="all"[^>]*>)All \d+ Guides(</button>)',
        rf"\g<1>All {len(articles)} Guides\g<2>",
        content
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated index.html with Lead Story ({lead['date']}) and {len(articles)} guide cards.")


def inject_trade_guides_into_calculators(articles):
    """Bidirectional sync: injects the 3 newest trade-matched articles into each of the 21 calculator HTML files."""
    if not articles:
        return
    updated_calcs = 0
    for calc_file in ALL_21_CALCULATORS:
        if not os.path.exists(calc_file):
            continue
        calc_rel = "/" + calc_file
        matched = [a for a in articles if a["calc_url"] == calc_rel]
        if len(matched) < 3:
            # Fill remaining slots with newest articles in the same category or overall newest
            seen = {a["url"] for a in matched}
            for a in articles:
                if a["url"] not in seen:
                    matched.append(a)
                    seen.add(a["url"])
                if len(matched) >= 3:
                    break
        top_three = matched[:3]

        cards_html = []
        for a in top_three:
            cards_html.append(f"""        <a href="{a['url']}" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; text-decoration: none; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <span style="font-size: 0.7rem; font-weight: 700; color: #2563eb; background: #eff6ff; padding: 0.2rem 0.5rem; border-radius: 4px; text-transform: uppercase;">{a['category']}</span>
              <span style="font-size: 0.75rem; color: #94a3b8;">{a['date']}</span>
            </div>
            <h4 style="margin: 0 0 0.45rem 0; font-size: 1.02rem; color: #0f172a; line-height: 1.38;">{a['title']}</h4>
            <p style="margin: 0 0 0.85rem 0; font-size: 0.84rem; color: #475569; line-height: 1.5;">{a['description']}</p>
          </div>
          <span style="font-size: 0.84rem; font-weight: 700; color: #2563eb;">Read Cost Breakdown &rarr;</span>
        </a>""")

        block_html = f"""<!-- TBM CALCULATOR TRADE GUIDES START -->
    <section class="tbm-calc-latest-guides" style="margin-top: 2.75rem; padding-top: 2.25rem; border-top: 1px solid #e2e8f0;">
      <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1.25rem;">
        <div>
          <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb;">Daily Research Sync</span>
          <h3 style="margin: 0.2rem 0 0 0; font-size: 1.35rem; color: #0f172a;">Latest 2026 Cost Audits &amp; Code Briefs for This Trade</h3>
        </div>
        <a href="/guides.html" style="font-size: 0.88rem; font-weight: 700; color: #2563eb; text-decoration: none;">Browse All Guides &rarr;</a>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.15rem;">
{chr(10).join(cards_html)}
      </div>
    </section>
    <!-- TBM CALCULATOR TRADE GUIDES END -->"""

        with open(calc_file, "r", encoding="utf-8") as f:
            c_html = f.read()
        orig = c_html

        if "<!-- TBM CALCULATOR TRADE GUIDES START -->" in c_html:
            c_html = re.sub(
                r"<!-- TBM CALCULATOR TRADE GUIDES START -->.*?<!-- TBM CALCULATOR TRADE GUIDES END -->",
                block_html,
                c_html,
                flags=re.DOTALL
            )
        elif "</main>" in c_html:
            c_html = c_html.replace("</main>", block_html + "\n\n  </main>", 1)

        if c_html != orig:
            with open(calc_file, "w", encoding="utf-8") as f:
                f.write(c_html)
            updated_calcs += 1

    print(f"Injected latest trade-matched guides into {updated_calcs} calculator page(s).")


def generate_sitemap_xml(articles):
    today_str = datetime.now().strftime("%Y-%m-%d")
    urls = [
        ("https://thebuyersmath.com/", today_str, "daily", "1.0"),
        ("https://thebuyersmath.com/guides.html", today_str, "daily", "0.9"),
        ("https://thebuyersmath.com/intel/index.html", today_str, "daily", "0.9"),
        ("https://thebuyersmath.com/about.html", today_str, "monthly", "0.6"),
        ("https://thebuyersmath.com/privacy-policy.html", "2026-10-09", "monthly", "0.3"),
        ("https://thebuyersmath.com/terms.html", "2026-10-09", "monthly", "0.3"),
        ("https://thebuyersmath.com/contact.html", "2026-10-09", "monthly", "0.4"),
    ]
    for c in ALL_21_CALCULATORS:
        urls.append((f"https://thebuyersmath.com/{c}", today_str, "daily", "0.9"))

    if os.path.exists("intel"):
        for fname in sorted(os.listdir("intel"), reverse=True):
            if fname.endswith("-daily-market-intelligence.html"):
                urls.append((f"https://thebuyersmath.com/intel/{fname}", fname[:10], "daily", "0.8"))

    for a in articles:
        urls.append((f"https://thebuyersmath.com{a['url']}", a["date"], "monthly", "0.8"))

    xml_items = []
    seen = set()
    for loc, lastmod, freq, prio in urls:
        if loc in seen:
            continue
        seen.add(loc)
        xml_items.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        )

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(xml_items) + "\n</urlset>\n"
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"Generated clean sitemap.xml with {len(xml_items)} canonical URLs.")


def generate_rss_feed(articles):
    items_xml = []
    for a in articles[:25]:
        try:
            dt = datetime.strptime(a["date"], "%Y-%m-%d")
        except Exception:
            dt = datetime.now()
        rfc_date = email.utils.format_datetime(dt)
        full_url = "https://thebuyersmath.com" + a["url"]
        items_xml.append(
            f"    <item>\n"
            f"      <title><![CDATA[{a['title']}]]></title>\n"
            f"      <link>{full_url}</link>\n"
            f"      <guid isPermaLink=\"true\">{full_url}</guid>\n"
            f"      <pubDate>{rfc_date}</pubDate>\n"
            f"      <description><![CDATA[{a['description']}]]></description>\n"
            f"      <category><![CDATA[{a['category']}]]></category>\n"
            f"    </item>"
        )
    now_rfc = email.utils.format_datetime(datetime.now())
    feed_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        "    <title>The Buyer's Math | Empirical Home Improvement Cost Guides</title>\n"
        "    <link>https://thebuyersmath.com/</link>\n"
        "    <description>Independent, data-driven financial modeling and cost estimators for homeowners.</description>\n"
        "    <language>en-us</language>\n"
        '    <atom:link href="https://thebuyersmath.com/feed.xml" rel="self" type="application/rss+xml" />\n'
        f"    <lastBuildDate>{now_rfc}</lastBuildDate>\n"
        + "\n".join(items_xml)
        + "\n  </channel>\n</rss>\n"
    )
    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(feed_xml)
    print("Generated feed.xml (RSS 2.0) successfully.")


if __name__ == "__main__":
    all_articles = get_all_articles()
    update_index_editorial(all_articles)
    inject_trade_guides_into_calculators(all_articles)
    generate_sitemap_xml(all_articles)
    generate_rss_feed(all_articles)
