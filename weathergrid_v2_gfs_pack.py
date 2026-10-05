"""Pack decoded global GFS cloud grids into compact WeatherGrid V2 binary tiles.

Format v1 is deliberately storage-neutral. A tile is raw row-major uint8 with
four interleaved channels per grid point in GFS_CLOUD_FIELDS order. Cloud cover
0..100 is stored losslessly at integer precision; 255 is reserved for missing.

The packer does not commit data to Git. A separate publisher decides where the
current-run artifacts live.
"""
from __future__ import annotations

import json
from pathlib import Path

from weathergrid_v2_gfs_global import GFS_CLOUD_FIELDS, cells_for_viewport

GFS_BINARY_TILE_DEG = 30.0
GFS_GRID_STEP_DEG = 0.25
MISSING_UINT8 = 255
BINARY_SCHEMA_VERSION = 1


def _normalize_lon_array(values):
    import numpy as np

    lon = np.asarray(values, dtype=float)
    normalized = ((lon + 180.0) % 360.0) - 180.0
    normalized[np.isclose(normalized, -0.0)] = 0.0
    order = np.argsort(normalized)
    return normalized[order], order


def _prepare_field(field: dict):
    import numpy as np

    lat = np.asarray(field["latitudes"], dtype=float)
    lon = np.asarray(field["longitudes"], dtype=float)
    values = np.asarray(field["values"], dtype=float)
    if lat.ndim != 1 or lon.ndim != 1:
        raise ValueError("GFS binary packer requires 1-D latitude/longitude axes")
    if values.shape != (len(lat), len(lon)):
        raise ValueError(
            f"GFS field shape {values.shape} != axes {(len(lat), len(lon))}"
        )

    lon, lon_order = _normalize_lon_array(lon)
    values = values[:, lon_order]
    lat_order = np.argsort(lat)
    lat = lat[lat_order]
    values = values[lat_order, :]
    return lat, lon, values


def _prepared_cloud_fields(decoded: dict):
    import numpy as np

    missing = [field for field in GFS_CLOUD_FIELDS if field not in decoded]
    if missing:
        raise ValueError(f"decoded GFS cloud fields missing: {missing}")

    prepared = {}
    reference_lat = None
    reference_lon = None
    for field in GFS_CLOUD_FIELDS:
        lat, lon, values = _prepare_field(decoded[field])
        if reference_lat is None:
            reference_lat, reference_lon = lat, lon
        else:
            if not np.array_equal(lat, reference_lat):
                raise ValueError(f"{field} latitude axis differs from cloud_cover")
            if not np.array_equal(lon, reference_lon):
                raise ValueError(f"{field} longitude axis differs from cloud_cover")
        prepared[field] = values
    return reference_lat, reference_lon, prepared


def _axis_mask(axis, low: float, high: float, *, include_high: bool):
    import numpy as np

    if include_high:
        return (axis >= low - 1e-9) & (axis <= high + 1e-9)
    return (axis >= low - 1e-9) & (axis < high - 1e-9)


def encode_cloud_tile(decoded: dict, cell: dict) -> tuple[bytes, dict]:
    """Encode one non-wrapping global cell from a decoded GFS frame."""
    import numpy as np

    b = cell["bbox"]
    if not (-180.0 <= b["west"] < b["east"] <= 180.0):
        raise ValueError("binary GFS cell must be non-wrapping")
    if not (-90.0 <= b["south"] < b["north"] <= 90.0):
        raise ValueError("invalid GFS cell latitude bounds")

    lat, lon, fields = _prepared_cloud_fields(decoded)
    lat_mask = _axis_mask(
        lat, b["south"], b["north"], include_high=b["north"] >= 90.0
    )
    lon_mask = _axis_mask(
        lon, b["west"], b["east"], include_high=False
    )
    tile_lat = lat[lat_mask]
    tile_lon = lon[lon_mask]
    if tile_lat.size == 0 or tile_lon.size == 0:
        raise ValueError(f"GFS cell {cell['id']} selects no source grid points")

    channels = []
    for field in GFS_CLOUD_FIELDS:
        subset = fields[field][np.ix_(lat_mask, lon_mask)]
        encoded = np.where(
            np.isfinite(subset),
            np.clip(np.rint(subset), 0, 100),
            MISSING_UINT8,
        ).astype(np.uint8)
        channels.append(encoded)
    interleaved = np.stack(channels, axis=-1)
    payload = interleaved.tobytes(order="C")
    rows, cols = interleaved.shape[:2]
    expected = rows * cols * len(GFS_CLOUD_FIELDS)
    if len(payload) != expected:
        raise AssertionError("binary tile byte count mismatch")

    metadata = {
        "schema_version": BINARY_SCHEMA_VERSION,
        "encoding": "uint8_interleaved",
        "missing_value": MISSING_UINT8,
        "channels": list(GFS_CLOUD_FIELDS),
        "rows": int(rows),
        "cols": int(cols),
        "grid_step_degrees": GFS_GRID_STEP_DEG,
        "bbox": dict(b),
        "lat_start": float(tile_lat[0]),
        "lat_end": float(tile_lat[-1]),
        "lon_start": float(tile_lon[0]),
        "lon_end": float(tile_lon[-1]),
        "bytes": len(payload),
    }
    return payload, metadata


def global_binary_cells(*, tile_deg: float = GFS_BINARY_TILE_DEG) -> list[dict]:
    return cells_for_viewport(
        {"west": -180.0, "south": -90.0, "east": 180.0, "north": 90.0},
        cell_deg=tile_deg,
    )


def write_global_frame(
    decoded: dict,
    output_dir: str | Path,
    *,
    reference_time_utc: str,
    valid_time_utc: str,
    forecast_hour: int,
    source: dict | None = None,
    tile_deg: float = GFS_BINARY_TILE_DEG,
) -> dict:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    tiles = []
    failures = []
    for cell in global_binary_cells(tile_deg=tile_deg):
        try:
            payload, meta = encode_cloud_tile(decoded, cell)
            filename = f"{cell['id']}.bin"
            (root / filename).write_bytes(payload)
            tiles.append(
                {
                    "cell_id": cell["id"],
                    "bbox": cell["bbox"],
                    "path": filename,
                    **{k: meta[k] for k in (
                        "rows", "cols", "lat_start", "lat_end",
                        "lon_start", "lon_end", "bytes",
                    )},
                }
            )
        except Exception as exc:
            failures.append({"cell_id": cell["id"], "error": str(exc)})

    required = global_binary_cells(tile_deg=tile_deg)
    manifest = {
        "schema_version": BINARY_SCHEMA_VERSION,
        "provider": "gfs",
        "model": "GFS_GLOBAL_0P25",
        "reference_time_utc": reference_time_utc,
        "valid_time_utc": valid_time_utc,
        "forecast_hour": int(forecast_hour),
        "supported_fields": list(GFS_CLOUD_FIELDS),
        "encoding": {
            "type": "uint8_interleaved",
            "missing_value": MISSING_UINT8,
            "channels": list(GFS_CLOUD_FIELDS),
            "grid_step_degrees": GFS_GRID_STEP_DEG,
            "tile_degrees": float(tile_deg),
        },
        "required_cell_count": len(required),
        "published_cell_ids": [item["cell_id"] for item in tiles],
        "coverage_complete": len(tiles) == len(required) and not failures,
        "tiles": tiles,
        "failed_cells": failures,
        "source": source or {},
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return manifest
