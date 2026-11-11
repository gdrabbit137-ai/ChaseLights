#!/usr/bin/env python3
"""CL-DATA-66 wave 1: scoped 168h evaluations regen for tw-125..tw-146,
spliced into apps/web-v2/evaluations-latest.json + per-place detail shards."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TMP = Path("C:/tmp/ev66")
if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)

ids = [f"tw-{n}" for n in range(125, 147)]
ok, fail = [], []
for pid in ids:
    out = TMP / f"{pid}.json"
    cmd = [sys.executable, str(ROOT / "packages/core-v2/tools/evaluate_batch.py"),
           "--only-place-id", pid, "--forecast-hours", "168",
           "--out", str(out), "--archive", str(TMP / "arch"),
           "--details-dir", str(TMP / "details")]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        fail.append((pid, r.stderr[-400:]))
        print("FAIL", pid, r.stderr[-200:])
        continue
    ok.append(pid)
    print("regen OK", pid)

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
