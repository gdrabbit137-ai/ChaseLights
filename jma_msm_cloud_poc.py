"""Fetch JMA MSM cloud layers for ChaseLights WeatherGrid.

The Japan Meteorological Agency MSM surface GPV publishes native total / low /
middle / high cloud cover on a 0.05° latitude × 0.0625° longitude regular grid.
Official operational distribution is via JMA/JMBSC GRIB2. ChaseLights reads
Open-Meteo's public AWS Open Data spatial OM files as a free transport layer.

Important:
- The model remains JMA MSM; Open-Meteo AWS is only the transport layer.
- The Taiwan artifact is an exact native-grid slice, not API point sampling.
- No API key, elevation downscaling, or cloud derivation from RH is used.
- The AWS run metadata exposes the actual JMA model cycle and valid times.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from jma_msm_aws_om import fetch_aws_snapshot


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
    # Keep one native cell inside the official south/west edge for the initial
    # browser footprint; the AWS adapter itself can read the exact model edge.
    "leftlon": 120.0625,
    "rightlon": 122.5,
    "bottomlat": 22.45,
    "toplat": 25.6,
}

DEFAULT_FORECAST_HOURS = 40

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


def fetch_snapshot(
    *,
    bbox: dict[str, float] | None = None,
    forecast_hours: int = DEFAULT_FORECAST_HOURS,
    metadata: dict | None = None,
    reader=None,
) -> dict:
    """Fetch native JMA MSM cloud fields from public AWS OM spatial files."""
    if forecast_hours < 1:
        raise ValueError("forecast_hours must be >= 1")
    if forecast_hours > JMA_MSM_EXTENDED_HORIZON_HOURS + 1:
        raise ValueError(
            f"forecast_hours must be <= {JMA_MSM_EXTENDED_HORIZON_HOURS + 1}"
        )

    bbox = dict(bbox or JMA_MSM_TAIWAN_BROWSER_BBOX)
    aws = fetch_aws_snapshot(
        bbox=bbox,
        forecast_hours=forecast_hours,
        metadata=metadata,
        reader=reader,
    )
    frames = aws["frames"]
    return {
        "schema_version": 1,
        "model_id": "jma_msm",
        "provider": "Japan Meteorological Agency (JMA)",
        "model": "JMA_MSM",
        "attribution": {
            "model_provider": "Japan Meteorological Agency (JMA)",
            "transport_provider": "Open-Meteo AWS Open Data",
            "transport_url": "https://registry.opendata.aws/open-meteo/",
            "license": "CC BY 4.0 attribution required for Open-Meteo-served data",
        },
        "transport": aws["transport"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cycle": {
            "cycle_time_utc": aws["reference_time_utc"],
            "label": aws["reference_time_utc"],
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
            "forecast_hour_semantics": "hours_from_model_cycle",
            "cycle_timestamp_available": True,
            "transport_note": (
                "Native JMA MSM cloud arrays are sliced directly from "
                "Open-Meteo AWS Open Data spatial OM files. No forecast API "
                "sampling, elevation downscaling, or paid API key is used."
            ),
            "production_transport": "open_meteo_aws_open_data_om",
            "aws_metadata_completed": aws["metadata_completed"],
            "aws_metadata_last_modified_time": aws[
                "metadata_last_modified_time"
            ],
        },
        "grid": aws["grid"],
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
    }

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="jma_msm_output")
    parser.add_argument(
        "--forecast-hours",
        type=int,
        default=DEFAULT_FORECAST_HOURS,
        help="Number of native hourly timestamps to read from the latest completed JMA run.",
    )
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
                    "transport": "open_meteo_aws_open_data_om",
                    "bbox": bbox,
                    "grid": [len(lats), len(lons)],
                    "points": len(points),
                    "forecast_hours": args.forecast_hours,
                    "native_cells": len(points),
                    "fields": list(API_VARIABLES.values()),
                },
                indent=2,
            )
        )
        return 0

    snapshot = fetch_snapshot(
        bbox=bbox,
        forecast_hours=args.forecast_hours,
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
                "cycle": snapshot["cycle"]["cycle_time_utc"],
                "transport": snapshot["provenance"]["production_transport"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
