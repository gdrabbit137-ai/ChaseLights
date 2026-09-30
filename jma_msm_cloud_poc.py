"""Fetch JMA MSM cloud layers for ChaseLights WeatherGrid.

The Japan Meteorological Agency MSM surface GPV publishes native total / low /
middle / high cloud cover on a 0.05° latitude × 0.0625° longitude regular grid.
Official operational distribution is via JMA/JMBSC GRIB2.  ChaseLights uses
Open-Meteo's JMA endpoint as the initial transport adapter because it exposes
those native JMA MSM cloud fields through a stable HTTP API.

Important:
- The model remains JMA MSM.  Open-Meteo is only the transport/API layer.
- Requests use nearest native grid cell and disable elevation downscaling.
- No cloud layer is derived from pressure-level RH.
- The browser artifact has its own JMA boundary and hourly timeline.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
import requests


JMA_MSM_API_URL = os.environ.get(
    "JMA_MSM_API_URL",
    "https://api.open-meteo.com/v1/jma",
)
JMA_MSM_MODEL = "jma_msm"
JMA_MSM_NATIVE_RESOLUTION_KM = 5.0
JMA_MSM_LAT_STEP_DEG = 0.05
JMA_MSM_LON_STEP_DEG = 0.0625
JMA_MSM_NATIVE_TIME_INTERVAL_HOURS = 1
JMA_MSM_UPDATE_INTERVAL_HOURS = 3
JMA_MSM_STANDARD_HORIZON_HOURS = 39
JMA_MSM_EXTENDED_HORIZON_HOURS = 78
JMA_MSM_EXTENDED_CYCLES_UTC = (0, 12)

JMA_MSM_NATIVE_DOMAIN = {
    "leftlon": 120.0,
    "rightlon": 150.0,
    "bottomlat": 22.4,
    "toplat": 47.6,
}

# Initial Taiwan browser subset.  This deliberately follows the JMA model
# boundary instead of pretending the model covers islands west of 120E or the
# portion of southern Taiwan below 22.4N.
JMA_MSM_TAIWAN_BROWSER_BBOX = {
    # One native grid cell inside the official south/west edge.  The
    # Open-Meteo transport can reject exact edge coordinates even though the
    # official JMA regular-grid product nominally starts at 22.4N / 120E.
    "leftlon": 120.0625,
    "rightlon": 122.5,
    "bottomlat": 22.45,
    "toplat": 25.6,
}

DEFAULT_FORECAST_HOURS = 40
DEFAULT_BATCH_SIZE = 100
DEFAULT_RETRIES = 3

API_VARIABLES = {
    "cloud_cover": "total_cloud_percent",
    "cloud_cover_low": "low_cloud_percent",
    "cloud_cover_mid": "mid_cloud_percent",
    "cloud_cover_high": "high_cloud_percent",
}

# JMA defines cloud-layer boundaries from surface pressure.  At a representative
# 1000 hPa surface pressure, these become ~850 hPa and ~500 hPa.
JMA_MSM_CLOUD_VERTICAL_DEFINITIONS = {
    "low_cloud_percent": {
        "coordinate": "pressure",
        "native_definition": (
            "surface–low/mid boundary; low/mid = Ps×0.85 "
            "(Ps=1000 hPa → ~850 hPa)"
        ),
        "approx_height": "海平面標準大氣約地面～1.5 km",
        "boundary_rule": {
            "low_mid_hpa": "surface_pressure_hpa * 0.85",
        },
        "definition_source": "JMA MSM cloud post-processing",
    },
    "mid_cloud_percent": {
        "coordinate": "pressure",
        "native_definition": (
            "low/mid–mid/high boundary; mid/high = "
            "min(low_mid×0.8, 500 hPa) "
            "(Ps=1000 hPa → ~850–500 hPa)"
        ),
        "approx_height": "海平面標準大氣約1.5～5.6 km",
        "boundary_rule": {
            "low_mid_hpa": "surface_pressure_hpa * 0.85",
            "mid_high_hpa": "min(low_mid_hpa * 0.8, 500)",
        },
        "definition_source": "JMA MSM cloud post-processing",
    },
    "high_cloud_percent": {
        "coordinate": "pressure",
        "native_definition": (
            "above mid/high boundary; mid/high = "
            "min(low_mid×0.8, 500 hPa) "
            "(Ps=1000 hPa → <~500 hPa)"
        ),
        "approx_height": "海平面標準大氣約5.6 km 以上",
        "boundary_rule": {
            "low_mid_hpa": "surface_pressure_hpa * 0.85",
            "mid_high_hpa": "min(low_mid_hpa * 0.8, 500)",
        },
        "definition_source": "JMA MSM cloud post-processing",
    },
    "total_cloud_percent": {
        "coordinate": "full_column",
        "native_definition": "full atmospheric column total cloud cover",
        "approx_height": "全大氣柱",
        "definition_source": "JMA MSM total cloud cover",
    },
}



def _utc_iso(value: str) -> str:
    value = str(value)
    if value.endswith("Z") or value.endswith("+00:00"):
        return value
    if len(value) == 16:
        return value + ":00Z"
    if len(value) == 19:
        return value + "Z"
    return value


def _axis(start: float, stop: float, step: float) -> list[float]:
    count = int(round((stop - start) / step))
    values = [round(start + i * step, 6) for i in range(count + 1)]
    if values[-1] > stop + 1e-6:
        values.pop()
    return values


def build_grid(
    bbox: dict[str, float] | None = None,
) -> tuple[list[float], list[float], list[tuple[float, float]]]:
    bbox = bbox or JMA_MSM_TAIWAN_BROWSER_BBOX
    latitudes = _axis(
        float(bbox["bottomlat"]),
        float(bbox["toplat"]),
        JMA_MSM_LAT_STEP_DEG,
    )
    longitudes = _axis(
        float(bbox["leftlon"]),
        float(bbox["rightlon"]),
        JMA_MSM_LON_STEP_DEG,
    )
    points = [(lat, lon) for lat in latitudes for lon in longitudes]
    return latitudes, longitudes, points


def _chunks(values: list, size: int):
    for i in range(0, len(values), size):
        yield values[i : i + size]


def _coerce_api_locations(payload, expected: int) -> list[dict]:
    if isinstance(payload, dict):
        rows = [payload]
    elif isinstance(payload, list):
        rows = payload
    else:
        raise RuntimeError(f"Unexpected JMA API response type: {type(payload)}")
    if len(rows) != expected:
        raise RuntimeError(
            f"JMA API returned {len(rows)} locations, expected {expected}"
        )
    return rows


def _request_batch(
    batch: list[tuple[float, float]],
    *,
    forecast_hours: int,
    timeout: int = 120,
    retries: int = DEFAULT_RETRIES,
    session: requests.Session | None = None,
) -> list[dict]:
    client = session or requests.Session()
    params = {
        "latitude": ",".join(f"{lat:.6f}" for lat, _ in batch),
        "longitude": ",".join(f"{lon:.6f}" for _, lon in batch),
        "hourly": ",".join(API_VARIABLES),
        "forecast_hours": int(forecast_hours),
        "models": JMA_MSM_MODEL,
        "cell_selection": "nearest",
        # Disable Open-Meteo elevation downscaling: cloud cover should remain
        # the JMA model-grid quantity.
        "elevation": ",".join("nan" for _ in batch),
        "timezone": "GMT",
    }

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = client.get(JMA_MSM_API_URL, params=params, timeout=timeout)
            try:
                response.raise_for_status()
            except Exception as exc:
                body = getattr(response, "text", "")
                raise RuntimeError(
                    f"{exc}; response={body[:500]}"
                ) from exc
            payload = response.json()
            return _coerce_api_locations(payload, len(batch))
        except Exception as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(min(2 ** (attempt - 1), 4))
    raise RuntimeError(f"JMA MSM API request failed: {last_error}")


def fetch_snapshot(
    *,
    bbox: dict[str, float] | None = None,
    forecast_hours: int = DEFAULT_FORECAST_HOURS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    session: requests.Session | None = None,
) -> dict:
    if forecast_hours < 1:
        raise ValueError("forecast_hours must be >= 1")
    if forecast_hours > JMA_MSM_EXTENDED_HORIZON_HOURS + 1:
        raise ValueError(
            f"forecast_hours must be <= {JMA_MSM_EXTENDED_HORIZON_HOURS + 1}"
        )
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    bbox = dict(bbox or JMA_MSM_TAIWAN_BROWSER_BBOX)
    latitudes, longitudes, points = build_grid(bbox)
    rows = len(latitudes)
    cols = len(longitudes)

    canonical_times = None
    frame_values = None
    returned_grid = []
    query_count = 0

    for batch in _chunks(points, batch_size):
        query_count += 1
        locations = _request_batch(
            batch,
            forecast_hours=forecast_hours,
            session=session,
        )
        for requested, location in zip(batch, locations):
            hourly = location.get("hourly") or {}
            times = hourly.get("time")
            if not times:
                raise RuntimeError("JMA MSM API response has no hourly time axis")
            if canonical_times is None:
                canonical_times = list(times)
                frame_values = [
                    {target: [] for target in API_VARIABLES.values()}
                    for _ in canonical_times
                ]
            elif list(times) != canonical_times:
                raise RuntimeError("JMA MSM API batches returned different time axes")

            for source_name, target_name in API_VARIABLES.items():
                values = hourly.get(source_name)
                if values is None or len(values) != len(canonical_times):
                    raise RuntimeError(
                        f"JMA MSM API missing/incomplete {source_name}"
                    )
                for idx, value in enumerate(values):
                    frame_values[idx][target_name].append(
                        None if value is None else float(value)
                    )

            returned_grid.append(
                {
                    "requested_lat": requested[0],
                    "requested_lon": requested[1],
                    "returned_lat": location.get("latitude"),
                    "returned_lon": location.get("longitude"),
                }
            )

    assert canonical_times is not None
    assert frame_values is not None

    expected_cells = rows * cols
    for frame in frame_values:
        for key, values in frame.items():
            if len(values) != expected_cells:
                raise RuntimeError(
                    f"{key} cell count {len(values)} != {expected_cells}"
                )

    frames = []
    for idx, (valid_time, values) in enumerate(
        zip(canonical_times, frame_values)
    ):
        frames.append(
            {
                "forecast_hour": idx,
                "valid_time_utc": _utc_iso(valid_time),
                "values": values,
            }
        )

    return {
        "schema_version": 1,
        "model_id": "jma_msm",
        "provider": "Japan Meteorological Agency (JMA)",
        "model": "JMA_MSM",
        "transport": {
            "adapter": "Open-Meteo JMA API",
            "endpoint": JMA_MSM_API_URL,
            "model_parameter": JMA_MSM_MODEL,
            "cell_selection": "nearest",
            "elevation_downscaling": False,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cycle": {
            "cycle_time_utc": None,
            "label": "latest available JMA MSM API snapshot",
        },
        "bbox": bbox,
        "native_domain": JMA_MSM_NATIVE_DOMAIN,
        "provenance": {
            "native_resolution_km": JMA_MSM_NATIVE_RESOLUTION_KM,
            "native_lat_step_degrees": JMA_MSM_LAT_STEP_DEG,
            "native_lon_step_degrees": JMA_MSM_LON_STEP_DEG,
            "native_time_interval_hours": JMA_MSM_NATIVE_TIME_INTERVAL_HOURS,
            "update_interval_hours": JMA_MSM_UPDATE_INTERVAL_HOURS,
            "standard_forecast_horizon_hours": JMA_MSM_STANDARD_HORIZON_HOURS,
            "extended_forecast_horizon_hours": JMA_MSM_EXTENDED_HORIZON_HOURS,
            "extended_cycles_utc": list(JMA_MSM_EXTENDED_CYCLES_UTC),
            "published_forecast_hours": len(frames),
            "forecast_hour_semantics": (
                "hours_from_first_published_valid_time_not_model_cycle"
            ),
            "cycle_timestamp_available": False,
            "query_count": query_count,
            "transport_note": (
                "Cloud fields are native JMA MSM fields delivered through "
                "Open-Meteo; nearest native cell is requested and elevation "
                "downscaling is disabled."
            ),
        },
        "grid": {
            "rows": rows,
            "cols": cols,
            "latitudes": latitudes,
            "longitudes": longitudes,
        },
        "fields": {
            key: {
                "unit": "%",
                "vertical_definition": JMA_MSM_CLOUD_VERTICAL_DEFINITIONS[key],
            }
            for key in (
                "total_cloud_percent",
                "low_cloud_percent",
                "mid_cloud_percent",
                "high_cloud_percent",
            )
        },
        "frames": frames,
        "returned_grid_sample": returned_grid[:12],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="jma_msm_output")
    parser.add_argument(
        "--forecast-hours",
        type=int,
        default=DEFAULT_FORECAST_HOURS,
        help="Number of hourly timestamps to fetch from the latest API view.",
    )
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--leftlon", type=float, default=None)
    parser.add_argument("--rightlon", type=float, default=None)
    parser.add_argument("--bottomlat", type=float, default=None)
    parser.add_argument("--toplat", type=float, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bbox = dict(JMA_MSM_TAIWAN_BROWSER_BBOX)
    for key in ("leftlon", "rightlon", "bottomlat", "toplat"):
        value = getattr(args, key)
        if value is not None:
            bbox[key] = value

    if not (
        JMA_MSM_NATIVE_DOMAIN["leftlon"] <= bbox["leftlon"] < bbox["rightlon"]
        <= JMA_MSM_NATIVE_DOMAIN["rightlon"]
        and JMA_MSM_NATIVE_DOMAIN["bottomlat"]
        <= bbox["bottomlat"]
        < bbox["toplat"]
        <= JMA_MSM_NATIVE_DOMAIN["toplat"]
    ):
        raise ValueError(f"bbox is outside JMA MSM native domain: {bbox}")

    lats, lons, points = build_grid(bbox)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "model_id": "jma_msm",
                    "api_url": JMA_MSM_API_URL,
                    "bbox": bbox,
                    "grid": [len(lats), len(lons)],
                    "points": len(points),
                    "forecast_hours": args.forecast_hours,
                    "batch_size": args.batch_size,
                    "estimated_requests": math.ceil(
                        len(points) / args.batch_size
                    ),
                    "fields": list(API_VARIABLES.values()),
                },
                indent=2,
            )
        )
        return 0

    snapshot = fetch_snapshot(
        bbox=bbox,
        forecast_hours=args.forecast_hours,
        batch_size=args.batch_size,
    )
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "jma_msm_tw_cloud_raw.json"
    path.write_text(
        json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "raw_snapshot": str(path),
                "frames": len(snapshot["frames"]),
                "grid": [
                    snapshot["grid"]["rows"],
                    snapshot["grid"]["cols"],
                ],
                "fields": list(snapshot["fields"]),
                "bbox": snapshot["bbox"],
                "query_count": snapshot["provenance"]["query_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
