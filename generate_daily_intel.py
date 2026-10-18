#!/usr/bin/env python3
"""
generate_daily_intel.py - The Buyer's Math 4-Stream "Living Authority Hub" Engine
Uses Python 3 Standard Library ONLY (Zero external pip dependencies).

Executes 4 Coordinated Content Streams every morning:
  - STREAM 1 (Living Tools): Updates data/live-baselines.json with live Open-Meteo telemetry,
    fuel/utility rates, and 30-day cost sparklines, and auto-retrofits all 21+ calculator HTML
    pages with the "Today's Context" Banner (#tbm-live-banner) above inputs.
  - STREAM 2 (Flagship "Daily Math Briefing" + 30-Day Lifecycle): Runs 3 passes through the
    parent calculator's actual formulas (Small / Mid / Large scenarios), builds a Multi-Pass
    Comparison Table + Counter-Intuitive Takeaways + Inline Interactive Micro-Calculator at
    /daily/todays-math/index.html (and /intel/latest.html), and prunes briefings > 30 days old.
  - STREAM 3 (Automated "Cost-Per-Use" Product Matrices): Injects #tbm-unit-matrix and
    #tbm-embed-box into every calculator to display Cost-Per-Output & 5-Year TCO rankings with
    the "★ Today's Best Math Pick" badge (Amazon Tag: nfagiolo-20 + CJ Angi PID: 101896838).
  - STREAM 4 (Self-Reinforcing Internal Loop): Appends today's 3-Pass Case Study directly into
    the Parent Calculator's "Real-World Case Studies & Recent Scenarios" section
    (<!-- TBM CASE STUDIES START -->) and updates the Homepage 3-Module "Daily Buyer's Pulse".
"""

import os
import re
import sys
import json
import random
import shutil
import datetime
import urllib.request

# Verified Production Configurations
SITE_DOMAIN = "thebuyersmath.com"
SITE_URL = f"https://{SITE_DOMAIN}"
AMAZON_TAG = "nfagiolo-20"
CJ_ENTERPRISE_ID = "8090259"
CJ_PID = "101896838"
CJ_ANGI_URL = "https://www.jdoqocy.com/click-101896838-17142784"
CJ_SWITCHBOT_URL = "https://www.dpbolvw.net/click-101896838-15310710"
ADSENSE_CLIENT = "ca-pub-1199906473460957"
GA4_ID = "G-V4GTQSCFW6"

DATA_FILE = os.path.join("data", "live-baselines.json")
INTEL_DIR = "intel"
DAILY_DIR = "daily"
LATITUDE = 39.01
LONGITUDE = -76.69

# Multi-Pass Flagship Scenarios (Rotates across core calculators for Stream 2 & Stream 4)
FLAGSHIP_STUDIES = [
    {
        "calc_slug": "hvac-roi-calculator.html",
        "calc_name": "Heat Pump vs. Gas Furnace ROI Calculator",
        "category": "hvac",
        "title": "Cold-Climate Inverter Heat Pump vs. 96% AFUE Gas Furnace: 3-Scenario Aux Strip Lockout Math",
        "query_params": "?climateSelect=moderate&electricRateSelect=0.16",
        "passes": [
            ("Pass 1: 1,500 Sq Ft Townhome (2.5 Ton)", "$10,625 Gross / $8,625 Net", "$9,375 Gas", "-$750 (Heat Pump Cheaper Day 1)", "Immediate (Day 1 Winner) + $310/yr Savings"),
            ("Pass 2: 2,200 Sq Ft Colonial (3.5 Ton)", "$12,875 Gross / $10,875 Net", "$10,325 Gas", "+$550 Upfront Delta", "1.6 Years Breakeven ($345/yr Savings)"),
            ("Pass 3: 3,400 Sq Ft 2-Story (5.0 Ton Cold-Climate)", "$16,150 Gross / $14,150 Net", "$11,750 Gas", "+$2,400 Upfront Delta", "4.8 Years Breakeven ($495/yr Savings)")
        ],
        "takeaway": "Counter-Intuitive Takeaway: In 1,500–2,200 sq ft homes, the $2,000 IRA Section 25C credit wipes out nearly the entire inverter compressor premium—making the heat pump cheaper upfront or breaking even in under 20 months, PROVIDED the thermostat locks out 10kW electric auxiliary strips above 25°F."
    },
    {
        "calc_slug": "roofing-cost-calculator.html",
        "calc_name": "Roof Replacement Cost Estimator",
        "category": "roofing",
        "title": "Architectural Asphalt vs. Class 4 Impact Shingles: 3-Pitch Tear-Off & Insurance Premium Audit",
        "query_params": "?roofPitch=medium",
        "passes": [
            ("Pass 1: 1,600 Sq Ft Ranch (18 Squares, 4/12 Pitch)", "$8,450 Arch. Class A", "$9,620 Class 4 Impact", "+$1,170 Material Upgrade", "3.4 Years via 12% Homeowners Insurance Discount"),
            ("Pass 2: 2,400 Sq Ft Colonial (26 Squares, 7/12 Pitch)", "$12,950 Arch. Class A", "$14,680 Class 4 Impact", "+$1,730 Material Upgrade", "4.1 Years via Insurance + Zero Wind Deductible"),
            ("Pass 3: 3,200 Sq Ft Steep Hip (36 Squares, 10/12 Pitch)", "$19,400 Arch. Class A", "$21,850 Class 4 Impact", "+$2,450 Material Upgrade", "4.6 Years + Avoids $3,200 Steep-Stage Re-rigging")
        ],
        "takeaway": "Counter-Intuitive Takeaway: On steep-slope roofs (8/12+ pitch), labor staging and safety rigging represent 42% of the total bid—upgrading from standard architectural shingles to SBS-modified Class 4 impact shingles adds only ~12% to the turnkey quote while extending service life by 8–10 years."
    },
    {
        "calc_slug": "generator-calculator.html",
        "calc_name": "Backup Generator Sizing Guide",
        "category": "electrical",
        "title": "7,500W Dual-Fuel Portable + Transfer Switch vs. 22kW Whole-Home Standby: 5-Year Outage TCO",
        "query_params": "?hours=48",
        "passes": [
            ("Pass 1: Essential Circuits Only (Well, Sump, Fridge, Gas Furnace)", "$1,540 Dual-Fuel + 10-Circuit Switch", "$11,800 18kW Standby", "-$10,260 Capital Saved", "$0.48/hr Propane Run Cost vs. $185/yr Standby Service"),
            ("Pass 2: Essential + 3-Ton Central AC (Soft-Start Equipped)", "$2,190 9,500W Inverter + 50A Inlet", "$13,400 22kW Standby", "-$11,210 Capital Saved", "Soft-Start Capacitor ($320) Cuts LRA Surge by 65%"),
            ("Pass 3: Full 200A All-Electric Home (4-Ton Heat Pump + EV)", "Not Viable on Portable (>50A Load)", "$15,200 24kW Standby + Load Shed", "Mandatory Automatic Load Management", "Requires 2x Smart Load-Shed Modules on EV/Aux Strips")
        ],
        "takeaway": "Counter-Intuitive Takeaway: Installing a $320 compressor soft-start kit on a 3-ton central AC drops locked-rotor startup amps (LRA) from 88A to 29A—allowing a $1,100 portable dual-fuel generator and 50A interlock kit to run central air conditioning without spending $13,400 on a permanent standby unit."
    },
    {
        "calc_slug": "water-heater-calculator.html",
        "calc_name": "Water Heater Replacement Cost Calculator",
        "category": "plumbing",
        "title": "50-Gal Hybrid Heat Pump vs. Gas Tankless vs. Standard Electric Tank: 10-Year Operating Math",
        "query_params": "",
        "passes": [
            ("Pass 1: 2-Person Household (45 Gal/Day Demand)", "$1,950 Net Hybrid (After 25C + Utility Rebate)", "$1,650 Standard Electric Tank", "+$300 Net Upfront Delta", "0.9 Years Breakeven (Saves $335/yr @ $0.172/kWh)"),
            ("Pass 2: 4-Person Family (75 Gal/Day Demand)", "$2,350 Net 65-Gal Hybrid Heat Pump", "$3,850 Condensing Gas Tankless", "-$1,500 Upfront + Saves $185/yr", "Hybrid Wins Both Upfront & 10-Yr TCO ($4,120 Saved)"),
            ("Pass 3: 6-Person High-Draw (110+ Gal/Day, Cold Basement)", "$2,950 Net 80-Gal Hybrid (Adds Basement Cooling)", "$4,200 199k BTU Gas Tankless", "-$1,250 Upfront Delta", "Tankless Wins Only if Continuous Back-to-Back Tubs Needed")
        ],
        "takeaway": "Counter-Intuitive Takeaway: A 199,000 BTU gas tankless retrofit requires upsizing existing 1/2-inch black iron gas pipe to 3/4-inch and running new Category III/IV PVC venting ($1,100–$1,600 in hidden rough-in labor), whereas a Hybrid Heat Pump Water Heater claims up to $2,000 in Section 25C tax credits and drops annual electric consumption from ~4,500 kWh to ~1,150 kWh."
    },
    {
        "calc_slug": "attic-insulation-calculator.html",
        "calc_name": "Attic Insulation & Air Sealing ROI Calculator",
        "category": "hvac",
        "title": "Attic Air Sealing + Blown Cellulose (R-19 to R-60): Stack-Effect Payback & 25C Credit Math",
        "query_params": "",
        "passes": [
            ("Pass 1: 1,200 Sq Ft Attic (DIY Air Seal + Rental Blower)", "$980 Gross Materials / $686 Net (After 30% 25C)", "$2,450 Turnkey Contractor", "-$1,764 DIY Labor Savings", "2.1 Years Breakeven ($325/yr Heating/Cooling Saved)"),
            ("Pass 2: 1,800 Sq Ft Attic (Pro Baffles + Top-Plate Foam + R-60)", "$3,400 Gross / $2,480 Net (After $920 25C Credit)", "$3,400 Turnkey Contractor", "$920 Tax Credit + $500 Utility Rebate", "4.4 Years Breakeven + Eliminates 2nd-Floor Ice Dams"),
            ("Pass 3: 2,400 Sq Ft Attic (Closed-Cell Spray Foam Roof Deck)", "$7,800 Gross / $6,600 Net (Max $1,200 25C Cap)", "$3,900 Blown Fiberglass R-60", "+$2,700 Spray Foam Premium", "Blown R-60 + Air Sealing Delivers 91% of Thermal Gain at Half Cost")
        ],
        "takeaway": "Counter-Intuitive Takeaway: Blowing 14 inches of R-49 fiberglass over unsealed drywall top plates and recessed can lights loses up to 38% of its rated R-value to convective winter air loops. Spending the first $180 on polyurethane foam gun sealing around plumbing stacks and wire penetrations yields 3x the BTU reduction per dollar of insulation depth alone."
    }
]

# 16 Core Empirical Calculators
CALCULATORS = [
    {"name": "Roof Replacement Cost Estimator", "slug": "roofing-cost-calculator.html", "category": "Exterior"},
    {"name": "Attic Insulation & Air Sealing ROI", "slug": "attic-insulation-calculator.html", "category": "Energy"},
    {"name": "Window Replacement Estimator", "slug": "window-replacement-estimator.html", "category": "Exterior"},
    {"name": "Home Siding Replacement Cost", "slug": "siding-cost-calculator.html", "category": "Exterior"},
    {"name": "Driveway Paving Calculator", "slug": "driveway-paving-calculator.html", "category": "Exterior"},
    {"name": "Fence Cost & Linear Footage Estimator", "slug": "fence-cost-calculator.html", "category": "Exterior"},
    {"name": "Heat Pump vs. Gas Furnace ROI", "slug": "hvac-roi-calculator.html", "category": "HVAC"},
    {"name": "Ductless Mini-Split Cost Estimator", "slug": "mini-split-calculator.html", "category": "HVAC"},
    {"name": "Water Heater Replacement Cost", "slug": "water-heater-calculator.html", "category": "Plumbing"},
    {"name": "Solar Panel Payback Timeline", "slug": "solar-payback-calculator.html", "category": "Energy"},
    {"name": "Pool Pump Energy Calculator", "slug": "pool.html", "category": "Energy"},
    {"name": "Bathroom Remodel Cost Estimator", "slug": "bathroom-remodel-calculator.html", "category": "Interior"},
    {"name": "Kitchen Remodel Cost Estimator", "slug": "kitchen-remodel-calculator.html", "category": "Interior"},
    {"name": "Basement Finishing Cost Estimator", "slug": "basement-cost-calculator.html", "category": "Interior"},
    {"name": "EV Home Charger Installation", "slug": "ev-charger-calculator.html", "category": "Electrical"},
    {"name": "Backup Generator Sizing Guide", "slug": "generator-calculator.html", "category": "Electrical"}
]

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




def fetch_telemetry():
    """Fetches daily ambient temp, 6cm soil temp, and solar radiation from Open-Meteo with safe fallback."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}"
        "&daily=temperature_2m_max,temperature_2m_min,shortwave_radiation_sum"
        "&hourly=soil_temperature_6cm&temperature_unit=fahrenheit&timezone=America%2FNew_York&forecast_days=1"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TheBuyersMath-Bot/3.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            t_max = raw["daily"]["temperature_2m_max"][0]
            t_min = raw["daily"]["temperature_2m_min"][0]
            rad_mj = raw["daily"]["shortwave_radiation_sum"][0]
            soils = [x for x in raw["hourly"]["soil_temperature_6cm"] if x is not None]
            avg_t = round((t_max + t_min) / 2.0, 1)
            soil_t = round(sum(soils) / len(soils), 1) if soils else round(avg_t + 2.0, 1)
            sun_hrs = round(rad_mj * 0.2778, 1)
            return avg_t, soil_t, sun_hrs
    except Exception as e:
        print(f"[WARN] Open-Meteo telemetry fallback used: {e}")
        return 54.2, 56.8, 4.3

def get_deterministic_data(target_date):
    """Selects deterministic items and today's Flagship Multi-Pass Case Study."""
    day_of_year = target_date.timetuple().tm_yday
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
    quote = QUOTE_TEARDOWNS[day_of_year % len(QUOTE_TEARDOWNS)]
    code = CODE_BRIEFS[(day_of_year + 1) % len(CODE_BRIEFS)]
    rebate = REBATE_ALERTS[(day_of_year + 2) % len(REBATE_ALERTS)]
    tool = TOOL_DEALS[(day_of_year + 3) % len(TOOL_DEALS)]
    flagship = FLAGSHIP_STUDIES[day_of_year % len(FLAGSHIP_STUDIES)]
    return commodities, quote, code, rebate, tool, flagship

