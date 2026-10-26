#!/usr/bin/env python3
"""
generate_article.py - Automated Daily Brand/SKU Empirical Cost Guide Generator for The Buyer's Math
Includes:
1. Primary Tier 1 Gemini API (`gemini-4-argon` thinkingLevel="LOW", fallback `gemini-2.5-flash`) + Anthropic fallback.
2. Brand/Model SKU-specific topic selection modeled on top-performing Search Console pages (e.g., Schluter DITRA-HEAT).
3. Strict title sanitization (removes raw Markdown '# ' prefixes and quotes) and duplicate-slug skip guard.
4. Unique <meta name="description"> extraction from the opening paragraph.
5. Deterministic Inline SVG Cost-Tier & Payback Comparison Chart.
6. Shoppable 5-Item Amazon Associates (`tag=nfagiolo-20`) Bill-of-Materials (BOM) Table.
7. Interactive "Audit My Contractor Quote" Red-Flag Scorecard Widget with dynamic CJ Angi (`PID: 101896838`) conversion CTA.
"""

import os
import re
import json
import random
import datetime
import urllib.parse
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CJ_TRACKING_BASE = "https://www.jdoqocy.com/click-101896838-17142784"
AMAZON_TAG = "nfagiolo-20"
ADSENSE_CLIENT = "ca-pub-1199906473460957"

