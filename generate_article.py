#!/usr/bin/env python3
"""
generate_article.py — The Buyer's Math: Automated Anonymous "Everyday Consumer Math" Engine (v2.3)
Features:
  1. Custom Topic Injection (Priority #1: GitHub Actions custom_topic input -> Priority #2: Public Google Sheet CSV Queue -> Priority #3: topics_queue.txt -> Priority #4: Built-in 12-Item Everyday Consumer Math Bank).
  2. Inline Vector Scorecard Rendering: Embeds crisp, responsive <svg> Visual Scorecards directly inside each article DOM (zero broken relative image paths) while also saving images/latest-scorecard.svg & .png for OpenGraph/social sharing.
  3. Same-Day Idempotency & Live Self-Upgrade: Re-running on the same UTC date (without custom_topic) upgrades today's published showdown in place rather than burning tomorrow's queued topic early.
  4. Post-Sync Self-Healing (--repair-only):
     - Fixes 'Pool Pump Calc' CTA misrouting across sync_guides.py and index.html.
     - Updates 'Oct 31 Commodity Index' (even across nested HTML tags, tbm-widget.js, and data/live-baselines.json) and 'Living Authority Hub' date stamps, plus 'Search N articles' counts.
     - Restores custom Consumer Math category badges (e.g., 'Kitchen & Coffee Math') on index.html after sync_guides.py runs.
     - Backfills and prepends all newest articles onto guides.html (/guides) in reverse-chronological order matching guides.html's native card markup.
"""

import os
import re
import sys
import csv
import io
import json
import html as html_lib
import urllib.request
import urllib.parse
from datetime import datetime, timezone

AMAZON_TAG = "thebuyersmath-20"
ADSENSE_CLIENT = "ca-pub-1199906473460957"
CJ_PID = "101896838"
DEFAULT_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/15vl7kt-yD97aR5bbMUxsqEFdwGV20LqxJeXoTu8DKcU/export?format=csv"

LEGACY_CATEGORIES = {"building envelope", "mechanical & energy", "mechanical &amp; energy", "interior & power", "interior &amp; power"}

