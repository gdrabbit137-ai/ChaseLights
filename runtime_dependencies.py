"""Formal dependency inventory for ChaseLights R4.2 Opportunity formulas.

This module separates content formula status from runtime implementation state.
Every needs_* status maps to an explicit set of reusable runtime components.
"""

DEPENDENCY_INVENTORY_VERSION = "r4.2-b79-deps-v18-aurora-runtime"

FORMULA_DEPENDENCIES = {
    "needs_visibility_module": ("visibility",),
    "needs_aurora_state_module": ("aurora_state",),
    "needs_aurora_state_dynamic_access_module": ("aurora_state", "dynamic_access"),
    "needs_dynamic_access_module": ("dynamic_access",),
    "needs_radiation_dynamic_access_module": ("radiation_DNI", "cloud_light_state", "dynamic_access"),
    "needs_spatial_weather_module": ("spatial_weather_vertical_cloud",),
    "needs_directional_horizon_module": ("directional_horizon",),
    "needs_directional_horizon_dynamic_access_module": ("directional_horizon", "dynamic_access"),
    "needs_lighting_state_module": ("managed_lighting_state",),
    "needs_marine_directional_horizon_module": ("marine_state", "directional_horizon"),
    "needs_marine_tide_module": ("marine_state", "tide_state"),
    "needs_lighting_water_surface_module": ("managed_lighting_state", "water_surface_state"),
    "needs_tide_directional_horizon_module": ("tide_state", "directional_horizon"),
    "needs_dynamic_access_directional_horizon_module": ("dynamic_access", "directional_horizon"),
    "needs_dynamic_access_directional_horizon_visibility_module": ("dynamic_access", "directional_horizon", "visibility"),
    "needs_dynamic_access_visibility_module": ("dynamic_access", "visibility"),
    "needs_snow_state_module": ("snow_state",),
    "needs_spatial_weather_dynamic_access_module": ("spatial_weather_vertical_cloud", "dynamic_access"),
    "needs_water_surface_module": ("water_surface_state",),
    "needs_water_surface_visibility_module": ("water_surface_state", "visibility"),
    "needs_geothermal_steam_visibility_access_module": ("geothermal_steam_state", "visibility", "dynamic_access"),
    "needs_astronomy_ephemeris_access_module": ("astronomy_ephemeris", "dynamic_access"),
    "needs_directional_horizon_visibility_module": ("directional_horizon", "visibility"),
    "needs_radiation_cloud_module": ("radiation_DNI", "cloud_sky_glow"),
    "needs_astronomy_ephemeris_module": ("astronomy_ephemeris",),
    "needs_geology_light_visibility_module": ("geology_light", "visibility"),
    "needs_lake_level_water_surface_access_module": ("lake_water_level", "water_surface_state", "dynamic_access"),
    "needs_seasonal_foreground_module": ("seasonal_foreground",),
    "needs_seasonal_foreground_tide_marine_directional_horizon_module": ("seasonal_foreground", "tide_state", "marine_state", "directional_horizon"),
    "needs_tide_water_surface_access_module": ("tide_state", "water_surface_state", "dynamic_access"),
    "needs_event_state_module": ("event_state",),
    "needs_event_state_access_module": ("event_state", "dynamic_access"),
    "needs_marine_tide_directional_horizon_access_module": ("marine_state", "tide_state", "directional_horizon", "dynamic_access"),
    "needs_marine_directional_horizon_dynamic_access_module": ("marine_state", "directional_horizon", "dynamic_access"),
    "needs_geometry_aware_ephemeris_adapter": ("directional_horizon", "verified_camera_geometry"),
    "needs_radiation_module": ("radiation_DNI", "cloud_light_state"),
    "needs_directional_horizon_cloud_sky_glow_module": ("directional_horizon", "cloud_sky_glow"),
    "needs_liushishishan_sunbeam_cloud_geometry": ("directional_horizon", "cloud_light_state", "verified_camera_geometry"),
    "needs_astronomy_ephemeris_marine_module": ("astronomy_ephemeris", "marine_state"),
    "needs_timetable_access_module": ("timetable", "dynamic_access"),
    "needs_directional_horizon_access_water_surface_module": ("directional_horizon", "dynamic_access", "water_surface_state"),
    "needs_exact_milky_way_geometry_access_light_state": ("astronomy_ephemeris", "verified_camera_geometry", "dynamic_access", "managed_lighting_state"),
    "needs_astronomy_ephemeris_water_surface_access_module": ("astronomy_ephemeris", "water_surface_state", "dynamic_access"),
    "needs_waterfall_flow_module": ("waterfall_flow",),
    "needs_waterfall_flow_mist_module": ("waterfall_flow", "mist_state"),
    "needs_waterfall_flow_dynamic_access_module": ("waterfall_flow", "dynamic_access"),
    "needs_lake_level_mist_access_module": ("lake_water_level", "mist_state", "dynamic_access"),
    "needs_mist_state_module": ("mist_state",),
    "needs_tide_access_module": ("tide_state", "dynamic_access"),
    "needs_tide_module": ("tide_state",),
    "needs_tidal_current_extremum_access_module": ("tidal_current_extremum", "dynamic_access"),
    "needs_directional_horizon_wildlife_module": ("directional_horizon", "wildlife_state"),
    "needs_wildlife_state_access_module": ("wildlife_state", "dynamic_access"),
    "needs_directional_horizon_cultural_permission_module": ("directional_horizon", "cultural_permission"),
}

