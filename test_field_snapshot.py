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


def main():
    test_qingshui_broad_clear_negative_replay()
    test_qingshui_missing_spatial_preserves_low_confidence_fallback()
    test_snapshot_is_write_once_and_hash_protected()
    print("field snapshot tests passed")


if __name__ == "__main__":
    main()
