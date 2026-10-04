# retrofit_articles.py
# One-time script to inject all 4 revenue generators into previously published articles.

import os
import re

CALCULATORS = [
    {"name": "Roof Replacement Cost Estimator", "url": "../roofing-cost-calculator.html", "keywords": ["roof", "shingle"]},
    {"name": "Heat Pump vs. Gas Furnace ROI", "url": "../hvac-roi-calculator.html", "keywords": ["hvac", "heat pump", "furnace"]},
    {"name": "Basement Finishing Cost Estimator", "url": "../basement-cost-calculator.html", "keywords": ["basement", "framing"]},
    {"name": "Solar Panel Payback Timeline", "url": "../solar-payback-calculator.html", "keywords": ["solar", "panels"]},
    {"name": "Kitchen Remodel Cost Estimator", "url": "../kitchen-remodel-calculator.html", "keywords": ["kitchen", "cabinet"]},
    {"name": "Driveway Paving Calculator", "url": "../driveway-paving-calculator.html", "keywords": ["driveway", "asphalt", "paving"]},
    {"name": "Window Replacement Estimator", "url": "../window-replacement-estimator.html", "keywords": ["window", "glazing"]},
    {"name": "Pool Pump Energy Calculator", "url": "../pool.html", "keywords": ["pool", "pump"]},
    {"name": "Mini-Split AC Cost Estimator", "url": "../mini-split-calculator.html", "keywords": ["mini-split", "ductless"]},
    {"name": "Backup Generator Sizing Guide", "url": "../generator-calculator.html", "keywords": ["generator", "backup"]},
    {"name": "Water Heater Replacement Cost", "url": "../water-heater-calculator.html", "keywords": ["water heater", "tankless"]}
]

def find_best_calculator(content):
    lower_content = content.lower()
    for calc in CALCULATORS:
        for kw in calc["keywords"]:
            if kw in lower_content:
                return calc["name"], calc["url"]
    return "Cost Calculators", "../index.html"

def retrofit_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already has top revenue box
    if "Recommended Project Gear" in content:
        print(f"Skipping {filepath} (already monetized)")
        return

    calc_name, calc_url = find_best_calculator(content)

    top_box = f"""
      <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 1.25rem 1.5rem; margin: 1.5rem 0 2rem 0; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span style="background: #f59e0b; color: #ffffff; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em;">Recommended Project Gear</span>
          <p style="margin: 0.4rem 0 0 0; font-weight: 600; color: #92400e; font-size: 1rem;">Tools &amp; Materials on Amazon</p>
          <p style="margin: 0.2rem 0 0 0; color: #78350f; font-size: 0.85rem;">Check real-time pricing and customer reviews before starting:</p>
        </div>
        <a href="https://www.amazon.com/s?k=home+improvement+tools&tag=nfagiolo-20" target="_blank" rel="noopener noreferrer" style="background: #d97706; color: #ffffff; padding: 0.65rem 1.25rem; border-radius: 6px; font-weight: 700; font-size: 0.9rem; text-decoration: none; display: inline-flex; align-items: center; gap: 0.4rem; box-shadow: 0 2px 4px rgba(217, 119, 6, 0.25);">
          🛒 Check Deals on Amazon &rarr;
        </a>
      </div>
    """

    mid_and_ads = f"""
      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #2563eb; border-radius: 8px; padding: 1.5rem; margin: 2.5rem 0; text-align: center;">
        <span style="color: #2563eb; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">Interactive Estimator</span>
        <h3 style="margin: 0.4rem 0 0.5rem 0; color: #1e3a8a; font-size: 1.3rem;">Calculate Exact Costs for Your Home</h3>
        <p style="margin: 0 0 1.25rem 0; color: #475569; font-size: 0.95rem;">Model custom square footage, labor rates, and local tax incentives with our free tool:</p>
        <a href="{calc_url}" style="background: #2563eb; color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 700; text-decoration: none; display: inline-block;">Open the {calc_name} &rarr;</a>
      </div>

      <div style="margin: 2.5rem 0; text-align: center; min-height: 250px;">
        <ins class="adsbygoogle"
             style="display:block; text-align:center;"
             data-ad-layout="in-article"
             data-ad-format="fluid"
             data-ad-client="ca-pub-1199906473460957"
             data-ad-slot="responsive"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
      </div>
    """

    # Inject top box
    if "Published on" in content:
        idx = content.find("Published on")
        end_div = content.find("</div>", idx)
        if end_div != -1:
            insert_pos = end_div + len("</div>")
            content = content[:insert_pos] + "\n" + top_box + content[insert_pos:]
    elif "</h1>" in content:
        content = content.replace("</h1>", f"</h1>\n{top_box}", 1)

    # Inject mid-article card
    if "</article>" in content:
        content = content.replace("</article>", f"{mid_and_ads}\n    </article>", 1)
    elif "</main>" in content:
        content = content.replace("</main>", f"{mid_and_ads}\n  </main>", 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated: {filepath}")

def main():
    articles_dir = "articles"
    if not os.path.exists(articles_dir):
        print("No articles directory found.")
        return

    for fname in os.listdir(articles_dir):
        if fname.endswith(".html"):
            retrofit_file(os.path.join(articles_dir, fname))
    print("Done retrofitting existing articles.")

if __name__ == "__main__":
    main()
