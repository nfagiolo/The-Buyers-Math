#!/usr/bin/env python3
"""
generate_article.py — The Buyer's Math: Automated Anonymous "Everyday Consumer Math" Engine
Features:
  1. Custom Topic Injection (Priority #1: GitHub Actions custom_topic input -> Priority #2: Public Google Sheet CSV Queue -> Priority #3: topics_queue.txt -> Priority #4: Built-in Everyday Consumer Math Bank).
  2. Anonymous, Witty "We Did the Math" Editorial Voice (Humble, slightly humorous consumer advocate tone; zero dry textbook fluff).
  3. High-Converting Impulse Amazon Associates Integration (Tag: thebuyersmath-20).
  4. Automated Visual Scorecard Generator (Saves images/latest-scorecard.svg & .png + daily_post_meta.json for automatic Facebook/social posting).
  5. Self-Healing Homepage & CTA Repair (--repair-only mode supported): Fixes the 'Pool Pump Calc' keyword collision on Heat Pump / Water Heater / Mini-Split cards in both sync_guides.py and index.html, and refreshes stale Oct 31 ticker stamps.
"""

import os
import re
import sys
import csv
import io
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

AMAZON_TAG = "thebuyersmath-20"
ADSENSE_CLIENT = "ca-pub-1199906473460957"
CJ_PID = "101896838"
DEFAULT_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/15vl7kt-yD97aR5bbMUxsqEFdwGV20LqxJeXoTu8DKcU/export?format=csv"

