// CL-UI-46 (owner-reported defects, presentation only):
//   (1) the spot card printed the sun angle TWICE — the top row's ☀ pill and a
//       second, lower meta line 「☀️ 247° / 0°」. The lower duplicate is gone;
//       everything the top row does NOT carry (moon %, galactic core, Kp) is
//       still rendered, and the modal's hourly cells keep the full text.
//   (2) the 不限來源/官方/私人 source-filter row is hidden while the member owns
//       no private place, and the place count is printed ONCE on the first
//       screen (the list header) instead of three times.
// Extracted-function tests over the shipped assets/app.js + source contracts,
// same approach as CL-UI-44/45 (the V1 shell has no DOM harness of its own).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const indexSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

const factory=new Function([
  grab('function astroText','// CL-UI-14: timezone labels'),
  'return {astroText,cardAstroText,darkSkyText};'
].join('\n'));
const {astroText,cardAstroText}=factory();

const HOUR={sun_azimuth:247.4,sun_elevation:0.3,moon_illumination:11.7,galactic_core_azimuth:80.1,galactic_core_elevation:-54.2,kp:5};

// ---------------------------------------------------------------- (1) angles

test('CL-UI-46 (1a): the modal keeps the full astronomy text — astroText is untouched',()=>{
  // CL-UI-44's contract still holds verbatim (the hourly kv row has no top pill
  // to duplicate, so it must keep printing the solar geometry).
  assert.equal(astroText({...HOUR},'mountain_view'),'☀️ 247° / 0°');
  assert.equal(astroText({...HOUR},'milky_way'),'☀️ 247° / 0° · 🌙 12% · 🌌 80° / -54°');
  assert.equal(astroText({...HOUR},'aurora'),'☀️ 247° / 0° · 🌌 Kp 5');
  assert.equal(astroText({sun_azimuth:null,sun_elevation:null},'mountain_view'),'');
});

test('CL-UI-46 (1b): the card line drops the repeated solar pair but keeps everything else',()=>{
  // The duplicated segment — and ONLY the duplicated segment — is gone.
  for(const theme of ['mountain_view','cloud_sea','sunrise','sunset','blue_hour','sky_glow','overcast_soft']){
    assert.equal(cardAstroText({...HOUR},theme),'',`${theme}: nothing left to print once the ☀ pill is removed`);
  }
  assert.doesNotMatch(cardAstroText({...HOUR},'mountain_view'),/☀|247|0°/,'the solar angles never reach the lower line');
  // Non-duplicate information survives: the ☀ pill carries no moon, no galactic
  // core and no Kp, so those must still be rendered on the card.
  assert.equal(cardAstroText({...HOUR},'milky_way'),'🌙 12% · 🌌 80° / -54°');
  assert.equal(cardAstroText({...HOUR},'aurora'),'🌌 Kp 5');
  // A genuinely missing field still degrades to nothing (no invented dash).
  assert.equal(cardAstroText(null,'mountain_view'),'');
});