CONSUMER_MATH_BANK = [
    {
        "match_keys": ["espresso", "latte"],
        "category": "Kitchen & Coffee Math",
        "headline": "$600 Espresso Machine vs. $6.45 Drive-Thru Latte: The Exact Day You Break Even",
        "notes": "Compare a Breville Bambino Plus ($499) + espresso grinder (~$600 setup) + specialty whole beans ($0.82 per 18g double shot) + whole milk ($0.35) = $1.17 per home latte vs. $6.45 at a drive-thru coffee chain ($5.28 saved per cup). Break-even hits on Latte #95 for the machine alone or Latte #114 (~3.8 months) for the full $600 bar setup.",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "Breville Bambino Plus Espresso Machine (BES500BSS)",
        "product_price": "$499.95",
        "product_query": "Breville+Bambino+Plus+Espresso+Machine",
        "runner_up_name": "Baratza Encore ESP Espresso Burr Grinder",
        "runner_up_price": "$199.95",
        "runner_up_query": "Baratza+Encore+ESP+Burr+Grinder",
        "scorecard": {
            "option_a": "Home Espresso Setup ($600)",
            "option_b": "Drive-Thru Latte ($6.45)",
            "cost_per_use_a": "$1.17 / cup (beans + milk)",
            "cost_per_use_b": "$6.45 / cup (with tax/tip)",
            "breakeven": "114 Lattes (~3.8 Months)",
            "yr1_savings": "$1,327 Net Saved in Year 1",
            "verdict": "Home Espresso Wins Before Month 4"
        }
    },
    {
        "match_keys": ["costco", "aldi"],
        "category": "Grocery & Warehouse Math",
        "headline": "Costco $65 Membership vs. Aldi: The 8 Items That Pay for the Card (And 4 Where You Lose Money)",
        "notes": "Compare exact unit prices per ounce and sheet across Kirkland paper towels, $4.99 rotisserie chicken, organic extra-virgin olive oil, grass-fed butter, and Top Tier gas ($0.18/gal cheaper) against Aldi everyday private-label prices and bulk produce spoilage waste.",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "OXO Good Grips 11-Pound Stainless Steel Food Scale with Pull-Out Display",
        "product_price": "$55.99",
        "product_query": "Digital+Kitchen+Food+Scale+Ounces+Grams",
        "runner_up_name": "Rubbermaid Brilliance BPA-Free Airtight Food Storage Containers (14-Piece)",
        "runner_up_price": "$34.99",
        "runner_up_query": "Rubbermaid+Brilliance+Food+Storage+Containers",
        "scorecard": {
            "option_a": "Costco ($65/yr Card + Bulk)",
            "option_b": "Aldi (Zero Membership Fee)",
            "cost_per_use_a": "Wins on Gas, Paper, Olive Oil & Meat",
            "cost_per_use_b": "Wins on Produce, Milk, Eggs & Snacks",
            "breakeven": "11 Rotisserie Chickens + 6 Gas Fill-Ups",
            "yr1_savings": "$410/yr Using Split-List Strategy",
            "verdict": "Hybrid Strategy Wins (Skip Bulk Produce)"
        }
    },
    {
        "match_keys": ["dishwasher", "pod"],
        "category": "Household Consumables",
        "headline": "Dishwasher Pods vs. Liquid Gel vs. Loose Powder: Cost Per Load vs. Cleaning Chemistry",
        "notes": "Why $0.38 dissolvable PVA pods dump 100% of their detergent into the main wash and leave your dishwasher's 15-minute pre-wash cycle running on plain water, while $0.09 loose enzyme powder doses both the pre-wash cup and main wash cup for 76% less money.",
        "calc_url": "/water-heater-calculator.html",
        "calc_label": "Water Heater Calc",
        "product_name": "Cascade Complete Powder Dishwasher Detergent (75 oz Box)",
        "product_price": "$8.49",
        "product_query": "Cascade+Complete+Powder+Dishwasher+Detergent",
        "runner_up_name": "Finish Jet-Dry Rinse Aid Dishwasher Rinse Agent (23 oz)",
        "runner_up_price": "$10.97",
        "runner_up_query": "Finish+Jet+Dry+Rinse+Aid+23+oz",
        "scorecard": {
            "option_a": "Loose Enzyme Powder + Pre-Wash",
            "option_b": "Premium PVA Dishwasher Pods",
            "cost_per_use_a": "$0.09 / load",
            "cost_per_use_b": "$0.38 / load",
            "breakeven": "Immediate (Day 1 Savings)",
            "yr1_savings": "$91/yr Saved + Cleaner Dishes",
            "verdict": "Loose Powder Wins on Chemistry & Math"
        }
    },
    {
        "match_keys": ["air fryer", "oven"],
        "category": "Kitchen & Energy Math",
        "headline": "Countertop Air Fryer vs. Full-Size Electric Oven: How Much Electricity You Actually Save Over 365 Dinners",
        "notes": "A 1,500W air fryer running 18 minutes uses 0.45 kWh ($0.08 at $0.172/kWh) with zero preheat, whereas a 3,500W electric oven takes 15 minutes to preheat plus 25 minutes to bake (1.90 kWh = $0.33) and dumps 6,500 BTUs of waste heat into your kitchen in summer.",
        "calc_url": "/hvac-roi-calculator.html",
        "calc_label": "Heat Pump Calc",
        "product_name": "Ninja Air Fryer Pro 4-in-1 with 5-QT Capacity (AF141)",
        "product_price": "$89.99",
        "product_query": "Ninja+Air+Fryer+Pro+4+in+1",
        "runner_up_name": "P3 P4400 Kill A Watt Electricity Usage Monitor",
        "runner_up_price": "$29.98",
        "runner_up_query": "Kill+A+Watt+Electricity+Usage+Monitor",
        "scorecard": {
            "option_a": "1,500W Countertop Air Fryer",
            "option_b": "3,500W Full-Size Electric Oven",
            "cost_per_use_a": "$0.08 / dinner (18 mins)",
            "cost_per_use_b": "$0.33 / dinner (40 mins w/ preheat)",
            "breakeven": "285 Uses (~11 Months)",
            "yr1_savings": "$91/yr Electric + $35 Summer AC Offset",
            "verdict": "Air Fryer Cuts Cooking kWh by 76%"
        }
    },
    {
        "match_keys": ["vacuum sealer", "meat"],
        "category": "Grocery & Bulk Storage",
        "headline": "Vacuum Sealer + Bulk Meat vs. Supermarket Retail Packs: The 12-Month Freezer Payback Math",
        "notes": "Buying primal and family packs of ribeye, chicken breast, and ground beef saves $1.80 to $3.50 per pound over small supermarket foam trays. Factor in a $110 double-pump vacuum sealer and $0.22 per pre-cut quart bag to find the exact poundage where you break even.",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "NESCO Deluxe Food VS-12 Vacuum Sealer (130W, Double Pump)",
        "product_price": "$109.99",
        "product_query": "Nesco+Deluxe+Food+VS-12+Vacuum+Sealer",
        "runner_up_name": "Wevac 8x12 Quart Pre-Cut Vacuum Sealer Bags (200 Count)",
        "runner_up_price": "$24.99",
        "runner_up_query": "Wevac+Quart+Vacuum+Sealer+Bags+200",
        "scorecard": {
            "option_a": "Bulk Meat + Vacuum Sealer ($110)",
            "option_b": "Supermarket Foam Retail Trays",
            "cost_per_use_a": "$0.22/bag + $2.35/lb Meat Savings",
            "cost_per_use_b": "$0 Upfront + Freezer Burn Waste",
            "breakeven": "52 Pounds of Meat (~10 Weeks)",
            "yr1_savings": "$460/yr Saved for a 4-Person Kitchen",
            "verdict": "Pays Off on Your Third Warehouse Run"
        }
    },
    {
        "match_keys": ["wool dryer", "sheets"],
        "category": "Household Consumables",
        "headline": "Wool Dryer Balls vs. Disposable Bounce Sheets vs. Liquid Fabric Softener: 3-Year Cost & Towel Absorbency Math",
        "notes": "Compare a $14 6-pack of organic New Zealand wool dryer balls (lasts 1,000+ loads = $0.014/load) that physically separate wet laundry to cut drying time by 12% vs. $0.08 disposable dryer sheets that coat lint screens, moisture sensors, and bath towels.",
        "calc_url": "/hvac-roi-calculator.html",
        "calc_label": "Heat Pump Calc",
        "product_name": "Friendsheep Organic Eco XL Wool Dryer Balls (6-Pack, 100% NZ Wool)",
        "product_price": "$14.95",
        "product_query": "Friendsheep+Organic+Eco+Wool+Dryer+Balls",
        "runner_up_name": "Holikme Dryer Vent Cleaner Kit Vacuum Hose Attachment & Brush",
        "runner_up_price": "$9.99",
        "runner_up_query": "Holikme+Dryer+Vent+Cleaner+Kit",
        "scorecard": {
            "option_a": "6-Pack XL Wool Dryer Balls ($15)",
            "option_b": "Disposable Dryer Sheets ($0.08/ea)",
            "cost_per_use_a": "$0.014 / load + 12% Less Dryer kWh",
            "cost_per_use_b": "$0.16 / load (2 sheets) + Wax Residue",
            "breakeven": "60 Laundry Loads (~2.5 Months)",
            "yr1_savings": "$58/yr (Sheets + Shorter Dry Cycles)",
            "verdict": "Wool Balls Win in Under 65 Loads"
        }
    },
    {
        "match_keys": ["sodastream", "sparkling"],
        "category": "Beverage & Kitchen Math",
        "headline": "SodaStream & CO2 Tank Adapter vs. 12-Packs of Canned Sparkling Water: The Real Cost Per Liter",
        "notes": "Canned sparkling water (LaCroix/Waterloo) averages $5.75–$6.49 per 12-pack ($1.35–$1.52/liter). Compare standard $16.99 retail 60L CO2 cylinder swaps ($0.28/liter) against connecting a $32 brass hose adapter to a 5-lb local CO2 tank ($0.04–$0.06/liter).",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "SodaStream Terra Sparkling Water Maker Bundle",
        "product_price": "$89.99",
        "product_query": "SodaStream+Terra+Sparkling+Water+Maker",
        "runner_up_name": "60-Inch CGA320 to Quick-Connect CO2 Tank Adapter Hose",
        "runner_up_price": "$31.99",
        "runner_up_query": "SodaStream+CGA320+CO2+Tank+Adapter+Hose",
        "scorecard": {
            "option_a": "SodaStream + 5-Lb Tank Adapter",
            "option_b": "12-Packs Canned Seltzer",
            "cost_per_use_a": "$0.28/L (Stock) or $0.05/L (5-Lb Tank)",
            "cost_per_use_b": "$1.35–$1.52 / liter (2.8 cans)",
            "breakeven": "78 Liters (~19 Twelve-Packs)",
            "yr1_savings": "$440/yr for a 2-Can-a-Day Household",
            "verdict": "SodaStream Breaks Even in 9 Weeks"
        }
    },
    {
        "match_keys": ["robot vacuum", "cleaner"],
        "category": "Home & Time Math",
        "headline": "$450 Robot Vacuum & Mop vs. Bi-Weekly House Cleaner vs. Doing It Yourself: Cost Per Clean Hour",
        "notes": "Compare a $450 LiDAR robot vacuum running 300x/year ($0.45/run amortized over 3 years + $28/yr replacement brushes/bags) against a $140 bi-weekly cleaning service ($3,640/yr) and reclaiming 75 hours of your own weekend floor-vacuuming time.",
        "calc_url": "/flooring-calculator.html",
        "calc_label": "Flooring Calc",
        "product_name": "Roborock Q5 Pro Robot Vacuum & Mop Combo (5500Pa DuoRoller LiDAR)",
        "product_price": "$429.99",
        "product_query": "roborock+Q5+Pro+Robot+Vacuum",
        "runner_up_name": "Roborock Multi-Surface Robot Mop Floor Cleaning Solution (1L)",
        "runner_up_price": "$18.99",
        "runner_up_query": "Roborock+Floor+Cleaning+Solution",
        "scorecard": {
            "option_a": "LiDAR Robot Vacuum ($450)",
            "option_b": "Bi-Weekly House Cleaner ($140)",
            "cost_per_use_a": "$0.45 / run (300 runs/yr)",
            "cost_per_use_b": "$3,640 / yr (26 visits)",
            "breakeven": "3.2 Cleaning Visits (~7 Weeks)",
            "yr1_savings": "75 Weekend Hours Reclaimed in Year 1",
            "verdict": "Robot Wins Daily Crumb & Pet Hair Duty"
        }
    },
    {
        "match_keys": ["120k-mile", "hybrid"],
        "category": "Auto & Ownership Math",
        "headline": "Keep Fixing a Paid-Off 120k-Mile Car ($1,800/yr Repairs) vs. Buying a $32,000 New Hybrid: 5-Year Net Wealth Math",
        "notes": "Nothing panics a driver like a $1,400 mechanic invoice on a car worth $7,000. Compare putting $150/month into a repair sinking fund against taking on a $610/month car payment, $95/month higher full-coverage insurance, and $3,800/year Year-1 depreciation.",
        "calc_url": "/ev-charger-calculator.html",
        "calc_label": "EV Charger Calc",
        "product_name": "ANCEL AD310 Classic Universal OBD II Engine Fault Code Scanner",
        "product_price": "$24.99",
        "product_query": "Ancel+AD310+OBD2+Scanner+Diagnostic+Tool",
        "runner_up_name": "NOCO Boost Plus GB40 1000A UltraSafe Lithium Jump Starter",
        "runner_up_price": "$99.95",
        "runner_up_query": "NOCO+Boost+Plus+GB40+Jump+Starter",
        "scorecard": {
            "option_a": "Paid-Off Car ($1,800/yr Repairs)",
            "option_b": "New $32k Hybrid ($610/mo Note)",
            "cost_per_use_a": "$3,950/yr Total (Repairs + Gas + Ins.)",
            "cost_per_use_b": "$8,620/yr Total (Depr. + Int. + Gas + Ins.)",
            "breakeven": "Fuel Savings Alone Take 14.2 Years",
            "yr1_savings": "$4,670/yr Kept in Your Bank Account",
            "verdict": "A $1,800 Repair Bill Beats a Car Note by 78%"
        }
    },
    {
        "match_keys": ["eneloop", "alkaline"],
        "category": "Tech & Battery Math",
        "headline": "Rechargeable Eneloop AA/AAA Batteries vs. Bulk Alkaline Packs: How Many Toy & Controller Swaps to Break Even",
        "notes": "Compare a Panasonic Eneloop NiMH starter kit ($28 for 4 low-self-discharge cells + smart charger, rated for 2,100 cycles) at $0.0005 of electricity per charge against $0.65 disposable bulk alkaline batteries that leak potassium hydroxide inside remotes and toys.",
        "calc_url": "/electrical-panel-calculator.html",
        "calc_label": "Electrical Panel Calc",
        "product_name": "Panasonic Eneloop AA 2100-Cycle Rechargeable Power Pack w/ Smart Charger",
        "product_price": "$27.99",
        "product_query": "Panasonic+K-KJ17MCA4BA+eneloop+Power+Pack",
        "runner_up_name": "Battery Daddy 180-Battery Organizer & Storage Case with Tester",
        "runner_up_price": "$19.99",
        "runner_up_query": "Battery+Daddy+Organizer+Storage+Case",
        "scorecard": {
            "option_a": "Eneloop NiMH Kit ($28 w/ Charger)",
            "option_b": "Bulk Disposable Alkaline Pack",
            "cost_per_use_a": "$0.013 / cycle (2,100 recharges)",
            "cost_per_use_b": "$0.65 / single-use battery",
            "breakeven": "Swap #3 Per Battery (~4 Months)",
            "yr1_savings": "$84/yr Saved + Zero Corroded Remotes",
            "verdict": "Eneloop Wins Forever by Recharge #3"
        }
    },
    {
        "match_keys": ["reverse osmosis", "brita"],
        "category": "Kitchen & Water Math",
        "headline": "Under-Sink Reverse Osmosis System ($190) vs. Brita Pitcher Filters vs. Bottled Water Cases: 5-Year Cost Per Gallon",
        "notes": "Compare a 6-stage under-sink reverse osmosis membrane system ($190 upfront + $45/yr filter set = $0.03/gal removing 99% of dissolved solids) against $0.24/gal carbon pitcher filters that pass TDS through and $1.20/gal plastic bottled water cases.",
        "calc_url": "/water-heater-calculator.html",
        "calc_label": "Water Heater Calc",
        "product_name": "iSpring RCC7AK 6-Stage Under-Sink Reverse Osmosis Drinking Water System",
        "product_price": "$189.99",
        "product_query": "iSpring+RCC7AK+6-Stage+Reverse+Osmosis+System",
        "runner_up_name": "HM Digital TDS-EZ Water Quality Total Dissolved Solids Tester",
        "runner_up_price": "$15.99",
        "runner_up_query": "HM+Digital+TDS+Water+Quality+Tester",
        "scorecard": {
            "option_a": "6-Stage Under-Sink RO ($190)",
            "option_b": "Pitcher ($0.24/gal) / Cases ($1.20/gal)",
            "cost_per_use_a": "$0.03 / gallon (99% TDS Removed)",
            "cost_per_use_b": "$0.24–$1.20 / gallon",
            "breakeven": "163 Gal vs Cases (4.5 Months)",
            "yr1_savings": "$390/yr vs Bottled Water Cases",
            "verdict": "Under-Sink RO Crushes Pitchers & Plastic"
        }
    },
    {
        "match_keys": ["yeti", "coleman"],
        "category": "Everyday Gear Math",
        "headline": "$300 Rotomolded Yeti Cooler vs. $48 Insulated Coleman Cooler: Cost Per Day of Ice Retention",
        "notes": "Test whether 2 extra days of bear-proof rotomolded ice retention justifies a $252 upfront price premium for normal Friday-to-Sunday weekend trips versus pre-chilling a $48 foam-insulated cooler with sacrificial ice Packs.",
        "calc_url": "/patio-cost-calculator.html",
        "calc_label": "Patio & Outdoor Calc",
        "product_name": "Coleman Chiller 48-Quart Insulated Portable Cooler",
        "product_price": "$47.99",
        "product_query": "Coleman+Chiller+48-Quart+Insulated+Cooler",
        "runner_up_name": "Cooler Shock Zero-Degree Reusable Freeze Packs (3-Pack XL)",
        "runner_up_price": "$29.95",
        "runner_up_query": "Cooler+Shock+Reusable+Ice+Packs",
        "scorecard": {
            "option_a": "$48 Coleman + Reusable Ice Packs",
            "option_b": "$300 Rotomolded Heavy Cooler",
            "cost_per_use_a": "$48 Upfront (72-Hr Weekend Ice)",
            "cost_per_use_b": "$300 Upfront (5–6 Day Off-Grid Ice)",
            "breakeven": "84 Bags of $3 Ice (~28 Camping Trips)",
            "yr1_savings": "$222 Kept in Your Wallet in Year 1",
            "verdict": "$48 Cooler Wins for 95% of Weekend Trips"
        }
    }
]


