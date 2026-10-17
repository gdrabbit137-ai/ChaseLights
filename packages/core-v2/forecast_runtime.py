"""W3 research runtime: canonical -> regional solar event -> NWS -> evaluator.

Standalone diagnostic only, not the W1 EvaluationResult or public query API.
There is deliberately no photography threshold, score, or publication path.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from adapters.nws_snapshot import fetch_nws_snapshot
from evaluator import evaluate_raw_forecast

ROOT = Path(__file__).resolve().parents[2]
_spec = spec_from_file_location("w3_runtime_solar", ROOT / "packages/models-v2/solar_window.py")
solar = module_from_spec(_spec)
_spec.loader.exec_module(solar)

PILOT_ID = "us-071-P01"
# Existing #482 regional Seattle sample, NOT the Kerry Park camera position.
SAMPLE = {"coordinate_role": "representative_place_sample", "lat": 47.6,
          "lon": -122.33, "uncertainty_m": None, "altitude_m": None,
          "coordinate_source": "https://github.com/gdrabbit137-ai/ChaseLights/pull/482 (Seattle regional sample only)"}
ZONE = "America/Los_Angeles"
ZONE_SOURCE = "packages/models-v2/README.md Seattle numerical benchmark; NWS /points properties.timeZone must corroborate weather sampling"


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical_hash(value):
    return _hash(json.dumps(value, sort_keys=True, separators=(",", ":"),
                            ensure_ascii=False, allow_nan=False).encode("utf-8"))


def run_forecast(canonical_bytes, *, local_date, freshness_policy, event="sunset"):
    """Run one supported pilot. Network and retrieval clock are never injectable.

    The public entry accepts original Canonical bytes (hashed in the output),
    an explicit local date and an operator-supplied data-age policy. The pilot
    is limited to Seattle's documented regional sample; no inferred camera GPS.
    All inputs remain research-only, even if a caller submits approved flags.
    """
    now = datetime.now(timezone.utc)
    if type(canonical_bytes) is not bytes:
        raise ValueError("CANONICAL_BYTES_REQUIRED")
    opportunity = json.loads(canonical_bytes)
    schema = json.loads((ROOT / "specs/v2/schema/opportunity-v2.1.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(opportunity)
    if (opportunity["opportunity_id"] != PILOT_ID or opportunity["place_id"] != "us-071"):
        raise ValueError("UNSUPPORTED_PILOT: no implicit Taiwan/Japan NWS coverage")
    if event not in ("sunrise", "sunset"):
        raise ValueError("UNSUPPORTED_SOLAR_EVENT")
    request = {
        "schema_version": "0.1.0", "request_id": f"{PILOT_ID}-{local_date}-{event}",
        "local_date": local_date, "time_zone": ZONE, "observer": dict(SAMPLE),
        "model": {"model_id": solar.MODEL_ID, "algorithm_version": solar.ALGORITHM_VERSION,
                  "horizon_assumption": "ideal_unobstructed", "sun_altitude_crossing_deg": -0.833},
    }
    window = solar.compute_solar_window(request, computed_at=now)
    selected_event = window[event]
    if selected_event["status"] == "CALCULATED":
        weather = fetch_nws_snapshot(
            latitude=SAMPLE["lat"], longitude=SAMPLE["lon"],
            coordinate_source=SAMPLE["coordinate_source"],
            valid_at=selected_event["time_utc"], freshness_policy=freshness_policy,
            expected_time_zone=ZONE)
    else:
        weather = {"source_state": "UNKNOWN", "records": [], "documents": [],
                   "fields": {}, "reasons": ["SOLAR_EVENT_UNAVAILABLE"]}
    records = weather["records"]
    weather_refs = [record["record_id"] for record in records]
    window_ref = _canonical_hash(window)
    context = {
        "WEATHER": {"refs": weather_refs, "reasons": weather["reasons"] + [
            "SKY_COVER_IS_NOT_SKYLINE_VISIBILITY", "ALTITUDE_AND_LINE_OF_SIGHT_UNVERIFIED"]},
        "ASTRONOMY": {"refs": [window_ref], "reasons": [
            "REGIONAL_SOLAR_EVENT_ONLY", "CITY_LIGHT_SWITCHING_AND_HORIZON_UNVERIFIED"]},
    }
    evaluated_at = datetime.now(timezone.utc)
    readiness = {**opportunity["readiness"], "lifecycle_status": opportunity["lifecycle_status"],
                 "research_only": True, "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z")}
    evaluation = evaluate_raw_forecast(opportunity["condition_contract"], context, readiness)
    condition_by_id = {c["id"]: c for c in opportunity["condition_contract"]["conditions"]}
    for trace in evaluation["conditions"]:
        condition = condition_by_id[trace["condition_id"]]
        trace.update({"metric": condition["metric"], "claim_refs": condition["claim_refs"],
                      "model_binding": condition["model_binding"],
                      "threshold": condition["threshold"], "unit": condition["unit"]})
    return {
        "diagnostic_version": "w3-real-forecast/0.1.0",
        "artifact_kind": "RESEARCH_RUNTIME_DIAGNOSTIC",
        "opportunity_id": PILOT_ID, "opportunity_revision": opportunity["revision"],
        "canonical_sha256": _hash(canonical_bytes),
        "contract_sha256": _canonical_hash(opportunity["condition_contract"]),
        "time_zone": ZONE, "time_zone_source": ZONE_SOURCE,
        "time_zone_scope": "REGIONAL_SAMPLE_ONLY_NOT_VERIFIED_PLACE_ZONE",
        "time_zone_verification": (
            "PROVIDER_REGIONAL_SAMPLE" if records and weather.get("retrieval_mode") == "HTTPS_TLS"
            else "TEST_FIXTURE" if records else "REGIONAL_DIAGNOSTIC_ASSUMPTION"),
        "selected_local_date": local_date, "selected_event": event,
        "source_kinds": {"weather": "FORECAST", "observation": "UNAVAILABLE",
                         "astronomy": "DETERMINISTIC_WINDOW"},
        "solar_window_sha256": window_ref, "solar_window": window,
        "weather": weather, "evaluation": evaluation,
        "access_advisories": [{"camera_context_id": c["id"],
                               "access_notes_i18n": c["access_notes_i18n"],
                               "safety_notes_i18n": c["safety_notes_i18n"],
                               "evidence_refs": c["evidence_refs"],
                               "affects_photography_suitability": False}
                              for c in opportunity["camera_contexts"]],
        "directions_eligible": False, "research_only": True,
        "photography_verdict": "NOT_EVALUABLE", "recommendation_eligible": False,
        "limitations_i18n": {
            "zh-TW": "此為西雅圖區域日出／日落與原始預報診斷，非機位或天際線能見度預報；街燈、地形遮蔽與攝影門檻未驗證，無拍攝建議或導航。",
            "en": "Seattle regional sunrise/sunset and raw forecast diagnostic, not a camera or skyline visibility forecast. City lights, horizon obstruction and photo thresholds are unverified; no shooting recommendation or directions.",
            "ja": "シアトル地域の日の出・日の入りと予報原データの診断。撮影地点や市街地の視認性の予報ではない。街明かり、地形の遮蔽、撮影条件の閾値は未検証で、撮影推奨や経路案内は行わない。",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path,
                        default=ROOT / "data/v2/opportunities/us-071-P01.json")
    parser.add_argument("--local-date", required=True)
    parser.add_argument("--event", choices=("sunrise", "sunset"), default="sunset")
    parser.add_argument("--freshness-policy", required=True, type=Path,
                        help="JSON approved/source/max_age_seconds; no production default")
    args = parser.parse_args()
    try:
        result = run_forecast(args.canonical.read_bytes(), local_date=args.local_date,
                              event=args.event,
                              freshness_policy=json.loads(args.freshness_policy.read_text()))
    except (ValueError, OSError, ValidationError) as exc:
        print(json.dumps({"photography_verdict": "NOT_EVALUABLE", "error": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["weather"]["source_state"] == "RAW_SOURCE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
