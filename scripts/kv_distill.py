#!/usr/bin/env python3
"""CL-API-01: distill evaluations-latest.json into per-place RESULTS for KV.

Contract: the APP/API layer never carries thresholds, operators, or condition
formulas — only verdicts and qualifying windows. Unknown days are kept honest.

Output: one JSON file with {"index":..., "places":{place_id: record}} for the
CI step to upload to Cloudflare KV (key v1:evals:<place_id> / v1:evals:index).
"""
import json, sys, os

STATES = {"GUIDANCE_SATISFIED", "UNFAVORABLE", "NOT_EVALUABLE"}


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


def main(src, out):
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
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"index": index, "places": places}, f, ensure_ascii=False, separators=(",", ":"))
    # fail-closed sanity: no forbidden keys anywhere
    text = json.dumps(places, ensure_ascii=False)
    for bad in ("threshold", "operator", "conditions", "hour_counts", "condition_contract"):
        if f'"{bad}"' in text:
            raise SystemExit(f"forbidden key '{bad}' leaked into distilled output")
    print(f"distilled {len(places)} places -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
