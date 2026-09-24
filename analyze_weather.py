import sys
import json
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from regions import get_spots
from fetch_data import (
    fetch_weather_for_spot,
    fetch_noaa_kp,
    fetch_noaa_kp_series,
    I18N_MESSAGES,
    FACTOR_TEMPLATES,
)


def _metric_for_theme(item, theme):
    scores = item.get("theme_scores") or item.get("tag_scores") or {}
    return scores.get(theme) or {}


def _metric_for_opportunity(item, opportunity_id):
    return (item.get("opportunity_scores") or {}).get(opportunity_id) or {}


def _window_for_metric(items, best_index, metric_getter):
    if not items:
        return None, None
    best_score = (metric_getter(items[best_index]) or {}).get("score", 0)
    threshold = max(55, best_score - 4)
    left = right = best_index
    while left > 0:
        score = (metric_getter(items[left - 1]) or {}).get("score", -1)
        if score < threshold:
            break
        left -= 1
    while right + 1 < len(items):
        score = (metric_getter(items[right + 1]) or {}).get("score", -1)
        if score < threshold:
            break
        right += 1
    start = items[left].get("time")
    try:
        end_dt = datetime.strptime(items[right].get("time"), "%Y-%m-%d %H:%M") + timedelta(hours=1)
        end = end_dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        end = items[right].get("time")
    return start, end


def _window_for_theme(items, best_index, theme):
    return _window_for_metric(items, best_index, lambda item: _metric_for_theme(item, theme))


def _window_for_opportunity(items, best_index, opportunity_id):
    if not items:
        return None, None

    def viable(item):
        metric = _metric_for_opportunity(item, opportunity_id) or {}
        return (
            metric.get("temporal_eligible") is not False
            and item.get("access_open") is not False
        )

    best_metric = _metric_for_opportunity(items[best_index], opportunity_id) or {}
    best_score = best_metric.get("score", 0)
    threshold = max(55, best_score - 4)
    left = right = best_index

    while left > 0 and viable(items[left - 1]):
        score = (_metric_for_opportunity(items[left - 1], opportunity_id) or {}).get("score", -1)
        if score < threshold:
            break
        left -= 1

    while right + 1 < len(items) and viable(items[right + 1]):
        score = (_metric_for_opportunity(items[right + 1], opportunity_id) or {}).get("score", -1)
        if score < threshold:
            break
        right += 1

    start = items[left].get("time")
    try:
        end_dt = datetime.strptime(items[right].get("time"), "%Y-%m-%d %H:%M") + timedelta(hours=1)
        end = end_dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        end = items[right].get("time")
    return start, end


def _base_snapshot(item, metric, window_start=None, window_end=None):
    return {
        "score": metric.get("score", item.get("score", 0)),
        "status_key": metric.get("status_key", item.get("status_key")),
        "indicator_key": metric.get("indicator_key", item.get("indicator_key")),
        "factors": metric.get("factors", item.get("factors", [])),
        "best_time": item.get("time"),
        "best_time_utc": item.get("time_utc"),
        "window_start": window_start or item.get("time"),
        "window_end": window_end or item.get("time"),
        "timezone_abbr": item.get("timezone_abbr"),
        "kp": item.get("kp"),
        "kp_source": item.get("kp_source"),
        "cloud_base_agl": item.get("cloud_base_agl"),
        "cloud_base_asl": item.get("cloud_base_asl"),
        "cloud_base_delta": item.get("cloud_base_delta"),
        "camera_elevation": item.get("camera_elevation"),
        "temp": item.get("temp"),
        "rh": item.get("rh"),
        "c_low": item.get("c_low"),
        "c_mid": item.get("c_mid"),
        "c_high": item.get("c_high"),
        "wind": item.get("wind"),
        "visibility": item.get("visibility"),
        "astronomy_valid": item.get("astronomy_valid"),
        "access_open": item.get("access_open"),
        "sun_azimuth": item.get("sun_azimuth"),
        "sun_elevation": item.get("sun_elevation"),
        "moon_azimuth": item.get("moon_azimuth"),
        "moon_elevation": item.get("moon_elevation"),
        "moon_illumination": item.get("moon_illumination"),
        "galactic_core_azimuth": item.get("galactic_core_azimuth"),
        "galactic_core_elevation": item.get("galactic_core_elevation"),
    }


def _compact_snapshot(item, theme, window_start=None, window_end=None):
    metric = _metric_for_theme(item, theme)
    snap = _base_snapshot(item, metric, window_start, window_end)
    snap["theme"] = theme
    return snap


