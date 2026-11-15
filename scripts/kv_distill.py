#!/usr/bin/env python3
"""CL-API-01: distill evaluations-latest.json into per-place RESULTS for KV.

Contract: the APP/API layer never carries thresholds, operators, or condition
formulas — only verdicts and qualifying windows. Unknown days are kept honest.

CL-UI-99: with --weather-dir, each place record additionally gains an
"hourly" list of SLIM raw weather rows (cloud low/mid/high %, precipitation
mm/h, visibility km, wind m/s) distilled from the W1 weather_details
hourly_forecast. Raw VALUES only — never thresholds/operators — and rows
already elapsed (is_past) are dropped. Missing/malformed weather files
degrade to verdict-only records (custom-conditions rules then honestly
never match; they are never fabricated).

Output: one JSON file with {"index":..., "places":{place_id: record}} for the
CI step to upload to Cloudflare KV (key v1:evals:<place_id> / v1:evals:index).
"""
import json, sys, os
from pathlib import Path

STATES = {"GUIDANCE_SATISFIED", "UNFAVORABLE", "NOT_EVALUABLE"}

# CL-UI-99: hourly_forecast fields -> custom-condition metric names.
HOURLY_FIELDS = ("c_low", "c_mid", "c_high", "precipitation", "visibility", "wind")
HOURLY_METRICS = ("cloud_low", "cloud_mid", "cloud_high", "precipitation", "visibility", "wind")


def norm_hour(h):
    """Bundle good_hours are 'HH:MM' strings (or ints). Normalize to 'HH:MM'."""
    if isinstance(h, int):
        return f"{h:02d}:00"
    if isinstance(h, str) and ":" in h:
        return h
    return None


def distill_opportunity(opp):
    days = []
    next_window = None
    for d in opp.get("days", []):
        state = d["state"] if d["state"] in STATES else "NOT_EVALUABLE"
        hours = sorted(x for x in (norm_hour(h) for h in d.get("good_hours", [])) if x)
        if state == "GUIDANCE_SATISFIED" and hours and next_window is None:
            next_window = {"local_date": d["local_date"], "hours": hours}
        days.append({"local_date": d["local_date"], "verdict": state, "hours": hours})
    return {
        "opportunity_id": opp["opportunity_id"],
        "name_i18n": opp.get("name_i18n", {}),
        "days": days,
        "next_window": next_window,
    }


def distill_place(place, generated_at):
    return {
        "place_id": place["place_id"],
        "name_i18n": place.get("name_i18n", {}),
        "generated_at": generated_at,
        "subjects": [distill_opportunity(o) for o in place.get("opportunities", [])],
    }


def slim_hourly_row(hour):
    """CL-UI-99: one hourly_forecast row -> {local_date, hour, values{...}}.

    Only the raw fields the custom-condition engine reads; falsy numerics
    (0 precipitation, 0 cloud) are kept, missing ones dropped honestly.
    """
    if not isinstance(hour, dict):
        return None
    local_date = hour.get("local_date")
    time_s = hour.get("time")
    if not isinstance(local_date, str) or not isinstance(time_s, str) or " " not in time_s:
        return None
    values = {}
    for field, metric in zip(HOURLY_FIELDS, HOURLY_METRICS):
        v = hour.get(field)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            values[metric] = round(float(v), 2)
    if not values:
        return None
    return {"local_date": local_date, "hour": time_s.split(" ", 1)[1], "values": values}


def attach_hourly(places, weather_dir):
    """Merge slim per-hour weather rows into place records (fail-soft per place)."""
    merged = 0
    for place_id, rec in places.items():
        path = Path(weather_dir) / place_id.split("-", 1)[0] / f"{place_id}.json"
        try:
            doc = json.loads(path.read_bytes().decode("utf-8"))
            hours = (doc.get("spot") or {}).get("hourly_forecast") or []
        except (ValueError, OSError, AttributeError):
            continue  # no weather file -> verdict-only record
        rows = []
        for h in hours:
            if isinstance(h, dict) and h.get("is_past"):
                continue
            row = slim_hourly_row(h)
            if row:
                rows.append(row)
        if rows:
            rec["hourly"] = rows
            merged += 1
    return merged


def main(src, out, weather_dir=None):
    with open(src, encoding="utf-8") as f:
        bundle = json.load(f)
    generated_at = bundle["generated_at"]
    index = {
        "generated_at": generated_at,
        "bundle_version": bundle.get("evaluation_bundle_version"),
        "forecast_hours": bundle.get("forecast_hours"),
        "place_ids": [p["place_id"] for p in bundle["places"]],
        "place_count": bundle.get("place_count", len(bundle["places"])),
    }
    places = {}
    for p in bundle["places"]:
        if p.get("opportunities") is not None:
            places[p["place_id"]] = distill_place(p, generated_at)
    if weather_dir:
        merged = attach_hourly(places, weather_dir)
        print(f"hourly rows merged for {merged}/{len(places)} places from {weather_dir}")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"index": index, "places": places}, f, ensure_ascii=False, separators=(",", ":"))
    # fail-closed sanity: no forbidden keys anywhere
    text = json.dumps(places, ensure_ascii=False)
    for bad in ("threshold", "operator", "conditions", "hour_counts", "condition_contract"):
        if f'"{bad}"' in text:
            raise SystemExit(f"forbidden key '{bad}' leaked into distilled output")
    print(f"distilled {len(places)} places -> {out}")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 5):
        raise SystemExit("usage: kv_distill.py <evaluations.json> <out.json> [--weather-dir <weather_details>]")
    main(sys.argv[1], sys.argv[2], sys.argv[4] if len(sys.argv) == 5 and sys.argv[3] == "--weather-dir" else None)
