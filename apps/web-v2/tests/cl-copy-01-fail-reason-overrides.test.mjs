// CL-COPY-01: handwritten per-opportunity×metric fail-reason overrides.
// Covers (1) lookup order — handwritten entry wins, mechanical map is the
// honest fallback when no entry exists (behavior unchanged); (2) coverage —
// every tw opportunity whose contract has evaluable metrics has entries;
// (3) showcase lines; (4) ja lines use Japanese-standard kanji (no simplified
// hanzi).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
const grab = (start, end) => {
  const i = appSource.indexOf(start);
  return appSource.slice(i, appSource.indexOf(end, i));
};
const failCode = grab('const V2_FAIL_PRIORITY', '// CL-UI-12: day0 (today) qualifying hours');

const makeFns = (lang, overrides) => {
  const ov = overrides ? `v2FailOverrides=${JSON.stringify(overrides)};` : 'v2FailOverrides=null;';
  return new Function(`let currentLang=${JSON.stringify(lang)};\n${ov}\n${failCode}\nreturn {v2DominantFailReason};`)();
};

const lowCloudDay = {conditions: [{metric: 'cloud_cover_low', day_verdict: 'FAIL'}]};
const lclDay = {conditions: [{metric: 'lcl_height_m_agl', day_verdict: 'FAIL'}]};
const here = dirname(fileURLToPath(import.meta.url));
const overridesPath = join(here, '..', '..', '..', 'data', 'v2', 'copy', 'fail_reason_overrides.json');
const oppDir = join(here, '..', '..', '..', 'data', 'v2', 'opportunities');

test('CL-COPY-01 (1a): lookup order — overrides[oppId][metric] first, fallback on miss', () => {
  const overrides = {'tw-003-P01': {'cloud_cover_low': {
    'zh-TW': '低雲太厚，碼頭與水面灰成一片',
    'en': 'Thick low cloud turns the wharf and the water into one grey mass',
    'ja': '低層雲が厚く、桟橋も水面も灰色に沈みます'}}};
  const zh = makeFns('zh-TW', overrides);
  assert.equal(zh.v2DominantFailReason(lowCloudDay.conditions, null, null, 'tw-003-P01'), '低雲太厚，碼頭與水面灰成一片');
  // same metric, different opportunity → honest mechanical fallback (mountain context keeps the peak wording)
  assert.equal(zh.v2DominantFailReason(lowCloudDay.conditions, null, 'mountain_view', 'tw-999-P01'), '低雲太厚，山頭沒入雲中');
  // same opportunity, unlisted metric → mechanical fallback
  assert.equal(zh.v2DominantFailReason(lclDay.conditions, null, null, 'tw-003-P01'), '雲底太低，容易身處雲中');
  // no opportunityId at all → behavior unchanged
  assert.equal(zh.v2DominantFailReason(lowCloudDay.conditions, null, 'mountain_view'), '低雲太厚，山頭沒入雲中');
  // en/ja use their own language entry
  const en = makeFns('en', overrides);
  assert.equal(en.v2DominantFailReason(lowCloudDay.conditions, null, null, 'tw-003-P01'), 'Thick low cloud turns the wharf and the water into one grey mass');
  const ja = makeFns('ja', overrides);
  assert.equal(ja.v2DominantFailReason(lowCloudDay.conditions, null, null, 'tw-003-P01'), '低層雲が厚く、桟橋も水面も灰色に沈みます');
});

test('CL-COPY-01 (1b): overrides load failure keeps behavior unchanged', () => {
  const zh = makeFns('zh-TW', null);
  assert.equal(zh.v2DominantFailReason(lowCloudDay.conditions, null, 'mountain_view', 'tw-003-P01'), '低雲太厚，山頭沒入雲中');
});

test('CL-COPY-01 (2): coverage — every tw opportunity with evaluable contract metrics has entries', () => {
  const overrides = JSON.parse(readFileSync(overridesPath, 'utf8'));
  const EVAL = new Set(['precipitation', 'visibility', 'aod_550nm', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_mid_and_high', 'cloud_cover_total', 'wind_speed_10m', 'lcl_height_m_agl', 'relative_humidity_925hpa', 'relative_humidity_700hpa', 'relative_humidity_600hpa', 'relative_humidity_850hpa', 'galactic_core_altitude', 'sunrise_time_window', 'sunset_window', 'golden_hour_window', 'blue_hour_window', 'city_night_window', 'light_window', 'astronomical_darkness', 'moon_illumination_fraction', 'moon_illuminance_proxy', 'moon_altitude', 'moon_target_separation_deg', 'wind_speed_850hpa', 'wind_speed_600hpa', 'temperature_delta_850_925_c', 'temperature_delta_700_600_c', 'water_surface_state', 'seasonal_state', 'river_flow_state', 'landform_present']);
  let evaluable = 0, covered = 0, entries = 0;
  const missing = [];
  for (const f of readdirSync(oppDir).filter(f => f.startsWith('tw-'))) {
    const d = JSON.parse(readFileSync(join(oppDir, f), 'utf8'));
    const ms = (((d.condition_contract || {}).conditions) || []).map(c => c.metric).filter(m => EVAL.has(m));
    if (!ms.length) continue;
    evaluable++;
    if (overrides[d.opportunity_id] && ms.every(m => overrides[d.opportunity_id][m])) covered++;
    else missing.push(d.opportunity_id);
    for (const m of Object.keys(overrides[d.opportunity_id] || {})) entries++;
  }
  assert.equal(evaluable, covered, `uncovered: ${missing.join(',')}`);
  assert.ok(entries >= 800, `tw handwritten entries ${entries} (expect >= 800)`);
});

test('CL-COPY-01 (3): showcase lines exist (漁人碼頭 low cloud / 大屯山雲海 LCL / 象山 night window)', () => {
  const overrides = JSON.parse(readFileSync(overridesPath, 'utf8'));
  assert.equal(overrides['tw-003-P01'].cloud_cover_low['zh-TW'], '低雲太厚，碼頭與水面灰成一片');
  assert.equal(overrides['tw-001-P02'].lcl_height_m_agl['zh-TW'], '雲底太高，盆地裡沒有雲海');
  assert.equal(overrides['tw-002-P02'].city_night_window['zh-TW'], '還沒暗到夜景好看');
  for (const id of ['tw-003-P01', 'tw-001-P02', 'tw-002-P02']) {
    for (const m of Object.keys(overrides[id])) {
      const e = overrides[id][m];
      for (const lang of ['zh-TW', 'en', 'ja']) assert.ok(e[lang], `${id}.${m}.${lang} present`);
    }
  }
});

test('CL-COPY-01 (4): ja lines contain zero simplified-form hanzi', () => {
  const overrides = JSON.parse(readFileSync(overridesPath, 'utf8'));
  const seen = new Set();
  for (const id of Object.keys(overrides)) {
    for (const m of Object.keys(overrides[id])) {
      const e = overrides[id][m];
      for (const lang of ['zh-TW', 'en', 'ja']) assert.ok(e[lang], `${id}.${m}.${lang} present`);
      seen.add(e.ja);
    }
  }
  // Simplified forms that must never leak into Japanese copy.
  const bad = '汉济证没汇银时后风关辉乐坚图圆场宫实宁宝对导恶战户扩择摊据权无词说谈论员阅简环让农动华变单贝车马龙鸟点发电东蓝难';
  for (const t of seen) for (const ch of bad) assert.ok(!t.includes(ch), `simplified '${ch}' leaked into: ${t}`);
});
