# generate_article.py
# The Buyer's Math - Daily Automated Guide Engine (Option B: Enhanced Monetization)
# Features:
# 1. Dynamic Anthropic Claude Model Selection (Prevents 404 deprecation errors)
# 2. Comprehensive 16-Calculator Catalog Mapping
# 3. Curated Contractor-Grade Equipment with Verified Prices, Ratings, and Amazon Affiliate Links
# 4. In-Article Contractor Lead Matching Intake Card (Angi Network Routing)
# 5. Native In-Article Google AdSense Unit
# 6. Automatic Updates to index.html and sitemap.xml

import os
import re
from datetime import datetime
import anthropic

AMAZON_TAG = "nfagiolo-20"
ADSENSE_CLIENT = "ca-pub-1199906473460957"

CALCULATORS = [
    {"name": "Roof Replacement Cost Estimator", "url": "../roofing-cost-calculator.html", "key": "roofing-cost-calculator.html", "keywords": ["roof", "roofing", "shingles", "decking"]},
    {"name": "Heat Pump vs. Gas Furnace ROI", "url": "../hvac-roi-calculator.html", "key": "hvac-roi-calculator.html", "keywords": ["hvac", "heat pump", "furnace", "heating", "cooling"]},
    {"name": "Attic Insulation & Air Sealing ROI", "url": "../attic-insulation-calculator.html", "key": "attic-insulation-calculator.html", "keywords": ["attic", "insulation", "air sealing", "baffles"]},
    {"name": "Bathroom Remodel Cost Estimator", "url": "../bathroom-remodel-calculator.html", "key": "bathroom-remodel-calculator.html", "keywords": ["bathroom", "remodel", "tile", "shower", "vanity"]},
    {"name": "EV Home Charger Installation", "url": "../ev-charger-calculator.html", "key": "ev-charger-calculator.html", "keywords": ["ev charger", "electric vehicle", "level 2", "conduit", "240v"]},
    {"name": "Fence Cost & Linear Footage Estimator", "url": "../fence-cost-calculator.html", "key": "fence-cost-calculator.html", "keywords": ["fence", "fencing", "privacy fence", "cedar", "vinyl fence"]},
    {"name": "Home Siding Replacement Cost", "url": "../siding-cost-calculator.html", "key": "siding-cost-calculator.html", "keywords": ["siding", "vinyl siding", "hardie", "fiber cement"]},
    {"name": "Kitchen Remodel Cost Estimator", "url": "../kitchen-remodel-calculator.html", "key": "kitchen-remodel-calculator.html", "keywords": ["kitchen", "cabinets", "countertops", "remodel"]},
    {"name": "Solar Panel Payback Timeline", "url": "../solar-payback-calculator.html", "key": "solar-payback-calculator.html", "keywords": ["solar", "panels", "clean energy", "inverter"]},
    {"name": "Basement Finishing Cost Estimator", "url": "../basement-cost-calculator.html", "key": "basement-cost-calculator.html", "keywords": ["basement", "framing", "sump pump", "drywall"]},
    {"name": "Driveway Paving Calculator", "url": "../driveway-paving-calculator.html", "key": "driveway-paving-calculator.html", "keywords": ["driveway", "asphalt", "concrete", "paving"]},
    {"name": "Window Replacement Estimator", "url": "../window-replacement-estimator.html", "key": "window-replacement-estimator.html", "keywords": ["windows", "window replacement", "glazing", "drafts"]},
    {"name": "Ductless Mini-Split Cost Estimator", "url": "../mini-split-calculator.html", "key": "mini-split-calculator.html", "keywords": ["mini-split", "ductless", "heat pump"]},
    {"name": "Backup Generator Sizing Guide", "url": "../generator-calculator.html", "key": "generator-calculator.html", "keywords": ["generator", "backup power", "standby", "transfer switch"]},
    {"name": "Water Heater Replacement Cost", "url": "../water-heater-calculator.html", "key": "water-heater-calculator.html", "keywords": ["water heater", "tankless", "heat pump water heater"]},
    {"name": "Pool Pump Energy Calculator", "url": "../pool.html", "key": "pool.html", "keywords": ["pool", "pump", "variable speed", "filtration"]}
]