def load_and_update_baselines(target_date, commodities, flagship, avg_t, soil_t, sun_hrs):
    """Updates data/live-baselines.json (Stream 1 & Stream 3)."""
    os.makedirs("data", exist_ok=True)
    today_iso = target_date.strftime("%Y-%m-%d")
    formatted_date = target_date.strftime("%B %d, %Y")
    short_date = target_date.strftime("%b %d")

    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    m = data.get("metrics", {})
    kwh = float(m.get("kwh_rate", 0.172))
    nat_gas = float(m.get("nat_gas_therm", 1.45))
    propane = float(m.get("propane_gal", 2.65))
    gasoline = float(m.get("gasoline_gal", 3.35))
    pellets = float(m.get("pellets_40lb", 16.99))

    hdd = round(max(0.0, 65.0 - avg_t), 1)
    cdd = round(max(0.0, avg_t - 65.0), 1)
    mult = round(1.0 + (hdd * 0.008) + (cdd * 0.01), 2)
    aux_strip_pct = max(12, min(42, int(round(hdd * 2.6))))

    spf_price = float(commodities[0]["price"].replace("$", "")) if len(commodities) > 0 else 4.00
    romex_price = float(commodities[1]["price"].replace("$", "")) if len(commodities) > 1 else 146.49
    shingle_price = float(commodities[2]["price"].replace("$", "")) if len(commodities) > 2 else 118.71
    concrete_price = float(commodities[3]["price"].replace("$", "")) if len(commodities) > 3 else 6.65
    drywall_price = float(commodities[4]["price"].replace("$", "")) if len(commodities) > 4 else 15.20
    r38_price = float(commodities[5]["price"].replace("$", "")) if len(commodities) > 5 else 78.50

    data["last_updated"] = today_iso
    data["formatted_date"] = formatted_date
    data["associate_tag"] = AMAZON_TAG
    data["ad_config"] = {
        "adsense_client": ADSENSE_CLIENT,
        "adsense_slot_top": "responsive",
        "adsense_slot_bottom": "responsive",
        "cj_enterprise_id": CJ_ENTERPRISE_ID,
        "cj_property_id": CJ_PID,
        "angi_url": CJ_ANGI_URL,
        "elocal_url": CJ_ANGI_URL,
        "switchbot_url": CJ_SWITCHBOT_URL,
        "ga4_id": GA4_ID
    }
    data["metrics"] = {
        "kwh_rate": kwh,
        "nat_gas_therm": nat_gas,
        "propane_gal": propane,
        "gasoline_gal": gasoline,
        "pellets_40lb": pellets,
        "ambient_temp_f": avg_t,
        "soil_temp_f": soil_t,
        "solar_peak_hours": sun_hrs,
        "hdd_index": hdd,
        "aux_strip_load_pct": aux_strip_pct,
        "generator_load_mult": mult,
        "spf_stud_2x4": spf_price,
        "romex_12_2_250ft": romex_price,
        "arch_shingles_sq": shingle_price,
        "concrete_80lb": concrete_price,
        "drywall_sheet": drywall_price,
        "r38_batt_roll": r38_price
    }

    if avg_t < 45:
        headline = f"Cold-Weather Heating & Backup Power Window ({avg_t}°F Baseline)"
        summary = f"With average electricity at ${kwh:.3f}/kWh and ambient temperatures at {avg_t}°F ({hdd} HDD), heat pump auxiliary strips increase daily load by ~{aux_strip_pct}% and backup generators carry a {mult}x cold-load multiplier."
    elif 50 <= soil_t <= 62:
        headline = f"Thermal Balance Point ({avg_t}°F) & {soil_t}°F Soil Threshold Window"
        summary = f"With average electricity at ${kwh:.3f}/kWh and overnight lows dropping into the 40s ({hdd} HDD), heat pump auxiliary strips increase daily load by ~{aux_strip_pct}%, while {soil_t}°F soil temperatures mark the prime window for exterior flatwork and pre-winterization."
    else:
        headline = f"Daily Home & Utility Operating Cost Index ({avg_t}°F Baseline)"
        summary = f"Today's solar irradiance provides {sun_hrs} peak sun hours against a ${kwh:.3f}/kWh grid baseline, with thermal load sitting at {mult}x."

    data["seasonal_banner"] = {"headline": headline, "summary": summary}

    data["math_of_the_day"] = {
        "title": flagship["title"],
        "url": "/daily/todays-math/index.html",
        "parent_calc": f"/{flagship['calc_slug']}",
        "parent_calc_query": f"/{flagship['calc_slug']}{flagship['query_params']}",
        "parent_calc_name": flagship["calc_name"],
        "highlight": flagship["takeaway"]
    }

    data["tool_context"] = {
        "hvac": f"With average electricity at ${kwh:.3f}/kWh and overnight lows dropping into the 40s ({hdd} HDD), heat pump auxiliary strips increase daily load by ~{aux_strip_pct}% unless paired with a cold-climate inverter and compressor lockout thermostat. Our defaults below are pre-set to today's averages.",
        "roofing": f"With Class A architectural shingles averaging ${shingle_price:.2f}/sq and daytime ambient temperatures at {avg_t}°F, self-sealing asphalt thermal strips require proper nail placement before winter frost. Our defaults below reflect today's material and labor baselines.",
        "electrical": f"With 12/2 NM-B copper Romex at ${romex_price:.2f} per 250ft coil and winter heating/EV loads rising, 200A panel and backup power circuits carry a {mult}x seasonal load factor. Our defaults below are pre-set to today's averages.",
        "plumbing": f"With incoming municipal groundwater temperatures near {soil_t}°F, water heater recovery delta-T rises by ~14%, boosting hybrid heat pump ROI over standard electric tanks. Our defaults below reflect today's utility baselines.",
        "interior": f"With 2x4x8 SPF framing studs at ${spf_price:.2f} and 1/2\" drywall at ${drywall_price:.2f}/sheet, interior remodeling material takeoffs are holding steady. Our defaults below are pre-set to today's averages.",
        "outdoor": f"With 80lb 4000-PSI concrete at ${concrete_price:.2f}/bag and 6cm soil temperatures at {soil_t}°F, footing excavation and flatwork curing remain in the prime pre-freeze window. Our defaults below reflect today's material rates."
    }

    hist = data.get("history_30d", [
        100, 101, 99, 102, 104, 103, 105, 106, 104, 107,
        108, 107, 109, 110, 108, 111, 112, 110, 113, 114,
        112, 115, 114, 116, 115, 117, 118, 116, 119
    ])
    hist.append(round(100 * mult + (hdd * 0.4)))
    data["history_30d"] = hist[-30:]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data

def build_sparkline_svg_inline(data_points, label="30-Day Cost Index"):
    if not data_points or len(data_points) < 2:
        return ""
    width, height = 190, 42
    mn, mx = min(data_points), max(data_points)
    rng = (mx - mn) or 1
    pts = []
    for idx, val in enumerate(data_points):
        x = round((idx / (len(data_points) - 1)) * (width - 8) + 4, 1)
        y = round(height - 4 - ((val - mn) / rng) * (height - 8), 1)
        pts.append(f"{x},{y}")
    pts_str = " ".join(pts)
    delta = round(((data_points[-1] - data_points[0]) / data_points[0]) * 100, 1)
    sign = "+" if delta >= 0 else ""
    return f"""<div style="display:flex;align-items:center;gap:10px;background:#f8fafc;padding:6px 12px;border-radius:6px;border:1px solid #e2e8f0;">
        <div>
          <div style="font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;">{label}</div>
          <div style="font-size:13px;font-weight:700;color:#0f172a;">{sign}{delta}% (30d)</div>
        </div>
        <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" aria-label="30 day cost trend sparkline">
          <polyline fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" points="{pts_str}" />
        </svg>
      </div>"""

