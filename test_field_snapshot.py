from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from field_snapshot import (
    SNAPSHOT_SCHEMA_VERSION,
    build_snapshot_from_event,
    diff_replay,
    evaluate_normalized_input,
    load_snapshot,
    replay_current,
    validate_snapshot,
    write_snapshot,
)


EPOCH = 1790556000  # deterministic 2026-09-28 morning UTC fixture

LIVE_QINGSHUI_BASELINE = (
    Path(__file__).parent
    / "test_fixtures"
    / "field_snapshot"
    / "FVS-TW-034-20260928-163925.json.gz.b64"
)

MORNING_QINGSHUI_BASELINE = (
    Path(__file__).parent
    / "test_fixtures"
    / "field_snapshot"
    / "FVS-TW-034-20260928-173805.json.gz.b64"
)


def _base_item(spatial_weather):
    return {
        "spot_id": "tw-034",
        "timestamp": EPOCH,
        "scenes": ["coast", "mountain"],
        "c_low": 27,
        "c_low_available": True,
        "c_mid": 12,
        "c_mid_available": True,
        "c_high": 8,
        "c_high_available": True,
        "pop": 0,
        "pop_available": True,
        "precipitation": 0.0,
        "snowfall": None,
        "snow_depth": None,
        "direct_normal_irradiance": 120.0,
        "weather_code": 1,
        "weather_code_available": True,
        "vis": 800,
        "vis_available": True,
        "rh": 77,
        "rh_available": True,
        "wind": 1.5,
        "wind_available": True,
        "temp": 25.3,
        "temp_available": True,
        "dew": 21.0,
        "dew_available": True,
        "kp": None,
        "hour": 6,
        "local_date": "2026-09-28",
        "local_time": "06:00",
        "local_month": 9,
        "is_day": True,
        "is_twilight": False,
        "access_open": True,
        "cloud_base_agl": 537,
        "cloud_base_asl": 550,
        "cloud_base_delta": -500,
        "cloud_below_camera": False,
        "cloud_base_near_camera": False,
        "sun_alignment": "unknown",
        "bortle_class": None,
        "dark_sky_score": None,
        "spatial_weather": spatial_weather,
        "marine_forecast": None,
        "tide_forecast": None,
        "aurora_forecast": None,
        "astronomy_valid": True,
        "sun_azimuth": 88.0,
        "sun_elevation": 8.0,
        "moon_azimuth": 250.0,
        "moon_elevation": -15.0,
        "moon_illumination": 10.0,
        "moon_phase": "waning",
        "astronomical_dark": False,
        "galactic_core_azimuth": None,
        "galactic_core_elevation": None,
        "galactic_core_visible": False,
    }


def _clear_sector():
    camera = {
        "point_id": "S00",
        "lat": 24.2,
        "lon": 121.68,
        "role": "camera",
        "elevation_m": 30,
        "visibility": 800,
        "relative_humidity_2m": 77,
        "cloud_cover_low": 27,
        "precipitation": 0.0,
        "weather_code": 1,
    }
    targets = []
    index = 1
    for distance in (2.5, 5.0):
        for bearing in (330.0, 0.0, 30.0):
            targets.append({
                "point_id": f"S{index:02d}",
                "lat": 24.2,
                "lon": 121.68,
                "role": "directional_mist_proxy",
                "elevation_m": 100,
                "bearing_deg": bearing,
                "distance_km": distance,
                "visibility": 12000,
                "relative_humidity_2m": 70,
                "cloud_cover_low": 20,
                "precipitation": 0.0,
                "weather_code": 1,
            })
            index += 1
    return {
        "tw-034-P03": {
            "camera": camera,
            "targets": targets,
            "camera_reference_elevation_m": 30,
            "target_resolution": (
                "directional_sector_environment_proxy_not_exact_cliff_or_mist_location"
            ),
        }
    }


def _event(item_data, output):
    return {
        "forecast_valid_epoch": EPOCH,
        "forecast_valid_at": datetime.fromtimestamp(
            EPOCH, timezone.utc
        ).isoformat(),
        "timezone": "Asia/Taipei",
        "language": "zh-TW",
        "raw_camera_weather": {
            "latitude": 24.2,
            "longitude": 121.68,
            "hourly": {"time": [EPOCH], "visibility": [800]},
        },
        "spatial_request_plan": {
            "version": "synthetic-b101",
            "points": [],
            "profiles": {},
        },
        "raw_spatial_weather": [],
        "normalized_input": item_data,
        "runtime_output": output["runtime_output"],
        "theme_scores": output["theme_scores"],
        "opportunity_scores": output["opportunity_scores"],
    }


