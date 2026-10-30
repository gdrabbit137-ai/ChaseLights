"""Time-specialization layering migration (owner-approved 2026-10-31).

Step 1 (--decompose): decompose every canonical opportunity contract into
(base layers, time specialization) assignment; fail-closed on unmapped metrics.
Step 2 (--apply-night): apply the owner-adjudicated night overlay to the 5
mislabelled opportunities. Writes staged contracts to data/v2/staging/contracts/
first, then copies byte-identically into canonical opportunities/ (governance
invariant: canonical == staged bytes).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OPP_DIR = ROOT / "data/v2/opportunities"
STAGING = ROOT / "data/v2/staging/template_layering"
STAGED_CONTRACTS = ROOT / "data/v2/staging/contracts"
NIGHT_TEMPLATE = json.loads(
    (ROOT / "data/v2/templates/night_sky.json").read_text(encoding="utf-8"))
CITY_NIGHT_TEMPLATE = json.loads(
    (ROOT / "data/v2/templates/city_night.json").read_text(encoding="utf-8"))

# Metrics that describe daytime-painting conditions and must NOT survive a
# night conversion (sunset window and the sunset/bunraku cloud-painting bands).
DAY_ONLY_METRICS = {"sunset_window", "sunrise_time_window", "blue_hour_window",
                    "golden_hour_window", "cloud_cover_mid_and_high",
                    "cloud_cover_low"}

NIGHT_SET = [c for c in NIGHT_TEMPLATE["conditions"]]
CITY_NIGHT_SET = [c for c in CITY_NIGHT_TEMPLATE["conditions"]]

# owner adjudication (2026-10-31, blanket approval of PROPOSAL section 3;
# tw-082-P06 tie-break: artificial light installations -> city_night)
TARGETS = {
    "tw-027-P02": ("night_sky", NIGHT_SET),
    "tw-035-P05": ("night_sky", NIGHT_SET),
    "tw-036-P02": ("night_sky", NIGHT_SET),
    "tw-038-P02": ("night_sky", NIGHT_SET),
    "tw-082-P06": ("city_night", CITY_NIGHT_SET),
}

KEEP_METRICS_NIGHT = {"landform_present", "seasonal_state", "precipitation",
                      "wind_speed_10m", "water_surface_state"}
KEEP_METRICS_CITY = {"precipitation"}


def bump_version(version: str) -> str:
    parts = [int(x) for x in version.split(".")]
    parts[-1] += 1
    return ".".join(str(p) for p in parts)


def convert_binding(binding):
    if binding is None:
        return None
    if isinstance(binding, str):
        return binding
    return (f"dataset:{binding.get('dataset')}|field:{binding.get('field')}"
            f"|role:{binding.get('role')}")


def night_condition(oid, index, template_condition, claim_ref):
    c = {
        "id": f"C-{oid}-{index:02d}",
        "role": template_condition["role"],
        "domain": template_condition["domain"],
        "evaluation_mode": template_condition["evaluation_mode"],
        "capability": template_condition["capability"],
        "metric": template_condition["metric"],
        "operator": template_condition["operator"],
        "threshold": template_condition.get("threshold"),
        "unit": template_condition.get("unit"),
        "unknown_policy": template_condition.get("unknown_policy",
                                                 "propagate_unknown"),
        "claim_refs": [claim_ref],
        "model_binding": convert_binding(template_condition.get("binding")),
        "validation_status": "provisional",
        "condition_tier": template_condition["condition_tier"],
        "threshold_source": template_condition.get("threshold_source",
                                                   "formula_derived"),
        "calibration_status": template_condition.get("calibration_status",
                                                     "provisional"),
        "rationale_i18n": template_condition["rationale_i18n"],
    }
    if template_condition.get("activate_when"):
        c["activate_when"] = template_condition["activate_when"]
    return c


def apply_night(doc, genre, template_set, keep_metrics, log):
    oid = doc["opportunity_id"]
    contract = doc["condition_contract"]
    claim_ref = (contract["conditions"][0].get("claim_refs") or [None])[0] or (
        f"{oid}-claim-01")
    kept, dropped = [], []
    for c in contract["conditions"]:
        if c["metric"] in keep_metrics:
            kept.append(c)
        else:
            dropped.append(c["metric"])
    # Stricter-merge for metrics the new set shares with kept conditions.
    existing_metrics = {c["metric"] for c in kept}
    added, replaced = [], []
    next_index = 1 + max(
        (int(re.search(r"-(\d+)$", c["id"]).group(1)) for c in kept), default=0)
    for tc in template_set:
        metric = tc["metric"]
        if metric in existing_metrics:
            for c in kept:
                if c["metric"] != metric:
                    continue
                if tc["operator"] == c["operator"] and \
                        tc.get("threshold") is not None and \
                        c.get("threshold") is not None:
                    if tc["operator"] in ("lte", "lt"):
                        c["threshold"] = min(tc["threshold"], c["threshold"])
                    elif tc["operator"] in ("gte", "gt"):
                        c["threshold"] = max(tc["threshold"], c["threshold"])
                    if tc["role"] == "REQUIRED" and c["role"] != "REQUIRED":
                        c["role"] = "REQUIRED"
                        c["condition_tier"] = "MAIN"
                    replaced.append(metric)
            continue
        added.append(metric)
        kept.append(night_condition(oid, next_index, tc, claim_ref))
        next_index += 1
    old_genre = contract["genre_template"]
    contract["genre_template"] = genre
    log.append({
        "opportunity_id": oid,
        "old_genre": old_genre,
        "new_genre": genre,
        "dropped_day_only": dropped,
        "added": added,
        "stricter_merged": sorted(set(replaced)),
        "reason": "owner adjudication 2026-10-31 (time-specialization "
                  "proposal section 3): night-sky subject carried a daytime "
                  "template; night layer adds astronomical_darkness + moon "
                  "constraints so daytime hours no longer report "
                  "GUIDANCE_SATISFIED",
    })
    contract["conditions"] = kept
    return doc


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--decompose"
    if mode == "--decompose":
        assignment = {}
        unmapped = []
        legacy_excluded = set()
        for path in sorted(OPP_DIR.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            cc = doc.get("condition_contract") or {}
            entries = []
            for c in cc.get("conditions", []):
                m = c["metric"]
                if m == "precipitation":
                    layer = "base:precipitation"
                elif m == "aod_550nm":
                    layer = "base:atmospheric_clarity"
                elif m in ("cloud_cover_low", "cloud_cover_mid",
                           "cloud_cover_mid_and_high", "cloud_cover_total"):
                    layer = "base:cloud_state"
                elif m == "wind_speed_10m":
                    layer = "base:wind_state"
                elif m == "water_surface_state":
                    layer = "base:water_surface"
                elif m == "seasonal_state":
                    layer = "base:seasonal"
                elif m == "landform_present":
                    layer = "base:landform"
                elif m == "river_flow_state":
                    layer = "base:river_flow"
                elif m in ("relative_humidity_925hpa", "relative_humidity_850hpa",
                           "lcl_height_m_agl", "temperature_delta_850_925_c",
                           "wind_speed_850hpa"):
                    layer = "base:atmospheric_profile"
                elif m == "visibility":
                    layer = "base:visibility"
                elif m in ("sunrise_time_window",):
                    layer = "spec:sunrise"
                elif m in ("sunset_window",):
                    layer = "spec:sunset"
                elif m == "golden_hour_window":
                    layer = "spec:golden"
                elif m == "blue_hour_window":
                    layer = "spec:blue"
                elif m in ("astronomical_darkness", "moon_illumination_fraction",
                           "moon_altitude", "moon_target_separation_deg",
                           "moon_illuminance_proxy", "galactic_core_altitude"):
                    layer = "spec:night"
                else:
                    legacy = m.startswith("legacy_") or m in (
                        "mount_fuji_visibility", "lavender_kochia_seasonal_state")
                    if legacy:
                        legacy_excluded.add(doc["opportunity_id"])
                        break
                    # opportunity-bespoke metric (e.g. tw-026 salt pan, us-071
                    # skyline): kept verbatim under the opportunity-specific layer
                    layer = "base:bespoke" 
                entries.append({"condition_id": c["id"], "metric": m,
                                "layer_id": layer})
            assignment[doc["opportunity_id"]] = {
                "genre_template": cc.get("genre_template"),
                "conditions": entries,
            }
        STAGING.mkdir(parents=True, exist_ok=True)
        (STAGING / "assignment.json").write_text(
            json.dumps(assignment, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(json.dumps({"status": "DECOMPOSED", "opportunities": len(assignment),
                          "legacy_excluded": len(legacy_excluded),
                          "unmapped": unmapped[:10], "unmapped_count": len(unmapped)}))
        return 1 if unmapped else 0

    if mode == "--apply-night":
        log = []
        STAGED_CONTRACTS.mkdir(parents=True, exist_ok=True)
        for oid, (genre, template_set) in TARGETS.items():
            path = OPP_DIR / f"{oid}.json"
            doc = json.loads(path.read_text(encoding="utf-8"))
            keep = KEEP_METRICS_CITY if genre == "city_night" else KEEP_METRICS_NIGHT
            doc = apply_night(doc, genre, template_set, keep, log)
            staged = STAGED_CONTRACTS / f"{oid}.json"
            staged.write_text(json.dumps(doc, ensure_ascii=False,
                                         separators=(",", ":")) + "\n",
                              encoding="utf-8")
            path.write_text(staged.read_text(encoding="utf-8"),
                            encoding="utf-8")
            assert path.read_bytes() == staged.read_bytes(), f"parity fail {oid}"
        (STAGING / "MIGRATION_LOG.json").write_text(
            json.dumps(log, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(json.dumps({"status": "NIGHT_APPLIED", "count": len(log),
                          "oids": [x["opportunity_id"] for x in log]}))
        return 0

    print("usage: migrate_layering.py --decompose | --apply-night")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
