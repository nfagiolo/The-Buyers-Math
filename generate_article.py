# generate_article.py
# The Buyer's Math - Daily Automated Guide Engine (Option B: Enhanced Monetization & Deduplication)
# Features:
# 1. Anti-Collision & Deduplication Engine (Tracks published archive, ensures 100% unique angles)
# 2. Category Balancing (Round-Robin Least-Recently-Used selection across all 16 calculators)
# 3. 7 Rotating Editorial Angles (Material Head-to-Head, Code/Permits, Tax Credits, Line-Item Labor, DIY vs Pro, Resale ROI, Diagnostics)
# 4. Dynamic Anthropic Claude Model Selection (Prevents 404 deprecation errors)
# 5. Multi-Network Monetization (CJ Affiliate SwitchBot + Amazon Associates + Angi Contractor Leads + AdSense)
# 6. Automatic Updates to index.html and sitemap.xml

import os
import re
import json
from datetime import datetime
import anthropic

AMAZON_TAG = "nfagiolo-20"
ADSENSE_CLIENT = "ca-pub-1199906473460957"
CJ_PID = "101896838"

CALCULATORS = [
    {"name": "Roof Replacement Cost Estimator", "url": "../roofing-cost-calculator.html", "key": "roofing-cost-calculator.html", "category": "Roofing", "keywords": ["roof", "roofing", "shingles", "decking"]},
    {"name": "Heat Pump vs. Gas Furnace ROI", "url": "../hvac-roi-calculator.html", "key": "hvac-roi-calculator.html", "category": "HVAC", "keywords": ["hvac", "heat pump", "furnace", "heating", "cooling"]},
    {"name": "Attic Insulation & Air Sealing ROI", "url": "../attic-insulation-calculator.html", "key": "attic-insulation-calculator.html", "category": "Insulation", "keywords": ["attic", "insulation", "air sealing", "baffles"]},
    {"name": "Bathroom Remodel Cost Estimator", "url": "../bathroom-remodel-calculator.html", "key": "bathroom-remodel-calculator.html", "category": "Bathroom Remodeling", "keywords": ["bathroom", "remodel", "tile", "shower", "vanity"]},
    {"name": "EV Home Charger Installation", "url": "../ev-charger-calculator.html", "key": "ev-charger-calculator.html", "category": "Electrical", "keywords": ["ev charger", "electric vehicle", "level 2", "conduit", "240v"]},
    {"name": "Fence Cost & Linear Footage Estimator", "url": "../fence-cost-calculator.html", "key": "fence-cost-calculator.html", "category": "Fencing", "keywords": ["fence", "fencing", "privacy fence", "cedar", "vinyl fence"]},
    {"name": "Home Siding Replacement Cost", "url": "../siding-cost-calculator.html", "key": "siding-cost-calculator.html", "category": "Siding", "keywords": ["siding", "vinyl siding", "hardie", "fiber cement"]},
    {"name": "Kitchen Remodel Cost Estimator", "url": "../kitchen-remodel-calculator.html", "key": "kitchen-remodel-calculator.html", "category": "Kitchen Remodeling", "keywords": ["kitchen", "cabinets", "countertops", "remodel"]},
    {"name": "Solar Panel Payback Timeline", "url": "../solar-payback-calculator.html", "key": "solar-payback-calculator.html", "category": "Solar", "keywords": ["solar", "panels", "clean energy", "inverter"]},
    {"name": "Basement Finishing Cost Estimator", "url": "../basement-cost-calculator.html", "key": "basement-cost-calculator.html", "category": "Basement Remodeling", "keywords": ["basement", "framing", "sump pump", "drywall"]},
    {"name": "Driveway Paving Calculator", "url": "../driveway-paving-calculator.html", "key": "driveway-paving-calculator.html", "category": "Paving & Concrete", "keywords": ["driveway", "asphalt", "concrete", "paving"]},
    {"name": "Window Replacement Estimator", "url": "../window-replacement-estimator.html", "key": "window-replacement-estimator.html", "category": "Windows", "keywords": ["windows", "window replacement", "glazing", "drafts"]},
    {"name": "Ductless Mini-Split Cost Estimator", "url": "../mini-split-calculator.html", "key": "mini-split-calculator.html", "category": "HVAC", "keywords": ["mini-split", "ductless", "heat pump"]},
    {"name": "Backup Generator Sizing Guide", "url": "../generator-calculator.html", "key": "generator-calculator.html", "category": "Generator & Electrical", "keywords": ["generator", "backup power", "standby", "transfer switch"]},
    {"name": "Water Heater Replacement Cost", "url": "../water-heater-calculator.html", "key": "water-heater-calculator.html", "category": "Plumbing", "keywords": ["water heater", "tankless", "heat pump water heater"]},
    {"name": "Pool Pump Energy Calculator", "url": "../pool.html", "key": "pool.html", "category": "Pool Maintenance", "keywords": ["pool", "pump", "variable speed", "filtration"]}
]

