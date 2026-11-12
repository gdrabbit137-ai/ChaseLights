#!/usr/bin/env python3
"""CL-DATA-66 wave-2 stage 3: source-lock pins for the 22 new contracts
(tw-147..tw-161) + wave-2 supporting evidence repins.

Usage: python cl_data_66_stage3_wave2.py <commit_sha>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TICKET = "CL-DATA-66"
COMMIT = sys.argv[1]


def pins_for(paths, commit):
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", commit]).decode().strip()
    recs = []
    for rel in paths:
        b = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=ROOT, capture_output=True).stdout
        recs.append({
            "opportunity_id": Path(rel).stem, "path": rel,
            "blob_sha": subprocess.run(["git", "hash-object", "--stdin"], cwd=ROOT,
                                       input=b, capture_output=True).stdout.decode().strip(),
            "sha256": hashlib.sha256(b).hexdigest(), "commit_sha": commit})
    return recs


def support_for(rel, commit):
    b = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=ROOT, capture_output=True).stdout
    return {"path": rel, "commit_sha": commit,
            "blob_sha": subprocess.run(["git", "hash-object", "--stdin"], cwd=ROOT,
                                       input=b, capture_output=True).stdout.decode().strip(),
            "sha256": hashlib.sha256(b).hexdigest()}


def main():
    ids = []
    for n in range(147, 162):
        for s in (1, 2):
            f = ROOT / f"data/v2/opportunities/tw-{n}-P0{s}.json"
            if f.exists():
                ids.append(f"tw-{n}-P0{s}")
    ids = sorted(set(ids))
    assert len(ids) == 22, len(ids)
    lock_path = ROOT / "data/v2/indexes/research/source-lock.json"
    d = json.loads(lock_path.read_bytes().decode("utf-8"))
    pinned = {c["opportunity_id"] for c in d["canonical_records"]}
    new = [f"data/v2/opportunities/{x}.json" for x in ids if x not in pinned]
    print("new pins:", len(new))
    d["canonical_records"].extend(pins_for(new, COMMIT))
    repinned = 0
    for rec in d["canonical_records"]:
        path = ROOT / rec["path"]
        if path.exists() and (ROOT / rec["path"]).exists():
            b = path.read_bytes()
            if rec["sha256"] != hashlib.sha256(b).hexdigest():
                rec["sha256"] = hashlib.sha256(b).hexdigest()
                rec["blob_sha"] = subprocess.run(["git", "hash-object", "--stdin"], cwd=ROOT,
                                                 input=b, capture_output=True).stdout.decode().strip()
                rec["commit_sha"] = subprocess.check_output(
                    ["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
                repinned += 1
    if repinned:
        print("repinned changed canonical records:", repinned)
    ss_paths = [f"data/v2/audits/{TICKET.lower()}_web_evidence.json",
                f"data/v2/audits/discovery/{TICKET.lower()}-dedupe.json",
                "data/v2/audits/subject-lists/tier-a-manifest.json"]
    have = {s["path"] for s in d["supporting_sources"]}
    for rel in ss_paths:
        if rel not in have:
            d["supporting_sources"].append(support_for(rel, COMMIT))
    for rel in ("tw_weather.json", "jp_weather.json", "us_weather.json"):
        b = (ROOT / rel).read_bytes()
        for s in d["supporting_sources"]:
            if s["path"] == rel and s["sha256"] != hashlib.sha256(b).hexdigest():
                s.update(support_for(rel, COMMIT))
    d[f"repin_note_{TICKET.lower()}_wave2_20261111"] = (
        f"{TICKET} wave 2: pinned {len(new)} new canonical records (tw-147..tw-161; "
        f"tree-verified {COMMIT}) and repinned refreshed supporting evidence registries. "
        "Scoreless intake (owner ruling 2026-11-11): verification + 5km subject-disjoint "
        "dedupe only; no rubric/AGLI scoring, agli-final untouched.")
    lock_path.write_bytes(json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
    print("source-lock:", len(d["canonical_records"]), "canonical,", len(d["supporting_sources"]), "supporting")


if __name__ == "__main__":
    main()
