#!/usr/bin/env python3
"""Fail-closed offline check of the single captured Open-Meteo response.

This authenticates the archived bytes against the reviewed #524 Git objects
and their one-shot acceptance, not forecast skill, freshness, or site accuracy.
No network access and no provider retry are performed.
"""
import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

FIELDS = (
    "temperature_2m", "dew_point_2m", "relative_humidity_2m",
    "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
    "wind_speed_10m", "visibility", "precipitation",
    "precipitation_probability",
)
UNITS = {
    "temperature_2m": "°C", "dew_point_2m": "°C",
    "relative_humidity_2m": "%", "cloud_cover_low": "%",
    "cloud_cover_mid": "%", "cloud_cover_high": "%",
    "wind_speed_10m": "m/s", "visibility": "m",
    "precipitation": "mm", "precipitation_probability": "%",
}

def _git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True
    ).strip()

def _utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def _require(condition, explanation):
    if not condition:
        raise ValueError("One-shot evidence: " + explanation)

def verify_one_shot_evidence(root, lock):
    root = Path(root)
    info = lock["hourly_pilot"]["one_shot_evidence"]
    prefix = "ops/v2/evidence/open-meteo-one-shot-20261019/"
    source = info["evidence_source_sha"]
    _require(info["provider_acceptance"] == "VERIFIED_ONE_SHOT", "acceptance")
    _require(info["data_state"] == "RAW_ONLY" and
             info["photography_verdict"] == "NOT_EVALUABLE" and
             not info["current_weather_eligible"], "non-scoring policy")
    _require(_git(root, "merge-base", "--is-ancestor", source, "HEAD") == "",
             "source commit ancestry")
    for relative, expected_blob in info["pinned_blobs"].items():
        path = prefix + relative
        _require(_git(root, "rev-parse", "HEAD:" + path) == expected_blob and
                 _git(root, "rev-parse", source + ":" + path) == expected_blob,
                 "blob/source mismatch: " + path)

    raw = (root / (prefix + "response-body.bin")).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    _require(digest == info["source_sha256"] and
             len(raw) == info["source_size_bytes"], "raw bytes digest/length")
    source_json = json.loads(raw)
    hourly = source_json["hourly"]
    times = hourly["time"]
    _require(len(times) == 72 and all(
        isinstance(t, int) and not isinstance(t, bool) for t in times),
        "72 epoch-second timestamps")
    _require(all(b-a == 3600 for a, b in zip(times, times[1:])),
             "hourly continuity")
    _require(datetime.fromtimestamp(times[0], timezone.utc).isoformat() ==
             "2026-10-19T16:00:00+00:00" and
             datetime.fromtimestamp(times[-1], timezone.utc).isoformat() ==
             "2026-10-22T15:00:00+00:00", "source time range")
    local = ZoneInfo("Asia/Taipei")
    _require(datetime.fromtimestamp(times[0], local).isoformat() ==
             "2026-10-20T00:00:00+08:00" and
             datetime.fromtimestamp(times[-1], local).isoformat() ==
             "2026-10-22T23:00:00+08:00", "place time zone")
    units = source_json["hourly_units"]
    _require(units.get("time") == "unixtime", "source time unit")
    for name in FIELDS:
        values = hourly[name]
        _require(units.get(name) == UNITS[name] and len(values) == 72,
                 "source field units/length " + name)
        _require(all(type(value) in (int, float) and
                     value == value and abs(value) != float("inf")
                     for value in values), "non-numeric source value " + name)
    _require(any(value == 0 for name in FIELDS for value in hourly[name]),
             "zero values were lost")
    _require(abs(source_json["latitude"] - 24.007029) < 0.00001 and
             abs(source_json["longitude"] - 121.59067) < 0.00001,
             "response grid provenance")

    summary = json.loads((root / (prefix + "acceptance-summary.json")).read_text())
    _require(summary["provider_acceptance"] == "VERIFIED_ONE_SHOT" and
             summary["http_status"] == 200 and summary["error"] is None and
             summary["raw_sha256"] == digest and
             summary["availability"] == "COMPLETE" and
             summary["replay_availability"] == "COMPLETE" and
             summary["hour_count"] == 72 and
             summary["available_cells"] == 720 and
             summary["missing_cells"] == 0, "acceptance summary")

    receipt = json.loads(gzip.decompress(
        (root / (prefix + "capture-capture.json.gz")).read_bytes()))
    replay = json.loads(gzip.decompress(
        (root / (prefix + "replay.json.gz")).read_bytes()))
    artifact = json.loads(gzip.decompress(
        (root / (prefix + "capture-artifact.json.gz")).read_bytes()))
    _require(receipt["http_status"] == 200 and
             receipt["http_attempts"] == 1 and
             receipt["raw_sha256"] == digest and
             receipt["raw_size"] == len(raw) and
             receipt["automatic_retries"] == 0, "original capture receipt")
    _require(replay["network_attempts"] == 0 and
             replay["result"]["availability"] == "COMPLETE", "offline replay")
    _require(artifact["data_state"] == "RAW_ONLY" and
             artifact["photography_verdict"] == "NOT_EVALUABLE" and
             artifact["recommendation_eligible"] is False and
             len(artifact["hours"]) == 72, "normalized research-only artifact")
    for row in artifact["hours"]:
        _require(len(row["values"]) == 10 and
                 all(v["state"] == "AVAILABLE" for v in row["values"].values()),
                 "normalized cells")

    ledger = [json.loads(x) for x in
              (root / (prefix + "capture-ledger.jsonl")).read_text().splitlines()]
    _require(len(ledger) == 2 and
             all(x["attempts_reserved"] == 1 for x in ledger) and
             (_utc(ledger[1]["requested_at_utc"]) -
              _utc(ledger[0]["requested_at_utc"])).total_seconds() >= 10800,
             "one-shot interval/ledger")
    return {
        "provider_acceptance": "VERIFIED_ONE_SHOT",
        "source_sha256": digest,
        "source_bytes": len(raw),
        "source_hours": len(times),
        "available_cells": 720,
        "replay_network_attempts": 0,
        "current_weather_eligible": False,
        "scoring_eligible": False,
    }
