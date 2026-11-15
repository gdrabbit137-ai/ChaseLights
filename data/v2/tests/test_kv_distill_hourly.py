# CL-UI-99: kv_distill --weather-dir hourly enrichment (custom-conditions KV feed).
# Raw VALUES only — the forbidden-key fail-closed check must keep passing, and
# missing/malformed weather files degrade to verdict-only records.
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load_distill():
    spec = importlib.util.spec_from_file_location(
        "kv_distill", ROOT / "scripts" / "kv_distill.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class KvDistillHourlyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_distill()

    def _bundle(self, tmp, place_id="tw-001"):
        src = Path(tmp) / "evals.json"
        src.write_text(json.dumps({
            "generated_at": "2026-11-15T05:10:58Z",
            "place_count": 1,
            "places": [{"place_id": place_id, "name_i18n": {"zh-TW": "測試"},
                        "opportunities": []}],
        }, ensure_ascii=False), encoding="utf-8")
        return str(src)

    def _weather(self, tmp, place_id, rows):
        d = Path(tmp) / "weather_details" / place_id.split("-", 1)[0]
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{place_id}.json").write_text(json.dumps({
            "spot": {"hourly_forecast": rows},
        }, ensure_ascii=False), encoding="utf-8")

    def test_slim_row_maps_fields_and_keeps_zero_values(self):
        row = self.mod.slim_hourly_row({
            "local_date": "2026-11-16", "time": "2026-11-16 05:00",
            "c_low": 100, "c_mid": 0, "c_high": 10,
            "precipitation": 0.0, "visibility": 24.1, "wind": 2.94,
            "is_past": False,
        })
        self.assertEqual(row["local_date"], "2026-11-16")
        self.assertEqual(row["hour"], "05:00")
        self.assertEqual(row["values"], {
            "cloud_low": 100.0, "cloud_mid": 0.0, "cloud_high": 10.0,
            "precipitation": 0.0, "visibility": 24.1, "wind": 2.94,
        })
        self.assertIsNone(self.mod.slim_hourly_row({"local_date": "2026-11-16"}))
        self.assertIsNone(self.mod.slim_hourly_row("junk"))

    def test_attach_hourly_drops_past_rows_and_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._bundle(tmp)
            self._weather(tmp, "tw-001", [
                {"local_date": "2026-11-15", "time": "2026-11-15 20:00",
                 "c_low": 5, "wind": 1.0, "is_past": True},
                {"local_date": "2026-11-16", "time": "2026-11-16 05:00",
                 "c_low": 5, "c_mid": 0, "c_high": 0,
                 "precipitation": 0.0, "visibility": 24.1, "wind": 1.2},
                {"local_date": "2026-11-17", "time": "bad-time"},
            ])
            self.mod.main(src, str(Path(tmp) / "out.json"), str(Path(tmp) / "weather_details"))
            out = json.loads((Path(tmp) / "out.json").read_text(encoding="utf-8"))
            rec = out["places"]["tw-001"]
            self.assertEqual(len(rec["hourly"]), 1)
            self.assertEqual(rec["hourly"][0]["values"]["wind"], 1.2)

            # place without a weather file stays verdict-only (honest absence)
            src2 = Path(tmp) / "evals2.json"
            src2.write_text(json.dumps({
                "generated_at": "2026-11-15T05:10:58Z", "place_count": 1,
                "places": [{"place_id": "tw-999", "name_i18n": {}, "opportunities": []}],
            }, ensure_ascii=False), encoding="utf-8")
            self.mod.main(str(src2), str(Path(tmp) / "out3.json"), str(Path(tmp) / "weather_details"))
            out3 = json.loads((Path(tmp) / "out3.json").read_text(encoding="utf-8"))
            self.assertNotIn("hourly", out3["places"]["tw-999"])

    def test_forbidden_key_check_still_passes_with_hourly(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = self._bundle(tmp)
            self._weather(tmp, "tw-001", [
                {"local_date": "2026-11-16", "time": "2026-11-16 05:00",
                 "c_low": 5, "precipitation": 0.0, "visibility": 10.0, "wind": 1.0},
            ])
            out_path = Path(tmp) / "out.json"
            self.mod.main(src, str(out_path), str(Path(tmp) / "weather_details"))
            text = out_path.read_text(encoding="utf-8")
            for bad in ("threshold", "operator", '"conditions"', "hour_counts",
                        "condition_contract"):
                self.assertNotIn(bad, text)


if __name__ == "__main__":
    unittest.main()