CONSUMER_MATH_BANK = [
    {
        "category": "Kitchen & Coffee Math",
        "headline": "$500 Home Espresso Machine vs. $6.45 Drive-Thru Latte: The Exact Day You Break Even",
        "notes": "Compare a Breville Bambino Plus ($499) + burr grinder + specialty whole beans ($0.82 per 18g double shot) + whole milk ($0.35) = $1.17 per home latte vs. $6.45 at a coffee chain ($5.28 saved per cup). Break-even occurs on Latte #95 (3.1 months for a daily drinker).",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "Breville Bambino Plus Espresso Machine (BES500BSS)",
        "product_price": "$499.95",
        "product_query": "Breville+Bambino+Plus+Espresso+Machine",
        "runner_up_name": "Baratza Encore ESP Espresso Burr Grinder",
        "runner_up_price": "$199.95",
        "runner_up_query": "Baratza+Encore+ESP+Burr+Grinder",
        "scorecard": {
            "option_a": "Home Espresso Setup ($499)",
            "option_b": "Drive-Thru Latte ($6.45)",
            "cost_per_use_a": "$1.17 / cup (beans + milk)",
            "cost_per_use_b": "$6.45 / cup (with tax/tip)",
            "breakeven": "95 Lattes (Day 95)",
            "yr1_savings": "$1,428 Saved in Year 1",
            "verdict": "Home Espresso Wins After 14 Weeks"
        }
    },
    {
        "category": "Grocery & Warehouse Math",
        "headline": "Costco $65 Membership vs. Aldi: The 8 Staples That Pay for the Card (And 4 Where You Lose Money)",
        "notes": "Compare unit prices per ounce/sheet across Kirkland paper towels, $4.99 rotisserie chicken, organic extra-virgin olive oil, Kerrygold butter, and gas ($0.18/gal cheaper) against Aldi private-label prices and bulk spoilage waste.",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "OXO Good Grips 11-Pound Stainless Steel Food Scale with Pull-Out Display",
        "product_price": "$55.99",
        "product_query": "OXO+Good+Grips+11+Pound+Stainless+Steel+Food+Scale",
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
            "verdict": "Hybrid Strategy Wins (Never Buy Produce in Bulk)"
        }
    },
    {
        "category": "Household Consumables",
        "headline": "Dishwasher Pods vs. Liquid Gel vs. Loose Powder: Cost Per Load vs. Cleaning Chemistry",
        "notes": "Why $0.38 dissolvable pods dump 100% of their detergent into the main wash and leave your 15-minute pre-wash running on plain water, while $0.09 loose enzyme powder fills both the pre-wash cup and main wash cup for 76% less money.",
        "calc_url": "/water-heater-calculator.html",
        "calc_label": "Hot Water Calc",
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
            "verdict": "Loose Powder Wins on Both Chemistry & Math"
        }
    },
    {
        "category": "Kitchen & Energy Math",
        "headline": "Countertop Air Fryer vs. Full-Size Electric Oven: How Much Electricity You Actually Save Over 365 Dinners",
        "notes": "A 1,500W air fryer running 18 minutes uses 0.45 kWh ($0.08 at $0.172/kWh) with zero preheat, whereas a 3,500W electric oven takes 15 minutes to preheat plus 25 minutes to bake (1.95 kWh = $0.34) and dumps 6,600 BTUs of waste heat into your kitchen in summer.",
        "calc_url": "/hvac-roi-calculator.html",
        "calc_label": "Energy & HVAC Calc",
        "product_name": "Ninja Air Fryer Pro 4-in-1 with 5-QT Capacity (AF141)",
        "product_price": "$89.99",
        "product_query": "Ninja+Air+Fryer+Pro+AF141",
        "runner_up_name": "P3 P4400 Kill A Watt Electricity Usage Monitor",
        "runner_up_price": "$29.98",
        "runner_up_query": "Kill+A+Watt+Electricity+Usage+Monitor",
        "scorecard": {
            "option_a": "1,500W Countertop Air Fryer",
            "option_b": "3,500W Full-Size Electric Oven",
            "cost_per_use_a": "$0.08 / dinner (18 mins)",
            "cost_per_use_b": "$0.34 / dinner (40 mins w/ preheat)",
            "breakeven": "285 Uses (~11 Months)",
            "yr1_savings": "$95/yr Electric + $35 Summer AC Offset",
            "verdict": "Air Fryer Cuts Cooking kWh by 76%"
        }
    },
    {
        "category": "Grocery & Bulk Storage",
        "headline": "Vacuum Sealer + Bulk Meat Packs vs. Supermarket Foam Trays: The 12-Month Freezer Payback Math",
        "notes": "Buying family/sub-primal packs of chicken thighs, ground beef, and strip steaks saves $1.75 to $3.40 per pound over small supermarket trays. Factor in a $110 vacuum sealer and $0.20 per pre-cut quart bag to find the exact poundage where you break even.",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "NESCO Deluxe Food VS-12 Vacuum Sealer (130 Watts, Double Pump)",
        "product_price": "$109.99",
        "product_query": "Nesco+Deluxe+Food+VS-12+Vacuum+Sealer",
        "runner_up_name": "Wevac 8x12 Quart Pre-Cut Vacuum Sealer Bags (200 Count)",
        "runner_up_price": "$24.99",
        "runner_up_query": "Wevac+Quart+Vacuum+Sealer+Bags+200",
        "scorecard": {
            "option_a": "Bulk Pack + Vacuum Sealer ($110)",
            "option_b": "Standard Supermarket Trays",
            "cost_per_use_a": "$0.20/bag + $2.25/lb Meat Savings",
            "cost_per_use_b": "$0 Upfront + Freezer Burn Waste",
            "breakeven": "54 Pounds of Meat (~10 Weeks)",
            "yr1_savings": "$460/yr Saved for a 4-Person Kitchen",
            "verdict": "Pays for Itself on Your Third Warehouse Run"
        }
    },
    {
        "category": "Household Consumables",
        "headline": "Wool Dryer Balls vs. Disposable Bounce Sheets: 3-Year Cost & Towel Absorbency Math",
        "notes": "Compare a $15 6-pack of organic New Zealand wool dryer balls (lasts 1,000+ loads = $0.015/load) that physically separate wet laundry to cut drying time by 12% vs. $0.08 disposable chemical sheets that coat moisture sensors and reduce bath towel absorbency.",
        "calc_url": "/hvac-roi-calculator.html",
        "calc_label": "Energy ROI Calc",
        "product_name": "Friendsheep Organic Eco Wool Dryer Balls (XL 6-Pack, 100% New Zealand Wool)",
        "product_price": "$14.95",
        "product_query": "Friendsheep+Organic+Eco+Wool+Dryer+Balls+6+Pack",
        "runner_up_name": "Holikme Dryer Vent Cleaner Kit Vacuum Hose Attachment & Brush",
        "runner_up_price": "$9.99",
        "runner_up_query": "Holikme+Dryer+Vent+Cleaner+Kit",
        "scorecard": {
            "option_a": "6-Pack XL Wool Dryer Balls ($15)",
            "option_b": "Disposable Dryer Sheets ($0.08/sheet)",
            "cost_per_use_a": "$0.015 / load + 12% Less Dryer kWh",
            "cost_per_use_b": "$0.16 / load (2 sheets) + Sensor Residue",
            "breakeven": "62 Laundry Loads (~2.5 Months)",
            "yr1_savings": "$58/yr (Sheets + Electric Dryer Time)",
            "verdict": "Wool Balls Win in Under 70 Loads"
        }
    },
    {
        "category": "Beverage & Kitchen Math",
        "headline": "SodaStream + 5-Lb CO2 Tank Adapter vs. 12-Packs of Canned Sparkling Water: The Real Cost Per Liter",
        "notes": "Canned sparkling water (LaCroix/Waterloo) now averages $6.49 per 12-pack ($1.52/liter). Compare standard $16.99 proprietary 60L CO2 cylinder swaps ($0.28/liter) against connecting a $32 brass hose adapter to a 5-lb local beverage CO2 tank ($22 refill = $0.06/liter).",
        "calc_url": "/kitchen-remodel-calculator.html",
        "calc_label": "Kitchen Math Calc",
        "product_name": "SodaStream Terra Sparkling Water Maker Bundle",
        "product_price": "$89.99",
        "product_query": "SodaStream+Terra+Sparkling+Water+Maker",
        "runner_up_name": "60-Inch CGA320 to Quick-Connect CO2 Tank Adapter Hose",
        "runner_up_price": "$31.99",
        "runner_up_query": "SodaStream+CGA320+CO2+Tank+Adapter+Hose",
        "scorecard": {
            "option_a": "SodaStream + Tank Adapter",
            "option_b": "12-Packs Canned Seltzer ($6.49)",
            "cost_per_use_a": "$0.28/L (Stock) or $0.06/L (5-lb Tank)",
            "cost_per_use_b": "$1.52 / liter (2.8 cans)",
            "breakeven": "73 Liters (~18 Twelve-Packs)",
            "yr1_savings": "$440/yr for a 2-Can-a-Day Household",
            "verdict": "SodaStream Breaks Even in 9 Weeks"
        }
    },
    {
        "category": "Auto & Ownership Math",
        "headline": "Keep Fixing a Paid-Off 120k-Mile Car ($1,800/yr Repairs) vs. Buying a $32,000 New Hybrid: 5-Year Wealth Math",
        "notes": "Nothing panics a car owner like a $1,400 mechanic invoice on a car worth $7,000. Compare putting $150/month into a repair fund against taking on a $610/month car note, $95/month higher full-coverage insurance, and $3,600/year depreciation.",
        "calc_url": "/ev-charger-calculator.html",
        "calc_label": "EV & Fuel Calc",
        "product_name": "ANCEL AD310 Classic Enhanced Universal OBD II Scanner Car Engine Fault Code Reader",
        "product_price": "$24.99",
        "product_query": "ANCEL+AD310+OBD+II+Scanner",
        "runner_up_name": "NOCO Boost Plus GB40 1000A UltraSafe Car Battery Jump Starter",
        "runner_up_price": "$99.95",
        "runner_up_query": "NOCO+Boost+Plus+GB40+Jump+Starter",
        "scorecard": {
            "option_a": "Keep Paid-Off Car ($1,800/yr Repairs)",
            "option_b": "Buy $32k New Hybrid ($610/mo Note)",
            "cost_per_use_a": "$3,950/yr Total (Repairs + Gas + Ins.)",
            "cost_per_use_b": "$8,420/yr Total (Depr. + Interest + Gas + Ins.)",
            "breakeven": "Gas Savings Alone Take 14.2 Years",
            "yr1_savings": "$4,470/yr Kept in Your Bank Account",
            "verdict": "A $1,800 Repair Bill Is Still 78% Cheaper Than a Car Note"
        }
    }
]


