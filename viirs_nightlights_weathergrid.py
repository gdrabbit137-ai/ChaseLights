"""Build a compact WeatherGrid contract for NASA Black Marble VNP46A4.

B169 models annual nighttime-light radiance as an environment layer. It does
not convert satellite upward radiance into Bortle class or zenith sky brightness.
"""

from __future__ import annotations

import math

FIELD_RADIANCE = "nighttime_lights_radiance_nw_cm2_sr"
FIELD_QUALITY = "nighttime_lights_quality_flag"
ENCODING_SCALE = 0.1

SOURCE_PRODUCT = "VNP46A4"
SOURCE_SDS = "AllAngle_Composite_Snow_Free"
SOURCE_QUALITY_SDS = "AllAngle_Composite_Snow_Free_Quality"
SOURCE_DOI = "10.5067/VIIRS/VNP46A4.002"


def _finite(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def build_bundle(latitudes, longitudes, radiance, quality, year):
    """Build one annual frame from normalized VNP46A4 arrays.

    Input radiance must already be decoded to nW/(cm^2 sr), independent of the
    source collection's storage dtype/scale. Quality follows the product flag:
    0 good, 1 poor, 2 gap-filled, 255 fill.
    """
    rows, cols = len(latitudes), len(longitudes)
    expected = rows * cols
    if rows < 2 or cols < 2:
        raise ValueError("nighttime-light grid must be at least 2x2")
    if len(radiance) != expected or len(quality) != expected:
        raise ValueError("radiance/quality cell count does not match grid")

    encoded = []
    q_values = []
    counts = {"good": 0, "poor": 0, "gap_filled": 0, "fill": 0, "other": 0}
    finite_values = []

    for raw, q_raw in zip(radiance, quality):
        q = int(q_raw) if q_raw is not None else 255
        if q == 0:
            counts["good"] += 1
        elif q == 1:
            counts["poor"] += 1
        elif q == 2:
            counts["gap_filled"] += 1
        elif q == 255:
            counts["fill"] += 1
        else:
            counts["other"] += 1

        value = _finite(raw)
        if q == 255 or value is None or value < 0:
            encoded.append(None)
            q_values.append(None if q == 255 else q)
            continue
        finite_values.append(value)
        encoded.append(int(round(value / ENCODING_SCALE)))
        q_values.append(q)

    year = int(year)
    bundle = {
        "schema_version": "weathergrid-browser-v1",
        "source": "nasa_black_marble_vnp46a4",
        "time_semantics": "annual_composite_environment_baseline",
        "grid": {
            "rows": rows,
            "cols": cols,
            "latitudes": [float(v) for v in latitudes],
            "longitudes": [float(v) for v in longitudes],
        },
        "bbox": {
            "leftlon": float(min(longitudes)),
            "rightlon": float(max(longitudes)),
            "bottomlat": float(min(latitudes)),
            "toplat": float(max(latitudes)),
        },
        "fields": {
            FIELD_RADIANCE: {
                "unit": "nW/(cm²·sr)",
                "encoding": "integer_scaled",
                "scale": ENCODING_SCALE,
                "decode": f"value * {ENCODING_SCALE}",
                "null": "missing",
                "quantity": "annual_nighttime_lights_radiance",
                "source_sds": SOURCE_SDS,
            },
            FIELD_QUALITY: {
                "unit": "quality flag",
                "encoding": "integer",
                "scale": 1,
                "decode": "value",
                "null": "fill_or_missing",
                "quantity": "vnp46a4_quality_flag",
                "source_sds": SOURCE_QUALITY_SDS,
                "flag_meaning": {"0": "good", "1": "poor", "2": "gap_filled"},
            },
        },
        "frames": [{
            "valid_time_utc": f"{year:04d}-07-02T00:00:00+00:00",
            "composite_year": year,
            "values": {
                FIELD_RADIANCE: encoded,
                FIELD_QUALITY: q_values,
            },
        }],
        "provenance": {
            "provider": "NASA LAADS DAAC",
            "product": SOURCE_PRODUCT,
            "collection": "2",
            "doi": SOURCE_DOI,
            "native_resolution": "15 arc-second (~500 m at equator)",
            "temporal_resolution": "annual",
            "source_sds": SOURCE_SDS,
            "quality_sds": SOURCE_QUALITY_SDS,
            "semantics": (
                "satellite-observed annual nighttime-light radiance; "
                "not Bortle class and not zenith sky brightness"
            ),
        },
    }
    qc = {
        "schema_version": "weathergrid-qc-v1",
        "source": "nasa_black_marble_vnp46a4",
        "composite_year": year,
        "cell_count": expected,
        "radiance": {
            "missing": expected - len(finite_values),
            "min": min(finite_values) if finite_values else None,
            "max": max(finite_values) if finite_values else None,
            "mean": sum(finite_values) / len(finite_values) if finite_values else None,
        },
        "quality_counts": counts,
        "flags": ([] if finite_values else ["all_missing"]),
    }
    return bundle, qc