def test_qingshui_broad_clear_negative_replay():
    item = _base_item(_clear_sector())
    output = evaluate_normalized_input(
        "tw-034", item, lang="zh-TW", timezone_name="Asia/Taipei"
    )
    runtime = output["runtime_output"]["tw-034-P03"]
    assert runtime["eligible"] is False
    assert runtime["reason"] == "directional_target_sector_lacks_mist_support"
    assert runtime["directional_mist_negative_evidence"] is True
    assert runtime["spatial_mist_context"]["target_sample_count"] == 6
    assert runtime["spatial_mist_context"]["clear_target_count"] == 6
    assert runtime["spatial_mist_context"]["clear_bearing_count"] == 3
    assert runtime["spatial_mist_context"]["broad_clear_target_sector"] is True

    snapshot = build_snapshot_from_event(
        "tw-034",
        _event(item, output),
        captured_at=datetime(2026, 9, 28, 6, 15, tzinfo=timezone.utc),
    )
    assert snapshot["schema_version"] == SNAPSHOT_SCHEMA_VERSION
    assert snapshot["observation"]["status"] == "unreviewed"
    assert validate_snapshot(snapshot) == []
    replayed = replay_current(snapshot)
    diff = diff_replay(snapshot, replayed)
    assert diff["match"] is True
    assert diff["different_opportunity_ids"] == []


def test_qingshui_missing_spatial_preserves_low_confidence_fallback():
    item = _base_item({})
    output = evaluate_normalized_input(
        "tw-034", item, lang="zh-TW", timezone_name="Asia/Taipei"
    )
    runtime = output["runtime_output"]["tw-034-P03"]
    assert runtime["eligible"] is True
    assert runtime["reason"] == "coastal_cliff_visibility_only_candidate"
    assert runtime["minimum_sufficient_score_hint"] == 68
    assert runtime["runtime_confidence_hint"] == "low"
    assert runtime["directional_mist_negative_evidence"] is False

    snapshot = build_snapshot_from_event(
        "tw-034",
        _event(item, output),
        captured_at=datetime(2026, 9, 28, 6, 16, tzinfo=timezone.utc),
    )
    assert diff_replay(snapshot, replay_current(snapshot))["match"] is True


def test_snapshot_is_write_once_and_hash_protected():
    item = _base_item({})
    output = evaluate_normalized_input(
        "tw-034", item, lang="zh-TW", timezone_name="Asia/Taipei"
    )
    snapshot = build_snapshot_from_event(
        "tw-034",
        _event(item, output),
        captured_at=datetime(2026, 9, 28, 6, 17, tzinfo=timezone.utc),
    )
    with TemporaryDirectory() as tmp:
        path = write_snapshot(snapshot, tmp)
        loaded = load_snapshot(path)
        assert loaded["snapshot_id"] == snapshot["snapshot_id"]

        try:
            write_snapshot(snapshot, tmp)
        except FileExistsError:
            pass
        else:
            raise AssertionError("snapshot writer must be write-once")

        tampered = deepcopy(loaded)
        first = sorted(tampered["recorded_output"]["opportunity_scores"])[0]
        tampered["recorded_output"]["opportunity_scores"][first]["score"] = 99
        assert "snapshot integrity hash mismatch" in validate_snapshot(tampered)


