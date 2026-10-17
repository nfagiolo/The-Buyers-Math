#!/usr/bin/env python3
"""
apply_calculator_updates.py - Full Monetization, Regional Multiplier & Live Commodity Updater
1. Enforces official CJ Angi affiliate tracking (PID 101896838 / Link 17142784) across all 21 calculators.
2. Injects a live Material Spot-Price & 30-Day Trend Badge (from data/commodity_history.json) into each calculator.
3. Injects an interactive 50-State Labor & Local Rebate Selector (from data/regional_multipliers.json) that dynamically scales the calculator's #totalCost, #stickyTotal, and 3-tier bid meter (#lowBidLabel, #fairBidLabel, #highBidLabel).
"""

import os
import re
import json
import urllib.parse

CJ_TRACKING_BASE = "https://www.jdoqocy.com/click-101896838-17142784"
AMAZON_TAG = "nfagiolo-20"

TRADE_QUERIES = {
    "roofing-cost-calculator.html": ("Roofing", "asphalt_shingles"),
    "attic-insulation-calculator.html": ("Insulation", "fiberglass_batt"),
    "window-replacement-estimator.html": ("Window Replacement", "fiberglass_batt"),
    "siding-cost-calculator.html": ("Siding", "asphalt_shingles"),
    "driveway-paving-calculator.html": ("Asphalt Paving", "concrete_bag"),
    "fence-cost-calculator.html": ("Fence", "spf_lumber"),
    "hvac-roi-calculator.html": ("HVAC", "fiberglass_batt"),
    "mini-split-calculator.html": ("Heat Pumps", "romex_wire"),
    "water-heater-calculator.html": ("Water Heater Installation", "fiberglass_batt"),
    "solar-payback-calculator.html": ("Solar Panel Installation", "romex_wire"),
    "pool.html": ("Swimming Pool Maintenance", "romex_wire"),
    "bathroom-remodel-calculator.html": ("Bathroom Remodeling", "drywall_sheet"),
    "kitchen-remodel-calculator.html": ("Kitchen Remodeling", "spf_lumber"),
    "basement-cost-calculator.html": ("Basement Remodeling", "spf_lumber"),
    "ev-charger-calculator.html": ("Electrician", "romex_wire"),
    "generator-calculator.html": ("Generators", "romex_wire"),
    "deck-cost-calculator.html": ("Deck Building and Repair", "spf_lumber"),
    "gutter-cost-calculator.html": ("Gutter Installation", "asphalt_shingles"),
    "garage-door-calculator.html": ("Garage Door Installation", "asphalt_shingles"),
    "patio-cost-calculator.html": ("Paver and Patio Installation", "concrete_bag"),
    "exterior-painting-calculator.html": ("Exterior Painting", "asphalt_shingles")
}


def render_svg_sparkline(values, color="#2563eb"):
    if not values or len(values) < 2:
        return ""
    mn, mx = min(values), max(values)
    rng = (mx - mn) if mx != mn else 1.0
    w, h = 90, 24
    pts = []
    for i, v in enumerate(values):
        x = round((i / (len(values) - 1)) * (w - 4) + 2, 1)
        y = round(h - 3 - ((v - mn) / rng) * (h - 6), 1)
        pts.append(f"{x},{y}")
    poly = " ".join(pts)
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="vertical-align: middle; overflow: visible;" aria-hidden="true">'
        f'<polyline fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{poly}" />'
        f'</svg>'
    )


