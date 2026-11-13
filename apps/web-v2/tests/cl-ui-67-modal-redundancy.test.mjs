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

test('CL-UI-67 (4): compact strip cells — no 🎯 next-window badge anywhere (CL-UI-75 owner ruling)',()=>{
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
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足'});
    const listSep=()=>'、';
    const formatHourSegments=list=>(list||[]).length>1?list[0]+'–'+list[list.length-1]:(list||[]).join('、');
    const compactHourSegmentsText=text=>String(text||'').split('、').map(seg=>seg.includes('–')?seg.replace(/:00/g,''):seg).join('、');
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
    const v2BestForSpot=null;
  `;
  const fns=new Function(prelude+helperCode+';return {v2DayStripHtml};')();
  const days=[
    {local_date:'2026-11-13',state:'UNFAVORABLE',good_hours:[],conditions:[]},
    {local_date:'2026-11-14',state:'GUIDANCE_SATISFIED',good_hours:['17:00'],conditions:[]},
    {local_date:'2026-11-15',state:'GUIDANCE_SATISFIED',good_hours:['06:00','07:00','08:00'],conditions:[]},
  ];
  // CL-UI-75: the strip no longer takes a next-note at all — a caller that
  // still passes one gets the identical compact strip (no 🎯 anywhere).
  const html=fns.v2DayStripHtml(days,['今天','明天','後天'],'Asia/Taipei',{spot_id:'jp-003'},'cloud_sea','jp-003-P01');
  const cells=html.match(/<button[\s\S]*?<\/button>/g)||[];
  assert.equal(cells.length,3);
  assert.ok(!html.includes('下一個符合時段') && !html.includes('🎯'),
    'the next-window badge is retired at every breakpoint');
  assert.ok(!html.includes('v2-strip-next'),'no badge span anywhere in the strip');
  assert.ok(!html.includes('title='),'no hover title information carrier');
  // aria-label keeps the FULL qualifying-hours wording (screen-reader parity).
  assert.match(html,/aria-label="明天 符合時數 1 · 17:00"/);
  // In-cell text is compact: met = ✓n hours badge + abbreviated window;
  // unmet = ✗short-reason; a lone whole-hour stamp keeps 17:00, a range
  // compresses to 06–08.
  assert.ok(cells[1].includes('<span class="v2-strip-hours">✓1</span>'),'hours badge, not a sentence');
  assert.ok(cells[1].includes('<span class="v2-strip-text">17:00</span>'),'lone stamp keeps its full form');
  assert.ok(cells[2].includes('<span class="v2-strip-hours">✓3</span>'),'hours badge on the second met cell');
  assert.ok(cells[2].includes('<span class="v2-strip-text">06–08</span>'),'range window abbreviated 06:00–08:00 → 06–08');
  assert.ok(cells[0].includes('<span class="v2-strip-text">未符</span>'),'unmet cell text present');
  assert.ok(!cells[0].includes('✗'),'no reason word on the stub — the plain label stays');
});

test('CL-UI-67 (5): cache-bust stamp bumped for the edited app.js/app.css',()=>{
  const index=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
  assert.match(index,/assets\/app\.js\?v=clui78/);
  assert.match(index,/assets\/app\.css\?v=clui78/);
});
