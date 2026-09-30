"""ICON Global cloud provider for ChaseLights WeatherGrid.

The provider downloads DWD's native ICON Global icosahedral cloud fields and
uses DWD's official 0.125 degree CDO remapping weights to produce a compact
regular latitude/longitude regional WeatherGrid. The remapped grid remains
traceable to the approximately 13 km native model. Browser-side bilinear
interpolation is presentation-only and does not claim extra forecast detail.

The first publisher remains Taiwan-scoped. The provider itself uses the global
ICON model and is structured so later batches can emit additional regional
tiles without changing the browser field contract.
"""

from __future__ import annotations

import argparse
import bz2
import json
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

from gfs_raw_poc import TAIWAN_BBOX, active_taiwan_spots, parse_forecast_hours
from gfs_multilayer_poc import sample_field_bilinear, sample_field_nearest
from weathergrid_model_resolver import (
    CloudModelRun,
    candidate_icon_cycles,
    icon_forecast_hour_is_published,
    icon_horizon_hours,
)

DWD_ICON_BASE = "https://opendata.dwd.de/weather/nwp/icon/grib"
DWD_CDO_PACKAGE_URL = (
    "https://opendata.dwd.de/weather/lib/cdo/"
    "ICON_GLOBAL2WORLD_0125_EASY.tar.bz2"
)
ICON_NATIVE_RESOLUTION_KM = 13.0
ICON_REMAP_GRID_DEG = 0.125
DEFAULT_FORECAST_HOURS = (0, 3, 6, 9, 12)

ICON_CLOUD_FIELDS = {
    "low_cloud_percent": ("clcl", "CLCL"),
    "mid_cloud_percent": ("clcm", "CLCM"),
    "high_cloud_percent": ("clch", "CLCH"),
}


def validate_icon_cycle(value: str) -> str:
    value = str(value).zfill(2)
    if value not in {"00", "06", "12", "18"}:
        raise ValueError(f"ICON cycle must be one of 00/06/12/18, got {value}")
    return value


def icon_run(cycle_time_utc: datetime, forecast_hour: int) -> CloudModelRun:
    cycle = cycle_time_utc.astimezone(timezone.utc)
    fh = int(forecast_hour)
    if fh < 0 or fh > icon_horizon_hours(cycle.hour):
        raise ValueError(
            f"ICON {cycle:%HZ} forecast hour {fh} exceeds "
            f"{icon_horizon_hours(cycle.hour)} h horizon"
        )
    if not icon_forecast_hour_is_published(fh):
        raise ValueError(f"ICON forecast hour {fh} is not on the published schedule")
    return CloudModelRun(
        provider="DWD Open Data",
        model="ICON_GLOBAL",
        cycle_time_utc=cycle,
        forecast_hour=fh,
        native_resolution_km=ICON_NATIVE_RESOLUTION_KM,
        native_grid="icosahedral_R03B07",
    )


def candidate_runs_for_forecast_hour(
    forecast_hour: int,
    *,
    now: datetime | None = None,
    publication_lag_hours: int = 4,
    count: int = 8,
) -> list[CloudModelRun]:
    runs = []
    for cycle in candidate_icon_cycles(
        now,
        publication_lag_hours=publication_lag_hours,
        count=count,
    ):
        try:
            runs.append(icon_run(cycle, forecast_hour))
        except ValueError:
            continue
    return runs


def build_icon_url(
    run: CloudModelRun,
    variable_dir: str,
    variable_code: str,
) -> str:
    stamp = run.cycle_time_utc.strftime("%Y%m%d%H")
    return (
        f"{DWD_ICON_BASE}/{run.cycle}/{variable_dir}/"
        f"icon_global_icosahedral_single-level_{stamp}_"
        f"{run.forecast_hour:03d}_{variable_code}.grib2.bz2"
    )


def download_icon_field(
    runs: list[CloudModelRun],
    *,
    variable_dir: str,
    variable_code: str,
    destination: Path,
    timeout: int = 120,
    retry_wait_seconds: float = 2.0,
) -> tuple[CloudModelRun, str]:
    """Download and decompress the first available candidate ICON field."""
    import requests

    destination.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for index, run in enumerate(runs):
        url = build_icon_url(run, variable_dir, variable_code)
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            compressed = response.content
            if len(compressed) < 16:
                raise RuntimeError(
                    f"compressed payload too small: {len(compressed)} bytes"
                )
            payload = bz2.decompress(compressed)
            if len(payload) < 16 or payload[:4] != b"GRIB":
                raise RuntimeError(
                    f"decompressed response is not GRIB2: "
                    f"bytes={len(payload)} prefix={payload[:16]!r}"
                )
            destination.write_bytes(payload)
            return run, url
        except Exception as exc:
            errors.append(
                f"{run.date}T{run.cycle}Z_f{run.forecast_hour:03d}: {exc}"
            )
            if index < len(runs) - 1:
                time.sleep(retry_wait_seconds)
    raise RuntimeError("No candidate ICON field downloaded: " + " | ".join(errors))