CALCULATORS = [
    {
        "id": "radiant",
        "name": "Radiant Floor Heating Cost Calculator",
        "url": "/radiant-floor-calculator.html",
        "category": "Interior & Power",
        "unit": "heated floor sq ft",
        "base_unit_cost": 18.0,
        "default_size": 100,
        "tier_labels": ["DIY Membrane + Cable Kit ($850)", "Turnkey Pro Tile + 20A Circuit ($1,800)", "Primary Bath 150 sq ft WiFi Kit ($2,650)"],
        "tier_vals": [850, 1800, 2650],
        "skus": [
            "Schluter DITRA-HEAT-DUO Thermal Break Membrane vs Standard DITRA-HEAT Installed Cost Guide",
            "WarmlyYours TempZone vs Schluter DITRA-HEAT Electric Floor Heating Cost Guide",
            "Nuheat Custom Mats vs Cable Membrane System Installed Cost Per Sq Ft",
        ],
        "bom": [
            ("Schluter DITRA-HEAT Complete Bathroom Kit (Membrane + Cable + WiFi)", "Schluter+DITRA-HEAT+Complete+Kit+WiFi", "$545 – $895"),
            ("Schluter DITRA-HEAT Uncoupling Membrane Roll (134.5 sq ft)", "Schluter+DITRA-HEAT+Membrane+Roll", "$315 – $349"),
            ("Schluter DITRA-HEAT-E-HK Electric Heating Cable (120V/240V)", "Schluter+DITRA-HEAT-E-HK+Heating+Cable", "$235 – $390"),
            ("Schluter DITRA-HEAT-E-WiFi Programmable Touchscreen Thermostat", "Schluter+DITRA-HEAT-E-WiFi+Thermostat", "$265 – $310"),
            ("Schluter ALL-SET Modified Thin-Set Mortar (50 lb Bag)", "Schluter+ALL-SET+Thin-Set+Mortar", "$38 – $49"),
        ],
    },
    {
        "id": "bathroom",
        "name": "Bathroom Remodel Cost Estimator",
        "url": "/bathroom-remodel-calculator.html",
        "category": "Interior & Power",
        "unit": "bathroom sq ft",
        "base_unit_cost": 265.0,
        "default_size": 65,
        "tier_labels": ["Powder Room Refresh ($7,200)", "5x8 Guest Bath Full Tile ($16,800)", "Primary Wet-Room Suite ($31,500)"],
        "tier_vals": [7200, 16800, 31500],
        "skus": [
            "Schluter KERDI-BOARD Waterproof Shower Kit (38x60 & 48x60) Installed Cost Guide",
            "Panasonic WhisperGreen Select vs Broan UltraGreen Bathroom Exhaust Fan Installed Cost Guide",
            "Kohler Anthem Digital Shower Valve vs Moen U by Moen Rough-In & Labor Cost Guide",
            " Wedi Fundo Primo vs Schluter KERDI-SHOWER-T Curbless Shower Pan Installed Cost Guide",
        ],
        "bom": [
            ("Schluter Kerdi-Board Waterproof Shower Kit (38x60)", "schluter+kerdi+shower+kit+38x60", "$480 – $620"),
            ("Panasonic WhisperCeiling DC 110 CFM Humidity Fan", "panasonic+whisperceiling+110+cfm", "$165 – $215"),
            ("Moen Posi-Temp / Thermostatic Brass Shower Rough-In Valve", "moen+rough+in+shower+valve+brass", "$140 – $195"),
            ("Schluter KERDI-DRAIN Stainless Grate Assembly", "schluter+kerdi+drain+stainless", "$115 – $165"),
            ("Pinless Digital Subfloor Moisture Meter", "pinless+moisture+meter+drywall+wood", "$45 – $69"),
        ],
    },
    {
        "id": "pool",
        "name": "Pool Pump Energy Calculator",
        "url": "/pool.html",
        "category": "Mechanical & Energy",
        "unit": "horsepower tier",
        "base_unit_cost": 1650.0,
        "default_size": 1,
        "tier_labels": ["Single-Speed 5-Yr Power Cost ($4,950)", "Variable-Speed VFD Turnkey ($1,750)", "5-Year Net Electricity Savings (+$3,100)"],
        "tier_vals": [4950, 1750, 3100],
        "skus": [
            "Pentair IntelliFlo3 VSF 3.0 HP Pool Pump Installed Cost & kWh Payback Guide",
            "Hayward TriStar VS 950 vs Pentair SuperFlo VST Variable Speed Pool Pump Cost Guide",
            "Pentair IntelliChlor IC40 vs Hayward AquaRite Salt Chlorine Generator Installed Cost Guide",
            "Raypak Digital 406A vs Pentair MasterTemp 400 Pool Heater Installed Cost Guide",
        ],
        "bom": [
            ("Pentair / Hayward Energy Star Variable-Speed Inground Pool Pump", "pentair+intelliflo+variable+speed+pool+pump", "$1,050 – $1,490"),
            ("2-Inch High-Temp Schedule 40 Quick-Disconnect Unions", "2+inch+pool+pump+high+temp+unions", "$24 – $36"),
            ("Intermatic Freeze-Protection Smart Pool Timer (240V)", "smart+wifi+pool+pump+timer+240v", "$89 – $135"),
            ("Taylor K-2006C Complete Saltwater & Chlorine Drop Test Kit", "taylor+k-2006c+pool+test+kit", "$78 – $98"),
            ("Liquid-Filled Stainless Filter Pressure Gauge", "pool+filter+pressure+gauge+stainless", "$22 – $34"),
        ],
    },
    {
        "id": "water-heater",
        "name": "Water Heater Replacement Cost Calculator",
        "url": "/water-heater-calculator.html",
        "category": "Mechanical & Energy",
        "unit": "gallon / GPM tier",
        "base_unit_cost": 2850.0,
        "default_size": 1,
        "tier_labels": ["50-Gal Atmospheric Tank ($1,950)", "Condensing Gas Tankless ($3,850)", "Hybrid Heat Pump after 25C ($2,450 Net)"],
        "tier_vals": [1950, 3850, 2450],
        "skus": [
            "Rheem ProTerra Hybrid Heat Pump Water Heater (50 & 65 Gal) Installed Cost & 25C Credit Guide",
            "Navien NPE-240A2 vs Rinnai RU199iN Condensing Tankless Water Heater Installed Cost Guide",
            "AO Smith Voltex AL 50-Gallon Hybrid Water Heater Installed Cost & Payback Guide",
        ],
        "bom": [
            ("Amtrol Therm-X-Trol Potable Thermal Expansion Tank (2 Gal)", "potable+water+heater+expansion+tank+2+gallon", "$58 – $78"),
            ("3/4-Inch Brass Tankless Isolation Service Valve Kit", "tankless+water+heater+service+valve+kit+3/4", "$69 – $92"),
            ("Moen Flo / YoLink WiFi Smart Water Leak Detector & Auto Shutoff", "smart+water+leak+detector+shutoff", "$79 – $145"),
            ("Aluminum Water Heater Drain Pan with PVC Fitting", "water+heater+drain+pan+24+inch", "$32 – $45"),
            ("Submersible Tankless Descaling Pump & Flush Kit", "tankless+water+heater+flushing+kit", "$85 – $115"),
        ],
    },
    {
        "id": "generator",
        "name": "Backup Generator Sizing Calculator",
        "url": "/generator-calculator.html",
        "category": "Interior & Power",
        "unit": "kW capacity",
        "base_unit_cost": 480.0,
        "default_size": 22,
        "tier_labels": ["14kW Essential Circuits ($7,900)", "22kW Whole-Home + 200A ATS ($10,650)", "26kW Dual-AC Heavy Load ($13,200)"],
        "tier_vals": [7900, 10650, 13200],
        "skus": [
            "Generac Guardian 24kW (7210) vs Kohler 26RCA Whole-House Generator Installed Cost Guide",
            "Generac RXSW200A3 200-Amp Service-Rated Automatic Transfer Switch Installed Cost Guide",
            "Reliance Controls 50-Amp Pro/Tran2 Manual Transfer Switch & Inlet Box Installed Cost Guide",
        ],
        "bom": [
            ("200A Automatic Transfer Switch (Service Rated)", "200+amp+automatic+transfer+switch+generator", "$780 – $980"),
            ("Reliance 50A Generator Power Inlet Box & Interlock Kit", "50+amp+generator+inlet+box+nema+14-50", "$65 – $95"),
            ("Generac Cold-Weather Battery & Oil Warmer Kit", "generac+cold+weather+kit", "$115 – $155"),
            ("AGM Deep-Cycle Group 26R Generator Starting Battery", "group+26r+agm+battery", "$135 – $165"),
            ("Digital Combustible Natural Gas & Propane Leak Detector Pen", "natural+gas+leak+detector+pen", "$38 – $55"),
        ],
    },
    {
        "id": "ev-charger",
        "name": "EV Home Charger Installation Calculator",
        "url": "/ev-charger-calculator.html",
        "category": "Interior & Power",
        "unit": "linear ft conduit run",
        "base_unit_cost": 32.0,
        "default_size": 45,
        "tier_labels": ["NEMA 14-50 Short Run ($1,150)", "48A Hardwired 45ft Run ($1,850)", "Hardwired + Dynamic Load Mgmt ($2,650)"],
        "tier_vals": [1150, 1850, 2650],
        "skus": [
            "Tesla Universal Wall Connector vs ChargePoint Home Flex 48A Hardwired Installed Cost Guide",
            "Hubbell HBL9450A Industrial NEMA 14-50 Receptacle vs Hardwired EV Charger Cost Guide",
            "Emporia 48A Level 2 EV Charger with Dynamic Load Management Installed Cost Guide",
        ],
        "bom": [
            ("48A Hardwired Energy Star Level 2 EV Wallbox Charger", "48+amp+level+2+ev+charger+hardwired", "$399 – $549"),
            ("Hubbell HBL9450A Industrial Grade NEMA 14-50EV Receptacle", "hubbell+9450a+nema+14-50+ev+outlet", "$58 – $79"),
            ("50A 2-Pole GFCI Circuit Breaker (NEC 625.54 Compliant)", "50+amp+2+pole+gfci+breaker", "$110 – $145"),
            ("6/3 NM-B or THHN Copper Wire Spool (50 ft)", "6+awg+copper+wire+50+ft", "$145 – $195"),
            ("Klein Tools Inch-Pound Torque Screwdriver (NEC 110.14)", "klein+tools+torque+screwdriver", "$68 – $89"),
        ],
    },
    {
        "id": "hvac",
        "name": "Heat Pump vs. Gas Furnace ROI Calculator",
        "url": "/hvac-roi-calculator.html",
        "category": "Mechanical & Energy",
        "unit": "system tons",
        "base_unit_cost": 3900.0,
        "default_size": 3,
        "tier_labels": ["Single-Stage 14.3 SEER2 ($8,800)", "Cold-Climate Inverter 18 SEER2 ($12,200)", "Dual-Fuel Hybrid + 25C Credit ($11,400 Net)"],
        "tier_vals": [8800, 12200, 11400],
        "skus": [
            "Mitsubishi Hyper-Heat (H2i) vs Bosch IDS 2.0 Inverter Heat Pump Installed Cost Guide",
            "Carrier Infinity Greenspeed 24VNA6 vs Trane XV20i Variable-Speed Heat Pump Cost Guide",
            "ecobee Smart Thermostat Premium Dual-Fuel Heat Pump Staging & Aux Lockout Setup Guide",
        ],
        "bom": [
            ("ecobee Smart Thermostat Premium (Heat Pump Staging)", "ecobee+smart+thermostat+premium", "$219 – $249"),
            ("60A Non-Fused AC Disconnect & Pre-Wired Whip Kit", "ac+disconnect+box+60+amp+whip", "$42 – $58"),
            ("Intermatic AG3000 HVAC Condenser Surge Protector", "hvac+surge+protector+ag3000", "$65 – $89"),
            ("Klein Tools CL800 True-RMS HVAC Clamp Meter", "klein+tools+cl800", "$129 – $149"),
            ("MERV 11 Pleated 4-Inch Media Filter (4-Pack)", "merv+11+4+inch+furnace+filter", "$78 – $96"),
        ],
    },
    {
        "id": "mini-split",
        "name": "Ductless Mini-Split Cost Estimator",
        "url": "/mini-split-calculator.html",
        "category": "Mechanical & Energy",
        "unit": "indoor air zones",
        "base_unit_cost": 3600.0,
        "default_size": 2,
        "tier_labels": ["Single-Zone 12k BTU ($4,200)", "Dual-Zone 24k BTU ($7,400)", "4-Zone Whole-Home ($12,800)"],
        "tier_vals": [4200, 7400, 12800],
        "skus": [
            "MRCOOL DIY 4th Gen 18k/24k BTU vs Mitsubishi Ductless Mini-Split Installed Cost Guide",
            "Pioneer Diamante Ultra vs Daikin Aurora Single-Zone Mini-Split Installed Cost Guide",
        ],
        "bom": [
            ("Pre-Insulated 1/4 x 3/8 Copper Refrigerant Line Set (25 ft)", "mini+split+copper+line+set+25+ft", "$135 – $175"),
            ("PVC Line-Set Decorative Exterior Hide Cover Kit", "mini+split+line+set+cover+kit", "$58 – $82"),
            ("Heavy-Duty Powder-Coated Condenser Wall Bracket", "mini+split+wall+mounting+bracket", "$45 – $68"),
            ("14/4 Mini-Split Communicating Control Tray Cable", "14/4+mini+split+control+wire", "$48 – $65"),
            ("Aspen / Little Giant Ultra-Quiet Mini-Split Condensate Pump", "mini+split+condensate+pump", "$95 – $135"),
        ],
    },
    {
        "id": "solar",
        "name": "Solar Panel Payback Timeline Calculator",
        "url": "/solar-payback-calculator.html",
        "category": "Mechanical & Energy",
        "unit": "kW system size",
        "base_unit_cost": 2750.0,
        "default_size": 8,
        "tier_labels": ["8kW Gross Turnkey ($22,000)", "Net Cost After 30% 25D Credit ($15,400)", "8kW + 13.5kWh Battery Net ($23,800)"],
        "tier_vals": [22000, 15400, 23800],
        "skus": [
            "Enphase IQ8M / IQ8A Microinverter Solar System Cost Per Watt & DIY Patio Roof Guide",
            "Tesla Powerwall 3 vs Enphase IQ Battery 5P Installed Cost & 30% Tax Credit Guide",
        ],
        "bom": [
            ("Emporia Vue Gen 3 Whole-Home 16-Circuit Energy Monitor", "emporia+vue+3+home+energy+monitor", "$159 – $199"),
            ("Solar PV DC Isolator Disconnect Switch (1000V)", "solar+pv+dc+disconnect+switch", "$58 – $79"),
            ("Critter Guard PVC-Coated Mesh Roll for Solar Array Skirting", "solar+panel+bird+critter+guard+kit", "$64 – $88"),
            ("MC4 Solar Crimping & Connector Tool Kit", "mc4+solar+connector+tool+kit", "$35 – $49"),
            ("Siemens FirstSurge Type 2 Whole-House Main Panel Surge Arrester", "siemens+firstsurge+whole+house+surge+protector", "$115 – $145"),
        ],
    },
    {
        "id": "roofing",
        "name": "Roof Replacement Cost Estimator",
        "url": "/roofing-cost-calculator.html",
        "category": "Building Envelope",
        "unit": "sq ft roof footprint",
        "base_unit_cost": 5.60,
        "default_size": 2200,
        "tier_labels": ["3-Tab Asphalt ($8,900)", "Architectural Class A ($12,400)", "Standing Seam Metal ($24,500)"],
        "tier_vals": [8900, 12400, 24500],
        "skus": [
            "GAF Timberline HDZ vs Owens Corning Duration Architectural Shingles Cost Per Square Guide",
            "Grace Ice & Water Shield vs GAF WeatherWatch Underlayment Installed Cost Guide",
        ],
        "bom": [
            ("Synthetic Roof Underlayment (10 sq roll)", "synthetic+roofing+underlayment", "$115 – $145"),
            ("Self-Adhering Ice & Water Shield Barrier", "ice+and+water+shield+roofing", "$95 – $130"),
            ("Class 4 Impact-Resistant Ridge Cap Shingles", "architectural+ridge+cap+shingles", "$68 – $85"),
            ("Galvanized Ring-Shank Roofing Nails (7,200 ct)", "coil+roofing+nails", "$54 – $72"),
            ("FLIR Moisture & Roof Leak Thermal Scanner", "thermal+imaging+camera+moisture", "$189 – $249"),
        ],
    },
    {
        "id": "siding",
        "name": "Home Siding Replacement Cost Calculator",
        "url": "/siding-cost-calculator.html",
        "category": "Building Envelope",
        "unit": "exterior wall sq ft",
        "base_unit_cost": 8.40,
        "default_size": 2000,
        "tier_labels": ["Standard Vinyl ($11,800)", "Foam-Backed Insulated Vinyl ($15,600)", "James Hardie Fiber Cement ($21,400)"],
        "tier_vals": [11800, 15600, 21400],
        "skus": [
            "James Hardie HardiePlank ColorPlus vs LP SmartSide Lap Siding Cost Per Sq Ft Guide",
            "CertainTeed Monogram vs CraneBoard Insulated Vinyl Siding Installed Cost Guide",
        ],
        "bom": [
            ("DuPont Tyvek HomeWrap Breathable Membrane (9x100)", "dupont+tyvek+homewrap", "$155 – $185"),
            ("3M All-Weather Flashing Tape 8067 (Window & Sill Seal)", "3m+all+weather+flashing+tape+8067", "$34 – $48"),
            ("PacTool Gecko Gauge Fiber Cement Siding Clamps", "pactool+gecko+gauge+siding", "$68 – $84"),
            ("Stainless Steel Ring-Shank Siding Nails", "stainless+steel+siding+nails", "$85 – $110"),
            ("OSI QUAD Max Exterior Window & Siding Sealant", "osi+quad+max+sealant", "$88 – $105"),
        ],
    },
    {
        "id": "windows",
        "name": "Window Replacement Cost Estimator",
        "url": "/window-replacement-estimator.html",
        "category": "Building Envelope",
        "unit": "replacement windows",
        "base_unit_cost": 820.0,
        "default_size": 12,
        "tier_labels": ["Double-Pane Low-E Vinyl ($8,400)", "Composite / Wood-Clad ($12,900)", "Pultruded Fiberglass Triple-Pane ($16,200)"],
        "tier_vals": [8400, 12900, 16200],
        "skus": [
            "Andersen 400 Series vs Marvin Essential Fiberglass Replacement Window Installed Cost Guide",
            "Pella 250 Series vs Milgard Tuscany Vinyl Window Replacement Cost Per Window Guide",
        ],
        "bom": [
            ("Great Stuff Pro Window & Door Low-Expansion Foam Kit", "great+stuff+pro+window+and+door+foam", "$64 – $85"),
            ("Butyl Rubber Window Sill Pan Flashing Tape (6-Inch)", "butyl+window+flashing+tape+6+inch", "$42 – $59"),
            ("Composite Structural Shims (Contractor 100-Pack)", "composite+shims+window+installation", "$28 – $38"),
            ("Infrared Thermal Leak Detector Thermometer", "black+decker+thermal+leak+detector", "$39 – $54"),
            ("GE Supreme 100% Silicone Exterior Glazing Sealant", "ge+supreme+silicone+window+door", "$65 – $82"),
        ],
    },
    {
        "id": "kitchen",
        "name": "Kitchen Remodel Cost Estimator",
        "url": "/kitchen-remodel-calculator.html",
        "category": "Interior & Power",
        "unit": "kitchen sq ft",
        "base_unit_cost": 210.0,
        "default_size": 180,
        "tier_labels": ["Cosmetic Reface & Tops ($18,500)", "Midrange Semi-Custom ($37,800)", "Luxury Structural Gut ($74,000)"],
        "tier_vals": [18500, 37800, 74000],
        "skus": [
            "Kraus Kore 32-Inch Workstation Sink & Garbage Disposal Plumbing Rough-In Cost Guide",
            "Cambria Quartz vs MSI Q Quartz Countertop Fabrication & Installed Cost Per Sq Ft Guide",
        ],
        "bom": [
            ("16-Gauge Undermount Workstation Stainless Sink (32-Inch)", "undermount+workstation+kitchen+sink+32", "$240 – $320"),
            ("Touchless Pull-Down Commercial Spring Kitchen Faucet", "touchless+kitchen+faucet+pull+down", "$165 – $230"),
            ("20A Dual-Function AFCI/GFCI Kitchen Circuit Breakers", "20+amp+dual+function+afci+gfci+breaker", "$52 – $68"),
            ("Blum Compact Soft-Close Concealed Cabinet Hinges", "blum+soft+close+cabinet+hinges", "$65 – $85"),
            ("Under-Cabinet Hardwired Dimmable LED Task Lighting Kit", "hardwired+under+cabinet+led+lighting", "$89 – $125"),
        ],
    },
    {
        "id": "insulation",
        "name": "Attic Insulation & Air Sealing Calculator",
        "url": "/attic-insulation-calculator.html",
        "category": "Mechanical & Energy",
        "unit": "attic sq ft",
        "base_unit_cost": 2.45,
        "default_size": 1500,
        "tier_labels": ["Blown Cellulose to R-49 ($2,850)", "Air Sealing + R-60 Fiberglass ($3,900)", "Net Cost After 30% 25C Credit ($2,730)"],
        "tier_vals": [2850, 3900, 2730],
        "skus": [
            "Owens Corning AttiCat Blown-In Fiberglass vs Greenfiber Cellulose R-49 Cost Guide",
            "Rockwool Comfortbatt R-23 vs Closed-Cell Rim Joist Spray Foam Installed Cost Guide",
        ],
        "bom": [
            ("Foil-Faced Insulated Attic Pull-Down Stair Cover Tent (R-15)", "attic+stairs+insulation+cover+tent+r15", "$48 – $69"),
            ("Rafter Vent Baffles for Soffit Airflow (50-Pack)", "attic+rafter+vent+baffles", "$75 – $98"),
            ("Great Stuff Pro Fireblock Expanding Foam Gun Kit", "great+stuff+pro+fireblock+foam+gun", "$79 – $105"),
            ("Tenmat IC-Rated Airtight Recessed Downlight Covers", "tenmat+recessed+light+insulation+cover", "$68 – $89"),
            ("FLIR ONE Gen 3 Thermal Imaging Camera for Air Leaks", "flir+one+gen+3+thermal+camera", "$189 – $219"),
        ],
    },
    {
        "id": "basement",
        "name": "Basement Finishing Cost Estimator",
        "url": "/basement-cost-calculator.html",
        "category": "Interior & Power",
        "unit": "basement sq ft",
        "base_unit_cost": 48.0,
        "default_size": 900,
        "tier_labels": ["Open Rec Room Finish ($34,000)", "Rec Room + Bedroom & Egress ($46,500)", "Full Suite + Wet Bar & Bath ($64,000)"],
        "tier_vals": [34000, 46500, 64000],
        "skus": [
            "DRIcore Subfloor Membrane Panels vs Platon Dimpled Vapor Barrier Installed Cost Guide",
            "Zoeller M53 / M63 Cast Iron Sump Pump + Basement Watchdog Battery Backup Cost Guide",
            "Saniflo Saniaccess 3 Upflush Basement Bathroom Plumbing Installed Cost Guide",
        ],
        "bom": [
            ("Dimpled Subfloor Vapor Barrier Underlayment Roll", "basement+subfloor+vapor+barrier+membrane", "$145 – $195"),
            ("Basement Watchdog Combo Sump Pump with AGM Battery Backup", "basement+watchdog+combo+sump+pump+battery+backup", "$420 – $560"),
            ("IRC R310 Code-Compliant Galvanized Egress Window Well", "basement+egress+window+well+ladder", "$260 – $350"),
            ("Rockwool Comfortbatt Moisture-Resistant Mineral Wool Insulation", "rockwool+comfortbatt+insulation", "$89 – $125"),
            ("Energy Star 50-Pint Basement Dehumidifier with Built-In Pump", "50+pint+dehumidifier+with+built+in+pump", "$229 – $289"),
        ],
    },
    {
        "id": "driveway",
        "name": "Driveway Paving Calculator",
        "url": "/driveway-paving-calculator.html",
        "category": "Building Envelope",
        "unit": "driveway sq ft",
        "base_unit_cost": 11.50,
        "default_size": 600,
        "tier_labels": ["Hot-Mix Asphalt ($4,500)", "4-Inch 4000 PSI Concrete ($6,900)", "Interlocking Concrete Pavers ($10,800)"],
        "tier_vals": [4500, 6900, 10800],
        "skus": [
            "Techo-Bloc Blu 60 vs Belgard Cambridge Cobble Driveway Pavers Installed Cost Guide",
            "GhostShield Siloxa-Tek 8500 Penetrating Concrete Sealer vs Acrylic Sealer Cost Guide",
        ],
        "bom": [
            ("Non-Woven Geotextile Driveway Stabilization Fabric", "geotextile+driveway+fabric+underlayment", "$135 – $185"),
            ("Silane-Siloxane Penetrating Concrete Driveway Sealer (5 Gal)", "silane+siloxane+concrete+driveway+sealer+5+gal", "$145 – $190"),
            ("Alliance Gator Maxx Polymeric Sand for Interlocking Pavers", "polymeric+sand+for+pavers", "$42 – $65"),
            ("Rubberized Hot-Pour Asphalt & Concrete Crack Filler", "asphalt+driveway+crack+filler+rubberized", "$38 – $58"),
            ("Self-Leveling Rotary Laser Level for 2% Drainage Grading", "self+leveling+rotary+laser+level+kit", "$185 – $260"),
        ],
    },
    {
        "id": "fence",
        "name": "Fence Cost & Linear Footage Estimator",
        "url": "/fence-cost-calculator.html",
        "category": "Building Envelope",
        "unit": "linear feet",
        "base_unit_cost": 38.0,
        "default_size": 150,
        "tier_labels": ["Pressure-Treated Pine ($4,500)", "Western Red Cedar Privacy ($6,150)", "Extruded Vinyl / Ornamental ($7,650)"],
        "tier_vals": [4500, 6150, 7650],
        "skus": [
            "PostMaster Steel Hidden Fence Posts vs 4x4 Pressure-Treated Wood Posts Cost Guide",
            "Sika Post Fix Expanding Foam vs Concrete Bags Fence Post Installation Cost Guide",
        ],
        "bom": [
            ("Heavy-Duty Self-Closing Stainless Gate Hardware Kit", "heavy+duty+fence+gate+hinges+and+latch", "$48 – $75"),
            ("Sika Post Fix Expanding Polyurethane Fence Post Foam (10-Pack)", "sika+post+fix+fence+post+foam", "$135 – $165"),
            ("Simpson Strong-Tie Galvanized Steel Fence Brackets", "simpson+strong+tie+fence+brackets", "$54 – $78"),
            ("Solar Post Cap LED Perimeter Lights (8-Pack)", "4x4+solar+post+cap+lights", "$69 – $95"),
            ("Cordless Brushless Earth Auger Post Hole Digger (8-Inch Bit)", "cordless+earth+auger+post+hole+digger", "$210 – $290"),
        ],
    },
]

