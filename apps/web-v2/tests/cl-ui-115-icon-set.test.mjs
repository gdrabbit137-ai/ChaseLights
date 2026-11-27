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

// ---------------------------------------------------------------------------
// CL-UI-116 — the LAST four emoji. §1 left them alone because they are
// navigational (the footer's 題材 / 地圖 / 天氣圖 entries and the weather panel
// title) rather than metric symbols. §1's premise still holds for them: an emoji
// codepoint is drawn by the platform's emoji font, so the same toolbar looked
// sharp on Windows and soft on the phone. This closes the set and pins it in
// the RENDERED DOM — a source grep cannot see that a label still renders emoji.
const NEW_KEYS=['subject','map_pin','map','weather_overview'];
// Emoji detection = Extended_Pictographic (the Unicode property that covers
// 🔴 ⏰ ⏱ ⌚ 🌦️ 🗺️ and every other pictograph an emoji font would draw) plus
// U+FE0F, the variation selector that forces emoji presentation on an otherwise
// text-shaped codepoint. Named ranges were too narrow: ⏰ U+23F0 / ⏱ U+23F1 /
// ⌚ U+231A sat outside them, so a re-introduced ⏰ passed this very check.
//
// Marks that are intentionally NOT emoji and must keep passing this regex:
//   ✓ U+2713 / ○ U+25CB / ✗ U+2717 — the tier verdict marks, plain glyphs from
//     the paragraph-symbol block (drawn by the UI font, not the emoji font;
//     none of them is Extended_Pictographic);
//   ★ U+2605 — the favourite toggle, likewise a plain star, not ⭐ U+2B50;
//   the LIVE badge — a CSS-painted .tool-live-dot (a border-radius div), so no
//     codepoint is involved at all and the label is bare text.
const EMOJI_RE=/[\p{Extended_Pictographic}\uFE0F]/u;

test('CL-UI-116: subject / map_pin / map / weather_overview draw real glyphs',()=>{
  for(const key of NEW_KEYS){
    const svg=G.clIcon(key);
    assert.match(svg,/^<svg /,`${key} resolves to the inline SVG`);
    assert.match(svg,new RegExp(`data-cl-icon="${key}"`),`${key} rides its own key`);
    assert.match(svg,/stroke="currentColor"/,`${key} strokes currentColor`);
    assert.match(svg,/aria-hidden="true"/,`${key} is decorative in markup`);
    assert.doesNotMatch(svg,/\swidth="|\sheight="/,`${key} carries no inline size — .cl-icon owns it`);
    assert.doesNotMatch(svg,/fill="(?!none")/,`${key} has no hard-coded fill`);
    const body=svg.slice(svg.indexOf('>')+1,svg.lastIndexOf('</svg>'));
    assert.ok(body.length>=40,`${key} draws a body of real length (got ${body.length} chars)`);
    assert.match(body,/[MmLlHhVvCcSsQqTtAaZz]\s*-?\d/,`${key} draws at least one SVG path command`);
  }
  const bodyOf=k=>{const s=G.clIcon(k);return s.slice(s.indexOf('>')+1,s.lastIndexOf('</svg>'));};
  // `subject` is a stack of framed subjects, never a re-run of the camera or a peak.
  const subjectBody=bodyOf('subject');
  for(const other of ['general','mountain_view','landscape','geology','all'])
    assert.notEqual(subjectBody,bodyOf(other),`subject must not reuse the ${other} shape`);
  // The map sheet and its pin are two marks, not one drawing twice.
  assert.notEqual(bodyOf('map'),bodyOf('map_pin'),'map and map_pin are distinct drawings');
  // The weather-panel title glyph and the two cloud verdict glyphs share a
  // silhouette at 1em (a sun/cloud pair on the same baseline), so the gate has
  // to compare them explicitly — a family split is not proof of distinctness.
  for(const other of ['partly','overcast','mostly_clear','clear','fog'])
    assert.notEqual(bodyOf('weather_overview'),bodyOf(other),
      `weather_overview must not re-run the ${other} drawing — the panel title would read as that verdict`);
  // partly = sun + cloud, overcast = one cloud, weather_overview = disc + cloud:
  // three separate drawings, and the title glyph always carries more than a cloud.
  assert.notEqual(bodyOf('partly'),bodyOf('overcast'),'partly and overcast are distinct verdicts');
  assert.ok(bodyOf('weather_overview').length>bodyOf('overcast').length,
    'weather_overview adds its disc on top of the cloud instead of being the bare overcast cloud');
});

