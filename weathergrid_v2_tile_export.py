"""Export native WeatherGrid snapshots into browser valid-time tiles."""
from __future__ import annotations
import json
from pathlib import Path

def frame_to_tile(snapshot: dict, frame_index: int = 0) -> dict:
    frames=snapshot.get("frames") or []
    if not frames:
        raise ValueError("snapshot has no frames")
    frame=frames[frame_index]
    grid=snapshot["grid"]
    rows=int(grid["rows"]); cols=int(grid["cols"])
    expected=rows*cols
    values={}
    for name,data in frame["values"].items():
        if len(data)!=expected:
            raise ValueError(f"{name} has {len(data)} values; expected {expected}")
        values[name]=data
    return {
        "schema_version":1,
        "provider":"jma",
        "model":"JMA_MSM",
        "native_grid":True,
        "reference_time_utc":snapshot["reference_time_utc"],
        "valid_time_utc":frame["valid_time_utc"],
        "forecast_hour":frame["forecast_hour"],
        "grid":{"rows":rows,"cols":cols,"latitudes":grid["latitudes"],"longitudes":grid["longitudes"]},
        "values":values,
        "transport":snapshot.get("transport",{}),
    }

def write_frame_tile(snapshot: dict, output: str|Path, frame_index: int=0) -> dict:
    tile=frame_to_tile(snapshot,frame_index)
    p=Path(output); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(tile,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    return tile
