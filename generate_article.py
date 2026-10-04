# generate_article.py
# Automated Daily Cost Guide Generator powered by Anthropic Claude
# Packed with high-converting revenue generators:
# 1. Top Amazon Quick-Pick Box (Above the fold)
# 2. In-content Responsive AdSense Display Unit
# 3. Interactive Calculator CTA Banner
# 4. Bottom Project Gear Recommendation Box

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

def select_active_model(client):
    try:
        models_response = client.models.list()
        active_ids = [m.id for m in models_response.data]
        preferred = [
            "claude-haiku-4-5", "claude-sonnet-4-6", "claude-sonnet-4-5",
            "claude-3-7-sonnet", "claude-opus-4-6", "claude-opus-4-5"
        ]
        for pref in preferred:
            for m_id in active_ids:
                if pref in m_id:
                    return m_id
        for m_id in active_ids:
            if "claude" in m_id and "embed" not in m_id:
                return m_id
        if active_ids:
            return active_ids[0]
    except Exception as e:
        print(f"Warning: Model listing fallback ({e})")
    return "claude-sonnet-4-6"

def call_claude(client, model_name, prompt, max_tokens=1500):
    msg = client.messages.create(
        model=model_name,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not found in environment.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    date_str = datetime.now().strftime("%Y-%m-%d")
    model_name = select_active_model(client)
    print(f"Using Anthropic model: {model_name}")

    # Step 1: Generate Topic, Amazon Keyword & Primary Matching Calculator
    calc_list_str = "\n".join([f"- {c['name']} ({c['url']})" for c in CALCULATORS])
    topic_prompt = f"""Generate a unique, high-intent home improvement or DIY cost analysis article title for 2026, paired with an Amazon product search keyword, and the best matching calculator from the list below.
Format strictly as: Title | Keyword | Calculator Name | Calculator URL
Example: How Much Does Attic Insulation Cost in 2026? | attic insulation baffles | Heat Pump vs. Gas Furnace ROI | ../hvac-roi-calculator.html

Available Calculators:
{calc_list_str}
"""

    raw_topic = call_claude(client, model_name, topic_prompt, max_tokens=200)
    parts = [p.strip() for p in raw_topic.split("|")]
    title = parts[0]
    amazon_kw = parts[1] if len(parts) > 1 else "home improvement tools"
    matched_calc_name = parts[2] if len(parts) > 2 else "Cost Calculators"
    matched_calc_url = parts[3] if len(parts) > 3 else "../index.html"
    slug = slugify(title)

    # Step 2: Generate Authoritative Content
    content_prompt = f"""Write an informative, authoritative 800-word homeowner's guide for: "{title}".

Requirements:
1. Provide realistic 2026 cost ranges (materials, labor, permits).
2. Format cleanly using HTML: <h2>, <h3>, <p>, <ul>, <li>, and <table> if applicable. Do NOT include <html> or <body> tags.
3. Reference and hyperlink naturally to the companion calculator: <a href="{matched_calc_url}">{matched_calc_name}</a>.
4. Provide a DIY vs. Professional breakdown.
5. Conclude with an FAQ section (3 questions using <details> and <summary>).
"""

    raw_body = call_claude(client, model_name, content_prompt, max_tokens=2500)
    article_body = re.sub(r'^```html\s*', '', raw_body)
    article_body = re.sub(r'\s*```$', '', article_body)

    # Revenue Generators Assembly:
    # 1. Top Amazon Quick-Pick Box
    top_revenue_box = f"""
      <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 1.25rem 1.5rem; margin: 1.5rem 0 2rem 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span style="background: #f59e0b; color: #ffffff; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em;">Recommended Project Gear</span>
          <p style="margin: 0.4rem 0 0 0; font-weight: 600; color: #92400e; font-size: 1rem;">Top-rated {amazon_kw.title()} &amp; Materials</p>
          <p style="margin: 0.2rem 0 0 0; color: #78350f; font-size: 0.85rem;">Check real-time pricing and customer reviews before starting:</p>
        </div>
        <a href="https://www.amazon.com/s?k={slugify(amazon_kw)}&tag=nfagiolo-20" target="_blank" rel="noopener noreferrer" style="background: #d97706; color: #ffffff; padding: 0.65rem 1.25rem; border-radius: 6px; font-weight: 700; font-size: 0.9rem; text-decoration: none; display: inline-flex; align-items: center; gap: 0.4rem; box-shadow: 0 2px 4px rgba(217, 119, 6, 0.25);">
          🛒 Check Deals on Amazon &rarr;
        </a>
      </div>
    """

    # 2. Mid-Article Interactive Calculator Banner
    mid_calculator_cta = f"""
      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; border-radius: 8px; padding: 1.5rem; margin: 2.5rem 0; text-align: center;">
        <span style="color: #2563eb; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Interactive Estimator</span>
        <h3 style="margin: 0.4rem 0 0.5rem 0; color: #1e3a8a; font-size: 1.3rem;">Calculate Exact Costs for Your Home</h3>
        <p style="margin: 0 0 1.25rem 0; color: #475569; font-size: 0.95rem;">Model custom square footage, labor rates, and local tax incentives with our free tool:</p>
        <a href="{matched_calc_url}" style="background: #2563eb; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 700; text-decoration: none; display: inline-block;">Open the {matched_calc_name} &rarr;</a>
      </div>
    """

    # 3. Responsive AdSense Display Unit
    adsense_unit = """
      <div style="margin: 2.5rem 0; text-align: center; min-height: 250px;">
        <ins class="adsbygoogle"
             style="display:block; text-align:center;"
             data-ad-layout="in-article"
             data-ad-format="fluid"
             data-ad-client="ca-pub-1199906473460957"
             data-ad-slot="responsive"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
      </div>
    """

    # 4. Bottom Gear Callout
    bottom_gear_box = f"""
      <div class="curated-recommendation" style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 1.5rem; margin: 3rem 0 1rem 0; text-align: center;">
        <p style="font-weight: 700; color: #92400e; margin: 0 0 0.5rem 0; font-size: 1.1rem;">🛠️ Essential DIY &amp; Jobsite Supplies</p>
        <p style="margin: 0 0 1rem 0; font-size: 0.95rem; color: #78350f;">Equip your project with contractor-grade {amazon_kw.title()} and safety gear:</p>
        <a href="https://www.amazon.com/s?k={slugify(amazon_kw)}&tag=nfagiolo-20" target="_blank" rel="noopener noreferrer" class="btn-affiliate" style="background: #d97706; color: #ffffff; font-weight: 700; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; display: inline-block;">
          View {amazon_kw.title()} on Amazon
        </a>
      </div>
    """

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
      <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem;">
        Published on {date_str} &bull; The Buyer's Math Editorial Staff &bull; 2026 Cost Data
      </div>

      {top_revenue_box}

      {article_body}

      {mid_calculator_cta}

      {adsense_unit}

      {bottom_gear_box}
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
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program. As an Amazon Associate, I earn from qualifying purchases. Calculations and tool results are directional models for informational purposes only.
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

    # Update index.html
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

    # Update sitemap.xml
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
