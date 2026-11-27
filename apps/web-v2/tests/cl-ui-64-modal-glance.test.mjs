// CL-UI-64: place-modal declutter (three-tier architecture, owner-approved).
// Tier 1 — top "today at a glance" quick view (subject-cards lookup: suitable
// -> short subject chips + window; not-met -> one dominant short reason word).
// Tier 2 — the 8-day assessment becomes a compact strip: one row of day+badge
// cells, click/hover reveals a SHORT reason word (never the long sentence).
// Tier 3 — 拍攝條件/成立條件 collapses into an accordion (default closed,
// summary shows 條件 ×N); the long narrative lives only behind it. Plus an
// hourly-forecast exit link at the modal bottom (weather-map deep link with
// place_id as spot). Source assertions + extracted pure helpers, per the
// established V1-shell test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const appCss = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');
// CL-CI-36: the artifact is read through the SAME stable pointer app.js uses
// (V2_SUBJECT_CARDS_FILE) — never a filename copied into the test.
const cardsFile = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
assert.ok(cardsFile, 'subject-cards filename pinned in app.js');
const artifact = JSON.parse(readFileSync(
  join(ROOT, 'data', 'v2', 'evaluations', cardsFile), 'utf8'));

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};

test('CL-UI-64 (1): forecast modal opens with a quick-view section fed by the gated bundle fetch', () => {
  // CL-UI-98 (DESIGN-6b efdd1febc): the quick view moved into the FORECAST
  // modal shell (index.html #modal-overlay) — the card-click surface; the
  // subject panel (#place-modal-overlay) no longer renders it.
  assert.match(indexSource, /<section class="place-quick-view modal-quick-view"[^>]*>/);
  assert.match(indexSource, /id="modal-quick-view-body"/);
  assert.ok(!appSource.includes('place-quick-view-body'),
    'CL-UI-98: the subject panel no longer hosts the quick view');
  // Filled inside mountQuickView's single gated fetch (subject cards load
  // alongside the evaluation bundle; a bundle failure degrades honestly).
  assert.match(appSource, /host\.innerHTML=bundle\?v2QuickViewHtml\(spot,qPlace\):`<span class="quick-none">\$\{esc\(d\(\)\.eval2_load_fail\)\}<\/span>`/);
  // The forecast modal mounts the SAME pipeline (one implementation).
  assert.match(appSource, /mountQuickView\(document\.getElementById\('modal-quick-view-body'\),spot\)/);
});

