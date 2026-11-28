// CL-UI-115 §2 — the card shows NOW, and the subject panel lists windows.
//
// Two behaviours with real data behind them:
//   (1) now_hour: the card weather row must equal the place's hourly row for the
//       CURRENT hour (in the place's timezone), clamped to the served range, and
//       never silently present another day's weather as today's.
//   (2) fog right now tints the condition chip (class + amber tokens) and adds a
//       reason, driven by fog_visibility / in_cloud_fog FAIL or visibility < 1 km.
//   (3) the subject-window model: per subject, today + the next six days, every
//       cell carries a window or an explicit 「今日無符合時段」/「資料不足」 string.
//       Asserted over ALL 459 places of the committed subject-cards artifact.
//
// Harness: the shipped functions are sliced out of assets/app.js and re-run with
// the real artifact — the same technique CL-UI-45/46/69 use (the V1 shell has no
// DOM harness of its own).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const APP=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
// CL-CI-36: the artifact filename is a refreshable pointer — read it from app.js
// (never copy a timestamp into a test; a six-hourly refresh would rot the pin).
const CARDS_FILE=(APP.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/)||[])[1];
assert.ok(CARDS_FILE,'app.js pins the subject-cards artifact filename');
const CARDS=JSON.parse(readFileSync(new URL('../../../data/v2/evaluations/'+CARDS_FILE,import.meta.url),'utf8'));
const BUNDLE=JSON.parse(readFileSync(new URL('../../web-v2/evaluations-latest.json',import.meta.url),'utf8'));

const DICT={
  clui115_fog_now:'目前起霧，能見度低',clui115_no_window_today:'今日無符合時段',clui115_no_window_day:'無符合時段',
  clui115_sw_title:'題材時段（今天起 7 天）',eval2_unk:'資料不足',nw_rel_0:'今天',nw_rel_1:'明天',nw_rel_2:'後天',
  wmo_clear:'晴',wmo_mostly_clear:'晴時多雲',wmo_partly:'多雲',wmo_overcast:'陰',wmo_fog:'霧',wmo_drizzle:'毛毛雨',
  wmo_rain:'雨',wmo_showers:'陣雨',wmo_snow:'雪',wmo_snow_showers:'陣雪',wmo_thunder:'雷雨',vis_cap:'≥ 24 km（資料上限）'
};

function slice(start,end){
  const i=APP.indexOf(start);
  const j=APP.indexOf(end,i);
  assert.ok(i>0&&j>i,`slice ${start} → ${end}`);
  return APP.slice(i,j);
}

// Dependencies the sliced block calls at runtime, provided here (never re-derived
// business logic — the verdict helpers come from app.js itself).
const PRELUDE=`
  const currentTempUnit='C';
  const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const d=()=>DICT;
  const formatTemp=c=>{ if(c==null||c===''||Number.isNaN(Number(c)))return '—'; return (Math.round(Number(c)*10)/10)+'°C'; };
  const visibilityText=km=>{ if(km==null||km==='')return null; const n=Number(km); if(!Number.isFinite(n))return null; if(n>=24.1)return DICT.vis_cap; return n+' km'; };
  const clIconSvg=k=>'<svg data-cl-icon="'+k+'" aria-hidden="true"></svg>';
  const wmoWord=()=>'天氣';
  const wmoIcon=()=>'<svg data-cl-icon="wmo" aria-hidden="true"></svg>';
  const clUrl=p=>p;
`;

function build(cards){
  const body=slice('function clui115LocalParts','function trMessage');
  const rowFn=slice('function v2SubjectCardRow','// CL-UI-63: dedup short subject names');
  const factory=new Function('v2SubjectCards','currentLang','DICT',[
    PRELUDE,rowFn,body,
    'return {clui115LocalParts,clui115HourRows,clui115NowHourRow,clui115NowFog,clui115NowChipHtml,clui115NowSkewTier,clui115SubjectWindowDates,clui115SubjectWindowRows,clui115SubjectWindowsHtml,clui115NowHourLabel};'
  ].join('\n'));
  return factory({places:cards.places,dictionaries:cards.dictionaries},'zh-TW',DICT);
}
const api=build(CARDS);

// Fixed instants (UTC) that land on known Taipei hours: 2026-11-27 10:20 Taipei
// is 02:20Z; 23:40 Taipei is 15:40Z.
const TPE='Asia/Taipei';
const AT_1020=Date.UTC(2026,10,27,2,20);
const AT_2340=Date.UTC(2026,10,27,15,40);

