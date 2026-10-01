(() => {
  const LIVE_DATA = './weathergrid/gfs_tw_weather_browser.json';
  const LIVE_QC = './weathergrid/gfs_tw_weather_qc.json';
  const LIVE_ICON_DATA = './weathergrid/icon_tw_cloud_browser.json';
  const LIVE_ICON_QC = './weathergrid/icon_tw_cloud_qc.json';
  const LIVE_CWA_DATA = './weathergrid/cwa_wrf3_tw_weather_browser.json';
  const LIVE_CWA_QC = './weathergrid/cwa_wrf3_tw_weather_qc.json';
  const LIVE_JMA_DATA = './weathergrid/jma_msm_tw_cloud_browser.json';
  const LIVE_JMA_QC = './weathergrid/jma_msm_tw_cloud_qc.json';
  const LIVE_HIMAWARI_DATA = './weathergrid/himawari9_tw_cloud_browser.json';
  const LIVE_HIMAWARI_QC = './weathergrid/himawari9_tw_cloud_qc.json';
  const LIVE_CAMS_DATA = './weathergrid/cams_global_tw_aod_browser.json';
  const LIVE_CAMS_QC = './weathergrid/cams_global_tw_aod_qc.json';
  const LIVE_VIIRS_DATA = './weathergrid/viirs_nightlights_tw_browser.json';
  const LIVE_VIIRS_QC = './weathergrid/viirs_nightlights_tw_qc.json';
  const LIVE_COVERAGE = './weathergrid/weathergrid_coverage_browser.json';
  const FALLBACK_DATA = './weathergrid_sample.json';
  const FALLBACK_COVERAGE = './weathergrid_coverage_sample.json';
  const MAPLIBRE_MODULE = 'https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl.mjs';
  const BASEMAP_STYLE = 'https://tiles.openfreemap.org/styles/liberty';

  // One provider-independent forecast cloud scale keeps JMA, CWA, ICON and
  // GFS directly comparable. Observation layers keep separate semantics.
  const CLOUD_PERCENT_BREAKS=[0,20,40,50,70,85,100];
  const CLOUD_PERCENT_BANDS=[
    {min:0,max:20,color:'hsl(190 78% 68%)'},
    {min:20,max:40,color:'hsl(199 82% 56%)'},
    {min:40,max:50,color:'hsl(216 82% 50%)'},
    {min:50,max:70,color:'hsl(238 78% 50%)'},
    {min:70,max:85,color:'hsl(263 72% 60%)'},
    {min:85,max:100,color:'hsl(285 48% 82%)'}
  ];
  const CLOUD_OPACITY_STOPS=[
    [0,.02],[20,.12],[40,.32],[50,.55],[70,.72],[85,.88],[100,1]
  ];
  const CLOUD_MAX_OVERLAY_ALPHA=.78;

  const layerConfig = {
    total_cloud_percent:{label:'全雲量', unit:'%', domain:[0,100], palette:'cloud', scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    low_cloud_percent: {label:'低雲', unit:'%', domain:[0,100], palette:'cloud', scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    mid_cloud_percent: {label:'中雲', unit:'%', domain:[0,100], palette:'cloud', scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    high_cloud_percent:{label:'高雲', unit:'%', domain:[0,100], palette:'cloud', scale:'cloud_percent', ticks:CLOUD_PERCENT_BREAKS},
    observed_cloud_mask:{label:'衛星雲遮罩', unit:'類別', domain:[0,1], palette:'cloudMask'},
    cloud_top_height_m:{label:'雲頂高度', unit:'m', domain:[0,16000], palette:'cloudHeight'},
    visibility_km:{label:'能見度', unit:'km', domain:[0,30], palette:'visibility'},
    precip_rate_mm_h:{label:'降雨率', unit:'mm/h', domain:[0,20], palette:'precip', scale:'precip_rate', ticks:[0,.1,.5,1,2,5,10,20]},
    wind_speed_10m_m_s:{label:'10 m 風場', unit:'m/s', domain:[0,20], palette:'wind'},
    wind_direction_10m_deg:{label:'10 m 風向', unit:'°', domain:[0,360], palette:'direction'},
    temperature_2m_c:{label:'2 m 氣溫', unit:'°C', domain:[-5,40], palette:'temperature'},
    relative_humidity_2m_percent:{label:'2 m 相對濕度', unit:'%', domain:[0,100], palette:'humidity'},
    precip_total_mm:{label:'累積降水', unit:'mm', domain:[0,100], palette:'precip'},
    shortwave_flux_w_m2:{label:'地表淨短波輻射', unit:'W/m²', domain:[0,1000], palette:'solar'},
    aerosol_optical_depth_550nm:{label:'AOD 550 nm', unit:'1', domain:[0,1.5], palette:'haze', scale:'aod', ticks:[0,.05,.1,.2,.4,.8,1.5]},
    pm2_5_ug_m3:{label:'PM2.5', unit:'µg/m³', domain:[0,75], palette:'pm25', scale:'pm25', ticks:[0,5,10,15,25,35,50,75]},
    nighttime_lights_radiance_nw_cm2_sr:{label:'夜間燈光', unit:'nW/(cm²·sr)', domain:[0,50], palette:'nightlights', scale:'nightlights', ticks:[0,.5,1,2,5,10,25,50]}
  };

  const state = {
    data:null,
    qc:null,
    iconData:null,
    iconQc:null,
    cwaData:null,
    cwaQc:null,
    jmaData:null,
    jmaQc:null,
    himawariData:null,
    himawariQc:null,
    camsData:null,
    camsQc:null,
    viirsData:null,
    viirsQc:null,
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
    timelinePlaying:false,
    timelineTimer:null,
    spotHitTargets:[],
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
    const targets=state.spotHitTargets || [];
    for(const target of targets){
      const d=Math.hypot(target.x-px,target.y-py);
      if(!best || d<best.d) best={target,d};
    }
    if(!best || best.d>Math.max(24,(best.target.radius || 0)+10)) return;
    const spots=best.target.spots || [];
    if(spots.length>1){
      zoomToSpotCluster(spots);
      return;
    }
    const spot=spots[0];
    if(spot){
      $('spot-select').value=spot.spot_id;
      selectSpot(spot.spot_id);
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
        attributionControl:false
      });
      state.map=map;
      map.touchZoomRotate.disableRotation();
      map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');
      map.addControl(new maplibregl.AttributionControl({compact:true}),'bottom-right');

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

  function normalizeHimawariBundle(raw){
    if(!raw?.grid || !raw?.fields || !raw?.values || !raw?.observation){
      throw new Error('Invalid Himawari-9 observation bundle');
    }
    const validTime=raw.observation.time_coverage_end || raw.observation.slot_utc;
    if(!validTime) throw new Error('Himawari-9 observation time missing');
    return {
      ...raw,
      model:'HIMAWARI9_AHI_OBS',
      fields:{
        ...raw.fields,
        observed_cloud_mask:{
          ...raw.fields.observed_cloud_mask,
          scale:Number.isFinite(raw.fields.observed_cloud_mask?.scale)
            ? raw.fields.observed_cloud_mask.scale
            : 1
        }
      },
      frames:[{
        forecast_hour:0,
        valid_time_utc:validTime,
        observation_time_utc:validTime,
        values:raw.values
      }]
    };
  }

  function isObservationMode(){
    return state.modelMode==='himawari' && Boolean(state.himawariData);
  }

  function isStaticEnvironmentMode(){
    return state.modelMode==='viirs' && Boolean(state.viirsData);
  }

  function observationAgeMinutes(data=state.himawariData){
    const stamp=data?.observation?.time_coverage_end || data?.observation?.slot_utc;
    const time=Date.parse(stamp || '');
    if(!Number.isFinite(time)) return null;
    return Math.max(0,(Date.now()-time)/60000);
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
        state.jmaData = await fetchJson(LIVE_JMA_DATA);
        try{ state.jmaQc = await fetchJson(LIVE_JMA_QC); }catch(_){ state.jmaQc = null; }
      }catch(err){
        console.warn('JMA MSM 5 km bundle unavailable', err);
        state.jmaData = null;
        state.jmaQc = null;
      }

      try{
        state.himawariData = normalizeHimawariBundle(
          await fetchJson(LIVE_HIMAWARI_DATA)
        );
        try{ state.himawariQc = await fetchJson(LIVE_HIMAWARI_QC); }catch(_){ state.himawariQc = null; }
      }catch(err){
        console.warn('Himawari-9 observation bundle unavailable', err);
        state.himawariData = null;
        state.himawariQc = null;
      }

      try{
        state.camsData = await fetchJson(LIVE_CAMS_DATA);
        try{ state.camsQc = await fetchJson(LIVE_CAMS_QC); }catch(_){ state.camsQc = null; }
      }catch(err){
        console.warn('CAMS Global AOD bundle unavailable', err);
        state.camsData = null;
        state.camsQc = null;
      }

      try{
        const viirsData = await fetchJson(LIVE_VIIRS_DATA);
        const viirsQc = await fetchJson(LIVE_VIIRS_QC);
        const qcFlags = Array.isArray(viirsQc?.flags) ? viirsQc.flags : ['qc_missing'];
        const validContract = viirsData?.source==='nasa_black_marble_vnp46a4' &&
          Boolean(viirsData?.fields?.nighttime_lights_radiance_nw_cm2_sr) &&
          qcFlags.length===0;
        if(!validContract) throw new Error('VIIRS nighttime-light artifact failed contract/QC gate');
        state.viirsData = viirsData;
        state.viirsQc = viirsQc;
      }catch(err){
        // B169f fail-closed UI contract: no real+QC-passing artifact means
        // no selectable nighttime-light source is exposed to the user.
        console.info('VIIRS nighttime-light layer not published', err);
        state.viirsData = null;
        state.viirsQc = null;
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
    if(mode==='himawari' && state.himawariData) return state.himawariData;
    if(mode==='jma' && state.jmaData) return state.jmaData;
    if(mode==='cwa' && state.cwaData) return state.cwaData;
    if(mode==='icon' && state.iconData) return state.iconData;
    if(mode==='cams' && state.camsData) return state.camsData;
    if(mode==='viirs' && state.viirsData) return state.viirsData;
    return state.data;
  }

  function modelQc(mode=state.modelMode){
    if(mode==='himawari' && state.himawariData) return state.himawariQc;
    if(mode==='jma' && state.jmaData) return state.jmaQc;
    if(mode==='cwa' && state.cwaData) return state.cwaQc;
    if(mode==='icon' && state.iconData) return state.iconQc;
    if(mode==='cams' && state.camsData) return state.camsQc;
    if(mode==='viirs' && state.viirsData) return state.viirsQc;
    return state.qc;
  }

  function modelLabel(mode=state.modelMode){
    if(mode==='himawari') return 'Himawari-9 2 km';
    if(mode==='jma') return 'JMA MSM 5 km';
    if(mode==='cwa') return 'CWA WRF 3 km';
    if(mode==='icon') return 'ICON Global';
    if(mode==='gfs') return 'GFS 0.25°';
    if(mode==='cams') return 'CAMS Global · 霧霾';
    if(mode==='viirs') return 'NASA Black Marble · 夜間燈光';
    return '自動';
  }

  function modelAvailable(mode){
    if(mode==='himawari') return Boolean(state.himawariData);
    if(mode==='jma') return Boolean(state.jmaData);
    if(mode==='cwa') return Boolean(state.cwaData);
    if(mode==='icon') return Boolean(state.iconData);
    if(mode==='gfs') return Boolean(state.data);
    if(mode==='cams') return Boolean(state.camsData);
    if(mode==='viirs') return Boolean(state.viirsData);
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
    const visibleLayerKeys=Object.keys(layerConfig).filter(key=>key!=='wind_direction_10m_deg');
    if(state.modelMode==='auto'){
      return visibleLayerKeys.filter(key=>
        Boolean(state.data?.fields?.[key]) ||
        Boolean(state.iconData?.fields?.[key])
      );
    }
    const data=modelDataset();
    return visibleLayerKeys.filter(key=>Boolean(data?.fields?.[key]));
  }

  function windFieldsAvailable(){
    return Boolean(
      activeDataset('wind_speed_10m_m_s')?.fields?.wind_speed_10m_m_s &&
      activeDataset('wind_direction_10m_deg')?.fields?.wind_direction_10m_deg
    );
  }

  function isWindLayer(layer=state.layer){
    return layer==='wind_speed_10m_m_s';
  }

  function syncWindVectorDefault(){
    if(!state.windVectorTouched){
      state.windVectors=isWindLayer() && windFieldsAvailable();
    }
  }

  function refreshModelControls(){
    const modelSelect=$('model-select');
    let viirsOption=modelSelect.querySelector('option[value="viirs"]');
    if(state.viirsData && !viirsOption){
      viirsOption=document.createElement('option');
      viirsOption.value='viirs';
      viirsOption.textContent='NASA Black Marble · 夜間燈光';
      modelSelect.appendChild(viirsOption);
    }else if(!state.viirsData && viirsOption){
      viirsOption.remove();
    }
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
    slider.disabled=isObservationMode() || isStaticEnvironmentMode();

    syncWindVectorDefault();
    const hasWind=windFieldsAvailable();
    const windToggle=$('wind-vector-toggle');
    windToggle.disabled=!hasWind;
    if(!hasWind) state.windVectors=false;
    windToggle.checked=state.windVectors;
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
    stopTimelinePlayback();
    refreshModelControls();
    setViewBbox(timeline.bbox,{animate:true,maxZoom:8});
    renderAll();
  }

  function stopTimelinePlayback(){
    if(state.timelineTimer){
      window.clearInterval(state.timelineTimer);
      state.timelineTimer=null;
    }
    state.timelinePlaying=false;
  }

  function setFrameIndex(index){
    const max=Math.max(0,(timelineDataset()?.frames?.length || 1)-1);
    state.frameIndex=Math.max(0,Math.min(max,Number(index) || 0));
    $('time-slider').value=state.frameIndex;
    renderAll();
  }

  function toggleTimelinePlayback(){
    const count=timelineDataset()?.frames?.length || 0;
    if(count<2){
      stopTimelinePlayback();
      renderAll();
      return;
    }
    if(state.timelinePlaying){
      stopTimelinePlayback();
      renderAll();
      return;
    }
    state.timelinePlaying=true;
    state.timelineTimer=window.setInterval(()=>{
      const count=timelineDataset()?.frames?.length || 0;
      if(count<2){
        stopTimelinePlayback();
        renderAll();
        return;
      }
      state.frameIndex=(state.frameIndex+1)%count;
      renderAll();
    },900);
    renderAll();
  }

  function initDataInfoDialog(){
    const dialog=$('data-info-dialog');
    const open=$('data-info-open');
    const close=$('data-info-close');
    if(!dialog || !open || !close) return;

    open.addEventListener('click',()=>{
      if(typeof dialog.showModal==='function') dialog.showModal();
      else dialog.setAttribute('open','');
    });
    close.addEventListener('click',()=>{
      if(typeof dialog.close==='function') dialog.close();
      else dialog.removeAttribute('open');
    });
    dialog.addEventListener('click',ev=>{
      if(ev.target!==dialog) return;
      if(typeof dialog.close==='function') dialog.close();
      else dialog.removeAttribute('open');
    });
  }

  function syncInspectorVisibility(){
    const hasSpot=Boolean(state.spotId);
    $('spot-panel').hidden=!hasSpot;
    $('coverage-panel').hidden=!hasSpot;

    // On phones, do not spend an entire row on a disabled topic selector.
    // Once a Place is selected the topic selector returns beside it.
    const opportunityControl=$('opportunity-control');
    const spotControl=document.querySelector('.spot-control');
    if(opportunityControl) opportunityControl.classList.toggle('mobile-inactive',!hasSpot);
    if(spotControl) spotControl.classList.toggle('mobile-full',!hasSpot);
  }

  function initControls(){
    const modelSelect=$('model-select');
    modelSelect.addEventListener('change',()=>switchModel(modelSelect.value));

    const layerSelect = $('layer-select');
    const windToggle=$('wind-vector-toggle');
    const layerDetailsToggle=$('layer-details-toggle');
    const layerDetails=$('layer-details');

    if(layerDetailsToggle && layerDetails){
      layerDetailsToggle.addEventListener('click',()=>{
        const expanded=layerDetailsToggle.getAttribute('aria-expanded')==='true';
        const next=!expanded;
        layerDetailsToggle.setAttribute('aria-expanded',next?'true':'false');
        layerDetailsToggle.textContent=next?'收合':'詳細';
        layerDetails.classList.toggle('is-expanded',next);
      });
    }

    windToggle.addEventListener('change',()=>{
      state.windVectors=windToggle.checked;
      state.windVectorTouched=true;
      renderAll();
    });

    layerSelect.addEventListener('change', () => {
      state.layer = layerSelect.value;
      syncWindVectorDefault();
      windToggle.checked=state.windVectors;
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
      stopTimelinePlayback();
      setFrameIndex(Number(slider.value));
    });
    $('time-prev').addEventListener('click',()=>{
      stopTimelinePlayback();
      setFrameIndex(state.frameIndex-1);
    });
    $('time-next').addEventListener('click',()=>{
      stopTimelinePlayback();
      setFrameIndex(state.frameIndex+1);
    });
    $('time-play').addEventListener('click',toggleTimelinePlayback);

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

    initDataInfoDialog();
    syncInspectorVisibility();
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
    if(state.modelMode==='himawari' && state.himawariData) return state.himawariData;
    if(state.modelMode==='jma' && state.jmaData) return state.jmaData;
    if(state.modelMode==='cwa' && state.cwaData) return state.cwaData;
    if(state.modelMode==='icon' && state.iconData) return state.iconData;
    if(state.modelMode==='cams' && state.camsData) return state.camsData;
    if(state.modelMode==='viirs' && state.viirsData) return state.viirsData;
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
    'total_cloud_percent',
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
    if(state.modelMode==='himawari' && state.himawariData) return state.himawariData;
    if(state.modelMode==='jma' && state.jmaData) return state.jmaData;
    if(state.modelMode==='cwa' && state.cwaData){
      return state.cwaData.fields[key] ? state.cwaData : state.cwaData;
    }
    if(state.modelMode==='icon' && state.iconData) return state.iconData;
    if(state.modelMode==='cams' && state.camsData) return state.camsData;
    if(state.modelMode==='viirs' && state.viirsData) return state.viirsData;
    if(state.modelMode==='gfs') return state.data;

    if(cloudLayers.has(key) && state.iconData){
      const iconFrame=iconFrameForValidTime(baseFrame()?.valid_time_utc);
      if(iconFrame && state.iconData.fields[key]) return state.iconData;
    }
    return state.data;
  }

  function activeFrame(key=state.layer){
    if(state.modelMode==='himawari' || state.modelMode==='jma' || state.modelMode==='cwa' || state.modelMode==='icon' || state.modelMode==='cams' || state.modelMode==='viirs' || state.modelMode==='gfs'){
      return timelineDataset()?.frames?.[state.frameIndex] || null;
    }
    const data=activeDataset(key);
    if(data===state.iconData){
      return iconFrameForValidTime(baseFrame()?.valid_time_utc);
    }
    return baseFrame();
  }

  function activeQc(key=state.layer){
    if(state.modelMode==='himawari') return state.himawariQc;
    if(state.modelMode==='jma') return state.jmaQc;
    if(state.modelMode==='cwa') return state.cwaQc;
    if(state.modelMode==='icon') return state.iconQc;
    if(state.modelMode==='cams') return state.camsQc;
    if(state.modelMode==='viirs') return state.viirsQc;
    if(state.modelMode==='gfs') return state.qc;
    return activeDataset(key)===state.iconData ? state.iconQc : state.qc;
  }

  function frame(){ return activeFrame(state.layer); }

  function decodeValue(key, encoded, data=activeDataset(key)){
    if(encoded == null || !data?.fields?.[key]) return null;
    const meta = data.fields[key];
    const scale=Number.isFinite(meta.scale) ? meta.scale : 1;
    let value = encoded * scale;
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

  function normalizedPiecewise(value,breaks){
    if(!Number.isFinite(value) || !breaks?.length) return 0;
    if(value<=breaks[0]) return 0;
    const last=breaks.length-1;
    if(value>=breaks[last]) return 1;
    for(let i=1;i<breaks.length;i++){
      if(value<=breaks[i]){
        const local=(value-breaks[i-1])/(breaks[i]-breaks[i-1]);
        return ((i-1)+local)/last;
      }
    }
    return 1;
  }

  function normalizedValue(value,cfg){
    if(value == null || !Number.isFinite(value)) return 0;
    if(cfg.scale==='precip_rate' || cfg.scale==='aod' || cfg.scale==='nightlights') return normalizedPiecewise(value,cfg.ticks);
    const span=cfg.domain[1]-cfg.domain[0];
    if(!span) return 0;
    return Math.max(0,Math.min(1,(value-cfg.domain[0])/span));
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

  function cloudColorFor(value){
    const v=Math.max(0,Math.min(100,Number(value)));
    const band=CLOUD_PERCENT_BANDS.find(item=>v<item.max) ||
      CLOUD_PERCENT_BANDS[CLOUD_PERCENT_BANDS.length-1];
    return band.color;
  }

  function cloudLegendGradient(){
    return CLOUD_PERCENT_BANDS.flatMap(item=>[
      `${item.color} ${item.min}%`,
      `${item.color} ${item.max}%`
    ]).join(',');
  }

  function cloudLegendLabels(){
    return CLOUD_PERCENT_BREAKS.map((value,index)=>{
      const edge=index===0?' first':(index===CLOUD_PERCENT_BREAKS.length-1?' last':'');
      const row=index%2===0?' lower':' upper';
      const midpoint=value===50?' midpoint':'';
      return `<span class="cloud-tick${edge}${row}${midpoint}" style="left:${value}%">${value}%</span>`;
    }).join('');
  }

  function layerOpacityCap(cfg){
    return cfg.palette==='cloud' ? CLOUD_MAX_OVERLAY_ALPHA : 1;
  }

  function cellOpacityFor(value,cfg){
    if(value == null || !Number.isFinite(value)){
      if(cfg.palette==='cloudMask' || cfg.palette==='cloudHeight') return 0;
      return .08;
    }
    const t=normalizedValue(value,cfg);
    if(cfg.palette==='cloudMask') return value>=.5 ? .84 : 0;
    if(cfg.palette==='cloudHeight') return .28 + .72*t;
    if(cfg.palette==='cloud'){
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

  function fillWeatherPolygon(points,value,cfg){
    ctx.beginPath();
    points.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y));
    ctx.closePath();
    ctx.globalAlpha=state.weatherOpacity*layerOpacityCap(cfg)*cellOpacityFor(value,cfg);
    ctx.fillStyle=colorFor(value,cfg);
    ctx.fill();
  }

  function bilinearValue(q00,q10,q01,q11,wx,wy){
    if([q00,q10,q01,q11].some(v=>!Number.isFinite(v))) return null;
    return q00*(1-wx)*(1-wy)+q10*wx*(1-wy)+
      q01*(1-wx)*wy+q11*wx*wy;
  }

  function windUv(speed,directionDeg){
    if(!Number.isFinite(directionDeg)) return null;
    const s=Number.isFinite(speed) ? Math.max(0,speed) : 1;
    const rad=directionDeg*Math.PI/180;
    // Meteorological direction is "from": u eastward, v northward.
    return {u:-s*Math.sin(rad),v:-s*Math.cos(rad)};
  }

  function directionFromUv(u,v){
    if(!Number.isFinite(u) || !Number.isFinite(v) || Math.hypot(u,v)<1e-9) return null;
    return ((Math.atan2(-u,-v)*180/Math.PI)%360+360)%360;
  }

  function bilinearWindDirection(d00,d10,d01,d11,s00,s10,s01,s11,wx,wy){
    const dirs=[d00,d10,d01,d11];
    if(dirs.some(v=>!Number.isFinite(v))) return null;
    const speeds=[s00,s10,s01,s11];
    const uv=dirs.map((d,i)=>windUv(Number.isFinite(speeds[i])?speeds[i]:1,d));
    const u=bilinearValue(uv[0].u,uv[1].u,uv[2].u,uv[3].u,wx,wy);
    const v=bilinearValue(uv[0].v,uv[1].v,uv[2].v,uv[3].v,wx,wy);
    return directionFromUv(u,v);
  }

  function visibleAxisRange(values,minValue,maxValue,pad=1){
    let first=-1,last=-1;
    for(let i=0;i<values.length;i++){
      const v=values[i];
      if(v>=minValue && v<=maxValue){
        if(first<0) first=i;
        last=i;
      }
    }
    if(first<0){
      // A viewport can sit between two grid centers. Find the nearest center
      // and keep a padded slice so cell edges/interpolation still render.
      let nearest=0,best=Infinity;
      const target=(minValue+maxValue)/2;
      for(let i=0;i<values.length;i++){
        const d=Math.abs(values[i]-target);
        if(d<best){best=d;nearest=i;}
      }
      first=last=nearest;
    }
    return [Math.max(0,first-pad),Math.min(values.length-1,last+pad)];
  }

  function visibleGridRange(data,visibleView,pad=1){
    const [row0,row1]=visibleAxisRange(
      data.grid.latitudes,visibleView.bottomlat,visibleView.toplat,pad
    );
    const [col0,col1]=visibleAxisRange(
      data.grid.longitudes,visibleView.leftlon,visibleView.rightlon,pad
    );
    return {row0,row1,col0,col1};
  }

  function drawNearestCells(data,vals,cfg,visibleView){
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    const lonStep=cols>1 ? Math.abs(lons[1]-lons[0]) : .25;
    const latStep=rows>1 ? Math.abs(lats[1]-lats[0]) : .25;
    const {row0,row1,col0,col1}=visibleGridRange(data,visibleView,1);
    for(let r=row0;r<=row1;r++){
      for(let c=col0;c<=col1;c++){
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

    const {row0,row1,col0,col1}=visibleGridRange(data,visibleView,1);
    const maxRow=Math.min(rows-2,row1);
    const maxCol=Math.min(cols-2,col1);
    for(let r=Math.min(row0,maxRow);r<=maxRow;r++){
      for(let c=Math.min(col0,maxCol);c<=maxCol;c++){
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

  function contourCrossing(p1,p2,v1,v2,threshold){
    if(!Number.isFinite(v1) || !Number.isFinite(v2) || v1===v2) return null;
    const a=v1-threshold,b=v2-threshold;
    if((a<0 && b<0) || (a>0 && b>0)) return null;
    const t=(threshold-v1)/(v2-v1);
    if(t<0 || t>1) return null;
    return {
      lon:p1.lon+(p2.lon-p1.lon)*t,
      lat:p1.lat+(p2.lat-p1.lat)*t
    };
  }

  function drawCloudThresholdContour(data,vals,threshold,visibleView){
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    if(rows<2 || cols<2) return;

    ctx.save();
    ctx.strokeStyle='rgba(254,240,138,.68)';
    ctx.lineWidth=1.15;
    ctx.setLineDash([2,3]);
    ctx.lineCap='round';

    const strokeSegment=(a,b)=>{
      const pa=project(a.lon,a.lat),pb=project(b.lon,b.lat);
      ctx.beginPath();ctx.moveTo(pa.x,pa.y);ctx.lineTo(pb.x,pb.y);ctx.stroke();
    };

    for(let r=0;r<rows-1;r++){
      for(let c=0;c<cols-1;c++){
        const lon0=lons[c],lon1=lons[c+1],lat0=lats[r],lat1=lats[r+1];
        const left=Math.min(lon0,lon1),right=Math.max(lon0,lon1);
        const bottom=Math.min(lat0,lat1),top=Math.max(lat0,lat1);
        if(right<visibleView.leftlon || left>visibleView.rightlon ||
           top<visibleView.bottomlat || bottom>visibleView.toplat) continue;

        const q00=vals[r*cols+c],q10=vals[r*cols+c+1];
        const q01=vals[(r+1)*cols+c],q11=vals[(r+1)*cols+c+1];
        if([q00,q10,q01,q11].some(v=>!Number.isFinite(v))) continue;

        const p00={lon:lon0,lat:lat0},p10={lon:lon1,lat:lat0};
        const p01={lon:lon0,lat:lat1},p11={lon:lon1,lat:lat1};
        const candidates=[
          contourCrossing(p00,p10,q00,q10,threshold),
          contourCrossing(p10,p11,q10,q11,threshold),
          contourCrossing(p11,p01,q11,q01,threshold),
          contourCrossing(p01,p00,q01,q00,threshold)
        ].filter(Boolean);
        const crossings=[];
        for(const point of candidates){
          if(!crossings.some(other=>
            Math.abs(other.lon-point.lon)<1e-9 && Math.abs(other.lat-point.lat)<1e-9
          )) crossings.push(point);
        }

        if(crossings.length===2){
          strokeSegment(crossings[0],crossings[1]);
        }else if(crossings.length===4){
          const center=(q00+q10+q01+q11)/4;
          if(center>=threshold){
            strokeSegment(crossings[0],crossings[3]);
            strokeSegment(crossings[1],crossings[2]);
          }else{
            strokeSegment(crossings[0],crossings[1]);
            strokeSegment(crossings[2],crossings[3]);
          }
        }
      }
    }
    ctx.restore();
  }

  function drawCircularDirectionSubcells(data,directions,speeds,cfg,visibleView){
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    if(rows<2 || cols<2){
      drawNearestCells(data,directions,cfg,visibleView);
      return;
    }
    const lonStep=Math.abs(lons[1]-lons[0]);
    const subdivisions=lonStep>=.20 ? 4 : (lonStep>=.10 ? 2 : 1);
    for(let r=0;r<rows-1;r++){
      for(let c=0;c<cols-1;c++){
        const lon0=lons[c], lon1=lons[c+1], lat0=lats[r], lat1=lats[r+1];
        const left=Math.min(lon0,lon1), right=Math.max(lon0,lon1);
        const bottom=Math.min(lat0,lat1), top=Math.max(lat0,lat1);
        if(right < visibleView.leftlon || left > visibleView.rightlon ||
           top < visibleView.bottomlat || bottom > visibleView.toplat) continue;
        const i00=r*cols+c, i10=i00+1, i01=(r+1)*cols+c, i11=i01+1;
        for(let sy=0;sy<subdivisions;sy++){
          for(let sx=0;sx<subdivisions;sx++){
            const x0=sx/subdivisions, x1=(sx+1)/subdivisions;
            const y0=sy/subdivisions, y1=(sy+1)/subdivisions;
            const wx=(x0+x1)/2, wy=(y0+y1)/2;
            const value=bilinearWindDirection(
              directions[i00],directions[i10],directions[i01],directions[i11],
              speeds[i00],speeds[i10],speeds[i01],speeds[i11],wx,wy
            );
            if(value==null) continue;
            const subLon0=lon0+(lon1-lon0)*x0, subLon1=lon0+(lon1-lon0)*x1;
            const subLat0=lat0+(lat1-lat0)*y0, subLat1=lat0+(lat1-lat0)*y1;
            fillWeatherPolygon([
              project(subLon0,subLat0),project(subLon1,subLat0),
              project(subLon1,subLat1),project(subLon0,subLat1)
            ],value,cfg);
          }
        }
      }
    }
  }

  function drawProviderBoundary(data){
    const b=normalizeViewBbox(data?.bbox);
    if(!b) return;
    const points=[
      project(b.leftlon,b.toplat),project(b.rightlon,b.toplat),
      project(b.rightlon,b.bottomlat),project(b.leftlon,b.bottomlat)
    ];
    ctx.save();
    ctx.beginPath();
    points.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y));
    ctx.closePath();
    ctx.strokeStyle='rgba(125,211,252,.52)';
    ctx.lineWidth=1.25;
    ctx.setLineDash([6,5]);
    ctx.stroke();
    ctx.restore();
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
    if(isObservationMode()){
      // Himawari presentation-grid values are observations/retrievals.
      // Do not synthesize intermediate satellite values with forecast-style interpolation.
      drawNearestCells(data,vals,cfg,visibleView);
    }else if(state.layer==='wind_direction_10m_deg'){
      const speeds=decodedArray('wind_speed_10m_m_s');
      drawCircularDirectionSubcells(data,vals,speeds,cfg,visibleView);
    }else{
      drawBilinearSubcells(data,vals,cfg,visibleView);
    }
    ctx.restore();

    if(!isObservationMode() && cfg.palette==='cloud'){
      drawCloudThresholdContour(data,vals,50,visibleView);
    }

    drawProviderBoundary(data);
    if(!state.mapReady) drawGrid();
    drawWindVectors();
    drawCoverage();
    drawSpots();
  }

  function windVectorStep(){
    const compactUi=window.matchMedia('(max-width:720px)').matches;
    if(state.mapReady && state.map){
      const zoom=state.map.getZoom();
      if(compactUi){
        if(zoom>=8) return 2;
        if(zoom>=6.4) return 3;
        return 4;
      }
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
    if(!state.windVectors && !isWindLayer()) return;
    const data=activeDataset('wind_speed_10m_m_s');
    if(!data?.fields?.wind_speed_10m_m_s ||
       !data?.fields?.wind_direction_10m_deg) return;

    const speeds=decodedArray('wind_speed_10m_m_s');
    const directions=decodedArray('wind_direction_10m_deg');
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    const visible=renderViewBbox();
    const step=windVectorStep();
    const compactUi=window.matchMedia('(max-width:720px)').matches;
    // High-resolution providers (for example CWA WRF 3 km) can still produce
    // a visually solid field even after grid decimation. Enforce a minimum
    // screen-space separation so vectors remain readable at every zoom level.
    const minVectorSpacingPx=compactUi?30:22;
    const occupiedVectorCells=new Set();

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
        const bucketX=Math.floor(p.x/minVectorSpacingPx);
        const bucketY=Math.floor(p.y/minVectorSpacingPx);
        const bucketKey=`${bucketX}:${bucketY}`;
        if(occupiedVectorCells.has(bucketKey)) continue;
        occupiedVectorCells.add(bucketKey);

        const length=(compactUi?9:11)+Math.min(speed/20,1)*(compactUi?13:17);
        // Normalized provider direction is meteorological "from". Arrow points toward motion.
        const toward=((direction+180)%360)*Math.PI/180;
        const dx=Math.sin(toward)*length/2;
        const dy=-Math.cos(toward)*length/2;
        const sx=p.x-dx, sy=p.y-dy, ex=p.x+dx, ey=p.y+dy;

        strokeWindArrow(sx,sy,ex,ey,'rgba(2,6,23,.72)',compactUi?3.5:4.5);
        strokeWindArrow(sx,sy,ex,ey,'rgba(224,242,254,.94)',compactUi?1.6:2);
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

  function spotClusterRadius(){
    const compactMap=canvas.clientWidth<=600;
    if(state.mapReady && state.map){
      const zoom=state.map.getZoom();
      if(compactMap){
        if(zoom<6.2) return 44;
        if(zoom<7.5) return 32;
        if(zoom<8.4) return 20;
        return 0;
      }
      if(zoom<6.2) return 24;
      if(zoom<7.5) return 16;
      return 0;
    }
    const span=Math.max(
      state.view.rightlon-state.view.leftlon,
      state.view.toplat-state.view.bottomlat
    );
    if(compactMap){
      if(span>5) return 44;
      if(span>2) return 32;
      if(span>1) return 20;
      return 0;
    }
    if(span>5) return 24;
    if(span>2) return 16;
    return 0;
  }

  function buildSpotHitTargets(){
    const width=canvas.clientWidth,height=canvas.clientHeight;
    const radius=spotClusterRadius();
    const targets=[];
    for(const spot of state.data.spots){
      const p=project(spot.lon,spot.lat);
      if(p.x<0||p.x>width||p.y<0||p.y>height) continue;
      if(spot.spot_id===state.spotId || radius===0){
        targets.push({x:p.x,y:p.y,spots:[spot],radius:spot.spot_id===state.spotId?7:3});
        continue;
      }
      let target=targets.find(t=>
        !t.spots.some(s=>s.spot_id===state.spotId) &&
        Math.hypot(t.x-p.x,t.y-p.y)<radius
      );
      if(!target){
        target={x:p.x,y:p.y,spots:[],radius};
        targets.push(target);
      }
      target.spots.push(spot);
      const points=target.spots.map(s=>project(s.lon,s.lat));
      target.x=points.reduce((sum,q)=>sum+q.x,0)/points.length;
      target.y=points.reduce((sum,q)=>sum+q.y,0)/points.length;
    }
    return targets;
  }

  function zoomToSpotCluster(spots){
    if(!spots?.length) return;
    if(spots.length===1){
      zoomToSpot(spots[0]);
      return;
    }
    let west=Math.min(...spots.map(s=>s.lon)), east=Math.max(...spots.map(s=>s.lon));
    let south=Math.min(...spots.map(s=>s.lat)), north=Math.max(...spots.map(s=>s.lat));
    const lonPad=Math.max(.08,(east-west)*.35), latPad=Math.max(.06,(north-south)*.35);
    setViewBbox({
      leftlon:west-lonPad,rightlon:east+lonPad,
      bottomlat:south-latPad,toplat:north+latPad
    },{animate:true,maxZoom:9});
    renderAll();
  }

  function drawSpots(){
    const selected=selectedSpot();
    const targets=buildSpotHitTargets();
    const compactMap=canvas.clientWidth<=600;
    state.spotHitTargets=targets;
    ctx.save();
    for(const target of targets){
      const spots=target.spots;
      const isSelected=spots.length===1 && spots[0].spot_id===state.spotId;
      if(spots.length>1){
        const r=compactMap
          ? 8+Math.min(4,Math.log2(spots.length+1)*1.6)
          : 9+Math.min(5,Math.log2(spots.length+1)*2);
        ctx.beginPath();ctx.arc(target.x,target.y,r,0,Math.PI*2);
        ctx.fillStyle='rgba(15,23,42,.72)';ctx.fill();
        ctx.strokeStyle='rgba(186,230,253,.72)';ctx.lineWidth=1.5;ctx.stroke();
        ctx.fillStyle='rgba(248,250,252,.9)';
        ctx.font=compactMap?'700 9px -apple-system, sans-serif':'700 10px -apple-system, sans-serif';
        ctx.textAlign='center';ctx.textBaseline='middle';
        ctx.fillText(String(spots.length),target.x,target.y+.5);
        target.radius=r;
      }else{
        ctx.beginPath();
        ctx.arc(target.x,target.y,isSelected?7:2.8,0,Math.PI*2);
        ctx.fillStyle=isSelected?'#fde68a':'rgba(248,250,252,.68)';
        ctx.fill();
        ctx.strokeStyle=isSelected?'rgba(15,23,42,.95)':'rgba(15,23,42,.65)';
        ctx.lineWidth=isSelected?2:1.2;ctx.stroke();
        target.radius=isSelected?7:3;
      }
    }
    ctx.textAlign='start';ctx.textBaseline='alphabetic';
    if(selected){
      const p=project(selected.lon,selected.lat);
      let selectedLabel=selected.name;
      const selectedCfg=layerConfig[state.layer];
      if(selectedCfg?.palette==='cloud' && !isObservationMode()){
        const value=samplePointValue({lat:selected.lat,lon:selected.lon},state.layer);
        if(Number.isFinite(value)){
          selectedLabel=`${selected.name} · ${formatValue(value,state.layer)}`;
        }
      }
      ctx.font=compactMap?'bold 16px -apple-system, sans-serif':'bold 20px -apple-system, sans-serif';
      ctx.fillStyle='#fef3c7';
      ctx.strokeStyle='rgba(2,6,23,.95)';
      ctx.lineWidth=compactMap?4:5;
      const labelWidth=ctx.measureText(selectedLabel).width;
      let labelX=p.x+13;
      if(labelX+labelWidth>canvas.clientWidth-8){
        labelX=Math.max(8,p.x-13-labelWidth);
      }
      const labelY=Math.max(20,p.y-10);
      ctx.strokeText(selectedLabel,labelX,labelY);
      ctx.fillText(selectedLabel,labelX,labelY);
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

  function sampleDatasetNearest(point,data,key,validTime){
    if(!point || !data?.fields?.[key] || !data?.frames?.length) return null;
    const bbox=normalizeViewBbox(data.bbox);
    if(bbox && (
      point.lon<bbox.leftlon || point.lon>bbox.rightlon ||
      point.lat<bbox.bottomlat || point.lat>bbox.toplat
    )) return null;
    const fi=nearestFrameIndex(data,validTime);
    const encoded=data.frames?.[fi]?.values?.[key];
    if(!encoded) return null;
    const index=nearestCellIndex(point.lon,point.lat,data);
    return decodeValue(key,encoded[index],data);
  }

  function classifyFogHazeEnvironment(point){
    if(!point) return null;
    const validTime=frame()?.valid_time_utc || null;
    const visibilityKm=sampleDatasetNearest(point,state.data,'visibility_km',validTime);
    const low=sampleDatasetNearest(point,state.data,'low_cloud_percent',validTime);
    const rh=sampleDatasetNearest(point,state.cwaData,'relative_humidity_2m_percent',validTime);
    const aod=sampleDatasetNearest(point,state.camsData,'aerosol_optical_depth_550nm',validTime);
    const pm25=sampleDatasetNearest(point,state.camsData,'pm2_5_ug_m3',validTime);
    const visibilityLow=Number.isFinite(visibilityKm) && visibilityKm<=5;
    const nearSaturation=Number.isFinite(rh) && rh>=95;
    const lowCloudSupport=Number.isFinite(low) && low>=70;
    const fogSupport=visibilityLow && (nearSaturation || lowCloudSupport);
    const aerosolSupport=(Number.isFinite(pm25) && pm25>=25) || (Number.isFinite(aod) && aod>=.4);
    const aerosolStrong=(Number.isFinite(pm25) && pm25>=35) || (Number.isFinite(aod) && aod>=.8);
    let stateKey='insufficient_visibility_evidence',confidence='low';
    if(fogSupport && aerosolSupport){
      stateKey='mixed_fog_haze';
      confidence=aerosolStrong && nearSaturation?'medium':'low';
    }else if(fogSupport){
      stateKey='fog_supported';
      confidence=nearSaturation && lowCloudSupport?'medium':'low';
    }else if(visibilityLow && aerosolSupport){
      stateKey='haze_supported';
      confidence=aerosolStrong?'medium':'low';
    }else if(visibilityLow){
      stateKey='low_visibility_unresolved';
    }else if(aerosolSupport){
      stateKey='aerosol_present_visibility_not_degraded';
    }else if(Number.isFinite(visibilityKm)){
      stateKey='no_fog_haze_signal';
    }
    return {state:stateKey,confidence,visibilityKm,rh,low,aod,pm25};
  }

  function fogHazeDiagnosticHtml(point){
    const d=classifyFogHazeEnvironment(point);
    if(!d) return '';
    const labels={
      fog_supported:'霧訊號較強',
      haze_supported:'霾／氣膠訊號較強',
      mixed_fog_haze:'霧與霾訊號並存',
      low_visibility_unresolved:'低能見度，原因未定',
      aerosol_present_visibility_not_degraded:'有氣膠訊號，但目前能見度未明顯下降',
      no_fog_haze_signal:'目前無明顯霧／霾訊號',
      insufficient_visibility_evidence:'能見度證據不足'
    };
    const confidence=d.confidence==='medium'?'中信心':'低信心';
    const metrics=[];
    if(Number.isFinite(d.visibilityKm)) metrics.push(`能見度 ${d.visibilityKm.toFixed(1)} km`);
    if(Number.isFinite(d.rh)) metrics.push(`RH ${Math.round(d.rh)}%`);
    if(Number.isFinite(d.aod)) metrics.push(`AOD ${d.aod.toFixed(2)}`);
    if(Number.isFinite(d.pm25)) metrics.push(`PM2.5 ${d.pm25.toFixed(1)} µg/m³`);
    return `<div><strong>攝影環境診斷 · ${escapeHtml(labels[d.state]||d.state)}</strong> · ${confidence}</div>`+
      `<div>${escapeHtml(metrics.join(' · ') || '資料不足')}</div>`+
      '<div class="muted">診斷用：GFS 能見度／低雲 + CWA RH + CAMS AOD／PM2.5；目前不影響攝影評分。</div>';
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
    if(isObservationMode()){
      return values[nearestCellIndex(point.lon,point.lat,data)] ?? null;
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
    if(key==='wind_direction_10m_deg'){
      const speeds=decodedArray('wind_speed_10m_m_s');
      const i00=toOrigY(y0i)*data.grid.cols+toOrigX(x0i);
      const i10=toOrigY(y0i)*data.grid.cols+toOrigX(x1i);
      const i01=toOrigY(y1i)*data.grid.cols+toOrigX(x0i);
      const i11=toOrigY(y1i)*data.grid.cols+toOrigX(x1i);
      return bilinearWindDirection(
        v00,v10,v01,v11,
        speeds[i00],speeds[i10],speeds[i01],speeds[i11],wx,wy
      ) ?? values[nearestCellIndex(point.lon,point.lat,data)];
    }
    return v00*(1-wx)*(1-wy)+v10*wx*(1-wy)+v01*(1-wx)*wy+v11*wx*wy;
  }

  function formatValue(v,key){
    if(v==null || !Number.isFinite(v)) return '—';
    if(key==='observed_cloud_mask') return v>=.5 ? '有雲' : '晴空';
    if(key==='cloud_top_height_m') return `${(v/1000).toFixed(1)} km`;
    if(key.includes('cloud')) return `${Math.round(v)}%`;
    if(key==='visibility_km') return `${v.toFixed(1)} km`;
    if(key==='precip_rate_mm_h') return `${v.toFixed(2)} mm/h`;
    if(key==='wind_speed_10m_m_s') return `${v.toFixed(1)} m/s`;
    if(key==='wind_direction_10m_deg') return `${Math.round(v)}°`;
    if(key==='temperature_2m_c') return `${v.toFixed(1)} °C`;
    if(key==='relative_humidity_2m_percent') return `${Math.round(v)}%`;
    if(key==='precip_total_mm') return `${v.toFixed(1)} mm`;
    if(key==='shortwave_flux_w_m2') return `${Math.round(v)} W/m²`;
    if(key==='aerosol_optical_depth_550nm') return v.toFixed(2);
    if(key==='pm2_5_ug_m3') return v.toFixed(1);
    if(key==='nighttime_lights_radiance_nw_cm2_sr') return `${v.toFixed(v<10?1:0)} nW/(cm²·sr)`;
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
    const usingJma=data===state.jmaData;
    const usingHimawari=data===state.himawariData;
    const usingCams=data===state.camsData;
    const usingViirs=data===state.viirsData;
    $('time-slider').value=state.frameIndex;
    const forecastHour=Number(f.forecast_hour || 0);
    const frameLead=`f${String(forecastHour).padStart(3,'0')}`;
    $('time-label').textContent=usingHimawari
      ? `觀測時間 · ${formatTaipeiTime(f.valid_time_utc)} TST`
      : (usingViirs
        ? `年度合成 · ${f.composite_year || data.provenance?.composite_year || new Date(f.valid_time_utc).getUTCFullYear()}`
        : (usingCams
          ? `CAMS 預報時間 · ${formatTaipeiTime(f.valid_time_utc)} TST`
          : `預報時間 · ${formatTaipeiTime(f.valid_time_utc)} · +${forecastHour}h`));
    $('opacity-label').textContent=`${Math.round(state.weatherOpacity*100)}%`;
    const opacityTitle=$('opacity-title');
    const opacitySlider=$('opacity-slider');
    if(opacityTitle){
      const compactUi=window.matchMedia('(max-width:720px)').matches;
      opacityTitle.textContent=compactUi
        ? (cfg.palette==='cloud'?'雲層透明度':'圖層透明度')
        : (cfg.palette==='cloud'?'雲層顯示強度':'圖層顯示強度');
    }
    if(opacitySlider){
      opacitySlider.title=cfg.palette==='cloud'
        ? '100% 顯示強度仍保留底圖；雲層最高不透明度限制為 78%'
        : '調整圖層顯示強度';
    }

    const status=$('source-state');
    if(state.source==='demo'){
      status.textContent='DEMO 範例資料';
      status.className='source-pill demo';
    }else{
      if(usingHimawari){
        status.textContent='OBS · Himawari-9 2 km';
      }else if(state.modelMode==='auto'){
        status.textContent=usingIcon?'AUTO · ICON Global':'AUTO · GFS';
      }else{
        status.textContent='LIVE · '+modelLabel(state.modelMode);
      }
      status.className='source-pill';
    }

    const interpolationLabel=state.layer==='wind_direction_10m_deg'
      ? '風向採 u/v 向量循環內插'
      : '顯示雙線性內插';
    let resolution;
    if(usingHimawari){
      const p=data.provenance || {};
      resolution=`原生約 ${p.nominal_native_resolution || '2 km at nadir'} · 瀏覽格 ${data.grid.step_degrees || 0.02}° · 觀測更新約 ${p.nominal_cadence_minutes || 10} 分鐘`;
    }else if(usingJma){
      const p=data.provenance || {};
      resolution=`原生約 ${p.native_resolution_km || 5} km · ${p.native_lat_step_degrees || 0.05}°×${p.native_lon_step_degrees || 0.0625}° · 原生時間間隔 ${p.native_time_interval_hours || 1} h`;
    }else if(usingCwa){
      const p=data.provenance || {};
      resolution=`原生約 ${p.native_resolution_km || 3} km · 瀏覽格 ${p.browser_grid_spacing_degrees || 0.03}° · 公開資料間隔 ${p.public_product_interval_hours || 6} h`;
    }else if(usingIcon){
      resolution=`原生約 ${data.provenance?.native_resolution_km || 13} km · 0.125° remap · ${interpolationLabel}`;
    }else if(usingCams){
      const p=data.provenance || {};
      resolution=`CAMS Global 原生約 ${p.native_resolution_km || 45} km · ${p.native_time_interval_hours || 3} h · 0.4° 取樣顯示格`;
    }else if(usingViirs){
      const p=data.provenance || {};
      resolution=`NASA Black Marble · ${p.native_resolution || '15 arc-second'} · 年度夜間燈光合成`;
    }else{
      resolution=`原生 0.25° · ${interpolationLabel}`;
    }
    const cycleText=usingViirs
      ? String(f.composite_year || new Date(f.valid_time_utc).getUTCFullYear())
      : (usingCams
        ? (data.cycle?.retrieved_at_utc || data.cycle?.label || '—')
        : (data.cycle?.cycle_time_utc || data.cycle?.label || '—'));
    const cycleDisplay=Number.isFinite(Date.parse(cycleText))
      ? `${formatTaipeiTime(cycleText)} TST`
      : cycleText;
    const autoPrefix=state.modelMode==='auto'?'自動模式：依圖層選優先模型 · ':'';
    const compactSummary=$('source-mobile-summary');
    if(usingHimawari){
      const age=observationAgeMinutes(data);
      const ageText=Number.isFinite(age) ? ` · 資料年齡 ${Math.round(age)} 分` : '';
      $('cycle-label').textContent=`衛星觀測 ${formatTaipeiTime(f.valid_time_utc)} TST${ageText} · ${data.grid.rows}×${data.grid.cols} · ${resolution}`;
      if(compactSummary){
        const ageCompact=Number.isFinite(age)?` · ${Math.round(age)} 分前`:'';
        compactSummary.textContent=`觀測 ${formatTaipeiTime(f.valid_time_utc)} · 2 km${ageCompact}`;
      }
    }else{
      $('cycle-label').textContent=usingViirs
        ? `年度合成 ${cycleText} · ${data.grid.rows}×${data.grid.cols} · ${resolution}`
        : (usingCams
          ? `資料更新 ${cycleDisplay} · ${data.grid.rows}×${data.grid.cols} · ${resolution}`
          : `${autoPrefix}模型起報 ${cycleDisplay} · ${data.grid.rows}×${data.grid.cols} · ${resolution}`);
      if(compactSummary){
        let compactResolution='0.25°';
        let compactCadence='';
        if(usingJma){
          const p=data.provenance || {};
          compactResolution=`${p.native_resolution_km || 5} km`;
          compactCadence=` · ${p.native_time_interval_hours || 1}h`;
        }else if(usingCwa){
          const p=data.provenance || {};
          compactResolution=`${p.native_resolution_km || 3} km`;
          compactCadence=` · ${p.public_product_interval_hours || 6}h`;
        }else if(usingIcon){
          compactResolution=`約 ${data.provenance?.native_resolution_km || 13} km`;
        }else if(usingCams){
          compactResolution=`約 ${data.provenance?.native_resolution_km || 45} km`;
          compactCadence=` · ${data.provenance?.native_time_interval_hours || 3}h`;
        }else if(usingViirs){
          compactResolution=data.provenance?.native_resolution || '15 arc-second';
        }
        compactSummary.textContent=usingViirs
          ? `年度 ${cycleText} · ${compactResolution}`
          : (usingCams
            ? `更新 ${cycleDisplay.replace(' TST','')} · ${compactResolution}${compactCadence}`
            : `起報 ${cycleDisplay.replace(' TST','')} · ${compactResolution}${compactCadence}`);
      }
    }
    const attributionHost=$('source-attribution');
    if(usingHimawari){
      attributionHost.textContent='衛星觀測：JMA Himawari-9 / AHI · Distribution: NOAA NODD / AWS Open Data';
    }else if(usingJma){
      attributionHost.innerHTML='資料模型：JMA MSM · Open Data transport: <a href="https://registry.opendata.aws/open-meteo/" target="_blank" rel="noopener noreferrer">Open-Meteo AWS</a>';
    }else if(usingCams){
      attributionHost.innerHTML='霧霾資料：Copernicus CAMS Global · API: <a href="https://open-meteo.com/en/docs/air-quality-api" target="_blank" rel="noopener noreferrer">Open-Meteo</a>';
    }else if(usingViirs){
      attributionHost.textContent='夜間燈光：NASA Black Marble VNP46A4 Collection 2 · 衛星輻亮度；QA 0 good / 1 poor / 2 gap-filled；不等同 Bortle 或天空亮度';
    }else{
      attributionHost.innerHTML='';
    }

    const arr=decodedArray(state.layer).filter(Number.isFinite);
    const min=arr.length?Math.min(...arr):null, max=arr.length?Math.max(...arr):null;
    $('layer-summary').textContent=cfg.label;
    $('layer-range').textContent=min==null
      ? '畫面資料範圍：—'
      : `畫面資料範圍：${formatValue(min,state.layer)} – ${formatValue(max,state.layer)}`;
    let providerRole='GFS';
    if(usingHimawari) providerRole='Himawari-9 AHI · 觀測';
    else if(usingJma) providerRole='JMA MSM 5 km';
    else if(usingCwa) providerRole='CWA WRF 3 km';
    else if(usingIcon) providerRole=state.modelMode==='auto'?'ICON Global · auto':'ICON Global';
    else if(usingCams) providerRole=state.layer==='pm2_5_ug_m3'?'CAMS Global · PM2.5':'CAMS Global · AOD 550 nm';
    else if(usingViirs) providerRole='NASA Black Marble VNP46A4 · 年度環境背景';
    else if(state.modelMode==='auto' && cloudLayers.has(state.layer)) providerRole='GFS fallback';
    const unitText=usingHimawari && state.layer==='cloud_top_height_m'
      ? '原始單位 m · 顯示 km'
      : `單位 ${data.fields[state.layer].unit}`;
    $('layer-unit').textContent=usingHimawari
      ? `${providerRole} · ${unitText} · 單張最新觀測`
      : (usingViirs
        ? `${providerRole} · ${unitText} · 靜態年度背景，不隨氣象預報時間軸變化`
        : `${providerRole} · ${unitText} · 各模型保留自己的範圍／解析度／時間軸`);
    const vertical=data.fields[state.layer]?.vertical_definition || null;
    const verticalHost=$('layer-vertical');
    if(usingHimawari && state.layer==='observed_cloud_mask'){
      verticalHost.innerHTML='<div><strong>Himawari-9 — 衛星雲遮罩</strong></div><div>目前衛星觀測：0＝晴空、1＝有雲。這不是預報雲量百分比。</div>';
    }else if(usingHimawari && state.layer==='cloud_top_height_m'){
      verticalHost.innerHTML='<div><strong>Himawari-9 — 雲頂高度</strong></div><div>使用 NOAA L2 雲頂高度與視差校正座標定位；缺值常代表晴空或沒有成功雲頂反演。</div><div>雲頂高度不能證明下方沒有其他雲層，也不等同低／中／高雲量百分比。</div>';
    }else if(vertical){
      const modelName=usingJma?'JMA MSM 5 km':(usingCwa?'CWA WRF 3 km':(usingIcon?'ICON Global':'GFS 0.25°'));
      verticalHost.innerHTML=
        `<div><strong>${escapeHtml(modelName)} — ${escapeHtml(cfg.label)}</strong></div>`+
        `<div>${escapeHtml(vertical.native_definition || "—")}</div>`+
        `<div>${escapeHtml(vertical.approx_height || "")}</div>`;
    }else if(
      usingCwa &&
      data.provenance?.cloud_layer_capability?.native_low_mid_high===false
    ){
      verticalHost.innerHTML='<div>CWA M-A0064 目前未提供原生低／中／高雲量；不以相對濕度代理冒充雲量。</div>';
    }else{
      verticalHost.innerHTML='';
    }

    syncInspectorVisibility();

    const spot=selectedSpot();
    const point=samplingPoint();
    $('spot-name').textContent=spot?spot.name:'尚未選取';
    const sv=samplePointValue(point,state.layer);
    $('spot-value').textContent=point?formatValue(sv,state.layer):'—';
    const sampleMethod=isObservationMode()
      ? '衛星 presentation grid 最近鄰取樣（觀測／反演資料不做雙線性混合）'
      : (usingViirs
        ? '年度夜間燈光顯示可內插；品質旗標以最近原始顯示格判讀'
        : '瀏覽器雙線性插值（風向以 u/v 向量循環插值；超出資料範圍不外推）');
    let viirsQualityHtml='';
    if(usingViirs && point){
      const q=sampleDatasetNearest(
        point,data,'nighttime_lights_quality_flag',f.valid_time_utc
      );
      const qualityLabel=q===0?'good（原始年度合成）'
        :(q===1?'poor（品質較低）'
          :(q===2?'gap-filled（缺口填補）':'未知／缺值'));
      viirsQualityHtml=`<div>VNP46A4 QA：${escapeHtml(qualityLabel)}</div>`;
    }
    $('spot-details').innerHTML=point
      ? `<div>${point.lat.toFixed(4)}°, ${point.lon.toFixed(4)}° · ${escapeHtml(point.label)}</div><div>取樣：${sampleMethod}</div>${viirsQualityHtml}`
      : '<div>可從下拉選單或地圖上的景點點位選取。</div>';
    const environmentHost=$('spot-environment');
    if(environmentHost){
      const environmentHtml=fogHazeDiagnosticHtml(point);
      environmentHost.hidden=!environmentHtml;
      environmentHost.innerHTML=environmentHtml;
    }

    updateLegend(cfg);
    updateTimeline();
    updateCoverageStatus();
    updateQc();
  }
  function updateLegend(cfg){
    const min=cfg.domain[0], max=cfg.domain[1], mid=(min+max)/2;
    let stopValues=[min,min+(max-min)*.25,mid,min+(max-min)*.75,max];
    let labels=[formatValue(min,state.layer),formatValue(mid,state.layer),formatValue(max,state.layer)];
    if(cfg.palette==='cloudMask'){
      stopValues=[0,1];
      labels=['晴空','有雲'];
    }else if(cfg.palette==='direction'){
      stopValues=[0,90,180,270,360];
      labels=['北 0°','東 90°','南 180°','西 270°','北 360°'];
    }else if(cfg.scale==='precip_rate'){
      stopValues=cfg.ticks;
      labels=['0','1','5','20 mm/h'];
    }else if(cfg.scale==='aod'){
      stopValues=cfg.ticks;
      labels=['0.00','0.20','0.80','1.50+'];
    }else if(cfg.scale==='nightlights'){
      stopValues=cfg.ticks;
      labels=['0','1','5','10','50+'];
    }

    let barHtml;
    let labelsHtml;
    let thresholdKey='';
    if(cfg.palette==='cloud'){
      barHtml=`<div class="legend-bar cloud-percent" style="background:linear-gradient(90deg,${cloudLegendGradient()})"><span class="cloud-midline" aria-hidden="true"></span></div>`;
      labelsHtml=`<div class="cloud-legend-labels">${cloudLegendLabels()}</div>`;
      thresholdKey='<div class="cloud-threshold-key"><span class="cloud-threshold-swatch"></span>50% 雲量分界</div>';
    }else{
      const stops=stopValues.map(v=>colorFor(v,cfg));
      const labelHtml=labels.map(v=>`<span>${escapeHtml(v)}</span>`).join('');
      barHtml=`<div class="legend-bar" style="background:linear-gradient(90deg,${stops.join(',')})"></div>`;
      labelsHtml=`<div class="legend-row">${labelHtml}</div>`;
    }

    const windKey=(state.windVectors || isWindLayer()) ? `
      <div class="wind-key"><span class="wind-arrow-icon">→</span> 箭頭＝風去向</div>` : '';
    const coverageKey=state.spotId ? `
      <div class="coverage-key">
        <span><i class="coverage-swatch camera"></i>Camera</span>
        <span><i class="coverage-swatch subject"></i>Subject</span>
        <span><i class="coverage-swatch environment"></i>Environment</span>
      </div>` : '';
    $('legend').innerHTML=`
      <strong>${cfg.label}</strong>
      ${barHtml}
      ${labelsHtml}
      ${thresholdKey}
      <div class="coverage-outline-key">虛線＝目前資料來源範圍</div>
      ${windKey}
      ${coverageKey}`;
  }

  function updateTimeline(){
    const frames=timelineDataset()?.frames || [];
    // Keep the provider-owned timeline contract explicit for existing UI tests.
    const frameLabels=timelineDataset().frames.map(f=>formatTaipeiTime(f.valid_time_utc));
    const last=Math.max(0,frames.length-1);
    const observation=isObservationMode();
    const timeKind=observation?'觀測時間':'預報時間';
    const tickIndices=[0,Math.round(last*.25),Math.round(last*.5),Math.round(last*.75),last]
      .filter((v,i,a)=>a.indexOf(v)===i);
    $('timeline').innerHTML=tickIndices.map(i=>`<span>${escapeHtml(frameLabels[i] || '')}</span>`).join('');
    $('time-prev').disabled=observation || state.frameIndex<=0;
    $('time-next').disabled=observation || state.frameIndex>=last;
    $('time-prev').setAttribute('aria-label',`前一個${timeKind}`);
    $('time-next').setAttribute('aria-label',`下一個${timeKind}`);
    $('time-slider').setAttribute('aria-label',timeKind);
    const play=$('time-play');
    play.disabled=observation || frames.length<2;
    play.textContent=state.timelinePlaying?'暫停':'播放';
    play.setAttribute('aria-pressed',state.timelinePlaying?'true':'false');
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

  function qcMessage(flag){
    const messages={
      visibility_ceiling_dominant:'能見度大量達模型上限，實際遠距能見度可能高於圖示值。',
      constant_field:'此圖層在目前時段幾乎沒有空間差異；可能是合理狀態，仍建議搭配相鄰時段判讀。'
    };
    return messages[flag] || '此圖層有資料品質提示，請搭配相鄰時段與其他模型判讀。';
  }

  function setQcSummary(tone,text){
    const summary=$('qc-summary');
    if(!summary) return;
    summary.className=`qc-summary ${tone}`;
    summary.textContent=`資料品質 · ${text}`;
  }

  function updateQc(){
    const host=$('qc-status');
    if(state.source==='demo'){
      setQcSummary('warn','DEMO');
      host.innerHTML='<div class="warn">⚠️ 目前顯示 DEMO fixture；發布 live WeatherGrid 後會自動採 ICON cloud / GFS fallback。</div>';
      return;
    }
    const qc=activeQc(state.layer);
    if(!qc){
      setQcSummary('warn','QC 未提供');
      host.innerHTML='<div class="warn">△ QC 資料未提供</div>';return;
    }
    if(isObservationMode()){
      setQcSummary('ok','觀測正常');
      const distance=qc.nearest_distance_m?.[state.layer];
      const stats=qc.field_stats?.[state.layer];
      const age=observationAgeMinutes();
      const distanceText=distance
        ? `最近鄰對位 p99 ${(distance.p99_m/1000).toFixed(2)} km · 最大 ${(distance.max_m/1000).toFixed(2)} km`
        : '無對位距離 QC';
      const missingText=stats
        ? `有效 ${stats.count.toLocaleString()} / ${(stats.count+stats.missing).toLocaleString()} 格`
        : '';
      host.innerHTML=
        `<div class="ok">✓ Himawari-9 最新觀測 · ${Number.isFinite(age)?Math.round(age)+' 分鐘前':'時間未知'}</div>`+
        `<div>${escapeHtml(distanceText)}</div>`+
        `<div>${escapeHtml(missingText)}</div>`+
        '<div>雲頂高度缺值可為晴空／無反演，不視為資料錯誤。</div>';
      return;
    }
    const fh=frame().forecast_hour;
    const flags=qc.flags.filter(x=>x.forecast_hour===fh && x.field===state.layer);
    if(!flags.length){
      setQcSummary('ok','資料正常');
      host.innerHTML='<div class="ok">✓ 資料正常</div>';
    }else{
      setQcSummary('warn','需注意');
      host.innerHTML=flags.map(x=>`<div class="warn">⚠ ${escapeHtml(qcMessage(x.flag))}<span class="qc-code" title="內部 QC 代碼">${escapeHtml(x.flag)}</span></div>`).join('');
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
      displayInterpolation: isObservationMode()?'nearest_observation':'bilinear_subcell',
      iconAvailable: Boolean(state.iconData),
      cwaAvailable: Boolean(state.cwaData),
      jmaAvailable: Boolean(state.jmaData),
      himawariAvailable: Boolean(state.himawariData),
      sourceKind: activeDataset(state.layer)?.source_kind || 'forecast',
      observationTime: state.himawariData?.observation?.time_coverage_end || null,
      modelMode: state.modelMode,
      timelineModel: timelineDataset()?.model || null,
      spotPanelVisible: !$('spot-panel').hidden,
      coveragePanelVisible: !$('coverage-panel').hidden,
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
    setQcSummary('warn','載入失敗');
    $('qc-status').innerHTML=`<div class="warn">${escapeHtml(err.message)}</div>`;
  });
})();
