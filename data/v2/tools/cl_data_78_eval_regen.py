#!/usr/bin/env python3
"""CL-DATA-78 Phase 1 — scoped 168h evaluations regen for star-sky places whose
moon_target_separation_deg contracts carry a resolvable view azimuth (tw-036 /
tw-038 / tw-076 / tw-080). CL-UI-25/CL-DATA-66 recipe: --only-place-id into temp
outputs (never clobbering the published bundle), then splice the place rows +
per-place detail shards. Never a full-batch run (禁全量)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TMP = Path("D:/tmp/cld78_eval")
TMP.mkdir(parents=True, exist_ok=True)

ids = ["tw-036", "tw-038", "tw-076", "tw-080"]
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

if fail:
    sys.exit(1)

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
out_path = ROOT / "apps/web-v2/evaluations-latest.json"
out_path.write_bytes(json.dumps(published, ensure_ascii=False, indent=1).encode("utf-8"))
print(f"spliced: +{new_place_count} places (+{new_opp_count} opp rows) -> {out_path.name}")
