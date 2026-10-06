"""Experimental photography-oriented diagnostics derived from CWA WRF fields.

These products are deliberately named as potentials/proxies.  They are not
native cloud fraction, observed fog, or calibrated probability forecasts.
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np

CLOUD_PROXY_VERSION = "cwa-rh-proxy-v1"
LOW_RH_LEVELS_HPA = (925, 850)
MID_RH_LEVELS_HPA = (700, 500)
HIGH_RH_LEVELS_HPA = (400, 300)


def _array(field: dict) -> np.ndarray:
    return np.asarray(field["values"], dtype=float)


def _grid_base(field: dict) -> dict:
    return {
        "latitudes": field["latitudes"],
        "longitudes": field["longitudes"],
    }


def _proxy_field(reference: dict, values, *, name: str, long_name: str, unit: str, derived_from: list[str], semantics: str) -> dict:
    return {
        **_grid_base(reference),
        "field_name": name,
        "field_attrs": {
            "short_name": name,
            "long_name": long_name,
            "source_units": unit,
            "normalized_units": unit,
            "product_type": "derived_proxy",
            "calibration_version": CLOUD_PROXY_VERSION,
            "calibration_status": "experimental_unvalidated",
            "derived_from": derived_from,
            "semantics": semantics,
            "native_cloud_fraction": False,
        },
        "values": np.asarray(values, dtype=float).tolist(),
    }


def _rh_field_name(level_hpa: int) -> str:
    return f"relative_humidity_{int(level_hpa)}hpa_percent"


def _stack_rh(fields: dict[str, dict], levels: Iterable[int]) -> tuple[np.ndarray, list[str]]:
    names = [_rh_field_name(level) for level in levels]
    missing = [name for name in names if name not in fields]
    if missing:
        raise ValueError(f"CWA derived model missing pressure-level RH fields: {missing}")
    arrays = [_array(fields[name]) for name in names]
    return np.stack(arrays, axis=0), names


def rh_cloud_potential(fields: dict[str, dict], levels: Iterable[int]) -> tuple[np.ndarray, list[str]]:
    """Map pressure-level RH to a bounded cloud-presence potential.

    The v1 transfer is intentionally transparent: 70% RH -> 0 potential and
    95% RH -> 100 potential, using the maximum RH in the requested pressure
    band.  This is a diagnostic proxy, not cloud fraction.
    """
    stacked, names = _stack_rh(fields, levels)
    max_rh = np.nanmax(stacked, axis=0)
    potential = np.clip((max_rh - 70.0) / 25.0, 0.0, 1.0) * 100.0
    return potential, names


def dewpoint_c_from_temperature_rh(temperature_c, rh_percent):
    t = np.asarray(temperature_c, dtype=float)
    rh = np.clip(np.asarray(rh_percent, dtype=float), 1.0e-3, 100.0)
    a = 17.625
    b = 243.04
    gamma = np.log(rh / 100.0) + (a * t) / (b + t)
    return (b * gamma) / (a - gamma)


def lcl_height_m_agl(temperature_c, rh_percent):
    """Approximate lifted condensation level above ground.

    Uses the common 125 m/K rule after estimating dew point with the Magnus
    relation.  It is an LCL diagnostic, not a measured cloud-base height.
    """
    t = np.asarray(temperature_c, dtype=float)
    td = dewpoint_c_from_temperature_rh(t, rh_percent)
    return np.clip(125.0 * np.maximum(t - td, 0.0), 0.0, 6000.0)


def derive_cwa_photography_fields(fields: dict[str, dict]) -> dict[str, dict]:
    required = (
        "temperature_2m_c",
        "relative_humidity_2m_percent",
        "wind_speed_10m_m_s",
    )
    missing = [name for name in required if name not in fields]
    if missing:
        raise ValueError(f"CWA derived model missing surface fields: {missing}")

    low, low_names = rh_cloud_potential(fields, LOW_RH_LEVELS_HPA)
    mid, mid_names = rh_cloud_potential(fields, MID_RH_LEVELS_HPA)
    high, high_names = rh_cloud_potential(fields, HIGH_RH_LEVELS_HPA)

    reference = fields["relative_humidity_2m_percent"]
    t2 = _array(fields["temperature_2m_c"])
    rh2 = _array(reference)
    wind = np.maximum(_array(fields["wind_speed_10m_m_s"]), 0.0)
    lcl = lcl_height_m_agl(t2, rh2)

    surface_saturation = np.clip((rh2 - 80.0) / 20.0, 0.0, 1.0)
    low_lcl = 1.0 - np.clip(lcl / 800.0, 0.0, 1.0)
    low_cloud = np.clip(low / 100.0, 0.0, 1.0)
    calm = 1.0 - np.clip(wind / 8.0, 0.0, 1.0)
    fog = np.clip(
        0.40 * surface_saturation
        + 0.30 * low_lcl
        + 0.20 * low_cloud
        + 0.10 * calm,
        0.0,
        1.0,
    ) * 100.0

    return {
        "rh_cloud_potential_low_percent": _proxy_field(
            reference,
            low,
            name="rh_cloud_potential_low_percent",
            long_name="CWA low-layer cloud presence potential from 925/850 hPa RH",
            unit="%",
            derived_from=low_names,
            semantics="RH-derived cloud-presence potential; not native cloud fraction",
        ),
        "rh_cloud_potential_mid_percent": _proxy_field(
            reference,
            mid,
            name="rh_cloud_potential_mid_percent",
            long_name="CWA middle-layer cloud presence potential from 700/500 hPa RH",
            unit="%",
            derived_from=mid_names,
            semantics="RH-derived cloud-presence potential; not native cloud fraction",
        ),
        "rh_cloud_potential_high_percent": _proxy_field(
            reference,
            high,
            name="rh_cloud_potential_high_percent",
            long_name="CWA high-layer cloud presence potential from 400/300 hPa RH",
            unit="%",
            derived_from=high_names,
            semantics="RH-derived cloud-presence potential; not native cloud fraction",
        ),
        "lcl_height_m_agl": _proxy_field(
            reference,
            lcl,
            name="lcl_height_m_agl",
            long_name="Estimated lifted condensation level above ground",
            unit="m AGL",
            derived_from=["temperature_2m_c", "relative_humidity_2m_percent"],
            semantics="thermodynamic LCL estimate; not observed or native model cloud base",
        ),
        "fog_potential_percent": _proxy_field(
            reference,
            fog,
            name="fog_potential_percent",
            long_name="Experimental near-surface fog potential",
            unit="%",
            derived_from=[
                "relative_humidity_2m_percent",
                "lcl_height_m_agl",
                "rh_cloud_potential_low_percent",
                "wind_speed_10m_m_s",
            ],
            semantics="diagnostic potential; not visibility and not a calibrated probability",
        ),
    }
