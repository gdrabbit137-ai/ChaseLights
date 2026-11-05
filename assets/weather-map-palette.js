// CL-WG-16: single source of truth for WeatherGrid color/opacity rendering.
// Extracted verbatim from weather-map.js so the CI-side PNG prerender
// generator imports THE SAME functions the browser draws with — the honest
// rule for pre-rendered frames. The generator (scripts/weathergrid_png_prerender.mjs)
// imports this module directly; PALETTE_VERSION is stamped into the PNG
// manifest and the frontend falls back to live JSON rendering on mismatch.
(function(global){
  'use strict';

  // Bump whenever any color/opacity formula or band table below changes.
  // Changing this invalidates every published PNG frame (frontend falls back
  // to JSON rendering until a new manifest with the matching version ships).
  const PALETTE_VERSION = 'wg21-p1';

  // One provider-independent forecast cloud scale keeps JMA, CWA, ICON and
  // GFS directly comparable. Observation layers keep separate semantics.
  const CLOUD_PERCENT_BREAKS=[0,20,40,50,70,85,100];
  // CL-WG-21: Windy-style cloud ramp — a single monotonic lightness ladder
  // (deep sea blue at 0% clear sky → neutral gray-white near 50% → pure white
  // at 100% overcast). No purple/pink hue jumps: readability comes from
  // lightness, which is also colorblind-safe by construction.
  const CLOUD_PERCENT_BANDS=[
    {min:0,max:20,color:'hsl(214 78% 44%)'},
    {min:20,max:40,color:'hsl(211 66% 58%)'},
    {min:40,max:50,color:'hsl(209 44% 71%)'},
    {min:50,max:70,color:'hsl(208 28% 82%)'},
    {min:70,max:85,color:'hsl(207 16% 91%)'},
    {min:85,max:100,color:'hsl(206 8% 97%)'}
  ];
  // CL-WG-21: low cloud keeps a gray-blue (slate) base tone — same monotonic
  // lightness ladder, slightly darker/duller than total cloud at every stop so
  // the layers stay kin but distinguishable (Windy low-cloud convention).
  const LOW_CLOUD_PERCENT_BANDS=[
    {min:0,max:20,color:'hsl(205 62% 48%)'},
    {min:20,max:40,color:'hsl(204 50% 60%)'},
    {min:40,max:50,color:'hsl(203 34% 70%)'},
    {min:50,max:70,color:'hsl(202 24% 79%)'},
    {min:70,max:85,color:'hsl(201 16% 87%)'},
    {min:85,max:100,color:'hsl(200 12% 92%)'}
  ];
  const CLOUD_OPACITY_STOPS=[
    [0,.02],[20,.12],[40,.32],[50,.55],[70,.72],[85,.88],[100,1]
  ];
  const CLOUD_MAX_OVERLAY_ALPHA=.78;

  function normalizedValue(value,cfg){
    if(value == null || !Number.isFinite(value)) return 0;
    if(cfg.scale==='precip_rate' || cfg.scale==='aod' || cfg.scale==='nightlights') return normalizedPiecewise(value,cfg.ticks);
    const span=cfg.domain[1]-cfg.domain[0];
    if(!span) return 0;
    return Math.max(0,Math.min(1,(value-cfg.domain[0])/span));
  }

  function normalizedPiecewise(value,ticks){
    if(!Number.isFinite(value) || !ticks?.length) return 0;
    if(value<=ticks[0]) return 0;
    const last=ticks.length-1;
    if(value>=ticks[last]) return 1;
    for(let i=1;i<ticks.length;i++){
      if(value<=ticks[i]){
        const local=(value-ticks[i-1])/(ticks[i]-ticks[i-1]);
        return ((i-1)+local)/last;
      }
    }
    return 1;
  }

  function interpolateStops(value,stops){
    const v=Number(value);
    if(!Number.isFinite(v) || !stops?.length) return 0;
    if(v<=stops[0][0]) return stops[0][1];
    for(let i=1;i<stops.length;i++){
      const [x1,y1]=stops[i];
      const [x0,y0]=stops[i-1];
      if(v<=x1){
        const t=(v-x0)/(x1-x0);
        return y0+(y1-y0)*t;
      }
    }
    return stops[stops.length-1][1];
  }

  function cloudColorFor(value,bands){
    const table=bands||CLOUD_PERCENT_BANDS;
    const v=Math.max(0,Math.min(100,Number(value)));
    const band=table.find(item=>v<item.max) ||
      table[table.length-1];
    return band.color;
  }

  function layerOpacityCap(cfg){
    return cfg.palette==='cloud' || cfg.palette==='cloudLow' ? CLOUD_MAX_OVERLAY_ALPHA : 1;
  }

  function cellOpacityFor(value,cfg){
    if(value == null || !Number.isFinite(value)){
      if(cfg.palette==='cloudMask' || cfg.palette==='cloudHeight') return 0;
      return .08;
    }
    const t=normalizedValue(value,cfg);
    if(cfg.palette==='cloudMask') return value>=.5 ? .84 : 0;
    if(cfg.palette==='cloudHeight') return .28 + .72*t;
    if(cfg.palette==='cloud' || cfg.palette==='cloudLow'){
      // Low percentages recede quickly; 50% becomes an explicit visual hinge.
      return interpolateStops(value,CLOUD_OPACITY_STOPS);
    }
    if(cfg.palette==='precip'){
      // Dry cells should not paint a dark blanket across the whole map.
      if(value < .01) return 0;
      return .18 + .82*Math.sqrt(t);
    }
    if(cfg.palette==='visibility'){
      // Poor visibility is the signal. Clear-air / ceiling-saturated cells recede.
      return .08 + .92*Math.pow(1-t,.8);
    }
    if(cfg.palette==='wind'){
      return .12 + .88*t;
    }
    if(cfg.palette==='temperature' || cfg.palette==='humidity' || cfg.palette==='solar'){
      return .18 + .82*Math.max(.12,t);
    }
    if(cfg.palette==='haze'){
      return .06 + .94*Math.pow(t,.78);
    }
    if(cfg.palette==='pm25'){
      return .06 + .94*Math.pow(t,.72);
    }
    if(cfg.palette==='nightlights'){
      return value<=0 ? 0 : .10 + .90*Math.pow(t,.68);
    }
    if(cfg.palette==='direction'){
      return .48;
    }
    return 1;
  }

  function colorFor(value,cfg){
    if(value == null || !Number.isFinite(value)) return 'rgba(30,41,59,.35)';
    let t = normalizedValue(value,cfg);
    if(cfg.palette==='cloudMask'){
      return value>=.5 ? 'hsl(205 18% 92%)' : 'rgba(0,0,0,0)';
    }
    if(cfg.palette==='cloudHeight'){
      const hue=205 + t*115;
      const light=46 + t*16;
      return `hsl(${hue} 72% ${light}%)`;
    }
    if(cfg.palette==='cloud'){
      return cloudColorFor(value);
    }
    if(cfg.palette==='cloudLow'){
      return cloudColorFor(value,LOW_CLOUD_PERCENT_BANDS);
    }
    if(cfg.palette==='visibility'){
      // CL-WG-21 audit: keep poor-visibility=warm semantics but make the ramp
      // a monotonic lightness ladder (dark/dim at poor → bright at clear) so
      // adjacent ticks are separable by lightness, not hue alone.
      const hue = 5 + t*145;
      const light = 36 + t*28;
      return `hsl(${hue} 72% ${light}%)`;
    }
    if(cfg.palette==='precip'){
      if(value < .01) return 'rgba(15,23,42,.82)';
      const hue = 215 - t*175;
      return `hsl(${hue} 82% 48%)`;
    }
    if(cfg.palette==='wind'){
      const hue = 260 - t*220;
      return `hsl(${hue} 78% 52%)`;
    }
    if(cfg.palette==='temperature'){
      const hue = 220 - t*220;
      return `hsl(${hue} 82% 52%)`;
    }
    if(cfg.palette==='humidity'){
      const light = 30 + t*48;
      return `hsl(198 72% ${light}%)`;
    }
    if(cfg.palette==='solar'){
      const hue = 48 - t*30;
      const light = 30 + t*32;
      return `hsl(${hue} 90% ${light}%)`;
    }
    if(cfg.palette==='haze'){
      const hue = 55 - t*48;
      const saturation = 72 + t*12;
      const light = 58 - t*20;
      return `hsl(${hue} ${saturation}% ${light}%)`;
    }
    if(cfg.palette==='pm25'){
      const hue = 150 - t*145;
      const saturation = 64 + t*18;
      const light = 54 - t*18;
      return `hsl(${hue} ${saturation}% ${light}%)`;
    }
    if(cfg.palette==='nightlights'){
      const hue = 275 - t*225;
      const saturation = 62 + t*28;
      const light = 24 + t*38;
      return `hsl(${hue} ${saturation}% ${light}%)`;
    }
    if(cfg.palette==='direction'){
      const hue=((value%360)+360)%360;
      return `hsl(${hue} 76% 52%)`;
    }
    return `hsl(${(value%360+360)%360} 76% 52%)`;
  }

  // Render-relevant layer config (palette/domain/scale/ticks) — single source
  // for both live rendering and the PNG prerender generator. weather-map.js
  // adds only display labels on top of these entries.
  const LAYER_RENDER_CONFIG = {
    total_cloud_percent:{palette:'cloud', domain:[0,100], scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    low_cloud_percent: {palette:'cloudLow', domain:[0,100], scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    mid_cloud_percent: {palette:'cloud', domain:[0,100], scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    high_cloud_percent:{palette:'cloud', domain:[0,100], scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    observed_cloud_mask:{palette:'cloudMask', domain:[0,1]},
    cloud_top_height_m:{palette:'cloudHeight', domain:[0,16000]},
    visibility_km:{palette:'visibility', domain:[0,30]},
    precip_rate_mm_h:{palette:'precip', domain:[0,20], scale:'precip_rate', ticks:[0,.1,.5,1,2,5,10,20]},
    wind_speed_10m_m_s:{palette:'wind', domain:[0,20]},
    wind_direction_10m_deg:{palette:'direction', domain:[0,360]},
    wind_speed_925hpa_m_s:{palette:'wind', domain:[0,30]},
    wind_direction_925hpa_deg:{palette:'direction', domain:[0,360]},
    wind_speed_850hpa_m_s:{palette:'wind', domain:[0,40]},
    wind_direction_850hpa_deg:{palette:'direction', domain:[0,360]},
    wind_speed_700hpa_m_s:{palette:'wind', domain:[0,50]},
    wind_direction_700hpa_deg:{palette:'direction', domain:[0,360]},
    temperature_925hpa_c:{palette:'temperature', domain:[-10,30]},
    temperature_850hpa_c:{palette:'temperature', domain:[-20,25]},
    temperature_700hpa_c:{palette:'temperature', domain:[-35,15]},
    temperature_2m_c:{palette:'temperature', domain:[-5,40]},
    relative_humidity_2m_percent:{palette:'humidity', domain:[0,100]},
    precip_total_mm:{palette:'precip', domain:[0,100]},
    shortwave_flux_w_m2:{palette:'solar', domain:[0,1000]},
    aerosol_optical_depth_550nm:{palette:'haze', domain:[0,1.5], scale:'aod', ticks:[0,.05,.1,.2,.4,.8,1.5]},
    pm2_5_ug_m3:{palette:'pm25', domain:[0,75], scale:'pm25', ticks:[0,5,10,15,25,35,50,75]},
    nighttime_lights_radiance_nw_cm2_sr:{palette:'nightlights', domain:[0,50], scale:'nightlights', ticks:[0,.5,1,2,5,10,25,50]}
  };

  const api = {
    PALETTE_VERSION,
    CLOUD_PERCENT_BREAKS,
    CLOUD_PERCENT_BANDS,
    LOW_CLOUD_PERCENT_BANDS,
    CLOUD_OPACITY_STOPS,
    CLOUD_MAX_OVERLAY_ALPHA,
    normalizedValue,
    normalizedPiecewise,
    interpolateStops,
    cloudColorFor,
    layerOpacityCap,
    cellOpacityFor,
    colorFor,
    LAYER_RENDER_CONFIG
  };

  global.WeatherMapPalette = api;
  if(typeof module !== 'undefined' && module.exports){
    module.exports = api;
  }
})(typeof window !== 'undefined' ? window : globalThis);