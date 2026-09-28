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
FIELD_VALIDATION_REPLAY_SCHEMA_VERSION = "field-validation-replay-r4.2-1"
_PROJECT_ROOT = Path(__file__).parent
FIELD_VALIDATION_REGISTRY_FILE = (
    _PROJECT_ROOT / "field_validation_registry_r4_2.json"
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

_ALLOWED_REPLAY_FIXTURE_TYPES = {
    "synthetic_minimum_reproduction",
    "captured_raw_model_inputs",
}

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def load_field_validation_registry(path=FIELD_VALIDATION_REGISTRY_FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _resolve_project_relative_path(path):
    candidate = (_PROJECT_ROOT / str(path)).resolve()
    root = _PROJECT_ROOT.resolve()
    if root != candidate and root not in candidate.parents:
        raise ValueError(f"path escapes project root: {path}")
    return candidate


def load_field_validation_replay_fixture(path):
    resolved = _resolve_project_relative_path(path)
    return json.loads(resolved.read_text(encoding="utf-8"))


def validate_field_validation_replay_fixture(fixture, *, expected_case_id=None):
    errors = []
    case_id = str(fixture.get("case_id") or expected_case_id or "<missing>")

    if fixture.get("schema_version") != FIELD_VALIDATION_REPLAY_SCHEMA_VERSION:
        errors.append(f"{case_id}: replay fixture schema mismatch")

    if expected_case_id and fixture.get("case_id") != expected_case_id:
        errors.append(f"{expected_case_id}: replay fixture case_id mismatch")

    fixture_type = fixture.get("fixture_type")
    if fixture_type not in _ALLOWED_REPLAY_FIXTURE_TYPES:
        errors.append(f"{case_id}: unsupported replay fixture type {fixture_type!r}")

    historical_raw_input = fixture.get("historical_raw_input")
    if not isinstance(historical_raw_input, bool):
        errors.append(f"{case_id}: replay historical_raw_input must be boolean")
    if fixture_type == "synthetic_minimum_reproduction" and historical_raw_input is not False:
        errors.append(f"{case_id}: synthetic replay must set historical_raw_input=false")
    if fixture_type == "captured_raw_model_inputs" and historical_raw_input is not True:
        errors.append(f"{case_id}: captured raw replay must set historical_raw_input=true")

    if not str(fixture.get("purpose") or "").strip():
        errors.append(f"{case_id}: replay purpose missing")

    epoch = fixture.get("epoch_utc")
    if not isinstance(epoch, (int, float)) or isinstance(epoch, bool):
        errors.append(f"{case_id}: replay epoch_utc must be numeric")

    item_data = fixture.get("item_data") or {}
    if not isinstance(item_data.get("cloud_base_agl"), (int, float)) or isinstance(
        item_data.get("cloud_base_agl"), bool
    ):
        errors.append(f"{case_id}: replay item_data.cloud_base_agl must be numeric")

    common = fixture.get("common_weather") or {}
    for key in (
        "temperature_2m",
        "dew_point_2m",
        "precipitation",
        "wind_speed_10m",
    ):
        if not isinstance(common.get(key), (int, float)) or isinstance(common.get(key), bool):
            errors.append(f"{case_id}: replay common_weather.{key} must be numeric")

    camera = fixture.get("camera") or {}
    for key in (
        "elevation_m",
        "visibility_m",
        "relative_humidity_2m",
        "cloud_cover_low",
        "weather_code",
    ):
        if not isinstance(camera.get(key), (int, float)) or isinstance(camera.get(key), bool):
            errors.append(f"{case_id}: replay camera.{key} must be numeric")

    targets = fixture.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append(f"{case_id}: replay targets must be non-empty")
        targets = []
    seen_points = set()
    for index, target in enumerate(targets):
        label = f"{case_id}: replay targets[{index}]"
        if not isinstance(target, dict):
            errors.append(f"{label} must be an object")
            continue
        for key in (
            "bearing_deg",
            "distance_km",
            "elevation_m",
            "visibility_m",
            "relative_humidity_2m",
            "cloud_cover_low",
            "weather_code",
        ):
            if not isinstance(target.get(key), (int, float)) or isinstance(target.get(key), bool):
                errors.append(f"{label}.{key} must be numeric")
        point_key = (target.get("bearing_deg"), target.get("distance_km"))
        if point_key in seen_points:
            errors.append(f"{label} duplicates bearing/distance {point_key}")
        seen_points.add(point_key)

    theme_metrics = fixture.get("theme_metrics")
    expected = fixture.get("expected")
    if not isinstance(theme_metrics, dict) or not theme_metrics:
        errors.append(f"{case_id}: replay theme_metrics missing")
        theme_metrics = {}
    if not isinstance(expected, dict) or not expected:
        errors.append(f"{case_id}: replay expected outcomes missing")
        expected = {}

    if set(theme_metrics) != set(expected):
        errors.append(f"{case_id}: replay theme_metrics / expected opportunity ids differ")

    for oid, outcome in expected.items():
        label = f"{case_id}: replay {oid}"
        if not isinstance(outcome, dict):
            errors.append(f"{label} expected outcome must be an object")
            continue
        if not str(outcome.get("condition_state") or "").strip():
            errors.append(f"{label} condition_state missing")
        if not isinstance(outcome.get("score"), (int, float)) or isinstance(outcome.get("score"), bool):
            errors.append(f"{label} score must be numeric")
        elif not 0 <= float(outcome["score"]) <= 100:
            errors.append(f"{label} score outside 0..100")
        if outcome.get("score_confidence") not in {"low", "medium", "high"}:
            errors.append(f"{label} score_confidence invalid")

    return errors


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

        replay = case.get("replay_fixture")
        if replay is not None:
            if not isinstance(replay, dict):
                errors.append(f"{case_id}: replay_fixture must be an object")
            else:
                if replay.get("status") != "available":
                    errors.append(f"{case_id}: replay_fixture.status must be available")
                if replay.get("schema_version") != FIELD_VALIDATION_REPLAY_SCHEMA_VERSION:
                    errors.append(f"{case_id}: replay_fixture schema mismatch")
                fixture_type = replay.get("fixture_type")
                if fixture_type not in _ALLOWED_REPLAY_FIXTURE_TYPES:
                    errors.append(f"{case_id}: replay_fixture type unsupported")
                historical_raw_input = replay.get("historical_raw_input")
                if not isinstance(historical_raw_input, bool):
                    errors.append(f"{case_id}: replay_fixture historical_raw_input must be boolean")
                if fixture_type == "synthetic_minimum_reproduction" and historical_raw_input is not False:
                    errors.append(f"{case_id}: synthetic replay registry link must set historical_raw_input=false")

                path = replay.get("path")
                if not str(path or "").strip():
                    errors.append(f"{case_id}: replay_fixture path missing")
                else:
                    try:
                        fixture = load_field_validation_replay_fixture(path)
                    except (OSError, ValueError, json.JSONDecodeError) as exc:
                        errors.append(f"{case_id}: replay fixture unreadable: {exc}")
                    else:
                        errors.extend(
                            validate_field_validation_replay_fixture(
                                fixture,
                                expected_case_id=case_id,
                            )
                        )
                        fixture_expected = fixture.get("expected") or {}
                        for oid, outcome in fixture_expected.items():
                            registry_expectation = opportunity_expectations.get(oid) or {}
                            if outcome.get("condition_state") != registry_expectation.get("current_verified_state"):
                                errors.append(f"{case_id}: replay {oid} state differs from registry verified state")
                            if outcome.get("score") != registry_expectation.get("current_verified_score"):
                                errors.append(f"{case_id}: replay {oid} score differs from registry verified score")
                            if outcome.get("score_confidence") != registry_expectation.get("current_verified_confidence"):
                                errors.append(f"{case_id}: replay {oid} confidence differs from registry verified confidence")

        limitations = case.get("limitations")
        if not isinstance(limitations, list) or not limitations:
            errors.append(f"{case_id}: limitations must be non-empty")

    return errors


if __name__ == "__main__":
    issues = validate_field_validation_registry()
    if issues:
        raise SystemExit("\n".join(issues))
    print("field validation registry structure valid")
