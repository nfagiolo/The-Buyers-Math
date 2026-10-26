#!/usr/bin/env python3
"""
retrofit_articles.py - Retrofits all existing articles in `articles/` and `guides/` with:
1. Clean titles (strips any raw Markdown '#' from <title> and <h1>).
2. Unique <meta name="description"> extracted from the opening paragraph if generic boilerplate is present.
3. Interactive "Audit My Contractor Quote" Red-Flag Scorecard Widget.
4. Inline SVG Turnkey Cost Benchmark Bar Chart.
5. Shoppable 5-Row Amazon Associates (`tag=nfagiolo-20`) Bill-of-Materials (BOM) Table.
6. Automatic deduplication of any repeated INTERACTIVE ESTIMATOR or widget blocks.
"""

import os
import re
from generate_article import (
    CALCULATORS,
    sanitize_title,
    extract_meta_description,
    build_svg_cost_chart,
    build_shoppable_bom_table,
    build_quote_auditor_widget,
)

GENERIC_BOILERPLATE = "Detailed empirical cost breakdown, licensed labor pricing, building code requirements, and contractor bid verification."

KEYWORD_MAP = [
    (["ditra", "schluter", "kerdi", "radiant", "heated floor", "tile", "bathroom", "shower", "wet-room", "vanity"], "bathroom"),
    (["pool", "pump"], "pool"),
    (["water heater", "tankless", "proterra"], "water-heater"),
    (["generator", "standby", "transfer switch", "generac"], "generator"),
    (["ev ", "charger", "30c", "nema 14-50", "wall connector"], "ev-charger"),
    (["mini-split", "ductless"], "mini-split"),
    (["insulation", "air sealing", "r-49", "r-60"], "insulation"),
    (["solar", "photovoltaic", "25d", "microinverter"], "solar"),
    (["window", "glazing", "u-factor"], "windows"),
    (["siding", "hardie", "vinyl siding"], "siding"),
    (["fence", "fencing"], "fence"),
    (["driveway", "asphalt"], "driveway"),
    (["basement", "egress"], "basement"),
    (["kitchen", "cabinet", "countertop"], "kitchen"),
    (["roof", "shingle", "underlayment"], "roofing"),
    (["heat pump", "furnace", "hvac", "seer2"], "hvac"),
]


def match_calculator(content: str) -> dict:
    calc_by_id = {c["id"]: c for c in CALCULATORS}

    # 1. Match against <title> and <h1> first so passing mentions in body text never hijack the trade
    t_match = re.search(r"<title>(.*?)</title>", content, flags=re.IGNORECASE | re.DOTALL)
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, flags=re.IGNORECASE | re.DOTALL)
    heading_text = ((t_match.group(1) if t_match else "") + " " + (h1_match.group(1) if h1_match else "")).lower()

    for kws, cid in KEYWORD_MAP:
        if any(k in heading_text for k in kws) and cid in calc_by_id:
            return calc_by_id[cid]

    # 2. Fallback to full content scan if heading didn't match a specific trade
    low = content.lower()
    for kws, cid in KEYWORD_MAP:
        if any(k in low for k in kws) and cid in calc_by_id:
            return calc_by_id[cid]

    return calc_by_id["roofing"]


def deduplicate_blocks(content: str) -> str:
    # Deduplicate commented Quote Auditor widgets
    blocks = re.findall(
        r"<!-- TBM QUOTE AUDITOR WIDGET START -->.*?<!-- TBM QUOTE AUDITOR WIDGET END -->",
        content,
        flags=re.DOTALL,
    )
    if len(blocks) > 1:
        for b in blocks[1:]:
            content = content.replace(b, "", 1)

    # Deduplicate commented Shoppable BOM tables
    bom_blocks = re.findall(
        r"<!-- TBM SHOPPABLE BOM START -->.*?<!-- TBM SHOPPABLE BOM END -->",
        content,
        flags=re.DOTALL,
    )
    if len(bom_blocks) > 1:
        for b in bom_blocks[1:]:
            content = content.replace(b, "", 1)

    # Deduplicate uncommented INTERACTIVE ESTIMATOR CTA boxes (fixes the 28x repeated CTA bug across all articles)
    cta_pattern = re.compile(
        r'<div[^>]*>\s*<span[^>]*>\s*INTERACTIVE ESTIMATOR\s*</span>\s*'
        r'<h2[^>]*>\s*Calculate Exact Costs for Your Home\s*</h2>.*?'
        r'Open the [^<]+</a>\s*</div>',
        re.IGNORECASE | re.DOTALL,
    )
    cta_matches = list(cta_pattern.finditer(content))
    if len(cta_matches) > 1:
        first_block = cta_matches[0].group(0)
        first_pos = cta_matches[0].start()
        stripped = cta_pattern.sub("", content)
        content = stripped[:first_pos] + first_block + stripped[first_pos:]

    return content


def retrofit_file(filepath: str) -> bool:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    orig = content

    # Deduplicate any repeated widgets or INTERACTIVE ESTIMATOR boxes
    content = deduplicate_blocks(content)

    # 1. Strip raw Markdown '#' from <title> and <h1>
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
            r'(<meta\s+name=["\']description["\']\s+content=["\'])(.*?)(["\']\s*/?>)',
            lambda m: m.group(1) + unique_desc + m.group(3),
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )

    calc = match_calculator(content)

    # If an existing non-insulation article accidentally got the Attic Insulation widget, strip it so it gets the right trade widget
    if calc["id"] != "insulation" and "Attic Insulation & Air Sealing" in content:
        content = re.sub(
            r"<!-- TBM QUOTE AUDITOR WIDGET START -->.*?<!-- TBM QUOTE AUDITOR WIDGET END -->",
            "",
            content,
            flags=re.DOTALL,
        )
        content = re.sub(
            r"<!-- TBM SHOPPABLE BOM START -->.*?<!-- TBM SHOPPABLE BOM END -->",
            "",
            content,
            flags=re.DOTALL,
        )

    # 3. Inject Interactive Quote Auditor & SVG Cost Chart if not already present
    if "<!-- TBM QUOTE AUDITOR WIDGET START -->" not in content:
        auditor_html = build_quote_auditor_widget(calc)
        chart_html = build_svg_cost_chart(calc)
        combo = "\n" + auditor_html + "\n" + chart_html + "\n"
        if "</p>" in content:
            content = content.replace("</p>", "</p>" + combo, 1)
        elif "</h1>" in content:
            content = content.replace("</h1>", "</h1>" + combo, 1)

    if 'name="google-adsense-account"' not in content and "</head>" in content:
        content = content.replace(
            "</head>",
            '  <meta name="google-adsense-account" content="ca-pub-1199906473460957">\n</head>',
            1,
        )

    if "<!-- TBM SHOPPABLE BOM START -->" not in content:
        bom_html = build_shoppable_bom_table(calc)
        bom_combo = "\n" + bom_html + "\n"
        if "</h2>" in content:
            content = content.replace("</h2>", "</h2>" + bom_combo, 1)
        elif "</p>" in content:
            content = content.replace("</p>", "</p>" + bom_combo, 1)

    if content != orig:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    modified = 0
    dirs_to_check = ["articles", "guides"]
    for d in dirs_to_check:
        if not os.path.isdir(d):
            continue
        for root, _, files in os.walk(d):
            for f in sorted(files):
                if f.endswith(".html"):
                    path = os.path.join(root, f)
                    if retrofit_file(path):
                        print(f"Retrofitted: {path}")
                        modified += 1
    print(f"Total retrofitted: {modified}")


if __name__ == "__main__":
    main()