def slugify(text):
    s = re.sub(r"[^a-zA-Z0-9\s-]", "", text.lower())
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    return s[:72].rstrip("-")


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
        if len(item) < 500 and (slug in item or item in slug):
            return True
        if len(item) >= 500 and headline.lower() in item:
            return True
    return False


def match_calculator_for_title(title_text):
    """Accurately maps an article title to its exact calculator without 'pump' colliding on Pool Pump."""
    t = title_text.lower()
    if any(k in t for k in ["water heater", "voltex", "tankless", "rheem", "bradford"]):
        return "/water-heater-calculator.html", "Water Heater Calc"
    if any(k in t for k in ["mini-split", "mini split", "mrcool", "ductless"]):
        return "/mini-split-calculator.html", "Mini-Split Calc"
    if any(k in t for k in ["heat pump", "hyper-heat", "bosch ids", "ecobee", "thermostat", "furnace", "hvac"]):
        return "/hvac-roi-calculator.html", "Heat Pump Calc"
    if any(k in t for k in ["pool pump", "intelliflo", "intellichlor", "mastertemp", "raypak", "pool heater", "salt chlorine"]):
        return "/pool.html", "Pool Pump Calc"
    if any(k in t for k in ["radiant", "nuheat", "ditra"]):
        return "/radiant-floor-calculator.html", "Radiant Floor Calc"
    if any(k in t for k in ["generator", "transfer switch", "rxsw", "kohler", "generac", "powerwall"]):
        return "/generator-calculator.html", "Generator Calc"
    if any(k in t for k in ["panel", "200a", "breaker", "subpanel"]):
        return "/electrical-panel-calculator.html", "Electrical Panel Calc"
    if any(k in t for k in ["ev ", "charger", "emporia", "wall connector"]):
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
    if any(k in t for k in ["floor", "lvp", "hardwood"]):
        return "/flooring-calculator.html", "Flooring Calc"
    if any(k in t for k in ["roof", "shingle"]):
        return "/roofing-cost-calculator.html", "Roofing Calc"
    return "/kitchen-remodel-calculator.html", "Kitchen Math Calc"


