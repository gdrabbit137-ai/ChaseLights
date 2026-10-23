#!/usr/bin/env python3
"""First-batch ConditionContract evaluation runner (test-only, offline).

Wires the admitted RAW_ONLY open-meteo hourly pilot artifact through the
threshold-observation bridge into the conservative core-v2 evaluator, and
emits EvaluationResult v0.1 documents validated against the pinned W1 schema.

Honesty contract:
- The canonical contract for the first batch opportunity (tw-036-P01) is in
  ``review`` status with ``provisional``/GUIDANCE conditions, so every
  produced result is UNKNOWN/NOT_EVALUABLE with machine reasons — the
  pipeline runs end to end without fabricating a favorable verdict.
- Every result carries provenance.test_only = true; the pinned schema itself
  forbids live_recommendation and FAVORABLE for such results.
- Provider run ``issued_at`` is the artifact retrieval time (the provider
  does not publish an issue time for this pilot); the gap is carried in
  ``unknown_reasons`` as PROVIDER_ISSUE_TIME_UNKNOWN.
- Freshness is recomputed against the ``--evaluated-at`` instant using the
  artifact's own retrieval_age_policy (21600 s).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for entry in (str(ROOT / "packages/core-v2"), str(ROOT / "packages/models-v2")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from adapters import open_meteo_hourly as adapter  # noqa: E402
from adapters import threshold_observations as bridge  # noqa: E402
from evaluator import evaluate  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402


def aligned_zone(declared_version):
    """Return an Asia/Taipei zone only when its definition version equals the
    artifact's declared tzdb version. The pinned tzdata Python package is the
    preferred source because its IANA version is machine-readable; a system
    zoneinfo tree is never trusted sight-unseen."""
    try:
        import tzdata
        if tzdata.IANA_VERSION == declared_version:
            import importlib.resources as resources
            with resources.files("tzdata.zoneinfo").joinpath("Asia/Taipei").open("rb") as file:
                return ZoneInfo.from_file(file, key="Asia/Taipei")
    except Exception:
        return None
    return None

SCHEMA_PATH = ROOT / "specs/v2/schema/evaluation-result-v0.1.schema.json"
OPPORTUNITY_PATH = ROOT / "data/v2/opportunities/tw-036-P01.json"
FRESHNESS_SECONDS = 21600


def jsonschema_validator():
    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema)


def contract_sha256(contract):
    canonical = json.dumps(contract, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def freshness_of(artifact, evaluated_at):
    age = (evaluated_at - parse_utc(artifact["source"]["retrieved_at_utc"])).total_seconds()
    return "FRESH" if age <= FRESHNESS_SECONDS else "STALE"


def build_provider_run(artifact, evaluated_at):
    source = artifact["source"]
    return {
        "run_id": "retrieved-" + source["retrieved_at_utc"],
        "provider": source["provider"],
        "source": source["source_url"],
        "provider_version": "not-provided-by-provider",
        "issued_at": source["retrieved_at_utc"],
        "valid_at": artifact["hours"][0]["valid_at_utc"],
        "freshness": freshness_of(artifact, evaluated_at),
    }


def evaluate_hours(opportunity, artifact, selected_date, evaluated_at):
    contract = opportunity["condition_contract"]
    opportunity_id = opportunity["opportunity_id"]
    opportunity_revision = int(opportunity["revision"])
    inputs = adapter.load_inputs(ROOT)
    declared_zone = aligned_zone(artifact["tzdb_version"])
    unaligned = None
    if declared_zone is not None:
        zone = declared_zone
        rows = [row for row in artifact["hours"]
                if adapter.utc(row["valid_at_utc"]).astimezone(zone).date().isoformat() == selected_date]
    else:
        # No zone definition matching the declared tzdb version: refuse to
        # guess a different one and emit an honest NOT_EVALUABLE bundle.
        zone = None
        unaligned = "TZDB_VERSION_MISMATCH"
        rows = []
    if unaligned is None and not rows:
        raise adapter.PilotFailure("NO_MATCHING_DATA")
    if unaligned is not None:
        return {"evaluation_bundle_version": "0.1.0",
                "opportunity_id": opportunity["opportunity_id"],
                "condition_contract_id": contract["contract_id"],
                "condition_contract_sha256": contract_sha256(contract),
                "selected_local_date": selected_date,
                "time_zone": "Asia/Taipei",
                "tzdb_version": artifact["tzdb_version"],
                "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z"),
                "test_only": True,
                "state": "NOT_EVALUABLE",
                "reason_code": unaligned,
                "provider_run": None,
                "results": []}
    provider_run = build_provider_run(artifact, evaluated_at)
    freshness = provider_run["freshness"]
    validator = jsonschema_validator()
    results = []
    for row in rows:
        at = parse_utc(row["valid_at_utc"])
        at_iso = row["valid_at_utc"]
        observations = {}
        for condition in contract["conditions"]:
            observation = None
            if bridge.comparable(condition) is not None:
                cell = row["values"].get(bridge.METRIC_FIELDS[condition["metric"]])
                observation = bridge.cell_observation(
                    condition, cell, at_iso=at_iso,
                    provider=artifact["source"]["provider"],
                    source=artifact["source"]["source_url"],
                    issued_at=artifact["source"]["retrieved_at_utc"],
                    freshness=freshness.lower(),
                    unit_expected=cell and cell.get("source_unit"))
            if observation is not None and observation["state"] != "UNKNOWN":
                observations[condition["id"]] = observation
        readiness = {"evaluated_at": at_iso, "research_only": True,
                     "lifecycle_status": opportunity.get("lifecycle_status", "research_only"),
                     "research_level": (opportunity.get("readiness") or {}).get("research_level", "R1")}
        verdict = evaluate(contract, observations, readiness)
        reasons = list(verdict["reasons"])
        reasons.append("PROVIDER_ISSUE_TIME_UNKNOWN")
        statuses = {"BLOCKED": "UNFAVORABLE", "UNKNOWN": "NOT_EVALUABLE",
                    "TEST_ONLY_CONDITIONS_MET": "UNCERTAIN"}
        result = {
            "evaluation_result_version": "0.1.0",
            "opportunity_id": opportunity_id,
            "opportunity_revision": opportunity_revision,
            "condition_contract_id": contract["contract_id"],
            "condition_contract_sha256": contract_sha256(contract),
            "issued_at": evaluated_at.isoformat().replace("+00:00", "Z"),
            "valid_at": at_iso,
            "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z"),
            "freshness": "FRESH" if freshness == "FRESH" else "STALE",
            "runtime_availability": "UNAVAILABLE",
            "status": statuses[verdict["decision"]],
            "live_recommendation": False,
            "model": None,
            "provider_runs": [provider_run],
            "conditions": [
                {"condition_id": trace["condition_id"], "role": trace["role"],
                 "evaluation_mode": trace["evaluation_mode"],
                 "verdict": trace["state"] if trace["state"] in ("PASS", "FAIL") else "UNKNOWN" if trace["state"] == "UNKNOWN" else "NOT_EVALUABLE",
                 "unknown_reasons": [trace["reason"]] if trace["state"] == "UNKNOWN" else [],
                 "provider_run_refs": [provider_run["run_id"]] if trace["state"] in ("PASS", "FAIL") else []}
                for trace in verdict["conditions"]
            ],
            "unknown_reasons": sorted(set(reasons)),
            "provenance": {"evaluator_id": "chase-v2-evaluator-first-batch",
                           "evaluator_version": "0.1.0", "test_only": True,
                           "input_digest": artifact["source"]["source_sha256"]},
        }
        validator.validate(result)
        results.append(result)
    return {"evaluation_bundle_version": "0.1.0",
            "opportunity_id": opportunity_id,
            "condition_contract_id": contract["contract_id"],
            "condition_contract_sha256": contract_sha256(contract),
            "selected_local_date": selected_date,
            "time_zone": zone.key,
            "tzdb_version": artifact["tzdb_version"],
            "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z"),
            "test_only": True,
            "state": "READY",
            "provider_run": provider_run,
            "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", default="apps/web-v2/weather-pilot-tw036.json")
    parser.add_argument("--opportunity", default=str(OPPORTUNITY_PATH))
    parser.add_argument("--local-date", required=True)
    parser.add_argument("--evaluated-at", required=True, help="UTC instant, ISO-8601 Z")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    evaluated_at = parse_utc(arguments.evaluated_at.replace("Z", "+00:00"))
    artifact = json.loads((ROOT / arguments.artifact).read_text(encoding="utf-8"))
    opportunity = json.loads(Path(arguments.opportunity).read_text(encoding="utf-8"))
    try:
        bundle = evaluate_hours(opportunity, artifact, arguments.local_date, evaluated_at)
    except adapter.PilotFailure as failure:
        print(json.dumps({"status": "FAIL", "error": str(failure)}))
        return 1
    output = Path(arguments.output)
    output.write_text(json.dumps(bundle, indent=1, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print(json.dumps({"status": "PASS", "results": len(bundle["results"]),
                      "statuses": sorted({r["status"] for r in bundle["results"]})}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
