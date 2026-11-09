#!/usr/bin/env python3
"""CL-DATA-53 stage 3: source-lock pins for the 41 new contracts (us-119..us-158)
+ supporting_sources entries for the new evidence registries."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TICKET = "CL-DATA-53"
COMMIT = sys.argv[1]  # commit whose tree carries the exact contract bytes


def pins_for(paths, commit):
    recs = []
    for rel in paths:
        b = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=ROOT,
                           capture_output=True).stdout
        recs.append({
            "opportunity_id": Path(rel).stem,
            "path": rel,
            "blob_sha": subprocess.run(["git", "hash-object", "--stdin"], cwd=ROOT,
                                       input=b, capture_output=True, text=True).stdout.strip(),
            "sha256": hashlib.sha256(b).hexdigest(),
            "commit_sha": commit,
        })
    return recs


def support_for(rel, commit):
    b = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=ROOT, capture_output=True).stdout
    return {"path": rel,
            "commit_sha": commit,
            "blob_sha": subprocess.run(["git", "hash-object", "--stdin"], cwd=ROOT,
                                       input=b, capture_output=True, text=True).stdout.strip(),
            "sha256": hashlib.sha256(b).hexdigest()}


def main():
    lock_path = ROOT / "data/v2/indexes/research/source-lock.json"
    d = json.loads(lock_path.read_bytes().decode("utf-8"))
    pinned = {c["opportunity_id"] for c in d["canonical_records"]}
    paths = sorted(str(p.relative_to(ROOT)).replace("\\", "/")
                   for p in (ROOT / "data/v2/opportunities").glob("us-1[0-9][0-9]-P*.json"))
    new = [p for p in paths if Path(p).stem not in pinned]
    print("new pins:", len(new))
    d["canonical_records"].extend(pins_for(new, COMMIT))
    ss_paths = [f"data/v2/audits/{TICKET.lower()}_web_evidence.json",
                f"data/v2/audits/discovery/{TICKET.lower()}-dedupe.json"]
    have = {s["path"] for s in d["supporting_sources"]}
    for rel in ss_paths:
        if rel not in have:
            d["supporting_sources"].append(support_for(rel, COMMIT))
    note = (f"repin_note_{TICKET.lower()}_20261109",
            f"{TICKET}: pinned {len(new)} new canonical records (us-119..us-158, tree-verified "
            f"{COMMIT}) and supporting evidence registries {ss_paths}. Stage-1b also backfilled the "
            "22 CL-DATA-42/43 legacy runtime spots (us-097..118); their contracts were already "
            "pinned, no re-pin needed.")
    key, msg = note
    d[key] = msg
    (ROOT / "data/v2/indexes/research/source-lock.json").write_bytes(
        json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8"))
    print("source-lock updated:", len(d["canonical_records"]), "canonical,", len(d["supporting_sources"]), "supporting")


if __name__ == "__main__":
    main()
