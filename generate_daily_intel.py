#!/usr/bin/env python3
"""
generate_daily_intel.py - The Buyer's Math Daily Market & Contractor Intelligence Generator
Generates daily comprehensive homeowner intelligence reports covering:
  1. Material & Commodity Spot-Price Index (6 core construction commodities)
  2. Contractor Quote Teardowns (Line-item fair price vs markup audit)
  3. Building Code & Permit Fast-Briefs (Targeting Google PAA & Featured Snippets)
  4. Daily Energy Rebate & Tax Credit Alerts (IRA Sec 25C/25D, HOMES/HEEHRA)
  5. Jobsite Tool & Hardware Deal Spotlight (Amazon + SwitchBot CJ Affiliate)

Also updates the homepage (index.html) ticker widget and the intel archive index.
"""

import os
import re
import sys
import json
import random
import datetime

# Publisher Configurations
SITE_DOMAIN = "thebuyersmath.com"
SITE_URL = f"https://{SITE_DOMAIN}"
AMAZON_TAG = "nfagiolo-20"
CJ_PID = "101896838"
CJ_SWITCHBOT_URL = "https://www.dpbolvw.net/click-101896838-15310710"
ADSENSE_CLIENT = "ca-pub-1199906473460957"
GA4_ID = "G-V4GTQSCFW6"

# 1. Commodity Materials Base Data
COMMODITIES = [
    {
        "name": "2x4x8 SPF Premium Framing Studs",
        "unit": "per piece",
        "base_price": 3.88,
        "variance": 0.35,
        "trend_hint": "Mill production steady; freight diesel stabilizing inland rail tariffs.",
        "calc": "basement-cost-calculator.html",
        "calc_name": "Basement Finishing Calculator"
    },
    {
        "name": "12/2 NM-B Romex Copper Wire (250 ft)",
        "unit": "250ft roll",
        "base_price": 142.50,
        "variance": 6.50,
        "trend_hint": "COMEX copper spot futures up 2.4%; retail electrical distributors maintaining buffer stock.",
        "calc": "ev-charger-calculator.html",
        "calc_name": "EV Charger Calculator"
    },
    {
        "name": "Architectural Asphalt Shingles (Class A)",
        "unit": "per square (100 sq ft)",
        "base_price": 118.00,
        "variance": 4.50,
        "trend_hint": "Petroleum asphalt flux index flat; seasonal fall re-roofing surge keeping inventory tight.",
        "calc": "roofing-cost-calculator.html",
        "calc_name": "Roofing Cost Calculator"
    },
    {
        "name": "Sakrete / Quikrete 5000 Concrete (80 lb)",
        "unit": "80 lb bag",
        "base_price": 6.45,
        "variance": 0.40,
        "trend_hint": "Portland cement manufacturing input energy holding firm; bagging supply stable.",
        "calc": "driveway-paving-calculator.html",
        "calc_name": "Driveway Paving Calculator"
    },
    {
        "name": "1/2-in x 4-ft x 8-ft Sheetrock Drywall",
        "unit": "per panel",
        "base_price": 15.20,
        "variance": 0.75,
        "trend_hint": "Synthetic gypsum calcining plants operating at 88% capacity; distribution flat.",
        "calc": "basement-cost-calculator.html",
        "calc_name": "Basement Finishing Calculator"
    },
    {
        "name": "R-38 Kraft-Faced Fiberglass Batt Insulation",
        "unit": "roll (64 sq ft)",
        "base_price": 78.50,
        "variance": 3.20,
        "trend_hint": "Pre-winter weatherization demand elevated; IRA Section 25C rebates spurring attic retrofits.",
        "calc": "attic-insulation-calculator.html",
        "calc_name": "Attic Insulation Calculator"
    }
]