function rowsFor(date,hours){
  return hours.map(h=>({time:`${date} ${h}:00`,local_date:date,weather_code:3,temp:18.4,visibility:12.5}));
}

// ------------------------------------------------------------------ now_hour

test('CL-UI-115 §2 (now_hour): the card row is the CURRENT hour of the place, not the day representative',()=>{
  const rows=rowsFor('2026-11-27',['08','09','10','11','12']);
  rows[2].temp=21.7;rows[2].weather_code=61;rows[2].visibility=4.2;
  const pick=api.clui115NowHourRow(rows,TPE,AT_1020);
  assert.equal(pick.hhmm,'10:00','the 10:20 Taipei instant selects the 10:00 row');
  assert.equal(pick.row.temp,21.7,'the selected row is the 10:00 row, not the day aggregate');
  assert.equal(pick.exact,true);
  const chip=api.clui115NowChipHtml(rows,TPE,AT_1020);
  assert.match(chip,/data-now-hour="10:00"/,'the chip labels its hour');
  assert.match(chip,/21\.7°C/,'the chip shows the current-hour temperature');
  assert.match(chip,/4\.2 km/,'the chip shows the current-hour visibility');
});

test('CL-UI-115 §2 (now_hour): an hour outside the served range clamps, and the label says which hour',()=>{
  // Forecast starts at 12:00 today; the user opens the page at 10:20.
  const late=rowsFor('2026-11-27',['12','13','14']);
  const pick=api.clui115NowHourRow(late,TPE,AT_1020);
  assert.equal(pick.hhmm,'12:00','clamped to the first served hour of today');
  assert.equal(pick.exact,false,'the chip is honest that it is not the exact current hour');
  assert.equal(pick.date,'2026-11-27','still the place-local today — never another day presented as now');
  assert.match(api.clui115NowChipHtml(late,TPE,AT_1020),/data-now-hour="12:00"/);
  // …and the other edge (all hours passed): clamp to the last served hour today.
  const early=rowsFor('2026-11-27',['06','07','08']);
  const pick2=api.clui115NowHourRow(early,TPE,AT_2340);
  assert.equal(pick2.hhmm,'08:00');
  assert.equal(pick2.date,'2026-11-27');
});