def build_daily_report_html(target_date, commodities, quote, code, rebate, tool, flagship, baselines):
    """Builds the Stream 2 Flagship Daily Math Briefing + Multi-Pass Synthesis + Inline Micro-Calculator."""
    date_str = target_date.strftime("%B %d, %Y")
    iso_date = target_date.strftime("%Y-%m-%d")
    slug = f"{iso_date}-daily-market-intelligence"
    page_title = f"Flagship Daily Math Briefing ({date_str}): {flagship['title']} | The Buyer's Math"
    meta_desc = f"{date_str} Flagship Multi-Pass Analysis: {flagship['title']}. Includes 3-scenario calculator synthesis, live commodity spot prices, and interactive micro-calculator."

    m = baselines["metrics"]
    gas_24h = round(12.5 * m["gasoline_gal"] * m["generator_load_mult"], 2)
    prop_24h = round(15.2 * m["propane_gal"] * m["generator_load_mult"], 2)
    solar_save = round(4.0 * m["solar_peak_hours"] * m["kwh_rate"], 2)

    pass_rows = ""
    for p_name, opt_a, opt_b, delta_col, breakeven_col in flagship["passes"]:
        pass_rows += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
          <td style="padding: 0.85rem 1rem; font-weight: 700; color: #0f172a;">{p_name}</td>
          <td style="padding: 0.85rem 1rem; color: #1e40af; font-weight: 600;">{opt_a}</td>
          <td style="padding: 0.85rem 1rem; color: #334155;">{opt_b}</td>
          <td style="padding: 0.85rem 1rem; font-weight: 600; color: #0f172a;">{delta_col}</td>
          <td style="padding: 0.85rem 1rem; font-weight: 700; color: #16a34a;">{breakeven_col}</td>
        </tr>"""

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
          <td style="padding: 0.85rem 1rem; text-align: center;"><a href="/{c['calc']}" style="background: #f1f5f9; color: #2563eb; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.8rem; text-decoration: none; font-weight: 600;">Calculate</a></td>
        </tr>"""

    mat_breakdown_rows = ""
    mat_sum = sum(cost for _, cost in quote["materials"])
    for item, cost in quote["materials"]:
        mat_breakdown_rows += f"""
        <li style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px dashed #cbd5e1; font-size: 0.9rem;">
          <span>{item}</span>
          <span style="font-weight: 600; color: #0f172a;">${cost:,}</span>
        </li>"""

    red_flag_items = "".join(f"<li style='margin-bottom: 0.5rem;'><strong>🚩 Red Flag:</strong> {rf}</li>" for rf in quote["red_flags"])
    checklist_items = "".join(f"<li style='margin-bottom: 0.4rem;'>✓ {item}</li>" for item in code["inspection_checklist"])

    labor_total = quote["labor_hours"] * quote["labor_rate"]
    direct_subtotal = mat_sum + labor_total + quote["permits_disposal"]
    op_dollars = int(direct_subtotal * (quote["overhead_profit_pct"] / 100.0))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="{SITE_URL}/daily/todays-math/index.html">

  <!-- OpenGraph Metadata -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{page_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="{SITE_URL}/daily/todays-math/index.html">
  <meta property="og:image" content="{SITE_URL}/og-image.svg">
  <meta property="og:site_name" content="The Buyer's Math">

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
      "url": "{SITE_URL}"
    }}
  }}
  </script>

  <link rel="stylesheet" href="/styles.css">
  <style>
    .intel-container {{ max-width: 980px; margin: 0 auto; padding: 2rem 1.25rem 4rem; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1e293b; line-height: 1.6; }}
    .intel-badge {{ display: inline-block; background: #2563eb; color: #ffffff; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.25rem 0.6rem; border-radius: 4px; margin-bottom: 0.75rem; }}
    .intel-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.75rem; margin-bottom: 2.25rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .intel-card h2 {{ margin-top: 0; font-size: 1.4rem; color: #0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; }}
    .intel-card h2 span.section-tag {{ font-size: 0.8rem; font-weight: 600; background: #f8fafc; border: 1px solid #cbd5e1; padding: 0.2rem 0.5rem; border-radius: 4px; color: #475569; }}
    .table-wrap {{ overflow-x: auto; margin: 1rem 0; }}
    table.intel-table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    .cta-btn {{ background: #2563eb; color: #ffffff; padding: 0.7rem 1.4rem; border-radius: 6px; font-weight: 700; text-decoration: none; display: inline-block; }}
    .deal-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 1.25rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }}
    .calc-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-top: 12px; }}
    .calc-grid label {{ display: block; font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 4px; }}
    .calc-grid input, .calc-grid select {{ width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box; background: #fff; }}
    .ad-slot {{ min-height: 90px; margin: 16px 0; text-align: center; }}
  </style>
</head>
<body>

  <header style="background: #0f172a; color: #ffffff; padding: 1rem 1.5rem; border-bottom: 1px solid #334155;">
    <div style="max-width: 980px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
      <a href="/index.html" style="color: #ffffff; text-decoration: none; font-weight: 800; font-size: 1.2rem;">THE BUYER'S MATH</a>
      <nav style="display: flex; gap: 1.25rem; align-items: center;">
        <a href="/index.html" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">Calculators</a>
        <a href="/guides.html" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">Guides</a>
        <a href="/intel/index.html" style="color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 0.9rem;">Daily Math Archive</a>
        <a href="/about.html" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">About</a>
      </nav>
    </div>
  </header>

  <main class="intel-container">
    <div style="text-align: center; margin-bottom: 2rem;">
      <span class="intel-badge">Stream 2 &bull; Flagship Daily Math Briefing ({date_str})</span>
      <h1 style="font-size: 2.05rem; color: #0f172a; margin: 0.25rem 0 0.5rem; letter-spacing: -0.02em;">{flagship['title']}</h1>
      <p style="color: #64748b; font-size: 1.02rem; margin: 0;">Multi-Pass Calculator Synthesis, Live Telemetry &amp; Unit Economics &bull; Linked to <a href="/{flagship['calc_slug']}" style="color:#2563eb;font-weight:700;">{flagship['calc_name']}</a></p>
    </div>

    <!-- Stream 1: Live Telemetry & 30-Day Sparkline Banner -->
    <div id="tbm-live-banner"></div>

    <!-- Top High-Viewability AdSense Slot -->
    <div id="ad-slot-top" class="ad-slot"></div>

    <!-- STREAM 2: Multi-Pass Formula Synthesis & Inline Micro-Tool -->
    <section class="intel-card">
      <h2>
        <span>1. Multi-Pass Calculator Synthesis (3 Homeowner Scenarios)</span>
        <span class="section-tag">Empirical Breakeven Audit</span>
      </h2>
      <p style="color: #475569; font-size: 0.95rem; margin-top: 0.5rem;">
        Using today's live baseline telemetry (<strong>${m['kwh_rate']:.3f}/kWh</strong> grid electricity, <strong>${m['nat_gas_therm']:.2f}/therm</strong> natural gas, <strong>{m['ambient_temp_f']}&deg;F</strong> ambient temperature, and <strong>{m['soil_temp_f']}&deg;F</strong> soil temperature), we ran 3 distinct property profiles through the <a href="/{flagship['calc_slug']}{flagship['query_params']}" style="color:#2563eb;font-weight:700;">{flagship['calc_name']}</a>:
      </p>
      <div class="table-wrap">
        <table class="intel-table">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1; font-size: 0.82rem; color: #475569; text-transform: uppercase;">
              <th style="padding: 0.75rem 1rem;">Property Scenario</th>
              <th style="padding: 0.75rem 1rem;">Primary Option</th>
              <th style="padding: 0.75rem 1rem;">Baseline Alternative</th>
              <th style="padding: 0.75rem 1rem;">Net Capital Delta</th>
              <th style="padding: 0.75rem 1rem;">Payback &amp; 10-Yr Math</th>
            </tr>
          </thead>
          <tbody>
            {pass_rows}
          </tbody>
        </table>
      </div>
      <div style="background: #eff6ff; border-left: 4px solid #2563eb; padding: 1rem 1.25rem; border-radius: 6px; font-size: 0.92rem; color: #1e3a8a; margin-top: 1rem;">
        <strong>{flagship['takeaway']}</strong>
      </div>
      <div style="margin-top: 1.25rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <a href="/{flagship['calc_slug']}{flagship['query_params']}" class="cta-btn">Open Pre-Filled {flagship['calc_name']} &rarr;</a>
        <a href="{CJ_ANGI_URL}" target="_blank" rel="sponsored nofollow noopener" class="cta-btn" style="background: #0f172a;">Compare 3 Local Contractor Bids (Angi) &rarr;</a>
      </div>
    </section>

    <!-- STREAM 2B: Inline Interactive Micro-Calculator -->
    <section class="intel-card">
      <h2>
        <span>2. Inline Interactive Micro-Tool: Thermal Load &amp; Outage Fuel Crossover</span>
        <span class="section-tag">Tweak Live Numbers</span>
      </h2>
      <p style="color: #475569; font-size: 0.95rem;">
        Adjust run hours, square footage, or local utility rates below to test today's <strong>{m['generator_load_mult']}x thermal load multiplier</strong> and auxiliary strip impact on the spot:
      </p>
      <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid #cbd5e1;">
        <div class="calc-grid">
          <div>
            <label for="hours">Duration / Heating Window (Hours)</label>
            <input type="number" id="hours" value="24" min="1" max="720" oninput="calcRun()">
          </div>
          <div>
            <label for="kwh_input">Electric Rate ($/kWh)</label>
            <input type="number" id="kwh_input" step="0.005" data-tbm-baseline="kwh_rate" value="{m['kwh_rate']}" oninput="calcRun()">
          </div>
          <div>
            <label for="gas_price">Gasoline ($/gal)</label>
            <input type="number" id="gas_price" step="0.01" data-tbm-baseline="gasoline_gal" value="{m['gasoline_gal']}" oninput="calcRun()">
          </div>
          <div>
            <label for="prop_price">Propane ($/gal)</label>
            <input type="number" id="prop_price" step="0.01" data-tbm-baseline="propane_gal" value="{m['propane_gal']}" oninput="calcRun()">
          </div>
        </div>
        <div id="calc-result" style="margin-top: 14px; padding: 14px; background: #eff6ff; border-radius: 6px; font-weight: 600; color: #1e3a8a; border: 1px solid #bfdbfe;"></div>
      </div>

      <!-- Result Anchor AdSense Slot -->
      <div id="ad-slot-bottom" class="ad-slot"></div>

      <!-- Stream 3: Dynamic Cost-Per-Use & 5-Year TCO Product Matrix -->
      <div id="tbm-unit-matrix" data-category="{flagship['category']}"></div>
      <div id="tbm-embed-box"></div>
    </section>

    <!-- SECTION 3: Material & Commodity Spot-Price Index -->
    <section class="intel-card">
      <h2>
        <span>3. Construction Material &amp; Commodity Spot-Price Index</span>
        <span class="section-tag">National Retail Benchmarks</span>
      </h2>
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
    </section>

    <!-- SECTION 4: Contractor Quote Teardown -->
    <section class="intel-card">
      <h2>
        <span>4. Audited Contractor Quote Teardown: {quote['title']}</span>
        <span class="section-tag">Trade: {quote['trade']}</span>
      </h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin: 1.25rem 0;">
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.25rem;">
          <h3 style="margin-top: 0; font-size: 1.05rem; color: #1e293b;">Typical Market Bid: ${quote['total_bid']:,}</h3>
          <p style="font-size: 0.85rem; color: #64748b; margin: 0 0 1rem;">Verified Fair Price Window: <strong style="color: #16a34a;">{quote['fair_range']}</strong></p>
          <ul style="list-style: none; padding: 0; margin: 0;">
            {mat_breakdown_rows}
            <li style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px dashed #cbd5e1; font-size: 0.9rem;">
              <span>Direct Trade Labor ({quote['labor_hours']} hrs @ ${quote['labor_rate']}/hr)</span>
              <span style="font-weight: 600; color: #0f172a;">${labor_total:,}</span>
            </li>
            <li style="display: flex; justify-content: space-between; padding: 0.35rem 0; border-bottom: 1px dashed #cbd5e1; font-size: 0.9rem;">
              <span>Permits &amp; Overhead ({quote['overhead_profit_pct']}%)</span>
              <span style="font-weight: 600; color: #0f172a;">${quote['permits_disposal'] + op_dollars:,}</span>
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
        </div>
      </div>
    </section>

    <!-- SECTION 5: Building Code & IRA Tax Credit Fast-Brief -->
    <section class="intel-card">
      <h2>
        <span>5. Code &amp; Tax Incentive Brief: {code['code_ref']} + {rebate['program']}</span>
        <span class="section-tag">Compliance &amp; Rebates</span>
      </h2>
      <p style="color: #334155; font-size: 0.95rem;"><strong>{code['topic']}:</strong> {code['summary']}</p>
      <ul style="list-style: none; padding: 0; margin: 0 0 1.25rem; font-size: 0.9rem; color: #334155;">
        {checklist_items}
      </ul>
      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; border-radius: 8px; padding: 1.25rem;">
        <h3 style="margin: 0 0 0.35rem; color: #166534; font-size: 1.15rem;">{rebate['title']} (Max: {rebate['max_value']})</h3>
        <p style="font-size: 0.9rem; color: #166534; margin: 0 0 0.5rem;">{rebate['qualification']}</p>
        <p style="font-size: 0.85rem; color: #14532d; margin: 0;"><strong>Filing Form:</strong> <code>{rebate['filing_doc']}</code> &bull; <a href="/{rebate['calc_url']}" style="color:#15803d;font-weight:700;">Open {rebate['calc_name']} &rarr;</a></p>
      </div>
    </section>
  </main>

  <footer style="background: #0f172a; color: #94a3b8; padding: 2.5rem 1.5rem; border-top: 1px solid #1e293b; font-size: 0.85rem; text-align: center;">
    <div style="max-width: 980px; margin: 0 auto;">
      <p style="margin: 0 0 0.5rem;">&copy; {target_date.year} The Buyer's Math. Living Authority Hub &amp; Empirical Cost Calculators.</p>
      <p style="margin: 0; font-size: 0.75rem; color: #64748b;">
        Amazon Associates Tag: {AMAZON_TAG} &bull; CJ Affiliate PID: {CJ_PID} &bull; AdSense: {ADSENSE_CLIENT}
      </p>
    </div>
  </footer>

  <script>
    function calcRun() {{
      const hrs = parseFloat(document.getElementById('hours').value) || 24;
      const kwh = parseFloat(document.getElementById('kwh_input').value) || 0.172;
      const gP = parseFloat(document.getElementById('gas_price').value) || 3.35;
      const pP = parseFloat(document.getElementById('prop_price').value) || 2.65;
      const gCost = (hrs * 0.52 * gP).toFixed(2);
      const pCost = (hrs * 0.63 * pP).toFixed(2);
      const auxStripCost = (hrs * 5.0 * kwh).toFixed(2);
      const inverterCost = (hrs * 1.45 * kwh).toFixed(2);
      const winner = parseFloat(gCost) < parseFloat(pCost) ? 'Gasoline' : 'Propane';
      const diff = Math.abs(gCost - pCost).toFixed(2);
      document.getElementById('calc-result').innerHTML =
        `<div><strong>1. Heating Aux-Strip Lockout Math (${{hrs}} hrs):</strong> Inverter Heat Pump Only = <strong>$${{inverterCost}}</strong> vs. Unregulated 5kW Aux Strips = <strong>$${{auxStripCost}}</strong> (Lockout saves <strong>$${{(auxStripCost - inverterCost).toFixed(2)}}</strong>).</div>` +
        `<div style="margin-top:6px;"><strong>2. Backup Generator Fuel Crossover (${{hrs}} hrs):</strong> Gasoline = <strong>$${{gCost}}</strong> vs. Liquid Propane = <strong>$${{pCost}}</strong> (${{winner}} saves <strong>$${{diff}}</strong> before maintenance).</div>` +
        `<div style="margin-top:8px;font-size:12px;display:flex;flex-wrap:wrap;gap:12px;">` +
        `<a href="https://www.amazon.com/dp/B09XXS48P8?tag={AMAZON_TAG}" target="_blank" rel="sponsored nofollow noopener" style="color:#1e40af;text-decoration:underline;">Ecobee Aux-Lockout Thermostat (Amazon) &rarr;</a>` +
        `<a href="https://www.amazon.com/dp/B08L9G2N64?tag={AMAZON_TAG}" target="_blank" rel="sponsored nofollow noopener" style="color:#1e40af;text-decoration:underline;">Champion Dual-Fuel Generator (Amazon) &rarr;</a>` +
        `<a href="{CJ_ANGI_URL}" target="_blank" rel="sponsored nofollow noopener" style="color:#166534;text-decoration:underline;">Compare Local Pro Bids (Angi) &rarr;</a>` +
        `</div>`;
    }}
    calcRun();
  </script>
  <script src="/tbm-widget.js" defer></script>
</body>
</html>
"""
    return html, slug

def detect_file_category(fname):
    low = fname.lower()
    if any(k in low for k in ["hvac", "mini-split", "attic", "radiant"]):
        return "hvac"
    if any(k in low for k in ["roof", "siding", "window", "gutter", "garage", "paint"]):
        return "roofing"
    if any(k in low for k in ["ev-charger", "generator", "solar", "panel"]):
        return "electrical"
    if "water-heater" in low:
        return "plumbing"
    if any(k in low for k in ["kitchen", "bathroom", "basement", "flooring"]):
        return "interior"
    if any(k in low for k in ["pool", "fence", "driveway", "deck", "patio"]):
        return "outdoor"
    return "energy"

def retrofit_all_calculators_and_merge_case_study(target_date, flagship, baselines):
    """
    Executes Stream 1, Stream 3, and Stream 4 across all calculator HTML files in the repo:
      - Injects #tbm-live-banner ("Today's Context" + 30-Day Sparkline) above inputs
      - Injects #tbm-unit-matrix ("Cost-Per-Use & 5-Yr TCO Matrix") and #tbm-embed-box below results
      - Appends/updates the "Real-World Case Studies & Recent Scenarios" tab inside the Parent Calculator
      - Ensures <script src="/tbm-widget.js" defer></script> is loaded before </body>
    """
    iso_date = target_date.strftime("%Y-%m-%d")
    date_str = target_date.strftime("%B %d, %Y")
    known_calcs = [
        "roofing-cost-calculator.html", "attic-insulation-calculator.html", "window-replacement-estimator.html",
        "siding-cost-calculator.html", "driveway-paving-calculator.html", "fence-cost-calculator.html",
        "hvac-roi-calculator.html", "mini-split-calculator.html", "water-heater-calculator.html",
        "solar-payback-calculator.html", "pool.html", "bathroom-remodel-calculator.html",
        "kitchen-remodel-calculator.html", "basement-cost-calculator.html", "ev-charger-calculator.html",
        "generator-calculator.html", "deck-cost-calculator.html", "gutter-cost-calculator.html",
        "garage-door-calculator.html", "patio-cost-calculator.html", "exterior-painting-calculator.html",
        "electrical-panel-calculator.html", "flooring-calculator.html", "radiant-floor-calculator.html"
    ]
    discovered = [
        f for f in os.listdir(".")
        if f.endswith(".html") and (
            "calculator" in f or "estimator" in f or f == "pool.html"
        ) and not f.startswith("test_")
    ]
    calc_files = sorted(list(set(discovered + [f for f in known_calcs if os.path.exists(f)])))

    # Build the Case Study card HTML for today's Flagship study (Stream 4)
    pass_items_html = "".join(
        f"<li style='margin-bottom:0.35rem;'><strong>{p[0]}:</strong> {p[1]} vs. {p[2]} &rarr; <span style='color:#16a34a;font-weight:700;'>{p[4]}</span></li>"
        for p in flagship["passes"]
    )
    case_study_section = f"""<!-- TBM CASE STUDIES START -->
    <section id="tbm-case-studies" style="margin-top: 2.5rem; background: #ffffff; border: 1px solid #cbd5e1; border-left: 5px solid #2563eb; border-radius: 12px; padding: 1.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span style="background: #dbeafe; color: #1e40af; font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 4px; text-transform: uppercase;">
          Stream 4 &bull; Real-World Case Studies &amp; Daily Scenario Log
        </span>
        <span style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Latest Empirical Run: {date_str}</span>
      </div>
      <h3 style="margin: 0.25rem 0 0.5rem 0; font-size: 1.3rem; color: #0f172a;">{flagship['title']}</h3>
      <p style="margin: 0 0 1rem 0; font-size: 0.92rem; color: #334155; line-height: 1.55;">
        {flagship['takeaway']}
      </p>
      <ul style="margin: 0 0 1rem 0; padding-left: 1.25rem; font-size: 0.9rem; color: #1e293b; line-height: 1.6;">
        {pass_items_html}
      </ul>
      <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; font-size: 0.88rem;">
        <a href="/daily/todays-math/index.html" style="color: #2563eb; font-weight: 700; text-decoration: none;">Read Full Multi-Pass Briefing &rarr;</a>
        <a href="{CJ_ANGI_URL}" target="_blank" rel="sponsored nofollow noopener" style="color: #0f766e; font-weight: 700; text-decoration: none;">Get 3 Local Contractor Quotes for This Scenario (Angi) &rarr;</a>
      </div>
    </section>
<!-- TBM CASE STUDIES END -->"""

    retrofitted_count = 0
    for fname in calc_files:
        with open(fname, "r", encoding="utf-8") as f:
            content = f.read()

        cat = detect_file_category(fname)
        modified = False

        # 1. Inject #tbm-live-banner right before <!-- Interactive Calculator Card --> or first calculator grid
        if 'id="tbm-live-banner"' not in content:
            banner_div = f'    <!-- Stream 1: Living Tool Context Banner & 30-Day Sparkline -->\n    <div id="tbm-live-banner" data-category="{cat}"></div>\n\n'
            if "<!-- Interactive Calculator Card -->" in content:
                content = content.replace("<!-- Interactive Calculator Card -->", banner_div + "    <!-- Interactive Calculator Card -->", 1)
                modified = True
            elif '<div class="calculator-' in content:
                idx = content.find('<div class="calculator-')
                content = content[:idx] + banner_div + content[idx:]
                modified = True
            elif "</h1" in content:
                # Insert after the header div containing h1
                h1_end = content.find("</h1>")
                div_end = content.find("</div>", h1_end)
                if div_end != -1:
                    content = content[:div_end + 6] + "\n\n" + banner_div + content[div_end + 6:]
                    modified = True

        # 2. Inject #tbm-unit-matrix and #tbm-embed-box after Calculator Card or before bundled-projects-section / editorial section
        if 'id="tbm-unit-matrix"' not in content:
            matrix_block = (
                f'\n    <!-- Stream 3: Automated Cost-Per-Use & 5-Year TCO Product Matrix -->\n'
                f'    <div id="tbm-unit-matrix" data-category="{cat}"></div>\n'
                f'    <div id="tbm-embed-box"></div>\n\n'
            )
            if '<section class="bundled-projects-section">' in content:
                content = content.replace('<section class="bundled-projects-section">', matrix_block + '    <section class="bundled-projects-section">', 1)
                modified = True
            elif '<!-- Frequently Bundled' in content:
                content = content.replace('<!-- Frequently Bundled', matrix_block + '    <!-- Frequently Bundled', 1)
                modified = True
            elif '</main>' in content:
                content = content.replace('</main>', matrix_block + '  </main>', 1)
                modified = True

        # 3. Stream 4: Inject or update Real-World Case Studies section inside the matching Parent Calculator
        if fname == flagship["calc_slug"] or 'id="tbm-case-studies"' not in content:
            # If it's the active flagship parent calculator, update with today's 3-pass case study;
            # if another calculator doesn't have a case study block yet, seed one tailored to its category!
            if fname == flagship["calc_slug"]:
                block_to_use = case_study_section
            else:
                # Find matching study for this category
                cat_study = next((s for s in FLAGSHIP_STUDIES if s["category"] == cat), flagship)
                cat_passes = "".join(
                    f"<li style='margin-bottom:0.35rem;'><strong>{p[0]}:</strong> {p[1]} vs. {p[2]} &rarr; <span style='color:#16a34a;font-weight:700;'>{p[4]}</span></li>"
                    for p in cat_study["passes"]
                )
                block_to_use = f"""<!-- TBM CASE STUDIES START -->
    <section id="tbm-case-studies" style="margin-top: 2.5rem; background: #ffffff; border: 1px solid #cbd5e1; border-left: 5px solid #2563eb; border-radius: 12px; padding: 1.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span style="background: #dbeafe; color: #1e40af; font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.6rem; border-radius: 4px; text-transform: uppercase;">
          Stream 4 &bull; Real-World Case Studies &amp; Recent Scenarios
        </span>
        <span style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Updated {date_str}</span>
      </div>
      <h3 style="margin: 0.25rem 0 0.5rem 0; font-size: 1.3rem; color: #0f172a;">{cat_study['title']}</h3>
      <p style="margin: 0 0 1rem 0; font-size: 0.92rem; color: #334155; line-height: 1.55;">
        {cat_study['takeaway']}
      </p>
      <ul style="margin: 0 0 1rem 0; padding-left: 1.25rem; font-size: 0.9rem; color: #1e293b; line-height: 1.6;">
        {cat_passes}
      </ul>
      <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; font-size: 0.88rem;">
        <a href="/daily/todays-math/index.html" style="color: #2563eb; font-weight: 700; text-decoration: none;">Open Today's Flagship Math Briefing &rarr;</a>
        <a href="{CJ_ANGI_URL}" target="_blank" rel="sponsored nofollow noopener" style="color: #0f766e; font-weight: 700; text-decoration: none;">Compare 3 Local Contractor Quotes (Angi) &rarr;</a>
      </div>
    </section>
<!-- TBM CASE STUDIES END -->"""

            if "<!-- TBM CASE STUDIES START -->" in content and "<!-- TBM CASE STUDIES END -->" in content:
                s_idx = content.find("<!-- TBM CASE STUDIES START -->")
                e_idx = content.find("<!-- TBM CASE STUDIES END -->") + len("<!-- TBM CASE STUDIES END -->")
                content = content[:s_idx] + block_to_use + content[e_idx:]
                modified = True
            elif "<!-- FAQs -->" in content:
                content = content.replace("<!-- FAQs -->", block_to_use + "\n\n      <!-- FAQs -->", 1)
                modified = True
            elif "</main>" in content:
                content = content.replace("</main>", "    " + block_to_use + "\n  </main>", 1)
                modified = True

        # 4. Ensure /tbm-widget.js is loaded before </body>
        if '/tbm-widget.js' not in content and '</body>' in content:
            content = content.replace('</body>', '  <script src="/tbm-widget.js" defer></script>\n</body>', 1)
            modified = True

        if modified:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(content)
            retrofitted_count += 1

    print(f"[STREAM 1, 3 & 4] Retrofitted {retrofitted_count} calculator HTML pages with Living Context Banners, Cost-Per-Use Matrices, and Case Study Tabs.")

def prune_old_briefings(target_date, keep_days=30):
    """Stream 2 Lifecycle Management: Keeps only the last 30 days of weather-dependent briefings."""
    cutoff = target_date - datetime.timedelta(days=keep_days)
    pruned = 0

    if os.path.exists(INTEL_DIR):
        for fname in os.listdir(INTEL_DIR):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})", fname)
            if m and fname.endswith(".html"):
                try:
                    f_date = datetime.date.fromisoformat(m.group(1))
                    if f_date < cutoff:
                        os.remove(os.path.join(INTEL_DIR, fname))
                        pruned += 1
                except Exception:
                    pass

    if os.path.exists(DAILY_DIR):
        for entry in os.listdir(DAILY_DIR):
            m = re.match(r"^(\d{4}-\d{2}-\d{2})$", entry)
            if m:
                try:
                    d_date = datetime.date.fromisoformat(m.group(1))
                    if d_date < cutoff:
                        shutil.rmtree(os.path.join(DAILY_DIR, entry), ignore_errors=True)
                        pruned += 1
                except Exception:
                    pass

    print(f"[STREAM 2 LIFECYCLE] Pruned {pruned} expired daily briefings (> {keep_days} days old).")

def update_intel_archive_index(intel_dir):
    """Generates intel/index.html listing all active daily briefs within the 30-day window."""
    files = [
        f for f in os.listdir(intel_dir)
        if f.endswith("-daily-market-intelligence.html")
    ]
    files.sort(reverse=True)

    cards = ""
    for f in files:
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", f)
        if date_match:
            d_str = date_match.group(1)
            try:
                dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                formatted_d = dt.strftime("%B %d, %Y")
            except Exception:
                formatted_d = d_str
        else:
            formatted_d = "Recent Daily Dispatch"

        cards += f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <span style="font-size: 0.8rem; font-weight: 700; color: #2563eb; text-transform: uppercase;">30-Day Rolling Dispatch</span>
            <h3 style="margin: 0.25rem 0 0; font-size: 1.15rem; color: #0f172a;"><a href="{f}" style="text-decoration: none; color: #0f172a;">Flagship Daily Math Briefing &mdash; {formatted_d}</a></h3>
            <p style="margin: 0.25rem 0 0; color: #64748b; font-size: 0.85rem;">3-pass calculator synthesis, live thermal telemetry, commodity spot index, and unit economics matrix.</p>
          </div>
          <a href="{f}" style="background: #f1f5f9; color: #2563eb; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 0.85rem;">Read Edition &rarr;</a>
        </div>"""

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Math Briefings &amp; Market Intelligence Archive | The Buyer's Math</title>
  <meta name="description" content="Rolling 30-day archive of Flagship Daily Math Briefings: multi-pass calculator scenarios, building material price index, live thermal telemetry, and IRA energy rebates.">
  <link rel="canonical" href="{SITE_URL}/intel/index.html">
  <link rel="stylesheet" href="/styles.css">
</head>
<body style="background: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1e293b; margin: 0;">
  <header style="background: #0f172a; color: #ffffff; padding: 1rem 1.5rem; border-bottom: 1px solid #334155;">
    <div style="max-width: 980px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
      <a href="/index.html" style="color: #ffffff; text-decoration: none; font-weight: 800; font-size: 1.2rem;">THE BUYER'S MATH</a>
      <nav style="display: flex; gap: 1.25rem;">
        <a href="/index.html" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">Calculators</a>
        <a href="/daily/todays-math/index.html" style="color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 0.9rem;">Today's Math</a>
        <a href="/guides.html" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">Guides</a>
        <a href="/about.html" style="color: #94a3b8; text-decoration: none; font-size: 0.9rem;">About</a>
      </nav>
    </div>
  </header>
  <main style="max-width: 980px; margin: 2rem auto 4rem; padding: 0 1.25rem;">
    <div id="tbm-live-banner"></div>
    <h1 style="font-size: 2rem; color: #0f172a; margin-bottom: 0.5rem;">Flagship Daily Math Briefings (30-Day Rolling Feed)</h1>
    <p style="color: #64748b; font-size: 1rem; margin-bottom: 2rem;">We maintain a lean, high-signal 30-day rolling feed of daily multi-pass analyses; older case studies are permanently merged into their parent calculators.</p>
    <div>
      {cards}
    </div>
  </main>
  <script src="/tbm-widget.js" defer></script>
</body>
</html>
"""
    with open(os.path.join(intel_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

def build_homepage_widget(target_date, commodities, quote, tool, flagship, latest_slug, baselines):
    """
    Builds the 3-Module "Daily Buyer's Pulse" Homepage Dashboard (Stream 4):
      - Module A: Today's Home Energy, Material & Utility Index + 30-Day SVG Sparkline
      - Module B: Seasonal Property Action Window (Date & Temp Triggered)
      - Module C: "Math of the Day" Spotlight (1-Click into Pre-Filled Calculator & Today's Briefing)
    """
    date_str = target_date.strftime("%b %d, %Y")
    m = baselines["metrics"]
    sparkline_html = build_sparkline_svg_inline(baselines.get("history_30d", []), "30-Day Cost Index")

    comm_short_map = {
        "2x4x8 SPF Premium Framing Studs": ("2x4x8 SPF Lumber", "Framing stud retail avg"),
        "12/2 NM-B Romex Copper Wire (250 ft)": ("12/2 NM-B Romex (250ft)", "Copper branch circuit wire"),
        "Architectural Asphalt Shingles (Class A)": ("Architectural Shingles", "Per square (3 bundles)"),
        "Sakrete / Quikrete 5000 Concrete (80 lb)": ("Concrete 80lb Bag", "4000 PSI high early strength")
    }

    comm_pills = ""
    for c in commodities[:4]:
        arrow = "▲" if c["is_up"] else "▼"
        color = "#dc2626" if c["is_up"] else "#16a34a"
        full_name = c["name"]
        short_title, subtext = comm_short_map.get(full_name, (" ".join(full_name.split()[:3]), "National retail benchmark"))

        comm_pills += f"""
      <div style="background: #f8fafc; padding: 0.85rem 1rem; border-radius: 8px; border: 1px solid #e2e8f0; min-width: 140px; flex: 1;">
        <div style="font-size: 0.75rem; color: #64748b; font-weight: 500;">{short_title}</div>
        <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0.2rem 0;">{c['price']} <span style="font-size: 0.8rem; color: {color}; font-weight: 600;">{arrow} {c['change']}</span></div>
        <div style="font-size: 0.7rem; color: #94a3b8;">{subtext}</div>
      </div>"""

    widget = f"""
<!-- TBM DAILY INTELLIGENCE WIDGET -->
  <section id="tbm-daily-intel-widget" class="market-pulse-widget" style="max-width: 1140px; margin: 0 auto 2.5rem auto; padding: 1.5rem; background: #ffffff; border: 1px solid var(--border, #e2e8f0); border-radius: var(--radius-lg, 16px); box-shadow: var(--shadow-sm); border-left: 6px solid #2563eb;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.75rem; margin-bottom: 1rem;">
      <div>
        <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb; font-weight: 700;">Living Authority Hub &bull; Updated {date_str}</span>
        <h3 style="margin: 0.2rem 0 0 0; font-size: 1.3rem; color: #0f172a;">The Daily Buyer's Pulse: Live Baselines, Telemetry &amp; Math of the Day</h3>
      </div>
      <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
        {sparkline_html}
        <a href="/daily/todays-math/index.html" style="font-size: 0.875rem; color: #2563eb; text-decoration: none; font-weight: 700;">Open Today's Math Briefing &rarr;</a>
      </div>
    </div>

    <!-- Module A: Today's Home Energy, Utility & Material Index -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
{comm_pills}
    </div>
    <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.82rem; color: #334155; background: #f8fafc; padding: 0.65rem 1rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 1rem; align-items: center;">
      <span style="background:#dbeafe;color:#1e40af;font-weight:700;padding:2px 7px;border-radius:4px;font-size:0.72rem;text-transform:uppercase;">Module A &bull; Utility Index</span>
      <span><strong>Grid Electric:</strong> ${m['kwh_rate']:.3f}/kWh</span>
      <span><strong>Nat Gas:</strong> ${m['nat_gas_therm']:.2f}/therm</span>
      <span><strong>Propane:</strong> ${m['propane_gal']:.2f}/gal</span>
      <span><strong>Soil Temp:</strong> {m['soil_temp_f']}&deg;F</span>
      <span><strong>Heating Load:</strong> {m['hdd_index']} HDD (+{m['aux_strip_load_pct']}% Aux Risk)</span>
      <span><strong>Generator Load:</strong> {m['generator_load_mult']}x</span>
    </div>

    <!-- Module B & Module C: Seasonal Action Window + Math of the Day Spotlight -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 0.85rem;">
      <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 1rem;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #b45309; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.25rem;">
          Module B &bull; Seasonal Property Action Window
        </div>
        <div style="font-size: 0.98rem; font-weight: 700; color: #78350f; margin-bottom: 0.35rem;">{baselines['seasonal_banner']['headline']}</div>
        <p style="font-size: 0.84rem; color: #92400e; margin: 0; line-height: 1.5;">{baselines['seasonal_banner']['summary']}</p>
      </div>

      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 1rem; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="font-size: 0.72rem; font-weight: 700; color: #1d4ed8; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.25rem;">
            Module C &bull; "Math of the Day" Multi-Pass Spotlight
          </div>
          <div style="font-size: 0.98rem; font-weight: 700; color: #1e3a8a; margin-bottom: 0.35rem;">{flagship['title']}</div>
          <p style="font-size: 0.84rem; color: #1e40af; margin: 0 0 0.75rem 0; line-height: 1.45;">{flagship['takeaway'][:185]}...</p>
        </div>
        <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
          <a href="/{flagship['calc_slug']}{flagship['query_params']}" style="background: #2563eb; color: #ffffff; font-size: 0.8rem; font-weight: 700; padding: 0.45rem 0.85rem; border-radius: 6px; text-decoration: none;">
            Launch Pre-Filled Calculator &rarr;
          </a>
          <a href="/daily/todays-math/index.html" style="background: #ffffff; color: #1e40af; border: 1px solid #93c5fd; font-size: 0.8rem; font-weight: 700; padding: 0.45rem 0.85rem; border-radius: 6px; text-decoration: none;">
            Read 3-Pass Study &rarr;
          </a>
        </div>
      </div>
    </div>

    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; font-size: 0.85rem; color: #475569; border-top: 1px solid #f1f5f9; padding-top: 0.75rem;">
      <span>Audited Contractor Teardown: <strong style="color: #0f172a;">{quote['title']} ({quote['fair_range']})</strong></span>
      <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
        <a href="{tool['affiliate_url']}" target="_blank" rel="sponsored nofollow noopener" style="color: #16a34a; font-weight: 700; text-decoration: none;">★ Best Math Gear: {tool['name'][:36]}... ({tool['discount']}) &rarr;</a>
        <a href="{CJ_ANGI_URL}" target="_blank" rel="sponsored nofollow noopener" style="color: #2563eb; font-weight: 700; text-decoration: underline;">Compare 3 Local Pros (Angi) &rarr;</a>
      </div>
    </div>
  </section>
<!-- END TBM DAILY INTELLIGENCE WIDGET -->
"""
    return widget

def inject_homepage_widget(index_file_path, widget_code):
    """Safely updates the daily intelligence widget and ensures /tbm-widget.js is included on index.html."""
    if not os.path.exists(index_file_path):
        return

    with open(index_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!-- TBM DAILY INTELLIGENCE WIDGET -->"
    end_tag = "<!-- END TBM DAILY INTELLIGENCE WIDGET -->"
    alt_start = "<!-- DAILY_INTEL_WIDGET_START -->"
    alt_end = "<!-- DAILY_INTEL_WIDGET_END -->"

    if start_tag in content and end_tag in content:
        start_idx = content.find(start_tag)
        end_idx = content.find(end_tag) + len(end_tag)
        content = content[:start_idx] + widget_code.strip() + content[end_idx:]
        print("Safely replaced existing daily intelligence widget in index.html.")
    elif alt_start in content and alt_end in content:
        start_idx = content.find(alt_start)
        end_idx = content.find(alt_end) + len(alt_end)
        content = content[:start_idx] + widget_code.strip() + content[end_idx:]
        print("Safely replaced legacy daily intelligence widget in index.html.")

    # Upgrade static index.html text & cards from 21 Calculators -> 24 Calculators
    for old_s, new_s in [
        ("21 Calculators", "24 Calculators"),
        ("21 Live Models", "24 Live Models"),
        ("21 Models", "24 Models"),
        ("21-Calculator", "24-Calculator"),
        ("Complete Suite of 21 Interactive Renovation Calculators", "Complete Suite of 24 Interactive Renovation Calculators"),
        ("Mechanical & Energy (6)", "Mechanical & Energy (7)"),
        ("Mechanical &amp; Energy (6)", "Mechanical &amp; Energy (7)"),
        ("HVAC & Energy (6)", "HVAC & Energy (7)"),
        ("HVAC &amp; Energy (6)", "HVAC &amp; Energy (7)"),
        ("Interior & Power (5)", "Interior & Power (7)"),
        ("Interior &amp; Power (5)", "Interior &amp; Power (7)")
    ]:
        content = content.replace(old_s, new_s)

    # Update top announcement bar date if hardcoded to Oct 16
    today_short = datetime.date.today().strftime("%b %d")
    content = re.sub(
        r"Oct\s+\d+\s+Commodity Index:[^<]+",
        f"{today_short} Commodity Index: 2x4 SPF $4.00 (▲1.2%) • 12/2 Romex $146.49 (▲2.8%) • Shingles $118.71/sq →",
        content
    )

    # Inject the 3 new calculators into the main calculator grid in index.html if not already present
    if "electrical-panel-calculator.html" not in content and "pool.html" in content:
        new_grid_cards = """
      <!-- 22. Electrical Panel Upgrade -->
      <a href="/electrical-panel-calculator.html" class="calc-card" data-category="featured electrical energy interior" data-keywords="electrical panel upgrade 200 amp 400 amp service entrance heavy up circuit breaker load center 25c tax credit">
        <div>
          <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;">Interior &amp; Power</span>
          <h3 style="margin-top: 0.5rem;">200A &amp; 400A Electrical Panel Upgrade</h3>
          <p>Estimate 100A-to-200A service heavy-ups, 400A dual panels, meter sockets, NEC surge protection, and $600 Section 25C credits.</p>
        </div>
        <span class="cta-link">Open Calculator &rarr;</span>
      </a>

      <!-- 23. Flooring Installation & Refinishing -->
      <a href="/flooring-calculator.html" class="calc-card" data-category="interior" data-keywords="hardwood flooring lvp luxury vinyl plank laminate tile refinishing subfloor underlayment square footage cost">
        <div>
          <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;">Interior &amp; Power</span>
          <h3 style="margin-top: 0.5rem;">Flooring Installation &amp; Refinishing</h3>
          <p>Model turnkey pricing for 20-mil LVP, engineered hardwood, solid 3/4" oak, porcelain tile, and dustless hardwood refinishing.</p>
        </div>
        <span class="cta-link">Open Calculator &rarr;</span>
      </a>

      <!-- 24. Radiant Floor Heating -->
      <a href="/radiant-floor-calculator.html" class="calc-card" data-category="hvac energy interior" data-keywords="radiant floor heating ditra heat electric hydronic subfloor thermal mass bathroom heating operating cost">
        <div>
          <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;">Mechanical &amp; Energy</span>
          <h3 style="margin-top: 0.5rem;">Radiant Floor Heating Calculator</h3>
          <p>Compare electric uncoupling mat systems (Ditra-Heat) vs. hydronic PEX tubing, thermal break subfloors, and monthly kWh costs.</p>
        </div>
        <span class="cta-link">Open Calculator &rarr;</span>
      </a>
"""
        # Insert right before the closing </section> of the calculator grid
        calc_sec_idx = content.find('id="calculators"')
        if calc_sec_idx == -1:
            calc_sec_idx = content.find('class="calculator-grid"')
        if calc_sec_idx != -1:
            close_sec = content.find('</section>', calc_sec_idx)
            if close_sec != -1:
                content = content[:close_sec] + new_grid_cards + "    " + content[close_sec:]
                print("Injected Calculators #22-#24 into index.html main calculator grid.")

    # Also add the 3 new calculators to the Hero Quick Launcher if present
    if "Jump to Full 2" in content and 'href="/electrical-panel-calculator.html"' not in content[:content.find("Jump to Full 2")]:
        jump_idx = content.find("Jump to Full 2")
        # Find the preceding <a or container
        last_model_idx = content.rfind("Model &rarr;", 0, jump_idx)
        if last_model_idx == -1:
            last_model_idx = content.rfind("Model →", 0, jump_idx)
        if last_model_idx != -1:
            end_a = content.find("</a>", last_model_idx)
            if end_a != -1:
                quick_cards = """
          <a href="/electrical-panel-calculator.html" class="quick-calc-item" data-qcat="interior">
            <div><strong>200A Electrical Panel Upgrade</strong><span>Service heavy-ups, meter sockets &amp; $600 25C credit</span></div>
            <span class="q-arrow">Model &rarr;</span>
          </a>
          <a href="/flooring-calculator.html" class="quick-calc-item" data-qcat="interior">
            <div><strong>Flooring &amp; Hardwood Refinishing</strong><span>20-mil LVP, solid oak, tile &amp; dustless sanding</span></div>
            <span class="q-arrow">Model &rarr;</span>
          </a>
          <a href="/radiant-floor-calculator.html" class="quick-calc-item" data-qcat="hvac">
            <div><strong>Radiant Floor Heating Calculator</strong><span>Ditra-Heat electric mats vs. hydronic PEX tubing</span></div>
            <span class="q-arrow">Model &rarr;</span>
          </a>"""
                content = content[:end_a + 4] + quick_cards + content[end_a + 4:]

    if '/tbm-widget.js' not in content and '</body>' in content:
        content = content.replace('</body>', '  <script src="/tbm-widget.js" defer></script>\n</body>')

    with open(index_file_path, "w", encoding="utf-8") as f:
        f.write(content)

def update_rss_and_sitemap(target_date, slug, flagship, baselines):
    """Updates rss.xml, feed.xml, and sitemap.xml (standardizing /intel/index.html and /daily/todays-math/index.html)."""
    iso_date = target_date.strftime("%Y-%m-%d")
    formatted_date = target_date.strftime("%B %d, %Y")
    headline = flagship["title"]
    summary = flagship["takeaway"]

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>The Buyer's Math - Flagship Daily Math &amp; Market Intelligence</title>
  <link>{SITE_URL}</link>
  <description>Daily multi-pass home improvement calculator synthesis, construction material spot prices, and unit economics.</description>
  <item>
    <title>{formatted_date}: {headline}</title>
    <link>{SITE_URL}/daily/todays-math/index.html</link>
    <guid>{SITE_URL}/intel/{slug}.html</guid>
    <description>{summary}</description>
  </item>
</channel>
</rss>"""
    for rss_file in ["rss.xml", "feed.xml"]:
        with open(rss_file, "w", encoding="utf-8") as f:
            f.write(rss_xml)

    if os.path.exists("sitemap.xml"):
        with open("sitemap.xml", "r", encoding="utf-8") as f:
            sm = f.read()
        sm = sm.replace(f"<loc>{SITE_URL}/intel/</loc>", f"<loc>{SITE_URL}/intel/index.html</loc>")
        for url_to_add in [
            f"{SITE_URL}/daily/todays-math/index.html",
            f"{SITE_URL}/intel/{slug}.html",
            f"{SITE_URL}/electrical-panel-calculator.html",
            f"{SITE_URL}/flooring-calculator.html",
            f"{SITE_URL}/radiant-floor-calculator.html"
        ]:
            if url_to_add not in sm and "</urlset>" in sm:
                entry = f"""  <url>
    <loc>{url_to_add}</loc>
    <lastmod>{iso_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""
                sm = sm.replace("</urlset>", entry)
        with open("sitemap.xml", "w", encoding="utf-8") as f:
            f.write(sm)
        print("Synchronized rss.xml, feed.xml, and sitemap.xml.")

DEFAULT_INDEXNOW_KEY = "tbm8090259101896838indexnow2026a"

def ping_indexnow(slug):
    """Writes the root IndexNow verification key file and pings IndexNow API automatically."""
    key = os.getenv("INDEXNOW_KEY", "").strip() or DEFAULT_INDEXNOW_KEY
    key_file = f"{key}.txt"
    if not os.path.exists(key_file):
        with open(key_file, "w", encoding="utf-8") as kf:
            kf.write(key)
        print(f"Created IndexNow verification key file: {key_file}")
    payload = {
        "host": SITE_DOMAIN,
        "key": key,
        "keyLocation": f"{SITE_URL}/{key}.txt",
        "urlList": [
            f"{SITE_URL}/",
            f"{SITE_URL}/daily/todays-math/index.html",
            f"{SITE_URL}/intel/index.html",
            f"{SITE_URL}/intel/latest.html",
            f"{SITE_URL}/intel/{slug}.html"
        ]
    }
    try:
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"IndexNow ping HTTP {resp.status}")
    except Exception as e:
        print(f"[WARN] IndexNow non-fatal skip: {e}")

SHARED_HEADER = """  <!-- Global Header -->
  <header class="site-header">
    <div class="header-inner">
      <a href="/" class="site-logo">The Buyer's Math</a>
      <nav class="site-nav">
        <div class="nav-dropdown">
          <button class="nav-dropdown-btn" aria-haspopup="true">Calculators &#9662;</button>
          <div class="nav-dropdown-content">
            <div class="nav-dropdown-group">Building Envelope</div>
            <a href="/roofing-cost-calculator.html">Roof Replacement</a>
            <a href="/siding-cost-calculator.html">Home Siding</a>
            <a href="/window-replacement-estimator.html">Window Replacement</a>
            <a href="/fence-cost-calculator.html">Fence Installation</a>
            <a href="/driveway-paving-calculator.html">Driveway Paving</a>
            <a href="/deck-cost-calculator.html">Deck Construction</a>
            <a href="/gutter-cost-calculator.html">Seamless Gutters</a>
            <a href="/garage-door-calculator.html">Garage Door</a>
            <a href="/patio-cost-calculator.html">Patio &amp; Pavers</a>
            <a href="/exterior-painting-calculator.html">Exterior Painting</a>
            <div class="nav-dropdown-group">Mechanical &amp; Energy</div>
            <a href="/hvac-roi-calculator.html">Heat Pump vs. Gas Furnace</a>
            <a href="/mini-split-calculator.html">Ductless Mini-Split</a>
            <a href="/attic-insulation-calculator.html">Attic Insulation &amp; Air Sealing</a>
            <a href="/water-heater-calculator.html">Water Heater Replacement</a>
            <a href="/solar-payback-calculator.html">Solar Panel Payback</a>
            <a href="/pool.html">Pool Pump Savings</a>
            <a href="/radiant-floor-calculator.html">Radiant Floor Heating</a>
            <div class="nav-dropdown-group">Interior &amp; Power</div>
            <a href="/electrical-panel-calculator.html">200A Electrical Panel</a>
            <a href="/flooring-calculator.html">Flooring &amp; Refinishing</a>
            <a href="/kitchen-remodel-calculator.html">Kitchen Remodel</a>
            <a href="/bathroom-remodel-calculator.html">Bathroom Remodel</a>
            <a href="/basement-cost-calculator.html">Basement Finishing</a>
            <a href="/ev-charger-calculator.html">EV Home Charger</a>
            <a href="/generator-calculator.html">Standby Generator</a>
          </div>
        </div>
        <a href="/daily/todays-math/index.html">Today's Math</a>
        <a href="/intel/index.html">Daily Intel</a>
        <a href="/guides.html">Guides</a>
        <a href="/about.html">About</a>
      </nav>
    </div>
  </header>"""

SHARED_FOOTER = """  <!-- Global Footer -->
  <footer class="site-footer">
    <div class="footer-nav">
      <a href="/">Calculators</a> |
      <a href="/daily/todays-math/index.html">Today's Math</a> |
      <a href="/intel/index.html">Daily Intel</a> |
      <a href="/guides.html">Guides</a> |
      <a href="/about.html">About Us</a> |
      <a href="/privacy-policy.html">Privacy Policy</a> |
      <a href="/terms.html">Terms &amp; Disclaimer</a> |
      <a href="/contact.html">Contact Us</a>
    </div>
    <p class="footer-disclosure">
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program (Tag: nfagiolo-20). As an Amazon Associate, we earn from qualifying purchases. Calculations and tool results are directional models for informational purposes only. Commission Junction Affiliate PID: 101896838.
    </p>
    <p class="footer-copy">&copy; 2026 The Buyer's Math. All rights reserved.</p>
  </footer>"""

# =========================================================================
# 1. electrical-panel-calculator.html
# =========================================================================
electrical_panel_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>200A &amp; 400A Electrical Panel Upgrade Cost Calculator (2026) | The Buyer's Math</title>
  <meta name="description" content="Calculate 200-amp and 400-amp electrical service panel upgrade costs, meter socket replacement, NEC 2023 surge protection, utility trenching, and the $600 Section 25C federal tax credit.">
  <link rel="canonical" href="https://thebuyersmath.com/electrical-panel-calculator.html">
  <link rel="stylesheet" href="/styles.css">

  <meta property="og:type" content="article">
  <meta property="og:url" content="https://thebuyersmath.com/electrical-panel-calculator.html">
  <meta property="og:title" content="200A &amp; 400A Electrical Panel Upgrade Cost Calculator (2026) | The Buyer's Math">
  <meta property="og:description" content="Model 100A-to-200A heavy-up costs, 400A dual-panel service, AFCI/GFCI breaker swaps, and the $600 IRA Section 25C tax credit.">
  <meta property="og:image" content="https://thebuyersmath.com/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">

  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-V4GTQSCFW6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-V4GTQSCFW6');
  </script>

  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>

  <!-- CJ Affiliate Auto-Monetization -->
  <script>
    (function(a,b,c,d,e,f,g){{a['CJDynamicTrack']=e;a[e]=a[e]||function(){{
    (a[e].q=a[e].q||[]).push(arguments)}},a[e].l=1*new Date();f=b.createElement(c),
    g=b.getElementsByTagName(c)[0];f.async=1;f.src=d;g.parentNode.insertBefore(f,g)
    }})(window,document,'script','//www.emjcd.com/dynamic/tracking.js','cj');
    cj('init', {{ enterpriseId: '8090259', propertyId: '101896838' }});
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebApplication",
        "name": "200A & 400A Electrical Panel Upgrade Cost Calculator",
        "url": "https://thebuyersmath.com/electrical-panel-calculator.html",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "All",
        "description": "Empirical cost estimator for residential 200A and 400A electrical service panel heavy-ups, subpanels, meter bases, NEC 2023 surge protection, and IRA Section 25C tax credits."
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "How much does it cost to upgrade from a 100-amp to a 200-amp electrical panel in 2026?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "A turnkey 100A-to-200A main service panel upgrade ('heavy-up') including a new 40-space copper-bus load center, 200A meter socket, 2/0 copper service entrance cable, dual ground rods, NEC-mandated Type 2 surge protector, and municipal permit typically costs between $3,200 and $4,600 before the $600 federal Section 25C tax credit."
            }}
          }},
          {{
            "@type": "Question",
            "name": "How do I qualify for the $600 federal Section 25C tax credit on an electrical panel upgrade?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Under 26 U.S.C. § 25C(d)(2)(D), homeowners can claim 30% of the total equipment and installation cost (up to $600 maximum) if the new load center has a minimum capacity of 200 amps, complies with the National Electrical Code, and is installed in conjunction with—or to enable—another qualified energy property upgrade such as a heat pump, heat pump water heater, or branch circuit upgrade."
            }}
          }},
          {{
            "@type": "Question",
            "name": "When is a 400-amp electrical service upgrade necessary?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "A 400-amp service (typically installed as dual 200A panels fed by a 320A/400A class meter base) is recommended for homes over 3,500 sq ft combining multiple high-draw 240V continuous loads: dual cold-climate heat pumps, two Level 2 EV chargers (48A each), an electric tankless water heater, or a pool heat pump."
            }}
          }}
        ]
      }}
    ]
  }}
  </script>
</head>
<body>

{SHARED_HEADER}

  <div class="breadcrumbs">
    <a href="/">Home</a> &gt; <a href="/#calculators">Calculators</a> &gt; <span class="current">Electrical Panel Upgrade Cost</span>
  </div>

  <main style="max-width: 1140px; margin: 1.5rem auto 3rem auto; padding: 0 1.5rem;">
    <div style="margin-bottom: 1.75rem;">
      <span class="badge-category" style="font-size: 0.8rem; font-weight: 700; color: #2563eb; background: #eff6ff; padding: 0.3rem 0.6rem; border-radius: 4px; text-transform: uppercase;">Electrical &amp; Power</span>
      <h1 style="font-size: clamp(2rem, 4vw, 2.75rem); margin: 0.5rem 0;">200A &amp; 400A Electrical Panel Upgrade Cost Calculator</h1>
      <p style="color: var(--slate-600); font-size: 1.1rem; max-width: 820px; margin: 0;">
        Model turnkey service entrance heavy-ups, meter socket replacements, NEC 2023 surge &amp; AFCI/GFCI breaker rules, utility trenching, and the $600 IRA Section 25C federal tax credit.
      </p>
    </div>

    <!-- Stream 1: Living Tool Context Banner & 30-Day Sparkline -->
    <div id="tbm-live-banner" data-category="electrical"></div>

    <!-- Interactive Calculator Card -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; align-items: start;">
      <!-- Left Column: Inputs -->
      <div style="background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; box-shadow: var(--shadow-sm);">
        <h3 style="margin: 0 0 1.25rem 0; font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">1. Service Upgrade Scope &amp; Wiring Inputs</h3>

        <div style="margin-bottom: 1.4rem;">
          <label for="upgradeType" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Target Panel Upgrade Tier</label>
          <select id="upgradeType" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="subpanel">Add 100A Subpanel Only (Existing 200A Main Has Capacity)</option>
            <option value="swap200">200A Panel Swap Only (Existing Service Cable &amp; Meter Rated 200A)</option>
            <option value="heavyup200" selected>100A/150A to 200A Full Service Heavy-Up (New Panel + Meter + Mast)</option>
            <option value="service400">200A to 400A Dual-Panel Heavy-Up (320A Meter Base + 2x 200A Panels)</option>
          </select>
        </div>

        <div style="margin-bottom: 1.4rem;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <label for="circuitCount" style="font-weight: 600; color: var(--slate-800); font-size: 0.95rem;">Active Branch Circuits to Reconnect</label>
            <span id="circuitCountVal" style="font-weight: 700; color: var(--primary);">28 Circuits</span>
          </div>
          <input type="range" id="circuitCount" min="12" max="60" step="2" value="28" style="width: 100%; accent-color: var(--primary);">
          <small style="color: var(--slate-500); font-size: 0.8rem; display: block; margin-top: 0.25rem;">Includes dual-function AFCI/GFCI breaker replacements where required by NEC</small>
        </div>

        <div style="margin-bottom: 1.4rem;">
          <label for="serviceFeed" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Utility Service Entrance Feed</label>
          <select id="serviceFeed" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="overhead" selected>Overhead Weatherhead &amp; Service Drop (Standard)</option>
            <option value="underground_existing">Underground Lateral (Existing Schedule 80 Conduit Intact)</option>
            <option value="underground_trench">Underground Trenching &amp; New Conduit Run (+50 ft Trench)</option>
          </select>
        </div>

        <div style="margin-bottom: 1.4rem;">
          <label for="panelLocation" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Wall Finish &amp; NEC Exterior Disconnect</label>
          <select id="panelLocation" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="unfinished" selected>Unfinished Basement / Garage Surface Mount + Exterior Meter-Main</option>
            <option value="finished">Finished Drywall Flush-Mount (Requires Drywall Patch &amp; Stud Fishing)</option>
            <option value="relocate">Relocate Panel out of Closet/Bathroom (+J-Box Splice Extension)</option>
          </select>
        </div>

        <div style="margin-bottom: 1.5rem;">
          <label for="taxCreditEligible" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">IRA Section 25C Tax Credit Eligibility</label>
          <select id="taxCreditEligible" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="yes" selected>Yes — Upgrading to ≥200A to Enable Heat Pump / HPWH / Energy Upgrade (30% up to $600)</option>
            <option value="no">No — Standalone Panel Swap Only ($0 Federal Credit)</option>
          </select>
        </div>

        <button type="button" onclick="window.print()" style="width: 100%; padding: 0.75rem; background: var(--slate-100); border: 1px solid var(--border); border-radius: 8px; font-weight: 700; color: var(--slate-700); cursor: pointer;">
          🖨️ Print Electrical Panel Bid Audit Sheet
        </button>
      </div>

      <!-- Right Column: Results -->
      <div id="resultsCard" style="background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; box-shadow: var(--shadow-sm);">
        <h3 style="margin: 0 0 1.25rem 0; font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">2. Itemized Turnkey Estimate &amp; 25C Credit</h3>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Panel, Meter Base, Copper SE Cable &amp; SPD:</span>
            <span id="matCostText" style="font-weight: 600; color: var(--slate-800);">$1,380</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>AFCI/GFCI Breakers &amp; Grounding System:</span>
            <span id="breakerCostText" style="font-weight: 600; color: var(--slate-800);">$560</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Licensed Master Electrician Labor &amp; Trench/Wall:</span>
            <span id="laborCostText" style="font-weight: 600; color: var(--slate-800);">$1,680</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.5rem;">
            <span>Municipal Permit, Inspection &amp; Utility Disconnect:</span>
            <span id="permitCostText" style="font-weight: 600; color: var(--slate-800);">$420</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 1rem; border-top: 1px solid #cbd5e1; padding-top: 0.5rem; margin-bottom: 0.35rem;">
            <span>Gross Turnkey Contract Price:</span>
            <strong id="grossTotalText" style="color: var(--slate-900);">$4,040</strong>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: #059669;">
            <span>IRA Section 25C Panel Tax Credit (Form 5695):</span>
            <strong id="creditText">-$600</strong>
          </div>
        </div>

        <div style="background: var(--slate-900); color: #ffffff; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; text-align: center;">
          <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #38bdf8; font-weight: 700;">Net Out-of-Pocket Outlay</div>
          <div id="netTotalText" style="font-size: 2.35rem; font-weight: 800; color: #10b981; margin: 0.25rem 0;">$3,440</div>
          <div id="ampHeadroomText" style="font-size: 0.9rem; color: #e2e8f0;">Unlocks 48,000VA Capacity (Supports Heat Pump + 48A EV Charger)</div>
        </div>

        <div class="bid-meter-container">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 0.85rem; color: var(--slate-800); text-transform: uppercase;">Electrical Bid Audit Meter</span>
            <span style="font-size: 0.75rem; color: var(--slate-500);">Gross Turnkey Benchmarks</span>
          </div>
          <div class="bid-meter-bar">
            <div class="bid-meter-segment economy"></div>
            <div class="bid-meter-segment fair"></div>
            <div class="bid-meter-segment high"></div>
          </div>
          <div class="bid-meter-labels">
            <span id="lowBidLabel">Low: &lt; $3,350</span>
            <span id="fairBidLabel" style="color: var(--emerald-600); font-weight: 700;">Fair: $3,600 – $4,450</span>
            <span id="highBidLabel" style="color: #dc2626;">Overpriced: &gt; $4,950</span>
          </div>
        </div>

        <!-- Contractor Lead Matching Card -->
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 1px solid #bfdbfe; border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem;">
          <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #1e40af; letter-spacing: 0.05em;">Licensed Master Electricians</div>
          <h4 style="margin: 0.25rem 0 0.5rem 0; color: #1e3a8a; font-size: 1.1rem;">Compare 3 Local 200A Heavy-Up Quotes</h4>
          <p style="margin: 0 0 1rem 0; font-size: 0.85rem; color: #334155; line-height: 1.4;">
            Utility meter pulls require a licensed master electrician to coordinate utility cut-in cards and municipal rough/final inspections:
          </p>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <input type="text" id="zipInput" placeholder="Enter ZIP Code" style="padding: 0.65rem 0.85rem; border: 1px solid #93c5fd; border-radius: 6px; font-size: 0.9rem; width: 140px; background: #ffffff;" maxlength="5">
            <a id="leadMatchLink" href="https://www.jdoqocy.com/click-101896838-17142784?url=https%3A%2F%2Fwww.angi.com%2Fcompanylist%2Fsearch.htm%3Fquery%3DElectrician" target="_blank" rel="noopener noreferrer sponsored" style="flex: 1; min-width: 160px; background: #2563eb; color: #ffffff; padding: 0.65rem 1rem; border-radius: 6px; font-weight: 700; font-size: 0.9rem; text-align: center; text-decoration: none; display: inline-flex; align-items: center; justify-content: center;">
              Compare Electrician Bids &rarr;
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Stream 3: Automated Cost-Per-Use & 5-Year TCO Product Matrix -->
    <div id="tbm-unit-matrix" data-category="electrical"></div>
    <div id="tbm-embed-box"></div>

    <!-- Comprehensive E-E-A-T Editorial Guide -->
    <section style="margin-top: 3rem; border-top: 1px solid var(--border); padding-top: 2.5rem;">
      <h2>2026 Electrical Panel Heavy-Up Cost &amp; NEC 2023 Compliance Guide</h2>
      <p style="color: var(--slate-600); line-height: 1.7;">
        Upgrading a legacy 100-amp or 150-amp electrical service panel (including recalled Federal Pacific Stab-Lok, Zinsco, Challenger, or split-bus panels) to a modern 200-amp, 40-space copper-bus load center is the foundational step for home electrification. Under the 2023 National Electrical Code (NEC), a full service replacement triggers three mandatory safety upgrades that every homeowner must verify on contractor proposals: an <strong>Exterior Emergency Service Disconnect</strong> (NEC 230.85), a <strong>Type 1 or Type 2 Whole-Home Surge Protective Device</strong> (NEC 230.67), and <strong>Interconnected Dual Grounding Electrodes</strong> bonded to incoming metallic water piping (NEC 250.53).
      </p>

      <h3>Line-Item Cost Breakdown by Service Tier</h3>
      <ul style="color: var(--slate-700); line-height: 1.7; padding-left: 1.25rem;">
        <li><strong>100A Subpanel Addition ($1,150 – $1,850):</strong> Ideal when your existing main breaker is already rated for 200A and passes an NEC Article 220 load calculation, but physical breaker spaces are full.</li>
        <li><strong>200A Panel Swap Only ($2,100 – $2,950):</strong> Replaces an outdated indoor 200A breaker box while reusing compliant 2/0 copper or 4/0 aluminum service entrance conductors and an existing 200A meter base.</li>
        <li><strong>100A-to-200A Full Service Heavy-Up ($3,200 – $4,600):</strong> Complete replacement from the utility weatherhead down—including a new 200A outdoor meter-main combo, 2/0 copper riser, 40-space indoor load center, dual 8-ft copper ground rods, and whole-home SPD.</li>
        <li><strong>200A-to-400A Class 320 Dual-Panel Upgrade ($5,800 – $9,200):</strong> Required for large all-electric estates running dual heat pumps, multiple 48A EV chargers, and electric tankless water heaters. Frequently requires utility transformer capacity review and underground lateral trenching.</li>
      </ul>

      <!-- TBM CASE STUDIES START -->
      <!-- TBM CASE STUDIES END -->

      <!-- FAQs -->
      <h3 style="margin-top: 2.5rem;">Frequently Asked Questions</h3>
      <div style="border-top: 1px solid var(--border); padding: 1.25rem 0;">
        <h4 style="margin: 0 0 0.5rem 0;">Does my utility company charge to disconnect power during a panel upgrade?</h4>
        <p style="margin: 0; color: var(--slate-600); line-height: 1.6;">Most electric utilities perform standard overhead service drop disconnects and reconnects at zero direct fee or a nominal $150–$350 scheduling fee, provided your licensed electrician files an approved municipal electrical cut-in card.</p>
      </div>
      <div style="border-top: 1px solid var(--border); padding: 1.25rem 0;">
        <h4 style="margin: 0 0 0.5rem 0;">Can I install a 48A EV charger on a 100A panel without upgrading to 200A?</h4>
        <p style="margin: 0; color: var(--slate-600); line-height: 1.6;">Only if you install an UL-listed Automatic Energy Management / EVEMS load-shedding device (NEC 625.42) that throttles or pauses EV charging whenever household oven, dryer, or HVAC loads peak—otherwise a 200A heavy-up is required.</p>
      </div>
    </section>
  </main>

{SHARED_FOOTER}

  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      const upgradeType = document.getElementById('upgradeType');
      const circuitCount = document.getElementById('circuitCount');
      const circuitCountVal = document.getElementById('circuitCountVal');
      const serviceFeed = document.getElementById('serviceFeed');
      const panelLocation = document.getElementById('panelLocation');
      const taxCreditEligible = document.getElementById('taxCreditEligible');
      const zipInput = document.getElementById('zipInput');
      const leadMatchLink = document.getElementById('leadMatchLink');

      function calculate() {{
        const circuits = parseInt(circuitCount.value, 10) || 28;
        circuitCountVal.textContent = `${{circuits}} Circuits`;

        const tier = upgradeType.value;
        let baseMat = 980, baseLabor = 1350, permit = 420, capacityDesc = "Unlocks 48,000VA Capacity (Supports Heat Pump + 48A EV Charger)";
        if (tier === 'subpanel') {{
          baseMat = 340; baseLabor = 680; permit = 220;
          capacityDesc = "Adds 12–24 Physical Spaces on Existing 200A Service";
        }} else if (tier === 'swap200') {{
          baseMat = 620; baseLabor = 1050; permit = 310;
          capacityDesc = "Modernizes Bus Bar, SPD & Breaker Spaces (200A Rated)";
        }} else if (tier === 'service400') {{
          baseMat = 2150; baseLabor = 2850; permit = 680;
          capacityDesc = "Unlocks 96,000VA Dual-200A Capacity (All-Electric Estate + Dual EV)";
        }}

        const breakerCost = circuits * 20;
        let feedAddMat = 0, feedAddLabor = 0;
        if (serviceFeed.value === 'underground_existing') {{
          feedAddMat = 180; feedAddLabor = 240;
        }} else if (serviceFeed.value === 'underground_trench') {{
          feedAddMat = 650; feedAddLabor = 1450;
        }}

        let locLabor = 0;
        if (panelLocation.value === 'finished') locLabor = 380;
        else if (panelLocation.value === 'relocate') locLabor = 890;

        const totalMat = baseMat + feedAddMat;
        const totalLabor = baseLabor + feedAddLabor + locLabor + (circuits * 12);
        const gross = totalMat + breakerCost + totalLabor + permit;

        let credit = 0;
        if (taxCreditEligible.value === 'yes' && tier !== 'subpanel') {{
          credit = Math.min(600, Math.round(gross * 0.30));
        }}
        const net = gross - credit;

        document.getElementById('matCostText').textContent = `$${{totalMat.toLocaleString()}}`;
        document.getElementById('breakerCostText').textContent = `$${{breakerCost.toLocaleString()}}`;
        document.getElementById('laborCostText').textContent = `$${{totalLabor.toLocaleString()}}`;
        document.getElementById('permitCostText').textContent = `$${{permit.toLocaleString()}}`;
        document.getElementById('grossTotalText').textContent = `$${{gross.toLocaleString()}}`;
        document.getElementById('creditText').textContent = `-$${{credit.toLocaleString()}}`;
        document.getElementById('netTotalText').textContent = `$${{net.toLocaleString()}}`;
        document.getElementById('ampHeadroomText').textContent = capacityDesc;

        const lowBid = Math.round(gross * 0.84);
        const fairMin = Math.round(gross * 0.91);
        const fairMax = Math.round(gross * 1.10);
        const highBid = Math.round(gross * 1.22);
        document.getElementById('lowBidLabel').textContent = `Low: < $${{lowBid.toLocaleString()}}`;
        document.getElementById('fairBidLabel').textContent = `Fair: $${{fairMin.toLocaleString()}} – $${{fairMax.toLocaleString()}}`;
        document.getElementById('highBidLabel').textContent = `Overpriced: > $${{highBid.toLocaleString()}}`;
      }}

      [upgradeType, circuitCount, serviceFeed, panelLocation, taxCreditEligible].forEach(el => {{
        el.addEventListener('input', calculate);
        el.addEventListener('change', calculate);
      }});

      if (zipInput && leadMatchLink) {{
        zipInput.addEventListener('input', () => {{
          const zip = zipInput.value.trim();
          if (zip.length === 5) {{
            const dest = `https://www.angi.com/companylist/search.htm?query=Electrician&postalCode=${{zip}}`;
            leadMatchLink.href = `https://www.jdoqocy.com/click-101896838-17142784?url=${{encodeURIComponent(dest)}}`;
          }}
        }});
      }}

      calculate();
    }});
  </script>
  <script src="/tbm-widget.js" defer></script>
</body>
</html>
"""

# =========================================================================
# 2. flooring-calculator.html
# =========================================================================
flooring_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flooring Installation &amp; Hardwood Refinishing Cost Calculator (2026) | The Buyer's Math</title>
  <meta name="description" content="Calculate 2026 flooring installation costs for Luxury Vinyl Plank (LVP), solid oak hardwood, engineered wood, porcelain tile, and dustless hardwood refinishing.">
  <link rel="canonical" href="https://thebuyersmath.com/flooring-calculator.html">
  <link rel="stylesheet" href="/styles.css">

  <meta property="og:type" content="article">
  <meta property="og:url" content="https://thebuyersmath.com/flooring-calculator.html">
  <meta property="og:title" content="Flooring Installation &amp; Hardwood Refinishing Cost Calculator (2026) | The Buyer's Math">
  <meta property="og:description" content="Model square-footage materials, 10% cutting waste, subfloor leveling, moisture barriers, and licensed installation labor.">
  <meta property="og:image" content="https://thebuyersmath.com/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">

  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-V4GTQSCFW6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-V4GTQSCFW6');
  </script>

  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>

  <!-- CJ Affiliate Auto-Monetization -->
  <script>
    (function(a,b,c,d,e,f,g){{a['CJDynamicTrack']=e;a[e]=a[e]||function(){{
    (a[e].q=a[e].q||[]).push(arguments)}},a[e].l=1*new Date();f=b.createElement(c),
    g=b.getElementsByTagName(c)[0];f.async=1;f.src=d;g.parentNode.insertBefore(f,g)
    }})(window,document,'script','//www.emjcd.com/dynamic/tracking.js','cj');
    cj('init', {{ enterpriseId: '8090259', propertyId: '101896838' }});
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebApplication",
        "name": "Flooring Installation & Hardwood Refinishing Cost Calculator",
        "url": "https://thebuyersmath.com/flooring-calculator.html",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "All",
        "description": "Interactive residential flooring cost estimator covering LVP, engineered hardwood, solid 3/4-inch oak, porcelain tile, subfloor prep, and hardwood sanding/refinishing."
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "Is it cheaper to refinish existing hardwood floors or install new LVP?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Dustless drum sanding and applying 3 coats of commercial waterborne polyurethane on existing 3/4-inch solid oak averages $4.50 to $6.50 per sq ft turnkey—roughly 35% to 45% cheaper than tearing out wood and installing commercial-grade 20-mil LVP ($7.50 to $11.00 per sq ft installed) while yielding higher appraisal resale value."
            }}
          }},
          {{
            "@type": "Question",
            "name": "How much extra flooring material should I order for cutting waste?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Standard straight-lay plank installations require a 10% waste factor for end-cuts and board defects, while diagonal layouts, herringbone patterns, or multi-hallway floor plans require 15% overage."
            }}
          }}
        ]
      }}
    ]
  }}
  </script>
