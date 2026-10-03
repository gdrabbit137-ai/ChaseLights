export const V2_INDEX_URL = './weathergrid/v2/index.json';

export async function loadV2Index(fetchImpl = fetch) {
  const r = await fetchImpl(V2_INDEX_URL, { cache: 'no-store' });
  if (!r.ok) throw new Error('V2 index HTTP ' + r.status);
  const data = await r.json();
  if (data.schema_version !== 2 || data.payload_partition !== 'valid_time') {
    throw new Error('unsupported V2 cache index');
  }
  return data;
}

export function tileToSamples(tile) {
  if (tile.schema_version !== 1 || !tile.native_grid) throw new Error('unsupported native tile');
  const {rows,cols,latitudes,longitudes}=tile.grid;
  const expected=rows*cols;
  const fields=Object.entries(tile.values);
  for (const [name,values] of fields) if (values.length!==expected) throw new Error(name+' grid length mismatch');
  const out=[];
  for(let r=0;r<rows;r+=1) for(let c=0;c<cols;c+=1){
    const i=r*cols+c, values={};
    for(const [name,array] of fields) values[name]=array[i];
    out.push({lat:latitudes[r],lon:longitudes[c],values,time:tile.valid_time_utc});
  }
  return out;
}

export async function loadNativeTile(url, fetchImpl = fetch) {
  const r=await fetchImpl(url,{cache:'no-store'});
  if(!r.ok) throw new Error('native tile HTTP '+r.status);
  const tile=await r.json();
  return {tile,samples:tileToSamples(tile)};
}


function intersects(a,b){
  return a.west < b.e && a.east > b.w && a.south < b.n && a.north > b.s;
}

export function cellsForViewport(index, region, viewport, provider='jma'){
  const r=index.regions?.[region];
  if(!r) return [];
  return r.cells.filter((cell)=>cell.providers?.[provider] && intersects(cell.bbox,viewport));
}

export function tileUrl(cell, provider, validTime){
  const spec=cell.providers?.[provider];
  if(!spec?.url_template) throw new Error('provider tile unavailable');
  const token=String(validTime).replace(/[-:]/g,'').replace('.000Z','Z');
  return spec.url_template.replace('{valid_time}',token);
}

export async function loadViewportTiles(index,region,viewport,provider,validTime,fetchImpl=fetch){
  const cells=cellsForViewport(index,region,viewport,provider);
  const settled=await Promise.allSettled(cells.map(async(cell)=>{
    const url=tileUrl(cell,provider,validTime);
    const loaded=await loadNativeTile(url,fetchImpl);
    return {cell,url,...loaded};
  }));
  const loaded=settled.filter(x=>x.status==='fulfilled').map(x=>x.value);
  const failed=settled.filter(x=>x.status==='rejected').map(x=>String(x.reason));
  return {cells,loaded,failed,samples:loaded.flatMap(x=>x.samples)};
}