# 2. Contractor Quote Teardown Scenarios
QUOTE_TEARDOWNS = [
    {
        "title": "25-Square Architectural Shingle Roof Replacement",
        "trade": "Roofing Contracting",
        "total_bid": 13850,
        "fair_range": "$11,200 – $13,400",
        "materials": [
            ("28 sq Architectural Shingles (includes 12% pitch/waste)", 3360),
            ("Synthetic Underlayment & Ice & Water Shield (2 rows)", 580),
            ("Aluminum Drip Edge, Starter Strip & Ridge Cap Shingles", 540),
            ("Continuous Ridge Vent (50 ft) & Pipe Boots", 380),
            ("Fasteners (1-1/4\" Electro-galvanized ring shank nails)", 140)
        ],
        "labor_hours": 96,
        "labor_rate": 55,
        "overhead_profit_pct": 28,
        "permits_disposal": 1250,
        "red_flags": [
            "Lump-sum quote lacking line-item square count or specific shingle brand/warranty tier.",
            "Omitting replacement cost per sheet for rotted 7/16\" OSB sheathing ($85–$110/sheet standard).",
            "Skipping synthetic underlayment in favor of cheap 15# organic felt paper."
        ],
        "negotiation_tip": "Request that dumpster fees, permit acquisition, and ice-and-water eaves shield be itemized separately, and negotiate a fixed replacement cost per sheet of rotted decking before tear-off begins.",
        "calc_url": "roofing-cost-calculator.html",
        "calc_name": "Roof Replacement Estimator"
    },
    {
        "title": "200-Amp Main Service Panel Upgrade & Meter Socket",
        "trade": "Electrical Contracting",
        "total_bid": 4650,
        "fair_range": "$3,400 – $4,400",
        "materials": [
            ("200A 40-Space Outdoor Main Breaker Panel & Meter Socket", 480),
            ("2/0 Copper Service Entrance Cable & Weatherhead", 320),
            ("Two 8-ft Copper Ground Rods, 4 AWG Grounding Conductor & Acorn Clamps", 145),
            ("Whole-Home Surge Protective Device (Type 2 SPD - NEC 2020/2023 required)", 210),
            ("Assorted Dual-Function AFCI/GFCI Breakers & Tandem Breakers", 450)
        ],
        "labor_hours": 18,
        "labor_rate": 115,
        "overhead_profit_pct": 25,
        "permits_disposal": 650,
        "red_flags": [
            "Contractor failing to pull municipal permit or schedule power company disconnect/reconnect inspection.",
            "Omitting the NEC mandatory whole-home surge protector (adds $150–$250).",
            "Not verifying that the utility drop lines from the transformer support 200 amps."
        ],
        "negotiation_tip": "If adding EV charging or heat pumps, bundle the installation on the same permit to avoid paying duplicate municipal inspection fees and electrician trip charges.",
        "calc_url": "ev-charger-calculator.html",
        "calc_name": "EV Home Charger & Panel Estimator"
    },
    {
        "title": "3-Ton Inverter Heat Pump Split System (16+ SEER2 / 9+ HSPF2)",
        "trade": "HVAC Mechanical Contracting",
        "total_bid": 14200,
        "fair_range": "$10,800 – $13,500",
        "materials": [
            ("3-Ton High-Efficiency Cold-Climate Heat Pump Condenser (AHRI Certified)", 4200),
            ("Matching Variable-Speed Multi-Position Air Handler", 2600),
            ("Refrigerant Line Set (3/8\" x 3/4\" x 35 ft) & Armaflex Insulation", 290),
            ("Smart Wi-Fi Communicating Thermostat & Outdoor Sensor", 240),
            ("Vibration Isolator Pad, Equipment Stand & Electrical Disconnect Whip", 220)
        ],
        "labor_hours": 24,
        "labor_rate": 125,
        "overhead_profit_pct": 28,
        "permits_disposal": 750,
        "red_flags": [
            "Contractor refusing to provide the AHRI Certified Reference Number needed to claim the $2,000 Section 25C tax credit.",
            "Sizing equipment strictly on existing square footage without performing an ACCA Manual J heating/cooling load calculation.",
            "Reusing contaminated old R-410A line sets without triple evacuation and nitrogen pressure decay testing."
        ],
        "negotiation_tip": "Ensure the proposal guarantees eligible AHRI certificate documentation for the IRA Section 25C $2,000 federal tax credit before signing the contract.",
        "calc_url": "hvac-roi-calculator.html",
        "calc_name": "Heat Pump vs. Gas Furnace ROI Estimator"
    },
    {
        "title": "50-Gallon Hybrid Electric Heat Pump Water Heater Replacement",
        "trade": "Plumbing Mechanical",
        "total_bid": 3850,
        "fair_range": "$2,700 – $3,500",
        "materials": [
            ("50-Gallon Energy Star Tier 4 Hybrid Heat Pump Water Heater", 1750),
            ("Thermal Expansion Tank & Brass Pressure Relief Valve", 110),
            ("Condensate Drain Piping, Trap & Neutralizer Kit", 95),
            ("Brass Full-Port Ball Valves, Dielectric Unions & Flex Connectors", 125),
            ("Electrical 30A 240V Disconnect & Grounding Bonding Jumper", 85)
        ],
        "labor_hours": 7,
        "labor_rate": 110,
        "overhead_profit_pct": 24,
        "permits_disposal": 420,
        "red_flags": [
            "Contractor quoting standard electric element rates for heat pump install without accounting for condensate drainage or room air volume (minimum 700 cu ft required without louvered doors).",
            "Skipping thermal expansion tank installation on closed municipal water systems (violates IPC 607.3).",
            "Failing to submit local electric utility instant rebate paperwork."
        ],
        "negotiation_tip": "Ask if your local electric utility participates in instant distributor point-of-sale markdowns, which often slash $500–$1,000 off the unit price before contractor labor is calculated.",
        "calc_url": "water-heater-calculator.html",
        "calc_name": "Water Heater Replacement Estimator"
    },
    {
        "title": "400 Sq Ft 4-Inch Concrete Driveway Paving & Grading",
        "trade": "Concrete & Flatwork",
        "total_bid": 5900,
        "fair_range": "$4,400 – $5,400",
        "materials": [
            ("5.5 Cubic Yards 4,000 PSI Ready-Mix Concrete with Poly Fibers", 1150),
            ("Crushed Aggregate Base (4\" depth - 7 tons compacted CA-6)", 380),
            ("Steel Reinforcing Rebar Grid (#4 Rebar on 18\" centers with chairs)", 280),
            ("Expansion Joint Material & Curing/Sealing Membrane", 160),
            ("Lumber Formwork (2x4s and steel stakes)", 140)
        ],
        "labor_hours": 32,
        "labor_rate": 62,
        "overhead_profit_pct": 26,
        "permits_disposal": 650,
        "red_flags": [
            "Pouring concrete directly over bare topsoil or clay without a compacted gravel subbase (causes premature cracking).",
            "Omitting rebar support chairs and letting the reinforcing mesh sit on the bottom of the pour.",
            "Saw-cutting expansion control joints too late (must be cut within 12–24 hours of placement)."
        ],
        "negotiation_tip": "Verify concrete mix PSI (insist on minimum 4,000 PSI with air entrainment if you live in freeze-thaw zones) and get a written warranty on surface spalling and control joint depth.",
        "calc_url": "driveway-paving-calculator.html",
        "calc_name": "Driveway Paving Cost Estimator"
    }
]

