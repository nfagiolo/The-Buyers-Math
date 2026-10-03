# apply_calculator_updates.py (v3: Rich Components & Cross-Recommendations)
import os
import re

CALCULATOR_METADATA = {
    "roofing-cost-calculator.html": {
        "title": "Roof Replacement Cost Estimator",
        "related": [
            ("Solar Panel Payback Timeline", "solar-payback-calculator.html", "Plan solar installation alongside your new roof."),
            ("Window Replacement Estimator", "window-replacement-estimator.html", "Upgrade building envelope efficiency."),
            ("Driveway Paving Calculator", "driveway-paving-calculator.html", "Complete your exterior home curb appeal.")
        ],
        "checklist": [
            ("Verify License & Worker's Comp", "Ensure the contractor carries active general liability ($1M minimum) and worker's compensation insurance."),
            ("Line-Item Tear-Off & Decking", "Confirm in writing whether tear-off disposal and rotted plywood replacement ($70-$95/sheet) are itemized."),
            ("Ice & Water Shield Code", "Require self-adhering ice & water membrane along all eaves (at least 24 inches inside warm wall) and in valleys."),
            ("Manufacturer Certification", "Hire GAF Master Elite, Owens Corning Platinum, or CertainTeed certified roofers for valid extended non-prorated warranties.")
        ]
    },
    "hvac-roi-calculator.html": {
        "title": "Heat Pump vs. Gas Furnace ROI Calculator",
        "related": [
            ("Mini-Split AC Cost Estimator", "mini-split-calculator.html", "Zone specific rooms or additions without ductwork."),
            ("Water Heater Replacement Cost", "water-heater-calculator.html", "Pair with a high-efficiency hybrid heat pump water heater."),
            ("Backup Generator Sizing Guide", "generator-calculator.html", "Protect critical electric heating loads during winter blackouts.")
        ],
        "checklist": [
            ("Require Manual J Load Calculation", "Never accept rule-of-thumb square footage sizing. Insist on a formal Manual J calculation to prevent oversized equipment short-cycling."),
            ("Inspect Existing Ductwork Static Pressure", "Ensure existing supply and return ducts can handle heat pump airflow (typically 400 CFM per ton)."),
            ("Verify Section 25C AHRI Certificate", "Obtain the AHRI reference certificate proving the exact condenser and air handler combination qualifies for the $2,000 tax credit."),
            ("Cold-Climate COP at 5°F", "Verify the heat pump maintains a Coefficient of Performance (COP) > 1.75 at 5°F to minimize electric auxiliary heat strip usage.")
        ]
    },
    "kitchen-remodel-calculator.html": {
        "title": "Kitchen Remodel Cost Estimator",
        "related": [
            ("Basement Finishing Cost Estimator", "basement-cost-calculator.html", "Coordinate plumbing rough-ins and living space additions."),
            ("Window Replacement Estimator", "window-replacement-estimator.html", "Brighten your kitchen workspace with natural light."),
            ("Water Heater Replacement Cost", "water-heater-calculator.html", "Upgrade hot water delivery for modern dishwashers.")
        ],
        "checklist": [
            ("Confirm Detailed Milestone Payments", "Never pay more than 10-15% upfront deposit. Tie subsequent payments to completed inspection milestones."),
            ("Establish a 15% Contingency Buffer", "Concealed electrical wiring or outdated plumbing behind walls commonly adds 10-15% in unforeseen change orders."),
            ("Specify Cabinet Construction Specs", "Confirm solid plywood boxes (not particle board) and full-extension soft-close dovetail drawer boxes in the contract."),
            ("Inspect Dust Containment & Site Protection", "Require negative air pressure HEPA scrubbing and floor plastic barriers to protect living areas from drywall dust.")
        ]
    },
    "solar-payback-calculator.html": {
        "title": "Solar Panel Payback Timeline Calculator",
        "related": [
            ("Roof Replacement Cost Estimator", "roofing-cost-calculator.html", "Inspect and replace aging shingles before installing 25-year solar panels."),
            ("Heat Pump vs. Gas Furnace ROI", "hvac-roi-calculator.html", "Power high-efficiency electric heating with self-generated solar kWh."),
            ("Backup Generator Sizing Guide", "generator-calculator.html", "Pair grid-tied solar with whole-home backup power.")
        ],
        "checklist": [
            ("Verify Roof Shingle Lifespan", "If your roof is over 12-15 years old, replace shingles first; removing panels later for re-roofing costs $150-$250 per panel."),
            ("Confirm Utility Interconnection & Net Metering", "Verify in writing whether your local utility operates under 1:1 net metering or avoided-cost export rates (NEM 3.0)."),
            ("Compare Inverter Architectures", "Evaluate microinverters (Enphase) vs string inverters with DC optimizers (SolarEdge) for roof shading resilience."),
            ("Review 25-Year Production Warranties", "Ensure linear production warranties guarantee at least 85% rated power output at year 25.")
        ]
    },
    "basement-cost-calculator.html": {
        "title": "Basement Finishing Cost Estimator",
        "related": [
            ("Kitchen Remodel Cost Estimator", "kitchen-remodel-calculator.html", "Coordinate cabinetry and entertaining bar installations."),
            ("Water Heater Replacement Cost", "water-heater-calculator.html", "Relocate or replace basement utility mechanicals."),
            ("Backup Generator Sizing Guide", "generator-calculator.html", "Protect critical basement sump pumps against power failure.")
        ],
        "checklist": [
            ("Perform a 48-Hour Calcium Chloride Moisture Test", "Ensure basement concrete slab moisture vapor emissions are under 3 lbs/1,000 sq ft before installing flooring."),
            ("Verify Emergency Egress Window Well Dimensions", "Egress wells must provide a minimum 9 sq ft horizontal projection and permanent ladder if over 44 inches deep."),
            ("Thermal Break Insulation on Foundation", "Require rigid foam (XPS/EPS) or closed-cell spray foam directly against concrete before stud framing to prevent mold."),
            ("Install Dual Sump Pumps with Battery Backup", "Protect finished basement investment with redundant primary and secondary battery-backup pumps.")
        ]
    },
    "driveway-paving-calculator.html": {
        "title": "Driveway Paving Calculator",
        "related": [
            ("Roof Replacement Cost Estimator", "roofing-cost-calculator.html", "Coordinate heavy dumpster logistics before paving your driveway."),
            ("Window Replacement Estimator", "window-replacement-estimator.html", "Enhance whole-home exterior curb appeal."),
            ("Basement Finishing Cost Estimator", "basement-cost-calculator.html", "Plan proper grading and rainwater runoff away from foundations.")
        ],
        "checklist": [
            ("Verify Sub-Base Compaction & Thickness", "Ensure at least 4-6 inches of crushed recycled concrete or road base gravel compacted with a heavy vibratory roller."),
            ("Confirm Asphalt Thickness & Mix Type", "Specify minimum 2.5 to 3 inches of compacted commercial hot-mix asphalt (State DOT approved)."),
            ("Verify Positive 2% Slope Drainage", "Ensure grade slopes at least 1/4 inch per foot away from the house garage foundation to prevent pooling."),
            ("Ask About Curing Times & Sealcoating", "Contractor should specify exact vehicle avoidance periods and schedule initial sealcoating 6-12 months post-installation.")
        ]
    },
    "window-replacement-estimator.html": {
        "title": "Window Replacement Estimator",
        "related": [
            ("Roof Replacement Cost Estimator", "roofing-cost-calculator.html", "Check drip edge flashings and exterior cladding."),
            ("Heat Pump vs. Gas Furnace ROI", "hvac-roi-calculator.html", "Reduce HVAC tonnage requirements with low-E insulated glass."),
            ("Driveway Paving Calculator", "driveway-paving-calculator.html", "Complete exterior home modernization.")
        ],
        "checklist": [
            ("Verify NFRC U-Factor & SHGC Labels", "Ensure windows carry National Fenestration Rating Council (NFRC) U-factor ratings ≤ 0.28 for cold climates."),
            ("Require Low-Expansion Polyurethane Foam", "Insist that installers insulate the rough opening gap with low-expansion foam rather than stuffed fiberglass."),
            ("Inspect Flashing Tape & Sill Pans", "Verify flexible self-adhering sill pan flashing is installed beneath window units to direct leaks outward."),
            ("Check Transferable Lifetime Workmanship Warranty", "Confirm glass seal failure coverage (preventing fogging) and installation leak warranties are transferable to future owners.")
        ]
    },
    "pool.html": {
        "title": "Pool Pump Energy Calculator",
        "related": [
            ("Solar Panel Payback Timeline", "solar-payback-calculator.html", "Offset pool pump filtration power with rooftop solar."),
            ("Heat Pump vs. Gas Furnace ROI", "hvac-roi-calculator.html", "Explore pool heat pump options for extended swimming seasons."),
            ("Backup Generator Sizing Guide", "generator-calculator.html", "Maintain pool freeze protection circulation during winter storm outages.")
        ],
        "checklist": [
            ("Verify Energy Star WEF Rating", "Confirm the pump carries a Weighted Energy Factor (WEF) ≥ 8.0 to qualify for utility electric company rebates."),
            ("Match Plumbing Pipe Diameters", "Ensure 1.5-inch or 2.0-inch suction and return lines can handle maximum flow without cavitation."),
            ("Program Multi-Speed Daily Schedules", "Set low filtration RPM (1,200–1,600 RPM) for 10-12 hours and higher RPM only for automated pool sweep cleaners."),
            ("Install Auxiliary Surge Protection", "Protect sensitive variable-speed drive electronics from lightning and utility voltage spikes with a dedicated surge arrester.")
        ]
    },
    "mini-split-calculator.html": {
        "title": "Ductless Mini-Split Cost Estimator",
        "related": [
            ("Heat Pump vs. Gas Furnace ROI", "hvac-roi-calculator.html", "Compare central heat pumps with ductless multi-zone systems."),
            ("Backup Generator Sizing Guide", "generator-calculator.html", "Calculate generator wattage needed for inverter compressors."),
            ("Solar Panel Payback Timeline", "solar-payback-calculator.html", "Offset ductless cooling and heating with rooftop solar generation.")
        ],
        "checklist": [
            ("Require Deep Vacuum Micron Gauge Decay Test", "Line-sets must be evacuated below 500 microns and hold for 15 minutes before opening refrigerant valves."),
            ("Flare Connection Torque Wrench Specification", "Ensure installer uses a calibrated torque wrench and nylon flare sealant to prevent micro-leaks of R-410A or R-32."),
            ("Condensate Gravity Drain Line Routing", "Verify drain lines are pitched at least 1/4 inch per foot with accessible cleanouts to prevent indoor wall water damage."),
            ("Outdoor Surge Protector & Disconnect", "Confirm a dedicated electrical whip, fused disconnect, and surge protector are mounted adjacent to the condenser.")
        ]
    },
    "generator-calculator.html": {
        "title": "Backup Generator Sizing Guide",
        "related": [
            ("Heat Pump vs. Gas Furnace ROI", "hvac-roi-calculator.html", "Calculate starting locked-rotor amperage (LRA) for heat pump compressors."),
            ("Solar Panel Payback Timeline", "solar-payback-calculator.html", "Coordinate automatic transfer switches with solar battery storage."),
            ("Water Heater Replacement Cost", "water-heater-calculator.html", "Evaluate gas vs electric water heating loads on generator capacity.")
        ],
        "checklist": [
            ("Verify Gas Meter Capacity (CFH)", "Ensure your municipal gas meter flow rating (e.g., 250 CFH vs 400+ CFH) can support generator BTU demand plus existing appliances."),
            ("Calculate Locked Rotor Amps (LRA) & Soft Starters", "If running central AC on generator power, consider installing a soft starter to reduce compressor surge amps by 60%."),
            ("Maintain 5-Foot Clearance from Openings", "Verify installation adheres to NFPA 37 clearance guidelines (minimum 5 feet from windows, doors, and vinyl soffits)."),
            ("Install Wireless Mobile Link Monitoring", "Ensure the generator controller connects to home WiFi for real-time mobile alerts during weekly automated test exercises.")
        ]
    },
    "water-heater-calculator.html": {
        "title": "Water Heater Replacement Cost Estimator",
        "related": [
            ("Heat Pump vs. Gas Furnace ROI", "hvac-roi-calculator.html", "Pair hybrid heat pump water heating with heat pump home HVAC."),
            ("Kitchen Remodel Cost Estimator", "kitchen-remodel-calculator.html", "Upgrade hot water delivery for modern luxury fixtures."),
            ("Basement Finishing Cost Estimator", "basement-cost-calculator.html", "Install smart leak shutoff valves before finishing basement spaces.")
        ],
        "checklist": [
            ("Install Thermal Expansion Tank", "Required by plumbing code on closed water systems to absorb thermal expansion pressure and protect tank glass lining."),
            ("Gas Line Sizing for Tankless Units", "Tankless units require 150k-199k BTUs. Confirm existing 1/2-inch gas lines are upsized to 3/4-inch to prevent burner starvation."),
            ("Verify Electric Service for Heat Pump Tanks", "Hybrid heat pump tanks require dedicated 240V / 30-amp electrical circuits. Ensure panel space is available."),
            ("Add Automatic Emergency Shutoff Valve", "Protect finished flooring with a smart brass shutoff valve paired with floor water sensing pucks.")
        ]
    }
}

