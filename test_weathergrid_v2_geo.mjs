import assert from 'node:assert/strict';
import {
  adaptiveGridShape,
  bboxCenterLon,
  bboxContains,
  bboxFromWestSpan,
  bboxLongitudeSegments,
  expandBBox,
  longitudeSpan,
  normalizeLon,
  sampleGrid,
} from './assets/weather-map-v2-sampling.js';

const wrapped={w:178,s:20,e:-178,n:24};
assert.equal(longitudeSpan(wrapped),4);
assert.deepEqual(bboxLongitudeSegments(wrapped),[[178,180],[-180,-178]]);
assert.equal(bboxCenterLon(wrapped),-180);

const expanded=expandBBox(wrapped,{factor:0.25,minLonPad:0.3,minLatPad:0.25,latMin:-80,latMax:80});
assert.equal(longitudeSpan(expanded),6);
assert.equal(expanded.w,177);
assert.equal(expanded.e,-177);
assert.ok(bboxContains(expanded,wrapped));
assert.equal(bboxContains({w:170,s:19,e:-170,n:25},wrapped),true);
assert.equal(bboxContains({w:-170,s:19,e:170,n:25},wrapped),false);

const fromRaw=bboxFromWestSpan(178,4,20,24);
assert.deepEqual(fromRaw,wrapped);
assert.equal(normalizeLon(181),-179);
assert.equal(normalizeLon(-181),179);

const grid=sampleGrid(wrapped,{
  width:900,
  height:600,
  zoom:6,
  minLonStepDeg:0.25,
  minLatStepDeg:0.25,
});
assert.equal(grid.wrapsAntimeridian,true);
assert.ok(grid.lonSpan<10);
assert.ok(grid.dx>0&&grid.dx<1);
assert.ok(grid.points.some((p)=>p.lon>178));
assert.ok(grid.points.some((p)=>p.lon<-178));
assert.ok(grid.points.every((p)=>Math.abs(p.lon)>170));

const ordinary=sampleGrid({w:120,s:20,e:124,n:24},{
  width:900,
  height:600,
  zoom:6,
  minLonStepDeg:0.25,
  minLatStepDeg:0.25,
});
assert.equal(ordinary.wrapsAntimeridian,false);
assert.equal(ordinary.lonSpan,4);
assert.ok(ordinary.points.every((p)=>p.lon>=120&&p.lon<=124));

const alaskaDesktop=adaptiveGridShape({width:1365,height:830,zoom:4});
assert.ok(alaskaDesktop.cols*alaskaDesktop.rows>=650,alaskaDesktop);
assert.ok(alaskaDesktop.cols*alaskaDesktop.rows<=720,alaskaDesktop);
assert.equal(alaskaDesktop.targetPx,42);
assert.equal(alaskaDesktop.maxPoints,720);

const regionalDesktop=adaptiveGridShape({width:1440,height:900,zoom:6});
assert.ok(regionalDesktop.cols*regionalDesktop.rows>=900,regionalDesktop);
assert.ok(regionalDesktop.cols*regionalDesktop.rows<=1080,regionalDesktop);
assert.equal(regionalDesktop.maxPoints,1080);

console.log(JSON.stringify({
  wrappedSpan:grid.lonSpan,
  wrappedCols:grid.cols,
  wrappedRows:grid.rows,
  firstLon:grid.points[0].lon,
  lastLon:grid.points[grid.cols-1].lon,
}));