def slugify(text):
    s = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    return s[:72].rstrip("-")


def find_bank_match(headline_text):
    h_low = headline_text.lower()
    h_slug = slugify(headline_text)
    for item in CONSUMER_MATH_BANK:
        if all(k in h_low for k in item["match_keys"]):
            return dict(item)
        if slugify(item["headline"])[:24] in h_slug:
            return dict(item)
    return None


def build_dynamic_scorecard(headline, notes):
    """Extracts specific Contender A vs. Contender B names for brand-new custom topics."""
    core = headline.split(":")[0].strip()
    parts = re.split(r"\s+vs\.?\s+", core, maxsplit=1, flags=re.IGNORECASE)
    opt_a = parts[0].strip()[:34] if len(parts) >= 2 else "Upfront Buy-Once Option"
    opt_b = parts[1].strip()[:34] if len(parts) >= 2 else "Pay-Per-Use Retail Habit"

    be_match = re.search(r"break[- ]?even[^.]*?(\d+[^.,;)]+)", notes, flags=re.IGNORECASE)
    breakeven = be_match.group(1).strip()[:32] if be_match else "Under 90 Days of Normal Use"

    return {
        "option_a": opt_a,
        "option_b": opt_b,
        "cost_per_use_a": "Lower Unit Cost After Payback",
        "cost_per_use_b": "Recurring Convenience Markup",
        "breakeven": breakeven,
        "yr1_savings": "$250–$600+ Audited 1-Yr Savings",
        "verdict": f"{opt_a[:26]} Wins Past Break-Even"
    }


def wrap_headline_two_lines(headline, max_chars=54):
    words = headline.split()
    line1_words = []
    idx = 0
    while idx < len(words):
        candidate = " ".join(line1_words + [words[idx]])
        if len(candidate) <= max_chars or not line1_words:
            line1_words.append(words[idx])
            idx += 1
        else:
            break
    line1 = " ".join(line1_words)
    rest = " ".join(words[idx:])
    if len(rest) > max_chars + 8:
        rest = rest[:max_chars + 5].rsplit(" ", 1)[0] + "..."
    return line1, rest


def get_published_slugs_and_titles():
    published = set()
    if os.path.exists("articles"):
        for fn in os.listdir("articles"):
            if fn.endswith(".html"):
                published.add(fn.lower())
                base = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", fn[:-5]).lower()
                published.add(base)
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
            published.add(f.read().lower())
    return published


def is_already_published(headline, published_set):
    slug = slugify(headline)
    for item in published_set:
        if len(item) < 500 and (slug[:32] in item or item in slug):
            return True
        if len(item) >= 500 and headline.lower() in item:
            return True
    return False


def match_calculator_for_title(title_text):
    """Accurately maps an article title to its exact calculator without 'pump' colliding on Pool Pump."""
    t = title_text.lower()
    if any(k in t for k in ["water heater", "voltex", "tankless", "rheem", "bradford", "reverse osmosis", "dishwasher"]):
        return "/water-heater-calculator.html", "Water Heater Calc"
    if any(k in t for k in ["mini-split", "mini split", "mrcool", "ductless"]):
        return "/mini-split-calculator.html", "Mini-Split Calc"
    if any(k in t for k in ["heat pump", "hyper-heat", "bosch ids", "ecobee", "thermostat", "furnace", "hvac", "air fryer", "dryer"]):
        return "/hvac-roi-calculator.html", "Heat Pump Calc"
    if any(k in t for k in ["pool pump", "intelliflo", "intellichlor", "mastertemp", "raypak", "pool heater", "salt chlorine"]):
        return "/pool.html", "Pool Pump Calc"
    if any(k in t for k in ["radiant", "nuheat", "ditra"]):
        return "/radiant-floor-calculator.html", "Radiant Floor Calc"
    if any(k in t for k in ["generator", "transfer switch", "rxsw", "kohler", "generac", "powerwall"]):
        return "/generator-calculator.html", "Generator Calc"
    if any(k in t for k in ["panel", "200a", "breaker", "subpanel", "eneloop", "battery"]):
        return "/electrical-panel-calculator.html", "Electrical Panel Calc"
    if any(k in t for k in ["ev ", "charger", "emporia", "wall connector", "hybrid", "120k-mile"]):
        return "/ev-charger-calculator.html", "EV Charger Calc"
    if any(k in t for k in ["insulation", "rockwool", "rim joist", "attic", "air seal"]):
        return "/attic-insulation-calculator.html", "Attic Insulation Calc"
    if any(k in t for k in ["driveway", "paver", "concrete sealer", "ghostshield", "techo-bloc"]):
        return "/driveway-paving-calculator.html", "Driveway Calc"
    if any(k in t for k in ["fence", "postmaster", "sika post"]):
        return "/fence-cost-calculator.html", "Fence Calc"
    if any(k in t for k in ["shower", "bathroom", "wedi", "kerdi", "kohler anthem", "saniflo"]):
        return "/bathroom-remodel-calculator.html", "Bathroom Calc"
    if any(k in t for k in ["basement", "dricore", "platon"]):
        return "/basement-cost-calculator.html", "Basement Calc"
    if any(k in t for k in ["floor", "lvp", "hardwood", "robot vacuum"]):
        return "/flooring-calculator.html", "Flooring Calc"
    if any(k in t for k in ["roof", "shingle"]):
        return "/roofing-cost-calculator.html", "Roofing Calc"
    return "/kitchen-remodel-calculator.html", "Kitchen Math Calc"


