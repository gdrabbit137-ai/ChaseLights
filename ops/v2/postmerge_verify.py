#!/usr/bin/env python3
"""After V2 owner merges, verify the actual main tree and run every V2 suite.

No source pin is relaxed, no network weather inputs, no deployment or live
scoring is performed here. This complements immutable base/head merge-tree rehearsal.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from run_integration import blob, run_group
from verify_open_meteo_one_shot import verify_one_shot_evidence


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
        ("w3", ("packages/core-v2", "packages/models-v2")),
        ("w4", ("apps/web-v2",)),
    ):
        pinned = lock["sources"][owner]["sha"]
        if subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", pinned, "HEAD"],
            capture_output=True, check=False,
        ).returncode:
            raise ValueError("Owner head not merged into main: " + owner + " " + pinned)
        for additional in lock["sources"][owner].get("additional_required_shas", []):
            if subprocess.run(
                ["git", "-C", str(root), "merge-base", "--is-ancestor", additional, "HEAD"],
                capture_output=True, check=False,
            ).returncode:
                raise ValueError("Required owner dependency not merged: " + owner + " " + additional)
        for p in paths:
            current = git(root, "rev-parse", "HEAD:" + p)
            expected = lock["sources"][owner].get("tree_sha") if len(paths) == 1 else None
            expected = expected or git(root, "rev-parse", pinned + ":" + p)
            if current != expected:
                raise ValueError(f"Merged {owner} subtree differs from tested pin: {p}")
            out["owner_trees"][p] = current
    if out["owner_trees"]["apps/web-v2"] != lock["sources"]["w4"]["tree_sha"]:
        raise ValueError("W4 final app tree mismatches tested corrected tree")
    if len(git(root, "ls-tree", "-r", "--name-only", "HEAD", "apps/web-v2").splitlines()) != lock["sources"]["w4"]["file_count"]:
        raise ValueError("W4 source file discovery differs from pinned owner")
    for p, expected in lock.get("effective_reviewed_blobs", {}).items():
        if git(root, "rev-parse", "HEAD:" + p) != expected:
            raise ValueError("Effective latest-main specification drift: " + p)
    for p in ("AGENTS.md", "RESEARCH_EVIDENCE_SPEC_R4_2.md", "NAVIGATION_SPEC_R4_2.md"):
        if git(root, "rev-parse", "HEAD:" + p) != lock["reviewed_blobs"][p]:
            raise ValueError("Main governance specification drift: " + p)
    for p, expected in lock["w1_changed_blobs"].items():
        if git(root, "rev-parse", "HEAD:" + p) != expected:
            raise ValueError("Corrected W1 contract blob drift: " + p)

    pilot = lock["hourly_pilot"]
    for label, entry in pilot["files"].items():
        path = entry["path"]
        raw = (root / path).read_bytes()
        if (git(root, "rev-parse", "HEAD:" + path) != entry["blob_sha"] or
                git(root, "rev-parse", entry["source_sha"] + ":" + path) != entry["blob_sha"] or
                hashlib.sha256(raw).hexdigest() != entry["sha256"] or
                blob(raw) != entry["blob_sha"]):
            raise ValueError("Hourly pilot immutable source mismatch: " + label)
    provenance = json.loads((root / pilot["w3_provenance_path"]).read_text())
    if (provenance["w1_w2_pr521_sha"] != lock["sources"]["w1"]["sha"] or
            provenance["schema_sha256"] != pilot["files"]["schema"]["sha256"] or
            provenance["binding_sha256"] != pilot["files"]["binding"]["sha256"] or
            provenance["provider_acceptance"] != "UNVERIFIED" or
            provenance["real_provider_bytes_received"] is not False or
            provenance["real_source_sha256"] is not None or
            pilot["data_state"] != "RAW_ONLY" or
            pilot["photography_verdict"] != "NOT_EVALUABLE"):
        raise ValueError("Hourly pilot provenance or non-scoring status drift")
    out["hourly_pilot"] = {"provider_acceptance": "UNVERIFIED",
                            "data_state": "RAW_ONLY", "photography_verdict": "NOT_EVALUABLE"}

    out["one_shot_acceptance"] = verify_one_shot_evidence(root, lock)

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
    # The public P01 Preview remains byte-pinned to the earlier verified Batch03 source,
    # not to the later five-record Batch04 W2 owner HEAD.
    expected_source = lock["sources"]["w2"]["canonical_content_sha"]
    if catalog.get("opportunities"):
        if catalog.get("source_pins", {}).get("tw-026-P01", {}).get("source_commit_sha") != expected_source:
            raise ValueError("Indexed P01 declares the wrong canonical commit")
        if catalog["source_pins"]["tw-026-P01"].get("source_blob_sha") != blob(p01):
            raise ValueError("Indexed P01 declares a non-canonical blob")
    else:
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
    if not catalog.get("opportunities") and {k: v for k, v in catalog.items() if k not in extras} != preview:
        raise ValueError("Published research-only catalog differs from W2 preview")
    for name, d in (("preview", preview), ("catalog", catalog)):
        if not (d.get("research_only") is True and
                d.get("selected_date_recommendation_eligible") is False and
                d.get("forecast_available") is False and d.get("evaluations") == []):
            raise ValueError("Live score/recommendation promotion: " + name)
    if manifest.get("human_semantic_signoff") != "PENDING":
        raise ValueError("Human review completion was fabricated")
    # Batch04 is an additive research admission only. The entire W2 subtree is
    # pinned to the reviewed Batch04 owner commit; new subjects are not public
    # just because their JSON exists. Independently verify the five-new-ID set.
    batch04 = lock["sources"]["w2"]["batch04"]
    audit = json.loads((root / batch04["audit_path"]).read_text(encoding="utf-8"))
    expected_ids = set(batch04["ids"])
    if (len(expected_ids) != 5 or len(audit["canonical_opportunity_ids"]) != 5
            or set(audit["canonical_opportunity_ids"]) != expected_ids):
        raise ValueError("Batch04 additions changed without coordinated audit")
    if (batch04["human_signoff"] != "PENDING" or
            audit["review"]["human_trilingual_semantics"] != "PENDING" or
            audit["review"]["human_geo"] != "PENDING" or
            batch04["live_eligible"] is not False):
        raise ValueError("Batch04 R1 human approval or forecastability was fabricated")
    for oid in batch04["ids"]:
        path = f"data/v2/opportunities/{oid}.json"
        candidate = json.loads((root / path).read_text(encoding="utf-8"))
        if (candidate["opportunity_id"] != oid or
                candidate["readiness"]["research_level"] != "R1" or
                candidate["lifecycle_status"] != "evidence_review" or
                candidate["provenance"]["review_status"] != "pending"):
            raise ValueError("Unreviewed Batch04 opportunity was promoted: " + oid)
        if any(c.get("domain") == "ACCESS_SAFETY" or
               c.get("evaluation_mode") == "AUTO" or c.get("threshold") is not None
               for c in candidate["condition_contract"]["conditions"]):
            raise ValueError("Batch04 false scoring or access contract: " + oid)
        if any(n.get("status") == "verified" or
               n.get("lat") is not None or n.get("lon") is not None
               for n in candidate["navigation_targets"]):
            raise ValueError("Batch04 unverified Directions were promoted: " + oid)
    # The new browse bundle must be the exact reviewed W2 index projection and
    # must carry byte-identical canonical records, including all five Batch04 IDs.
    index_dir = root / "data/v2/indexes/research"
    bundle = json.loads((root / "apps/web-v2/browse-index.v2.json").read_text())
    browse_source = lock["sources"]["w2"]["browse_index_source_sha"]
    if (subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                       browse_source, lock["sources"]["w2"]["sha"]],
                      capture_output=True).returncode or
            git(root, "rev-parse", "HEAD:data/v2/indexes/research") !=
            git(root, "rev-parse", browse_source + ":data/v2/indexes/research")):
        raise ValueError("W2 pilot changed the accepted browse index")
    if bundle.get("source_commit_sha") != browse_source:
        raise ValueError("Browse index does not identify the accepted W2 source")
    index_manifest = json.loads((index_dir / "manifest.json").read_text())
    if bundle.get("manifest") != index_manifest or index_manifest.get("mode") != "RESEARCH_ONLY":
        raise ValueError("W4 browse manifest differs from W2")
    for field in ("place_index", "topic_index", "field_provenance", "index_status"):
        name = field.replace("_", "-") + ".json"
        raw = (index_dir / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != index_manifest["files"][name]:
            raise ValueError("W2 browse index digest mismatch: " + name)
        if bundle.get(field) != json.loads(raw):
            raise ValueError("W4 browse index differs from W2: " + name)
    # No-review gate decision (2026-10-22): the admitted breadth catalog is
    # 216 Places / 428 Opportunities, all byte-pinned to their W2 sources.
    if (catalog.get("source_index_revision") != index_manifest["index_revision"] or
            catalog.get("source_index_commit_sha") != browse_source or
            len(catalog.get("places", [])) != 216
            or len(catalog.get("opportunities", [])) != 428):
        raise ValueError("W4 catalog is not the admitted 216-place W2 index")
    for row in catalog["opportunities"]:
        oid = row["opportunity_id"]
        path = f"data/v2/opportunities/{oid}.json"
        raw = (root / path).read_bytes()
        if (row != json.loads(raw) or
                catalog["source_pins"][oid]["source_blob_sha"] != blob(raw) or
                git(root, "rev-parse", "HEAD:" + path) != blob(raw)):
            raise ValueError("W4 canonical browse record drift: " + oid)
    out["batch04_ids"] = sorted(expected_ids)
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
    report = {"status": "FAIL", "root_head": git(root, "rev-parse", "HEAD"),
              "tested_parents": git(root, "show", "-s", "--format=%P", "HEAD").split(),
              "checks": [], "groups": []}
    try:
        lock = json.loads((root / "ops/v2/integration-sources.json").read_text())
        report["reviewed_main_sha"] = lock["reviewed_main"]
        report["actual_base_sha"] = os.environ.get("W5_BASE_SHA", lock["reviewed_main"])
        report["candidate_sha"] = os.environ.get("W5_HEAD_SHA", report["root_head"])
        for value in (report["actual_base_sha"], report["candidate_sha"]):
            if len(value) != 40 or git(root, "rev-parse", value + "^{commit}") != value:
                raise ValueError("Immutable base/head commit unavailable")
        if (report["candidate_sha"] != report["root_head"] and
                report["candidate_sha"] not in report["tested_parents"]):
            raise ValueError("Actual checkout does not link to candidate HEAD")
        report["source_shas"] = {owner: pin["sha"] for owner, pin in lock["sources"].items()}
        report["source_provenance"] = verify_main(root, lock)
        report["root_head"] = report["source_provenance"]["repository_head"]
        (logs / "provenance.json").write_text(
            json.dumps(report["source_provenance"], indent=2) + "\n")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   WORKER2_DATA_DIR=str(root / "data/v2/opportunities"),
                   CHASELIGHTS_W1_SPEC_ROOT=str(root / "specs/v2"),
                   W4_SCREENSHOT_DIR=str(logs / "w4-screenshots"),
                   W4_TOPICS_SCREENSHOT_DIR=str(logs / "topics-screenshots"),
                   W5_SCREENSHOT_DIR=str(logs / "built-screenshots"),
                   V2_BUILD_DIR=str(logs / "candidate-build"))
        groups = [
            ("w1-schema", ["specs/v2/tests", "test_schema_smoke.py"], 17, True, False),
            ("w1-solar-window-contract", ["specs/v2/tests", "test_solar_window_contract.py"], 4, True, False),
            ("w1-weather-source-contract", ["specs/v2/tests", "test_weather_source_contract.py"], 5, True, False),
            ("w1-evaluation-schema", ["specs/v2/tests", "test_evaluation_result_security.py"], 4, True, False),
            ("w1-free-composition", ["specs/v2/tests", "test_free_composition_contract.py"], 6, True, False),
            ("w1-shared-browse-contracts", ["specs/v2/tests", "test_task_w_contracts.py"], 31, True, False),
            ("w1-hourly-pilot-contract", ["specs/v2/tests", "test_hourly_weather_pilot_contract.py"], 12, True, False),
            ("w5-contract", ["ops/v2/tests", "test_integration_gate.py"], 7, True, False),
            ("w5-watchdog", ["ops/v2/tests", "test_worker_watchdog.py"], 3, True, False),
            ("w5-runner", ["ops/v2/tests", "test_ci_runner.py"], 7, True, False),
            ("w5-task-r-release-tools", ["ops/v2/tests", "test_task_r_release_tools.py"], 12, True, False),
            ("w5-task-v-integration", ["ops/v2/tests", "test_task_v_integration.py"], 11, True, False),
            ("w3-evaluator-and-hourly-source", ["packages/core-v2/tests", "test_*.py"], 121, True, False),
            ("w3-solar-model", ["packages/models-v2/tests", "test_*.py"], 10, True, False),
            ("w2-crosswalk-schema-index-and-hourly-binding", ["data/v2/tests", "test_*.py"], 47, True, False),
            ("w2-real-records", [sys.executable, "specs/v2/tests/validate_contract.py",
                *[str(p.relative_to(root)) for p in sorted((root / "data/v2/opportunities").glob("*.json"))]],
                None, False, False),
            ("schema-valid-fixture", [sys.executable, "specs/v2/tests/validate_contract.py"], None, False, False),
            ("w3-compile", [sys.executable, "-m", "py_compile",
                "packages/core-v2/evaluator.py", "packages/core-v2/adapters/source_observation.py",
                "packages/core-v2/adapters/nws_gridpoint.py",
                "packages/core-v2/adapters/open_meteo_hourly.py",
                "packages/core-v2/tools/open_meteo_hourly_pilot.py"],
                None, False, False),
            ("w4-node", ["node", "--test", "--test-isolation=none", "--test-timeout=120000",
                "--test-reporter=tap", *[str(p.relative_to(root)) for p in sorted(
                    (root / "apps/web-v2/tests").glob("*.test.mjs"))]], 58, False, True),
            ("w5-public-source-contract", ["node", "--test", "--test-reporter=tap",
                "ops/v2/tests/public-source-contract.test.mjs"], 6, False, True),
            ("local-isolation", [sys.executable, "ops/v2/integration_gate.py", "--root", str(root)],
                None, False, False),
            # Owner direction 2026-10-22: the playwright-era suites are replaced by
            # the CDP-driven local smoke (no playwright dependency). It prints the
            # TAP summary lines parse_node requires.
            ("browser-smoke", ["node", "apps/web-v2/tests/local-smoke.mjs"], 35, False, True),
            ("static-build", [sys.executable, "ops/v2/build_static.py", "--root", str(root),
                "--output", str(logs / "candidate-build")], None, False, False),
            ("candidate-build-browser", ["node", "--test", "--test-isolation=none",
                "--test-timeout=120000", "--test-reporter=tap",
                "ops/v2/tests/static-build-smoke.mjs"], 6, False, True),
        ]
        for name, command, expected, python, node in groups:
            report["groups"].append(
                run_group(name, command, root, logs, env, expected, python, node))
        report["counts"] = {
            key: sum(g["counts"].get(key, 0) for g in report["groups"])
            for key in ("tests", "pass", "fail", "error", "skip")
        }
        if report["counts"] != {
            "tests": 402, "pass": 402, "fail": 0, "error": 0, "skip": 0
        }:
            raise ValueError("Post-merge exact 402-case requirement failed")
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
