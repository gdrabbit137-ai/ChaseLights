#!/usr/bin/env python3
"""Simulate the reviewed PR chain on a detached copy of current main; never push."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

CHAINS = [
    ("W1 #450", "bf60a497e5338a45bda63d9bc24b33e9ea1d3b43", ("specs/v2/",)),
    ("W2 #440", "a816c833ac4f83f440d1d76350cb46da74f43013", ("data/v2/",)),
    ("W2 #444", "8725bf13348dfae371ae8358930a25dd424a3361", ("data/v2/",)),
    ("W3 #435", "d24af0dbea61c158482bea9522ac36eac016843d", ("packages/core-v2/", "packages/models-v2/")),
    ("W3 #441", "77b040fd1af806a564282eea7e3a7c7166a180d3", ("packages/core-v2/", "packages/models-v2/")),
    ("W3 #447", "b26a014fec9705d40f794ae3ddb02530d3cb5574", ("packages/core-v2/", "packages/models-v2/")),
    ("W4 owner base", "e931981a31d2ade1a94f921edd66f069027ec47c", ("apps/web-v2/",)),
    ("W4 #436", "7cc1ac237f806c737113bc753e1e8d1996b07c43", ("apps/web-v2/",)),
    ("W4 #442", "9fe8816e8e1c4d284cc56ee0435fc62278577fe7", ("apps/web-v2/",)),
    ("W4 #443", "97f7b5744d3b37153176dff12c9d87eac287df02", ("apps/web-v2/",)),
    ("W4 #446", "ff11d330884be5fdc90853f9dc100b012278c2f3", ("apps/web-v2/",)),
    ("W4 #448", "ddf9f2c4bd2eeb556bf0aa3b244f01de3256b05f", ("apps/web-v2/",)),
]
TIPS = {"specs/v2": CHAINS[0][1], "data/v2": CHAINS[2][1],
        "packages/core-v2": CHAINS[5][1], "apps/web-v2": CHAINS[11][1]}
LEGACY = ("index.html", "CNAME", "assets/app.js")


def run(repo, *args, check=True):
    p = subprocess.run(["git", "-C", str(repo), *args], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and p.returncode:
        raise RuntimeError("git " + " ".join(args) + ": " + p.stdout)
    return p


def sha(repo, ref):
    return run(repo, "rev-parse", ref).stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    log_dir = args.log_dir.resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    report = {"status": "FAIL", "main": None, "steps": [], "final": None}
    try:
        base = sha(repo, "HEAD")
        report["main"] = base
        legacy = {p: sha(repo, "HEAD:" + p) for p in LEGACY}
        task = Path(__file__).resolve().parents[2]
        w5 = sha(task, "HEAD")
        steps = CHAINS + [("W5 Task J", w5, ("ops/v2/", ".github/workflows/v2-integration.yml"))]
        run(repo, "switch", "--detach", base)
        run(repo, "config", "user.name", "ChaseLights merge simulation")
        run(repo, "config", "user.email", "merge-simulation@localhost")
        for name, commit, allowed in steps:
            if not run(repo, "cat-file", "-e", commit + "^{commit}", check=False).returncode == 0:
                run(repo, "fetch", "--no-tags", "origin", commit)
            if run(repo, "merge-base", "--is-ancestor", commit, "HEAD", check=False).returncode == 0:
                raise RuntimeError(name + " already on candidate main; refresh the chain")
            before = sha(repo, "HEAD")
            merged = run(repo, "merge", "--no-ff", "--no-edit", commit, check=False)
            lines.append(name + " " + commit + "\n" + merged.stdout)
            if merged.returncode:
                conflict = run(repo, "diff", "--name-only", "--diff-filter=U", check=False).stdout
                raise RuntimeError(name + " merge failed; unmerged paths: " + conflict)
            after = sha(repo, "HEAD")
            changed = run(repo, "diff", "--name-only", before, after).stdout.splitlines()
            outside = [p for p in changed if not any(p.startswith(a) for a in allowed)]
            if outside or not changed:
                raise RuntimeError(name + " changed unexpected/no paths: " + repr(outside or changed))
            report["steps"].append({"name": name, "source": commit, "merge_commit": after,
                                    "changed_paths": changed})
        for path, commit in {**TIPS, "ops/v2": w5,
                             ".github/workflows/v2-integration.yml": w5}.items():
            if sha(repo, "HEAD:" + path) != sha(repo, commit + ":" + path):
                raise RuntimeError("Final tree lost source bytes: " + path)
        for path, original in legacy.items():
            if sha(repo, "HEAD:" + path) != original:
                raise RuntimeError("Legacy path changed: " + path)
        report["final"] = sha(repo, "HEAD")
        report["status"] = "PASS"
    except Exception as exc:
        report["error"] = str(exc)
        lines.append("FAIL: " + str(exc))
    (log_dir / "merge-simulation.log").write_text("\n".join(lines) + "\n")
    (log_dir / "merge-simulation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "main": report["main"],
                      "steps": len(report["steps"]), "final": report["final"],
                      "error": report.get("error")}))
    return report["status"] != "PASS"


if __name__ == "__main__":
    sys.exit(main())