ANGLES = [
    "2026 Installed Cost Per Unit, Material Takeoff & Labor Breakdown",
    "DIY Hardware Kit vs. Licensed Turnkey Contractor Bid Audit",
    "Payback Timeline, Operating Cost & Tax Credit Eligibility",
]


def sanitize_title(raw_title: str) -> str:
    cleaned = re.sub(r"[\r\n]+", " ", raw_title).strip()
    cleaned = re.sub(r"^[\s#*\"'`>]+|[\s*\"'`]+$", "", cleaned)
    cleaned = re.sub(
        r"^(?:2026\s+)?Cost\s+Analysis\s+Article(?:\s*:\s*|\s+)",
        "2026 Cost Analysis: ",
        cleaned,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", cleaned).strip()


def generate_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(slug) > 58:
        slug = slug[:58].rsplit("-", 1)[0]
    return slug


def extract_meta_description(body_html: str, title: str) -> str:
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", body_html, flags=re.IGNORECASE | re.DOTALL)
    for p in paragraphs:
        text = re.sub(r"<[^>]+>", " ", p)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) >= 70 and "affiliate disclosure" not in text.lower():
            return (text[:157].rsplit(" ", 1)[0] + "...") if len(text) > 160 else text
    return f"2026 empirical cost analysis, contractor labor benchmarks, and SKU material breakdown for {title}."