def generate_checklist_html(items):
    cards_html = ""
    for title, desc in items:
        cards_html += f"""        <div class="checklist-item">
          <strong>✓ {title}</strong>
          <p>{desc}</p>
        </div>\n"""
    return f"""  <!-- Contractor Vetting Checklist -->
  <section class="contractor-checklist-card">
    <h3>📋 Contractor Vetting Checklist: 4 Questions to Ask Before Signing</h3>
    <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.25rem;">Protect your home and budget by verifying these critical technical standards with prospective contractors:</p>
    <div class="checklist-grid">
{cards_html}    </div>
  </section>\n"""

def generate_related_html(related_items):
    cards_html = ""
    for title, url, desc in related_items:
        cards_html += f"""      <a href="{url}" class="calc-card" style="text-decoration: none;">
        <div>
          <span class="badge-category">Related Tool</span>
          <h3 style="font-size: 1.15rem; margin-top: 0.25rem;">{title}</h3>
          <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem;">{desc}</p>
        </div>
        <span class="cta-link" style="font-size: 0.9rem;">Open Calculator &rarr;</span>
      </a>\n"""
    return f"""  <!-- Related Calculators Section -->
  <section class="related-calculators-section">
    <h3>Explore Related Home Improvement Calculators</h3>
    <div class="related-grid">
{cards_html}    </div>
  </section>\n"""

def update_calculator(filename, meta):
    if not os.path.exists(filename):
        return

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    # Avoid duplicate injection
    if "Contractor Vetting Checklist" in content:
        print(f"{filename} already has rich components.")
        return

    checklist_html = generate_checklist_html(meta["checklist"])
    related_html = generate_related_html(meta["related"])

    # Inject checklist and related calculators before </main> or before footer
    if "</main>" in content:
        content = content.replace("</main>", f"{checklist_html}\n{related_html}\n  </main>", 1)
    elif "<footer" in content:
        content = content.replace("<footer", f"{checklist_html}\n{related_html}\n<footer", 1)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully added rich components to {filename}")

def main():
    for filename, meta in CALCULATOR_METADATA.items():
        update_calculator(filename, meta)
    print("Done adding rich components to all calculators.")

if __name__ == "__main__":
    main()
