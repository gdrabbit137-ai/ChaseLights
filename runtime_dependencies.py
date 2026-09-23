"""Formal dependency inventory for ChaseLights R4.2 Opportunity formulas.

This module separates content formula status from runtime implementation state.
Every needs_* status maps to an explicit set of reusable runtime components.
"""

DEPENDENCY_INVENTORY_VERSION = "r4.2-b25-deps-v7"

FORMULA_DEPENDENCIES = {
    "needs_spatial_weather_module": ("spatial_weather_vertical_cloud",),
    "needs_directional_horizon_module": ("directional_horizon",),
    "needs_directional_horizon_dynamic_access_module": ("directional_horizon", "dynamic_access"),
    "needs_lighting_state_module": ("managed_lighting_state",),
    "needs_marine_directional_horizon_module": ("marine_state", "directional_horizon"),
    "needs_marine_tide_module": ("marine_state", "tide_state"),
    "needs_lighting_water_surface_module": ("managed_lighting_state", "water_surface_state"),
    "needs_tide_directional_horizon_module": ("tide_state", "directional_horizon"),
    "needs_dynamic_access_directional_horizon_module": ("dynamic_access", "directional_horizon"),
    "needs_dynamic_access_visibility_module": ("dynamic_access", "visibility"),
    "needs_snow_state_module": ("snow_state",),
    "needs_spatial_weather_dynamic_access_module": ("spatial_weather_vertical_cloud", "dynamic_access"),
    "needs_water_surface_module": ("water_surface_state",),
    "needs_astronomy_ephemeris_access_module": ("astronomy_ephemeris", "dynamic_access"),
    "needs_directional_horizon_visibility_module": ("directional_horizon", "visibility"),
    "needs_radiation_cloud_module": ("radiation_DNI", "cloud_sky_glow"),
    "needs_astronomy_ephemeris_module": ("astronomy_ephemeris",),
    "needs_geology_light_visibility_module": ("geology_light", "visibility"),
    "needs_lake_level_water_surface_access_module": ("lake_water_level", "water_surface_state", "dynamic_access"),
    "needs_seasonal_foreground_module": ("seasonal_foreground",),
    "needs_seasonal_foreground_tide_marine_directional_horizon_module": ("seasonal_foreground", "tide_state", "marine_state", "directional_horizon"),
    "needs_tide_water_surface_access_module": ("tide_state", "water_surface_state", "dynamic_access"),
    "needs_event_state_access_module": ("event_state", "dynamic_access"),
    "needs_marine_directional_horizon_dynamic_access_module": ("marine_state", "directional_horizon", "dynamic_access"),
    "needs_geometry_aware_ephemeris_adapter": ("directional_horizon", "verified_camera_geometry"),
    "needs_radiation_module": ("radiation_DNI", "cloud_light_state"),
    "needs_directional_horizon_cloud_sky_glow_module": ("directional_horizon", "cloud_sky_glow"),
    "needs_astronomy_ephemeris_marine_module": ("astronomy_ephemeris", "marine_state"),
    "needs_timetable_access_module": ("timetable", "dynamic_access"),
    "needs_directional_horizon_access_water_surface_module": ("directional_horizon", "dynamic_access", "water_surface_state"),
    "needs_exact_milky_way_geometry_access_light_state": ("astronomy_ephemeris", "verified_camera_geometry", "dynamic_access", "managed_lighting_state"),
    "needs_astronomy_ephemeris_water_surface_access_module": ("astronomy_ephemeris", "water_surface_state", "dynamic_access"),
    "needs_waterfall_flow_module": ("waterfall_flow",),
    "needs_waterfall_flow_mist_module": ("waterfall_flow", "mist_state"),
    "needs_waterfall_flow_dynamic_access_module": ("waterfall_flow", "dynamic_access"),
    "needs_lake_level_mist_access_module": ("lake_water_level", "mist_state", "dynamic_access"),
    "needs_tide_access_module": ("tide_state", "dynamic_access"),
    "needs_tide_module": ("tide_state",),
    "needs_directional_horizon_wildlife_module": ("directional_horizon", "wildlife_state"),
    "needs_directional_horizon_cultural_permission_module": ("directional_horizon", "cultural_permission"),
}

