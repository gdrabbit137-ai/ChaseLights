import json
import unittest
from pathlib import Path

from photography_transparency import evaluate_transparency


FIXTURE = Path(__file__).parent / "test_fixtures" / "transparency_replay_cases.json"


class TransparencyReplayTest(unittest.TestCase):
    def test_replay_states_and_non_scoring_boundary(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertIn("not a universal photography quality score", payload["note"])
        for case in payload["cases"]:
            with self.subTest(case=case["id"]):
                result = evaluate_transparency(case["input"])
                self.assertTrue(result["available"])
                self.assertIn(result["state"], case["expected_state"])
                self.assertEqual(result["score_effect"], "none")
                self.assertEqual(result["calibration_status"], "uncalibrated")

    def test_mist_can_be_photogenic_even_when_transparency_is_poor(self):
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        case = next(c for c in payload["cases"] if c["id"] == "qingshui-photogenic-mist")
        result = evaluate_transparency(case["input"])
        self.assertLess(result["transparency_index"], 50)
        self.assertIn("desirable mist subject", case["semantic"])


if __name__ == "__main__":
    unittest.main()
