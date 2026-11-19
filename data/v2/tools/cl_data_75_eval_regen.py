#!/usr/bin/env python3
"""CL-DATA-75 Phase 0 — scoped 168h evaluations regen for the §1-affected places.

Per CL-UI-25/CL-DATA-66 recipe: evaluate_batch --only-place-id per place into
temp outputs (never clobbering the published bundle), then splice the place
rows + per-place detail shards into apps/web-v2/evaluations-latest.json /
apps/web-v2/evaluations-details/. Never a full-batch run (禁全量).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TMP = Path("D:/ChaseLightsWorkspace/tmp/data75_eval")
TMP.mkdir(parents=True, exist_ok=True)

ids = [l.strip() for l in (ROOT / "../../data75_places.txt").read_text().splitlines() if l.strip()]
ok, fail = [], []
for pid in ids:
    out = TMP / f"{pid}.json"
    if out.exists():
        ok.append(pid)
        continue
    cmd = [sys.executable, str(ROOT / "packages/core-v2/tools/evaluate_batch.py"),
           "--only-place-id", pid, "--forecast-hours", "168",
           "--out", str(out), "--archive", str(TMP / "arch"),
           "--details-dir", str(TMP / "details")]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        fail.append((pid, r.stderr[-300:]))
        print("FAIL", pid, r.stderr[-150:], flush=True)
        continue
    ok.append(pid)
    print("regen OK", pid, flush=True)

published = json.loads((ROOT / "apps/web-v2/evaluations-latest.json").read_bytes().decode("utf-8"))
places = {p["place_id"]: p for p in published["places"]}
skipped = list(published.get("skipped") or [])
fetch_failures = list(published.get("fetch_failures") or [])
new_place_count = new_opp_count = 0
for pid in ok:
    part = json.loads((TMP / f"{pid}.json").read_bytes().decode("utf-8"))
    for p in part["places"]:
        places[p["place_id"]] = p
        new_place_count += 1
        new_opp_count += len(p.get("opportunities") or [])
    for s in part.get("skipped") or []:
        if s not in skipped:
            skipped.append(s)
    for s in part.get("fetch_failures") or []:
        if s not in fetch_failures:
            fetch_failures.append(s)
    src = TMP / "details" / f"{pid}.json"
    if src.exists():
        (ROOT / f"apps/web-v2/evaluations-details/{pid}.json").write_bytes(src.read_bytes())

published["places"] = sorted(places.values(), key=lambda p: p["place_id"])
published["place_count"] = len(published["places"])
published["opportunity_count"] = sum(len(p.get("opportunities") or []) for p in published["places"])
published["skipped"] = skipped
published["fetch_failures"] = fetch_failures
(ROOT / "apps/web-v2/evaluations-latest.json").write_bytes(
    json.dumps(published, ensure_ascii=False).encode("utf-8"))
print("spliced:", new_place_count, "places /", new_opp_count, "opps;",
      "bundle now", published["place_count"], "places /", published["opportunity_count"], "opps")
print("failures:", fail)
