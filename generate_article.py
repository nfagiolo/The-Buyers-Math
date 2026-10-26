#!/usr/bin/env python3
"""
generate_article.py - Automated Daily Brand/SKU Empirical Cost Guide Generator for The Buyer's Math
Includes:
1. Primary Tier 1 Gemini API (`gemini-4-argon` thinkingLevel="LOW", fallback `gemini-2.5-flash`) + Anthropic fallback.
2. Brand/Model SKU-specific topic selection modeled on top-performing Search Console pages (e.g., Schluter DITRA-HEAT).
3. Strict title sanitization (removes raw Markdown '# ' prefixes and quotes) and duplicate-slug skip guard.
4. Unique <meta name="description"> extraction from the opening paragraph.
5. Deterministic Inline SVG Cost-Tier & Payback Comparison Chart.
6. Shoppable 5-Item Amazon Associates (`tag=nfagiolo-20`) Bill-of-Materials (BOM) Table.
7. Interactive "Audit My Contractor Quote" Red-Flag Scorecard Widget with dynamic CJ Angi (`PID: 101896838`) conversion CTA.
"""

import os
import re
import json
import random
import datetime
import urllib.parse
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CJ_TRACKING_BASE = "https://www.jdoqocy.com/click-101896838-17142784"
AMAZON_TAG = "nfagiolo-20"
ADSENSE_CLIENT = "ca-pub-1199906473460957"

CALCULATORS = [
    {
        "id": "radiant",
        "name": "Radiant Floor Heating Cost Calculator",
        "url": "/radiant-floor-calculator.html",
        "category": "Interior & Power",
        "unit": "heated floor sq ft",
        "base_unit_cost": 18.0,
        "default_size": 100,
        "tier_labels": ["DIY Membrane + Cable Kit ($850)", "Turnkey Pro Tile + 20A Circuit ($1,800)", "Primary Bath 150 sq ft WiFi Kit ($2,650)"],
        "tier_vals": [850, 1800, 2650],
        "skus": [
            "Schluter DITRA-HEAT-DUO Thermal Break Membrane vs Standard DITRA-HEAT Installed Cost Guide",
            "WarmlyYours TempZone vs Schluter DITRA-HEAT Electric Floor Heating Cost Guide",
            "Nuheat Custom Mats vs Cable Membrane System Installed Cost Per Sq Ft",
        ],
        "bom": [
            ("Schluter DITRA-HEAT Complete Bathroom Kit (Membrane + Cable + WiFi)", "Schluter+DITRA-HEAT+Complete+Kit+WiFi", "$545 – $895"),
            ("Schluter DITRA-HEAT Uncoupling Membrane Roll (134.5 sq ft)", "Schluter+DITRA-HEAT+Membrane+Roll", "$315 – $349"),
            ("Schluter DITRA-HEAT-E-HK Electric Heating Cable (120V/240V)", "Schluter+DITRA-HEAT-E-HK+Heating+Cable", "$235 – $390"),
            ("Schluter DITRA-HEAT-E-WiFi Programmable Touchscreen Thermostat", "Schluter+DITRA-HEAT-E-WiFi+Thermostat", "$265 – $310"),
            ("Schluter ALL-SET Modified Thin-Set Mortar (50 lb Bag)", "Schluter+ALL-SET+Thin-Set+Mortar", "$38 – $49"),
        ],
    },
    {
        "id": "bathroom",
        "name": "Bathroom Remodel Cost Estimator",
        "url": "/bathroom-remodel-calculator.html",
        "category": "Interior & Power",
        "unit": "bathroom sq ft",
        "base_unit_cost": 265.0,
        "default_size": 65,
        "tier_labels": ["Powder Room Refresh ($7,200)", "5x8 Guest Bath Full Tile ($16,800)", "Primary Wet-Room Suite ($31,500)"],
        "tier_vals": [7200, 16800, 31500],
        "skus": [
            "Schluter KERDI-BOARD Waterproof Shower Kit (38x60 & 48x60) Installed Cost Guide",
            "Panasonic WhisperGreen Select vs Broan UltraGreen Bathroom Exhaust Fan Installed Cost Guide",
            "Kohler Anthem Digital Shower Valve vs Moen U by Moen Rough-In & Labor Cost Guide",
            " Wedi Fundo Primo vs Schluter KERDI-SHOWER-T Curbless Shower Pan Installed Cost Guide",
        ],
        "bom": [
            ("Schluter Kerdi-Board Waterproof Shower Kit (38x60)", "schluter+kerdi+shower+kit+38x60", "$480 – $620"),
            ("Panasonic WhisperCeiling DC 110 CFM Humidity Fan", "panasonic+whisperceiling+110+cfm", "$165 – $215"),
            ("Moen Posi-Temp / Thermostatic Brass Shower Rough-In Valve", "moen+rough+in+shower+valve+brass", "$140 – $195"),
            ("Schluter KERDI-DRAIN Stainless Grate Assembly", "schluter+kerdi+drain+stainless", "$115 – $165"),
            ("Pinless Digital Subfloor Moisture Meter", "pinless+moisture+meter+drywall+wood", "$45 – $69"),
        ],
    },
    {
        "id": "pool",
        "name": "Pool Pump Energy Calculator",
        "url": "/pool.html",
        "category": "Mechanical & Energy",
        "unit": "horsepower tier",
        "base_unit_cost": 1650.0,
        "default_size": 1
