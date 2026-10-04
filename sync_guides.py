
sync_guides.py

100%
#!/usr/bin/env python3
"""
sync_guides.py - Automated Guide Archive Generator & Navigation Sync for The Buyer's Math
Scans both `articles/` and `guides/` folders, regenerates `guides.html`,
updates `index.html` with the latest articles + archive link, and syncs `sitemap.xml`.
"""

import os
import re
from datetime import datetime

FLAGSHIP_GUIDES = [
    {
        "url": "/guides/heat-pump-tax-credit-2026.html",
        "title": "Heat Pump Tax Credit 2026: Section 25C Eligibility, Costs & Payback",
        "date": "2026-10-03",
        "description": "Complete breakdown of 2026 Inflation Reduction Act Section 25C tax credits, AHRI standards, and payback economics for heat pumps.",
        "category": "HVAC & Energy"
    },
    {
        "url": "/guides/roof-replacement-cost-per-square-2026.html",
        "title": "Roof Replacement Cost per Square in 2026: Architectural vs. 3-Tab",
        "date": "2026-10-03",
        "description": "Empirical pricing per roofing square (100 sq ft), tear-off labor rates, pitch slope premiums, and shingle warranties.",
        "category": "Building Envelope"
    }
]

def get_all_articles():
    articles = list(FLAGSHIP_GUIDES)
    articles_dir = "articles"
    if os.path.exists(articles_dir):
        for fname in sorted(os.listdir(articles_dir), reverse=True):
            if fname.endswith(".html"):
                fpath = os.path.join(articles_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                t_match = re.search(r"<title>(.*?)(?: \| The Buyer's Math)?</title>", content, re.IGNORECASE)
                title = t_match.group(1).replace(" | The Buyer's Math", "").strip() if t_match else fname.replace(".html", "")

                d_match = re.search(r'Published on (\d{4}-\d{2}-\d{2})', content)
                if not d_match:
                    d_match = re.match(r"^(\d{4}-\d{2}-\d{2})", fname)
                date_str = d_match.group(1) if d_match else datetime.now().strftime("%Y-%m-%d")

                desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
                description = desc_match.group(1).strip() if desc_match else "Empirical pricing data, materials breakdown, and buying advice."

                # Category classification
                cat = "Home Improvement"
                low = (title + " " + description).lower()
                if any(w in low for w in ["roof", "shingle", "siding", "window", "fence", "driveway"]):
                    cat = "Exterior & Envelope"
                elif any(w in low for w in ["heat pump", "furnace", "hvac", "mini-split", "ac", "insulation"]):
                    cat = "HVAC & Energy"
                elif any(w in low for w in ["bathroom", "kitchen", "basement", "remodel"]):
                    cat = "Interior Remodeling"
                elif any(w in low for w in ["solar", "generator", "charger", "ev", "electric"]):
                    cat = "Power & Renewables"

                articles.append({
                    "url": f"/articles/{fname}",
                    "title": title,
                    "date": date_str,
                    "description": description,
                    "category": cat
                })
    # Sort newest first
    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles

def generate_guides_html(articles):
    cards_html = []
    for a in articles:
        card = f"""      <article class="guide-card" data-category="{a['category'].lower()}">
        <div class="guide-card-header">
          <span class="guide-badge">{a['category']}</span>
          <span class="guide-date">{a['date']}</span>
        </div>
        <h2 class="guide-title"><a href="{a['url']}">{a['title']}</a></h2>
        <p class="guide-desc">{a['description']}</p>
        <a href="{a['url']}" class="guide-read-link">Read Full Guide &rarr;</a>
      </article>"""
        cards_html.append(card)

    cards_str = "\n\n".join(cards_html)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Home Improvement Buying Guides & Cost Breakdowns | The Buyer's Math</title>
  <meta name="description" content="Browse our comprehensive library of empirical home improvement cost guides, Inflation Reduction Act tax credit rules, and contractor quote benchmarks.">
  <link rel="canonical" href="https://thebuyersmath.com/guides.html">
  <link rel="stylesheet" href="/styles.css">

  <!-- OpenGraph Social Meta Tags -->
  <meta property="og:title" content="Home Improvement Buying Guides & Cost Breakdowns | The Buyer's Math">
  <meta property="og:description" content="Browse our library of empirical cost guides, tax credit breakdowns, and contractor pricing benchmarks.">
  <meta property="og:url" content="https://thebuyersmath.com/guides.html">
  <meta property="og:type" content="website">

  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-V4GTQSCFW6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-V4GTQSCFW6');
  </script>

  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>

  <style>
    .guides-hero {{
      text-align: center;
      padding: 3rem 1.5rem 2rem 1.5rem;
      max-width: 860px;
      margin: 0 auto;
    }}
    .guides-hero h1 {{
      font-size: clamp(2rem, 4vw, 2.75rem);
      margin-bottom: 0.75rem;
      letter-spacing: -0.03em;
    }}
    .guides-hero p {{
      color: #64748b;
      font-size: 1.15rem;
      max-width: 680px;
      margin: 0 auto 1.5rem auto;
    }}
    .guide-search-box {{
      max-width: 520px;
      margin: 0 auto 2rem auto;
      padding: 0 1.5rem;
    }}
    .guide-search-input {{
      width: 100%;
      padding: 0.85rem 1.25rem;
      border: 1px solid #cbd5e1;
      border-radius: 9999px;
      font-size: 1rem;
      font-family: inherit;
      box-sizing: border-box;
      outline: none;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      transition: all 0.2s ease;
    }}
    .guide-search-input:focus {{
      border-color: #2563eb;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }}
    .guides-container {{
      max-width: 1140px;
      margin: 0 auto 4rem auto;
      padding: 0 1.5rem;
    }}
    .guides-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.75rem;
    }}
    .guide-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 1.75rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s ease;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .guide-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(0,0,0,0.08);
      border-color: #93c5fd;
    }}
    .guide-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.85rem;
    }}
    .guide-badge {{
      font-size: 0.75rem;
      font-weight: 700;
      color: #2563eb;
      background: #eff6ff;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .guide-date {{
      font-size: 0.85rem;
      color: #94a3b8;
    }}
    .guide-title {{
      font-size: 1.25rem;
      font-weight: 700;
      line-height: 1.35;
      margin: 0 0 0.75rem 0;
    }}
    .guide-title a {{
      color: #0f172a;
      text-decoration: none;
    }}
    .guide-title a:hover {{
      color: #2563eb;
    }}
    .guide-desc {{
      color: #475569;
      font-size: 0.95rem;
      line-height: 1.55;
      margin: 0 0 1.25rem 0;
      flex-grow: 1;
    }}
    .guide-read-link {{
      color: #2563eb;
      font-weight: 700;
      font-size: 0.95rem;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }}
    .guide-read-link:hover {{
      color: #1d4ed8;
      text-decoration: underline;
    }}
  </style>
