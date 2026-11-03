/**
 * WeatherGrid region registry — CL-WG-04.
 *
 * Region-scoped bboxes are fixed constants (owner spec): each region's box
 * follows the cloud-coverage area its meteorological broadcast uses, and is
 * checked against the catalogued place coordinates (apps/web-v2/catalog.v2.json)
 * so every live place inside the region stays inside the box:
 *
 * - tw  105–145°E / 5–40°N
 *   CL-WG-13 (owner ruling 2026-11-04, with the CWA official satellite
 *   cloud-map screenshot 「台灣地區的圖我想要這麼大」): the display range is
 *   the CWA official cloud-map extent over the western Pacific. The global
 *   free sources (GFS / ICON / CAMS) publish full-frame bundles over this
 *   exact box, so the main render is one single source with no seam; the
 *   regional high-resolution models (CWA WRF 3 km / JMA MSM / Himawari-9)
 *   stay listed as model options and render honestly only inside their own
 *   coverage (blank outside, never a fabricated value).
 * - jp  122–146°E / 24–46°N (covers catalogued places 32.7–43.7°N,
 *   129.9–144.5°E).
 * - us  "US Mainland" per owner spec: 125°W–70.5°W / 25–49.5°N covering all
 *   63 CONUS places (25.8–48.9°N, 124.6–71.0°W). Alaska/Hawaii places are
 *   routed to their own independent regional frames (owner ruling
 *   2026-11-03: 阿拉斯加跟夏威夷可以獨立框架) and are NOT part of this view.
 * - ak  Alaska independent frame: 158°W–132°W / 55–69.5°N, widened around the
 *   20 catalogued Alaska places (57.83–68.13°N, 155.79–134.41°W) with margin.
 * - hi  Hawaii independent frame: owner spec 160.3°W–154.8°W / 18.8–22.4°N.
 *   The catalog currently has NO Hawaii places, so the region renders an
 *   honest empty state (no fabricated places or data).
 *
 * A data source is only listed for a region when its published bundle fully
 * covers that region's bbox. Source selection priority is photographer-first:
 * highest usable resolution / most complete photography fields first, all
 * free sources. NASA Black Marble (VIIRS) is fail-closed: it is not listed
 * for a new region until its provenance-verified download covers that bbox.
 */