test('CL-UI-46 (1c): the card renders the reduced text on the lower line and keeps the ☀ pill on top',()=>{
  assert.match(appSource,/const astro=\(researchPending\|\|noViable\)\?'':cardAstroText\(metric,theme\);/,
    'createSpotCard feeds the reduced helper into the lower meta row');
  assert.doesNotMatch(appSource,/const astro=\(researchPending\|\|noViable\)\?'':astroText\(metric,theme\);/,
    'the duplicated call is gone from the card');
  // The top row is untouched: elevation + the sun pill still sit in the chips.
  // CL-UI-115 §1: the pill's glyph is the inline SVG azimuth icon (emoji only
  // survives as fallback data), and the degrees text is unchanged.
  assert.match(appSource,/const clSunPill=\(metric&&metric\.sun_azimuth!=null&&metric\.sun_elevation!=null\)\?`<span class="metric-chip">\$\{clIconSvg\('azimuth'\)\} \$\{Math\.round\(metric\.sun_azimuth\)\}°\/\$\{Math\.round\(metric\.sun_elevation\)\}°<\/span>`:'';/,
    'the ☀ azimuth/elevation pill is the single place the card states the angles');
  assert.doesNotMatch(appSource,/const clSunPill=[^;]*'☀ \$/, 'no emoji sun glyph in the pill any more');
  assert.match(appSource,/<span class="card-metric-chips">\$\{clElevPill\}\$\{clSunPill\}/,
    'the pill still renders in the top chip row');
  // The lower line renders only when it has something to say.
  assert.match(appSource,/\$\{astro\?`<div class="info-row card-meta-row card-meta-astro">\$\{astro\}<\/div>`:''\}/,
    'an empty lower line is not emitted at all (the card loses a whole row)');
});

// ------------------------------------------------------- (2b) one count only

test('CL-UI-46 (2b): the day pill no longer prints the place count as visible text',()=>{
  const sync=grab('function syncDayButtons','function openDayPicker');
  assert.match(sync,/const summary=n===null\?'':`\$\{n>0\?d\(\)\.day_summary_viable\.replace\('\{n\}',n\):d\(\)\.day_summary_none\}`;/,
    'the 「N 個景點符合」 string no longer carries the " · " glue that put it on the pill face');
  assert.match(sync,/<span class="day-picker-main">📅 \$\{esc\(o\.label\)\}<\/span>/,
    'the visible main line is the day label alone');
  assert.match(sync,/const subLine=regionSummary;/,
    'the visible sub-line is the region summary alone (no 「列表 N 個」)');
  // …but nothing is lost: both numbers move into the tooltip + SR label.
  assert.match(sync,/const clListCount=clListN===null\?'':d\(\)\.clui45_listed\.replace\('\{n\}',clListN\);/,
    'CL-UI-45 (counts): the list length still reads the same publish');
  assert.match(sync,/const triggerInfo=\[summary,clListCount\]\.filter\(Boolean\)\.join\(' · '\);/);
  assert.match(sync,/trigger\.setAttribute\('title',triggerInfo\)/,'the counts are reachable on hover');
  assert.match(sync,/trigger\.setAttribute\('aria-label',`\$\{o\.label\}\$\{triggerInfo\?' — '\+triggerInfo:''\} — \$\{d\(\)\.day_picker_label\}`\)/,
    'and are announced to screen readers');
  // The pill face must not contain a digit-count template any more.
  const faceStart=sync.indexOf('trigger.innerHTML=');
  const face=sync.slice(faceStart,sync.indexOf(';\n',faceStart));
  assert.doesNotMatch(face,/個景點|spots|clui45_listed|day_summary_viable/,'the rendered face carries no count');
});

test('CL-UI-46 (2b): the list header is the ONE visible place count',()=>{
  // #filter-result-summary keeps its count (it sits with the 地區/排序 controls
  // inside the sticky filter shell, so it stays on screen while the list
  // scrolls), and nothing else in the shell prints 「N 個景點」.
  assert.match(appSource,/function updateFilterResultSummary\(count,effSort\)\{[\s\S]*?el\.textContent=template\.replace\('\{n\}',count\);/,
    'the list header still states the honest list length');
  assert.match(indexSource,/<div class="rank-summary" id="filter-result-summary"><\/div>/,'the header host survives');
  assert.match(cssSource,/\.filter-shell \{[^}]*position:\s*sticky/,'desktop: the header lives in the sticky shell');
  // …and the mobile rule really is static (the comment must not claim more).
  assert.match(cssSource,/\.filter-shell \{\s*position:\s*static;/,'mobile ≤640px: .filter-shell is static, so the header scrolls away — the comment says so');
  // No other first-screen surface re-derives a 「個景點」 count of its own.
  assert.doesNotMatch(grab('function syncDayButtons','function openDayPicker').replace(/\/\/[^\n]*/g,''),/個景點/,
    'the day pill prints no place count');
});

// ------------------------------------------- (2a) the source-filter row hides

test('CL-UI-46 (2a): the source-filter row is hidden unless the member owns a private place',()=>{
  assert.match(cssSource,/body:not\(\[data-cp-has-private="1"\]\) \.cl-cp-view-bar\{display:none\}/,
    'the view bar is display:none for every state except an explicit flag');
  // Default-hidden must out-specify the owning stylesheet's `display:flex`
  // (custom-places.css loads AFTER app.css).
  const rule=cssSource.match(/body:not\(\[data-cp-has-private="1"\]\) \.cl-cp-view-bar\{[^}]*\}/)[0];
  assert.match(rule,/display:none/);
  assert.ok(rule.indexOf('body')===0,'the body-scoped selector wins the cascade');
  assert.doesNotMatch(cssSource,/\.cl-cp-view-bar\{display:flex/,'app.css does not force the bar visible');
  // app.js publishes the flag from the member's REAL private-place list …
  const sync=grab('function clui46SyncPrivateFlag','function filterAndRender');
  assert.match(sync,/const st=\(api&&typeof api\.state==='function'\)\?api\.state\(\):null;/,
    'the count reads the module state that the bar label itself counts');
  assert.match(sync,/n=\(st&&st\.data&&Array\.isArray\(st\.data\.places\)\)\?st\.data\.places\.length:0;/,
    'it counts state.data.places (custom-places privatePlaces()), never rendered rows');
  assert.doesNotMatch(sync,/cardRows/,
    'CONDITION 1: cardRows() drops trial-expired / pending / theme-less places — it must not drive the flag');
  assert.match(sync,/catch\(e\)\{n=0;\}/,'fail-closed: a broken state read keeps the bar hidden');
  assert.match(sync,/document\.body\.setAttribute\('data-cp-has-private',n>0\?'1':'0'\)/,
    'exactly one private place flips the flag on');
  // … and does it BEFORE the data guard, so a member who adds his first place
  // while the summary bundle is still loading still gets the row back.
  const pass=grab('function filterAndRender','const cpView=document.body.getAttribute');
  assert.ok(pass.indexOf('clui46SyncPrivateFlag()')<pass.indexOf("if(!currentData)return;"),
    'the flag is published before the currentData early return');
  // CONDITION 2: every cp-data event re-reads it, even with no summary data; a
  // sign-out clears it at once.
  assert.match(appSource,/document\.addEventListener\('chaselights:cp-data',function\(\)\{clui46SyncPrivateFlag\(\);if\(currentData\)filterAndRender\(\);\}\);/,
    'the cp-data handler syncs the flag unconditionally (no currentData gate)');
  assert.match(appSource,/document\.addEventListener\('chaselights:auth',function\(e\)\{[\s\S]{0,340}?if\(!member\)\{try\{document\.body\.setAttribute\('data-cp-has-private','0'\);/,
    'sign-out clears the flag immediately');
  // A member WITH private places keeps today's bar behaviour verbatim.
  assert.match(appSource,/let cpRows=\(window\.ChaseLightsCustomPlaces&&window\.ChaseLightsCustomPlaces\.cardRows\)\?window\.ChaseLightsCustomPlaces\.cardRows\(\):\[\];/,'the private rows still flow into the one filter pipeline');
  assert.match(appSource,/if\(cpView==='official'\)cpRows=\[\];/,'view tabs still compose (官方)');
  assert.match(appSource,/if\(cpView==='private'\)rowsAll\.length=0;/,'view tabs still compose (私人)');
});

// ----------------------------------------------------------- cache-bust stamp

test('CL-UI-46: app.js/app.css generation bumped to clui144 on every page that loads them',()=>{
  // CL-UI-115: the icon set joins the generation — three stamped assets now.
  assert.equal((indexSource.match(/\?v=clui144/g)||[]).length,3,'app.css + app.js + icons.js all at clui144');
  assert.match(indexSource,/assets\/app\.js\?v=clui144/);
  assert.match(indexSource,/assets\/app\.css\?v=clui144/);
  // CL-UI-115 §1: the icon set is a first-class stamped asset, loaded BEFORE app.js.
  assert.match(indexSource,/assets\/icons\.js\?v=clui144/);
  assert.ok(indexSource.indexOf('assets/icons.js')<indexSource.indexOf('assets/app.js'),
    'icons.js must load before app.js so its label tables can resolve glyphs');
  const pages={index:'index.html','genre-eval':'genre-eval.html',reminders:'reminders.html',sources:'sources.html'};
  for(const [name,file] of Object.entries(pages)){
    const html=readFileSync(new URL('../../../'+file,import.meta.url),'utf8');
    assert.match(html,/assets\/app\.css\?v=clui144/,`${name}: app.css carries the bumped stamp`);
  }
  // No page and no shipped asset may still quote the old generation.
  assert.ok(!indexSource.includes('clui135'),'index.html: no stale stamp');
  assert.ok(!appSource.includes('clui135'),'app.js: no stale stamp');
});
