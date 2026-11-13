// CL-UI-29 (blueprint §7.3 contract): the card toolbar's 雷達 button is replaced
// by a WeatherGrid deep link built by weatherMapDeepLinkUrl() — region + spot id
// (WeatherGrid positions its own camera from the spot, zoom 9–11 adaptive) plus
// the spot's current best subject genre (?subject=), omitted when there is no
// evaluated best subject (region default layer, fail-closed).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
const indexSource = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');

// grab() — same source-slice helper convention as the other cl-ui tests.
const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};

// Factory: prelude stubs for cardBestGenre's collaborators (v2PlaceForSpot /
// v2BestForSpot / v2Contract are stubbed, so only the URL builder itself is
// under test), then the CL-UI-29 slices only.
const buildWithGenre = (genre, region = 'tw') => {
  const f = new Function([
    `let currentRegion='${region}',currentLang='zh-TW',currentTempUnit='C',currentDayFilter='today';`,
    'let stubGenre=' + (genre === undefined ? 'undefined' : JSON.stringify(genre)) + ';',
    // stub BEFORE the grabbed slice would be shadowed by hoisting if cardBestGenre
    // were grabbed too — so grab only the URL builder (it precedes cardBestGenre).
    grab('function weatherMapDeepLinkUrl', 'function cardBestGenre'),
    `function cardBestGenre(){return stubGenre===undefined?null:stubGenre;}`,
    'return {weatherMapDeepLinkUrl};'
  ].join('\n'));
  return f();
};

test('CL-UI-29: deep link carries region + spot, no subject when no best genre', () => {
  const { weatherMapDeepLinkUrl } = buildWithGenre(undefined);
  assert.equal(weatherMapDeepLinkUrl({ spot_id: 'tw-036' }), './weather-map.html?region=tw&spot=tw-036');
});

test('CL-UI-29: deep link appends ?subject= from the current best genre', () => {
  const { weatherMapDeepLinkUrl } = buildWithGenre('sunset');
  assert.equal(
    weatherMapDeepLinkUrl({ spot_id: 'tw-030' }),
    './weather-map.html?region=tw&spot=tw-030&subject=sunset'
  );
});

test('CL-UI-29: deep link URL-encodes region, spot id and subject genre', () => {
  const { weatherMapDeepLinkUrl } = buildWithGenre('night_sky_milkyway', 'jp');
  assert.equal(
    weatherMapDeepLinkUrl({ spot_id: 'jp-012' }),
    './weather-map.html?region=jp&spot=jp-012&subject=night_sky_milkyway'
  );
});

test('CL-UI-29: cardBestGenre resolves genre_template from the V2 best opportunity', () => {
  const f = new Function([
    "let currentRegion='tw',currentLang='zh-TW',currentTempUnit='C',currentDayFilter='today';",
    grab('function cardBestGenre', 'function navigationTargetNote'),
    `function v2PlaceForSpot(){return {opportunities:[{opportunity_id:'tw-030-P01',genre_template:'sunset'}]};}`,
    `function v2BestForSpot(){return {oppId:'tw-030-P01'};}`,
    `function v2Contract(){return null;}`, // exercise the opportunities fallback
    'return {cardBestGenre};'
  ].join('\n'));
  const { cardBestGenre } = f();
  assert.equal(cardBestGenre({ spot_id: 'tw-030', timezone: 'Asia/Taipei' }), 'sunset');
});

test('CL-UI-29: cardBestGenre prefers the condition-contract genre_template', () => {
  const f = new Function([
    "let currentRegion='tw',currentLang='zh-TW',currentTempUnit='C',currentDayFilter='today';",
    grab('function cardBestGenre', 'function navigationTargetNote'),
    `function v2PlaceForSpot(){return {opportunities:[{opportunity_id:'tw-030-P01',genre_template:'sunset'}]};}`,
    `function v2BestForSpot(){return {oppId:'tw-030-P01'};}`,
    `function v2Contract(){return {genre_template:'golden_hour'};}`,
    'return {cardBestGenre};'
  ].join('\n'));
  const { cardBestGenre } = f();
  assert.equal(cardBestGenre({ spot_id: 'tw-030', timezone: 'Asia/Taipei' }), 'golden_hour');
});

test('CL-UI-29: cardBestGenre returns null with no V2 place (subject omitted)', () => {
  const f = new Function([
    "let currentRegion='tw',currentLang='zh-TW',currentTempUnit='C',currentDayFilter='today';",
    grab('function cardBestGenre', 'function navigationTargetNote'),
    `function v2PlaceForSpot(){return null;}`,
    `function v2BestForSpot(){throw new Error('not reached');}`,
    `function v2Contract(){throw new Error('not reached');}`,
    'return {cardBestGenre};'
  ].join('\n'));
  const { cardBestGenre } = f();
  assert.equal(cardBestGenre({ spot_id: 'tw-036', timezone: 'Asia/Taipei' }), null);
});

test('CL-UI-29: the external radarUrl() helper is removed and the card anchor deep-links', () => {
  assert.ok(!appSource.includes('function radarUrl'), 'radarUrl() must be removed');
  assert.ok(!appSource.includes('OBS_Radar.html'), 'CWA radar external link must be gone');
  assert.ok(!appSource.includes('radar.weather.gov'), 'NWS radar external link must be gone');
  assert.ok(!appSource.includes('jma.go.jp/bosai/nowc'), 'JMA nowc external link must be gone');
  // The card toolbar anchor points at the deep-link builder.
  const anchor = appSource.match(/<a href="\$\{weatherMapDeepLinkUrl\(spot\)\}"[^>]*\$\{toolButtonAttrs\(d\(\)\.radar_link\)\}>/);
  assert.ok(anchor, 'card toolbar radar anchor must use weatherMapDeepLinkUrl(spot)');
});

test('CL-UI-29: 天氣預報 stays the in-page modal (not a duplicate deep link)', () => {
  assert.ok(appSource.includes("data-weather"), 'weather button still opens the modal');
  assert.ok(appSource.includes('openWeatherModal(spot,metric)'), 'weather button handler opens openWeatherModal');
});

test('CL-UI-29: radar_link label reads 天氣圖 in all three languages', () => {
  for (const [lang, label] of [['zh-TW', '🗺️ 天氣圖'], ['en', '🗺️ Weather map'], ['ja', '🗺️ 天気マップ']]) {
    const re = new RegExp(`radar_link:'${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}'`);
    assert.ok(re.test(appSource), `${lang} radar_link must be ${label}`);
  }
  // no leftover radar wording anywhere in the dictionaries
  assert.ok(!appSource.includes('雷達'), 'zh-TW 雷達 wording must be gone');
  assert.ok(!appSource.includes('レーダー'), 'ja レーダー wording must be gone');
});

test('CL-UI-29: homepage cache-bust stamp bumped to clui41', () => {
  assert.ok(indexSource.includes('app.js?v=clui85'), 'index.html must carry the current app.js stamp');
  assert.ok(!indexSource.includes('?v=clui30'), 'stale clui30 stamp must be gone');
});