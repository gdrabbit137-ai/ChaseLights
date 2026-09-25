"""Authoritative Yahikoyama Ropeway access provider for jp-022.

The provider is deliberately fail-closed:
- the official ropeway homepage can prove live ropeway operation;
- static published schedules can prove that an Opportunity is closed;
- the Yahikoyama Skyline seasonal schedule alone never proves that the road is
  actually open, because temporary closures are possible;
- the 2026 Night View & Stargazing Cruise schedule is year-specific and is not
  projected into future years.
"""

from datetime import datetime, time as dt_time, timezone
from html.parser import HTMLParser
import re
import time
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo


PROVIDER_VERSION = "yahiko-access-r1-preview"

AUTHORITY = "Yahikoyama Ropeway"
HOME_URL = "https://yahikoyama-ropeway.jp/"
TOURISM_ROPEWAY_URL = "https://niigata-kankou.or.jp/spot/7484"
SKYLINE_URL = "https://niigata-kankou.or.jp/spot/7478"

JST = ZoneInfo("Asia/Tokyo")

NIGHT_CRUISE_DATES_2026 = frozenset({
    (2026, 8, 11), (2026, 8, 12),
    (2026, 8, 14), (2026, 8, 15), (2026, 8, 16),
    (2026, 9, 19), (2026, 9, 20), (2026, 9, 21),
    (2026, 9, 22), (2026, 9, 23),
})


class _VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        value = re.sub(r"\s+", " ", str(data or "")).strip()
        if value:
            self.parts.append(value)

    def text(self):
        return "\n".join(self.parts)


def _visible_text(html):
    parser = _VisibleTextParser()
    parser.feed(str(html or ""))
    return parser.text()


def _today_section(text):
    marker = "本日のロープウェイ情報"
    pos = text.find(marker)
    if pos < 0:
        return text[:5000]
    return text[pos:pos + 3500]


def _parse_clock_after(section, labels):
    for label in labels:
        pos = section.find(label)
        if pos < 0:
            continue
        tail = section[pos:pos + 240]
        match = re.search(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)", tail)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return dt_time(hour, minute)
    return None


def _status_from_section(section):
    normalized = re.sub(r"\s+", "", section)
    closed_tokens = ("運休", "休止", "営業休止", "運転休止", "本日休業", "休業")
    restricted_tokens = ("見合わせ", "一時停止", "減速運転", "変更運行")
    open_tokens = ("通常営業", "通常運行", "運行中", "営業中")

    if any(token in normalized for token in closed_tokens):
        return "closed"
    if any(token in normalized for token in restricted_tokens):
        return "restricted"
    if any(token in normalized for token in open_tokens):
        return "open"
    return "unknown"


def parse_yahiko_homepage_status(html, fetched_at_epoch=None):
    """Parse today's official ropeway operation state and published service times."""
    fetched_at_epoch = float(fetched_at_epoch if fetched_at_epoch is not None else time.time())
    text = _visible_text(html)
    section = _today_section(text)

    first_ascent = _parse_clock_after(section, ("始 発", "始発"))
    last_ascent = _parse_clock_after(section, ("上り 最終", "上り最終", "上り"))
    last_descent = _parse_clock_after(section, ("下り 最終", "下り最終", "下り"))
    status = _status_from_section(section)

    # The page explicitly labels this block as today's information.  A fetch of
    # that authoritative page is therefore the live snapshot time.
    has_today_block = "本日のロープウェイ情報" in text
    parse_ok = bool(
        has_today_block
        and status != "unknown"
        and first_ascent is not None
        and last_ascent is not None
        and last_descent is not None
    )

    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": HOME_URL,
        "source_kind": "official_ropeway_today_status",
        "fetched_at_epoch": fetched_at_epoch,
        "checked_at_epoch": fetched_at_epoch if parse_ok else None,
        "visible_update_text": "本日のロープウェイ情報" if has_today_block else None,
        "status": status,
        "first_ascent": first_ascent.strftime("%H:%M") if first_ascent else None,
        "last_ascent": last_ascent.strftime("%H:%M") if last_ascent else None,
        "last_descent": last_descent.strftime("%H:%M") if last_descent else None,
        "parse_ok": parse_ok,
    }


def unknown_yahiko_provider_state(reason="provider_unavailable", fetched_at_epoch=None):
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": HOME_URL,
        "source_kind": "official_ropeway_today_status",
        "fetched_at_epoch": float(fetched_at_epoch if fetched_at_epoch is not None else time.time()),
        "checked_at_epoch": None,
        "visible_update_text": None,
        "status": "unknown",
        "first_ascent": None,
        "last_ascent": None,
        "last_descent": None,
        "parse_ok": False,
        "provider_reason": reason,
    }


def fetch_yahiko_homepage_status(timeout=12, attempts=2):
    req = urllib.request.Request(
        HOME_URL,
        headers={"User-Agent": "ChaseLights/2.0 (+weather photography)"},
    )
    last_error = None
    for attempt in range(max(1, int(attempts))):
        fetched_at_epoch = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                html = response.read().decode(charset, errors="replace")
            return parse_yahiko_homepage_status(html, fetched_at_epoch=fetched_at_epoch)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt + 1 < max(1, int(attempts)):
            time.sleep(1.0 * (attempt + 1))
    return unknown_yahiko_provider_state(
        reason=f"fetch_failed:{type(last_error).__name__}" if last_error else "fetch_failed"
    )


def _clock(value):
    try:
        hour, minute = str(value).split(":", 1)
        return dt_time(int(hour), int(minute))
    except (TypeError, ValueError):
        return None


