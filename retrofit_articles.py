#!/usr/bin/env python3
"""
retrofit_articles.py - Retrofits all existing articles in `articles/` and `guides/` with:
 1. Clean titles (strips any raw Markdown '# ' from <title> and <h1>).
 2. Unique <meta name="description"> extracted from the opening paragraph if generic boilerplate is present.
 3. Interactive "Audit My Contractor Quote" Red-Flag Scorecard Widget.
 4. Inline SVG Turnkey Cost Benchmark Bar Chart.
 5. Shoppable 5-Row Amazon Associates (`tag=nfagiolo-20`) Bill-of-Materials (BOM) Table.
"""

import os
import re
from generate_article import (
    CALCULATORS,
    sanitize_title,
    extract_meta_description,
    build_svg_cost_chart,
    build_shoppable_bom_table,
    build_quote_auditor_widget
)

GENERIC_BOILERPLATE = "Detailed empirical cost breakdown, licensed labor pricing, building code requirements, and contractor bid verification."


def match_calculator(content: str) -> dict:
    low = content.lower()
    keyword_map = [
        (["pool", "pump"], "pool"),
        (["water heater", "tankless"], "water-heater"),
        (["generator", "standby", "transfer switch"], "generator"),
        (["ev ", "charger", "30c", "nema 14-50"], "ev-charger"),
        (["mini-split", "ductless"], "mini-split"),
        (["insulation", "air sealing", "r-49", "r-60"], "insulation"),
        (["solar", "photovoltaic", "25d"], "solar"),
        (["window", "glazing", "u-factor"], "windows"),
        (["siding", "hardie", "vinyl siding"], "siding"),
        (["fence", "fencing"], "fence"),
        (["driveway", "asphalt"], "driveway"),
        (["basement", "egress"], "basement"),
        (["bathroom", "shower", "ditra"], "bathroom"),
        (["kitchen", "cabinet"], "kitchen"),
        (["roof", "shingle"], "roofing"),
        (["heat pump", "furnace", "hvac", "seer2"], "hvac"),
    ]
    calc_by_id = {c["id"]: c for c in CALCULATORS}
    for kws, cid in keyword_map:
        if any(k in low for k in kws) and cid in calc_by_id:
            return calc_by_id[cid]
    return calc_by_id["roofing"]


def retrofit_file(filepath: str) -> bool:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    orig = content

    # 1. Strip raw Markdown '# ' from <title> and <h1>
    t_match = re.search(r"<title>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    if t_match:
        raw_t = t_match.group(1)
        clean_t = sanitize_title(raw_t.replace("| The Buyer's Math", "")) + " | The Buyer's Math"
        if raw_t != clean_t:
            content = content.replace(f"<title>{raw_t}</title>", f"<title>{clean_t}</title>", 1)

    content = re.sub(r"(<h1[^>]*>)\s*#+\s*", r"\1", content, flags=re.IGNORECASE)

    # 2. Upgrade generic boilerplate <meta name="description">
    title_only = sanitize_title(t_match.group(1)) if t_match else "Home Improvement Guide"
    unique_desc = extract_meta_description(content, title_only)
    if GENERIC_BOILERPLATE.lower() in content.lower():
        content = re.sub(
            r'(<meta\s+name=["\']description["\']\s+content=["\']).*?(["\']\s*/?>)',
            rf"\g<1>{unique_desc}\g<2>",
            content,
            flags=re.IGNORECASE | re.DOTALL
        )

    calc = match_calculator(content)

    # 3. Inject Interactive Quote Auditor & SVG Cost Chart if not already present
    if "<!-- TBM QUOTE AUDITOR WIDGET START -->" not in content:
        auditor_html = build_quote_auditor_widget(calc)
        chart_html = build_svg_cost_chart(calc)
        combo = "\n" + auditor_html + "\n" + chart_html + "\n"
        if "</p>" in content:
            content = content.replace("</p>", "</p>" + combo, 1)
        elif "</h1>" in content:
            content = content.replace("</h1>", "</h1>" + combo, 1)

    # 4. Inject Shoppable Amazon BOM Table before </article> or </main>
    if "<!-- TBM SHOPPABLE BOM START -->" not in content:
        bom_html = build_shoppable_bom_table(calc)
        if "</article>" in content:
            content = content.replace("</article>", bom_html + "\n    </article>", 1)
        elif "</main>" in content:
            content = content.replace("</main>", bom_html + "\n  </main>", 1)

    if content != orig:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Retrofitted {filepath} with Quote Auditor, SVG Chart & Shoppable BOM.")
        return True
    return False


def main():
    updated = 0
    for folder in ["articles", "guides"]:
        if not os.path.exists(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(".html"):
                if retrofit_file(os.path.join(folder, fname)):
                    updated += 1
    print(f"Retrofit complete: {updated} article(s) upgraded.")


if __name__ == "__main__":
    main()
