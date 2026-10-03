# generate_article.py (Auto-Discovers Available Claude Models)
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

def get_active_claude_model(client):
    try:
        models_resp = client.models.list()
        model_ids = [m.id for m in models_resp.data]
        print(f"Available Claude models on your account: {model_ids}")
        # Prioritize 3.5 Sonnet, then Haiku, or fallback to first available
        for target in ["3-5-sonnet", "3-haiku", "sonnet", "haiku"]:
            for mid in model_ids:
                if target in mid:
                    print(f"Selected model: {mid}")
                    return mid
        if model_ids:
            return model_ids[0]
    except Exception as e:
        print(f"Models list query notice: {e}")
    # Default fallback
    return "claude-3-5-sonnet-20241022"

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY environment variable not found.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    model = get_active_claude_model(client)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Step 1: Generate Topic & Amazon Product Keyword
    calc_list_str = "\n".join([f"- {c['name']} ({c['url']})" for c in CALCULATORS])
    topic_prompt = f"""Generate a unique, high-intent home improvement or DIY cost analysis article title for 2026, paired with an Amazon product search keyword.
Respond strictly in this format: Title | Keyword
Example: How Much Does Attic Insulation Cost in 2026? | attic insulation baffles

Site Calculators available for reference:
{calc_list_str}
"""
    topic_msg = client.messages.create(
        model=model,
        max_tokens=150,
        messages=[{"role": "user", "content": topic_prompt}]
    )
    raw_topic = topic_msg.content[0].text.strip()
    title_raw = raw_topic.split("|")
    title = title_raw[0].strip()
    amazon_kw = title_raw[1].strip() if len(title_raw) > 1 else "home improvement tools"
    slug = slugify(title)

    # Step 2: Generate 800-Word SEO Article Body
    content_prompt = f"""Write an authoritative, highly practical 800-word homeowner's buying guide for: "{title}".
Requirements:
1. Provide realistic 2026 cost ranges (materials, labor, permit fees).
2. Format cleanly using HTML: <h2>, <h3>, <p>, <ul>, <li>, and <table> where relevant. Do NOT wrap in <html>, <head>, or <body> tags.
3. Naturally reference and hyperlink to 1 or 2 of these site calculators within the text:
{calc_list_str}
4. Include a practical DIY vs. Professional Contractor decision breakdown.
5. Conclude with an FAQ section featuring 3 questions formatted with <details> and <summary>.
"""
    body_msg = client.messages.create(
        model=model,
        max_tokens=3500,
        messages=[{"role": "user", "content": content_prompt}]
    )
    article_body = body_msg.content[0].text.strip()
    article_body = re.sub(r'^```html\s*', '', article_body)
    article_body = re.sub(r'\s*```$', '', article_body)

    # Step 3: Full Page Assembly
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

    # Step 5: Update sitemap.xml
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

if __name__ == "__main__":
    main()
