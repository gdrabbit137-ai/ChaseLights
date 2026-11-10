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

PRODUCT_STATUS_BY_SPOT = {
    "tw-063": "retired",
    # CL-DATA-25R (2026-11-07, rubric v2 alignment): v1-built but v2-rejected places
    # (<3.8) retired from the product catalog; ids stay reserved (positional spot_id
    # stability), dossiers move to the Excel side list.
    "jp-050": "retired",   # 安比高原雲海ゴンドラ (v2 3.30)
    "tw-090": "retired",   # 加路蘭海岸遊憩區 (v2 3.70)
    "tw-092": "retired",   # 北關海潮公園 (v2 3.60)
    "tw-096": "retired",   # 半天寮好望角 (v2 3.70)
    "tw-097": "retired",   # 擎天崗草原 (v2 3.20)
    # CL-DATA-62 (owner 裁決 2026-11-10 適拍性審計，依 CL-DATA-61 審計名單)：
    # 適拍性不足退役；ids 保留（positional spot_id 穩定），regions.py tuple 不動，
    # 各 catalog/runtime surface 隱藏。
    "tw-068": "retired",   # 綠島朝日溫泉 (retire-onsen)
    "tw-083": "retired",   # 雲山水 (retire-small)
    "tw-084": "retired",   # 大農大富平地森林園區 (retire-small)
    "us-075": "retired",   # 探索公園 Discovery Park (retire-small)
    "us-076": "retired",   # 漢密爾頓 Hamilton (retire-small)
    "us-077": "retired",   # 黎剎 Rizal Park (retire-small)
}


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
