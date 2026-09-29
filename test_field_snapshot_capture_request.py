import json
from pathlib import Path
from tempfile import TemporaryDirectory

from field_snapshot import load_snapshot
from field_snapshot_capture_request import (
    REGISTRY_SCHEMA_VERSION,
    REQUEST_SCHEMA_VERSION,
    build_metadata,
    build_registry_entry,
    load_request,
    register_baseline,
    validate_request,
)


ROOT = Path(__file__).parent
SNAPSHOT = (
    ROOT
    / "test_fixtures"
    / "field_snapshot"
    / "FVS-TW-034-20260928-191509.json.gz.b64"
)


def _request(**overrides):
    payload = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "request_id": "FSCR-B115-SMOKE",
        "place_id": "tw-034",
        "valid_at": "2026-09-29T06:00:00+08:00",
        "capture_ref": "ac6726360cef60fe9e77219af5ece92cfd670c7b",
        "scene_family": "qingshui_cliff_mist",
        "revision_group": "tw-034@2026-09-28T22:00:00+00:00",
        "persist": True,
    }
    payload.update(overrides)
    return payload


def test_validate_request_contract():
    assert validate_request(_request()) == []

    bad = _request(
        request_id="bad request",
        valid_at="2026-09-29T06:00:00",
        capture_ref="main",
        persist="yes",
    )
    errors = validate_request(bad)
    assert any("request_id" in item for item in errors)
    assert any("offset-aware" in item for item in errors)
    assert any("40-character" in item for item in errors)
    assert any("persist" in item for item in errors)


def test_load_request_and_metadata():
    snapshot = load_snapshot(SNAPSHOT)
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "request.json"
        path.write_text(
            json.dumps(_request(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        request = load_request(path)

    metadata = build_metadata(snapshot, request)
    assert metadata["request_id"] == "FSCR-B115-SMOKE"
    assert metadata["snapshot_id"] == "FVS-TW-034-20260928-191509"
    assert metadata["capture_ref_requested"] == (
        "ac6726360cef60fe9e77219af5ece92cfd670c7b"
    )
    assert metadata["git_commit"] == (
        "ac6726360cef60fe9e77219af5ece92cfd670c7b"
    )
    assert metadata["forecast_local_time"] == "2026-09-29T06:00:00+08:00"
    assert metadata["observation_status"] == "unreviewed"


def test_build_and_register_baseline_entry():
    snapshot = load_snapshot(SNAPSHOT)
    request = _request(revision_group=None)
    entry = build_registry_entry(
        snapshot,
        request,
        archive_path="test_fixtures/field_snapshot/example.json.gz.b64",
        metadata_path="test_fixtures/field_snapshot/example.metadata.json",
        workflow_run_id="12345",
        artifact_name="field-snapshot-FSCR-B115-SMOKE",
        source_branch="snapshot-capture/b115-smoke",
    )

    assert entry["snapshot_id"] == snapshot["snapshot_id"]
    assert entry["revision_group"] == (
        "tw-034@2026-09-28T22:00:00+00:00"
    )
    assert entry["model_commit"] == snapshot["provenance"]["git_commit"]
    assert entry["observation_status"] == "unreviewed"
    assert entry["source"]["workflow_run_id"] == 12345
    assert entry["source"]["capture_request_id"] == "FSCR-B115-SMOKE"

    p02 = entry["recorded_summary"]["tw-034-P02"]
    assert p02["score"] == 54
    assert p02["runtime_reason"] == "visibility_too_low"

    p03 = entry["recorded_summary"]["tw-034-P03"]
    assert p03["score"] == 54
    assert p03["runtime_reason"] == "low_visibility_without_mist_support"
    assert p03["mist_target_count"] == 0
    assert p03["directional_mist_target_count"] == 0
    assert p03["broad_clear_target_sector"] is False

    with TemporaryDirectory() as tmp:
        registry_path = Path(tmp) / "registry.json"
        registry_path.write_text(
            json.dumps(
                {
                    "schema_version": REGISTRY_SCHEMA_VERSION,
                    "policy": {},
                    "baselines": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        register_baseline(registry_path, entry)
        saved = json.loads(registry_path.read_text(encoding="utf-8"))
        assert saved["baselines"] == [entry]

        try:
            register_baseline(registry_path, entry)
        except ValueError as exc:
            assert "already registered" in str(exc)
        else:
            raise AssertionError("duplicate snapshot registration must fail")


def test_request_never_promotes_ground_truth():
    snapshot = load_snapshot(SNAPSHOT)
    entry = build_registry_entry(
        snapshot,
        _request(),
        archive_path="a",
        metadata_path="b",
    )
    assert entry["observation_status"] == "unreviewed"
    assert any(
        "not an observed scene" in item
        for item in entry["limitations"]
    )


def main():
    test_validate_request_contract()
    test_load_request_and_metadata()
    test_build_and_register_baseline_entry()
    test_request_never_promotes_ground_truth()
    print("field snapshot capture request tests passed")


if __name__ == "__main__":
    main()
