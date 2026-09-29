"""B117 ChaseLights GFS multi-layer WeatherGrid proof of concept.

This POC extends the proven low-cloud pipeline without changing production
scoring. It downloads one small Taiwan subset from NOAA/NCEP GFS and extracts:

- low / middle / high cloud cover
- surface visibility
- surface precipitation rate
- 10 m wind U/V, plus derived speed and meteorological direction

It writes one browser-friendly WeatherGrid JSON and one six-panel validation
PNG per forecast hour, plus a per-Place time series and manifest.

Example:
    python gfs_multilayer_poc.py --forecast-hours 0,3,6,9,12 \
      --output-dir gfs_multilayer_output
"""

from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from gfs_raw_poc import (
    GFSRun,
    NOMADS_FILTER_URL,
    TAIWAN_BBOX,
    active_taiwan_spots,
    candidate_runs,
    haversine_km,
    parse_forecast_hours,
    validate_cycle,
)

REQUEST_PARAMS = {
    "var_LCDC": "on",
    "var_MCDC": "on",
    "var_HCDC": "on",
    "var_VIS": "on",
    "var_PRATE": "on",
    "var_UGRD": "on",
    "var_VGRD": "on",
    "lev_low_cloud_layer": "on",
    "lev_middle_cloud_layer": "on",
    "lev_high_cloud_layer": "on",
    "lev_surface": "on",
    "lev_10_m_above_ground": "on",
}

FIELD_SPECS = {
    "low_cloud_percent": {
        "aliases": {"lcc", "lcdc"},
        "level": "lowcloudlayer",
        "kind": "percent",
    },
    "mid_cloud_percent": {
        "aliases": {"mcc", "mcdc"},
        "level": "middlecloudlayer",
        "kind": "percent",
    },
    "high_cloud_percent": {
        "aliases": {"hcc", "hcdc"},
        "level": "highcloudlayer",
        "kind": "percent",
    },
    "visibility_km": {
        "aliases": {"vis"},
        "level": "surface",
        "kind": "visibility",
    },
    "precip_rate_mm_h": {
        "aliases": {"prate"},
        "level": "surface",
        "kind": "precip_rate",
    },
    "wind_u_10m_m_s": {
        "aliases": {"10u", "u10", "u", "ugrd"},
        "level": "heightaboveground",
        "kind": "wind",
    },
    "wind_v_10m_m_s": {
        "aliases": {"10v", "v10", "v", "vgrd"},
        "level": "heightaboveground",
        "kind": "wind",
    },
}

DEFAULT_FORECAST_HOURS = (0, 3, 6, 9, 12)


def build_multilayer_url(run: GFSRun, bbox: dict[str, float] | None = None) -> str:
    bbox = dict(TAIWAN_BBOX if bbox is None else bbox)
    if bbox["leftlon"] >= bbox["rightlon"] or bbox["bottomlat"] >= bbox["toplat"]:
        raise ValueError(f"invalid bounding box: {bbox}")
    params = {
        "file": run.filename,
        **REQUEST_PARAMS,
        "subregion": "",
        **bbox,
        "dir": run.directory,
    }
    return f"{NOMADS_FILTER_URL}?{urlencode(params)}"


def download_multilayer_grib(
    runs: list[GFSRun],
    destination: Path,
    timeout: int = 60,
    retry_wait_seconds: int = 10,
    bbox: dict[str, float] | None = None,
) -> tuple[GFSRun, str]:
    import requests

    destination.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for index, run in enumerate(runs):
        url = build_multilayer_url(run, bbox=bbox)
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            payload = response.content
            if len(payload) < 16 or payload[:4] != b"GRIB":
                raise RuntimeError(
                    f"response is not GRIB2 (status={response.status_code}, "
                    f"content_type={response.headers.get('content-type')!r}, "
                    f"bytes={len(payload)}, prefix={payload[:80]!r})"
                )
            destination.write_bytes(payload)
            return run, url
        except Exception as exc:
            errors.append(f"{run.id}: {exc}")
            if index < len(runs) - 1:
                time.sleep(retry_wait_seconds)
    raise RuntimeError("No candidate GFS run downloaded: " + " | ".join(errors))


def _coord_values(dataset, names: tuple[str, ...]):
    for name in names:
        if name in dataset.coords:
            return dataset.coords[name].values
    return None


def _norm_token(value) -> str:
    return str(value or "").lower().replace("_", "").replace(" ", "")


