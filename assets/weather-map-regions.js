/**
 * WeatherGrid region registry — CL-WG-04.
 *
 * Region-scoped bboxes are fixed constants (owner spec): each region's box
 * follows the cloud-coverage area its meteorological broadcast uses, and is
 * checked against the catalogued place coordinates (apps/web-v2/catalog.v2.json)
 * so every live place inside the region stays inside the box:
 *
 * - tw  118–123°E / 21.5–26.5°N
 *   Owner base box 118–123°E / 21–26°N with outlying-island margin. The
 *   northmost catalogued place is Dongyin (tw-066, 26.365°N) and the
 *   southmost is Tainan-area 21.929°N, so the box is widened to 21.5–26.5°N.
 *   The 21.5°N south edge also keeps the Himawari-9 bundle (118–124°E /
 *   21.5–27°N) a full-cover source for the region.
 * - jp  122–146°E / 24–46°N (covers catalogued places 32.7–43.7°N,
 *   129.9–144.5°E).
 * - us  "US Mainland" per owner spec: 125°W–70.5°W / 25–49.5°N covering all
 *   63 CONUS places (25.8–48.9°N, 124.6–71.0°W). Alaska/Hawaii places lie
 *   outside the mainland box by definition and are not offered in this view.
 *
 * A data source is only listed for a region when its published bundle fully
 * covers that region's bbox. Source selection priority is photographer-first:
 * highest usable resolution / most complete photography fields first, all
 * free sources.
 */
(() => {
  const REGION_ORDER = ['tw', 'jp', 'us'];

  const REGION_BBOXES = {
    tw: {leftlon: 118, rightlon: 123, bottomlat: 21.5, toplat: 26.5},
    jp: {leftlon: 122, rightlon: 146, bottomlat: 24, toplat: 46},
    us: {leftlon: -125, rightlon: -70.5, bottomlat: 25, toplat: 49.5}
  };

  // Trilingual equivalent labels (zh-TW / en / ja) for the region cards.
  const REGION_LABELS = {
    tw: {'zh-TW': '台灣', en: 'Taiwan', ja: '台湾'},
    jp: {'zh-TW': '日本', en: 'Japan', ja: '日本'},
    us: {'zh-TW': '美國本土', en: 'US Mainland', ja: 'アメリカ本土'}
  };

  const REGION_CARD_META = {
    tw: {flag: '🇹🇼'},
    jp: {flag: '🇯🇵'},
    us: {flag: '🇺🇸'}
  };

  // Catalog-derived place extremes per region (apps/web-v2/catalog.v2.json,
  // opportunities[].navigation_targets lat/lon). Kept here so tests and
  // runtime can prove the region box still contains every live place.
  const PLACE_EXTREMES = {
    tw: {north: 26.36542, south: 21.929, west: 118.29849, east: 121.89314},
    jp: {north: 43.6620489, south: 32.7016613, west: 129.869083, east: 144.507319},
    // Mainland-only: Alaska/Hawaii places are outside the mainland box by
    // owner spec ("美國本土（或現有覆蓋區域）").
    us: {north: 48.8682, south: 25.76584, west: -124.638, east: -71.0372}
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
    if (!extreme || !region) return false;
    return extreme.south >= region.bottomlat && extreme.north <= region.toplat &&
      extreme.west >= region.leftlon && extreme.east <= region.rightlon;
  }

  /**
   * Filter a source catalog down to the sources that fully cover `regionId`.
   * `catalog` maps source id -> { coverage: {<regionId>: bbox}, ... }.
   * Returns ids in catalog insertion order (insertion order = priority).
   */
  function sourcesForRegion(regionId, catalog) {
    const region = normalizeBbox(REGION_BBOXES[regionId]);
    if (!region || !catalog) return [];
    return Object.keys(catalog).filter(id => {
      const entry = catalog[id] || {};
      return sourceCoversRegion(region, entry.coverage?.[regionId]);
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

  const api = {
    REGION_ORDER, REGION_BBOXES, REGION_LABELS, REGION_CARD_META, PLACE_EXTREMES,
    normalizeBbox, sourceCoversRegion, regionContainsPoint,
    regionContainsAllPlaces, sourcesForRegion, maskLayersForRegion
  };

  if (typeof window !== 'undefined') {
    window.WeatherMapRegions = api;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})();
