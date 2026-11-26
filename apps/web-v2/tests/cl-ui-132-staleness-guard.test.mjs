// CL-UI-132 (owner 2026-11-26): the staleness guard.
// A GUIDANCE bundle that stopped refreshing must not keep claiming a verdict.
// On 11/26 the cards still quoted an 11/20 bundle and read "✓ 推薦" for a day
// six days stale — the same failure mode as "15:00 日出": the data was past
// its shelf life and the UI presented it as current.
//
// Contract under test:
//   1. v2EvalFreshness() reports stale when the bundle is >24h old.
//   2. ... and when the newest local_date it covers is already in the past.
//   3. ... and stays fresh when neither condition fires.
//   4. The card badge renders the stale text (not a tier) when stale, and the
//      CSS class it asks for exists.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const ROOT = new URL('../../..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const appJs = readFileSync(join(ROOT, 'assets/app.js'), 'utf8');
const appCss = readFileSync(join(ROOT, 'assets/app.css'), 'utf8');

function extractFn(src, name) {
  const start = src.indexOf('function ' + name + '(');
  assert.ok(start >= 0, `function ${name} present in app.js`);
  let i = src.indexOf('{', start);
  let depth = 0;
  for (let j = i; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') {
      depth--;
      if (depth === 0) return src.slice(start, j + 1);
    }
  }
  throw new Error('unbalanced braces extracting ' + name);
}

// Build the guard with the two globals it closes over. `today` is the page's
// local calendar date, so the test controls "now" without touching the clock.
function buildGuard(bundle, today, nowMs) {
  const fn = extractFn(appJs, 'v2EvalFreshness');
  const factory = new Function(
    'v2EvalBundle', 'localDateString', 'V2_STALE_AFTER_MS',
    `let v2FreshnessCache=null;
     const NOW = ${nowMs};
     const RealDate = globalThis.Date;
     function FakeDate(...a){ return a.length ? new RealDate(...a) : new RealDate(NOW); }
     FakeDate.now = () => NOW;
     FakeDate.parse = RealDate.parse;
     FakeDate.UTC = RealDate.UTC;
     const Date = FakeDate;
     ${fn}
     return v2EvalFreshness;`
  );
  return factory(bundle, () => today, 24 * 60 * 60 * 1000);
}

function bundleWith({generatedAt, dates}) {
  return {
    generated_at: generatedAt,
    places: [{opportunities: [{days: dates.map((d) => ({local_date: d}))}]}],
  };
}

test('CL-UI-132 (1): a bundle older than 24h is stale', () => {
  const now = Date.parse('2026-11-26T12:00:00Z');
  const guard = buildGuard(
    bundleWith({generatedAt: '2026-11-20T06:06:59Z', dates: ['2026-11-26', '2026-12-02']}),
    '2026-11-26', now);
  const r = guard();
  assert.equal(r.stale, true, 'stale when the bundle is six days old');
  assert.equal(r.reason, 'age');
  assert.match(r.stamp, /^\d{2}\/\d{2} \d{2}:\d{2}$/, 'the stamp is MM/DD HH:mm');
});

test('CL-UI-132 (2): a bundle whose newest local_date is past is stale', () => {
  const now = Date.parse('2026-11-27T02:00:00Z');
  const guard = buildGuard(
    bundleWith({generatedAt: '2026-11-26T23:30:00Z', dates: ['2026-11-25', '2026-11-26']}),
    '2026-11-27', now);
  const r = guard();
  assert.equal(r.stale, true, 'the forecast window ended yesterday');
  assert.equal(r.reason, 'date');
});

test('CL-UI-132 (3): a fresh bundle covering today is not stale', () => {
  const now = Date.parse('2026-11-26T12:00:00Z');
  const guard = buildGuard(
    bundleWith({generatedAt: '2026-11-26T06:00:00Z', dates: ['2026-11-26', '2026-12-02']}),
    '2026-11-26', now);
  const r = guard();
  assert.equal(r.stale, false, 'six hours old and covers today');
  assert.equal(r.reason, null);
});

test('CL-UI-132 (4): the card badge states the truth instead of a tier', () => {
  const badge = appJs.match(/const clBadgeTier=staleInfo\.stale\?'stale':/);
  assert.ok(badge, 'clBadgeTier short-circuits to the stale class');
  const label = appJs.match(/const clBadgeLabel=staleInfo\.stale\?d\(\)\.v2_stale_badge\.replace\('\{t\}',staleInfo\.stamp\):/);
  assert.ok(label, 'the badge label carries the update stamp');
  // the secondary lines repeat the tier claim — they must not contradict it
  assert.match(appJs, /const scSecondLine=staleInfo\.stale\?'':/,
    'the second-line verdict is suppressed while stale');
  assert.match(appJs, /const clFallbackRows=\(\(\)=>\{if\(staleInfo\.stale\|\|/,
    'the fallback tier rows are suppressed while stale');
  // every language states the same fact
  for (const [lang, text] of [['zh-TW', '資料更新延遲中'], ['en', 'Data refresh delayed'], ['ja', 'データ更新']]) {
    const re = new RegExp(`v2_stale_badge:`);
    assert.match(appJs, re, 'v2_stale_badge key present');
    assert.ok(appJs.includes(text), `stale copy exists for ${lang}`);
  }
  assert.match(appCss, /\.tier-stale\{[^}]*\}/, 'the stale badge has a style');
});
