"""CL-DATA-68: minute-level solar window boundaries for the derived layer.

The evaluation engine (astro_hourly) judges hour buckets by SUB-HOUR
INTERVAL SAMPLING (5-min samples, CL-UI-08) — the bucket is the unit and a
qualifying bucket is stamped at its earliest passing sample (CL-DATA-31).
The derived subject-card layer, however, judged civil light by the hourly
Open-Meteo grid instant (sun_elevation > -6) — an hour-bucket verdict that
mislabels the dawn/dusk boundary hours by up to a full bucket: at civil dawn
05:23 the 05:00 bucket reads dark at the grid instant although it contains
37 civil-light minutes.

This module computes the solar-elevation window boundaries directly from
coordinates + local date with the SAME NOAA/Meeus altitude chain as
solar_window.py (Open-Meteo does not publish solar angles), refined to the
minute by bisection:

- light_window        civil light, sun altitude > -6°  (civil dawn → civil dusk)
- daylight_window     sun altitude > 0°                (sunrise → sunset)
- city_night_window   sun altitude <= -6°              (civil dusk → civil dawn)
- astronomical_darkness sun altitude <= -18°
- golden_hour_window  -6° <= altitude <= +6°           (dawn and dusk sides)
- blue_hour_window    -8° <= altitude <= -4°
- sunrise_time_window sunrise ±40 min, sunset_window sunset ±40 min

Intervals are returned in LOCAL MINUTES relative to the local date's
midnight (values may be negative or > 1440 when a window crosses midnight —
night subjects legitimately start on the previous evening). No crossing in
the sampled span (polar day/night) propagates honestly: no interval, no
fabricated boundary. Results are cached once per place-day.

No weather, no scoring, no live recommendation. Deterministic per instant.
"""
from __future__ import annotations

import math
import sys
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path

