// CL-UI-15: homepage card status-row denoise (three packed items).
// V1 shell repo-root assets/app.js — source assertions plus one extracted
// pure function (stripSpotNamePrefix), per the established test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const cardBlock=(start,end)=>appSource.slice(
  appSource.indexOf(start),
  appSource.indexOf(end,start)
);
const createSpotCardBlock=cardBlock('function createSpotCard','function distanceToSpotKm');

// Extract stripSpotNamePrefix with the spotName const it depends on.
const grab=(start,end)=>{const i=appSource.indexOf(start);return appSource.slice(i,appSource.indexOf(end,i));};
const stripFn=grab('function stripSpotNamePrefix','// CL-UI-05: single V2 day-state label mapping');
const spotNameConst=grab('const spotName=s=>','\n');
const stripSpotNamePrefix=new Function(`${spotNameConst}\nlet currentLang='zh-TW';\n${stripFn}\nreturn stripSpotNamePrefix;`)();

test('CL-UI-15 (1): summary line strips a leading spot-name prefix (display-level only)',()=>{
  const spot={name_i18n:{'zh-TW':'合歡山'},name_local:'Hehuan Mountain'};
  // current-language name (spotName) prefix is stripped.
  assert.equal(stripSpotNamePrefix('合歡山：雲海',spot),'雲海');
  // name_local prefix is stripped too.
  assert.equal(stripSpotNamePrefix('Hehuan Mountain sea of clouds',spot),'sea of clouds');
  // A name_local in the local language is stripped as well.
  const spotLocal={name_i18n:{'zh-TW':'合歡山'},name_local:'合歡山主峰'};
  assert.equal(stripSpotNamePrefix('合歡山主峰：日出',spotLocal),'日出');
  // Safe prefix: a subject that merely contains the name is untouched.
  assert.equal(stripSpotNamePrefix('夢幻合歡山雲海',spot),'夢幻合歡山雲海');
  // A subject that is exactly the spot name stays (never render an empty subject).
  assert.equal(stripSpotNamePrefix('合歡山',spot),'合歡山');
  // No prefix at all: unchanged.
  assert.equal(stripSpotNamePrefix('雲海',spot),'雲海');
  // Render path consumes the helper.
  assert.match(createSpotCardBlock,/esc\(stripSpotNamePrefix\(v2Best\.name,spot\)\)/);
});

test('CL-UI-15 (2): per-card timezone row is removed from the card list',()=>{
  // The card template no longer carries a card-timezone span.
  assert.equal(/class="card-timezone"/.test(createSpotCardBlock),false,
    'card status list must not repeat a per-card timezone row');
  // The removal carries a reason comment (future multi-timezone restoration).
  assert.match(createSpotCardBlock,/CL-UI-15: the per-card timezone row/);
  // tzAbbrLabel is kept for the header clock and modal windows.
  assert.match(appSource,/function tzAbbrLabel\(/);
  assert.match(appSource,/tzAbbrLabel\(tz\)/);
});

test('CL-UI-15 (3): forecast-status row omitted on GUIDANCE_SATISFIED cards',()=>{
  // The row renders only for non-satisfied V2 evaluations.
  assert.match(createSpotCardBlock,
    /\$\{v2Best&&v2Best\.state!=='GUIDANCE_SATISFIED'\?`<div class="info-row forecast-status-row card-meta-row">/);
  // Grouping (CL-UI-12) and fail-closed (CL-UI-14) semantics are untouched.
  assert.match(appSource,/const v2Evaluated=!!v2Best;/);
  assert.match(createSpotCardBlock,/d\(\)\.research_pending_card/);
});