"""B123 subject-aware WeatherGrid fetch planning.

Turns the B120/B121 researched coverage contract into a provider request bbox.

Two scoped request modes are supported:
- one Photography Opportunity
- one Place, only when every active Opportunity at that Place has migrated and
  every coverage plan is complete

The planner deliberately refuses incomplete subject coverage instead of
silently falling back to a Place center.

The current NOAA/NCEP GFS NOMADS subset path accepts one ordinary west/east
bbox. Antimeridian-wrapping plans are therefore reported as unsupported for a
single request; a future provider adapter can split them into two requests.
"""

from __future__ import annotations

from dataclasses import dataclass

from weathergrid_coverage import (
    CoverageError,
    apply_registry_entry,
    index_catalog_opportunities,
    plan_opportunity_coverage,
    plan_place_coverage,
)


@dataclass
class ScopedFetchPlan:
    scope_type: str
    scope_id: str
    complete: bool
    fetch_bbox: dict | None
    viewport_bbox: dict | None
    coverage_bbox: dict | None
    opportunity_ids: list[str]
    errors: list[str]
    warnings: list[str]

    def to_dict(self) -> dict:
        return {
            "scope_type": self.scope_type,
            "scope_id": self.scope_id,
            "complete": self.complete,
            "fetch_bbox": self.fetch_bbox,
            "viewport_bbox": self.viewport_bbox,
            "coverage_bbox": self.coverage_bbox,
            "opportunity_ids": self.opportunity_ids,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def _registry_by_opportunity(registry: dict) -> dict[str, dict]:
    indexed = {}
    for entry in registry.get("entries", []) or []:
        oid = entry.get("opportunity_id")
        if not oid:
            raise CoverageError("coverage registry entry missing opportunity_id")
        if oid in indexed:
            raise CoverageError(f"duplicate coverage registry entry: {oid}")
        indexed[oid] = entry
    return indexed


def _catalog_spots(catalog: dict) -> dict[str, dict]:
    return {
        spot["spot_id"]: spot
        for spot in catalog.get("spots", []) or []
        if spot.get("spot_id")
    }


def _nomads_bbox(fetch_bbox: dict | None) -> dict[str, float] | None:
    if not fetch_bbox:
        return None
    if fetch_bbox.get("wraps_antimeridian"):
        return None
    return {
        "leftlon": float(fetch_bbox["west"]),
        "rightlon": float(fetch_bbox["east"]),
        "toplat": float(fetch_bbox["north"]),
        "bottomlat": float(fetch_bbox["south"]),
    }


def build_scoped_fetch_plan(
    catalog: dict,
    registry: dict,
    *,
    opportunity_id: str | None = None,
    spot_id: str | None = None,
    provider_grid_spacing_deg: float = 0.25,
    default_display_padding_km: float = 10.0,
) -> ScopedFetchPlan:
    if bool(opportunity_id) == bool(spot_id):
        raise CoverageError(
            "exactly one of opportunity_id or spot_id must be supplied"
        )

    opportunities = index_catalog_opportunities(catalog)
    registry_index = _registry_by_opportunity(registry)

    if opportunity_id:
        base = opportunities.get(opportunity_id)
        if not base:
            return ScopedFetchPlan(
                scope_type="opportunity",
                scope_id=opportunity_id,
                complete=False,
                fetch_bbox=None,
                viewport_bbox=None,
                coverage_bbox=None,
                opportunity_ids=[opportunity_id],
                errors=["opportunity not found in catalog"],
                warnings=[],
            )
        entry = registry_index.get(opportunity_id)
        if not entry:
            return ScopedFetchPlan(
                scope_type="opportunity",
                scope_id=opportunity_id,
                complete=False,
                fetch_bbox=None,
                viewport_bbox=None,
                coverage_bbox=None,
                opportunity_ids=[opportunity_id],
                errors=["opportunity has not migrated to WeatherGrid coverage"],
                warnings=[],
            )

        merged = apply_registry_entry(base, entry)
        plan = plan_opportunity_coverage(
            merged,
            provider_grid_spacing_deg=provider_grid_spacing_deg,
            default_display_padding_km=default_display_padding_km,
        )
        errors = list(plan.errors)
        warnings = list(plan.warnings)
        if not plan.complete:
            errors.append(
                "subject-aware coverage is incomplete; scoped provider fetch refused"
            )
        if plan.fetch_bbox and plan.fetch_bbox.get("wraps_antimeridian"):
            errors.append(
                "single NOMADS bbox cannot represent antimeridian-wrapping coverage"
            )

        complete = plan.complete and not errors
        return ScopedFetchPlan(
            scope_type="opportunity",
            scope_id=opportunity_id,
            complete=complete,
            fetch_bbox=plan.fetch_bbox if complete else None,
            viewport_bbox=plan.viewport_bbox,
            coverage_bbox=plan.coverage_bbox,
            opportunity_ids=[opportunity_id],
            errors=errors,
            warnings=warnings,
        )

    spots = _catalog_spots(catalog)
    spot = spots.get(spot_id)
    if not spot:
        return ScopedFetchPlan(
            scope_type="place",
            scope_id=spot_id or "",
            complete=False,
            fetch_bbox=None,
            viewport_bbox=None,
            coverage_bbox=None,
            opportunity_ids=[],
            errors=["spot not found in catalog"],
            warnings=[],
        )

    active = [
        op
        for op in spot.get("opportunities", []) or []
        if op.get("product_status") != "RETIRED"
    ]
    missing = [
        op.get("opportunity_id")
        for op in active
        if op.get("opportunity_id") not in registry_index
    ]
    errors = []
    warnings = []
    if missing:
        errors.append(
            "not all active Opportunities have migrated coverage: "
            + ", ".join(x for x in missing if x)
        )

    merged = []
    for op in active:
        oid = op.get("opportunity_id")
        entry = registry_index.get(oid)
        if entry:
            merged.append(apply_registry_entry(op, entry))

    place_plan = plan_place_coverage(
        merged,
        provider_grid_spacing_deg=provider_grid_spacing_deg,
        default_display_padding_km=default_display_padding_km,
    )
    if place_plan["incomplete_opportunities"]:
        errors.append(
            "one or more migrated Opportunities still have incomplete coverage"
        )
    if place_plan.get("fetch_bbox") and place_plan["fetch_bbox"].get(
        "wraps_antimeridian"
    ):
        errors.append(
            "single NOMADS bbox cannot represent antimeridian-wrapping coverage"
        )

    complete = bool(active) and not errors and place_plan["complete"]
    return ScopedFetchPlan(
        scope_type="place",
        scope_id=spot_id or "",
        complete=complete,
        fetch_bbox=place_plan["fetch_bbox"] if complete else None,
        viewport_bbox=place_plan["viewport_bbox"],
        coverage_bbox=place_plan["coverage_bbox"],
        opportunity_ids=[op.get("opportunity_id") for op in active if op.get("opportunity_id")],
        errors=errors,
        warnings=warnings,
    )


def nomads_bbox_for_plan(plan: ScopedFetchPlan) -> dict[str, float]:
    if not plan.complete or not plan.fetch_bbox:
        raise CoverageError(
            f"scoped fetch plan is incomplete for {plan.scope_type} {plan.scope_id}: "
            + "; ".join(plan.errors)
        )
    bbox = _nomads_bbox(plan.fetch_bbox)
    if bbox is None:
        raise CoverageError(
            "provider request needs split antimeridian support"
        )
    return bbox
