/**
 * WeatherGrid deep-link parameter module — CL-WG-19.
 *
 * Pure functions that turn weather-map.html URL parameters into initial page
 * state. The card pages (homepage) link here with:
 *
 *   ?region=tw|jp|us|ak|hi   initial region (overrides localStorage memory;
 *                            no param = last browsed region; neither = tw)
 *   &spot=tw-036            spot id from the catalog (focus the camera)
 *   &layer=<layer key>      initial photography layer (region-validated)
 *   &subject=<genre>        card best-subject genre → most relevant layer
 *                           via SUBJECT_LAYER_CANDIDATES (fail-closed to the
 *                           region's default main layer when unmappable or
 *                           unavailable)
 *   &focus=lat,lon,zoom     camera center + zoom (「景點＋拍攝範圍」 view)
 *
 * Fail-closed rule: ANY invalid parameter (unknown region, unknown layer,
 * malformed focus, malformed spot id) degrades to the default behavior and
 * never throws. URL state sync uses history.replaceState (never pushes a
 * history entry).
 */
(() => {
  // Region default main layer: the layer a fresh region lands on (and the
  // fallback when a deep-link layer/subject mapping is unavailable).
  const DEFAULT_MAIN_LAYER = 'low_cloud_percent';

  // localStorage key for the region-context memory (CL-WG-19 #5).
  const REGION_MEMORY_KEY = 'weathergrid.region';

  // Valid spot-id shape, e.g. tw-036 / jp-012 / ak-004.
  const SPOT_ID_PATTERN = /^[a-z]{2}-\d{2,4}$/i;

  const KNOWN_REGIONS = ['tw', 'jp', 'us', 'ak', 'hi'];

  /**
   * Subject genre → ordered layer candidates (CL-WG-19 #4). Pure mapping
   * table. First candidate that the active region actually offers wins;
   * unknown/unordered genres return null → caller falls back to the region
   * default main layer. Genre vocabulary follows the V2 condition-contract
   * `genre_template` values (taxonomy_v004).
   */
  const SUBJECT_LAYER_CANDIDATES = {
    // 霧景/低雲/雲海 → 低雲圖層
    cloud_sea: ['low_cloud_percent'],
    overcast_soft: ['low_cloud_percent', 'total_cloud_percent'],
    fog: ['low_cloud_percent'],
    fog_mist: ['low_cloud_percent'],
    // 霧霾 → AOD
    haze: ['aerosol_optical_depth_550nm'],
    // 夜景/銀河/暗空 → 夜間雲圖或暗空證據（VIIRS 夜間燈光）
    city_night: ['nighttime_lights_radiance_nw_cm2_sr'],
    night_sky: ['nighttime_lights_radiance_nw_cm2_sr'],
    milky_way: ['nighttime_lights_radiance_nw_cm2_sr'],
    astro: ['nighttime_lights_radiance_nw_cm2_sr'],
    // 日出/日落/霞光 → 雲量＋短波
    sunrise: ['total_cloud_percent', 'shortwave_flux_w_m2'],
    sunset: ['total_cloud_percent', 'shortwave_flux_w_m2'],
    golden_hour: ['total_cloud_percent', 'shortwave_flux_w_m2'],
    // 風景通透 → 能見度
    mountain_view: ['visibility_km'],
    overlook: ['visibility_km'],
    geological_landform: ['visibility_km'],
    landscape: ['visibility_km'],
    reflection: ['visibility_km'],
    scenic_visibility: ['visibility_km']
  };

  /**
   * Ordered layer candidates for a subject genre, or null when the genre
   * cannot be mapped (fail-closed to the region default at the caller).
   */
  function subjectLayerCandidates(genre) {
    if (typeof genre !== 'string') return null;
    const key = genre.trim().toLowerCase();
    const direct = SUBJECT_LAYER_CANDIDATES[key];
    if (direct) return direct.slice();
    // Subtype forms like "night_sky_milkyway" / "fog_mist_valley".
    for (const [genreKey, layers] of Object.entries(SUBJECT_LAYER_CANDIDATES)) {
      if (key.includes(genreKey)) return layers.slice();
    }
    return null;
  }

  /**
   * First candidate present in the region's available layer keys.
   */
  function resolveSubjectLayer(genre, availableLayerKeys) {
    const candidates = subjectLayerCandidates(genre);
    if (!candidates) return null;
    const available = new Set(availableLayerKeys || []);
    for (const key of candidates) {
      if (available.has(key)) return key;
    }
    return null;
  }

  /**
   * Parse the URL deep-link parameters. `paramsLike` is anything with a
   * `get()` (URLSearchParams) — or null/undefined for "no parameters".
   * Options: { validRegions, validLayers, maxZoom }.
   * Returns { region, spot, layer, subject, focus, urlKeys, hasAny }:
   *   region  — valid region id from the URL, else null (caller falls back
   *             to localStorage memory / 'tw').
   *   layer   — valid layer id from the URL, else null (invalid → default).
   *   focus   — {lat, lon, zoom} with finite numbers, else null.
   *   urlKeys — set of deep-link keys actually present in the URL (kept on
   *             replaceState while the entry region stays unchanged).
   */
  function parseDeepLinkParams(paramsLike, options = {}) {
    const validRegions = new Set(options.validRegions || KNOWN_REGIONS);
    const validLayers = options.validLayers ? new Set(options.validLayers) : null;
    const maxZoom = Number.isFinite(Number(options.maxZoom)) ? Number(options.maxZoom) : 13;
    const out = {
      region: null, spot: null, layer: null, subject: null, focus: null,
      urlKeys: [], hasAny: false
    };
    if (!paramsLike || typeof paramsLike.get !== 'function') return out;
    const get = name => {
      try { return paramsLike.get(name); } catch (_) { return null; }
    };
    const rawRegion = get('region');
    const rawSpot = get('spot');
    const rawLayer = get('layer');
    const rawSubject = get('subject');
    const rawFocus = get('focus');
    for (const key of ['region', 'spot', 'layer', 'subject', 'focus']) {
      if (get(key) !== null) out.urlKeys.push(key);
    }
    out.hasAny = out.urlKeys.length > 0;
    // Fail-closed: an unknown region name simply yields null (default path).
    if (typeof rawRegion === 'string' && validRegions.has(rawRegion.trim().toLowerCase())) {
      out.region = rawRegion.trim().toLowerCase();
    }
    if (typeof rawSpot === 'string' && SPOT_ID_PATTERN.test(rawSpot.trim())) {
      out.spot = rawSpot.trim().toLowerCase();
    }
    if (typeof rawLayer === 'string' && rawLayer.trim()) {
      const key = rawLayer.trim();
      // Without a validLayers catalog the string passes through untouched;
      // with one, unknown keys fail closed to the default layer.
      if (!validLayers || validLayers.has(key)) out.layer = key;
    }
    if (typeof rawSubject === 'string' && rawSubject.trim()) {
      out.subject = rawSubject.trim().toLowerCase();
    }
    if (typeof rawFocus === 'string') {
      const rawParts = rawFocus.split(',');
      const parts = rawParts.map(s => (s.trim() === '' ? NaN : Number(s.trim())));
      if (parts.length === 3 && parts.every(Number.isFinite)) {
        const [lat, lon, zoom] = parts;
        if (Math.abs(lat) <= 90 && Math.abs(lon) <= 180 && zoom >= 1) {
          out.focus = { lat, lon, zoom: Math.min(zoom, maxZoom) };
        }
      }
    }
    return out;
  }

  /**
   * Initial region resolution order (CL-WG-19 #1): URL region param →
   * localStorage memory → 'tw'. The stored value is fail-closed too: a
   * corrupted/non-region value is ignored.
   */
  function resolveInitialRegion({urlRegion, storedRegion} = {}) {
    if (urlRegion) return urlRegion;
    if (typeof storedRegion === 'string' && KNOWN_REGIONS.includes(storedRegion)) {
      return storedRegion;
    }
    return 'tw';
  }

  /**
   * Spot deep-link camera: a bbox centered on the spot, sized adaptively
   * from the region bbox scale (owner spec: zoom 約 9–11，涵蓋景點與周邊
   * 拍攝範圍). Half-spans = 2% of the region bbox span, clamped to sane
   * photography-view bounds; the result is clamped so the fitted view stays
   * inside the region bbox. Small frames (hi) get tighter views than large
   * ones (us). Returns a view bbox or null.
   */
  function spotFocusBbox(lat, lon, regionId, regionBboxes) {
    const bbox = regionBboxes && regionBboxes[regionId];
    const la = Number(lat), lo = Number(lon);
    if (!bbox || !Number.isFinite(la) || !Number.isFinite(lo)) return null;
    const lonSpan = Number(bbox.rightlon) - Number(bbox.leftlon);
    const latSpan = Number(bbox.toplat) - Number(bbox.bottomlat);
    if (!(lonSpan > 0) || !(latSpan > 0)) return null;
    const lonHalf = Math.min(Math.max(lonSpan * 0.02, 0.25), 1.2);
    const latHalf = Math.min(Math.max(latSpan * 0.02, 0.2), 0.9);
    // Keep the view box inside the region bbox (shift, never shrink below
    // the minimum, so the camera can always settle at photography zoom).
    let left = lo - lonHalf, right = lo + lonHalf;
    let bottom = la - latHalf, top = la + latHalf;
    if (left < bbox.leftlon) { right += bbox.leftlon - left; left = bbox.leftlon; }
    if (right > bbox.rightlon) { left -= right - bbox.rightlon; right = bbox.rightlon; }
    if (bottom < bbox.bottomlat) { top += bbox.bottomlat - bottom; bottom = bbox.bottomlat; }
    if (top > bbox.toplat) { bottom -= top - bbox.toplat; top = bbox.toplat; }
    return {leftlon: left, rightlon: right, bottomlat: bottom, toplat: top};
  }

  /**
   * Canvas-fallback bbox for a focus camera: approximates the MapLibre
   * viewport span at the given zoom (Web Mercator, 512px tile space) so the
   * pre-MapLibre render and the eventual jumpTo agree.
   */
  function focusBboxFromCamera(lat, lon, zoom) {
    const la = Number(lat), lo = Number(lon), z = Number(zoom);
    if (![la, lo, z].every(Number.isFinite) || z < 1) return null;
    const lonSpan = Math.min(Math.max(360 / Math.pow(2, z), 0.02), 360);
    const latSpan = Math.min(Math.max(lonSpan * 0.75, 0.02), 180);
    return {
      leftlon: Math.max(-180, lo - lonSpan / 2),
      rightlon: Math.min(180, lo + lonSpan / 2),
      bottomlat: Math.max(-85, la - latSpan / 2),
      toplat: Math.min(85, la + latSpan / 2)
    };
  }

  /**
   * Validated camera for &focus=lat,lon,zoom: clamped zoom, world-range
   * center. Returns {center:[lon,lat], zoom} or null (fail-closed).
   */
  function focusCamera(focus, maxZoom = 13) {
    if (!focus) return null;
    const lat = Number(focus.lat), lon = Number(focus.lon), zoom = Number(focus.zoom);
    if (![lat, lon, zoom].every(Number.isFinite)) return null;
    if (Math.abs(lat) > 90 || Math.abs(lon) > 180) return null;
    const cap = Number.isFinite(Number(maxZoom)) ? Number(maxZoom) : 13;
    return {center: [lon, lat], zoom: Math.max(1, Math.min(zoom, cap))};
  }

  const api = {
    DEFAULT_MAIN_LAYER, REGION_MEMORY_KEY, SPOT_ID_PATTERN, KNOWN_REGIONS,
    SUBJECT_LAYER_CANDIDATES,
    subjectLayerCandidates, resolveSubjectLayer,
    parseDeepLinkParams, resolveInitialRegion,
    spotFocusBbox, focusBboxFromCamera, focusCamera
  };

  if (typeof window !== 'undefined') {
    window.WeatherMapDeepLink = api;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})();