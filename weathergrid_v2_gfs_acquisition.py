"""Efficient NOAA GFS global-cloud acquisition for WeatherGrid V2.

The NOAA Open Data S3 object contains a full global GRIB2 file plus a small
wgrib-style .idx sidecar. We use the index to range-fetch only the four cloud
messages needed by WeatherGrid V2, then concatenate those complete GRIB2
messages into one small decode input. This avoids thousands of per-tile NOMADS
requests and avoids downloading the full ~hundreds-of-MB forecast file.

This module is V2-only and does not publish coverage by itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from gfs_raw_poc import GFSRun
from weathergrid_v2_gfs_global import GFS_CLOUD_FIELDS

AWS_GFS_BASE = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
GFS_GRIB_VARS = {
    "cloud_cover": "TCDC",
    "cloud_cover_low": "LCDC",
    "cloud_cover_mid": "MCDC",
    "cloud_cover_high": "HCDC",
}
GFS_LEVEL_MATCH = {
    "cloud_cover": ("entire atmosphere",),
    "cloud_cover_low": ("low cloud layer",),
    "cloud_cover_mid": ("middle cloud layer",),
    "cloud_cover_high": ("high cloud layer",),
}


@dataclass(frozen=True)
class IndexRecord:
    message: int
    offset: int
    end: int | None
    date_token: str
    variable: str
    level: str
    descriptor: str

    @property
    def range_header(self) -> str:
        if self.end is None:
            return f"bytes={self.offset}-"
        return f"bytes={self.offset}-{self.end}"


def aws_grib_url(run: GFSRun) -> str:
    return (
        f"{AWS_GFS_BASE}/gfs.{run.date}/{run.cycle}/atmos/"
        f"{run.filename}"
    )


def aws_idx_url(run: GFSRun) -> str:
    return aws_grib_url(run) + ".idx"


def parse_gfs_idx(text: str, *, file_size: int | None = None) -> list[IndexRecord]:
    """Parse NOAA wgrib-style index and derive inclusive byte ranges."""
    raw = []
    for line in str(text).splitlines():
        if not line.strip():
            continue
        parts = line.rstrip("\n").split(":")
        if len(parts) < 6:
            raise ValueError(f"invalid GFS idx line: {line!r}")
        try:
            message = int(parts[0])
            offset = int(parts[1])
        except ValueError as exc:
            raise ValueError(f"invalid GFS idx offset: {line!r}") from exc
        raw.append(
            {
                "message": message,
                "offset": offset,
                "date_token": parts[2],
                "variable": parts[3].strip(),
                "level": parts[4].strip(),
                "descriptor": ":".join(parts[5:]).strip(),
            }
        )

    if not raw:
        raise ValueError("GFS idx is empty")
    for i in range(1, len(raw)):
        if raw[i]["offset"] <= raw[i - 1]["offset"]:
            raise ValueError("GFS idx offsets must be strictly increasing")

    records = []
    for i, item in enumerate(raw):
        if i + 1 < len(raw):
            end = raw[i + 1]["offset"] - 1
        elif file_size is not None:
            if int(file_size) <= item["offset"]:
                raise ValueError("file_size does not contain final GFS idx record")
            end = int(file_size) - 1
        else:
            end = None
        records.append(IndexRecord(end=end, **item))
    return records


def _norm(value: str) -> str:
    return " ".join(str(value).lower().replace("_", " ").split())


def select_cloud_records(records: Iterable[IndexRecord]) -> dict[str, IndexRecord]:
    """Select exactly one preferred GFS record for each browser cloud field."""
    rows = list(records)
    selected = {}
    for field in GFS_CLOUD_FIELDS:
        var = GFS_GRIB_VARS[field]
        levels = tuple(_norm(x) for x in GFS_LEVEL_MATCH[field])
        candidates = [
            row
            for row in rows
            if row.variable.upper() == var
            and any(level in _norm(row.level) for level in levels)
        ]
        if not candidates:
            raise KeyError(f"missing required GFS cloud record {field} ({var})")
        # Stable fail-closed choice. Duplicate exact field/level records are
        # ambiguous for the V2 contract and must not be silently guessed.
        exact = [
            row for row in candidates
            if _norm(row.level) in levels
        ]
        choice_pool = exact or candidates
        if len(choice_pool) != 1:
            details = [f"{r.message}:{r.variable}:{r.level}:{r.descriptor}" for r in choice_pool]
            raise ValueError(f"ambiguous GFS cloud record {field}: {details}")
        selected[field] = choice_pool[0]
    return selected


def fetch_cloud_subset(
    run: GFSRun,
    destination: str | Path,
    *,
    session=None,
    timeout: int = 90,
) -> dict:
    """Range-fetch the four required global cloud GRIB messages from NOAA S3."""
    if session is None:
        import requests
        session = requests.Session()

    grib_url = aws_grib_url(run)
    idx_url = aws_idx_url(run)
    idx_response = session.get(idx_url, timeout=timeout)
    idx_response.raise_for_status()

    records = parse_gfs_idx(idx_response.text)
    selected = select_cloud_records(records)
    if any(record.end is None for record in selected.values()):
        head = session.head(grib_url, timeout=timeout)
        head.raise_for_status()
        size = int(head.headers["Content-Length"])
        records = parse_gfs_idx(idx_response.text, file_size=size)
        selected = select_cloud_records(records)

    parts = []
    transfer = []
    for field in GFS_CLOUD_FIELDS:
        record = selected[field]
        response = session.get(
            grib_url,
            headers={"Range": record.range_header},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.content
        if len(payload) < 16 or payload[:4] != b"GRIB":
            raise RuntimeError(
                f"{field} range is not a complete GRIB2 message "
                f"({record.range_header}, bytes={len(payload)})"
            )
        parts.append(payload)
        transfer.append(
            {
                "field": field,
                "variable": record.variable,
                "level": record.level,
                "message": record.message,
                "byte_range": record.range_header,
                "bytes": len(payload),
            }
        )

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(parts))
    return {
        "provider": "NOAA/NCEP",
        "model": "GFS_GLOBAL_0P25",
        "reference_time_utc": run.cycle_time_utc.isoformat().replace("+00:00", "Z"),
        "valid_time_utc": run.valid_time_utc.isoformat().replace("+00:00", "Z"),
        "forecast_hour": run.forecast_hour,
        "grib_url": grib_url,
        "idx_url": idx_url,
        "fields": list(GFS_CLOUD_FIELDS),
        "messages": transfer,
        "subset_bytes": sum(item["bytes"] for item in transfer),
        "path": str(path),
    }


def _coord_values(dataset, names: tuple[str, ...]):
    for name in names:
        if name in dataset.coords:
            return dataset.coords[name].values
    return None


def _token(value) -> str:
    return str(value or "").lower().replace("_", "").replace(" ", "")


def decode_cloud_subset(path: str | Path) -> dict[str, dict]:
    """Decode the four cloud messages into normalized browser field arrays."""
    import cfgrib
    import numpy as np

    datasets = cfgrib.open_datasets(str(path), backend_kwargs={"indexpath": ""})
    decoded = {}
    for field in GFS_CLOUD_FIELDS:
        var = _token(GFS_GRIB_VARS[field])
        level_tokens = {_token(x) for x in GFS_LEVEL_MATCH[field]}
        candidates = []
        for ds in datasets:
            for name, array in ds.data_vars.items():
                attrs = array.attrs or {}
                short = _token(attrs.get("GRIB_shortName", name))
                level = _token(attrs.get("GRIB_typeOfLevel", ""))
                long_name = _token(attrs.get("long_name", attrs.get("GRIB_name", "")))
                score = 0
                if short == var:
                    score += 10
                if any(token in level for token in level_tokens):
                    score += 8
                if field == "cloud_cover" and "totalcloud" in long_name:
                    score += 3
                if array.ndim >= 2:
                    score += 1
                candidates.append((score, ds, name, array))
        candidates.sort(key=lambda item: item[0], reverse=True)
        if not candidates or candidates[0][0] < 11:
            raise RuntimeError(f"could not decode required GFS field {field}")
        score, ds, name, array = candidates[0]
        values = np.squeeze(np.asarray(array.values, dtype=float))
        if values.ndim != 2:
            raise RuntimeError(f"{field} expected 2-D grid, got {values.shape}")
        finite = values[np.isfinite(values)]
        if finite.size and float(np.nanmax(finite)) <= 1.5:
            values = values * 100.0
        values = np.clip(values, 0.0, 100.0)
        lat = _coord_values(ds, ("latitude", "lat"))
        lon = _coord_values(ds, ("longitude", "lon"))
        if lat is None or lon is None:
            raise RuntimeError(f"{field} missing latitude/longitude coordinates")
        decoded[field] = {
            "field_name": name,
            "source_variable": GFS_GRIB_VARS[field],
            "normalized_units": "%",
            "latitudes": np.asarray(lat, dtype=float).tolist(),
            "longitudes": np.asarray(lon, dtype=float).tolist(),
            "values": values.tolist(),
        }

    if set(decoded) != set(GFS_CLOUD_FIELDS):
        raise RuntimeError("decoded GFS cloud subset is incomplete")
    return decoded
