"""CL-UI-62: derived subject-card layer over evaluation bundles.

Builds, from an evaluation bundle, a per-place per-day derived summary:

    {suitable: [{subject_short: <trilingual genre short name>, window: [hour buckets]}],
     dominant_reason: <trilingual short weather word or null>,
     status: "clear" | "failed" | "not_evaluable"}

Inputs (committed, W2-owned):
  - data/v2/copy/genre_short_names.json  (genre_template -> short name, trilingual)
  - data/v2/copy/fail_reason_short.json  (metric -> short weather word, trilingual,
                                          + metric_priority + dominant_reason rule)

CLI:
  python data/v2/tools/build_subject_cards.py --latest            # newest bundle in data/v2/evaluations
  python data/v2/tools/build_subject_cards.py --bundle <path> --out <path>

Output is deterministic for a given bundle; bytes are LF on disk.

Dominant-reason rule (full text in fail_reason_short.json): each failed subject
casts one vote for its most core violated metric (FAIL conditions ranked by
metric_priority, then REQUIRED>QUALITY, MAIN>other tiers, then declaration
order; fallback REQUIRED+MAIN UNKNOWN, then PARTIAL with pass_hours=0, then
CL-UI-65: any PARTIAL condition, fewest pass_hours first — an UNFAVORABLE day
whose conditions only PARTIAL (no FAIL hour) still owes the card a reason);
highest vote count wins, ties break to earlier metric_priority then metric id.

CL-UI-65 general baseline (owner ruling, general-v0.1 full-catalog): the
derivation layer additionally computes a per-place per-day shootability floor
directly from the committed hourly weather data (weather_details/<region>/
<place_id>.json hourly_forecast) — NO formal opportunity contract is created
(460 contracts would flood the catalog):

    general_baseline: {ok: bool, reason_short: trilingual word|null}

CL-UI-65 owner ruling (display semantics upgraded to three tiers): each
place-day also carries

    tier: "recommend" | "shootable" | "not_recommended" | null

  - recommend  — a curated subject qualifies (suitable non-empty);
  - shootable  — every curated subject unmet but the general baseline passes
                 ("weather allows, no decisive light");
  - not_recommended — the general baseline also fails (reason_short names why);
  - null — no known hourly weather for the day (honest no-verdict).

Conditions (general template v0.1 semantics): visibility >= view_scale_km
(vista 8 / general 5 / close-range 3 by the place's genre mix, same mapping as
mount_general_opportunities.scale_for_place), precipitation < 0.5 mm/h,
relative humidity <= 95% (surface rh is the committed proxy for the template's
925 hPa field), and the daylight window (sun elevation > -6 deg civil light).
A day is ok when at least one hour passes all four; each known-violating hour
votes its most core violated metric (metric_priority order) and the dominant
vote becomes reason_short. Hours with missing fields are UNKNOWN: they never
pass (fail-closed ok) and never fabricate a reason.

NOT_EVALUABLE is NOT an evaluated failure: a place-day mixing NOT_EVALUABLE
with evaluated subjects keeps the evaluated verdict (clear/failed + votes);
only a place-day whose every contribution was NOT_EVALUABLE stays
not_evaluable — and its dominant_reason falls back to the general baseline
reason. A failed row without any vote falls back the same way (dominant_source
records which path produced the reason: curated_votes | general_baseline).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COPY_DIR = ROOT / "data/v2/copy"
EVAL_DIR = ROOT / "data/v2/evaluations"
WEATHER_DIR = ROOT / "weather_details"

STATUS_CLEAR = "clear"
STATUS_FAILED = "failed"
STATUS_NOT_EVALUABLE = "not_evaluable"

# CL-UI-65 general baseline constants — mirror mount_general_opportunities
# (CL-DATA-65) so the derived baseline and the mounted P99 template never
# disagree about a place's view scale.
GENERAL_VISTA_GENRES = {"overlook", "mountain_view", "cloud_sea", "night_sky"}
GENERAL_NEAR_GENRES = {"waterfall", "tidal", "geological_landform", "reflection"}
GENERAL_PRECIP_MM_H_MAX = 0.5
GENERAL_RH_PERCENT_MAX = 95
GENERAL_SUN_ELEVATION_MIN = -6  # civil light; night hours never qualify


def load_copy():
    genres = json.loads((COPY_DIR / "genre_short_names.json").read_bytes().decode("utf-8"))["genres"]
    fails = json.loads((COPY_DIR / "fail_reason_short.json").read_bytes().decode("utf-8"))
    return genres, fails


def _condition_sort_key(cond, priority_map):
    """Most-core-first sort key: priority, then role, then tier, then order."""
    role_rank = 0 if cond.get("role") == "REQUIRED" else 1
    tier_rank = 0 if cond.get("tier") == "MAIN" else 1
    return (priority_map.get(cond.get("metric"), len(priority_map)),
            role_rank, tier_rank, cond.get("_order", 0))


def _core_violation_metric(conds, priority_map):
    """One metric id (or None) = the subject's most core violated condition."""
    fails = [c for c in conds if c.get("day_verdict") == "FAIL"]
    pool = fails or [c for c in conds if c.get("day_verdict") == "UNKNOWN"
                     and c.get("role") == "REQUIRED" and c.get("tier") == "MAIN"]
    pool = pool or [c for c in conds if c.get("day_verdict") == "PARTIAL"
                    and c.get("pass_hours") == 0]
    # CL-UI-65: an UNFAVORABLE day can carry only PARTIAL conditions with some
    # passing hours (the passing windows never coincide). The day still owes
    # the card a short reason — fall back to any PARTIAL condition, the fewest
    # passing hours first (the binding constraint), then the core-vote order.
    pool = pool or [c for c in conds if c.get("day_verdict") == "PARTIAL"]
    if not pool:
        return None
    best = min(pool, key=lambda c: (c.get("pass_hours", 0),
                                    _condition_sort_key(c, priority_map)))
    return best.get("metric")


