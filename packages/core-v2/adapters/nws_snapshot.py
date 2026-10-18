"""One NWS /points -> /gridpoints snapshot, with replayable original bytes.

Uses the existing W1 v0.1 record contract and W3 parser. No live clock or
transport injection is exposed. Replay is explicitly TEST_FIXTURE, even when
an archive claims it was originally downloaded over HTTPS.
"""
from base64 import b64decode, b64encode
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from urllib.error import HTTPError, URLError

from . import nws_gridpoint as nws

FIELDS = ("skyCover", "windSpeed", "probabilityOfPrecipitation")


def _unknown(reason):
    return {"source_state": "UNKNOWN", "records": [], "fields": {},
            "documents": [], "reasons": [reason],
            "photography_verdict": "NOT_EVALUABLE", "live_recommendation": False}


def _document(url, raw):
    return {"url": url, "sha256": hashlib.sha256(raw).hexdigest(),
            "body_base64": b64encode(raw).decode("ascii")}


def _parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise nws.SourceFailure("AMBIGUOUS_SOURCE_JSON")
            result[key] = value
        return result

    def reject_constant(value):
        raise nws.SourceFailure("NONFINITE_SOURCE_JSON")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=reject_constant)


def _normalize_snapshot(points_raw, grid_raw, *, points_url, grid_url,
                        valid_at, retrieved_at, as_of, coordinate_source,
                        freshness_policy, retrieval_mode, expected_time_zone=None):
    documents = [_document(points_url, points_raw), _document(grid_url, grid_raw)]
    try:
        points, grid = _parse(points_raw), _parse(grid_raw)
        if not isinstance(points, dict) or not isinstance(grid, dict):
            raise nws.SourceFailure("INVALID_SOURCE_DOCUMENT")
        if not isinstance(points.get("geometry"), dict):
            raise nws.SourceFailure("POINTS_COORDINATE_MISMATCH")
        if not isinstance(points.get("properties"), dict):
            raise nws.SourceFailure("INVALID_SOURCE_DOCUMENT")
        if (expected_time_zone is not None
                and points.get("properties", {}).get("timeZone") != expected_time_zone):
            raise nws.SourceFailure("PROVIDER_TIME_ZONE_MISMATCH")
        properties = grid.get("properties")
        match = nws._validate_url(grid_url, "grid")
        # The source body must corroborate the lookup; the URL alone is not
        # proof that a body belongs to this grid.
        if (not isinstance(properties, dict)
                or properties.get("gridId") != match.group(1)
                or type(properties.get("gridX")) is not int
                or type(properties.get("gridY")) is not int
                or properties["gridX"] != int(match.group(2))
                or properties["gridY"] != int(match.group(3))):
            raise nws.SourceFailure("GRID_BODY_MAPPING_MISMATCH")
        age = nws._strict_policy(freshness_policy)
        retrieved, now, requested = map(nws._time, (retrieved_at, as_of, valid_at))
        if retrieved > now:
            raise nws.SourceFailure("FUTURE_RETRIEVAL")
        if requested < now:
            raise nws.SourceFailure("PAST_EVENT_NOT_FORECASTABLE")
        updated = nws._time(properties.get("updateTime"))
        if (now - updated).total_seconds() > age:
            raise nws.SourceFailure("STALE_SOURCE")
        fields = {}
        for field in FIELDS:
            try:
                fields[field] = nws._normalize(
                    points, grid, grid_raw, points_url=points_url, grid_url=grid_url,
                    field=field, valid_at=valid_at, retrieved_at=retrieved_at,
                    coordinate_source=coordinate_source, freshness_policy=freshness_policy,
                    retrieval_mode=retrieval_mode)
            except (nws.SourceFailure, TypeError, KeyError, ValueError, OverflowError) as exc:
                fields[field] = nws._no_record(str(exc))
        records = [item["record"] for item in fields.values() if item["record"] is not None]
        reasons = sorted({reason for item in fields.values() if item["record"] is None
                          for reason in item["reasons"]})
        return {"source_state": "RAW_SOURCE_ONLY" if records else "UNKNOWN",
                "records": records, "fields": fields, "documents": documents,
                "retrieval_mode": retrieval_mode,
                "retrieved_at_utc": nws._utc(retrieved),
                "checked_at_utc": nws._utc(now), "valid_at_utc": nws._utc(requested),
                # This is an operational age cutoff, NOT a model issuance or
                # scientific forecast horizon. Recheck on every replay/use.
                "expires_at_utc": nws._utc(updated + timedelta(seconds=age)),
                "freshness_policy": dict(freshness_policy),
                "time_zone": points.get("properties", {}).get("timeZone"),
                "provider_metadata": {
                    "provider": "NOAA_NWS", "source_kind": "FORECAST",
                    "model_id": None, "model_version": None,
                    "provider_run_id": None, "provider_issued_at_utc": None,
                    "native_resolution_m": None, "forecast_horizon_hours": None,
                    "terms_source": "https://www.weather.gov/disclaimer",
                    "terms_review": "REQUIRED_BEFORE_PUBLIC_REDISTRIBUTION",
                },
                "reasons": ["NO_APPROVED_PHOTO_THRESHOLD", "NO_VERIFIED_MODEL_RUN"] + reasons,
                "photography_verdict": "NOT_EVALUABLE", "live_recommendation": False}
    except (nws.SourceFailure, TypeError, KeyError, ValueError, OverflowError) as exc:
        result = _unknown(str(exc))
        result["documents"] = documents
        return result