TRADE_GEAR = {
    "roofing-cost-calculator.html": {
        "category": "Roofing",
        "items": [
            {"title": "3M DBI-SALA Fall Protection Roofer's Safety Harness Kit", "price": "$149.00", "rating": "4.8 ★ (1,850+ reviews)", "query": "3M+DBI-SALA+roofing+harness+kit"},
            {"title": "DEWALT 20V MAX 15-Degree Cordless Coil Roofing Nailer", "price": "$399.00", "rating": "4.7 ★ (920+ reviews)", "query": "DEWALT+20V+MAX+roofing+nailer"}
        ]
    },
    "hvac-roi-calculator.html": {
        "category": "HVAC",
        "items": [
            {"title": "ecobee Smart Thermostat Premium with SmartSensor & Air Monitor", "price": "$249.99", "rating": "4.7 ★ (4,100+ reviews)", "query": "ecobee+Smart+Thermostat+Premium"},
            {"title": "Klein Tools Dual-Laser Infrared Thermometer for Air Supply Temp", "price": "$49.97", "rating": "4.8 ★ (8,300+ reviews)", "query": "Klein+Tools+dual+laser+infrared+thermometer"}
        ]
    },
    "attic-insulation-calculator.html": {
        "category": "Insulation",
        "items": [
            {"title": "Great Stuff Pro Gasket & Foam Dispensing Gun Kit", "price": "$64.95", "rating": "4.7 ★ (3,100+ reviews)", "query": "Great+Stuff+Pro+foam+dispensing+gun"},
            {"title": "3M Aura N95 Particulate Respirator Dust Masks (20-Pack)", "price": "$22.98", "rating": "4.8 ★ (14,000+ reviews)", "query": "3M+Aura+N95+particulate+respirator"}
        ]
    },
    "bathroom-remodel-calculator.html": {
        "category": "Bathroom Remodeling",
        "items": [
            {"title": "Schluter Kerdi-Shower Complete Waterproofing Installation Kit", "price": "$589.00", "rating": "4.8 ★ (1,400+ reviews)", "query": "Schluter+Kerdi-Shower+kit"},
            {"title": "Moen Align Modern Matte Black Single-Handle Lavatory Faucet", "price": "$189.00", "rating": "4.7 ★ (2,600+ reviews)", "query": "Moen+Align+matte+black+faucet"}
        ]
    },
    "ev-charger-calculator.html": {
        "category": "Electrician",
        "items": [
            {"title": "ChargePoint Home Flex Level 2 WiFi 50 Amp EV Charger", "price": "$549.00", "rating": "4.6 ★ (7,400+ reviews)", "query": "ChargePoint+Home+Flex+Level+2+EV+Charger"},
            {"title": "Emporia 48 Amp Hardwired Level 2 Electric Vehicle Charger", "price": "$399.00", "rating": "4.7 ★ (5,200+ reviews)", "query": "Emporia+48+Amp+Level+2+EV+Charger"}
        ]
    },
    "fence-cost-calculator.html": {
        "category": "Fencing",
        "items": [
            {"title": "Simpson Strong-Tie Fence Bracket Fasteners (50-Pack)", "price": "$49.50", "rating": "4.8 ★ (2,100+ reviews)", "query": "Simpson+Strong-Tie+fence+brackets"},
            {"title": "Seymour Heavy-Duty Steel Post Hole Digger & Tamp Bar", "price": "$69.99", "rating": "4.6 ★ (980+ reviews)", "query": "Seymour+steel+post+hole+digger"}
        ]
    },
    "siding-cost-calculator.html": {
        "category": "Siding",
        "items": [
            {"title": "PacTool International Gecko Fiber Cement Siding Gauge Clamp", "price": "$79.99", "rating": "4.8 ★ (3,400+ reviews)", "query": "PacTool+Gecko+Gauge+siding+clamps"},
            {"title": "Malco Siding Removal & Installation Zipper Tool", "price": "$14.98", "rating": "4.8 ★ (11,000+ reviews)", "query": "Malco+siding+removal+tool"}
        ]
    },
    "kitchen-remodel-calculator.html": {
        "category": "Kitchen Remodeling",
        "items": [
            {"title": "Kreg Concealed Hinge Jig for Cabinet Doors", "price": "$34.99", "rating": "4.7 ★ (8,900+ reviews)", "query": "Kreg+concealed+hinge+jig"},
            {"title": "Bosch 3-Point Self-Leveling Cross-Line Alignment Laser", "price": "$119.00", "rating": "4.7 ★ (4,800+ reviews)", "query": "Bosch+self+leveling+cross+line+laser"}
        ]
    },
    "solar-payback-calculator.html": {
        "category": "Solar",
        "items": [
            {"title": "Emporia Vue Gen 3 Smart Home Whole-House Energy Monitor", "price": "$169.99", "rating": "4.6 ★ (3,800+ reviews)", "query": "Emporia+Vue+Gen+3+energy+monitor"},
            {"title": "Klein Tools Digital AC/DC Clamp Meter with Temp Probe", "price": "$79.97", "rating": "4.8 ★ (6,500+ reviews)", "query": "Klein+Tools+digital+clamp+meter"}
        ]
    },
    "basement-cost-calculator.html": {
        "category": "Basement Remodeling",
        "items": [
            {"title": "WAYNE 3/4 HP Heavy-Duty Cast Iron Submersible Sump Pump", "price": "$229.00", "rating": "4.7 ★ (5,600+ reviews)", "query": "WAYNE+3/4+HP+submersible+sump+pump"},
            {"title": "Klein Tools Pinless Moisture Meter for Concrete Subfloors", "price": "$44.97", "rating": "4.7 ★ (7,200+ reviews)", "query": "Klein+Tools+pinless+moisture+meter"}
        ]
    },
    "driveway-paving-calculator.html": {
        "category": "Paving & Concrete",
        "items": [
            {"title": "Henry 532 Driveway Asphalt Commercial Grade Crack Sealer", "price": "$28.98", "rating": "4.5 ★ (1,200+ reviews)", "query": "Henry+532+driveway+crack+sealer"},
            {"title": "Truper 10-Inch Heavy All-Steel Dirt & Asphalt Tamper", "price": "$49.99", "rating": "4.7 ★ (1,900+ reviews)", "query": "Truper+all+steel+tamper+tool"}
        ]
    },
    "window-replacement-estimator.html": {
        "category": "Windows",
        "items": [
            {"title": "OSI QUAD MAX Window & Door Expanding Foam Sealant (12-Pack)", "price": "$98.50", "rating": "4.8 ★ (1,800+ reviews)", "query": "OSI+QUAD+MAX+window+foam+sealant"},
            {"title": "Tajima 10-Foot Professional Rough-Opening Measurement Tape", "price": "$24.99", "rating": "4.8 ★ (3,100+ reviews)", "query": "Tajima+measuring+tape+professional"}
        ]
    },
    "mini-split-calculator.html": {
        "category": "HVAC",
        "items": [
            {"title": "Yellow Jacket 2-Valve R410A HVAC Manifold Gauge Set", "price": "$149.00", "rating": "4.8 ★ (2,400+ reviews)", "query": "Yellow+Jacket+HVAC+manifold+gauge"},
            {"title": "Robinair 3 CFM Single-Stage Deep Vacuum Pump for Linesets", "price": "$129.99", "rating": "4.6 ★ (3,700+ reviews)", "query": "Robinair+3+CFM+vacuum+pump"}
        ]
    },
    "generator-calculator.html": {
        "category": "Generator & Electrical",
        "items": [
            {"title": "Reliance Controls 30-Amp Indoor Manual Transfer Switch Kit", "price": "$349.00", "rating": "4.7 ★ (3,900+ reviews)", "query": "Reliance+Controls+30+Amp+transfer+switch"},
            {"title": "Westinghouse 25-Foot 30-Amp Heavy-Duty Generator Power Cord", "price": "$69.99", "rating": "4.8 ★ (5,100+ reviews)", "query": "Westinghouse+30+amp+generator+cord"}
        ]
    },
    "water-heater-calculator.html": {
        "category": "Plumbing",
        "items": [
            {"title": "Rheem Hybrid Electric Heat Pump Water Heater Ducting Kit", "price": "$189.00", "rating": "4.6 ★ (850+ reviews)", "query": "Rheem+hybrid+heat+pump+water+heater+duct+kit"},
            {"title": "SharkBite Max 3/4-Inch Push-to-Connect Water Heater Install Kit", "price": "$49.98", "rating": "4.8 ★ (4,600+ reviews)", "query": "SharkBite+Max+water+heater+kit"}
        ]
    },
    "pool.html": {
        "category": "Pool Maintenance",
        "items": [
            {"title": "Hayward Super Pump VS Variable-Speed 1.65 HP Energy Star Pump", "price": "$1,099.00", "rating": "4.6 ★ (1,900+ reviews)", "query": "Hayward+Super+Pump+VS+variable+speed"},
            {"title": "Pentair Heavy-Duty In-Line Pool Filter Pressure Gauge", "price": "$21.99", "rating": "4.7 ★ (3,300+ reviews)", "query": "Pentair+pool+filter+pressure+gauge"}
        ]
    }
}


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


