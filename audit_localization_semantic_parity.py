#!/usr/bin/env python3
"""Audit supported-locale semantic parity for researched Photography Opportunities.

The audit has two jobs:
1. prevent new or modified localization debt while the historical catalog is backfilled;
2. verify that localized canonical fields survive into generated regional weather output.

Human review is still required for semantic equivalence. This script can prove presence
and preservation, not translation quality.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Iterable, Tuple


ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "runtime_catalog_v004_r4_2.json"
GENERATED_PATHS = tuple(ROOT / f"{region}_weather.json" for region in ("tw", "jp", "us"))
SUPPORTED_LOCALES = ("zh-TW", "en", "ja")
BASELINE_COMMIT = "5f6bd312a0900b6b32e34919982a819ca6ef41d2"
REPORT_PATH = ROOT / "localization_semantic_parity_audit.json"

# These are the researched strings currently exposed by the production Place guide.
# If a future user-facing semantic field is added, it must be added here in the same
# change so the machine gate follows the presentation contract.
OP_FIELDS = (
    ("name_zh", "name_i18n"),
    ("best_time", "best_time_i18n"),
    ("best_season", "best_season_i18n"),
)
VARIANT_FIELDS = (
    ("variant_name", "variant_name_i18n"),
    ("required_conditions", "required_conditions_i18n"),
    ("boosters", "boosters_i18n"),
    ("penalties", "penalties_i18n"),
)
VIEWPOINT_FIELDS = (("name", "name_i18n"),)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _baseline_catalog() -> Dict[str, Any]:
    cmd = ["git", "show", f"{BASELINE_COMMIT}:{CATALOG_PATH.name}"]
    try:
        payload = subprocess.check_output(cmd, cwd=ROOT, text=True, encoding="utf-8")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"cannot read frozen localization baseline {BASELINE_COMMIT}; "
            "CI must fetch that commit before running this audit"
        ) from exc
    return json.loads(payload)


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _records(catalog: Dict[str, Any]) -> Iterable[Tuple[str, str, str, Dict[str, Any]]]:
    """Yield (stable_key, field_label, source_value, locale_map)."""
    for spot_index, spot in enumerate(catalog.get("spots") or []):
        spot_id = spot.get("spot_id") or f"spot-index-{spot_index}"
        for op_index, op in enumerate(spot.get("opportunities") or []):
            op_id = op.get("opportunity_id") or f"op-index-{op_index}"
            for source_key, i18n_key in OP_FIELDS:
                source = _clean(op.get(source_key))
                if source:
                    yield (
                        f"op:{spot_id}:{op_id}:{source_key}",
                        f"op.{i18n_key}",
                        source,
                        op.get(i18n_key) if isinstance(op.get(i18n_key), dict) else {},
                    )

            for variant_index, variant in enumerate(op.get("condition_variants") or []):
                variant_id = variant.get("variant_id") or f"variant-index-{variant_index}"
                for source_key, i18n_key in VARIANT_FIELDS:
                    source = _clean(variant.get(source_key))
                    if source:
                        yield (
                            f"variant:{spot_id}:{op_id}:{variant_id}:{source_key}",
                            f"variant.{i18n_key}",
                            source,
                            variant.get(i18n_key) if isinstance(variant.get(i18n_key), dict) else {},
                        )

            for viewpoint_index, viewpoint in enumerate(op.get("viewpoints") or []):
                viewpoint_id = viewpoint.get("viewpoint_id") or f"viewpoint-index-{viewpoint_index}"
                for source_key, i18n_key in VIEWPOINT_FIELDS:
                    source = _clean(viewpoint.get(source_key))
                    if source:
                        yield (
                            f"viewpoint:{spot_id}:{op_id}:{viewpoint_id}:{source_key}",
                            f"viewpoint.{i18n_key}",
                            source,
                            viewpoint.get(i18n_key) if isinstance(viewpoint.get(i18n_key), dict) else {},
                        )


def _gap_map(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    gaps: Dict[str, Dict[str, Any]] = {}
    for key, field, source, locale_map in _records(catalog):
        missing = tuple(locale for locale in SUPPORTED_LOCALES if not _clean(locale_map.get(locale)))
        if missing:
            gaps[key] = {
                "field": field,
                "source": source,
                "missing": missing,
            }
    return gaps


def _catalog_record_map(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        key: {
            "field": field,
            "source": source,
            "locales": {locale: _clean(locale_map.get(locale)) for locale in SUPPORTED_LOCALES},
        }
        for key, field, source, locale_map in _records(catalog)
    }


def _generated_catalog() -> Dict[str, Any]:
    spots = []
    for path in GENERATED_PATHS:
        payload = _read_json(path)
        spots.extend(payload.get("spots") or [])
    return {"spots": spots}


def audit(strict: bool = False) -> Dict[str, Any]:
    current_catalog = _read_json(CATALOG_PATH)
    baseline_catalog = _baseline_catalog()

    current_gaps = _gap_map(current_catalog)
    baseline_gaps = _gap_map(baseline_catalog)

    regressions = []
    for key, current in sorted(current_gaps.items()):
        baseline = baseline_gaps.get(key)
        if baseline is None:
            regressions.append(
                {
                    "key": key,
                    "reason": "new localization debt",
                    "field": current["field"],
                    "missing": list(current["missing"]),
                }
            )
            continue
        if current["source"] != baseline["source"]:
            regressions.append(
                {
                    "key": key,
                    "reason": "canonical user-facing text changed while localization remains incomplete",
                    "field": current["field"],
                    "missing": list(current["missing"]),
                }
            )
            continue
        newly_missing = sorted(set(current["missing"]) - set(baseline["missing"]))
        if newly_missing:
            regressions.append(
                {
                    "key": key,
                    "reason": "supported locale regressed from present to missing",
                    "field": current["field"],
                    "missing": newly_missing,
                }
            )

    baseline_count = Counter()
    current_count = Counter()
    for item in baseline_gaps.values():
        for locale in item["missing"]:
            baseline_count[f'{item["field"]}:{locale}'] += 1
    for item in current_gaps.values():
        for locale in item["missing"]:
            current_count[f'{item["field"]}:{locale}'] += 1

    canonical_records = _catalog_record_map(current_catalog)
    generated_records = _catalog_record_map(_generated_catalog())
    propagation_errors = []
    localized_fields_checked = 0
    for key, canonical in sorted(canonical_records.items()):
        present = {locale: value for locale, value in canonical["locales"].items() if value}
        if not present:
            continue
        localized_fields_checked += 1
        generated = generated_records.get(key)
        if generated is None:
            propagation_errors.append(
                {
                    "key": key,
                    "reason": "localized canonical semantic field missing from generated output",
                    "field": canonical["field"],
                }
            )
            continue
        for locale, expected in present.items():
            actual = generated["locales"].get(locale, "")
            if actual != expected:
                propagation_errors.append(
                    {
                        "key": key,
                        "reason": "generated locale map does not preserve canonical value",
                        "field": canonical["field"],
                        "locale": locale,
                    }
                )

    report = {
        "supported_locales": list(SUPPORTED_LOCALES),
        "baseline_commit": BASELINE_COMMIT,
        "baseline_missing_by_field_locale": dict(sorted(baseline_count.items())),
        "current_missing_by_field_locale": dict(sorted(current_count.items())),
        "historical_debt_fields_remaining": len(current_gaps),
        "new_or_modified_debt": regressions,
        "localized_fields_checked_in_generated_output": localized_fields_checked,
        "generated_output_propagation_errors": propagation_errors,
        "strict": strict,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failures = list(regressions) + list(propagation_errors)
    if strict and current_gaps:
        failures.append(
            {
                "reason": "strict mode requires zero historical localization debt",
                "remaining": len(current_gaps),
            }
        )

    if failures:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return report | {"ok": False}

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report | {"ok": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail while any supported-locale semantic field remains incomplete",
    )
    args = parser.parse_args()
    try:
        result = audit(strict=args.strict)
    except Exception as exc:
        print(f"localization semantic parity audit failed to run: {exc}", file=sys.stderr)
        return 2
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