DEFAULT_REGIONS = {
    "US": {
        "name": "National Average (Baseline)",
        "labor_mult": 1.0,
        "material_mult": 1.0,
        "climate": "Mixed",
        "frost_in": 36,
        "rebate_note": "Federal IRA Section 25C (up to $3,200/yr) & Section 30C (up to $1,000) active nationwide."
    },
    "AL": {
        "name": "Alabama",
        "labor_mult": 0.84,
        "material_mult": 0.95,
        "climate": "Hot-Humid",
        "frost_in": 12,
        "rebate_note": "Alabama Power heat pump & water heater instant distributor rebates available."
    },
    "AK": {
        "name": "Alaska",
        "labor_mult": 1.38,
        "material_mult": 1.28,
        "climate": "Subarctic",
        "frost_in": 72,
        "rebate_note": "Cold-climate CEE Tier 2 heat pump and R-60 attic insulation incentives apply."
    },
    "AZ": {
        "name": "Arizona",
        "labor_mult": 0.96,
        "material_mult": 0.99,
        "climate": "Hot-Dry",
        "frost_in": 12,
        "rebate_note": "APS & SRP cool-roof, variable-speed pool pump, and high-SEER2 AC rebates active."
    },
    "AR": {
        "name": "Arkansas",
        "labor_mult": 0.82,
        "material_mult": 0.94,
        "climate": "Mixed-Humid",
        "frost_in": 18,
        "rebate_note": "Entergy & SWEPCO home weatherization and duct sealing rebates available."
    },
    "CA": {
        "name": "California",
        "labor_mult": 1.34,
        "material_mult": 1.15,
        "climate": "Mediterranean / Mixed",
        "frost_in": 12,
        "rebate_note": "TECH Clean California heat pump incentives + Title 24 cool-roof & solar storage mandates."
    },
    "CO": {
        "name": "Colorado",
        "labor_mult": 1.06,
        "material_mult": 1.03,
        "climate": "Cold / Semi-Arid",
        "frost_in": 42,
        "rebate_note": "Xcel Energy heat pump, 200A panel upgrade, and state heat pump tax credits stackable with 25C."
    },
    "CT": {
        "name": "Connecticut",
        "labor_mult": 1.24,
        "material_mult": 1.08,
        "climate": "Cold-Humid",
        "frost_in": 42,
        "rebate_note": "Energize CT instant rebates on air-source heat pumps, insulation, and hybrid water heaters."
    },
    "DE": {
        "name": "Delaware",
        "labor_mult": 1.08,
        "material_mult": 1.02,
        "climate": "Mixed-Humid",
        "frost_in": 32,
        "rebate_note": "Energize Delaware home performance rebates and Delmarva Power appliance credits."
    },
    "DC": {
        "name": "District of Columbia",
        "labor_mult": 1.22,
        "material_mult": 1.07,
        "climate": "Mixed-Humid",
        "frost_in": 30,
        "rebate_note": "DCSEU electrification, solar, and high-efficiency heat pump rebates available."
    },
    "FL": {
        "name": "Florida",
        "labor_mult": 0.94,
        "material_mult": 1.01,
        "climate": "Hot-Humid / Hurricane",
        "frost_in": 6,
        "rebate_note": "My Safe Florida Home wind-mitigation grants (roofing/impact windows) + FPL HVAC rebates."
    },
    "GA": {
        "name": "Georgia",
        "labor_mult": 0.91,
        "material_mult": 0.97,
        "climate": "Mixed-Humid",
        "frost_in": 18,
        "rebate_note": "Georgia Power EV charger, heat pump water heater, and smart thermostat rebates active."
    },
    "HI": {
        "name": "Hawaii",
        "labor_mult": 1.36,
        "material_mult": 1.3,
        "climate": "Tropical",
        "frost_in": 0,
        "rebate_note": "Hawaii Energy solar water heating, mini-split, and variable-speed pool pump rebates."
    },
    "ID": {
        "name": "Idaho",
        "labor_mult": 0.93,
        "material_mult": 0.99,
        "climate": "Cold",
        "frost_in": 42,
        "rebate_note": "Idaho Power ducted/ductless heat pump and attic weatherization incentives."
    },
    "IL": {
        "name": "Illinois",
        "labor_mult": 1.19,
        "material_mult": 1.04,
        "climate": "Cold-Humid",
        "frost_in": 42,
        "rebate_note": "ComEd & Ameren Illinois heat pump, air sealing, and smart panel rebates active."
    },
    "IN": {
        "name": "Indiana",
        "labor_mult": 0.95,
        "material_mult": 0.98,
        "climate": "Cold-Humid",
        "frost_in": 36,
        "rebate_note": "AES Indiana & Duke Energy HVAC, insulation, and hybrid water heater rebates."
    },
    "IA": {
        "name": "Iowa",
        "labor_mult": 0.92,
        "material_mult": 0.97,
        "climate": "Cold",
        "frost_in": 48,
        "rebate_note": "MidAmerican Energy & Alliant Energy cold-climate heat pump and insulation rebates."
    },
    "KS": {
        "name": "Kansas",
        "labor_mult": 0.9,
        "material_mult": 0.97,
        "climate": "Mixed-Dry / Cold",
        "frost_in": 36,
        "rebate_note": "Evergy high-efficiency HVAC and thermostat demand-response incentives."
    },
    "KY": {
        "name": "Kentucky",
        "labor_mult": 0.89,
        "material_mult": 0.96,
        "climate": "Mixed-Humid",
        "frost_in": 30,
        "rebate_note": "LG&E/KU and Duke Energy Kentucky weatherization and heat pump rebates."
    },
    "LA": {
        "name": "Louisiana",
        "labor_mult": 0.87,
        "material_mult": 0.97,
        "climate": "Hot-Humid",
        "frost_in": 12,
        "rebate_note": "Louisiana Fortified Roof grants + Entergy New Orleans energy efficiency rebates."
    },
    "ME": {
        "name": "Maine",
        "labor_mult": 1.05,
        "material_mult": 1.04,
        "climate": "Very Cold",
        "frost_in": 60,
        "rebate_note": "Efficiency Maine whole-home heat pump rebates ($4,000\u2013$8,000) stackable with 25C."
    },
    "MD": {
        "name": "Maryland",
        "labor_mult": 1.12,
        "material_mult": 1.03,
        "climate": "Mixed-Humid",
        "frost_in": 32,
        "rebate_note": "BGE, Pepco & SMECO EmPOWER Maryland rebates for heat pumps, insulation, and EV chargers."
    },
    "MA": {
        "name": "Massachusetts",
        "labor_mult": 1.29,
        "material_mult": 1.1,
        "climate": "Cold-Humid",
        "frost_in": 48,
        "rebate_note": "Mass Save whole-home heat pump rebates (up to $10,000) and 75% insulation incentives."
    },
    "MI": {
        "name": "Michigan",
        "labor_mult": 1.06,
        "material_mult": 1.01,
        "climate": "Cold",
        "frost_in": 42,
        "rebate_note": "DTE & Consumers Energy cold-climate HVAC, egress window, and insulation rebates."
    },
    "MN": {
        "name": "Minnesota",
        "labor_mult": 1.14,
        "material_mult": 1.03,
        "climate": "Very Cold",
        "frost_in": 60,
        "rebate_note": "Xcel Energy & CenterPoint air-sealing, R-60 attic insulation, and dual-fuel heat pump rebates."
    },
    "MS": {
        "name": "Mississippi",
        "labor_mult": 0.81,
        "material_mult": 0.94,
        "climate": "Hot-Humid",
        "frost_in": 12,
        "rebate_note": "Mississippi Power & Entergy heat pump water heater and attic insulation rebates."
    },
    "MO": {
        "name": "Missouri",
        "labor_mult": 0.98,
        "material_mult": 0.98,
        "climate": "Mixed-Humid",
        "frost_in": 36,
        "rebate_note": "Ameren Missouri & Evergy Pay-As-You-Save HVAC and electrical panel upgrade rebates."
    },
    "MT": {
        "name": "Montana",
        "labor_mult": 0.96,
        "material_mult": 1.02,
        "climate": "Very Cold",
        "frost_in": 54,
        "rebate_note": "NorthWestern Energy weatherization, window replacement, and cold-climate heat pump rebates."
    },
    "NE": {
        "name": "Nebraska",
        "labor_mult": 0.91,
        "material_mult": 0.97,
        "climate": "Cold",
        "frost_in": 42,
        "rebate_note": "OPPD & LES high-efficiency heat pump and smart load-management rebates."
    },
    "NV": {
        "name": "Nevada",
        "labor_mult": 1.05,
        "material_mult": 1.02,
        "climate": "Hot-Dry",
        "frost_in": 18,
        "rebate_note": "NV Energy PowerShift variable-speed pool pump, solar storage, and AC rebates."
    },
    "NH": {
        "name": "New Hampshire",
        "labor_mult": 1.09,
        "material_mult": 1.04,
        "climate": "Cold",
        "frost_in": 54,
        "rebate_note": "NHSaves weatherization, air sealing, and cold-climate mini-split rebates."
    },
    "NJ": {
        "name": "New Jersey",
        "labor_mult": 1.25,
        "material_mult": 1.08,
        "climate": "Mixed-Humid",
        "frost_in": 36,
        "rebate_note": "PSE&G, JCP&L & NJ Clean Energy whole-house comfort and EV charger installation rebates."
    },
    "NM": {
        "name": "New Mexico",
        "labor_mult": 0.91,
        "material_mult": 0.98,
        "climate": "Mixed-Dry",
        "frost_in": 24,
        "rebate_note": "PNM heat pump, evaporative cooling, and state solar market development tax credits."
    },
    "NY": {
        "name": "New York",
        "labor_mult": 1.33,
        "material_mult": 1.11,
        "climate": "Cold-Humid",
        "frost_in": 48,
        "rebate_note": "NYSERDA Clean Heat, EmPower+ insulation, and NY-Sun solar incentives stack with 25C/25D."
    },
    "NC": {
        "name": "North Carolina",
        "labor_mult": 0.9,
        "material_mult": 0.97,
        "climate": "Mixed-Humid",
        "frost_in": 20,
        "rebate_note": "Duke Energy Home Energy Improvement rebates for HVAC, attic insulation, and duct sealing."
    },
    "ND": {
        "name": "North Dakota",
        "labor_mult": 0.95,
        "material_mult": 1.01,
        "climate": "Very Cold",
        "frost_in": 66,
        "rebate_note": "Dual-fuel cold-climate heat pump and deep-frost foundation insulation incentives."
    },
    "OH": {
        "name": "Ohio",
        "labor_mult": 0.99,
        "material_mult": 0.99,
        "climate": "Cold-Humid",
        "frost_in": 38,
        "rebate_note": "AEP Ohio, Duke Energy & FirstEnergy rebates alongside IRA 25C federal tax credits."
    },
    "OK": {
        "name": "Oklahoma",
        "labor_mult": 0.86,
        "material_mult": 0.95,
        "climate": "Mixed-Humid",
        "frost_in": 22,
        "rebate_note": "OG&E & PSO weatherization, storm-resistant Class 4 shingle insurance discounts, and HVAC rebates."
    },
    "OR": {
        "name": "Oregon",
        "labor_mult": 1.15,
        "material_mult": 1.06,
        "climate": "Marine",
        "frost_in": 24,
        "rebate_note": "Energy Trust of Oregon cash incentives for heat pumps, windows, insulation, and solar."
    },
    "PA": {
        "name": "Pennsylvania",
        "labor_mult": 1.1,
        "material_mult": 1.02,
        "climate": "Cold-Humid",
        "frost_in": 40,
        "rebate_note": "PECO, PPL & Duquesne Light Act 129 rebates for heat pumps, water heaters, and pool pumps."
    },
    "RI": {
        "name": "Rhode Island",
        "labor_mult": 1.21,
        "material_mult": 1.07,
        "climate": "Cold-Humid",
        "frost_in": 42,
        "rebate_note": "Clean Heat RI & Rhode Island Energy 75%+ weatherization and heat pump incentives."
    },
    "SC": {
        "name": "South Carolina",
        "labor_mult": 0.88,
        "material_mult": 0.96,
        "climate": "Hot-Humid",
        "frost_in": 14,
        "rebate_note": "Dominion Energy SC & Duke Energy HVAC, ductwork, and 25% state solar tax credit."
    },
    "SD": {
        "name": "South Dakota",
        "labor_mult": 0.89,
        "material_mult": 0.98,
        "climate": "Cold",
        "frost_in": 54,
        "rebate_note": "Black Hills Energy & Xcel high-efficiency heating and water heater rebates."
    },
    "TN": {
        "name": "Tennessee",
        "labor_mult": 0.89,
        "material_mult": 0.96,
        "climate": "Mixed-Humid",
        "frost_in": 20,
        "rebate_note": "TVA EnergyRight rebates for heat pumps, attic insulation ($500+), and duct sealing."
    },
    "TX": {
        "name": "Texas",
        "labor_mult": 0.91,
        "material_mult": 0.97,
        "climate": "Hot-Humid / Hot-Dry",
        "frost_in": 12,
        "rebate_note": "Oncor, CenterPoint & Austin Energy rebates for SEER2 HVAC, solar, and standby generators."
    },
    "UT": {
        "name": "Utah",
        "labor_mult": 0.95,
        "material_mult": 0.99,
        "climate": "Cold / Dry",
        "frost_in": 36,
        "rebate_note": "Rocky Mountain Power Wattsmart & Enbridge Gas dual-fuel heat pump and insulation rebates."
    },
    "VT": {
        "name": "Vermont",
        "labor_mult": 1.07,
        "material_mult": 1.05,
        "climate": "Very Cold",
        "frost_in": 60,
        "rebate_note": "Efficiency Vermont point-of-sale rebates on cold-climate heat pumps and weatherization."
    },
    "VA": {
        "name": "Virginia",
        "labor_mult": 1.04,
        "material_mult": 1.01,
        "climate": "Mixed-Humid",
        "frost_in": 28,
        "rebate_note": "Dominion Energy Virginia & NOVEC rebates for heat pumps, tune-ups, and EV chargers."
    },
    "WA": {
        "name": "Washington",
        "labor_mult": 1.2,
        "material_mult": 1.08,
        "climate": "Marine / Cold",
        "frost_in": 24,
        "rebate_note": "PSE, Seattle City Light & WA Clean Buildings heat pump conversion and panel upgrade rebates."
    },
    "WV": {
        "name": "West Virginia",
        "labor_mult": 0.92,
        "material_mult": 0.97,
        "climate": "Mixed-Humid / Cold",
        "frost_in": 36,
        "rebate_note": "Appalachian Power & Mon Power home performance and heat pump water heater rebates."
    },
    "WI": {
        "name": "Wisconsin",
        "labor_mult": 1.05,
        "material_mult": 1.01,
        "climate": "Cold",
        "frost_in": 54,
        "rebate_note": "Focus on Energy Wisconsin cash-back rebates on furnaces, heat pumps, and air sealing."
    },
    "WY": {
        "name": "Wyoming",
        "labor_mult": 0.94,
        "material_mult": 1.01,
        "climate": "Cold / Dry",
        "frost_in": 48,
        "rebate_note": "Rocky Mountain Power & Black Hills Energy high-efficiency heating and insulation incentives."
    }
}

