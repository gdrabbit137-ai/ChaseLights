(() => {
  const LIVE_DATA = './weathergrid/gfs_tw_weather_browser.json';
  const LIVE_QC = './weathergrid/gfs_tw_weather_qc.json';
  const LIVE_ICON_DATA = './weathergrid/icon_tw_cloud_browser.json';
  const LIVE_ICON_QC = './weathergrid/icon_tw_cloud_qc.json';
  const LIVE_CWA_DATA = './weathergrid/cwa_wrf3_tw_weather_browser.json';
  const LIVE_CWA_QC = './weathergrid/cwa_wrf3_tw_weather_qc.json';
  const LIVE_COVERAGE = './weathergrid/weathergrid_coverage_browser.json';
  const FALLBACK_DATA = './weathergrid_sample.json';
  const FALLBACK_COVERAGE = './weathergrid_coverage_sample.json';
  const MAPLIBRE_MODULE = 'https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl.mjs';
  const BASEMAP_STYLE = 'https://tiles.openfreemap.org/styles/liberty';

  const layerConfig = {
    low_cloud_percent: {label:'低雲', unit:'%', domain:[0,100], palette:'cloud'},
    mid_cloud_percent: {label:'中雲', unit:'%', domain:[0,100], palette:'cloud'},
    high_cloud_percent:{label:'高雲', unit:'%', domain:[0,100], palette:'cloud'},
    visibility_km:{label:'能見度', unit:'km', domain:[0,30], palette:'visibility'},
    precip_rate_mm_h:{label:'降雨率', unit:'mm/h', domain:[0,10], palette:'precip'},
    wind_speed_10m_m_s:{label:'10 m 風速', unit:'m/s', domain:[0,20], palette:'wind'},
    wind_direction_10m_deg:{label:'10 m 風向', unit:'°', domain:[0,360], palette:'direction'},
    temperature_2m_c:{label:'2 m 氣溫', unit:'°C', domain:[-5,40], palette:'temperature'},
    relative_humidity_2m_percent:{label:'2 m 相對濕度', unit:'%', domain:[0,100], palette:'humidity'},
    precip_total_mm:{label:'累積降水', unit:'mm', domain:[0,100], palette:'precip'},
    shortwave_flux_w_m2:{label:'地表短波輻射', unit:'W/m²', domain:[0,1000], palette:'solar'}
  };

  const state = {
    data:null,
    qc:null,
    iconData:null,
    iconQc:null,
    cwaData:null,
    cwaQc:null,
    modelMode:'auto',
    coverage:{spots:[]},
    frameIndex:0,
    layer:'low_cloud_percent',
    spotId:'',
    opportunityId:'',
    view:null,
    weatherOpacity:0.62,
    windVectors:false,
    windVectorTouched:false,
    lastWindVectorCount:0,
    map:null,
    mapReady:false,
    basemapStatus:'loading',
    source:'loading',
    coverageSource:'loading'
  };

  const $ = id => document.getElementById(id);
  const canvas = $('weather-canvas');
  const ctx = canvas.getContext('2d');

  function setBasemapStatus(status,message){
    state.basemapStatus=status;
    const host=$('basemap-status');
    if(!host) return;
    host.textContent=message;
    host.className=`basemap-status ${status}`;
  }

  function normalizeViewBbox(bbox){
    if(!bbox) return null;
    const leftlon=Number(bbox.leftlon ?? bbox.west);
    const rightlon=Number(bbox.rightlon ?? bbox.east);
    const bottomlat=Number(bbox.bottomlat ?? bbox.south);
    const toplat=Number(bbox.toplat ?? bbox.north);
    if(![leftlon,rightlon,bottomlat,toplat].every(Number.isFinite)) return null;
    if(rightlon<=leftlon || toplat<=bottomlat) return null;
    return {leftlon,rightlon,bottomlat,toplat};
  }

  function setViewBbox(bbox,{animate=false,maxZoom=13}={}){
    const view=normalizeViewBbox(bbox);
    if(!view) return false;
    state.view=view;
    if(state.mapReady && state.map){
      state.map.fitBounds(
        [[view.leftlon,view.bottomlat],[view.rightlon,view.toplat]],
        {padding:28,duration:animate?450:0,maxZoom}
      );
    }
    return true;
  }

  function renderViewBbox(){
    if(!state.mapReady || !state.map) return state.view;
    const b=state.map.getBounds();
    return {
      leftlon:b.getWest(),rightlon:b.getEast(),
      bottomlat:b.getSouth(),toplat:b.getNorth()
    };
  }

  function syncCanvasSize(){
    const rect=canvas.getBoundingClientRect();
    const dpr=Math.min(window.devicePixelRatio || 1,2);
    const width=Math.max(1,Math.round(rect.width*dpr));
    const height=Math.max(1,Math.round(rect.height*dpr));
    if(canvas.width!==width || canvas.height!==height){
      canvas.width=width;
      canvas.height=height;
    }
    ctx.setTransform(dpr,0,0,dpr,0,0);
    return {width:rect.width,height:rect.height};
  }

  function pickSpotAtPoint(px,py){
    let best=null;
    for(const spot of state.data.spots){
      const p=project(spot.lon,spot.lat);
      const d=Math.hypot(p.x-px,p.y-py);
      if(!best || d<best.d) best={spot,d};
    }
    if(best && best.d<26){
      $('spot-select').value=best.spot.spot_id;
      selectSpot(best.spot.spot_id);
    }
  }

  async function initBasemap(){
    setBasemapStatus('loading','底圖載入中…');
    try{
      const maplibregl=await import(MAPLIBRE_MODULE);
      const b=normalizeViewBbox(state.data.bbox);
      const map=new maplibregl.Map({
        container:'weather-basemap',
        style:BASEMAP_STYLE,
        center:[(b.leftlon+b.rightlon)/2,(b.bottomlat+b.toplat)/2],
        zoom:5.4,
        bearing:0,
        pitch:0,
        dragRotate:false,
        touchPitch:false,
        attributionControl:true
      });
      state.map=map;
      map.touchZoomRotate.disableRotation();
      map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');

      const timeout=window.setTimeout(()=>{
        if(state.mapReady) return;
        try{ map.remove(); }catch(_){}
        state.map=null;
        canvas.style.pointerEvents='auto';
        setBasemapStatus('fallback','底圖逾時 · Canvas fallback');
        renderAll();
      },8000);

      map.on('load',()=>{
        window.clearTimeout(timeout);
        state.mapReady=true;
        canvas.style.pointerEvents='none';
        setBasemapStatus('ready','MapLibre · OpenFreeMap');
        setViewBbox(state.view || state.data.bbox);
        renderAll();
      });
      map.on('move',()=>{
        if(!state.mapReady) return;
        draw();
      });
      map.on('resize',()=>{
        syncCanvasSize();
        draw();
      });
      map.on('click',ev=>pickSpotAtPoint(ev.point.x,ev.point.y));
      map.on('error',ev=>console.warn('WeatherGrid basemap error',ev?.error || ev));
    }catch(err){
      console.warn('WeatherGrid basemap unavailable; using Canvas fallback',err);
      state.map=null;
      state.mapReady=false;
      canvas.style.pointerEvents='auto';
      setBasemapStatus('fallback','底圖離線 · Canvas fallback');
      renderAll();
    }
  }

  function escapeHtml(v){
    return String(v ?? '').replace(/[&<>"']/g, c => (
      {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
    ));
  }

  async function fetchJson(url){
    const r = await fetch(url, {cache:'no-store'});
    if(!r.ok) throw new Error(`${r.status} ${url}`);
    return r.json();
  }

  async function load(){
    try{
      state.data = await fetchJson(LIVE_DATA);
      state.source = 'live';
      try{ state.qc = await fetchJson(LIVE_QC); }catch(_){ state.qc = null; }
    }catch(err){
      console.warn('WeatherGrid live bundle unavailable; using demo fixture', err);
      state.data = await fetchJson(FALLBACK_DATA);
      state.qc = null;
      state.source = 'demo';
    }

    if(state.source === 'live'){
      try{
        state.iconData = await fetchJson(LIVE_ICON_DATA);
        try{ state.iconQc = await fetchJson(LIVE_ICON_QC); }catch(_){ state.iconQc = null; }
      }catch(err){
        console.warn('ICON Global cloud bundle unavailable; GFS remains active', err);
        state.iconData = null;
        state.iconQc = null;
      }

      try{
        state.cwaData = await fetchJson(LIVE_CWA_DATA);
        try{ state.cwaQc = await fetchJson(LIVE_CWA_QC); }catch(_){ state.cwaQc = null; }
      }catch(err){
        console.warn('CWA WRF 3 km bundle unavailable', err);
        state.cwaData = null;
        state.cwaQc = null;
      }

      try{
        state.coverage = await fetchJson(LIVE_COVERAGE);
        state.coverageSource = 'live';
      }catch(err){
        console.warn('Live subject-aware coverage bundle unavailable', err);
        state.coverage = {schema_version:1,spots:[]};
        state.coverageSource = 'missing';
      }
    }else{
      state.coverage = await fetchJson(FALLBACK_COVERAGE);
      state.coverageSource = 'demo';
    }

    setViewBbox(state.data.bbox);
    initControls();
    renderAll();
    initBasemap();
    window.__weatherGridPreviewReady = true;
  }

  function modelDataset(mode=state.modelMode){
    if(mode==='cwa' && state.cwaData) return state.cwaData;
    if(mode==='icon' && state.iconData) return state.iconData;
    return state.data;
  }

  function modelQc(mode=state.modelMode){
    if(mode==='cwa' && state.cwaData) return state.cwaQc;
    if(mode==='icon' && state.iconData) return state.iconQc;
    return state.qc;
  }

  function modelLabel(mode=state.modelMode){
    if(mode==='cwa') return 'CWA WRF 3 km';
    if(mode==='icon') return 'ICON Global';
    if(mode==='gfs') return 'GFS 0.25°';
    return '自動';
  }

  function modelAvailable(mode){
    if(mode==='cwa') return Boolean(state.cwaData);
    if(mode==='icon') return Boolean(state.iconData);
    if(mode==='gfs') return Boolean(state.data);
    return true;
  }

  function nearestFrameIndex(data,validTime){
    if(!data?.frames?.length) return 0;
    if(!validTime) return 0;
    const target=Date.parse(validTime);
    let best=0,bestDelta=Infinity;
    data.frames.forEach((f,i)=>{
      const t=Date.parse(f.valid_time_utc);
      const d=Math.abs(t-target);
      if(Number.isFinite(d) && d<bestDelta){best=i;bestDelta=d;}
    });
    return best;
  }

  function availableLayerKeys(){
    if(state.modelMode==='auto'){
      return Object.keys(layerConfig).filter(key=>
        Boolean(state.data?.fields?.[key]) ||
        Boolean(state.iconData?.fields?.[key])
      );
    }
    const data=modelDataset();
    return Object.keys(layerConfig).filter(key=>Boolean(data?.fields?.[key]));
  }

  function refreshModelControls(){
    const modelSelect=$('model-select');
    for(const option of modelSelect.options){
      if(option.value!=='auto') option.disabled=!modelAvailable(option.value);
    }
    modelSelect.value=state.modelMode;

    const layerSelect=$('layer-select');
    const layers=availableLayerKeys();
    if(!layers.includes(state.layer) && layers.length){
      if(state.modelMode==='cwa' && layers.includes('wind_speed_10m_m_s')){
        state.layer='wind_speed_10m_m_s';
      }else{
        state.layer=layers[0];
      }
    }
    layerSelect.innerHTML=layers
      .map(key=>'<option value="'+key+'">'+layerConfig[key].label+'</option>')
      .join('');
    layerSelect.value=state.layer;

    const timeline=timelineDataset();
    const slider=$('time-slider');
    slider.max=Math.max(0,(timeline?.frames?.length || 1)-1);
    state.frameIndex=Math.min(state.frameIndex,Number(slider.max));
    slider.value=state.frameIndex;

    const hasWind=Boolean(
      activeDataset('wind_speed_10m_m_s')?.fields?.wind_speed_10m_m_s &&
      activeDataset('wind_direction_10m_deg')?.fields?.wind_direction_10m_deg
    );
    const windToggle=$('wind-vector-toggle');
    windToggle.disabled=!hasWind;
    if(!hasWind){
      state.windVectors=false;
      windToggle.checked=false;
    }else{
      windToggle.checked=state.windVectors;
    }
  }

  function switchModel(mode){
    const oldTime=frame()?.valid_time_utc || null;
    state.modelMode=mode;
    const timeline=timelineDataset();
    state.frameIndex=nearestFrameIndex(timeline,oldTime);
    const layers=availableLayerKeys();
    if(!layers.includes(state.layer) && layers.length){
      state.layer=(mode==='cwa' && layers.includes('wind_speed_10m_m_s'))
        ? 'wind_speed_10m_m_s'
        : layers[0];
    }
    refreshModelControls();
    setViewBbox(timeline.bbox,{animate:true,maxZoom:8});
    renderAll();
  }

  function initControls(){
    const modelSelect=$('model-select');
    modelSelect.addEventListener('change',()=>switchModel(modelSelect.value));

    const layerSelect = $('layer-select');
    const windToggle=$('wind-vector-toggle');

    windToggle.addEventListener('change',()=>{
      state.windVectors=windToggle.checked;
      state.windVectorTouched=true;
      renderAll();
    });

    layerSelect.addEventListener('change', () => {
      state.layer = layerSelect.value;
      const hasWind=Boolean(
        activeDataset('wind_speed_10m_m_s')?.fields?.wind_speed_10m_m_s &&
        activeDataset('wind_direction_10m_deg')?.fields?.wind_direction_10m_deg
      );
      const windLayer=state.layer==='wind_speed_10m_m_s' ||
        state.layer==='wind_direction_10m_deg';
      if(windLayer && hasWind && !state.windVectorTouched){
        state.windVectors=true;
        windToggle.checked=true;
      }
      renderAll();
    });

    const opacitySlider=$('opacity-slider');
    opacitySlider.value=Math.round(state.weatherOpacity*100);
    opacitySlider.addEventListener('input',()=>{
      state.weatherOpacity=Number(opacitySlider.value)/100;
      renderAll();
    });

    const slider = $('time-slider');
    slider.addEventListener('input', () => {
      state.frameIndex = Number(slider.value);
      renderAll();
    });

    const spotSelect = $('spot-select');
    spotSelect.innerHTML = '<option value="">全部景點</option>' +
      state.data.spots.map(s =>
        '<option value="'+escapeHtml(s.spot_id)+'">'+escapeHtml(s.name)+'</option>'
      ).join('');
    spotSelect.addEventListener('change', () => {
      selectSpot(spotSelect.value);
    });

    const opportunitySelect = $('opportunity-select');
    opportunitySelect.addEventListener('change', () => {
      state.opportunityId = opportunitySelect.value;
      applyCoverageView();
      renderAll();
    });

    $('reset-view').addEventListener('click', () => {
      setViewBbox(timelineDataset().bbox,{animate:true,maxZoom:8});
      renderAll();
    });

    canvas.addEventListener('click', ev => {
      if(state.mapReady) return;
      const rect=canvas.getBoundingClientRect();
      pickSpotAtPoint(ev.clientX-rect.left,ev.clientY-rect.top);
    });

    refreshModelControls();
  }
  function selectSpot(spotId){
    state.spotId = spotId;
    state.opportunityId = '';
    refreshOpportunityOptions();
    if(state.spotId){
      const group = selectedCoverageGroup();
      const union = group && unionViewport(group.opportunities);
      if(union) fitCoverageBbox(union);
      else zoomToSpot(selectedSpot());
    }else{
      state.view = {...timelineDataset().bbox};
    }
    renderAll();
  }

  function refreshOpportunityOptions(){
    const select = $('opportunity-select');
    const group = selectedCoverageGroup();
    if(!state.spotId){
      select.disabled = true;
      select.innerHTML = '<option value="">先選景點</option>';
      return;
    }
    if(!group || !group.opportunities.length){
      select.disabled = true;
      select.innerHTML = '<option value="">尚未建立題材 coverage</option>';
      return;
    }
    select.disabled = false;
    select.innerHTML =
      '<option value="">全部已建 coverage 題材</option>' +
      group.opportunities.map(op => {
        const suffix = op.complete ? '' : ' ⚠';
        return `<option value="${escapeHtml(op.opportunity_id)}">${escapeHtml(op.name_zh || op.opportunity_id)}${suffix}</option>`;
      }).join('');
    select.value = state.opportunityId;
  }

  function selectedSpot(){
    return state.data.spots.find(s => s.spot_id === state.spotId) || null;
  }

  function coverageGroupForSpot(spotId){
    return (state.coverage?.spots || []).find(s => s.spot_id === spotId) || null;
  }

  function selectedCoverageGroup(){
    return coverageGroupForSpot(state.spotId);
  }

  function selectedOpportunity(){
    const group = selectedCoverageGroup();
    if(!group || !state.opportunityId) return null;
    return group.opportunities.find(x => x.opportunity_id === state.opportunityId) || null;
  }

  function activeCoverageOpportunities(){
    const selected = selectedOpportunity();
    if(selected) return [selected];
    const group = selectedCoverageGroup();
    return group ? group.opportunities : [];
  }

  function zoomToSpot(spot){
    if(!spot) return;
    const lonHalf = 0.85;
    const latHalf = 0.65;
    setViewBbox({
      leftlon:spot.lon-lonHalf,
      rightlon:spot.lon+lonHalf,
      bottomlat:spot.lat-latHalf,
      toplat:spot.lat+latHalf
    },{animate:true,maxZoom:10});
  }

  function unionViewport(opportunities){
    const boxes = (opportunities || [])
      .map(x => x.viewport_bbox)
      .filter(x => x && !x.wraps_antimeridian);
    if(!boxes.length) return null;
    return {
      west:Math.min(...boxes.map(x=>x.west)),
      south:Math.min(...boxes.map(x=>x.south)),
      east:Math.max(...boxes.map(x=>x.east)),
      north:Math.max(...boxes.map(x=>x.north)),
      wraps_antimeridian:false
    };
  }

  function fitCoverageBbox(bbox){
    if(!bbox || bbox.wraps_antimeridian) return false;
    let west=Number(bbox.west), east=Number(bbox.east);
    let south=Number(bbox.south), north=Number(bbox.north);
    if(![west,east,south,north].every(Number.isFinite)) return false;
    const minLonSpan=.18, minLatSpan=.14;
    if(east-west < minLonSpan){
      const mid=(west+east)/2; west=mid-minLonSpan/2; east=mid+minLonSpan/2;
    }
    if(north-south < minLatSpan){
      const mid=(south+north)/2; south=mid-minLatSpan/2; north=mid+minLatSpan/2;
    }
    return setViewBbox(
      {leftlon:west,rightlon:east,bottomlat:south,toplat:north},
      {animate:true,maxZoom:13}
    );
  }

  function applyCoverageView(){
    const op = selectedOpportunity();
    if(op?.viewport_bbox && !op.viewport_bbox.wraps_antimeridian){
      fitCoverageBbox(op.viewport_bbox);
      return;
    }
    const group = selectedCoverageGroup();
    const union = group && unionViewport(group.opportunities);
    if(union){
      fitCoverageBbox(union);
      return;
    }
    if(selectedSpot()) zoomToSpot(selectedSpot());
  }

  function timelineDataset(){
    if(state.modelMode==='cwa' && state.cwaData) return state.cwaData;
    if(state.modelMode==='icon' && state.iconData) return state.iconData;
    return state.data;
  }

  function providerCoversBbox(bbox){
    if(!bbox || bbox.wraps_antimeridian) return false;
    const data=activeDataset(state.layer);
    const b=data?.bbox;
    if(!b) return false;
    return bbox.west >= b.leftlon && bbox.east <= b.rightlon &&
      bbox.south >= b.bottomlat && bbox.north <= b.toplat;
  }

  const cloudLayers = new Set([
    'low_cloud_percent',
    'mid_cloud_percent',
    'high_cloud_percent'
  ]);

  function baseFrame(){
    const timeline=timelineDataset();
    return timeline?.frames?.[state.frameIndex] || null;
  }

  function iconFrameForValidTime(validTime){
    if(!state.iconData || !validTime) return null;
    return state.iconData.frames.find(f => f.valid_time_utc===validTime) || null;
  }

  function activeDataset(key=state.layer){
    if(state.modelMode==='cwa' && state.cwaData){
      return state.cwaData.fields[key] ? state.cwaData : state.cwaData;
    }
    if(state.modelMode==='icon' && state.iconData) return state.iconData;
    if(state.modelMode==='gfs') return state.data;

    if(cloudLayers.has(key) && state.iconData){
      const iconFrame=iconFrameForValidTime(baseFrame()?.valid_time_utc);
      if(iconFrame && state.iconData.fields[key]) return state.iconData;
    }
    return state.data;
  }

  function activeFrame(key=state.layer){
    if(state.modelMode==='cwa' || state.modelMode==='icon' || state.modelMode==='gfs'){
      return timelineDataset()?.frames?.[state.frameIndex] || null;
    }
    const data=activeDataset(key);
    if(data===state.iconData){
      return iconFrameForValidTime(baseFrame()?.valid_time_utc);
    }
    return baseFrame();
  }

  function activeQc(key=state.layer){
    if(state.modelMode==='cwa') return state.cwaQc;
    if(state.modelMode==='icon') return state.iconQc;
    if(state.modelMode==='gfs') return state.qc;
    return activeDataset(key)===state.iconData ? state.iconQc : state.qc;
  }

  function frame(){ return activeFrame(state.layer); }

  function decodeValue(key, encoded, data=activeDataset(key)){
    if(encoded == null || !data?.fields?.[key]) return null;
    const meta = data.fields[key];
    let value = encoded * meta.scale;
    if(meta.wrap) value = ((value % meta.wrap) + meta.wrap) % meta.wrap;
    return value;
  }

  function decodedArray(key){
    const data=activeDataset(key);
    const active=activeFrame(key);
    if(!active || !active.values[key]) return [];
    return active.values[key].map(v => decodeValue(key,v,data));
  }
  function project(lon,lat){
    if(state.mapReady && state.map){
      const p=state.map.project([lon,lat]);
      return {x:p.x,y:p.y};
    }
    const v=state.view;
    return {
      x:(lon-v.leftlon)/(v.rightlon-v.leftlon)*canvas.clientWidth,
      y:(v.toplat-lat)/(v.toplat-v.bottomlat)*canvas.clientHeight
    };
  }

  function normalizedValue(value,cfg){
    if(value == null || !Number.isFinite(value)) return 0;
    const span=cfg.domain[1]-cfg.domain[0];
    if(!span) return 0;
    return Math.max(0,Math.min(1,(value-cfg.domain[0])/span));
  }

  function cellOpacityFor(value,cfg){
    if(value == null || !Number.isFinite(value)) return .08;
    const t=normalizedValue(value,cfg);
    if(cfg.palette==='cloud'){
      // Clear sky should reveal the basemap; denser cloud progressively dominates.
      return .04 + .96*Math.pow(t,.8);
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
    if(cfg.palette==='direction'){
      return .48;
    }
    return 1;
  }

  function colorFor(value,cfg){
    if(value == null || !Number.isFinite(value)) return 'rgba(30,41,59,.35)';
    let t = normalizedValue(value,cfg);
    if(cfg.palette==='cloud'){
      const l = 22 + t*65;
      return `hsl(205 70% ${l}%)`;
    }
    if(cfg.palette==='visibility'){
      const hue = 5 + t*145;
      return `hsl(${hue} 72% 46%)`;
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
    return `hsl(${(value%360+360)%360} 76% 52%)`;
  }

  function fillWeatherPolygon(points,value,cfg){
    ctx.beginPath();
    points.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y));
    ctx.closePath();
    ctx.globalAlpha=state.weatherOpacity*cellOpacityFor(value,cfg);
    ctx.fillStyle=colorFor(value,cfg);
    ctx.fill();
  }

  function bilinearValue(q00,q10,q01,q11,wx,wy){
    if([q00,q10,q01,q11].some(v=>!Number.isFinite(v))) return null;
    return q00*(1-wx)*(1-wy)+q10*wx*(1-wy)+
      q01*(1-wx)*wy+q11*wx*wy;
  }

  function drawNearestCells(data,vals,cfg,visibleView){
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    const lonStep=cols>1 ? Math.abs(lons[1]-lons[0]) : .25;
    const latStep=rows>1 ? Math.abs(lats[1]-lats[0]) : .25;
    for(let r=0;r<rows;r++){
      for(let c=0;c<cols;c++){
        const lon=lons[c], lat=lats[r];
        const left=lon-lonStep/2, right=lon+lonStep/2;
        const top=lat+latStep/2, bottom=lat-latStep/2;
        if(right < visibleView.leftlon || left > visibleView.rightlon ||
           top < visibleView.bottomlat || bottom > visibleView.toplat) continue;
        fillWeatherPolygon([
          project(left,top),project(right,top),
          project(right,bottom),project(left,bottom)
        ],vals[r*cols+c],cfg);
      }
    }
  }

  function drawBilinearSubcells(data,vals,cfg,visibleView){
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    if(rows<2 || cols<2){
      drawNearestCells(data,vals,cfg,visibleView);
      return;
    }

    // Provider-independent display interpolation:
    // GFS 0.25° -> 4x4, ICON 0.125° -> 2x2, CWA browser grid 0.03° -> 1x1.
    // This is display smoothing only; native model provenance stays visible.
    const lonStep=Math.abs(lons[1]-lons[0]);
    const subdivisions=lonStep>=.20 ? 4 : (lonStep>=.10 ? 2 : 1);

    for(let r=0;r<rows-1;r++){
      for(let c=0;c<cols-1;c++){
        const lon0=lons[c], lon1=lons[c+1];
        const lat0=lats[r], lat1=lats[r+1];
        const left=Math.min(lon0,lon1), right=Math.max(lon0,lon1);
        const bottom=Math.min(lat0,lat1), top=Math.max(lat0,lat1);
        if(right < visibleView.leftlon || left > visibleView.rightlon ||
           top < visibleView.bottomlat || bottom > visibleView.toplat) continue;

        const q00=vals[r*cols+c];
        const q10=vals[r*cols+c+1];
        const q01=vals[(r+1)*cols+c];
        const q11=vals[(r+1)*cols+c+1];

        for(let sy=0;sy<subdivisions;sy++){
          for(let sx=0;sx<subdivisions;sx++){
            const x0=sx/subdivisions, x1=(sx+1)/subdivisions;
            const y0=sy/subdivisions, y1=(sy+1)/subdivisions;
            const wx=(x0+x1)/2, wy=(y0+y1)/2;
            const value=bilinearValue(q00,q10,q01,q11,wx,wy);
            if(value==null) continue;

            const subLon0=lon0+(lon1-lon0)*x0;
            const subLon1=lon0+(lon1-lon0)*x1;
            const subLat0=lat0+(lat1-lat0)*y0;
            const subLat1=lat0+(lat1-lat0)*y1;
            fillWeatherPolygon([
              project(subLon0,subLat0),project(subLon1,subLat0),
              project(subLon1,subLat1),project(subLon0,subLat1)
            ],value,cfg);
          }
        }
      }
    }
  }

  function draw(){
    const data=activeDataset(state.layer);
    const cfg=layerConfig[state.layer];
    const vals=decodedArray(state.layer);
    const size=syncCanvasSize();
    const visibleView=renderViewBbox();

    ctx.clearRect(0,0,size.width,size.height);
    if(!state.mapReady){
      ctx.fillStyle='#07101f';
      ctx.fillRect(0,0,size.width,size.height);
    }

    ctx.save();
    if(state.layer==='wind_direction_10m_deg'){
      // Circular direction degrees must not be linearly interpolated.
      drawNearestCells(data,vals,cfg,visibleView);
    }else{
      drawBilinearSubcells(data,vals,cfg,visibleView);
    }
    ctx.restore();

    if(!state.mapReady) drawGrid();
    drawWindVectors();
    drawCoverage();
    drawSpots();
  }

  function windVectorStep(){
    if(state.mapReady && state.map){
      const zoom=state.map.getZoom();
      if(zoom>=8) return 1;
      if(zoom>=6.4) return 2;
      return 3;
    }
    const span=Math.max(
      state.view.rightlon-state.view.leftlon,
      state.view.toplat-state.view.bottomlat
    );
    if(span<1.2) return 1;
    if(span<3.2) return 2;
    return 3;
  }

  function strokeWindArrow(sx,sy,ex,ey,stroke,width){
    const angle=Math.atan2(ey-sy,ex-sx);
    const head=5.5;
    ctx.beginPath();
    ctx.moveTo(sx,sy);
    ctx.lineTo(ex,ey);
    ctx.lineTo(
      ex-head*Math.cos(angle-Math.PI/6),
      ey-head*Math.sin(angle-Math.PI/6)
    );
    ctx.moveTo(ex,ey);
    ctx.lineTo(
      ex-head*Math.cos(angle+Math.PI/6),
      ey-head*Math.sin(angle+Math.PI/6)
    );
    ctx.strokeStyle=stroke;
    ctx.lineWidth=width;
    ctx.stroke();
  }

  function drawWindVectors(){
    state.lastWindVectorCount=0;
    if(!state.windVectors) return;
    const data=activeDataset('wind_speed_10m_m_s');
    if(!data?.fields?.wind_speed_10m_m_s ||
       !data?.fields?.wind_direction_10m_deg) return;

    const speeds=decodedArray('wind_speed_10m_m_s');
    const directions=decodedArray('wind_direction_10m_deg');
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    const visible=renderViewBbox();
    const step=windVectorStep();

    ctx.save();
    ctx.lineCap='round';
    ctx.lineJoin='round';

    for(let r=0;r<rows;r+=step){
      for(let c=0;c<cols;c+=step){
        const i=r*cols+c;
        const speed=speeds[i], direction=directions[i];
        if(!Number.isFinite(speed) || !Number.isFinite(direction) || speed<0.5) continue;

        const lon=lons[c], lat=lats[r];
        if(lon<visible.leftlon || lon>visible.rightlon ||
           lat<visible.bottomlat || lat>visible.toplat) continue;

        const p=project(lon,lat);
        const length=11+Math.min(speed/20,1)*17;
        // Normalized provider direction is meteorological "from". Arrow points toward motion.
        const toward=((direction+180)%360)*Math.PI/180;
        const dx=Math.sin(toward)*length/2;
        const dy=-Math.cos(toward)*length/2;
        const sx=p.x-dx, sy=p.y-dy, ex=p.x+dx, ey=p.y+dy;

        strokeWindArrow(sx,sy,ex,ey,'rgba(2,6,23,.78)',4.5);
        strokeWindArrow(sx,sy,ex,ey,'rgba(224,242,254,.96)',2);
        state.lastWindVectorCount+=1;
      }
    }
    ctx.restore();
  }

  function drawGrid(){
    const v=state.view;
    const width=canvas.clientWidth,height=canvas.clientHeight;
    ctx.save();
    ctx.strokeStyle='rgba(226,232,240,.18)';
    ctx.fillStyle='rgba(226,232,240,.72)';
    ctx.font='18px -apple-system, sans-serif';
    ctx.lineWidth=1;
    const lonStart=Math.ceil(v.leftlon);
    for(let lon=lonStart;lon<=v.rightlon;lon++){
      const p=project(lon,v.bottomlat);
      ctx.beginPath();ctx.moveTo(p.x,0);ctx.lineTo(p.x,height);ctx.stroke();
      ctx.fillText(`${lon}°E`,p.x+4,22);
    }
    const latStart=Math.ceil(v.bottomlat);
    for(let lat=latStart;lat<=v.toplat;lat++){
      const p=project(v.leftlon,lat);
      ctx.beginPath();ctx.moveTo(0,p.y);ctx.lineTo(width,p.y);ctx.stroke();
      ctx.fillText(`${lat}°N`,6,p.y-5);
    }
    ctx.restore();
  }

  function destination(lat,lon,bearingDeg,distanceKm){
    const R=6371.0088;
    const b=bearingDeg*Math.PI/180;
    const d=distanceKm/R;
    const lat1=lat*Math.PI/180, lon1=lon*Math.PI/180;
    const lat2=Math.asin(
      Math.sin(lat1)*Math.cos(d)+Math.cos(lat1)*Math.sin(d)*Math.cos(b)
    );
    const lon2=lon1+Math.atan2(
      Math.sin(b)*Math.sin(d)*Math.cos(lat1),
      Math.cos(d)-Math.sin(lat1)*Math.sin(lat2)
    );
    return {lat:lat2*180/Math.PI,lon:((lon2*180/Math.PI+540)%360)-180};
  }

  function sectorBearings(start,end){
    const s=((Number(start)%360)+360)%360;
    const raw=Number(end)-Number(start);
    let span=((Number(end)-s)%360+360)%360;
    if(Math.abs(raw)>=359.999) span=360;
    const count=Math.max(1,Math.ceil(span/6));
    return Array.from({length:count+1},(_,i)=>(s+span*i/count)%360);
  }

  function cameraById(op,id){
    return (op.camera_zones||[]).find(c=>c.viewpoint_id===id) || null;
  }

  function geometryOrigin(geometry,op){
    if(Number.isFinite(Number(geometry.origin_lat)) && Number.isFinite(Number(geometry.origin_lon))){
      return {lat:Number(geometry.origin_lat),lon:Number(geometry.origin_lon)};
    }
    const camera=cameraById(op,geometry.origin_viewpoint_id);
    if(camera && Number.isFinite(Number(camera.lat)) && Number.isFinite(Number(camera.lon))){
      return {lat:Number(camera.lat),lon:Number(camera.lon)};
    }
    return null;
  }

  function drawPath(points,{stroke,fill=null,dashed=false,width=3,close=false}){
    if(!points.length) return;
    ctx.save();
    ctx.beginPath();
    points.forEach((pt,i)=>{
      const p=project(pt.lon,pt.lat);
      if(i===0) ctx.moveTo(p.x,p.y); else ctx.lineTo(p.x,p.y);
    });
    if(close) ctx.closePath();
    if(fill){ctx.fillStyle=fill;ctx.fill();}
    ctx.strokeStyle=stroke;
    ctx.lineWidth=width;
    ctx.setLineDash(dashed?[10,8]:[]);
    ctx.stroke();
    ctx.restore();
  }

  function drawGeometry(item,op,kind){
    const g=item?.geometry;
    if(!g) return;
    const subject=kind==='subject';
    const stroke=subject?'rgba(251,146,60,.95)':'rgba(34,211,238,.95)';
    const fill=subject?'rgba(251,146,60,.10)':'rgba(34,211,238,.08)';
    const dashed=!subject;

    if(g.type==='point'){
      const p=project(Number(g.lon),Number(g.lat));
      ctx.save();
      ctx.strokeStyle=stroke;ctx.lineWidth=3;ctx.setLineDash(dashed?[8,6]:[]);
      ctx.strokeRect(p.x-7,p.y-7,14,14);ctx.restore();
      return;
    }

    if(g.type==='bbox'){
      const points=[
        {lon:Number(g.west),lat:Number(g.south)},
        {lon:Number(g.east),lat:Number(g.south)},
        {lon:Number(g.east),lat:Number(g.north)},
        {lon:Number(g.west),lat:Number(g.north)}
      ];
      drawPath(points,{stroke,fill,dashed,width:3,close:true});
      return;
    }

    if(g.type==='polygon'){
      const points=(g.coordinates||[]).map(([lon,lat])=>({lon:Number(lon),lat:Number(lat)}));
      drawPath(points,{stroke,fill,dashed,width:3,close:true});
      return;
    }

    if(g.type==='corridor'){
      const points=(g.coordinates||[]).map(([lon,lat])=>({lon:Number(lon),lat:Number(lat)}));
      drawPath(points,{stroke,dashed,width:5,close:false});
      return;
    }

    if(g.type==='sector'){
      const origin=geometryOrigin(g,op);
      if(!origin) return;
      const bearings=sectorBearings(g.azimuth_start_deg,g.azimuth_end_deg);
      const maxRange=Number(g.max_range_km||0);
      const minRange=Number(g.min_range_km||0);
      const outer=bearings.map(b=>destination(origin.lat,origin.lon,b,maxRange));
      let points;
      if(minRange>0){
        const inner=[...bearings].reverse().map(b=>destination(origin.lat,origin.lon,b,minRange));
        points=[...outer,...inner];
      }else{
        points=[origin,...outer];
      }
      drawPath(points,{stroke,fill,dashed,width:3,close:true});
    }
  }

  function drawCoverage(){
    const opportunities=activeCoverageOpportunities();
    if(!opportunities.length) return;
    for(const op of opportunities){
      for(const item of op.environment_geometries||[]) drawGeometry(item,op,'environment');
      for(const item of op.subject_geometries||[]) drawGeometry(item,op,'subject');
      for(const camera of op.camera_zones||[]){
        if(!Number.isFinite(Number(camera.lat)) || !Number.isFinite(Number(camera.lon))) continue;
        const p=project(Number(camera.lon),Number(camera.lat));
        ctx.save();
        ctx.beginPath();ctx.arc(p.x,p.y,8,0,Math.PI*2);
        ctx.fillStyle='#fbbf24';ctx.fill();
        ctx.strokeStyle='#111827';ctx.lineWidth=3;ctx.stroke();
        ctx.restore();
      }
    }
  }

  function drawSpots(){
    const selected=selectedSpot();
    const width=canvas.clientWidth,height=canvas.clientHeight;
    ctx.save();
    for(const s of state.data.spots){
      const p=project(s.lon,s.lat);
      if(p.x<0||p.x>width||p.y<0||p.y>height) continue;
      ctx.beginPath();
      ctx.arc(p.x,p.y,s.spot_id===state.spotId?7:3.5,0,Math.PI*2);
      ctx.fillStyle=s.spot_id===state.spotId?'#fde68a':'#f8fafc';
      ctx.fill();
      ctx.strokeStyle='rgba(15,23,42,.9)';
      ctx.lineWidth=2;ctx.stroke();
    }
    if(selected){
      const p=project(selected.lon,selected.lat);
      ctx.font='bold 20px -apple-system, sans-serif';
      ctx.fillStyle='#fef3c7';
      ctx.strokeStyle='rgba(2,6,23,.95)';
      ctx.lineWidth=5;
      ctx.strokeText(selected.name,p.x+13,p.y-10);
      ctx.fillText(selected.name,p.x+13,p.y-10);
    }
    ctx.restore();
  }

  function nearestCellIndex(lon,lat,data=state.data){
    const lons=data.grid.longitudes, lats=data.grid.latitudes;
    let ci=0,ri=0,cd=Infinity,rd=Infinity;
    lons.forEach((v,i)=>{const d=Math.abs(v-lon);if(d<cd){cd=d;ci=i;}});
    lats.forEach((v,i)=>{const d=Math.abs(v-lat);if(d<rd){rd=d;ri=i;}});
    return ri*data.grid.cols+ci;
  }

  function samplingPoint(){
    const op=selectedOpportunity();
    const camera=(op?.camera_zones||[]).find(c=>Number.isFinite(Number(c.lat))&&Number.isFinite(Number(c.lon)));
    if(camera) return {lat:Number(camera.lat),lon:Number(camera.lon),label:'Camera Zone'};
    const spot=selectedSpot();
    return spot ? {lat:spot.lat,lon:spot.lon,label:'景點代表點'} : null;
  }

  function samplePointValue(point,key){
    if(!point) return null;
    const data=activeDataset(key);
    const bbox=normalizeViewBbox(data?.bbox);
    if(bbox && (
      point.lon<bbox.leftlon || point.lon>bbox.rightlon ||
      point.lat<bbox.bottomlat || point.lat>bbox.toplat
    )) return null;
    const values=decodedArray(key);
    if(key==='wind_direction_10m_deg'){
      return values[nearestCellIndex(point.lon,point.lat,data)];
    }

    const lons=data.grid.longitudes, lats=data.grid.latitudes;
    const ascLon=lons[0] < lons[lons.length-1];
    const ascLat=lats[0] < lats[lats.length-1];
    const lonA=ascLon?lons:[...lons].reverse();
    const latA=ascLat?lats:[...lats].reverse();

    function bracket(arr,v){
      if(v<=arr[0]) return [0,0];
      if(v>=arr[arr.length-1]) return [arr.length-1,arr.length-1];
      for(let i=1;i<arr.length;i++) if(v<=arr[i]) return [i-1,i];
      return [arr.length-1,arr.length-1];
    }
    const [x0i,x1i]=bracket(lonA,point.lon), [y0i,y1i]=bracket(latA,point.lat);
    const toOrigX=i=>ascLon?i:lons.length-1-i;
    const toOrigY=i=>ascLat?i:lats.length-1-i;
    const x0=lonA[x0i],x1=lonA[x1i],y0=latA[y0i],y1=latA[y1i];
    const v00=values[toOrigY(y0i)*data.grid.cols+toOrigX(x0i)];
    const v10=values[toOrigY(y0i)*data.grid.cols+toOrigX(x1i)];
    const v01=values[toOrigY(y1i)*data.grid.cols+toOrigX(x0i)];
    const v11=values[toOrigY(y1i)*data.grid.cols+toOrigX(x1i)];
    if([v00,v10,v01,v11].some(v=>v==null)){
      return values[nearestCellIndex(point.lon,point.lat,data)];
    }
    const wx=x1===x0?0:(point.lon-x0)/(x1-x0);
    const wy=y1===y0?0:(point.lat-y0)/(y1-y0);
    return v00*(1-wx)*(1-wy)+v10*wx*(1-wy)+v01*(1-wx)*wy+v11*wx*wy;
  }

  function formatValue(v,key){
    if(v==null || !Number.isFinite(v)) return '—';
    if(key.includes('cloud')) return `${Math.round(v)}%`;
    if(key==='visibility_km') return `${v.toFixed(1)} km`;
    if(key==='precip_rate_mm_h') return `${v.toFixed(2)} mm/h`;
    if(key==='wind_speed_10m_m_s') return `${v.toFixed(1)} m/s`;
    if(key==='wind_direction_10m_deg') return `${Math.round(v)}°`;
    if(key==='temperature_2m_c') return `${v.toFixed(1)} °C`;
    if(key==='relative_humidity_2m_percent') return `${Math.round(v)}%`;
    if(key==='precip_total_mm') return `${v.toFixed(1)} mm`;
    if(key==='shortwave_flux_w_m2') return `${Math.round(v)} W/m²`;
    return v.toFixed(1);
  }

  function formatTaipeiTime(iso){
    try{
      return new Intl.DateTimeFormat('zh-TW',{
        timeZone:'Asia/Taipei',month:'2-digit',day:'2-digit',
        hour:'2-digit',minute:'2-digit',hour12:false
      }).format(new Date(iso));
    }catch(_){ return iso; }
  }

  function updateControls(){
    const f=frame(), cfg=layerConfig[state.layer];
    const data=activeDataset(state.layer);
    const usingIcon=data===state.iconData;
    const usingCwa=data===state.cwaData;
    $('time-slider').value=state.frameIndex;
    $('time-label').textContent=`時間 · ${formatTaipeiTime(f.valid_time_utc)} (f${String(f.forecast_hour).padStart(3,'0')})`;
    $('opacity-label').textContent=`${Math.round(state.weatherOpacity*100)}%`;

    const status=$('source-state');
    if(state.source==='demo'){
      status.textContent='DEMO 範例資料';
      status.className='source-pill demo';
    }else{
      if(state.modelMode==='auto'){
        status.textContent=usingIcon?'AUTO · ICON Global':'AUTO · GFS';
      }else{
        status.textContent='LIVE · '+modelLabel(state.modelMode);
      }
      status.className='source-pill';
    }

    let resolution;
    if(usingCwa){
      const p=data.provenance || {};
      resolution=`原生約 ${p.native_resolution_km || 3} km · 瀏覽格 ${p.browser_grid_spacing_degrees || 0.03}° · 公開資料間隔 ${p.public_product_interval_hours || 6} h`;
    }else if(usingIcon){
      resolution=`原生約 ${data.provenance?.native_resolution_km || 13} km · 0.125° remap · 顯示雙線性內插`;
    }else{
      resolution='原生 0.25° · 顯示雙線性內插';
    }
    $('cycle-label').textContent=`Cycle ${data.cycle?.cycle_time_utc || '—'} · ${data.grid.rows}×${data.grid.cols} · ${resolution}`;

    const arr=decodedArray(state.layer).filter(Number.isFinite);
    const min=arr.length?Math.min(...arr):null, max=arr.length?Math.max(...arr):null;
    $('layer-summary').textContent=min==null?'—':`${formatValue(min,state.layer)} – ${formatValue(max,state.layer)}`;
    let providerRole='GFS';
    if(usingCwa) providerRole='CWA WRF 3 km';
    else if(usingIcon) providerRole=state.modelMode==='auto'?'ICON Global · auto':'ICON Global';
    else if(state.modelMode==='auto' && cloudLayers.has(state.layer)) providerRole='GFS fallback';
    $('layer-unit').textContent=`${cfg.label} · ${data.fields[state.layer].unit} · ${providerRole} · 各模型保留自己的範圍／解析度／時間軸`;

    const spot=selectedSpot();
    const point=samplingPoint();
    $('spot-name').textContent=spot?spot.name:'尚未選取';
    const sv=samplePointValue(point,state.layer);
    $('spot-value').textContent=point?formatValue(sv,state.layer):'—';
    $('spot-details').innerHTML=point
      ? `<div>${point.lat.toFixed(4)}°, ${point.lon.toFixed(4)}° · ${escapeHtml(point.label)}</div><div>取樣：瀏覽器雙線性插值（風向使用最近格點；超出模型範圍不外推）</div>`
      : '<div>可從下拉選單或地圖上的景點點位選取。</div>';

    updateLegend(cfg);
    updateTimeline();
    updateCoverageStatus();
    updateQc();
  }
  function updateLegend(cfg){
    const min=cfg.domain[0], max=cfg.domain[1], mid=(min+max)/2;
    const stops=[0,.25,.5,.75,1].map(t=>colorFor(min+(max-min)*t,cfg));
    const windKey=state.windVectors ? `
      <div class="wind-key"><span class="wind-arrow-icon">→</span> 10 m 風向箭頭 · 箭頭指向風去向</div>` : '';
    const coverageKey=state.spotId ? `
      <div class="coverage-key">
        <span><i class="coverage-swatch camera"></i>Camera</span>
        <span><i class="coverage-swatch subject"></i>Subject</span>
        <span><i class="coverage-swatch environment"></i>Environment</span>
      </div>` : '';
    $('legend').innerHTML=`
      <strong>${cfg.label}</strong>
      <div class="legend-bar" style="background:linear-gradient(90deg,${stops.join(',')})"></div>
      <div class="legend-row"><span>${formatValue(min,state.layer)}</span><span>${formatValue(mid,state.layer)}</span><span>${formatValue(max,state.layer)}</span></div>
      ${windKey}
      ${coverageKey}`;
  }

  function updateTimeline(){
    $('timeline').innerHTML=timelineDataset().frames.map((f,i)=>
      `<button type="button" data-i="${i}" class="${i===state.frameIndex?'active':''}">${formatTaipeiTime(f.valid_time_utc)}</button>`
    ).join('');
    $('timeline').querySelectorAll('button').forEach(b=>b.onclick=()=>{
      state.frameIndex=Number(b.dataset.i);renderAll();
    });
  }

  function statusBadge(op){
    if(op.status==='verified' && op.complete) return '<span class="coverage-badge ok">verified</span>';
    if(op.status==='provisional' && op.complete) return '<span class="coverage-badge provisional">provisional</span>';
    return '<span class="coverage-badge pending">needs research</span>';
  }

  function updateCoverageStatus(){
    const host=$('coverage-status');
    if(!state.spotId){
      host.innerHTML='<div>先選景點。題材 coverage 會同時標示 Camera / Subject / Environment。</div>';
      return;
    }

    if(state.coverageSource==='missing'){
      host.innerHTML='<div class="warn">⚠ Live WeatherGrid 已載入，但尚未發布 subject-aware coverage bundle。請執行 publish_preview。</div>';
      return;
    }

    const group=selectedCoverageGroup();
    if(!group){
      host.innerHTML='<div class="warn">⚠ 此景點尚未進入 B120/B121 coverage migration；目前不能宣稱所有題材的相機與被攝主體均已涵蓋。</div>';
      return;
    }

    const op=selectedOpportunity();
    if(!op){
      const total=Number(group.catalog_opportunity_count ?? group.opportunities.length);
      const migrated=Number(group.coverage_entry_count ?? group.opportunities.length);
      const incomplete=group.opportunities.filter(x=>!x.complete).length;
      const allComplete=Boolean(group.all_topics_complete);
      const union=unionViewport(group.opportunities);
      const providerOk=union ? providerCoversBbox(union) : false;
      host.innerHTML=`
        <div>${allComplete?'<span class="coverage-badge ok">all topics covered</span>':'<span class="coverage-badge provisional">partial migration</span>'}</div>
        <div>已建立 coverage：${migrated} / ${total} 個題材；其中 ${incomplete} 個仍不完整。</div>
        <div>${providerOk?'✓ 目前 WeatherGrid bbox 可涵蓋已建立的題材視野。':'⚠ 目前 WeatherGrid bbox 無法完整涵蓋已建立題材視野。'}</div>
        <div>選擇單一題材可檢查 Camera / Subject / Environment。</div>`;
      return;
    }

    const providerOk=op.viewport_bbox ? providerCoversBbox(op.viewport_bbox) : false;
    const errors=(op.errors||[]).map(e=>`<div class="warn">⚠ ${escapeHtml(e)}</div>`).join('');
    const warnings=(op.warnings||[]).map(e=>`<div class="warn">△ ${escapeHtml(e)}</div>`).join('');
    host.innerHTML=`
      <div>${statusBadge(op)} <strong>${escapeHtml(op.name_zh||op.opportunity_id)}</strong></div>
      <div>Camera ${(op.camera_zones||[]).length} · Subject ${(op.subject_geometries||[]).length} · Environment ${(op.environment_geometries||[]).length}</div>
      <div>${providerOk?'✓ 當前氣象資料涵蓋題材 viewport。':'⚠ 題材 viewport 超出當前氣象資料範圍；空白區不可視為晴朗。'}</div>
      ${op.note?`<div>${escapeHtml(op.note)}</div>`:''}
      ${errors}${warnings}`;
  }

  function updateQc(){
    const host=$('qc-status');
    if(state.source==='demo'){
      host.innerHTML='<div class="warn">⚠️ 目前顯示 DEMO fixture；發布 live WeatherGrid 後會自動採 ICON cloud / GFS fallback。</div>';
      return;
    }
    const qc=activeQc(state.layer);
    if(!qc){
      host.innerHTML='<div>此快照沒有 QC 檔。</div>';return;
    }
    const fh=frame().forecast_hour;
    const flags=qc.flags.filter(x=>x.forecast_hour===fh && x.field===state.layer);
    if(!flags.length){
      host.innerHTML='<div class="ok">✓ 此圖層／時段沒有 QC 警示</div>';
    }else{
      host.innerHTML=flags.map(x=>`<div class="warn">⚠ ${escapeHtml(x.flag)}</div>`).join('');
    }
  }

  function renderAll(){
    if(!state.data) return;
    draw();
    updateControls();
    window.__weatherGridCoverageDebug = {
      spotId: state.spotId,
      opportunityId: state.opportunityId,
      coverageSource: state.coverageSource,
      windVectors: state.windVectors,
      windVectorStep: windVectorStep(),
      windVectorCount: state.lastWindVectorCount,
      activeModel: activeDataset(state.layer)?.model || null,
      displayInterpolation: state.layer==='wind_direction_10m_deg'?'nearest':'bilinear_subcell',
      iconAvailable: Boolean(state.iconData),
      cwaAvailable: Boolean(state.cwaData),
      modelMode: state.modelMode,
      timelineModel: timelineDataset()?.model || null,
      view: {...state.view}
    };
  }

  window.addEventListener('resize',()=>{
    if(state.map) state.map.resize();
    renderAll();
  });
  load().catch(err=>{
    console.error(err);
    $('source-state').textContent='載入失敗';
    $('source-state').className='source-pill error';
    $('qc-status').innerHTML=`<div class="warn">${escapeHtml(err.message)}</div>`;
  });
})();
