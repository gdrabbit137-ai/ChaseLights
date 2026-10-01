import json
from pathlib import Path

import fetch_data
from photography_environment import classify_fog_haze


FIXTURE = Path(__file__).parent / "test_fixtures" / "fog_haze_replay_cases.json"


def test_qingshui_qixingtan_environment_replay_states():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert "not historical ground truth" in payload["note"]
    for case in payload["cases"]:
        result = classify_fog_haze(case["input"])
        assert result["state"] == case["expected_state"], case["id"]
        assert result["diagnostic_only"] is True
        assert result["score_effect"] == "none"


def test_runtime_diagnostics_expose_environment_without_changing_policy():
    item = {
        "vis": 2800,
        "rh": 93,
        "c_low": 62,
        "temp": 23.0,
        "dew": 22.0,
        "weather_code": 45,
        "aod_550nm": 0.12,
        "pm2_5_ug_m3": 8.0,
        "pop": 5,
        "precipitation": 0.0,
        "access_open": True,
        "local_time": "06:00",
        "local_month": 9,
    }
    opportunity = {
        "opportunity_id": "tw-034-P03",
        "runtime_policy": "minimum_sufficient_available",
    }
    diagnostics = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": [opportunity]}, item
    )
    diag = diagnostics["tw-034-P03"]
    assert diag["runtime_policy"] == "minimum_sufficient_available"
    assert diag["photography_environment"]["state"] == "fog_supported"
    assert diag["photography_environment"]["score_effect"] == "none"