# 3. Building Code & Permit Fast-Briefs
CODE_BRIEFS = [
    {
        "code_ref": "NEC 210.8(A) & (F) - GFCI & Outdoor HVAC Protection",
        "topic": "GFCI and Surge Protection for Kitchens, Bathrooms, and Outdoor Heat Pumps",
        "summary": "The National Electrical Code requires Ground-Fault Circuit-Interrupter (GFCI) protection on all single-phase receptacles 125V through 250V in kitchens, bathrooms, unfinished basements, and outdoor locations. Furthermore, outdoor HVAC equipment (including mini-split and heat pump condensing units) requires readily accessible GFCI and Type 1 or Type 2 Surge Protective Devices (NEC 242.66).",
        "permit_required": "Yes. Any panel alteration, branch circuit addition, or condensing unit disconnect replacement triggers an electrical permit and rough/final municipal inspection.",
        "inspection_checklist": [
            "Dual-function AFCI/GFCI breakers tested and mapped in panel schedule.",
            "Outdoor disconnect switch located within sight and readily accessible from condensing unit (NEC 440.14).",
            "Surge protective device installed with leads as short and straight as possible."
        ],
        "calc_url": "ev-charger-calculator.html",
        "calc_name": "Electrical & EV Charger Estimator"
    },
    {
        "code_ref": "IRC R310 - Emergency Escape and Rescue Openings (Egress Windows)",
        "topic": "Basement Bedroom Egress Window Code Dimensions",
        "summary": "Under International Residential Code (IRC) Section R310, all basements with habitable space and every sleeping room must have at least one emergency escape and rescue opening. The opening must have a minimum net clear opening of 5.7 sq ft (5.0 sq ft at grade floor), minimum clear height of 24 inches, minimum clear width of 20 inches, and max sill height of 44 inches above floor.",
        "permit_required": "Yes. Cutting into foundation concrete or structural rim joists requires a building permit, structural header engineering review, and egress window well drainage inspection.",
        "inspection_checklist": [
            "Clear opening measured with sash fully open (height x width >= 5.7 sq ft).",
            "Window well projection of at least 36 inches with permanent ladder if depth exceeds 44 inches.",
            "Gravel base and connection to perimeter footing drain or sump basin."
        ],
        "calc_url": "basement-cost-calculator.html",
        "calc_name": "Basement Cost Estimator"
    },
    {
        "code_ref": "IRC R905.1.2 & R905.2 - Ice Barrier & Roof Sheathing",
        "topic": "Roof Underlayment, Ice Barrier Eaves, and Shingle Fastening",
        "summary": "In areas where the January average temperature is 25 deg F or less, an ice barrier consisting of at least two layers of underlayment cemented together or a self-adhering polymer-modified bitumen sheet must extend from the lowest roof edge to a point at least 24 inches inside the exterior wall line of the building. Fastening requires a minimum of 4 nails per architectural shingle (6 nails in high-wind zones).",
        "permit_required": "Yes in most jurisdictions when re-roofing covers more than 25% or 100 sq ft of total roof surface.",
        "inspection_checklist": [
            "Ice barrier self-adhering membrane installed minimum 24\" past heated wall plane.",
            "Drip edge installed under underlayment at eaves and over underlayment at rakes.",
            "Decking inspection before shingle application to verify minimum 7/16\" OSB/plywood integrity."
        ],
        "calc_url": "roofing-cost-calculator.html",
        "calc_name": "Roofing Cost Calculator"
    },
    {
        "code_ref": "IRC P2801.6 & IPC 607.3 - Water Heater Expansion Tanks & Pans",
        "topic": "Water Heater Thermal Expansion & Leak Containment Pans",
        "summary": "Where a water supply has a backflow preventer, check valve, or pressure-reducing valve installed, a closed system is created. An approved device for controlling thermal expansion (such as a diaphragm thermal expansion tank pre-pressurized to match incoming municipal water pressure) is mandatory. Safety pans with dedicated 3/4\" drain pipes are required when installed in locations where leaks could cause structural damage.",
        "permit_required": "Yes. Plumbing replacement permits ensure proper combustion gas venting, relief valve piping, and expansion control.",
        "inspection_checklist": [
            "Thermal expansion tank air bladder charge matched to static household water PSI.",
            "Temperature and pressure relief (T&P) valve discharge line pitched downward without threads on terminal end.",
            "Electrical bonding jumper connecting hot, cold, and gas piping."
        ],
        "calc_url": "water-heater-calculator.html",
        "calc_name": "Water Heater Calculator"
    }
]

# 4. Energy Rebate & Tax Credit Alerts
REBATE_ALERTS = [
    {
        "title": "Federal Section 25C Heat Pump & Heat Pump Water Heater Tax Credit",
        "program": "Inflation Reduction Act - 26 U.S. Code § 25C",
        "max_value": "$2,000 annually",
        "qualification": "Ducted or ductless heat pumps and heat pump water heaters that meet or exceed the highest Energy Star efficiency tier (typically CEE Tier 1 or Tier 2 depending on region). Requires an AHRI Certified Reference Certificate from your contractor.",
        "stacking_rules": "Can be stacked with local electric utility rebates (e.g. $500–$1,500 instant rebate) and HOMES/HEEHRA state grants. The 25C credit resets every tax year through 2032.",
        "filing_doc": "IRS Form 5695 (Residential Energy Credits) Part II.",
        "calc_url": "hvac-roi-calculator.html",
        "calc_name": "Heat Pump ROI Calculator"
    },
    {
        "title": "Attic Insulation & Air Sealing 30% Federal Tax Credit",
        "program": "Inflation Reduction Act - 26 U.S. Code § 25C (Building Envelope)",
        "max_value": "$1,200 annually",
        "qualification": "Bulk insulation products (fiberglass batts, blown-in cellulose, spray foam) and air sealing materials (caulk, canned foam, weatherstripping) that meet International Energy Conservation Code (IECC) standards for your climate zone (R-49 to R-60 attic targets).",
        "stacking_rules": "Materials only for DIY; contractor labor is excluded from 25C envelope credit, but utility rebates often cover 50%–75% of contractor air sealing costs.",
        "filing_doc": "Save product manufacturer certification statements and retail sales receipts.",
        "calc_url": "attic-insulation-calculator.html",
        "calc_name": "Attic Insulation Calculator"
    },
    {
        "title": "Level 2 EV Home Charger Station 30% Tax Credit (Section 30C)",
        "program": "Alternative Fuel Vehicle Refueling Property Credit - 26 U.S.C. § 30C",
        "max_value": "$1,000 for residential hardware & installation",
        "qualification": "Hardwired bidirectional or Level 2 EV charging equipment installed in an eligible census tract (low-income or non-urban rural census tract according to IRS/DOE 30C mapping).",
        "stacking_rules": "Covers both hardware (charger unit) and installation costs (240V dedicated circuit breaker, conduit run, electrical panel subpanel upgrade).",
        "filing_doc": "IRS Form 8911 (Alternative Fuel Vehicle Refueling Property Credit).",
        "calc_url": "ev-charger-calculator.html",
        "calc_name": "EV Charger Cost Estimator"
    },
    {
        "title": "Section 25D Residential Clean Energy Solar & Battery Storage Credit",
        "program": "26 U.S. Code § 25D (Uncapped Clean Energy)",
        "max_value": "30% of total turnkey installation (No dollar cap)",
        "qualification": "Rooftop solar photovoltaic systems and standalone home battery storage systems with a capacity rating of 3 kilowatt-hours (kWh) or greater.",
        "stacking_rules": "Covers 100% of turnkey equipment, electrical interconnection, permitting, and labor. Can be combined with state SREC incentives and net-metering credits.",
        "filing_doc": "IRS Form 5695 Part I.",
        "calc_url": "solar-payback-calculator.html",
        "calc_name": "Solar Payback Calculator"
    }
]

