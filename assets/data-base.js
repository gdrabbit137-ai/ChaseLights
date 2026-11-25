/* CL-PAGES-04: single switch for the data plane.
 *
 * The heavy JSON (weathergrid/ + weather_details/) now lives in Cloudflare R2
 * at data.chaselights.app; the static shell stays on Cloudflare Pages. Set
 * window.CL_DATA_BASE before the app scripts run and every ./weathergrid/ or
 * ./weather_details/ URL is rewritten onto that origin. Leave it unset (or
 * empty) and nothing changes — local dev and the old same-origin layout keep
 * working, which is what makes the cut-over reversible.
 */
(function () {
  var base = typeof window.CL_DATA_BASE === 'string' ? window.CL_DATA_BASE.replace(/\/+$/, '') : '';
  window.clUrl = function (url) {
    if (!base || typeof url !== 'string') return url;
    if (url.charAt(0) !== '.' || url.charAt(1) !== '/') return url; // absolute / already external
    if (url.indexOf('./weathergrid/') !== 0 && url.indexOf('./weather_details/') !== 0) return url;
    return base + url.slice(1);
  };
})();
