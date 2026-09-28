"""Authoritative Denali Mountain Vista / Park Road access provider for us-041.

The provider is intentionally fail-closed.

It reads the official Denali Current Conditions page, which NPS states
supersedes other trip-planning information. The provider only recognizes
explicit present-tense statements that the Park Road is open far enough to
reach Mountain Vista, or explicit present-tense closure at/before Park
Headquarters that blocks vehicle access to Mountain Vista.

Closures farther west (for example Pretty Rocks / Mile 43) do not block the
Mountain Vista Camera Zone at roughly Mile 13 and therefore must not be treated
as a closure of this Opportunity.

Both OPEN and CLOSED results are short-lived live snapshots. The generic
access-state freshness contract therefore prevents a current road state from
being extrapolated across the multi-day weather forecast.
"""

from __future__ import annotations

from html.parser import HTMLParser
import re
import time
import urllib.error
import urllib.request


PROVIDER_VERSION = "denali-mountain-vista-access-r1-preview"

AUTHORITY = "U.S. National Park Service"
CURRENT_CONDITIONS_URL = "https://www.nps.gov/dena/planyourvisit/conditions.htm"
SOURCE_KIND = "official_denali_current_park_road_conditions"


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


def _normalize(text):
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def parse_denali_current_conditions(html, fetched_at_epoch=None):
    """Parse the NPS Current Conditions page for Mountain Vista reachability.

    The parser deliberately ignores closures farther west than Mountain Vista.
    A broad "road closed at Mile 43" statement is not evidence that Mile 13 is
    inaccessible.

    If the page contains contradictory or insufficient present-tense access
    language, return UNKNOWN.
    """
    fetched_at_epoch = float(
        fetched_at_epoch if fetched_at_epoch is not None else time.time()
    )
    text = _normalize(_visible_text(html))

    has_denali = "denali" in text
    has_road = "park road" in text or "denali park road" in text
    has_mountain_vista = "mountain vista" in text
    has_context = has_denali and has_road and has_mountain_vista

    # Explicit current/open-to target statements that reach or pass Mile 13.
    open_patterns = (
        r"road is open.{0,180}to tek(?:lanika)?",
        r"road is open.{0,180}mile 30",
        r"road is open.{0,180}savage river",
        r"road is open.{0,180}mile 15",
        r"road is open.{0,180}mountain vista",
        r"road is open.{0,180}mile 13",
        r"road is open.{0,180}mile 12",
        r"open to private vehicles.{0,180}teklanika",
        r"open to private vehicles.{0,180}savage river",
        r"open to private vehicles.{0,180}mountain vista",
        r"personal vehicles.{0,180}drive to tek(?:lanika)?",
        r"personal vehicles.{0,180}drive to savage river",
        r"personal vehicles.{0,180}drive to mountain vista",
        r"private vehicles.{0,180}as far as tek(?:lanika)?",
        r"private vehicles.{0,180}as far as savage river",
        r"private vehicles.{0,180}as far as mountain vista",
    )

    # Explicit current closure at/before Park Headquarters blocks normal
    # vehicle access to Mountain Vista. "May close" is intentionally excluded.
    closed_patterns = (
        r"road is currently closed.{0,120}park headquarters",
        r"road is closed.{0,120}park headquarters",
        r"park road is currently closed.{0,120}mile 3(?:\.4)?",
        r"park road is closed.{0,120}mile 3(?:\.4)?",
        r"vehicle access is currently closed.{0,120}park headquarters",
        r"vehicle access is closed.{0,120}park headquarters",
        r"closed to vehicles.{0,120}park headquarters",
    )

    explicit_open = any(re.search(pattern, text) for pattern in open_patterns)
    explicit_closed = any(re.search(pattern, text) for pattern in closed_patterns)

    # A current-conditions page can mention an unrelated western closure, such
    # as Pretty Rocks at Mile 43. Record it for diagnostics only.
    western_closure = bool(
        re.search(r"(?:closed|closure).{0,120}mile (?:4[3-9]|[5-9]\d)", text)
        or re.search(r"mile (?:4[3-9]|[5-9]\d).{0,120}(?:closed|closure)", text)
    )

    if has_context and explicit_open and not explicit_closed:
        status = "open"
        status_basis = "official_nps_current_road_open_past_mountain_vista"
    elif has_context and explicit_closed and not explicit_open:
        status = "closed"
        status_basis = "official_nps_current_road_closed_before_mountain_vista"
    else:
        status = "unknown"
        status_basis = (
            "official_nps_current_conditions_conflicting"
            if explicit_open and explicit_closed
            else "official_nps_current_conditions_not_unambiguous"
        )

    parse_ok = has_context and status in {"open", "closed"}
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": CURRENT_CONDITIONS_URL,
        "source_kind": SOURCE_KIND,
        "fetched_at_epoch": fetched_at_epoch,
        "checked_at_epoch": fetched_at_epoch if parse_ok else None,
        "status": status,
        "status_basis": status_basis,
        "parse_ok": parse_ok,
        "has_context": has_context,
        "explicit_open": explicit_open,
        "explicit_closed": explicit_closed,
        "western_closure_present": western_closure,
    }