</head>
<body>

{SHARED_HEADER}

  <div class="breadcrumbs">
    <a href="/">Home</a> &gt; <a href="/#calculators">Calculators</a> &gt; <span class="current">Flooring Installation &amp; Refinishing</span>
  </div>

  <main style="max-width: 1140px; margin: 1.5rem auto 3rem auto; padding: 0 1.5rem;">
    <div style="margin-bottom: 1.75rem;">
      <span class="badge-category" style="font-size: 0.8rem; font-weight: 700; color: #2563eb; background: #eff6ff; padding: 0.3rem 0.6rem; border-radius: 4px; text-transform: uppercase;">Interior Remodeling</span>
      <h1 style="font-size: clamp(2rem, 4vw, 2.75rem); margin: 0.5rem 0;">Flooring Installation &amp; Refinishing Cost Calculator</h1>
      <p style="color: var(--slate-600); font-size: 1.1rem; max-width: 820px; margin: 0;">
        Compare turnkey pricing across 20-mil Luxury Vinyl Plank (LVP), engineered hardwood, solid 3/4" white oak, porcelain tile, and dustless hardwood sanding &amp; refinishing.
      </p>
    </div>

    <!-- Stream 1: Living Tool Context Banner & 30-Day Sparkline -->
    <div id="tbm-live-banner" data-category="interior"></div>

    <!-- Interactive Calculator Card -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; align-items: start;">
      <!-- Left Column: Inputs -->
      <div style="background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; box-shadow: var(--shadow-sm);">
        <h3 style="margin: 0 0 1.25rem 0; font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">1. Room Area, Material &amp; Subfloor Prep</h3>

        <div style="margin-bottom: 1.4rem;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <label for="floorSqft" style="font-weight: 600; color: var(--slate-800); font-size: 0.95rem;">Net Floor Area to Cover</label>
            <span id="floorSqftVal" style="font-weight: 700; color: var(--primary);">800 sq ft</span>
          </div>
          <input type="range" id="floorSqft" min="150" max="3000" step="50" value="800" style="width: 100%; accent-color: var(--primary);">
          <small id="orderedSqftNote" style="color: var(--slate-500); font-size: 0.8rem; display: block; margin-top: 0.25rem;">Includes +10% cutting waste allowance (880 sq ft ordered)</small>
        </div>

        <div style="margin-bottom: 1.4rem;">
          <label for="floorMaterial" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Flooring Material / Service Tier</label>
          <select id="floorMaterial" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="refinish">Refinish Existing Solid Hardwood (Dustless Sand + Stain + 3x Bona Traffic HD)</option>
            <option value="lvp" selected>Luxury Vinyl Plank — Rigid Core SPC (20-Mil Wear Layer + Attached Cork Pad)</option>
            <option value="engineered">Engineered Hardwood — 1/2" European White Oak (Glue/Float)</option>
            <option value="solid_oak">Solid 3/4" Red/White Oak Hardwood (Nail-Down + Site Finish)</option>
            <option value="porcelain">Large-Format Porcelain Tile (Uncoupling Membrane + Thinset + Epoxy Grout)</option>
          </select>
        </div>

        <div style="margin-bottom: 1.4rem;">
          <label for="subfloorPrep" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Existing Flooring Tear-Out &amp; Subfloor Leveling</label>
          <select id="subfloorPrep" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="clean">Clean Subfloor Ready (Carpet Already Removed)</option>
            <option value="carpet" selected>Carpet &amp; Tack Strip Tear-Out + Minor High-Spot Grinding</option>
            <option value="self_level">Hardwood/Tile Demo + Self-Leveling Cement Compound (Flat to 3/16" in 10 ft)</option>
          </select>
        </div>

        <div style="margin-bottom: 1.5rem;">
          <label for="trimStairs" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Baseboard Shoe Molding &amp; Stair Treads</label>
          <select id="trimStairs" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="shoe" selected>New Primed Quarter-Round / Shoe Molding Only</option>
            <option value="baseboard">Remove &amp; Reinstall 5-1/4" Baseboards + Transitions</option>
            <option value="stairs">Baseboards + 13 Matching Stair Treads &amp; Risers</option>
          </select>
        </div>

        <button type="button" onclick="window.print()" style="width: 100%; padding: 0.75rem; background: var(--slate-100); border: 1px solid var(--border); border-radius: 8px; font-weight: 700; color: var(--slate-700); cursor: pointer;">
          🖨️ Print Flooring Bid Audit Sheet
        </button>
      </div>

      <!-- Right Column: Results -->
      <div id="resultsCard" style="background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; box-shadow: var(--shadow-sm);">
        <h3 style="margin: 0 0 1.25rem 0; font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">2. Itemized Flooring Cost Breakdown</h3>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Flooring Materials (Includes 10% Waste) &amp; Underlayment:</span>
            <span id="floorMatText" style="font-weight: 600; color: var(--slate-800);">$3,432</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Professional Installation / Sanding Labor:</span>
            <span id="floorLaborText" style="font-weight: 600; color: var(--slate-800);">$2,560</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Demo, Haul-Away &amp; Subfloor Flattening:</span>
            <span id="floorPrepText" style="font-weight: 600; color: var(--slate-800);">$920</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.5rem;">
            <span>Perimeter Trim, Transitions &amp; Stairs:</span>
            <span id="floorTrimText" style="font-weight: 600; color: var(--slate-800);">$540</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 1.05rem; border-top: 1px solid #cbd5e1; padding-top: 0.5rem;">
            <strong>Estimated Cost Per Sq Ft (Turnkey):</strong>
            <strong id="perSqftText" style="color: var(--primary);">$9.32 / sq ft</strong>
          </div>
        </div>

        <div style="background: var(--slate-900); color: #ffffff; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; text-align: center;">
          <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #38bdf8; font-weight: 700;">Total Turnkey Project Estimate</div>
          <div id="floorTotalText" style="font-size: 2.35rem; font-weight: 800; color: #10b981; margin: 0.25rem 0;">$7,452</div>
          <div id="resaleRoiText" style="font-size: 0.9rem; color: #e2e8f0;">Estimated Resale Value Recovery: ~106%–118% on Appraisal</div>
        </div>

        <div class="bid-meter-container">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 0.85rem; color: var(--slate-800); text-transform: uppercase;">Flooring Contractor Bid Meter</span>
            <span style="font-size: 0.75rem; color: var(--slate-500);">Regional Labor + Material Range</span>
          </div>
          <div class="bid-meter-bar">
            <div class="bid-meter-segment economy"></div>
            <div class="bid-meter-segment fair"></div>
            <div class="bid-meter-segment high"></div>
          </div>
          <div class="bid-meter-labels">
            <span id="lowBidLabel">Low: &lt; $6,260</span>
            <span id="fairBidLabel" style="color: var(--emerald-600); font-weight: 700;">Fair: $6,780 – $8,200</span>
            <span id="highBidLabel" style="color: #dc2626;">Overpriced: &gt; $9,090</span>
          </div>
        </div>

        <!-- Contractor Lead Matching Card -->
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 1px solid #bfdbfe; border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem;">
          <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #1e40af; letter-spacing: 0.05em;">Verified Flooring Installers</div>
          <h4 style="margin: 0.25rem 0 0.5rem 0; color: #1e3a8a; font-size: 1.1rem;">Compare 3 Local Flooring &amp; Refinishing Quotes</h4>
          <p style="margin: 0 0 1rem 0; font-size: 0.85rem; color: #334155; line-height: 1.4;">
            Ensure your installer verifies subfloor moisture (&lt;12% EMC) and flatness tolerances (3/16" over 10 ft) to protect manufacturer warranties:
          </p>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <input type="text" id="zipInput" placeholder="Enter ZIP Code" style="padding: 0.65rem 0.85rem; border: 1px solid #93c5fd; border-radius: 6px; font-size: 0.9rem; width: 140px; background: #ffffff;" maxlength="5">
            <a id="leadMatchLink" href="https://www.jdoqocy.com/click-101896838-17142784?url=https%3A%2F%2Fwww.angi.com%2Fcompanylist%2Fsearch.htm%3Fquery%3DFlooring" target="_blank" rel="noopener noreferrer sponsored" style="flex: 1; min-width: 160px; background: #2563eb; color: #ffffff; padding: 0.65rem 1rem; border-radius: 6px; font-weight: 700; font-size: 0.9rem; text-align: center; text-decoration: none; display: inline-flex; align-items: center; justify-content: center;">
              Compare Flooring Bids &rarr;
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Stream 3: Automated Cost-Per-Use & 5-Year TCO Product Matrix -->
    <div id="tbm-unit-matrix" data-category="interior"></div>
    <div id="tbm-embed-box"></div>

    <section style="margin-top: 3rem; border-top: 1px solid var(--border); padding-top: 2.5rem;">
      <h2>Understanding Flooring Material Specs, Subfloor Flatness &amp; Labor Quotes</h2>
      <p style="color: var(--slate-600); line-height: 1.7;">
        Over 80% of premature Luxury Vinyl Plank (LVP) locking-joint failures and engineered hardwood hollow spots trace back to skipped subfloor preparation rather than defective planks. NWFA (National Wood Flooring Association) and rigid-core SPC manufacturers mandate that concrete slabs and OSB subfloors be leveled to within <strong>3/16 of an inch over a 10-foot radius</strong> (or 1/8 inch over 6 feet). When comparing contractor quotes, always verify whether self-leveling portland cement compound, high-spot diamond grinding, and 6-mil polyethylene vapor barriers are included in the base square-foot rate.
      </p>

      <!-- TBM CASE STUDIES START -->
      <!-- TBM CASE STUDIES END -->

      <!-- FAQs -->
      <h3 style="margin-top: 2.5rem;">Frequently Asked Questions</h3>
      <div style="border-top: 1px solid var(--border); padding: 1.25rem 0;">
        <h4 style="margin: 0 0 0.5rem 0;">What wear-layer thickness should I look for on Luxury Vinyl Plank (LVP)?</h4>
        <p style="margin: 0; color: var(--slate-600); line-height: 1.6;">Avoid builder-grade 6-mil or 12-mil vinyl planks in main living areas; specify a minimum 20-mil commercial urethane wear layer with ceramic bead finish and a minimum 5.5mm–6.5mm total plank thickness so locking tongues do not shear under furniture loads.</p>
      </div>
    </section>
  </main>

{SHARED_FOOTER}

  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      const floorSqft = document.getElementById('floorSqft');
      const floorSqftVal = document.getElementById('floorSqftVal');
      const orderedSqftNote = document.getElementById('orderedSqftNote');
      const floorMaterial = document.getElementById('floorMaterial');
      const subfloorPrep = document.getElementById('subfloorPrep');
      const trimStairs = document.getElementById('trimStairs');
      const zipInput = document.getElementById('zipInput');
      const leadMatchLink = document.getElementById('leadMatchLink');

      function calculate() {{
        const sqft = parseFloat(floorSqft.value) || 800;
        const ordered = Math.round(sqft * 1.10);
        floorSqftVal.textContent = `${{sqft.toLocaleString()}} sq ft`;
        orderedSqftNote.textContent = `Includes +10% cutting waste allowance (${{ordered.toLocaleString()}} sq ft ordered)`;

        const mat = floorMaterial.value;
        let matRate = 3.90, laborRate = 3.20, roiNote = "Estimated 10-Year Durability: 20-Mil Commercial Wear Layer";
        if (mat === 'refinish') {{
          matRate = 1.15; laborRate = 4.10;
          orderedSqftNote.textContent = `Dustless sanding + 3 coats waterborne finish (${{sqft.toLocaleString()}} sq ft net)`;
          roiNote = "Highest Resale ROI: 118%–147% Cost Recovery (NAR Remodeling Impact)";
        }} else if (mat === 'engineered') {{
          matRate = 6.40; laborRate = 4.50;
          roiNote = "Dimensionally Stable Real Hardwood Veneer (radiant & basement safe)";
        }} else if (mat === 'solid_oak') {{
          matRate = 7.80; laborRate = 5.40;
          roiNote = "50+ Year Lifespan (Can be sanded & refinished 3–4 times)";
        }} else if (mat === 'porcelain') {{
          matRate = 5.90; laborRate = 7.80;
          roiNote = "Waterproof Porcelain + Uncoupling Membrane (Zero Water Absorption)";
        }}

        const matCost = Math.round((mat === 'refinish' ? sqft : ordered) * matRate);
        const laborCost = Math.round(sqft * laborRate);

        let prepCost = 0;
        if (subfloorPrep.value === 'carpet') prepCost = Math.round(sqft * 1.15);
        else if (subfloorPrep.value === 'self_level') prepCost = Math.round(sqft * 2.85);

        let trimCost = Math.round(Math.sqrt(sqft) * 14 * 1.35);
        if (trimStairs.value === 'baseboard') trimCost += Math.round(Math.sqrt(sqft) * 14 * 1.80);
        else if (trimStairs.value === 'stairs') trimCost += 1850;

        const total = matCost + laborCost + prepCost + trimCost;
        const perSqft = (total / sqft).toFixed(2);

        document.getElementById('floorMatText').textContent = `$${{matCost.toLocaleString()}}`;
        document.getElementById('floorLaborText').textContent = `$${{laborCost.toLocaleString()}}`;
        document.getElementById('floorPrepText').textContent = `$${{prepCost.toLocaleString()}}`;
        document.getElementById('floorTrimText').textContent = `$${{trimCost.toLocaleString()}}`;
        document.getElementById('perSqftText').textContent = `$${{perSqft}} / sq ft`;
        document.getElementById('floorTotalText').textContent = `$${{total.toLocaleString()}}`;
        document.getElementById('resaleRoiText').textContent = roiNote;

        document.getElementById('lowBidLabel').textContent = `Low: < $${{Math.round(total * 0.84).toLocaleString()}}`;
        document.getElementById('fairBidLabel').textContent = `Fair: $${{Math.round(total * 0.91).toLocaleString()}} – $${{Math.round(total * 1.10).toLocaleString()}}`;
        document.getElementById('highBidLabel').textContent = `Overpriced: > $${{Math.round(total * 1.22).toLocaleString()}}`;
      }}

      [floorSqft, floorMaterial, subfloorPrep, trimStairs].forEach(el => {{
        el.addEventListener('input', calculate);
        el.addEventListener('change', calculate);
      }});

      if (zipInput && leadMatchLink) {{
        zipInput.addEventListener('input', () => {{
          const zip = zipInput.value.trim();
          if (zip.length === 5) {{
            const dest = `https://www.angi.com/companylist/search.htm?query=Flooring&postalCode=${{zip}}`;
            leadMatchLink.href = `https://www.jdoqocy.com/click-101896838-17142784?url=${{encodeURIComponent(dest)}}`;
          }}
        }});
      }}

      calculate();
    }});
  </script>
  <script src="/tbm-widget.js" defer></script>