KNOWN_COMPONENTS = {
    "astronomy_ephemeris",
    "aurora_state",
    "cloud_sky_glow",
    "cloud_light_state",
    "cultural_permission",
    "directional_horizon",
    "dynamic_access",
    "event_state",
    "geology_light",
    "geothermal_steam_state",
    "lake_water_level",
    "managed_lighting_state",
    "marine_state",
    "mist_state",
    "radiation_DNI",
    "seasonal_foreground",
    "snow_state",
    "spatial_weather_vertical_cloud",
    "tide_state",
    "tidal_current_extremum",
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
    "access_hold_current_photography_not_accepted",
    "minimum_sufficient_local_scene",
    "data_insufficient_geometry",
    # B32 Japan: Blue Pond research is complete, but current weather providers
    # cannot establish whether the pond is actually blue/turbid or snow-covered.
    "data_insufficient_blue_water_state",
}

# Formula status is intentionally broad; these profiles need narrower contracts.
# In particular, post-sunset sky-glow must not require positive DNI.
OPPORTUNITY_DEPENDENCY_OVERRIDES = {
    # B30: these researched B28 profiles explicitly require the subject/horizon
    # to remain visible. Visibility is therefore part of the scoring contract,
    # not merely a descriptive penalty in the Place Guide.
    "tw-033-P01": ("marine_state", "directional_horizon", "visibility"),
    "tw-033-P02": ("marine_state", "directional_horizon", "visibility"),
    "tw-036-P01": ("marine_state", "directional_horizon", "visibility"),
    "tw-072-P01": ("marine_state", "directional_horizon", "visibility"),
    "tw-072-P02": ("marine_state", "directional_horizon", "visibility"),
    "tw-073-P01": ("seasonal_foreground", "tide_state", "marine_state", "directional_horizon", "visibility"),
    "tw-075-P01": ("marine_state", "directional_horizon", "visibility"),
    "tw-077-P01": ("marine_state", "directional_horizon", "visibility"),
    "tw-077-P02": ("marine_state", "tide_state", "visibility"),
    "tw-079-P01": ("marine_state", "directional_horizon", "visibility"),
    "tw-079-P02": ("marine_state", "tide_state", "visibility"),
    "tw-013-P02": ("radiation_DNI", "cloud_sky_glow", "visibility"),
    "tw-026-P02": ("cloud_sky_glow",),
    "tw-030-P02": ("cloud_sky_glow",),
    "tw-020-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
    "tw-024-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
    "tw-043-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
    "tw-047-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
}


# Explicit profile-configuration gaps for implemented components.
# These are not magic counts: each ID is a known catalog dependency that
# intentionally has no configured runtime profile yet. Adapter tests assert
# registered profiles + these gaps exactly cover canonical dependencies.
RUNTIME_PROFILE_GAPS = {
    "seasonal_foreground": frozenset({
        "tw-085-P03",
    }),
    "spatial_weather_vertical_cloud": frozenset({
        "jp-002-P01",
        "tw-021-P02",
        "tw-025-P01", "tw-025-P02",
        "tw-026-P01",
        "tw-032-P03",
    }),
    "directional_horizon": frozenset({
        "tw-005-P01", "tw-010-P02",
        "tw-019-P01", "tw-019-P02",
        "tw-021-P01", "tw-024-P01", "tw-028-P04",
        "tw-034-P01", "tw-035-P09", "tw-038-P01",
        "tw-040-P01", "tw-040-P05",
        "tw-041-P02", "tw-041-P04", "tw-043-P04",
        "tw-045-P01", "tw-045-P04", "tw-049-P02",
        "tw-064-P01", "tw-068-P01", "tw-069-P01",
        "tw-085-P01", "tw-085-P02",
    }),
}


# Configured profiles that intentionally remain runtime-not-ready because an
# external prerequisite is missing. Keep these separate from RUNTIME_PROFILE_GAPS,
# which means no component profile is configured at all.
RUNTIME_READINESS_GAPS = {
    "dynamic_access": frozenset({
        "jp-036-P03",
    }),
    "spatial_weather_vertical_cloud": frozenset({
        # The Alishan boardwalk Camera Zone is researched as a linear zone but
        # still lacks an exact lat/lon anchor required by the spatial sampler.
        "tw-032-P02",
    }),
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

    for component, opportunity_ids in RUNTIME_PROFILE_GAPS.items():
        if component not in KNOWN_COMPONENTS:
            errors.append(f"{component}: unknown runtime profile gap component")
        if not opportunity_ids:
            errors.append(f"{component}: empty runtime profile gap set")
        for oid in opportunity_ids:
            if not str(oid).startswith(("tw-", "jp-", "us-")):
                errors.append(f"{component}: invalid runtime profile gap id {oid}")

    for component, opportunity_ids in RUNTIME_READINESS_GAPS.items():
        if component not in KNOWN_COMPONENTS:
            errors.append(f"{component}: unknown runtime readiness gap component")
        if not opportunity_ids:
            errors.append(f"{component}: empty runtime readiness gap set")
        overlap = set(opportunity_ids) & set(RUNTIME_PROFILE_GAPS.get(component, ()))
        if overlap:
            errors.append(f"{component}: profile/readiness gaps overlap {sorted(overlap)}")
        for oid in opportunity_ids:
            if not str(oid).startswith(("tw-", "jp-", "us-")):
                errors.append(f"{component}: invalid runtime readiness gap id {oid}")

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
