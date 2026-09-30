"""JMA MSM 5 km cloud provider for ChaseLights WeatherGrid.

Data source
-----------
JMA's MSM surface GPV contains native total/low/middle/high cloud cover.
ChaseLights reads the same native JMA fields from Open-Meteo's AWS Open Data
spatial mirror (CC-BY-4.0), which preserves the native 0.05° x 0.0625°
regular grid and hourly valid times.

The source is still identified as JMA MSM.  Open-Meteo is the transport/mirror,
not a replacement forecast model.

JMA native domain:
    22.4N..47.6N, 120E..150E
    0.05° latitude x 0.0625° longitude
    481 x 505 surface grid
    hourly surface output
    39 h, extended to 78 h for 00/12 UTC runs

B153 initially publishes only a Taiwan-relevant subset and an hourly 0..12 h
window.  This keeps the browser payload small while preserving native spatial
and temporal resolution inside the published region.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from gfs_raw_poc import active_taiwan_spots, parse_forecast_hours
from gfs_multilayer_poc import sample_field_bilinear

OPEN_METEO_BUCKET = "openmeteo"
OPEN_METEO_SPATIAL_PREFIX = "data_spatial/jma_msm"

JMA_MSM_NATIVE = {
    "leftlon": 120.0,
    "rightlon": 150.0,
    "bottomlat": 22.4,
    "toplat": 47.6,
    "dx": 0.0625,
    "dy": 0.05,
    "nx": 481,
    "ny": 505,
    "native_resolution_km": 5.0,
    "update_interval_hours": 3,
    "surface_time_interval_hours": 1,
}

# Taiwan-relevant part of the native MSM domain.  Southern Taiwan below 22.4 N
# and islands west of 120 E are outside MSM's published native domain.
JMA_TAIWAN_BROWSER_BBOX = {
    "leftlon": 120.0,
    "rightlon": 123.0,
    "bottomlat": 22.4,
    "toplat": 26.0,
}

DEFAULT_FORECAST_HOURS = tuple(range(0, 13))

SOURCE_FIELDS = {
    "total_cloud_percent": "cloud_cover",
    "low_cloud_percent": "cloud_cover_low",
    "mid_cloud_percent": "cloud_cover_mid",
    "high_cloud_percent": "cloud_cover_high",
}

JMA_CLOUD_VERTICAL_DEFINITIONS = {
    "low_cloud_percent": {
        "coordinate": "model_levels_reference_pressure",
        "native_definition": "下層：地表～約850 hPa（地上気圧1000 hPa時の基準）",
        "approx_height": "約地面～1.5 km",
        "reference_pressure_bounds_hpa": {
            "bottom": "surface",
            "top": 850,
        },
        "definition_source": "JMA NWP product calculation method",
        "note": (
            "JMA first diagnoses model-level cloud amount, then combines model "
            "layers. 850 hPa is the reference low/mid boundary when surface "
            "pressure is 1000 hPa."
        ),
    },
    "mid_cloud_percent": {
        "coordinate": "model_levels_reference_pressure",
        "native_definition": "中層：約850～500 hPa（地上気圧1000 hPa時の基準）",
        "approx_height": "約1.5～5.6 km",
        "reference_pressure_bounds_hpa": {
            "bottom": 850,
            "top": 500,
        },
        "definition_source": "JMA NWP product calculation method",
        "note": (
            "500 hPa is the reference mid/high boundary when surface pressure "
            "is 1000 hPa."
        ),
    },
    "high_cloud_percent": {
        "coordinate": "model_levels_reference_pressure",
        "native_definition": "上層：約500 hPa以上（低圧側）",
        "approx_height": "約5.6 km 以上",
        "reference_pressure_bounds_hpa": {
            "bottom": 500,
            "top": "model_top",
        },
        "definition_source": "JMA NWP product calculation method",
        "note": "Pressure boundaries are authoritative references; km text is approximate.",
    },
}


@dataclass(frozen=True)
class JmaMsmRun:
    cycle_time_utc: datetime

    @property
    def max_forecast_hour(self) -> int:
        return 78 if self.cycle_time_utc.hour in (0, 12) else 39


def validate_forecast_hours(hours) -> list[int]:
    result = sorted(dict.fromkeys(int(x) for x in hours))
    if not result:
        raise ValueError("forecast-hour list cannot be empty")
    if result[0] < 0:
        raise ValueError("forecast hour cannot be negative")
    if result[-1] > 78:
        raise ValueError("JMA MSM forecast hour cannot exceed 78 h")
    return result


def candidate_runs(
    now: datetime | None = None,
    *,
    publication_lag_hours: float = 2.5,
    count: int = 10,
) -> list[JmaMsmRun]:
    """Newest likely-published 3-hourly MSM runs, with older fallbacks."""
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    eligible = now.astimezone(timezone.utc) - timedelta(hours=publication_lag_hours)
    floored_hour = eligible.hour - (eligible.hour % 3)
    first = eligible.replace(hour=floored_hour, minute=0, second=0, microsecond=0)
    return [
        JmaMsmRun(first - timedelta(hours=3 * i))
        for i in range(count)
    ]


def spatial_key(run: JmaMsmRun, forecast_hour: int) -> str:
    valid = run.cycle_time_utc + timedelta(hours=int(forecast_hour))
    return (
        f"{OPEN_METEO_SPATIAL_PREFIX}/"
        f"{run.cycle_time_utc:%Y/%m/%d/%H%M}Z/"
        f"{valid:%Y-%m-%dT%H%M}.om"
    )


def s3_uri(run: JmaMsmRun, forecast_hour: int) -> str:
    return f"s3://{OPEN_METEO_BUCKET}/{spatial_key(run, forecast_hour)}"


def _anonymous_s3_client():
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config

    return boto3.client(
        "s3",
        region_name="us-west-2",
        config=Config(signature_version=UNSIGNED),
    )


def resolve_run(
    forecast_hours: list[int],
    *,
    now: datetime | None = None,
) -> JmaMsmRun:
    """Choose the freshest run that covers all requested leads and exists."""
    s3 = _anonymous_s3_client()
    hours = validate_forecast_hours(forecast_hours)
    for run in candidate_runs(now):
        if max(hours) > run.max_forecast_hour:
            continue
        # Check first and last requested timestamps.  If those exist, interior
        # hourly files for the same completed run are expected to exist too.
        keys = {spatial_key(run, hours[0]), spatial_key(run, hours[-1])}
        ok = True
        for key in keys:
            try:
                s3.head_object(Bucket=OPEN_METEO_BUCKET, Key=key)
            except Exception:
                ok = False
                break
        if ok:
            return run
    raise RuntimeError(
        "No recent Open-Meteo JMA MSM spatial run covers "
        f"forecast hours {hours[0]}..{hours[-1]}"
    )


def _grid_index(lon: float, lat: float) -> tuple[int, int]:
    col = int(round((lon - JMA_MSM_NATIVE["leftlon"]) / JMA_MSM_NATIVE["dx"]))
    row = int(round((lat - JMA_MSM_NATIVE["bottomlat"]) / JMA_MSM_NATIVE["dy"]))
    return row, col


def subset_slices(bbox: dict[str, float]) -> tuple[slice, slice, list[float], list[float]]:
    r0, c0 = _grid_index(bbox["leftlon"], bbox["bottomlat"])
    r1, c1 = _grid_index(bbox["rightlon"], bbox["toplat"])
    if r0 < 0 or c0 < 0 or r1 >= JMA_MSM_NATIVE["ny"] or c1 >= JMA_MSM_NATIVE["nx"]:
        raise ValueError(f"bbox outside JMA MSM native grid: {bbox}")
    rows = slice(min(r0, r1), max(r0, r1) + 1)
    cols = slice(min(c0, c1), max(c0, c1) + 1)
    latitudes = [
        JMA_MSM_NATIVE["bottomlat"] + i * JMA_MSM_NATIVE["dy"]
        for i in range(rows.start, rows.stop)
    ]
    longitudes = [
        JMA_MSM_NATIVE["leftlon"] + i * JMA_MSM_NATIVE["dx"]
        for i in range(cols.start, cols.stop)
    ]
    return rows, cols, latitudes, longitudes


def read_cloud_frame(
    run: JmaMsmRun,
    forecast_hour: int,
    *,
    bbox: dict[str, float] | None = None,
    cache_dir: Path | None = None,
) -> dict:
    import fsspec
    import numpy as np
    from omfiles import OmFileReader

    bbox = dict(bbox or JMA_TAIWAN_BROWSER_BBOX)
    rows, cols, latitudes, longitudes = subset_slices(bbox)
    cache_dir = cache_dir or Path(".cache/openmeteo-jma-msm")
    cache_dir.mkdir(parents=True, exist_ok=True)

    uri = s3_uri(run, forecast_hour)
    backend = fsspec.open(
        f"blockcache::{uri}",
        mode="rb",
        s3={"anon": True, "default_block_size": 65536},
        blockcache={
            "cache_storage": str(cache_dir),
            "same_names": True,
        },
    )

    fields = {}
    source_shapes = {}
    with OmFileReader(backend) as root:
        for target_name, source_name in SOURCE_FIELDS.items():
            reader = root.get_child_by_name(source_name)
            if reader is None:
                raise KeyError(f"{source_name} missing in {uri}")
            source_shapes[source_name] = list(reader.shape)
            if tuple(reader.shape) != (
                JMA_MSM_NATIVE["ny"],
                JMA_MSM_NATIVE["nx"],
            ):
                raise ValueError(
                    f"Unexpected JMA MSM grid shape for {source_name}: "
                    f"{reader.shape}"
                )
            arr = np.asarray(reader[rows, cols], dtype=float)
            if arr.shape != (len(latitudes), len(longitudes)):
                raise ValueError(
                    f"Unexpected subset shape {arr.shape} for {source_name}"
                )
            arr = np.clip(arr, 0.0, 100.0)
            fields[target_name] = {
                "field_name": source_name,
                "field_attrs": {
                    "source_name": source_name,
                    "source_units": "%",
                    "normalized_units": "%",
                    "native_grid_spacing_degrees": {
                        "latitude": JMA_MSM_NATIVE["dy"],
                        "longitude": JMA_MSM_NATIVE["dx"],
                    },
                    "native_resolution_km": JMA_MSM_NATIVE["native_resolution_km"],
                    **(
                        {
                            "vertical_definition":
                                JMA_CLOUD_VERTICAL_DEFINITIONS[target_name]
                        }
                        if target_name in JMA_CLOUD_VERTICAL_DEFINITIONS
                        else {}
                    ),
                },
                "latitudes": latitudes,
                "longitudes": longitudes,
                "values": arr.tolist(),
            }

    valid = run.cycle_time_utc + timedelta(hours=int(forecast_hour))
    return {
        "schema_version": 1,
        "model_id": "jma_msm",
        "provider": "Japan Meteorological Agency (JMA)",
        "transport": "Open-Meteo AWS Open Data spatial mirror",
        "transport_license": "CC-BY-4.0",
        "model": "JMA_MSM_5KM",
        "native_resolution_km": JMA_MSM_NATIVE["native_resolution_km"],
        "native_domain": {
            key: JMA_MSM_NATIVE[key]
            for key in ("leftlon", "rightlon", "bottomlat", "toplat", "dx", "dy", "nx", "ny")
        },
        "run": {
            "cycle_time_utc": run.cycle_time_utc.isoformat(),
            "forecast_hour": int(forecast_hour),
            "valid_time_utc": valid.isoformat(),
        },
        "bbox": bbox,
        "source_uri": uri,
        "source_shapes": source_shapes,
        "fields": fields,
    }


def sample_places(fields: dict, bbox: dict) -> list[dict]:
    spots = []
    for spot in active_taiwan_spots():
        lon, lat = float(spot["lon"]), float(spot["lat"])
        if not (
            bbox["leftlon"] <= lon <= bbox["rightlon"]
            and bbox["bottomlat"] <= lat <= bbox["toplat"]
        ):
            continue
        weather = {}
        for key, field in fields.items():
            sample = sample_field_bilinear(field, lat, lon)
            value = sample["value"] if isinstance(sample, dict) else sample
            weather[key] = {
                "value": round(float(value), 3),
                "units": "%",
            }
        spots.append({**spot, "weather": weather})
    return spots


def write_frame(frame: dict, output_path: Path) -> None:
    output_path.write_text(
        json.dumps(frame, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_manifest(
    *,
    run: JmaMsmRun,
    frames: list[dict],
    bbox: dict[str, float],
    output_path: Path,
) -> None:
    payload = {
        "schema_version": 1,
        "model_id": "jma_msm",
        "provider": "Japan Meteorological Agency (JMA)",
        "transport": "Open-Meteo AWS Open Data spatial mirror",
        "transport_license": "CC-BY-4.0",
        "model": "JMA_MSM_5KM",
        "cycle": {
            "cycle_time_utc": run.cycle_time_utc.isoformat(),
            "date": run.cycle_time_utc.strftime("%Y%m%d"),
            "cycle": run.cycle_time_utc.strftime("%H"),
        },
        "bbox": bbox,
        "native_domain": {
            key: JMA_MSM_NATIVE[key]
            for key in (
                "leftlon", "rightlon", "bottomlat", "toplat",
                "dx", "dy", "nx", "ny",
            )
        },
        "native_resolution_km": JMA_MSM_NATIVE["native_resolution_km"],
        "native_time_interval_hours": JMA_MSM_NATIVE["surface_time_interval_hours"],
        "update_interval_hours": JMA_MSM_NATIVE["update_interval_hours"],
        "max_forecast_hour": run.max_forecast_hour,
        "cloud_vertical_definitions": JMA_CLOUD_VERTICAL_DEFINITIONS,
        "frames": [
            {
                "forecast_hour": item["run"]["forecast_hour"],
                "valid_time_utc": item["run"]["valid_time_utc"],
                "json": item["_filename"],
                "source_uri": item["source_uri"],
            }
            for item in frames
        ],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--forecast-hours",
        default=",".join(str(v) for v in DEFAULT_FORECAST_HOURS),
    )
    parser.add_argument("--output-dir", default="jma_msm_output")
    parser.add_argument("--cache-dir", default=".cache/openmeteo-jma-msm")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hours = validate_forecast_hours(parse_forecast_hours(args.forecast_hours))
    bbox = dict(JMA_TAIWAN_BROWSER_BBOX)

    if args.dry_run:
        now = datetime.now(timezone.utc)
        candidates = candidate_runs(now)
        print(json.dumps({
            "model_id": "jma_msm",
            "forecast_hours": hours,
            "native_domain": JMA_MSM_NATIVE,
            "browser_bbox": bbox,
            "candidate_runs": [
                {
                    "cycle_time_utc": r.cycle_time_utc.isoformat(),
                    "max_forecast_hour": r.max_forecast_hour,
                    "example_uri": s3_uri(r, hours[0]),
                }
                for r in candidates[:4]
            ],
        }, indent=2))
        return 0

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    run = resolve_run(hours)
    frames = []
    for fh in hours:
        frame = read_cloud_frame(
            run,
            fh,
            bbox=bbox,
            cache_dir=Path(args.cache_dir),
        )
        frame["spots"] = sample_places(frame["fields"], bbox)
        filename = f"jma_msm_tw_f{fh:03d}.json"
        frame["_filename"] = filename
        write_frame(
            {k: v for k, v in frame.items() if k != "_filename"},
            out / filename,
        )
        frames.append(frame)

    write_manifest(
        run=run,
        frames=frames,
        bbox=bbox,
        output_path=out / "jma_msm_tw_cloud_manifest.json",
    )
    print(json.dumps({
        "model_id": "jma_msm",
        "cycle_time_utc": run.cycle_time_utc.isoformat(),
        "forecast_hours": hours,
        "frames": len(frames),
        "bbox": bbox,
        "grid": [
            len(frames[0]["fields"]["low_cloud_percent"]["latitudes"]),
            len(frames[0]["fields"]["low_cloud_percent"]["longitudes"]),
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