def general_view_scale(genre_templates):
    """view_scale_km from the place's genre mix (CL-DATA-65 mapping)."""
    present = set(genre_templates)
    if present & GENERAL_VISTA_GENRES:
        return 8
    if present & GENERAL_NEAR_GENRES:
        return 3
    return 5


def load_place_hourly_weather(place_id):
    """Committed hourly weather for a place, grouped by local_date.

    weather_details/<region>/<place_id>.json is the W1 detail artifact; its
    spot.hourly_forecast rows carry local_date plus the raw fields the general
    baseline reads (visibility, precipitation, rh, sun_elevation). Missing
    file/fields degrade to UNKNOWN hours — never fabricated verdicts.
    """
    path = WEATHER_DIR / place_id.split("-", 1)[0] / ("%s.json" % place_id)
    if not path.exists():
        return {}
    try:
        doc = json.loads(path.read_bytes().decode("utf-8"))
    except (ValueError, OSError):
        return {}
    hours = ((doc.get("spot") or {}).get("hourly_forecast")) or []
    by_date = {}
    for hour in hours:
        date = hour.get("local_date")
        if isinstance(date, str):
            by_date.setdefault(date, []).append(hour)
    return by_date


def general_hour_state(hour, view_scale, priority):
    """CL-UI-73: one weather hour against the general-v0.1 floor.

    Returns (violated_metrics, known). Any missing field makes the hour
    UNKNOWN: known=False — it cannot pass (fail-closed) and cannot vote.
    """
    vis = hour.get("visibility")
    precip = hour.get("precipitation")
    rh = hour.get("rh")
    sun = hour.get("sun_elevation")
    violated = []
    if vis is not None and vis < view_scale:
        violated.append("visibility")
    if precip is not None and precip >= GENERAL_PRECIP_MM_H_MAX:
        violated.append("precipitation")
    if rh is not None and rh > GENERAL_RH_PERCENT_MAX:
        violated.append("relative_humidity_925hpa")
    if sun is not None and sun <= GENERAL_SUN_ELEVATION_MIN:
        violated.append("light_window")
    known = (vis is not None and precip is not None
             and rh is not None and sun is not None)
    return violated, known


def general_day_baseline(hours, view_scale, priority, words):
    """general-v0.1 baseline for one place-day: {ok, reason_short}."""
    votes = {}
    ok = False
    for hour in hours:
        violated, known = general_hour_state(hour, view_scale, priority)
        if known and not violated:
            ok = True
        if violated:
            metric = min(violated, key=lambda m: priority.get(m, len(priority)))
            votes[metric] = votes.get(metric, 0) + 1
    if ok:
        return {"ok": True, "reason_short": None}
    best = None
    if votes:
        best = min(sorted(votes), key=lambda m: (-votes[m], priority.get(m, len(priority)), m))
    return {"ok": False, "reason_short": dict(words[best]) if best else None}


