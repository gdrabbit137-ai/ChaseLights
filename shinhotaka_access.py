"""Authoritative Shinhotaka Ropeway access provider for jp-021.

This module is deliberately fail-closed.  Static official schedules can prove
that access is closed, but a published timetable alone can never prove that the
ropeway is actually operating.  Live "open" decisions require a fresh official
operation-status snapshot.

The 2026 Stargazing Service dates are year-specific and must never be projected
into a later year.
"""

from datetime import datetime, time as dt_time, timedelta, timezone
from html.parser import HTMLParser
import re
import time
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo


PROVIDER_VERSION = "shinhotaka-access-r1-preview"

AUTHORITY = "Shinhotaka Ropeway"
HOME_URL = "https://shinhotaka-ropeway.jp/en/"
TIMETABLE_URL = "https://shinhotaka-ropeway.jp/pdf/pamphlet/en.pdf"
MAINTENANCE_URL = (
    "https://shinhotaka-ropeway.jp/"
    "%E3%80%902026%E5%B9%B4%E5%BA%A6%E3%80%91"
    "%E6%96%B0%E7%A9%82%E9%AB%98%E3%83%AD%E3%83%BC%E3%83%97%E3%82%A6%E3%82%A7%E3%82%A4"
    "%E3%81%AE%E9%81%8B%E8%A1%8C%E8%A8%88%E7%94%BB%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/"
)
STARGAZING_URL = (
    "https://shinhotaka-ropeway.jp/en/"
    "2025%E5%B9%B4%E5%BA%A6%E3%81%AE%E6%98%9F%E7%A9%BA%E8%A6%B3%E8%B3%9E%E4%BE%BF"
    "%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/"
)

JST = ZoneInfo("Asia/Tokyo")
LIVE_MAX_AGE_SECONDS = 6 * 3600

# Officially published 2026 full-line closure periods.
MAINTENANCE_CLOSURES_2026 = (
    ((2026, 6, 15), (2026, 6, 26)),
    ((2026, 11, 24), (2026, 11, 27)),
)

# Official 2026 Stargazing Service dates.  These are intentionally not inferred
# for any other year.
STARGAZING_DATES_2026 = frozenset({
    (2026, 5, 3), (2026, 5, 4), (2026, 5, 5),
    (2026, 10, 2), (2026, 10, 3), (2026, 10, 4),
    (2026, 10, 9), (2026, 10, 10), (2026, 10, 11), (2026, 10, 12),
    (2026, 10, 30), (2026, 10, 31),
    (2026, 11, 1), (2026, 11, 2), (2026, 11, 3),
    (2026, 11, 6), (2026, 11, 7), (2026, 11, 8),
})

# The English timetable states 08:15 on October Saturdays, Sundays and holidays.
# 2026 Sports Day is explicitly curated here; future-year holiday dates are not
# guessed by this provider.
OCTOBER_HOLIDAYS_2026 = frozenset({(2026, 10, 12)})


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


def _operation_window(text):
    lower = text.lower()
    starts = [
        pos for marker in ("operation status", "運行状況", "運行情報")
        if (pos := lower.find(marker.lower())) >= 0
    ]
    if not starts:
        return text[:8000]
    start = min(starts)
    # Include some preceding text because the visible "MM/DD HH:MM update" can
    # be placed immediately above the status heading.
    return text[max(0, start - 600): start + 5000]


def _parse_visible_update(text, fetched_at_epoch):
    segment = _operation_window(text)
    patterns = (
        r"(?P<m>\d{1,2})\s*/\s*(?P<d>\d{1,2}).{0,160}?"
        r"(?P<h>\d{1,2}):(?P<min>\d{2})\s*(?:update|updated|更新)",
        r"(?P<m>\d{1,2})\s*月\s*(?P<d>\d{1,2})\s*日.{0,160}?"
        r"(?P<h>\d{1,2}):(?P<min>\d{2})\s*(?:update|updated|更新)",
    )
    match = None
    for pattern in patterns:
        match = re.search(pattern, segment, flags=re.IGNORECASE | re.DOTALL)
        if match:
            break
    if not match:
        return None, None

    try:
        fetched_local = datetime.fromtimestamp(float(fetched_at_epoch), timezone.utc).astimezone(JST)
        month = int(match.group("m"))
        day = int(match.group("d"))
        hour = int(match.group("h"))
        minute = int(match.group("min"))
        candidates = []
        for year in (fetched_local.year - 1, fetched_local.year, fetched_local.year + 1):
            try:
                candidates.append(datetime(year, month, day, hour, minute, tzinfo=JST))
            except ValueError:
                pass
        if not candidates:
            return None, None
        chosen = min(candidates, key=lambda dt: abs((dt - fetched_local).total_seconds()))
        return chosen.timestamp(), match.group(0)
    except (TypeError, ValueError, OverflowError):
        return None, None