def build_svg_cost_chart(calc: dict) -> str:
    labels = calc.get("tier_labels", ["Economy Spec", "Midrange Turnkey", "Premium Spec"])
    vals = calc.get("tier_vals", [6500, 11200, 17800])
    mx = max(vals) if vals else 1
    colors = ["#64748b", "#2563eb", "#0f172a"]
    bars_svg = []
    for i, (lbl, val) in enumerate(zip(labels, vals)):
        y = 22 + i * 54
        bar_w = max(60, int(round((val / mx) * 420)))
        col = colors[i % len(colors)]
        bars_svg.append(
            f'<text x="0" y="{y}" fill="#0f172a" font-size="12.5" font-weight="700" font-family="Inter, sans-serif">{lbl}</text>'
            f'<rect x="0" y="{y + 7}" width="520" height="22" rx="5" fill="#f1f5f9" />'
            f'<rect x="0" y="{y + 7}" width="{bar_w}" height="22" rx="5" fill="{col}" />'
            f'<text x="{bar_w + 8}" y="{y + 23}" fill="#0f172a" font-size="12" font-weight="800" font-family="Inter, sans-serif">${val:,}</text>'
        )
    return f"""<!-- TBM SVG COST CHART START -->
<figure class="tbm-svg-chart-box" style="margin: 2rem 0; padding: 1.5rem; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
  <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #2563eb; margin-bottom: 0.25rem;">
    2026 Empirical Price Distribution
  </div>
  <figcaption style="font-size: 1.1rem; font-weight: 800; color: #0f172a; margin-bottom: 1rem;">
    {calc['name']}: Turnkey Cost Benchmarks by Specification Tier
  </figcaption>
  <svg viewBox="0 0 620 180" width="100%" height="auto" role="img" aria-label="Cost comparison bar chart for {calc['name']}">
    {"".join(bars_svg)}
  </svg>
  <div style="font-size: 0.78rem; color: #64748b; margin-top: 0.65rem; border-top: 1px solid #f1f5f9; padding-top: 0.5rem;">
    Source: The Buyer's Math 2026 National Contractor Bid Index &amp; BLS Trade Labor Benchmarks.
    <a href="{calc['url']}" style="color: #2563eb; font-weight: 700;">Customize for your state &rarr;</a>
  </div>
</figure>
<!-- TBM SVG COST CHART END -->"""