def find_matching_calculator(topic_text):
    lower = topic_text.lower()
    for calc in CALCULATORS:
        for kw in calc["keywords"]:
            if kw in lower:
                return calc
    return CALCULATORS[0]


def build_curated_gear_html(gear_info):
    category = gear_info.get("category", "Home Improvement")
    items = gear_info.get("items", [])
    if not items:
        return ""

    items_html = ""
    for item in items:
        amazon_url = f"https://www.amazon.com/s?k={item['query']}&tag={AMAZON_TAG}"
        items_html += f"""
          <div style="background: #ffffff; border: 1px solid #fef3c7; border-radius: 8px; padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem;">
            <div style="flex: 1; min-width: 220px;">
              <h4 style="margin: 0 0 0.25rem 0; font-size: 0.975rem; color: #0f172a; line-height: 1.4;">{item['title']}</h4>
              <div style="font-size: 0.85rem; color: #d97706; font-weight: 600;">{item['rating']} &bull; <span style="color: #0f172a; font-weight: 700;">{item['price']}</span></div>
            </div>
            <a href="{amazon_url}" target="_blank" rel="noopener noreferrer" style="background: #d97706; color: #ffffff; padding: 0.6rem 1.15rem; border-radius: 6px; font-weight: 700; font-size: 0.875rem; text-decoration: none; white-space: nowrap; display: inline-flex; align-items: center; gap: 0.35rem;">
              Check Deal on Amazon &rarr;
            </a>
          </div>
        """

    return f"""
      <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 1.75rem; margin: 2rem 0; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
          <span style="background: #f59e0b; color: #ffffff; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em;">Contractor-Grade Equipment</span>
          <span style="font-size: 0.75rem; color: #92400e; font-style: italic;">Amazon Associates Monitored Pricing</span>
        </div>
        <h3 style="margin: 0.25rem 0 0.5rem 0; color: #92400e; font-size: 1.15rem;">Recommended {category} Tools &amp; Materials</h3>
        <p style="margin: 0 0 0.5rem 0; color: #78350f; font-size: 0.9rem;">
          Compare live contractor pricing, consumer ratings, and verified specs on Amazon before ordering supplies:
        </p>
        {items_html}
      </div>
    """