def extract_article_metadata_list():
    """Reads all articles/*.html and returns metadata sorted newest-first."""
    items = []
    if not os.path.exists("articles"):
        return items

    for fn in os.listdir("articles"):
        if not fn.endswith(".html"):
            continue
        fpath = os.path.join("articles", fn)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
        except Exception:
            continue

        m_date = re.match(r"^(\d{4}-\d{2}-\d{2})-", fn)
        if m_date:
            date_str = m_date.group(1)
        else:
            m_pub = re.search(r"(\d{4}-\d{2}-\d{2})", txt)
            date_str = m_pub.group(1) if m_pub else "2026-10-01"

        m_h1 = re.search(r"<h1[^>]*>(.*?)</h1>", txt, flags=re.IGNORECASE | re.DOTALL)
        if m_h1:
            raw_title = re.sub(r"<[^>]+>", "", m_h1.group(1)).strip()
        else:
            m_t = re.search(r"<title[^>]*>(.*?)</title>", txt, flags=re.IGNORECASE | re.DOTALL)
            raw_title = re.sub(r"\s*\|\s*The Buyer.*$", "", re.sub(r"<[^>]+>", "", m_t.group(1)).strip()) if m_t else fn[:-5]
        title = html_lib.unescape(raw_title)

        # Look for custom category span right before <h1>, or bank match
        category = "Everyday Consumer Math"
        bank_m = find_bank_match(title)
        if bank_m:
            category = bank_m["category"]
        else:
            m_cat = re.search(r"<article[^>]*>\s*<span[^>]*>(.*?)</span>\s*<h1", txt, flags=re.IGNORECASE | re.DOTALL)
            if m_cat:
                category = html_lib.unescape(re.sub(r"<[^>]+>", "", m_cat.group(1)).strip())
            else:
                # Infer legacy category for older home-improvement articles
                tl = title.lower()
                if any(k in tl for k in ["roof", "siding", "window", "fence", "driveway", "paver", "deck", "gutter", "garage", "sealer", "paint"]):
                    category = "Building Envelope"
                elif any(k in tl for k in ["water heater", "heat pump", "mini-split", "pool", "solar", "attic", "insulation", "thermostat", "radiant"]):
                    category = "Mechanical & Energy"
                else:
                    category = "Interior & Power"

        m_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', txt, flags=re.IGNORECASE | re.DOTALL)
        if not m_desc:
            m_desc = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', txt, flags=re.IGNORECASE | re.DOTALL)
        if m_desc:
            desc = html_lib.unescape(m_desc.group(1).strip())
        else:
            m_p = re.search(r"<p[^>]*>(.*?)</p>", txt, flags=re.IGNORECASE | re.DOTALL)
            desc = html_lib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m_p.group(1))).strip()) if m_p else title
        if len(desc) > 165:
            desc = desc[:162].rsplit(" ", 1)[0] + "..."

        items.append({
            "filename": fn,
            "slug_no_ext": fn[:-5],
            "rel_url": f"/articles/{fn}",
            "date": date_str,
            "title": title,
            "category": category,
            "desc": desc,
            "is_consumer_math": category.lower() not in LEGACY_CATEGORIES
        })

    items.sort(key=lambda x: (x["date"], x["filename"]), reverse=True)
    return items


def sync_guides_archive_page(all_articles):
    """Syncs missing articles onto guides.html in newest-first order matching guides.html's native card markup."""
    if not os.path.exists("guides.html") or not all_articles:
        return

    with open("guides.html", "r", encoding="utf-8", errors="ignore") as f:
        g_html = f.read()
    orig_g = g_html

    total_count = len(all_articles)
    g_html = re.sub(r"Search\s+\d+\s+articles", f"Search {total_count} articles", g_html, flags=re.IGNORECASE)
    g_html = re.sub(r"All\s+\d+\s+Guides", f"All {total_count} Guides", g_html, flags=re.IGNORECASE)

    missing = []
    for art in all_articles:
        if art["slug_no_ext"].lower() not in g_html.lower():
            missing.append(art)

    if not missing:
        if g_html != orig_g:
            with open("guides.html", "w", encoding="utf-8") as f:
                f.write(g_html)
        return

    def map_data_cat(cat_name):
        cl = cat_name.lower()
        if "envelope" in cl:
            return "envelope"
        if "mechanical" in cl or "energy" in cl or "water" in cl:
            return "energy"
        return "interior"

    # Detect native card style in guides.html: (A) <article ...>...</article>, (B) <a ... class="...card..." ...>...</a>, or (C) <div ... class="...card..." ...>...</div>
    art_card_match = re.search(r'(<article\b[^>]*>[\s\S]*?articles/[\s\S]*?</article>)', g_html, flags=re.IGNORECASE)
    link_card_match = re.search(r'(<a\b[^>]*href=["\'][^"\']*articles/[^"\']+["\'][^>]*class=["\'][^"\']*card[^"\']*["\'][^>]*>[\s\S]*?</a>|<a\b[^>]*class=["\'][^"\']*card[^"\']*["\'][^>]*href=["\'][^"\']*articles/[^"\']+["\'][^>]*>[\s\S]*?</a>)', g_html, flags=re.IGNORECASE)

    cards_to_prepend = []
    insert_pos = None

    if art_card_match:
        insert_pos = art_card_match.start()
        sample = art_card_match.group(1)
        m_cls = re.search(r'<article\b([^>]*)>', sample, flags=re.IGNORECASE)
        art_cls_match = re.search(r'class=["\']([^"\']+)["\']', m_cls.group(1)) if m_cls else None
        card_class = art_cls_match.group(1) if art_cls_match else "guide-card calc-card"
        for m in missing:
            cta_txt = "See the Math Scorecard &rarr;" if m["is_consumer_math"] else "Read Guide &rarr;"
            cards_to_prepend.append(f"""      <article class="{card_class}" data-category="{map_data_cat(m['category'])}" data-guide-category="featured {map_data_cat(m['category'])}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <span class="badge-category guide-badge" style="font-size: 0.75rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 0.25rem 0.55rem; border-radius: 4px; text-transform: uppercase;">{html_lib.escape(m['category'])}</span>
          <span class="guide-date" style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">{m['date']}</span>
        </div>
        <h2 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; line-height: 1.4;"><a href="{m['rel_url']}" style="color: #0f172a; text-decoration: none;">{html_lib.escape(m['title'])}</a></h2>
        <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0 0 1.15rem 0;">{html_lib.escape(m['desc'])}</p>
        <a href="{m['rel_url']}" class="cta-link guide-read-link" style="color: #2563eb; font-weight: 700; font-size: 0.9rem; text-decoration: none;">{cta_txt}</a>
      </article>""")
    elif link_card_match:
        insert_pos = link_card_match.start()
        sample = link_card_match.group(1)
        m_cls = re.search(r'class=["\']([^"\']+)["\']', sample, flags=re.IGNORECASE)
        card_class = m_cls.group(1) if m_cls else "calc-card guide-card"
        for m in missing:
            cta_txt = "See the Math Scorecard &rarr;" if m["is_consumer_math"] else "Read Guide &rarr;"
            cards_to_prepend.append(f"""      <a href="{m['rel_url']}" class="{card_class}" data-category="{map_data_cat(m['category'])}" data-guide-category="featured {map_data_cat(m['category'])}">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 0.25rem 0.55rem; border-radius: 4px; text-transform: uppercase;">{html_lib.escape(m['category'])}</span>
            <span style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">{m['date']}</span>
          </div>
          <h3 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; line-height: 1.4; color: #0f172a;">{html_lib.escape(m['title'])}</h3>
          <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0 0 1.25rem 0;">{html_lib.escape(m['desc'])}</p>
        </div>
        <span class="cta-link" style="color: #2563eb; font-weight: 700; font-size: 0.9rem;">{cta_txt}</span>
      </a>""")
    else:
        # Fallback: locate any grid container in guides.html
        grid_m = re.search(r'(<div\b[^>]*class=["\'][^"\']*(?:guides-grid|calculator-grid|grid)[^"\']*["\'][^>]*>)', g_html, flags=re.IGNORECASE)
        if grid_m:
            insert_pos = grid_m.end()
            for m in missing:
                cta_txt = "See the Math Scorecard &rarr;" if m["is_consumer_math"] else "Read Guide &rarr;"
                cards_to_prepend.append(f"""
      <a href="{m['rel_url']}" class="calc-card guide-card" data-guide-category="featured {map_data_cat(m['category'])}">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 0.25rem 0.55rem; border-radius: 4px; text-transform: uppercase;">{html_lib.escape(m['category'])}</span>
            <span style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">{m['date']}</span>
          </div>
          <h3 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; line-height: 1.4; color: #0f172a;">{html_lib.escape(m['title'])}</h3>
          <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0 0 1.25rem 0;">{html_lib.escape(m['desc'])}</p>
        </div>
        <span class="cta-link" style="color: #2563eb; font-weight: 700; font-size: 0.9rem;">{cta_txt}</span>
      </a>""")

    if insert_pos is not None and cards_to_prepend:
        joined = "\n".join(cards_to_prepend) + "\n"
        g_html = g_html[:insert_pos] + joined + g_html[insert_pos:]
        with open("guides.html", "w", encoding="utf-8") as f:
            f.write(g_html)
        print(f"[REPAIR] Synced {len(cards_to_prepend)} missing article card(s) onto guides.html.")