test('CL-UI-116: the toolbar labels are pure text and every call site passes its key',()=>{
  for(const [key,zh,en] of [['v2_subject_link','題材','Subjects'],['map_link','地圖','Map'],
    ['radar_link','天氣圖','Weather map'],['weather_link','天氣預報','Weather'],
    ['nav_pending','導航待確認','Nav pending'],['map_link_approx','地圖（概略座標）','Map (approximate pin)']]){
    const zhLabel=(appSource.match(new RegExp(`${key}:'([^']*)'`))||[])[1];
    assert.equal(zhLabel,zh,`${key} zh-TW label is the bare text ${zh}`);
    assert.ok(appSource.includes(`${key}:'${en}'`),`${key} en label is the bare text ${en}`);
    assert.doesNotMatch(zhLabel||'',EMOJI_RE,`${key} carries no emoji codepoint`);
  }
  // The icon arrives as a key, not as a prefix string to be split apart again.
  assert.match(appSource,/function toolButtonInner\(label,iconKey\)/,'toolButtonInner takes an explicit icon key');
  assert.match(appSource,/clIconSvg\(iconKey\)/,'the key goes through the shared icon lookup');
  assert.match(appSource,/toolButtonInner\(d\(\)\.v2_subject_link,'subject'\)/,'題材 uses the subject glyph');
  assert.match(appSource,/toolButtonInner\(d\(\)\.map_link,'map_pin'\)/,'地圖 uses the map_pin glyph');
  assert.match(appSource,/toolButtonInner\(d\(\)\.radar_link,'map'\)/,'天氣圖 uses the map glyph');
  // The <span class="tool-ico"> box is kept (hit area / flex slot / focus ring).
  assert.match(appSource,/<span class="tool-ico" aria-hidden="true">\$\{icon\}<\/span><span class="tool-txt">\$\{esc\(label\)\}<\/span>/,
    'the icon keeps its own box and the label keeps its own text span');
  // The weather panel title: SVG glyph + text, never an emoji prefix.
  assert.equal((appSource.match(/clIconSvg\('weather_overview'\)/g)||[]).length,2,
    'both weather-modal title render sites use the weather_overview glyph');
  assert.doesNotMatch(appSource,/innerText=`🌦️/,'the emoji title prefix is gone');
});

test('CL-UI-116: the emoji gate itself catches ⏰/⏱/⌚ and the dead nav_link key is gone',()=>{
  // Reviewer condition 2: the old named ranges missed U+231A/U+23F0/U+23F1, so a
  // re-introduced ⏰ passed. The property-based regex must now flag them…
  for(const cp of ['\u231A','\u23F0','\u23F1','\u{1F534}','\u{1F5FA}\uFE0F','\u{1F326}\uFE0F'])
    assert.match(cp,EMOJI_RE,`U+${cp.codePointAt(0).toString(16).toUpperCase()} is caught as emoji`);
  // …while the legitimate non-emoji marks stay clean (named in the EMOJI_RE comment).
  for(const mark of ['✓','○','✗','★','·','—','：'])
    assert.doesNotMatch(mark,EMOJI_RE,`${mark} is a UI-font mark, not emoji`);
  // No toolbar label in ANY language may carry a pictograph (live_link included).
  // The scan is per-key on purpose: the same dictionaries still hold other
  // surfaces' emoji (scene_label 🖼️, theme_label 📸 …) that CL-UI-116 does not own.
  const TOOLBAR_KEYS=['v2_subject_link','weather_link','nav_link','map_link','map_link_approx','nav_pending','radar_link','live_link'];
  const toolbarLabels=[...appSource.matchAll(new RegExp(`(?:${TOOLBAR_KEYS.join('|')}):'([^']*)'`,'g'))].map(m=>m[1]);
  assert.ok(toolbarLabels.length>=18,`the three tables expose ${TOOLBAR_KEYS.length} toolbar labels each (got ${toolbarLabels.length})`);
  for(const label of toolbarLabels) assert.doesNotMatch(label,EMOJI_RE,`toolbar label "${label}" carries no pictograph or U+FE0F`);
  for(const live of toolbarLabels.filter(l=>/LIVE/.test(l))) assert.equal(live,'LIVE','the LIVE label is bare text in every language');
  // Reviewer condition 3: nav_link had no call site (`d().nav_link` is never
  // read) but carried a 🗺️ emoji — a future trap. Deleted, not icon-swapped,
  // because the toolbar's 地圖/nav entries already ride map_pin.
  assert.doesNotMatch(appSource,/nav_link/,'the dead nav_link key is gone from all three tables (no call site exists)');
  assert.match(appSource,/map_link:'地圖',/,'the surviving map label is bare text');
});

