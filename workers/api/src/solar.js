// Sunrise/sunset for a local calendar date at (lat, lng) — NOAA solar
// equations (public domain), minute-level. Serves the CL-APP-09 anchor time
// windows (window_type before_sunrise/after_sunrise/before_sunset/
// after_sunset): the judgment engine expands those anchors with the place's
// REAL sun times for EACH row's local date, so 冬天/夏至 give different
// windows without any upstream fetch or new weather call.
//
// Contract:
//   sunTimesForDate("2026-12-03", 25.033, 121.5654, 8)
//     -> { sunriseMin, sunsetMin }   // minutes since local midnight
//     -> null                        // polar day/night: no event that day
//   All hours here are the ROW convention of the KV grids: spot-LOCAL time
//   (official places distilled per bundle timezone; custom places Open-Meteo
//   timezone=auto). utcOffsetHours defaults to +8 (the Taiwan baseline).
const RAD = Math.PI / 180;
const DEG = 180 / Math.PI;

// Julian Day at 00:00 UT for a civil date (Gregorian, Fliegel–Van Flandern).
function julianDay0UT(y, m, d) {
  if (m <= 2) { y -= 1; m += 12; }
  const a = Math.floor(y / 100);
  const b = 2 - a + Math.floor(a / 4);
  return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + b - 1524.5;
}

// One solar computation pass: apparent declination (deg) and equation of time
// (minutes) for the Julian-century T of the target instant.
function solarGeom(jd) {
  const T = (jd - 2451545.0) / 36525;
  const L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360;
  const M = 357.52911 + T * (35999.05029 - 0.0001537 * T);
  const e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T);
  const Mr = M * RAD;
  // Equation of center in DEGREES (NOAA coefficients) — no radian conversion.
  const C = (Math.sin(Mr) * (1.914602 - T * (0.004817 + 0.000014 * T)) +
    Math.sin(2 * Mr) * (0.019993 - 0.000101 * T) +
    Math.sin(3 * Mr) * 0.000289);
  const trueLong = L0 + C;
  const omega = 125.04 - 1934.136 * T;
  const lambda = trueLong - 0.00569 - 0.00478 * Math.sin(omega * RAD);
  const eps0 = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60;
  const eps = eps0 + 0.00256 * Math.cos(omega * RAD);
  const decl = Math.asin(Math.sin(eps * RAD) * Math.sin(lambda * RAD)) * DEG;
  const y = Math.tan(eps * RAD / 2) ** 2;
  const L0r = L0 * RAD;
  const eqtime = 4 * DEG * (
    y * Math.sin(2 * L0r) -
    2 * e * Math.sin(Mr) +
    4 * e * y * Math.sin(Mr) * Math.cos(2 * L0r) -
    0.5 * y * y * Math.sin(4 * L0r) -
    1.25 * e * e * Math.sin(2 * Mr)
  );
  return { decl, eqtime };
}

export function sunTimesForDate(localDate, lat, lng, utcOffsetHours = 8) {
  const md = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(localDate || ""));
  if (!md) return null;
  const phi = Number(lat), lngv = Number(lng);
  if (lat == null || lng == null || !Number.isFinite(phi) || !Number.isFinite(lngv) || Math.abs(phi) > 90 || Math.abs(lngv) > 180) return null;
  const y = Number(md[1]), m = Number(md[2]), d = Number(md[3]);
  const offMin = (Number.isFinite(utcOffsetHours) ? utcOffsetHours : 8) * 60;
  // Anchor on the LOCAL NOON of the row's date: JD of that civil date plus the
  // (12:00 local − UT) displacement, so the solar geometry is evaluated for
  // the same calendar day the hour rows belong to.
  const jdNoon = julianDay0UT(y, m, d) + (12 * 60 - offMin) / 1440;
  const { decl, eqtime } = solarGeom(jdNoon);
  // Hour angle for sunrise/sunset at zenith 90.833° (disc + refraction).
  const cosH = (Math.cos(90.833 * RAD) - Math.sin(phi * RAD) * Math.sin(decl * RAD)) /
    (Math.cos(phi * RAD) * Math.cos(decl * RAD));
  if (cosH > 1 || cosH < -1) return null; // polar: sun never crosses the horizon
  const H = Math.acos(cosH) * DEG; // degrees
  // Solar noon in UT minutes (longitude EAST positive).
  const solarNoonUT = 720 - 4 * lngv - eqtime;
  const riseUT = solarNoonUT - 4 * H;
  const setUT = solarNoonUT + 4 * H;
  const norm = (x) => ((x % 1440) + 1440) % 1440;
  const rise = Math.round(norm(riseUT + offMin));
  const set = Math.round(norm(setUT + offMin));
  return { sunriseMin: rise, sunsetMin: set };
}

export function minutesToHM(min) {
  const m = ((Number(min) % 1440) + 1440) % 1440;
  const hh = String(Math.floor(m / 60)).padStart(2, "0");
  const mm = String(m % 60).padStart(2, "0");
  return `${hh}:${mm}`;
}
