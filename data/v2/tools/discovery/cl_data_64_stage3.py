#!/usr/bin/env python3
"""CL-DATA-64 stage 3: source-lock pins for the 13 new contracts (tw-121..124,
us-159..160, jp-092..095, us-161..163) + supporting evidence registries.

Usage: python cl_data_64_stage3.py <commit_sha>  (commit whose tree carries the
exact contract bytes, same convention as cl_data_53_stage3.py).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TICKET = "CL-DATA-64"
COMMIT = sys.argv[1]
NEW = ["tw-121-P01", "tw-122-P01", "tw-123-P01", "tw-124-P01",
       "us-159-P01", "us-160-P01", "jp-092-P01", "jp-093-P01",
       "jp-094-P01", "jp-095-P01", "us-161-P01", "us-162-P01", "us-163-P01"]


def pins_for(paths, commit):
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
    lock_path = ROOT / "data/v2/indexes/research/source-lock.json"
    d = json.loads(lock_path.read_bytes().decode("utf-8"))
    pinned = {c["opportunity_id"] for c in d["canonical_records"]}
    new = [f"data/v2/opportunities/{x}.json" for x in NEW if x not in pinned]
    print("new pins:", len(new))
    d["canonical_records"].extend(pins_for(new, COMMIT))
    ss_paths = [f"data/v2/audits/{TICKET.lower()}_web_evidence.json",
                f"data/v2/audits/discovery/{TICKET.lower()}-dedupe.json"]
    have = {s["path"] for s in d["supporting_sources"]}
    for rel in ss_paths:
        if rel not in have:
            d["supporting_sources"].append(support_for(rel, COMMIT))
    d[f"repin_note_{TICKET.lower()}_20261110"] = (
        f"{TICKET}: pinned {len(new)} new canonical records (tw-121..124, us-159..160, "
        f"jp-092..095, us-161..163; tree-verified {COMMIT}) and supporting evidence "
        "registries. Owner-confirmed viewpoint/subject separation fields and REQUIRED "
        "volcanic_activity (USGS HVO, fail-closed) semantics recorded.")
    lock_path.write_bytes(json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
    print("source-lock:", len(d["canonical_records"]), "canonical,", len(d["supporting_sources"]), "supporting")


if __name__ == "__main__":
    main()