# repo root = packages/models-v2/civil_twilight.py -> parents[2]
_REPO = Path(__file__).resolve().parents[2]
for entry in (str(_REPO / "packages" / "models-v2"), str(_REPO)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from solar_window import _solar_altitude_deg  # noqa: E402

SCAN_STEP_MIN = 2
BISECT_ITERATIONS = 16
SUNRISE_HALF_WIDTH_MIN = 40
SUNSET_HALF_WIDTH_MIN = 40
# Night windows (city night, astronomical darkness) legitimately start on the
# previous evening, so the sampled span reaches beyond both midnight edges.
SPAN_MARGIN_HOURS = 26

# metric -> (lo_deg, hi_deg, lo_strict, hi_strict). Membership is
# lo <= alt <= hi with the strict flags turning a bound open (engine
# semantics: light/daylight are strictly above the bound, city night
# strictly at-or-below it, golden/blue inclusive on both ends).
BAND_MEMBERSHIP = {
    "light_window": (-6.0, 90.0, True, False),
    "daylight_window": (0.0, 90.0, True, False),
    "city_night_window": (-90.0, -6.0, False, True),
    "astronomical_darkness": (-90.0, -18.0, False, True),
    "golden_hour_window": (-6.0, 6.0, False, False),
    "blue_hour_window": (-8.0, -4.0, False, False),
}


def _member_fn(lo, hi, lo_strict, hi_strict):
    def member(alt):
        if lo_strict:
            if not alt > lo:
                return False
        elif not alt >= lo:
            return False
        if hi_strict:
            return alt < hi
        return alt <= hi
    return member


def _day_start_epoch(local_date, utc_offset_hours):
    """UTC epoch of the local date's midnight (offset = local - UTC)."""
    return (datetime(local_date.year, local_date.month, local_date.day,
                     tzinfo=timezone.utc).timestamp()
            - utc_offset_hours * 3600.0)


def _local_minutes(epoch_utc, day_start_epoch, utc_offset_hours):
    """UTC epoch -> local minutes relative to the local date's midnight.

    day_start_epoch is already the UTC epoch of local midnight, so no extra
    offset arithmetic applies here (the offset lives in day_start_epoch)."""
    return (epoch_utc - day_start_epoch) / 60.0


def _sample(lat, lon, start_epoch, end_epoch):
    """Grid the span at SCAN_STEP_MIN and evaluate the altitude chain once."""
    ts = [start_epoch]
    step = SCAN_STEP_MIN * 60.0
    while ts[-1] < end_epoch:
        ts.append(min(end_epoch, ts[-1] + step))
    alts = [_solar_altitude_deg(datetime.fromtimestamp(t, timezone.utc), lat, lon)
            for t in ts]
    return ts, alts


def _bisect_edge(lat, lon, t_outside, t_inside, member):
    """Refine a membership edge between a non-member and a member instant."""
    lo, hi = t_outside, t_inside
    for _ in range(BISECT_ITERATIONS):
        mid = (lo + hi) / 2.0
        if member(_solar_altitude_deg(datetime.fromtimestamp(mid, timezone.utc),
                                      lat, lon)):
            hi = mid
        else:
            lo = mid
    return hi


def _band_intervals_utc(lat, lon, ts, alts, member):
    """Maximal member stretches inside the sampled span, edges bisected to
    sub-second precision (floor to the minute by the caller). An empty list
    is the honest polar answer: the band never occurs in the span."""
    runs = []
    start = None
    for i, alt in enumerate(alts):
        if member(alt):
            if start is None:
                start = i
        elif start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(alts) - 1))
    out = []
    n = len(ts)
    for i0, i1 in runs:
        # Interior runs only: a run touching the span edge has no sampled
        # non-member neighbour to bisect against (the +-26h margin makes
        # every window edge interior for the supported latitudes).
        if i0 > 0:
            start_t = _bisect_edge(lat, lon, ts[i0 - 1], ts[i0], member)
        else:
            start_t = ts[i0]
        if i1 < n - 1:
            end_t = _bisect_edge(lat, lon, ts[i1 + 1], ts[i1], member)
        else:
            end_t = ts[i1]
        if end_t > start_t:
            out.append((start_t, end_t))
    return out


def _zero_crossings(lat, lon, ts, alts):
    """Sunrise/sunset crossings (altitude 0) linearly interpolated on the
    scan grid, then bisected on the altitude sign for minute precision."""
    out = []
    for i in range(1, len(ts)):
        a, b = alts[i - 1], alts[i]
        if a == 0.0 or a * b > 0:
            continue
        rising = a < 0
        lo, hi = ts[i - 1], ts[i]
        for _ in range(BISECT_ITERATIONS):
            mid = (lo + hi) / 2.0
            if (_solar_altitude_deg(datetime.fromtimestamp(mid, timezone.utc),
                                    lat, lon) > 0) == (b > 0):
                hi = mid
            else:
                lo = mid
        out.append((hi, "sunrise" if rising else "sunset"))
    return out