def repair_cta_links_and_sync_scripts():
    """
    Fixes the Mechanical & Energy 'Pool Pump Calc' CTA misrouting across sync_guides.py and index.html,
    and refreshes stale Oct 31 header/pulse date stamps on index.html.
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

    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        orig_html = html

        # Refresh stale Oct 31 Commodity Index & Living Authority Hub date stamps
        html = re.sub(r"Oct 31(\s+Commodity Index:)", f"{short_date}\\1", html)
        html = re.sub(r"(Living Authority Hub\s*(?:&bull;|•)\s*Updated\s*)Oct 31,\s*2026", f"\\g<1>{long_date}", html)

        # Split around every Pool Pump Calc anchor and inspect its preceding card context
        anchor_pattern = r'(<a\b[^>]*href=["\']/?pool\.html["\'][^>]*>[^<]*Pool Pump Calc[^<]*</a>)'
        chunks = re.split(anchor_pattern, html, flags=re.IGNORECASE)
        for i in range(1, len(chunks), 2):
            # Only inspect the closest heading/card text immediately preceding this specific anchor
            window = chunks[i - 1][-420:]
            last_close = max(window.rfind("</a>"), window.rfind("</article>"), window.rfind("</section>"))
            local_ctx = (window[last_close:] if last_close != -1 else window).lower()
            anchor = chunks[i]

            if any(p in local_ctx for p in ["intelliflo", "pool pump", "pool heater", "mastertemp", "raypak", "intellichlor", "salt chlorine"]):
                continue
            if any(w in local_ctx for w in ["water heater", "voltex", "tankless", "rheem"]):
                anchor = re.sub(r'href=["\']/?pool\.html["\']', 'href="/water-heater-calculator.html"', anchor)
                anchor = anchor.replace("Open Pool Pump Calc", "Open Water Heater Calc").replace("Pool Pump Calc", "Water Heater Calc")
            elif any(m in local_ctx for m in ["mini-split", "mini split", "mrcool", "ductless"]):
                anchor = re.sub(r'href=["\']/?pool\.html["\']', 'href="/mini-split-calculator.html"', anchor)
                anchor = anchor.replace("Open Pool Pump Calc", "Open Mini-Split Calc").replace("Pool Pump Calc", "Mini-Split Calc")
            elif any(h in local_ctx for h in ["heat pump", "hyper-heat", "bosch ids", "ecobee", "thermostat", "furnace"]):
                anchor = re.sub(r'href=["\']/?pool\.html["\']', 'href="/hvac-roi-calculator.html"', anchor)
                anchor = anchor.replace("Open Pool Pump Calc", "Open Heat Pump Calc").replace("Pool Pump Calc", "Heat Pump Calc")
            chunks[i] = anchor
        html = "".join(chunks)

        if html != orig_html:
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("[REPAIR] Repaired misrouted 'Pool Pump Calc' CTAs and refreshed ticker dates in index.html.")


def fetch_custom_topic(published_set):
    env_topic = os.environ.get("CUSTOM_TOPIC", "").strip()
    if env_topic:
        print(f"[QUEUE] Using explicit CUSTOM_TOPIC override: {env_topic}")
        c_url, c_lbl = match_calculator_for_title(env_topic)
        return {
            "category": "Everyday Consumer Math",
            "headline": env_topic,
            "notes": f"Run a rigorous, witty consumer cost-per-use and break-even math breakdown on: {env_topic}.",
            "calc_url": c_url,
            "calc_label": c_lbl,
            "product_name": f"Top-Rated Value Pick: {env_topic[:42]}",
            "product_price": "Check Current Deal",
            "product_query": urllib.parse.quote_plus(env_topic[:40]),
            "runner_up_name": "Kill A Watt Electricity & Appliance Cost Monitor",
            "runner_up_price": "$29.98",
            "runner_up_query": "Kill+A+Watt+Electricity+Monitor",
            "scorecard": None
        }

    csv_url = os.environ.get("TOPIC_QUEUE_CSV_URL", DEFAULT_SHEET_CSV_URL).strip()
    if csv_url:
        try:
            req = urllib.request.Request(csv_url, headers={"User-Agent": "TheBuyersMath-Bot/2.2"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                csv_text = resp.read().decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                status = (row.get("Status") or "Queued").strip().lower()
                headline = (row.get("TopicHeadline") or row.get("Topic / Idea") or "").strip()
                if not headline or status in ("published", "done", "skip"):
                    continue
                if not is_already_published(headline, published_set):
                    print(f"[QUEUE] Pulled next unposted topic from Google Sheet Queue: {headline}")
                    matched_bank = next((b for b in CONSUMER_MATH_BANK if slugify(b["headline"])[:24] in slugify(headline)), None)
                    if matched_bank:
                        return matched_bank
                    query_str = (row.get("TargetAmazonProduct_SearchQuery") or headline[:35]).strip().replace(" ", "+")
                    c_url, c_lbl = match_calculator_for_title(headline)
                    return {
                        "category": (row.get("Category") or "Everyday Consumer Math").strip(),
                        "headline": headline,
                        "notes": (row.get("MathAngle_Notes") or f"Break down upfront cost, cost per use, hidden traps, and exact break-even timeline for {headline}.").strip(),
                        "calc_url": c_url,
                        "calc_label": c_lbl,
                        "product_name": f"Best-Value Pick for {headline[:40]}",
                        "product_price": "Check Current Price",
                        "product_query": query_str,
                        "runner_up_name": "Runner-Up Comparison Alternative",
                        "runner_up_price": "Check Current Price",
                        "runner_up_query": query_str,
                        "scorecard": None
                    }
        except Exception as e:
            print(f"[QUEUE] Google Sheet CSV check skipped ({e}); checking fallback bank.")

    for item in CONSUMER_MATH_BANK:
        if not is_already_published(item["headline"], published_set):
            print(f"[AUTOPILOT] Selected next unposted showdown from built-in bank: {item['headline']}")
            return item

    return CONSUMER_MATH_BANK[datetime.now(timezone.utc).timetuple().tm_yday % len(CONSUMER_MATH_BANK)]


def generate_visual_scorecard(topic_item, article_url, date_str):
    os.makedirs("images", exist_ok=True)
    sc = topic_item.get("scorecard") or {
        "option_a": "Option A (Upfront Investment)",
        "option_b": "Option B (Recurring Habit)",
        "cost_per_use_a": "Lower Cost Per Use",
        "cost_per_use_b": "Higher Recurring Cost",
        "breakeven": "See Full Break-Even Table",
        "yr1_savings": "Audited 12-Month Delta",
        "verdict": "See The Buyer's Math Verdict"
    }
    headline = topic_item["headline"]
    line1 = headline[:52] + ("..." if len(headline) > 52 else "")
    line2 = headline[52:104] if len(headline) > 52 else ""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#0f172a"/>
  <rect x="36" y="36" width="1128" height="558" rx="18" fill="#1e293b" stroke="#334155" stroke-width="2"/>
  <rect x="68" y="68" width="290" height="36" rx="6" fill="#2563eb"/>
  <text x="84" y="92" fill="#ffffff" font-family="system-ui, -apple-system, sans-serif" font-size="16" font-weight="800" letter-spacing="1">THE BUYER'S MATH • SCORECARD</text>
  <text x="1120" y="92" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="16" font-weight="600" text-anchor="end">{date_str}</text>
  <text x="68" y="152" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="30" font-weight="800">{line1.replace("&", "&amp;")}</text>
  <text x="68" y="190" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="24" font-weight="700">{line2.replace("&", "&amp;")}</text>
  <rect x="68" y="220" width="510" height="230" rx="12" fill="#0f172a" stroke="#16a34a" stroke-width="2"/>
  <text x="92" y="258" fill="#4ade80" font-family="system-ui, sans-serif" font-size="15" font-weight="800">CONTENDER A</text>
  <text x="92" y="295" fill="#ffffff" font-family="system-ui, sans-serif" font-size="24" font-weight="800">{sc['option_a'].replace("&", "&amp;")[:34]}</text>
  <text x="92" y="345" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="16">Real Cost Per Use:</text>
  <text x="92" y="375" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="22" font-weight="700">{sc['cost_per_use_a'].replace("&", "&amp;")[:36]}</text>
  <text x="92" y="422" fill="#4ade80" font-family="system-ui, sans-serif" font-size="18" font-weight="700">Break-Even: {sc['breakeven'].replace("&", "&amp;")[:32]}</text>
  <rect x="610" y="220" width="510" height="230" rx="12" fill="#0f172a" stroke="#475569" stroke-width="2"/>
  <text x="634" y="258" fill="#f87171" font-family="system-ui, sans-serif" font-size="15" font-weight="800">CONTENDER B</text>
  <text x="634" y="295" fill="#ffffff" font-family="system-ui, sans-serif" font-size="24" font-weight="800">{sc['option_b'].replace("&", "&amp;")[:34]}</text>
  <text x="634" y="345" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="16">Real Cost Per Use:</text>
  <text x="634" y="375" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="22" font-weight="700">{sc['cost_per_use_b'].replace("&", "&amp;")[:36]}</text>
  <text x="634" y="422" fill="#fbbf24" font-family="system-ui, sans-serif" font-size="18" font-weight="700">12-Mo Impact: {sc['yr1_savings'].replace("&", "&amp;")[:30]}</text>
  <rect x="68" y="476" width="1052" height="84" rx="12" fill="#16a34a"/>
  <text x="96" y="512" fill="#dcfce7" font-family="system-ui, sans-serif" font-size="14" font-weight="800" letter-spacing="1">THE MATH VERDICT</text>
  <text x="96" y="542" fill="#ffffff" font-family="system-ui, sans-serif" font-size="24" font-weight="800">{sc['verdict'].replace("&", "&amp;")[:56]}</text>
  <text x="1096" y="532" fill="#ffffff" font-family="system-ui, sans-serif" font-size="18" font-weight="700" text-anchor="end">thebuyersmath.com</text>
</svg>"""

    svg_path = os.path.join("images", "latest-scorecard.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    png_path = os.path.join("images", "latest-scorecard.png")
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (1200, 630), color=(15, 23, 42))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([36, 36, 1164, 594], radius=18, fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        draw.rounded_rectangle([68, 68, 360, 104], radius=6, fill=(37, 99, 235))
        draw.text((84, 78), "THE BUYER'S MATH • SCORECARD", fill=(255, 255, 255))
        draw.text((68, 130), line1, fill=(248, 250, 252))
        if line2:
            draw.text((68, 165), line2, fill=(203, 213, 225))
        draw.rounded_rectangle([68, 220, 578, 450], radius=12, fill=(15, 23, 42), outline=(22, 163, 74), width=2)
        draw.text((92, 245), f"OPTION A: {sc['option_a']}", fill=(74, 222, 128))
        draw.text((92, 300), f"Cost Per Use: {sc['cost_per_use_a']}", fill=(248, 250, 252))
        draw.text((92, 355), f"Break-Even: {sc['breakeven']}", fill=(74, 222, 128))
        draw.rounded_rectangle([610, 220, 1120, 450], radius=12, fill=(15, 23, 42), outline=(71, 85, 105), width=2)
        draw.text((634, 245), f"OPTION B: {sc['option_b']}", fill=(248, 113, 113))
        draw.text((634, 300), f"Cost Per Use: {sc['cost_per_use_b']}", fill=(248, 250, 252))
        draw.text((634, 355), f"1-Yr Delta: {sc['yr1_savings']}", fill=(251, 191, 36))
        draw.rounded_rectangle([68, 476, 1120, 560], radius=12, fill=(22, 163, 74))
        draw.text((96, 508), f"VERDICT: {sc['verdict']}  |  thebuyersmath.com", fill=(255, 255, 255))
        img.save(png_path, "PNG")
    except Exception as e:
        print(f"[SCORECARD] Pillow PNG fallback skipped ({e}); SVG saved.")

    with open("daily_post_meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "headline": headline,
            "category": topic_item["category"],
            "url": article_url,
            "scorecard": sc,
            "image_png": png_path if os.path.exists(png_path) else None,
            "image_svg": svg_path
        }, f, indent=2)