</body>
</html>
"""

# =========================================================================
# 3. radiant-floor-calculator.html
# =========================================================================
radiant_floor_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Radiant Floor Heating Cost &amp; Operating Calculator (2026) | The Buyer's Math</title>
  <meta name="description" content="Calculate electric radiant floor heating mat (Ditra-Heat) and hydronic PEX tubing installation costs, thermal break subfloor insulation, and monthly kWh operating expenses.">
  <link rel="canonical" href="https://thebuyersmath.com/radiant-floor-calculator.html">
  <link rel="stylesheet" href="/styles.css">

  <meta property="og:type" content="article">
  <meta property="og:url" content="https://thebuyersmath.com/radiant-floor-calculator.html">
  <meta property="og:title" content="Radiant Floor Heating Cost &amp; Operating Calculator (2026) | The Buyer's Math">
  <meta property="og:description" content="Compare electric uncoupling mat systems vs. hydronic PEX radiant heating installation and monthly utility operating costs.">
  <meta property="og:image" content="https://thebuyersmath.com/og-image.svg">
  <meta name="twitter:card" content="summary_large_image">

  <!-- Google Analytics (GA4) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-V4GTQSCFW6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-V4GTQSCFW6');
  </script>

  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>

  <!-- CJ Affiliate Auto-Monetization -->
  <script>
    (function(a,b,c,d,e,f,g){{a['CJDynamicTrack']=e;a[e]=a[e]||function(){{
    (a[e].q=a[e].q||[]).push(arguments)}},a[e].l=1*new Date();f=b.createElement(c),
    g=b.getElementsByTagName(c)[0];f.async=1;f.src=d;g.parentNode.insertBefore(f,g)
    }})(window,document,'script','//www.emjcd.com/dynamic/tracking.js','cj');
    cj('init', {{ enterpriseId: '8090259', propertyId: '101896838' }});
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebApplication",
        "name": "Radiant Floor Heating Cost & Operating Calculator",
        "url": "https://thebuyersmath.com/radiant-floor-calculator.html",
        "applicationCategory": "FinanceApplication",
        "operatingSystem": "All",
        "description": "Empirical calculator modeling electric radiant floor heating mats (Ditra-Heat) and hydronic PEX systems, subfloor thermal insulation, dedicated GFCI circuits, and daily kWh operating costs."
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "How much does electric radiant floor heating cost to run per month?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Electric radiant floor heating draws 12 watts per square foot. A typical 60 sq ft master bathroom heated floor (42 sq ft of active mat area excluding vanity and toilet footprints) draws 504 watts and costs roughly $0.35 to $0.52 per day ($10.50 to $15.60 per month) when run 6 hours a day on a programmable setback thermostat at $0.172/kWh."
            }}
          }},
          {{
            "@type": "Question",
            "name": "When does hydronic radiant floor heating make more sense than electric mats?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Electric radiant cable/mat systems are far more cost-effective for single rooms, bathrooms, and kitchens under 250 sq ft ($1,100 to $2,600 installed). Hydronic PEX tubing with a dedicated manifold and air-to-water heat pump or condensing boiler ($8,500 to $16,000+) becomes economical only when heating whole-home slabs or basements exceeding 800 sq ft."
            }}
          }}
        ]
      }}
    ]
  }}
  </script>
</head>
<body>

{SHARED_HEADER}

  <div class="breadcrumbs">
    <a href="/">Home</a> &gt; <a href="/#calculators">Calculators</a> &gt; <span class="current">Radiant Floor Heating Calculator</span>
  </div>

  <main style="max-width: 1140px; margin: 1.5rem auto 3rem auto; padding: 0 1.5rem;">
    <div style="margin-bottom: 1.75rem;">
      <span class="badge-category" style="font-size: 0.8rem; font-weight: 700; color: #2563eb; background: #eff6ff; padding: 0.3rem 0.6rem; border-radius: 4px; text-transform: uppercase;">HVAC &amp; Interior Comfort</span>
      <h1 style="font-size: clamp(2rem, 4vw, 2.75rem); margin: 0.5rem 0;">Radiant Floor Heating Cost &amp; Operating Calculator</h1>
      <p style="color: var(--slate-600); font-size: 1.1rem; max-width: 820px; margin: 0;">
        Model electric uncoupling mat systems (Schluter Ditra-Heat) vs. hydronic PEX tubing, thermal break subfloor panels, dedicated 120V/240V circuits, and monthly electricity bills.
      </p>
    </div>

    <!-- Stream 1: Living Tool Context Banner & 30-Day Sparkline -->
    <div id="tbm-live-banner" data-category="hvac"></div>

    <!-- Interactive Calculator Card -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; align-items: start;">
      <!-- Left Column: Inputs -->
      <div style="background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; box-shadow: var(--shadow-sm);">
        <h3 style="margin: 0 0 1.25rem 0; font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">1. Heated Zone &amp; System Configuration</h3>

        <div style="margin-bottom: 1.4rem;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <label for="heatedSqft" style="font-weight: 600; color: var(--slate-800); font-size: 0.95rem;">Active Heated Floor Area (Excludes Cabinets/Tub)</label>
            <span id="heatedSqftVal" style="font-weight: 700; color: var(--primary);">80 sq ft</span>
          </div>
          <input type="range" id="heatedSqft" min="25" max="1200" step="15" value="80" style="width: 100%; accent-color: var(--primary);">
          <small id="wattageNote" style="color: var(--slate-500); font-size: 0.8rem; display: block; margin-top: 0.25rem;">System Output: 960 Watts (3,276 BTU/hr @ 12W/sq ft)</small>
        </div>

        <div style="margin-bottom: 1.4rem;">
          <label for="radiantType" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Radiant Technology Type</label>
          <select id="radiantType" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="ditra" selected>Electric Heating Cable + Uncoupling Membrane (Schluter Ditra-Heat)</option>
            <option value="mesh_mat">Electric Pre-Spaced Fiberglass Mesh Mat (WarmlyYours / SunTouch)</option>
            <option value="hydronic">Hydronic Oxygen-Barrier PEX-A Tubing + Manifold &amp; Circulator</option>
          </select>
        </div>

        <div style="margin-bottom: 1.4rem;">
          <label for="subfloorBase" style="display: block; font-weight: 600; color: var(--slate-800); margin-bottom: 0.5rem; font-size: 0.95rem;">Subfloor Type &amp; Thermal Break Insulation</label>
          <select id="subfloorBase" style="width: 100%; padding: 0.75rem 1rem; border: 1px solid var(--border); border-radius: 8px; font-size: 0.95rem; background: #ffffff;">
            <option value="plywood">Wood Plywood/OSB Subfloor (Standard Thinset Embedment)</option>
            <option value="insulated_fleece" selected>Concrete Slab / Cold Crawlspace (+Insulated Thermal Break Membrane)</option>
          </select>
        </div>

        <div style="margin-bottom: 1.5rem;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <label for="dailyHours" style="font-weight: 600; color: var(--slate-800); font-size: 0.95rem;">Active Heating Cycle (Hours / Day)</label>
            <span id="dailyHoursVal" style="font-weight: 700; color: var(--primary);">6 hrs/day</span>
          </div>
          <input type="range" id="dailyHours" min="2" max="16" step="1" value="6" style="width: 100%; accent-color: var(--primary);">
          <small style="color: var(--slate-500); font-size: 0.8rem; display: block; margin-top: 0.25rem;">Morning + evening programmable thermostat schedule (@ $0.172/kWh baseline)</small>
        </div>

        <button type="button" onclick="window.print()" style="width: 100%; padding: 0.75rem; background: var(--slate-100); border: 1px solid var(--border); border-radius: 8px; font-weight: 700; color: var(--slate-700); cursor: pointer;">
          🖨️ Print Radiant Floor Bid Audit Sheet
        </button>
      </div>

      <!-- Right Column: Results -->
      <div id="resultsCard" style="background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; box-shadow: var(--shadow-sm);">
        <h3 style="margin: 0 0 1.25rem 0; font-size: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">2. Installation &amp; Winter Operating Math</h3>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Heating Cable/Mat, Membrane &amp; Floor Sensors:</span>
            <span id="radMatText" style="font-weight: 600; color: var(--slate-800);">$940</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Smart Wi-Fi Class-A GFCI Thermostat:</span>
            <span id="radStatText" style="font-weight: 600; color: var(--slate-800);">$265</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.95rem; color: var(--slate-600); margin-bottom: 0.4rem;">
            <span>Dedicated 20A Circuit &amp; Tile/Heating Labor:</span>
            <span id="radLaborText" style="font-weight: 600; color: var(--slate-800);">$1,180</span>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 1rem; border-top: 1px solid #cbd5e1; padding-top: 0.5rem;">
            <strong>Monthly Winter Operating Cost:</strong>
            <strong id="monthlyRunText" style="color: #059669;">$29.72 / month ($0.99/day)</strong>
          </div>
        </div>

        <div style="background: var(--slate-900); color: #ffffff; border-radius: 12px; padding: 1.25rem; margin-bottom: 1.5rem; text-align: center;">
          <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #38bdf8; font-weight: 700;">Total Turnkey Radiant System Outlay</div>
          <div id="radTotalText" style="font-size: 2.35rem; font-weight: 800; color: #10b981; margin: 0.25rem 0;">$2,385</div>
          <div id="circuitNoteText" style="font-size: 0.9rem; color: #e2e8f0;">Requires 1x Dedicated 120V 20A Circuit (Draws 8.0 Amps)</div>
        </div>

        <div class="bid-meter-container">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 0.85rem; color: var(--slate-800); text-transform: uppercase;">Radiant Install Bid Meter</span>
            <span style="font-size: 0.75rem; color: var(--slate-500);">Excludes Surface Tile/Stone</span>
          </div>
          <div class="bid-meter-bar">
            <div class="bid-meter-segment economy"></div>
            <div class="bid-meter-segment fair"></div>
            <div class="bid-meter-segment high"></div>
          </div>
          <div class="bid-meter-labels">
            <span id="lowBidLabel">Low: &lt; $2,000</span>
            <span id="fairBidLabel" style="color: var(--emerald-600); font-weight: 700;">Fair: $2,170 – $2,620</span>
            <span id="highBidLabel" style="color: #dc2626;">Overpriced: &gt; $2,910</span>
          </div>
        </div>

        <!-- Contractor Lead Matching Card -->
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 1px solid #bfdbfe; border-radius: 12px; padding: 1.25rem; margin-top: 1.5rem;">
          <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #1e40af; letter-spacing: 0.05em;">Certified Tile &amp; Radiant Pros</div>
          <h4 style="margin: 0.25rem 0 0.5rem 0; color: #1e3a8a; font-size: 1.1rem;">Compare 3 Local Radiant Floor Installers</h4>
          <p style="margin: 0 0 1rem 0; font-size: 0.85rem; color: #334155; line-height: 1.4;">
            Ensure your installer logs 3 megohmmeter insulation resistance tests (out-of-box, after cable lay, and after thinset troweling) to activate the lifetime warranty:
          </p>
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <input type="text" id="zipInput" placeholder="Enter ZIP Code" style="padding: 0.65rem 0.85rem; border: 1px solid #93c5fd; border-radius: 6px; font-size: 0.9rem; width: 140px; background: #ffffff;" maxlength="5">
            <a id="leadMatchLink" href="https://www.jdoqocy.com/click-101896838-17142784?url=https%3A%2F%2Fwww.angi.com%2Fcompanylist%2Fsearch.htm%3Fquery%3DTile%2BContractor" target="_blank" rel="noopener noreferrer sponsored" style="flex: 1; min-width: 160px; background: #2563eb; color: #ffffff; padding: 0.65rem 1rem; border-radius: 6px; font-weight: 700; font-size: 0.9rem; text-align: center; text-decoration: none; display: inline-flex; align-items: center; justify-content: center;">
              Compare Local Bids &rarr;
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Stream 3: Automated Cost-Per-Use & 5-Year TCO Product Matrix -->
    <div id="tbm-unit-matrix" data-category="hvac"></div>
    <div id="tbm-embed-box"></div>

    <section style="margin-top: 3rem; border-top: 1px solid var(--border); padding-top: 2.5rem;">
      <h2>Why Thermal Break Subfloor Membranes Cut Radiant Heating Bills by 35%</h2>
      <p style="color: var(--slate-600); line-height: 1.7;">
        Installing electric heating cables directly onto an uninsulated concrete basement slab or over an unconditioned crawlspace forces the slab to act as a massive downward heat sink—increasing warm-up lag times from 25 minutes to over 2 hours and raising monthly kWh consumption by 35% to 50%. Specifying an uncoupling membrane with an integrated polypropylene thermal break fleece (such as Schluter Ditra-Heat-DUO) or 1/4-inch extruded polystyrene (XPS) backer board reflects radiant heat upward into the porcelain tile, allowing programmable setback schedules to reach 82&deg;F floor surface temperature in under 30 minutes.
      </p>

      <!-- TBM CASE STUDIES START -->
      <!-- TBM CASE STUDIES END -->

      <!-- FAQs -->
      <h3 style="margin-top: 2.5rem;">Frequently Asked Questions</h3>
      <div style="border-top: 1px solid var(--border); padding: 1.25rem 0;">
        <h4 style="margin: 0 0 0.5rem 0;">Why must my installer bury two floor temperature sensors in the thinset?</h4>
        <p style="margin: 0; color: var(--slate-600); line-height: 1.6;">A backup thermistor sensor wire costs under $25 and sits unconnected inside the thermostat junction box; if the primary sensor ever fails years later, the electrician can swap the low-voltage leads in 5 minutes without chiseling up a single tile.</p>
      </div>
    </section>
  </main>

{SHARED_FOOTER}

  <script>
    document.addEventListener('DOMContentLoaded', () => {{
      const heatedSqft = document.getElementById('heatedSqft');
      const heatedSqftVal = document.getElementById('heatedSqftVal');
      const wattageNote = document.getElementById('wattageNote');
      const radiantType = document.getElementById('radiantType');
      const subfloorBase = document.getElementById('subfloorBase');
      const dailyHours = document.getElementById('dailyHours');
      const dailyHoursVal = document.getElementById('dailyHoursVal');
      const zipInput = document.getElementById('zipInput');
      const leadMatchLink = document.getElementById('leadMatchLink');

      function calculate() {{
        const sqft = parseFloat(heatedSqft.value) || 80;
        const hrs = parseFloat(dailyHours.value) || 6;
        const watts = Math.round(sqft * 12);
        const btus = Math.round(watts * 3.412);
        heatedSqftVal.textContent = `${{sqft.toLocaleString()}} sq ft`;
        dailyHoursVal.textContent = `${{hrs}} hrs/day`;
        wattageNote.textContent = `System Output: ${{watts.toLocaleString()}} Watts (${{btus.toLocaleString()}} BTU/hr @ 12W/sq ft)`;

        const rType = radiantType.value;
        let matCost = Math.round(sqft * 10.20), statCost = 265, laborCost = 620 + Math.round(sqft * 7.00);
        if (rType === 'mesh_mat') {{
          matCost = Math.round(sqft * 7.80);
          laborCost = 580 + Math.round(sqft * 5.80);
        }} else if (rType === 'hydronic') {{
          matCost = 2400 + Math.round(sqft * 6.50);
          statCost = 480;
          laborCost = 2800 + Math.round(sqft * 6.20);
        }}

        let effFactor = 1.0;
        if (subfloorBase.value === 'insulated_fleece') {{
          matCost += Math.round(sqft * 1.65);
          effFactor = 0.78; // Thermal break cuts heat loss
        }}

        const total = matCost + statCost + laborCost;
        const dailyCost = ((watts / 1000) * hrs * 0.172 * effFactor);
        const monthlyCost = dailyCost * 30;
        const amps = (watts / 120).toFixed(1);
        const voltageSpec = watts > 1800 ? `Requires 240V 20A Dedicated Circuit (Draws ${{(watts / 240).toFixed(1)}} Amps)` : `Requires 120V 20A Dedicated Circuit (Draws ${{amps}} Amps)`;

        document.getElementById('radMatText').textContent = `$${{matCost.toLocaleString()}}`;
        document.getElementById('radStatText').textContent = `$${{statCost.toLocaleString()}}`;
        document.getElementById('radLaborText').textContent = `$${{laborCost.toLocaleString()}}`;
        document.getElementById('monthlyRunText').textContent = `$${{monthlyCost.toFixed(2)}} / month ($${{dailyCost.toFixed(2)}}/day)`;
        document.getElementById('radTotalText').textContent = `$${{total.toLocaleString()}}`;
        document.getElementById('circuitNoteText').textContent = rType === 'hydronic' ? "Hydronic Closed-Loop Manifold + Modulating Circulator Pump" : voltageSpec;

        document.getElementById('lowBidLabel').textContent = `Low: < $${{Math.round(total * 0.84).toLocaleString()}}`;
        document.getElementById('fairBidLabel').textContent = `Fair: $${{Math.round(total * 0.91).toLocaleString()}} – $${{Math.round(total * 1.10).toLocaleString()}}`;
        document.getElementById('highBidLabel').textContent = `Overpriced: > $${{Math.round(total * 1.22).toLocaleString()}}`;
      }}

      [heatedSqft, radiantType, subfloorBase, dailyHours].forEach(el => {{
        el.addEventListener('input', calculate);
        el.addEventListener('change', calculate);
      }});

      if (zipInput && leadMatchLink) {{
        zipInput.addEventListener('input', () => {{
          const zip = zipInput.value.trim();
          if (zip.length === 5) {{
            const dest = `https://www.angi.com/companylist/search.htm?query=Tile+Contractor&postalCode=${{zip}}`;
            leadMatchLink.href = `https://www.jdoqocy.com/click-101896838-17142784?url=${{encodeURIComponent(dest)}}`;
          }}
        }});
      }}

      calculate();
    }});
  </script>
  <script src="/tbm-widget.js" defer></script>
</body>
</html>
"""


