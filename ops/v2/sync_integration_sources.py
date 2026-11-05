#!/usr/bin/env python3
"""Auto-sync the W1–W4 owner tree pins in integration-sources.json.

The old model pinned each owner subtree to a frozen tree_sha/file_count that
every ticket touching those trees had to re-pin by hand. The new normal is:
after a fully-green postmerge_verify run, CI (or a developer) runs this script
and the pins follow the tree automatically.

Guard rails that survive automation:
- sync never *lowers* a pinned file_count. Deleting subtree files therefore
  fails verification until the removal is accepted explicitly with
  --accept-decrease (recorded in the lock for audit).
- postmerge_verify still enforces exact per-suite test counts, reviewed blob
  pins and canonical record pins, so a broken tree cannot self-certify.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

OWNER_PATHS = {
    "w1": ("specs/v2",),
    "w2": ("data/v2",),
    "w4": ("apps/web-v2",),
}


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def current_trees(root):
    out = {}
    for owner, paths in OWNER_PATHS.items():
        tree = git(root, "rev-parse", "HEAD:" + paths[0])
        count = len(git(root, "ls-tree", "-r", "--name-only", "HEAD", paths[0]).splitlines())
        out[owner] = {"tree_sha": tree, "file_count": count, "paths": list(paths)}
    return out


def sync(root, accept_decrease=False):
    lock_path = root / "ops/v2/integration-sources.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    trees = current_trees(root)
    changes, refusals = {}, []
    for owner, info in trees.items():
        pin = lock["sources"][owner]
        old_tree, old_count = pin.get("tree_sha"), pin.get("file_count")
        if old_tree != info["tree_sha"]:
            pin["previous_tree_sha"] = old_tree
            pin["tree_sha"] = info["tree_sha"]
            changes[owner] = {"path": info["paths"][0], "previous_tree_sha": old_tree,
                              "tree_sha": info["tree_sha"]}
        if old_count != info["file_count"]:
            if old_count is not None and info["file_count"] < old_count and not accept_decrease:
                refusals.append(f"{owner} {info['paths'][0]}: file_count "
                                f"{old_count} -> {info['file_count']} (decrease requires --accept-decrease)")
            else:
                if old_count is not None and info["file_count"] < old_count:
                    pin["accepted_file_count_decrease"] = {
                        "previous_file_count": old_count,
                        "file_count": info["file_count"], "via": "--accept-decrease",
                    }
                pin["previous_file_count"] = old_count
                pin["file_count"] = info["file_count"]
                changes.setdefault(owner, {})["file_count"] = {
                    "previous": old_count, "current": info["file_count"]}
    if refusals:
        raise ValueError("Refusing to lower pinned file_count: " + "; ".join(refusals))
    if changes:
        lock_path.write_text(json.dumps(lock, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--accept-decrease", action="store_true")
    parser.add_argument("--check", action="store_true",
                        help="Fail if the pins are stale instead of updating them")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.check:
        lock = json.loads((root / "ops/v2/integration-sources.json").read_text(encoding="utf-8"))
        stale = {owner: {"path": info["paths"][0], "pinned_tree_sha": lock["sources"][owner]["tree_sha"],
                         "current_tree_sha": info["tree_sha"]}
                 for owner, info in current_trees(root).items()
                 if lock["sources"][owner]["tree_sha"] != info["tree_sha"]}
        if stale:
            print(json.dumps({"status": "STALE", "stale": stale}))
            return 1
        print(json.dumps({"status": "IN_SYNC"}))
        return 0
    changes = sync(root, args.accept_decrease)
    print(json.dumps({"status": "SYNCED" if changes else "IN_SYNC", "changes": changes}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
