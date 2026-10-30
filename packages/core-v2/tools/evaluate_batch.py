#!/usr/bin/env python3
"""Batch V2 opportunity evaluation — GUIDANCE-only live verdicts (owner-authorized 2026-10-26).

Evaluates every genre-contracted opportunity against real Open-Meteo forecast
data (72h) plus deterministic astronomy, and publishes an evaluation-bundle
v0.1 artifact for the web-v2 UI.

Honesty contract (owner-ratified evaluation semantics):
- All conditions are GUIDANCE-mode with provisional/approved calibration.
  Results are guidance, never FAVORABLE: `live_recommendation` is always false
  and `runtime_availability` is GUIDANCE_ONLY. FAVORABLE stays locked until
  thresholds are calibrated against real shoot outcomes.
- REQUIRED-tier condition FAIL at an hour -> UNFAVORABLE for that hour.
  Any REQUIRED UNKNOWN -> NOT_EVALUABLE. Otherwise GUIDANCE_SATISFIED.
- Known-honest gaps stay UNKNOWN: water_surface_state and seasonal_state have
  no live observation source (propagate_unknown); landform_present is the
  owner-declared static presence (deterministic PASS).
- Provider provenance (URL, SHA256, retrieval time, grid point) is carried for
  every place; freshness is bounded by the pilot policy (6h -> STALE).

Usage:
  python packages/core-v2/tools/evaluate_batch.py --out apps/web-v2/evaluations-latest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for entry in (str(ROOT / "packages/core-v2"), str(ROOT / "packages/models-v2"), str(ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from adapters import open_meteo_batch as adapter  # noqa: E402
from adapters.threshold_observations import METRIC_FIELDS, compare  # noqa: E402
from astro_hourly import hour_observations, sun_events_span  # noqa: E402

BUNDLE_VERSION = "0.1.0"
ASTRO_METRICS = {"sunrise_time_window", "sunset_window", "blue_hour_window",
                 "golden_hour_window", "astronomical_darkness",
                 "moon_illumination_fraction", "moon_altitude",
                 "moon_target_separation_deg", "moon_illuminance_proxy",
                 "galactic_core_altitude"}
DECLARED_PASS_METRICS = {"landform_present"}
NO_SOURCE_METRICS = {"water_surface_state", "seasonal_state"}
# Display-only local clocks (approximate; Place index time_zone is UNKNOWN).
TZ_DISPLAY = [
    ((54, 72, -170, -130), "America/Anchorage", 9),
    ((32, 55, -130, -114), "America/Los_Angeles", 8),
    ((30, 49, -114, -96), "America/Denver", 7),
    ((24, 50, -96, -66), "America/New_York", 5),
    ((21, 26.6, 117.5, 122.2), "Asia/Taipei", 8),
    ((23, 46, 122.2, 146), "Asia/Tokyo", 9),
]


def static_timezone(lat, lon):
    for (lat_lo, lat_hi, lon_lo, lon_hi), zone, offset in TZ_DISPLAY:
        if lat_lo <= lat <= lat_hi and lon_lo <= lon <= lon_hi:
            return zone, offset
    return None, 0


def condition_verdict(condition, values, astro_row):
    """Return (verdict, detail) with verdict in PASS/FAIL/UNKNOWN."""
    metric = condition["metric"]
    operator = condition.get("operator")
    threshold = condition.get("threshold")
    if metric in NO_SOURCE_METRICS:
        return "UNKNOWN", "NO_LIVE_OBSERVATION_SOURCE"
    if metric in DECLARED_PASS_METRICS:
        return "PASS", "OWNER_DECLARED_PRESENCE"
    if metric in ASTRO_METRICS:
        value = astro_row.get(metric)
        if value is None:
            return "UNKNOWN", "ASTRO_UNAVAILABLE_AT_INSTANT"
        if operator == "none":
            # window-membership metric: astro_row carries the boolean directly
            return ("PASS" if value else "FAIL"), "ASTRO_WINDOW_MEMBERSHIP"
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "UNKNOWN", "ASTRO_NON_NUMERIC"
        try:
            passed = compare(float(value), operator, threshold)
        except Exception:
            return "UNKNOWN", "INVALID_THRESHOLD"
        return ("PASS" if passed else "FAIL"), "ASTRO_THRESHOLD"
    field = METRIC_FIELDS.get(metric)
    if field is None:
        return "UNKNOWN", "METRIC_NOT_MAPPED"
    cell = values.get(field)
    if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
        return "UNKNOWN", "CELL_NOT_AVAILABLE"
    value = cell.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "UNKNOWN", "CELL_VALUE_INVALID"
    if operator in ("is_true", "is_false", "none"):
        return "UNKNOWN", "NON_NUMERIC_OPERATOR"
    try:
        passed = compare(float(value), operator, threshold)
    except Exception:
        return "UNKNOWN", "INVALID_THRESHOLD"
    return ("PASS" if passed else "FAIL"), "FORECAST_THRESHOLD"


def hour_status(roles, verdicts):
    """Aggregate one hour into its status, honouring role semantics:
    REQUIRED FAIL or BLOCKER PASS -> UNFAVORABLE; REQUIRED/BLOCKER UNKNOWN ->
    NOT_EVALUABLE; QUALITY never gates (advisory only)."""
    fails = [cid for cid, v in verdicts.items()
             if v == "FAIL" and roles.get(cid) == "REQUIRED"]
    blockers = [cid for cid, v in verdicts.items()
                if v == "PASS" and roles.get(cid) == "BLOCKER"]
    unknowns = [cid for cid, v in verdicts.items()
                if v == "UNKNOWN" and roles.get(cid) in ("REQUIRED", "BLOCKER")]
    if fails or blockers:
        return "UNFAVORABLE", fails, unknowns
    if unknowns:
        return "NOT_EVALUABLE", fails, unknowns
    return "GUIDANCE_SATISFIED", fails, unknowns


def load_contracted():
    opportunities = []
    for path in sorted((ROOT / "data/v2/opportunities").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        contract = doc.get("condition_contract") or {}
        if not contract.get("genre_template"):
            continue
        opportunities.append(doc)
    return opportunities


def coordinate_of(opportunity):
    oid = opportunity["opportunity_id"]
    if oid == "tw-036-P01":
        # Sourced pilot binding coordinate (representative_place_weather_sample).
        return 24.031426, 121.62717, "pilot_binding_tw036"
    camera = opportunity["camera_contexts"][0]
    geo = ((camera.get("geometry") or {}).get("geojson") or {}).get("coordinates")
    if not geo:
        return None
    return geo[1], geo[0], "camera_context_provisional"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "apps/web-v2/evaluations-latest.json"))
    parser.add_argument("--archive", default=str(ROOT / "data/v2/evaluations"))
    parser.add_argument("--forecast-hours", type=int, default=72)
    arguments = parser.parse_args()

    opportunities = load_contracted()
    places_index = json.loads((ROOT / "data/v2/indexes/research/place-index.json")
                              .read_text(encoding="utf-8"))
    names = {p["place_id"]: p.get("name_i18n") or {} for p in places_index["places"]}

    by_coordinate = {}
    skipped = []
    for doc in opportunities:
        coord = coordinate_of(doc)
        if coord is None:
            skipped.append({"opportunity_id": doc["opportunity_id"],
                            "reason": "NO_VERIFIED_GEOMETRY"})
            continue
        lat, lon, source = coord
        by_coordinate.setdefault((round(lat, 4), round(lon, 4)),
                                 {"lat": lat, "lon": lon, "source": source,
                                  "opportunities": []})["opportunities"].append(doc)

    generated_at = datetime.now(timezone.utc)
    generated_iso = generated_at.isoformat(timespec="seconds").replace("+00:00", "Z")
    span_start = int(generated_at.timestamp())
    span_end = span_start + arguments.forecast_hours * 3600

    places_out = []
    provider_runs = []
    failures = []
    for index, (key, group) in enumerate(sorted(by_coordinate.items())):
        lat, lon = group["lat"], group["lon"]
        try:
            artifact = adapter.fetch_place(lat, lon, arguments.forecast_hours)
        except adapter.FetchFailure as failure:
            failures.append({"coordinate": [lat, lon], "error": str(failure)})
            continue
        provider_runs.append({
            "run_id": f"om-{lat:.4f}-{lon:.4f}-{artifact['retrieved_at_utc']}",
            "provider": "open-meteo",
            "source": artifact["sources"][0]["source_url"],
            "issued_at": artifact["retrieved_at_utc"],
            "valid_at": artifact["hours"][0]["valid_at_utc"],
            "freshness": "FRESH",
            "grid": artifact["grid"],
        })
        events = sun_events_span(lat, lon, span_start, span_end)
        zone, offset = static_timezone(lat, lon)
        need_moon = any("moon" in c["metric"] or "galactic" in c["metric"]
                        for doc in group["opportunities"]
                        for c in doc["condition_contract"]["conditions"])
        hours = artifact["hours"]
        place_out = {"place_id": None, "coordinate": [lat, lon],
                     "coordinate_source": group["source"],
                     "timezone_display": {"iana": zone, "utc_offset_hours": offset,
                                          "status": "DISPLAY_APPROXIMATION"},
                     "provider_run": provider_runs[-1],
                     "opportunities": []}
        for doc in group["opportunities"]:
            oid = doc["opportunity_id"]
            contract = doc["condition_contract"]
            contract_sha = hashlib.sha256(
                json.dumps(contract, sort_keys=True, separators=(",", ":"))
                .encode("utf-8")).hexdigest()
            days = {}
            for hour_row in hours:
                at = datetime.fromisoformat(hour_row["valid_at_utc"].replace("Z", "+00:00"))
                astro_row = hour_observations(at, lat, lon, events=events,
                                              need_moon=need_moon)
                states = {}
                roles = {}
                for condition in contract["conditions"]:
                    states[condition["id"]] = condition_verdict(
                        condition, hour_row["values"], astro_row)[0]
                    roles[condition["id"]] = condition.get("role")
                status, fails, unknowns = hour_status(roles, states)
                local_stamp = at + timedelta(hours=offset)
                day_key = local_stamp.date().isoformat()
                entry = days.setdefault(day_key, {"local_date": day_key, "hours": []})
                entry["hours"].append({
                    "utc": hour_row["valid_at_utc"],
                    "local": local_stamp.strftime("%H:%M"),
                    "status": status,
                    "failed": fails,
                    "unknown": unknowns,
                })
            day_out = []
            condition_by_id = {c["id"]: c for c in contract["conditions"]}
            for day_key in sorted(days):
                hours_out = days[day_key]["hours"]
                counts = {"GUIDANCE_SATISFIED": 0, "UNFAVORABLE": 0,
                          "NOT_EVALUABLE": 0}
                for h in hours_out:
                    counts[h["status"]] = counts.get(h["status"], 0) + 1
                if counts["GUIDANCE_SATISFIED"]:
                    state = "GUIDANCE_SATISFIED"
                elif counts["NOT_EVALUABLE"] and not counts["UNFAVORABLE"]:
                    state = "NOT_EVALUABLE"
                elif counts["UNFAVORABLE"]:
                    state = "UNFAVORABLE"
                else:
                    state = "NOT_EVALUABLE"
                conditions_day = []
                total = len(hours_out)
                for cid, cond in condition_by_id.items():
                    fails = sum(1 for h in hours_out if cid in h["failed"])
                    unknowns = sum(1 for h in hours_out if cid in h["unknown"])
                    pass_n = total - fails - unknowns
                    if unknowns == total:
                        verdict = "UNKNOWN"
                    elif pass_n == total:
                        verdict = "PASS"
                    elif fails == total:
                        verdict = "FAIL"
                    else:
                        verdict = "PARTIAL"
                    conditions_day.append({
                        "id": cid, "metric": cond["metric"],
                        "tier": cond.get("condition_tier"),
                        "role": cond.get("role"),
                        "day_verdict": verdict,
                        "pass_hours": pass_n,
                    })
                day_out.append({
                    "local_date": day_key,
                    "state": state,
                    "good_hours": [h["local"] for h in hours_out
                                   if h["status"] == "GUIDANCE_SATISFIED"],
                    "hour_counts": counts,
                    "conditions": conditions_day,
                })
            place_out["opportunities"].append({
                "opportunity_id": oid,
                "name_i18n": doc.get("name_i18n") or {},
                "genre_template": contract.get("genre_template"),
                "condition_contract_id": contract.get("contract_id"),
                "condition_contract_sha256": contract_sha,
                "days": day_out,
            })
            if place_out["place_id"] is None:
                place_out["place_id"] = doc["place_id"]
        place_out["name_i18n"] = names.get(place_out["place_id"], {})
        places_out.append(place_out)
        time.sleep(0.25)

    bundle = {
        "evaluation_bundle_version": BUNDLE_VERSION,
        "generated_at": generated_iso,
        "forecast_hours": arguments.forecast_hours,
        "guidance_only": True,
        "live_recommendation": False,
        "calibration_status": "PROVISIONAL_THRESHOLDS",
        "provider": {
            "name": "Open-Meteo",
            "licence": "CC BY 4.0",
            "urls": {"terms": "https://open-meteo.com/en/terms",
                     "licence": "https://open-meteo.com/en/licence"},
        },
        "limitations_i18n": {
            "zh-TW": "評估結果為 GUIDANCE 参考：門檻為 provisional/approved 題材模板值，"
                     "未經實拍校準，永不構成 FAVORABLE 保證。湖面狀態與花季窗口暫無即時"
                     "觀測來源（標記 UNKNOWN）。天氣為網格預報，不代表拍攝點實況。",
            "en": "Results are GUIDANCE only: thresholds are provisional/approved "
                  "genre-template values, not calibrated against real shoots, and never "
                  "constitute a FAVORABLE guarantee. Water-surface state and seasonal "
                  "windows have no live observation source (UNKNOWN). Weather is grid "
                  "forecast data, not on-site conditions.",
            "ja": "評価結果はGUIDANCE参考値です: 閾値は暫定/承認済みテンプレート値で、"
                  "実写検証されておらず、FAVORABLE保証にはなりません。水面状態と開花"
                  "窗口は観測ソースがなくUNKNOWN。天気はグリッド予報であり現地実況では"
                  "ありません。",
        },
        "place_count": len(places_out),
        "opportunity_count": sum(len(p["opportunities"]) for p in places_out),
        "fetch_failures": failures,
        "skipped": skipped,
        "provider_runs_count": len(provider_runs),
        "places": places_out,
    }
    output = Path(arguments.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    archive = Path(arguments.archive)
    archive.mkdir(parents=True, exist_ok=True)
    stamp = generated_at.strftime("%Y%m%dT%H%M%SZ")
    (archive / f"bundle-{stamp}.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "places": len(places_out),
                      "opportunities": bundle["opportunity_count"],
                      "failures": len(failures),
                      "skipped": len(skipped),
                      "bytes": output.stat().st_size}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
