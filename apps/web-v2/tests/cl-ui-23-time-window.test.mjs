// CL-UI-23: night-subject time-window invariant on the served V2 bundle.
//
// Root cause: city_night contracts have no contract-level time window (owner
// data-layer gap). evaluate_batch.py now injects an evaluation-layer REQUIRED
// gate (EVALGATE-city_night-window, metric city_night_window) so a daytime
// hour can never be GUIDANCE_SATISFIED for a night subject — the card's
// 最佳拍攝時段 and the modal both read good_hours / hour statuses from the
// same evaluation, so this invariant keeps every surface consistent.
//
// Invariants asserted over the published artifacts:
// 1. every good_hours entry of a city_night opportunity maps to a details
//    hour with status GUIDANCE_SATISFIED whose conditions contain the
//    evaluation-layer gate with verdict PASS;
// 2. every details GUIDANCE_SATISFIED hour of a city_night opportunity
//    carries the gate with verdict PASS (daytime hours are never good hours);
// 3. an opportunity that already declares a real time-window condition is not
//    double-gated (the gate only exists when the contract lacks one).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.resolve(here, '..');
const repo = path.resolve(webRoot, '..', '..');
const GATE_ID = 'EVALGATE-city_night-window';
const WINDOW_METRICS = new Set(['sunrise_time_window', 'sunset_window',
  'blue_hour_window', 'golden_hour_window', 'astronomical_darkness',
  'city_night_window']);

const summary = JSON.parse(readFileSync(path.join(webRoot, 'evaluations-latest.json'), 'utf8'));
const detailsById = new Map();
for (const f of readdirSync(path.join(webRoot, 'evaluations-details'))) {
  const d = JSON.parse(readFileSync(path.join(webRoot, 'evaluations-details', f), 'utf8'));
  detailsById.set(d.place_id, d);
}

function hoursIndex(detail, oppId) {
  const opp = detail.opportunities.find((o) => o.opportunity_id === oppId);
  if (!opp) return null;
  const map = new Map();
  for (const day of opp.days) for (const h of day.hours) map.set(day.local_date + ' ' + h.local, h);
  return map;
}

test('city_night good_hours carry the evaluation-layer night gate (card side)', () => {
  let checked = 0;
  for (const place of summary.places) {
    const detail = detailsById.get(place.place_id);
    // Known pre-existing artifact collision: two coordinate groups sharing a
    // place_id write the same details filename (later group wins), so some
    // summary opportunities have no surviving details row. Only assert when
    // the per-hour evidence is available.
    if (!detail) continue;
    for (const opp of place.opportunities) {
      if (opp.genre_template !== 'city_night') continue;
      const hours = hoursIndex(detail, opp.opportunity_id);
      if (!hours) continue;
      for (const day of opp.days) {
        for (const h of day.good_hours) {
          checked += 1;
          const hour = hours.get(day.local_date + ' ' + h);
          assert.ok(hour, `good hour ${day.local_date} ${h} must exist in details`);
          assert.equal(hour.status, 'GUIDANCE_SATISFIED',
            `good hour ${day.local_date} ${h} of ${opp.opportunity_id} must be GUIDANCE_SATISFIED`);
          const gate = hour.conditions.find((c) => c.id === GATE_ID);
          assert.ok(gate, `good hour ${day.local_date} ${h} must carry the night gate`);
          assert.equal(gate.verdict, 'PASS',
            `night hour ${day.local_date} ${h} of ${opp.opportunity_id} must be inside the night window`);
        }
      }
    }
  }
  assert.ok(checked > 0, 'expected city_night good_hours to verify');
});

test('city_night satisfied hours in details are always night-window PASS', () => {
  let satisfied = 0;
  for (const [, detail] of detailsById) {
    for (const opp of detail.opportunities) {
      if (opp.genre_template !== 'city_night') continue;
      for (const day of opp.days) {
        for (const h of day.hours) {
          if (h.status !== 'GUIDANCE_SATISFIED') continue;
          satisfied += 1;
          const gate = h.conditions.find((c) => c.id === GATE_ID);
          assert.ok(gate && gate.verdict === 'PASS',
            `${detail.place_id} ${opp.opportunity_id} ${day.local_date} ${h.local}: ` +
            'satisfied night hour must pass the night gate');
        }
      }
    }
  }
  assert.ok(satisfied > 0, 'expected city_night satisfied hours to verify');
});

test('gate stands down when the contract declares a real time window', () => {
  for (const [, detail] of detailsById) {
    for (const opp of detail.opportunities) {
      if (opp.genre_template !== 'city_night') continue;
      for (const day of opp.days) {
        for (const h of day.hours) {
          const realWindow = h.conditions.some((c) =>
            WINDOW_METRICS.has(c.metric) && c.id !== GATE_ID);
          if (realWindow) {
            assert.ok(!h.conditions.some((c) => c.id === GATE_ID),
              'double-gating forbidden for ' + opp.opportunity_id);
          }
        }
      }
    }
  }
});
