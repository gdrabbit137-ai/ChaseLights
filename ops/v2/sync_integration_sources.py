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
import re
import subprocess
import sys
from pathlib import Path

# CL-CI-10: w3 owns two subtrees (packages/core-v2, packages/models-v2).
# Leaving w3 out of this map was the Round 9 race: sync refreshed only the
# w1/w2/w4 pins while verify_main still checked the w3 subtrees against a
# frozen tree_sha, so every push touching packages/** red-lit V2 Integration
# ("w3 subtree pin differs") until a manual re-pin landed.
OWNER_PATHS = {
    "w1": ("specs/v2",),
    "w2": ("data/v2",),
    "w3": ("packages/core-v2", "packages/models-v2"),
    "w4": ("apps/web-v2",),
}

# Lock key for a subtree beyond the owner's primary path. The w3 lock already
# uses "models_tree_sha" for packages/models-v2 (CL-CI-10 keeps that key).
EXTRA_TREE_KEYS = {"packages/models-v2": "models_tree_sha"}


def tree_sha_key(path):
    return (EXTRA_TREE_KEYS.get(path) or
            path.rsplit("/", 1)[-1].replace("-", "_") + "_tree_sha")


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


# CL-CI-13: the scheduled evaluations workflow rotates data/v2/evaluations
# bundles with a rolling retention (oldest bundle-<timestamp>.json files are
# deleted, a fresh one is added). That is generated-artifact churn, not a
# suspicious hand deletion — before this carve-out, the first bundle rotation
# after a green pin sync permanently red-lit every push (the 1746 -> 1743
# refusal) because sync refuses to lower file_count. Rotation paths are still
# counted normally (no exemption); the decrease is just auto-accepted and
# recorded for audit. Any OTHER deleted file still requires --accept-decrease.
GENERATED_BUNDLE_RE = re.compile(r"^data/v2/evaluations/bundle-\d{8}T\d{6}Z\.json$")


def generated_bundle_rotation(root, owner_path, old_tree, new_tree):
    """Deleted paths between two subtree trees if ALL of them are generated
    bundle rotations; None when nothing was deleted or any deletion is not a
    generated bundle. `git diff` between two subtree TREES reports paths
    relative to that subtree, so they are re-anchored to owner_path."""
    if not old_tree or not new_tree or old_tree == new_tree:
        return None
    deleted = []
    for line in git(root, "diff", "--name-status", old_tree, new_tree).splitlines():
        parts = line.split("\t")
        status = parts[0] if parts else ""
        if status == "D" and len(parts) >= 2:
            deleted.append(parts[1])
        elif status.startswith("R") and len(parts) >= 3:
            deleted.append(parts[1])
    if not deleted:
        return None
    full = [p if p.startswith(owner_path + "/") else f"{owner_path}/{p}"
            for p in deleted]
    if not all(GENERATED_BUNDLE_RE.match(p) for p in full):
        return None
    return full


def current_trees(root):
    def _rev(path):
        # A path absent from HEAD (e.g. every file deleted) has no tree;
        # report None so the file_count guard (0 files) refuses the drop
        # instead of crashing the sync.
        proc = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD:" + path],
                              capture_output=True, check=False, text=True)
        return proc.stdout.strip() if proc.returncode == 0 else None

    def _count(path):
        proc = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "HEAD", path],
            capture_output=True, check=False, text=True)
        return len(proc.stdout.splitlines()) if proc.returncode == 0 else 0

    out = {}
    for owner, paths in OWNER_PATHS.items():
        # Per-subtree tree SHAs. paths[0] keeps the legacy "tree_sha" key;
        # every additional subtree is keyed by tree_sha_key(path) so w3's
        # models-v2 subtree is pinned independently of core-v2.
        trees = {p: _rev(p) for p in paths}
        count = sum(_count(p) for p in paths)
        info = {"tree_sha": trees[paths[0]], "file_count": count, "paths": list(paths)}
        for p in paths[1:]:
            info[tree_sha_key(p)] = trees[p]
        out[owner] = info
    return out


