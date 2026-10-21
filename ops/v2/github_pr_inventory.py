#!/usr/bin/env python3
"""Read-only GitHub PR evidence inventory, not an authorization to merge.

Uses GitHub's public REST endpoints with an optional GITHUB_TOKEN. Outputs raw
observations and UNKNOWN for facts not proven by these endpoints. No writes.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def get_json(path, token=None):
    request = urllib.request.Request(
        "https://api.github.com/" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "ChaseLights-W5-readonly-inventory",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": "Bearer " + token} if token else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def collect(owner, repo, number, fetch=get_json, token=None):
    prefix = f"repos/{owner}/{repo}"
    observations = {"repository": f"{owner}/{repo}", "pr_number": number, "authorization": "UNKNOWN"}
    errors = []

    def request(name, path):
        try:
            observations[name] = fetch(path, token)
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError, OSError) as exc:
            errors.append({"endpoint": name, "error": str(exc)})
            observations[name] = None
        return observations[name]

    pr = request("pull_request", f"{prefix}/pulls/{number}")
    if not isinstance(pr, dict):
        observations["errors"] = errors
        return observations
    head = (pr.get("head") or {}).get("sha")
    base = (pr.get("base") or {}).get("sha")
    branch = (pr.get("base") or {}).get("ref")
    observations["head_sha"] = head
    observations["base_sha"] = base
    observations["draft"] = pr.get("draft")
    observations["mergeable"] = pr.get("mergeable")
    if not head or not base or not branch:
        errors.append({"endpoint": "pull_request", "error": "missing head/base SHA or base ref"})
        observations["errors"] = errors
        return observations
    ref = request("base_branch", f"{prefix}/branches/{branch}")
    observations["current_main_sha"] = ((ref or {}).get("commit") or {}).get("sha") if isinstance(ref, dict) else None
    request("commit_status", f"{prefix}/commits/{head}/status")
    request("check_runs", f"{prefix}/commits/{head}/check-runs?per_page=100")
    request("reviews", f"{prefix}/pulls/{number}/reviews?per_page=100")
    request("changed_files", f"{prefix}/pulls/{number}/files?per_page=100")
    request("branch_protection", f"{prefix}/branches/{branch}/protection")
    # Repository rulesets, CODEOWNERS, provenance, human evidence signoff,
    # check pagination and review dismissal semantics are NOT proven here.
    observations["limitations"] = [
        "Read-only inventory: never pass as a merge-authorizing snapshot",
        "First page only for checks, reviews and changed files",
        "Rulesets, CODEOWNERS, environment protection and review semantics unverified",
        "Source provenance, human signoff and semantic localization unverified",
    ]
    observations["errors"] = errors
    return observations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", type=int, required=True)
    args = parser.parse_args()
    if args.pr <= 0 or not all(s.replace("-", "").replace("_", "").isalnum() for s in (args.owner, args.repo)):
        parser.error("invalid repository or PR number")
    result = collect(args.owner, args.repo, args.pr, token=os.getenv("GITHUB_TOKEN"))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