def test_archived_live_qingshui_baseline_fixture():
    snapshot = load_snapshot(LIVE_QINGSHUI_BASELINE)
    assert snapshot["snapshot_id"] == "FVS-TW-034-20260928-163925"
    assert snapshot["place_id"] == "tw-034"
    assert snapshot["provenance"]["git_commit"] == (
        "fadfc65aeb8e9219cec2b60fc0ed91bf9fc98e21"
    )
    assert snapshot["integrity"]["payload_sha256"] == (
        "0736bab3200a9d229a696d2ac896b737dba5e2484459c88a864c42496e341e6f"
    )
    assert snapshot["observation"]["status"] == "unreviewed"

    item = snapshot["normalized_input"]
    assert item["local_date"] == "2026-09-29"
    assert item["local_time"] == "01:00"
    assert item["vis"] == 500.0
    assert item["rh"] == 82
    assert item["c_low"] == 41

    p03 = snapshot["recorded_output"]["opportunity_scores"]["tw-034-P03"]
    assert p03["score"] == 38
    assert p03["score_confidence"] == "medium"
    assert (
        p03["condition_state"]
        == "minimum_sufficient_weather_match_outside_time_window"
    )
    assert p03["runtime"]["reason"] == "camera_visibility_too_low_for_cliff_readability"
    assert p03["runtime"]["minimum_sufficient_score_hint"] == 68
    assert p03["runtime"]["directional_mist_negative_evidence"] is False

    spatial = p03["runtime"]["spatial_mist_context"]
    assert spatial["available"] is True
    assert spatial["eligible"] is True
    assert spatial["reason"] == "directional_mist_signal_detected"
    assert spatial["target_sample_count"] == 6
    assert spatial["mist_target_count"] == 5
    assert spatial["directional_mist_target_count"] == 2
    assert spatial["clear_target_count"] == 0
    assert spatial["clear_bearing_count"] == 0
    assert spatial["broad_clear_target_sector"] is False

    # The permanent baseline must remain executable by current code, but model
    # evolution is allowed to change its outcome. The fixture itself is the
    # immutable reference; matrix replay reports differences without forcing
    # future scoring versions to reproduce B101 forever.
    replayed = replay_current(snapshot)
    assert set(replayed["opportunity_scores"]) == set(
        snapshot["recorded_output"]["opportunity_scores"]
    )
    diff = diff_replay(snapshot, replayed)
    assert diff["snapshot_id"] == snapshot["snapshot_id"]


def test_archived_qingshui_morning_baseline_fixture():
    snapshot = load_snapshot(MORNING_QINGSHUI_BASELINE)
    assert snapshot["snapshot_id"] == "FVS-TW-034-20260928-173805"
    assert snapshot["place_id"] == "tw-034"
    assert snapshot["provenance"]["git_commit"] == (
        "808a585ba2c3f087c6d49a60d6a3d1bcb39ca9e6"
    )
    assert snapshot["integrity"]["payload_sha256"] == (
        "3f370784e11bf2403c2f960dfbfa2a2b2e318ecda013ac4168c31e7557644d59"
    )
    assert snapshot["observation"]["status"] == "unreviewed"

    item = snapshot["normalized_input"]
    assert item["local_date"] == "2026-09-29"
    assert item["local_time"] == "06:00"
    assert item["vis"] == 3560.0
    assert item["rh"] == 66
    assert item["c_low"] == 5
    assert item["precipitation"] == 0.0
    assert item["sun_elevation"] == 2.7

    p02 = snapshot["recorded_output"]["opportunity_scores"]["tw-034-P02"]
    assert p02["score"] == 54
    assert p02["score_confidence"] == "medium"
    assert p02["condition_state"] == "minimum_sufficient_conditions_miss"
    assert p02["runtime"]["reason"] == "visibility_too_low"

    p03 = snapshot["recorded_output"]["opportunity_scores"]["tw-034-P03"]
    assert p03["score"] == 54
    assert p03["score_confidence"] == "medium"
    assert p03["condition_state"] == "minimum_sufficient_conditions_miss"
    assert p03["runtime"]["reason"] == "low_visibility_without_mist_support"
    assert p03["runtime"]["minimum_sufficient_score_hint"] == 0
    assert p03["runtime"]["directional_mist_negative_evidence"] is False

    spatial = p03["runtime"]["spatial_mist_context"]
    assert spatial["available"] is True
    assert spatial["eligible"] is False
    assert spatial["reason"] == "directional_mist_not_distinguished_from_camera"
    assert spatial["target_sample_count"] == 6
    assert spatial["mist_target_count"] == 0
    assert spatial["directional_mist_target_count"] == 0
    assert spatial["clear_target_count"] == 0
    assert spatial["clear_bearing_count"] == 0
    assert spatial["broad_clear_target_sector"] is False

    replayed = replay_current(snapshot)
    assert set(replayed["opportunity_scores"]) == set(
        snapshot["recorded_output"]["opportunity_scores"]
    )
    diff = diff_replay(snapshot, replayed)
    assert diff["snapshot_id"] == snapshot["snapshot_id"]


def main():
    test_qingshui_broad_clear_negative_replay()
    test_qingshui_missing_spatial_preserves_low_confidence_fallback()
    test_snapshot_is_write_once_and_hash_protected()
    test_archived_live_qingshui_baseline_fixture()
    print("field snapshot tests passed")


if __name__ == "__main__":
    main()