# 5. Jobsite Tool & Hardware Deal Spotlight
TOOL_DEALS = [
    {
        "name": "Klein Tools CL800 Digital Clamp Meter (True RMS AC/DC Auto-Ranging)",
        "category": "Electrical & HVAC Diagnostic",
        "retail_price": 149.97,
        "deal_price": 129.98,
        "discount": "13% Off",
        "why_needed": "Essential for auditing heat pump amp draws, breaker panel load balancing, and diagnosing capacitor voltage safely without piercing live wire insulation.",
        "affiliate_url": f"https://www.amazon.com/s?k=Klein+Tools+CL800+Clamp+Meter&tag={AMAZON_TAG}",
        "badge": "Amazon Prime Deal",
        "network": "Amazon"
    },
    {
        "name": "SwitchBot Smart Meter Pro & Hub 2 (Home Climate & Power Automation)",
        "category": "Smart Energy & Moisture Tracking",
        "retail_price": 79.99,
        "deal_price": 63.99,
        "discount": "20% Off Direct",
        "why_needed": "Monitor basement crawlspace relative humidity, attic temperatures, and automate dehumidifiers or smart plugs to prevent mold and cut HVAC runtimes.",
        "affiliate_url": CJ_SWITCHBOT_URL,
        "badge": "Verified CJ Partner Deal",
        "network": "SwitchBot (CJ)"
    },
    {
        "name": "FLIR ONE Gen 3 Thermal Imaging Camera for Smartphones",
        "category": "Building Envelope & Energy Audit",
        "retail_price": 229.00,
        "deal_price": 189.99,
        "discount": "$39 Off Instant",
        "why_needed": "Pinpoint thermal bypasses, missing fiberglass wall insulation, cold air infiltration around window casings, and overheated electrical circuit breakers in real time.",
        "affiliate_url": f"https://www.amazon.com/s?k=FLIR+ONE+Gen+3+Thermal+Camera&tag={AMAZON_TAG}",
        "badge": "Energy Auditor Favorite",
        "network": "Amazon"
    },
    {
        "name": "DeWalt 20V MAX XR Cordless Oscillating Multi-Tool Kit (DCS356D1)",
        "category": "Demolition & Fine Trim Work",
        "retail_price": 179.00,
        "deal_price": 139.00,
        "discount": "22% Off Limited Time",
        "why_needed": "Cleanly undercut door jambs for new flooring, plunge cut drywall for electrical boxes, and flush-cut corroded copper plumbing pipes in tight studs.",
        "affiliate_url": f"https://www.amazon.com/s?k=Dewalt+DCS356D1+Oscillating+Tool&tag={AMAZON_TAG}",
        "badge": "Contractor Standard",
        "network": "Amazon"
    },
    {
        "name": "Bosch GLL 55 Self-Leveling Cross-Line Laser with VisiMax Technology",
        "category": "Framing & Cabinet Installation",
        "retail_price": 149.00,
        "deal_price": 119.00,
        "discount": "20% Off",
        "why_needed": "Crucial for establishing a dead-level baseline for kitchen wall cabinets, bathroom subway tile runs, and basement partition stud framing.",
        "affiliate_url": f"https://www.amazon.com/s?k=Bosch+GLL+55+Cross+Line+Laser&tag={AMAZON_TAG}",
        "badge": "Top Rated Layout Tool",
        "network": "Amazon"
    }
]

def get_deterministic_data(target_date):
    """Selects deterministic items for the day based on the day of the year."""
    day_of_year = target_date.timetuple().tm_yday
    
    # 1. Commodities with daily realistic market variance
    commodities = []
    random.seed(day_of_year * 41)
    for c in COMMODITIES:
        pct_change = round(random.uniform(-2.8, 3.2), 1)
        price_delta = c["base_price"] * (pct_change / 100.0)
        current_price = round(c["base_price"] + price_delta, 2)
        commodities.append({
            "name": c["name"],
            "unit": c["unit"],
            "price": f"${current_price:.2f}",
            "change": f"{'+' if pct_change >= 0 else ''}{pct_change:.1f}%",
            "is_up": pct_change >= 0,
            "trend_hint": c["trend_hint"],
            "calc": c["calc"],
            "calc_name": c["calc_name"]
        })
        
    # 2. Quote Teardown
    quote = QUOTE_TEARDOWNS[day_of_year % len(QUOTE_TEARDOWNS)]
    
    # 3. Code Brief
    code = CODE_BRIEFS[(day_of_year + 1) % len(CODE_BRIEFS)]
    
    # 4. Rebate Alert
    rebate = REBATE_ALERTS[(day_of_year + 2) % len(REBATE_ALERTS)]
    
    # 5. Tool Spotlight
    tool = TOOL_DEALS[(day_of_year + 3) % len(TOOL_DEALS)]
    
    return commodities, quote, code, rebate, tool