def generate_body_html(topic_item):
    headline = topic_item["headline"]
    notes = topic_item["notes"]
    sc = topic_item.get("scorecard") or {
        "option_a": "Option A (Upfront Purchase)",
        "option_b": "Option B (Pay-Per-Use Habit)",
        "cost_per_use_a": "Lower unit cost after payback",
        "cost_per_use_b": "High recurring retail markup",
        "breakeven": "Under 90 Days of Normal Use",
        "yr1_savings": "$250–$600+ Annual Savings",
        "verdict": "Option A Wins Once You Pass the Break-Even Threshold"
    }

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""Write an engaging, witty, anonymous consumer math showdown article for 'The Buyer's Math' titled:
"{headline}"

Context & Numbers to Include:
{notes}

Style Rules:
- Write in a sharp, humble, slightly self-deprecating, humorous consumer-advocate voice ("We ran the spreadsheet so you don't get fleeced").
- Zero generic AI throat-clearing, zero em-dashes, and zero dry textbook language.
- Include:
  1. An opening hook about why everyone argues about this purchase (begin with a concrete dollar comparison in the very first sentence so homepage excerpts grab readers immediately).
  2. A clean HTML comparison table (<table style="width:100%;border-collapse:collapse;margin:1.5rem 0;">) comparing Upfront Cost, Real Cost Per Use, The Hidden Catch, Break-Even Timeline, and 1-Year Net Impact.
  3. "The Sneaky Hidden Variable Nobody Counts" (energy, waste, consumables, or Tuesday-morning human laziness).
  4. "The Buyer's Math Verdict: When to Buy vs. When to Walk Away."
