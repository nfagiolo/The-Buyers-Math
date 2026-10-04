# apply_seo_social_tags.py
# The Buyer's Math - Automated OpenGraph, Twitter Card & Schema.org Enhancer
# Run in repository root to ensure all calculators, guides, and articles have
# rich preview cards for social sharing (Reddit, X, Facebook, LinkedIn, iMessage).

import os
import re

CALCULATOR_METADATA = {
    "roofing-cost-calculator.html": {
        "title": "Roof Replacement Cost Estimator (2026) | The Buyer's Math",
        "desc": "Calculate roof replacement costs based on home footprint, pitch slope, and shingle material grades."
    },
    "hvac-roi-calculator.html": {
        "title": "Heat Pump vs. Gas Furnace ROI Calculator (2026) | The Buyer's Math",
        "desc": "Compare upfront installation costs, Section 25C federal tax credits, and annual operating costs between heat pumps and gas furnaces."
    },
    "attic-insulation-calculator.html": {
        "title": "Attic Insulation & Air Sealing ROI Calculator (2026) | The Buyer's Math",
        "desc": "Calculate attic insulation upgrade costs, air sealing savings, Section 25C federal tax credits, and utility payback timeline."
    },
    "bathroom-remodel-calculator.html": {
        "title": "Bathroom Remodel Cost Estimator (2026) | The Buyer's Math",
        "desc": "Estimate 2026 bathroom remodeling costs across powder rooms, guest baths, and primary luxury suites."
    },
    "ev-charger-calculator.html": {
        "title": "EV Home Charger Installation Cost Estimator (2026) | The Buyer's Math",
        "desc": "Calculate Level 2 EV home charger installation costs, 240V conduit runs, electrical panel upgrades, and Section 30C tax credits."
    },
    "fence-cost-calculator.html": {
        "title": "Fence Cost & Linear Footage Estimator (2026) | The Buyer's Math",
        "desc": "Calculate fence installation costs per linear foot. Compare pressure-treated pine, cedar, vinyl privacy, and aluminum fencing budgets."
    },
    "siding-cost-calculator.html": {
        "title": "Home Siding Replacement Cost Estimator (2026) | The Buyer's Math",
        "desc": "Calculate 2026 home siding replacement costs per square (100 sq ft). Compare vinyl, insulated vinyl, fiber cement, and engineered wood."
    },
    "kitchen-remodel-calculator.html": {
        "title": "Kitchen Remodel Cost Estimator (2026) | The Buyer's Math",
        "desc": "Estimate kitchen remodeling budgets across cosmetic refresh, midrange pull-and-replace, and luxury custom renovations."
    },
    "solar-payback-calculator.html": {
        "title": "Solar Panel Payback Timeline Calculator (2026) | The Buyer's Math",
        "desc": "Calculate residential solar panel payback period, net metering utility offset, and federal 30% solar tax credit."
    },
    "basement-cost-calculator.html": {
        "title": "Basement Finishing Cost Estimator (2026) | The Buyer's Math",
        "desc": "Estimate total basement finishing costs including framing, drywall, subfloor moisture mitigation, electrical, and flooring."
    },
    "driveway-paving-calculator.html": {
        "title": "Driveway Paving Calculator (2026) | The Buyer's Math",
        "desc": "Estimate asphalt, concrete, and interlocking paver driveway installation and resurfacing costs per square foot."
    },
    "window-replacement-estimator.html": {
        "title": "Window Replacement Estimator (2026) | The Buyer's Math",
        "desc": "Estimate vinyl, wood, and fiberglass replacement window pricing including installation labor and energy savings."
    },
    "mini-split-calculator.html": {
        "title": "Ductless Mini-Split Cost Estimator (2026) | The Buyer's Math",
        "desc": "Estimate single and multi-zone ductless mini-split heat pump equipment costs, lineset installation, and efficiency savings."
    },
    "generator-calculator.html": {
        "title": "Standby Generator Sizing & Cost Guide (2026) | The Buyer's Math",
        "desc": "Calculate whole-house standby generator wattage requirements, fuel consumption, and automatic transfer switch installation costs."
    },
    "water-heater-calculator.html": {
        "title": "Water Heater Replacement Cost Estimator (2026) | The Buyer's Math",
        "desc": "Compare tankless, standard atmospheric tank, and hybrid heat pump water heater replacement costs and utility savings."
    },
    "pool.html": {
        "title": "Pool Pump Energy Savings Calculator (2026) | The Buyer's Math",
        "desc": "Calculate annual electricity savings and payback timeline from upgrading to an ENERGY STAR variable-speed pool pump."
    },
    "index.html": {
        "title": "The Buyer's Math | 16 Empirical Home Improvement Cost & ROI Calculators (2026)",
        "desc": "Transparent, empirical pricing models, Section 25C federal tax credits, and contractor estimate calculators for 16 major residential renovations."
    },
    "guides.html": {
        "title": "Homeowner Cost Guides & Renovation Intelligence | The Buyer's Math",
        "desc": "In-depth, data-backed guides to navigating contractor estimates, federal tax incentives, and material ROI."
    }
}


def build_social_tags(title, desc, rel_url, is_article=False):
    og_type = "article" if is_article else "website"
    full_url = f"https://thebuyersmath.com/{rel_url.lstrip('/')}"
    og_img = "https://thebuyersmath.com/og-image.svg"

    return f"""  <!-- OpenGraph / Social Meta Tags -->
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="The Buyer's Math">
  <meta property="og:url" content="{full_url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{og_img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">

  <!-- Twitter Card Meta Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{og_img}">"""


def enhance_html_file(filepath, meta=None, is_article=False):
    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if og:image is already present
    if "property=\"og:image\"" in content or "property='og:image'" in content:
        return

    rel_name = os.path.relpath(filepath, ".").replace("\\", "/")

    title = ""
    desc = ""
    if meta:
        title = meta.get("title", "")
        desc = meta.get("desc", "")

    if not title:
        m_title = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        title = m_title.group(1).strip() if m_title else "The Buyer's Math"

    if not desc:
        m_desc = re.search(r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']", content, re.IGNORECASE)
        desc = m_desc.group(1).strip() if m_desc else "Independent, data-driven home renovation financial calculators."

    tags_block = build_social_tags(title, desc, rel_name, is_article=is_article)

    # Inject right before </head>
    if "</head>" in content:
        content = content.replace("</head>", f"{tags_block}\n</head>", 1)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Enhanced social tags: {filepath}")


def main():
    print("Applying OpenGraph and Twitter Card social metadata across the site...")

    # 1. Calculators and Core Pages
    for fname, meta in CALCULATOR_METADATA.items():
        if os.path.exists(fname):
            enhance_html_file(fname, meta=meta, is_article=False)

    # 2. Standalone Guides
    guides_dir = "guides"
    if os.path.exists(guides_dir):
        for fname in os.listdir(guides_dir):
            if fname.endswith(".html"):
                enhance_html_file(os.path.join(guides_dir, fname), is_article=True)

    # 3. Daily Articles
    articles_dir = "articles"
    if os.path.exists(articles_dir):
        for fname in os.listdir(articles_dir):
            if fname.endswith(".html"):
                enhance_html_file(os.path.join(articles_dir, fname), is_article=True)

    print("Completed OpenGraph and Twitter card deployment.")


if __name__ == "__main__":
    main()
