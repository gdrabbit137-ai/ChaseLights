"""CL-DATA-115: compact `now` sidecar generator.

Pins the contract the homepage card will read once the browser-side switch
lands: one current-hour row per place, in the place's own timezone, derived
from the same hydrated shards the publish run already has — no evaluator
re-run, no threshold touched. Covers:

  * current-hour pick from two fixture shards;
  * timezone handling (the same instant is a different local date/hour in
    Pacific/Honolulu vs Asia/Taipei — and the pick follows the SHARD's zone);
  * timezone-hint fallback (shard carries no zone, the bundle's iana wins) and
    a hard per-place failure for an unresolvable zone (no silent UTC);
  * DST both directions: the spring gap (a local hour that does not exist) and
    the fall-back repeat (a local hour that happens twice);
  * omission when the shard has no row for the place-local today;
  * nearest-edge-of-today fallback (same rule as the shipped client picker);
  * PER-PLACE staleness: one fresh shard never rescues stale ones, all-stale
    emits nothing, `data_stale: true` omits an otherwise fresh shard, and a
    shard whose freshness lags inside the forecast horizon is omitted;
  * refusals: stale, coverage floor, unknown zone — non-zero exit AND the
    previous artifact removed so the client 404s;
  * determinism (identical inputs -> byte-identical artifact);
  * `hours` nullable; ARTIFACT_VERSION emitted;
  * size budget: < 400 KB for 459 places.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "data/v2/tools"))

import build_now_sidecar as bns  # noqa: E402

BUNDLE_STAMP = "2026-11-27T02:44:37Z"
STALE_STAMP = "2026-11-25T18:00:00Z"       # two days before the bundle
STALE_EDGE_STAMP = "2026-11-26T23:00:00Z"  # before the bundle's UTC day


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


def shard(place_id, tz, rows, offset_seconds=28800, updated_at=BUNDLE_STAMP,
          region=None, data_stale=None, with_updated_at=True):
    doc = {
        "schema_version": 10,
        "region": region or place_id.split("-", 1)[0],
        "spot_id": place_id,
        "spot": {
            "spot_id": place_id,
            "timezone": tz,
            "utc_offset_seconds": offset_seconds,
            "hourly_forecast": rows,
        },
    }
    if with_updated_at:
        doc["updated_at"] = updated_at
    if data_stale is not None:
        doc["data_stale"] = data_stale
    return doc


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
    if hours is None:
        bundle.pop("forecast_hours")
    Path(path).write_text(json.dumps(bundle), encoding="utf-8")
    return Path(path)


def today_rows(date="2026-11-27", tz="Asia/Taipei", hours=range(24)):
    return [hour(date, "%02d:00" % h, tz=tz) for h in hours]


class NowSidecarTests(unittest.TestCase):
    def setUp(self):
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

    def derive(self, now=None, bundle=None):
        bundle = bundle if bundle is not None else json.loads(self.bundle_path.read_text("utf-8"))
        return bns.derive(bundle, self.weather, now=now)

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
        # 2026-11-27T02:44Z -> Taipei 10:44 (today 11/27, hour 10), Honolulu 16:44 on 11/26.
        payload, data, stats = bns.build(self.bundle_path, self.weather, out)

        self.assertEqual(payload["artifact_version"], bns.ARTIFACT_VERSION)
        self.assertEqual(payload["generated_at"], BUNDLE_STAMP)
        self.assertEqual(payload["source_bundle"], "bundle-20261127T024437Z.json")
        self.assertEqual(payload["hours"], 168)
        self.assertEqual(sorted(payload["places"]), ["tw-001", "us-112"])
        self.assertEqual(payload["places"]["tw-001"],
                         {"local_date": "2026-11-27", "hour": "10:00", "wmo": 61,
                          "temp_c": 24.5, "vis_km": 8.0, "is_today": True})
        self.assertEqual(payload["places"]["us-112"]["local_date"], "2026-11-26",
                         "Honolulu is still on 11/26 at 02:44Z: pick follows the shard zone")
        self.assertEqual(payload["places"]["us-112"]["hour"], "16:00")
        self.assertEqual(payload["places"]["us-112"]["vis_km"], 0.8)
        self.assertTrue(out.exists())
        self.assertEqual(stats["shards_read"], 2)
        self.assertEqual(stats["place_emitted"], 2)
        self.assertEqual(stats["place_total"], 2)

    def test_timezone_uses_shard_zone_over_bundle_hint(self):
        # Bundle claims Taipei, shard says Honolulu: the shard is the served truth.
        write_shard(self.weather, "tw-001", shard("tw-001", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
            hour("2026-11-27", "10:00"),
        ], offset_seconds=-36000))
        payload, _newest, _stats = self.derive()
        self.assertEqual(payload["places"]["tw-001"]["local_date"], "2026-11-26")
        self.assertEqual(payload["places"]["tw-001"]["hour"], "16:00")

    def test_timezone_hint_fallback_when_shard_has_no_zone(self):
        # A shard without its own `timezone` must use the bundle's iana hint,
        # not UTC, which would put Honolulu on the wrong day.
        doc = shard("us-112", None, [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
            hour("2026-11-27", "10:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000)
        doc["spot"]["timezone"] = None
        write_shard(self.weather, "us-112", doc)
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  today_rows(hours=range(11))))
        payload, _data, _stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        self.assertEqual(payload["places"]["us-112"]["local_date"], "2026-11-26")
        self.assertEqual(payload["places"]["us-112"]["hour"], "16:00")

    def test_unresolvable_zone_is_a_hard_per_place_failure(self):
        # No silent UTC fallback: a zone the host cannot resolve fails the place,
        # is counted, and the run exits non-zero without writing anything.
        write_shard(self.weather, "tw-001", shard("tw-001", "Mars/Olympus_Mons", [
            hour("2026-11-27", "10:00"),
        ]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        out = self.tmp / "out.json"
        with self.assertRaises(bns.NowSidecarError) as ctx:
            bns.build(self.bundle_path, self.weather, out)
        self.assertEqual(ctx.exception.code, bns.ERR_UNKNOWN_ZONE)
        self.assertIn("tw-001", str(ctx.exception))
        self.assertFalse(out.exists())
        self.assertEqual(bns.main(["--bundle", str(self.bundle_path), "--weather-dir",
                                   str(self.weather), "--out", str(out)]),
                         bns.EXIT_UNKNOWN_ZONE)

    def test_row_from_another_zone_is_never_used(self):
        # Shard zone Taipei but the row is stamped Pacific/Honolulu: skip, do not
        # emit a wrong-timezone "now".
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-27", "10:00", tz="Pacific/Honolulu"),
        ]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        payload, _newest, stats = self.derive()
        self.assertNotIn("tw-001", payload["places"])
        self.assertEqual(stats["timezone_mismatch"], 1)

    # -- DST both directions -------------------------------------------------
    def _la_shard(self, rows, updated_at=BUNDLE_STAMP):
        write_shard(self.weather, "us-112", shard(
            "us-112", "America/Los_Angeles", rows, offset_seconds=-28800,
            updated_at=updated_at))

    def test_dst_spring_gap_hour_does_not_exist(self):
        # 2026-03-08 02:00 PST -> 03:00 PDT: local 02:00 never happens. At
        # 10:30Z the place is at 03:30 PDT, so the pick is the 03:00 row.
        self.bundle_path = write_bundle(
            self.tmp / "bundle-20261127T024437Z.json",
            [("tw-001", "Asia/Taipei"), ("us-112", "America/Los_Angeles")],
            generated_at="2026-03-08T10:30:00Z")
        self._la_shard([
            hour("2026-03-08", "01:00", tz="America/Los_Angeles", temp=8.0),
            hour("2026-03-08", "03:00", tz="America/Los_Angeles", temp=9.5),
            hour("2026-03-08", "04:00", tz="America/Los_Angeles", temp=11.0),
        ])
        payload, _data, stats = self.derive()
        row = payload["places"]["us-112"]
        self.assertEqual((row["local_date"], row["hour"]), ("2026-03-08", "03:00"))
        self.assertEqual(row["temp_c"], 9.5)
        self.assertEqual(stats["no_today_row"], 0)

    def test_dst_fall_back_repeated_hour_picks_the_same_local_hour(self):
        # 2026-11-01: 01:00 occurs twice (PDT then PST). Both instants must map
        # to local 01:00 on 11-01, with no shift to 00:00 or 02:00.
        self.bundle_path = write_bundle(
            self.tmp / "bundle-20261127T024437Z.json",
            [("tw-001", "Asia/Taipei"), ("us-112", "America/Los_Angeles")],
            generated_at="2026-11-01T08:30:00Z")  # 01:30 PDT
        self._la_shard([
            hour("2026-11-01", "00:00", tz="America/Los_Angeles", temp=15.0),
            hour("2026-11-01", "01:00", tz="America/Los_Angeles", temp=14.0),
            hour("2026-11-01", "02:00", tz="America/Los_Angeles", temp=13.0),
        ])
        payload, _data, _stats = self.derive()
        self.assertEqual(payload["places"]["us-112"]["hour"], "01:00")
        self.assertEqual(payload["places"]["us-112"]["local_date"], "2026-11-01")

        # Second pass: 09:30Z is 01:30 PST, the same local hour on the same day.
        payload, _data, _stats = self.derive(now="2026-11-01T09:30:00Z")
        self.assertEqual(payload["places"]["us-112"]["hour"], "01:00")
        self.assertEqual(payload["places"]["us-112"]["local_date"], "2026-11-01")

    # -- edges / omission ----------------------------------------------------
    def test_nearest_edge_of_today_when_current_hour_not_served(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", [
            hour("2026-11-27", "00:00"),
            hour("2026-11-27", "06:00", temp=18.0),
            hour("2026-11-27", "21:00"),
        ]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
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
        payload, _newest, stats = self.derive()
        self.assertNotIn("tw-001", payload["places"], "no today row: omit, card keeps the day chip")
        self.assertIn("us-112", payload["places"])
        self.assertEqual(stats["no_today_row"], 1)

    def test_omits_place_with_no_shard(self):
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        payload, _newest, stats = self.derive()
        self.assertEqual(sorted(payload["places"]), ["us-112"])
        self.assertEqual(stats["no_shard"], 1)

    # -- per-place staleness (review condition 2) ----------------------------
    def test_one_fresh_shard_does_not_rescue_stale_ones(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  today_rows(hours=range(11))))
        for pid in ("tw-002", "tw-003", "tw-004"):
            # Rows claim TODAY, but the shard's own updated_at is two days old:
            # the hours are an older forecast wearing a fresh-looking date.
            write_shard(self.weather, pid, shard(pid, "Asia/Taipei",
                                                 today_rows(hours=range(11)),
                                                 updated_at=STALE_STAMP))
        bundle = {
            "generated_at": BUNDLE_STAMP,
            "forecast_hours": 168,
            "places": [{"place_id": p, "timezone_display": {"iana": "Asia/Taipei"}}
                       for p in ("tw-001", "tw-002", "tw-003", "tw-004")],
        }
        payload, _newest, stats = bns.derive(bundle, self.weather)
        self.assertEqual(sorted(payload["places"]), ["tw-001"],
                         "only the genuinely fresh place may carry a now row")
        self.assertEqual(stats["stale_shard"], 3)
        self.assertEqual(stats["place_emitted"], 1)
        self.assertEqual(stats["place_total"], 4)

    def test_all_stale_emits_no_places(self):
        for pid in ("tw-001", "us-112"):
            write_shard(self.weather, pid, shard(pid, "Asia/Taipei", today_rows(),
                                                 updated_at=STALE_STAMP))
        payload, _newest, stats = self.derive()
        self.assertEqual(payload["places"], {}, "a stale shard never wears a `now` row")
        self.assertEqual(stats["stale_shard"], 2)

        out = self.tmp / "out.json"
        with self.assertRaises(bns.NowSidecarError) as ctx:
            bns.build(self.bundle_path, self.weather, out)
        self.assertEqual(ctx.exception.code, bns.ERR_STALE)
        self.assertFalse(out.exists(), "a stale sidecar must never be written")

    def test_data_stale_flag_omits_an_otherwise_fresh_shard(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  today_rows(hours=range(11)),
                                                  data_stale=True))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        payload, _newest, stats = self.derive()
        self.assertNotIn("tw-001", payload["places"])
        self.assertEqual(stats["stale_data"], 1)

    def test_stale_in_horizon_shard_lags_behind_the_bundle(self):
        # Fresh-looking today rows, but the shard was last refreshed before the
        # bundle's UTC day: one refresh cycle is not enough once it crosses
        # midnight into the bundle's day.
        stale_rows = today_rows(hours=range(11))
        stale_rows[10]["time_utc"] = "2026-11-27T22:00:00Z"  # must never be the "newest"
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  stale_rows,
                                                  updated_at=STALE_EDGE_STAMP))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        payload, newest, stats = self.derive()
        self.assertNotIn("tw-001", payload["places"])
        self.assertEqual(stats["stale_shard"], 1)
        self.assertEqual(newest.strftime("%Y-%m-%dT%H:%M"),
                         "2026-11-27T02:00",
                         "the stale shard must not contribute to the newest-row stamp either")

    def test_missing_or_bad_updated_at_is_stale(self):
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  today_rows(hours=range(11)),
                                                  with_updated_at=False))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000, updated_at="not-a-timestamp"))
        payload, _newest, stats = self.derive()
        self.assertEqual(payload["places"], {})
        self.assertEqual(stats["stale_shard"], 2)

    # -- refusals: coverage floor, non-zero exit, artifact withdrawal --------
    def test_coverage_floor_refuses_a_collapsing_catalog(self):
        # 10 places declared, 1 emitted (10%) -> refuse, do not publish.
        place_ids = [("tw-%03d" % i, "Asia/Taipei") for i in range(1, 11)]
        bundle_path = write_bundle(self.tmp / "bundle-10.json", place_ids)
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  today_rows(hours=range(11))))
        out = self.tmp / "out.json"
        with self.assertRaises(bns.NowSidecarError) as ctx:
            bns.build(bundle_path, self.weather, out)
        self.assertEqual(ctx.exception.code, bns.ERR_COVERAGE)
        self.assertIn("1/10", str(ctx.exception))
        self.assertFalse(out.exists())
        self.assertEqual(bns.main(["--bundle", str(bundle_path), "--weather-dir",
                                   str(self.weather), "--out", str(out)]),
                         bns.EXIT_COVERAGE)

    def test_coverage_floor_allows_a_normal_run(self):
        place_ids = [("tw-%03d" % i, "Asia/Taipei") for i in range(1, 11)]
        bundle_path = write_bundle(self.tmp / "bundle-10.json", place_ids)
        for pid, _tz in place_ids[:7]:  # 70% >= 60%
            write_shard(self.weather, pid, shard(pid, "Asia/Taipei",
                                                 today_rows(hours=range(11))))
        payload, _data, stats = bns.build(bundle_path, self.weather, self.tmp / "out.json")
        self.assertEqual(stats["place_emitted"], 7)
        self.assertEqual(stats["place_total"], 10)
        self.assertEqual(len(payload["places"]), 7)

    def test_refusal_deletes_the_previous_artifact_only(self):
        # A previous run left an artifact behind; a stale run must remove it so
        # the client 404s and falls back to the day chip.
        out = self.tmp / "apps/web-v2/now-latest.json"
        out.parent.mkdir(parents=True)
        out.write_text('{"generated_at":"2026-11-20T00:00:00Z","places":{}}\n', encoding="utf-8")
        sibling = out.parent / "evaluations-latest.json"
        sibling.write_text("{}", encoding="utf-8")
        for pid in ("tw-001", "us-112"):
            write_shard(self.weather, pid, shard(pid, "Asia/Taipei", today_rows(),
                                                 updated_at=STALE_STAMP))

        code = bns.main(["--bundle", str(self.bundle_path), "--weather-dir",
                         str(self.weather), "--out", str(out)])
        self.assertEqual(code, bns.EXIT_STALE)
        self.assertFalse(out.exists(), "the stale artifact must be gone so the client 404s")
        self.assertTrue(sibling.exists(), "only the file this run owns may be deleted")

    def test_success_keeps_the_artifact_in_place(self):
        out = self.tmp / "now-latest.json"
        out.write_text("old\n", encoding="utf-8")
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  today_rows(hours=range(11))))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu"),
        ], offset_seconds=-36000))
        self.assertEqual(bns.main(["--bundle", str(self.bundle_path), "--weather-dir",
                                   str(self.weather), "--out", str(out)]), 0)
        self.assertEqual(json.loads(out.read_text("utf-8"))["generated_at"], BUNDLE_STAMP)

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
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  [hour("2026-11-27", "10:00")]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu")], offset_seconds=-36000))
        payload, _data, _stats = bns.build(self.bundle_path, self.weather, self.tmp / "out.json")
        self.assertEqual(sorted(payload),
                         ["artifact_version", "generated_at", "hours", "places", "source_bundle"])
        self.assertEqual(payload["artifact_version"], "now-sidecar@1")
        for row in payload["places"].values():
            self.assertEqual(sorted(row), ["hour", "is_today", "local_date", "temp_c", "vis_km", "wmo"])
            self.assertRegex(row["hour"], r"^\d{2}:00$")
            self.assertRegex(row["local_date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertIs(row["is_today"], True)

    def test_hours_is_null_when_the_bundle_omits_it(self):
        bundle_path = write_bundle(self.tmp / "bundle-nohours.json",
                                   [("tw-001", "Asia/Taipei"), ("us-112", "Pacific/Honolulu")],
                                   hours=None)
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei",
                                                  [hour("2026-11-27", "10:00")]))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu")], offset_seconds=-36000))
        payload, data, _stats = bns.build(bundle_path, self.weather, self.tmp / "out.json")
        self.assertIsNone(payload["hours"])
        self.assertIn(b'"hours":null', data)

    def test_missing_values_are_null_not_fabricated(self):
        rows = [{"time": "2026-11-27 10:00", "local_date": "2026-11-27", "timezone": "Asia/Taipei"}]
        write_shard(self.weather, "tw-001", shard("tw-001", "Asia/Taipei", rows))
        write_shard(self.weather, "us-112", shard("us-112", "Pacific/Honolulu", [
            hour("2026-11-26", "16:00", tz="Pacific/Honolulu")], offset_seconds=-36000))
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
        bundle_path = write_bundle(self.tmp / "bundle-459.json", place_ids, hours=168)
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
        _payload, data, stats = bns.build(bundle_path, self.weather, self.tmp / "out.json",
                                          now=base + timedelta(hours=3))
        self.assertLess(len(data), 400 * 1024, "artifact must stay under 400 KB for 459 places")
        self.assertGreater(len(data), 0)
        self.assertGreaterEqual(stats["place_emitted"],
                                int(stats["place_total"] * bns.COVERAGE_MIN))


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
        self.assertIn("--out apps/web-v2/now-latest.json", step)
        self.assertIn("git add apps/web-v2/now-latest.json", step)
        self.assertIn("git push origin HEAD:main", step, "the artifact must ride the publish push")

    def test_bundle_pick_is_deterministic_not_mtime_based(self):
        step = self.text.split("Build now sidecar (CL-DATA-115)", 1)[1]
        self.assertIn(
            "newest_bundle=$(ls data/v2/evaluations/bundle-*.json | sort | tail -n 1)", step)
        self.assertNotIn("ls -t data/v2/evaluations/bundle-*.json | head -n 1", step,
                         "mtime order is not timestamp order when files share an mtime")

    def test_workflow_installs_tzdata_before_running(self):
        step = self.text.split("Build now sidecar (CL-DATA-115)", 1)[1]
        self.assertIn("pip install --quiet 'tzdata", step,
                      "a host without tzdata must not silently fall back to UTC")
        self.assertLess(step.index("pip install --quiet 'tzdata"),
                        step.index("build_now_sidecar.py"),
                        "tzdata must be installed before the generator runs")

    def test_workflow_publishes_the_withdrawal_on_refusal(self):
        step = self.text.split("Build now sidecar (CL-DATA-115)", 1)[1]
        self.assertIn("sidecar_status=$?", step)
        self.assertIn('if [[ "$sidecar_status" -ne 0 ]]', step)
        withdraw = step.split('if [[ "$sidecar_status" -ne 0 ]]', 1)[1]
        self.assertIn("git add -A apps/web-v2/now-latest.json", withdraw,
                      "the deletion must be committed, or the site keeps the old now block")
        self.assertIn('exit "$sidecar_status"', withdraw, "the run must still fail loudly")

    def test_no_assets_change_is_required_by_this_ticket(self):
        # CL-DATA-115 is backend-only: the browser switch is a separate ticket.
        step = self.text.split("Build now sidecar (CL-DATA-115)", 1)[1]
        self.assertNotIn("assets/", step)


if __name__ == "__main__":
    unittest.main()
