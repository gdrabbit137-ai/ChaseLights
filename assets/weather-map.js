(() => {
  const LIVE_DATA = './weathergrid/gfs_tw_weather_browser.json';
  const LIVE_QC = './weathergrid/gfs_tw_weather_qc.json';
  const FALLBACK_DATA = './weathergrid_sample.json';

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
    data:null,qc:null,frameIndex:0,layer:'low_cloud_percent',spotId:'',
    view:null,source:'loading'
  };

  const $ = id => document.getElementById(id);
  const canvas = $('weather-canvas');
  const ctx = canvas.getContext('2d');

  function escapeHtml(v){
    return String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
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
    state.view = {...state.data.bbox};
    initControls();
    renderAll();
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

    const slider = $('time-slider');
    slider.max = Math.max(0, state.data.frames.length - 1);
    slider.value = state.frameIndex;
    slider.addEventListener('input', () => {
      state.frameIndex = Number(slider.value);
      renderAll();
    });

    const spotSelect = $('spot-select');
    spotSelect.innerHTML = '<option value="">全部景點</option>' +
      state.data.spots.map(s => `<option value="${escapeHtml(s.spot_id)}">${escapeHtml(s.name)}</option>`).join('');
    spotSelect.addEventListener('change', () => {
      state.spotId = spotSelect.value;
      if(state.spotId) zoomToSpot(selectedSpot());
      else state.view = {...state.data.bbox};
      renderAll();
    });

    $('reset-view').addEventListener('click', () => {
      state.view = {...state.data.bbox};
      renderAll();
    });

    canvas.addEventListener('click', ev => {
      const rect = canvas.getBoundingClientRect();
      const px = (ev.clientX - rect.left) * canvas.width / rect.width;
      const py = (ev.clientY - rect.top) * canvas.height / rect.height;
      let best = null;
      for(const spot of state.data.spots){
        const p = project(spot.lon, spot.lat);
        const d = Math.hypot(p.x - px, p.y - py);
        if(!best || d < best.d) best = {spot,d};
      }
      if(best && best.d < 26){
        state.spotId = best.spot.spot_id;
        $('spot-select').value = state.spotId;
        zoomToSpot(best.spot);
        renderAll();
      }
    });
  }

  function selectedSpot(){
    return state.data.spots.find(s => s.spot_id === state.spotId) || null;
  }

  function zoomToSpot(spot){
    if(!spot) return;
    const lonHalf = 0.85;
    const latHalf = 0.65;
    state.view = {
      leftlon:Math.max(state.data.bbox.leftlon, spot.lon-lonHalf),
      rightlon:Math.min(state.data.bbox.rightlon, spot.lon+lonHalf),
      bottomlat:Math.max(state.data.bbox.bottomlat, spot.lat-latHalf),
      toplat:Math.min(state.data.bbox.toplat, spot.lat+latHalf)
    };
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
    const v = state.view;
    return {
      x:(lon-v.leftlon)/(v.rightlon-v.leftlon)*canvas.width,
      y:(v.toplat-lat)/(v.toplat-v.bottomlat)*canvas.height
    };
  }

  function colorFor(value,cfg){
    if(value == null || !Number.isFinite(value)) return 'rgba(30,41,59,.35)';
    let t = (value-cfg.domain[0])/(cfg.domain[1]-cfg.domain[0]);
    t = Math.max(0,Math.min(1,t));
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
    const data = state.data;
    const cfg = layerConfig[state.layer];
    const vals = decodedArray(state.layer);
    const rows = data.grid.rows, cols = data.grid.cols;
    const lats = data.grid.latitudes, lons = data.grid.longitudes;

    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle='#07101f';
    ctx.fillRect(0,0,canvas.width,canvas.height);

    const lonStep = cols>1 ? Math.abs(lons[1]-lons[0]) : .25;
    const latStep = rows>1 ? Math.abs(lats[1]-lats[0]) : .25;

    for(let r=0;r<rows;r++){
      for(let c=0;c<cols;c++){
        const lon=lons[c], lat=lats[r];
        const left=lon-lonStep/2, right=lon+lonStep/2;
        const top=lat+latStep/2, bottom=lat-latStep/2;
        if(right < state.view.leftlon || left > state.view.rightlon ||
           top < state.view.bottomlat || bottom > state.view.toplat) continue;
        const p1=project(left,top), p2=project(right,bottom);
        ctx.fillStyle=colorFor(vals[r*cols+c],cfg);
        ctx.fillRect(p1.x,p1.y,p2.x-p1.x+1,p2.y-p1.y+1);
      }
    }

    drawGrid();
    drawSpots();
  }

  function drawGrid(){
    const v=state.view;
    ctx.save();
    ctx.strokeStyle='rgba(226,232,240,.18)';
    ctx.fillStyle='rgba(226,232,240,.72)';
    ctx.font='18px -apple-system, sans-serif';
    ctx.lineWidth=1;
    const lonStart=Math.ceil(v.leftlon);
    for(let lon=lonStart;lon<=v.rightlon;lon++){
      const p=project(lon,v.bottomlat);
      ctx.beginPath();ctx.moveTo(p.x,0);ctx.lineTo(p.x,canvas.height);ctx.stroke();
      ctx.fillText(`${lon}°E`,p.x+4,22);
    }
    const latStart=Math.ceil(v.bottomlat);
    for(let lat=latStart;lat<=v.toplat;lat++){
      const p=project(v.leftlon,lat);
      ctx.beginPath();ctx.moveTo(0,p.y);ctx.lineTo(canvas.width,p.y);ctx.stroke();
      ctx.fillText(`${lat}°N`,6,p.y-5);
    }
    ctx.restore();
  }

  function drawSpots(){
    const selected=selectedSpot();
    ctx.save();
    for(const s of state.data.spots){
      const p=project(s.lon,s.lat);
      if(p.x<0||p.x>canvas.width||p.y<0||p.y>canvas.height) continue;
      ctx.beginPath();
      ctx.arc(p.x,p.y,s.spot_id===state.spotId?9:4,0,Math.PI*2);
      ctx.fillStyle=s.spot_id===state.spotId?'#fbbf24':'#f8fafc';
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

  function sampleSpotValue(spot,key){
    if(!spot) return null;
    const values=decodedArray(key);
    if(key==='wind_direction_10m_deg') return values[nearestCellIndex(spot.lon,spot.lat)];

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
    const [x0i,x1i]=bracket(lonA,spot.lon), [y0i,y1i]=bracket(latA,spot.lat);
    const toOrigX=i=>ascLon?i:lons.length-1-i;
    const toOrigY=i=>ascLat?i:lats.length-1-i;
    const x0=lonA[x0i],x1=lonA[x1i],y0=latA[y0i],y1=latA[y1i];
    const v00=values[toOrigY(y0i)*state.data.grid.cols+toOrigX(x0i)];
    const v10=values[toOrigY(y0i)*state.data.grid.cols+toOrigX(x1i)];
    const v01=values[toOrigY(y1i)*state.data.grid.cols+toOrigX(x0i)];
    const v11=values[toOrigY(y1i)*state.data.grid.cols+toOrigX(x1i)];
    if([v00,v10,v01,v11].some(v=>v==null)) return values[nearestCellIndex(spot.lon,spot.lat)];
    const wx=x1===x0?0:(spot.lon-x0)/(x1-x0);
    const wy=y1===y0?0:(spot.lat-y0)/(y1-y0);
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
    $('layer-unit').textContent=`${cfg.label} · ${state.data.fields[state.layer].unit}`;

    const spot=selectedSpot();
    $('spot-name').textContent=spot?spot.name:'尚未選取';
    const sv=sampleSpotValue(spot,state.layer);
    $('spot-value').textContent=spot?formatValue(sv,state.layer):'—';
    $('spot-details').innerHTML=spot
      ? `<div>${spot.lat.toFixed(4)}°, ${spot.lon.toFixed(4)}°</div><div>取樣：瀏覽器雙線性插值（風向使用最近格點）</div>`
      : '<div>可從下拉選單或地圖上的景點點位選取。</div>';

    updateLegend(cfg);
    updateTimeline();
    updateQc();
  }

  function updateLegend(cfg){
    const min=cfg.domain[0], max=cfg.domain[1], mid=(min+max)/2;
    const stops=[0,.25,.5,.75,1].map(t=>colorFor(min+(max-min)*t,cfg));
    $('legend').innerHTML=`
      <strong>${cfg.label}</strong>
      <div class="legend-bar" style="background:linear-gradient(90deg,${stops.join(',')})"></div>
      <div class="legend-row"><span>${formatValue(min,state.layer)}</span><span>${formatValue(mid,state.layer)}</span><span>${formatValue(max,state.layer)}</span></div>`;
  }

  function updateTimeline(){
    $('timeline').innerHTML=state.data.frames.map((f,i)=>
      `<button type="button" data-i="${i}" class="${i===state.frameIndex?'active':''}">${formatTaipeiTime(f.valid_time_utc)}</button>`
    ).join('');
    $('timeline').querySelectorAll('button').forEach(b=>b.onclick=()=>{
      state.frameIndex=Number(b.dataset.i);renderAll();
    });
  }

  function updateQc(){
    const host=$('qc-status');
    if(state.source==='demo'){
      host.innerHTML='<div class="warn">⚠️ 目前顯示 DEMO fixture；執行 B119 publish workflow 後會自動載入最新 GFS 快照。</div>';
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
  }

  window.addEventListener('resize', renderAll);
  load().catch(err=>{
    console.error(err);
    $('source-state').textContent='載入失敗';
    $('source-state').className='source-pill error';
    $('qc-status').innerHTML=`<div class="warn">${escapeHtml(err.message)}</div>`;
  });
})();