def _ropeway_section(text, number):
    markers = {
        1: (r"no\.?\s*1\s*ropeway", r"第\s*1\s*ロープウェイ"),
        2: (r"no\.?\s*2\s*ropeway", r"第\s*2\s*ロープウェイ"),
    }
    own = []
    for pattern in markers[number]:
        found = re.search(pattern, text, flags=re.IGNORECASE)
        if found:
            own.append(found)
    if not own:
        return None
    start_match = min(own, key=lambda m: m.start())
    start = start_match.start()
    end = min(len(text), start + 900)
    for other_number, other_patterns in markers.items():
        if other_number == number:
            continue
        for pattern in other_patterns:
            found = re.search(pattern, text[start_match.end():], flags=re.IGNORECASE)
            if found:
                end = min(end, start_match.end() + found.start())
    return text[start:end]


def _status_from_section(section):
    if not section:
        return "unknown"
    value = re.sub(r"\s+", " ", section).lower()

    closed_tokens = (
        "suspended", "suspension", "closed", "not operating", "operation ended",
        "out of service", "運休", "休止", "停止", "営業終了", "運行終了",
    )
    restricted_tokens = ("restricted", "limited service", "一部運休", "一部運行")
    open_tokens = ("open", "operating", "in operation", "normal operation", "運行中", "通常運行")

    if any(token in value for token in closed_tokens):
        return "closed"
    if any(token in value for token in restricted_tokens):
        return "restricted"
    if any(token in value for token in open_tokens):
        return "open"
    return "unknown"


def parse_shinhotaka_homepage_status(html, fetched_at_epoch=None):
    """Parse official No.1/No.2 operation status and visible update time."""
    fetched_at_epoch = float(fetched_at_epoch if fetched_at_epoch is not None else time.time())
    text = _visible_text(html)
    segment = _operation_window(text)
    checked_at_epoch, visible_update_text = _parse_visible_update(text, fetched_at_epoch)
    no1 = _status_from_section(_ropeway_section(segment, 1))
    no2 = _status_from_section(_ropeway_section(segment, 2))
    parse_ok = checked_at_epoch is not None and no1 != "unknown" and no2 != "unknown"
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": HOME_URL,
        "source_kind": "official_ropeway_operation_status",
        "fetched_at_epoch": fetched_at_epoch,
        "checked_at_epoch": checked_at_epoch,
        "visible_update_text": visible_update_text,
        "no1_status": no1,
        "no2_status": no2,
        "parse_ok": parse_ok,
    }


def unknown_shinhotaka_provider_state(reason="provider_unavailable", fetched_at_epoch=None):
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": HOME_URL,
        "source_kind": "official_ropeway_operation_status",
        "fetched_at_epoch": float(fetched_at_epoch if fetched_at_epoch is not None else time.time()),
        "checked_at_epoch": None,
        "visible_update_text": None,
        "no1_status": "unknown",
        "no2_status": "unknown",
        "parse_ok": False,
        "provider_reason": reason,
    }


def fetch_shinhotaka_homepage_status(timeout=12, attempts=2):
    """Fetch the official public homepage with bounded retries."""
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
            return parse_shinhotaka_homepage_status(html, fetched_at_epoch=fetched_at_epoch)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt + 1 < max(1, int(attempts)):
            time.sleep(1.0 * (attempt + 1))
    return unknown_shinhotaka_provider_state(
        reason=f"fetch_failed:{type(last_error).__name__}" if last_error else "fetch_failed"
    )


def _inside_maintenance(local_dt):
    current = (local_dt.year, local_dt.month, local_dt.day)
    return any(start <= current <= end for start, end in MAINTENANCE_CLOSURES_2026)


def _p01_window(local_dt):
    """Return official regular summit-access window in JST, or None if unknown."""
    md = (local_dt.month, local_dt.day)
    date_key = (local_dt.year, local_dt.month, local_dt.day)

    if (4, 1) <= md <= (11, 30):
        first = dt_time(8, 45)
        if local_dt.month == 8:
            first = dt_time(8, 15)
        elif local_dt.month == 10 and (
            local_dt.weekday() >= 5 or date_key in OCTOBER_HOLIDAYS_2026
        ):
            first = dt_time(8, 15)
        return first, dt_time(16, 45)

    if md >= (12, 1) or md <= (3, 31):
        return dt_time(9, 15), dt_time(16, 15)

    return None


def _time_in_window(local_dt, start_time, end_time):
    current = local_dt.timetz().replace(tzinfo=None)
    return start_time <= current <= end_time


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
    provider_state = provider_state or unknown_shinhotaka_provider_state()
    snapshot = {
        "status": status,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": HOME_URL,
        "source_kind": "official_ropeway_operation_status",
        "freshness_mode": "live",
        "status_basis": basis,
        "checked_at_epoch": provider_state.get("checked_at_epoch"),
        "visible_update_text": provider_state.get("visible_update_text"),
        "provider_version": provider_state.get("provider_version", PROVIDER_VERSION),
        "no1_status": provider_state.get("no1_status", "unknown"),
        "no2_status": provider_state.get("no2_status", "unknown"),
        "provider_parse_ok": provider_state.get("parse_ok", False),
    }
    snapshot.update(extra)
    return snapshot


