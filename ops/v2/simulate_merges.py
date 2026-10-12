#!/usr/bin/env python3
"""Rehearse the pinned main-based V2 chain in a detached checkout; never push."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ("index.html", "CNAME", "assets/app.js")
W2_BASE = "a816c833ac4f83f440d1d76350cb46da74f43013"
W3_BASE = "d24af0dbea61c158482bea9522ac36eac016843d"
W3_MIDDLE = "77b040fd1af806a564282eea7e3a7c7166a180d3"


def run(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and result.returncode:
        raise RuntimeError("git " + " ".join(args) + ": " + result.stdout)
    return result


def sha(repo, ref):
    return run(repo, "rev-parse", ref).stdout.strip()


def present(repo, ref):
    return run(repo, "cat-file", "-e", ref, check=False).returncode == 0


def fetch(repo, commit):
    if not present(repo, commit + "^{commit}"):
        run(repo, "fetch", "--no-tags", "origin", commit)


def tree(repo, commit, path):
    ref = commit + ":" + path
    return sha(repo, ref) if present(repo, ref) else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--assembly-main", type=Path, required=True)
    args = parser.parse_args()
    repo, logs = args.repo.resolve(), args.log_dir.resolve()
    logs.mkdir(parents=True, exist_ok=True)
    lines = []
    report = {"status": "FAIL", "main": None, "steps": [], "final": None}
    try:
        lock = json.loads((ROOT / "ops/v2/integration-sources.json").read_text())
        base = sha(repo, "HEAD")
        report["main"] = base
        if base != sha(args.assembly_main.resolve(), "HEAD"):
            raise RuntimeError("main changed between integration assembly and merge checkout; rerun")
        task_head = sha(ROOT, "HEAD")
        w1, w2, w3, w4 = (lock["sources"][key]["sha"] for key in ("w1", "w2", "w3", "w4"))
        steps = [
            ("W1 #450", w1, ("specs/v2/",)),
            ("W2 #440", W2_BASE, ("data/v2/",)),
            ("W2 #444", w2, ("data/v2/",)),
            ("W3 #435", W3_BASE, ("packages/core-v2/", "packages/models-v2/")),
            ("W3 #441", W3_MIDDLE, ("packages/core-v2/", "packages/models-v2/")),
            ("W3 #447", w3, ("packages/core-v2/", "packages/models-v2/")),
            ("W4 #454", w4, ("apps/web-v2/",)),
            ("W5 current HEAD", task_head, ("ops/v2/", ".github/workflows/v2-integration.yml")),
        ]
        for _, commit, _ in steps:
            fetch(repo, commit)
        historical = lock["sources"]["w4"]["historical_sha"]
        fetch(repo, historical)  # Evidence only; never merge the obsolete W4 stack.
        for older, newer in ((W2_BASE, w2), (W3_BASE, W3_MIDDLE), (W3_MIDDLE, w3)):
            if run(repo, "merge-base", "--is-ancestor", older, newer, check=False).returncode:
                raise RuntimeError("Owner chain is not an actual Git ancestor: " + older + " -> " + newer)
        web_tree = lock["sources"]["w4"]["tree_sha"]
        if tree(repo, w4, "apps/web-v2") != web_tree or tree(repo, historical, "apps/web-v2") != web_tree:
            raise RuntimeError("W4 #454/#448 web Git Trees differ from pinned 52-file source")
        paths = run(repo, "ls-tree", "-r", "--name-only", w4, "--", "apps/web-v2").stdout.splitlines()
        if len(paths) != lock["sources"]["w4"]["file_count"]:
            raise RuntimeError("W4 consolidated file count differs from reviewed source")
        if run(repo, "merge-base", "--is-ancestor", historical, w4, check=False).returncode == 0:
            raise RuntimeError("W4 #454 unexpectedly replays historical #448 ancestry")
        original_legacy = {p: sha(repo, "HEAD:" + p) for p in LEGACY}
        owner_tips = {"specs/v2": w1, "data/v2": w2,
                      "packages/core-v2": w3, "packages/models-v2": w3,
                      "apps/web-v2": w4}
        accepted = {}
        run(repo, "switch", "--detach", base)
        run(repo, "config", "user.name", "ChaseLights merge simulation")
        run(repo, "config", "user.email", "merge-simulation@localhost")
        for name, commit, allowed in steps:
            if run(repo, "merge-base", "--is-ancestor", commit, "HEAD", check=False).returncode == 0:
                raise RuntimeError(name + " already in candidate main; refresh the chain")
            before = sha(repo, "HEAD")
            merged = run(repo, "merge", "--no-ff", "--no-edit", commit, check=False)
            lines.append(name + " " + commit + "\n" + merged.stdout)
            if merged.returncode:
                conflicts = run(repo, "diff", "--name-only", "--diff-filter=U", check=False).stdout
                raise RuntimeError(name + " merge failed; unmerged paths: " + conflicts)
            after = sha(repo, "HEAD")
            changed = run(repo, "diff", "--name-only", before, after).stdout.splitlines()
            outside = [path for path in changed if not any(path.startswith(p) for p in allowed)]
            if outside or not changed:
                raise RuntimeError(name + " changed unexpected/no paths: " + repr(outside or changed))
            for path, tip in accepted.items():
                if tree(repo, "HEAD", path) != tree(repo, tip, path):
                    raise RuntimeError(name + " overwrote previously accepted owner tree: " + path)
            for path, original in original_legacy.items():
                if sha(repo, "HEAD:" + path) != original:
                    raise RuntimeError(name + " changed Legacy blob: " + path)
            if run(repo, "status", "--porcelain").stdout.strip():
                raise RuntimeError(name + " left a dirty working tree")
            if commit == w1:
                accepted["specs/v2"] = w1
            elif commit == w2:
                accepted["data/v2"] = w2
            elif commit == w3:
                for path in ("packages/core-v2", "packages/models-v2"):
                    accepted[path] = w3
            elif commit == w4:
                accepted["apps/web-v2"] = w4
            for path, tip in accepted.items():
                if tree(repo, "HEAD", path) != tree(repo, tip, path):
                    raise RuntimeError(name + " lost final owner tree: " + path)
            report["steps"].append({"name": name, "source": commit,
                                    "merge_commit": after, "changed_paths": changed})
        for path, tip in {**owner_tips, "ops/v2": task_head,
                          ".github/workflows/v2-integration.yml": task_head}.items():
            if tree(repo, "HEAD", path) != tree(repo, tip, path):
                raise RuntimeError("Final tree/blob lost source bytes: " + path)
        if run(repo, "merge-base", "--is-ancestor", historical, "HEAD", check=False).returncode == 0:
            raise RuntimeError("Obsolete W4 #448 chain was included as a duplicate")
        if sha(repo, "HEAD:apps/web-v2") != web_tree:
            raise RuntimeError("Final website tree drifted")
        report["final"] = sha(repo, "HEAD")
        report["w4_web_tree"] = web_tree
        report["w4_file_count"] = len(paths)
        report["status"] = "PASS"
    except Exception as exc:
        report["error"] = str(exc)
        lines.append("FAIL: " + str(exc))
    (logs / "merge-simulation.log").write_text("\n".join(lines) + "\n")
    (logs / "merge-simulation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "main": report["main"],
                      "steps": len(report["steps"]), "final": report["final"],
                      "error": report.get("error")}))
    return report["status"] != "PASS"


if __name__ == "__main__":
    sys.exit(main())
