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
CL-UI-70 (CHALLENGER-13): time-window metrics (WINDOW_METRICS below) never
vote when the window occurred (pass_hours > 0) — the day reason is then a
weather word; they vote only when the window did not occur (pass_hours == 0)
and no weather condition shows a concrete violation, with the neutral word
「非拍攝時段」. Qualification metrics (QUALIFICATION_METRICS: season /
landform / light direction) never vote at place-day level; their reason stays
in the modal's per-subject expansion rows.

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
DETAILS_DIR = ROOT / "apps/web-v2/evaluations-details"

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


# CL-UI-70 (CHALLENGER-13 audit, owner ruling — suggestion b): time-window
# metrics describe the WHEN of a subject, not its weather. A night/blue-hour
# subject is outside its window for most of any day, so the CL-UI-65
# "fewest pass_hours wins" tie-break systematically crowned the window over
# the real weather failure — a day whose window DID occur (pass_hours > 0)
# was labelled 「時段不對」 when the truth was cloud/rain/haze. Window metrics
# therefore vote only when the window did not occur at all (pass_hours == 0)
# and no weather-class condition shows a concrete violation (FAIL/PARTIAL);
# their word is the neutral 「非拍攝時段」, never a failure wording.
WINDOW_METRICS = frozenset((
    "sunrise_time_window", "sunset_window", "golden_hour_window",
    "blue_hour_window", "city_night_window", "daylight_window",
    "light_window", "astronomical_darkness"))
# CL-UI-70: per-subject eligibility conditions (season / landform / light
# direction) mean nothing at place-day level — a day word 「非季節」 next to
# recommended chips contradicts the same row (CHALLENGER-13 P3). They stay
# per-subject: their reason lives in the modal's 題材展開區, never in the
# place-day dominant vote.
QUALIFICATION_METRICS = frozenset(
    ("seasonal_state", "landform_present", "light_direction"))


