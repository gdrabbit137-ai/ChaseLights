"""Read-only V2 Worker audit. GitHub activity != execution, success or approval."""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PREFIXES = {
    "W1": ("v2/worker1-", "worker1/"),
    "W2": ("v2/worker2-", "worker2/"),
    "W3": ("w3/v2-", "worker3/"),
    "W4": ("worker4/v2-",),
    "W5": ("worker5/v2-",),
}

def identify(branch):
    return next((w for w, prefixes in PREFIXES.items()
                 if any(branch.startswith(prefix) for prefix in prefixes)), None)

def classify(date, now):
    if not date:
        return "UNKNOWN"
    age = (now - datetime.fromisoformat(date.replace("Z", "+00:00"))).total_seconds() / 3600
    return "REVIEW_NO_RECENT_COMMIT" if age >= 3 else "RECENT_COMMIT"

class Api:
    def __init__(self, repo, token):
        self.repo, self.token = repo, token

    def get(self, path):
        req = urllib.request.Request(
            "https://api.github.com/repos/" + self.repo + "/" + path,
            headers={"Accept": "application/vnd.github+json",
                     "Authorization": "Bearer " + self.token,
                     "User-Agent": "ChaseLights-V2-worker-watchdog"})
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)

    def pages(self, path):
        results = []
        for page in range(1, 11):
            separator = "&" if "?" in path else "?"
            items = self.get(path + separator + "per_page=100&page=" + str(page))
            if not isinstance(items, list):
                raise ValueError("Unexpected GitHub response for " + path)
            results.extend(items)
            if len(items) < 100:
                return results
        raise RuntimeError("GitHub pagination limit exceeded for " + path)

def snapshot(api, now):
    workers = {worker: [] for worker in PREFIXES}
    for item in api.pages("branches"):
        worker = identify(item["name"])
        if worker is None:
            continue
        sha = item["commit"]["sha"]
        commit = api.get("commits/" + urllib.parse.quote(sha))
        date = commit["commit"]["committer"]["date"]
        workers[worker].append({"branch": item["name"], "sha": sha, "commit_time": date})
    worker_info = {}
    for worker, branches in workers.items():
        recent = sorted(branches, key=lambda b: b["commit_time"], reverse=True)
        head = recent[0] if recent else None
        worker_info[worker] = {
            "latest": head, "branch_count": len(recent),
            "signal": classify(head["commit_time"] if head else None, now),
            "automation_run": "UNOBSERVABLE_FROM_GITHUB",
        }
    prs = []
    for pr in api.pages("pulls?state=open"):
        if not identify(pr["head"]["ref"]):
            continue
        sha = pr["head"]["sha"]
        checks = api.get("commits/" + urllib.parse.quote(sha) + "/check-runs")
        runs = checks.get("check_runs", [])
        action = ("CHECKS_MISSING" if not runs else
                  "INVESTIGATE_FAILED_CHECKS" if any(
                      c.get("conclusion") in ("failure", "cancelled", "timed_out")
                      for c in runs) else "CHECK_REVIEW_AND_MERGE_GATES")
        prs.append({"number": pr["number"], "url": pr["html_url"], "sha": sha,
                    "branch": pr["head"]["ref"], "draft": pr["draft"],
                    "checks": [{"name": c["name"], "status": c["status"],
                                "conclusion": c["conclusion"]} for c in runs],
                    "action": action})
    return {"schema": "v2-worker-audit-1", "timestamp": now.isoformat(),
            "workers": worker_info, "open_worker_prs": prs,
            "limitations": "Commit freshness is not proof of task success; W5 must inspect automation runs, actual tests, data quality and latest main specs."}

def render(report):
    lines = ["# ChaseLights V2 GitHub activity audit", "",
             "Generated: " + report["timestamp"], "",
             "| Worker | Latest branch | Signal |",
             "|---|---|---|"]
    for worker, info in report["workers"].items():
        branch = info["latest"]["branch"] if info["latest"] else "NONE"
        lines.append("| " + worker + " | " + branch + " | " + info["signal"] + " |")
    lines.extend(["", "## Open Worker PRs"])
    for pr in report["open_worker_prs"]:
        lines.append("- PR #" + str(pr["number"]) + ": " + pr["action"] +
                     " (" + pr["url"] + ")")
    lines.extend(["", "**Advisory only. W5 must diagnose and actually remediate each confirmed blocker.**"])
    return "\n".join(lines) + "\n"

def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("BLOCKED: GITHUB_TOKEN unavailable", file=sys.stderr)
        return 2
    try:
        data = snapshot(Api(os.getenv("GITHUB_REPOSITORY", "gdrabbit137-ai/ChaseLights"), token),
                        datetime.now(timezone.utc))
    except Exception as exc:
        print("BLOCKED: GitHub API audit failed: " + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        return 1
    out = Path("ops/v2/watchdog-output")
    out.mkdir(parents=True, exist_ok=True)
    (out / "snapshot.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    summary = render(data)
    (out / "summary.md").write_text(summary, encoding="utf-8")
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as file:
            file.write(summary)
    print(summary)
    return 0

if __name__ == "__main__":
    sys.exit(main())
