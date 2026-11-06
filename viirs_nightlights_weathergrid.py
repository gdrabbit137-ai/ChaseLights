"""Build a compact WeatherGrid contract for daily NASA GIBS VIIRS DNB.

CL-CI-20: models DAILY nighttime-light radiance as an environment layer from
the NASA GIBS public WMTS rendered VIIRS DayNightBand tiles (NOAA-20 primary;
Suomi NPP layers survive only as a historical archive). It does not convert
satellite radiance into Bortle class or zenith sky brightness.

Honest limitations (B169 quality labeling):
- daily raw DNB is CLOUD-AFFECTED, not a cloud-free composite;
- no per-pixel quality flags exist in the rendered GIBS layer;
- values are colormap-bin-quantized inversions of the rendered PNG.
"""

from __future__ import annotations

import math

FIELD_RADIANCE = "nighttime_lights_radiance_nw_cm2_sr"
ENCODING_SCALE = 0.01
MAX_BROWSER_CELLS = 250_000

SOURCE = "nasa_gibs_viirs_noaa20_dnb"
SOURCE_LAYER = "VIIRS_NOAA20_DayNightBand_At_Sensor_Radiance"
SOURCE_LAYER_SNPP_HISTORICAL = "VIIRS_SNPP_DayNightBand_At_Sensor_Radiance"
SOURCE_LAYER_COLORMAP_URL = (
    "https://gibs.earthdata.nasa.gov/colormaps/v1.3/"
    "VIIRS_DayNightBand_At_Sensor_Radiance.xml"
)
SOURCE_LAYER_COLORMAP_VERSION = "v1.3"
SOURCE_DISTRIBUTION = "NASA EOSDIS GIBS public WMTS (no authentication)"
CLOUD_CAVEAT = (
    "daily raw DNB contains cloud contamination; this is NOT a cloud-free "
    "composite and GIBS rendered tiles carry no per-pixel quality flags"
)
LAADS_DEAD_END = (
    "legacy LAADS VNP46A4 path is a dead end: Suomi NPP data supply was "
    "terminated 2026-11-01 and VNP46A4 is an SNPP product (product lifecycle "
    "end-of-life), so the annual composite can no longer be sourced"
)


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


def _downsample_grid(latitudes, longitudes, radiance, max_cells):
    rows, cols = len(latitudes), len(longitudes)
    stride = _stride_for_budget(rows, cols, max_cells)
    if stride == 1:
        return list(latitudes), list(longitudes), list(radiance), stride

    row_idx = list(range(0, rows, stride))
    col_idx = list(range(0, cols, stride))
    out_radiance = []
    for ri in row_idx:
        for ci in col_idx:
            index = ri * cols + ci
            out_radiance.append(radiance[index])
    return (
        [latitudes[i] for i in row_idx],
        [longitudes[i] for i in col_idx],
        out_radiance,
        stride,
    )


