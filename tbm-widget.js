/**
 * The Buyer's Math - Universal Living Hub & Monetization Widget (tbm-widget.js)
 * Pre-wired with verified production IDs:
 *   - Amazon Associates: nfagiolo-20
 *   - Google AdSense: ca-pub-1199906473460957
 *   - CJ Affiliate (Angi & SwitchBot): Enterprise 8090259 / PID 101896838
 *   - Google Analytics 4: G-V4GTQSCFW6
 */
(function () {
  const DATA_URL = '/data/live-baselines.json';
  const DEFAULT_TAG = 'nfagiolo-20';
  const DEFAULT_ADSENSE = 'ca-pub-1199906473460957';
  const DEFAULT_ANGI = 'https://www.jdoqocy.com/click-101896838-17142784';
  const DEFAULT_SWITCHBOT = 'https://www.dpbolvw.net/click-101896838-15310710';

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

  function buildSparklineSVG(dataPoints) {
    if (!dataPoints || dataPoints.length < 2) return '';
    const width = 180, height = 40;
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
          <div style="font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;">30-Day Cost Index</div>
          <div style="font-size:13px;font-weight:700;color:#0f172a;">${sign}${delta}% Trend</div>
        </div>
        <svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" aria-label="30 day cost trend sparkline">
          <polyline fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" points="${points}" />
        </svg>
      </div>`;
  }

  function renderLiveBanner(data) {
    const el = document.getElementById('tbm-live-banner');
    if (!el || !data || !data.metrics) return;
    const m = data.metrics;
    const banner = data.seasonal_banner || {
      headline: 'Daily Home & Utility Operating Cost Index',
      summary: 'Live meteorological, utility, and material cost telemetry.'
    };
    el.innerHTML = `
      <div style="border-left:4px solid #2563eb;background:#ffffff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);margin-bottom:20px;border:1px solid #e2e8f0;border-left-width:5px;">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px;">
          <div>
            <span style="background:#dbeafe;color:#1e40af;font-size:11px;font-weight:700;padding:3px 8px;border-radius:4px;text-transform:uppercase;">
              Live Telemetry &bull; Updated ${data.formatted_date || data.last_updated}
            </span>
            <h3 style="margin:8px 0 4px;font-size:16px;color:#0f172a;">${banner.headline}</h3>
          </div>
          ${buildSparklineSVG(data.history_30d)}
        </div>
        <p style="margin:0 0 12px;font-size:14px;color:#334155;line-height:1.5;">${banner.summary}</p>
        <div style="display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:#475569;border-top:1px solid #f1f5f9;padding-top:10px;align-items:center;">
          <span><strong>Avg Grid Rate:</strong> $${Number(m.kwh_rate || 0.172).toFixed(3)}/kWh</span>
          <span><strong>Propane:</strong> $${Number(m.propane_gal || 2.65).toFixed(2)}/gal</span>
          <span><strong>Gasoline:</strong> $${Number(m.gasoline_gal || 3.35).toFixed(2)}/gal</span>
          <span><strong>Soil Temp:</strong> ${m.soil_temp_f || 56.8}&deg;F</span>
          <span><strong>Peak Sun:</strong> ${m.solar_peak_hours || 4.3} hrs/day</span>
          <a href="/intel/latest.html" style="margin-left:auto;color:#2563eb;font-weight:700;text-decoration:none;">Open Today's Full Dispatch &rarr;</a>
        </div>
      </div>`;
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
      const target = inputs[0] || document.querySelector('input[type="number"]');
      if (target) {
        target.dispatchEvent(new Event('input', { bubbles: true }));
        target.dispatchEvent(new Event('change', { bubbles: true }));
      }
      if (typeof window.calcRun === 'function') {
        try { window.calcRun(); } catch (e) {}
      }
    }
  }

  function renderAffiliateMatrix(data) {
    const el = document.getElementById('tbm-unit-matrix');
    if (!el || !data || !data.catalog) return;
    const cat = el.getAttribute('data-category') || 'energy';
    const items = data.catalog[cat] || data.catalog.energy || [];
    const tag = data.associate_tag || DEFAULT_TAG;
    const adCfg = data.ad_config || {};
    const angiUrl = adCfg.angi_url || DEFAULT_ANGI;
    const switchbotUrl = adCfg.switchbot_url || DEFAULT_SWITCHBOT;

    const rows = items.map((item, idx) => {
      const badge = idx === 0
        ? `<span style="display:inline-block;background:#dcfce7;color:#166534;font-size:11px;font-weight:700;padding:2px 6px;border-radius:4px;margin-bottom:4px;">&#9733; Best Unit Math Pick</span><br>`
        : '';
      const url = `https://www.amazon.com/dp/${item.asin}?tag=${encodeURIComponent(tag)}`;
      return `
        <tr style="border-bottom:1px solid #e2e8f0;">
          <td style="padding:12px 8px;">
            ${badge}<strong style="color:#0f172a;font-size:14px;">${item.name}</strong>
            <div style="font-size:12px;color:#64748b;margin-top:2px;">${item.note}</div>
          </td>
          <td style="padding:12px 8px;white-space:nowrap;">
            <div style="font-size:11px;color:#64748b;">${item.spec_label}</div>
            <div style="font-size:14px;font-weight:700;color:#0f172a;">${item.unit_cost}</div>
          </td>
          <td style="padding:12px 8px;text-align:right;white-space:nowrap;">
            <a href="${url}" target="_blank" rel="sponsored nofollow noopener"
               style="display:inline-block;background:#0f172a;color:#ffffff;font-size:12px;font-weight:600;padding:8px 12px;border-radius:6px;text-decoration:none;">
              Verify on Amazon &rarr;
            </a>
          </td>
        </tr>`;
    }).join('');

    el.innerHTML = `
      <div style="margin-top:24px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;background:#ffffff;">
        <div style="background:#f8fafc;padding:12px 16px;border-bottom:1px solid #cbd5e1;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <strong style="font-size:15px;color:#0f172a;">Unit Economics &amp; Equipment ROI Matrix</strong>
          <span style="font-size:11px;color:#64748b;">Sorted by Cost-Per-Output Efficiency</span>
        </div>
        <div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;text-align:left;"><tbody>${rows}</tbody></table></div>
        <div style="padding:12px 16px;background:#eff6ff;border-top:1px solid #bfdbfe;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;">
          <div style="font-size:13px;color:#1e3a8a;">
            <strong>Need Licensed Installation or Local Quotes?</strong> Compare prescreened contractor bids vs. DIY math:
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a href="${angiUrl}" target="_blank" rel="sponsored nofollow noopener"
               style="background:#2563eb;color:#ffffff;font-size:12px;font-weight:700;padding:7px 12px;border-radius:6px;text-decoration:none;">
              Compare 3 Local Pros (Angi) &rarr;
            </a>
            <a href="${switchbotUrl}" target="_blank" rel="sponsored nofollow noopener"
               style="background:#0f766e;color:#ffffff;font-size:12px;font-weight:700;padding:7px 12px;border-radius:6px;text-decoration:none;">
              Smart Telemetry Sensors (SwitchBot) &rarr;
            </a>
          </div>
        </div>
        <div style="padding:8px 16px;background:#f8fafc;font-size:11px;color:#64748b;border-top:1px solid #e2e8f0;">
          Disclosure: As an Amazon Associate (${tag}) and CJ Affiliate partner (PID 101896838), The Buyer's Math earns from qualifying purchases and contractor quote requests.
        </div>
      </div>`;
  }

  function renderEmbedBox() {
    const el = document.getElementById('tbm-embed-box');
    if (!el) return;
    const url = window.location.origin + window.location.pathname;
    const title = document.title.split('|')[0].trim();
    const snippet = `<iframe src="${url}?embed=true" width="100%" height="460" style="border:1px solid #cbd5e1;border-radius:8px;" loading="lazy"></iframe><p style="font-size:12px;margin-top:4px;">Powered by <a href="${url}">${title} - The Buyer's Math</a></p>`;
    el.innerHTML = `
      <details style="margin-top:20px;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;background:#f8fafc;">
        <summary style="cursor:pointer;font-size:13px;font-weight:600;color:#334155;">+ Embed This Live Calculator on Your Site (Free)</summary>
        <div style="margin-top:10px;">
          <textarea readonly onclick="this.select()" style="width:100%;height:65px;font-family:monospace;font-size:11px;padding:8px;border:1px solid #cbd5e1;border-radius:4px;background:#fff;box-sizing:border-box;">${snippet.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
        </div>
      </details>`;
  }

  async function init() {
    renderEmbedBox();
    try {
      const res = await fetch(DATA_URL);
      if (res.ok) {
        const data = await res.json();
        renderAdSlots(data.ad_config);
        renderLiveBanner(data);
        hydrateInputs(data);
        renderAffiliateMatrix(data);
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