</head>
<body>

  <!-- Global Sticky Header -->
  <header class="site-header">
    <div class="header-inner">
      <a href="/" class="site-logo">The Buyer's Math</a>
      <nav class="site-nav">
        <a href="/">Calculators</a>
        <a href="/guides.html" class="active" style="color: #2563eb; font-weight: 600;">Guides</a>
        <a href="/privacy-policy.html">Privacy Policy</a>
        <a href="/terms.html">Terms &amp; Disclaimer</a>
        <a href="/contact.html">Contact Us</a>
      </nav>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="guides-hero">
    <h1>Guides &amp; Cost Analysis Archive</h1>
    <p>Comprehensive cost breakdowns, Section 25C federal tax credit instructions, and equipment comparison models for homeowners.</p>
  </section>

  <!-- Live Search Bar -->
  <div class="guide-search-box">
    <input type="text" id="guide-search" class="guide-search-input" placeholder="Search guides (e.g. tax credit, roof, heat pump)..." aria-label="Search guides">
  </div>

  <!-- Guides Grid -->
  <main class="guides-container">
    <div class="guides-grid" id="guides-grid">
{cards_str}
    </div>
  </main>

  <!-- Global Footer -->
  <footer class="site-footer">
    <div class="footer-nav">
      <a href="/">Calculators</a> |
      <a href="/guides.html">Guides</a> |
      <a href="/privacy-policy.html">Privacy Policy</a> |
      <a href="/terms.html">Terms &amp; Disclaimer</a> |
      <a href="/contact.html">Contact Us</a>
    </div>
    <p class="footer-disclosure">
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program. As an Amazon Associate, I earn from qualifying purchases. Calculations and tool results are directional models for informational purposes only.
    </p>
    <p class="footer-copy">&copy; 2026 The Buyer's Math. All rights reserved.</p>
  </footer>

  <script>
    const searchInput = document.getElementById('guide-search');
    const cards = document.querySelectorAll('.guide-card');

    if (searchInput) {{
      searchInput.addEventListener('input', () => {{
        const q = searchInput.value.toLowerCase().trim();
        cards.forEach(card => {{
          const text = card.innerText.toLowerCase();
          if (!q || text.includes(q)) {{
            card.style.display = 'flex';
          }} else {{
            card.style.display = 'none';
          }}
        }});
      }});
    }}
  </script>
</body>
</html>
"""
    with open("guides.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated guides.html with {len(articles)} guides.")

def update_index_latest(articles):
    if not os.path.exists("index.html"):
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Show top 6 latest articles on the homepage
    top_articles = articles[:6]
    items_html = []
    for a in top_articles:
        items_html.append(f'          <li><span class="article-date">{a["date"]}</span> <a href="{a["url"]}">{a["title"]}</a></li>')

    archive_btn = f"""          <li style="margin-top: 1.5rem; list-style: none;">
            <a href="/guides.html" style="display: inline-block; background: #2563eb; color: #ffffff; padding: 0.65rem 1.25rem; border-radius: 6px; font-weight: 700; text-decoration: none;">
              Browse Full Guides Archive ({len(articles)} Articles) &rarr;
            </a>
          </li>"""

    items_html.append(archive_btn)
    items_html.append("          <!-- ARTICLES_LIST_MARKER -->")

    # Replace existing article-list contents
    marker_pattern = r'<ul id="article-list">.*?</ul>'
    replacement = '<ul id="article-list">\n' + "\n".join(items_html) + '\n        </ul>'
    new_content = re.sub(marker_pattern, replacement, content, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Updated index.html with latest guides and archive button.")

if __name__ == "__main__":
    all_articles = get_all_articles()
    generate_guides_html(all_articles)
    update_index_latest(all_articles)
Displaying sync_guides.py.
