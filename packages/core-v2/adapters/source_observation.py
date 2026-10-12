"""Read-only source-record gate for NWS gridpoint data; never evaluates photo conditions.

The caller supplies an externally retrieved record. URL matching is structural,
NOT proof of HTTP origin, coverage-to-camera mapping, or license approval.
No network calls, thresholds, probability, or live recommendations occur here.
"""

from datetime import datetime
import math
import re
from urllib.parse import urlsplit

_GRID = re.compile(r"/gridpoints/([A-Z]{3})/(\d+),(\d+)$")


def _time(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def evaluate_source_record(record, *, as_of, freshness_policy):
    """Validate a normalized source record; all condition decisions stay UNKNOWN.

    An approved freshness_policy contains approved=True, source, max_age_seconds.
    It is a data-age limit supplied by governance, NOT a photo threshold.
    """
    result = {"provider": None, "source": None, "issued_at": None,
              "valid_at": None, "valid_until": None, "unit": None,
              "coverage": None, "license": None, "freshness": "unknown",
              "source_state": "UNKNOWN", "decision": "UNKNOWN",
              "raw_value": None, "live_recommendation": False, "reasons": []}

    def fail(reason):
        result["reasons"].append(reason)
        return result

    if not isinstance(record, dict):
        return fail("MISSING_SOURCE_RECORD")
    result.update({k: record.get(k) for k in
                   ("provider", "source", "issued_at", "valid_at", "valid_until",
                    "unit", "coverage", "license")})
    if record.get("provider") != "NOAA_NWS":
        return fail("UNAPPROVED_PROVIDER")
    url = record.get("source")
    try:
        p = urlsplit(url) if isinstance(url, str) else None
        match = _GRID.fullmatch(p.path) if p else None
        valid_url = bool(p and p.scheme == "https" and p.netloc == "api.weather.gov"
                         and not p.query and not p.fragment and match)
    except ValueError:
        valid_url = False
        match = None
    if not valid_url:
        return fail("INVALID_SOURCE_URL")
    coverage = record.get("coverage")
    if (not isinstance(coverage, dict) or coverage.get("type") != "nws_gridpoint"
            or coverage.get("office") != match.group(1)
            or type(coverage.get("grid_x")) is not int
            or type(coverage.get("grid_y")) is not int
            or coverage["grid_x"] != int(match.group(2))
            or coverage["grid_y"] != int(match.group(3))):
        return fail("COVERAGE_UNVERIFIED")
    if not isinstance(record.get("license"), str) or not record["license"].strip():
        return fail("LICENSE_UNVERIFIED")
    if not isinstance(record.get("unit"), str) or not record["unit"].strip():
        return fail("UNIT_MISSING")
    value = record.get("raw_value")
    if type(value) not in (int, float) or not math.isfinite(value):
        return fail("RAW_VALUE_INVALID")
    at, issued, start, end = (_time(as_of), _time(record.get("issued_at")),
                              _time(record.get("valid_at")), _time(record.get("valid_until")))
    if not all((at, issued, start, end)) or not issued <= at or not start <= at < end:
        return fail("INVALID_SOURCE_TIME")
    policy = freshness_policy
    if (not isinstance(policy, dict) or policy.get("approved") is not True
            or not isinstance(policy.get("source"), str) or not policy["source"].strip()
            or type(policy.get("max_age_seconds")) is not int
            or policy["max_age_seconds"] <= 0):
        return fail("FRESHNESS_POLICY_UNAPPROVED")
    if (at - issued).total_seconds() > policy["max_age_seconds"]:
        result["freshness"] = "stale"
        return fail("STALE_SOURCE")
    result["freshness"] = "fresh"
    result["raw_value"] = value
    # A caller-supplied URL and fields cannot authenticate a provider response.
    # TEST_ONLY records can exercise the structural contract, not prove provenance.
    if record.get("test_only") is True:
        result["source_state"] = "TEST_ONLY_RAW"
        return fail("TEST_ONLY_NOT_LIVE")
    return fail("PROVIDER_AUTHENTICITY_NOT_VERIFIED")