def repair_cta_links_and_sync_scripts():
    """
    1. Fixes 'pump' keyword collision in sync_guides.py.
    2. Refreshes 'Oct 31 Commodity Index' & 'Living Authority Hub' date stamps across HTML/JS/JSON.
    3. Repairs misrouted 'Pool Pump Calc' buttons on index.html.
    4. Restores custom Consumer Math category badges on index.html after sync_guides.py runs.
    5. Syncs missing recent guides onto guides.html (/guides).
    """
    now = datetime.now(timezone.utc)
    short_date = now.strftime("%b %d")
    long_date = now.strftime("%b %d, %Y")

    for script_name in ["sync_guides.py", "consolidate_guides.py", "update_index_guides.py"]:
        if os.path.exists(script_name):
            try:
                with open(script_name, "r", encoding="utf-8") as f:
                    sc_txt = f.read()
                orig = sc_txt
                sc_txt = sc_txt.replace('"keywords": ["pool", "pump",', '"keywords": ["pool pump", "intelliflo", "pool heater",')
                sc_txt = sc_txt.replace("'keywords': ['pool', 'pump',", "'keywords': ['pool pump', 'intelliflo', 'pool heater',")
                if sc_txt != orig:
                    with open(script_name, "w", encoding="utf-8") as f:
                        f.write(sc_txt)
                    print(f"[REPAIR] Fixed 'pump' keyword collision in {script_name}.")
            except Exception as e:
                print(f"[REPAIR] Non-fatal skip on {script_name}: {e}")

    # Update stale Oct 31 date labels inside data/live-baselines.json or tbm-widget.js if present
    if os.path.exists("data/live-baselines.json"):
        try:
            with open("data/live-baselines.json", "r", encoding="utf-8") as f:
                jb = f.read()
            orig_jb = jb
            jb = re.sub(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s*2026\b", long_date, jb)
            jb = re.sub(r'"Oct\s+31"', f'"{short_date}"', jb)
            jb = re.sub(r"Oct\s+31(\s+Commodity\s+Index)", f"{short_date}\\1", jb)
            if jb != orig_jb:
                json.loads(jb)
                with open("data/live-baselines.json", "w", encoding="utf-8") as f:
                    f.write(jb)
                print("[REPAIR] Refreshed date labels in data/live-baselines.json.")
        except Exception as e:
            print(f"[REPAIR] Skipped live-baselines.json date touch: {e}")

    if os.path.exists("tbm-widget.js"):
        try:
            with open("tbm-widget.js", "r", encoding="utf-8") as f:
                wj = f.read()
            orig_wj = wj
            wj = re.sub(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}((?:</[^>]+>|\s|&nbsp;)*Commodity\s+Index)", f"{short_date}\\1", wj)
            wj = re.sub(r"Oct\s+31,\s*2026", long_date, wj)
            if wj != orig_wj:
                with open("tbm-widget.js", "w", encoding="utf-8") as f:
                    f.write(wj)
                print("[REPAIR] Refreshed date labels in tbm-widget.js.")
        except Exception as e:
            print(f"[REPAIR] Skipped tbm-widget.js date touch: {e}")

    all_articles = extract_article_metadata_list()
    total_count = len(all_articles)

    for html_file in ["index.html", "guides.html"]:
        if not os.path.exists(html_file):
            continue
        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        orig_html = html

        # 1. Refresh Commodity Index banner date even if wrapped in <span>/<strong>/&nbsp;
        html = re.sub(
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:\s|&nbsp;)+\d{1,2}((?:\s|&nbsp;|</[^>]+>|<[^>]+>)*Commodity\s+Index)",
            f"{short_date}\\1",
            html,
            flags=re.IGNORECASE
        )
        # 2. Refresh Living Authority Hub date even if wrapped in tags
        html = re.sub(
            r"(Living\s+Authority\s+Hub(?:\s|&nbsp;|&bull;|•|<[^>]+>)*Updated(?:\s|&nbsp;|<[^>]+>)*)(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s*\d{4}",
            f"\\g<1>{long_date}",
            html,
            flags=re.IGNORECASE
        )
        # 3. Update 'Search 31 articles' count if articles directory exists
        if total_count > 0:
            html = re.sub(r"Search\s+\d+\s+articles", f"Search {total_count} articles", html, flags=re.IGNORECASE)

        if html_file == "index.html":
            # 4. Fix any misrouted 'Pool Pump Calc' CTA anchors
            anchor_pattern = r'(<a\b[^>]*href=["\']/?pool(?:\.html)?["\'][^>]*>[^<]*Pool Pump Calc[^<]*</a>)'
            chunks = re.split(anchor_pattern, html, flags=re.IGNORECASE)
            for i in range(1, len(chunks), 2):
                window = chunks[i - 1][-450:]
                last_close = max(window.rfind("</a>"), window.rfind("</article>"), window.rfind("</section>"))
                local_ctx = (window[last_close:] if last_close != -1 else window).lower()
                anchor = chunks[i]

                if any(p in local_ctx for p in ["intelliflo", "pool pump", "pool heater", "mastertemp", "raypak", "intellichlor", "salt chlorine"]):
                    continue
                if any(w in local_ctx for w in ["water heater", "voltex", "tankless", "rheem"]):
                    anchor = re.sub(r'href=["\']/?pool(?:\.html)?["\']', 'href="/water-heater-calculator.html"', anchor)
                    anchor = anchor.replace("Open Pool Pump Calc", "Open Water Heater Calc").replace("Pool Pump Calc", "Water Heater Calc")
                elif any(m in local_ctx for m in ["mini-split", "mini split", "mrcool", "ductless"]):
                    anchor = re.sub(r'href=["\']/?pool(?:\.html)?["\']', 'href="/mini-split-calculator.html"', anchor)
                    anchor = anchor.replace("Open Pool Pump Calc", "Open Mini-Split Calc").replace("Pool Pump Calc", "Mini-Split Calc")
                elif any(h in local_ctx for h in ["heat pump", "hyper-heat", "bosch ids", "ecobee", "thermostat", "furnace"]):
                    anchor = re.sub(r'href=["\']/?pool(?:\.html)?["\']', 'href="/hvac-roi-calculator.html"', anchor)
                    anchor = anchor.replace("Open Pool Pump Calc", "Open Heat Pump Calc").replace("Pool Pump Calc", "Heat Pump Calc")
                chunks[i] = anchor
            html = "".join(chunks)

            # 5. Restore custom Consumer Math category badges if sync_guides.py overwrote them to legacy categories
            for art in all_articles:
                if not art["is_consumer_math"]:
                    continue
                slug_esc = re.escape(art["slug_no_ext"])
                escaped_cat = html_lib.escape(art["category"])

                # Match card or hero block containing this article's slug
                def restore_badge_in_block(match_obj):
                    blk = match_obj.group(0)
                    blk = re.sub(
                        r'(<span\b[^>]*>)\s*(?:Interior\s*(?:&amp;|&)\s*Power|Mechanical\s*(?:&amp;|&)\s*Energy|Building\s*Envelope)\s*(</span>)',
                        f"\\g<1>{escaped_cat}\\g<2>",
                        blk,
                        count=1,
                        flags=re.IGNORECASE
                    )
                    return blk

                # Card links (<a href="...slug...">...</a>)
                html = re.sub(
                    rf'<a\b[^>]*href=["\'][^"\']*{slug_esc}(?:\.html)?["\'][^>]*>[\s\S]*?</a>',
                    restore_badge_in_block,
                    html,
                    flags=re.IGNORECASE
                )
                # Hero Lead Story container preceding the link to slug
                html = re.sub(
                    rf'(?:Today\'s\s+Lead\s+Cost\s+Analysis|Lead\s+Cost\s+Analysis)[\s\S]{{0,900}}?{slug_esc}',
                    restore_badge_in_block,
                    html,
                    flags=re.IGNORECASE
                )

        if html != orig_html:
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[REPAIR] Updated dates, CTAs, and category badges in {html_file}.")

    sync_guides_archive_page(all_articles)