def _p01_snapshot(local_dt, provider_state):
    if _inside_maintenance(local_dt):
        return _schedule_snapshot(
            "closed", MAINTENANCE_URL, "official_maintenance_schedule",
            "official_2026_full_line_maintenance_closure",
        )

    window = _p01_window(local_dt)
    if window is None:
        return _schedule_snapshot(
            "unknown", TIMETABLE_URL, "official_ropeway_timetable",
            "regular_timetable_not_resolved",
        )
    first, last = window
    if not _time_in_window(local_dt, first, last):
        return _schedule_snapshot(
            "closed", TIMETABLE_URL, "official_ropeway_timetable",
            "outside_regular_ropeway_access_window",
            timetable_first_ascent=first.strftime("%H:%M"),
            timetable_last_descent=last.strftime("%H:%M"),
        )

    provider_state = provider_state or unknown_shinhotaka_provider_state()
    no1 = provider_state.get("no1_status", "unknown")
    no2 = provider_state.get("no2_status", "unknown")
    if no1 == "open" and no2 == "open" and provider_state.get("parse_ok"):
        status = "open"
        basis = "fresh_live_no1_and_no2_open_required"
    elif no1 in {"closed", "restricted"} or no2 in {"closed", "restricted"}:
        status = "closed" if "closed" in {no1, no2} else "restricted"
        basis = "live_required_ropeway_not_fully_open"
    else:
        status = "unknown"
        basis = "live_required_ropeway_status_unknown"
    return _live_snapshot(
        status, provider_state, basis,
        timetable_first_ascent=first.strftime("%H:%M"),
        timetable_last_descent=last.strftime("%H:%M"),
    )


def _event_date_known(local_dt):
    return local_dt.year == 2026


def _p02_snapshot(local_dt, provider_state):
    if _inside_maintenance(local_dt):
        return _schedule_snapshot(
            "closed", MAINTENANCE_URL, "official_maintenance_schedule",
            "official_2026_full_line_maintenance_closure",
        )

    date_key = (local_dt.year, local_dt.month, local_dt.day)
    if not _event_date_known(local_dt):
        return _schedule_snapshot(
            "unknown", STARGAZING_URL, "official_annual_stargazing_schedule",
            "stargazing_schedule_not_verified_for_year",
            schedule_year_verified=2026,
        )

    if date_key not in STARGAZING_DATES_2026:
        return _schedule_snapshot(
            "closed", STARGAZING_URL, "official_annual_stargazing_schedule",
            "not_an_official_2026_stargazing_service_date",
            schedule_year_verified=2026,
        )

    event_start = dt_time(18, 0)
    event_end = dt_time(21, 0)
    if not _time_in_window(local_dt, event_start, event_end):
        return _schedule_snapshot(
            "closed", STARGAZING_URL, "official_annual_stargazing_schedule",
            "outside_official_stargazing_service_window",
            event_first_ascent="18:00",
            event_last_ascent="20:20",
            event_last_descent="21:00",
        )

    provider_state = provider_state or unknown_shinhotaka_provider_state()
    checked = provider_state.get("checked_at_epoch")
    checked_local = None
    try:
        if checked is not None:
            checked_local = datetime.fromtimestamp(float(checked), timezone.utc).astimezone(JST)
    except (TypeError, ValueError, OverflowError):
        checked_local = None

    # A daytime operation-status update cannot prove that the special night
    # service is actually operating.  Require an official status update from
    # the same event date and within the event service window.
    update_in_event = bool(
        checked_local
        and checked_local.date() == local_dt.date()
        and _time_in_window(checked_local, event_start, event_end)
    )
    no2 = provider_state.get("no2_status", "unknown")
    if update_in_event and provider_state.get("parse_ok") and no2 == "open":
        status = "open"
        basis = "official_event_date_and_live_no2_night_status_open"
    elif update_in_event and no2 in {"closed", "restricted"}:
        status = "closed" if no2 == "closed" else "restricted"
        basis = "official_event_date_but_live_no2_not_open"
    else:
        status = "unknown"
        basis = "event_date_requires_same_window_live_no2_confirmation"

    return _live_snapshot(
        status, provider_state, basis,
        event_first_ascent="18:00",
        event_last_ascent="20:20",
        event_last_descent="21:00",
        schedule_year_verified=2026,
    )


def build_shinhotaka_access_state(timestamp, provider_state=None):
    """Build per-Opportunity authoritative access snapshots for jp-021."""
    try:
        local_dt = datetime.fromtimestamp(float(timestamp), timezone.utc).astimezone(JST)
    except (TypeError, ValueError, OverflowError):
        unknown = _schedule_snapshot(
            "unknown", HOME_URL, "official_ropeway_operation_status",
            "evaluation_timestamp_invalid",
        )
        return {"jp-021-P01": dict(unknown), "jp-021-P02": dict(unknown)}

    return {
        "jp-021-P01": _p01_snapshot(local_dt, provider_state),
        "jp-021-P02": _p02_snapshot(local_dt, provider_state),
    }