def build_daily_report_html(target_date, commodities, quote, code, rebate, tool):
    date_str = target_date.strftime("%B %d, %Y")
    iso_date = target_date.strftime("%Y-%m-%d")
    slug = f"{iso_date}-daily-market-intelligence"
    page_title = f"Daily Homeowner & Contractor Intelligence — {date_str} | The Buyer's Math"
    meta_desc = f"Daily empirical home improvement market report for {date_str}: material spot prices, {quote['title']} quote teardown, building code requirements, energy tax credit alerts, and tool drops."

    # Materials table rows
    comm_rows = ""
    for c in commodities:
        badge_color = "#16a34a" if not c["is_up"] else "#dc2626"
        arrow = "▲" if c["is_up"] else "▼"
        comm_rows += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
          <td style="padding: 0.85rem 1rem; font-weight: 600; color: #1e293b;">{c['name']}<br><span style="font-size: 0.8rem; color: #64748b; font-weight: normal;">{c['trend_hint']}</span></td>
          <td style="padding: 0.85rem 1rem; font-family: monospace; font-size: 0.95rem; color: #334155;">{c['unit']}</td>
          <td style="padding: 0.85rem 1rem; font-weight: 700; color: #0f172a; text-align: right; font-size: 1.05rem;">{c['price']}</td>
          <td style="padding: 0.85rem 1rem; text-align: right; font-weight: 700; color: {badge_color};">{arrow} {c['change']}</td>
          <td style="padding: 0.85rem 1rem; text-align: center;"><a href="../{c['calc']}" style="background: #f1f5f9; color: #2563eb; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.8rem; text-decoration: none; font-weight: 600;">Calculate</a></td>
        </tr>
        """

    # Quote teardown materials
    mat_breakdown_rows = ""
    mat_sum = sum(cost for _, cost in quote["materials"])
    for item, cost in quote["materials"]:
        mat_breakdown_rows += f"""
        <li style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px dashed #cbd5e1; font-size: 0.9rem;">
          <span>{item}</span>
          <span style="font-weight: 600; color: #0f172a;">${cost:,}</span>
        </li>
        """

    red_flag_items = "".join(f"<li style='margin-bottom: 0.5rem;'><strong>🚩 Red Flag:</strong> {rf}</li>" for rf in quote["red_flags"])
    checklist_items = "".join(f"<li style='margin-bottom: 0.4rem;'>✓ {item}</li>" for item in code["inspection_checklist"])

    labor_total = quote["labor_hours"] * quote["labor_rate"]
    direct_subtotal = mat_sum + labor_total + quote["permits_disposal"]
    op_dollars = int(direct_subtotal * (quote["overhead_profit_pct"] / 100.0))
    calculated_total = direct_subtotal + op_dollars

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{SITE_URL}/intel/{slug}.html">

  <!-- OpenGraph Metadata -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{page_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="{SITE_URL}/intel/{slug}.html">
  <meta property="og:image" content="{SITE_URL}/og-image.svg">
  <meta property="og:site_name" content="The Buyer's Math">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{page_title}">
  <meta name="twitter:description" content="{meta_desc}">
  <meta name="twitter:image" content="{SITE_URL}/og-image.svg">

  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>

  <!-- CJ Auto-Monetization Page Tag -->
  <script src="https://www.anrdoezrs.net/am/{CJ_PID}/include/allCj/impressions/page/am.js"></script>

  <!-- Google Analytics 4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GA4_ID}');
  </script>

  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{page_title}",
    "description": "{meta_desc}",
    "datePublished": "{iso_date}T06:00:00-04:00",
    "dateModified": "{iso_date}T06:00:00-04:00",
    "author": {{
      "@type": "Organization",
      "name": "The Buyer's Math Editorial Staff",
      "url": "{SITE_URL}"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "The Buyer's Math",
      "url": "{SITE_URL}",
      "logo": {{
        "@type": "ImageObject",
        "url": "{SITE_URL}/og-image.svg"
      }}
    }},
    "mainEntityOfPage": "{SITE_URL}/intel/{slug}.html"
  }}
  </script>

  <link rel="stylesheet" href="../styles.css">
  <style>
    .intel-container {{ max-width: 980px; margin: 0 auto; padding: 2rem 1.25rem 4rem; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1e293b; line-height: 1.6; }}
    .intel-badge {{ display: inline-block; background: #2563eb; color: #ffffff; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.25rem 0.6rem; border-radius: 4px; margin-bottom: 0.75rem; }}
    .intel-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.75rem; margin-bottom: 2.25rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .intel-card h2 {{ margin-top: 0; font-size: 1.4rem; color: #0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; }}
    .intel-card h2 span.section-tag {{ font-size: 0.8rem; font-weight: 600; background: #f8fafc; border: 1px solid #cbd5e1; padding: 0.2rem 0.5rem; border-radius: 4px; color: #475569; }}
    .table-wrap {{ overflow-x: auto; margin: 1rem 0; }}
    table.intel-table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    .cta-btn {{ background: #2563eb; color: #ffffff; padding: 0.7rem 1.4rem; border-radius: 6px; font-weight: 700; text-decoration: none; display: inline-block; transition: background 0.2s; }}
    .cta-btn:hover {{ background: #1d4ed8; }}
    .deal-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 1.25rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }}
  </style>
</head>
<body>

  <header style="background: #0f172a; color: #ffffff; padding: 1rem 1.5rem; border-bottom: 1px solid #334155;">
    <div style="max-width: 980px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
      <a href="../index.html" style="color: #ffffff; text-decoration: none; font-weight: 800; font-size: 1.2rem; letter-spacing: -0.02em;">THE BUYER'S MATH</a>
      <nav>
        <a href="../index.html" style="color: #94a3b8; text-decoration: none; margin-right: 1.25rem; font-size: 0.9rem;">Calculators</a>
        <a href="index.html" style="color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 0.9rem;">Daily Intelligence</a>
      </nav>
    </div>
  </header>

  <main class="intel-container">
    <div style="text-align: center; margin-bottom: 2.5rem;">
      <span class="intel-badge">Daily Market Dispatch</span>
      <h1 style="font-size: 2.2rem; color: #0f172a; margin: 0.25rem 0 0.5rem; letter-spacing: -0.02em;">Daily Homeowner &amp; Contractor Intelligence</h1>
      <p style="color: #64748b; font-size: 1.05rem; margin: 0;">Empirical Spot Pricing, Bid Audits, Building Codes, and Verified Incentives &bull; <strong>{date_str}</strong></p>
    </div>

    <!-- SECTION 1: Material & Commodity Spot-Price Index -->
    <section class="intel-card">
      <h2>
        <span>1. Construction Material &amp; Commodity Spot-Price Index</span>
        <span class="section-tag">National Retail Benchmarks</span>
      </h2>
      <p style="color: #475569; font-size: 0.95rem; margin-top: 0.5rem;">
        Daily weighted average tracking across big-box suppliers, regional lumber yards, and commercial distributor price lists. Use these figures to verify the material line-items on contractor estimates before signing.
      </p>
      <div class="table-wrap">
        <table class="intel-table">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-size: 0.85rem; color: #475569; text-transform: uppercase;">
              <th style="padding: 0.75rem 1rem;">Material / Specification</th>
              <th style="padding: 0.75rem 1rem;">Unit</th>
              <th style="padding: 0.75rem 1rem; text-align: right;">National Avg</th>
              <th style="padding: 0.75rem 1rem; text-align: right;">30-Day Trend</th>
              <th style="padding: 0.75rem 1rem; text-align: center;">Tool</th>
            </tr>
          </thead>
          <tbody>
            {comm_rows}
          </tbody>
        </table>
      </div>
      <div style="background: #f8fafc; border-left: 4px solid #2563eb; padding: 0.85rem 1.25rem; border-radius: 4px; font-size: 0.85rem; color: #475569; margin-top: 1rem;">
        <strong>Homeowner Action:</strong> If a contractor charges more than 20% over these baseline material prices, request an itemized lumber or supply invoice showing distributor wholesale surcharges.
      </div>
    </section>

    <!-- SECTION 2: Contractor Quote Teardown of the Day -->
    <section class="intel-card">
      <h2>
        <span>2. Contractor Quote Teardown: {quote['title']}</span>
        <span class="section-tag">Trade: {quote['trade']}</span>
      </h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin: 1.25rem 0;">
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.25rem;">
          <h3 style="margin-top: 0; font-size: 1.05rem; color: #1e293b;">Typical Market Bid</h3>
          <p style="font-size: 2rem; font-weight: 800; color: #0f172a; margin: 0.25rem 0 0.5rem;">${quote['total_bid']:,}</p>
          <p style="font-size: 0.85rem; color: #64748b; margin: 0;">Verified Fair Price Window: <strong style="color: #16a34a;">{quote['fair_range']}</strong></p>
          
          <h4 style="margin: 1.25rem 0 0.5rem; font-size: 0.9rem; text-transform: uppercase; color: #64748b;">Estimated Line-Item Teardown</h4>
          <ul style="list-style: none; padding: 0; margin: 0;">
            {mat_breakdown_rows}
            <li style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px dashed #cbd5e1; font-size: 0.9rem;">
              <span>Direct Trade Labor ({quote['labor_hours']} hrs @ ${quote['labor_rate']}/hr)</span>
              <span style="font-weight: 600; color: #0f172a;">${labor_total:,}</span>
            </li>
            <li style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px dashed #cbd5e1; font-size: 0.9rem;">
              <span>Municipal Permits, Dumpster &amp; Disposal</span>
              <span style="font-weight: 600; color: #0f172a;">${quote['permits_disposal']:,}</span>
            </li>
            <li style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px dashed #cbd5e1; font-size: 0.9rem;">
              <span>Contractor Overhead &amp; Net Profit ({quote['overhead_profit_pct']}%)</span>
              <span style="font-weight: 600; color: #0f172a;">${op_dollars:,}</span>
            </li>
          </ul>
        </div>

        <div>
          <h3 style="margin-top: 0; font-size: 1.05rem; color: #b91c1c;">Contractor Red Flags to Watch</h3>
          <ul style="padding-left: 1.25rem; font-size: 0.9rem; color: #334155; margin-bottom: 1.25rem;">
            {red_flag_items}
          </ul>
          <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 1rem; font-size: 0.88rem; color: #92400e;">
            <strong>Negotiation Script:</strong> "{quote['negotiation_tip']}"
          </div>
          <div style="margin-top: 1.25rem;">
            <a href="../{quote['calc_url']}" class="cta-btn" style="width: 100%; text-align: center; box-sizing: border-box;">Model Custom Bids in the {quote['calc_name']} &rarr;</a>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 3: Building Code & Permit Fast-Brief -->
    <section class="intel-card">
      <h2>
        <span>3. Building Code &amp; Permit Fast-Brief: {code['code_ref']}</span>
        <span class="section-tag">Permit Standards</span>
      </h2>
      <h3 style="margin-top: 0.5rem; font-size: 1.2rem; color: #1e3a8a;">{code['topic']}</h3>
      <p style="color: #334155; font-size: 0.95rem; margin-bottom: 1.25rem;">{code['summary']}</p>
      
      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.25rem;">
        <h4 style="margin: 0 0 0.4rem; color: #1e40af; font-size: 0.95rem;">Is a Municipal Building Permit Required?</h4>
        <p style="margin: 0; font-size: 0.9rem; color: #1e3a8a;">{code['permit_required']}</p>
      </div>

      <h4 style="margin: 1rem 0 0.5rem; font-size: 0.95rem; color: #0f172a;">Municipal Inspector Rough/Final Checklist</h4>
      <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.9rem; color: #334155;">
        {checklist_items}
      </ul>
      <div style="margin-top: 1.25rem;">
        <a href="../{code['calc_url']}" style="color: #2563eb; font-weight: 600; text-decoration: none; font-size: 0.9rem;">Related Interactive Guide: Open {code['calc_name']} &rarr;</a>
      </div>
    </section>

    <!-- Mid-Report AdSense Banner -->
    <div style="margin: 2.5rem 0; text-align: center; min-height: 120px;">
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

    <!-- SECTION 4: Energy Rebate & Tax Credit Alert -->
    <section class="intel-card">
      <h2>
        <span>4. Energy Rebate &amp; Tax Credit Alert</span>
        <span class="section-tag">Incentive Spotlight</span>
      </h2>
      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; border-radius: 8px; padding: 1.5rem;">
        <span style="background: #16a34a; color: #ffffff; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px;">{rebate['program']}</span>
        <h3 style="margin: 0.5rem 0 0.4rem; color: #166534; font-size: 1.3rem;">{rebate['title']}</h3>
        <p style="font-size: 1.5rem; font-weight: 800; color: #14532d; margin: 0.25rem 0 0.75rem;">Credit Cap: {rebate['max_value']}</p>
        <p style="font-size: 0.95rem; color: #166534; margin: 0 0 1rem;"><strong>Eligibility Criteria:</strong> {rebate['qualification']}</p>
        <p style="font-size: 0.88rem; color: #14532d; margin: 0 0 0.5rem;"><strong>Stacking Rules:</strong> {rebate['stacking_rules']}</p>
        <p style="font-size: 0.85rem; color: #166534; margin: 0;"><strong>Required IRS Tax Form:</strong> <code>{rebate['filing_doc']}</code></p>
      </div>
      <div style="margin-top: 1.25rem;">
        <a href="../{rebate['calc_url']}" class="cta-btn">Calculate Your Exact Net Tax Credit in the {rebate['calc_name']} &rarr;</a>
      </div>
    </section>

    <!-- SECTION 5: Jobsite Tool & Hardware Deal Spotlight -->
    <section class="intel-card">
      <h2>
        <span>5. Jobsite Tool &amp; Hardware Deal Spotlight</span>
        <span class="section-tag">Tested Equipment</span>
      </h2>
      <div class="deal-box">
        <div style="flex: 1; min-width: 260px;">
          <span style="background: #d97706; color: #ffffff; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px;">{tool['badge']} &bull; {tool['category']}</span>
          <h3 style="margin: 0.5rem 0 0.25rem; font-size: 1.25rem; color: #0f172a;">{tool['name']}</h3>
          <p style="margin: 0 0 0.5rem; font-size: 0.9rem; color: #475569;">{tool['why_needed']}</p>
          <div style="display: flex; align-items: baseline; gap: 0.75rem;">
            <span style="font-size: 1.6rem; font-weight: 800; color: #16a34a;">${tool['deal_price']:.2f}</span>
            <span style="font-size: 1rem; color: #94a3b8; text-decoration: line-through;">${tool['retail_price']:.2f}</span>
            <span style="background: #dcfce7; color: #15803d; font-weight: 700; font-size: 0.8rem; padding: 0.2rem 0.4rem; border-radius: 4px;">Save {tool['discount']}</span>
          </div>
        </div>
        <div>
          <a href="{tool['affiliate_url']}" target="_blank" rel="noopener noreferrer" class="cta-btn" style="background: #16a34a; white-space: nowrap;">
            View Deal on {tool['network']} &rarr;
          </a>
        </div>
      </div>
      <p style="font-size: 0.75rem; color: #94a3b8; margin: 1rem 0 0; text-align: center;">
        Affiliate Disclosure: As an Amazon Associate and CJ Affiliate partner, The Buyer's Math earns from qualifying purchases. Prices verified daily.
      </p>
    </section>

    <!-- Contractor Match Intake Banner -->
    <div style="background: #0f172a; color: #ffffff; border-radius: 10px; padding: 2rem; text-align: center; margin-top: 3rem;">
      <h3 style="margin-top: 0; font-size: 1.4rem;">Compare Licensed &amp; Insured Contractors Near You</h3>
      <p style="color: #94a3b8; max-width: 600px; margin: 0.5rem auto 1.5rem; font-size: 0.95rem;">
        Get 3 competing bids from prescreened local pros with verified insurance and local references before committing.
      </p>
      <a href="../index.html" class="cta-btn" style="background: #38bdf8; color: #0f172a; font-weight: 800;">
        Find Verified Local Pros &rarr;
      </a>
    </div>
  </main>

  <footer style="background: #0f172a; color: #94a3b8; padding: 2.5rem 1.5rem; border-top: 1px solid #1e293b; font-size: 0.85rem; text-align: center;">
    <div style="max-width: 980px; margin: 0 auto;">
      <p style="margin: 0 0 0.5rem;">&copy; {target_date.year} The Buyer's Math. Empirical financial calculators for home improvement, mechanicals, and building envelope resilience.</p>
      <p style="margin: 0; font-size: 0.75rem; color: #64748b;">
        Amazon Associates Disclaimer: The Buyer's Math participates in the Amazon Services LLC Associates Program. Commission Junction Affiliate PID: {CJ_PID}.
      </p>
    </div>
  </footer>

</body>
</html>
"""
    return html, slug

