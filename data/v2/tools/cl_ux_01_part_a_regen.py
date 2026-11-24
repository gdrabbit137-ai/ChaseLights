#!/usr/bin/env python3
"""CL-UX-01 Part A: scoped 168h re-evaluation for tw-082 (鯉魚潭) after adding the
civil light_window to tw-082-P01. CL-DATA-78/81/66 recipe: --only-place-id into a
temp output, then splice the place row + its detail shard into the published
bundle. Never a full-batch run (禁全量). Scoped to ONE place on purpose.

Usage: python data/v2/tools/cl_ux_01_part_a_regen.py
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TMP = Path("D:/ChaseLightsWorkspace/tmp/cl-ux-01-part-a")
IDS = ["tw-082"]


def main():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    (TMP / "details").mkdir()
    ok, fail = [], []
    for pid in IDS:
        out = TMP / f"{pid}.json"
        cmd = [sys.executable, str(ROOT / "packages/core-v2/tools/evaluate_batch.py"),
               "--only-place-id", pid, "--forecast-hours", "168",
               "--out", str(out), "--archive", str(TMP / "arch"),
               "--details-dir", str(TMP / "details")]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            fail.append((pid, (r.stderr or r.stdout)[-400:]))
            print("FAIL", pid, (r.stderr or r.stdout)[-300:])
            continue
        ok.append(pid)
        print("regen OK", pid)

    published = json.loads((ROOT / "apps/web-v2/evaluations-latest.json").read_bytes().decode("utf-8"))
    places = {p["place_id"]: p for p in published["places"]}
    skipped = list(published.get("skipped") or [])
    fetch_failures = list(published.get("fetch_failures") or [])
    for pid in ok:
        part = json.loads((TMP / f"{pid}.json").read_bytes().decode("utf-8"))
        for p in part["places"]:
            places[p["place_id"]] = p
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
    print("spliced:", len(ok), "places; bundle now", published["place_count"], "places /",
          published["opportunity_count"], "opps")
    print("failures:", fail)


if __name__ == "__main__":
    main()