def build_bundle(
    latitudes,
    longitudes,
    radiance,
    observation_date,
    source_layer=SOURCE_LAYER,
    tile_level=6,
    max_browser_cells=MAX_BROWSER_CELLS,
):
    """Build one daily frame from colormap-decoded GIBS DNB radiance values.

    Input radiance must already be decoded to nW/(cm^2 sr) via the GIBS
    colormap LUT (see viirs_nightlights_ingest). None cells stay null.
    """
    rows, cols = len(latitudes), len(longitudes)
    expected = rows * cols
    if rows < 2 or cols < 2:
        raise ValueError("nighttime-light grid must be at least 2x2")
    if len(radiance) != expected:
        raise ValueError("radiance cell count does not match grid")
    if max_browser_cells < 4:
        raise ValueError("max_browser_cells must allow at least a 2x2 grid")

    source_rows, source_cols = rows, cols
    latitudes, longitudes, radiance, browser_stride = _downsample_grid(
        latitudes, longitudes, radiance, int(max_browser_cells)
    )
    rows, cols = len(latitudes), len(longitudes)
    expected = rows * cols

    encoded = []
    finite_values = []
    for raw in radiance:
        value = _finite(raw)
        if value is None or value < 0:
            encoded.append(None)
            continue
        finite_values.append(value)
        encoded.append(int(round(value / ENCODING_SCALE)))

    date = str(observation_date)
    bundle = {
        "schema_version": "weathergrid-browser-v1",
        "source": SOURCE,
        "time_semantics": "daily_raw_dnb_cloud_affected_environment_baseline",
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
                "unit": "nW/(cm²\u00b7sr)",
                "encoding": "integer_scaled",
                "scale": ENCODING_SCALE,
                "decode": f"value * {ENCODING_SCALE}",
                "null": "missing",
                "quantity": "daily_nighttime_lights_radiance",
                "quantization": "GIBS colormap bin midpoint (bin width 0.1-0.6)",
            },
        },
        "frames": [{
            "valid_time_utc": f"{date}T00:00:00+00:00",
            "observation_date": date,
            "values": {
                FIELD_RADIANCE: encoded,
            },
        }],
        "provenance": {
            "provider": "NASA EOSDIS GIBS",
            "source_layer": source_layer,
            "source_layer_snpp_historical": SOURCE_LAYER_SNPP_HISTORICAL,
            "source_layer_snpp_note": (
                "Suomi NPP DNB GIBS layers are a historical archive with gaps "
                "only; the SNPP data supply terminated 2026-11-01"
            ),
            "distribution": SOURCE_DISTRIBUTION,
            "observation_date": date,
            "tile_matrix_set": "500m",
            "tile_level": int(tile_level),
            "native_resolution": "500 m",
            "browser_sampling_stride": browser_stride,
            "browser_grid_semantics": (
                "display sampling at WMTS tile level {0}; native source "
                "remains 500 m".format(int(tile_level))
            ),
            "temporal_resolution": "daily",
            "colormap_url": SOURCE_LAYER_COLORMAP_URL,
            "colormap_version": SOURCE_LAYER_COLORMAP_VERSION,
            "colormap_fetched": "2026-11-07",
            "cloud_caveat": CLOUD_CAVEAT,
            "laads_dead_end": LAADS_DEAD_END,
            "semantics": (
                "satellite-observed daily nighttime-light radiance; "
                "not Bortle class and not zenith sky brightness"
            ),
        },
    }
    qc = {
        "schema_version": "weathergrid-qc-v1",
        "source": SOURCE,
        "observation_date": date,
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
        "limitations": [
            CLOUD_CAVEAT,
            "values are GIBS colormap-bin inversions of rendered tiles, not raw HDF5 radiance",
            LAADS_DEAD_END,
        ],
        "flags": ([] if finite_values else ["all_missing"]),
    }
    return bundle, qc


def sample_bundle_at_location(bundle, latitude, longitude, qc=None):
    """Sample the nearest published VIIRS browser cell, preserving provenance.

    This samples the bounded browser artifact, not the native 500 m archive.
    Callers must retain browser_sampling_stride and sampled coordinates
    so the evidence is never presented as native-resolution sampling.
    The GIBS daily layer carries no per-pixel quality flag; the returned
    quality is None and consumers must treat dark-sky evidence accordingly.
    """
    if not isinstance(bundle, dict) or bundle.get("source") != SOURCE:
        return None
    if qc is not None:
        if qc.get("source") != SOURCE or qc.get("flags"):
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
    if index >= len(radiance_values):
        return None

    encoded = radiance_values[index]
    if encoded is None:
        return None
    try:
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
        "viirs_sample": {
            "source": bundle.get("source"),
            "source_layer": provenance.get("source_layer"),
            "observation_date": frames[0].get("observation_date"),
            "sampled_latitude": sampled_lat,
            "sampled_longitude": sampled_lon,
            "distance_km": round(distance_km, 3),
            "browser_sampling_stride": provenance.get("browser_sampling_stride", 1),
            "native_resolution": provenance.get("native_resolution"),
            "quality_flag": None,
            "quality_note": provenance.get("cloud_caveat"),
            "sampling_semantics": "nearest published browser-grid cell; not native-resolution sampling",
        },
    }