Output clean HTML paragraphs (<h2>, <h3>, <p>, <table>, <ul>) without <html> or <body> wrappers."""
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2200,
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        except Exception as e:
            print(f"[AI] Anthropic call skipped ({e}), using built-in consumer math template.")

    return f"""
      <p style="font-size: 1.12rem; line-height: 1.75; color: #1e293b;">
        {notes} Every household has at least one recurring money debate where one person swears spending upfront is reckless and the other swears weekly retail convenience markups are bleeding the checking account dry, so we ran the unit economics line by line.
      </p>

      <h2 style="margin-top: 2rem; color: #0f172a;">1. The Head-to-Head Unit Math Scorecard</h2>
      <div style="overflow-x: auto; margin: 1.5rem 0;">
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden;">
          <thead>
            <tr style="background: #0f172a; color: #ffffff; text-align: left;">
              <th style="padding: 12px 14px;">Metric</th>
              <th style="padding: 12px 14px;">{sc['option_a']}</th>
              <th style="padding: 12px 14px;">{sc['option_b']}</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom: 1px solid #e2e8f0; background: #ffffff;">
              <td style="padding: 12px 14px; font-weight: 700;">Real Cost Per Use</td>
              <td style="padding: 12px 14px; color: #16a34a; font-weight: 700;">{sc['cost_per_use_a']}</td>
              <td style="padding: 12px 14px; color: #dc2626; font-weight: 600;">{sc['cost_per_use_b']}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0; background: #f8fafc;">
              <td style="padding: 12px 14px; font-weight: 700;">Exact Break-Even Point</td>
              <td colspan="2" style="padding: 12px 14px; font-weight: 700; color: #1e40af;">{sc['breakeven']}</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0; background: #ffffff;">
              <td style="padding: 12px 14px; font-weight: 700;">12-Month Net Wallet Impact</td>
              <td colspan="2" style="padding: 12px 14px; font-weight: 700; color: #15803d;">{sc['yr1_savings']}</td>
            </tr>
            <tr style="background: #f0fdf4;">
              <td style="padding: 12px 14px; font-weight: 800; color: #166534;">The Math Verdict</td>
              <td colspan="2" style="padding: 12px 14px; font-weight: 800; color: #166534;">{sc['verdict']}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 style="margin-top: 2rem; color: #0f172a;">2. The "Human Laziness" Tax Nobody Puts in the Brochure</h2>
      <p style="line-height: 1.7; color: #334155;">
        A cost-per-use spreadsheet only works if you actually use what you bought. Investing in better gear or bulk packs yields a 0% return if the machine gathers dust behind the toaster or the bulk pack expires in the pantry. Be honest about your own Tuesday-morning friction tolerance before spending upfront.
      </p>

      <h2 style="margin-top: 2rem; color: #0f172a;">3. The Bottom-Line Verdict</h2>
      <p style="line-height: 1.7; color: #334155;">
        Once you cross the break-even threshold ({sc['breakeven']}), every single use afterward is a tax-free dividend back into your bank account. Skip the gimmicky middle tier, grab the workhorse model when seasonal deals hit, and stop paying the convenience tax.
      </p>
    """


def post_to_facebook_if_configured(topic_item, article_full_url):
    page_id = os.environ.get("FB_PAGE_ID", "").strip()
    token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "").strip()
    if not page_id or not token:
        print("[FB-AUTOPOST] FB_PAGE_ID / FB_PAGE_ACCESS_TOKEN not set; skipping Facebook cross-post.")
        return
    sc = topic_item.get("scorecard") or {}
    caption = (
        f"🧮 WE DID THE MATH: {topic_item['headline']}\n\n"
        f"• Option A ({sc.get('option_a', 'Upfront Option')}): {sc.get('cost_per_use_a', 'See table')}\n"
        f"• Option B ({sc.get('option_b', 'Recurring Habit')}): {sc.get('cost_per_use_b', 'See table')}\n"
        f"• Exact Break-Even Point: {sc.get('breakeven', 'See full breakdown')}\n"
        f"• 12-Month Wallet Impact: {sc.get('yr1_savings', 'Audited 1-yr savings')}\n\n"
        f"🏆 Verdict: {sc.get('verdict', 'Read full breakdown')}\n\n"
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


def main():
    if "--repair-only" in sys.argv:
        repair_cta_links_and_sync_scripts()
        return

    repair_cta_links_and_sync_scripts()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    published_set = get_published_slugs_and_titles()
    topic_item = fetch_custom_topic(published_set)

    title = topic_item["headline"]
    slug = slugify(title)
    article_rel_url = f"articles/{date_str}-{slug}.html"
    article_full_url = f"https://thebuyersmath.com/{article_rel_url}"

    body_html = generate_body_html(topic_item)
    generate_visual_scorecard(topic_item, article_full_url, date_str)

    p1_url = f"https://www.amazon.com/s?k={topic_item['product_query']}&tag={AMAZON_TAG}"
    p2_url = f"https://www.amazon.com/s?k={topic_item['runner_up_query']}&tag={AMAZON_TAG}"

    gear_box = f"""
      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; border-radius: 12px; padding: 1.5rem; margin: 1.75rem 0;">
        <div style="font-size: 0.75rem; font-weight: 800; color: #166534; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
          ★ The Buyer's Math Best-Value Hardware &amp; Deal Picks
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
          <div style="background: #ffffff; border: 1px solid #dcfce7; border-radius: 8px; padding: 1rem;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.25rem;">{topic_item['product_name']}</div>
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Benchmark Price: <strong>{topic_item['product_price']}</strong></div>
            <a href="{p1_url}" target="_blank" rel="sponsored nofollow noopener" style="display: inline-block; background: #16a34a; color: #ffffff; font-weight: 700; font-size: 0.85rem; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none;">Check Live Price &amp; Deals on Amazon &rarr;</a>
          </div>
          <div style="background: #ffffff; border: 1px solid #dcfce7; border-radius: 8px; padding: 1rem;">
            <div style="font-weight: 700; color: #0f172a; margin-bottom: 0.25rem;">{topic_item['runner_up_name']}</div>
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem;">Benchmark Price: <strong>{topic_item['runner_up_price']}</strong></div>
            <a href="{p2_url}" target="_blank" rel="sponsored nofollow noopener" style="display: inline-block; background: #0f172a; color: #ffffff; font-weight: 700; font-size: 0.85rem; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none;">Compare on Amazon &rarr;</a>
          </div>
        </div>
      </div>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | The Buyer's Math</title>
  <meta name="description" content="{topic_item['notes'][:155]}">
  <meta property="og:title" content="{title} | The Buyer's Math">
  <meta property="og:description" content="{topic_item['notes'][:155]}">
  <meta property="og:image" content="https://thebuyersmath.com/images/latest-scorecard.png">
  <link rel="stylesheet" href="../styles.css">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
  <script async src="https://www.anrdoezrs.net/am/{CJ_PID}/include/allCj/impressions/page/am.js"></script>
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="../index.html" class="site-logo">The Buyer's Math</a>
      <nav class="site-nav">
        <a href="../index.html">Daily Showdowns</a>
        <a href="../guides.html">All Audits</a>
        <a href="../index.html#calculators">24 Calculators</a>
        <a href="../privacy-policy.html">Privacy</a>
        <a href="../contact.html">Contact</a>
      </nav>
    </div>
  </header>
  <main class="container" style="max-width: 820px; margin: 2rem auto; padding: 0 1.5rem;">
    <article class="card" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 2.25rem;">
      <span style="background: #dbeafe; color: #1e40af; font-size: 0.75rem; font-weight: 800; padding: 0.25rem 0.6rem; border-radius: 4px; text-transform: uppercase;">{topic_item['category']}</span>
      <h1 style="font-size: 2.1rem; margin: 0.6rem 0; color: #0f172a; line-height: 1.25;">{title}</h1>
      <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem;">
        Published on {date_str} &bull; Anonymous Consumer Math Desk &bull; Zero-Sponsor Unit Audit
      </div>
      <div style="margin: 1.25rem 0;">
        <img src="../images/latest-scorecard.svg" alt="{title} Scorecard" style="width: 100%; height: auto; border-radius: 10px; border: 1px solid #cbd5e1;">
      </div>
      {body_html}
      {gear_box}
    </article>
  </main>
  <footer class="site-footer">
    <div class="footer-nav">
      <a href="../index.html">Home &amp; Showdowns</a> |
      <a href="../guides.html">Guides Archive</a> |
      <a href="../privacy-policy.html">Privacy Policy</a> |
      <a href="../terms.html">Terms &amp; Disclaimer</a> |
      <a href="../contact.html">Contact Us</a>
    </div>
    <p class="footer-disclosure">
      <strong>Affiliate Disclosure:</strong> The Buyer's Math is a participant in the Amazon Services LLC Associates Program (Tag: {AMAZON_TAG}). As an Amazon Associate, I earn from qualifying purchases. Calculations and tool results are directional models for informational purposes only. Commission Junction Affiliate PID: {CJ_PID}.
    </p>
    <p class="footer-copy">&copy; 2026 The Buyer's Math. All rights reserved.</p>
  </footer>