def hourly_general_rows(hours, view_scale, priority):
    """CL-UI-73: per-hour general floor + fitting-subject buckets for one day.

    Compact, deduped shape (reasons reference the artifact-level
    fail_reason_short dictionary by metric id — never duplicated per hour):

        {"ok":  ["HH:MM", ...],          # general floor passes for THIS hour
         "no":  {"HH:MM": metric_id},    # floor fails; short word via dict
         "fit": {"HH:MM": [genre ids]},  # curated window covers the hour
         "unk": ["HH:MM", ...]}          # known hour, incomplete fields

    Fail-closed: a missing hour is absent from all four (the renderer shows
    an honest no-verdict), an incomplete hour lands in "unk" (g=null, never a
    fabricated pass/fail), and a word-less metric id still names the metric
    (the renderer falls back to the bare ✗).
    """
    ok, no, unk = [], {}, []
    for hour in hours:
        t = hour.get("time")
        hh = t[-5:] if isinstance(t, str) and len(t) >= 5 else None
        if not hh:
            continue
        violated, known = general_hour_state(hour, view_scale, priority)
        if not known:
            unk.append(hh)
            continue
        if violated:
            no[hh] = min(violated, key=lambda m: priority.get(m, len(priority)))
        else:
            ok.append(hh)
    return {"ok": ok, "no": no, "fit": {}, "unk": unk}


def derive_place_days(bundle, genres, fails):
    """Return (derived subject-card tree, set of unknown metric/genre refs)."""
    priority = {m: i for i, m in enumerate(fails["metric_priority"])}
    unknown_metrics = set()

    def prio_index(metric):
        if metric not in priority:
            unknown_metrics.add(metric)
            return len(priority)
        return priority[metric]

    def short_word(metric):
        return fails["words"].get(metric)

    places_out = {}
    weather_cache = {}
    for place in bundle["places"]:
        place_id = place["place_id"]
        by_date = {}
        for opp in place["opportunities"]:
            genre = opp.get("genre_template")
            if genre == "general":
                # CL-UI-65 owner ruling: the general subject is never a curated
                # chip — the mounted P99 general opportunity is superseded by
                # the derived general_baseline/tier in this layer. Its days
                # still anchor place-day rows (a general-only place keeps its
                # date coverage); they contribute no chips and no votes.
                for day in opp.get("days", []):
                    by_date.setdefault(day["local_date"], {
                        "status": STATUS_CLEAR, "suitable": [], "votes": {},
                        "not_evaluable": 0, "failed": False})
                continue
            genre_short = genres.get(genre)
            for day in opp.get("days", []):
                date = day["local_date"]
                row = by_date.setdefault(date, {
                    "status": STATUS_CLEAR, "suitable": [], "votes": {},
                    "not_evaluable": 0, "failed": False})
                state = day.get("state")
                if state == "NOT_EVALUABLE":
                    # CL-UI-65: NOT_EVALUABLE is not an evaluated failure — it
                    # never overwrites a verdict derived from evaluated
                    # subjects; it only marks the row when nothing evaluated.
                    row["not_evaluable"] += 1
                    continue
                if state == "GUIDANCE_SATISFIED" and day.get("good_hours"):
                    if genre_short is None:
                        unknown_metrics.add("genre:%s" % genre)
                        continue
                    row["suitable"].append({
                        # CL-UI-73: the genre id rides along so the hourly
                        # buckets can reference the artifact-level dictionary
                        # instead of duplicating trilingual dicts per hour.
                        "genre": genre,
                        "subject_short": dict(genre_short),
                        "window": list(day["good_hours"]),
                    })
                elif state == "UNFAVORABLE":
                    row["failed"] = True
                    conds = list(day.get("conditions", []))
                    for i, c in enumerate(conds):
                        c["_order"] = i
                    metric = _core_violation_metric(conds, priority)
                    if metric is not None:
                        row["votes"][metric] = row["votes"].get(metric, 0) + 1

        if place_id not in weather_cache:
            weather_cache[place_id] = load_place_hourly_weather(place_id)
        place_weather = weather_cache[place_id]
        view_scale = general_view_scale(opp.get("genre_template")
                                        for opp in place["opportunities"])

        dates_out = {}
        for date in sorted(by_date):
            row = by_date[date]
            baseline = general_day_baseline(
                place_weather.get(date, []), view_scale, priority, fails["words"])
            dominant = None
            best = None
            dominant_source = None
            if row["votes"]:
                best = min(sorted(row["votes"]), key=lambda m: (-row["votes"][m], prio_index(m), m))
                dominant = short_word(best)
                dominant_source = "curated_votes"
            elif baseline["reason_short"] is not None and (
                    row["failed"] or row["not_evaluable"]):
                # CL-UI-65 fallback: no curated vote (all-NOT_EVALUABLE day, or
                # an UNFAVORABLE day the extended rule still cannot name) — the
                # general baseline supplies the reason instead of a bare verdict.
                best = min(
                    ("precipitation", "visibility", "relative_humidity_925hpa", "light_window"),
                    key=lambda m: (0 if fails["words"].get(m) == baseline["reason_short"] else 1,
                                   prio_index(m)))
                dominant = dict(baseline["reason_short"])
                dominant_source = "general_baseline"
            if row["failed"]:
                status = STATUS_FAILED
            elif row["suitable"]:
                status = STATUS_CLEAR
            elif row["not_evaluable"]:
                status = STATUS_NOT_EVALUABLE
            else:
                status = STATUS_CLEAR
            # CL-UI-65 three-tier display semantics (owner ruling):
            # recommend > shootable > not_recommended; null = no known weather.
            hours_for_day = place_weather.get(date) or []
            known_hours = any(
                all(hour.get(k) is not None for k in
                    ("visibility", "precipitation", "rh", "sun_elevation"))
                for hour in hours_for_day)
            if row["suitable"]:
                tier = "recommend"
            elif baseline["ok"]:
                tier = "shootable"
            elif known_hours:
                tier = "not_recommended"
            else:
                tier = None
            # CL-UI-73: hourly granularity — each weather hour of the day gets
            # its own general-floor verdict and its fitting-subject bucket
            # (a curated subject fits the hour when the hour is inside its
            # qualifying window, i.e. the same hours that made it suitable).
            # Fail-closed: no weather / unknown fields → g=None, no reason.
            hourly = hourly_general_rows(hours_for_day, view_scale, priority)
            for entry in row["suitable"]:
                genre = entry.get("genre")
                if not genre:
                    continue
                for hh in entry.get("window") or []:
                    fit = hourly["fit"].get(hh)
                    if fit is None:
                        hourly["fit"][hh] = [genre]
                    elif genre not in fit:
                        fit.append(genre)
            dates_out[date] = {
                "status": status,
                "suitable": row["suitable"],
                "hours": hourly,
                "dominant_metric": best if dominant else None,
                "dominant_reason": dict(dominant) if dominant else None,
                "dominant_source": dominant_source,
                "general_baseline": baseline,
                "tier": tier,
            }
        places_out[place_id] = dates_out

    return {
        "schema_version": "1.2",
        "ticket": "CL-UI-62",
        "layer": "subject_cards",
        "derived_from": {
            "source_bundle": Path(bundle["_source_path"]).name,
            "source_bundle_sha256": bundle["_source_sha256"],
            "generator": "data/v2/tools/build_subject_cards.py",
            "rule_version": fails["dominant_reason_rule"]["rule_version"],
            "general_baseline": {
                "rule": "general-v0.1",
                "rule_version": "1.0",
                "source": "weather_details/<region>/<place_id>.json hourly_forecast",
                "note": "derived in this layer; no formal opportunity contract is mounted",
            },
            # CL-UI-73: the same general-v0.1 floor, evaluated per hour; the
            # day-level ok/reason stays the aggregate of these hour verdicts.
            "hourly_granularity": {
                "rule": "general-v0.1 per hour; subjects_fitting = curated "
                        "subject whose good_hours window covers the hour",
                "fail_closed": "missing weather or unknown fields → g=null, "
                               "no fitting subjects, no fabricated reason",
            },
        },
        "dictionaries": {"genre_short_names": genres, "fail_reason_short": fails["words"]},
        "places": places_out,
    }, unknown_metrics


