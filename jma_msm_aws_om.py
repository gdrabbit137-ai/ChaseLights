"""Read JMA MSM native cloud fields from Open-Meteo AWS Open Data OM files.

This is a transport adapter only. The meteorological model remains JMA MSM.
It reads the public openmeteo AWS Open Data bucket anonymously and slices
only the ChaseLights Taiwan native-grid window from each spatial OM file.
No Open-Meteo forecast API key is required.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import requests

JMA_MSM_MODEL = "jma_msm"
AWS_BUCKET = "openmeteo"
AWS_REGION = "us-west-2"
AWS_SPATIAL_ROOT = "s3://openmeteo/data_spatial"
AWS_METADATA_ROOT = "https://openmeteo.s3.amazonaws.com/data_spatial"
LATEST_METADATA_URL = f"{AWS_METADATA_ROOT}/{JMA_MSM_MODEL}/latest.json"
IN_PROGRESS_METADATA_URL = (
    f"{AWS_METADATA_ROOT}/{JMA_MSM_MODEL}/in-progress.json"
)

NATIVE_LAT_MIN = 22.4
NATIVE_LON_MIN = 120.0
NATIVE_DY = 0.05
NATIVE_DX = 0.0625
NATIVE_NY = 505
NATIVE_NX = 481

SOURCE_TO_TARGET = {
    "cloud_cover": "total_cloud_percent",
    "cloud_cover_low": "low_cloud_percent",
    "cloud_cover_mid": "mid_cloud_percent",
    "cloud_cover_high": "high_cloud_percent",
}


@dataclass(frozen=True)
class GridSlice:
    y: slice
    x: slice
    latitudes: list[float]
    longitudes: list[float]


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    )


def _utc_iso(value: str) -> str:
    return _parse_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def grid_slice_for_bbox(bbox: dict[str, float]) -> GridSlice:
    """Return exact native-grid indices for an aligned ChaseLights bbox."""

    def index(value: float, origin: float, step: float, axis: str) -> int:
        raw = (float(value) - origin) / step
        rounded = int(round(raw))
        if abs(raw - rounded) > 1e-6:
            raise ValueError(
                f"{axis}={value} is not aligned to JMA MSM native step {step}"
            )
        return rounded

    x0 = index(bbox["leftlon"], NATIVE_LON_MIN, NATIVE_DX, "leftlon")
    x1 = index(bbox["rightlon"], NATIVE_LON_MIN, NATIVE_DX, "rightlon")
    y0 = index(bbox["bottomlat"], NATIVE_LAT_MIN, NATIVE_DY, "bottomlat")
    y1 = index(bbox["toplat"], NATIVE_LAT_MIN, NATIVE_DY, "toplat")

    if not (0 <= x0 <= x1 < NATIVE_NX and 0 <= y0 <= y1 < NATIVE_NY):
        raise ValueError(f"bbox is outside JMA MSM native grid: {bbox}")

    latitudes = [
        round(NATIVE_LAT_MIN + y * NATIVE_DY, 6)
        for y in range(y0, y1 + 1)
    ]
    longitudes = [
        round(NATIVE_LON_MIN + x * NATIVE_DX, 6)
        for x in range(x0, x1 + 1)
    ]
    return GridSlice(
        y=slice(y0, y1 + 1),
        x=slice(x0, x1 + 1),
        latitudes=latitudes,
        longitudes=longitudes,
    )


def _fetch_metadata_url(
    url: str,
    *,
    session: requests.Session | None = None,
    timeout: int = 30,
) -> dict:
    client = session or requests.Session()
    response = client.get(url, timeout=timeout)
    try:
        response.raise_for_status()
    except Exception as exc:
        body = getattr(response, "text", "")
        raise RuntimeError(
            f"JMA MSM AWS metadata request failed: {exc}; response={body[:500]}"
        ) from exc
    metadata = response.json()
    metadata["_metadata_url"] = url
    return metadata


def _metadata_is_usable(metadata: dict, forecast_hours: int) -> bool:
    if not metadata.get("reference_time"):
        return False
    valid_times = list(metadata.get("valid_times") or [])
    if len(valid_times) < forecast_hours:
        return False
    variables = set(metadata.get("variables") or [])
    return set(SOURCE_TO_TARGET).issubset(variables)


def fetch_best_metadata(
    *,
    forecast_hours: int,
    session: requests.Session | None = None,
    timeout: int = 30,
) -> dict:
    """Prefer a fresher partial run once all requested hours are available."""
    candidates = []
    errors = []
    for url in (IN_PROGRESS_METADATA_URL, LATEST_METADATA_URL):
        try:
            metadata = _fetch_metadata_url(
                url, session=session, timeout=timeout
            )
        except Exception as exc:
            errors.append(f"{url}: {exc}")
            continue
        if _metadata_is_usable(metadata, forecast_hours):
            candidates.append(metadata)

    if not candidates:
        raise RuntimeError(
            "No usable JMA MSM AWS metadata for requested window; "
            + "; ".join(errors)
        )

    return max(candidates, key=lambda x: _parse_utc(x["reference_time"]))


def spatial_s3_uri(reference_time: str, valid_time: str) -> str:
    run = _parse_utc(reference_time)
    valid = _parse_utc(valid_time)
    return (
        f"{AWS_SPATIAL_ROOT}/{JMA_MSM_MODEL}/"
        f"{run:%Y/%m/%d/%H%MZ}/{valid:%Y-%m-%dT%H%M}.om"
    )


def _default_reader(uri: str, grid: GridSlice) -> dict[str, np.ndarray]:
    """Read four native cloud arrays using chunked anonymous S3 range access."""
    import fsspec
    from omfiles import OmFileReader

    cache_dir = Path(".cache") / "jma_msm_om"
    cache_dir.mkdir(parents=True, exist_ok=True)
    backend = fsspec.open(
        f"blockcache::{uri}",
        mode="rb",
        s3={"anon": True, "default_block_size": 65536},
        blockcache={"cache_storage": str(cache_dir), "same_names": True},
    )
    out: dict[str, np.ndarray] = {}
    with OmFileReader(backend) as root:
        for source in SOURCE_TO_TARGET:
            child = root.get_child_by_name(source)
            if child is None or not child.is_array:
                raise RuntimeError(f"OM spatial file missing array {source}: {uri}")
            if tuple(child.shape) != (NATIVE_NY, NATIVE_NX):
                raise RuntimeError(
                    f"Unexpected {source} OM shape {tuple(child.shape)}; "
                    f"expected {(NATIVE_NY, NATIVE_NX)}"
                )
            out[source] = np.asarray(
                child.read_array((grid.y, grid.x)), dtype=np.float32
            )
    return out


def fetch_aws_snapshot(
    *,
    bbox: dict[str, float],
    forecast_hours: int,
    metadata: dict | None = None,
    session: requests.Session | None = None,
    reader: Callable[[str, GridSlice], dict[str, np.ndarray]] | None = None,
) -> dict:
    if forecast_hours < 1:
        raise ValueError("forecast_hours must be >= 1")

    metadata = metadata or fetch_best_metadata(
        forecast_hours=forecast_hours,
        session=session,
    )
    grid = grid_slice_for_bbox(bbox)
    reference_time = metadata["reference_time"]
    run = _parse_utc(reference_time)
    valid_times = list(metadata["valid_times"])

    valid_times = [
        value for value in valid_times if _parse_utc(value) >= run
    ][:forecast_hours]
    if len(valid_times) < forecast_hours:
        raise RuntimeError(
            f"JMA MSM AWS run exposes only {len(valid_times)} valid times; "
            f"requested {forecast_hours}"
        )

    read = reader or _default_reader
    frames = []
    for valid_time in valid_times:
        uri = spatial_s3_uri(reference_time, valid_time)
        arrays = read(uri, grid)
        values = {}
        for source, target in SOURCE_TO_TARGET.items():
            array = np.asarray(arrays[source], dtype=np.float32)
            expected_shape = (len(grid.latitudes), len(grid.longitudes))
            if tuple(array.shape) != expected_shape:
                raise RuntimeError(
                    f"{source} subset shape {tuple(array.shape)} != "
                    f"{expected_shape}"
                )
            array = np.clip(array, 0.0, 100.0)
            values[target] = [
                None if np.isnan(x) else float(x)
                for x in array.reshape(-1)
            ]
        lead = int(
            (_parse_utc(valid_time) - run).total_seconds() // 3600
        )
        frames.append(
            {
                "forecast_hour": lead,
                "valid_time_utc": _utc_iso(valid_time),
                "values": values,
            }
        )

    return {
        "reference_time_utc": _utc_iso(reference_time),
        "metadata_completed": bool(metadata.get("completed")),
        "metadata_last_modified_time": metadata.get("last_modified_time"),
        "grid": {
            "rows": len(grid.latitudes),
            "cols": len(grid.longitudes),
            "latitudes": grid.latitudes,
            "longitudes": grid.longitudes,
        },
        "frames": frames,
        "transport": {
            "adapter": "Open-Meteo AWS Open Data OM spatial files",
            "bucket": AWS_BUCKET,
            "region": AWS_REGION,
            "layout": "data_spatial",
            "anonymous": True,
            "api_key_required": False,
            "metadata_url": metadata.get("_metadata_url", LATEST_METADATA_URL),
            "metadata_state": (
                "in_progress"
                if metadata.get("_metadata_url") == IN_PROGRESS_METADATA_URL
                else "latest_completed"
            ),
        },
    }
