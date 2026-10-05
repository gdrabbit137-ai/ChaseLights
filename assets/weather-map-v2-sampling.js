const clampInt=(value,min,max)=>Math.max(min,Math.min(max,Math.round(value)));

export function adaptiveGridShape({width,height,zoom}={}){
  const w=Math.max(320,Number(width)||960);
  const h=Math.max(240,Number(height)||640);
  const z=Number.isFinite(Number(zoom))?Number(zoom):6;
  const targetPx=z>=7.5?42:(z>=5?58:72);
  const maxPoints=z>=7.5?640:(z>=5?420:240);
  let cols=clampInt(Math.ceil(w/targetPx)+1,6,48);
  let rows=clampInt(Math.ceil(h/targetPx)+1,5,36);
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
  const maxColsBySource=minLonStep>0?Math.max(2,Math.floor((bbox.e-bbox.w)/minLonStep)+1):shape.cols;
  const maxRowsBySource=minLatStep>0?Math.max(2,Math.floor((bbox.n-bbox.s)/minLatStep)+1):shape.rows;
  const cols=Math.min(shape.cols,maxColsBySource);
  const rows=Math.min(shape.rows,maxRowsBySource);
  const dx=(bbox.e-bbox.w)/Math.max(1,cols-1);
  const dy=(bbox.n-bbox.s)/Math.max(1,rows-1);
  const points=[];
  for(let r=0;r<rows;r+=1){
    const lat=bbox.s+dy*r;
    for(let c=0;c<cols;c+=1){
      points.push({lat,lon:bbox.w+dx*c});
    }
  }
  return {...shape,cols,rows,points,dx,dy};
}

export function chunkPoints(points,batchSize=100){
  const size=clampInt(batchSize,1,100);
  const batches=[];
  for(let i=0;i<points.length;i+=size) batches.push(points.slice(i,i+size));
  return batches;
}
