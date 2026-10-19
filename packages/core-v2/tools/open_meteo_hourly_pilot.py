"""Manual, one-attempt capture and offline replay; no scheduler or evaluator."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path
import signal
import ssl
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapters"))
import open_meteo_hourly as adapter

USER_AGENT = "ChaseLights-V2-OpenMeteo-Pilot/0.1 (noncommercial research; https://github.com/gdrabbit137-ai/ChaseLights)"


def now():
    return datetime.now(timezone.utc)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@contextmanager
def network_deadline(seconds=20):
    """Linux manual CLI: bound the complete open/read, including slow bodies."""
    previous = signal.getsignal(signal.SIGALRM)
    if signal.getitimer(signal.ITIMER_REAL)[0]:
        raise adapter.PilotFailure("NETWORK_TIMER_ALREADY_ACTIVE")
    def expired(*_):
        raise TimeoutError("20 second network deadline")
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def reserve_capture(ledger, when):
    """Local rolling budget only. Reservation consumes one attempt even on failure."""
    when = adapter.utc(when)
    ledger = Path(ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(ledger, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "r+", encoding="utf-8") as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        text = file.read(65537)
        if len(text) > 65536:
            raise adapter.PilotFailure("CAPTURE_LEDGER_TOO_LARGE")
        try:
            times = [adapter.utc(json.loads(line)["requested_at_utc"]) for line in text.splitlines()]
        except (ValueError, KeyError, TypeError) as exc:
            raise adapter.PilotFailure("INVALID_CAPTURE_LEDGER") from exc
        if times and (max(times) > when or (when - max(times)).total_seconds() < 10800):
            raise adapter.PilotFailure("CAPTURE_REFRESH_BUDGET_OR_FUTURE_CLOCK")
        if sum(t > when - timedelta(days=1) for t in times) >= 8:
            raise adapter.PilotFailure("CAPTURE_DAILY_BUDGET")
        file.seek(0, os.SEEK_END)
        file.write(json.dumps({"requested_at_utc": adapter.stamp(when), "attempts_reserved": 1}) + "\n")
        file.flush()
        os.fsync(file.fileno())


def fetch_one(url, *, opener=None):
    """One HTTP attempt; injectable transport is for tests, never evidence."""
    result = {"http_status": None, "content_type": None, "http_date": None,
              "retry_after": None, "final_url": None, "body_complete": False,
              "error": None, "raw": None}
    opener = opener if opener is not None else build_opener(NoRedirect())
    try:
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json",
                                        "Accept-Encoding": "identity"})
        with network_deadline():
            try:
                response = opener.open(request, timeout=20)
            except HTTPError as exc:
                response = exc  # archive bounded HTTP error bytes, never normalize them
            with response:
                result.update(http_status=response.status, final_url=response.geturl(),
                              content_type=response.headers.get("Content-Type"),
                              http_date=response.headers.get("Date"),
                              retry_after=response.headers.get("Retry-After"))
                raw = response.read(adapter.MAX_BYTES + 1)
                result["raw"] = raw
                result["body_complete"] = len(raw) <= adapter.MAX_BYTES
                encoding = response.headers.get("Content-Encoding", "identity").lower()
                if len(raw) > adapter.MAX_BYTES:
                    result["error"] = "OVERSIZED_BODY_TRUNCATED"
                elif response.geturl() != url:
                    result["error"] = "REDIRECT_REJECTED"
                elif response.status != 200:
                    result["error"] = "HTTP_" + str(response.status)
                elif encoding != "identity":
                    result["error"] = "UNSUPPORTED_CONTENT_ENCODING"
                elif (result["content_type"] or "").split(";", 1)[0].strip().lower() != "application/json":
                    result["error"] = "NON_JSON_CONTENT_TYPE"
    except (URLError, ssl.SSLError, TimeoutError, OSError, HTTPException) as exc:
        result["error"] = type(exc).__name__ + ": " + str(getattr(exc, "reason", exc))
    return result


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, allow_nan=False, indent=2) + "\n", encoding="utf-8")


def capture_once(output, ledger, quota_note, *, repo=None):
    """Only the opt-in CLI calls this real HTTPS path; no injected live clock/body."""
    inputs = adapter.load_inputs(repo)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    url = adapter.build_request(inputs)
    requested = now()
    receipt = {
        "operation": "ONE_MANUAL_HTTPS_CAPTURE", "contract_sha": adapter.CONTRACT_SHA,
        "w3_study_sha": adapter.STUDY_SHA, "pilot_binding_sha256": adapter.BINDING_SHA256,
        "schema_sha256": adapter.SCHEMA_SHA256, "request_url": url,
        "request": adapter.request_metadata(inputs), "requested_at_utc": adapter.stamp(requested),
        "http_attempts": 0, "raw_sha256": None, "raw_size": None,
        "provider_acceptance": "UNVERIFIED", "shared_quota_check_note": quota_note,
        "scope": "NONCOMMERCIAL_RESEARCH_PILOT_ONLY", "automatic_retries": 0,
        "retrieval_mode": "HTTPS_TLS", "retrieved_at_utc": None, "normalized_at_utc": None,
    }
    try:
        reserve_capture(ledger, requested)
        receipt["http_attempts"] = 1
        packet = fetch_one(url)
        retrieved = now()  # actual completion clock; HTTP Date is metadata only
        raw = packet.pop("raw")
        receipt.update(packet, retrieved_at_utc=adapter.stamp(retrieved))
        if raw is not None:
            (output / "response-body.bin").write_bytes(raw)
            receipt.update(raw_sha256=hashlib.sha256(raw).hexdigest(), raw_size=len(raw))
        normalized = now()
        receipt["normalized_at_utc"] = adapter.stamp(normalized)
        if packet["error"]:
            result = adapter.diagnostic(packet["error"])
        else:
            result = adapter._normalize(raw, inputs=inputs, source_url=url,
                                        expected_sha256=receipt["raw_sha256"], requested_at=requested,
                                        retrieved_at=retrieved, normalized_at=normalized,
                                        checked_at=normalized, retrieval_mode="HTTPS_TLS")
        if result["artifact"] is not None:
            _write(output / "artifact.json", result["artifact"])
            if result["availability"] == "COMPLETE":
                receipt["provider_acceptance"] = "CAPTURE_COMPLETE_REPLAY_PENDING"
    except (adapter.PilotFailure, OSError) as exc:
        result = adapter.diagnostic(str(exc))
    receipt["result"] = result
    _write(output / "capture.json", receipt)
    return receipt


def replay_capture(directory, *, repo=None, checked_at=None):
    """Offline hash/contract replay of archive provenance, never another TLS call.

    Receipt hashes establish byte consistency, not a cryptographic attestation
    of a provider. W5 must inspect the actual capture execution independently.
    """
    inputs = adapter.load_inputs(repo)
    directory = Path(directory)
    try:
        receipt = adapter.decode((directory / "capture.json").read_bytes())
        if (receipt["contract_sha"] != adapter.CONTRACT_SHA
                or receipt["pilot_binding_sha256"] != adapter.BINDING_SHA256
                or receipt["schema_sha256"] != adapter.SCHEMA_SHA256
                or receipt["request"] != adapter.request_metadata(inputs)
                or receipt["request_url"] != adapter.build_request(inputs)
                or receipt["retrieval_mode"] not in ("HTTPS_TLS", "TEST_FIXTURE")):
            raise adapter.PilotFailure("CAPTURE_IDENTITY_MISMATCH")
        if (receipt.get("http_status") != 200 or receipt.get("error")
                or receipt.get("body_complete") is not True
                or receipt.get("final_url") != receipt["request_url"]):
            raise adapter.PilotFailure("CAPTURE_NOT_ACCEPTED: " + str(receipt.get("error")))
        with (directory / "response-body.bin").open("rb") as file:
            raw = file.read(adapter.MAX_BYTES + 1)
        if len(raw) != receipt["raw_size"]:
            raise adapter.PilotFailure("CAPTURE_SIZE_MISMATCH")
        result = adapter._normalize(raw, inputs=inputs, source_url=receipt["request_url"],
                                    expected_sha256=receipt["raw_sha256"],
                                    requested_at=receipt["requested_at_utc"],
                                    retrieved_at=receipt["retrieved_at_utc"],
                                    normalized_at=receipt["normalized_at_utc"],
                                    checked_at=checked_at if checked_at is not None else now(),
                                    retrieval_mode=receipt["retrieval_mode"])
    except (adapter.PilotFailure, OSError, KeyError, TypeError, ValueError) as exc:
        result = adapter.diagnostic(str(exc))
    return {"operation": "OFFLINE_REPLAY", "network_attempts": 0,
            "new_live_capture": False, "result": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    capture = sub.add_parser("capture")
    capture.add_argument("--live", action="store_true", required=True,
                         help="Explicit opt-in to one noncommercial research HTTPS request")
    capture.add_argument("--quota-note", required=True,
                         help="Record actual local/shared application-IP quota review; state unknowns honestly")
    capture.add_argument("--ledger", type=Path, required=True)
    capture.add_argument("--output", type=Path, required=True)
    replay = sub.add_parser("replay")
    replay.add_argument("--capture-dir", type=Path, required=True)
    replay.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "capture":
            if not args.quota_note.strip():
                raise adapter.PilotFailure("QUOTA_REVIEW_NOTE_REQUIRED")
            result = capture_once(args.output, args.ledger, args.quota_note, repo=args.repo)
            accepted = result["result"]["artifact"] is not None
        else:
            if args.output.exists():
                raise adapter.PilotFailure("REPLAY_OUTPUT_ALREADY_EXISTS")
            result = replay_capture(args.capture_dir, repo=args.repo)
            _write(args.output, result)
            accepted = result["result"]["artifact"] is not None
        print(json.dumps({"status": "PASS" if accepted else "UNVERIFIED",
                          "operation": args.command, "output": str(args.output),
                          "reasons": result["result"]["reasons"]}, ensure_ascii=False))
        return 0 if accepted else 2
    except (adapter.PilotFailure, OSError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
