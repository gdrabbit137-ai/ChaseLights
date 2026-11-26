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
highest vote count wins, ties break to earlier metric_priority then metric id;
CAVEAT_METRICS (data_contradiction 「資料矛盾」, a data-quality flag) only
compete when every vote is a caveat — a caveat never hides the weather.
CL-PHYS-02: a SKY veto (SKY_VETO_METRICS: in_cloud_fog 「雲霧籠罩」 /
cloud_sea_inversion 「逆溫濕層不足」) that FAILED the subject-day is the
subject's core violation by construction, and any vote for one is decisive at
place-day level (see day_dominant_metric, the single rule both the generator
and its tests call).
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

CL-DATA-68 (owner-approved plan) — MINUTE-LEVEL WINDOW BOUNDARIES: the
civil-light floor above judged hours by the hourly Open-Meteo grid instant
(sun_elevation > -6), an hour-bucket verdict that mislabels the dawn/dusk
boundary hours by up to a full bucket. The layer now computes the
sun-elevation windows directly from the place coordinate + local date with
the validated NOAA/Meeus altitude chain (packages/models-v2/
civil_twilight.py — Open-Meteo publishes no solar angles), refined to the
minute by bisection and cached once per place-day. Every civil-light
judgment (general baseline hour floor, per-hour na/ok buckets) uses the
civil-light interval intersection; each row carries the minute-level
civil_light {dawn, dusk} provenance. A place-day whose geometry yields no
boundary (polar) or a place without coordinate/offset falls back to the
old hourly sun_elevation bucket honestly — never a fabricated verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COPY_DIR = ROOT / "data/v2/copy"
EVAL_DIR = ROOT / "data/v2/evaluations"
WEATHER_DIR = ROOT / "weather_details"
# CL-CI-37: committed same-run weather input snapshot (see load_place_hourly_weather).
WEATHER_SNAPSHOT = None
SNAPSHOT_SCHEMA = "subject-cards-weather-input@1"
SNAPSHOT_HOUR_FIELDS = ("time", "visibility", "precipitation", "rh", "sun_elevation")
DETAILS_DIR = ROOT / "apps/web-v2/evaluations-details"

# CL-DATA-68: minute-level solar windows (civil light et al.) from the same
# NOAA/Meeus chain solar_window is validated against. Open-Meteo publishes
# no solar angles, so the derived layer computes them from coordinates.
_MODELS_DIR = ROOT / "packages" / "models-v2"
if str(_MODELS_DIR) not in sys.path:
    sys.path.insert(0, str(_MODELS_DIR))
from civil_twilight import (  # noqa: E402
    hour_hits_interval, solar_day_windows)

STATUS_CLEAR = "clear"
STATUS_FAILED = "failed"
STATUS_NOT_EVALUABLE = "not_evaluable"

# CL-DATA-68 time-aware tier (owner-approved plan, single tier truth):
# today rows judge the REMAINING period after the evaluation instant
# (tier_evaluated_at = the bundle run), cross-day rows keep the full-day
# rules. Rule 2's shootable note (窗已過·今日仍可拍) is attached to the row
# as tier_reason so the card renders it without inventing new i18n keys.
TIER_NOTE_WINDOW_PASSED = {
    "zh-TW": "窗已過·今日仍可拍",
    "en": "windows passed · still shootable today",
    "ja": "撮影窓は終了・本日は撮影可",
}


def parse_evaluated_at(bundle):
    """The evaluation instant (bundle generated_at, ISO UTC) as a UTC-aware
    datetime, or None when the bundle carries none (fabricated test bundles
    keep the full-day rules)."""
    stamp = bundle.get("generated_at")
    if not isinstance(stamp, str):
        return None
    try:
        return datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None


