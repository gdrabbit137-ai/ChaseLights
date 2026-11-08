// CL-UI-26: plain-language dominant fail reason on 不符 cards and modal day
// rows. Source assertions plus extracted pure helpers, per the established
// test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const grab=(start,end)=>{const i=appSource.indexOf(start);return appSource.slice(i,appSource.indexOf(end,i));};
const failCode=grab('const V2_FAIL_PRIORITY','// CL-UI-12: day0 (today) qualifying hours');
const makeFns=lang=>new Function(`let currentLang=${JSON.stringify(lang)};\n${failCode}\nconst v2PlaceForSpot=()=>null;\nreturn {v2DominantFailReason,v2FailReasonSuffix};`)();

const rainDay={state:'UNFAVORABLE',conditions:[
  {metric:'cloud_cover_mid',day_verdict:'FAIL'},
  {metric:'precipitation',day_verdict:'FAIL'},
  {metric:'sunset_window',day_verdict:'FAIL'}]};
const hazeDay={state:'UNFAVORABLE',conditions:[
  {metric:'aod_550nm',day_verdict:'FAIL'},
  {metric:'wind_speed_10m',day_verdict:'FAIL'}]};
const windowDay={state:'UNFAVORABLE',conditions:[{metric:'blue_hour_window',day_verdict:'FAIL'}]};

test('CL-UI-26 (1): dominant reason picks the strongest failing metric, not a list',()=>{
  const zh=makeFns('zh-TW');
  assert.equal(zh.v2DominantFailReason(rainDay.conditions),'下大雨視線不清');
  assert.equal(zh.v2DominantFailReason(hazeDay.conditions),'空氣霧霾嚴重，看不清楚');
  assert.equal(zh.v2DominantFailReason(windowDay.conditions),'需藍調時段');
  // visibility beats low cloud in the priority order.
  assert.equal(zh.v2DominantFailReason([
    {metric:'cloud_cover_total',day_verdict:'FAIL'},
    {metric:'visibility',day_verdict:'FAIL'}]),'大霧看不到');
  // Only day_verdict FAIL/PARTIAL conditions count; PASS/UNKNOWN is never a reason.
  assert.equal(zh.v2DominantFailReason([{metric:'precipitation',day_verdict:'PASS'}]),null);
  assert.equal(zh.v2DominantFailReason([{metric:'precipitation',day_verdict:'UNKNOWN'}]),null);
  assert.equal(zh.v2DominantFailReason([{metric:'precipitation',day_verdict:'PARTIAL'}]),'下大雨視線不清');
  assert.equal(zh.v2DominantFailReason([]),null);
  assert.equal(zh.v2DominantFailReason(null),null);
});

test('CL-UI-26 (2): reason strings exist and stay equivalent in zh-TW/en/ja',()=>{
  const keySets=['zh-TW','en','ja'].map(lang=>Object.keys(makeFns(lang).v2DominantFailReason===undefined?{}:new Function(`let currentLang='${lang}';\n${grab('const V2_FAIL_PRIORITY','// CL-UI-12: day0 (today) qualifying hours')}\nreturn V2_FAIL_REASONS;`)()).sort().join(','));
  assert.equal(keySets[0],keySets[1],`en keys: ${keySets[1]}`);
  assert.equal(keySets[0],keySets[2],`ja keys: ${keySets[2]}`);
  const en=makeFns('en');
  assert.match(String(en.v2DominantFailReason(rainDay.conditions)),/[Rr]ain/);
  const ja=makeFns('ja');
  const jaRain=ja.v2DominantFailReason(rainDay.conditions);
  assert.ok(jaRain.includes('大雨')||jaRain.includes('雨'),'ja rain reason: '+jaRain);
  // ja copy carries zero simplified-han characters (視界/霧/霞 are ja kanji).
  assert.equal(/(题|视|湿|风)/.test(jaRain),false);
});

