// CL-UI-62: genre short-name dictionary + failure-reason short-word mapping +
// derived subject-card layer (build-time artifact over the evaluation bundle).
// Data-layer ticket: covers (1) EVERY genre_template in opportunities/bundles
// has a trilingual short name; (2) EVERY metric in contracts/overrides/bundles
// has a trilingual short weather word and no dangling priority entry; (3) the
// committed derived artifact matches its declared source bundle and the copy
// dictionaries; (4) structural spot-checks of the derived rows against the
// source bundle.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, readdirSync, existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const copyDir = join(ROOT, 'data', 'v2', 'copy');
const evalDir = join(ROOT, 'data', 'v2', 'evaluations');
const oppDir = join(ROOT, 'data', 'v2', 'opportunities');

const genreDict = JSON.parse(readFileSync(join(copyDir, 'genre_short_names.json'), 'utf8'));
const failShort = JSON.parse(readFileSync(join(copyDir, 'fail_reason_short.json'), 'utf8'));
const LANGS = ['zh-TW', 'en', 'ja'];

function oppFiles() {
  return readdirSync(oppDir).filter((f) => f.endsWith('.json')).map((f) => join(oppDir, f));
}

test('CL-UI-62: every genre_template in opportunities has a trilingual short name', () => {
  const genres = new Set();
  for (const f of oppFiles()) {
    const txt = readFileSync(f, 'utf8');
    for (const m of txt.matchAll(/"genre_template"\s*:\s*"([^"]+)"/g)) genres.add(m[1]);
  }
  assert.ok(genres.size >= 20, `expected a real genre corpus, got ${genres.size}`);
  for (const g of genres) {
    const entry = genreDict.genres[g];
    assert.ok(entry, `missing genre short name: ${g}`);
    for (const lang of LANGS) {
      assert.ok(typeof entry[lang] === 'string' && entry[lang].length > 0, `${g} missing ${lang}`);
    }
    assert.ok(entry['zh-TW'].length <= 3, `${g} zh-TW short name must be 2-3 chars, got "${entry['zh-TW']}"`);
  }
});

test('CL-UI-62: every violated metric has a trilingual short weather word', () => {
  const metrics = new Set();
  for (const f of oppFiles()) {
    const txt = readFileSync(f, 'utf8');
    for (const m of txt.matchAll(/"metric"\s*:\s*"([^"]+)"/g)) metrics.add(m[1]);
  }
  const overrides = JSON.parse(readFileSync(join(copyDir, 'fail_reason_overrides.json'), 'utf8'));
  for (const perOpp of Object.values(overrides)) {
    for (const metric of Object.keys(perOpp)) metrics.add(metric);
  }
  // bundle condition metrics
  const artifactPath = join(evalDir, 'subject-cards-20261112T202312Z.json');
  const artifact = JSON.parse(readFileSync(artifactPath, 'utf8'));
  const bundle = JSON.parse(readFileSync(join(evalDir, artifact.derived_from.source_bundle), 'utf8'));
  for (const place of bundle.places) {
    for (const opp of place.opportunities) {
      for (const day of opp.days) {
        for (const cond of day.conditions) metrics.add(cond.metric);
      }
    }
  }
  for (const metric of metrics) {
    const entry = failShort.words[metric];
    assert.ok(entry, `missing short weather word for metric: ${metric}`);
    for (const lang of LANGS) {
      assert.ok(typeof entry[lang] === 'string' && entry[lang].length > 0, `${metric} missing ${lang}`);
    }
  }
  // every priority entry resolves to a word
  for (const metric of failShort.metric_priority) {
    assert.ok(failShort.words[metric], `metric_priority has dangling entry: ${metric}`);
  }
  // rule doc present and versioned (CL-UI-70: rule 1.1 — window metrics
  // abstain when the window occurred; qualification metrics never day-vote)
  assert.equal(failShort.dominant_reason_rule.rule_version, '1.1');
  assert.ok(failShort.dominant_reason_rule['zh-TW'].length > 40);
  assert.ok(failShort.dominant_reason_rule.en.length > 40);
});

test('CL-UI-62: metric_priority keeps the shipped legacy head order', () => {
  // The first two entries must match assets/app.js V2_FAIL_PRIORITY so the data
  // layer can never contradict the live card UX.
  assert.equal(failShort.metric_priority[0], 'precipitation');
  assert.equal(failShort.metric_priority[1], 'visibility');
  assert.equal(new Set(failShort.metric_priority).size, failShort.metric_priority.length, 'priority list has duplicates');
});

