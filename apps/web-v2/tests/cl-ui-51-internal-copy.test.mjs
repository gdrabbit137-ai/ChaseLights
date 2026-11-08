// CL-UI-51: internal-engineering terminology must never reach the user-facing
// place modal. Two defects fixed in the V1 shell (repo-root assets/app.js):
// (1) condition rationale_i18n carries audit provenance (ticket ids like
//     CL-DATA-19, spot ids like tw-062-P01, gate/evaluator terms like
//     layering parity gate / propagate_unknown / legacy_long_exposure, and
//     audit-log narrative) and was rendered verbatim into the modal's 說明
//     rows — v2PublicRationale now filters it at the render boundary;
// (2) the modal's 「下一個符合時段」 trusted the bundle's live.next_good even
//     when the opportunity's own day rows disagreed (芹壁: next window
//     advertised 16:00 while the same day's qualifying hours started 16:30).
//     The fallback is now corroborated against the day rows before display.
// No DOM harness exists for the V1 shell, so this suite combines
// extracted-function tests with source assertions (CL-UI-12/13 approach).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

// Extract the shipped pure helpers and run them for real. localeText is
// stubbed with the same first-preference fallback the shell uses.
const factory=new Function([
  grab('function v2RemainingHoursList','function v2EffectiveHours'),
  grab('function v2ParseLocalStamp','function v2LocalNow'),
  grab('const V2_INTERNAL_COPY_RE','function v2NextWindowLocal'),
  grab('function v2NextWindowLocal','function v2BestForSpot'),
  'const i18nDict={};',
  'function localeText(i18n){if(!i18n)return"";return i18n["zh-TW"]||i18n.en||i18n.ja||"";}',
  'return {v2PublicRationale,v2NextWindowLocal};'
].join('\n'));
const {v2PublicRationale,v2NextWindowLocal}=factory();

const day=(date,hours)=>({local_date:date,good_hours:hours});
const now=d=>({date:d[0],minutes:d[1]});

test('CL-UI-51 (a): rationale containing internal ticket/audit wording is withheld',()=>{
  // 東引燈塔-style light_window audit annotation.
  const audit='2026-11-06 CL-DATA-19 全面稽查：中緯度全日題材補 light_window（civil，太陽仰角 > −6°，CL-DATA-11 同源定義；夜間一律不符合）。得月樓（tw-062-P01）抽查實證。本筆為語意修正，layering parity gate 豁免。';
  assert.equal(v2PublicRationale({'zh-TW':audit}), '');
  assert.equal(v2PublicRationale({en:'2026-11-06 CL-DATA-19 full audit: adds light_window (tw-062-P01); layering parity gate exempt.'}), '');
  assert.equal(v2PublicRationale({ja:'2026-11-06 CL-DATA-19 全面監査：light_window を追加。layering parity ゲートは免除。'}), '');
});

test('CL-UI-51 (b): evaluator/gate terminology is withheld in every language',()=>{
  for(const t of ['propagate_unknown 保底','legacy_long_exposure 判據','parity gate 豁免']){
    assert.equal(v2PublicRationale({'zh-TW':t}),'');
  }
});

test('CL-UI-51 (c): a parenthetical that only cross-references another spot id is dropped, the rest is kept',()=>{
  const kept=v2PublicRationale({'zh-TW':'拍攝受雨影響；0.3 mm/h 以下視為不受影響（與 tw-036-P01 相同門檻）。'});
  assert.equal(kept,'拍攝受雨影響；0.3 mm/h 以下視為不受影響。');
  const keptEn=v2PublicRationale({en:'Rain interferes with shooting; below 0.3 mm/h is fine (same as tw-036-P01).'});
  assert.equal(keptEn,'Rain interferes with shooting; below 0.3 mm/h is fine.');
});

test('CL-UI-51 (d): clean photographer-facing copy passes through untouched',()=>{
  const clean='低雲在太陽方位扇形內會直接擋住落日；55% 仍允許塊狀雲，雲塊反而是上色主角。';
  assert.equal(v2PublicRationale({'zh-TW':clean}),clean);
  assert.equal(v2PublicRationale({}), '');
  assert.equal(v2PublicRationale(null), '');
});

test('CL-UI-51 (e): wiring — the modal 說明 row renders only filtered rationale',()=>{
  const condBlock=grab('const v2Groups=v2c?','if(c.role===\'REQUIRED\')');
  assert.match(condBlock,/v2PublicRationale\(c\.rationale_i18n\)/);
  // The raw localeText(c.rationale_i18n) render is gone.
  assert.doesNotMatch(condBlock,/v2-why">\$\{esc\(localeText\(c\.rationale_i18n\)\)\}/);
  // A withheld rationale renders no 說明 line at all (never an empty one).
  assert.match(condBlock,/why\?`<div class="v2-why">/);
});

test('CL-UI-51 (f): next-window fallback must be corroborated by the day rows (芹壁 16:00 vs 16:30)',()=>{
  // The live bundle advertised next_good 16:00 on a day whose good_hours
  // start at 16:30 — the day-scan result must win.
  const rows=[day('2026-11-08',[]),day('2026-11-11',['16:30'])];
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-08',10*60]),'2026-11-11 16:00'),'2026-11-11 16:30');
  // A corroborated, still-future fallback still passes through untouched.
  assert.equal(v2NextWindowLocal(rows,now(['2026-11-08',10*60]),'2026-11-11 16:30'),'2026-11-11 16:30');
  // Today-case: a corroborated remaining hour passes; a contradicting one
  // falls back to the remaining-hours scan.
  const rows2=[day('2026-11-08',['17:00'])];
  assert.equal(v2NextWindowLocal(rows2,now(['2026-11-08',15*60]),'2026-11-08 17:00'),'2026-11-08 17:00');
  assert.equal(v2NextWindowLocal(rows2,now(['2026-11-08',15*60]),'2026-11-08 16:00'),'2026-11-08 17:00');
});

test('CL-UI-51 (h): internal evaluator metric ids get a photographer-facing label, never the raw id',()=>{
  // legacy_long_exposure (tw-059 migration stub) used to render as a raw
  // snake_case id via v2MetricName's ||m fallback.
  const metricsBlock=grab('const V2_EVAL_METRICS','function v2MetricName');
  for(const lang of ['zh-TW','en','ja']){
    let k=metricsBlock.indexOf("'"+lang+"': {");
    if(k<0)k=metricsBlock.indexOf(lang+": {");
    assert.ok(k>=0, lang+' dict present');
    const seg=metricsBlock.slice(k, metricsBlock.indexOf('}', k));
    assert.match(seg,/legacy_long_exposure:'[^']+'/);
  }
});

test('CL-UI-51 (g): the corroboration check sits inside v2NextWindowLocal before the pass-through',()=>{
  const fn=grab('function v2NextWindowLocal','function v2BestForSpot');
  assert.match(fn,/fbQualifies/);
  assert.match(fn,/hoursOf\(day\)\.includes\(fbTime\)/);
  assert.match(fn,/if\(fb&&fbQualifies&&\(fb\.date>now\.date\|\|\(fb\.date===now\.date&&fb\.minutes>=now\.minutes\)\)\)return fallback;/);
});