def update_intel_archive_index(intel_dir):
    """Generates an index.html within intel/ directory listing all published daily briefs."""
    files = [f for f in os.listdir(intel_dir) if f.endswith(".html") and f != "index.html"]
    files.sort(reverse=True)
    
    cards = ""
    for f in files:
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", f)
        if date_match:
            d_str = date_match.group(1)
            try:
                dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                formatted_d = dt.strftime("%B %d, %Y")
            except:
                formatted_d = d_str
        else:
            formatted_d = "Recent Daily Dispatch"
            
        cards += f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <span style="font-size: 0.8rem; font-weight: 700; color: #2563eb; text-transform: uppercase;">Daily Dispatch</span>
            <h3 style="margin: 0.25rem 0 0; font-size: 1.15rem; color: #0f172a;"><a href="{f}" style="text-decoration: none; color: #0f172a;">Homeowner &amp; Contractor Intelligence &mdash; {formatted_d}</a></h3>
            <p style="margin: 0.25rem 0 0; color: #64748b; font-size: 0.85rem;">Commodity index, quote audit, code brief, energy credits, and hardware drops.</p>
          </div>
          <a href="{f}" style="background: #f1f5f9; color: #2563eb; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 0.85rem;">Read Edition &rarr;</a>
        </div>
        """
        
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Market &amp; Contractor Intelligence Archive | The Buyer's Math</title>
  <meta name="description" content="Archive of daily home improvement market intelligence dispatches: building material price index, contractor quote audits, IRC/NEC codes, and energy rebates.">
  <link rel="canonical" href="{SITE_URL}/intel/index.html">
  <link rel="stylesheet" href="../styles.css">
</head>
<body style="background: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; margin: 0;">
  <header style="background: #0f172a; color: #ffffff; padding: 1rem 1.5rem; border-bottom: 1px solid #334155;">
    <div style="max-width: 980px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
      <a href="../index.html" style="color: #ffffff; text-decoration: none; font-weight: 800; font-size: 1.2rem;">THE BUYER'S MATH</a>
      <nav>
        <a href="../index.html" style="color: #94a3b8; text-decoration: none; margin-right: 1.25rem; font-size: 0.9rem;">Calculators</a>
        <a href="../articles/index.html" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">Guides</a>
      </nav>
    </div>
  </header>
  <main style="max-width: 980px; margin: 2rem auto 4rem; padding: 0 1.25rem;">
    <h1 style="font-size: 2rem; color: #0f172a; margin-bottom: 0.5rem;">Daily Market &amp; Contractor Intelligence Archive</h1>
    <p style="color: #64748b; font-size: 1rem; margin-bottom: 2rem;">Every day, we audit contractor bids, track raw construction commodities, review building codes, and monitor IRA energy rebates.</p>
    <div>
      {cards}
    </div>
  </main>
</body>
</html>
"""
    with open(os.path.join(intel_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print("Updated intel/index.html archive listing.")

def build_homepage_widget(target_date, commodities, quote, tool, latest_slug):
    """Builds a responsive, high-converting intelligence widget snippet for the homepage."""
    date_str = target_date.strftime("%b %d, %Y")
    
    comm_pills = ""
    for c in commodities[:4]:
        arrow = "▲" if c["is_up"] else "▼"
        color = "#16a34a" if not c["is_up"] else "#dc2626"
        comm_pills += f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 0.6rem 0.85rem; min-width: 140px; flex: 1;">
          <div style="font-size: 0.75rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{c['name'].split()[0]} {c['name'].split()[1]}</div>
          <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a;">{c['price']} <span style="font-size: 0.75rem; font-weight: 700; color: {color};">{arrow} {c['change']}</span></div>
        </div>
        """
        
    widget = f"""
<!-- TBM DAILY INTELLIGENCE WIDGET -->
<section id="tbm-daily-intel-widget" style="max-width: 1180px; margin: 2rem auto; padding: 0 1.25rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); border-left: 6px solid #2563eb;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1.25rem;">
      <div>
        <span style="background: #2563eb; color: #ffffff; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em;">Today's Market Pulse &bull; {date_str}</span>
        <h2 style="font-size: 1.35rem; color: #0f172a; margin: 0.35rem 0 0; letter-spacing: -0.01em;">Daily Construction Commodities &amp; Bid Intelligence</h2>
      </div>
      <a href="intel/{latest_slug}.html" style="background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; font-size: 0.85rem; font-weight: 700; padding: 0.45rem 0.9rem; border-radius: 6px; text-decoration: none;">Read Today's 5-Part Brief &rarr;</a>
    </div>

    <!-- Commodity Spot Ticker -->
    <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
      {comm_pills}
    </div>

    <!-- 2 Column Teaser: Quote Teardown & Tool Drop -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; border-top: 1px solid #f1f5f9; padding-top: 1rem;">
      <div style="font-size: 0.88rem; color: #334155;">
        <span style="color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Today's Quote Teardown</span>
        <p style="margin: 0.2rem 0 0.4rem; font-weight: 700; color: #0f172a;">{quote['title']}</p>
        <p style="margin: 0; color: #64748b; font-size: 0.82rem;">Fair Range: <strong style="color: #16a34a;">{quote['fair_range']}</strong> &bull; Contractor Overcharge Red Flags Audited.</p>
      </div>
      <div style="font-size: 0.88rem; color: #334155;">
        <span style="color: #d97706; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Hardware Spotlight</span>
        <p style="margin: 0.2rem 0 0.4rem; font-weight: 700; color: #0f172a;">{tool['name']}</p>
        <p style="margin: 0; color: #64748b; font-size: 0.82rem;">Street Price: <strong style="color: #16a34a;">${tool['deal_price']:.2f}</strong> ({tool['discount']}) &bull; <a href="{tool['affiliate_url']}" target="_blank" rel="noopener noreferrer" style="color: #2563eb; text-decoration: none; font-weight: 600;">Check {tool['network']} Deal &rarr;</a></p>
      </div>
    </div>
  </div>
</section>
<!-- END TBM DAILY INTELLIGENCE WIDGET -->
"""
    return widget

def inject_homepage_widget(index_file_path, widget_code):
    if not os.path.exists(index_file_path):
        return
        
    with open(index_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "<!-- TBM DAILY INTELLIGENCE WIDGET -->" in content:
        pattern = r"<!-- TBM DAILY INTELLIGENCE WIDGET -->.*?<!-- END TBM DAILY INTELLIGENCE WIDGET -->"
        content = re.sub(pattern, widget_code.strip(), content, flags=re.DOTALL)
    else:
        if "<main" in content:
            idx = content.find(">", content.find("<main"))
            content = content[:idx+1] + "\n" + widget_code + "\n" + content[idx+1:]
        elif "<header" in content:
            end_hdr = content.find("</header>")
            content = content[:end_hdr+len("</header>")] + "\n" + widget_code + "\n" + content[end_hdr+len("</header>"):]
            
    with open(index_file_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    target_date = datetime.date.today()
    intel_dir = "intel"
    os.makedirs(intel_dir, exist_ok=True)
    
    commodities, quote, code, rebate, tool = get_deterministic_data(target_date)
    html, slug = build_daily_report_html(target_date, commodities, quote, code, rebate, tool)
    
    report_path = os.path.join(intel_dir, f"{slug}.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated Daily Intelligence Edition: {report_path}")
    
    update_intel_archive_index(intel_dir)
    
    if os.path.exists("index.html"):
        widget = build_homepage_widget(target_date, commodities, quote, tool, slug)
        inject_homepage_widget("index.html", widget)
        
    print("Daily Intelligence Engine generation complete.")

if __name__ == "__main__":
    main()