def subject_window_left(entry, solar, eval_min):
    """Rule 1 helper: does this suitable subject still have qualifying
    window minutes after the evaluation instant?

    The good_hours stamps are the qualifying (weather+astro) bucket
    samples; the window END is the minute-level interval of the subject's
    sun-elevation window metrics covering that bucket, capped by the
    bucket end (weather is only known per hourly grid bucket — minutes
    beyond a qualified bucket are never claimed). No geometry (polar /
    no window metric) degrades to the bucket end — the old implicit
    semantics, never a fabricated later end."""
    intervals = []
    if solar is not None:
        for metric in entry.get("window_metrics") or []:
            intervals.extend(solar["intervals"].get(metric, []))
    for stamp in entry.get("window") or []:
        if not isinstance(stamp, str) or len(stamp) < 4 or ":" not in stamp:
            continue
        hh = stamp[:2]
        if not hh.isdigit():
            continue
        bucket_start = int(hh) * 60
        bucket_end = bucket_start + 60
        ends = [e for (s, e) in intervals if s < bucket_end and e > bucket_start]
        window_end = min(max(ends), bucket_end) if ends else bucket_end
        if window_end > eval_min:
            return True
    return False


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
# CL-PHYS-02 (stage 1, owner rule 2026-11-27): the evaluation-layer gates
# split into two classes that must NOT share precedence.
#
# SKY_VETO_METRICS describe the SKY and are decisive: In-Cloud Fog
# (「雲霧籠罩」) is the honest reason a white-out day was blocked, not the
# weather field it happens to trip alongside (a white-out also "fails
# visibility"); the cloud-sea inversion moisture layer (「逆溫濕層不足」) is
# the cloud sea's real primary criterion. Both SUPERSEDE the ordinary vote.
#
# CAVEAT_METRICS are data-quality flags: data_contradiction (「資料矛盾」) =
# low cloud >= 90 % while raw visibility >= 10 km, i.e. the provider fields
# disagree. That is a caveat about the data, never the weather itself, so it
# may only name a day that has no concrete weather reason — it must never
# hide the actual weather (tw-188 2026-11-26: thick cloud FAIL alongside a
# 4-hour contradiction PARTIAL must read 「厚雲」, not 「資料矛盾」).
# Precedence lives here instead of the priority table so the shipped legacy
# head order (precipitation, visibility, ...) stays byte-identical.
SKY_VETO_METRICS = ("in_cloud_fog", "cloud_sea_inversion")
CAVEAT_METRICS = frozenset(("data_contradiction",))


def _core_violation_metric(conds, priority_map):
    """One metric id (or None) = the subject's most core violated condition."""
    # CL-PHYS-02: a SKY veto that failed this day is the core violation by
    # construction — the gate IS the reason the subject was blocked (In-Cloud
    # Fog 「雲霧籠罩」 / cloud-sea inversion 「逆溫濕層不足」), not the weather
    # field that happens to trip alongside it. Gate order decides ties (fewest
    # passing hours first, then SKY_VETO_METRICS order). A data-quality CAVEAT
    # (data_contradiction 「資料矛盾」) is NOT in this branch: it competes like
    # any other condition and is demoted below (see `pool`).
    gate_fails = [c for c in conds
                  if c.get("metric") in SKY_VETO_METRICS
                  and c.get("day_verdict") == "FAIL"]
    if gate_fails:
        return min(gate_fails, key=lambda c: (
            c.get("pass_hours", 0),
            SKY_VETO_METRICS.index(c["metric"])))["metric"]
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
    # The data-quality caveat never preempts a weather reason: when the pool
    # holds any non-caveat condition, the caveat leaves it (owner rule — a
    # caveat must not hide the actual weather). It still names the subject
    # when it is the ONLY thing wrong (a contradiction with clear weather).
    weather_pool = [c for c in pool if c.get("metric") not in CAVEAT_METRICS]
    if weather_pool:
        pool = weather_pool
    best = min(pool, key=lambda c: (c.get("pass_hours", 0),
                                    _condition_sort_key(c, priority_map)))
    return best.get("metric")


def subject_core_vote(day, priority_map):
    """The single metric one UNFAVORABLE subject-day votes for (None = abstain).

    The builder's own entry point to the documented core-violation rule — the
    tests call THIS instead of re-deriving the order, so the assertion can
    never drift from the generator.
    """
    conds = list(day.get("conditions", []))
    for i, c in enumerate(conds):
        c["_order"] = i
    return _core_violation_metric(conds, priority_map)


def place_day_votes(place, date, priority_map):
    """The per-metric vote tally for one place-day, exactly as the builder
    derives it (the mounted `general` opportunity contributes no votes)."""
    votes = {}
    for opp in place.get("opportunities", []):
        if opp.get("genre_template") == "general":
            continue
        for day in opp.get("days", []):
            if day.get("local_date") != date or day.get("state") != "UNFAVORABLE":
                continue
            metric = subject_core_vote(day, priority_map)
            if metric is not None:
                votes[metric] = votes.get(metric, 0) + 1
    return votes


