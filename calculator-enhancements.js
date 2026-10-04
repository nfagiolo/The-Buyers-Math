/**
 * The Buyer's Math - Client-Side Calculator Enhancements
 * 1. Regional Cost Multiplier (Low, National, High, Urban)
 * 2. LocalStorage Persistence (Auto-Save & Restore)
 * 3. 1-Page Printable Contractor Estimate & Bid Sheet
 */

(function() {
  'use strict';

  const STORAGE_KEY = 'tbm_calc_' + window.location.pathname.replace(/[^a-zA-Z0-9]/g, '_');
  const REGION_STORAGE_KEY = 'tbm_global_region_multiplier';

  const REGIONS = [
    { factor: '1.00', label: 'National Average (Baseline 1.0x)' },
    { factor: '0.85', label: 'Lower Cost / Rural / South Central (-15%)' },
    { factor: '1.20', label: 'Higher Cost / Mid-Atlantic / West (+20%)' },
    { factor: '1.35', label: 'Major Urban / Coastal Metro (NYC, SF, Boston) (+35%)' }
  ];

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
      <div style="flex: 1; min-width: 260px;">
        <label for="tbm-region-select" style="display: block; font-size: 0.825rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.25rem;">
          📍 Location / Labor Cost Adjustment:
        </label>
        <select id="tbm-region-select" style="width: 100%; padding: 0.5rem 0.75rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; font-family: inherit; background: #ffffff; color: #0f172a; outline: none;">
          ${regionOptionsHtml}
        </select>
      </div>
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span id="tbm-save-status" style="font-size: 0.8rem; color: #059669; font-weight: 600; display: inline-flex; align-items: center; gap: 0.25rem;">
          ✓ Auto-saved
        </span>
        <button type="button" id="tbm-reset-btn" style="background: none; border: 1px solid #cbd5e1; color: #64748b; font-size: 0.75rem; padding: 0.35rem 0.65rem; border-radius: 4px; cursor: pointer;">
          Reset Inputs
        </button>
      </div>
    `;

    mainForm.insertBefore(controlsDiv, mainForm.firstChild);

    document.getElementById('tbm-region-select').addEventListener('change', function(e) {
      localStorage.setItem(REGION_STORAGE_KEY, e.target.value);
      updateRegionalDisplay();
      triggerRecalculate();
    });

    document.getElementById('tbm-reset-btn').addEventListener('click', function() {
      localStorage.removeItem(STORAGE_KEY);
      window.location.reload();
    });

    injectPrintComponents();
  }

  function injectPrintComponents() {
    const mainEl = document.querySelector('main') || document.body;
    const resultBox = document.querySelector('.result-box') || document.querySelector('.estimate-box') || document.querySelector('.receipt') || document.querySelector('.card');

    if (resultBox && !document.getElementById('tbm-print-trigger-btn')) {
      const printBtnContainer = document.createElement('div');
      printBtnContainer.style.cssText = 'margin: 1.5rem 0; text-align: center;';
      printBtnContainer.className = 'no-print';

      const printBtn = document.createElement('button');
      printBtn.type = 'button';
      printBtn.id = 'tbm-print-trigger-btn';
      printBtn.className = 'btn-print';
      printBtn.style.cssText = 'background: #0f172a; color: #ffffff; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-weight: 700; font-size: 0.95rem; cursor: pointer; display: inline-flex; align-items: center; gap: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: background 0.15s ease;';
      printBtn.innerHTML = '🖨️ Print / Save Contractor Bid Sheet (PDF)';
      printBtn.addEventListener('click', function() {
        updatePrintSheet();
        window.print();
      });

      printBtnContainer.appendChild(printBtn);
      resultBox.parentNode.insertBefore(printBtnContainer, resultBox.nextSibling);
    }

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

  function updatePrintSheet() {
    const summaryContainer = document.getElementById('tbm-print-inputs-summary');
    if (!summaryContainer) return;

    let items = [];
    const inputs = document.querySelectorAll('main input, main select');
    inputs.forEach(el => {
      if (el.id === 'tbm-region-select' || el.id === 'calc-search') return;
      let label = '';
      const labelEl = document.querySelector(`label[for="${el.id}"]`);
      if (labelEl) label = labelEl.innerText.replace(/[:*]/g, '').trim();
      else if (el.placeholder) label = el.placeholder;
      else if (el.name) label = el.name;

      if (!label) return;

      let val = el.value;
      if (el.type === 'checkbox') val = el.checked ? 'Yes' : 'No';
      if (el.tagName === 'SELECT') {
        val = el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : el.value;
      }

      if (val) items.push(`<strong>${label}:</strong> ${val}`);
    });

    const regionSelect = document.getElementById('tbm-region-select');
    if (regionSelect) {
      const regText = regionSelect.options[regionSelect.selectedIndex].text;
      items.push(`<strong>Regional Labor Market:</strong> ${regText}`);
    }

    summaryContainer.innerHTML = items.length ? items.join(' &bull; ') : 'Custom project measurements evaluated on thebuyersmath.com';
  }

  function setupPersistence() {
    const inputs = document.querySelectorAll('main input, main select');
    if (!inputs.length) return;

    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const data = JSON.parse(raw);
        inputs.forEach(el => {
          const key = el.id || el.name;
          if (key && data[key] !== undefined) {
            if (el.type === 'checkbox') {
              el.checked = data[key];
            } else {
              el.value = data[key];
            }
          }
        });
        triggerRecalculate();
      }
    } catch(e) {
      console.warn('LocalStorage restore error:', e);
    }

    function saveForm() {
      const data = {};
      inputs.forEach(el => {
        if (el.id === 'tbm-region-select' || el.id === 'calc-search') return;
        const key = el.id || el.name;
        if (key) {
          data[key] = (el.type === 'checkbox') ? el.checked : el.value;
        }
      });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));

      const statusEl = document.getElementById('tbm-save-status');
      if (statusEl) {
        statusEl.innerText = '✓ Saved';
        setTimeout(() => { if (statusEl) statusEl.innerText = '✓ Auto-saved'; }, 1500);
      }
    }

    inputs.forEach(el => {
      el.addEventListener('input', saveForm);
      el.addEventListener('change', saveForm);
    });
  }

  function triggerRecalculate() {
    const firstInput = document.querySelector('main input, main select');
    if (firstInput) {
      firstInput.dispatchEvent(new Event('input', { bubbles: true }));
      firstInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }

  function updateRegionalDisplay() {
    const regionVal = parseFloat(localStorage.getItem(REGION_STORAGE_KEY) || '1.00');
    window.TBM_REGIONAL_MULTIPLIER = regionVal;
  }

  function init() {
    if (document.querySelector('main input, main select, .calc-card')) {
      injectControls();
      setupPersistence();
      updateRegionalDisplay();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
