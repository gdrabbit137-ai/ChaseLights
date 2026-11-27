"""CL-DATA-115: compact `now` sidecar generator.

Pins the contract the homepage card will read once the browser-side switch
lands: one current-hour row per place, in the place's own timezone, derived
from the same hydrated shards the publish run already has — no evaluator
re-run, no threshold touched. Covers:

  * current-hour pick from two fixture shards;
  * timezone handling (the same instant is a different local date/hour in
    Pacific/Honolulu vs Asia/Taipei — and the pick follows the SHARD's zone);
  * omission when the shard has no row for the place-local today;
  * nearest-edge-of-today fallback (same rule as the shipped client picker);
  * refusal to write when the shard set is older than the bundle's day;
  * determinism (identical inputs → byte-identical artifact);
  * size budget: < 400 KB for 459 places.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "data/v2/tools"))

import build_now_sidecar as bns  # noqa: E402

BUNDLE_STAMP = "2026-11-27T02:44:37Z"


def hour(local_date, hhmm, temp=14.2, wmo=3, vis=12.0, tz="Asia/Taipei", utc=None):
    row = {
        "time": "%s %s" % (local_date, hhmm),
        "local_date": local_date,
        "timezone": tz,
        "temp": temp,
        "weather_code": wmo,
        "visibility": vis,
    }
    if utc:
        row["time_utc"] = utc
    return row


def shard(place_id, tz, rows, offset_seconds=28800, updated_at=BUNDLE_STAMP, region=None):
    return {
        "schema_version": 10,
        "updated_at": updated_at,
        "region": region or place_id.split("-", 1)[0],
        "spot_id": place_id,
        "spot": {
            "spot_id": place_id,
            "timezone": tz,
            "utc_offset_seconds": offset_seconds,
            "hourly_forecast": rows,
        },
    }


def write_shard(root, place_id, doc):
    path = Path(root) / place_id.split("-", 1)[0] / ("%s.json" % place_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def write_bundle(path, place_ids, generated_at=BUNDLE_STAMP, hours=168):
    bundle = {
        "evaluation_bundle_version": "0.2.0",
        "generated_at": generated_at,
        "forecast_hours": hours,
        "place_count": len(place_ids),
        "places": [
            {"place_id": pid, "timezone_display": {"iana": tz, "utc_offset_hours": 8}}
            for pid, tz in place_ids
        ],
    }
    Path(path).write_text(json.dumps(bundle), encoding="utf-8")
    return Path(path)


class NowSidecarTests(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.weather = self.tmp / "weather_details"
        self.weather.mkdir()
        self.bundle_path = write_bundle(
            self.tmp / "bundle-20261127T024437Z.json",
            [("tw-001", "Asia/Taipei"), ("us-112", "Pacific/Honolulu")],
        )

    def tearDown(self):
        self._tmp.cleanup()

    # -- current-hour pick ---------------------------------------------------
    def test_current_hour_picked_from_two_shards(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-27", "02:00", temp=1.0, wmo=0),
            hour("2026-11-27", "10:00", temp=24.5, wmo=61, vis=8.0),
            hour("2026-11-27", "11:00", temp=25.1, wmo=2, vis=20.0),
            hour("2026-11-27", "12:00", temp=26.0, wmo=1),
        ]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "15:00", temp=27.0, wmo=1, tz="Pacific/Honolulu"),
            hour("2026-11-26", "16:00", temp=26.4, wmo=45, vis=0.8, tz="Pacific/Honolulu"),
            hour("2026-11-26", "17:00", temp=25.9, wmo=3, tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))

        out = self.tmp / "now-latest.json"
        # 2026-11-27T02:44Z → Taipei 10:44 (today 11/27, hour 10), Honolulu 16:44 on 11/26.
        payload, data, stats = bns.build(self.bundle_path, self.weather, out)

        self.assertEqual(payload["generated_at"], BUNDLE_STAMP)
        self.assertEqual(payload["source_bundle"], "bundle-20261127T024437Z.json")
        self.assertEqual(payload["hours"], 168)
        self.assertEqual(sorted(payload["places"]), ["tw-001", "us-112"])
        self.assertEqual(payload["places"]["tw-001"],
                         {"local_date": "2026-11-27", "hour": "10:00", "wmo": 61,
                          "temp_c": 24.5, "vis_km": 8.0, "is_today": True})
        self.assertEqual(payload["places"]["us-112"]["local_date"], "2026-11-26",
                         "Honolulu is still on 11/26 at 02:44Z — the pick must follow the shard zone")
        self.assertEqual(payload["places"]["us-112"]["hour"], "16:00")
        self.assertEqual(payload["places"]["us-112"]["vis_km"], 0.8)
        self.assertTrue(out.exists())
        self.assertEqual(stats["shards_read"], 2)

    def test_timezone_uses_shard_zone_over_bundle_hint(self):
        # Bundle claims Taipei, shard says Honolulu: the shard is the served truth.
        write_shard(self.weather, "tw-001", shard("tw-001", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
            hour("2026-11-27", "10:00"),
        ], offset_seconds=-36000))
        payload, _data, _stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        self.assertEqual(payload["places"]["tw-001"]["local_date"], "2026-11-26")
        self.assertEqual(payload["places"]["tw-001"]["hour"], "16:00")

    def test_row_from_another_zone_is_never_used(self):
        # Shard zone Taipei but the row is stamped Pacific/Honolulu: skip, do not
        # emit a wrong-timezone "now".
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-27", "10:00", tz="Pacific/Honolulu"),
        ]))
        payload, _data, stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        self.assertNotIn("tw-001", payload["places"])
        self.assertEqual(stats["timezone_mismatch"], 1)

    # -- edges / omission ----------------------------------------------------
    def test_nearest_edge_of_today_when_current_hour_not_served(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-27", "00:00"),
            hour("2026-11-27", "06:00", temp=18.0),
            hour("2026-11-27", "21:00"),
        ]))
        payload, _data, _stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        row = payload["places"]["tw-001"]
        self.assertEqual(row["hour"], "06:00", "10:44 clamps to the nearest earlier hour of today")
        self.assertEqual(row["local_date"], "2026-11-27")

    def test_omits_place_without_a_today_row(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-15", "02:00"), hour("2026-11-15", "03:00"),
        ]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        out = self.tmp / "out.json"
        payload, _data, stats = bns.build(self.bundle_path, self.weather, out)
        self.assertNotIn("tw-001", payload["places"], "no today row → omit, card keeps the day chip")
        self.assertIn("us-112", payload["places"])
        self.assertEqual(stats["no_today_row"], 1)

    def test_omits_place_with_no_shard(self):
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        payload, _data, stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        self.assertEqual(sorted(payload["places"]), ["us-112"])
        self.assertEqual(stats["no_shard"], 1)

    # -- staleness refusal ---------------------------------------------------
    def test_refuses_stale_shard_set_and_writes_nothing(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-15", "02:00"), hour("2026-11-16", "02:00"),
        ]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-15", "22:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        out = self.tmp / "out.json"
        with self.assertRaises(bns.NowSidecarError) as ctx:
            bns.build(self.bundle_path, self.weather, out)
        self.assertEqual(ctx.exception.code, bns.ERR_STALE)
        self.assertFalse(out.exists(), "a stale sidecar must never be written")

    def test_cli_exit_code_is_nonzero_on_stale(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [hour("2026-11-15", "02:00")]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-15", "22:00", tz="Pacific/Honolulu")], offset_seconds=-36000))
        out = self.tmp / "out.json"
        code = bns.main(["--bundle", str(self.bundle_path), "--weather-dir", str(self.weather),
                         "--out", str(out)])
        self.assertEqual(code, bns.EXIT_STALE)
        self.assertFalse(out.exists())

    def test_refuses_when_no_shard_is_readable(self):
        with self.assertRaises(bns.NowSidecarError) as ctx:
            bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        self.assertEqual(ctx.exception.code, bns.ERR_NO_SHARDS)

    # -- determinism / shape / size -----------------------------------------
    def test_output_is_byte_deterministic(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-27", "10:00"), hour("2026-11-27", "11:00"),
        ]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        a = self.tmp / "a.json"
        b = self.tmp / "b.json"
        _p1, data1, _s1 = bns.build(self.bundle_path, self.weather, a)
        _p2, data2, _s2 = bns.build(self.bundle_path, self.weather, b)
        self.assertEqual(data1, data2)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(a.read_bytes(), data1)

    def test_shape_is_exactly_the_declared_keys(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [hour("2026-11-27", "10:00")]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu")], offset_seconds=-36000))
        payload, _data, _stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        self.assertEqual(sorted(payload), ["generated_at", "hours", "places", "source_bundle"])
        for row in payload["places"].values():
            self.assertEqual(sorted(row), ["hour", "is_today", "local_date", "temp_c", "vis_km", "wmo"])
            self.assertRegex(row["hour"], r"^\d{2}:00$")
            self.assertRegex(row["local_date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertIs(row["is_today"], True)

    def test_missing_values_are_null_not_fabricated(self):
        rows = [{"time": "2026-11-27 10:00", "local_date": "2026-11-27", "timezone": "Asia/Taipei"}]
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", rows))
        payload, _data, _stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        row = payload["places"]["tw-001"]
        self.assertIsNone(row["temp_c"])
        self.assertIsNone(row["vis_km"])
        self.assertIsNone(row["wmo"])

    def test_artifact_under_400kb_for_459_places(self):
        from datetime import datetime, timedelta, timezone

        base = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
        place_ids = [("tw-%03d" % i, "Asia/Taipei") for i in range(1, 220)]
        place_ids += [("us-%03d" % i, "Pacific/Honolulu") for i in range(1, 147)]
        place_ids += [("jp-%03d" % i, "Asia/Tokyo") for i in range(1, 95)]
        self.assertEqual(len(place_ids), 459)
        bundle_path = write_bundle(self.tmp / "bundle-459.json", place_ids)
        for pid, tz in place_ids:
            rows = []
            for h in range(24):
                rows.append({
                    "time": "2026-11-27 %02d:00" % h,
                    "local_date": "2026-11-27",
                    "timezone": tz,
                    "temp": round(10 + h * 0.6, 1),
                    "weather_code": 3,
                    "visibility": round(6.0 + (h % 7) * 1.5, 1),
                    "relative_humidity_2m": 78,
                    "precipitation": 0.0,
                    "cloud_cover_low": 40,
                    "cloud_cover_mid": 35,
                    "cloud_cover_high": 20,
                    "wind_speed_10m": 4.1,
                })
            write_shard(self.weather, pid, shard(pid, tz, rows))
        _payload, data, _stats = bns.build(bundle_path, self.weather, self.tmp / "out.json",
                                           now=base + timedelta(hours=3))
        self.assertLess(len(data), 400 * 1024, "artifact must stay under 400 KB for 459 places")
        self.assertGreater(len(data), 0)


class PublishWiringTests(unittest.TestCase):
    """The sidecar only earns its keep if the scheduled run regenerates it in
    the same run as the bundle it is stamped with."""

    def setUp(self):
        self.text = (ROOT / ".github/workflows/update_evaluations.yml").read_text(encoding="utf-8")

    def test_sidecar_step_runs_after_bundle_commit(self):
        names = [line.strip().removeprefix("- name: ").strip()
                 for line in self.text.splitlines() if line.strip().startswith("- name:")]
        self.assertIn("Build now sidecar (CL-DATA-115)", names)
        self.assertLess(names.index("Commit evaluation bundle"),
                        names.index("Build now sidecar (CL-DATA-115)"),
                        "the sidecar step must follow the bundle commit, not precede it")

    def test_sidecar_step_generates_from_the_newest_bundle_and_commits_it(self):
        step = self.text.split("Build now sidecar (CL-DATA-115)", 1)[1]
        self.assertIn("data/v2/tools/build_now_sidecar.py", step)
        self.assertIn('newest_bundle=$(ls -t data/v2/evaluations/bundle-*.json | head -n 1)', step)
        self.assertIn("--out apps/web-v2/now-latest.json", step)
        self.assertIn("git add apps/web-v2/now-latest.json", step)
        self.assertIn("git push origin HEAD:main", step, "the artifact must ride the publish push")

    def test_no_assets_change_is_required_by_this_ticket(self):
        # CL-DATA-115 is backend-only: the browser switch is a separate ticket.
        step = self.text.split("Build now sidecar (CL-DATA-115)", 1)[1]
        self.assertNotIn("assets/", step)


if __name__ == "__main__":
    unittest.main()
