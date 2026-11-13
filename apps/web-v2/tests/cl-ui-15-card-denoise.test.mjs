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
  // Render path consumes the helper, passing the V2 evaluation-bundle place
  // object as an extra alias source (CL-UI-47).
  assert.match(createSpotCardBlock,/esc\(stripSpotNamePrefix\(v2Best\.name,spot,v2PlaceData\?\[v2PlaceData\]:\[\]\)\)/);
});

test('CL-UI-48: ja strip drops the dangling leading particle (grammar-safe)',()=>{
  // ja copy is grammar-bound to the name: 「関渡大橋の夜間ライトアップと光跡」
  // strips to 「の夜間…」 unless the particle goes too. zh/en must be untouched.
  const stripFnJa=grab('function stripSpotNamePrefix','// CL-UI-05: single V2 day-state label mapping');
  const stripJa=new Function(`${spotNameConst}\nlet currentLang='ja';\n${stripFnJa}\nreturn stripSpotNamePrefix;`)();
  const spot={name_i18n:{ja:'関渡大橋'},name_local:'關渡大橋'};
  assert.equal(stripJa('関渡大橋の夜間ライトアップと光跡',spot),'夜間ライトアップと光跡');
  // Each listed particle is dropped in ja.
  for(const p of ['は','が','を','に','へ','と','で','や','も','から','まで']){
    assert.equal(stripJa('関渡大橋'+p+'夜景',spot),'夜景',`particle ${p}`);
  }
  // Only ONE leading particle goes; the rest of the copy is intact.
  assert.equal(stripJa('関渡大橋ののっぽの塔',spot),'のっぽの塔');
  // Separators still strip first, then no particle remains.
  assert.equal(stripJa('関渡大橋：夜景',spot),'夜景');
  // zh-TW is unchanged: no particle logic runs outside ja.
  assert.equal(stripSpotNamePrefix('合歡山：雲海',{name_i18n:{'zh-TW':'合歡山'},name_local:'Hehuan Mountain'}),'雲海');
  // The remainder check: if stripping would not leave a CJK char or letter
  // (e.g. the subject is the name plus a particle only), keep the full string.
  assert.equal(stripJa('関渡大橋の',spot),'関渡大橋の');
});

test('CL-UI-47: alias place name from the V2 bundle strips a name-variant prefix',()=>{
  // tw-086 regression: the legacy spot name uses 淡水大橋 while the V2
  // research/contract subject uses the variant 淡江大橋; the alias source
  // must let the strip remove the full place-name echo. True-prefix and
  // longest-first semantics are unchanged.
  const spot={name_i18n:{'zh-TW':'八里崁頭里・淡水大橋觀景點'},name_local:'八里崁頭里・淡水大橋觀景點'};
  const v2Place={name_i18n:{'zh-TW':'八里崁頭里・淡江大橋觀景點'}};
  assert.equal(
    stripSpotNamePrefix('八里崁頭里・淡江大橋觀景點：淡江大橋日景通透（白天通透）',spot,[v2Place]),
    '淡江大橋日景通透（白天通透）');
  // Without the alias source the variant prefix is left untouched (no fuzzy match).
  assert.equal(
    stripSpotNamePrefix('八里崁頭里・淡江大橋觀景點：淡江大橋日景通透（白天通透）',spot),
    '八里崁頭里・淡江大橋觀景點：淡江大橋日景通透（白天通透）');
  // Alias still honours true full-name match: a mere near-match must not strip.
  assert.equal(
    stripSpotNamePrefix('合歡山北峰：日出',spot,[{name_i18n:{'zh-TW':'合歡山主峰'}}]),
    '合歡山北峰：日出');
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

test('CL-UI-15 (3): forecast-status row is retired on every card (CL-UI-63)',()=>{
  // CL-UI-63: the long-sentence status line left the card entirely — the
  // second line carries the verdict + short chips from the subject-cards layer.
  assert.equal(/forecast-status-row/.test(createSpotCardBlock),false,
    'card status list must not render the forecast-status row');
  // Grouping (CL-UI-12) and fail-closed (CL-UI-14) semantics are untouched.
  assert.match(appSource,/const v2Evaluated=!!v2Best;/);
  assert.match(createSpotCardBlock,/v2NoEvalReasonText\(spot\)/);
});