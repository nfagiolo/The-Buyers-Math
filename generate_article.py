# generate_article.py
# Automated Daily Cost Guide Generator powered by Anthropic Claude
# Features multi-model fallback to ensure seamless runs without deprecation 404s.

import os
import re
from datetime import datetime
import anthropic

CALCULATORS = [
    {"name": "Roof Replacement Cost Estimator", "url": "../roofing-cost-calculator.html", "keywords": ["roof", "roofing", "shingles"]},
    {"name": "Heat Pump vs. Gas Furnace ROI", "url": "../hvac-roi-calculator.html", "keywords": ["hvac", "heat pump", "furnace", "heating", "cooling"]},
    {"name": "Basement Finishing Cost Estimator", "url": "../basement-cost-calculator.html", "keywords": ["basement", "remodel", "framing", "drywall"]},
    {"name": "Solar Panel Payback Timeline", "url": "../solar-payback-calculator.html", "keywords": ["solar", "panels", "electric bill", "clean energy"]},
    {"name": "Kitchen Remodel Cost Estimator", "url": "../kitchen-remodel-calculator.html", "keywords": ["kitchen", "cabinets", "countertops", "appliances"]},
    {"name": "Driveway Paving Calculator", "url": "../driveway-paving-calculator.html", "keywords": ["driveway", "asphalt", "concrete", "paving"]},
    {"name": "Window Replacement Estimator", "url": "../window-replacement-estimator.html", "keywords": ["windows", "glazing", "drafts", "replacement"]},
    {"name": "Pool Pump Energy Calculator", "url": "../pool.html", "keywords": ["pool", "pump", "filtration", "energy"]},
    {"name": "Mini-Split AC Cost Estimator", "url": "../mini-split-calculator.html", "keywords": ["mini-split", "ductless", "air conditioning"]},
    {"name": "Backup Generator Sizing Guide", "url": "../generator-calculator.html", "keywords": ["generator", "backup power", "standby", "outage"]},
    {"name": "Water Heater Replacement Cost", "url": "../water-heater-calculator.html", "keywords": ["water heater", "tankless", "plumbing"]}
]

def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '-', text).strip('-')