test('CL-UI-64 (2): quick view is 「現在去會怎樣」 — tier chip / band / next moment (CL-UI-95 DESIGN-5)', () => {
  const helperCode = grab('function v2DominantFailMetric', 'function ensureV2Detail');
  // CL-CI-36: the scheduled refresh slides the 8-day window every run, so
  // the tier exemplars are DERIVED from the current artifact: one row per
  // tier verdict (recommend / shootable+tier_reason / not_recommended).
  const anchorDate = {};
  for (const [pid, days] of Object.entries(artifact.places)) {
    for (const [dt, row] of Object.entries(days)) {
      if (!anchorDate.rec && row.tier === 'recommend') anchorDate.rec = {pid, dt};
      if (!anchorDate.mid && row.tier === 'shootable' && row.tier_reason) anchorDate.mid = {pid, dt};
      if (!anchorDate.bad && row.tier === 'not_recommended' && row.dominant_reason) anchorDate.bad = {pid, dt};
    }
  }
  assert.ok(anchorDate.rec && anchorDate.mid && anchorDate.bad,
    'artifact carries recommend / shootable(+reason) / not_recommended rows');
  const makePrelude = (dayDate, cards) => `
    const V2_EVAL_METRICS={'zh-TW':{precipitation:'降水',visibility:'能見度',cloud_cover_low:'低雲'},en:{precipitation:'Precipitation',visibility:'Visibility',cloud_cover_low:'Low cloud'},ja:{precipitation:'降水',visibility:'視程',cloud_cover_low:'下層雲'}};
    const V2_FAIL_PRIORITY=['precipitation','visibility','cloud_cover_low'];
    let currentLang='zh-TW';
    let v2SubjectCards=${JSON.stringify(cards)};
    const v2SubjectCardRow=(id,date)=>(v2SubjectCards[id]&&v2SubjectCards[id][date])||null;
    const v2SubjectCardShorts=(row,lang)=>((row&&row.suitable)||[]).map(s=>s.subject_short&&(s.subject_short[lang]||s.subject_short['zh-TW'])).filter(Boolean);
    const v2SubjectCardShortReason=(row,lang)=>row&&row.dominant_reason?(row.dominant_reason[lang]||row.dominant_reason['zh-TW']||''):'';
    const v2GeneralBaseline=row=>{const gb=row&&row.general_baseline;return (gb&&typeof gb.ok==='boolean')?gb:null;};
    const localDateString=(tz,off)=>dayDate;
    let dayDate=${JSON.stringify(dayDate)};
    const selectedDayOffset=()=>0;
    const localNowMinutes=()=>0;
    const v2RemainingHoursList=(times)=>(times||[]).filter(t=>/^([01]\\d|2[0-3]):[0-5]\\d$/.test(String(t||'')));
    const v2NextWindowLocal=()=>'';
    const v2LocalNow=()=>null;
    const nextWindowStamp=s=>s;
    const clui82PlainWeather=()=>'';
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({'v2_quick_title':'現在去會怎樣','v2_quick_none':'尚無速覽資料','v2_quick_next':'下一個符合時刻：',
      'v2_tier_recommend':'✓ 推薦','v2_tier_shootable':'○ 可拍','v2_tier_not_recommended':'✗ 不宜',
      'eval2_hours':'符合時數','eval2_ok':'符合','eval2_bad':'未符','eval2_unk':'資料不足'});
    const listSep=()=>'、';
    const formatHourSegments=list=>(list||[]).join('、');
    const compactHourSegmentsText=text=>String(text||'').split('、').map(seg=>seg.includes('–')?seg.replace(/:00/g,''):seg).join('、');
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
    const v2BestForSpot=null;
    const v2HourSubjectCell=()=>({kind:'na'});
  `;
  const quickOf = (dayDate, cards, spot, place) => new Function(
    makePrelude(dayDate, cards) + helperCode + ';return {v2QuickViewHtml};')().v2QuickViewHtml(spot, place);
  const strip = h => h.replace(/<[^>]*>/g, '');

  // ○可拍+tier_reason (the 汐止翠湖 single-truth case): the chip reads the
  // CARD's tier (row.tier + tier_reason) — the old status:'failed'→✗短因
  // read would contradict the card.
  const mid = anchorDate.mid;
  const midHtml = quickOf(mid.dt, artifact.places, {spot_id: mid.pid, timezone: 'Asia/Taipei'}, null);
  assert.ok(midHtml.includes('data-tier="mid"'), 'shootable row → mid tier chip: ' + midHtml);
  assert.ok(midHtml.includes('○ 可拍'), 'chip carries the card tier word');
  assert.ok(midHtml.includes('窗已過'), 'chip carries row.tier_reason');
  assert.ok(!midHtml.includes('✗'), 'never renders the ✗ status-level miss against the card tier');
  assert.ok(!midHtml.includes('低雲'), 'subject-level short reason left the quick panel');
  assert.ok(midHtml.includes('q-t') && midHtml.includes('現在去會怎樣'), 'panel title = 現在去會怎樣 · M/D');

  // ✓推薦: chip + the row's own next matching moment (time + subject).
  const rec = anchorDate.rec;
  const recRow = artifact.places[rec.pid][rec.dt];
  const recHtml = quickOf(rec.dt, artifact.places, {spot_id: rec.pid, timezone: 'Asia/Taipei'}, null);
  assert.ok(recHtml.includes('data-tier="ok"') && recHtml.includes('✓ 推薦'), 'recommend row → ok chip');
  const stamps = [...new Set((recRow.suitable || []).flatMap(s => (s && s.window) || []))]
    .filter(w => /^([01]\d|2[0-3]):[0-5]\d$/.test(String(w || '')));
  if (stamps.length) {
    const first = stamps[0];
    assert.ok(recHtml.includes('q-next') && recHtml.includes('q-w'), 'next matching moment line');
    assert.ok(recHtml.includes(`>${first}<`), 'next moment uses the row window stamp ' + first);
    const nm = (recRow.suitable || []).map(s => s.subject_short && (s.subject_short['zh-TW'] || '')).filter(Boolean)[0];
    if (nm) assert.ok(recHtml.includes(nm), '「16:25 山景」式: moment + subject name');
  }

  // ✗不宜: chip = ✗不宜·短因 (card tier truth), never a bare invented cause.
  const bad = anchorDate.bad;
  const badHtml = quickOf(bad.dt, artifact.places, {spot_id: bad.pid, timezone: 'Asia/Taipei'}, null);
  assert.ok(badHtml.includes('data-tier="bad"') && badHtml.includes('✗ 不宜'), 'not_recommended row → bad chip');
  assert.ok(!/[。！？，]/.test(strip(badHtml).replace('✗', '')),
    'quick view never carries a long sentence: ' + badHtml);

  // A row WITHOUT tier/dominant_reason degrades to the honest none-line —
  // never an invented cause. (CL-INT-154: injected synthetically instead of
  // pinning live data; CL-CI-36: the injected day sits outside the refresh
  // window so the anchor can never collide with a real refreshed row.)
  const synthTree = Object.assign({}, artifact.places, {
    'xx-000': {'2099-01-01': {status: 'failed', suitable: []}}});
  const failedHtml = quickOf('2099-01-01', synthTree, {spot_id: 'xx-000', timezone: 'UTC'}, null);
  assert.ok(failedHtml.includes('quick-none'), 'a rowless verdict degrades honestly');

  // No row at all: honest none-line (never invented copy).
  const noneHtml = quickOf(anchorDate.mid.dt, artifact.places, {spot_id: 'xx-999', timezone: 'UTC'}, null);
  assert.ok(noneHtml.includes('quick-none'));
});

