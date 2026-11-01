"""Re-pin changed canonical records in data/v2/indexes/research/source-lock.json.

Updates blob_sha/sha256 for every record whose working-tree bytes differ from
the pin. commit_sha is set to the task-branch HEAD (bytes live on this branch;
the reviewer/PM gate re-verifies). LF bytes as committed convention.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\d\Dick\Project\ChaseLights-wt-CL-DATA-01")
LOCK = ROOT / "data/v2/indexes/research/source-lock.json"


def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def main():
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    head = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
    changed = []
    for rec in lock["canonical_records"]:
        path = ROOT / rec["path"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != rec["sha256"] or blob(raw) != rec["blob_sha"]:
            rec["sha256"] = hashlib.sha256(raw).hexdigest()
            rec["blob_sha"] = blob(raw)
            rec["commit_sha"] = head
            changed.append(rec["path"])
    LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
    print(json.dumps({"repinned": len(changed), "head": head}, ensure_ascii=False))
    for c in changed:
        print(" -", c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
