"""Region-aware CI weather impact detection for ChaseLights.

Fail-safe rule: ambiguous or generic weather/runtime changes regenerate all
regions. Region-specific catalog/registry changes regenerate only the affected
region(s).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import urllib.request
from pathlib import Path

REGIONS = ("tw", "jp", "us")
REGION_ID_RE = re.compile(r"\b(tw|jp|us)-\d{3}(?:-P\d{2})?\b")

ALWAYS_ALL_FILES = {
    "ci_weather_impact.py",
    "analyze_weather.py",
    "fetch_data.py",
    "opportunities.py",
    "runtime_dependencies.py",
    "spatial_weather.py",
    "marine_state.py",
    "tide_state.py",
    "aurora_state.py",
    "taxonomy_v004.py",
}
REGION_PATCH_FILES = {
    "opportunity_runtime.py",
    "access_state.py",
    "runtime_event_calendar_r4_2.json",
}
FIXED_REGION_FILES = {
    "shinhotaka_access.py": {"jp"},
    "yahiko_access.py": {"jp"},
    "johnston_ridge_access.py": {"us"},
    "denali_access.py": {"us"},
}
WORKFLOW_REGION_FILES = {
    ".github/workflows/b30_candidate_weather.yml": {"tw"},
    ".github/workflows/b32_jp_candidate_weather.yml": {"jp"},
    ".github/workflows/b61_us_candidate_weather.yml": {"us"},
    # Editing Browser Smoke's own detector/generation contract should exercise
    # the complete three-region path.
    ".github/workflows/b30_browser_smoke.yml": set(REGIONS),
}
CATALOG_FILE = "runtime_catalog_v004_r4_2.json"
# Manifest/evidence changes are integrity/evidence concerns; the actual catalog
# or runtime file determines weather-output impact.
NON_OUTPUT_DATA_FILES = {
    "runtime_catalog_manifest_r4_2.json",
    "runtime_evidence_registry_r4_2.json",
}
GENERIC_CODE_RE = re.compile(
    r"^\s*(?:def\s|class\s|return\b|raise\b|if\s|elif\s|else\s*:|"
    r"for\s|while\s|try\s*:|except\b|with\s|import\s|from\s)"
)


def _region_from_id(value: str) -> str | None:
    match = REGION_ID_RE.search(value)
    return match.group(1) if match else None


def catalog_changed_regions(base_payload: dict, head_payload: dict) -> set[str]:
    """Return regions whose canonical spot definitions changed."""
    for key in ("schema_version", "catalog_role"):
        if base_payload.get(key) != head_payload.get(key):
            return set(REGIONS)

    base_spots = {s["spot_id"]: s for s in base_payload.get("spots", [])}
    head_spots = {s["spot_id"]: s for s in head_payload.get("spots", [])}
    changed = set()
    for spot_id in set(base_spots) | set(head_spots):
        if base_spots.get(spot_id) != head_spots.get(spot_id):
            region = _region_from_id(spot_id)
            if region:
                changed.add(region)
            else:
                return set(REGIONS)
    return changed


def patch_region_delta(patch: str | None) -> set[str]:
    """Infer region changes from added/removed Opportunity/Place IDs.

    Symmetric ID deltas avoid false all-region classification for registry lines
    where pre-existing TW/JP IDs remain and only a US ID is added.
    """
    if not patch:
        return set()
    added_ids = set()
    removed_ids = set()
    for line in patch.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        target = None
        if line.startswith("+"):
            target = added_ids
        elif line.startswith("-"):
            target = removed_ids
        if target is not None:
            target.update(m.group(0) for m in REGION_ID_RE.finditer(line[1:]))

    delta = (added_ids - removed_ids) | (removed_ids - added_ids)
    chosen = delta or (added_ids | removed_ids)
    return {m.group(1) for value in chosen if (m := REGION_ID_RE.search(value))}


def patch_has_generic_code_change(patch: str | None) -> bool:
    if not patch:
        return True
    for line in patch.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        body = line[1:].strip()
        if not body or body.startswith("#"):
            continue
        if REGION_ID_RE.search(body):
            continue
        if GENERIC_CODE_RE.match(body):
            return True
    return False


def spot_name_region_map() -> dict[str, str]:
    from regions import get_spots

    mapping = {}
    for region in REGIONS:
        for spot in get_spots(region):
            names = set()
            for value in (spot.get("name_i18n") or {}).values():
                if isinstance(value, str) and value.strip():
                    names.add(value.strip())
            for key in ("name_local", "name", "canonical_name"):
                value = spot.get(key)
                if isinstance(value, str) and value.strip():
                    names.add(value.strip())
            for name in names:
                mapping[name] = region
    return mapping


def regions_patch_regions(patch: str | None, name_map: dict[str, str]) -> set[str]:
    if not patch:
        return set()
    changed_text = "\n".join(
        line[1:]
        for line in patch.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    )
    regions = {region for name, region in name_map.items() if name and name in changed_text}
    return regions


def api_json(url: str, token: str):
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def list_pr_files(repo: str, pr_number: str, token: str) -> list[dict]:
    items = []
    page = 1
    while True:
        batch = api_json(
            f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files?per_page=100&page={page}",
            token,
        )
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def fetch_repo_json(repo: str, path: str, ref: str, token: str) -> dict:
    payload = api_json(
        f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}",
        token,
    )
    encoded = payload.get("content")
    if not encoded:
        raise RuntimeError(f"{path}@{ref}: GitHub contents response omitted file content")
    return json.loads(base64.b64decode(encoded).decode("utf-8"))


def detect_regions(
    file_items: list[dict],
    base_catalog: dict | None,
    head_catalog: dict | None,
    name_map: dict[str, str],
) -> tuple[set[str], list[str]]:
    changed = {item["filename"] for item in file_items}
    reasons = []

    all_hits = sorted(changed & ALWAYS_ALL_FILES)
    if all_hits:
        return set(REGIONS), [f"generic/shared weather input: {x}" for x in all_hits]

    regions = set()

    if CATALOG_FILE in changed:
        if base_catalog is None or head_catalog is None:
            return set(REGIONS), ["canonical catalog changed but semantic comparison unavailable"]
        catalog_regions = catalog_changed_regions(base_catalog, head_catalog)
        if not catalog_regions:
            return set(REGIONS), ["canonical catalog changed without a resolvable spot delta"]
        regions |= catalog_regions
        reasons.append("canonical catalog: " + ",".join(sorted(catalog_regions)))

    patches = {item["filename"]: item.get("patch") for item in file_items}

    if "regions.py" in changed:
        patch = patches.get("regions.py")
        mapped = regions_patch_regions(patch, name_map)
        if not mapped:
            return set(REGIONS), ["regions.py changed but Place region could not be resolved"]
        regions |= mapped
        reasons.append("regions.py Place data: " + ",".join(sorted(mapped)))

    for path in sorted(changed & REGION_PATCH_FILES):
        patch = patches.get(path)
        if patch_has_generic_code_change(patch):
            return set(REGIONS), [f"{path}: generic executable logic changed"]
        mapped = patch_region_delta(patch)
        if not mapped:
            # JSON/context hunks can carry the owning Opportunity ID on an
            # unchanged context line; use the whole patch as a safe fallback.
            if patch:
                mapped = {m.group(1) for m in REGION_ID_RE.finditer(patch)}
        if not mapped:
            return set(REGIONS), [f"{path}: region could not be resolved"]
        regions |= mapped
        reasons.append(f"{path}: " + ",".join(sorted(mapped)))

    for path, fixed in FIXED_REGION_FILES.items():
        if path in changed:
            regions |= fixed
            reasons.append(f"{path}: " + ",".join(sorted(fixed)))

    for path, fixed in WORKFLOW_REGION_FILES.items():
        if path in changed:
            regions |= fixed
            reasons.append(f"{path}: workflow contract")

    known = (
        ALWAYS_ALL_FILES
        | REGION_PATCH_FILES
        | set(FIXED_REGION_FILES)
        | set(WORKFLOW_REGION_FILES)
        | NON_OUTPUT_DATA_FILES
        | {CATALOG_FILE, "regions.py"}
    )
    unresolved = sorted(
        path for path in changed
        if path in {
            "regions.py",
            "analyze_weather.py",
            "fetch_data.py",
            "opportunities.py",
            CATALOG_FILE,
            "runtime_catalog_manifest_r4_2.json",
            "opportunity_runtime.py",
            "runtime_event_calendar_r4_2.json",
            "runtime_dependencies.py",
            "access_state.py",
            "shinhotaka_access.py",
            "yahiko_access.py",
            "johnston_ridge_access.py",
            "denali_access.py",
            "spatial_weather.py",
            "marine_state.py",
            "tide_state.py",
            "aurora_state.py",
            "taxonomy_v004.py",
            "ci_weather_impact.py",
        } and path not in known
    )
    if unresolved:
        return set(REGIONS), ["unresolved weather input: " + ",".join(unresolved)]

    return regions, reasons


def write_outputs(regions: set[str], reasons: list[str]):
    output_path = os.environ.get("GITHUB_OUTPUT")
    payload = {
        "regions": sorted(regions),
        "tw": "tw" in regions,
        "jp": "jp" in regions,
        "us": "us" in regions,
        "reasons": reasons,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            for region in REGIONS:
                output.write(f"{region}={'true' if region in regions else 'false'}\n")
            output.write(f"regenerate={'true' if regions else 'false'}\n")
            output.write(f"regions={' '.join(r for r in REGIONS if r in regions)}\n")


def self_test():
    base = {
        "schema_version": "x", "catalog_role": "canonical_runtime_catalog",
        "spots": [
            {"spot_id": "tw-001", "x": 1},
            {"spot_id": "jp-001", "x": 1},
            {"spot_id": "us-001", "x": 1},
        ],
    }
    head = json.loads(json.dumps(base))
    head["spots"][2]["x"] = 2
    assert catalog_changed_regions(base, head) == {"us"}

    registry_patch = '''@@
-    "facility": ("tw-001-P01", "jp-001-P01"),
+    "facility": ("tw-001-P01", "jp-001-P01", "us-024-P02"),
'''
    assert patch_region_delta(registry_patch) == {"us"}
    assert patch_has_generic_code_change(registry_patch) is False

    same_id_patch = '''@@
-    "us-021-P01": {"center": 85.0},
+    "us-021-P01": {"center": 90.0},
'''
    assert patch_region_delta(same_id_patch) == {"us"}

    assert patch_has_generic_code_change("+def evaluator(item):\n+    return item\n") is True

    name_map = {"約書亞樹國家公園": "us", "七星潭月牙灣": "tw"}
    assert regions_patch_regions('+    "約書亞樹國家公園": {"lat": 1}\n', name_map) == {"us"}

    file_items = [
        {"filename": CATALOG_FILE, "patch": "..."},
        {"filename": "regions.py", "patch": '+    "約書亞樹國家公園": {"lat": 1}\n'},
        {"filename": "opportunity_runtime.py", "patch": '+    "us-021-P01": {"center": 90.0}\n'},
    ]
    regions, _ = detect_regions(file_items, base, head, name_map)
    assert regions == {"us"}

    regions, _ = detect_regions(
        [{"filename": "fetch_data.py", "patch": "+def changed():\n+    pass\n"}],
        base, head, name_map,
    )
    assert regions == set(REGIONS)

    regions, _ = detect_regions(
        [{"filename": "aurora_state.py", "patch": "+def changed():\n+    pass\n"}],
        base, head, name_map,
    )
    assert regions == set(REGIONS)
    print("ci_weather_impact self-test passed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return

    repo = os.environ["REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]
    base_sha = os.environ["BASE_SHA"]
    token = os.environ["GH_TOKEN"]

    try:
        file_items = list_pr_files(repo, pr_number, token)
        changed = {item["filename"] for item in file_items}
        base_catalog = head_catalog = None
        if CATALOG_FILE in changed:
            base_catalog = fetch_repo_json(repo, CATALOG_FILE, base_sha, token)
            head_catalog = json.loads(Path(CATALOG_FILE).read_text(encoding="utf-8"))
        names = spot_name_region_map() if "regions.py" in changed else {}
        regions, reasons = detect_regions(file_items, base_catalog, head_catalog, names)
    except Exception as exc:
        # CI optimization must fail safe: ambiguity costs time, never coverage.
        regions = set(REGIONS)
        reasons = [f"detector fallback to all regions: {type(exc).__name__}: {exc}"]

    write_outputs(regions, reasons)


if __name__ == "__main__":
    main()