def _field_candidates(datasets, spec: dict):
    candidates = []
    for ds in datasets:
        for name, array in ds.data_vars.items():
            attrs = array.attrs or {}
            short_name = _norm_token(attrs.get("GRIB_shortName", name))
            data_name = _norm_token(name)
            type_of_level = _norm_token(attrs.get("GRIB_typeOfLevel", ""))
            score = 0
            aliases = {_norm_token(x) for x in spec["aliases"]}
            if short_name in aliases:
                score += 8
            if data_name in aliases:
                score += 5
            if spec["level"] == type_of_level:
                score += 8
            if array.ndim >= 2:
                score += 1
            candidates.append((score, ds, name, array))
    return sorted(candidates, key=lambda item: item[0], reverse=True)


def _normalize_values(values, kind: str, units: str):
    import numpy as np

    arr = np.asarray(values, dtype=float)
    units_l = str(units or "").lower()

    if kind == "percent":
        finite = arr[np.isfinite(arr)]
        if finite.size and float(np.nanmax(finite)) <= 1.5:
            arr = arr * 100.0
        return np.clip(arr, 0.0, 100.0), "%"

    if kind == "visibility":
        if units_l.strip() in {"m", "meter", "metre", "meters", "metres"}:
            arr = arr / 1000.0
        return np.maximum(arr, 0.0), "km"

    if kind == "precip_rate":
        # GFS PRATE is normally kg m^-2 s^-1; 1 kg m^-2 water = 1 mm.
        if "s" in units_l and ("kg" in units_l or "mm" in units_l):
            arr = arr * 3600.0
        return np.maximum(arr, 0.0), "mm/h"

    if kind == "wind":
        return arr, "m/s"

    return arr, units or ""


def extract_fields(grib_path: Path) -> dict[str, dict]:
    import cfgrib
    import numpy as np

    datasets = cfgrib.open_datasets(
        str(grib_path),
        backend_kwargs={"indexpath": ""},
    )
    fields = {}

    for key, spec in FIELD_SPECS.items():
        candidates = _field_candidates(datasets, spec)
        if not candidates or candidates[0][0] < 9:
            available = sorted({
                f"{name}:{(array.attrs or {}).get('GRIB_typeOfLevel')}"
                for ds in datasets
                for name, array in ds.data_vars.items()
            })
            raise RuntimeError(
                f"Could not identify required field {key}; available={available}"
            )

        score, ds, name, array = candidates[0]
        values = np.squeeze(np.asarray(array.values, dtype=float))
        if values.ndim != 2:
            raise RuntimeError(f"{key} expected 2-D grid, got {values.shape}")

        lat = _coord_values(ds, ("latitude", "lat"))
        lon = _coord_values(ds, ("longitude", "lon"))
        if lat is None or lon is None:
            raise RuntimeError(f"{key} is missing latitude/longitude coordinates")

        normalized, normalized_unit = _normalize_values(
            values,
            spec["kind"],
            (array.attrs or {}).get("units", ""),
        )
        fields[key] = {
            "field_name": name,
            "field_attrs": {
                "short_name": (array.attrs or {}).get("GRIB_shortName"),
                "type_of_level": (array.attrs or {}).get("GRIB_typeOfLevel"),
                "long_name": (
                    (array.attrs or {}).get("long_name")
                    or (array.attrs or {}).get("GRIB_name")
                ),
                "source_units": (array.attrs or {}).get("units"),
                "normalized_units": normalized_unit,
            },
            "latitudes": np.asarray(lat, dtype=float).tolist(),
            "longitudes": np.asarray(lon, dtype=float).tolist(),
            "values": normalized.tolist(),
        }

    fields.update(_derive_wind_fields(fields))
    return fields


