#!/usr/bin/env python3
"""
update_content.py - Safe, idempotent Daily Buyer's Math Tip updater.
1. Uses Tier 1 Gemini API (`gemini-4-argon` with `gemini-2.5-flash` fallback) instead of retired `gemini-1.5-flash`.
2. Uses verified Amazon search queries (`https://www.amazon.com/s?k=...&tag=nfagiolo-20`) instead of hallucinated `/dp/ASIN` links.
3. Replaces the Daily Tip cleanly inside `<!-- TBM DAILY TIP START --> ... <!-- TBM DAILY TIP END -->` so tips never stack infinitely.
4. Calls `sync_guides.py` to keep `index.html`, calculator trade guides, `sitemap.xml`, and `feed.xml` synchronized.
"""

import os
import re
from datetime import date
import requests
import sync_guides

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
AMAZON_TAG = "nfagiolo-20"
ADSENSE_CLIENT = "ca-pub-1199906473460957"

PROMPT = """Write a concise, authoritative 140-word daily homeowner cost-saving tip focusing on the math and ROI behind ONE specific high-intent upgrade:
- Schluter DITRA-HEAT electric floor warming vs. contractor markup
- Pentair IntelliFlo3 variable-speed pool pump kWh payback
- Rheem ProTerra hybrid heat pump water heater Section 25C tax credit math
- Generac 24kW standby generator vs. 50A portable interlock kit cost
- Hardwired 48A EV charger vs. Hubbell NEMA 14-50 receptacle cost

Format strictly as raw HTML with a bold <h4> subheadline and one <p> paragraph (no ```html fences).
Include ONE contextual Amazon Associates search link inside the paragraph using this exact URL format (with '+' between keywords):
<a href="[https://www.amazon.com/s?k=KEYWORD+HERE&tag=nfagiolo-20](https://www.amazon.com/s?k=KEYWORD+HERE&tag=nfagiolo-20)" target="_blank" rel="noopener sponsored" style="color: #2563eb; font-weight: 700;">
"""


def generate_daily_tip() -> str:
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY not set; skipping daily tip generation.")
        return ""

    for model_name, use_thinking in [("gemini-4-argon", True), ("gemini-2.5-flash", False)]:
        url = f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){model_name}:generateContent?key={GEMINI_API_KEY}"
        gen_cfg = {"maxOutputTokens": 2048, "temperature": 0.3}
        if use_thinking:
            gen_cfg["thinkingConfig"] = {"thinkingLevel": "LOW"}
        payload = {
            "contents": [{"parts": [{"text": PROMPT}]}],
            "generationConfig": gen_cfg,
        }
        try:
            res = requests.post(url, json=payload, timeout=60)
            if res.status_code == 200:
                parts = res.json()["candidates"][0]["content"]["parts"]
                text = "".join(p.get("text", "") for p in parts if not p.get("thought", False)).strip()
                return re.sub(r"^```html\s*|\s*```$", "", text).strip()
        except Exception as e:
            print(f"{model_name} error: {e}")
    return ""


def update_index_tip(tip_html: str):
    if not tip_html or not os.path.exists("index.html"):
        return

    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # Clean up any legacy stacked daily-tip-container blocks from old runs
    html_content = re.sub(
        r'<div class="daily-tip-container".*?</div>\s*</div>',
        "",
        html_content,
        flags=re.DOTALL,
    )

    date_str = date.today().strftime("%B %d, %Y")
    block = f"""<!-- TBM DAILY TIP START -->
<div class="daily-tip-container" style="padding: 1.25rem 1.5rem; background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 10px; margin: 1.5rem 0;">
  <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb; margin-bottom: 0.25rem;">
    Buyer's Math Tip of the Day &bull; {date_str}
  </div>
  {tip_html}
</div>
<!-- TBM DAILY TIP END -->"""

    if "<!-- TBM DAILY TIP START -->" in html_content and "<!-- TBM DAILY TIP END -->" in html_content:
        html_content = re.sub(
            r"<!-- TBM DAILY TIP START -->.*?<!-- TBM DAILY TIP END -->",
            lambda _: block,
            html_content,
            flags=re.DOTALL,
        )
    elif "<!-- GEMINI_TIP_PLACEHOLDER -->" in html_content:
        html_content = html_content.replace("<!-- GEMINI_TIP_PLACEHOLDER -->", block, 1)
        html_content = html_content.replace("<!-- GEMINI_TIP_PLACEHOLDER -->", "")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Updated single idempotent Daily Tip in index.html for {date_str}.")


if __name__ == "__main__":
    tip = generate_daily_tip()
    update_index_tip(tip)
    all_articles = sync_guides.get_all_articles()
    sync_guides.update_index_editorial(all_articles)
    sync_guides.inject_trade_guides_into_calculators(all_articles)
    sync_guides.generate_sitemap_xml(all_articles)
    sync_guides.generate_rss_feed(all_articles)
