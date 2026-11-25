"""Physical local-clock guards for the sunrise / sunset window families.

A sunrise window can only ever exist in the early morning LOCAL to the spot and
a sunset window only in the evening: a card that tells a user "sunrise 15:00"
destroys trust in every other number on the page, whatever the numeric cause
(offset slip, DST, unknown timezone falling back to UTC, an event list computed
for the wrong coordinate group). The evaluation layer therefore owns a hard
invariant, independent of how well the caller threaded the offset:

  * 'sunrise_time_window' samples must sit in local 04:30-08:30 AND within
    +/-40 min of the rising crossing AND have the sun in the eastern quadrant
    (azimuth 45-135 deg).
  * 'sunset_window' samples must sit in local 16:00-19:30 AND within +/-40 min
    of the setting crossing AND have the sun in the western quadrant
    (azimuth 225-315 deg).

These tests walk full days (24 hour buckets x 12 sub-hour samples) at several
latitudes — including the reported 七星潭 tw-036 spot — and assert the
invariant for every sample that qualifies, plus that the guard is not vacuous
(real morning / evening windows still exist).
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "astro_hourly", ROOT / "packages/models-v2/astro_hourly.py")
ah = importlib.util.module_from_spec(spec)
sys.modules.setdefault("astro_hourly", ah)
spec.loader.exec_module(ah)

SUNRISE_LOCAL_GUARD = (4 * 60 + 30, 8 * 60 + 30)     # 04:30-08:30 local
SUNSET_LOCAL_GUARD = (16 * 60, 19 * 60 + 30)         # 16:00-19:30 local
SUNRISE_QUADRANT = (45.0, 135.0)
SUNSET_QUADRANT = (225.0, 315.0)

# (label, lat, lon, utc_offset_hours, local date)
CASES = [
    ("tw-036 七星潭 Hualien", 24.031426, 121.62717, 8, "2026-11-21"),
    ("Tokyo mid-latitude", 35.6812, 139.7671, 9, "2026-11-21"),
    ("Reykjavik high-latitude winter", 64.1466, -21.9426, 0, "2026-11-21"),
    ("Tromso high-latitude midnight sun", 69.6492, 18.9553, 1, "2026-06-21"),
]


def _local_minute(epoch_s, offset_hours):
    return (((epoch_s + offset_hours * 3600.0) % 86400.0) + 86400.0) % 86400.0 / 60.0


def _in_guard(local_min, guard):
    start, end = guard
    if start <= end:
        return start <= local_min <= end
    return local_min >= start or local_min <= end


def _day_samples(lat, lon, offset_hours, local_date):
    """Every (bucket, sample_epoch) of the 24 local hours of `local_date`."""
    y, m, d = (int(part) for part in local_date.split("-"))
    local_midnight = (datetime(y, m, d, tzinfo=timezone.utc)
                      - timedelta(hours=offset_hours))
    for hour in range(24):
        bucket = local_midnight + timedelta(hours=hour)
        samples = [bucket.timestamp() + off * 60.0
                   for off in ah.WINDOW_SAMPLE_OFFSETS]
        yield bucket, samples


def _profiles_for_day(lat, lon, offset_hours, local_date):
    for bucket, samples in _day_samples(lat, lon, offset_hours, local_date):
        events = ah.sun_events_span(lat, lon, bucket.timestamp() - 86400,
                                    bucket.timestamp() + 86400)
        profiles = ah.window_pass_profiles(
            bucket, lat, lon, events=events,
            utc_offset_seconds=offset_hours * 3600)
        yield bucket, samples, events, profiles


def test_sunrise_never_outside_local_morning_guard():
    for label, lat, lon, offset, date in CASES:
        for bucket, samples, events, profiles in _profiles_for_day(
                lat, lon, offset, date):
            for i, epoch in enumerate(samples):
                if not profiles["sunrise_time_window"][i]:
                    continue
                local_min = _local_minute(epoch, offset)
                assert _in_guard(local_min, SUNRISE_LOCAL_GUARD), (
                    f"{label} {bucket.isoformat()}: sunrise sample "
                    f"{int(local_min) // 60:02d}:{int(local_min) % 60:02d} "
                    f"local is outside 04:30-08:30")
                at = datetime.fromtimestamp(epoch, timezone.utc)
                az = ah._sun_azimuth(at, lat, lon)
                assert az is not None, f"{label}: no azimuth at sunrise sample"
                assert SUNRISE_QUADRANT[0] <= az <= SUNRISE_QUADRANT[1], (
                    f"{label} {bucket.isoformat()}: sunrise sample azimuth "
                    f"{az:.1f} not in the eastern quadrant 45-135")
                nearest = min(abs(t - epoch) for t, k in events if k == "sunrise")
                assert nearest <= ah.SUNRISE_HALF_WIDTH_MIN * 60, (
                    f"{label}: sunrise sample {nearest / 60:.1f} min from any "
                    f"rising crossing")


def test_sunset_never_outside_local_evening_guard():
    for label, lat, lon, offset, date in CASES:
        for bucket, samples, events, profiles in _profiles_for_day(
                lat, lon, offset, date):
            for i, epoch in enumerate(samples):
                if not profiles["sunset_window"][i]:
                    continue
                local_min = _local_minute(epoch, offset)
                assert _in_guard(local_min, SUNSET_LOCAL_GUARD), (
                    f"{label} {bucket.isoformat()}: sunset sample "
                    f"{int(local_min) // 60:02d}:{int(local_min) % 60:02d} "
                    f"local is outside 16:00-19:30")
                at = datetime.fromtimestamp(epoch, timezone.utc)
                az = ah._sun_azimuth(at, lat, lon)
                assert az is not None, f"{label}: no azimuth at sunset sample"
                assert SUNSET_QUADRANT[0] <= az <= SUNSET_QUADRANT[1], (
                    f"{label} {bucket.isoformat()}: sunset sample azimuth "
                    f"{az:.1f} not in the western quadrant 225-315")
                nearest = min(abs(t - epoch) for t, k in events if k == "sunset")
                assert nearest <= ah.SUNSET_HALF_WIDTH_MIN * 60, (
                    f"{label}: sunset sample {nearest / 60:.1f} min from any "
                    f"setting crossing")


def test_guard_is_not_vacuous_for_a_mid_latitude_spot():
    """tw-036 must still get its real morning and evening windows."""
    label, lat, lon, offset, date = CASES[0]
    sunrise_hours, sunset_hours = [], []
    for bucket, samples, events, profiles in _profiles_for_day(
            lat, lon, offset, date):
        local_hh = _local_minute(bucket.timestamp(), offset) // 60
        if any(profiles["sunrise_time_window"]):
            sunrise_hours.append(int(local_hh))
        if any(profiles["sunset_window"]):
            sunset_hours.append(int(local_hh))
    assert sunrise_hours, f"{label}: the guard swallowed every sunrise window"
    assert sunset_hours, f"{label}: the guard swallowed every sunset window"
    assert all(4 <= h <= 8 for h in sunrise_hours), sunrise_hours
    assert all(16 <= h <= 19 for h in sunset_hours), sunset_hours


def test_hour_observations_respects_the_guard():
    """The aggregated hour verdicts must inherit the guard, not bypass it."""
    label, lat, lon, offset, date = CASES[0]
    for bucket, _samples, events, _profiles in _profiles_for_day(
            lat, lon, offset, date):
        obs = ah.hour_observations(bucket, lat, lon, events=events,
                                   utc_offset_seconds=offset * 3600)
        local_min = _local_minute(bucket.timestamp(), offset)
        if obs["sunrise_time_window"]:
            assert _in_guard(local_min, SUNRISE_LOCAL_GUARD), (
                f"{label} {bucket.isoformat()}: hour verdict claims a sunrise "
                f"window at {int(local_min) // 60:02d}:{int(local_min) % 60:02d} local")
        if obs["sunset_window"]:
            assert _in_guard(local_min, SUNSET_LOCAL_GUARD), (
                f"{label} {bucket.isoformat()}: hour verdict claims a sunset "
                f"window at {int(local_min) // 60:02d}:{int(local_min) % 60:02d} local")
