"""CL-DATA-80 Stage 1: mechanical migration of the 720+ condition contracts to the
QUALITY-engine v2 shape (spec: data/v2/audits/spec-quality-engine.md §3–§5).

For every data/v2/opportunities/*.json contract this script derives, WITHOUT touching
the legacy `conditions` array (source of truth for the --legacy-engine boolean path):

  condition_contract.windows        = {"time_of_day": [...], "seasonal": ...}
      - REQUIRED/QUALITY time-window metrics -> windows.time_of_day (semantic names)
      - seasonal_state (eq window_open)      -> windows.seasonal = "calendar"
        (resolved at evaluation time from data/v2/seasonal-calendar.json, exactly
         like the legacy bridge — the calendar is never copied into the contract)
  condition_contract.conditions_v2  = {"required": [...], "quality": [...]}

  - REQUIRED non-window, non-state conditions -> required entry
        {"id", "metric", "op", "value"}   (op/value mirror the legacy operator/threshold)
  - REQUIRED derived-state conditions (operator "none") stay gatekeeper members as
        {"id", "metric", "op": "derived_state"} (the engine reuses the legacy
        condition_verdict derivations; only "unfit"-class states veto)
  - QUALITY numeric conditions -> quality entry
        {"id", "metric", "weight", "ideal": [b, c], "acceptable": [a, d], "provisional": bool}
        trapezoid [a,b,c,d] from spec §5 when (template family, metric) has an entry,
        else a conservative wide ladder derived from the condition's own threshold and
        marked provisional=true. Unbounded bounds are encoded as null (= ±inf).
  - QUALITY window metrics (sunset_window, golden_hour_window, ...) are WINDOW
    semantics, not scores -> windows.time_of_day, never a quality entry.

Idempotent: re-running recomputes windows/conditions_v2 from the unchanged legacy
`conditions` array and writes only when the derived block differs (byte-stable reruns).

Usage: python data/v2/migration/contract_v2_migrate.py [--check]
  --check : exit 1 if any file would change (no writes).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP_DIR = ROOT / "data" / "v2" / "opportunities"

# spec §5 tag -> contract genre_template family
TEMPLATE_FAMILY = {
    "sunset": "sunrise_sunset", "sunrise": "sunrise_sunset",
    "overlook": "scenic_lookout", "mountain_view": "mountain_vista",
    "geological_landform": "mountain_vista", "scenic_lookout": "scenic_lookout",
    "mountain_vista": "mountain_vista", "city_night": "city_night",
    "blue_hour_city": "city_night", "reflection": "water_reflection",
    "water_reflection": "water_reflection", "night_sky": "astrophotography",
    "star_trails": "astrophotography", "moonlit_scene": "astrophotography",
    "seasonal_plant": "seasonal_foliage", "seasonal_foliage": "seasonal_foliage",
    "snow_ice": "snow_ice", "snow_scene": "snow_ice", "snow_ice_night": "snow_ice",
    "drift_ice": "snow_ice", "overcast_soft": "overcast_soft_light",
    "overcast_soft_light": "overcast_soft_light", "golden_hour": "golden_hour",
    "alpenglow": "golden_hour", "cloud_sea": "cloud_sea", "volcanic_glow": "golden_hour",
}

# spec §5 (family, metric) -> (weight, [a, b, c, d])
SPEC5 = {
    ("water_reflection", "wind_speed_10m"): (3.0, [0, 0, 0.8, 2.0]),
    ("water_reflection", "golden_hour_window"): (2.0, [0, 1, 1, 1]),
    ("water_reflection", "cloud_cover_total"): (1.5, [0, 20, 50, 75]),
    ("mountain_vista", "cloud_cover_mid"): (2.0, [0, 20, 50, 75]),
    ("mountain_vista", "cloud_cover_mid_and_high"): (2.0, [0, 20, 50, 75]),
    ("mountain_vista", "visibility"): (2.0, [15, 30, None, None]),
    ("mountain_vista", "golden_hour_window"): (1.5, [0, 1, 1, 1]),
    ("mountain_vista", "aod_550nm"): (1.0, [0, 0, 0.15, 0.5]),
    ("sunrise_sunset", "cloud_cover_mid_and_high"): (3.0, [5, 25, 65, 85]),
    ("sunrise_sunset", "cloud_cover_low"): (2.5, [0, 0, 10, 35]),
    ("sunrise_sunset", "aod_550nm"): (1.0, [0, 0.05, 0.25, 0.6]),
    ("golden_hour", "cloud_cover_low"): (2.5, [0, 0, 15, 40]),
    ("golden_hour", "cloud_cover_mid_and_high"): (1.5, [0, 15, 45, 70]),
    ("golden_hour", "aod_550nm"): (1.5, [0, 0, 0.2, 0.5]),
    ("city_night", "blue_hour_window"): (2.5, [0, 1, 1, 1]),
    ("city_night", "visibility"): (2.0, [10, 25, None, None]),
    ("city_night", "aod_550nm"): (1.5, [0, 0, 0.15, 0.5]),
    ("city_night", "wind_speed_10m"): (2.0, [0, 0, 1.0, 2.5]),
    ("astrophotography", "cloud_cover_total"): (3.0, [0, 0, 5, 20]),
    ("astrophotography", "moon_illumination_fraction"): (2.5, [0, 0, 0.05, 0.35]),
    ("astrophotography", "galactic_core_altitude"): (1.5, [25, None, None, None]),
    ("astrophotography", "aod_550nm"): (1.5, [0, 0, 0.1, 0.3]),
    ("seasonal_foliage", "cloud_cover_total"): (2.0, [10, 40, 75, 95]),
    ("seasonal_foliage", "wind_speed_10m"): (2.0, [0, 0, 1.5, 5.0]),
    ("seasonal_foliage", "golden_hour_window"): (1.5, [0, 1, 1, 1]),
    ("snow_ice", "snow_depth_cm"): (3.0, [2, 15, None, None]),
    ("snow_ice", "wind_speed_10m"): (2.0, [0, 0, 2.5, 7.0]),
    ("snow_ice", "golden_hour_window"): (1.5, [0, 1, 1, 1]),
    ("overcast_soft_light", "cloud_cover_total"): (3.0, [70, 85, 100, 100]),
    ("overcast_soft_light", "wind_speed_10m"): (2.0, [0, 0, 1.5, 4.5]),
    ("overcast_soft_light", "precipitation"): (1.5, [0, 0, 0.1, 0.5]),
    ("scenic_lookout", "visibility"): (3.0, [15, 35, None, None]),
    ("scenic_lookout", "aod_550nm"): (2.0, [0, 0, 0.12, 0.4]),
    ("scenic_lookout", "cloud_cover_low"): (1.5, [0, 0, 10, 30]),
}

# Window metrics -> windows.time_of_day semantic names.
WINDOW_METRIC_NAMES = {
    "light_window": "civil_daylight",
    "daylight_window": "civil_daylight",
    "golden_hour_window": "golden_hour",
    "sunset_window": "sunset",
    "sunrise_time_window": "sunrise",
    "blue_hour_window": "blue_hour",
    "astronomical_darkness": "astro_darkness",
    "city_night_window": "city_night",
    "soft_light_window": "soft_light",
    "morning_window": "morning",
    "alpenglow_window": "alpenglow",
    "venue_open_window": "venue_open",
}
SEASON_METRICS = {"seasonal_state"}
TIME_WINDOW_METRICS = set(WINDOW_METRIC_NAMES)

# Per-metric semantic names for derived-state (operator none) REQUIRED conditions.
DERIVED_STATE_METRICS = {
    "water_reflection_state", "river_flow_state", "spring_tide_state",
    "fog_state", "snow_cover_state", "water_surface_state",
    "nearshore_surf_state", "noctiluca_concentration", "landform_present",
    "light_direction", "cloud_base_height", "lcl_height_m_agl",
    "moon_illuminance_proxy", "seasonal_state",
}


def trapezoid_from_threshold(metric, operator, threshold, family):
    """(weight, [a,b,c,d], provisional) for a QUALITY condition without a §5 row."""
    if isinstance(threshold, (list, tuple)) and len(threshold) == 2:
        lo, hi = float(threshold[0]), float(threshold[1])
        pad = (hi - lo) / 2.0
        a = max(0.0, lo - pad) if lo - pad >= 0 else 0.0
        return (1.0, [a, lo, hi, hi + pad], True)
    if isinstance(threshold, (int, float)) and not isinstance(threshold, bool):
        t = float(threshold)
        if operator == "lte" or operator == "lt":
            # lower-is-better bonus: ideal up to t, acceptable tail +50%
            return (1.0, [0.0, 0.0, t, t * 1.5], True)
        if operator == "gte":
            # higher-is-better: rise from t/2, ideal from t upward (null = inf)
            return (1.0, [t / 2.0, t, None, None], True)
    return (1.0, None, True)  # unusable threshold -> caller falls back


def migrate_doc(doc, report):
    cc = doc["condition_contract"]
    family = TEMPLATE_FAMILY.get(cc.get("genre_template"), None)
    legacy = cc["conditions"]
    time_of_day, required, quality, seasonal = [], [], [], None
    for c in legacy:
        metric = c.get("metric")
        role = c["role"]
        operator = c.get("operator")
        threshold = c.get("threshold")
        if metric in WINDOW_METRIC_NAMES:
            name = WINDOW_METRIC_NAMES[metric]
            if name not in time_of_day:
                time_of_day.append(name)
            continue
        if metric in SEASON_METRICS:
            seasonal = "calendar"
            continue
        if role == "REQUIRED":
            if operator in ("none", None):
                required.append({"id": c["id"], "metric": metric,
                                 "op": "derived_state", "value": threshold})
            else:
                required.append({"id": c["id"], "metric": metric, "op": operator,
                                 "value": threshold})
            continue
        # role == QUALITY
        entry = {"id": c["id"], "metric": metric}
        key = (family, metric) if family else None
        if key and key in SPEC5:
            weight, quad = SPEC5[key]
            entry.update({"weight": weight, "ideal": quad[1:3],
                          "acceptable": [quad[0], quad[3]],
                          "provisional": False})
        elif isinstance(threshold, (int, float)) and operator not in ("none", None, "eq", "in"):
            weight, quad, provisional = trapezoid_from_threshold(
                metric, operator, threshold, family)
            if quad is not None:
                entry.update({"weight": weight, "ideal": quad[1:3],
                              "acceptable": [quad[0], quad[3]],
                              "provisional": provisional})
            else:
                entry.update({"weight": 1.0, "ideal": [1, 1], "acceptable": [0, 1],
                              "provisional": True, "kind": "binary"})
        elif isinstance(threshold, list) and len(threshold) == 2:
            weight, quad, provisional = trapezoid_from_threshold(
                metric, operator, threshold, family)
            entry.update({"weight": weight, "ideal": quad[1:3],
                          "acceptable": [quad[0], quad[3]],
                          "provisional": provisional})
        else:
            # enum / derived-state QUALITY condition: binary membership trapezoid
            entry.update({"weight": 1.0, "ideal": [1, 1], "acceptable": [0, 1],
                          "provisional": True, "kind": "binary"})
        quality.append(entry)
    windows = {"time_of_day": time_of_day, "seasonal": seasonal}
    v2 = {"required": required, "quality": quality}
    changed = []
    if cc.get("windows") != windows:
        cc["windows"] = windows
        changed.append("windows")
    if cc.get("conditions_v2") != v2:
        cc["conditions_v2"] = v2
        changed.append("conditions_v2")
    if doc.get("schema_version") != "2.2.0":
        doc["schema_version"] = "2.2.0"
        changed.append("schema_version")
    report["contracts"] += 1
    report["changed"] += 1 if changed else 0
    report["time_of_day_names"].update(time_of_day)
    report["seasonal_contracts"] += 1 if seasonal else 0
    report["required_entries"] += len(required)
    report["quality_entries"] += len(quality)
    report["provisional_quality"] += sum(1 for q in quality if q.get("provisional"))
    if family is None:
        report["unmapped_templates"].add(cc.get("genre_template"))
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    report = {"contracts": 0, "changed": 0, "seasonal_contracts": 0,
              "required_entries": 0, "quality_entries": 0,
              "provisional_quality": 0,
              "time_of_day_names": set(),
              "unmapped_templates": set()}
    for f in sorted(OPP_DIR.glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        before = f.read_text(encoding="utf-8")
        changed = migrate_doc(doc, report)
        if changed and not args.check:
            f.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
        elif args.check and changed:
            print(f"WOULD-CHANGE {f.name}: {changed}")
    report["time_of_day_names"] = sorted(report["time_of_day_names"])
    report["unmapped_templates"] = sorted(report["unmapped_templates"])
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
