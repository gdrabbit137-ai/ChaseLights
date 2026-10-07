"""CWA WRF 3 km provider for ChaseLights WeatherGrid.

This provider uses Central Weather Administration (CWA) open data and keeps the
CWA model independent from ICON and GFS.  Each provider owns its own:

- geographic browser artifact boundary;
- native resolution metadata;
- forecast-hour cadence;
- set of available fields.

CWA's current WRF_D documentation describes the operational model as a 3 km
regional system with 00/06/12/18Z runs and hourly model output to 126 h.  This
provider intentionally integrates the public M-A0064 GRIB2 series, whose public
product IDs run from 000 through 084 at 6-hour steps.  The browser therefore
records both model capability and the cadence/horizon of the public series it
actually publishes.  The public AWS Open Data bucket can be read without an
AWS account.

The browser artifact is intentionally a Taiwan-and-nearby-islands subset of the
larger native regional model domain.  The native model is not represented as a
regular lat/lon grid; we linearly remap the selected native WRF points to a
regular browser grid.  The remap does not create new meteorological resolution.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from gfs_raw_poc import active_taiwan_spots, parse_forecast_hours
from gfs_multilayer_poc import sample_field_bilinear, sample_field_nearest
from cwa_weathergrid_derived import derive_cwa_photography_fields

CWA_BUCKET = "cwaopendata"
CWA_DATASET_PREFIX = "M-A0064"
CWA_NATIVE_RESOLUTION_KM = 3.0
CWA_MODEL_OUTPUT_INTERVAL_HOURS = 1
CWA_MODEL_FORECAST_HORIZON_HOURS = 126
CWA_PUBLIC_FORECAST_INTERVAL_HOURS = 6
CWA_PUBLIC_FORECAST_HORIZON_HOURS = 84
CWA_RUN_HOURS = (0, 6, 12, 18)

# Browser artifact boundary.  This deliberately differs from GFS / ICON and can
# be changed independently without touching those providers.
CWA_TAIWAN_BROWSER_BBOX = {
    "leftlon": 117.5,
    "rightlon": 125.5,
    "bottomlat": 20.0,
    "toplat": 27.0,
}
CWA_BROWSER_GRID_DEG = 0.03
DEFAULT_FORECAST_HOURS = (0, 6, 12, 18, 24)
CWA_PRESSURE_RH_LEVELS_HPA = (1000, 925, 850, 700, 500, 400, 300)

# Official documentation reference corners for the 3 km regional grid.
CWA_NATIVE_DOMAIN_REFERENCE = {
    "first_point": {"lat": 14.02224, "lon": 105.2500},
    "last_point": {"lat": 32.12021, "lon": 140.91388},
    "grid_shape": [673, 1158],
}

CORE_FIELD_SPECS = {
    "temperature_2m_c": {
        "aliases": {"2t", "t2m", "tmp", "temperature"},
        "tokens": ("temperature",),
        "level_tokens": ("heightaboveground",),
        "level_value": 2.0,
        "kind": "temperature",
    },
    "relative_humidity_2m_percent": {
        "aliases": {"2r", "r2", "rh", "r", "relativehumidity"},
        "tokens": ("relative", "humidity"),
        "level_tokens": ("heightaboveground",),
        "level_value": 2.0,
        "kind": "percent",
    },
    "wind_u_10m_m_s": {
        "aliases": {"10u", "u10", "ugrd", "u"},
        "tokens": ("u", "wind"),
        "level_tokens": ("heightaboveground",),
        "level_value": 10.0,
        "kind": "wind",
    },
    "wind_v_10m_m_s": {
        "aliases": {"10v", "v10", "vgrd", "v"},
        "tokens": ("v", "wind"),
        "level_tokens": ("heightaboveground",),
        "level_value": 10.0,
        "kind": "wind",
    },
}

OPTIONAL_FIELD_SPECS = {
    "precip_total_mm": {
        "aliases": {"tp", "apcp", "totalprecipitation"},
        "tokens": ("precipitation",),
        "level_tokens": ("surface",),
        "kind": "precip_total",
    },
    "shortwave_flux_w_m2": {
        "aliases": {"dswrf", "ssrd", "nswrs", "nswrf", "sdswrf", "snswrf"},
        "tokens": ("shortwave",),
        "level_tokens": ("surface",),
        "kind": "shortwave",
    },
}


@dataclass(frozen=True)
class CwaRunMetadata:
    cycle_time_utc: datetime
    forecast_hour: int
    valid_time_utc: datetime


def _norm(value) -> str:
    return str(value or "").lower().replace("_", "").replace(" ", "")


def validate_forecast_hours(hours: Iterable[int]) -> list[int]:
    result = []
    for raw in hours:
        fh = int(raw)
        if fh < 0 or fh > CWA_PUBLIC_FORECAST_HORIZON_HOURS:
            raise ValueError(f"CWA WRF3 forecast hour out of range: {fh}")
        if fh % CWA_PUBLIC_FORECAST_INTERVAL_HOURS:
            raise ValueError(
                f"CWA WRF3 public interval is 6 h; unsupported forecast hour {fh}"
            )
        result.append(fh)
    if not result:
        raise ValueError("forecast-hour list cannot be empty")
    return sorted(dict.fromkeys(result))


def dataset_id(forecast_hour: int) -> str:
    fh = validate_forecast_hours([forecast_hour])[0]
    return f"{CWA_DATASET_PREFIX}-{fh:03d}"


def candidate_s3_keys(forecast_hour: int) -> list[str]:
    data_id = dataset_id(forecast_hour)
    # CWA's historical/public file layout uses MIC/M-A0064-xxx.grb2.
    # Keep Model/ candidates as a compatibility path because the AWS Open Data
    # announcement also documents numerical-model products under Model/.
    return [
        f"MIC/{data_id}.grb2",
        f"MIC/{data_id}.grib2",
        f"Model/{data_id}.grb2",
        f"Model/{data_id}.grib2",
        f"Model/{data_id}/{data_id}.grb2",
        f"Model/{data_id}/{data_id}.grib2",
    ]


def legacy_public_url(forecast_hour: int) -> str:
    data_id = dataset_id(forecast_hour)
    template = os.environ.get(
        "CWA_WRF3_URL_TEMPLATE",
        "https://opendata.cwa.gov.tw/fileapi/opendata/MIC/{data_id}.grb2",
    )
    return template.format(data_id=data_id, forecast_hour=f"{forecast_hour:03d}")


def _download_s3_unsigned(forecast_hour: int, destination: Path) -> str:
    import boto3
    from botocore import UNSIGNED
    from botocore.config import Config
    from botocore.exceptions import ClientError

    client = boto3.client(
        "s3",
        region_name="ap-northeast-1",
        config=Config(signature_version=UNSIGNED),
    )
    errors = []

    for key in candidate_s3_keys(forecast_hour):
        try:
            response = client.get_object(Bucket=CWA_BUCKET, Key=key)
            payload = response["Body"].read()
            if len(payload) >= 16 and payload[:4] == b"GRIB":
                destination.write_bytes(payload)
                return f"s3://{CWA_BUCKET}/{key}"
        except ClientError:
            continue

    # If the bucket layout evolves, keep the provider resilient by listing only
    # the narrow data-id prefix rather than scanning the whole bucket.
    for prefix in (
        f"MIC/{dataset_id(forecast_hour)}",
        f"Model/{dataset_id(forecast_hour)}",
    ):
        try:
            response = client.list_objects_v2(
                Bucket=CWA_BUCKET,
                Prefix=prefix,
                MaxKeys=50,
            )
        except ClientError as exc:
            errors.append(f"S3 list {prefix}: {exc}")
            continue

        for item in response.get("Contents", []):
            key = item["Key"]
            if not key.lower().endswith((".grb2", ".grib2", ".grb")):
                continue
            response = client.get_object(Bucket=CWA_BUCKET, Key=key)
            payload = response["Body"].read()
            if len(payload) >= 16 and payload[:4] == b"GRIB":
                destination.write_bytes(payload)
                return f"s3://{CWA_BUCKET}/{key}"

    raise FileNotFoundError(
        f"No public CWA object found for {dataset_id(forecast_hour)}"
    )


def download_cwa_grib(
    forecast_hour: int,
    destination: Path,
    *,
    timeout: int = 120,
) -> str:
    """Download one CWA WRF3 GRIB file.

    Primary source is the official public AWS Open Data bucket.  A direct CWA
    public file endpoint is retained as a compatibility fallback because CWA
    has historically exposed these same dataset IDs there.
    """
    import requests

    destination.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    try:
        return _download_s3_unsigned(forecast_hour, destination)
    except Exception as exc:
        errors.append(f"S3: {exc}")

    url = legacy_public_url(forecast_hour)
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        payload = response.content
        if len(payload) < 16 or payload[:4] != b"GRIB":
            raise RuntimeError(
                f"response is not GRIB: bytes={len(payload)} "
                f"prefix={payload[:16]!r}"
            )
        destination.write_bytes(payload)
        return url
    except Exception as exc:
        errors.append(f"HTTP: {exc}")

    raise RuntimeError(
        f"Unable to download {dataset_id(forecast_hour)}: " + " | ".join(errors)
    )


def read_grib_run_metadata(path: Path, expected_forecast_hour: int) -> CwaRunMetadata:
    from eccodes import (
        codes_get,
        codes_grib_new_from_file,
        codes_is_defined,
        codes_release,
    )

    with path.open("rb") as handle:
        gid = codes_grib_new_from_file(handle)
        if gid is None:
            raise RuntimeError(f"No GRIB message found in {path}")
        try:
            date = int(codes_get(gid, "dataDate"))
            time_hhmm = int(codes_get(gid, "dataTime"))
            forecast_hour = int(expected_forecast_hour)
            if codes_is_defined(gid, "forecastTime"):
                try:
                    forecast_hour = int(codes_get(gid, "forecastTime"))
                except Exception:
                    forecast_hour = int(expected_forecast_hour)

            cycle = datetime.strptime(
                f"{date:08d}{time_hhmm:04d}",
                "%Y%m%d%H%M",
            ).replace(tzinfo=timezone.utc)

            if codes_is_defined(gid, "validityDate") and codes_is_defined(
                gid, "validityTime"
            ):
                validity_date = int(codes_get(gid, "validityDate"))
                validity_time = int(codes_get(gid, "validityTime"))
                valid = datetime.strptime(
                    f"{validity_date:08d}{validity_time:04d}",
                    "%Y%m%d%H%M",
                ).replace(tzinfo=timezone.utc)
            else:
                from datetime import timedelta

                valid = cycle + timedelta(hours=int(expected_forecast_hour))
        finally:
            codes_release(gid)

    # Some accumulated/averaged GRIB messages can expose forecastTime in units
    # that are not the public dataset lead.  The dataset ID is authoritative for
    # the browser timeline; valid time still comes from GRIB when available.
    return CwaRunMetadata(
        cycle_time_utc=cycle,
        forecast_hour=int(expected_forecast_hour),
        valid_time_utc=valid,
    )


def _coord_values(dataset, names: tuple[str, ...]):
    for name in names:
        if name in dataset.coords:
            return dataset.coords[name].values
    return None


def _array_level_value(array) -> float | None:
    attrs = array.attrs or {}
    for key in ("GRIB_level", "GRIB_scaledValueOfFirstFixedSurface"):
        value = attrs.get(key)
        if value is not None:
            try:
                return float(value)
            except Exception:
                pass
    for coord_name in ("heightAboveGround", "height_above_ground"):
        if coord_name in array.coords:
            try:
                value = array.coords[coord_name].values
                return float(value.item() if hasattr(value, "item") else value)
            except Exception:
                pass
    return None


def _candidate_score(name: str, array, spec: dict) -> int:
    attrs = array.attrs or {}
    short = _norm(attrs.get("GRIB_shortName", name))
    data_name = _norm(name)
    long_name = _norm(attrs.get("long_name") or attrs.get("GRIB_name"))
    level = _norm(attrs.get("GRIB_typeOfLevel"))
    aliases = {_norm(x) for x in spec["aliases"]}

    score = 0
    if short in aliases:
        score += 14
    if data_name in aliases:
        score += 10
    if all(_norm(token) in long_name for token in spec.get("tokens", ())):
        score += 8
    if level in {_norm(x) for x in spec.get("level_tokens", ())}:
        score += 7
    if array.ndim >= 2:
        score += 1

    required_level = spec.get("level_value")
    if required_level is not None:
        actual_level = _array_level_value(array)
        if actual_level is not None:
            if abs(actual_level - float(required_level)) <= 0.01:
                score += 10
            else:
                score -= 12
    return score


def _normalize_values(values, kind: str, units: str):
    import numpy as np

    arr = np.asarray(values, dtype=float)
    units_l = _norm(units)

    if kind == "temperature":
        finite = arr[np.isfinite(arr)]
        if "k" == units_l or (finite.size and float(np.nanmedian(finite)) > 150):
            arr = arr - 273.15
        return arr, "°C"

    if kind == "percent":
        finite = arr[np.isfinite(arr)]
        if finite.size and float(np.nanmax(finite)) <= 1.5:
            arr = arr * 100.0
        return np.clip(arr, 0.0, 100.0), "%"

    if kind == "wind":
        return arr, "m/s"

    if kind == "precip_total":
        if units_l in {"m", "metre", "meter"}:
            arr = arr * 1000.0
        return np.maximum(arr, 0.0), "mm"

    if kind == "shortwave":
        return arr, "W/m²"

    return arr, units or ""


def _extract_one_field(datasets, key: str, spec: dict) -> dict | None:
    import numpy as np

    candidates = []
    for ds in datasets:
        for name, array in ds.data_vars.items():
            score = _candidate_score(name, array, spec)
            candidates.append((score, ds, name, array))
    candidates.sort(key=lambda item: item[0], reverse=True)
    if not candidates or candidates[0][0] < 9:
        return None

    score, ds, name, array = candidates[0]
    values = np.squeeze(np.asarray(array.values, dtype=float))
    if values.ndim != 2:
        return None

    lat = _coord_values(ds, ("latitude", "lat"))
    lon = _coord_values(ds, ("longitude", "lon"))
    if lat is None or lon is None:
        return None

    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    if lat.ndim == 1 and lon.ndim == 1:
        lon2, lat2 = np.meshgrid(lon, lat)
    elif lat.shape == lon.shape:
        lat2, lon2 = lat, lon
    else:
        return None

    if values.shape != lat2.shape:
        if values.T.shape == lat2.shape:
            values = values.T
        else:
            return None

    normalized, normalized_unit = _normalize_values(
        values,
        spec["kind"],
        (array.attrs or {}).get("units", ""),
    )

    return {
        "field_name": name,
        "candidate_score": score,
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
        "latitudes_2d": lat2,
        "longitudes_2d": lon2,
        "values_2d": normalized,
    }


def _pressure_level_view(array, pressure_hpa: int):
    import numpy as np

    for coord_name in ("isobaricInhPa", "isobaricInPa", "pressure", "level"):
        if coord_name not in array.coords:
            continue
        coord = array.coords[coord_name]
        values = np.asarray(coord.values, dtype=float).reshape(-1)
        if not values.size:
            continue
        target = float(pressure_hpa)
        if float(np.nanmedian(np.abs(values))) > 2000.0:
            target *= 100.0
        index = int(np.nanargmin(np.abs(values - target)))
        tolerance = 250.0 if target > 2000.0 else 2.5
        if abs(float(values[index]) - target) > tolerance:
            continue
        if coord_name in array.dims:
            return array.isel({coord_name: index})

    attrs = array.attrs or {}
    level_type = _norm(attrs.get("GRIB_typeOfLevel"))
    level_value = _array_level_value(array)
    if (
        array.ndim == 2
        and level_value is not None
        and level_type in {"isobaricinhpa", "isobaricinpa", "isobaric"}
        and abs(float(level_value) - float(pressure_hpa)) <= 2.5
    ):
        return array
    return None


def _extract_pressure_rh_field(datasets, pressure_hpa: int) -> dict | None:
    import numpy as np

    candidates = []
    for ds in datasets:
        for name, array in ds.data_vars.items():
            view = _pressure_level_view(array, pressure_hpa)
            if view is None:
                continue
            attrs = view.attrs or array.attrs or {}
            short = _norm(attrs.get("GRIB_shortName", name))
            data_name = _norm(name)
            long_name = _norm(attrs.get("long_name") or attrs.get("GRIB_name"))
            score = 0
            if short in {"r", "rh", "relativehumidity"}:
                score += 14
            if data_name in {"r", "rh", "relativehumidity"}:
                score += 10
            if "relative" in long_name and "humidity" in long_name:
                score += 8
            if view.ndim >= 2:
                score += 1
            candidates.append((score, ds, name, view))

    candidates.sort(key=lambda item: item[0], reverse=True)
    if not candidates or candidates[0][0] < 9:
        return None

    score, ds, name, array = candidates[0]
    values = np.squeeze(np.asarray(array.values, dtype=float))
    if values.ndim != 2:
        return None

    lat = _coord_values(ds, ("latitude", "lat"))
    lon = _coord_values(ds, ("longitude", "lon"))
    if lat is None or lon is None:
        return None
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    if lat.ndim == 1 and lon.ndim == 1:
        lon2, lat2 = np.meshgrid(lon, lat)
    elif lat.shape == lon.shape:
        lat2, lon2 = lat, lon
    else:
        return None
    if values.shape != lat2.shape:
        if values.T.shape == lat2.shape:
            values = values.T
        else:
            return None

    normalized, normalized_unit = _normalize_values(
        values,
        "percent",
        (array.attrs or {}).get("units", ""),
    )
    return {
        "field_name": name,
        "candidate_score": score,
        "field_attrs": {
            "short_name": (array.attrs or {}).get("GRIB_shortName"),
            "type_of_level": (array.attrs or {}).get("GRIB_typeOfLevel"),
            "pressure_level_hpa": int(pressure_hpa),
            "long_name": (
                (array.attrs or {}).get("long_name")
                or (array.attrs or {}).get("GRIB_name")
                or f"Relative humidity at {pressure_hpa} hPa"
            ),
            "source_units": (array.attrs or {}).get("units"),
            "normalized_units": normalized_unit,
        },
        "latitudes_2d": lat2,
        "longitudes_2d": lon2,
        "values_2d": normalized,
    }


def extract_native_fields(grib_path: Path) -> dict[str, dict]:
    import cfgrib

    datasets = cfgrib.open_datasets(
        str(grib_path),
        backend_kwargs={"indexpath": ""},
    )
    fields = {}

    for key, spec in CORE_FIELD_SPECS.items():
        field = _extract_one_field(datasets, key, spec)
        if field is None:
            available = sorted({
                (
                    name,
                    (array.attrs or {}).get("GRIB_shortName"),
                    (array.attrs or {}).get("GRIB_typeOfLevel"),
                    (array.attrs or {}).get("GRIB_level"),
                )
                for ds in datasets
                for name, array in ds.data_vars.items()
            })
            raise RuntimeError(
                f"CWA WRF3 required field {key} not found; available={available}"
            )
        fields[key] = field

    for key, spec in OPTIONAL_FIELD_SPECS.items():
        field = _extract_one_field(datasets, key, spec)
        if field is not None:
            fields[key] = field

    for pressure_hpa in CWA_PRESSURE_RH_LEVELS_HPA:
        key = f"relative_humidity_{pressure_hpa}hpa_percent"
        field = _extract_pressure_rh_field(datasets, pressure_hpa)
        if field is None:
            raise RuntimeError(
                f"CWA WRF3 required pressure-level RH field missing: {pressure_hpa} hPa"
            )
        fields[key] = field

    return fields


def build_regrid_context(
    reference_field: dict,
    bbox: dict[str, float],
    *,
    spacing_deg: float = CWA_BROWSER_GRID_DEG,
    halo_deg: float = 0.4,
) -> dict:
    import numpy as np
    from scipy.spatial import Delaunay, cKDTree

    lat = np.asarray(reference_field["latitudes_2d"], dtype=float)
    lon = np.asarray(reference_field["longitudes_2d"], dtype=float)
    finite = np.isfinite(lat) & np.isfinite(lon)

    left = float(bbox["leftlon"])
    right = float(bbox["rightlon"])
    bottom = float(bbox["bottomlat"])
    top = float(bbox["toplat"])
    local = (
        finite
        & (lon >= left - halo_deg)
        & (lon <= right + halo_deg)
        & (lat >= bottom - halo_deg)
        & (lat <= top + halo_deg)
    )
    if int(local.sum()) < 100:
        raise RuntimeError(
            f"CWA native subset too small for interpolation: {int(local.sum())}"
        )

    source_points = np.column_stack([lon[local], lat[local]])
    target_lons = np.arange(left, right + spacing_deg * 0.25, spacing_deg)
    target_lats = np.arange(bottom, top + spacing_deg * 0.25, spacing_deg)
    xx, yy = np.meshgrid(target_lons, target_lats)
    targets = np.column_stack([xx.ravel(), yy.ravel()])

    triangulation = Delaunay(source_points)
    tree = cKDTree(source_points)
    return {
        "local_mask": local,
        "source_points": source_points,
        "triangulation": triangulation,
        "tree": tree,
        "target_lons": target_lons,
        "target_lats": target_lats,
        "target_x": xx,
        "target_y": yy,
        "target_points": targets,
        "spacing_deg": spacing_deg,
    }


def regrid_field(field: dict, context: dict) -> dict:
    import numpy as np
    from scipy.interpolate import LinearNDInterpolator

    values = np.asarray(field["values_2d"], dtype=float)
    local_values = values[context["local_mask"]]
    interpolator = LinearNDInterpolator(
        context["triangulation"],
        local_values,
        fill_value=np.nan,
    )
    target_values = np.asarray(
        interpolator(context["target_points"]),
        dtype=float,
    ).reshape(context["target_x"].shape)

    missing = ~np.isfinite(target_values)
    if missing.any():
        _, nearest_index = context["tree"].query(
            context["target_points"][missing.ravel()],
            k=1,
        )
        flat = target_values.ravel()
        flat[missing.ravel()] = local_values[nearest_index]
        target_values = flat.reshape(target_values.shape)

    return {
        "field_name": field["field_name"],
        "field_attrs": {
            **field["field_attrs"],
            "native_grid": "CWA WRF 3 km regional projected grid",
            "native_resolution_km": CWA_NATIVE_RESOLUTION_KM,
            "spatial_interpolation": "linear_native_to_regular",
            "edge_fill": "nearest",
            "browser_grid_spacing_degrees": context["spacing_deg"],
        },
        "latitudes": context["target_lats"].tolist(),
        "longitudes": context["target_lons"].tolist(),
        "values": target_values.tolist(),
    }


def derive_wind_fields(fields: dict[str, dict]) -> dict[str, dict]:
    import numpy as np

    u = fields["wind_u_10m_m_s"]
    v = fields["wind_v_10m_m_s"]
    ua = np.asarray(u["values"], dtype=float)
    va = np.asarray(v["values"], dtype=float)
    speed = np.sqrt(ua ** 2 + va ** 2)
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
                "long_name": "10 m wind speed derived from CWA WRF U/V",
                "source_units": "m/s",
                "normalized_units": "m/s",
                "native_resolution_km": CWA_NATIVE_RESOLUTION_KM,
                "spatial_interpolation": "linear_native_to_regular",
            },
            "values": speed.tolist(),
        },
        "wind_direction_10m_deg": {
            **base,
            "field_name": "derived_wind_direction_10m",
            "field_attrs": {
                "short_name": "wind_direction_10m",
                "long_name": (
                    "10 m meteorological wind direction derived from CWA WRF U/V"
                ),
                "source_units": "degree",
                "normalized_units": "degree",
                "native_resolution_km": CWA_NATIVE_RESOLUTION_KM,
                "spatial_interpolation": "linear_native_to_regular",
            },
            "values": direction.tolist(),
        },
    }


def sample_places(fields: dict[str, dict], bbox: dict, spots: list[dict]) -> list[dict]:
    result = []
    for spot in spots:
        if not (
            bbox["leftlon"] <= float(spot["lon"]) <= bbox["rightlon"]
            and bbox["bottomlat"] <= float(spot["lat"]) <= bbox["toplat"]
        ):
            continue
        weather = {}
        for key, field in fields.items():
            if key in {"wind_u_10m_m_s", "wind_v_10m_m_s"}:
                continue
            nearest = sample_field_nearest(field, spot["lat"], spot["lon"])
            if key == "wind_direction_10m_deg":
                value = nearest["value"]
            else:
                value = sample_field_bilinear(
                    field, spot["lat"], spot["lon"]
                )
            if isinstance(value, dict):
                value = value["value"]
            weather[key] = {
                "value": round(float(value), 3),
                "nearest": nearest["value"],
                "units": field["field_attrs"].get("normalized_units"),
            }
        result.append({**spot, "weather": weather})
    return result


def write_frame(
    *,
    fields: dict[str, dict],
    run: CwaRunMetadata,
    source: str,
    bbox: dict[str, float],
    spots: list[dict],
    output_path: Path,
) -> None:
    payload = {
        "schema_version": 1,
        "model_id": "cwa_wrf3",
        "provider": "Central Weather Administration (CWA)",
        "model": "CWA_WRF_3KM",
        "native_resolution_km": CWA_NATIVE_RESOLUTION_KM,
        "model_output_interval_hours": CWA_MODEL_OUTPUT_INTERVAL_HOURS,
        "model_forecast_horizon_hours": CWA_MODEL_FORECAST_HORIZON_HOURS,
        "public_product_interval_hours": CWA_PUBLIC_FORECAST_INTERVAL_HOURS,
        "public_product_horizon_hours": CWA_PUBLIC_FORECAST_HORIZON_HOURS,
        "native_domain_reference": CWA_NATIVE_DOMAIN_REFERENCE,
        "browser_grid_spacing_degrees": CWA_BROWSER_GRID_DEG,
        "run": {
            "cycle_time_utc": run.cycle_time_utc.isoformat(),
            "forecast_hour": run.forecast_hour,
            "valid_time_utc": run.valid_time_utc.isoformat(),
        },
        "bbox": bbox,
        "source": source,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "fields": fields,
        "spots": spots,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def write_manifest(
    frames: list[dict],
    *,
    bbox: dict[str, float],
    output_path: Path,
) -> None:
    if not frames:
        raise ValueError("CWA manifest requires frames")
    cycle = frames[0]["run"].cycle_time_utc
    payload = {
        "schema_version": 1,
        "model_id": "cwa_wrf3",
        "provider": "Central Weather Administration (CWA)",
        "model": "CWA_WRF_3KM",
        "cycle": {
            "cycle_time_utc": cycle.isoformat(),
            "date": cycle.strftime("%Y%m%d"),
            "cycle": cycle.strftime("%H"),
        },
        "bbox": bbox,
        "native_resolution_km": CWA_NATIVE_RESOLUTION_KM,
        "model_output_interval_hours": CWA_MODEL_OUTPUT_INTERVAL_HOURS,
        "model_forecast_horizon_hours": CWA_MODEL_FORECAST_HORIZON_HOURS,
        "public_product_interval_hours": CWA_PUBLIC_FORECAST_INTERVAL_HOURS,
        "public_product_horizon_hours": CWA_PUBLIC_FORECAST_HORIZON_HOURS,
        "native_domain_reference": CWA_NATIVE_DOMAIN_REFERENCE,
        "browser_grid_spacing_degrees": CWA_BROWSER_GRID_DEG,
        "frames": [
            {
                "forecast_hour": item["run"].forecast_hour,
                "valid_time_utc": item["run"].valid_time_utc.isoformat(),
                "json": item["json_path"].name,
                "source": item["source"],
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
    parser.add_argument("--output-dir", default="cwa_wrf3_output")
    parser.add_argument(
        "--browser-grid-deg",
        type=float,
        default=CWA_BROWSER_GRID_DEG,
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hours = validate_forecast_hours(parse_forecast_hours(args.forecast_hours))
    bbox = dict(CWA_TAIWAN_BROWSER_BBOX)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(json.dumps({
            "model_id": "cwa_wrf3",
            "provider": "CWA",
            "forecast_hours": hours,
            "dataset_ids": [dataset_id(fh) for fh in hours],
            "candidate_s3_keys": {
                str(fh): candidate_s3_keys(fh) for fh in hours
            },
            "http_fallbacks": {
                str(fh): legacy_public_url(fh) for fh in hours
            },
            "bbox": bbox,
            "native_resolution_km": CWA_NATIVE_RESOLUTION_KM,
            "model_output_interval_hours": CWA_MODEL_OUTPUT_INTERVAL_HOURS,
            "model_forecast_horizon_hours": CWA_MODEL_FORECAST_HORIZON_HOURS,
            "public_product_interval_hours": CWA_PUBLIC_FORECAST_INTERVAL_HOURS,
            "public_product_horizon_hours": CWA_PUBLIC_FORECAST_HORIZON_HOURS,
        }, indent=2))
        return 0

    frames = []
    expected_cycle = None
    regrid_context = None
    spots = active_taiwan_spots()

    for frame_index, fh in enumerate(hours):
        grib_path = out / f"cwa_wrf3_f{fh:03d}.grb2"
        source = download_cwa_grib(fh, grib_path)
        run = read_grib_run_metadata(grib_path, fh)

        if expected_cycle is None:
            expected_cycle = run.cycle_time_utc
        elif run.cycle_time_utc != expected_cycle:
            raise RuntimeError(
                "CWA files crossed a model-cycle update during refresh: "
                f"expected {expected_cycle.isoformat()}, got "
                f"{run.cycle_time_utc.isoformat()} for f{fh:03d}"
            )

        native_fields = extract_native_fields(grib_path)
        reference = native_fields["temperature_2m_c"]
        if regrid_context is None:
            regrid_context = build_regrid_context(
                reference,
                bbox,
                spacing_deg=float(args.browser_grid_deg),
            )

        regular_fields = {
            key: regrid_field(field, regrid_context)
            for key, field in native_fields.items()
        }
        regular_fields.update(derive_wind_fields(regular_fields))
        regular_fields.update(derive_cwa_photography_fields(regular_fields))

        sampled = sample_places(regular_fields, bbox, spots)
        frame_path = out / f"cwa_wrf3_tw_f{fh:03d}.json"
        write_frame(
            fields=regular_fields,
            run=run,
            source=source,
            bbox=bbox,
            spots=sampled,
            output_path=frame_path,
        )
        frames.append({
            "run": run,
            "source": source,
            "json_path": frame_path,
        })

    manifest_path = out / "cwa_wrf3_tw_weather_manifest.json"
    write_manifest(frames, bbox=bbox, output_path=manifest_path)

    print(json.dumps({
        "model_id": "cwa_wrf3",
        "cycle_time_utc": expected_cycle.isoformat() if expected_cycle else None,
        "forecast_hours": hours,
        "frames": len(frames),
        "bbox": bbox,
        "browser_grid_spacing_degrees": float(args.browser_grid_deg),
        "manifest": str(manifest_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
