const clampInt=(value,min,max)=>Math.max(min,Math.min(max,Math.round(value)));

export function adaptiveGridShape({width,height,zoom}={}){
  const w=Math.max(320,Number(width)||960);
  const h=Math.max(240,Number(height)||640);
  const z=Number.isFinite(Number(zoom))?Number(zoom):6;
  const targetPx=z>=7.5?34:(z>=5?42:64);
  const maxPoints=z>=7.5?1200:(z>=5?800:320);
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
  const dx=(bbox.e-bbox.w)/Math.max(1,shape.cols-1);
  const dy=(bbox.n-bbox.s)/Math.max(1,shape.rows-1);
  const points=[];
  for(let r=0;r<shape.rows;r+=1){
    const lat=bbox.s+dy*r;
    for(let c=0;c<shape.cols;c+=1){
      points.push({lat,lon:bbox.w+dx*c});
    }
  }
  return {...shape,points,dx,dy};
}

export function chunkPoints(points,batchSize=80){
  const size=clampInt(batchSize,1,100);
  const batches=[];
  for(let i=0;i<points.length;i+=size) batches.push(points.slice(i,i+size));
  return batches;
}