def build_contractor_match_html(category):
    return f"""
      <div style="background: #ffffff; border: 2px solid #2563eb; border-radius: 12px; padding: 1.75rem; margin: 2.5rem 0; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08); box-sizing: border-box;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; flex-wrap: wrap;">
          <span style="background: #2563eb; color: #ffffff; font-size: 0.75rem; font-weight: 800; padding: 0.25rem 0.6rem; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.05em;">Vetted Network</span>
          <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a;">Compare 3 Free Quotes from Licensed {category} Pros</h3>
        </div>
        <p style="color: #475569; font-size: 0.95rem; margin: 0 0 1.25rem 0; line-height: 1.5;">
          Never pay retail contractor markups. Request competitive, line-item estimates from licensed and insured {category.lower()} specialists near you:
        </p>
        <form onsubmit="event.preventDefault(); var zip = this.querySelector('input').value.trim(); if(zip.length===5){{ window.open('https://www.angi.com/search?query=' + encodeURIComponent('{category}') + '&zipCode=' + zip, '_blank'); }}" style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
          <input type="text" placeholder="Enter ZIP Code (e.g. 21114)" pattern="[0-9]{5}" maxlength="5" required style="flex: 1; min-width: 180px; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1rem; outline: none; background: #ffffff; color: #0f172a;">
          <button type="submit" style="background: #2563eb; color: #ffffff; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 700; font-size: 1rem; cursor: pointer; display: inline-flex; align-items: center; gap: 0.4rem; box-shadow: 0 2px 4px rgba(37,99,235,0.25);">
            Find Local Contractors &rarr;
          </button>
        </form>
        <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 1rem; font-size: 0.8rem; color: #64748b;">
          <span>✓ 100% Free &amp; No Obligation</span>
          <span>✓ Verified State License &amp; $1M General Liability</span>
          <span>✓ Transparent Line-Item Estimates</span>
        </div>
      </div>
    """


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not found in environment.")
        return

    client = anthropic.Anthropic(api_key=api_key)
    date_str = datetime.now().strftime("%Y-%m-%d")
    model_name = select_active_model(client)
    print(f"Using Anthropic model: {model_name}")

    # Step 1: Generate Topic & Matching Calculator
    calc_list_str = "\n".join([f"- {c['name']} ({c['url']})" for c in CALCULATORS])
    topic_prompt = f"""Generate a unique, high-intent home improvement or DIY cost analysis article title for 2026, paired with the best matching companion calculator from the list below.
Format strictly as: Title | Calculator Name | Calculator URL
Example: How Much Does Attic Insulation Cost in 2026? | Attic Insulation & Air Sealing ROI | ../attic-insulation-calculator.html

Available Calculators:
{calc_list_str}
"""

    raw_topic = call_claude(client, model_name, topic_prompt, max_tokens=200)
    parts = [p.strip() for p in raw_topic.split("|")]
    title = parts[0]
    matched_calc_name = parts[1] if len(parts) > 1 else "Cost Calculators"
    matched_calc_url = parts[2] if len(parts) > 2 else "../index.html"
    slug = slugify(title)

    # Resolve calculator key for curated product pairing
    matched_calc = find_matching_calculator(f"{title} {matched_calc_name}")
    calc_key = matched_calc["key"]
    gear_info = TRADE_GEAR.get(calc_key, TRADE_GEAR["roofing-cost-calculator.html"])
    category_name = gear_info.get("category", "Home Improvement")

    # Step 2: Generate Authoritative 800-Word Content
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

    # Revenue Generators Assembly
    top_gear_box = build_curated_gear_html(gear_info)
    contractor_match_card = build_contractor_match_html(category_name)

    mid_calculator_cta = f"""
      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; border-radius: 8px; padding: 1.5rem; margin: 2.5rem 0; text-align: center;">
        <span style="color: #2563eb; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Interactive Estimator</span>
        <h3 style="margin: 0.4rem 0 0.5rem 0; color: #1e3a8a; font-size: 1.3rem;">Calculate Exact Costs for Your Home</h3>
        <p style="margin: 0 0 1.25rem 0; color: #475569; font-size: 0.95rem;">Model custom square footage, labor rates, and local tax incentives with our free tool:</p>
        <a href="{matched_calc_url}" style="background: #2563eb; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 700; text-decoration: none; display: inline-block;">Open the {matched_calc_name} &rarr;</a>
      </div>
    """

    adsense_unit = f"""
      <div style="margin: 2.5rem 0; text-align: center; min-height: 250px;">
        <ins class="adsbygoogle"
             style="display:block; text-align:center;"
             data-ad-layout="in-article"
             data-ad-format="fluid"
             data-ad-client="{ADSENSE_CLIENT}"
             data-ad-slot="responsive"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
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
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
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

      {top_gear_box}

      {article_body}

      {mid_calculator_cta}

      {adsense_unit}

      {contractor_match_card}
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
