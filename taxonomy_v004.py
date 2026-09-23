"""ChaseLights v0.04 R4.2 taxonomy and post-review product-catalog policy.

R4 product policy now has 70 active Taiwan Places. tw-063 翟山坑道 was retired
in B26 after product-quality review concluded it is not strong enough as a
dedicated landscape-photography destination. Dynamic closures of otherwise
strong Places remain runtime state rather than retirement.
"""

TAXONOMY_VERSION = "v0.04-r4.2-b26-preview"

SCENE_TYPES_V004 = {
    "mountain", "coast", "lake", "river", "wetland", "waterfall",
    "forest", "geology", "grassland", "rural", "cityscape", "architecture",
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
    "long_exposure", "telephoto_compression", "panorama", "light_trails",
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

PRODUCT_STATUS_BY_SPOT = {"tw-063": "retired"}


def product_status(spot_id):
    return PRODUCT_STATUS_BY_SPOT.get(spot_id, "keep")


def active_in_catalog(spot_id):
    return product_status(spot_id) != "retired"


def validate_taxonomy():
    errors = []
    valid_status = {"keep", "review", "exit_candidate", "retired"}
    for spot_id, status in PRODUCT_STATUS_BY_SPOT.items():
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
    raise ValueError("Invalid v0.04 R4.2 taxonomy: " + "; ".join(_ERRORS))