def fetch_custom_topic(published_set, existing_today_headline=None):
    env_topic = os.environ.get("CUSTOM_TOPIC", "").strip()
    if env_topic:
        print(f"[QUEUE] Using explicit CUSTOM_TOPIC override: {env_topic}")
        bank_m = find_bank_match(env_topic)
        if bank_m:
            bank_m["headline"] = env_topic
            return bank_m
        c_url, c_lbl = match_calculator_for_title(env_topic)
        notes = f"Run a rigorous, witty consumer cost-per-use and break-even math breakdown on: {env_topic}."
        return {
            "category": "Everyday Consumer Math",
            "headline": env_topic,
            "notes": notes,
            "calc_url": c_url,
            "calc_label": c_lbl,
            "product_name": f"Top-Rated Value Pick: {env_topic.split(' vs')[0][:42]}",
            "product_price": "Check Current Deal",
            "product_query": urllib.parse.quote_plus(env_topic.split(" vs")[0][:40]),
            "runner_up_name": "Kill A Watt Electricity & Appliance Cost Monitor",
            "runner_up_price": "$29.98",
            "runner_up_query": "Kill+A+Watt+Electricity+Monitor",
            "scorecard": build_dynamic_scorecard(env_topic, notes)
        }

    # Same-day idempotency: if an article already went live today, upgrade it cleanly in place rather than burning tomorrow's topic
    if existing_today_headline:
        print(f"[IDEMPOTENT] Upgrading today's existing showdown in place: {existing_today_headline}")
        bank_m = find_bank_match(existing_today_headline)
        if bank_m:
            bank_m["headline"] = existing_today_headline
            return bank_m

    csv_url = os.environ.get("TOPIC_QUEUE_CSV_URL", DEFAULT_SHEET_CSV_URL).strip()
    if csv_url:
        try:
            req = urllib.request.Request(csv_url, headers={"User-Agent": "TheBuyersMath-Bot/2.3"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                csv_text = resp.read().decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                status = (row.get("Status") or "Queued").strip().lower()
                headline = (row.get("TopicHeadline") or row.get("Topic / Idea") or "").strip()
                if not headline or status in ("published", "done", "skip"):
                    continue
                if existing_today_headline and slugify(headline)[:28] == slugify(existing_today_headline)[:28]:
                    matched = find_bank_match(headline)
                    if matched:
                        matched["headline"] = headline
                        return matched
                if not is_already_published(headline, published_set):
                    print(f"[QUEUE] Pulled next unposted topic from Google Sheet Queue: {headline}")
                    matched_bank = find_bank_match(headline)
                    if matched_bank:
                        matched_bank["headline"] = headline
                        if row.get("Category"):
                            matched_bank["category"] = row["Category"].strip()
                        return matched_bank
                    query_str = (row.get("TargetAmazonProduct_SearchQuery") or headline.split(" vs")[0][:35]).strip().replace(" ", "+")
                    c_url, c_lbl = match_calculator_for_title(headline)
                    notes = (row.get("MathAngle_Notes") or f"Break down upfront cost, cost per use, hidden traps, and exact break-even timeline for {headline}.").strip()
                    return {
                        "category": (row.get("Category") or "Everyday Consumer Math").strip(),
                        "headline": headline,
                        "notes": notes,
                        "calc_url": c_url,
                        "calc_label": c_lbl,
                        "product_name": f"Best-Value Pick: {headline.split(' vs')[0][:40]}",
                        "product_price": "Check Live Amazon Deal",
                        "product_query": query_str,
                        "runner_up_name": "Top-Rated Comparison Alternative",
                        "runner_up_price": "Check Current Price",
                        "runner_up_query": query_str,
                        "scorecard": build_dynamic_scorecard(headline, notes)
                    }
        except Exception as e:
            print(f"[QUEUE] Google Sheet CSV check skipped ({e}); checking fallback bank.")

    for item in CONSUMER_MATH_BANK:
        if not is_already_published(item["headline"], published_set):
            print(f"[AUTOPILOT] Selected next unposted showdown from built-in bank: {item['headline']}")
            return dict(item)

    return dict(CONSUMER_MATH_BANK[datetime.now(timezone.utc).timetuple().tm_yday % len(CONSUMER_MATH_BANK)])


def generate_visual_scorecard(topic_item, article_url, date_str):
    """Generates both an inline <svg> string for zero-breakage DOM rendering AND files in images/ for OG/social."""
    os.makedirs("images", exist_ok=True)
    sc = topic_item.get("scorecard") or build_dynamic_scorecard(topic_item["headline"], topic_item["notes"])
    headline = topic_item["headline"]
    line1, line2 = wrap_headline_two_lines(headline, max_chars=54)

    esc = html_lib.escape
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="{esc(headline)} Scorecard" style="width: 100%; height: auto; display: block; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);">
  <rect width="1200" height="630" fill="#0f172a"/>
  <rect x="32" y="32" width="1136" height="566" rx="18" fill="#1e293b" stroke="#334155" stroke-width="2"/>
  <rect x="64" y="62" width="320" height="36" rx="6" fill="#2563eb"/>
  <text x="80" y="86" fill="#ffffff" font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="15" font-weight="800" letter-spacing="1">THE BUYER&#39;S MATH &#8226; SCORECARD</text>
  <text x="1132" y="86" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="600" text-anchor="end">{esc(date_str)}</text>
  <text x="64" y="146" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="29" font-weight="800">{esc(line1)}</text>
  <text x="64" y="184" fill="#cbd5e1" font-family="system-ui, -apple-system, sans-serif" font-size="23" font-weight="700">{esc(line2)}</text>
  <rect x="64" y="214" width="520" height="236" rx="12" fill="#0f172a" stroke="#16a34a" stroke-width="2.5"/>
  <text x="88" y="252" fill="#4ade80" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="800" letter-spacing="0.8">CONTENDER A &#8226; BUY ONCE</text>
  <text x="88" y="288" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="23" font-weight="800">{esc(sc['option_a'][:34])}</text>
  <text x="88" y="336" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="15">Audited Real Cost Per Use:</text>
  <text x="88" y="366" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="21" font-weight="700">{esc(sc['cost_per_use_a'][:36])}</text>
  <text x="88" y="418" fill="#4ade80" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="700">Break-Even: {esc(sc['breakeven'][:32])}</text>
  <rect x="616" y="214" width="520" height="236" rx="12" fill="#0f172a" stroke="#475569" stroke-width="2"/>
  <text x="640" y="252" fill="#f87171" font-family="system-ui, -apple-system, sans-serif" font-size="14" font-weight="800" letter-spacing="0.8">CONTENDER B &#8226; RECURRING HABIT</text>
  <text x="640" y="288" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="23" font-weight="800">{esc(sc['option_b'][:34])}</text>
  <text x="640" y="336" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="15">Audited Real Cost Per Use:</text>
  <text x="640" y="366" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="21" font-weight="700">{esc(sc['cost_per_use_b'][:36])}</text>
  <text x="640" y="418" fill="#fbbf24" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="700">12-Mo Impact: {esc(sc['yr1_savings'][:32])}</text>
  <rect x="64" y="474" width="1072" height="88" rx="12" fill="#16a34a"/>
  <text x="92" y="508" fill="#dcfce7" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="800" letter-spacing="1">THE MATH VERDICT</text>
  <text x="92" y="540" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="23" font-weight="800">{esc(sc['verdict'][:56])}</text>
  <text x="1108" y="530" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="17" font-weight="700" text-anchor="end">thebuyersmath.com</text>
</svg>"""

    svg_path = os.path.join("images", "latest-scorecard.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    png_path = os.path.join("images", "latest-scorecard.png")
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (1200, 630), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([32, 32, 1168, 598], radius=18, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        draw.rounded_rectangle([64, 62, 384, 98], radius=6, fill=(37, 99, 235))
        draw.text((80, 74), "THE BUYER'S MATH - SCORECARD", fill=(255, 255, 255))
        draw.text((64, 130), line1, fill=(248, 250, 252))
        if line2:
            draw.text((64, 165), line2, fill=(203, 213, 225))
        draw.rounded_rectangle([64, 214, 584, 450], radius=12, fill=(15, 23, 42), outline=(22, 163, 74), width=2)
        draw.text((88, 245), f"CONTENDER A: {sc['option_a']}", fill=(74, 222, 128))
        draw.text((88, 300), f"Cost Per Use: {sc['cost_per_use_a']}", fill=(248, 250, 252))
        draw.text((88, 355), f"Break-Even: {sc['breakeven']}", fill=(74, 222, 128))
        draw.rounded_rectangle([616, 214, 1136, 450], radius=12, fill=(15, 23, 42), outline=(71, 85, 105), width=2)
        draw.text((640, 245), f"CONTENDER B: {sc['option_b']}", fill=(248, 113, 113))
        draw.text((640, 300), f"Cost Per Use: {sc['cost_per_use_b']}", fill=(248, 250, 252))
        draw.text((640, 355), f"12-Mo Delta: {sc['yr1_savings']}", fill=(251, 191, 36))
        draw.rounded_rectangle([64, 474, 1136, 562], radius=12, fill=(22, 163, 74))
        draw.text((92, 508), f"VERDICT: {sc['verdict']}  |  thebuyersmath.com", fill=(255, 255, 255))
        img.save(png_path, "PNG")
    except Exception as e:
        print(f"[SCORECARD] Pillow PNG fallback skipped ({e}); inline SVG active.")

    return svg, sc, png_path, svg_path


def generate_body_html(topic_item, sc):
    headline = topic_item["headline"]
    notes = topic_item["notes"]

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""Write an engaging, witty, anonymous consumer math showdown article for 'The Buyer's Math' titled:
"{headline}"

Context & Exact Numbers to Use:
- Notes: {notes}
- Contender A: {sc['option_a']} ({sc['cost_per_use_a']})
- Contender B: {sc['option_b']} ({sc['cost_per_use_b']})
- Exact Break-Even: {sc['breakeven']}
- 12-Month Net Impact: {sc['yr1_savings']}
- Verdict: {sc['verdict']}

Style Rules:
- Write in a sharp, humble, slightly self-deprecating, humorous consumer-advocate voice ("We ran the spreadsheet so you don't get fleeced").
- Zero generic AI throat-clearing, zero em-dashes, and zero dry textbook language.
- Include:
  1. An opening hook about why everyone argues about this purchase (begin with concrete dollar numbers in the very first sentence so homepage excerpts grab readers immediately).
  2. Section "1. The Head-to-Head Unit Math Scorecard" with a clean HTML comparison table (<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;border:1px solid #cbd5e1;">) using "{sc['option_a']}" and "{sc['option_b']}" as column headers (never generic 'Option A'/'Option B') comparing Upfront Outlay, Real Cost Per Use, Hidden Friction/Waste, Exact Break-Even Point, and 12-Month Net Wallet Impact.
  3. Section "2. The 'Tuesday-Morning Laziness' Variable Nobody Puts on the Box" analyzing real-world friction, consumables, or maintenance.
  4. Section "3. The Buyer's Math Verdict: Who Should Buy vs. Who Should Walk Away."
Output clean HTML paragraphs (<h2>, <h3>, <p>, <table>, <ul>) without <html> or <body> wrappers."""
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2200,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        except Exception as e:
            print(f"[AI] Anthropic call skipped ({e}), using built-in consumer math template.")

    esc = html_lib.escape
    return f"""
      <p style="font-size: 1.12rem; line-height: 1.75; color: #1e293b;">
        {esc(notes)} Every household has at least one recurring money debate where one camp swears spending upfront is reckless and the other camp swears weekly convenience markups are quietly draining the checking account, so we ran the unit economics down to the penny.
      </p>

      <h2 style="margin-top: 2rem; color: #0f172a;">1. The Head-to-Head Unit Math Scorecard</h2>
      <div style="overflow-x: auto; margin: 1.5rem 0;">
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden;">
          <thead>
            <tr style="background: #0f172a; color: #ffffff; text-align: left;">
              <th style="padding: 12px 14px;">Audit Metric</th>
              <th style="padding: 12px 14px;">{esc(sc['option_a'])}</th>
              <th style="padding: 12px 14px;">{esc(sc['option_b'])}</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom: 1px solid #e2e8f0; background: #ffffff;">
              <td style="padding: 12px 14px; font-weight: 700;">Real Cost Per Use</td>
              <td style="padding: 12px 14px; color: #16a34a; font-weight: 700;">{esc(sc['cost_per_use_a'])}</td>
              <td style="padding: 12px 14px; color: #dc2626; font-weight: 600;">{esc(sc['cost_per_use_b'])}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0; background: #f8fafc;">
              <td style="padding: 12px 14px; font-weight: 700;">Exact Break-Even Point</td>
              <td colspan="2" style="padding: 12px 14px; font-weight: 700; color: #1e40af;">{esc(sc['breakeven'])}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0; background: #ffffff;">
              <td style="padding: 12px 14px; font-weight: 700;">12-Month Net Wallet Impact</td>
              <td colspan="2" style="padding: 12px 14px; font-weight: 700; color: #15803d;">{esc(sc['yr1_savings'])}</td>
            </tr>
            <tr style="background: #f0fdf4;">
              <td style="padding: 12px 14px; font-weight: 800; color: #166534;">The Math Verdict</td>
              <td colspan="2" style="padding: 12px 14px; font-weight: 800; color: #166534;">{esc(sc['verdict'])}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 style="margin-top: 2rem; color: #0f172a;">2. The &ldquo;Tuesday-Morning Laziness&rdquo; Tax Nobody Puts on the Box</h2>
      <p style="line-height: 1.7; color: #334155;">
        A cost-per-use spreadsheet only works if you actually use what you bought. Investing upfront in better hardware or bulk refills yields a 0% return if the gear collects dust behind the toaster or bulk perishables spoil in the back of the fridge. Measure your own weekday-morning friction tolerance honestly before spending upfront.
      </p>

      <h2 style="margin-top: 2rem; color: #0f172a;">3. The Bottom-Line Verdict</h2>
      <p style="line-height: 1.7; color: #334155;">
        Once you pass the audited break-even mark ({esc(sc['breakeven'])}), every single use afterward acts like a tax-free dividend back into your checking account. Skip the overpriced luxury trim, stick to the proven workhorse tier, and stop paying the retail convenience tax.
      </p>
    """


def post_to_facebook_if_configured(topic_item, sc, article_full_url):
    page_id = os.environ.get("FB_PAGE_ID", "").strip()
    token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "").strip()
    if not page_id or not token:
        print("[FB-AUTOPOST] FB_PAGE_ID / FB_PAGE_ACCESS_TOKEN not set; skipping Facebook cross-post.")
        return
    caption = (
        f"🧮 WE DID THE MATH: {topic_item['headline']}\n\n"
        f"• {sc['option_a']}: {sc['cost_per_use_a']}\n"
        f"• {sc['option_b']}: {sc['cost_per_use_b']}\n"
        f"• Exact Break-Even Point: {sc['breakeven']}\n"
        f"• 12-Month Wallet Impact: {sc['yr1_savings']}\n\n"
        f"🏆 Verdict: {sc['verdict']}\n\n"
        f"Full unit-price math & breakdown in the first comment 👇"
    )
    try:
        feed_url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
        payload = urllib.parse.urlencode({"message": caption, "access_token": token}).encode("utf-8")
        req = urllib.request.Request(feed_url, data=payload, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
        post_id = res_data.get("id")
        print(f"[FB-AUTOPOST] Published native Facebook post: {post_id}")
        if post_id:
            c_url = f"https://graph.facebook.com/v21.0/{post_id}/comments"
            c_payload = urllib.parse.urlencode({"message": f"Full line-by-line math breakdown: {article_full_url}", "access_token": token}).encode("utf-8")
            c_req = urllib.request.Request(c_url, data=c_payload, method="POST")
            urllib.request.urlopen(c_req, timeout=15)
    except Exception as e:
        print(f"[FB-AUTOPOST] Non-fatal warning posting to Facebook: {e}")


def detect_existing_today_article(date_str):
    """Checks if an article was already published for today's UTC date and returns (filepath, headline) if found."""
    if not os.path.exists("articles"):
        return None, None
    prefix = f"{date_str}-"
    matches = sorted([fn for fn in os.listdir("articles") if fn.startswith(prefix) and fn.endswith(".html")])
    if not matches:
        return None, None
    fpath = os.path.join("articles", matches[0])
    try:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        m_h1 = re.search(r"<h1[^>]*>(.*?)</h1>", txt, flags=re.IGNORECASE | re.DOTALL)
        if m_h1:
            return fpath, html_lib.unescape(re.sub(r"<[^>]+>", "", m_h1.group(1)).strip())
    except Exception:
        pass
    return fpath, None


def main():
    if "--repair-only" in sys.argv:
        repair_cta_links_and_sync_scripts()
        return

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    env_custom = os.environ.get("CUSTOM_TOPIC", "").strip()
    existing_today_path, existing_today_headline = (None, None) if env_custom else detect_existing_today_article(date_str)

    # Check whether Facebook was already posted for today's URL to avoid duplicate social posts on re-runs
    already_posted_url = None
    if os.path.exists("daily_post_meta.json"):
        try:
            with open("daily_post_meta.json", "r", encoding="utf-8") as f:
                prev_meta = json.load(f)
                already_posted_url = prev_meta.get("url")
        except Exception:
            pass

    published_set = get_published_slugs_and_titles()
    topic_item = fetch_custom_topic(published_set, existing_today_headline=existing_today_headline)

    title = topic_item["headline"]
    if existing_today_path:
        article_rel_url = existing_today_path.replace("\\", "/")
    else:
        slug = slugify(title)
        article_rel_url = f"articles/{date_str}-{slug}.html"
    article_full_url = f"https://thebuyersmath.com/{article_rel_url}"

    inline_svg, sc, png_path, svg_path = generate_visual_scorecard(topic_item, article_full_url, date_str)
    body_html = generate_body_html(topic_item, sc)

    with open("daily_post_meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "headline": title,
            "category": topic_item["category"],
            "url": article_full_url,
            "scorecard": sc,
            "image_png": png_path if os.path.exists(png_path) else None,
            "image_svg": svg_path
        }, f, indent=2)

    esc = html_lib.escape
    p1_url = f"https://www.amazon.com/s?k={topic_item['product_query']}&tag={AMAZON_TAG}"
    p2_url = f"https://www.amazon.com/s?k={topic_item['runner_up_query']}&tag={AMAZON_TAG}"

    gear_box = f"""
      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; border-radius: 12px; padding: 1.5rem; margin: 1.75rem 0;">
        <div style="font-size: 0.75rem; font-weight: 800; color: #166534; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.65rem;">
          &#9733; The Buyer&#39;s Math Best-Value Hardware &amp; Deal Picks
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
          <div style="background: #ffffff; border: 1px solid #dcfce7; border-radius: 8px; padding: 1rem;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.25rem;">{esc(topic_item['product_name'])}</div>
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Benchmark Price: <strong>{esc(topic_item['product_price'])}</strong></div>
            <a href="{p1_url}" target="_blank" rel="sponsored nofollow noopener" style="display: inline-block; background: #16a34a; color: #ffffff; font-weight: 700; font-size: 0.85rem; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none;">Check Live Price &amp; Deals on Amazon &rarr;</a>
          </div>
          <div style="background: #ffffff; border: 1px solid #dcfce7; border-radius: 8px; padding: 1rem;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.25rem;">{esc(topic_item['runner_up_name'])}</div>
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Benchmark Price: <strong>{esc(topic_item['runner_up_price'])}</strong></div>
            <a href="{p2_url}" target="_blank" rel="sponsored nofollow noopener" style="display: inline-block; background: #0f172a; color: #ffffff; font-weight: 700; font-size: 0.85rem; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none;">Compare on Amazon &rarr;</a>
          </div>
        </div>
      </div>
    """

    desc_meta = esc(topic_item["notes"][:155])
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} | The Buyer&#39;s Math</title>
  <meta name="description" content="{desc_meta}">
  <meta property="og:title" content="{esc(title)} | The Buyer&#39;s Math">
  <meta property="og:description" content="{desc_meta}">
  <meta property="og:image" content="https://thebuyersmath.com/images/latest-scorecard.png">
  <link rel="stylesheet" href="/styles.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
  <script async src="https://www.anrdoezrs.net/am/{CJ_PID}/include/allCj/impressions/page/am.js"></script>
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="/index.html" class="site-logo">The Buyer&#39;s Math</a>
      <nav class="site-nav">
        <a href="/index.html">Daily Showdowns</a>
        <a href="/guides.html">All Audits</a>
        <a href="/index.html#calculators">24 Calculators</a>
        <a href="/privacy-policy.html">Privacy</a>
        <a href="/contact.html">Contact</a>
      </nav>
    </div>
  </header>
  <main class="container" style="max-width: 820px; margin: 2rem auto; padding: 0 1.5rem;">
    <article class="card" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 2.25rem;">
      <span style="background: #dbeafe; color: #1e40af; font-size: 0.75rem; font-weight: 800; padding: 0.25rem 0.6rem; border-radius: 4px; text-transform: uppercase;">{esc(topic_item['category'])}</span>
      <h1 style="font-size: 2.1rem; margin: 0.6rem 0; color: #0f172a; line-height: 1.25;">{esc(title)}</h1>
      <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem;">
        Published on {date_str} &bull; Anonymous Consumer Math Desk &bull; Zero-Sponsor Unit Audit
      </div>
      <div class="scorecard-hero" style="margin: 1.25rem 0;">
        {inline_svg}
      </div>
      {body_html}
      {gear_box}
    </article>
  </main>
  <footer class="site-footer">
    <div class="footer-nav">
      <a href="/index.html">Home &amp; Showdowns</a> |
      <a href="/guides.html">Guides Archive</a> |
      <a href="/privacy-policy.html">Privacy Policy</a> |
      <a href="/terms.html">Terms &amp; Disclaimer</a> |
      <a href="/contact.html">Contact Us</a>
    </div>
    <p class="footer-disclosure">
      <strong>Affiliate Disclosure:</strong> The Buyer&#39;s Math is a participant in the Amazon Services LLC Associates Program (Tag: {AMAZON_TAG}). As an Amazon Associate, I earn from qualifying purchases. Calculations and tool results are directional models for informational purposes only. Commission Junction Affiliate PID: {CJ_PID}.
    </p>
    <p class="footer-copy">&copy; 2026 The Buyer&#39;s Math. All rights reserved.</p>
  </footer>
