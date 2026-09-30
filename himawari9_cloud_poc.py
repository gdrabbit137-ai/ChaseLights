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
