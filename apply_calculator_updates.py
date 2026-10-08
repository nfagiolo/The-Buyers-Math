#!/usr/bin/env python3
"""
apply_calculator_updates.py
Batch updates all 21 core calculators with official CJ Angi affiliate tracking links.
Ensures every contractor bid match and ZIP code lookup tracks to Publisher ID 101896838 / Link ID 17142784.
"""

import os
import glob
import re
import urllib.parse

CJ_TRACKING_BASE = "https://www.jdoqocy.com/click-101896838-17142784"

TRADE_QUERIES = {
    "roofing-cost-calculator.html": "Roofing",
    "attic-insulation-calculator.html": "Insulation",
    "window-replacement-estimator.html": "Window Replacement",
    "siding-cost-calculator.html": "Siding",
    "driveway-paving-calculator.html": "Asphalt Paving",
    "fence-cost-calculator.html": "Fence",
    "hvac-roi-calculator.html": "HVAC",
    "mini-split-calculator.html": "Heat Pumps",
    "water-heater-calculator.html": "Water Heater Installation",
    "solar-payback-calculator.html": "Solar Panel Installation",
    "pool.html": "Swimming Pool Maintenance",
    "bathroom-remodel-calculator.html": "Bathroom Remodeling",
    "kitchen-remodel-calculator.html": "Kitchen Remodeling",
    "basement-cost-calculator.html": "Basement Remodeling",
    "ev-charger-calculator.html": "Electrician",
    "generator-calculator.html": "Generators",
    "deck-cost-calculator.html": "Deck Building and Repair",
    "gutter-cost-calculator.html": "Gutter Installation",
    "garage-door-calculator.html": "Garage Door Installation",
    "patio-cost-calculator.html": "Paver and Patio Installation",
    "exterior-painting-calculator.html": "Exterior Painting"
}

def main():
    updated_count = 0
    for filename, trade in TRADE_QUERIES.items():
        if not os.path.exists(filename):
            continue

        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        orig = content
        default_dest = f"https://www.angi.com/companylist/search.htm?query={urllib.parse.quote_plus(trade)}"
        default_cj_url = f"{CJ_TRACKING_BASE}?url={urllib.parse.quote(default_dest, safe='')}"

        # 1. Update HTML leadMatchLink href
        content = re.sub(
            r'(<a\s+id=[\'"]leadMatchLink[\'"]\s+href=[\'"])[^\'"]*([\'"])',
            r'\g<1>' + default_cj_url + r'\g<2>',
            content
        )

        # 2. Update JS input listener for 5-digit ZIP codes
        js_old_pattern = r'leadMatchLink\.href\s*=\s*[`\'"]https://www\.angi\.com/companylist/search\.htm\?query=[^`\'"]*&postalCode=\$\{zip\}[`\'"];'
        js_replacement = f'const dest = `https://www.angi.com/companylist/search.htm?query={urllib.parse.quote_plus(trade)}&postalCode=${{zip}}`;\n            leadMatchLink.href = `{CJ_TRACKING_BASE}?url=${{encodeURIComponent(dest)}}`;'

        content = re.sub(js_old_pattern, js_replacement, content)

        if content != orig:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            updated_count += 1
            print(f"Updated {filename}")

    print(f"Batch completed: {updated_count} calculators updated with CJ Angi tracking.")

if __name__ == "__main__":
    main()
