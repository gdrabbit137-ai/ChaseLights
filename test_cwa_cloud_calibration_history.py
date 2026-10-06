import unittest

from cwa_cloud_calibration_history import longitudinal_readiness, update_history


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
        "promotion": {
            "eligible": False,
            "observed": {
                "brier_improvement": 0.02,
                "specificity_improvement": 0.12,
                "sensitivity_loss": 0.05,
                "auc_change": 0.01,
            },
        },
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

    def test_longitudinal_review_requires_six_distinct_validation_slots(self):
        payload = None
        for index in range(5):
            payload = update_history(
                payload,
                report(
                    f"2026-10-0{index + 1}T00:00:00Z",
                    f"2026-10-0{index + 1}T06:00:00Z",
                    str(index),
                ),
            )
        readiness = payload["review_readiness"]
        self.assertFalse(readiness["eligible_for_model_review"])
        self.assertEqual(readiness["status"], "collect_more_validation_slots")
        self.assertEqual(readiness["observed_distinct_validation_slots"], 5)

        payload = update_history(
            payload,
            report(
                "2026-10-06T00:00:00Z",
                "2026-10-06T06:00:00Z",
                "5",
            ),
        )
        readiness = payload["review_readiness"]
        self.assertTrue(readiness["eligible_for_model_review"])
        self.assertEqual(readiness["status"], "eligible_for_model_review")
        self.assertEqual(readiness["observed_distinct_validation_slots"], 6)
        self.assertTrue(all(readiness["gates"].values()))

    def test_longitudinal_gate_uses_median_not_one_good_pair(self):
        entries = []
        for index in range(6):
            item = report(
                f"2026-10-{index + 1:02d}T00:00:00Z",
                f"2026-10-{index + 1:02d}T06:00:00Z",
                str(index),
            )
            if index >= 3:
                item["promotion"]["observed"]["specificity_improvement"] = 0.04
            entries.append({
                "validation_slot": item["split"]["validation_slot"],
                "generated_at": item["generated_at"],
                "selected_candidate": item["selected_candidate"],
                "promotion": item["promotion"],
            })
        readiness = longitudinal_readiness(entries)
        self.assertFalse(readiness["eligible_for_model_review"])
        self.assertEqual(readiness["status"], "longitudinal_metrics_not_stable")
        self.assertFalse(
            readiness["gates"]["median_specificity_improvement_at_least_0p10"]
        )

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