test('CL-UI-68 (3): 8-day strip — info written INSIDE the cell (two lines), no hover/title carrier', () => {
  const helperCode = grab('function v2MetricName', '// CL-COPY-01: handwritten')
    + grab('function v2DominantFailMetric', 'function ensureV2Detail');
  const prelude = `
    const V2_EVAL_METRICS={'zh-TW':{precipitation:'降水',visibility:'能見度',cloud_cover_low:'低雲'},en:{},ja:{}};
    const V2_FAIL_PRIORITY=['precipitation','visibility','cloud_cover_low'];
    let currentLang='zh-TW';
    let v2SubjectCards={};
    const v2SubjectCardRow=()=>null;
    const v2SubjectCardShortReason=()=>'';
    const v2SubjectCardShorts=()=>[];
    const localDateString=()=>'2026-11-13';
    const selectedDayOffset=()=>0;
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足'});
    const listSep=()=>'、';
    const formatHourSegments=list=>(list||[]).join('、');
    const compactHourSegmentsText=text=>String(text||'').split('、').map(seg=>seg.includes('–')?seg.replace(/:00/g,''):seg).join('、');
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
    const v2BestForSpot=null;
  `;
  const fns = new Function(prelude + helperCode +
    ';return {v2QuickViewHtml,v2DayStripHtml,v2ShortReasonWord,v2DominantFailMetric};')();
  const days = [
    {local_date: '2026-11-13', state: 'GUIDANCE_SATISFIED', good_hours: ['17:00'], conditions: []},
    {local_date: '2026-11-14', state: 'UNFAVORABLE', good_hours: [], conditions: [
      {metric: 'precipitation', day_verdict: 'FAIL'}]},
    {local_date: '2026-11-15', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
  ];
  const html = fns.v2DayStripHtml(days, ['今天', '明天', '後天'], 'Asia/Taipei', {spot_id: 'jp-003'}, 'cloud_sea', 'jp-003-P01');
  const cells = html.match(/<button[\s\S]*?<\/button>/g) || [];
  assert.equal(cells.length, 3, 'one cell per day row');
  assert.ok(html.includes('v2-ok') && html.includes('v2-bad') && html.includes('v2-unk'));
  assert.ok(html.includes('data-reason="降水"'), 'short reason word on the failed cell');
  // CL-UI-68: the text lives INSIDE the cell — CL-UI-75 compact copy:
  // met = ✓n qualifying-hours badge + abbreviated window, unmet = ✗short
  // reason, unknown = the honest label. No hover/title carrier, no
  // click-to-reveal note, no 🎯 badge (CL-UI-75 owner ruling).
  // CL-UI-125 (owner ruling): a met cell is ONE check mark — no hour count and
  // no hour list underneath (06–08 + 10–14 has no honest one-line form).
  assert.ok(html.includes('<span class="v2-strip-mark" aria-hidden="true">✓</span>'),
    'met cell: a single check mark');
  assert.ok(!html.includes('v2-strip-hours'), 'no ✓n badge on any cell');
  assert.ok(!html.includes('<span class="v2-strip-text">17:00</span>'),
    'no hour stamp under a met cell');
  assert.ok(html.includes('<span class="v2-strip-text">✗降水</span>'),
    'unmet cell text: ✗short reason');
  assert.ok(html.includes('<span class="v2-strip-text">資料不足</span>'),
    'unknown cell text: the honest label');
  // CL-UI-88 re-anchor (owner defect fix): the cell keeps the compact copy
  // visible and the FULL wording rides the tooltip (title=) beside the
  // aria-label parity copy — hover is supplementary, never the only carrier.
  assert.ok(html.includes('title='), 'the full segments ride the cell tooltip');
  assert.ok(html.includes('aria-label='), 'aria parity copy intact');
  assert.ok(!html.includes('v2-strip-note') && !html.includes('v2-strip-bar'),
    'click-to-reveal note and bare color bar retired');
  assert.ok(!html.includes('🎯') && !html.includes('v2-strip-next'),
    'CL-UI-75: the 🎯 next-window badge is retired at every breakpoint');
  // decorateV2Eval no longer wires a click -> note reveal.
  assert.ok(!appSource.includes("el.querySelectorAll('.v2-strip-cell').forEach(cell=>cell.addEventListener('click'"));
  // The modal no longer renders the 8 long day rows.
  assert.ok(!appSource.includes('v2DayHtml(day,labels[i]||day.local_date'));
});

test('CL-UI-64 (4): 拍攝條件/成立條件 collapses into an accordion (default closed, 條件 ×N)', () => {
  // CL-APP-09 patch-4: the fold markup lives in the SHARED v2CondFoldHtml
  // builder (panel + private-point popup render through it), so the pins
  // anchor there — the summary count still uses the i18n key.
  const fold = grab('function v2CondFoldHtml', 'function openPlaceModal');
  assert.match(fold, /<details class="v2-cond-details"><summary class="v2-cond-summary">\$\{esc\(t\.v2_cond_count\)\.replace\('\{n\}',String\(v2CondCount\)\)\}/);
  // Default collapsed: the markup never opens the details.
  assert.ok(!/<details class="v2-cond-details"[^>]*open/.test(appSource));
  assert.match(fold, /const v2CondCount=list\.length;/);
  // The long metric narrative (v2-why) stays inside the accordion.
  assert.ok(appSource.includes('v2-why'), 'why-lines remain in the collapsed layer');
  assert.ok(fold.includes('</details>'));
  // The place panel still renders the fold through the shared builder.
  assert.match(appSource, /const v2CondHtml=v2CondFoldHtml\(v2c\?v2c\.conditions:null\);/);
});

test('CL-UI-64 (5): bottom hourly-forecast control stays on-page (CL-UI-79 owner ruling)', () => {
  // CL-UI-79: the control is a BUTTON, not an anchor — it must never
  // navigate away to weather-map.html. It opens the same-page weather
  // forecast modal for this place (or smooth-scrolls to a future in-modal
  // hourly table).
  assert.doesNotMatch(appSource, /<a class="place-hourly-link"/);
  assert.doesNotMatch(appSource, /place-hourly-link"[^>]*href=/);
  assert.match(appSource, /<button type="button" class="place-hourly-link" id="place-hourly-btn" data-spot-id="\$\{esc\(spot\.spot_id\|\|''\)\}">/);
  assert.match(appSource, /\$\{esc\(d\(\)\.v2_hourly_link\)\}/);
  const handler = grab("if(hourlyBtn)hourlyBtn.addEventListener('click'", "decorateV2Eval(spot)");
  assert.ok(handler.includes('openWeatherModal(latest'), 'fallback opens the same-page forecast modal');
  assert.ok(handler.includes("scrollIntoView({behavior:'smooth'"), 'in-modal table preference: smooth scroll');
  const modalBlock = grab('function openPlaceModal(spot,summaryMetric){', 'function syncModalScrollLock()');
  assert.ok(!modalBlock.includes('weather-map.html'), 'no navigation to weather-map from the place modal');
});

test('CL-UI-64 (6): i18n keys exist in all three dictionaries', () => {
  for (const key of ['v2_quick_title', 'v2_quick_none', 'v2_quick_next', 'v2_ds_label',
    'v2_ds_none', 'v2_ds_next', 'v2_ds_nonext', 'v2_ds_ok_today',
    'v2_cond_count', 'v2_hourly_link']) {
    const count = appSource.split(key + ':').length - 1;
    assert.equal(count, 3, key + ' must exist in zh-TW/en/ja');
  }
  assert.match(appSource, /v2_quick_title:'現在去會怎樣'/);
  assert.match(appSource, /v2_quick_title:'If I go now'/);
  assert.match(appSource, /v2_quick_title:'今すぐ行くと'/);
  assert.match(appSource, /v2_hourly_link:'查看逐小時預報 →'/);
});

test('CL-UI-64 (7): shell styles + 390px mobile rules + cache-bust stamp bumped', () => {
  for (const cls of ['.place-quick-view', '.q-chip', '.q-next', '.v2-day-strip',
    '.v2-strip-cell', '.v2-strip-text', '.v2-strip-mark', '.v2-cond-details',
    '.v2-cond-details[open]', '.place-hourly-link']) {
    assert.ok(appCss.includes(cls), 'css missing ' + cls);
  }
  // CL-UI-95: the retired status-level chip classes are gone repo-wide.
  assert.ok(!appCss.includes('.quick-chip') && !appCss.includes('.quick-miss') && !appCss.includes('.quick-window'),
    'CL-UI-95: quick-chip/quick-miss/quick-window CSS retired with the status read');
  // CL-UI-75: the strip is ONE horizontal row of cells that scrolls
  // horizontally at 390px — no wrap tier, no vertical one-char reflow; the
  // 🎯 badge CSS is retired with the badge.
  // CL-UI-88 re-anchor (owner defect fix): the fixed 46px cell + in-cell
  // ellipsis tier is retired — cells are content-sized and the slot string
  // is never truncated at any width.
  assert.ok(appCss.includes('@media (max-width:390px)'), '390px tier present');
  assert.ok(!appCss.includes('.v2-strip-bar') && !appCss.includes('.v2-strip-note'),
    'bare bar / note CSS retired');
  assert.ok(!appCss.includes('.v2-strip-next') && !appCss.includes('🎯'),
    'CL-UI-75: next-window badge CSS retired');
  assert.match(appCss, /\.v2-day-strip\{[^}]*grid-auto-flow:column/);
  assert.match(appCss, /\.v2-day-strip\{[^}]*overflow-x:auto/);
  assert.ok(!/(?<!min-)width:46px/.test(appCss), 'CL-UI-88: the fixed 46px cell tier is retired');
  const stripTextRule = appCss.match(/\.v2-strip-text\{[^}]*\}/g) || [];
  assert.ok(stripTextRule.length >= 1, '.v2-strip-text rule present');
  for (const rule of stripTextRule) {
    assert.ok(!rule.includes('text-overflow:ellipsis') && !rule.includes('overflow:hidden'),
      'CL-UI-88: the slot string is never ellipsis-truncated: ' + rule);
  }
  assert.match(indexSource, /assets\/app\.js\?v=clui141/);
  assert.match(indexSource, /assets\/app\.css\?v=clui141/);
});
