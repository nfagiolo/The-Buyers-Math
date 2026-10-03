import os
import re
from datetime import datetime
from google import genai

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

def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found.")
        return

    client = genai.Client(api_key=api_key)
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Step 1: Generate Topic & Amazon Keyword
    calc_list_str = "\n".join([f"- {c['name']} ({c['url']})" for c in CALCULATORS])
    topic_prompt = f"""Generate a unique, high-intent home improvement or DIY cost analysis article title for 2026, paired with an Amazon product search keyword.
Format as: Title | Keyword
Example: How Much Does Attic Insulation Cost in 2026? | attic insulation baffles

Site Calculators available for contextual reference:
{calc_list_str}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=topic_prompt)
    title_raw = response.text.strip().split("|")
    title = title_raw[0].strip()
    amazon_kw = title_raw[1].strip() if len(title_raw) > 1 else "home improvement tools"
    slug = slugify(title)

    # Step 2: Generate Article Body with Contextual Links
    content_prompt = f"""Write an informative, detailed 800-word homeowner's guide for: "{title}".
Requirements:
1. Provide realistic 2026 cost ranges (materials, labor, permits).
2. Format cleanly using HTML: <h2>, <h3>, <p>, <ul>, <li>, and <table> if applicable. Do NOT include <html> or <body> tags.
3. Where naturally relevant, reference and hyperlink to 1 or 2 of these site calculators:
{calc_list_str}
4. Provide a DIY vs. Professional breakdown.
5. Conclude with an FAQ section (3 questions).
"""
    body_resp = client.models.generate_content(model="gemini-2.5-flash", contents=content_prompt)
    article_body = body_resp.text.strip()
    # Clean possible markdown code fences
    article_body = re.sub(r'^```html\s*', '', article_body)
    article_body = re.sub(r'\s*```$', '', article_body)

    # Step 3: Full Page Assembly with Navigation, Footer, and Amazon Disclosure
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | The Buyer's Math</title>
  <meta name="description" content="{title} - Real 2026 cost estimates, labor vs material breakdown, and buying guide.">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>
  <style>
    :root {{ --bg: #fafafa; --card: #ffffff; --text: #0f172a; --muted: #475569; --border: #e2e8f0; --primary: #2563eb; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: var(--text); background: var(--bg); margin: 0; padding: 0; }}
    .site-header {{ background: #fff; border-bottom: 1px solid var(--border); padding: 1rem 1.5rem; display: flex; justify-content: space-between; align-items: center; max-width: 960px; margin: 0 auto; }}
    .site-header a {{ color: var(--text); text-decoration: none; font-weight: 700; font-size: 1.25rem; }}
    .site-nav a {{ font-size: 0.95rem; font-weight: 500; color: var(--muted); margin-left: 1.25rem; text-decoration: none; }}
    .site-nav a:hover {{ color: var(--primary); }}
    .article-wrap {{ max-width: 820px; margin: 2rem auto; padding: 2rem; background: var(--card); border: 1px solid var(--border); border-radius: 8px; }}
    h1 {{ font-size: 2.2rem; color: #0f172a; margin-top: 0; }}
    .meta {{ font-size: 0.875rem; color: #64748b; margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }}
    .affiliate-box {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 1.25rem; border-radius: 6px; margin: 2rem 0; text-align: center; }}
    .affiliate-btn {{ display: inline-block; background: #d97706; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 0.5rem; }}
    .footer {{ border-top: 1px solid var(--border); padding: 2.5rem 1rem; text-align: center; font-size: 0.875rem; color: #64748b; margin-top: 4rem; background: #fff; }}
    .footer a {{ color: var(--muted); text-decoration: none; margin: 0 0.5rem; }}
  </style>
</head>
<body>
  <header class="site-header">
    <a href="../index.html">The Buyer's Math</a>
    <nav class="site-nav">
      <a href="../index.html">Calculators</a>
      <a href="../index.html#article-list">Guides</a>
      <a href="../privacy-policy.html">Privacy</a>
      <a href="../terms.html">Terms</a>
      <a href="../contact.html">Contact</a>
    </nav>
  </header>

  <main class="article-wrap">
    <h1>{title}</h1>
    <div class="meta">Published on {date_str} &bull; The Buyer's Math Editorial Staff</div>
    {article_body}

    <div class="affiliate-box">
      <p style="margin:0 0 0.5rem 0; font-weight:600; color:#92400e;">Recommended Tools & Materials for This Project:</p>
      <a href="https://www.amazon.com/s?k={slugify(amazon_kw)}&tag=nfagiolo-20" target="_blank" rel="noopener noreferrer" class="affiliate-btn">🛠️ View {amazon_kw.title()} on Amazon</a>
    </div>
  </main>

  <footer class="footer">
    <div style="margin-bottom: 1rem;">
      <a href="../index.html">Calculators</a> |
      <a href="../index.html#article-list">Guides</a> |
      <a href="../privacy-policy.html">Privacy Policy</a> |
      <a href="../terms.html">Terms & Disclaimer</a> |
      <a href="../contact.html">Contact Us</a>
    </div>
    <p style="max-width: 680px; margin: 0 auto 0.75rem auto; font-size: 0.8rem; line-height: 1.5; color: #94a3b8;">
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program. As an Amazon Associate, I earn from qualifying purchases.
    </p>
    <p style="margin: 0; font-size: 0.8rem; color: #94a3b8;">&copy; 2026 The Buyer's Math. All rights reserved.</p>
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

    # Step 4: Robust Update of index.html with Deduplication
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

if __name__ == "__main__":
    main()