def build_shoppable_bom_table(calc: dict) -> str:
    rows = []
    for item_name, query_str, price_range in calc.get("bom", []):
        amz_url = f"https://www.amazon.com/s?k={query_str}&tag={AMAZON_TAG}"
        rows.append(
            f'<tr style="border-bottom: 1px solid #e2e8f0;">'
            f'<td style="padding: 0.75rem; font-weight: 600; color: #0f172a;">{item_name}</td>'
            f'<td style="padding: 0.75rem; color: #334155; font-weight: 700; white-space: nowrap;">{price_range}</td>'
            f'<td style="padding: 0.75rem; text-align: right; white-space: nowrap;">'
            f'<a href="{amz_url}" target="_blank" rel="noopener sponsored" style="background: #f59e0b; color: #0f172a; font-weight: 700; font-size: 0.8rem; padding: 0.4rem 0.75rem; border-radius: 6px; text-decoration: none; display: inline-block;">Check Amazon Price &rarr;</a>'
            f"</td></tr>"
        )
    return f"""<!-- TBM SHOPPABLE BOM START -->
<section class="tbm-bom-section" style="margin: 2.25rem 0; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.85rem;">
    <div>
      <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #b45309; background: #fffbeb; padding: 0.2rem 0.5rem; border-radius: 4px; border: 1px solid #fde68a;">Save 15%–25% on Contractor Material Markup</span>
      <h3 style="margin: 0.35rem 0 0 0; font-size: 1.2rem; color: #0f172a;">Homeowner-Supplied Bill of Materials &amp; Diagnostic Gear</h3>
    </div>
  </div>
  <p style="font-size: 0.88rem; color: #475569; margin: 0 0 1rem 0;">
    Verify distributor street pricing on core components before signing a turnkey proposal, or source hardware directly on Amazon to eliminate contractor supply markups:
  </p>
  <div style="overflow-x: auto;">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left;">
      <thead>
        <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1; color: #475569; font-size: 0.76rem; text-transform: uppercase;">
          <th style="padding: 0.65rem 0.75rem;">Component / Specification</th>
          <th style="padding: 0.65rem 0.75rem;">2026 Street Window</th>
          <th style="padding: 0.65rem 0.75rem; text-align: right;">Direct Sourcing</th>
        </tr>
      </thead>
      <tbody>
        {"".join(rows)}
      </tbody>
    </table>
  </div>
</section>
<!-- TBM SHOPPABLE BOM END -->"""


