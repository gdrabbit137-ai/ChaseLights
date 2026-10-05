"""Global GFS cell and antimeridian contract for WeatherGrid V2.

Addressable cells are not published coverage. Runtime/provider manifests must
prove that every required field and valid time for a cell was actually written
before the cell may be advertised as published.
"""
from __future__ import annotations

import math

GLOBAL_WEST = -180.0
GLOBAL_EAST = 180.0
GLOBAL_SOUTH = -90.0
GLOBAL_NORTH = 90.0
DEFAULT_CELL_DEG = 4.0
GFS_CLOUD_FIELDS = (
    "cloud_cover",
    "cloud_cover_low",
    "cloud_cover_mid",
    "cloud_cover_high",
)


def normalize_lon(lon: float) -> float:
    value = ((float(lon) + 180.0) % 360.0) - 180.0
    return 0.0 if value == -0.0 else value


def longitude_segments(west: float, east: float) -> list[tuple[float, float]]:
    """Return non-wrapping [-180, 180] segments for a possibly wrapped bbox."""
    west_raw = float(west)
    east_raw = float(east)
    if abs(east_raw - west_raw) >= 360.0:
        return [(GLOBAL_WEST, GLOBAL_EAST)]

    w = normalize_lon(west_raw)
    e = normalize_lon(east_raw)

    # Preserve +180 as the eastern boundary of an ordinary non-wrapping bbox.
    if east_raw > west_raw and math.isclose(e, GLOBAL_WEST) and east_raw > GLOBAL_WEST:
        e = GLOBAL_EAST

    if w < e:
        return [(w, e)]
    if w > e:
        return [(w, GLOBAL_EAST), (GLOBAL_WEST, e)]
    return []


def nomads_segments(bbox: dict[str, float]) -> list[dict[str, float]]:
    """Convert a wrapped bbox into legal non-wrapping NOMADS rectangles."""
    south = max(GLOBAL_SOUTH, float(bbox["south"]))
    north = min(GLOBAL_NORTH, float(bbox["north"]))
    if south >= north:
        return []
    return [
        {
            "leftlon": west,
            "rightlon": east,
            "bottomlat": south,
            "toplat": north,
        }
        for west, east in longitude_segments(float(bbox["west"]), float(bbox["east"]))
        if west < east
    ]


def _cell_id(x: float, y: float, d: float) -> str:
    ix = int(math.floor((x - GLOBAL_WEST) / d))
    iy = int(math.floor((y - GLOBAL_SOUTH) / d))
    return f"gfs_global_{d:g}_{ix}_{iy}".replace(".", "p")


def cells_for_viewport(
    bbox: dict[str, float],
    *,
    cell_deg: float = DEFAULT_CELL_DEG,
    prefetch_cells: int = 0,
) -> list[dict]:
    """Return deduplicated global cells intersecting viewport plus prefetch ring."""
    d = float(cell_deg)
    if d <= 0 or d > 180:
        raise ValueError("cell_deg must be in (0, 180]")
    if prefetch_cells < 0:
        raise ValueError("prefetch_cells must be >= 0")

    south = max(GLOBAL_SOUTH, float(bbox["south"]) - prefetch_cells * d)
    north = min(GLOBAL_NORTH, float(bbox["north"]) + prefetch_cells * d)
    if south >= north:
        return []

    segments = longitude_segments(
        float(bbox["west"]) - prefetch_cells * d,
        float(bbox["east"]) + prefetch_cells * d,
    )
    out: dict[str, dict] = {}
    for west, east in segments:
        start_x = GLOBAL_WEST + math.floor((west - GLOBAL_WEST) / d) * d
        end_x = GLOBAL_WEST + math.ceil((east - GLOBAL_WEST) / d) * d
        start_y = GLOBAL_SOUTH + math.floor((south - GLOBAL_SOUTH) / d) * d
        end_y = GLOBAL_SOUTH + math.ceil((north - GLOBAL_SOUTH) / d) * d
        y = max(GLOBAL_SOUTH, start_y)
        while y < min(GLOBAL_NORTH, end_y) - 1e-9:
            x = max(GLOBAL_WEST, start_x)
            while x < min(GLOBAL_EAST, end_x) - 1e-9:
                cell = {
                    "id": _cell_id(x, y, d),
                    "bbox": {
                        "west": x,
                        "south": y,
                        "east": min(x + d, GLOBAL_EAST),
                        "north": min(y + d, GLOBAL_NORTH),
                    },
                }
                out[cell["id"]] = cell
                x += d
            y += d
    return [out[key] for key in sorted(out)]


def all_global_cells(*, cell_deg: float = DEFAULT_CELL_DEG) -> list[dict]:
    return cells_for_viewport(
        {
            "west": GLOBAL_WEST,
            "south": GLOBAL_SOUTH,
            "east": GLOBAL_EAST,
            "north": GLOBAL_NORTH,
        },
        cell_deg=cell_deg,
    )


def coverage_complete(required_cell_ids, published_cell_ids) -> bool:
    """Fail closed: addressability never proves publication."""
    required = set(required_cell_ids)
    published = set(published_cell_ids)
    return bool(required) and required.issubset(published)
