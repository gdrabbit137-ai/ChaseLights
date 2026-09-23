"""ChaseLights v0.04 R4.2 full Taiwan Opportunity compatibility adapter.

This preview adapter loads the curated B15 runtime catalog and bridges it into
existing schema-9 output without changing legacy Theme score semantics.

Important:
- Place -> Photography Opportunity -> Condition Variant is the governing model.
- Viewpoints are reference/precision geography, not universal tripod points.
- Explicit runtime blockers never silently become a generic Theme fallback.
- Prototype formulas are metadata-ready but not production-certified.
"""

from copy import deepcopy
import base64
import bz2
import json
from pathlib import Path

from opportunity_runtime import dependency_state, supports_runtime_contract

ADAPTER_VERSION = "v0.04-r4.2-b28-p0-final-simple-preview"
CATALOG_PART_PATTERN = "runtime_catalog_v004_r4_2_b15.compact.part{part}.b64"
VALID_MODES = {"area_opportunity", "composition_specific"}
VALID_TOPOLOGIES = {
    "local_area",
    "area_plus_environment",
    "directional_sector",
    "exact_alignment",
}


def _load_catalog():
    base = Path(__file__).parent
    encoded = "".join(
        (base / CATALOG_PART_PATTERN.format(part=part)).read_text(encoding="ascii").strip()
        for part in range(1, 6)
    )
    if len(encoded) != 19356 or len(encoded) % 4:
        raise ValueError(f"Invalid compact runtime catalog payload length: {len(encoded)}")
    raw = bz2.decompress(base64.b64decode(encoded, validate=True))
    catalog = json.loads(raw.decode("utf-8"))
    if catalog.get("schema_version") != "v0.04-r4.2-b15-preview":
        raise ValueError(f"Unexpected R4.2 runtime catalog version: {catalog.get('schema_version')}")
    return catalog


_RUNTIME_CATALOG = _load_catalog()
CATALOG_SCHEMA_VERSION = _RUNTIME_CATALOG["schema_version"]
CATALOG_SOURCE_DATABASE = _RUNTIME_CATALOG.get("source_database")

B28_ADDITIONS_FILE = "runtime_catalog_v004_r4_2_b28_additions.json"

def _load_b28_additions():
    path = Path(__file__).parent / B28_ADDITIONS_FILE
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "v0.04-r4.2-b28-additions-5":
        raise ValueError(f"Unexpected B28 additions version: {payload.get('schema_version')}")
    return payload

_B28_ADDITIONS = _load_b28_additions()
CATALOG_ADDITIONS_SCHEMA_VERSION = _B28_ADDITIONS["schema_version"]

# tw-063 翟山坑道 was removed from the product photography catalog in B26.
# B28 Batch 1 layers newly curated P0 Places onto the stable B15 payload while
# keeping IDs stable; a later full catalog regeneration can collapse this layer.
RETIRED_SPOT_IDS = {"tw-063"}
_COMPOSITE_SPOTS = list(_RUNTIME_CATALOG.get("spots", [])) + list(_B28_ADDITIONS.get("spots", []))
_ACTIVE_SPOTS = [
    spot for spot in _COMPOSITE_SPOTS
    if spot.get("spot_id") not in RETIRED_SPOT_IDS
]
CATALOG_COUNTS = {
    "spots": len(_ACTIVE_SPOTS),
    "opportunities": sum(len(spot.get("opportunities", [])) for spot in _ACTIVE_SPOTS),
    "condition_variants": sum(
        len(opportunity.get("condition_variants", []))
        for spot in _ACTIVE_SPOTS
        for opportunity in spot.get("opportunities", [])
    ),
    "profile_viewpoint_relations": sum(
        len(opportunity.get("viewpoints", []))
        for spot in _ACTIVE_SPOTS
        for opportunity in spot.get("opportunities", [])
    ),
}

CURATED_OPPORTUNITIES = {
    spot["spot_id"]: spot.get("opportunities", [])
    for spot in _ACTIVE_SPOTS
}


def runtime_policy(opportunity):
    """Return the safe runtime action for a curated Opportunity.

    This deliberately has no legacy Theme-score fallback. Missing modules,
    explicit holds, and insufficient data remain visible blockers until the
    corresponding runtime dependency is implemented and tested.
    """
    status = str(opportunity.get("formula_status") or "")
    if status.startswith("access_hold_") or status.endswith("_hold") or "_hold_" in status:
        return "hold"
    if status.startswith("data_insufficient_"):
        return "data_insufficient"
    if status == "prototype_formula_available":
        return "prototype_pending_certification"
    if supports_runtime_contract(opportunity):
        return "preview_module_available"
    if status.startswith("needs_"):
        return "module_pending"
    return "unclassified"


def get_opportunities(region_key, spot_id):
    """Return curated Opportunities for one Place, including runtime policy."""
    if region_key != "tw":
        return []
    opportunities = deepcopy(CURATED_OPPORTUNITIES.get(spot_id, []))
    for opportunity in opportunities:
        opportunity["runtime_policy"] = runtime_policy(opportunity)
        opportunity["runtime_dependency_state"] = dependency_state(opportunity)
    return opportunities