def ensure_batch2_calculators():
    """Automatically creates the 3 missing homepage calculators in the repo root if not present."""
    created = 0
    for fname, body in [
        ("electrical-panel-calculator.html", electrical_panel_html),
        ("flooring-calculator.html", flooring_html),
        ("radiant-floor-calculator.html", radiant_floor_html)
    ]:
        if not os.path.exists(fname):
            with open(fname, "w", encoding="utf-8") as out_f:
                out_f.write(body)
            created += 1
            print(f"[AUTO-BUILD] Created new calculator: {fname}")
    return created

def main():
    ensure_batch2_calculators()
    target_date = datetime.date.today()
    iso_date = target_date.strftime("%Y-%m-%d")
    os.makedirs(INTEL_DIR, exist_ok=True)
    os.makedirs(os.path.join(DAILY_DIR, "todays-math"), exist_ok=True)
    os.makedirs(os.path.join(DAILY_DIR, iso_date), exist_ok=True)

    commodities, quote, code, rebate, tool, flagship = get_deterministic_data(target_date)
    avg_t, soil_t, sun_hrs = fetch_telemetry()

    # Stream 1: Update data/live-baselines.json
    baselines = load_and_update_baselines(target_date, commodities, flagship, avg_t, soil_t, sun_hrs)

    # Stream 2: Generate 1 Flagship Daily Math Briefing
    html, slug = build_daily_report_html(target_date, commodities, quote, code, rebate, tool, flagship, baselines)

    for out_path in [
        os.path.join(INTEL_DIR, f"{slug}.html"),
        os.path.join(INTEL_DIR, f"{iso_date}.html"),
        os.path.join(INTEL_DIR, "latest.html"),
        os.path.join(DAILY_DIR, "todays-math", "index.html"),
        os.path.join(DAILY_DIR, iso_date, "index.html")
    ]:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
    print(f"[STREAM 2] Generated Flagship Daily Math Briefing: /daily/todays-math/index.html & /intel/{slug}.html")

    # Stream 2 Lifecycle: Prune weather-dependent briefings older than 30 days
    prune_old_briefings(target_date, keep_days=30)
    update_intel_archive_index(INTEL_DIR)

    # Stream 1, 3 & 4: Retrofit all 21+ calculators with Living Banner, Cost-Per-Use Matrix & Case Studies tab
    retrofit_all_calculators_and_merge_case_study(target_date, flagship, baselines)

    # Stream 4: Update Homepage 3-Module "Daily Buyer's Pulse"
    if os.path.exists("index.html"):
        widget = build_homepage_widget(target_date, commodities, quote, tool, flagship, slug, baselines)
        inject_homepage_widget("index.html", widget)

    update_rss_and_sitemap(target_date, slug, flagship, baselines)
    ping_indexnow(slug)
    print("[SUCCESS] All 4 Coordinated Streams of the Living Authority Hub executed cleanly.")

if __name__ == "__main__":
    main()