def unknown_denali_provider_state(
    reason="provider_unavailable",
    fetched_at_epoch=None,
):
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": CURRENT_CONDITIONS_URL,
        "source_kind": SOURCE_KIND,
        "fetched_at_epoch": float(
            fetched_at_epoch if fetched_at_epoch is not None else time.time()
        ),
        "checked_at_epoch": None,
        "status": "unknown",
        "status_basis": "provider_unavailable",
        "parse_ok": False,
        "provider_reason": reason,
    }


def fetch_denali_current_conditions(timeout=12, attempts=2):
    """Fetch the official Denali Current Conditions page with bounded retries."""
    req = urllib.request.Request(
        CURRENT_CONDITIONS_URL,
        headers={"User-Agent": "ChaseLights/2.0 (+weather photography)"},
    )
    last_error = None
    for attempt in range(max(1, int(attempts))):
        fetched_at_epoch = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                html = response.read().decode(charset, errors="replace")
            return parse_denali_current_conditions(
                html,
                fetched_at_epoch=fetched_at_epoch,
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as exc:
            last_error = exc
        if attempt + 1 < max(1, int(attempts)):
            time.sleep(1.0 * (attempt + 1))

    return unknown_denali_provider_state(
        reason=(
            f"fetch_failed:{type(last_error).__name__}"
            if last_error
            else "fetch_failed"
        )
    )


def _snapshot(provider_state):
    provider_state = (
        provider_state
        if isinstance(provider_state, dict)
        else unknown_denali_provider_state()
    )
    status = str(provider_state.get("status") or "unknown").lower()
    parse_ok = provider_state.get("parse_ok") is True

    if not parse_ok or status not in {"open", "closed"}:
        return {
            "status": "unknown",
            "authoritative": True,
            "authority": provider_state.get("authority", AUTHORITY),
            "source_url": provider_state.get(
                "source_url", CURRENT_CONDITIONS_URL
            ),
            "source_kind": provider_state.get("source_kind", SOURCE_KIND),
            "freshness_mode": "live",
            "checked_at_epoch": None,
            "status_basis": provider_state.get(
                "status_basis", "provider_status_unknown"
            ),
            "provider_version": provider_state.get(
                "provider_version", PROVIDER_VERSION
            ),
            "provider_parse_ok": False,
        }

    return {
        "status": status,
        "authoritative": True,
        "authority": provider_state.get("authority", AUTHORITY),
        "source_url": provider_state.get(
            "source_url", CURRENT_CONDITIONS_URL
        ),
        "source_kind": provider_state.get("source_kind", SOURCE_KIND),
        "freshness_mode": "live",
        "checked_at_epoch": provider_state.get("checked_at_epoch"),
        "status_basis": provider_state.get("status_basis"),
        "provider_version": provider_state.get("provider_version", PROVIDER_VERSION),
        "provider_parse_ok": True,
        "western_closure_present": provider_state.get("western_closure_present"),
    }


def build_denali_mountain_vista_access_state(timestamp, provider_state=None):
    """Return Opportunity-keyed Mountain Vista access snapshots."""
    _ = timestamp
    snapshot = _snapshot(provider_state)
    return {
        "us-041-P01": dict(snapshot),
        "us-041-P02": dict(snapshot),
    }
