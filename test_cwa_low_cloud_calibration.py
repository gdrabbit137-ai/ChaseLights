import unittest

from cwa_low_cloud_calibration import (
    BASELINE_FEATURE,
    Sample,
    _build_labels,
    _promotion_decision,
    evaluate,
    fit_linear_candidate,
)


class CwaLowCloudCalibrationTests(unittest.TestCase):
    def test_observation_labels_exclude_high_cloud_ambiguity(self):
        labels = _build_labels(
            [0, 1, 1, 1, None],
            [None, 1800.0, 3700.0, 8500.0, 1000.0],
            low_cloud_top_m=3700.0,
        )
        self.assertEqual(labels, [0, 1, 1, None, None])

    def test_two_layer_agreement_can_beat_one_layer_max_false_positives(self):
        samples = []
        # Clear cases: one layer is humid, the other is not. max-RH overcalls them.
        for _ in range(40):
            samples.append(Sample("train", 0, 94, 66, 70, 900, 5))
            samples.append(Sample("train", 0, 68, 95, 72, 850, 5))
        # Low-cloud cases: both layers are humid.
        for _ in range(80):
            samples.append(Sample("train", 1, 91, 93, 85, 350, 3))

        baseline = evaluate(
            samples,
            feature=BASELINE_FEATURE,
            low_rh=70,
            high_rh=95,
        )
        fitted = fit_linear_candidate(samples)
        self.assertIn(fitted["feature"], {"min_rh_925_850", "mean_rh_925_850"})
        self.assertLess(fitted["brier"], baseline["brier"])
        self.assertGreater(
            fitted["threshold_50"]["specificity"],
            baseline["threshold_50"]["specificity"],
        )

    def test_promotion_requires_independent_time_slots(self):
        baseline = {
            "brier": 0.30,
            "threshold_50": {
                "sensitivity": 0.80,
                "specificity": 0.30,
                "balanced_accuracy": 0.55,
            },
        }
        candidate = {
            "brier": 0.20,
            "threshold_50": {
                "sensitivity": 0.70,
                "specificity": 0.75,
                "balanced_accuracy": 0.725,
            },
        }
        decision = _promotion_decision(
            observed_slots=2,
            minimum_slots=6,
            baseline_holdout=baseline,
            candidate_holdout=candidate,
        )
        self.assertEqual(decision["status"], "collect_more_independent_slots")
        self.assertFalse(decision["automatic_production_change"])
        self.assertFalse(decision["gates"]["minimum_independent_slots"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
