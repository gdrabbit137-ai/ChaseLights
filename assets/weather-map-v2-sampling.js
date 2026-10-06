const EPS=1e-9;
const clampInt=(value,min,max)=>Math.max(min,Math.min(max,Math.round(value)));
const clampNumber=(value,min,max)=>Math.max(min,Math.min(max,Number(value)));

export function normalizeLon(value){
  const lon=Number(value);
  if(!Number.isFinite(lon)) throw new TypeError('longitude must be finite');
  let normalized=((lon+180)%360+360)%360-180;
  if(Object.is(normalized,-0)) normalized=0;
  return normalized;
}

export function longitudeSpan(bbox){
  const west=Number(bbox?.w), east=Number(bbox?.e);
  if(!Number.isFinite(west)||!Number.isFinite(east)) throw new TypeError('bbox longitude must be finite');
  if(Math.abs(east-west)>=360-EPS) return 360;
  const w=normalizeLon(west), e=normalizeLon(east);
  const span=(e-w+360)%360;
  return span< EPS ? 0 : span;
}

export function bboxFromWestSpan(west,span,south,north){
  const width=Math.max(0,Math.min(360,Number(span)));
  if(!Number.isFinite(width)) throw new TypeError('longitude span must be finite');
  const s=Number(south), n=Number(north);
  if(width>=360-EPS) return {w:-180,s,e:180,n};
  const w=normalizeLon(west);
  const end=w+width;
  const e=end<=180+EPS?Math.min(180,end):end-360;
  return {w,s,e,n};
}

export function bboxLongitudeSegments(bbox){
  const span=longitudeSpan(bbox);
  if(span>=360-EPS) return [[-180,180]];
  const w=normalizeLon(bbox.w);
  if(span<=EPS) return [[w,w]];
  const end=w+span;
  if(end<=180+EPS) return [[w,Math.min(180,end)]];
  return [[w,180],[-180,end-360]];
}

export function bboxContains(outer,inner){
  if(!outer||!inner) return false;
  const eps=1e-7;
  if(Number(outer.s)>Number(inner.s)+eps||Number(outer.n)<Number(inner.n)-eps) return false;
  const outerSegments=bboxLongitudeSegments(outer);
  return bboxLongitudeSegments(inner).every(([iw,ie])=>
    outerSegments.some(([ow,oe])=>ow<=iw+eps&&oe>=ie-eps)
  );
}

export function bboxCenterLon(bbox){
  return normalizeLon(Number(bbox.w)+longitudeSpan(bbox)/2);
}

export function expandBBox(bbox,{factor=0.25,minLonPad=0.3,minLatPad=0.25,latMin=-80,latMax=80}={}){
  const span=longitudeSpan(bbox);
  const dx=Math.max(Number(minLonPad)||0,span*(Number(factor)||0));
  const dy=Math.max(Number(minLatPad)||0,(Number(bbox.n)-Number(bbox.s))*(Number(factor)||0));
  const expandedSpan=Math.min(360,span+2*dx);
  const lon=bboxFromWestSpan(Number(bbox.w)-dx,expandedSpan,0,0);
  return {
    w:lon.w,
    s:clampNumber(Number(bbox.s)-dy,latMin,latMax),
    e:lon.e,
    n:clampNumber(Number(bbox.n)+dy,latMin,latMax),
  };
}

function longitudeAt(west,offset){
  const raw=normalizeLon(west)+Number(offset);
  return raw<=180+EPS?Math.min(180,raw):raw-360;
}

export function adaptiveGridShape({width,height,zoom,maxPointsOverride}={}){
  const w=Math.max(320,Number(width)||960);
  const h=Math.max(240,Number(height)||640);
  const z=Number.isFinite(Number(zoom))?Number(zoom):6;
  // Keep continental views legible without exploding browser/API work.
  // The previous 240-point cap produced ~80 px blocks on a 1365 px desktop
  // viewport (the Alaska regression case).  These budgets target roughly
  // 35–45 px fallback cells while preserving a hard upper bound.
  const targetPx=z>=7.5?28:(z>=5?34:42);
  const defaultMaxPoints=z>=7.5?1600:(z>=5?1080:720);
  const requestedCap=Number(maxPointsOverride);
  const maxPoints=Number.isFinite(requestedCap)&&requestedCap>0
    ? Math.min(defaultMaxPoints,clampInt(requestedCap,24,defaultMaxPoints))
    : defaultMaxPoints;
  let cols=clampInt(Math.ceil(w/targetPx)+1,6,64);
  let rows=clampInt(Math.ceil(h/targetPx)+1,5,48);
  while(cols*rows>maxPoints){
    if(cols>=rows&&cols>6) cols-=1;
    else if(rows>5) rows-=1;
    else break;
  }
  return {cols,rows,targetPx,maxPoints};
}

export function sampleGrid(bbox,metrics={}){
  const shape=adaptiveGridShape(metrics);
  const minLonStep=Math.max(0,Number(metrics.minLonStepDeg)||0);
  const minLatStep=Math.max(0,Number(metrics.minLatStepDeg)||0);
  const lonSpan=longitudeSpan(bbox);
  const latSpan=Math.max(0,Number(bbox.n)-Number(bbox.s));
  const maxColsBySource=minLonStep>0?Math.max(2,Math.floor(lonSpan/minLonStep)+1):shape.cols;
  const maxRowsBySource=minLatStep>0?Math.max(2,Math.floor(latSpan/minLatStep)+1):shape.rows;
  const cols=Math.min(shape.cols,maxColsBySource);
  const rows=Math.min(shape.rows,maxRowsBySource);
  const dx=lonSpan/Math.max(1,cols-1);
  const dy=latSpan/Math.max(1,rows-1);
  const points=[];
  for(let r=0;r<rows;r+=1){
    const lat=Number(bbox.s)+dy*r;
    for(let c=0;c<cols;c+=1){
      points.push({lat,lon:longitudeAt(bbox.w,dx*c)});
    }
  }
  return {...shape,cols,rows,points,dx,dy,lonSpan,wrapsAntimeridian:Number(bbox.e)<Number(bbox.w)};
}

export function chunkPoints(points,batchSize=100){
  const size=clampInt(batchSize,1,100);
  const batches=[];
  for(let i=0;i<points.length;i+=size) batches.push(points.slice(i,i+size));
  return batches;
}