def _derive_wind_fields(fields: dict[str, dict]) -> dict[str, dict]:
    import numpy as np

    u = fields["wind_u_10m_m_s"]
    v = fields["wind_v_10m_m_s"]
    ua = np.asarray(u["values"], dtype=float)
    va = np.asarray(v["values"], dtype=float)
    speed = np.sqrt(ua ** 2 + va ** 2)
    # Meteorological direction: direction wind is coming from.
    direction = (270.0 - np.degrees(np.arctan2(va, ua))) % 360.0

    base = {
        "latitudes": u["latitudes"],
        "longitudes": u["longitudes"],
    }
    return {
        "wind_speed_10m_m_s": {
            **base,
            "field_name": "derived_wind_speed_10m",
            "field_attrs": {
                "short_name": "wind_speed_10m",
                "type_of_level": "heightAboveGround",
                "long_name": "10 m wind speed derived from GFS U/V",
                "source_units": "m/s",
                "normalized_units": "m/s",
            },
            "values": speed.tolist(),
        },
        "wind_direction_10m_deg": {
            **base,
            "field_name": "derived_wind_direction_10m",
            "field_attrs": {
                "short_name": "wind_direction_10m",
                "type_of_level": "heightAboveGround",
                "long_name": "10 m meteorological wind direction derived from GFS U/V",
                "source_units": "degree",
                "normalized_units": "degree",
            },
            "values": direction.tolist(),
        },
    }


def _mesh(field: dict):
    import numpy as np

    lat = np.asarray(field["latitudes"], dtype=float)
    lon = np.asarray(field["longitudes"], dtype=float)
    values = np.asarray(field["values"], dtype=float)
    if lat.ndim == 1 and lon.ndim == 1:
        x, y = np.meshgrid(lon, lat)
    elif lat.shape == lon.shape:
        x, y = lon, lat
    else:
        raise RuntimeError(f"unsupported coordinate shapes {lat.shape}, {lon.shape}")
    if values.shape != x.shape:
        raise RuntimeError(f"grid shape mismatch {values.shape} vs {x.shape}")
    return x, y, values


def sample_field_nearest(field: dict, lat: float, lon: float) -> dict:
    import numpy as np

    x, y, values = _mesh(field)
    distance2 = (x - float(lon)) ** 2 + (y - float(lat)) ** 2
    row, col = np.unravel_index(np.nanargmin(distance2), distance2.shape)
    grid_lat = float(y[row, col])
    grid_lon = float(x[row, col])
    return {
        "value": round(float(values[row, col]), 3),
        "grid_lat": grid_lat,
        "grid_lon": grid_lon,
        "grid_distance_km": round(
            haversine_km(float(lat), float(lon), grid_lat, grid_lon), 2
        ),
        "grid_row": int(row),
        "grid_col": int(col),
    }


def sample_field_bilinear(field: dict, lat: float, lon: float) -> float:
    import numpy as np

    lat_axis = np.asarray(field["latitudes"], dtype=float)
    lon_axis = np.asarray(field["longitudes"], dtype=float)
    values = np.asarray(field["values"], dtype=float)
    if lat_axis.ndim != 1 or lon_axis.ndim != 1:
        return sample_field_nearest(field, lat, lon)["value"]

    if lat_axis[0] > lat_axis[-1]:
        lat_axis = lat_axis[::-1]
        values = values[::-1, :]
    if lon_axis[0] > lon_axis[-1]:
        lon_axis = lon_axis[::-1]
        values = values[:, ::-1]

    plat, plon = float(lat), float(lon)
    if (
        plat < lat_axis[0] or plat > lat_axis[-1]
        or plon < lon_axis[0] or plon > lon_axis[-1]
    ):
        return sample_field_nearest(field, plat, plon)["value"]

    hi_lat = min(max(int(np.searchsorted(lat_axis, plat, side="right")), 1), len(lat_axis) - 1)
    hi_lon = min(max(int(np.searchsorted(lon_axis, plon, side="right")), 1), len(lon_axis) - 1)
    lo_lat, lo_lon = hi_lat - 1, hi_lon - 1
    y0, y1 = float(lat_axis[lo_lat]), float(lat_axis[hi_lat])
    x0, x1 = float(lon_axis[lo_lon]), float(lon_axis[hi_lon])
    q00 = float(values[lo_lat, lo_lon])
    q10 = float(values[lo_lat, hi_lon])
    q01 = float(values[hi_lat, lo_lon])
    q11 = float(values[hi_lat, hi_lon])
    wx = 0.0 if x1 == x0 else (plon - x0) / (x1 - x0)
    wy = 0.0 if y1 == y0 else (plat - y0) / (y1 - y0)
    return round(
        q00 * (1 - wx) * (1 - wy)
        + q10 * wx * (1 - wy)
        + q01 * (1 - wx) * wy
        + q11 * wx * wy,
        3,
    )


