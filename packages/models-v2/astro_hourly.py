"""Per-hour astronomy observations for V2 opportunity evaluation.

Pure geometry from coordinates + instants using the existing dependency-free
contracts (models-v2.solar_window solar altitude; lunar_ephemeris moon/core).
Window definitions come from metric-vocabulary.json notes and
GENRE_CONDITION_TEMPLATES.md:

- sunrise_time_window: sunrise ±40 min (local solar computation)
- sunset_window: sunset ±40 min
- blue_hour_window: sun elevation between -8° and -4°
- golden_hour_window: sun elevation between -6° and +6°
- astronomical_darkness: sun elevation <= -18°
- city_night_window: EVERY sampled instant in the hour bucket has sun
  elevation <= -6° (civil darkness) — CL-UI-23 evaluation-layer gate for
  city_night contracts that carry no contract-level time window yet
- light_window: EVERY sampled instant in the hour bucket has sun elevation
  > -6° (civil light) — CL-DATA-11 cloud-sea visibility window; night hours
  never qualify regardless of the moon (owner clarification 2026-11-05)
- moon_illuminance_proxy: illumination_fraction × sin(moon_altitude), 0 below horizon
- galactic_core_altitude: lunar_ephemeris galactic-core contract

No weather, no scoring, no live recommendation. Deterministic per instant.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import sys
from pathlib import Path

# repo root = packages/models-v2/astro_hourly.py -> parents[2]
_REPO = Path(__file__).resolve().parents[2]
for entry in (str(_REPO / "packages" / "models-v2"), str(_REPO)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from solar_window import _solar_altitude_deg, _solar_azimuth_deg  # noqa: E402
from lunar_ephemeris import (  # noqa: E402
    GALACTIC_CORE_DEC_DEG, GALACTIC_CORE_RA_DEG, lunar_ephemeris_for_galactic_core,
)

SUNRISE_HALF_WIDTH_MIN = 40
SUNSET_HALF_WIDTH_MIN = 40
BLUE_LOW_DEG = -8.0
BLUE_HIGH_DEG = -4.0
GOLDEN_LOW_DEG = -6.0
GOLDEN_HIGH_DEG = 6.0
DARKNESS_MAX_DEG = -18.0
# CL-UI-23: night-subject hours gate (evaluation layer). A city-night hour
# bucket qualifies only when EVERY sampled instant inside [h, h+1h) has the
# sun at or below -6° (civil darkness): city lights are the subject, so a
# daytime or mid-dusk hour must never appear as a "good hour" even when the
# weather conditions alone would pass.
CITY_NIGHT_MAX_DEG = -6.0

# CL-DATA-11: cloud-sea light window (owner ruling 2026-11-05, clarified same
# day: 夜間一律不符合 — a sea of clouds is visible ONLY in civil light; the
# earlier "moonlit night" reading was an owner rhetorical question, not a
# ruling, and the moonlight exception is withdrawn). The hour bucket qualifies
# only when EVERY sampled instant inside it has sun elevation > -6 deg (civil
# light). A dark hour (e.g. 23:00 local) can never qualify regardless of the
# moon, even when the weather conditions all pass. Pure solar geometry: no
# moon data is consulted.
CIVIL_LIGHT_MIN_DEG = -6.0

# CL-DATA-24: the sun's phase for an hour bucket — "dawn" (morning side of
# the day, nearest horizon crossing is a sunrise) or "dusk" (evening side,
# nearest crossing is a sunset). blue_hour_window / golden_hour_window are
# symmetric by elevation alone, so a dusk-named subject evaluated without a
# phase constraint matched 05:00 morning twilight hours as well; the phase
# scalar lets window conditions declare `phase: dusk|dawn` and the evaluator
# keeps only the phase the subject name names.
SUN_PHASE = ("dawn", "dusk")

# CL-UI-08: window metrics are evaluated by SUB-HOUR INTERVAL SAMPLING, not by
# the single grid instant. Narrow windows (blue hour 20-50 min, sunrise/sunset
# ±40 min, golden hour) can fall entirely between two whole-hour grid points;
# sampling the hour bucket [h, h+1h) at SUBHOUR_STEP_MIN guarantees that any
# window at least one step wide is detected (any interval longer than the step
# contains a step-aligned sample). Provenance for the sampling regime is
# published with the evaluation artifacts (see evaluate_batch.py).
SUBHOUR_STEP_MIN = 5
WINDOW_SAMPLE_OFFSETS = list(range(0, 60, SUBHOUR_STEP_MIN))
ASTRO_SAMPLING_PROVENANCE = {
    "mode": "sub_hour_interval_scan",
    "step_minutes": SUBHOUR_STEP_MIN,
    "samples_per_hour": len(WINDOW_SAMPLE_OFFSETS),
    "sample_offsets_minutes": WINDOW_SAMPLE_OFFSETS,
    "metrics": ["astronomical_darkness", "city_night_window", "golden_hour_window",
                "blue_hour_window", "sunrise_time_window", "sunset_window",
                "light_window"],
    "bucket": "[hour_start, hour_start+60min)",
}


def _sun_altitude(dt_utc, lat, lon):
    return _solar_altitude_deg(dt_utc.astimezone(timezone.utc), lat, lon)


def _sun_phase(altitudes):
    """CL-DATA-24: the hour bucket's phase, from the sun's rise/set direction
    — the altitude curve ascends on the dawn side of the day (midnight to
    solar noon) and descends on the dusk side (solar noon to midnight). The
    first vs last sub-hour sample sign splits the symmetric elevation windows
    (blue/golden hour) into their morning vs evening half: rising -> "dawn",
    falling -> "dusk". A bucket straddling the noon/midnight turning point
    defaults to "dusk"; no twilight window is active there anyway. Derived
    from the already-sampled altitudes, so no extra events list is needed and
    the result is exact at every span edge (no truncated-events bias)."""
    if len(altitudes) < 2:
        return None
    return "dawn" if altitudes[-1] > altitudes[0] else "dusk"


def _sun_azimuth(dt_utc, lat, lon):
    """CL-DATA-13: solar azimuth (0-360, north=0) from the same NOAA/Meeus
    chain as the altitude — same source, same sampling granularity (the grid
    instant). Out-of-range outputs (impossible by construction, guarded
    anyway) degrade honestly to None so QC failures propagate as unknown
    instead of a wrong direction."""
    try:
        value = _solar_azimuth_deg(dt_utc.astimezone(timezone.utc), lat, lon)
    except Exception:
        return None
    return value if 0.0 <= value <= 360.0 else None


def sun_events_span(lat, lon, start_epoch, end_epoch, step_s=600):
    """All sunrise/sunset crossings in [start, end] at step resolution,
    linearly interpolated to the crossing second. Compute once per place/span;
    the altitude curve is monotonic between crossings, so a 10-minute scan
    with linear interpolation stays within ~1 minute of the true event."""
    events = []
    previous_alt = _sun_altitude(datetime.fromtimestamp(start_epoch, timezone.utc), lat, lon)
    previous_t = start_epoch
    t = start_epoch
    while t < end_epoch:
        t += step_s
        current = _sun_altitude(datetime.fromtimestamp(t, timezone.utc), lat, lon)
        if previous_alt <= 0 < current:
            frac = (0 - previous_alt) / (current - previous_alt)
            events.append((previous_t + frac * step_s, "sunrise"))
        elif previous_alt >= 0 > current:
            frac = (previous_alt - 0) / (previous_alt - current)
            events.append((previous_t + frac * step_s, "sunset"))
        previous_alt, previous_t = current, t
    return events


def _bucket_altitudes(dt_utc, lat, lon, events=None):
    """The WINDOW_SAMPLE_OFFSETS grid instants and their sun altitudes for one
    hour bucket — the shared sample base of hour_observations and
    window_pass_profiles. `events` is computed here when omitted (same
    convention as hour_observations)."""
    if events is None:
        epoch0 = dt_utc.timestamp()
        events = sun_events_span(lat, lon, epoch0 - 86400, epoch0 + 86400)
    epoch = dt_utc.timestamp()
    samples = [epoch + off * 60.0 for off in WINDOW_SAMPLE_OFFSETS]
    altitudes = [_sun_altitude(datetime.fromtimestamp(t, timezone.utc), lat, lon)
                 for t in samples]
    return samples, altitudes, events


def window_pass_profiles(dt_utc, lat, lon, events=None):
    """CL-DATA-31: per-sample pass booleans for every sub-hour window metric,
    over the SAME [dt, dt+60min) bucket and WINDOW_SAMPLE_OFFSETS grid that
    hour_observations aggregates with any()/all(). A bucket qualifies when ANY
    sample sits inside a narrow window (e.g. sunrise ±40 min), so a
    bucket-start stamp can LEAD the actual window by up to ~55 minutes — a
    06:05 sunrise marks the 05:00 bucket qualifying even though its window
    only opens 05:25 (sun still below −10° at 05:00; challenger audit
    2026-11-08). The evaluator uses the profiles to stamp a qualifying bucket
    at its EARLIEST passing sample instead of the bucket start, so a
    qualifying-hour label never claims light earlier than the window provides."""
    if events is None:
        epoch0 = dt_utc.timestamp()
        events = sun_events_span(lat, lon, epoch0 - 86400, epoch0 + 86400)
    samples, altitudes, events = _bucket_altitudes(dt_utc, lat, lon, events)
    profiles = {
        "astronomical_darkness": [a <= DARKNESS_MAX_DEG for a in altitudes],
        "city_night_window": [a <= CITY_NIGHT_MAX_DEG for a in altitudes],
        "golden_hour_window": [GOLDEN_LOW_DEG <= a <= GOLDEN_HIGH_DEG
                               for a in altitudes],
        "blue_hour_window": [BLUE_LOW_DEG <= a <= BLUE_HIGH_DEG
                             for a in altitudes],
        "light_window": [a > CIVIL_LIGHT_MIN_DEG for a in altitudes],
        "sunrise_time_window": [False] * len(samples),
        "sunset_window": [False] * len(samples),
    }
    for key, kind, half in (("sunrise_time_window", "sunrise",
                             SUNRISE_HALF_WIDTH_MIN * 60),
                            ("sunset_window", "sunset",
                             SUNSET_HALF_WIDTH_MIN * 60)):
        for i, t in enumerate(samples):
            best = None
            for event_t, event_kind in events:
                if event_kind == kind:
                    delta = abs(event_t - t)
                    if best is None or delta < best:
                        best = delta
            profiles[key][i] = best is not None and best <= half
    return profiles


def hour_observations(dt_utc, lat, lon, events=None, need_moon=False):
    """Astronomy metric values for one hour bucket. `events` is the precomputed
    sun_events_span list for this coordinate (computed once per place when
    omitted). Window metrics are evaluated by SUB-HOUR INTERVAL SAMPLING over
    the bucket [dt, dt+60min) at SUBHOUR_STEP_MIN spacing: a window metric is
    PASS for the hour if ANY sampled instant inside the bucket falls inside the
    window. This removes the systematic false negative where a narrow window
    (blue hour, sunrise/sunset, golden hour) falls entirely between two
    whole-hour grid points. Altitude-based membership compares the sampled
    altitude against the window bounds; sunrise/sunset membership compares
    each sample against the NEAREST crossing of that kind. Non-window metrics
    (moon/galactic-core) remain evaluated at the grid instant."""
    if events is None:
        epoch0 = dt_utc.timestamp()
        events = sun_events_span(lat, lon, epoch0 - 86400, epoch0 + 86400)
    # CL-DATA-31: hour_observations is exactly the any()/all() aggregation of
    # the per-sample window profiles over the same bucket and sampling grid,
    # so both functions share one code path and can never drift.
    profiles = window_pass_profiles(dt_utc, lat, lon, events=events)
    # CL-DATA-13: azimuth at the grid instant — same chain and same sampling
    # granularity as the altitude scalar (windows sample; scalars don't).
    out = {
        "sun_azimuth_deg": _sun_azimuth(dt_utc, lat, lon),
        "phase": _sun_phase(_bucket_altitudes(dt_utc, lat, lon, events)[1]),
        "astronomical_darkness": any(profiles["astronomical_darkness"]),
        "city_night_window": all(profiles["city_night_window"]),
        "golden_hour_window": any(profiles["golden_hour_window"]),
        "blue_hour_window": any(profiles["blue_hour_window"]),
        # CL-DATA-11: cloud-sea light window — pure civil-light geometry.
        "light_window": all(profiles["light_window"]),
    }
    # No crossing of that kind within the events span (polar day/night):
    # propagate UNKNOWN honestly (None), never a False FAIL.
    for key, kind in (("sunrise_time_window", "sunrise"),
                      ("sunset_window", "sunset")):
        out[key] = (any(profiles[key]) if any(e_kind == kind
                                              for _, e_kind in events) else None)
    if need_moon:
        out.update(moon_observation(dt_utc, lat, lon))
    return out


def moon_observation(dt_utc, lat, lon):
    lunar = lunar_ephemeris_for_galactic_core(dt_utc, lat, lon)
    altitude = lunar.get("moon_altitude_deg")
    separation = lunar.get("moon_target_separation_deg")
    # Moon below the horizon = zero interference: the separation gate
    # (moon_target_separation_deg, "moon at least 40 deg from the core")
    # is vacuously satisfied, so report a large sentinel instead of None
    # (None would propagate UNKNOWN and wrongly block the night hours).
    if altitude is not None and altitude < 0:
        separation = 999.0
    illumination = lunar.get("moon_illumination_fraction")
    proxy = None
    if altitude is not None and illumination is not None:
        proxy = illumination * math.sin(math.radians(altitude)) if altitude > 0 else 0.0
    core_altitude = None
    # lunar_ephemeris_for_galactic_core targets the core for separation; the
    # core altitude itself is computed from its RA/Dec via the same alt/az math.
    from fetch_data import _radec_to_altaz  # same approximation chain
    core_az, core_alt = _radec_to_altaz(
        GALACTIC_CORE_RA_DEG, GALACTIC_CORE_DEC_DEG, dt_utc, lat, lon)
    core_altitude = core_alt
    return {
        "moon_altitude": altitude,
        "moon_illumination_fraction": illumination,
        "moon_target_separation_deg": separation,
        "moon_illuminance_proxy": proxy,
        "galactic_core_altitude": core_altitude,
    }
