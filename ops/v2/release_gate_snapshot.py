#!/usr/bin/env python3
"""Offline, fail-closed V2 PR release snapshot validator.

Consumes an externally collected, immutable JSON snapshot. This does NOT fetch
GitHub, prove provenance, invoke Codex, merge or deploy. Its output is advisory.
"""
import argparse
import json
import sys

REQUIRED_CHECKS = ("spec", "tests", "source", "localization", "navigation", "evidence")
ALLOWED_OWNERS = {
    "W1": ("specs/v2/",),
    "W2": ("data/v2/",),
    "W3": ("packages/core-v2/", "packages/models-v2/"),
    "W4": ("apps/web-v2/",),
    "W5": ("ops/v2/", ".github/workflows/"),
}


def validate(snapshot):
    failures = []
    if not isinstance(snapshot, dict):
        return ["snapshot must be an object"]
    def required_str(key):
        value = snapshot.get(key)
        if not isinstance(value, str) or not value.strip():
            failures.append(f"{key}: missing")
            return ""
        return value

    base = required_str("base_sha")
    head = required_str("head_sha")
    tested = required_str("tested_head_sha")
    main = required_str("current_main_sha")
    owner = required_str("owner")
    if head and tested and head != tested:
        failures.append("tested head differs from PR head")
    if base and main and base != main:
        failures.append("base differs from current main: revalidate")
    if snapshot.get("draft") is not False:
        failures.append("PR is draft or draft state unverified")
    if snapshot.get("mergeable") is not True:
        failures.append("mergeability unverified or false")
    if snapshot.get("branch_protection_satisfied") is not True:
        failures.append("branch protection not verified")
    if snapshot.get("required_reviews_satisfied") is not True:
        failures.append("required reviews not verified")
    if snapshot.get("human_evidence_signoff_required") is not False and snapshot.get("human_evidence_signoff") is not True:
        failures.append("human evidence signoff not verified")
    if snapshot.get("safety_refusal") is not False:
        failures.append("safety refusal state not cleared")
    paths = snapshot.get("changed_paths")
    prefixes = ALLOWED_OWNERS.get(owner)
    if prefixes is None:
        failures.append("unknown owner")
    if not isinstance(paths, list) or not paths or any(not isinstance(p, str) or not p for p in paths):
        failures.append("changed_paths must be a nonempty list of paths")
    elif prefixes and any(not p.startswith(prefixes) for p in paths):
        failures.append("changed paths exceed worker ownership")
    checks = snapshot.get("checks")
    if not isinstance(checks, dict):
        failures.append("checks missing")
    else:
        for check in REQUIRED_CHECKS:
            if checks.get(check) != "success":
                failures.append(f"{check} check not successful")
    if snapshot.get("source_sha_verified") is not True:
        failures.append("source SHA not verified")
    if snapshot.get("latest_main_spec_verified") is not True:
        failures.append("latest main spec not verified")
    if snapshot.get("provenance_verified") is not True:
        failures.append("provenance not verified")
    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", help="local JSON snapshot collected by an independent trusted integration")
    args = parser.parse_args()
    try:
        with open(args.snapshot, encoding="utf-8") as file:
            snapshot = json.load(file)
    except (OSError, ValueError) as exc:
        print(json.dumps({"eligible": False, "reasons": [str(exc)]}))
        return 2
    failures = validate(snapshot)
    print(json.dumps({"eligible": not failures, "reasons": failures}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