def _time_in_window(local_dt, start, end):
    current = local_dt.timetz().replace(tzinfo=None)
    return start <= current <= end


def _schedule_snapshot(status, source_url, source_kind, basis, **extra):
    snapshot = {
        "status": status,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": source_url,
        "source_kind": source_kind,
        "freshness_mode": "schedule",
        "status_basis": basis,
    }
    snapshot.update(extra)
    return snapshot


def _live_snapshot(status, provider_state, basis, **extra):
    provider_state = provider_state or unknown_yahiko_provider_state()
    snapshot = {
        "status": status,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": HOME_URL,
        "source_kind": "official_ropeway_today_status",
        "freshness_mode": "live",
        "status_basis": basis,
        "checked_at_epoch": provider_state.get("checked_at_epoch"),
        "visible_update_text": provider_state.get("visible_update_text"),
        "provider_version": provider_state.get("provider_version", PROVIDER_VERSION),
        "ropeway_status": provider_state.get("status", "unknown"),
        "provider_parse_ok": provider_state.get("parse_ok", False),
    }
    snapshot.update(extra)
    return snapshot


def _regular_ropeway_snapshot(local_dt, provider_state):
    provider_state = provider_state or unknown_yahiko_provider_state()
    first = _clock(provider_state.get("first_ascent"))
    last_down = _clock(provider_state.get("last_descent"))

    if not provider_state.get("parse_ok") or first is None or last_down is None:
        return _live_snapshot(
            "unknown", provider_state, "live_ropeway_status_or_timetable_unknown"
        )

    if not _time_in_window(local_dt, first, last_down):
        # Ropeway is closed for this timestamp.  The Skyline may provide another
        # route Apr-Nov, but its published hours alone are not live closure proof.
        return _schedule_snapshot(
            "unknown", SKYLINE_URL, "official_skyline_seasonal_schedule",
            "ropeway_outside_window_and_skyline_live_status_unavailable",
            ropeway_first_ascent=first.strftime("%H:%M"),
            ropeway_last_descent=last_down.strftime("%H:%M"),
        )

    status = provider_state.get("status", "unknown")
    if status == "open":
        basis = "fresh_official_ropeway_today_status_open"
    elif status in {"closed", "restricted"}:
        basis = "fresh_official_ropeway_today_status_not_open"
    else:
        basis = "fresh_official_ropeway_today_status_unknown"
    return _live_snapshot(
        status, provider_state, basis,
        ropeway_first_ascent=first.strftime("%H:%M"),
        ropeway_last_descent=last_down.strftime("%H:%M"),
    )


def _night_cruise_snapshot(local_dt, provider_state):
    if local_dt.year != 2026:
        return _schedule_snapshot(
            "unknown", TOURISM_ROPEWAY_URL, "official_annual_night_cruise_schedule",
            "night_cruise_schedule_not_verified_for_year",
            schedule_year_verified=2026,
        )

    date_key = (local_dt.year, local_dt.month, local_dt.day)
    if date_key not in NIGHT_CRUISE_DATES_2026:
        return _schedule_snapshot(
            "closed", TOURISM_ROPEWAY_URL, "official_annual_night_cruise_schedule",
            "not_an_official_2026_night_cruise_date",
            schedule_year_verified=2026,
        )

    event_start = dt_time(18, 0)
    event_end = dt_time(21, 0)
    if not _time_in_window(local_dt, event_start, event_end):
        return _schedule_snapshot(
            "closed", TOURISM_ROPEWAY_URL, "official_annual_night_cruise_schedule",
            "outside_official_2026_night_cruise_window",
            event_first_ascent="18:00",
            event_last_ascent="20:30",
            event_last_descent="21:00",
            schedule_year_verified=2026,
        )

    provider_state = provider_state or unknown_yahiko_provider_state()
    last_down = _clock(provider_state.get("last_descent"))
    live_confirms_night_service = bool(
        provider_state.get("parse_ok")
        and provider_state.get("status") == "open"
        and last_down is not None
        and last_down >= event_end
    )
    if live_confirms_night_service:
        status = "open"
        basis = "official_event_date_and_live_ropeway_night_service_open"
    elif provider_state.get("parse_ok") and provider_state.get("status") in {"closed", "restricted"}:
        status = provider_state.get("status")
        basis = "official_event_date_but_live_ropeway_not_open"
    else:
        status = "unknown"
        basis = "event_date_requires_live_night_service_confirmation"

    return _live_snapshot(
        status, provider_state, basis,
        event_first_ascent="18:00",
        event_last_ascent="20:30",
        event_last_descent="21:00",
        schedule_year_verified=2026,
    )


def build_yahiko_access_state(timestamp, provider_state=None):
    """Build authoritative per-Opportunity access snapshots for jp-022."""
    try:
        local_dt = datetime.fromtimestamp(float(timestamp), timezone.utc).astimezone(JST)
    except (TypeError, ValueError, OverflowError):
        unknown = _schedule_snapshot(
            "unknown", HOME_URL, "official_ropeway_today_status",
            "evaluation_timestamp_invalid",
        )
        return {
            "jp-022-P01": dict(unknown),
            "jp-022-P02": dict(unknown),
            "jp-022-P03": dict(unknown),
        }

    regular = _regular_ropeway_snapshot(local_dt, provider_state)
    return {
        "jp-022-P01": dict(regular),
        "jp-022-P02": dict(regular),
        "jp-022-P03": _night_cruise_snapshot(local_dt, provider_state),
    }