test('CL-UI-117 §5: the THREE-TIER hour policy — now / stale / dropped',()=>{
  // Reviewer finding: a same-day 06:00 row painted as `.now-wx` at 20:00 — the
  // date matched, the hour was 14 h away, and the chip still claimed "now".
  // Owner ruling (replaces the earlier "drop past 2 h"): the artifact is
  // republished every 6 h, so a 2 h bound blanks the row for most of a cycle.
  //   skew <= 1 h        -> current row, `.now-wx`
  //   1 h < skew <= 6 h  -> `.now-wx.now-stale`, its OWN hour in the label
  //   skew > 6 h         -> dropped, the honest day chip stays
  const AT_1000=Date.UTC(2026,10,27,2,0);
  const AT_1001=Date.UTC(2026,10,27,2,1);

  // --- tier 1: current row
  const fresh=api.clui115NowChipHtml(rowsFor('2026-11-27',['10']),TPE,AT_1020);
  assert.match(fresh,/class="metric-chip day-wx now-wx"/,'20 min away is a current row');
  assert.doesNotMatch(fresh,/now-stale/);
  // Both sides of the 1 h boundary: 60 min is still current, 61 min is not.
  assert.match(api.clui115NowChipHtml(rowsFor('2026-11-27',['09']),TPE,AT_1000),/now-wx"/,
    'exactly 60 min behind is a current row (boundary inside)');
  assert.match(api.clui115NowChipHtml(rowsFor('2026-11-27',['09']),TPE,AT_1001),/now-stale/,
    '61 min behind is stale, not current (boundary outside)');

  // --- tier 2: rendered, but explicitly NOT now
  const stale=api.clui115NowChipHtml(rowsFor('2026-11-27',['06']),TPE,AT_1020);
  assert.match(stale,/now-wx now-stale/,'a 260 min old row is still rendered');
  assert.match(stale,/data-now-stale="1"/);
  assert.match(stale,/<span class="now-hour">06:00<\/span> · /,'its own hour LEADS the label');
  assert.match(stale,/18\.4°C/,'the observation itself is still shown');
  assert.doesNotMatch(stale,/現在|now"|>now</,'a stale row is never labelled as a present tense');
  // Both sides of the 6 h boundary: 360 min renders stale, 361 min is dropped.
  const atEdge=api.clui115NowChipHtml(rowsFor('2026-11-27',['04']),TPE,AT_1000);
  assert.match(atEdge,/now-stale/,'exactly 6 h behind still renders (labelled stale)');
  assert.equal(api.clui115NowChipHtml(rowsFor('2026-11-27',['04']),TPE,AT_1001),'',
    '6 h 01 min behind is dropped');

  // --- tier 3: dropped (the 14 h case the reviewer found)
  const morning=rowsFor('2026-11-27',['06','07','08']);
  assert.equal(api.clui115NowHourRow(morning,TPE,AT_2340).hhmm,'08:00','the picker still clamps…');
  assert.equal(api.clui115NowChipHtml(morning,TPE,AT_2340),'','…but a 15 h gap is never rendered');
  // The boundary constants are the documented ones.
  assert.equal(api.clui115NowSkewTier({date:'2026-11-27',hhmm:'09:00'},TPE,AT_1000).tier,'now');
  assert.equal(api.clui115NowSkewTier({date:'2026-11-27',hhmm:'09:00'},TPE,AT_1001).tier,'stale');
  assert.equal(api.clui115NowSkewTier({date:'2026-11-27',hhmm:'03:00'},TPE,AT_1001),null);
});

test('CL-UI-115 §2 (now_hour): a row from another local date is NEVER a now row',()=>{
  // Reviewer condition 3. A stale shard (its newest row 11/15 while the clock
  // reads 11/27) used to paint a `now-wx` chip built from 11/15 with a
  // `11/15 02:00` suffix. A date suffix does not make it honest: the chip still
  // says "right now". So no row for the place-local today ⇒ no now row at all,
  // and the card keeps the day-weather chip, which labels its own date.
  const stale=rowsFor('2026-11-15',['02','03','04']);
  assert.equal(api.clui115NowHourRow(stale,TPE,AT_1020),null,'no row for the place-local today → no pick');
  assert.equal(api.clui115NowChipHtml(stale,TPE,AT_1020),'','…and therefore no now chip (the day chip stays)');
  // BRANCH 2 — the SAME shard on its own day really is now, and keeps its row.
  const onItsDay=Date.UTC(2026,10,14,18,20); // 2026-11-15 02:20 Asia/Taipei
  const pick=api.clui115NowHourRow(stale,TPE,onItsDay);
  assert.ok(pick,'a today row still yields a now row');
  assert.equal(pick.date,'2026-11-15','and the pick is a row of the place-local today');
  assert.match(api.clui115NowChipHtml(stale,TPE,onItsDay),/data-now-hour="02:00"/,'the real now row is rendered, hour label and all');
  // A future-dated shard follows the same rule (never presented as now).
  const future=rowsFor('2026-11-28',['00','01','02']);
  assert.equal(api.clui115NowChipHtml(future,TPE,AT_1020),'');
  // No hourly forecast at all → no chip either.
  assert.equal(api.clui115NowChipHtml([],TPE,AT_1020),'');
  assert.equal(api.clui115NowHourRow(null,TPE,AT_1020),null);
  // A today row never carries a date prefix in its label.
  const chip=api.clui115NowChipHtml(rowsFor('2026-11-27',['10']),TPE,AT_1020);
  assert.doesNotMatch(chip,/data-now-hour="\d{1,2}\/\d{1,2} /,'a now row labels an hour of today, never another date');
});

test('CL-UI-115 §5: the hour is picked from the PASSED instant, never a fresh Date.now()',()=>{
  // Recomputing Date.now() inside the helpers (the old bug) makes the pick
  // depend on wall-clock time, so a test and the page disagree.
  const rows=rowsFor('2026-11-27',['08','09','10','11']);
  assert.equal(api.clui115NowHourRow(rows,TPE,AT_1020).hhmm,'10:00','the passed instant selects the 10:00 row');
  assert.equal(api.clui115NowHourRow(rows,TPE,Date.UTC(2026,10,27,0,5)).hhmm,'08:00','a different instant selects a different hour');
  const pick=api.clui115NowHourRow(rows,TPE,AT_1020);
  assert.equal(api.clui115NowHourLabel(pick),'10:00','the label is the picked hour');
  assert.equal(api.clui115NowHourLabel(null),'','no pick → no label');
  // The label helper reads no clock at all (and carries no date prefix branch:
  // a non-today row is not a now row in the first place, condition 3).
  const labelFn=slice('function clui115NowHourLabel','// ONE renderer for the now chip')
    .split('\n').filter(l=>!l.trim().startsWith('//')).join('\n');
  assert.doesNotMatch(labelFn,/Date\.now\(\)/,'the label helper never reads the clock');
  assert.doesNotMatch(labelFn,/pick\.date/,'no cross-day labelling survives — that row would have been suppressed');
  assert.match(labelFn,/pick\.hhmm/,'it returns the picked hour');
});


test('CL-UI-115 §2 (fog): a foggy now tints the chip and states the reason',()=>{
  const foggy=rowsFor('2026-11-27',['10']);foggy[0].visibility=0.4;
  const html=api.clui115NowChipHtml(foggy,TPE,AT_1020);
  assert.match(html,/cl-now-fog/,'the fog state is a CLASS (CSS owns the amber tint)');
  assert.match(html,/data-now-fog="1"/);
  assert.match(html,/now-fog-reason/,'the reason text rides the chip');
  assert.match(html,/目前起霧/);
  // a fog WMO code counts too
  const code=rowsFor('2026-11-27',['10']);code[0].weather_code=45;
  assert.equal(api.clui115NowFog(code[0]),true,'WMO 45 (fog) is fog right now');
  // an explicit metric verdict list is NOT a signal: the shards carry raw values
  // only (measured: 0 of 42,048 rows have `conditions[]`), so the dead branch was
  // deleted rather than left claiming a verdict path that never runs.
  const verdict=rowsFor('2026-11-27',['10']);
  verdict[0].conditions=[{metric:'fog_visibility',verdict:'FAIL'}];
  assert.equal(api.clui115NowFog(verdict[0]),false,'a fog_visibility FAIL row is not a source — no shard carries conditions[]');
  verdict[0].conditions=[{metric:'in_cloud_fog',verdict:'FAIL'}];
  assert.equal(api.clui115NowFog(verdict[0]),false,'an in_cloud_fog FAIL row is not a source either');
  // the documented signals are visibility < 1 km and WMO 45/48 — nothing else.
  const justUnder=rowsFor('2026-11-27',['10']);justUnder[0].visibility=0.9;
  assert.equal(api.clui115NowFog(justUnder[0]),true,'visibility under 1 km is fog');
  const atOne=rowsFor('2026-11-27',['10']);atOne[0].visibility=1;
  assert.equal(api.clui115NowFog(atOne[0]),false,'1.0 km is the boundary, not fog');
  const code48=rowsFor('2026-11-27',['10']);code48[0].weather_code=48;
  assert.equal(api.clui115NowFog(code48[0]),true,'WMO 48 (depositing rime fog) is fog');
  // clean weather keeps the plain chip
  const clean=rowsFor('2026-11-27',['10']);
  const cleanHtml=api.clui115NowChipHtml(clean,TPE,AT_1020);
  assert.doesNotMatch(cleanHtml,/cl-now-fog/,'clear weather is not tinted');
  assert.doesNotMatch(cleanHtml,/now-fog-reason/);
});

// --------------------------------------------------------- subject windows

test('CL-UI-115 §2 (subject windows): today + the following six days, per subject',()=>{
  const dates=api.clui115SubjectWindowDates(TPE,AT_1020,7);
  assert.equal(dates.length,7);
  assert.equal(dates[0],'2026-11-27','the first column is the place-local today');
  assert.equal(dates[6],'2026-12-03');
  const model=api.clui115SubjectWindowRows('jp-003',TPE,AT_1020,['overlook']);
  assert.ok(model.rows.length>=1,'the place with a suitable row produces at least one subject row');
  const row=model.rows.find(r=>r.genre==='overlook');
  assert.ok(row,'the supported subject is present');
  assert.equal(row.cols.length,7);
  // CL-CI-140: do not pin a weather-dependent hour. The window moves whenever
  // the artifact is regenerated, so derive the expectation from the artifact
  // itself: the cell must state the artifact's own first window stamp, or say
  // 資料不足 when that place-day has no suitable row at all.
  const dayRow=(CARDS.places['jp-003']||{})['2026-11-27']||{};
  const suit=(dayRow.suitable||[]).find(s=>s&&s.genre==='overlook');
  if(suit&&Array.isArray(suit.window)&&suit.window.length){
    assert.ok(row.cols[0].text.includes(suit.window[0]),
      `today's window is the artifact's window (expected ${suit.window[0]}, got ${row.cols[0].text})`);
  }else{
    assert.match(row.cols[0].text,/資料不足/,
      `no suitable window in the artifact ⇒ the cell says 資料不足 (got ${row.cols[0].text})`);
  }
});

test('CL-UI-115 §2 (subject windows): ZERO empty cells across all 459 places',()=>{
  const places=Object.keys(CARDS.places);
  assert.equal(places.length,459,`the artifact carries 459 places (got ${places.length})`);
  const genresByPlace=new Map();
  for(const place of BUNDLE.places||[]){
    const gs=(place.opportunities||[]).map(o=>o&&o.genre_template).filter(Boolean);
    if(gs.length)genresByPlace.set(place.place_id,gs);
  }
  let rows=0,cells=0,emptyCells=0,emptyNames=0;
  for(const id of places){
    const model=api.clui115SubjectWindowRows(id,TPE,AT_1020,genresByPlace.get(id));
    for(const row of model.rows){
      rows++;
      if(!row.name||!row.name.trim())emptyNames++;
      for(const col of row.cols){
        cells++;
        if(!col.text||!col.text.trim())emptyCells++;
      }
    }
  }
  assert.equal(emptyCells,0,`every subject×day cell states a window or an explicit no-window string (checked ${cells} cells over ${places.length} places)`);
  assert.equal(emptyNames,0,`every subject row is named (checked ${rows} rows)`);
  assert.ok(rows>=459,`every place contributes at least one subject row (got ${rows} rows)`);
});

test('CL-UI-115 §2 (subject windows): a day the layer cannot cover says 資料不足, never空白',()=>{
  // A place id that does not exist in the artifact at all: every cell must be an
  // explicit string, so the panel can never render a hollow row.
  const model=api.clui115SubjectWindowRows('tw-999','Asia/Taipei',AT_1020,['sunset']);
  assert.equal(model.rows.length,1,'the supported subject still gets a row');
  for(const col of model.rows[0].cols) assert.equal(col.text,'資料不足');
  const html=api.clui115SubjectWindowsHtml('tw-999','Asia/Taipei',AT_1020,['sunset']);
  assert.match(html,/data-subject-windows="1"/);
  assert.equal((html.match(/<span class="sw-win">([^<]*)<\/span>/g)||[]).every(m=>!/<span class="sw-win"><\/span>/.test(m)),true,'no hollow window cell');
});

test('CL-UI-117 §5: `.now-stale` is visibly muted — it must not look like a current row',()=>{
  const CSS=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
  const rule=(CSS.match(/\.now-wx\.now-stale\{([^}]*)\}/)||[])[1];
  assert.ok(rule,'a .now-stale modifier rule exists');
  assert.match(rule,/opacity:\.\d+/,'the row is faded…');
  assert.match(rule,/color:var\(--cl-text-2\)/,'…and carries the secondary tone');
  assert.match(CSS,/\.now-wx\.now-stale svg\{[^}]*stroke:/,'the icon stroke is muted too');
  // It must be a DIFFERENT rendering than a current row, not an alias.
  const freshRule=(CSS.match(/\.now-wx\{([^}]*)\}/)||[])[1]||'';
  assert.doesNotMatch(freshRule,/opacity/,'a current row is not faded');
});