def sample_place(fields: dict[str, dict], spot: dict) -> dict:
    lat, lon = spot["lat"], spot["lon"]
    output = {**spot, "weather": {}}
    sample_keys = [
        "low_cloud_percent",
        "mid_cloud_percent",
        "high_cloud_percent",
        "visibility_km",
        "precip_rate_mm_h",
    ]
    reference = sample_field_nearest(fields["low_cloud_percent"], lat, lon)

    for key in sample_keys:
        nearest = sample_field_nearest(fields[key], lat, lon)
        bilinear = sample_field_bilinear(fields[key], lat, lon)
        output["weather"][key] = {
            "value": bilinear,
            "nearest": nearest["value"],
            "delta": round(bilinear - nearest["value"], 3),
            "units": fields[key]["field_attrs"]["normalized_units"],
        }

    u = sample_field_bilinear(fields["wind_u_10m_m_s"], lat, lon)
    v = sample_field_bilinear(fields["wind_v_10m_m_s"], lat, lon)
    speed = math.sqrt(u * u + v * v)
    direction = (270.0 - math.degrees(math.atan2(v, u))) % 360.0
    output["weather"]["wind_10m"] = {
        "speed_m_s": round(speed, 3),
        "direction_deg": round(direction, 1),
        "u_m_s": round(u, 3),
        "v_m_s": round(v, 3),
    }
    output["grid_reference"] = {
        k: reference[k]
        for k in ("grid_lat", "grid_lon", "grid_distance_km", "grid_row", "grid_col")
    }
    return output


def sample_places(fields: dict[str, dict], spots: list[dict]) -> list[dict]:
    return [sample_place(fields, spot) for spot in spots]


def _add_map_context(ax, projection, bbox: dict[str, float]):
    import cartopy.feature as cfeature

    ax.add_feature(cfeature.COASTLINE.with_scale("10m"), linewidth=0.7)
    ax.add_feature(cfeature.BORDERS.with_scale("10m"), linewidth=0.4)
    admin1 = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="10m",
        facecolor="none",
    )
    ax.add_feature(admin1, linewidth=0.25, alpha=0.55)
    ax.set_extent(
        [
            bbox["leftlon"],
            bbox["rightlon"],
            bbox["bottomlat"],
            bbox["toplat"],
        ],
        crs=projection,
    )


def render_overview(
    fields: dict[str, dict],
    spots: list[dict],
    output_path: Path,
    title: str,
    bbox: dict[str, float],
) -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    import cartopy.crs as ccrs

    projection = ccrs.PlateCarree()
    fig, axes = plt.subplots(
        2, 3,
        figsize=(15, 9),
        subplot_kw={"projection": projection},
        constrained_layout=True,
    )
    specs = [
        ("low_cloud_percent", "Low cloud (%)", 0, 100),
        ("mid_cloud_percent", "Middle cloud (%)", 0, 100),
        ("high_cloud_percent", "High cloud (%)", 0, 100),
        ("visibility_km", "Visibility (km)", 0, 50),
        ("precip_rate_mm_h", "Precipitation rate (mm/h)", 0, 20),
        ("wind_speed_10m_m_s", "10 m wind speed (m/s)", 0, 30),
    ]

    for ax, (key, label, vmin, vmax) in zip(axes.flat, specs):
        field = fields[key]
        x, y, values = _mesh(field)
        mesh = ax.pcolormesh(
            x, y, values,
            shading="auto",
            vmin=vmin,
            vmax=vmax,
            transform=projection,
        )
        _add_map_context(ax, projection, bbox)
        if spots:
            ax.scatter(
                [s["lon"] for s in spots],
                [s["lat"] for s in spots],
                s=4,
                linewidths=0,
                transform=projection,
            )
        if key == "wind_speed_10m_m_s":
            _, _, u = _mesh(fields["wind_u_10m_m_s"])
            _, _, v = _mesh(fields["wind_v_10m_m_s"])
            stride = 2
            ax.quiver(
                x[::stride, ::stride],
                y[::stride, ::stride],
                u[::stride, ::stride],
                v[::stride, ::stride],
                transform=projection,
                scale=180,
                width=0.002,
            )
        ax.set_title(label, fontsize=9)
        fig.colorbar(mesh, ax=ax, fraction=0.04, pad=0.02)

    fig.suptitle(title, fontsize=12)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=140)
    plt.close(fig)


