"""Structured field-validation registry for ChaseLights R4.2.

Field observations validate runtime behavior for already-admitted photographic
subjects. They do not replace the Place-specific evidence gate in
RESEARCH_EVIDENCE_SPEC_R4_2.md.

The registry intentionally stores structured, non-identifying observations.
User-supplied images are not committed by default.
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re

FIELD_VALIDATION_SCHEMA_VERSION = "field-validation-registry-r4.2-1"
FIELD_VALIDATION_REGISTRY_FILE = (
    Path(__file__).parent / "field_validation_registry_r4_2.json"
)

_ALLOWED_SOURCE_TYPES = {
    "user_field_observation",
    "maintainer_field_observation",
    "official_observation",
}

_ALLOWED_PUBLICATION = {
    "metadata_only_image_not_committed",
    "explicitly_authorized_publication",
}

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def load_field_validation_registry(path=FIELD_VALIDATION_REGISTRY_FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _score_errors(case_id, label, payload):
    errors = []
    for key in (
        "minimum_score",
        "maximum_score_for_low_confidence_proxy",
        "current_verified_score",
    ):
        if key not in payload:
            continue
        value = payload[key]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{case_id}: {label}.{key} must be numeric")
            continue
        if not 0 <= float(value) <= 100:
            errors.append(f"{case_id}: {label}.{key} outside 0..100")
    if (
        "minimum_score" in payload
        and "current_verified_score" in payload
        and float(payload["current_verified_score"]) < float(payload["minimum_score"])
    ):
        errors.append(f"{case_id}: {label} verified score below minimum")
    if (
        "maximum_score_for_low_confidence_proxy" in payload
        and "current_verified_score" in payload
        and payload.get("current_verified_confidence") == "low"
        and float(payload["current_verified_score"])
        > float(payload["maximum_score_for_low_confidence_proxy"])
    ):
        errors.append(f"{case_id}: {label} low-confidence score exceeds cap")
    return errors


def validate_field_validation_registry(
    registry=None,
    *,
    known_place_ids=None,
    known_opportunity_ids=None,
):
    if registry is None:
        registry = load_field_validation_registry()

    errors = []
    if registry.get("schema_version") != FIELD_VALIDATION_SCHEMA_VERSION:
        errors.append(
            "field validation schema mismatch: "
            f"{registry.get('schema_version')!r}"
        )

    policy = registry.get("policy") or {}
    for key in ("purpose", "admission_boundary", "privacy_boundary", "forecast_boundary"):
        if not str(policy.get(key) or "").strip():
            errors.append(f"field validation policy missing {key}")

    cases = registry.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["field validation registry must contain at least one case"]

    seen_ids = set()
    known_place_ids = set(known_place_ids or ())
    known_opportunity_ids = set(known_opportunity_ids or ())

    for case in cases:
        case_id = str(case.get("case_id") or "")
        if not case_id.startswith("FV-"):
            errors.append(f"{case_id or '<missing>'}: invalid case id")
        if case_id in seen_ids:
            errors.append(f"{case_id}: duplicate case id")
        seen_ids.add(case_id)

        place_id = str(case.get("place_id") or "")
        if not place_id:
            errors.append(f"{case_id}: missing place_id")
        elif known_place_ids and place_id not in known_place_ids:
            errors.append(f"{case_id}: unknown place_id {place_id}")

        ts = case.get("local_timestamp")
        try:
            dt = datetime.fromisoformat(str(ts))
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError("naive")
        except (TypeError, ValueError):
            errors.append(f"{case_id}: local_timestamp must be offset-aware ISO8601")

        direction = case.get("camera_direction") or {}
        if not str(direction.get("cardinal") or "").strip():
            errors.append(f"{case_id}: missing camera direction")

        source = case.get("source") or {}
        source_type = source.get("type")
        if source_type not in _ALLOWED_SOURCE_TYPES:
            errors.append(f"{case_id}: unsupported source type {source_type!r}")
        publication = source.get("publication")
        if publication not in _ALLOWED_PUBLICATION:
            errors.append(f"{case_id}: unsupported publication state {publication!r}")
        if (
            source_type == "user_field_observation"
            and publication == "explicitly_authorized_publication"
            and not source.get("publication_authorization")
        ):
            errors.append(f"{case_id}: public user image requires authorization metadata")

        observed = case.get("observed_scene") or {}
        required_observed = (
            "camera_whiteout",
            "coast_and_sea_readable",
            "northward_mountain_layers_readable",
            "terrain_attached_cloud_band_visible",
            "ridge_partially_visible",
        )
        for key in required_observed:
            if not isinstance(observed.get(key), bool):
                errors.append(f"{case_id}: observed_scene.{key} must be boolean")

        snapshot = case.get("captured_forecast_snapshot") or {}
        camera = snapshot.get("camera") or {}
        sector = snapshot.get("northward_elevated_sector") or {}
        for key in ("visibility_km", "low_cloud_pct", "lcl_agl_proxy_m"):
            if not isinstance(camera.get(key), (int, float)) or isinstance(camera.get(key), bool):
                errors.append(f"{case_id}: captured camera.{key} must be numeric")
        for key in (
            "elevated_target_count",
            "min_visibility_km",
            "min_visibility_to_camera_ratio",
            "terrain_lcl_intersection_target_count",
            "terrain_lcl_intersection_bearing_count",
        ):
            if not isinstance(sector.get(key), (int, float)) or isinstance(sector.get(key), bool):
                errors.append(f"{case_id}: captured sector.{key} must be numeric")

        expected = case.get("expected_model_behavior") or {}
        overall = expected.get("overall") or {}
        preferred = overall.get("preferred_opportunity_id")
        if not preferred:
            errors.append(f"{case_id}: missing preferred_opportunity_id")
        elif known_opportunity_ids and preferred not in known_opportunity_ids:
            errors.append(f"{case_id}: unknown preferred opportunity {preferred}")
        errors.extend(_score_errors(case_id, "overall", overall))

        opportunity_expectations = expected.get("opportunities") or {}
        if not isinstance(opportunity_expectations, dict) or not opportunity_expectations:
            errors.append(f"{case_id}: missing opportunity expectations")
            opportunity_expectations = {}
        for oid, exp in opportunity_expectations.items():
            if known_opportunity_ids and oid not in known_opportunity_ids:
                errors.append(f"{case_id}: unknown expected opportunity {oid}")
            states = exp.get("acceptable_states") or []
            if not isinstance(states, list) or not states or not all(
                isinstance(x, str) and x for x in states
            ):
                errors.append(f"{case_id}: {oid} acceptable_states invalid")
            verified_state = exp.get("current_verified_state")
            if verified_state and verified_state not in states:
                errors.append(
                    f"{case_id}: {oid} verified state not in acceptable_states"
                )
            errors.extend(_score_errors(case_id, oid, exp))

        if preferred and opportunity_expectations and preferred not in opportunity_expectations:
            errors.append(
                f"{case_id}: preferred opportunity missing detailed expectation"
            )

        verification = case.get("verification") or {}
        for key in ("model_code_commit", "weather_data_commit"):
            sha = str(verification.get(key) or "")
            if not _SHA40.match(sha):
                errors.append(f"{case_id}: invalid {key}")
        data_sha = str(snapshot.get("data_commit") or "")
        if data_sha and data_sha != str(verification.get("weather_data_commit") or ""):
            errors.append(f"{case_id}: snapshot/verification weather commit mismatch")
        if verification.get("result") not in {"pass", "known_miss", "pending"}:
            errors.append(f"{case_id}: invalid verification result")

        limitations = case.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            errors.append(f"{case_id}: limitations must be non-empty")

    return errors


if __name__ == "__main__":
    issues = validate_field_validation_registry()
    if issues:
        raise SystemExit("\n".join(issues))
    print("field validation registry structure valid")
