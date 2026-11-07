// CL-UI-44: the weather-modal astronomy cell is field-driven — any hour with
// solar azimuth/elevation shows it (all-day subjects no longer render a
// black-box ※); a genuinely missing field degrades to a NAMED missing marker.
// Extracted-function tests over the shipped assets/app.js helpers (no DOM
// harness in the V1 shell), same approach as CL-UI-12/13/14.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));
const factory=new Function([
  grab('const i18nDict','const categoryKeys'),
  "let currentLang='zh-TW';const d=()=>i18nDict[currentLang]||i18nDict['zh-TW'];",
  grab('function esc','const OPPORTUNITY_NEGATIVE_STATUS_KEYS'),
  grab('function astroText','// CL-UI-14: timezone labels'),
  grab('const VIS_CAP_KM','// CL-UI-14/F1: the modal'),
  'return {astroText,astroMissingHtml,astroMissingTitle};'
].join('\n'));
const {astroText,astroMissingHtml,astroMissingTitle}=factory();

// ---- CL-UI-44: field-driven astronomy cell ----

test('CL-UI-44: the astronomy cell is field-driven — all-day subjects show sun data, not ※',()=>{
  const hour={astronomy_valid:true,sun_azimuth:99.5,sun_elevation:-13.2,moon_illumination:11.7,galactic_core_azimuth:80.1,galactic_core_elevation:-54.2};
  // All-day subjects (previously a bare ※) now show the solar geometry.
  for(const theme of ['mountain_view','cloud_sea','overcast_soft','sunrise','sunset','blue_hour','sky_glow']){
    assert.equal(astroText(hour,theme),'☀️ 100° / -13°');
  }
  // Niche extras are preserved.
  assert.equal(astroText(hour,'milky_way'),'☀️ 100° / -13° · 🌙 12% · 🌌 80° / -54°');
  assert.equal(astroText({...hour,kp:5},'aurora'),'☀️ 100° / -13° · 🌌 Kp 5');
  // astronomy_valid=false no longer hides real fields.
  assert.equal(astroText({...hour,astronomy_valid:false},'mountain_view'),'☀️ 100° / -13°');
  // Truly missing data → empty text + a NAMED missing marker.
  const bare={astronomy_valid:false,sun_azimuth:null,sun_elevation:null};
  assert.equal(astroText(bare,'mountain_view'),'');
  assert.match(astroMissingHtml(bare,true),/缺太陽方位／仰角資料/);
  assert.match(astroMissingTitle(bare,true),/缺太陽方位\/仰角資料|缺太陽方位／仰角資料/);
  // Non-hour callers keep the generic honest wording.
  assert.match(astroMissingHtml({},false),/該時段無天文資料/);
  // Trilingual named-missing wording.
  assert.ok(appSource.includes("astro_missing_sun:'缺太陽方位／仰角資料'"));
  assert.ok(appSource.includes("astro_missing_sun:'Missing sun azimuth/elevation data'"));
  assert.ok(appSource.includes("astro_missing_sun:'太陽の方位角・高度データなし'"));
  // The whitelist is gone from the source.
  assert.ok(!appSource.includes("['sunrise','sunset','sky_glow','blue_hour'].includes(theme)"));
});
