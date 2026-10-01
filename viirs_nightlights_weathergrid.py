"""Build a compact WeatherGrid contract for NASA Black Marble VNP46A4.

B169 models annual nighttime-light radiance as an environment layer. It does
not convert satellite upward radiance into Bortle class or zenith sky brightness.
"""

from __future__ import annotations

import math

FIELD_RADIANCE = "nighttime_lights_radiance_nw_cm2_sr"
FIELD_QUALITY = "nighttime_lights_quality_flag"
ENCODING_SCALE = 0.1
MAX_BROWSER_CELLS = 250_000

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


def _stride_for_budget(rows, cols, max_cells):
    stride = 1
    while math.ceil(rows / stride) * math.ceil(cols / stride) > max_cells:
        stride += 1
    return stride


def _downsample_grid(latitudes, longitudes, radiance, quality, max_cells):
    rows, cols = len(latitudes), len(longitudes)
    stride = _stride_for_budget(rows, cols, max_cells)
    if stride == 1:
        return list(latitudes), list(longitudes), list(radiance), list(quality), stride

    row_idx = list(range(0, rows, stride))
    col_idx = list(range(0, cols, stride))
    out_radiance, out_quality = [], []
    for ri in row_idx:
        for ci in col_idx:
            index = ri * cols + ci
            out_radiance.append(radiance[index])
            out_quality.append(quality[index])
    return (
        [latitudes[i] for i in row_idx],
        [longitudes[i] for i in col_idx],
        out_radiance,
        out_quality,
        stride,
    )


def build_bundle(latitudes, longitudes, radiance, quality, year, max_browser_cells=MAX_BROWSER_CELLS):
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
    if max_browser_cells < 4:
        raise ValueError("max_browser_cells must allow at least a 2x2 grid")

    source_rows, source_cols = rows, cols
    latitudes, longitudes, radiance, quality, browser_stride = _downsample_grid(
        latitudes, longitudes, radiance, quality, int(max_browser_cells)
    )
    rows, cols = len(latitudes), len(longitudes)
    expected = rows * cols

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
            "native_resolution": "15 arc-second",
            "browser_sampling_stride": browser_stride,
            "browser_grid_semantics": "display sampling; native VNP46A4 source remains 15 arc-second",
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
        "source_cell_count": source_rows * source_cols,
        "browser_sampling_stride": browser_stride,
        "browser_budget_cells": int(max_browser_cells),
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


def sample_bundle_at_location(bundle, latitude, longitude, qc=None):
    """Sample the nearest published VIIRS browser cell, preserving provenance.

    This samples the bounded browser artifact, not the native 15 arc-second
    archive. Callers must retain browser_sampling_stride and sampled coordinates
    so the evidence is never presented as native-resolution sampling.
    """
    if not isinstance(bundle, dict) or bundle.get("source") != "nasa_black_marble_vnp46a4":
        return None
    if qc is not None:
        if qc.get("source") != "nasa_black_marble_vnp46a4" or qc.get("flags"):
            return None

    grid = bundle.get("grid") or {}
    lats = grid.get("latitudes") or []
    lons = grid.get("longitudes") or []
    if not lats or not lons:
        return None

    lat = _finite(latitude)
    lon = _finite(longitude)
    if lat is None or lon is None:
        return None
    bbox = bundle.get("bbox") or {}
    try:
        if not (
            float(bbox["bottomlat"]) <= lat <= float(bbox["toplat"])
            and float(bbox["leftlon"]) <= lon <= float(bbox["rightlon"])
        ):
            return None
    except (KeyError, TypeError, ValueError):
        return None

    row = min(range(len(lats)), key=lambda i: abs(float(lats[i]) - lat))
    col = min(range(len(lons)), key=lambda i: abs(float(lons[i]) - lon))
    index = row * len(lons) + col
    frames = bundle.get("frames") or []
    if not frames:
        return None
    values = (frames[0].get("values") or {})
    radiance_values = values.get(FIELD_RADIANCE) or []
    quality_values = values.get(FIELD_QUALITY) or []
    if index >= len(radiance_values) or index >= len(quality_values):
        return None

    encoded = radiance_values[index]
    quality = quality_values[index]
    if encoded is None or quality is None:
        return None
    try:
        quality = int(quality)
        radiance = float(encoded) * float(
            (bundle.get("fields") or {}).get(FIELD_RADIANCE, {}).get("scale", ENCODING_SCALE)
        )
    except (TypeError, ValueError):
        return None

    sampled_lat = float(lats[row])
    sampled_lon = float(lons[col])
    # Approximate great-circle distance is only sampling provenance, not a
    # geodetic claim used by scoring.
    phi1, phi2 = math.radians(lat), math.radians(sampled_lat)
    dphi = phi2 - phi1
    dlambda = math.radians(sampled_lon - lon)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    distance_km = 6371.0088 * 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1 - a)))

    provenance = bundle.get("provenance") or {}
    return {
        FIELD_RADIANCE: radiance,
        FIELD_QUALITY: quality,
        "viirs_sample": {
            "source": bundle.get("source"),
            "product": provenance.get("product"),
            "composite_year": frames[0].get("composite_year"),
            "sampled_latitude": sampled_lat,
            "sampled_longitude": sampled_lon,
            "distance_km": round(distance_km, 3),
            "browser_sampling_stride": provenance.get("browser_sampling_stride", 1),
            "native_resolution": provenance.get("native_resolution"),
            "sampling_semantics": "nearest published browser-grid cell; not native-resolution sampling",
        },
    }
