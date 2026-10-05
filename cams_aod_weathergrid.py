"""Build compact CAMS Global AOD 550 nm and PM2.5 WeatherGrid bundles via Open-Meteo."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Iterable

import requests


API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
FIELD_API = "aerosol_optical_depth"
FIELD_GRID = "aerosol_optical_depth_550nm"
PM25_FIELD_API = "pm2_5"
PM25_FIELD_GRID = "pm2_5_ug_m3"
PM25_ENCODING_SCALE = 0.1
TAIWAN_BBOX = {
    "leftlon": 117.6,
    "rightlon": 123.6,
    "bottomlat": 20.4,
    "toplat": 26.8,
}
REQUEST_STEP_DEG = 0.4
ENCODING_SCALE = 0.001
NATIVE_RESOLUTION_KM = 45.0
NATIVE_TIME_INTERVAL_HOURS = 3
UPDATE_INTERVAL_HOURS = 12


def axis_values(start: float, stop: float, step: float) -> list[float]:
    count = int(round((stop - start) / step))
    values = [round(start + i * step, 6) for i in range(count + 1)]
    if not math.isclose(values[-1], stop, abs_tol=1e-6):
        raise ValueError((start, stop, step, values[-1]))
    return values


def request_grid() -> tuple[list[float], list[float], list[tuple[float, float]]]:
    lats = axis_values(
        TAIWAN_BBOX["bottomlat"], TAIWAN_BBOX["toplat"], REQUEST_STEP_DEG
    )
    lons = axis_values(
        TAIWAN_BBOX["leftlon"], TAIWAN_BBOX["rightlon"], REQUEST_STEP_DEG
    )
    points = [(lat, lon) for lat in lats for lon in lons]
    return lats, lons, points


def _chunks(items: list[tuple[float, float]], size: int) -> Iterable[list[tuple[float, float]]]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


def _as_utc_iso(value: str) -> str:
    value = str(value)
    if value.endswith("Z"):
        return value
    if len(value) == 16:
        return value + ":00Z"
    if len(value) == 19:
        return value + "Z"
    return value


def _three_hour_indices(times: list[str]) -> list[int]:
    selected = []
    for index, stamp in enumerate(times):
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if dt.hour % NATIVE_TIME_INTERVAL_HOURS == 0:
            selected.append(index)
    return selected


def fetch_responses(
    points: list[tuple[float, float]],
    *,
    forecast_hours: int = 120,
    batch_size: int = 60,
    session=requests,
) -> list[dict]:
    responses: list[dict] = []
    for batch in _chunks(points, batch_size):
        params = {
            "latitude": ",".join(f"{lat:.4f}" for lat, _ in batch),
            "longitude": ",".join(f"{lon:.4f}" for _, lon in batch),
            "hourly": f"{FIELD_API},{PM25_FIELD_API}",
            "domains": "cams_global",
            "forecast_hours": int(forecast_hours),
            "timezone": "GMT",
            "cell_selection": "nearest",
        }
        response = session.get(API_URL, params=params, timeout=60)
        response.raise_for_status()
        payload = response.json()
        items = payload if isinstance(payload, list) else [payload]
        if len(items) != len(batch):
            raise ValueError(
                f"Open-Meteo returned {len(items)} locations for {len(batch)} requests"
            )
        responses.extend(items)
    return responses


def build_bundle(
    responses: list[dict],
    *,
    retrieved_at: datetime | None = None,
) -> tuple[dict, dict]:
    lats, lons, points = request_grid()
    if len(responses) != len(points):
        raise ValueError(f"Expected {len(points)} location responses, got {len(responses)}")

    first_hourly = responses[0].get("hourly") or {}
    times = [_as_utc_iso(x) for x in first_hourly.get("time", [])]
    if not times:
        raise ValueError("CAMS/Open-Meteo response has no hourly times")
    indices = _three_hour_indices(times)
    if not indices:
        raise ValueError("No 3-hour CAMS-aligned frames found")

    for item in responses:
        hourly = item.get("hourly") or {}
        item_times = [_as_utc_iso(x) for x in hourly.get("time", [])]
        if item_times != times:
            raise ValueError("CAMS/Open-Meteo time axis changed across request grid")
        values = hourly.get(FIELD_API)
        pm25_values = hourly.get(PM25_FIELD_API)
        if values is None or len(values) != len(times):
            raise ValueError("AOD array missing or length mismatch")
        if pm25_values is None or len(pm25_values) != len(times):
            raise ValueError("PM2.5 array missing or length mismatch")

    frames = []
    qc_frames = []
    first_dt = datetime.fromisoformat(times[indices[0]].replace("Z", "+00:00"))
    for time_index in indices:
        values = []
        pm25_values = []
        missing = 0
        pm25_missing = 0
        raw_finite = []
        pm25_raw_finite = []
        for item in responses:
            value = item["hourly"][FIELD_API][time_index]
            if value is None or not math.isfinite(float(value)):
                values.append(None)
                missing += 1
            else:
                number = float(value)
                raw_finite.append(number)
                values.append(int(round(number / ENCODING_SCALE)))

            pm25_value = item["hourly"][PM25_FIELD_API][time_index]
            if pm25_value is None or not math.isfinite(float(pm25_value)):
                pm25_values.append(None)
                pm25_missing += 1
            else:
                pm25_number = float(pm25_value)
                pm25_raw_finite.append(pm25_number)
                pm25_values.append(int(round(pm25_number / PM25_ENCODING_SCALE)))

        valid = times[time_index]
        valid_dt = datetime.fromisoformat(valid.replace("Z", "+00:00"))
        lead = int(round((valid_dt - first_dt).total_seconds() / 3600))
        frames.append(
            {
                "forecast_hour": lead,
                "valid_time_utc": valid,
                "values": {FIELD_GRID: values, PM25_FIELD_GRID: pm25_values},
            }
        )
        qc_frames.append(
            {
                "forecast_hour": lead,
                "valid_time_utc": valid,
                "fields": {
                    FIELD_GRID: {
                        "count": len(values),
                        "missing": missing,
                        "min": min(raw_finite) if raw_finite else None,
                        "max": max(raw_finite) if raw_finite else None,
                        "mean": (
                            sum(raw_finite) / len(raw_finite)
                            if raw_finite
                            else None
                        ),
                        "flags": (
                            ["all_missing"]
                            if not raw_finite
                            else (["partial_missing"] if missing else [])
                        ),
                    },
                    PM25_FIELD_GRID: {
                        "count": len(pm25_values),
                        "missing": pm25_missing,
                        "min": min(pm25_raw_finite) if pm25_raw_finite else None,
                        "max": max(pm25_raw_finite) if pm25_raw_finite else None,
                        "mean": (
                            sum(pm25_raw_finite) / len(pm25_raw_finite)
                            if pm25_raw_finite
                            else None
                        ),
                        "flags": (
                            ["all_missing"]
                            if not pm25_raw_finite
                            else (["partial_missing"] if pm25_missing else [])
                        ),
                    },
                },
            }
        )

    # Open-Meteo may expose the requested time axis before the newest CAMS
    # cycle has populated its far forecast tail. Do not publish frames where
    # every requested production field is missing across the whole grid.
    # Only trim the trailing unavailable horizon: interior gaps remain visible
    # to QC instead of being silently hidden.
    trimmed_trailing_frames = 0
    while qc_frames:
        tail_fields = qc_frames[-1]["fields"].values()
        if not all(details["missing"] == details["count"] for details in tail_fields):
            break
        frames.pop()
        qc_frames.pop()
        trimmed_trailing_frames += 1

    if not frames:
        raise ValueError("CAMS/Open-Meteo returned no publishable frames")

    now = retrieved_at or datetime.now(timezone.utc)
    retrieved_iso = now.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    returned_cells = {
        (
            round(float(item.get("latitude")), 4),
            round(float(item.get("longitude")), 4),
        )
        for item in responses
        if item.get("latitude") is not None and item.get("longitude") is not None
    }

    bundle = {
        "schema_version": 2,
        "provider": "Copernicus CAMS via Open-Meteo",
        "model": "CAMS_GLOBAL",
        "cycle": {
            "label": "CAMS Global latest via Open-Meteo",
            "retrieved_at_utc": retrieved_iso,
        },
        "bbox": dict(TAIWAN_BBOX),
        "provenance": {
            "upstream_model": "CAMS Global Atmospheric Composition Forecast",
            "api": "Open-Meteo Air Quality API",
            "api_domain": "cams_global",
            "native_resolution_km": NATIVE_RESOLUTION_KM,
            "native_grid_degrees": 0.4,
            "native_time_interval_hours": NATIVE_TIME_INTERVAL_HOURS,
            "update_interval_hours": UPDATE_INTERVAL_HOURS,
            "api_output_interval_hours": 1,
            "published_interval_hours": NATIVE_TIME_INTERVAL_HOURS,
            "request_grid_spacing_degrees": REQUEST_STEP_DEG,
            "browser_grid_semantics": "request_presentation_lattice",
            "provider_cell_selection": "nearest",
            "returned_provider_cell_count": len(returned_cells),
            "field_semantics": "AOD 550 nm is column aerosol loading; PM2.5 is near-surface particulate mass concentration",
            "licence": "CC BY 4.0 data; Open-Meteo free endpoint non-commercial use",
            "attribution": "Copernicus Atmosphere Monitoring Service (CAMS) + Open-Meteo",
        },
        "grid": {
            "rows": len(lats),
            "cols": len(lons),
            "latitudes": lats,
            "longitudes": lons,
        },
        "fields": {
            FIELD_GRID: {
                "unit": "1",
                "encoding": "integer_scaled",
                "scale": ENCODING_SCALE,
                "decode": f"value * {ENCODING_SCALE}",
                "null": "missing",
                "wavelength_nm": 550,
                "quantity": "aerosol_optical_depth",
            },
            PM25_FIELD_GRID: {
                "unit": "µg/m³",
                "encoding": "integer_scaled",
                "scale": PM25_ENCODING_SCALE,
                "decode": f"value * {PM25_ENCODING_SCALE}",
                "null": "missing",
                "quantity": "particulate_matter_2_5",
                "semantics": "near-surface PM2.5 mass concentration; not column AOD",
            }
        },
        "frames": frames,
    }

    flags = []
    for frame in qc_frames:
        for field_name, details in frame["fields"].items():
            for flag in details["flags"]:
                flags.append(
                    {
                        "forecast_hour": frame["forecast_hour"],
                        "field": field_name,
                        "flag": flag,
                    }
                )
    qc = {
        "schema_version": 1,
        "provider": bundle["provider"],
        "model": bundle["model"],
        "frame_count": len(frames),
        "grid_rows": len(lats),
        "grid_cols": len(lons),
        "request_point_count": len(points),
        "returned_provider_cell_count": len(returned_cells),
        "frames": qc_frames,
        "flags": flags,
        "trimmed_trailing_all_missing_frames": trimmed_trailing_frames,
        "notes": [
            "Browser coordinates are a 0.4 degree request/presentation lattice.",
            "PM2.5 and AOD share the same CAMS request/time lattice but retain distinct physical meanings.",
            "Open-Meteo selects nearest CAMS Global cells; this does not increase native resolution.",
            "Only 3-hourly frames are published even though the API exposes hourly output.",
        ],
    }
    return bundle, qc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="cams_aod_output")
    parser.add_argument("--forecast-hours", type=int, default=120)
    parser.add_argument("--batch-size", type=int, default=60)
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    _, _, points = request_grid()
    responses = fetch_responses(
        points,
        forecast_hours=args.forecast_hours,
        batch_size=args.batch_size,
    )
    bundle, qc = build_bundle(responses)
    bundle_path = out / "cams_global_tw_aod_browser.json"
    qc_path = out / "cams_global_tw_aod_qc.json"
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
                "frames": len(bundle["frames"]),
                "fields": list(bundle["fields"]),
                "grid": [bundle["grid"]["rows"], bundle["grid"]["cols"]],
                "provider_cells": qc["returned_provider_cell_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
