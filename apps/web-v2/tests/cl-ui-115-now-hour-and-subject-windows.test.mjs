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
const CARDS_FILE='subject-cards-20261112T202312Z.json';
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
    'return {clui115LocalParts,clui115HourRows,clui115NowHourRow,clui115NowFog,clui115NowChipHtml,clui115SubjectWindowDates,clui115SubjectWindowRows,clui115SubjectWindowsHtml,clui115NowHourLabel};'
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
  assert.equal(pick.today,true,'still today — never another day presented as now');
  assert.match(api.clui115NowChipHtml(late,TPE,AT_1020),/data-now-hour="12:00"/);
  // …and the other edge (all hours passed): clamp to the last served hour today.
  const early=rowsFor('2026-11-27',['06','07','08']);
  const pick2=api.clui115NowHourRow(early,TPE,AT_2340);
  assert.equal(pick2.hhmm,'08:00');
  assert.equal(pick2.today,true);
});

test('CL-UI-115 §2 (now_hour): a forecast that does not cover today is labelled with its own date',()=>{
  const future=rowsFor('2026-11-28',['00','01','02']);
  const pick=api.clui115NowHourRow(future,TPE,AT_1020);
  assert.equal(pick.today,false,'today is not covered — the row is NOT claimed as today');
  const chip=api.clui115NowChipHtml(future,TPE,AT_1020);
  assert.match(chip,/data-now-hour="11\/28 00:00"/,'the label carries the date of the row actually shown');
  // No hourly forecast at all → no chip (the caller keeps the day-weather chip).
  assert.equal(api.clui115NowChipHtml([],TPE,AT_1020),'');
  assert.equal(api.clui115NowHourRow(null,TPE,AT_1020),null);
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
  // an explicit metric verdict counts too (fog_visibility / in_cloud_fog FAIL)
  const verdict=rowsFor('2026-11-27',['10']);
  verdict[0].conditions=[{metric:'fog_visibility',verdict:'FAIL'}];
  assert.equal(api.clui115NowFog(verdict[0]),true,'fog_visibility FAIL at now_hour');
  verdict[0].conditions=[{metric:'in_cloud_fog',verdict:'FAIL'}];
  assert.equal(api.clui115NowFog(verdict[0]),true,'in_cloud_fog FAIL at now_hour');
  verdict[0].conditions=[{metric:'in_cloud_fog',verdict:'PASS'}];
  assert.equal(api.clui115NowFog(verdict[0]),false,'a PASS verdict is not fog');
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
  assert.match(row.cols[0].text,/16:00/,'today\'s window is the artifact\'s window');
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

test('CL-UI-115 §2 (single source): the panel reads v2SubjectCardRow — no re-derived verdict',()=>{
  const body=slice('function clui115SubjectWindowRows','function clui115SubjectWindowsHtml');
  assert.match(body,/v2SubjectCardRow\(spotId,date\)/,'the subject rows come from the card\'s own lookup');
  assert.doesNotMatch(body,/hour_counts|good_hours|state===/,'the panel never re-derives a verdict from the bundle');
  // The card and the panel share the NOW renderer.
  const card=slice('const dayWx=dayWeatherFor','const tempChip=tempChipHtml(metric.temp);');
  assert.match(card,/clui115NowChipHtml\(clui115NowRows\(spot\.spot_id\)/,'the card paints the now chip through the SAME renderer');
});
