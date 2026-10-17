#!/usr/bin/env python3
"""
generate_article.py - Daily Empirical Cost Guide Generator for The Buyer's Math
 Enhancements:
 1. Strips raw Markdown `# ` prefixes and quotes from Claude title output.
 2. Generates a unique, article-specific <meta name="description"> from the opening analysis paragraph instead of repeating generic boilerplate.
 3. Positions the interactive Companion Calculator CTA box immediately after the executive summary to maximize calculator & Angi lead conversions.
"""

import os
import re
import random
import datetime
import requests

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_NAME = "claude-3-5-sonnet-20241022"
CJ_ANGI_LINK = "https://www.jdoqocy.com/click-101896838-17142784"
AMAZON_TAG = "nfagiolo-20"

CALCULATORS = [
    {"id": "roofing", "name": "Roof Replacement Cost Estimator", "url": "/roofing-cost-calculator.html", "category": "Building Envelope"},
    {"id": "hvac", "name": "Heat Pump vs. Gas Furnace ROI Calculator", "url": "/hvac-roi-calculator.html", "category": "Mechanical & Energy"},
    {"id": "kitchen", "name": "Kitchen Remodel Cost Estimator", "url": "/kitchen-remodel-calculator.html", "category": "Interior & Power"},
    {"id": "bathroom", "name": "Bathroom Remodel Cost Estimator", "url": "/bathroom-remodel-calculator.html", "category": "Interior & Power"},
    {"id": "siding", "name": "Home Siding Replacement Calculator", "url": "/siding-cost-calculator.html", "category": "Building Envelope"},
    {"id": "windows", "name": "Window Replacement Cost Estimator", "url": "/window-replacement-estimator.html", "category": "Building Envelope"},
    {"id": "solar", "name": "Solar Panel Payback Calculator", "url": "/solar-payback-calculator.html", "category": "Mechanical & Energy"},
    {"id": "water-heater", "name": "Water Heater Replacement Calculator", "url": "/water-heater-calculator.html", "category": "Mechanical & Energy"},
    {"id": "generator", "name": "Backup Generator Sizing Calculator", "url": "/generator-calculator.html", "category": "Interior & Power"},
    {"id": "ev-charger", "name": "EV Home Charger Installation Calculator", "url": "/ev-charger-calculator.html", "category": "Interior & Power"},
    {"id": "mini-split", "name": "Ductless Mini-Split Cost Estimator", "url": "/mini-split-calculator.html", "category": "Mechanical & Energy"},
    {"id": "insulation", "name": "Attic Insulation & Air Sealing Calculator", "url": "/attic-insulation-calculator.html", "category": "Mechanical & Energy"},
    {"id": "basement", "name": "Basement Finishing Cost Estimator", "url": "/basement-cost-calculator.html", "category": "Interior & Power"},
    {"id": "driveway", "name": "Driveway Paving Calculator", "url": "/driveway-paving-calculator.html", "category": "Building Envelope"},
    {"id": "fence", "name": "Fence Cost & Linear Footage Estimator", "url": "/fence-cost-calculator.html", "category": "Building Envelope"},
    {"id": "pool", "name": "Pool Pump Energy Savings Calculator", "url": "/pool.html", "category": "Mechanical & Energy"},
    {"id": "deck", "name": "Deck Construction Cost Estimator", "url": "/deck-cost-calculator.html", "category": "Building Envelope"},
    {"id": "gutter", "name": "Seamless Gutters & Guards Estimator", "url": "/gutter-cost-calculator.html", "category": "Building Envelope"},
    {"id": "garage-door", "name": "Garage Door Replacement Calculator", "url": "/garage-door-calculator.html", "category": "Building Envelope"},
    {"id": "patio", "name": "Patio & Paver Installation Estimator", "url": "/patio-cost-calculator.html", "category": "Building Envelope"},
    {"id": "painting", "name": "Exterior House Painting Estimator", "url": "/exterior-painting-calculator.html", "category": "Building Envelope"}
]

ANGLES = [
    "Material Durability vs. Installed Cost Tradeoff",
    "2026 Building Code, Permit & Inspection Breakdown",
    "IRA Section 25C/30C Tax Credits & Utility Rebate Math",
    "Line-Item Trade Labor & Contractor Markup Audit",
    "Climate Zone Failure Modes & Preventative Spec Upgrades",
    "Appraisal Equity Impact vs. Turnkey Installation Cost"
]


def sanitize_title(raw_title: str) -> str:
    """Removes Markdown '#', quotes, and line breaks from generated titles."""
    cleaned = re.sub(r"[\r\n]+", " ", raw_title).strip()
    cleaned = re.sub(r"^[\s#*\"'`>]+|[\s*\"'`]+$", "", cleaned)
    cleaned = re.sub(
        r"^(?:2026\s+)?Cost\s+Analysis\s+Article(?:\s*:\s*|\s+)",
        "2026 Cost Analysis: ",
        cleaned,
        flags=re.IGNORECASE
    )
    return re.sub(r"\s+", " ", cleaned).strip()


def generate_slug(title: str) -> str:
    """Generates a clean URL-friendly slug capped at 58 characters."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(slug) > 58:
        slug = slug[:58].rsplit("-", 1)[0]
    return slug


def extract_meta_description(body_html: str, title: str) -> str:
    """Extracts the first substantive paragraph from the generated article for SEO & card excerpts."""
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", body_html, flags=re.IGNORECASE | re.DOTALL)
    for p in paragraphs:
        text = re.sub(r"<[^>]+>", " ", p)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) >= 70:
            return (text[:157].rsplit(" ", 1)[0] + "...") if len(text) > 160 else text
    return f"2026 empirical cost analysis and contractor bid breakdown for {title}."


def build_calculator_cta_box(calc: dict) -> str:
    """High-converting companion calculator + Angi quote match block placed right after the intro."""
    return f"""
    <aside class="companion-calc-cta" style="margin: 1.75rem 0; padding: 1.35rem 1.5rem; background: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #2563eb; border-radius: 12px;">
      <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #1d4ed8; margin-bottom: 0.25rem;">
        Interactive Financial Model
      </div>
      <h3 style="margin: 0 0 0.4rem 0; font-size: 1.15rem; color: #0f172a;">
        Run Your Exact Project Numbers in the {calc['name']}
      </h3>
      <p style="margin: 0 0 1rem 0; font-size: 0.92rem; color: #334155;">
        Adjust square footage, material grades, local trade labor rates, and 2026 federal tax credits to audit your contractor quotes in real time.
      </p>
      <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <a href="{calc['url']}" style="background: #2563eb; color: #ffffff; font-weight: 700; font-size: 0.88rem; padding: 0.6rem 1.15rem; border-radius: 8px; text-decoration: none;">
          Open {calc['name']} &rarr;
        </a>
        <a href="{CJ_ANGI_LINK}" target="_blank" rel="noopener sponsored" style="background: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; font-weight: 600; font-size: 0.88rem; padding: 0.6rem 1.15rem; border-radius: 8px; text-decoration: none;">
          Compare 3 Local Contractor Bids &rarr;
        </a>
      </div>
    </aside>
    """
