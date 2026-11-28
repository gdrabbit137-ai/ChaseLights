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

    // ------------------------------------------------- navigation & panels
    // CL-UI-116: the four navigational glyphs that stayed emoji because they
    // point somewhere instead of measuring something. Each is its own drawing —
    // `subject` is a stack of framed stills (the subject LIST), never the camera
    // (`general`) or a peak (`mountain_view`); `map` is the folded sheet, its
    // pin is the point.
    subject: '<path d="M4.6 3.4h11.2a1.6 1.6 0 0 1 1.6 1.6v8.6a1.6 1.6 0 0 1-1.6 1.6H4.6A1.6 1.6 0 0 1 3 13.6V5a1.6 1.6 0 0 1 1.6-1.6Z"/><path d="M3.6 9 6.6 6.2l3.4 3.2"/><path d="M6.6 17.6h11a1.6 1.6 0 0 0 1.6-1.6V8"/><path d="M9.6 21.2h9.4a1.6 1.6 0 0 0 1.6-1.6v-8"/>',
    map_pin: '<path d="M12 21.2c4.4-4.8 6.8-8 6.8-11a6.8 6.8 0 1 0-13.6 0c0 3 2.4 6.2 6.8 11Z"/><circle cx="12" cy="9.8" r="2.4"/>',
    map: '<path d="M9 4.4 3.6 6.8v13L9 17.4l6 2.4 5.4-2.4v-13L15 6.8Z"/><path d="M9 4.4v13M15 6.8v13"/>',
    weather_overview: '<circle cx="8.8" cy="8.2" r="3"/><path d="M8.8 2.8v1.6M3.6 8.2H5M4.9 4.3l1.2 1.2M12.7 4.3l-1.2 1.2M2.8 13.2h1.8"/><path d="M8.6 20.4h9.2a3.2 3.2 0 0 0 .2-6.4 4.6 4.6 0 0 0-8.6-1.2 3.8 3.8 0 0 0-.8 7.6Z"/>',

    // ---------------------------------------------------------------- metrics
    visibility: '<path d="M2.2 12s3.6-5.6 9.8-5.6S21.8 12 21.8 12 18.2 17.6 12 17.6 2.2 12 2.2 12Z"/><circle cx="12" cy="12" r="2.9"/>',
    cloud: '<path d="M6.8 18.6h10.4a3.4 3.4 0 0 0 .2-6.8 4.8 4.8 0 0 0-9.1-1.2 4 4 0 0 0-1.5 8Z"/>',
    // CL-UI-119: the cloud BASE — the cloud deck sits high with a short arrow
    // rising toward it (how high the deck is above this place), never the
    // `cloud` dome, the `fog` bands, the `elevation` peak+arrow or the
    // `weather_overview` sun+cloud. The owner read the old shared mountain as
    // 「the same quantity twice」 next to the terrain elevation.
    cloud_base: '<path d="M8.2 10.4h7.6a2.9 2.9 0 0 0 .1-5.8 4.1 4.1 0 0 0-7.9-1 3.4 3.4 0 0 0 .2 6.8Z"/><path d="M12 21.6V14.4"/><path d="M9.2 17.2 12 14.4l2.8 2.8"/>',
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
    thunder: '⛈️', visibility: '👁', cloud: '☁️', cloud_base: '☁️', wind: '💨', humidity: '💧',
    temperature: '🌡️', elevation: '⛰', azimuth: '☀', moon: '🌙', star: '⭐',
    all: '🌐', mountain_view: '🏔️', alpine_lake: '🏔️', sunrise: '🌅',
    sunset: '🌇', blue_hour: '🔵', sky_glow: '🌈', cloud_sea: '☁️',
    fog_mist: '🌫️', reflection: '🪞', sunbeam: '🌤️', milky_way: '🌌',
    long_exposure: '💧', city_night: '🌃', city_view: '🏙️', coast: '🌊',
    forest: '🌲', geology: '🪨', lake: '🏞️', landscape: '📷',
    waterfall: '💦', snow_scene: '❄️', aurora: '🌌',
    // the artifact's own genre vocabulary (same emoji the old alias produced)
    geological_landform: '🪨', overlook: '🏔️', blue_hour_city: '🔵', overcast_soft: '☁️',
    night_sky: '🌌', golden_hour: '🌈', alpenglow: '🌇', seasonal_plant: '🌸',
    star_trails: '⭐', moonlit_scene: '🌙', tidal: '🌊', general: '📷',
    drift_ice: '🧊', blue_tears: '⭐', firefly: '⭐', astro: '🔭',
    astrophotography: '📷', snow_ice: '❄️', snow_ice_night: '❄️', misty_forest: '🌫️',
    volcanic_glow: '🌋', city: '🏙️', architecture: '🏛️',
    subject: '🎞', map_pin: '📍', map: '🗺️', weather_overview: '🌦️'
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

  // The subject LABEL table (app.js) names 23 themes, but the committed
  // subject-cards artifact speaks its own genre vocabulary
  // (`genre_short_names`: geological_landform, overlook, misty_forest,
  // snow_ice_night, volcanic_glow, …). CL-UI-115 §1 covers EVERY subject a
  // card / filter row / summary / modal can render, so each of those genres
  // gets a drawing here.
  //
  // They are their OWN shapes, never an alias onto a neighbouring key. An alias
  // made 山景 (mountain_view) and 眺望 (overlook) draw the identical 99-byte
  // mountain, and 金山 (alpenglow) / 夕陽 (sunset) were one edit away from the
  // same collision: two rows of a subject list showing the same picture read as
  // one repeated subject, not two. Two keys may share a shape ONLY when the
  // user-visible LABEL is the same subject; no such pair exists in this
  // dictionary, so every key below is unique path data (guarded by
  // cl-ui-115-icon-set.test.mjs, which hashes the glyph of every subject key).
  var ALIAS = {
    // landform: horizontal strata + a fault line (a cut face, not a peak)
    geological_landform: '<path d="M2.6 8.6c3.4-2 6.6 1.4 9.6 0s6-2.6 9.2-.6"/><path d="M2.6 13.4c3.4-2 6.6 1.4 9.6 0s6-2.6 9.2-.6"/><path d="M2.6 18.2c3.4-2 6.6 1.4 9.6 0s6-2.6 9.2-.6"/><path d="M8.4 5.4 15 21.6"/>',
    // overlook: a railed platform on a cliff, sightlines running out to the view
    overlook: '<path d="M3 19.6h9.4"/><path d="M3 19.6 4.4 11.4h7l1.2 8.2"/><path d="M4.4 8.4h7M7.9 8.4v3"/><path d="M15.8 6.6h5.6M15.8 10.2h4.4M15.8 13.8h3.2"/>',
    // blue hour over a city: towers + a crescent (blue_hour is peaks + a disc)
    blue_hour_city: '<path d="M3 20.4h18"/><path d="M4.6 20.4v-8l4-2.4v10.4"/><path d="M8.6 20.4v-6l4.4 2.2v3.8"/><path d="M13 20.4V9.6l4.6 2.2v8.6"/><path d="M20.4 4.4a2.6 2.6 0 1 0 2 4.4 3.2 3.2 0 0 1-2-4.4Z"/>',
    // soft overcast: a stacked cloud deck (the plain overcast is one cloud)
    overcast_soft: '<path d="M4.2 15.2h9.4a3 3 0 0 0 .2-6 4.3 4.3 0 0 0-8.1-1.1 3.6 3.6 0 0 0-1.5 7.1Z"/><path d="M13.2 20.2h6.2a2.4 2.4 0 0 0 0-4.8 3.4 3.4 0 0 0-6.4-.9"/>',
    // night sky: a constellation (milky_way is a band with dust specks)
    night_sky: '<path d="M4 6.6 7 9.4 10.4 8 13.6 11.2 17 10.2 20 13"/><circle cx="4" cy="6.6" r="1"/><circle cx="7" cy="9.4" r="1"/><circle cx="10.4" cy="8" r="1"/><circle cx="13.6" cy="11.2" r="1"/><circle cx="17" cy="10.2" r="1"/><circle cx="20" cy="13" r="1"/><path d="M5.6 19.2h.02M9 21h.02M15.4 19.6h.02"/>',
    // golden hour: a low sun disc with long rays over a ground line (sky_glow is a dome)
    golden_hour: '<path d="M2.8 19.6h18.4"/><circle cx="12" cy="13.4" r="3.2"/><path d="M12 3.2v4.2M4.6 6.4l2.6 2.6M19.4 6.4l-2.6 2.6M2.6 13.4h2.6M18.8 13.4h2.6"/>',
    // alpenglow: a peak lit from behind by a glow arc with rays (sunset is a dome on a flat line)
    alpenglow: '<path d="M2.4 20.4 8.8 8.6l3.4 5.6 2.2-2.8 6.4 9Z"/><path d="M6.4 8a6.4 6.4 0 0 1 10.2 1.4"/><path d="M4.6 5.2 6.2 6.6M17.6 3.6l-.6 2.2M11 3.2v2.2"/>',
    // seasonal flora: a flower on a stem (forest is conifers)
    seasonal_plant: '<circle cx="12" cy="8.6" r="1.8"/><path d="M12 6.8a2.8 2.8 0 1 1 2.6-1.2M12 10.4a2.8 2.8 0 1 0 2.6 1.2M9.6 8.6a2.8 2.8 0 1 0-1.4 2.6M14.4 8.6a2.8 2.8 0 1 1 1.4 2.6"/><path d="M12 12.4v8.2"/><path d="M12 16.4c-2.2 0-3.4-1.4-3.6-3.2 2.2-.2 3.4 1.2 3.6 3.2Z"/>',
    // star trails: concentric arcs around the pole (a bare star is one polygon)
    star_trails: '<circle cx="12" cy="20.2" r="1.2"/><path d="M9.8 20.2a2.2 2.2 0 0 1 4.4 0"/><path d="M6.6 20.2a5.4 5.4 0 0 1 10.8 0"/><path d="M3.2 20.2a8.8 8.8 0 0 1 17.6 0"/>',
    // moonlit scene: a crescent over two water lines (moon alone is just the crescent)
    moonlit_scene: '<path d="M14.6 3.4a6.6 6.6 0 1 0 4.4 10.6 6.6 6.6 0 0 1-4.4-10.6Z"/><path d="M2.8 17.4c1.6-1.2 3.2-1.2 4.8 0s3.2 1.2 4.8 0 3.2-1.2 4.8 0 3.2 1.2 4.8 0"/><path d="M2.8 20.6c1.6-1.2 3.2-1.2 4.8 0s3.2 1.2 4.8 0 3.2-1.2 4.8 0 3.2 1.2 4.8 0"/>',
    // tide: a water line with rising/falling level arrows (coast is surf + a headland)
    tidal: '<path d="M2.6 16.4c1.8-1.4 3.6-1.4 5.4 0s3.6 1.4 5.4 0 3.6-1.4 5.4 0"/><path d="M2.6 20.2c1.8-1.4 3.6-1.4 5.4 0s3.6 1.4 5.4 0 3.6-1.4 5.4 0"/><path d="M18.6 3.4v7.8M16.8 5.2l1.8-1.8 1.8 1.8M16.8 9.4l1.8 1.8 1.8-1.8"/>',
    // general ("shootable"): a camera (the `all` filter keeps the globe)
    general: '<path d="M3 8.4h3.4L8 6h8l1.6 2.4H21v10.2H3Z"/><circle cx="12" cy="13.4" r="3.4"/>',
    // drift ice: floes riding a wave (snow_scene is a bare snowflake)
    drift_ice: '<path d="M3.4 18.2c1.4-1.2 2.8-1.2 4.2 0s2.8 1.2 4.2 0 2.8-1.2 4.2 0 2.8 1.2 4.2 0"/><path d="M4.6 14.4 6.4 9.8h3.6l1.4 4.6Z"/><path d="M13.4 14.4l1.2-3.4h3.4l1 3.4Z"/>',
    // blue tears: glowing specks in the surf + a sparkle (reflection is an arrow into water)
    blue_tears: '<path d="M2.6 12.4c1.8-1.4 3.6-1.4 5.4 0s3.6 1.4 5.4 0 3.6-1.4 5.4 0"/><path d="M2.6 17.4c1.8-1.4 3.6-1.4 5.4 0s3.6 1.4 5.4 0 3.6-1.4 5.4 0"/><circle cx="7" cy="20.4" r=".9"/><circle cx="13" cy="20.8" r=".9"/><circle cx="18.4" cy="20.2" r=".9"/><path d="M16.6 4.4v4M14.6 6.4h4M15.2 5l2.8 2.8M18 5l-2.8 2.8"/>',
    // firefly: a winged insect with a glow (a star is a polygon)
    firefly: '<path d="M12 8.6v7.8"/><path d="M12 10.4C9.4 8 6.6 7.4 4.8 9.2s1 4.6 4.2 4.4"/><path d="M12 10.4c2.6-2.4 5.4-3 7.2-1.2s-1 4.6-4.2 4.4"/><circle cx="12" cy="5.4" r="1.6"/><path d="M10.8 17.6 9.4 21M13.2 17.6l1.4 3.4"/>',
    // astronomy: a telescope on a tripod
    astro: '<path d="M3.6 9.4 15.4 3.6l2.4 4.6L6 14Z"/><path d="M8.6 13.2 12 20.4M12 20.4l3.4-7.2M8.6 20.4h6.8"/><path d="M17.8 3.2l2.2-1"/>',
    // astrophotography: a camera aimed at stars (a tripod alone is `astro`)
    astrophotography: '<path d="M5.4 11.6h13.2a1.6 1.6 0 0 1 1.6 1.6v6a1.6 1.6 0 0 1-1.6 1.6H5.4a1.6 1.6 0 0 1-1.6-1.6v-6a1.6 1.6 0 0 1 1.6-1.6Z"/><circle cx="12" cy="16.2" r="2.4"/><path d="M9.6 11.6 10.8 9.8h2.4l1.2 1.8"/><path d="M4 6.6 5.2 5.4M17.6 4.4V2.6M20.4 7.4l1.4-.8"/>',
    // snow & ice: an ice block with a crack and a snow cap (snow_scene is a snowflake)
    snow_ice: '<path d="M4 13.2h16v6.6H4Z"/><path d="M8.4 13.2 10.6 19.8M15.6 13.2l-1.6 6.6"/><path d="M7.6 6.2 12 2.2l4.4 4M9.8 8.4l2.2 1.8 2.2-1.8"/>',
    // night snow & ice: the same ice ground under a crescent (a daylight scene)
    snow_ice_night: '<path d="M14.6 3.2a4.6 4.6 0 1 0 3.2 7.4 4.6 4.6 0 0 1-3.2-7.4Z"/><path d="M6.4 12.6v6.4M3.8 14.2l5.2 3.2M9 14.2l-5.2 3.2"/><path d="M2.4 21h19.2"/>',
    // misty forest: conifers behind mist bands (fog_mist has no trees, forest has no mist)
    misty_forest: '<path d="M7.6 3.6 3.4 10.4h2.2l-2 4.4h8l-2-4.4h2.2Z"/><path d="M7.6 14.8v2.4"/><path d="M16.8 7 13.8 12h1.8l-1.6 3.2h5.6L18 12h1.8Z"/><path d="M16.8 15.2v2"/><path d="M2.4 19h11.2M7.4 21.4h14.2"/>',
    // volcanic glow: a cratered cone with a lava channel and glow rays
    volcanic_glow: '<path d="M2.6 20.4 8.6 8.4h6.8l5.6 12Z"/><path d="M8.6 8.4c1.2-1.2 2.4-1.2 3.4 0 1.2 1.2 2.2 1.2 3.4 0"/><path d="M11 20.4l1.2-6 1.4 6"/><path d="M3.4 12.6l-1.6-1M20.6 12.6l1.6-1M12 2.6v2.4"/>',
    // city: a dense skyline, no windows (city_view is three detailed towers)
    city: '<path d="M2.6 20.6h18.8"/><path d="M4 20.6v-6.4h3.2v6.4M7.2 20.6V8.4h3.4v12.2M10.6 20.6v-9.2h3.2v9.2M13.8 20.6V5.6h3.6v15M17.4 20.6v-7.4h3v7.4"/>',
    // architecture: a portico with columns (a skyline is `city`)
    architecture: '<path d="M3.4 9.6 12 3.4l8.6 6.2"/><path d="M5.6 9.6h12.8"/><path d="M7.4 11.4v6.4M12 11.4v6.4M16.6 11.4v6.4"/><path d="M4.4 20.6h15.2M6.4 17.8h11.2"/>'
  };
  var CL_ICONS = {};
  Object.keys(SHAPES).forEach(function (key) { CL_ICONS[key] = svg(key, SHAPES[key]); });
  Object.keys(WMO_SHAPE).forEach(function (code) {
    CL_ICONS[code] = svg(code, SHAPES[WMO_SHAPE[code]]);
  });

  // The artifact's genre vocabulary is a first-class part of the same map, so a
  // look-up by either name (theme key or artifact genre) hits the frozen table.
  Object.keys(ALIAS).forEach(function (k) { SHAPES[k] = ALIAS[k]; });
  Object.keys(ALIAS).forEach(function (k) { CL_ICONS[k] = svg(k, ALIAS[k]); });
  Object.freeze(CL_ICONS);

  function shapeKey(key) {
    var k = String(key == null ? '' : key);
    if (SHAPES[k]) return k;
    if (WMO_SHAPE[k]) return WMO_SHAPE[k];
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
  // The artifact-genre key list, so a test can enumerate the full subject
  // vocabulary without re-parsing this file.
  root.CL_SUBJECT_GENRES = Object.freeze(Object.keys(ALIAS));
  root.CL_ICON_EMOJI = Object.freeze(FALLBACK);
  root.CL_WMO_ICON_EMOJI = Object.freeze({0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️', 45: '🌫️', 48: '🌫️', 51: '🌦️', 53: '🌦️', 55: '🌦️', 56: '🌧️', 57: '🌧️', 61: '🌧️', 63: '🌧️', 65: '🌧️', 66: '🌧️', 67: '🌧️', 71: '🌨️', 73: '🌨️', 75: '❄️', 77: '❄️', 80: '🌦️', 81: '🌧️', 82: '⛈️', 85: '🌨️', 86: '🌨️', 95: '⛈️', 96: '⛈️', 99: '⛈️'});
  root.clIcon = clIcon;
  root.clIconKeyForWmo = function (code) { return WMO_SHAPE[String(code)] || null; };
})(typeof window !== 'undefined' ? window : this);