def merge_legacy_themes(themes, opportunities):
    """Preserve schema-9 legacy UI labels while the R4 scorer is built.

    This function is additive for backward compatibility only. It must not be
    interpreted as permission to score an Opportunity whose runtime_policy is
    hold, data_insufficient, or module_pending with a generic Theme formula.
    """
    merged = set(themes or [])
    for opportunity in opportunities or []:
        theme = opportunity.get("legacy_theme")
        if theme:
            merged.add(theme)
    return sorted(merged)


def validate_curated_opportunities():
    errors = []
    opportunity_ids = set()
    variant_ids = set()
    viewpoint_relations = 0

    expected_spots = {f"tw-{i:03d}" for i in range(1, 82)} - RETIRED_SPOT_IDS
    actual_spots = set(CURATED_OPPORTUNITIES)
    if actual_spots != expected_spots:
        errors.append(
            f"expected active Taiwan spot keys excluding retired IDs; missing={sorted(expected_spots-actual_spots)} "
            f"extra={sorted(actual_spots-expected_spots)}"
        )

    for spot_id, opportunities in CURATED_OPPORTUNITIES.items():
        if not spot_id.startswith("tw-"):
            errors.append(f"{spot_id}: Taiwan catalog key expected")
        if not opportunities:
            errors.append(f"{spot_id}: at least one curated Opportunity expected")

        for opportunity in opportunities:
            oid = opportunity.get("opportunity_id")
            if not oid:
                errors.append(f"{spot_id}: missing opportunity_id")
                continue
            if oid in opportunity_ids:
                errors.append(f"{spot_id}: duplicate opportunity_id {oid}")
            opportunity_ids.add(oid)

            if opportunity.get("spot_id") != spot_id:
                errors.append(f"{oid}: spot_id mismatch {opportunity.get('spot_id')} != {spot_id}")

            mode = opportunity.get("mode")
            topology = opportunity.get("sampling_topology")
            if mode not in VALID_MODES:
                errors.append(f"{oid}: invalid mode {mode}")
            if topology not in VALID_TOPOLOGIES:
                errors.append(f"{oid}: invalid topology {topology}")

            geometry_required = bool(opportunity.get("geometry_required"))
            if mode == "composition_specific" and not geometry_required:
                errors.append(f"{oid}: composition_specific must require geometry")
            if topology == "exact_alignment" and (mode != "composition_specific" or not geometry_required):
                errors.append(f"{oid}: exact_alignment contract invalid")
            if mode == "area_opportunity" and geometry_required:
                errors.append(f"{oid}: area_opportunity cannot require exact geometry")

            confidence = opportunity.get("formula_confidence")
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 100:
                errors.append(f"{oid}: invalid formula_confidence {confidence}")

            status = str(opportunity.get("formula_status") or "")
            version = str(opportunity.get("formula_version") or "")
            if status == "legacy_fallback_pending_curated":
                errors.append(f"{oid}: legacy fallback forbidden after B14")
            if version.startswith("legacy_"):
                errors.append(f"{oid}: legacy formula version forbidden after B15")
            if runtime_policy(opportunity) == "unclassified":
                errors.append(f"{oid}: formula_status has no safe runtime policy: {status}")

            variants = opportunity.get("condition_variants") or []
            if not variants:
                errors.append(f"{oid}: missing Condition Variant")
            for variant in variants:
                vid = variant.get("variant_id")
                if not vid:
                    errors.append(f"{oid}: missing variant_id")
                elif vid in variant_ids:
                    errors.append(f"{oid}: duplicate variant_id {vid}")
                else:
                    variant_ids.add(vid)

            viewpoints = opportunity.get("viewpoints") or []
            if not viewpoints:
                errors.append(f"{oid}: missing profile_viewpoint relation")
            viewpoint_relations += len(viewpoints)

    if len(opportunity_ids) != 189:
        errors.append(f"expected 189 opportunities, got {len(opportunity_ids)}")
    if len(variant_ids) != 199:
        errors.append(f"expected 199 variants, got {len(variant_ids)}")
    if viewpoint_relations != 194:
        errors.append(f"expected 194 profile_viewpoint relations, got {viewpoint_relations}")

    exact = {
        opportunity["opportunity_id"]
        for opportunities in CURATED_OPPORTUNITIES.values()
        for opportunity in opportunities
        if opportunity.get("geometry_required")
    }
    expected_exact = {"tw-017-P01", "tw-028-P04", "tw-038-P02"}
    if exact != expected_exact:
        errors.append(f"exact geometry regression: {sorted(exact)}")

    return errors


_ADAPTER_ERRORS = validate_curated_opportunities()
if _ADAPTER_ERRORS:
    raise ValueError("Invalid v0.04 R4.2 Opportunity adapter: " + "; ".join(_ADAPTER_ERRORS))
