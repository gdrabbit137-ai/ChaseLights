import json
import tempfile
import unittest
from pathlib import Path

from weathergrid_v2_publish import publish_jma_regions


def fake_snapshot(*, bbox, forecast_hours, metadata):
    rows = 2
    cols = 2
    frames = []
    for hour in range(1, forecast_hours + 1):
        frames.append(
            {
                "forecast_hour": hour,
                "valid_time_utc": f"2026-10-03T{hour:02d}:00:00Z",
                "values": {
                    "total_cloud_percent": [10, 20, 30, 40],
                    "low_cloud_percent": [11, 21, 31, 41],
                    "mid_cloud_percent": [12, 22, 32, 42],
                    "high_cloud_percent": [13, 23, 33, 43],
                },
            }
        )
    return {
        "reference_time_utc": "2026-10-03T00:00:00Z",
        "grid": {
            "rows": rows,
            "cols": cols,
            "latitudes": [bbox["bottomlat"], bbox["toplat"]],
            "longitudes": [bbox["leftlon"], bbox["rightlon"]],
        },
        "frames": frames,
        "transport": {"layout": "test"},
    }


class WorkflowContractTest(unittest.TestCase):
    def test_v2_publisher_follows_successful_production_jma_refresh(self):
        workflow = (
            Path(__file__).resolve().parent
            / ".github/workflows/weathergrid_v2_jma_publish.yml"
        ).read_text(encoding="utf-8")
        self.assertIn('workflows: ["Update JMA MSM WeatherGrid"]', workflow)
        self.assertIn("types: [completed]", workflow)
        self.assertIn(
            "github.event_name != 'workflow_run' || "
            "github.event.workflow_run.conclusion == 'success'",
            workflow,
        )
        self.assertIn('default: "12"', workflow)
        self.assertIn("inputs.forecast_hours || '12'", workflow)


class PublishTest(unittest.TestCase):
    def test_publishes_tiles_manifest_and_index(self):
        with tempfile.TemporaryDirectory() as d:
            summary = publish_jma_regions(
                ["tw"],
                d,
                forecast_hours=2,
                metadata={"reference_time": "2026-10-03T00:00:00Z"},
                fetcher=fake_snapshot,
                max_cells=1,
                selection_time_utc="2026-10-03T01:40:00Z",
            )
            root = Path(d)
            self.assertEqual(summary["cells"], 1)
            self.assertEqual(summary["tiles"], 2)
            manifest = json.loads(
                (root / "jma/current/manifest.json").read_text()
            )
            self.assertEqual(
                manifest["default_valid_time_utc"],
                "2026-10-03T02:00:00Z",
            )
            self.assertEqual(
                manifest["nearest_valid_time_utc"],
                "2026-10-03T02:00:00Z",
            )
            self.assertEqual(
                manifest["nearest_valid_time_token"],
                "20261003T0200Z",
            )
            index = json.loads((root / "index.json").read_text())
            self.assertEqual(
                index["provider_runs"]["jma"]["reference_time_utc"],
                "2026-10-03T00:00:00Z",
            )
            cell_id = summary["published_cells"][0]["cell_id"]
            self.assertEqual(manifest["published_regions"], ["tw"])
            self.assertEqual(manifest["published_cell_ids"], [cell_id])
            self.assertEqual(index["provider_runs"]["jma"]["published_cell_ids"], [cell_id])
            tile = json.loads(
                (root / "jma/current/20261003T0100Z" / f"{cell_id}.json").read_text()
            )
            self.assertIn("cloud_cover_low", tile["values"])
            self.assertNotIn("low_cloud_percent", tile["values"])

    def test_rejects_unknown_region(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                publish_jma_regions(
                    ["moon"],
                    d,
                    metadata={},
                    fetcher=fake_snapshot,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
