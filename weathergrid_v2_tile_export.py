"""Export native WeatherGrid snapshots into browser valid-time tiles."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BROWSER_FIELD_MAP = {
    "total_cloud_percent": "cloud_cover",
    "low_cloud_percent": "cloud_cover_low",
    "mid_cloud_percent": "cloud_cover_mid",
    "high_cloud_percent": "cloud_cover_high",
    # Already-browser-normalized names are accepted for tests/other adapters.
    "cloud_cover": "cloud_cover",
    "cloud_cover_low": "cloud_cover_low",
    "cloud_cover_mid": "cloud_cover_mid",
    "cloud_cover_high": "cloud_cover_high",
}
NATIVE_BROWSER_FIELDS = tuple(sorted(set(BROWSER_FIELD_MAP.values())))


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def valid_time_token(value: str) -> str:
    """Return one canonical URL-safe UTC valid-time token."""
    return _parse_utc(value).strftime("%Y%m%dT%H%MZ")


def _browser_values(raw_values: dict, expected: int) -> dict:
    values = {}
    for source, data in raw_values.items():
        target = BROWSER_FIELD_MAP.get(source)
        if target is None:
            continue
        if len(data) != expected:
            raise ValueError(f"{source} has {len(data)} values; expected {expected}")
        if target in values:
            raise ValueError(f"duplicate browser field {target}")
        values[target] = data
    if not values:
        raise ValueError("frame has no browser-supported native fields")
    return values


def frame_to_tile(snapshot: dict, frame_index: int = 0) -> dict:
    frames = snapshot.get("frames") or []
    if not frames:
        raise ValueError("snapshot has no frames")
    frame = frames[frame_index]
    grid = snapshot["grid"]
    rows = int(grid["rows"])
    cols = int(grid["cols"])
    expected = rows * cols
    values = _browser_values(frame["values"], expected)
    return {
        "schema_version": 1,
        "provider": "jma",
        "model": "JMA_MSM",
        "native_grid": True,
        "reference_time_utc": snapshot["reference_time_utc"],
        "valid_time_utc": frame["valid_time_utc"],
        "valid_time_token": valid_time_token(frame["valid_time_utc"]),
        "forecast_hour": frame["forecast_hour"],
        "supported_fields": sorted(values),
        "grid": {
            "rows": rows,
            "cols": cols,
            "latitudes": grid["latitudes"],
            "longitudes": grid["longitudes"],
        },
        "values": values,
        "transport": snapshot.get("transport", {}),
    }


def run_manifest(
    snapshot: dict,
    *,
    target_time_utc: str | datetime | None = None,
) -> dict:
    """Describe one native run and the valid time nearest publication time."""
    frames = snapshot.get("frames") or []
    if not frames:
        raise ValueError("snapshot has no frames")
    entries = [
        {
            "valid_time_utc": frame["valid_time_utc"],
            "token": valid_time_token(frame["valid_time_utc"]),
            "forecast_hour": frame["forecast_hour"],
        }
        for frame in frames
    ]
    fields = sorted(
        {
            BROWSER_FIELD_MAP[source]
            for frame in frames
            for source in frame.get("values", {})
            if source in BROWSER_FIELD_MAP
        }
    )
    if target_time_utc is None:
        target = datetime.now(timezone.utc)
    elif isinstance(target_time_utc, datetime):
        if target_time_utc.tzinfo is None:
            raise ValueError("target_time_utc datetime must be timezone-aware")
        target = target_time_utc.astimezone(timezone.utc)
    else:
        target = _parse_utc(target_time_utc)
    nearest = min(
        entries,
        key=lambda entry: abs(
            (_parse_utc(entry["valid_time_utc"]) - target).total_seconds()
        ),
    )
    return {
        "schema_version": 1,
        "provider": "jma",
        "model": "JMA_MSM",
        "reference_time_utc": snapshot["reference_time_utc"],
        "default_valid_time_utc": nearest["valid_time_utc"],
        "nearest_valid_time_utc": nearest["valid_time_utc"],
        "nearest_valid_time_token": nearest["token"],
        "valid_times": entries,
        "supported_fields": fields,
    }


def write_frame_tile(snapshot: dict, output: str | Path, frame_index: int = 0) -> dict:
    tile = frame_to_tile(snapshot, frame_index)
    p = Path(output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(tile, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return tile


def write_run_manifest(
    snapshot: dict,
    output: str | Path,
    *,
    target_time_utc: str | datetime | None = None,
) -> dict:
    manifest = run_manifest(snapshot, target_time_utc=target_time_utc)
    p = Path(output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return manifest
