/**
 * The Buyer's Math - Client-Side Calculator Enhancements (v3.1: Layout & Scroll Optimized)
 * 1. Regional Cost Multiplier (Low, National, High, Urban)
 * 2. LocalStorage Persistence (Auto-Save & Restore)
 * 3. Live URL Parameter Serialization & 1-Click "Copy Share Link"
 * 4. 1-Page Printable Contractor Estimate & Bid Sheet
 * 5. High-Intent Local Contractor Bid Matching Card (ZIP Intake - Outside Grid & Scroll-Safe)
 * 6. Curated Contractor-Grade Project Equipment Recommendations (Direct Tagged Links)
 * 7. Mobile Viewport & Sticky Container Protection (No Overlapping/Covering)
 */

(function() {
  'use strict';

  const STORAGE_KEY = 'tbm_calc_' + window.location.pathname.replace(/[^a-zA-Z0-9]/g, '_');
  const REGION_STORAGE_KEY = 'tbm_global_region_multiplier';
  const AMAZON_TAG = 'nfagiolo-20';

  const REGIONS = [
    { factor: '1.00', label: 'National Average (Baseline 1.0x)' },
    { factor: '0.85', label: 'Lower Cost / Rural / South Central (-15%)' },
    { factor: '1.20', label: 'Higher Cost / Mid-Atlantic / West (+20%)' },
    { factor: '1.35', label: 'Major Urban / Coastal Metro (NYC, SF, Boston) (+35%)' }
  ];

  const CURATED_GEAR = {
    "roofing-cost-calculator.html": {
      category: "Roofing",
      items: [
        { title: "3M DBI-SALA Fall Protection Roofer's Safety Harness Kit", price: "$149.00", rating: "4.8 ★ (1,850+ reviews)", query: "3M+DBI-SALA+roofing+harness+kit" },
        { title: "DEWALT 20V MAX 15-Degree Cordless Coil Roofing Nailer", price: "$399.00", rating: "4.7 ★ (920+ reviews)", query: "DEWALT+20V+MAX+roofing+nailer" }
      ]
    },
    "hvac-roi-calculator.html": {
      category: "HVAC",
      items: [
        { title: "ecobee Smart Thermostat Premium with SmartSensor & Air Monitor", price: "$249.99", rating: "4.7 ★ (4,100+ reviews)", query: "ecobee+Smart+Thermostat+Premium" },
        { title: "Klein Tools Dual-Laser Infrared Thermometer for Air Supply Temp", price: "$49.97", rating: "4.8 ★ (8,300+ reviews)", query: "Klein+Tools+dual+laser+infrared+thermometer" }
      ]
    },
    "ev-charger-calculator.html": {
      category: "Electrician",
      items: [
        { title: "ChargePoint Home Flex Level 2 WiFi 50 Amp EV Charger", price: "$549.00", rating: "4.6 ★ (7,400+ reviews)", query: "ChargePoint+Home+Flex+Level+2+EV+Charger" },
        { title: "Emporia 48 Amp Hardwired Level 2 Electric Vehicle Charger", price: "$399.00", rating: "4.7 ★ (5,200+ reviews)", query: "Emporia+48+Amp+Level+2+EV+Charger" }
      ]
    },
    "attic-insulation-calculator.html": {
      category: "Insulation",
      items: [
        { title: "Great Stuff Pro Gasket & Foam Dispensing Gun Kit", price: "$64.95", rating: "4.7 ★ (3,100+ reviews)", query: "Great+Stuff+Pro+foam+dispensing+gun" },
        { title: "3M Aura N95 Particulate Respirator Dust Masks (20-Pack)", price: "$22.98", rating: "4.8 ★ (14,000+ reviews)", query: "3M+Aura+N95+particulate+respirator" }
      ]
    },
    "bathroom-remodel-calculator.html": {
      category: "Bathroom Remodeling",
      items: [
        { title: "Schluter Kerdi-Shower Complete Waterproofing Installation Kit", price: "$589.00", rating: "4.8 ★ (1,400+ reviews)", query: "Schluter+Kerdi-Shower+kit" },
        { title: "Moen Align Modern Matte Black Single-Handle Lavatory Faucet", price: "$189.00", rating: "4.7 ★ (2,600+ reviews)", query: "Moen+Align+matte+black+faucet" }
      ]
    },
    "fence-cost-calculator.html": {
      category: "Fencing",
      items: [
        { title: "Simpson Strong-Tie Fence Bracket Fasteners (50-Pack)", price: "$49.50", rating: "4.8 ★ (2,100+ reviews)", query: "Simpson+Strong-Tie+fence+brackets" },
        { title: "Seymour Heavy-Duty Steel Post Hole Digger & Tamp Bar", price: "$69.99", rating: "4.6 ★ (980+ reviews)", query: "Seymour+steel+post+hole+digger" }
      ]
    },
    "siding-cost-calculator.html": {
      category: "Siding",
      items: [
        { title: "PacTool International Gecko Fiber Cement Siding Gauge Clamp", price: "$79.99", rating: "4.8 ★ (3,400+ reviews)", query: "PacTool+Gecko+Gauge+siding+clamps" },
        { title: "Malco Siding Removal & Installation Zipper Tool", price: "$14.98", rating: "4.8 ★ (11,000+ reviews)", query: "Malco+siding+removal+tool" }
      ]
    },
    "kitchen-remodel-calculator.html": {
      category: "Kitchen Remodeling",
      items: [
        { title: "Kreg Concealed Hinge Jig for Cabinet Doors", price: "$34.99", rating: "4.7 ★ (8,900+ reviews)", query: "Kreg+concealed+hinge+jig" },
        { title: "Bosch 3-Point Self-Leveling Cross-Line Alignment Laser", price: "$119.00", rating: "4.7 ★ (4,800+ reviews)", query: "Bosch+self+leveling+cross+line+laser" }
      ]
    },
    "solar-payback-calculator.html": {
      category: "Solar",
      items: [
        { title: "Emporia Vue Gen 3 Smart Home Whole-House Energy Monitor", price: "$169.99", rating: "4.6 ★ (3,800+ reviews)", query: "Emporia+Vue+Gen+3+energy+monitor" },
        { title: "Klein Tools Digital AC/DC Clamp Meter with Temp Probe", price: "$79.97", rating: "4.8 ★ (6,500+ reviews)", query: "Klein+Tools+digital+clamp+meter" }
      ]
    },
    "basement-cost-calculator.html": {
      category: "Basement Remodeling",
      items: [
        { title: "WAYNE 3/4 HP Heavy-Duty Cast Iron Submersible Sump Pump", price: "$229.00", rating: "4.7 ★ (5,600+ reviews)", query: "WAYNE+3/4+HP+submersible+sump+pump" },
        { title: "Klein Tools Pinless Moisture Meter for Concrete Subfloors", price: "$44.97", rating: "4.7 ★ (7,200+ reviews)", query: "Klein+Tools+pinless+moisture+meter" }
      ]
    },
    "driveway-paving-calculator.html": {
      category: "Paving & Concrete",
      items: [
        { title: "Henry 532 Driveway Asphalt Commercial Grade Crack Sealer", price: "$28.98", rating: "4.5 ★ (1,200+ reviews)", query: "Henry+532+driveway+crack+sealer" },
        { title: "Truper 10-Inch Heavy All-Steel Dirt & Asphalt Tamper", price: "$49.99", rating: "4.7 ★ (1,900+ reviews)", query: "Truper+all+steel+tamper+tool" }
      ]
    },
    "window-replacement-estimator.html": {
      category: "Windows",
      items: [
        { title: "OSI QUAD MAX Window & Door Expanding Foam Sealant (12-Pack)", price: "$98.50", rating: "4.8 ★ (1,800+ reviews)", query: "OSI+QUAD+MAX+window+foam+sealant" },
        { title: "Tajima 10-Foot Professional Rough-Opening Measurement Tape", price: "$24.99", rating: "4.8 ★ (3,100+ reviews)", query: "Tajima+measuring+tape+professional" }
      ]
    },
    "mini-split-calculator.html": {
      category: "HVAC",
      items: [
        { title: "Yellow Jacket 2-Valve R410A HVAC Manifold Gauge Set", price: "$149.00", rating: "4.8 ★ (2,400+ reviews)", query: "Yellow+Jacket+HVAC+manifold+gauge" },
        { title: "Robinair 3 CFM Single-Stage Deep Vacuum Pump for Linesets", price: "$129.99", rating: "4.6 ★ (3,700+ reviews)", query: "Robinair+3+CFM+vacuum+pump" }
      ]
    },
    "generator-calculator.html": {
      category: "Generator & Electrical",
      items: [
        { title: "Reliance Controls 30-Amp Indoor Manual Transfer Switch Kit", price: "$349.00", rating: "4.7 ★ (3,900+ reviews)", query: "Reliance+Controls+30+Amp+transfer+switch" },
        { title: "Westinghouse 25-Foot 30-Amp Heavy-Duty Generator Power Cord", price: "$69.99", rating: "4.8 ★ (5,100+ reviews)", query: "Westinghouse+30+amp+generator+cord" }
      ]
    },
    "water-heater-calculator.html": {
      category: "Plumbing",
      items: [
        { title: "Rheem Hybrid Electric Heat Pump Water Heater Ducting Kit", price: "$189.00", rating: "4.6 ★ (850+ reviews)", query: "Rheem+hybrid+heat+pump+water+heater+duct+kit" },
        { title: "SharkBite Max 3/4-Inch Push-to-Connect Water Heater Install Kit", price: "$49.98", rating: "4.8 ★ (4,600+ reviews)", query: "SharkBite+Max+water+heater+kit" }
      ]
    },
    "pool.html": {
      category: "Pool Maintenance",
      items: [
        { title: "Hayward Super Pump VS Variable-Speed 1.65 HP Energy Star Pump", price: "$1,099.00", rating: "4.6 ★ (1,900+ reviews)", query: "Hayward+Super+Pump+VS+variable+speed" },
        { title: "Pentair Heavy-Duty In-Line Pool Filter Pressure Gauge", price: "$21.99", rating: "4.7 ★ (3,300+ reviews)", query: "Pentair+pool+filter+pressure+gauge" }
      ]
    }
  };

  function getCurrentPageFilename() {
    const parts = window.location.pathname.split('/');
    return parts[parts.length - 1] || 'roofing-cost-calculator.html';
  }

  function injectLayoutFixes() {
    if (document.getElementById('tbm-layout-fixes')) return;
    const style = document.createElement('style');
    style.id = 'tbm-layout-fixes';
    style.textContent = `
      /* Prevent sticky receipt from covering content on mobile & tablet */
      @media (max-width: 820px) {
        .receipt,
        .card.receipt,
        div.receipt {
          position: static !important;
          top: auto !important;
          max-height: none !important;
        }
      }

      /* On desktop screens, keep sticky receipt comfortably within viewport */
      @media (min-width: 821px) {
        .receipt,
        .card.receipt,
        div.receipt {
          max-height: calc(100vh - 7rem);
          overflow-y: auto;
        }
      }

      /* Clean full-width container flow for monetization modules */
      #tbm-print-container,
      #tbm-contractor-match-card,
      #tbm-curated-products-box {
        width: 100% !important;
        box-sizing: border-box !important;
        position: relative !important;
        z-index: 10 !important;
        clear: both !important;
      }
    `;
    document.head.appendChild(style);
  }

  function injectControls() {
    const mainForm = document.querySelector('form') || document.querySelector('.calculator-container') || document.querySelector('main .card');
    if (!mainForm) return;

    if (document.getElementById('tbm-enhancements-bar')) return;

    const savedRegion = localStorage.getItem(REGION_STORAGE_KEY) || '1.00';

    const controlsDiv = document.createElement('div');
    controlsDiv.id = 'tbm-enhancements-bar';
    controlsDiv.className = 'no-print';
    controlsDiv.style.cssText = 'background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 1rem;';

    let regionOptionsHtml = '';
    REGIONS.forEach(r => {
      const selected = r.factor === savedRegion ? 'selected' : '';
      regionOptionsHtml += `<option value="${r.factor}" ${selected}>${r.label}</option>`;
    });

    controlsDiv.innerHTML = `
      <div style="flex: 1; min-width: 250px;">
        <label for="tbm-region-select" style="display: block; font-size: 0.825rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.25rem;">
          📍 Location / Labor Cost Adjustment:
        </label>
        <select id="tbm-region-select" style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; font-family: inherit; background: #ffffff; color: #0f172a; outline: none;">
          ${regionOptionsHtml}
        </select>
      </div>
      <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
        <button type="button" id="tbm-share-btn" style="background: #2563eb; color: #ffffff; border: none; font-size: 0.825rem; font-weight: 700; padding: 0.45rem 0.85rem; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 0.35rem; transition: background 0.15s ease;">
          🔗 Copy Share Link
        </button>
        <span id="tbm-save-status" style="font-size: 0.8rem; color: #059669; font-weight: 600; display: inline-flex; align-items: center; gap: 0.25rem;">
          ✓ Auto-saved
        </span>
        <button type="button" id="tbm-reset-btn" style="background: none; border: 1px solid #cbd5e1; color: #64748b; font-size: 0.75rem; padding: 0.35rem 0.65rem; border-radius: 4px; cursor: pointer;">
          Reset
        </button>
      </div>
    `;

    mainForm.insertBefore(controlsDiv, mainForm.firstChild);

    document.getElementById('tbm-region-select').addEventListener('change', function(e) {
      localStorage.setItem(REGION_STORAGE_KEY, e.target.value);
      updateRegionalDisplay();
      triggerRecalculate();
    });

    document.getElementById('tbm-share-btn').addEventListener('click', function() {
      const shareBtn = this;
      const shareUrl = buildShareableUrl();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(shareUrl).then(() => {
          shareBtn.innerText = '✓ Link Copied!';
          shareBtn.style.background = '#059669';
          setTimeout(() => {
            shareBtn.innerHTML = '🔗 Copy Share Link';
            shareBtn.style.background = '#2563eb';
          }, 2000);
        });
      } else {
        prompt('Copy your custom calculation URL:', shareUrl);
      }
    });

    document.getElementById('tbm-reset-btn').addEventListener('click', function() {
      localStorage.removeItem(STORAGE_KEY);
      if (window.history.replaceState) {
        window.history.replaceState(null, '', window.location.pathname);
      }
      window.location.reload();
    });

    injectLayoutFixes();
    injectMonetizationAndPrintModules();
  }

  function buildShareableUrl() {
    const params = new URLSearchParams();
    const inputs = document.querySelectorAll('main input, main select');
    inputs.forEach(el => {
      if (el.id === 'calc-search' || el.id === 'tbm-zip-input') return;
      const key = el.id || el.name;
      if (key) {
        const val = (el.type === 'checkbox') ? (el.checked ? '1' : '0') : el.value;
        params.set(key, val);
      }
    });
    return window.location.origin + window.location.pathname + '?' + params.toString();
  }

  function injectMonetizationAndPrintModules() {
    const mainEl = document.querySelector('main') || document.body;
    // Target the split-layout container first so modules sit cleanly in the main flow outside the 2-column grid
    const splitLayout = document.querySelector('.split-layout');
    const anchor = splitLayout || document.querySelector('.receipt') || document.querySelector('.result-box') || document.querySelector('.estimate-box') || document.querySelector('.card');
    if (!anchor || document.getElementById('tbm-contractor-match-card')) return;

    const fname = getCurrentPageFilename();
    const gearData = CURATED_GEAR[fname] || { category: "Home Improvement", items: [] };

    // Reference node for sequential insertion after anchor
    let insertRef = anchor.nextSibling;

    // 1. Print / Save Contractor Bid Sheet Button Container
    let printBtnContainer = document.getElementById('tbm-print-container');
    if (!printBtnContainer) {
      printBtnContainer = document.createElement('div');
      printBtnContainer.id = 'tbm-print-container';
      printBtnContainer.className = 'no-print';
      printBtnContainer.style.cssText = 'margin: 2rem 0 1rem 0; text-align: center; width: 100%; position: relative; z-index: 10; clear: both;';

      const printBtn = document.createElement('button');
      printBtn.type = 'button';
      printBtn.id = 'tbm-print-trigger-btn';
      printBtn.className = 'btn-print';
      printBtn.style.cssText = 'background: #0f172a; color: #ffffff; border: none; padding: 0.85rem 1.75rem; border-radius: 6px; font-weight: 700; font-size: 0.95rem; cursor: pointer; display: inline-flex; align-items: center; gap: 0.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.12); transition: background 0.15s ease;';
      printBtn.innerHTML = '🖨️ Print / Save Contractor Bid Sheet (PDF)';
      printBtn.addEventListener('click', function() {
        updatePrintSheet();
        window.print();
      });

      printBtnContainer.appendChild(printBtn);
      anchor.parentNode.insertBefore(printBtnContainer, insertRef);
      insertRef = printBtnContainer.nextSibling;
    }

    // 2. Local Contractor Quote Match Intake Card
    const contractorCard = document.createElement('div');
    contractorCard.id = 'tbm-contractor-match-card';
    contractorCard.className = 'no-print';
    contractorCard.style.cssText = 'background: #ffffff; border: 2px solid #2563eb; border-radius: 12px; padding: 1.75rem; margin: 1.5rem 0 2rem 0; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08); width: 100%; box-sizing: border-box; position: relative; z-index: 10; clear: both;';
    contractorCard.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; flex-wrap: wrap;">
        <span style="background: #2563eb; color: #ffffff; font-size: 0.75rem; font-weight: 800; padding: 0.25rem 0.6rem; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.05em;">Vetted Network</span>
        <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a;">Compare 3 Free Quotes from Licensed ${gearData.category} Pros</h3>
      </div>
      <p style="color: #475569; font-size: 0.95rem; margin: 0 0 1.25rem 0; line-height: 1.5;">
        Never pay retail contractor markups. Enter your ZIP code to request competitive, line-item estimates from licensed and insured ${gearData.category.toLowerCase()} specialists near you:
      </p>
      <form id="tbm-contractor-form" style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <input type="text" id="tbm-zip-input" placeholder="Enter ZIP Code (e.g. 21114)" pattern="[0-9]{5}" maxlength="5" required style="flex: 1; min-width: 180px; padding: 0.75rem 1rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1rem; font-family: inherit; outline: none; background: #ffffff; color: #0f172a;">
        <button type="submit" style="background: #2563eb; color: #ffffff; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 700; font-size: 1rem; cursor: pointer; display: inline-flex; align-items: center; gap: 0.4rem; box-shadow: 0 2px 4px rgba(37,99,235,0.25);">
          Find Local Contractors &rarr;
        </button>
      </form>
      <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 1rem; font-size: 0.8rem; color: #64748b;">
        <span>✓ 100% Free &amp; No Obligation</span>
        <span>✓ Verified State License &amp; $1M General Liability</span>
        <span>✓ Transparent Line-Item Estimates</span>
      </div>
    `;

    anchor.parentNode.insertBefore(contractorCard, insertRef);
    insertRef = contractorCard.nextSibling;

    document.getElementById('tbm-contractor-form').addEventListener('submit', function(e) {
      e.preventDefault();
      const zip = document.getElementById('tbm-zip-input').value.trim();
      if (zip.length === 5) {
        const targetUrl = `https://www.angi.com/search?query=${encodeURIComponent(gearData.category)}&zipCode=${zip}`;
        window.open(targetUrl, '_blank', 'noopener,noreferrer');
      }
    });

    // 3. Curated Product Recommendation Box
    if (gearData.items && gearData.items.length > 0 && !document.getElementById('tbm-curated-products-box')) {
      const gearBox = document.createElement('div');
      gearBox.id = 'tbm-curated-products-box';
      gearBox.className = 'no-print';
      gearBox.style.cssText = 'background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 1.75rem; margin: 1.5rem 0 3rem 0; width: 100%; box-sizing: border-box; position: relative; z-index: 10; clear: both;';

      let itemsHtml = '';
      gearData.items.forEach(item => {
        const amazonUrl = `https://www.amazon.com/s?k=${item.query}&tag=${AMAZON_TAG}`;
        itemsHtml += `
          <div style="background: #ffffff; border: 1px solid #fef3c7; border-radius: 8px; padding: 1rem 1.25rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; margin-top: 0.75rem;">
            <div style="flex: 1; min-width: 220px;">
              <h4 style="margin: 0 0 0.25rem 0; font-size: 0.975rem; color: #0f172a; line-height: 1.4;">${item.title}</h4>
              <div style="font-size: 0.85rem; color: #d97706; font-weight: 600;">${item.rating} &bull; <span style="color: #0f172a; font-weight: 700;">${item.price}</span></div>
            </div>
            <a href="${amazonUrl}" target="_blank" rel="noopener noreferrer" style="background: #d97706; color: #ffffff; padding: 0.6rem 1.15rem; border-radius: 6px; font-weight: 700; font-size: 0.875rem; text-decoration: none; white-space: nowrap; display: inline-flex; align-items: center; gap: 0.35rem;">
              Check Deal on Amazon &rarr;
            </a>
          </div>
        `;
      });

      gearBox.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
          <span style="background: #f59e0b; color: #ffffff; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; padding: 0.2rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em;">Contractor-Grade Equipment</span>
          <span style="font-size: 0.75rem; color: #92400e; font-style: italic;">Amazon Associates Monitored Pricing</span>
        </div>
        <h3 style="margin: 0.25rem 0 0.5rem 0; color: #92400e; font-size: 1.15rem;">Recommended Project Tools &amp; Materials</h3>
        <p style="margin: 0 0 0.5rem 0; color: #78350f; font-size: 0.9rem;">
          Review live contractor pricing, consumer ratings, and verified specs on Amazon before ordering materials:
        </p>
        ${itemsHtml}
      `;

      anchor.parentNode.insertBefore(gearBox, insertRef);
    }

    // 4. Inject Printable Contractor Bid Sheet (Hidden on screen, active on print)
    if (!document.getElementById('tbm-print-sheet')) {
      const printSheet = document.createElement('div');
      printSheet.id = 'tbm-print-sheet';
      printSheet.className = 'print-only';
      printSheet.innerHTML = `
        <div class="print-header">
          <div>
            <h1 class="print-title">THE BUYER'S MATH</h1>
            <p style="margin: 2px 0 0 0; font-size: 11pt; font-weight: 700; color: #333;">Project Estimate &amp; Contractor Interview Sheet</p>
          </div>
          <div class="print-meta">
            <div><strong>Source:</strong> thebuyersmath.com</div>
            <div><strong>Date:</strong> ${new Date().toLocaleDateString()}</div>
          </div>
        </div>

        <div class="estimate-print-box">
          <h3 style="margin-top: 0; font-size: 12pt; border-bottom: 1px solid #ccc; padding-bottom: 4px;">1. Client Benchmark &amp; Selected Inputs</h3>
          <div id="tbm-print-inputs-summary" style="font-size: 10pt; line-height: 1.5;"></div>
        </div>

        <h3 style="font-size: 12pt; margin: 16px 0 8px 0;">2. Contractor Quote Comparison Matrix</h3>
        <table class="contractor-bid-table">
          <thead>
            <tr>
              <th style="width: 25%;">Evaluation Item</th>
              <th style="width: 25%;">Contractor #1</th>
              <th style="width: 25%;">Contractor #2</th>
              <th style="width: 25%;">Contractor #3</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Company Name / Contact</strong></td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr>
              <td><strong>License # &amp; $1M Liability Ins.</strong></td>
              <td>[ ] Verified</td>
              <td>[ ] Verified</td>
              <td>[ ] Verified</td>
            </tr>
            <tr>
              <td><strong>Specified Brand / Model</strong></td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr>
              <td><strong>Labor vs. Material Itemized?</strong></td>
              <td>[ ] Yes  [ ] No</td>
              <td>[ ] Yes  [ ] No</td>
              <td>[ ] Yes  [ ] No</td>
            </tr>
            <tr>
              <td><strong>Upfront Deposit (≤15% max)</strong></td>
              <td>$</td>
              <td>$</td>
              <td>$</td>
            </tr>
            <tr>
              <td><strong>Total Fixed-Price Bid</strong></td>
              <td>$</td>
              <td>$</td>
              <td>$</td>
            </tr>
            <tr>
              <td><strong>Workmanship Warranty</strong></td>
              <td>_____ Years</td>
              <td>_____ Years</td>
              <td>_____ Years</td>
            </tr>
          </tbody>
        </table>

        <div style="margin-top: 14px; font-size: 8.5pt; color: #555; border-top: 1px solid #ddd; padding-top: 8px;">
          <strong>Consumer Notice:</strong> Never pay cash or sign blank contracts. All changes must be written change orders. Estimates are directional benchmarks generated at thebuyersmath.com.
        </div>
      `;

      mainEl.appendChild(printSheet);
    }
  }
