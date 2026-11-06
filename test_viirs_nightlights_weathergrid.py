"""CL-CI-20: daily GIBS bundle contract (schema, provenance, honest quality)."""
import unittest

from viirs_nightlights_weathergrid import (
    FIELD_RADIANCE,
    LAADS_DEAD_END,
    SOURCE,
    SOURCE_LAYER,
    build_bundle,
    sample_bundle_at_location,
)


def make_inputs():
    lats = [2.0, 1.0]
    lons = [0.0, 1.0]
    radiance = [0.25, 0.0, None, 3.7]
    return lats, lons, radiance


class BundleSchemaTest(unittest.TestCase):
    def test_bundle_is_daily_gibs_noaa20(self):
        bundle, qc = build_bundle(*make_inputs(), observation_date="2026-11-04")
        self.assertEqual(bundle["source"], SOURCE)
        self.assertEqual(bundle["time_semantics"], "daily_raw_dnb_cloud_affected_environment_baseline")
        self.assertEqual(bundle["frames"][0]["observation_date"], "2026-11-04")
        self.assertEqual(bundle["frames"][0]["valid_time_utc"], "2026-11-04T00:00:00+00:00")
        self.assertIn(FIELD_RADIANCE, bundle["fields"])
        self.assertNotIn("nighttime_lights_quality_flag", bundle["fields"])

    def test_encoding_roundtrip(self):
        bundle, _ = build_bundle(*make_inputs(), observation_date="2026-11-04")
        values = bundle["frames"][0]["values"][FIELD_RADIANCE]
        self.assertEqual(values[0], 25)  # 0.25 / 0.01
        self.assertEqual(values[1], 0)
        self.assertIsNone(values[2])
        self.assertEqual(values[3], 370)  # 3.7 / 0.01

    def test_provenance_documents_cloud_caveat_and_dead_end(self):
        bundle, qc = build_bundle(*make_inputs(), observation_date="2026-11-04")
        prov = bundle["provenance"]
        self.assertEqual(prov["source_layer"], SOURCE_LAYER)
        self.assertIn("NASA EOSDIS GIBS", prov["distribution"])
        self.assertIn("cloud contamination", prov["cloud_caveat"])
        self.assertIn("NOT a cloud-free composite", prov["cloud_caveat"])
        self.assertIn("not Bortle class", prov["semantics"])
        self.assertIn("dead end", prov["laads_dead_end"])
        self.assertIn("terminated 2026-11-01", prov["laads_dead_end"])
        self.assertEqual(prov["colormap_version"], "v1.3")
        self.assertIn("colormaps/v1.3", prov["colormap_url"])
        self.assertIn("cloud contamination", qc["limitations"][0])

    def test_qc_fail_closed_flags(self):
        lats, lons = [2.0, 1.0], [0.0, 1.0]
        bundle, qc = build_bundle(lats, lons, [None, None, None, None], "2026-11-04")
        self.assertEqual(qc["flags"], ["all_missing"])
        bundle, qc = build_bundle(lats, lons, [0.1, 0.2, 0.3, 0.4], "2026-11-04")
        self.assertEqual(qc["flags"], [])

    def test_downsampling_budget(self):
        lats = [10.0 - i * 0.1 for i in range(600)]
        lons = [100.0 + i * 0.1 for i in range(600)]
        values = [0.5] * (600 * 600)
        bundle, qc = build_bundle(lats, lons, values, "2026-11-04")
        self.assertLessEqual(bundle["grid"]["rows"] * bundle["grid"]["cols"], 250_000)
        self.assertGreater(qc["browser_sampling_stride"], 1)


class SampleTest(unittest.TestCase):
    def test_sample_returns_radiance_and_quality_is_honestly_unknown(self):
        bundle, qc = build_bundle(*make_inputs(), observation_date="2026-11-04")
        sample = sample_bundle_at_location(bundle, 1.0, 1.0, qc=qc)
        self.assertIsNotNone(sample)
        self.assertAlmostEqual(sample[FIELD_RADIANCE], 3.7, places=6)
        self.assertIsNone(sample["viirs_sample"]["quality_flag"])
        self.assertIn("cloud", sample["viirs_sample"]["quality_note"])
        self.assertEqual(sample["viirs_sample"]["source_layer"], SOURCE_LAYER)

    def test_sample_rejects_foreign_source_and_flagged_qc(self):
        bundle, qc = build_bundle(*make_inputs(), observation_date="2026-11-04")
        foreign = dict(bundle)
        foreign["source"] = "nasa_black_marble_vnp46a4"
        self.assertIsNone(sample_bundle_at_location(foreign, 1.0, 1.0))
        self.assertIsNone(sample_bundle_at_location(bundle, 1.0, 1.0, qc={"source": "x"}))

    def test_sample_outside_bbox_is_none(self):
        bundle, _ = build_bundle(*make_inputs(), observation_date="2026-11-04")
        self.assertIsNone(sample_bundle_at_location(bundle, 50.0, 1.0))


if __name__ == "__main__":
    unittest.main()
