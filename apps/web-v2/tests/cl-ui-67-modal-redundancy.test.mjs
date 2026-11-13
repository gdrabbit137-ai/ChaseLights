// CL-UI-67: detail-modal redundant-element removal (owner ruling). The 8-day
// strip (CL-UI-64) is self-explaining, so the place-guide modal must no longer
// render any of these standalone rows:
//   1. top-level overall 「✗ 未符」 warning row,
//   2. per-subject 「✗/✅ 未符·…」 current line (opportunity-current),
//   3. 「⏱ today HH:MM — 未符」 now row (v2-now),
//   4. 「🎯 下一個符合時段」 row (v2-next) — merged into the FIRST qualifying
//      strip cell as an in-cell badge (CL-UI-68: no hover),
//   5. 「即時條件評估」 title row (v2-title) — the strip is the assessment.
// Final modal structure: title → 8-day strip → conditions ×N → viewpoints →
// guide → hourly link.
// The V1 shell has no DOM harness, so this suite combines source assertions
// with an extracted-function run of v2DayStripHtml (same pattern as CL-UI-64).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const grab=(start,end)=>{
  const a=appSource.indexOf(start);
  const b=appSource.indexOf(end,a+1);
  assert.ok(a>=0&&b>a,`source block ${start}…${end} not found`);
  return appSource.slice(a,b);
};

test('CL-UI-67 (1): place-guide modal render path no longer emits the redundant rows',()=>{
  const v2PlaceBlock=grab('function v2PlaceForSpot','async function cleanupOldCaches');
  // v2-now (⏱ now — 未符), v2-next (🎯 next window) and v2-title
  // (即時條件評估) rows are gone from the decorateV2Eval render.
  assert.doesNotMatch(v2PlaceBlock,/v2-now/);
  assert.doesNotMatch(v2PlaceBlock,/v2-next/);
  assert.doesNotMatch(v2PlaceBlock,/v2-title/);
  // The eval block now renders ONLY the strip (self-explaining).
  assert.match(v2PlaceBlock,/el\.innerHTML=`<div class="v2-eval-block">\$\{dayHtml\}<\/div>`;/);
});

test('CL-UI-67 (2): per-subject current verdict line removed from the modal cards',()=>{
  const cardBlock=grab('const renderOpportunityCard=','const selectedCards=');
  assert.doesNotMatch(cardBlock,/opportunity-current/);
  // The removed line was the only consumer of the modal's index-anchored
  // v2day lookup — that lookup is gone with it (CL-DATA-21 stays enforced).
  assert.doesNotMatch(cardBlock,/v2DayForOffset\(v2op,/);
});

test('CL-UI-67 (3): dead CSS for the removed rows is gone',()=>{
  assert.ok(!cssSource.includes('.opportunity-current'));
  assert.ok(!cssSource.includes('.v2-now'));
  assert.ok(!cssSource.includes('.v2-next'));
  assert.ok(!cssSource.includes('.v2-title'));
});

test('CL-UI-67 (4): next window rides INSIDE the first qualifying cell (badge, no hover)',()=>{
  const helperCode=grab('function v2DominantFailMetric','function ensureV2Detail');
  const prelude=`
    const V2_EVAL_METRICS={'zh-TW':{},en:{},ja:{}};
    const V2_FAIL_PRIORITY=[];
    let currentLang='zh-TW';
    let v2SubjectCards={};
    const v2SubjectCardRow=()=>null;
    const v2SubjectCardShortReason=()=>('');
    const v2SubjectCardShorts=()=>[];
    const localDateString=()=>'2026-11-13';
    const selectedDayOffset=()=>0;
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足',v2_next_window:'下一個符合時段：'});
    const listSep=()=>'、';
    const formatHourSegments=list=>(list||[]).join('、');
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
    const v2BestForSpot=null;
  `;
  const fns=new Function(prelude+helperCode+';return {v2DayStripHtml};')();
  const days=[
    {local_date:'2026-11-13',state:'UNFAVORABLE',good_hours:[],conditions:[]},
    {local_date:'2026-11-14',state:'GUIDANCE_SATISFIED',good_hours:['17:00'],conditions:[]},
    {local_date:'2026-11-15',state:'GUIDANCE_SATISFIED',good_hours:['06:00'],conditions:[]},
  ];
  const withNote=fns.v2DayStripHtml(days,['今天','明天','後天'],'Asia/Taipei',{spot_id:'jp-003'},'cloud_sea','jp-003-P01','下一個符合時段：後天 11/15 06:00');
  const cells=withNote.match(/<button[\s\S]*?<\/button>/g)||[];
  assert.equal(cells.length,3);
  // CL-UI-68: the FIRST qualifying cell (明天, idx 1) carries the note as an
  // in-cell badge — no hover/title carrier anywhere in the strip; the earlier
  // 未符 cell does not carry it, and the second qualifying cell doesn't repeat.
  assert.ok(!cells[0].includes('下一個符合時段'),'no badge on the non-qualifying cell');
  assert.ok(cells[1].includes('<span class="v2-strip-next">🎯 下一個符合時段：後天 11/15 06:00</span>'),'badge inside the first qualifying cell');
  assert.ok(!cells[2].includes('下一個符合時段'),'note is not repeated on later qualifying cells');
  assert.ok(!withNote.includes('title='),'no hover title information carrier');
  // aria-label mirrors the in-cell text + badge (screen-reader parity).
  assert.match(withNote,/aria-label="明天 符合時數 1 · 17:00 · 🎯 下一個符合時段：後天 11\/15 06:00"/);
  // In-cell text is present on every cell (CL-UI-68 unified format).
  assert.ok(cells[0].includes('<span class="v2-strip-text">未符</span>'),'unmet cell text present');
  assert.ok(cells[1].includes('<span class="v2-strip-text">符合時數 1 · 17:00</span>'),'met cell text present');

  // No qualifying day in the strip → nothing to attach the note to; the strip
  // stays clean (the note is omitted together with the row).
  const badDays=days.map(day=>({...day,state:'UNFAVORABLE',good_hours:[]}));
  const noNote=fns.v2DayStripHtml(badDays,['今天','明天','後天'],'Asia/Taipei',{spot_id:'jp-003'},'cloud_sea','jp-003-P01','下一個符合時段：後天 11/15 06:00');
  assert.ok(!noNote.includes('下一個符合時段'));

  // Empty nextNote (no still-future window): titles unchanged, no note.
  const plain=fns.v2DayStripHtml(days,['今天','明天','後天'],'Asia/Taipei',{spot_id:'jp-003'},'cloud_sea','jp-003-P01','');
  assert.ok(!plain.includes('下一個符合時段'));
});

test('CL-UI-67 (5): cache-bust stamp bumped for the edited app.js/app.css',()=>{
  const index=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
  assert.match(index,/assets\/app\.js\?v=clui75/);
  assert.match(index,/assets\/app\.css\?v=clui75/);
});
