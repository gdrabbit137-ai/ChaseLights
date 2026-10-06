import unittest

from cwa_cloud_calibration_history import update_history


def report(train, validation, generated, feature="rh_avg"):
    return {
        "calibration_id": "cwa-low-cloud-himawari-v1",
        "generated_at": generated,
        "split": {
            "training_slots": [train],
            "validation_slot": validation,
        },
        "baseline": {"feature": "max"},
        "selected_candidate": {"feature": feature},
        "validation": {"slot_utc": validation},
        "validation_candidates": [{"feature": feature}],
        "promotion": {"eligible": False},
        "snapshots": [{"slot_utc": train}, {"slot_utc": validation}],
    }


class CwaCalibrationHistoryTests(unittest.TestCase):
    def test_dedupes_same_pair_and_keeps_latest_result(self):
        first = report("2026-10-06T12:00:00Z", "2026-10-06T18:00:00Z", "a")
        second = report("2026-10-06T12:00:00Z", "2026-10-06T18:00:00Z", "b", "rh_min")
        payload = update_history(None, first)
        payload = update_history(payload, second)
        self.assertEqual(len(payload["entries"]), 1)
        self.assertEqual(payload["entries"][0]["generated_at"], "b")
        self.assertEqual(payload["entries"][0]["selected_candidate"]["feature"], "rh_min")

    def test_history_is_bounded(self):
        payload = None
        for index in range(4):
            payload = update_history(
                payload,
                report(
                    f"2026-10-0{index + 1}T00:00:00Z",
                    f"2026-10-0{index + 1}T06:00:00Z",
                    str(index),
                ),
                max_entries=2,
            )
        self.assertEqual(len(payload["entries"]), 2)
        self.assertEqual(
            [x["validation_slot"] for x in payload["entries"]],
            ["2026-10-03T06:00:00Z", "2026-10-04T06:00:00Z"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
