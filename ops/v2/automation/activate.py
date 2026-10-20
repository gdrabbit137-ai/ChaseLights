#!/usr/bin/env python3
"""Trusted activation check; missing configuration is an explicit BLOCKED artifact."""
import argparse
import json
import os
from pathlib import Path
from runner import Stop, validate_policy


def activate(policy, environ):
    report = {"status": "BLOCKED", "ready": False, "live_model_e2e": "NOT_RUN",
              "merge_allowed": False, "deployment_allowed": False}
    missing = [k for k in ("OPENAI_API_KEY", "GH_APP_ID", "GH_APP_PRIVATE_KEY") if not environ.get(k)]
    report["missing_configuration"] = missing
    try:
        validate_policy(policy, live=True)
        if missing:
            raise Stop("MISSING_EXECUTOR_CREDENTIALS")
    except Stop as exc:
        report["code"] = exc.code
    else:
        report.update(status="READY", ready=True, code="READY_FOR_BOUNDED_PILOT_ONLY")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = activate(json.loads(Path("ops/v2/automation/policy.json").read_text()), os.environ)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write("ready=" + str(result["ready"]).lower() + "\n")
    print(json.dumps(result, sort_keys=True))
