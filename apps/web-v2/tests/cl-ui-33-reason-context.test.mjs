// CL-UI-33: context-aware fail-reason copy (mountain vs flat waterfront),
// reflection wind variant, and zero missing-reason paths on cards that show
// 「本日無符合題材」 while a known failure exists.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const grab=(start,end)=>{const i=appSource.indexOf(start);return appSource.slice(i,appSource.indexOf(end,i));};
const failCode=grab('const V2_FAIL_PRIORITY','// CL-UI-12: day0 (today) qualifying hours');
// makeFns injects a stub v2PlaceForSpot (real one lives further down app.js).
const makeFns=(lang,placeForSpot='()=>null')=>new Function(`let currentLang=${JSON.stringify(lang)};\n${failCode}\nconst v2PlaceForSpot=${placeForSpot};\nreturn {v2DominantFailReason,v2FailReasonSuffix,v2FailReasonContext,v2FailReasonText};`)();

const lowCloudDay={state:'UNFAVORABLE',conditions:[{metric:'cloud_cover_low',day_verdict:'FAIL'}]};
const windDay={state:'UNFAVORABLE',conditions:[{metric:'wind_speed_10m',day_verdict:'FAIL'}]};

test('CL-UI-33 (1): same metric, different copy — mountain card vs harbor card',()=>{
  for(const lang of ['zh-TW','en','ja']){
    const fns=makeFns(lang);
    const mountain=fns.v2DominantFailReason(lowCloudDay.conditions,{scenes:['mountain']},'sunset');
    const flat=fns.v2DominantFailReason(lowCloudDay.conditions,{scenes:['coast']},'sunset');
    assert.notEqual(mountain,flat);
    // A mountain-context genre alone flips the copy (no scene needed).
    assert.equal(fns.v2DominantFailReason(lowCloudDay.conditions,null,'mountain_view'),mountain);
    assert.equal(fns.v2DominantFailReason(lowCloudDay.conditions,null,'cloud_sea'),mountain);
    assert.equal(fns.v2DominantFailReason(lowCloudDay.conditions,null,'overlook'),mountain);
    // Flat context (harbor/city/coast): neutral view-blocked wording.
    assert.equal(fns.v2DominantFailReason(lowCloudDay.conditions,null,''),flat);
    assert.equal(fns.v2DominantFailReason(lowCloudDay.conditions,null,'reflection'),flat);
  }
  const zh=makeFns('zh-TW');
  assert.equal(zh.v2DominantFailReason(lowCloudDay.conditions,{scenes:['mountain']},'sunset'),'低雲太厚，山頭沒入雲中');
  assert.equal(zh.v2DominantFailReason(lowCloudDay.conditions,{scenes:['coast']},'sunset'),'低雲太厚，遮蔽景觀');
  const en=makeFns('en');
  assert.equal(en.v2DominantFailReason(lowCloudDay.conditions,{scenes:['coast']},'sunset'),'Thick low cloud blocks the view');
  assert.equal(en.v2DominantFailReason(lowCloudDay.conditions,{scenes:['mountain']},'sunset'),'Low cloud swallows the peak');
  const ja=makeFns('ja');
  assert.equal(ja.v2DominantFailReason(lowCloudDay.conditions,{scenes:['coast']},'sunset'),'低層雲が厚く、景観が遮られます');
  assert.equal(/(题|视|湿|风)/.test(ja.v2DominantFailReason(lowCloudDay.conditions,{scenes:['coast']},'sunset')),false);
});

test('CL-UI-33 (2): wind on a reflection subject names the still water, not camera shake',()=>{
  const zh=makeFns('zh-TW');
  assert.equal(zh.v2DominantFailReason(windDay.conditions,null,'reflection'),'風太大，水面不平');
  // Non-reflection contexts keep the camera-shake wording.
  assert.equal(zh.v2DominantFailReason(windDay.conditions,null,'sunset'),'風太大，畫面容易晃');
  const en=makeFns('en');
  assert.equal(en.v2DominantFailReason(windDay.conditions,null,'reflection'),'Too windy — the water surface is not still');
  const ja=makeFns('ja');
  assert.equal(ja.v2DominantFailReason(windDay.conditions,null,'reflection'),'風が強すぎて、水面が揺れています');
  assert.equal(/(题|视|湿|风)/.test(ja.v2DominantFailReason(windDay.conditions,null,'reflection')),false);
});

test('CL-UI-33 (3): no-reason paths — every known failure resolves to a reason',()=>{
  const zh=makeFns('zh-TW');
  // Context map keys exist in all three languages with the same structure.
  const keySets=['zh-TW','en','ja'].map(lang=>{
    const src=grab('const V2_FAIL_PRIORITY','// CL-UI-12: day0 (today) qualifying hours');
    return new Function(`let currentLang='${lang}';\n${src}\nreturn Object.entries(V2_FAIL_REASON_CONTEXT).map(([m,v])=>m+':'+Object.keys(v).sort().join('+')).sort().join(',');`)();
  });
  assert.equal(keySets[0],keySets[1]);
  assert.equal(keySets[0],keySets[2]);
  // A best day with NO known fail falls back to a sibling opportunity on the
  // same local date — the card never shows 「本日無符合題材」 silently while
  // a known failure exists elsewhere in the same place/day.
  const sibling={
    'tw-003':{place_id:'tw-003',opportunities:[
      {opportunity_id:'tw-003-P02',genre_template:'sunset',days:[{local_date:'2026-11-05',conditions:[{metric:'cloud_cover_low',day_verdict:'UNKNOWN'}]}]},
      {opportunity_id:'tw-003-P03',genre_template:'reflection',days:[{local_date:'2026-11-05',conditions:[{metric:'wind_speed_10m',day_verdict:'FAIL'}]}]}]}};
  const placeStub=`(spot)=>(${JSON.stringify(sibling)}[spot.spot_id]||null)`;
  const fns=makeFns('zh-TW',placeStub);
  const best={state:'NOT_EVALUABLE',day:{local_date:'2026-11-05',conditions:[{metric:'cloud_cover_low',day_verdict:'UNKNOWN'}]}};
  const spot={spot_id:'tw-003',scenes:['coast']};
  assert.equal(fns.v2FailReasonSuffix(best,spot),' · 風太大，水面不平');
  // No sibling knowledge at all → honest silence stays (資料不足).
  assert.equal(fns.v2FailReasonSuffix(best,{spot_id:'tw-999',scenes:[]}),'');
});

test('CL-UI-33 (4): mechanical mapping only — no per-card hand copy',()=>{
  // The context decision is a genre/scene lookup, not a spot-name switch.
  assert.match(appSource,/V2_MOUNTAIN_GENRES=\['mountain_view','cloud_sea','overlook'\]/);
  assert.match(appSource,/includes\('mountain'\)/);
  // The i18n cache-bust stamp rides the same commit.
  const index=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
  assert.match(index,/assets\/app\.js\?v=clui39/);
  assert.match(index,/assets\/app\.css\?v=clui39/);
});