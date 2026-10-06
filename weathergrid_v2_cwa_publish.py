"""Publish the compact CWA WRF browser bundle as WeatherGrid V2 tiles."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from weathergrid_v2_cache_index import cells_for_region, write_index
from weathergrid_v2_tile_export import valid_time_token

FIELD_MAP = {
    "temperature_2m_c": "cwa_temperature_2m",
    "relative_humidity_2m_percent": "cwa_rh_2m",
    "relative_humidity_925hpa_percent": "cwa_rh_925",
    "relative_humidity_850hpa_percent": "cwa_rh_850",
    "relative_humidity_700hpa_percent": "cwa_rh_700",
    "relative_humidity_500hpa_percent": "cwa_rh_500",
    "relative_humidity_400hpa_percent": "cwa_rh_400",
    "relative_humidity_300hpa_percent": "cwa_rh_300",
    "rh_cloud_potential_low_percent": "cwa_cloud_potential_low",
    "rh_cloud_potential_mid_percent": "cwa_cloud_potential_mid",
    "rh_cloud_potential_high_percent": "cwa_cloud_potential_high",
    "lcl_height_m_agl": "cwa_lcl_height",
    "fog_potential_percent": "cwa_fog_potential",
    "wind_speed_10m_m_s": "cwa_wind_speed_10m",
}
REQUIRED_DERIVED_FIELDS = {
    "cwa_cloud_potential_low",
    "cwa_cloud_potential_mid",
    "cwa_cloud_potential_high",
    "cwa_lcl_height",
    "cwa_fog_potential",
}


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _existing_provider_runs(index_path: Path) -> dict:
    if not index_path.exists():
        return {}
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 2:
        raise RuntimeError("existing V2 index schema_version must be 2")
    runs = payload.get("provider_runs", {})
    if not isinstance(runs, dict):
        raise RuntimeError("existing V2 index provider_runs must be an object")
    return dict(runs)


def _decoded_fields(bundle: dict, frame: dict) -> dict[str, list]:
    out = {}
    fields_meta = bundle.get("fields", {})
    for source, target in FIELD_MAP.items():
        if source not in frame.get("values", {}) or source not in fields_meta:
            continue
        scale = float(fields_meta[source].get("scale", 1.0))
        out[target] = [
            None if value is None else float(value) * scale
            for value in frame["values"][source]
        ]
    missing = REQUIRED_DERIVED_FIELDS - set(out)
    if missing:
        raise RuntimeError(f"CWA compact bundle missing required derived fields: {sorted(missing)}")
    return out


def _indices(values, low: float, high: float) -> list[int]:
    epsilon = 1.0e-8
    return [
        i for i, value in enumerate(values)
        if float(value) >= low - epsilon and float(value) <= high + epsilon
    ]


def _slice_tile(bundle: dict, frame: dict, cell: dict) -> dict | None:
    grid = bundle["grid"]
    lats = [float(x) for x in grid["latitudes"]]
    lons = [float(x) for x in grid["longitudes"]]
    bbox = cell["bbox"]
    lat_idx = _indices(lats, bbox["south"], bbox["north"])
    lon_idx = _indices(lons, bbox["west"], bbox["east"])
    if not lat_idx or not lon_idx:
        return None

    decoded = _decoded_fields(bundle, frame)
    cols = int(grid["cols"])
    values = {}
    for field, source_values in decoded.items():
        subset = []
        for r in lat_idx:
            for c in lon_idx:
                subset.append(source_values[r * cols + c])
        values[field] = subset

    valid = frame["valid_time_utc"]
    cycle = bundle.get("cycle", {})
    reference = cycle.get("cycle_time_utc") or cycle.get("reference_time_utc") or valid
    return {
        "schema_version": 1,
        "provider": "cwa",
        "model": "CWA_WRF_3KM_DERIVED",
        "native_grid": False,
        "regular_grid": True,
        "reference_time_utc": reference,
        "valid_time_utc": valid,
        "valid_time_token": valid_time_token(valid),
        "forecast_hour": frame.get("forecast_hour"),
        "supported_fields": sorted(values),
        "grid": {
            "rows": len(lat_idx),
            "cols": len(lon_idx),
            "latitudes": [lats[i] for i in lat_idx],
            "longitudes": [lons[i] for i in lon_idx],
        },
        "values": values,
        "provenance": {
            **bundle.get("provenance", {}),
            "transport": "published_regular_grid_tiles",
            "derived_model": "B173",
        },
    }


def publish_cwa_bundle(input_path: str | Path, output_root: str | Path) -> dict:
    input_path = Path(input_path)
    root = Path(output_root)
    bundle = json.loads(input_path.read_text(encoding="utf-8"))
    if bundle.get("model") != "CWA_WRF_3KM":
        raise RuntimeError(f"unexpected CWA bundle model: {bundle.get('model')}")
    frames = bundle.get("frames") or []
    if not frames:
        raise RuntimeError("CWA compact bundle has no frames")

    published_cells = []
    tile_count = 0
    for cell in cells_for_region("tw"):
        wrote = False
        for frame in frames:
            tile = _slice_tile(bundle, frame, cell)
            if tile is None:
                continue
            token = tile["valid_time_token"]
            output = root / "cwa" / "current" / token / f"{cell['id']}.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(tile, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            tile_count += 1
            wrote = True
        if wrote:
            published_cells.append(cell["id"])

    if not published_cells:
        raise RuntimeError("CWA bundle did not intersect any WeatherGrid V2 Taiwan cells")

    valid_times = [
        {
            "valid_time_utc": frame["valid_time_utc"],
            "token": valid_time_token(frame["valid_time_utc"]),
            "forecast_hour": frame.get("forecast_hour"),
        }
        for frame in frames
    ]
    now = datetime.now(timezone.utc)
    nearest = min(valid_times, key=lambda item: abs((_parse_time(item["valid_time_utc"]) - now).total_seconds()))
    supported_fields = sorted(_decoded_fields(bundle, frames[0]))
    cycle = bundle.get("cycle", {})
    reference = cycle.get("cycle_time_utc") or cycle.get("reference_time_utc") or frames[0]["valid_time_utc"]
    manifest = {
        "schema_version": 1,
        "provider": "cwa",
        "model": "CWA_WRF_3KM_DERIVED",
        "reference_time_utc": reference,
        "default_valid_time_utc": nearest["valid_time_utc"],
        "nearest_valid_time_utc": nearest["valid_time_utc"],
        "nearest_valid_time_token": nearest["token"],
        "valid_times": valid_times,
        "supported_fields": supported_fields,
        "published_regions": ["tw"],
        "published_cell_ids": published_cells,
        "provenance": {
            **bundle.get("provenance", {}),
            "transport": "published_regular_grid_tiles",
            "derived_model": "B173",
        },
    }
    manifest_path = root / "cwa" / "current" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    provider_runs = _existing_provider_runs(root / "index.json")
    provider_runs["cwa"] = manifest
    write_index(root / "index.json", provider_runs=provider_runs)
    return {
        "provider": "cwa",
        "model": manifest["model"],
        "frames": len(frames),
        "cells": len(published_cells),
        "tiles": tile_count,
        "supported_fields": supported_fields,
        "nearest_valid_time_utc": nearest["valid_time_utc"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="weathergrid/cwa_wrf3_tw_weather_browser.json")
    parser.add_argument("--output-root", default="weathergrid/v2")
    args = parser.parse_args()
    print(json.dumps(publish_cwa_bundle(args.input, args.output_root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
