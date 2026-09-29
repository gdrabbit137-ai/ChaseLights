"""Provider-aware WeatherGrid fetch planning for B123.

The map coverage contract (B120/B121) describes what geography matters to a
Photography Opportunity. This module turns that derived coverage into a safe
provider request envelope.

Important safety rule: a scoped Place/Opportunity request is used only when the
coverage registry is complete enough to prove that all required Camera /
Subject / Environment geometry is inside the request. Otherwise the planner
falls back to the broader regional bbox (or fails in strict mode). It never
shrinks a request around the Place center merely because subject geometry is
missing.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from gfs_raw_poc import TAIWAN_BBOX
from weathergrid_coverage import (
    CoverageError,
    apply_registry_entry,
    bbox_contains_bbox,
    index_catalog_opportunities,
    plan_opportunity_coverage,
)

GFS_GRID_SPACING_DEG = 0.25

DEFAULT_CATALOG_PATH = Path("runtime_catalog_v004_r4_2.json")
DEFAULT_REGISTRY_PATH = Path("weathergrid_coverage_registry_r4_2.json")


def _coverage_bbox_from_nomads(bbox: dict[str, float]) -> dict:
    return {
        "west": float(bbox["leftlon"]),
        "south": float(bbox["bottomlat"]),
        "east": float(bbox["rightlon"]),
        "north": float(bbox["toplat"]),
        "wraps_antimeridian": False,
    }


def _nomads_bbox_from_coverage(bbox: dict[str, float]) -> dict[str, float]:
    return {
        "leftlon": float(bbox["west"]),
        "rightlon": float(bbox["east"]),
        "toplat": float(bbox["north"]),
        "bottomlat": float(bbox["south"]),
    }


def _snap_down(value: float, step: float) -> float:
    return math.floor((float(value) + 1e-12) / step) * step


def _snap_up(value: float, step: float) -> float:
    return math.ceil((float(value) - 1e-12) / step) * step


def snap_nomads_bbox_outward(
    bbox: dict[str, float],
    *,
    grid_spacing_deg: float = GFS_GRID_SPACING_DEG,
) -> dict[str, float]:
    """Snap a non-wrapped NOMADS bbox outward to the provider grid."""
    step = float(grid_spacing_deg)
    if step <= 0:
        raise CoverageError("grid_spacing_deg must be > 0")

    left = _snap_down(float(bbox["leftlon"]), step)
    right = _snap_up(float(bbox["rightlon"]), step)
    bottom = _snap_down(float(bbox["bottomlat"]), step)
    top = _snap_up(float(bbox["toplat"]), step)

    left = max(-180.0, left)
    right = min(180.0, right)
    bottom = max(-90.0, bottom)
    top = min(90.0, top)

    if not left < right:
        raise CoverageError(f"invalid snapped longitude range: {left}, {right}")
    if not bottom < top:
        raise CoverageError(f"invalid snapped latitude range: {bottom}, {top}")

    return {
        "leftlon": round(left, 8),
        "rightlon": round(right, 8),
        "toplat": round(top, 8),
        "bottomlat": round(bottom, 8),
    }


def split_coverage_bbox_for_nomads(
    bbox: dict,
    *,
    grid_spacing_deg: float = GFS_GRID_SPACING_DEG,
) -> list[dict[str, float]]:
    """Convert an antimeridian-aware coverage bbox to NOMADS request bboxes."""
    west = float(bbox["west"])
    east = float(bbox["east"])
    south = float(bbox["south"])
    north = float(bbox["north"])
    wraps = bool(bbox.get("wraps_antimeridian", west > east))

    if south >= north:
        raise CoverageError("coverage bbox south must be < north")

    if not wraps:
        return [
            snap_nomads_bbox_outward(
                {
                    "leftlon": west,
                    "rightlon": east,
                    "bottomlat": south,
                    "toplat": north,
                },
                grid_spacing_deg=grid_spacing_deg,
            )
        ]

    raw_segments = [
        {
            "leftlon": west,
            "rightlon": 180.0,
            "bottomlat": south,
            "toplat": north,
        },
        {
            "leftlon": -180.0,
            "rightlon": east,
            "bottomlat": south,
            "toplat": north,
        },
    ]
    segments = []
    for segment in raw_segments:
        if segment["rightlon"] - segment["leftlon"] <= 1e-9:
            continue
        segments.append(
            snap_nomads_bbox_outward(
                segment,
                grid_spacing_deg=grid_spacing_deg,
            )
        )
    if not segments:
        raise CoverageError("wrapped coverage bbox produced no provider segments")
    return segments


def _load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _registry_index(registry: dict) -> dict[str, dict]:
    indexed = {}
    for entry in registry.get("entries", []) or []:
        oid = entry.get("opportunity_id")
        if not oid:
            continue
        if oid in indexed:
            raise CoverageError(f"duplicate coverage registry entry: {oid}")
        indexed[oid] = entry
    return indexed


def _spot_index(catalog: dict) -> dict[str, dict]:
    indexed = {}
    for spot in catalog.get("spots", []) or []:
        sid = spot.get("spot_id")
        if not sid:
            continue
        if sid in indexed:
            raise CoverageError(f"duplicate spot_id in catalog: {sid}")
        indexed[sid] = spot
    return indexed


def _regional_plan(region: str, reason: str | None = None) -> dict:
    if region != "tw":
        raise CoverageError(f"B123 currently has no curated regional fallback for {region!r}")
    bbox = dict(TAIWAN_BBOX)
    return {
        "provider": "NOAA/NCEP NOMADS",
        "model": "GFS",
        "grid_spacing_degrees": GFS_GRID_SPACING_DEG,
        "requested_scope": {"type": "region", "id": region},
        "effective_scope": {"type": "region", "id": region},
        "coverage_complete": True,
        "safe_to_scope": True,
        "safe_to_publish_preview": True,
        "fallback_reason": reason,
        "spot_ids": [],
        "coverage_bbox": _coverage_bbox_from_nomads(bbox),
        "viewport_bbox": _coverage_bbox_from_nomads(bbox),
        "fetch_bbox": _coverage_bbox_from_nomads(bbox),
        "segments": [bbox],
    }


def _fallback_or_raise(
    *,
    region: str,
    requested_scope: dict,
    reason: str,
    strict: bool,
    spot_ids: list[str],
    diagnostics: dict | None = None,
) -> dict:
    if strict:
        raise CoverageError(reason)
    plan = _regional_plan(region, reason=reason)
    plan["requested_scope"] = requested_scope
    plan["coverage_complete"] = False
    plan["safe_to_scope"] = False
    plan["safe_to_publish_preview"] = False
    plan["spot_ids"] = list(spot_ids)
    if diagnostics is not None:
        plan["coverage_diagnostics"] = diagnostics
    return plan


def _build_opportunity_plan(
    catalog: dict,
    registry: dict,
    opportunity_id: str,
    *,
    region: str,
    strict: bool,
) -> dict:
    opportunities = index_catalog_opportunities(catalog)
    registry_by_id = _registry_index(registry)
    opportunity = opportunities.get(opportunity_id)
    if not opportunity:
        raise CoverageError(f"opportunity not found: {opportunity_id}")

    spot_id = opportunity.get("spot_id")
    requested = {"type": "opportunity", "id": opportunity_id}

    if region == "tw" and not str(spot_id or "").startswith("tw-"):
        raise CoverageError(
            f"opportunity {opportunity_id} is outside the Taiwan GFS POC region"
        )

    entry = registry_by_id.get(opportunity_id)
    if not entry:
        return _fallback_or_raise(
            region=region,
            requested_scope=requested,
            reason=f"{opportunity_id} has no subject-aware coverage registry entry",
            strict=strict,
            spot_ids=[spot_id] if spot_id else [],
        )

    merged = apply_registry_entry(opportunity, entry)
    coverage_plan = plan_opportunity_coverage(
        merged,
        provider_grid_spacing_deg=GFS_GRID_SPACING_DEG,
    )
    if not coverage_plan.complete or not coverage_plan.fetch_bbox:
        return _fallback_or_raise(
            region=region,
            requested_scope=requested,
            reason=(
                f"{opportunity_id} subject-aware coverage is incomplete "
                f"(status={coverage_plan.status})"
            ),
            strict=strict,
            spot_ids=[spot_id] if spot_id else [],
            diagnostics=coverage_plan.to_dict(),
        )

    segments = split_coverage_bbox_for_nomads(
        coverage_plan.fetch_bbox,
        grid_spacing_deg=GFS_GRID_SPACING_DEG,
    )
    # Snapping must only grow the already halo-padded fetch bbox.
    if len(segments) == 1:
        snapped_coverage = _coverage_bbox_from_nomads(segments[0])
        if not bbox_contains_bbox(snapped_coverage, coverage_plan.fetch_bbox):
            raise CoverageError("provider snapping unexpectedly cropped fetch_bbox")

    return {
        "provider": "NOAA/NCEP NOMADS",
        "model": "GFS",
        "grid_spacing_degrees": GFS_GRID_SPACING_DEG,
        "requested_scope": requested,
        "effective_scope": requested,
        "coverage_complete": True,
        "safe_to_scope": True,
        "safe_to_publish_preview": False,
        "fallback_reason": None,
        "spot_ids": [spot_id] if spot_id else [],
        "coverage_bbox": coverage_plan.coverage_bbox,
        "viewport_bbox": coverage_plan.viewport_bbox,
        "fetch_bbox": coverage_plan.fetch_bbox,
        "coverage_diagnostics": coverage_plan.to_dict(),
        "segments": segments,
    }


def _build_place_plan(
    catalog: dict,
    registry: dict,
    spot_id: str,
    *,
    region: str,
    strict: bool,
) -> dict:
    spots = _spot_index(catalog)
    registry_by_id = _registry_index(registry)
    spot = spots.get(spot_id)
    if not spot:
        raise CoverageError(f"spot not found: {spot_id}")

    if region == "tw" and not spot_id.startswith("tw-"):
        raise CoverageError(f"spot {spot_id} is outside the Taiwan GFS POC region")

    requested = {"type": "place", "id": spot_id}
    active = [
        opportunity
        for opportunity in spot.get("opportunities", []) or []
        if opportunity.get("product_status") != "RETIRED"
    ]
    if not active:
        return _fallback_or_raise(
            region=region,
            requested_scope=requested,
            reason=f"{spot_id} has no active Opportunities",
            strict=strict,
            spot_ids=[spot_id],
        )

    coverage_plans = []
    missing_entries = []
    incomplete = []
    points = []

    for opportunity in active:
        oid = opportunity.get("opportunity_id")
        entry = registry_by_id.get(oid)
        if not entry:
            missing_entries.append(oid)
            continue
        merged = apply_registry_entry(opportunity, entry)
        plan = plan_opportunity_coverage(
            merged,
            provider_grid_spacing_deg=GFS_GRID_SPACING_DEG,
        )
        coverage_plans.append((oid, plan))
        if not plan.complete or not plan.fetch_bbox:
            incomplete.append({
                "opportunity_id": oid,
                "status": plan.status,
                "errors": plan.errors,
            })
            continue
        # Union fetch bboxes, not just viewports: each Opportunity's provider
        # halo must survive the Place-level union.
        from weathergrid_coverage import geometry_points
        fb = plan.fetch_bbox
        points.extend(
            geometry_points({
                "type": "bbox",
                "west": fb["west"],
                "south": fb["south"],
                "east": fb["east"],
                "north": fb["north"],
            })
        )

    if missing_entries or incomplete:
        return _fallback_or_raise(
            region=region,
            requested_scope=requested,
            reason=(
                f"{spot_id} does not yet have complete coverage for every active "
                f"Opportunity (missing={len(missing_entries)}, incomplete={len(incomplete)})"
            ),
            strict=strict,
            spot_ids=[spot_id],
            diagnostics={
                "catalog_opportunity_count": len(active),
                "migrated_count": len(coverage_plans),
                "missing_registry_entries": missing_entries,
                "incomplete_opportunities": incomplete,
            },
        )

    if not points:
        return _fallback_or_raise(
            region=region,
            requested_scope=requested,
            reason=f"{spot_id} produced no complete provider fetch geometry",
            strict=strict,
            spot_ids=[spot_id],
        )

    from weathergrid_coverage import bbox_from_points

    fetch_bbox = bbox_from_points(points)
    segments = split_coverage_bbox_for_nomads(fetch_bbox)

    # The browser's Place-level display union is derived separately. For B123
    # provider planning, fetch_bbox is the authoritative all-Opportunity union.
    return {
        "provider": "NOAA/NCEP NOMADS",
        "model": "GFS",
        "grid_spacing_degrees": GFS_GRID_SPACING_DEG,
        "requested_scope": requested,
        "effective_scope": requested,
        "coverage_complete": True,
        "safe_to_scope": True,
        "safe_to_publish_preview": False,
        "fallback_reason": None,
        "spot_ids": [spot_id],
        "coverage_bbox": None,
        "viewport_bbox": None,
        "fetch_bbox": fetch_bbox,
        "coverage_diagnostics": {
            "catalog_opportunity_count": len(active),
            "migrated_count": len(coverage_plans),
            "missing_registry_entries": [],
            "incomplete_opportunities": [],
        },
        "segments": segments,
    }


def build_gfs_fetch_plan(
    *,
    scope_type: str = "region",
    scope_id: str | None = None,
    region: str = "tw",
    strict: bool = False,
    catalog: dict | None = None,
    registry: dict | None = None,
    catalog_path: str | Path = DEFAULT_CATALOG_PATH,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict:
    """Build a safe GFS fetch plan for region / Place / Opportunity scope."""
    scope_type = str(scope_type or "region").lower()
    if scope_type not in {"region", "place", "opportunity"}:
        raise CoverageError(f"unsupported coverage scope: {scope_type}")

    if scope_type == "region":
        if scope_id not in (None, "", region):
            raise CoverageError("region scope does not accept a different scope_id")
        return _regional_plan(region)

    if not scope_id:
        raise CoverageError(f"{scope_type} scope requires scope_id")

    catalog = catalog if catalog is not None else _load_json(catalog_path)
    registry = registry if registry is not None else _load_json(registry_path)

    if scope_type == "opportunity":
        return _build_opportunity_plan(
            catalog,
            registry,
            str(scope_id),
            region=region,
            strict=strict,
        )
    return _build_place_plan(
        catalog,
        registry,
        str(scope_id),
        region=region,
        strict=strict,
    )


def write_fetch_plan(plan: dict, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