(() => {
  const REGION_ORDER = ['tw', 'jp', 'us', 'ak', 'hi'];

  const REGION_BBOXES = {
    // CL-WG-13: CWA official satellite cloud-map extent (105–145°E / 5–40°N).
    tw: {leftlon: 105, rightlon: 145, bottomlat: 5, toplat: 40},
    jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
    us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5},
    ak: {leftlon: -158, rightlon: -132, bottomlat: 55, toplat: 69.5},
    hi: {leftlon: -160.3, rightlon: -154.8, bottomlat: 18.8, toplat: 22.4}
  };

  // Trilingual equivalent labels (zh-TW / en / ja) for the region cards.
  const REGION_LABELS = {
    tw: {'zh-TW': '台灣', en: 'Taiwan', ja: '台湾'},
    jp: {'zh-TW': '日本', en: 'Japan', ja: '日本'},
    us: {'zh-TW': '美國本土', en: 'US Mainland', ja: 'アメリカ本土'},
    ak: {'zh-TW': '阿拉斯加', en: 'Alaska', ja: 'アラスカ'},
    hi: {'zh-TW': '夏威夷', en: 'Hawaii', ja: 'ハワイ'}
  };

  const REGION_CARD_META = {
    tw: {flag: '🇹🇼'},
    jp: {flag: '🇯🇵'},
    us: {flag: '🇺🇸'},
    ak: {flag: '🇺🇸'},
    hi: {flag: '🇺🇸'}
  };

  // Catalog-derived place extremes per region (apps/web-v2/catalog.v2.json,
  // opportunities[].navigation_targets lat/lon). Kept here so tests and
  // runtime can prove the region box still contains every live place.
  const PLACE_EXTREMES = {
    tw: {north: 26.36542, south: 21.929, west: 118.29849, east: 121.89314},
    jp: {north: 43.6620489, south: 32.7016613, west: 129.869083, east: 144.507319},
    // Mainland-only: Alaska/Hawaii places are routed to their own
    // independent regional frames (ak/hi), never to this box.
    us: {north: 48.8682, south: 25.76584, west: -124.638, east: -71.0372},
    // Catalog-derived extremes for the 20 Alaska places.
    ak: {north: 68.133, south: 57.82759, west: -155.79193, east: -134.40617},
    // The catalog has no Hawaii places yet; null = vacuously empty so the
    // region stays an honest empty state until real places are catalogued.
    hi: null
  };

  function normalizeBbox(bbox) {
    if (!bbox) return null;
    const leftlon = Number(bbox.leftlon);
    const rightlon = Number(bbox.rightlon);
    const bottomlat = Number(bbox.bottomlat);
    const toplat = Number(bbox.toplat);
    if (![leftlon, rightlon, bottomlat, toplat].every(Number.isFinite)) return null;
    if (rightlon <= leftlon || toplat <= bottomlat) return null;
    return {leftlon, rightlon, bottomlat, toplat};
  }

  // A source covers a region only when its data bbox fully contains the
  // region bbox (owner rule: 蓋不滿的源在該地區的下拉中直接不提供).
  function sourceCoversRegion(regionBbox, sourceBbox) {
    const region = normalizeBbox(regionBbox);
    const source = normalizeBbox(sourceBbox);
    if (!region || !source) return false;
    return source.leftlon <= region.leftlon &&
      source.rightlon >= region.rightlon &&
      source.bottomlat <= region.bottomlat &&
      source.toplat >= region.toplat;
  }

  function regionContainsPoint(regionId, lat, lon) {
    const region = normalizeBbox(REGION_BBOXES[regionId]);
    if (!region) return false;
    return lat >= region.bottomlat && lat <= region.toplat &&
      lon >= region.leftlon && lon <= region.rightlon;
  }

  function regionContainsAllPlaces(regionId) {
    const extreme = PLACE_EXTREMES[regionId];
    const region = normalizeBbox(REGION_BBOXES[regionId]);
    if (!region) return false;
    // A region with no catalogued places is vacuously complete (honest
    // empty state) — it must not be failed for missing data.
    if (!extreme) return true;
    return extreme.south >= region.bottomlat && extreme.north <= region.toplat &&
      extreme.west >= region.leftlon && extreme.east <= region.rightlon;
  }

  /**
   * Route a place coordinate to its region: ak and hi are independent frames
   * checked before the mainland us box so outlying US places never fall back
   * into the US Mainland card. Returns null for coordinates in no region.
   */
  function regionForPoint(lat, lon) {
    for (const id of ['ak', 'hi', 'jp', 'us', 'tw']) {
      if (regionContainsPoint(id, lat, lon)) return id;
    }
    return null;
  }

  /**
   * Filter a source catalog down to the sources offered for `regionId`.
   * `catalog` maps source id -> { coverage: {<regionId>: bbox}, ... }.
   * Returns ids in catalog insertion order (insertion order = priority).
   *
   * CL-WG-13: global full-frame sources (gfs/icon/cams) keep the strict
   * cover-gate — they must fully contain the region bbox or they are not
   * offered. Regional high-resolution models (cwa/jma/himawari) and
   * limited-extent observation layers (viirs) are offered as REGIONAL MODEL
   * OPTIONS whenever a published coverage entry exists for the region: they
   * render only inside their own coverage and stay honestly blank outside
   * (the layer panel / QC panel labels this), so full containment is no
   * longer required for them.
   */
  const REGIONAL_MODEL_SOURCES = new Set(['cwa', 'jma', 'himawari', 'viirs']);

  function sourcesForRegion(regionId, catalog) {
    const region = normalizeBbox(REGION_BBOXES[regionId]);
    if (!region || !catalog) return [];
    return Object.keys(catalog).filter(id => {
      const entry = catalog[id] || {};
      const coverage = normalizeBbox(entry.coverage?.[regionId]);
      if (!coverage) return false;
      if (REGIONAL_MODEL_SOURCES.has(id)) return true;
      return sourceCoversRegion(region, coverage);
    });
  }

  /**
   * Layer masking: the UI must never offer a layer key no enabled source of
   * this region can serve. `enabledSources` is the list of loaded source
   * entries ({id, layers:[...]}) for the active region; a key survives only
   * if some enabled source declares it AND that source actually carries the
   * field (`fieldsBySource` maps source id -> fields object from the bundle).
   */
  function maskLayersForRegion(candidateKeys, enabledSources, fieldsBySource) {
    const usable = new Set();
    for (const source of enabledSources || []) {
      const fields = fieldsBySource?.[source.id] || {};
      for (const key of source.layers || []) {
        if (fields[key] !== undefined) usable.add(key);
      }
    }
    return (candidateKeys || []).filter(key => usable.has(key));
  }

  /**
   * CL-WG-06 camera confinement helpers. Each region's map camera is limited
   * to that region's data bbox: maxBounds sits on the bbox edges, minZoom sits just below the zoom that fits
   * the bbox (a fixed floor, CL-WG-07), and a fixed maxZoom keeps spot-level
   * detail.
   */
  function cameraBounds(bbox) {
    const region = normalizeBbox(bbox);
    if (!region) return null;
    return [[region.leftlon, region.bottomlat], [region.rightlon, region.toplat]];
  }

  // Allow a small margin below the bbox-fit zoom so the fitted region always
  // stays the dominant view and the camera can never pull back to a
  // continent view. CL-WG-07: the floor is a FIXED value derived only from
  // fitZoom, never from the current zoom — otherwise zooming in raises the
  // floor with it and the minus button can no longer return to the full
  // region view.
  function cameraMinZoom(fitZoom) {
    const fit = Number(fitZoom);
    if (!Number.isFinite(fit)) return null;
    return Math.max(0, fit - 0.05);
  }

  const CAMERA_MAX_ZOOM = 13;

  const api = {
    REGION_ORDER, REGION_BBOXES, REGION_LABELS, REGION_CARD_META, PLACE_EXTREMES,
    REGIONAL_MODEL_SOURCES,
    normalizeBbox, sourceCoversRegion, regionContainsPoint,
    regionContainsAllPlaces, regionForPoint, sourcesForRegion, maskLayersForRegion,
    cameraBounds, cameraMinZoom, CAMERA_MAX_ZOOM
  };

  if (typeof window !== 'undefined') {
    window.WeatherMapRegions = api;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})();