// NOTE — WRONG DEVICE CLOCK is INTENDED degradation (CL-UI-117 §6): a device
// whose clock is off by more than the 26 h artifact bound gets NO now row at all
// (both the artifact bound and the hour-tier gate read the device clock), and
// keeps the honest day chip. There is deliberately no test asserting a row in
// that case: presenting one would be a fabricated present tense. This note is
// the record so a later reader does not "fix" the blank row by trusting the
// device clock.
test('CL-UI-115 §2 (single source): the panel reads v2SubjectCardRow — no re-derived verdict',()=>{
  const body=slice('function clui115SubjectWindowRows','function clui115SubjectWindowsHtml');
  assert.match(body,/v2SubjectCardRow\(spotId,date\)/,'the subject rows come from the card\'s own lookup');
  assert.doesNotMatch(body,/hour_counts|good_hours|state===/,'the panel never re-derives a verdict from the bundle');
  // The card and the panel share the NOW renderer. CL-UI-117 changed only the
  // SOURCE of the rows (the precomputed sidecar first, the shard cache second) —
  // the renderer is still the one function, so the chip's wording cannot drift.
  const card=slice('const dayWx=dayWeatherFor','const tempChip=tempChipHtml(metric.temp);');
  assert.match(card,/clui115NowChipHtml\(clui117NowRows\(spot\.spot_id,spot\.timezone/,'the card paints the now chip through the SAME renderer');
});
