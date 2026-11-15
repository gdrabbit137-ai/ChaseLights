#!/usr/bin/env python3
"""CL-DATA-74 stage 3: source-lock pins for the 17 new five-genre canonical
contracts (CL-DATA-64 stage3 convention: pin the exact contract bytes at the
commit that carries them).

Usage: python cl_data_74_stage3_locks.py <commit_sha>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TICKET = "CL-DATA-74"
COMMIT = sys.argv[1]
NEW = ["tw-041-P06", "tw-042-P02", "tw-044-P04", "tw-046-P03", "jp-065-P02",
       "tw-019-P07", "tw-120-P02", "tw-093-P03", "jp-065-P03", "us-009-P02",
       "tw-151-P02", "tw-144-P03", "tw-024-P06", "tw-140-P03",
       "tw-027-P04", "tw-199-P02", "us-121-P02"]


def pins_for(paths, commit):
    recs = []
    for rel in paths:
        b = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=ROOT,
                           capture_output=True).stdout
        recs.append({
            "opportunity_id": Path(rel).stem, "path": rel,
            "blob_sha": subprocess.run(["git", "hash-object", "--stdin"], cwd=ROOT,
                                       input=b, capture_output=True).stdout.decode().strip(),
            "sha256": hashlib.sha256(b).hexdigest(), "commit_sha": commit})
    return recs


def main():
    lock_path = ROOT / "data/v2/indexes/research/source-lock.json"
    d = json.loads(lock_path.read_bytes().decode("utf-8"))
    pinned = {c["opportunity_id"] for c in d["canonical_records"]}
    new = [f"data/v2/opportunities/{x}.json" for x in NEW if x not in pinned]
    print("new pins:", len(new))
    d["canonical_records"].extend(pins_for(new, COMMIT))
    d[f"repin_note_{TICKET.lower()}_20261116"] = (
        f"{TICKET}: pinned {len(new)} new five-genre canonical records "
        "(alpenglow/snow_scene/firefly/star_trails/moonlit_scene mounts; "
        f"tree-verified {COMMIT}). Owner-approved data pack 2026-11-16; "
        "snow/firefly season windows ride the seasonal-calendar bridge "
        "(fail-closed typical-only).")
    lock_path.write_bytes(json.dumps(d, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
    print("source-lock:", len(d["canonical_records"]), "canonical,",
          len(d["supporting_sources"]), "supporting")


if __name__ == "__main__":
    main()
