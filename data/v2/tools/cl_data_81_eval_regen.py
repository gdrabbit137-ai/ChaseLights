#!/usr/bin/env python3
"""CL-DATA-81 — scoped 168h evaluations regen for the 37 condition-affected
places (3 sea-view sunrise visibility/aod gates + 34 star contracts whose
moonlight M1 gate was deduped). CL-DATA-78 recipe: --only-place-id into temp
outputs (never clobbering the published bundle), verdict BEFORE/AFTER
snapshots + comparison, then splice place rows + per-place detail shards.
Never a full-batch run (禁全量).

Usage: python data/v2/tools/cl_data_81_eval_regen.py before|regen|splice|compare
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TMP = Path("D:/ChaseLightsWorkspace/tmp/cl-data-81-regen")
BEFORE = Path("D:/ChaseLightsWorkspace/tmp/cl-data-81-before.json")
AFTER = Path("D:/ChaseLightsWorkspace/tmp/cl-data-81-after.json")
IDS = ["jp-008", "jp-021", "jp-022", "jp-042", "jp-089", "jp-090",
       "tw-019", "tw-024", "tw-035", "tw-036", "tw-038", "tw-040",
       "tw-045", "tw-070", "tw-072", "tw-075", "tw-076", "tw-080",
       "tw-091", "tw-093", "tw-094", "tw-095", "tw-140", "tw-144",
       "us-001", "us-005", "us-006", "us-014", "us-018", "us-097",
       "us-100", "us-106", "us-108", "us-112", "us-115", "us-149", "us-153"]
LATEST = ROOT / "apps/web-v2/evaluations-latest.json"


def affected_oids():
    out = set()
    for pid in IDS:
        for path in (ROOT / "data/v2/opportunities").glob(f"{pid}-P*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            if doc.get("lifecycle_status") != "retired":
                out.add(doc["opportunity_id"])
    return sorted(out)


def snapshot(path):
    doc = json.loads(LATEST.read_bytes().decode("utf-8"))
    want = set(affected_oids())
    out = {}
    for place in doc["places"]:
        for opp in place.get("opportunities") or []:
            if opp["opportunity_id"] not in want:
                continue
            days = {}
            for day in opp.get("days") or []:
                days[day["local_date"]] = {
                    "state": day.get("state"),
                    "good_hours": len(day.get("good_hours") or []),
                    "hour_counts": day.get("hour_counts"),
                }
            out[opp["opportunity_id"]] = {
                "genre_template": opp.get("genre_template"),
                "contract_sha": opp.get("condition_contract_sha256"),
                "days": days,
            }
    Path(path).write_text(json.dumps(out, ensure_ascii=False, indent=1),
                          encoding="utf-8", newline="\n")
    print("snapshotted", path, len(out), "opportunities")


def regen():
    TMP.mkdir(parents=True, exist_ok=True)
    ok, fail = [], []
    for i, pid in enumerate(IDS, 1):
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
            fail.append(pid)
            print("FAIL", pid, (r.stderr or "")[-150:], flush=True)
        else:
            ok.append(pid)
            print(f"[{i}/{len(IDS)}] regen OK {pid}", flush=True)
    print(f"REGEN DONE ok={len(ok)} fail={len(fail)}")
    if fail:
        sys.exit(1)


def splice():
    published = json.loads(LATEST.read_bytes().decode("utf-8"))
    places = {p["place_id"]: p for p in published["places"]}
    skipped = list(published.get("skipped") or [])
    fetch_failures = list(published.get("fetch_failures") or [])
    n_p = n_o = 0
    for pid in IDS:
        part = json.loads((TMP / f"{pid}.json").read_bytes().decode("utf-8"))
        for p in part["places"]:
            places[p["place_id"]] = p
            n_p += 1
            n_o += len(p.get("opportunities") or [])
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
    published["opportunity_count"] = sum(
        len(p.get("opportunities") or []) for p in published["places"])
    published["skipped"] = skipped
    published["fetch_failures"] = fetch_failures
    LATEST.write_bytes(json.dumps(published, ensure_ascii=False, indent=1).encode("utf-8"))
    print(f"spliced: +{n_p} places (+{n_o} opp rows) -> {LATEST.name}")


def compare():
    before = json.loads(BEFORE.read_text(encoding="utf-8"))
    after = json.loads(AFTER.read_text(encoding="utf-8"))
    changed, unchanged = [], []
    for oid in sorted(set(before) | set(after)):
        b, a = before.get(oid), after.get(oid)
        if b is None or a is None:
            changed.append((oid, [("opportunity", "PLACE_OP_REMOVED_OR_ADDED")]))
            continue
        diffs = []
        for date in sorted(set(b["days"]) | set(a["days"])):
            bd, ad = b["days"].get(date), a["days"].get(date)
            if bd is None or ad is None:
                diffs.append((date, "day_set_changed"))
            elif bd["state"] != ad["state"]:
                diffs.append((date, f"state {bd['state']}->{ad['state']}"))
            elif bd["good_hours"] != ad["good_hours"]:
                diffs.append((date, f"good_hours {bd['good_hours']}->{ad['good_hours']}"))
            elif bd["hour_counts"] != ad["hour_counts"]:
                diffs.append((date, "hour_counts_changed"))
        if diffs:
            changed.append((oid, diffs))
        else:
            contract_changed = b["contract_sha"] != a["contract_sha"]
            unchanged.append((oid, "contract_sha_changed_only" if contract_changed else "identical"))
    lines = [f"opportunities compared: {len(set(before) | set(after))}; "
             f"verdict-changed: {len(changed)}; unchanged: {len(unchanged)}"]
    lines += [f"CHANGED {oid}\t{str(d)[:240]}" for oid, d in changed]
    out = ROOT / "data/v2/audits/cl-data-81-verdict-comparison.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines[:12]))
    print("WROTE", out)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "before":
        snapshot(BEFORE)
    elif mode == "after":
        snapshot(AFTER)
    elif mode == "regen":
        regen()
    elif mode == "splice":
        splice()
    elif mode == "compare":
        compare()
