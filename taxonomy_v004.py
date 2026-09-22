"""ChaseLights v0.04 R4 content taxonomy and product-catalog policy.

Scene = stable physical environment.
Opportunity = curated photographic outcome.
Condition modules = forecastable/observable conditions.
Technique = optional shooting method, never a weather Theme.

Legacy themes remain runtime compatibility labels only.
"""

TAXONOMY_VERSION = "v0.04-r4-preview"

SCENE_TYPES_V004 = {
    "mountain",
    "coast",
    "lake",
    "river",
    "wetland",
    "waterfall",
    "forest",
    "geology",
    "grassland",
    "rural",
    "cityscape",
    "architecture",
}

CONDITION_FAMILIES = {
    "visibility": {"clear_view", "haze", "camera_fog"},
    "solar_light": {"sunrise", "sunset", "blue_hour", "golden_hour", "sky_glow", "sunbeam"},
    "cloud_fog": {"cloud_sea", "fog_mist", "layered_mist"},
    "water_surface": {"reflection", "calm_water"},
    "night_sky": {"night_sky", "milky_way", "moonlight", "moon_alignment"},
    "snow_ice": {"snow_cover", "fresh_snow", "rime"},
    "marine_tide": {"tide_stage", "wave_state", "swell"},
    "seasonal": {"flower_bloom", "foliage", "crop_state", "silvergrass"},
    "timed_event": {"train", "fireworks", "lighting_event"},
    "aurora": {"aurora_activity"},
}

TECHNIQUE_TYPES = {
    "long_exposure",
    "telephoto_compression",
    "panorama",
    "light_trails",
}

LEGACY_THEME_POLICY = {
    "mountain_view": "deprecated_as_theme",
    "sunrise": "condition",
    "sunset": "condition",
    "blue_hour": "condition",
    "sky_glow": "condition",
    "cloud_sea": "condition",
    "fog_mist": "condition",
    "reflection": "condition",
    "sunbeam": "rename_directional_light",
    "milky_way": "subject_condition",
    "long_exposure": "technique",
    "city_night": "deprecated_as_theme",
    "snow_scene": "rename_surface_condition",
    "aurora": "phenomenon",
}

# R4 first-pass conservative catalog triage.
# Stable IDs remain in source/audit history even when hidden from the preview catalog.
PRODUCT_STATUS_BY_SPOT = {
    # Exit candidates: hidden in v0.04 preview UI, not deleted from audit history.
    "tw-052": "exit_candidate",  # 小崗山雲臺
    "tw-058": "exit_candidate",  # 澎湖跨海大橋
    "tw-062": "exit_candidate",  # 水頭聚落・得月樓
    "tw-063": "exit_candidate",  # 翟山坑道

    # Review candidates: remain visible pending targeted photographic-value review.
    "tw-009": "review",
    "tw-016": "review",
    "tw-029": "review",
    "tw-042": "review",
    "tw-048": "review",
    "tw-050": "review",
    "tw-051": "review",
    "tw-066": "review",
}


def product_status(spot_id):
    return PRODUCT_STATUS_BY_SPOT.get(spot_id, "keep")


def active_in_catalog(spot_id):
    return product_status(spot_id) != "exit_candidate"


def validate_taxonomy():
    errors = []
    valid_status = {"keep", "review", "exit_candidate", "retired"}
    for spot_id, status in PRODUCT_STATUS_BY_SPOT.items():
        if not spot_id.startswith("tw-"):
            errors.append(f"{spot_id}: R4 triage currently supports Taiwan only")
        if status not in valid_status:
            errors.append(f"{spot_id}: invalid product status {status}")

    for family, modules in CONDITION_FAMILIES.items():
        if not family or not modules:
            errors.append(f"{family}: empty condition family")

    overlap = TECHNIQUE_TYPES & set().union(*CONDITION_FAMILIES.values())
    if overlap:
        errors.append(f"techniques overlap condition modules: {sorted(overlap)}")
    return errors


_ERRORS = validate_taxonomy()
if _ERRORS:
    raise ValueError("Invalid v0.04 R4 taxonomy: " + "; ".join(_ERRORS))
