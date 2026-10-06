#!/usr/bin/env python3
"""
inject_hardware_cards.py - Automated Amazon Hardware Grid Upgrader
Injects curated 3-card Amazon equipment recommendations (tag=nfagiolo-20)
directly above the bundled projects section on all 14 remaining calculators.
"""

import os

TAG = "nfagiolo-20"

def make_section(heading, cards):
    cards_html = ""
    for badge, bg, col, title, desc, q in cards:
        cards_html += f"""        <div style="border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; background: var(--slate-50); display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <span style="display: inline-block; background: {bg}; color: {col}; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px; margin-bottom: 0.5rem;">{badge}</span>
            <h4 style="margin: 0 0 0.5rem 0; font-size: 1.05rem; color: var(--slate-900);">{title}</h4>
            <p style="font-size: 0.85rem; color: var(--slate-600); line-height: 1.5; margin: 0 0 1rem 0;">
              {desc}
            </p>
          </div>
          <a href="https://www.amazon.com/s?k={q}&tag={TAG}" target="_blank" rel="noopener noreferrer sponsored" style="display: inline-block; background: #ffffff; border: 1px solid var(--border); padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; font-size: 0.85rem; color: var(--primary); text-decoration: none; text-align: center;">
            View on Amazon &rarr;
          </a>
        </div>\n"""

    return f"""    <!-- Essential Equipment & Hardware Recommendations -->
    <section style="margin-top: 3rem; background: #ffffff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.75rem; box-shadow: var(--shadow-sm);">
      <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.5rem;">
        <div>
          <span style="font-size: 0.8rem; font-weight: 700; color: #2563eb; text-transform: uppercase;">Essential Equipment</span>
          <h3 style="margin: 0.25rem 0 0 0; font-size: 1.35rem; color: var(--slate-900);">{heading}</h3>
        </div>
        <small style="color: var(--slate-500);">Direct Builder-Grade Equipment Recommendations</small>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem;">
{cards_html}      </div>
    </section>\n\n"""