def _compact_opportunity_snapshot(item, opportunity, window_start=None, window_end=None):
    oid = opportunity.get("opportunity_id")
    metric = _metric_for_opportunity(item, oid)
    snap = _base_snapshot(item, metric, window_start, window_end)
    snap.update({
        "opportunity_id": oid,
        "opportunity_name": opportunity.get("name_zh"),
        "theme": opportunity.get("legacy_theme"),
        "runtime_policy": metric.get("runtime_policy", opportunity.get("runtime_policy")),
        "condition_state": metric.get("condition_state"),
        "score_confidence": metric.get("score_confidence"),
        "base_theme_score": metric.get("base_theme_score"),
        "formula_confidence": metric.get("formula_confidence", opportunity.get("formula_confidence")),
        "temporal_eligible": metric.get("temporal_eligible"),
        "temporal_reason": metric.get("temporal_reason"),
    })
    return snap


def _build_day_summaries(hourly, themes, opportunities=None):
    future = [h for h in hourly if not h.get("is_past")]
    by_date = defaultdict(list)
    for h in future:
        if h.get("local_date"):
            by_date[h["local_date"]].append(h)

    researched = [
        opportunity for opportunity in (opportunities or [])
        if opportunity.get("opportunity_id") and opportunity.get("name_zh")
    ]

    days = []
    for date in sorted(by_date)[:3]:
        items = sorted(by_date[date], key=lambda x: x.get("time_utc", ""))

        # Opportunity-first summaries are authoritative for researched Places.
        opportunity_summaries = {}
        for opportunity in researched:
            oid = opportunity["opportunity_id"]
            candidates = [
                (i, (_metric_for_opportunity(it, oid) or {}).get("score", -1))
                for i, it in enumerate(items)
                if (
                    (_metric_for_opportunity(it, oid) or {}).get("temporal_eligible") is not False
                    and it.get("access_open") is not False
                )
            ]
            candidates = [x for x in candidates if x[1] >= 0]
            if not candidates:
                continue
            best_idx, _ = max(candidates, key=lambda x: x[1])
            ws, we = _window_for_opportunity(items, best_idx, oid)
            opportunity_summaries[oid] = _compact_opportunity_snapshot(
                items[best_idx], opportunity, ws, we
            )

        # Keep Theme summaries for schema-9 backward compatibility only.
        theme_summaries = {}
        for theme in themes:
            candidates = [
                (i, (_metric_for_theme(it, theme) or {}).get("score", -1))
                for i, it in enumerate(items)
            ]
            candidates = [x for x in candidates if x[1] >= 0]
            if not candidates:
                continue
            best_idx, _ = max(candidates, key=lambda x: x[1])
            ws, we = _window_for_theme(items, best_idx, theme)
            theme_summaries[theme] = _compact_snapshot(items[best_idx], theme, ws, we)

        if opportunity_summaries:
            winner_id = max(opportunity_summaries, key=lambda oid: opportunity_summaries[oid]["score"])
            winner = dict(opportunity_summaries[winner_id])
            winner["research_pending"] = False
            winner["no_viable_opportunity"] = False
        elif researched:
            # Research exists, but every researched Opportunity is temporally
            # impossible in the remaining hours of this local day. Do not invent
            # a winner from the least-bad impossible timestamp.
            winner = {
                "theme": None,
                "score": None,
                "research_pending": False,
                "no_viable_opportunity": True,
                "status_key": "NO_VIABLE_OPPORTUNITY",
                "indicator_key": "NO_VIABLE_OPPORTUNITY",
                "factors": [],
            }
        else:
            # A Place without curated Photography Opportunities may keep legacy
            # Theme metrics for compatibility/weather inspection, but it must
            # not publish a photography recommendation score. Research first.
            winner = {
                "theme": None,
                "score": None,
                "research_pending": True,
                "no_viable_opportunity": False,
                "status_key": "OPPORTUNITY_DATA_INSUFFICIENT",
                "indicator_key": "OPPORTUNITY_DATA_INSUFFICIENT",
                "factors": [],
            }

        days.append({
            "date": date,
            "all": winner,
            "opportunities": opportunity_summaries,
            "themes": theme_summaries,
        })
    return days