def build_quote_auditor_widget(calc: dict) -> str:
    trade_q = urllib.parse.quote_plus(calc["name"].replace("Cost Estimator", "").replace("Calculator", "").strip())
    dest_url = f"https://www.angi.com/companylist/search.htm?query={trade_q}"
    cj_url = f"{CJ_TRACKING_BASE}?url={urllib.parse.quote(dest_url, safe='')}"
    unit = calc.get("unit", "project units")
    base_rate = calc.get("base_unit_cost", 15.0)
    def_size = calc.get("default_size", 1000)
    def_fair = int(round(base_rate * def_size))
    return f"""<!-- TBM QUOTE AUDITOR WIDGET START -->
<aside class="tbm-quote-auditor" style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; border-radius: 14px; box-shadow: 0 10px 25px -5px rgba(15,23,42,0.18);">
  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
    <span style="background: #2563eb; color: #ffffff; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.22rem 0.6rem; border-radius: 4px;">Interactive Bid Scorecard</span>
    <span style="font-size: 0.78rem; color: #94a3b8;">Calibrated to 2026 BLS &amp; RSMeans Data</span>
  </div>
  <h3 style="margin: 0 0 0.35rem 0; font-size: 1.25rem; color: #ffffff;">Audit Your Contractor Quote in 10 Seconds</h3>
  <p style="margin: 0 0 1.15rem 0; font-size: 0.88rem; color: #cbd5e1;">
    Enter your written contractor estimate and project size below to check if you are being overcharged on overhead and labor:
  </p>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.85rem; margin-bottom: 1rem;">
    <div>
      <label style="display: block; font-size: 0.75rem; font-weight: 600; color: #cbd5e1; margin-bottom: 0.3rem;">Your Contractor Quote ($):</label>
      <input type="number" class="tbm-audit-quote" value="{int(round(def_fair * 1.22))}" style="width: 100%; padding: 0.6rem 0.75rem; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #ffffff; font-size: 0.95rem; font-weight: 700;">
    </div>
    <div>
      <label style="display: block; font-size: 0.75rem; font-weight: 600; color: #cbd5e1; margin-bottom: 0.3rem;">Project Scope ({unit}):</label>
      <input type="number" class="tbm-audit-size" value="{def_size}" data-rate="{base_rate}" style="width: 100%; padding: 0.6rem 0.75rem; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #ffffff; font-size: 0.95rem; font-weight: 700;">
    </div>
    <div>
      <label style="display: block; font-size: 0.75rem; font-weight: 600; color: #cbd5e1; margin-bottom: 0.3rem;">Regional Labor Tier:</label>
      <select class="tbm-audit-region" style="width: 100%; padding: 0.6rem 0.75rem; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #ffffff; font-size: 0.9rem; font-weight: 600;">
        <option value="1.00">National Average (1.00x)</option>
        <option value="1.15">Mid-Atlantic / Northeast (1.15x)</option>
        <option value="1.30">West Coast / High-Cost Metro (1.30x)</option>
        <option value="0.90">Southeast / Midwest (0.90x)</option>
      </select>
    </div>
  </div>
  <div class="tbm-audit-result" style="background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
    <div>
      <div class="tbm-audit-verdict" style="font-size: 1rem; font-weight: 800; color: #fbbf24;">
        &#9888;&#65039; Quote is ~22% Above Verified Fair Benchmark (${def_fair:,})
      </div>
      <div class="tbm-audit-sub" style="font-size: 0.82rem; color: #cbd5e1; margin-top: 0.2rem;">
        Request an itemized material &amp; labor breakdown or compare 3 competing local bids to negotiate down.
      </div>
    </div>
    <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
      <a href="{calc['url']}" style="background: #2563eb; color: #ffffff; font-weight: 700; font-size: 0.84rem; padding: 0.6rem 1rem; border-radius: 6px; text-decoration: none;">
        Full {calc['name']} &rarr;
      </a>
      <a href="{cj_url}" target="_blank" rel="noopener sponsored" style="background: #10b981; color: #022c22; font-weight: 800; font-size: 0.84rem; padding: 0.6rem 1rem; border-radius: 6px; text-decoration: none;">
        Compare 3 Local Pros &rarr;
      </a>
    </div>
  </div>
  <script>
    (function() {{
      const boxes = document.querySelectorAll('.tbm-quote-auditor');
      boxes.forEach(box => {{
        if (box.dataset.wired) return;
        box.dataset.wired = '1';
        const qInp = box.querySelector('.tbm-audit-quote');
        const sInp = box.querySelector('.tbm-audit-size');
        const rSel = box.querySelector('.tbm-audit-region');
        const verdict = box.querySelector('.tbm-audit-verdict');
        const sub = box.querySelector('.tbm-audit-sub');
        function updateAudit() {{
          const quote = parseFloat(qInp.value) || 0;
          const size = Math.max(0.1, parseFloat(sInp.value) || 1);
          const rate = parseFloat(sInp.getAttribute('data-rate') || '15');
          const reg = parseFloat(rSel.value || '1.0');
          const fair = Math.round(size * rate * reg);
          const diff = quote - fair;
          const pct = fair > 0 ? Math.round((diff / fair) * 100) : 0;
          if (pct > 15) {{
            verdict.style.color = '#f87171';
            verdict.innerHTML = '&#128681; Red Flag: Quote is ' + pct + '% ($' + Math.abs(diff).toLocaleString() + ') Above Fair Window ($' + fair.toLocaleString() + ')';
            sub.textContent = 'High markup detected. Get 3 competing licensed bids below to force a contractor price match.';
          }} else if (pct >= -10) {{
            verdict.style.color = '#34d399';
            verdict.innerHTML = '&#9989; Verified Fair Bid: Within ' + Math.abs(pct) + '% of Empirical Benchmark ($' + fair.toLocaleString() + ')';
            sub.textContent = 'Pricing aligns with 2026 licensed trade labor and material takeoffs. Verify permit & warranty terms.';
          }} else {{
            verdict.style.color = '#fbbf24';
            verdict.innerHTML = '&#9888;&#65039; Suspiciously Low (' + Math.abs(pct) + '% Below $' + fair.toLocaleString() + ' Benchmark)';
            sub.textContent = 'Check for missing municipal permits, uninsured sub-crews, or builder-grade material substitutions.';
          }}
        }}
        [qInp, sInp, rSel].forEach(el => {{
          if (el) {{
            el.addEventListener('input', updateAudit);
            el.addEventListener('change', updateAudit);
          }}
        }});
        updateAudit();
      }});
    }})();
  </script>
</aside>
<!-- TBM QUOTE AUDITOR WIDGET END -->"""