EDITORIAL_ANGLES = [
    "Material Comparison & Durability Tradeoffs (Head-to-head comparison of standard vs premium materials, lifespan vs upfront cost)",
    "Hidden Costs, Code Compliance & Inspection Requirements (Concealed damage, rough-in requirements, municipal building codes, permit fees)",
    "Federal Tax Incentives, Rebates & Inflation Reduction Act Rules (Section 25C, Section 30C, utility peak demand rebates, qualification criteria)",
    "Labor vs. Material Line-Item Pricing Breakdown (Itemized trade labor rates, scaffolding, equipment staging, dumpster fees, contractor markup)",
    "DIY vs. Licensed Professional Trade Boundaries (What homeowners can legally and safely do vs where licensed master trades are strictly required)",
    "Long-Term Resale Value & Cost vs. Value Appraisal Impact (Real estate ROI, appraisal equity boost, buyer appeal vs cost recovery)",
    "Regional Climate Performance & Failure Diagnostics (Freeze-thaw cycles, moisture vapor barriers, high-heat efficiency thresholds, preventative maintenance)"
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
            {"title": "SwitchBot Indoor/Outdoor Thermo-Hygrometer (Attic Climate Monitor)", "price": "$17.99", "rating": "4.7 ★ (4,100+ reviews)", "cj_url": f"https://www.dpbolvw.net/click-{CJ_PID}-15310710", "merchant": "SwitchBot Official"}
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
            {"title": "SwitchBot Smart Hygrometer & Moisture Sensor (Subfloor & Humidity)", "price": "$14.99", "rating": "4.6 ★ (3,200+ reviews)", "cj_url": f"https://www.dpbolvw.net/click-{CJ_PID}-15310710", "merchant": "SwitchBot Official"}
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
            {"title": "SwitchBot Solar-Powered Smart Curtain Automator (Thermal Glazing Control)", "price": "$89.99", "rating": "4.5 ★ (2,800+ reviews)", "cj_url": f"https://www.dpbolvw.net/click-{CJ_PID}-15310710", "merchant": "SwitchBot Official"}
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
            {"title": "SwitchBot 15A Smart Plug with Live Energy & Wattage Monitor", "price": "$14.99", "rating": "4.6 ★ (1,800+ reviews)", "cj_url": f"https://www.dpbolvw.net/click-{CJ_PID}-15310710", "merchant": "SwitchBot Official"}
        ]
    }
}


def slugify(text, max_len=60):
    text = text.lower()
    slug = re.sub(r'[\W_]+', '-', text).strip('-')
    if len(slug) > max_len:
        slug = slug[:max_len].rsplit('-', 1)[0]
    return slug


