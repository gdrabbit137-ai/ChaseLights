#!/usr/bin/env python3
"""After V2 owner merges, verify the actual main tree and run every V2 suite.

No source pin is relaxed, no network weather inputs, no deployment or live
scoring is performed here. This complements pre-merge 13-step rehearsal.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from run_integration import blob, run_group


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def verify_main(root, lock):
    """All shipped owner trees must exactly equal the tested owner heads."""
    out = {"repository_head": git(root, "rev-parse", "HEAD"), "owner_trees": {}}
    for owner, paths in (
        ("w1", ("specs/v2",)),
        ("w2", ("data/v2",)),
        ("w3", ("packages/core-v2",)),
        ("w4", ("apps/web-v2",)),
    ):
        pinned = lock["sources"][owner]["sha"]
        if subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", pinned, "HEAD"],
            capture_output=True, check=False,
        ).returncode:
            raise ValueError("Owner head not merged into main: " + owner + " " + pinned)
        for p in paths:
            current = git(root, "rev-parse", "HEAD:" + p)
            expected = git(root, "rev-parse", pinned + ":" + p)
            if current != expected:
                raise ValueError(f"Merged {owner} subtree differs from tested pin: {p}")
            out["owner_trees"][p] = current
    if out["owner_trees"]["apps/web-v2"] != lock["sources"]["w4"]["tree_sha"]:
        raise ValueError("W4 final app tree mismatches tested corrected tree")
    for p in ("AGENTS.md", "RESEARCH_EVIDENCE_SPEC_R4_2.md", "NAVIGATION_SPEC_R4_2.md"):
        if git(root, "rev-parse", "HEAD:" + p) != lock["reviewed_blobs"][p]:
            raise ValueError("Main governance specification drift: " + p)
    for p, expected in lock["w1_changed_blobs"].items():
        if git(root, "rev-parse", "HEAD:" + p) != expected:
            raise ValueError("Corrected W1 contract blob drift: " + p)

    manifest = json.loads(
        (root / "apps/web-v2/tests/fixtures/worker2/manifest.json").read_text()
    )
    if manifest["commit_sha"] != lock["sources"]["w2"]["canonical_content_sha"]:
        raise ValueError("W2 source commit declaration drift")
    expected_paths = {
        "data/v2/opportunities/tw-016-P01.json",
        "data/v2/opportunities/tw-026-P01.json",
        "data/v2/opportunities/tw-026-P02.json",
        "data/v2/previews/tw-026-P01.research-only.v21.json",
    }
    if len(manifest["files"]) != 4 or {x["source_path"] for x in manifest["files"]} != expected_paths:
        raise ValueError("Missing/duplicate source manifest records")
    data = {}
    for entry in manifest["files"]:
        p = entry["source_path"]
        source = (root / p).read_bytes()
        if git(root, "rev-parse", "HEAD:" + p) != entry["blob_sha"]:
            raise ValueError("Main W2 canonical source mismatch: " + p)
        if git(root, "rev-parse", lock["sources"]["w2"]["sha"] + ":" + p) != entry["blob_sha"]:
            raise ValueError("Original W2 pin mismatch: " + p)
        if blob(source) != entry["blob_sha"] or hashlib.sha256(source).hexdigest() != entry["sha256"]:
            raise ValueError("Canonical byte/source digest mismatch: " + p)
        if source != (root / "apps/web-v2/tests/fixtures/worker2" / entry["fixture"]).read_bytes():
            raise ValueError("W4 fixture not canonical: " + p)
        data[p] = json.loads(source)

    p01 = (root / "data/v2/opportunities/tw-026-P01.json").read_bytes()
    if p01 != (root / "packages/core-v2/tests/fixtures/tw-026-P01.w2-fe52720.json").read_bytes():
        raise ValueError("W3 real-record fixture differs from W2 source")
    for p in expected_paths:
        if "/opportunities/" not in p:
            continue
        item = data[p]
        if item.get("readiness", {}).get("research_level") != "R1":
            raise ValueError("W2 research level was silently promoted: " + p)
        if any(c.get("domain") == "ACCESS_SAFETY"
               for c in item["condition_contract"]["conditions"]):
            raise ValueError("Closure leaked into photographic conditions: " + p)
        for camera in item["camera_contexts"]:
            for attr in ("access_notes_i18n", "safety_notes_i18n"):
                if not all(camera.get(attr, {}).get(lang, "").strip()
                           for lang in ("zh-TW", "en", "ja")):
                    raise ValueError("Missing three-language access warning: " + p)
        if any(nav.get("status") == "verified" for nav in item["navigation_targets"]):
            raise ValueError("Unreviewed navigation was promoted: " + p)

    preview = data["data/v2/previews/tw-026-P01.research-only.v21.json"]
    catalog = json.loads((root / "apps/web-v2/catalog.v2.json").read_text())
    expected_source = lock["sources"]["w2"]["canonical_content_sha"]
    if catalog.get("source_commit_sha") != expected_source:
        raise ValueError("Default catalog declares the wrong canonical commit")
    if catalog.get("source_blob_sha") != blob(p01):
        raise ValueError("Default catalog declares a non-canonical P01 blob")
    if catalog.get("source_preview_blob_sha") != blob(
        (root / "data/v2/previews/tw-026-P01.research-only.v21.json").read_bytes()
    ):
        raise ValueError("Default catalog preview blob drift")
    extras = {"source_commit_sha", "source_path", "source_blob_sha",
              "source_preview_path", "source_preview_blob_sha"}
    if {k: v for k, v in catalog.items() if k not in extras} != preview:
        raise ValueError("Published research-only catalog differs from W2 preview")
    for name, d in (("preview", preview), ("catalog", catalog)):
        if not (d.get("research_only") is True and
                d.get("selected_date_recommendation_eligible") is False and
                d.get("forecast_available") is False and d.get("evaluations") == []):
            raise ValueError("Live score/recommendation promotion: " + name)
    if manifest.get("human_semantic_signoff") != "PENDING":
        raise ValueError("Human review completion was fabricated")
    # W2 Batch04 adds five reviewed-source *research-only* records, without
    # retroactively modifying the four byte-pinned original W2/W3/W4 inputs.
    # This is additional coverage; provenance of the earlier Preview remains
    # tied to canonical_content_sha, not the new W2 owner-branch commit.
    batch = lock["sources"]["w2"].get("batch04")
    if not batch or len(batch.get("opportunities", [])) != 5:
        raise ValueError("Five-place Batch04 owner pin missing")
    new_ids = batch["opportunities"]
    if len(set(new_ids)) != 5:
        raise ValueError("Duplicate Batch04 Opportunity ID")
    new_audit = json.loads((root / batch["source_audit"]).read_text())
    if set(new_audit["canonical_opportunity_ids"]) != set(new_ids):
        raise ValueError("Batch04 official-source audit doesn't match the pinned five")
    if new_audit["review"]["human_trilingual_semantics"] != "PENDING":
        raise ValueError("Batch04 human translation signoff was fabricated")
    if new_audit["review"]["human_geo"] != "PENDING":
        raise ValueError("Batch04 human lawful-camera-area signoff was fabricated")
    new_blobs = {}
    for new_id in new_ids:
        new_path = f"data/v2/opportunities/{new_id}.json"
        item = json.loads((root / new_path).read_text())
        if item["opportunity_id"] != new_id or item["place_id"] != new_id.split("-P")[0]:
            raise ValueError("Wrong Batch04 Place/Opportunity identity " + new_id)
        if item["readiness"]["research_level"] != "R1" or item["lifecycle_status"] != "evidence_review":
            raise ValueError("Batch04 research level improperly promoted: " + new_id)
        if item["provenance"]["review_status"] != "pending":
            raise ValueError("Batch04 human review was fabricated: " + new_id)
        if len(item["condition_contract"]["conditions"]) != 2:
            raise ValueError("Batch04 unexpected condition count: " + new_id)
        for condition in item["condition_contract"]["conditions"]:
            if (condition["domain"] == "ACCESS_SAFETY" or condition["evaluation_mode"] == "AUTO"
                    or condition.get("threshold") is not None or condition.get("model_binding") is not None):
                raise ValueError("Batch04 fabricated access score or validated forecast: " + new_id)
            if not all(condition.get("notes_i18n", {}).get(lang, "").strip()
                       for lang in ("zh-TW", "en", "ja")):
                raise ValueError("Batch04 missing condition translation: " + new_id)
        for camera in item["camera_contexts"]:
            if camera["geometry"]["status"] != "unknown":
                raise ValueError("Batch04 unverified Camera geometry promoted: " + new_id)
            for key in ("access_notes_i18n", "safety_notes_i18n"):
                if not all(camera.get(key, {}).get(lang, "").strip()
                           for lang in ("zh-TW", "en", "ja")):
                    raise ValueError("Batch04 missing camera advisory: " + new_id)
        for nav in item["navigation_targets"]:
            if nav["status"] == "verified" or nav.get("lat") is not None or nav.get("lon") is not None:
                raise ValueError("Batch04 unverified Directions promoted: " + new_id)
        new_blobs[new_path] = git(root, "rev-parse", "HEAD:" + new_path)
    out["batch04_canonical_git_blobs"] = new_blobs

    out["canonical_git_blobs"] = {x["source_path"]: x["blob_sha"] for x in manifest["files"]}
    out["research_only"] = True
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--logs-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    logs = args.logs_dir.resolve()
    logs.mkdir(parents=True, exist_ok=True)
    report = {"status": "FAIL", "root_head": None, "checks": [], "groups": []}
    try:
        lock = json.loads((root / "ops/v2/integration-sources.json").read_text())
        report["source_provenance"] = verify_main(root, lock)
        report["root_head"] = report["source_provenance"]["repository_head"]
        (logs / "provenance.json").write_text(
            json.dumps(report["source_provenance"], indent=2) + "\n")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   WORKER2_DATA_DIR=str(root / "data/v2/opportunities"))
        groups = [
            ("w1-schema", ["specs/v2/tests", "test_schema_smoke.py"], 17, True, False),
            ("w1-evaluation-schema", ["specs/v2/tests", "test_evaluation_result_security.py"], 4, True, False),
            ("w1-free-composition", ["specs/v2/tests", "test_free_composition_contract.py"], 6, True, False),
            ("w5-contract", ["ops/v2/tests", "test_integration_gate.py"], 7, True, False),
            ("w5-watchdog", ["ops/v2/tests", "test_worker_watchdog.py"], 3, True, False),
            ("w5-runner", ["ops/v2/tests", "test_ci_runner.py"], 7, True, False),
            ("w3-evaluator", ["packages/core-v2/tests", "test_*.py"], 32, True, False),
            ("w2-crosswalk-schema", ["data/v2/tests", "test_*.py"], 15, True, False),
            ("w2-real-records", [sys.executable, "specs/v2/tests/validate_contract.py",
                *[str(p.relative_to(root)) for p in sorted((root / "data/v2/opportunities").glob("*.json"))]],
                None, False, False),
            ("schema-valid-fixture", [sys.executable, "specs/v2/tests/validate_contract.py"], None, False, False),
            ("w3-compile", [sys.executable, "-m", "py_compile",
                "packages/core-v2/evaluator.py", "packages/core-v2/adapters/source_observation.py"],
                None, False, False),
            ("w4-node", ["node", "--test", "--test-isolation=none", "--test-timeout=120000",
                "--test-reporter=tap", *[str(p.relative_to(root)) for p in sorted(
                    (root / "apps/web-v2/tests").glob("*.test.mjs"))]], 31, False, True),
            ("local-isolation", [sys.executable, "ops/v2/integration_gate.py", "--root", str(root)],
                None, False, False),
            ("browser-smoke", ["node", "--test", "--test-isolation=none", "--test-timeout=120000",
                "--test-reporter=tap", "apps/web-v2/tests/browser-smoke.mjs"], 6, False, True),
        ]
        for name, command, expected, python, node in groups:
            report["groups"].append(
                run_group(name, command, root, logs, env, expected, python, node))
        report["counts"] = {
            key: sum(g["counts"].get(key, 0) for g in report["groups"])
            for key in ("tests", "pass", "fail", "error", "skip")
        }
        if report["counts"] != {
            "tests": 128, "pass": 128, "fail": 0, "error": 0, "skip": 0
        }:
            raise ValueError("Post-merge exact 128-case requirement failed")
        if not all(g["status"] == "PASS" for g in report["groups"]):
            raise ValueError("One or more required suites failed")
        report["status"] = "PASS"
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        (logs / "failure.log").write_text(report["error"] + "\n")
    (logs / "postmerge-summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "head": report["root_head"],
                      "counts": report.get("counts"), "error": report.get("error")}), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
