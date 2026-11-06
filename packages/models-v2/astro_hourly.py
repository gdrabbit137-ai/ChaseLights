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

from solar_window import _solar_altitude_deg  # noqa: E402
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

# CL-DATA-11: cloud-sea light window (owner ruling 2026-11-05: 雲海晚上除非有
# 月光否則看不到 — a sea of clouds is invisible at night without moonlight).
# A hour bucket qualifies only when EVERY sampled instant inside it has LIGHT:
# either civil daylight (sun elevation > -6 deg) or moonlight (moon above the
# horizon AND moon illumination fraction >= 0.5, using the existing
# moon_illumination_fraction semantics from lunar_ephemeris). A daytime hour
# passes on the solar branch alone; a dark, moonless hour (e.g. 23:00 local)
# can never qualify even when every weather condition passes. When the bucket
# is not fully sunlit and no moon data was requested, the metric is None
# (honest unknown) rather than a guess.
CIVIL_LIGHT_MIN_DEG = -6.0
MOON_LIGHT_MIN_ILLUMINATION = 0.5

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
    epoch = dt_utc.timestamp()
    samples = [epoch + off * 60.0 for off in WINDOW_SAMPLE_OFFSETS]
    altitudes = [_sun_altitude(datetime.fromtimestamp(t, timezone.utc), lat, lon)
                 for t in samples]
    out = {
        "astronomical_darkness": any(a <= DARKNESS_MAX_DEG for a in altitudes),
        "city_night_window": all(a <= CITY_NIGHT_MAX_DEG for a in altitudes),
        "golden_hour_window": any(GOLDEN_LOW_DEG <= a <= GOLDEN_HIGH_DEG
                                  for a in altitudes),
        "blue_hour_window": any(BLUE_LOW_DEG <= a <= BLUE_HIGH_DEG
                                for a in altitudes),
        # CL-DATA-11: cloud-sea light window. Solar branch first — a fully
        # sunlit bucket needs no moon data. Otherwise the moon branch decides
        # and requires lunar ephemeris per sample; without moon data the
        # metric is None (honest unknown).
        "light_window": None,
    }
    if all(a > CIVIL_LIGHT_MIN_DEG for a in altitudes):
        out["light_window"] = True
    elif need_moon:
        out["light_window"] = True
        for alt, off in zip(altitudes, WINDOW_SAMPLE_OFFSETS):
            if alt > CIVIL_LIGHT_MIN_DEG:
                continue
            sample_dt = datetime.fromtimestamp(epoch + off * 60.0, timezone.utc)
            lunar = lunar_ephemeris_for_galactic_core(sample_dt, lat, lon)
            moon_alt = lunar.get("moon_altitude_deg")
            illum = lunar.get("moon_illumination_fraction")
            moonlit = (moon_alt is not None and moon_alt > 0
                       and illum is not None
                       and illum >= MOON_LIGHT_MIN_ILLUMINATION)
            if not moonlit:
                out["light_window"] = False
                break
    for key, kind, half in (("sunrise_time_window", "sunrise", SUNRISE_HALF_WIDTH_MIN * 60),
                            ("sunset_window", "sunset", SUNSET_HALF_WIDTH_MIN * 60)):
        best = None
        for t in samples:
            for event_t, event_kind in events:
                if event_kind == kind:
                    delta = abs(event_t - t)
                    if best is None or delta < best:
                        best = delta
        out[key] = None if best is None else best <= half
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
