import os
import re

CALCULATORS = {
    "roofing-cost-calculator.html": {
        "title": "Roof Replacement Cost Estimator",
        "desc": "Calculate roof replacement costs based on home footprint, pitch complexity, and tear-off layers."
    },
    "hvac-roi-calculator.html": {
        "title": "Heat Pump vs. Gas Furnace ROI Calculator",
        "desc": "Compare upfront installation costs, federal tax credits, and annual operating costs between heat pumps and gas furnaces."
    },
    "basement-cost-calculator.html": {
        "title": "Basement Finishing Cost Estimator",
        "desc": "Estimate total basement finishing costs including framing, drywall, electrical, and flooring."
    },
    "solar-payback-calculator.html": {
        "title": "Solar Panel Payback Timeline Calculator",
        "desc": "Calculate solar panel payback period, net metering savings, and federal 30% solar tax credit."
    },
    "kitchen-remodel-calculator.html": {
        "title": "Kitchen Remodel Cost Estimator",
        "desc": "Estimate kitchen remodeling budgets across minor, midrange, and major luxury renovations."
    },
    "driveway-paving-calculator.html": {
        "title": "Driveway Paving Calculator",
        "desc": "Estimate asphalt, concrete, and paver driveway installation and resurfacing costs."
    },
    "window-replacement-estimator.html": {
        "title": "Window Replacement Estimator",
        "desc": "Estimate vinyl, wood, and fiberglass replacement window pricing including installation."
    },
    "pool.html": {
        "title": "Pool Pump Energy Calculator",
        "desc": "Calculate electricity savings from upgrading to a variable speed swimming pool pump."
    },
    "mini-split-calculator.html": {
        "title": "Ductless Mini-Split Cost Estimator",
        "desc": "Estimate multi-zone ductless mini-split heat pump installation costs and energy efficiency."
    },
    "generator-calculator.html": {
        "title": "Standby Generator Sizing & Cost Guide",
        "desc": "Size and calculate whole-house standby generator equipment and transfer switch installation costs."
    },
    "water-heater-calculator.html": {
        "title": "Water Heater Replacement Cost Estimator",
        "desc": "Compare tankless vs. storage tank water heater replacement costs and energy efficiency."
    }
}

HEADER_HTML = """  <!-- Global Navigation Header -->
  <header style="background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 0.875rem 1.5rem; margin-bottom: 1rem;">
    <div style="max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
      <a href="/" style="color: #0f172a; text-decoration: none; font-weight: 700; font-size: 1.25rem;">The Buyer's Math</a>
      <nav style="display: flex; gap: 1.25rem; font-size: 0.95rem;">
        <a href="/" style="color: #2563eb; text-decoration: none; font-weight: 600;">Calculators</a>
        <a href="/#article-list" style="color: #475569; text-decoration: none;">Guides</a>
        <a href="/privacy-policy.html" style="color: #475569; text-decoration: none;">Privacy Policy</a>
        <a href="/terms.html" style="color: #475569; text-decoration: none;">Terms &amp; Disclaimer</a>
        <a href="/contact.html" style="color: #475569; text-decoration: none;">Contact Us</a>
      </nav>
    </div>
  </header>
"""

FOOTER_HTML = """  <!-- Global Footer with Amazon Disclosure -->
  <footer style="margin-top: 4rem; padding: 2.5rem 1rem; border-top: 1px solid #e2e8f0; text-align: center; color: #64748b; font-size: 0.875rem; background-color: #f8fafc;">
    <div style="margin-bottom: 1rem;">
      <a href="/" style="color: #475569; text-decoration: none; margin: 0 0.75rem; font-weight: 500;">Calculators</a> |
      <a href="/#article-list" style="color: #475569; text-decoration: none; margin: 0 0.75rem; font-weight: 500;">Guides</a> |
      <a href="/privacy-policy.html" style="color: #475569; text-decoration: none; margin: 0 0.75rem; font-weight: 500;">Privacy Policy</a> |
      <a href="/terms.html" style="color: #475569; text-decoration: none; margin: 0 0.75rem; font-weight: 500;">Terms &amp; Disclaimer</a> |
      <a href="/contact.html" style="color: #475569; text-decoration: none; margin: 0 0.75rem; font-weight: 500;">Contact Us</a>
    </div>
    <p style="max-width: 680px; margin: 0 auto 0.75rem auto; font-size: 0.8rem; line-height: 1.5; color: #94a3b8;">
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program. As an Amazon Associate, I earn from qualifying purchases. Calculations and tool results are directional models for informational purposes only.
    </p>
    <p style="margin: 0; font-size: 0.8rem; color: #94a3b8;">&copy; 2026 The Buyer's Math. All rights reserved.</p>
  </footer>
"""

def update_file(filename, meta):
    if not os.path.exists(filename):
        print(f"Skipping {filename} (not found)")
        return

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already updated
    if "The Buyer's Math is a participant in the Amazon Services LLC Associates Program" in content:
        print(f"{filename} is already updated.")
        return

    title = meta["title"]
    desc = meta["desc"]

    # 1. Inject Schema into <head>
    schema_snippet = f"""  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "{title}",
    "url": "https://thebuyersmath.com/{filename}",
    "applicationCategory": "FinanceApplication",
    "operatingSystem": "All",
    "description": "{desc}"
  }}
  </script>
</head>"""
    content = content.replace("</head>", schema_snippet, 1)

    # 2. Inject Header and Breadcrumb after <body>
    breadcrumb = f"""  <nav style="max-width: 1100px; margin: 0 auto 1.5rem auto; padding: 0 1.5rem; font-size: 0.875rem; color: #64748b;" aria-label="Breadcrumb">
    <a href="/" style="color: #475569; text-decoration: none;">Home</a> &gt;
    <a href="/" style="color: #475569; text-decoration: none;">Calculators</a> &gt;
    <span style="color: #0f172a; font-weight: 500;">{title}</span>
  </nav>
"""
    body_match = re.search(r'<body[^>]*>', content, re.IGNORECASE)
    if body_match:
        idx = body_match.end()
        content = content[:idx] + "\n" + HEADER_HTML + breadcrumb + content[idx:]

    # 3. Inject Footer before </body>
    content = content.replace("</body>", FOOTER_HTML + "\n</body>", 1)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully updated {filename}")

def main():
    print("Updating all calculator pages...")
    for filename, meta in CALCULATORS.items():
        update_file(filename, meta)
    print("Done! All calculator pages have been updated.")

if __name__ == "__main__":
    main()
