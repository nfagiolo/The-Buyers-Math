/**
 * The Buyers Math - Universal Living Hub Widget (tbm-widget.js)
 * Zero external dependencies. Safe for root, /intel/, /guides/, and /articles/.
 */
(function () {
  const DATA_URL = '/data/live-baselines.json';

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
    if (!el) return;
    const m = data.metrics;
    el.innerHTML = `
      <div style="border-left:4px solid #2563eb;background:#ffffff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.08);margin-bottom:20px;">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;margin-bottom:10px;">
          <div>
            <span style="background:#dbeafe;color:#1e40af;font-size:11px;font-weight:700;padding:3px 8px;border-radius:4px;text-transform:uppercase;">
              Live Telemetry • Updated ${data.formatted_date}
            </span>
            <h3 style="margin:8px 0 4px;font-size:16px;color:#0f172a;">${data.seasonal_banner.headline}</h3>
          </div>
          ${buildSparklineSVG(data.history_30d)}
        </div>
        <p style="margin:0 0 12px;font-size:14px;color:#334155;line-height:1.5;">${data.seasonal_banner.summary}</p>
        <div style="display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:#475569;border-top:1px solid #f1f5f9;padding-top:10px;">
          <span><strong>Avg Grid Rate:</strong> $${m.kwh_rate.toFixed(3)}/kWh</span>
          <span><strong>Propane:</strong> $${m.propane_gal.toFixed(2)}/gal</span>
          <span><strong>Gasoline:</strong> $${m.gasoline_gal.toFixed(2)}/gal</span>
          <span><strong>Soil Temp:</strong> ${m.soil_temp_f}°F</span>
          <span><strong>Peak Sun:</strong> ${m.solar_peak_hours} hrs/day</span>
          <a href="/intel/latest.html" style="margin-left:auto;color:#2563eb;font-weight:700;text-decoration:none;">Open Today's Full Dispatch →</a>
        </div>
      </div>`;
  }

  function hydrateInputs(data) {
    const m = data.metrics;
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

    if (changed && inputs.length > 0) {
      inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  function renderAffiliateMatrix(data) {
    const el = document.getElementById('tbm-unit-matrix');
    if (!el || !data.catalog) return;
    const cat = el.getAttribute('data-category') || 'energy';
    const items = data.catalog[cat] || data.catalog.energy;
    const tag = data.associate_tag || 'thebuyersmath-20';

    const rows = items.map((item, idx) => {
      const badge = idx === 0
        ? `<span style="display:inline-block;background:#dcfce7;color:#166534;font-size:11px;font-weight:700;padding:2px 6px;border-radius:4px;margin-bottom:4px;">★ Best Unit Math Pick</span><br>`
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
              Verify Price →
            </a>
          </td>
        </tr>`;
    }).join('');

    el.innerHTML = `
      <div style="margin-top:24px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;background:#ffffff;">
        <div style="background:#f8fafc;padding:12px 16px;border-bottom:1px solid #cbd5e1;display:flex;justify-content:space-between;align-items:center;">
          <strong style="font-size:15px;color:#0f172a;">Unit Economics & Equipment ROI Matrix</strong>
          <span style="font-size:11px;color:#64748b;">Sorted by Cost-Per-Output Efficiency</span>
        </div>
        <div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;text-align:left;"><tbody>${rows}</tbody></table></div>
        <div style="padding:8px 16px;background:#f8fafc;font-size:11px;color:#64748b;border-top:1px solid #e2e8f0;">
          As an Amazon Associate, The Buyers Math earns from qualifying purchases.
        </div>
      </div>`;
  }

  function renderEmbedBox() {
    const el = document.getElementById('tbm-embed-box');
    if (!el) return;
    const url = window.location.origin + window.location.pathname;
    const title = document.title.split('|')[0].trim();
    const snippet = `<iframe src="${url}?embed=true" width="100%" height="460" style="border:1px solid #cbd5e1;border-radius:8px;" loading="lazy"></iframe><p style="font-size:12px;margin-top:4px;">Powered by <a href="${url}">${title} - The Buyers Math</a></p>`;
    el.innerHTML = `
      <details style="margin-top:20px;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;background:#f8fafc;">
        <summary style="cursor:pointer;font-size:13px;font-weight:600;color:#334155;">+ Embed This Live Calculator on Your Site (Free)</summary>
        <div style="margin-top:10px;">
          <textarea readonly onclick="this.select()" style="width:100%;height:65px;font-family:monospace;font-size:11px;padding:8px;border:1px solid #cbd5e1;border-radius:4px;background:#fff;">${snippet.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
        </div>
      </details>`;
  }

  async function init() {
    renderEmbedBox();
    try {
      const res = await fetch(DATA_URL);
      if (res.ok) {
        const data = await res.json();
        renderLiveBanner(data);
        hydrateInputs(data);
        renderAffiliateMatrix(data);
      }
    } catch (err) {
      console.warn('TBM Widget non-blocking skip:', err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