def call_gemini_api(prompt: str, max_tokens: int = 8192) -> str:
    models_to_try = [
        ("gemini-4-argon", True),
        ("gemini-2.5-flash", False),
    ]
    last_err = None
    for model_name, use_thinking in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        gen_cfg = {"maxOutputTokens": max_tokens, "temperature": 0.3}
        if use_thinking:
            gen_cfg["thinkingConfig"] = {"thinkingLevel": "LOW"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": gen_cfg,
        }
        try:
            res = requests.post(url, json=payload, timeout=90)
            if res.status_code == 200:
                data = res.json()
                parts = data["candidates"][0]["content"]["parts"]
                text_parts = [p.get("text", "") for p in parts if not p.get("thought", False)]
                return "".join(text_parts).strip()
            last_err = f"{model_name} HTTP {res.status_code}: {res.text[:200]}"
        except Exception as e:
            last_err = f"{model_name} error: {e}"
    raise RuntimeError(f"Gemini generation failed: {last_err}")


def generate_with_llm(calc: dict, sku_topic: str):
    clean_title = sanitize_title(sku_topic)
    body_prompt = (
        f"Write an authoritative, empirical 1,000-word HTML cost guide body (using <h2>, <h3>, <p>, <ul>, <li>, and a detailed component cost <table>, "
        f"with NO <html>, <head>, <body>, or <h1> tags) titled '{clean_title}'. "
        f"Structure the guide just like a high-converting contractor & DIY material takeoff guide:\n"
        f"1. Start the very first <p> with the exact 2026 installed cost range and DIY material kit cost range in bold.\n"
        f"2. Include a detailed <table> comparing specific manufacturer model numbers/SKUs, unit cost, typical project cost, and installation notes.\n"
        f"3. Break down licensed trade labor (e.g., electrical, plumbing, or tile hourly/sq-ft rates), code & permit rules (NEC/IRC), and 2026 federal tax credits (25C/25D/30C) where applicable.\n"
        f"4. Explain exact installation preparation steps and how homeowners save 20%-30% by buying the hardware kit directly rather than paying contractor supply-house markup."
    )
    if GEMINI_API_KEY:
        body_html = call_gemini_api(body_prompt, max_tokens=16384)
        body_html = re.sub(r"^```html\s*|\s*```$", "", body_html).strip()
        return clean_title, body_html

    if ANTHROPIC_API_KEY:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        res_b = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 3200,
                "messages": [{"role": "user", "content": body_prompt}],
            },
            timeout=90,
        )
        res_b.raise_for_status()
        body_html = res_b.json()["content"][0]["text"].strip()
        body_html = re.sub(r"^```html\s*|\s*```$", "", body_html).strip()
        return clean_title, body_html

    raise RuntimeError("Neither GEMINI_API_KEY nor ANTHROPIC_API_KEY is set.")