def _safe_extract_tar(archive: Path, destination: Path) -> None:
    destination = destination.resolve()
    with tarfile.open(archive, mode="r:bz2") as tar:
        for member in tar.getmembers():
            target = (destination / member.name).resolve()
            if destination not in target.parents and target != destination:
                raise RuntimeError(f"unsafe path in DWD CDO archive: {member.name}")
        tar.extractall(destination)


def prepare_cdo_weights(
    cache_dir: Path,
    *,
    timeout: int = 180,
) -> tuple[Path, Path]:
    """Ensure DWD's official ICON Global 0.125 degree remap files are present."""
    import requests

    cache_dir.mkdir(parents=True, exist_ok=True)
    target_name = "target_grid_world_0125.txt"
    weights_name = "weights_icogl2world_0125.nc"

    existing_target = next(cache_dir.rglob(target_name), None)
    existing_weights = next(cache_dir.rglob(weights_name), None)
    if existing_target and existing_weights:
        return existing_target, existing_weights

    archive = cache_dir / "ICON_GLOBAL2WORLD_0125_EASY.tar.bz2"
    if not archive.exists():
        response = requests.get(DWD_CDO_PACKAGE_URL, timeout=timeout)
        response.raise_for_status()
        archive.write_bytes(response.content)

    _safe_extract_tar(archive, cache_dir)
    target = next(cache_dir.rglob(target_name), None)
    weights = next(cache_dir.rglob(weights_name), None)
    if target is None or weights is None:
        raise RuntimeError(
            "DWD CDO archive did not contain the expected 0.125 degree files"
        )
    return target, weights


def build_cdo_command(
    *,
    input_grib: Path,
    output_netcdf: Path,
    target_grid: Path,
    weights: Path,
    bbox: dict[str, float],
) -> list[str]:
    left = float(bbox["leftlon"])
    right = float(bbox["rightlon"])
    bottom = float(bbox["bottomlat"])
    top = float(bbox["toplat"])
    if not (left < right and bottom < top):
        raise ValueError(f"invalid bbox: {bbox}")
    box = f"{left},{right},{bottom},{top}"
    remap = f"{target_grid},{weights}"
    return [
        "cdo",
        "-O",
        "-f",
        "nc4",
        f"-sellonlatbox,{box}",
        f"-remap,{remap}",
        str(input_grib),
        str(output_netcdf),
    ]


def remap_icon_field(
    *,
    input_grib: Path,
    output_netcdf: Path,
    target_grid: Path,
    weights: Path,
    bbox: dict[str, float],
) -> None:
    """Run DWD's documented native triangular -> 0.125 degree remap."""
    command = build_cdo_command(
        input_grib=input_grib,
        output_netcdf=output_netcdf,
        target_grid=target_grid,
        weights=weights,
        bbox=bbox,
    )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or not output_netcdf.exists():
        raise RuntimeError(
            "CDO ICON remap failed: "
            f"returncode={completed.returncode}; stderr={completed.stderr[-2000:]}"
        )


def _coord_values(dataset, names: tuple[str, ...]):
    for name in names:
        if name in dataset.coords:
            return name, dataset.coords[name].values
    return None, None


