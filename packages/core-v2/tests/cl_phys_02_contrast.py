#!/usr/bin/env python3
"""CL-PHYS-02 before/after harness — ONE fixture, TWO checkouts.

Usage:  python cl_phys_02_contrast.py <repo-root>

Runs the 大屯山助航站 (tw-001-P02) white-wall fixture (grid 1082 m, viewpoint
1092 m, LCL 25 m AGL, 低雲 100 %, RH850/925 100 %, visibility 2.84 km) through
the *real* evaluate_batch.main() of the checkout given on the command line and
prints the per-day verdicts it produces.

The point is fidelity: the "before" leg is not simulated in the branch's own
code (no monkeypatched old semantics) — the harness is run against a pristine
`origin/main` worktree and against the CL-PHYS-02 branch, and the two stdout
blocks are the actual output of each tree.
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

HOURS = 168          # matches --forecast-hours 168 (7 days, published horizon)
OID = "tw-001-P02"


def available(value):
    return {"value": value, "state": "AVAILABLE"}


def artifact():
    """7 days of the white-wall hour; no grid_elevation_m (adapter's job)."""
    start = datetime(2026, 11, 26, 0, 0, tzinfo=timezone.utc)
    hours = []
    for index in range(HOURS):
        values = {
            "temperature_2m": available(12.0), "dew_point_2m": available(12.1),
            "relative_humidity_2m": available(100), "cloud_cover_low": available(100),
            "cloud_cover_mid": available(100), "cloud_cover_high": available(100),
            "cloud_cover_total": available(100), "wind_speed_10m": available(3.0),
            "visibility": available(2.84), "precipitation": available(0.2),
            "precipitation_probability": available(80),
            "relative_humidity_925hpa": available(100),
            "relative_humidity_850hpa": available(100),
            "wind_speed_850hpa": available(3.0),
            "aod_550nm": available(0.2),
            "temperature_delta_850_925_c": available(1.0),
            "cloud_cover_mid_and_high": available(100),
            "lcl_height_m_agl": available(25),
        }
        hours.append({"valid_at_utc": (start + timedelta(hours=index))
                      .strftime("%Y-%m-%dT%H:%M:%SZ"), "values": values})
    return {
        "adapter_version": "open-meteo-batch-0.1", "provider": "open-meteo",
        "place_coordinate": {"latitude": 25.1833, "longitude": 121.5333},
        "grid": {"latitude": 25.18, "longitude": 121.53, "elevation_m": 1082.0},
        "retrieved_at_utc": "2026-11-26T00:00:00Z",
        "sources": [
            {"source_url": "stub://forecast", "source_sha256": "0" * 64,
             "kind": "forecast", "fields": []},
            {"source_url": "stub://air-quality", "source_sha256": "0" * 64,
             "kind": "air_quality", "fields": []}],
        "freshness_policy": {}, "notes": {}, "hours": hours,
    }


def load(root):
    root = Path(root).resolve()
    for entry in (str(root / "packages/core-v2"),
                  str(root / "packages/models-v2"), str(root)):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    spec = importlib.util.spec_from_file_location(
        "evaluate_batch_contrast",
        root / "packages/core-v2/tools/evaluate_batch.py")
    eb = importlib.util.module_from_spec(spec)
    sys.modules["evaluate_batch_contrast"] = eb
    spec.loader.exec_module(eb)
    return eb


def run(root):
    eb = load(root)
    scratch = Path(tempfile.mkdtemp(prefix="cl-phys02-contrast-"))
    out = scratch / "bundle.json"
    argv = ["evaluate_batch.py", "--forecast-hours", str(HOURS),
            "--only-place-id", "tw-001", "--out", str(out),
            "--archive", str(scratch / "archive"),
            "--details-dir", str(scratch / "details")]

    def fake_fetch(lat, lon, forecast_hours):
        assert forecast_hours == HOURS, forecast_hours
        return artifact()

    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(eb.adapter, "fetch_place", fake_fetch))
        stack.enter_context(mock.patch.object(sys, "argv", argv))
        eb.main()

    bundle = json.loads(out.read_text(encoding="utf-8"))
    opportunity = next(o for place in bundle["places"]
                       for o in place["opportunities"]
                       if o["opportunity_id"] == OID)
    return eb, bundle, opportunity


def summarise(root):
    eb, bundle, opportunity = run(root)
    commit = ""
    head = Path(root).resolve() / ".git"
    try:
        import subprocess
        commit = subprocess.check_output(
            ["git", "-C", str(Path(root).resolve()), "rev-parse", "--short", "HEAD"],
            text=True).strip()
    except Exception:                     # detached/bare edge — not important
        pass
    print(f"### {Path(root).resolve()} @ {commit or 'unknown'}")
    print(f"bundle hours: {len(bundle.get('hours') or [])}"
          f"  days: {len(opportunity['days'])}")
    for day in opportunity["days"]:
        print(f"  {day['local_date']} state={day['state']}"
              f" hour_counts={day.get('hour_counts')}")
        for cond in day["conditions"]:
            if cond["metric"] in ("in_cloud_fog", "cloud_base_height",
                                  "lcl_height_m_agl", "cloud_sea_inversion"):
                print(f"      {cond['metric']}: {cond['day_verdict']}"
                      f" pass_hours={cond['pass_hours']}")
    gates = sorted({c["metric"] for d in opportunity["days"]
                    for c in d["conditions"]
                    if c["metric"] in ("in_cloud_fog", "data_contradiction",
                                       "cloud_sea_inversion")})
    print(f"  gates present: {gates}")
    return opportunity


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    summarise(sys.argv[1])