def day_dominant_metric(votes, priority_map):
    """Place-day dominant metric from the vote tally (None = no vote).

    Precedence (documented in fail_reason_short.json):
      1. a SKY veto with any vote is decisive (most votes, then
         SKY_VETO_METRICS order) — 「雲霧籠罩」 is the reason, not the field;
      2. otherwise the most-voted metric, ties to the earlier metric_priority
         entry, then metric id — but CAVEAT_METRICS only compete when every
         vote is a caveat, so 「資料矛盾」 can never hide the weather.
    """
    if not votes:
        return None
    sky = [m for m in SKY_VETO_METRICS if votes.get(m)]
    if sky:
        return max(sky, key=lambda m: (votes[m], -SKY_VETO_METRICS.index(m)))
    pool = {m: n for m, n in votes.items() if m not in CAVEAT_METRICS} or dict(votes)
    return min(sorted(pool),
               key=lambda m: (-pool[m], priority_map.get(m, len(priority_map)), m))


def general_view_scale(genre_templates):
    """view_scale_km from the place's genre mix (CL-DATA-65 mapping)."""
    present = set(genre_templates)
    if present & GENERAL_VISTA_GENRES:
        return 8
    if present & GENERAL_NEAR_GENRES:
        return 3
    return 5


def hour_local_minute(hour):
    """CL-DATA-68: the hour row's local bucket start in day minutes, or
    None when the row carries no parseable local time."""
    t = hour.get("time")
    if isinstance(t, str) and len(t) >= 5:
        hh, mm = t[-5:].split(":")[:2]
        if hh.isdigit() and mm.isdigit():
            return int(hh) * 60 + int(mm)
    return None


def place_day_solar(place, date):
    """CL-DATA-68: the place-day's minute-level solar windows, or None when
    the geometry is unavailable (no coordinate / no offset / compute error).
    civil_twilight caches one computation per place-day."""
    coord = place.get("coordinate")
    offset = (place.get("timezone_display") or {}).get("utc_offset_hours")
    if not coord or offset is None:
        return None
    try:
        return solar_day_windows(coord[0], coord[1], date, offset)
    except Exception:
        return None


def civil_light_intervals(solar):
    """The place-day's civil-light minute intervals ([] = honestly none),
    or None when no geometry is available (hourly bucket fallback)."""
    if solar is None:
        return None
    return solar["intervals"].get("light_window", [])


