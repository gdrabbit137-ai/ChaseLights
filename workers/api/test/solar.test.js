// CL-APP-09 patch-2: minute-level sun times for the ANCHOR time windows.
// Reference values are Open-Meteo daily=sunrise,sunset (minute-level, spot
// local) for the exact coordinates below — the winter/summer pairs pin the
// seasonal shift the anchor expansion must track.
import test from "node:test";
import assert from "node:assert/strict";
import { sunTimesForDate, minutesToHM } from "../src/solar.js";

const TPE = { lat: 25.033, lng: 121.5654, off: 8 };   // 台北
const CTS = { lat: 43.0, lng: 141.35, off: 9 };       // 北海道

function expectSun(date, p, sunrise, sunset, toleranceMin = 3) {
  const t = sunTimesForDate(date, p.lat, p.lng, p.off);
  assert.ok(t, `${date} must have sun events at lat ${p.lat}`);
  const toMin = (hm) => Number(hm.slice(0, 2)) * 60 + Number(hm.slice(3));
  const dRise = Math.abs(t.sunriseMin - toMin(sunrise));
  const dSet = Math.abs(t.sunsetMin - toMin(sunset));
  assert.ok(dRise <= toleranceMin, `sunrise ${date}: got ${minutesToHM(t.sunriseMin)} want ${sunrise} (±${toleranceMin})`);
  assert.ok(dSet <= toleranceMin, `sunset ${date}: got ${minutesToHM(t.sunsetMin)} want ${sunset} (±${toleranceMin})`);
}

test("solar: Taipei winter/summer solstice bracket the seasonal shift (Open-Meteo reference, ±3 min)", () => {
  expectSun("2026-08-17", TPE, "05:28", "18:27");
  expectSun("2026-12-03", TPE, "06:23", "17:03");
  // the seasonal gap the engine must reproduce: >50 min of sunrise drift
  const a = sunTimesForDate("2026-08-17", TPE.lat, TPE.lng, TPE.off);
  const b = sunTimesForDate("2026-12-03", TPE.lat, TPE.lng, TPE.off);
  assert.ok(b.sunriseMin - a.sunriseMin > 45, "winter sunrise is ~55 min later than late summer");
});

test("solar: higher latitude + other timezone stays minute-accurate", () => {
  expectSun("2026-12-03", CTS, "06:47", "16:00");
  expectSun("2026-08-17", CTS, "04:42", "18:34");
});

test("solar: polar day/night returns null (honest unresolved), bad input never throws", () => {
  assert.equal(sunTimesForDate("2026-12-03", 78.2, 15.6, 1), null, "polar night: no sunrise");
  assert.equal(sunTimesForDate("2026-06-21", 78.2, 15.6, 1), null, "midnight sun: no sunset");
  assert.equal(sunTimesForDate("garbage", 25.033, 121.5654, 8), null);
  assert.equal(sunTimesForDate("2026-12-03", null, 121.5654, 8), null);
  assert.equal(sunTimesForDate("2026-12-03", 25.033, undefined, 8), null);
});

test("solar: minutesToHM normalizes out-of-range minutes", () => {
  assert.equal(minutesToHM(0), "00:00");
  assert.equal(minutesToHM(383), "06:23");
  assert.equal(minutesToHM(-30), "23:30");
  assert.equal(minutesToHM(1500), "01:00");
});
