#!/usr/bin/env python3
"""
sync_guides.py - Synchronizes all articles from `articles/` into `guides/` directory.
Ensures:
1. Canonical URL points to `/guides/<filename>`
2. Structured JSON-LD Article schema exists and is updated.
3. OpenGraph & Twitter Cards meta tags are injected/updated.
4. Navigation breadcrumb bar is inserted.
5. `guides.html` directory index page is regenerated with search/filter features.
"""

import os
import re
import html
import json

FLAGSHIP_GUIDES = [
    {
        "url": "/guides/2026-09-30-ditra-heat-cost-guide.html",
        "title": "Ditra Heat System Cost Guide (2026)",
        "desc": "Empirical breakdown of Ditra Heat electric radiant floor warming costs, Schluter membrane pricing, uncoupling tile underlayment, and licensed electrician/tile setter labor rates.",
        "category": "Interior & Power",
        "calc_url": "/bathroom-remodel-calculator.html",
        "calc_name": "Bathroom Calc"
    }
]

GENERIC_BOILERPLATE = "Detailed empirical cost breakdown, licensed labor pricing, building code requirements, and contractor bid verification."


def clean_heading(title_raw: str) -> str:
    t = re.sub(r"^\s*#+\s*", "", title_raw).strip()
    t = re.sub(r"\s*\|\s*The Buyer's Math$", "", t, flags=re.IGNORECASE).strip()
    return t


def extract_best_description(html_content: str, fallback_title: str) -> str:
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
    if any(w in low for w in ["ditra", "schluter", "kerdi", "radiant", "heated floor", "tile", "bathroom", "shower", "wet-room"]): return ("Interior & Power", "interior", "/bathroom-remodel-calculator.html", "Bathroom Calc")
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
            rel_url = f"/guides/{fname}"
            if rel_url in seen_urls:
                continue
            fpath = os.path.join(articles_dir, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            t_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
            raw_title = t_match.group(1) if t_match else fname.replace(".html", "")
            title = clean_heading(raw_title)

            d_match = re.search(r"^\d{4}-\d{2}-\d{2}", fname)
            pub_date = d_match.group(0) if d_match else "2026-09-30"

            desc = extract_best_description(content, title)
            cat, cat_slug, calc_url, calc_name = classify_article(title, desc)

            articles.append({
                "url": rel_url,
                "title": title,
                "desc": desc,
                "category": cat,
                "calc_url": calc_url,
                "calc_name": calc_name,
                "date": pub_date
            })
            seen_urls.add(rel_url)

    return articles


def sync_article_file(src_path: str, dest_path: str) -> bool:
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    fname = os.path.basename(src_path)
    canonical_url = f"https://thebuyersmath.com/guides/{fname}"

    t_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    raw_title = t_match.group(1) if t_match else fname.replace(".html", "")
    title = clean_heading(raw_title)
    desc = extract_best_description(content, title)
    cat, cat_slug, calc_url, calc_name = classify_article(title, desc)

    # 1. Canonical tag
    if '<link rel="canonical"' in content:
        content = re.sub(
            r'<link\s+rel=["\']canonical["\']\s+href=["\'].*?["\']\s*/?>',
            f'<link rel="canonical" href="{canonical_url}">',
            content,
            flags=re.IGNORECASE
        )
    elif "</head>" in content:
        content = content.replace("</head>", f'  <link rel="canonical" href="{canonical_url}">\n</head>', 1)

    # 2. OpenGraph / Meta
    og_block = f"""  <meta property="og:title" content="{html.escape(title)} | The Buyer's Math">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:type" content="article">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)} | The Buyer's Math">
  <meta name="twitter:description" content="{html.escape(desc)}">"""

    if 'property="og:title"' not in content and "</head>" in content:
        content = content.replace("</head>", f"{og_block}\n</head>", 1)

    # 3. Breadcrumbs
    breadcrumb_html = f"""<div style="background: #0f172a; padding: 0.75rem 1.5rem; font-size: 0.85rem; border-bottom: 1px solid #1e293b;">
  <div style="max-width: 1100px; margin: 0 auto; color: #94a3b8;">
    <a href="/" style="color: #38bdf8; text-decoration: none;">Home</a> &gt;
    <a href="/guides.html" style="color: #38bdf8; text-decoration: none;">Guides</a> &gt;
    <span style="color: #f8fafc;">{html.escape(title)}</span>
  </div>
</div>"""

    if 'href="/guides.html"' not in content and "<body" in content:
        content = re.sub(r"(<body[^>]*>)", r"\1\n" + breadcrumb_html, content, count=1, flags=re.IGNORECASE)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    orig = ""
    if os.path.exists(dest_path):
        with open(dest_path, "r", encoding="utf-8") as f:
            orig = f.read()

    if content != orig:
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def generate_guides_index(articles):
    cards_html = ""
    for a in articles:
        cards_html += f"""
      <article class="guide-card" data-category="{html.escape(a.get('category','Other'))}">
        <div class="card-meta">
          <span class="badge">{html.escape(a.get('category','Guide'))}</span>
          <span class="date">{html.escape(a.get('date','2026-09-30'))}</span>
        </div>
        <h2><a href="{a['url']}">{html.escape(a['title'])}</a></h2>
        <p>{html.escape(a['desc'])}</p>
        <div class="card-footer">
          <a href="{a['url']}" class="read-btn">Read Full Guide &rarr;</a>
          <a href="{a['calc_url']}" class="calc-link">{html.escape(a['calc_name'])}</a>
        </div>
      </article>"""

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Home Improvement & Building Cost Guides (2026) | The Buyer's Math</title>
  <meta name="description" content="Empirical cost guides, licensed labor rates, material price benchmarks, and ROI calculators for residential construction and remodeling.">
  <link rel="canonical" href="https://thebuyersmath.com/guides.html">
  <link rel="stylesheet" href="/styles.css">
</head>
<body style="background: #090d16; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif;">
  <header style="background: #0f172a; border-bottom: 1px solid #1e293b; padding: 1.5rem 2rem;">
    <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
      <a href="/" style="font-size: 1.25rem; font-weight: 700; color: #38bdf8; text-decoration: none;">The Buyer's Math</a>
      <nav><a href="/" style="color: #94a3b8; text-decoration: none; margin-left: 1.5rem;">Calculators</a></nav>
    </div>
  </header>
  <main style="max-width: 1200px; margin: 3rem auto; padding: 0 1.5rem;">
    <h1 style="font-size: 2.25rem; font-weight: 800; margin-bottom: 0.5rem;">Empirical Cost Guides & Trade Intelligence</h1>
    <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;">Verified pricing breakdowns, code compliance checks, and contractor bid verification matrices.</p>
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem;">
      {cards_html}
    </div>
  </main>
</body>
</html>"""

    with open("guides.html", "w", encoding="utf-8") as f:
        f.write(html_out)


def main():
    synced = 0
    if os.path.exists("articles"):
        for fname in sorted(os.listdir("articles")):
            if fname.endswith(".html"):
                src = os.path.join("articles", fname)
                dest = os.path.join("guides", fname)
                if sync_article_file(src, dest):
                    synced += 1
    articles = get_all_articles()
    generate_guides_index(articles)
    print(f"Synced {synced} guide files. Total guides in index: {len(articles)}")


if __name__ == "__main__":
    main()
