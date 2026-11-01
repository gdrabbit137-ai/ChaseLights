"""Set source-lock commit_sha to the CL-DATA-01 data commit for the records
whose bytes that commit changed (precedent: 640960c20)."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT = Path(r"D:\d\Dick\Project\ChaseLights-wt-CL-DATA-01")
LOCK = ROOT / "data/v2/indexes/research/source-lock.json"
DATA_COMMIT = sys.argv[1]
changed = subprocess.check_output(
    ["git", "-C", str(ROOT), "diff", "--name-only", DATA_COMMIT + "^", DATA_COMMIT],
    text=True).split()
changed_rel = {"data/v2/opportunities/" + p for p in (x.rsplit("/", 1)[-1] for x in changed)
               if p.endswith(".json")}
lock = json.loads(LOCK.read_text(encoding="utf-8"))
n = 0
for rec in lock["canonical_records"]:
    if rec["path"] in changed_rel:
        rec["commit_sha"] = DATA_COMMIT
        n += 1
LOCK.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
print(json.dumps({"commit_sha_updated": n, "data_commit": DATA_COMMIT}))