def calculate_title_similarity(t1, t2):
    """Calculates Jaccard keyword overlap to prevent semantic duplicate topics."""
    stop_words = {'how', 'much', 'does', 'cost', 'in', '2026', 'the', 'a', 'an', 'and', 'vs', 'to', 'for', 'of', 'is'}
    w1 = set(re.findall(r'\w+', t1.lower())) - stop_words
    w2 = set(re.findall(r'\w+', t2.lower())) - stop_words
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def get_existing_articles():
    """Scans articles directory and index.html to build the historical title/slug archive."""
    existing = []

    # 1. Inspect articles directory
    if os.path.exists("articles"):
        for fname in os.listdir("articles"):
            if fname.endswith(".html"):
                path = os.path.join("articles", fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        txt = f.read()
                    m = re.search(r"<title>(.*?)</title>", txt, re.IGNORECASE)
                    title = m.group(1).replace("| The Buyer's Math", "").strip() if m else fname
                    slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', fname.replace('.html', ''))
                    existing.append({"filename": fname, "title": title, "slug": slug})
                except Exception:
                    pass

    # 2. Inspect index.html
    if os.path.exists("index.html"):
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                idx_txt = f.read()
            matches = re.findall(r'href="articles/([^"]+)">(.*?)</a>', idx_txt)
            for href_file, link_title in matches:
                clean_title = re.sub(r'<[^>]+>', '', link_title).strip()
                slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', href_file.replace('.html', ''))
                if not any(e["slug"] == slug for e in existing):
                    existing.append({"filename": href_file, "title": clean_title, "slug": slug})
        except Exception:
            pass

    return existing


def select_target_calculator_and_angle(existing_articles):
    """Balanced Round-Robin: Selects the calculator with the least existing coverage, paired with a rotating angle."""
    counts = {c["key"]: 0 for c in CALCULATORS}

    for art in existing_articles:
        lower_t = art["title"].lower()
        for c in CALCULATORS:
            if any(kw in lower_t for kw in c["keywords"]):
                counts[c["key"]] += 1

    # Sort calculators by least covered
    sorted_calcs = sorted(CALCULATORS, key=lambda c: counts[c["key"]])
    target_calc = sorted_calcs[0]

    # Select angle based on total number of articles published
    angle_idx = len(existing_articles) % len(EDITORIAL_ANGLES)
    target_angle = EDITORIAL_ANGLES[angle_idx]

    return target_calc, target_angle


def select_active_model(client):
    """Dynamically queries Anthropic API for active models to prevent deprecation 404s."""
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


def build_curated_gear_html(gear_info):
    category = gear_info.get("category", "Home Improvement")
    items = gear_info.get("items", [])
    if not items:
        return ""

    items_html = ""
    for item in items:
        item_url = item.get("cj_url") or f"https://www.amazon.com/s?k={item.get('query', '')}&tag={AMAZON_TAG}"
        is_cj = bool(item.get("cj_url"))
        btn_label = "View on SwitchBot &rarr;" if is_cj else "Check Deal on Amazon &rarr;"
        btn_bg = "#059669" if is_cj else "#d97706"
        badge_label = item.get("merchant") or "Amazon Associates"

        items_html += f"""
          <div style="background: #ffffff; border: 1px solid #fef3c7; border-radius: 8px; padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem;">
            <div style="flex: 1; min-width: 220px;">
              <h4 style="margin: 0 0 0.25rem 0; font-size: 0.975rem; color: #0f172a; line-height: 1.4;">{item['title']}</h4>
              <div style="font-size: 0.85rem; color: #d97706; font-weight: 600;">{item['rating']} &bull; <span style="color: #0f172a; font-weight: 700;">{item['price']}</span> &bull; <span style="color: #64748b; font-size: 0.78rem;">{badge_label}</span></div>
            </div>
            <a href="{item_url}" target="_blank" rel="noopener noreferrer" style="background: {btn_bg}; color: #ffffff; padding: 0.6rem 1.15rem; border-radius: 6px; font-weight: 700; font-size: 0.875rem; text-decoration: none; white-space: nowrap; display: inline-flex; align-items: center; gap: 0.35rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
              {btn_label}
            </a>
          </div>
        """

    return f"""
      <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 1.75rem; margin: 2rem 0; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
          <span style="background: #f59e0b; color: #ffffff; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em;">Contractor-Grade Equipment</span>
          <span style="font-size: 0.75rem; color: #92400e; font-style: italic;">Verified Retail &amp; Partner Pricing</span>
        </div>
        <h3 style="margin: 0.25rem 0 0.5rem 0; color: #92400e; font-size: 1.15rem;">Recommended {category} Tools &amp; Materials</h3>
        <p style="margin: 0 0 0.5rem 0; color: #78350f; font-size: 0.9rem;">
          Compare live contractor pricing, consumer ratings, and verified specs before ordering supplies:
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

    # Step 1: Scan Existing Articles for Collision & Deduplication Guard
    existing_articles = get_existing_articles()
    existing_titles = [a["title"] for a in existing_articles]
    existing_slugs = [a["slug"] for a in existing_articles]
    print(f"Detected {len(existing_articles)} existing articles in site archive.")

    target_calc, target_angle = select_target_calculator_and_angle(existing_articles)
    print(f"Targeting category: {target_calc['name']} via Angle: {target_angle}")

   # Build anti-repetition corpus prompt
    recent_titles_str = "\n".join([f"- {t}" for t in existing_titles[-25:]]) if existing_titles else "None (Initial publication)"

    topic_prompt = (
        f"Generate a completely unique, highly specific, high-intent 2026 homeowner cost analysis title focusing on: {target_calc['name']}.\n"
        f"Editorial Lens to use: {target_angle}\n\n"
        f"STRICT CONSTRAINTS:\n"
        f"1. Title Length: Between 6 and 10 words (MAXIMUM 70 characters). Never output run-on sentences.\n"
        f"2. Anti-Duplication: You MUST NOT duplicate or closely mimic any previously published title below:\n"
        f"{recent_titles_str}\n\n"
        f"Format strictly as: Title\n"
        f"Example: 2026 Architectural Shingle vs Metal: 30-Year Roof Math"
    )

    # Retry loop to guarantee zero collisions
    title = ""
    slug = ""
    for attempt in range(3):
        candidate_title = call_claude(client, model_name, topic_prompt, max_tokens=30).strip().strip('"')
        candidate_slug = slugify(candidate_title)

        is_duplicate = False
        if candidate_slug in existing_slugs:
            is_duplicate = True
        else:
            for past_t in existing_titles:
                if calculate_title_similarity(candidate_title, past_t) > 0.60:
                    is_duplicate = True
                    break

        if not is_duplicate:
            title = candidate_title
            slug = candidate_slug
            break
        else:
            print(f"Attempt {attempt+1}: Duplicate or high similarity detected for '{candidate_title}'. Retrying...")
            topic_prompt += f"\nAvoid this exact rejected title: {candidate_title}\n"

    if not title:
        title = f"{date_str} {target_calc['name']} Analysis: 2026 Pricing Guide"
        slug = slugify(title)

    print(f"Final Unique Topic Selected: {title} (slug: {slug})")

    calc_key = target_calc["key"]
    gear_info = TRADE_GEAR.get(calc_key, TRADE_GEAR["roofing-cost-calculator.html"])
    category_name = gear_info.get("category", target_calc.get("category", "Home Improvement"))

    # Step 2: Generate Authoritative 800-Word Content
    content_prompt = f"""Write an informative, authoritative, highly empirical 800-word homeowner's guide for: "{title}".

Requirements:
1. Provide realistic 2026 cost ranges (materials, licensed trade labor, permits, contingency buffers).
2. Ground the guide in empirical data, building codes, and regional variables.
3. Format cleanly using HTML: <h2>, <h3>, <p>, <ul>, <li>, and <table> where relevant. Do NOT include <html>, <head>, or <body> tags.
4. Reference and hyperlink naturally to the companion calculator: <a href="{target_calc['url']}">{target_calc['name']}</a>.
5. Provide a clear DIY vs. Professional Contractor breakdown with safety and warranty considerations.
6. Conclude with an FAQ section (3 questions using <details> and <summary> tags).
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
        <a href="{target_calc['url']}" style="background: #2563eb; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 700; text-decoration: none; display: inline-block;">Open the {target_calc['name']} &rarr;</a>
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
  <script async src="https://www.anrdoezrs.net/am/{CJ_PID}/include/allCj/impressions/page/am.js"></script>
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
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program and the CJ Affiliate Network. As an affiliate partner, I earn from qualifying purchases and verified referrals. Calculations and tool results are directional models for informational purposes only.
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

 # Update index.html (Consolidated Trade Hub Grid)
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            idx_content = f.read()

        article_rel_url = f"articles/{date_str}-{slug}.html"
           if article_rel_url not in idx_content:
            calc_cat = target_calc.get("category", "")
            if calc_cat in ["Roofing", "Insulation", "Windows", "Siding", "Fencing", "Paving & Concrete", "Decks", "Gutters", "Garage Doors", "Painting"]:
                cat_slug = "envelope"
                badge_title = "Building Envelope"
            elif calc_cat in ["Bathroom Remodeling", "Kitchen Remodeling", "Basement Remodeling", "Electrical", "Generator & Electrical"]:
                cat_slug = "interior"
                badge_title = "Interior & Power"
            else:
                cat_slug = "mechanical"
                badge_title = "Mechanical & Energy"

            summary_snippet = meta_desc if 'meta_desc' in locals() and meta_desc else "Detailed empirical cost breakdown, licensed labor pricing, building code requirements, and contractor bid verification."
            if len(summary_snippet) > 170:
                summary_snippet = summary_snippet[:167].rsplit(" ", 1)[0] + "..."

            new_card = f'''        <div class="calculator-grid" id="guides-grid" style="padding-bottom: 1rem;">
      <!-- Guide: {title} -->
      <a href="/{article_rel_url}" class="calc-card guide-card" data-guide-category="featured {cat_slug}">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #2563eb; background: #eff6ff; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;">{badge_title}</span>
            <span style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">{date_str}</span>
          </div>
          <h3 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; line-height: 1.4; color: #0f172a;">{title}</h3>
          <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0 0 1.25rem 0;">{summary_snippet}</p>
        </div>
        <span class="cta-link" style="color: #2563eb; font-weight: 600; font-size: 0.9rem;">Read Guide &rarr;</span>
      </a>'''

            grid_target = '<div class="calculator-grid" id="guides-grid" style="padding-bottom: 1rem;">'
            if grid_target in idx_content:
                idx_content = idx_content.replace(grid_target, new_card, 1)
                with open("index.html", "w", encoding="utf-8") as f:
                    f.write(idx_content)
                print("Updated index.html guides grid with new card.")

    # Update guides.html
    if os.path.exists("guides.html"):
        with open("guides.html", "r", encoding="utf-8") as f:
            guides_content = f.read()

        if article_rel_url not in guides_content:
            guide_card_entry = f"""    <div class="guides-grid" id="guides-grid">
      <!-- Guide: {title} -->
      <article class="guide-card" data-category="{cat_slug}">
        <div class="guide-card-header">
          <span class="guide-badge">{badge_title}</span>
          <span class="guide-date">{date_str}</span>
        </div>
        <h2 class="guide-title"><a href="/{article_rel_url}">{title}</a></h2>
        <p class="guide-desc">{summary_snippet}</p>
        <a href="/{article_rel_url}" class="guide-read-link">Read Full Guide &rarr;</a>
      </article>"""
            if '<div class="guides-grid" id="guides-grid">' in guides_content:
                guides_content = guides_content.replace('<div class="guides-grid" id="guides-grid">', guide_card_entry, 1)
                with open("guides.html", "w", encoding="utf-8") as f:
                    f.write(guides_content)
                print("Updated guides.html with new article card.")

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
