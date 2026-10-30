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
- moon_illuminance_proxy: illumination_fraction × sin(moon_altitude), 0 below horizon
- galactic_core_altitude: lunar_ephemeris galactic-core contract

No weather, no scoring, no live recommendation. Deterministic per instant.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
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

# Solar-noon offset trick: local apparent noon in UTC minutes is derived from
# the altitude curve; we classify sunrise/sunset side by the altitude trend.


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
    """Astronomy metric values for one instant. `events` is the precomputed
    sun_events_span list for this coordinate (computed once per place when
    omitted). Window membership compares against the NEAREST crossing."""
    if events is None:
        epoch0 = dt_utc.timestamp()
        events = sun_events_span(lat, lon, epoch0 - 86400, epoch0 + 86400)
    altitude = _sun_altitude(dt_utc, lat, lon)
    out = {
        "astronomical_darkness": altitude <= DARKNESS_MAX_DEG,
        "golden_hour_window": GOLDEN_LOW_DEG <= altitude <= GOLDEN_HIGH_DEG,
        "blue_hour_window": BLUE_LOW_DEG <= altitude <= BLUE_HIGH_DEG,
    }
    epoch = dt_utc.timestamp()
    for key, kind, half in (("sunrise_time_window", "sunrise", SUNRISE_HALF_WIDTH_MIN * 60),
                            ("sunset_window", "sunset", SUNSET_HALF_WIDTH_MIN * 60)):
        best = None
        for event_t, event_kind in events:
            if event_kind == kind:
                delta = abs(event_t - epoch)
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
