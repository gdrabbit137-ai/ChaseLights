"""Global tile addressing contract for WeatherGrid V2 GFS cloud layers.

V2-only: addressable cells are not published coverage. Runtime manifests must
prove the requested cells and valid time exist before coverage is complete.
"""
from __future__ import annotations
import math

GLOBAL_WEST, GLOBAL_EAST = -180.0, 180.0
GLOBAL_SOUTH, GLOBAL_NORTH = -90.0, 90.0
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


def _lon_segments(west: float, east: float):
    if abs(float(east) - float(west)) >= 360.0:
        return [(GLOBAL_WEST, GLOBAL_EAST)]
    w, e = normalize_lon(west), normalize_lon(east)
    if east > west and math.isclose(e, GLOBAL_WEST) and east > GLOBAL_WEST:
        e = GLOBAL_EAST
    if w < e:
        return [(w, e)]
    if w > e:
        return [(w, GLOBAL_EAST), (GLOBAL_WEST, e)]
    return []


def _cell_id(x: float, y: float, d: float) -> str:
    ix = int(math.floor((x - GLOBAL_WEST) / d))
    iy = int(math.floor((y - GLOBAL_SOUTH) / d))
    return f"gfs_global_{d:g}_{ix}_{iy}".replace(".", "p")


def cells_for_viewport(bbox: dict, *, cell_deg: float = DEFAULT_CELL_DEG, prefetch_cells: int = 0):
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
    segments = _lon_segments(
        float(bbox["west"]) - prefetch_cells * d,
        float(bbox["east"]) + prefetch_cells * d,
    )
    out = {}
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
                    "bbox": {"west": x, "south": y, "east": min(x+d, GLOBAL_EAST), "north": min(y+d, GLOBAL_NORTH)},
                }
                out[cell["id"]] = cell
                x += d
            y += d
    return [out[key] for key in sorted(out)]


def coverage_complete(required_cell_ids, published_cell_ids) -> bool:
    """Fail closed: a URL/addressable cell never proves native published data."""
    required, published = set(required_cell_ids), set(published_cell_ids)
    return bool(required) and required.issubset(published)