def _core_violation_metric(conds, priority_map):
    """One metric id (or None) = the subject's most core violated condition."""
    # CL-UI-70: whether any weather-class condition shows a concrete problem.
    # Weather-class = neither a time window nor a per-subject qualification.
    weather_trouble = any(
        c.get("metric") not in WINDOW_METRICS
        and c.get("metric") not in QUALIFICATION_METRICS
        and c.get("day_verdict") in ("FAIL", "PARTIAL")
        for c in conds)
    # Window metrics are vote-eligible only when the window never happened
    # (pass_hours == 0) AND the weather was not the problem; qualification
    # metrics never vote at place-day level.
    def _vote_eligible(c):
        metric = c.get("metric")
        if metric in QUALIFICATION_METRICS:
            return False
        if metric in WINDOW_METRICS:
            return c.get("pass_hours", 0) == 0 and not weather_trouble
        return True
    fails = [c for c in conds if c.get("day_verdict") == "FAIL"
             and _vote_eligible(c)]
    pool = fails or [c for c in conds if c.get("day_verdict") == "UNKNOWN"
                     and c.get("role") == "REQUIRED" and c.get("tier") == "MAIN"
                     and _vote_eligible(c)]
    pool = pool or [c for c in conds if c.get("day_verdict") == "PARTIAL"
                    and c.get("pass_hours") == 0 and _vote_eligible(c)]
    # CL-UI-65: an UNFAVORABLE day can carry only PARTIAL conditions with some
    # passing hours (the passing windows never coincide). The day still owes
    # the card a short reason — fall back to any PARTIAL condition, the fewest
    # passing hours first (the binding constraint), then the core-vote order.
    pool = pool or [c for c in conds if c.get("day_verdict") == "PARTIAL"
                    and _vote_eligible(c)]
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
         "na":  ["HH:MM", ...]}          # night hour, clean weather, no window

    CHALLENGER-14/B: light_window is no longer a per-hour FAILURE word. The
    hour floor judges WEATHER only (visibility / precipitation / RH) — a
    weather violation names a weather word. A night hour
    (sun_elevation <= GENERAL_SUN_ELEVATION_MIN) with clean weather is not a
    failure and not a general pass: night scenery subjects are IN their
    window at night, so window coverage decides — hours a curated window
    covers move to "fit" (merge below); the rest land in the neutral "na"
    bucket (「非建議時段」, never a failure-style short word).

    Fail-closed: a missing hour is absent from all five (the renderer shows
    an honest no-verdict), an incomplete hour lands in "unk" (g=null, never a
    fabricated pass/fail), and a word-less metric id still names the metric
    (the renderer falls back to the bare ✗).
    """
    ok, no, unk, na = [], {}, [], []
    for hour in hours:
        t = hour.get("time")
        hh = t[-5:] if isinstance(t, str) and len(t) >= 5 else None
        if not hh:
            continue
        violated, known = general_hour_state(hour, view_scale, priority)
        if not known:
            unk.append(hh)
            continue
        # CHALLENGER-14/B: weather words win the no bucket; light_window is
        # excluded from the hour verdict entirely (it stays a DAY-layer vote
        # in general_day_baseline, which the hour layer must not echo).
        weather = [m for m in violated if m != "light_window"]
        sun = hour.get("sun_elevation")
        if weather:
            no[hh] = min(weather, key=lambda m: priority.get(m, len(priority)))
        elif sun is not None and sun <= GENERAL_SUN_ELEVATION_MIN:
            na.append(hh)
        else:
            ok.append(hh)
    return {"ok": ok, "no": no, "fit": {}, "unk": unk, "na": na}


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
                    # CHALLENGER-14/D (CHALLENGER-13 P7 closure): good_hours
                    # can carry the engine's precise sub-hour stamp (17:35,
                    # the earliest passing sample inside the 17:00 bucket).
                    # The hourly grid only renders :00 rows, so a sub-hour
                    # stamp folds into the bucket that CONTAINS it (floor to
                    # :00) — the same bucket the engine's details rows key as
                    # sub_hour_of_bucket. Kept unnormalised, those buckets
                    # were unreachable from the table (720 in the previous
                    # artifact); the precise stamp itself is untouched in the
                    # suitable[].window list, which drives the card hint.
                    key = hh[:3] + "00" if isinstance(hh, str) and len(hh) == 5 and hh[2] == ":" and hh[3:] != "00" else hh
                    fit = hourly["fit"].get(key)
                    if fit is None:
                        hourly["fit"][key] = [genre]
                    elif genre not in fit:
                        fit.append(genre)
            # CHALLENGER-14/B: one hour, one bucket — a curated window
            # covering the hour wins outright, so the hour leaves "no"
            # (previously only shadowed by the renderer's fit>ok>no priority)
            # and the neutral "na" list. fit∩no double verdicts (1,163 hours
            # in the previous artifact) become structurally impossible.
            for key in hourly["fit"]:
                hourly["no"].pop(key, None)
            if hourly["na"]:
                hourly["na"] = [key for key in hourly["na"] if key not in hourly["fit"]]
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
        "schema_version": "1.3",
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
            # CHALLENGER-14/B: the HOUR verdict is weather-only — night hours
            # are never a light_window failure; hours no curated window
            # covers land in the neutral "na" bucket (「非建議時段」), hours a
            # window covers land in "fit" and are removed from no/na (one
            # bucket per hour). The DAY baseline keeps the light_window vote
            # (day-layer wording, unchanged).
            # CHALLENGER-14/D: sub-hour good_hours stamps fold into the
            # covering :00 bucket (17:35 → 17:00, the engine's
            # sub_hour_of_bucket), so every fit bucket is reachable from the
            # hourly table's :00 rows.
            "hourly_granularity": {
                "rule": "general-v0.1 per hour, weather metrics only; "
                        "subjects_fitting = curated subject whose good_hours "
                        "window covers the hour (sub-hour stamps fold to the "
                        "covering :00 bucket); night hours without a "
                        "covering window sit in the neutral na bucket",
                "fail_closed": "missing weather or unknown fields → g=null, "
                               "no fitting subjects, no fabricated reason",
                "same_run": "generated only from the bundle run the "
                            "evaluations-details carry (asserted fail-fast, "
                            "CHALLENGER-14/A)",
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


def _bundle_run_stamp(path):
    """bundle-20261113T071212Z.json → 2026-11-13T07:12:12Z (details generated_at form)."""
    name = Path(path).name
    stem = name[len("bundle-"):-len(".json")] if name.startswith("bundle-") and name.endswith(".json") else None
    if not stem or len(stem) != 16 or stem[8] != "T" or stem[-1] != "Z":
        return None
    return "%s-%s-%sT%s:%s:%sZ" % (stem[0:4], stem[4:6], stem[6:8], stem[9:11], stem[11:13], stem[13:15])


def assert_same_run_as_details(bundle_path, details_dir=None):
    """CHALLENGER-14/A: fail-fast on cross-run drift.

    The status column (evaluations-details, the curated per-hour verdicts)
    and the subject column (this artifact) must come from the SAME
    evaluation run — different runs forecast different windows, and the same
    row then contradicts itself (owner case tw-197 11-14/15). The CI
    schedule regenerates both in one job (CL-UI-70); this assertion makes
    same-source a CONTRACT, not luck: refuse to generate when the details
    layer does not carry this bundle's run.

    details generated_at (ISO, e.g. 2026-11-13T07:12:12Z) and the bundle
    filename stamp (20261113T071212Z) are the same evaluate_batch.py run
    timestamp. Local/offline runs with NO details present degrade to a
    warning — never a fabricated pass.
    """
    details_dir = Path(details_dir) if details_dir is not None else DETAILS_DIR
    run = _bundle_run_stamp(bundle_path)
    if run is None:
        return  # not an archive bundle name; nothing to compare against
    runs = set()
    if details_dir.exists():
        for path in sorted(details_dir.glob("*.json")):
            try:
                stamp = json.loads(path.read_bytes().decode("utf-8")).get("generated_at")
            except (ValueError, OSError):
                continue
            if isinstance(stamp, str) and stamp:
                runs.add(stamp)
    if not runs:
        print("WARN: no evaluations-details under %s — same-run assertion skipped"
              % details_dir)
        return
    if run not in runs:
        newer = sorted(r for r in runs if r > run)
        raise SystemExit(
            "FAIL: subject-cards refused — cross-run drift (CHALLENGER-14/A): "
            "bundle %s (run %s) is not the run the evaluations-details carry "
            "(%s%s). Regenerate details and subject-cards from the same run "
            "(CL-UI-70 ordering: evaluate_batch.py first, then this tool)."
            % (Path(bundle_path).name, run,
               ", ".join(sorted(runs)[:3]) + ("…" if len(runs) > 3 else ""),
               "; %d detail run(s) NEWER than this bundle" % len(newer) if newer else ""))


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
    # CHALLENGER-14/A: same-run contract with the evaluations-details layer —
    # refuse to generate a subject-cards artifact from a run the status
    # column does not share (fail-fast instead of a contradictory render).
    assert_same_run_as_details(path)

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
