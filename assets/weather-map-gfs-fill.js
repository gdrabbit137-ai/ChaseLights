/**
 * WeatherGrid GFS bbox-outside fill — CL-WG-11 (Taiwan pilot).
 *
 * When the selected main-source layer has no data outside its own bundle bbox
 * (e.g. Himawari-9 2 km, CWA WRF 3 km on the TW region frame) and the GFS
 * 0.25° bundle publishes a field with IDENTICAL semantics (same field key),
 * the bare-basemap area outside the main bbox is rendered from the GFS
 * bundle instead. Inside the main bbox the main source always wins — the GFS
 * fill never overwrites it. A feather band (~0.5° wide, outward from the main
 * bbox edge) ramps the GFS fill alpha 0 → 1 so the seam is a gradient, not a
 * hard edge. The seam band is mixed provenance and is labeled honestly in the
 * QC panel (see updateQc in weather-map.js).
 *
 * Honest-degradation rules: layers whose semantics do not exist in the GFS
 * bundle (Himawari satellite cloud mask / cloud top height, CAMS AOD/PM2.5,
 * VIIRS night lights, CWA temperature / RH / precip_total / shortwave flux)
 * are NEVER filled with a different-semantics field — they stay blank
 * outside the bbox. The pilot is scoped to the Taiwan region only.
 */
(() => {
  // Feather band width in degrees, measured outward from the main bbox edge.
  const GFS_FILL_BAND_DEG = 0.5;

  // GFS bundle fields that share the EXACT key and semantics with the
  // browser layer keys. Anything not listed here must not be filled.
  const GFS_FILL_FIELDS = new Set([
    'total_cloud_percent',
    'low_cloud_percent',
    'mid_cloud_percent',
    'high_cloud_percent',
    'visibility_km',
    'precip_rate_mm_h',
    'wind_speed_10m_m_s',
    'wind_direction_10m_deg'
  ]);

  // CL-WG-11 pilot scope: Taiwan region only.
  const GFS_FILL_REGIONS = new Set(['tw']);

  function gfsFillFieldAvailable(layerKey) {
    return GFS_FILL_FIELDS.has(layerKey);
  }

  // Perpendicular distance (in degrees) from a point to the outside of a
  // normalized bbox; 0 when the point is inside.
  function gfsFillDistanceOutside(point, bbox) {
    if (!point || !bbox) return Infinity;
    return Math.max(
      0,
      bbox.leftlon - point.lon,
      point.lon - bbox.rightlon,
      bbox.bottomlat - point.lat,
      point.lat - bbox.toplat
    );
  }

  // Feather alpha for the GFS fill layer at a point: 0 inside the main bbox
  // (main source territory), ramping 0 → 1 across the band outside, then 1.
  function gfsFillFeatherAlpha(point, mainBbox, bandDeg = GFS_FILL_BAND_DEG) {
    const dist = gfsFillDistanceOutside(point, mainBbox);
    if (dist <= 0) return 0;
    const band = Number.isFinite(bandDeg) && bandDeg > 0 ? bandDeg : GFS_FILL_BAND_DEG;
    return Math.max(0, Math.min(1, dist / band));
  }

  // Nearest GFS frame to the main source's target valid time (frame-axis
  // alignment). Returns {frame, offset_minutes} or null.
  function nearestGfsFrame(gfsData, targetValidTime) {
    const frames = gfsData?.frames || [];
    if (!frames.length || !targetValidTime) return null;
    const targetMs = Date.parse(targetValidTime);
    if (!Number.isFinite(targetMs)) return null;
    let best = null;
    for (const frame of frames) {
      const ms = Date.parse(frame.valid_time_utc);
      if (!Number.isFinite(ms)) continue;
      const offsetMinutes = Math.round((ms - targetMs) / 60000);
      if (!best || Math.abs(offsetMinutes) < Math.abs(best.offset_minutes)) {
        best = {frame, offset_minutes: offsetMinutes};
      }
    }
    return best;
  }

  // Trigger conditions for the fill pass. Returns a plan object or null.
  // - region must be in the pilot scope (tw).
  // - the layer must have a same-semantics GFS field with frame data.
  // - the GFS bundle must extend beyond the region bbox (otherwise there is
  //   nothing it can contribute).
  // - the camera view must actually extend beyond the region bbox (the
  //   bare-basemap padding is exactly what the fill covers).
  // The feather seam is anchored on the REGION bbox edge: inside it the main
  // source always wins (fill alpha = 0), the ~0.5° band outside it ramps the
  // GFS fill 0 → 1.
  function gfsFillPlan({regionId, layerKey, gfsDataset, viewBbox, regionBbox}) {
    if (!regionId || !GFS_FILL_REGIONS.has(regionId)) return null;
    if (!gfsDataset?.frames?.length || !gfsDataset?.fields?.[layerKey]) return null;
    if (!gfsFillFieldAvailable(layerKey)) return null;
    const gfsBbox = gfsDataset.bbox;
    const region = regionBbox;
    if (!gfsBbox || !region || !viewBbox) return null;
    const view = {
      leftlon: Math.min(viewBbox.leftlon, viewBbox.rightlon),
      rightlon: Math.max(viewBbox.leftlon, viewBbox.rightlon),
      bottomlat: Math.min(viewBbox.bottomlat, viewBbox.toplat),
      toplat: Math.max(viewBbox.bottomlat, viewBbox.toplat)
    };
    const insideRegion = view.leftlon >= region.leftlon && view.rightlon <= region.rightlon &&
      view.bottomlat >= region.bottomlat && view.toplat <= region.toplat;
    if (insideRegion) return null;
    const gfsWider =
      gfsBbox.leftlon < region.leftlon || gfsBbox.rightlon > region.rightlon ||
      gfsBbox.bottomlat < region.bottomlat || gfsBbox.toplat > region.toplat;
    if (!gfsWider) return null;
    return {
      regionId, layerKey,
      main_bbox: {leftlon: region.leftlon, rightlon: region.rightlon,
        bottomlat: region.bottomlat, toplat: region.toplat},
      gfs_bbox: {leftlon: gfsBbox.leftlon, rightlon: gfsBbox.rightlon,
        bottomlat: gfsBbox.bottomlat, toplat: gfsBbox.toplat},
      band_deg: GFS_FILL_BAND_DEG
    };
  }

  const api = {
    GFS_FILL_BAND_DEG, GFS_FILL_FIELDS, GFS_FILL_REGIONS,
    gfsFillFieldAvailable, gfsFillDistanceOutside, gfsFillFeatherAlpha,
    nearestGfsFrame, gfsFillPlan
  };

  if (typeof window !== 'undefined') {
    window.WeatherMapGfsFill = api;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})();