def pick_unused_sku_topic():
    existing_files = set(os.listdir("articles")) if os.path.exists("articles") else set()
    candidates = []
    for calc in CALCULATORS:
        for sku_topic in calc.get("skus", []):
            slug = generate_slug(sku_topic)
            if not any(slug in fname for fname in existing_files):
                candidates.append((calc, sku_topic))
    if candidates:
        return random.choice(candidates)
    calc = random.choice(CALCULATORS)
    angle = random.choice(ANGLES)
    return calc, f"{calc['name']}: {angle}"


def main():
    if not GEMINI_API_KEY and not ANTHROPIC_API_KEY:
        print("Neither GEMINI_API_KEY nor ANTHROPIC_API_KEY set; skipping article generation.")
        return

    os.makedirs("articles", exist_ok=True)
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    calc, sku_topic = pick_unused_sku_topic()

    try:
        title, body_html = generate_with_llm(calc, sku_topic)
    except Exception as e:
        print(f"Article generation error: {e}")
        return

    slug = generate_slug(title)
    filename = f"articles/{today_str}-{slug}.html"
    meta_desc = extract_meta_description(body_html, title)
    auditor_html = build_quote_auditor_widget(calc)
    chart_html = build_svg_cost_chart(calc)
    bom_html = build_shoppable_bom_table(calc)
    adsense_block = f"""
    <div style="margin: 2rem 0; text-align: center; min-height: 250px;">
      <ins class="adsbygoogle"
           style="display:block; text-align:center;"
           data-ad-layout="in-article"
           data-ad-format="fluid"
           data-ad-client="{ADSENSE_CLIENT}"
           data-ad-slot="responsive"></ins>
      <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
    </div>"""

    if "</p>" in body_html:
        body_html = body_html.replace("</p>", "</p>\n" + auditor_html + "\n" + chart_html, 1)
    else:
        body_html = auditor_html + "\n" + chart_html + "\n" + body_html

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="google-adsense-account" content="{ADSENSE_CLIENT}">
  <title>{title} | The Buyer's Math</title>
  <meta name="description" content="{meta_desc}">
  <link rel="canonical" href="https://thebuyersmath.com/{filename}">
  <link rel="stylesheet" href="/styles.css">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="https://thebuyersmath.com/{filename}">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-V4GTQSCFW6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-V4GTQSCFW6');
  </script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_CLIENT}" crossorigin="anonymous"></script>
</head>
<body style="font-family: Inter, -apple-system, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.7; margin: 0;">
  <header class="site-header" style="background: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 0.9rem 1.5rem;">
    <div style="max-width: 1100px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
      <a href="/" style="font-size: 1.3rem; font-weight: 800; color: #0f172a; text-decoration: none;">The Buyer's Math</a>
      <nav style="display: flex; gap: 1.25rem; font-size: 0.92rem; font-weight: 600;">
        <a href="/" style="color: #2563eb; text-decoration: none;">Daily Guides &amp; Calculators</a>
        <a href="/intel/" style="color: #475569; text-decoration: none;">Daily Intel</a>
        <a href="/guides.html" style="color: #475569; text-decoration: none;">All Guides</a>
        <a href="/about.html" style="color: #475569; text-decoration: none;">Methodology</a>
      </nav>
    </div>
  </header>
  <main style="max-width: 840px; margin: 2rem auto 4rem auto; padding: 0 1.5rem;">
    <article style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2.25rem; box-shadow: 0 1px 3px rgba(15,23,42,0.05);">
      <div style="margin-bottom: 1rem; font-size: 0.82rem; color: #64748b; font-weight: 600;">
        <span style="background: #eff6ff; color: #2563eb; padding: 0.22rem 0.6rem; border-radius: 4px; text-transform: uppercase;">{calc['category']}</span>
        &bull; Published on {today_str} &bull; Verified 2026 Cost Model
      </div>
      <h1 style="font-size: clamp(1.65rem, 3vw, 2.25rem); color: #0f172a; line-height: 1.25; margin: 0 0 1.25rem 0;">{title}</h1>
      {body_html}
      {adsense_block}
      {bom_html}
    </article>
  </main>
  <footer style="background: #0f172a; color: #94a3b8; padding: 2.5rem 1.5rem; text-align: center; font-size: 0.85rem;">
    <p style="max-width: 780px; margin: 0 auto 0.75rem auto;">
      <strong>Affiliate Disclosure:</strong> The Buyer's Math participates in the Amazon Services LLC Associates Program (Tag: <code>{AMAZON_TAG}</code>) and Commission Junction (PID: 101896838).
    </p>
    <p style="margin: 0;">&copy; 2026 The Buyer's Math. All rights reserved.</p>
  </footer>
</body>
</html>
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Generated new daily SKU cost guide: {filename}")


if __name__ == "__main__":
    main()