</body>
</html>"""

    os.makedirs("articles", exist_ok=True)
    with open(article_rel_url, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[PUBLISHED] Wrote Everyday Consumer Math showdown with inline SVG scorecard: {article_rel_url}")

    summary_snippet = topic_item["notes"][:162] + ("..." if len(topic_item["notes"]) > 162 else "")
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            idx_content = f.read()

        slug_no_ext = os.path.basename(article_rel_url)[:-5]
        if slug_no_ext not in idx_content:
            new_card = f"""        <div class="calculator-grid" id="guides-grid" style="padding-bottom: 1rem;">
      <!-- Guide: {esc(title)} -->
      <a href="/{article_rel_url}" class="calc-card guide-card" data-guide-category="featured interior">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #166534; background: #dcfce7; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;">{esc(topic_item['category'])}</span>
            <span style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">{date_str}</span>
          </div>
          <h3 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; line-height: 1.4; color: #0f172a;">{esc(title)}</h3>
          <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0 0 1.25rem 0;">{esc(summary_snippet)}</p>
        </div>
        <span class="cta-link" style="color: #16a34a; font-weight: 700; font-size: 0.9rem;">See the Math Scorecard &rarr;</span>
      </a>"""
            grid_target = '<div class="calculator-grid" id="guides-grid" style="padding-bottom: 1rem;">'
            if grid_target in idx_content:
                idx_content = idx_content.replace(grid_target, new_card, 1)
                with open("index.html", "w", encoding="utf-8") as f:
                    f.write(idx_content)

    if os.path.exists("sitemap.xml"):
        with open("sitemap.xml", "r", encoding="utf-8") as f:
            sitemap_content = f.read()
        if article_full_url not in sitemap_content:
            sitemap_entry = f"""  <url>
    <loc>{article_full_url}</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
            sitemap_content = sitemap_content.replace("</urlset>", sitemap_entry)
            with open("sitemap.xml", "w", encoding="utf-8") as f:
                f.write(sitemap_content)

    repair_cta_links_and_sync_scripts()

    if article_full_url != already_posted_url:
        post_to_facebook_if_configured(topic_item, sc, article_full_url)


if __name__ == "__main__":
    main()
