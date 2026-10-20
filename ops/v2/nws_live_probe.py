#!/usr/bin/env python3
"""One-shot real NWS gridpoint source acceptance for V2 M6b.

This is not a photo forecast, not a camera GPS, and not continuous ingestion.
Intentional external-network test; fail closed if actual provider is unavailable.
"""
import argparse
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "packages/core-v2/adapters/nws_gridpoint.py"
spec = spec_from_file_location("m6b_nws_live_probe", MODULE)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".ci/nws-live-probe.json"))
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    # Named regional sample near the Seattle metro area, NOT Kerry Park's
    # surveyed legal camera/subject/navigation coordinate.
    outcome = mod.fetch_nws_gridpoint(
        latitude=47.6,
        longitude=-122.33,
        field="skyCover",
        valid_at=now + timedelta(hours=2),
        coordinate_source="Seattle metro representative sample; NOT any Camera Zone, Subject or NavigationTarget",
        # Explicit one-shot operational age allowance, NOT an approved
        # photography-quality, provider-model or scientific calibration gate.
        freshness_policy={
            "approved": True,
            "source": "M6b one-shot test-only operational maximum source age 24h; NOT photo-model approval",
            "max_age_seconds": 86400,
        },
        retrieved_at=now,
        timeout=12.0,
    )
    summary = {
        "run_utc": now.isoformat(),
        "probe": "Seattle NOAA/NWS representative raw grid forecast",
        "source_state": outcome["source_state"],
        "photography_verdict": outcome["photography_verdict"],
        "live_recommendation": outcome["live_recommendation"],
        "reasons": outcome["reasons"],
        "result": None,
        "human_research_signoff": "PENDING",
    }
    record = outcome.get("record")
    if record is not None:
        summary["result"] = {
            key: record[key] for key in (
                "provider", "source_kind", "source_url", "mapping_url",
                "source_sha256", "source_update_time_utc", "retrieved_at_utc",
                "valid_from_utc", "valid_until_utc", "retrieval_mode",
                "field", "uom", "raw_value", "provider_issued_at_utc",
                "provider_run_id", "grid", "data_state", "calibration_status",
                "photography_verdict", "recommendation_eligible"
            )
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    safe = (
        outcome["source_state"] == "RAW_SOURCE_ONLY"
        and outcome["photography_verdict"] == "NOT_EVALUABLE"
        and outcome["live_recommendation"] is False
        and record is not None
        and record["retrieval_mode"] == "HTTPS_TLS"
        and record["provider_issued_at_utc"] is None
        and record["provider_run_id"] is None
        and record["recommendation_eligible"] is False
    )
    if not safe:
        print("FAIL: provider did not return an authenticatable, strict raw-only sample",
              file=sys.stderr)
        return 1
    print("PASS: one real NOAA NWS raw forecast sampled; NO photography score/authorization")
    return 0


if __name__ == "__main__":
    sys.exit(main())
