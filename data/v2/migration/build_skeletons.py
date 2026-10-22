"""V1 -> V2 breadth-migration skeleton generator (W2, R0 Research-only).

Deterministically converts every V1 catalog Opportunity (runtime_catalog_v004_r4_2.json,
joined with the per-region V1 weather JSON files for coordinates) into a
schema-valid V2 opportunity skeleton under data/v2/migration/skeletons/.

Rules (from the tw-001/tw-002 pilot and W2_V1_PARITY_PROGRESSION_PROPOSAL.md):
- One skeleton per V1 opportunity; place_id = V1 spot_id.
- V1 information parity: name_zh carried verbatim as zh-TW; en/ja are explicit
  provisional placeholders (never invented translations).
- Camera context / target geometry = V1 spot point, status provisional,
  derivation_method imported_from_v1_viewpoint_reference.
- Condition: one provisional GUIDANCE condition, metric = legacy_<legacy_theme>,
  domain ASTRONOMY, no thresholds, unknown_policy propagate_unknown.
- Navigation target: needs_review, low confidence, generic unverified label.
- Provenance: source_catalog runtime_catalog_v004_r4_2.json,
  source_revision v1-spot-<spot_id>, review_status pending.
- Skeletons accumulate in data/v2/migration/skeletons/ only; they are NEVER
  written into data/v2/opportunities/ (that set is source-lock pinned).

The generator is idempotent: existing files are never overwritten unless
--force is given, and re-running with the same --imported-at reproduces
byte-identical output for determinism checks.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CATALOG = ROOT / "runtime_catalog_v004_r4_2.json"
DEFAULT_WEATHER = [ROOT / "tw_weather.json", ROOT / "jp_weather.json", ROOT / "us_weather.json"]
DEFAULT_OUT = Path(__file__).resolve().parent / "skeletons"
DEFAULT_INVENTORY = Path(__file__).resolve().parent / "inventory.json"
SCHEMA_PATH = ROOT / "specs/v2/schema/opportunity-v2.1.schema.json"

PROVISIONAL_SUFFIX_EN = "(provisional English title, pending review)"
PROVISIONAL_SUFFIX_JA = "（暫定日本語タイトル、レビュー待ち）"
SKELETON_NOTE_ZH = "V1 遷移骨架；內容待第二輪研究完善。"
SKELETON_NOTE_EN = "V1 migration skeleton; content to be refined in round 2."
SKELETON_NOTE_JA = "V1移行スケルトン。内容は第2ラウンドで精緻化予定。"

ACCESS_NOTES = {
    "zh-TW": "存取資訊尚未核實；請依現場公告與規定。",
    "en": "Access information not yet verified; follow on-site notices and rules.",
    "ja": "アクセス情報は未確認。現地の告知と規定に従ってください。",
}
SAFETY_NOTES = {
    "zh-TW": "請依現場安全指示行動。",
    "en": "Follow on-site safety guidance.",
    "ja": "現地の安全指示に従ってください。",
}
NAV_LABELS = {
    "zh-TW": "實際抵達點尚未核實",
    "en": "Practical arrival point not verified",
    "ja": "実際の到着地点は未確認",
}
CONDITION_NOTES = {
    "zh-TW": "由 V1 主題對應的暫定條件；實際閾值待研究核實。",
    "en": "Provisional condition mapped from the V1 theme; thresholds pending research.",
    "ja": "V1テーマから対応した暫定条件。閾値は研究待ち。",
}
REL_UNCERTAINTY = "Imported V1 reference; angles and distance unknown."
CLAIM_SCOPE = "Skeleton import from V1 catalog; no independent evidence attached yet."


def _i18n(zh_text):
    return {
        "zh-TW": zh_text,
        "en": f"{zh_text} {PROVISIONAL_SUFFIX_EN}",
        "ja": f"{zh_text}{PROVISIONAL_SUFFIX_JA}",
    }


def _point_geometry(lat, lon):
    return {
        "kind": "point",
        "status": "provisional",
        "geojson": {"type": "Point", "coordinates": [lon, lat]},
        "uncertainty_m": None,
        "derivation_method": "imported_from_v1_viewpoint_reference",
        "source_geometry_revision": None,
        "reason_if_absent": None,
    }


def build_skeleton(spot, opp, imported_at):
    oid = opp["opportunity_id"]
    name_zh = opp["name_zh"]
    name = _i18n(name_zh)
    lat, lon = spot["lat"], spot["lon"]
    theme = opp.get("legacy_theme") or "landscape"
    return {
        "schema_version": "2.1.0",
        "opportunity_id": oid,
        "place_id": spot["spot_id"],
        "revision": 1,
        "lifecycle_status": "draft",
        "name_i18n": name,
        "description_i18n": {
            "zh-TW": f"{name_zh}（{SKELETON_NOTE_ZH}）",
            "en": f"{name_zh} ({SKELETON_NOTE_EN})",
            "ja": f"{name_zh}（{SKELETON_NOTE_JA}）",
        },
        "camera_contexts": [{
            "id": f"CZ-{oid}-01",
            "kind": "area",
            "geometry": _point_geometry(lat, lon),
            "verification_status": "provisional",
            "evidence_refs": [],
            "access_notes_i18n": ACCESS_NOTES,
            "safety_notes_i18n": SAFETY_NOTES,
            "altitude_m": spot.get("elevation") if spot.get("elevation") is not None else spot.get("api_elevation"),
        }],
        "targets": [{
            "id": f"SG-{oid}-01",
            "kind": "multi_component",
            "name_i18n": name,
            "geometry": _point_geometry(lat, lon),
            "phenomenon_model_id": None,
            "evidence_refs": [],
            "components": [],
        }],
        "observation_relations": [{
            "id": f"VR-{oid}-01",
            "camera_context_id": f"CZ-{oid}-01",
            "target_id": f"SG-{oid}-01",
            "type": "foreground_background",
            "geometry_mode": "unknown",
            "azimuth_deg": None,
            "elevation_deg": None,
            "distance_m": None,
            "evidence_refs": [],
            "derivation_method": None,
            "uncertainty_note": REL_UNCERTAINTY,
        }],
        "navigation_targets": [{
            "id": f"NAV-{oid}-01",
            "status": "needs_review",
            "target_type": "other",
            "lat": lat,
            "lon": lon,
            "label_i18n": NAV_LABELS,
            "evidence_refs": [],
            "confidence": "low",
        }],
        "condition_contract": {
            "contract_id": f"CC-{oid}-v1",
            "status": "draft",
            "conditions": [{
                "id": f"C-{oid}-01",
                "role": "REQUIRED",
                "domain": "ASTRONOMY",
                "evaluation_mode": "GUIDANCE",
                "capability": "CONDITIONS",
                "metric": f"legacy_{theme}",
                "operator": "none",
                "threshold": None,
                "unit": None,
                "unknown_policy": "propagate_unknown",
                "claim_refs": [f"{oid}-claim-01"],
                "model_binding": None,
                "notes_i18n": CONDITION_NOTES,
                "validation_status": "provisional",
            }],
            "recommendation_policy_version": None,
        },
        "evidence_claims": [{
            "claim_id": f"{oid}-claim-01",
            "claim_type": "existence",
            "evidence_refs": [],
            "audit_status": "UNKNOWN",
            "scope_note": CLAIM_SCOPE,
        }],
        "readiness": {"research_level": "R0", "gaps": ["RESEARCH_GAP", "GEOMETRY_GAP"]},
        "provenance": {
            "source_catalog": "runtime_catalog_v004_r4_2.json",
            "source_revision": f"v1-spot-{spot['spot_id']}",
            "imported_at": imported_at,
            "review_status": "pending",
            "reviewed_by": None,
        },
    }


def load_inputs(catalog_path, weather_paths):
    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    coords = {}
    names = {}
    for wp in weather_paths:
        data = json.loads(Path(wp).read_text(encoding="utf-8"))
        for spot in data["spots"]:
            coords[spot["spot_id"]] = (spot["lat"], spot["lon"])
            names[spot["spot_id"]] = spot
    return catalog, coords, names


def validate_document(doc, schema):
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema-not-installed"]
    from jsonschema import Draft202012Validator
    errors = sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.path))
    return [f"{list(e.path)}: {e.message}" for e in errors]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    ap.add_argument("--weather", nargs="*", default=[str(p) for p in DEFAULT_WEATHER])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    ap.add_argument("--imported-at", default=None,
                    help="ISO-8601 UTC timestamp stamped into provenance; omit = current UTC")
    ap.add_argument("--force", action="store_true", help="overwrite existing skeleton files")
    ap.add_argument("--region", choices=["tw", "jp", "us"], default=None)
    ap.add_argument("--limit-spots", type=int, default=None, help="process at most N unprocessed spots")
    ap.add_argument("--ids", nargs="*", default=None, help="explicit spot_id list")
    ap.add_argument("--check-only", action="store_true", help="plan and validate but write nothing")
    args = ap.parse_args()

    imported_at = args.imported_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalog, coords, _ = load_inputs(args.catalog, args.weather)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    schema = None
    if SCHEMA_PATH.exists():
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    canonical_dir = ROOT / "data/v2/opportunities"
    admitted = {p.stem for p in canonical_dir.glob("*.json")} if canonical_dir.exists() else set()

    written, skipped, admitted_skipped, errors = [], [], [], []
    per_region = {"tw": {"spots": 0, "opportunities": 0},
                  "jp": {"spots": 0, "opportunities": 0},
                  "us": {"spots": 0, "opportunities": 0}}
    planned_spots = 0

    for spot in catalog["spots"]:
        sid = spot["spot_id"]
        region = sid.split("-")[0]
        if args.region and region != args.region:
            continue
        if args.ids and sid not in args.ids:
            continue
        if sid not in coords:
            errors.append(f"{sid}: no V1 coordinate source")
            continue
        if args.limit_spots is not None and planned_spots >= args.limit_spots:
            break
        planned_spots += 1
        opp_count = 0
        for opp in spot["opportunities"]:
            oid = opp["opportunity_id"]
            doc = build_skeleton({**spot, "lat": coords[sid][0], "lon": coords[sid][1]}, opp, imported_at)
            if schema:
                errs = validate_document(doc, schema)
                if errs and errs != ["jsonschema-not-installed"]:
                    errors.append(f"{oid}: schema {errs}")
                    continue
            target = out_dir / f"{oid}.json"
            if oid in admitted:
                admitted_skipped.append(oid)
                opp_count += 1
                continue
            if target.exists() and not args.force:
                skipped.append(oid)
                opp_count += 1
                continue
            if not args.check_only:
                target.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            written.append(oid)
            opp_count += 1
        per_region[region]["spots"] += 1
        per_region[region]["opportunities"] += opp_count

    processed_ids = sorted(p.stem for p in out_dir.glob("*.json"))
    all_spots = catalog["spots"]
    done_places = sorted({i.rsplit("-P", 1)[0] for i in processed_ids})
    skeleton_or_admitted = set(processed_ids) | admitted
    pending_places = [s["spot_id"] for s in all_spots
                      if any(o["opportunity_id"] not in skeleton_or_admitted for o in s["opportunities"])
                      and (not args.region or s["spot_id"].split("-")[0] == args.region)]
    inventory = {
        "format_version": "0.1.0",
        "mode": "RESEARCH_ONLY_R0_SKELETON",
        "policy": "W2_V1_PARITY_PROGRESSION_PROPOSAL two-pass (Pass 1 breadth)",
        "imported_at": imported_at,
        "v1_inventory": {
            "spots_total": len(all_spots),
            "opportunities_total": sum(len(s["opportunities"]) for s in all_spots),
        },
        "first_pass": {
            "skeleton_files": len(processed_ids),
            "admitted_canonical": sorted(admitted),
            "places_with_skeleton": len(done_places),
            "places_first_pass_covered": len([s for s in all_spots
                                              if all(o["opportunity_id"] in skeleton_or_admitted
                                                     for o in s["opportunities"])]),
            "places_pending": pending_places,
            "per_region": per_region,
        },
        "skeleton_dir": "data/v2/migration/skeletons",
        "note": "Skeletons are R0 draft research-only; admission into data/v2/opportunities/ requires the explicit W2 source re-review process. Never a live forecast.",
    }
    if not args.check_only:
        Path(args.inventory).write_text(
            json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(json.dumps({"written": len(written), "skipped_existing": len(skipped),
                      "admitted_skipped": sorted(admitted_skipped),
                      "errors": errors, "inventory_spots": planned_spots}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