KNOWN_COMPONENTS = {
    "astronomy_ephemeris",
    "cloud_sky_glow",
    "cloud_light_state",
    "cultural_permission",
    "directional_horizon",
    "dynamic_access",
    "event_state",
    "geology_light",
    "lake_water_level",
    "managed_lighting_state",
    "marine_state",
    "mist_state",
    "radiation_DNI",
    "seasonal_foreground",
    "snow_state",
    "spatial_weather_vertical_cloud",
    "tide_state",
    "timetable",
    "verified_camera_geometry",
    "visibility",
    "water_surface_state",
    "waterfall_flow",
    "wildlife_state",
}

SPECIAL_NON_MODULE_STATUSES = {
    "prototype_formula_available",
    "access_hold_construction",
    "access_hold_current_hours_night_bioluminescence",
    "data_insufficient_geometry",
}

# Formula status is intentionally broad; these profiles need narrower contracts.
# In particular, post-sunset sky-glow must not require positive DNI.
OPPORTUNITY_DEPENDENCY_OVERRIDES = {
    "tw-013-P02": ("radiation_DNI", "cloud_sky_glow"),
    "tw-026-P02": ("cloud_sky_glow",),
    "tw-030-P02": ("cloud_sky_glow",),
    "tw-020-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
    "tw-024-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
    "tw-043-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
    "tw-047-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
}


def dependencies_for_status(formula_status):
    return FORMULA_DEPENDENCIES.get(str(formula_status or ""), ())


def dependencies_for_opportunity(opportunity):
    oid = opportunity.get("opportunity_id")
    if oid in OPPORTUNITY_DEPENDENCY_OVERRIDES:
        return OPPORTUNITY_DEPENDENCY_OVERRIDES[oid]
    return dependencies_for_status(opportunity.get("formula_status"))


def validate_dependency_inventory(known_formula_statuses=None):
    errors = []
    for oid, dependencies in OPPORTUNITY_DEPENDENCY_OVERRIDES.items():
        if not str(oid).startswith("tw-"):
            errors.append(f"{oid}: invalid opportunity override id")
        if not dependencies:
            errors.append(f"{oid}: empty opportunity dependency override")
        unknown = sorted(set(dependencies) - KNOWN_COMPONENTS)
        if unknown:
            errors.append(f"{oid}: unknown override components {unknown}")

    for status, dependencies in FORMULA_DEPENDENCIES.items():
        if not status.startswith("needs_"):
            errors.append(f"{status}: dependency status must start with needs_")
        if not dependencies:
            errors.append(f"{status}: empty dependency set")
        if len(set(dependencies)) != len(dependencies):
            errors.append(f"{status}: duplicate dependency")
        unknown = sorted(set(dependencies) - KNOWN_COMPONENTS)
        if unknown:
            errors.append(f"{status}: unknown components {unknown}")

    if known_formula_statuses is not None:
        known = set(known_formula_statuses)
        needs = {status for status in known if str(status).startswith("needs_")}
        missing = sorted(needs - set(FORMULA_DEPENDENCIES))
        extra = sorted(set(FORMULA_DEPENDENCIES) - needs)
        if missing:
            errors.append(f"missing dependency mappings: {missing}")
        if extra:
            errors.append(f"dependency mappings not present in catalog: {extra}")

        unexplained = sorted(
            known - set(FORMULA_DEPENDENCIES) - SPECIAL_NON_MODULE_STATUSES
        )
        if unexplained:
            errors.append(f"unclassified formula statuses: {unexplained}")

    return errors


_ERRORS = validate_dependency_inventory()
if _ERRORS:
    raise ValueError("Invalid R4.2 dependency inventory: " + "; ".join(_ERRORS))