def reanchor_browse_index_source(root, lock, changes):
    """CL-CI-31: keep w2.browse_index_source_sha on the index-creating commit.

    postmerge_verify requires browse_index_source_sha's
    data/v2/indexes/research tree to EXACTLY match HEAD's. That invariant is
    NOT the w2 acceptance pointer (w2.sha): w2.sha advances with
    contract/evaluation work whose tree generally differs from the accepted
    browse index, so pointing this key at w2.sha (or re-anchoring it together
    with w2.sha during a merge) reds V2 Integration with "W2 pilot changed
    the accepted browse index" on the next push. Auto-sync therefore never
    derives this key from w2.sha: it re-anchors to the newest commit that
    (a) actually touched data/v2/indexes/research and (b) is an ancestor of
    w2.sha with a matching index tree — i.e. the browse-index-creating commit.
    """
    pin = lock["sources"]["w2"]
    w2_sha = pin.get("sha")
    if not w2_sha:
        return None
    index_tree = git(root, "rev-parse", "HEAD:data/v2/indexes/research")
    current = pin.get("browse_index_source_sha")
    if current:
        try:
            if git(root, "rev-parse", current + ":data/v2/indexes/research") == index_tree:
                return None
        except subprocess.CalledProcessError:
            pass  # current value unresolvable; fall through to re-anchor
    # git log newest-first; pick the first commit whose index subtree tree
    # matches HEAD's and which is an ancestor of the accepted w2 pointer.
    commits = git(root, "log", "--format=%H", "-n", "40", "HEAD", "--",
                  "data/v2/indexes/research").split()
    for commit in commits:
        try:
            if git(root, "rev-parse", commit + ":data/v2/indexes/research") != index_tree:
                continue
        except subprocess.CalledProcessError:
            continue
        if subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                           commit, w2_sha], capture_output=True).returncode:
            continue
        if commit != current:
            pin["previous_browse_index_source_sha"] = current
            pin["browse_index_source_sha"] = commit
            changes.setdefault("w2", {})["browse_index_source_sha"] = {
                "previous": current, "current": commit}
        return commit
    # No matching commit found: leave the pin untouched and let
    # postmerge_verify report the drift honestly rather than guessing.
    return None


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
        # CL-CI-10: additional owned subtrees (w3 models-v2) follow the same
        # auto-sync guard rails as the primary subtree.
        for extra_path in info["paths"][1:]:
            key = tree_sha_key(extra_path)
            old_extra = pin.get(key)
            if old_extra != info[key]:
                pin["previous_" + key] = old_extra
                pin[key] = info[key]
                changes.setdefault(owner, {})[extra_path] = {
                    "previous_" + key: old_extra, key: info[key]}
        if old_count != info["file_count"]:
            if old_count is not None and info["file_count"] < old_count and not accept_decrease:
                # CL-CI-13: a decrease caused purely by generated evaluations
                # bundle rotation is auto-accepted (and recorded); any other
                # deletion still requires --accept-decrease.
                rotated = generated_bundle_rotation(
                    root, info["paths"][0], old_tree, info["tree_sha"])
                if rotated is None:
                    refusals.append(f"{owner} {info['paths'][0]}: file_count "
                                    f"{old_count} -> {info['file_count']} (decrease requires --accept-decrease)")
                else:
                    pin["accepted_file_count_decrease"] = {
                        "previous_file_count": old_count,
                        "file_count": info["file_count"],
                        "via": "auto-generated-bundle-rotation",
                        "generated_paths": rotated,
                    }
                    pin["previous_file_count"] = old_count
                    pin["file_count"] = info["file_count"]
                    changes.setdefault(owner, {})["file_count"] = {
                        "previous": old_count, "current": info["file_count"]}
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
    reanchor_browse_index_source(root, lock, changes)
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
        stale = {owner: {key: lock["sources"][owner].get(key),
                         "current": info[key]}
                 for owner, info in current_trees(root).items()
                 for key in ["tree_sha"] + [tree_sha_key(p) for p in info["paths"][1:]]
                 if lock["sources"][owner].get(key) != info[key]}
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
