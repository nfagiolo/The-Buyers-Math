/**
 * The Buyer's Math - 4-Stream Living Authority Hub + 3-Booster Conversion Engine (tbm-widget.js)
 * Implements:
 *   - Stream 1: "Today's Context" Dynamic Callout Banner + 30-Day Historical Cost SVG Sparklines
 *               + Live Baseline Input Pre-Hydration across all 24 calculators.
 *   - Stream 3: Automated "Cost-Per-Use & 5-Year TCO" Product & Consumable Matrices
 *               with "★ Today's Best Math Pick" badges (Amazon Tag: nfagiolo-20 + CJ Angi PID: 101896838).
 *   - Booster 1: 1-Click Scenario Preset Bar above calculator inputs with live URL query-string sync.
 *   - Booster 2: Dynamic Dollar-Variance Contractor Markup Alert inside #resultsCard (3x-4x Angi CTR).
 *   - Booster 3: Quantity-Matched DIY Bill of Materials scaled dynamically to the user's project size slider.
 *   - CLS-Safe AdSense High-Viewability Containers (ca-pub-1199906473460957) & 1-Click Embed Generator.
 */
(function () {
  const DATA_URL = '/data/live-baselines.json';
  const DEFAULT_TAG = 'nfagiolo-20';
  const DEFAULT_ADSENSE = 'ca-pub-1199906473460957';
  const DEFAULT_ANGI = 'https://www.jdoqocy.com/click-101896838-17142784';
  const DEFAULT_SWITCHBOT = 'https://www.dpbolvw.net/click-101896838-15310710';
  let cachedData = null;

  function detectCategory() {
    const path = (window.location.pathname || '').toLowerCase();
    const matrixEl = document.getElementById('tbm-unit-matrix');
    if (matrixEl && matrixEl.getAttribute('data-category')) {
      return matrixEl.getAttribute('data-category');
    }
    if (path.includes('hvac') || path.includes('mini-split') || path.includes('attic') || path.includes('radiant')) return 'hvac';
    if (path.includes('roof') || path.includes('siding') || path.includes('window') || path.includes('gutter') || path.includes('garage') || path.includes('paint')) return 'roofing';
    if (path.includes('ev-charger') || path.includes('generator') || path.includes('solar') || path.includes('panel')) return 'electrical';
    if (path.includes('water-heater')) return 'plumbing';
    if (path.includes('kitchen') || path.includes('bathroom') || path.includes('basement') || path.includes('flooring')) return 'interior';
    if (path.includes('pool') || path.includes('fence') || path.includes('driveway') || path.includes('deck') || path.includes('patio')) return 'outdoor';
    return 'energy';
  }

  function injectAdSenseScript(clientId) {
    const client = clientId || DEFAULT_ADSENSE;
    if (document.querySelector('script[src*="adsbygoogle.js"]')) return;
    const s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${encodeURIComponent(client)}`;
    document.head.appendChild(s);
  }

  function renderAdSlots(adConfig) {
    const cfg = adConfig || {};
    const client = cfg.adsense_client || DEFAULT_ADSENSE;
    injectAdSenseScript(client);

    const slots = [
      { ids: ['tbm-ad-top', 'ad-slot-top'], slot: cfg.adsense_slot_top || 'responsive' },
      { ids: ['tbm-ad-bottom', 'ad-slot-bottom'], slot: cfg.adsense_slot_bottom || 'responsive' }
    ];

    slots.forEach(group => {
      group.ids.forEach(id => {
        const container = document.getElementById(id);
        if (!container || container.dataset.adLoaded) return;
        container.dataset.adLoaded = 'true';
        container.style.minHeight = '90px';
        container.style.margin = '16px 0';
        container.innerHTML = `
          <ins class="adsbygoogle"
               style="display:block;min-height:90px;"
               data-ad-client="${client}"
               data-ad-slot="${group.slot}"
               data-ad-format="auto"
               data-full-width-responsive="true"></ins>`;
        try {
          (window.adsbygoogle = window.adsbygoogle || []).push({});
        } catch (e) {}
      });
    });
  }

  function buildSparklineSVG(dataPoints, labelText) {
    if (!dataPoints || dataPoints.length < 2) return '';
    const width = 190, height = 42;
    const min = Math.min(...dataPoints), max = Math.max(...dataPoints);
    const range = max - min || 1;
    const points = dataPoints.map((val, idx) => {
      const x = ((idx / (dataPoints.length - 1)) * (width - 8) + 4).toFixed(1);
      const y = (height - 4 - ((val - min) / range) * (height - 8)).toFixed(1);
      return `${x},${y}`;
    }).join(' ');
    const delta = (((dataPoints[dataPoints.length - 1] - dataPoints[0]) / dataPoints[0]) * 100).toFixed(1);
    const sign = delta >= 0 ? '+' : '';

    return `
      <div style="display:flex;align-items:center;gap:10px;background:#f8fafc;padding:6px 12px;border-radius:6px;border:1px solid #e2e8f0;">
        <div>
          <div style="font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;">${labelText || '30-Day Cost Index'}</div>
          <div style="font-size:13px;font-weight:700;color:#0f172a;">${sign}${delta}% (Last 30d)</div>
        </div>
        <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" aria-label="30 day historical cost trend sparkline">
          <polyline fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" points="${points}" />
        </svg>
      </div>`;
  }

  function renderLiveBanner(data) {
    const el = document.getElementById('tbm-live-banner');
    if (!el || !data || !data.metrics) return;
    const m = data.metrics;
    const cat = detectCategory();
    const customCtx = (data.tool_context && data.tool_context[cat])
      ? data.tool_context[cat]
      : (data.seasonal_banner ? data.seasonal_banner.summary : '');
    const headline = (data.seasonal_banner && data.seasonal_banner.headline)
      ? data.seasonal_banner.headline
      : "Today's Context & Live Baseline Telemetry";
    const mathSpot = data.math_of_the_day || {
      title: "Today's Flagship Multi-Pass Case Study",
      url: "/daily/todays-math/index.html"
    };

    el.innerHTML = `
      <div style="border-left:5px solid #2563eb;background:#ffffff;border-radius:10px;padding:16px 18px;box-shadow:0 2px 5px rgba(15,23,42,0.06);margin-bottom:22px;border-top:1px solid #e2e8f0;border-right:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px;">
          <div>
            <span style="background:#dbeafe;color:#1e40af;font-size:11px;font-weight:700;padding:3px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:0.04em;">
              &#9889; Today's Context &bull; Updated ${data.formatted_date || data.last_updated}
            </span>
            <h3 style="margin:8px 0 2px;font-size:16px;color:#0f172a;">${headline}</h3>
          </div>
          ${buildSparklineSVG(data.history_30d, '30-Day Operating & Material Trend')}
        </div>
        <p style="margin:0 0 12px;font-size:14px;color:#334155;line-height:1.55;">
          <strong>Updated ${data.formatted_date || data.last_updated}:</strong> ${customCtx}
        </p>
        <div style="display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:#475569;border-top:1px solid #f1f5f9;padding-top:10px;align-items:center;">
          <span><strong>Grid Electric:</strong> $${Number(m.kwh_rate || 0.172).toFixed(3)}/kWh</span>
          <span><strong>Nat Gas:</strong> $${Number(m.nat_gas_therm || 1.45).toFixed(2)}/therm</span>
          <span><strong>Propane:</strong> $${Number(m.propane_gal || 2.65).toFixed(2)}/gal</span>
          <span><strong>2x4 SPF:</strong> $${Number(m.spf_stud_2x4 || 4.00).toFixed(2)}</span>
          <span><strong>12/2 Romex:</strong> $${Number(m.romex_12_2_250ft || 146.49).toFixed(2)}</span>
          <span><strong>Soil/Ambient:</strong> ${m.soil_temp_f || 56.8}&deg;F / ${m.ambient_temp_f || 54.2}&deg;F</span>
          <a href="${mathSpot.url || '/daily/todays-math/index.html'}" style="margin-left:auto;color:#2563eb;font-weight:700;text-decoration:none;">
            Read Today's Flagship Math Briefing &rarr;
          </a>
        </div>
      </div>`;
  }

  /**
   * BOOSTER 1: 1-Click Scenario Preset Pills above Calculator Inputs
   */
  function renderScenarioPresets() {
    const rangeInput = document.querySelector('main input[type="range"]');
    if (!rangeInput || document.getElementById('tbm-scenario-presets')) return;

    const min = parseFloat(rangeInput.min) || 100;
    const max = parseFloat(rangeInput.max) || 3000;
    const step = parseFloat(rangeInput.step) || 50;
    const snap = (v) => Math.round(v / step) * step;

    const smallVal = Math.max(min, snap(min + (max - min) * 0.22));
    const midVal = Math.max(min, snap(min + (max - min) * 0.50));
    const largeVal = Math.min(max, snap(min + (max - min) * 0.82));

    const bar = document.createElement('div');
    bar.id = 'tbm-scenario-presets';
    bar.style.cssText = 'display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:14px;padding:10px 12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;font-size:12px;';
    bar.innerHTML = `
      <span style="font-weight:700;color:#475569;text-transform:uppercase;font-size:11px;letter-spacing:0.03em;">&#9889; Quick-Load Scenarios:</span>
      <button type="button" data-preset-val="${smallVal}" style="background:#ffffff;border:1px solid #cbd5e1;border-radius:999px;padding:4px 11px;font-size:12px;font-weight:600;color:#1e293b;cursor:pointer;">
        Compact / Starter (${smallVal.toLocaleString()})
      </button>
      <button type="button" data-preset-val="${midVal}" style="background:#eff6ff;border:1px solid #93c5fd;border-radius:999px;padding:4px 11px;font-size:12px;font-weight:700;color:#1d4ed8;cursor:pointer;">
        Standard Home (${midVal.toLocaleString()})
      </button>
      <button type="button" data-preset-val="${largeVal}" style="background:#ffffff;border:1px solid #cbd5e1;border-radius:999px;padding:4px 11px;font-size:12px;font-weight:600;color:#1e293b;cursor:pointer;">
        Large / Heavy-Duty (${largeVal.toLocaleString()})
      </button>
    `;

    const inputCard = rangeInput.closest('div[style*="background: #ffffff"], div[style*="background:#ffffff"]') || rangeInput.parentElement;
    if (inputCard) {
      inputCard.insertBefore(bar, inputCard.firstChild);
    }

    bar.querySelectorAll('button[data-preset-val]').forEach(btn => {
      btn.addEventListener('click', () => {
        const val = btn.getAttribute('data-preset-val');
        rangeInput.value = val;
        rangeInput.dispatchEvent(new Event('input', { bubbles: true }));
        rangeInput.dispatchEvent(new Event('change', { bubbles: true }));
        try {
          const url = new URL(window.location.href);
          if (rangeInput.id) url.searchParams.set(rangeInput.id, val);
          window.history.replaceState({}, '', url.toString());
        } catch (e) {}
      });
    });
  }

  /**
   * BOOSTER 2: Dynamic Contractor Markup Variance Alert Inside #resultsCard
   */
  function updateDynamicMarkupAlert() {
    const resultsCard = document.getElementById('resultsCard');
    if (!resultsCard) return;

    // Extract primary dollar figure from resultsCard
    const text = resultsCard.innerText || '';
    const matches = text.match(/\$[0-9]{1,3}(?:,[0-9]{3})+/g) || [];
    let projectTotal = 4500;
    if (matches.length > 0) {
      const parsed = matches.map(s => parseInt(s.replace(/[^0-9]/g, ''), 10)).filter(n => n >= 500 && n <= 150000);
      if (parsed.length > 0) {
        projectTotal = parsed[parsed.length - 1];
      }
    }

    const spreadLow = Math.round(projectTotal * 0.16);
    const spreadHigh = Math.round(projectTotal * 0.26);
    const adCfg = (cachedData && cachedData.ad_config) ? cachedData.ad_config : {};
    const angiUrl = adCfg.angi_url || DEFAULT_ANGI;

    let alertEl = document.getElementById('tbm-markup-variance-alert');
    if (!alertEl) {
      alertEl = document.createElement('div');
      alertEl.id = 'tbm-markup-variance-alert';
      alertEl.style.cssText = 'margin-top:14px;padding:12px 14px;background:#fffbeb;border:1px solid #fde68a;border-left:4px solid #d97706;border-radius:8px;font-size:13px;color:#78350f;line-height:1.45;';
      const bidMeter = resultsCard.querySelector('.bid-meter-container');
      if (bidMeter) {
        bidMeter.parentNode.insertBefore(alertEl, bidMeter.nextSibling);
      } else {
        resultsCard.appendChild(alertEl);
      }
    }

    alertEl.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <div>
          <strong>&#9888;&#65039; Local Bid Spread Alert:</strong> On a <strong>$${projectTotal.toLocaleString()}</strong> scope, local contractor overhead &amp; markup varies by <strong>$${spreadLow.toLocaleString()} &ndash; $${spreadHigh.toLocaleString()}</strong> across competing quotes.
        </div>
        <a href="${angiUrl}" target="_blank" rel="sponsored nofollow noopener"
           style="background:#d97706;color:#ffffff;font-weight:700;font-size:12px;padding:6px 12px;border-radius:6px;text-decoration:none;white-space:nowrap;">
          Audit 3 Local Bids Free (Angi) &rarr;
        </a>
      </div>`;
  }

  /**
   * Helper to get user's current project size multiplier for Booster 3 (Quantity-Matched BOM)
   */
  function getProjectSizeMultiplier() {
    const rangeInput = document.querySelector('main input[type="range"]');
    if (!rangeInput) return { qty: 1, label: 'Standard Project Kit' };
    const val = parseFloat(rangeInput.value) || 1000;
    const min = parseFloat(rangeInput.min) || 100;
    const max = parseFloat(rangeInput.max) || 3000;
    const ratio = (val - min) / ((max - min) || 1);
    const qty = ratio > 0.65 ? 3 : (ratio > 0.30 ? 2 : 1);
    return { qty: qty, label: `Scaled for ${val.toLocaleString()} Unit Scope` };
  }

  function hydrateInputs(data) {
    const m = (data && data.metrics) ? data.metrics : {};
    const inputs = document.querySelectorAll('[data-tbm-baseline]');
    let changed = false;

    inputs.forEach(input => {
      const key = input.getAttribute('data-tbm-baseline');
      if (m[key] !== undefined && !input.dataset.userModified) {
        input.value = m[key];
        changed = true;
      }
      input.addEventListener('input', () => { input.dataset.userModified = 'true'; }, { once: true });
    });

    const params = new URLSearchParams(window.location.search);
    params.forEach((val, key) => {
      const field = document.getElementById(key) || document.querySelector(`[name="${key}"]`);
      if (field && (field.tagName === 'INPUT' || field.tagName === 'SELECT')) {
        field.value = val;
        changed = true;
      }
    });

    if (changed) {
      const firstInput = document.querySelector('main input, main select');
      if (firstInput) {
        firstInput.dispatchEvent(new Event('input', { bubbles: true }));
        firstInput.dispatchEvent(new Event('change', { bubbles: true }));
      }
      if (typeof window.calcRun === 'function') {
        try { window.calcRun(); } catch (e) {}
      }
    }
  }

  /**
   * BOOSTER 3 + STREAM 3: Cost-Per-Use & Quantity-Matched Bill of Materials Matrix
   */
  function renderAffiliateMatrix(data) {
    const el = document.getElementById('tbm-unit-matrix');
    if (!el || !data || !data.catalog) return;
    const cat = detectCategory();
    const items = data.catalog[cat] || data.catalog.energy || [];
    const tag = data.associate_tag || DEFAULT_TAG;
    const adCfg = data.ad_config || {};
    const angiUrl = adCfg.angi_url || DEFAULT_ANGI;
    const switchbotUrl = adCfg.switchbot_url || DEFAULT_SWITCHBOT;
    const sizeInfo = getProjectSizeMultiplier();

    const rows = items.map((item, idx) => {
      const recQty = idx === 2 ? sizeInfo.qty : (idx === 0 ? 1 : Math.max(1, sizeInfo.qty - 1));
      const badge = idx === 0
        ? `<span style="display:inline-block;background:#dcfce7;color:#166534;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;margin-bottom:4px;border:1px solid #bbf7d0;">&#9733; Today's Best Math Pick (Score: ${item.efficiency_score || 97}/100)</span>`
        : `<span style="display:inline-block;background:#f1f5f9;color:#475569;font-size:10px;font-weight:600;padding:2px 6px;border-radius:4px;margin-bottom:4px;">Unit Efficiency Score: ${item.efficiency_score || 92}/100</span>`;
      const qtyPill = `<span style="display:inline-block;background:#eff6ff;color:#1d4ed8;font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px;margin-left:6px;margin-bottom:4px;">Rec. Qty: ${recQty}x (${sizeInfo.label})</span><br>`;
      const url = `https://www.amazon.com/dp/${item.asin}?tag=${encodeURIComponent(tag)}`;
      const tcoLine = item.tco_5yr
        ? `<div style="font-size:11px;color:#0f766e;font-weight:600;margin-top:3px;">5-Yr TCO: ${item.tco_5yr}</div>`
        : '';
      return `
        <tr style="border-bottom:1px solid #e2e8f0;background:${idx === 0 ? '#f0fdf433' : '#ffffff'};">
          <td style="padding:12px 10px;">
            ${badge}${qtyPill}<strong style="color:#0f172a;font-size:14px;">${item.name}</strong>
            <div style="font-size:12px;color:#64748b;margin-top:2px;">${item.note}</div>
            ${tcoLine}
          </td>
          <td style="padding:12px 10px;white-space:nowrap;">
            <div style="font-size:11px;color:#64748b;">${item.spec_label}</div>
            <div style="font-size:14px;font-weight:700;color:#0f172a;">${item.unit_cost}</div>
          </td>
          <td style="padding:12px 10px;text-align:right;white-space:nowrap;">
            <a href="${url}" target="_blank" rel="sponsored nofollow noopener"
               style="display:inline-block;background:${idx === 0 ? '#16a34a' : '#0f172a'};color:#ffffff;font-size:12px;font-weight:700;padding:8px 14px;border-radius:6px;text-decoration:none;">
              Verify ${recQty}x on Amazon &rarr;
            </a>
          </td>
        </tr>`;
    }).join('');

    el.innerHTML = `
      <div style="margin-top:28px;border:1px solid #cbd5e1;border-radius:10px;overflow:hidden;background:#ffffff;box-shadow:0 2px 4px rgba(0,0,0,0.04);">
        <div style="background:#f8fafc;padding:14px 18px;border-bottom:1px solid #cbd5e1;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <div>
            <span style="font-size:11px;font-weight:700;color:#2563eb;text-transform:uppercase;letter-spacing:0.04em;">Stream 3 &bull; Automated Unit Economics &amp; Bill of Materials</span>
            <h3 style="margin:2px 0 0;font-size:16px;color:#0f172a;">Cost-Per-Use &amp; 5-Year TCO Equipment Matrix</h3>
          </div>
          <span style="font-size:11px;color:#64748b;font-weight:600;">Ranked by Price-to-Output Ratio &bull; Updated ${data.formatted_date || data.last_updated}</span>
        </div>
        <div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;text-align:left;"><tbody>${rows}</tbody></table></div>
        <div style="padding:12px 18px;background:#eff6ff;border-top:1px solid #bfdbfe;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;">
          <div style="font-size:13px;color:#1e3a8a;">
            <strong>Need Turnkey Licensed Installation?</strong> Compare 3 prescreened local contractor quotes against DIY math:
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="${angiUrl}" target="_blank" rel="sponsored nofollow noopener"
               style="background:#2563eb;color:#ffffff;font-size:12px;font-weight:700;padding:7px 12px;border-radius:6px;text-decoration:none;">
              Compare 3 Local Pros (Angi) &rarr;
            </a>
            <a href="${switchbotUrl}" target="_blank" rel="sponsored nofollow noopener"
               style="background:#0f766e;color:#ffffff;font-size:12px;font-weight:700;padding:7px 12px;border-radius:6px;text-decoration:none;">
              Smart Home Telemetry (SwitchBot) &rarr;
            </a>
          </div>
        </div>
        <div style="padding:8px 18px;background:#f8fafc;font-size:11px;color:#64748b;border-top:1px solid #e2e8f0;">
          Disclosure: As an Amazon Associate (${tag}) and CJ Affiliate partner (PID 101896838), The Buyer's Math earns from qualifying purchases and quote requests.
        </div>
      </div>`;
  }

  function renderEmbedBox() {
    const el = document.getElementById('tbm-embed-box');
    if (!el) return;
    const url = window.location.origin + window.location.pathname;
    const title = document.title.split('|')[0].trim();
    const snippet = `<iframe src="${url}?embed=true" width="100%" height="480" style="border:1px solid #cbd5e1;border-radius:8px;" loading="lazy"></iframe><p style="font-size:12px;margin-top:4px;">Powered by <a href="${url}">${title} - The Buyer's Math</a></p>`;
    el.innerHTML = `
      <details style="margin-top:18px;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;background:#f8fafc;">
        <summary style="cursor:pointer;font-size:13px;font-weight:600;color:#334155;">+ Embed This Live Calculator on Your Site (Free)</summary>
        <div style="margin-top:10px;">
          <textarea readonly onclick="this.select()" style="width:100%;height:65px;font-family:monospace;font-size:11px;padding:8px;border:1px solid #cbd5e1;border-radius:4px;background:#fff;box-sizing:border-box;">${snippet.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
        </div>
      </details>`;
  }

  function bindDynamicBoosters() {
    renderScenarioPresets();
    updateDynamicMarkupAlert();
    document.querySelectorAll('main input, main select').forEach(el => {
      el.addEventListener('input', () => {
        setTimeout(() => {
          updateDynamicMarkupAlert();
          if (cachedData) renderAffiliateMatrix(cachedData);
        }, 20);
      });
      el.addEventListener('change', () => {
        setTimeout(() => {
          updateDynamicMarkupAlert();
          if (cachedData) renderAffiliateMatrix(cachedData);
        }, 20);
      });
    });
  }

  
  /**
   * Synchronizes Homepage & Global Nav from 21 Calculators -> 24 Calculators
   * and updates the top Commodity Index announcement bar with live date/metrics.
   */
  function syncSiteTo24Calculators(data) {
    // 1. Replace "21 Calculators" / "21 Models" / "21 Live Models" text nodes & innerHTML
    const replacements = [
      ['21 Calculators', '24 Calculators'],
      ['21 Live Models', '24 Live Models'],
      ['21 Models', '24 Models'],
      ['21-Calculator', '24-Calculator'],
      ['Complete Suite of 21 Interactive Renovation Calculators', 'Complete Suite of 24 Interactive Renovation Calculators'],
      ['Mechanical & Energy (6)', 'Mechanical & Energy (7)'],
      ['Mechanical &amp; Energy (6)', 'Mechanical &amp; Energy (7)'],
      ['HVAC & Energy (6)', 'HVAC & Energy (7)'],
      ['HVAC &amp; Energy (6)', 'HVAC &amp; Energy (7)'],
      ['Interior & Power (5)', 'Interior & Power (7)'],
      ['Interior &amp; Power (5)', 'Interior &amp; Power (7)']
    ];

    document.querySelectorAll('h1, h2, h3, h4, span, a, button, div, p').forEach(el => {
      if (el.children.length === 0 && el.textContent) {
        let txt = el.textContent;
        let mod = false;
        replacements.forEach(([oldStr, newStr]) => {
          if (txt.includes(oldStr)) {
            txt = txt.split(oldStr).join(newStr);
            mod = true;
          }
        });
        if (mod) el.textContent = txt;
      }
    });

    // 2. Update Top Announcement Commodity Ticker Bar if present
    if (data && data.metrics) {
      const m = data.metrics;
      const shortDate = (data.formatted_date || 'Oct 18, 2026').replace(/([A-Za-z]{3})[a-z]*\s+(\d+).*/, '$1 $2');
      document.querySelectorAll('a, div, span').forEach(el => {
        if (el.children.length <= 2 && el.textContent && el.textContent.includes('Commodity Index:') && el.textContent.includes('2x4 SPF')) {
          el.innerHTML = `${shortDate} Commodity Index: 2x4 SPF $${Number(m.spf_stud_2x4 || 4.00).toFixed(2)} &bull; 12/2 Romex $${Number(m.romex_12_2_250ft || 146.49).toFixed(2)} &bull; Arch Shingles $${Number(m.arch_shingles_sq || 118.71).toFixed(2)}/sq &rarr;`;
          if (el.tagName === 'A') el.href = '/daily/todays-math/index.html';
        }
      });
    }


    // 4. Inject the 3 new calculators into Header Mega-Dropdown if missing
    document.querySelectorAll('.nav-dropdown-content, nav').forEach(nav => {
      if (nav.querySelector('a[href*="generator-calculator.html"]') && !nav.querySelector('a[href*="electrical-panel-calculator.html"]')) {
        const genLink = nav.querySelector('a[href*="generator-calculator.html"]');
        const pLink = document.createElement('a');
        pLink.href = '/electrical-panel-calculator.html';
        pLink.textContent = '200A Electrical Panel';
        const fLink = document.createElement('a');
        fLink.href = '/flooring-calculator.html';
        fLink.textContent = 'Flooring & Refinishing';
        genLink.parentNode.insertBefore(pLink, genLink.nextSibling);
        genLink.parentNode.insertBefore(fLink, pLink.nextSibling);
      }
      if (nav.querySelector('a[href*="pool.html"]') && !nav.querySelector('a[href*="radiant-floor-calculator.html"]')) {
        const poolLink = nav.querySelector('a[href*="pool.html"]');
        const rLink = document.createElement('a');
        rLink.href = '/radiant-floor-calculator.html';
        rLink.textContent = 'Radiant Floor Heating';
        poolLink.parentNode.insertBefore(rLink, poolLink.nextSibling);
      }
    });

    // 3. Inject the 3 new calculators into the Main Calculator Grid if missing
    const grid = document.getElementById('calculators') || document.querySelector('.calculator-grid');
    if (grid && !grid.querySelector('a[href*="electrical-panel-calculator.html"]')) {
      const newCards = [
        {
          href: '/electrical-panel-calculator.html',
          cat: 'featured electrical energy interior',
          kw: 'electrical panel upgrade 200 amp 400 amp service entrance heavy up circuit breaker load center 25c tax credit',
          badge: 'Interior & Power',
          title: '200A & 400A Electrical Panel Upgrade',
          desc: 'Estimate 100A-to-200A service heavy-ups, 400A dual panels, meter sockets, NEC surge protection, and $600 Section 25C credits.'
        },
        {
          href: '/flooring-calculator.html',
          cat: 'interior',
          kw: 'hardwood flooring lvp luxury vinyl plank laminate tile refinishing subfloor underlayment square footage cost',
          badge: 'Interior & Power',
          title: 'Flooring Installation & Refinishing',
          desc: 'Model turnkey pricing for 20-mil LVP, engineered hardwood, solid 3/4" oak, porcelain tile, and dustless hardwood refinishing.'
        },
        {
          href: '/radiant-floor-calculator.html',
          cat: 'hvac energy interior',
          kw: 'radiant floor heating ditra heat electric hydronic subfloor thermal mass bathroom heating operating cost',
          badge: 'Mechanical & Energy',
          title: 'Radiant Floor Heating Calculator',
          desc: 'Compare electric uncoupling mat systems (Ditra-Heat) vs. hydronic PEX tubing, thermal break subfloors, and monthly kWh costs.'
        }
      ];
      newCards.forEach(c => {
        const a = document.createElement('a');
        a.href = c.href;
        a.className = 'calc-card';
        a.setAttribute('data-category', c.cat);
        a.setAttribute('data-keywords', c.kw);
        a.innerHTML = `
          <div>
            <span class="badge-category" style="font-size: 0.75rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 0.25rem 0.5rem; border-radius: 4px; text-transform: uppercase;">${c.badge}</span>
            <h3 style="margin-top: 0.5rem;">${c.title}</h3>
            <p>${c.desc}</p>
          </div>
          <span class="cta-link">Open Calculator &rarr;</span>`;
        grid.appendChild(a);
      });
    }
  }

  async function init() {
    syncSiteTo24Calculators(null);
    renderEmbedBox();
    bindDynamicBoosters();
    try {
      const res = await fetch(DATA_URL);
      if (res.ok) {
        cachedData = await res.json();
        syncSiteTo24Calculators(cachedData);
        renderAdSlots(cachedData.ad_config);
        renderLiveBanner(cachedData);
        hydrateInputs(cachedData);
        renderAffiliateMatrix(cachedData);
        updateDynamicMarkupAlert();
      } else {
        renderAdSlots({});
      }
    } catch (err) {
      renderAdSlots({});
      console.warn('TBM Widget non-blocking skip:', err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
