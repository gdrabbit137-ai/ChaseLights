"""Build a compact browser payload for B122 Opportunity-aware WeatherGrid UI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from weathergrid_coverage import (
    apply_registry_entry,
    index_catalog_opportunities,
    plan_opportunity_coverage,
)


def _spot_index(catalog: dict) -> dict[str, dict]:
    return {
        spot["spot_id"]: spot
        for spot in catalog.get("spots", []) or []
        if spot.get("spot_id")
    }


def _camera_payload(opportunity: dict, coverage: dict) -> list[dict]:
    viewpoints = {
        vp.get("viewpoint_id"): vp
        for vp in opportunity.get("viewpoints", []) or []
        if vp.get("viewpoint_id")
    }
    exposures = coverage.get("camera_zone_browser_exposure") or {}
    result = []
    for ref in coverage.get("camera_zone_refs") or []:
        vp = viewpoints.get(ref)
        if not vp:
            continue
        exposure = exposures.get(ref)
        if exposure not in {"public", "generalized", "internal_only"}:
            # Browser export is intentionally fail-closed. A future private
            # Camera Zone must never leak because an exposure field was omitted.
            exposure = "internal_only"
        row = {
            "viewpoint_id": ref,
            "name": vp.get("name"),
            "browser_exposure": exposure,
            "geometry_type": vp.get("geometry_type"),
            "geometry_extent_m": vp.get("geometry_extent_m"),
            "geometry_confidence": vp.get("geometry_confidence"),
        }
        if exposure in {"public", "generalized"}:
            row["lat"] = vp.get("lat")
            row["lon"] = vp.get("lon")
        result.append(row)
    return result


def build_coverage_browser_payload(catalog: dict, registry: dict) -> dict:
    opportunities = index_catalog_opportunities(catalog)
    spots = _spot_index(catalog)
    grouped: dict[str, dict] = {}

    for entry in registry.get("entries", []) or []:
        oid = entry.get("opportunity_id")
        base = opportunities.get(oid)
        if not base:
            continue
        merged = apply_registry_entry(base, entry)
        coverage = merged["weather_coverage"]
        plan = plan_opportunity_coverage(merged)
        spot_id = base.get("spot_id")
        spot = spots.get(spot_id, {})

        group = grouped.setdefault(
            spot_id,
            {
                "spot_id": spot_id,
                "canonical_name": spot.get("canonical_name"),
                "opportunities": [],
            },
        )
        group["opportunities"].append(
            {
                "opportunity_id": oid,
                "name_zh": base.get("name_zh"),
                "legacy_theme": base.get("legacy_theme"),
                "status": plan.status,
                "complete": plan.complete,
                "coverage_confidence": plan.coverage_confidence,
                "camera_zones": _camera_payload(base, coverage),
                "subject_geometries": coverage.get("subject_geometries") or [],
                "environment_geometries": coverage.get("environment_geometries") or [],
                "coverage_bbox": plan.coverage_bbox,
                "viewport_bbox": plan.viewport_bbox,
                "errors": plan.errors,
                "warnings": plan.warnings,
                "note": coverage.get("note"),
            }
        )

    for spot_id, group in grouped.items():
        group["opportunities"].sort(key=lambda x: x["opportunity_id"])
        spot = spots.get(spot_id, {})
        active_catalog_opportunities = [
            op
            for op in spot.get("opportunities", []) or []
            if op.get("product_status") != "RETIRED"
        ]
        group["catalog_opportunity_count"] = len(active_catalog_opportunities)
        group["coverage_entry_count"] = len(group["opportunities"])
        group["all_topics_migrated"] = (
            group["coverage_entry_count"] == group["catalog_opportunity_count"]
        )
        group["all_topics_complete"] = (
            group["all_topics_migrated"]
            and all(op["complete"] for op in group["opportunities"])
        )

    return {
        "schema_version": 1,
        "registry_version": registry.get("registry_version"),
        "contract": registry.get("contract"),
        "spots": sorted(grouped.values(), key=lambda x: x["spot_id"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="runtime_catalog_v004_r4_2.json")
    parser.add_argument(
        "--registry",
        default="weathergrid_coverage_registry_r4_2.json",
    )
    parser.add_argument(
        "--output",
        default="weathergrid_coverage_browser.json",
    )
    # CL-DATA-07: optional per-region export (e.g. us). When given, the
    # payload is scoped to that region's spots and carries the region's
    # photography layer list derived from its published WeatherGrid bundles
    # (data-driven; a source without a published bundle contributes nothing).
    parser.add_argument("--region", default=None)
    parser.add_argument("--bundles-dir", default="weathergrid")
    return parser.parse_args()


def region_layer_list(region: str, bundles_dir: str) -> dict:
    """Photography layers per source for a region, from its published bundles.

    Fail-closed by construction: only sources with an existing published
    bundle appear, and only fields those bundles actually carry. A missing
    VIIRS/CAMS bundle therefore never advertises layers the region cannot
    render.
    """
    bundle_names = {
        "gfs": f"gfs_{region}_weather_browser.json",
        "icon": f"icon_{region}_cloud_browser.json",
        "cwa": f"cwa_wrf3_{region}_weather_browser.json",
        "jma": f"jma_msm_{region}_cloud_browser.json",
        "himawari": f"himawari9_{region}_cloud_browser.json",
        "cams": f"cams_global_{region}_aod_browser.json",
        "viirs": f"viirs_nightlights_{region}_browser.json",
    }
    result = {}
    for source_id, filename in bundle_names.items():
        path = Path(bundles_dir) / filename
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        fields = data.get("fields")
        if isinstance(fields, dict) and fields:
            result[source_id] = sorted(fields)
    return result


def apply_region_scope(payload: dict, region: str, bundles_dir: str) -> dict:
    """Scope a coverage browser payload to one region and attach its layers."""
    prefix = region.lower() + "-"
    payload["spots"] = [
        spot
        for spot in payload["spots"]
        if str(spot.get("spot_id", "")).startswith(prefix)
    ]
    payload["region"] = region.lower()
    payload["region_layers"] = region_layer_list(region, bundles_dir)
    return payload


def main() -> int:
    args = parse_args()
    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    payload = build_coverage_browser_payload(catalog, registry)
    if args.region:
        payload = apply_region_scope(payload, args.region, args.bundles_dir)
    Path(args.output).write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": args.output,
        "region": args.region,
        "spots": len(payload["spots"]),
        "opportunities": sum(len(s["opportunities"]) for s in payload["spots"]),
        "region_layers": payload.get("region_layers"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