def read_bundle(path):
    raw = Path(path).read_bytes()
    bundle = json.loads(raw.decode("utf-8"))
    bundle["_source_path"] = str(path)
    bundle["_source_sha256"] = hashlib.sha256(raw).hexdigest()
    return bundle


def latest_bundle_path():
    bundles = sorted(EVAL_DIR.glob("bundle-*.json"))
    if not bundles:
        raise FileNotFoundError("no evaluation bundles under %s" % EVAL_DIR)
    return bundles[-1]


def main(argv=None):
    ap = argparse.ArgumentParser(description="CL-UI-62: build the derived subject-card layer from an evaluation bundle.")
    ap.add_argument("--bundle", help="path to an evaluation bundle JSON")
    ap.add_argument("--latest", action="store_true", help="use newest bundle in data/v2/evaluations")
    ap.add_argument("--out", help="output path (default: stdout)")
    args = ap.parse_args(argv)

    if not args.bundle and not args.latest:
        ap.error("pass --bundle <path> or --latest")
    path = args.bundle or latest_bundle_path()

    genres, fails = load_copy()
    out, unknown = derive_place_days(read_bundle(path), genres, fails)
    if unknown:
        ap.exit(2, "FAIL: metrics/genres missing from the copy dictionaries: %s\n" % sorted(unknown))
    text = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "wb") as fh:
            fh.write(text.encode("utf-8"))
        print("wrote %s (%d places)" % (args.out, len(out["places"])))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
