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
    regions = load_json_safe("data/regional_multipliers.json", {
        "US": {"name": "National Average (Baseline)", "labor_mult": 1.0, "material_mult": 1.0, "climate": "Mixed", "frost_in": 36, "rebate_note": "Federal IRA Section 25C & 30C active."}
    })
    comm_store = load_json_safe("data/commodity_history.json", {"last_updated": "2026-10-17", "commodities": {}})
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
            r'\g<1>' + default_cj_url + r'\g<2>',
            content
        )

        # 2. Update JS input listener for 5-digit ZIP codes
        js_old_pattern = r'leadMatchLink\.href\s*=\s*[`"\']https://www\.angi\.com/companylist/search\.htm\?query=[^`"\']*&amp;postalCode=\$\{zip\}[`"\'];'
        js_replacement = (
            f"const dest = `https://www.angi.com/companylist/search.htm?query={urllib.parse.quote_plus(trade)}&postalCode=${{zip}}`;\n"
            f"          leadMatchLink.href = `{CJ_TRACKING_BASE}?url=${{encodeURIComponent(dest)}}`;"
        )
        content = re.sub(js_old_pattern, js_replacement, content)

        # 3. Inject or refresh Regional & Live Commodity Spot-Price Widget
        comm_info = commodities.get(comm_key, {})
        widget_html = build_regional_and_commodity_widget(trade, comm_info, regions, last_updated)

        if "<!-- TBM REGIONAL & COMMODITY WIDGET START -->" in content:
            content = re.sub(
                r"<!-- TBM REGIONAL & COMMODITY WIDGET START -->.*?<!-- TBM REGIONAL & COMMODITY WIDGET END -->",
                widget_html,
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

        if content != orig:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            updated_count += 1
            print(f"Updated {filename} with 50-state multiplier, live commodity badge & CJ Angi tracking.")

    print(f"Batch completed: {updated_count} calculators updated.")


if __name__ == "__main__":
    main()
