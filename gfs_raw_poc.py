"""ChaseLights GFS raw-data proof of concept.

Downloads a small NOAA/NCEP GFS 0.25° GRIB2 subset for Taiwan, extracts
low-cloud cover, writes a browser-friendly JSON grid, and renders a PNG with
ChaseLights Place coordinates overlaid.

This module is intentionally isolated from production scoring.  It proves the
raw-data ingestion/rendering path before ChaseLights depends on it.

Examples:
    python gfs_raw_poc.py --dry-run
    python gfs_raw_poc.py --forecast-hour 0 --output-dir gfs_poc_output
    python gfs_raw_poc.py --date 20260929 --cycle 00 --forecast-hour 6

Runtime dependencies for a real fetch/render:
    requests cfgrib eccodes xarray numpy matplotlib
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
    # GFS publishes low-cloud cover as LCDC on the low-cloud layer. TCDC is
    # total cloud cover and does not form the requested field/level pair.
    "var_LCDC": "on",
    "lev_low_cloud_layer": "on",
}


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


def candidate_runs(
    now: datetime | None = None,
    forecast_hour: int = 0,
    count: int = 4,
    publication_lag_hours: int = 4,
) -> list[GFSRun]:
    """Return recent likely-published GFS runs, newest first.

    GFS cycles initialize every six hours.  We intentionally lag the current
    clock before selecting a cycle because model products are not available
    instantly at initialization time.
    """
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
            # A valid GRIB2 message starts with GRIB.  NOMADS may return an
            # explanatory HTML/text body with HTTP 200 for an unavailable file.
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

    # GFS cloud cover is percentage, but normalize defensively if a decoder
    # exposes fractions.
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

    # cfgrib normally exposes one-dimensional regular GFS coordinates, but
    # support two-dimensional coordinate arrays to keep the renderer generic.
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


def render_low_cloud_png(grid: dict, spots: list[dict], output_path: Path, title: str) -> None:
    import matplotlib.pyplot as plt

    x, y, values = _mesh_coordinates(grid)
    fig, ax = plt.subplots(figsize=(9, 9), constrained_layout=True)
    mesh = ax.pcolormesh(x, y, values, shading="auto", vmin=0, vmax=100)
    cbar = fig.colorbar(mesh, ax=ax, fraction=0.042, pad=0.025)
    cbar.set_label("Low cloud cover (%)")

    if spots:
        ax.scatter(
            [s["lon"] for s in spots],
            [s["lat"] for s in spots],
            s=10,
            marker="o",
            linewidths=0.25,
            edgecolors="black",
        )

    ax.set_xlim(TAIWAN_BBOX["leftlon"], TAIWAN_BBOX["rightlon"])
    ax.set_ylim(TAIWAN_BBOX["bottomlat"], TAIWAN_BBOX["toplat"])
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(title)
    ax.grid(alpha=0.18)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def write_grid_json(
    grid: dict,
    spots: list[dict],
    run: GFSRun,
    source_url: str,
    output_path: Path,
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
        },
        "bbox": TAIWAN_BBOX,
        "variable": "low_cloud_cover",
        "source_url": source_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **grid,
        "spots": spots,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="GFS run date YYYYMMDD")
    parser.add_argument("--cycle", help="GFS cycle: 00, 06, 12 or 18")
    parser.add_argument("--forecast-hour", type=int, default=0)
    parser.add_argument("--output-dir", default="gfs_poc_output")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print candidate NOMADS URLs without downloading",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fh = validate_forecast_hour(args.forecast_hour)
    if bool(args.date) != bool(args.cycle):
        raise SystemExit("--date and --cycle must be provided together")

    if args.date and args.cycle:
        runs = [GFSRun(args.date, validate_cycle(args.cycle), fh)]
    else:
        runs = candidate_runs(forecast_hour=fh)

    if args.dry_run:
        print(json.dumps(
            [{"run": run.id, "url": build_nomads_url(run)} for run in runs],
            indent=2,
        ))
        return 0

    out = Path(args.output_dir)
    grib_path = out / "gfs_tw_low_cloud.grib2"
    run, source_url = download_grib(runs, grib_path)
    grid = extract_low_cloud(grib_path)
    spots = active_taiwan_spots()

    json_path = out / "gfs_tw_low_cloud.json"
    png_path = out / "gfs_tw_low_cloud.png"
    write_grid_json(grid, spots, run, source_url, json_path)
    render_low_cloud_png(
        grid,
        spots,
        png_path,
        title=f"GFS 0.25° Taiwan low cloud · {run.id}",
    )

    print(json.dumps({
        "run": run.id,
        "grib2": str(grib_path),
        "json": str(json_path),
        "png": str(png_path),
        "spots": len(spots),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