test('CL-UI-26 (3): card state row appends the dominant known failure reason',()=>{
  const zh=makeFns('zh-TW');
  const bestRain={state:'UNFAVORABLE',day:rainDay};
  assert.equal(zh.v2FailReasonSuffix(bestRain,null),' · 下大雨視線不清');
  // CL-UI-33: a NOT_EVALUABLE day with a KNOWN failing condition still names
  // it — only a genuinely unknown day stays silent (資料不足).
  const bestUnk={state:'NOT_EVALUABLE',day:rainDay};
  assert.equal(zh.v2FailReasonSuffix(bestUnk,null),' · 下大雨視線不清');
  // A NOT_EVALUABLE day with no known fail at all keeps the honest silence.
  const unknownDay={state:'NOT_EVALUABLE',conditions:[{metric:'cloud_cover_low',day_verdict:'UNKNOWN'},{metric:'precipitation',day_verdict:'PASS'}]};
  assert.equal(zh.v2FailReasonSuffix({state:'NOT_EVALUABLE',day:unknownDay},null),'');
  assert.equal(zh.v2FailReasonSuffix({state:'GUIDANCE_SATISFIED',day:rainDay},null),'');
  assert.equal(zh.v2FailReasonSuffix(null,null),'');
  // Render path consumes the helper in the card state row (CL-UI-50: on a
  // NOT_EVALUABLE day the suffix is used instead of repeating the label).
  assert.match(appSource,/esc\(v2StateLabel\)\+esc\(v2FailReasonSuffix\(v2Best,spot\)\)/);
  assert.match(appSource,/v2Best\.state==='NOT_EVALUABLE'\?\(v2NotEvalReason\?esc\(d\(\)\[v2NotEvalReason\]\):esc\(v2FailReasonSuffix\(v2Best,spot\)\)\)/);
  // The winning day row is carried on the best object so card and day share
  // one source of conditions, plus the context genre.
  assert.match(appSource,/oppDays:o\.days\|\|\[\],day,genre:o\.genre_template/);
});

test('CL-UI-26 (4): modal day rows name the dominant reason instead of a metric list',()=>{
  assert.match(appSource,/const failReason=\(day\.state!=='GUIDANCE_SATISFIED'\)\?v2DominantFailReason\(day\.conditions,spot,genre,opportunityId\):null;/);
  assert.match(appSource,/\$\{esc\(d\(\)\.v2_fail_reason\)\}\$\{esc\(failReason\)\}/);
  // The honest NOT_EVALUABLE mapping is untouched in the day-row renderer.
  assert.match(appSource,/day\.state==='NOT_EVALUABLE'\?d\(\)\.eval2_unk/);
});

test('CL-UI-26 (5): the v2_fail_reason label exists in all three dictionaries',()=>{
  for(const lang of ['zh-TW','en','ja']){
  assert.match(appSource,new RegExp(`v2_fail_reason:'[^']+'`),'i18n key for '+lang);
  }
  assert.match(appSource,/v2_fail_reason:'未符原因：'/);
  assert.match(appSource,/v2_fail_reason:'Reason: '/);
  assert.match(appSource,/v2_fail_reason:'未達成の理由：'/);
});

test('CL-UI-32: low-cloud fail reason copy pinned in all three languages',()=>{
  const reasons=lang=>new Function('let currentLang='+JSON.stringify(lang)+';\n'+failCode+'\nreturn V2_FAIL_REASONS;')()[lang];
  assert.equal(reasons('zh-TW').cloud_cover_low,'低雲太厚，山頭沒入雲中');
  assert.equal(reasons('en').cloud_cover_low,'Low cloud swallows the peak');
  assert.equal(reasons('ja').cloud_cover_low,'低層雲が厚く、山頂が雲に埋もれます');
  // ja copy carries zero simplified-han characters.
  assert.equal(/(题|视|湿|风)/.test(reasons('ja').cloud_cover_low),false);
  // Sibling cloud copy stays distinct: mid/total are generic visibility, LCL is the
  // cloud-sea metric, low cloud names the engulfed peak.
  const zh=reasons('zh-TW');
  assert.equal(zh.cloud_cover_mid,'雲層太厚，看不到');
  assert.equal(zh.cloud_cover_total,'雲層太厚，看不到');
  assert.equal(zh.lcl_height_m_agl,'雲底太低，容易身處雲中');
  assert.notEqual(zh.cloud_cover_low,zh.cloud_cover_mid);
});

test('CL-UI-26 (6): cache-bust stamp bumped for the edited app.js',()=>{
  const index=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
  assert.match(index,/assets\/app\.js\?v=clui55/);
  assert.match(index,/assets\/app\.css\?v=clui53/);
});
