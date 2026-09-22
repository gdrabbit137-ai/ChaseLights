"""ChaseLights v0.04 Opportunity compatibility adapter.

Preview-only bridge between the current Place + Theme runtime and the v0.04
Place -> Photography Opportunity -> Condition Variant model.

Important:
- This file does NOT change the public weather JSON schema.
- Legacy themes remain available for the existing UI.
- Only manually reviewed opportunities are listed here.
- Unreviewed places continue to use the V5.4 theme fallback unchanged.
"""

ADAPTER_VERSION = "v0.04-r3-preview"

VALID_MODES = {"area_opportunity", "composition_specific"}
VALID_TOPOLOGIES = {
    "local_area",
    "area_plus_environment",
    "directional_sector",
    "exact_alignment",
}

# R2 representative classification only. Do not extrapolate by theme.
CURATED_OPPORTUNITIES = {
    "tw-001": [
        {
            "opportunity_id": "tw-001-P01",
            "name_zh": "大屯夕照與芒草",
            "legacy_theme": "sunset",
            "mode": "area_opportunity",
            "sampling_topology": "directional_sector",
            "geometry_required": False,
            "formula_status": "legacy_fallback_pending_curated",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 55,
        },
        {
            "opportunity_id": "tw-001-P02",
            "name_zh": "大屯雲海／琉璃光",
            "legacy_theme": "cloud_sea",
            "mode": "area_opportunity",
            "sampling_topology": "area_plus_environment",
            "geometry_required": False,
            "formula_status": "prototype_formula_available",
            "formula_version": "photo_first_r3",
            "formula_confidence": 66,
        },
        {
            "opportunity_id": "tw-001-P03",
            "name_zh": "台北盆地藍調／夜景",
            "legacy_theme": "city_night",
            "mode": "area_opportunity",
            "sampling_topology": "area_plus_environment",
            "geometry_required": False,
            "formula_status": "legacy_fallback_pending_curated",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 60,
        },
    ],
    "tw-035": [
        {
            "opportunity_id": "tw-035-P01",
            "name_zh": "六十石山縱谷層巒遠眺",
            "legacy_theme": "mountain_view",
            "mode": "area_opportunity",
            "sampling_topology": "area_plus_environment",
            "geometry_required": False,
            "formula_status": "needs_seasonal_foreground_module",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 50,
        },
        {
            "opportunity_id": "tw-035-P02",
            "name_zh": "六十石山雲隙光",
            "legacy_theme": "sunbeam",
            "mode": "area_opportunity",
            "sampling_topology": "directional_sector",
            "geometry_required": False,
            "formula_status": "needs_radiation_module",
            "formula_version": "photo_first_r3",
            "formula_confidence": 56,
        },
        {
            "opportunity_id": "tw-035-P03",
            "name_zh": "六十石山夕照",
            "legacy_theme": "sunset",
            "mode": "area_opportunity",
            "sampling_topology": "directional_sector",
            "geometry_required": False,
            "formula_status": "legacy_fallback_pending_curated",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 55,
        },
        {
            "opportunity_id": "tw-035-P04",
            "name_zh": "六十石山彩霞",
            "legacy_theme": "sky_glow",
            "mode": "area_opportunity",
            "sampling_topology": "directional_sector",
            "geometry_required": False,
            "formula_status": "legacy_fallback_pending_curated",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 55,
        },
        {
            "opportunity_id": "tw-035-P05",
            "name_zh": "六十石山銀河",
            "legacy_theme": "milky_way",
            "mode": "area_opportunity",
            "sampling_topology": "local_area",
            "geometry_required": False,
            "formula_status": "legacy_fallback_pending_curated",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 65,
        },
        {
            "opportunity_id": "tw-035-P06",
            "name_zh": "六十石山雲海",
            "legacy_theme": "cloud_sea",
            "mode": "area_opportunity",
            "sampling_topology": "area_plus_environment",
            "geometry_required": False,
            "formula_status": "needs_spatial_weather_module",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 50,
        },
    ],
    "tw-038": [
        {
            "opportunity_id": "tw-038-P01",
            "name_zh": "三仙台日出",
            "legacy_theme": "sunrise",
            "mode": "area_opportunity",
            "sampling_topology": "directional_sector",
            "geometry_required": False,
            "formula_status": "access_hold_construction",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 60,
        },
        {
            "opportunity_id": "tw-038-P02",
            "name_zh": "三仙台銀河",
            "legacy_theme": "milky_way",
            "mode": "composition_specific",
            "sampling_topology": "exact_alignment",
            "geometry_required": True,
            "formula_status": "geometry_pending_construction_hold",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 45,
        },
    ],
    "tw-046": [
        {
            "opportunity_id": "tw-046-P01",
            "name_zh": "中霸坪大小霸經典遠眺",
            "legacy_theme": "mountain_view",
            "mode": "area_opportunity",
            "sampling_topology": "area_plus_environment",
            "geometry_required": False,
            "formula_status": "legacy_fallback_pending_curated",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 70,
        },
        {
            "opportunity_id": "tw-046-P02",
            "name_zh": "霸基近距離大霸峰體",
            "legacy_theme": "mountain_view",
            "mode": "area_opportunity",
            "sampling_topology": "local_area",
            "geometry_required": False,
            "formula_status": "legacy_fallback_pending_curated",
            "formula_version": "legacy_v5_4",
            "formula_confidence": 65,
        },
    ],
}