def decode_remapped_cloud(netcdf_path: Path) -> dict:
    """Decode one regional regular-grid cloud field from the CDO output."""
    import numpy as np
    import xarray as xr

    with xr.open_dataset(netcdf_path) as dataset:
        lat_name, lat = _coord_values(dataset, ("lat", "latitude"))
        lon_name, lon = _coord_values(dataset, ("lon", "longitude"))
        if lat is None or lon is None:
            raise RuntimeError("remapped ICON file has no latitude/longitude axes")

        candidates = []
        for name, array in dataset.data_vars.items():
            dims = set(array.dims)
            score = int(lat_name in dims) + int(lon_name in dims)
            if score == 2:
                candidates.append((array.size, name, array))
        if not candidates:
            raise RuntimeError("remapped ICON file has no 2-D lat/lon data field")

        _, name, array = max(candidates, key=lambda item: item[0])
        values = np.squeeze(np.asarray(array.values, dtype=float))
        lat = np.asarray(lat, dtype=float)
        lon = np.asarray(lon, dtype=float)
        if values.ndim != 2:
            raise RuntimeError(
                f"remapped ICON cloud field expected 2-D data, got {values.shape}"
            )

        # Normalize to rows=latitude and cols=longitude.
        dims = [dim for dim in array.squeeze().dims]
        if dims == [lon_name, lat_name]:
            values = values.T
        elif dims != [lat_name, lon_name]:
            raise RuntimeError(
                f"unexpected remapped ICON dimension order: {dims}"
            )

        finite = values[np.isfinite(values)]
        if finite.size and float(np.nanmax(finite)) <= 1.5:
            values = values * 100.0
        values = np.clip(values, 0.0, 100.0)

        if lat[0] > lat[-1]:
            lat = lat[::-1]
            values = values[::-1, :]
        if lon[0] > lon[-1]:
            lon = lon[::-1]
            values = values[:, ::-1]

        attrs = dict(array.attrs)

    return {
        "field_name": name,
        "field_attrs": {
            "short_name": attrs.get("short_name", name),
            "source_units": attrs.get("units", ""),
            "normalized_units": "%",
            "native_grid": "ICON Global R03B07 icosahedral",
            "native_resolution_km": ICON_NATIVE_RESOLUTION_KM,
            "remap_grid_spacing_degrees": ICON_REMAP_GRID_DEG,
            "spatial_interpolation": "DWD_CDO_precomputed_weights",
            "browser_interpolation": "bilinear_subcell",
        },
        "latitudes": lat.tolist(),
        "longitudes": lon.tolist(),
        "values": values.tolist(),
    }


def sample_places(fields: dict[str, dict], spots: list[dict]) -> list[dict]:
    sampled = []
    for spot in spots:
        weather = {}
        reference = sample_field_nearest(
            fields["low_cloud_percent"],
            spot["lat"],
            spot["lon"],
        )
        for key, field in fields.items():
            nearest = sample_field_nearest(field, spot["lat"], spot["lon"])
            bilinear = sample_field_bilinear(field, spot["lat"], spot["lon"])
            weather[key] = {
                "value": round(float(bilinear), 3),
                "nearest": nearest["value"],
                "delta": round(float(bilinear) - nearest["value"], 3),
                "units": "%",
            }
        sampled.append({
            **spot,
            "weather": weather,
            "grid_reference": {
                key: reference[key]
                for key in (
                    "grid_lat",
                    "grid_lon",
                    "grid_distance_km",
                    "grid_row",
                    "grid_col",
                )
            },
        })
    return sampled


