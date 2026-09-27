"""Authoritative Mount Rainier road-access provider for us-012.

The provider is deliberately profile-specific and fail-closed:
- us-012-P01 Reflection Lakes depends on current Stevens Canyon Road vehicle access.
- us-012-P02 Tipsoo Lake depends on current SR 410 / Chinook Pass vehicle access.

NPS states that its Road Status report is updated when road status changes.
A fresh fetch of that explicit current-status page can therefore serve as a
live snapshot even when the visible report date itself is older than six hours.

The parser never treats season/month or favorable weather as proof of access.
Unknown markup, missing route rows, ambiguous status, or fetch failure yields
unknown and is rejected by the canonical dynamic-access evaluator.
"""

from datetime import datetime
from html.parser import HTMLParser
import re
import time
import urllib.error
import urllib.request


PROVIDER_VERSION = "mount-rainier-access-r1-preview"
AUTHORITY = "U.S. National Park Service"
ROAD_STATUS_URL = "https://www.nps.gov/mora/planyourvisit/road-status.htm"

PROFILE_ROUTES = {
    "us-012-P01": {
        "route_key": "stevens_canyon",
        "route_label": "Stevens Canyon Road",
    },
    "us-012-P02": {
        "route_key": "chinook_pass",
        "route_label": "SR 410 (Chinook Pass)",
    },
}


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


def _report_date(text):
    match = re.search(
        r"Road\s+Status\s*[-–—]\s*Updated\s+"
        r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    try:
        return datetime.strptime(
            f"{match.group(1)} {match.group(2)}, {match.group(3)}",
            "%B %d, %Y",
        ).date().isoformat()
    except ValueError:
        return None


def _first_status_after(text, marker, max_chars=600):
    lower = text.lower()
    pos = lower.find(marker.lower())
    if pos < 0:
        return "unknown", None
    segment = text[pos:pos + max_chars]
    match = re.search(r"\b(OPEN|CLOSED)\b", segment, flags=re.IGNORECASE)
    if not match:
        return "unknown", segment
    return match.group(1).lower(), segment


def parse_mount_rainier_road_status(html, fetched_at_epoch=None):
    """Parse the official NPS Road Status report for the two us-012 routes."""
    fetched_at_epoch = float(
        fetched_at_epoch if fetched_at_epoch is not None else time.time()
    )
    text = _visible_text(html)

    current_report_marker = bool(
        re.search(
            r"report\s+is\s+updated\s+when\s+road\s+status\s+changes",
            text,
            flags=re.IGNORECASE,
        )
    )
    report_updated_date = _report_date(text)

    stevens_status, stevens_segment = _first_status_after(
        text, "Stevens Canyon Road", max_chars=500
    )
    chinook_status, chinook_segment = _first_status_after(
        text, "SR 410 (Chinook Pass)", max_chars=650
    )

    parse_ok = bool(
        current_report_marker
        and report_updated_date
        and stevens_status in {"open", "closed"}
        and chinook_status in {"open", "closed"}
    )

    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": ROAD_STATUS_URL,
        "source_kind": "official_nps_current_road_status",
        "fetched_at_epoch": fetched_at_epoch,
        # NPS labels this as a current report that is updated when status
        # changes, so a successful current fetch is the live snapshot time.
        "checked_at_epoch": fetched_at_epoch if parse_ok else None,
        "report_updated_date": report_updated_date,
        "current_report_marker": current_report_marker,
        "stevens_canyon_status": stevens_status,
        "chinook_pass_status": chinook_status,
        "parse_ok": parse_ok,
        "stevens_segment": stevens_segment,
        "chinook_segment": chinook_segment,
    }


def unknown_mount_rainier_provider_state(
    reason="provider_unavailable", fetched_at_epoch=None
):
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": ROAD_STATUS_URL,
        "source_kind": "official_nps_current_road_status",
        "fetched_at_epoch": float(
            fetched_at_epoch if fetched_at_epoch is not None else time.time()
        ),
        "checked_at_epoch": None,
        "report_updated_date": None,
        "current_report_marker": False,
        "stevens_canyon_status": "unknown",
        "chinook_pass_status": "unknown",
        "parse_ok": False,
        "provider_reason": reason,
    }


def fetch_mount_rainier_road_status(timeout=12, attempts=2):
    """Fetch the official NPS road-status page with bounded retries."""
    req = urllib.request.Request(
        ROAD_STATUS_URL,
        headers={"User-Agent": "ChaseLights/2.0 (+weather photography)"},
    )
    last_error = None
    for attempt in range(max(1, int(attempts))):
        fetched_at_epoch = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                html = response.read().decode(charset, errors="replace")
            return parse_mount_rainier_road_status(
                html, fetched_at_epoch=fetched_at_epoch
            )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
        if attempt + 1 < max(1, int(attempts)):
            time.sleep(1.0 * (attempt + 1))

    return unknown_mount_rainier_provider_state(
        reason=(
            f"fetch_failed:{type(last_error).__name__}"
            if last_error
            else "fetch_failed"
        )
    )


def _snapshot(status, provider_state, route_key, route_label):
    provider_state = provider_state or unknown_mount_rainier_provider_state()
    parse_ok = bool(provider_state.get("parse_ok"))
    if not parse_ok:
        status = "unknown"
        basis = "official_road_status_parse_or_fetch_unavailable"
    elif status == "open":
        basis = f"official_current_{route_key}_open"
    elif status == "closed":
        basis = f"official_current_{route_key}_closed"
    else:
        status = "unknown"
        basis = f"official_current_{route_key}_status_unknown"

    return {
        "status": status,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": ROAD_STATUS_URL,
        "source_kind": "official_nps_current_road_status",
        "freshness_mode": "live",
        "status_basis": basis,
        "checked_at_epoch": provider_state.get("checked_at_epoch"),
        "provider_version": provider_state.get("provider_version", PROVIDER_VERSION),
        "provider_parse_ok": parse_ok,
        "report_updated_date": provider_state.get("report_updated_date"),
        "route_key": route_key,
        "route_label": route_label,
    }


def build_mount_rainier_access_state(timestamp, provider_state=None):
    """Build authoritative per-Opportunity road snapshots for us-012.

    timestamp is accepted to match the other access-provider interfaces.
    Freshness against each hourly target is enforced centrally by access_state.
    """
    _ = timestamp
    provider_state = provider_state or unknown_mount_rainier_provider_state()
    return {
        "us-012-P01": _snapshot(
            provider_state.get("stevens_canyon_status", "unknown"),
            provider_state,
            "stevens_canyon",
            "Stevens Canyon Road",
        ),
        "us-012-P02": _snapshot(
            provider_state.get("chinook_pass_status", "unknown"),
            provider_state,
            "chinook_pass",
            "SR 410 (Chinook Pass)",
        ),
    }


def validate_mount_rainier_provider():
    errors = []
    if set(PROFILE_ROUTES) != {"us-012-P01", "us-012-P02"}:
        errors.append("unexpected Mount Rainier access profile registry")
    for oid, config in PROFILE_ROUTES.items():
        if not config.get("route_key") or not config.get("route_label"):
            errors.append(f"{oid}: route metadata missing")
    return errors


_ERRORS = validate_mount_rainier_provider()
if _ERRORS:
    raise ValueError("Invalid Mount Rainier access provider: " + "; ".join(_ERRORS))