DEFAULT_COMMODITIES = {
    "last_updated": "2026-10-17",
    "commodities": {
        "spf_lumber": {
            "name": "2x4x8 SPF Framing Stud",
            "unit": "per piece",
            "current_price": 3.93,
            "change_30d_pct": 1.2,
            "note": "Mill production steady; freight diesel stabilizing inland rail tariffs.",
            "calc_url": "/deck-cost-calculator.html",
            "trades": [
                "deck-cost-calculator.html",
                "basement-cost-calculator.html",
                "fence-cost-calculator.html",
                "kitchen-remodel-calculator.html"
            ],
            "history": [
                3.88,
                3.89,
                3.87,
                3.9,
                3.91,
                3.94,
                3.96,
                3.95,
                3.98,
                4.0,
                3.97,
                3.94,
                3.92,
                3.9,
                3.88,
                3.89,
                3.91,
                3.92,
                3.94,
                3.95,
                3.93,
                3.91,
                3.9,
                3.88,
                3.89,
                3.91,
                3.92,
                3.94,
                3.92,
                3.93
            ]
        },
        "romex_wire": {
            "name": "12/2 NM-B Romex (250ft)",
            "unit": "250ft roll",
            "current_price": 138.65,
            "change_30d_pct": -2.7,
            "note": "COMEX copper spot futures moderating; electrical distributors well stocked.",
            "calc_url": "/ev-charger-calculator.html",
            "trades": [
                "ev-charger-calculator.html",
                "generator-calculator.html",
                "solar-payback-calculator.html",
                "mini-split-calculator.html",
                "pool.html"
            ],
            "history": [
                142.5,
                143.1,
                144.0,
                145.2,
                146.49,
                145.8,
                144.9,
                143.5,
                142.8,
                141.9,
                141.2,
                140.8,
                140.22,
                140.5,
                141.0,
                140.4,
                139.9,
                139.6,
                139.2,
                139.0,
                138.9,
                139.1,
                139.4,
                139.15,
                138.95,
                138.8,
                138.75,
                138.7,
                138.68,
                138.65
            ]
        },
        "asphalt_shingles": {
            "name": "Architectural Asphalt Shingles",
            "unit": "per square (100 sq ft)",
            "current_price": 117.65,
            "change_30d_pct": -0.3,
            "note": "Petroleum asphalt flux index flat; late-fall re-roofing demand normalizing.",
            "calc_url": "/roofing-cost-calculator.html",
            "trades": [
                "roofing-cost-calculator.html",
                "siding-cost-calculator.html",
                "gutter-cost-calculator.html",
                "exterior-painting-calculator.html",
                "garage-door-calculator.html"
            ],
            "history": [
                118.0,
                118.2,
                118.5,
                118.71,
                119.1,
                119.6,
                120.1,
                120.71,
                120.4,
                120.0,
                119.7,
                119.3,
                119.0,
                118.8,
                118.6,
                118.4,
                118.2,
                118.1,
                118.0,
                117.9,
                117.85,
                117.8,
                117.75,
                117.7,
                117.72,
                117.68,
                117.66,
                117.64,
                117.65,
                117.65
            ]
        },
        "concrete_bag": {
            "name": "Sakrete / Quikrete 5000 (80lb)",
            "unit": "80 lb bag",
            "current_price": 6.56,
            "change_30d_pct": 1.7,
            "note": "Portland cement kiln energy inputs firm; pre-freeze flatwork orders active.",
            "calc_url": "/driveway-paving-calculator.html",
            "trades": [
                "driveway-paving-calculator.html",
                "patio-cost-calculator.html"
            ],
            "history": [
                6.45,
                6.46,
                6.48,
                6.5,
                6.55,
                6.6,
                6.65,
                6.62,
                6.58,
                6.52,
                6.45,
                6.4,
                6.38,
                6.4,
                6.42,
                6.44,
                6.46,
                6.48,
                6.49,
                6.5,
                6.51,
                6.52,
                6.53,
                6.54,
                6.54,
                6.55,
                6.55,
                6.56,
                6.56,
                6.56
            ]
        },
        "drywall_sheet": {
            "name": "1/2-in x 4x8 Sheetrock Drywall",
            "unit": "per panel",
            "current_price": 14.75,
            "change_30d_pct": -1.9,
            "note": "Synthetic gypsum calcining plants at 89% capacity; interior remodel stock high.",
            "calc_url": "/bathroom-remodel-calculator.html",
            "trades": [
                "bathroom-remodel-calculator.html"
            ],
            "history": [
                15.04,
                15.02,
                15.0,
                14.98,
                14.95,
                14.92,
                14.9,
                14.88,
                14.85,
                14.82,
                14.8,
                14.8,
                14.79,
                14.79,
                14.78,
                14.78,
                14.77,
                14.77,
                14.76,
                14.76,
                14.76,
                14.75,
                14.75,
                14.75,
                14.75,
                14.75,
                14.75,
                14.75,
                14.75,
                14.75
            ]
        },
        "fiberglass_batt": {
            "name": "R-38 Kraft Fiberglass Batt",
            "unit": "roll (64 sq ft)",
            "current_price": 81.4,
            "change_30d_pct": 3.4,
            "note": "Pre-winter weatherization surge; IRA Section 25C $1,200 cap driving attic retrofits.",
            "calc_url": "/attic-insulation-calculator.html",
            "trades": [
                "attic-insulation-calculator.html",
                "hvac-roi-calculator.html",
                "window-replacement-estimator.html",
                "water-heater-calculator.html"
            ],
            "history": [
                78.7,
                78.9,
                79.1,
                79.3,
                79.5,
                79.8,
                80.1,
                80.4,
                80.6,
                80.86,
                80.9,
                80.95,
                81.0,
                81.05,
                81.1,
                81.12,
                81.15,
                81.18,
                81.2,
                81.22,
                81.25,
                81.28,
                81.3,
                81.32,
                81.34,
                81.35,
                81.37,
                81.38,
                81.39,
                81.4
            ]
        }
    }
}