def analyze_spot(spot, kp_rows=None):
    raw = fetch_weather_for_spot(spot, "zh-TW", kp_rows=kp_rows)
    if not isinstance(raw, dict) or not raw:
        return None, None

    common = {
        "spot_id": spot.get("spot_id"),
        "name_i18n": spot.get("name_i18n", {}),
        "name_local": spot.get("name_local", ""),
        "category": spot.get("category", ""),
        "scenes": spot.get("scenes", []),
        "themes": spot.get("themes", []),
        "opportunities": spot.get("opportunities", []),
        "product_status": spot.get("product_status", "keep"),
        "active_in_catalog": spot.get("active_in_catalog", True),
        "lat": spot.get("lat"),
        "lon": spot.get("lon"),
        "elevation": spot.get("elevation"),
        "api_elevation": raw.get("api_elevation"),
        "timezone": raw.get("timezone"),
        "timezone_abbr": raw.get("timezone_abbr"),
        "utc_offset_seconds": raw.get("utc_offset_seconds"),
        "view_azimuth": raw.get("view_azimuth", spot.get("view_azimuth")),
        "view_tolerance": raw.get("view_tolerance", spot.get("view_tolerance")),
        "access_mode": raw.get("access_mode", spot.get("access_mode")),
        "access_hours": spot.get("access_hours"),
        "access_hours_windows": spot.get("access_hours_windows"),
        "access_hours_source": spot.get("access_hours_source"),
        "access_note_i18n": spot.get("access_note_i18n"),
        "map_query": spot.get("map_query"),
        "coordinate_source": spot.get("coordinate_source"),
        "coordinate_confidence": spot.get("coordinate_confidence"),
        "bortle_class": spot.get("bortle_class"),
        "dark_sky_score": spot.get("dark_sky_score"),
        "light_pollution_source": spot.get("light_pollution_source"),
        "light_pollution_confidence": spot.get("light_pollution_confidence"),
    }
    hourly = raw.get("hourly_forecast", [])
    summary = dict(common)
    summary["daily"] = _build_day_summaries(hourly, spot.get("themes", []), spot.get("opportunities", []))

    details = dict(common)
    details["hourly_forecast"] = hourly
    return summary, details


def _active_spots(region):
    """Return only product-active Places; retired tombstones never reach output."""
    return [
        spot for spot in get_spots(region)
        if spot.get("active_in_catalog", True)
    ]


def _load_previous_spot_map(path):
    """Load the last committed weather rows for transient-failure fallback."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, json.JSONDecodeError, TypeError):
        return {}
    return {
        row.get("spot_id"): row
        for row in (payload.get("spots", []) or [])
        if isinstance(row, dict) and row.get("spot_id")
    }


def _mark_stale(row, reason):
    row = dict(row)
    row["data_stale"] = True
    row["data_stale_reason"] = reason
    return row


def main():
    region = sys.argv[1].lower() if len(sys.argv) > 1 else "tw"
    spots = _active_spots(region)
    if not spots:
        print(f"❌ 找不到區域 [{region}] 的景點清單！")
        raise SystemExit(1)

    kp_rows = fetch_noaa_kp_series()
    kp_info = fetch_noaa_kp()
    now_utc_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    summary_name = f"{region}_weather.json"
    details_name = f"{region}_weather_details.json"
    previous_summaries = _load_previous_spot_map(summary_name)
    previous_details = _load_previous_spot_map(details_name)

    summaries, details = [], []
    stale_spot_ids, failed_spot_ids = [], []
    for n, spot in enumerate(spots, 1):
        print(f"[{n}/{len(spots)}] {spot['name_i18n'].get('zh-TW')} ...")
        summary, detail = analyze_spot(spot, kp_rows=kp_rows)
        if summary:
            summary["data_stale"] = False
            detail["data_stale"] = False
            summaries.append(summary)
            details.append(detail)
            continue

        spot_id = spot.get("spot_id")
        previous_summary = previous_summaries.get(spot_id)
        previous_detail = previous_details.get(spot_id)
        if previous_summary and previous_detail:
            print(f"  ↳ using previous committed weather row for {spot_id}")
            summaries.append(_mark_stale(previous_summary, "weather_fetch_failed"))
            details.append(_mark_stale(previous_detail, "weather_fetch_failed"))
            stale_spot_ids.append(spot_id)
        else:
            failed_spot_ids.append(spot_id)

    if failed_spot_ids:
        raise RuntimeError(
            "Refusing to publish incomplete weather catalog; no fallback for active Places: "
            + ", ".join(failed_spot_ids)
        )
    if len(summaries) != len(spots) or len(details) != len(spots):
        raise RuntimeError(
            f"Weather catalog completeness regression: active={len(spots)} "
            f"summary={len(summaries)} details={len(details)}"
        )

    base_meta = {
        "schema_version": 9,
        "updated_at": now_utc_str,
        "region": region,
        "latest_kp": kp_info.get("kp_index") if kp_info else None,
        "latest_kp_source": kp_info.get("source") if kp_info else "unavailable",
        "total_spots": len(summaries),
        "stale_spot_count": len(stale_spot_ids),
        "stale_spot_ids": stale_spot_ids,
    }
    summary_data = {
        **base_meta,
        "translations": {"messages": I18N_MESSAGES, "factors": FACTOR_TEMPLATES},
        "spots": summaries,
    }
    detail_data = {**base_meta, "spots": details}

    with open(summary_name, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, separators=(",", ":"))
    with open(details_name, "w", encoding="utf-8") as f:
        json.dump(detail_data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"✅ {summary_name}: {len(summaries)} spots")
    print(f"✅ {details_name}: 96H details on demand")


if __name__ == "__main__":
    main()
