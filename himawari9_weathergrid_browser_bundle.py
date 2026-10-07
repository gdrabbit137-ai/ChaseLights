#!/usr/bin/env python3
"""Build a compact Taiwan browser bundle from current Himawari-9 cloud observations."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from himawari9_cloud_poc import (
    TAIWAN_QC_BBOX,
    build_fs,
    find_latest_pair,
    find_pair_for_slot,
    fixed_grid_window,
    normalize_slot_utc,
)

OUTPUT_BBOX = {
    "leftlon": 118.0,
    "rightlon": 124.0,
    "bottomlat": 21.5,
    "toplat": 27.0,
}
OUTPUT_STEP_DEG = 0.02
MAX_NEAREST_DISTANCE_M = 5000.0
HEIGHT_SCALE_M = 100.0


def regular_axis(start: float, stop: float, step: float) -> list[float]:
    if step <= 0 or stop < start:
        raise ValueError((start, stop, step))
    count = int(round((stop - start) / step))
    values = [round(start + index * step, 6) for index in range(count + 1)]
    if abs(values[-1] - stop) > 1e-6:
        raise AssertionError((values[-1], stop))
    return values


def _attr_text(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    try:
        if hasattr(value, "item"):
            value = value.item()
            if isinstance(value, bytes):
                return value.decode("utf-8", errors="replace")
    except Exception:
        pass
    return str(value)


def _fill_value(dataset):
    value = dataset.attrs.get("_FillValue")
    if value is None:
        return None
    try:
        return value.reshape(-1)[0].item()
    except Exception:
        try:
            return value.item()
        except Exception:
            return value


def _valid_geo(latitudes, longitudes):
    import numpy as np

    latitudes = np.asarray(latitudes, dtype="float64")
    longitudes = np.asarray(longitudes, dtype="float64")
    return (
        np.isfinite(latitudes)
        & np.isfinite(longitudes)
        & (latitudes > -90.0)
        & (latitudes < 90.0)
        & (longitudes > -180.0)
        & (longitudes < 180.0)
    )


def nearest_regular_grid(
    source_lat,
    source_lon,
    source_values,
    *,
    target_latitudes: list[float],
    target_longitudes: list[float],
    fill_value=None,
    max_distance_m: float = MAX_NEAREST_DISTANCE_M,
) -> tuple[list, dict]:
    """Nearest-neighbour resample using Taiwan TWD97 metres for distance QC."""
    import numpy as np
    from pyproj import Transformer
    from scipy.spatial import cKDTree

    source_lat = np.asarray(source_lat, dtype="float64")
    source_lon = np.asarray(source_lon, dtype="float64")
    source_values = np.asarray(source_values)
    if source_lat.shape != source_lon.shape or source_lat.shape != source_values.shape:
        raise ValueError(
            (source_lat.shape, source_lon.shape, source_values.shape)
        )

    valid_geo = _valid_geo(source_lat, source_lon)
    source_flat_indices = np.flatnonzero(valid_geo)
    if source_flat_indices.size == 0:
        raise AssertionError("No valid source geolocation points")

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3826", always_xy=True)
    src_lon = source_lon.reshape(-1)[source_flat_indices]
    src_lat = source_lat.reshape(-1)[source_flat_indices]
    src_x, src_y = transformer.transform(src_lon, src_lat)
    tree = cKDTree(np.column_stack([src_x, src_y]))

    target_lon_grid, target_lat_grid = np.meshgrid(
        np.asarray(target_longitudes, dtype="float64"),
        np.asarray(target_latitudes, dtype="float64"),
    )
    target_x, target_y = transformer.transform(
        target_lon_grid.reshape(-1),
        target_lat_grid.reshape(-1),
    )
    distances, nearest = tree.query(
        np.column_stack([target_x, target_y]),
        k=1,
        workers=-1,
    )

    source_values_flat = source_values.reshape(-1)
    sampled = source_values_flat[source_flat_indices[nearest]]

    valid_distance = np.isfinite(distances) & (distances <= max_distance_m)
    valid_value = np.ones(sampled.shape, dtype=bool)
    if fill_value is not None:
        valid_value &= sampled != fill_value
    if np.issubdtype(sampled.dtype, np.floating):
        valid_value &= np.isfinite(sampled)

    valid = valid_distance & valid_value
    encoded = [
        value.item() if ok and hasattr(value, "item") else (value if ok else None)
        for value, ok in zip(sampled, valid)
    ]

    finite_distances = distances[np.isfinite(distances)]
    distance_qc = {
        "max_allowed_m": max_distance_m,
        "p50_m": round(float(np.percentile(finite_distances, 50)), 2),
        "p95_m": round(float(np.percentile(finite_distances, 95)), 2),
        "p99_m": round(float(np.percentile(finite_distances, 99)), 2),
        "max_m": round(float(np.max(finite_distances)), 2),
        "outside_max_distance": int(np.count_nonzero(~valid_distance)),
        "target_count": int(distances.size),
    }
    return encoded, distance_qc


def quantize_height(values: list[float | int | None]) -> list[int | None]:
    result = []
    for value in values:
        if value is None:
            result.append(None)
            continue
        number = float(value)
        if not math.isfinite(number) or number < -300.0 or number > 20000.0:
            result.append(None)
            continue
        result.append(int(round(number / HEIGHT_SCALE_M)))
    return result


def _field_stats(values: list[float | int | None], *, scale: float = 1.0) -> dict:
    finite = [float(value) * scale for value in values if value is not None]
    if not finite:
        return {
            "count": 0,
            "missing": len(values),
            "min": None,
            "max": None,
            "mean": None,
        }
    return {
        "count": len(finite),
        "missing": len(values) - len(finite),
        "min": round(min(finite), 3),
        "max": round(max(finite), 3),
        "mean": round(sum(finite) / len(finite), 3),
    }


def _read_source_arrays(fs, pair: dict[str, str], window: dict) -> dict:
    import h5py

    rs = slice(window["row_start"], window["row_stop"])
    cs = slice(window["col_start"], window["col_stop"])

    with fs.open(
        pair["cloud_mask"],
        "rb",
        block_size=8 * 1024 * 1024,
        cache_type="readahead",
    ) as fileobj:
        with h5py.File(fileobj, "r") as handle:
            mask_ds = handle["CloudMaskBinaryAWIPS"]
            source_mask = {
                "values": mask_ds[rs, cs],
                "lat": handle["Latitude"][rs, cs],
                "lon": handle["Longitude"][rs, cs],
                "fill": _fill_value(mask_ds),
                "chunks": list(mask_ds.chunks or ()),
                "compression": mask_ds.compression,
                "size_bytes": int(
                    fs.info(pair["cloud_mask"]).get(
                        "Size",
                        fs.info(pair["cloud_mask"]).get("size", 0),
                    )
                ),
                "time_coverage_start": _attr_text(handle.attrs.get("time_coverage_start", "")),
                "time_coverage_end": _attr_text(handle.attrs.get("time_coverage_end", "")),
            }

    with fs.open(
        pair["cloud_height"],
        "rb",
        block_size=8 * 1024 * 1024,
        cache_type="readahead",
    ) as fileobj:
        with h5py.File(fileobj, "r") as handle:
            height_ds = handle["CldTopHghtAWIPS"]
            lat_name = "Latitude_Pc" if "Latitude_Pc" in handle else "Latitude"
            lon_name = "Longitude_Pc" if "Longitude_Pc" in handle else "Longitude"
            source_height = {
                "values": height_ds[rs, cs],
                "lat": handle[lat_name][rs, cs],
                "lon": handle[lon_name][rs, cs],
                "fill": _fill_value(height_ds),
                "chunks": list(height_ds.chunks or ()),
                "compression": height_ds.compression,
                "geolocation": {
                    "latitude_dataset": lat_name,
                    "longitude_dataset": lon_name,
                    "parallax_corrected": lat_name.endswith("_Pc"),
                },
                "size_bytes": int(
                    fs.info(pair["cloud_height"]).get(
                        "Size",
                        fs.info(pair["cloud_height"]).get("size", 0),
                    )
                ),
                "time_coverage_start": str(handle.attrs.get("time_coverage_start", "")),
                "time_coverage_end": str(handle.attrs.get("time_coverage_end", "")),
            }

    return {
        "cloud_mask": source_mask,
        "cloud_height": source_height,
    }


def build_live_bundle(
    *,
    lookback_slots: int = 36,
    now: datetime | None = None,
    slot_utc: datetime | None = None,
) -> tuple[dict, dict]:
    now = now or datetime.now(timezone.utc)
    fs = build_fs()
    if slot_utc is None:
        slot, pair = find_latest_pair(fs, now=now, lookback_slots=lookback_slots)
    else:
        slot, pair = find_pair_for_slot(fs, slot=normalize_slot_utc(slot_utc))
    source_window = fixed_grid_window(TAIWAN_QC_BBOX)
    source = _read_source_arrays(fs, pair, source_window)

    latitudes = regular_axis(
        OUTPUT_BBOX["bottomlat"],
        OUTPUT_BBOX["toplat"],
        OUTPUT_STEP_DEG,
    )
    longitudes = regular_axis(
        OUTPUT_BBOX["leftlon"],
        OUTPUT_BBOX["rightlon"],
        OUTPUT_STEP_DEG,
    )

    mask_values, mask_distance = nearest_regular_grid(
        source["cloud_mask"]["lat"],
        source["cloud_mask"]["lon"],
        source["cloud_mask"]["values"],
        target_latitudes=latitudes,
        target_longitudes=longitudes,
        fill_value=source["cloud_mask"]["fill"],
    )
    height_raw, height_distance = nearest_regular_grid(
        source["cloud_height"]["lat"],
        source["cloud_height"]["lon"],
        source["cloud_height"]["values"],
        target_latitudes=latitudes,
        target_longitudes=longitudes,
        fill_value=source["cloud_height"]["fill"],
    )

    mask_encoded = [
        None if value is None else int(value)
        for value in mask_values
    ]
    height_encoded = quantize_height(height_raw)
    expected = len(latitudes) * len(longitudes)
    if len(mask_encoded) != expected or len(height_encoded) != expected:
        raise AssertionError((len(mask_encoded), len(height_encoded), expected))

    mask_stats = _field_stats(mask_encoded)
    height_stats = _field_stats(height_encoded, scale=HEIGHT_SCALE_M)
    if mask_stats["missing"] > expected * 0.01:
        raise AssertionError(f"Too many missing cloud-mask targets: {mask_stats}")
    if mask_distance["p99_m"] > MAX_NEAREST_DISTANCE_M:
        raise AssertionError(mask_distance)
    if height_distance["p99_m"] > MAX_NEAREST_DISTANCE_M:
        raise AssertionError(height_distance)

    time_start = source["cloud_mask"]["time_coverage_start"]
    time_end = source["cloud_mask"]["time_coverage_end"]
    observation = {
        "slot_utc": slot.isoformat().replace("+00:00", "Z"),
        "time_coverage_start": time_start,
        "time_coverage_end": time_end,
    }

    bundle = {
        "schema_version": 1,
        "source_kind": "observation",
        "source_id": "himawari9_ahi",
        "provider": "Japan Meteorological Agency (JMA)",
        "platform": "Himawari-9",
        "instrument": "AHI",
        "distribution": "NOAA NODD / AWS Open Data",
        "attribution": {
            "observation_provider": "Japan Meteorological Agency (JMA)",
            "distribution_provider": "NOAA Open Data Dissemination (NODD)",
        },
        "observation": observation,
        "bbox": OUTPUT_BBOX,
        "grid": {
            "rows": len(latitudes),
            "cols": len(longitudes),
            "latitudes": latitudes,
            "longitudes": longitudes,
            "step_degrees": OUTPUT_STEP_DEG,
        },
        "fields": {
            "observed_cloud_mask": {
                "unit": "1",
                "encoding": "integer_category",
                "categories": {
                    "0": "clear",
                    "1": "cloudy",
                },
                "null": "missing",
                "source_dataset": "CloudMaskBinaryAWIPS",
                "spatial_method": "nearest neighbour from native 2 km Full Disk",
            },
            "cloud_top_height_m": {
                "unit": "m",
                "encoding": "integer_scaled",
                "scale": HEIGHT_SCALE_M,
                "decode": f"value * {HEIGHT_SCALE_M}",
                "null": "missing/no successful cloud-top retrieval",
                "source_dataset": "CldTopHghtAWIPS",
                "spatial_method": (
                    "nearest neighbour using NOAA parallax-corrected geolocation"
                    if source["cloud_height"]["geolocation"]["parallax_corrected"]
                    else "nearest neighbour using source geolocation"
                ),
            },
        },
        "values": {
            "observed_cloud_mask": mask_encoded,
            "cloud_top_height_m": height_encoded,
        },
        "provenance": {
            "anonymous_access": True,
            "api_key_required": False,
            "nominal_native_resolution": "2 km at nadir",
            "nominal_cadence_minutes": 10,
            "source_window": source_window,
            "browser_grid_is_regridded": True,
            "browser_grid_interpolation": "nearest_neighbour",
            "forecast": False,
            "semantic_guardrail": (
                "Observed cloud-top height is not forecast low/mid/high cloud-cover diagnostics."
            ),
        },
    }

    qc = {
        "schema_version": 1,
        "source_id": "himawari9_ahi",
        "observation": observation,
        "target_grid": {
            "rows": len(latitudes),
            "cols": len(longitudes),
            "cells": expected,
            "step_degrees": OUTPUT_STEP_DEG,
        },
        "source_window": source_window,
        "source_products": {
            "cloud_mask": {
                "path": pair["cloud_mask"],
                "size_bytes": source["cloud_mask"]["size_bytes"],
                "chunks": source["cloud_mask"]["chunks"],
                "compression": source["cloud_mask"]["compression"],
            },
            "cloud_height": {
                "path": pair["cloud_height"],
                "size_bytes": source["cloud_height"]["size_bytes"],
                "chunks": source["cloud_height"]["chunks"],
                "compression": source["cloud_height"]["compression"],
                "geolocation": source["cloud_height"]["geolocation"],
            },
        },
        "nearest_distance_m": {
            "observed_cloud_mask": mask_distance,
            "cloud_top_height_m": height_distance,
        },
        "field_stats": {
            "observed_cloud_mask": mask_stats,
            "cloud_top_height_m": height_stats,
        },
        "cloud_fraction": round(
            sum(value == 1 for value in mask_encoded if value is not None)
            / max(1, sum(value is not None for value in mask_encoded)),
            6,
        ),
        "notes": [
            "The browser grid is a compact regular lon/lat presentation grid.",
            "Cloud mask uses source Latitude/Longitude geolocation.",
            (
                "Cloud-top height uses parallax-corrected Latitude_Pc/Longitude_Pc "
                "when present."
            ),
            (
                "Satellite observations are not forecast-model low/mid/high "
                "cloud-cover fields."
            ),
        ],
    }
    return bundle, qc


def parse_slot_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return normalize_slot_utc(parsed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookback-slots", type=int, default=36)
    parser.add_argument(
        "--slot-utc",
        help="Exact 10-minute Himawari UTC slot for replay/calibration.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("himawari9_output"))
    args = parser.parse_args()

    slot = parse_slot_utc(args.slot_utc) if args.slot_utc else None
    bundle, qc = build_live_bundle(
        lookback_slots=args.lookback_slots,
        slot_utc=slot,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = args.output_dir / "himawari9_tw_cloud_browser.json"
    qc_path = args.output_dir / "himawari9_tw_cloud_qc.json"
    bundle_path.write_text(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    qc_path.write_text(
        json.dumps(qc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "browser_bundle": str(bundle_path),
                "qc_report": str(qc_path),
                "observation": bundle["observation"],
                "grid": [bundle["grid"]["rows"], bundle["grid"]["cols"]],
                "fields": list(bundle["fields"]),
                "cloud_fraction": qc["cloud_fraction"],
                "nearest_distance_m": qc["nearest_distance_m"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
