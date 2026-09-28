"""Authoritative Johnston Ridge / SR 504 access provider for us-017.

The provider is intentionally fail-closed.

Current closure can be proven from the official WSDOT project page. A future
"open" result requires explicit present-tense reopening language; historical
project narrative, construction completion targets, or favorable weather never
prove that the Johnston Ridge Camera Zone is publicly reachable.

A parsed long-term closure is emitted as a schedule-style CLOSED snapshot so it
can safely cover the forecast horizon. A parsed reopening is emitted as a
short-lived LIVE snapshot and therefore requires fresh confirmation.
"""

from __future__ import annotations

from html.parser import HTMLParser
import re
import time
import urllib.error
import urllib.request


PROVIDER_VERSION = "johnston-ridge-access-r1-closure-preview"

AUTHORITY = "Washington State Department of Transportation"
PROJECT_URL = (
    "https://wsdot.wa.gov/construction-planning/search-projects/"
    "sr-504-south-coldwater-slide-spirit-lake-outlet-bridge-washout"
)
SOURCE_KIND = "official_sr504_johnston_ridge_project_status"


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


def parse_johnston_ridge_project_status(html, fetched_at_epoch=None):
    """Parse explicit current closure/reopening language from the WSDOT page.

    Historical prose is expected to remain on the project page after reopening,
    so an OPEN verdict needs strong present-tense language. Otherwise the
    provider returns UNKNOWN rather than inferring access.
    """
    fetched_at_epoch = float(
        fetched_at_epoch if fetched_at_epoch is not None else time.time()
    )
    text = _normalize(_visible_text(html))

    has_sr504 = "sr 504" in text or "state route 504" in text
    has_johnston = "johnston ridge observatory" in text
    has_context = has_sr504 and has_johnston

    construction_status = bool(
        re.search(r"project status.{0,120}\bconstruction\b", text)
    )

    explicit_open_tokens = (
        "johnston ridge observatory is open to the public",
        "johnston ridge observatory has reopened to the public",
        "johnston ridge observatory is now open",
        "full length of sr 504 is open to the public",
        "full length of state route 504 is open to the public",
        "travelers can now drive the full length of sr 504",
    )
    explicit_closed_tokens = (
        "road is currently closed",
        "currently closed at the winter gate",
        "public access closed",
        "johnston ridge observatory is currently closed",
        "johnston ridge observatory remains closed",
        "before it can reopen to the public",
    )

    explicit_open = any(token in text for token in explicit_open_tokens)
    explicit_closed = any(token in text for token in explicit_closed_tokens)

    # Strong present-tense reopening can supersede historical closure prose, but
    # not while the same page still labels the project as active construction.
    if has_context and explicit_open and not construction_status:
        status = "open"
        status_basis = "official_wsdot_explicit_current_reopening"
    elif has_context and (explicit_closed or construction_status):
        status = "closed"
        status_basis = (
            "official_wsdot_explicit_current_closure"
            if explicit_closed
            else "official_wsdot_project_status_construction"
        )
    else:
        status = "unknown"
        status_basis = "official_wsdot_status_not_unambiguous"

    parse_ok = has_context and status in {"open", "closed"}
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": PROJECT_URL,
        "source_kind": SOURCE_KIND,
        "fetched_at_epoch": fetched_at_epoch,
        "checked_at_epoch": fetched_at_epoch if parse_ok else None,
        "status": status,
        "status_basis": status_basis,
        "parse_ok": parse_ok,
        "has_context": has_context,
        "construction_status": construction_status,
    }


def unknown_johnston_ridge_provider_state(
    reason="provider_unavailable",
    fetched_at_epoch=None,
):
    return {
        "provider_version": PROVIDER_VERSION,
        "authoritative": True,
        "authority": AUTHORITY,
        "source_url": PROJECT_URL,
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


def fetch_johnston_ridge_project_status(timeout=12, attempts=2):
    """Fetch the official WSDOT project page with bounded retries."""
    req = urllib.request.Request(
        PROJECT_URL,
        headers={"User-Agent": "ChaseLights/2.0 (+weather photography)"},
    )
    last_error = None
    for attempt in range(max(1, int(attempts))):
        fetched_at_epoch = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                html = response.read().decode(charset, errors="replace")
            return parse_johnston_ridge_project_status(
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

    return unknown_johnston_ridge_provider_state(
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
        else unknown_johnston_ridge_provider_state()
    )
    status = str(provider_state.get("status") or "unknown").lower()
    parse_ok = provider_state.get("parse_ok") is True

    if not parse_ok or status not in {"open", "closed"}:
        return {
            "status": "unknown",
            "authoritative": True,
            "authority": provider_state.get("authority", AUTHORITY),
            "source_url": provider_state.get("source_url", PROJECT_URL),
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

    if status == "closed":
        # The current WSDOT page explicitly describes a long-running public
        # access closure. Closed schedule snapshots may prove CLOSED across the
        # forecast horizon; every generator process still refetches the page.
        freshness_mode = "schedule"
    else:
        # Reopening is more safety-sensitive: it must remain tied to a fresh
        # present-tense authoritative page snapshot.
        freshness_mode = "live"

    return {
        "status": status,
        "authoritative": True,
        "authority": provider_state.get("authority", AUTHORITY),
        "source_url": provider_state.get("source_url", PROJECT_URL),
        "source_kind": provider_state.get("source_kind", SOURCE_KIND),
        "freshness_mode": freshness_mode,
        "checked_at_epoch": provider_state.get("checked_at_epoch"),
        "status_basis": provider_state.get("status_basis"),
        "provider_version": provider_state.get("provider_version", PROVIDER_VERSION),
        "provider_parse_ok": True,
        "construction_status": provider_state.get("construction_status"),
    }


def build_johnston_ridge_access_state(timestamp, provider_state=None):
    """Return the Opportunity-keyed access snapshot expected by access_state."""
    _ = timestamp
    return {"us-017-P01": _snapshot(provider_state)}