def write_frame(
    *,
    fields: dict[str, dict],
    spots: list[dict],
    run: CloudModelRun,
    source_urls: dict[str, str],
    bbox: dict[str, float],
    output_path: Path,
) -> None:
    payload = {
        "schema_version": 1,
        "provider": "DWD Open Data",
        "model": "ICON_GLOBAL",
        "native_grid": "R03B07 icosahedral",
        "native_resolution_km": ICON_NATIVE_RESOLUTION_KM,
        "remap_grid_spacing_degrees": ICON_REMAP_GRID_DEG,
        "spatial_interpolation": {
            "native_to_regular": "DWD CDO 0.125 degree precomputed weights",
            "browser_display": "bilinear subcell",
            "note": (
                "Interpolation smooths the model field for display. "
                "It does not increase forecast resolution."
            ),
        },
        "run": {
            "date": run.date,
            "cycle": run.cycle,
            "forecast_hour": run.forecast_hour,
            "cycle_time_utc": run.cycle_time_utc.isoformat(),
            "valid_time_utc": run.valid_time_utc.isoformat(),
        },
        "bbox": bbox,
        "source_urls": source_urls,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fields": fields,
        "spots": spots,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_manifest(
    *,
    frames: list[dict],
    bbox: dict[str, float],
    output_path: Path,
) -> None:
    first = frames[0]["run"]
    payload = {
        "schema_version": 1,
        "provider": "DWD Open Data",
        "model": "ICON_GLOBAL",
        "native_grid": "R03B07 icosahedral",
        "native_resolution_km": ICON_NATIVE_RESOLUTION_KM,
        "remap_grid_spacing_degrees": ICON_REMAP_GRID_DEG,
        "cycle": {
            "date": first.date,
            "cycle": first.cycle,
            "cycle_time_utc": first.cycle_time_utc.isoformat(),
        },
        "bbox": bbox,
        "variables": list(ICON_CLOUD_FIELDS),
        "frames": [
            {
                "forecast_hour": item["run"].forecast_hour,
                "valid_time_utc": item["run"].valid_time_utc.isoformat(),
                "json": item["json_path"].name,
            }
            for item in frames
        ],
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _explicit_cycle(date: str, cycle: str) -> datetime:
    cycle = validate_icon_cycle(cycle)
    return datetime.strptime(
        f"{date}{cycle}",
        "%Y%m%d%H",
    ).replace(tzinfo=timezone.utc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="ICON run date YYYYMMDD")
    parser.add_argument("--cycle", help="ICON cycle: 00, 06, 12 or 18")
    parser.add_argument(
        "--forecast-hours",
        default=",".join(str(x) for x in DEFAULT_FORECAST_HOURS),
    )
    parser.add_argument("--output-dir", default="icon_cloud_output")
    parser.add_argument(
        "--cdo-cache-dir",
        default=".cache/dwd-icon-cdo",
        help="Cache directory for DWD's stable CDO remapping package.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.date) != bool(args.cycle):
        raise SystemExit("--date and --cycle must be provided together")

    forecast_hours = parse_forecast_hours(args.forecast_hours)
    max_fh = max(forecast_hours)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    bbox = dict(TAIWAN_BBOX)

    if args.date:
        cycle_time = _explicit_cycle(args.date, args.cycle)
        candidates = [icon_run(cycle_time, max_fh)]
    else:
        candidates = candidate_runs_for_forecast_hour(max_fh)
    if not candidates:
        raise SystemExit(f"No ICON cycle can provide forecast hour {max_fh}")

    if args.dry_run:
        print(json.dumps([
            {
                "candidate_cycle": candidate.cycle_time_utc.isoformat(),
                "forecast_hours": {
                    str(fh): {
                        key: build_icon_url(
                            icon_run(candidate.cycle_time_utc, fh),
                            variable_dir,
                            variable_code,
                        )
                        for key, (variable_dir, variable_code)
                        in ICON_CLOUD_FIELDS.items()
                    }
                    for fh in forecast_hours
                    if fh <= icon_horizon_hours(candidate.cycle_time_utc.hour)
                    and icon_forecast_hour_is_published(fh)
                },
            }
            for candidate in candidates
        ], indent=2))
        return 0

    target_grid, weights = prepare_cdo_weights(Path(args.cdo_cache_dir))

    # Probe the furthest low-cloud file first, then keep one model cycle for
    # every field/frame in this browser series.
    anchor_grib = out / f"icon_tw_clcl_f{max_fh:03d}.grib2"
    anchor_run, anchor_url = download_icon_field(
        candidates,
        variable_dir=ICON_CLOUD_FIELDS["low_cloud_percent"][0],
        variable_code=ICON_CLOUD_FIELDS["low_cloud_percent"][1],
        destination=anchor_grib,
    )
    selected_cycle = anchor_run.cycle_time_utc
    spots = active_taiwan_spots()
    frames = []

    for frame_index, fh in enumerate(forecast_hours):
        run = icon_run(selected_cycle, fh)
        fields = {}
        source_urls = {}

        for field_index, (key, (variable_dir, variable_code)) in enumerate(
            ICON_CLOUD_FIELDS.items()
        ):
            grib_path = out / f"icon_tw_{variable_dir}_f{fh:03d}.grib2"
            if fh == max_fh and key == "low_cloud_percent":
                if grib_path != anchor_grib:
                    grib_path.write_bytes(anchor_grib.read_bytes())
                source_url = anchor_url
            else:
                _, source_url = download_icon_field(
                    [run],
                    variable_dir=variable_dir,
                    variable_code=variable_code,
                    destination=grib_path,
                    retry_wait_seconds=0,
                )

            netcdf_path = out / f"icon_tw_{variable_dir}_f{fh:03d}.nc"
            remap_icon_field(
                input_grib=grib_path,
                output_netcdf=netcdf_path,
                target_grid=target_grid,
                weights=weights,
                bbox=bbox,
            )
            fields[key] = decode_remapped_cloud(netcdf_path)
            source_urls[key] = source_url

            if field_index < len(ICON_CLOUD_FIELDS) - 1:
                time.sleep(0.15)

        sampled = sample_places(fields, spots)
        frame_path = out / f"icon_tw_cloud_f{fh:03d}.json"
        write_frame(
            fields=fields,
            spots=sampled,
            run=run,
            source_urls=source_urls,
            bbox=bbox,
            output_path=frame_path,
        )
        frames.append({"run": run, "json_path": frame_path})

        if frame_index < len(forecast_hours) - 1:
            time.sleep(0.35)

    manifest_path = out / "icon_tw_cloud_manifest.json"
    write_manifest(frames=frames, bbox=bbox, output_path=manifest_path)

    print(json.dumps({
        "provider": "DWD Open Data",
        "model": "ICON_GLOBAL",
        "cycle": selected_cycle.isoformat(),
        "forecast_hours": forecast_hours,
        "native_resolution_km": ICON_NATIVE_RESOLUTION_KM,
        "remap_grid_spacing_degrees": ICON_REMAP_GRID_DEG,
        "frames": len(frames),
        "spots": len(spots),
        "manifest": str(manifest_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