CALCULATOR_DATA = {
    "roofing-cost-calculator.html": (
        "Builder-Grade Roofing Tools & Safety Upgrades", [
            ("OSHA Fall Protection", "#fee2e2", "#991b1b", "Roofing Safety Harness & Lanyard Kit", "Complete 50-ft vertical lifeline, heavy-duty reusable roof anchor bracket, and full-body harness for steep-slope tear-offs.", "roofing+safety+harness+kit+50ft"),
            ("Jobsite Clean-Up", "#e0e7ff", "#3730a3", "Heavy-Duty Magnetic Nail Sweeper", "Rolling magnetic sweeper with quick-release handle retrieves thousands of discarded roofing nails from lawn and driveway pavers.", "magnetic+sweeper+with+wheels+for+roofing+nails"),
            ("Ice Dam Prevention", "#dcfce7", "#166534", "Self-Adhering Ice & Water Membrane", "High-temperature rubberized asphalt roll seals eaves, valleys, and rakes against wind-driven rain and winter ice backups.", "ice+and+water+shield+roofing+underlayment")
        ]
    ),
    "siding-cost-calculator.html": (
        "Builder-Grade Siding Tools & Weather Barriers", [
            ("Precision Cutting", "#e0e7ff", "#3730a3", "Fiber Cement Circular Saw Blade (PCD)", "Polycrystalline diamond-tipped blades cut James Hardie lap siding cleanly with 50% less airborne silica dust.", "hardie+blade+fiber+cement+circular+saw"),
            ("Vapor Permeable", "#dcfce7", "#166534", "Commercial Drainable Housewrap", "Engineered drainage spacer pattern sheds wind-driven moisture behind vinyl and fiber cement cladding, preventing wall rot.", "drainable+housewrap+vapor+barrier+roll"),
            ("Installation Labor", "#fef3c7", "#92400e", "Siding Gecko Gauge Clamping Tools", "Patented gauges support and gauge lap siding for solo installation with exact consistent reveals without chalk lines.", "gecko+gauge+fiber+cement+siding+tools")
        ]
    ),
    "window-replacement-estimator.html": (
        "Flashing, Air Sealing & Installation Hardware", [
            ("Window Rough-In", "#e0e7ff", "#3730a3", "Flexible Sill Flashing Membrane Tape", "Conformable butyl adhesive tape seals rough window sill pans seamlessly, directing intruding rainwater to the exterior.", "flexible+window+sill+flashing+tape"),
            ("Non-Bowing Sealant", "#dcfce7", "#166534", "Low-Pressure Window & Door Spray Foam", "AAMA-certified polyurethane foam seals perimeter air gaps without expanding so forcefully that it deflects vinyl window frames.", "window+and+door+low+pressure+foam+sealant"),
            ("UV & Heat Defense", "#fef3c7", "#92400e", "Ceramic Low-E Window Tint Film", "Reduces solar heat gain coefficient (SHGC) on existing double-pane windows, blocking 99% UV rays and cutting AC runtime.", "ceramic+low-e+window+tint+film+heat+blocking")
        ]
    ),
    "fence-cost-calculator.html": (
        "Builder-Grade Fence Digging & Gate Hardware", [
            ("Sag Prevention", "#fee2e2", "#991b1b", "Heavy-Duty Anti-Sag Gate Corner Bracket Kit", "Welded steel corner brackets and turnbuckle cable assembly prevent wooden privacy gates from dragging on grass and binding.", "anti+sag+gate+kit+heavy+duty+turnbuckle"),
            ("Labor Efficiency", "#e0e7ff", "#3730a3", "Gasoline / Electric Post Hole Digger Auger", "High-torque 52cc auger powerhead with 8-inch bit drills 36-inch deep frost-line post footings in under 2 minutes per hole.", "gas+post+hole+digger+auger+fence+posts"),
            ("Post Rot Defense", "#dcfce7", "#166534", "Post Protector Barrier Sleeves", "Heavy-duty polymer sleeves isolate pressure-treated wood posts from sub-soil bacteria and concrete, preventing ground-level rot.", "post+protector+barrier+sleeves+4x4")
        ]
    ),
    "driveway-paving-calculator.html": (
        "Paving Maintenance & Crack Sealing Equipment", [
            ("Freeze-Thaw Defense", "#fee2e2", "#991b1b", "Commercial Rubberized Asphalt Crack Filler", "Hot-pour or direct cold-pour elastomeric sealant bridges expansion joints to stop winter water intrusion and frost heave.", "rubberized+asphalt+crack+filler+commercial"),
            ("Surface Protection", "#e0e7ff", "#3730a3", "Silane-Siloxane Concrete Penetrating Sealer", "Hydrophobic deep-penetrating sealer chemically bonds with concrete pores to prevent de-icing salt pitting and spalling.", "silane+siloxane+penetrating+concrete+sealer"),
            ("Prep & Clean", "#dcfce7", "#166534", "Gas Pressure Washer (3200+ PSI)", "Essential high-output pressure washer with rotary surface cleaner attachment cleans oil, mildew, and loose aggregate prior to sealing.", "gas+pressure+washer+surface+cleaner+attachment")
        ]
    ),
    "hvac-roi-calculator.html": (
        "Smart Heat Pump Controls & Air Quality Hardware", [
            ("Dual-Fuel Optimization", "#dcfce7", "#166534", "Ecobee Smart Thermostat Premium", "Programmable compressor lockout staging switches seamlessly between heat pump and auxiliary gas furnace at economic balance points.", "ecobee+smart+thermostat+premium"),
            ("Surge Defense", "#e0e7ff", "#3730a3", "HVAC Disconnect Surge Protective Device", "Inverter heat pump control boards cost $800+ to replace; dedicated outdoor disconnect SPDs safeguard delicate variable-speed electronics.", "hvac+surge+protector+intermatic"),
            ("Drain Pan Overflow", "#fee2e2", "#991b1b", "Automatic Condensate Float Safety Switch", "Shuts down cooling immediately if evaporator drain lines clog with algae, preventing catastrophic ceiling water leaks.", "hvac+condensate+overflow+switch+safe-t-switch")
        ]
    ),
    "mini-split-calculator.html": (
        "Ductless Installation & Line-Set Hardware", [
            ("Exterior Aesthetics", "#e0e7ff", "#3730a3", "Decorative PVC Line-Set Cover Kit", "Weatherproof paintable conduit hide hides copper refrigeration lines, communication cables, and drain hoses on exterior siding.", "mini+split+line+set+cover+kit+decorative"),
            ("Snow & Ice Defense", "#fee2e2", "#991b1b", "Heavy-Duty Wall Mounting Bracket", "Elevates outdoor inverter condenser 12 to 24 inches off ground level to prevent winter snow drift blockages and vibration noise.", "mini+split+wall+mounting+bracket+heavy+duty"),
            ("Active Drainage", "#dcfce7", "#166534", "Mini-Split Automatic Condensate Removal Pump", "Ultra-quiet internal reservoir pump lifts indoor head unit condensate when gravity drainage through exterior walls is impossible.", "mini+split+condensate+pump+quiet")
        ]
    ),
    "attic-insulation-calculator.html": (
        "Attic Weatherization & Air Sealing Upgrades", [
            ("Major Air Leak", "#fee2e2", "#991b1b", "Attic Stair Insulation Cover Tent", "Heavy-duty double reflective radiant barrier zipper tent seals pull-down attic stairs, eliminating massive ceiling heat loss.", "attic+stairs+insulation+cover+tent+fireproof"),
            ("Soffit Airflow", "#e0e7ff", "#3730a3", "AccuVent / Rafter Insulation Baffles", "Prevents blown-in cellulose or fiberglass from blocking soffit intake vents, ensuring continuous ventilation to stop roof ice dams.", "rafter+insulation+baffles+attic+ventilation"),
            ("Air Sealing", "#dcfce7", "#166534", "Professional Foam Dispensing Gun & Canister", "Precision trigger dispensing gun seals wire penetrations, top plates, and plumbing chases with zero waste compared to straw cans.", "pro+expanding+foam+gun+applicator")
        ]
    ),
    "water-heater-calculator.html": (
        "Plumbing Safety, Expansion & Descaling Upgrades", [
            ("IPC Code Requirement", "#fee2e2", "#991b1b", "Thermal Expansion Tank (2.1 Gallon)", "Absorbs dangerous thermal water pressure spikes in closed municipal loop systems, preventing premature water heater tank rupture.", "thermal+expansion+tank+water+heater+amtrol"),
            ("Tankless Flush Kit", "#e0e7ff", "#3730a3", "Tankless Water Heater Descaler Kit", "Submersible utility pump, hoses, and non-toxic solution cleans mineral scale from heat exchangers to maintain factory warranty.", "tankless+water+heater+flush+kit+submersible+pump"),
            ("Flood Defense", "#dcfce7", "#166534", "Automatic Water Shut-Off Valve & Leak Sensor", "Motorized brass ball valve automatically cuts main water supply in seconds when moisture contacts the floor sensor.", "automatic+water+shutoff+valve+leak+sensor")
        ]
    ),
    "solar-payback-calculator.html": (
        "Solar Energy Monitoring & Storage Hardware", [
            ("Power Intelligence", "#dcfce7", "#166534", "Emporia Vue Gen 3 Energy Monitor", "Tracks real-time solar generation vs. household consumption per circuit, verifying utility net metering credits on your electric bill.", "emporia+vue+gen+3+home+energy+monitor"),
            ("Emergency Backup", "#e0e7ff", "#3730a3", "EcoFlow DELTA Pro Portable Power Station", "3.6 kWh expandable LFP battery with 240V output connects directly to solar arrays or manual transfer switches during grid blackouts.", "ecoflow+delta+pro+portable+power+station"),
            ("Pest Protection", "#fee2e2", "#991b1b", "Solar Panel Bird & Critter Guard Kit", "Heavy-duty black PVC-coated wire mesh clips around panel frames, preventing pigeons and squirrels from chewing DC wiring.", "solar+panel+bird+guard+wire+mesh+clips")
        ]
    ),
    "kitchen-remodel-calculator.html": (
        "High-Utility Kitchen Fixtures & Hardware", [
            ("Water Purification", "#dcfce7", "#166534", "Tankless Reverse Osmosis Water System", "High-flow 800 GPD tankless RO system fits under sink cabinets, removing PFAS, lead, and microplastics with zero water stagnation.", "tankless+reverse+osmosis+system+under+sink+waterdrop"),
            ("Cabinet Organization", "#e0e7ff", "#3730a3", "Rev-A-Shelf Pullout Waste & Recycling Bins", "Soft-close undermount ball-bearing slides conceal dual 35-quart trash and recycling bins inside base cabinets.", "rev-a-shelf+double+pullout+trash+can+soft+close"),
            ("Hardware Installation", "#fef3c7", "#92400e", "Cabinet Hardware Jig & Hole Locator", "Precision aluminum drilling template ensures handles and pulls align with zero crooked drill holes across cabinet doors and drawers.", "cabinet+hardware+jig+drilling+template")
        ]
    ),
    "bathroom-remodel-calculator.html": (
        "Tile Waterproofing & Luxury Bathroom Hardware", [
            ("Leak-Proof Shower", "#fee2e2", "#991b1b", "Schluter Kerdi Shower Kit (38\" x 60\")", "Complete pre-sloped shower pan, integrated drain assembly, and waterproof membrane roll eliminates traditional mud-bed leaks.", "schluter+kerdi+shower+kit+with+drain"),
            ("Heated Floors", "#dcfce7", "#166534", "DITRA-HEAT Electric Radiant Floor Warming Kit", "Uncoupling membrane prevents tile grout cracking while electric cables and WiFi touchscreen thermostat provide warm tile floors.", "schluter+ditra+heat+complete+floor+warming+kit"),
            ("Quiet Humidity Exhaust", "#e0e7ff", "#3730a3", "Panasonic WhisperSense Humidity-Sensing Fan", "Whisper-quiet (0.3 sones) 110 CFM bath fan activates automatically when steam rises, preventing mirror fogging and mold growth.", "panasonic+whispersense+humidity+sensing+bathroom+fan")
        ]
    ),
    "ev-charger-calculator.html": (
        "Level 2 Charging Hardware & Electrical Upgrades", [
            ("Universal Standard", "#e0e7ff", "#3730a3", "Tesla Universal Wall Connector", "Integrated Magic Dock adapter automatically charges both NACS (Tesla) and J1772 electric vehicles up to 48A (11.5 kW).", "tesla+universal+wall+connector+level+2"),
            ("Heavy-Duty Safety", "#fee2e2", "#991b1b", "Bryant / Hubbell Industrial NEMA 14-50 Outlet", "Industrial-grade receptacle with thick brass screw terminals prevents high-resistance overheating and melted outlets from continuous 32A/40A draw.", "bryant+industrial+nema+14-50r+receptacle"),
            ("Load Management", "#dcfce7", "#166534", "NeoCharge Smart Circuit Splitter (240V)", "UL-listed smart switch shares an existing 240V dryer outlet with your EV charger, avoiding a $3,500 main service panel upgrade.", "neocharge+smart+splitter+240v+ev+charger")
        ]
    ),
    "generator-calculator.html": (
        "Emergency Backup Power & Transfer Hardware", [
            ("Safe Electrical Feed", "#fee2e2", "#991b1b", "Reliance 50-Amp Power Inlet Box (NEMA 3R)", "Outdoor rainproof inlet connects portable or standby generator power cords directly to your indoor transfer switch safely.", "reliance+50+amp+generator+power+inlet+box"),
            ("Heavy-Duty Link", "#e0e7ff", "#3730a3", "50-Amp 25-Foot Generator Power Cord", "Heavy pure copper 6 AWG wire with NEMA 14-50P and SS2-50R twist-lock ends safely handles up to 12,500 continuous running watts.", "50+amp+generator+cord+25+ft+heavy+duty"),
            ("AC Protection", "#dcfce7", "#166534", "Micro-Air EasyStart Soft Starter", "Reduces AC compressor locked rotor amps (LRA) by 65–70%, allowing a smaller standby generator to start central AC without stalling.", "micro-air+easystart+soft+starter+for+air+conditioner")
        ]
    )
}

def inject():
    marker = '<section class="bundled-projects-section">'
    count = 0
    for filename, (heading, cards) in CALCULATOR_DATA.items():
        if not os.path.exists(filename):
            print(f"Skipping {filename}: not found.")
            continue
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'tag=nfagiolo-20' in content and 'Essential Equipment' in content:
            print(f"Skipping {filename}: already has hardware section.")
            continue
        if marker not in content:
            print(f"Warning: Marker missing in {filename}.")
            continue
        section_code = make_section(heading, cards)
        content = content.replace(marker, section_code + marker, 1)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Upgraded {filename}")
        count += 1
    print(f"Done. Upgraded {count} files.")

if __name__ == '__main__':
    inject()