ADSENSE_META_TAG = '<meta name="google-adsense-account" content="ca-pub-1199906473460957">'
ADSENSE_SCRIPT_TAG = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>'
ADS_TXT_LINE = "google.com, pub-1199906473460957, DIRECT, f08c47fec0942fa0\n"

def ensure_adsense_and_ads_txt():
    with open("ads.txt", "w", encoding="utf-8") as f:
        f.write(ADS_TXT_LINE)
    for rp in ["index.html", "guides.html", "about.html", "privacy-policy.html", "terms.html", "contact.html", "intel/index.html"]:
        if os.path.exists(rp):
            with open(rp, "r", encoding="utf-8") as f:
                h = f.read()
            orig_h = h
            if 'name="google-adsense-account"' not in h and "</head>" in h:
                h = h.replace("</head>", "  " + ADSENSE_META_TAG + "\n</head>", 1)
            if "ca-pub-1199906473460957" not in h and "</head>" in h:
                h = h.replace("</head>", "  " + ADSENSE_SCRIPT_TAG + "\n</head>", 1)
            if h != orig_h:
                with open(rp, "w", encoding="utf-8") as f:
                    f.write(h)

def load_json_multi(paths, default):
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    if d:
                        return d
            except Exception:
                pass
    return default

def load_json_safe(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def build_regional_and_commodity_widget(trade_name, comm_data, regions_data, last_updated):
    c_name = comm_data.get("name", "Construction Material Index")
    c_unit = comm_data.get("unit", "per unit")
    c_price = comm_data.get("current_price", 0.0)
    c_chg = comm_data.get("change_30d_pct", 0.0)
    c_hist = comm_data.get("history", [])
    arrow = "▲" if c_chg >= 0 else "▼"
    chg_color = "#dc2626" if c_chg > 0 else "#059669"
    spark_svg = render_svg_sparkline(c_hist, chg_color)

    options_html = []
    for code, info in regions_data.items():
        sel = ' selected' if code == "US" else ''
        mult_pct = int(round((info["labor_mult"] - 1.0) * 100))
        sign = f"+{mult_pct}%" if mult_pct > 0 else (f"{mult_pct}%" if mult_pct < 0 else "Baseline")
        options_html.append(
            f'<option value="{code}" data-labor="{info["labor_mult"]}" data-mat="{info["material_mult"]}" '
            f'data-climate="{info["climate"]}" data-frost="{info["frost_in"]}" '
            f'data-rebate="{info["rebate_note"]}"{sel}>{info["name"]} (Labor: {sign})</option>'
        )

    return f"""<!-- TBM REGIONAL & COMMODITY WIDGET START -->
    <div id="tbmRegionalCommodityBar" style="background: #ffffff; border: 1px solid #cbd5e1; border-left: 5px solid #2563eb; border-radius: 12px; padding: 1.15rem 1.35rem; margin: 0 0 1.75rem 0; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div style="flex: 1; min-width: 260px;">
          <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb; margin-bottom: 0.25rem;">
            Live Material Benchmark &bull; Updated {last_updated}
          </div>
          <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
            <strong style="font-size: 0.98rem; color: #0f172a;">{c_name}:</strong>
            <span style="font-size: 1.05rem; font-weight: 800; color: #0f172a;">${c_price:.2f}</span>
            <span style="font-size: 0.78rem; font-weight: 700; color: {chg_color}; background: #f8fafc; padding: 0.15rem 0.45rem; border-radius: 4px; border: 1px solid #e2e8f0;">
              {arrow} {c_chg:+.1f}% (30d)
            </span>
            {spark_svg}
            <span style="font-size: 0.75rem; color: #64748b;">({c_unit})</span>
          </div>
        </div>

        <div style="flex: 1; min-width: 260px;">
          <label for="tbmStateSelector" style="display: block; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #334155; margin-bottom: 0.3rem;">
            Localize Labor Rates &amp; Utility Rebates by State:
          </label>
          <select id="tbmStateSelector" style="width: 100%; padding: 0.55rem 0.75rem; border: 1px solid #93c5fd; border-radius: 8px; font-size: 0.9rem; font-weight: 600; color: #0f172a; background: #eff6ff; cursor: pointer;">
            {"".join(options_html)}
          </select>
        </div>
      </div>
      <div id="tbmStateRebateBanner" style="margin-top: 0.75rem; padding-top: 0.65rem; border-top: 1px solid #f1f5f9; font-size: 0.82rem; color: #475569; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
        <span id="tbmStateRebateText"><strong> Incentive &amp; Code Note:</strong> Federal IRA Section 25C (up to $3,200/yr) &amp; Section 30C (up to $1,000) active nationwide.</span>
        <a href="/intel/" style="color: #2563eb; font-weight: 700; text-decoration: none; white-space: nowrap;">View Daily Market Brief &rarr;</a>
      </div>
    </div>
    <script>
      document.addEventListener('DOMContentLoaded', () => {{
        const stateSel = document.getElementById('tbmStateSelector');
        const rebateText = document.getElementById('tbmStateRebateText');
        const totalEl = document.getElementById('totalCost');
        const stickyEl = document.getElementById('stickyTotal');
        const lowEl = document.getElementById('lowBidLabel');
        const fairEl = document.getElementById('fairBidLabel');
        const highEl = document.getElementById('highBidLabel');
        const leadLink = document.getElementById('leadMatchLink');
        if (!stateSel || !totalEl) return;

        let currentMultiplier = 1.0;
        let applyingRegional = false;

        function parseCurrency(str) {{
          const m = (str || '').replace(/,/g, '').match(/\\$(\\d+)/);
          return m ? parseInt(m[1], 10) : null;
        }}

        function applyRegionalScaling() {{
          if (applyingRegional) return;
          const opt = stateSel.options[stateSel.selectedIndex];
          if (!opt) return;
          const laborMult = parseFloat(opt.getAttribute('data-labor') || '1.0');
          const matMult = parseFloat(opt.getAttribute('data-mat') || '1.0');
          const blended = (laborMult * 0.55) + (matMult * 0.45);
          const rebate = opt.getAttribute('data-rebate') || '';
          const climate = opt.getAttribute('data-climate') || '';
          const frost = opt.getAttribute('data-frost') || '36';
          const stateCode = stateSel.value;

          if (rebateText) {{
            rebateText.innerHTML = '<strong>' + opt.text.split(' (')[0] + ' (' + climate + ' &bull; ' + frost + '&quot; Frost Line):</strong> ' + rebate;
          }}

          const currentVal = parseCurrency(totalEl.textContent);
          if (currentVal) {{
            applyingRegional = true;
            const unscaledBase = Math.round(currentVal / currentMultiplier);
            currentMultiplier = blended;
            const scaledTotal = Math.round(unscaledBase * currentMultiplier);
            totalEl.textContent = '$' + scaledTotal.toLocaleString();
            if (stickyEl) stickyEl.textContent = '$' + scaledTotal.toLocaleString();

            const lowBid = Math.round(scaledTotal * 0.86);
            const fairMin = Math.round(scaledTotal * 0.92);
            const fairMax = Math.round(scaledTotal * 1.15);
            const highBid = Math.round(scaledTotal * 1.35);
            if (lowEl) lowEl.textContent = 'Budget: < $' + lowBid.toLocaleString();
            if (fairEl) fairEl.textContent = 'Fair: $' + fairMin.toLocaleString() + ' \u2013 $' + fairMax.toLocaleString();
            if (highEl) highEl.textContent = 'Red Flag: > $' + highBid.toLocaleString();
            setTimeout(() => {{ applyingRegional = false; }}, 50);
          }}

          if (leadLink && stateCode !== 'US') {{
            leadLink.textContent = 'Compare ' + stateCode + ' Contractor Bids \u2192';
          }}
        }}

        stateSel.addEventListener('change', applyRegionalScaling);

        // Re-apply state scaling whenever calculator inputs change
        document.querySelectorAll('select:not(#tbmStateSelector), input').forEach(inp => {{
          inp.addEventListener('change', () => {{
            currentMultiplier = 1.0;
            setTimeout(applyRegionalScaling, 20);
          }});
          inp.addEventListener('input', () => {{
            currentMultiplier = 1.0;
            setTimeout(applyRegionalScaling, 20);
          }});
        }});
      }});
    </script>
    <!-- TBM REGIONAL & COMMODITY WIDGET END -->"""


def main():
    ensure_adsense_and_ads_txt()
    regions = load_json_multi(["data/regional_multipliers.json", "regional_multipliers.json"], DEFAULT_REGIONS)
    comm_store = load_json_multi(["data/commodity_history.json", "commodity_history.json"], DEFAULT_COMMODITIES)
    commodities = comm_store.get("commodities", {})
    last_updated = comm_store.get("last_updated", "2026-10-17")

    updated_count = 0
    for filename, (trade, comm_key) in TRADE_QUERIES.items():
        if not os.path.exists(filename):
            continue
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        orig = content

        default_dest = f"https://www.angi.com/companylist/search.htm?query={urllib.parse.quote_plus(trade)}"
        default_cj_url = f"{CJ_TRACKING_BASE}?url={urllib.parse.quote(default_dest, safe='')}"

        # 1. Update HTML leadMatchLink href
        content = re.sub(
            r'(<a\s+id=["\']leadMatchLink["\']\s+href=["\'])[^"\']*(["\'])',
            lambda m: m.group(1) + default_cj_url + m.group(2),
            content
        )

        # 2. Update JS input listener for 5-digit ZIP codes
        js_old_pattern = r'leadMatchLink\.href\s*=\s*[`"\']https://www\.angi\.com/companylist/search\.htm\?query=[^`"\']*&amp;postalCode=\$\{zip\}[`"\'];'
        js_replacement = (
            f"const dest = `https://www.angi.com/companylist/search.htm?query={urllib.parse.quote_plus(trade)}&postalCode=${{zip}}`;\n"
            f"          leadMatchLink.href = `{CJ_TRACKING_BASE}?url=${{encodeURIComponent(dest)}}`;"
        )
        content = re.sub(js_old_pattern, lambda _: js_replacement, content)

        # 3. Inject or refresh Regional & Live Commodity Spot-Price Widget
        comm_info = commodities.get(comm_key, {})
        widget_html = build_regional_and_commodity_widget(trade, comm_info, regions, last_updated)

        if "<!-- TBM REGIONAL & COMMODITY WIDGET START -->" in content:
            content = re.sub(
                r"<!-- TBM REGIONAL & COMMODITY WIDGET START -->.*?<!-- TBM REGIONAL & COMMODITY WIDGET END -->",
                lambda _: widget_html,
                content,
                flags=re.DOTALL
            )
        elif "<!-- 2-Column Calculator Grid -->" in content:
            content = content.replace(
                "<!-- 2-Column Calculator Grid -->",
                widget_html + "\n\n    <!-- 2-Column Calculator Grid -->",
                1
            )
        elif "<h1" in content:
            h1_end = content.find("</h1>")
            if h1_end != -1:
                next_div = content.find("</div>", h1_end)
                if next_div != -1:
                    pos = next_div + len("</div>")
                    content = content[:pos] + "\n\n    " + widget_html + content[pos:]

        if 'name="google-adsense-account"' not in content and "</head>" in content:
            content = content.replace("</head>", "  " + ADSENSE_META_TAG + "\n</head>", 1)
        if content != orig:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            updated_count += 1
            print(f"Updated {filename} with 50-state multiplier, live commodity badge & CJ Angi tracking.")

    print(f"Batch completed: {updated_count} calculators updated.")


if __name__ == "__main__":
    main()