test('CL-UI-62: derived artifact provenance binds it to a real bundle', () => {
  const artifactPath = join(evalDir, 'subject-cards-20261112T202312Z.json');
  const artifact = JSON.parse(readFileSync(artifactPath, 'utf8'));
  assert.equal(artifact.layer, 'subject_cards');
  assert.equal(artifact.ticket, 'CL-UI-62');
  assert.equal(artifact.derived_from.generator, 'data/v2/tools/build_subject_cards.py');
  const bundlePath = join(evalDir, artifact.derived_from.source_bundle);
  assert.ok(existsSync(bundlePath), `declared source bundle missing: ${artifact.derived_from.source_bundle}`);
  const sha = createHash('sha256').update(readFileSync(bundlePath)).digest('hex');
  assert.equal(sha, artifact.derived_from.source_bundle_sha256, 'source bundle sha mismatch');
  // embedded dictionaries must equal the copy files verbatim
  assert.deepEqual(artifact.dictionaries.genre_short_names, genreDict.genres);
  assert.deepEqual(artifact.dictionaries.fail_reason_short, failShort.words);
});

test('CL-UI-62: derived rows join back to the source bundle (460 places, all days)', () => {
  const artifactPath = join(evalDir, 'subject-cards-20261112T202312Z.json');
  const artifact = JSON.parse(readFileSync(artifactPath, 'utf8'));
  const bundle = JSON.parse(readFileSync(join(evalDir, artifact.derived_from.source_bundle), 'utf8'));
  assert.equal(Object.keys(artifact.places).length, bundle.places.length);
  for (const place of bundle.places) {
    const days = artifact.places[place.place_id];
    assert.ok(days, `missing derived rows for place ${place.place_id}`);
    for (const opp of place.opportunities) {
      for (const day of opp.days) {
        const row = days[day.local_date];
        assert.ok(row, `missing derived row ${place.place_id} ${day.local_date}`);
        assert.ok(['clear', 'failed', 'not_evaluable'].includes(row.status), `bad status ${row.status}`);
        for (const s of row.suitable) {
          assert.ok(Array.isArray(s.window), 'suitable window must be an array');
        }
        if (row.dominant_reason !== null) {
          assert.ok(failShort.words[row.dominant_metric], `dominant metric unmapped: ${row.dominant_metric}`);
          assert.deepEqual(row.dominant_reason, failShort.words[row.dominant_metric]);
        } else {
          assert.equal(row.dominant_metric, null);
        }
      }
    }
  }
});

test('CL-UI-62: suitable rows match bundle GUIDANCE_SATISFIED days with qualifying hours', () => {
  const artifactPath = join(evalDir, 'subject-cards-20261112T202312Z.json');
  const artifact = JSON.parse(readFileSync(artifactPath, 'utf8'));
  const bundle = JSON.parse(readFileSync(join(evalDir, artifact.derived_from.source_bundle), 'utf8'));
  for (const place of bundle.places) {
    const days = artifact.places[place.place_id];
    const expectedByDate = new Map();
    for (const opp of place.opportunities) {
      if (opp.genre_template === 'general') continue; // CL-UI-65: never a chip
      for (const day of opp.days) {
        if (day.state === 'GUIDANCE_SATISFIED' && (day.good_hours || []).length > 0) {
          expectedByDate.set(day.local_date, (expectedByDate.get(day.local_date) || 0) + 1);
        }
      }
    }
    for (const [date, expected] of expectedByDate) {
      const actual = days[date].suitable.length;
      assert.equal(actual, expected, `suitable count mismatch ${place.place_id} ${date}`);
      // every subject_short must be a dictionary entry for a genre actually
      // present among that place-date's suitable opportunities
      const allowed = new Set();
      const canon = (o) => JSON.stringify(Object.fromEntries(Object.entries(o).sort()));
      for (const opp of place.opportunities) {
        if (opp.genre_template === 'general') continue; // CL-UI-65: never a chip
        for (const day of opp.days) {
          if (day.local_date === date && day.state === 'GUIDANCE_SATISFIED' && (day.good_hours || []).length > 0) {
            allowed.add(canon(genreDict.genres[opp.genre_template]));
          }
        }
      }
      for (const s of days[date].suitable) {
        assert.ok(allowed.has(canon(s.subject_short)), `subject_short not from a suitable subject: ${JSON.stringify(s.subject_short)}`);
      }
    }
    // and no suitable entries appear on dates the bundle never satisfies
    for (const [date, row] of Object.entries(days)) {
      if (!expectedByDate.has(date)) assert.equal(row.suitable.length, 0, `unexpected suitable ${place.place_id} ${date}`);
    }
  }
});