def call_claude(client, prompt, max_tokens=1500):
    """Tries primary models with automatic fallback to prevent 404 deprecation errors."""
    candidate_models = [
        "claude-3-5-sonnet-latest",
        "claude-3-5-sonnet-20241022",
        "claude-3-haiku-20240307"
    ]
    for model in candidate_models:
        try:
            print(f"Querying Claude model: {model}...")
            msg = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text.strip()
        except anthropic.NotFoundError:
            print(f"Model {model} returned 404, falling back to next candidate...")
            continue
    raise RuntimeError("None of the specified Anthropic models were accessible.")

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not found in environment.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Step 1: Generate Topic & Amazon Keyword
    calc_list_str = "\n".join([f"- {c['name']} ({c['url']})" for c in CALCULATORS])
    topic_prompt = f"""Generate a unique, high-intent home improvement or DIY cost analysis article title for 2026, paired with an Amazon product search keyword.
Format strictly as: Title | Keyword
Example: How Much Does Attic Insulation Cost in 2026? | attic insulation baffles

Site Calculators available for contextual reference:
{calc_list_str}
"""

    raw_topic = call_claude(client, topic_prompt, max_tokens=150)
    title_raw = raw_topic.split("|")
    title = title_raw[0].strip()
    amazon_kw = title_raw[1].strip() if len(title_raw) > 1 else "home improvement tools"
    slug = slugify(title)

    # Step 2: Generate Article Body with Contextual Links
    content_prompt = f"""Write an informative, authoritative 800-word homeowner's guide for: "{title}".

Requirements:
1. Provide realistic 2026 cost ranges (materials, labor, permits).
2. Format cleanly using HTML: <h2>, <h3>, <p>, <ul>, <li>, and <table> if applicable. Do NOT include <html> or <body> tags.
3. Where naturally relevant, reference and hyperlink to 1 or 2 of these site calculators:
{calc_list_str}
4. Provide a DIY vs. Professional breakdown.
5. Conclude with an FAQ section (3 questions using <details> and <summary>).
"""

    raw_body = call_claude(client, content_prompt, max_tokens=2500)
    article_body = re.sub(r'^```html\s*', '', raw_body)
    article_body = re.sub(r'\s*```$', '', article_body)

    # Step 3: Full Page Assembly linked to styles.css
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | The Buyer's Math</title>
  <meta name="description" content="{title} - Real 2026 cost estimates, labor vs material breakdown, and buying guide.">
  <link rel="stylesheet" href="../styles.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="../index.html" class="site-logo">The Buyer's Math</a>
      <nav class="site-nav">
        <a href="../index.html">Calculators</a>
        <a href="../index.html#article-list">Guides</a>
        <a href="../privacy-policy.html">Privacy</a>
        <a href="../terms.html">Terms</a>
        <a href="../contact.html">Contact</a>
      </nav>
    </div>
  </header>
  
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <a href="../index.html">Home</a> &gt;
    <a href="../index.html#article-list">Guides</a> &gt;
    <span class="current">{title}</span>
  </nav>
  
  <main class="container" style="max-width: 860px; margin: 2rem auto; padding: 0 1.5rem;">
    <article class="card" style="padding: 2.5rem;">
      <h1 style="font-size: 2.25rem; margin-top: 0; margin-bottom: 0.5rem;">{title}</h1>
      <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 2rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem;">
        Published on {date_str} &bull; The Buyer's Math Editorial Staff &bull; 2026 Cost Data
      </div>

      {article_body}

      <div class="curated-recommendation">
        <p class="rec-title">Recommended Project Gear</p>
        <p style="margin: 0.25rem 0 1rem 0; font-size: 0.95rem; color: #475569;">Compare top-rated tools and materials for this project on Amazon:</p>
        <a href="https://www.amazon.com/s?k={slugify(amazon_kw)}&tag=nfagiolo-20" target="_blank" rel="noopener noreferrer" class="btn-affiliate">🛠️ View {amazon_kw.title()} on Amazon</a>
      </div>
    </article>
  </main>
  
  <footer class="site-footer">
    <div class="footer-nav">
      <a href="../index.html">Calculators</a> |
      <a href="../index.html#article-list">Guides</a> |
      <a href="../privacy-policy.html">Privacy Policy</a> |
      <a href="../terms.html">Terms &amp; Disclaimer</a> |
      <a href="../contact.html">Contact Us</a>
    </div>
    <p class="footer-disclosure">
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program. As an Amazon Associate, I earn from qualifying purchases.
    </p>
    <p class="footer-copy">&copy; 2026 The Buyer's Math. All rights reserved.</p>
  </footer>
</body>
</html>
"""

    # Write article file
    os.makedirs("articles", exist_ok=True)
    article_path = f"articles/{date_str}-{slug}.html"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Created: {article_path}")

    # Step 4: Update index.html with Deduplication
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            idx_content = f.read()

        article_rel_url = f"articles/{date_str}-{slug}.html"
        if article_rel_url not in idx_content and slug not in idx_content:
            new_item = f'<li><span class="article-date">{date_str}</span> <a href="{article_rel_url}">{title}</a></li>\n    <!-- ARTICLES_LIST_MARKER -->'
            idx_content = idx_content.replace("<!-- ARTICLES_LIST_MARKER -->", new_item)
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(idx_content)
            print("Updated index.html with new article.")
        else:
            print("Article already present in index.html; skipped duplicate injection.")

    # Step 5: Automatically Update sitemap.xml with the New Article URL
    if os.path.exists("sitemap.xml"):
        with open("sitemap.xml", "r", encoding="utf-8") as f:
            sitemap_content = f.read()

        article_full_url = f"https://thebuyersmath.com/articles/{date_str}-{slug}.html"
        if article_full_url not in sitemap_content:
            sitemap_entry = f"""  <url>
    <loc>{article_full_url}</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>"""
            sitemap_content = sitemap_content.replace("</urlset>", sitemap_entry)
            with open("sitemap.xml", "w", encoding="utf-8") as f:
                f.write(sitemap_content)
            print("Updated sitemap.xml with new article.")
        else:
            print("Article already present in sitemap.xml.")

if __name__ == "__main__":
    main()