def get_opportunities(region_key, spot_id):
    """Return manually reviewed opportunities for one place."""
    if region_key != "tw":
        return []
    return [dict(x) for x in CURATED_OPPORTUNITIES.get(spot_id, [])]


def merge_legacy_themes(themes, opportunities):
    """Keep legacy UI themes while ensuring curated opportunities remain addressable.

    This is intentionally additive. R3 does not remove legacy themes because
    unreviewed opportunities still rely on V5.4 fallback behavior.
    """
    merged = set(themes or [])
    for opportunity in opportunities or []:
        theme = opportunity.get("legacy_theme")
        if theme:
            merged.add(theme)
    return sorted(merged)


def runtime_policy(opportunity):
    """Map curation state to an adapter action without changing score semantics."""
    status = opportunity.get("formula_status")
    if status in {"access_hold_construction", "geometry_pending_construction_hold"}:
        return "hold"
    if status == "prototype_formula_available":
        return "prototype_pending_runtime_inputs"
    if status and status.startswith("needs_"):
        return "module_pending"
    return "legacy_fallback"


def validate_curated_opportunities():
    errors = []
    ids = set()
    for spot_id, opportunities in CURATED_OPPORTUNITIES.items():
        if not spot_id.startswith("tw-"):
            errors.append(f"{spot_id}: curated R3 sample must be Taiwan")
        for opportunity in opportunities:
            oid = opportunity.get("opportunity_id")
            if not oid:
                errors.append(f"{spot_id}: missing opportunity_id")
            elif oid in ids:
                errors.append(f"{spot_id}: duplicate opportunity_id {oid}")
            else:
                ids.add(oid)

            mode = opportunity.get("mode")
            topology = opportunity.get("sampling_topology")
            if mode not in VALID_MODES:
                errors.append(f"{oid}: invalid mode {mode}")
            if topology not in VALID_TOPOLOGIES:
                errors.append(f"{oid}: invalid topology {topology}")

            geometry_required = bool(opportunity.get("geometry_required"))
            if mode == "composition_specific" and not geometry_required:
                errors.append(f"{oid}: composition_specific must require geometry")
            if topology == "exact_alignment" and not geometry_required:
                errors.append(f"{oid}: exact_alignment must require geometry")
            if mode == "area_opportunity" and geometry_required:
                errors.append(f"{oid}: area_opportunity must not require exact geometry in R3")

            confidence = opportunity.get("formula_confidence")
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 100:
                errors.append(f"{oid}: invalid formula_confidence {confidence}")
    return errors


_ADAPTER_ERRORS = validate_curated_opportunities()
if _ADAPTER_ERRORS:
    raise ValueError("Invalid v0.04 opportunity adapter: " + "; ".join(_ADAPTER_ERRORS))
