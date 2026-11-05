// CL-UI-23: night-subject time-window invariant on the served V2 bundle.
//
// Root cause: city_night contracts had no contract-level time window, so
// daytime hours passed every REQUIRED weather condition and became good_hours.
// CL-UI-23 added an evaluation-layer REQUIRED gate (EVALGATE-city_night-window,
// metric city_night_window) for contracts lacking a window; CL-UI-25 added the
// real contract-level city_night_window condition to all 22 city_night
// contracts, so the evaluation-layer gate stands down automatically and every
// satisfied night hour carries the CONTRACT window condition (verdict PASS)
// instead of the eval-layer gate id. This invariant keeps every surface
// consistent regardless of which of the two sources is active.
//
// Invariants asserted over the published artifacts:
// 1. every good_hours entry of a city_night opportunity maps to a details
//    hour with status GUIDANCE_SATISFIED whose conditions contain a
//    city_night_window condition with verdict PASS (either the contract-level
//    window or the evaluation-layer gate);
// 2. every details GUIDANCE_SATISFIED hour of a city_night opportunity
//    carries such a PASS window condition (daytime hours are never good hours);
// 3. an hour is never double-gated (contract window and eval-layer gate do
//    not coexist).
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

function nightWindowCond(hour) {
  return hour.conditions.find((c) =>
    c.metric === 'city_night_window' ||
    WINDOW_METRICS.has(c.metric) && c.id === GATE_ID);
}

test('city_night good_hours carry the evaluation-layer night gate (card side)', () => {
  let checked = 0;
  for (const place of summary.places) {
    const detail = detailsById.get(place.place_id);
    // CL-UI-25: detail docs are keyed per place_id and merged across coordinate
    // groups, so every summary place has a details row; keep the tolerant skip
    // for any place without evaluated details.
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
          const gate = nightWindowCond(hour);
          assert.ok(gate, `good hour ${day.local_date} ${h} must carry the night window`);
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
          const gate = nightWindowCond(h);
          assert.ok(gate && gate.verdict === 'PASS',
            `${detail.place_id} ${opp.opportunity_id} ${day.local_date} ${h.local}: ` +
            'satisfied night hour must pass the night window');
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
