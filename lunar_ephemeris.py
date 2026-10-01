"""Low-cost lunar ephemeris contract for photography planning.

This module reuses the same dependency-free astronomy approximation already
used by ChaseLights. It is deterministic/replayable and is not intended for
navigation or scientific astrometry.
"""

from datetime import datetime, timezone
from fetch_data import _angular_separation, _moon_radec, _radec_to_altaz


GALACTIC_CORE_RA_DEG = 266.41683
GALACTIC_CORE_DEC_DEG = -29.00781
CONTRACT_VERSION = "b171b-approx-1"


def _utc(dt):
    if not isinstance(dt, datetime):
        raise TypeError("dt must be datetime")
    if dt.tzinfo is None:
        raise ValueError("dt must be timezone-aware")
    return dt.astimezone(timezone.utc)


def lunar_ephemeris(dt, lat_deg, lon_deg, target_ra_deg=None, target_dec_deg=None):
    dt = _utc(dt)
    moon_ra, moon_dec = _moon_radec(dt)
    moon_az, moon_alt = _radec_to_altaz(moon_ra, moon_dec, dt, lat_deg, lon_deg)

    # The existing ChaseLights illumination approximation uses Sun/Moon
    # elongation. Import lazily to keep this contract tied to the same math.
    from fetch_data import _sun_radec
    sun_ra, sun_dec = _sun_radec(dt)
    elong = _angular_separation(sun_ra, sun_dec, moon_ra, moon_dec)
    import math
    illumination = (1.0 - math.cos(math.radians(elong))) / 2.0

    target_sep = None
    if target_ra_deg is not None or target_dec_deg is not None:
        if target_ra_deg is None or target_dec_deg is None:
            raise ValueError("target RA and Dec must be supplied together")
        target_sep = _angular_separation(
            moon_ra, moon_dec, float(target_ra_deg), float(target_dec_deg)
        )

    return {
        "module": "lunar_ephemeris",
        "contract_version": CONTRACT_VERSION,
        "time_utc": dt.isoformat().replace("+00:00", "Z"),
        "moon_ra_deg": round(moon_ra, 3),
        "moon_dec_deg": round(moon_dec, 3),
        "moon_azimuth_deg": round(moon_az, 1),
        "moon_altitude_deg": round(moon_alt, 1),
        "moon_illumination_fraction": round(illumination, 4),
        "moon_target_separation_deg": (
            round(target_sep, 1) if target_sep is not None else None
        ),
        "planning_accuracy": "approximate",
        "scientific_astrometry": False,
    }


def lunar_ephemeris_for_galactic_core(dt, lat_deg, lon_deg):
    return lunar_ephemeris(
        dt, lat_deg, lon_deg,
        GALACTIC_CORE_RA_DEG, GALACTIC_CORE_DEC_DEG,
    )