def fetch_nws_snapshot(*, latitude, longitude, valid_at, coordinate_source,
                       freshness_policy, timeout=12, expected_time_zone=None):
    """Only the default pinned TLS/no-redirect transport can create HTTPS_TLS.

    One lookup and one raw-grid request serve all fields. The original response
    bodies are archived, including on semantic rejection. No API keys required.
    """
    try:
        age = nws._strict_policy(freshness_policy)
        if (type(latitude) not in (float, int) or type(longitude) not in (float, int)
                or not math.isfinite(latitude) or not math.isfinite(longitude)
                or not -90 <= latitude <= 90 or not -180 <= longitude <= 180):
            raise nws.SourceFailure("OUT_OF_RANGE_LOCATION")
        if type(timeout) not in (int, float) or not 0 < timeout <= 30:
            raise nws.SourceFailure("INVALID_TIMEOUT")
        nws._time(valid_at)
        if not isinstance(coordinate_source, str) or len(coordinate_source.strip()) < 4:
            raise nws.SourceFailure("COORDINATE_SOURCE_UNVERIFIED")
        points_url = f"https://api.weather.gov/points/{latitude:g},{longitude:g}"
        transport = nws.build_opener(nws.NoRedirect)
        _, points_raw = nws._get_json_bytes(points_url, timeout=timeout, opener=transport)
        points = _parse(points_raw)
        prop = points.get("properties") if isinstance(points, dict) else None
        grid_url = prop.get("forecastGridData") if isinstance(prop, dict) else None
        if not isinstance(grid_url, str):
            raise nws.SourceFailure("INVALID_SOURCE_URL")
        nws._validate_url(grid_url, "grid")
        _, grid_raw = nws._get_json_bytes(grid_url, timeout=timeout, opener=transport)
        # Read the real completion clock. A caller cannot backdate this fetch.
        retrieved = datetime.now(timezone.utc)
        return _normalize_snapshot(
            points_raw, grid_raw, points_url=points_url, grid_url=grid_url,
            valid_at=valid_at, retrieved_at=retrieved, as_of=retrieved,
            coordinate_source=coordinate_source,
            freshness_policy={**freshness_policy, "max_age_seconds": age},
            retrieval_mode="HTTPS_TLS", expected_time_zone=expected_time_zone)
    except (HTTPError, URLError, OSError, TimeoutError) as exc:
        result = _unknown("PROVIDER_TRANSPORT_UNAVAILABLE")
        result["transport_error"] = type(exc).__name__
        return result
    except (nws.SourceFailure, TypeError, KeyError, ValueError, OverflowError) as exc:
        return _unknown(str(exc))


def replay_nws_snapshot(documents, *, valid_at, retrieved_at, as_of,
                        coordinate_source, freshness_policy, expected_time_zone=None):
    """Verify archive hashes and recheck current age/interval; never live proof."""
    try:
        if not isinstance(documents, list) or len(documents) != 2:
            raise nws.SourceFailure("MISSING_ARCHIVE_DOCUMENTS")
        raw = []
        for document in documents:
            nws._validate_url(document["url"], "points" if not raw else "grid")
            encoded = document["body_base64"]
            if not isinstance(encoded, str) or len(encoded) > 4 * ((nws.MAX_BYTES + 2) // 3):
                raise nws.SourceFailure("INVALID_ARCHIVE_SIZE")
            data = b64decode(encoded, validate=True)
            if not 0 < len(data) <= nws.MAX_BYTES:
                raise nws.SourceFailure("INVALID_ARCHIVE_SIZE")
            if hashlib.sha256(data).hexdigest() != document["sha256"]:
                raise nws.SourceFailure("ARCHIVE_HASH_MISMATCH")
            raw.append(data)
        return _normalize_snapshot(
            *raw, points_url=documents[0]["url"], grid_url=documents[1]["url"],
            valid_at=valid_at, retrieved_at=retrieved_at, as_of=as_of,
            coordinate_source=coordinate_source, freshness_policy=freshness_policy,
            retrieval_mode="TEST_FIXTURE", expected_time_zone=expected_time_zone)
    except (nws.SourceFailure, TypeError, KeyError, ValueError, OverflowError) as exc:
        return _unknown(str(exc))
