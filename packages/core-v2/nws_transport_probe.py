"""One-shot transport diagnostics; never a weather source or scoring input.

Uses the environment's existing network route. No retries, redirects, proxy
overrides, credentials, TLS bypass or arbitrary URL input. curl is required.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from adapters.nws_gridpoint import USER_AGENT

URL = "https://api.weather.gov/points/47.6,-122.33"
ACCEPT = "application/geo+json, application/json"
SAFE_HEADERS = {
    "date", "server", "content-type", "content-length", "retry-after",
    "via", "age", "cache-control", "expires", "x-cache", "x-request-id",
    "x-correlation-id", "x-amzn-requestid", "x-amz-cf-id",
}


def classify(connect_status, http_status, curl_exit):
    """Locate a failure without attributing a generic HTTP 403 to NOAA."""
    if connect_status and connect_status != 200:
        return "PROXY_CONNECT_REJECTED"
    if http_status:
        if curl_exit:
            return "HTTP_RESPONSE_TRANSFER_FAILED"
        if http_status == 200:
            return "HTTP_200_TRANSPORT_ONLY"
        if http_status == 429:
            return "HTTP_429_RATE_LIMIT_SIGNAL_ORIGIN_UNVERIFIED"
        if http_status == 403:
            return "HTTP_403_CAUSE_AND_ORIGIN_UNVERIFIED"
        return "HTTP_NON_200_ORIGIN_UNVERIFIED"
    return "DNS_TCP_TLS_OR_PROXY_FAILURE_UNRESOLVED"


def header_blocks(raw):
    """Retain status lines and allowlisted diagnostics, never cookies/auth."""
    blocks = []
    for line in raw.splitlines():
        if line.startswith("HTTP/"):
            blocks.append({"status_line": line, "headers": {}})
        elif blocks and ":" in line:
            key, value = line.split(":", 1)
            if key.lower() in SAFE_HEADERS:
                blocks[-1]["headers"].setdefault(key.lower(), []).append(value.strip())
    return blocks


def probe():
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="nws-transport-") as directory:
        headers = Path(directory) / "headers"
        body = Path(directory) / "body"
        # -q first disables user curl configuration; environment route remains.
        command = ["curl", "-q", "--silent", "--show-error", "--proto", "=https",
                   "--max-redirs", "0", "--connect-timeout", "10", "--max-time", "20",
                   "--max-filesize", "1048576", "--user-agent", USER_AGENT,
                   "--header", "Accept: " + ACCEPT, "--dump-header", str(headers),
                   "--output", str(body), "--write-out",
                   "%{http_connect}\n%{http_code}\n%{time_total}\n", URL]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=25)
            timed_out = False
        except subprocess.TimeoutExpired:
            # Preserve a structured UNKNOWN diagnostic instead of crashing on
            # an incomplete transfer; never claim an HTTP response was seen.
            completed = subprocess.CompletedProcess(command, 124, stdout="")
            timed_out = True
        parts = (completed.stdout or "").splitlines()
        try:
            connect, status = int(parts[0]), int(parts[1])
        except (IndexError, ValueError):
            connect, status = 0, 0
        try:
            elapsed = float(parts[2])
        except (IndexError, ValueError):
            elapsed = None
        raw_body = body.read_bytes() if body.exists() else b""
        return {
            "artifact_kind": "TRANSPORT_DIAGNOSTIC_NOT_WEATHER_EVIDENCE",
            "url": URL, "method": "GET", "started_at_utc": started,
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "request_headers": {"User-Agent": USER_AGENT, "Accept": ACCEPT},
            "proxy_environment_present": any(os.environ.get(key) for key in
                ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy")),
            "curl_exit": completed.returncode, "connect_http_status": connect,
            "target_http_status": status, "elapsed_seconds": elapsed,
            "timed_out": timed_out, "status_output_complete": len(parts) >= 3,
            "classification": classify(connect, status, completed.returncode),
            "response_header_blocks": header_blocks(headers.read_text(errors="replace"))
                if headers.exists() else [],
            "received_body_bytes": len(raw_body),
            "received_body_sha256": hashlib.sha256(raw_body).hexdigest() if raw_body else None,
            "photography_verdict": "NOT_EVALUABLE", "recommendation_eligible": False,
        }


if __name__ == "__main__":
    result = probe()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["classification"] == "HTTP_200_TRANSPORT_ONLY" else 1)