test('CL-UI-116: rendered zh-TW and en pages carry no emoji in the card footer or the weather title',async()=>{
  const {createServer}=await import('node:http');
  const {readFileSync,statSync}=await import('node:fs');
  const {dirname,join,normalize}=await import('node:path');
  const {fileURLToPath,pathToFileURL}=await import('node:url');
  const HERE=dirname(fileURLToPath(import.meta.url));
  const ROOT=normalize(join(HERE,'..','..','..'));
  const PW=process.env.PLAYWRIGHT_MODULE||join(ROOT,'.ci','tooling','node_modules','playwright','index.js');
  const CHROME=process.env.CHROMIUM_EXECUTABLE||process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe';
  const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2'};
  const server=createServer((req,res)=>{
    const url=new URL(req.url,'http://127.0.0.1');
    let p=normalize(join(ROOT,decodeURIComponent(url.pathname)));
    if(!p.startsWith(ROOT)){res.writeHead(403);res.end();return;}
    try{if(statSync(p).isDirectory())p=join(p,'index.html');}catch(e){res.writeHead(404);res.end('not found');return;}
    let body;try{body=readFileSync(p);}catch(e){res.writeHead(404);res.end('not found');return;}
    const ext=/\.([a-z0-9]+)$/i.exec(p);
    res.writeHead(200,{'content-type':MIME[ext?'.'+ext[1].toLowerCase():'']||'application/octet-stream'});
    res.end(body);
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const base=`http://127.0.0.1:${server.address().port}`;
  const pw=await import(pathToFileURL(PW).href);
  const chromium=pw.chromium||(pw.default&&pw.default.chromium);
  const browser=await chromium.launch({executablePath:CHROME,args:['--no-sandbox','--disable-dev-shm-usage']});
  try{
    for(const [lang,expect] of [
      ['zh-TW',{subject:'題材',map:['地圖','地圖（概略座標）','導航待確認'],radar:'天氣圖',title:'天氣預報'}],
      ['en',{subject:'Subjects',map:['Map','Map (approximate pin)','Nav pending'],radar:'Weather map',title:'Weather'}],
    ]){
      const page=await browser.newPage({viewport:{width:1440,height:900},locale:lang});
      await page.goto(`${base}/index.html?region=tw&lang=${lang}`,{waitUntil:'domcontentloaded'});
      await page.waitForFunction(()=>document.querySelectorAll('#spots-container .card').length>0,null,{timeout:60000});
      await page.waitForFunction(()=>{const t=document.querySelector('#spots-container .card .tier');return t&&t.textContent.trim().length>0;},null,{timeout:60000});
      const footer=await page.evaluate(()=>{
        const out=[];
        // The 4th button (CL-UI-111 LIVE) is a thumbnail + red-dot badge by design,
        // not a navigational glyph — it keeps its own mark and is excluded here.
        for(const link of document.querySelectorAll('#spots-container .card .card-footer-tools .tool-link:not(.tool-live)')){
          const svgs=[...link.querySelectorAll('.tool-ico svg[data-cl-icon]')];
          const s=svgs[0];
          const iconBox=s?s.parentElement:null;
          const cs=s?getComputedStyle(s):null;
          out.push({
            text:link.textContent.replace(/\s+/g,' ').trim(),
            keys:svgs.map(x=>x.getAttribute('data-cl-icon')),
            w:cs?parseFloat(cs.width):null,
            h:cs?parseFloat(cs.height):null,
            fs:iconBox?parseFloat(getComputedStyle(iconBox).fontSize):null,
            stroke:cs?cs.stroke:null,
            color:cs?getComputedStyle(link).color:null,
            attrSize:s?(s.getAttribute('width')||s.getAttribute('height')):null,
          });
        }
        return out;
      });
      assert.ok(footer.length>=6,`${lang}: the cards render a toolbar row (got ${footer.length} links)`);
      for(const link of footer){
        assert.doesNotMatch(link.text,EMOJI_RE,`${lang}: footer link "${link.text}" carries no emoji`);
        assert.equal(link.keys.length,1,`${lang}: "${link.text}" holds exactly one SVG glyph (got ${JSON.stringify(link.keys)})`);
        assert.equal(link.attrSize,null,`${lang}: ${link.keys[0]} carries no inline width/height`);
        assert.ok(Math.abs(link.w-link.fs)<0.75&&link.w>6,`${lang}: ${link.keys[0]} renders at 1em (${link.w}px vs ${link.fs}px)`);
        assert.ok(Math.abs(link.w-link.h)<0.5,`${lang}: ${link.keys[0]} is square`);
        assert.equal(link.stroke,link.color,`${lang}: ${link.keys[0]} inherits currentColor (hover/active tint)`);
      }
      const texts=footer.map(l=>l.text);
      const live=await page.evaluate(()=>document.querySelectorAll('#spots-container .card .card-footer-tools .tool-link.tool-live').length);
      assert.ok(live>=1,`${lang}: the LIVE button is still in the row (it owns the red dot, not a glyph)`);
      // CL-UI-116 reviewer condition 1: .tool-live is INSIDE the no-emoji gate
      // now. It used to be exempt here, which is exactly how 🔴 survived next to
      // the CSS .tool-live-dot and painted two red dots in the live row.
      const allFooterTexts=await page.evaluate(()=>[...document.querySelectorAll('#spots-container .card .card-footer-tools .tool-link')]
        .map(l=>l.textContent.replace(/\s+/g,' ').trim()));
      assert.ok(allFooterTexts.length>footer.length,`${lang}: the gate covers the LIVE button too (${allFooterTexts.length} links, ${footer.length} glyph links)`);
      for(const t of allFooterTexts) assert.doesNotMatch(t,EMOJI_RE,`${lang}: footer link "${t}" carries no emoji — including .tool-live`);
      assert.ok(allFooterTexts.includes('LIVE'),`${lang}: the LIVE button's bare text label survives (got ${JSON.stringify(allFooterTexts)})`);
      assert.ok(texts.includes(expect.subject),`${lang}: the subject entry keeps its text label ${expect.subject}`);
      assert.ok(expect.map.some(m=>texts.includes(m)),`${lang}: the map entry keeps its text label`);
      assert.ok(texts.includes(expect.radar),`${lang}: the weather-map entry keeps its text label ${expect.radar}`);
      assert.ok(footer.some(l=>l.text===expect.subject&&l.keys[0]==='subject'),`${lang}: 題材 rides the subject key`);
      assert.ok(footer.some(l=>expect.map.includes(l.text)&&l.keys[0]==='map_pin'),`${lang}: 地圖 rides the map_pin key`);
      assert.ok(footer.some(l=>l.text===expect.radar&&l.keys[0]==='map'),`${lang}: 天氣圖 rides the map key`);
      // …and the weather panel title.
      await page.locator('#spots-container .card').first().click({position:{x:20,y:20}});
      await page.waitForFunction(()=>document.getElementById('modal-overlay').style.display==='flex',null,{timeout:15000});
      const title=await page.evaluate(()=>{
        const el=document.getElementById('modal-spot-name');
        const s=el.querySelector('svg[data-cl-icon]');
        return {text:el.textContent.replace(/\s+/g,' ').trim(),key:s?s.getAttribute('data-cl-icon'):null,
          html:el.innerHTML.slice(0,160)};
      });
      assert.doesNotMatch(title.text,EMOJI_RE,`${lang}: the weather title "${title.text}" carries no emoji`);
      assert.equal(title.key,'weather_overview',`${lang}: the title leads with the weather_overview glyph (${title.html})`);
      assert.ok(title.text.includes('—'),`${lang}: the place — forecast separator survives`);
      assert.ok(title.text.endsWith(expect.title),`${lang}: the title keeps its text label ${expect.title} (got "${title.text}")`);
      await page.close();
    }
    // CL-UI-116 reviewer condition 4: the 44px icon-only toolbar. At
    // <=640px .tool-txt is display:none and the whole button is the glyph, so
    // this is the state where an emoji fallback would be most visible (and
    // where a text-less button would be most invisible). Assert the SAME
    // data-cl-icon SVG renders at 1em inside a >=44px square — not a codepoint.
    const mobile=await browser.newPage({viewport:{width:390,height:844},locale:'zh-TW'});
    try{
      await mobile.goto(`${base}/index.html?region=tw&lang=zh-TW`,{waitUntil:'domcontentloaded'});
      await mobile.waitForFunction(()=>document.querySelectorAll('#spots-container .card').length>0,null,{timeout:60000});
      await mobile.waitForFunction(()=>document.querySelectorAll('#spots-container .card .card-footer-tools .tool-ico svg[data-cl-icon]').length>0,null,{timeout:60000});
      const mobileLinks=await mobile.evaluate(()=>[...document.querySelectorAll('#spots-container .card .card-footer-tools .tool-link:not(.tool-live)')].map(l=>{
        const svg=l.querySelector('.tool-ico svg[data-cl-icon]');
        const ico=l.querySelector('.tool-ico');
        const txt=l.querySelector('.tool-txt');
        const box=l.getBoundingClientRect();
        const cs=svg?getComputedStyle(svg):null;
        return {
          text:l.textContent.replace(/\s+/g,' ').trim(),
          key:svg?svg.getAttribute('data-cl-icon'):null,
          isSvg:!!svg&&svg.outerHTML.startsWith('<svg '),
          icoText:ico?ico.textContent.trim():null,
          txtDisplay:txt?getComputedStyle(txt).display:null,
          w:box.width,h:box.height,
          svgW:cs?parseFloat(cs.width):null,svgH:cs?parseFloat(cs.height):null,
        };
      }));
      assert.ok(mobileLinks.length>=6,`mobile: the toolbar renders on the 390px contract (got ${mobileLinks.length} glyph links)`);
      for(const l of mobileLinks){
        assert.ok(l.isSvg,`mobile: "${l.text}" renders the inline SVG, not an emoji fallback`);
        assert.doesNotMatch(l.icoText,EMOJI_RE,`mobile: the icon box of "${l.text}" holds no emoji codepoint (got ${JSON.stringify(l.icoText)})`);
        assert.equal(l.txtDisplay,'none',`mobile: "${l.text}" is icon-only — the text label is hidden, not squeezed out`);
        assert.ok(l.w>=43.5&&l.h>=43.5,`mobile: "${l.text}" keeps the 44px touch target (${l.w}x${l.h})`);
        assert.ok(l.svgW>6&&Math.abs(l.svgW-l.svgH)<0.5,`mobile: ${l.key} stays a square 1em glyph (${l.svgW}x${l.svgH})`);
      }
      assert.deepEqual([...new Set(mobileLinks.map(l=>l.key))].sort(),['map','map_pin','subject'],
        'mobile: the same three keys as desktop — the icon-only state never substitutes a different mark');
    }finally{
      try{await mobile.close();}catch(e){/* noop */}
    }
  }finally{
    try{await browser.close();}catch(e){/* noop */}
    await new Promise(r=>server.close(r));
  }
});