def write_frame_json(
    fields: dict[str, dict],
    sampled_spots: list[dict],
    run: GFSRun,
    source_url: str,
    output_path: Path,
    bbox: dict[str, float],
    fetch_plan: dict,
) -> None:
    payload = {
        "schema_version": 1,
        "provider": "NOAA/NCEP NOMADS",
        "model": "GFS",
        "grid_resolution_degrees": 0.25,
        "run": {
            "date": run.date,
            "cycle": run.cycle,
            "forecast_hour": run.forecast_hour,
            "id": run.id,
            "cycle_time_utc": run.cycle_time_utc.isoformat(),
            "valid_time_utc": run.valid_time_utc.isoformat(),
        },
        "bbox": bbox,
        "fetch_scope": {
            "requested": fetch_plan.get("requested_scope"),
            "effective": fetch_plan.get("effective_scope"),
            "coverage_complete": fetch_plan.get("coverage_complete"),
            "fallback_reason": fetch_plan.get("fallback_reason"),
        },
        "sampling": {
            "display_value": "bilinear",
            "raw_reference": "nearest_grid_cell",
        },
        "source_url": source_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fields": fields,
        "spots": sampled_spots,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_spot_series(frames: list[dict], spots: list[dict], output_path: Path) -> None:
    by_spot = {
        spot["spot_id"]: {
            "spot_id": spot["spot_id"],
            "name": spot["name"],
            "lat": spot["lat"],
            "lon": spot["lon"],
            "series": [],
        }
        for spot in spots
    }

    for frame in frames:
        run = frame["run"]
        for sampled in frame["sampled_spots"]:
            by_spot[sampled["spot_id"]]["series"].append({
                "forecast_hour": run.forecast_hour,
                "valid_time_utc": run.valid_time_utc.isoformat(),
                **sampled["weather"],
                "grid_reference": sampled["grid_reference"],
            })

    output_path.write_text(
        json.dumps({
            "schema_version": 1,
            "provider": "NOAA/NCEP NOMADS",
            "model": "GFS",
            "variables": list(FIELD_SPECS) + [
                "wind_speed_10m_m_s",
                "wind_direction_10m_deg",
            ],
            "places": list(by_spot.values()),
        }, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_manifest(
    frames: list[dict],
    output_path: Path,
    bbox: dict[str, float],
    fetch_plan: dict,
) -> None:
    first = frames[0]["run"]
    payload = {
        "schema_version": 1,
        "provider": "NOAA/NCEP NOMADS",
        "model": "GFS",
        "cycle": {
            "date": first.date,
            "cycle": first.cycle,
            "cycle_time_utc": first.cycle_time_utc.isoformat(),
        },
        "bbox": bbox,
        "fetch_scope": {
            "requested": fetch_plan.get("requested_scope"),
            "effective": fetch_plan.get("effective_scope"),
            "coverage_complete": fetch_plan.get("coverage_complete"),
            "fallback_reason": fetch_plan.get("fallback_reason"),
        },
        "variables": list(FIELD_SPECS) + [
            "wind_speed_10m_m_s",
            "wind_direction_10m_deg",
        ],
        "frames": [
            {
                "forecast_hour": frame["run"].forecast_hour,
                "valid_time_utc": frame["run"].valid_time_utc.isoformat(),
                "grib2": frame["grib_path"].name,
                "json": frame["json_path"].name,
                "overview_png": frame["png_path"].name,
            }
            for frame in frames
        ],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="GFS run date YYYYMMDD")
    parser.add_argument("--cycle", help="GFS cycle: 00, 06, 12 or 18")
    parser.add_argument(
        "--forecast-hours",
        default=",".join(str(x) for x in DEFAULT_FORECAST_HOURS),
    )
    parser.add_argument("--output-dir", default="gfs_multilayer_output")
    parser.add_argument(
        "--coverage-scope",
        choices=("region", "place", "opportunity"),
        default="region",
        help="Provider request scope. Scoped requests use B120/B121 coverage.",
    )
    parser.add_argument(
        "--coverage-id",
        help="Place or Opportunity ID required for scoped requests.",
    )
    parser.add_argument(
        "--strict-coverage",
        action="store_true",
        help="Fail instead of falling back to the Taiwan regional bbox when coverage is incomplete.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.date) != bool(args.cycle):
        raise SystemExit("--date and --cycle must be provided together")
    forecast_hours = parse_forecast_hours(args.forecast_hours)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    from weathergrid_fetch_plan import build_gfs_fetch_plan, write_fetch_plan

    fetch_plan = build_gfs_fetch_plan(
        scope_type=args.coverage_scope,
        scope_id=args.coverage_id,
        region="tw",
        strict=args.strict_coverage,
    )
    if len(fetch_plan["segments"]) != 1:
        raise SystemExit(
            "B123 GFS POC currently supports one NOMADS rectangle per run; "
            "antimeridian split plans are validated but not yet downloaded."
        )
    request_bbox = fetch_plan["segments"][0]
    fetch_plan_path = out / "gfs_tw_weather_fetch_plan.json"
    write_fetch_plan(fetch_plan, fetch_plan_path)

    if args.date and args.cycle:
        candidate_base_runs = [
            GFSRun(args.date, validate_cycle(args.cycle), max(forecast_hours))
        ]
    else:
        candidate_base_runs = candidate_runs(
            forecast_hour=max(forecast_hours),
            count=4,
        )

    if args.dry_run:
        print(json.dumps({
            "fetch_plan": fetch_plan,
            "candidate_runs": [
                {
                    "candidate_cycle": {"date": run.date, "cycle": run.cycle},
                    "urls": [
                        {
                            "forecast_hour": fh,
                            "url": build_multilayer_url(
                                GFSRun(run.date, run.cycle, fh),
                                bbox=request_bbox,
                            ),
                        }
                        for fh in forecast_hours
                    ],
                }
                for run in candidate_base_runs
            ],
        }, indent=2))
        return 0

    anchor_fh = max(forecast_hours)
    anchor_path = out / f"gfs_tw_weather_f{anchor_fh:03d}.grib2"
    anchor_run, anchor_url = download_multilayer_grib(
        candidate_base_runs,
        anchor_path,
        bbox=request_bbox,
    )
    selected_date, selected_cycle = anchor_run.date, anchor_run.cycle
    spots = active_taiwan_spots()
    scoped_spot_ids = set(fetch_plan.get("spot_ids") or [])
    if scoped_spot_ids:
        spots = [spot for spot in spots if spot.get("spot_id") in scoped_spot_ids]
    frames = []

    for index, fh in enumerate(forecast_hours):
        run = GFSRun(selected_date, selected_cycle, fh)
        grib_path = out / f"gfs_tw_weather_f{fh:03d}.grib2"
        if fh == anchor_fh:
            source_url = anchor_url
        else:
            run, source_url = download_multilayer_grib(
                [run],
                grib_path,
                retry_wait_seconds=0,
                bbox=request_bbox,
            )
            if index < len(forecast_hours) - 1:
                time.sleep(1)

        fields = extract_fields(grib_path)
        sampled_spots = sample_places(fields, spots)
        json_path = out / f"gfs_tw_weather_f{fh:03d}.json"
        png_path = out / f"gfs_tw_weather_f{fh:03d}.png"
        write_frame_json(
            fields,
            sampled_spots,
            run,
            source_url,
            json_path,
            request_bbox,
            fetch_plan,
        )
        render_overview(
            fields,
            spots,
            png_path,
            title=(
                "GFS 0.25° WeatherGrid · "
                f"{run.id} · valid {run.valid_time_utc:%Y-%m-%d %H:%MZ}"
            ),
            bbox=request_bbox,
        )
        frames.append({
            "run": run,
            "sampled_spots": sampled_spots,
            "grib_path": grib_path,
            "json_path": json_path,
            "png_path": png_path,
        })

    manifest_path = out / "gfs_tw_weather_manifest.json"
    series_path = out / "gfs_tw_weather_spot_series.json"
    write_manifest(frames, manifest_path, request_bbox, fetch_plan)
    write_spot_series(frames, spots, series_path)

    print(json.dumps({
        "cycle": f"{selected_date}T{selected_cycle}Z",
        "forecast_hours": forecast_hours,
        "frames": len(frames),
        "spots": len(spots),
        "variables": list(FIELD_SPECS) + [
            "wind_speed_10m_m_s",
            "wind_direction_10m_deg",
        ],
        "manifest": str(manifest_path),
        "spot_series": str(series_path),
        "fetch_plan": str(fetch_plan_path),
        "requested_scope": fetch_plan.get("requested_scope"),
        "effective_scope": fetch_plan.get("effective_scope"),
        "coverage_complete": fetch_plan.get("coverage_complete"),
        "request_bbox": request_bbox,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
