"""B120 Topic-aware WeatherGrid coverage helpers.

This module implements the geometry/coverage contract from
WEATHERGRID_COVERAGE_SPEC_R4_2.md. It is deliberately independent from
production Opportunity scoring.

The first responsibility is deterministic validation and envelope planning:
- validate supported subject/environment geometries
- resolve Camera Zone references to existing Opportunity viewpoints
- derive antimeridian-aware coverage/viewport/fetch bounding boxes
- surface incomplete coverage instead of silently falling back to Place center

No weather score is changed by this module.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

EARTH_RADIUS_KM = 6371.0088
SUPPORTED_GEOMETRY_TYPES = {"point", "bbox", "polygon", "sector", "corridor"}
COVERAGE_STATUSES = {"verified", "provisional", "needs_research"}
BROWSER_EXPOSURES = {"public", "generalized", "internal_only"}


class CoverageError(ValueError):
    pass


def normalize_lon(lon: float) -> float:
    value = ((float(lon) + 180.0) % 360.0) - 180.0
    # Keep +180 when the input was explicitly positive 180-ish; this makes
    # display output a little easier to understand while preserving equivalence.
    if value == -180.0 and float(lon) > 0:
        return 180.0
    return value


def validate_lat(lat: float) -> float:
    value = float(lat)
    if not -90.0 <= value <= 90.0:
        raise CoverageError(f"latitude out of range: {lat}")
    return value


def validate_lon(lon: float) -> float:
    value = float(lon)
    if not -180.0 <= value <= 180.0:
        raise CoverageError(f"longitude out of range: {lon}")
    return value


def _destination(lat: float, lon: float, bearing_deg: float, distance_km: float) -> tuple[float, float]:
    """Return a spherical-Earth destination point."""
    lat1 = math.radians(validate_lat(lat))
    lon1 = math.radians(validate_lon(lon))
    bearing = math.radians(float(bearing_deg) % 360.0)
    angular = max(0.0, float(distance_km)) / EARTH_RADIUS_KM

    sin_lat2 = (
        math.sin(lat1) * math.cos(angular)
        + math.cos(lat1) * math.sin(angular) * math.cos(bearing)
    )
    lat2 = math.asin(max(-1.0, min(1.0, sin_lat2)))
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular) * math.cos(lat1),
        math.cos(angular) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), normalize_lon(math.degrees(lon2))


def _azimuth_span(start: float, end: float) -> float:
    return (float(end) - float(start)) % 360.0


def _sample_sector_bearings(start: float, end: float, step_deg: float = 10.0) -> list[float]:
    start = float(start) % 360.0
    span = _azimuth_span(start, end)
    # start == end means a full-circle sector only when explicitly declared by
    # a 360-degree numeric difference; otherwise it is a zero-width ray.
    raw_difference = float(end) - float(start)
    if abs(raw_difference) >= 359.999:
        span = 360.0
    count = max(1, int(math.ceil(span / step_deg)))
    return [((start + span * i / count) % 360.0) for i in range(count + 1)]


def geometry_points(
    geometry: dict,
    *,
    viewpoint_lookup: dict[str, dict] | None = None,
) -> list[tuple[float, float]]:
    """Expand a supported geometry into representative (lat, lon) points."""
    if not isinstance(geometry, dict):
        raise CoverageError("geometry must be an object")
    kind = geometry.get("type")
    if kind not in SUPPORTED_GEOMETRY_TYPES:
        raise CoverageError(f"unsupported geometry type: {kind!r}")

    if kind == "point":
        return [(validate_lat(geometry["lat"]), validate_lon(geometry["lon"]))]

    if kind == "bbox":
        west = validate_lon(geometry["west"])
        east = validate_lon(geometry["east"])
        south = validate_lat(geometry["south"])
        north = validate_lat(geometry["north"])
        if south > north:
            raise CoverageError("bbox south must be <= north")
        return [(south, west), (south, east), (north, west), (north, east)]

    if kind == "polygon":
        coords = geometry.get("coordinates")
        if not isinstance(coords, list) or len(coords) < 3:
            raise CoverageError("polygon requires at least three coordinates")
        points = []
        for pair in coords:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise CoverageError("polygon coordinates must be [lon, lat]")
            lon, lat = pair
            points.append((validate_lat(lat), validate_lon(lon)))
        return points

    if kind == "corridor":
        coords = geometry.get("coordinates")
        width = float(geometry.get("half_width_km", 0.0))
        if not isinstance(coords, list) or len(coords) < 2:
            raise CoverageError("corridor requires at least two coordinates")
        if width < 0:
            raise CoverageError("corridor half_width_km must be >= 0")
        points: list[tuple[float, float]] = []
        for pair in coords:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise CoverageError("corridor coordinates must be [lon, lat]")
            lon, lat = pair
            lat = validate_lat(lat)
            lon = validate_lon(lon)
            points.append((lat, lon))
            if width:
                for bearing in (0, 90, 180, 270):
                    points.append(_destination(lat, lon, bearing, width))
        return points

    # sector
    origin_ref = geometry.get("origin_viewpoint_id")
    if origin_ref:
        if not viewpoint_lookup or origin_ref not in viewpoint_lookup:
            raise CoverageError(f"sector origin viewpoint not found: {origin_ref}")
        vp = viewpoint_lookup[origin_ref]
        if vp.get("lat") is None or vp.get("lon") is None:
            raise CoverageError(f"sector origin viewpoint has no coordinate: {origin_ref}")
        origin_lat = validate_lat(vp["lat"])
        origin_lon = validate_lon(vp["lon"])
    else:
        origin_lat = validate_lat(geometry["origin_lat"])
        origin_lon = validate_lon(geometry["origin_lon"])

    min_range = float(geometry.get("min_range_km", 0.0))
    max_range = float(geometry["max_range_km"])
    if min_range < 0 or max_range < 0 or min_range > max_range:
        raise CoverageError("sector range must satisfy 0 <= min <= max")

    start = float(geometry["azimuth_start_deg"])
    end = float(geometry["azimuth_end_deg"])
    bearings = _sample_sector_bearings(start, end)
    points = [(origin_lat, origin_lon)]
    for bearing in bearings:
        if min_range:
            points.append(_destination(origin_lat, origin_lon, bearing, min_range))
        points.append(_destination(origin_lat, origin_lon, bearing, max_range))
    return points


def _minimal_longitude_arc(longitudes: Iterable[float]) -> tuple[float, float, bool]:
    """Return west/east bounds using the smallest circular longitude arc."""
    values = [((normalize_lon(lon) + 360.0) % 360.0) for lon in longitudes]
    if not values:
        raise CoverageError("no longitudes supplied")
    values.sort()
    if len(values) == 1:
        lon = normalize_lon(values[0])
        return lon, lon, False

    gaps = []
    for i, current in enumerate(values):
        nxt = values[(i + 1) % len(values)]
        if i == len(values) - 1:
            nxt += 360.0
        gaps.append((nxt - current, i))
    _, gap_index = max(gaps)
    start = values[(gap_index + 1) % len(values)]
    end = values[gap_index]
    if end < start:
        end += 360.0

    west = normalize_lon(start)
    east = normalize_lon(end)
    wraps = west > east
    return west, east, wraps


def bbox_from_points(points: Iterable[tuple[float, float]]) -> dict:
    points = list(points)
    if not points:
        raise CoverageError("cannot derive bbox from empty geometry")
    lats = [validate_lat(lat) for lat, _ in points]
    lons = [validate_lon(lon) for _, lon in points]
    west, east, wraps = _minimal_longitude_arc(lons)
    return {
        "west": round(west, 7),
        "south": round(min(lats), 7),
        "east": round(east, 7),
        "north": round(max(lats), 7),
        "wraps_antimeridian": wraps,
    }


def _bbox_points(bbox: dict) -> list[tuple[float, float]]:
    return geometry_points({
        "type": "bbox",
        "west": bbox["west"],
        "south": bbox["south"],
        "east": bbox["east"],
        "north": bbox["north"],
    })


def pad_bbox_km(bbox: dict, padding_km: float) -> dict:
    padding_km = float(padding_km)
    if padding_km < 0:
        raise CoverageError("padding_km must be >= 0")
    if padding_km == 0:
        return dict(bbox)

    points = _bbox_points(bbox)
    expanded = list(points)
    for lat, lon in points:
        for bearing in (0, 90, 180, 270):
            expanded.append(_destination(lat, lon, bearing, padding_km))
    return bbox_from_points(expanded)


def bbox_contains_point(bbox: dict, lat: float, lon: float, tolerance: float = 1e-7) -> bool:
    lat = validate_lat(lat)
    lon = normalize_lon(validate_lon(lon))
    if not (bbox["south"] - tolerance <= lat <= bbox["north"] + tolerance):
        return False
    west = normalize_lon(bbox["west"])
    east = normalize_lon(bbox["east"])
    wraps = bool(bbox.get("wraps_antimeridian", west > east))
    if wraps:
        return lon >= west - tolerance or lon <= east + tolerance
    return west - tolerance <= lon <= east + tolerance


def bbox_contains_bbox(outer: dict, inner: dict) -> bool:
    return all(bbox_contains_point(outer, lat, lon) for lat, lon in _bbox_points(inner))


@dataclass
class CoveragePlan:
    complete: bool
    status: str
    coverage_bbox: dict | None
    viewport_bbox: dict | None
    fetch_bbox: dict | None
    camera_zone_count: int
    subject_geometry_count: int
    environment_geometry_count: int
    coverage_confidence: str | None
    errors: list[str]
    warnings: list[str]

    def to_dict(self) -> dict:
        return {
            "complete": self.complete,
            "status": self.status,
            "coverage_bbox": self.coverage_bbox,
            "viewport_bbox": self.viewport_bbox,
            "fetch_bbox": self.fetch_bbox,
            "camera_zone_count": self.camera_zone_count,
            "subject_geometry_count": self.subject_geometry_count,
            "environment_geometry_count": self.environment_geometry_count,
            "coverage_confidence": self.coverage_confidence,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def plan_opportunity_coverage(
    opportunity: dict,
    *,
    provider_grid_spacing_deg: float = 0.25,
    default_display_padding_km: float = 10.0,
) -> CoveragePlan:
    """Validate one Opportunity and derive coverage/viewport/fetch envelopes."""
    coverage = opportunity.get("weather_coverage") or {}
    status = coverage.get("status", "needs_research")
    errors: list[str] = []
    warnings: list[str] = []

    if status not in COVERAGE_STATUSES:
        errors.append(f"invalid weather_coverage.status: {status!r}")
        status = "needs_research"

    viewpoints = {
        vp.get("viewpoint_id"): vp
        for vp in opportunity.get("viewpoints", [])
        if vp.get("viewpoint_id")
    }

    all_points: list[tuple[float, float]] = []
    camera_refs = coverage.get("camera_zone_refs") or []
    camera_exposures = coverage.get("camera_zone_browser_exposure") or {}
    resolved_camera_count = 0
    for ref in camera_refs:
        exposure = camera_exposures.get(ref)
        if exposure not in BROWSER_EXPOSURES:
            errors.append(
                f"camera_zone_ref requires explicit browser exposure: {ref}"
            )
        vp = viewpoints.get(ref)
        if not vp:
            errors.append(f"camera_zone_ref not found: {ref}")
            continue
        if vp.get("lat") is None or vp.get("lon") is None:
            errors.append(f"camera_zone_ref has no coordinate: {ref}")
            continue
        try:
            all_points.append((validate_lat(vp["lat"]), validate_lon(vp["lon"])))
            resolved_camera_count += 1
            if vp.get("geometry_type") not in {None, "point"}:
                warnings.append(
                    f"{ref} uses {vp.get('geometry_type')} geometry; B120 currently envelopes "
                    "its coordinate anchor until a reconstructable public extent is curated"
                )
        except CoverageError as exc:
            errors.append(f"{ref}: {exc}")

    def add_geometries(items: list[dict], kind_label: str) -> int:
        count = 0
        for item in items:
            geometry = item.get("geometry") if isinstance(item, dict) else None
            exposure = item.get("browser_exposure", "public") if isinstance(item, dict) else "public"
            if exposure not in BROWSER_EXPOSURES:
                errors.append(f"{kind_label} has invalid browser_exposure: {exposure!r}")
            try:
                points = geometry_points(geometry, viewpoint_lookup=viewpoints)
            except (CoverageError, KeyError, TypeError, ValueError) as exc:
                errors.append(f"{kind_label} geometry invalid: {exc}")
                continue
            all_points.extend(points)
            count += 1
        return count

    subjects = coverage.get("subject_geometries") or []
    environments = coverage.get("environment_geometries") or []
    subject_count = add_geometries(subjects, "subject")
    environment_count = add_geometries(environments, "environment")

    if not camera_refs:
        errors.append("weather_coverage requires at least one camera_zone_ref")
    if resolved_camera_count == 0:
        errors.append("no Camera Zone coordinate could be resolved")

    # A local/celestial Opportunity may deliberately use a horizon/environment
    # geometry instead of a terrestrial Subject Geometry, but that exception
    # must still be explicit rather than an implicit Place-center fallback.
    if subject_count == 0 and environment_count == 0:
        errors.append("coverage requires subject or environment geometry")

    coverage_bbox = viewport_bbox = fetch_bbox = None
    if all_points:
        try:
            coverage_bbox = bbox_from_points(all_points)
            padding = float(coverage.get("display_padding_km", default_display_padding_km))
            viewport_bbox = pad_bbox_km(coverage_bbox, padding)

            # One whole grid spacing is required around the viewport for
            # bilinear interpolation. Convert a degree-sized source cell to a
            # conservative km halo using meridional degree length.
            spacing = float(provider_grid_spacing_deg)
            if spacing <= 0:
                raise CoverageError("provider_grid_spacing_deg must be > 0")
            provider_halo_km = spacing * 111.32
            fetch_bbox = pad_bbox_km(viewport_bbox, provider_halo_km)
        except (CoverageError, TypeError, ValueError) as exc:
            errors.append(f"coverage planning failed: {exc}")

    complete = not errors and status in {"verified", "provisional"}
    if status == "needs_research":
        complete = False

    return CoveragePlan(
        complete=complete,
        status=status,
        coverage_bbox=coverage_bbox,
        viewport_bbox=viewport_bbox,
        fetch_bbox=fetch_bbox,
        camera_zone_count=resolved_camera_count,
        subject_geometry_count=subject_count,
        environment_geometry_count=environment_count,
        coverage_confidence=coverage.get("coverage_confidence"),
        errors=errors,
        warnings=warnings,
    )


def plan_place_coverage(
    opportunities: list[dict],
    *,
    provider_grid_spacing_deg: float = 0.25,
    default_display_padding_km: float = 10.0,
) -> dict:
    """Union active Opportunity coverage for a Place-level default viewport."""
    plans = []
    union_points: list[tuple[float, float]] = []
    for opportunity in opportunities:
        if opportunity.get("product_status") == "RETIRED":
            continue
        plan = plan_opportunity_coverage(
            opportunity,
            provider_grid_spacing_deg=provider_grid_spacing_deg,
            default_display_padding_km=default_display_padding_km,
        )
        plans.append((opportunity.get("opportunity_id"), plan))
        if plan.coverage_bbox:
            union_points.extend(_bbox_points(plan.coverage_bbox))

    coverage_bbox = bbox_from_points(union_points) if union_points else None
    viewport_bbox = None
    fetch_bbox = None
    if coverage_bbox:
        viewport_bbox = pad_bbox_km(coverage_bbox, default_display_padding_km)
        fetch_bbox = pad_bbox_km(
            viewport_bbox,
            float(provider_grid_spacing_deg) * 111.32,
        )

    incomplete = [
        {"opportunity_id": oid, "errors": plan.errors, "status": plan.status}
        for oid, plan in plans
        if not plan.complete
    ]
    return {
        "complete": not incomplete and bool(plans),
        "coverage_bbox": coverage_bbox,
        "viewport_bbox": viewport_bbox,
        "fetch_bbox": fetch_bbox,
        "opportunity_count": len(plans),
        "incomplete_opportunities": incomplete,
    }


def index_catalog_opportunities(catalog: dict) -> dict[str, dict]:
    """Return opportunity_id -> Opportunity for the runtime catalog."""
    indexed: dict[str, dict] = {}
    for spot in catalog.get("spots", []) or []:
        for opportunity in spot.get("opportunities", []) or []:
            oid = opportunity.get("opportunity_id")
            if not oid:
                continue
            if oid in indexed:
                raise CoverageError(f"duplicate opportunity_id in catalog: {oid}")
            indexed[oid] = opportunity
    return indexed


def apply_registry_entry(opportunity: dict, registry_entry: dict) -> dict:
    """Return a shallow Opportunity copy with sidecar weather_coverage applied."""
    oid = opportunity.get("opportunity_id")
    if registry_entry.get("opportunity_id") != oid:
        raise CoverageError(
            f"registry opportunity mismatch: {registry_entry.get('opportunity_id')} != {oid}"
        )
    weather_coverage = registry_entry.get("weather_coverage")
    if not isinstance(weather_coverage, dict):
        raise CoverageError(f"{oid} registry entry missing weather_coverage object")
    merged = dict(opportunity)
    merged["weather_coverage"] = weather_coverage
    return merged


def audit_coverage_registry(catalog: dict, registry: dict) -> dict:
    """Validate a sidecar B121 coverage registry against the runtime catalog."""
    if registry.get("schema_version") != 1:
        raise CoverageError("coverage registry schema_version must be 1")

    indexed = index_catalog_opportunities(catalog)
    seen = set()
    results = []
    counts = {
        "entries": 0,
        "verified": 0,
        "provisional": 0,
        "needs_research": 0,
        "complete": 0,
        "incomplete": 0,
        "missing_opportunity": 0,
    }

    for entry in registry.get("entries", []) or []:
        oid = entry.get("opportunity_id")
        counts["entries"] += 1
        if not oid:
            results.append({"opportunity_id": None, "complete": False, "errors": ["missing opportunity_id"]})
            counts["incomplete"] += 1
            continue
        if oid in seen:
            results.append({"opportunity_id": oid, "complete": False, "errors": ["duplicate registry entry"]})
            counts["incomplete"] += 1
            continue
        seen.add(oid)

        opportunity = indexed.get(oid)
        if not opportunity:
            results.append({"opportunity_id": oid, "complete": False, "errors": ["opportunity not found in catalog"]})
            counts["missing_opportunity"] += 1
            counts["incomplete"] += 1
            continue

        merged = apply_registry_entry(opportunity, entry)
        plan = plan_opportunity_coverage(merged)
        status = plan.status
        if status in {"verified", "provisional", "needs_research"}:
            counts[status] += 1
        if plan.complete:
            counts["complete"] += 1
        else:
            counts["incomplete"] += 1

        expected_spot = entry.get("spot_id")
        if expected_spot and expected_spot != opportunity.get("spot_id"):
            plan.errors.append(
                f"registry spot_id mismatch: {expected_spot} != {opportunity.get('spot_id')}"
            )
            if plan.complete:
                plan.complete = False
                counts["complete"] -= 1
                counts["incomplete"] += 1

        results.append({
            "opportunity_id": oid,
            "spot_id": opportunity.get("spot_id"),
            **plan.to_dict(),
            "provenance": entry.get("provenance"),
        })

    return {
        "schema_version": 1,
        "registry_version": registry.get("registry_version"),
        "counts": counts,
        "results": results,
    }
