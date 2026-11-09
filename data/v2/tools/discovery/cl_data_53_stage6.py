#!/usr/bin/env python3
"""CL-DATA-53 stage 6 splice: run scoped 168h evals for us-119..us-158 and splice
into apps/web-v2/evaluations-latest.json (bundle keeps its pre-existing 309 places)."""
import json
import os
import subprocess
import sys

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))) \
    if False else r"D:/tmp/cd53-wt"
SCRATCH = r"D:/tmp/cd53-scratch/ev"
os.makedirs(SCRATCH + "/det", exist_ok=True)
PIDS = [f"us-{n}" for n in range(119, 159)]


def splice(bundle, scoped):
    by_id = [p["place_id"] for p in bundle["places"]]
    for p in scoped["places"]:
        if p["place_id"] in by_id:
            bundle["places"][by_id.index(p["place_id"])] = p
        else:
            bundle["places"].append(p)
    bundle["place_count"] = len(bundle["places"])
    bundle["opportunity_count"] = sum(len(p.get("opportunities", [])) for p in bundle["places"])
    bundle["generated_at"] = scoped["generated_at"]
    bundle["fetch_failures"] = scoped.get("fetch_failures", [])
    bundle["skipped"] = scoped.get("skipped", [])
    bundle["provider_runs_count"] = scoped.get("provider_runs_count", bundle.get("provider_runs_count"))


def main():
    bundle_path = os.path.join(W, "apps/web-v2/evaluations-latest.json")
    b = json.load(open(bundle_path, encoding="utf-8"))
    assert b["place_count"] >= 300, b["place_count"]
    for i, pid in enumerate(PIDS):
        one_path = f"{SCRATCH}/one.json"
        r = subprocess.run([sys.executable, "packages/core-v2/tools/evaluate_batch.py",
                            "--only-place-id", pid, "--forecast-hours", "168",
                            "--out", one_path, "--details-dir", SCRATCH + "/det"],
                           capture_output=True, text=True, cwd=W)
        one = json.load(open(one_path, encoding="utf-8"))
        splice(b, one)
        print(i + 1, pid, one["place_count"], one["opportunity_count"])
    with open(bundle_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(b, f, ensure_ascii=False, indent=2)
    print("SPLICED", b["place_count"], b["opportunity_count"], b["forecast_hours"],
          "failures", b["fetch_failures"], "skipped", b["skipped"])


if __name__ == "__main__":
    main()