def civil_light_stamp(solar):
    """Minute-level civil dawn/dusk provenance for the row ({HH:MM,HH:MM}),
    or None when the geometry has no boundary (polar day/night)."""
    if solar is None:
        return None
    dawn = solar["events"]["civil_dawn"]
    dusk = solar["events"]["civil_dusk"]
    if dawn is None or dusk is None:
        return None
    return {"dawn": "%02d:%02d" % (dawn // 60, dawn % 60),
            "dusk": "%02d:%02d" % (dusk // 60, dusk % 60)}


def load_place_hourly_weather(place_id):
    # CL-CI-37: when a committed same-run weather snapshot is active, the
    # derivation reads it instead of the sliding weather_details window —
    # the artifact becomes byte-reproducible from committed inputs alone
    # (the CI sparse checkout has no /weather_details/ at all: 1.2G), and
    # the auto-update bots moving weather_details can no longer rot the
    # determinism tests red between refreshes.
    if WEATHER_SNAPSHOT is not None:
        return WEATHER_SNAPSHOT.get("places", {}).get(place_id, {})
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


def general_hour_state(hour, view_scale, priority, civil=None):
    """CL-UI-73: one weather hour against the general-v0.1 floor.

    Returns (violated_metrics, known). Any missing field makes the hour
    UNKNOWN: known=False — it cannot pass (fail-closed) and cannot vote.

    CL-DATA-68: `civil` is the place-day's minute-level civil-light interval
    list (civil_twilight, cached once per place-day). When present the light
    test is the civil-light interval intersection — the hour has civil-light
    minutes — replacing the hourly grid-instant bucket; the hour's sun
    elevation field is then no longer required for a light verdict. A None
    `civil` (no geometry: missing coordinate/offset, polar day) keeps the
    old hourly sun_elevation > -6 bucket honestly.
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
    if civil is not None:
        h_min = hour_local_minute(hour)
        if h_min is None or not hour_hits_interval(h_min, 60, civil):
            violated.append("light_window")
    elif sun is not None and sun <= GENERAL_SUN_ELEVATION_MIN:
        violated.append("light_window")
    known = (vis is not None and precip is not None and rh is not None
             and (civil is not None or sun is not None))
    return violated, known


def general_day_baseline(hours, view_scale, priority, words, civil=None):
    """general-v0.1 baseline for one place-day: {ok, reason_short}.

    CL-DATA-68: `civil` threads the minute-level civil-light intervals —
    the light_window vote then counts only hours with NO civil-light
    minutes instead of the hourly grid instant."""
    votes = {}
    ok = False
    for hour in hours:
        violated, known = general_hour_state(hour, view_scale, priority,
                                             civil=civil)
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


def hourly_general_rows(hours, view_scale, priority, civil=None):
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
        violated, known = general_hour_state(hour, view_scale, priority,
                                             civil=civil)
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
        else:
            # CL-DATA-68: night = the hour has no civil-light minutes
            # (minute-level civil-light interval) when the geometry is
            # available; the hourly grid instant stays the fallback.
            if civil is not None:
                h_min = hour_local_minute(hour)
                night = h_min is None or not hour_hits_interval(
                    h_min, 60, civil)
            else:
                night = sun is not None and sun <= GENERAL_SUN_ELEVATION_MIN
            if night:
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
    eval_dt = parse_evaluated_at(bundle)
    for place in bundle["places"]:
        place_id = place["place_id"]
        # CL-DATA-68: the evaluation instant in the place's display clock —
        # today rows judge the remaining period after it.
        offset = (place.get("timezone_display") or {}).get("utc_offset_hours")
        if eval_dt is not None and offset is not None:
            eval_local = eval_dt + timedelta(hours=offset)
            eval_today = eval_local.strftime("%Y-%m-%d")
            eval_minute = (eval_local.hour * 60 + eval_local.minute
                           + eval_local.second / 60.0)
        else:
            eval_local = None
            eval_today = None
            eval_minute = None
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
                    # CL-E2E-131: an all-day panorama subject whose sunrise/
                    # sunset window is only a MODIFIER (CL-DATA-12 audit) must
                    # not be labelled with the astro genre name on the card —
                    # 「日出: 11:00–16:00」 is physically impossible and the
                    # semantic gate rightly rejects it. Keep the subject
                    # (its daylight window is real) but label the row with the
                    # opportunity's own name so the card never claims a
                    # midday sunrise.
                    win_metric = {"sunrise": "sunrise_time_window",
                                  "sunset": "sunset_window"}.get(genre)
                    win_cond = next((c for c in day.get("conditions", [])
                                     if c.get("metric") == win_metric), None)
                    label_override = bool(
                        win_cond and not (win_cond.get("role") == "REQUIRED"
                                          and win_cond.get("tier") == "MAIN"))
                    entry = {
                        # CL-UI-73: the genre id rides along so the hourly
                        # buckets can reference the artifact-level dictionary
                        # instead of duplicating trilingual dicts per hour.
                        "genre": genre,
                        "subject_short": dict(genre_short),
                        "window": list(day["good_hours"]),
                        # CL-DATA-68: the opportunity's sun-elevation window
                        # metrics — the remaining-window end for the
                        # time-aware tier reads their minute-level intervals
                        # instead of an hour-bucket bucket-end.
                        "window_metrics": sorted({
                            c.get("metric") for c in day.get("conditions", [])
                            if c.get("metric") in WINDOW_METRICS}),
                    }
                    if label_override:
                        entry["name"] = dict(opp.get("name_i18n") or {})
                    row["suitable"].append(entry)
                elif state == "UNFAVORABLE":
                    row["failed"] = True
                    metric = subject_core_vote(day, priority)
                    if metric is not None:
                        row["votes"][metric] = row["votes"].get(metric, 0) + 1

        if place_id not in weather_cache:
            weather_cache[place_id] = load_place_hourly_weather(place_id)
        place_weather = weather_cache[place_id]
        view_scale = general_view_scale(opp.get("genre_template")
                                        for opp in place["opportunities"])

        dates_out = {}
        solar_by_date = {}
        for date in sorted(by_date):
            row = by_date[date]
            # CL-DATA-68: minute-level solar windows for this place-day
            # (cached once per place-day inside civil_twilight).
            solar = place_day_solar(place, date)
            solar_by_date[date] = solar
            civil = civil_light_intervals(solar)
            baseline = general_day_baseline(
                place_weather.get(date, []), view_scale, priority, fails["words"],
                civil=civil)
            dominant = None
            best = None
            dominant_source = None
            if row["votes"]:
                # CL-PHYS-02: the day-level rule (sky veto decisive, caveat
                # demoted) lives in day_dominant_metric so the tests can
                # exercise it instead of re-implementing the order.
                best = day_dominant_metric(row["votes"], priority)
                if best is not None:
                    prio_index(best)  # records an unlisted metric id
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
            # CL-DATA-68 time-aware tier: TODAY rows judge the REMAINING
            # period after tier_evaluated_at — (1) a curated subject window
            # with qualifying minutes still ahead → recommend; (2) every
            # curated window passed (or never matched) but the remaining-
            # period general baseline passes → shootable with the
            # 「窗已過·今日仍可拍」 note; (3) the remaining baseline also
            # fails → not_recommended with the short remaining reason;
            # no known remaining hour stays honest-null. Cross-day rows
            # (tomorrow/future) keep the full-day rules (rule 4) — and so
            # do rows whose bundle carries no evaluation instant.
            hours_for_day = place_weather.get(date) or []
            known_hours = any(
                all(hour.get(k) is not None for k in
                    ("visibility", "precipitation", "rh", "sun_elevation"))
                for hour in hours_for_day)
            tier_basis = "full_day"
            remaining_baseline = None
            tier_reason = None
            is_today = (eval_today is not None and date == eval_today)
            if is_today:
                tier_basis = "remaining"
                eval_min = eval_minute
                remaining = [h for h in hours_for_day
                             if (hour_local_minute(h) is not None
                                 and hour_local_minute(h) + 60 > eval_min)]  # type: ignore[operator]
                remaining_baseline = general_day_baseline(
                    remaining, view_scale, priority, fails["words"], civil=civil)
                window_left = any(
                    subject_window_left(entry, solar, eval_min)
                    for entry in row["suitable"])
                rem_known = any(
                    all(h.get(k) is not None
                        for k in ("visibility", "precipitation", "rh"))
                    and (civil is not None
                         or h.get("sun_elevation") is not None)
                    for h in remaining)
                if window_left:
                    tier = "recommend"
                elif remaining_baseline["ok"]:
                    tier = "shootable"
                    tier_reason = dict(TIER_NOTE_WINDOW_PASSED)
                elif rem_known:
                    tier = "not_recommended"
                    tier_reason = (dict(remaining_baseline["reason_short"])
                                   if remaining_baseline["reason_short"]
                                   else None)
                else:
                    tier = None
            elif row["suitable"]:
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
            hourly = hourly_general_rows(hours_for_day, view_scale, priority,
                                         civil=civil)
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
                # CL-DATA-68: minute-level civil dawn/dusk provenance for the
                # row (None = no geometry boundary, e.g. polar day).
                "civil_light": civil_light_stamp(solar),
                # CL-DATA-68 time-aware tier provenance: which rule set set
                # this tier, and (today rows) the remaining-period baseline
                # and the rule-2/rule-3 short note the card renders.
                "tier_basis": tier_basis,
                "remaining_baseline": remaining_baseline,
                "tier_reason": tier_reason,
            }
        places_out[place_id] = dates_out

    tier_semantics = {
        "rule": "CL-DATA-68 time-aware tier (owner-approved): today rows "
                "judge the REMAINING period after tier_evaluated_at — "
                "recommend when a curated subject window still has "
                "qualifying minutes ahead (window end = minute-level "
                "sun-elevation window interval, capped by the last "
                "qualified hour bucket); shootable (「窗已過·今日仍可拍」) "
                "when every curated window passed or never matched but the "
                "remaining-period general baseline passes; not_recommended "
                "(short remaining reason) when the remaining baseline also "
                "fails; no known remaining hour stays honest-null. "
                "Cross-day rows keep the full-day rules (tier_basis=full_day).",
        "rule_version": "1.0",
        "evaluated_at": bundle.get("generated_at") if isinstance(
            bundle.get("generated_at"), str) else None,
        "civil_light": {
            "rule": "CL-DATA-68 minute-level window boundaries (civil -6 deg "
                    "et al.) computed from the place coordinate + NOAA/Meeus "
                    "altitude chain, cached once per place-day; civil-light "
                    "judgments use the interval intersection, the hourly "
                    "grid instant stays the honest fallback when the "
                    "geometry yields no boundary",
            "source": "packages/models-v2/civil_twilight.py solar_day_windows",
        },
    }
    return {
        "schema_version": "1.4",
        "ticket": "CL-UI-62",
        "layer": "subject_cards",
        # CL-DATA-68: the instant every today-tier was judged against —
        # the UI's freshness check for the tier column.
        "tier_evaluated_at": tier_semantics["evaluated_at"],
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
            "tier_semantics": tier_semantics,
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


def load_weather_snapshot(path):
    """CL-CI-37: load a committed same-run weather input snapshot."""
    doc = json.loads(Path(path).read_bytes().decode("utf-8"))
    if doc.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("weather snapshot schema mismatch: %s" % doc.get("schema"))
    return doc


def write_weather_snapshot(path, weather_cache, bundle_name):
    """CL-CI-37: freeze the exact derivation inputs (grouped hour rows,
    filtered to the fields the general baseline reads) so the artifact is
    byte-reproducible from committed files alone."""
    slim = {}
    for place_id, by_date in sorted(weather_cache.items()):
        slim[place_id] = {
            date: [{k: h.get(k) for k in SNAPSHOT_HOUR_FIELDS} for h in hours]
            for date, hours in sorted(by_date.items())
        }
    doc = {"schema": SNAPSHOT_SCHEMA, "source_bundle": bundle_name, "places": slim}
    text = json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=1) + "\n"
    with open(path, "wb") as fh:
        fh.write(text.encode("utf-8"))
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description="CL-UI-62: build the derived subject-card layer from an evaluation bundle.")
    ap.add_argument("--bundle", help="path to an evaluation bundle JSON")
    ap.add_argument("--latest", action="store_true", help="use newest bundle in data/v2/evaluations")
    ap.add_argument("--out", help="output path (default: stdout)")
    ap.add_argument("--weather-snapshot", help="CL-CI-37: derive from this committed same-run weather input snapshot instead of the sliding weather_details window")
    ap.add_argument("--write-weather-snapshot", help="CL-CI-37: freeze the consumed weather inputs to this path (committed alongside the artifact)")
    args = ap.parse_args(argv)

    if not args.bundle and not args.latest:
        ap.error("pass --bundle <path> or --latest")
    path = args.bundle or latest_bundle_path()
    # CHALLENGER-14/A: same-run contract with the evaluations-details layer —
    # refuse to generate a subject-cards artifact from a run the status
    # column does not share (fail-fast instead of a contradictory render).
    assert_same_run_as_details(path)

    snapshot_doc = None
    if args.weather_snapshot:
        global WEATHER_SNAPSHOT
        snapshot_doc = load_weather_snapshot(args.weather_snapshot)
        WEATHER_SNAPSHOT = snapshot_doc

    genres, fails = load_copy()
    recorded_cache = {}
    if args.write_weather_snapshot:
        real_loader = load_place_hourly_weather
        def recording_loader(place_id, _real=real_loader, _cache=recorded_cache):
            if place_id not in _cache:
                _cache[place_id] = _real(place_id)
            return _cache[place_id]
        # derive_place_days reads the module-level loader through the
        # module namespace; patch it there so the wrapper sees every call.
        globals()["load_place_hourly_weather"] = recording_loader
        try:
            out, unknown = derive_place_days(read_bundle(path), genres, fails)
        finally:
            globals()["load_place_hourly_weather"] = real_loader
    else:
        out, unknown = derive_place_days(read_bundle(path), genres, fails)
    if args.write_weather_snapshot:
        snap_path = args.write_weather_snapshot
        write_weather_snapshot(snap_path, recorded_cache, Path(path).name)
    if args.weather_snapshot or args.write_weather_snapshot:
        snap_name = Path(args.weather_snapshot or args.write_weather_snapshot).name
        import hashlib
        sha = hashlib.sha256(Path(args.weather_snapshot or args.write_weather_snapshot).read_bytes()).hexdigest()
        out["derived_from"]["weather_snapshot"] = snap_name
        out["derived_from"]["weather_snapshot_sha256"] = sha
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
