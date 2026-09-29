(() => {
  const LIVE_DATA = './weathergrid/gfs_tw_weather_browser.json';
  const LIVE_QC = './weathergrid/gfs_tw_weather_qc.json';
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
    wind_direction_10m_deg:{label:'10 m 風向', unit:'°', domain:[0,360], palette:'direction'}
  };

  const state = {
    data:null,
    qc:null,
    coverage:{spots:[]},
    frameIndex:0,
    layer:'low_cloud_percent',
    spotId:'',
    opportunityId:'',
    view:null,
    weatherOpacity:0.62,
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

  function initControls(){
    const layerSelect = $('layer-select');
    layerSelect.innerHTML = Object.entries(layerConfig)
      .filter(([key]) => state.data.fields[key])
      .map(([key,cfg]) => `<option value="${key}">${cfg.label}</option>`).join('');
    layerSelect.value = state.layer;
    layerSelect.addEventListener('change', () => {
      state.layer = layerSelect.value;
      renderAll();
    });

    const opacitySlider=$('opacity-slider');
    opacitySlider.value=Math.round(state.weatherOpacity*100);
    opacitySlider.addEventListener('input',()=>{
      state.weatherOpacity=Number(opacitySlider.value)/100;
      renderAll();
    });

    const slider = $('time-slider');
    slider.max = Math.max(0, state.data.frames.length - 1);
    slider.value = state.frameIndex;
    slider.addEventListener('input', () => {
      state.frameIndex = Number(slider.value);
      renderAll();
    });

    const spotSelect = $('spot-select');
    spotSelect.innerHTML = '<option value="">全部景點</option>' +
      state.data.spots.map(s =>
        `<option value="${escapeHtml(s.spot_id)}">${escapeHtml(s.name)}</option>`
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
      setViewBbox(state.data.bbox,{animate:true,maxZoom:8});
      renderAll();
    });

    canvas.addEventListener('click', ev => {
      if(state.mapReady) return;
      const rect=canvas.getBoundingClientRect();
      pickSpotAtPoint(ev.clientX-rect.left,ev.clientY-rect.top);
    });
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
      state.view = {...state.data.bbox};
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

  function providerCoversBbox(bbox){
    if(!bbox || bbox.wraps_antimeridian) return false;
    const b=state.data.bbox;
    return bbox.west >= b.leftlon && bbox.east <= b.rightlon &&
      bbox.south >= b.bottomlat && bbox.north <= b.toplat;
  }

  function frame(){ return state.data.frames[state.frameIndex]; }

  function decodeValue(key, encoded){
    if(encoded == null) return null;
    const meta = state.data.fields[key];
    let value = encoded * meta.scale;
    if(meta.wrap) value = ((value % meta.wrap) + meta.wrap) % meta.wrap;
    return value;
  }

  function decodedArray(key){
    return frame().values[key].map(v => decodeValue(key,v));
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
    return `hsl(${(value%360+360)%360} 76% 52%)`;
  }

  function draw(){
    const data=state.data;
    const cfg=layerConfig[state.layer];
    const vals=decodedArray(state.layer);
    const rows=data.grid.rows, cols=data.grid.cols;
    const lats=data.grid.latitudes, lons=data.grid.longitudes;
    const size=syncCanvasSize();
    const visibleView=renderViewBbox();

    ctx.clearRect(0,0,size.width,size.height);
    if(!state.mapReady){
      ctx.fillStyle='#07101f';
      ctx.fillRect(0,0,size.width,size.height);
    }

    const lonStep=cols>1 ? Math.abs(lons[1]-lons[0]) : .25;
    const latStep=rows>1 ? Math.abs(lats[1]-lats[0]) : .25;

    ctx.save();
    for(let r=0;r<rows;r++){
      for(let c=0;c<cols;c++){
        const lon=lons[c], lat=lats[r];
        const left=lon-lonStep/2, right=lon+lonStep/2;
        const top=lat+latStep/2, bottom=lat-latStep/2;
        if(right < visibleView.leftlon || left > visibleView.rightlon ||
           top < visibleView.bottomlat || bottom > visibleView.toplat) continue;
        const points=[
          project(left,top),project(right,top),
          project(right,bottom),project(left,bottom)
        ];
        ctx.beginPath();
        points.forEach((p,i)=>i===0?ctx.moveTo(p.x,p.y):ctx.lineTo(p.x,p.y));
        ctx.closePath();
        const value=vals[r*cols+c];
        ctx.globalAlpha=state.weatherOpacity*cellOpacityFor(value,cfg);
        ctx.fillStyle=colorFor(value,cfg);
        ctx.fill();
      }
    }
    ctx.restore();

    if(!state.mapReady) drawGrid();
    drawCoverage();
    drawSpots();
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

  function nearestCellIndex(lon,lat){
    const lons=state.data.grid.longitudes, lats=state.data.grid.latitudes;
    let ci=0,ri=0,cd=Infinity,rd=Infinity;
    lons.forEach((v,i)=>{const d=Math.abs(v-lon);if(d<cd){cd=d;ci=i;}});
    lats.forEach((v,i)=>{const d=Math.abs(v-lat);if(d<rd){rd=d;ri=i;}});
    return ri*state.data.grid.cols+ci;
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
    const values=decodedArray(key);
    if(key==='wind_direction_10m_deg') return values[nearestCellIndex(point.lon,point.lat)];

    const lons=state.data.grid.longitudes, lats=state.data.grid.latitudes;
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
    const v00=values[toOrigY(y0i)*state.data.grid.cols+toOrigX(x0i)];
    const v10=values[toOrigY(y0i)*state.data.grid.cols+toOrigX(x1i)];
    const v01=values[toOrigY(y1i)*state.data.grid.cols+toOrigX(x0i)];
    const v11=values[toOrigY(y1i)*state.data.grid.cols+toOrigX(x1i)];
    if([v00,v10,v01,v11].some(v=>v==null)) return values[nearestCellIndex(point.lon,point.lat)];
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
    $('time-slider').value=state.frameIndex;
    $('time-label').textContent=`時間 · ${formatTaipeiTime(f.valid_time_utc)} (f${String(f.forecast_hour).padStart(3,'0')})`;
    $('opacity-label').textContent=`${Math.round(state.weatherOpacity*100)}%`;

    const status=$('source-state');
    if(state.source==='demo'){
      status.textContent='DEMO 範例資料';
      status.className='source-pill demo';
    }else{
      status.textContent='LIVE GFS 快照';
      status.className='source-pill';
    }
    $('cycle-label').textContent=`Cycle ${state.data.cycle?.cycle_time_utc || '—'} · ${state.data.grid.rows}×${state.data.grid.cols}`;

    const arr=decodedArray(state.layer).filter(Number.isFinite);
    const min=arr.length?Math.min(...arr):null, max=arr.length?Math.max(...arr):null;
    $('layer-summary').textContent=min==null?'—':`${formatValue(min,state.layer)} – ${formatValue(max,state.layer)}`;
    $('layer-unit').textContent=`${cfg.label} · ${state.data.fields[state.layer].unit} · 底圖可見度依數值動態調整`;

    const spot=selectedSpot();
    const point=samplingPoint();
    $('spot-name').textContent=spot?spot.name:'尚未選取';
    const sv=samplePointValue(point,state.layer);
    $('spot-value').textContent=point?formatValue(sv,state.layer):'—';
    $('spot-details').innerHTML=point
      ? `<div>${point.lat.toFixed(4)}°, ${point.lon.toFixed(4)}° · ${escapeHtml(point.label)}</div><div>取樣：瀏覽器雙線性插值（風向使用最近格點）</div>`
      : '<div>可從下拉選單或地圖上的景點點位選取。</div>';

    updateLegend(cfg);
    updateTimeline();
    updateCoverageStatus();
    updateQc();
  }

  function updateLegend(cfg){
    const min=cfg.domain[0], max=cfg.domain[1], mid=(min+max)/2;
    const stops=[0,.25,.5,.75,1].map(t=>colorFor(min+(max-min)*t,cfg));
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
      ${coverageKey}`;
  }

  function updateTimeline(){
    $('timeline').innerHTML=state.data.frames.map((f,i)=>
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
      host.innerHTML='<div class="warn">⚠️ 目前顯示 DEMO fixture；執行 B117 publish_preview 後會切換為 GFS live snapshot。</div>';
      return;
    }
    if(!state.qc){
      host.innerHTML='<div>此快照沒有 QC 檔。</div>';return;
    }
    const fh=frame().forecast_hour;
    const flags=state.qc.flags.filter(x=>x.forecast_hour===fh && x.field===state.layer);
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