@lru_cache(maxsize=None)
def solar_day_windows(lat, lon, local_date, utc_offset_hours):
    """CL-DATA-68: minute-level window boundaries for ONE place-day.

    Returns {"intervals": {metric: [(start_min, end_min), ...]},
             "events": {"civil_dawn": min|None, "civil_dusk": min|None,
                        "sunrise": min|None, "sunset": min|None}} with local
    minutes floored to the whole minute (windows precise to the minute).
    Cached once per place-day (rounded coordinate). Callers fall back to the
    hourly grid-instant semantics when their metric has no interval — never
    a fabricated boundary.
    """
    lat = float(lat)
    lon = float(lon)
    offset = float(utc_offset_hours)
    local_date = _as_date(local_date)
    day_start = _day_start_epoch(local_date, offset)
    margin = SPAN_MARGIN_HOURS * 3600.0
    span_start = day_start - margin
    span_end = day_start + 24.0 * 3600.0 + margin
    ts, alts = _sample(lat, lon, span_start, span_end)
    intervals = {}
    for metric, (lo, hi, lo_strict, hi_strict) in BAND_MEMBERSHIP.items():
        member = _member_fn(lo, hi, lo_strict, hi_strict)
        spans = _band_intervals_utc(lat, lon, ts, alts, member)
        intervals[metric] = sorted(
            (math.floor(_local_minutes(s, day_start, offset)),
             math.floor(_local_minutes(e, day_start, offset)))
            for s, e in spans)
    events = {"civil_dawn": None, "civil_dusk": None,
              "sunrise": None, "sunset": None}
    crossings = _zero_crossings(lat, lon, ts, alts)
    for t, kind in crossings:
        m = _local_minutes(t, day_start, offset)
        # Only the crossings inside THIS local day name its sunrise/sunset;
        # neighbours (yesterday's late event, tomorrow's early one) exist in
        # the widened span and must not overwrite them.
        if 0 <= m < 1440:
            events[kind] = math.floor(m)
    # sunrise/sunset ±40 min windows ride the same crossings (minute level).
    for kind, half in (("sunrise", SUNRISE_HALF_WIDTH_MIN),
                       ("sunset", SUNSET_HALF_WIDTH_MIN)):
        intervals["%s_time_window" % kind if kind == "sunrise"
                  else "sunset_window"] = sorted(
            (math.floor(_local_minutes(t, day_start, offset) - half),
             math.floor(_local_minutes(t, day_start, offset) + half))
            for t, k in crossings if k == kind)
    # Civil dawn/dusk are the morning/evening edges of the civil-light
    # stretch that actually overlaps the local day. A stretch covering the
    # whole day (polar summer, midnight sun) has no boundary inside it:
    # honest None, never a fabricated horizon event.
    for s, e in intervals["light_window"]:
        if e <= 0 or s >= 1440:
            continue  # yesterday's / tomorrow's civil light
        if s < -SPAN_MARGIN_HOURS * 60 / 2 or e > 1440 + SPAN_MARGIN_HOURS * 60 / 2:
            events["civil_dawn"] = None
            events["civil_dusk"] = None
            break
        events["civil_dawn"] = s
        events["civil_dusk"] = e
        break
    return {"intervals": intervals, "events": events}


def _as_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def hour_hits_interval(start_min, dur_min, intervals):
    """True when the hour bucket [start, start+dur) intersects any interval."""
    end_min = start_min + dur_min
    return any(s < end_min and e > start_min for s, e in intervals)


def local_day_start_epoch(local_date, utc_offset_hours):
    """UTC epoch of the local date's midnight (exposed for callers that must
    place an evaluation instant on the same local-minute scale)."""
    return _day_start_epoch(_as_date(local_date), float(utc_offset_hours))


def epoch_local_minutes(day_start_epoch, epoch_utc):
    """Minutes since local midnight for an absolute UTC epoch."""
    return (epoch_utc - day_start_epoch) / 60.0


def hour_inside_interval(start_min, dur_min, intervals):
    """True when the hour bucket lies ENTIRELY inside one interval
    (the engine's all()-aggregation semantics for whole-bucket windows)."""
    end_min = start_min + dur_min
    return any(s <= start_min and end_min <= e for s, e in intervals)


def civil_light_bounds(lat, lon, local_date, utc_offset_hours):
    """(civil dawn local minute, civil dusk local minute) for one place-day,
    or (None, None) honestly when no civil-light crossing exists."""
    solar = solar_day_windows(lat, lon, local_date, utc_offset_hours)
    return solar["events"]["civil_dawn"], solar["events"]["civil_dusk"]


def window_intervals(lat, lon, local_date, utc_offset_hours, metric):
    """The minute-level intervals of ONE sun-elevation window metric for a
    place-day (local minutes), or [] when the metric never occurs."""
    solar = solar_day_windows(lat, lon, local_date, utc_offset_hours)
    return solar["intervals"].get(metric, [])
