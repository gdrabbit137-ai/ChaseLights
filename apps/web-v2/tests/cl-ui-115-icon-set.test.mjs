// CL-UI-115 §1 — one inline SVG icon set for every metric/weather glyph.
//
// Why: every metric/weather symbol used to be an emoji literal baked into
// assets/app.js, so the same codepoint was drawn by a different font on Windows,
// macOS, Android and iOS (the owner saw a sharp eye on desktop, a soft one on
// the phone). There was no second code path — only the platform emoji font.
//
// This file pins the CONTRACT of assets/icons.js and the fact that app.js routes
// its metric/weather positions through it:
//   - frozen CL_ICONS map, currentColor strokes, no hard-coded fill, no width/height
//   - a key for every WMO code in app.js, every subject in the label table, plus
//     the twelve metric keys
//   - clIcon(key) falls back to the historical emoji for an unknown key
//   - .cl-icon is a 1em box with a fixed baseline offset (no layout shift)
//   - no emoji left in a metric/weather render position in app.js
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const iconSource=readFileSync(new URL('../../../assets/icons.js',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const indexSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');

// Load the shipped icon set the way the browser does (a plain script that
// assigns onto its global), then inspect the REAL map, not a copy of it.
const sandbox={window:{},Object,Number,String,isFinite,RegExp};
vm.createContext(sandbox);
vm.runInContext(iconSource.replace(/^\(function \(root\)/,'(function (root)'), sandbox);
const G=sandbox.window;
assert.ok(G.CL_ICONS&&G.clIcon,'assets/icons.js publishes CL_ICONS + clIcon onto the global');

const WMO_CODES=(()=>{
  const table=appSource.slice(appSource.indexOf('const WMO_ICON_FALLBACK='),appSource.indexOf('function clIconSvg'));
  return [...table.matchAll(/(\d+):'/g)].map(m=>m[1]);
})();
const SUBJECT_KEYS=(()=>{
  const start=appSource.indexOf('const themeLabels = {');
  const block=appSource.slice(start,appSource.indexOf('\n    };',start));
  const zh=block.slice(block.indexOf("'zh-TW':{")+9,block.indexOf('},',block.indexOf("'zh-TW':{")));
  return [...zh.matchAll(/(?:^|,)([a-z_]+):'/g)].map(m=>m[1]);
})();
const METRIC_KEYS=['visibility','cloud','fog','wind','humidity','temperature','elevation','azimuth','sunrise','sunset','moon','star'];

test('CL-UI-115 §1: CL_ICONS is a frozen map of currentColor-stroke SVGs',()=>{
  assert.ok(Object.isFrozen(G.CL_ICONS),'CL_ICONS is frozen');
  const keys=Object.keys(G.CL_ICONS);
  assert.ok(keys.length>=60,`the set carries the whole table (got ${keys.length} keys)`);
  for(const key of keys){
    const svg=G.CL_ICONS[key];
    assert.match(svg,/^<svg /,`${key}: is an inline <svg>`);
    assert.match(svg,/data-cl-icon="/,`${key}: is addressable by data-cl-icon`);
    assert.match(svg,/stroke="currentColor"/,`${key}: strokes currentColor so CSS can tint it`);
    assert.doesNotMatch(svg,/\swidth="|\sheight="/,`${key}: no inline width/height — the CSS box owns the size`);
    assert.doesNotMatch(svg,/fill="(?!none")/,`${key}: no hard-coded fill colour`);
    assert.match(svg,/aria-hidden="true"/,`${key}: decorative glyph is hidden from AT (the text label carries the name)`);
  }
});

test('CL-UI-115 §1: every WMO code, subject and metric key has a glyph',()=>{
  assert.ok(WMO_CODES.length>=28,`app.js carries the full WMO table (got ${WMO_CODES.length} codes)`);
  for(const code of WMO_CODES){
    assert.ok(G.CL_ICONS[code],`WMO ${code} has an icon`);
    assert.equal(G.clIconKeyForWmo(code)!==null,true,`WMO ${code} maps to a shape`);
  }
  assert.equal(SUBJECT_KEYS.length,23,`the subject label table has 23 subjects (got ${SUBJECT_KEYS.length})`);
  for(const key of SUBJECT_KEYS) assert.ok(G.CL_ICONS[key],`subject ${key} has an icon`);
  for(const key of METRIC_KEYS) assert.ok(G.CL_ICONS[key],`metric ${key} has an icon`);
});

test('CL-UI-115 §1: an unknown key still renders something (emoji fallback data)',()=>{
  // A WMO code the forecast adds tomorrow, an unmapped named metric, a null.
  assert.equal(G.clIcon('12'),'☁️','an unknown numeric code falls back to the range emoji, never blank');
  assert.equal(G.clIcon('999'),'⛈️','unknown severe codes keep the storm emoji');
  assert.equal(G.clIcon('not_a_key'),'','a fully unknown named key degrades to empty, never to "[object Object]"');
  assert.equal(G.clIcon(null),'','null is handled without throwing');
  // …and a KNOWN key never returns the emoji any more.
  assert.match(G.clIcon('visibility'),/^<svg /,'visibility resolves to the SVG, not 👁');
  for(const code of WMO_CODES) assert.match(G.clIcon(code),/^<svg /,`WMO ${code} resolves to the SVG`);
});

test('CL-UI-115 §1: app.js routes every metric/weather position through the icon set',()=>{
  // The lookup helper is typeof-guarded so extracted test slices stay self-contained.
  assert.match(appSource,/function clIconSvg\(key\)\{[\s\S]*?typeof clIcon==='function'/, 'the helper guards the global lookup');
  assert.match(appSource,/function wmoIcon\(code\)\{[\s\S]*?clIconSvg\(String\(c\)\)/, 'wmoIcon reads the icon set');
  assert.match(appSource,/const cloudChip=clBaseTxt\?`<span class="metric-chip">\$\{clIconSvg\('cloud'\)\}/, 'the cloud-base chip uses the cloud icon');
  assert.match(appSource,/const clElevPill=clElev!=null\?`<span class="metric-chip">\$\{clIconSvg\('elevation'\)\}/, 'the elevation pill uses the elevation icon');
  assert.match(appSource,/\$\{clIconSvg\('visibility'\)\} \$\{esc\(vt\)\}/, 'the visibility value carries the eye icon');
  assert.match(appSource,/function tempChipHtml\(temp\)[\s\S]*?clIconSvg\('temperature'\)/, 'the temperature chip uses the temperature icon');
  // Emoji survive ONLY as fallback data: the render positions may not carry one.
  for(const literal of ['`👁 ','>☁️ ${esc(clBaseTxt)', '>⛰ ${clElev}', '>🌡 ${esc(t)}', "'☀ ${Math.round(metric.sun_azimuth)}"]){
    assert.ok(!appSource.includes(literal),`no emoji metric glyph "${literal}" remains in a render position`);
  }
});

test('CL-UI-115 §1: .cl-icon is a 1em box with a fixed baseline offset',()=>{
  const rule=cssSource.match(/\.cl-icon \{[^}]*\}/);
  assert.ok(rule,'app.css defines .cl-icon');
  assert.match(rule[0],/width:\s*1em/);
  assert.match(rule[0],/height:\s*1em/);
  assert.match(rule[0],/vertical-align:\s*-0\.125em/);
  assert.match(rule[0],/stroke:\s*currentColor/);
  assert.match(rule[0],/fill:\s*none/);
});

test('CL-UI-115 §1: icons.js loads before app.js with a cache stamp',()=>{
  assert.match(indexSource,/assets\/icons\.js\?v=clui\d+/,'index.html stamps the icon set');
  assert.ok(indexSource.indexOf('assets/icons.js')<indexSource.indexOf('assets/app.js'),'icons.js loads first');
});

// REGRESSION GUARD (reviewer condition 1). The icon commit stripped the emoji
// prefix out of the 23-row subject label table (`☁️ 雲海` → `雲海`) and never
// re-attached a glyph, so every subject surface — card subject row, hourly
// subject chip, filter row, summary line — silently went plain-text. A table
// with no emoji is only correct if a SUBJECT ICON lookup replaces it, so these
// assertions pin both halves: no emoji in the table AND an SVG in every
// subject render position.
test('CL-UI-115 §1: the 23 subject keys carry no emoji but DO carry an SVG glyph',()=>{
  const start=appSource.indexOf('const themeLabels = {');
  const block=appSource.slice(start,appSource.indexOf('\n    };',start));
  assert.equal(SUBJECT_KEYS.length,23);
  for(const key of SUBJECT_KEYS){
    assert.ok(G.clIcon(key),`subject key ${key} resolves to a glyph`);
    assert.match(G.clIcon(key),/^<svg /,`subject key ${key} resolves to the SVG, not a codepoint`);
  }
  // No emoji left in the label table itself (the historical form was `🌅 日出`).
  assert.doesNotMatch(block,/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u,'the subject label table carries no emoji');
  // …but the text label is still there, per §1.4 (an icon is never the only carrier).
  assert.match(block,/'zh-TW':\{[^}]*cloud_sea:'雲海'/,'the zh-TW text label survives');
});

test('CL-UI-115 §1: card row, hourly chip, filter row and summary all render the subject glyph',()=>{
  // themeLabelHtml: the text-label table's render form (icon + escaped text).
  assert.match(appSource,/function themeLabelHtml\(k\)\{[\s\S]*?clIconSvg\(k\)[\s\S]*?esc\(text\)/,'themeLabelHtml prefixes the same text with the icon');
  // card subject row — its own span so the pinned name/colon/window anatomy is untouched
  assert.match(appSource,/const iconHtml=icon\?`<span class="cl-subject-icon">\$\{icon\}<\/span>`:''/,'the card subject row wraps its glyph in its own span');
  assert.match(appSource,/\$\{iconHtml\}<span class="cl-subject-name/,'the row inserts the glyph before the subject name');
  assert.match(appSource,/const icon=\(entry&&entry\.genre\)\?clIconSvg\(entry\.genre\):''/,'the row resolves the glyph from the artifact genre');
  // hourly subject chip
  assert.match(appSource,/<span class="subj-chip">\$\{clIconSvg\(c\.genre\)\} \$\{esc\(c\.label\)\}<\/span>/,'the hourly subject chip carries its glyph plus the text label');
  // filter row
  assert.match(appSource,/const icon=clIconSvg\(iconKey\|\|key\);b\.innerHTML=`\$\{icon\?icon\+' ':''\}\$\{esc\(label\)\}`/,'the filter chip renders glyph + text');
  assert.match(appSource,/clui66SubjectCatalogKeys\.forEach\(k=>mk\(k,clui66SubjectCatalogNames\[k\]\?clui66SubjectDisplayName\(k\):null,clui66SubjectCatalogGenres\[k\]\|\|k\)\)/,'the filter row passes the artifact genre as the icon key');
  // A catalog key without a localized name still renders glyph + text (the
  // shipped theme label table is the fallback), so no chip is ever bare text.
  assert.match(appSource,/if\(label==null\)\{b\.innerHTML=themeLabelHtml\(iconKey\|\|key\);\}/,'the no-name fallback still goes through themeLabelHtml');
  // summary (7-day summary + modal day rows)
  assert.match(appSource,/function v2SubjectCardShortHtml\(row,lang,limit\)[\s\S]*?<span class="cl-summary-subject">\$\{icon\?icon\+' ':''\}\$\{esc\(label\)\}<\/span>/,'the summary renders glyph + text per subject');
  assert.match(appSource,/const shorts=scRow\?v2SubjectCardShortHtml\(scRow,currentLang,3\)/,'the modal day summary uses the glyph-aware shorts');
  assert.match(appSource,/const shorts=v2SubjectCardShortHtml\(v2SubjectCardRow\(spot\.spot_id,date\),currentLang,3\)/,'the 7-day summary uses the glyph-aware shorts');
  // the pure-text accessor stays text (other surfaces/tests depend on it)
  assert.match(appSource,/function v2SubjectCardShorts\(row,lang\)\{\n\s+const canon=/,'v2SubjectCardShorts remains a pure text accessor');
});

test('CL-UI-115 §1: every subject genre the artifact can emit resolves to a glyph',()=>{
  // The committed subject-cards artifact names subjects with its own genre
  // vocabulary, so EVERY key of its `genre_short_names` dictionary is part of
  // the contract — not only the genres that happen to appear in today's pinned
  // rows. A genre the dictionary knows but the rows do not yet use (misty_forest,
  // snow_ice_night, volcanic_glow were exactly that) rendered text-only on the
  // card row, filter row, summary and modal, and a row-only enumeration could
  // never catch it. The dictionary is the authority: one glyph per key, no ''.
  const cardsFile=(appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/)||[])[1];
  assert.ok(cardsFile,'app.js pins the subject-cards artifact filename');
  const cards=JSON.parse(readFileSync(new URL('../../../data/v2/evaluations/'+cardsFile,import.meta.url),'utf8'));
  const dictGenres=Object.keys((cards.dictionaries||{}).genre_short_names||{});
  assert.ok(dictGenres.length>=25,`the dictionary carries the genre vocabulary (got ${dictGenres.length})`);
  for(const g of dictGenres){
    const svg=G.clIcon(g);
    assert.match(svg,/^<svg /,`dictionary genre ${g} resolves to a glyph, never ''`);
    assert.match(svg,new RegExp(`data-cl-icon="${g}"`),`${g}: the artifact's own key rides the SVG`);
    // The wrapper proves nothing on its own: `<svg …></svg>` (an EMPTY body)
    // matches /^<svg / too, so this gate reads the DRAWING. A real glyph has a
    // body well past the wrapper's overhead (the smallest is 82 chars) and at
    // least one SVG path command — an empty or placeholder body fails here
    // directly, instead of only in the distinct-data test further down.
    const body=svg.slice(svg.indexOf('>')+1,svg.lastIndexOf('</svg>'));
    assert.ok(body.length>=40,
      `dictionary genre ${g} draws a body of real length (got ${body.length} chars: ${JSON.stringify(svg)}) — an empty body is not a glyph`);
    assert.match(body,/[MmLlHhVvCcSsQqTtAaZz]\s*-?\d/,
      `dictionary genre ${g} draws at least one SVG path command (body: ${JSON.stringify(body)})`);
  }
  // …and the genres that DO appear in the pinned rows are a subset of it.
  const rowGenres=new Set();
  for(const tree of Object.values(cards.places||{}))
    for(const row of Object.values(tree||{}))
      for(const s of (row&&row.suitable)||[]) if(s&&s.genre) rowGenres.add(s.genre);
  assert.ok(rowGenres.size>=15,`the artifact rows carry a broad genre vocabulary (got ${rowGenres.size})`);
  for(const g of rowGenres) assert.ok(dictGenres.includes(g),`row genre ${g} is a dictionary key`);
  for(const g of rowGenres) assert.match(G.clIcon(g),/^<svg /,`artifact genre ${g} has an icon`);
});

test('CL-UI-115 §1: every subject key draws DISTINCT path data (no shared alias)',()=>{
  // A shared shape is not a style choice: `overlook` used to alias `mountain_view`,
  // so 山景 and 眺望 drew the identical 99-byte mountain in the same subject list —
  // two rows, one picture, reading as one repeated subject. 金山 (alpenglow) and
  // 夕陽 (sunset) were one alias away from the same collision. The rule: a shape
  // may be shared ONLY when the user-visible label is the same subject; no such
  // pair exists in this dictionary, so every key must hash differently.
  const cardsFile=(appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/)||[])[1];
  const cards=JSON.parse(readFileSync(new URL('../../../data/v2/evaluations/'+cardsFile,import.meta.url),'utf8'));
  const dictGenres=Object.keys((cards.dictionaries||{}).genre_short_names||{});
  const keys=[...new Set([...SUBJECT_KEYS,...dictGenres,...G.CL_SUBJECT_GENRES])];
  assert.equal(SUBJECT_KEYS.length,23,'the 23 theme keys are all in the set');
  assert.ok(G.CL_SUBJECT_GENRES.length>=20,`icons.js publishes its artifact-genre key list (got ${G.CL_SUBJECT_GENRES.length})`);
  assert.ok(keys.length>=44,`the subject vocabulary is the 23 keys plus the artifact genres (got ${keys.length})`);
  const bodyOf=key=>{
    const svg=G.clIcon(key);
    assert.match(svg,/^<svg /,`${key}: resolves to an SVG before it can be compared`);
    return svg.slice(svg.indexOf('>')+1,svg.lastIndexOf('</svg>'));
  };
  const seen=new Map();
  for(const key of keys){
    const body=bodyOf(key);
    assert.ok(body.length>20,`${key}: draws something`);
    assert.equal(seen.has(body),false,`${key} draws the same path data as ${seen.get(body)} — distinct subjects need distinct glyphs`);
    seen.set(body,key);
  }
  assert.equal(seen.size,keys.length,`one distinct glyph per subject key (${seen.size} of ${keys.length})`);
});

test('CL-UI-115 §1: the three dictionary genres that rendered text-only draw real shapes',()=>{
  // Reviewer condition 1: misty_forest / snow_ice_night / volcanic_glow were in
  // the artifact's dictionary but resolved to '' — text-only on the card row,
  // filter row, summary and modal. Each needs a real drawing: trees + mist,
  // moon/snowflake, mountain with glow.
  const forest=G.clIcon('misty_forest');
  assert.match(forest,/^<svg /,'misty_forest draws');
  assert.ok((forest.match(/<path /g)||[]).length>=2,'misty_forest draws trees AND mist bands');
  const snow=G.clIcon('snow_ice_night');
  assert.match(snow,/^<svg /,'snow_ice_night draws');
  assert.ok((snow.match(/<path /g)||[]).length>=2,'snow_ice_night draws a moon figure and snow/ground');
  const lava=G.clIcon('volcanic_glow');
  assert.match(lava,/^<svg /,'volcanic_glow draws');
  assert.ok((lava.match(/<path /g)||[]).length>=3,'volcanic_glow draws a cone, a crater and a glow');
});