</body>
</html>"""

    os.makedirs("articles", exist_ok=True)
    with open(article_rel_url, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"[PUBLISHED] Created Everyday Consumer Math showdown: {article_rel_url}")

    summary_snippet = topic_item["notes"][:165] + ("..." if len(topic_item["notes"]) > 165 else "")
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            idx_content = f.read()

        if article_rel_url not in idx_content:
            new_card = f"""        <div class="calculator-grid" id="guides-grid" style="padding-bottom: 1rem;">
      <!-- Guide: {title} -->
      <a href="/{article_rel_url}" class="calc-card guide-card" data-guide-category="featured interior">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #166534; background: #dcfce7; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;">{topic_item['category']}</span>
            <span style="font-size: 0.8rem; color: #94a3b8; font-weight: 500;">{date_str}</span>
          </div>
          <h3 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; line-height: 1.4; color: #0f172a;">{title}</h3>
          <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0 0 1.25rem 0;">{summary_snippet}</p>
        </div>
        <span class="cta-link" style="color: #16a34a; font-weight: 700; font-size: 0.9rem;">See the Math Scorecard &rarr;</span>
      </a>"""
            grid_target = '<div class="calculator-grid" id="guides-grid" style="padding-bottom: 1rem;">'
            if grid_target in idx_content:
                idx_content = idx_content.replace(grid_target, new_card, 1)
                with open("index.html", "w", encoding="utf-8") as f:
                    f.write(idx_content)

    if os.path.exists("guides.html"):
        with open("guides.html", "r", encoding="utf-8") as f:
            guides_content = f.read()
        if article_rel_url not in guides_content:
            guide_card_entry = f"""    <div class="guides-grid" id="guides-grid">
      <!-- Guide: {title} -->
      <article class="guide-card" data-category="interior">
        <div class="guide-card-header">
          <span class="guide-badge">{topic_item['category']}</span>
          <span class="guide-date">{date_str}</span>
        </div>
        <h2 class="guide-title"><a href="/{article_rel_url}">{title}</a></h2>
        <p class="guide-desc">{summary_snippet}</p>
        <a href="/{article_rel_url}" class="guide-read-link">See the Math Scorecard &rarr;</a>
      </article>"""
            if '<div class="guides-grid" id="guides-grid">' in guides_content:
                guides_content = guides_content.replace('<div class="guides-grid" id="guides-grid">', guide_card_entry, 1)
                with open("guides.html", "w", encoding="utf-8") as f:
                    f.write(guides_content)

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

    post_to_facebook_if_configured(topic_item, article_full_url)


if __name__ == "__main__":
    main()
