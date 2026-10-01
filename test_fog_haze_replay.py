import json
import unittest
from pathlib import Path

import fetch_data
from photography_environment import classify_fog_haze


FIXTURE = Path(__file__).parent / "test_fixtures" / "fog_haze_replay_cases.json"


class FogHazeReplayTest(unittest.TestCase):
    def test_qingshui_qixingtan_environment_replay_states(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertIn("not historical ground truth", payload["note"])
        for case in payload["cases"]:
            with self.subTest(case=case["id"]):
                result = classify_fog_haze(case["input"])
                self.assertEqual(result["state"], case["expected_state"])
                self.assertTrue(result["diagnostic_only"])
                self.assertEqual(result["score_effect"], "none")

    def test_environment_diagnostic_is_timestamp_level_and_non_scoring(self):
        item = {
            "vis": 2800,
            "rh": 93,
            "c_low": 62,
            "temp": 23.0,
            "dew": 22.0,
            "weather_code": 45,
            "aod_550nm": 0.12,
            "pm2_5_ug_m3": 8.0,
        }
        environment = fetch_data._build_photography_environment_diagnostic(item)
        self.assertEqual(environment["state"], "fog_supported")
        self.assertEqual(environment["score_effect"], "none")

        # Opportunity runtime remains subject-specific and must not duplicate
        # the same environment object for every Opportunity.
        opportunity = {
            "opportunity_id": "tw-034-P03",
            "runtime_policy": "minimum_sufficient_available",
        }
        runtime = fetch_data._build_opportunity_runtime_diagnostics(
            {"opportunities": [opportunity]},
            {
                **item,
                "pop": 5,
                "precipitation": 0.0,
                "access_open": True,
                "local_time": "06:00",
                "local_month": 9,
            },
        )
        self.assertNotIn("photography_environment", runtime["tw-034-P03"])


if __name__ == "__main__":
    unittest.main()
