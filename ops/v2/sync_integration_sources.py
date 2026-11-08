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
    """CL-CI-31/31c: keep w2.browse_index_source_sha on the index-creating commit.

    postmerge_verify requires browse_index_source_sha's data/v2/indexes/research
    tree to EXACTLY match HEAD's and (CL-CI-31c) the anchor to be an ancestor of
    HEAD. That invariant is NOT the w2 acceptance pointer (w2.sha), and it is
    NOT derived from w2.sha either: the ancestor-of-w2.sha requirement was
    structurally unsatisfiable for the regenerated-index flow — index regens
    land on main (e.g. the CL-DATA-35 stage chain) outside the W2 pilot branch
    lineage, so no commit can be both a tree-matching index commit and an
    ancestor of the pinned pilot sha, and the old rule silently left a broken
    anchor in place while reporting IN_SYNC. browse_index_source_sha therefore
    identifies the newest main (HEAD) ancestor commit whose research-index tree
    matches HEAD's — i.e. the commit that produced the accepted index.
    """
    pin = lock["sources"]["w2"]
    if not pin.get("sha"):
        return None
    index_tree = git(root, "rev-parse", "HEAD:data/v2/indexes/research")
    current = pin.get("browse_index_source_sha")
    if current:
        try:
            current_tree = git(root, "rev-parse", current + ":data/v2/indexes/research")
        except subprocess.CalledProcessError:
            current_tree = None  # unresolvable; fall through to re-anchor
        if (current_tree == index_tree and
                subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                                current, "HEAD"], capture_output=True).returncode == 0):
            verify_browse_chain(root, pin)
            return None
    # git log newest-first; pick the newest HEAD-ancestor commit whose index
    # subtree tree matches HEAD's (the index-creating commit). Every commit in
    # this walk is an ancestor of HEAD by construction.
    commits = git(root, "log", "--format=%H", "-n", "40", "HEAD", "--",
                  "data/v2/indexes/research").split()
    for commit in commits:
        try:
            if git(root, "rev-parse", commit + ":data/v2/indexes/research") != index_tree:
                continue
        except subprocess.CalledProcessError:
            continue
        if commit != current:
            pin["previous_browse_index_source_sha"] = current
            pin["browse_index_source_sha"] = commit
            changes.setdefault("w2", {})["browse_index_source_sha"] = {
                "previous": current, "current": commit}
        verify_browse_chain(root, pin)
        return commit
    # No tree-matching commit reachable from HEAD: the accepted index tree no
    # longer exists in main's history (index regenerated but never committed,
    # or HEAD:data/v2/indexes/research was hand-edited). Fail loudly instead of
    # silently reporting IN_SYNC against an inconsistent lock (CL-CI-31c).
    raise ValueError(
        "browse_index_source_sha unresolvable: no HEAD ancestor commit has "
        "HEAD's data/v2/indexes/research tree (" + index_tree + ") — the "
        "research index must be regenerated through the merge-regen chain")


def verify_browse_chain(root, pin):
    """CL-CI-31c: sync verifies the full precheck chain, not just its own diff.

    The auto-sync bot previously committed a lock whose browse anchor was fine
    while apps/web-v2/browse-index.v2.json / catalog.v2.json still named an
    older source commit — sync reported IN_SYNC and postmerge red-lit with
    'Browse index does not identify the accepted W2 source'. Both downstream
    source pointers must name the same commit the lock anchors."""
    browse = pin.get("browse_index_source_sha")
    bundle = json.loads((root / "apps/web-v2/browse-index.v2.json")
                        .read_text(encoding="utf-8"))
    if bundle.get("source_commit_sha") != browse:
        raise ValueError(
            "browse-index.v2.json source_commit_sha (" +
            str(bundle.get("source_commit_sha")) + ") != browse_index_source_sha (" +
            str(browse) + ") — regenerate browse-index.v2.json via the "
            "research-index/build_web_catalog merge-regen chain")
    catalog = json.loads((root / "apps/web-v2/catalog.v2.json")
                         .read_text(encoding="utf-8"))
    if catalog.get("source_index_commit_sha") != browse:
        raise ValueError(
            "catalog.v2.json source_index_commit_sha (" +
            str(catalog.get("source_index_commit_sha")) + ") != browse_index_source_sha (" +
            str(browse) + ") — regenerate catalog.v2.json via build_web_catalog")


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
        # CL-CI-31c: write LF bytes explicitly — a Windows text-mode write
        # would translate every \n to \r\n and rewrite the whole lock file
        # (repo convention is LF; whole-file EOL churn also breaks the
        # pin-sync bot's small-diff pushes).
        lock_path.write_bytes(
            (json.dumps(lock, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
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
