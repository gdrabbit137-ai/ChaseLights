"""ChaseLights GFS raw-data proof of concept.

Downloads a small NOAA/NCEP GFS 0.25° GRIB2 subset for Taiwan, extracts
low-cloud cover, samples the grid at ChaseLights Place coordinates, writes
browser-friendly JSON, and renders georeferenced PNGs.

B115 extends the first proof of concept with:
- coastlines / national borders / Natural Earth admin-1 reference lines
- nearest-grid low-cloud values for every active Taiwan Place
- one consistent GFS model run across multiple forecast hours
- a compact per-Place time-series artifact plus a manifest

This module remains isolated from production scoring.

Examples:
    python gfs_raw_poc.py --dry-run
    python gfs_raw_poc.py --forecast-hours 0,3,6,9,12 --output-dir gfs_poc_output
    python gfs_raw_poc.py --date 20260929 --cycle 00 --forecast-hours 0,6,12

Runtime dependencies for a real fetch/render:
    requests cfgrib eccodes xarray numpy matplotlib cartopy
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode

NOMADS_FILTER_URL = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"

# Slightly wider than Taiwan so offshore weather approaching the island is
# visible in the proof-of-concept map.
TAIWAN_BBOX = {
    "leftlon": 117.5,
    "rightlon": 123.5,
    "toplat": 26.75,
    "bottomlat": 20.5,
}

REQUEST_VARIABLES = {
    "var_LCDC": "on",
    "lev_low_cloud_layer": "on",
}

DEFAULT_FORECAST_HOURS = (0, 3, 6, 9, 12, 15, 18, 21, 24)


@dataclass(frozen=True)
class GFSRun:
    date: str
    cycle: str
    forecast_hour: int = 0

    @property
    def filename(self) -> str:
        return f"gfs.t{self.cycle}z.pgrb2.0p25.f{self.forecast_hour:03d}"

    @property
    def directory(self) -> str:
        return f"/gfs.{self.date}/{self.cycle}/atmos"

    @property
    def id(self) -> str:
        return f"{self.date}T{self.cycle}Z_f{self.forecast_hour:03d}"

    @property
    def cycle_time_utc(self) -> datetime:
        return datetime.strptime(
            f"{self.date}{self.cycle}", "%Y%m%d%H"
        ).replace(tzinfo=timezone.utc)

    @property
    def valid_time_utc(self) -> datetime:
        return self.cycle_time_utc + timedelta(hours=self.forecast_hour)


def validate_cycle(value: str) -> str:
    value = str(value).zfill(2)
    if value not in {"00", "06", "12", "18"}:
        raise ValueError(f"GFS cycle must be one of 00/06/12/18, got {value}")
    return value


def validate_forecast_hour(value: int) -> int:
    value = int(value)
    if value < 0 or value > 384:
        raise ValueError("forecast hour must be between 0 and 384")
    return value


def parse_forecast_hours(value: str | Iterable[int] | None) -> list[int]:
    if value is None:
        return list(DEFAULT_FORECAST_HOURS)
    if isinstance(value, str):
        raw = [part.strip() for part in value.split(",") if part.strip()]
        if not raw:
            raise ValueError("forecast-hours must contain at least one hour")
        hours = [validate_forecast_hour(int(part)) for part in raw]
    else:
        hours = [validate_forecast_hour(int(part)) for part in value]
    # Preserve chronological order and remove duplicates.
    return sorted(set(hours))


def candidate_runs(
    now: datetime | None = None,
    forecast_hour: int = 0,
    count: int = 4,
    publication_lag_hours: int = 4,
) -> list[GFSRun]:
    """Return recent likely-published GFS runs, newest first."""
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    probe = now.astimezone(timezone.utc) - timedelta(hours=publication_lag_hours)
    cycle_hour = (probe.hour // 6) * 6
    cycle_dt = probe.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)
    fh = validate_forecast_hour(forecast_hour)
    return [
        GFSRun(
            date=(cycle_dt - timedelta(hours=6 * i)).strftime("%Y%m%d"),
            cycle=(cycle_dt - timedelta(hours=6 * i)).strftime("%H"),
            forecast_hour=fh,
        )
        for i in range(count)
    ]


def build_nomads_url(run: GFSRun, bbox: dict[str, float] | None = None) -> str:
    bbox = dict(TAIWAN_BBOX if bbox is None else bbox)
    if bbox["leftlon"] >= bbox["rightlon"] or bbox["bottomlat"] >= bbox["toplat"]:
        raise ValueError(f"invalid bounding box: {bbox}")
    params = {
        "file": run.filename,
        **REQUEST_VARIABLES,
        "subregion": "",
        **bbox,
        "dir": run.directory,
    }
    return f"{NOMADS_FILTER_URL}?{urlencode(params)}"


def download_grib(
    runs: Iterable[GFSRun],
    destination: Path,
    timeout: int = 60,
    retry_wait_seconds: int = 10,
) -> tuple[GFSRun, str]:
    """Download the first available candidate, respecting NOMADS loop guidance."""
    import requests

    destination.parent.mkdir(parents=True, exist_ok=True)
    runs = list(runs)
    errors: list[str] = []
    for index, run in enumerate(runs):
        url = build_nomads_url(run)
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


def extract_low_cloud(grib_path: Path) -> dict:
    """Extract low-cloud cover as a 2-D percent grid from a GRIB2 subset."""
    import cfgrib
    import numpy as np

    datasets = cfgrib.open_datasets(
        str(grib_path),
        backend_kwargs={"indexpath": ""},
    )
    candidates = []
    for ds in datasets:
        for name, array in ds.data_vars.items():
            attrs = array.attrs or {}
            short_name = str(attrs.get("GRIB_shortName", name)).lower()
            type_of_level = str(attrs.get("GRIB_typeOfLevel", "")).lower()
            long_name = str(attrs.get("long_name", attrs.get("GRIB_name", ""))).lower()
            score = 0
            if short_name in {"lcc", "tcc"}:
                score += 4
            if "lowcloud" in type_of_level.replace("_", ""):
                score += 5
            if "low cloud" in long_name:
                score += 3
            if array.ndim >= 2:
                score += 1
            candidates.append((score, ds, name, array))

    if not candidates:
        raise RuntimeError("No fields found in GRIB2 file")
    candidates.sort(key=lambda item: item[0], reverse=True)
    score, ds, name, array = candidates[0]
    if score <= 1:
        raise RuntimeError(
            "Could not identify a low-cloud field; found "
            + ", ".join(sorted({item[2] for item in candidates}))
        )

    values = np.asarray(array.values, dtype=float)
    values = np.squeeze(values)
    if values.ndim != 2:
        raise RuntimeError(f"Expected a 2-D low-cloud grid, got shape {values.shape}")

    lat = _coord_values(ds, ("latitude", "lat"))
    lon = _coord_values(ds, ("longitude", "lon"))
    if lat is None or lon is None:
        raise RuntimeError("GRIB2 dataset is missing latitude/longitude coordinates")
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)

    finite = values[np.isfinite(values)]
    if finite.size and float(np.nanmax(finite)) <= 1.5:
        values = values * 100.0
    values = np.clip(values, 0.0, 100.0)

    return {
        "field_name": name,
        "field_attrs": {
            "short_name": array.attrs.get("GRIB_shortName"),
            "type_of_level": array.attrs.get("GRIB_typeOfLevel"),
            "long_name": array.attrs.get("long_name") or array.attrs.get("GRIB_name"),
            "units": array.attrs.get("units"),
        },
        "latitudes": lat.tolist(),
        "longitudes": lon.tolist(),
        "values": values.tolist(),
    }


def active_taiwan_spots() -> list[dict]:
    from regions import get_spots

    return [
        {
            "spot_id": spot["spot_id"],
            "name": spot["name_i18n"]["zh-TW"],
            "lat": float(spot["lat"]),
            "lon": float(spot["lon"]),
        }
        for spot in get_spots("tw")
        if spot.get("active_in_catalog", True)
    ]


def _mesh_coordinates(grid: dict):
    import numpy as np

    lat = np.asarray(grid["latitudes"], dtype=float)
    lon = np.asarray(grid["longitudes"], dtype=float)
    values = np.asarray(grid["values"], dtype=float)

    if lat.ndim == 1 and lon.ndim == 1:
        x, y = np.meshgrid(lon, lat)
    elif lat.shape == lon.shape:
        x, y = lon, lat
    else:
        raise RuntimeError(
            f"Unsupported coordinate shapes lat={lat.shape}, lon={lon.shape}"
        )
    if values.shape != x.shape:
        raise RuntimeError(
            f"Grid shape mismatch values={values.shape}, coords={x.shape}"
        )
    return x, y, values


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sample_grid_nearest(grid: dict, lat: float, lon: float) -> dict:
    """Sample the nearest GFS cell and return traceable grid metadata."""
    import numpy as np

    x, y, values = _mesh_coordinates(grid)
    distance2 = (x - float(lon)) ** 2 + (y - float(lat)) ** 2
    row, col = np.unravel_index(np.nanargmin(distance2), distance2.shape)
    grid_lat = float(y[row, col])
    grid_lon = float(x[row, col])
    value = float(values[row, col])
    return {
        "low_cloud_percent": round(value, 2),
        "grid_lat": grid_lat,
        "grid_lon": grid_lon,
        "grid_distance_km": round(
            haversine_km(float(lat), float(lon), grid_lat, grid_lon), 2
        ),
        "grid_row": int(row),
        "grid_col": int(col),
    }


def sample_spots(grid: dict, spots: list[dict]) -> list[dict]:
    return [
        {
            **spot,
            **sample_grid_nearest(grid, spot["lat"], spot["lon"]),
        }
        for spot in spots
    ]


def render_low_cloud_png(
    grid: dict,
    sampled_spots: list[dict],
    output_path: Path,
    title: str,
) -> None:
    import matplotlib.pyplot as plt

    x, y, values = _mesh_coordinates(grid)

    # Cartopy gives the POC geographic context while keeping the weather layer
    # itself in raw model coordinates. Natural Earth admin-1 lines are used as
    # reference boundaries only; they are not part of the weather data source.
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        projection = ccrs.PlateCarree()
        fig = plt.figure(figsize=(9, 9), constrained_layout=True)
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        mesh = ax.pcolormesh(
            x, y, values, shading="auto", vmin=0, vmax=100, transform=projection
        )
        ax.add_feature(cfeature.COASTLINE.with_scale("10m"), linewidth=0.8)
        ax.add_feature(cfeature.BORDERS.with_scale("10m"), linewidth=0.45)
        admin1 = cfeature.NaturalEarthFeature(
            category="cultural",
            name="admin_1_states_provinces_lines",
            scale="10m",
            facecolor="none",
        )
        ax.add_feature(admin1, linewidth=0.3, alpha=0.65)
        ax.set_extent(
            [
                TAIWAN_BBOX["leftlon"],
                TAIWAN_BBOX["rightlon"],
                TAIWAN_BBOX["bottomlat"],
                TAIWAN_BBOX["toplat"],
            ],
            crs=projection,
        )
        scatter_kwargs = {"transform": projection}
        gridlines = ax.gridlines(
            crs=projection,
            draw_labels=True,
            linewidth=0.35,
            alpha=0.35,
            linestyle="--",
        )
        gridlines.top_labels = False
        gridlines.right_labels = False
    except Exception as exc:
        # Rendering still succeeds if Natural Earth download or Cartopy setup
        # is unavailable. The manifest/log makes the fallback visible.
        print(f"Cartopy geographic context unavailable; using plain axes: {exc}")
        fig, ax = plt.subplots(figsize=(9, 9), constrained_layout=True)
        mesh = ax.pcolormesh(x, y, values, shading="auto", vmin=0, vmax=100)
        ax.set_xlim(TAIWAN_BBOX["leftlon"], TAIWAN_BBOX["rightlon"])
        ax.set_ylim(TAIWAN_BBOX["bottomlat"], TAIWAN_BBOX["toplat"])
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(alpha=0.18)
        scatter_kwargs = {}

    cbar = fig.colorbar(mesh, ax=ax, fraction=0.042, pad=0.025)
    cbar.set_label("Low cloud cover (%)")

    if sampled_spots:
        ax.scatter(
            [s["lon"] for s in sampled_spots],
            [s["lat"] for s in sampled_spots],
            s=9,
            marker="o",
            linewidths=0.2,
            edgecolors="black",
            **scatter_kwargs,
        )

        # Label only a small fixed set in the overview to avoid turning 83
        # Places into unreadable text. All 83 values remain in JSON.
        label_ids = {"tw-019", "tw-034", "tw-035", "tw-036", "tw-077", "tw-082", "tw-083", "tw-084"}
        for spot in sampled_spots:
            if spot["spot_id"] not in label_ids:
                continue
            label = f'{spot["name"]}\n{spot["low_cloud_percent"]:.0f}%'
            kwargs = {"fontsize": 6, "xytext": (4, 4), "textcoords": "offset points"}
            if scatter_kwargs:
                kwargs["transform"] = scatter_kwargs["transform"]
            ax.annotate(
                label,
                xy=(spot["lon"], spot["lat"]),
                **kwargs,
            )

    ax.set_title(title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def write_grid_json(
    grid: dict,
    sampled_spots: list[dict],
    run: GFSRun,
    source_url: str,
    output_path: Path,
) -> None:
    payload = {
        "schema_version": 2,
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
        "bbox": TAIWAN_BBOX,
        "variable": "low_cloud_cover",
        "sampling": "nearest_grid_cell",
        "source_url": source_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **grid,
        "spots": sampled_spots,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_spot_series(
    frames: list[dict],
    spots: list[dict],
    output_path: Path,
) -> None:
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
            by_spot[sampled["spot_id"]]["series"].append(
                {
                    "forecast_hour": run.forecast_hour,
                    "valid_time_utc": run.valid_time_utc.isoformat(),
                    "low_cloud_percent": sampled["low_cloud_percent"],
                    "grid_lat": sampled["grid_lat"],
                    "grid_lon": sampled["grid_lon"],
                    "grid_distance_km": sampled["grid_distance_km"],
                }
            )
    payload = {
        "schema_version": 1,
        "provider": "NOAA/NCEP NOMADS",
        "model": "GFS",
        "variable": "low_cloud_cover",
        "sampling": "nearest_grid_cell",
        "places": list(by_spot.values()),
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_manifest(frames: list[dict], output_path: Path) -> None:
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
        "variable": "low_cloud_cover",
        "bbox": TAIWAN_BBOX,
        "frames": [
            {
                "forecast_hour": item["run"].forecast_hour,
                "valid_time_utc": item["run"].valid_time_utc.isoformat(),
                "grib2": item["grib_path"].name,
                "json": item["json_path"].name,
                "png": item["png_path"].name,
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
    parser.add_argument("--date", help="GFS run date YYYYMMDD")
    parser.add_argument("--cycle", help="GFS cycle: 00, 06, 12 or 18")
    parser.add_argument(
        "--forecast-hours",
        default=",".join(str(x) for x in DEFAULT_FORECAST_HOURS),
        help="comma-separated forecast hours, e.g. 0,3,6,9,12",
    )
    # Backward-compatible single-hour option used by early B113 commands.
    parser.add_argument("--forecast-hour", type=int, default=None)
    parser.add_argument("--output-dir", default="gfs_poc_output")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print candidate NOMADS URLs without downloading",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.date) != bool(args.cycle):
        raise SystemExit("--date and --cycle must be provided together")

    forecast_hours = (
        [validate_forecast_hour(args.forecast_hour)]
        if args.forecast_hour is not None
        else parse_forecast_hours(args.forecast_hours)
    )
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.date and args.cycle:
        base_date = args.date
        base_cycle = validate_cycle(args.cycle)
        candidate_base_runs = [
            GFSRun(base_date, base_cycle, max(forecast_hours))
        ]
    else:
        # Anchor on the furthest requested hour. If that file is published,
        # the earlier forecast frames for the same cycle should also exist.
        candidate_base_runs = candidate_runs(
            forecast_hour=max(forecast_hours),
            count=4,
        )

    if args.dry_run:
        print(json.dumps(
            [
                {
                    "candidate_cycle": {
                        "date": run.date,
                        "cycle": run.cycle,
                    },
                    "urls": [
                        {
                            "forecast_hour": fh,
                            "url": build_nomads_url(GFSRun(run.date, run.cycle, fh)),
                        }
                        for fh in forecast_hours
                    ],
                }
                for run in candidate_base_runs
            ],
            indent=2,
        ))
        return 0

    # First download the furthest forecast frame to choose one fully-published
    # model cycle for the entire series.
    anchor_fh = max(forecast_hours)
    anchor_path = out / f"gfs_tw_low_cloud_f{anchor_fh:03d}.grib2"
    anchor_run, anchor_url = download_grib(candidate_base_runs, anchor_path)
    selected_date, selected_cycle = anchor_run.date, anchor_run.cycle

    spots = active_taiwan_spots()
    frames: list[dict] = []

    for index, fh in enumerate(forecast_hours):
        run = GFSRun(selected_date, selected_cycle, fh)
        grib_path = out / f"gfs_tw_low_cloud_f{fh:03d}.grib2"
        if fh == anchor_fh:
            source_url = anchor_url
        else:
            run, source_url = download_grib(
                [run],
                grib_path,
                retry_wait_seconds=0,
            )
            # Be polite to the public NOMADS filter even though files are tiny.
            if index < len(forecast_hours) - 1:
                time.sleep(1)

        grid = extract_low_cloud(grib_path)
        sampled_spots = sample_spots(grid, spots)
        json_path = out / f"gfs_tw_low_cloud_f{fh:03d}.json"
        png_path = out / f"gfs_tw_low_cloud_f{fh:03d}.png"
        write_grid_json(grid, sampled_spots, run, source_url, json_path)
        render_low_cloud_png(
            grid,
            sampled_spots,
            png_path,
            title=(
                "GFS 0.25° Taiwan low cloud · "
                f"{run.id} · valid {run.valid_time_utc:%Y-%m-%d %H:%MZ}"
            ),
        )
        frames.append(
            {
                "run": run,
                "sampled_spots": sampled_spots,
                "grib_path": grib_path,
                "json_path": json_path,
                "png_path": png_path,
            }
        )

    manifest_path = out / "gfs_tw_low_cloud_manifest.json"
    series_path = out / "gfs_tw_low_cloud_spot_series.json"
    write_manifest(frames, manifest_path)
    write_spot_series(frames, spots, series_path)

    print(json.dumps({
        "cycle": f"{selected_date}T{selected_cycle}Z",
        "forecast_hours": forecast_hours,
        "frames": len(frames),
        "spots": len(spots),
        "manifest": str(manifest_path),
        "spot_series": str(series_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
