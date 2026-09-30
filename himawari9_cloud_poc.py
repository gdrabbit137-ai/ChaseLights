#!/usr/bin/env python3
"""B155 live probe for JMA Himawari-9 observed cloud products on NOAA NODD."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

BUCKET = "noaa-himawari9"
PRODUCT_ROOT = "AHI-L2-FLDK-Clouds"
MASK_PREFIX = "AHI-CMSK_"
HEIGHT_PREFIX = "AHI-CHGT_"

# Himawari AHI 2 km Full Disk is a fixed 5500 x 5500 normalized
# geostationary grid. Use the nominal 2 km projection-plane spacing only to
# predict a small read window, then verify that window against the product's
# own Latitude/Longitude arrays before trusting it.
FULL_DISK_PIXELS = 5500
NOMINAL_PIXEL_SIZE_M = 2000.0
NOMINAL_HALF_EXTENT_M = FULL_DISK_PIXELS * NOMINAL_PIXEL_SIZE_M / 2.0
TAIWAN_BBOX = {
    "leftlon": 119.5,
    "rightlon": 123.0,
    "bottomlat": 21.5,
    "toplat": 26.0,
}

# Standard Himawari AHI 2 km Full Disk fixed grid.
# JMA HSD navigation uses a 140.7E sub-satellite longitude.  Satpy's
# himawari_ahi_fes_2km definition expresses the 5500 x 5500 fixed grid as a
# geostationary projection with this exact area extent.
HIMAWARI_GRID_SIZE = 5500
HIMAWARI_SUB_LON_DEG = 140.7
HIMAWARI_HEIGHT_M = 35785863.0
HIMAWARI_SEMI_MAJOR_M = 6378137.0
HIMAWARI_INV_FLATTENING = 298.257024882273
HIMAWARI_AREA_EXTENT_M = (
    -5499999.9012,
    -5499999.9012,
    5499999.9012,
    5499999.9012,
)
TAIWAN_QC_BBOX = (118.0, 21.5, 124.0, 27.0)  # west, south, east, north


def fixed_grid_window(
    bbox: tuple[float, float, float, float],
    *,
    padding_pixels: int = 8,
) -> dict:
    """Convert lon/lat bbox to a conservative Himawari 2 km fixed-grid window."""
    import math

    from pyproj import CRS, Transformer

    west, south, east, north = bbox
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError(f"Invalid bbox: {bbox}")
    if padding_pixels < 0:
        raise ValueError("padding_pixels must be >= 0")

    geos = CRS.from_proj4(
        f"+proj=geos +h={HIMAWARI_HEIGHT_M:g} "
        f"+lon_0={HIMAWARI_SUB_LON_DEG:g} "
        f"+a={HIMAWARI_SEMI_MAJOR_M:g} "
        f"+rf={HIMAWARI_INV_FLATTENING:.12f} "
        "+sweep=y +units=m +no_defs"
    )
    transformer = Transformer.from_crs("EPSG:4326", geos, always_xy=True)

    lons = (west, (west + east) / 2.0, east)
    lats = (south, (south + north) / 2.0, north)
    projected = [transformer.transform(lon, lat) for lon in lons for lat in lats]
    if not all(math.isfinite(x) and math.isfinite(y) for x, y in projected):
        raise ValueError(f"Bbox is outside Himawari fixed-grid visibility: {bbox}")

    min_x, min_y, max_x, max_y = HIMAWARI_AREA_EXTENT_M
    pixel_x = (max_x - min_x) / HIMAWARI_GRID_SIZE
    pixel_y = (max_y - min_y) / HIMAWARI_GRID_SIZE

    cols = [(x - min_x) / pixel_x for x, _ in projected]
    rows = [(max_y - y) / pixel_y for _, y in projected]

    col_start = max(0, math.floor(min(cols)) - padding_pixels)
    col_stop = min(
        HIMAWARI_GRID_SIZE,
        math.ceil(max(cols)) + 1 + padding_pixels,
    )
    row_start = max(0, math.floor(min(rows)) - padding_pixels)
    row_stop = min(
        HIMAWARI_GRID_SIZE,
        math.ceil(max(rows)) + 1 + padding_pixels,
    )
    if row_start >= row_stop or col_start >= col_stop:
        raise ValueError(f"Empty fixed-grid window for bbox: {bbox}")

    return {
        "bbox_lon_lat": [west, south, east, north],
        "row_start": row_start,
        "row_stop": row_stop,
        "col_start": col_start,
        "col_stop": col_stop,
        "rows": row_stop - row_start,
        "cols": col_stop - col_start,
        "padding_pixels": padding_pixels,
        "pixel_size_m": [pixel_x, pixel_y],
        "projection": {
            "proj": "geos",
            "longitude_of_projection_origin": HIMAWARI_SUB_LON_DEG,
            "perspective_point_height_m": HIMAWARI_HEIGHT_M,
            "semi_major_axis_m": HIMAWARI_SEMI_MAJOR_M,
            "inverse_flattening": HIMAWARI_INV_FLATTENING,
            "sweep_angle_axis": "y",
            "area_extent_m": list(HIMAWARI_AREA_EXTENT_M),
            "grid_size": [HIMAWARI_GRID_SIZE, HIMAWARI_GRID_SIZE],
        },
    }


def _numeric_window_stats(values, *, fill_value=None) -> dict:
    import numpy as np

    array = np.asarray(values)
    valid = np.isfinite(array)
    if fill_value is not None:
        fill = np.asarray(fill_value).reshape(-1)
        if fill.size:
            valid &= array != fill[0]

    valid_values = array[valid]
    result = {
        "shape": list(array.shape),
        "total_count": int(array.size),
        "valid_count": int(valid_values.size),
        "fill_or_invalid_count": int(array.size - valid_values.size),
    }
    if valid_values.size:
        result.update(
            {
                "min": _attr_text(valid_values.min()),
                "max": _attr_text(valid_values.max()),
                "mean": float(valid_values.mean()),
            }
        )
        unique = np.unique(valid_values)
        if unique.size <= 16:
            result["value_counts"] = {
                str(_attr_text(value)): int((valid_values == value).sum())
                for value in unique
            }
    return result


def read_fixed_grid_window(
    fs,
    path: str,
    *,
    dataset_name: str,
    window: dict,
    latitude_name: str,
    longitude_name: str,
) -> dict:
    """Range-read only the selected fixed-grid window and its geolocation QC."""
    import h5py
    import numpy as np

    rs, re = window["row_start"], window["row_stop"]
    cs, ce = window["col_start"], window["col_stop"]

    with fs.open(
        path,
        "rb",
        block_size=8 * 1024 * 1024,
        cache_type="readahead",
    ) as fileobj:
        with h5py.File(fileobj, "r") as handle:
            for required in (dataset_name, latitude_name, longitude_name):
                if required not in handle:
                    raise AssertionError(f"{required} missing from {path}")

            dataset = handle[dataset_name]
            if list(dataset.shape) != [HIMAWARI_GRID_SIZE, HIMAWARI_GRID_SIZE]:
                raise AssertionError(
                    f"Unexpected {dataset_name} grid: {dataset.shape}"
                )

            values = dataset[rs:re, cs:ce]
            latitudes = handle[latitude_name][rs:re, cs:ce]
            longitudes = handle[longitude_name][rs:re, cs:ce]

            fill_value = dataset.attrs.get("_FillValue")
            lat_fill = handle[latitude_name].attrs.get("_FillValue")
            lon_fill = handle[longitude_name].attrs.get("_FillValue")

            data_stats = _numeric_window_stats(values, fill_value=fill_value)
            lat_stats = _numeric_window_stats(latitudes, fill_value=lat_fill)
            lon_stats = _numeric_window_stats(longitudes, fill_value=lon_fill)

            if not data_stats["valid_count"]:
                raise AssertionError(f"No valid {dataset_name} pixels in Taiwan window")
            if not lat_stats["valid_count"] or not lon_stats["valid_count"]:
                raise AssertionError("No valid geolocation pixels in Taiwan window")

            west, south, east, north = window["bbox_lon_lat"]
            tolerance_deg = 0.25
            if lat_stats["min"] > south + tolerance_deg or lat_stats["max"] < north - tolerance_deg:
                raise AssertionError(
                    f"Latitude window does not cover bbox: {lat_stats}, bbox={window['bbox_lon_lat']}"
                )
            if lon_stats["min"] > west + tolerance_deg or lon_stats["max"] < east - tolerance_deg:
                raise AssertionError(
                    f"Longitude window does not cover bbox: {lon_stats}, bbox={window['bbox_lon_lat']}"
                )

            return {
                "dataset": dataset_name,
                "dataset_chunks": list(dataset.chunks) if dataset.chunks else None,
                "dataset_compression": dataset.compression,
                "data": data_stats,
                "geolocation": {
                    "latitude_dataset": latitude_name,
                    "longitude_dataset": longitude_name,
                    "latitude": lat_stats,
                    "longitude": lon_stats,
                },
            }


def floor_to_ten_minutes(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.replace(minute=(value.minute // 10) * 10, second=0, microsecond=0)


def slot_prefix(value: datetime) -> str:
    value = value.astimezone(timezone.utc)
    return (
        f"{PRODUCT_ROOT}/{value:%Y/%m/%d}/{value:%H%M}/"
    )


def candidate_slots(now: datetime, lookback_slots: int) -> list[datetime]:
    if lookback_slots < 1:
        raise ValueError("lookback_slots must be >= 1")
    start = floor_to_ten_minutes(now)
    return [start - timedelta(minutes=10 * i) for i in range(lookback_slots)]


def select_product_pair(paths: Iterable[str]) -> dict[str, str] | None:
    mask = None
    height = None
    for path in sorted(paths):
        name = path.rsplit("/", 1)[-1]
        if name.startswith(MASK_PREFIX) and name.endswith(".nc"):
            mask = path
        elif name.startswith(HEIGHT_PREFIX) and name.endswith(".nc"):
            height = path
    if mask and height:
        return {"cloud_mask": mask, "cloud_height": height}
    return None


def build_fs():
    import s3fs

    return s3fs.S3FileSystem(
        anon=True,
        client_kwargs={"region_name": "us-east-1"},
    )


def find_latest_pair(fs, *, now: datetime, lookback_slots: int) -> tuple[datetime, dict[str, str]]:
    for slot in candidate_slots(now, lookback_slots):
        prefix = f"{BUCKET}/{slot_prefix(slot)}"
        try:
            paths = fs.ls(prefix, detail=False)
        except FileNotFoundError:
            continue
        pair = select_product_pair(paths)
        if pair:
            return slot, pair
    raise RuntimeError(
        f"No same-slot CMSK + CHGT pair found in the last {lookback_slots * 10} minutes"
    )


def _attr_text(value) -> str | int | float | bool | list | None:
    try:
        import numpy as np

        if isinstance(value, np.ndarray):
            value = value.tolist()
        elif isinstance(value, np.generic):
            value = value.item()
    except Exception:
        pass
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_attr_text(item) for item in value]
    return str(value)


def _interesting_attrs(obj) -> dict:
    attrs = {}
    for name in (
        "long_name",
        "standard_name",
        "units",
        "grid_mapping",
        "grid_mapping_name",
        "perspective_point_height",
        "semi_major_axis",
        "semi_minor_axis",
        "inverse_flattening",
        "longitude_of_projection_origin",
        "latitude_of_projection_origin",
        "sweep_angle_axis",
        "scale_factor",
        "add_offset",
        "valid_range",
        "_FillValue",
    ):
        if name in obj.attrs:
            attrs[name] = _attr_text(obj.attrs[name])
    return attrs


def _dataset_summary(dataset) -> dict:
    result = {
        "shape": list(dataset.shape),
        "dtype": str(dataset.dtype),
        "chunks": list(dataset.chunks) if dataset.chunks else None,
        "compression": dataset.compression,
        "attrs": _interesting_attrs(dataset),
    }
    if dataset.ndim == 1 and dataset.size:
        result["coordinate_endpoints"] = [
            _attr_text(dataset[0]),
            _attr_text(dataset[-1]),
        ]
    elif dataset.ndim == 0:
        try:
            result["value"] = _attr_text(dataset[()])
        except Exception:
            pass
    return result


def _projection_diagnostics(handle) -> dict:
    """Read only root metadata; avoid walking the remote HDF5 object tree."""
    objects = {}
    root_attrs = {
        name: _attr_text(value)
        for name, value in handle.attrs.items()
        if (
            "projection" in name.lower()
            or "satellite" in name.lower()
            or "longitude" in name.lower()
            or "latitude" in name.lower()
            or "perspective" in name.lower()
        )
    }

    for name, obj in handle.items():
        attrs = _interesting_attrs(obj)
        semantic = name.lower()
        is_scalar = getattr(obj, "ndim", None) == 0
        if (
            name in {"x", "y"}
            or is_scalar
            or "projection" in semantic
            or "geos" in semantic
            or "himawari" in semantic
            or "grid_mapping_name" in attrs
            or "perspective_point_height" in attrs
        ):
            summary = {
                "kind": type(obj).__name__,
                "attrs": attrs,
            }
            if hasattr(obj, "shape"):
                summary["shape"] = list(obj.shape)
                summary["dtype"] = str(obj.dtype)
                if getattr(obj, "ndim", None) == 1 and obj.size:
                    summary["coordinate_endpoints"] = [
                        _attr_text(obj[0]),
                        _attr_text(obj[-1]),
                    ]
                elif is_scalar:
                    try:
                        summary["value"] = _attr_text(obj[()])
                    except Exception:
                        pass
            objects[name] = summary

    return {
        "root_keys": list(handle.keys()),
        "root_projection_attrs": root_attrs,
        "objects": objects,
    }


def projected_xy_to_pixel(x_m: float, y_m: float) -> tuple[float, float]:
    """Convert nominal geostationary projection metres to 0-based row/column."""
    col = (x_m + NOMINAL_HALF_EXTENT_M) / NOMINAL_PIXEL_SIZE_M
    row = (NOMINAL_HALF_EXTENT_M - y_m) / NOMINAL_PIXEL_SIZE_M
    return row, col


def nominal_bbox_window(
    bbox: dict[str, float],
    *,
    pad_pixels: int = 32,
) -> dict[str, int]:
    """Predict a small Full-Disk read window, later validated from lat/lon."""
    from pyproj import CRS, Transformer

    geos = CRS.from_proj4(
        "+proj=geos +h=35785863 +lon_0=140.7 +sweep=y "
        "+a=6378137 +b=6356752.3 +units=m +no_defs"
    )
    transformer = Transformer.from_crs("EPSG:4326", geos, always_xy=True)

    points = []
    for lon in (bbox["leftlon"], bbox["rightlon"]):
        for lat in (bbox["bottomlat"], bbox["toplat"]):
            x_m, y_m = transformer.transform(lon, lat)
            if not (float("-inf") < x_m < float("inf")) or not (
                float("-inf") < y_m < float("inf")
            ):
                raise AssertionError((lon, lat, x_m, y_m))
            points.append(projected_xy_to_pixel(x_m, y_m))

    rows = [point[0] for point in points]
    cols = [point[1] for point in points]

    import math

    row_start = max(0, math.floor(min(rows)) - pad_pixels)
    row_end = min(FULL_DISK_PIXELS, math.ceil(max(rows)) + pad_pixels + 1)
    col_start = max(0, math.floor(min(cols)) - pad_pixels)
    col_end = min(FULL_DISK_PIXELS, math.ceil(max(cols)) + pad_pixels + 1)

    if row_end <= row_start or col_end <= col_start:
        raise AssertionError((row_start, row_end, col_start, col_end))

    return {
        "row_start": row_start,
        "row_end": row_end,
        "col_start": col_start,
        "col_end": col_end,
        "rows": row_end - row_start,
        "cols": col_end - col_start,
    }


def _valid_geo(values):
    import numpy as np

    values = np.asarray(values, dtype="float64")
    return np.where((values > -900.0) & np.isfinite(values), values, np.nan)


def _window_geo_summary(latitudes, longitudes, bbox: dict[str, float]) -> dict:
    import numpy as np

    latitudes = _valid_geo(latitudes)
    longitudes = _valid_geo(longitudes)
    valid = np.isfinite(latitudes) & np.isfinite(longitudes)
    if not np.any(valid):
        raise AssertionError("Taiwan probe window has no valid geolocation pixels")

    target_lat = (bbox["bottomlat"] + bbox["toplat"]) / 2.0
    target_lon = (bbox["leftlon"] + bbox["rightlon"]) / 2.0
    distance2 = np.where(
        valid,
        (latitudes - target_lat) ** 2 + (longitudes - target_lon) ** 2,
        np.inf,
    )
    nearest_flat = int(np.argmin(distance2))
    nearest = np.unravel_index(nearest_flat, distance2.shape)
    nearest_lat = float(latitudes[nearest])
    nearest_lon = float(longitudes[nearest])

    if abs(nearest_lat - target_lat) > 0.15 or abs(nearest_lon - target_lon) > 0.15:
        raise AssertionError(
            ("Nominal Himawari Taiwan window missed target center", nearest_lat, nearest_lon)
        )

    actual = {
        "leftlon": float(np.nanmin(longitudes)),
        "rightlon": float(np.nanmax(longitudes)),
        "bottomlat": float(np.nanmin(latitudes)),
        "toplat": float(np.nanmax(latitudes)),
    }
    if not (
        actual["leftlon"] <= bbox["leftlon"]
        and actual["rightlon"] >= bbox["rightlon"]
        and actual["bottomlat"] <= bbox["bottomlat"]
        and actual["toplat"] >= bbox["toplat"]
    ):
        raise AssertionError(("Taiwan probe window does not cover requested bbox", actual, bbox))

    inside = (
        valid
        & (longitudes >= bbox["leftlon"])
        & (longitudes <= bbox["rightlon"])
        & (latitudes >= bbox["bottomlat"])
        & (latitudes <= bbox["toplat"])
    )
    return {
        "actual_bbox": actual,
        "valid_pixels": int(np.count_nonzero(valid)),
        "pixels_inside_requested_bbox": int(np.count_nonzero(inside)),
        "nearest_target_center": {
            "row_offset": int(nearest[0]),
            "col_offset": int(nearest[1]),
            "lat": nearest_lat,
            "lon": nearest_lon,
        },
    }


def read_taiwan_crop(fs, path: str, *, kind: str, window: dict[str, int]) -> dict:
    import h5py
    import numpy as np

    rows = slice(window["row_start"], window["row_end"])
    cols = slice(window["col_start"], window["col_end"])

    with fs.open(
        path,
        "rb",
        block_size=8 * 1024 * 1024,
        cache_type="readahead",
    ) as fileobj:
        with h5py.File(fileobj, "r") as handle:
            lat = handle["Latitude"][rows, cols]
            lon = handle["Longitude"][rows, cols]
            geo = _window_geo_summary(lat, lon, TAIWAN_BBOX)

            if kind == "cloud_mask":
                values = np.asarray(handle["CloudMaskBinary"][rows, cols])
                valid = values >= 0
                if not np.any(valid):
                    raise AssertionError("Taiwan CloudMaskBinary crop has no valid pixels")
                unique, counts = np.unique(values[valid], return_counts=True)
                field = {
                    "dataset": "CloudMaskBinary",
                    "valid_pixels": int(np.count_nonzero(valid)),
                    "value_counts": {
                        str(int(value)): int(count)
                        for value, count in zip(unique, counts)
                    },
                }
            elif kind == "cloud_height":
                values = np.asarray(handle["CldTopHght"][rows, cols], dtype="float64")
                valid = (values > -900.0) & np.isfinite(values)
                if not np.any(valid):
                    raise AssertionError("Taiwan CldTopHght crop has no valid pixels")
                good = values[valid]
                field = {
                    "dataset": "CldTopHght",
                    "unit": "Meter",
                    "valid_pixels": int(good.size),
                    "min": float(np.min(good)),
                    "p50": float(np.percentile(good, 50)),
                    "p90": float(np.percentile(good, 90)),
                    "max": float(np.max(good)),
                }
                if "Latitude_Pc" in handle and "Longitude_Pc" in handle:
                    pc_lat = handle["Latitude_Pc"][rows, cols]
                    pc_lon = handle["Longitude_Pc"][rows, cols]
                    field["parallax_corrected_geo"] = _window_geo_summary(
                        pc_lat, pc_lon, TAIWAN_BBOX
                    )
            else:
                raise ValueError(kind)

    return {
        "window": window,
        "geolocation": geo,
        "field": field,
    }


def inspect_remote_product(fs, path: str, *, kind: str) -> dict:
    import h5py

    with fs.open(
        path,
        "rb",
        block_size=8 * 1024 * 1024,
        cache_type="readahead",
    ) as fileobj:
        with h5py.File(fileobj, "r") as handle:
            datasets = {
                name: obj
                for name, obj in handle.items()
                if isinstance(obj, h5py.Dataset)
            }

            relevant = {}
            for name, dataset in datasets.items():
                long_name = _attr_text(dataset.attrs.get("long_name", ""))
                semantic = f"{name} {long_name}".lower()
                if (
                    name in {
                        "Latitude",
                        "Longitude",
                        "Latitude_Pc",
                        "Longitude_Pc",
                        "x",
                        "y",
                        "himawari_imager_projection",
                    }
                    or "cloud mask" in semantic
                    or "cloud top height" in semantic
                    or name in {"CldTopHght", "CldTopHghtAWIPS"}
                ):
                    relevant[name] = _dataset_summary(dataset)

            if kind == "cloud_mask":
                candidates = [
                    name
                    for name, dataset in datasets.items()
                    if "cloud mask"
                    in f"{name} {_attr_text(dataset.attrs.get('long_name', ''))}".lower()
                    or (
                        "cloud" in name.lower()
                        and "mask" in name.lower()
                    )
                ]
                if not candidates:
                    raise AssertionError(
                        f"No cloud-mask dataset found in {path}; sample variables={list(datasets)[:40]}"
                    )
            elif kind == "cloud_height":
                candidates = [
                    name
                    for name, dataset in datasets.items()
                    if name in {"CldTopHght", "CldTopHghtAWIPS"}
                    or "cloud top height"
                    in f"{name} {_attr_text(dataset.attrs.get('long_name', ''))}".lower()
                ]
                if not candidates:
                    raise AssertionError(
                        f"No cloud-top-height dataset found in {path}; sample variables={list(datasets)[:40]}"
                    )
            else:
                raise ValueError(kind)

            shapes = [list(datasets[name].shape) for name in candidates]
            if not any(len(shape) >= 2 and min(shape[-2:]) > 1000 for shape in shapes):
                raise AssertionError(f"Unexpected {kind} grid shapes: {shapes}")

            globals_of_interest = {}
            for name in (
                "title",
                "satellite_name",
                "instrument_name",
                "processing_level",
                "resolution",
                "time_coverage_start",
                "time_coverage_end",
                "date_created",
                "summary",
                "cdm_data_type",
                "geospatial_bounds",
            ):
                if name in handle.attrs:
                    globals_of_interest[name] = _attr_text(handle.attrs[name])

            return {
                "path": path,
                "size_bytes": int(fs.info(path).get("Size", fs.info(path).get("size", 0))),
                "global_attrs": globals_of_interest,
                "candidate_datasets": candidates,
                "candidate_shapes": shapes,
                "relevant_datasets": relevant,
                "projection_diagnostics": _projection_diagnostics(handle),
            }


def run_probe(*, lookback_slots: int, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    fs = build_fs()
    slot, pair = find_latest_pair(fs, now=now, lookback_slots=lookback_slots)

    mask = inspect_remote_product(fs, pair["cloud_mask"], kind="cloud_mask")
    height = inspect_remote_product(fs, pair["cloud_height"], kind="cloud_height")

    taiwan_window = fixed_grid_window(TAIWAN_QC_BBOX)
    mask_window = read_fixed_grid_window(
        fs,
        pair["cloud_mask"],
        dataset_name="CloudMaskBinaryAWIPS",
        window=taiwan_window,
        latitude_name="Latitude",
        longitude_name="Longitude",
    )
    height_window = read_fixed_grid_window(
        fs,
        pair["cloud_height"],
        dataset_name="CldTopHghtAWIPS",
        window=taiwan_window,
        latitude_name="Latitude_Pc",
        longitude_name="Longitude_Pc",
    )

    result = {
        "schema_version": 1,
        "source_kind": "observation",
        "forecast": False,
        "platform": "JMA Himawari-9",
        "instrument": "AHI",
        "distribution": "NOAA NODD / AWS Open Data",
        "bucket": f"s3://{BUCKET}",
        "product_root": PRODUCT_ROOT,
        "anonymous_access": True,
        "api_key_required": False,
        "nominal_cadence_minutes": 10,
        "nominal_resolution": "2 km at nadir",
        "slot_utc": slot.isoformat().replace("+00:00", "Z"),
        "products": {
            "cloud_mask": mask,
            "cloud_height": height,
        },
        "taiwan_range_read": {
            "window": taiwan_window,
            "cloud_mask": mask_window,
            "cloud_height": height_window,
            "full_disk_pixels": HIMAWARI_GRID_SIZE * HIMAWARI_GRID_SIZE,
            "window_pixels": taiwan_window["rows"] * taiwan_window["cols"],
            "window_fraction_of_full_disk": (
                taiwan_window["rows"]
                * taiwan_window["cols"]
                / (HIMAWARI_GRID_SIZE * HIMAWARI_GRID_SIZE)
            ),
        },
        "semantic_guardrail": (
            "Observed cloud-top height is not forecast low/mid/high cloud-cover diagnostics."
        ),
    }

    for product in result["products"].values():
        attrs = product["global_attrs"]
        satellite = str(attrs.get("satellite_name", "")).lower()
        if satellite and "himawari-9" not in satellite:
            raise AssertionError(f"Unexpected satellite_name: {attrs.get('satellite_name')}")
        resolution = str(attrs.get("resolution", "")).lower()
        if resolution and "2km" not in resolution.replace(" ", ""):
            raise AssertionError(f"Unexpected nominal resolution: {attrs.get('resolution')}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lookback-slots", type=int, default=36)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_probe(lookback_slots=args.lookback_slots)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
