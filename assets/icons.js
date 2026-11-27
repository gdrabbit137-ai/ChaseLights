/* CL-UI-115 §1 — one inline SVG icon set for every metric and weather glyph.
 *
 * Why this file exists: every metric/weather symbol used to be an emoji literal
 * baked into assets/app.js. The same codepoint is drawn by a different font on
 * Windows, macOS, Android and iOS, so the eye glyph used for visibility looked
 * sharp on the desktop page and soft on the phone. Nothing in that path was a
 * second code path — it was one string, rendered by the platform emoji font.
 *
 * Contract:
 *   - CL_ICONS is a frozen map key → '<svg …>' built from `currentColor` strokes.
 *   - No hard-coded fill colours and no inline width/height: size and colour come
 *     from CSS (.cl-icon {width:1em;height:1em;stroke:currentColor;fill:none}).
 *   - Decorative glyphs carry aria-hidden="true"; the caller keeps its text label.
 *   - clIcon(key) returns the SVG string, or the historical emoji literal when the
 *     key is unknown, so an unmapped code still renders something.
 *
 * Load order: this file is a plain <script> loaded BEFORE assets/app.js, so the
 * globals exist when app.js builds its label tables.
 */
(function (root) {
  'use strict';

  // Every glyph is a 24×24 line drawing. `body` is the inner markup; the builder
  // wraps it in one <svg> so no string ever carries width/height or a fill colour.
  var SHAPES = {
    // ---------------------------------------------------------------- weather
    clear: '<circle cx="12" cy="12" r="4.2"/><path d="M12 2.6v2.6M12 18.8v2.6M2.6 12h2.6M18.8 12h2.6M5.4 5.4l1.9 1.9M16.7 16.7l1.9 1.9M18.6 5.4l-1.9 1.9M7.3 16.7l-1.9 1.9"/>',
    mostly_clear: '<circle cx="9.4" cy="9.4" r="3.5"/><path d="M9.4 2.8v2.1M2.8 9.4h2.1M4.9 4.9l1.5 1.5M13.9 4.9l-1.5 1.5M4.9 13.9l1.5-1.5"/><path d="M7.6 19.2h9.6a3.1 3.1 0 0 0 .3-6.2 4.5 4.5 0 0 0-8.5-1.2 3.7 3.7 0 0 0-1.4 7.4Z"/>',
    partly: '<path d="M8.2 3.6a3.2 3.2 0 1 0 0 6.4 3.2 3.2 0 0 0 0-6.4Z"/><path d="M8.2 1.6v1.2M3.1 6.8H1.9M5.2 3.8 4.3 2.9M11.2 3.8l.9-.9"/><path d="M8.4 20.4h9.3a3.2 3.2 0 0 0 .2-6.4 4.6 4.6 0 0 0-8.7-1.2 3.8 3.8 0 0 0-.8 7.6Z"/>',
    overcast: '<path d="M6.6 18.6h11a3.4 3.4 0 0 0 .2-6.8 4.8 4.8 0 0 0-9.1-1.3 4 4 0 0 0-2.1 8.1Z"/>',
    fog: '<path d="M6.4 8.6h7.2a2.6 2.6 0 0 0 .1-5.2 3.7 3.7 0 0 0-7-1"/><path d="M4 12.4h16M6 15.6h12M4.8 18.8h14.4"/>',
    drizzle: '<path d="M6.6 12.6h10.8a3.3 3.3 0 0 0 .2-6.6 4.7 4.7 0 0 0-8.9-1.2 3.9 3.9 0 0 0-2.1 7.8Z"/><path d="M8.6 15.4v1.8M12 15.4v2.8M15.4 15.4v1.8"/>',
    rain: '<path d="M6.6 11.6h10.8a3.3 3.3 0 0 0 .2-6.6 4.7 4.7 0 0 0-8.9-1.2 3.9 3.9 0 0 0-2.1 7.8Z"/><path d="M8.4 14.2l-1.4 4M12 14.2l-1.4 4M15.6 14.2l-1.4 4M18.4 14.2l-1 3"/>',
    showers: '<path d="M7.4 4.2 4.6 8.4h3.2L5.4 12.6"/><path d="M12.6 4.2l-2.8 4.2h3.2l-2.4 4.2"/><path d="M6.8 16h9.8a3 3 0 0 0 .2-6 4.4 4.4 0 0 0-8.3-1.1 3.6 3.6 0 0 0-1.7 7.1Z"/><path d="M9.4 18.6l-.9 2.6M14.6 18.6l-.9 2.6"/>',
    snow: '<path d="M6.8 11h10.4a3.3 3.3 0 0 0 .2-6.6 4.7 4.7 0 0 0-8.8-1.2A3.9 3.9 0 0 0 6.8 11Z"/><path d="M8.4 15.4v3.4M6.9 16.2l3 1.8M11.4 16.2l-3 1.8M15.6 15.4v3.4M14.1 16.2l3 1.8M18.6 16.2l-3 1.8"/>',
    snow_showers: '<path d="M6.8 10.6h10.4a3.3 3.3 0 0 0 .2-6.6 4.7 4.7 0 0 0-8.8-1.2A3.9 3.9 0 0 0 6.8 10.6Z"/><path d="M9.2 18.4h.02M12.2 20.4h.02M15.4 18.4h.02M12.2 15.6h.02"/>',
    thunder: '<path d="M6.6 10.6h9.8a3.2 3.2 0 0 0 .2-6.4 4.6 4.6 0 0 0-8.6-1.2 3.8 3.8 0 0 0-1.4 7.6Z"/><path d="M13.2 12.2 9.8 17h3.4l-1.6 4.4 4.4-5.8h-3.2l1.8-3.4Z"/>',

    // ---------------------------------------------------------------- subjects
    all: '<circle cx="12" cy="12" r="8.4"/><path d="M3.6 12h16.8M12 3.6c2.4 2.4 3.6 5.2 3.6 8.4S14.4 18 12 20.4C9.6 18 8.4 15.2 8.4 12S9.6 6 12 3.6Z"/>',
    mountain_view: '<path d="M2.4 19.2 9 7.2l4.2 7.2 2.4-3.6 6 8.4Z"/><path d="m6.6 12.6 2.4 1.8 2.2-1.4"/>',
    alpine_lake: '<path d="M2.4 15 8.4 5.4l4.8 6.6 2.4-2.4 6 5.4"/><path d="M3 19.2c1.8-1.2 3.6-1.2 5.4 0s3.6 1.2 5.4 0 3.6-1.2 5.4 0"/>',
    sunrise: '<path d="M3 17.4h18"/><path d="M6.6 17.4a5.4 5.4 0 0 1 10.8 0"/><path d="M12 2.8v3.6M4.9 5.6l2.1 2.1M19.1 5.6l-2.1 2.1M2.6 12.4h2.4M19 12.4h2.4"/>',
    sunset: '<path d="M3 17.4h18"/><path d="M6.6 17.4a5.4 5.4 0 0 1 10.8 0"/><path d="M12 6.6v-3.4M6.9 8l-2.1-2.1M17.1 8l2.1-2.1M2.6 12.4h2.4M19 12.4h2.4"/>',
    blue_hour: '<path d="M4 19.2h16"/><path d="M5.4 15.6 8.4 9l3 4.2 2.4-2.4 3.4 4.8"/><circle cx="17.4" cy="6" r="2.6"/>',
    sky_glow: '<path d="M3 18.6h18"/><path d="M6 18.6a6 6 0 0 1 12 0"/><path d="M12 3v2.4M3.8 8.4l1.8 1.2M20.2 8.4l-1.8 1.2M3 13.4h2.2M18.8 13.4H21"/>',
    cloud_sea: '<path d="M3 15.6c1.8 0 1.8-1.6 3.6-1.6s1.8 1.6 3.6 1.6 1.8-1.6 3.6-1.6 1.8 1.6 3.6 1.6 1.8-1.6 3.6-1.6"/><path d="M3 19.4c1.8 0 1.8-1.6 3.6-1.6s1.8 1.6 3.6 1.6 1.8-1.6 3.6-1.6 1.8 1.6 3.6 1.6 1.8-1.6 3.6-1.6"/><path d="M7 10.6h10a2.8 2.8 0 0 0 0-5.6 4.2 4.2 0 0 0-8-1 3.4 3.4 0 0 0-2 6.6Z"/>',
    fog_mist: '<path d="M6.6 10h7.2a2.6 2.6 0 0 0 .1-5.2 3.7 3.7 0 0 0-7-1"/><path d="M4 13.4h16M6.4 16.6h12M4.6 19.8h14.8"/>',
    reflection: '<path d="M12 3v9.4"/><path d="M8.6 6.4 12 3l3.4 3.4"/><path d="M3 16.2c1.8-1.4 3.6-1.4 5.4 0s3.6 1.4 5.4 0 3.6-1.4 5.4 0"/><path d="M3 20c1.8-1.4 3.6-1.4 5.4 0s3.6 1.4 5.4 0 3.6-1.4 5.4 0"/>',
    sunbeam: '<circle cx="8" cy="7.6" r="3"/><path d="M11.2 10.4 20 19.2M13.6 15.6 20 15.6M13.6 15.6 13.6 22"/>',
    milky_way: '<path d="M3.4 20.6c3-6.4 6-9.6 9.6-12.2 2.6-1.8 5-3.4 7.6-6.4"/><path d="M6.6 21.2c2.6-4.8 5.4-7.6 8.6-10"/><circle cx="17.4" cy="6.4" r="1"/><circle cx="9.6" cy="13" r=".9"/><circle cx="14.6" cy="9.6" r=".8"/>',
    long_exposure: '<path d="M5 8.4h14"/><path d="M5 12h14"/><path d="M7 15.6h10"/><path d="M9 19.2h6"/><circle cx="12" cy="4.6" r="1.6"/>',
    city_night: '<path d="M3.4 20.4h17.2"/><path d="M5 20.4V9.6l4.4-2.2v13"/><path d="M9.4 20.4V12l4.6 2.2v6.2"/><path d="M14 20.4V8.6l4.6 2v9.8"/><path d="M6.6 12.4h1.2M11.2 15.4h1.2M16 13.4h1.2M16 16.8h1.2"/><path d="M18.4 5.2a2.2 2.2 0 1 0 0 4.4"/>',
    city_view: '<path d="M2.8 20.2h18.4"/><path d="M4.6 20.2V11l4-1.8V20.2"/><path d="M8.6 20.2V6.4l4.6 2.4v11.4"/><path d="M13.2 20.2V12l5.2 2.2v6"/><path d="M6.2 13.6h1M10.4 10.4h1M15.2 15h1"/>',
    coast: '<path d="M2.6 14.2c1.8-1.6 3.6-1.6 5.4 0s3.6 1.6 5.4 0 3.6-1.6 5.4 0"/><path d="M2.6 18c1.8-1.6 3.6-1.6 5.4 0s3.6 1.6 5.4 0 3.6-1.6 5.4 0"/><path d="M7 10.6 12 3l5 7.6"/>',
    forest: '<path d="M8 19.4 3.4 12h2.4L2.8 7h3.2L9 3.4 11.6 7h3.2l-3 5h2.4L9.8 19.4Z"/><path d="M9 19.4v2.2"/><path d="M17 20v-5.4M15 16.4l2-1.8 2 1.8"/>',
    geology: '<path d="M2.6 20.4 9 8.6l3.6 6 2.6-3.4 6.2 9.2Z"/><path d="m6.4 13.4 2.6 1.6 2-1.2M13.4 16.4l2 1.2 2.2-1.6"/>',
    lake: '<path d="M3.2 14.4c2-1.8 4-1.8 6 0s4 1.8 6 0 4-1.8 6 0"/><path d="M3.2 18.4c2-1.8 4-1.8 6 0s4 1.8 6 0 4-1.8 6 0"/><path d="M5 11 9.4 4.6l4.4 6.4"/>',
    landscape: '<path d="M4.8 5h14.4a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4.8a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z"/><path d="m4.8 16.4 4.6-5.4 3.2 3.4 2.4-2.4 4.2 4.4"/><circle cx="16.4" cy="9.2" r="1.4"/>',
    waterfall: '<path d="M4 4.4h6.6v3.8H4z"/><path d="M7.3 8.2v3.4M5.6 11.6v4.8M9 11.6v5.6"/><path d="M3 20.4c1.6-1.4 3.2-1.4 4.8 0s3.2 1.4 4.8 0 3.2-1.4 4.8 0 3.2 1.4 4.8 0"/>',
    snow_scene: '<path d="M12 3v18M4.2 7.4l15.6 9.2M19.8 7.4 4.2 16.6"/><path d="m9.6 4.4 2.4 2 2.4-2M9.6 19.6l2.4-2 2.4 2"/>',
    aurora: '<path d="M3 13.4c2.4-6.4 4.8-6.4 7.2 0s4.8 6.4 7.2 0 2.4-5.4 3.6-7.4"/><path d="M3 18.6c2.4-4.6 4.8-4.6 7.2 0s4.8 4.6 7.2 0 2.4-4 3.6-5.2"/><path d="M2.4 21.4h19.2"/>',

    // ---------------------------------------------------------------- metrics
    visibility: '<path d="M2.2 12s3.6-5.6 9.8-5.6S21.8 12 21.8 12 18.2 17.6 12 17.6 2.2 12 2.2 12Z"/><circle cx="12" cy="12" r="2.9"/>',
    cloud: '<path d="M6.8 18.6h10.4a3.4 3.4 0 0 0 .2-6.8 4.8 4.8 0 0 0-9.1-1.2 4 4 0 0 0-1.5 8Z"/>',
    wind: '<path d="M3 8.4h11.4a2.6 2.6 0 1 0-2.6-2.6"/><path d="M3 12.6h15.6a2.6 2.6 0 1 1-2.6 2.6"/><path d="M3 16.8h8"/>',
    humidity: '<path d="M12 3.2s5.6 6 5.6 9.8A5.6 5.6 0 0 1 6.4 13c0-3.8 5.6-9.8 5.6-9.8Z"/><path d="M9.6 13.6a2.6 2.6 0 0 0 2.6 2.6"/>',
    temperature: '<path d="M10 14.2V5.4a2 2 0 1 1 4 0v8.8a3.8 3.8 0 1 1-4 0Z"/><path d="M12 8.6v7.8"/>',
    elevation: '<path d="M2.6 20.4 9.6 7.6l4.2 7.4 2.4-3.2 5.2 8.6Z"/><path d="M9.6 7.6V3.2M7.8 4.8 9.6 3l1.8 1.8"/>',
    azimuth: '<path d="M12 21.4V12h8.4"/><path d="M12 12 6.8 6.8"/><path d="m13.6 4.6 2.6 1.6 1.6-2.6"/><circle cx="12" cy="12" r="1.2"/>',
    moon: '<path d="M15.6 3.4a8.6 8.6 0 1 0 5 15.2 8.6 8.6 0 0 1-5-15.2Z"/>',
    star: '<path d="m12 3.4 2.6 5.6 6 .8-4.4 4.2 1.1 6-5.3-3-5.3 3 1.1-6L3.4 9.8l6-.8Z"/>'
  };

  // The historical emoji literals stay as FALLBACK DATA only: an unknown key
  // (a WMO code the forecast adds tomorrow) still renders a glyph, and the
  // caller is never left with an empty cell.
  var FALLBACK = {
    clear: '☀️', mostly_clear: '🌤️', partly: '⛅', overcast: '☁️', fog: '🌫️',
    drizzle: '🌦️', rain: '🌧️', showers: '🌦️', snow: '❄️', snow_showers: '🌨️',
    thunder: '⛈️', visibility: '👁', cloud: '☁️', wind: '💨', humidity: '💧',
    temperature: '🌡️', elevation: '⛰', azimuth: '☀', moon: '🌙', star: '⭐',
    all: '🌐', mountain_view: '🏔️', alpine_lake: '🏔️', sunrise: '🌅',
    sunset: '🌇', blue_hour: '🔵', sky_glow: '🌈', cloud_sea: '☁️',
    fog_mist: '🌫️', reflection: '🪞', sunbeam: '🌤️', milky_way: '🌌',
    long_exposure: '💧', city_night: '🌃', city_view: '🏙️', coast: '🌊',
    forest: '🌲', geology: '🪨', lake: '🏞️', landscape: '📷',
    waterfall: '💦', snow_scene: '❄️', aurora: '🌌'
  };

  // WMO weather code → glyph key (Open-Meteo WMO set, exactly the codes the
  // app's WMO_ICONS table carried).
  var WMO_SHAPE = {
    0: 'clear', 1: 'mostly_clear', 2: 'partly', 3: 'overcast',
    45: 'fog', 48: 'fog',
    51: 'drizzle', 53: 'drizzle', 55: 'drizzle', 56: 'rain', 57: 'rain',
    61: 'rain', 63: 'rain', 65: 'rain', 66: 'rain', 67: 'rain',
    71: 'snow', 73: 'snow', 75: 'snow', 77: 'snow',
    80: 'showers', 81: 'rain', 82: 'thunder',
    85: 'snow_showers', 86: 'snow_showers',
    95: 'thunder', 96: 'thunder', 99: 'thunder'
  };
  // Emoji fallback for a WMO code that has no shape (mirrors the old
  // wmoIcon() range fallback so an unknown code still renders).
  function wmoFallbackEmoji(code) {
    var c = Number(code);
    if (!isFinite(c)) return '';
    if (c >= 95) return '⛈️';
    if (c >= 80) return '🌧️';
    if (c >= 50) return '🌦️';
    return '☁️';
  }

  function svg(key, body) {
    return '<svg class="cl-icon" data-cl-icon="' + key + '" viewBox="0 0 24 24" ' +
      'aria-hidden="true" focusable="false" stroke="currentColor" stroke-width="1.5" ' +
      'stroke-linecap="round" stroke-linejoin="round" fill="none">' + body + '</svg>';
  }

  var CL_ICONS = {};
  Object.keys(SHAPES).forEach(function (key) { CL_ICONS[key] = svg(key, SHAPES[key]); });
  Object.keys(WMO_SHAPE).forEach(function (code) {
    CL_ICONS[code] = svg(code, SHAPES[WMO_SHAPE[code]]);
  });
  Object.freeze(CL_ICONS);

  // Update: the subject LABEL table (app.js) uses the 23 theme keys above, but
  // the committed subject-cards artifact names a subset with its own genre
  // vocabulary (geological_landform, overlook, blue_hour_city, …). CL-UI-115 §1
  // covers EVERY subject a card/filter/summary can render, so the artifact's
  // extra genres alias onto the closest drawn shape rather than falling back to
  // plain text. The alias key still rides the SVG as data-cl-icon, so a chip can
  // be asserted against the artifact's own genre name.
  var ALIAS = {
    geological_landform: 'geology', overlook: 'mountain_view', blue_hour_city: 'blue_hour',
    overcast_soft: 'overcast', night_sky: 'milky_way', golden_hour: 'sky_glow',
    alpenglow: 'sunset', seasonal_plant: 'forest', star_trails: 'star',
    moonlit_scene: 'moon', tidal: 'coast', general: 'all', drift_ice: 'snow_scene',
    blue_tears: 'star', firefly: 'star', astro: 'star', astrophotography: 'star',
    snow_ice: 'snow_scene', city: 'city_view', architecture: 'city_view'
  };

  function shapeKey(key) {
    var k = String(key == null ? '' : key);
    if (SHAPES[k]) return k;
    if (WMO_SHAPE[k]) return WMO_SHAPE[k];
    if (ALIAS[k] && SHAPES[ALIAS[k]]) return ALIAS[k];
    return null;
  }

  function clIcon(key) {
    var k = String(key == null ? '' : key);
    if (CL_ICONS[k]) return CL_ICONS[k];
    var sk = shapeKey(k);
    if (sk) return svg(k, SHAPES[sk]);
    if (/^-?\d+(\.\d+)?$/.test(k)) return wmoFallbackEmoji(k);
    return FALLBACK[k] || '';
  }

  root.CL_ICONS = CL_ICONS;
  root.CL_ICON_EMOJI = Object.freeze(FALLBACK);
  root.CL_WMO_ICON_EMOJI = Object.freeze({0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️', 45: '🌫️', 48: '🌫️', 51: '🌦️', 53: '🌦️', 55: '🌦️', 56: '🌧️', 57: '🌧️', 61: '🌧️', 63: '🌧️', 65: '🌧️', 66: '🌧️', 67: '🌧️', 71: '🌨️', 73: '🌨️', 75: '❄️', 77: '❄️', 80: '🌦️', 81: '🌧️', 82: '⛈️', 85: '🌨️', 86: '🌨️', 95: '⛈️', 96: '⛈️', 99: '⛈️'});
  root.clIcon = clIcon;
  root.clIconKeyForWmo = function (code) { return WMO_SHAPE[String(code)] || null; };
})(typeof window !== 'undefined' ? window : this);
